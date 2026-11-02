"""HIS 1031 t1 AND ARM UPDATES, against his own worked examples. NOTHING IS FITTED TO THEM."""
import io, os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
#   THE SWALLOW COVERS THE NOISY IMPORTS ONLY, and `finally` restores stderr whatever
#   happens. Without it a refusal from v4_knobs.check() - an off-ruled run with no
#   W_V4_EXPERIMENT=1 - goes into the StringIO and the process exits 1 with NOTHING on
#   either stream. That cost a diagnosis on 1101.
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_rcfg_sweep as RS
    import v4_live_lines as LL
    import v4_l2_proxy as PX
    import v4_l2_cadence as CAD
    import v4_lineage2 as L2
    import ln
finally:
    sys.stderr = _e
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = LL.arm_lines(E); MG = LL.mage()
BD = PX.Board(E, E, MG=MG, MGE=MG, PS=None)
rlo, rhi = 100.0 - float(K.LIN2_T1_R_FNC), float(K.LIN2_T1_R_FNC)
alo, ahi = 100.0 - float(K.LIN2_ARM_B_FNC), float(K.LIN2_ARM_B_FNC)
print('# HIS 1031 UPDATES | RULED_OK %s' % K.RULED_OK)
print()
print('| the setting | value | whose |')
print('|---|---|---|')
print('| t1 b line | %s | his |' % K.LIN2_T1_B_LINE)
print('| t1 b cross hold | %d bars = %d s | his |' % (K.LIN2_T1_B_WOB, K.LIN2_T1_B_WOB * 5))
print('| t1 r gate fence | (%.1f, %.1f) | his knob 56 |' % (rlo, rhi))
print('| t1 r line | ws1r | his |')
print('| t1 grace window starts on | the %s bar | MINE, he asked for the knob and the diff |'
      % K.LIN2_T1_GRACE_AT)
print('| arm b line | %s | his |' % K.LIN2_ARM_B_LINE)
print('| arm b fence | (%.1f, %.1f), at or beyond | his |' % (alo, ahi))
print('| arm b wob, both edges | %d bars = %d s | his |' % (K.LIN2_ARM_B_WOB, K.LIN2_ARM_B_WOB * 5))
print('| arm ws3r | %s | his uncertainty, off |' % ('ON' if int(K.LIN2_ARM_WS3R_ON) else 'OFF'))
print()
print('## HIS t1 r-GATE EXAMPLES - 09-03 1152 must FAIL, 1233 must PASS')
print()
r1 = np.asarray(CL['r'][1], float)
print('| his example | the bar | ws1r there | the fence it must clear | qualifies? | he said |')
print('|---|---|---|---|---|---|')
for t, want in (('2026-09-03 11:52:00', 'no'), ('2026-09-03 12:33:00', 'YES')):
    k = ln.K(t); v = float(r1[k])
    hi_ok, lo_ok = v >= rhi, v <= rlo
    got = 'YES on the high side' if hi_ok else ('YES on the low side' if lo_ok else 'no')
    print('| r %s | %s | %.2f | >= %.1f high, <= %.1f low | %s | %s |'
          % ('50.3' if want == 'no' else '59', t, v, rhi, rlo, got, want))
print()
print('## HIS FOUR 09-03 ARM TIMES - the side is handed in, as he ruled')
print()
HIS = [('2026-09-03 22:01:00', -1, 'S 2201'), ('2026-09-03 21:14:00', +1, 'L 2114'),
       ('2026-09-03 20:01:00', -1, 'S 2001'), ('2026-09-03 17:17:00', +1, 'L 1717')]
A0 = ln.K('2026-09-03 00:00:00'); B0 = ln.K('2026-09-03 23:59:55')
print('| his arm | the side | the nearest arm_race firing at or before it | which condition | the gap | why |')
print('|---|---|---|---|---|---|')
for t, sd, lbl in sorted(HIS):
    tgt = ln.K(t)
    best = None
    k = A0
    while k <= tgt:
        arm, which, why = L2.arm_race(CL, BD, sd, k, B0)
        if arm is None or int(arm) > tgt:
            break
        best = (int(arm), which, why)
        k = int(arm) + 1
    if best is None:
        print('| %s | %s | NONE on the day at or before it | - | - | - |'
              % (lbl, 'low' if sd < 0 else 'high'))
        continue
    b, wh, wy = best
    print('| %s | %s | %s | %s | %.1f min | %s |'
          % (lbl, 'low' if sd < 0 else 'high', ln.U(b), wh, (tgt - b) * 5 / 60.0,
             str(wy).replace('|', '\\|')))
