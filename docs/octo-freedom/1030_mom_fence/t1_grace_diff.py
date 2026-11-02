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


#   ===========================================================================================
#   1101 ANNOTATION - THE PER-CROSS TRACE. His one-script rule, so this lives here beside the
#   cadence list it explains rather than in a new file.
#
#   HIS 1101 READ, verbatim: *"I don't see the cadence marker at 2326: gcws30b returns to ib and
#   the wob should be confirmed ~23:24:30"*. The cadence list above has no bar there. This block
#   prints EVERY gcws30b oob->ib cross in the SAME A..B window, with each t1 condition at its own
#   bar and the FIRST one that fails, so a missing cadence has a named cause instead of a silence.
#
#   THE CONDITIONS, in t1's own order (v4_l2_cadence.t1):
#     1  oob_ib_cross returns the cross - gcws30b IB on both sides for LIN2_T1_B_WOB bars
#     2  the cross's own side matches the target side
#     3  a run of the HELD oob mask ends exactly at c - 1          <- LIN2_B1_OOB_DWELL lives here
#     4  a ws1r reversal raw bar inside that run, r past the fence  (the DURING branch)
#     5  else a ws1r reversal raw bar in the 120 s grace, r past the fence  (the GRACE branch)
#
#   THE LINE TABLE'S BOUNDS ARE MINE, not his - W_TRACE_A and W_TRACE_B, and they bound the
#   printed line table ONLY. The cross trace scans the driver's own A..B and is not windowed.
#   ===========================================================================================
if os.environ.get('W_TRACE'):
    _e2 = sys.stderr; sys.stderr = io.StringIO()
    try:
        from optimus9.analysis.jig import (oob_ib_cross, anchor_floater, mage_cascade_bar,
                                           MC_GAP)
        from v4_backstop_trades import prices
    finally:
        sys.stderr = _e2
    _close, _h, _l = prices()
    _px = np.asarray(_close, float)
    _MG1 = np.asarray(LL.mage(1)[1], float)
    SD = -1 if os.environ.get('W_TRACE_SIDE', 'low') == 'low' else 1
    NM = 'low' if SD < 0 else 'high'
    b1 = np.asarray(CL['g30b'], float)
    r1 = np.asarray(CL['r'][1], float)
    w1 = max(1, int(K.LIN2_T1_B_WOB))
    raw_oob = np.asarray(K.oob_mask(b1, SD), bool)
    held = CAD.b1_beyond(b1, SD)
    raws = [int(x) for x in CAD.ws1r_revs(r1, SD)]
    grace = max(0, int(K.L2_T1_GRACE_S) // 5)
    rlo, rhi = 100.0 - float(K.LIN2_T1_R_FNC), float(K.LIN2_T1_R_FNC)
    rfence = rhi if SD > 0 else rlo
    #   CAD._stamp, NOT K.lift_stamp - K.lift_stamp adds LIFT_WOB - 1 = 7 bars
    #   = 35 s and lineage2's ws1r wob is its own. The first build of this trace
    #   used K.lift_stamp and read every r value 35 s after the mech reads it.
    rpass = lambda x: (float(r1[CAD._stamp(x)]) >= rhi) if SD > 0 \
        else (float(r1[CAD._stamp(x)]) <= rlo)

    print()
    print('## the t1 read\'s own knobs, %s side' % NM)
    print()
    print('| the knob | value | what it gates |')
    print('|---|---|---|')
    print('| LIN2_T1_B_LINE | %s | the b line t1 reads |' % K.LIN2_T1_B_LINE)
    print('| LIN2_T1_B_WOB | %d bars = %d s | the IB hold that CONFIRMS the cross |' % (w1, w1 * 5))
    print('| the oob fence | %.1f / %.1f | oob_ib_cross\'s own hi/lo - oob is 15/85 |'
          % (K.OOB_LO, K.OOB_HI))
    print('| LIN2_B1_OOB_DWELL | %d bars = %d s | the oob run must REACH this before it counts |'
          % (K.LIN2_B1_OOB_DWELL, K.LIN2_B1_OOB_DWELL * 5))
    print('| LIN2_B1_HOLD | %d bars = %d s | a blip back to IB shorter than this still reads oob |'
          % (K.LIN2_B1_HOLD, K.LIN2_B1_HOLD * 5))
    print('| LIN2_T1_R_FNC | %.1f -> (%.1f, %.1f) | ws1r at its stamp must be past %.1f |'
          % (K.LIN2_T1_R_FNC, rlo, rhi, rfence))
    print('| L2_T1_GRACE_S | %d s = %d bars | the forward window for a late ws1r reversal |'
          % (K.L2_T1_GRACE_S, grace))
    print('| LIN2_T1_GRACE_AT | %r | where that window starts |' % str(K.LIN2_T1_GRACE_AT))
    print('| L2_CWS1R_WOB | %d bars = %d s | the ws1r lift-off\'s own hold - CAD._stamp adds'
          ' this minus 1 to the raw bar. NOT LIFT_WOB %d |'
          % (K.L2_CWS1R_WOB, K.L2_CWS1R_WOB * 5, K.LIFT_WOB))

    print()
    print('## every gcws30b oob->ib cross, %s side, %s .. %s - the driver\'s own window'
          % (NM, ln.U(A), ln.U(B)))
    print()
    print('| the cross bar | the confirm bar | gcws30b at the cross | the run before | the HELD'
          ' run ending at cross-1 | ws1r revs in that run | ws1r revs in the grace | the cadence'
          ' | the first condition that fails |')
    print('|---|---|---|---|---|---|---|---|---|')
    for c, cf, s in oob_ib_cross(b1, K.OOB_HI, K.OOB_LO, w1):
        if not (int(A) <= int(cf) <= int(B)):
            continue
        rr = next((r for r in CAD._runs(raw_oob) if r[1] == c - 1), None)
        hr = next((r for r in CAD._runs(held) if r[1] == c - 1), None)
        dur = [] if hr is None else [x for x in raws if hr[0] <= x <= hr[1]]
        g0 = int(c) if str(K.LIN2_T1_GRACE_AT) == 'cross' else int(cf)
        lat = [x for x in raws if g0 < x <= g0 + grace]
        fire, fail = '-', ''
        if s != SD:
            fail = 'the run before the cross was on the %s side' % ('high' if s > 0 else 'low')
        elif hr is None:
            fail = ('no HELD oob run ends at %s - the raw run %s is %d bars, the dwell needs %d'
                    % (ln.U(c - 1)[11:],
                       '%s..%s' % (ln.U(rr[0])[11:], ln.U(rr[1])[11:]) if rr else 'none',
                       0 if rr is None else rr[1] - rr[0] + 1, int(K.LIN2_B1_OOB_DWELL)))
        else:
            dok = [x for x in dur if rpass(x)]
            lok = [x for x in lat if rpass(x)]
            if dok:
                fire = ln.U(max(int(cf), CAD._stamp(dok[-1])))
            elif lok:
                fire = ln.U(max(int(cf), CAD._stamp(lok[0])))
            elif dur or lat:
                fail = ('every ws1r reversal is inside the %.1f fence: %s'
                        % (rfence, ', '.join('%s r %.2f' % (ln.U(CAD._stamp(x))[11:],
                                                            float(r1[CAD._stamp(x)]))
                                             for x in (dur + lat))))
            else:
                fail = 'no ws1r reversal in the run or in the %d s grace' % K.L2_T1_GRACE_S
        fmt = lambda xs: ('-' if not xs else
                          ', '.join('%s r %.2f%s' % (ln.U(CAD._stamp(x))[11:],
                                                     float(r1[CAD._stamp(x)]),
                                                     '' if rpass(x) else ' INSIDE')
                                    for x in xs))
        print('| %s | %s | %.2f | %s | %s | %s | %s | %s | %s |'
              % (ln.U(c), ln.U(cf), float(b1[c]),
                 '%s..%s %s' % (ln.U(rr[0])[11:], ln.U(rr[1])[11:], 'raw') if rr else 'none',
                 '%s..%s' % (ln.U(hr[0])[11:], ln.U(hr[1])[11:]) if hr else 'NONE',
                 fmt(dur), fmt(lat), fire, fail))

    TA, TB = ln.K(os.environ['W_TRACE_A']), ln.K(os.environ['W_TRACE_B'])
    print()
    print('## gcws30b and ws1r bar by bar, %s .. %s - THESE BOUNDS ARE MINE'
          % (ln.U(TA), ln.U(TB)))
    print()
    #   1101 ANNOTATION - THE DIVERGENCE STATE JOINS THIS TABLE. His 1101 idea: *"instead of
    #   using it as a trade detector, the divergence signal could be a trigger to fudge the ws1r
    #   value so that it appears (to the code) as an oob print"*. Before any of that is built, the
    #   question is whether a trigger EXISTS on the bars where the r gate is read. Both anchor arms
    #   are printed because neither is ruled. Nothing here fudges anything - this is a read.
    print('| the bar | gcws30b | IB? | raw oob? | HELD oob? | ws1r | a ws1r reversal raw bar? |'
          ' div state, cadence anchor | div verdict there | the extremum bar | div state, extremum'
          ' anchor | div verdict there |')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|')
    rs = set(raws)

    def _dv(bar):
        """(raw state, verdict) of anchor_floater AT `bar`. The verdict collapses PM to None."""
        got = anchor_floater(r1, _px, int(SD), int(bar))
        if got is None:
            return None, None
        st = int(got['state'])
        assert int(got['anchor'][0]) == int(bar), 'the anchor is not the bar it was read on'
        return st, (st if abs(st) == 1 else None)

    def _ex(bar):
        """The target-side ws1Mage extremum at or before `bar` - the cascade's own picker."""
        pk = mage_cascade_bar(_MG1, int(bar), int(SD), mode='extrema', gap=MC_GAP)
        return int(bar) if pk is None else int(pk[0])

    for i in range(TA, TB + 1):
        cs, cv = _dv(i)
        eb = _ex(i)
        assert eb <= i, 'the extremum anchor is after the bar it serves'
        es, ev = _dv(eb)
        vn = lambda v: '-' if v is None else ('%+d bullish' % v if v < 0 else '%+d bearish' % v)
        print('| %s | %.2f | %s | %s | %s | %.2f | %s | %s | %s | %s | %s | %s |'
              % (ln.U(i), float(b1[i]),
                 'YES' if K.OOB_LO < float(b1[i]) < K.OOB_HI else 'no',
                 'YES' if raw_oob[i] else 'no', 'YES' if held[i] else 'no',
                 float(r1[i]),
                 'YES, stamp %s r %.2f' % (ln.U(CAD._stamp(i))[11:],
                                           float(r1[CAD._stamp(i)])) if i in rs else '-',
                 '-' if cs is None else '%+d' % cs, vn(cv),
                 ln.U(eb)[11:], '-' if es is None else '%+d' % es, vn(ev)))


#   ===========================================================================================
#   1101 ANNOTATION - THE OPEN-TO-ARM GAP READ. His 1101 spec, cut down to one line: *"drop the
#   rider reset and retain only the "creates an arm if the trade does not already have an arm""*.
#
#   THE MECH CAN ONLY ACT BETWEEN AN OPEN AND ITS ARM, because that is the only stretch where a
#   trade has no arm. `v4_lineage2.walk` opens with the ARM row at :506 or :513, so inside a walk
#   there is no such bar.
#
#   WHICH BARS THE DIVERGENCE IS TESTED ON IS UNRULED, and it is the whole mech. Two causal
#   readings are printed, neither chosen:
#     every bar    the divergence read on each 5 s bar of the gap
#     t1 only      the divergence read only at the t1 cadences inside the gap. THE DETECTOR is
#                  computable there - `CAD.t1(CL, side, A, B)` takes a window - but HIS 1101
#                  RULING IS THAT t1 REQUIRES AN ARM: *"t1 definitely needs an arm - it will show
#                  up in the updates that I'm presently holding"*. So this reading is DEAD for the
#                  open-to-arm gap by his spec, not by the code, and the rows stay only as the
#                  measurement that retired it.
#   crossed with the two anchor arms, LIN2_DIV_AT 'cadence' and 'extremum'. Four rows per leg.
#
#   THE OPENS AND ARMS ARE HIS, from his 1101 list. His times are estimates to the minute and are
#   used exactly as given - no knob is fitted to them.
#   THE TARGET SIDE IS AN INPUT: LONG hunts the high oob, SHORT the low one.
#   ===========================================================================================
if os.environ.get('W_ARMGAP'):
    _e4 = sys.stderr; sys.stderr = io.StringIO()
    try:
        from optimus9.analysis.jig import anchor_floater, mage_cascade_bar, MC_GAP
        from v4_backstop_trades import prices
    finally:
        sys.stderr = _e4
    _cl, _h2, _l2 = prices()
    _px2 = np.asarray(_cl, float)
    _MG = np.asarray(LL.mage(1)[1], float)
    _r = np.asarray(CL['r'][1], float)

    LEGS = [('2026-09-03 17:01:00', 'LONG',  '2026-09-03 17:16:00'),
            ('2026-09-03 19:30:00', 'SHORT', '2026-09-03 22:01:00'),
            ('2026-09-03 23:24:00', 'LONG',  '2026-09-03 23:39:00'),
            ('2026-09-03 23:43:00', 'SHORT', '2026-09-04 00:07:00'),
            ('2026-09-04 00:09:00', 'LONG',  '2026-09-04 00:36:00')]

    def verdict(sd, bar, arm):
        """(the verdict, the anchor bar) at `bar` under anchor arm `arm`. Causal."""
        ab = int(bar)
        if arm == 'extremum':
            pk = mage_cascade_bar(_MG, int(bar), int(sd), mode='extrema', gap=MC_GAP)
            if pk is not None:
                ab = int(pk[0])
        assert ab <= int(bar), 'the divergence anchor is after the bar it serves'
        got = anchor_floater(_r, _px2, int(sd), int(ab))
        if got is None:
            return None, ab
        st = int(got['state'])
        return (st if abs(st) == 1 else None), ab

    print()
    print('## the divergence inside each open-to-arm gap - his 1101 list, four readings per leg')
    print()
    print('| the open | the side | the target side | the arm he gave | the gap, min | the bars'
          ' tested | the anchor arm | bars tested in the gap | bars whose verdict matches the'
          ' target side | the FIRST match | its anchor bar | min earlier than his arm |')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|')
    for op, sdn, am in LEGS:
        sd = 1 if sdn == 'LONG' else -1
        tgt = 'high' if sd > 0 else 'low'
        o, a = ln.K(op), ln.K(am)
        gap = (a - o) * 5 / 60.0
        cads = [int(b) for b, _t, _w in CAD.t1(CL, sd, o, a)]
        for label, bars in (('every bar', list(range(int(o), int(a) + 1))),
                            ('t1 only', cads)):
            for arm in ('cadence', 'extremum'):
                hit, n = None, 0
                hb = None
                for k in bars:
                    v, ab = verdict(sd, k, arm)
                    if v is not None and int(v) == int(sd):
                        n += 1
                        if hit is None:
                            hit, hb = int(k), int(ab)
                print('| %s | %s | %s | %s | %.1f | %s | %s | %d | %d | %s | %s | %s |'
                      % (ln.U(o), sdn, tgt, ln.U(a), gap, label, arm, len(bars), n,
                         '-' if hit is None else ln.U(hit),
                         '-' if hb is None else ln.U(hb),
                         '-' if hit is None else '%.1f' % ((a - hit) * 5 / 60.0)))


#   ===========================================================================================
#   1101 ANNOTATION - THE gcws30b SOURCE ARM. His 1101 read of the chain: *"I don't see a t1 at
#   0215.  the nearest is 0235.  maybe gcws30 needs to be closed-p"*.
#
#   WHY IT IS NOT ALREADY ROUTED: his rule was *"ws1{any} and gcws1{any} stay on emerging"*, and I
#   read that as every line at or below ws1's 60 s - which left gcws30b at 30 s on the every-bar
#   read. His chart says the t1 bar is wrong, which is the test of that reading.
#
#   THE SWAP IS LOCAL TO THIS DIAGNOSTIC. CL['g30b'] is replaced with its chart-matched series -
#   `v4_closed_prev.series` at 30 s, the value at the last 5 s bar of the completed 30 s bar,
#   carried forward - and t1 is re-listed. Nothing is banked.
#   ===========================================================================================
if os.environ.get('W_B_SRC_AB'):
    _e6 = sys.stderr; sys.stderr = io.StringIO()
    try:
        import v4_closed_prev as CP
    finally:
        sys.stderr = _e6
    SIDES = {-1: 'low', 1: 'high'}
    g_em = np.asarray(CL['g30b'], float)
    g_cp = np.asarray(CP.series(g_em, 30), float)
    K.LIN2_T1_B_LINE, K.LIN2_T1_B_WOB = 'gcws30b', 6
    K.LIN2_T1_R_FNC, K.LIN2_T1_GRACE_AT = 56.0, 'cross'
    OUT = {}
    for src, arr in (('emerging', g_em), ('closed_prev', g_cp)):
        CL['g30b'] = arr
        CAD._LO.clear()
        for sd in (-1, 1):
            OUT[(src, sd)] = [(int(b), w) for b, _t, w in CAD.t1(CL, sd, A, B)]
    CL['g30b'] = g_em
    CAD._LO.clear()
    print()
    print('## the t1 cadence list with gcws30b on each source, %s .. %s' % (ln.U(A), ln.U(B)))
    print()
    print('| the read | low side | high side |')
    print('|---|---|---|')
    for src in ('emerging', 'closed_prev'):
        print('| t1 cadences, gcws30b %s | %d | %d |'
              % (src, len(OUT[(src, -1)]), len(OUT[(src, 1)])))
    for sd in (-1, 1):
        for sd_name in (SIDES[sd],):
            e = {b for b, _w in OUT[('emerging', sd)]}
            c = {b for b, _w in OUT[('closed_prev', sd)]}
            print('| %s side: bars only on emerging | %d | |' % (sd_name, len(e - c)))
            print('| %s side: bars only on closed_prev | %d | |' % (sd_name, len(c - e)))
    for sd in (-1, 1):
        for src in ('emerging', 'closed_prev'):
            rows = OUT[(src, sd)]
            print()
            print('## %s side, gcws30b %s - %d t1 cadences' % (SIDES[sd], src, len(rows)))
            print()
            print('| the cadence bar | why |')
            print('|---|---|')
            for b, w in rows:
                print('| %s | %s |' % (ln.U(b), str(w).replace('|', '\\|')))


#   ===========================================================================================
#   1101 ANNOTATION - THE gcws30b VALUE TRACE. His 1101 read: *"how did 0519 exit without a t1?  I
#   see the t1 at 0528"*. The 05:19:25 cadence's own row says gcws30b came back inside the 5.0
#   fence at 05:19:00, so the question is whether the line was really past 5.0 before that bar.
#
#   BOTH SOURCES ARE PRINTED. The banked read is the chart-matched one, and `CL['g30b']` already
#   carries it - so the EMERGING series is rebuilt here from `sub_line` rather than assumed.
#   THE WINDOW IS W_G_A..W_G_B, and whoever passes it owns it.
#   ===========================================================================================
if os.environ.get('W_G_A'):
    GA, GB = ln.K(os.environ['W_G_A']), ln.K(os.environ['W_G_B'])
    g_now = np.asarray(CL['g30b'], float)
    g_em = np.asarray(LL.sub_line('gcws30b'), float)
    blo, bhi = 100.0 - float(K.LIN2_T1_B_FNC), float(K.LIN2_T1_B_FNC)
    print()
    print('## gcws30b bar by bar, %s .. %s | the banked read is %s | the t1 fence is (%.1f, %.1f)'
          % (ln.U(GA), ln.U(GB), K.LIN2_CP_GCWS30B, blo, bhi))
    print()
    #   1101: THE ib COLUMNS. His read: *"I don't see gcws30b + xwob 6 crossing over 15 (ib)
    #   until 0529"*. ib is `oob_ib_cross`'s own test - STRICTLY between the oob pair, so
    #   15.0 < v < 85.0 - and the cross is confirmed once ib has held LIN2_T1_B_WOB bars. The
    #   run length is counted on the BANKED read, which is what the mech uses.
    _w = max(1, int(K.LIN2_T1_B_WOB))
    _ibrun = 0
    print('| the bar | gcws30b, the banked chart-matched read | at or below %.1f? | ib, strictly'
          ' inside %.1f..%.1f? | the ib run so far, bars | the %d-bar hold met? | gcws30b on the'
          ' every-bar read | ib there? |'
          % (blo, K.OOB_LO, K.OOB_HI, _w))
    print('|---|---|---|---|---|---|---|---|')
    for i in range(int(GA), int(GB) + 1):
        a, b = float(g_now[i]), float(g_em[i])
        aib = bool(K.OOB_LO < a < K.OOB_HI)
        bib = bool(K.OOB_LO < b < K.OOB_HI)
        _ibrun = _ibrun + 1 if aib else 0
        print('| %s | %.2f | %s | %s | %d | %s | %.2f | %s |'
              % (ln.U(i), a, 'YES' if a <= blo else 'no', 'YES' if aib else 'no', _ibrun,
                 'YES' if _ibrun >= _w else 'no', b, 'YES' if bib else 'no'))
