"""WHAT THE WALK LEFT ON THE TABLE, IN pxs. 1009.

Joe 1009: *"the results are measurable - use pxs diff"*, after I called the 69.9% an opportunity
rather than a result.

AT EACH STALL where a line inside lin_hop was already r-pred, the baton would have taken that line
and ridden until THAT line stalls. So the span is defined by the mech, not chosen by me: from the
stall bar to the first bar the new rider stalls on the leg's side. No cap, no horizon.

Measured per stall, in the leg's own direction:
  the pxs diff   what the extended ride would have returned
  the MAE        the worst drawdown inside that span, which the 2.50 stop would have met
  stopped?       whether the extension would have breached `mae_stop_pct` before the new stall

THE HONEST BOUND: this is ONE extra hop, measured against the tape. It is not the rebuilt chain -
every changed exit bar moves the next leg's open, and that reshuffle is only visible in a full run.
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
RR, PRED = {}, {}
for t in list(C.ALL_TF):
    r = np.asarray(SC.LD(t * 60, 'r'), float)[:N]
    m = np.asarray(SC.LD(t * 60, 'm'), float)[:N]
    g = np.asarray(SC.LD(t * 60, 'Mage'), float)[:N]
    RR[t] = r
    PRED[t] = predict_breach(r, m, g, BHI, BLO, FENCE_HI, FENCE_LO)
TFS = sorted(RR)
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
    L['next_real'] = legs[i + 1]['real'] if i + 1 < len(legs) else None
fs = [L for L in legs if L['why'] == 'final stalled' and L['rider'] is not None]

rows = []
for L in fs:
    j, d_, r_, ac = L['xk'], L['d'], L['rider'], L['aceil']
    cap = min(r_ + C.LIN_HOP, ac)
    cands = [t for t in TFS if r_ < t <= cap and rp(t, j, d_)]
    if not cands: continue
    nr = max(cands)                      # the baton takes the highest qualifying line, as it does today
    st = C.ST[(nr, d_)]
    e = None
    for q in range(j + 1, N):
        if st[q]: e = q; break
    if e is None: continue
    p0 = float(PX[j]); s = 1 if d_ > 0 else -1
    seg = np.asarray(PX[j:e + 1], float); ok = np.isfinite(seg) & (seg > 0)
    rel = np.where(ok, (seg - p0) / p0 * 100.0 * s, np.nan)
    mae = -float(np.nanmin(rel)); mfe = float(np.nanmax(rel))
    stop = mae > C.MAE_STOP
    # a stopped extension realises the knob, per Joe 1007
    got = -C.MAE_STOP if stop else float(rel[-1])
    rows.append(dict(day=DAY(j), bar=j, d=d_, rider=r_, nr=nr, end=e,
                     mins=(int(SC.ts[e]) - int(SC.ts[j])) / 60000.0,
                     diff=float(rel[-1]), got=got, mae=mae, mfe=mfe, stop=stop,
                     nb=L['next_breach'], nxt=L['next_real']))
print('# %d stalls had an r-pred line inside lin_hop with a later stall to ride to\n' % len(rows),
      flush=True)
for nm, sel in (('EVERY ONE', rows),
                ('THE ONES THAT HANDED INTO A BREACH', [x for x in rows if x['nb']])):
    if not sel: continue
    n = len(sel)
    D = np.array([x['got'] for x in sel], float)
    RAW = np.array([x['diff'] for x in sel], float)
    print('\n# %s — %d stalls' % (nm, n))
    box(('the measure', 'value'),
        [('summed pxs diff of the extended ride, stop rule applied', '%+.4f' % D.sum()),
         ('  the same without the stop rule', '%+.4f' % RAW.sum()),
         ('mean per stall', '%+.4f' % D.mean()),
         ('median', '%+.4f' % float(np.median(D))),
         ('positive', '%d = %.1f%%' % (int((D > 0).sum()), 100.0 * (D > 0).sum() / n)),
         ('extensions that would have breached the %.2f stop' % C.MAE_STOP,
          '%d = %.1f%%' % (sum(1 for x in sel if x['stop']),
                           100.0 * sum(1 for x in sel if x['stop']) / n)),
         ('median ride length', '%.1f min' % float(np.median([x['mins'] for x in sel]))),
         ('median MFE inside the ride', '%.4f' % float(np.median([x['mfe'] for x in sel]))),
         ('median MAE inside the ride', '%.4f' % float(np.median([x['mae'] for x in sel]))),
         ('what the chain ACTUALLY got on the next leg',
          '%+.4f' % sum(x['nxt'] for x in sel if x['nxt'] is not None)),
         ('one extra fee per extension — it replaces a leg boundary', 'none; the ride replaces the '
          'next leg\'s open, so the fee count is unchanged')])
print('\n# THE FIRST 20, OLDEST FIRST')
box(('day', 'the stall', 'dr', 'rider was', 'baton would take', 'rides to', 'min',
     'pxs diff', 'scored', 'MAE', 'MFE', 'stopped?', 'the next leg got'),
    [(x['day'], U(x['bar']), '%+d' % x['d'], 'ws%d' % x['rider'], 'ws%d' % x['nr'], U(x['end']),
      '%.1f' % x['mins'], '%+.4f' % x['diff'], '%+.4f' % x['got'], '%.4f' % x['mae'],
      '%.4f' % x['mfe'], 'YES' if x['stop'] else 'no',
      '%+.4f' % x['nxt'] if x['nxt'] is not None else '—') for x in rows[:20]])
