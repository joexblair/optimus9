"""WHERE THE DRAWDOWN SITS, FOR THE LEGS THAT RELY ON 2.something. 1008.

Joe 1008: *"my goal is not to reduce the 2.5 based on reports. my goal is to move the opens that are
reliant on 2.something to locations that allow us to reduce the stop, to increase the overall
profitably with less risk"*.

So the question is not what stop value scores best. It is: FOR A LEG THAT ONLY SURVIVES BECAUSE THE
STOP IS WIDE, WHERE WOULD A BETTER OPEN HAVE BEEN?

The first thing that decides that is WHEN the drawdown happens:

  MAE BEFORE MFE   the open is too EARLY. Price went against the trade first and the move came
                   later. A later open catches the same move with less drawdown - the walk's job.
  MFE BEFORE MAE   the open was fine and the trade GAVE BACK. A later open does not help; an
                   earlier EXIT does.

MEASURED PER LEG, on the 1.06 build (mae_stop_pct 2.5, reent_xwob 18, x-cross OFF, rest banked),
for every leg that survived with measured MAE above 1.90 - the band that cannot live under a 2.0
stop:

  mae min       minutes from the open to the ADVERSE extreme
  mfe min       minutes from the open to the FAVOURABLE extreme
  order         which came first
  the better open  the bar inside the leg's own span where the trade's MAE would have been
                   SMALLEST while keeping a positive outcome at the leg's own exit - measured, not
                   proposed, so Joe can see what a relocation is worth before any mech is built
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

assert C.NOX, 'run with W_NOX=1'
SC, PX, box, U = C.SC, C.PX, C.box, C.SC.U
N = len(SC.ts); FEE = 0.11
BAND = 1.90
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
C.MAE_STOP = 2.5
_idx = np.arange(N); fin = np.isfinite(T.X1) & np.isfinite(T.R1)
def holds(m, w):
    run = (_idx + 1) - np.maximum.accumulate(np.where(m, 0, _idx + 1))
    h = run >= w; cf = h & ~np.r_[False, h[:-1]]
    return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
T.XWOB = 18
T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & fin, 18)]
                   + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & fin, 18)], key=lambda z: z[1])

legs = []; k, d = 1, +1; g = 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    p0 = float(PX[k]); sgn = 1 if d > 0 else -1
    seg = PX[k:xk + 1]
    ok = np.isfinite(seg) & (seg > 0)
    rel = (seg - p0) / p0 * 100.0 * sgn
    rel = np.where(ok, rel, 0.0)
    iw = int(np.argmin(rel)); ib = int(np.argmax(rel))
    legs.append(dict(day=DAYOF(k), open=k, exit=xk, d=d, why=why, side='LONG' if d > 0 else 'SHORT',
                     mae=-float(rel[iw]), mfe=float(rel[ib]),
                     maebar=k + iw, mfebar=k + ib,
                     real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d

sel = [r for r in legs if r['why'] != 'mae breach' and r['mae'] > BAND]
mn = lambda a, b: (int(SC.ts[b]) - int(SC.ts[a])) / 60000.0
for r in sel:
    r['tmae'] = mn(r['open'], r['maebar']); r['tmfe'] = mn(r['open'], r['mfebar'])
    r['hold'] = mn(r['open'], r['exit'])
    r['order'] = 'MAE first — the open is EARLY' if r['maebar'] < r['mfebar'] \
        else 'MFE first — it GAVE BACK'
    # the best open inside the leg's own span: the bar that minimises the MAE while still
    # finishing positive at the leg's own exit bar
    best = None
    pe = float(PX[r['exit']]); sg = r['d']
    for j in range(r['open'], r['exit']):
        pj = float(PX[j])
        if not np.isfinite(pj) or pj <= 0: continue
        out = (pe - pj) / pj * 100.0 * sg
        if out <= 0: continue
        seg = PX[j:r['exit'] + 1]
        rel = (seg - pj) / pj * 100.0 * sg
        m = -float(np.nanmin(rel))
        if best is None or m < best[1]: best = (j, m, out)
    r['best'] = best

print('# THE LEGS THAT RELY ON A STOP ABOVE %.2f — 1.06 build, %d of %d legs'
      % (BAND, len(sel), len(legs)), flush=True)
box(('the measure', 'value'),
    [('legs surviving with MAE > %.2f' % BAND, str(len(sel))),
     ('their summed realised', '%+.4f' % sum(r['real'] for r in sel)),
     ('of them, MAE BEFORE MFE — the open is early', '**%d**'
      % sum(1 for r in sel if r['maebar'] < r['mfebar'])),
     ('of them, MFE BEFORE MAE — it gave back', str(sum(1 for r in sel
                                                        if r['maebar'] >= r['mfebar']))),
     ('median minutes from open to the adverse extreme', '%.1f'
      % sorted(r['tmae'] for r in sel)[len(sel) // 2]),
     ('median minutes from open to the favourable extreme', '%.1f'
      % sorted(r['tmfe'] for r in sel)[len(sel) // 2]),
     ('legs where a better open exists inside their own span',
      '**%d**' % sum(1 for r in sel if r['best'])),
     ('their median best-open MAE', '%.4f'
      % sorted(r['best'][1] for r in sel if r['best'])[sum(1 for r in sel if r['best']) // 2]),
     ('their median ACTUAL MAE', '%.4f' % sorted(r['mae'] for r in sel)[len(sel) // 2])])

sel.sort(key=lambda r: -r['mae'])
print('\n# EVERY ONE, WORST DRAWDOWN FIRST')
box(('day', 'side', 'open', 'exit', 'hold min', 'why', 'MAE', 'at +min', 'MFE', 'at +min',
     'which came first', 'realised', 'the lowest-MAE open in its own span', 'that open\'s MAE',
     'and its outcome'),
    [(r['day'], r['side'], U(r['open']), U(r['exit']), '%.1f' % r['hold'], r['why'],
      '%.4f' % r['mae'], '%.1f' % r['tmae'], '%.4f' % r['mfe'], '%.1f' % r['tmfe'],
      r['order'], '%+.4f' % r['real'],
      U(r['best'][0]) if r['best'] else 'none',
      '%.4f' % r['best'][1] if r['best'] else '—',
      '%+.4f' % r['best'][2] if r['best'] else '—') for r in sel])
