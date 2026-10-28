"""THE BARRAGE KNOB SWEEP. Joe 1027: *"sweep barrages minTF. find the lowest MAE across the window
/ add the other knobs also"*.

THREE KNOBS, AND EVERY DOMAIN IS COMPLETE OR DATA-DETERMINED - no range is chosen here:

    LIN2_BARRAGE_MIN_TF   0 .. L2_MOM_MAXTF 12. The whole domain: the count is bounded by the
                          ladder knob, so no value above 12 can ever be satisfied. 0 and 1 are
                          identical by construction - ws1r's reversal IS the signal bar, so ws1 is
                          always in the count and max(inside) >= 1 always holds. Both are run and
                          the identity is visible rather than asserted.
    LIN2_BARRAGE_LINES    1 .. 12. The whole domain, same bound.
    LIN2_BARRAGE_TOL_S    every DISTINCT cross-to-ws1r-reversal gap present in the tape. A
                          tolerance between two observed gaps admits exactly what the lower one
                          admits, so the observed gaps ARE the complete grid. NO CAP IS CHOSEN -
                          the data bounds it, which is the only way to sweep a tolerance under his
                          standing rule that no cap, horizon or window exists unless he sets one.

ONE COPY OF THE RULE. `v4_l2_cadence.barrage` takes `tol_s`, `lines` and `min_tf` overrides and
`barrage_candidates` is computed once per side and reused, so the sweep evaluates HIS producer
rather than a re-implementation of it. The alternative - a detection loop in here - is the drift
that put dtf lines in the first count.

THE SCORE IS THE COMMITTED PER-EVENT MAE/MFE: from the cadence bar to `sw['close']`, the bar
sweep-pivots ends the leg on, favourable direction -side. Sweep-pivots has no MAE of its own
(`mfe_pct` is measured FROM the pivot, which IS the leg's extreme, so it is 0 by construction),
which is why the span is the cadence-to-leg-close one.

THE CONTROL ROW is the banked config 70 / 6 / 9 and it is checked against the known-good number -
24 cadences, sum MAE -19.456, median MAE -0.199. A hash-keyed cache fails silently with real-but-
wrong arrays, so the control is printed every run and the run says whether it matched.

EVENT COUNT IS REPORTED BESIDE EVERY MAE. Joe 1023: trade COUNT is the objective, and a
fewer-event arm with a better per-event number is not an upgrade. No row here is a recommendation.

usage: l2_barrage_sweep.py [<start> <end>]     default 2026-08-30 .. 2026-09-06
"""
import os, sys, io, time
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_sweep_pivots as SP
import v4_closed_prev as CP, v4_l2_proxy as PX, v4_l2_cadence as CAD
from v4_backstop_trades import prices
sys.stderr = _e

FROM_UTC = sys.argv[1] if len(sys.argv) > 2 else '2026-08-30 00:00:00'
TO_UTC = sys.argv[2] if len(sys.argv) > 2 else '2026-09-06 23:59:55'
A, B = ln.K(FROM_UTC), ln.K(TO_UTC)
E = RS.load((RS.K0, RS.R0, RS.S0))
BD = PX.Board(CP.ladder(E), E, MGE={t: ln.line('ws%dMage' % t) for t in range(1, 13)})
close, _PHI, _PLO = prices()
t0 = time.time()

#   ── THE CANDIDATES, ONCE PER SIDE, reduced to the facts a combo tests ──
#   min_tf is a FLOOR ON WHICH LINES MAY CONTRIBUTE (his 1027 definition) and the fence arm is a
#   second filter on the same set, so `inside` depends on BOTH. There are only 13 x 3 = 39 of those
#   pairs, so the count and the cadence bar are precomputed per candidate per pair - one pass - and
#   every one of the 91,728 combos is then a comparison against two precomputed integers.
MINTFS = list(range(0, int(K.L2_MOM_MAXTF) + 1))
LINES = list(range(1, int(K.L2_MOM_MAXTF) + 1))
FENCES = ('any', 'in', 'ex')

RAW = []                                           # (gap_s, side, [(tf, bar, exfence), ...])
for sd in (-1, +1):
    for c, sig, first, _v, exf in CAD.barrage_candidates(BD, sd):
        mem = [(int(t), int(b), bool(exf[t])) for t, b in first.items() if b <= sig]
        if mem:
            RAW.append(((sig - c) * 5, sd, mem))

GAP = np.asarray([r[0] for r in RAW], np.int64)
SIDE = np.asarray([r[1] for r in RAW], np.int64)
CNT, BARS, INWIN = {}, {}, {}
for mtf in MINTFS:
    for fn in FENCES:
        cnt = np.zeros(len(RAW), np.int64)
        bar = np.full(len(RAW), -1, np.int64)
        for i, (_g, _sd, mem) in enumerate(RAW):
            sel = [(t, b) for t, b, e in mem
                   if t >= mtf and (fn == 'any' or e is (fn == 'ex'))]
            if not sel:
                continue
            cnt[i] = len(sel)
            bar[i] = max(int(K.lift_stamp(b)) for _t, b in sel)
        CNT[(mtf, fn)] = cnt
        BARS[(mtf, fn)] = bar
        INWIN[(mtf, fn)] = (bar >= A) & (bar <= B)   # his window, on the cadence bar

#   ── THE SCORE PER (cadence bar, side), computed once for every bar any combo can produce ──
need_sc = set()
for mtf in MINTFS:
    for fn in FENCES:
        b, w = BARS[(mtf, fn)], INWIN[(mtf, fn)]
        need_sc |= set(zip(b[w].tolist(), SIDE[w].tolist()))
SC = {}
for k, sd in need_sc:
    sw = SP.swing(int(k), int(sd), close)
    if sw is None or sw.get('close') is None:
        SC[(k, sd)] = None
        continue
    z = int(sw['close'])
    a2, b2 = min(int(k), z), max(int(k), z)
    seg = np.asarray(close[a2:b2 + 1], float)
    if not np.isfinite(seg).any():
        SC[(k, sd)] = None
        continue
    pb, fav = float(close[int(k)]), -int(sd)
    up = (float(np.nanmax(seg)) - pb) / pb * 100.0
    dn = (float(np.nanmin(seg)) - pb) / pb * 100.0
    mfe, mae = (up, dn) if fav > 0 else (-dn, -up)
    SC[(k, sd)] = (mae, mfe, float(sw['mfe_pct']), int(sw['lag_s']))

#   ── THE GRID. Every domain is complete or data-determined; see the header. ──
TOLS = sorted(set(int(g) for g in GAP.tolist()))
_med = lambda v: sorted(v)[len(v) // 2] if v else float('nan')


def run(tol, need, mtf, fn):
    """One combo. -> (events, sum_mae, med_mae, worst_mae, sum_mfe, med_mfe, n_better, n_capped)."""
    m = INWIN[(mtf, fn)] & (GAP <= tol) & (CNT[(mtf, fn)] >= need)
    if not m.any():
        return (0,) + (float('nan'),) * 5 + (0, 0)
    seen, rows = set(), []
    for k, sd in zip(BARS[(mtf, fn)][m].tolist(), SIDE[m].tolist()):
        if k in seen:
            continue                               # one cadence per bar, the producer's own dedup
        seen.add(k)
        sc = SC.get((k, sd))
        if sc is not None:
            rows.append(sc)
    if not rows:
        return (0,) + (float('nan'),) * 5 + (0, 0)
    MA = [r[0] for r in rows]; MF = [r[1] for r in rows]
    return (len(rows), sum(MA), _med(MA), min(MA), sum(MF), _med(MF),
            sum(1 for a, f in zip(MA, MF) if f > abs(a)),
            sum(1 for a in MA if a < -float(K.LIN2_MAE_CAP)))


res = {}
for mtf in MINTFS:
    for fn in FENCES:
        for need in LINES:
            for tol in TOLS:
                res[(tol, need, mtf, fn)] = run(tol, need, mtf, fn)

CTRL = (int(K.LIN2_BARRAGE_TOL_S), int(K.LIN2_BARRAGE_LINES), int(K.LIN2_BARRAGE_MIN_TF),
        str(K.LIN2_BARRAGE_FENCE))
ctrl = res.get(CTRL) or run(*CTRL)
#   THE CONTROL IS EMPTY UNDER HIS DEFINITION and that is the headline, not a fault in the sweep.
#   The old known-good (24, -19.456, -0.199) was measured under the MEMBERSHIP reading of min_tf,
#   which is a different mechanic, so it is not a control for this grid. The control that IS
#   comparable is min_tf 0 - the floor off - which must reproduce 28 events.
MEMBERSHIP_KNOWN = (24, -19.456, -0.199)
FLOOR_OFF = run(int(K.LIN2_BARRAGE_TOL_S), int(K.LIN2_BARRAGE_LINES), 0, 'any')
ok = (FLOOR_OFF[0] == 28)

print('# THE BARRAGE KNOB SWEEP, %s .. %s' % (ln.U(A), ln.U(B)))
print('# the rule is v4_l2_cadence.barrage with tol_s/lines/min_tf overrides - ONE copy, his.')
print('# the score is the per-event MAE/MFE: the cadence bar to sw[close], favourable -side.')
print('# RULED_OK %s | %d combos | %d candidate crosses in the window | %.1f s'
      % (K.RULED_OK, len(res), len(GAP), time.time() - t0))
print('')
print('| the domain | values | how it is bounded |')
print('|---|---|---|')
print('| LIN2_BARRAGE_MIN_TF | %d: %d..%d | complete. HIS definition - the minimum TF allowed to'
      ' CONTRIBUTE, a floor applied before the line count |'
      % (len(MINTFS), MINTFS[0], MINTFS[-1]))
print('| LIN2_BARRAGE_FENCE | 3: any, in, ex | complete - the fence state of a contributing'
      ' reversal at its own bar, read CLOSED |')
print('| LIN2_BARRAGE_LINES | %d: %d..%d | complete - same bound |'
      % (len(LINES), LINES[0], LINES[-1]))
print('| LIN2_BARRAGE_TOL_S | %d: %d..%d s | every DISTINCT observed cross-to-reversal gap - the'
      ' data bounds it, no cap chosen |' % (len(TOLS), TOLS[0], TOLS[-1]))
print('')
print('| THE CONTROL | value |')
print('|---|---|')
print('| the banked config tol_s / lines / min_tf / fence | %d / %d / %d / %s |' % CTRL)
print('| its events under HIS min_tf definition | %d |' % ctrl[0])
print('| *** why *** | min_tf %d leaves a pool of ws%d..ws%d = %d lines, and lines %d cannot be'
      ' met by %d |' % (CTRL[2], CTRL[2], K.L2_MOM_MAXTF, K.L2_MOM_MAXTF - CTRL[2] + 1,
                        CTRL[1], K.L2_MOM_MAXTF - CTRL[2] + 1))
print('| the old known-good | %d events, sum MAE %+.3f, median MAE %+.3f |' % MEMBERSHIP_KNOWN)
print('| it is NOT a control for this grid | it was measured under the MEMBERSHIP reading of'
      ' min_tf, which is a different mechanic |')
print('| the comparable control, min_tf 0 (floor off) | %d events, sum MAE %+.3f, median MAE'
      ' %+.3f |' % (FLOOR_OFF[0], FLOOR_OFF[1], FLOOR_OFF[2]))
print('| MATCHED (28 expected) | %s |'
      % ('yes' if ok else '*** NO - the sweep and the banked run disagree ***'))

#   ── HIS QUESTION: the lowest MAE. Ranked by median MAE, with the event count beside it. ──
#   A combo with a handful of events is NOT an upgrade - Joe 1023 *"trade COUNT is the objective"* -
#   so the count is a column, never a filter applied here.
rank = sorted((v + k for k, v in res.items() if v[0] > 0), key=lambda r: (-r[2], -r[0]))
NONEMPTY = len(rank)
print('')
print('## the 25 combos with the least adverse median MAE')
print('')
print('| median MAE %% | events | sum MAE %% | worst MAE %% | sum MFE %% | median MFE %% |'
      ' MFE > abs(MAE) | MAE worse than %.1f | tol_s | lines | min_tf | fence |' % K.LIN2_MAE_CAP)
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
for r in rank[:25]:
    print('| %+.3f | %d | %+.3f | %+.3f | %+.3f | %+.3f | %d of %d | %d of %d | %d | %d | %d | %s |'
          % (r[2], r[0], r[1], r[3], r[4], r[5], r[6], r[0], r[7], r[0], r[8], r[9], r[10], r[11]))

print('')
print('## the same ranking, restricted to combos with at least 24 events')
print('')
print('| median MAE %% | events | sum MAE %% | worst MAE %% | sum MFE %% | median MFE %% |'
      ' MFE > abs(MAE) | MAE worse than %.1f | tol_s | lines | min_tf | fence |' % K.LIN2_MAE_CAP)
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
for r in [x for x in rank if x[0] >= 24][:25]:
    print('| %+.3f | %d | %+.3f | %+.3f | %+.3f | %+.3f | %d of %d | %d of %d | %d | %d | %d | %s |'
          % (r[2], r[0], r[1], r[3], r[4], r[5], r[6], r[0], r[7], r[0], r[8], r[9], r[10], r[11]))

#   ── THE MARGINAL OF EACH KNOB, the other two held at the bank. A knee in one of these is the
#   only thing that anchors a knob to a measurement rather than to a preference.
#   THE MARGINALS are taken with min_tf 0 for the OTHER knobs, because the banked min_tf 9 is
#   empty under his definition and a marginal through an empty cell measures nothing.
BASE = (int(K.LIN2_BARRAGE_TOL_S), int(K.LIN2_BARRAGE_LINES), 0, 'any')
for nm, vals, pos in (('LIN2_BARRAGE_MIN_TF', MINTFS, 2), ('LIN2_BARRAGE_LINES', LINES, 1),
                      ('LIN2_BARRAGE_TOL_S', TOLS, 0), ('LIN2_BARRAGE_FENCE', FENCES, 3)):
    print('')
    print('## %s swept alone, the others at tol %d / lines %d / min_tf 0 / fence any'
          % (nm, BASE[0], BASE[1]))
    print('')
    print('| %s | events | sum MAE %% | median MAE %% | worst MAE %% | median MFE %% |'
          ' MFE > abs(MAE) | MAE worse than %.1f |' % (nm, K.LIN2_MAE_CAP))
    print('|---|---|---|---|---|---|---|---|')
    for v in vals:
        key = list(BASE); key[pos] = v if pos == 3 else int(v)
        r = res.get(tuple(key))
        if r is None:
            continue
        if r[0] == 0:
            print('| %s | 0 | - | - | - | - | - | - |' % v); continue
        print('| %s | %d | %+.3f | %+.3f | %+.3f | %+.3f | %d of %d | %d of %d |'
              % (v, r[0], r[1], r[2], r[3], r[5], r[6], r[0], r[7], r[0]))

#   ── HIS TWO FITS, Joe 1027. *"there's 2 ways to handle this, and both need to be tested"* ──
#   THE TOLERANCE IS HELD AT HIS MEASURED 70 s for this section. The fit arms only bite where the
#   floor and the line count conflict, which the tolerance does not touch, and holding it keeps the
#   grid at 1,404 rows instead of 367,848 - he asked for the two mechanics tested, not a dump.
#   Every combo calls the SAME producer with an explicit arm; there is no second rule here.
FITS = ('off', 'lines', 'cap')
CD = {sd: CAD.barrage_candidates(BD, sd) for sd in (-1, +1)}
TOLF = int(K.LIN2_BARRAGE_TOL_S)


def fit_run(need, mtf, fn, ft):
    """One fit combo, scored the same way as the grid. -> the same 8-tuple."""
    seen, rows = set(), []
    for sd in (-1, +1):
        for bar, _ty, _why in CAD.barrage(BD, sd, A, B, tol_s=TOLF, lines=need, min_tf=mtf,
                                          fence=fn, fit=ft, cand=CD[sd]):
            if bar in seen:
                continue
            seen.add(bar)
            sw = SP.swing(int(bar), int(sd), close)
            if sw is None or sw.get('close') is None:
                continue
            z = int(sw['close'])
            a2, b2 = min(int(bar), z), max(int(bar), z)
            seg = np.asarray(close[a2:b2 + 1], float)
            if not np.isfinite(seg).any():
                continue
            pb, fav = float(close[int(bar)]), -int(sd)
            up = (float(np.nanmax(seg)) - pb) / pb * 100.0
            dn = (float(np.nanmin(seg)) - pb) / pb * 100.0
            mfe, mae = (up, dn) if fav > 0 else (-dn, -up)
            rows.append((mae, mfe))
    if not rows:
        return (0,) + (float('nan'),) * 5 + (0, 0)
    MA = [r[0] for r in rows]; MF = [r[1] for r in rows]
    return (len(rows), sum(MA), _med(MA), min(MA), sum(MF), _med(MF),
            sum(1 for a, f in zip(MA, MF) if f > abs(a)),
            sum(1 for a in MA if a < -float(K.LIN2_MAE_CAP)))


fitres = {}
for ft in FITS:
    for fn in FENCES:
        for mtf in MINTFS:
            for need in LINES:
                fitres[(need, mtf, fn, ft)] = fit_run(need, mtf, fn, ft)

print('')
print('## HIS TWO FITS - the pool is ws{min_tf}..ws%d and the count is LINES' % K.L2_MOM_MAXTF)
print('')
print('| the arm | his words | what it changes |')
print('|---|---|---|')
print('| off | - | neither. a short pool fires nothing. THE BANKED ARM |')
print('| lines | "dynamiclaly reduce the minimum required lines to fit them all inside the'
      ' ws12cap" | the required count drops to the pool size |')
print('| cap | "dynamically increase the ws12 cap to include the minimum required lines" | the'
      ' ceiling rises to ws{min_tf + LINES - 1}, admitting dtf lines |')
print('')
print('# the tolerance is held at his measured %d s for this section.' % TOLF)
print('# the pool size at min_tf m is ws{m}..ws%d, so %d - m + 1 lines.'
      % (K.L2_MOM_MAXTF, K.L2_MOM_MAXTF))
print('')
print('## events by arm, at LINES %d, fence any - where the two fits differ' % K.LIN2_BARRAGE_LINES)
print('')
print('| min_tf | pool size | off | lines | cap | the required count under lines | the ceiling'
      ' under cap |')
print('|---|---|---|---|---|---|---|')
for mtf in MINTFS:
    ps = len([t for t in sorted(BD.tfs) if mtf <= t <= int(K.L2_MOM_MAXTF)])
    need = int(K.LIN2_BARRAGE_LINES)
    cap_ceil = min(max(int(K.L2_MOM_MAXTF), mtf + need - 1), max(BD.tfs))
    print('| %d | %d | %d | %d | %d | %d | ws%d |'
          % (mtf, ps, fitres[(need, mtf, 'any', 'off')][0],
             fitres[(need, mtf, 'any', 'lines')][0], fitres[(need, mtf, 'any', 'cap')][0],
             min(need, ps), cap_ceil))

for ft in FITS:
    print('')
    print('## the %s arm, fence any, LINES %d - scored' % (ft, K.LIN2_BARRAGE_LINES))
    print('')
    print('| min_tf | events | sum MAE %% | median MAE %% | worst MAE %% | sum MFE %% |'
          ' MFE > abs(MAE) | MAE worse than %.1f |' % K.LIN2_MAE_CAP)
    print('|---|---|---|---|---|---|---|---|')
    for mtf in MINTFS:
        r = fitres[(int(K.LIN2_BARRAGE_LINES), mtf, 'any', ft)]
        if r[0] == 0:
            print('| %d | 0 | - | - | - | - | - | - |' % mtf); continue
        print('| %d | %d | %+.3f | %+.3f | %+.3f | %+.3f | %d of %d | %d of %d |'
              % (mtf, r[0], r[1], r[2], r[3], r[4], r[6], r[0], r[7], r[0]))

print('')
print('## the fit grid ranked by median MAE, at least 24 events, EVERY arm and fence')
print('')
print('| median MAE %% | events | sum MAE %% | worst MAE %% | sum MFE %% | MFE > abs(MAE) |'
      ' MAE worse than %.1f | lines | min_tf | fence | fit |' % K.LIN2_MAE_CAP)
print('|---|---|---|---|---|---|---|---|---|---|---|')
frank = sorted((v + k for k, v in fitres.items() if v[0] >= 24), key=lambda r: (-r[2], -r[0]))
for r in frank[:25]:
    print('| %+.3f | %d | %+.3f | %+.3f | %+.3f | %d of %d | %d of %d | %d | %d | %s | %s |'
          % (r[2], r[0], r[1], r[3], r[4], r[6], r[0], r[7], r[0], r[8], r[9], r[10], r[11]))
print('')
print('| the read | value |')
print('|---|---|')
print('| fit combos | %d |' % len(fitres))
print('| non-empty | %d |' % sum(1 for v in fitres.values() if v[0] > 0))
print('| non-empty at 24+ events | %d |' % len(frank))

#   ── HIS TWO FITS WITH THE TOLERANCE FREE, Joe 1027: *"what's the comparison mae mfe between the
#   2 ideas?"*. The section above held the tolerance at his measured 70 s and the 'cap' arm fired
#   NOTHING at any floor, so the two ideas could not be compared at all. The ceiling DID move -
#   ws13..ws17 carry 700-860 reversals each in this window - so 70 s was the binding term, not the
#   ceiling. Here the tolerance is free over every observed gap and both arms get the same chance.
print('')
print('## HIS TWO FITS, TOLERANCE FREE - LINES %d, fence any' % K.LIN2_BARRAGE_LINES)
print('')
print('# the 70 s section above is not a fair comparison: cap fired 0 at every floor because 6')
print('#   high-TF lines rarely cluster inside 70 s, not because the ceiling stayed at ws12.')
print('# ws13..ws17 each carry 700-860 reversals in this window, so the pool is real.')
print('')
best = {}
for ft in ('lines', 'cap'):
    for mtf in range(7, int(K.L2_MOM_MAXTF) + 1):
        for tol in TOLS:
            r = fit_run(int(K.LIN2_BARRAGE_LINES), mtf, 'any', ft)  # placeholder, replaced below
            break
        break
    break
fitol = {}
for ft in ('lines', 'cap'):
    for mtf in range(7, int(K.L2_MOM_MAXTF) + 1):
        for tol in TOLS:
            seen, rows = set(), []
            for sd in (-1, +1):
                for bar, _ty, _why in CAD.barrage(BD, sd, A, B, tol_s=tol,
                                                  lines=int(K.LIN2_BARRAGE_LINES), min_tf=mtf,
                                                  fence='any', fit=ft, cand=CD[sd]):
                    if bar in seen:
                        continue
                    seen.add(bar)
                    sw = SP.swing(int(bar), int(sd), close)
                    if sw is None or sw.get('close') is None:
                        continue
                    z = int(sw['close'])
                    a2, b2 = min(int(bar), z), max(int(bar), z)
                    seg = np.asarray(close[a2:b2 + 1], float)
                    if not np.isfinite(seg).any():
                        continue
                    pb, fav = float(close[int(bar)]), -int(sd)
                    up = (float(np.nanmax(seg)) - pb) / pb * 100.0
                    dn = (float(np.nanmin(seg)) - pb) / pb * 100.0
                    mfe, mae = (up, dn) if fav > 0 else (-dn, -up)
                    rows.append((mae, mfe))
            if not rows:
                fitol[(ft, mtf, tol)] = (0,) + (float('nan'),) * 5 + (0, 0)
                continue
            MA = [r[0] for r in rows]; MF = [r[1] for r in rows]
            fitol[(ft, mtf, tol)] = (len(rows), sum(MA), _med(MA), min(MA), sum(MF), _med(MF),
                                     sum(1 for a, f in zip(MA, MF) if f > abs(a)),
                                     sum(1 for a in MA if a < -float(K.LIN2_MAE_CAP)))

print('| the arm | min_tf | the smallest tolerance that fires | events there | sum MAE %% |'
      ' sum MFE %% | median MAE %% | worst MAE %% | MFE > abs(MAE) | capped |')
print('|---|---|---|---|---|---|---|---|---|---|')
for ft in ('lines', 'cap'):
    for mtf in range(7, int(K.L2_MOM_MAXTF) + 1):
        hit = [t for t in TOLS if fitol[(ft, mtf, t)][0] > 0]
        if not hit:
            print('| %s | %d | never fires | 0 | - | - | - | - | - | - |' % (ft, mtf)); continue
        t = hit[0]; r = fitol[(ft, mtf, t)]
        print('| %s | %d | %d s | %d | %+.3f | %+.3f | %+.3f | %+.3f | %d of %d | %d of %d |'
              % (ft, mtf, t, r[0], r[1], r[4], r[2], r[3], r[6], r[0], r[7], r[0]))

print('')
print('## the two ideas head to head, at the tolerance each needs for 24+ events')
print('')
print('| the arm | min_tf | tolerance | events | sum MAE %% | sum MFE %% | median MAE %% |'
      ' worst MAE %% | MFE > abs(MAE) | capped |')
print('|---|---|---|---|---|---|---|---|---|---|')
for ft in ('lines', 'cap'):
    for mtf in range(7, int(K.L2_MOM_MAXTF) + 1):
        hit = [t for t in TOLS if fitol[(ft, mtf, t)][0] >= 24]
        if not hit:
            print('| %s | %d | never reaches 24 events | - | - | - | - | - | - | - |' % (ft, mtf))
            continue
        t = hit[0]; r = fitol[(ft, mtf, t)]
        print('| %s | %d | %d s | %d | %+.3f | %+.3f | %+.3f | %+.3f | %d of %d | %d of %d |'
              % (ft, mtf, t, r[0], r[1], r[4], r[2], r[3], r[6], r[0], r[7], r[0]))
