"""predict_breach tolerance knob (Joe 0709). tol=0 must be bit-identical to the spec'd behaviour."""
import numpy as np

from optimus9.compute.breaching_line import predict_breach


def test_tol_zero_is_the_spec():
    k = [75, 75, 50, 90, 20]
    mn = [56, 56, 56, 56, 5]
    mj = [120, 90, 120, 120, 44]
    assert list(predict_breach(k, mn, mj, tol=0.0)) == [1, 0, 0, 0, -1]


def test_tol_relaxes_only_the_overshoot():
    # anchor 90 overshoots by 5, k undershoots by 10 -> false at tol=0, true at tol=6
    assert predict_breach([75], [56], [90], tol=0.0)[0] == 0
    assert predict_breach([75], [56], [90], tol=6.0)[0] == 1


def test_tol_cannot_fire_with_an_ib_anchor():
    # anchor 80 is inside the boundary: no tolerance may create a prediction
    assert predict_breach([75], [56], [80], tol=50.0)[0] == 0


def test_tol_mirrors_on_the_lo_side():
    assert predict_breach([25], [10], [56], tol=0.0)[0] == 0
    assert predict_breach([25], [10], [56], tol=6.0)[0] == -1
