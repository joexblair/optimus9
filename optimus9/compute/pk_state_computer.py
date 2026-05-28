"""
PKStateComputer — pure PK state computation per bar.

VECTORIZED numpy implementation. Computes pk_state values per bar based
on line vs DEMA slope analysis. Matches Pine's f_pk_state exactly.

Window semantics (Pine-aligned):
  For bar i, the peak search window covers line[i - upper + 1 : i - lower + 1],
  i.e. pool_range bars ending at i - lower. This matches Pine's
  ta.highest(line[lower], pool_range).

Implementation:
  - Compute rolling max + rolling min of size pool_range over line
  - Shift the rolling arrays by `lower` so index i carries the peak that
    would be found by looking back [i-upper+1 : i-lower+1]
  - Per-bar peak selection via np.where(line > midpoint, max, min)
  - Slope computation via np.roll for the dema lookback
  - First `upper + 1` bars are masked NaN to match the original loop's
    `range(upper + 1, n)` skip (also neutralises any np.roll wraparound;
    see r07_open_items.md "dema[i - center] wraparound" note)
  - State classification vectorized via np.where cascades

r08 NOTE: high_b / low_b currently sit per-row in indicator_configs but
every row is 85/15. These are global system constants and should move
to a system_settings table.
"""

import numpy as np
import pandas as pd

from logger import get_logger


class PKStateComputer:
    """Pure math: compute pk_state per bar for a single pool config. Vectorized."""

    _PM_LONG  =  2.0
    _PM_SHORT = -2.0

    def __init__(self, high_b: float = 85.0, low_b: float = 15.0) -> None:
        # r08: high_b/low_b should be global system settings.
        self._midpoint = (high_b + low_b) / 2.0
        self._log      = get_logger(self.__class__.__name__)

    def compute(self, line: np.ndarray, dema: np.ndarray,
                bars: int, pool_range: int,
                multiplier: int, slope_floor: float) -> np.ndarray:
        """
        Return ndarray of pk_state values, length == min(len(line), len(dema)).

        Values:
          NaN  — not yet computable (insufficient lookback or NaN inputs)
          0    — neutral (slope_diff under floor)
          ±1   — divergence (line and price slopes disagree on sign)
          ±2   — PM sentinel (slopes agree on sign with significant magnitude)

        Length-mismatch note (r07):
          When ind_seconds == 5, line is built from ind_df which can be shorter
          than base_df because IndicatorComputer.resample drops bars with NaN
          opens (gaps in kline collection). The original PKDetector loop
          accidentally tolerated this via `range(upper + 1, len(line))` — only
          the first len(line) bars of dema were ever read. This vectorized
          version reproduces that behavior by explicitly truncating both to
          min(len(line), len(dema)). See r07_open_items.md "align_to_base
          should always produce base-length output" for the upstream cleanup.
        """
        # Match original loop's implicit truncation. See docstring above.
        n = min(len(line), len(dema))
        line = line[:n]
        dema = dema[:n]
        states = np.full(n, np.nan, dtype=np.float64)

        if pool_range == 0:
            return states

        half   = pool_range // 2
        lower  = (bars - half) * multiplier
        upper  = (bars + half) * multiplier
        center = bars * multiplier

        # ── Rolling peak / trough on `line` ────────────────────────────────
        # rolling_max[j] = max(line[j - pool_range + 1 : j + 1])
        # We want bar i's peak from window ending at i - lower, so we shift
        # the rolling array forward by `lower` positions:
        #   peak_max[i] = rolling_max[i - lower]   for i >= lower
        s_line = pd.Series(line)
        rolling_max = s_line.rolling(pool_range, min_periods=pool_range).max().to_numpy()
        rolling_min = s_line.rolling(pool_range, min_periods=pool_range).min().to_numpy()

        if lower > 0:
            pad      = np.full(lower, np.nan)
            peak_max = np.concatenate([pad, rolling_max[: n - lower]])
            peak_min = np.concatenate([pad, rolling_min[: n - lower]])
        else:
            peak_max = rolling_max.copy()
            peak_min = rolling_min.copy()

        peak = np.where(line > self._midpoint, peak_max, peak_min)

        # ── Slopes ─────────────────────────────────────────────────────────
        line_slope = line - peak

        # dema lookback: dema[i] - dema[i - center]. np.roll wraps the first
        # `center` entries to the end of the array — but we mask the first
        # `upper + 1` bars in the validity step below (upper > center for any
        # pool_range > 0), so wraparound never reaches the output.
        dema_shifted = np.roll(dema, center)
        price_slope  = dema - dema_shifted

        slope_diff = np.abs(line_slope - price_slope)

        # ── Validity mask ───────────────────────────────────────────────────
        # Match the Python loop's `range(upper + 1, n)` skip.
        valid = np.ones(n, dtype=bool)
        valid[: upper + 1] = False
        valid &= ~np.isnan(line)
        valid &= ~np.isnan(dema)
        valid &= ~np.isnan(peak)
        valid &= ~np.isnan(price_slope)

        # ── State classification ────────────────────────────────────────────
        below_floor = valid & (slope_diff <= slope_floor)
        above_floor = valid & (slope_diff >  slope_floor)

        sign_line  = np.sign(line_slope)
        sign_price = np.sign(price_slope)
        signs_disagree = above_floor & (sign_line != sign_price)
        signs_agree    = above_floor & (sign_line == sign_price)

        states[below_floor] = 0.0
        states[signs_disagree & (line_slope > 0)] =  1.0
        states[signs_disagree & (line_slope < 0)] = -1.0
        states[signs_agree    & (line_slope > 0)] =  self._PM_LONG
        states[signs_agree    & (line_slope < 0)] =  self._PM_SHORT

        return states
