"""
Tests for optimus9.compute.swing_detect (ZigZag swing detection).
threshold pct=0.9 unless noted.
"""
import numpy as np

from optimus9.compute.swing_detect import find_pivots, legs, swing_mask


def test_up_then_down():
    price = [100, 101, 102, 103, 102, 101, 100]   # +3% up, ~-2.9% down
    piv = find_pivots(price, 0.9)
    assert piv == [(0, 'L'), (3, 'H'), (6, 'L')]


def test_down_then_up():
    price = [100, 99, 98, 97, 98, 99, 100]
    piv = find_pivots(price, 0.9)
    assert piv == [(0, 'H'), (3, 'L'), (6, 'H')]


def test_chop_below_threshold_makes_no_interior_pivots():
    # oscillation within +/-0.3% never triggers a pivot
    price = [100, 100.3, 99.8, 100.2, 99.9, 100.1]
    piv = find_pivots(price, 0.9)
    # only the boundary pivots (start + final provisional), no interior turns
    assert len(piv) <= 2


def test_legs_amplitude_and_direction():
    price = [100, 103, 100]                        # +3% then -2.9%
    piv = find_pivots(price, 0.9)
    lg = legs(price, piv)
    assert len(lg) == 2
    assert lg[0]['dir'] == 1 and abs(lg[0]['amp_pct'] - 3.0) < 1e-9
    assert lg[1]['dir'] == -1 and lg[1]['amp_pct'] < 0


def test_swing_mask_marks_leg_bars():
    price = [100, 101, 102, 103, 102, 101, 100]
    piv = find_pivots(price, 0.9)
    m = swing_mask(len(price), legs(price, piv), 0.9)
    assert m.all()                                  # both legs >= 0.9%, tile fully


def test_alternation():
    rng = np.random.default_rng(3)
    price = 100 + np.cumsum(rng.normal(0, 0.2, 800))
    piv = find_pivots(price, 0.9)
    kinds = [k for _, k in piv]
    assert all(kinds[i] != kinds[i + 1] for i in range(len(kinds) - 1))  # strictly alternating
    idxs = [i for i, _ in piv]
    assert idxs == sorted(idxs)                     # monotonic in time
