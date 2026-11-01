"""THE t1 CADENCE LIST UNDER HIS 1031 UPDATE, AND THE GRACE-ANCHOR DIFF HE ASKED FOR.

His update: the b line is gcws30b at wob 6, and the r gate is ws1r past the (44, 56) pair on the
target side instead of the side-of-50 test.

His open question, verbatim: *"I'm not sure about this.  my spec build notes didn't allow for it.
give it an on off knob and show the diff"*. LIN2_T1_GRACE_AT is that knob - where the 120 s grace
window starts, at the b line's ib CROSS bar or at its 6-bar CONFIRM bar. Neither is ruled.

Three lists per side: the pre-1031 t1 on ws1b at wob 12, and the new t1 on each grace arm.
"""
import io, os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import v4_knobs as K
import v4_rcfg_sweep as RS
import v4_live_lines as LL
import v4_l2_cadence as CAD
import ln
sys.stderr = _e
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = LL.arm_lines(E)
A = ln.K(os.environ.get('W_WIN_START', '2026-09-03 00:00:00'))
B = ln.K(os.environ.get('W_WIN_END', '2026-09-04 23:59:55'))
print('# THE t1 CADENCE LIST, %s .. %s' % (ln.U(A), ln.U(B)))
print('# the new t1: %s at wob %d bars = %d s | the r gate: ws1r past (%.1f, %.1f) at its stamp'
      % (K.LIN2_T1_B_LINE, K.LIN2_T1_B_WOB, K.LIN2_T1_B_WOB * 5,
         100.0 - K.LIN2_T1_R_FNC, K.LIN2_T1_R_FNC))
print('# the pre-1031 t1: ws1b at wob %d bars = %d s | the r gate: ws1r on the target side of 50'
      % (K.LIN2_CROSS_WOB, K.LIN2_CROSS_WOB * 5))
print()


def run(line, wob, rfnc, gat, side):
    K.LIN2_T1_B_LINE, K.LIN2_T1_B_WOB = line, wob
    K.LIN2_T1_R_FNC, K.LIN2_T1_GRACE_AT = rfnc, gat
    return [(int(b), w) for b, _t, w in CAD.t1(CL, side, A, B)]


OLD, NEW_C, NEW_F = {}, {}, {}
for sd in (-1, +1):
    #   the pre-1031 arm cannot be re-created by knob alone - its r gate was side_of(50), which the
    #   update replaced. R_FNC 50.0 IS that test: past 50 on the target side.
    OLD[sd] = run('ws1b', int(K.LIN2_CROSS_WOB), 50.0, 'cross', sd)
    NEW_C[sd] = run('gcws30b', 6, 56.0, 'cross', sd)
    NEW_F[sd] = run('gcws30b', 6, 56.0, 'confirm', sd)
K.LIN2_T1_B_LINE, K.LIN2_T1_B_WOB = 'gcws30b', 6
K.LIN2_T1_R_FNC, K.LIN2_T1_GRACE_AT = 56.0, 'cross'

print('| the read | low side | high side |')
print('|---|---|---|')
print('| pre-1031 t1 cadences, ws1b wob 12, r past 50 | %d | %d |' % (len(OLD[-1]), len(OLD[1])))
print('| new t1, gcws30b wob 6, r past 56, grace on the CROSS bar | %d | %d |'
      % (len(NEW_C[-1]), len(NEW_C[1])))
print('| new t1, same but grace on the CONFIRM bar | %d | %d |' % (len(NEW_F[-1]), len(NEW_F[1])))
for sd in (-1, +1):
    c = {b for b, _w in NEW_C[sd]}; f = {b for b, _w in NEW_F[sd]}
    print('| the two grace arms differ by, %s side | %d bars only in CROSS, %d only in CONFIRM |'
          ' %s |' % ('low' if sd < 0 else 'high', len(c - f), len(f - c), '') if sd < 0 else
          ('| the two grace arms differ by, high side | | %d only in CROSS, %d only in CONFIRM |'
           % (len(c - f), len(f - c))))
print()
for sd in (-1, +1):
    nm = 'low' if sd < 0 else 'high'
    c = dict(NEW_C[sd]); f = dict(NEW_F[sd])
    only = sorted(set(c) ^ set(f))
    print('## the grace-anchor diff, %s side - %d cadences differ' % (nm, len(only)))
    print()
    if not only:
        print('| the two arms produce an identical cadence list on this side |')
        print('|---|')
        print('| no bar differs |')
        print()
        continue
    print('| the cadence bar | in the CROSS arm? | in the CONFIRM arm? | why |')
    print('|---|---|---|---|')
    for b in only:
        w = c.get(b) or f.get(b)
        print('| %s | %s | %s | %s |'
              % (ln.U(b), 'YES' if b in c else 'no', 'YES' if b in f else 'no',
                 str(w).replace('|', '\\|')))
    print()
for sd in (-1, +1):
    nm = 'low' if sd < 0 else 'high'
    print('## the new t1 cadence list, %s side, grace on the CROSS bar - %d cadences'
          % (nm, len(NEW_C[sd])))
    print()
    print('| the cadence bar | why |')
    print('|---|---|')
    for b, w in NEW_C[sd]:
        print('| %s | %s |' % (ln.U(b), str(w).replace('|', '\\|')))
    print()
