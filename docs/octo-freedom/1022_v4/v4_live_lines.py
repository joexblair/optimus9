"""THE FOUR LINES THE WALK IS HANDED, ON THE LIVE READ. Joe 1029: *"completely drop prev-close"*.

WHAT THIS REPLACES. `v4_closed_prev.arm_lines` returned the same four things built from the
previous completed bar's close, held forward. That read is dropped: he asked whether a ws1r
crossing at 2026-08-30 00:19 would be reading a ws12r value set at 00:12, and measured at that bar
ws12r was 7.08 minutes stale and ws10r 9.08 minutes stale.

WHAT IT COST WHILE IT WAS STILL IN THE WALK'S PATH. His ws1b hold is meant to hold the
00:59:25..01:20:45 low excursion together as one event. On the live read ws1b's crossing back
inside at 01:04:50 holds only 4 bars, so at 12 bars it does not qualify and the excursion stands.
On the prev-close read the same moment is one clean crossing at 01:04:00 holding 24 bars, which
qualifies, so the hold had no effect and the exit fired at 01:04:55 either way.

THE SHAPE IS UNCHANGED, so every caller swaps one import and no mech is edited.
"""
import io
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln
sys.stderr = _e


def arm_lines(E):
    """The four lines the walk reads, every one live. -> {'b', 'r', 'M'}.

    `E` is the live r ladder keyed by timeframe in minutes, the same dict `v4_rcfg_sweep.load`
    returns. ws1b and the two Mage lines come straight off the tape.
    """
    return {'b': np.asarray(ln.line('ws1b'), float),
            'r': {int(t): np.asarray(v, float) for t, v in E.items()},
            'M': {t: np.asarray(ln.line('ws%dMage' % t), float) for t in (1, 2)}}


def mage(hi=12):
    """The Mage ladder ws1..ws{hi}, live. -> {tf: array}."""
    return {t: np.asarray(ln.line('ws%dMage' % t), float) for t in range(1, int(hi) + 1)}
