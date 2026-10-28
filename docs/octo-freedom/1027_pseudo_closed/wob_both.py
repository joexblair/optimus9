"""BOTH WOB ARMS, STATIC AND TF-RELATIVE, SCORED TOGETHER. Joe 1027: *"try both"*.

    STATIC    one bar count for every TF - the shape LIFT_WOB has today, and the shape his 1026
              *"static wob12. noted, we'll keep the static"* ruling preserved
    FRACTION  T / d, so each line gets a wob proportional to its own bar width - the shape the
              knee in revwob.md pointed at

THE DOMAINS ARE DATA-ANCHORED, not chosen:
    static    1 .. 156 bars. 156 is one full ws13 bar, the shortest TF in this set, so past it a
              static wob exceeds a whole bar on at least one line. Sampled, not every integer.
    fraction  T/1 .. T/16. T/1 is one full bar - the same end of the domain from the other side.

THE SCORE IS AGGREGATED ACROSS ALL 8 (line, side) ROWS so one arm cannot win on one line:
    coverage      closed reversals caught, out of 864 across the 8 rows
    unconfirmed   the share of emerging reversals the closed chart never agreed with - a reversal
                  ENDS a lineage2 walk, so this is the kill-signal error rate
    lead          the median minutes the emerging stamp arrives before the closed reversal

Per-row detail follows for the best of each arm, because an aggregate hides a line that breaks.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
from optimus9.analysis.jig import lift_off
sys.stderr = _e

A, B = ln.K('2026-08-30 00:00:00'), ln.K('2026-09-06 23:59:55')
E = RS.load((RS.K0, RS.R0, RS.S0))
TFS = [13, 14, 15, 16]
ROWS = [(t, sd) for t in TFS for sd in (-1, +1)]
STATICS = [1, 2, 3, 4, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40, 48, 56, 64, 78, 96, 120, 156]
DENOMS = [1, 2, 3, 4, 5, 6, 8, 10, 12, 16]
_med = lambda v: sorted(v)[len(v) // 2] if v else float('nan')

EM, CLR, TB = {}, {}, {}
for t in TFS:
    em = np.asarray(E[t], float)
    EM[t] = em
    cl = CP.series(em, t * 60)
    TB[t] = t * 60 // 5
    for sd in (-1, +1):
        CLR[(t, sd)] = sorted(int(b) for b in lift_off(cl, sd, K.LIFT_PTS, K.gap_for(t),
                                                       K.LIFT_TOL, int(K.LIFT_WOB))
                              if A <= b <= B)
TOTAL_CLOSED = sum(len(CLR[r]) for r in ROWS)


def one(t, sd, w):
    """-> (detected, covered, closed, unconfirmed, median lead min)."""
    T = TB[t]
    raw = lift_off(EM[t], sd, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL, int(w))
    st = np.asarray(sorted(int(b) + int(w) - 1 for b in raw
                           if A <= (int(b) + int(w) - 1) <= B), np.int64)
    ca = np.asarray(CLR[(t, sd)], np.int64)
    if not len(st) or not len(ca):
        return len(st), 0, len(ca), len(st), float('nan')
    hit, leads = 0, []
    for c in ca:
        near = st[(st >= c - T) & (st <= c)]
        if len(near):
            hit += 1
            leads.append((c - near[-1]) * 5 / 60.0)
    unconf = int(sum(1 for x in st if not len(ca[(ca >= x) & (ca <= x + T)])))
    return len(st), hit, len(ca), unconf, _med(leads)


def agg(wof):
    """wof(t) -> the wob for that TF. -> (detected, covered, unconf, unconf%, median of leads)."""
    d = cv = un = 0
    leads = []
    for (t, sd) in ROWS:
        a, b, _c, u, lg = one(t, sd, wof(t))
        d += a; cv += b; un += u
        if lg == lg:
            leads.append(lg)
    return d, cv, un, (100.0 * un / d if d else float('nan')), _med(leads)


print('# BOTH WOB ARMS, %s .. %s' % (ln.U(A), ln.U(B)))
print('# the reference is the CLOSED read at LIFT_WOB %d, on ws13..ws16, both sides - 8 rows.'
      % K.LIFT_WOB)
print('# a reversal ENDS a lineage2 walk, so `unconfirmed` is the kill-signal error rate.')
print('# closed reversals across the 8 rows: %d. RULED_OK %s' % (TOTAL_CLOSED, K.RULED_OK))
print('')
print('## ARM 1 - STATIC, one bar count for every TF')
print('')
print('| wob bars | wob s | detected | coverage | coverage %% | unconfirmed | unconfirmed %% |'
      ' median lead min |')
print('|---|---|---|---|---|---|---|---|')
best_s = None
for w in STATICS:
    d, cv, un, up, lg = agg(lambda _t, w=w: w)
    mark = ' **BANKED**' if w == int(K.LIFT_WOB) else ''
    print('| %d%s | %d | %d | %d of %d | %.1f%% | %d | %.1f%% | %.1f |'
          % (w, mark, w * 5, d, cv, TOTAL_CLOSED, 100.0 * cv / TOTAL_CLOSED, un, up, lg))
    if best_s is None or cv > best_s[1]:
        best_s = (w, cv, un, up, lg, d)

print('')
print('## ARM 2 - TF-RELATIVE, T/d so each line scales with its own bar width')
print('')
print('| the fraction | ws13 bars | ws16 bars | detected | coverage | coverage %% | unconfirmed |'
      ' unconfirmed %% | median lead min |')
print('|---|---|---|---|---|---|---|---|---|')
best_f = None
for dn in DENOMS:
    f = lambda t, dn=dn: max(1, TB[t] // dn)
    d, cv, un, up, lg = agg(f)
    print('| T/%d | %d | %d | %d | %d of %d | %.1f%% | %d | %.1f%% | %.1f |'
          % (dn, f(13), f(16), d, cv, TOTAL_CLOSED, 100.0 * cv / TOTAL_CLOSED, un, up, lg))
    if best_f is None or cv > best_f[1]:
        best_f = (dn, cv, un, up, lg, d)

print('')
print('## the best of each arm by coverage, per row - an aggregate hides a line that breaks')
print('')
print('| the arm | the line | side | wob bars | detected | coverage | unconfirmed %% |'
      ' median lead min |')
print('|---|---|---|---|---|---|---|---|')
for nm, wof in (('static %d' % best_s[0], lambda _t, w=best_s[0]: w),
                ('T/%d' % best_f[0], lambda t, dn=best_f[0]: max(1, TB[t] // dn)),
                ('banked %d' % int(K.LIFT_WOB), lambda _t: int(K.LIFT_WOB))):
    for (t, sd) in ROWS:
        a, b, c, u, lg = one(t, sd, wof(t))
        print('| %s | ws%dr | %s | %d | %d | %d of %d | %.1f%% | %s |'
              % (nm, t, 'LOW' if sd < 0 else 'HIGH', wof(t), a, b, c,
                 100.0 * u / a if a else float('nan'),
                 '%.1f' % lg if lg == lg else '-'))
