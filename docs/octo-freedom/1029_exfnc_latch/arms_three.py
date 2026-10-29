"""ONE OPEN, THREE WAYS OF READING THE VALUES, AND WHAT EACH DOES TO EACH LEG'S NET %.

Joe 1029: *"there is only one OPEN, and it's 2353. the other legs you've described have no value to
us / when I asked for the comparative trades, I was refering to the different ways of collecting
values and their impacts on the leg's net% (emreging +wob, psuedo-closed, and the impact of the new
latch exfence mech)"*.

THE OPEN IS FIXED for all three: 2026-08-29 23:53:55 SHORT - the router's fire bar off the
lin2-reentry signal at 23:53:50.

THE THREE ARMS, and nothing else moves between them:

  1  live values            every fence test reads the line's value at that bar. The reversal wob
                            is LIFT_WOB, 8 bars = 40 s, its banked value.
  2  pseudo-closed          ws1..ws3 keep the live value; ws4 upward read the pseudo-closed line.
                            LIN2_PSEUDO_MIN_TF 4, his value.
  3  the ex-fence latch     live values, plus the per-line ex-fence latch on the baton tests.
                            LIN2_EXFNC_LATCH_WOB 4 bars = 20 s, his value.

THE LAST-COMPLETED-BAR READ IS NOT AN ARM. His 1029 ruling drops it. Every number this session
produced before that ruling was taken on it and none of them carries forward.

ONE BOARD PER ARM, built once and reused across the legs of that arm.

THE 1.1% STOP IS ON, his 1029 ask: *"apply the mae1.1 cap to the 3 options"*. When the adverse
excursion reaches LIN2_MAE_CAP the leg ends there with a realised of -1.1, the chain goes FLAT, and
the way back in is the next lin2-reentry signal - his own first line for that mech. The 1028
take-profit sweep already walked the cap this way, and intra-bar ties go to the adverse side.

BOTH STOP ARMS ARE RUN so the cap's own cost is visible beside each read.
"""
import os, sys, io, time
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
T0 = time.time()

A, B = ln.K('2026-08-30 00:00:00'), ln.K('2026-08-30 23:59:55')
close, phi, plo = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = CP.arm_lines(E)
C = CP.ladder(E)
B1 = np.asarray(ln.line('ws1b'), float)
MG = {t: np.asarray(ln.line('ws%dMage' % t), float) for t in range(1, 13)}

#   THE OPEN IS HIS, NAMED: *"there is only one OPEN, and it's 2353"*. Taking "the last signal
#   at or before the window start" picked 23:56:00 instead - the same backward selection I have now
#   got wrong three times. The signal is named, not searched for.
SIG = [s for s in L2R.signals(B1, MG) if s['bar'] == ln.K('2026-08-29 23:53:50')]
assert len(SIG) == 1, 'the 2026-08-29 23:53:50 lin2-reentry signal is not in the list'
OPEN_BAR = SG.fire_bar(SIG[0])
#   THE WALK'S SIDE IS THE TRADE'S TARGET SIDE, NOT THE SIGNAL'S SIDE, and the layer owns both
#   conversions. A signal on the HIGH side opens a SHORT, and a SHORT hunts the LOW oob. Passing
#   the signal's side straight into the walk inverted every leg of the previous run: leg 1 printed
#   LONG when the trade is a SHORT.
OPEN_DIR = SG.direction(SIG[0]['side'])
OPEN_SIDE = SG.target_side(OPEN_DIR)
assert OPEN_DIR == 'SHORT' and OPEN_SIDE == -1, \
    'the 23:53:50 HIGH signal must open a SHORT whose target side is LOW, got %s / %d' % (
        OPEN_DIR, OPEN_SIDE)
TOP = max(int(K.L2_MOM_MAXTF), int(K.LIN2_BARRAGE_MAX_TF))
IDX = np.arange(min(OPEN_BAR, A), B + 1)
PS = {}
for t in range(int(K.LIN2_PSEUDO_MIN_TF), TOP + 1):
    PS[t] = np.full(len(close), np.nan)
    PS[t][IDX] = PC.series(close, t, IDX)

ARMS = [
    ('1 live values', dict(LIN2_STATE_LIVE=1, LIN2_PSEUDO_MIN_TF=99, LIN2_LATCH_EXFNC_ON=0)),
    ('2 pseudo-closed ws4 up', dict(LIN2_STATE_LIVE=1, LIN2_PSEUDO_MIN_TF=4,
                                    LIN2_LATCH_EXFNC_ON=0)),
    ('3 the ex-fence latch', dict(LIN2_STATE_LIVE=1, LIN2_PSEUDO_MIN_TF=99,
                                  LIN2_LATCH_EXFNC_ON=1)),
]

print('# ONE OPEN, THREE WAYS OF READING THE VALUES')
print('# the open is %s %s - the router fire bar off the lin2-reentry signal %s, which came in'
      ' from the %s side' % (ln.U(OPEN_BAR), OPEN_DIR, ln.U(SIG[0]['bar']),
                             'HIGH' if SIG[0]['side'] > 0 else 'LOW'))
print('# WINDOW %s .. %s | TAPE %d bars' % (ln.U(A), ln.U(B), len(close)))
print('# drag %.4f%% per round trip, its own column and its own total.' % CH.DRAG_PCT)
print('# the reversal wob is LIFT_WOB %d bars = %d s. the latch wob is LIN2_EXFNC_LATCH_WOB'
      ' %d bars = %d s.' % (K.LIFT_WOB, K.LIFT_WOB * 5, K.LIN2_EXFNC_LATCH_WOB,
                            K.LIN2_EXFNC_LATCH_WOB * 5))
print('# THE LAST-COMPLETED-BAR READ IS NOT AN ARM - his 1029 ruling drops it.')
print('# THE STOP: when the adverse excursion reaches %.2f%% the leg ends there at -%.2f%%, the'
      ' chain goes FLAT,' % (float(K.LIN2_MAE_CAP), float(K.LIN2_MAE_CAP)))
print('#   and the next open is the next lin2-reentry signal. Intra-bar ties go to the adverse'
      ' side.')
print('')

ALLSIG = L2R.signals(B1, MG)
CAP = float(K.LIN2_MAE_CAP)
RES = []
for cap, ctag in ((None, 'no stop'), (CAP, 'stop at %.2f%%' % CAP)):
    for name, kn in ARMS:
        for k, v in kn.items():
            setattr(K, k, v)
        bd = PX.Board(C, E, MG=MG, MGE=MG, PS=PS)
        lg, zero, op = CH.legs(CL, bd, close, phi, plo, A, B, MG=MG, B1=B1,
                               open_at=(OPEN_BAR, OPEN_SIDE), mae_cap=cap, resig=ALLSIG)
        RES.append(('%s, %s' % (name, ctag), kn, lg, zero, CH.score(lg), bd))

print('## every leg of every arm, one row per leg')
print('')
print('| the arm | leg | the open | dir | the exit | ended by | held min |'
      ' the rider chain | MAE % | MFE % | realised % | drag % | net % |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for name, kn, lg, zero, sc, bd in RES:
    for i, x in enumerate(lg, 1):
        d = 'LONG' if x['side'] > 0 else 'SHORT'
        ch = []
        for r in x['rows']:
            rd = r.get('rider')
            if rd and (not ch or ch[-1] != rd):
                ch.append(rd)
        chs = ' > '.join('ws%d' % t for t in ch) if ch else '-'
        if x['exit'] is None:
            print('| %s | %d | %s | %s | - | no exhaust | - | %s | - | - | - | - | - |'
                  % (name, i, ln.U(x['opn']), d, chs))
            continue
        print('| %s | %d | %s | %s | %s | %s | %.1f | %s | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
              % (name, i, ln.U(x['opn']), d, ln.U(x['exit']), x['ctype'], x['held_min'], chs,
                 x['mae'], x['mfe'], x['rel'], CH.DRAG_PCT, x['rel'] - CH.DRAG_PCT))
    print('| %s | TOTAL %d legs | | | | | %.1f | | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
          % (name, sc['n'], sc['held'], sc['mae'], sc['mfe'], sc['rel'], sc['drag'], sc['net']))
print('')

print('## the three arms, totals')
print('')
print('| the read | ' + ' | '.join(n for n, _k, _l, _z, _c, _b in RES) + ' |')
print('|---|' + '---|' * len(RES))
print('| the open bar | ' + ' | '.join(ln.U(OPEN_BAR) for _ in RES) + ' |')
print('| the direction | ' + ' | '.join(OPEN_DIR for _ in RES) + ' |')
for lab, k, f in (('legs', 'n', '%d'), ('unresolved legs', 'unres', '%d'),
                  ('barrage exits', 'barr', '%d'), ('legs net-positive after drag', 'win', '%d'),
                  ('stops', 'stops', '%d'),
                  ('summed held min', 'held', '%.1f'), ('summed MAE %', 'mae', '%.4f'),
                  ('summed MFE %', 'mfe', '%+.4f'), ('summed realised %', 'rel', '%+.4f'),
                  ('summed drag %', 'drag', '%.4f'), ('summed net %', 'net', '%+.4f')):
    print(('| %s | ' % lab) + ' | '.join(f % sc[k] for _n, _k, _l, _z, sc, _b in RES) + ' |')
b0 = RES[0][4]['net']
print('| net % against arm 1 | ' + ' | '.join('%+.4f' % (sc['net'] - b0)
                                              for _n, _k, _l, _z, sc, _b in RES) + ' |')
print('| MFE collected | '
      + ' | '.join(('%.1f%%' % (sc['rel'] / sc['mfe'] * 100.0)) if sc['mfe'] > 0 else 'n/a'
                   for _n, _k, _l, _z, sc, _b in RES) + ' |')
print('| net % per leg | ' + ' | '.join('%+.4f' % (sc['net'] / sc['n'] if sc['n'] else 0.0)
                                        for _n, _k, _l, _z, sc, _b in RES) + ' |')
print('')
print('| the read | value |')
print('|---|---|')
print('| legs with no bars, exit before open | %s |'
      % ', '.join('%s %d' % (n.split()[0], len(z)) for n, _k, _l, z, _c, _b in RES))
print('| seconds to compute | %.1f |' % (time.time() - T0))
