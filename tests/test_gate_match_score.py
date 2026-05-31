"""
Tests for optimus9.compute.gate_match_score (gate sweep Stage 1 scorer).

The polarity bridge is the high-risk bit: LO breach (-1) enables LONG (+1),
HI breach (+1) enables SHORT (-1), so a hit is `gate == -P`. The inversion
guard below fails loudly if anyone ever writes `gate == P`.
"""
import numpy as np

from optimus9.compute.gate_match_score import gate_match_score


def test_lo_breach_aligns_with_long():
    s = gate_match_score(np.array([-1]), np.array([1]))   # LO + long-P = hit
    assert s['score'] == 1.0 and s['hits'] == 1


def test_hi_breach_aligns_with_short():
    s = gate_match_score(np.array([1]), np.array([-1]))    # HI + short-P = hit
    assert s['score'] == 1.0 and s['hits'] == 1


def test_polarity_inversion_guard():
    # LO breach (-1) + short-P (-1): same sign → WRONG side, NOT a hit.
    # A `gate == P` scorer would wrongly score this 1.0.
    s = gate_match_score(np.array([-1]), np.array([-1]))
    assert s['score'] == 0.0
    assert s['hits'] == 0 and s['wrong_side'] == 1


def test_perfect_alignment():
    gate = np.array([-1,  1, -1,  1])
    P    = np.array([ 1, -1,  1, -1])
    s = gate_match_score(gate, P)
    assert s['score'] == 1.0
    assert s['hits'] == 4 and s['false_open'] == 0 and s['missed'] == 0


def test_mixed_counts():
    #            bar:  0   1   2   3   4   5   6
    gate = np.array([-1, -1,  1,  1,  0, -1,  0])
    P    = np.array([ 1, -1, -1,  1,  1,  0,  0])
    # hits: bar0 (LO+long), bar2 (HI+short)            → 2
    # wrong_side: bar1 (LO+short), bar3 (HI+long)      → 2
    # painted: bars 0-5                                → 6
    s = gate_match_score(gate, P)
    assert s['hits'] == 2
    assert s['painted'] == 6
    assert abs(s['score'] - 2 / 6) < 1e-9
    assert s['wrong_side'] == 2
    assert s['false_open'] == 3      # gate open at 0,1,2,3,5; not-hit at 1,3,5
    assert s['missed'] == 3          # P tradeable at 0,1,2,3,4; not-hit at 1,3,4


def test_nothing_painted_is_nan():
    s = gate_match_score(np.zeros(5, int), np.zeros(5, int))
    assert np.isnan(s['score'])
    assert s['painted'] == 0


def test_shape_mismatch_raises():
    try:
        gate_match_score(np.zeros(3), np.zeros(4))
        assert False, 'expected ValueError'
    except ValueError:
        pass
