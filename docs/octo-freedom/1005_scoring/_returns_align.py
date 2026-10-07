"""THE FIVE wob-6 VALIDATED RETURN BARS, SIDE BY SIDE. 09-25. 1007.

Joe 1007: *"the pierces aren't important to the mech"* / *"aside from the pierces, where do see
disparity that would prevent us from claiming that both 08:x and 11.x are aligned?"*

Measured ONLY on the lines the mech already uses: ws1r, ws1x, dr, ws1Mage, ws2Mage, and the Mage
ladder. The ladder's rising-step count is DESCRIPTIVE - the cascade test has no ruled producer.
"""
import sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
SC, PX, box = C.SC, C.PX, C.box
R1, X1, M2 = C.R[1], C.X[1], C.M2
N = len(SC.ts)
DRv = (SC.DR if hasattr(SC, 'DR') else SC.DRv)[:N]
G1 = SC.MTD['ws1'][:N]
MG = {t: SC.Mg[t][:N] for t in SC.TF}
EXF_LO = float(SC.LG['momo_fence_r'])
K = lambda t: SC.K('2026-09-25 %s' % t)

RET = [('08:x', '08:08:05', 6), ('08:x', '08:08:45', 21), ('08:x', '08:11:25', 139),
       ('11:x', '11:19:05', 7), ('11:x', '11:22:05', 64)]

def ladder(k):
    v = [float(MG[t][k]) for t in SC.TF]
    st = [v[i] - v[i - 1] for i in range(1, len(v))]
    return v, sum(1 for s in st if s > 0), len(st)

print('# THE FIVE wob-6 VALIDATED RETURN BARS')
rows = []
for ep, ts, run in RET:
    k = K(ts)
    v, up, n = ladder(k)
    rows.append((ep, ts, str(run), 'Y' if run >= 8 else '-',
                 '%.2f' % float(R1[k]), 'Y' if float(R1[k]) <= EXF_LO else '-',
                 '%.2f' % float(X1[k]), '%+d' % int(DRv[k]),
                 '%.2f' % float(G1[k]), '%.2f' % float(M2[k]),
                 '%d of %d' % (up, n), '%.2f' % max(v), 'ws%d' % SC.TF[int(np.argmax(v))],
                 '%.6f' % float(PX[k])))
box(('episode', 'return bar', 'above-run bars', 'wob 8?', 'ws1r', 'ws1r <= 17?', 'ws1x', 'dr',
     'ws1Mage', 'ws2Mage', 'rising Mage steps', 'ladder max', 'at', 'pxs'), rows)

print('\n# THE SPREAD WITHIN EACH EPISODE, AND BETWEEN THEM')
def span(vals):
    return '%.2f to %.2f' % (min(vals), max(vals))
rows = []
for lbl, fn in (('ws1r', lambda k: float(R1[k])),
                ('ws1x', lambda k: float(X1[k])),
                ('ws1Mage', lambda k: float(G1[k])),
                ('ws2Mage', lambda k: float(M2[k])),
                ('rising Mage steps', lambda k: float(ladder(k)[1])),
                ('ladder max', lambda k: max(ladder(k)[0])),
                ('ladder max TF', lambda k: float(SC.TF[int(np.argmax(ladder(k)[0]))]))):
    a = [fn(K(t)) for e, t, r in RET if e == '08:x']
    b = [fn(K(t)) for e, t, r in RET if e == '11:x']
    rows.append((lbl, span(a), span(b),
                 '%+.2f' % (sum(b) / len(b) - sum(a) / len(a)),
                 'OVERLAP' if (min(a) <= max(b) and min(b) <= max(a)) else 'DISJOINT'))
box(('what', '08:x range (3 bars)', '11:x range (2 bars)', '11:x mean - 08:x mean',
     'do the ranges overlap?'), rows)

print('\n# THE MAGE LADDER AT ALL FIVE RETURN BARS')
box(('TF',) + tuple('%s %s' % (e, t) for e, t, r in RET),
    [('ws%d' % tf,) + tuple('%.2f' % float(MG[tf][K(t)]) for e, t, r in RET) for tf in SC.TF])
