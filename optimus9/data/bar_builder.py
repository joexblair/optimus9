"""
BarBuilder — see class docstring for purpose, Pine alignment, and design notes.
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

# ── cross-package imports ─────────────────────────────────────────────────
from ..db.database_manager import DatabaseManager


class BarBuilder:
    """
    Wakes at each 5s wall-clock boundary.
    Builds the bar that ended one interval ago — guarantees TickCollector has committed.
    Tick-derived bars overwrite synthetic ones via ON DUPLICATE KEY UPDATE.
    """

    _BAR_S = 5

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    def run(self, tp_pk: int) -> None:
        self._log.info('BarBuilder started')
        while True:
            self._sleep_to_boundary()
            boundary_ms = int(time.time() * 1000)
            bar_end     = boundary_ms - self._BAR_S * 1000
            bar_start   = bar_end     - self._BAR_S * 1000
            self._build(tp_pk, bar_start, bar_end)

    def _sleep_to_boundary(self) -> None:
        now = time.time()
        time.sleep(max(0.0, math.ceil(now / self._BAR_S) * self._BAR_S - now))

    def _build(self, tp_pk: int, start_ms: int, end_ms: int) -> None:
        rows = self._db.execute(
            '''SELECT tk_price, tk_volume FROM ticks
               WHERE tk_tp_pk = %s AND tk_timestamp >= %s AND tk_timestamp < %s
               ORDER BY tk_timestamp ASC''',
            (tp_pk, start_ms, end_ms), fetch=True,
        )
        if not rows:
            self._log.debug(f'No ticks for bar {start_ms}')
            return

        prices  = [float(r['tk_price'])  for r in rows]
        volumes = [float(r['tk_volume']) for r in rows]

        self._db.execute(
            '''INSERT INTO kline_collection
                   (kc_tp_pk, kc_timestamp, kc_open, kc_high, kc_low, kc_close, kc_volume)
               VALUES (%s,%s,%s,%s,%s,%s,%s)
               ON DUPLICATE KEY UPDATE
                   kc_open=VALUES(kc_open), kc_high=VALUES(kc_high),
                   kc_low=VALUES(kc_low),   kc_close=VALUES(kc_close),
                   kc_volume=VALUES(kc_volume)''',
            (tp_pk, start_ms, prices[0], max(prices), min(prices), prices[-1], sum(volumes)),
        )
        self._log.debug(
            f'Bar ts={start_ms}  o={prices[0]}  h={max(prices)}'
            f'  l={min(prices)}  c={prices[-1]}  v={sum(volumes):.4f}'
        )
