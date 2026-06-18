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
from ..compute.pk_vote_machine    import PKVoteMachine


class Pk5sGateComputer:
    """
    The 5s PK vote machine. Pine s5_pk_final equivalent, replicated in Python.

    Purpose
    -------
    Produces a directional gate from a multi-line weighted PK vote, evaluated
    every 5s bar. Each contributing line votes 'long', 'short', or 'neutral'
    based on its slope vs DEMA slope; votes accumulate with per-line weights;
    PM (price-matched) votes suppress the opposing bucket; ratios are
    thresholded; pk_raw becomes s5_pk_final directly (r07: decision delay
    removed).

    r07 Step 2: vote-folding math extracted to PKVoteMachine. Pk5sGateComputer
    is now a thin composer — it computes per-line states (via _states_standard
    or _states_roc_curl), flattens them into the (pool_id, probe_label)-keyed
    dict shape PKVoteMachine expects, and delegates the math. The class
    docstring's "vote machine" phrasing refers to the conceptual pattern;
    the actual aggregation now lives in PKVoteMachine.

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
                          (Pine line 1508) — now in PKVoteMachine.aggregate
      • PM suppression  → adj_long  = max(0, long_pts  − pm_short_wt × pm_supp)
                          adj_short = max(0, short_pts − pm_long_wt  × pm_supp)
                          (Pine line 1613-1614) — now in PKVoteMachine.aggregate
      • ratio scaling   → (adj_x / active_w) × 10
                          denominator includes neutrals (Pine pm_option_a=false)
                          (Pine line 1616-1618) — now in PKVoteMachine.aggregate
      • decision delay  → REMOVED in r07. Pine retains it for validation
                          comparisons. See r07_vote_machine_design.md.

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

    def __init__(self, db: 'DatabaseManager',
                 vote_machine: Optional[PKVoteMachine] = None) -> None:
        """
        Parameters
        ----------
        db : DatabaseManager
            Used by _load_votes for the tce vote rows lookup.
        vote_machine : PKVoteMachine, optional
            Injected vote machine instance. When None (default), compute()
            constructs a fresh PKVoteMachine using params['pm_suppression'].
            Injection point exists for r08 multi-line / SnF work where a
            single vote machine config may apply across multiple compute()
            calls; production single-config path uses the default.
        """
        self._db           = db
        self._log          = get_logger(self.__class__.__name__)
        self._vote_machine = vote_machine

    # ── public ──────────────────────────────────────────────────────────────
    def compute(self, tce_pk: int,
                base_df:  pd.DataFrame,
                dema:     np.ndarray,
                params:   dict,
                midpoint: float = 50.0,
                vote_overrides: list = None) -> np.ndarray:
        """
        Build the OOB-equivalent gate array for one pk_5s tce row.

        Parameters
        ----------
        tce_pk : the pk_5s test_config_extensions row PK
        base_df : 5s OHLCV
        dema : DEMA series on the base 5s (same dema as PKDetector consumes)
        params : tce_params dict (pool_c, pool_w, pool_slope, pool_range,
                 threshold_long, threshold_short, pm_suppression).
                 Any `decision_delay` field is ignored (r07: removed).
        midpoint : f_pk_state midpoint, default 50
        vote_overrides : optional list of vote dicts matching the shape
                 returned by _load_votes. When provided, bypasses the DB
                 lookup entirely — tce_pk becomes a log-only identifier.
                 Used by Reconciler with xlsx-sourced config to avoid
                 mutating test_config_ext_votes for one-off comparisons.

        Returns
        -------
        int8 array length len(base_df), sign-inverted vs Pine s5_pk_final:
          -1 = long PK fired (oob_side equivalent: LO OOB → expected = +1 long)
          +1 = short PK fired (oob_side equivalent: HI OOB → expected = -1 short)
           0 = idle / no verdict
        """
        votes = vote_overrides if vote_overrides is not None else self._load_votes(tce_pk)
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
        # r07 Step 4 pass-through: optional pm_additive dial. Default 0.0 keeps
        # behaviour identical to pre-Step-4 grinds when the sweep grid doesn't
        # populate it.
        pm_additive  = float(params.get('pm_additive', 0.0))

        # r07 Step 2: build per-probe state dict, delegate vote folding to
        # PKVoteMachine. The flattening loop replaces inline accumulation;
        # the math itself is identical to pre-Step-2 (validated by
        # test_pk_vote_machine.py).
        probe_states  = {}
        probe_weights = {}
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

            pool_id = int(v['tcev_pk'])
            for pool_label in ('close', 'wide'):
                weight = int(v[f'tcev_weight_{pool_label}'])
                if weight == 0:
                    continue
                probe_states[(pool_id, pool_label)]  = pool_states[pool_label]
                probe_weights[(pool_id, pool_label)] = weight

        if not probe_states:
            self._log.warning(f'pk_5s tce_pk={tce_pk}: all probes zero-weighted')
            return np.zeros(n, dtype=np.int8)

        vm = self._vote_machine or PKVoteMachine(
            pm_suppress_str=pm_supp,
            pm_additive_str=pm_additive,
        )
        result = vm.aggregate(probe_states, probe_weights, thr_long, thr_short)
        pk_raw = result['pk_raw']

        # r07: decision delay removed — hostile to HTF anchor signals
        s5_pk_final = pk_raw

        fires_long  = int((s5_pk_final ==  1).sum())
        fires_short = int((s5_pk_final == -1).sum())
        self._log.debug(
            f'pk_5s tce_pk={tce_pk}: '
            f'fires {fires_long + fires_short} ({fires_long}L / {fires_short}S)'
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
    def _pk_state_from_slopes(line_slope, price_slope, slope_floor):
        """Core pk-state decision from the line & price slopes — the SEAM shared by the pooled
        standard_pk path and any direct-fed peak (e.g. the bias machine's anchor/floater feed,
        where line_slope = osc(anchor)-osc(floater), price_slope = px(anchor)-px(floater)).
        Returns {NaN, 0.0, ±1.0 divergence, ±2.0 PM}. Vectorised; also valid on scalars.
        Pine: f_pk_state inner branch, bbstr.pine line 1368."""
        with np.errstate(invalid='ignore'):
            diverge = np.sign(line_slope) != np.sign(price_slope)
            noise   = np.abs(line_slope - price_slope) <= slope_floor
            result  = np.where(
                diverge,
                np.where(line_slope > 0, 1.0, -1.0),
                np.where(line_slope > 0, Pk5sGateComputer._PM_LONG, Pk5sGateComputer._PM_SHORT),
            )
            result = np.where(noise, 0.0, result)
        return np.where(np.isnan(line_slope) | np.isnan(price_slope), np.nan, result)

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
        result      = Pk5sGateComputer._pk_state_from_slopes(line_slope, price_slope, slope_floor)

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
