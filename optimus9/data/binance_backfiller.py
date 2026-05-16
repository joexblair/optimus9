"""
BinanceBackfiller — see class docstring for purpose, Pine alignment, and design notes.
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
from ..data.binance_client import BinanceClient
from .._helpers import _ms_to_iso


class BinanceBackfiller:
    """Fills kline_collection gaps from Binance Spot REST. Kept for non-futures pairs."""

    _LOOKBACK_WEEKS   = 5
    _DEFAULT_INTERVAL = '5s'

    def __init__(self, db: DatabaseManager, client: BinanceClient) -> None:
        self._db     = db
        self._client = client
        self._log    = get_logger(self.__class__.__name__)

    def backfill(self, tp_pk: int, symbol: str, interval: str = _DEFAULT_INTERVAL) -> int:
        start_ms = self._gap_start(tp_pk)
        end_ms   = int(datetime.now(timezone.utc).timestamp() * 1000)
        if end_ms - start_ms < 5_000:
            self._log.info('kline_collection is current')
            return 0
        self._log.info(f'Backfilling {symbol} {interval} from {_ms_to_iso(start_ms)}')
        candles = self._client.fetch_klines(symbol, interval, start_ms, end_ms)
        if not candles:
            self._log.error('Binance returned no candles')
            return 0
        self._db.executemany(
            '''INSERT IGNORE INTO kline_collection
                   (kc_tp_pk, kc_timestamp, kc_open, kc_high, kc_low, kc_close, kc_volume)
               VALUES (%s,%s,%s,%s,%s,%s,%s)''',
            [(tp_pk, c['timestamp'], c['open'], c['high'], c['low'], c['close'], c['volume'])
             for c in candles],
        )
        self._log.info(f'Stored {len(candles)} candles')
        return len(candles)

    def run_loop(self, tp_pk: int, symbol: str, interval: str = _DEFAULT_INTERVAL) -> None:
        self.backfill(tp_pk, symbol, interval)

    def _gap_start(self, tp_pk: int) -> int:
        rows = self._db.execute(
            'SELECT MAX(kc_timestamp) AS latest FROM kline_collection WHERE kc_tp_pk = %s',
            (tp_pk,), fetch=True,
        )
        latest = rows[0]['latest'] if rows and rows[0]['latest'] is not None else None
        if latest is not None:
            return int(latest) + 1
        return int((datetime.now(timezone.utc) - timedelta(weeks=self._LOOKBACK_WEEKS)).timestamp() * 1000)
