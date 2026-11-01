"""LINEAGE2's baton chain from his 2026-08-14 06:59 arm, under each of his three pass modes.

HIS 1031 ASK: *"lineage2 / latch enabled / build whatever you need"*, on top of *"there's a open
SHORT with a low side armed event at 08-14 0659. this is our starting point / using the current
"pass on ib", 25/75 fence, max-lineage-TF ws30: print a table showing when each of the baton passes
are made, and when the exhaust prints"*, then the same with 'reversal' and with 'reversal +
1/4 width of the TF'.

THE ARM IS HANDED IN. `walk(arm_at=...)` skips the arm race, his own route for this. He ruled the
timestamp: *"the arm logic has changed - trust my 0659 timestamp"*, so chain_open is not consulted.

THE SIDE IS AN INPUT, not derived: SHORT hunts the low oob, so side -1.

NO END BOUND. B is the last tape bar; the walk returns at its own verdict.

usage: baton_l2_0814.py '<YYYY-MM-DD HH:MM:SS>' <high|low>
"""
import io
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import v4_knobs as K
import v4_rcfg_sweep as RS
import v4_live_lines as LL
import v4_l2_proxy as PX
import v4_lineage2 as L2
import ln
from v4_backstop_trades import prices
sys.stderr = _e

MODES = ('ib', 'reversal', 'reversal+quarter')
ARM = ln.K(sys.argv[1])
SIDE = 1 if sys.argv[2] == 'high' else -1
close, _phi, _plo = prices()
#   THE FORWARD BOUND. Default is the last tape bar - no end bound. W_B_END exists ONLY for the
#   causality truncation test: bounding B at the verdict bar must not change the verdict, and
#   bounding it one bar earlier must reproduce every row before it.
B = ln.K(os.environ['W_B_END']) if os.environ.get('W_B_END') else len(close) - 1
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = LL.arm_lines(E)
MG = LL.mage()
BD = PX.Board(E, E, MG=MG, MGE=MG, PS=None)
assert max(MG) == int(K.L2_MOM_MAXTF), 'the Mage ladder top does not match the knob'
assert int(K.LIN2_LATCH_EXFNC_ON) == 1, 'the per-line ex-fence latch is OFF - he asked for enabled'

print('# LINEAGE2 BATON CHAIN - THE ARM IS HANDED IN AT %s, SIDE %s' % (ln.U(ARM), sys.argv[2]))
print('# TAPE %d bars | B %s, the last tape bar, no end bound | RULED_OK %s'
      % (len(close), ln.U(B), K.RULED_OK))
print()
print('| the setting | value | what it is |')
print('|---|---|---|')
print('| the r fence | %.1f -> (%.1f, %.1f) | his 25/75 |' % (K.RMOM_FNC, 100.0 - K.RMOM_FNC, K.RMOM_FNC))
print('| the ladder top | ws%d | his max-lineage-TF ws30 |' % K.L2_MOM_MAXTF)
print('| the per-line ex-fence latch | ON | his "latch enabled" |')
print('| the latch\'s on-edge hold | %d bars = %d s | an ex-fence cross must hold this |'
      % (K.LIN2_EXFNC_LATCH_WOB, K.LIN2_EXFNC_LATCH_WOB * 5))
print('| what releases the latch | %r | %s |'
      % (K.LIN2_EXFNC_LATCH_REL,
         {'lift': "the latched line's own lift-off, and nothing else - his 1031 spec line",
          'barrage': 'a barrage on that side, or an opposite-side ex-fence cross - the pre-1031'
                     ' arm, renamed from "bank"'}[str(K.LIN2_EXFNC_LATCH_REL)]))
print('| the baton path\'s oob reads at depth | %d | the banked arm |' % K.LIN2_LATCH_OOB_ON)
print('| the hops a baton may make | %d | rider -> candidate, between cadences |' % K.L2_LIN_HOP)
print('| the cross hold on a pass | %d bars = %d s | mode \'ib\' only |'
      % (K.LIN2_CROSS_WOB, K.LIN2_CROSS_WOB * 5))
print('| the reversal hold | %d bars = %d s | modes \'reversal\' and \'reversal+quarter\' |'
      % (K.LIN2_REV_WOB, K.LIN2_REV_WOB * 5))
print('| a quarter of the TF width | %.2f x TF x 12 bars | ws22 -> %d bars = %d s |'
      % (K.LIN2_PASS_QUARTER, K.lin2_quarter_tf(22), K.lin2_quarter_tf(22) * 5))
print('| the ws1b counter-oob exit | %d | 0 = his 1030 "drop the opposing oob side forced exit" |'
      % K.LIN2_COUNTER_OOB_ON)
print('| ws1b\'s oob dwell | %d bars | his value 12 is not banked |' % K.LIN2_B1_OOB_DWELL)
print('| pseudo-closed | %s | 99 = off, the banked arm |' % K.LIN2_PSEUDO_MIN_TF)
print('| the cadence types that may decide | %s | his 1031 filter |' % K.LIN2_CAD_TYPES)
print('| the latch RE-LATCH | %s | his 1031 mech: a lift-off that printed ex-fence, the line never'
      ' reaching in-fence since, and the value back at or beyond that lift-off value |'
      % ('ON, at cadences only' if int(K.LIN2_RELATCH_ON) else 'OFF'))
print('| the rider jump bound | %s | his 1031 rule, from a rider of 0 at the arm |'
      % ('%d TFs' % K.LIN2_RIDER_JUMP if int(K.LIN2_RIDER_JUMP) else 'none'))
print('| the retest gate | %s | it holds the walk\'s start either way; only its cadence is filtered |'
      % ('ON' if int(K.L2_ARM_RETEST) else 'OFF'))
print('| the barrage mech | %s | |' % ('ON' if int(K.LIN2_BARRAGE_ON) else 'OFF'))
print('| the 2-staged cadence latch | %s | |' % ('ON' if int(K.LIN2_CAD_LATCH_ON) else 'OFF'))
print('| t3 | %s | |' % ('ON' if int(K.L2_T3_ON) else 'OFF'))
print('| the ladder-top rider reset | %s | his 1031 trick: at the top rung\'s exhaust the rider'
      ' resets to 0 and re-scans, capped by the jump bound. No limit on repeats |'
      % ('ON' if int(K.LIN2_TOP_RESET_ON) else 'OFF'))
print('| the mage cascade | %s | his 1031 "completely disable the mage cascade" - at 0 neither'
      ' the OPPOSES exhaust nor the MATCHES no-action fires. Its verdict is still PRINTED in the'
      ' cadence rows, as data |'
      % ('DECIDES' if int(K.LIN2_CASCADE_NO_ACTION) else 'DISABLED'))
print('| the stop | not applied - this is a walk, not a scored leg |  |')

RUNS = {}
for m in MODES:
    K.LIN2_PASS = m
    L2._PB.clear()
    v, b, rows = L2.walk(CL, BD, close, SIDE, ARM, B, arm_at=ARM)
    RUNS[m] = (v, b, rows)

for m in MODES:
    v, b, rows = RUNS[m]
    K.LIN2_PASS = m
    print()
    print('## MODE %r - the baton passes and the exhaust' % m)
    print()
    print('| the bar | the stage | from rider | to rider | the candidates offered | why |')
    print('|---|---|---|---|---|---|')
    n = 0
    for r in rows:
        if r['stage'] not in ('BATON', 'EXHAUST', 'NO PASS', 'ARM', 'RIDER', 'NO VERDICT',
                              'CADENCE', 'CASCADE GATED', 'NO ACTION', 'NO RIDER',
                              'TOP RESET', 'TOP RESET EMPTY', 'HOLD'):
            continue
        if r['stage'] == 'BATON':
            n += 1
        cd = r.get('cands')
        cc = ('-' if cd is None else
              ('none offered' if cd == () else
               ', '.join('ws%d %.2f' % (t, BD.value(int(t), int(r['bar']))) for t in cd)))
        print('| %s | %s | %s | %s | %s | %s |'
              % (ln.U(int(r['bar'])) if r.get('bar') is not None else '-',
                 r['stage'],
                 'ws%d' % r['rider'] if r.get('rider') else '-',
                 'ws%d' % r['to'] if r.get('to') else '-',
                 cc,
                 str(r['why']).replace('|', '\\|')))
    print()
    print('| the read | value |')
    print('|---|---|')
    print('| the verdict | %s |' % v)
    print('| the verdict bar | %s |' % (ln.U(b) if b else '-'))
    print('| baton passes made | %d |' % n)
    print('| minutes from the arm to the verdict | %s |'
          % ('-' if b is None else '%.1f' % ((b - ARM) * 5 / 60.0)))
    ch = []
    for r in rows:
        rd = r.get('rider')
        if rd and (not ch or ch[-1] != rd):
            ch.append(rd)
    print('| the rider chain | %s |' % (' > '.join('ws%d' % t for t in ch) if ch else '-'))

for m in MODES:
    v, b, rows = RUNS[m]
    K.LIN2_PASS = m
    print()
    print('## MODE %r - every row of the walk' % m)
    print()
    print('| the bar | the stage | rider | why |')
    print('|---|---|---|---|')
    for r in rows:
        print('| %s | %s | %s | %s |'
              % (ln.U(int(r['bar'])) if r.get('bar') is not None else '-',
                 r['stage'], 'ws%d' % r['rider'] if r.get('rider') else '-',
                 str(r['why']).replace('|', '\\|')))
