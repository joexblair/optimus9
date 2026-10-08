"""THE 17:32:35 LEG UNDER THE NEW DIP BAND. 09-25. 1008. Verification only."""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

SC, PX, box = C.SC, C.PX, C.box
N = len(SC.ts); U = SC.U
K = lambda s: SC.K('2026-09-25 %s' % s)
A, B = K('17:00:00'), K('20:30:00')
print('# dip band %.0f-%.0f, dwell %d bars' % (C.DIP_LO, C.DIP_HI, C.DIP_DWELL))
k, d = T.K(T.START_D, '02:48:50'), +1
legs = []
for _ in range(300):
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    legs.append((k, d, xk, why, hand, tr))
    if k > B: break
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A)
        if cf is None: break
        k, d = cf, sd; continue
    k = xk; d = -d
hit = [L for L in legs if A <= L[0] <= B or A <= L[2] <= B]
print('\n# EVERY LEG TOUCHING 17:00-20:30 ON 09-25')
box(('open', 'side', 'exit', 'hold min', 'why', 'handover', 'pct'),
    [(U(k_), 'LONG' if d_ > 0 else 'SHORT', U(x_),
      '%.1f' % ((int(SC.ts[x_]) - int(SC.ts[k_])) / 60000.0), w_,
      U(h_) if h_ else '—',
      '%+.4f' % ((float(PX[x_]) - float(PX[k_])) / float(PX[k_]) * 100.0 * (1 if d_ > 0 else -1)))
     for k_, d_, x_, w_, h_, t_ in hit])
for k_, d_, x_, w_, h_, t_ in hit:
    p0 = float(PX[k_]); sgn = 1 if d_ > 0 else -1
    pct = lambda j: '%+.4f' % ((float(PX[j]) - p0) / p0 * 100.0 * sgn)
    mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[k_])) / 60000.0)
    print('\n## %s   %s' % (U(k_), 'LONG' if d_ > 0 else 'SHORT'))
    box(('ts', '+min', 'event', 'pxs', 'pct'),
        [(U(k_), '+0.0', 'OPEN', '%.6f' % p0, '+0.0000')]
        + [(U(j), mn(j), lab, '%.6f' % float(PX[j]), pct(j)) for j, lab in t_]
        + [(U(x_), mn(x_), 'EXIT — %s' % w_, '%.6f' % float(PX[x_]), pct(x_))])
