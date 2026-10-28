"""THE SLOW r LINES OVER THE FULL TAPE. Joe 1028: *"are we ignoring this for a reason?"*

NO GOOD REASON. ws120r produced 4 trades in the 08-31..09-03 window and I dismissed it on
sample size - but the window was MINE, inherited from his 4-day instruction, and a 120-minute
line needs ~20x that window to produce a comparable count. The full tape is 94 days.

SIGNALLING LINES: ws45r, ws60r, ws90r, ws120r only. The fast lines were already measured on
a window that suited them and all lost.

r x Mage MIX AND MATCH, WITH THE GATE'S TWO oob READINGS. Joe 1028:

    "1) if a long trade is printed while the mage is already low oob, does the LONG open?
        inverted for high oob
     2) mix and match the r's and mages (eg ws10Mage and ws15r) out of [5 10 15 30 45 60 90 120]"

IDEA 1 IS TWO GATE ARMS, because his question has two answers and only one was built:
    'while-oob'  the gate reads the last oob SIDE whether or not the Mage is still there. A LONG
                 opens while the Mage is sitting in low oob. THIS IS WHAT THE PREVIOUS RUN DID.
    'left-oob'   the trade is only allowed once the Mage has LEFT oob - the last oob side is known
                 AND the Mage is now inside the fence.

IDEA 2 IS ALL 64 (r TF, Mage TF) PAIRS from his eight: 5 10 15 30 45 60 90 120. ws45 and above are
not in the r ladder RS.load returns; they come from ln.line, which carries all eight for both r and
Mage.

EVERYTHING ELSE IS THE PREVIOUS SWEEP UNCHANGED: the signal is the CLOSED ws{r}r reversal, both
sides; open = stamp + 1; exit = whichever comes FIRST of the TP, the SL, or the next reversal;
first touch exact with ties to the SL; both side-map arms; DRAG 0.1975% round trip, o9-live's
figure; TP and SL grids data-anchored per pair.

256 CELLS: 64 pairs x 2 side arms x 2 gate arms. The file carries every one; a reply carries the
top rows, because a sweep is not a dump.
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

DRAG = 0.1975
A, B = ln.K('2026-07-02 12:00:00'), ln.K('2026-10-04 23:59:55')
close, PHI, PLO = prices()
TFS = [5, 10, 15, 30, 45, 60, 90, 120]
RTFS = [45, 60, 90, 120]   # the SLOW signalling lines - 4 days starved them, the full tape does not

#   the gate state per Mage TF: the last oob side, and whether the Mage is oob right now
GATE = {}
for mt in TFS:
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
    GATE[mt] = (last, hi | lo)                      # (last oob side, is oob now)

#   the legs per signalling r TF - the SLOW ones only
LEG = {}
for rt in RTFS:
    em = np.asarray(ln.line('ws%dr' % rt), float)
    cl = CP.series(em, rt * 60)
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
    fmax = max([float(r[0][-1]) for d in (-1, +1) for r in pre[d]] or [0.1])
    amax = max([float(r[1][-1]) for d in (-1, +1) for r in pre[d]] or [0.1])
    TPS = np.array([round(0.1 * i, 1) for i in range(1, int(np.ceil(fmax / 0.1)) + 1)])
    SLS = np.array([round(0.1 * i, 1) for i in range(1, int(np.ceil(amax / 0.1)) + 1)])
    LEG[rt] = (legs, pre, TPS, SLS)

ROWS = []
for rt in RTFS:
    legs, pre, TPS, SLS = LEG[rt]
    for mt in TFS:
        last, isoob = GATE[mt]
        for arm, hi_dir in (('A HIGH->SHORT', -1), ('B HIGH->LONG', +1)):
            for garm in ('while-oob', 'left-oob'):
                take = []
                for k, (en, _ex, sd) in enumerate(legs):
                    d = hi_dir if sd > 0 else -hi_dir
                    g = int(last[en])
                    if g == 0:
                        continue
                    if garm == 'left-oob' and bool(isoob[en]):
                        continue
                    if d != (+1 if g < 0 else -1):
                        continue
                    take.append((k, d))
                n = len(take)
                if n == 0:
                    continue
                TOT = np.zeros((len(TPS), len(SLS)))
                NTP = np.zeros_like(TOT); NSL = np.zeros_like(TOT)
                for k, d in take:
                    fav, adv, rev = pre[d][k]
                    itp = np.searchsorted(fav, TPS, side='left')
                    isl = np.searchsorted(adv, SLS, side='left')
                    htp = (itp < len(fav))[:, None]
                    hsl = (isl < len(adv))[None, :]
                    stop = hsl & (~htp | (isl[None, :] <= itp[:, None]))
                    tpok = (~stop) & htp
                    TOT += np.where(stop, -SLS[None, :], np.where(tpok, TPS[:, None], rev))
                    NTP += tpok; NSL += stop
                NET = TOT - n * DRAG
                i, j = np.unravel_index(int(np.argmax(NET)), NET.shape)
                ROWS.append((float(NET[i, j]), rt, mt, arm, garm, n, float(TPS[i]), float(SLS[j]),
                             float(TOT[i, j]), n * DRAG, int(NTP[i, j]), int(NSL[i, j]),
                             int((NET > 0).sum()), NET.size, len(legs)))

ROWS.sort(reverse=True)
print('# r x Mage MIX AND MATCH, %s .. %s' % (ln.U(A), ln.U(B)))
print('# the signal is the CLOSED ws{r}r reversal; the gate is ws{Mage}Mage\'s last oob SIDE.')
print('# gate arms: while-oob allows the trade with the Mage STILL oob (what the last run did);')
print('#   left-oob requires the Mage to have LEFT oob first. HIS idea 1, both readings.')
print('# TFs: %s, for r and Mage independently - HIS idea 2, all 64 pairs.'
      % ' '.join(str(t) for t in TFS))
print('# DRAG %.4f%% round trip (o9-live). first touch exact, ties to the SL.' % DRAG)
print('# %d cells. RULED_OK %s' % (len(ROWS), K.RULED_OK))
print('')
print('| NET %% | the r | the Mage | arm | gate | trades | TP %% | SL %% | gross %% | drag %% |'
      ' TP hits | SL hits | gross/trade %% | positive combos |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for r in ROWS:
    print('| %+.3f | ws%dr | ws%dMage | %s | %s | %d | %.1f | %.1f | %+.3f | %.3f | %d | %d |'
          ' %+.4f | %d of %d |'
          % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11],
             r[8] / r[5], r[12], r[13]))
print('')
print('| the read | value |')
print('|---|---|')
print('| cells | %d |' % len(ROWS))
print('| cells with a positive best net | %d |' % sum(1 for r in ROWS if r[0] > 0))
print('| cells where gross/trade beats the %.4f%% drag | %d |'
      % (DRAG, sum(1 for r in ROWS if r[8] / r[5] > DRAG)))
print('| the best net %% | %+.3f on ws%dr / ws%dMage, arm %s, gate %s |'
      % (ROWS[0][0], ROWS[0][1], ROWS[0][2], ROWS[0][3], ROWS[0][4]))
print('| its trades | %d |' % ROWS[0][5])
