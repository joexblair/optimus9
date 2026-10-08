"""THE x-CROSS SOURCED FROM ws4x, ws5x AND ws6x — the 15:41 leg on dr -1. 1008.

Joe 1008: *"what time does the x-cross happen if it's source from ws4x?"*

THE RIDER WINDOWS on the dr -1 walk, from _w1541.py:
  ws4   15:41:35 (KICKSTART)  ->  15:45:00
  ws5   15:45:00 (baton)      ->  15:54:00
  ws6   15:54:00 (baton)      ->  15:55:05 (the exit the walk took)

Each source is reported THREE WAYS and nothing is truncated:
  xcond(t)          the walk's own exit test: ws{t}x past BOTH ws{t+1}r and ws{t+2}r, with both of
                    those r lines in-fence. This is the test that fires 'x-cross'.
  ws{t}x X ws{t}r   the simple reading of the words - x crossing its OWN r.
  ws{t} stall       stall_mask on ws{t}r, stall_n 6 - tested BEFORE the x-cross on the same bar.

WHETHER THE WALK COULD TAKE IT is a separate column: the walk only tests the CURRENT rider, so a
fire outside that TF's rider window is unreachable without a different baton rule.
"""
import os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, PX, box = C.SC, C.PX, C.box
R, X, ST = C.R, C.X, C.ST
N = len(SC.ts); U = SC.U
OPEN = SC.K('2026-09-25 15:41:00')
P0 = float(PX[OPEN])
HI, LO = SC.HI, SC.LO
EXF_LO = float(SC.LG['momo_fence_r'])
mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[OPEN])) / 60000.0)
real = lambda j, dd: (float(PX[j]) - P0) / P0 * 100.0 * dd

def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]; seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return 0.0, 0.0
    p_ = float(PX[s_])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

D = -1
WIN = {4: (SC.K('2026-09-25 15:41:35'), SC.K('2026-09-25 15:45:00')),
       5: (SC.K('2026-09-25 15:45:00'), SC.K('2026-09-25 15:54:00')),
       6: (SC.K('2026-09-25 15:54:00'), SC.K('2026-09-25 15:55:05'))}

print('\n# THE OPEN BAR 15:41:00, pxs %.6f, dr -1. ws4x %.2f vs ws5r %.2f and ws6r %.2f'
      % (P0, float(X[4][OPEN]), float(R[5][OPEN]), float(R[6][OPEN])))
print('# xcond at dr -1 needs ws{t}x ABOVE both targets and both targets in-fence (r > %.0f).'
      % EXF_LO)

def xcross_own(t):
    return lambda j: (float(X[t][j]) > float(R[t][j]) and float(X[t][j-1]) <= float(R[t][j-1]))

rows = []
for t in (4, 5, 6):
    a, b = WIN[t]
    for nm, pr in (("xcond(ws%d) — the walk's exit test" % t, lambda j, t=t: C.xcond(t, j, D)),
                   ('ws%dx crosses ws%dr' % (t, t), xcross_own(t)),
                   ('ws%d stall (stall_n 6)' % t, lambda j, t=t: bool(ST[(t, D)][j]))):
        hits = [j for j in range(OPEN + 1, N) if pr(j)]
        if not hits:
            rows.append((nm, 'never', '—', '—', '—', '—', 'n/a', '0')); continue
        j = hits[0]
        inwin = [q for q in hits if a <= q <= b]
        aS, fS = mm(OPEN, j, D)
        rows.append((nm, U(j), mn(j), '%.6f' % float(PX[j]), '%+.4f' % real(j, D),
                     '%.4f' % aS,
                     ('YES — %s' % U(inwin[0])) if inwin else 'no',
                     str(len(hits))))
print('\n# EVERY SOURCE, ITS FIRST FIRE AFTER THE OPEN')
box(('the test', 'first fire', '+min', 'pxs', 'SHORT realised', 'SHORT MAE',
     'inside that TF\'s rider window?', 'fires to tape end'), rows)
print('- rider windows: ws4 15:41:35-15:45:00, ws5 15:45:00-15:54:00, ws6 15:54:00-15:55:05.')
print('- the walk tests only the CURRENT rider, so a "no" in that column is unreachable without a')
print('  different baton rule.')

# ---- bar by bar through the ws4 rider window, so the exact fire bar is visible
print('\n# BAR BY BAR WHILE ws4 IS THE RIDER — 15:41:35 to 15:45:00')
a, b = WIN[4]
box(('ts', '+min', 'ws4x', 'ws5r', 'ws6r', 'ws5 in-fence', 'ws6 in-fence', 'xcond(ws4)',
     'ws4 stall', 'SHORT pct'),
    [(U(j), mn(j), '%.2f' % float(X[4][j]), '%.2f' % float(R[5][j]), '%.2f' % float(R[6][j]),
      'Y' if float(R[5][j]) > EXF_LO else 'no', 'Y' if float(R[6][j]) > EXF_LO else 'no',
      'FIRE' if C.xcond(4, j, D) else '-', 'FIRE' if bool(ST[(4, D)][j]) else '-',
      '%+.4f' % real(j, D)) for j in range(a, b + 1)])
