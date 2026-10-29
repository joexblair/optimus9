"""THE CHAIN OPEN, A/B: his ws5Mage mech against the handed-in open it replaces.

Joe 1029: *"the chain open should be on the ws5Mage oob with at least 2 higher TFs printing LOWER
values if ws5Mage is high oob, HIGHER if it is low oob"*, and on the window *"option B is the
answer"* - the window stays put and the chain reaches back for the open already running into it.

BOTH ARMS, SAME WINDOW, in one table, because a changed number is printed beside the one it
replaced. The pseudo-closed lines are built from the EARLIER of the two opens so neither arm reads
a NaN the other does not.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1027_pseudo_closed')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
import v4_l2_proxy as PX, v4_l2_cadence as CAD, v4_chain as CH
import pseudo_closed as PC
from v4_backstop_trades import prices
sys.stderr = _e

WIN = os.environ.get('W_WIN', 'day')
if WIN == 'week':
    A, B = ln.K('2026-08-30 00:00:00'), ln.K('2026-09-06 23:59:55')
else:
    A, B = ln.K('2026-08-30 00:00:00'), ln.K('2026-08-30 23:59:55')

close, phi, plo = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
C = CP.ladder(E)
CL = CP.arm_lines(E)
MGL = {t: CP.line('ws%dMage' % t, t * 60) for t in range(1, 13)}
MGE = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
TOP = max(int(K.L2_MOM_MAXTF), int(K.LIN2_BARRAGE_MAX_TF))

#   THE OPEN IS FOUND FIRST, off the Mage ladder alone, so the pseudo span can reach it.
B1E = np.asarray(ln.line('ws1b'), float)                      # EMERGING ws1b
MGEM = {t: np.asarray(ln.line('ws%dMage' % t), float) for t in range(1, 13)}
prod = CAD.chain_open(B1E, MGEM, A)
assert prod is not None, 'no chain open at or before %s' % ln.U(A)
LO = min(int(prod['bar']), int(A))
IDX = np.arange(LO, B + 1)
PS = {}
for t in range(int(K.LIN2_PSEUDO_MIN_TF), TOP + 1):
    PS[t] = np.full(len(close), np.nan)
    PS[t][IDX] = PC.series(close, t, IDX)
BD = PX.Board(C, E, MG=MGL, MGE=MGE, PS=PS)

print('# THE CHAIN OPEN, A/B - his ws5Mage mech against the handed-in open')
print('# WINDOW %s .. %s | TAPE %d bars | RULED_OK %s'
      % (ln.U(A), ln.U(B), len(close), K.RULED_OK))
print('# KNOBS: LIN2_CHAIN_OPEN_ON %d | LIN2_CHAIN_OPEN_TF %d | LIN2_CHAIN_OPEN_LINES %d |'
      ' band ws%d..ws%d'
      % (K.LIN2_CHAIN_OPEN_ON, K.LIN2_CHAIN_OPEN_TF, K.LIN2_CHAIN_OPEN_LINES,
         K.LIN2_CHAIN_OPEN_TF + 1, K.L2_MOM_MAXTF))
print('# PSEUDO LINES built from %s - the earlier of the two opens - to the window end.' % ln.U(LO))
print('# DRAG %.4f%% per round trip, its own column and its own total.' % CH.DRAG_PCT)
print('')

print('## the produced open')
print('')
print('| the read | value |')
print('|---|---|')
print('| the firing bar | %s |' % ln.U(prod['bar']))
print('| the raw ws1b cross | %s |' % ln.U(prod['raw']))
print('| the candidate side | %s |' % ('HIGH' if prod['cand_side'] > 0 else 'LOW'))
print('| the anchor bar | %s |' % ln.U(prod['anchor']))
print('| the trade side | %s |' % ('LONG' if prod['side'] > 0 else 'SHORT'))
print('| ws%dMage at the anchor | %.2f |' % (K.LIN2_CHAIN_OPEN_TF, prod['trig']))

print('| higher TFs on the far side | %d of %d - %s |'
      % (len(prod['lines']), K.L2_MOM_MAXTF - K.LIN2_CHAIN_OPEN_TF,
         ', '.join('ws%d' % t for t in prod['lines'])))
print('| required | %d |' % K.LIN2_CHAIN_OPEN_LINES)
print('| his stated moment | 2026-08-29 ~23:45, a SHORT |')
print('| bars before the window start | %d = %.1f min |'
      % (A - prod['bar'], (A - prod['bar']) * 5 / 60.0))
print('')

ARMS = []
for on, lab in ((1, 'A: the ws1b firing mech'), (0, 'B: the handed-in open, +1 at 00:00:00')):
    K.LIN2_CHAIN_OPEN_ON = on
    lg, zero, op = CH.legs(CL, BD, close, phi, plo, A, B, MG=MGEM, fallback_side=+1,
                           B1=B1E)
    ARMS.append((lab, on, lg, zero, op, CH.score(lg)))
K.LIN2_CHAIN_OPEN_ON = 1

print('## the two arms, one row per leg')
print('')
print('| arm | leg | the open | dir | the exit | ended by | held min | the rider chain | MAE % |'
      ' MFE % | realised % | drag % | net % |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for lab, on, lg, zero, op, sc in ARMS:
    for i, x in enumerate(lg, 1):
        ch = []
        for r in x['rows']:
            rd = r.get('rider')
            if rd and (not ch or ch[-1] != rd):
                ch.append(rd)
        chs = ' > '.join('ws%d' % t for t in ch) if ch else '-'
        d = 'LONG' if x['side'] > 0 else 'SHORT'
        if x['exit'] is None:
            print('| %s | %d | %s | %s | - | no exhaust | - | %s | - | - | - | - | - |'
                  % (lab, i, ln.U(x['opn']), d, chs))
            continue
        print('| %s | %d | %s | %s | %s | %s | %.1f | %s | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
              % (lab, i, ln.U(x['opn']), d, ln.U(x['exit']), x['ctype'], x['held_min'], chs,
                 x['mae'], x['mfe'], x['rel'], CH.DRAG_PCT, x['rel'] - CH.DRAG_PCT))
    print('| %s | TOTAL %d legs | | | | | %.1f | | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
          % (lab, sc['n'], sc['held'], sc['mae'], sc['mfe'], sc['rel'], sc['drag'], sc['net']))
print('')

print('## the two arms, totals')
print('')
print('| the read | %s | %s |' % (ARMS[0][0], ARMS[1][0]))
print('|---|---|---|')
a, b = ARMS[0][5], ARMS[1][5]
oa, ob = ARMS[0][4], ARMS[1][4]
print('| the open bar | %s | %s |' % (ln.U(oa['bar']), ln.U(ob['bar'])))
print('| the first side | %s | %s |' % ('LONG' if oa['side'] > 0 else 'SHORT',
                                        'LONG' if ob['side'] > 0 else 'SHORT'))
print('| where the open comes from | %s | %s |' % (oa['src'], ob['src']))
for nm, k, f in (('legs', 'n', '%d'), ('unresolved legs', 'unres', '%d'),
                 ('barrage exits', 'barr', '%d'), ('legs net-positive after drag', 'win', '%d'),
                 ('summed held min', 'held', '%.1f'), ('summed MAE %', 'mae', '%.4f'),
                 ('summed MFE %', 'mfe', '%+.4f'), ('summed realised %', 'rel', '%+.4f'),
                 ('summed drag %', 'drag', '%.4f'), ('summed net %', 'net', '%+.4f')):
    print(('| %s | ' + f + ' | ' + f + ' |') % (nm, a[k], b[k]))
print('| net %% difference, A minus B | %+.4f | |' % (a['net'] - b['net']))
print('| MFE collected | %s | %s |'
      % ('%.1f%%' % (a['rel'] / a['mfe'] * 100.0) if a['mfe'] > 0 else 'n/a',
         '%.1f%%' % (b['rel'] / b['mfe'] * 100.0) if b['mfe'] > 0 else 'n/a'))
print('')

print('## the zero-length legs - exhaust bar BEFORE the open bar')
print('')
print('| arm | the open bar | the exit bar | dir | ended by |')
print('|---|---|---|---|---|')
nz = 0
for lab, on, lg, zero, op, sc in ARMS:
    for z in zero:
        nz += 1
        print('| %s | %s | %s | %s | %s |'
              % (lab, ln.U(z['opn']), ln.U(z['exit']),
                 'LONG' if z['side'] > 0 else 'SHORT', z['ctype']))
if not nz:
    print('| - | none in either arm over this window | | | |')
print('')
print('| the read | value |')
print('|---|---|')
print('| zero-length legs | %d |' % nz)
print('| NOT scored and NOT charged drag | they span no bars; whether such a leg pays the'
      ' %.4f%% is UNRULED |' % CH.DRAG_PCT)
