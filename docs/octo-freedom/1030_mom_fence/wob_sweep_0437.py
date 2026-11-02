"""CAN ANY ex-fence latch wob PRODUCE AN EXHAUST AT 2026-09-03 04:37:55?

His 1101: *"I want a ex-fence wob that creates an exhaust ar 0437.  if that can't be done, then we
have to apply this new update now"*.

THE BRANCH ORDER AT A CADENCE, from v4_lineage2.walk, is what decides this:
    1  the matryoshka takeover   - OFF
    2  the candidate scan        - an exhaust needs it EMPTY
    3  HOLD                      - an exhaust needs it to DECLINE
    4  the ladder-top reset      - the rider is ws12, not the top
    5  EXHAUST
HOLD declines only when `baton_oob(rider)` is False AND (no-longer-ex-fence OR reversed).

NOTHING IS APPLIED. The knob is set on the module per arm and restored.
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
    import v4_lineage2 as L2
    import ln
finally:
    sys.stderr = _e
E = RS.load((RS.K0, RS.R0, RS.S0))
MG = LL.mage()
BAR = ln.K('2026-09-03 04:37:55')
SIDE = -1
RIDER = 12
BANKED = int(K.LIN2_EXFNC_LATCH_WOB)
lo, hi = K.fence()
print('# 2026-09-03 04:37:55 | leg 2 SHORT, low side | rider ws%d | the banked wob %d bars = %d s'
      % (RIDER, BANKED, BANKED * 5))
print('# the fence is (%.1f, %.1f) | oob is %.1f/%.1f | the jump cap at a ws%d rider is ws%d'
      % (lo, hi, K.OOB_LO, K.OOB_HI, RIDER, RIDER + K.LIN2_RIDER_JUMP))
print()
print('| the wob | bars = s | the candidates in ws13..ws20 | ws%d latched? | ws%d no-longer-exfence?'
      ' | ws%d reversed? | ws%d oob by value? | HOLD declines? | THE BRANCH |'
      % (RIDER, RIDER, RIDER, RIDER))
print('|---|---|---|---|---|---|---|---|---|')
cap = RIDER + int(K.LIN2_RIDER_JUMP)
for w in (1, 2, 4, 6, 8, 12, 18, 24, 36, 48, 60, 90, 120, 180, 240, 360, 480):
    K.LIN2_EXFNC_LATCH_WOB = w
    BD = PX.Board(E, E, MG=MG, MGE=MG, PS=None)
    got = L2.candidates(BD, SIDE, BAR, RIDER, cap=cap, at_cadence=True)
    lat = bool(BD.baton_ex_fence(RIDER, BAR, SIDE, at_cadence=True))
    no_ex = not lat
    revd = bool(BD.reversed_in(RIDER, SIDE, BAR - 1, BAR))
    oob = bool(BD.baton_oob(RIDER, BAR, SIDE))
    hold = oob or (not no_ex and not revd)
    br = ('BATON -> ws%d' % max(got)) if got else ('HOLD' if hold else 'EXHAUST')
    print('| %d | %d bars = %d s | %s | %s | %s | %s | %s | %s | %s |'
          % (w, w, w * 5, ', '.join('ws%d' % t for t in got) or 'NONE',
             'YES' if lat else 'no', 'YES' if no_ex else 'no', 'YES' if revd else 'no',
             'YES' if oob else 'no', 'no' if hold else 'YES', br))
K.LIN2_EXFNC_LATCH_WOB = BANKED
BD = PX.Board(E, E, MG=MG, MGE=MG, PS=None)
print()
print('| the read | value |'); print('|---|---|')
print('| ws%d r value at the bar | %.2f |' % (RIDER, BD.value(RIDER, BAR)))
print('| the low oob fence | %.1f |' % K.OOB_LO)
print('| so ws%d is oob by value | %s |'
      % (RIDER, 'YES, by %.2f points' % (K.OOB_LO - BD.value(RIDER, BAR))))
print('| LIN2_LATCH_OOB_ON | %d - at 0 the baton oob read IS the line value, not the latch |'
      % K.LIN2_LATCH_OOB_ON)
print('| the wob the knob is restored to | %d |' % K.LIN2_EXFNC_LATCH_WOB)
