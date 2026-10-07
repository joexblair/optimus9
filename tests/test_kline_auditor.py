"""
Behaviour-by-example for the kline auditor's pure core (the DoD — no separate design
doc). The auditor independently rebuilds 5s bars from Bybit REST 1s samples and records
the per-field O/H/L/C variance IN TICKS vs kline_collection (5s) + the official closed
1m bar. These cases pin: the bar construction (mirrors BarBuilder._build_one), the 1m
aggregate, and the tick-variance measure (observe mode).
"""
from optimus9.data.kline_auditor import build_5s_bar, aggregate_1m, tick_variance, is_frozen


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


# ── freeze detection (5s liveness): kc static while the REST price moved ──────
MOVE = 3 * TICK


def test_is_frozen_static_kc_while_rest_moved():
    recent = [(0.10000, 0.10000), (0.10000, 0.10002), (0.10000, 0.10004)]   # rest +4 ticks
    assert is_frozen(recent, MOVE)


def test_is_frozen_quiet_market_not_frozen():
    assert not is_frozen([(0.10000, 0.10000)] * 4, MOVE)                     # both static = quiet


def test_is_frozen_kc_moving_not_frozen():
    assert not is_frozen([(0.10000, 0.10000), (0.10001, 0.10002)], MOVE)    # kc moving


def test_is_frozen_rest_move_below_threshold():
    assert not is_frozen([(0.10000, 0.10000), (0.10000, 0.10001)], MOVE)    # rest +1 tick ≤ 3


# ── 1m reconcile when only the auditor's REST samples are short (Joe 1007) ──
import logging
from optimus9.data.kline_auditor import KlineAuditor
from optimus9.live.rc_alerts import ThrottleGate

M0 = 1791396000000


def _auditor(kc_bars, official):
    a = object.__new__(KlineAuditor)
    a._tick, a._log, a.rows = 0.00001, logging.getLogger('t'), []
    a._kc_minute = lambda tp, m: kc_bars
    a._official_1m = lambda sym, m: official
    a._record = lambda tp, ts, tier, verdict, kc, audit, off, var, detail: a.rows.append((verdict, detail))
    return a


def _bars(closes):
    return [(c, c, c, c, 10.0) for c in closes]


def _audit_5s(n):
    return {M0 + i * 5000: (0.18, 0.18, 0.18, 0.18) for i in range(n)}


def test_audit_short_tape_matches_stays_incomplete_and_the_alarm_stays_silent():
    kc = _bars([0.18] * 12)
    a = _auditor(kc, aggregate_1m(kc))
    a._reconcile_1m(1, 'X', M0, _audit_5s(11), 0.0)
    verdict, detail = a.rows[0]
    assert verdict == 'incomplete' and 'audit=11/12 kc=12/12 official=True' in detail and 'off_vs_kc:match' in detail
    rec = {'source': 'kline_audit', 'kind': '1m incomplete', 'bar_ms': M0, 'detail': detail}
    assert ThrottleGate().feed(rec) == (False, None)


def test_audit_short_tape_differs_is_a_variance():
    kc = _bars([0.18] * 12)
    off = list(aggregate_1m(kc)); off[3] = 0.18009                  # exchange close 9 ticks higher
    a = _auditor(kc, tuple(off))
    a._reconcile_1m(1, 'X', M0, _audit_5s(11), 0.0)
    verdict, detail = a.rows[0]
    assert verdict == 'variance' and ('off_vs_kc:c-9' in detail or 'off_vs_kc:c+9' in detail) and 'off_vs_audit:skipped' in detail


def test_our_tape_short_is_still_incomplete():
    kc = _bars([0.18] * 11)
    a = _auditor(kc, aggregate_1m(_bars([0.18] * 12)))
    a._reconcile_1m(1, 'X', M0, _audit_5s(12), 0.0)
    assert a.rows[0] == ('incomplete', 'audit=12/12 kc=11/12 official=True')
