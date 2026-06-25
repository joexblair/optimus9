"""
DatabaseManager — see class docstring for purpose, Pine alignment, and design notes.
"""


"""
managers.py — PK Optimizer
All process classes. One responsibility per class.
Every class calls get_logger(self.__class__.__name__).

Terminology:
  OOB  = out of boundary (indicator has crossed high/low threshold)
  IB   = in boundary (indicator is within thresholds)
  OS/OB remain only in RSI/K oscillator context where they are technically correct.
"""

import asyncio
import itertools
import json
import math
import multiprocessing
import signal
import time
from dataclasses import dataclass, field
import re
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

import mysql.connector
import numpy as np
import pandas as pd
import requests
import websockets

from logger import get_logger


class DatabaseManager:
    """Owns the MySQL connection lifecycle and raw query execution.

    Self-healing: a long-running connection can die (server `wait_timeout`, a MySQL
    restart, a network blip) and mysql-connector then raises InterfaceError/OperationalError
    ('MySQL Connection not available.', 'server has gone away') on every subsequent call.
    `execute`/`executemany` catch ONLY that connection-loss family, reconnect with bounded
    backoff, and retry the op ONCE. Real SQL errors (ProgrammingError: syntax, unknown column)
    are NOT retried — they re-raise immediately. Reconnection is this class's single
    responsibility; consumers (collector, auditor, bias engine) heal for free."""

    # connection-loss family → reconnect+retry. (NOT ProgrammingError/IntegrityError — those fail fast.)
    _RECONNECT_ERRS = (mysql.connector.errors.InterfaceError,
                       mysql.connector.errors.OperationalError)

    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3306):
        self._cfg  = dict(host=host, user=user, password=password, database=database, port=port)
        self._conn = None
        self._log  = get_logger(self.__class__.__name__)

    def connect(self) -> None:
        self._open(first=True)

    def _open(self, first: bool = False) -> None:
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
        self._conn = mysql.connector.connect(**self._cfg, autocommit=True)
        self._log.info('MySQL connected' if first else 'MySQL reconnected')

    def _reconnect(self, attempts: int = 6, base_delay: float = 1.0) -> None:
        """Reconnect with exponential backoff (capped at 30s). Raises if all attempts fail."""
        last = None
        for i in range(attempts):
            try:
                self._open()
                return
            except mysql.connector.Error as e:
                last = e
                delay = min(base_delay * (2 ** i), 30.0)
                self._log.error(f'reconnect {i + 1}/{attempts} failed: {e} — retrying in {delay:.0f}s')
                time.sleep(delay)
        raise last

    def _with_reconnect(self, fn):
        """Run a DB op; on a connection-loss error, reconnect once and retry."""
        try:
            return fn()
        except self._RECONNECT_ERRS as e:
            self._log.error(f'MySQL connection lost ({e.__class__.__name__}: {e}); reconnecting + retrying')
            self._reconnect()
            return fn()

    def disconnect(self) -> None:
        if self._conn and self._conn.is_connected():
            self._conn.close()
            self._log.info('MySQL disconnected')

    def execute(self, sql: str, params: tuple = (), *, fetch: bool = False):
        return self._with_reconnect(lambda: self._execute_impl(sql, params, fetch))

    def _execute_impl(self, sql: str, params: tuple, fetch: bool):
        cursor = self._conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        if fetch:
            result = cursor.fetchall()
            cursor.close()
            return result
        last_id = cursor.lastrowid
        cursor.close()
        return last_id

    def executemany(self, sql: str, rows: list, chunk: int = 1000) -> int:
        return self._with_reconnect(lambda: self._executemany_impl(sql, rows, chunk))

    def _executemany_impl(self, sql: str, rows: list, chunk: int = 1000) -> int:
        """Batch insert via chunked multi-row INSERT — one statement per `chunk` rows, all chunks
        in ONE transaction so the returned first auto-increment ID is contiguous across the whole
        batch (callers like optimizer_runner derive child PKs as first_id+offset; a concurrent
        writer between chunks must not gap the range). mysql-connector's own executemany is
        effectively per-row (≈1.5k rows/s); this is ~10-30× faster. Non-`VALUES` SQL → driver path."""
        if not rows:
            return 0
        cursor = self._conn.cursor()
        m = re.search(r'\bVALUES\s*', sql, re.IGNORECASE)
        if not m:                                          # not an INSERT…VALUES — driver path
            cursor.executemany(sql, rows)
            first_id = cursor.lastrowid
            cursor.close()
            return first_id
        prefix, template = sql[:m.end()].rstrip(), sql[m.end():].strip()
        first_id = None
        own_txn = not self._conn.in_transaction            # don't nest if a caller opened one
        if own_txn:
            self._conn.start_transaction()
        try:
            for i in range(0, len(rows), chunk):
                batch = rows[i:i + chunk]
                cursor.execute(f'{prefix} ' + ','.join([template] * len(batch)),
                               [v for row in batch for v in row])
                if first_id is None:
                    first_id = cursor.lastrowid
            if own_txn:
                self._conn.commit()
        except Exception:
            if own_txn:
                self._conn.rollback()
            cursor.close()
            raise
        cursor.close()
        return first_id or 0
