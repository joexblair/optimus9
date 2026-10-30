"""THE oob LATCH A/B OVER THE WHOLE OF 2026-08-30. Joe 1029: *"do a 08-30 chain AB test to validate
or drop the oob latch"*.

ARM A is the banked machine: the baton path reads ex-fence from the latch and oob from the line
value.

ARM B routes the baton path's oob reads through the latch as well - ONE latch read at depth, which
is latched AND 15/85 confirmed at or after that latch's own on-bar. It is a filter on the one
state, never a second latch, because his reading makes "oob but not ex-fence" impossible and the
code agrees: 0 values across 0.00 to 100.00 are oob without also being ex-fence.

NOTHING ELSE MOVES. Same open, same window, same board, same cascade anchor, same holds.
"""
import os, sys, io, time
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS
import v4_live_lines as LL, v4_l2_proxy as PX, v4_chain as CH
import v4_signal as SG, v4_sig_lin2_reentry as L2R
from v4_backstop_trades import prices
sys.stderr = _e
T0 = time.time()

A, B = ln.K('2026-08-30 00:00:00'), ln.K(os.environ.get('W_AB_END',
                                                           '2026-08-30 23:59:55'))
close, phi, plo = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = LL.arm_lines(E)
MG = LL.mage(12)
B1 = np.asarray(CL['b'], float)
SIG = [g for g in L2R.signals(B1, MG) if g['bar'] == ln.K('2026-08-29 23:53:50')]
assert len(SIG) == 1
OPEN_DIR = SG.direction(int(SIG[0]['side']))
OPEN = (SG.fire_bar(SIG[0]), SG.target_side(OPEN_DIR))
ALLSIG = L2R.signals(B1, MG)

print('# THE oob LATCH A/B, THE WHOLE OF 2026-08-30')
print('# WINDOW %s .. %s | TAPE %d bars' % (ln.U(A), ln.U(B), len(close)))
print('# the open is %s %s for both arms. the ex-fence latch is ON at a %d-bar = %d s hold.'
      % (ln.U(OPEN[0]), OPEN_DIR, K.LIN2_EXFNC_LATCH_WOB, K.LIN2_EXFNC_LATCH_WOB * 5))
print('# the cascade anchors on a ws1Mage extremum. the 1.1%% stop is off. drag %.4f%% a round trip.'
      % CH.DRAG_PCT)
print('# ARM A: the baton path reads oob from the LINE VALUE. banked.')
print('# ARM B: it reads oob from the ONE latch at depth - latched AND 15/85 confirmed since the')
print('#   latch own on-bar. a filter on the one state, never a second latch.')
print('')

RES = []
for on, lab in ((0, 'A: oob from the line value'), (1, 'B: oob from the latch at depth')):
    K.LIN2_LATCH_OOB_ON = on
    bd = PX.Board(E, E, MG=MG, MGE=MG, PS=None)
    lg, zero, op = CH.legs(CL, bd, close, phi, plo, A, B, MG=MG, B1=B1, open_at=OPEN,
                           resig=ALLSIG)
    RES.append((lab, lg, zero, CH.score(lg), bd))
K.LIN2_LATCH_OOB_ON = 0

print('## every leg of each arm, one row per leg')
print('')
print('| the arm | leg | the open | dir | the exit | ended by | held min | the rider chain |'
      ' MAE % | MFE % | realised % | drag % | net % |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for lab, lg, zero, sc, bd in RES:
    for i, x in enumerate(lg, 1):
        ch = []
        for r in x['rows']:
            rd = r.get('rider')
            if rd and (not ch or ch[-1] != rd):
                ch.append(rd)
        chs = ' > '.join('ws%d' % t for t in ch) if ch else '-'
        d = 'LONG' if x['side'] > 0 else 'SHORT'
        if x['exit'] is None:
            print('| %s | %d | %s | %s | - | no exit | - | %s | - | - | - | - | - |'
                  % (lab.split(':')[0], i, ln.U(x['opn']), d, chs))
            continue
        print('| %s | %d | %s | %s | %s | %s | %.1f | %s | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
              % (lab.split(':')[0], i, ln.U(x['opn']), d, ln.U(x['exit']), x['ctype'],
                 x['held_min'], chs, x['mae'], x['mfe'], x['rel'], CH.DRAG_PCT,
                 x['rel'] - CH.DRAG_PCT))
    print('| %s | TOTAL %d legs | | | | | %.1f | | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
          % (lab.split(':')[0], sc['n'], sc['held'], sc['mae'], sc['mfe'], sc['rel'], sc['drag'],
             sc['net']))
print('')

print('## the two arms, totals')
print('')
print('| the read | ' + ' | '.join(l for l, _g, _z, _s, _b in RES) + ' |')
print('|---|---|---|')
for nm, k, f in (('legs', 'n', '%d'), ('legs with no exit', 'unres', '%d'),
                 ('exits on the barrage', 'barr', '%d'),
                 ('legs net-positive after drag', 'win', '%d'),
                 ('summed held min', 'held', '%.1f'), ('summed MAE %', 'mae', '%.4f'),
                 ('summed MFE %', 'mfe', '%+.4f'), ('summed realised %', 'rel', '%+.4f'),
                 ('summed drag %', 'drag', '%.4f'), ('summed net %', 'net', '%+.4f')):
    print(('| %s | ' % nm) + ' | '.join(f % sc[k] for _l, _g, _z, sc, _b in RES) + ' |')
a0 = RES[0][3]['net']
print('| net %% against arm A | +0.0000 | %+.4f |' % (RES[1][3]['net'] - a0))
print('| MFE collected | '
      + ' | '.join(('%.1f%%' % (sc['rel'] / sc['mfe'] * 100.0)) if sc['mfe'] > 0 else 'n/a'
                   for _l, _g, _z, sc, _b in RES) + ' |')
print('| legs with no bars | ' + ' | '.join('%d' % len(z) for _l, _g, z, _s, _b in RES) + ' |')
print('')

print('## how far the depth read differs from the plain oob read, 2026-08-30')
print('')
bd = RES[1][4]
print('| the line | side | bars oob by VALUE | bars oob at DEPTH | the difference |')
print('|---|---|---|---|---|')
tv = td = 0
for sd, nm in ((-1, 'LOW'), (+1, 'HIGH')):
    for t in range(1, int(K.L2_MOM_MAXTF) + 1):
        if t not in bd.tfs:
            continue
        vo = K.oob_mask(bd.line(t), sd)[A:B + 1]
        dp = bd._deep(t, sd)[A:B + 1]
        nv, nd = int(np.count_nonzero(vo)), int(np.count_nonzero(dp))
        tv += nv; td += nd
        print('| ws%d | %s | %d | %d | %+d |' % (t, nm, nv, nd, nd - nv))
print('')
print('| the read | value |')
print('|---|---|')
print('| summed bars oob by value, 24 line-sides | %d |' % tv)
print('| summed bars oob at depth | %d |' % td)
print('| the depth read as a multiple of the value read | %.2fx |' % (td / tv if tv else 0))
print('| seconds to compute | %.1f |' % (time.time() - T0))
