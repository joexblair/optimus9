"""fdm2-diag1, THE r-pred WEB UI - HIS 1111 *"name the webUI report: fdm2-diag1"*, banked 2026-11-12. Joe 1109: *"I want to access this -1/+1 r-pred data in a dhtml webUI"*.

HIS SPEC, 1109:
    the rows      *"the data will be anchored on closed-prev ws1 bars"* - one row per ws1 bar
    the cells     *"the r-pred data will be emerging based"* - predict_breach on EMERGING r, m and Mage
    the box       15 columns: the ws1 time, then one per wsf line, *"wsf = gcws15 to ws12"*. -1 and +1
                  are coloured, the headers are fixed, the rows update as the mouse wheel scrolls
    the cache     *"an ever-evolving cache of the rpred data, so that a) we don't bog the ui down with too
                  much data at once, and 2) so that the data is available immediately"*
    the calendar  *"click on any day, and scroll from the beginning of the day that I click on"*

HIS ANSWERS, 1109:
    the row time  the ws1 bar's OPEN - the 00:12 row is the bar 00:12:00 .. 00:12:55
    the cell      the emerging value at the 5 s bar where closed-prev first shows that ws1 bar, 00:13:00
                  for the 00:12 row
    the colours   -1 red, +1 green
    the days      the fixed tape

HIS 1109 ADDITION, two columns on the right:
    *"col1: the sum of the r-pred decisions from ws13 to ws20"* / *"col2: the same for ws21 to ws30"*, read
    the same way as every other cell. *"for these 2 columns only, the coloring is red for <0, green for >0
    and orange for 0"*.

A MISSING INPUT READS 0. predict_breach returns 0 when r, m or Mage is NaN - every line's warm-up at the
tape's start (ws30 runs to 2026-07-03 06:28:00) and 3 rows where m is NaN mid-tape. That is the producer's
own output, shown as it comes. HIS 1109 ANSWER: keep 0 - no mark, and the sums count them as 0.

THE SIDE RADIO IS NOT BUILT. He asked for it only *"if the side is required"*; predict_breach returns
+1 (high) and -1 (low) in one read, so both print at once.

THE CACHE, two halves:
    the server    computes the whole matrix once at start, ~2 s, and holds it in memory - no disk cache,
                  so a line rebuild can never be served stale. 136,079 rows x 17 lines, int8.
    the browser   fetches BLOCK rows at a time, prefetches AHEAD blocks in the scroll direction (and
                  one behind), and drops the least recently used blocks past KEEP. Only the rows on
                  screen are in the page. A calendar day prefetches its blocks when the pointer is over it.

THE LAST ws1 BAR ON THE TAPE HAS NO ROW: its print bar, the 5 s bar after it, is past the tape's end.

HIS 1109 TOWARDS/AWAY, baked in: *"the output of towards/away will be baked into the r-pred webUI. for each row,
for each field, print TO or AW below the number, in a bold font."* and *"use a slighty lower font (eg the same size
as the weekdays above the calenders) for the summary ws13 and ws21 fields, print this "TO:x  AW:x"*. The states
come from ../../1109_towards_away/towards_away.py, read at the SAME print bar as the r-pred cell above them. Only
ws1..ws30 carry a state (his 1110 add ws1-3; 10A was ws4..ws30), so gcws15 and gcws30 print no TO/AW. A row before the first
pseudo trade opens has no target-side, so it prints none either.

HIS 1109 ROUNDS 2 AND 3: TO/AW at 10 px like the sum labels; the time cell 20% red for a LOW target-side and 20% green
for HIGH; *"append `(inf)` or `(exf)` to the `TO` and `AW` labels (example "TO(exf)") to denote if a line is infence
or exfence"* - ex-20/80 on the target-side by the banked reader the towards/away mech uses. The build notes are
section 7 of docs/octo-freedom/1109_towards_away.md.

HIS 1110: *"for the webUI - any r-pred signal that prints on an AW signal will need to print the fields background at
55% opaque"* - a -1 or +1 line cell whose own line reads AW(inf) or AW(exf) at that bar: red or green at 55%, not 100%.
The sums carry no single TO/AW state, so they are unchanged.

HIS 1110 CROSS ROW: *"the e-crosses and the x-crosses need to be printed on a row under the AW/TO data.  if the target
is low side, print only the crossovers. inverted for high side.  center the text.  the format will be "X↑, ↓X, ↓E, ↑E".
if ws{TF}e and ws{TF}x  fire on the same ws1 bar, print them together in the label with 4 spaces between them"*. His
answer on the x-cross: raw, no hold. Both are jig.e_race_wins over the whole tape, per side - the race lift-off's e path
uses (v4_lift_e.race: the 15/85 boundary, closed-prev ws{TF}Mage, closed-prev ws{TF}r; first line crossed wins; it
re-opens on crossing back; no hold) - with ws{TF}e or ws{TF}x (emerging) as the crossing line. A cross prints on the row
of the ws1 bar it lands in, [open, open + 60 s), in the direction of the row's target-side (the time cell's colour).
MINE: X before E in the joined label, the race over the whole tape (lift-off's, not re-opened at a trade's open), the
ws1..ws15 cells only (the cells that carry TO/AW).

HIS 1110: *"change the x/e cross row to a non-bright yellow font"* - dark yellow, #a68a00 light / #c9a83a dark (MINE, the
shades) - and *"make a row highlighted if I click on that row"*: a 16% blue tint and a 2 px blue outline. MINE: one row
at a time, a click on another row moves it, a click on the same row clears it; it lives in the page, not across a reload.

HIS 1110: *"for the webUI, drop the table that starts with"* the a-row line, *"so that the data frame can be bigger"*.
The legend table is gone from the page and from /meta. MINE: the data box takes the rest of the window under the
calendar and the status line (it was 68% of the window), never under 320 px.

HIS 1110: *"now I need to see when a TF flips from TO to AW"* / *"for those 2 fields in 1257, brighten the AW row"* /
*"this is a one time application, ie the 'AW's in the following rows are treated normally"*. A ws1..ws15 cell whose line
reads AW on its row and TO on the row before prints its AW text white (black in light mode) - his answer "White
text" - on that row only. A -1/+1 cell's text is already white, so a flip there looks the same (4,848 of 34,149 flip
cells, 1110 count). MINE: the flag is made in the server, +4 on the cross code, so a row at the edge of a 12 h
block still sees the row before it.

HIS 1110: *"make a place holder line for the x/e cross row,  if there is no x/e data available"* / *"this is so that
the row's 3 datasets are horizointally aligned"*. Every data cell prints three lines - the number, the TO/AW line,
the cross line - with a blank line where one has nothing. MINE, from his aligned goal: gcws15 and gcws30 also get a
blank TO/AW line and the two sums a blank cross line, so every number sits on the same line across a row.

HIS 1111 COLUMNS: *"make ws13,ws14,ws15 their own columns, and populate them with the same datasets"* - r-pred,
TO/AW with (inf)/(exf), the cross line, the 55% background and the TO -> AW flip, read as for ws1..ws12. *"the last 2
columns will now be ws16-22 and ws23-30"*, labelled without "sum" *"to make the columns thinner"*: -7..+7 and
-8..+8. *"the gcws15 to ws15 columns stay the same width as they are now"* - 72.36 px, their width at the 1110
page's 1420 px cap (measured, headless Chrome). *"ws1 time can drop the year"* - the time cell prints MM-DD HH:MM:SS.
MINE: the two sum columns take the same 72.36 px (their widest text, "TO:8  AW:8", is 52 px); the time column
is 116 px, its text plus the 32 px of room it had at 150 px; the page widens to hold the table. The 1109 control
still checks gcws15..ws12 alone.

HIS 1111: *"the frame has a horizontal scroll bar - that can be dropped"* / *"I've tested on multiple resolutions
and the bar is still there"*. The box never scrolls sideways. gcws15..ws15 stay 72.36 px; the time column takes
what is left (94 px at least) and the two sums give way next (56 px at least), so the table always fills the box
exactly and no pixel rounding can push it over. MINE: below that (a box under 1,436 px) the right edge is cut off.
*"make the r-pred field's AW/TO inf/exf text grey, unless that field is reporting a AW flip"* - every TO/AW
line prints grey, the 0 cells' grey, on a -1/+1 cell too; only the flip prints white (black in light mode).

HIS 1111 M-no-rev: *"add a column between ws15 and ws16-22 that shows when a target-side oob line has not reversed"*,
labelled M-no-rev, *"and the field will print the **highest** TF"* as ws{TF}; *"if there is no Mage qualifying, don't
print anything in the field"*. His answers: ws1..ws30Mage, and the rule is the one his 1111 table of every change from
2026-09-21 15:44:00 used - m_no_rev has it. MINE: the TF prints on the number line (blank TO/AW and cross lines keep
the row aligned), weight 600, a separator line on both sides; the column gives way with the sums, to 68 px at least.
*"if the field is populated, add the line's value to the text, eg "ws23:95.2"* - the line's CLOSED-PREV value at the
row's print bar (the value the oob test reads), 1 dp as his example. Its widest text is 65.0 px, so the column's least
width is 68 px and the table's 1,504 px (1,436 before M-no-rev); a narrower box cuts off the right edge.
*"update the x and e cross row:  make the text bold (and brighter if possible)"* - it was bold 700 already; now 900,
and dark mode #c9a83a -> #ecc94b (MINE, the shade). Light mode keeps #a68a00: a lighter yellow on white reads worse.
HIS 1111 *"in the summary columns (16-22 and 22-30)"*: *"if any of the individual lines are printing TO(exf), print
"TO(exf)" under the TO:x AW:x row"* - a line reads TO(exf) as a ws1..ws15 cell prints it (TO, and ex-20/80 on the
target-side at the print bar); the sum cell's third line, blank when none of its lines does. MINE: the TO:x AW:x
line's style (10 px, weight 700, the cell's white text), not the cross row's yellow.

HIS 1112 PIVOT BUTTON: *"I want a button at the top (on the right of the calenders), to toggle an offset in the UI.
clikcing the button will move the pivots forward 15 minutes - eg 09-21 1616 becomes 09-21 1631, and return to the
current state when I click the button again"*. The pivots are the ws2Mage pivots that make the pseudo trades (his
example is the 2026-09-21 16:17:15 HIGH pivot). With the button on, every pivot is PIV_SHIFT (15 min) later, so every
pseudo trade opens and closes 15 min later on the same side and towards/away runs again on those trades: the time
cell's colour, TO/AW and (inf)/(exf), the sums' TO:x AW:x and TO(exf), the cross row's side, the TO -> AW flip and
M-no-rev all follow. The r-pred numbers do not read the pseudo trade and stay as they are (asserted). The server
builds both states at start-up; the page keeps each state's blocks apart and the button changes no scroll position -
*"if you can make it that the toggle doesn't change the visible timestamp rows positioning inside the frame"*.
MINE: the label "pivots +15 min", blue when on like the selected day; the last trade still closes at the tape's end.

HIS 1112 TOWARDS/AWAY UPDATE: *"I want to see the flip from TO to AW based on the x and e cross."* No page change: the
TO/AW codes come from towards_away.run, which now carries the 50 reset, the excursion sample on e and x, the void
values, the row rule and the x/e path (spec section 12). Both pivot states read it.

usage: rpred_ui.py [port]   then open http://127.0.0.1:<port>
"""
import io
import json
import os
import sys
import time

import numpy as np

V4 = '/home/joe/thecodes/docs/octo-freedom/1022_v4'
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, V4)
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
os.chdir(V4)                                    # the tape is cwd-sensitive - every run prints its bar count
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    import v4_rcfg_sweep as RS
    import v4_live_lines as LL
    import ln
    from optimus9.compute.breaching_line import predict_breach
    sys.path.insert(0, os.path.join(os.path.dirname(V4), '1109_towards_away'))
    import towards_away as TA
    import v4_lift_e as LE
    import v4_ws_e as WSE
    import v4_closed_prev as CP
    import v4_knobs as K
    from optimus9.analysis import jig as JIG
finally:
    sys.stderr = _e
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8788
if __name__ == '__main__':
    #   A TAKEN PORT FAILS IN A SECOND, NOT AFTER THE ~50 s BUILD. As the o9-rpred-ui service (Restart=always) a
    #   late failure would rebuild every few seconds while another process holds the port.
    import socket
    _sk = socket.socket()
    _sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        _sk.bind(('127.0.0.1', PORT))
    except OSError as _e:
        raise SystemExit('port %d is in use (%s) - not building' % (PORT, _e))
    finally:
        _sk.close()
LINES = ['gcws15', 'gcws30'] + ['ws%d' % t for t in range(1, 16)]      # HIS 1109 wsf, + ws13..ws15 HIS 1111
SUMS = [('ws16-22', range(16, 23)), ('ws23-30', range(23, 31))]   # HIS 1111 two right columns (1109: ws13-20, ws21-30)
CONTROL_FLAGGED = 257295        # 1109 measurement: the 14 wsf columns' cells at -1 or +1, whole tape
CONTROL_COLS = 14               # the control reads gcws15..ws12, the first 14 columns, alone
MNR_LABEL = 'M-no-rev'          # HIS 1111 column label, between ws15 and ws16-22
MNR_TOP = 30                    # HIS 1111 answer: ws1..ws30Mage, not the ladder's 33
STRIDE = len(LINES) + len(SUMS) + len(LINES) + 2 * len(SUMS) + len(LINES) + len(SUMS) + 4   # bytes per row: r-pred,
#   the TO/AW codes, the TO/AW counts, the cross codes (HIS 1110: 1 X, 2 E, 3 both, on the row's target-side; +4 the
#   line reads AW on this row and TO on the row before, HIS 1110 TO -> AW flip), per sum the count of its lines
#   reading TO(exf) (HIS 1111), the M-no-rev TF (HIS 1111, 0 none),
#   its line's closed-prev value x 10 as an int16 in two bytes (low byte first), then the pseudo trade's target-side at the row's read bar: -1 LOW, +1 HIGH, 0 no trade


PIV_SHIFT = 15                  # minutes - HIS 1112 button: *"move the pivots forward 15 minutes"*
OFFS = (0, PIV_SHIFT)           # the page's two states: the pivots as found, and every pivot PIV_SHIFT later


def m_no_rev(sps, prt):
    """HIS 1111 M-no-rev. -> [(int8 [rows], int16 [rows])], one per target-side array in sps: the highest TF whose
    Mage qualifies at the row's print bar, 0 = none, and that line's CLOSED-PREV value there x 10 (HIS 1111 *"add
    the line's value to the text"*, his example 1 dp), 0 where no TF prints. The lift-off reads do not depend on
    the target-side, so both of the page's states share them.

    A ws{TF}Mage, ws1..ws30, qualifies on a row when, at the row's print bar:
      oob       its CLOSED-PREV value is at or beyond 85 high / 15 low on the row's target-side (the time cell's
                colour). No pseudo trade open, no target-side, nothing prints
      the cross its cross INTO oob is the first bar of its current closed-prev oob run. The cross back to ib has
                no bearing (HIS 1111)
      reversal  no lift-off reversal printed between the cross and the print bar. The lift-off is jig.lift_off on
                the EMERGING Mage line over the whole tape - one unbroken rolling window - at the banked LIFT_*
                knobs with no e path, the call every Mage reader makes. A reversal counts from its KNOWABLE bar,
                the end of its 40 s hold (lift_stamp), at or after the cross - HIS 1111: build it *"based on that
                table's output"*, the 1111 table of every change from 2026-09-21 15:44:00, which read it that way
    """
    idx = np.arange(ln.N)
    res = [[np.zeros(len(prt), np.int8), np.zeros(len(prt), np.int16)] for _ in sps]
    for t in range(1, MNR_TOP + 1):               # ascending, so the highest qualifying TF is the one left
        em = np.asarray(ln.line('ws%dMage' % t), float)
        cp = CP.series(em, t * 60)
        for sd in (+1, -1):
            with np.errstate(invalid='ignore'):
                oob = cp >= K.OOB_HI if sd > 0 else cp <= K.OOB_LO
            start = oob & ~np.concatenate([[False], oob[:-1]])
            cross = np.where(oob, np.maximum.accumulate(np.where(start, idx, -1)), -1)
            raw = np.asarray(JIG.lift_off(em, sd, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL, K.LIFT_WOB), int)
            st = np.asarray([K.lift_stamp(int(b)) for b in raw], int)
            k = np.searchsorted(st, idx, side='right') - 1     # the last reversal knowable at or before each bar
            last = np.where(k >= 0, st[np.clip(k, 0, None)], -1)
            assert (last <= idx).all(), 'a reversal is read before it is knowable'
            un = (oob & (last < cross))[prt]
            for r, sp in zip(res, sps):
                q = (sp == sd) & un
                r[0] = np.where(q, t, r[0]).astype(np.int8)
                v10 = np.round(np.where(q, cp[prt], 0.0) * 10.0)
                assert (np.abs(v10) < 32767).all(), 'a Mage value x 10 does not fit an int16'
                r[1] = np.where(q, v10, r[1]).astype(np.int16)
    return [tuple(r) for r in res]


def build():
    """-> (row open ms [n], {offset minutes: [n, STRIDE] int8 - r-pred per line, then the two sums, then the rest}).
    Row i is the ws1 bar opening at t0 + 60 s * i. The r-pred bytes are the same in both; every byte that reads the
    pseudo trade (its target-side, towards/away, the cross row's side, M-no-rev) is built per offset."""
    ts = np.asarray(ln.ts, np.int64)
    assert (np.diff(ts) == 5000).all(), 'the 5 s grid has a gap - a row would not be one ws1 bar'
    E = RS.load((RS.K0, RS.R0, RS.S0))           # fdm2's emerging r lines, ws1..ws30

    def rpred(name):
        if name.startswith('gc'):                # ln.line multiplies the digits by 60, so the sub-minute lines
            r, m, M = (np.asarray(LL.sub_line(name + s), float) for s in ('r', 'm', 'Mage'))
        else:
            r = np.asarray(E[int(name[2:])], float)
            #   CONTROL: fdm2's r is the stored ws r line, exactly
            assert np.array_equal(r, np.asarray(ln.line(name + 'r'), float), equal_nan=True), name
            m, M = np.asarray(ln.line(name + 'm'), float), np.asarray(ln.line(name + 'Mage'), float)
        return predict_breach(r, m, M)

    first = np.flatnonzero((ts % 60000) == 0)    # each ws1 bar's first 5 s bar
    first = first[first + 12 < ln.N]             # its print bar, 12 five-second bars on, must be on the tape
    assert (np.diff(ts[first]) == 60000).all(), 'a ws1 bar is missing - row i would not be t0 + 60 s * i'
    prt = first + 12                             # HIS ANSWER: the cell is the value where closed-prev shows it
    assert (ts[prt] - ts[first] == 60000).all()
    base = [rpred(name)[prt] for name in LINES]
    for _, tfs in SUMS:                          # the same read, summed: -7..+7 and -8..+8, fits int8
        base.append(np.sum([rpred('ws%d' % t)[prt].astype(int) for t in tfs], 0))
    LN, piv, trades, ST, det = TA.build()
    print('towards/away: %d ws2Mage pivots, %d pseudo trades, first opens %s'
          % (len(piv), len(trades), ln.U(trades[0][0])))
    #   HIS 1110 CROSS ROW: the e and x race wins per side over the whole tape, each put on the row of the ws1 bar it
    #   lands in. They do not read the pseudo trade, so both states share them; the row's target-side picks
    #   which side prints - crossovers LOW, crossunders HIGH
    XC = {}
    for name in LINES:
        t = int(name[2:]) if name.startswith('ws') else 0
        if t not in ST:
            continue
        XC[name] = {}
        for sd in (-1, +1):
            race = LE.race(t, sd)
            c = np.zeros(len(prt), np.int8)
            for bit, line in ((1, np.asarray(ln.line('ws%dx' % t), float)), (2, WSE.lines()[t])):
                wins = np.asarray([b for b, _ in JIG.e_race_wins(line, race, sd)], np.int64)
                row = (wins - first[0]) // 12
                row = row[(wins >= first[0]) & (row < len(prt))]
                c[row] |= bit
            XC[name][sd] = c
    #   HIS 1112 *"move the pivots forward 15 minutes"*: every ws2Mage pivot PIV_SHIFT later, so every pseudo trade
    #   opens and closes PIV_SHIFT later on the same side, and towards/away runs again on those trades. The last
    #   trade still closes at the tape's end
    STATES = []
    for off in OFFS:
        k = off * 12                             # 5 s bars
        tr = [(o + k, min(c + k, ln.N), s) for o, c, s in trades if o + k < ln.N]
        STATES.append((tr, ST if not off else TA.run(LN, tr)[0]))
        if off:
            print('pivots +%d min: %d pseudo trades, first opens %s' % (off, len(tr), ln.U(tr[0][0])))
    SIDES = []
    for tr, _ in STATES:
        side = np.zeros(ln.N, np.int8)
        for o, c, s in tr:
            side[o:c] = s
        SIDES.append(side)
    MNR = m_no_rev([side[prt] for side in SIDES], prt)
    mats = {}
    for off, (tr, ST), side, (mn, mv) in zip(OFFS, STATES, SIDES, MNR):
        cols = list(base)
        live = side != 0
        sp = side[prt]

        def exf_at(t):
            #   HIS 1109 *"append `(inf)` or `(exf)`"*: ex-20/80 on the target-side by the banked reader - the
            #   one the towards/away mech's own ex-fence test uses (closed-prev, or the emerging 60 s extreme)
            return np.where(sp > 0, TA.exf_mask(LN, t, +1)[prt], TA.exf_mask(LN, t, -1)[prt]) & (sp != 0)
        #   TOWARDS/AWAY at the same print bar: 0 no state, 1 TO, 2 AW, and +2 when the line is ex-20/80 on the
        #   target-side there - 3 TO(exf), 4 AW(exf). Then per sum column the TO count and the AW count over its
        #   lines, both -1 where no pseudo trade is open (no target-side, so nothing to count)
        for name in LINES:
            t = int(name[2:]) if name.startswith('ws') else 0
            if t not in ST:
                cols.append(np.zeros(len(prt), np.int8))
                continue
            st = ST[t][prt].astype(np.int8)
            cols.append(np.where((st != TA.NONE) & exf_at(t), st + 2, st))
        for _, tfs in SUMS:
            for code in (TA.TO, TA.AW):
                n = np.sum([(ST[t][prt] == code).astype(int) for t in tfs], 0)
                cols.append(np.where(live[prt], n, -1))
        for name in LINES:
            if name not in XC:
                cols.append(np.zeros(len(prt), np.int8))
                continue
            xc = np.where(sp < 0, XC[name][-1], np.where(sp > 0, XC[name][+1], 0)).astype(np.int8)
            #   HIS 1110 *"when a TF flips from TO to AW"*: +4 on the row that reads AW where the row before read TO;
            #   that row only - *"the 'AW's in the following rows are treated normally"*
            st = ST[int(name[2:])][prt]
            xc[1:] |= 4 * ((st[:-1] == TA.TO) & (st[1:] == TA.AW)).astype(np.int8)
            cols.append(xc)
        #   HIS 1111 *"if any of the individual lines are printing TO(exf), print "TO(exf)" under the TO:x AW:x row"*:
        #   per sum column, how many of its lines read TO(exf) - the code a ws1..ws15 cell prints as TO(exf)
        for _, tfs in SUMS:
            cols.append(np.sum([((ST[t][prt] == TA.TO) & exf_at(t)).astype(int) for t in tfs], 0))
        cols.append(mn)                          # HIS 1111 M-no-rev: the highest qualifying TF, 0 none, and its value
        cols.append((mv & 0xFF).astype(np.uint8).view(np.int8))
        cols.append((mv >> 8).astype(np.int8))
        cols.append(side[prt])                   # HIS 1109: the time cell's 20% colour, red LOW, green HIGH
        mats[off] = np.ascontiguousarray(np.stack(cols, 1).astype(np.int8))
    return ts[first], mats


T0 = time.time()
OPEN, MATS = build()
RP = MATS[0]                                    # the pivots as found - every check below reads it
assert all(m.shape == RP.shape for m in MATS.values()) and RP.shape[1] == STRIDE
assert all(np.array_equal(m[:, :len(LINES) + len(SUMS)], RP[:, :len(LINES) + len(SUMS)]) for m in MATS.values()), \
    'the r-pred bytes differ between the two pivot states'
DAYS = []
for i, ms in enumerate(OPEN):
    d = time.strftime('%Y-%m-%d', time.gmtime(int(ms) // 1000))
    if not DAYS or DAYS[-1][0] != d:
        DAYS.append([d, i])
FLAGGED = int((RP[:, :CONTROL_COLS] != 0).sum())
TAC = RP[:, len(LINES) + len(SUMS):2 * len(LINES) + len(SUMS)]
U = lambda ms: time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(ms) // 1000))
META = json.dumps({
    'lines': LINES, 'mnr': MNR_LABEL, 'sums': [s for s, _ in SUMS], 'stride': STRIDE, 'rows': int(len(OPEN)), 't0': int(OPEN[0]), 'step': 60000,
    'days': DAYS, 'shift': PIV_SHIFT})


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body, kind):
        self.send_response(200)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith('/meta'):
            return self._send(META.encode(), 'application/json')
        if self.path.startswith('/rows'):
            q = dict(kv.split('=') for kv in self.path.split('?', 1)[1].split('&'))
            m = MATS.get(int(q.get('off', 0)))  # HIS 1112: 0 the pivots as found, PIV_SHIFT every pivot moved
            if m is None:
                self.send_error(400, 'off must be one of %s' % (OFFS,))
                return
            a = max(0, int(q['start'])); b = min(len(m), a + max(0, int(q['count'])))
            return self._send(m[a:b].tobytes(), 'application/octet-stream')    # STRIDE bytes per row
        return self._send(PAGE.encode(), 'text/html; charset=utf-8')


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>fdm2-diag1</title>
<style>
:root{--bg:#ffffff;--fg:#1d1d1f;--mut:#6e6e73;--line:#dcdce0;--hd:#f1f1f4;--zebra:#fafafb;--red:#d93025;--grn:#1e8e3e;
  --on:#ffffff;--sel:#1a73e8;--dis:#c4c4c8;--org:#d9650b;
  --redA:color-mix(in srgb,var(--red) 20%,transparent);--grnA:color-mix(in srgb,var(--grn) 20%,transparent);
  --redB:color-mix(in srgb,var(--red) 55%,transparent);--grnB:color-mix(in srgb,var(--grn) 55%,transparent);
  --xc:#a68a00;--hl:color-mix(in srgb,var(--sel) 16%,transparent);--flip:#000000}
@media (prefers-color-scheme: dark){:root{--bg:#141416;--fg:#e8e8ea;--mut:#9a9aa0;--line:#2e2e33;--hd:#1e1e22;
  --zebra:#18181b;--red:#e5483b;--grn:#2ea44f;--on:#ffffff;--sel:#8ab4f8;--dis:#4a4a50;--org:#e8710a;--xc:#ecc94b;--flip:#ffffff}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:13px/1.4 system-ui,-apple-system,Segoe UI,sans-serif}
.wrap{max-width:1420px;margin:0 auto;padding:12px 16px;height:100vh;display:flex;flex-direction:column}
h1{font-size:15px;margin:0 0 8px;font-weight:600}
.cal{display:flex;gap:18px;flex-wrap:wrap;margin-bottom:10px}
.mon{min-width:200px}
.mon b{display:block;font-size:12px;margin-bottom:3px}
.grid{display:grid;grid-template-columns:repeat(7,26px);gap:2px}
.grid span{font-size:10px;color:var(--mut);text-align:center}
.grid button{height:22px;border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:4px;
  font:11px system-ui,sans-serif;cursor:pointer;padding:0}
.grid button:hover{border-color:var(--sel)}
.grid button:disabled{color:var(--dis);border-color:transparent;cursor:default}
.grid button.on{background:var(--sel);border-color:var(--sel);color:var(--bg);font-weight:600}
.tog{align-self:flex-start;height:26px;padding:0 12px;border:1px solid var(--line);background:var(--bg);color:var(--fg);
  border-radius:4px;font:12px system-ui,sans-serif;cursor:pointer;white-space:nowrap}
.tog:hover{border-color:var(--sel)}
.tog.on{background:var(--sel);border-color:var(--sel);color:var(--bg);font-weight:600}
.status{display:flex;gap:18px;color:var(--mut);font-size:12px;margin:4px 0 6px;font-variant-numeric:tabular-nums}
.box{flex:1 1 0;min-height:320px;border:1px solid var(--line);border-radius:6px;overflow-y:auto;overflow-x:hidden;position:relative;overflow-anchor:none}
.inner{min-width:0}
.hd,.row{display:grid;grid-template-columns:var(--gt);height:24px;align-items:center}
.row{height:50px}
.hd{position:sticky;top:0;z-index:2;background:var(--hd);border-bottom:1px solid var(--line);font-weight:600}
.hd div{text-align:center;font-size:12px}
.hd div:first-child,.row .t{text-align:left;padding-left:8px}
.body{position:relative}
.row{position:absolute;left:0;right:0;top:0;font-variant-numeric:tabular-nums;border-bottom:1px solid var(--line)}
.row.z{background:var(--zebra)}
.row div{text-align:center;height:49px;display:flex;flex-direction:column;justify-content:center;line-height:16px}
.row .t{display:block;line-height:49px}
.row div b{font-weight:700;font-size:10px}
.row div b.s,.row div b.x{white-space:pre}
.row div b.x{color:var(--xc);font-weight:900}
.row .mn{font-weight:600}
.row div b.g{color:var(--mut)}
.row div b.f{color:var(--flip)}
.row.sel{background:var(--hl);outline:2px solid var(--sel);outline-offset:-2px}
.row .t.lo{background:var(--redA)}
.row .t.hi{background:var(--grnA)}
.row .t{color:var(--fg);white-space:nowrap}
.row .m{background:var(--red);color:var(--on);font-weight:600}
.row .p{background:var(--grn);color:var(--on);font-weight:600}
.row .m.a{background:var(--redB)}
.row .p.a{background:var(--grnB)}
.row .w{color:var(--dis)}
.row .zr{color:var(--mut)}
.row .o{background:var(--org);color:var(--on);font-weight:600}
.hd .sx,.row .sx{border-left:2px solid var(--mut)}
</style></head><body><div class="wrap">
<h1>fdm2-diag1 - r-pred, gcws15 to ws15, M-no-rev, plus the ws16-22 and ws23-30 sums, emerging, on closed-prev ws1 bars, with towards/away</h1>
<div class="cal" id="cal"></div>
<div class="status"><span id="top">top row: -</span><span id="held">cache: -</span><span id="err"></span></div>
<div class="box" id="box"><div class="inner"><div class="hd" id="hd"></div><div class="body" id="body"></div></div></div>
</div><script>
const RH = 50;          // row height, px - three lines: the number, TO / AW, then the crosses (HIS 1110)
const BLOCK = 720;      // rows per fetch: 12 h of ws1 bars
const AHEAD = 3;        // blocks prefetched in the scroll direction
const KEEP = 60;        // blocks held before the least recently used is dropped
const TW = 116;         // px, the time column: MM-DD HH:MM:SS (HIS 1111 drops the year) plus the 32 px it had
const TMIN = 94, SMIN = 56;   // px, the least the time column and a sum column give way to: their text, 84 and 52 px
const MMIN = 68;      // px, the least M-no-rev gives way to: its widest text, "ws23:100.0", is 65.0 px in the cell (headless Chrome)
const CW = 72.36;      // px, every line and sum column - HIS 1111 *"stay the same width as they are now"*
let meta, NL, NC, NS;
const cache = new Map(), pending = new Set();
const box = document.getElementById('box'), body = document.getElementById('body');
const pool = [];
let lastTop = 0, dir = 1, raf = 0, dayOn = '';
const NB = '\u00a0';   // HIS 1110: the place holder line - a blank line keeps a cell's 3 lines aligned
let sel = -1;           // HIS 1110: the clicked row, highlighted; a click on another row moves it, on the same row clears it
let OFF = 0;            // HIS 1112: minutes the pivots are moved forward - 0 as found, meta.shift with the button on

const fmt = ms => new Date(ms).toISOString().slice(0, 19).replace('T', ' ');

function fetchBlock(b) {
  const off = OFF, key = off + ':' + b;          // HIS 1112: each pivot state keeps its own blocks
  if (b < 0 || b * BLOCK >= meta.rows || cache.has(key) || pending.has(key)) return;
  pending.add(key);
  fetch('rows?start=' + (b * BLOCK) + '&count=' + BLOCK + '&off=' + off)
    .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.arrayBuffer(); })
    .then(buf => { pending.delete(key); cache.set(key, new Int8Array(buf)); evict(); schedule(); })
    .catch(e => { pending.delete(key); document.getElementById('err').textContent = 'fetch failed: ' + e.message; });
}
function getBlock(b) {
  const key = OFF + ':' + b, a = cache.get(key);
  if (a) { cache.delete(key); cache.set(key, a); }   // most recently used goes to the back
  return a;
}
function evict() {
  while (cache.size > KEEP) cache.delete(cache.keys().next().value);
  document.getElementById('held').textContent = 'cache: ' + cache.size + ' blocks, ' +
    (cache.size * BLOCK).toLocaleString() + ' rows held of ' + meta.rows.toLocaleString();
}
function prefetch(first, n) {
  const b0 = Math.floor(first / BLOCK), b1 = Math.floor((first + n) / BLOCK);
  for (let b = b0; b <= b1; b++) fetchBlock(b);
  for (let k = 1; k <= AHEAD; k++) fetchBlock(dir > 0 ? b1 + k : b0 - k);
  fetchBlock(dir > 0 ? b0 - 1 : b1 + 1);
}
function ensurePool(n) {
  while (pool.length < n) {
    const el = document.createElement('div'); el.className = 'row';
    const cells = [];
    let mc = null;
    for (let c = 0; c <= NC; c++) {
      if (c === NL + 1) {              // HIS 1111 M-no-rev, between ws15 and the sums; 3 lines like every data cell
        mc = document.createElement('div'); mc.n = document.createElement('span');
        mc.ta = document.createElement('b'); mc.xc = document.createElement('b'); mc.append(mc.n, mc.ta, mc.xc);
        el.appendChild(mc);
      }
      const d = document.createElement('div'); d.className = c ? '' : 't'; el.appendChild(d);
      if (c) { d.n = document.createElement('span'); d.ta = document.createElement('b'); d.append(d.n, d.ta); if (c > NL) d.ta.className = 's'; }
      if (c) { d.xc = document.createElement('b'); d.xc.className = 'x'; d.append(d.xc); }   // HIS 1110 cross row, every cell
      cells.push(d);
    }
    body.appendChild(el); pool.push({el, cells, mc, i: -1, ok: false});
  }
}
function draw() {
  raf = 0;
  const top = box.scrollTop;
  dir = top >= lastTop ? 1 : -1; lastTop = top;
  const first = Math.max(0, Math.floor(top / RH));
  const n = Math.ceil(box.clientHeight / RH) + 2;
  ensurePool(n);
  prefetch(first, n);
  for (let k = 0; k < pool.length; k++) {
    const p = pool[k], i = first + k;
    if (k >= n || i >= meta.rows) { p.el.style.display = 'none'; p.i = -1; continue; }
    p.el.style.display = '';
    if (p.i === i && p.ok) continue;
    p.el.style.transform = 'translateY(' + (i * RH) + 'px)';
    p.el.className = 'row' + (i % 2 ? ' z' : '') + (i === sel ? ' sel' : '');
    p.cells[0].textContent = fmt(meta.t0 + i * meta.step).slice(5);   // HIS 1111: no year
    const blk = getBlock(Math.floor(i / BLOCK)), o = (i % BLOCK) * NS;
    const sd = blk ? blk[o + NS - 1] : 0;   // HIS 1109: the trade's target-side, 20% red LOW / green HIGH
    p.cells[0].className = 't' + (sd < 0 ? ' lo' : sd > 0 ? ' hi' : '');
    //   HIS 1111 M-no-rev: the highest target-side oob Mage TF with no lift-off reversal since its cross to oob;
    //   *"if there is no Mage qualifying, don't print anything in the field"*
    //   HIS 1111 *"if the field is populated, add the line's value to the text"*: closed-prev, 1 dp, "ws23:95.2"
    const mv = blk ? blk[o + NS - 4] : 0, mx = blk ? ((blk[o + NS - 2] << 8) | (blk[o + NS - 3] & 255)) : 0;
    p.mc.n.textContent = !blk ? '·' : mv > 0 ? 'ws' + mv + ':' + (mx / 10).toFixed(1) : NB;
    p.mc.ta.textContent = NB; p.mc.xc.textContent = NB;
    p.mc.className = (blk ? 'mn' : 'w') + ' sx';
    for (let c = 0; c < NC; c++) {
      const d = p.cells[c + 1], sx = c === NL ? ' sx' : '';
      if (!blk) { d.n.textContent = '·'; d.ta.textContent = NB; d.xc.textContent = NB; d.className = 'w' + sx; continue; }
      const v = blk[o + c];
      if (c < NL) {                     // a wsf line: -1 red, +1 green, 0 plain
        d.n.textContent = v === -1 ? '-1' : v === 1 ? '+1' : '0';
        const s = blk[o + NC + c];      // HIS 1109: TO or AW below the number, bold
        //   HIS 1110: a -1 / +1 on an AW line (code 2 AW(inf), 4 AW(exf)) prints its background at 55% opaque
        d.className = (v === -1 ? 'm' : v === 1 ? 'p' : 'zr') + (v !== 0 && (s === 2 || s === 4) ? ' a' : '');
        d.ta.textContent = ['', 'TO(inf)', 'AW(inf)', 'TO(exf)', 'AW(exf)'][s] || NB;   // HIS 1109 (inf) / (exf)
        //   HIS 1110: crossovers on a LOW target-side, crossunders on HIGH; X and E on one ws1 bar join, 4 spaces apart
        const xc = blk[o + NC + NL + 2 * (NC - NL) + c];
        d.xc.textContent = [xc & 1 ? (sd < 0 ? 'X↑' : '↓X') : '', xc & 2 ? (sd < 0 ? '↑E' : '↓E') : '']
          .filter(Boolean).join('    ') || NB;
        d.ta.className = xc & 4 ? 'f' : 'g';   // HIS 1110: TO on the row before, AW on this one - white, this row only;
                                               // HIS 1111: every other TO/AW grey, on a -1/+1 cell too
      } else {                          // a sum, HIS 1109: red below 0, green above 0, orange at 0
        d.n.textContent = v > 0 ? '+' + v : String(v);
        d.className = (v < 0 ? 'm' : v > 0 ? 'p' : 'o') + sx;
        const k = o + NC + NL + 2 * (c - NL), to = blk[k], aw = blk[k + 1];
        d.ta.textContent = to < 0 ? NB : 'TO:' + to + '  AW:' + aw;   // HIS "TO:x  AW:x", the weekday size
        //   HIS 1111: "TO(exf)" under it when any of the column's lines reads TO(exf); the TO:x AW:x line's style
        d.xc.textContent = blk[o + NC + 2 * NL + 2 * (NC - NL) + (c - NL)] > 0 ? 'TO(exf)' : NB;
        d.xc.className = 's';
      }
    }
    p.i = i; p.ok = !!blk;
  }
  const t = meta.t0 + first * meta.step;
  document.getElementById('top').textContent = 'top row: ' + fmt(t);
  markDay(fmt(t).slice(0, 10));
}
function schedule() { if (!raf) raf = requestAnimationFrame(draw); }

function markDay(d) {
  if (d === dayOn) return;
  const old = document.querySelector('.grid button.on'); if (old) old.classList.remove('on');
  const b = document.querySelector('.grid button[data-d="' + d + '"]'); if (b) b.classList.add('on');
  dayOn = d;
}
function buildCal() {
  const rowOf = new Map(meta.days);
  const months = [...new Set(meta.days.map(d => d[0].slice(0, 7)))];
  const cal = document.getElementById('cal');
  for (const ym of months) {
    const [y, m] = ym.split('-').map(Number);
    const mon = document.createElement('div'); mon.className = 'mon';
    mon.innerHTML = '<b>' + new Date(Date.UTC(y, m - 1, 1)).toLocaleString('en', {month: 'long', timeZone: 'UTC'}) + ' ' + y + ' (UTC)</b>';
    const g = document.createElement('div'); g.className = 'grid';
    for (const w of ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']) { const s = document.createElement('span'); s.textContent = w; g.appendChild(s); }
    const lead = (new Date(Date.UTC(y, m - 1, 1)).getUTCDay() + 6) % 7;
    for (let k = 0; k < lead; k++) g.appendChild(document.createElement('span'));
    const nd = new Date(Date.UTC(y, m, 0)).getUTCDate();
    for (let d = 1; d <= nd; d++) {
      const key = ym + '-' + String(d).padStart(2, '0');
      const b = document.createElement('button'); b.textContent = d; b.dataset.d = key;
      if (!rowOf.has(key)) b.disabled = true;
      else {
        const r = rowOf.get(key);
        b.title = key + ' from ' + fmt(meta.t0 + r * meta.step);
        b.onmouseenter = () => { const b0 = Math.floor(r / BLOCK); fetchBlock(b0); fetchBlock(b0 + 1); fetchBlock(b0 + 2); };
        b.onclick = () => { dir = 1; box.scrollTop = r * RH; lastTop = box.scrollTop; draw(); };
      }
      g.appendChild(b);
    }
    mon.appendChild(g); cal.appendChild(mon);
  }
}
async function init() {
  meta = await (await fetch('meta')).json();
  NL = meta.lines.length; NC = NL + meta.sums.length; NS = meta.stride;
  const hd = document.getElementById('hd');
  for (const h of ['ws1 time (UTC)'].concat(meta.lines, [meta.mnr], meta.sums)) { const d = document.createElement('div'); d.textContent = h; hd.appendChild(d); }
  hd.children[NL + 1].className = 'sx'; hd.children[NL + 2].className = 'sx';
  body.style.height = (meta.rows * RH) + 'px';
  //   HIS 1111: no sideways bar. The lines stay CW; the time column takes what is left, then M-no-rev and the
  //   sums give way together
  const inner = box.firstElementChild, tw = TW + (NC + 1) * CW;
  inner.style.setProperty('--gt', 'minmax(' + TMIN + 'px,1fr) repeat(' + NL + ',' + CW + 'px) minmax(' + MMIN + 'px,' +
                          CW + 'px) repeat(' + (NC - NL) + ',minmax(' + SMIN + 'px,' + CW + 'px))');
  //   after the body's height, so the vertical scrollbar is in the box's width
  document.querySelector('.wrap').style.maxWidth = (tw + box.offsetWidth - box.clientWidth + 32) + 'px';
  buildCal();
  //   HIS 1112 *"I want a button at the top (on the right of the calenders), to toggle an offset in the UI"*. The
  //   scroll position is not touched, so the rows on screen stay where they are and only their cells change
  const tg = document.createElement('button'); tg.className = 'tog'; tg.textContent = 'pivots +' + meta.shift + ' min';
  tg.title = 'move every ws2Mage pivot ' + meta.shift + ' minutes forward; click again for the pivots as found';
  tg.setAttribute('aria-pressed', 'false');
  tg.onclick = () => {
    OFF = OFF ? 0 : meta.shift;
    tg.classList.toggle('on', OFF > 0); tg.setAttribute('aria-pressed', String(OFF > 0));
    for (const p of pool) p.ok = false;
    schedule();
  };
  document.getElementById('cal').appendChild(tg);
  box.addEventListener('scroll', schedule, {passive: true});
  body.addEventListener('click', e => {           // HIS 1110: *"make a row highlighted if I click on that row"*
    const el = e.target.closest('.row'), p = el && pool.find(q => q.el === el);
    if (!p || p.i < 0) return;
    sel = sel === p.i ? -1 : p.i;
    for (const q of pool) q.el.classList.toggle('sel', q.i === sel);
  });
  window.addEventListener('resize', schedule);
  evict();
  schedule();
}
init().catch(e => { document.getElementById('err').textContent = 'load failed: ' + e.message; });
</script></body></html>
"""


if __name__ == '__main__':
    print('bars %d, %s .. %s' % (ln.N, ln.U(0), ln.U(ln.N - 1)))
    print('rows %d, %s .. %s, built in %.1f s' % (len(OPEN), U(OPEN[0]), U(OPEN[-1]), time.time() - T0))
    print('CONTROL flagged cells %d, 1109 measurement %d: %s'
          % (FLAGGED, CONTROL_FLAGGED, 'MATCH' if FLAGGED == CONTROL_FLAGGED else 'DIFFERS'))
    for k, (label, _) in enumerate(SUMS):
        v = RP[:, len(LINES) + k].astype(int)
        print('%s: below 0 %d, at 0 %d, above 0 %d, min %d, max %d'
              % (label, (v < 0).sum(), (v == 0).sum(), (v > 0).sum(), v.min(), v.max()))
    print('towards/away cells: TO(inf) %d, AW(inf) %d, TO(exf) %d, AW(exf) %d, none %d'
          % tuple((TAC == k).sum() for k in (1, 2, 3, 4, 0)))
    _xc = RP[:, 2 * len(LINES) + 3 * len(SUMS):3 * len(LINES) + 3 * len(SUMS)]
    print('cross row cells: X only %d, E only %d, both %d'
          % tuple(int(((_xc & 3) == k).sum()) for k in (1, 2, 3)))
    print('TO -> AW flip cells (white AW text): %d, %d of them on a -1/+1 cell'
          % (int((_xc & 4).astype(bool).sum()), int(((_xc & 4).astype(bool) & (RP[:, :len(LINES)] != 0)).sum())))
    _rp = RP[:, :len(LINES)]
    print('r-pred -1/+1 cells on an AW line (55%% background): %d of %d flagged, all %d columns'
          % (int(((_rp != 0) & ((TAC == 2) | (TAC == 4))).sum()), int((_rp != 0).sum()), len(LINES)))
    _mn = RP[:, STRIDE - 4].astype(int)
    _mv = (RP[:, STRIDE - 2].astype(int) << 8) | (RP[:, STRIDE - 3].astype(int) & 255)
    for k, (label, _) in enumerate(SUMS):
        _ex = RP[:, 3 * len(LINES) + 3 * len(SUMS) + k].astype(int)
        print('%s: rows printing TO(exf) %d of %d, most lines reading TO(exf) on one row %d'
              % (label, int((_ex > 0).sum()), len(_ex), int(_ex.max())))
    print('M-no-rev (ws1..ws%dMage): rows printing a TF %d of %d, highest TF printed %d, value %.1f .. %.1f'
          % (MNR_TOP, int((_mn > 0).sum()), len(_mn), int(_mn.max()), _mv[_mn > 0].min() / 10, _mv[_mn > 0].max() / 10))
    for _off in OFFS[1:]:
        _m = MATS[_off]
        print('pivots +%d min: rows whose target-side differs from the pivots as found %d of %d, cells that differ %d of %d'
              % (_off, int((_m[:, STRIDE - 1] != RP[:, STRIDE - 1]).sum()), len(RP), int((_m != RP).sum()), RP.size))
    print('towards/away knobs (banked): ' + ' '.join('%s=%s' % (k, v) for k, v, _, _ in TA.KNOBS))
    print('open http://127.0.0.1:%d' % PORT)
    sys.stdout.flush()
    ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
