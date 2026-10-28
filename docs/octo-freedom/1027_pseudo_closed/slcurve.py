"""DOES THE EDGE SURVIVE A REAL STOP? Joe 1028, after the full-tape run.

The best cell netted +61.263% with SL 15.2% and ZERO stop hits - 178 of 193 trades simply held to
the next reversal. That is not risk control, and his own MAE 1.1 cap was the premise an hour
earlier. This walks the SL down to where a stop actually fires, and reports what the net does.

PER CELL, the SL is swept across the WHOLE grid at the cell's best TP, and three SL values are
called out: his 1.1 cap, the SL where stop hits first exceed a tenth of the trades, and the cell's
own best. The TP is held at the cell's best so the SL axis is read alone.

THE CELLS are the top six from mixmatch_full.md, by net. No new search; this is the same six
re-read under a stop that works.

FULL TAPE, 94 days. DRAG 0.1975%. First touch exact, ties to the SL.
BUY AND HOLD over the same tape is +21.779%, which is the bar any long-biased arm has to clear.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_closed_prev as CP
from optimus9.analysis.jig import lift_off
from v4_backstop_trades import prices
sys.stderr = _e

DRAG, BH = 0.1975, 21.779
A, B = ln.K('2026-07-02 12:00:00'), ln.K('2026-10-04 23:59:55')
close, PHI, PLO = prices()
CELLS = [(90, 120, +1, 'while-oob', 5.0), (120, 5, +1, 'while-oob', 6.1),
         (120, 120, +1, 'left-oob', 5.4), (90, 120, +1, 'left-oob', 5.8),
         (120, 90, +1, 'left-oob', 7.0), (120, 60, +1, 'left-oob', 6.7)]

GATE = {}
for mt in {c[1] for c in CELLS}:
    mg = CP.series(np.asarray(ln.line('ws%dMage' % mt), float), mt * 60)
    hi = np.array([bool(K.oob(v, +1)) for v in mg])
    lo = np.array([bool(K.oob(v, -1)) for v in mg])
    last = np.zeros(len(mg), np.int8); cur = 0
    for i in range(len(mg)):
        if hi[i]:
            cur = +1
        elif lo[i]:
            cur = -1
        last[i] = cur
    GATE[mt] = (last, hi | lo)

LEG = {}
for rt in {c[0] for c in CELLS}:
    cl = CP.series(np.asarray(ln.line('ws%dr' % rt), float), rt * 60)
    sides = {}
    for sd in (-1, +1):
        for raw in lift_off(cl, sd, K.LIFT_PTS, K.gap_for(rt), K.LIFT_TOL, int(K.LIFT_WOB)):
            st = int(raw) + int(K.LIFT_WOB) - 1
            if A <= st <= B:
                sides[st] = int(sd)
    ev = sorted(sides)
    legs = [(ev[i] + 1, ev[i + 1], sides[ev[i]]) for i in range(len(ev) - 1)
            if ev[i] + 1 < ev[i + 1]]
    pre = {}
    for d in (-1, +1):
        rows = []
        for en, ex, _s in legs:
            p0 = float(close[en])
            h = (np.asarray(PHI[en:ex + 1], float) - p0) / p0 * 100.0
            l = (np.asarray(PLO[en:ex + 1], float) - p0) / p0 * 100.0
            rows.append((np.maximum.accumulate(h if d > 0 else -l),
                         np.maximum.accumulate(-l if d > 0 else h),
                         (float(close[ex]) - p0) / p0 * 100.0 * d))
        pre[d] = rows
    LEG[rt] = (legs, pre)

print('# DOES THE EDGE SURVIVE A REAL STOP? full tape %s .. %s' % (ln.U(A), ln.U(B)))
print('# the SL is swept at each cell\'s BEST TP, so the SL axis is read alone.')
print('# BUY AND HOLD over the same tape is %+.3f%% - the bar a long-biased arm must clear.' % BH)
print('# DRAG %.4f%%. first touch exact, ties to the SL. RULED_OK %s' % (DRAG, K.RULED_OK))
print('')
for rt, mt, hi_dir, garm, tp in CELLS:
    legs, pre = LEG[rt]
    last, isoob = GATE[mt]
    take = []
    for k, (en, _ex, sd) in enumerate(legs):
        d = hi_dir if sd > 0 else -hi_dir
        g = int(last[en])
        if g == 0 or (garm == 'left-oob' and bool(isoob[en])):
            continue
        if d != (+1 if g < 0 else -1):
            continue
        take.append((k, d))
    print('## ws%dr signalled, ws%dMage gated, arm %s, gate %s, TP %.1f%% - %d trades'
          % (rt, mt, 'B HIGH->LONG' if hi_dir > 0 else 'A HIGH->SHORT', garm, tp, len(take)))
    print('')
    print('| SL %% | trades | TP hits | SL hits | held to reversal | gross %% | drag %% | NET %% |'
          ' gross/trade %% | beats buy and hold |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for sl in [0.5, 0.8, 1.1, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 15.2]:
        tot = 0.0; n_tp = n_sl = n_rv = 0
        for k, d in take:
            fav, adv, rev = pre[d][k]
            itp = int(np.searchsorted(fav, tp, side='left'))
            isl = int(np.searchsorted(adv, sl, side='left'))
            htp, hsl = itp < len(fav), isl < len(adv)
            if hsl and (not htp or isl <= itp):
                tot -= sl; n_sl += 1
            elif htp:
                tot += tp; n_tp += 1
            else:
                tot += rev; n_rv += 1
        n = len(take)
        net = tot - n * DRAG
        mark = '**his 1.1 cap**' if abs(sl - 1.1) < 1e-9 else ''
        print('| %.1f %s | %d | %d | %d | %d | %+.3f | %.3f | %+.3f | %+.4f | %s |'
              % (sl, mark, n, n_tp, n_sl, n_rv, tot, n * DRAG, net, tot / n,
                 'yes' if net > BH else 'no'))
    print('')
