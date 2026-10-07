"""Leg 10 held past 10:56:40 — where does the momentum above it actually end? Joe 1007:
*"there is more momentum above 10:56, and I wonder if we capture it in one trade"*.

THREE EXIT VARIANTS on the SAME leg (LONG, open 10:17:05), using _chain10's own producers:
  as built      x-cross or final stalled, whichever first  -> 10:56:40
  stall only    the x-cross DISABLED; the rider's stall is the only exit
  neither       no exit at all, to show where the move actually ended

Nothing is chosen here. The x-cross is Joe's ruled exit; this measures what it left behind.
"""
import sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
SC, PX, box = C.SC, C.PX, C.box
R, X, M2, ST, ALL_TF = C.R, C.X, C.M2, C.ST, C.ALL_TF
LIN_HOP, BASE_HI, CEIL_HI, TRIG = C.LIN_HOP, C.BASE_HI, C.CEIL_HI, C.TRIG_TF
oobf, xcond, bnd = C.oobf, C.xcond, C.bnd
K = lambda t: SC.K('2026-09-25 %s' % t)
k0, d = K('10:17:05'), +1
p0 = float(PX[k0])
pct = lambda k: (float(PX[k]) - p0) / p0 * 100.0 * d
mn = lambda k: (int(SC.ts[k]) - int(SC.ts[k0])) / 60000.0

def walk(use_x, last):
    tr = []; armed = False; rider = None; ceil = BASE_HI
    for j in range(k0 + 1, last + 1):
        if ceil == BASE_HI and oobf(TRIG, j, d) and not oobf(TRIG, j - 1, d):
            ceil = CEIL_HI; tr.append((j, 'CEILING ws%d -> ws%d' % (BASE_HI, CEIL_HI)))
        if not armed:
            if float(M2[j]) >= SC.HI and float(M2[j - 1]) < SC.HI:
                armed = True
                tr.append((j, 'exit-armed — ws2Mage over 85 (%.2f)' % float(M2[j])))
            else:
                continue
        if rider is None:
            c = [t for t in ALL_TF if t <= ceil and oobf(t, j, d)]
            if c:
                rider = max(c)
                tr.append((j, 'KICKSTART — rider ws%d (r %.2f)' % (rider, float(R[rider][j]))))
            continue
        cand = [t for t in range(rider + 1, min(rider + LIN_HOP, ceil) + 1) if oobf(t, j, d)]
        if cand:
            rider = max(cand)
            tr.append((j, 'baton -> ws%d oob (r %.2f)' % (rider, float(R[rider][j])))); continue
        if ST[(rider, d)][j]:
            tr.append((j, 'final stalled on ws%d (r %.2f %s)'
                       % (rider, float(R[rider][j]), bnd(rider, j, d))))
            return j, 'final stalled', tr
        if use_x and xcond(rider, j, d):
            tr.append((j, 'x-cross on ws%d' % rider))
            return j, 'x-cross', tr
    return None, 'no exit in the window', tr

last = K('13:30:00')
print('# LEG 10, LONG, open 10:17:05 pxs %.6f — THREE EXIT VARIANTS' % p0)
rows = []
for lbl, ux in (('as built (x-cross or stall)', True), ('stall only, x-cross DISABLED', False)):
    xk, why, tr = walk(ux, last)
    rows.append((lbl, SC.U(xk) if xk else '—', why,
                 '%.1f' % mn(xk) if xk else '—', '%+.4f' % pct(xk) if xk else '—'))
box(('variant', 'exit', 'why', 'hold min', 'realised'), rows)

print('\n# THE STALL-ONLY WALK, EVERY EVENT')
xk, why, tr = walk(False, last)
box(('ts', '+min', 'event', 'pxs', 'pct'),
    [(SC.U(k0), '+0.0', 'OPEN LONG', '%.6f' % p0, '+0.0000')]
    + [(SC.U(j), '%+.1f' % mn(j), lbl, '%.6f' % float(PX[j]), '%+.4f' % pct(j))
       for j, lbl in tr]
    + ([(SC.U(xk), '%+.1f' % mn(xk), 'EXIT — %s' % why, '%.6f' % float(PX[xk]),
         '%+.4f' % pct(xk))] if xk else []))

print('\n# WHERE THE MOVE ACTUALLY ENDED — pxs per 5 min from 10:50 to 12:30')
a, b = K('10:50:00'), K('12:30:00')
box(('ts', '+min from open', 'pxs', 'pct LONG', 'ws6r', 'ws12r', 'ws2Mage'),
    [(SC.U(k), '%+.1f' % mn(k), '%.6f' % float(PX[k]), '%+.4f' % pct(k),
      '%.2f' % float(R[6][k]), '%.2f' % float(R[12][k]), '%.2f' % float(M2[k]))
     for k in range(a, b + 1, 60)])
seg = PX[k0:b + 1]; idx = np.arange(k0, b + 1)
ok = np.isfinite(seg) & (seg > 0); seg, idx = seg[ok], idx[ok]
f = int(seg.argmax())
print('- the highest pxs from the open to 12:30 is %.6f at %s, pct %+.4f (+%.1f min)'
      % (float(seg[f]), SC.U(int(idx[f])), pct(int(idx[f])), mn(int(idx[f]))))
print('- the as-built exit took %+.4f at 10:56:40' % pct(K('10:56:40')))
