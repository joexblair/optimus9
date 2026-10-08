"""THE INVERSION TEST — any stopped open, walked UPWARD per Joe's spec. 09-25. 1008.

Joe 1008, the spec: *"04:41 is a SHORT trade, therefore to improve the entry the price needs to be
higher, which means we are riding a upward lineage / -at 04:41, the lineage stops at ws1, because
ws2 and ws3 are infence, that is the end of the lineage walk - it walks zero bars / --ie ws1r is hi
oob and ws1x has crossed under r. ws2r and ws3r are infence when the ws1x cross passes under them.
the direction of the x cross is defined by the trade - it's a SHORT trade, so the cross is downward
/ -my perspective on the inversion: I think code is walking a downward lineage when it should be
walking upward (to improve the entry)"*, and on 10:56:40: *"this needs exactly the spec I just laid
out - it must lineage walk upward so that it does not attract mae1.1"*.

THE FRAME, PER JOE: *"the direction of the x cross is defined by the trade"*. A downward cross is
`d > 0` in the code, so a SHORT trade (side −1) walks on frame **+1**, and a LONG trade on frame −1.
THE FRAME IS THE INVERSE OF THE TRADE SIDE. Arm 1 took it from `int(DRv[k])`, which is a different
rule that happens to agree on some legs.

THE ARM is reported separately, because Joe reads the lineage straight off the ladder and gets ws1
with zero bars walked, while the naked walk inherits `exit-armed` - ws2Mage crossing into oob -
before any rider can be picked.

ZERO BARS needs the rider and the exit on the SAME bar, which `run_leg` does not do: its KICKSTART
bar `continue`s. Both conventions are reported, neither is chosen.

  W_BAR   the open bar, default 10:56:40
  W_NSIDE the trade's native side, +1 LONG or -1 SHORT, default -1
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, PX, box = C.SC, C.PX, C.box
R, X, ST, M2 = C.R, C.X, C.ST, C.M2
N = len(SC.ts); U = SC.U
DRv = (SC.DR if hasattr(SC, 'DR') else SC.DRv)[:N]
HI, LO = SC.HI, SC.LO
EXF_LO = float(SC.LG['momo_fence_r']); EXF_HI = 100.0 - EXF_LO
BAR = os.environ.get('W_BAR', '10:56:40')
SIDE = int(os.environ.get('W_NSIDE', '-1'))
K0 = SC.K('2026-09-25 %s' % BAR)
P0 = float(PX[K0])
LBL = 'LONG' if SIDE > 0 else 'SHORT'
FRAME = -SIDE                      # JOE'S RULE: the cross direction is set by the trade
mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[K0])) / 60000.0)
imp = lambda j: (P0 - float(PX[j])) / P0 * 100.0 * SIDE

def fen(t, k, d):
    v = float(R[t][k])
    if d > 0: return 'hi oob' if v >= HI else ('hi ex-f' if v >= EXF_HI else 'in-fence')
    return 'lo oob' if v <= LO else ('lo ex-f' if v <= EXF_LO else 'in-fence')

def armed_at(k, d):
    return (float(M2[k]) >= HI) if d > 0 else (float(M2[k]) <= LO)

def arm_cross(k, d):
    if d > 0: return float(M2[k]) >= HI and float(M2[k-1]) < HI
    return float(M2[k]) <= LO and float(M2[k-1]) > LO

def walk(k0, d, noarm, samebar):
    """The lineage walk. noarm skips `exit-armed`; samebar lets the KICKSTART bar also exit."""
    armed = bool(noarm); rider = None; ceil = C.BASE_HI; tr = []
    for j in range(k0, N):
        if j > k0 and ceil == C.BASE_HI and C.oobf(C.TRIG_TF, j, d) \
           and not C.oobf(C.TRIG_TF, j - 1, d):
            ceil = C.CEIL_HI
            tr.append((j, 'CEILING ws%d -> ws%d' % (C.BASE_HI, C.CEIL_HI)))
        if not armed:
            if j > k0 and arm_cross(j, d):
                armed = True
                tr.append((j, 'armed — ws2Mage %.2f crosses into oob' % float(M2[j])))
            else:
                continue
        if rider is None:
            c = [t for t in C.ALL_TF if t <= ceil and C.oobf(t, j, d)]
            if c:
                rider = max(c)
                tr.append((j, 'KICKSTART — rider ws%d (r %.2f %s)'
                           % (rider, float(R[rider][j]), fen(rider, j, d))))
                if not samebar: continue
            else:
                continue
        cand = [t for t in range(rider + 1, min(rider + C.LIN_HOP, ceil) + 1) if C.oobf(t, j, d)]
        if cand:
            rider = max(cand)
            tr.append((j, 'baton -> ws%d oob (r %.2f)' % (rider, float(R[rider][j]))))
            continue
        if ST[(rider, d)][j]:
            return j, 'final stalled on ws%d' % rider, tr
        if C.xcond(rider, j, d):
            return j, 'x-cross on ws%d (target ws%dr %.2f and ws%dr %.2f, both in-fence)' \
                   % (rider, rider + 1, float(R[rider+1][j]), rider + 2, float(R[rider+2][j])), tr
    return None, 'never terminated', tr

print('\n# %s  pxs %.6f   the trade is %s   tape dr %+d   JOE\'S WALK FRAME %+d'
      % (BAR, P0, LBL, int(DRv[K0]), FRAME))
print('# a %s entry is BETTER at a %s price. Joe: "it must lineage walk upward".'
      % (LBL, 'LOWER' if SIDE > 0 else 'HIGHER'))

print('\n# THE LADDER AT %s' % BAR)
box(('TF', 'r', 'on frame +1 (downward cross)', 'on frame -1 (upward cross)', 'x', 'x vs own r',
     'Mage'),
    [('ws%d' % t, '%.2f' % float(R[t][K0]), fen(t, K0, +1), fen(t, K0, -1),
      '%.2f' % float(X[t][K0]),
      'x under r' if float(X[t][K0]) < float(R[t][K0]) else 'x over r',
      '%.2f' % float(SC.Mg[t][K0]) if t in SC.Mg else '—') for t in range(1, 13)])

print('\n# JOE\'S 04:41 READ, TESTED CLAUSE BY CLAUSE AT %s ON FRAME %+d' % (BAR, FRAME))
rr = [('ws1r is oob on the walk frame', 'ws1r %s %.0f' % ('>=' if FRAME > 0 else '<=',
                                                          HI if FRAME > 0 else LO),
       '%.2f' % float(R[1][K0]), 'YES' if C.oobf(1, K0, FRAME) else 'no'),
      ('ws1x has crossed under r', 'ws1x < ws1r',
       '%.2f vs %.2f' % (float(X[1][K0]), float(R[1][K0])),
       'YES' if float(X[1][K0]) < float(R[1][K0]) else 'no'),
      ('ws2r is in-fence', '%.0f < ws2r < %.0f' % (EXF_LO, EXF_HI), '%.2f' % float(R[2][K0]),
       'YES' if EXF_LO < float(R[2][K0]) < EXF_HI else 'no'),
      ('ws3r is in-fence', '%.0f < ws3r < %.0f' % (EXF_LO, EXF_HI), '%.2f' % float(R[3][K0]),
       'YES' if EXF_LO < float(R[3][K0]) < EXF_HI else 'no'),
      ('the lineage stops at ws1', 'neither ws2r nor ws3r oob on the frame',
       'ws2 %s / ws3 %s' % (fen(2, K0, FRAME), fen(3, K0, FRAME)),
       'YES' if not (C.oobf(2, K0, FRAME) or C.oobf(3, K0, FRAME)) else 'no'),
      ('the x-cross fires on ws1, zero bars', 'xcond(ws1) on the frame',
       'ws1x %.2f vs ws2r %.2f and ws3r %.2f'
       % (float(X[1][K0]), float(R[2][K0]), float(R[3][K0])),
       'YES' if C.xcond(1, K0, FRAME) else 'no'),
      ('the walk can pick a rider at all', 'ws2Mage already oob on the frame',
       '%.2f' % float(M2[K0]), 'YES' if armed_at(K0, FRAME) else 'no — the arm blocks it')]
box(('the claim', 'the test', 'the value', 'holds?'), rr)

print('\n# THE WALK FROM %s, FOUR WAYS — the landing bar and the %s entry it gives' % (BAR, LBL))
rows = []
for d in (FRAME, -FRAME):
    for noarm in (False, True):
        for samebar in (False, True):
            lb, lw, tr = walk(K0, d, noarm, samebar)
            rows.append(('%+d %s' % (d, "JOE'S" if d == FRAME else 'the inverse'),
                         'removed' if noarm else 'live', 'yes' if samebar else 'no',
                         U(lb) if lb else 'never', mn(lb) if lb else '—',
                         '%.6f' % float(PX[lb]) if lb else '—',
                         '%+.4f' % imp(lb) if lb else '—', lw.split(' (')[0], str(len(tr))))
box(('walk frame', 'the arm', 'exit on the KICKSTART bar?', 'landing bar', '+min', 'entry pxs',
     '%s entry better by %%' % LBL, 'what landed it', 'walk events'), rows)
print('- "%s entry better by %%" = (%s price - landing price) / %s price * 100 * %+d. + is better.'
      % (LBL, BAR, BAR, SIDE))

# ---- the timestamped table, Joe's format, for the arm-live / no-same-bar walk on Joe's frame
for noarm in (False, True):
    lb, lw, tr = walk(K0, FRAME, noarm, False)
    if lb is None:
        print('\n## %s — %s   walk frame %+d   arm %s: THE WALK NEVER TERMINATED'
              % (BAR, LBL, FRAME, 'removed' if noarm else 'live'))
        continue
    xk, why, mae, cb, hand, tr2 = C.run_leg(lb, SIDE)
    p_ent = float(PX[lb])
    ps = lambda j: '%+.4f' % ((float(PX[j]) - P0) / P0 * 100.0 * SIDE)
    pe = lambda j: '%+.4f' % ((float(PX[j]) - p_ent) / p_ent * 100.0 * SIDE)
    print('\n\n## %s — %s   walk frame %+d   arm %s   pxs %.6f'
          % (BAR, LBL, FRAME, 'removed' if noarm else 'live', P0))
    tbl = [(U(K0), '+0.0', 'WALK STARTS — naked, nothing open', '%.6f' % P0, '+0.0000', '—')]
    tbl += [(U(j), mn(j), 'walk: %s' % lab, '%.6f' % float(PX[j]), ps(j), '—') for j, lab in tr]
    tbl += [(U(lb), mn(lb), 'LANDING — %s' % lw, '%.6f' % p_ent, ps(lb), '—')]
    tbl += [(U(lb), mn(lb), 'ENTER %s' % LBL, '%.6f' % p_ent, ps(lb), '+0.0000')]
    tbl += [(U(j), mn(j), lab, '%.6f' % float(PX[j]), ps(j), pe(j)) for j, lab in tr2]
    if xk is not None:
        tbl += [(U(xk), mn(xk), 'EXIT — %s' % why, '%.6f' % float(PX[xk]), ps(xk), pe(xk))]
    box(('ts', '+min', 'event', 'pxs', 'pct from %s' % BAR, 'pct from entry'), tbl)
    print('- pct from %s is NOT P&L above the ENTER row - nothing is open while the walk walks.'
          % BAR)

# ---- the baseline, for the comparison
bx, bw, bmae, _, _, btr = C.run_leg(K0, SIDE)
print('\n# THE BASELINE — %s ENTERED AT %s WITH NO WALK' % (LBL, BAR))
box(('ts', '+min', 'event', 'pxs', 'pct'),
    [(U(K0), '+0.0', 'OPEN %s' % LBL, '%.6f' % P0, '+0.0000')]
    + [(U(j), mn(j), lab, '%.6f' % float(PX[j]),
        '%+.4f' % ((float(PX[j]) - P0) / P0 * 100.0 * SIDE)) for j, lab in btr]
    + ([(U(bx), mn(bx), 'EXIT — %s' % bw, '%.6f' % float(PX[bx]),
         '%+.4f' % ((float(PX[bx]) - P0) / P0 * 100.0 * SIDE))] if bx else []))
