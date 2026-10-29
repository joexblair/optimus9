"""THE FIRST 3 LEGS ON THE PSEUDO BOARD, TIMESTAMPED ROWS. Joe 1028:

    "1, I honestly don't know what to expect. our only way to begin to know is to build the
     timestamped-rows tables for the first 3 legs"
    "3, let it happen. we need to get in the weeds now - seeing the legs in timestamped rows will
     give us both the clarity we're hunting for"

THE BOARD: ws1..ws3 keep their current reads; ws4 upward read PSEUDO-CLOSED for the ex-fence state
and for the value printed beside it. LIN2_PSEUDO_MIN_TF 4, his value.

THE WALK IS UNCHANGED - v4_lineage2.walk, every banked mech, decisions at cadences. Only the board
under it moved.

TWO REVERSAL COLUMNS, his ruling: *"the candidates for a reversal mech are lift-off and pseudo - we
need to see both reversal times in different columns"*. Per row, for the rider named on it:
    lift-off rev   the most recent lift_off stamp on the EMERGING line at or before the bar
    pseudo rev     the most recent lift_off stamp on the PSEUDO line at or before the bar
The WALK still acts on lift-off - the reversal mech is undecided and the bank does not move.

HIS 01:46:55 CHECK, point 2: *"pseudo for ws4 at 90.48 isn't bad, depending on what ws5 is printing
when ws4 returns to ib. if ws5 is infence at ws4-ib, then the exahaust stands"*. Every row carries
the candidate set, so the ws4 ib-cross and ws5's state at it are both visible.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1027_pseudo_closed')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
import v4_l2_proxy as PX, v4_lineage2 as L2
import pseudo_closed as PC
from optimus9.analysis.jig import lift_off
from v4_backstop_trades import prices
sys.stderr = _e

DAY = '2026-08-30'
A, B = ln.K('%s 00:00:00' % DAY), ln.K('%s 23:59:55' % DAY)
MINTF, TOP = int(K.LIN2_PSEUDO_MIN_TF), int(K.L2_MOM_MAXTF)
N_LEGS = 3
close, _h, _l = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
C = CP.ladder(E)
CL = CP.arm_lines(E)
MGL = {t: CP.line('ws%dMage' % t, t * 60) for t in range(1, 13)}
MGE = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}

IDX = np.arange(A, B + 1)
PS = {}
for t in range(MINTF, TOP + 1):
    PS[t] = np.full(len(close), np.nan)
    PS[t][IDX] = PC.series(close, t, IDX)
BD = PX.Board(C, E, MG=MGL, MGE=MGE, PS=PS)

#   the two reversal sources, per TF per side: stamps on the EMERGING line and on the PSEUDO line
REV = {}
for t in range(1, TOP + 1):
    for sd in (-1, +1):
        REV[('lift', t, sd)] = sorted(int(K.lift_stamp(int(b))) for b in
                                      lift_off(np.asarray(E[t], float), sd, K.LIFT_PTS,
                                               K.gap_for(t), K.LIFT_TOL, int(K.LIFT_WOB)))
        src = PS[t] if t in PS else np.asarray(C[t], float)
        REV[('pseudo', t, sd)] = sorted(int(K.lift_stamp(int(b))) for b in
                                        lift_off(src, sd, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL,
                                                 int(K.LIFT_WOB)))


def last_rev(kind, tf, sd, bar):
    r = [x for x in REV[(kind, int(tf), int(sd))] if x <= int(bar)]
    return ln.U(r[-1]) if r else 'none'


print('# THE FIRST %d LEGS ON THE PSEUDO BOARD, %s' % (N_LEGS, DAY))
print('# ws1..ws%d keep their reads; ws%d.. read PSEUDO for ex-fence and for the value shown.'
      % (MINTF - 1, MINTF))
print('# the walk is unchanged - every banked mech, decisions at cadences. only the board moved.')
print('# the WALK acts on lift-off; both reversal times are reported. his ruling.')
print('# the rider prefix says which board answered: cws = closed, ws = pseudo.')
print('# RULED_OK %s | LIN2_PSEUDO_MIN_TF %d | LIFT_WOB %d' % (K.RULED_OK, MINTF, K.LIFT_WOB))
print('')

prev, leg = int(A), 0
side = +1
while leg < N_LEGS:
    v, bar, rows = L2.walk(CL, BD, close, side, prev, B)
    leg += 1
    arm = [r for r in rows if r['stage'] == 'ARM']
    print('## leg %d - target side %s, walking from %s'
          % (leg, 'HIGH' if side > 0 else 'LOW', ln.U(prev)))
    print('')
    print('| the bar | stage | rider | its value | board | lift-off rev | pseudo rev | candidates |'
          ' why |')
    print('|---|---|---|---|---|---|---|---|---|')
    for r in rows:
        b = r.get('bar')
        rd = r.get('rider')
        vs = ('%.2f' % BD.value(rd, b)) if (rd and b is not None) else '-'
        src = BD.state_src(rd) if rd else '-'
        pref = 'ws' if src == 'pseudo' else 'cws'
        lo = last_rev('lift', rd, side, b) if (rd and b is not None) else '-'
        pr = last_rev('pseudo', rd, side, b) if (rd and b is not None) else '-'
        cd = r.get('cands')
        print('| %s | %s | %s | %s | %s | %s | %s | %s | %s |'
              % (ln.U(b) if b is not None else '-', r['stage'],
                 '%s%d' % (pref, rd) if rd else '-', vs, src, lo, pr,
                 (','.join('ws%d' % x for x in cd) if cd else ('none' if cd == () else '-')),
                 str(r['why']).replace('|', '\\|')))
    print('')
    print('| leg %d | value |' % leg)
    print('|---|---|')
    print('| the verdict | %s |' % v)
    print('| the bar | %s |' % (ln.U(bar) if bar is not None else '-'))
    print('| the arm | %s |' % (ln.U(arm[0]['bar']) if arm and arm[0]['bar'] is not None else '-'))
    print('| rows | %d |' % len(rows))
    print('')
    if bar is None:
        break
    prev, side = int(bar), -side
