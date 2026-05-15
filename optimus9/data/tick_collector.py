"""
TickCollector — see class docstring for purpose, Pine alignment, and design notes.
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
from ..data.bybit_websocket_client import BybitWebSocketClient
from .._helpers import _ms_to_iso


class TickCollector:
    """
    Subscribes to Bybit public trade stream.
    Commits each WebSocket message to the ticks table immediately — no buffering.
    Prunes ticks older than 7 days hourly.
    """

    _TOPIC_PREFIX    = 'publicTrade'
    _PRUNE_KEEP_DAYS = 7

    def __init__(self, db: DatabaseManager) -> None:
        self._db         = db
        self._ws         = BybitWebSocketClient()
        self._log        = get_logger(self.__class__.__name__)
        self._last_prune = time.time()

    def run(self, tp_pk: int, symbol: str) -> None:
        self._log.info(f'Collecting ticks: {symbol}')
        self._ws.stream(
            f'{self._TOPIC_PREFIX}.{symbol}',
            lambda msg: self._on_message(tp_pk, msg),
        )

    def _on_message(self, tp_pk: int, msg: dict) -> None:
        trades = msg.get('data', [])
        if not trades:
            return
        self._db.executemany(
            '''INSERT IGNORE INTO ticks (tk_tp_pk, tk_timestamp, tk_price, tk_volume, tk_side)
               VALUES (%s,%s,%s,%s,%s)''',
            [(tp_pk, int(t['T']), float(t['p']), float(t['v']),
              'buy' if t['S'] == 'Buy' else 'sell')
             for t in trades],
        )
        for t in trades:
            self._log.debug(
                f'{t["s"]:16s}  {"BUY " if t["S"] == "Buy" else "SELL"}'
                f'  p={float(t["p"]):>14.8f}  v={float(t["v"]):>12.4f}'
                f'  {_ms_to_iso(int(t["T"]))}'
            )
        now = time.time()
        if now - self._last_prune >= 3600:
            self._prune(tp_pk)
            self._last_prune = now

    def _prune(self, tp_pk: int) -> None:
        cutoff = int((datetime.now(timezone.utc) - timedelta(days=self._PRUNE_KEEP_DAYS)).timestamp() * 1000)
        self._db.execute(
            'DELETE FROM ticks WHERE tk_tp_pk = %s AND tk_timestamp < %s', (tp_pk, cutoff),
        )
        self._log.info(f'Ticks pruned — keeping last {self._PRUNE_KEEP_DAYS} days')
