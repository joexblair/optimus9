"""fdm3-oracle, THE r-pred WEB UI. OWNED BY 7c82535c from HIS 1114 *"rename it to fdm3-oracle in all places, including renaming any references to rpred. you can take ownership of it now"*, which supersedes HIS 1113 *"rename the webUI report: fdm2-oracle"* (HIS 1111 named it fdm2-diag1, banked 2026-11-12).
A RESTART COSTS ~18 MINUTES, HIS 1114: *"it takes ~18 minutes to restart"*. The 7 towards/away runs go one
after another at 97.9 s to 109.4 s each, and the matrix is held in memory with no disk cache, so every code change
to this file means ~18 minutes with the page down. TREAT A RESTART AS EXPENSIVE: batch changes, and read the
running page rather than restarting to check something. His 1113 parallel-start-up note is the standing idea for
cutting it - cupy 14.1.1 and one RTX 3060 Ti are available, and each state must stay byte-identical to the
serial page.

HIS 1114 ALSO SET THE RENAME'S SCOPE: *"I was refering only to rpred as it sits inside of the fdm3-oracle build"*. Every path, the unit, the log, the page title and the heading now
carry fdm3-oracle. `r-pred` SURVIVES EVERYWHERE IT NAMES THE SIGNAL - breaching_line.predict_breach's -1/+1 - because that is HIS word for the signal and it
carries the banked knob FDM2_MOMO_FLOOR_RPRED. His 1114: *"you were right to hold on the rpred rename"*. Joe 1109: *"I want to access this -1/+1 r-pred data in a dhtml webUI"*.

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

HIS 1112 PIVOT BUTTON, REMOVED HIS 1115 *"remove also the pivots+15 button"*. It moved every ws2Mage pivot 15 min
later (his 1112 *"move the pivots forward 15 minutes"*); no page state moves a pivot now.

HIS 1112 TOWARDS/AWAY UPDATE: *"I want to see the flip from TO to AW based on the x and e cross."* No page change: the
TO/AW codes come from towards_away.run, which now carries the 50 reset, the excursion sample on e and x, the void
values, the row rule and the x/e path (spec section 12). Both pivot states read it.

HIS 1113 FENCE BUTTON, REMOVED HIS 1115 *"23/77 has proven to be the best option, so we can remove that button and lock
23/77 for the UI"*. Every towards/away read on the page - the reach, the scenario-1 vote, the pair's in-fence samples,
the x/e path's in-fence extremum - and the (inf)/(exf) tags and the sums' TO(exf) read 23/77 (FNC). The read itself
is unchanged: closed-prev OR the emerging extreme of the last 12 bars. Where a paragraph below says ex-20/80, the page
now reads ex-23/77. The banked towards/away run outside the page is still 20/80.

HIS 1113 FLIP BUTTON: *"add a button that flips the pivots directions, ie the green rows will become the red rows and
vice versa"*. With the button on, every ws2Mage pivot's side is flipped on its own bar - a HIGH pivot reads LOW and a
LOW pivot HIGH - so every pseudo trade opens and closes on the same bars with its target-side flipped (asserted), and
towards/away runs again on those trades. The time cell's red and green swap, and, as with the pivot button, everything
that reads the pseudo trade follows: TO/AW and (inf)/(exf), the sums' TO:x AW:x and TO(exf), the cross row's side, the
TO -> AW flip and M-no-rev. The r-pred numbers do not read the pseudo trade and stay as they are (asserted). No
button changes the scroll position. MINE: the label "flip pivots", blue when on; since 1115 it is the first button.

HIS 1115 THE TWO A BUTTONS: *"I want to try A first, but in way that I can control it. I'm deep in developing a strategy
and my decisions have been made on the existing build"* / *"I'm not sure if the lower TFs and the higher TFs need the
same mech shape.  create two buttons that A will be applied to - the first button shows A for ws1-ws6, and the second
shows A for ws7-ws15"*. A is his choice from the 1115 ws5r 2026-09-20 trace: lift-off's window extreme is read off
EVERY bar of its span, (LIFT_PTS - 1) x gap_for(TF) bars, not only the six samples - jig.at_extreme `line_extreme`,
OFF BY DEFAULT so nothing outside these buttons moves. The six samples, the 2.0 tolerance, the 8-bar hold and the pivot
rule are unchanged. With a button on, towards/away runs with A on the lift-off reads of that band's r lines: the
natural reversals (scenario 1 and the x/e path's pivot) and, his *"1 and 2: agreed"*, the e-cross reversals, which read
A's natural reversals. M-no-rev's Mage lift-off stays as built (agreed). A line with A on also moves the scenario-2
test of the lines above it, which reads the 5 lines under them - so A ws1-ws6 can move ws7..ws11 cells, and A
ws7-ws15 the ws16-22 and ws23-30 sums. The two buttons and flip pivots combine: 8 states built at start-up, each kept
apart in the page. With both A buttons off a state is the 1113 page's 23/77 state byte for byte (checked 1115 against
the running page). MINE: the labels "A ws1-ws6" and "A ws7-ws15", blue when on, on the right of flip pivots.

HIS 1115 SL% AND THE gcws COLUMNS: *"while we're in test mode, add this dynamic stop loss mech and produce it in skinny
column labeled 'SL%', to the right of 'ws1 time'"* / *"drop the gcws15 and gcws30 columns. keep the table's existing
columns at their current width, ie don't attempt to fill the lost column space"*. sl_pct has his spec and his 09-20
walk. The column is 48 px (MINE), 2 dp, blank where no leg ends in the last 6 h; it reads neither the pivots nor A, so
it is the same in every state. gcws15 and gcws30 are gone from the page and the payload; the 1109 r-pred control still
reads them (CONTROL_LINES), so its 257,295 is the same check. Every other column keeps its width and the box narrows.

HIS 1113 ws1 TO(exf) FLIP: *"in ws1 only, in the same format as any flip to AW(*), highlight the field when ws1 flips to
TO(exf)"*. His answer to which readings on the row before count: *"any except TO(exf)"* - blank, TO(inf), AW(inf) or
AW(exf). The ws1 cell's TO(exf) prints white (black in light mode) on that row only, like the TO -> AW flip; the server
marks it +8 in the cross code. MINE, from his "any": the row before counts whichever pseudo trade it is in, as the
TO -> AW flip already compares (on the pivots as found at 20/80, 100 TO(inf) and 160 AW(inf) rows of the previous
pseudo trade, 2026-11-14).

HIS 1113 SUM COLUMNS, TO(exf) COUNT: *"in the ws16-22 and ws23-30 columns, add the count of TO(exf) lines, if TO(exf) is
printing"* - the third line reads "TO(exf):x", x the number of the column's lines reading TO(exf) (the count the page
already carried), blank when none. MINE: the "TO:x" form of the line above it.

HIS 1113 NEXT ITERATION - BUILD THE STATES IN PARALLEL: *"building the 8 combos in parallel is a great idea.  add that
as a docstring so that you remember it when we build the next iteration.  note you have cupy available if that helps"*.
build() makes the eight states one after another: towards_away.run once per state other than the first, 7 runs of
97.9 s to 109.4 s each (measured alone, 2026-11-13), and start-up is 1028.2 s on 16 cores. The states do not read each
other, so each run can go to its own process (forked after the lines load, so the line arrays are shared, not copied),
returning its 30 int8 state arrays; M-no-rev and the cross row stay in the parent. cupy 14.1.1 is installed with one GPU
(NVIDIA GeForce RTX 3060 Ti, checked 2026-11-14). Every state must stay byte-identical to the serial build (md5 per state).
HIS 1114 *"GPU or CPU?"* - MEASURED 2026-11-14, answer CPU processes: one run makes 269,224,773 Python/numpy calls
(18,885,905 numpy reductions) on short slices of the tape; one "any value above 0.5" check takes 1.4 us on the CPU and
155.3 us on the GPU for 100 values, 2.3 us vs 177.2 us for 10,000, and 385.3 us vs 232.9 us for the whole tape
(1,632,960). The natural lift-off reads (32.2 s) and the e-cross lift-off reads (5.9 s, after a first run) take only
the lines, the TF and the side - the same in all 8 states - so they can be read once and shared. A first run in a fresh
process took 216.8 s, the runs after it in the page 97.9 s to 109.4 s (cause not traced): fork after the bank run.
Scratch: scratchpad/gpucpu/.

usage: fdm3_oracle.py [port]   then open http://127.0.0.1:<port>
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
    import v4_backstop_trades as BT
    import v4_knobs as K
    from optimus9.analysis import jig as JIG
finally:
    sys.stderr = _e
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8788
if __name__ == '__main__':
    #   A TAKEN PORT FAILS IN A SECOND, NOT AFTER THE ~50 s BUILD. As the o9-fdm3-oracle service (Restart=always) a
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
LINES = ['ws%d' % t for t in range(1, 16)]      # HIS 1109 wsf + ws13..ws15 HIS 1111; HIS 1115 *"drop the gcws15 and gcws30
#                                                 columns"*
SUMS = [('ws16-22', range(16, 23)), ('ws23-30', range(23, 31))]   # HIS 1111 two right columns (1109: ws13-20, ws21-30)
CONTROL_FLAGGED = 257295        # 1109 measurement: the 14 wsf columns' cells at -1 or +1, whole tape
CONTROL_LINES = ['gcws15', 'gcws30'] + ['ws%d' % t for t in range(1, 13)]   # the 1109 control's 14 lines - gcws15 and
#                                 gcws30 are still read for it, though the page no longer shows them (HIS 1115)
SL_LINE = 'gcws15b'             # HIS 1115 STOPLOSS: *"between gcws15b extrema (oob to opposing oob)"*, on 15 s closed bars
SL_HOURS = 6.0                  # HIS 1115 *"averaged over the last 6 hours"*
SL_NONE = -1                    # SL% x 100 where no leg ends in the window, or the tape has under 6 h behind the row
#   HIS 1117: *"I can't decide between ws15 and ws25, so we'll need two m-no-rev columns - one for
#   each. the columns can be skinny. label them mnr1 and mnr2"*. mnr1 is the LOWER ceiling.
MNR_LABELS = ('mnr1', 'mnr2')
MNR_TOPS = (15, 25)             # mnr1 ws1..ws15, mnr2 ws1..ws25
MNR_LO = 1                      # HIS 1117: *"we'll settle on ws1 to ws25"* - ws1 adds no leg end that
#                                 ws2 does not already give, but he keeps it: *"m-no-rev is a 'keep
#                                 walking' gate, not a 'bet the bank on it' event"*
MNR_RESET = True                # HIS 1117 closed-prev resume, on. False restores the 1111 column
#                                 exactly, for his A/B
STRIDE = (len(LINES) + len(SUMS) + len(LINES) + 2 * len(SUMS) + len(LINES) + len(SUMS)
          + len(LINES) + 3 + 3 * len(MNR_TOPS))   # bytes per row: r-pred,
#   the TO/AW codes, the TO/AW counts, the cross codes (HIS 1110: 1 X, 2 E, 3 both, on the row's target-side; +4 the
#   line reads AW on this row and TO on the row before, HIS 1110 TO -> AW flip; +8 ws1 only, TO(exf) on this row and
#   anything else on the row before, HIS 1113), per sum the count of its lines
#   reading TO(exf) (HIS 1111), HIS 1116 the UP/DN pair per line (bits 0-1 position 1, this row against the row 3
#   back; bits 2-3 position 2, against the row 2 back; 0 a dead tie or no row that far back, 1 up, 2 dn),
#   HIS 1115 SL% x 100 as an int16 in two bytes (low byte first, SL_NONE blank), then PER M-no-rev COLUMN (HIS 1117
#   mnr1 ws1..ws15, mnr2 ws1..ws25) its TF (0 none) and that line's closed-prev value x 10 as an int16 in two bytes
#   (low byte first), then the pseudo trade's target-side at the row's read bar: -1 LOW, +1 HIGH, 0 no trade


FNC = 23.0                      # HIS 1115 *"23/77 has proven to be the best option, so we can remove that button and lock
#                                 23/77 for the UI"* - the smaller end, his 1103 rule. The fence button is gone
A_BANDS = (('ws1-ws6', tuple(range(1, 7))), ('ws7-ws15', tuple(range(7, 16))))   # HIS 1115 the two A buttons: *"the
#                                 first button shows A for ws1-ws6, and the second shows A for ws7-ws15"*
#   HIS 1117: *"bank A ws1-ws6 and make it the machine - that will reduce the build time"*. A is no
#   longer switchable: ws1..ws6 is on, ws7..ws15 off, one A state instead of four.
A_LOCK = (1, 0)                 # A ws1-ws6 on, A ws7-ws15 off - BANKED, not a button
A_TFS = [t for (_, band), on in zip(A_BANDS, A_LOCK) if on for t in band]
#   HIS 1117: *"I need the 'pivot +15 min' button reintroduced on 8790. instead of +15, make it +30
#   minutes"*. It was dropped in the 1115 rebuild; this is HIS 1112 button at his new value.
PIV_SHIFT = 30                  # minutes - HIS 1117, was 15 at his 1112
OFFS = (0, PIV_SHIFT)           # the pivots as found, and every pivot PIV_SHIFT later
FLIP_TOX = 'ws1'                # HIS 1113: the one line whose flip into TO(exf) is highlighted, *"in ws1 only"*
TO_EXF = 3                      # the TO/AW code a cell prints as TO(exf): TO 1, +2 ex-fence on the target-side
FLIPS = (0, 1)                  # HIS 1113 button: *"flips the pivots directions"* - 0 as found, 1 every pivot's side flipped


def mnr_reset(cp, oob, cross, st, step, sd):
    """HIS 1117 M-no-rev resume, walked per oob run. -> bool array: the line reads oob-and-not-yet-reversed here.

    HIS WORDS: *"let's go back to the banked state (any Mage to oob, m-no-rev prints. Mage reverses, m-no-rev
    stops printing) / instead of reacting to a more extreme Mage value using emerging values, we'll use
    closed-prev... then, if the following closed-prev bar is more extreme, m-no-rev starts printing again until it
    is terminated by a fresh reversal. if the next closed-prev bar is less extreme, nothing happens"*.

    `cp` the closed-prev Mage - the oob test's own reading and the only one this mech reads. `oob` / `cross` that
    test's run mask and each bar's cross-into-oob bar. `st` the reversals' knowable stamps, sorted. `step` True on
    the bars where cp carries a NEW value that is more extreme on the target side than the one before it - the
    line's own closed bars, from v4_closed_prev.seam_bars, so for ws15Mage one comparison every 15 minutes.

    CAUSAL: a reversal arms only from its KNOWABLE stamp, a step is read on the bar it lands on, and the loop
    never looks past the bar it is deciding.
    """
    assert (np.diff(st) >= 0).all(), 'the reversal stamps are not sorted'
    out = np.zeros(len(cp), bool)
    n, i = len(st), 0
    while i < len(cp):
        if not oob[i]:
            i += 1
            continue
        c = int(cross[i])
        armed = True                            # a run opens not-yet-reversed, as it always did
        p = int(np.searchsorted(st, c, side='left'))
        while i < len(cp) and oob[i]:
            while p < n and st[p] <= i:         # every reversal knowable by this bar
                if st[p] >= c:                  # HIS 1111: only one at or after the cross counts
                    armed = False
                p += 1
            if not armed and step[i]:
                armed = True                    # HIS 1117: a more extreme closed bar resumes the print
            out[i] = armed
            i += 1
    return out


def m_no_rev(sps, prt):
    """HIS 1111 M-no-rev. -> [(int8 [rows], int16 [rows])], one per target-side array in sps: the highest TF whose
    Mage qualifies at the row's print bar, 0 = none, and that line's CLOSED-PREV value there x 10 (HIS 1111 *"add
    the line's value to the text"*, his example 1 dp), 0 where no TF prints. The lift-off reads do not depend on
    the target-side, so every page state shares them.

    A ws{TF}Mage, ws1..ws30, qualifies on a row when, at the row's print bar:
      oob       its CLOSED-PREV value is at or beyond 85 high / 15 low on the row's target-side (the time cell's
                colour). No pseudo trade open, no target-side, nothing prints
      the cross its cross INTO oob is the first bar of its current closed-prev oob run. The cross back to ib has
                no bearing (HIS 1111)
      reversal  no lift-off reversal printed between the cross and the print bar, UNLESS the line has since been
                reset - see below. The lift-off is jig.lift_off on the EMERGING Mage line over the whole tape - one
                unbroken rolling window - at the banked LIFT_* knobs with no e path, the call every Mage reader
                makes. A reversal counts from its KNOWABLE bar, the end of its 40 s hold (lift_stamp), at or after
                the cross - HIS 1111: build it *"based on that table's output"*, the 1111 table of every change
                from 2026-09-21 15:44:00, which read it that way

    HIS 1116 RESET: *"m-no-rev column stops printing on the first MAge reversal, when the Mage is oob. the update to
    the mech: -store that "final" reversal value with the line -if the Mage prints further "away from 50 towards
    target-side" ... AND is bound to the current OOB excursion --reset the line to 'oob-and-not-yet-reversed', and
    resume printing"*, and *"the stored value is read as emerging at the pivot"*.

    So a reversal no longer ends the oob run's printing for good. It stores the EMERGING Mage's value at the
    lift-off PIVOT bar - his ruling, over the same value at the knowable stamp and over either closed-prev reading -
    and the line prints again from the first later bar whose EMERGING Mage is STRICTLY further from 50 on the
    target-side than that stored value: above it on a HIGH target-side, below it on a LOW one. His *"increases"* is
    why it is strict. The next reversal stamp stores a new value and stops the print again, so a run can cycle any
    number of times.

    *"bound to the current OOB excursion"* scopes all of it to the Mage's OWN current oob run: a fresh cross into
    oob clears the stored value and nothing carries across. The oob test itself is unchanged - still closed-prev.
    """
    idx = np.arange(ln.N)
    #   HIS 1117: one result per ceiling per target-side array. One pass over the lines fills both,
    #   because mnr2's range contains mnr1's - a line that qualifies for mnr1 qualifies for mnr2.
    res = [[[np.zeros(len(prt), np.int8), np.zeros(len(prt), np.int16)] for _ in MNR_TOPS]
           for _ in sps]
    #   HIS 1117 ws1 up. Ascending, so the highest qualifying TF is the one left in each column
    seam_of = {}
    for t in range(MNR_LO, max(MNR_TOPS) + 1):
        em = np.asarray(ln.line('ws%dMage' % t), float)
        cp = CP.series(em, t * 60)
        for sd in (+1, -1):
            with np.errstate(invalid='ignore'):
                oob = cp >= K.OOB_HI if sd > 0 else cp <= K.OOB_LO
            start = oob & ~np.concatenate([[False], oob[:-1]])
            cross = np.where(oob, np.maximum.accumulate(np.where(start, idx, -1)), -1)
            raw = np.asarray(JIG.lift_off(em, sd, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL, K.LIFT_WOB), int)
            st = np.sort(np.asarray([K.lift_stamp(int(b)) for b in raw], int))
            k = np.searchsorted(st, idx, side='right') - 1     # the last reversal knowable at or before each bar
            last = np.where(k >= 0, st[np.clip(k, 0, None)], -1)
            assert (last <= idx).all(), 'a reversal is read before it is knowable'
            if not MNR_RESET:
                un = (oob & (last < cross))[prt]
            else:
                #   HIS 1117: the bars cp steps on, and whether the step is more extreme on this side
                #   A CLOSED-PREV SERIES STEPS ONE BAR AFTER ITS SEAM: seam_bars names the last 5 s
                #   bar of a completed bucket and the new value lands on the bar after it. So the
                #   comparison is simply "this bar's value against the one it replaced", and the
                #   assert holds it to CP's own seams rather than trusting that reading.
                if t not in seam_of:
                    m = np.zeros(ln.N, bool)
                    m[np.asarray(CP.seam_bars(t * 60), int) + 1] = True
                    seam_of[t] = m[:ln.N]
                step = np.zeros(ln.N, bool)
                with np.errstate(invalid='ignore'):
                    changed = cp[1:] != cp[:-1]
                    more = (cp[1:] > cp[:-1]) if sd > 0 else (cp[1:] < cp[:-1])
                step[1:] = changed & more
                #   A RESUME CAN ONLY LAND ON THE SEAM GRID. A closed-prev value also "changes"
                #   where the line warms up out of NaN, but a NaN comparison is False on both sides,
                #   so `more` cannot fire there - measured: every off-grid change on ws1, ws5, ws9,
                #   ws15 and ws25 has a non-finite value on one side, 0 with both finite.
                assert not (step & ~seam_of[t]).any(), 'a resume landed off the closed-prev seams'
                un = mnr_reset(cp, oob, cross, st, step, sd)[prt]
            for r, sp in zip(res, sps):
                q = (sp == sd) & un
                v10 = np.round(np.where(q, cp[prt], 0.0) * 10.0)
                assert (np.abs(v10) < 32767).all(), 'a Mage value x 10 does not fit an int16'
                for k, top in enumerate(MNR_TOPS):
                    if t > top:
                        continue                 # this line sits above that column's ceiling
                    r[k][0] = np.where(q, t, r[k][0]).astype(np.int8)
                    r[k][1] = np.where(q, v10, r[k][1]).astype(np.int16)
    return [tuple(tuple(c) for c in r) for r in res]


def sl_pct(prt):
    """HIS 1115 STOPLOSS dynamic values. -> int16 [rows]: SL% x 100 at each row's print bar, SL_NONE where none.

    HIS SPEC: *"collect the 15s closed bar abs(price pct diff), between gcws15b extrema (oob to opposing oob), averaged
    over the last 6 hours"* / *"if the pct pattern continued for the full 6 hours, the stop loss would be ~2%"*. HIS
    WALK, from 2026-09-20 09:41:45: *"the lowside oob to ib can only be known when g15b crosses to highside oob, and
    vice-versa"* / *"this allows g15b to "bounce" on the opposing oob until it has completed its time on that side's
    oob"* / *"the timestamp of g15b returning to high oob is 1015:45, and the walk can now detect that the final lowside
    cross from oob to ib was 1013:45"* / *"the highside's final cross to ib is 1035:30, and this is known when g15b
    crossed to lowside oob at 1040"*.

    gcws15b is read on its closed 15 s bars (the value at each 15 s bar's last 5 s bar, the midnight grid), oob at 15/85
    (OOB_LO / OOB_HI). A side's FINAL cross to ib is its last oob -> ib cross before g15b enters the opposing oob, and it
    is known at the close of the 15 s bar that enters - readable from the next 5 s bar, closed-prev. A leg runs from one
    final cross to the next (they alternate sides); its value is abs(price pct diff) of the two 15 s bars' closes (the
    tape's raw close). The row's SL% is the mean of the legs that are known by the print bar and whose end cross is
    inside the 6 h up to it. His 09-20 walk reproduces bar for bar (checked 1115).

    MINE, his to change: the plain mean of the legs, not weighted by leg length; blank (SL_NONE) where no leg ends in
    the window and where the tape has under SL_HOURS behind the print bar; a 15 s bar that goes from one oob straight
    into the other is that side's final cross and the entry on the same bar.
    """
    b = np.asarray(LL.sub_line(SL_LINE), float)
    close = np.asarray(BT.prices()[0], float)
    ts = np.asarray(ln.ts, np.int64)
    cb = np.flatnonzero(((ts + 5000) % 15000) == 0)      # each 15 s bar's last 5 s bar: its closed value and close
    v, px = b[cb], close[cb]
    lo, hi = float(K.OOB_LO), float(K.OOB_HI)
    pts = []                                             # the final crosses: (5 s bar, price, side, known 5 s bar)
    cur, last = 0, {+1: None, -1: None}
    for i in range(1, len(cb)):
        a, z = v[i - 1], v[i]
        if not (np.isfinite(a) and np.isfinite(z)):
            continue
        if a >= hi > z:                                  # HIGH oob -> ib; the latest one is the side's final so far
            last[+1] = i
        if a <= lo < z:                                  # LOW oob -> ib
            last[-1] = i
        for s, enters in ((+1, a < hi <= z), (-1, a > lo >= z)):
            if not enters or cur == s:
                continue                                 # a bounce on the side it is already on changes nothing
            if cur == -s and last[-s] is not None:       # the opposing side is complete: its final cross is known here
                j = last[-s]
                pts.append((int(cb[j]), float(px[j]), -s, int(cb[i])))
            last[-s], last[s], cur = None, None, s
    assert all(pts[k][2] != pts[k + 1][2] for k in range(len(pts) - 1)), 'two final crosses in a row share a side'
    assert all(p[0] <= p[3] for p in pts), 'a final cross is known before its own bar'   # equal: one bar oob to oob
    end = np.asarray([p[0] for p in pts[1:]], np.int64)
    known = np.asarray([p[3] for p in pts[1:]], np.int64) + 1          # readable from the next 5 s bar
    pct = np.asarray([abs(q[1] - p[1]) / p[1] * 100.0 for p, q in zip(pts[:-1], pts[1:])], float)
    cs = np.concatenate([[0.0], np.cumsum(pct)])
    w = int(SL_HOURS * 3600 * 1000)
    k1 = np.searchsorted(known, prt, side='right')                     # legs readable at the print bar
    k0 = np.searchsorted(ts[end], ts[prt] - w, side='left')            # legs whose end cross is inside the 6 h
    n = k1 - k0
    with np.errstate(invalid='ignore', divide='ignore'):
        m = np.where(n > 0, (cs[np.maximum(k1, k0)] - cs[k0]) / np.maximum(n, 1), np.nan)
    m[ts[prt] - ts[0] < w] = np.nan
    out = np.where(np.isfinite(m), np.round(m * 100.0), SL_NONE)
    assert (out < 32767).all(), 'an SL% x 100 does not fit an int16'
    global SL_LEGS
    SL_LEGS = (pts, pct)
    return out.astype(np.int16)


def build():
    """-> (row open ms [n], {(flip, A ws1-ws6, A ws7-ws15): [n, STRIDE] int8 - r-pred per line, then the two sums,
    then the rest}). Row i is the ws1 bar opening at t0 + 60 s * i. The r-pred bytes are the same in every state; every
    byte that reads the pseudo trade (its target-side, towards/away, the cross row's side, M-no-rev) is built per flip,
    and towards/away per A state too. Every towards/away read is at the locked 23/77 fence (HIS 1115)."""
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
    global FLAGGED                               # the 1109 control: its own 14 lines, gcws15 and gcws30 included
    FLAGGED = int(sum((rpred(name)[prt] != 0).sum() for name in CONTROL_LINES))
    sl = sl_pct(prt)
    for _, tfs in SUMS:                          # the same read, summed: -7..+7 and -8..+8, fits int8
        base.append(np.sum([rpred('ws%d' % t)[prt].astype(int) for t in tfs], 0))
    #   HIS 1116 TOP ROW: *"the top row (which currently prints r-pred +1, -1, 0) is replaced by a mech that
    #   calculates if the current ws{tf}r row's value is higher or lower than the same ws{TF}r, 2 rows earlier and 3
    #   rows earlier ... position1 is the diff between current row and current row - 3, and position2 reports on
    #   current row - 2 --this update applies to ws1-15 only"*, and on a dead tie: *"'-'"*.
    #   The r-pred byte stays and still sets the cell's colour - *"keep the r-pred colors as is"*.
    #   THE EMERGING r AT THE ROW'S PRINT BAR, the line r-pred itself reads. Closed-prev was measured and rejected
    #   before this was built: a high-TF closed line does not move between rows 2 and 3 minutes apart, so it ties on
    #   52% of cells against 12.7% for emerging.
    UD = []
    for name in LINES:
        v = np.asarray(E[int(name[2:])], float)[prt]
        code = np.zeros(len(prt), np.int8)
        for bit, back in ((0, 3), (2, 2)):
            with np.errstate(invalid='ignore'):
                up, dn = v[back:] > v[:-back], v[back:] < v[:-back]
            one = np.zeros(len(prt), np.int8)
            one[back:] = np.where(up, 1, np.where(dn, 2, 0))   # 0 is a dead tie OR no row that far back
            code = (code | (one << bit)).astype(np.int8)
        UD.append(code)
    assert len(UD) == len(LINES) and all(0 <= int(c.min()) and int(c.max()) <= 10 for c in UD)
    LN, piv, trades, ST, det = TA.build(FNC)        # the 23/77 run with A off: the first page state
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
    #   HIS 1113 *"flips the pivots directions"*: each pivot's side flips on its own bar, so every pseudo trade keeps
    #   its bars and its target-side flips
    #   HIS 1115 the two A buttons: towards/away runs once per flip and A state, with A (jig.at_extreme `line_extreme`)
    #   on the lift-off reads of the ws1..ws6 r lines, the ws7..ws15 r lines, both or neither. The pivots +15 min and
    #   fence buttons are gone (HIS 1115), so no state moves a pivot and every state reads 23/77
    #   HIS 1117: A is locked, so the states are the pivot offset crossed with the flip - FOUR runs
    #   where there were eight. Every pivot PIV_SHIFT later moves each pseudo trade's open and close
    #   by the same amount on the same side, and towards/away runs again on those trades; the last
    #   trade still closes at the tape's end.
    STATES, SIDES = [], {}
    for off in OFFS:
        k = off * 12                             # 5 s bars
        for fl in FLIPS:
            tr = [(o + k, min(c + k, ln.N), -s if fl else s) for o, c, s in trades if o + k < ln.N]
            t1 = time.time()
            STATES.append((off, fl, ST if not off and not fl else TA.run(LN, tr, FNC, A_TFS)[0]))
            print('state pivots +%d min, flip %d: %d pseudo trades, first opens %s, %.1f s'
                  % (off, fl, len(tr), ln.U(tr[0][0]), time.time() - t1))
            side = np.zeros(ln.N, np.int8)
            for o, c, s in tr:
                side[o:c] = s
            SIDES[(off, fl)] = side
    assert all(np.array_equal(SIDES[(off, 1)], -SIDES[(off, 0)]) for off in OFFS), \
        'a flipped pseudo trade is not the as-found one on the same bars with the other target-side'
    MNR = dict(zip(SIDES, m_no_rev([SIDES[key][prt] for key in SIDES], prt)))
    mats = {}
    for off, fl, ST in STATES:
        side, mnr = SIDES[(off, fl)], MNR[(off, fl)]
        cols = list(base)
        live = side != 0
        sp = side[prt]

        def exf_at(t):
            #   HIS 1109 *"append `(inf)` or `(exf)`"*: ex-20/80 on the target-side by the banked reader - the
            #   one the towards/away mech's own ex-fence test uses (closed-prev, or the emerging 60 s extreme).
            #   HIS 1115: locked at 23/77
            return np.where(sp > 0, TA.exf_mask(LN, t, +1, FNC)[prt], TA.exf_mask(LN, t, -1, FNC)[prt]) & (sp != 0)
        #   TOWARDS/AWAY at the same print bar: 0 no state, 1 TO, 2 AW, and +2 when the line is ex-20/80 on the
        #   target-side there - 3 TO(exf), 4 AW(exf). Then per sum column the TO count and the AW count over its
        #   lines, both -1 where no pseudo trade is open (no target-side, so nothing to count)
        CODE = {}
        for name in LINES:
            t = int(name[2:]) if name.startswith('ws') else 0
            if t not in ST:
                cols.append(np.zeros(len(prt), np.int8))
                continue
            st = ST[t][prt].astype(np.int8)
            CODE[name] = np.where((st != TA.NONE) & exf_at(t), st + 2, st)
            cols.append(CODE[name])
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
            #   HIS 1113 *"in ws1 only, in the same format as any flip to AW(*), highlight the field when ws1 flips to
            #   TO(exf)"*, his answer *"any except TO(exf)"*: +8 on the ws1 row that reads TO(exf) where the row before
            #   read anything else - blank, TO(inf), AW(inf) or AW(exf) - whichever pseudo trade that row is in
            if name == FLIP_TOX:
                cd = CODE[name]
                xc[1:] |= 8 * ((cd[:-1] != TO_EXF) & (cd[1:] == TO_EXF)).astype(np.int8)
            cols.append(xc)
        #   HIS 1111 *"if any of the individual lines are printing TO(exf), print "TO(exf)" under the TO:x AW:x row"*:
        #   per sum column, how many of its lines read TO(exf) - the code a ws1..ws15 cell prints as TO(exf)
        for _, tfs in SUMS:
            cols.append(np.sum([((ST[t][prt] == TA.TO) & exf_at(t)).astype(int) for t in tfs], 0))
        cols.extend(UD)                          # HIS 1116 the up/dn pair per line, the same in every state
        cols.append((sl & 0xFF).astype(np.uint8).view(np.int8))     # HIS 1115 SL%, the same in every state
        cols.append((sl >> 8).astype(np.int8))
        for mn_k, mv_k in mnr:                   # HIS 1117 mnr1 then mnr2: its TF, 0 none, and its value
            cols.append(mn_k)
            cols.append((mv_k & 0xFF).astype(np.uint8).view(np.int8))
            cols.append((mv_k >> 8).astype(np.int8))
        cols.append(side[prt])                   # HIS 1109: the time cell's 20% colour, red LOW, green HIGH
        mats[(off, fl)] = np.ascontiguousarray(np.stack(cols, 1).astype(np.int8))
    return ts[first], mats


T0 = time.time()
OPEN, MATS = build()
RP = MATS[(0, 0)]                               # the pivots as found, A locked, 23/77 - every check below reads it
assert all(m.shape == RP.shape for m in MATS.values()) and RP.shape[1] == STRIDE
assert all(np.array_equal(m[:, :len(LINES) + len(SUMS)], RP[:, :len(LINES) + len(SUMS)]) for m in MATS.values()), \
    'the r-pred bytes differ between the page states'
DAYS = []
for i, ms in enumerate(OPEN):
    d = time.strftime('%Y-%m-%d', time.gmtime(int(ms) // 1000))
    if not DAYS or DAYS[-1][0] != d:
        DAYS.append([d, i])
TAC = RP[:, len(LINES) + len(SUMS):2 * len(LINES) + len(SUMS)]
U = lambda ms: time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(ms) // 1000))
META = json.dumps({
    'lines': LINES, 'mnr': MNR_LABELS[0], 'sums': [s for s, _ in SUMS], 'stride': STRIDE, 'rows': int(len(OPEN)), 't0': int(OPEN[0]), 'step': 60000,
    'days': DAYS, 'fence': FNC, 'abands': [b for b, _ in A_BANDS], 'flips': list(FLIPS),
    'mnrs': list(MNR_LABELS), 'mnrtops': list(MNR_TOPS),
    'shift': PIV_SHIFT, 'alock': list(A_LOCK),
    #   HIS 1116: where the up/dn block starts, so a reader is told rather than re-deriving the layout
    'updn': len(LINES) + len(SUMS) + len(LINES) + 2 * len(SUMS) + len(LINES) + len(SUMS)})


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
            #   HIS 1113 flip: 0 the pivots' sides as found, 1 every side flipped; HIS 1115 alo / ahi: the A buttons,
            #   0 lift-off as built, 1 A on ws1..ws6 / ws7..ws15
            #   HIS 1117: off is the pivot shift and flip the pivot direction. A is locked, so alo
            #   and ahi are accepted only at their banked values.
            _a = (int(q.get('alo', A_LOCK[0])), int(q.get('ahi', A_LOCK[1])))
            m = MATS.get((int(q.get('off', 0)), int(q.get('flip', 0)))) if _a == A_LOCK else None
            if m is None:
                self.send_error(400, 'off must be one of %s, flip one of %s, and alo / ahi the locked %s'
                                % (OFFS, FLIPS, A_LOCK))
                return
            a = max(0, int(q['start'])); b = min(len(m), a + max(0, int(q['count'])))
            return self._send(m[a:b].tobytes(), 'application/octet-stream')    # STRIDE bytes per row
        return self._send(PAGE.encode(), 'text/html; charset=utf-8')


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>fdm3-oracle</title>
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
.tog:disabled{cursor:default;opacity:.7}   /* HIS 1117: a banked A button shows its position, no click */
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
/*   HIS 1117: *"the dn/up rows are printing bold when rpred coloring is applied. ensure that the top row
     (of the cell) is non-bold"*. The red/green r-pred classes put font-weight 600 on the whole cell and the
     top line is a span inside it, so the span gets its own weight. The two <b> lines below keep theirs -
     his *"the ws1 TO(exf) flap and any ws AW(*) flip on the [middle] row needs to stay bolded"*   */
.row div span.ud{font-weight:400}
.row div b.s,.row div b.x{white-space:pre}
.row div b.x{color:var(--xc);font-weight:900}
/*   HIS 1117: *"the columns can be skinny... the cells' data can be wordwrapped, ws{TF} on the top row
     and the line value on the lower row. reduce the font"*. Two lines in the cell's own three-line box,
     so the wrap is deterministic rather than left to the browser   */
.row .mn{font-weight:600;font-size:9px}
.row .mn b{font-size:9px;font-weight:600}
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
<h1>fdm3-oracle - SL%, r-pred ws1 to ws15, M-no-rev, plus the ws16-22 and ws23-30 sums, emerging, on closed-prev ws1 bars, with towards/away</h1>
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
const MNRW = 34;      // px, HIS 1117 *"the columns can be skinny"* - its widest line, "100.0" at 9px, is 25 px
const CW = 72.36;      // px, every line and sum column - HIS 1111 *"stay the same width as they are now"*
const SLW = 48;        // px, HIS 1115 *"skinny column labeled 'SL%', to the right of 'ws1 time'"* - its widest text, "99.99"
let meta, NL, NC, NS, UD0;
//   HIS 1116: the top row's two positions. 0 is a dead tie or no row that far back, and he asked for '-' there
const UDW = ['-', 'up', 'dn', '-'];
const cache = new Map(), pending = new Set();
const box = document.getElementById('box'), body = document.getElementById('body');
const pool = [];
let lastTop = 0, dir = 1, raf = 0, dayOn = '';
const NB = '\u00a0';   // HIS 1110: the place holder line - a blank line keeps a cell's 3 lines aligned
let sel = -1;           // HIS 1110: the clicked row, highlighted; a click on another row moves it, on the same row clears it
let FLIP = 0;           // HIS 1113: 0 the pivots' sides as found, 1 every side flipped with the button on
let OFF = 0;            // HIS 1117: the pivot offset button - 0 the pivots as found, meta.shift minutes later
let ALO = 0, AHI = 0;   // HIS 1117: A is LOCKED, these take meta.alock and no button changes them

const fmt = ms => new Date(ms).toISOString().slice(0, 19).replace('T', ' ');

function fetchBlock(b) {
  const off = OFF, flip = FLIP, key = off + ':' + flip + ':' + b;   // each state keeps its own blocks
  if (b < 0 || b * BLOCK >= meta.rows || cache.has(key) || pending.has(key)) return;
  pending.add(key);
  fetch('rows?start=' + (b * BLOCK) + '&count=' + BLOCK + '&off=' + off + '&flip=' + flip +
        '&alo=' + ALO + '&ahi=' + AHI)
    .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.arrayBuffer(); })
    .then(buf => { pending.delete(key); cache.set(key, new Int8Array(buf)); evict(); schedule(); })
    .catch(e => { pending.delete(key); document.getElementById('err').textContent = 'fetch failed: ' + e.message; });
}
function getBlock(b) {
  const key = OFF + ':' + FLIP + ':' + b, a = cache.get(key);
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
    let mcs = [], slc = null;
    for (let c = 0; c <= NC; c++) {
      if (c === NL + 1) {              // HIS 1111 M-no-rev, between ws15 and the sums; 3 lines like every data cell
        //   HIS 1117: one skinny cell per M-no-rev ceiling, mnr1 then mnr2
        for (const _ of meta.mnrs) {
          const m = document.createElement('div'); m.n = document.createElement('span');
          m.ta = document.createElement('b'); m.xc = document.createElement('b'); m.append(m.n, m.ta, m.xc);
          el.appendChild(m); mcs.push(m);
        }
      }
      const d = document.createElement('div'); d.className = c ? '' : 't'; el.appendChild(d);
      if (!c) {                         // HIS 1115 SL%, right of the time; 3 lines like every data cell
        slc = document.createElement('div'); slc.n = document.createElement('span');
        slc.ta = document.createElement('b'); slc.xc = document.createElement('b'); slc.append(slc.n, slc.ta, slc.xc);
        el.appendChild(slc);
      }
      if (c) { d.n = document.createElement('span'); d.ta = document.createElement('b'); d.append(d.n, d.ta); if (c > NL) d.ta.className = 's'; else d.n.className = 'ud'; }
      if (c) { d.xc = document.createElement('b'); d.xc.className = 'x'; d.append(d.xc); }   // HIS 1110 cross row, every cell
      cells.push(d);
    }
    body.appendChild(el); pool.push({el, cells, mcs, slc, i: -1, ok: false});
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
    //   HIS 1117: mnr1's three bytes then mnr2's, both before the side. ws{TF} on the top line and the
    //   line's closed-prev value under it
    for (let k = 0; k < p.mcs.length; k++) {
      const b0 = o + NS - 1 - 3 * (p.mcs.length - k);
      const mv = blk ? blk[b0] : 0, mx = blk ? ((blk[b0 + 2] << 8) | (blk[b0 + 1] & 255)) : 0;
      const m = p.mcs[k];
      m.n.textContent = !blk ? '·' : mv > 0 ? 'ws' + mv : NB;
      m.ta.textContent = (blk && mv > 0) ? (mx / 10).toFixed(1) : NB;
      m.xc.textContent = NB;
      m.className = (blk ? 'mn' : 'w') + (k === 0 ? ' sx' : '');
    }
    //   HIS 1115 SL%: the mean abs price % of the gcws15b legs (final oob -> ib to final oob -> ib) ending in the last
    //   6 h, x 100 in two bytes; blank where there is none
    const sl = blk ? ((blk[o + NS - 5] << 8) | (blk[o + NS - 6] & 255)) : 0;
    p.slc.n.textContent = !blk ? '·' : sl < 0 ? NB : (sl / 100).toFixed(2);
    p.slc.ta.textContent = NB; p.slc.xc.textContent = NB;
    p.slc.className = blk ? 'sl' : 'w';
    for (let c = 0; c < NC; c++) {
      const d = p.cells[c + 1], sx = c === NL ? ' sx' : '';
      if (!blk) { d.n.textContent = '·'; d.ta.textContent = NB; d.xc.textContent = NB; d.className = 'w' + sx; continue; }
      const v = blk[o + c];
      if (c < NL) {                     // a wsf line: -1 red, +1 green, 0 plain
        //   HIS 1116: the top row prints the UP/DN pair, not the r-pred number. position1 is this row against the
        //   row 3 back, position2 against the row 2 back, and a dead tie prints '-'. The CELL'S COLOUR below still
        //   comes from the r-pred byte - *"keep the r-pred colors as is"*
        const ud = blk[o + UD0 + c];
        d.n.textContent = UDW[ud & 3] + ' | ' + UDW[(ud >> 2) & 3];
        const s = blk[o + NC + c];      // HIS 1109: TO or AW below the number, bold
        //   HIS 1110: a -1 / +1 on an AW line (code 2 AW(inf), 4 AW(exf)) prints its background at 55% opaque
        //   HIS 1117: *"drop the rpred coloring for all but the 2 combined columns (ws16-22 and
        //   ws23-30)"*. A ws line cell carries no red, green or grey now, and the 55% AW background
        //   went with it - that class only ever shaded the red and the green
        d.className = '';
        d.ta.textContent = ['', 'TO(inf)', 'AW(inf)', 'TO(exf)', 'AW(exf)'][s] || NB;   // HIS 1109 (inf) / (exf)
        //   HIS 1110: crossovers on a LOW target-side, crossunders on HIGH; X and E on one ws1 bar join, 4 spaces apart
        const xc = blk[o + NC + NL + 2 * (NC - NL) + c];
        d.xc.textContent = [xc & 1 ? (sd < 0 ? 'X↑' : '↓X') : '', xc & 2 ? (sd < 0 ? '↑E' : '↓E') : '']
          .filter(Boolean).join('    ') || NB;
        d.ta.className = xc & 12 ? 'f' : 'g';  // HIS 1110: TO on the row before, AW on this one - white, this row only;
                                               // HIS 1111: every other TO/AW grey, on a -1/+1 cell too;
                                               // HIS 1113: ws1 only, TO(exf) after anything else - white, the same way
      } else {                          // a sum, HIS 1109: red below 0, green above 0, orange at 0
        d.n.textContent = v > 0 ? '+' + v : String(v);
        d.className = (v < 0 ? 'm' : v > 0 ? 'p' : 'o') + sx;
        const k = o + NC + NL + 2 * (c - NL), to = blk[k], aw = blk[k + 1];
        d.ta.textContent = to < 0 ? NB : 'TO:' + to + '  AW:' + aw;   // HIS "TO:x  AW:x", the weekday size
        //   HIS 1111: "TO(exf)" under it when any of the column's lines reads TO(exf); the TO:x AW:x line's style.
        //   HIS 1113 *"add the count of TO(exf) lines, if TO(exf) is printing"*: "TO(exf):x"
        const tx = blk[o + NC + 2 * NL + 2 * (NC - NL) + (c - NL)];
        d.xc.textContent = tx > 0 ? 'TO(exf):' + tx : NB;
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
  NL = meta.lines.length; NC = NL + meta.sums.length; NS = meta.stride; UD0 = meta.updn;
  [ALO, AHI] = meta.alock;   // HIS 1117: A is locked, the page only reports it
  const hd = document.getElementById('hd');
  for (const h of ['ws1 time (UTC)', 'SL%'].concat(meta.lines, meta.mnrs, meta.sums)) { const d = document.createElement('div'); d.textContent = h; hd.appendChild(d); }
  hd.children[NL + 2].className = 'sx'; hd.children[NL + 3].className = 'sx';
  body.style.height = (meta.rows * RH) + 'px';
  //   HIS 1111: no sideways bar. The lines stay CW; the time column takes what is left, then M-no-rev and the
  //   sums give way together
  //   HIS 1115 *"keep the table's existing columns at their current width, ie don't attempt to fill the lost column space"*:
  //   the box narrows by the two dropped columns, less the SL% column
  //   HIS 1117: the one wide M-no-rev column becomes two skinny ones
  const inner = box.firstElementChild, tw = TW + SLW + NC * CW + meta.mnrs.length * MNRW;
  inner.style.setProperty('--gt', 'minmax(' + TMIN + 'px,1fr) ' + SLW + 'px repeat(' + NL + ',' + CW + 'px) repeat(' +
                          meta.mnrs.length + ',' + MNRW + 'px) repeat(' + (NC - NL) + ',minmax(' + SMIN + 'px,' + CW + 'px))');
  //   after the body's height, so the vertical scrollbar is in the box's width
  document.querySelector('.wrap').style.maxWidth = (tw + box.offsetWidth - box.clientWidth + 32) + 'px';
  buildCal();
  //   HIS 1113 *"add a button that flips the pivots directions, ie the green rows will become the red rows and vice
  //   versa"*, on the right of the calendars. No button changes the scroll position (his 1112 positioning rule):
  //   the rows on screen stay where they are and only their cells change
  const fp = document.createElement('button'); fp.className = 'tog'; fp.textContent = 'flip pivots';
  fp.title = 'flip the side of every ws2Mage pivot, so a HIGH pivot reads LOW and a LOW pivot HIGH; click again for the sides as found';
  fp.setAttribute('aria-pressed', 'false');
  fp.onclick = () => {
    FLIP = FLIP ? meta.flips[0] : meta.flips[1];
    fp.classList.toggle('on', FLIP > 0); fp.setAttribute('aria-pressed', String(FLIP > 0));
    for (const p of pool) p.ok = false;
    schedule();
  };
  document.getElementById('cal').appendChild(fp);
  //   HIS 1115 *"create two buttons that A will be applied to - the first button shows A for ws1-ws6, and the second
  //   shows A for ws7-ws15"*. A: lift-off's window extreme off every bar of its span, not only the six samples. They
  //   combine with each other and with flip pivots
  //   HIS 1117: *"I need the 'pivot +15 min' button reintroduced on 8790. instead of +15, make it
  //   +30 minutes"*. Every ws2Mage pivot meta.shift minutes later, so every pseudo trade opens and
  //   closes that much later on the same side
  const pb = document.createElement('button'); pb.className = 'tog';
  pb.textContent = 'pivots +' + meta.shift + ' min';
  pb.title = 'every ws2Mage pivot ' + meta.shift + ' minutes later; click again for the pivots as found';
  pb.setAttribute('aria-pressed', 'false');
  pb.onclick = () => {
    OFF = OFF ? 0 : meta.shift;
    pb.classList.toggle('on', OFF > 0); pb.setAttribute('aria-pressed', String(OFF > 0));
    for (const p of pool) p.ok = false;
    schedule();
  };
  document.getElementById('cal').appendChild(pb);
  //   HIS 1117 banked A: the two buttons show the locked positions and cannot be clicked
  for (const [i, band] of meta.abands.entries()) {
    const ab = document.createElement('button'); ab.className = 'tog'; ab.textContent = 'A ' + band;
    const on = meta.alock[i];
    ab.title = 'lift-off A on the ' + band + ' r lines: BANKED ' + (on ? 'on' : 'off') + ', not a button';
    ab.disabled = true;
    ab.classList.toggle('on', on > 0); ab.setAttribute('aria-pressed', String(on > 0));
    document.getElementById('cal').appendChild(ab);
  }
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
    _j = LINES.index(FLIP_TOX)
    print('%s flips into TO(exf) (white TO(exf) text): %d, other columns marked %d'
          % (FLIP_TOX, int((_xc[:, _j] & 8).astype(bool).sum()), int((_xc & 8).astype(bool).sum() - (_xc[:, _j] & 8).astype(bool).sum())))
    _rp = RP[:, :len(LINES)]
    #   HIS 1117 dropped the r-pred colour from the line cells, so this no longer describes a
    #   background the page draws - it stays as the 1110 measurement of the same cells
    print('r-pred -1/+1 cells on an AW line (the 1110 measurement): %d of %d flagged, all %d columns'
          % (int(((_rp != 0) & ((TAC == 2) | (TAC == 4))).sum()), int((_rp != 0).sum()), len(LINES)))
    #   HIS 1117 two columns: mnr1's bytes sit at STRIDE-7..-5 and mnr2's at STRIDE-4..-2
    _MNR = [(RP[:, STRIDE - 1 - 3 * (len(MNR_TOPS) - k)].astype(int),
             (RP[:, STRIDE - 1 - 3 * (len(MNR_TOPS) - k) + 2].astype(int) << 8)
             | (RP[:, STRIDE - 1 - 3 * (len(MNR_TOPS) - k) + 1].astype(int) & 255))
            for k in range(len(MNR_TOPS))]
    for k, (label, _) in enumerate(SUMS):
        _ex = RP[:, 3 * len(LINES) + 3 * len(SUMS) + k].astype(int)
        print('%s: rows printing TO(exf) %d of %d, most lines reading TO(exf) on one row %d'
              % (label, int((_ex > 0).sum()), len(_ex), int(_ex.max())))
    for _lab, _top, (_mn, _mv) in zip(MNR_LABELS, MNR_TOPS, _MNR):
        print('%s (ws%d..ws%dMage): rows printing a TF %d of %d, highest TF printed %d, value %.1f .. %.1f'
              % (_lab, MNR_LO, _top, int((_mn > 0).sum()), len(_mn), int(_mn.max()),
                 _mv[_mn > 0].min() / 10, _mv[_mn > 0].max() / 10))
    print('fence: %d/%d, locked (HIS 1115)' % (FNC, 100 - FNC))
    for (_off, _fl), _m in MATS.items():
        if (_off, _fl) == (0, 0):
            continue
        _tac = _m[:, len(LINES) + len(SUMS):2 * len(LINES) + len(SUMS)]
        print('pivots +%d min%s: rows whose target-side differs from the pivots as found %d of %d, cells '
              'that differ %d of %d; TO(inf) %d, AW(inf) %d, TO(exf) %d, AW(exf) %d'
              % ((_off, ', flipped' if _fl else '',
                  int((_m[:, STRIDE - 1] != RP[:, STRIDE - 1]).sum()), len(RP), int((_m != RP).sum()), RP.size)
                 + tuple(int((_tac == k).sum()) for k in (1, 2, 3, 4))))
        if _alo or _ahi:
            print('    TO/AW cells moved by A, against the same pivots with A off: '
                  + ', '.join('%s %d' % (n, int(c)) for n, c in zip(LINES, _dc) if c))
    print('towards/away knobs (banked): ' + ' '.join('%s=%s' % (k, v) for k, v, _, _ in TA.KNOBS))
    print('open http://127.0.0.1:%d' % PORT)
    sys.stdout.flush()
    ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
