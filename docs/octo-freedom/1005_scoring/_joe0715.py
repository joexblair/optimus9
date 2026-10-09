"""JOE'S 07-15 READ, THE THREE ITEMS. 1009.

  1 *"2026-07-15 09:36:15 SHORT should have closed by lineage at 09:56, ws4 last rider"*
  2 *"2026-07-15 14:49:00 LONG - this can't be a LONG signal - the ws12r oob is low oob"*
  3 *"because BB lines lead K lines, the ws60r UP event that the current code consumes needs to be
    reversed by the downward ws60x-cross-race that fired ~14:15 (+/-20 minutes) with a 24 or 48 bar
    xwob ... ws60r then has no choice but to turn DOWN and follow ws60x"* / *"the lookback needed
    for 'recent ws60x' is not clear to me on my TV charts"*.

Item 3 is answered by MEASURING THE LAG: from a ws60x cross held `xwob` bars, how many bars until
ws60r's own traj turns to match it. The distribution of that lag IS the lookback.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1005_scoring')
os.environ['W_DGATE'] = 'vote'; os.environ.setdefault('W_VOTE_TIE', 'c3')
import _chain10 as C
from _trajmech import traj
SC, box, U, PX = C.SC, C.box, C.SC.U, C.PX
N = len(SC.ts); TF = C.TRIG_TF
R12 = np.asarray(C.R[TF], float)[:N]
R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
X60 = np.asarray(SC.LD(60 * 60, 'x'), float)[:N]

print('########## ITEM 1 — the B that opened 2026-07-15 09:36:15 SHORT')
k = SC.K('2026-07-15 09:36:15'); d = -1
xk, why, mae, cb, hand, tr = C.run_leg(k, d)
p0 = float(PX[k]); s = -1
pct = lambda j: '%+.4f' % ((float(PX[j]) - p0) / p0 * 100.0 * s)
mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[k])) / 60000.0)
box(('ts', '+min', 'event', 'pxs', 'pct'),
    [(U(k), '+0.0', 'B OPENS SHORT', '%.6f' % p0, '+0.0000')]
    + [(U(j), mn(j), t, '%.6f' % float(PX[j]), pct(j)) for j, t in sorted(tr)]
    + [(U(xk), mn(xk), 'B CLOSES on %s' % why, '%.6f' % float(PX[xk]), pct(xk))])
print('\n# THE WALK\'S STATE AROUND 09:56 — is ws4 stalled, and what is the rider allowed to be')
b0, b1 = SC.K('2026-07-15 09:50:00'), SC.K('2026-07-15 10:02:00')
rows = []
for j in range(b0, b1 + 1, 24):
    rows.append((U(j), '%.2f' % float(C.R[4][j]),
                 'YES' if C.ST[(4, d)][j] else 'no',
                 'YES' if C.oobf(4, j, d) else 'no',
                 ', '.join('ws%d' % t for t in C.ALL_TF
                           if t <= C.CEIL_HI and C.oobf(t, j, d)) or 'none',
                 ', '.join('ws%d' % t for t in C.ALL_TF
                           if t <= C.CEIL_HI and C.ST[(t, d)][j]) or 'none'))
box(('ts', 'ws4r', 'ws4 STALLED?', 'ws4 oob?', 'every TF oob on the dr side',
     'every TF stalled on the dr side'), rows)

print('\n\n########## ITEM 2 — the B that opened 2026-07-15 14:49:00 LONG, and its parent A')
kb = SC.K('2026-07-15 14:49:00')
# find the A leg whose exit bar is kb, by walking the chain
import _chain_2day as T
_i = np.arange(N); fin = np.isfinite(T.X1) & np.isfinite(T.R1)
def holds(m, w):
    run = (_i + 1) - np.maximum.accumulate(np.where(m, 0, _i + 1))
    h = run >= w; cf = h & ~np.r_[False, h[:-1]]
    return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
T.XWOB = 18
T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & fin, 18)]
                   + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & fin, 18)], key=lambda z: z[1])
k2, d2, g, par = 1, +1, 0, None
while True:
    g += 1
    if g > 20000: break
    xk2, why2, mae2, cb2, hand2, tr2 = C.run_leg(k2, d2)
    if xk2 is None: break
    if xk2 == kb: par = (k2, d2, xk2, why2, tr2); break
    if why2 == 'mae breach':
        rb, cf, sd = T.find_reentry(xk2, T.gate_A, N - 1)
        if cf is None: break
        k2, d2 = cf, sd; continue
    if xk2 >= N - 1: break
    k2 = xk2; d2 = -d2
if par is None:
    print('- no A leg on the chain exits at 14:49:00')
else:
    ka, da, xa, wa, tra = par
    box(('the fact', 'value'),
        [('A opens', '%s %s' % (U(ka), 'LONG' if da > 0 else 'SHORT')),
         ('A closes', U(xa)), ('A\'s exit', wa),
         ('so B opens', 'LONG' if -da > 0 else 'SHORT'),
         ('ws%dr at A\'s exit bar' % TF, '%.2f' % float(R12[xa])),
         ('which oob side that is', 'LOW (<=%.0f)' % C.G_LO if float(R12[xa]) <= C.G_LO
          else ('HIGH (>=%.0f)' % C.G_HI if float(R12[xa]) >= C.G_HI else 'IN-BOUNDS')),
         ('the oob run goob tests on A\'s dr %+d' % da,
          'HIGH' if da > 0 else 'LOW')])
    print('\n# A\'s own trace, for the oob run that produced the flip')
    box(('ts', 'event'), [(U(j), t) for j, t in sorted(tra)])

print('\n\n########## ITEM 3 — THE ws60x CROSS-RACE NEAR 14:15, AND THE LAG TO ws60r TURNING')
a0, a1 = SC.K('2026-07-15 13:45:00'), SC.K('2026-07-15 15:10:00')
xu = X60 < R60
rows = []
for j in range(a0 + 1, a1 + 1):
    if xu[j] and not xu[j - 1]:
        hold = 0
        while j + hold < N and xu[j + hold]: hold += 1
        rows.append((U(j), '%.4f' % float(X60[j]), '%.4f' % float(R60[j]),
                     '%+.4f' % (float(X60[j]) - float(R60[j])), str(hold),
                     '%.1f' % (hold * 5 / 60.0),
                     'YES' if hold >= 24 else 'no', 'YES' if hold >= 48 else 'no'))
print('# every DOWNWARD ws60x cross of ws60r in 13:45-15:10 on 07-15')
box(('the cross', 'ws60x', 'ws60r', 'x - r', 'bars it held', 'min held',
     'holds 24 bars?', 'holds 48 bars?'), rows)
