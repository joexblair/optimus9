"""HIS 1031 ARM LIST - the arm is the FIRST firing at or after its own open, on the trade's side.

His list, opens and arms per row:
    09-03 1701 L -> 1716 | 1930 S -> 2201 | 2324 L -> 2339 | 2343 S -> 09-04 0007
    09-04 0009 L -> 0036

Two readings are printed per row and NEITHER is fitted to him:
  the RACE      - arm_race as the walk calls it, whichever of the three conditions fires first
  the gcws30b ARM ALONE - his 1031 update's own three terms, with the other two conditions removed
"""
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
B = ln.K('2026-09-04 12:00:00')
aw = max(1, int(K.LIN2_ARM_B_WOB))
alo, ahi = 100.0 - float(K.LIN2_ARM_B_FNC), float(K.LIN2_ARM_B_FNC)
g = np.asarray(CL['g30b'], float)
r1 = np.asarray(CL['r'][1], float); r2 = np.asarray(CL['r'][2], float)
ST = {sd: np.asarray(CAD.b1_beyond(g, sd, hold=aw, dwell=aw,
                                   mask=K.beyond_mask(g, sd, alo, ahi)), bool) for sd in (-1, 1)}
#   HIS 1031 REVISION: *"(ws1r or ws2r) + gcws30b"* - the r lines are an OR.
OK = {sd: ST[sd] & (K.oob_mask(r1, sd) | K.oob_mask(r2, sd)) for sd in (-1, 1)}
#   1101 ANNOTATION - THE 0437 LEG JOINED THE LIST. His 1101: *"this is the reason for me pushing
#   to build an arm on a divergence signal - 0437 needs to exhaust"*. The mech he is specifying can
#   only act where a trade has NO arm, so the question is whether 2026-09-03 04:37:55 sits inside
#   this leg's open-to-arm gap. The open comes from the chain run chain_0903_armcheck.md - leg 2,
#   2026-09-03 01:36:05 SHORT, exited 04:56:55 by the 1.1% stop. THE THIRD COLUMN IS NOT AN ARM HE
#   GAVE: it is the 04:37:55 bar, carried so the gap column measures against it.
ROWS = [('2026-09-03 01:36:05', -1, '2026-09-03 04:37:55'),
        ('2026-09-03 17:01:00', +1, '2026-09-03 17:16:00'),
        ('2026-09-03 19:30:00', -1, '2026-09-03 22:01:00'),
        ('2026-09-03 23:24:00', +1, '2026-09-03 23:39:00'),
        ('2026-09-03 23:43:00', -1, '2026-09-04 00:07:00'),
        ('2026-09-04 00:09:00', +1, '2026-09-04 00:36:00')]
print('# HIS ARM LIST - the first firing at or after each open, on the trade side')
print('# gcws30b at or beyond (%.1f, %.1f) held %d bars = %d s, AND (ws1r oob OR ws2r oob)'
      % (alo, ahi, aw, aw * 5))
print('# oob %.1f/%.1f | ws3r %s | the ruled check passes: %s'
      % (K.OOB_LO, K.OOB_HI, 'IN' if int(K.LIN2_ARM_WS3R_ON) else 'OUT', K.RULED_OK))
print()
print('| his open | side | HIS arm | the gcws30b arm alone fires | the gap to his |'
      ' gcws30b there | ws1r | ws2r |')
print('|---|---|---|---|---|---|---|---|')
for op, sd, hisarm in ROWS:
    o, h = ln.K(op), ln.K(hisarm)
    nz = np.flatnonzero(OK[sd][o:B + 1])
    if not len(nz):
        print('| %s | %s | %s | NONE to %s | - | - | - | - |'
              % (op, 'LONG' if sd > 0 else 'SHORT', hisarm, ln.U(B)))
        continue
    k = o + int(nz[0])
    print('| %s | %s | %s | %s | %+.1f min | %.2f | %.2f | %.2f |'
          % (op, 'LONG' if sd > 0 else 'SHORT', hisarm, ln.U(k), (k - h) * 5 / 60.0,
             g[k], r1[k], r2[k]))
print()
print('| his open | side | HIS arm | the RACE fires | which condition | the gap to his | why |')
print('|---|---|---|---|---|---|---|')
for op, sd, hisarm in ROWS:
    o, h = ln.K(op), ln.K(hisarm)
    arm, which, why = L2.arm_race(CL, BD, sd, o, B)
    if arm is None:
        print('| %s | %s | %s | NONE | - | - | %s |'
              % (op, 'LONG' if sd > 0 else 'SHORT', hisarm, str(why).replace('|', '\\|')))
        continue
    print('| %s | %s | %s | %s | %s | %+.1f min | %s |'
          % (op, 'LONG' if sd > 0 else 'SHORT', hisarm, ln.U(int(arm)), which,
             (int(arm) - h) * 5 / 60.0, str(why).replace('|', '\\|')))
