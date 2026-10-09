"""THE REACH RATE UNDER THE ws12r MOM-TRUE OPEN. 1009.

Joe 1009: *"I like the ws12 mom-true event idea"*.

ws2Mage's open gave a reach rate of 17.8% - 3,120 of 3,795 pseudo trades were already flat when
their own ws12r oob event arrived, a median 56.1 min early. This measures the mom-true open against
the same question before anything is rebuilt on it.

THE OPEN: walking back from the oob crossing, the newest bar where ws12r BECOMES mom-true on the
event's side - the RISING EDGE of `momo_gated.momo_g`. Joe 1009 ruled the function:
*"we're not using it for our current builds"* of strip-mom-at-fence, so curl gates on, strip off.

ALSO MEASURED, because it decides whether the open is meaningful or incidental:
  is ws12r mom-true AT the oob crossing bar?  If yes, the rising edge we walk back to is the start
  of the CURRENT run and the trade is open across the whole climb. If no, the edge belongs to an
  older, unrelated run and the open is arbitrary.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
from _momtrue import momtrue_mask, rising
from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
assert C.DGATE == 'traj'
SC, box, U = C.SC, C.box, C.SC.U
PXa = C.PX; N = len(SC.ts); TF = C.TRIG_TF
R12 = C.R[TF]; HI, LO = SC.HI, SC.LO
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                               datetime.timezone.utc).strftime('%Y-%m-%d')
mn = lambda a, b: (int(SC.ts[b]) - int(SC.ts[a])) / 60000.0
MT = momtrue_mask(C.RL[TF], TF, C.BANK[TF], SC.EM, HOURS, WARMUP, 'gated', N)
RE = {d: rising(MT[d]) for d in (+1, -1)}
LAST = {}
for d in (+1, -1):
    a = np.full(N, -1, np.int64); last = -1
    for k in range(N):
        if RE[d][k]: last = k
        a[k] = last
    LAST[d] = a
# the start of the CURRENT mom-true run at bar k, or -1 when not mom-true there
RUN0 = {}
for d in (+1, -1):
    a = np.full(N, -1, np.int64); st = -1
    for k in range(N):
        if MT[d][k]:
            if st < 0: st = k
            a[k] = st
        else:
            st = -1; a[k] = -1
    RUN0[d] = a
print('# mom-true masks ready', flush=True)

r = np.asarray(R12[:N], float)
EV = []
for k in range(1, N):
    for side in (+1, -1):
        if ((r[k] >= HI) if side > 0 else (r[k] <= LO)) and \
           not ((r[k - 1] >= HI) if side > 0 else (r[k - 1] <= LO)):
            EV.append((k, side)); break
print('# %d ws12r oob events' % len(EV), flush=True)

_days = sorted({DAY(k) for k in range(0, N, 2000)})
BLK = {'all': set(_days), 'fit': set(_days[:47]), 'hold': set(_days[47:])}
res = []; seen = {}
for i, (ev, side) in enumerate(EV):
    mt_at = bool(MT[side][ev])
    o = int(RUN0[side][ev]) if mt_at else int(LAST[side][ev])
    if o < 0: 
        res.append(dict(ev=ev, side=side, open=None, mt_at=mt_at)); continue
    if (o, side) in seen: a0, a1 = seen[(o, side)]
    else:
        a = C.run_leg(o, side)
        if a[0] is None:
            res.append(dict(ev=ev, side=side, open=o, mt_at=mt_at, axk=None)); continue
        a0, a1 = a[0], a[1]; seen[(o, side)] = (a0, a1)
    res.append(dict(ev=ev, side=side, open=o, mt_at=mt_at, axk=a0, awhy=a1,
                    reach=(a0 >= ev), lead=mn(o, ev), gap=mn(a0, ev)))
    if i % 500 == 0: print('#   %d of %d' % (i, len(EV)), flush=True)
ok = [x for x in res if x.get('axk')]
print('# %d scored, %d distinct opens' % (len(ok), len(seen)), flush=True)

print('\n# IS ws12r MOM-TRUE AT ITS OWN oob CROSSING')
box(('the measure', 'all 95 days', 'fit', 'hold'),
    [(lab, *[str(f([x for x in res if blk == 'all' or DAY(x['ev']) in BLK[blk]]))
             for blk in ('all', 'fit', 'hold')])
     for lab, f in (('ws12r oob events', len),
                    ('mom-true AT the crossing — the open is the current run\'s start',
                     lambda z: sum(1 for x in z if x['mt_at'])),
                    ('NOT mom-true there — the open is an older rising edge',
                     lambda z: sum(1 for x in z if not x['mt_at'])),
                    ('no rising edge before it at all',
                     lambda z: sum(1 for x in z if x.get('open') is None)))])

print('\n# DOES A REACH ITS OWN INTERCHANGE — mom-true open vs the ws2Mage open')
box(('the measure', 'all 95 days', 'fit', 'hold'),
    [(lab, *[str(f([x for x in ok if blk == 'all' or DAY(x['ev']) in BLK[blk]]))
             for blk in ('all', 'fit', 'hold')])
     for lab, f in (('pseudo trades scored', len),
                    ('A still OPEN at the interchange', lambda z: sum(1 for x in z if x['reach'])),
                    ('A already CLOSED before it', lambda z: sum(1 for x in z if not x['reach'])))])
rr = [x for x in ok if x['reach']]; nn = [x for x in ok if not x['reach']]
box(('the measure', 'the mom-true open', 'the ws2Mage open'),
    [('reach rate', '**%.1f%%**' % (100.0 * len(rr) / len(ok)), '17.8%'),
     ('median lead min — reached', '%.1f' % np.median([x['lead'] for x in rr]), '68.0'),
     ('median lead min — not reached',
      '%.1f' % np.median([x['lead'] for x in nn]) if nn else '—', '97.2'),
     ('median min A closed before it',
      '%.1f' % np.median([-x['gap'] for x in nn]) if nn else '—', '-56.1')])
if nn:
    w = collections.Counter(x['awhy'] for x in nn)
    print('\n# WHY A STILL CLOSED EARLY')
    box(('A\'s exit', 'trades', 'as %'),
        [(k2, str(c), '%.1f%%' % (100.0 * c / len(nn))) for k2, c in w.most_common()])
w = collections.Counter(x['awhy'] for x in rr)
print('\n# THE EXITS OF THE ONES THAT REACHED IT')
box(('A\'s exit', 'trades', 'as %'),
    [(k2, str(c), '%.1f%%' % (100.0 * c / len(rr))) for k2, c in w.most_common()])
