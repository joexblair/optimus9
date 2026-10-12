"""THE 6.1-MINUTE WINDOW BETWEEN THE CEILING RAISE AND THE HANDOVER. 1009.

Joe 1009, on the 07-15 03:13:15 SHORT: *"03:26 should be passing to >ws12 oob, not to ceil 24"*.

Two mechs key off the SAME event - ws12r crossing into oob:
  the CEILING RAISE  immediate. Joe's ceil_hi ruling, *"if ws12r crosses into oob, then extend the
                     max TF to ws23"*.
  the HANDOVER       delayed by oob_gate_bars 72 = 6.1 min of dwell.

So between them the baton may climb ABOVE ws12, into the range the >ws12 mech owns. This counts it.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

SC, box, U, PX = C.SC, C.box, C.SC.U, C.PX
N = len(SC.ts)
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                datetime.timezone.utc).strftime('%Y-%m-%d')
_i = np.arange(N); fin = np.isfinite(T.X1) & np.isfinite(T.R1)
def holds(m, w):
    run = (_i + 1) - np.maximum.accumulate(np.where(m, 0, _i + 1))
    h = run >= w; cf = h & ~np.r_[False, h[:-1]]
    return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
T.XWOB = 18
T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & fin, 18)]
                   + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & fin, 18)], key=lambda z: z[1])
legs = []; k, d, g = 1, +1, 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    ceilbar = next((j for j, t in tr if 'CEILING' in t), None)
    handbar = next((j for j, t in tr if t.startswith('HANDOVER')), None)
    above = [(j, int(t.split('ws')[1].split(' ')[0]))
             for j, t in tr
             if (t.startswith('baton -> ws') or t.startswith('KICKSTART'))
             and int((t.split('baton -> ws')[1] if 'baton -> ws' in t
                      else t.split('rider ws')[1]).split(' ')[0]) > C.BASE_HI]
    p0 = float(PX[k]); s = 1 if d > 0 else -1
    legs.append(dict(k=k, xk=xk, d=d, why=why, ceil=ceilbar, hand=handbar, above=above,
                     real=(float(PX[xk]) - p0) / p0 * 100.0 * s))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d
cr = [L for L in legs if L['ceil'] is not None]
print('# %d legs, %d raised the ceiling\n' % (len(legs), len(cr)), flush=True)
c = collections.Counter(); rows = []
for L in cr:
    inwin = [(j, t) for j, t in L['above']
             if j >= L['ceil'] and (L['hand'] is None or j < L['hand'])]
    aft = [(j, t) for j, t in L['above'] if L['hand'] is not None and j >= L['hand']]
    if inwin:
        c['the baton climbed ABOVE ws%d inside the window' % C.BASE_HI] += 1
        rows.append((DAY(L['k']), U(L['k']), '%+d' % L['d'], U(L['ceil']),
                     U(L['hand']) if L['hand'] else 'never',
                     '%.1f' % ((int(SC.ts[L['hand']]) - int(SC.ts[L['ceil']])) / 60000.0)
                     if L['hand'] else '—',
                     ', '.join('ws%d at %s' % (t, U(j)) for j, t in inwin),
                     '%.1f' % ((int(SC.ts[inwin[0][0]]) - int(SC.ts[L['ceil']])) / 60000.0),
                     str(max(t for _, t in inwin)), L['why'], '%+.4f' % L['real']))
    else:
        c['the baton stayed at or below ws%d in the window' % C.BASE_HI] += 1
    if aft: c['  it also climbed above after the handover'] += 1
    if L['hand'] is None: c['  this leg never handed over at all'] += 1
box(('the reading', 'legs', 'share of the %d' % len(cr)),
    [(kk, str(v), '%.1f%%' % (100.0 * v / len(cr))) for kk, v in sorted(c.items())])
if rows:
    print('\n# EVERY LEG WHERE THE BATON CLIMBED ABOVE ws%d BEFORE THE HANDOVER, %d of them'
          % (C.BASE_HI, len(rows)))
    box(('day', 'the leg opens', 'dr', 'the ceiling rose', 'the handover', 'the window min',
         'what the baton took', 'first climb at +min', 'highest line', 'the exit', 'realised'),
        rows)
    r = np.array([float(x[10]) for x in rows])
    box(('those %d legs' % len(rows), 'value'),
        [('summed realised', '%+.4f' % r.sum()), ('mean', '%+.4f' % r.mean()),
         ('positive', '%d = %.1f%%' % (int((r > 0).sum()), 100.0 * (r > 0).sum() / len(r)))])
