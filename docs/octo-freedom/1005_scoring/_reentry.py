"""THE STOP OVERSHOOT, AND THE TWO RE-ENTRIES COMPARED. 09-25. 1007.

Joe 1007: *"how did 14 print mae1.1 yet the realised is -1.222?"* and *"do you see the ~same
pattern in both re-entries? you might need to walk back or forth a few bars to get a result"*.

THE RE-ENTRY PATTERN is Joe's, from the spec he shared at 08:10: *"ws1r is low oob reversing and
there is an upward Mage cascade"*. Component 1 is measurable from the lines. Component 2 has NO
RULED PRODUCER - task #22 is parked - so the Mage ladder is PRINTED and its rising-step count is a
DESCRIPTION, not a test.
"""
import sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
SC, PX, box = C.SC, C.PX, C.box
R, M2 = C.R, C.M2
MG = {t: SC.Mg[t][:len(SC.ts)] for t in SC.TF}
K = lambda t: SC.K('2026-09-25 %s' % t)

print('# THE STOP OVERSHOOT — the bar before the breach, and the breach bar')
rows = []
for lbl, op, side, xk in (('leg 11', '10:56:40', -1, '11:07:45'),
                          ('leg 14', '12:27:05', +1, '13:22:35')):
    k0, kb = K(op), K(xk)
    p0 = float(PX[k0])
    adv = lambda k: -((float(PX[k]) - p0) / p0 * 100.0 * side)
    rows.append((lbl, op, SC.U(kb - 1), '%.4f' % adv(kb - 1), SC.U(kb), '%.4f' % adv(kb),
                 '%.4f' % (adv(kb) - adv(kb - 1)), '%.4f' % (adv(kb) - 1.1),
                 '%.6f' % float(PX[kb - 1]), '%.6f' % float(PX[kb])))
box(('leg', 'open', 'last bar under 1.1', 'its adverse', 'breach bar', 'its adverse',
     'one-bar jump', 'overshoot past 1.1', 'pxs before', 'pxs at breach'), rows)
print('- the stop is a PER-BAR test: the first bar whose adverse exceeds 1.1000 is the exit, so the')
print('  realised is that bar\'s adverse, not 1.1000. The overshoot is one bar of price movement.')

def ws1r_low(k, back=720):
    """The most recent bar at or before k where ws1r was low oob, and ws1r's min since."""
    for j in range(k, max(0, k - back) - 1, -1):
        if float(R[1][j]) <= SC.LO:
            seg = R[1][j:k + 1]
            return j, float(np.nanmin(seg))
    return None, None

def ladder(k):
    v = [float(MG[t][k]) for t in SC.TF]
    steps = [v[i] - v[i - 1] for i in range(1, len(v))]
    return v, sum(1 for s in steps if s > 0), len(steps)

print('\n# THE TWO RE-ENTRY BARS, SIDE BY SIDE')
rows = []
for lbl, ts in (('08:10:00 — Joe\'s first', '08:10:00'), ('11:21:00 — Joe\'s second', '11:21:00')):
    k = K(ts)
    lo_bar, lo_min = ws1r_low(k)
    v, up, n = ladder(k)
    rows.append((lbl, '%.2f' % float(R[1][k]),
                 SC.U(lo_bar) if lo_bar else 'none in 60 min',
                 '%.2f' % lo_min if lo_min is not None else '—',
                 '%.2f' % (float(R[1][k]) - lo_min) if lo_min is not None else '—',
                 '%d of %d' % (up, n), '%.2f' % v[0], '%.2f' % max(v),
                 'ws%d' % SC.TF[int(np.argmax(v))], '%.2f' % float(M2[k]),
                 '%.6f' % float(PX[k])))
box(('re-entry bar', 'ws1r', 'last ws1r low-oob bar', 'ws1r min since', 'ws1r risen by',
     'rising Mage steps', 'ws1Mage', 'ladder max', 'at', 'ws2Mage', 'pxs'), rows)

print('\n# THE MAGE LADDER AT BOTH BARS')
box(('TF', 'Mage at 08:10:00', 'step', 'Mage at 11:21:00', 'step'),
    [('ws%d' % t,
      '%.2f' % float(MG[t][K('08:10:00')]),
      '—' if i == 0 else '%+.2f' % (float(MG[t][K('08:10:00')]) - float(MG[SC.TF[i-1]][K('08:10:00')])),
      '%.2f' % float(MG[t][K('11:21:00')]),
      '—' if i == 0 else '%+.2f' % (float(MG[t][K('11:21:00')]) - float(MG[SC.TF[i-1]][K('11:21:00')])))
     for i, t in enumerate(SC.TF)])

print('\n# WALKING 11:21 — ws1r AND THE LADDER EVERY 30 s FROM 11:12 TO 11:30')
a, b = K('11:12:00'), K('11:30:00')
rows = []
for k in range(a, b + 1, 6):
    lo_bar, lo_min = ws1r_low(k)
    v, up, n = ladder(k)
    rows.append((SC.U(k), '%.2f' % float(R[1][k]),
                 'Y' if float(R[1][k]) <= SC.LO else '-',
                 '%.2f' % lo_min if lo_min is not None else '—',
                 '%d of %d' % (up, n), '%.2f' % v[0], '%.2f' % float(M2[k]),
                 '%.6f' % float(PX[k])))
box(('ts', 'ws1r', 'low oob?', 'ws1r min in 60 min', 'rising Mage steps', 'ws1Mage', 'ws2Mage',
     'pxs'), rows)
print('\n- rising Mage steps counts how many of the 11 ws1->ws12 steps are positive at that bar.')
print('  DESCRIPTIVE. Joe\'s "upward Mage cascade" has no ruled producer (task #22, parked).')
