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
    _MAX_FILL_BARS = 720          # cap live forward-fill at ~1h; bigger gaps → backfiller
    _COMMIT_DELAY_MS = 500        # print just past the seam (ticks commit <1s) — Joe 2026-06-06
    _REBUILD_BARS    = 3          # re-process the last N bars each cycle to absorb late ticks

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)
        self._log.setLevel('INFO')  # r07: drop per-bar DEBUG flooding debug.log

    def run(self, tp_pk: int) -> None:
        self._log.info('BarBuilder started')
        while True:
            self._sleep_to_boundary()                              # wake at the seam + commit delay
            bar          = self._BAR_S * 1000
            boundary_ms  = (int(time.time() * 1000) // bar) * bar   # the seam we just crossed
            latest_start = boundary_ms - bar                        # print the JUST-closed window now
            self._catch_up(tp_pk, latest_start)

    def _sleep_to_boundary(self) -> None:
        """Wake just past each 5s seam — the commit delay lets ticks land, so the bar
        that just closed is printed at seam+delay (≈:50.5 for the :45 bar)."""
        now    = time.time()
        target = math.ceil(now / self._BAR_S) * self._BAR_S + self._COMMIT_DELAY_MS / 1000.0
        time.sleep(max(0.0, target - now))

    def _catch_up(self, tp_pk: int, latest_start: int) -> None:
        """Build the just-closed bar AND re-process the last _REBUILD_BARS bars so late
        ticks update already-printed rows (_build_one upserts). GAPLESS: a window with
        ticks opens at the prior close; an empty window is a doji at the prior close. A
        gap larger than the cap is left to the backfiller."""
        bar  = self._BAR_S * 1000
        prev = self._db.execute(
            '''SELECT kc_timestamp, kc_close FROM kline_collection
               WHERE kc_tp_pk = %s ORDER BY kc_timestamp DESC LIMIT 1''',
            (tp_pk,), fetch=True,
        )
        if not prev:
            self._build_one(tp_pk, latest_start, None)            # cold start
            return
        last_stored = int(prev[0]['kc_timestamp'])
        last_close  = float(prev[0]['kc_close'])
        new_first   = last_stored + bar

        # big forward gap → print latest only, backfiller owns the rest (no re-build)
        if new_first <= latest_start and (latest_start - new_first) // bar + 1 > self._MAX_FILL_BARS:
            self._log.warning(
                f'gap > {self._MAX_FILL_BARS} bars to {latest_start}; building latest '
                'only — backfiller owns the rest')
            self._build_one(tp_pk, latest_start, last_close)
            return

        # re-process the last _REBUILD_BARS bars (late-tick absorption) + any new bars
        walk_from = min(new_first, latest_start - self._REBUILD_BARS * bar)
        anchor = self._db.execute(
            '''SELECT kc_close FROM kline_collection
               WHERE kc_tp_pk = %s AND kc_timestamp = %s''', (tp_pk, walk_from - bar), fetch=True)
        if anchor:
            cur = float(anchor[0]['kc_close'])
        else:                                                     # re-build window predates stored data
            walk_from, cur = new_first, last_close                # forward-only, gapless from last close
        if walk_from > latest_start:
            return                                                # nothing to do (already current)
        for ws in range(walk_from, latest_start + bar, bar):
            cur = self._build_one(tp_pk, ws, cur)

    def _build_one(self, tp_pk: int, start_ms: int, prior_close):
        """Build+upsert one 5s bar. open = prior_close (gapless) when known; empty
        window → doji at prior_close. Returns the bar's close (the next open)."""
        bar  = self._BAR_S * 1000
        rows = self._db.execute(
            '''SELECT tk_timestamp, tk_price, tk_volume FROM ticks
               WHERE tk_tp_pk = %s AND tk_timestamp >= %s AND tk_timestamp < %s
               ORDER BY tk_timestamp ASC''',
            (tp_pk, start_ms, start_ms + bar), fetch=True,
        )
        if rows:
            tss    = [int(r['tk_timestamp']) for r in rows]
            prices = [float(r['tk_price'])   for r in rows]
            vol    = sum(float(r['tk_volume']) for r in rows)
            o = float(prior_close) if prior_close is not None else prices[0]
            c = prices[-1]
            h = max([o] + prices)
            l = min([o] + prices)
            if prior_close is not None:
                self._check_continuity(tp_pk, start_ms, o, c, tss, prices)   # regression guard
        elif prior_close is not None:
            o = h = l = c = float(prior_close); vol = 0.0        # gapless doji (no trades)
        else:
            return None                                          # cold start, no ticks
        self._db.execute(
            '''INSERT INTO kline_collection
                   (kc_tp_pk, kc_timestamp, kc_open, kc_high, kc_low, kc_close, kc_volume)
               VALUES (%s,%s,%s,%s,%s,%s,%s)
               ON DUPLICATE KEY UPDATE
                   kc_open=VALUES(kc_open), kc_high=VALUES(kc_high),
                   kc_low=VALUES(kc_low),   kc_close=VALUES(kc_close),
                   kc_volume=VALUES(kc_volume)''',
            (tp_pk, start_ms, o, h, l, c, vol),
        )
        return c

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
