"""THE 09-03 to 09-04 LEGS: the exit's own cadence type, and every other type firing on that bar.

Joe 1030: *"in a table share the timestamps, trade direction, cadence type, any other exit types
that fired, for the 09-03 to 09-04"*, after picking the pair as the balanced one - 18 cascade
reversals won, 17 lost.

THE "OTHER TYPES" COLUMN is every cadence the walk's own list produced on the SAME bar as the exit,
with the exit's own type left out. The list is t1, t2, the barrage, and the retest gate's cadence;
the ws1b counter-oob cadence is OFF on this arm so it contributes nothing.
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
import v4_l2_cadence as CAD
import v4_chain as CH
import v4_signal as SG
import v4_sig_lin2_reentry as L2R
import ln
from v4_backstop_trades import prices
sys.stderr = _e

T0 = time.time()
K.LIN2_PSEUDO_MIN_TF = 99
K.LIN2_LATCH_EXFNC_ON = 1
K.LIN2_B1_HOLD = 0
A = ln.K(os.environ.get('W_WIN_START', '2026-09-03 00:00:00'))
B = ln.K(os.environ.get('W_WIN_END', '2026-09-04 23:59:55'))
close, phi, plo = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = LL.arm_lines(E)
MG = LL.mage()
B1 = np.asarray(CL['b'], float)
BD = PX.Board(E, E, MG=MG, MGE=MG, PS=None)
SIG = [g for g in L2R.signals(B1, MG) if g['bar'] == ln.K('2026-08-29 23:53:50')]
assert len(SIG) == 1
OPEN = (SG.fire_bar(SIG[0]), SG.target_side(SG.direction(int(SIG[0]['side']))))
#   THE 1.1% STOP, env-driven. His 1030: *"recreate the table using the mae1.1 cap"*.
#   IT NEEDS THE SIGNAL LIST: v4_chain.legs goes FLAT at a stop - his own lin2-reentry line is
#   *"there is no trade open (either because of a STOP, or because the machine is cold-starting)"* -
#   and the way back in is the next lin2-reentry signal. Without it a stop ENDS the chain.
CAP = float(K.LIN2_MAE_CAP) if os.environ.get('W_MAE_CAP') == 'on' else None
RESIG = L2R.signals(B1, MG) if CAP is not None else None
lg, zero, op = CH.legs(CL, BD, close, phi, plo, A, B, MG=MG, B1=B1, open_at=OPEN,
                       mae_cap=CAP, resig=RESIG)

#   every cadence the list produces on this window, per side, indexed by bar
AT = {}
for sd in (-1, +1):
    for b, ty, w in (CAD.t1(CL, sd, A, B) + CAD.t2(CL, sd, A, B)
                     + (CAD.counter_oob(CL, sd, A, B) if int(K.LIN2_COUNTER_OOB_ON) else [])
                     + (CAD.barrage(BD, sd, A, B) if int(K.LIN2_BARRAGE_ON) else [])):
        AT.setdefault((int(sd), int(b)), set()).add(str(ty))


def owner(x):
    if x['exit'] is None:
        return 'no exit'
    if x.get('stopped'):
        return 'the 1.1%% stop'
    ex = [r for r in x['rows'] if r['stage'] == 'EXHAUST']
    if not ex:
        return str(x['verdict'])
    w = str(ex[-1].get('why') or '')
    if 'OPPOSES' in w:
        return 'mage-cascade OPPOSES'
    if 'LIN2_MATRY_WSF_TAKEOVER' in w:
        return 'LIN2_MATRY_WSF_TAKEOVER'
    if 'no ws1..ws%d r is ex-fence' % K.L2_MOM_MAXTF in w:
        return 'no rider at the gate cadence'
    if 'no-longer-exfence' in w or 'nowhere to pass' in w or 'no candidate' in w:
        return 'the board review'
    return str(x['verdict'])


print('# 2026-09-03 to 2026-09-04 | TAPE %d bars | RULED_OK %s' % (len(close), K.RULED_OK))
print('# RMOM_FNC %.1f -> (%.1f, %.1f) | L2_MOM_MAXTF %d | LIN2_EXFNC_LATCH_REL %r'
      % (K.RMOM_FNC, 100.0 - K.RMOM_FNC, K.RMOM_FNC, K.L2_MOM_MAXTF, K.LIN2_EXFNC_LATCH_REL))
print('# the counter-oob cadence is %s | the takeover is %s | the cascade gate is %s | the stop is'
      ' %s' % ('ON' if int(K.LIN2_COUNTER_OOB_ON) else 'OFF',
               'ON' if int(K.LIN2_MATRY_WSF_TAKEOVER_ON) else 'OFF',
               'ON' if int(K.LIN2_CASC_REV_GATE_ON) else 'OFF',
               'OFF' if CAP is None else ('ON at LIN2_MAE_CAP %.2f%%, with %d lin2-reentry signals'
                                          ' as the way back in' % (CAP, len(RESIG or ())))))
print('# drag %.4f%% a round trip, its own column and its own total.' % CH.DRAG_PCT)
print('')
print('| the open | dir | the exit | the exit\'s cadence type | who owned the exit | other cadence'
      ' types on that bar | held min | MAE % | MFE % | realised % | drag % | net % |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
nm = nf = nr = nh = 0.0
sc = 0
for x in lg:
    d = 'LONG' if x['side'] > 0 else 'SHORT'
    if x['exit'] is None:
        print('| %s | %s | - | %s | %s | - | - | - | - | - | - | - |'
              % (ln.U(x['opn']), d, x['ctype'], owner(x)))
        continue
    oth = sorted(AT.get((int(x['side']), int(x['exit'])), set()) - {str(x['ctype'])})
    sc += 1
    nm += x['mae']; nf += x['mfe']; nr += x['rel']; nh += x['held_min']
    print('| %s | %s | %s | %s | %s | %s | %.1f | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
          % (ln.U(x['opn']), d, ln.U(x['exit']), x['ctype'], owner(x),
             ', '.join(oth) or 'none', x['held_min'], x['mae'], x['mfe'], x['rel'],
             CH.DRAG_PCT, x['rel'] - CH.DRAG_PCT))
print('| TOTAL %d scored legs | | | | | | %.1f | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
      % (sc, nh, nm, nf, nr, CH.DRAG_PCT * sc, nr - CH.DRAG_PCT * sc))
print('')
print('| the read | value |')
print('|---|---|')
print('| legs | %d |' % len(lg))
print('| legs scored | %d |' % sc)
print('| legs with another cadence type on the exit bar | %d |'
      % sum(1 for x in lg if x['exit'] is not None
            and (AT.get((int(x['side']), int(x['exit'])), set()) - {str(x['ctype'])})))
print('| seconds to compute | %.1f |' % (time.time() - T0))
