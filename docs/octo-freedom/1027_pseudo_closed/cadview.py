"""ws13r SEEN ONLY AT THE CADENCE MARKERS. Joe 1028:

    "what do you see if you view the lines from the cadence markers? do the same early reversals
     still print?"

HIS PIVOT SIDES, given 1028:
    00:55 high, 02:56 low, 07:44 high, 10:23 low, 11:19 high, 13:53 low
    acceptable: 03:53 high, 04:17 low, 11:54 low, 12:11 high

So a leg runs from one pivot to the next and the side that matters is the CLOSING pivot's side -
travelling down to a low pivot, the thing that turns you back is a LOW-side reversal. Both the
early reversal and the target reversal are read on that one side. That is his structure, not a
choice here.

TWO VIEWS OF THE SAME LINE:
    5s SCAN       lift_off on the 5 s series, stamped at raw + wob - 1. What the mech does today.
    CADENCE VIEW  ws13r sampled ONLY at the cadence markers, and a turn read in that sampled
                  sequence. Flicker between two cadences is never seen at all.

THE TURN RULE IN THE CADENCE VIEW IS MINE, and he has not specified one. A HIGH-side turn is
confirmed at cadence i when v[i-2] < v[i-1] and v[i-1] > v[i] - the turn is AT i-1 and knowable at
i. Three points, the same shape as LIFT_PTS, and causal: nothing past i is read. LOW side mirrored.

THE CADENCE MARKERS are the real t1 and t2 from v4_l2_cadence on the closed cws set, both target
sides, on 08-31 only.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
import v4_l2_cadence as CAD
from optimus9.analysis.jig import lift_off
sys.stderr = _e

DAY = '2026-08-31'
A, B = ln.K('%s 00:00:00' % DAY), ln.K('%s 23:59:55' % DAY)
PIV = [('00:55', +1), ('02:56', -1), ('07:44', +1), ('10:23', -1), ('11:19', +1), ('13:53', -1),
       ('14:43', +1)]
OK = [('03:53', +1), ('04:17', -1), ('11:54', -1), ('12:11', +1)]
TOLB = 60                                            # +/-5 min, his own estimate note
P = [(ln.K('%s %s:00' % (DAY, s)), sd) for s, sd in PIV]
OKB = [(ln.K('%s %s:00' % (DAY, s)), sd) for s, sd in OK]

E = RS.load((RS.K0, RS.R0, RS.S0))
em = np.asarray(E[13], float)
CL = CP.arm_lines(E)
CB = sorted({int(b) for sd in (-1, +1)
             for b, _t, _w in (CAD.t1(CL, sd, A, B) + CAD.t2(CL, sd, A, B))})
CBA = np.asarray(CB, np.int64)
V = em[CBA]

print('# ws13r AT THE CADENCE MARKERS vs THE 5s SCAN, %s' % DAY)
print('# the cadence markers are the real t1/t2 from v4_l2_cadence, both sides: %d on the day.'
      % len(CB))
print('# the side that matters per leg is the CLOSING pivot\'s side - his 1028 sides.')
print('# the cadence turn rule is MINE: v[i-2] < v[i-1] > v[i] confirms a HIGH turn at i-1,')
print('#   knowable at i. Three points, LIFT_PTS\'s shape, nothing past i read. LOW mirrored.')
print('# RULED_OK %s' % K.RULED_OK)
print('')
print('| the cadence markers | %s |' % ', '.join(ln.U(b)[11:16] for b in CB))
print('')

#   the cadence-view turns, per side, stamped at the cadence they are confirmed on
cv = {-1: [], +1: []}
for i in range(2, len(V)):
    a, b2, c = V[i - 2], V[i - 1], V[i]
    if np.isfinite([a, b2, c]).all():
        if a < b2 > c:
            cv[+1].append(int(CBA[i]))
        if a > b2 < c:
            cv[-1].append(int(CBA[i]))

WOBS = [8, 20, 32]
S5 = {}
for w in WOBS:
    for sd in (-1, +1):
        S5[(w, sd)] = sorted(int(b) + w - 1 for b in
                             lift_off(em, sd, K.LIFT_PTS, K.gap_for(13), K.LIFT_TOL, int(w))
                             if A <= int(b) + w - 1 <= B)

print('| the leg | the closing side | the view | early reversals between the pivots | verdict |'
      ' first after the closing pivot | its gap |')
print('|---|---|---|---|---|---|---|')
SUM = {}
for i in range(len(P) - 1):
    (pa, _sa), (pb, sb) = P[i], P[i + 1]
    leg = '%s -> %s' % (PIV[i][0], PIV[i + 1][0])
    views = [('cadence view', cv[sb])] + [('5s scan wob %d' % w, S5[(w, sb)]) for w in WOBS]
    for nm, rl in views:
        early = [x for x in rl if pa < x < pb]
        exempt = [x for x in early if any(abs(x - o) <= TOLB and od == sb for o, od in OKB)]
        bad = [x for x in early if x not in exempt]
        after = [x for x in rl if x >= pb]
        vd = 'clean' if not early else ('acceptable' if not bad else 'TURNED BACK x%d' % len(bad))
        s = SUM.setdefault(nm, [0, 0, 0, []])
        s[0] += 1
        if not bad:
            s[1] += 1
        s[2] += len(bad)
        if after:
            s[3].append((after[0] - pb) * 5 / 60.0)
        print('| %s | %s | %s | %s | %s | %s | %s |'
              % (leg, 'HIGH' if sb > 0 else 'LOW', nm,
                 ', '.join(ln.U(x)[11:] for x in early) or 'none', vd,
                 ln.U(after[0]) if after else 'none on the day',
                 '%+.1f min' % ((after[0] - pb) * 5 / 60.0) if after else '-'))

_med = lambda v: sorted(v)[len(v) // 2] if v else float('nan')
print('')
print('| the view | legs | legs with no turn-back | unwanted early reversals |'
      ' median gap after the pivot | reversals on the day, LOW | HIGH |')
print('|---|---|---|---|---|---|---|')
for nm in ['cadence view'] + ['5s scan wob %d' % w for w in WOBS]:
    s = SUM[nm]
    if nm == 'cadence view':
        nl, nh = len(cv[-1]), len(cv[+1])
    else:
        w = int(nm.split()[-1]); nl, nh = len(S5[(w, -1)]), len(S5[(w, +1)])
    print('| %s | %d | %d of %d | %d | %s | %d | %d |'
          % (nm, s[0], s[1], s[0], s[2],
             '%+.1f min' % _med(s[3]) if s[3] else '-', nl, nh))
