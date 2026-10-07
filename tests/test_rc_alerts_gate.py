"""rc_alerts.ThrottleGate - Joe 1007: the API-throttle 1m incomplete alerts only with a downstream issue."""
import sys

sys.path.insert(0, '/home/joe/thecodes')
from optimus9.live.rc_alerts import ThrottleGate

M = 1791396000000                                     # 10-07 18:00:00, a minute start


def inc(m=M, audit=11, kc=12, official='True'):
    return {'source': 'kline_audit', 'kind': '1m incomplete', 'bar_ms': m,
            'detail': 'audit=%d/12 kc=%d/12 official=%s | tick var o/h/l/c None/None/None/None' % (audit, kc, official)}


def frozen(b):
    return {'source': 'kline_audit', 'kind': '5s frozen', 'bar_ms': b, 'detail': 'match | tick var o/h/l/c 0/0/0/0'}


def test_throttle_alone_is_silent():
    assert ThrottleGate().feed(inc()) == (False, None)


def test_downstream_before_the_1m_line_pairs_and_alerts():
    g = ThrottleGate()
    assert g.feed(frozen(M + 20_000)) is None              # no throttle yet: normal path decides
    a = g.feed(inc())
    assert a[0] is True and '1 downstream' in a[1] and '5s frozen 18:00:20' in a[1]


def test_downstream_after_the_1m_line_alerts():
    g = ThrottleGate()
    g.feed(inc())
    a = g.feed(frozen(M + 55_000))
    assert a[0] is True and 'API throttle at 18:00:00 + downstream 5s frozen 18:00:55' in a[1]


def test_a_verdict_in_another_minute_does_not_pair():
    g = ThrottleGate()
    g.feed(frozen(M + 60_000))                             # 18:01:00 - the next minute
    assert g.feed(inc()) == (False, None)
    assert g.feed(frozen(M - 5_000)) is None               # 17:59:55 - the minute before


def test_our_tape_short_or_official_missing_alerts_as_before():
    assert ThrottleGate().feed(inc(kc=11)) is None         # None = the normal path alerts it
    assert ThrottleGate().feed(inc(official='False')) is None


def test_other_sources_are_untouched():
    g = ThrottleGate()
    g.feed(inc())
    assert g.feed({'source': 'klinecollect', 'kind': 'ERROR', 'bar_ms': None, 'detail': 'x'}) is None
    assert g.feed({'source': 'o9live', 'kind': 'error', 'bar_ms': M + 10_000, 'detail': 'x'}) is None


def test_old_minutes_are_forgotten():
    g = ThrottleGate()
    g.feed(inc())
    g.feed(frozen(M + 11 * 60_000))                        # 11 min later moves 'newest' on
    assert M not in g.throttled
