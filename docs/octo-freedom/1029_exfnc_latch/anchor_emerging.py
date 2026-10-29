"""THE ANCHOR ON THE EMERGING ws5Mage, both firing-bar options. Joe 1029 chose arm B.

HIS RULING: the anchor is the ws5Mage EXTREMUM, read on the EMERGING line - *"B"* - because the
word only does work on a line that moves, and closed_prev holds one value per 5-min bucket.

THE CAUSALITY CONSTRAINT THAT COMES WITH IT, and it is not optional: at the firing bar the oob run
may still be open, so the extremum is only knowable over [run start, firing bar]. Taking it over
the whole run would read bars after the fire. Asserted below.

WHICH READ EACH ELEMENT USES, stated so it can be corrected:
    ws1b, the cross           closed_prev - the PREVIOUS completed bucket's close, causal
    ws5Mage oob gate          closed_prev
    the ANCHOR                EMERGING, his arm B
    the ws6..ws12 Mage test   read at the anchor bar on BOTH, printed side by side
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
from optimus9.analysis.jig import oob_ib_cross
sys.stderr = _e

A, B = ln.K('2026-08-29 23:00:00'), ln.K('2026-08-30 00:30:00')
BAND = list(range(6, int(K.L2_MOM_MAXTF) + 1))
LB_S = 300
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = CP.arm_lines(E)
B1 = np.asarray(CL['b'], float)
MGC = {t: np.asarray(CP.line('ws%dMage' % t, t * 60), float) for t in range(1, 13)}
MGE = {t: np.asarray(ln.line('ws%dMage' % t), float) for t in range(1, 13)}
W = max(1, int(K.LIN2_CROSS_WOB))
NEED = int(K.LIN2_CHAIN_OPEN_LINES)


def causal_anchor(side, fire):
    """The extremum of EMERGING ws5Mage over its oob run, up to `fire`. -> (bar, value) or None.

    The run is the contiguous oob stretch on `side` containing or immediately preceding `fire`.
    Only bars at or before `fire` are looked at - the run may still be open.
    """
    m = K.oob_mask(MGE[5], int(side))
    f = int(fire)
    j = f if m[f] else None
    if j is None:
        lo = f - LB_S // 5
        for i in range(f, max(0, lo) - 1, -1):
            if m[i]:
                j = i
                break
    if j is None:
        return None
    i = j
    while i > 0 and m[i - 1]:
        i -= 1
    seg = MGE[5][i:j + 1]
    k = i + (int(np.nanargmax(seg)) if side > 0 else int(np.nanargmin(seg)))
    assert k <= f, 'the anchor is after the firing bar - that read is lookahead'
    return (k, float(MGE[5][k]))


print('# THE ANCHOR ON THE EMERGING ws5Mage - his arm B')
print('# SPAN %s .. %s | RULED_OK %s' % (ln.U(A), ln.U(B), K.RULED_OK))
print('# ws1b and the oob gate are closed_prev (causal). The ANCHOR is EMERGING.')
print('# the anchor is the extremum over [run start, FIRING BAR] - never past it.')
print('')

crosses = []
for c, cf, sd in oob_ib_cross(B1, K.OOB_HI, K.OOB_LO, W):
    c, cf, sd = int(c), int(cf), int(sd)
    if A <= c <= B:
        crosses.append((c, cf, sd))

for fname, pick in (('the RAW cross bar', lambda c, cf: c),
                    ('the wob %d CONFIRM bar' % W, lambda c, cf: cf)):
    print('## firing on %s' % fname)
    print('')
    print('| the firing bar | candidate side | ws5Mage oob gate | the anchor bar |'
          ' ws5Mage at the anchor, EMERGING | lines away | required | FIRES? | the trade side |')
    print('|---|---|---|---|---|---|---|---|---|')
    for c, cf, sd in crosses:
        f = pick(c, cf)
        m = K.oob_mask(MGC[5], sd)
        lb = f - LB_S // 5
        gate = bool(m[f]) or bool(m[max(0, lb):f + 1].any())
        if not gate:
            print('| %s | %s | no | - | - | - | %d | no | - |'
                  % (ln.U(f), 'HIGH' if sd > 0 else 'LOW', NEED))
            continue
        an = causal_anchor(sd, f)
        if an is None:
            print('| %s | %s | YES | none on EMERGING | - | - | %d | no | - |'
                  % (ln.U(f), 'HIGH' if sd > 0 else 'LOW', NEED))
            continue
        k, v5 = an
        got = [t for t in BAND
               if np.isfinite(MGE[t][k])
               and ((float(MGE[t][k]) < v5) if sd > 0 else (float(MGE[t][k]) > v5))]
        ok = len(got) >= NEED
        print('| %s | %s | YES | %s | %.2f | %d - %s | %d | %s | %s |'
              % (ln.U(f), 'HIGH' if sd > 0 else 'LOW', ln.U(k), v5, len(got),
                 ','.join('ws%d' % t for t in got) if got else 'none', NEED,
                 'YES' if ok else 'no', ('SHORT' if sd > 0 else 'LONG') if ok else '-'))
    print('')

print('## the ladder at the anchor, EMERGING against closed_prev - the first firing cross only')
print('')
c, cf, sd = [x for x in crosses if x[0] == ln.K('2026-08-29 23:54:00')][0]
for fname, f in (('raw 23:54:00', c), ('confirm 23:54:55', cf)):
    an = causal_anchor(sd, f)
    k, v5 = an
    print('### firing %s, the anchor is %s' % (fname, ln.U(k)))
    print('')
    print('| the line | EMERGING at the anchor | closed_prev at the anchor |'
          ' away from HIGH on EMERGING? |')
    print('|---|---|---|---|')
    print('| ws5Mage | %.2f | %.2f | the anchor itself |' % (v5, float(MGC[5][k])))
    for t in BAND:
        print('| ws%dMage | %.2f | %.2f | %s |'
              % (t, float(MGE[t][k]), float(MGC[t][k]),
                 'YES' if float(MGE[t][k]) < v5 else 'no'))
    print('')

print('| the read | value |')
print('|---|---|')
print('| his prediction for the open | 2026-08-29 ~23:53 |')
print('| the open I had built on the ws5Mage oob entry | 2026-08-29 23:50:00 |')
