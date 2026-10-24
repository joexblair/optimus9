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


def _line(role, tf):
    p = os.path.join(LINE_DIR,
                     _line_key(ln.EM, HOURS, WARMUP, override(tf * 60, ln.SPEC[role][0], MODE))
                     + '.npy')
    if not os.path.exists(p):
        raise SystemExit('MISSING closed array: ws%d%s' % (tf, role))
    return np.asarray(np.load(p, mmap_mode='r'), float)[:ln.N]


def lines():
    """-> {'b': cws1b, 'r': {1,2,3}, 'M': {1,2}}. The six closed lines v4core reads."""
    return {'b': _line('b', 1),
            'r': {t: _line('r', t) for t in (1, 2, 3)},
            'M': {t: _line('Mage', t) for t in (1, 2)}}


def _mage_ok(CL, k, side):
    return (K.past_v4core_mage(CL['M'][1][k], side)
            or K.past_v4core_mage(CL['M'][2][k], side))


def arm(CL, open_bar, side, B):
    """STEP1 then STEP2 on `side`. -> (the arm bar, the cws1b gate bar) or (None, gate).

    STEP2's join is `or` in his spec and is NOT knobbed; STEP0's is `V4CORE_STEP0_JOIN`.
    """
    gate = None
    for k in range(int(open_bar), int(B) + 1):
        if gate is None:
            if K.oob(CL['b'][k], side):
                gate = k
            continue
        if K.step2_r_ok(CL['r'][2][k], CL['r'][3][k], side) and _mage_ok(CL, k, side):
            return k, gate
    return None, gate


def start_tf(CL, k, side):
    """STEP4's start TF: whichever of cws2r / cws3r triggered, ws3 on a tie. Read AT the arm bar.

    Joe 1023: *"the starting timeframe is either cws2r or cws3r - whichever one triggered v4core.
    if they triggered simultaeneously, defer to cws3r"*.
    """
    if K.oob(CL['r'][3][k], side):
        return 3
    assert K.oob(CL['r'][2][k], side), 'neither cws2r nor cws3r is oob at the arm bar'
    return 2
