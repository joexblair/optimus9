"""THE TRADE CHAINS ON 2026-08-30, FOUR OPENS, ONE TABLE.

Joe 1029: *"you have enough now to recreate the comparative trade chains that we're produced ~70
minutes ago and starting at the wrong time with the wrong direction"*.

THE FOUR OPENS, and two of them are mine and wrong:

  A  lin2-reentry through the router      2026-08-29 23:53:55 SHORT   the signal is 23:53:50, the
                                                                     router fires one bar later
  B  handed in at the window start        2026-08-30 00:00:00 LONG    never a mech, just a boundary
                                                                     and a side I chose
  C  the ws5Mage crossing-to-oob bar      2026-08-29 23:50:00 SHORT   MINE AND WRONG - built on the
                                                                     last-completed-bar read, which
                                                                     is dropped
  D  the backward search's answer         2026-08-29 23:56:00 SHORT   MINE AND WRONG - a bar the
                                                                     chain cannot reach, because
                                                                     the trade opened at 23:53:50

Every leg between the open and the window's end is walked and scored. Drag keeps its own column
and its own total.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1027_pseudo_closed')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
import v4_l2_proxy as PX, v4_chain as CH, v4_signal as SG, v4_sig_lin2_reentry as L2R
import pseudo_closed as PC
from v4_backstop_trades import prices
sys.stderr = _e

A, B = ln.K('2026-08-30 00:00:00'), ln.K('2026-08-30 23:59:55')
close, phi, plo = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = CP.arm_lines(E)
C = CP.ladder(E)
MGL = {t: CP.line('ws%dMage' % t, t * 60) for t in range(1, 13)}
B1 = np.asarray(ln.line('ws1b'), float)
MG = {t: np.asarray(ln.line('ws%dMage' % t), float) for t in range(1, 13)}

sig = [s for s in L2R.signals(B1, MG) if s['bar'] <= A]
assert sig, 'no lin2-reentry signal at or before the window start'
first = sig[-1]
#   THE LAST SIGNAL BEFORE THE WINDOW IS NOT NECESSARILY THE ONE THE ROUTER TOOK. It is used here
#   only to place arm A's open for the comparison; which signal the router acts on over the full
#   tape is the router's call and is not decided in this file.
OPENS = [
    ('A: lin2-reentry, the router fire bar', ln.K('2026-08-29 23:53:55'), -1),
    ('B: handed in at the window start', A, +1),
    ('C: MINE AND WRONG - the ws5Mage crossing to oob', ln.K('2026-08-29 23:50:00'), -1),
    ('D: MINE AND WRONG - the backward search', ln.K('2026-08-29 23:56:00'), -1),
]
LO = min(b for _n, b, _s in OPENS + [('w', A, 0)])
TOP = max(int(K.L2_MOM_MAXTF), int(K.LIN2_BARRAGE_MAX_TF))
IDX = np.arange(LO, B + 1)
PS = {}
for t in range(int(K.LIN2_PSEUDO_MIN_TF), TOP + 1):
    PS[t] = np.full(len(close), np.nan)
    PS[t][IDX] = PC.series(close, t, IDX)
BD = PX.Board(C, E, MG=MGL, MGE=MG, PS=PS)

print('# THE TRADE CHAINS ON 2026-08-30, FOUR OPENS')
print('# WINDOW %s .. %s | TAPE %d bars | RULED_OK %s' % (ln.U(A), ln.U(B), len(close), K.RULED_OK))
print('# the lines the open is built from are the LIVE read. drag %.4f%% per round trip.'
      % CH.DRAG_PCT)
print('# every leg between the open and the window end is walked. no cap, no cut-off.')
print('')
print('## the lin2-reentry signals near the window, and what the router does with each')
print('')
print('| the signal bar | the side ws1b came in from | the router fire bar | the direction |')
print('|---|---|---|---|')
for s in [x for x in L2R.signals(B1, MG)
          if ln.K('2026-08-29 23:00:00') <= x['bar'] <= ln.K('2026-08-30 00:30:00')]:
    print('| %s | %s | %s | %s |'
          % (ln.U(s['bar']), 'HIGH' if s['side'] > 0 else 'LOW', ln.U(SG.fire_bar(s)),
             SG.direction(s['side'])))
print('')

RES = []
for name, bar, sd in OPENS:
    lg, zero, op = CH.legs(CL, BD, close, phi, plo, A, B, MG=MG, B1=B1, open_at=(bar, sd))
    RES.append((name, bar, sd, lg, zero, CH.score(lg)))

print('## every leg of every chain, one row per leg')
print('')
print('| the chain | leg | the open | dir | the exit | ended by | held min | MAE % | MFE % |'
      ' realised % | drag % | net % |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
for name, bar, sd, lg, zero, sc in RES:
    for i, x in enumerate(lg, 1):
        d = 'LONG' if x['side'] > 0 else 'SHORT'
        if x['exit'] is None:
            print('| %s | %d | %s | %s | - | no exhaust | - | - | - | - | - | - |'
                  % (name, i, ln.U(x['opn']), d))
            continue
        print('| %s | %d | %s | %s | %s | %s | %.1f | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
              % (name, i, ln.U(x['opn']), d, ln.U(x['exit']), x['ctype'], x['held_min'],
                 x['mae'], x['mfe'], x['rel'], CH.DRAG_PCT, x['rel'] - CH.DRAG_PCT))
    print('| %s | TOTAL %d legs | | | | | %.1f | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
          % (name, sc['n'], sc['held'], sc['mae'], sc['mfe'], sc['rel'], sc['drag'], sc['net']))
print('')

print('## the four chains, totals')
print('')
print('| the read | ' + ' | '.join(n.split(':')[0] for n, _b, _s, _l, _z, _c in RES) + ' |')
print('|---|' + '---|' * len(RES))
print('| the open bar | ' + ' | '.join(ln.U(b) for _n, b, _s, _l, _z, _c in RES) + ' |')
print('| the direction | ' + ' | '.join('SHORT' if s < 0 else 'LONG'
                                        for _n, _b, s, _l, _z, _c in RES) + ' |')
for lab, k, f in (('legs', 'n', '%d'), ('unresolved legs', 'unres', '%d'),
                  ('barrage exits', 'barr', '%d'), ('legs net-positive after drag', 'win', '%d'),
                  ('summed held min', 'held', '%.1f'), ('summed MAE %', 'mae', '%.4f'),
                  ('summed MFE %', 'mfe', '%+.4f'), ('summed realised %', 'rel', '%+.4f'),
                  ('summed drag %', 'drag', '%.4f'), ('summed net %', 'net', '%+.4f')):
    print(('| %s | ' % lab) + ' | '.join(f % sc[k] for _n, _b, _s, _l, _z, sc in RES) + ' |')
base = [sc['net'] for n, _b, _s, _l, _z, sc in RES if n.startswith('B')][0]
print('| net % against the handed-in open | '
      + ' | '.join('%+.4f' % (sc['net'] - base) for _n, _b, _s, _l, _z, sc in RES) + ' |')
print('| MFE collected | '
      + ' | '.join(('%.1f%%' % (sc['rel'] / sc['mfe'] * 100.0)) if sc['mfe'] > 0 else 'n/a'
                   for _n, _b, _s, _l, _z, sc in RES) + ' |')
print('')
print('| the read | value |')
print('|---|---|')
print('| legs with no bars, exit before open | %s |'
      % ', '.join('%s %d' % (n.split(':')[0], len(z)) for n, _b, _s, _l, z, _c in RES))
print('| those legs are not scored and not charged drag | whether such a leg pays the %.4f%% is'
      ' UNRULED |' % CH.DRAG_PCT)
