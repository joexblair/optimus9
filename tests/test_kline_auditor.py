"""
Behaviour-by-example for the kline auditor's pure core (the DoD — no separate design
doc). The auditor independently rebuilds 5s bars from Bybit REST 1s samples and
validates them against kline_collection (5s) + the official closed 1m bar. These cases
pin: the bar construction (mirrors BarBuilder._build_one exactly), the zero-tolerance
OHLC verdict, and the 1m three-way reconcile with a dialable volume tolerance.
"""
from optimus9.data.kline_auditor import (
    build_5s_bar, compare_5s, aggregate_1m, reconcile_1m,
)


# ── 5s construction: mirror BarBuilder._build_one, from REST samples ─────────
def test_build_gapless_open_extremes_include_open():
    # O = prior close (gapless, NOT the first sample); H/L include O; C = last sample
    assert build_5s_bar(100.0, [101, 99, 102, 100]) == (100.0, 102.0, 99.0, 100.0)


def test_build_cold_start_open_is_first_sample():
    # no prior close → open = first sample (matches BarBuilder's cold-start branch)
    assert build_5s_bar(None, [101, 99, 102]) == (101.0, 102.0, 99.0, 102.0)


def test_build_flat_samples_is_emergent_doji():
    # price held all window (no trade moved it) → O=H=L=C falls out of max/min/last
    assert build_5s_bar(100.0, [100, 100, 100]) == (100.0, 100.0, 100.0, 100.0)


def test_build_no_samples_dojis_at_prior_close():
    assert build_5s_bar(100.0, []) == (100.0, 100.0, 100.0, 100.0)


def test_build_cold_start_no_samples_is_none():
    assert build_5s_bar(None, []) is None


# ── 5s verdict: zero-tolerance OHLC ──────────────────────────────────────────
def test_5s_exact_match_is_ok():
    bar = (100.0, 102.0, 99.0, 101.0)
    assert compare_5s(bar, bar)['verdict'] == 'ok'


def test_5s_any_close_delta_is_mismatch():
    r = compare_5s((100.0, 102.0, 99.0, 101.0), (100.0, 102.0, 99.0, 101.5))
    assert r['verdict'] == 'mismatch' and r['fields'] == ['c']


def test_5s_high_delta_is_mismatch():
    r = compare_5s((100.0, 102.5, 99.0, 101.0), (100.0, 102.0, 99.0, 101.0))
    assert r['verdict'] == 'mismatch' and r['fields'] == ['h']


def test_5s_missing_kc_bar():
    assert compare_5s(None, (100.0, 100.0, 100.0, 100.0))['verdict'] == 'missing'


# ── 1m aggregate: five 5s bars → 1m OHLCV ────────────────────────────────────
def test_aggregate_1m_ohlcv():
    bars = [(100, 101, 100, 100.5, 10),
            (100.5, 103, 100.5, 102, 20),
            (102, 102, 98, 99, 30)]
    assert aggregate_1m(bars) == (100, 103, 98, 99, 60)   # O=first C=last H=max L=min V=sum


# ── 1m reconcile: official vs audit-agg vs kc-agg ────────────────────────────
def test_1m_all_three_agree():
    bar = (100, 103, 98, 99, 60)
    r = reconcile_1m(official=bar, audit=bar, kc=bar, vol_tol=0)
    assert r['official_vs_audit']['ok'] and r['official_vs_kc']['ok']


def test_1m_kc_close_diverges_from_exchange():
    official = (100, 103, 98, 99, 60)
    kc       = (100, 103, 98, 98, 60)            # our tape's close ≠ the exchange
    r = reconcile_1m(official=official, audit=official, kc=kc, vol_tol=0)
    assert r['official_vs_audit']['ok']
    assert not r['official_vs_kc']['ok'] and r['official_vs_kc']['ohlc'] == ['c']


def test_1m_volume_within_tolerance_ok():
    r = reconcile_1m((100, 103, 98, 99, 60.0), (100, 103, 98, 99, 60.0),
                     (100, 103, 98, 99, 60.4), vol_tol=0.5)
    assert r['official_vs_kc']['ok']


def test_1m_volume_beyond_tolerance_mismatch():
    r = reconcile_1m((100, 103, 98, 99, 60.0), (100, 103, 98, 99, 60.0),
                     (100, 103, 98, 99, 61.0), vol_tol=0.5)
    assert not r['official_vs_kc']['ok'] and r['official_vs_kc']['vol'] is True


def test_1m_volume_zero_tolerance_default():
    # default vol_tol=0 → any volume delta fails (your "dial in from 0" stance)
    r = reconcile_1m((100, 103, 98, 99, 60.0), (100, 103, 98, 99, 60.0),
                     (100, 103, 98, 99, 60.001))
    assert not r['official_vs_kc']['ok']
