"""
Tests for optimus9.orchestration.gate_sweep_runner (gate sweep core).

DB-free: synthetic base + partition, hand-built grid. Locks the param→config
mapping, the per-combo result shape, and descending-by-score ordering.
"""
import numpy as np
import pandas as pd

from optimus9.orchestration.gate_sweep_runner import (
    build_gate_configs, score_combo, run_sweep, SCOUT_A_TEMPLATE,
)
from optimus9.compute.profit_partition import compute_profit_partition


def _base(n: int = 1200, seed: int = 1) -> pd.DataFrame:
    rng   = np.random.default_rng(seed)
    t0    = 1_700_000_000_000
    ts    = t0 + np.arange(n) * 5000
    close = 100.0 + np.cumsum(rng.normal(0, 0.06, n))
    return pd.DataFrame({
        'timestamp': ts,
        'open':  close + rng.normal(0, 0.02, n),
        'high':  close + rng.uniform(0, 0.06, n),
        'low':   close - rng.uniform(0, 0.06, n),
        'close': close,
        'volume': np.ones(n),
    })


def test_build_gate_configs_maps_fields():
    combo = dict(M_src='hl2', M_bb_len=58, M_bb_mult=1.24, p_src='ohlc4', p_k_len=21)
    cfgM, cfgP = build_gate_configs(combo, SCOUT_A_TEMPLATE)
    # bnyM (BB)
    assert cfgM['ic_line_type'] == 'bb'
    assert cfgM['ic_bb_len'] == 58 and cfgM['ic_bb_mult'] == 1.24 and cfgM['ic_src'] == 'hl2'
    assert cfgM['ic_itf_seconds'] == 30
    assert cfgM['ic_high_boundary'] == 85 and cfgM['ic_low_boundary'] == 15
    # bnyp (K) — rsi/stc fixed
    assert cfgP['ic_line_type'] == 'k'
    assert cfgP['ic_k_len'] == 21 and cfgP['ic_rsi_len'] == 114 and cfgP['ic_stc_len'] == 105
    assert cfgP['ic_src'] == 'ohlc4'


def test_score_combo_shape():
    base = _base()
    P = compute_profit_partition(base['close'].to_numpy(float),
                                 threshold_pct=0.9, horizon=60)['cls']
    combo = dict(M_src='hl2', M_bb_len=40, M_bb_mult=1.0, p_src='ohlc4', p_k_len=14)
    r = score_combo(combo, SCOUT_A_TEMPLATE, base, P)
    assert 'score' in r and 'painted' in r and 'wrong_side' in r
    assert len(r['solo_scores']) == 2
    assert r['combo'] == combo


def test_run_sweep_sorts_descending():
    base = _base()
    P = compute_profit_partition(base['close'].to_numpy(float),
                                 threshold_pct=0.9, horizon=60)['cls']
    combos = [dict(M_src='hl2', M_bb_len=L, M_bb_mult=1.0, p_src='ohlc4', p_k_len=k)
              for L in (20, 40) for k in (10, 20)]
    res = run_sweep(combos, SCOUT_A_TEMPLATE, base, P)
    assert len(res) == 4
    for r in res:
        assert r['combo'] in combos and len(r['solo_scores']) == 2
    scores = [r['score'] for r in res if not np.isnan(r['score'])]
    assert scores == sorted(scores, reverse=True)
