"""
Pine-parity tests for PKStateComputer's `multiplier` dimension.

Why this exists (2026-05-31):
  Pine's f_pk_state scales the peak-search window by `multiplier`:
      _window = _upper - _lower = pool_range * multiplier
  The earlier vectorized compute() hard-fixed the rolling window at
  `pool_range`, so it only matched Pine at multiplier=1 — the only value
  ever ground until now. The window is now `pool_range * multiplier`.

  These tests prove the vectorized compute() reproduces Pine's f_pk_state
  math at multiplier > 1, by diffing it against an INDEPENDENT naive
  reference written straight from the Pine source (emit/pine_strategy_emitter
  f_pk_state) — not from compute()'s internals.

Scope:
  EVEN pool_range only. Pine's `_half = pool_range / 2` is a float, so for
  ODD pool_range the window OFFSET sits 0.5*multiplier bars closer than
  Python's floored `half`. Width is identical either way (the halves
  cancel), but matching Pine's fractional-index rounding for odd pool_range
  needs a real Pine-export diff — out of scope here and flagged in
  pk_state_computer.compute(). The production spec (gcs5M) uses p_r=4 (even).

  multiplier=1 is the regression guard: window = pool_range*1 = pool_range,
  i.e. the pre-fix behaviour, so a green mult=1 case proves zero drift on
  every historical grind (all ran multiplier=1).
"""
import numpy as np
import pytest

from optimus9 import PKStateComputer

_PM_LONG, _PM_SHORT = 2.0, -2.0


def _pine_reference(line: np.ndarray, dema: np.ndarray,
                    bars: int, pool_range: int, multiplier: int,
                    slope_floor: float, midpoint: float) -> np.ndarray:
    """
    Naive per-bar transcription of Pine f_pk_state. O(n * window), no numpy
    vectorization, deliberately written to mirror the Pine source line for
    line so it shares no implementation with the class under test.

    Pine (emit/pine_strategy_emitter.py f_pk_state):
        _half   = pool_range / 2
        _lower  = (bars - _half) * mult
        _upper  = (bars + _half) * mult
        _window = _upper - _lower          # = pool_range * mult
        _center = bars * mult
        _peak   = line > mid ? highest(line[_lower], _window)
                             : lowest( line[_lower], _window)
        line_slope  = line - _peak
        price_slope = price - price[_center]
        slope_diff  = |line_slope - price_slope|
          <= floor                       -> 0
          sign(line_slope) != sign(price) -> ±1 (divergence)
          else                            -> ±2 (PM)
    Masks the first `_upper` bars (matches the loop's range(upper+1, n) skip).
    Assumes EVEN pool_range so the floored/float half agree.
    """
    n = min(len(line), len(dema))
    line, dema = line[:n], dema[:n]
    states = np.full(n, np.nan, dtype=np.float64)
    if pool_range == 0:
        return states

    half   = pool_range // 2          # even pool_range -> == pool_range / 2
    lower  = (bars - half) * multiplier
    upper  = (bars + half) * multiplier
    center = bars * multiplier
    window = pool_range * multiplier

    for i in range(n):
        if i <= upper:                # first upper+1 bars masked
            continue
        hi_start = i - lower - window + 1
        hi_end   = i - lower          # inclusive upper edge of search
        if hi_start < 0 or (i - center) < 0:
            continue
        seg  = line[hi_start:hi_end + 1]
        peak = seg.max() if line[i] > midpoint else seg.min()
        line_slope  = line[i] - peak
        price_slope = dema[i] - dema[i - center]
        slope_diff  = abs(line_slope - price_slope)

        if slope_diff <= slope_floor:
            states[i] = 0.0
        elif np.sign(line_slope) != np.sign(price_slope):
            if   line_slope > 0: states[i] =  1.0
            elif line_slope < 0: states[i] = -1.0
        else:
            if   line_slope > 0: states[i] = _PM_LONG
            elif line_slope < 0: states[i] = _PM_SHORT
    return states


def _synthetic_series(n: int = 600):
    """Deterministic line/dema that straddle the 50 midpoint with enough
    swing to exercise all of {0, ±1, ±2}. No RNG — pure functions keep the
    test reproducible."""
    i = np.arange(n, dtype=np.float64)
    line = 50.0 + 28.0 * np.sin(i * 0.09) + 8.0 * np.cos(i * 0.027)
    dema = 50.0 + 22.0 * np.sin(i * 0.07 + 0.6) + 5.0 * np.sin(i * 0.15)
    return line, dema


# (bars, pool_range, multiplier) — multiplier=1 is the regression guard,
# 9 is the gcs5M spec value; 2/3 catch off-by-multiplier scaling errors.
_CASES = [
    (bars, pr, mult)
    for bars in (5, 8)
    for pr   in (2, 4)        # EVEN only (see module docstring)
    for mult in (1, 2, 3, 9)
]


@pytest.mark.parametrize('bars,pool_range,multiplier', _CASES)
def test_compute_matches_pine_reference(bars, pool_range, multiplier):
    line, dema = _synthetic_series()
    sc = PKStateComputer()                      # default midpoint = 50.0
    slope_floor = 2.5

    got = sc.compute(line, dema, bars, pool_range, multiplier, slope_floor)
    exp = _pine_reference(line, dema, bars, pool_range, multiplier,
                          slope_floor, sc._midpoint)

    # assert_array_equal treats same-position NaNs as equal.
    np.testing.assert_array_equal(got, exp)


def test_multiplier_actually_widens_window():
    """Guard against a future regression to the fixed-pool_range window:
    at multiplier > 1 the result must DIFFER from a fixed pool_range-width
    search. If someone reverts `window = pool_range * multiplier` back to
    `pool_range`, this fails."""
    line, dema = _synthetic_series()
    sc = PKStateComputer()
    bars, pool_range, slope_floor = 8, 4, 2.5

    scaled = sc.compute(line, dema, bars, pool_range, 9, slope_floor)
    # Fixed-window reference == Pine ref with window forced to pool_range,
    # i.e. the OLD (buggy) behaviour. Emulate it by running the naive ref
    # with multiplier folded only into the offsets, window held at pool_range.
    n = len(line)
    old = np.full(n, np.nan)
    half = pool_range // 2
    lower  = (bars - half) * 9
    upper  = (bars + half) * 9
    center = bars * 9
    for i in range(n):
        if i <= upper or (i - lower - pool_range + 1) < 0 or (i - center) < 0:
            continue
        seg = line[i - lower - pool_range + 1: i - lower + 1]   # width pool_range
        peak = seg.max() if line[i] > sc._midpoint else seg.min()
        ls = line[i] - peak
        ps = dema[i] - dema[i - center]
        sd = abs(ls - ps)
        if sd <= slope_floor:        old[i] = 0.0
        elif np.sign(ls) != np.sign(ps): old[i] = 1.0 if ls > 0 else (-1.0 if ls < 0 else np.nan)
        else:                            old[i] = _PM_LONG if ls > 0 else (_PM_SHORT if ls < 0 else np.nan)

    # The fix must have changed behaviour at multiplier=9.
    assert not np.array_equal(scaled, old, equal_nan=True)


def test_reference_exercises_all_states():
    """Sanity: the synthetic data + spec geometry must actually produce
    0, a divergence (±1) and a PM (±2) — otherwise parity passes vacuously."""
    line, dema = _synthetic_series()
    sc = PKStateComputer()
    states = sc.compute(line, dema, 8, 4, 9, 2.5)
    present = set(np.unique(states[~np.isnan(states)]))
    assert 0.0 in present
    assert present & {1.0, -1.0}, 'no divergence states produced'
    assert present & {2.0, -2.0}, 'no PM states produced'
