"""
Pk5sGateComputer — see class docstring for purpose, Pine alignment, and design notes.
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
from ..compute.indicator_computer import IndicatorComputer


class Pk5sGateComputer:
    """
    The 5s PK vote machine. Pine s5_pk_final equivalent, replicated in Python.

    Purpose
    -------
    Produces a directional gate from a multi-line weighted PK vote, evaluated
    every 5s bar. Each contributing line votes 'long', 'short', or 'neutral'
    based on its slope vs DEMA slope; votes accumulate with per-line weights;
    PM (price-matched) votes suppress the opposing bucket; ratios are
    thresholded; a decision-delay countdown gates final fires.

    Output is sign-inverted from Pine s5_pk_final (Pine +1=long → Python -1)
    so it plugs into IndicatorComputer.fold_gates alongside bny30M/p as a
    third OOB-equivalent gate. After folding, PKDetector consumes oob_side
    and emits/suppresses per-line PK signals.

    Pine alignment
    --------------
    Mirrors bbstr.pine sections (line numbers may drift; concept-stable):
      • f_pk_state      → per-line state (±1 divergence, ±2 PM, 0 neutral)
                          (Pine line 1368, replicated here in _states_standard)
      • f_vote          → state → long/short/neutral buckets at full weight
                          (Pine line 1508)
      • PM suppression  → adj_long  = max(0, long_pts  − pm_short_wt × pm_supp)
                          adj_short = max(0, short_pts − pm_long_wt  × pm_supp)
                          (Pine line 1613-1614)
      • ratio scaling   → (adj_x / active_w) × 10
                          denominator includes neutrals (Pine pm_option_a=false)
                          (Pine line 1616-1618)
      • decision delay  → N-bar persistence before fire; gate-open check only
                          at countdown start, in-progress countdowns run to
                          completion. At the 5s level there is no upstream gate
                          to check.
                          (Pine line 1624-1648)

    Pk5sGateComputer's f_pk_state window matches Pine exactly: covers
    line[i - upper + 1 : i - lower + 1] of length pool_range bars. The
    existing PKDetector carries a 1-bar wider window — intentionally left
    as-is for continuity with the 30-day grind dataset. See PKDetector
    docstring and round spec 260514 for rationale.

    Design notes
    ------------
    PM divergence (captured for the codebase, not just chat):

        PM_LONG means "the bullish lines and the price proxy are organically
        aligned — no visible divergence here." That alignment is the opposite
        of divergence; it's evidence of ongoing directional strength. The 0.4
        suppression weight lets that evidence reduce opposing votes by 40% of
        its own weight, without itself voting directionally. Gating the
        verdict out when PM did the heavy lifting would contradict trusting
        PM evidence at all.

    Dead zone: not implemented. With the ×10 ratio scaling, threshold 7.5
    mathematically forces a ≥5-point ratio gap — already a strong condition.

    Trigger modes (per-line, via tcev_trigger_mode):
      • 'standard_pk' — f_pk_state evaluates every history-valid bar.
      • 'roc_curl'    — evaluates only on bars where line slope changed by
                        more than tcev_roc_threshold° from the prior bar.
                        Peak = line[i-1] (the spike); DEMA anchor = dema[i-1].
                        Used by b30M / b30b in the future trend machine.
                        No seed rows use this mode in the 5s gate round.

    Round spec: 260514_pk5s_spec.md
    """

    _PM_LONG  =  2.0
    _PM_SHORT = -2.0

    def __init__(self, db: 'DatabaseManager') -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    # ── public ──────────────────────────────────────────────────────────────
    def compute(self, tce_pk: int,
                base_df:  pd.DataFrame,
                dema:     np.ndarray,
                params:   dict,
                midpoint: float = 50.0) -> np.ndarray:
        """
        Build the OOB-equivalent gate array for one pk_5s tce row.

        Parameters
        ----------
        tce_pk : the pk_5s test_config_extensions row PK
        base_df : 5s OHLCV
        dema : DEMA series on the base 5s (same dema as PKDetector consumes)
        params : tce_params dict (pool_c, pool_w, pool_slope, pool_range,
                 threshold_long, threshold_short, pm_suppression,
                 decision_delay)
        midpoint : f_pk_state midpoint, default 50

        Returns
        -------
        int8 array length len(base_df), sign-inverted vs Pine s5_pk_final:
          -1 = long PK fired (oob_side equivalent: LO OOB → expected = +1 long)
          +1 = short PK fired (oob_side equivalent: HI OOB → expected = -1 short)
           0 = idle / suppressed by decision delay / no verdict
        """
        votes = self._load_votes(tce_pk)
        n     = len(base_df)
        if not votes:
            self._log.warning(f'pk_5s tce_pk={tce_pk}: no active vote lines')
            return np.zeros(n, dtype=np.int8)

        pool_c       = int(params['pool_c'])
        pool_w       = int(params['pool_w'])
        pool_range   = int(params['pool_range'])
        slope_floor  = float(params['pool_slope'])
        thr_long     = float(params['threshold_long'])
        thr_short    = float(params['threshold_short'])
        pm_supp      = float(params['pm_suppression'])
        decision_dly = int(params['decision_delay'])

        long_pts    = np.zeros(n, dtype=np.float64)
        short_pts   = np.zeros(n, dtype=np.float64)
        neutral_pts = np.zeros(n, dtype=np.float64)
        pm_long_wt  = np.zeros(n, dtype=np.float64)
        pm_short_wt = np.zeros(n, dtype=np.float64)

        for v in votes:
            line = self._compute_line(v, base_df)

            # Trigger-mode dispatch. roc_curl produces a single state array
            # used for both pool labels — pool_c/pool_w don't define different
            # evaluations in that mode, only how much weight contributes.
            if v['tcev_trigger_mode'] == 'roc_curl':
                threshold = float(v.get('tcev_roc_threshold') or 45.0)
                s_curl    = self._states_roc_curl(line, dema, threshold, midpoint)
                pool_states = {'close': s_curl, 'wide': s_curl}
            else:
                pool_states = {
                    'close': self._states_standard(line, dema, pool_c, pool_range, slope_floor, midpoint),
                    'wide':  self._states_standard(line, dema, pool_w, pool_range, slope_floor, midpoint),
                }

            for pool_label in ('close', 'wide'):
                weight = int(v[f'tcev_weight_{pool_label}'])
                if weight == 0:
                    continue
                states = pool_states[pool_label]

                # Pine: f_vote — PM sentinels route to neutral at full weight
                long_pts    += np.where(states ==  1.0, weight, 0.0)
                short_pts   += np.where(states == -1.0, weight, 0.0)
                neutral_pts += np.where(
                    (states == 0.0) | (states == self._PM_LONG) | (states == self._PM_SHORT),
                    weight, 0.0
                )
                pm_long_wt  += np.where(states == self._PM_LONG,  weight, 0.0)
                pm_short_wt += np.where(states == self._PM_SHORT, weight, 0.0)

        # Pine: PM suppression post-processing
        adj_long  = np.maximum(0.0, long_pts  - pm_short_wt * pm_supp)
        adj_short = np.maximum(0.0, short_pts - pm_long_wt  * pm_supp)
        active_w  = adj_long + adj_short + neutral_pts        # pm_option_a=false

        with np.errstate(invalid='ignore', divide='ignore'):
            long_ratio  = np.where(active_w > 0, (adj_long  / active_w) * 10.0, 0.0)
            short_ratio = np.where(active_w > 0, (adj_short / active_w) * 10.0, 0.0)

        pk_raw = np.where(long_ratio  > thr_long,   1,
                 np.where(short_ratio > thr_short, -1, 0)).astype(np.int8)

        s5_pk_final = self._apply_decision_delay(pk_raw, decision_dly)

        fires_long  = int((s5_pk_final ==  1).sum())
        fires_short = int((s5_pk_final == -1).sum())
        self._log.info(
            f'pk_5s tce_pk={tce_pk}: raw fires {int((pk_raw != 0).sum())}, '
            f'after {decision_dly}-bar delay {fires_long + fires_short} '
            f'({fires_long}L / {fires_short}S)'
        )

        # Sign-invert for oob_side convention (Pine s5_pk_final +1 = long
        # → here -1, so PKDetector's `expected = -side` yields +1 long).
        return (-s5_pk_final).astype(np.int8)

    # ── data loading ────────────────────────────────────────────────────────
    def _load_votes(self, tce_pk: int) -> list:
        """Active vote rows joined with their indicator_configs context."""
        return self._db.execute(
            '''SELECT tcev.tcev_pk, tcev.tcev_weight_close, tcev.tcev_weight_wide,
                      tcev.tcev_trigger_mode, tcev.tcev_roc_threshold,
                      ic.ic_pk, ic.ic_line_type, ic.ic_src,
                      ic.ic_bb_len, ic.ic_bb_mult,
                      ic.ic_k_len,  ic.ic_rsi_len, ic.ic_stc_len,
                      itf.itf_seconds AS ic_itf_seconds,
                      s.is_prefix, itf.itf_label, il.il_suffix
               FROM test_config_ext_votes tcev
               JOIN indicator_configs    ic  ON ic.ic_pk    = tcev.tcev_ic_pk
               JOIN indicator_timeframes itf ON itf.itf_pk  = ic.ic_itf_pk
               JOIN indicator_series     s   ON s.is_pk     = ic.ic_is_pk
               JOIN indicator_lines      il  ON il.il_pk    = ic.ic_il_pk
               WHERE tcev.tcev_tce_pk    = %s
                 AND tcev.tcev_is_active = 1
                 AND (tcev.tcev_weight_close > 0 OR tcev.tcev_weight_wide > 0)''',
            (tce_pk,), fetch=True,
        )

    @staticmethod
    def _compute_line(v: dict, base_df: pd.DataFrame) -> np.ndarray:
        """
        Compute one indicator line on the base 5s timeline.

        For 5s-native lines: direct compute, no resampling. For higher-TF
        lines: forward-fill resample (matches Pine request.security without
        lookahead). This method is called by the 5s gate; for the 5s seed
        all six contributors are 5s-native so the forward-fill path is unused.
        """
        line_seconds = int(v['ic_itf_seconds'])
        src_df = base_df if line_seconds == 5 else IndicatorComputer.resample(base_df, line_seconds)
        src    = IndicatorComputer.build_source(src_df, v['ic_src'])
        if v['ic_line_type'] == 'bb':
            raw = IndicatorComputer.f_bb(src, int(v['ic_bb_len']), float(v['ic_bb_mult']))
        else:
            raw = IndicatorComputer.f_k(src, int(v['ic_rsi_len']),
                                        int(v['ic_stc_len']), int(v['ic_k_len']))
        return raw if line_seconds == 5 else IndicatorComputer.align_to_base(raw, src_df, base_df)

    # ── per-line state evaluators ──────────────────────────────────────────
    @staticmethod
    def _states_standard(line: np.ndarray, dema: np.ndarray,
                         bars: int, pool_range: int, slope_floor: float,
                         midpoint: float) -> np.ndarray:
        """
        Vectorised f_pk_state for one line at one pool depth (standard_pk mode).

        Pine: f_pk_state, bbstr.pine line 1368. Multiplier fixed at 1 (5s
        native — higher-TF lines forward-fill before reaching this function).

        Window matches Pine `ta.highest(line[lower], window)` exactly: covers
        line[i - upper + 1 : i - lower + 1], length = pool_range bars.

        Returns float (n,) of {NaN, 0.0, ±1.0, ±2.0}.
        """
        n      = len(line)
        half   = pool_range // 2
        lower  = bars - half
        upper  = bars + half
        center = bars
        win    = upper - lower             # = pool_range

        if upper + 1 >= n or win <= 0:
            return np.full(n, np.nan)

        s        = pd.Series(line)
        shifted  = s.shift(lower)          # shifted[i] = line[i - lower]
        roll_hi  = shifted.rolling(win, min_periods=win).max().to_numpy()
        roll_lo  = shifted.rolling(win, min_periods=win).min().to_numpy()
        # Net effect: roll_hi[i] = max(line[i - upper + 1 .. i - lower])

        # DEMA anchor at i - center
        dema_anchor = np.full(n, np.nan)
        if center < n:
            dema_anchor[center:] = dema[:n - center]

        peak        = np.where(line > midpoint, roll_hi, roll_lo)
        line_slope  = line - peak
        price_slope = dema - dema_anchor
        slope_diff  = np.abs(line_slope - price_slope)

        with np.errstate(invalid='ignore'):
            diverge = np.sign(line_slope) != np.sign(price_slope)
            noise   = slope_diff <= slope_floor
            result  = np.where(
                diverge,
                np.where(line_slope > 0,  1.0, -1.0),
                np.where(line_slope > 0,  Pk5sGateComputer._PM_LONG,
                                          Pk5sGateComputer._PM_SHORT),
            )
            result = np.where(noise, 0.0, result)

        invalid = (
            np.isnan(line) | np.isnan(dema) | np.isnan(dema_anchor)
            | np.isnan(roll_hi) | np.isnan(roll_lo)
        )
        return np.where(invalid, np.nan, result)

    @staticmethod
    def _states_roc_curl(line: np.ndarray, dema: np.ndarray,
                         threshold_deg: float, midpoint: float) -> np.ndarray:
        """
        Vectorised f_pk_state for one line in roc_curl trigger mode.

        Triggers only on bars where the line's slope changed by more than
        threshold_deg from the prior bar. On a curl bar i:
          peak       = line[i-1]       (the spike — the bar before the curl)
          dema_anchor = dema[i-1]      (paired with the prior-bar peak)
          line_slope  = line[i] - line[i-1]
          price_slope = dema[i] - dema[i-1]
          pk_state    = ±1 divergence / ±2 PM via sign comparison

        slope_floor is not applied — the ROC trigger itself is the noise
        filter (only non-subtle moves reach evaluation).

        Returns float (n,) of {NaN, 0.0, ±1.0, ±2.0}. Bars below the curl
        threshold return NaN (no vote contribution).

        Not exercised by the 5s gate seed (all six contributors use
        standard_pk). Pre-built for b30M / b30b in the future trend machine.
        """
        n = len(line)
        if n < 3:
            return np.full(n, np.nan)

        # ROC curl trigger: change in 1-bar slope angle from i-1 to i.
        slope_prev = np.diff(line, prepend=np.nan)          # slope_prev[i] = line[i] - line[i-1]
        slope_curr = slope_prev                              # at i, "current" slope is the i-1→i delta
        slope_back = np.roll(slope_prev, 1)                  # at i, prior slope is i-2→i-1 delta
        slope_back[0] = np.nan
        with np.errstate(invalid='ignore'):
            curl_deg = np.abs(
                np.arctan(slope_curr) - np.arctan(slope_back)
            ) * (180.0 / np.pi)
        fires = curl_deg > threshold_deg

        # 1-bar slopes for the PK decision
        line_slope  = slope_prev                             # line[i] - line[i-1]
        dema_anchor = np.roll(dema, 1); dema_anchor[0] = np.nan
        price_slope = dema - dema_anchor

        out = np.full(n, np.nan)
        with np.errstate(invalid='ignore'):
            diverge = np.sign(line_slope) != np.sign(price_slope)
            states  = np.where(
                diverge,
                np.where(line_slope > 0,  1.0, -1.0),
                np.where(line_slope > 0,  Pk5sGateComputer._PM_LONG,
                                          Pk5sGateComputer._PM_SHORT),
            )
            # If both slopes are exactly zero, mark neutral (no signal)
            both_zero = (line_slope == 0.0) & (price_slope == 0.0)
            states    = np.where(both_zero, 0.0, states)

        valid = fires & ~np.isnan(line_slope) & ~np.isnan(price_slope)
        out   = np.where(valid, states, np.nan)
        return out

    # ── decision-delay state machine ───────────────────────────────────────
    @staticmethod
    def _apply_decision_delay(pk_raw: np.ndarray, delay: int) -> np.ndarray:
        """
        Pine: bbstr.pine line 1624-1648.

        State machine (no upstream gate at the 5s level, so the Pine
        `_gate_open` branch collapses):

            if pk_raw != 0:
                if pk_raw == pending:
                    countdown -= 1
                    if countdown == 0: fire = pk_raw
                else:
                    pending   = pk_raw
                    countdown = delay
                    fire      = 0
            else:
                pending = 0; countdown = 0; fire = 0

        Sequential by necessity — the state machine doesn't vectorise cleanly.
        Loop is in plain Python; n is typically a few hundred thousand 5s bars
        for a 30-day grind, well within tolerable single-pass loop time.
        """
        n         = len(pk_raw)
        out       = np.zeros(n, dtype=np.int8)
        pending   = 0
        countdown = 0
        for i in range(n):
            d = int(pk_raw[i])
            if d != 0:
                if d == pending:
                    countdown = max(0, countdown - 1)
                    if countdown == 0:
                        out[i] = d
                else:
                    pending   = d
                    countdown = delay
            else:
                pending   = 0
                countdown = 0
        return out
