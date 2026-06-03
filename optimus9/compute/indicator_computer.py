"""
IndicatorComputer — see class docstring for purpose, Pine alignment, and design notes.
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

from ..constants import RSI_OVERBOUGHT, RSI_OVERSOLD


class IndicatorComputer:
    """Pure computation. Replicates Pine Script f_bb, f_k, DEMA. No I/O."""

    @staticmethod
    def resample(df: pd.DataFrame, target_seconds: int) -> pd.DataFrame:
        """Aggregate a 5s OHLCV DataFrame into target_seconds bars."""
        tmp = df.copy()
        tmp['dt'] = pd.to_datetime(tmp['timestamp'], unit='ms', utc=True)
        tmp = tmp.set_index('dt').sort_index()
        agg = tmp.resample(f'{target_seconds}s').agg(
            timestamp=('timestamp', 'first'), open=('open', 'first'),
            high=('high', 'max'), low=('low', 'min'),
            close=('close', 'last'), volume=('volume', 'sum'),
        ).dropna(subset=['open'])
        return agg.reset_index(drop=True)

    @staticmethod
    def align_to_base(values: np.ndarray,
                      source_df: pd.DataFrame,
                      base_df:   pd.DataFrame) -> np.ndarray:
        """
        Forward-fill indicator values from source_df timestamps to base_df timestamps.
        Uses searchsorted for O(n log m) vectorised alignment.
        Mimics Pine Script request.security() — each base bar sees the last completed source bar.
        """
        src_ts  = source_df['timestamp'].to_numpy()
        base_ts = base_df['timestamp'].to_numpy()
        idx     = np.searchsorted(src_ts, base_ts, side='right') - 1
        out     = np.full(len(base_ts), np.nan)
        valid   = idx >= 0
        out[valid] = values[idx[valid]]
        return out

    @staticmethod
    def fold_gates(sides: list) -> np.ndarray:
        """
        Combine N OOB side arrays with OR logic.
          Both non-zero and agree → that direction.
          Both non-zero and oppose → 0 (gate closed).
          One non-zero, one zero → non-zero direction (OR).
          Both zero → 0 (IB, gate closed).
        """
        if not sides:
            return np.zeros(0, dtype=np.int8)
        result = sides[0].copy().astype(np.int8)
        for s in sides[1:]:
            s        = s.astype(np.int8)
            opposing = (result != 0) & (s != 0) & (result != s)
            s_only   = (result == 0) & (s != 0)
            result   = np.where(opposing, np.int8(0),
                       np.where(s_only, s, result)).astype(np.int8)
        return result

    @staticmethod
    def compute_oob_side(cfg: dict, df: pd.DataFrame) -> np.ndarray:
        """
        Compute OOB side array for one indicator config row.
        Returns +1 (HI OOB), -1 (LO OOB), 0 (IB) for each bar.
        Dispatches to f_bb or f_k based on ic_line_type.
        """
        src         = IndicatorComputer.build_source(df, cfg['ic_src'])
        boundary_hi = float(cfg['ic_high_boundary'])    # OOB detection (85/15)
        boundary_lo = float(cfg['ic_low_boundary'])

        if cfg['ic_line_type'] == 'bb':
            vals = IndicatorComputer.f_bb(src, int(cfg['ic_bb_len']), float(cfg['ic_bb_mult']))
        else:
            vals = IndicatorComputer.f_k(
                src, int(cfg['ic_rsi_len']), int(cfg['ic_stc_len']), int(cfg['ic_k_len'])
            )

        result = np.zeros(len(vals), dtype=np.int8)
        with np.errstate(invalid='ignore'):
            result[vals >= boundary_hi] =  1
            result[vals <= boundary_lo] = -1
        return result

    @staticmethod
    def build_source(df: pd.DataFrame, src: str) -> np.ndarray:
        o, h, l, c = (df[col].to_numpy(dtype=float) for col in ('open', 'high', 'low', 'close'))
        mapping = {
            'close': c, 'open': o, 'high': h, 'low': l,
            'hl2':   (h + l) / 2,
            'hlc3':  (h + l + c) / 3,
            'ohlc4': (o + h + l + c) / 4,
            'hlcc4': (h + l + c + c) / 4,
        }
        if src not in mapping:
            raise ValueError(f'Unknown source {src!r}')
        return mapping[src]

    @staticmethod
    def f_bb(src: np.ndarray, length: int, mult: float,
             rsi_ob: float = RSI_OVERBOUGHT, rsi_os: float = RSI_OVERSOLD) -> np.ndarray:
        # rsi_ob/rsi_os are the RSI-domain RESCALE endpoints (70/30), NOT OOB
        # boundaries — feeding 85/15 here was the historical conflation.
        basis = IndicatorComputer._sma(src, length)
        dev   = mult * IndicatorComputer._stdev(src, length)
        span  = (basis + dev) - (basis - dev)
        with np.errstate(invalid='ignore', divide='ignore'):
            pct = np.where(span != 0.0, (src - (basis - dev)) / span, np.nan)
        return (rsi_ob - rsi_os) * pct + rsi_os

    @staticmethod
    def f_k(src: np.ndarray, rsi_len: int, stc_len: int, k_len: int) -> np.ndarray:
        return IndicatorComputer._sma(
            IndicatorComputer._stoch(IndicatorComputer._rsi(src, rsi_len), stc_len),
            k_len,
        )

    @staticmethod
    def dema(src: np.ndarray, length: int) -> np.ndarray:
        e1 = IndicatorComputer._ema(src, length)
        return 2.0 * e1 - IndicatorComputer._ema(e1, length)

    @staticmethod
    def _sma(src: np.ndarray, n: int) -> np.ndarray:
        return pd.Series(src).rolling(n, min_periods=n).mean().to_numpy()

    @staticmethod
    def _stdev(src: np.ndarray, n: int) -> np.ndarray:
        return pd.Series(src).rolling(n, min_periods=n).std(ddof=0).to_numpy()

    @staticmethod
    def _ema(src: np.ndarray, n: int) -> np.ndarray:
        alpha = 2.0 / (n + 1)
        out   = np.full_like(src, np.nan, dtype=float)
        valid = np.where(~np.isnan(src))[0]
        if len(valid) < n:
            return out
        seed      = valid[n - 1]
        out[seed] = float(np.nanmean(src[valid[0] : seed + 1]))
        for i in range(seed + 1, len(src)):
            out[i] = alpha * src[i] + (1.0 - alpha) * out[i - 1] if not np.isnan(src[i]) else out[i - 1]
        return out

    @staticmethod
    def _rma(src: np.ndarray, n: int) -> np.ndarray:
        """Wilder's RMA (Pine ta.rma): SMA-seeded, recursive with alpha = 1/n.
        ta.rsi uses THIS, not the 2/(n+1) EMA."""
        out   = np.full_like(src, np.nan, dtype=float)
        valid = np.where(~np.isnan(src))[0]
        if len(valid) < n:
            return out
        seed      = valid[n - 1]
        out[seed] = float(np.nanmean(src[valid[0]: seed + 1]))
        for i in range(seed + 1, len(src)):
            out[i] = (out[i - 1] * (n - 1) + src[i]) / n if not np.isnan(src[i]) else out[i - 1]
        return out

    @staticmethod
    def _rsi(src: np.ndarray, n: int) -> np.ndarray:
        delta = np.diff(src, prepend=np.nan)
        avg_g = IndicatorComputer._rma(np.where(delta > 0,  delta, 0.0), n)
        avg_l = IndicatorComputer._rma(np.where(delta < 0, -delta, 0.0), n)
        with np.errstate(invalid='ignore', divide='ignore'):
            rs = np.where(avg_l != 0, avg_g / avg_l, np.inf)
        return 100.0 - (100.0 / (1.0 + rs))

    @staticmethod
    def _stoch(src: np.ndarray, n: int) -> np.ndarray:
        s   = pd.Series(src)
        lo  = s.rolling(n, min_periods=n).min()
        hi  = s.rolling(n, min_periods=n).max()
        rng = hi - lo
        out = np.where(rng != 0, 100.0 * (s - lo) / rng, 50.0)
        out = np.where(rng.isna(), np.nan, out)
        return out.astype(float)

    # ═══════════════════════════════════════════════════════════════════
    # PIECE B — r05 gate composition helpers
    #
    # compute_gate_mask: generalize ReportManager._load_gate_configs flow
    # into a reusable classmethod for inspector + FoldManager + future
    # consumers. Existing fold_gates (OR semantics) is preserved for
    # production grinds; new code uses fold='AND' for conservative
    # bny30M+bny30p gating.
    # ═══════════════════════════════════════════════════════════════════

    @classmethod
    def compute_gate_mask(cls, db, ic_pks: list,
                          base_df: pd.DataFrame,
                          fold: str = 'AND') -> np.ndarray:
        """
        Compute a folded per-bar gate mask from multiple gate indicators.

        Each ic_pk loaded from indicator_configs, OOB-side computed at its
        native TF, aligned to 5s base, then all gates folded.

        Args:
            db       — DatabaseManager instance
            ic_pks   — list of ic_pks (e.g. [2, 3] for bny30M + bny30p)
            base_df  — 5s base DataFrame (alignment target)
            fold     — 'AND' (every gate must agree, conservative) or
                       'OR' (any gate fires; legacy fold_gates semantics)

        Returns:
            np.ndarray shape (len(base_df),) values {-1, 0, +1}
        """
        if not ic_pks:
            return np.zeros(len(base_df), dtype=np.int8)
        configs = cls._load_gate_configs(db, ic_pks)
        return cls._mask_from_configs(configs, base_df, fold)

    @staticmethod
    def _load_gate_configs(db, ic_pks: list) -> list:
        """Load indicator_configs (+ itf_seconds) for `ic_pks`, joined to their
        timeframe/series/line metadata. Raises if any ic_pk is missing."""
        placeholders = ','.join(['%s'] * len(ic_pks))
        configs = db.execute(
            f'''SELECT ic.*,
                       itf.itf_seconds AS ic_itf_seconds,
                       s.is_prefix,
                       itf.itf_label,
                       il.il_suffix
                FROM indicator_configs ic
                JOIN indicator_timeframes itf ON itf.itf_pk = ic.ic_itf_pk
                JOIN indicator_series     s   ON s.is_pk    = ic.ic_is_pk
                JOIN indicator_lines      il  ON il.il_pk   = ic.ic_il_pk
                WHERE ic.ic_pk IN ({placeholders})''',
            tuple(ic_pks), fetch=True,
        )
        if len(configs) != len(ic_pks):
            present = {c['ic_pk'] for c in configs}
            missing = set(ic_pks) - present
            raise ValueError(f'Missing indicator_configs for ic_pks: {missing}')
        return configs

    @classmethod
    def _mask_from_configs(cls, configs: list,
                           base_df: pd.DataFrame,
                           fold: str = 'AND') -> np.ndarray:
        """
        Build a folded per-bar gate mask from already-resolved config dicts.

        Each config dict needs `ic_itf_seconds` plus the fields
        `compute_oob_side` reads (`ic_line_type`, `ic_src`, `ic_high_boundary`,
        `ic_low_boundary`, and the line-type params: ic_bb_len/ic_bb_mult for
        'bb', ic_k_len/ic_rsi_len/ic_stc_len for 'k').

        Shared by `compute_gate_mask` (configs loaded from DB by ic_pk) and the
        gate sweep (configs built from grid params per combo; see
        gate_sweep_design.md). Factors the per-gate loop so it can be driven by
        params, not only ic_pks — the DB-loaded path stays byte-identical.
        """
        if not configs:
            return np.zeros(len(base_df), dtype=np.int8)

        gate_sides = []
        for gcfg in configs:
            gate_df   = cls.resample(base_df, int(gcfg['ic_itf_seconds']))
            oob_raw   = cls.compute_oob_side(gcfg, gate_df)
            oob_align = cls.align_to_base(oob_raw, gate_df, base_df)
            gate_sides.append(oob_align)

        if fold == 'AND':
            return cls._fold_and(gate_sides)
        elif fold == 'OR':
            return cls.fold_gates(gate_sides)
        else:
            raise ValueError(f'Unknown fold={fold!r}; use "AND" or "OR"')

    @staticmethod
    def _fold_and(sides: list) -> np.ndarray:
        """
        AND fold: bar is HI iff EVERY gate says HI; LO iff every says LO;
        IB otherwise. Counterpart to fold_gates (OR) for conservative
        bny30M+bny30p gating per Joe's spec.
        """
        if not sides:
            return np.zeros(0, dtype=np.int8)
        stack = np.stack(sides)              # (n_gates, n_bars)
        n_bars = stack.shape[1]
        out = np.zeros(n_bars, dtype=np.int8)
        out[np.all(stack ==  1, axis=0)] =  1
        out[np.all(stack == -1, axis=0)] = -1
        return out

# ═══════════════════════════════════════════════════════════════════════════
# PIECE A — IndicatorComputer additions
#
# Three new @staticmethod entries. Adds lookahead (Pine barmerge.lookahead_on)
# equivalents for resampling and BB/K computation. Used when --p_rev is on.
# ═══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def lookahead_resample(base_df: pd.DataFrame, target_seconds: int) -> pd.DataFrame:
        """
        Produce a 5s-aligned 'developing' OHLC view of a higher-TF.

        Each row in the returned DataFrame corresponds to a 5s timestamp in
        base_df. The OHLC at that row reflects the in-progress higher-TF bar
        that contains the timestamp:

            O = first 5s open in the higher-TF window (constant across window)
            H = cumulative max of 5s highs from window start through t
            L = cumulative min of 5s lows  from window start through t
            C = current 5s close at t

        Pine equivalent:
            request.security(syminfo.tickerid, "<target>S",
                             line, barmerge.gaps_off, barmerge.lookahead_on)

        Volume is intentionally excluded — BB/K chains don't consume it.

        Parameters
        ----------
        base_df : 5s OHLCV DataFrame with columns timestamp, open, high, low, close
        target_seconds : higher TF in seconds (e.g. 30, 60, 360)

        Returns
        -------
        DataFrame parallel to base_df (same length, same timestamps) with
        columns: timestamp, open, high, low, close.
        """
        ts        = base_df['timestamp'].to_numpy()
        window_id = (ts // (target_seconds * 1000)).astype(np.int64)

        # kline_collection columns are DECIMAL → object dtype via pymysql.
        # Cast to float64 up front so groupby cython ops (transform/cummax/cummin)
        # can run. Without this we hit "function is not implemented for dtype:object".
        tmp = pd.DataFrame({
            'open':  base_df['open'].to_numpy(dtype=float),
            'high':  base_df['high'].to_numpy(dtype=float),
            'low':   base_df['low'].to_numpy(dtype=float),
            'close': base_df['close'].to_numpy(dtype=float),
        })

        g = tmp.groupby(window_id, sort=False)
        return pd.DataFrame({
            'timestamp': ts,
            'open':      g['open'].transform('first').to_numpy(),
            'high':      g['high'].cummax().to_numpy(),
            'low':       g['low'].cummin().to_numpy(),
            'close':     tmp['close'].to_numpy(),
        })
        
    @staticmethod
    def f_bb_lookahead(base_df: pd.DataFrame, target_seconds: int,
                       length: int, mult: float, src: str,
                       rsi_ob: float = RSI_OVERBOUGHT, rsi_os: float = RSI_OVERSOLD) -> np.ndarray:
        """
        BB(length, mult) at each 5s bar against the developing higher-TF bar.

        Pine equivalent:
            bb_value = request.security(..., "<target>S",
                                        bb_calc(src, length, mult),
                                        barmerge.gaps_off, barmerge.lookahead_on)

        At each 5s bar t in developing window w, the BB sees:
          • (length-1) source values from the closed windows: w-(length-1) .. w-1
          • 1 developing source value: the lookahead-resampled source at t

        Mean and stdev are closed-form: pre-compute rolling sum and rolling
        sum-of-squares over the closed source series at window length (length-1),
        then combine with the developing value at each 5s.

        Returns a 1D float array parallel to base_df (NaN where insufficient
        history). Same return shape and scaling as f_bb.
        """
        # ── closed higher-TF source series ────────────────────────────────
        closed     = IndicatorComputer.resample(base_df, target_seconds)
        closed_src = IndicatorComputer.build_source(closed, src)
        closed_ts  = closed['timestamp'].to_numpy()

        # Rolling sums over the prior (length-1) closed bars.
        # roll_sum[i] = sum of closed_src[i-(length-2) .. i]  (window length-1)
        s    = pd.Series(closed_src)
        roll_sum   = s.rolling(length - 1, min_periods=length - 1).sum().to_numpy()
        roll_sumsq = (s ** 2).rolling(length - 1, min_periods=length - 1).sum().to_numpy()

        # ── developing source values at every 5s ──────────────────────────
        dev_df  = IndicatorComputer.lookahead_resample(base_df, target_seconds)
        dev_src = IndicatorComputer.build_source(dev_df, src)

        # ── map each 5s timestamp to its developing-window index in closed ─
        base_ts = base_df['timestamp'].to_numpy()
        # searchsorted(right) - 1 = last closed bar whose timestamp <= base_ts.
        # Since closed bars are at window-start timestamps, this gives the
        # closed-array index of the CURRENT developing window.
        idx = np.searchsorted(closed_ts, base_ts, side='right') - 1

        # Lookback uses closed bars 0..idx-1 (length-1 of them ending at idx-1).
        # Safe-index trick: clamp to 0 for invalid rows, mask result via np.where.
        valid_idx    = idx >= 1
        lookback_idx = np.where(valid_idx, idx - 1, 0)
        lb_sum   = np.where(valid_idx, roll_sum  [lookback_idx], np.nan)
        lb_sumsq = np.where(valid_idx, roll_sumsq[lookback_idx], np.nan)

        full_sum   = lb_sum   + dev_src
        full_sumsq = lb_sumsq + dev_src * dev_src

        mean = full_sum / length
        var  = full_sumsq / length - mean * mean
        with np.errstate(invalid='ignore'):
            var = np.where(var < 0.0, 0.0, var)   # numerical guard
        std = np.sqrt(var)

        # Same final scaling as f_bb: position of src within [basis-dev, basis+dev]
        # mapped to [rsi_os, rsi_ob] (the RSI rescale domain, not OOB boundaries).
        dev_band = mult * std
        span     = 2.0 * dev_band
        with np.errstate(invalid='ignore', divide='ignore'):
            pct = np.where(span != 0.0, (dev_src - (mean - dev_band)) / span, np.nan)
        return (rsi_ob - rsi_os) * pct + rsi_os

    @staticmethod
    def f_k_lookahead(base_df: pd.DataFrame, target_seconds: int,
                      k_len: int, rsi_len: int, stc_len: int, src: str) -> np.ndarray:
        """
        K chain (RSI → Stoch → SMA) at each 5s bar against the developing
        higher-TF bar.

        Pine equivalent:
            k_value = request.security(..., "<target>S",
                                       sma(stoch(rsi(src, rsi_len), stc_len), k_len),
                                       barmerge.gaps_off, barmerge.lookahead_on)

        Not exercised by the 5s gate round (b6M is BB, all six 5s vote
        contributors are 5s-native). Provided as forward-looking infrastructure
        for when a K-line target is calibrated on a higher TF — pre-built so
        we don't have to think about it under pressure later.

        Implementation parallels f_bb_lookahead: rolling state on the closed
        series, single-step update at each 5s using developing values. RSI uses
        the same _ema as IndicatorComputer._rsi (alpha = 2/(n+1)) for consistency
        with the non-lookahead path — known to deviate slightly from Pine's
        Wilder smoothing, same way the non-lookahead version does.

        Returns a 1D float array parallel to base_df.
        """
        # ── closed higher-TF chain ────────────────────────────────────────
        closed     = IndicatorComputer.resample(base_df, target_seconds)
        closed_src = IndicatorComputer.build_source(closed, src)
        closed_ts  = closed['timestamp'].to_numpy()

        # RSI components on closed series
        delta_c = np.diff(closed_src, prepend=np.nan)
        g_c     = np.where(delta_c > 0,  delta_c, 0.0)
        l_c     = np.where(delta_c < 0, -delta_c, 0.0)
        avg_g_c = IndicatorComputer._rma(g_c, rsi_len)
        avg_l_c = IndicatorComputer._rma(l_c, rsi_len)

        # Stoch needs rolling min/max of RSI — but we'll compute developing RSI
        # at each 5s, then do windowed min/max combining closed and developing.
        rsi_c   = IndicatorComputer._rsi(closed_src, rsi_len)  # consistent with the non-lookahead path

        # Stoch denominator components over previous (stc_len-1) closed RSI values
        rsi_c_s        = pd.Series(rsi_c)
        roll_rsi_min   = rsi_c_s.rolling(stc_len - 1, min_periods=stc_len - 1).min().to_numpy()
        roll_rsi_max   = rsi_c_s.rolling(stc_len - 1, min_periods=stc_len - 1).max().to_numpy()

        # SMA(k_len) at developing position uses (k_len-1) closed Stoch values
        # + 1 developing Stoch value. Need closed stoch series first.
        stoch_c        = IndicatorComputer._stoch(rsi_c, stc_len)
        stoch_c_s      = pd.Series(stoch_c)
        roll_stoch_sum = stoch_c_s.rolling(k_len - 1, min_periods=k_len - 1).sum().to_numpy()

        # ── developing source at every 5s ─────────────────────────────────
        dev_df  = IndicatorComputer.lookahead_resample(base_df, target_seconds)
        dev_src = IndicatorComputer.build_source(dev_df, src)

        base_ts = base_df['timestamp'].to_numpy()
        idx     = np.searchsorted(closed_ts, base_ts, side='right') - 1

        # Need at least one closed window prior for RSI's smoothing reference.
        valid    = idx >= 1
        lb_idx   = np.where(valid, idx - 1, 0)

        # ── developing RSI: single-step update from last-closed RSI state ──
        # Wilder RMA update (alpha = 1/n): avg_new = avg_prev + (x - avg_prev)/n
        alpha   = 1.0 / rsi_len
        prev_src = np.where(valid, closed_src[lb_idx], np.nan)
        delta_d  = dev_src - prev_src
        g_d      = np.where(delta_d > 0,  delta_d, 0.0)
        l_d      = np.where(delta_d < 0, -delta_d, 0.0)
        avg_g_d  = alpha * g_d + (1.0 - alpha) * np.where(valid, avg_g_c[lb_idx], np.nan)
        avg_l_d  = alpha * l_d + (1.0 - alpha) * np.where(valid, avg_l_c[lb_idx], np.nan)
        with np.errstate(invalid='ignore', divide='ignore'):
            rs       = np.where(avg_l_d != 0.0, avg_g_d / avg_l_d, np.inf)
        rsi_d    = 100.0 - (100.0 / (1.0 + rs))

        # ── developing Stoch ──────────────────────────────────────────────
        lb_rsi_min = np.where(valid, roll_rsi_min[lb_idx], np.nan)
        lb_rsi_max = np.where(valid, roll_rsi_max[lb_idx], np.nan)
        stoch_min  = np.minimum(lb_rsi_min, rsi_d)
        stoch_max  = np.maximum(lb_rsi_max, rsi_d)
        rng        = stoch_max - stoch_min
        with np.errstate(invalid='ignore', divide='ignore'):
            stoch_d = np.where(rng != 0.0, 100.0 * (rsi_d - stoch_min) / rng, 50.0)

        # ── developing SMA of Stoch ───────────────────────────────────────
        lb_stoch_sum = np.where(valid, roll_stoch_sum[lb_idx], np.nan)
        return (lb_stoch_sum + stoch_d) / k_len
