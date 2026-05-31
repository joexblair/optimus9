"""
Tests for optimus9.compute.profit_partition (gate sweep Stage 0).

Pure-math: hand-built close sequences with known ±0.9% crossings, plus the
bounded-MAE property the design relies on. threshold_pct=0.9, entry=100 →
up level 100.9, down level 99.1.
"""
import numpy as np

from optimus9.compute.profit_partition import (
    compute_profit_partition, summarize_partition, LONG, SHORT, NEITHER,
)


def _run(close, horizon=50):
    return compute_profit_partition(np.array(close, dtype=float),
                                    threshold_pct=0.9, horizon=horizon)


def test_clear_long():
    r = _run([100, 100.95])
    assert r['cls'][0] == LONG
    assert r['bars_to_win'][0] == 1
    assert r['mae_pct'][0] == 0.0          # no adverse before the win


def test_clear_short():
    r = _run([100, 99.0])
    assert r['cls'][0] == SHORT
    assert r['bars_to_win'][0] == 1
    assert r['mae_pct'][0] == 0.0


def test_long_with_drawdown_records_mae():
    # dips to 99.5 (-0.5%, not past -0.9%) then crosses +0.9%
    r = _run([100, 99.5, 100.95])
    assert r['cls'][0] == LONG
    assert r['bars_to_win'][0] == 2
    assert abs(r['mae_pct'][0] - 0.5) < 1e-9


def test_down_cross_wins_even_if_up_comes_later():
    # -0.9% at bar 1 beats +0.9% at bar 2 → short, despite the later spike
    r = _run([100, 99.0, 101.0])
    assert r['cls'][0] == SHORT
    assert r['bars_to_win'][0] == 1


def test_neither_when_no_cross_in_horizon():
    r = _run([100, 100.3, 99.8, 100.2, 99.9, 100.1])
    assert r['cls'][0] == NEITHER
    assert np.isnan(r['mae_pct'][0])
    assert r['bars_to_win'][0] == -1


def test_horizon_cutoff():
    close = [100, 100.2, 100.3, 100.95]      # +0.9% only at bar 3
    assert _run(close, horizon=2)['cls'][0] == NEITHER   # bar 3 out of reach
    assert _run(close, horizon=3)['cls'][0] == LONG      # bar 3 in reach


def test_mae_bounded_under_threshold():
    # deterministic oscillation that produces a mix of winners
    i = np.arange(4000, dtype=float)
    close = 100.0 + 2.0 * np.sin(i * 0.05) + 0.6 * np.sin(i * 0.31)
    r = compute_profit_partition(close, threshold_pct=0.9, horizon=400)
    winners = r['mae_pct'][~np.isnan(r['mae_pct'])]
    assert winners.size > 0
    assert winners.max() < 0.9               # strictly bounded by construction
    assert (winners >= 0.0).all()


def test_summary_fractions_sum_to_one():
    i = np.arange(2000, dtype=float)
    close = 100.0 + 1.5 * np.sin(i * 0.07)
    r = compute_profit_partition(close, threshold_pct=0.9, horizon=300)
    s = summarize_partition(r['cls'], r['mae_pct'], threshold_pct=0.9)
    total = s['long_frac'] + s['short_frac'] + s['neither_frac']
    assert abs(total - 1.0) < 1e-9
    assert abs(s['tradeable_frac'] - (s['long_frac'] + s['short_frac'])) < 1e-9
