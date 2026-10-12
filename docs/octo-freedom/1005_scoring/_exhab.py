"""THE EXHAUSTION WINDOW AND HOLD, A/B. 1009.

Joe 1009: *"apply the 6 minute dwell gate to ws12r oob / if ws12x crosses ws12r during the dwell
period, reverse the trade"* and *"let's use 6 - it's safer"*.

  seam 4   the 1/4 seam window 3.0 min, hold 4 bars. AS FIRST BUILT.
  seam 6   the same window, the new hold.
  dwell 4  the full 6.1-min dwell, the old hold.
  dwell 6  JOE'S SPEC.

The ws60r gate is ON because the exhaustion path only exists inside it, and x-cross is suppressed
per his standing 1009 ruling. The seam-4 arm is the CONTROL for the pair.
"""
import os, sys, importlib, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1005_scoring')

def walk(win, hold):
    os.environ['W_EXH_WIN'] = win; os.environ['XWOB_WS12X'] = str(hold)
    os.environ['W_DGATE'] = 'traj'; os.environ['W_NOX'] = '1'
    os.environ['W_BATON'] = 'oob'
    for m in ('_chain10', '_trajmech', '_chain_2day', '_momtrue'):
        sys.modules.pop(m, None)
    C = importlib.import_module('_chain10'); T = importlib.import_module('_chain_2day')
    N = len(C.SC.ts); _i = np.arange(N); fin = np.isfinite(T.X1) & np.isfinite(T.R1)
    def holds(m, w):
        run = (_i + 1) - np.maximum.accumulate(np.where(m, 0, _i + 1))
        h = run >= w; cf = h & ~np.r_[False, h[:-1]]
        return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
    T.XWOB = 18
    T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & fin, 18)]
                       + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & fin, 18)],
                       key=lambda z: z[1])
    k, d, g = 1, +1, 0
    gross = 0.0; n = 0; why = collections.Counter(); cx = 0; cancel = 0
    while True:
        g += 1
        if g > 40000: break
        xk, w, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None: break
        p0 = float(C.PX[k]); sg = 1 if d > 0 else -1
        gross += (float(C.PX[xk]) - p0) / p0 * 100.0 * sg; n += 1
        why[w] += 1
        for b, t in tr:
            if 'crossed ws' in t and 'exhaustion window' in t: cx += 1
            elif 'did NOT hold' in t: cancel += 1
        if w == 'mae breach':
            rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
            if cf is None: break
            k, d = cf, sd; continue
        if xk >= N - 1: break
        k = xk; d = -d
    return dict(nm='%s %d' % (win, hold), legs=n, gross=gross, net=gross - n * 0.11,
                why=why, cx=cx, cancel=cancel, winbars=C.EXH_BARS)

out = []
for win, hold in (('seam', 4), ('seam', 6), ('dwell', 4), ('dwell', 6)):
    r = walk(win, hold)
    out.append(r)
    print('# %-8s window %3d bars = %4.1f min  legs %4d  NET %+9.4f  exhaustion exits %3d  '
          'crosses seen %4d  cancelled %4d'
          % (r['nm'], r['winbars'], r['winbars'] * 5 / 60.0, r['legs'], r['net'],
             r['why'].get('ws12r exhaustion', 0), r['cx'], r['cancel']), flush=True)
import _chain10 as C
base = out[0]
C.box(('window + hold', 'window min', 'legs', 'gross', 'drag', 'NET AFTER DRAG', 'vs seam 4',
       'exhaustion exits', 'crosses seen', 'cancelled on the hold'),
      [(r['nm'], '%.1f' % (r['winbars'] * 5 / 60.0), str(r['legs']), '%+.4f' % r['gross'],
        '%.4f' % (r['legs'] * 0.11), '%+.4f' % r['net'], '%+.4f' % (r['net'] - base['net']),
        str(r['why'].get('ws12r exhaustion', 0)), str(r['cx']), str(r['cancel'])) for r in out])
ws = sorted({w for r in out for w in r['why']})
C.box(('the exit', *[r['nm'] for r in out]),
      [(w, *[str(r['why'].get(w, 0)) for r in out]) for w in ws])
