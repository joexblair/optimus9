"""THE 07-15 / 07-16 TRADES THAT STALLED AND EXITED BELOW ws3. 1009.

Joe 1009: *"show me the trades in 07-15 and 07-16 that stalled and exited before ws3"* - the ws1
and ws2 deaths, which carry 34.0% and 22.1% of all stalls.

Per trade: the full walk, then what was sitting one and two rungs above the rider at the exit bar -
momentum, r-pred and oob side by side, with whether the baton could have taken it.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T
from _momtrue import CACHE, _key
from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
from optimus9.compute.breaching_line import predict_breach as _pb
from optimus9.constants import FENCE_HI as _FH, FENCE_LO as _FL

SC, box, U, PX = C.SC, C.box, C.SC.U, C.PX
N = len(SC.ts)
MOMT, RPRED = {}, {}
for t in C.ALL_TF:
    p = os.path.join(CACHE, 'momt_%s.npz'
                     % _key(SC.EM, HOURS, WARMUP, t, int(C.BANK[t]['k_window']), 'gated'))
    if os.path.exists(p):
        z = np.load(p)
        if len(z['p']) == N: MOMT[t] = {+1: z['p'].astype(bool), -1: z['m'].astype(bool)}
    RPRED[t] = _pb(np.asarray(C.RL[t], float)[:N],
                   np.asarray(SC.LD(t * 60, 'm'), float)[:N],
                   np.asarray(SC.LD(t * 60, 'Mage'), float)[:N], SC.HI, SC.LO, _FH, _FL)
print('# momentum masks for: %s' % ', '.join('ws%d' % t for t in sorted(MOMT)), flush=True)
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                datetime.timezone.utc).strftime('%Y-%m-%d')
DAYS = set(os.environ.get('X_DAYS', '2026-07-15,2026-07-16').split(','))
MAXR = int(os.environ.get('X_MAXR', 3))      # 'before ws3' = the rider was below ws3
_i = np.arange(N); fin = np.isfinite(T.X1) & np.isfinite(T.R1)
def holds(m, w):
    run = (_i + 1) - np.maximum.accumulate(np.where(m, 0, _i + 1))
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
    seg = np.asarray(PX[k:xk + 1], float); ok = np.isfinite(seg) & (seg > 0)
    rel = np.where(ok, (seg - p0) / p0 * 100.0 * s, np.nan)
    legs.append(dict(k=k, xk=xk, d=d, why=why, rider=rider, aceil=aceil, tr=list(tr),
                     real=(float(PX[xk]) - p0) / p0 * 100.0 * s,
                     mae=-float(np.nanmin(rel)), mfe=float(np.nanmax(rel))))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d
for i, L in enumerate(legs):
    L['nb'] = bool(i + 1 < len(legs) and legs[i + 1]['why'] == 'mae breach'
                   and legs[i + 1]['k'] == L['xk'])
    L['nxt'] = legs[i + 1]['real'] if i + 1 < len(legs) else None
sel = [L for L in legs if L['why'] == 'final stalled' and L['rider'] is not None
       and L['rider'] < MAXR and DAY(L['xk']) in DAYS]
print('# %d trades on %s stalled with the rider below ws%d\n'
      % (len(sel), ' and '.join(sorted(DAYS)), MAXR), flush=True)
for n, L in enumerate(sel, 1):
    j, d_, r_ = L['xk'], L['d'], L['rider']
    p0 = float(PX[L['k']]); s = 1 if d_ > 0 else -1
    pct = lambda q: '%+.4f' % ((float(PX[q]) - p0) / p0 * 100.0 * s)
    mn = lambda q: '%+.1f' % ((int(SC.ts[q]) - int(SC.ts[L['k']])) / 60000.0)
    print('\n########## %s %s %s — stalls %s on ws%d — realised %+.4f  MAE %.4f  MFE %.4f%s'
          % (DAY(L['k']), U(L['k']), 'LONG' if d_ > 0 else 'SHORT', U(j), r_,
             L['real'], L['mae'], L['mfe'],
             '   >>> THE NEXT TRADE BREACHED (%+.4f)' % L['nxt'] if L['nb'] else ''))
    box(('ts', '+min', 'event', 'pxs', 'pct'),
        [(U(L['k']), '+0.0', 'OPEN %s' % ('LONG' if d_ > 0 else 'SHORT'),
          '%.6f' % p0, '+0.0000')]
        + [(U(q), mn(q), t, '%.6f' % float(PX[q]), pct(q)) for q, t in sorted(L['tr'])]
        + [(U(j), mn(j), 'EXIT — final stalled on ws%d' % r_, '%.6f' % float(PX[j]), pct(j))])
    rows = []
    for t in sorted(set(C.ALL_TF)):
        if t <= r_ or t > min(r_ + 6, L['aceil']): continue
        mt = ('YES' if MOMT[t][d_][j] else 'no') if t in MOMT else '(no mask yet)'
        rows.append(('ws%d' % t, str(t - r_), '%.2f' % float(C.RL[t][j]),
                     'YES' if ((float(C.RL[t][j]) >= SC.HI) if d_ > 0 else
                               (float(C.RL[t][j]) <= SC.LO)) else 'no',
                     mt, 'YES' if int(RPRED[t][j]) == (1 if d_ > 0 else -1) else 'no',
                     'YES' if t - r_ <= C.LIN_HOP else 'no'))
    box(('the line', 'rungs up', 'r at the exit', 'oob?', 'momentum?', 'r-pred?',
         'inside lin_hop 2?'), rows)
