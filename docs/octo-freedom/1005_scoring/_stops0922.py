"""EVERY STOP ON 2026-09-22, CHAIN 0. 1008.

Joe 1008: *"sticking with chain 0, pick the day in september or october that has the most stops and
show them in the standard timestamped-rows event table"*.

2026-09-22 is that day: **12 stops on 18 legs**, realised -7.4220, the most of any September or
October day in the 95-day run. The next are 09-21 at 11 and 09-18 / 09-29 at 9.

CHAIN 0 is the banked mech, no entry-optimising walk: the lineage walk with the baton passing on
**oob** and exiting on **x-cross** or **final stalled**, the >ws12 oob mech taking the exit after the
handover, and the 1.10 MAE stop per leg. Gate A's ws1x hold / `reent_xwob` 6 router finds
the re-entry after each stop.

THE CHAIN IS SEEDED AT THE TAPE'S FIRST BAR, as the 95-day run was, so these legs are the ones the
full-window chain actually produced on that day.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

SC, PX, box = C.SC, C.PX, C.box
N = len(SC.ts); U = SC.U
MAE_STOP = C.MAE_STOP
DAY = os.environ.get('W_DAY2', '2026-09-22')
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')

def chain0(gate, seed, last):
    rows = []; n = 0
    k, d, seg_n = seed, +1, 0
    while True:
        xk, why, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None: break
        n += 1
        p0 = float(PX[k]); sgn = 1 if d > 0 else -1
        rows.append(dict(brk=False, leg=n, side='LONG' if d > 0 else 'SHORT', open=k, exit=xk,
                         real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn, why=why, hand=hand, d=d,
                         mae=mae, tr=tr))
        if why == 'mae breach':
            rb, cf, sd = T.find_reentry(xk, gate, last)
            if cf is None:
                rows.append(dict(brk=True, a=xk, b=None, rb=None)); break
            rows.append(dict(brk=True, a=xk, b=cf, rb=rb, sd=sd))
            k, d, seg_n = cf, sd, 0
            continue
        if xk >= last: break
        k = xk; d = -d
    return rows

print('# chain 0 over the whole tape, %d bars ...' % N, flush=True)
R = chain0(T.gate_A, 1, N - 1)
legs = [r for r in R if not r['brk'] and DAYOF(r['open']) == DAY]
stops = [r for r in legs if r['why'] == 'mae breach']

def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]; seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return 0.0, 0.0
    p_ = float(PX[s_])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

print('\n# %s — EVERY LEG, AND WHICH ONES STOPPED' % DAY)
rA = rF = rR = 0.0
rows = []
for r in legs:
    a_, f_ = (MAE_STOP, 0.0) if r['why'] == 'mae breach' else mm(r['open'], r['exit'], r['d'])
    rA += a_; rF += f_; rR += r['real']
    rows.append((str(r['leg']), r['side'], U(r['open']),
                 ('%s %s' % (DAYOF(r['exit'])[5:], U(r['exit'])))
                 if DAYOF(r['exit']) != DAY else U(r['exit']),
                 '%.1f' % ((int(SC.ts[r['exit']]) - int(SC.ts[r['open']])) / 60000.0),
                 r['why'], SC.U(r['hand']) if r['hand'] else '—',
                 '%.4f' % a_, '%.4f' % f_, '%+.4f' % r['real'],
                 '%.4f' % rA, '%.4f' % rF, '%+.4f' % rR))
box(('leg', 'side', 'open', 'exit', 'hold min', 'why', 'handover', 'leg MAE', 'leg MFE',
     'realised', 'running MAE', 'running MFE', 'running realised'), rows)
print('- a stopped leg scores MAE %.4f and MFE 0.0000, Joe 1007.' % MAE_STOP)
print('- %d legs, %d stops, %d positive.'
      % (len(legs), len(stops), sum(1 for r in legs if r['real'] > 0)))

print('\n# THE %d STOPS, AND THE RE-ENTRY THAT FOLLOWED EACH' % len(stops))
rows = []
for r in R:
    if not r['brk'] or r.get('a') is None: continue
    if DAYOF(r['a']) != DAY: continue
    rows.append((U(r['a']), ('%s %s' % (DAYOF(r['b'])[5:], U(r['b']))) if r.get('b') else 'NONE',
                 '%.1f' % ((int(SC.ts[r['b']]) - int(SC.ts[r['a']])) / 60000.0)
                 if r.get('b') else '—',
                 U(r['rb']) if r.get('rb') else '—'))
box(('the stop bar', 're-entry conf', 'gap min', 'the ws1x return bar'), rows)

print('\n\n' + '=' * 78)
print('# %s — THE %d STOPPED LEGS, SEQUENTIALLY' % (DAY, len(stops)))
print('=' * 78)
for r in stops:
    k, xk, d = r['open'], r['exit'], r['d']
    p0 = float(PX[k])
    pct = lambda j: '%+.4f' % ((float(PX[j]) - p0) / p0 * 100.0 * (1 if d > 0 else -1))
    mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[k])) / 60000.0)
    print('\n## %s %s   %s   open %s   pxs %.6f'
          % (DAYOF(k)[5:], U(k), r['side'], U(k), p0))
    box(('ts', '+min', 'event', 'pxs', 'pct'),
        [(U(k), '+0.0', 'OPEN %s' % r['side'], '%.6f' % p0, '+0.0000')]
        + [(U(j), mn(j), lab, '%.6f' % float(PX[j]), pct(j)) for j, lab in r['tr']]
        + [(U(xk), mn(xk), 'EXIT — mae breach', '%.6f' % float(PX[xk]), pct(xk))])
