"""THE 2026-08-30 CHAIN AT ONE (RMOM_FNC, L2_MOM_MAXTF) PAIR. One arm per run, env-driven.

WHY IT EXISTS. Joe 1030: *"stats don't tell us how the chain will behave - can you create a 75/25
momfnc with max 20 TF chain?"*. `fence_pop.md` counted the fence's population; this walks the chain
on it.

ONE ARM PER PROCESS, ON PURPOSE. Both knobs sit in v4_knobs.RULED, and the refusal gate runs at
IMPORT. Mutating them after import would walk an off-ruled chain while RULED_OK still printed True
- his *"an off-ruled run is not the machine"*. So the arm is selected by environment before the
import, the gate sees it, and an off-bank arm prints its own deltas and needs W_V4_EXPERIMENT=1.

    the bank      python3 chain_mom.py
    his 1030      W_V4_RMOM_FNC=75 W_V4_L2_MOM_MAXTF=20 W_V4_EXPERIMENT=1 python3 chain_mom.py

ONLY THE TWO KNOBS HE NAMED MOVE. MC_TF_HI stays 12, and the absolute line counts - MC_MIN 4,
LIN2_CHAIN_OPEN_LINES 2, LIN2_BARRAGE_LINES 6 - stay where they were measured. Those are open
questions on his desk, not things this run decides.

THE OPEN IS NOT PINNED. Each arm runs its own LIN2_CHAIN_OPEN_ON mech, so a knob that moves the
open shows up as a moved open rather than being hidden by a handed-in bar.
"""
import io
import os
import sys
import time

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import v4_knobs as K
import v4_rcfg_sweep as RS
import v4_live_lines as LL
import v4_l2_proxy as PX
import v4_chain as CH
import ln
sys.stderr = _e

T0 = time.time()
K.LIN2_PSEUDO_MIN_TF = 99          # pseudo-closed is not in this arm - his 1029 bank
K.LIN2_LATCH_EXFNC_ON = 1          # the per-line ex-fence latch is ON - his 1029 bank
K.LIN2_B1_HOLD = 0                 # *"let's use wob 0 until we sweep"*

A, B = ln.K('2026-08-30 00:00:00'), ln.K('2026-08-30 23:59:55')
from v4_backstop_trades import prices
close, phi, plo = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = LL.arm_lines(E)
MG = LL.mage()                     # ws1..ws{L2_MOM_MAXTF} - the knob owns the top rung
B1 = np.asarray(CL['b'], float)
BD = PX.Board(E, E, MG=MG, MGE=MG, PS=None)
assert max(MG) == int(K.L2_MOM_MAXTF), 'the Mage ladder top does not match the knob'

lg, zero, op = CH.legs(CL, BD, close, phi, plo, A, B, MG=MG, B1=B1)

lo, hi = 100.0 - K.RMOM_FNC, K.RMOM_FNC
print('# THE 2026-08-30 CHAIN AT RMOM_FNC %.1f -> (%.1f, %.1f), L2_MOM_MAXTF %d'
      % (K.RMOM_FNC, lo, hi, K.L2_MOM_MAXTF))
print('# WINDOW %s .. %s | TAPE %d bars | RULED_OK %s' % (ln.U(A), ln.U(B), len(close), K.RULED_OK))
print('# the Mage ladder handed to the board is ws1..ws%d. The r ladder on the board is ws%d..ws%d.'
      % (max(MG), min(BD.tfs), max(BD.tfs)))
print('# every line is the live read - prev-close is out. the ex-fence latch hold is %d bars = %d s.'
      % (K.LIN2_EXFNC_LATCH_WOB, K.LIN2_EXFNC_LATCH_WOB * 5))
print('# MC_TF_HI stays 12. MC_MIN %d, LIN2_CHAIN_OPEN_LINES %d, LIN2_BARRAGE_LINES %d - all'
      ' unmoved.' % (4,
                     K.LIN2_CHAIN_OPEN_LINES, K.LIN2_BARRAGE_LINES))
print('# the 1.1%% stop is OFF. drag %.4f%% per round trip, its own column and its own total.'
      % CH.DRAG_PCT)
print('')
print('## the chain open this arm found for itself')
print('')
print('| the read | value |')
print('|---|---|')
print('| the open bar | %s |' % ln.U(op['bar']))
print('| the direction | %s |' % ('LONG' if op['side'] > 0 else 'SHORT'))
print('| the candidate side | %s |' % ({-1: 'LOW', 0: '-', 1: 'HIGH'}[int(op['cand_side'])]))
print('| the anchor bar | %s |' % ('-' if op['anchor'] is None else ln.U(op['anchor'])))
print('| the lines away at the anchor | %s |'
      % (', '.join('ws%d' % t for t in op['lines']) if op['lines'] else '-'))
print('| how it was found | %s |' % op['src'])

print('')
print('## every leg, one row per leg')
print('')
print('| leg | the open | dir | the exit | ended by | held min | the rider chain | MAE % | MFE % |'
      ' realised % | drag % | net % |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
nmae = nmfe = nrel = nheld = 0.0
scored = 0
for n, x in enumerate(lg, 1):
    ch = []
    for r in x['rows']:
        rd = r.get('rider')
        if rd and (not ch or ch[-1] != rd):
            ch.append(rd)
    chs = ' > '.join('ws%d' % t for t in ch) if ch else '-'
    d = 'LONG' if x['side'] > 0 else 'SHORT'
    if x['exit'] is None:
        print('| %d | %s | %s | - | %s | - | %s | - | - | - | - | - |'
              % (n, ln.U(x['opn']), d, x['ctype'], chs))
        continue
    scored += 1
    nmae += x['mae']; nmfe += x['mfe']; nrel += x['rel']; nheld += x['held_min']
    print('| %d | %s | %s | %s | %s | %.1f | %s | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
          % (n, ln.U(x['opn']), d, ln.U(x['exit']), x['ctype'], x['held_min'], chs, x['mae'],
             x['mfe'], x['rel'], CH.DRAG_PCT, x['rel'] - CH.DRAG_PCT))
print('| TOTAL %d scored legs | | | | | %.1f | | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
      % (scored, nheld, nmae, nmfe, nrel, CH.DRAG_PCT * scored,
         nrel - CH.DRAG_PCT * scored))

print('')
print('## the aggregate')
print('')
print('| the read | value |')
print('|---|---|')
print('| RMOM_FNC | %.1f -> (%.1f, %.1f) |' % (K.RMOM_FNC, lo, hi))
print('| L2_MOM_MAXTF | %d |' % K.L2_MOM_MAXTF)
print('| the open | %s %s |' % (ln.U(op['bar']), 'LONG' if op['side'] > 0 else 'SHORT'))
print('| legs walked | %d |' % len(lg))
print('| legs scored | %d |' % scored)
print('| zero-length legs, recorded not scored | %d |' % len(zero))
print('| legs net-positive | %d |'
      % sum(1 for x in lg if x['exit'] is not None and x['rel'] - CH.DRAG_PCT > 0))
print('| summed held min | %.1f |' % nheld)
print('| summed MAE %% | %.4f |' % nmae)
print('| summed MFE %% | %+.4f |' % nmfe)
print('| summed realised %% | %+.4f |' % nrel)
print('| summed drag %% | %.4f |' % (CH.DRAG_PCT * scored))
print('| net %% | %+.4f |' % (nrel - CH.DRAG_PCT * scored))
print('| MFE collected %% | %.1f%% |' % (100.0 * nrel / nmfe if nmfe else 0.0))
print('| seconds to compute | %.1f |' % (time.time() - T0))
