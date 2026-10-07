"""THE WHOLE 1 TO 11 CHAIN, one table, with the running MAE/MFE. 09-25. 1007.

Joe 1007: *"the whole 1 to 11 chain thanks"* / *"when you stop, provide a table that shows all legs
and the running MAEMFE. if mae1.1 was hit, then MFE is zero and MAE is 1.1"*.

TWO SEGMENTS, because the chain broke once:
  legs 1-7    from the 02:48:50 octo-sig. Ends 07:51:05 on ws1's stall.
  THE BREAK   07:51:05 -> 08:10:00. Joe 1007 picked the reopen by hand: *"07:51 is stopped, so the
              chain is broken and needs a new open bar. I've chosen 08:10 as the open bar"*. Not a
              leg, and shown as a break row so the gap is not hidden inside a hold time.
  legs 8-11   from 08:10:00. Ends 11:07:45 on the mae 1.1 stop.

THE MECH IS ONE BUILD ACROSS BOTH: `_chain10.run_leg` - the lineage walk until the >ws12 handover,
the >ws12 oob mech after it, the mae 1.1 stop over everything. Imported, not copied, so the legs
here and the legs in `_chain10.py` cannot drift.

SCORING: a leg that hit the stop scores MFE 0.0000 and MAE 1.1000 - the KNOB value, Joe's rule, not
the measured overshoot. Its `realised` keeps the measured figure.
"""
import os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, PX, box, MAE_STOP = C.SC, C.PX, C.box, C.MAE_STOP
D = C.D
SEGS = [('02:48:50', +1, 7), ('08:10:00', +1, 0)]      # start, side, max legs (0 = until the stop)

def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]
    seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return 0.0, 0.0
    p_ = float(PX[s_])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

ROWS = []; n = 0; prev_exit = None
for si, (st, sd, ml) in enumerate(SEGS):
    k = SC.K('%s %s' % (D, st)); d = sd
    if prev_exit is not None:
        ROWS.append(dict(brk=True, a=prev_exit, b=k))
    seg_n = 0
    while True:
        xk, why, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None:
            break
        n += 1; seg_n += 1
        p0 = float(PX[k]); sgn = 1 if d > 0 else -1
        real = (float(PX[xk]) - p0) / p0 * 100.0 * sgn
        ROWS.append(dict(brk=False, leg=n, side='LONG' if d > 0 else 'SHORT', open=k, exit=xk,
                         real=real, why=why, hand=hand, d=d))
        prev_exit = xk
        if why == 'mae breach':
            break
        if ml and seg_n >= ml:
            break
        k = xk; d = -d

print('\n# THE WHOLE CHAIN, LEGS 1 TO %d, WITH THE RUNNING MAE / MFE' % n)
rows = []; rA = 0.0; rF = 0.0; rR = 0.0
for r in ROWS:
    if r['brk']:
        rows.append(('—', 'BREAK', SC.U(r['a']), SC.U(r['b']),
                     '%.1f' % ((int(SC.ts[r['b']]) - int(SC.ts[r['a']])) / 60000.0),
                     'chain broken, Joe picked the reopen', '—', '—', '—', '—',
                     '%.4f' % rA, '%.4f' % rF, '%+.4f' % rR))
        continue
    if r['why'] == 'mae breach':
        a_, f_ = MAE_STOP, 0.0
    else:
        a_, f_ = mm(r['open'], r['exit'], r['d'])
    rA += a_; rF += f_; rR += r['real']
    rows.append((str(r['leg']), r['side'], SC.U(r['open']), SC.U(r['exit']),
                 '%.1f' % ((int(SC.ts[r['exit']]) - int(SC.ts[r['open']])) / 60000.0),
                 r['why'], '%.4f' % a_, '%.4f' % f_,
                 ('%.2f' % (f_ / a_)) if a_ > 0 else 'inf',
                 '%+.4f' % r['real'], '%.4f' % rA, '%.4f' % rF, '%+.4f' % rR))
box(('leg', 'side', 'open', 'exit', 'hold min', 'why', 'leg MAE', 'leg MFE', 'MFE/MAE',
     'realised', 'running MAE', 'running MFE', 'running realised'), rows)

L = [r for r in ROWS if not r['brk']]
print('\n- %d legs, %d positive, %d handed over to the >ws12 mech, %d stopped on mae %.2f'
      % (len(L), sum(1 for r in L if r['real'] > 0), sum(1 for r in L if r['hand']),
         sum(1 for r in L if r['why'] == 'mae breach'), MAE_STOP))
print('- running MAE %.4f, running MFE %.4f, ratio %.2f, running realised %+.4f'
      % (rA, rF, rF / rA if rA else float('nan'), rR))
print('- capture: realised %+.4f of MFE %.4f = %.1f%%' % (rR, rF, rR / rF * 100.0 if rF else 0.0))
w = {}
for r in L: w[r['why']] = w.get(r['why'], 0) + 1
print('\n# HOW EVERY LEG EXITED')
box(('why', 'legs', 'realised'),
    [(kk, str(w[kk]), '%+.4f' % sum(r['real'] for r in L if r['why'] == kk))
     for kk in sorted(w, key=lambda z: -w[z])])
