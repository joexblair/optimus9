"""lineage2 validated against Joe's own 1025 examples. Nothing here decides anything."""
import os, sys
import numpy as np
sys.path.insert(0,'/home/joe/thecodes'); sys.path.insert(0,'/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END','2026-10-05')
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_core_arm as CA
import v4_l2_cadence as CAD, v4_lineage2 as L2, v4_l2_proxy as PX, v4_closed_prev as CP
from v4_backstop_trades import prices

E = RS.load((RS.K0, RS.R0, RS.S0))                # EMERGING ws1r..ws12r - reversal TIMING
C = CP.ladder(E)                                  # the CAUSAL last-closed r ladder
CL = CP.arm_lines(E)                              # cws1b, cws1r..cws12r, cws1Mage, cws2Mage
#   THE CAUSAL MAGE LADDER for the cascade, Joe 1027. Same last-closed rule as the r set.
MGL = {t: CP.line('ws%dMage' % t, t * 60) for t in range(1, 13)}
#   THE EMERGING MAGE LADDER for the barrage's ws1Mage oob->ib cross, 1027.
MGE = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
BD = PX.Board(C, E, MG=MGL, MGE=MGE)                      # the proxy owns the routing
close, _hi, _lo = prices()
U = lambda k: ln.U(int(k))

print('# lineage2 VALIDATION against his 1025 examples. RULED_OK %s' % K.RULED_OK)
print('# L2_MOM_MAXTF %d | L2_LIN_HOP %d | L2_T1_GRACE_S %d | L2_T3_FRAC %s | RMOM_FNC %s'
      % (K.L2_MOM_MAXTF, K.L2_LIN_HOP, K.L2_T1_GRACE_S, K.L2_T3_FRAC, K.RMOM_FNC))
print('# L2_CWS1R_WOB %d | L2_GATE_MODE %s | STATE closed, reversal TIMING emerging,'
      % (K.L2_CWS1R_WOB, K.L2_GATE_MODE))
print('#   t3 GATES on %s - routed by v4_l2_proxy.Board' % BD.gate_mode())
print('')

# ---- t1cadence: his four examples
print('## t1cadence - his examples')
print('')
print('| his example | side | my nearest t1 | gap | why | his verdict |')
print('|---|---|---|---|---|---|')
T1 = [('2026-08-29 04:30:00', -1, 'NOT a cadence'),
      ('2026-08-29 04:36:00', -1, 'a cadence'),
      ('2026-08-29 07:47:00', +1, 'cws1r not yet qualified'),
      ('2026-08-29 07:48:00', +1, 'the cadence fires')]
for ex, sd, hv in T1:
    k = ln.K(ex)
    A, B = k - 2400, k + 2400
    got = CAD.t1(CL, sd, A, B)
    if not got:
        print('| %s | %s | none in +/-2h | - | - | %s |' % (ex, 'HIGH' if sd>0 else 'LOW', hv)); continue
    n = min(got, key=lambda z: abs(z[0]-k))
    print('| %s | %s | %s | %+d s | %s | %s |' % (ex,'HIGH' if sd>0 else 'LOW',U(n[0]),(n[0]-k)*5,n[1],hv))

# ---- t2cadence: his four examples
print('')
print('## t2cadence - his examples')
print('')
print('| his example | side | my nearest t2 | gap | why |')
print('|---|---|---|---|---|')
for ex, sd in (('2026-08-28 14:58:00', +1), ('2026-08-28 17:48:00', +1),
               ('2026-08-29 05:42:00', None), ('2026-08-29 10:13:00', None)):
    k = ln.K(ex)
    for s in ((sd,) if sd else (-1, +1)):
        got = CAD.t2(CL, s, k - 2400, k + 2400)
        if not got:
            print('| %s | %s | none in +/-2h | - | - |' % (ex,'HIGH' if s>0 else 'LOW')); continue
        n = min(got, key=lambda z: abs(z[0]-k))
        print('| %s | %s | %s | %+d s | %s |' % (ex,'HIGH' if s>0 else 'LOW',U(n[0]),(n[0]-k)*5,n[1]))

# ---- his t3cadence walk: 08-29 0704 high
print('')
print('## his 2026-08-29 07:04 HIGH walk - every row')
print('')
v, bar, rows = L2.walk(CL, BD, close, +1, ln.K('2026-08-29 07:00:00'), ln.K('2026-08-29 09:00:00'))
print('| the bar | stage | why |'); print('|---|---|---|')
for r in rows:
    print('| %s | %s | %s |' % (U(r['bar']) if r['bar'] is not None else '-', r['stage'], r['why']))
print('')
print('verdict %s at %s. his: t1 0704, t2 0723, t1 0734, t1 0747, t3 0749 end-of-walk'
      % (v, U(bar) if bar is not None else '-'))

# ---- his t4cadence walk: 08-30 1837 arm
print('')
print('## his 2026-08-30 18:37 walk - every row')
print('')
for sd in (-1, +1):
    v, bar, rows = L2.walk(CL, BD, close, sd, ln.K('2026-08-30 18:35:00'), ln.K('2026-08-30 23:59:55'))
    print('### target-side %s' % ('HIGH' if sd>0 else 'LOW'))
    print('')
    print('| the bar | stage | why |'); print('|---|---|---|')
    for r in rows:
        print('| %s | %s | %s |' % (U(r['bar']) if r['bar'] is not None else '-', r['stage'], r['why']))
    print('')
    print('verdict %s at %s' % (v, U(bar) if bar is not None else '-'))
    print('')
print('his: t1 1837, baton 1842 ws6->ws7, 1844 ws7->ws8, t4 1902 ws8 reverses, ws11 exfence,')
print('     1915 ws11 oob->ib, t3 end-of-walk')

# ---- his basic walk: 08-29 0235 reentry LONG
print('')
print('## his 2026-08-29 02:35 basic walk - LONG, target-side HIGH')
print('')
v, bar, rows = L2.walk(CL, BD, close, +1, ln.K('2026-08-29 02:35:05'), ln.K('2026-08-29 06:00:00'))
print('| the bar | stage | why |'); print('|---|---|---|')
for r in rows:
    print('| %s | %s | %s |' % (U(r['bar']) if r['bar'] is not None else '-', r['stage'], r['why']))
print('')
print('verdict %s at %s. his: arm 0300 on ws4r oob, t1 0303, exhaust -> SHORT, then arm 0356 low'
      % (v, U(bar) if bar is not None else '-'))

# ---- the barrage producer against the banked standalone list
print('')
print('## the barrage producer, 2026-08-30, against out/l2_barrage.md')
print('')
print('# LIN2_BARRAGE_TOL_S %d s | LIN2_BARRAGE_LINES %d | LIN2_BARRAGE_MIN_TF %d | ON %d'
      % (K.LIN2_BARRAGE_TOL_S, K.LIN2_BARRAGE_LINES, K.LIN2_BARRAGE_MIN_TF, K.LIN2_BARRAGE_ON))
print('# the cadence bar is the LAST CONTRIBUTING REVERSAL\'S STAMP - the raw ws1r reversal bar is')
print('#   in the why, so the banked list and this table can be lined up.')
print('')
A0, B0 = ln.K('2026-08-30 00:00:00'), ln.K('2026-08-30 23:59:55')
print('| the target side | the cadence bar | why |')
print('|---|---|---|')
_bar_rows = []
for sd in (-1, +1):
    for b, ty, w in CAD.barrage(BD, sd, A0, B0):
        _bar_rows.append((int(b), sd, w))
for b, sd, w in sorted(_bar_rows):
    print('| %s | %s | %s |' % ('HIGH' if sd > 0 else 'LOW', U(b), w.replace('|', '\\|')))
print('')
print('| the read | value |')
print('|---|---|')
print('| cadences produced | %d |' % len(_bar_rows))
print('| on the LOW target side | %d |' % sum(1 for r in _bar_rows if r[1] < 0))
print('| on the HIGH target side | %d |' % sum(1 for r in _bar_rows if r[1] > 0))
print('| his 02:29 instance | %s |'
      % ('present' if any('02:29:00' in r[2] for r in _bar_rows)
         else 'DROPPED by LIN2_BARRAGE_MIN_TF %d, his ruling' % K.LIN2_BARRAGE_MIN_TF))
print('| the 02:34 instance that replaces it | %s |'
      % ('present' if any('02:34:45' in r[2] for r in _bar_rows) else 'ABSENT'))
