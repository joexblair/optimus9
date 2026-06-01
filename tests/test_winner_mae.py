"""
Tests for outcome_walker.winner_mae — MAE of eventual winners (stop ignored).
entry=100, profit=0.9 → LONG win 100.9; SHORT win 99.1.
"""
import numpy as np

from optimus9.compute.outcome_walker import winner_mae


def _m(close, d=1, horizon=None):
    return winner_mae(np.array(close, float), 0, d, 0.9, horizon)


def test_long_winner_records_dip():
    # dips to 99.7 (-0.3009%) then wins at 100.95
    assert _m([100, 99.7, 100.95]) == round((100 / 99.7 - 1) * 100, 6)


def test_long_non_winner_returns_none():
    assert _m([100, 99.5, 100.1]) is None        # never reaches 100.9


def test_long_clean_winner_zero_mae():
    assert _m([100, 100.5, 100.95]) == 0.0        # never dipped below entry


def test_short_winner_records_spike():
    # spikes to 100.3 (+0.3%) then wins at 99.0
    assert _m([100, 100.3, 99.0], d=-1) == round((100.3 / 100 - 1) * 100, 6)


def test_horizon_caps_winner_detection():
    close = [100, 100.2, 100.95]                   # wins only at bar 2
    assert _m(close, horizon=1) is None            # not reached within 1 bar
    assert _m(close, horizon=2) == 0.0             # reached, no adverse dip
