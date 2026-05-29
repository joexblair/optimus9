"""
Tests for optimus9.compute.pk_signal_detector — r07 Step 3a.

Step 3a adds an optional vote_machine injection point. These tests pin the
3a contract:
  - the constructor accepts vote_machine (default None)
  - the None path (the gated grind path) is the only implemented flow
  - supplying a vote_machine raises until Step 3b lands

Byte-identical regression of the None path against pre-3a behaviour is
proven by the grind diff (baseline_3a.csv vs after-3a snapshot), not here.
"""
import numpy as np
import pytest

from optimus9 import PKSignalDetector, PKVoteMachine


def test_constructor_accepts_optional_vote_machine():
    """Injection point exists; defaults to None (unchanged gated path)."""
    assert PKSignalDetector()._vote_machine is None
    assert PKSignalDetector(vote_machine=None)._vote_machine is None
    vm = PKVoteMachine()
    assert PKSignalDetector(vote_machine=vm)._vote_machine is vm


def test_vote_machine_supplied_raises_until_step_3b():
    """The vote-engaged flow is Step 3b — supplying a vote_machine raises."""
    d = PKSignalDetector(vote_machine=PKVoteMachine())
    line = np.full(40, 50.0)
    dema = np.full(40, 50.0)
    oob  = np.zeros(40, dtype=int)
    with pytest.raises(NotImplementedError, match='Step 3b'):
        d.detect(line, dema, 5, 23, 8, 1, 10.0, oob,
                 {'len': 6, 'src': 'close', 'mult': 0.74})


def test_none_path_returns_list():
    """vote_machine=None drives the existing per-probe path (returns a list)."""
    d = PKSignalDetector(vote_machine=None)
    line = np.full(40, 50.0)
    dema = np.full(40, 50.0)
    oob  = np.zeros(40, dtype=int)
    out = d.detect(line, dema, 5, 23, 8, 1, 10.0, oob,
                   {'len': 6, 'src': 'close', 'mult': 0.74})
    assert isinstance(out, list)
