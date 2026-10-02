"""test_trade_walk — holds what the 1002 `TradeBook` stepper added to `trade_walk`.

The pre-1002 behaviour is held separately, against the committed code read from git:
`docs/octo-freedom/1002_live_producer/regress_trade_walk.py` (5,000 random cases, 0 mismatches).

    T1  `walk()` and a hand-driven `TradeBook` give the same trades, bar for bar
    T2  `open_dr` sets the trade's side, not `dr[k]` - Joe 1001: the arm's dr governs
    T3  a same-dr signal while a trade is open is NOTED and does nothing - Joe 1002: *"no pyramid
        trades. note the signal for recon and keep walking"*
    T4  `label` names both the opener and an opposing close; the default stays 'sig_utc'
    T5  the stepper refuses a skipped bar, the same guard as `ArmState` and `LeashWalk`

    python3 -m pytest tests/test_trade_walk.py -q
    python3 tests/test_trade_walk.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optimus9.compute.trade_walk import TradeBook, walk  # noqa: E402


def _series(n=4000, seed=3):
    rng = np.random.default_rng(seed)
    dr = np.zeros(n, np.int8)
    k, cur = 5, 1
    while k < n:
        L = int(rng.integers(5, 300)); dr[k:k + L] = cur; cur = -cur; k += L
    px = 100.0 * np.exp(np.cumsum(rng.normal(0, 0.002, n)))
    opens = np.flatnonzero(rng.random(n) < 0.01)
    opens = opens[opens > 10]                    # after the first latch: a signal on a dr-0 bar opens a
    return dr, px, opens                         # dr-0 trade that nothing closes (pre-1002 behaviour too)


def test_t1_walk_equals_hand_driven_book():
    dr, px, opens = _series()
    trades, pos = walk(opens, dr, px, 1, len(dr) - 1, 0.70)
    book = TradeBook(0.70)
    got, O = [], set(int(x) for x in opens)
    for k in range(1, len(dr)):
        for ev in book.step(k, int(dr[k]), int(dr[k - 1]), float(px[k]), k in O):
            if ev[0] == 'close':
                got.append(ev[1])
    assert len(trades) > 20, 'T1 setup: too few trades to compare (%d)' % len(trades)
    assert got == trades, 'T1: walk() and the hand-driven book disagree'
    assert book.pos == pos, 'T1: final open trade differs'
    return len(trades)


def test_t2_open_dr_sets_the_side():
    n = 20
    dr = np.ones(n, np.int8)                     # the series says +1 everywhere
    px = np.full(n, 100.0)
    trades, pos = walk([5], dr, px, 1, n - 1, 0.70, open_dr={5: -1})
    assert pos is not None and pos['dr'] == -1, 'T2: open_dr did not set the side: %r' % (pos,)
    trades0, pos0 = walk([5], dr, px, 1, n - 1, 0.70)
    assert pos0['dr'] == 1, 'T2: default must read dr[k]'
    return pos['dr']


def test_t3_same_dr_signal_is_noted_and_inert():
    n = 30
    dr = np.ones(n, np.int8)
    px = np.full(n, 100.0)
    noted = []
    trades, pos = walk([5, 9, 14], dr, px, 1, n - 1, 0.70, open_dr={5: 1, 9: 1, 14: 1}, noted=noted)
    assert trades == [], 'T3: a same-dr signal closed a trade: %r' % (trades,)
    assert pos['open'] == 5, 'T3: a same-dr signal re-opened: %r' % (pos,)
    assert noted == [(9, 1), (14, 1)], 'T3: noted %r' % (noted,)
    return len(noted)


def test_t4_label_names_opener_and_opposing_close():
    n = 30
    dr = np.ones(n, np.int8)
    px = np.full(n, 100.0)
    trades, pos = walk([5, 12], dr, px, 1, n - 1, 0.70, label='octo-sig', open_dr={5: 1, 12: -1})
    assert trades == [dict(open=5, close=12, dr=1, opened_by='octo-sig', closed_by='octo-sig')], \
        'T4: %r' % (trades,)
    assert pos['opened_by'] == 'octo-sig' and pos['dr'] == -1
    trades0, _ = walk([5, 12], np.r_[np.ones(10, np.int8), -np.ones(20, np.int8)], px, 1, n - 1, None)
    assert trades0[0]['opened_by'] == 'sig_utc' and trades0[0]['closed_by'] == 'sig_utc', \
        'T4: the default label moved: %r' % (trades0,)
    return trades[0]['closed_by']


def test_t5_step_refuses_a_skipped_bar():
    book = TradeBook(0.70)
    book.step(10, 1, 1, 100.0, True)
    try:
        book.step(12, 1, 1, 100.0, False)
    except ValueError:
        return True
    raise AssertionError('T5: step accepted a skipped bar')


if __name__ == '__main__':
    print('T1 walk() == hand-driven TradeBook        OK  %d trades' % test_t1_walk_equals_hand_driven_book())
    print('T2 open_dr sets the side                  OK  dr %+d' % test_t2_open_dr_sets_the_side())
    print('T3 same-dr signal noted, inert            OK  %d noted' % test_t3_same_dr_signal_is_noted_and_inert())
    print('T4 label names opener + opposing close    OK  %s' % test_t4_label_names_opener_and_opposing_close())
    print('T5 step refuses a skipped bar             OK' if test_t5_step_refuses_a_skipped_bar() else 'FAIL')
