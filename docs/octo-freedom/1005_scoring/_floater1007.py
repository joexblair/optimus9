"""THE 10:07 SETUP, read with the sanctioned producers only. 09-25. Joe 1007.

JOE: *"at -dr ~10:07, you have ws2Mage oob, ws1r reversing and printing a divergence (floater is
09:43, not 09:54 - 09:54 has not dropped below 50 so is disqualified. I think this is already baked
at the jig), and a bullish mage cascade. create the close/open signals and hunt the next +dr
target"* / *"ws2Mage oob is the arm trigger"*.

WHAT THIS FILE DOES: prints the three components at and around 10:07 from the producers that
already exist. It creates NO signal - the cascade test has no producer I can name (task #22, the
mage-cascade, is PARKED), so the close/open signals are not built here.

THE PRODUCERS USED, both already in optimus9/analysis/jig.py:
  anchor_floater(r, px, dr, k)   jig.py:314, Joe 0912. Steps 1-4. Step 3 walks back in `block`=60
                                 bar (300 s) blocks and counts ONLY bars on the dr side of 50 -
                                 which is the 09:54 disqualification, already baked.
                                 `fired` = -1 bullish at dr -1 (anchor is a low, px falls, r rises).
  ws2Mage oob                    the arm trigger. The fence is `oob_hi`/`oob_lo` 85/15 from
                                 lazy_g_config.
"""
import io, contextlib, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.analysis.jig import anchor_floater, AF_BLOCK
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC

D = '2026-09-25'
N = len(SC.ts)
R1 = SC.LD(60, 'r')[:N]; M2 = SC.Mg[2][:N]; PX = SC.PX[:N]
DRv = SC.DR if hasattr(SC, 'DR') else SC.DRv
K = lambda t: SC.K('%s %s' % (D, t))
def box(hdr, rr):
    w = [max(len(hdr[i]), max((len(str(x[i])) for x in rr), default=0)) for i in range(len(hdr))]
    L = lambda a, m, b: a + m.join('─' * (x + 2) for x in w) + b
    print(L('┌', '┬', '┐'))
    print('│' + '│'.join(' ' + hdr[i].center(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(L('├', '┼', '┤'))
    for x in rr:
        print('│' + '│'.join(' ' + str(x[i]).ljust(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(L('└', '┴', '┘'))

print('# dr, ws1r AND ws2Mage THROUGH THE WINDOW — one row per minute, 09:40 to 10:20')
a, b = K('09:40:00'), K('10:20:00')
box(('ts', 'dr', 'ws1r', 'ws1r vs 50', 'ws2Mage', 'ws2Mage oob low (<=15)', 'pxs'),
    [(SC.U(j), '%+d' % int(DRv[j]), '%.2f' % float(R1[j]),
      'below' if float(R1[j]) < 50 else 'above', '%.2f' % float(M2[j]),
      'Y' if float(M2[j]) <= SC.LO else '-', '%.6f' % float(PX[j]))
     for j in range(a, b + 1, 12)])

print('\n# ws2Mage CROSSINGS OF THE LOW FENCE (%.0f) IN THE WINDOW' % SC.LO)
cr = [(SC.U(j), '%.2f' % float(M2[j - 1]), '%.2f' % float(M2[j]),
       'into oob' if float(M2[j]) <= SC.LO else 'out to ib', '%+d' % int(DRv[j]))
      for j in range(a, b + 1)
      if (float(M2[j]) <= SC.LO) != (float(M2[j - 1]) <= SC.LO)]
box(('ts', 'ws2Mage prev', 'ws2Mage', 'direction', 'dr'), cr or [('—', '—', '—', '—', '—')])

print('\n# THE TWO FLOATER CANDIDATES JOE NAMED — did r drop below 50?')
rows = []
for lbl, t0, t1 in (('09:43', '09:41:00', '09:45:00'), ('09:54', '09:52:00', '09:56:00')):
    s, e = K(t0), K(t1)
    seg = R1[s:e + 1]
    rows.append((lbl, '%s..%s' % (t0, t1), '%.2f' % float(np.nanmin(seg)),
                 '%.2f' % float(np.nanmax(seg)),
                 'YES' if float(np.nanmin(seg)) < 50 else 'NO — disqualified at step 3'))
box(('candidate', 'window scanned', 'ws1r min', 'ws1r max', 'dropped below 50?'), rows)

print('\n# anchor_floater(ws1r, pxs, dr, k) AT EVERY 30 s FROM 10:04 TO 10:12')
rows = []
for j in range(K('10:04:00'), K('10:12:00') + 1, 6):
    d = int(DRv[j])
    af = anchor_floater(R1, PX, d, j)
    if af is None:
        rows.append((SC.U(j), '%+d' % d, '%.2f' % float(R1[j]), 'None — step 1 or 2 refused',
                     '—', '—', '—', '—', '—'))
        continue
    fb, fr, fp = af['floater']; pb = af['pivot'][0]
    rows.append((SC.U(j), '%+d' % d, '%.2f' % float(R1[j]), SC.U(fb), '%.2f' % fr,
                 '%.6f' % fp, SC.U(pb), '%+.2f' % af['d_osc'],
                 {1: '+1 bearish', -1: '-1 BULLISH', 0: '0 none'}[int(af['fired'])]))
box(('ts', 'dr', 'ws1r (anchor)', 'floater bar', 'floater r', 'floater pxs', 'pivot bar',
     'd_osc', 'fired'), rows)

print('\n# THE MAGE LADDER ws1..ws12 AT 10:07:00 — printed, NOT tested')
k7 = K('10:07:00')
box(('TF', 'Mage', 'ws{t}Mage - ws{t-1}Mage'),
    [('ws%d' % t, '%.2f' % float(SC.Mg[t][k7]),
      '—' if t == 1 else '%+.2f' % (float(SC.Mg[t][k7]) - float(SC.Mg[t - 1][k7])))
     for t in SC.TF])
print('- dr at 10:07:00 %+d, ws1r %.2f, ws2Mage %.2f, pxs %.6f'
      % (int(DRv[k7]), float(R1[k7]), float(M2[k7]), float(PX[k7])))
print('- AF_BLOCK %d bars = %d s' % (AF_BLOCK, AF_BLOCK * 5))
