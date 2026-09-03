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
               IT REPORTS THE LOOKBACK ANSWER. Reading only the bar itself said "no dr" at
               03:53:00 while the mechanic had dr +1 from 5 seconds earlier. It also says plainly
               when the board's dr is not the one the three lines give.
               ONE LINE. Joe 0825: "my label was the complete label. one line of footer real-estate
               is all that is needed". The Mage values, the source bar and the lag are banked in
               dtf_delegation and wsf_mage_oob and none of them is needed to reach a verdict.
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
    x-cross    ON A wsf-exhaust BAR ONLY - the cross that turns the exhaust into a trade signal.
               Joe, spec 1.6, verbatim: "the next action after `wsf-exhaust`: walk forward. if
               ws{weak-mage}x-cross has printed, then create a trade signal". The watched line is
               ws{weak-mage-tf}x and the weak-mage timeframe is RE-READ AT EACH BAR of the walk,
               which is what build_wsf_exhaust_bar.py line 43 does. The moment is the RISING EDGE
               of a cross held XCROSS_XWOB 5 bars - wsf_x_cross latches `fired`, so without the
               rising-edge test a cross already running would be reported as new. NO CAP on the
               walk; Joe named no horizon.

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
                 how cleanly the line tracks: slack = level_slack x r2 x min(1, |slope| /
                 momo_slope_min), both read from the bound bank - see momo_core.level_gate().
                 A line that tracks perfectly can sit 13.9 points the wrong side of 50 and still pass.
                 This column prints the level the line actually had to reach at this bar.
  blocked by 50  yes when this gate is what turned the verdict to none. Joe 0820 read ws8r at
                 07:36:20 as "not over 50 ... therefore momentum = false".

THE STATE READS `wsf-forced-exhaust` when the x-cross forces it. Joe 0826: "let's make it real:
replace wsf-momoc with wsf-forced-exhaust". The conditions are Joe's 0825 ingredient - a line at or
past the fence reading `none`, a HIGHER line holding momo or curl INSIDE the fence, and the crossed
line's OWN x crossing its OWN r (wxc_x_r at XCROSS_XWOB, the banked flag). The report shows the
CONDITION; the walk's one-shot guard lives in build_wsf_walk_events.py and is not repeated here.

THE `trade` FOOTNOTE is signal-level and comes from the x-cross mech at this bar, not from the
slots. Joe 0828: "the slots have a different purpose: they serve at the machine level, not the
signal level". It prints on any wsf-exhaust bar whose x-cross resolves.

THE TRADE SLOTS line follows the state. They belong to the walk, not to one bar, so they are read
from wsf_exhaust_event - the most recent event at or before this bar.
Joe 0828: "I don't need to know about `armed`. what I'm looking for, at a glance, is: how many
trades are open, and when did they open". So a slot prints the bar the TRADE OPENED - the x-cross -
and a free slot prints `-empty-`.
SOURCE MOVED 0828 from wsf_walk to wsf_exhaust_event. Joe sunsetted build_wsf_walk.py and the pool
was ported into build_wsf_walk_events.py.

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
import datetime as dt
from collections import defaultdict
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute import momo_core as MC   # level_gate(): the ONE 50-gate formula, 0903
from optimus9.compute.momo_gated import curl_gates
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.analysis.jig import wsf_facing_dr, wsf_dr_lookback, stoch_out_extreme
from build_wsf_setup_model import LTF, HTF
from build_wsf_walk_events import SIG as WALK_SIG   # the walk owns the knob signature;
                                                    # this report joins to it, never restates it

WIN_FROM = '2026-08-04 00:00:00'
MAX_TF   = 12    # KNOB, mirrored from build_wsf_walk_events. Joe 0826: "wsf is limited to TF12"
DAY      = '2026-08-04'
HI, LO   = 85.0, 15.0
# THE TWO KNOBS THIS FILE USED TO HOLD ARE GONE, 0903. LEVEL_SLACK 13.9 and MOMO_SLOPE_MIN 1.0
# were literals here while build_wsf_walk_events read the shared ones, so the gate printed here and
# the gate the walk applied were different numbers and nothing said so. momo_core.level_gate() now
# owns the formula and both callers use it, so both follow whichever bank is bound.
MOMO_KILL    = 'state'  # which reading of Joe 0820's rule to read back. See build_wsf_line_bar.py
MOMO_FENCE_R = 17       # momo-fence-r, Joe 0820: 100 - 17 = 83 at the top, 17 at the bottom
MOMO_XWOB    = 4        # 5 s bars held outside the fence before an exit counts. Joe 0821
MOMO_STALL_DELAY = 5    # KNOB, Joe 0829: "option 2: create a {knob:5} MOMO_STALL_DELAY
                        # (25 seconds)". 5 bars = 25 s at the 5 s grid. The bars r must hold
                        # off its extrema before `heading` prints away. It REPLACES the stall
                        # test inside heading() - see the docstring there.
                        # NOT IN ANY KNOB SIGNATURE. `heading` is ingredient 4, home
                        # report_wsf_bar, NOT BANKED, so nothing banked reads this. The day a
                        # test reads `heading` it must go into the walk's signature or the
                        # A/B overwrites itself. MINE, STATED.
MAGE_KNOB    = 20       # Joe 0823: "{100 - knob:20 fence}" -> the dr fence is 80 / 20
XCROSS_XWOB  = 5        # the x-cross hold, build_wsf_x_cross.py / build_wsf_exhaust_bar.py
DR_LOOKBACK_S = 180     # Joe 0823: "restrict the lookback to 3 minutes". Owned by
                        # build_dtf_delegation as DDS_LOOKBACK_S; repeated here because this report
                        # reads the line cache directly and does not import that builder.
WMT_TF_LO    = 2        # the weak-mage scan's lowest timeframe. Joe 0821 moved it from 1 to 2
XCROSS_TARGET = 'r'     # KNOB, Joe 0828. 'r' = x crosses its own r. 'race' = Mage, b, boundary
HIGH_TF_GAP   = 15.0    # KNOB, Joe 0828. The r gap under which the H+1 line takes the ungated cross
WMT_TF_HI    = 12       # the weak-mage scan's highest timeframe. Joe 0826: "weak-mage-tf scan
                        # is now TF2 to TF12". It is in wsf_bar_tf's unique key, so it MUST be
                        # pinned in every join here - the ceiling-8 rows are still banked.
KNOBS = ('kw4_fs21_sn6_hi85_lo15_r20.5_sl1_arc4_sk13.9_cr0.4_'
         f'mk{MOMO_KILL}_mf{MOMO_FENCE_R}_xw{MOMO_XWOB}')
# THE JOIN MUST PIN EVERY KNOB ON BOTH TABLES. Both now hold several knob sets side by side - that
# is what the unique keys are for - so a join that pins only some of them returns one row per
# COMBINATION. Unpinned, this report printed four rows per line.


def _n(v):
    return '' if v is None else f'{float(v):.2f}'


def _i(v):
    return '' if v is None else str(int(v))


def extrema(db, bar, dr):
    """`extrema r` and `extrema dwell` per line, Joe 0829: "add the last 2 columns (`lowest r`,
    and `at`) to wsf-model-report. call them `extrema r` and `extrema dwell`".

    THE EXTREME IS THE TRUE ONE, Joe 0829 C7 - the highest or lowest r the line actually printed,
    not the stall lattice's sampled extreme. The two differ: at 10:40:25 the lattice put ws9's
    extreme at 38.19 and the true low was 22.13, and ws11's lattice extreme predated its real low
    by 18 minutes because the lattice sampled past it.

    THE CYCLE IS BOUNDED BY momentum-true, Joe 0829 C4: "a line will lose away status when it is
    tagged as momentum-true (ie, it's travelled far enough start a new cycle)". So the search runs
    from the line's last momo-or-curl bar to this bar.

    dr -1 reads the lowest r, dr +1 the highest - the extreme is on the oob side of the direction.

    MINE, STATED, three of them:
      a line with no momentum-true bar since WIN_FROM starts its cycle at WIN_FROM. That is where
        the data begins; there is nothing earlier to read.
      a line that is momentum-true AT this bar starts its cycle here, so its extrema r is its r
        now and its dwell is 0 s. That is C4 applied to the current bar, not a special case.
      the dwell is seconds, Joe 0829 C8 "agreed", printed like the last-verdict dwell beside it.

    -> {tf: (extrema_r, dwell_seconds, bars_held_off_the_extrema)}
    """
    out = {}
    hist = defaultdict(list)
    for x in db.execute('SELECT wflb_tf tf, wflb_utc t, wflb_r r, wflb_verdict v '
                        'FROM wsf_line_bar WHERE wflb_knobs=%s AND wflb_dr=%s AND wflb_tf<=%s '
                        'AND wflb_utc >= %s AND wflb_utc <= %s ORDER BY wflb_tf, wflb_utc',
                        (KNOBS, dr, MAX_TF, WIN_FROM, bar), fetch=True):
        hist[int(x['tf'])].append((x['t'], float(x['r']), x['v']))
    now = dt.datetime.strptime(bar, '%Y-%m-%d %H:%M:%S')
    for tf, seq in hist.items():
        start = 0
        for k in range(len(seq) - 1, -1, -1):
            if seq[k][2] in ('momo', 'curl'):
                start = k
                break
        seg = seq[start:]
        pick = min(seg, key=lambda z: z[1]) if dr < 0 else max(seg, key=lambda z: z[1])
        # THE HOLD, Joe 0829's MOMO_STALL_DELAY, counted ELAPSE - Joe 0829 chose it over the
        # consecutive-with-reset reading I had built. Bars since the turn, no reset; only a NEW
        # extrema restarts it. A wobble back onto the extrema does not un-happen a turn.
        #
        # I HAD THIS WRONG. I built it on the MOMO_XWOB 4 / wflb_mfr_run precedent, which counts
        # consecutive bars and resets. That hold asks "is the line outside the fence NOW", where a
        # return genuinely cancels the state. This one asks "did the line turn", where it does not.
        # Measured over 08-04, both dr, TF1 to TF12, on 3,064 turns:
        #     reading   printed away   never printed   median lag   worst lag
        #     stall            1,940     1,124 36.7%        0m00s      14m25s
        #     reset            1,815     1,249 40.8%        0m20s      19m40s
        #     elapse           1,961     1,103 36.0%        0m20s       0m20s
        # The reset reading was worse than the stall it replaced on both counts. Elapse beats the
        # stall on both and has no tail at all.
        ex, held, turned = None, 0, False
        for _t, r, _v in seg:
            if ex is None or (r < ex if dr < 0 else r > ex):
                ex, held, turned = r, 0, False   # a new extrema - the line has not turned
                continue
            if turned or ((r > ex) if dr < 0 else (r < ex)):
                turned = True
                held += 1                        # the clock runs from the turn, whatever r does
        out[tf] = (pick[1], int((now - pick[0]).total_seconds()), held)
    return out


def heading(dr, held, extrema_r, momentum_true):
    """Joe 0829, verbatim: "`toward` means the line is heading towards the oob, and `away` means
    that the line has gone as far as it can into oob, printed an extrema, and is now moving `away`
    from the extrema".

    THIS REPLACES A FITTED RULE. The old one read the slope sign and called any line outside
    momo-fence-r `away`. It was mine, fitted to Joe read at 07:36:20, and at 10:40:25 it printed
    the exact inverse of Joe definition on all twelve lines.

    JOE RULINGS, 0829, one per condition:
      C1  the fence is momo-fence-r, not the 85/15 boundary. It fixes which side oob is on.
      C2  "no - it can be away if it heading away from an extrema" - reaching oob is NOT required.
          A line that turned above the fence still reads away; `extrema r` tells you it never
          sprang from oob, which Joe 0829 calls "important information ... it tells us that the
          line does not have the same momentum power as a line that sprang from oob".
      C3  "using `stall` makes the most sense - it is an established mech that we can rely on".
      C4  "a line will lose away status when it is tagged as momentum-true (ie, it is travelled
          far enough start a new cycle)".
      C6  no `flat`: "I have never seen it printed on a exhaust report, so it can not have a
          value-add to the mech".
      C9  the move off the extrema is tested as "r now vs r then", not by the slope.
      C10 `away` needs "a genuine `stalled` event", not one sample past the extreme.

    C10 IS SUPERSEDED. Joe 0829, after seeing the cost: "now I see the downfall of using stall -
    300 seconds consumes a lot of potential profit. if your reading `toward` while it is truly
    heading away, your recipe will be muddied". Measured over 08-04, both dr, TF1 to TF12: of 3,064
    turns, 36.7% never printed away before the cycle reset and 11.9% printed late, median 0m50s and
    worst 14m25s on ws12. Joe chose option 2: "create a {knob:5} MOMO_STALL_DELAY (25 seconds)".
    The stall no longer gates away; a bar hold on the move does. `stalled` stays on the board as
    ingredient 9, it just stops deciding this column.

    THE HOLD, MINE, STATED, on the precedent of MOMO_XWOB 4 and wflb_mfr_run:
      it counts CONSECUTIVE bars off the extrema and resets if r returns to it.
      a new extrema resets it too - a line printing a better extreme has not turned.

    dr -1 puts oob at the bottom, so away is r rising above the extrema; dr +1 is the mirror.

    MINE, STATED: r_now exactly equal to extrema_r has not moved off it, so it reads toward. With
    `flat` gone there is nowhere else for a tie to land."""
    if momentum_true:
        return 'toward'                    # C4 - a new cycle has started
    if extrema_r is None:
        return 'toward'
    return 'away' if held >= MOMO_STALL_DELAY else 'toward'


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    t = sys.argv[1]
    bar = f'{DAY} {t}' if len(t) <= 8 else t
    force = sys.argv[2].lower() if len(sys.argv) > 2 else None

    db = DatabaseManager(**get_db_config()); db.connect()
    # THE BANK. This report reads wsf_line_bar rows, TF1..12, which is one bank; checked, not
    # assumed. It is bound for the whole run because the 50 gate and the curl gates are computed
    # from those banked rows further down.
    _bk = {tf: momo_bank(db, tf) for tf in range(1, 13)}
    _ids = {(b['mech'], b['tf_lo'], b['tf_hi'], b['version']) for b in _bk.values()}
    if len(_ids) != 1:
        raise SystemExit(f'TF1..12 spans {len(_ids)} momentum banks: {sorted(_ids)}. '
                         'One run must sit inside one bank.')
    _CFG = momo_config(_bk[1]); _CFG.__enter__()   # held for the life of main; the name keeps it
    #                                                alive - drop the reference and Python collects
    #                                                it, which runs its finally and unbinds.
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
              AND b.wbt_wmt_tf_lo=%s AND b.wbt_wmt_tf_hi=%s ORDER BY b.wbt_tf""",
        (WIN_FROM, bar, dr, KNOBS, WMT_TF_LO, WMT_TF_HI), fetch=True)
    EX = extrema(db, bar, dr)
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
    COLS = (('line', '', '<'), ('r', 'value', '>'), ('heading', '', '<'),
            ('extrema', 'r', '>'), ('extrema', 'dwell', '>'), ('r', 'IB', '<'),
            ('verdict', '', '<'), ('curl', 'dr', '>'), ('wsf-curl', 'mode', '<'),
            ('stalled', '', '<'), ('50', 'gate', '>'), ('blocked', 'by 50', '<'),
            ('last', 'verdict', '<'), ('last-verdict', 'dwell', '>'), ('Mage', 'value', '>'),
            ('lb-mage', 'oob', '<'), ('weak', 'mage', '<'), ('stoch', 'now', '>'),
            ('stoch', 'out', '>'), ('sat', 'clock', '>'), ('sat', 'left', '>'),
            ('RSI', '', '>'), ('RSI', 'lo', '>'), ('RSI', 'hi', '>'))
    cells = []
    for x in rows:
        tf = int(x['tf']); rv = float(x['r'])
        exr, exd, exheld = EX.get(tf, (None, 0, 0))
        h = heading(dr, exheld, exr, x['u'] in ('momo', 'curl'))
        rib = 'yes' if LO < rv < HI else ''
        # the slack the level gate earned at this bar, recomputed from the stored fit
        gate = MC.level_gate(x['fi'], x['sp'], dr)
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
        cells.append([f'ws{tf}', f'{rv:.2f}', h,
                      (f'{exr:.2f}' if exr is not None else '-'), f'{exd} s',
                      rib, x['u'], cdr, cm,
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

    V = {int(x['tf']): x['u'] for x in rows}
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
        # THE TEXT NAMES THE RANGE ACTUALLY TESTED, not a fixed ws1-ws8. The ladder ceiling
        # moved to TF12 on Joe 0826 and a hardcoded string would state something untrue.
        _lo, _hi = (min(r['tf'] for r in rows), max(r['tf'] for r in rows)) if rows else (1, 8)
        state, why = 'wsf-exhaust', f'no r line from ws{_lo} to ws{_hi} carries momentum'
    # THE x-CROSS FORCED wsf-exhaust. Joe 0828's ungated-cross gate, verbatim:
    #   -if any TF prints a x-cross while an r line is outside of momo-fence-r
    #   --gate the cross, hold the signal
    #   --tag the highest TF that is outside of momo-fence-r
    #   --if ws{highest_TF}r - ws{highest_TF +1}r < 15 ... then ws{highest_TF +1}x will print the
    #     ungated cross  --ELSE ws{highest_TF}x will print the ungated cross
    #   --if the the TF holding the gated x-cross == the TF designated to print the ungated cross,
    #     then the ungated cross is print the held x-cross
    # The gap is ABSOLUTE and ws{H+1} must be momentum-true - both Joe 0828.
    # REPLACED 0828. The 0825 three-condition test - P past the fence reading none, a HIGHER holder
    # inside the fence, P's own x crossing its own r - is gone. Joe validated the gate alone on all
    # 24 of his forced rows: "all 24 rows are perfect ... bake it".
    #
    # ONE BAR CANNOT SEE A HELD CROSS. The walk carries `pending` across bars, so a cross gated at
    # an earlier bar and released here is invisible to a single-bar read. This prints the
    # release-at-the-gated-bar case only, which is what the walk's own trace shows at most events.
    R = {int(x['tf']): float(x['r']) for x in rows}
    out = [tf for tf in R if V.get(tf) == 'none' and (R[tf] >= HI if dr > 0 else R[tf] <= LO)]
    ins = [tf for tf in R if V.get(tf) in ('momo', 'curl')
           and not (R[tf] >= HI if dr > 0 else R[tf] <= LO)]
    xc = {int(x['tf']): (int(x['f'] or 0) if XCROSS_TARGET == 'r' else (1 if x['w'] else 0))
          for x in db.execute('SELECT wxc_tf tf, wxc_x_r f, wxc_race_won w FROM wsf_x_cross '
                              'WHERE wxc_utc=%s AND wxc_dr=%s AND wxc_xwob=%s',
                              (bar, dr, XCROSS_XWOB), fetch=True)}
    xtfs = sorted(tf for tf in R if xc.get(tf))
    OB = {int(x['tf']): int(x['ob'] or 0) for x in rows}   # wflb_mfr_out, the momo-fence-r flag
    outside = sorted(tf for tf in R if OB.get(tf))
    forced, why_gate = None, None
    if xtfs and outside:
        h = max(outside)
        top = max(R)
        if h >= top:
            des, why_gate = h, f'ws{h} is the ceiling'
        else:
            ra, rb = R.get(h), R.get(h + 1)
            gap = None if ra is None or rb is None else abs(ra - rb)
            mom = V.get(h + 1) in ('momo', 'curl')
            if gap is not None and gap < HIGH_TF_GAP and mom:
                des = h + 1
                why_gate = (f'|ws{h}r - ws{h+1}r| = {gap:.2f} under {HIGH_TF_GAP:g} '
                            f'and ws{h+1}r holds momentum')
            else:
                des = h
                why_gate = (f'|ws{h}r - ws{h+1}r| = {gap:.2f} at or over {HIGH_TF_GAP:g}'
                            if gap is not None and gap >= HIGH_TF_GAP
                            else f'ws{h+1}r has no momentum')
        if des in xtfs:
            forced = des
    if forced is not None:
        state = 'wsf-forced-exhaust'
        why = (f'ws{forced}x printed the ungated cross. highest line outside momo-fence-r is '
               f'ws{max(outside)}; {why_gate}. ' + why)
    print(f'    STATE AT THIS BAR: {state}   -   {why}')

    # THE TRADE SLOTS, Joe 0828. Read from wsf_exhaust_event - the most recent event at or before
    # this bar. A slot prints the bar the trade OPENED; `-empty-` when the slot is free.
    # THE LATEST RUN AT THIS KNOB SIGNATURE ONLY. `wee_run` restarts at 1 for every signature -
    # the walk allocates it as MAX(wee_run) WHERE wee_knobs = SIG - so MAX(wee_run) on its own
    # picks the highest number across ALL signatures, which is a different walk. Joe's standing
    # rule: every knob that changes rows goes in the unique key AND in every summary query.
    w = db.execute('SELECT wee_trade1_utc a, wee_trade1_tf af, wee_trade2_utc b, wee_trade2_tf bf '
                   'FROM wsf_exhaust_event WHERE wee_utc <= %s AND wee_knobs = %s '
                   'AND wee_run = (SELECT MAX(wee_run) FROM wsf_exhaust_event WHERE wee_knobs = %s) '
                   'ORDER BY wee_utc DESC, wee_seq DESC LIMIT 1',
                   (bar, WALK_SIG, WALK_SIG), fetch=True)
    t1, f1, t2, f2 = (w[0]['a'], w[0]['af'], w[0]['b'], w[0]['bf']) if w else (None, None, None, None)
    cell = lambda u: (str(u)[11:] if u else '-empty-')
    print('    ' + '-' * 43)
    print(f"    | {'trade 1':^17} | {'trade 2':^17} |")
    print('    ' + '-' * 43)
    print(f"    | {cell(t1):^17} | {cell(t2):^17} |")
    print('    ' + '-' * 43)

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
        # ONE LINE, AND THE LABEL IS JOE'S COMPLETE LABEL, 0825 verbatim: "my label was the
        # complete label. one line of footer real-estate is all that is needed:
        # 'three-mage-lb: {yes/no}, three-mage-dr: {dr}'". The Mage values, the source bar and the
        # lag are all banked elsewhere and none of them is needed to reach a verdict.
        head = (f"three-mage-lb: {'yes' if fdr else 'no'}, "
                f"three-mage-dr: {f'{fdr:+d}' if fdr else 'none'}")
        if fdr and fdr != dr:
            head += f'   BOARD READ AT dr {dr:+d}'
        print(f'      {head}')
    else:
        print('      three-mage-lb: no, three-mage-dr: none   (the three lines are not banked here)')

    # 2. Joe's template markers, spec 3.5: the ceiling line reversing, many aways, many ltf
    #    `r IB`s, weak-mage.
    #    THE CEILING LINE IS READ FROM THE BOARD, NOT HARDCODED. It was ws8 while TF8 was the
    #    ceiling; Joe 0826 moved the ladder to TF12, so a fixed ws8 named the wrong line.
    top = max(H) if H else None
    w8 = H.get(top)
    past = (float(w8['r']) - HI) if dr > 0 else (LO - float(w8['r'])) if w8 else None
    print(f"      template      away {len(away)} ({tfs(away)})   toward {len(tow)} ({tfs(tow)})"
          f"   r IB {len(rib)} ({tfs(rib)})")
    print(f"                    LTF away {len([t for t in away if t in LTF])}"
          f"   HTF toward {len([t for t in tow if t in HTF])}"
          f"   (LTF is ws{LTF[0]}-ws{LTF[-1]}, HTF is ws{HTF[0]}-ws{HTF[-1]}, Joe 0824)")
    if w8:
        print(f"                    ws{top}r {float(w8['r']):.2f} is {abs(past):.2f} "
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


    # 4. the x-cross that turns a wsf-exhaust into a trade signal. Joe, spec 1.6, verbatim:
    #    "the next action after `wsf-exhaust`: walk forward. if ws{weak-mage}x-cross has printed,
    #    then create a trade signal". Printed ONLY on a wsf-exhaust bar, because that is the state
    #    his rule starts from.
    #    THE WATCHED LINE IS ws{weak-mage-tf}x, AND THE TIMEFRAME IS FIXED AT THIS BAR.
    #    Joe 0828, ruling on the two readings: "reads weak-mage-tf at the exhaust bar and watches
    #    that line forward -- this is the correct option". The walk does the same.
    #    CORRECTED 0828. This query previously re-read the weak-mage timeframe at every forward
    #    bar and took the first bar where the crossing line happened to match, which named ws2x at
    #    00:25:15 where the walk named ws12x at 00:15:10 from the same data.
    #    THE MOMENT IS THE RISING EDGE of a cross held XCROSS_XWOB bars: the first bar where the
    #    race has a winner and the bar before it did not. wsf_x_cross latches `fired`, so without
    #    the rising-edge test a cross already running would be reported as new.
    #    NO CAP ON THE WALK. Joe named no horizon; the search runs to the end of the tape.
    # BOTH EXHAUST STATES. wsf-forced-exhaust is a wsf-exhaust that the x-cross declared, so it
    # arms the weak-mage line exactly the same way. The guard read only 'wsf-exhaust', which
    # silently dropped the x-cross and trade footnotes on every forced event.
    if state in ('wsf-exhaust', 'wsf-forced-exhaust'):
        # the weak-mage timeframe AT THIS BAR. NULL is Joe's rule C: watch ws2x instead.
        # Joe 0817 as corrected 0826: "if weak-mage-tf == None and domTF state is FREE, fire a
        # trade signal on the next ws2x-cross".
        wm_row = db.execute('SELECT wbt_weak_mage_tf w FROM wsf_bar_tf WHERE wbt_utc=%s '
                            'AND wbt_dr=%s AND wbt_tf=1 AND wbt_wmt_tf_lo=%s AND wbt_wmt_tf_hi=%s',
                            (bar, dr, WMT_TF_LO, WMT_TF_HI), fetch=True)
        watch = int(wm_row[0]['w']) if wm_row and wm_row[0]['w'] else 2
        route = 'weak-mage' if wm_row and wm_row[0]['w'] else 'rule C, no weak-mage'
        # BIG-HAMMER, Joe 0829: "if wsf-forced-exhaust fires, then the trade prints at the same
        # time". On a forced bar the cross IS the exhaust, so there is nothing to scan forward for.
        # The line is the designated one from the gate above, Joe 0829: "the trade rides the
        # designated line that created the wsf-forced-exhaust". weak-mage-tf is still read and
        # printed in the board's `weak mage` column - Joe 0829: "weak-mage is decoration only when
        # a forced exhaust happens".
        if forced is not None:
            print(f"      x-cross       ws{forced}x crossed its {XCROSS_TARGET} target at "
                  f"{bar[11:]}, 0m00s after this bar   ->  TRADE SIGNAL   (big-hammer)")
            print(f"      trade         opened {bar[11:]} on ws{forced}x-cross")
            wmt = int(wm_row[0]['w']) if wm_row and wm_row[0]['w'] else None
            print(f"      weak-mage     {('ws' + str(wmt)) if wmt else 'NONE'}"
                  f"   decoration only on a forced exhaust - big-hammer took the signal")
            _bh = True
        else:
            _bh = False
        xr = [] if _bh else db.execute("""SELECT wxc_utc u, wxc_tf tf, wxc_race_won won FROM wsf_x_cross
            WHERE wxc_dr=%s AND wxc_xwob=%s AND wxc_tf=%s AND wxc_utc >= %s
            ORDER BY wxc_utc""", (dr, XCROSS_XWOB, watch, bar), fetch=True)
        fired = None
        prev_won = None
        for k, y in enumerate(xr):
            if y['won'] is not None and (k == 0 or prev_won is None):
                if k > 0 or str(y['u']) != bar:      # a cross already standing at this bar is not new
                    fired = y
                    break
            prev_won = y['won']
        if fired:
            gap = int((fired['u'] - dt.datetime.strptime(bar, '%Y-%m-%d %H:%M:%S')).total_seconds())
            print(f"      x-cross       ws{fired['tf']}x crossed its {fired['won']} target at "
                  f"{str(fired['u'])[11:]}, {gap // 60}m{gap % 60:02d}s after this bar"
                  f"   ->  TRADE SIGNAL   ({route})")
            # THE TRADE, Joe 0828: "for the footnote only, I want to capture the trade data as soon
            # as the x-cross mech has produced a timestamp, when the event is 'exhaust'. ie before
            # the mech knows anything about slot information -- that's where I'll look for the
            # trade data that matches an exhaust event. the slots have a different purpose: they
            # serve at the machine level, not the signal level".
            # SO IT IS SOURCED FROM `fired` ABOVE, NOT FROM THE SLOT COLUMNS. It prints on any
            # wsf-exhaust bar whose x-cross resolves, whether or not the walk banked an event there.
            print(f"      trade         opened {str(fired['u'])[11:]} on ws{fired['tf']}x-cross")
        elif not _bh:
            print(f'      x-cross       no cross on ws{watch}x to the end of the tape   ({route})')
            print('      trade         none - the x-cross mech produced no timestamp')
    print()
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
