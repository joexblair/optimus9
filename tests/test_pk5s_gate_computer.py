"""Tests for optimus9.compute.pk5s_gate_computer state-machine pieces."""

import numpy as np

from optimus9 import Pk5sGateComputer


def test_decision_delay_fires_after_n_consecutive():
    """A direction must persist for `delay` bars before firing."""
    pk_raw = np.array([0, 1, 1, 1, 1, 0, 0], dtype=np.int8)
    # delay=3 means: bar 1 starts countdown, bars 2 and 3 decrement, bar 4 fires
    out = Pk5sGateComputer._apply_decision_delay(pk_raw, delay=3)
    assert out[4] == 1, f'expected fire at bar 4, got {out}'
    assert out[3] == 0
    assert out[1] == 0


def test_decision_delay_direction_change_resets_countdown():
    """A flip mid-countdown restarts the count with the new direction."""
    pk_raw = np.array([0, 1, 1, -1, -1, -1, -1], dtype=np.int8)
    out = Pk5sGateComputer._apply_decision_delay(pk_raw, delay=3)
    # bar 3 flips to -1 → countdown restart; bars 4,5 decrement; bar 6 fires
    assert out[6] == -1
    assert all(out[:6] == 0)


def test_decision_delay_zero_clears_pending():
    """Returning to neutral clears the pending state — no implicit re-arm."""
    pk_raw = np.array([1, 1, 0, 1, 1, 1, 1], dtype=np.int8)
    out = Pk5sGateComputer._apply_decision_delay(pk_raw, delay=3)
    # bar 2 resets; bar 3 starts fresh countdown; bars 4,5 decrement; bar 6 fires
    assert out[6] == 1
    assert all(out[:6] == 0)
