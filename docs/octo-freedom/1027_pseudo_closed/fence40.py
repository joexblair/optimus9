"""HIS 40/60 REVERSAL FENCE, VALIDATED ACROSS THE WINDOW. Joe 1028:

    "we require our reversals for a SHORT, (low-side target) to reverse below 40. for a LONG,
     high-side target, the reverse must be above 60 (100 - {knob:40}) fence"

THE FENCE IS 40 AND ITS MIRROR 60. It is NOT oob (15/85) and NOT ex-fence (RMOM_FNC 80 -> 20/80).
It is a third fence and it has no name but the value he gave it, so the rows say "the 40 fence".

    LOW-side reversal  counts only if the value is BELOW 40
    HIGH-side reversal counts only if the value is ABOVE 60

WHICH VALUE CLEARS THE FENCE IS UNSPECIFIED, so both readings are measured and neither is picked:
    at the TURN        the middle of the three cadence samples - where the view puts the extreme
    at the CONFIRM     the third sample, the bar the turn becomes knowable on
and the 5s scan is measured at its own raw reversal bar for comparison.

THE CADENCE VIEW's turn rule is MINE: v[i-2] > v[i-1] < v[i] confirms a LOW turn at i-1, knowable
at i. Three points, LIFT_PTS's shape, nothing past i read.

HIS PIVOT LEGS on 08-31 are the review set; the 8-day window follows for the count effect.
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

FENCE = 40.0
TF = 13
DAY = '2026-08-31'
D0, D1 = ln.K('%s 00:00:00' % DAY), ln.K('%s 23:59:55' % DAY)
W0, W1 = ln.K('2026-08-30 00:00:00'), ln.K('2026-09-06 23:59:55')
PIV = [('00:55', +1), ('02:56', -1), ('07:44', +1), ('10:23', -1), ('11:19', +1), ('13:53', -1),
       ('14:43', +1)]
E = RS.load((RS.K0, RS.R0, RS.S0))
em = np.asarray(E[TF], float)
CL = CP.arm_lines(E)


def cad_bars(a, b):
    return sorted({int(x) for sd in (-1, +1)
                   for x, _t, _w in (CAD.t1(CL, sd, a, b) + CAD.t2(CL, sd, a, b))})


def cad_turns(bars):
    """-> [(confirm_bar, turn_bar, side, v_turn, v_confirm)] from the cadence samples alone."""
    B = np.asarray(bars, np.int64)
    V = em[B]
    out = []
    for i in range(2, len(B)):
        a, m, c = V[i - 2], V[i - 1], V[i]
        if not np.isfinite([a, m, c]).all():
            continue
        if a < m > c:
            out.append((int(B[i]), int(B[i - 1]), +1, float(m), float(c)))
        if a > m < c:
            out.append((int(B[i]), int(B[i - 1]), -1, float(m), float(c)))
    return out


print('# HIS 40/60 REVERSAL FENCE on ws%dr - the knob is %.0f, its mirror %.0f' % (TF, FENCE, 100 - FENCE))
print('# LOW reversal counts only BELOW %.0f; HIGH only ABOVE %.0f.' % (FENCE, 100 - FENCE))
print('# NOT oob (15/85) and NOT ex-fence (20/80). A third fence, named by its value only.')
print('# both readings measured: the value at the TURN sample, and at the CONFIRM sample.')
print('# the cadence turn rule is MINE. RULED_OK %s' % K.RULED_OK)
print('')
CB = cad_bars(D0, D1)
T = cad_turns(CB)
print('## %s - every cadence-view turn, with the fence verdict' % DAY)
print('')
print('| the confirm bar | the turn bar | side | ws%dr at the turn | at the confirm |'
      ' clears at the turn | clears at the confirm |' % TF)
print('|---|---|---|---|---|---|---|')
for cb, tb, sd, vt, vc in T:
    lim = FENCE if sd < 0 else (100 - FENCE)
    ok_t = (vt < lim) if sd < 0 else (vt > lim)
    ok_c = (vc < lim) if sd < 0 else (vc > lim)
    print('| %s | %s | %s | %.2f | %.2f | %s | %s |'
          % (ln.U(cb), ln.U(tb), 'LOW' if sd < 0 else 'HIGH', vt, vc,
             'yes' if ok_t else 'NO', 'yes' if ok_c else 'NO'))

print('')
print('## his pivot legs on %s - what the fence removes' % DAY)
print('')
print('| the leg | closing side | turns before the fence | turns after, at the TURN |'
      ' turns after, at the CONFIRM |')
print('|---|---|---|---|---|')
P = [(ln.K('%s %s:00' % (DAY, s)), sd) for s, sd in PIV]
for i in range(len(P) - 1):
    (pa, _sa), (pb, sb) = P[i], P[i + 1]
    lim = FENCE if sb < 0 else (100 - FENCE)
    inleg = [(cb, tb, sd, vt, vc) for cb, tb, sd, vt, vc in T if sd == sb and pa < cb < pb]
    kt = [x for x in inleg if ((x[3] < lim) if sb < 0 else (x[3] > lim))]
    kc = [x for x in inleg if ((x[4] < lim) if sb < 0 else (x[4] > lim))]
    print('| %s -> %s | %s | %d | %d | %d |'
          % (PIV[i][0], PIV[i + 1][0], 'HIGH' if sb > 0 else 'LOW',
             len(inleg), len(kt), len(kc)))

print('')
print('## the 8-day window 08-30..09-06 - the count effect, both views')
print('')
CBW = cad_bars(W0, W1)
TW = [x for x in cad_turns(CBW) if W0 <= x[0] <= W1]
print('| the view | side | turns | clear the fence at the TURN | at the CONFIRM |')
print('|---|---|---|---|---|')
for sd in (-1, +1):
    lim = FENCE if sd < 0 else (100 - FENCE)
    s = [x for x in TW if x[2] == sd]
    kt = sum(1 for x in s if (x[3] < lim if sd < 0 else x[3] > lim))
    kc = sum(1 for x in s if (x[4] < lim if sd < 0 else x[4] > lim))
    print('| cadence view | %s | %d | %d | %d |' % ('LOW' if sd < 0 else 'HIGH', len(s), kt, kc))
for sd in (-1, +1):
    lim = FENCE if sd < 0 else (100 - FENCE)
    raw = [int(b) for b in lift_off(em, sd, K.LIFT_PTS, K.gap_for(TF), K.LIFT_TOL, int(K.LIFT_WOB))
           if W0 <= b <= W1]
    k = sum(1 for b in raw if (em[b] < lim if sd < 0 else em[b] > lim))
    print('| 5s scan wob %d | %s | %d | %d | - |' % (K.LIFT_WOB, 'LOW' if sd < 0 else 'HIGH',
                                                     len(raw), k))
