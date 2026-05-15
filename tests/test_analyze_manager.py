"""Tests for optimus9.analysis.analyze_manager centroid math."""

import pandas as pd

from optimus9 import AnalyzeManager


class _DummyDB:
    """Minimal DB stub — AnalyzeManager only needs an attribute presence."""
    def execute(self, *args, **kwargs):
        return []


def test_compute_centroid_int_params_round_to_int():
    """
    Regression for 260515: int params (len, pool_c, pool_w, pool_range,
    multiplier) must come out as Python ints, not floats like 18.25.
    """
    am = AnalyzeManager(_DummyDB())
    df = pd.DataFrame({
        'len':         [19, 20, 21],
        'mult':        [0.6, 0.7, 0.8],
        'pool_c':      [8, 10, 12],
        'pool_w':      [50, 55, 60],
        'pool_range':  [2, 2, 4],
        'slope_floor': [2.5, 2.5, 2.5],
        'multiplier':  [3, 3, 3],
        'src':         ['close', 'close', 'hl2'],
        'expectancy':  [0.1, 0.2, 0.3],
    })
    cent = am._compute_centroid(df, n=3)
    for p in ['len', 'pool_c', 'pool_w', 'pool_range', 'multiplier']:
        assert isinstance(cent[p], int), f'{p}={cent[p]!r} should be int'
    # mult and slope_floor stay float
    assert isinstance(cent['mult'], float)


def test_compute_centroid_all_negative_uses_uniform_weights():
    """
    When every expectancy is non-positive, the weighted-by-expectancy
    fallback should produce a uniform-weighted centroid rather than NaN.
    """
    am = AnalyzeManager(_DummyDB())
    df = pd.DataFrame({
        'len':         [10, 20],
        'mult':        [0.5, 0.7],
        'pool_c':      [5, 10],
        'pool_w':      [30, 50],
        'pool_range':  [2, 4],
        'slope_floor': [2.5, 2.5],
        'multiplier':  [3, 3],
        'src':         ['close', 'hl2'],
        'expectancy':  [-0.33, -0.33],
    })
    cent = am._compute_centroid(df, n=2)
    assert cent['len'] == 15  # (10 + 20) / 2 = 15, rounded
    assert cent['mult'] == 0.6  # (0.5 + 0.7) / 2 = 0.6
