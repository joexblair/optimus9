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
        self._log.setLevel('INFO')  # r07: drop per-bar DEBUG flooding debug.log

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
            '''SELECT tk_timestamp, tk_price, tk_volume FROM ticks
               WHERE tk_tp_pk = %s AND tk_timestamp >= %s AND tk_timestamp < %s
               ORDER BY tk_timestamp ASC''',
            (tp_pk, start_ms, end_ms), fetch=True,
        )
        if not rows:
            self._log.debug(f'No ticks for bar {start_ms}')
            return

        tss     = [int(r['tk_timestamp']) for r in rows]
        prices  = [float(r['tk_price'])   for r in rows]
        volumes = [float(r['tk_volume'])  for r in rows]
        o, h, l, c = prices[0], max(prices), min(prices), prices[-1]

        self._check_continuity(tp_pk, start_ms, o, c, tss, prices)

        self._db.execute(
            '''INSERT INTO kline_collection
                   (kc_tp_pk, kc_timestamp, kc_open, kc_high, kc_low, kc_close, kc_volume)
               VALUES (%s,%s,%s,%s,%s,%s,%s)
               ON DUPLICATE KEY UPDATE
                   kc_open=VALUES(kc_open), kc_high=VALUES(kc_high),
                   kc_low=VALUES(kc_low),   kc_close=VALUES(kc_close),
                   kc_volume=VALUES(kc_volume)''',
            (tp_pk, start_ms, o, h, l, c, sum(volumes)),
        )
        self._log.debug(f'Bar ts={start_ms}  o={o} h={h} l={l} c={c} v={sum(volumes):.4f}')

    def _check_continuity(self, tp_pk, start_ms, open_, close_, tss, prices) -> None:
        """Quick-and-dirty live tape gate: on a gapless tape a new bar's open == the
        prior bar's close. Fire a rich ERROR on a non-gapless seam OR a missing-bar
        gap, so the fault is visible the instant it happens (incl. how late the first
        tick lands — the prime suspect for the open drift)."""
        prev = self._db.execute(
            '''SELECT kc_timestamp, kc_close FROM kline_collection
               WHERE kc_tp_pk = %s AND kc_timestamp < %s
               ORDER BY kc_timestamp DESC LIMIT 1''',
            (tp_pk, start_ms), fetch=True,
        )
        if not prev:
            return
        p_ts    = int(prev[0]['kc_timestamp'])
        p_close = float(prev[0]['kc_close'])
        bar     = self._BAR_S * 1000
        f_off   = tss[0]  - start_ms          # ms the first tick lands after bar open
        l_off   = tss[-1] - start_ms
        def _u(ms): return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime('%H:%M:%S')

        if p_ts < start_ms - bar:
            missing = (start_ms - bar - p_ts) // bar
            self._log.error(
                f'KLINE GAP: {missing} missing bar(s) before {_u(start_ms)} '
                f'(ts={start_ms}). prev {_u(p_ts)} close={p_close}; this open={open_}; '
                f'{len(prices)} ticks, first +{f_off}ms / last +{l_off}ms')
        elif abs(open_ - p_close) > 1e-12:
            d   = open_ - p_close
            bps = (d / p_close * 1e4) if p_close else 0.0
            self._log.error(
                f'KLINE NON-GAPLESS @ {_u(start_ms)} (ts={start_ms}): '
                f'open {open_} != prev close {p_close}  jump={d:+.8f} ({bps:+.2f} bps) | '
                f'h={max(prices)} l={min(prices)} c={close_} | '
                f'{len(prices)} ticks, first +{f_off}ms (p={prices[0]}) '
                f'last +{l_off}ms (p={prices[-1]})')
