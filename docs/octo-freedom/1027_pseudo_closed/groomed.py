"""THE PSEUDO-CLOSED LINE, GROOMED AND SCORED. Joe 1028:

    "score it. use the same grooming that we applied to emerging (except the wob - that should be
     recreated on the pseudo-closed data), on the same sample pivots"

THE GROOMING STACK, as applied to emerging earlier in the session:
    1  the reversal wob          RECREATED here on the pseudo-closed data, his instruction
    2  the cadence-sampled view  the line read ONLY at his real t1/t2 cadence bars
    3  his 40/60 reversal fence  LIN2_REV_FENCE 40, at LIN2_REV_FENCE_AT 'confirm' - his ruling

THE SAMPLE IS HIS SIX 2026-08-31 PIVOT LEGS, with his sides:
    00:55 high, 02:56 low, 07:44 high, 10:23 low, 11:19 high, 13:53 low, and 14:43 closing
and his four acceptable reversals 03:53 high, 04:17 low, 11:54 low, 12:11 high at +/-5 min.

THE REFERENCE for the wob sweep is the product's CLOSED read, the same reference the emerging wob
was priced against - coverage of the chart's reversals, and the unconfirmed rate.

THE CADENCE TURN RULE IS MINE and unchanged: v[i-2] > v[i-1] < v[i] confirms a LOW turn at i-1,
knowable at i. Three points, LIFT_PTS's shape, nothing past i read.

NOTHING IS WIRED. lineage2 does not read the pseudo line; this scores it.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1027_pseudo_closed')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
import v4_l2_cadence as CAD
import pseudo_closed as PC
from optimus9.analysis.jig import lift_off
from v4_backstop_trades import prices
sys.stderr = _e

TF = 13
T = TF * 60 // 5
FENCE = float(K.LIN2_REV_FENCE)
DAY = '2026-08-31'
D0, D1 = ln.K('%s 00:00:00' % DAY), ln.K('%s 23:59:55' % DAY)
W0, W1 = ln.K('2026-08-30 00:00:00'), ln.K('2026-09-06 23:59:55')
S0, S1 = ln.K('2026-08-29 00:00:00'), ln.K('2026-09-07 23:59:55')   # a margin for lift_off
PIV = [('00:55', +1), ('02:56', -1), ('07:44', +1), ('10:23', -1), ('11:19', +1), ('13:53', -1),
       ('14:43', +1)]
OK = [('03:53', +1), ('04:17', -1), ('11:54', -1), ('12:11', +1)]
TOLB = 60

close, _h, _l = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
em = np.asarray(E[TF], float)
cl = CP.series(em, TF * 60)
CL = CP.arm_lines(E)

#   the pseudo-closed line, placed in a full-length array so lift_off can read it like any line
ps = np.full(len(em), np.nan)
IDX = np.arange(S0, S1 + 1)
ps[IDX] = PC.series(close, TF, IDX)

print('# THE PSEUDO-CLOSED LINE, GROOMED AND SCORED - ws%dr, %s' % (TF, DAY))
print('# grooming: the wob RECREATED on pseudo data, then the cadence view, then his %.0f/%.0f'
      % (FENCE, 100 - FENCE))
print('#   fence at the CONFIRM reading. The sample is his six %s pivot legs.' % DAY)
print('# the wob reference is the product\'s CLOSED read, as the emerging wob was priced.')
print('# pseudo computed over %s .. %s, BARS %d. RULED_OK %s'
      % (ln.U(S0), ln.U(S1), PC.BARS, K.RULED_OK))
print('')

# ── 1. THE WOB, RECREATED ON THE PSEUDO-CLOSED DATA ─────────────────────────────────────────────
print('## 1. the reversal wob, recreated on the pseudo-closed data, %s .. %s' % (ln.U(W0), ln.U(W1)))
print('')
print('| the line | side | wob bars | detected | coverage | unconfirmed | unconfirmed %% |'
      ' median lead min |')
print('|---|---|---|---|---|---|---|---|')
_med = lambda v: sorted(v)[len(v) // 2] if v else float('nan')
WOBS = sorted({1, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, T // 8, T // 4, T // 2, T})
BESTW = {}
for sd in (-1, +1):
    rc = sorted(int(b) for b in lift_off(cl, sd, K.LIFT_PTS, K.gap_for(TF), K.LIFT_TOL,
                                         int(K.LIFT_WOB)) if W0 <= b <= W1)
    ca = np.asarray(rc, np.int64)
    best = None
    for w in WOBS:
        raw = lift_off(ps, sd, K.LIFT_PTS, K.gap_for(TF), K.LIFT_TOL, int(w))
        st = np.asarray(sorted(int(b) + w - 1 for b in raw if W0 <= (int(b) + w - 1) <= W1),
                        np.int64)
        if not len(st) or not len(ca):
            print('| pseudo ws%dr | %s | %d | %d | - | - | - | - |'
                  % (TF, 'LOW' if sd < 0 else 'HIGH', w, len(st)))
            continue
        hit, leads = 0, []
        for c in ca:
            near = st[(st >= c - T) & (st <= c)]
            if len(near):
                hit += 1
                leads.append((c - near[-1]) * 5 / 60.0)
        unconf = int(sum(1 for x in st if not len(ca[(ca >= x) & (ca <= x + T)])))
        print('| pseudo ws%dr | %s | %d | %d | %d of %d | %d | %.1f%% | %s |'
              % (TF, 'LOW' if sd < 0 else 'HIGH', w, len(st), hit, len(ca), unconf,
                 100.0 * unconf / len(st), '%.1f' % _med(leads) if leads else '-'))
        if best is None or hit > best[1]:
            best = (w, hit, unconf, len(st))
    BESTW[sd] = best
    print('')
print('| side | the wob with peak coverage on pseudo | coverage | unconfirmed | detected |')
print('|---|---|---|---|---|')
for sd in (-1, +1):
    b = BESTW[sd]
    print('| %s | %d | %d | %d | %d |' % ('LOW' if sd < 0 else 'HIGH', b[0], b[1], b[2], b[3]))

# ── 2 + 3. THE CADENCE VIEW AND HIS FENCE, ON HIS PIVOT LEGS ────────────────────────────────────
CB = sorted({int(x) for sd in (-1, +1)
             for x, _t, _w in (CAD.t1(CL, sd, D0, D1) + CAD.t2(CL, sd, D0, D1))})
B = np.asarray(CB, np.int64)


def turns(line):
    V = line[B]
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


P = [(ln.K('%s %s:00' % (DAY, s)), sd) for s, sd in PIV]
OKB = [(ln.K('%s %s:00' % (DAY, s)), sd) for s, sd in OK]
print('')
print('## 2 + 3. the cadence view and his %.0f/%.0f fence at CONFIRM, on his six pivot legs'
      % (FENCE, 100 - FENCE))
print('')
print('| the leg | closing side | the line | early reversals, no fence | after the fence |'
      ' verdict | first after the closing pivot | its gap |')
print('|---|---|---|---|---|---|---|---|')
SUM = {}
for nm, line in (('pseudo', ps), ('emerging', em)):
    TN = turns(line)
    for i in range(len(P) - 1):
        (pa, _sa), (pb, sb) = P[i], P[i + 1]
        lim = FENCE if sb < 0 else (100 - FENCE)
        inleg = [x for x in TN if x[2] == sb and pa < x[0] < pb]
        kept = [x for x in inleg if ((x[4] < lim) if sb < 0 else (x[4] > lim))]
        bad = [x for x in kept
               if not any(abs(x[0] - o) <= TOLB and od == sb for o, od in OKB)]
        after = [x for x in TN if x[2] == sb and x[0] >= pb
                 and ((x[4] < lim) if sb < 0 else (x[4] > lim))]
        s = SUM.setdefault(nm, [0, 0, 0, 0])
        s[0] += 1; s[1] += len(inleg); s[2] += len(bad)
        if not bad:
            s[3] += 1
        print('| %s -> %s | %s | %s | %d | %d | %s | %s | %s |'
              % (PIV[i][0], PIV[i + 1][0], 'HIGH' if sb > 0 else 'LOW', nm,
                 len(inleg), len(kept),
                 'clean' if not bad else 'TURNED BACK x%d' % len(bad),
                 ln.U(after[0][0]) if after else 'none on the day',
                 '%+.1f min' % ((after[0][0] - pb) * 5 / 60.0) if after else '-'))

print('')
print('| the line, groomed | legs | early reversals before the fence | after, unwanted |'
      ' clean legs |')
print('|---|---|---|---|---|')
for nm in ('pseudo', 'emerging'):
    s = SUM[nm]
    print('| %s | %d | %d | %d | %d of %d |' % (nm, s[0], s[1], s[2], s[3], s[0]))

print('')
print('| the day\'s turn count, cadence view | side | no fence | after the fence at CONFIRM |')
print('|---|---|---|---|')
for nm, line in (('pseudo', ps), ('emerging', em)):
    TN = turns(line)
    for sd in (-1, +1):
        lim = FENCE if sd < 0 else (100 - FENCE)
        s = [x for x in TN if x[2] == sd]
        k = sum(1 for x in s if ((x[4] < lim) if sd < 0 else (x[4] > lim)))
        print('| %s | %s | %d | %d |' % (nm, 'LOW' if sd < 0 else 'HIGH', len(s), k))
