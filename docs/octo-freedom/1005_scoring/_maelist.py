"""THE mae breach LIST, DATE ORDER. 1009.

Joe 1009: *"before I started this ws60r tangent, I was working on improving MAE braches ... I was
investigating a list that started on 07-11"*.

The build is the one in force before the tangent, per `_maetiming.py`'s own header: mae_stop_pct
2.5, reent_xwob 18, x-cross OFF, the rest banked, no ws60r gate.

Joe 1008 set the goal and it is NOT the stop: *"my goal is not to reduce the 2.5 based on reports.
my goal is to move the opens that are reliant on 2.something to locations that allow us to reduce
the stop, to increase the overall profitably with less risk"*.

So each breach carries WHERE ITS DRAWDOWN SAT: the MAE bar, the MFE bar, which came first, and the
best the leg ever reached before the stop took it.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

# W_NOX is a knob here, not an assert - the banked build has the x-cross LIVE
assert C.DGATE == 'off', 'run with W_DGATE=off - the pre-tangent build'
SC, box, U, PX = C.SC, C.box, C.SC.U, C.PX
N = len(SC.ts)
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                datetime.timezone.utc).strftime('%Y-%m-%d')
mn = lambda a, b: (int(SC.ts[b]) - int(SC.ts[a])) / 60000.0
C.MAE_STOP = float(os.environ.get('X_STOP', C.MAE_STOP))
_i = np.arange(N); fin = np.isfinite(T.X1) & np.isfinite(T.R1)
def holds(m, w):
    run = (_i + 1) - np.maximum.accumulate(np.where(m, 0, _i + 1))
    h = run >= w; cf = h & ~np.r_[False, h[:-1]]
    return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
T.XWOB = int(os.environ.get('X_REENT', 18))
T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & fin, T.XWOB)]
                   + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & fin, T.XWOB)],
                   key=lambda z: z[1])
print('# the build: mae_stop_pct %.2f, reent_xwob %d, W_NOX %s, W_DGATE %s'
      % (C.MAE_STOP, T.XWOB, C.NOX, C.DGATE), flush=True)
legs = []
k, d, g = 1, +1, 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    p0 = float(PX[k]); s = 1 if d > 0 else -1
    seg = np.asarray(PX[k:xk + 1], float); ok = np.isfinite(seg) & (seg > 0)
    rel = np.where(ok, (seg - p0) / p0 * 100.0 * s, np.nan)
    iw, ib = int(np.nanargmin(rel)), int(np.nanargmax(rel))
    arm = next((j for j, t in tr if t.startswith('exit-armed')), None)
    kick = next((j for j, t in tr if t.startswith('KICKSTART')), None)
    legs.append(dict(k=k, xk=xk, d=d, why=why, arm=arm, kick=kick, nev=len(tr),
                     real=(float(PX[xk]) - p0) / p0 * 100.0 * s,
                     mae=-float(rel[iw]), mfe=float(rel[ib]), maebar=k + iw, mfebar=k + ib,
                     mfe_before=max(0.0, float(np.nanmax(rel[:iw + 1])))))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d
br = [L for L in legs if L['why'] == 'mae breach']
box(('the chain', 'value'),
    [('legs', str(len(legs))),
     ('gross', '%+.4f' % sum(L['real'] for L in legs)),
     ('drag', '%.4f' % (len(legs) * 0.11)),
     ('NET AFTER DRAG', '%+.4f' % (sum(L['real'] for L in legs) - len(legs) * 0.11)),
     ('mae breaches', '%d = %.1f%% of legs' % (len(br), 100.0 * len(br) / len(legs))),
     ('their summed realised', '%+.4f' % sum(L['real'] for L in br)),
     ('the FIRST breach', '%s %s' % (DAY(br[0]['k']), U(br[0]['k'])) if br else 'none'),
     ('breaches whose walk NEVER armed',
      '%d of %d' % (sum(1 for L in br if L['arm'] is None), len(br)))])
# X_FROM filters the LIST, not the chain: the chain always walks from bar 1 so the leg boundaries
# are the banked ones. Joe 1009: *"I was investigating a list that started on 07-11"*.
FROM = os.environ.get('X_FROM_DAY', '')
if FROM:
    br = [L for L in br if DAY(L['k']) >= FROM]
    print('\n# filtered to breaches from %s onward: %d of them' % (FROM, len(br)))
NS = int(os.environ.get('X_N', 12))
print('\n# THE FIRST %d mae breach LEGS, DATE ORDER' % NS)
box(('day', 'opens', 'side', 'breaches', 'held min', 'realised', 'MAE', 'MFE',
     'MFE before the MAE bar', 'the MFE bar', 'at +min', 'which came first',
     'exit-armed at', 'KICKSTART at', 'trace events'),
    [(DAY(L['k']), U(L['k']), 'LONG' if L['d'] > 0 else 'SHORT', U(L['xk']),
      '%.1f' % mn(L['k'], L['xk']), '%+.4f' % L['real'], '%.4f' % L['mae'], '%.4f' % L['mfe'],
      '%.4f' % L['mfe_before'], U(L['mfebar']), '%.1f' % mn(L['k'], L['mfebar']),
      'MAE' if L['maebar'] < L['mfebar'] else 'MFE',
      U(L['arm']) if L['arm'] else 'NEVER', U(L['kick']) if L['kick'] else 'never',
      str(L['nev'])) for L in br[:NS]])
