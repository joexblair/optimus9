"""THE EX-FENCE LATCH ARM WITH THE ws1b CROSSING HOLD AT 1 BAR AND AT 12 BARS.

Joe 1029: *"let's focus on the ex-fence mech first / place a xwob 12 on ws1b crossing to ib and
tell me if the leg1 0104 exit moves to a later time"*.

THE ONLY ws1b CROSSING-TO-INSIDE IN THE TREE is the lin2-reentry entry test, so the hold he names
is the entry one. Nothing in the exit mechs reads a ws1b crossing: the two cadences that fire on a
crossing read ws1r and already hold it 12 bars, and the counter-side test reads whether ws1b is
beyond the line, not whether it crossed.

So this moves the OPEN, and the question is whether leg 1's exit follows it.

The pseudo-closed line is not built here - the latch arm reads live values at every timeframe, so
nothing would read it.
"""
import os, sys, io, time
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
import v4_l2_proxy as PX, v4_chain as CH, v4_signal as SG, v4_sig_lin2_reentry as L2R
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

K.LIN2_STATE_LIVE = 1
K.LIN2_PSEUDO_MIN_TF = 99
K.LIN2_LATCH_EXFNC_ON = 1

print('# THE EX-FENCE LATCH ARM: THE ws1b CROSSING HOLD AT 1 BAR AND AT 12 BARS')
print('# WINDOW %s .. %s | TAPE %d bars' % (ln.U(A), ln.U(B), len(close)))
print('# the latch hold is %d bars = %d s. drag %.4f%% per round trip.'
      % (K.LIN2_EXFNC_LATCH_WOB, K.LIN2_EXFNC_LATCH_WOB * 5, CH.DRAG_PCT))
print('# every fence test reads the live value. the pseudo-closed line is not in this arm.')
print('')

print('## what the hold does to the signal and the open')
print('')
print('| the hold | the raw ws1b crossing | the signal bar | the open bar | the direction |')
print('|---|---|---|---|---|')
SIGS = {}
for w in (1, 12):
    K.LIN2_CHAIN_OPEN_XWOB = w
    allsig = L2R.signals(B1, MG)
    SIGS[w] = allsig
    near = [g for g in allsig
            if ln.K('2026-08-29 23:50:00') <= g['bar'] <= ln.K('2026-08-29 23:58:00')]
    g = near[0]
    d = SG.direction(int(g['side']))
    print('| %d bar%s = %d s | 2026-08-29 23:53:50 | %s | %s | %s |'
          % (w, '' if w == 1 else 's', w * 5, ln.U(g['bar']), ln.U(SG.fire_bar(g)), d))
print('')

RES = []
for w in (1, 12):
    K.LIN2_CHAIN_OPEN_XWOB = w
    allsig = SIGS[w]
    g = [x for x in allsig
         if ln.K('2026-08-29 23:50:00') <= x['bar'] <= ln.K('2026-08-29 23:58:00')][0]
    d = SG.direction(int(g['side']))
    bd = PX.Board(C, E, MG=MG, MGE=MG, PS=None)
    lg, zero, op = CH.legs(CL, bd, close, phi, plo, A, B, MG=MG, B1=B1,
                           open_at=(SG.fire_bar(g), SG.target_side(d)), resig=allsig)
    RES.append((w, lg, CH.score(lg)))

print('## leg 1 of each, which is what he asked about')
print('')
print('| the hold | the open | dir | the exit | ended by | held min | MAE % | MFE % |'
      ' realised % | drag % | net % |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for w, lg, sc in RES:
    x = lg[0]
    print('| %d bar%s | %s | %s | %s | %s | %.1f | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
          % (w, '' if w == 1 else 's', ln.U(x['opn']), 'LONG' if x['side'] > 0 else 'SHORT',
             ln.U(x['exit']), x['ctype'], x['held_min'], x['mae'], x['mfe'], x['rel'],
             CH.DRAG_PCT, x['rel'] - CH.DRAG_PCT))
print('')
e1, e12 = RES[0][1][0]['exit'], RES[1][1][0]['exit']
print('| the read | value |')
print('|---|---|')
print('| leg 1 exit at the 1-bar hold | %s |' % ln.U(e1))
print('| leg 1 exit at the 12-bar hold | %s |' % ln.U(e12))
print('| does it move | %s |' % ('NO - the same bar' if e1 == e12 else
                                 ('LATER by %.1f min' % ((e12 - e1) * 5 / 60.0) if e12 > e1
                                  else 'EARLIER by %.1f min' % ((e1 - e12) * 5 / 60.0))))
print('')

print('## every leg of each, one row per leg')
print('')
print('| the hold | leg | the open | dir | the exit | ended by | held min | the rider chain |'
      ' MAE % | MFE % | realised % | drag % | net % |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for w, lg, sc in RES:
    for i, x in enumerate(lg, 1):
        ch = []
        for r in x['rows']:
            rd = r.get('rider')
            if rd and (not ch or ch[-1] != rd):
                ch.append(rd)
        chs = ' > '.join('ws%d' % t for t in ch) if ch else '-'
        d = 'LONG' if x['side'] > 0 else 'SHORT'
        if x['exit'] is None:
            print('| %d bars | %d | %s | %s | - | no exhaust | - | %s | - | - | - | - | - |'
                  % (w, i, ln.U(x['opn']), d, chs))
            continue
        print('| %d bars | %d | %s | %s | %s | %s | %.1f | %s | %.4f | %+.4f | %+.4f | %.4f |'
              ' %+.4f |'
              % (w, i, ln.U(x['opn']), d, ln.U(x['exit']), x['ctype'], x['held_min'], chs,
                 x['mae'], x['mfe'], x['rel'], CH.DRAG_PCT, x['rel'] - CH.DRAG_PCT))
    print('| %d bars | TOTAL %d legs | | | | | %.1f | | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
          % (w, sc['n'], sc['held'], sc['mae'], sc['mfe'], sc['rel'], sc['drag'], sc['net']))
print('')
print('| the read | 1-bar hold | 12-bar hold |')
print('|---|---|---|')
for lab, k, f in (('legs', 'n', '%d'), ('summed MAE %', 'mae', '%.4f'),
                  ('summed MFE %', 'mfe', '%+.4f'), ('summed realised %', 'rel', '%+.4f'),
                  ('summed drag %', 'drag', '%.4f'), ('summed net %', 'net', '%+.4f')):
    print(('| %s | ' % lab) + ' | '.join(f % sc[k] for _w, _l, sc in RES) + ' |')
print('| signals on the whole tape | ' + ' | '.join('%d' % len(SIGS[w]) for w, _l, _s in RES)
      + ' |')
print('| seconds to compute | %.1f | |' % (time.time() - T0))
