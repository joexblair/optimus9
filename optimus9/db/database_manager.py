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
    """Owns the MySQL connection lifecycle and raw query execution."""

    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3306):
        self._cfg  = dict(host=host, user=user, password=password, database=database, port=port)
        self._conn = None
        self._log  = get_logger(self.__class__.__name__)

    def connect(self) -> None:
        self._conn = mysql.connector.connect(**self._cfg, autocommit=True)
        self._log.info('MySQL connected')

    def disconnect(self) -> None:
        if self._conn and self._conn.is_connected():
            self._conn.close()
            self._log.info('MySQL disconnected')

    def execute(self, sql: str, params: tuple = (), *, fetch: bool = False):
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
