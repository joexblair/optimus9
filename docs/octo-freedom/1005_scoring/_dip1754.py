"""THE ws1Mage DIP AT ~17:54, AND THE LEG THAT EXITED 18:59:10. 09-25. 1008.

Joe 1008: *"18:59 should have exited/opened earlier / -per ws12 oob mech, the ws1 divergence print at
~18:15 should have print the trigger / -the possible disqualifier is the Mage dip. at ~17:54, my TV
view says it's 50. --if I'm correct and the dip was not captured, we'll use a small 100-{knob:53}
fence, ie 47 to 53"*.

THE DIP TEST AS IT STANDS, from `_chain10.run_leg`:
    indip = lambda k, d: (G1[k] < dip_mid 50) if d > 0 else (G1[k] > 50)
    if indip(j, d) and not indip(j - 1, d):        # a CROSSING of 50, not a touch
        n = the run of consecutive indip bars
        if n > dip_dwell_bars 12: dip, conf = j, j + 12 - 1

So the dip must CROSS 50 strictly. A dip that comes down to 50.00 and turns is not captured.

MEASURED HERE: ws1Mage bar by bar through 17:45-18:05, its minimum and where it sits, whether the
crossing test ever fires, and what the ws1r / ws2r divergence was doing at ~18:15.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.analysis.lr_v2 import _mage_rev
from optimus9.analysis.jig import anchor_floater
import _chain10 as C

SC, PX, box = C.SC, C.PX, C.box
N = len(SC.ts); U = SC.U
G1, R, X = C.G1, C.R, C.X
DIP_MID, DIP_DWELL = C.DIP_MID, C.DIP_DWELL
K = lambda s: SC.K('2026-09-25 %s' % s)
A, B = K('17:45:00'), K('18:05:00')
print('# dip_mid %.1f, dip_dwell_bars %d. The leg running into 18:59:10 is LONG (sides alternate),'
      % (DIP_MID, DIP_DWELL))
print('# so for it the dip is ws1Mage crossing BELOW %.1f.' % DIP_MID)

print('\n# ws1Mage, 17:45:00 TO 18:05:00 — EVERY BAR WHERE IT CHANGES')
rows = []; prev = None
for j in range(A, B + 1):
    v = float(G1[j])
    if prev is not None and v == prev: continue
    rows.append((U(j), '%.4f' % v, '—' if prev is None else '%+.4f' % (v - prev),
                 'BELOW 50' if v < 50 else ('AT 50.0000' if v == 50 else 'above 50'),
                 'in 47-53' if 47.0 <= v <= 53.0 else 'outside 47-53',
                 '%.6f' % float(PX[j])))
    prev = v
box(('ts', 'ws1Mage', 'step', 'vs the hard 50', 'vs the 47-53 fence', 'pxs'), rows)

lo = min(float(G1[j]) for j in range(A, B + 1))
lob = A + int(np.argmin([float(G1[j]) for j in range(A, B + 1)]))
cross = [j for j in range(A + 1, B + 1) if float(G1[j]) < DIP_MID and float(G1[j-1]) >= DIP_MID]
inband = [j for j in range(A, B + 1) if 47.0 <= float(G1[j]) <= 53.0]
under53 = [j for j in range(A, B + 1) if float(G1[j]) <= 53.0]
print('\n# WAS THE DIP CAPTURED?')
box(('the question', 'the answer'),
    [('ws1Mage minimum, 17:45-18:05', '%.4f at %s' % (lo, U(lob))),
     ('Joe\'s TV read at ~17:54', '50'),
     ('ws1Mage at 17:54:00', '%.4f' % float(G1[K('17:54:00')])),
     ('does it CROSS below %.1f?' % DIP_MID,
      ('YES at %s' % U(cross[0])) if cross else 'NO — it never goes under %.1f' % DIP_MID),
     ('bars inside the 47-53 fence', '%d' % len(inband)),
     ('bars at or under 53', '%d' % len(under53)),
     ('so the dip as coded is', 'CAPTURED' if cross else 'NOT CAPTURED')])

print('\n# THE LEG THAT EXITS 18:59:10 — its full trace, LONG')
# find it: walk the 2-day gate-A chain is heavy; run the leg from the previous exit directly.
import _chain_2day as T
rows = []; k, d = T.K(T.START_D, '02:48:50'), +1
tr_hit = None
for _ in range(200):
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    if xk == K('18:59:10'):
        tr_hit = (k, d, xk, why, hand, tr); break
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A)
        if cf is None: break
        k, d = cf, sd; continue
    k = xk; d = -d
if tr_hit:
    k, d, xk, why, hand, tr = tr_hit
    p0 = float(PX[k]); sgn = 1 if d > 0 else -1
    pct = lambda j: '%+.4f' % ((float(PX[j]) - p0) / p0 * 100.0 * sgn)
    mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[k])) / 60000.0)
    print('## %s   %s   handover %s' % (U(k), 'LONG' if d > 0 else 'SHORT',
                                        U(hand) if hand else 'NONE'))
    box(('ts', '+min', 'event', 'pxs', 'pct'),
        [(U(k), '+0.0', 'OPEN %s' % ('LONG' if d > 0 else 'SHORT'), '%.6f' % p0, '+0.0000')]
        + [(U(j), mn(j), lab, '%.6f' % float(PX[j]), pct(j)) for j, lab in tr]
        + [(U(xk), mn(xk), 'EXIT — %s' % why, '%.6f' % float(PX[xk]), pct(xk))])
else:
    print('- no leg in the first 200 exits at 18:59:10 under the current router.')

print('\n# THE ws1r AND ws2r DIVERGENCE CANDIDATES, 18:05 TO 18:30')
dd = tr_hit[1] if tr_hit else +1
REV = {t: _mage_rev(R[t], C.RREV) for t in C.DIV_TFS}
rows = []
for j in range(K('18:05:00'), K('18:30:00') + 1):
    for t in C.DIV_TFS:
        if REV[t][j] != C.WANT(dd) or not C.xund(t, j, dd): continue
        af = anchor_floater(R[t], PX, dd, j)
        rows.append((U(j), 'ws%dr' % t, '%.2f' % float(R[t][j]), '%.2f' % float(X[t][j]),
                     'yes' if af else 'no',
                     ('%d' % int(af['fired'])) if af else '—',
                     ('%+.2f' % af['d_osc']) if af else '—',
                     (U(af['floater'][0])) if af else '—',
                     'WOULD FIRE' if (af and int(af['fired'])) else 'no fire'))
box(('ts', 'line', 'r', 'x', 'floater found', 'fired', 'd_osc', 'the floater bar', 'ruling'),
    rows or [('—', '—', '—', '—', '—', '—', '—', '—', 'no candidate in the window')])
print('- the divergence can only be tested AFTER the handover and AFTER the dip confirms.')
