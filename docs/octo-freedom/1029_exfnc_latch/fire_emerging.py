"""HIS ws1b FIRING MECH WITH EVERY READ ON EMERGING, against the closed_prev version.

Joe 1029: *"bank this and make it the machine"* and, in the same message, *"closed_prev is also not
an option"*. The mech I measured read ws1b and the ws5Mage oob gate on closed_prev, so banking it
means re-measuring it with those on emerging too. Both are printed side by side.

EVERY READ, stated:
    ws1b, the oob->ib cross   EMERGING   ln.line('ws1b')
    the ws5Mage oob gate      EMERGING   ln.line('ws5Mage')
    the anchor extremum       EMERGING   his arm B
    the ws6..ws12 Mage test   EMERGING, at the anchor bar

THE ANCHOR IS CAUSAL: the extremum is taken over [run start, FIRING BAR] only. The run may still be
open at the fire, so reading past it would be lookahead. Asserted.
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
NEED = int(K.LIN2_CHAIN_OPEN_LINES)
W = max(1, int(K.LIN2_CROSS_WOB))

E = RS.load((RS.K0, RS.R0, RS.S0))
B1E = np.asarray(ln.line('ws1b'), float)                                   # EMERGING
B1C = np.asarray(CP.arm_lines(E)['b'], float)                              # closed_prev
MGE = {t: np.asarray(ln.line('ws%dMage' % t), float) for t in range(1, 13)}
MGC = {t: np.asarray(CP.line('ws%dMage' % t, t * 60), float) for t in range(1, 13)}


def anchor(M5, side, fire):
    """The extremum of M5 over its oob run, up to `fire`. -> (bar, value) or None. CAUSAL."""
    m = K.oob_mask(M5, int(side))
    f = int(fire)
    j = f if m[f] else None
    if j is None:
        for i in range(f, max(0, f - LB_S // 5) - 1, -1):
            if m[i]:
                j = i
                break
    if j is None:
        return None
    i = j
    while i > 0 and m[i - 1]:
        i -= 1
    seg = M5[i:j + 1]
    k = i + (int(np.nanargmax(seg)) if side > 0 else int(np.nanargmin(seg)))
    assert k <= f, 'the anchor is after the firing bar - that read is lookahead'
    return (k, float(M5[k]))


def fires(B1, M, label, wob):
    rows = []
    for c, cf, sd in oob_ib_cross(B1, K.OOB_HI, K.OOB_LO, wob):
        c, cf, sd = int(c), int(cf), int(sd)
        if not (A <= c <= B):
            continue
        f = cf if wob > 1 else c
        m = K.oob_mask(M[5], sd)
        gate = bool(m[f]) or bool(m[max(0, f - LB_S // 5):f + 1].any())
        an = anchor(M[5], sd, f) if gate else None
        got = []
        if an is not None:
            k, v5 = an
            got = [t for t in BAND
                   if np.isfinite(M[t][k])
                   and ((float(M[t][k]) < v5) if sd > 0 else (float(M[t][k]) > v5))]
        rows.append(dict(raw=c, conf=cf, fire=f, sd=sd, gate=gate, an=an, got=got,
                         ok=bool(an is not None and len(got) >= NEED), lab=label))
    return rows


print('# HIS ws1b FIRING MECH - EVERY READ ON EMERGING, against the closed_prev version')
print('# SPAN %s .. %s | RULED_OK %s' % (ln.U(A), ln.U(B), K.RULED_OK))
print('# the band is ws6..ws%d. required lines %d. the oob lookback is %d s.'
      % (K.L2_MOM_MAXTF, NEED, LB_S))
print('# the anchor extremum is taken over [run start, FIRING BAR] - never past it.')
print('')

ARMS = [('EMERGING, raw cross', B1E, MGE, 1),
        ('EMERGING, wob %d confirm' % W, B1E, MGE, W),
        ('closed_prev, raw cross', B1C, MGC, 1),
        ('closed_prev, wob %d confirm' % W, B1C, MGC, W)]

print('## every ws1b oob->ib cross, per arm')
print('')
print('| arm | the raw cross | the firing bar | candidate side | ws5Mage oob gate | the anchor bar |'
      ' ws5Mage at the anchor | lines away | FIRES? | side |')
print('|---|---|---|---|---|---|---|---|---|---|')
ALL = {}
for lab, B1, M, wob in ARMS:
    rs = fires(B1, M, lab, wob)
    ALL[lab] = rs
    for r in rs:
        an = r['an']
        print('| %s | %s | %s | %s | %s | %s | %s | %d - %s | %s | %s |'
              % (lab, ln.U(r['raw']), ln.U(r['fire']), 'HIGH' if r['sd'] > 0 else 'LOW',
                 'YES' if r['gate'] else 'no',
                 ln.U(an[0]) if an else '-', '%.2f' % an[1] if an else '-',
                 len(r['got']), ','.join('ws%d' % t for t in r['got']) if r['got'] else 'none',
                 'YES' if r['ok'] else 'no',
                 ('SHORT' if r['sd'] > 0 else 'LONG') if r['ok'] else '-'))
print('')

print('## the FIRST firing cross per arm - the chain open')
print('')
print('| arm | the open bar | the trade side | the anchor bar | ws5Mage at the anchor |'
      ' lines away | gap from his 23:53 |')
print('|---|---|---|---|---|---|---|')
H = ln.K('2026-08-29 23:53:00')
for lab, _b, _m, _w in ARMS:
    hit = [r for r in ALL[lab] if r['ok']]
    if not hit:
        print('| %s | none in the span | - | - | - | - | - |' % lab)
        continue
    r = hit[0]
    print('| %s | %s | %s | %s | %.2f | %d of %d | %+.1f min |'
          % (lab, ln.U(r['fire']), 'SHORT' if r['sd'] > 0 else 'LONG', ln.U(r['an'][0]),
             r['an'][1], len(r['got']), len(BAND), (r['fire'] - H) * 5 / 60.0))
print('')

print('## the ws6..ws%d Mage ladder at the EMERGING anchor, raw-cross arm' % K.L2_MOM_MAXTF)
print('')
hit = [r for r in ALL['EMERGING, raw cross'] if r['ok']]
if hit:
    r = hit[0]
    k, v5 = r['an']
    print('| the line | EMERGING at the anchor | away from the %s candidate side? |'
          % ('HIGH' if r['sd'] > 0 else 'LOW'))
    print('|---|---|---|')
    print('| ws5Mage | %.2f | the anchor itself |' % v5)
    for t in BAND:
        v = float(MGE[t][k])
        print('| ws%dMage | %.2f | %s |' % (t, v, 'YES' if ((v < v5) if r['sd'] > 0 else (v > v5))
                                            else 'no'))
print('')
print('| the read | value |')
print('|---|---|')
print('| his prediction | 2026-08-29 ~23:53, a SHORT |')
print('| the ws5Mage-oob-entry open I built first | 2026-08-29 23:50:00 |')
