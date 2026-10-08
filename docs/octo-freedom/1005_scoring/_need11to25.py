"""THE 2-DAY WINDOW WITH THE MOST TRADES THAT NEEDED 1.1 -> 2.5 TO MAKE PROFIT. 1008.

Joe 1008: *"reducing the stop loss is my goal for today - I need a 2 day window that has the most
trades that needed to rely on 1.1 to 2.5 to make profit"*.

THE DEFINITION, exactly as he put it - a trade NEEDED the widening when:
  its own measured MAE is MORE than 1.10  - a 1.10 stop would have killed it
  AND at most 2.50                        - a 2.50 stop kept it; past 2.50 it stopped anyway
  AND it realised MORE than 0             - it went on to PROFIT

This is tighter than §27's version, which counted every surviving leg past 1.10 whether or not it
came home green. Those 331 legs summed to -22.6437. Joe is asking for the PROFITABLE subset.

RUN AT THE CONFIG HE IS WORKING FROM - the MFE/MAE 1.06 build: `mae_stop_pct` 2.5, `reent_xwob` 18,
the walk's x-cross exit OFF, everything else banked. It is the build whose stop he wants to narrow,
so it is the one the legs must come from.

THE WINDOW IS 2 CONSECUTIVE CALENDAR DAYS. Ranked by COUNT first, as asked, with their realised
alongside so the count is never read on its own.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

assert C.NOX, 'run me with W_NOX=1 - the x-cross exit must be OFF for the 1.06 build'
SC, PX, box, U = C.SC, C.PX, C.box, C.SC.U
N = len(SC.ts); FEE = 0.11
LO_STOP, HI_STOP = 1.10, 2.50
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
C.MAE_STOP = HI_STOP
_idx = np.arange(N); fin = np.isfinite(T.X1) & np.isfinite(T.R1)
def holds(m, w):
    run = (_idx + 1) - np.maximum.accumulate(np.where(m, 0, _idx + 1))
    h = run >= w; cf = h & ~np.r_[False, h[:-1]]
    return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
T.XWOB = 18
T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & fin, 18)]
                   + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & fin, 18)], key=lambda z: z[1])
print('# the 1.06 build: mae_stop_pct %.2f, reent_xwob %d, x-cross OFF, rest banked'
      % (C.MAE_STOP, T.XWOB), flush=True)

def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]; seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return 0.0, 0.0
    p_ = float(PX[s_])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

legs = []; k, d = 1, +1; g = 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    p0 = float(PX[k]); sgn = 1 if d > 0 else -1
    a_, f_ = mm(k, xk, d)
    legs.append(dict(day=DAYOF(k), open=k, exit=xk, d=d, why=why, mae=mae, mfe=f_, hand=hand,
                     side='LONG' if d > 0 else 'SHORT',
                     real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn, tr=tr))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d

need = [r for r in legs
        if r['why'] != 'mae breach' and LO_STOP < r['mae'] <= HI_STOP and r['real'] > 0]
print('\n# THE POPULATION')
box(('the measure', 'value'),
    [('all legs', str(len(legs))),
     ('legs with measured MAE in (%.2f, %.2f]' % (LO_STOP, HI_STOP),
      str(sum(1 for r in legs if r['why'] != 'mae breach'
              and LO_STOP < r['mae'] <= HI_STOP))),
     ('  of those, PROFITABLE — "needed 1.1 to 2.5 to make profit"', '**%d**' % len(need)),
     ('  of those, a loss', str(sum(1 for r in legs if r['why'] != 'mae breach'
                                    and LO_STOP < r['mae'] <= HI_STOP and r['real'] <= 0))),
     ('the profitable ones summed realised', '%+.4f' % sum(r['real'] for r in need)),
     ('the whole chain gross', '%+.4f' % sum(r['real'] for r in legs)),
     ('their share of the gross', '%.1f%%'
      % (100.0 * sum(r['real'] for r in need) / sum(r['real'] for r in legs))),
     ('their median measured MAE', '%.4f' % sorted(r['mae'] for r in need)[len(need) // 2]),
     ('their median MFE', '%.4f' % sorted(r['mfe'] for r in need)[len(need) // 2])])

pn = collections.Counter(); pv = collections.defaultdict(float)
for r in need:
    pn[r['day']] += 1; pv[r['day']] += r['real']
days = sorted({r['day'] for r in legs})
wins = []
for i in range(len(days) - 1):
    w = days[i:i + 2]
    wins.append((sum(pn[x] for x in w), sum(pv[x] for x in w), w))
wins.sort(key=lambda z: (-z[0], -z[1]))
print('\n# THE 2-DAY WINDOWS, RANKED BY HOW MANY NEEDED IT')
box(('the window', 'legs that needed 1.1->2.5', 'their realised', 'the window\'s whole realised',
     'their share'),
    [('%s + %s' % (w[0], w[1]), str(n), '%+.4f' % v,
      '%+.4f' % sum(r['real'] for r in legs if r['day'] in w),
      '%.0f%%' % (100.0 * v / sum(r['real'] for r in legs if r['day'] in w))
      if sum(r['real'] for r in legs if r['day'] in w) else '—')
     for n, v, w in wins[:10]])

TOP = wins[0][2]
print('\n# %s + %s — EVERY LEG THAT NEEDED 1.1 -> 2.5 TO MAKE PROFIT' % (TOP[0], TOP[1]))
box(('day', 'side', 'open', 'exit', 'hold min', 'why', 'handover', 'measured MAE', 'MFE',
     'MFE/MAE', 'realised'),
    [(r['day'], r['side'], U(r['open']), U(r['exit']),
      '%.1f' % ((int(SC.ts[r['exit']]) - int(SC.ts[r['open']])) / 60000.0), r['why'],
      U(r['hand']) if r['hand'] else '—', '%.4f' % r['mae'], '%.4f' % r['mfe'],
      '%.2f' % (r['mfe'] / r['mae']), '%+.4f' % r['real'])
     for r in need if r['day'] in TOP])

print('\n# AND EVERY OTHER LEG IN THAT WINDOW, FOR THE CONTEXT')
box(('day', 'side', 'open', 'exit', 'hold min', 'why', 'measured MAE', 'MFE', 'realised',
     'needed 1.1->2.5?'),
    [(r['day'], r['side'], U(r['open']), U(r['exit']),
      '%.1f' % ((int(SC.ts[r['exit']]) - int(SC.ts[r['open']])) / 60000.0), r['why'],
      '%.4f' % r['mae'], '%.4f' % r['mfe'], '%+.4f' % r['real'],
      'YES' if r in need else '')
     for r in legs if r['day'] in TOP])
