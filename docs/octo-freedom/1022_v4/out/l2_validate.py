"""lineage2 validated against Joe's own 1025 examples. Nothing here decides anything."""
import os, sys
import numpy as np
sys.path.insert(0,'/home/joe/thecodes'); sys.path.insert(0,'/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END','2026-10-05')
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_core_arm as CA
import v4_l2_cadence as CAD, v4_lineage2 as L2
from v4_backstop_trades import prices

R = RS.load((RS.K0, RS.R0, RS.S0))
CL = CA.lines(); CL['M'] = CA.mage_ladder(2)      # cws1Mage, cws2Mage CLOSED
close, _hi, _lo = prices()
U = lambda k: ln.U(int(k))

print('# lineage2 VALIDATION against his 1025 examples. RULED_OK %s' % K.RULED_OK)
print('# L2_MOM_MAXTF %d | L2_LIN_HOP %d | L2_T1_GRACE_S %d | L2_T3_FRAC %s | RMOM_FNC %s'
      % (K.L2_MOM_MAXTF, K.L2_LIN_HOP, K.L2_T1_GRACE_S, K.L2_T3_FRAC, K.RMOM_FNC))
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
v, bar, rows = L2.walk(CL, R, close, +1, ln.K('2026-08-29 07:00:00'), ln.K('2026-08-29 09:00:00'))
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
    v, bar, rows = L2.walk(CL, R, close, sd, ln.K('2026-08-30 18:35:00'), ln.K('2026-08-30 20:00:00'))
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
v, bar, rows = L2.walk(CL, R, close, +1, ln.K('2026-08-29 02:35:05'), ln.K('2026-08-29 06:00:00'))
print('| the bar | stage | why |'); print('|---|---|---|')
for r in rows:
    print('| %s | %s | %s |' % (U(r['bar']) if r['bar'] is not None else '-', r['stage'], r['why']))
print('')
print('verdict %s at %s. his: arm 0300 on ws4r oob, t1 0303, exhaust -> SHORT, then arm 0356 low'
      % (v, U(bar) if bar is not None else '-'))
