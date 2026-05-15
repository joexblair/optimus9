"""
SyntheticBackfiller — see class docstring for purpose, Pine alignment, and design notes.
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
from ..data.bybit_kline_client import BybitKlineClient
from ..data.synthetic_bar_builder import SyntheticBarBuilder
from .._helpers import _ms_to_iso


class SyntheticBackfiller:
    """
    Fetches Bybit 1m futures history, splits to 12 × 5s, writes to kline_collection.
    Provides synthetic 5s bar history before live tick collection has accumulated.
    Live tick-derived bars overwrite synthetic ones (ON DUPLICATE KEY UPDATE in BarBuilder).
    """

    _LOOKBACK_WEEKS = 5

    def __init__(self, db: DatabaseManager, client: BybitKlineClient) -> None:
        self._db     = db
        self._client = client
        self._log    = get_logger(self.__class__.__name__)

    def backfill(self, tp_pk: int, symbol: str) -> int:
        start_ms  = self._gap_start(tp_pk)
        end_ms    = int(datetime.now(timezone.utc).timestamp() * 1000)
        if end_ms - start_ms < 30_000:
            self._log.info('kline_collection is current — no backfill needed')
            return 0

        span_days = (end_ms - start_ms) / 86_400_000
        self._log.info(
            f'Backfilling {symbol} synthetic 5s bars'
            f' — {span_days:.1f} days from {_ms_to_iso(start_ms)}'
        )
        bars_1m = self._client.fetch_klines(symbol, '1', start_ms, end_ms)
        if not bars_1m:
            self._log.error('No 1m bars returned from Bybit')
            return 0

        self._log.info(
            f'Splitting {len(bars_1m)} × 1m bars into {SyntheticBarBuilder._N} × 5s bars...'
        )
        bars_5s = SyntheticBarBuilder.split_batch(bars_1m)

        self._log.info(f'Writing {len(bars_5s)} bars to kline_collection...')
        self._persist(tp_pk, bars_5s)

        self._log.info(
            f'Done — {len(bars_5s)} synthetic 5s bars stored'
            f'  [{_ms_to_iso(bars_5s[0]["timestamp"])}  →  {_ms_to_iso(bars_5s[-1]["timestamp"])}]'
        )
        return len(bars_5s)

    def _gap_start(self, tp_pk: int) -> int:
        rows = self._db.execute(
            'SELECT MAX(kc_timestamp) AS latest FROM kline_collection WHERE kc_tp_pk = %s',
            (tp_pk,), fetch=True,
        )
        latest = rows[0]['latest'] if rows and rows[0]['latest'] is not None else None
        if latest is not None:
            return int(latest) + 1
        return int((datetime.now(timezone.utc) - timedelta(weeks=self._LOOKBACK_WEEKS)).timestamp() * 1000)

    def _persist(self, tp_pk: int, bars: list) -> None:
        self._db.executemany(
            '''INSERT IGNORE INTO kline_collection
                   (kc_tp_pk, kc_timestamp, kc_open, kc_high, kc_low, kc_close, kc_volume)
               VALUES (%s,%s,%s,%s,%s,%s,%s)''',
            [(tp_pk, b['timestamp'], b['open'], b['high'], b['low'], b['close'], b['volume'])
             for b in bars],
        )
