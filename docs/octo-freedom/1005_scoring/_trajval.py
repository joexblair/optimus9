"""VALIDATING traj's TRUE/FALSE RETURN AGAINST pxs — the TRAJ_TAIL_TF_SAMP sweep. 1009.

Joe 1009: *"this needs a pxs comparison based on the 4 #7 mechs to validate the TRUE FALSE return.
if you're up for it, then lets build and sweep"*.

THE RETURN, on Joe's #7 polarity, which is the same four cases whichever line supplies the
direction:
    TRUE   the traj direction OPPOSES the oob side -> pxs reverses -> ws12r prints a trade signal
    FALSE  the traj direction MATCHES the oob side -> no reversal  -> delegate to `>ws12r oob`
and when traj returns 0 (a wholly flat lookback) the caller falls back to Joe's #7:
    TRUE iff sign(ws60Mage - ws60r) == -(the oob side)

THE SCORER is swing_detect. Joe 1008: *"swing detect is strictly a backtest tool"*, so it never
reaches the mech. For a HIGH oob event a reversal is an 'L' pivot; for a LOW oob event an 'H'.
`pxs move against the oob side` is signed so + means price turned away from the oob side.

SWEPT
  TRAJ_TAIL_TF_SAMP   1 / 2 / 3 / 6 / 12 samples   = 5 / 10 / 15 / 30 / 60 min at block 60
  the sample kind     'close' / 'extreme'          MINE, unruled - see _trajmech's docstring
  the bar read        the ws12r oob CROSSING / the 6-min DWELL-ENDING
  swing_detect pct    1.0 / 0.9
HELD
  block 60 bars = 5 min (Joe 1009), TRAJ_MULTI_TF_SAMP 2 -> 24 samples (measured slack: the
  deferral never reached past 12 samples in 764 events)

THE BASE RATE IS THE FALSE COLUMN, printed beside TRUE on every row. A hit rate with no base rate
is not a measurement. Ranked on nothing - every row is printed, fit and hold separately.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute.swing_detect import find_pivots
from _trajmech import traj
import _chain10 as C

SC, box, U = C.SC, C.box, C.SC.U
PXa = C.PX
N = len(SC.ts)
R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
M60 = np.asarray(SC.LD(60 * 60, 'Mage'), float)[:N]
R12 = C.R[C.TRIG_TF]
HI, LO = SC.HI, SC.LO
GATE, BLOCK, LOOK_N = C.GATE_BARS, 60, 24
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                               datetime.timezone.utc).strftime('%Y-%m-%d')
_days = sorted({DAY(k) for k in range(0, N, 2000)})
BLK = {'all': set(_days), 'fit': set(_days[:47]), 'hold': set(_days[47:])}
print('# block %d bars = %.0f min, lookback %d samples = %.0f min, oob_gate_bars %d'
      % (BLOCK, BLOCK * 5 / 60.0, LOOK_N, LOOK_N * BLOCK * 5 / 60.0, GATE), flush=True)

EV = []
k = 1
while k < N:
    for side in (+1, -1):
        now = (float(R12[k]) >= HI) if side > 0 else (float(R12[k]) <= LO)
        was = (float(R12[k - 1]) >= HI) if side > 0 else (float(R12[k - 1]) <= LO)
        if now and not was:
            j = k
            while j < N and (((float(R12[j]) >= HI) if side > 0 else (float(R12[j]) <= LO))): j += 1
            EV.append((k, side, j - k)); break
    k += 1
print('# %d ws12r oob crossings; %d reach the dwell-ending'
      % (len(EV), sum(1 for _, _, r in EV if r > GATE + 1)), flush=True)

PIV = {}
for pct in (1.0, 0.9):
    pv = find_pivots(PXa, pct)
    ni = np.full(N, -1, np.int64); nk = np.zeros(N, np.int8)
    s_ = 0
    for b_, kd_ in pv:
        if b_ > s_:
            ni[s_:b_] = b_; nk[s_:b_] = 1 if kd_ == 'H' else -1
        s_ = b_
    PIV[pct] = (ni, nk)

def run(pct, bar, tail, kind, blk):
    ni, nk = PIV[pct]
    T = [0, 0, 0.0]; F = [0, 0, 0.0]; fb = 0
    for k0, side, rn in EV:
        b = k0 if bar == 'x' else (k0 + GATE + 1 if rn > GATE + 1 else None)
        if b is None or b >= N: continue
        if blk != 'all' and DAY(b) not in BLK[blk]: continue
        r = traj(R60, b, BLOCK, tail, LOOK_N, kind, side)
        d = r['dir']
        if d == 0:                                   # Joe's #7 fallback, in the caller
            g = float(M60[b]) - float(R60[b])
            if g == 0: continue
            ret = (1 if g > 0 else -1) == -side
            fb += 1
        else:
            ret = (d == -side)
        if int(ni[b]) < 0: continue
        rev = int(nk[b]) == -side
        p0 = float(PXa[b]); p1 = float(PXa[int(ni[b])])
        mv = (p1 - p0) / p0 * 100.0 * (-side)
        t = T if ret else F
        t[0] += 1; t[1] += rev; t[2] += mv
    return T, F, fb

HDR = ('TRAJ_TAIL_TF_SAMP', 'block', 'events', 'TRUE — pxs reverses', 'of those, it DID reverse',
       'FALSE — delegate', 'of those, it reversed anyway', 'spread, pts',
       'TRUE mean pxs move against the oob side', 'FALSE mean pxs move against', '#7 fallbacks')
for kind in ('close', 'extreme'):
    for bar, blab in (('h', 'at the 6-min DWELL-ENDING'), ('x', 'at the ws12r oob CROSSING')):
        for pct in (1.0,):
            print('\n# sample kind %s, %s, swing_detect %.1f%%' % (kind, blab, pct))
            rows = []
            for tail in (1, 2, 3, 6, 12):
                for blk in ('all', 'fit', 'hold'):
                    T, F, fb = run(pct, bar, tail, kind, blk)
                    rows.append(('%d / %.0f min' % (tail, tail * BLOCK * 5 / 60.0), blk,
                                 str(T[0] + F[0]),
                                 str(T[0]), '%.1f%%' % (100.0 * T[1] / T[0]) if T[0] else '—',
                                 str(F[0]), '%.1f%%' % (100.0 * F[1] / F[0]) if F[0] else '—',
                                 '**%+.1f**' % ((100.0 * T[1] / T[0]) - (100.0 * F[1] / F[0]))
                                 if T[0] and F[0] else '—',
                                 '%+.4f' % (T[2] / T[0]) if T[0] else '—',
                                 '%+.4f' % (F[2] / F[0]) if F[0] else '—', str(fb)))
            box(HDR, rows)
print('\n# THE SAME AT swing_detect 0.9%, dwell-ending only, sample kind close')
rows = []
for tail in (1, 2, 3, 6, 12):
    for blk in ('all', 'fit', 'hold'):
        T, F, fb = run(0.9, 'h', tail, 'close', blk)
        rows.append(('%d / %.0f min' % (tail, tail * BLOCK * 5 / 60.0), blk, str(T[0] + F[0]),
                     str(T[0]), '%.1f%%' % (100.0 * T[1] / T[0]) if T[0] else '—',
                     str(F[0]), '%.1f%%' % (100.0 * F[1] / F[0]) if F[0] else '—',
                     '**%+.1f**' % ((100.0 * T[1] / T[0]) - (100.0 * F[1] / F[0]))
                     if T[0] and F[0] else '—',
                     '%+.4f' % (T[2] / T[0]) if T[0] else '—',
                     '%+.4f' % (F[2] / F[0]) if F[0] else '—', str(fb)))
box(HDR, rows)
print('\n- the FALSE column is the base rate. If traj works, TRUE sits well above FALSE.')
print('- for reference on the same events: the void step_dir gate separated +36.4 pts, and Joe\'s')
print('  #7 Mage rule alone separated +2.3 pts at the dwell-ending.')
