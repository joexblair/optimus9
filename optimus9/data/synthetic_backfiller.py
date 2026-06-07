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

    def backfill(self, tp_pk: int, symbol: str, lookback_days: int = None) -> int:
        """
        Two modes:
          • lookback_days=None — gap-fill from MAX(kc_timestamp) to now.
            Short-circuits if gap < 30s. Default for manual backfill_synthetic.
          • lookback_days=N    — window mode. Always fetch the last N days.
            INSERT IGNORE dedupes against existing rows. Use when caller
            needs a guaranteed minimum coverage window (e.g. supervisor).
        """
        end_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        if lookback_days is not None:
            start_ms = end_ms - lookback_days * 86_400_000
        else:
            start_ms = self._gap_start(tp_pk)
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

    _PERSIST_CHUNK = 5000   # one executemany of all 35d (604k rows) blows InnoDB's lock table (1206)

    def _persist(self, tp_pk: int, bars: list) -> None:
        rows = [(tp_pk, b['timestamp'], b['open'], b['high'], b['low'], b['close'], b['volume'])
                for b in bars]
        # overwrite only existing dojis (kc_volume=0) so the official-1m fills gap windows;
        # never clobber a real-tick bar (kc_volume>0). chunked: one executemany of all 35d
        # (604k rows) blows InnoDB's lock table (1206); autocommit releases locks per batch.
        for i in range(0, len(rows), self._PERSIST_CHUNK):
            self._db.executemany(
                '''INSERT INTO kline_collection
                       (kc_tp_pk, kc_timestamp, kc_open, kc_high, kc_low, kc_close, kc_volume)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)
                   ON DUPLICATE KEY UPDATE
                       kc_open   = IF(kc_volume=0, VALUES(kc_open),   kc_open),
                       kc_high   = IF(kc_volume=0, VALUES(kc_high),   kc_high),
                       kc_low    = IF(kc_volume=0, VALUES(kc_low),    kc_low),
                       kc_close  = IF(kc_volume=0, VALUES(kc_close),  kc_close),
                       kc_volume = IF(kc_volume=0, VALUES(kc_volume), kc_volume)''',
                rows[i:i + self._PERSIST_CHUNK],
            )
