"""v4nuggies' SIGNAL PRODUCER, and nothing else. Joe 1024 named it: *"mechname :v4nuggies"*.

ONE RESPONSIBILITY: state every v4nuggies signal on the tape. It reads no open position and the
router owns the fire bar, the direction and the pyramid test — same contract as the other three
producers.

HIS SPEC IS IN v4nuggies.md, verbatim, with every one of his 1024 answers beside the clause it
settles. Nothing is decided here.

THE SIDE IS cws1b's OOB SIDE. Joe 1024: *"everything is same side as the cws1b oob. mage cascade
is agnostic, it provides only a direction"*.

CAUSAL. The lift-off STAMP is the bar the trigger may act on — `K.lift_stamp(b)` = b + LIFT_WOB - 1,
his standing rule. The cascade is read at the cws1Mage EXTREMA bar, which is at or before that
stamp, so it reads a past bar. The gcws30Mage ib cross is acted on at its CONFIRM bar, the last
bar of the proven dwell. Every claim is an assert, not a comment.

NOTHING IS DEFAULTED. `ib_xwob` is a REQUIRED argument: the dwell on the gcws30Mage ib cross has no
banked value, and every other mech's is a Joe number (SAV_IB_XWOB 2, LIN_W4_G1_XWOB 4, SP_XWOB 18,
LIN_IB_DWELL scaled by TF). A default here would be me choosing his knob.
"""
import io
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
import v4_knobs as K
import v4_signal as SG
_e = sys.stderr; sys.stderr = io.StringIO()
import ln
from optimus9.analysis.jig import lift_off, mage_cascade
from optimus9.compute.line_config import override
from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
from optimus9.orchestration.rpl_cache import LINE_DIR, _line_key
sys.stderr = _e

#   *"-IF mage cascade's verdict ... is counter oob-side (ie low-oob, verdict:UP. high-oob,
#   verdict:DOWN)"* - his mapping, as a table rather than an if.
COUNTER = {-1: 'up', +1: 'down'}

STOP_TFS = tuple(range(2, 11))              # *"any ws{TF2 to TF10}r"* - Joe 1024
G30_TF_SECONDS = 30                         # *"g30Mage is shorthand for gcws30Mage"*
G30_MODE = 'closed'                         # *"it will need to be mode:closed"*


def g30():
    """The gcws30Mage closed array. -> ndarray.

    Built by `v4_build_closed.py` as an override on its own cache key; the indicator_configs row
    stays `emerging`, which is v4core's own precedent for its cws set.
    """
    p = os.path.join(LINE_DIR,
                     _line_key(ln.EM, HOURS, WARMUP,
                               override(G30_TF_SECONDS, ln.SPEC['Mage'][0], G30_MODE)) + '.npy')
    if not os.path.exists(p):
        raise SystemExit('MISSING gcws30Mage %s array - run v4_build_closed.py' % G30_MODE)
    return np.asarray(np.load(p, mmap_mode='r'), float)[:ln.N]


def _oob_run_start(line, b, side):
    """The first bar of the cws1Mage oob run that `b` belongs to. -> bar or None.

    *"cws1Mage's extrema over what span: -since cws1Mage went oob"*. `b` is the lift-off bar, which
    is the first bar the extreme stopped holding, so the run may already have ENDED by b. The walk
    back finds the most recent oob bar at or before b and then the start of its run.
    """
    j = int(b)
    while j >= 0 and not K.oob(line[j], side):
        j -= 1                                     # b may sit just after the run
    if j < 0:
        return None
    s = j
    while s - 1 >= 0 and K.oob(line[s - 1], side):
        s -= 1
    return s


def _extrema(line, frm, to, side):
    """The span's extreme and the bar it landed on. -> (value, bar).

    LOW side takes the min, HIGH the max - the extreme the line reached while it was oob.
    """
    seg = np.asarray(line[int(frm):int(to) + 1], float)
    i = int(np.nanargmin(seg)) if int(side) < 0 else int(np.nanargmax(seg))
    return float(seg[i]), int(frm) + i


def _ib_confirm(g, frm, B, xwob):
    """The first gcws30Mage ib cross at or after `frm` whose dwell is proven. -> bar or None.

    IB is the banked reading - strictly inside the oob fence, both sides, the same expression
    `v4_fast.ib_cross` uses. The CONFIRM bar is `the run's start + xwob - 1`, so a dwell whose last
    bar is past B is not confirmed on data we have and is not returned.
    """
    need = max(1, int(xwob))
    ib = (g > K.OOB_LO) & (g < K.OOB_HI)
    d = np.diff(np.r_[False, ib, False].astype(np.int8))
    s, e = np.flatnonzero(d == 1), np.flatnonzero(d == -1) - 1
    i = int(np.searchsorted(e, int(frm)))
    while i < len(s):
        k = max(int(s[i]), int(frm))
        c = k + need - 1
        if c <= int(e[i]) and c <= int(B):
            assert bool(ib[k:c + 1].all()), 'the gcws30Mage ib dwell is not in bounds end to end'
            return c
        i += 1
    return None


def produce(CL, R, MG, G, A, B, ib_xwob, trace=None):
    """Every v4nuggies signal in [A, B], both sides. -> list of signals, bar-ordered.

        CL       the closed c-set from v4_core_arm.lines() - 'b', 'r'{1..8}, 'M'{1,2}
        R        the EMERGING r lines, {tf: array}. ws2r..ws10r for the STOP test
        MG       {tf: the Mage line} for the cascade ladder
        G        the gcws30Mage closed array, from `g30()`
        ib_xwob  REQUIRED. The dwell the gcws30Mage ib cross must prove. No default - see §8
        trace    an optional list; every candidate appends one row with the stage it reached

    THE SIGNAL BAR IS THE gcws30Mage ib CONFIRM BAR, which is the bar his rev-trade clause becomes
    knowable on: the STOP test is read there too - *"the STOP is tested when s30Mage is ib"*.
    """
    assert int(ib_xwob) >= 1, 'the gcws30Mage ib dwell must be at least 1 bar'
    out = []
    for side in (-1, +1):
        M1 = np.asarray(CL['M'][1], float)
        for b in lift_off(M1, side, K.LIFT_PTS, K.gap_for(1), K.LIFT_TOL, K.LIFT_WOB):
            b = int(b)
            st = K.lift_stamp(b)
            if st < int(A) or st > int(B):
                continue
            row = {'side': side, 'lift': b, 'stamp': st, 'stage': 'lift-off'}

            rs = _oob_run_start(M1, b, side)
            if rs is None:
                row['stage'] = 'no cws1Mage oob run'
                _keep(trace, row); continue
            ex, exb = _extrema(M1, rs, b, side)
            row.update({'run_from': rs, 'extrema': ex, 'extrema_bar': exb})
            if not K.past_v4core_mage(ex, side):
                row['stage'] = 'the extrema is not ex 5/95'
                _keep(trace, row); continue

            if not K.oob(CL['b'][st], side):
                row['stage'] = 'cws1b not oob at the stamp'
                _keep(trace, row); continue
            row['cws1b'] = float(CL['b'][st])
            if not K.ex_fence(CL['r'][1][st], side):
                row['stage'] = 'cws1r not ex-fence at the stamp'
                _keep(trace, row); continue
            row['cws1r'] = float(CL['r'][1][st])

            assert exb <= st, 'the cascade anchor is past the bar it is read on'
            c = mage_cascade(MG, exb, zoom=K.SAV_CASCADE_ZOOM, min_lines=K.SAV_CASCADE_MIN)
            row['verdict'] = None if c is None else c['verdict']
            if row['verdict'] != COUNTER[side]:
                row['stage'] = 'the cascade verdict is not counter'
                _keep(trace, row); continue

            ib = _ib_confirm(G, st, B, ib_xwob)
            if ib is None:
                row['stage'] = 'no gcws30Mage ib cross'
                _keep(trace, row); continue
            assert ib >= st, 'the gcws30Mage ib confirm precedes the trigger stamp'
            row['ib'] = ib

            hit = [t for t in STOP_TFS if t in R and K.oob(R[t][ib], side)]
            if hit:
                row['stage'] = 'STOP - ws%s same-side oob' % ','.join(str(t) for t in hit)
                _keep(trace, row); continue

            row['stage'] = 'rev-trade'
            _keep(trace, row)
            out.append(SG.signal(ib, side, 'nuggies', st,
                                 'lift %s, extrema %.2f at %s, ib %s'
                                 % (SG.why_time(st), ex, SG.why_time(exb), SG.why_time(ib))))
    out.sort(key=lambda z: (z['bar'], z['side']))
    return out


def _keep(trace, row):
    if trace is not None:
        trace.append(row)
