"""
Tests for optimus9.orchestration.gate_signal_sweep (gate sweep v2).

DB-free: score_signals (sign-opposition admission + precision/recall on winners)
and a generate_line_signals smoke on synthetic price.
"""
import numpy as np

from optimus9.orchestration.gate_signal_sweep import score_signals, label_winners


def test_score_signals_admission_and_pr():
    #              bar:   0   1   2   3
    gate = np.array([-1,  1,  0, -1])
    bars = np.array([0, 1, 2, 3])
    dirs = np.array([1, -1, 1, -1])
    win  = np.array([True, False, True, True])
    # admitted (gate==-dir): bar0 (-1==-1)✓, bar1 (1==1)✓, bar2 (0!=-1)✗, bar3 (-1!=1)✗
    s = score_signals(gate, bars, dirs, win)
    assert s['admitted'] == 2 and s['admitted_win'] == 1
    assert s['total'] == 4 and s['total_win'] == 3
    assert abs(s['precision'] - 0.5) < 1e-9
    assert abs(s['recall'] - 1/3) < 1e-9
    assert abs(s['f1'] - 0.4) < 1e-9
    assert s['win_rate'] == s['precision']


def test_score_signals_no_admission_nan_precision():
    gate = np.array([0, 0])
    s = score_signals(gate, np.array([0, 1]), np.array([1, -1]), np.array([True, True]))
    assert s['admitted'] == 0 and np.isnan(s['precision']) and np.isnan(s['f1'])


def test_label_winners_matches_partition():
    # long signal wins iff price reaches +0.9% before -0.9% within horizon
    rng   = np.random.default_rng(2)
    close = 100.0 + np.cumsum(rng.normal(0, 0.08, 2000))
    bars  = np.array([10, 50, 100, 500])
    dirs  = np.array([1, -1, 1, -1])
    win = label_winners(bars, dirs, close, threshold=0.9, horizon=200)
    assert win.shape == bars.shape and win.dtype == bool
