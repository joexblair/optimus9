"""A TAKE-PROFIT SWEEP ON THE ws13r REVERSAL CHAIN. Joe 1028: *"see if you can find a take-profit
level that's profitable"*.

EACH TRADE EXITS ON WHICHEVER COMES FIRST, walked bar by bar from the entry:
    the TP          the favourable excursion reaches the level  -> realised +TP
    the stop        the adverse excursion reaches LIN2_MAE_CAP  -> realised -1.1, his pseudo-stop
    the next reversal   neither was touched                     -> the directional close-to-close

THE FIRST-TOUCH ORDER IS WALKED, not inferred from the trade's MAE and MFE. A trade whose MFE
reaches the TP is only a win if the TP came before the stop.

INTRA-BAR TIES GO TO THE ADVERSE SIDE. Inside one 5 s bar the high and the low are both present
and their order is unknown, so a bar that breaches both is scored as the stop. That is MY
convention, it is the conservative one, and it is stated rather than buried.

THE TP GRID IS DATA-ANCHORED: 0.1% to the largest MFE any trade reached, in 0.1 steps. Past that
no trade could ever hit, so the data ends the domain and no cap is chosen.

BOTH SIDE-MAP ARMS are run, because the reversal-side to trade-side map is an input.
NO DRAG IS MODELLED - the nets are gross.
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

A, B = ln.K('2026-08-31 00:00:00'), ln.K('2026-09-03 23:59:55')
close, PHI, PLO = prices()
em = np.asarray(RS.load((RS.K0, RS.R0, RS.S0))[13], float)
cl = CP.series(em, 13 * 60)
CAP = float(K.LIN2_MAE_CAP)

EV = []
for sd in (-1, +1):
    for raw in lift_off(cl, sd, K.LIFT_PTS, K.gap_for(13), K.LIFT_TOL, int(K.LIFT_WOB)):
        st = int(raw) + int(K.LIFT_WOB) - 1
        if A <= st <= B:
            EV.append((st, int(sd)))
EV.sort()

LEGS = []
for i in range(len(EV) - 1):
    st, sd = EV[i]
    en, ex = st + 1, EV[i + 1][0]
    if en < ex:
        LEGS.append((en, ex, sd))

_med = lambda v: sorted(v)[len(v) // 2] if v else float('nan')


def walk(en, ex, d, tp):
    """-> ('tp'|'stop'|'rev', realised %). First touch, walked. Ties go to the adverse side."""
    p0 = float(close[en])
    for b in range(en, ex + 1):
        hi, lo = float(PHI[b]), float(PLO[b])
        adv = ((lo - p0) if d > 0 else (p0 - hi)) / p0 * 100.0
        fav = ((hi - p0) if d > 0 else (p0 - lo)) / p0 * 100.0
        if adv <= -CAP:
            return 'stop', -CAP
        if fav >= tp:
            return 'tp', tp
    return 'rev', (float(close[ex]) - p0) / p0 * 100.0 * d


#   the domain end: the largest favourable excursion any trade reaches, on either arm
mx = 0.0
for en, ex, sd in LEGS:
    for d in (-1, +1):
        p0 = float(close[en])
        hi = float(np.nanmax(PHI[en:ex + 1])); lo = float(np.nanmin(PLO[en:ex + 1]))
        mx = max(mx, ((hi - p0) if d > 0 else (p0 - lo)) / p0 * 100.0)
GRID = [round(0.1 * i, 1) for i in range(1, int(np.ceil(mx / 0.1)) + 1)]

print('# A TAKE-PROFIT SWEEP ON THE ws13r REVERSAL CHAIN, %s .. %s' % (ln.U(A), ln.U(B)))
print('# exit = whichever comes FIRST, walked bar by bar: the TP, the %.1f%% stop, or the next'
      % CAP)
print('#   reversal. intra-bar ties go to the ADVERSE side - my convention, the conservative one.')
print('# the TP grid is 0.1 .. %.1f in 0.1 steps - %.1f is the largest excursion any trade reached,'
      % (GRID[-1], mx))
print('#   so the data ends the domain. %d legs. NO DRAG - the nets are gross.' % len(LEGS))
print('# RULED_OK %s' % K.RULED_OK)
print('')
for arm, hi_dir in (('ARM A - HIGH reversal opens SHORT', -1),
                    ('ARM B - HIGH reversal opens LONG', +1)):
    print('## %s' % arm)
    print('')
    print('| TP %% | trades | TP hits | stop hits | held to the next reversal | NET realised %% |'
          ' median realised %% | winners |')
    print('|---|---|---|---|---|---|---|---|')
    best = None
    for tp in GRID:
        res = [walk(en, ex, hi_dir if sd > 0 else -hi_dir, tp) for en, ex, sd in LEGS]
        RL = [r[1] for r in res]
        n_tp = sum(1 for k, _ in res if k == 'tp')
        n_st = sum(1 for k, _ in res if k == 'stop')
        n_rv = sum(1 for k, _ in res if k == 'rev')
        net = sum(RL)
        print('| %.1f | %d | %d | %d | %d | %+.3f | %+.3f | %d of %d |'
              % (tp, len(res), n_tp, n_st, n_rv, net, _med(RL),
                 sum(1 for x in RL if x > 0), len(RL)))
        if best is None or net > best[1]:
            best = (tp, net)
    print('')
    print('| %s | value |' % arm.split(' - ')[0])
    print('|---|---|')
    print('| the best TP by net | %.1f%% |' % best[0])
    print('| its net realised %% (gross) | %+.3f |' % best[1])
    print('| profitable TP levels | %d of %d |'
          % (sum(1 for tp in GRID
                 if sum(r[1] for r in [walk(en, ex, hi_dir if sd > 0 else -hi_dir, tp)
                                       for en, ex, sd in LEGS]) > 0), len(GRID)))
    print('')
