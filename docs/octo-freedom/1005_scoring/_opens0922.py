"""WHAT CREATED EVERY OPEN ON 2026-09-22. chain 0 at reent_xwob 6. 1008.

Joe 1008: *"1) for each of the alternation opens on 09-22, show the walk that creates the open /
2) tag each open created by reentry"*.

AN OPEN BAR IS CREATED ONE OF TWO WAYS:
  ALTERNATION   the previous leg's EXIT bar, side flipped. The walk that produced that exit IS what
                created this open, so the previous leg's full trace is printed under it.
  RE-ENTRY      the router's conf bar after a 1.10 stop. Always LONG - the router forces d = +1.
                The hold / conf decisions and both gate values are printed under it.

CHAIN 0 AT reent_xwob 6, so these are not §22's legs: that table ran at the old hold of 8.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

SC, PX, box = C.SC, C.PX, C.box
N = len(SC.ts); U = SC.U
R1, X1, MG = T.R1, T.X1, T.MG
EXF_LO, XWOB, TFHI = T.EXF_LO, T.XWOB, SC.TF[-1]
MAE_STOP = C.MAE_STOP
DAY = os.environ.get('W_DAY2', '2026-09-22')
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
def chain0(gate, seed, last):
    rows = []; n = 0
    k, d, tag, rb, cf = seed, +1, 'seed', None, None
    while True:
        xk, why, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None: break
        n += 1
        p0 = float(PX[k]); sgn = 1 if d > 0 else -1
        rows.append(dict(leg=n, side='LONG' if d > 0 else 'SHORT', open=k, exit=xk, tag=tag,
                         real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn, why=why, d=d, tr=tr,
                         rb=rb, cf=cf, hand=hand))
        if why == 'mae breach':
            rb, cf, sd = T.find_reentry(xk, gate, last)
            if cf is None: break
            k, d, tag = cf, sd, 're-entry'
            continue
        if xk >= last: break
        k = xk; d = -d; tag = 'alternation'; rb = cf = None
    return rows

print('# reent_xwob %d bars. chain 0 over the whole tape ...' % XWOB, flush=True)
L = chain0(T.gate_A, 1, N - 1)
idx = {r['leg']: i for i, r in enumerate(L)}
day = [r for r in L if DAYOF(r['open']) == DAY]

print('\n# %s — EVERY OPEN, TAGGED BY WHAT CREATED IT' % DAY)
box(('leg', 'side', 'open', 'TAG — what created this open', 'the creating event', 'exit',
     'hold min', 'why', 'realised'),
    [(str(r['leg']), r['side'], U(r['open']), r['tag'].upper(),
      ('%s on %s' % (L[idx[r['leg']] - 1]['why'], U(L[idx[r['leg']] - 1]['open'])))
      if r['tag'] == 'alternation' and idx[r['leg']] > 0 else
      ('router conf, hold from %s' % U(r['rb'])) if r['tag'] == 're-entry' else 'the tape\'s first bar',
      U(r['exit']) if DAYOF(r['exit']) == DAY else '%s %s' % (DAYOF(r['exit'])[5:], U(r['exit'])),
      '%.1f' % ((int(SC.ts[r['exit']]) - int(SC.ts[r['open']])) / 60000.0),
      r['why'], '%+.4f' % r['real']) for r in day])
na = sum(1 for r in day if r['tag'] == 'alternation')
nr = sum(1 for r in day if r['tag'] == 're-entry')
print('- %d opens: %d ALTERNATION, %d RE-ENTRY.' % (len(day), na, nr))

for r in day:
    i = idx[r['leg']]
    print('\n\n' + '=' * 78)
    print('## OPEN %s   %s   leg %d   TAG: %s' % (U(r['open']), r['side'], r['leg'],
                                                  r['tag'].upper()))
    print('=' * 78)
    if r['tag'] == 'alternation' and i > 0:
        p = L[i - 1]
        p0 = float(PX[p['open']]); sgn = p['d']
        pct = lambda j: '%+.4f' % ((float(PX[j]) - p0) / p0 * 100.0 * sgn)
        mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[p['open']])) / 60000.0)
        print('\n# THE WALK THAT CREATED IT — leg %d, %s, opened %s %s'
              % (p['leg'], p['side'], DAYOF(p['open'])[5:], U(p['open'])))
        box(('ts', '+min', 'event', 'pxs', 'pct'),
            [(U(p['open']), '+0.0', 'OPEN %s' % p['side'], '%.6f' % p0, '+0.0000')]
            + [(U(j), mn(j), lab, '%.6f' % float(PX[j]), pct(j)) for j, lab in p['tr']]
            + [(U(p['exit']), mn(p['exit']),
                'EXIT — %s   ** THIS BAR IS THE OPEN ABOVE **' % p['why'],
                '%.6f' % float(PX[p['exit']]), pct(p['exit']))])
        if not p['tr']:
            print('- the walk printed NO events: leg %d never armed, so no rider, no baton. Its'
                  % p['leg'])
            print('  exit on `%s` is the only decision it made.' % p['why'])
    elif r['tag'] == 're-entry':
        rb, cf = r['rb'], r['cf']
        up = r['d'] > 0
        fen = EXF_LO if up else 100.0 - EXF_LO
        print('\n# THE ROUTER THAT CREATED IT — the %s branch' % r['side'])
        box(('ts', 'the decision', 'the value', 'the test', 'ruling'),
            [(U(rb), 'ws1x holds %s ws1r' % ('AT OR ABOVE' if up else 'AT OR BELOW'),
              'ws1x %.2f vs ws1r %.2f' % (float(X1[rb]), float(R1[rb])),
              'must HOLD reent_xwob %d bars. NO PIERCE REQUIRED' % XWOB, 'held'),
             (U(rb), 'gate A, the fence', 'ws1r %.2f' % float(R1[rb]),
              '%s %.0f' % ('<=' if up else '>=', fen),
              'PASS' if ((float(R1[rb]) <= fen) if up else (float(R1[rb]) >= fen)) else 'fail'),
             (U(cf), 'conf = return + %d' % (XWOB - 1), '%.0f s after the return' % ((XWOB - 1) * 5),
              'the first bar the hold is knowable', 'the only bar a re-entry can be placed on'),
             (U(cf), 'gate A, the Mage line',
              'ws%dMage %.2f vs ws1Mage %.2f' % (TFHI, float(MG[TFHI][cf]), float(MG[1][cf])),
              'ws%dMage %s ws1Mage' % (TFHI, '>' if up else '<'),
              'PASS' if ((float(MG[TFHI][cf]) > float(MG[1][cf])) if up
                         else (float(MG[TFHI][cf]) < float(MG[1][cf]))) else 'fail'),
             (U(cf), 'OPEN %s' % r['side'], '%.6f' % float(PX[cf]),
              'the branch that fired sets the side', 'this open')])
        prev_stop = L[i - 1] if i > 0 else None
        if prev_stop is not None:
            print('- the stop that sent it here: leg %d %s %s, exit %s on `%s` at %+.4f, a %.1f min'
                  % (prev_stop['leg'], prev_stop['side'], U(prev_stop['open']),
                     U(prev_stop['exit']), prev_stop['why'], prev_stop['real'],
                     (int(SC.ts[cf]) - int(SC.ts[prev_stop['exit']])) / 60000.0))
            print('  gap.')
