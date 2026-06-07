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

# ── cross-package imports ─────────────────────────────────────────────────
from .._helpers import _ms_to_iso


class _RateLimited(Exception):
    """Bybit retCode 10006 — back off and retry rather than truncate the backfill."""


class BybitKlineClient:
    """Fetches OHLCV klines from Bybit Futures REST API (v5) for synthetic backfill."""

    _BASE        = 'https://api.bybit.com'
    _PATH        = '/v5/market/kline'
    _TRADE_PATH  = '/v5/market/recent-trade'
    _BATCH_LIMIT = 200
    _RATE_DELAY  = 0.15
    _MAX_TRIES   = 8

    def __init__(self) -> None:
        self._session = requests.Session()
        self._log     = get_logger(self.__class__.__name__)

    def fetch_klines(self, symbol: str, interval: str, start_ms: int, end_ms: int) -> list:
        all_candles: list = []
        cursor_end = end_ms
        while cursor_end > start_ms:
            batch = self._fetch_batch_retry(symbol, interval, start_ms, cursor_end)
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

    def fetch_recent_trades(self, symbol: str, limit: int = 1000) -> list:
        """Recent public trades (newest-first) for the (re)start gap-fill. Dedupe-safe:
        each trade's `execId` == the WS publicTrade `i` (verified — same exec UUID), so
        INSERT IGNORE on the trade_id ignores overlap with the live stream. Returns
        [{trade_id, ts, price, size, side}]."""
        params = {'category': 'linear', 'symbol': symbol, 'limit': min(int(limit), 1000)}
        resp = self._session.get(self._BASE + self._TRADE_PATH, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get('retCode') != 0:
            raise RuntimeError(f'Bybit recent-trade error: {data}')
        return [{'trade_id': t['execId'], 'ts': int(t['time']), 'price': float(t['price']),
                 'size': float(t['size']), 'side': t['side'].lower()}
                for t in data['result']['list']]

    def _fetch_batch_retry(self, symbol: str, interval: str, start_ms: int, end_ms: int) -> list:
        """_fetch_batch with exponential backoff on rate limits / transient network
        errors — so a 10006 mid-pagination recovers instead of silently truncating
        the backfill. Raises (loud) only after exhausting retries."""
        delay = 1.0
        for attempt in range(1, self._MAX_TRIES + 1):
            try:
                return self._fetch_batch(symbol, interval, start_ms, end_ms)
            except (_RateLimited, requests.RequestException) as e:
                if attempt == self._MAX_TRIES:
                    raise RuntimeError(f'kline fetch failed after {attempt} tries: {e}') from e
                self._log.warning(f'{type(e).__name__}: {str(e)[:60]} — backing off '
                                  f'{delay:.0f}s (try {attempt}/{self._MAX_TRIES})')
                time.sleep(delay)
                delay = min(delay * 2, 30.0)

    def _fetch_batch(self, symbol: str, interval: str, start_ms: int, end_ms: int) -> list:
        params = {'category': 'linear', 'symbol': symbol, 'interval': interval,
                  'start': start_ms, 'end': end_ms, 'limit': self._BATCH_LIMIT}
        resp = self._session.get(self._BASE + self._PATH, params=params, timeout=10)
        resp.raise_for_status()                                   # HTTP/network → retry
        data = resp.json()
        code = data.get('retCode')
        if code == 10006:                                        # rate limit → retry
            raise _RateLimited(data.get('retMsg', 'rate limit'))
        if code != 0:                                            # other API error → loud
            raise RuntimeError(f'Bybit API error: {data}')
        return [{'timestamp': int(r[0]), 'open': float(r[1]), 'high': float(r[2]),
                 'low': float(r[3]), 'close': float(r[4]), 'volume': float(r[5])}
                for r in data['result']['list']]
