"""v4core's arm on the CLOSED c-lines. SRP: STEP1, STEP2 and the lineage start TF. Nothing else.

SPLIT OUT OF v4core.py 1023 so the stitched machine imports the arm without importing a __main__.
The rules are Joe's and they are banked in v4core.md; nothing new is decided here.

THE LINES ARE THE CLOSED c-SET, all six. Joe 1023: *"db row"* for the r and Mage specs, then
*"ws1b should be mode:closed"*. These are what he reads on TV - measured 0.35 mean gap against
emerging's 4.21 across the twelve values he quoted.

STEP1 IS A ONE-TIME GATE, not a held condition: *"on trade open, walk until ws1b is oob on
target-side"* is a walk that completes, and STEP2 then tests from there.

CAUSAL. A forward loop; each test reads only the bar it fires on.
"""
import io
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
import ln
import v4_knobs as K
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.compute.line_config import override
from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
from optimus9.orchestration.rpl_cache import LINE_DIR, _line_key
sys.stderr = _e

MODE = 'closed'
ARM2_TFS = (4, 5, 6, 7, 8)                  # *"any TWO of ws4-8r are same-side oob"* - Joe 1024


def _line(role, tf):
    p = os.path.join(LINE_DIR,
                     _line_key(ln.EM, HOURS, WARMUP, override(tf * 60, ln.SPEC[role][0], MODE))
                     + '.npy')
    if not os.path.exists(p):
        raise SystemExit('MISSING closed array: ws%d%s' % (tf, role))
    return np.asarray(np.load(p, mmap_mode='r'), float)[:ln.N]


def lines():
    """-> {'b': cws1b, 'r': {1..8}, 'M': {1,2}}. The closed lines v4core reads.

    cws4r..cws8r joined the set for the SECOND ARM, Joe 1024 - *"any TWO of ws4-8r are same-side
    oob"*. STEP2 still reads only cws2r and cws3r.
    """
    return {'b': _line('b', 1),
            'r': {t: _line('r', t) for t in (1, 2, 3) + ARM2_TFS},
            'M': {t: _line('Mage', t) for t in (1, 2)}}


def mage_ladder(hi):
    """{tf: the CLOSED cws{tf}Mage array} for tf 1..hi. -> dict.

    Joe 1024: *"create cws{TF3-10}Mage lines and set them all to mode: closed"*. All eleven were
    already in the cache on their own spec keys; `v4_build_closed.py` declares the set and prints
    the step rates that prove the mode. The ladder's top rung is the CALLER'S, because he asked for
    two of them - cws1 to cws10, and cws1 to cws5.
    """
    return {t: _line('Mage', t) for t in range(1, int(hi) + 1)}


def _mage_ok(CL, k, side):
    return (K.past_v4core_mage(CL['M'][1][k], side)
            or K.past_v4core_mage(CL['M'][2][k], side))


def arm2_ok(CL, k, side):
    """v4core's SECOND ARM at bar k. -> bool. Joe 1024, his words:

        if ws1r is oob on target side, min dwell 18 bars, and ws1Mage is same-side oob, and any
        TWO of ws4-8r are same-side oob, arm.

    THE DWELL IS THE ws1r OOB RUN'S OWN LENGTH, so the earliest arm is the 18th bar of the run -
    which is what his 2026-09-01 03:34:00 and 13:49:00 examples are, both landing on bar 18 of
    their run. ARM2_DWELL is his number.

    STEP2'S SIBLING, not its replacement - *"is it STEP2's sibling - yes"*. Either arm may fire and
    `arm` takes whichever lands first.

    EVERY LINE IS A CLOSED c-LINE. Joe 1024: *"everything is measured on closed bars"*, after his
    first reading of the four examples was taken off the emerging lines. cws1Mage is the clause
    that moves: at his 06:24 example cws1Mage is -5.60 and LOW oob while the emerging ws1Mage is
    23.33 and not.
    """
    if not K.oob(CL['r'][1][k], side):
        return False
    n = 0                                              # the ws1r oob run's length, ending at k
    while k - n >= 0 and K.oob(CL['r'][1][k - n], side):
        n += 1
        if n >= K.ARM2_DWELL:
            break
    if n < K.ARM2_DWELL:
        return False
    if not K.oob(CL['M'][1][k], side):
        return False
    return sum(1 for t in ARM2_TFS if K.oob(CL['r'][t][k], side)) >= K.ARM2_POOL_MIN


def armed_at(CL, k, side):
    """WHICH arm fires at bar k, ignoring the gate. -> 'step2', 'arm2' or None.

    SPLIT OUT 1024 so the CONDITION and the SEARCH are separate things. `arm` is a forward search
    and a signal producer needs the predicate: without it, collapsing a run of qualifying bars into
    one arm means guessing a bar gap, and the closed c-lines step every ~10 bars so an
    adjacent-bar test silently reports one arm as dozens.
    """
    if K.step2_r_ok(CL['r'][2][k], CL['r'][3][k], side) and _mage_ok(CL, k, side):
        return 'step2'
    if K.ARM2 and arm2_ok(CL, k, side):
        return 'arm2'
    return None


def gate_at(CL, k, side, frm=0):
    """The most recent cws1b oob bar at or before k, on `side`. -> bar or None.

    STEP1's gate, read backwards. Joe 1024: *"the gate must be at or before the arm bar - yes"*.
    A forward search finds the gate then the arm; a tape scan has the arm and needs its gate.
    """
    for j in range(int(k), int(frm) - 1, -1):
        if K.oob(CL['b'][j], side):
            return j
    return None


def arm(CL, open_bar, side, B):
    """STEP1's gate, then EITHER arm on `side`. -> (the arm bar, the gate bar, which) or (None, gate, None).

    THE GATE IS AT OR BEFORE THE ARM BAR, Joe 1024: *"yes. apply this to the existing mech as
    well"*. It used to `continue` past the gate bar without testing an arm there, so the gate bar
    could never also be the arm bar and every arm was at least one bar late. On 09-01 all five
    second-arm candidates have cws1b oob ON the arm bar itself, which is how he found it.

    STEP2's join is `or` in his spec and is NOT knobbed; STEP0's is `V4CORE_STEP0_JOIN`.
    `which` names the sibling that fired - 'step2' or 'arm2' - because the lineage START TF differs
    between them: STEP2 uses cws2r/cws3r, arm2 starts at ws1 on his 1024 ruling.
    """
    gate = None
    for k in range(int(open_bar), int(B) + 1):
        if gate is None and K.oob(CL['b'][k], side):
            gate = k                                   # the SAME bar may arm - 1024
        if gate is None:
            continue
        w = armed_at(CL, k, side)
        if w is not None:
            return k, gate, w
    return None, gate, None


def start_tf(CL, k, side):
    """STEP4's start TF: whichever of cws2r / cws3r triggered, ws3 on a tie. Read AT the arm bar.

    Joe 1023: *"the starting timeframe is either cws2r or cws3r - whichever one triggered v4core.
    if they triggered simultaeneously, defer to cws3r"*.
    """
    if K.oob(CL['r'][3][k], side):
        return 3
    assert K.oob(CL['r'][2][k], side), 'neither cws2r nor cws3r is oob at the arm bar'
    return 2
