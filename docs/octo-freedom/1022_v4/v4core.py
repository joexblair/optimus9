"""`v4core` — STEP0, STEP1 and STEP2. The arm. Joe 1023.

HIS SPEC IS IN v4core.md, VERBATIM. This file implements the three steps that need no rulings I do
not have, and STOPS at STEP4. What STEP4 is missing is listed at the bottom of this docstring and
in v4core.md - the lineage walk's start TF, its anchor bar, and which r lines it reads are all
unspecified, and Joe's standing instruction is to stop at an unplanned decision rather than take
it.

THE LINES ARE THE CLOSED SET, SETTLED 1023. cws1b, cws1r, cws2r, cws3r, cws1Mage, cws2Mage - the
DB mech_lines('wsf') specs at value_mode 'closed'. Joe: *"db row"* and *"ws1b should be
mode:closed"*. His TV values matched closed to a 0.35 mean gap against emerging's 4.21, so these
are the lines he actually reads.

THE SIDE AT STEP0 IS SCANNED, NOT DERIVED FROM A TRADE. Joe 1023: *"scan both sides as you walk.
when the setup prints, the lines will all be on either high oob or low oob. if low oob, open a
LONG, if high oob, open a short"*. Two hypotheses, one per side; the first to complete sets it.

THE TWO MEANINGS OF `target-side`, and both are correct in place:
    STEP0            the side being SCANNED - there is no trade yet
    STEP1 / STEP2    the OPEN TRADE's target-side: high for a LONG, low for a SHORT
which makes STEP1/STEP2 the mirror of STEP0 - one setup shape, either side.

STEP1 IS A ONE-TIME GATE, NOT A HELD CONDITION, and that is MY structural read of his numbered
steps, stated rather than assumed: *"STEP1 on trade open, walk until ws1b is oob on target-side"*
is a walk that completes, and STEP2 then tests from there. cws1b is not re-checked at the arm bar.

STEP3 IS NOT HERE. His line is `STEP3: # disabled: pre-lineage test. ws1-3`.

CAUSAL. Every test reads the bar it fires on and no later bar. The closed lines carry their own
lag by construction - a closed value only changes when its own TF bar closes - and that lag is the
POINT, not a defect: it is what Joe reads on the chart.

STEP4'S THREE INPUTS, ALL RULED 1023. They were blanks in his spec and he filled them:
    the starting bar  *"the starting bar is the bar where v4core fires"* - the ARM bar, STEP2's.
    the starting TF   *"either cws2r or cws3r - whichever one triggered v4core. if they triggered
                      simultaeneously, defer to cws3r"*. So it is DYNAMIC per arm, not a constant,
                      which is why none of the fixed-TF readings measured on 1023 was his mech.
    the lines         *"the v4core lines (cws3r, cws2r, cws1r, cws2Mage, cws1Mage, cws1b) are all
                      mode:closed"*. The baton therefore STARTS on a closed line. What ws4r..ws12r
                      use as the ladder continues is NOT in that list and is still open - see
                      v4core.md.

usage: v4core.py <'start'> <'end'>
"""
import sys
import io
import os

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


def _line(role, tf):
    p = os.path.join(LINE_DIR,
                     _line_key(ln.EM, HOURS, WARMUP, override(tf * 60, ln.SPEC[role][0], MODE))
                     + '.npy')
    if not os.path.exists(p):
        raise SystemExit('MISSING closed array: ws%d%s' % (tf, role))
    return np.asarray(np.load(p, mmap_mode='r'), float)[:ln.N]


def lines():
    """-> the closed set v4core reads. B=cws1b, R={1,2,3}, M={1,2}."""
    return (_line('b', 1), {t: _line('r', t) for t in (1, 2, 3)},
            {t: _line('Mage', t) for t in (1, 2)})


def _mage_ok(M, k, side):
    """STEP0 and STEP2 share this: either Mage past the 5/95 fence on `side`."""
    return K.past_v4core_mage(M[1][k], side) or K.past_v4core_mage(M[2][k], side)


def step0(B1, R, M, A, Bn):
    """STEP0, both sides scanned. -> (the bar the setup prints, the side) or (None, None).

    Joe's order: *"walk until ws1b is oob on target-side, then walk to (ws2r oob AND ws3r oob) AND
    (ws1Mage or ws2Mage are same-side past 5/95)"*. So per side: cws1b oob FIRST, and only from
    that bar onward does the r+Mage test count. A FORWARD LOOP, which is his causal form - at each
    bar, ask what is true at that bar.
    """
    gate = {+1: None, -1: None}
    for k in range(int(A), int(Bn) + 1):
        for s in (+1, -1):
            if gate[s] is None:
                if K.oob(B1[k], s):
                    gate[s] = k
                continue
            if K.step0_r_ok(R[2][k], R[3][k], s) and _mage_ok(M, k, s):
                return k, s
    return None, None


def arm(B1, R, M, open_bar, target_side, Bn):
    """STEP1 then STEP2 from an open trade. -> (the arm bar, the cws1b gate bar) or (None, None).

    STEP1 walks to cws1b oob on the trade's target-side; STEP2 then needs (cws2r OR cws3r oob) AND
    a Mage past 5/95, both on that same side. STEP2's join is `or` in his spec and is not knobbed.
    """
    gate = None
    for k in range(int(open_bar), int(Bn) + 1):
        if gate is None:
            if K.oob(B1[k], target_side):
                gate = k
            continue
        if K.step2_r_ok(R[2][k], R[3][k], target_side) and _mage_ok(M, k, target_side):
            return k, gate
    return None, gate


def start_tf(R, k, side):
    """STEP4's starting timeframe: whichever of cws2r / cws3r triggered the arm. -> 2 or 3

    Joe 1023: *"the starting timeframe is either cws2r or cws3r - whichever one triggered v4core.
    if they triggered simultaeneously, defer to cws3r"*. So ws3 wins a tie, and this is read AT
    the arm bar - the same bar STEP2 fired on, so nothing later is read.
    """
    r3 = K.oob(R[3][k], side)
    if r3:
        return 3                      # his tie-break, and the sole trigger case
    assert K.oob(R[2][k], side), 'neither cws2r nor cws3r is oob at the arm bar'
    return 2


def target_side(direction):
    """A LONG hunts the HIGH oob, a SHORT the LOW. Banked, and set once at the trade's open."""
    assert direction in ('LONG', 'SHORT'), direction
    return +1 if direction == 'LONG' else -1
