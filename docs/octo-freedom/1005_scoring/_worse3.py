"""THE FIRST 3 LEGS THE NAKED WALK MADE WORSE — the timestamped event tables. 1008.

Joe 1008: *"in the normal timestmaped table, show me the first 3 that made the outcome worse"*.

WORSE = the walk landed on an entry that is WORSE than the bar the chain would have opened on, in
the leg's own native side's favour. That is the thing the mech exists to improve, so it is the
thing measured. The legs are taken in CHAIN ORDER and the first 3 are printed.

TWO pct COLUMNS, both fields of the same bar:
  pct from walk start   the move from the bar the baseline would have entered on. Only this column
                        shows what walking cost. It is NOT P&L above the ENTER row - nothing is open.
  pct from entry        the position's own P&L. Blank until the ENTER row, because there is no
                        position until then.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T
import _nakedchain as NK

SC, PX, box = C.SC, C.PX, C.box
U = SC.U
DAYOF = lambda k: datetime.datetime.utcfromtimestamp(int(SC.ts[k]) / 1000).strftime('%Y-%m-%d')

rows = NK.run_chain_naked(T.gate_A, 'end')
legs = [r for r in rows if not r['brk']]
worse = [r for r in legs if r['imp'] < 0]
print('\n# %d of the %d arm-1 legs landed on a WORSE entry than their walk-start bar.'
      % (len(worse), len(legs)))
box(('leg', 'side', 'the walk starts', 'frame dr', 'entry bar', 'naked min', 'entry better by %',
     'exit', 'why'),
    [(str(r['leg']), r['side'], '%s %s' % (DAYOF(r['walkfrom'])[5:], U(r['walkfrom'])),
      '%+d' % r['frame'], U(r['land']), '%.1f' % r['naked'], '%+.4f' % r['imp'],
      U(r['exit']), r['why']) for r in worse])

for r in worse[:3]:
    k, lb, xk, d = r['walkfrom'], r['land'], r['exit'], r['d']
    fr = r['frame']; sgn = 1 if d > 0 else -1
    p_start = float(PX[k]); p_ent = float(PX[lb])
    _, lw, ltr = NK.naked_walk(k, fr)
    _, why, mae, cb, hand, ltr2 = C.run_leg(lb, d)
    ps = lambda j: '%+.4f' % ((float(PX[j]) - p_start) / p_start * 100.0 * sgn)
    pe = lambda j: '%+.4f' % ((float(PX[j]) - p_ent) / p_ent * 100.0 * sgn)
    mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[k])) / 60000.0)
    print('\n\n## LEG %d — %s   walk starts %s %s   pxs %.6f   walk frame dr %+d'
          % (r['leg'], r['side'], DAYOF(k)[5:], U(k), p_start, fr))
    tbl = [(U(k), '+0.0', 'WALK STARTS — naked, nothing open. The baseline opens %s HERE.' % r['side'],
            '%.6f' % p_start, '+0.0000', '—')]
    tbl += [(U(j), mn(j), 'walk: %s' % lab, '%.6f' % float(PX[j]), ps(j), '—') for j, lab in ltr]
    tbl += [(U(lb), mn(lb), 'LANDING — %s' % lw, '%.6f' % p_ent, ps(lb), '—')]
    tbl += [(U(lb), mn(lb), 'ENTER %s' % r['side'], '%.6f' % p_ent, ps(lb), '+0.0000')]
    tbl += [(U(j), mn(j), lab, '%.6f' % float(PX[j]), ps(j), pe(j)) for j, lab in ltr2]
    tbl += [(U(xk), mn(xk), 'EXIT — %s' % why, '%.6f' % float(PX[xk]), ps(xk), pe(xk))]
    box(('ts', '+min', 'event', 'pxs', 'pct from walk start', 'pct from entry'), tbl)
    base_x, base_w, base_mae, _, _, _ = C.run_leg(k, d)
    print('- the baseline leg from %s, same native side, exits %s on %s at %+.4f.'
          % (U(k), U(base_x) if base_x else '—', base_w,
             ((float(PX[base_x]) - p_start) / p_start * 100.0 * sgn) if base_x else float('nan')))
    print('- the walked leg realised %+.4f from its own entry, and %+.4f measured from %s.'
          % (r['real'], (float(PX[xk]) - p_start) / p_start * 100.0 * sgn, U(k)))
