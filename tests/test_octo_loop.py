"""test_octo_loop — the decide layer maps the producer's records to orders under Joe's 1002 rulings.

The producer is stubbed: these checks hold `OctoLoop`'s mapping, not the walk (that is
`docs/octo-freedom/1002_live_producer/replay_0901.py`'s job).

    L1  an octo-sig at dr +1 opens a Sell; dr -1 opens a Buy (Joe 0925: dr +1 = SHORT)
    L2  a reversal closes the open side, then opens the other, in that order
    L3  a same-dr octo-sig places nothing and is dumped as `non-trading octo-sig` (Joe 1002)
    L4  a feed gap: under 5 min the open is placed late; 5 min or more it is not, and is dumped as
        `non-trading octo-sig`; a close in the gap is placed either way (Joe 1002)
    L5  a position on the exchange at startup stops the loop - adopt / flatten is Joe's
    L6  every dump line carries only the five ruled fields

    python3 tests/test_octo_loop.py
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optimus9.live.octo_loop import OctoLoop  # noqa: E402
from optimus9.live.trade_signal_dump import TradeSignalDump  # noqa: E402

B = 5000


class _Arm:
    live, arm_dr = False, 0


class _Walk:
    arm = _Arm()


class _Inp:
    def __init__(self, T):
        self.ts = [T - B, T]


class _Prod:
    """Hands back whatever records the test queues for each call."""

    def __init__(self):
        self.queue = []
        self.walk = _Walk()
        self.book = None
        self._prev_emitted = False

    def window(self, end_ms):
        T = (int(end_ms) - 1) // B * B - B
        return object(), _Inp(T)

    def advance(self, inp, live_from):
        return self.queue.pop(0) if self.queue else []


def _loop():
    fd, path = tempfile.mkstemp(suffix='.log'); os.close(fd)
    L = OctoLoop.__new__(OctoLoop)
    L.cfg, L.prod, L.dump, L.log = None, _Prod(), TradeSignalDump(path), (lambda *a: None)
    L._W = L._inp = L._live_from = L._last_T = None
    return L, path


def _rec(ts, events):
    return dict(ts=ts, events=events)


def _bar(L, T, recs, positions=None):
    L.prod.queue.append(recs)
    W = L.window(T + B + 700)
    return L.intents(W, positions or {})


def _dump(path):
    return [json.loads(x) for x in open(path)]


def test_l1_sides():
    L, p = _loop()
    T = 1_000_000 * B
    out = _bar(L, T, [_rec(T, [('open', dict(open=T // B, dr=1, opened_by='octo-sig', left=False))])])
    assert [(i.action, i.side, i.reason) for i in out] == [('open', 'Sell', 'octo-sig')], out
    out = _bar(L, T + B, [_rec(T + B, [('open', dict(open=T // B + 1, dr=-1, opened_by='octo-sig',
                                                           left=False))])])
    assert [(i.action, i.side) for i in out] == [('open', 'Buy')], out
    return len(_dump(p))


def test_l2_reversal_order():
    L, p = _loop()
    T = 1_000_000 * B
    _bar(L, T, [])
    ev = [('close', dict(open=1, close=T // B + 1, dr=1, opened_by='octo-sig', closed_by='octo-sig')),
          ('open', dict(open=T // B + 1, dr=-1, opened_by='octo-sig', left=False))]
    out = _bar(L, T + B, [_rec(T + B, ev)], positions={'Sell': {'side': 'Sell', 'size': 7.0}})
    assert [(i.action, i.side, i.qty, i.reason) for i in out] == \
        [('close', 'Buy', 7.0, 'octo-sig'), ('open', 'Buy', 0.0, 'octo-sig')], out
    return len(out)


def test_l3_same_dr_is_noted_not_placed():
    L, p = _loop()
    T = 1_000_000 * B
    _bar(L, T, [])
    out = _bar(L, T + B, [_rec(T + B, [('inert', T // B + 1, 1)])], positions={'Sell': {'size': 1.0}})
    assert out == [], out
    d = _dump(p)[-1]
    assert (d['action'], d['side'], d['reason'], d['bar_ms']) == ('open', 'Sell', 'non-trading octo-sig',
                                                                  T + B), d
    return d['reason']


def test_l4_feed_gap():
    L, p = _loop()
    T = 1_000_000 * B
    _bar(L, T, [])
    o = ('open', dict(open=0, dr=1, opened_by='octo-sig', left=False))
    c = ('close', dict(open=0, close=0, dr=-1, opened_by='octo-sig', closed_by='dr-flip'))
    # 4 min 55 s gap: the open at the first missed bar is placed, late
    T2 = T + 59 * B
    out = _bar(L, T2, [_rec(T + B, [o]), _rec(T2, [])])
    assert [(i.action, i.side) for i in out] == [('open', 'Sell')], out
    # 5 min gap: the open is not placed and is dumped as non-trading; the close in the gap is placed
    T3 = T2 + 60 * B
    out = _bar(L, T3, [_rec(T2 + B, [c, o]), _rec(T3, [])], positions={'Buy': {'size': 3.0}})
    assert [(i.action, i.side, i.reason) for i in out] == [('close', 'Sell', 'dr-flip')], out
    assert _dump(p)[-1]['reason'] == 'non-trading octo-sig'
    return len(out)


def test_l5_position_at_startup_stops():
    L, p = _loop()
    try:
        _bar(L, 1_000_000 * B, [], positions={'Buy': {'size': 1.0}})
    except RuntimeError:
        return True
    raise AssertionError('L5: started on a position the book did not open')


def test_l6_dump_fields():
    L, p = _loop()
    T = 1_000_000 * B
    _bar(L, T, [_rec(T, [('open', dict(open=T // B, dr=1, opened_by='octo-sig', left=False))])])
    _bar(L, T + B, [_rec(T + B, [('inert', T // B + 1, 1)])])
    for d in _dump(p):
        assert sorted(d) == ['action', 'bar_ms', 'reason', 'side', 'wall_ms'], d
    return len(_dump(p))


if __name__ == '__main__':
    print('L1 dr +1 -> Sell, dr -1 -> Buy             OK  %d dump lines' % test_l1_sides())
    print('L2 reversal: close, then open             OK  %d intents' % test_l2_reversal_order())
    print('L3 same-dr: dumped, not placed            OK  %s' % test_l3_same_dr_is_noted_not_placed())
    print('L4 feed gap <5 min placed, >=5 not        OK  %d intent' % test_l4_feed_gap())
    print('L5 position at startup stops the loop     OK' if test_l5_position_at_startup_stops() else 'FAIL')
    print('L6 dump lines carry the five fields only  OK  %d lines' % test_l6_dump_fields())


def test_l7_signal_on_a_stop_bar_is_noted_not_placed():
    """Joe 1008 "b": the stop wins the bar (Joe 0929); the walk's signal on that bar is noted."""
    L, p = _loop()
    T = 1_000_000 * B
    _bar(L, T, [])
    stop = ('close', dict(open=1, close=T // B + 1, dr=-1, opened_by='octo-sig', closed_by='stop'))
    rec = dict(ts=T + B, events=[stop], live=True, fires=True, arm_dr=1)
    out = _bar(L, T + B, [rec], positions={'Buy': {'side': 'Buy', 'size': 5.0}})
    assert [(i.action, i.side, i.reason) for i in out] == [('close', 'Sell', 'stop')], out
    d = [(x['action'], x['side'], x['reason'], x['bar_ms']) for x in _dump(p)]
    assert d == [('close', 'Buy', 'stop', T + B), ('open', 'Sell', 'non-trading octo-sig', T + B)], d
    return len(d)
