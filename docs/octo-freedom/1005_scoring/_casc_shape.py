"""THE 0918 CASCADE SHAPE FINDING, APPLIED TO THE TWO RE-ENTRY EPISODES. 1007.

docs/mage_cascade_findings.md section 8 (the mean ladder):
  *"bumps >= 8 is not a rough cascade. It is a ladder that turns over at ws4 - the mid-board...
    bumps <= 7 is the clean monotone procession with no turn. At bumps >= 8 the r ladder is the one
    cascading (27.9 -> 59.8) while the Mage ladder humps. At bumps <= 7 r is nearly flat."*

Joe's own read, section 3, verbatim 0918:
  *"the first thing I look at is the lowest TF's value, and the highest TF's value (~90 to ~73). I
    can draw a mental downward line between those 2 numbers, making allowances for the bumps. then
    I check for ws1 to be oob."*

So: ws1 vs ws12 on Mage, the turn point, and whether r cascades while Mage humps.
Printed, not scored - the 0918 bump gate REVERSED out of sample and is not being rebuilt here.
"""
import sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
SC, PX, box = C.SC, C.PX, C.box
N = len(SC.ts)
MG = {t: SC.Mg[t][:N] for t in SC.TF}
RL = {t: C.R[t] for t in SC.TF}
K = lambda t: SC.K('2026-09-25 %s' % t)
RET = [('08:x', '08:08:05'), ('08:x', '08:08:45'), ('08:x', '08:11:25'),
       ('11:x', '11:19:05'), ('11:x', '11:22:05')]

print('# JOE\'S ws1-vs-ws12 READ ON Mage, AT THE FIVE RETURN BARS')
rows = []
for ep, ts in RET:
    k = K(ts)
    v = [float(MG[t][k]) for t in SC.TF]
    turn = SC.TF[int(np.argmax(v))]
    rows.append((ep, ts, '%.2f' % v[0], '%.2f' % v[-1], '%+.2f' % (v[-1] - v[0]),
                 'CLIMBS away from the low' if v[-1] > v[0] else 'FALLS away from the low',
                 'ws%d' % turn, '%.2f' % max(v),
                 '%+.2f' % (max(v) - v[-1])))
box(('episode', 'return bar', 'ws1Mage', 'ws12Mage', 'ws12 - ws1', "Joe's line",
     'ladder peak at', 'peak value', 'peak - ws12'), rows)

print('\n# THE r LADDER AT THE SAME BARS — does r cascade while Mage humps?')
rows = []
for ep, ts in RET:
    k = K(ts)
    rv = [float(RL[t][k]) for t in SC.TF]
    mv = [float(MG[t][k]) for t in SC.TF]
    rows.append((ep, ts, '%.2f' % rv[1], '%.2f' % rv[-1], '%+.2f' % (rv[-1] - rv[1]),
                 '%.2f' % mv[0], '%.2f' % mv[-1], '%+.2f' % (mv[-1] - mv[0]),
                 'r climbs, Mage falls' if (rv[-1] > rv[1] and mv[-1] < mv[0]) else
                 ('both climb' if (rv[-1] > rv[1] and mv[-1] > mv[0]) else 'other')))
box(('episode', 'return bar', 'ws2r', 'ws12r', 'ws12r - ws2r', 'ws1Mage', 'ws12Mage',
     'ws12M - ws1M', 'the 0918 shape?'), rows)

print('\n# BOTH LADDERS IN FULL, ws2r ONWARD (ws1r ignored per Joe 0918)')
box(('TF',) + tuple('%s M' % t for e, t in RET) + tuple('%s r' % t for e, t in RET),
    [('ws%d' % tf,) + tuple('%.1f' % float(MG[tf][K(t)]) for e, t in RET)
     + tuple('%.1f' % float(RL[tf][K(t)]) for e, t in RET) for tf in SC.TF])
