"""CAN THE LINEAGE WALK REACH ws6 FROM 15:41? 09-25. 1008.

Joe 1008: *"tell me if there's a method that would lneage walk 15:41 to the more optimised bar at
-dr ws6x-cross or stall (I can't recall if we're using x-cross or stall)"*.

WHICH ONE THE MECH USES — BOTH, in this order, from _chain10.run_leg:
    if ST[(rider, d)][j]:          -> 'final stalled'   (tested FIRST)
    if (not NOX) and xcond(...):   -> 'x-cross'         (tested SECOND)
whichever fires first on the bar wins, and the stall is checked before the cross on the same bar.

THREE READINGS OF "ws6 x-cross", all printed because the walk uses only the first:
  the walk's exit test   xcond(6): ws6x on the far side of BOTH ws7r and ws8r, and both of those
                         in-fence. This is the exit the walk actually fires.
  ws6x crosses ws6r      the simple reading of the words, on the dr side.
  ws6 stall              stall_mask(ws6r, d, stall_n 6) - no new extreme for 6 samples.

TWO FRAMES, because 15:41 is a LONG leg sitting on a dr -1 tape:
  the leg's own side     LONG, d +1  - what the chain ran, and what stopped at mae 1.1
  the tape's dr          SHORT, d -1 - Joe's "-dr", the frame his ws6 read is in

NOTHING IS TRUNCATED. Each test reports its FIRST fire after the open (which is the only one the
walk could take), plus the total count and the last fire to the tape end.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, PX, box = C.SC, C.PX, C.box
R, X, ST, M2 = C.R, C.X, C.ST, C.M2
N = len(SC.ts)
DRv = (SC.DR if hasattr(SC, 'DR') else SC.DRv)[:N]
HI, LO = SC.HI, SC.LO
EXF_LO = float(SC.LG['momo_fence_r']); EXF_HI = 100.0 - EXF_LO
OPEN = SC.K('2026-09-25 15:41:00')
MAE_STOP = C.MAE_STOP
U = SC.U
mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[OPEN])) / 60000.0)

def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]; seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return 0.0, 0.0
    p_ = float(PX[s_])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

P0 = float(PX[OPEN])
real = lambda j, dd: (float(PX[j]) - P0) / P0 * 100.0 * dd

print('\n# THE OPEN BAR  2026-09-25 15:41:00   pxs %.6f   tape dr %+d'
      % (P0, int(DRv[OPEN])))

# ---- 1. the two frames, as the walk runs them
for dd, lbl in ((+1, 'LONG  (the leg the chain ran)'), (-1, 'SHORT (the tape dr, Joe\'s -dr)')):
    xk, why, mae, cb, hand, tr = C.run_leg(OPEN, dd)
    print('\n## THE WALK FROM 15:41:00 AS %s' % lbl)
    rows = [(U(OPEN), '+0.0', 'OPEN', '%.6f' % P0, '+0.0000')]
    rows += [(U(j), mn(j), lab, '%.6f' % float(PX[j]), '%+.4f' % real(j, dd)) for j, lab in tr]
    if xk is not None:
        rows += [(U(xk), mn(xk), 'EXIT — %s' % why, '%.6f' % float(PX[xk]), '%+.4f' % real(xk, dd))]
    else:
        rows += [('—', '—', 'NO EXIT before the tape end (%s)' % why, '—', '—')]
    box(('ts', '+min', 'event', 'pxs', 'pct'), rows)

# ---- 2. the ladder at the open, both frames
print('\n# THE LINE STATE AT 15:41:00 — can a KICKSTART even pick ws6?')
def bnd(t, k, d):
    v = float(R[t][k])
    if d > 0: return 'oob' if v >= HI else ('ex-f' if v >= EXF_HI else 'in-fence')
    return 'oob' if v <= LO else ('ex-f' if v <= EXF_LO else 'in-fence')
box(('TF', 'r', 'at dr +1 (LONG)', 'at dr -1 (SHORT)', 'x', 'x vs own r', 'Mage'),
    [('ws%d' % t, '%.2f' % float(R[t][OPEN]), bnd(t, OPEN, +1), bnd(t, OPEN, -1),
      '%.2f' % float(X[t][OPEN]) if t in X else '—',
      ('x under r' if float(X[t][OPEN]) < float(R[t][OPEN]) else 'x over r') if t in X else '—',
      '%.2f' % float(SC.Mg[t][OPEN]) if t in SC.Mg else '—') for t in range(1, 13)])
print('- the KICKSTART picks max(TF <= ceiling) whose r is oob on the LEG\'s side. ws2Mage is the')
print('  arm, and it must CROSS into oob on the leg\'s side before the rider is ever chosen.')

# ---- 3. every candidate bar, first fire / count / last fire
X6, R6 = X[6], R[6]
def arm(d):
    return lambda j: ((float(M2[j]) >= HI and float(M2[j-1]) < HI) if d > 0
                      else (float(M2[j]) <= LO and float(M2[j-1]) > LO))
def xr6(d):
    return lambda j: ((float(X6[j]) < float(R6[j]) and float(X6[j-1]) >= float(R6[j-1])) if d > 0
                      else (float(X6[j]) > float(R6[j]) and float(X6[j-1]) <= float(R6[j-1])))
TESTS = [
    ('ws2Mage arms the walk',      'd +1', arm(+1)),
    ('ws2Mage arms the walk',      'd -1', arm(-1)),
    ('ws6 stall (stall_n 6)',      'd +1', lambda j: bool(ST[(6, +1)][j])),
    ('ws6 stall (stall_n 6)',      'd -1', lambda j: bool(ST[(6, -1)][j])),
    ("ws6 x-cross, the walk's exit test", 'd +1', lambda j: C.xcond(6, j, +1)),
    ("ws6 x-cross, the walk's exit test", 'd -1', lambda j: C.xcond(6, j, -1)),
    ('ws6x crosses ws6r',          'd +1', xr6(+1)),
    ('ws6x crosses ws6r',          'd -1', xr6(-1)),
]
print('\n# EVERY TEST, ITS FIRST FIRE AFTER THE OPEN, AND WHAT THE TRADE IS WORTH THERE')
rows = []
for nm, dl, pr in TESTS:
    d = +1 if dl == 'd +1' else -1
    hits = [j for j in range(OPEN + 1, N) if pr(j)]
    if not hits:
        rows.append((nm, dl, 'never', '—', '—', '—', '—', '—', '—', '0', '—')); continue
    j = hits[0]
    aL, fL = mm(OPEN, j, +1); aS, fS = mm(OPEN, j, -1)
    rows.append((nm, dl, U(j), mn(j), '%+.4f' % real(j, +1), '%.4f' % aL, '%.4f' % fL,
                 '%+.4f' % real(j, -1), '%.4f' % aS, str(len(hits)), U(hits[-1])))
box(('the test', 'frame', 'first fire', '+min', 'LONG realised', 'LONG MAE', 'LONG MFE',
     'SHORT realised', 'SHORT MAE', 'fires to tape end', 'last fire'), rows)
print('- "fires to tape end" counts every occurrence from the open to %s, nothing truncated.'
      % U(N - 1))
print('- the walk exits on the FIRST fire, so the first-fire column is the only one it could take.')

# ---- 4. the stop bar, for the comparison Joe is making
stop = next((j for j in range(OPEN + 1, N)
             if np.isfinite(PX[j]) and float(PX[j]) > 0
             and -((float(PX[j]) - P0) / P0 * 100.0) > MAE_STOP), None)
stopS = next((j for j in range(OPEN + 1, N)
              if np.isfinite(PX[j]) and float(PX[j]) > 0
              and ((float(PX[j]) - P0) / P0 * 100.0) > MAE_STOP), None)
print('\n# THE %.2f STOP ON EACH FRAME' % MAE_STOP)
box(('frame', 'stop bar', '+min', 'pxs', 'realised at the stop', 'overshoot past %.2f' % MAE_STOP),
    [('LONG  (as the chain ran it)',
      U(stop) if stop else 'never', mn(stop) if stop else '—',
      '%.6f' % float(PX[stop]) if stop else '—',
      '%+.4f' % real(stop, +1) if stop else '—',
      '%.4f' % (abs(real(stop, +1)) - MAE_STOP) if stop else '—'),
     ('SHORT (the -dr frame)',
      U(stopS) if stopS else 'never', mn(stopS) if stopS else '—',
      '%.6f' % float(PX[stopS]) if stopS else '—',
      '%+.4f' % real(stopS, -1) if stopS else '—',
      '%.4f' % (abs(real(stopS, -1)) - MAE_STOP) if stopS else '—')])
