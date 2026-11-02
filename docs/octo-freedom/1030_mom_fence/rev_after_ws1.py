"""HIS 1030 HYPOTHESIS, TESTED: does ws2/ws3/ws4 reverse soon after ws1, and only when the
immediate exhaust is the right call?

His words: *"I think the immediate exhaust event (where the candidate lines never make it to
exfence) will print a ws2,ws3,or ws4 reversal soon after ws1 reverses. if the baton pass is going
to happen, then the lines above ws1 are more likely to continue on their trajectory (so no reversal
will be detected in thosse lines)"*, and *"not proven (I can't prove it on TV closed bars panes)"*.

SO THE DISCRIMINATOR HE IS PROPOSING IS A REVERSAL, NOT A CANDIDATE. gate_hold.py asks whether
ws2..ws4 become baton CANDIDATES - past the fence and `towards`. This asks whether they REVERSE,
which is the opposite reading of the same lines, and it is the test his hypothesis names.

THE TWO GROUPS, split by what the board offered at the cadence bar:
    immediate exhaust   no baton candidate anywhere in ws1..ws4 - his "the candidate lines never
                        make it to exfence". He predicts ws2..ws4 REVERSALS soon after ws1's.
    a baton was there   a candidate existed. He predicts NO reversal in those lines - they
                        continue.

CAUSAL. Every reversal is read at its STAMP, lift + LIFT_WOB - 1, and the window runs forward from
ws1's own stamp. A reversal inside the window is knowable at the window's last bar, which is the
bar a consumer would act on. Nothing past it is read.

THIS IS A MECHANISM TEST, NOT A NET TEST. It reports counts and timings. No knob is moved.
"""
import io
import os
import sys
import time

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
#   THE SWALLOW COVERS THE NOISY IMPORTS ONLY, and `finally` restores stderr whatever
#   happens. Without it a refusal from v4_knobs.check() - an off-ruled run with no
#   W_V4_EXPERIMENT=1 - goes into the StringIO and the process exits 1 with NOTHING on
#   either stream. That cost a diagnosis on 1101.
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_rcfg_sweep as RS
    import v4_live_lines as LL
    import v4_l2_proxy as PX
    import v4_chain as CH
    import v4_lineage2 as L2
    import v4_fast as F
    import v4_signal as SG
    import v4_sig_lin2_reentry as L2R
    import ln
    from v4_backstop_trades import prices
finally:
    sys.stderr = _e

T0 = time.time()
K.LIN2_PSEUDO_MIN_TF = 99
K.LIN2_LATCH_EXFNC_ON = 1
K.LIN2_B1_HOLD = 0
MINS = (1, 2, 3, 4)
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


def stamps(tf, side):
    """every reversal of ws{tf}r on `side`, at its STAMP. -> sorted int array."""
    return np.asarray(sorted(int(K.lift_stamp(b))
                             for b in F.revs(np.asarray(E[int(tf)], float), int(tf), int(side))),
                      int)


ST = {(t, s): stamps(t, s) for t in (1, 2, 3, 4) for s in (-1, +1)}
rows = []
for i, x in enumerate(lg):
    if x['exit'] is None:
        continue
    ex = [r for r in x['rows'] if r['stage'] == 'EXHAUST']
    if not ex or 'OPPOSES' not in str(ex[-1].get('why') or ''):
        continue
    bar, side = int(x['exit']), int(x['side'])
    cd = L2.candidates(BD, side, bar, 0, cap=4)
    #   ws1r's own most recent reversal stamp at or before the cadence bar - the anchor his
    #   hypothesis starts from. No stamp means the window has no origin and the row says so.
    s1 = ST[(1, side)]
    j = int(np.searchsorted(s1, bar, 'right')) - 1
    a1 = int(s1[j]) if j >= 0 else None
    nxt = lg[i + 1] if i + 1 < len(lg) else None
    nnet = None if (nxt is None or nxt['exit'] is None) else nxt['rel'] - CH.DRAG_PCT
    r = dict(bar=bar, side=side, grp=('a baton was there' if cd else 'immediate exhaust'),
             a1=a1, nnet=nnet)
    for m in MINS:
        hit = None
        if a1 is not None:
            for t in (2, 3, 4):
                s = ST[(t, side)]
                w = s[(s >= a1) & (s <= a1 + m * 12)]
                if len(w):
                    b0 = int(w[0])
                    if hit is None or b0 < hit[0]:
                        hit = (b0, t)
        r['m%d' % m] = hit
    rows.append(r)

print('# HIS 1030 HYPOTHESIS | WINDOW %s .. %s | TAPE %d bars | RULED_OK %s'
      % (ln.U(A), ln.U(B), len(close), K.RULED_OK))
print('# the stop is OFF. RMOM_FNC %.1f, L2_MOM_MAXTF %d. reversals are read at their STAMP,'
      ' lift + LIFT_WOB - 1 = lift + %d bars.' % (K.RMOM_FNC, K.L2_MOM_MAXTF, K.LIFT_WOB - 1))
print('# the window runs forward from ws1r\'s own reversal stamp, and 12 bars is one minute.')
print('')
print('## every cascade reversal, its group, and the first ws2/ws3/ws4 reversal after ws1\'s')
print('')
print('| the cadence bar | dir | the group | ws1r\'s reversal stamp | 1 min | 2 min | 3 min | 4 min'
      ' | the next leg\'s net % |')
print('|---|---|---|---|---|---|---|---|---|')
for r in sorted(rows, key=lambda z: z['bar']):
    c = []
    for m in MINS:
        h = r['m%d' % m]
        c.append('-' if h is None else 'ws%d at %s' % (h[1], ln.U(h[0])[11:]))
    print('| %s | %s | %s | %s | %s | %s | %s | %s | %s |'
          % (ln.U(r['bar']), 'LONG' if r['side'] > 0 else 'SHORT', r['grp'],
             '-' if r['a1'] is None else ln.U(r['a1'])[11:], c[0], c[1], c[2], c[3],
             '-' if r['nnet'] is None else '%+.4f' % r['nnet']))

print('')
print('## HIS CLAIM, scored. He predicts a reversal in the immediate-exhaust group and none in the'
      ' baton group.')
print('')
print('| the window | the group | events | a ws2/ws3/ws4 reversal inside it | that share |')
print('|---|---|---|---|---|')
for m in MINS:
    for g in ('immediate exhaust', 'a baton was there'):
        sel = [r for r in rows if r['grp'] == g and r['a1'] is not None]
        hit = [r for r in sel if r['m%d' % m] is not None]
        print('| %d min | %s | %d | %d | %s |'
              % (m, g, len(sel), len(hit),
                 '%.1f%%' % (100.0 * len(hit) / len(sel)) if sel else '-'))

print('')
print('| the read | value |')
print('|---|---|')
print('| cascade reversals in the window | %d |' % len(rows))
print('| immediate exhaust - no ws1..ws4 candidate | %d |'
      % len([r for r in rows if r['grp'] == 'immediate exhaust']))
print('| a baton was there | %d |' % len([r for r in rows if r['grp'] == 'a baton was there']))
print('| rows with no ws1r reversal stamp at or before the cadence | %d |'
      % len([r for r in rows if r['a1'] is None]))
print('| seconds to compute | %.1f |' % (time.time() - T0))
