"""THE BATON A/B — four arms, one knob apart. 1009.

Joe 1009: *"r-pred and lineage need to be AB'd"* and, on the fourth arm, *"so yes, go. play"*.

  oob        r is out of bounds at this bar. AS BUILT.
  momentum   the line is mom-true, momo OR curl. Joe's 1006 clause, finally built.
  rpred      the line is predicted to breach. Joe's 0730 mech.
  either     momentum OR rpred.

Everything else is held: mae_stop_pct 2.50, reent_xwob 18, lin_hop 2, no ws60r gate.
THE CONTROL is the oob arm, which must return 1623 legs / NET +4.8307 or the run is not comparable.
"""
import os, sys, importlib, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1005_scoring')

def walk(arm, nox=None):
    os.environ['W_BATON'] = arm; os.environ['W_DGATE'] = 'off'
    # X_NOX=1 runs every arm with the walk's x-cross exit suppressed. Joe 1009: *"x-cross is
    # troublesome at the moment, it's on my list for us after the sweep"* - and on the r-pred arm
    # x-cross exits went 979 -> 1086 while `final stalled` halved, so the extra ride is landing on
    # the exit he already distrusts. This separates his fix from that exit.
    if nox is None: nox = os.environ.get('X_NOX', '0') == '1'
    if nox: os.environ['W_NOX'] = '1'
    else: os.environ.pop('W_NOX', None)
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
    gross = 0.0; n = 0; why = collections.Counter(); hops = 0; riders = collections.Counter()
    holdmin = 0.0; breach = 0; noarm = 0
    while True:
        g += 1
        if g > 40000: break
        xk, w, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None: break
        p0 = float(C.PX[k]); sg = 1 if d > 0 else -1
        gross += (float(C.PX[xk]) - p0) / p0 * 100.0 * sg; n += 1
        why[w] += 1
        holdmin += (int(C.SC.ts[xk]) - int(C.SC.ts[k])) / 60000.0
        if w == 'mae breach': breach += 1
        rd = None
        if not any(t.startswith('exit-armed') for _, t in tr): noarm += 1
        for b, t in tr:
            if t.startswith('baton -> ws'):
                hops += 1; rd = int(t.split('baton -> ws')[1].split(' ')[0])
            elif t.startswith('KICKSTART'):
                rd = int(t.split('rider ws')[1].split(' ')[0])
        if rd is not None: riders[rd] += 1
        if w == 'mae breach':
            rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
            if cf is None: break
            k, d = cf, sd; continue
        if xk >= N - 1: break
        k = xk; d = -d
    return dict(arm=('%s%s' % (arm, ' noX' if nox else '')), legs=n, gross=gross,
                net=gross - n * 0.11, why=why, hops=hops,
                riders=riders, holdmin=holdmin, breach=breach, noarm=noarm)

ARMS = os.environ.get('X_ARMS', 'oob,rpred').split(',')
out = []
for a in ARMS:
    nox = a.endswith('!')
    r = walk(a.rstrip('!'), nox)
    out.append(r)
    print('# %-9s legs %4d  gross %+9.4f  NET %+9.4f  breaches %3d (%.1f%%)  baton hops %5d  '
          'mean hold %5.1f min  never-armed %3d'
          % (a, r['legs'], r['gross'], r['net'], r['breach'], 100.0 * r['breach'] / r['legs'],
             r['hops'], r['holdmin'] / r['legs'], r['noarm']), flush=True)
import _chain10 as C
box = C.box
base = out[0]
box(('the arm', 'legs', 'gross', 'drag', 'NET AFTER DRAG', 'vs the oob arm', 'breaches',
     '% of legs', 'baton hops', 'mean hold min', 'never-armed'),
    [(r['arm'], str(r['legs']), '%+.4f' % r['gross'], '%.4f' % (r['legs'] * 0.11),
      '%+.4f' % r['net'], '%+.4f' % (r['net'] - base['net']), str(r['breach']),
      '%.1f%%' % (100.0 * r['breach'] / r['legs']), str(r['hops']),
      '%.1f' % (r['holdmin'] / r['legs']), str(r['noarm'])) for r in out])
ws = sorted({w for r in out for w in r['why']})
box(('the exit', *[r['arm'] for r in out]),
    [(w, *[str(r['why'].get(w, 0)) for r in out]) for w in ws])
tfs = sorted({t for r in out for t in r['riders']})
box(('the last rider', *[r['arm'] for r in out]),
    [('ws%d' % t, *[str(r['riders'].get(t, 0)) for r in out]) for t in tfs])
print('\n- the oob arm is the CONTROL: 1623 legs / NET +4.8307. Anything else and the run is not')
print('  comparable.')
