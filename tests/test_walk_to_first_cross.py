"""
Tests for outcome_walker.walk_to_first_cross — directional asymmetric first-cross.
entry=100, profit=0.9, stop=0.4 → LONG win 100.9 / stop 99.6; SHORT win 99.1 / stop 100.4.
"""
import numpy as np

from optimus9.compute.outcome_walker import walk_to_first_cross


def _w(close, d=1, horizon=None):
    return walk_to_first_cross(np.array(close, float), 0, d, 0.9, 0.4, horizon)


def test_long_win():
    assert _w([100, 100.95]) == (1, None)


def test_long_stop():
    assert _w([100, 99.5]) == (None, 1)


def test_long_stop_beats_later_win():
    assert _w([100, 99.5, 101.0]) == (None, 1)


def test_long_small_dip_does_not_stop():
    # -0.3% < 0.4% stop → not stopped; later +0.9% wins
    assert _w([100, 99.7, 100.95]) == (2, None)


def test_short_win():
    assert _w([100, 99.0], d=-1) == (1, None)


def test_short_stop():
    assert _w([100, 100.5], d=-1) == (None, 1)


def test_neither_undecided():
    assert _w([100, 100.2, 99.8, 100.1]) == (None, None)


def test_horizon_caps_the_walk():
    close = [100, 100.2, 100.95]          # win only at bar 2
    assert _w(close, horizon=1) == (None, None)
    assert _w(close, horizon=2) == (2, None)
