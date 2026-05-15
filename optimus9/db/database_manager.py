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

    def executemany(self, sql: str, rows: list) -> int:
        """Batch insert — returns first auto-increment ID of the batch."""
        if not rows:
            return 0
        cursor = self._conn.cursor()
        cursor.executemany(sql, rows)
        first_id = cursor.lastrowid
        cursor.close()
        return first_id
