"""THE ~08:49 EPISODE, FULL RE-TEST. 09-25. 1007.

Joe 1007: *"ok I stand corrected on 08:11 - a proven non-example of the mech. walk to ~08:49 and
re-test"*.

The same battery the 08:11 and 11:21 episodes were put through:
  the return    ws1x crossing back above ws1r, wob 6 and wob 8 on the ABOVE-r run only
  the fence     ws1r <= momo_fence_r 17 at the return bar
  the dr        at the return bar
  Joe's line    ws1Mage against ws12Mage, section 3 of mage_cascade_findings 0918
  the shape     the ladder's peak TF, and whether r climbs while Mage falls (section 8, bumps >= 8)
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
RL = {t: C.R[t] for t in SC.TF}
EXF_LO = float(SC.LG['momo_fence_r'])
K = lambda t: SC.K('2026-09-25 %s' % t)

def episodes(a, b):
    below = (X1 < R1) & np.isfinite(X1) & np.isfinite(R1)
    out = []; j = a
    while j <= b:
        if not below[j]:
            j += 1; continue
        p0 = j
        while j <= N - 1 and below[j]:
            j += 1
        p1 = j - 1
        rb = j if j <= N - 1 else None
        run = 0
        if rb is not None:
            while rb + run <= N - 1 and not below[rb + run]:
                run += 1
        out.append((p0, p1, rb, run))
    return out

A, B = '08:44:00', '08:54:00'
print('# PIERCE / RETURN EPISODES, %s to %s' % (A, B))
eps = episodes(K(A), K(B))
box(('pierce from', 'to', 'pierce bars', 'return bar', 'above-r run', 'wob 6?', 'wob 8?',
     'ws1r at return', 'ws1r <= 17?', 'dr', 'conf at wob 6'),
    [(SC.U(p0), SC.U(p1), str(p1 - p0 + 1), SC.U(rb) if rb else '—', str(run),
      'Y' if run >= 6 else '-', 'Y' if run >= 8 else '-',
      '%.2f' % float(R1[rb]) if rb else '—',
      ('Y' if float(R1[rb]) <= EXF_LO else '-') if rb else '—',
      '%+d' % int(DRv[rb]) if rb else '—',
      SC.U(rb + 5) if (rb and run >= 6) else '—')
     for p0, p1, rb, run in eps] or [('—',) * 11])

VAL = [(rb, run) for p0, p1, rb, run in eps if rb and run >= 6]
print('\n# THE wob-6 VALIDATED RETURNS — JOE\'S ws1-vs-ws12 READ AND THE SHAPE')
rows = []
for rb, run in VAL:
    mv = [float(MG[t][rb]) for t in SC.TF]
    rv = [float(RL[t][rb]) for t in SC.TF]
    st = [mv[i] - mv[i - 1] for i in range(1, len(mv))]
    rows.append((SC.U(rb), str(run), 'Y' if run >= 8 else '-',
                 '%.2f' % float(R1[rb]), 'Y' if float(R1[rb]) <= EXF_LO else '-',
                 '%+d' % int(DRv[rb]),
                 '%.2f' % mv[0], '%.2f' % mv[-1], '%+.2f' % (mv[-1] - mv[0]),
                 'CLIMBS' if mv[-1] > mv[0] else 'FALLS',
                 'ws%d' % SC.TF[int(np.argmax(mv))], '%+.2f' % (max(mv) - mv[-1]),
                 '%d of %d' % (sum(1 for s in st if s > 0), len(st)),
                 '%+.2f' % (rv[-1] - rv[1]),
                 'r climbs, Mage falls' if (rv[-1] > rv[1] and mv[-1] < mv[0]) else
                 ('both climb' if (rv[-1] > rv[1] and mv[-1] > mv[0]) else 'other')))
box(('return bar', 'above-run', 'wob 8?', 'ws1r', '<= 17?', 'dr', 'ws1Mage', 'ws12Mage',
     'ws12 - ws1', "Joe's line", 'peak at', 'peak - ws12', 'rising steps', 'ws12r - ws2r',
     'the 0918 shape?'), rows or [('—',) * 15])

print('\n# THE THREE EPISODES SIDE BY SIDE, ON JOE\'S LINE')
REF = [('08:x  08:11:25', K('08:11:25')), ('11:x  11:19:05', K('11:19:05')),
       ('11:x  11:22:05', K('11:22:05'))]
ALL = [('08:49  %s' % SC.U(rb), rb) for rb, run in VAL] + REF
box(('bar', 'ws1Mage', 'ws12Mage', 'ws12 - ws1', "Joe's line", 'peak at', 'ws1r', '<= 17?'),
    [(lbl, '%.2f' % float(MG[1][k]), '%.2f' % float(MG[SC.TF[-1]][k]),
      '%+.2f' % (float(MG[SC.TF[-1]][k]) - float(MG[1][k])),
      'CLIMBS' if float(MG[SC.TF[-1]][k]) > float(MG[1][k]) else 'FALLS',
      'ws%d' % SC.TF[int(np.argmax([float(MG[t][k]) for t in SC.TF]))],
      '%.2f' % float(R1[k]), 'Y' if float(R1[k]) <= EXF_LO else '-') for lbl, k in ALL])

print('\n# THE FULL LADDERS AT THE ~08:49 VALIDATED RETURNS')
if VAL:
    box(('TF',) + tuple('%s Mage' % SC.U(rb) for rb, run in VAL)
        + tuple('%s r' % SC.U(rb) for rb, run in VAL),
        [('ws%d' % tf,) + tuple('%.1f' % float(MG[tf][rb]) for rb, run in VAL)
         + tuple('%.1f' % float(RL[tf][rb]) for rb, run in VAL) for tf in SC.TF])
