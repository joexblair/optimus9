"""HIS 1031 ARM UPDATE, CONDITION 2 ALONE, against his four 09-03 arm times.

WHY ALONE. `arm_race` returns the first bar where ANY of the three qualifies, and conditions 1
(ws4r oob) and 3 (ws2Mage + ws2r oob) fire far more often, so the race winner says nothing about
condition 2. This states every bar condition 2 itself qualifies on.
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
    import v4_l2_cadence as CAD
    import ln
finally:
    sys.stderr = _e
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = LL.arm_lines(E)
A = ln.K('2026-09-03 00:00:00'); B = ln.K('2026-09-03 23:59:55')
g = np.asarray(CL['g30b'], float)
r1 = np.asarray(CL['r'][1], float); r2 = np.asarray(CL['r'][2], float)
r3 = np.asarray(CL['r'][3], float)
aw = max(1, int(K.LIN2_ARM_B_WOB))
alo, ahi = 100.0 - float(K.LIN2_ARM_B_FNC), float(K.LIN2_ARM_B_FNC)
print('# CONDITION 2 ALONE, 2026-09-03 | gcws30b at or beyond (%.1f, %.1f) held %d bars = %d s,'
      ' AND ws1r oob, AND ws2r oob' % (alo, ahi, aw, aw * 5))
print('# oob is %.1f/%.1f | ws3r is %s'
      % (K.OOB_LO, K.OOB_HI, 'IN' if int(K.LIN2_ARM_WS3R_ON) else 'OUT'))
print()
HIS = {-1: ['2026-09-03 22:01:00', '2026-09-03 20:01:00'],
       +1: ['2026-09-03 21:14:00', '2026-09-03 17:17:00']}
for sd in (-1, +1):
    st = np.asarray(CAD.b1_beyond(g, sd, hold=aw, dwell=aw,
                                  mask=K.beyond_mask(g, sd, alo, ahi)), bool)
    o1 = K.oob_mask(r1, sd); o2 = K.oob_mask(r2, sd); o3 = K.oob_mask(r3, sd)
    ok = st & o1 & o2
    runs = []
    k = A
    while k <= B:
        if ok[k]:
            j = k
            while j + 1 <= B and ok[j + 1]:
                j += 1
            runs.append((k, j)); k = j + 1
        else:
            k += 1
    print('## side %s - his arms here: %s'
          % ('low (SHORT)' if sd < 0 else 'high (LONG)',
             ', '.join(ln.U(ln.K(t))[11:16] for t in HIS[sd])))
    print()
    print('| condition 2 qualifies from | to | bars | gcws30b at the first bar | ws1r | ws2r |'
          ' ws3r | near one of his? |')
    print('|---|---|---|---|---|---|---|---|')
    for a0, b0 in runs:
        near = ''
        for t in HIS[sd]:
            d = abs(ln.K(t) - a0) * 5 / 60.0
            if d <= 10:
                near = 'his %s, %.1f min' % (ln.U(ln.K(t))[11:16], d)
        print('| %s | %s | %d | %.2f | %.2f | %.2f | %.2f | %s |'
              % (ln.U(a0), ln.U(b0)[11:], b0 - a0 + 1, g[a0], r1[a0], r2[a0], r3[a0], near or '-'))
    if not runs:
        print('| NONE on the day | - | - | - | - | - | - | - |')
    print()
    print('| the read | value |'); print('|---|---|')
    print('| bars gcws30b is beyond the fence, held | %d |' % int(st[A:B + 1].sum()))
    print('| bars ws1r is oob | %d |' % int(o1[A:B + 1].sum()))
    print('| bars ws2r is oob | %d |' % int(o2[A:B + 1].sum()))
    print('| bars all three hold together | %d |' % int(ok[A:B + 1].sum()))
    print('| bars all three PLUS ws3r | %d |' % int((ok & o3)[A:B + 1].sum()))
    print('| separate episodes | %d |' % len(runs))
    print()
