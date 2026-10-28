"""HIS test#1 ROUTE: the lineage2 walk triggered at every barrage fire. Joe 1027.

    "if we trigger the lineage2 walk at barrage-fire (08-31 1432) and scan the wsf range for the
     highest exfence line, then the high exfence ws9 takes the baton. exhaust fires at 1501. this
     lineage2 walk is the same as usual: decisions at cadences only"

THE WALK IS THE ONE IN v4_lineage2, with `arm_at` set to the barrage bar so the arm race is
skipped - the barrage bar IS the arm. Nothing else about the walk changes.

THE TARGET SIDE IS THE BARRAGE'S OWN SIDE. His 08-31 1432 example is a HIGH barrage and he says
"the high exfence ws9 takes the baton", so the ex-fence scan is on the HIGH side. That is MY
reading of the side and it is the one gap this run assumes.

NOTHING IS GATED. Every one of the 28 fires is walked, and each row says which "recently" windows
would have blocked it, so the route can be read against any value he rules.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_sweep_pivots as SP, v4_fast as F
import v4_closed_prev as CP, v4_l2_proxy as PX, v4_l2_cadence as CAD, v4_lineage2 as L2
from v4_backstop_trades import prices
sys.stderr = _e

A, B = ln.K('2026-08-30 00:00:00'), ln.K('2026-09-06 23:59:55')
E = RS.load((RS.K0, RS.R0, RS.S0))
C = CP.ladder(E)
BD = PX.Board(C, E, MG={t: CP.line('ws%dMage' % t, t * 60) for t in range(1, 13)},
              MGE={t: ln.line('ws%dMage' % t) for t in range(1, 13)})
CL = CP.arm_lines(E)
close, PHI, PLO = prices()
CD = {sd: CAD.barrage_candidates(BD, sd) for sd in (-1, +1)}

EV = []
for sd in (-1, +1):
    for bar, _t, why in CAD.barrage(BD, sd, A, B, tol_s=70, lines=6, min_tf=0, fence='any',
                                    fit='off', win_s=0, cand=CD[sd]):
        EV.append((int(bar), int(sd)))
EV.sort()

DTF = [t for t in sorted(BD.tfs) if t >= 13]
WINS = (60, 300, 600, 1800, 3600)
revs = {sd: {t: sorted(int(b) for b in F.revs(BD.E[t], t, sd)) for t in DTF} for sd in (-1, +1)}

print('# HIS test#1 ROUTE - the lineage2 walk from every barrage fire, %s .. %s' % (ln.U(A), ln.U(B)))
print('# the walk is v4_lineage2.walk with arm_at = the barrage bar. the arm race is skipped;')
print('#   the barrage bar IS the arm, the rider is the highest ex-fence wsf line there, and')
print('#   every decision after that is at a cadence - his "the same as usual".')
print('# THE TARGET SIDE IS THE BARRAGE SIDE. that is my reading of his 08-31 1432 example.')
print('# NOTHING IS GATED: all %d fires are walked. the block columns are for reading against' % len(EV))
print('#   whatever "recently" he rules - 60/300/600/1800/3600 s.')
print('# MAE/MFE are the cadence bar to sw[close], favourable -side. RULED_OK %s' % K.RULED_OK)
print('')
print('| the barrage fire | side | the rider at fire | the walk verdict | the exhaust bar |'
      ' minutes held | MAE % | MFE % | SP TF | leg MFE % | test#1 blocks at |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
MA, MF, LEG, held = [], [], [], []
nver = {}
for bar, sd in EV:
    rider = L2.rider_at(BD, sd, bar)
    v, eb, _rows = L2.walk(CL, BD, close, sd, bar, B, arm_at=bar)
    nver[v] = nver.get(v, 0) + 1
    blk = ','.join(str(w) for w in WINS
                   if any(any(bar - w // 5 <= b <= bar for b in revs[sd][t]) for t in DTF)) or '-'
    if eb is None:
        print('| %s | %s | %s | %s | - | - | - | - | - | - | %s |'
              % (ln.U(bar), 'HIGH' if sd > 0 else 'LOW',
                 'none' if rider is None else 'cws%d' % rider, v, blk))
        continue
    z = int(eb)
    a2, b2 = min(bar, z), max(bar, z)
    seg = np.asarray(close[a2:b2 + 1], float)
    pb, fav = float(close[bar]), -int(sd)
    up = (float(np.nanmax(seg)) - pb) / pb * 100.0
    dn = (float(np.nanmin(seg)) - pb) / pb * 100.0
    mfe, mae = (up, dn) if fav > 0 else (-dn, -up)
    sw = SP.swing(int(z), int(sd), close)
    lg = ('%.3f' % sw['mfe_pct']) if sw and sw.get('close') is not None else '-'
    tf = sw['tf'] if sw and sw.get('close') is not None else '-'
    mins = (z - bar) * 5 / 60.0
    MA.append(mae); MF.append(mfe); held.append(mins)
    if lg != '-':
        LEG.append(float(lg))
    print('| %s | %s | %s | %s | %s | %.1f | %+.3f | %+.3f | %s | %s | %s |'
          % (ln.U(bar), 'HIGH' if sd > 0 else 'LOW',
             'none' if rider is None else 'cws%d' % rider, v, ln.U(z), mins, mae, mfe, tf, lg, blk))

_med = lambda v: sorted(v)[len(v) // 2] if v else float('nan')
print('')
print('| the MAE/MFE read, the barrage fire to the walk exhaust | value |')
print('|---|---|')
print('| events scored | %d of %d |' % (len(MA), len(EV)))
print('| sum MAE %% | %+.3f |' % sum(MA))
print('| sum MFE %% | %+.3f |' % sum(MF))
print('| median MAE %% | %+.3f |' % _med(MA))
print('| median MFE %% | %+.3f |' % _med(MF))
print('| worst MAE %% | %+.3f |' % min(MA))
print('| best MFE %% | %+.3f |' % max(MF))
print('| MFE > abs(MAE) | %d of %d |' % (sum(1 for a, f in zip(MA, MF) if f > abs(a)), len(MA)))
print('| MAE worse than %.1f%% | %d of %d |'
      % (K.LIN2_MAE_CAP, sum(1 for a in MA if a < -float(K.LIN2_MAE_CAP)), len(MA)))
print('| median minutes held | %.1f |' % _med(held))
print('| the span | the barrage fire bar to the walk\'s own exhaust bar - no horizon applied |')
print('')
print('| the verdict | walks |')
print('|---|---|')
for v in sorted(nver):
    print('| %s | %d |' % (v, nver[v]))
