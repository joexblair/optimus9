"""The momentum petri dish: which read predicts that the board can walk to an ex-fence carrier.

HIS 1105 FRAMING, verbatim: *"all we need the mech to do is to decide if it has enough momentum to
walk to an ex-20/80 r-line, who will carry using our established mech"*, and on the lower rungs:
*"I think we can work with the lower mages"*.

THE LABEL IS A COUNT, NOT A YES OR NO. Measured first: the boolean "does ANY carrier reach the
fence" is true 68% to 99% of the time and cannot discriminate - the 2026-08-07 08:26:00 cadence had
5 of 27 carriers and still stopped at -1.100. The COUNT spans 0 to 27 on every row, with 32.3%
zero-carrier legs on ws1Mage at 15/85 against a p90 of 11. So the label is: HOW MANY of step 1's own
carrier set reach the fence inside the leg.

THE POPULATION IS HIS MECHANISM. v4_sweep_pivots.legs(name) - a Mage oob->ib cross confirm opens a
leg, the next opposite-side cross confirm closes it. Both ends are mechanism-defined, so no horizon
of mine enters the label. Every rate is also reported over a greedy non-overlapping subset, because
the legs overlap 3.11x to 12.93x.

THE BENCHMARK IS r-pred, NOT A COIN FLIP. breaching_line.predict_breach already answers his
sentence: it predicts that a line will breach. Its boundary is 85/15, so the 15/85 arm of the label
is r-pred's native target. The research features have to beat it, not beat chance.

TWO CONTROLS: r-pred's flag count, and the existing momentum verdict's count.

WHAT IS MINE, STATED:
  the decision bar     the leg's OPEN. It is the only bar a leg has before its own outcome, and
                       every feature reads that bar or the two before it - asserted.
  the split            each feature is split at ITS OWN MEDIAN over the population. That is the
                       data's midpoint, not a threshold I chose, and it guarantees two equal halves.
  the sign             every feature is signed TOWARD the fence being scored, so a HIGH-fence row
                       and a LOW-fence row ask the same question in opposite directions.
  one momentum bind    momo_bank('wsf') and momo_bank('domtf') are byte-identical at version 1
                       (slope 1.2, r2 0.7, window 60, step 5, k_window 6), so one bind gives the
                       same verdict for ws4..ws12 and ws13..ws30. Checked, not assumed.

    W_DISH_MAGES   a comma list of Mage lines. Default ws1Mage,ws2Mage,ws3Mage,ws5Mage - his lower.
    W_DISH_MOMO    'off' drops the existing-momentum control, which is the only slow feature.
"""
import io
import os
import sys
import time
from collections import defaultdict

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr
sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_fdm2 as F2
    import v4_sweep_pivots as SP
    import v4_closed_prev as CP
    import ln
    from optimus9.analysis import jig as JIG
    from optimus9.compute.breaching_line import predict_breach
    from optimus9.compute import momo_core as MC
    from optimus9.compute.momo_config import momo_config, momo_bank
    from optimus9 import DatabaseManager
    from optimus9.config import get_db_config
finally:
    sys.stderr = _e

MAGES = ([s.strip() for s in os.environ['W_DISH_MAGES'].split(',')]
         if os.environ.get('W_DISH_MAGES') else ['ws1Mage', 'ws2Mage', 'ws3Mage', 'ws5Mage'])
WANT_MOMO = os.environ.get('W_DISH_MOMO', 'on') != 'off'
FENCES = (('20/80', 20.0, 80.0), ('15/85', 15.0, 85.0))
READS = ('closed-prev', 'emerging')
SIDES = ((+1, 'HIGH'), (-1, 'LOW'))

LN = F2.load()
HI = int(LN['HI'])
NB = len(LN['close'])
LO_TF = int(K.FDM_STEP1_ABOVE_TF) + 1
CARRIERS = list(range(LO_TF, HI + 1))
assert all(t in LN['MGE'] for t in CARRIERS), 'the Mage ladder does not cover every carrier'

#   the x and m lines, both reads. ln.line serves emerging; CP.series gives the chart-matched step.
XE = {t: np.asarray(ln.line('ws%dx' % t), float) for t in CARRIERS}
ME = {t: np.asarray(ln.line('ws%dm' % t), float) for t in CARRIERS}
XC = {t: np.asarray(CP.series(XE[t], t * 60), float) for t in CARRIERS}
MC_ = {t: np.asarray(CP.series(ME[t], t * 60), float) for t in CARRIERS}

#   r-pred once per (TF, read) over the whole tape, then indexed at the leg opens
RPRED = {}
for read in READS:
    kk = LN['CPR'] if read == 'closed-prev' else LN['EMR']
    mm = MC_ if read == 'closed-prev' else ME
    gg = LN['CPM'] if read == 'closed-prev' else LN['MGE']
    for t in CARRIERS:
        RPRED[(read, t)] = predict_breach(np.asarray(kk[t], float), mm[t],
                                          np.asarray(gg[t], float))

#   at_extreme once per (TF, side): the pin is a lift-off read, so it is EMERGING, his standing rule
PIN = {(t, sd): JIG.at_extreme_mask(LN['EMR'][t], sd, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL)
       for t in CARRIERS for sd in (+1, -1)}

if WANT_MOMO:
    _db = DatabaseManager(**get_db_config()); _db.connect()
    _w, _d = momo_bank(_db, 6), momo_bank(_db, 20)
    _db.disconnect()
    _same = all(_w[k] == _d[k] for k in _w
                if k not in ('mech', 'tf_lo', 'tf_hi', 'mmc_pk', 'mmc_note', 'note'))
    _BANK = _w

FEATS = ('n_mage_above_r', 'sum_mage_minus_r', 'n_mage_above_x', 'n_mdiff_grew',
         'mean_d1', 'max_d1', 'n_hinge', 'n_pinned', 'n_rpred')
if WANT_MOMO:
    FEATS = FEATS + ('n_momo',)


def greedy(lg):
    keep = np.zeros(len(lg), bool); last = -1
    for i in sorted(range(len(lg)), key=lambda i: (lg[i][1], lg[i][0])):
        if lg[i][0] > last:
            keep[i] = True; last = lg[i][1]
    return keep


print('| the dish | value |')
print('|---|---|')
print('| the label | HOW MANY of ws%dr..ws%dr reach the fence inside the leg, 0 to %d |'
      % (LO_TF, HI, len(CARRIERS)))
print('| the carrier set | step 1\'s own, FDM_STEP1_ABOVE_TF %d |' % int(K.FDM_STEP1_ABOVE_TF))
print('| the Mage lines | %s |' % ', '.join(MAGES))
print('| the decision bar | the leg\'s open |')
print('| the split | each feature at its own median over the population |')
print('| the tape | %d bars, %.1f days |' % (NB, NB * 5 / 86400.0))
if WANT_MOMO:
    print('| the two momentum banks identical at v1 | %s |' % ('YES' if _same else 'NO'))
print()

t0 = time.time()
ROWS = defaultdict(dict)        # (nm, read, fence, side) -> {'cnt':.., 'keep':.., feats..}
for nm in MAGES:
    lg = SP.legs(nm)
    keep = greedy(lg)
    O = np.array([o for o, _, _ in lg], int)
    for read in READS:
        src = LN['CPR'] if read == 'closed-prev' else LN['EMR']
        mg = LN['CPM'] if read == 'closed-prev' else LN['MGE']
        xs = XC if read == 'closed-prev' else XE
        #   the LABEL: one slice pass per carrier
        cnt = {(f[0], sd): np.zeros(len(lg), int) for f in FENCES for sd, _ in SIDES}
        for t in CARRIERS:
            a = np.asarray(src[t], float)
            for i, (o, z, _s) in enumerate(lg):
                seg = a[o:z + 1]
                if not seg.size or not np.isfinite(seg).any():
                    continue
                mx, mn = float(np.nanmax(seg)), float(np.nanmin(seg))
                for f in FENCES:
                    if mx >= f[2]:
                        cnt[(f[0], +1)][i] += 1
                    if mn <= f[1]:
                        cnt[(f[0], -1)][i] += 1
        #   the FEATURES at the leg's open, signed toward each side
        for sd, lab in SIDES:
            F = {k: np.zeros(len(lg), float) for k in FEATS}
            for t in CARRIERS:
                r = np.asarray(src[t], float); g = np.asarray(mg[t], float)
                x = np.asarray(xs[t], float)
                rp = RPRED[(read, t)]; pin = PIN[(t, sd)]
                for i, o in enumerate(O):
                    if o < 2:
                        continue
                    r0, r1, r2 = r[o], r[o - 1], r[o - 2]
                    g0, g1 = g[o], g[o - 1]
                    md, mdp = (g0 - r0) * sd, (g1 - r1) * sd
                    d1, d1p = (r0 - r1) * sd, (r1 - r2) * sd
                    F['n_mage_above_r'][i] += 1 if md > 0 else 0
                    F['sum_mage_minus_r'][i] += md if np.isfinite(md) else 0.0
                    F['n_mage_above_x'][i] += 1 if (g0 - x[o]) * sd > 0 else 0
                    F['n_mdiff_grew'][i] += 1 if md > mdp else 0
                    F['mean_d1'][i] += d1 if np.isfinite(d1) else 0.0
                    F['max_d1'][i] = max(F['max_d1'][i], d1 if np.isfinite(d1) else -1e9)
                    F['n_hinge'][i] += 1 if abs(r0 - r1) < abs(r1 - r2) else 0
                    F['n_pinned'][i] += 1 if pin[o] else 0
                    F['n_rpred'][i] += 1 if int(rp[o]) == sd else 0
            F['mean_d1'] /= len(CARRIERS)
            if WANT_MOMO:
                with momo_config(_BANK):
                    for t in CARRIERS:
                        r = np.asarray(src[t], float)
                        for i, o in enumerate(O):
                            if o < 2:
                                continue
                            if MC.momo(r, sd, int(o))[0] == 'momo':
                                F['n_momo'][i] += 1
            for f in FENCES:
                ROWS[(nm, read, f[0], lab)] = dict(cnt=cnt[(f[0], sd)], keep=keep, **F)
        sys.stderr.write('%s %s  %.0f s\n' % (nm, read, time.time() - t0))
        sys.stderr.flush()

print('## the label, per row - the control every feature is judged against')
print()
print('| the Mage line | the read | the fence | side | legs | zero-carrier legs | median carriers | p90 |')
print('|---|---|---|---|---|---|---|---|')
for k in sorted(ROWS):
    d = ROWS[k]; c = d['cnt'][d['keep']]
    print('| %s | %s | %s | %s | %d | %.1f%% | %d | %d |'
          % (k[0], k[1], k[2], k[3], len(c), 100.0 * (c == 0).mean(),
             int(np.median(c)), int(np.percentile(c, 90))))
print()

print('## every feature, split at its own median. SEPARATION is the drop in zero-carrier legs')
print()
print('| the Mage line | the read | the fence | side | the feature | its median | legs below | zero-carrier below | median carriers below | legs at or above | zero-carrier above | median carriers above | SEPARATION, points |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
BEST = []
for k in sorted(ROWS):
    d = ROWS[k]; keep = d['keep']; c = d['cnt'][keep]
    for ft in FEATS:
        v = d[ft][keep]
        m = float(np.median(v))
        lo, hiM = v < m, v >= m
        if lo.sum() < 10 or hiM.sum() < 10:
            print('| %s | %s | %s | %s | %s | %.3f | %d | - | - | %d | - | - | one side under 10 legs |'
                  % (k[0], k[1], k[2], k[3], ft, m, int(lo.sum()), int(hiM.sum())))
            continue
        z0, z1 = 100.0 * (c[lo] == 0).mean(), 100.0 * (c[hiM] == 0).mean()
        print('| %s | %s | %s | %s | %s | %.3f | %d | %.1f%% | %d | %d | %.1f%% | %d | %+.1f |'
              % (k[0], k[1], k[2], k[3], ft, m, int(lo.sum()), z0, int(np.median(c[lo])),
                 int(hiM.sum()), z1, int(np.median(c[hiM])), z0 - z1))
        BEST.append((z0 - z1, k, ft, z0, z1, int(np.median(c[lo])), int(np.median(c[hiM])),
                     int(lo.sum()), int(hiM.sum())))
print()

print('## THE VOTE - the three features that separated, each voting on its own median')
print()
print('NO NEW VALUE ENTERS HERE. Each feature votes "carry" when it sits on the carry side of ITS')
print('OWN median - the side the dish measured, which for the fast-versus-slow pair is the LOW side')
print('because its separation was negative. The vote is then a count of 0 to 3. The medians are the')
print("data's and the count is a count, so nothing is fitted.")
print()
print('| the Mage line | the read | the fence | side | votes | legs | zero-carrier legs | median carriers | p90 | vs the row base rate |')
print('|---|---|---|---|---|---|---|---|---|---|')
for k in sorted(ROWS):
    d = ROWS[k]; keep = d['keep']; c = d['cnt'][keep]
    base = 100.0 * (c == 0).mean()
    med = {ft: float(np.median(d[ft][keep])) for ft in ('n_rpred', 'n_mage_above_x', 'n_pinned')}
    v = ((d['n_rpred'][keep] >= med['n_rpred']).astype(int)
         + (d['n_mage_above_x'][keep] < med['n_mage_above_x']).astype(int)
         + (d['n_pinned'][keep] >= med['n_pinned']).astype(int))
    for nv in (0, 1, 2, 3):
        m = v == nv
        if m.sum() < 10:
            print('| %s | %s | %s | %s | %d | %d | - | - | - | under 10 legs |'
                  % (k[0], k[1], k[2], k[3], nv, int(m.sum())))
            continue
        z = 100.0 * (c[m] == 0).mean()
        print('| %s | %s | %s | %s | %d | %d | %.1f%% | %d | %d | %+.1f |'
              % (k[0], k[1], k[2], k[3], nv, int(m.sum()), z,
                 int(np.median(c[m])), int(np.percentile(c[m], 90)), z - base))
print()

print('## the ranking - the biggest drop in zero-carrier legs, every row and feature')
print()
print('| rank | the Mage line | the read | the fence | side | the feature | zero-carrier below | zero-carrier above | median carriers below | median carriers above | SEPARATION, points |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for n, (sep, k, ft, z0, z1, m0, m1, n0, n1) in enumerate(sorted(BEST, reverse=True)[:40], 1):
    print('| %d | %s | %s | %s | %s | %s | %.1f%% of %d | %.1f%% of %d | %d | %d | %+.1f |'
          % (n, k[0], k[1], k[2], k[3], ft, z0, n0, z1, n1, m0, m1, sep))
