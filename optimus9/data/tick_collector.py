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
import os
import threading
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
from ..data.bybit_websocket_client import BybitWebSocketClient, RestartGate
from ..data.ws_liveness import WsLiveness

# THE SOCKETS (Joe 1002, from his 0708 `docs/second_ws_spec.md`): two connections to DIFFERENT hosts, both
# writing into `ticks`; INSERT IGNORE on (tk_tp_pk, tk_trade_id) merges them, so a trade dropped on one
# lands via the other. Config, not code: O9_TICK_ENDPOINTS = "url|stall_s|label,url|stall_s|label".
#   stall_s   Joe 1002: "auto restart on any tick freeze that dwells more than 60 seconds"
#   label     names the socket's per-second liveness log, ws_liveness_<label>.log (outage item #1)
_ENDPOINTS = os.environ.get(
    'O9_TICK_ENDPOINTS',
    'wss://stream.bybit.com/v5/public/linear|60|collector,wss://stream.bytick.com/v5/public/linear|60|collector2')
_RESTART_OFFSET_S = float(os.environ.get('O9_TICK_RESTART_OFFSET_S', '10'))   # Joe 1002: "10s is enough, your call"
_LIVENESS_DIR = os.environ.get('O9_LIVENESS_DIR', '/home/joe/thecodes')


def _endpoints():
    out = []
    for part in _ENDPOINTS.split(','):
        url, stall, label = part.strip().split('|')
        out.append((url, float(stall), label))
    return out
from .._helpers import _ms_to_iso


class TickCollector:
    """
    Subscribes to Bybit public trade stream on EVERY socket in O9_TICK_ENDPOINTS (two by default).
    Commits each WebSocket message to the ticks table immediately — no buffering.
    Prunes ticks older than 7 days hourly - the FIRST socket only, so N sockets never race the DELETE.

    Each socket runs in its own thread with its own DB connection (MySQL connections are not
    thread-safe) and its own asyncio loop; every socket funnels through the one `_on_message`.
    Each socket auto-restarts after its stall_s with no trades; the shared RestartGate keeps any two
    restarts at least _RESTART_OFFSET_S apart; every reconnect runs the REST gap-fill (Joe 1002).
    """

    _TOPIC_PREFIX    = 'publicTrade'
    _PRUNE_KEEP_DAYS = 7

    def __init__(self, db: DatabaseManager) -> None:
        self._db         = db
        self._gate       = RestartGate(_RESTART_OFFSET_S)
        self._log        = get_logger(self.__class__.__name__)
        self._log.setLevel('INFO')  # r07: drop per-tick DEBUG flooding debug.log
        self._last_prune = time.time()

    def run(self, tp_pk: int, symbol: str) -> None:
        self._log.info(f'Collecting ticks: {symbol}')
        # WS first (no missed live ticks); backfill the (re)start gap in a parallel thread —
        # overlap with the live stream is deduped by trade_id.
        threading.Thread(target=self._backfill_recent, args=(tp_pk, symbol), daemon=True).start()
        eps = _endpoints()
        for i, ep in enumerate(eps[1:], 1):
            threading.Thread(target=self._socket, args=(ep, tp_pk, symbol, None, False),
                             name='ticks-%s' % ep[2], daemon=True).start()
        self._socket(eps[0], tp_pk, symbol, self._db, True)        # the first socket owns the process

    def _socket(self, ep, tp_pk: int, symbol: str, db, prune: bool) -> None:
        url, stall_s, label = ep
        if db is None:                                             # a thread's own connection
            from ..config import get_db_config
            db = DatabaseManager(**get_db_config())
            db.connect()
        self._log.info(f'socket {label}: {url}, auto-restart after {stall_s:.0f}s without trades')

        def on_connect(reconnect: bool) -> None:
            if reconnect:                                          # Joe 1002: gap-fill after reconnect
                threading.Thread(target=self._backfill_recent, args=(tp_pk, symbol, f'{label} reconnect'),
                                 daemon=True).start()
        BybitWebSocketClient(
            url=url, liveness=WsLiveness(os.path.join(_LIVENESS_DIR, f'ws_liveness_{label}.log'), label),
            stall_s=stall_s, on_connect=on_connect, restart_gate=self._gate,
        ).stream(f'{self._TOPIC_PREFIX}.{symbol}', lambda msg: self._on_message(db, tp_pk, msg, prune))

    def _backfill_recent(self, tp_pk: int, symbol: str, why: str = 'startup') -> None:
        """Fill the (re)start gap: pull recent public trades via REST and INSERT IGNORE.
        Own DB connection (MySQL conns aren't thread-safe); overlap with the live WS is
        deduped by trade_id. Best-effort — a failure just leans on the WS."""
        try:
            from ..config import get_db_config
            from .bybit_kline_client import BybitKlineClient
            db = DatabaseManager(**get_db_config())
            db.connect()
            trades = BybitKlineClient().fetch_recent_trades(symbol)
            db.executemany(
                '''INSERT IGNORE INTO ticks (tk_tp_pk, tk_trade_id, tk_timestamp, tk_price, tk_volume, tk_side)
                   VALUES (%s,%s,%s,%s,%s,%s)''',
                [(tp_pk, t['trade_id'], t['ts'], t['price'], t['size'], t['side']) for t in trades])
            db.disconnect()
            self._log.info(f'{why} backfill: merged {len(trades)} recent trades (gap-fill)')
        except Exception as e:
            self._log.error(f'{why} backfill failed (leaning on WS): {e}')

    def _on_message(self, db, tp_pk: int, msg: dict, prune: bool = True) -> None:
        trades = msg.get('data', [])
        if not trades:
            return
        db.executemany(
            '''INSERT IGNORE INTO ticks (tk_tp_pk, tk_trade_id, tk_timestamp, tk_price, tk_volume, tk_side)
               VALUES (%s,%s,%s,%s,%s,%s)''',
            [(tp_pk, t.get('i'), int(t['T']), float(t['p']), float(t['v']),
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
        if prune and now - self._last_prune >= 3600:
            self._prune(tp_pk)
            self._last_prune = now

    def _prune(self, tp_pk: int) -> None:
        cutoff = int((datetime.now(timezone.utc) - timedelta(days=self._PRUNE_KEEP_DAYS)).timestamp() * 1000)
        self._db.execute(
            'DELETE FROM ticks WHERE tk_tp_pk = %s AND tk_timestamp < %s', (tp_pk, cutoff),
        )
        self._log.info(f'Ticks pruned — keeping last {self._PRUNE_KEEP_DAYS} days')
