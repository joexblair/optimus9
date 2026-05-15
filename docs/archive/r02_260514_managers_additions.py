"""
260514_managers_additions.py — code to add to managers.py for the 5s PK gate
                               + p-rev round.

Two pieces, both for managers.py:

  Piece A — IndicatorComputer additions:
            Three new @staticmethod entries on the existing IndicatorComputer
            class. Insert anywhere inside the class body (suggest immediately
            after the existing `_stoch` method, before the close-brace).

  Piece B — Pk5sGateComputer class:
            New top-level class. Insert immediately AFTER PKDetector and
            BEFORE SwingAnalyzer (around line 770 in the current file).

Documentation conventions per the round spec:
  • Module-level header (above) — what this file delivers and why
  • Class docstrings in three sections: Purpose, Pine alignment, Design notes
  • Method docstrings: purpose + non-obvious params + return shape
  • Inline comments: only "this looks weird but here's why" moments
  • Pine references: `# Pine: <symbol>, bbstr.pine line N` for transposition audits

Round spec: 260514_pk5s_spec.md
"""

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
        ts         = base_df['timestamp'].to_numpy()
        window_id  = (ts // (target_seconds * 1000)).astype(np.int64)

        # transform('first') broadcasts the window's opening value to every row
        # in that window. cummax/cummin run within each window group.
        g = base_df.groupby(window_id, sort=False)
        return pd.DataFrame({
            'timestamp': ts,
            'open':      g['open'].transform('first').to_numpy(),
            'high':      g['high'].cummax().to_numpy(),
            'low':       g['low'].cummin().to_numpy(),
            'close':     base_df['close'].to_numpy(),
        })

    @staticmethod
    def f_bb_lookahead(base_df: pd.DataFrame, target_seconds: int,
                       length: int, mult: float, src: str,
                       high_b: float = 85.0, low_b: float = 15.0) -> np.ndarray:
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
        # mapped to [low_b, high_b].
        dev_band = mult * std
        span     = 2.0 * dev_band
        with np.errstate(invalid='ignore', divide='ignore'):
            pct = np.where(span != 0.0, (dev_src - (mean - dev_band)) / span, np.nan)
        return (high_b - low_b) * pct + low_b

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
        avg_g_c = IndicatorComputer._ema(g_c, rsi_len)
        avg_l_c = IndicatorComputer._ema(l_c, rsi_len)

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
        # alpha = 2/(n+1) update: avg_new = alpha*x + (1-alpha)*avg_prev
        alpha   = 2.0 / (rsi_len + 1.0)
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


# ═══════════════════════════════════════════════════════════════════════════
# PIECE B — Pk5sGateComputer class
#
# Insert as a new top-level class in managers.py, immediately after
# PKDetector and before SwingAnalyzer (around line 770 in the current file).
# ═══════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# Pk5sGateComputer
# ─────────────────────────────────────────────────────────────────────────────

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
