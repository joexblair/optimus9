"""report_wsf_bar — THE wsf-model-report. One bar, one table. Joe 0820.

THE FORMAT IS NAMED AND FIXED. Joe 0820: "bank this format as wsf-model-report", and gave the
column list verbatim:

    line | r value | heading | r IB | verdict | stalled | 50 gate | blocked by 50 | last-verdict |
    last-verdict-dwell | Mage value | lb-mage-oob | weak-mage

Columns are not added, removed or reordered without Joe saying so.

ADDED 0824 on Joe's word, in this order after `verdict`:
    curl_dr         which way the line points AFTER the turn. Joe 0824: "if r was 80 and heading
                    upwards, then the following curl will be curl_dr -1". Prints only where
                    verdict = curl, Joe 0824.
    wsf-curl-mode   the curl verdict with GATE 2 EXCLUDED - the gate that discards a curl whose
                    bend points against dr. Joe 0824 named it and set its scope: "gate 2 only",
                    momentum-kill still applies, curl_dr rule unchanged. Prints only where the
                    producer's raw fit said curl.

THE FOOTNOTES, Joe 0824: "add any pertinent data to the report. it seems that most of them are
footnotes. only add data columns if you need to". Every one is a reading of the WHOLE board, so
none of them became a column. No producer is restated here - each is imported.

    dr         gcws30Mage, ws1Mage and ws2Mage against the 80/20 fence, and the dr they give.
               jig.wsf_facing_dr for the fence test, jig.wsf_dr_lookback for the 3-minute lookback.
               Joe 0823: "wsf's dr will be set by the positioing of gcws30Mage, ws1Mage and ws2Mage
               - if they are all > {100 - knob:20 fence} then dr = +1" and "restrict the lookback
               to 3 minutes". The three lines are read from ws_line_bar, PROVEN identical to
               build_dtf_delegation's own values across all 85 delegation bars, 0 mismatches, and
               the lookback producer is PROVEN to reproduce all 85 banked answers, 0 mismatches.
               IT REPORTS THE LOOKBACK ANSWER, naming the bar it came from and how far back.
               Reading only the bar itself said "no dr" at 03:53:00 while the mechanic had dr +1
               from 5 seconds earlier. It also says plainly when the board's dr is not the one the
               three lines give.
               THE LABEL IS `dr`, Joe 0825: "it's better to stick with our universal dr". "facing"
               was my coinage from Joe's question "which way am I facing?" and is gone. The two
               readings are labelled together, Joe 0825 verbatim: "three-mage-lb: {yes/no},
               three-mage-dr: {dr}" - lb is whether the lookback found a bar, dr is what it gives.
    template   Joe's spec 3.5 markers - the away count, the toward count, the r IB count, the LTF
               and HTF splits, how far ws8r is from its fence and what its verdict did, the
               weak-mage and how many Mage lines are out. LTF and HTF are imported from
               build_wsf_setup_model so the setup model and this report cannot drift apart.
    stoch      jig.stoch_out_extreme - the reading LEAVING the seven-bar window, at 0 or at 100,
               fixes which way r can still move. Then how many lines are committed to the
               direction the bar is read at.

THE dtf STATE IS STILL NOT QUERIED HERE. The footer's "domTF is blocking" rule reads wsf_domtf on
ws_fin_9of12 and therefore only fires on a wsf9of12 signal bar. Joe 0824, asked whether it should
read dtf_state_flip instead: "not yet; we need to build our wsf fu first. it's on my radar."

THE HEADER IS TWO LINES, Joe 0824: "print the column names on 2 lines so that the report fits in my
screen". Each name splits at its own hyphen or space, never mid-word, so nothing is renamed. Column
widths are then computed from the data and the two header halves, which is what narrows the table:
257 characters before, 196 after.

EXTENDED 0821, Joe: "if the six new columns pass the test, add them to the formal wsf-model-report".
They passed - 84 truncation checks, 0 mismatches. Seven columns were stored, not six; the extra one
is the developing stoch reading that Joe's own question about emerging lines produced.

    stoch now   the DEVELOPING stoch reading, updated every 5 s
    stoch out   THE INCOMING THRESHOLD - the oldest closed stoch still inside the seven-bar
                average, the one that leaves when this line's next bar closes. r rises only if the
                incoming beats it. (stoch now - stoch out) / 7 is the move r is taking right now
    sat clock   bars of this line since RSI last SET its 8-bar extreme on the side read. The
                DEVELOPING bar is bar 0 and competes for it, so a fresh extreme reads 0
    sat left    bars before that extreme must roll out of the window and the stoch must fall
    RSI         RSI(5) on the developing bar
    RSI lo/hi   the window the stoch divides by. hi minus lo is the amplifier - a narrow window
                turns a small RSI move into a large stoch move

    python3 report_wsf_bar.py 07:36:20            the bar's own side, from ws_fin_9of12
    python3 report_wsf_bar.py 07:36:20 up         force the upward read
    python3 report_wsf_bar.py 07:36:20 down       force the downward read

Reads only what is already banked - wsf_line_bar for the r line and its momentum, wsf_bar_tf for
Mage and the weak-mage scan. Nothing is recomputed, so a request is a query.

THE COLUMNS, and where each comes from.
  r value        ws{tf}r at this bar.
  verdict        the momentum verdict on that line, read on this bar's side, AFTER Joe 0820's rule:
                 a momentum-true r line that is out of bounds or stalled reads none. The producer's
                 own answer is kept alongside in wflb_ungated and is not what this column shows.
  stalled        the STALL_N 6 mechanic: 6 lattice samples in a row with no new extreme.
  Mage value     ws{tf}Mage at this bar.
  lb-mage-oob    Mage is out of bounds on this side now, OR was inside the last 120 seconds.
                 That tolerance is the spec's WMT_LOOKBACK_S.
  weak-mage      the one line the scan stops at: ws1 upward, the first Mage the tolerance does not
                 count as out. Only that row is marked.
  heading        MY RULE, fitted to Joe's read at 07:36:20 and matching all seven lines he called:
                   a line already past its fence is heading AWAY - it has made the cross already
                   otherwise the sign of the momentum fit's slope says which way it points
                 Every value it reads is printed at or before this bar. Joe's own explanation used
                 the bar's CLOSE, which at 07:36:20 had not printed yet.
  r IB           r is inside the fence. Joe 0820 first asked for "1) inside the fence and 2)
                 heading away", then withdrew the second condition: "I can't rely on `heading` to
                 support `r IB`. the reason: r lines cannot be relied on - sometimes they are
                 crossing out of the fence later that wsf9of12, and sometimes they don't exit the
                 fence at all". So heading no longer gates it.
                 THE FENCE HERE IS STILL 85/15. Joe moved `heading` onto momo-fence-r and has not
                 moved this one. It changes only lines sitting between 83 and 85.
  50 gate        the level test inside momo_core. The line must be on the far side of 50 for its
                 direction, but the gate SLACKENS by up to LEVEL_SLACK 13.9 points in proportion to
                 how cleanly the line tracks: slack = 13.9 x r2 x min(1, |slope| / MOMO_SLOPE_MIN 1.0).
                 A line that tracks perfectly can sit 13.9 points the wrong side of 50 and still pass.
                 This column prints the level the line actually had to reach at this bar.
  blocked by 50  yes when this gate is what turned the verdict to none. Joe 0820 read ws8r at
                 07:36:20 as "not over 50 ... therefore momentum = false".

THE FOOTER, Joe 0820: "add a footer row that reports the wsf-momoc/momo-none/exhaust state".
It is the reading AT THIS BAR and carries nothing forward:
    domTF is blocking          -> wsf-momo-none.  Joe 0820: "'none' occurs when a trade fires, or
                                  when domTF blocks (overrides excluded)"
    else any of ws4r..ws8r carries momentum   -> wsf-momoc, and the footer names that group
    else any of ws1r..ws3r carries momentum   -> wsf-momoc, and the footer names that group
    else                                      -> wsf-exhaust
Momentum means the verdict is momo or curl - Joe 0817: "(curl or momo) create wsf-momoc".
NOT A STATE MACHINE. Joe's flow is wsf-momoc -> wsf-exhaust -> wsf-momo-none -> wsf-momoc, and five
questions on it are still open: what acquiring wsf-momoc means, whether the all-in-bounds reset
fires momo-none, whether a domTF block is a moment or a stretch, the starting state, and whether one
bar can hold two changes. Until those land this footer reads one bar and holds no history.

NOT REPORTED. The wsf momentum state - momoc, exhaust, momo-none. The three-state flow has five
open questions and nothing here invents it.
"""
import sys
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.momo_gated import curl_gates
from optimus9.analysis.jig import wsf_facing_dr, wsf_dr_lookback, stoch_out_extreme
from build_wsf_setup_model import LTF, HTF

WIN_FROM = '2026-08-04 00:00:00'
DAY      = '2026-08-04'
HI, LO   = 85.0, 15.0
LEVEL_SLACK = 13.9   # momo_core. How far the 50 gate can slacken for a cleanly tracking line
SLOPE_MIN   = 1.0    # momo_core MOMO_SLOPE_MIN, r-units per sample
MOMO_KILL    = 'state'  # which reading of Joe 0820's rule to read back. See build_wsf_line_bar.py
MOMO_FENCE_R = 17       # momo-fence-r, Joe 0820: 100 - 17 = 83 at the top, 17 at the bottom
MOMO_XWOB    = 4        # 5 s bars held outside the fence before an exit counts. Joe 0821
MAGE_KNOB    = 20       # Joe 0823: "{100 - knob:20 fence}" -> the dr fence is 80 / 20
DR_LOOKBACK_S = 180     # Joe 0823: "restrict the lookback to 3 minutes". Owned by
                        # build_dtf_delegation as DDS_LOOKBACK_S; repeated here because this report
                        # reads the line cache directly and does not import that builder.
WMT_TF_LO    = 2        # the weak-mage scan's lowest timeframe. Joe 0821 moved it from 1 to 2
KNOBS = ('kw4_fs21_sn6_hi85_lo15_r20.5_sl1_arc4_sk13.9_cr0.4_'
         f'mk{MOMO_KILL}_mf{MOMO_FENCE_R}_xw{MOMO_XWOB}')
# THE JOIN MUST PIN EVERY KNOB ON BOTH TABLES. Both now hold several knob sets side by side - that
# is what the unique keys are for - so a join that pins only some of them returns one row per
# COMBINATION. Unpinned, this report printed four rows per line.


def _n(v):
    return '' if v is None else f'{float(v):.2f}'


def _i(v):
    return '' if v is None else str(int(v))


def heading(out_fence, slope):
    """Left momo-fence-r -> away. Otherwise the slope's sign against the direction read.

    Joe 0820: "apply the fence to this mech". The test was against the global 85/15 boundary; it is
    now against momo-fence-r, 83/17."""
    if out_fence:
        return 'away'
    return 'toward' if slope > 0 else 'away' if slope < 0 else 'flat'


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    t = sys.argv[1]
    bar = f'{DAY} {t}' if len(t) <= 8 else t
    force = sys.argv[2].lower() if len(sys.argv) > 2 else None

    db = DatabaseManager(**get_db_config()); db.connect()
    sig = db.execute("SELECT wsf_side s, wsf_domtf d FROM ws_fin_9of12 WHERE wsf_utc=%s "
                     "AND wsf_ho_rule='median' AND wsf_line_hcap='ws1b:1'", (bar,), fetch=True)
    if force in ('up', 'down'):
        dr = 1 if force == 'up' else -1
    elif sig:
        dr = int(sig[0]['s'])
    else:
        print(f'  {bar} is not a wsf9of12 signal bar, so it carries no side of its own.')
        print(f'  Re-run with "up" or "down" to pick the read.')
        db.disconnect()
        return 1

    # the three lines over the lookback window ENDING at this bar, so the lookback can run.
    face = db.execute('SELECT wlb_utc t, wlb_g30Mage a, wlb_ws1Mage b, wlb_ws2Mage c '
                      'FROM ws_line_bar WHERE wlb_utc <= %s ORDER BY wlb_utc DESC LIMIT %s',
                      (bar, DR_LOOKBACK_S // 5 + 1), fetch=True)
    face = list(reversed(face))
    rows = db.execute("""SELECT b.wbt_tf tf, b.wbt_r r, b.wbt_mage mg, b.wbt_mage_oob_tol mt,
              b.wbt_weak_mage_tf wmt, l.wflb_verdict u, l.wflb_curl_ends ce, l.wflb_stalled sl, l.wflb_slope sp,
              l.wflb_ungated ung, l.wflb_aligned al, l.wflb_bend_align ba, l.wflb_bendfit bf,
              l.wflb_mfr_out ob, l.wflb_fit fi, l.wflb_level lv, l.wflb_verdict_dwell vdw, l.wflb_last_verdict lv2,
              b.wbt_stoch_now sn, b.wbt_stoch_out so, b.wbt_sat_bars sb, b.wbt_sat_left sl2,
              b.wbt_rsi rsi, b.wbt_rsi_lo rlo, b.wbt_rsi_hi rhi
         FROM wsf_bar_tf b
         JOIN wsf_line_bar l ON l.wflb_utc=b.wbt_utc AND l.wflb_tf=b.wbt_tf AND l.wflb_dr=b.wbt_dr
        WHERE b.wbt_win_from=%s AND b.wbt_utc=%s AND b.wbt_dr=%s AND l.wflb_knobs=%s
              AND b.wbt_wmt_tf_lo=%s ORDER BY b.wbt_tf""",
        (WIN_FROM, bar, dr, KNOBS, WMT_TF_LO), fetch=True)
    if not rows:
        print(f'    no rows banked for {bar}. The dataset covers {DAY} only.')
        db.disconnect()
        return 1

    print(f'\n  BAR {bar}')
    print(f'    a wsf9of12 signal bar: {"yes" if sig else "no"}'
          + (f'   domTF reads {sig[0]["d"]}' if sig else ''))
    print('    read ' + ('upward, so the fence each line can reach is 85'
                         if dr > 0 else 'downward, so the fence each line can reach is 15'))
    wmt = rows[0]['wmt']
    print()
    # THE HEADER IS TWO LINES, Joe 0824: "print the column names on 2 lines so that the report
    # fits in my screen". Each name is split at its own hyphen or space, never mid-word, so no
    # column is renamed. Every column is then as narrow as the widest of its two header halves and
    # its own data, which is what pulls the table in.
    COLS = (('line', '', '<'), ('r', 'value', '>'), ('heading', '', '<'), ('r', 'IB', '<'),
            ('verdict', '', '<'), ('curl', 'dr', '>'), ('wsf-curl', 'mode', '<'),
            ('stalled', '', '<'), ('50', 'gate', '>'), ('blocked', 'by 50', '<'),
            ('last', 'verdict', '<'), ('last-verdict', 'dwell', '>'), ('Mage', 'value', '>'),
            ('lb-mage', 'oob', '<'), ('weak', 'mage', '<'), ('stoch', 'now', '>'),
            ('stoch', 'out', '>'), ('sat', 'clock', '>'), ('sat', 'left', '>'),
            ('RSI', '', '>'), ('RSI', 'lo', '>'), ('RSI', 'hi', '>'))
    cells = []
    for x in rows:
        tf = int(x['tf']); rv = float(x['r'])
        h = heading(bool(x['ob']), float(x['sp']))
        rib = 'yes' if LO < rv < HI else ''
        # the slack the level gate earned at this bar, recomputed from the stored fit
        trk = max(0.0, min(1.0, float(x['fi']) * min(1.0, abs(float(x['sp'])) / SLOPE_MIN)))
        gate = (50 - LEVEL_SLACK * trk) if dr > 0 else (50 + LEVEL_SLACK * trk)
        blocked = '' if int(x['lv']) else 'yes'
        # curl_dr, Joe 0824: "the curl_dr will represent the end of the curl - ie if r was 80 and
        # heading upwards, then the following curl will be curl_dr -1 (the curl has reversed the
        # line's upward travel)". wflb_curl_ends holds 'up'/'down' from the sign of the bend.
        # Joe 0824: "curl_dr prints only on rows where verdict = curl".
        cdr = ('' if x['u'] != 'curl' else
               '+1' if x['ce'] == 'up' else '-1' if x['ce'] == 'down' else '')
        # wsf-curl-mode, named by Joe 0824: "a curl-detection mode that excludes gate 2, so that
        # the curl and its dr can contribute to your modelling". Gate 2 is the one that throws a
        # curl away for bending against dr. Gates 1 and 3 and Joe's momentum-kill all still apply,
        # Joe 0824: "momentum flipping from true to false is part of the line's lifecycle".
        # It prints only where the producer's raw fit said curl - the rows the gates act on.
        # THE GATES ARE NOT RE-IMPLEMENTED HERE. curl_gates() is momo_gated's own, fed the five
        # measurements banked per bar. Proven against all 276,496 banked rows at gate2=True:
        # 0 mismatches with wflb_gated.
        if x['ung'] != 'curl':
            cm = ''
        elif x['u'] != 'curl':
            cm = 'none'            # Joe's momentum-kill already turned it off, before any gate
        else:
            cm = 'curl' if curl_gates(
                {'aligned': bool(x['al']), 'quad': x['ba'] is not None,
                 'quad_aligned': None if x['ba'] is None else bool(x['ba']),
                 'quad_r2': x['bf'], 'quad_why': None}, gate2=False)[0] else 'none'
        cells.append([f'ws{tf}', f'{rv:.2f}', h, rib, x['u'], cdr, cm,
                      'yes' if x['sl'] else '', f'{gate:.2f}', blocked,
                      (x['lv2'] or ''), f"{int(x['vdw'])} s", f"{float(x['mg']):.2f}",
                      'yes' if x['mt'] else '', 'yes' if wmt == tf else '',
                      _n(x['sn']), _n(x['so']), _i(x['sb']), _i(x['sl2']),
                      _n(x['rsi']), _n(x['rlo']), _n(x['rhi'])])

    W = [max(len(t), len(b), *(len(c[j]) for c in cells))
         for j, (t, b, _a) in enumerate(COLS)]
    for line in (0, 1):
        print('    ' + ' | '.join(f'{h[line]:{a}{w}}' for (*h, a), w in zip(COLS, W)).rstrip())
    for c in cells:
        print('    ' + ' | '.join(f'{v:{a}{w}}' for v, (_t, _b, a), w in zip(c, COLS, W)))

    mom = {int(x['tf']) for x in rows if x['u'] in ('momo', 'curl')}
    hi_grp = sorted(t for t in mom if t >= 4)
    lo_grp = sorted(t for t in mom if t <= 3)
    if sig and sig[0]['d'] == 'BLOCKED':
        state, why = 'wsf-momo-none', 'domTF is blocking at this bar'
    elif hi_grp:
        state, why = 'wsf-momoc', 'momentum on ' + ', '.join(f'ws{t}r' for t in hi_grp) + ' (the ws4 to ws8 group)'
    elif lo_grp:
        state, why = 'wsf-momoc', 'momentum on ' + ', '.join(f'ws{t}r' for t in lo_grp) + ' (the ws1 to ws3 group)'
    else:
        state, why = 'wsf-exhaust', 'no r line from ws1 to ws8 carries momentum'
    print(f'    STATE AT THIS BAR: {state}   -   {why}')

    # ----- FOOTNOTES, Joe 0824: "add any pertinent data to the report. it seems that most of them
    # are footnotes. only add data columns if you need to". Every one of these is a reading of the
    # WHOLE board, so none of them is a column. The producers are imported, never restated.
    H = {int(x['tf']): x for x in rows}
    hd = {t: heading(bool(H[t]['ob']), float(H[t]['sp'])) for t in H}
    away = sorted(t for t in H if hd[t] == 'away')
    tow = sorted(t for t in H if hd[t] == 'toward')
    rib = sorted(t for t in H if LO < float(H[t]['r']) < HI)
    tfs = lambda g: ','.join(f'ws{t}' for t in g) if g else '-'
    print()
    print('    FOOTNOTES')

    # 1. the dr the three Mage lines give. Joe 0823: "wsf's dr will be set by the positioing of
    #    gcws30Mage, ws1Mage and ws2Mage - if they are all > {100 - knob:20 fence} then dr = +1",
    #    and "restrict the lookback to 3 minutes". BOTH producers are jig's, and the lookback is
    #    the same one build_dtf_delegation runs - proven identical on all 85 delegation rows,
    #    0 mismatches.
    #    IT REPORTS THE LOOKBACK ANSWER, NOT THE BAR-ONLY TEST. Reading only the bar said "no dr"
    #    on 08-04 03:53:00 while the mechanic had dr +1 from 5 seconds earlier.
    if face:
        f = face[-1]
        live = wsf_facing_dr([[x['a'] for x in face], [x['b'] for x in face],
                              [x['c'] for x in face]], 100 - MAGE_KNOB, MAGE_KNOB)
        lb, lg = wsf_dr_lookback(live, DR_LOOKBACK_S // 5)
        fdr, lag = int(lb[-1]), int(lg[-1])
        # THE LABELS ARE JOE'S, 0825, verbatim: "label them together, like this:
        # 'three-mage-lb: {yes/no}, three-mage-dr: {dr}'".
        head = (f"three-mage-lb: {'yes' if fdr else 'no'}, "
                f"three-mage-dr: {f'{fdr:+d}' if fdr else 'none'}")
        if fdr and lag:
            src = face[len(face) - 1 - lag]
            head += f"   from {str(src['t'])[11:]}, {lag * 5} s back"
        elif fdr:
            head += '   all three outside the fence at THIS bar'
        else:
            head += f'   nothing on one side of the fence in the last {DR_LOOKBACK_S} s'
        print(f'      dr            {head}')
        if fdr and lag:
            print(f"                    at {str(src['t'])[11:]}   gcws30Mage {float(src['a']):.2f}"
                  f"   ws1Mage {float(src['b']):.2f}   ws2Mage {float(src['c']):.2f}")
        print(f"                    at this bar   gcws30Mage {float(f['a']):.2f}"
              f"   ws1Mage {float(f['b']):.2f}   ws2Mage {float(f['c']):.2f}"
              f"   against the {100 - MAGE_KNOB}/{MAGE_KNOB} fence")
        if fdr != 0 and fdr != dr:
            print(f"                    THE BOARD ABOVE IS READ AT dr {dr:+d}, WHICH IS NOT WHAT"
                  f" three-mage-dr GIVES.")
    else:
        print('      dr            gcws30Mage / ws1Mage / ws2Mage are not banked at this bar')

    # 2. Joe's template markers, spec 3.5: ws8r reversing, many aways, many ltf `r IB`s, weak-mage.
    w8 = H.get(8)
    past = (float(w8['r']) - HI) if dr > 0 else (LO - float(w8['r'])) if w8 else None
    print(f"      template      away {len(away)} ({tfs(away)})   toward {len(tow)} ({tfs(tow)})"
          f"   r IB {len(rib)} ({tfs(rib)})")
    print(f"                    LTF away {len([t for t in away if t in LTF])}"
          f"   HTF toward {len([t for t in tow if t in HTF])}"
          f"   (LTF is ws1-ws4, HTF is ws5-ws8, Joe 0824)")
    if w8:
        print(f"                    ws8r {float(w8['r']):.2f} is {abs(past):.2f} "
              f"{'past' if past > 0 else 'short of'} the {HI if dr > 0 else LO:g} fence"
              f"   verdict {w8['u']}   after {w8['lv2'] or 'nothing'}   dwell {int(w8['vdw'])} s")
    print(f"                    weak-mage {'ws' + str(wmt) if wmt else 'NONE'}"
          f"   Mage lines out of bounds {sum(1 for t in H if H[t]['mt'])} of {len(H)}")

    # 3. the stoch reading. jig.stoch_out_extreme - the outgoing reading at an extreme fixes which
    #    way r can still move. Joe 0824: "r has dropped to the ~floor ... and has nowhere to go".
    rise = sorted(t for t in H if stoch_out_extreme(H[t]['so']) > 0)
    fall = sorted(t for t in H if stoch_out_extreme(H[t]['so']) < 0)
    want = 'fall' if dr > 0 else 'rise'
    with_trade = fall if dr > 0 else rise
    print(f"      stoch         r can only RISE on {len(rise)} ({tfs(rise)})"
          f"   r can only FALL on {len(fall)} ({tfs(fall)})")
    print(f"                    a dr {dr:+d} trade needs r to {want}, so {len(with_trade)} of"
          f" {len(H)} lines are mechanically committed to it")
    print()
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
