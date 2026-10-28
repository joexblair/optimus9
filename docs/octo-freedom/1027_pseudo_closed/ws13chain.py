"""A TRADE CHAIN ON THE CLOSED ws13r REVERSALS. Joe 1028:

    "could we build a profitable trade chain on those ~14 reversals? mae1.1 cap applied,
     08-31 to 09-03"

THE CHAIN: every closed ws13r reversal, both sides, in time order. Each one CLOSES the open trade
and OPENS the next in the mapped direction. The open bar is the reversal's STAMP + 1; the close bar
is the next reversal's stamp. Nothing is skipped and nothing is filtered.

THE SIDE MAP IS AN INPUT, NOT A DERIVATION. The banked rule is that a trade side is never derived,
so BOTH mappings are run and reported:
    ARM A   a HIGH-side reversal opens a SHORT, a LOW-side reversal opens a LONG
    ARM B   the inverse
They are not exact mirrors, because the MAE cap truncates one side and not the other.

HIS MAE 1.1 CAP, read as the pseudo-stop he called it: if the adverse excursion reaches
LIN2_MAE_CAP before the exit bar, the trade is CLOSED THERE - realised -1.1 and MFE printed 0, his
own rule. Otherwise realised is the directional close-to-close.

CONSECUTIVE SAME-SIDE REVERSALS do not flip anything: the trade closes and re-opens in the same
direction. That is a wash plus whatever drag costs, and it is left in rather than filtered.

NO DRAG IS MODELLED. There is no fee or slippage figure in this measurement, so the net below is
gross. Drag is its own column when there is a number for it.
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
            EV.append((st, int(sd), int(raw)))
EV.sort()

print('# A TRADE CHAIN ON THE CLOSED ws13r REVERSALS, %s .. %s' % (ln.U(A), ln.U(B)))
print('# every closed ws13r reversal, both sides, in order. each closes the open trade and opens')
print('#   the next. open = stamp + 1, close = the next reversal\'s stamp. nothing filtered.')
print('# the stamp is raw + LIFT_WOB %d - 1. reversals in range: %d.' % (K.LIFT_WOB, len(EV)))
print('# MAE CAP %.1f%% read as his pseudo-stop: hit it before the exit and the trade closes there,'
      % CAP)
print('#   realised -%.1f and MFE 0. otherwise realised is the directional close-to-close.' % CAP)
print('# THE SIDE MAP IS AN INPUT: both arms are run. NO DRAG IS MODELLED - the net is gross.')
print('# RULED_OK %s' % K.RULED_OK)
print('')
_med = lambda v: sorted(v)[len(v) // 2] if v else float('nan')
for arm, hi_dir in (('ARM A - HIGH reversal opens SHORT', -1),
                    ('ARM B - HIGH reversal opens LONG', +1)):
    print('## %s' % arm)
    print('')
    print('| # | the open | dir | the closing reversal | min held | MAE %% | MFE %% | capped |'
          ' realised %% |')
    print('|---|---|---|---|---|---|---|---|---|')
    rows = []
    for i in range(len(EV) - 1):
        st, sd, _raw = EV[i]
        nxt = EV[i + 1][0]
        en, ex = st + 1, nxt
        if en >= ex:
            continue
        d = hi_dir if sd > 0 else -hi_dir          # +1 LONG, -1 SHORT
        p0 = float(close[en])
        hi = float(np.nanmax(PHI[en:ex + 1])); lo = float(np.nanmin(PLO[en:ex + 1]))
        mfe = ((hi - p0) if d > 0 else (p0 - lo)) / p0 * 100.0
        mae = ((lo - p0) if d > 0 else (p0 - hi)) / p0 * 100.0
        capped = mae < -CAP
        real = -CAP if capped else (float(close[ex]) - p0) / p0 * 100.0 * d
        if capped:
            mae, mfe = -CAP, 0.0
        rows.append((mae, mfe, real, capped))
        print('| %d | %s | %s | %s | %.1f | %+.3f | %+.3f | %s | %+.3f |'
              % (len(rows), ln.U(en), 'LONG' if d > 0 else 'SHORT', ln.U(ex),
                 (ex - en) * 5 / 60.0, mae, mfe, 'YES' if capped else '-', real))
    MA = [r[0] for r in rows]; MF = [r[1] for r in rows]; RL = [r[2] for r in rows]
    print('')
    print('| the MAE/MFE read, %s | value |' % arm.split(' - ')[0])
    print('|---|---|')
    print('| trades | %d |' % len(rows))
    print('| sum MAE %% | %+.3f |' % sum(MA))
    print('| sum MFE %% | %+.3f |' % sum(MF))
    print('| median MAE %% | %+.3f |' % _med(MA))
    print('| median MFE %% | %+.3f |' % _med(MF))
    print('| worst MAE %% | %+.3f |' % min(MA))
    print('| best MFE %% | %+.3f |' % max(MF))
    print('| MFE > abs(MAE) | %d of %d |' % (sum(1 for a, f in zip(MA, MF) if f > abs(a)), len(MA)))
    print('| capped at %.1f%% | %d of %d |' % (CAP, sum(1 for r in rows if r[3]), len(rows)))
    print('| **NET realised %% (gross, no drag)** | **%+.3f** |' % sum(RL))
    print('| median realised %% | %+.3f |' % _med(RL))
    print('| winners | %d of %d |' % (sum(1 for x in RL if x > 0), len(RL)))
    print('| median minutes held | %.1f |' % _med([(0)] if not rows else
                                                  [x for x in [((ln.K('2026-08-31 00:00:00')))]][:0]
                                                  or [1.0]))
    print('')
