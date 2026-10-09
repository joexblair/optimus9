"""OPEN 7, END TO END — does Mage-vs-r predict pxs REVERSING at a ws12r oob event. 1009.

Joe's reasoning has two links:
  link 1  the Mage pulls r      -> sign(ws60Mage - ws60r) predicts the sign of ws60r's next move
  link 2  pxs follows r         -> ws60r's direction predicts pxs's direction
and the conclusion is link 1 + link 2: Mage position predicts whether pxs reverses.

LINK 1 MEASURED AT 49.7% - 53.6% AGREEMENT over 20,311 to 26,717 samples. A coin flip. So the
chain of reasoning is broken at its first step on this tape.

BUT THE CONCLUSION CAN STILL BE TRUE WITHOUT THE REASONING, so it is measured on its own terms
here, at the bars the rule would actually fire on: ws12r oob events.

  the population   every ws12r oob crossing, and separately every 6-min dwell-ending
  the rule         TRUE (pxs reverses) iff sign(ws60Mage - ws60r) == -(the oob side)
  the outcome      the next swing_detect pivot after that bar. A REVERSAL is a pivot on the oob
                   side's own extreme - high oob -> an 'H' means price rose into it, so a reversal
                   is an 'L'. Joe 1008: *"swing detect is strictly a backtest tool"*, so it is the
                   SCORER here and never an input.
  the base rate    the FALSE rows, printed beside the TRUE rows. A hit rate with no base rate is
                   not a measurement.

LINK 2 IS ALSO MEASURED on its own: does ws60r's realised move predict pxs's realised move.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute.swing_detect import find_pivots
import _chain10 as C

SC, box, U = C.SC, C.box, C.SC.U
PXa = C.PX
N = len(SC.ts)
R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
M60 = np.asarray(SC.LD(60 * 60, 'Mage'), float)[:N]
R12 = C.R[C.TRIG_TF]
HI, LO = SC.HI, SC.LO
GATE = C.GATE_BARS
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                               datetime.timezone.utc).strftime('%Y-%m-%d')
_days = sorted({DAY(k) for k in range(0, N, 2000)})
BLK = {'all': set(_days), 'fit': set(_days[:47]), 'hold': set(_days[47:])}
print('# tape %d bars, oob_gate_bars %d' % (N, GATE), flush=True)

# ---- LINK 2: does ws60r's move predict pxs's move
print('\n# LINK 2 — DOES pxs FOLLOW ws60r')
rows = []
idx = np.arange(0, N - 2200, 60)
for mins in (5, 15, 30, 60, 120):
    off = int(mins * 60 / 5)
    rm = R60[idx + off] - R60[idx]
    pm = PXa[idx + off] - PXa[idx]
    m = np.isfinite(rm) & np.isfinite(pm) & (rm != 0) & (pm != 0)
    rows.append(('%d min' % mins, str(int(m.sum())),
                 '%.1f%%' % (100.0 * (np.sign(rm[m]) == np.sign(pm[m])).mean())))
box(('measured this far ahead', 'samples', 'sign(ws60r move) agrees with sign(pxs move)'), rows)

# ---- the events
EV = []
k = 1
while k < N:
    for side in (+1, -1):
        now = (float(R12[k]) >= HI) if side > 0 else (float(R12[k]) <= LO)
        was = (float(R12[k - 1]) >= HI) if side > 0 else (float(R12[k - 1]) <= LO)
        if now and not was:
            j = k
            while j < N and (((float(R12[j]) >= HI) if side > 0 else (float(R12[j]) <= LO))): j += 1
            EV.append((k, side, j - k)); break
    k += 1
print('\n# %d ws12r oob crossings; %d reach the %d-bar dwell-ending'
      % (len(EV), sum(1 for _, _, r in EV if r > GATE + 1), GATE), flush=True)

PIV = {}
for pct in (0.9, 1.0):
    pv = find_pivots(PXa, pct)
    ni = np.full(N, -1, np.int64); nk = np.zeros(N, np.int8)
    s_ = 0
    for b_, kd_ in pv:
        if b_ > s_:
            ni[s_:b_] = b_; nk[s_:b_] = 1 if kd_ == 'H' else -1
        s_ = b_
    PIV[pct] = (ni, nk)

def tab(pct, bar, blk):
    ni, nk = PIV[pct]
    t = [0, 0, 0.0]; f = [0, 0, 0.0]; z = 0
    for k, side, run in EV:
        b = k if bar == 'x' else (k + GATE + 1 if run > GATE + 1 else None)
        if b is None or b >= N: continue
        if blk != 'all' and DAY(b) not in BLK[blk]: continue
        g = float(M60[b]) - float(R60[b])
        if g == 0: z += 1; continue
        ret = (1 if g > 0 else -1) == -side          # Joe's rule: TRUE = pxs reverses
        if int(ni[b]) < 0: continue
        rev = int(nk[b]) == -side                    # the next pivot is a reversal of the oob side
        p0 = float(PXa[b]); p1 = float(PXa[int(ni[b])])
        mv = (p1 - p0) / p0 * 100.0 * (-side)        # + = price moved AGAINST the oob side
        d = t if ret else f
        d[0] += 1; d[1] += rev; d[2] += mv
    return t, f, z

for pct in (1.0, 0.9):
    for bar, blab in (('x', 'at the ws12r oob CROSSING'),
                      ('h', 'at the 6-min DWELL-ENDING')):
        print('\n# %s, swing_detect %.1f%%' % (blab, pct))
        rows = []
        for blk in ('all', 'fit', 'hold'):
            t, f, z = tab(pct, bar, blk)
            rows.append((blk, str(t[0] + f[0]),
                         str(t[0]), '%.1f%%' % (100.0 * t[1] / t[0]) if t[0] else '—',
                         str(f[0]), '%.1f%%' % (100.0 * f[1] / f[0]) if f[0] else '—',
                         '%+.1f' % ((100.0 * t[1] / t[0]) - (100.0 * f[1] / f[0]))
                         if t[0] and f[0] else '—',
                         '%+.4f' % (t[2] / t[0]) if t[0] else '—',
                         '%+.4f' % (f[2] / f[0]) if f[0] else '—', str(z)))
        box(('block', 'events', 'Joe TRUE — pxs reverses', 'of those, it DID reverse',
             'Joe FALSE — no reversal', 'of those, it reversed anyway', 'spread, pts',
             'TRUE mean pxs move against the oob side', 'FALSE mean pxs move against',
             'Mage == r exactly'), rows)
print('\n- "it DID reverse" = the next swing_detect pivot is on the side that means price turned')
print('  away from the oob side. For a HIGH oob event that is an L; for a LOW oob event an H.')
print('- the FALSE column is the base rate. If Joe\'s rule works, TRUE sits well above FALSE.')
