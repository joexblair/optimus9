"""wan_reload's rule (Joe 1002), on synthetic liveness rows. No ssh is run here.

W1  trades within 50 s of the socket restart resolve the episode - no reload
W2  no trades for 50 s after the restart -> one reload, decided at restart + 50 s
W3  after a reload the first trade is recorded with its delay - Joe's infra signal
W4  no limit: a second stall after the recovery opens a second episode and a second reload
W5  a trade BEFORE the restart does not resolve it
"""
import sys

sys.path.insert(0, '/home/joe/thecodes')
from optimus9.live.wan_reload import Episodes  # noqa: E402

S = 1000


def stall(t):
    return dict(t_ms=t, ev='stall-restart')


def sec(t, trades):
    return dict(t_ms=t, msgs=trades, trades=trades)


def test_w1_trades_resolve():
    e = Episodes()
    assert e.feed(stall(100 * S)) == []
    assert e.tick(120 * S) == []
    out = e.feed(sec(130 * S, 3))
    assert out and out[0][0] == 'resolved' and out[0][1]['first_trade_ms'] == 130 * S
    assert e.tick(200 * S) == []


def test_w2_reload_at_50s():
    e = Episodes()
    e.feed(stall(100 * S))
    assert e.tick(149 * S) == []
    out = e.tick(150 * S)
    assert out == [('reload', dict(restart_ms=100 * S, last_trade_ms=None, decided_ms=150 * S))]


def test_w3_recovery_recorded():
    e = Episodes()
    e.feed(stall(100 * S)); e.tick(150 * S)
    out = e.feed(sec(172 * S, 1))
    assert out[0][0] == 'recovered' and out[0][1]['recovery_s'] == 22.0


def test_w4_no_limit():
    e = Episodes()
    e.feed(stall(100 * S)); e.tick(150 * S); e.feed(sec(160 * S, 1))
    e.feed(stall(300 * S))
    assert e.tick(350 * S)[0][0] == 'reload'


def test_w5_trade_before_restart_does_not_resolve():
    e = Episodes()
    e.feed(sec(90 * S, 2))
    e.feed(stall(100 * S))
    assert e.feed(sec(99 * S, 2)) == []
    assert e.tick(150 * S)[0][0] == 'reload'
