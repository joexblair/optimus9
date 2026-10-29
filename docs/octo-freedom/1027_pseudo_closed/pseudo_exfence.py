"""WHAT THE PSEUDO EX-FENCE READ CHANGES. Joe 1028:

    "we've already had cases yesterday when a line that I thought should be ex-fence and the walk
     saw the emerging spikes which early-exhausted the walk. let's confine pseudo-closed to >3"
    "1, pseudo for exfence"

LIN2_PSEUDO_MIN_TF 4: ws1..ws3 keep their current reads, ws4 upward read pseudo-closed for the
EX-FENCE state and for the value printed beside it.

THIS RUN REPORTS, on 2026-08-30:
    1  every bar where the closed and pseudo ex-fence states DISAGREE, per line per side - the
       population his complaint lives in
    2  the rider pick at every ARM and every t1/t2 cadence bar, under each ladder, side by side

NOTHING IS WIRED INTO A WALK HERE. The proxy routes the reads; this measures what that routing
moves before any chain runs on it.

PSEUDO IS NOT CACHEABLE TAPE-WIDE - 121 TF-bar samples per 5 s bar. It is computed for this day
plus 120 x T bars of history, per line.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1027_pseudo_closed')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
import v4_l2_proxy as PX, v4_l2_cadence as CAD, v4_lineage2 as L2
import pseudo_closed as PC
from v4_backstop_trades import prices
sys.stderr = _e

DAY = '2026-08-30'
A, B = ln.K('%s 00:00:00' % DAY), ln.K('%s 23:59:55' % DAY)
MINTF = int(K.LIN2_PSEUDO_MIN_TF)
TOP = int(K.L2_MOM_MAXTF)
close, _h, _l = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
C = CP.ladder(E)
CL = CP.arm_lines(E)

#   the pseudo ladder for ws{MINTF}..ws{TOP}, over the day plus the history each line needs
IDX = np.arange(A, B + 1)
PS = {}
for t in range(MINTF, TOP + 1):
    PS[t] = np.full(len(close), np.nan)
    PS[t][IDX] = PC.series(close, t, IDX)

BD_cl = PX.Board(C, E)                                   # no pseudo - the closed board
BD_ps = PX.Board(C, E, PS=PS)                            # pseudo above the band

print('# WHAT THE PSEUDO EX-FENCE READ CHANGES, %s' % DAY)
print('# LIN2_PSEUDO_MIN_TF %d: ws1..ws%d keep their reads, ws%d.. read pseudo for EX-FENCE.'
      % (MINTF, MINTF - 1, MINTF))
print('# the value printed beside a pseudo decision is the pseudo value - my call, in the knob.')
print('# ex-fence is K.ex_fence, the %.0f/%.0f fence from RMOM_FNC. RULED_OK %s'
      % (100 - K.RMOM_FNC, K.RMOM_FNC, K.RULED_OK))
print('')
print('## 1. where the two ladders DISAGREE on ex-fence, %s' % DAY)
print('')
print('| the line | side | bars ex-fence CLOSED | bars ex-fence PSEUDO | bars they disagree |'
      ' disagree %% | pseudo says YES, closed NO | closed YES, pseudo NO |')
print('|---|---|---|---|---|---|---|---|')
for t in range(MINTF, TOP + 1):
    cl = np.asarray(C[t], float)[IDX]
    ps = PS[t][IDX]
    for sd in (-1, +1):
        fc = np.array([bool(K.ex_fence(v, sd)) for v in cl])
        fp = np.array([bool(K.ex_fence(v, sd)) for v in ps])
        dis = fc != fp
        print('| ws%dr | %s | %d | %d | %d | %.1f%% | %d | %d |'
              % (t, 'LOW' if sd < 0 else 'HIGH', int(fc.sum()), int(fp.sum()), int(dis.sum()),
                 100.0 * dis.mean(), int((fp & ~fc).sum()), int((fc & ~fp).sum())))

#   the decision bars: every arm the chain found, plus every t1/t2 cadence
CB = sorted({int(x) for sd in (-1, +1)
             for x, _t, _w in (CAD.t1(CL, sd, A, B) + CAD.t2(CL, sd, A, B))})
ARMS = []
for sd in (-1, +1):
    a, which, _w = L2.arm_race(CL, BD_cl, sd, A, B)
    if a is not None:
        ARMS.append((int(a), sd, which))
BARS = sorted({b for b in CB} | {a for a, _s, _w in ARMS})

print('')
print('## 2. the rider pick at every decision bar, both ladders')
print('')
print('| the bar | side | rider on CLOSED | its value | rider on PSEUDO | its value | changed? |')
print('|---|---|---|---|---|---|---|')
n_chg = 0
for b in BARS:
    for sd in (-1, +1):
        rc = L2.rider_at(BD_cl, sd, b)
        rp = L2.rider_at(BD_ps, sd, b)
        if rc is None and rp is None:
            continue
        chg = rc != rp
        if chg:
            n_chg += 1
        print('| %s | %s | %s | %s | %s | %s | %s |'
              % (ln.U(b), 'LOW' if sd < 0 else 'HIGH',
                 'cws%d' % rc if rc else 'none',
                 '%.2f' % BD_cl.value(rc, b) if rc else '-',
                 'ws%d' % rp if rp else 'none',
                 '%.2f' % BD_ps.value(rp, b) if rp else '-',
                 'YES' if chg else 'no'))
print('')
print('| the read | value |')
print('|---|---|')
print('| decision bars examined | %d |' % len(BARS))
print('| rider picks that change | %d |' % n_chg)
