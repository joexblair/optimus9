"""
BinanceClient — see class docstring for purpose, Pine alignment, and design notes.
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


class BinanceClient:
    """
    Fetches klines from Binance Spot REST API.
    5s interval supported on spot (FARTCOINUSDT is futures-only — kept for other pairs).
    """

    _BASE        = 'https://api.binance.com'
    _KLINES_PATH = '/api/v3/klines'
    _BATCH_LIMIT = 1500
    _RATE_DELAY  = 0.12

    _VALID_INTERVALS = frozenset({
        '1s', '5s', '15s', '30s',
        '1m', '3m', '5m', '15m', '30m',
        '1h', '2h', '4h', '6h', '8h', '12h',
        '1d', '3d', '1w', '1M',
    })

    def __init__(self) -> None:
        self._session = requests.Session()
        self._log     = get_logger(self.__class__.__name__)

    def fetch_klines(self, symbol: str, interval: str, start_ms: int, end_ms: int) -> list:
        if interval not in self._VALID_INTERVALS:
            raise ValueError(f'Interval {interval!r} not supported')

        all_candles = []
        cursor = start_ms
        while cursor < end_ms:
            batch = self._fetch_batch(symbol, interval, cursor, end_ms)
            if not batch:
                break
            all_candles.extend(batch)
            last_ts = batch[-1]['timestamp']
            if last_ts >= end_ms or len(batch) < self._BATCH_LIMIT:
                break
            cursor = last_ts + 1
            time.sleep(self._RATE_DELAY)

        self._log.info(f'Fetched {len(all_candles)} candles ({symbol} {interval})')
        return all_candles

    def _fetch_batch(self, symbol: str, interval: str, start_ms: int, end_ms: int) -> list:
        params = {'symbol': symbol, 'interval': interval,
                  'startTime': start_ms, 'endTime': end_ms, 'limit': self._BATCH_LIMIT}
        resp = self._session.get(self._BASE + self._KLINES_PATH, params=params, timeout=10)
        if not resp.ok:
            self._log.error(f'Binance {resp.status_code}: {resp.text}')
            resp.raise_for_status()
        return [{'timestamp': int(r[0]), 'open': float(r[1]), 'high': float(r[2]),
                 'low': float(r[3]), 'close': float(r[4]), 'volume': float(r[5])}
                for r in resp.json()]
