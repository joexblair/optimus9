"""WHO OWNS EACH LEG'S EXIT, and what the leg that exit OPENED went on to do.

Joe 1030: *"how often does mage-cascade own the decision, and the resulting trade is negative net
becasue mage-cascade was wrong??"*

TWO WAYS THE CASCADE CAN BE WRONG, and they are different questions:
    the OPPOSES branch   it exhausts a leg and the router reverses. If the leg that reversal OPENED
                         ends negative, the reversal was into a loser.
    the MATCHES branch   it ends the cadence with no action and the walk keeps going, so the board
                         is never reviewed at that bar. If the leg it held open ends negative, it
                         held a loser open.

THE OWNER IS READ OFF THE EXIT ROW's own text, not inferred. v4_lineage2 writes the branch it took
into `why`, so 'OPPOSES' marks the cascade's exhaust and 'matches ... no action' marks its hold.

NOT EDITED: chain_lift_2d.py. The 358-arm sweep launches batches from that file over 12 h, so an
edit mid-run would change the arms that have not started yet. This is a separate reader.
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


def owner(x):
    """Which branch ended this leg. -> a label, read off the exit row's own text."""
    if x['exit'] is None:
        return 'no exit'
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


def held(x):
    """How many times the cascade's MATCHES branch ended a cadence inside this leg. -> int."""
    return sum(1 for r in x['rows']
               if r['stage'] == 'NO ACTION' and 'matches the' in str(r.get('why') or ''))


print('# WHO OWNS EACH LEG\'S EXIT | WINDOW %s .. %s | TAPE %d bars | RULED_OK %s'
      % (ln.U(A), ln.U(B), len(close), K.RULED_OK))
print('# RMOM_FNC %.1f | L2_MOM_MAXTF %d | LIN2_EXFNC_LATCH_REL %r | LIN2_COUNTER_OOB_ON %d'
      ' | takeover %d | stop %s'
      % (K.RMOM_FNC, K.L2_MOM_MAXTF, K.LIN2_EXFNC_LATCH_REL, K.LIN2_COUNTER_OOB_ON,
         K.LIN2_MATRY_WSF_TAKEOVER_ON, 'OFF'))
print('# drag %.4f%% a round trip, its own column and its own total.' % CH.DRAG_PCT)
print('')
print('## every leg, who ended it, and what the leg it opened did')
print('')
print('| the open | dir | the exit | ended by | who owned the exit | cascade MATCHES rows inside'
      ' it | net % | the NEXT leg opened by this exit | its net % |')
print('|---|---|---|---|---|---|---|---|---|')
rows = []
for i, x in enumerate(lg):
    nxt = lg[i + 1] if i + 1 < len(lg) else None
    net = None if x['exit'] is None else x['rel'] - CH.DRAG_PCT
    nnet = None if (nxt is None or nxt['exit'] is None) else nxt['rel'] - CH.DRAG_PCT
    ow = owner(x)
    rows.append(dict(opn=x['opn'], side=x['side'], ex=x['exit'], ct=x['ctype'], ow=ow,
                     hm=held(x), net=net, nopn=None if nxt is None else nxt['opn'], nnet=nnet))
    print('| %s | %s | %s | %s | %s | %d | %s | %s | %s |'
          % (ln.U(x['opn']), 'LONG' if x['side'] > 0 else 'SHORT',
             '-' if x['exit'] is None else ln.U(x['exit']), x['ctype'], ow, held(x),
             '-' if net is None else '%+.4f' % net,
             '-' if nxt is None else ln.U(nxt['opn']),
             '-' if nnet is None else '%+.4f' % nnet))

print('')
print('## the cascade OPPOSES branch - it exhausted a leg and reversed. Was the reversal into a loser?')
print('')
op_rows = [r for r in rows if r['ow'] == 'mage-cascade OPPOSES' and r['nnet'] is not None]
bad = [r for r in op_rows if r['nnet'] < 0]
print('| the read | value |'); print('|---|---|')
print('| legs the cascade exhausted, with a next leg to judge | %d |' % len(op_rows))
print('| of those, the leg it opened ended NEGATIVE | %d |' % len(bad))
print('| that share | %s |' % ('%.1f%%' % (100.0 * len(bad) / len(op_rows)) if op_rows else '-'))
print('| summed net %% of the legs it opened | %+.4f |' % sum(r['nnet'] for r in op_rows))
print('| summed net %% of the negative ones only | %+.4f |' % sum(r['nnet'] for r in bad))
print('')
print('## the cascade MATCHES branch - it held a leg open. Did that leg end negative?')
print('')
hm_rows = [r for r in rows if r['hm'] > 0 and r['net'] is not None]
hbad = [r for r in hm_rows if r['net'] < 0]
print('| the read | value |'); print('|---|---|')
print('| legs with at least one cascade MATCHES row inside them | %d |' % len(hm_rows))
print('| of those, the leg ended NEGATIVE | %d |' % len(hbad))
print('| that share | %s |' % ('%.1f%%' % (100.0 * len(hbad) / len(hm_rows)) if hm_rows else '-'))
print('| summed net %% of those legs | %+.4f |' % sum(r['net'] for r in hm_rows))
print('| summed net %% of the negative ones only | %+.4f |' % sum(r['net'] for r in hbad))
print('')
print('## HIS 1030 GATE: honour the cascade\'s reversal ONLY when ws1..ws4 offer no baton candidate')
print('# *"if ws1-4r show no baton candidates at the cadence event (exhaust) then the cascade\'s')
print('#  (up/down) reversal signal is honored"*.')
print('# the candidate test is v4_lineage2.candidates with rider 0 and the cap at ws4, so it is the')
print('#  SAME ex-fence-and-towards test the baton uses - not a second copy. The ex-fence read goes')
print('#  through baton_ex_fence, which is the latch under LIN2_LATCH_EXFNC_ON 1.')
print('')
print('| the exit bar | dir | ws1..ws4 baton candidates at that bar | the gate | the leg it opened'
      ' | its net % |')
print('|---|---|---|---|---|---|')
gate = []
for r in rows:
    if r['ow'] != 'mage-cascade OPPOSES' or r['ex'] is None:
        continue
    cd = L2.candidates(BD, int(r['side']), int(r['ex']), 0, cap=4)
    g = 'GATED - a candidate exists' if cd else 'honoured - none'
    gate.append(dict(r, cd=tuple(cd), g=('gated' if cd else 'honoured')))
    print('| %s | %s | %s | %s | %s | %s |'
          % (ln.U(r['ex']), 'LONG' if r['side'] > 0 else 'SHORT',
             ', '.join('ws%d: %.2f' % (t, BD.value(t, int(r['ex']))) for t in cd) or 'none',
             g, '-' if r['nopn'] is None else ln.U(r['nopn']),
             '-' if r['nnet'] is None else '%+.4f' % r['nnet']))
print('')
print('| the read | value |')
print('|---|---|')
jg = [r for r in gate if r['nnet'] is not None]
for lab, sel in (('honoured - no ws1..ws4 candidate', 'honoured'),
                 ('GATED - a ws1..ws4 candidate exists', 'gated')):
    g = [r for r in jg if r['g'] == sel]
    bad = [r for r in g if r['nnet'] < 0]
    print('| %s - reversals | %d |' % (lab, len(g)))
    print('| %s - of those, the leg it opened LOST | %d |' % (lab, len(bad)))
    print('| %s - that share | %s |'
          % (lab, '%.1f%%' % (100.0 * len(bad) / len(g)) if g else '-'))
    print('| %s - summed net %% of the legs it opened | %+.4f |' % (lab, sum(r['nnet'] for r in g)))
    print('| %s - summed net %% of the losing ones | %+.4f |' % (lab, sum(r['nnet'] for r in bad)))
print('| of the LOSING reversals, how many his gate removes | %d of %d |'
      % (len([r for r in jg if r['g'] == 'gated' and r['nnet'] < 0]),
         len([r for r in jg if r['nnet'] < 0])))
print('| of the WINNING reversals, how many his gate also removes | %d of %d |'
      % (len([r for r in jg if r['g'] == 'gated' and r['nnet'] >= 0]),
         len([r for r in jg if r['nnet'] >= 0])))

print('')
print('## every owner, with its legs and its net')
print('')
print('| who owned the exit | legs | legs negative | summed net % | summed net % of the legs they'
      ' opened |')
print('|---|---|---|---|---|')
for ow in sorted({r['ow'] for r in rows}):
    g = [r for r in rows if r['ow'] == ow]
    sc = [r for r in g if r['net'] is not None]
    nx = [r for r in g if r['nnet'] is not None]
    print('| %s | %d | %d | %s | %s |'
          % (ow, len(g), sum(1 for r in sc if r['net'] < 0),
             '%+.4f' % sum(r['net'] for r in sc) if sc else '-',
             '%+.4f' % sum(r['nnet'] for r in nx) if nx else '-'))
print('')
print('| the read | value |'); print('|---|---|')
print('| legs in the chain | %d |' % len(lg))
print('| seconds to compute | %.1f |' % (time.time() - T0))
