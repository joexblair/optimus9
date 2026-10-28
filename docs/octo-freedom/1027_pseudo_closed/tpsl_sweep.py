"""TP x SL x SIGNALLING LINE, TARGETED ON NET. Joe 1028:

    "sweep the tp, sl, and the signalling line: ws15, ws10, ws30 / use net % as the sweeps target"

DRAG IS 0.1975% ROUND TRIP, the figure o9-live carries: 11.0 bps taker fee (2 x 5.50, a set Bybit
rate) + 8.75 bps slippage. docs/o9-live-recon/OPEN.md, and it is live as `drag_pct` in o9_control.

    NOT 0.55% - that is the stale sneaky_trade_1 figure from Joe 0916, before slippage was measured.
    NOT 0.29% - his recollection; nothing in the repo carries it.

THE SLIPPAGE HALF IS AN ASSUMPTION, and the doc says so: 8.75 bps was measured ONCE at 22,000 coins
and is applied FLAT regardless of size or book depth. o9-live measures per fill instead, so a
backtest net and a live net are not the same quantity. Joe 0929 ruled slippage is not to be
modelled further in the backtest, so the flat figure is the ruled one.

DRAG IS ITS OWN COLUMN AND ITS OWN TOTAL, his standing rule.
BREAK-EVEN: a trade must average above 0.1975% to stand still, so a TP below that cannot pay at
any hit rate.

THE CHAIN per signalling line: every closed ws{N}r reversal, both sides, in order. Each closes the
open trade and opens the next. Open = the reversal's stamp + 1; the exit is whichever comes FIRST -
the TP, the SL, or the next reversal's stamp.

FIRST TOUCH IS EXACT: the running favourable max and adverse max are built per leg and both touch
bars are looked up. Ties go to the SL - my convention, the conservative one.

BOTH SIDE-MAP ARMS, because the reversal-side to trade-side map is an input, never derived.
THE GRIDS ARE DATA-ANCHORED: TP 0.1 to the largest favourable excursion any leg reached, SL 0.1 to
the largest adverse. Past either, no leg could touch, so the data ends both domains.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
from optimus9.analysis.jig import lift_off
from v4_backstop_trades import prices
sys.stderr = _e

DRAG = 0.1975
A, B = ln.K('2026-08-31 00:00:00'), ln.K('2026-09-03 23:59:55')
close, PHI, PLO = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
LINES = [15, 10, 30]

print('# TP x SL x SIGNALLING LINE, TARGETED ON NET, %s .. %s' % (ln.U(A), ln.U(B)))
print('# NET = sum realised - trades x %.4f%%. DRAG is o9-live\'s figure: 11.0 bps fee +' % DRAG)
print('#   8.75 bps slippage round trip (docs/o9-live-recon/OPEN.md, drag_pct in o9_control).')
print('#   NOT 0.55 (stale, pre-slippage) and NOT 0.29 (not in the repo).')
print('# the slippage half is measured ONCE at 22,000 coins and applied FLAT - the doc says so.')
print('# BREAK-EVEN per trade is %.4f%%, so a TP below that cannot pay at any hit rate.' % DRAG)
print('# first touch is exact; ties go to the SL. both side-map arms. RULED_OK %s' % K.RULED_OK)
print('')
BEST = []
for t in LINES:
    em = np.asarray(E[t], float)
    cl = CP.series(em, t * 60)
    SIDES = {}
    for sd in (-1, +1):
        for raw in lift_off(cl, sd, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL, int(K.LIFT_WOB)):
            st = int(raw) + int(K.LIFT_WOB) - 1
            if A <= st <= B:
                SIDES[st] = int(sd)
    EV = sorted(SIDES)
    legs = [(EV[i] + 1, EV[i + 1], SIDES[EV[i]]) for i in range(len(EV) - 1)
            if EV[i] + 1 < EV[i + 1]]
    PRE = {}
    for d in (-1, +1):
        rows = []
        for en, ex, _sd in legs:
            p0 = float(close[en])
            hi = (np.asarray(PHI[en:ex + 1], float) - p0) / p0 * 100.0
            lo = (np.asarray(PLO[en:ex + 1], float) - p0) / p0 * 100.0
            fav = np.maximum.accumulate(hi if d > 0 else -lo)
            adv = np.maximum.accumulate(-lo if d > 0 else hi)   # positive = adverse magnitude
            rows.append((fav, adv, (float(close[ex]) - p0) / p0 * 100.0 * d))
        PRE[d] = rows
    fmax = max(float(r[0][-1]) for d in (-1, +1) for r in PRE[d])
    amax = max(float(r[1][-1]) for d in (-1, +1) for r in PRE[d])
    TPS = [round(0.1 * i, 1) for i in range(1, int(np.ceil(fmax / 0.1)) + 1)]
    SLS = [round(0.1 * i, 1) for i in range(1, int(np.ceil(amax / 0.1)) + 1)]
    print('## ws%dr - %d reversals in range, %d legs. TP grid 0.1..%.1f, SL grid 0.1..%.1f'
          % (t, len(EV), len(legs), TPS[-1], SLS[-1]))
    print('')
    for arm, hi_dir in (('A: HIGH->SHORT', -1), ('B: HIGH->LONG', +1)):
        res = []
        for tp in TPS:
            for sl in SLS:
                tot = 0.0; n_tp = n_sl = n_rv = 0
                for k, (_en, _ex, sd) in enumerate(legs):
                    d = hi_dir if sd > 0 else -hi_dir
                    fav, adv, rev = PRE[d][k]
                    i_tp = int(np.searchsorted(fav, tp, side='left'))
                    i_sl = int(np.searchsorted(adv, sl, side='left'))
                    hit_tp, hit_sl = i_tp < len(fav), i_sl < len(adv)
                    if hit_sl and (not hit_tp or i_sl <= i_tp):
                        tot -= sl; n_sl += 1
                    elif hit_tp:
                        tot += tp; n_tp += 1
                    else:
                        tot += rev; n_rv += 1
                n = len(legs)
                res.append((tot - n * DRAG, tot, n * DRAG, n, n_tp, n_sl, n_rv, tp, sl))
        res.sort(reverse=True)
        print('### arm %s - the 8 best by NET' % arm)
        print('')
        print('| TP %% | SL %% | trades | TP hits | SL hits | held to reversal | gross %% |'
              ' drag %% | NET %% |')
        print('|---|---|---|---|---|---|---|---|---|')
        for r in res[:8]:
            print('| %.1f | %.1f | %d | %d | %d | %d | %+.3f | %.3f | %+.3f |'
                  % (r[7], r[8], r[3], r[4], r[5], r[6], r[1], r[2], r[0]))
        pos = sum(1 for r in res if r[0] > 0)
        print('')
        print('| ws%dr arm %s | value |' % (t, arm))
        print('|---|---|')
        print('| combos | %d |' % len(res))
        print('| combos with a POSITIVE net | %d |' % pos)
        print('| the best net %% | %+.3f at TP %.1f / SL %.1f |' % (res[0][0], res[0][7], res[0][8]))
        print('| its gross %% | %+.3f |' % res[0][1])
        print('| its drag %% | %.3f |' % res[0][2])
        print('')
        BEST.append((t, arm, res[0][0], res[0][7], res[0][8], res[0][3], res[0][1], res[0][2],
                     pos, len(res)))

print('## every line and arm, by net')
print('')
print('| the line | arm | trades | TP %% | SL %% | gross %% | drag %% | NET %% | positive combos |')
print('|---|---|---|---|---|---|---|---|---|')
for t, arm, net, tp, sl, n, gr, dg, pos, tot in sorted(BEST, key=lambda z: -z[2]):
    print('| ws%dr | %s | %d | %.1f | %.1f | %+.3f | %.3f | %+.3f | %d of %d |'
          % (t, arm, n, tp, sl, gr, dg, net, pos, tot))
