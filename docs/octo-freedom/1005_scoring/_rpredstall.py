"""WAS A lin_hop LINE ALREADY r-pred WHEN THE WALK GAVE UP? 1009.

Joe 1009: *"climbing r lines is a very old mech (look for r-pred) that I've iterated and evolved
over time"* / *"the r-pred calc compared the distance from r to boundary while r was ib, against
Mage's distance to the boundary while Mage was oob"* / *"M is Mage. we changed it because the db
collation wasn't case sensitive"*.

So the anchor is max(m, Mage) on the hi side, min on the lo side - `predict_breach` in
optimus9/compute/breaching_line.py, his mech from 0730.

EACH LINE PREDICTS ITSELF from its own m and Mage. The cross-timeframe form Joe has in
arm_gate_emit.py - s5m/s5Mage predicting s10r - is a separate variant, not this.

The question is the same one the momentum masks are being built for, asked with a mech that costs
nothing: at the bar the walk stalled, was a line the baton could have reached ALREADY predicted to
breach on the leg's side.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T
from optimus9.compute.breaching_line import predict_breach, HI as BHI, LO as BLO
from optimus9.constants import FENCE_HI, FENCE_LO

SC, box, U, PX = C.SC, C.box, C.SC.U, C.PX
N = len(SC.ts)
EXTRA = [45, 60, 90, 120]
RR, PRED = {}, {}
for t in list(C.ALL_TF) + EXTRA:
    try:
        r = np.asarray(SC.LD(t * 60, 'r'), float)[:N]
        m = np.asarray(SC.LD(t * 60, 'm'), float)[:N]
        g = np.asarray(SC.LD(t * 60, 'Mage'), float)[:N]
    except Exception as e:
        print('# ws%d skipped: %s' % (t, str(e)[:70]), flush=True); continue
    RR[t] = r
    PRED[t] = predict_breach(r, m, g, BHI, BLO, FENCE_HI, FENCE_LO)
TFS = sorted(RR)
print('# r-pred computed for %d lines, boundary %.0f/%.0f, fence %.0f/%.0f'
      % (len(TFS), BHI, BLO, FENCE_HI, FENCE_LO), flush=True)
box(('the line', 'r-pred HIGH bars', '% of tape', 'r-pred LOW bars', '% of tape'),
    [('ws%d' % t, str(int((PRED[t] > 0).sum())), '%.2f%%' % (100.0 * (PRED[t] > 0).sum() / N),
      str(int((PRED[t] < 0).sum())), '%.2f%%' % (100.0 * (PRED[t] < 0).sum() / N)) for t in TFS])

oob = lambda t, j, d: (float(RR[t][j]) >= SC.HI) if d > 0 else (float(RR[t][j]) <= SC.LO)
rp = lambda t, j, d: (int(PRED[t][j]) == (1 if d > 0 else -1))
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                datetime.timezone.utc).strftime('%Y-%m-%d')
_i = np.arange(N); fin = np.isfinite(T.X1) & np.isfinite(T.R1)
def holds(m_, w):
    run = (_i + 1) - np.maximum.accumulate(np.where(m_, 0, _i + 1))
    h = run >= w; cf = h & ~np.r_[False, h[:-1]]
    return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
T.XWOB = 18
T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & fin, 18)]
                   + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & fin, 18)], key=lambda z: z[1])
legs = []
k, d, g = 1, +1, 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    rider = None; aceil = C.BASE_HI
    for j, t in tr:
        if t.startswith('KICKSTART'): rider = int(t.split('rider ws')[1].split(' ')[0])
        elif t.startswith('baton -> ws'): rider = int(t.split('baton -> ws')[1].split(' ')[0])
        elif 'CEILING' in t: aceil = C.CEIL_HI
    p0 = float(PX[k]); s = 1 if d > 0 else -1
    legs.append(dict(k=k, xk=xk, d=d, why=why, rider=rider, aceil=aceil,
                     real=(float(PX[xk]) - p0) / p0 * 100.0 * s))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d
for i, L in enumerate(legs):
    L['next_breach'] = bool(i + 1 < len(legs) and legs[i + 1]['why'] == 'mae breach'
                            and legs[i + 1]['k'] == L['xk'])
fs = [L for L in legs if L['why'] == 'final stalled' and L['rider'] is not None]
print('\n# %d legs, %d stalled with a known rider, %d of those hand into a breach'
      % (len(legs), len(fs), sum(1 for L in fs if L['next_breach'])), flush=True)

for nm, sel in (('EVERY STALL', fs),
                ('THE STALLS THAT HAND INTO A BREACH', [L for L in fs if L['next_breach']])):
    if not sel: continue
    n = len(sel); c = collections.Counter(); hi = collections.Counter()
    for L in sel:
        j, d_, r_, ac = L['xk'], L['d'], L['rider'], L['aceil']
        cap = min(r_ + C.LIN_HOP, ac)
        inhop = [t for t in TFS if r_ < t <= cap]
        c['stalls where a lin_hop line was r-pred' if any(rp(t, j, d_) for t in inhop)
          else 'stalls where NO lin_hop line was r-pred'] += 1
        if any(rp(t, j, d_) for t in inhop):
            for t in inhop:
                if rp(t, j, d_): hi['ws%d' % t] += 1
        anyab = [t for t in TFS if t > r_ and rp(t, j, d_)]
        if anyab: c['  and somewhere above the rider, r-pred fired'] += 1
        c['stalls where ANY line above the rider was r-pred' if anyab
          else 'stalls where NO line above the rider was r-pred'] += 1
    print('\n# %s — %d stalls' % (nm, n))
    box(('the reading', 'stalls', '% of them'),
        [(kk, str(v), '%.1f%%' % (100.0 * v / n)) for kk, v in sorted(c.items())])
    if hi:
        box(('the r-pred line inside lin_hop', 'stalls', '% of them'),
            [(kk, str(v), '%.1f%%' % (100.0 * v / n)) for kk, v in sorted(hi.items(),
             key=lambda z: -z[1])])
