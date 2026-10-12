"""1011-v1 — THE WALK FROM 07-18 03:41, THE MECH INTACT.

Joe 1011: *"walk from 07-18 03:41 past the ws10 oob and stop on the following ws1Mage + ws1r oob
-use a timestamp-per-row report to show the baton events and any other important states that
negativcely impact the MAE/MFE result. include the related line values (r and Mage) per row
--this report will be called '1011-v1'"*.

NOTHING IS DISABLED. The walk is `_chain10.run_leg`, called as the build has it, so the exits are
the mech's own and this script cannot alter them. The only knob set from Joe's own sentence is the
loop reset, off, because he said walk PAST the ws10 oob.

The first version of this report switched the exhaustion exit off to make the walk reach the ws10
oob. That was not mine to do. It is deleted.

TWO ARMS, because one knob is UNRULED: `W_LOOP_EXH` on_stall vs always. Joe's 1010 ruling made
exhaustion live from the arm but did not say which bar it is tested on, and the answer changes
where this leg ends. Both are run and labelled. Neither is presented as the mech.

THE TWO MARKS Joe named - the ws10r oob crossing and the first bar after it where ws1Mage AND ws1r
are both oob on the same side - are located independently of the walk and reported whether or not
the mech reaches them.

THE SIDE is the side of the ws10r oob crossing Joe anchored on. The walk has to ride a side from
the open and he named no other anchor.

ROWS: every bar the mech's own trace emits, plus the open, the exit, the MAE bar, the MFE bar, and
the two marks when they fall inside the window. The event column is LAST so the numbers read from
the left without the mech's own wording pushing them off the page.
"""
import os, re, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, box, U, PX = C.SC, C.box, C.SC.U, C.PX
N = len(SC.ts)
HI, LO = SC.HI, SC.LO
R, bnd = C.R, C.bnd
MAGE = {t: np.asarray(SC.LD(t * 60, 'Mage'), float)[:N] for t in C.ALL_TF}
D = os.environ.get('V_DAY', '2026-07-18')
k0 = SC.K('%s %s' % (D, os.environ.get('V_OPEN', '03:41:00')))
TF10 = int(os.environ.get('V_TF', 10))
oob = lambda a, j, s: (float(a[j]) >= HI) if s > 0 else (float(a[j]) <= LO)

# ---- mark 1: the first ws10r oob crossing after the open, and its side
ka = d = None
for j in range(k0 + 1, N):
    for s in (+1, -1):
        if oob(R[TF10], j, s) and not oob(R[TF10], j - 1, s):
            ka, d = j, s; break
    if ka: break
assert ka, 'no ws%dr oob crossing after the open' % TF10
# ---- mark 2: ws1Mage AND ws1r both oob on that same side, first bar at or after mark 1
kb = next((j for j in range(ka, N) if oob(R[1], j, d) and oob(MAGE[1], j, d)), None)
assert kb, 'ws1Mage + ws1r never both oob on that side'

print('# 1011-v1   %s   open %s   side %s (from the ws%dr oob crossing)'
      % (D, U(k0), 'LONG' if d > 0 else 'SHORT', TF10))
print('# MARK 1  ws%dr crosses into %s oob at %s, r %.2f'
      % (TF10, 'HIGH' if d > 0 else 'LOW', U(ka), float(R[TF10][ka])))
print('# MARK 2  ws1r %.2f and ws1Mage %.2f both oob at %s'
      % (float(R[1][kb]), float(MAGE[1][kb]), U(kb)))
print('# MECH    W_LOOP_EXH %s   W_NOX %s   W_STALL_UP %s   W_KICK %s   loop %s   stop %.2f'
      % (C.EXH_LOOP, C.NOX, C.STALL_UP, C.KICK, C.LOOP_TFS or 'off', C.MAE_STOP), flush=True)

xk, why, mae, cb, hand, tr = C.run_leg(k0, d)
assert xk is not None, 'the leg found no exit before the tape end'
p0 = float(PX[k0]); sg = 1 if d > 0 else -1
pc = lambda j: (float(PX[j]) - p0) / p0 * 100.0 * sg
rel = np.array([pc(j) for j in range(k0, xk + 1)])
run_mae = np.maximum.accumulate(np.maximum(0.0, -rel))
run_mfe = np.maximum.accumulate(rel)
mae_b = k0 + int(np.argmin(rel)); mfe_b = k0 + int(np.argmax(rel))

EV = {}
add = lambda j, s: EV.setdefault(j, []).append(s)
add(k0, 'OPEN %s' % ('LONG' if d > 0 else 'SHORT'))
for j, t in tr:
    add(j, t)
add(xk, 'EXIT — %s' % why)
add(mae_b, 'MAE bar')
add(mfe_b, 'MFE bar')
if k0 <= ka <= xk: add(ka, 'MARK 1 — ws%dr crosses into oob' % TF10)
if k0 <= kb <= xk: add(kb, 'MARK 2 — ws1r + ws1Mage both oob')

# the rider per row, read off the MECH'S OWN trace text, not re-derived
rider = None; RIDE = {}
_tf = re.compile(r'ws(\d+)')
for j in sorted(set(list(EV) + [x for x, _ in tr])):
    for t in EV.get(j, []):
        if t.startswith(('KICKSTART', 'WALK STARTS', 'baton ->', 'stalled -> rider advances')):
            m = _tf.search(t)
            if m: rider = int(m.group(1))
    RIDE[j] = rider

mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[k0])) / 60000.0)
rows = []
for j in sorted(EV):
    rd = RIDE.get(j)
    rows.append((U(j), mn(j), '%.6f' % float(PX[j]), '%+.4f' % pc(j),
                 '%.4f' % run_mae[j - k0], '%.4f' % run_mfe[j - k0],
                 ('ws%d' % rd) if rd else '—',
                 ('%.2f %s' % (float(R[rd][j]), bnd(rd, j, d))) if rd else '—',
                 ('%.2f' % float(MAGE[rd][j])) if rd else '—',
                 '%.2f %s' % (float(R[1][j]), bnd(1, j, d)), '%.2f' % float(MAGE[1][j]),
                 '%.2f %s' % (float(R[TF10][j]), bnd(TF10, j, d)), '%.2f' % float(MAGE[TF10][j]),
                 ' | '.join(EV[j])))
print('\n# 1011-v1  %s  %s -> %s  (%.1f min)  exit: %s'
      % ('LONG' if d > 0 else 'SHORT', U(k0), U(xk),
         (int(SC.ts[xk]) - int(SC.ts[k0])) / 60000.0, why))
box(('ts', '+min', 'pxs', 'pct', 'MAE%', 'MFE%', 'rider', 'rider r', 'rider Mage',
     'ws1r', 'ws1Mage', 'ws%dr' % TF10, 'ws%dMage' % TF10, 'event'), rows)
print('# r fence tag: O = oob %.0f/%.0f, x = past the ex-fence %.0f/%.0f, . = inside it'
      % (LO, HI, C.EXF_LO, C.EXF_HI))
print('# MAE%% / MFE%% are RUNNING to that bar. pct is the walk-side return from the open.')
print('- exit %s at %+.4f. MAE %.4f at %s. MFE %.4f at %s.'
      % (U(xk), pc(xk), run_mae[-1], U(mae_b), run_mfe[-1], U(mfe_b)))
print('- MARK 1 %s: %s' % (U(ka), 'inside the leg' if k0 <= ka <= xk else
                           'NOT REACHED — %.1f min after the exit'
                           % ((int(SC.ts[ka]) - int(SC.ts[xk])) / 60000.0)))
print('- MARK 2 %s: %s' % (U(kb), 'inside the leg' if k0 <= kb <= xk else
                           'NOT REACHED — %.1f min after the exit'
                           % ((int(SC.ts[kb]) - int(SC.ts[xk])) / 60000.0)))
