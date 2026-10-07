"""Joe's 3-TF x-cross exit condition, tested on 09-25 19:49:55.

JOE 1007: *"if rider TF is oob AND x-crossed while the {riderTF+2} TFs are crossed by the same
x-cross AND they are infence, then the x-cross is valid and the correct exit is created"*.
"""
import io, contextlib, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import time as _t; _T0 = _t.time()
_P = lambda m: print('# [%5.1fs] %s' % (_t.time() - _T0, m), flush=True)
_P('importing score39 ...')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
_P('ready')

D, DR = '2026-09-25', +1
RIDER = 11
BAND_HI = SC.TF[-1]                       # the lineage band tops out at ws12
EXF = 100.0 - float(SC.LG['momo_fence_r'])   # 83.0 on the dr +1 side

R = {t: SC.Rl[t] for t in SC.TF}
X = {t: SC.LD(t * 60, 'x') for t in (10, 11, 12)}
_P('x lines loaded for ws10, ws11, ws12')

band = lambda t, k: ('O' if float(R[t][k]) >= SC.HI else
                     ('x' if float(R[t][k]) >= EXF else '.'))

print('\n# THE CONDITION, BAR BY BAR AROUND THE ws11 x-CROSS')
print('# rider ws%d. riderTF+2 reaches ws%d and ws%d.' % (RIDER, RIDER + 1, RIDER + 2))
print('# ws%d IS OUTSIDE THE LINEAGE BAND (ws1..ws%d) - no r, no x loaded for it here.'
      % (RIDER + 2, BAND_HI))
print('\n| ts | ws11r | ws11 band | ws11x | x<r | ws12r | ws12 band | ws12x | x<r | condition |')
print('|---|---|---|---|---|---|---|---|---|---|')
a, b = SC.K('%s 20:44:00' % D), SC.K('%s 20:50:00' % D)
for k in range(a, b + 1, 3):
    r11, x11 = float(R[11][k]), float(X[11][k])
    r12, x12 = float(R[12][k]), float(X[12][k])
    c11, c12 = x11 < r11, x12 < r12
    ok = c11 and c12 and band(12, k) == '.'
    print('| %s | %.2f | %s | %.2f | %s | %.2f | %s | %.2f | %s | %s |'
          % (SC.U(k), r11, band(11, k), x11, 'Y' if c11 else '-',
             r12, band(12, k), x12, 'Y' if c12 else '-',
             '**FIRES**' if ok else '-'))

print('\n# THE FOUR TRADE BARS, with the condition evaluated')
for lbl, ts in (('baton -> ws11 oob', '20:32:35'), ('price MFE +3.8615', '20:34:30'),
                ('baton -> ws12 oob', '20:36:10'), ('x-cross wob2', '20:45:55'),
                ('x-cross wob3', '20:46:00'), ('EXIT final stalled', '20:57:40')):
    k = SC.K('%s %s' % (D, ts))
    r11, x11 = float(R[11][k]), float(X[11][k])
    r12, x12 = float(R[12][k]), float(X[12][k])
    print('| %s | %-22s | ws11 r %.2f %s  x %.2f  x<r %s | ws12 r %.2f %s  x %.2f  x<r %s |'
          % (ts, lbl, r11, band(11, k), x11, 'Y' if x11 < r11 else '-',
             r12, band(12, k), x12, 'Y' if x12 < r12 else '-'))

print('\n# WHEN DOES EACH TF x-CROSS UNDER ITS OWN r, after 20:32:35?')
print('| TF | first x<r bar | +min from 20:32:35 | its r there | its band |')
print('|---|---|---|---|---|')
k0 = SC.K('%s 20:32:35' % D)
for t in (10, 11, 12):
    f = next((k for k in range(k0, k0 + 2000) if float(X[t][k]) < float(R[t][k])), None)
    if f is None:
        print('| ws%d | — | — | | |' % t); continue
    print('| ws%d | %s | %+.1f | %.2f | %s |'
          % (t, SC.U(f), (int(SC.ts[f]) - int(SC.ts[k0])) / 60000.0, float(R[t][f]), band(t, f)))
