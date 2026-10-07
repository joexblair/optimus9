"""Joe's x-cross exit, read LITERALLY, 1007.

JOE: *"my view is literal: ws{oob tag holder tf}x crossing ws{tf+1 and tf+2}r"* and
*"if rider TF is oob AND x-crossed while the {riderTF+2} TFs are crossed by the same x-cross AND
they are infence, then the x-cross is valid and the correct exit is created"*.

ONE x LINE, TWO r TARGETS. The tag holder's x crosses ws{t+1}r AND ws{t+2}r. That is what makes it
"the same x-cross" - it is literally one line.

DIRECTION, settled: dr +1 -> x crosses UNDER its target. dr -1 -> x crosses OVER.

`oob` MEANS THE TAG HOLDER, Joe 1007 - the line that reached oob and holds the `waiting for stalled`
tag. It does NOT need to still be oob at the cross: measured on 09-25, ws11r was 95.48 at 20:45:45
and 81.19 at 20:46:00, so r-still-oob and x-under-r never overlap on this line.
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

D, DR, T = '2026-09-25', +1, 11
EXF = 100.0 - float(SC.LG['momo_fence_r'])
R = {t: SC.LD(t * 60, 'r') for t in (T, T + 1, T + 2)}
X = SC.LD(T * 60, 'x')
_P('ws%dx + ws%d/%d/%dr loaded' % (T, T, T + 1, T + 2))

band = lambda t, k: ('O' if float(R[t][k]) >= SC.HI else
                     ('x' if float(R[t][k]) >= EXF else '.'))
under = lambda k, t: float(X[k]) < float(R[t][k])      # dr +1

print('\n# ws%dx vs ws%dr AND ws%dr   dr %+d   (dr +1 = x crosses UNDER)' % (T, T + 1, T + 2, DR))
print('| ts | ws11x | ws12r | band | x<ws12r | ws13r | band | x<ws13r | both in-fence | CONDITION |')
print('|---|---|---|---|---|---|---|---|---|---|')
a, b = SC.K('%s 20:32:00' % D), SC.K('%s 21:00:00' % D)
fired = None
for k in range(a, b + 1, 6):
    u1, u2 = under(k, T + 1), under(k, T + 2)
    inf = band(T + 1, k) == '.' and band(T + 2, k) == '.'
    ok = u1 and u2 and inf
    if ok and fired is None: fired = k
    print('| %s | %.2f | %.2f | %s | %s | %.2f | %s | %s | %s | %s |'
          % (SC.U(k), float(X[k]), float(R[T + 1][k]), band(T + 1, k), 'Y' if u1 else '-',
             float(R[T + 2][k]), band(T + 2, k), 'Y' if u2 else '-',
             'Y' if inf else '-', '**FIRES**' if ok else '-'))

print('\n# FIRST BAR THE CONDITION HOLDS, scanned every bar')
f = None
for k in range(a, b + 1):
    if under(k, T + 1) and under(k, T + 2) and band(T + 1, k) == '.' and band(T + 2, k) == '.':
        f = k; break
if f is None:
    print('- never in the window')
else:
    k0 = SC.K('%s 20:34:30' % D)
    print('| first fire | %s |' % SC.U(f))
    print('| vs the price MFE 20:34:30 | %+.1f min |' % ((int(SC.ts[f]) - int(SC.ts[k0])) / 60000.0))
    print('| vs the stall exit 20:57:40 | %+.1f min |'
          % ((int(SC.ts[f]) - int(SC.ts[SC.K('%s 20:57:40' % D)])) / 60000.0))
    print('| pxs at the fire bar | %.6f |' % float(SC.PX[f]))
    print('| pxs at the stall exit | %.6f |' % float(SC.PX[SC.K('%s 20:57:40' % D)]))
    print('| pxs at the open 19:49:55 | %.6f |' % float(SC.PX[SC.K('%s 19:49:55' % D)]))
