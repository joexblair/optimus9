"""
BybitKlineClient — see class docstring for purpose, Pine alignment, and design notes.
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


class BybitKlineClient:
    """Fetches OHLCV klines from Bybit Futures REST API (v5) for synthetic backfill."""

    _BASE        = 'https://api.bybit.com'
    _PATH        = '/v5/market/kline'
    _BATCH_LIMIT = 200
    _RATE_DELAY  = 0.12

    def __init__(self) -> None:
        self._session = requests.Session()
        self._log     = get_logger(self.__class__.__name__)

    def fetch_klines(self, symbol: str, interval: str, start_ms: int, end_ms: int) -> list:
        all_candles: list = []
        cursor_end = end_ms
        while cursor_end > start_ms:
            batch = self._fetch_batch(symbol, interval, start_ms, cursor_end)
            if not batch:
                break
            all_candles.extend(batch)
            earliest = batch[-1]['timestamp']
            self._log.info(
                f'  fetched {len(batch)} bars  '
                f'[{_ms_to_iso(earliest)}  →  {_ms_to_iso(batch[0]["timestamp"])}]'
                f'  total: {len(all_candles)}'
            )
            if earliest <= start_ms or len(batch) < self._BATCH_LIMIT:
                break
            cursor_end = earliest - 1
            time.sleep(self._RATE_DELAY)

        all_candles.sort(key=lambda x: x['timestamp'])
        self._log.info(f'Fetched {len(all_candles)} candles ({symbol} {interval}m)')
        return all_candles

    def _fetch_batch(self, symbol: str, interval: str, start_ms: int, end_ms: int) -> list:
        params = {'category': 'linear', 'symbol': symbol, 'interval': interval,
                  'start': start_ms, 'end': end_ms, 'limit': self._BATCH_LIMIT}
        resp = self._session.get(self._BASE + self._PATH, params=params, timeout=10)
        if not resp.ok:
            self._log.error(f'Bybit {resp.status_code}: {resp.text}')
            resp.raise_for_status()
        data = resp.json()
        if data.get('retCode') != 0:
            self._log.error(f'Bybit API error: {data}')
            return []
        return [{'timestamp': int(r[0]), 'open': float(r[1]), 'high': float(r[2]),
                 'low': float(r[3]), 'close': float(r[4]), 'volume': float(r[5])}
                for r in data['result']['list']]
