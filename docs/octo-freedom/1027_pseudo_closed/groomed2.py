"""TWO FIXES ON THE PSEUDO SCORE. Joe 1028: *"both"*.

FIX 1 - THE WOB RANKING WAS DEGENERATE. The previous run picked the wob with peak COVERAGE alone,
which on the HIGH side chose wob 1 with 4,270 unconfirmed of 4,971 detected: coverage maximised by
firing constantly. The fix is NOT a different scoring formula - a weighting between coverage and
unconfirmed would be a preference I invented. The automated pick is REMOVED and the full curve is
printed with both columns, the same way the emerging curve was read.

FIX 2 - WHY THE 00:55 -> 02:56 LEG GOES BLIND FOR 7 HOURS on pseudo. Every LOW-side cadence turn
after the 02:56 pivot is listed with its value at the confirm bar, so the ones his 40 fence rejects
are visible rather than inferred.

Everything else is unchanged from groomed.py.
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
S0, S1 = ln.K('2026-08-29 00:00:00'), ln.K('2026-09-07 23:59:55')
close, _h, _l = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
em = np.asarray(E[TF], float)
cl = CP.series(em, TF * 60)
CL = CP.arm_lines(E)
ps = np.full(len(em), np.nan)
IDX = np.arange(S0, S1 + 1)
ps[IDX] = PC.series(close, TF, IDX)
_med = lambda v: sorted(v)[len(v) // 2] if v else float('nan')

print('# TWO FIXES ON THE PSEUDO SCORE - ws%dr' % TF)
print('# FIX 1: the automated "best wob" pick is REMOVED. It ranked on coverage alone and chose')
print('#   wob 1 on the HIGH side - 4270 unconfirmed of 4971 detected. The full curve is printed')
print('#   instead; a weighting between coverage and unconfirmed would be a preference of mine.')
print('# FIX 2: every LOW cadence turn after the 02:56 pivot, with its confirm-bar value, so the')
print('#   7-hour blind leg is visible rather than inferred.')
print('# RULED_OK %s' % K.RULED_OK)
print('')
print('## FIX 1 - the pseudo wob curve, both columns, %s .. %s' % (ln.U(W0), ln.U(W1)))
print('')
WOBS = sorted({1, 2, 4, 8, 12, 16, 20, 24, 28, 32, 40, 48, 64, T // 8, T // 4, T // 2, T})
for sd in (-1, +1):
    rc = sorted(int(b) for b in lift_off(cl, sd, K.LIFT_PTS, K.gap_for(TF), K.LIFT_TOL,
                                         int(K.LIFT_WOB)) if W0 <= b <= W1)
    ca = np.asarray(rc, np.int64)
    print('### %s side - the closed chart has %d reversals in the window'
          % ('LOW' if sd < 0 else 'HIGH', len(rc)))
    print('')
    print('| wob bars | wob s | detected | coverage | coverage %% | unconfirmed | unconfirmed %% |'
          ' median lead min |')
    print('|---|---|---|---|---|---|---|---|')
    for w in WOBS:
        raw = lift_off(ps, sd, K.LIFT_PTS, K.gap_for(TF), K.LIFT_TOL, int(w))
        st = np.asarray(sorted(int(b) + w - 1 for b in raw if W0 <= (int(b) + w - 1) <= W1),
                        np.int64)
        if not len(st):
            print('| %d | %d | 0 | - | - | - | - | - |' % (w, w * 5)); continue
        hit, leads = 0, []
        for c in ca:
            near = st[(st >= c - T) & (st <= c)]
            if len(near):
                hit += 1
                leads.append((c - near[-1]) * 5 / 60.0)
        unconf = int(sum(1 for x in st if not len(ca[(ca >= x) & (ca <= x + T)])))
        print('| %d | %d | %d | %d of %d | %.1f%% | %d | %.1f%% | %s |'
              % (w, w * 5, len(st), hit, len(ca), 100.0 * hit / len(ca), unconf,
                 100.0 * unconf / len(st), '%.1f' % _med(leads) if leads else '-'))
    print('')

CB = sorted({int(x) for sd in (-1, +1)
             for x, _t, _w in (CAD.t1(CL, sd, D0, D1) + CAD.t2(CL, sd, D0, D1))})
B = np.asarray(CB, np.int64)


def turns(line, side):
    V = line[B]
    out = []
    for i in range(2, len(B)):
        a, m, c = V[i - 2], V[i - 1], V[i]
        if not np.isfinite([a, m, c]).all():
            continue
        if side > 0 and a < m > c:
            out.append((int(B[i]), int(B[i - 1]), float(m), float(c)))
        if side < 0 and a > m < c:
            out.append((int(B[i]), int(B[i - 1]), float(m), float(c)))
    return out


p0, p1 = ln.K('%s 00:55:00' % DAY), ln.K('%s 02:56:00' % DAY)
print('## FIX 2 - every LOW cadence turn after the 02:56 pivot, pseudo, with the %.0f fence verdict'
      % FENCE)
print('')
print('| the confirm bar | the turn bar | pseudo at the turn | at the confirm |'
      ' clears below %.0f | minutes after the 02:56 pivot |' % FENCE)
print('|---|---|---|---|---|---|')
for cb, tb, vt, vc in turns(ps, -1):
    if cb < p1:
        continue
    print('| %s | %s | %.2f | %.2f | %s | %+.1f |'
          % (ln.U(cb), ln.U(tb), vt, vc, 'YES' if vc < FENCE else 'no', (cb - p1) * 5 / 60.0))

print('')
print('## the same for emerging, for the contrast')
print('')
print('| the confirm bar | the turn bar | emerging at the turn | at the confirm |'
      ' clears below %.0f | minutes after the 02:56 pivot |' % FENCE)
print('|---|---|---|---|---|---|')
for cb, tb, vt, vc in turns(em, -1):
    if cb < p1:
        continue
    print('| %s | %s | %.2f | %.2f | %s | %+.1f |'
          % (ln.U(cb), ln.U(tb), vt, vc, 'YES' if vc < FENCE else 'no', (cb - p1) * 5 / 60.0))
