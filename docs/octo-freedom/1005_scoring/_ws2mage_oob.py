"""ws2Mage crossing high oob on 09-25 — every crossing, how long each holds, and the wob that
reconciles with Joe's read.

JOE 1007: *"I didn't see ws2Mage oob until ~05:06 - maybe it needs a wob"*. His TV read is a
measurement; the code found 04:34:45. This prints every crossing and the run length above the fence
so the two can be reconciled rather than one assumed right.
"""
import os, io, contextlib, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import time as _t; _T0 = _t.time()
_P = lambda m: print('# [%5.1fs] %s' % (_t.time() - _T0, m), flush=True)
_P('importing score39 ...')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
_P('ready')

D = '2026-09-25'
M2 = SC.Mg[2]
HI = SC.HI
a, b = SC.K('%s 04:20:00' % D), SC.K('%s 05:30:00' % D)

print('\n# EVERY ws2Mage CROSSING UP THROUGH %.0f, %s 04:20 .. 05:30' % (HI, D))
print('| ts | ws2Mage prev | ws2Mage | bars held above | seconds held | falls back at |')
print('|---|---|---|---|---|---|')
cross = []
for k in range(a, b + 1):
    if float(M2[k]) >= HI and float(M2[k - 1]) < HI:
        j = k
        while j <= SC.TAPE_LAST and float(M2[j]) >= HI: j += 1
        cross.append((k, j - k))
        print('| **%s** | %.2f | %.2f | %d | %d | %s |'
              % (SC.U(k), float(M2[k - 1]), float(M2[k]), j - k, (j - k) * 5,
                 SC.U(j) if j <= SC.TAPE_LAST else '—'))
print('\n- %d crossings in the window' % len(cross))

print('\n# THE FIRST CROSSING THAT HOLDS FOR N CONSECUTIVE BARS')
print('| wob (bars) | wob (seconds) | first confirmed bar | +min from 04:34:45 |')
print('|---|---|---|---|')
k_ref = SC.K('%s 04:34:45' % D)
for wob in (1, 2, 3, 6, 12, 24, 36, 48, 60):
    f = None
    run = 0
    for k in range(a, SC.TAPE_LAST + 1):
        if float(M2[k]) >= HI:
            run += 1
            if run >= wob: f = k; break
        else: run = 0
    print('| %d | %d | %s | %+.1f |'
          % (wob, wob * 5, SC.U(f) if f else '—',
             ((int(SC.ts[f]) - int(SC.ts[k_ref])) / 60000.0) if f else 0.0))

print('\n# ws2Mage PER 30 s, 04:30 .. 05:15')
print('| ts | ws2Mage | >= %.0f |' % HI); print('|---|---|---|')
for k in range(SC.K('%s 04:30:00' % D), SC.K('%s 05:15:00' % D) + 1, 6):
    v = float(M2[k])
    print('| %s | %.2f | %s |' % (SC.U(k), v, '**Y**' if v >= HI else '-'))
