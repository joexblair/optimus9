"""LINEAGE2's baton chain from his 2026-08-14 06:59 arm, under each of his three pass modes.

HIS 1031 ASK: *"lineage2 / latch enabled / build whatever you need"*, on top of *"there's a open
SHORT with a low side armed event at 08-14 0659. this is our starting point / using the current
"pass on ib", 25/75 fence, max-lineage-TF ws30: print a table showing when each of the baton passes
are made, and when the exhaust prints"*, then the same with 'reversal' and with 'reversal +
1/4 width of the TF'.

THE ARM IS HANDED IN. `walk(arm_at=...)` skips the arm race, his own route for this. He ruled the
timestamp: *"the arm logic has changed - trust my 0659 timestamp"*, so chain_open is not consulted.

1101 ANNOTATION - THIS FILE SERVES ANY HANDED-IN ARM, not only 08-14 06:59. The arm bar and the
target side are both argv, so his 1101 rule *"you now only use one script and annotate changes,
instead of building a new script for every update"* is met by annotating here. Arms walked so far:

    2026-08-14 06:59:00  low   his original ask, EXHAUST 14:07:20
    2026-09-03 22:01:15  low   the SHORT whose cadence at 23:24 he asked about on 1101: does the
                               walk print EXHAUST there on its own, with the divergence OFF?
                               22:01:15 is the arm race's own bar, not his 2201 estimate.
    2026-08-25 06:58:00  low   his 1109 ask: the highest ws{TF}r that is ex-fence AND towards at
                               that bar is ws13r 19.13, and he asked how far up the ladder the
                               baton goes from it on ib - emerging and closed_prev - and on
                               lift-off reversal. THE WALK DOES NOT TAKE A HANDED-IN RIDER: the
                               arm bar is handed in and `rider_at` picks the rider itself, which
                               is ws12 r 10.97 at the first t1 cadence 07:01:25, one rung under
                               his ws13 read at 06:58 and 3 min 25 s later. Results:
                                 emerging + ib        EXHAUST 11:06:25, 6 passes, top rung ws30
                                 emerging + reversal  EXHAUST 11:06:25, 8 passes, top rung ws30
                                 closed_prev + ib     EXHAUST 11:48:25, 5 passes, top rung ws28
                                 closed_prev + rev    identical to emerging + reversal, as it must
                                                      be - `_pass_bars` does not read the ib cross
                                                      in reversal mode, so LIN2_CP_IB cannot move it

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
    from v4_backstop_trades import prices
finally:
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
#   1101: THE LATCH ASSERT IS GONE. It demanded the latch ON, from his 1031 *"latch
#   enabled"*. His 1101 word retires it: *"disable the latch.  I introduced it get around
#   emerging"*, and the chart-matched ex-fence read is what it was standing in for. The
#   ruled bank now carries 0, so v4_knobs refuses an ON run without W_V4_EXPERIMENT=1 -
#   which is a stronger check than this line was.
assert str(K.LIN2_CP_EXFNC) in ('emerging', 'closed_prev'), \
    'LIN2_CP_EXFNC %r is not an arm' % (K.LIN2_CP_EXFNC,)

print('# LINEAGE2 BATON CHAIN - THE ARM IS HANDED IN AT %s, SIDE %s' % (ln.U(ARM), sys.argv[2]))
print('# TAPE %d bars | B %s, the last tape bar, no end bound | RULED_OK %s'
      % (len(close), ln.U(B), K.RULED_OK))
print()
print('| the setting | value | what it is |')
print('|---|---|---|')
print('| the r fence | %.1f -> (%.1f, %.1f) | his 25/75 |' % (K.RMOM_FNC, 100.0 - K.RMOM_FNC, K.RMOM_FNC))
print('| the ladder top | ws%d | his max-lineage-TF ws30 |' % K.L2_MOM_MAXTF)
print('| the per-line ex-fence latch | %s | his 1101 "disable the latch" |'
      % ('ON' if int(K.LIN2_LATCH_EXFNC_ON) else 'OFF'))
print('| the ex-fence read\'s source | %s | his 1101 "closed_prev only for exiting fences" |'
      % K.LIN2_CP_EXFNC)
print('| the oob read\'s source | %s | he put oob in neither category - both arms built |'
      % K.LIN2_CP_OOB)
print('| the oob->ib cross\'s source | %s | his gut, with the other arm built |' % K.LIN2_CP_IB)
print('| the TF floor for the chart-matched read | ws%d | his "ws1{any} and gcws1{any} stay on'
      ' emerging" |' % K.LIN2_CP_MIN_TF)
print('| reversal detection | emerging, always | his "keeping the lift-off on emerging allows us'
      ' to capture those much needed 0445 reversal timestamps" |')
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

#   ===========================================================================================
#   1101 ANNOTATION - THE RESET-SCAN READ. His 1101 spec: *"instead of "send a rev-trade to
#   router", treat a divergence (bullish for low, bearish for high) signal as a signal to 1) build
#   an arm event if the trade has not already printed an arm, and 2) reset the TF rider, using the
#   established reset rider TF mech"*.
#
#   NOTHING IS BUILT HERE. This prints, at each bar handed in, the two reads his mech would need:
#   the divergence state under both anchor arms, and what the ESTABLISHED reset would return - the
#   same call the ladder-top reset makes at v4_lineage2.py:930, `candidates(BD, side, bar, 0,
#   cap=LIN2_RIDER_JUMP, at_cadence=True)`. The walk's branches are untouched.
#
#   W_RESET_SCAN is a comma-separated bar list. The bars are HIS, not a window of mine.
#   ===========================================================================================
if os.environ.get('W_RESET_SCAN'):
    _e3 = sys.stderr; sys.stderr = io.StringIO()
    try:
        from optimus9.analysis.jig import mage_cascade_bar, MC_GAP
    finally:
        sys.stderr = _e3
    MG1 = np.asarray(LL.mage(1)[1], float)
    JMP = int(K.LIN2_RIDER_JUMP) or None
    print()
    print('## the reset-scan read at the bars handed in, side %s' % sys.argv[2])
    print()
    print('| the bar | div state, cadence anchor | div verdict | the extremum bar | div state,'
          ' extremum anchor | div verdict | the rider-0 re-scan, capped at ws%s | it would take |'
          % (JMP if JMP else 'none'))
    print('|---|---|---|---|---|---|---|---|')
    for t in [x.strip() for x in os.environ['W_RESET_SCAN'].split(',') if x.strip()]:
        k = ln.K(t)
        cs = L2.div_state(CL, close, SIDE, k)
        cv = L2.div_verdict(CL, close, SIDE, k)
        pk = mage_cascade_bar(MG1, int(k), int(SIDE), mode='extrema', gap=MC_GAP)
        eb = int(k) if pk is None else int(pk[0])
        assert eb <= int(k), 'the extremum anchor is after the bar it serves'
        es = L2.div_state(CL, close, SIDE, eb)
        ev = L2.div_verdict(CL, close, SIDE, eb)
        got = L2.candidates(BD, SIDE, int(k), 0, cap=JMP, at_cadence=True)
        vn = lambda v: '-' if v is None else ('%+d bullish' % v if v < 0 else '%+d bearish' % v)
        print('| %s | %s | %s | %s | %s | %s | %s | %s |'
              % (ln.U(k), '-' if cs is None else '%+d' % cs, vn(cv), ln.U(eb),
                 '-' if es is None else '%+d' % es, vn(ev),
                 'none' if not got else ', '.join('ws%d %.2f' % (t2, BD.value(int(t2), int(k)))
                                                  for t2 in got),
                 'ws%d' % max(got) if got else 'NOTHING - the established mech prints TOP RESET'
                                              ' EMPTY and falls through to EXHAUST'))


#   ===========================================================================================
#   1101 ANNOTATION - THE SAMPLE-AND-HOLD READ. His 1101 ask, verbatim: *"I want to dive into ws4
#   24.86 at 0437 / -instead of printing each 5s bar leading up to 04:37:55, print and hold the ws4
#   r value at 1 minute intervals and 2 minute intervals from 0430 to 0440"*.
#
#   THE WINDOW AND THE INTERVALS ARE HIS - 04:30 to 04:40, 1 min and 2 min. Nothing here is a
#   window of mine.
#
#   THE VALUE COMES FROM `BD.value(tf, bar)`, the SAME read the reset scan prints, so 04:37:55
#   reproduces its 24.86 exactly. ln.line('ws4r') resolves the DB wsf spec and can return a
#   different array of the same name - that is the 13-ws5r trap ln.py's own docstring records.
#
#   W_HOLD_TF, W_HOLD_A, W_HOLD_B, W_HOLD_MINS (comma-separated minute intervals).
#   ===========================================================================================
if os.environ.get('W_HOLD_A'):
    HTF = int(os.environ.get('W_HOLD_TF', '4'))
    HA, HB = ln.K(os.environ['W_HOLD_A']), ln.K(os.environ['W_HOLD_B'])
    rfnc_lo, rfnc_hi = 100.0 - float(K.RMOM_FNC), float(K.RMOM_FNC)
    for mins in [int(x) for x in os.environ.get('W_HOLD_MINS', '1,2').split(',')]:
        step = mins * 12          # 12 bars of 5 s = 1 min
        print()
        print('## ws%dr sampled every %d min and HELD, %s .. %s' % (HTF, mins, ln.U(HA), ln.U(HB)))
        print()
        #   1101 ANNOTATION - THE SEAM COLUMN. His 1101 ask: *"for each ws4 seam from 0400 to
        #   0448, print the values of seam-5s (ie 03:59:55 to 04:47:55, step 240s)"*. The seam is
        #   the sample bar + 1 bar = 5 s, straight from his own "seam-5s". W_HOLD_SEAM turns the
        #   label column on; the sampled bar and its value are unchanged either way.
        seam = bool(os.environ.get('W_HOLD_SEAM'))
        print('| %sthe sampled bar | ws%dr there, held from here | the move from the last sample |'
              ' at or below the %.1f oob? | past the %.1f fence? |'
              % ('the seam | ' if seam else '', HTF, K.OOB_LO, rfnc_lo))
        print('|%s---|---|---|---|---|' % ('---|' if seam else ''))
        prev = None
        k = int(HA)
        while k <= int(HB):
            v = float(BD.value(HTF, k))
            print('| %s%s | %.2f | %s | %s | %s |'
                  % ('%s | ' % ln.U(k + 1) if seam else '',
                     ln.U(k), v, '-' if prev is None else '%+.2f' % (v - prev),
                     'YES' if v <= K.OOB_LO else 'no', 'YES' if v <= rfnc_lo else 'no'))
            prev = v
            k += step
    print()
    print('## the bar the reset scan reads, for comparison - NOT part of either series above')
    print()
    print('| the bar | ws%dr | at or below the %.1f oob? | past the %.1f fence? |'
          % (HTF, K.OOB_LO, rfnc_lo))
    print('|---|---|---|---|')
    for t in [x.strip() for x in os.environ.get('W_HOLD_MARK', '').split(',') if x.strip()]:
        k = ln.K(t)
        v = float(BD.value(HTF, k))
        print('| %s | %.2f | %s | %s |'
              % (ln.U(k), v, 'YES' if v <= K.OOB_LO else 'no', 'YES' if v <= rfnc_lo else 'no'))


#   ===========================================================================================
#   1101 ANNOTATION - THE FIRST-REVERSAL SCAN. His 1101 ask, verbatim: *"who is the rider at 0437?
#   for each ws{7 to 15) low-side reversals after 0437, print the first reversal for all them.  add
#   their value"*.
#
#   THE REVERSAL READ IS lineage2's OWN - `_rev_pairs(BD, tf, side)`, the one home for a rung's
#   reversal stamp at LIN2_REV_WOB 12 bars = 60 s. The raw bar is the reversal's identity and the
#   stamp is raw + wob - 1, the first bar a consumer may act on. Both are printed; neither is mine.
#
#   NO FORWARD BOUND. He said *"after 0437"* and named no end, so the scan runs to the tape end.
#   W_REVSCAN_AT is his bar, W_REVSCAN_TFS his ws7..ws15 range.
#   ===========================================================================================
if os.environ.get('W_REVSCAN_AT'):
    RA = ln.K(os.environ['W_REVSCAN_AT'])
    TFS = [int(x) for x in os.environ.get('W_REVSCAN_TFS', '7,8,9,10,11,12,13,14,15').split(',')]
    print()
    print('## the first %s-side reversal of each rung at or after %s - no forward bound'
          % (sys.argv[2], ln.U(RA)))
    print()
    print('| the rung | its value at %s | the first reversal raw bar | min after %s |'
          ' its value at the raw bar | the stamp, raw + %d bars | its value at the stamp |'
          % (ln.U(RA)[11:], ln.U(RA)[11:], int(K.LIN2_REV_WOB) - 1))
    print('|---|---|---|---|---|---|---|')
    for tf in TFS:
        prs = [(int(r), int(st)) for r, st in L2._rev_pairs(BD, tf, SIDE) if int(r) >= int(RA)]
        v0 = float(BD.value(tf, int(RA)))
        if not prs:
            print('| ws%d | %.2f | NONE to the tape end | - | - | - | - |' % (tf, v0))
            continue
        r, st = prs[0]
        assert r >= int(RA), 'a reversal before the bar the scan starts at'
        print('| ws%d | %.2f | %s | %.1f | %.2f | %s | %.2f |'
              % (tf, v0, ln.U(r), (r - int(RA)) * 5 / 60.0, float(BD.value(tf, r)),
                 ln.U(st), float(BD.value(tf, st))))


#   ===========================================================================================
#   1101 ANNOTATION - THE LIFT-OFF SAMPLING ARMS. His 1101 question: *"would reducing lift-offs
#   sampling (width and sample count) pull the timestamp back to an earlier time?"*
#
#   THE TWO KNOBS HE NAMED, and nothing else moves:
#     LIFT_PTS     the sample count in the lattice, banked 6
#     GAP_PER_TF   the width - bars per TF-minute, banked 2.8, so gap_for(tf) = round(tf x 2.8)
#   LIFT_TOL 2.0 and the wobs are untouched.
#
#   THE DIRECTION IS NOT DERIVABLE, which is why this is measured. `at_extreme_mask` takes the
#   window extreme over span = (pts - 1) x gap bars. A SMALLER span means a nearer extreme, so the
#   at-extreme state is EASIER to hold - and a state that holds longer fails LATER. Reducing the
#   sampling can therefore move a lift-off later as readily as earlier, and can also create
#   lift-offs where the lattice never held before.
#
#   THE CACHES MUST BE CLEARED PER ARM. `_rev_pairs` keys on (id(BD), tf, side, LIN2_REV_WOB) and
#   `ws1r_revs` on (id(line), side, L2_CWS1R_WOB) - neither key carries LIFT_PTS or GAP_PER_TF, so
#   without the clear every arm would return the FIRST arm's arrays. THE BANK ARM IS THE CONTROL
#   ROW: it must reproduce revscan_0437.md, and a silent cache would show it unchanged everywhere.
#
#   ARMS ARE OFF-RULED. The run carries W_V4_EXPERIMENT=1 or v4_knobs refuses.
#   ===========================================================================================
if os.environ.get('W_LIFT_ARMS'):
    #   v4_l2_cadence is not in this driver's import block - it owns the ws1r lift-off cache that
    #   has to be cleared per arm, so it is imported here.
    _e5 = sys.stderr; sys.stderr = io.StringIO()
    try:
        import v4_l2_cadence as CAD
    finally:
        sys.stderr = _e5
    LA = ln.K(os.environ['W_LIFT_ARMS_AT'])
    LTFS = [int(x) for x in os.environ.get('W_REVSCAN_TFS',
                                           '7,8,9,10,11,12,13,14,15').split(',')]
    P0, G0 = int(K.LIFT_PTS), float(K.GAP_PER_TF)
    ARMS = [('the bank - the CONTROL row', P0, G0)]
    for spec in [x.strip() for x in os.environ['W_LIFT_ARMS'].split(';') if x.strip()]:
        pt, gp = spec.split(',')
        ARMS.append(('LIFT_PTS %s, GAP_PER_TF %s' % (pt, gp), int(pt), float(gp)))
    print()
    print('## the first %s-side reversal at or after %s under each lift-off sampling arm'
          % (sys.argv[2], ln.U(LA)))
    print()
    print('| the arm | LIFT_PTS | GAP_PER_TF | the rung | its lattice gap, bars | its lattice'
          ' span, bars = s | the first reversal raw bar | min after %s | vs the bank, min |'
          % ln.U(LA)[11:])
    print('|---|---|---|---|---|---|---|---|---|')
    base = {}
    for nm, pt, gp in ARMS:
        K.LIFT_PTS, K.GAP_PER_TF = pt, gp
        L2._RV.clear()
        CAD._LO.clear()
        for tf in LTFS:
            g = K.gap_for(tf)
            span = (max(2, pt) - 1) * max(1, g)
            prs = [int(r) for r, _st in L2._rev_pairs(BD, tf, SIDE) if int(r) >= int(LA)]
            r = prs[0] if prs else None
            if nm.startswith('the bank'):
                base[tf] = r
            dm = ('-' if r is None or base.get(tf) is None
                  else '%+.1f' % ((r - base[tf]) * 5 / 60.0))
            print('| %s | %d | %.1f | ws%d | %d | %d = %d s | %s | %s | %s |'
                  % (nm, pt, gp, tf, g, span, span * 5,
                     'NONE to the tape end' if r is None else ln.U(r),
                     '-' if r is None else '%.1f' % ((r - int(LA)) * 5 / 60.0), dm))
    K.LIFT_PTS, K.GAP_PER_TF = P0, G0
    L2._RV.clear()
    CAD._LO.clear()


#   ===========================================================================================
#   1101 ANNOTATION - EVERY REVERSAL IN HIS WINDOW. His 1101 ask, verbatim: *"let's focus on ws5r
#   to ws10r.  print their reversals 5 minutes before the 0437 cadence, and 10 minutes after"*.
#
#   THE WINDOW IS HIS - the 04:37:55 cadence minus 5 min to plus 10 min. EVERY reversal inside it,
#   not the first: he asked for their reversals.
#
#   THE READ IS lineage2's OWN `_rev_pairs(BD, tf, side)` at LIN2_REV_WOB 12 bars = 60 s. The raw
#   bar is the reversal's identity; the stamp is raw + wob - 1, the first bar a consumer may act on.
#   ===========================================================================================
if os.environ.get('W_REVWIN_AT'):
    RC = ln.K(os.environ['W_REVWIN_AT'])
    bef = int(float(os.environ.get('W_REVWIN_BEFORE_MIN', '5')) * 12)
    aft = int(float(os.environ.get('W_REVWIN_AFTER_MIN', '10')) * 12)
    WA, WB = int(RC) - bef, int(RC) + aft
    WTFS = [int(x) for x in os.environ.get('W_REVWIN_TFS', '5,6,7,8,9,10').split(',')]
    rows = []
    for tf in WTFS:
        for r, st in L2._rev_pairs(BD, tf, SIDE):
            if WA <= int(r) <= WB:
                rows.append((int(r), int(tf), int(st)))
    rows.sort()
    print()
    print('## every %s-side reversal of ws%d r .. ws%d r, %s .. %s - HIS WINDOW, the %s cadence'
          ' minus %.0f min to plus %.0f min'
          % (sys.argv[2], min(WTFS), max(WTFS), ln.U(WA), ln.U(WB), ln.U(RC),
             bef / 12.0, aft / 12.0))
    print()
    print('| the reversal raw bar | the rung | its value at the raw bar | min from the cadence |'
          ' the stamp, raw + %d bars | its value at the stamp |' % (int(K.LIN2_REV_WOB) - 1))
    print('|---|---|---|---|---|---|')
    if not rows:
        print('| no reversal of any of those rungs falls in the window | - | - | - | - | - |')
    for r, tf, st in rows:
        print('| %s | ws%d | %.2f | %+.1f | %s | %.2f |'
              % (ln.U(r), tf, float(BD.value(tf, r)), (r - int(RC)) * 5 / 60.0,
                 ln.U(st), float(BD.value(tf, st))))
    print()
    print('| the rung | reversals in the window | before the cadence | at or after it |')
    print('|---|---|---|---|')
    for tf in WTFS:
        mine = [r for r, t, _s in rows if t == tf]
        print('| ws%d | %d | %d | %d |'
              % (tf, len(mine), sum(1 for r in mine if r < int(RC)),
                 sum(1 for r in mine if r >= int(RC))))


#   ===========================================================================================
#   1101 ANNOTATION - THE SAMPLING PHASE A/B. His 1101 question: *"now I want to know if this is
#   the best way to print closed bars causally, or would it be better if the value is sampled at
#   (seam - 0s, ie seam)?  let's see the comparison"*.
#
#   THERE IS ONE ws4r ARRAY IN PLAY, so this is a question about WHICH BAR, not which ladder.
#   `Board._state` returns `self.E[tf]` because this driver passes PS=None, and the Board's own
#   __init__ asserts C and E are the same arrays - his 1029 ruling *"completely drop prev-close"*.
#   So seam-5s and seam are two bars of the same series.
#
#   BOTH PHASES ARE CAUSAL. seam-5s is the last 5 s bar of the ws{tf} bar that just closed; seam
#   is the first bar of the next one. Neither reads forward. WHICH ONE IS THE CLOSED BAR'S VALUE
#   IS HIS CALL, not mine, and the diff column is what it turns on.
#   ===========================================================================================
if os.environ.get('W_SEAM_AB_A'):
    STF = int(os.environ.get('W_SEAM_AB_TF', '4'))
    SA, SB = ln.K(os.environ['W_SEAM_AB_A']), ln.K(os.environ['W_SEAM_AB_B'])
    sstep = int(float(os.environ.get('W_SEAM_AB_MIN', '4')) * 12)
    rfl = 100.0 - float(K.RMOM_FNC)
    print()
    print('## ws%dr at seam minus 5 s against ws%dr at the seam - %s .. %s, step %d bars = %d s'
          % (STF, STF, ln.U(SA), ln.U(SB), sstep, sstep * 5))
    print()
    print('| the seam | ws%dr at seam minus 5 s | ws%dr at the seam | the seam minus the'
          ' seam-minus-5s | at or below the %.1f oob at seam-5s? | at the seam? |'
          ' past the %.1f fence at seam-5s? | at the seam? |'
          % (STF, STF, K.OOB_LO, rfl))
    print('|---|---|---|---|---|---|---|---|')
    AB = []
    k = int(SA)
    while k <= int(SB):
        va, vb = float(BD.value(STF, k)), float(BD.value(STF, k + 1))
        AB.append((k + 1, va, vb))
        print('| %s | %.2f | %.2f | %+.2f | %s | %s | %s | %s |'
              % (ln.U(k + 1), va, vb, vb - va,
                 'YES' if va <= K.OOB_LO else 'no', 'YES' if vb <= K.OOB_LO else 'no',
                 'YES' if va <= rfl else 'no', 'YES' if vb <= rfl else 'no'))
        k += sstep
    d = [abs(b - a) for _s, a, b in AB]
    print()
    print('| the read | value |')
    print('|---|---|')
    print('| seams compared | %d |' % len(AB))
    print('| seams where the two phases are identical | %d |' % sum(1 for x in d if x == 0.0))
    print('| seams where they differ | %d |' % sum(1 for x in d if x > 0.0))
    print('| the largest absolute difference | %.2f r-points |' % (max(d) if d else 0.0))
    print('| the mean absolute difference | %.2f r-points |'
          % ((sum(d) / len(d)) if d else 0.0))
    print('| seams where the fence verdict differs between the phases | %d |'
          % sum(1 for _s, a, b in AB if (a <= rfl) != (b <= rfl)))
    print('| seams where the oob verdict differs between the phases | %d |'
          % sum(1 for _s, a, b in AB if (a <= K.OOB_LO) != (b <= K.OOB_LO)))
    #   1101 ANNOTATION - WHAT THE CHART CANNOT SHOW. His 1101 point: *"if I take seam, then 0436
    #   prints an ex-fence latch value that I can't see on the charts.  I need to be able to match
    #   the charts causally so that the stratgegy I've mapped out fits the code"*. The code tests
    #   its fences on EVERY 5 s bar; a chart of a ws{tf} line shows him one value per tf. This
    #   counts the gap on the same window - how many ex-fence and oob bars exist that no seam-5s
    #   sample reports.
    allb = [float(BD.value(STF, k)) for k in range(int(SA), int(SB) + 2)]
    smp = [a for _s, a, _b in AB]
    print()
    print('| the read | every 5 s bar | the seam-minus-5s samples |')
    print('|---|---|---|')
    print('| bars or samples in the window | %d | %d |' % (len(allb), len(smp)))
    print('| past the %.1f fence | %d | %d |'
          % (rfl, sum(1 for v in allb if v <= rfl), sum(1 for v in smp if v <= rfl)))
    print('| at or below the %.1f oob | %d | %d |'
          % (K.OOB_LO, sum(1 for v in allb if v <= K.OOB_LO),
             sum(1 for v in smp if v <= K.OOB_LO)))
    print('| the lowest value seen | %.2f | %.2f |' % (min(allb), min(smp)))
    print('| the highest value seen | %.2f | %.2f |' % (max(allb), max(smp)))


#   ===========================================================================================
#   1101 ANNOTATION - THE BOARD SNAPSHOT. His 1101 read: *"0554 can't exhaust - ws3r is oob so it
#   must walk to the next cadence"*. The exhaust row names the rider as ws5 at 58.61, so the
#   question is what the REST of the board was doing at that bar.
#
#   EVERY RUNG, EVERY READ THE WALK USES, at one bar. Each column names the source it came from,
#   because the three reads are now routed independently.
#   W_BOARD_AT is his bar.
#   ===========================================================================================
if os.environ.get('W_BOARD_AT'):
    BA = ln.K(os.environ['W_BOARD_AT'])
    RD = int(os.environ.get('W_BOARD_RIDER', '0'))
    JMP = int(K.LIN2_RIDER_JUMP) or None
    cap = (RD + JMP) if (RD and JMP) else None
    print()
    print('## the board at %s, side %s | rider ws%s | the candidate band is ws%s..ws%s'
          % (ln.U(BA), sys.argv[2], RD or '-', (RD + 1) if RD else 1,
             cap if cap else K.L2_MOM_MAXTF))
    print()
    print('| the rung | its r value | oob at %.1f/%.1f? | past the %.1f/%.1f fence? | reversed'
          ' since the bar before? | above the rider? | inside the jump band? |'
          % (K.OOB_LO, K.OOB_HI, 100.0 - K.RMOM_FNC, K.RMOM_FNC))
    print('|---|---|---|---|---|---|---|')
    for tf in range(1, int(K.L2_MOM_MAXTF) + 1):
        v = float(BD.value(tf, int(BA)))
        inband = bool(RD and tf > RD and (cap is None or tf <= cap))
        print('| ws%d | %.2f | %s | %s | %s | %s | %s |'
              % (tf, v,
                 'YES' if BD.oob(tf, int(BA), SIDE) else 'no',
                 'YES' if BD.ex_fence(tf, int(BA), SIDE) else 'no',
                 'YES' if BD.reversed_in(tf, SIDE, int(BA) - 1, int(BA)) else 'no',
                 'YES' if (RD and tf > RD) else 'no',
                 'YES' if inband else 'no'))
    print()
    print('| the read | value |')
    print('|---|---|')
    print('| the oob read\'s source | %s |' % K.LIN2_CP_OOB)
    print('| the ex-fence read\'s source | %s |' % K.LIN2_CP_EXFNC)
    print('| rungs oob on this side | %d |'
          % sum(1 for tf in range(1, int(K.L2_MOM_MAXTF) + 1) if BD.oob(tf, int(BA), SIDE)))
    print('| rungs ex-fence on this side | %d |'
          % sum(1 for tf in range(1, int(K.L2_MOM_MAXTF) + 1) if BD.ex_fence(tf, int(BA), SIDE)))


#   ===========================================================================================
#   1101 ANNOTATION - THE 120 s MATRYOSHKA READ. His 1101 proposal, verbatim: *"if we walk forward
#   120s from the cadence and test ws1,2,3r (or ws1,2,3,4r) for a matryoshka pattern (based on the
#   reversing and away states), will we be able to predict pxs reversing?  I can see it working at
#   05:02:55 +120s, and again at ~0529 +120s.  I don't know if it will hold for 0555 +120s, which
#   is why I've added ws4r. ws4r's positioning indicates the next move:  if it's oob, then the
#   matryoshka pattern is invalid"*.
#
#   NOTHING IS BUILT. This prints the states he named at the three bars he named, so the pattern is
#   his to read. His matryoshka definition is the banked one, 1026: *"if >1 lines that are lower TF
#   than the rider TF and have reversed, then it is likely that the rider TF will also reverse"*.
#
#   THE WINDOW IS HIS - 120 s = 24 bars from the cadence, counting the cadence bar.
#   AWAY IS `not towards`, the banked trajectory read with the perspective on the target side.
#   THE PRICE COLUMN IS THE BAR'S CLOSE, which is what the chain's own legend calls pxs.
#   THE OUTCOME COLUMN READS BARS AFTER THE WINDOW ON PURPOSE: his question is whether the pattern
#   PREDICTS, so the thing predicted has to be looked at. It is an outcome, never an input, and no
#   mech reads it.
#   ===========================================================================================
if os.environ.get('W_MATRY'):
    #   1101: W_MATRY_SRC picks which VALUES the pattern reads - his *"let's see it on closed"*.
    #   'emerging' is this driver's own Board, whose value/line/towards/oob all resolve to the live
    #   ladder. 'closed_prev' builds a SECOND Board over the chart-matched ladder, so every read in
    #   the pattern - the value, the away state, the oob verdict and the reversal detector - comes
    #   off the seam-5s series carried forward. Nothing in the walk uses this Board.
    MB = BD
    if os.environ.get('W_MATRY_SRC', 'emerging') == 'closed_prev':
        _e7 = sys.stderr; sys.stderr = io.StringIO()
        try:
            import v4_closed_prev as CP
        finally:
            sys.stderr = _e7
        _cpl = CP.ladder(E)
        MB = PX.Board(_cpl, _cpl, MG=MG, MGE=MG, PS=None)
    MW = int(float(os.environ.get('W_MATRY_S', '120')) / 5)
    ROWS = [x.strip() for x in os.environ['W_MATRY'].split(';') if x.strip()]
    TFS = [int(x) for x in os.environ.get('W_MATRY_TFS', '1,2,3,4').split(',')]
    print()
    print('## the %d s = %d bar window after each cadence he named | away is `not towards`'
          ' | the values are %s'
          % (MW * 5, MW, os.environ.get('W_MATRY_SRC', 'emerging')))
    print()
    print('| the cadence | its side | the rung | its first AWAY bar | min from the cadence |'
          ' away at the window end? | its first reversal bar, the detector | oob at the window'
          ' end? | its value at the cadence | at the window end |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    SUM = []
    for spec in ROWS:
        t, sdn = [x.strip() for x in spec.split('|')]
        sd = 1 if sdn == 'high' else -1
        k = ln.K(t)
        e = int(k) + MW - 1
        #   *** HIS 1101 CORRECTION: AWAY IS THE EVIDENCE OF A TURN. *** *"ws2r (or any line)
        #   printing away infers a reversal has already happened"*. So the matryoshka count is the
        #   AWAY state, not the reversal detector - and the PATTERN is the ORDER the rungs go away
        #   in, lowest timeframe first, which is what matryoshka means in his 1026 words.
        #   THE FIRST AWAY BAR is therefore the per-rung field, beside the detector's own first
        #   reversal bar so the two reads sit against each other.
        nrev = naway = 0
        for tf in TFS:
            fr = None
            for b in range(int(k), e + 1):
                if MB.reversed_in(tf, sd, int(k), b):
                    fr = b
                    break
            fa = None
            for b in range(int(k), e + 1):
                if not L2.towards(MB, tf, b, sd):
                    fa = b
                    break
            aw = not L2.towards(MB, tf, e, sd)
            ob = MB.oob(tf, e, sd)
            if fr is not None:
                nrev += 1
            if aw:
                naway += 1
            print('| %s | %s | ws%d | %s | %s | %s | %s | %s | %.2f | %.2f |'
                  % (ln.U(k), sdn, tf,
                     '-' if fa is None else ln.U(fa),
                     '-' if fa is None else '%+.1f' % ((fa - int(k)) * 5 / 60.0),
                     'YES' if aw else 'no',
                     '-' if fr is None else ln.U(fr),
                     'YES' if ob else 'no',
                     float(MB.value(tf, int(k))), float(MB.value(tf, e))))
        SUM.append((k, sdn, sd, e, nrev, naway, (4 in TFS) and MB.oob(4, e, sd)))
    print()
    _nm = 'ws%d..ws%d' % (min(TFS), max(TFS))
    print('| the cadence | its side | %s that reversed in the window | %s away at the end |'
          ' ws4r oob at the end? | the pattern, by his rule | pxs at the cadence | at the window'
          ' end | the move over the window | OUTCOME ONLY, never a mech input: the move over the'
          ' %d bars past the window |' % (_nm, _nm, MW))
    print('|---|---|---|---|---|---|---|---|---|---|')
    for k, sdn, sd, e, nrev, naway, ob4 in SUM:
        p0, p1 = float(close[int(k)]), float(close[e])
        n2 = min(e + MW, len(close) - 1)
        p2 = float(close[n2])
        print('| %s | %s | %d of %d | %d of %d | %s | %s | %.6f | %.6f | %+.4f%% | %+.4f%% |'
              % (ln.U(k), sdn, nrev, len(TFS), naway, len(TFS),
                 'YES' if ob4 else ('no' if 4 in TFS else 'ws4r is OUT - his 1101 "remove ws4r"'),
                 'INVALID - ws4r is oob' if ob4 else
                 ('matryoshka: more than 1 AWAY' if naway > 1 else 'not met: 1 or fewer AWAY'),
                 p0, p1, (p1 - p0) / p0 * 100.0, (p2 - p1) / p1 * 100.0))
