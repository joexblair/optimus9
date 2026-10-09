"""HOW MANY PSEUDO TRADES EVEN REACH THEIR ws12r INTERCHANGE. 1009.

Found on 08-22's first two pseudo trades: BOTH closed before their ws12r oob event arrived.
  trade 1  A opens 22:27:45 SHORT, closes 23:54:10 on x-cross. The interchange is 00:12:00 - 18 min
           AFTER A was already flat.
  trade 2  A opens 00:10:20 LONG, closes 00:26:55 on x-cross. The interchange is 01:24:00 - 57 min
           after.
So neither tested the ws12r decision at all, and every statistic I reported from the 3,795 is
weighted by trades that never got there. This counts it.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
assert C.DGATE == 'traj'
SC, box, U = C.SC, C.box, C.SC.U
PXa = C.PX; N = len(SC.ts); TF = C.TRIG_TF
R12, M2 = C.R[TF], C.M2; HI, LO = SC.HI, SC.LO
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                               datetime.timezone.utc).strftime('%Y-%m-%d')
mn = lambda a, b: (int(SC.ts[b]) - int(SC.ts[a])) / 60000.0
m = np.asarray(M2[:N], float); fin = np.isfinite(m)
up = np.zeros(N, bool); dn = np.zeros(N, bool)
up[1:] = fin[1:] & fin[:-1] & (m[:-1] <= LO) & (m[1:] > LO)
dn[1:] = fin[1:] & fin[:-1] & (m[:-1] >= HI) & (m[1:] < HI)
lu = ld = -1; LU = np.full(N, -1, np.int64); LD = np.full(N, -1, np.int64)
for k in range(N):
    if up[k]: lu = k
    if dn[k]: ld = k
    LU[k] = lu; LD[k] = ld
r = np.asarray(R12[:N], float)
EV = []
for k in range(1, N):
    for side in (+1, -1):
        if ((r[k] >= HI) if side > 0 else (r[k] <= LO)) and \
           not ((r[k - 1] >= HI) if side > 0 else (r[k - 1] <= LO)):
            EV.append((k, side, int(LU[k]) if side > 0 else int(LD[k]))); break
print('# %d ws12r oob events' % len(EV), flush=True)
_days = sorted({DAY(k) for k in range(0, N, 2000)})
BLK = {'all': set(_days), 'fit': set(_days[:47]), 'hold': set(_days[47:])}
res = []
seen = {}
for i, (ev, side, o) in enumerate(EV):
    if o < 0: continue
    if (o, side) in seen:
        a0, a1 = seen[(o, side)]
    else:
        a = C.run_leg(o, side)
        if a[0] is None: continue
        a0, a1 = a[0], a[1]
        seen[(o, side)] = (a0, a1)
    res.append(dict(ev=ev, side=side, open=o, axk=a0, awhy=a1,
                    reach=(a0 >= ev), lead=mn(o, ev), gap=mn(a0, ev)))
    if i % 500 == 0: print('#   %d of %d' % (i, len(EV)), flush=True)
print('# %d scored, %d distinct (open, side) pairs' % (len(res), len(seen)), flush=True)

print('\n# DOES A REACH ITS OWN ws12r INTERCHANGE')
box(('the measure', 'all 95 days', 'fit', 'hold'),
    [(lab, *[str(f([x for x in res if blk == 'all' or DAY(x['ev']) in BLK[blk]]))
             for blk in ('all', 'fit', 'hold')])
     for lab, f in (
        ('pseudo trades scored', len),
        ('A still OPEN at the interchange — the decision happens',
         lambda z: sum(1 for x in z if x['reach'])),
        ('A already CLOSED before the interchange — no decision',
         lambda z: sum(1 for x in z if not x['reach'])),
     )])
rr = [x for x in res if x['reach']]
nn = [x for x in res if not x['reach']]
box(('the measure', 'value'),
    [('reach rate', '%.1f%%' % (100.0 * len(rr) / len(res))),
     ('median lead min, open to the interchange — reached', '%.1f' % np.median([x['lead'] for x in rr])),
     ('median lead min — NOT reached', '%.1f' % np.median([x['lead'] for x in nn])),
     ('median min A closed BEFORE the interchange', '%.1f' % np.median([-x['gap'] for x in nn])),
     ('worst, A closed this long before it', '%.1f' % max(-x['gap'] for x in nn))])
print('\n# WHY A CLOSED EARLY — the exits of the trades that never reached their interchange')
w = collections.Counter(x['awhy'] for x in nn)
box(('A\'s exit', 'trades', 'as % of the not-reached'),
    [(k2, str(c), '%.1f%%' % (100.0 * c / len(nn))) for k2, c in w.most_common()])
print('\n# AND THE EXITS OF THE ONES THAT DID REACH IT')
w = collections.Counter(x['awhy'] for x in rr)
box(('A\'s exit', 'trades', 'as % of the reached'),
    [(k2, str(c), '%.1f%%' % (100.0 * c / len(rr))) for k2, c in w.most_common()])
