"""HOW MANY HONOURED REVERSALS A HOLD WOULD GATE, at 2, 3 and 4 minutes.

Joe 1030: *"how many other 'failures' would be prevented with a 2,3, 4 minute walk forward, to
detect a baton candidate in ws2,3,4"*, after naming the two gaps in his own mech himself.

IT IS A HOLD, NOT A FORWARD PEEK. The reversal is not acted on at the cadence bar: it is held for
N minutes, the gate watches ws2r..ws4r across that hold, and the reversal fires at cadence + N only
if no candidate appeared inside it. Every bar read lies inside the hold, so the decision is made at
the bar it is dated to - the same shape as LIN2_CROSS_WOB 12 on a cross.

WHAT THE HOLD COSTS IS NOT MEASURED HERE. A reversal that still fires, fires N minutes later at a
different price. This counts DETECTIONS only. The net cost needs the hold wired into the walk.

ws2..ws4 IS HIS RANGE, from *"a baton candidate in ws2,3,4"*. ws1..ws4 is printed beside it because
that is the range the built gate uses.
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
import v4_lineage2 as L2
import v4_signal as SG
import v4_sig_lin2_reentry as L2R
import ln
from v4_backstop_trades import prices
sys.stderr = _e

T0 = time.time()
K.LIN2_PSEUDO_MIN_TF = 99
K.LIN2_LATCH_EXFNC_ON = 1
K.LIN2_B1_HOLD = 0
HOLDS = (2, 3, 4)                      # his minutes
A = ln.K(os.environ.get('W_WIN_START', '2026-08-30 00:00:00'))
B = ln.K(os.environ.get('W_WIN_END', '2026-09-06 23:59:55'))
close, phi, plo = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = LL.arm_lines(E)
MG = LL.mage()
B1 = np.asarray(CL['b'], float)
BD = PX.Board(E, E, MG=MG, MGE=MG, PS=None)
SIG = [g for g in L2R.signals(B1, MG) if g['bar'] == ln.K('2026-08-29 23:53:50')]
assert len(SIG) == 1
OPEN = (SG.fire_bar(SIG[0]), SG.target_side(SG.direction(int(SIG[0]['side']))))
lg, zero, op = CH.legs(CL, BD, close, phi, plo, A, B, MG=MG, B1=B1, open_at=OPEN)


def first_cand(side, bar, mins, lo):
    """The first bar inside the hold with a candidate in ws{lo+1}..ws4. -> bar or None.

    The hold is bar+1 .. bar + mins*12, since 12 bars is a minute at the 5 s grid. Nothing past
    the hold's last bar is read.
    """
    end = int(bar) + int(mins) * 12
    for k in range(int(bar), min(end, len(close) - 1) + 1):
        if L2.candidates(BD, int(side), k, int(lo), cap=4):
            return k
    return None


rows = []
for i, x in enumerate(lg):
    if x['exit'] is None:
        continue
    ex = [r for r in x['rows'] if r['stage'] == 'EXHAUST']
    if not ex or 'OPPOSES' not in str(ex[-1].get('why') or ''):
        continue
    bar, side = int(x['exit']), int(x['side'])
    if L2.candidates(BD, side, bar, 0, cap=4):
        continue                                   # already gated at the bar itself
    nxt = lg[i + 1] if i + 1 < len(lg) else None
    nnet = None if (nxt is None or nxt['exit'] is None) else nxt['rel'] - CH.DRAG_PCT
    r = dict(bar=bar, side=side, nnet=nnet)
    for m in HOLDS:
        r['h2_%d' % m] = first_cand(side, bar, m, 1)   # ws2..ws4, HIS range
        r['h1_%d' % m] = first_cand(side, bar, m, 0)   # ws1..ws4, the built gate's range
    rows.append(r)

print('# THE HOLD ON AN HONOURED REVERSAL | WINDOW %s .. %s | TAPE %d bars | RULED_OK %s'
      % (ln.U(A), ln.U(B), len(close), K.RULED_OK))
print('# the stop is OFF. drag %.4f%% a round trip. RMOM_FNC %.1f, L2_MOM_MAXTF %d.'
      % (CH.DRAG_PCT, K.RMOM_FNC, K.L2_MOM_MAXTF))
print('# a hold of N minutes reads bar .. bar + N*12 and nothing past it.')
print('')
print('## every honoured reversal, and the first bar a ws2..ws4 candidate appears inside each hold')
print('')
print('| the reversal bar | dir | the next leg\'s net % | 2 min | 3 min | 4 min |')
print('|---|---|---|---|---|---|')
for r in sorted(rows, key=lambda z: z['bar']):
    print('| %s | %s | %s | %s | %s | %s |'
          % (ln.U(r['bar']), 'LONG' if r['side'] > 0 else 'SHORT',
             '-' if r['nnet'] is None else '%+.4f' % r['nnet'],
             '-' if r['h2_2'] is None else ln.U(r['h2_2'])[11:],
             '-' if r['h2_3'] is None else ln.U(r['h2_3'])[11:],
             '-' if r['h2_4'] is None else ln.U(r['h2_4'])[11:]))
jg = [r for r in rows if r['nnet'] is not None]
bad = [r for r in jg if r['nnet'] < 0]
good = [r for r in jg if r['nnet'] >= 0]
print('')
print('## what each hold length detects')
print('')
print('| the hold | the range | losing reversals it gates | of %d | winning reversals it also gates'
      ' | of %d | net %% of the losers it gates | net %% of the winners it gates |'
      % (len(bad), len(good)))
print('|---|---|---|---|---|---|---|---|')
for lo, nm in ((1, 'ws2..ws4 - HIS'), (0, 'ws1..ws4 - the built gate')):
    for m in HOLDS:
        kb = [r for r in bad if r['h%d_%d' % (2 if lo else 1, m)] is not None]
        kg = [r for r in good if r['h%d_%d' % (2 if lo else 1, m)] is not None]
        print('| %d min | %s | %d | %d | %d | %d | %+.4f | %+.4f |'
              % (m, nm, len(kb), len(bad), len(kg), len(good),
                 sum(r['nnet'] for r in kb), sum(r['nnet'] for r in kg)))
print('')
print('| the read | value |')
print('|---|---|')
print('| honoured reversals in the window | %d |' % len(rows))
print('| of those with a next leg to judge | %d |' % len(jg))
print('| the losers among them | %d |' % len(bad))
print('| summed net %% of the losers | %+.4f |' % sum(r['nnet'] for r in bad))
print('| summed net %% of the winners | %+.4f |' % sum(r['nnet'] for r in good))
print('| his 11:09:40 case, 2 min | %s |'
      % next((('a candidate at %s' % ln.U(r['h2_2'])) if r['h2_2'] else 'no candidate inside 2 min')
             for r in rows if ln.U(r['bar']) == '2026-09-04 11:09:40') if any(
          ln.U(r['bar']) == '2026-09-04 11:09:40' for r in rows) else 'not in this window\'s set')
print('| seconds to compute | %.1f |' % (time.time() - T0))
