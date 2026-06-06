"""
Behaviour-by-example for the kline auditor's pure core (the DoD — no separate design
doc). The auditor independently rebuilds 5s bars from Bybit REST 1s samples and records
the per-field O/H/L/C variance IN TICKS vs kline_collection (5s) + the official closed
1m bar. These cases pin: the bar construction (mirrors BarBuilder._build_one), the 1m
aggregate, and the tick-variance measure (observe mode).
"""
from optimus9.data.kline_auditor import build_5s_bar, aggregate_1m, tick_variance


# ── 5s construction: mirror BarBuilder._build_one, from REST samples ─────────
def test_build_gapless_open_extremes_include_open():
    assert build_5s_bar(100.0, [101, 99, 102, 100]) == (100.0, 102.0, 99.0, 100.0)


def test_build_cold_start_open_is_first_sample():
    assert build_5s_bar(None, [101, 99, 102]) == (101.0, 102.0, 99.0, 102.0)


def test_build_flat_samples_is_emergent_doji():
    assert build_5s_bar(100.0, [100, 100, 100]) == (100.0, 100.0, 100.0, 100.0)


def test_build_no_samples_dojis_at_prior_close():
    assert build_5s_bar(100.0, []) == (100.0, 100.0, 100.0, 100.0)


def test_build_cold_start_no_samples_is_none():
    assert build_5s_bar(None, []) is None


# ── 1m aggregate: a minute's 5s bars → 1m OHLCV ──────────────────────────────
def test_aggregate_1m_ohlcv():
    bars = [(100, 101, 100, 100.5, 10),
            (100.5, 103, 100.5, 102, 20),
            (102, 102, 98, 99, 30)]
    assert aggregate_1m(bars) == (100, 103, 98, 99, 60)   # O=first C=last H=max L=min V=sum


# ── tick variance (observe mode): per-field O/H/L/C in ticks ─────────────────
TICK = 0.00001


def test_tick_variance_exact_match_is_all_zero():
    bar = (0.10000, 0.10002, 0.09998, 0.10001)
    assert tick_variance(bar, bar, TICK) == {'o': 0, 'h': 0, 'l': 0, 'c': 0}


def test_tick_variance_per_field_counts():
    kc    = (0.10000, 0.10002, 0.09998, 0.10001)
    audit = (0.10000, 0.10001, 0.09998, 0.09999)          # h +1 tick, c +2 ticks
    assert tick_variance(kc, audit, TICK) == {'o': 0, 'h': 1, 'l': 0, 'c': 2}


def test_tick_variance_signed():
    kc    = (0.09999, 0.10000, 0.10000, 0.10000)          # o is 1 tick BELOW audit
    audit = (0.10000, 0.10000, 0.10000, 0.10000)
    assert tick_variance(kc, audit, TICK)['o'] == -1


def test_tick_variance_rounds_to_nearest_tick():
    base = (0.10000, 0.10000, 0.10000, 0.10000)
    assert tick_variance((0.100004, 0.1, 0.1, 0.1), base, TICK)['o'] == 0   # 0.4 tick → 0
    assert tick_variance((0.100006, 0.1, 0.1, 0.1), base, TICK)['o'] == 1   # 0.6 tick → 1


def test_tick_variance_missing_bar_is_none():
    bar = (0.1, 0.1, 0.1, 0.1)
    assert tick_variance(None, bar, TICK) is None
    assert tick_variance(bar, None, TICK) is None
