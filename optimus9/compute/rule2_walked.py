"""rule2_walked — `walked`, and the bar it completes on. Joe 0925.

ONE JOB: walk forward from a sig_utc and say where the walk ends. It produces no trade signal, owns
no fence, and reads no DB. The line mechanics are `rule2_trajectory`'s and the 3roob test is
`three_r_oob`'s; this module only decides where the walk stops.

JOE'S TWO TERMINATORS, VERBATIM

  0925, the quiet terminator:
    "do we have a definition for walked is complete? it's important that `walked` stops when all of
     the 3 lines are not printing trajectory"

  0925, the 3roob terminator:
    "this needs an arm that resets on dr-flip. we only test for 3-r-oob during the `walked` mech.
     ie if `walked` has completed and not found 3-r-oob, the arm is disabled"
    "the table shows that 3-r-oob (which I shortened to 3roob) needs to be baked in so that #6 is
     completed by the 3roob mech at 18:15"

  and the outer bound is the dr flip, which has been the backstop since 0922.

THE QUIET TEST IS A SINGLE BAR, AND THAT IS JOE'S WORDING. There is no confirmation window on it.
Measured #9, 09-03, dr +1: the walk completes at 13:06:10 on an 11 bar = 55 s hole. ws3r lapsed
because it fell 55.23 -> 47.04 in one 5 s print at 13:06:05, which became its own dr-opposed
extrema — 1 bar back, travel +0.00, against `min_bars` 24. ws1r carried again at 13:07:05. The
55 s hole ends the walk. Joe has seen this number and the wording stands.

WHICH TERMINATOR WINS. The earlier bar. On the 11 IS rows the 3roob bar is earlier on 3 of them:
#6 18:15:00 against 18:46:20, #8 06:39:00 against 06:45:10, #12 06:35:00 against 06:46:00.

THE ARM IS THE WALK'S OWN LIFE. Joe asked for an arm that resets on the dr flip and is disabled
when the walk completes without finding 3roob. That is exactly a search bounded by [sig_utc, the
completion bar], so the arm needs no separate state: `reason` says whether 3roob was what ended it.

THE SIGNAL AT A 3roob COMPLETION IS THE MAGE-REV. Joe 0926, asked directly whether it was the 3roob
bar itself or the mage-rev walked from it: *"the mage-rev"*. `signal` does that and nothing else.

THE tf COMES FROM §22.10's HIGHEST-TF RULE, read at the completion bar. On all three 3roob rows all
three lines carry at complete - 1, so the highest is ws3 with nothing to break a tie on.

`sig_lookback` HAS NO DEFAULT ON `signal`. The caller states it. Joe's banked value is 24 bars =
2 min, §22.17, and #6 is the row it was raised for: the gcws30Mage sig at 09-02 18:15:00 sits
1 bar = 5 s before the ws3Mage rev anchor at 18:15:05, so a strict "after the anchor" skips it and
the walk lands 18:37:45 instead of 18:15:15.

CAUSAL. `trajectory` reads bars at or before the test bar; `three_r_oob.held` reads a backward
tolerance window. The walk visits bars in order and never reads past the bar it is on.
"""
import numpy as np

from .rule2_trajectory import trajectory
from .three_r_oob import held


def carrying(lines, dr, k, block, min_bars, min_travel=0.0):
    """Which of the lines carry trajectory at bar `k`. -> sorted list of keys."""
    return [t for t in sorted(lines)
            if trajectory(lines[t], dr, int(k), block, min_bars, min_travel)['has']]


def walked(lines, dr, k0, end, block, min_bars, tol_bars, oob=(15.0, 85.0), min_travel=0.0):
    """Walk from `k0` to `end` and return where it completes. -> a dict, never None.

    lines     {1: ws1r, 2: ws2r, 3: ws3r} on the 5 s grid
    dr        the stretch's dr, +1 or -1
    k0        the sig_utc bar the walk starts from
    end       the dr flip bar. The walk reads no bar past it
    block     `anchor_floater.block`, 60 bars = 300 s
    min_bars  `trajectory` threshold, 24 bars = 2 min
    tol_bars  the 3roob tolerance, 12 bars = 60 s
    oob       (15.0, 85.0). Always

    keys: bar, reason, carrying, quiet_bar, oob_bar
      bar        the completion bar
      reason     'three_r_oob', 'quiet', or 'dr_flip' when neither fired inside the stretch
      carrying   the lines carrying trajectory at bar - 1, i.e. what the walk was on at the end
      quiet_bar  the first bar with no line carrying, or None
      oob_bar    the first 3roob event bar, or None

    BOTH terminator bars are reported whichever one won, so the one that did not end the walk
    stays visible. The walk still stops at the earlier of them.
    """
    k0 = int(k0); end = int(end)
    h = held(lines, dr, k0, end, tol_bars, oob)
    oob_bar = None
    quiet_bar = None
    for i in range(k0, end + 1):
        if oob_bar is None and bool(h[i - k0]):
            oob_bar = i
        if quiet_bar is None and not carrying(lines, dr, i, block, min_bars, min_travel):
            quiet_bar = i
        if oob_bar is not None and quiet_bar is not None:
            break

    if oob_bar is not None and (quiet_bar is None or oob_bar <= quiet_bar):
        bar, reason = oob_bar, 'three_r_oob'
    elif quiet_bar is not None:
        bar, reason = quiet_bar, 'quiet'
    else:
        bar, reason = end, 'dr_flip'

    prev = max(k0, bar - 1)
    return {'bar': bar, 'reason': reason,
            'carrying': carrying(lines, dr, prev, block, min_bars, min_travel),
            'quiet_bar': quiet_bar, 'oob_bar': oob_bar}


def signal(walk, dr, mage_rev, end, sig_lookback):
    """The trade signal at the walk's completion bar. -> a dict, never None.

    Joe 0926: *"the mage-rev"*.

    walk          a `walked` result
    mage_rev      a callable (tf, dr, from_bar, sig_lookback) -> bar or None, the ws{tf}Mage-rev
                  ordered walk. Passed in so `compute/` keeps no dependency on the jig
    end           the dr flip bar. A print past it is not a signal
    sig_lookback  NO DEFAULT. Joe's banked value is 24 bars = 2 min, §22.17

    keys: tf, bar, raw
      tf   the highest line carrying at the completion bar - 1, or None when none carries
      raw  what the walk returned, unbounded, so a print past `end` stays visible
      bar  raw, or None when it lands past `end` or no tf was available
    """
    tf = max(walk['carrying']) if walk['carrying'] else None
    out = {'tf': tf, 'bar': None, 'raw': None}
    if tf is None:
        return out
    b = mage_rev(tf, int(dr), int(walk['bar']), int(sig_lookback))
    out['raw'] = b
    if b is not None and b <= int(end):
        out['bar'] = b
    return out
