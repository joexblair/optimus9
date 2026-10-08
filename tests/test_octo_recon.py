"""test_octo_recon — the recon's expectation rules, on synthetic book events.

    R1  an open implies an `open` line with `octo-sig`; dr +1 -> Sell (Joe 0925)
    R2  an open on a bar that fell in a feed gap of 5 min or more implies `non-trading octo-sig`, and
        that trade's close implies NO close line - an open without a close (Joe 1002)
    R3  a same-dr signal ('inert') implies an `open` line with `non-trading octo-sig`

    python3 tests/test_octo_recon.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optimus9.live.octo_recon import expected_lines  # noqa: E402

B = 5000


def test_r1_open():
    ev = [(100 * B, ('open', dict(open=100, dr=1, opened_by='octo-sig', left=False)))]
    assert expected_lines(ev, {}) == {100 * B: [('open', 'Sell', 'octo-sig')]}
    return 1


def test_r2_gap_open_has_no_close():
    ev = [(100 * B, ('open', dict(open=100, dr=-1, opened_by='octo-sig', left=False))),
          (150 * B, ('close', dict(open=100, close=150, dr=-1, opened_by='octo-sig', closed_by='dr-flip')))]
    got = expected_lines(ev, {100 * B: True})
    assert got == {100 * B: [('open', 'Buy', 'non-trading octo-sig')]}, got
    got = expected_lines(ev, {})
    assert got == {100 * B: [('open', 'Buy', 'octo-sig')], 150 * B: [('close', 'Buy', 'dr-flip')]}, got
    return 2


def test_r3_inert():
    ev = [(120 * B, ('inert', 120, 1))]
    assert expected_lines(ev, {}) == {120 * B: [('open', 'Sell', 'non-trading octo-sig')]}
    return 1


if __name__ == '__main__':
    print('R1 open -> octo-sig line, dr +1 Sell       OK  %d' % test_r1_open())
    print('R2 gap open: non-trading, no close line   OK  %d' % test_r2_gap_open_has_no_close())
    print('R3 inert -> non-trading octo-sig line     OK  %d' % test_r3_inert())


def test_r4_signal_on_a_stop_bar_is_expected_as_noted():
    from optimus9.live.octo_recon import _note_consumed
    stop = ('close', dict(open=90, close=120, dr=-1, opened_by='octo-sig', closed_by='stop'))
    ev = [(120 * B, e) for e in _note_consumed(120 * B, [stop], 1)]
    assert expected_lines(ev, {}) == {120 * B: [('close', 'Buy', 'stop'), ('open', 'Sell', 'non-trading octo-sig')]}
    assert _note_consumed(120 * B, [stop], None) == [stop]           # no signal on the bar: unchanged
