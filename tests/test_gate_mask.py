"""
Tests for IndicatorComputer._mask_from_configs (gate sweep Stage 1).

The gate sweep drives gate computation from param dicts instead of DB-loaded
ic_pks. These verify the extracted, param-driven path (DB-free): empty case,
single-gate equivalence, and the AND-fold intersection semantics. The
byte-identity of the DB path (compute_gate_mask on [bnyM, bnyp]) is checked
live against a fixed-window snapshot; this file covers the pure logic.
"""
import numpy as np
import pandas as pd

from optimus9.compute.indicator_computer import IndicatorComputer as IC


def _base(n: int = 240, seed: int = 0) -> pd.DataFrame:
    rng   = np.random.default_rng(seed)
    t0    = 1_700_000_000_000                    # ms epoch, multiple of 5000
    ts    = t0 + np.arange(n) * 5000
    close = 100.0 + np.cumsum(rng.normal(0, 0.05, n))
    return pd.DataFrame({
        'timestamp': ts,
        'open':  close + rng.normal(0, 0.02, n),
        'high':  close + rng.uniform(0, 0.05, n),
        'low':   close - rng.uniform(0, 0.05, n),
        'close': close,
        'volume': np.ones(n),
    })


# Configs at the base TF (5s) so resample + align are identity — keeps the
# expected output computable without a DB.
_BB = dict(ic_itf_seconds=5, ic_line_type='bb', ic_src='close',
           ic_high_boundary=85, ic_low_boundary=15, ic_bb_len=10, ic_bb_mult=1.0)
_K  = dict(ic_itf_seconds=5, ic_line_type='k',  ic_src='hlc3',
           ic_high_boundary=85, ic_low_boundary=15,
           ic_k_len=3, ic_rsi_len=5, ic_stc_len=5)


def test_empty_configs_returns_zeros():
    base = _base()
    m = IC._mask_from_configs([], base, 'AND')
    assert m.shape == (len(base),)
    assert (m == 0).all()


def test_single_gate_matches_aligned_oob():
    base = _base()
    m = IC._mask_from_configs([_BB], base, 'AND')
    expected = IC.compute_oob_side(_BB, IC.resample(base, 5))  # identity at base TF
    assert np.array_equal(m.astype(np.int8), expected.astype(np.int8))


def test_and_fold_is_intersection():
    base    = _base()
    gate_df = IC.resample(base, 5)
    s1 = IC.align_to_base(IC.compute_oob_side(_BB, gate_df), gate_df, base)
    s2 = IC.align_to_base(IC.compute_oob_side(_K,  gate_df), gate_df, base)
    m  = IC._mask_from_configs([_BB, _K], base, 'AND')

    # AND breaches a direction iff BOTH gates breach that same direction
    for v in (1, -1):
        assert np.array_equal(m == v, (s1 == v) & (s2 == v))
    # never opens unless both gates are out-of-band
    assert (((m != 0)) <= ((s1 != 0) & (s2 != 0))).all()


def test_and_is_stricter_than_or():
    base = _base()
    n_and = int((IC._mask_from_configs([_BB, _K], base, 'AND') != 0).sum())
    n_or  = int((IC._mask_from_configs([_BB, _K], base, 'OR')  != 0).sum())
    assert n_and <= n_or
