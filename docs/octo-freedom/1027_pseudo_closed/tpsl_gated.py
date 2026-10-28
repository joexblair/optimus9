"""TP x SL x SIGNALLING LINE, WITH HIS Mage SIDE GATE. Joe 1028:

    "add this gate to the trades: if the associated (same TF) Mage was last oob on the low side,
     allow only LONG trades. if the last oob was high side, allow only short trades"

THE GATE, at each trade's OPEN bar: find the most recent bar at or before it where ws{N}Mage was
oob, and read which side.
    last oob LOW  -> only a LONG may open
    last oob HIGH -> only a SHORT may open
A trade whose mapped direction disagrees is NOT TAKEN, so it also carries no drag. That is where a
directional gate can move a net: it removes cost as well as outcome.

THE Mage IS THE CLOSED READ, same as the signalling line, so the gate and the signal see the same
kind of bar. oob is K.oob - the 15/85 fence, one home.

NO PRIOR oob = NOT TAKEN, and the count is reported. The gate has no state before the Mage has
been oob once; skipping is the choice that invents nothing, and it only touches the first trades.

DRAG 0.1975% round trip, o9-live's figure. Everything else is the previous sweep unchanged: first
touch exact, ties to the SL, both side-map arms, data-anchored TP and SL grids.
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

print('# TP x SL x LINE, WITH HIS Mage SIDE GATE, %s .. %s' % (ln.U(A), ln.U(B)))
print('# the gate: ws{N}Mage\'s LAST oob side at the open bar. low -> LONG only, high -> SHORT only.')
print('# a blocked trade is NOT TAKEN, so it carries no drag either.')
print('# the Mage is the CLOSED read, same as the signal. oob is K.oob, the 15/85 fence.')
print('# no prior oob = not taken; the count is reported. DRAG %.4f%% round trip (o9-live).' % DRAG)
print('# RULED_OK %s' % K.RULED_OK)
print('')
BEST = []
for t in LINES:
    em = np.asarray(E[t], float)
    cl = CP.series(em, t * 60)
    mg = CP.series(np.asarray(ln.line('ws%dMage' % t), float), t * 60)
    #   the gate's state per bar: +1 the last oob was HIGH, -1 LOW, 0 never yet
    hi_m = np.array([bool(K.oob(v, +1)) for v in mg])
    lo_m = np.array([bool(K.oob(v, -1)) for v in mg])
    state = np.zeros(len(mg), np.int8)
    cur = 0
    for i in range(len(mg)):
        if hi_m[i]:
            cur = +1
        elif lo_m[i]:
            cur = -1
        state[i] = cur

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
            rows.append((np.maximum.accumulate(hi if d > 0 else -lo),
                         np.maximum.accumulate(-lo if d > 0 else hi),
                         (float(close[ex]) - p0) / p0 * 100.0 * d))
        PRE[d] = rows
    fmax = max(float(r[0][-1]) for d in (-1, +1) for r in PRE[d])
    amax = max(float(r[1][-1]) for d in (-1, +1) for r in PRE[d])
    TPS = [round(0.1 * i, 1) for i in range(1, int(np.ceil(fmax / 0.1)) + 1)]
    SLS = [round(0.1 * i, 1) for i in range(1, int(np.ceil(amax / 0.1)) + 1)]
    print('## ws%dr signalled, gated by ws%dMage - %d legs before the gate' % (t, t, len(legs)))
    print('')
    for arm, hi_dir in (('A: HIGH->SHORT', -1), ('B: HIGH->LONG', +1)):
        #   the gate verdict per leg: taken or not, under this arm
        take, nostate, blocked = [], 0, 0
        for k, (en, _ex, sd) in enumerate(legs):
            d = hi_dir if sd > 0 else -hi_dir           # +1 LONG, -1 SHORT
            g = int(state[en])
            if g == 0:
                nostate += 1
                continue
            allowed = +1 if g < 0 else -1               # last oob LOW -> LONG, HIGH -> SHORT
            if d != allowed:
                blocked += 1
                continue
            take.append((k, d))
        res = []
        for tp in TPS:
            for sl in SLS:
                tot = 0.0; n_tp = n_sl = n_rv = 0
                for k, d in take:
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
                n = len(take)
                res.append((tot - n * DRAG, tot, n * DRAG, n, n_tp, n_sl, n_rv, tp, sl))
        res.sort(reverse=True)
        print('### arm %s - %d of %d legs taken (%d blocked by the gate, %d with no gate state)'
              % (arm, len(take), len(legs), blocked, nostate))
        print('')
        if not take:
            print('no trades pass the gate on this arm.')
            print('')
            continue
        print('| TP %% | SL %% | trades | TP hits | SL hits | held to reversal | gross %% |'
              ' drag %% | NET %% |')
        print('|---|---|---|---|---|---|---|---|---|')
        for r in res[:8]:
            print('| %.1f | %.1f | %d | %d | %d | %d | %+.3f | %.3f | %+.3f |'
                  % (r[7], r[8], r[3], r[4], r[5], r[6], r[1], r[2], r[0]))
        pos = sum(1 for r in res if r[0] > 0)
        print('')
        print('| ws%dr arm %s gated | value |' % (t, arm))
        print('|---|---|')
        print('| combos | %d |' % len(res))
        print('| combos with a POSITIVE net | %d |' % pos)
        print('| the best net %% | %+.3f at TP %.1f / SL %.1f |' % (res[0][0], res[0][7], res[0][8]))
        print('| its gross %% | %+.3f | ' % res[0][1])
        print('| its drag %% | %.3f |' % res[0][2])
        print('| gross per trade %% | %+.4f |' % (res[0][1] / res[0][3]))
        print('')
        BEST.append((t, arm, res[0][0], res[0][7], res[0][8], res[0][3], res[0][1], res[0][2],
                     pos, len(res), len(legs), blocked, nostate))

print('## every line and arm, GATED, by net')
print('')
print('| the line | arm | legs | taken | blocked | no state | TP %% | SL %% | gross %% | drag %% |'
      ' NET %% | positive combos |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
for t, arm, net, tp, sl, n, gr, dg, pos, tot, nl, bl, ns in sorted(BEST, key=lambda z: -z[2]):
    print('| ws%dr | %s | %d | %d | %d | %d | %.1f | %.1f | %+.3f | %.3f | %+.3f | %d of %d |'
          % (t, arm, nl, n, bl, ns, tp, sl, gr, dg, net, pos, tot))
