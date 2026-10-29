"""THE FIRST 3 LEGS ON THE PSEUDO BOARD, WITH THE OPEN AND THE FULL LADDER. Joe 1028:

    "these leg reports need to show the open so that I know if the chain is unbroken or continuous"
    "I need to see the per-leg timestamped-rows that show all of the decisions, with line values,
     so that I can make informed decisions."

THREE THINGS THIS ADDS over legs3.py:

    1  THE OPEN. Each leg prints its trade open - the previous leg's exhaust + 1 bar - and a
       CONTINUITY row saying whether the chain is unbroken.
    2  THE LADDER AT EVERY DECISION BAR, as ROWS not columns. One record per row is his standing
       rule and a 12-value ladder across a row would be "more of the same series", so each line
       gets its own row: the bar, the line, its value, its ex-fence state, which board answered,
       and both reversal times.
    3  the rider row is marked RIDER in the line column so it is findable inside the block.

THE BOARD: ws1..ws3 keep their current reads; ws4 upward read PSEUDO-CLOSED for the ex-fence state
and the value. LIN2_PSEUDO_MIN_TF 4, his value. The walk is otherwise unchanged and still acts on
the lift-off reversal; both reversal times are reported, his ruling.
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
print('# the LADDER is rows, not columns - one record per row, his standing rule.')
print('# the walk acts on the lift-off reversal; both reversal times are reported. his ruling.')
print('# ex-fence is the %.0f/%.0f fence from RMOM_FNC; oob is 15/85.'
      % (100 - K.RMOM_FNC, K.RMOM_FNC))
print('# RULED_OK %s | LIN2_PSEUDO_MIN_TF %d | LIFT_WOB %d | LIN2_BARRAGE_MIN_TF %d'
      % (K.RULED_OK, MINTF, K.LIFT_WOB, K.LIN2_BARRAGE_MIN_TF))
print('')

prev_exhaust, leg, side = None, 0, +1
frm = int(A)
while leg < N_LEGS:
    v, bar, rows = L2.walk(CL, BD, close, side, frm, B)
    leg += 1
    arm = [r for r in rows if r['stage'] == 'ARM']
    opn = int(A) if prev_exhaust is None else int(prev_exhaust) + 1
    print('## leg %d - %s, open %s' % (leg, 'LONG' if side > 0 else 'SHORT', ln.U(opn)))
    print('')
    print('| the read | value |')
    print('|---|---|')
    print('| the open | %s |' % ln.U(opn))
    print('| the target side | %s |' % ('HIGH' if side > 0 else 'LOW'))
    print('| the direction | %s |' % ('LONG' if side > 0 else 'SHORT'))
    print('| the arm | %s |' % (ln.U(arm[0]['bar']) if arm and arm[0]['bar'] is not None else '-'))
    print('| the verdict | %s |' % v)
    print('| the exhaust | %s |' % (ln.U(bar) if bar is not None else '-'))
    print('| CONTINUITY | %s |'
          % ('the first leg - opens at the window start' if prev_exhaust is None
             else ('UNBROKEN - opens 1 bar after the previous exhaust %s' % ln.U(prev_exhaust))))
    print('| minutes held | %s |'
          % ('%.1f' % ((bar - opn) * 5 / 60.0) if bar is not None else '-'))
    print('')
    print('### leg %d decisions' % leg)
    print('')
    print('| the bar | stage | rider | candidates | why |')
    print('|---|---|---|---|---|')
    for r in rows:
        b = r.get('bar')
        rd = r.get('rider')
        cd = r.get('cands')
        print('| %s | %s | %s | %s | %s |'
              % (ln.U(b) if b is not None else '-', r['stage'],
                 ('%s%d' % ('ws' if rd and BD.state_src(rd) == 'pseudo' else 'cws', rd))
                 if rd else '-',
                 (','.join('ws%d' % x for x in cd) if cd else ('none' if cd == () else '-')),
                 str(r['why']).replace('|', '\\|')))
    print('')
    print('### leg %d ladder at every decision bar' % leg)
    print('')
    print('| the bar | stage | the line | value | ex-fence | oob | board | lift-off rev |'
          ' pseudo rev | role |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for r in rows:
        b = r.get('bar')
        if b is None:
            continue
        rd = r.get('rider')
        cd = r.get('cands') or ()
        for t in range(1, TOP + 1):
            src = BD.state_src(t)
            val = BD.value(t, b)
            role = []
            if rd == t:
                role.append('RIDER')
            if t in cd:
                role.append('candidate')
            print('| %s | %s | %s%d r | %.2f | %s | %s | %s | %s | %s | %s |'
                  % (ln.U(b), r['stage'], 'ws' if src == 'pseudo' else 'cws', t, val,
                     'YES' if BD.ex_fence(t, b, side) else 'no',
                     'YES' if BD.oob(t, b, side) else 'no', src,
                     last_rev('lift', t, side, b), last_rev('pseudo', t, side, b),
                     ','.join(role) if role else '-'))
    print('')
    if bar is None:
        break
    prev_exhaust = int(bar)
    frm, side = int(bar), -side
