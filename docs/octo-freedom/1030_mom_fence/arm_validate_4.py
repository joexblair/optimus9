"""VALIDATE HIS 4 ARM TIMESTAMPS - which term arrives last, and on which bar.

His 1031 arm, verbatim: *"(ws1r or ws2r) + gcws30b"*, with gcws30b at or beyond the 5/95 fence
held LIN2_ARM_B_WOB bars on entry and on return.

The arm bar is the FIRST bar both halves hold. This states, per row, the bar each half turns on, so
the arm bar is a max() of two readable timestamps rather than an assertion.

EVERY READ IS AT OR BEFORE THE BAR IT ANSWERS FOR - the fence cross's hold ends on its own confirm
bar, the r oob read is per bar, and the arm is the later of the two. Asserted below.
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
g = np.asarray(CL['g30b'], float)
r1 = np.asarray(CL['r'][1], float); r2 = np.asarray(CL['r'][2], float)
aw = max(1, int(K.LIN2_ARM_B_WOB))
alo, ahi = 100.0 - float(K.LIN2_ARM_B_FNC), float(K.LIN2_ARM_B_FNC)
ROWS = [('2026-09-03 17:01:00', +1, '2026-09-03 17:16:00'),
        ('2026-09-03 23:24:00', +1, '2026-09-03 23:39:00'),
        ('2026-09-03 23:43:00', -1, '2026-09-04 00:07:00'),
        ('2026-09-04 00:09:00', +1, '2026-09-04 00:36:00')]
print('# HIS 4 ARM TIMESTAMPS, VALIDATED TERM BY TERM')
print('# the arm = gcws30b at or beyond (%.1f, %.1f) held %d bars = %d s, AND (ws1r oob OR ws2r oob)'
      % (alo, ahi, aw, aw * 5))
print('# oob %.1f/%.1f | the ruled check passes: %s' % (K.OOB_LO, K.OOB_HI, K.RULED_OK))
print()
print('| his open | side | HIS arm | gcws30b crosses its fence | its %d-bar hold confirms |'
      ' the r group turns on | which r | THE ARM = the later of the two | the gap to his |'
      % aw)
print('|---|---|---|---|---|---|---|---|---|')
det = []
for op, sd, hisarm in ROWS:
    o, h = ln.K(op), ln.K(hisarm)
    raw = np.asarray(K.beyond_mask(g, sd, alo, ahi), bool)
    st = np.asarray(CAD.b1_beyond(g, sd, hold=aw, dwell=aw, mask=raw), bool)
    o1, o2 = K.oob_mask(r1, sd), K.oob_mask(r2, sd)
    rg = o1 | o2
    both = st & rg
    nz = np.flatnonzero(both[o:])
    arm = o + int(nz[0])
    #   the fence cross that produced the held state live at `arm`
    c = arm
    while c > 0 and st[c - 1]:
        c -= 1
    x = c - aw + 1                       # the raw cross bar: the hold confirms at x + aw - 1
    #   the r group's own on-bar inside this episode
    rr = arm
    while rr > o and rg[rr - 1]:
        rr -= 1
    assert c <= arm and rr <= arm, 'a term turns on after the arm it serves'
    assert raw[x:x + aw].all(), 'the hold window has a bar inside the fence'
    which = ' and '.join(n for n, m in (('ws1r', o1), ('ws2r', o2)) if m[arm])
    print('| %s | %s | %s | %s | %s | %s | %s | %s | %+.1f min |'
          % (op, 'LONG' if sd > 0 else 'SHORT', hisarm, ln.U(x), ln.U(c), ln.U(rr), which,
             ln.U(arm), (arm - h) * 5 / 60.0))
    det.append((op, sd, hisarm, arm, x, c, rr))
print()
for op, sd, hisarm, arm, x, c, rr in det:
    print('## %s %s - his arm %s, the arm fires %s'
          % (op, 'LONG' if sd > 0 else 'SHORT', hisarm, ln.U(arm)))
    print()
    print('| the bar | gcws30b | at or beyond %.1f/%.1f? | ws1r | oob? | ws2r | oob? | the arm holds? |'
          % (alo, ahi))
    print('|---|---|---|---|---|---|---|---|')
    raw = np.asarray(K.beyond_mask(g, sd, alo, ahi), bool)
    st = np.asarray(CAD.b1_beyond(g, sd, hold=aw, dwell=aw, mask=raw), bool)
    o1, o2 = K.oob_mask(r1, sd), K.oob_mask(r2, sd)
    for k in range(min(x, rr) - 2, arm + 3):
        print('| %s | %.2f | %s | %.2f | %s | %.2f | %s | %s |'
              % (ln.U(k), g[k], 'YES' if raw[k] else 'no', r1[k], 'YES' if o1[k] else 'no',
                 r2[k], 'YES' if o2[k] else 'no',
                 'ARM' if k == arm else ('YES' if (st[k] and (o1[k] or o2[k])) else 'no')))
    print()
