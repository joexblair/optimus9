"""EVERY TIMESTAMPED DECISION WITH LINE VALUES. 1008.

Joe 1008 on 09-25 17:31: *"show me every timestamped decision with line values for 09-25 17:31. my
view is zero bars, because there is no DOWNWARD lineage after ws2r. I've highlighted DOWNWARD for a
critical reason, and the reason is baked into my earlier instruction on how to optimise an entry
through the use of the lineage walk"*.

THE DIRECTION, from Joe's 04:41 instruction: *"04:41 is a SHORT trade, therefore to improve the
entry the price needs to be higher, which means we are riding a upward lineage"*. Inverted for a
LONG: to improve a LONG entry the price must go DOWN, so the walk rides a **DOWNWARD** lineage. The
cross is upward, the lineage is downward, and in the code that is frame `d = -1` - the LOW oob side.

  W_BAR    the open bar, default 17:31:55
  W_NSIDE  the trade's native side, +1 LONG or -1 SHORT, default +1

WHAT IS PRINTED
  1  the ladder at the open bar, ws1..ws30, with the fence state on the walk's frame
  2  Joe's clause: where the downward lineage breaks, and what the baton could reach
  3  the gate: ws2Mage's value and whether its CROSSING can fire at all
  4  every state-change bar of the walk with the line values AT that bar
  5  the zero-bars test: what the walk's two exits give at the open bar itself
"""
import os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, PX, box = C.SC, C.PX, C.box
R, X, ST, M2 = C.R, C.X, C.ST, C.M2
N = len(SC.ts); U = SC.U
DRv = (SC.DR if hasattr(SC, 'DR') else SC.DRv)[:N]
HI, LO = SC.HI, SC.LO
EXF_LO = float(SC.LG['momo_fence_r']); EXF_HI = 100.0 - EXF_LO
BAR = os.environ.get('W_BAR', '17:31:55')
SIDE = int(os.environ.get('W_NSIDE', '1'))
K0 = SC.K('2026-09-25 %s' % BAR)
P0 = float(PX[K0])
LBL = 'LONG' if SIDE > 0 else 'SHORT'
FRAME = -SIDE
LDIR = 'DOWNWARD' if SIDE > 0 else 'UPWARD'
mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[K0])) / 60000.0)
imp = lambda j: (P0 - float(PX[j])) / P0 * 100.0 * SIDE
MAXTF = C.CEIL_HI

def fen(t, k, d):
    v = float(R[t][k])
    if d > 0: return 'hi oob' if v >= HI else ('hi ex-f' if v >= EXF_HI else 'in-fence')
    return 'lo oob' if v <= LO else ('lo ex-f' if v <= EXF_LO else 'in-fence')

print('\n# %s  pxs %.6f   the trade is %s   tape dr %+d' % (BAR, P0, LBL, int(DRv[K0])))
print('# a %s entry improves as price goes %s, so the walk rides a %s lineage —' %
      (LBL, 'DOWN' if SIDE > 0 else 'UP', LDIR))
print('# which is frame d = %+d, the %s oob side. ceiling ws%d, lin_hop %d.'
      % (FRAME, 'LOW' if FRAME < 0 else 'HIGH', C.BASE_HI, C.LIN_HOP))

print('\n# 1 — THE LADDER AT %s, ws1 TO ws%d' % (BAR, MAXTF))
box(('TF', 'r', 'on the walk frame %+d (%s lineage)' % (FRAME, LDIR), 'x', 'x vs own r', 'm',
     'Mage'),
    [('ws%d' % t, '%.2f' % float(R[t][K0]), fen(t, K0, FRAME),
      '%.2f' % float(X[t][K0]) if t in X else '—',
      ('x under r' if float(X[t][K0]) < float(R[t][K0]) else 'x over r') if t in X else '—',
      '%.2f' % float(SC.LD(t * 60, 'm')[K0]),
      '%.2f' % float(SC.Mg[t][K0]) if t in SC.Mg else '—') for t in range(1, MAXTF + 1)])

print('\n# 2 — WHERE THE %s LINEAGE BREAKS, AND WHAT THE BATON COULD REACH' % LDIR)
oob = [t for t in range(1, MAXTF + 1) if C.oobf(t, K0, FRAME)]
run = []
for t in range(1, MAXTF + 1):
    if C.oobf(t, K0, FRAME): run.append(t)
    else: break
rider0 = max([t for t in C.ALL_TF if t <= C.BASE_HI and C.oobf(t, K0, FRAME)], default=None)
reach = []
if rider0 is not None:
    cur = rider0
    while True:
        nxt = [t for t in range(cur + 1, min(cur + C.LIN_HOP, C.BASE_HI) + 1)
               if C.oobf(t, K0, FRAME)]
        if not nxt: break
        cur = max(nxt); reach.append(cur)
box(('the question', 'the answer', 'the values'),
    [('every TF oob on frame %+d' % FRAME,
      ', '.join('ws%d' % t for t in oob) or 'NONE',
      ', '.join('ws%d %.2f' % (t, float(R[t][K0])) for t in oob) or '—'),
     ('the unbroken run from ws1',
      ('ws1-ws%d' % run[-1]) if run else 'NONE — ws1 is not oob',
      ('breaks at ws%d, r %.2f, %s' % (run[-1] + 1, float(R[run[-1] + 1][K0]),
                                       fen(run[-1] + 1, K0, FRAME))) if run else
      'ws1 r %.2f %s' % (float(R[1][K0]), fen(1, K0, FRAME))),
     ('the KICKSTART rider at this bar', ('ws%d' % rider0) if rider0 else 'NONE — no oob TF',
      ('r %.2f' % float(R[rider0][K0])) if rider0 else '—'),
     ('what the baton could reach from it, lin_hop %d' % C.LIN_HOP,
      ', '.join('ws%d' % t for t in reach) or 'NOTHING — the baton cannot pass',
      ', '.join('ws%d r %.2f' % (t, float(R[t][K0])) for t in reach) or
      ('ws%d and ws%d are %s / %s'
       % (rider0 + 1, rider0 + 2, fen(rider0 + 1, K0, FRAME), fen(rider0 + 2, K0, FRAME))
       if rider0 and rider0 + 2 <= MAXTF else '—'))])

print('\n# 3 — THE GATE: CAN THE WALK PICK A RIDER AT %s AT ALL?' % BAR)
need = 'ws2Mage >= %.0f' % HI if FRAME > 0 else 'ws2Mage <= %.0f' % LO
past = (float(M2[K0]) >= HI) if FRAME > 0 else (float(M2[K0]) <= LO)
cross = None
for j in range(K0 + 1, N):
    c = (float(M2[j]) >= HI and float(M2[j-1]) < HI) if FRAME > 0 \
        else (float(M2[j]) <= LO and float(M2[j-1]) > LO)
    if c: cross = j; break
box(('the test', 'what it needs', 'the value at %s' % BAR, 'satisfied at the open bar?',
     'first CROSSING after the open', '+min'),
    [('exit-armed', need, '%.2f' % float(M2[K0]), 'YES' if past else 'no',
      U(cross) if cross else 'never', mn(cross) if cross else '—')])
print('- the arm needs a CROSSING, not a level. A line already past its fence cannot cross it.')

def walk(k0, d, noarm, samebar):
    armed = bool(noarm); rider = None; ceil = C.BASE_HI; tr = []
    for j in range(k0, N):
        if j > k0 and ceil == C.BASE_HI and C.oobf(C.TRIG_TF, j, d) \
           and not C.oobf(C.TRIG_TF, j - 1, d):
            ceil = C.CEIL_HI; tr.append((j, 'CEILING ws%d -> ws%d' % (C.BASE_HI, C.CEIL_HI), rider))
        if not armed:
            if j > k0 and ((d > 0 and float(M2[j]) >= HI and float(M2[j-1]) < HI)
                           or (d < 0 and float(M2[j]) <= LO and float(M2[j-1]) > LO)):
                armed = True
                tr.append((j, 'exit-armed — ws2Mage %.2f crosses its fence' % float(M2[j]), rider))
            else:
                continue
        if rider is None:
            c = [t for t in C.ALL_TF if t <= ceil and C.oobf(t, j, d)]
            if c:
                rider = max(c)
                tr.append((j, 'KICKSTART — rider ws%d' % rider, rider))
                if not samebar: continue
            else:
                continue
        cand = [t for t in range(rider + 1, min(rider + C.LIN_HOP, ceil) + 1) if C.oobf(t, j, d)]
        if cand:
            rider = max(cand); tr.append((j, 'baton -> ws%d' % rider, rider)); continue
        if ST[(rider, d)][j]:
            tr.append((j, 'LANDING — final stalled on ws%d' % rider, rider)); return j, tr
        if C.xcond(rider, j, d):
            tr.append((j, 'LANDING — x-cross on ws%d' % rider, rider)); return j, tr
    return None, tr

print('\n# 4 — EVERY STATE-CHANGE BAR OF THE WALK, WITH THE LINE VALUES AT THAT BAR')
print('#     frame %+d, the arm LIVE, no same-bar exit — the mech exactly as it runs' % FRAME)
lb, tr = walk(K0, FRAME, False, False)
rows = [(U(K0), '+0.0', 'WALK STARTS — naked, nothing open', '—', '—', '—', '—', '—',
         '%.2f' % float(M2[K0]), '%.6f' % P0, '+0.0000')]
for j, lab, rd in tr:
    rows.append((U(j), mn(j), lab,
                 ('ws%d' % rd) if rd else '—',
                 ('%.2f' % float(R[rd][j])) if rd else '—',
                 ('%.2f' % float(X[rd][j])) if rd and rd in X else '—',
                 ('%.2f %s' % (float(R[rd+1][j]), fen(rd+1, j, FRAME)))
                 if rd and rd + 1 in R else '—',
                 ('%.2f %s' % (float(R[rd+2][j]), fen(rd+2, j, FRAME)))
                 if rd and rd + 2 in R else '—',
                 '%.2f' % float(M2[j]), '%.6f' % float(PX[j]), '%+.4f' % imp(j)))
box(('ts', '+min', 'the decision', 'rider', 'rider r', 'rider x', 'target rider+1 r',
     'target rider+2 r', 'ws2Mage', 'pxs', '%s entry better by %%' % LBL), rows)
print('- the x-cross needs the rider x past BOTH targets AND both targets in-fence.')
print('- "%s entry better by %%" = (%s price - this bar\'s price) / %s price * 100 * %+d.'
      % (LBL, BAR, BAR, SIDE))

print('\n# 5 — THE ZERO-BARS TEST AT %s ITSELF' % BAR)
rows = []
if rider0 is None:
    rows.append(('no rider can be picked', 'no TF in ws1..ws%d is oob on frame %+d'
                 % (C.BASE_HI, FRAME), '—', 'the walk cannot start, let alone end'))
else:
    rows.append(('final stalled on ws%d' % rider0, 'stall_mask(ws%dr, %+d, stall_n %d)'
                 % (rider0, FRAME, int(SC.LG['stall_n'])),
                 'TRUE' if ST[(rider0, FRAME)][K0] else 'false',
                 'would land at %s, zero bars' % BAR if ST[(rider0, FRAME)][K0]
                 else 'does not land here'))
    t1, t2 = rider0 + 1, rider0 + 2
    rows.append(('x-cross on ws%d' % rider0,
                 'ws%dx past ws%dr and ws%dr, both in-fence' % (rider0, t1, t2),
                 'ws%dx %.2f vs ws%dr %.2f (%s) and ws%dr %.2f (%s)'
                 % (rider0, float(X[rider0][K0]), t1, float(R[t1][K0]), fen(t1, K0, FRAME),
                    t2, float(R[t2][K0]), fen(t2, K0, FRAME)) if t2 in R else '—',
                 'would land at %s, zero bars' % BAR if C.xcond(rider0, K0, FRAME)
                 else 'does not land here'))
box(('the exit', 'the test', 'the values at %s' % BAR, 'zero bars?'), rows)

print('\n# THE FOUR WALKS FROM %s' % BAR)
rows = []
for d in (FRAME, -FRAME):
    for noarm in (False, True):
        l2, t2_ = walk(K0, d, noarm, True)
        rows.append(('%+d %s' % (d, 'JOE\'S %s' % LDIR if d == FRAME else 'the inverse'),
                     'removed' if noarm else 'live',
                     U(l2) if l2 else 'never', mn(l2) if l2 else '—',
                     '%.6f' % float(PX[l2]) if l2 else '—',
                     '%+.4f' % imp(l2) if l2 else '—',
                     t2_[-1][1].replace('LANDING — ', '') if t2_ else '—', str(len(t2_))))
box(('walk frame', 'the arm', 'landing bar', '+min', 'entry pxs',
     '%s entry better by %%' % LBL, 'what landed it', 'state changes'), rows)
