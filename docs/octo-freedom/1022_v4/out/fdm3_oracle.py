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
                  HIS 1124 SUPERSEDES THE "no disk cache": *"the rows are a small file - it should be kept on
                  disk as well as in memory to avoid downtime on small cosmetic changes or restarts"*. The rows
                  are on disk too, per page settings, and a start-up reads them only when every source module,
                  data file and database read its full start-up used is unchanged - see rows_from_cache_or_build.
                  The start-up itself runs in a forked child since his 1124 "Free start-up only", so a serving
                  page holds the rows and little else.
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
Both are jig.race_wins over the whole tape, per side, EACH IN ITS OWN RACE - the race
lift-off's e path uses (v4_lift_e.race: the 15/85 boundary, closed-prev ws{TF}Mage, closed-prev ws{TF}r; first line
crossed wins; no hold) - with ws{TF}e or ws{TF}x (emerging) as the crossing line. HIS 1118 set the ws{TF}x race's
re-open to B, crossing back over ANY of the three; ws{TF}e keeps his 1109 4B, crossing back over the winner.
STRUCK 1118: this note used to read *"His answer on the x-cross: raw, no hold"* and no such words of his exist -
he never ruled an x-cross race or hold. Reusing the e race on the x line was MINE. A cross prints on the row
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

HIS 1112 PIVOT BUTTON, back at his 1117 and at 15 minutes again since his 1119. It moves every pivot that much later
(his 1112 *"move the pivots forward 15 minutes"*), so every pseudo trade opens and closes later on the same side.

HIS 1112 TOWARDS/AWAY UPDATE: *"I want to see the flip from TO to AW based on the x and e cross."* No page change: the
TO/AW codes come from towards_away.run, which now carries the 50 reset, the excursion sample on e and x, the void
values, the row rule and the x/e path (spec section 12). Both pivot states read it.

HIS 1113 FENCE BUTTON, REMOVED HIS 1115 *"23/77 has proven to be the best option, so we can remove that button and lock
23/77 for the UI"*. Every towards/away read on the page - the reach, the scenario-1 vote, the pair's in-fence samples,
the x/e path's in-fence extremum - and the (inf)/(exf) tags and the sums' TO(exf) read 23/77 (FNC). The read itself
is unchanged: closed-prev OR the emerging extreme of the last 12 bars. Where a paragraph below says ex-20/80, the page
now reads ex-23/77. The banked towards/away run outside the page is still 20/80.

HIS 1113 FLIP BUTTON: *"add a button that flips the pivots directions, ie the green rows will become the red rows and
vice versa"*. With the button on, every pivot's side is flipped on its own bar - a HIGH pivot reads LOW and a
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
import hashlib
import io
import json
import os
import shutil
import sys
import time

import numpy as np

T_START_NS = time.time_ns()                     # HIS 1124 row cache: an input edited after this is not trusted
_SELF = os.path.realpath(__file__)
V4 = '/home/joe/thecodes/docs/octo-freedom/1022_v4'
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, V4)
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
os.chdir(V4)                                    # the tape is cwd-sensitive - every run prints its bar count
#   HIS 1124 *"the rows are a small file - it should be kept on disk as well as in memory to avoid downtime on small
#   cosmetic changes or restarts"*. The row cache (rows_from_cache_or_build, below) is read only when every input of the
#   start-up is what it was when the rows were built, so a changed line, knob or rule can never be served stale. So
#   this process RECORDS ITS INPUTS AS IT READS THEM, from here on: every file numpy loads, and every database read with
#   a hash of what came back. MINE, structural: what counts as an input and how each is compared.
_LOADED = set()
_np_load = np.load


def _np_load_rec(f, *a, **k):
    if isinstance(f, (str, os.PathLike)):
        _LOADED.add(os.path.realpath(os.fspath(f)))
    return _np_load(f, *a, **k)


np.load = _np_load_rec
_DBREADS = {}
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    from optimus9.db import database_manager as _DBMOD
finally:
    sys.stderr = _e
_db_exec = _DBMOD.DatabaseManager.execute


def _db_exec_rec(self, sql, params=(), *, fetch=False):
    out = _db_exec(self, sql, params, fetch=fetch)
    if fetch:
        _DBREADS[(sql, repr(tuple(params)))] = hashlib.sha1(repr(out).encode()).hexdigest()
    return out


_DBMOD.DatabaseManager.execute = _db_exec_rec
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
ROWS_CHECK = os.environ.get('FDM3_ROWS_CHECK', '0') == '1'      # HIS 1124 row cache: say whether it would be read, then stop
ROWS_REBUILD = os.environ.get('FDM3_ROWS_REBUILD', '0') == '1'  # HIS 1124 row cache: ignore it, start up in full
if __name__ == '__main__' and not ROWS_CHECK:
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
#   HIS 1124: *"I need a parallel webservice built, named fdm3-htf-oracle.  fdm3-htf-oracle will clone fdm3-oracle, and
#   replace all columns except `ws1 time` with these new columns:"* / *"ws20,21,22,23,24,25,26,27,28,29,30,45,60,90,120,240"* /
#   *"these replacement columns will print the same data as fdm3-oracle's ws1-15 fields"* / *"the rows will be per 1
#   minute seam (not 30s)"*. ONE FILE SERVES BOTH, the way every earlier clone of this page was a setting on it: FDM3_PAGE
#   'htf' is fdm3-htf-oracle (out/fdm3_htf_oracle.py sets it), anything else this page as it was. MINE, structural:
#   one file rather than a copy, and the setting's name.
PAGE_MODE = os.environ.get('FDM3_PAGE', 'oracle')
assert PAGE_MODE in ('oracle', 'htf'), PAGE_MODE
HTF = PAGE_MODE == 'htf'
HTF_COLS = (20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 45, 60, 90, 120, 240)   # HIS 1124, his order
LINES = ['ws%d' % t for t in range(1, 16)]      # HIS 1109 wsf + ws13..ws15 HIS 1111; HIS 1115 *"drop the gcws15 and gcws30
#                                                 columns"*
SUMS = [('ws16-22', range(16, 23)), ('ws23-30', range(23, 31))]   # HIS 1111 two right columns (1109: ws13-20, ws21-30)
if HTF:                                         # HIS 1124: his 16 columns are every column but the time; no sums
    LINES, SUMS = ['ws%d' % t for t in HTF_COLS], []
CONTROL_FLAGGED = 257295        # 1109 measurement: the 14 wsf columns' cells at -1 or +1, whole tape
CONTROL_LINES = ['gcws15', 'gcws30'] + ['ws%d' % t for t in range(1, 13)]   # the 1109 control's 14 lines - gcws15 and
#                                 gcws30 are still read for it, though the page no longer shows them (HIS 1115)
SL_LINE = 'gcws15b'             # HIS 1115 STOPLOSS: *"between gcws15b extrema (oob to opposing oob)"*, on 15 s closed bars
SL_HOURS = 6.0                  # HIS 1115 *"averaged over the last 6 hours"*
SL_NONE = -1                    # SL% x 100 where no leg ends in the window, or the tape has under 6 h behind the row
#   HIS 1117: *"I can't decide between ws15 and ws25, so we'll need two m-no-rev columns - one for
#   each. the columns can be skinny. label them mnr1 and mnr2"*. mnr1 is the LOWER ceiling.
#   HIS 1119: *"I'm not using the m-no-rev column. drop it and replace it with a new max Mage TF
#   column that repeats the value on every row of the leg"*. mnr1 and mnr2 are gone, and one column
#   takes their place.
#   THE VALUE IS THE INCOMING LEG'S, STAMPED AT THIS LEG'S OPEN AND CARRIED UNCHANGED. That is what
#   makes it causal AND constant across the leg: the max over THIS leg would need bars that have
#   not happened yet on every row but the last. It is also the quantity he asked about: *"the max
#   oob is derived during the period where an incoming trade ends and an outgoing trade begins. how
#   do we make sure that the max oob seen at the pivot is consumed by the outgoing trade?"*
MNR_LABELS = ('legMage',)
MNR_TOPS = (15,)                # the climb runs ws1..ws15
MNR_LO = 1                      # HIS 1117: *"we'll settle on ws1 to ws25"* - ws1 adds no leg end that
#                                 ws2 does not already give, but he keeps it: *"m-no-rev is a 'keep
#                                 walking' gate, not a 'bet the bank on it' event"*
MNR_RESET = True                # HIS 1117 closed-prev resume, on. False restores the 1111 column
#                                 exactly, for his A/B
#   HIS 1117: *"now I want to see oracle printing rows that are 30sec apart"* / *"my need is
#   per-30s AW/TO data and per-30s x/e cross data"*. The row is a 30 s slot, read where closed-prev
#   shows that slot - ROW_S / 5 bars on, as the minute row was read 12 bars on.
#   SECONDS PER ROW. FDM3_ROW_S=60 is the 1117 minute grid, one ws1 bar; 30 is his 1117 30 s grid, so
#   one file serves both sides of the A/B and they differ by the row step alone - same columns, same
#   M-no-rev ceilings, r-pred off on both.
#   HIS 1122 *"make this the machine"* and his answer *"Move them"*: 30 is the default, so a launch with no settings
#   serves the machine. It was 60.
ROW_S = int(os.environ.get('FDM3_ROW_S', 60 if HTF else 30))   # HIS 1124 fdm3-htf-oracle: *"per 1 minute seam (not 30s)"*
assert 60 % ROW_S == 0 and ROW_S % 5 == 0, 'a row must be a whole number of 5 s bars and divide a minute'
#   HIS 1117: *"I'm not using r-pred at all so it can be disabled"*. The per-line r-pred byte and the
#   two sums' r-pred byte are gone from the row; the two sum COLUMNS stay for their TO:x AW:x and
#   TO(exf) lines, which are towards/away reads, not r-pred. The 1109 control still computes the
#   r-pred of its own 14 lines, so the producer stays honest - it is just not stored or drawn.
RPRED_ON = False
#   HIS 1124/1125 fdm3-htf-oracle's two VWAP columns on the far right, ws5 then ws10 - docs/fdm3/fdm3_vwap.py has his
#   words, his answers and the rule. Per TF six int16 (% x 100, low byte first): lo udist, lo vdist, lo ldist, hi udist,
#   hi vdist, hi ldist. They read no trade, so every state carries the same bytes. None on fdm3-oracle.
VW_TFS = (5, 10) if HTF else ()
VW_BYTES = 12 * len(VW_TFS)
VW_NOTE = []                    # the start-up's VWAP lines, one per TF - a list so the child can hand it back
STRIDE = (len(LINES) + 2 * len(SUMS) + len(LINES) + len(SUMS) + VW_BYTES
          + len(LINES) + 3 + len(MNR_TOPS))      # bytes per row:
#   the TO/AW codes, the TO/AW counts, the cross codes (HIS 1110: 1 X, 2 E, 3 both, on the row's target-side; +4 the
#   line reads AW on this row and TO on the row before, HIS 1110 TO -> AW flip; +8 ws1 only, TO(exf) on this row and
#   anything else on the row before, HIS 1113), per sum the count of its lines
#   reading TO(exf) (HIS 1111), HIS 1116 the UP/DN pair per line (bits 0-1 position 1, this row against the row 180 s
#   back; bits 2-3 position 2, against the row 120 s back; 0 a dead tie or no row that far back, 1 up, 2 dn) with
#   HIS 1118 the EMERGING Mage's side of 50.00 in bits 4-5 of the same byte (0 neither, 1 over, 2 under),
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
#   HIS 1117: *"The 33/67 reset is your workmate's work, uncommitted" / "take ownership of this and
#   build it into 8790"*. HIS 1115 SPEC: *"I want to simply swap the static 50 'line' with a
#   (100 - {knob:33,`fdm3-fence-reset-TO`}) 33/67 fence"* / *"the mech will reset r to TO if it
#   crosses into the fence then crosses out if the fence on the sameside as the infence incursion"* /
#   *"if the line continues through the fence entirely (eg travels from 90 to 30, then back to 80)
#   the same logic applies: the r will be tagged TO when r crosses over 67"*. towards_away.run takes
#   it as `rst`: the flip at 50, the 50 reset and the void all read the fence's target-side line - 67
#   on a HIGH target-side, 33 on a LOW one, his *"Q1: move them to the fence"*. BANKED here, no
#   button: every page state reads it.
FENCE_RESET_TO = 33.0           # his `fdm3-fence-reset-TO`, the smaller end of the pair
#   HIS 1118: the ws1..ws15 cell carries its ws{TF}Mage's side of 50 as a background - green over
#   50.00, red under it. He set the strength by eye off a test that stepped 100% down to 0% in
#   tens: *"the setting at 0726 is perfect"*, and 07:26 fell in the 20% step. BANKED, no button.
#   THE READ IS EMERGING, his 1118 *"my bad: use emerging"*.
MAGE50_PCT = 20                 # his `fdm3-oracle-mage50-pct` (MY name) - per cent, 0 paints nothing
#   HIS 1118, after reading what the 1109 re-open does to ws6x on 09-24: *"lines move all the time
#   and there is no gaurantee that they will be available for the reset. the only workable answer is
#   B"*. B is: a race re-opens when the line crosses back over ANY of its three race lines, not only
#   over the one that won. HIS ws{TF}x ROW ONLY - he ruled it looking at the x-cross row, and the
#   ws{TF}e row keeps his 1109 4B until he rules on it.
X_REOPEN = 'any'                # his B, the ws{TF}x race's re-open
E_REOPEN = 'winner'             # his 1109 4B, unchanged - the ws{TF}e race
#   HIS 1118, asked whether B reaches the towards/away ws{TF}x races - the 1112 row rule and the
#   hunt samples - as well as the cross row: *"the only way to answer is a button on 8791"*. So this
#   process builds BOTH towards/away states when FDM3_XRE_BUTTON=1 and the page carries a button;
#   with it off there is one state and no button, which is what 8790 runs. Each extra state is a
#   full towards/away run, so the button roughly doubles the start-up.
#   HIS 1119 *"yes"*, the button comes out. It moved 9,313 of 4,082,385 TO/AW cells - 0.23%, and
#   only ever TO(inf) into AW(inf) - for eight extra minutes of start-up. The ws{TF}x CROSS ROW
#   stays at his B permanently (X_REOPEN above); this was only ever the towards/away x races.
XRES = ('winner',)
#   HIS 1118: *"create a test UI with these new pivots"*. With FDM3_PIVOTS=pooled the page imports
#   sweep-pivots' four-read pivot trades instead of towards_away.pseudo_trades's ws2Mage ones. Every
#   TO/AW cell follows, because towards/away runs on whatever trades it is handed.
#   HIS 1120 SRP, *"the pivots can't belong in any fdm3 classes"*: the pivots' rule, knobs, sets and
#   LOOKAHEAD are sweep-pivots' - v4_sweep_pivots.py and v4_sweep_pivots.md section 10. This page
#   only picks which producer and which set it imports.
#   WHICH PRODUCER MAKES THIS PAGE'S PSEUDO TRADES. Every TO/AW cell, every count and the row's side
#   byte are scoped to a trade, so this one env var decides what the whole page means:
#     'ws2Mage'  towards_away.pseudo_trades - the ws2Mage leg extremes, 1564 trades on the tape.
#     'pooled'   v4_sweep_pivots.pooled_trades at sweep-pivots' bank - 3006 trades.
#   IT IS PUBLISHED IN /meta AS `pivots`, because a reader cannot infer it and must not guess: the
#   fdm3 probe scored ws2Mage trades against a pooled page until his 1119 caught it, and on 09-24
#   the two target-sides were opposite on 679 of 2880 rows.
#     'two'      HIS 1122 *"instead of using pivots to create legs, I now want two continuous trades that run for the
#                full window's length, one short and the other long.  I'll use a button to flip between the 2
#                trades"*. No pivots: one trade from the tape's first bar to its end, and the flip button's set is
#                the other one on the same bars. His answers: legMage and fdm3-small-trade *"Blank both"*.
#   HIS 1122 *"Move them"*: 'two' is the default - the machine. It was 'ws2Mage'; 8792 passed 'pooled'.
PIVOTS = os.environ.get('FDM3_PIVOTS', 'two')
assert PIVOTS in ('ws2Mage', 'pooled', 'two'), PIVOTS
A_TFS = [t for (_, band), on in zip(A_BANDS, A_LOCK) if on for t in band]
#   HIS 1119: *"rebuild 8792 with a pivot +15 minute button , and drop pivot +30 button"*, and he
#   ruled it for all three pages, so the +30 button is gone everywhere. It was his 1112 value, went
#   to 30 at his 1117 *"instead of +15, make it +30 minutes"*, and is back at 15.
import v4_sweep_pivots as SP    # noqa: E402 - HIS 1120 SRP: the pivot sets and their knobs are sweep-pivots'
PIV_SHIFT = SP.SET_SHIFT_MIN    # minutes, sweep-pivots' +15 set - HIS 1119, was 30 at his 1117 and 15 at his 1112
OFFS = (0, PIV_SHIFT)           # the pivots as found, and every pivot PIV_SHIFT later
if PIVOTS == 'two':
    OFFS = (0,)                 # HIS 1122 two trades: no pivots, so no +15 set to import and no +15 button
FLIP_TOX = 'ws1'                # HIS 1113: the one line whose flip into TO(exf) is highlighted, *"in ws1 only"*
#   HIS 1120: *"currently, a flip to AW from TO(exf) is highlighted in white"* / *"keep this in place, and add a white
#   highlight on TO(inf) if the previous row was TO(exf). eg, 09-30 0649 and 0649:30"*, his answer *"ws5 only"*, on
#   8792 and 8788. +16 in the cross code on the ws5 row that prints TO(inf) where the row before printed TO(exf),
#   whichever pseudo trade that row is in - the TO -> AW flip's own rule for the row before.
FLIP_TOINF = 'ws5'              # the one line whose TO(inf) after TO(exf) prints white
#   HIS 1124 fdm3-htf-oracle has no ws1 or ws5 column; his answer *"On every column"* puts both highlights on all 16
FLIP_TOX_LINES = tuple(LINES) if HTF else (FLIP_TOX,)
FLIP_TOINF_LINES = tuple(LINES) if HTF else (FLIP_TOINF,)
TO_INF = 1                      # the TO/AW code a cell prints as TO(inf), whatever its in-fence band
TO_EXF = 3                      # the TO/AW code a cell prints as TO(exf): TO 1, +2 ex-fence on the target-side
#   HIS 1119 `fdm3-infence-power`: *"for every TO(inf) line, add a suffix based on these critreria"*,
#   with his five bands, and his ruling on the 7.9% of cells his bands did not reach - a -3 band
#   under the low edge and a +3 band at or over the high one. The cause of those cells: the ex-fence
#   test reads the TARGET side only, so a HIGH target-side line is in-fence at any value under 77.
#   HIS *"all values are 2dp: eg 62 to 73 is actually 62.00 to 72.99"*, so the value is ROUNDED to
#   2dp and then placed. THE VALUE IS THE r THE KNOB INFENCE_READ NAMES (IFP_READ below): the
#   closed-prev r on the bank, the banked chart-matched read; the emerging r on his 1120 8788.
#   HIS 1121 on 8793: *"add  +4 and -4 ranges.  100-92  for '+4' and 0-8 for '-4'"* / *"adjust +3 and -3 to fit
#   accordingly"*. The edges are the banked knob INFENCE_EDGES: 23 28 38 62 73 77 on the bank, 8 and 92 added on 8793. The
#   labels follow the count - 2n edges give -n .. +n - and the band+1 sits in bits 3-6, so +4 is 9 and every band read
#   masks with 15. Bit 7 stays clear: 6 | 9 << 3 is 78.
import fdm3_knobs_shim as _FKS  # noqa: E402 - the banked fdm3 knobs, from the page's own directory
IFP_EDGES = tuple(_FKS.INFENCE_EDGES)
assert len(IFP_EDGES) % 2 == 0 and list(IFP_EDGES) == sorted(set(IFP_EDGES)), IFP_EDGES
IFP_LABELS = tuple('%+d' % k if k else '0' for k in range(-len(IFP_EDGES) // 2, len(IFP_EDGES) // 2 + 1))
assert len(IFP_LABELS) <= 15, 'the band+1 has four bits'
#   HIS 1121 on 8793: *"for coloring: when a highband line (ws8-15) flips from +4 to +3, or from -4 to -3, print the 3
#   in red"*, his answers "Yes, suffix alone", "+3 / -3, sign and digit" and "Yes, any drop off ±4". +32 in the cross
#   code on a ws8..ws15 row whose suffix is under +4 where the row before printed +4, or over -4 where the row before
#   printed -4, whatever the tag on either row - that row only, whichever pseudo trade the row before is in, the TO ->
#   AW flip's own rule for the row before. Only a page with his +4 and -4 has them, so a seven-band page never sets it.
#   HIS 1122: *"there is a red colouring applied to hband (high band lines) when 4 flips to 3.  expand the red colour
#   mech's coverage to include ws2-ws15"*. The rule is unchanged; only its lines move from ws8..ws15 to ws2..ws15.
IFP_RED4 = len(IFP_LABELS) == 9
RED4_TFS = tuple(_FKS.RED4_TFS)  # HIS 1122 the lines the red suffix reads, the fdm3 knob RED4_LINES: ws2..ws15 on the
#                                  bank, ws8..ws15 at his 1121 and on 8794 at his answer *"As it was"*
#   HIS 1124 fdm3-htf-oracle, the b9 colours - *"I'm now refering to the 9 bands as `b9`"* / *"a (+/-) 4 to 3 change will
#   still be coloured in red"* / *"for any of (+/-) 3 to 2, 2 to 1, 1 to 0,  where the change has moved to a band that is
#   counter trade (existing behaviour), the number will be coloured orange"*. His answers: counter trade is *"Against the
#   trade's side"* - on the short trade (target-side LOW) a move UP, on the long trade (target-side HIGH) a move DOWN;
#   *"Red against trade only"*; and *"Orange on any such move"*, more than one band too. So on a row whose suffix moved
#   against the row's target-side from the row before: red when the row before printed -4 (short) / +4 (long), orange
#   when it printed -3, -2 or -1 (short) / +3, +2 or +1 (long). +64 in the cross code, red's +32 beside it. On all 16
#   columns. This page (fdm3-oracle) keeps its red as it is.
if HTF:
    RED4_TFS = tuple(HTF_COLS)
IFP_REDN = [0]                  # ws2..ws15 cells whose suffix prints red, counted across every state
IFP_ORGN = [0]                  # HIS 1124 fdm3-htf-oracle: cells whose suffix prints orange, counted across every state
IFP_DP = 2                      # his 2dp - the value is rounded before it is placed
IFP_BARE = [0]                  # TO(inf) cells with no value to band, counted across every state
IFP_INF = [0]                   # TO(inf) cells in all, so the bare share is readable
#   HIS 1119 `fdm3-small-trade`: *"can you turn this small-trade detector into a causal mech? it would
#   have to evolve with the walk - the resting state is `small-trade` until the mech(s) prove
#   `large-trade`"*, on his ruling *"highband lines printing TO(exf) during the trade:  2 is the max
#   for a small trade."*, then *"print it underneath the existing 'legmage' data.  the labels will be
#   `sml` and `lrg`"*, held to the trade's close. One bit of the legMage byte - legMage is ws1..ws15,
#   bits 0-3 - so the row stays 55 bytes, and every legMage read masks with 15.
SMALL_HI = tuple(range(8, 16))  # his highband, ws8..ws15
SMALL_LRG = 64                  # the bit in the legMage byte: set = `lrg`, clear inside a trade = `sml`
SMALL_ROWS = [0, 0]             # rows inside a trade, and of them `lrg`, over every state
LRG_AF = {}                     # HIS 1121 B: each as-found state's `lrg`, which a carried state must match on shared rows
CARRY_SHARED = [0]              # HIS 1121 B: bars where a carried +15 state was asserted equal to its as-found state
CARRY_ROWS = [0]                # HIS 1121 B: rows where a carried +15 page state was asserted equal to the as-found page
SMALL_MAX = int(_FKS.SMALL_TRADE_MAX_TOEXF)     # his `fdm3-small-trade-max-toexf`, 2 lines
#   HIS 1120: *"duplicate 8792 onto 8788, with one change: AW(inf) cells get the same 7 in-fence
#   bands as TO(inf), and all 14 bands use emerging bars instead of closed-prev"*. THE r THE BAND
#   READS is the banked knob INFENCE_READ: 'closed_prev' on the bank, 'emerging' on 8788 as an
#   off-ruled run. Only the band moves - the TO/AW code and its ex-fence test read what they read.
#   HIS 1121, on 8793 as a clone of 8792: *"instead of the 7 bands updating on closed-prev, I now want them to all
#   update per closed-prev minute"* / *"ws12 will now print 12 updates over 12 minutes, instead of 1 update per 12
#   minutes"*. 'closed_prev_minute' is the closed-prev arithmetic at 60 s on every line's emerging r: the value at the
#   last 5 s bar of the last closed minute. ws1 reads what it read; ws2..ws15 step once a minute.
#   HIS 1122: *"instead of testing values on the 1 minute seam (current behaviour for all TFs), now the seam will be
#   every 30sec.  it should fire at x:25 and x:55 so that oracel has the most current data"*. 'closed_prev_30s' is the
#   same arithmetic at 30 s: the value at the last 5 s bar of the last closed 30 s slot, the x:25 or x:55 bar. A row's
#   print bar opens at x:00 or x:30, so every row reads the bar just before it.
IFP_READ = _FKS.INFENCE_READ
assert IFP_READ in ('closed_prev', 'emerging', 'closed_prev_minute', 'closed_prev_30s'), IFP_READ
IFP_KEY = {'closed_prev': 'CPR', 'emerging': 'EMR', 'closed_prev_minute': 'EMR', 'closed_prev_30s': 'EMR'}[IFP_READ]
IFP_SEAM_S = {'closed_prev_minute': 60, 'closed_prev_30s': 30}.get(IFP_READ)   # the seam in seconds, None = no seam   # towards_away.load()'s
#   HIS 1121 on 8793: *"we'll add the suffix to TO/AW(exf) now.  this addition will serve to  highlight diffs between
#   the closed-prev derived 'exf', and the more granular 1m seams"*, his answers 8793 only and "-(exf)" too. On, the
#   same band of the same value goes on TO(exf) 3, AW(exf) 4 and -(exf) 6; off, the in-fence codes alone carry it.
IFP_EXF = bool(_FKS.EXF_SUFFIX)
IFP_EXFN = [0, 0]               # (exf) cells carrying the suffix, and of them bare, counted across every state
IFP_MIN = {}                    # HIS 1121: each line's r at its last closed seam, built once per line and reused per state


def ifp_value(LN, t):
    """The r the in-fence power band reads on line ws{t}, at every 5 s bar. -> float array, len N."""
    if IFP_SEAM_S is None:
        return np.asarray(LN[IFP_KEY][t], float)
    if t not in IFP_MIN:
        IFP_MIN[t] = np.asarray(CP.series(LN[IFP_KEY][t], IFP_SEAM_S), float)
    return IFP_MIN[t]
#   HIS 1120: *"now all lines will be non-tagged (eg "-") if they are on the counter side of 50 (not the fence)"*.
#   The level towards/away's run masks at - his 50, not FENCE_RESET_TO's line - or None for the run as banked.
#   Every TO/AW read on the page follows the mask: the cells, the TO:x AW:x and TO(exf) sums, the flip marks and
#   fdm3-small-trade.
UNTAG = 50.0 if int(_FKS.UNTAG50) else None
#   HIS 1120 *"I need to see the "hold 1, tolerance 0.67" applied in 8791"*, his answer towards/away only: the lift-off
#   (tolerance, hold) every towards/away run here uses. None is v4's banked pair. Nothing else on the page reads
#   lift-off: m_no_rev is not called since his 1119 legMage took its slot.
TALIFT = _FKS.TA_LIFT
#   HIS 1121: *"clone 8793 to 8792 and change the config of r.  the new config is K len:6, RSI len:6, stoch range: 9"* /
#   *"contain the r config update to 8792 only.  you'll need a separate cache"*. 'db' reads ws{TF}r off the shared line
#   cache as always. Any other config switches THIS PROCESS's ln to its separate cache before anything reads r, so
#   towards/away, lift-off's e path, the bands, the (exf) test, the "-" rule and the up/dn pair all read the one config.
import fdm3_r_cache as RC  # noqa: E402 - docs/fdm3, on the path since the shim import
R_CFG = _FKS.ORACLE_R_CFG
R_USE = RC.use(R_CFG)           # None on 'db'; else (directory, manifest, built now)
#   HIS 1124 fdm3-htf-oracle, his answer "A separate cache": every line his 16 columns read that no cache held - the 5
#   minutes under each column over ws30 and ws240 itself in all four lines, r and e for ws45..ws120 - comes from that
#   page's own cache. towards/away runs scenario 1 on ws15..ws30 and those TFs, and scenario 2 (the state) on the 16
#   columns alone: his *"The 5 minutes under it"* reads ws15..ws19 under ws20..ws24 and ws40..ws44 under ws45.
HTF_USE, TA_TFS = None, None
if HTF:
    assert R_USE is not None and PIVOTS == 'two', 'fdm3-htf-oracle is built on the two trades and its own r config'
    import fdm3_htf_lines as HL  # noqa: E402 - docs/fdm3
    HTF_USE = HL.use(R_CFG)
    TA_TFS = sorted(set(range(15, 31)) | set(HL.NEW) | set(HL.OLD_HI))
    assert TA.s2_tfs(TA_TFS) == list(HTF_COLS), ('the TFs with a state are not his 16 columns', TA.s2_tfs(TA_TFS))
RUN_A_TFS = [t for t in A_TFS if TA_TFS is None or t in TA_TFS]   # HIS 1117 A ws1-ws6: no such line on fdm3-htf-oracle
#   HIS 1120, after seeing the whole cell go to "-": *"I only asked for an update on TO, but now the whole row has been
#   replaced with a "-"  I still need to see the ([inf,exf])[the 7 bands]  data"*, and his answer that TO and AW both
#   give way. So a masked cell keeps its fence tag and its band: "-(inf)-1", "-(exf)". Two new codes in bits 0-2 -
#   5 and 6 were free - so every reader that asks for TO(inf) 1, AW(inf) 2, TO(exf) 3 or AW(exf) 4 still gets the
#   states towards/away gave, and a "-" cell is none of them.
UN_INF, UN_EXF = 5, 6
#   the band is stored as band+1 in bits 3-5 of the TO/AW byte, so 0 means NO VALUE and prints a
#   bare TO(inf). The code itself stays in bits 0-2, which is why every reader masks with 7.
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


def leg_max_mage(side, prt):
    """HIS 1119 LEG MAGE: *"a new max Mage TF column that repeats the value on every row of the
    leg"*. -> [array of int8 per row], one entry so it slots where the M-no-rev columns were.

    THE VALUE IS THE INCOMING LEG'S, stamped at the outgoing leg's open and carried unchanged to
    its last row. That is what makes it both CONSTANT across the leg and CAUSAL: the max over THIS
    leg needs bars that have not happened yet on every row but the last.
    It is the quantity he asked about: *"the max oob is derived during the period where an incoming
    trade ends and an outgoing trade begins. how do we make sure that the max oob seen at the pivot
    is consumed by the outgoing trade?"*

    THE CLIMB is his: start at the LOWEST ws1..ws{MNR_TOPS[0]} whose CLOSED-PREV Mage is oob on the
    INCOMING leg's own target-side at some bar of that leg, and step up while the next timeframe -
    or the one after it, his *"jumps of 2 should be allowed"* - is oob too. 0 where none is.
    """
    import fdm3_knobs_shim as _FK
    oobf = float(K.OOB_LO)
    hi = int(MNR_TOPS[0])
    CPM = {t: np.asarray(CP.series(np.asarray(ln.line('ws%dMage' % t), float), t * 60), float)
           for t in range(1, hi + 1)}
    #   the legs: a run of bars that share one target-side. side is 0 outside every trade.
    edges = [0] + [int(b) for b in np.flatnonzero(side[1:] != side[:-1]) + 1] + [len(side)]
    val = np.zeros(len(side), np.int8)
    carry = 0
    for i in range(len(edges) - 1):
        o, z = edges[i], edges[i + 1]
        val[o:z] = carry                          # THIS leg shows the leg BEFORE it
        sd = int(side[o])
        if sd:
            hits = []
            for t in range(1, hi + 1):
                v = CPM[t][o:z]
                if not np.isfinite(v).any():
                    continue
                with np.errstate(invalid='ignore'):
                    out = (np.nanmax(v) >= 100 - oobf) if sd > 0 else (np.nanmin(v) <= oobf)
                if out:
                    hits.append(t)
            run = hits[0] if hits else 0
            for t in hits[1:]:
                if t - run <= int(_FK.OOB_JUMP):
                    run = t
                else:
                    break
            carry = run
        else:
            carry = 0
    assert val.min() >= 0 and val.max() <= hi, ('the leg Mage TF is outside ws1..ws%d' % hi)
    return [val[prt]]


def small_trade(code, side, prt, cap):
    """HIS 1119 `fdm3-small-trade`. -> bool per row, True = `lrg`.

    THE COUNT: distinct ws8..ws15 lines whose cell reads TO(exf) on ANY row from the trade's first
    row to this one - his *"highband lines printing TO(exf) during the trade"* read as it evolves,
    so a row never reads a later row. `lrg` once the count passes `cap` (his 2), and it holds to
    the trade's close because the count only grows; the next trade opens back at `sml`.
    THE ROW GRAIN IS THE PAGE'S: the cells he reads. A trade is a run of bars sharing one
    target-side, as leg_max_mage takes it - the trades alternate sides.
    """
    tid = np.concatenate(([0], np.cumsum(side[1:] != side[:-1])))[prt]   # trade id per row
    first = np.concatenate(([0], np.flatnonzero(np.diff(tid)) + 1))     # each trade's first row
    start = first[np.searchsorted(first, np.arange(len(prt)), side='right') - 1]
    n = np.zeros(len(prt), np.int32)
    for t in SMALL_HI:
        hit = ((code['ws%d' % t] & 7) == TO_EXF).astype(np.int64)
        cs = np.cumsum(hit)
        before = np.where(start > 0, cs[np.maximum(start - 1, 0)], 0)
        n += ((cs - before) > 0).astype(np.int32)                   # seen since the trade's first row
    live = side[prt] != 0
    lrg = live & (n > int(cap))
    #   THE HOLD: inside one trade `lrg` never goes back to `sml`
    assert not np.any(lrg[:-1] & ~lrg[1:] & (tid[:-1] == tid[1:])), 'a trade went lrg -> sml'
    return lrg


def small_trade_carried(own, runs, prt, cap, exm):
    """HIS 1121 B `fdm3-small-trade` on the +15 set. -> bool per row, True = `lrg`.

    small_trade's count - distinct ws8..ws15 lines that have read TO(exf) since the trade opened - over a CARRIED
    trade's own run (towards_away.run_carried's OWN): from its own open, so the rows before its first printed row,
    which the page gives to the trade before it, count too. TO(exf) is the TO state with the line ex-fence on the
    trade's target-side, as the page's cells build it; `exm` holds those ex-fence masks per (TF, side).
    """
    lrg = np.zeros(len(prt), bool)
    for k, (o, sh, c, s) in enumerate(runs):
        a, b, z = (int(np.searchsorted(prt, x, 'left')) for x in (o, sh, c))
        if z <= b:
            continue
        rows = prt[a:z]
        hit = np.stack([(own[k][t][rows - o] == TA.TO) & exm[(t, s)][rows] for t in SMALL_HI], 1)
        lrg[b:z] = np.logical_or.accumulate(hit, 0).sum(1)[b - a:] > int(cap)
    return lrg


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
    if ln.R_DIR is None:
        E = RS.load((RS.K0, RS.R0, RS.S0))       # fdm2's emerging r lines, ws1..ws30
    else:                                        # HIS 1121: this page's own r config, from its separate cache
        E = {t: np.asarray(ln.line('ws%dr' % t), float) for t in sorted(set(RC.TFS) | set(TA_TFS or ()))}

    def rpred(name):
        if name.startswith('gc'):                # ln.line multiplies the digits by 60, so the sub-minute lines
            r, m, M = (np.asarray(LL.sub_line(name + s), float) for s in ('r', 'm', 'Mage'))
        else:
            r = np.asarray(E[int(name[2:])], float)
            #   CONTROL: fdm2's r is the stored ws r line, exactly
            assert np.array_equal(r, np.asarray(ln.line(name + 'r'), float), equal_nan=True), name
            m, M = np.asarray(ln.line(name + 'm'), float), np.asarray(ln.line(name + 'Mage'), float)
        return predict_breach(r, m, M)

    #   HIS 1117: a ROW_S second slot, not a ws1 bar
    _rb = ROW_S // 5                             # 5 s bars per row
    first = np.flatnonzero((ts % (ROW_S * 1000)) == 0)
    first = first[first + _rb < ln.N]            # its print bar, _rb bars on, must be on the tape
    assert (np.diff(ts[first]) == ROW_S * 1000).all(), \
        'a %d s slot is missing - row i would not be t0 + %d s * i' % (ROW_S, ROW_S)
    prt = first + _rb                            # HIS ANSWER: the cell is the value where closed-prev shows it
    assert (ts[prt] - ts[first] == ROW_S * 1000).all(), 'a print bar is not one row on from its row'
    base = [rpred(name)[prt] for name in LINES] if RPRED_ON else []
    #   THE 1109 CONTROL STAYS ON THE MINUTE GRID. It counted the flagged cells at each ws1 bar's
    #   print bar, so reading it at a 30 s row would be a different measurement and its 257,295 would
    #   never match again. It keeps its own bars, which also keeps the r-pred producer checked even
    #   though RPRED_ON is False and no r-pred byte is stored.
    global FLAGGED
    _m1 = np.flatnonzero((ts % 60000) == 0)
    _m1 = _m1[_m1 + 12 < ln.N] + 12
    FLAGGED = int(sum((rpred(name)[_m1] != 0).sum() for name in CONTROL_LINES))
    sl = np.full(len(prt), SL_NONE, np.int16) if HTF else sl_pct(prt)   # HIS 1124: no SL% column on fdm3-htf-oracle
    if RPRED_ON:
        for _, tfs in SUMS:                      # the same read, summed: -7..+7 and -8..+8, fits int8
            base.append(np.sum([rpred('ws%d' % t)[prt].astype(int) for t in tfs], 0))
    #   HIS 1116 TOP ROW: *"the top row (which currently prints r-pred +1, -1, 0) is replaced by a mech that
    #   calculates if the current ws{tf}r row's value is higher or lower than the same ws{TF}r, 2 rows earlier and 3
    #   rows earlier ... position1 is the diff between current row and current row - 3, and position2 reports on
    #   current row - 2 --this update applies to ws1-15 only"*, and on a dead tie: *"'-'"*.
    #   The r-pred byte stays and still sets the cell's colour - *"keep the r-pred colors as is"*.
    #   THE EMERGING r AT THE ROW'S PRINT BAR, the line r-pred itself reads. Closed-prev was measured and rejected
    #   before this was built: a high-TF closed line does not move between rows 2 and 3 minutes apart, so it ties on
    #   52% of cells against 12.7% for emerging.
    #   HIS 1118 MAGE SIDE OF 50: *"add a mech that shows the Mage's side of 50, ws1-ws15. if
    #   ws{TF}Mage is over 50.00, print a green background. under 50.00, red background"*. It rides
    #   in the same per-line byte as the up/dn pair - bits 4-5, where the two positions use 0-3 - so
    #   the row does not grow: 0 neither way, 1 over 50.00, 2 under 50.00.
    #   EMERGING - HIS 1118 *"my bad: use emerging"*, correcting the closed-prev read I had put in.
    #   So it is the Mage at the row's print bar itself, the same bar and the same reading the up/dn
    #   pair beside it takes. Exactly 50.00 is neither, and so is a bar where the line has no value.
    UD = []
    for name in LINES:
        v = np.asarray(E[int(name[2:])], float)[prt]
        code = np.zeros(len(prt), np.int8)
        _mg = np.asarray(ln.line(name + 'Mage'), float)[prt]
        with np.errstate(invalid='ignore'):
            code |= np.where(_mg > 50.0, 1 << 4, np.where(_mg < 50.0, 2 << 4, 0)).astype(np.int8)
        #   HIS 1117: *"the up/dn pairs stay on 180 and 120"* - SECONDS, so the look-back is pinned
        #   to wall-clock time and a change to ROW_S cannot quietly redefine it
        for bit, secs in ((0, 180), (2, 120)):
            back = secs // ROW_S
            assert back * ROW_S == secs, ('%d s is not a whole number of %d s rows' % (secs, ROW_S))
            with np.errstate(invalid='ignore'):
                up, dn = v[back:] > v[:-back], v[back:] < v[:-back]
            one = np.zeros(len(prt), np.int8)
            one[back:] = np.where(up, 1, np.where(dn, 2, 0))   # 0 is a dead tie OR no row that far back
            code = (code | (one << bit)).astype(np.int8)
        UD.append(code)
    assert len(UD) == len(LINES) and all(0 <= int(c.min()) and int(c.max()) <= 42 for c in UD)
    #   the 23/77 run with A ws1-ws6 on and the 33/67 reset: the first page state
    if PIVOTS == 'pooled':
        #   HIS 1119, after the probe scored ws2Mage trades against this page's cells: the
        #   construction has ONE HOME, v4_sweep_pivots.pooled_trades, which the probe calls too.
        #   HIS 1120 SRP: so do its knobs - the page imports the set at sweep-pivots' own bank.
        pv = SP.pooled_pivots()
        piv = [(c, sd) for _cf, c, sd in pv]
        trades = SP.pooled_trades()
        print('pooled pivots: %d on the tape, %d pseudo trades, first opens %s'
              % (len(pv), len(trades), ln.U(trades[0][0])))
        LN = TA.load()
        ST, det = TA.run(LN, trades, FNC, A_TFS, FENCE_RESET_TO, untag=UNTAG, lift=TALIFT)
    elif PIVOTS == 'two':
        #   HIS 1122 two continuous trades. As found is the SHORT one, target-side LOW - a SHORT hunts the low oob -
        #   from the tape's first bar to its end; the flip set is the LONG one, target-side HIGH, on the same bars
        piv, trades = [], [(0, int(ln.N), -1)]
        print('HIS 1122 two trades: short %s to %s, target-side LOW; long on the same bars, target-side HIGH'
              % (ln.U(0), ln.U(ln.N - 1)))
        LN = TA.load(TA_TFS)                     # HIS 1124: None is the banked ws1..ws30
        ST, det = TA.run(LN, trades, FNC, RUN_A_TFS, FENCE_RESET_TO, untag=UNTAG, lift=TALIFT)
    else:
        LN, piv, trades, ST, det = TA.build(FNC, A_TFS, FENCE_RESET_TO, untag=UNTAG, lift=TALIFT)
    #   HIS 1119 caught this line calling the pooled ws1 pivots `ws2Mage`: it printed the same
    #   words on both paths, and that mislabel is how a ws2Mage read went unnoticed on this page.
    print('towards/away: %d %s pivots, %d pseudo trades, first opens %s'
          % (len(piv), 'pooled ws%d (Mage and b, emerging and closed-prev)' % int(SP.POOL_TF)
             if PIVOTS == 'pooled' else 'no' if PIVOTS == 'two' else 'ws2Mage', len(trades), ln.U(trades[0][0])))
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
            #   TWO SEPARATE RACES. The x line and the e line each run their own, with their own
            #   open/shut state: neither can shut the other. HIS 1118 asked whether they were
            #   linked - they never were, but the reader's old parameter name said `e` and read as
            #   though they might be.
            for bit, line, ro in ((1, np.asarray(ln.line('ws%dx' % t), float), X_REOPEN),
                                  (2, WSE.line(t), E_REOPEN)):
                wins = np.asarray([b for b, _ in JIG.race_wins(line, race, sd, reopen=ro)], np.int64)
                #   HIS 1117: the row a win lands in is ROW_S seconds wide, not a fixed 12 bars. At
                #   ROW_S 30 a //12 here binned every cross at half its row index, so the whole page
                #   lost them.
                row = (wins - first[0]) // _rb
                row = row[(wins >= first[0]) & (row < len(prt))]
                c[row] |= bit
            XC[name][sd] = c
    #   HIS 1113 *"flips the pivots directions"* and the +15 min button are SETS OF PIVOTS the page imports from
    #   sweep-pivots (v4_sweep_pivots.pivot_set) - HIS 1120 *"the +15 button is there to import a different set of
    #   pivots"*, the flip *"same treatment"*. The page only picks which set; each state is one set
    #   HIS 1115 the two A buttons: towards/away runs once per flip and A state, with A (jig.at_extreme `line_extreme`)
    #   on the lift-off reads of the ws1..ws6 r lines, the ws7..ws15 r lines, both or neither. The pivot shift and
    #   fence buttons are gone (HIS 1115), so no state moves a pivot and every state reads 23/77
    #   HIS 1117: A is locked, so the states are the pivot offset crossed with the flip - FOUR runs
    #   where there were eight. Every pivot PIV_SHIFT later moves each pseudo trade's open and close
    #   by the same amount on the same side, and towards/away runs again on those trades; the last
    #   trade still closes at the tape's end.
    #   HIS 1118 BUTTON: the ws{TF}x race's re-open is a third state dimension when XRE_BUTTON is
    #   on. It changes the towards/away run only - the cross row's own x bits are built above at
    #   X_REOPEN and are the same in every state.
    #   HIS 1121 *"B"*, after the +15 button changed rows the as-found view already showed (2026-09-14 22:33:00 to
    #   22:36:30): on the +15 set a trade KEEPS ITS OWN OPEN AND ITS HUNT and only its close moves. Its rows still
    #   print in pivot_set's window - so the target-side on every row is unchanged - but towards/away runs it from its
    #   own open (v4_sweep_pivots.carried_set, towards_away.run_carried), and the reads that count from a trade's open
    #   (fdm3-small-trade, legMage) count from that open too.
    STATES, SIDES, TRS, CARRY, OWN = [], {}, {}, {}, {}
    for off in OFFS:
        for fl in FLIPS:
            tr = SP.pivot_set(trades, off, bool(fl))
            side = np.zeros(ln.N, np.int8)
            for o, c, s in tr:
                side[o:c] = s
            SIDES[(off, fl)] = side
            TRS[(off, fl)] = tr
            if off:
                CARRY[(off, fl)] = SP.carried_set(trades, off, bool(fl))
            for xre in XRES:
                t1 = time.time()
                if not off and not fl and xre == 'winner':
                    st_, ng = ST, 1
                elif not off:
                    st_, ng = TA.run(LN, tr, FNC, RUN_A_TFS, FENCE_RESET_TO, xre, UNTAG, TALIFT)[0], 1
                else:
                    st_, ng, OWN[(off, fl, xre)] = TA.run_carried(LN, CARRY[(off, fl)], FNC, A_TFS, FENCE_RESET_TO,
                                                                  xre, UNTAG, TALIFT, keep=SMALL_HI)
                STATES.append((off, fl, xre, st_))
                print('state pivots +%d min, flip %d, x race re-opens on %s: %d pseudo trades, '
                      'first opens %s, %d towards/away run%s, %.1f s'
                      % (off, fl, xre, len(tr), ln.U(tr[0][0]), ng, '' if ng == 1 else 's', time.time() - t1))
    assert all(np.array_equal(SIDES[(off, 1)], -SIDES[(off, 0)]) for off in OFFS), \
        'a flipped pseudo trade is not the as-found one on the same bars with the other target-side'
    #   HIS 1121 B AS AN INVARIANT: from a carried trade's first printed bar to its OWN close, every towards/away state
    #   equals the as-found trade's - those are the rows both views share. A run that read past its bar breaks this.
    AFS = {(fl, xre): st_ for off, fl, xre, st_ in STATES if not off}
    for off, fl, xre, st_ in STATES:
        if not off:
            continue
        shared = np.zeros(ln.N, bool)
        for (o, sh, c, s), (o0, c0, s0) in zip(CARRY[(off, fl)], SP.pivot_set(trades, 0, bool(fl))):
            assert o == o0 and s == s0, 'a carried trade is not its as-found self'
            shared[sh:c0] = True
        for t in st_:
            assert np.array_equal(st_[t][shared], AFS[(fl, xre)][t][shared]), \
                ('HIS 1121 B: a carried trade differs from its as-found self on a shared bar', off, fl, xre, t)
        CARRY_SHARED[0] += int(shared.sum())
    #   HIS 1119 legMage is the INCOMING leg's, stamped at the trade's open. A carried trade keeps its open, so its
    #   value is the as-found trade's, printed over its carried window
    EXM = {(t, s): TA.exf_mask(LN, t, s, FNC) for t in SMALL_HI for s in (-1, +1)} if len(OFFS) > 1 else {}   # HIS 1121 B
    #                                            small-trade, read on the +15 set only
    MNR = {}
    for fl in FLIPS:
        if PIVOTS == 'two':                      # HIS 1122 *"Blank both"*: no legMage on the two trades
            _vb = np.zeros(ln.N, np.int8)
        else:
            _vb = leg_max_mage(SIDES[(0, fl)], np.arange(ln.N))[0]
        MNR[(0, fl)] = [_vb[prt]]
        for off in OFFS[1:]:
            _v = np.zeros(ln.N, np.int8)
            for o, sh, c, s in CARRY[(off, fl)]:
                _v[sh:c] = _vb[o]
            MNR[(off, fl)] = [_v[prt]]
    #   HIS 1124/1125 the VWAP columns, the same in every state
    VWC = []
    if VW_TFS:
        import fdm3_vwap as VW
        assert tuple(VW.TFS) == VW_TFS, (VW.TFS, VW_TFS)
        _c, _h, _l = (np.asarray(a, float) for a in BT.prices())
        _vr = VW.rows(prt, ts, _c, _h, _l, VW.volume(), lambda t: np.asarray(ln.line('ws%dMage' % t), float))
        del VW_NOTE[:]
        for t in VW_TFS:
            _an = VW.anchors(t, ts, _h, _l, np.asarray(ln.line('ws%dMage' % t), float))
            VW_NOTE.append('ws%d: %d low and %d high anchors, rows with both VWAPs %d of %d, first %s'
                           % (t, sum(a[1] < 0 for a in _an), sum(a[1] > 0 for a in _an),
                              int((_vr[t] != VW.BLANK).all(1).sum()), len(prt),
                              ln.U(prt[int(np.argmax((_vr[t] != VW.BLANK).all(1)))])))
            for q in range(6):
                v = _vr[t][:, q].astype(np.int16)
                VWC += [(v & 0xFF).astype(np.uint8).view(np.int8), (v >> 8).astype(np.int8)]
    mats = {}
    for off, fl, xre, ST in STATES:
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
            if UNTAG is not None:
                #   HIS 1120: the masked cells - in a trade, with an r value, no state - print "-" with their fence tag
                _r = np.asarray(LN['EMR'][t], float)[prt]
                _un = (st == TA.NONE) & (sp != 0) & np.isfinite(_r)
                assert np.all(np.where(sp[_un] > 0, _r[_un] < UNTAG, _r[_un] > UNTAG)), \
                    'a "-" cell is not on the counter side of %g' % UNTAG
                CODE[name] = np.where(_un, np.where(exf_at(t), UN_EXF, UN_INF), CODE[name])
            #   HIS 1119 `fdm3-infence-power`: the band of the line's own value. His first ask was
            #   *"for every TO(inf) line"*; he then added *"in the same manner as TO(inf), add the
            #   (+2,+1,0,-1,-2) suffixs to AW(inf). same ranges"*, and ruled the same seven bands
            #   there, so BOTH IN-FENCE CODES carry it. searchsorted on his edges with side='right'
            #   gives 0 under the first edge and len(edges) at or over the last, which is his -3
            #   and +3; +1 keeps 0 free for a cell with no value.
            #   ONE CELL IS NEVER BOTH TO(inf) AND AW(inf), so the two share bits 3-5 and the code
            #   in bits 0-2 says which tag the suffix belongs to. No bit was added. HIS 1121 +4 and -4
            #   take bit 6 too, on a page with nine bands.
            _v = np.round(ifp_value(LN, t)[prt], IFP_DP)
            _bd = (np.searchsorted(IFP_EDGES, _v, side='right') + 1).astype(np.int8)
            _bd = np.where(np.isfinite(_v), _bd, 0).astype(np.int8)
            #   TO(inf) is TA.TO and AW(inf) is TA.AW with the ex-fence bit unset - a +2 would
            #   have made them TO(exf) / AW(exf), which carry no in-fence distance
            _inf = (CODE[name] == TA.TO) | (CODE[name] == TA.AW) | (CODE[name] == UN_INF)   # HIS 1120 "-(inf)" too
            #   HIS 1121: TO(exf), AW(exf) and "-(exf)" too, when the page carries his (exf) suffix
            _exf = ((CODE[name] == TA.TO + 2) | (CODE[name] == TA.AW + 2) | (CODE[name] == UN_EXF)) & IFP_EXF
            CODE[name] = (CODE[name] | np.where(_inf | _exf, _bd << 3, 0)).astype(np.int8)
            assert not np.any(_exf & (_bd == 0) & np.isfinite(_v)), \
                'an (exf) cell has a %s value but no band' % IFP_READ
            IFP_EXFN[0] += int(np.sum(_exf))
            IFP_EXFN[1] += int(np.sum(_exf & (_bd == 0)))
            #   A TO(inf) cell CAN be bandless, and only in the tape's warm-up: a line has no
            #   closed-prev value until its first bar closes, which for ws15 is 2026-07-02
            #   16:29:55, after the first pseudo trade opens at 14:33:45. Those cells keep band 0
            #   and print a bare TO(inf). What must never happen is a cell WITH a value and no
            #   band - that would be a packing fault, so that is what this holds.
            assert not np.any(_inf & (_bd == 0) & np.isfinite(_v)), \
                'an in-fence cell has a %s value but no band' % IFP_READ
            IFP_BARE[0] += int(np.sum(_inf & (_bd == 0)))
            IFP_INF[0] += int(np.sum(_inf))
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
            if name in FLIP_TOX_LINES:
                cd = CODE[name] & 7          # HIS 1119: bits 3-5 are the in-fence power band, 3-6 since HIS 1121 +4
                xc[1:] |= 8 * ((cd[:-1] != TO_EXF) & (cd[1:] == TO_EXF)).astype(np.int8)
            #   HIS 1120 *"add a white highlight on TO(inf) if the previous row was TO(exf)"*, ws5 only: +16
            if name in FLIP_TOINF_LINES:
                cd = CODE[name] & 7
                xc[1:] |= 16 * ((cd[:-1] == TO_EXF) & (cd[1:] == TO_INF)).astype(np.int8)
            #   HIS 1121 the red suffix on a line leaving +4 or -4: +32, on ws2..ws15 since HIS 1122. pw is the band+1,
            #   0 = no suffix
            if IFP_RED4 and int(name[2:]) in RED4_TFS and not HTF:
                pw = (CODE[name].astype(int) >> 3) & 15
                pw = np.where((CODE[name] & 7) > 0, pw, 0)
                top = len(IFP_LABELS)
                red = (pw[:-1] > 0) & (pw[1:] > 0) & (((pw[:-1] == top) & (pw[1:] < top)) | ((pw[:-1] == 1) & (pw[1:] > 1)))
                xc[1:] |= 32 * red.astype(np.int8)
                IFP_REDN[0] += int(red.sum())
            #   HIS 1124 fdm3-htf-oracle: the b9 colours against the row's target-side. bv is the b9 value, -4..+4
            if IFP_RED4 and HTF:
                pw = (CODE[name].astype(int) >> 3) & 15
                pw = np.where((CODE[name] & 7) > 0, pw, 0)
                bv = pw - (len(IFP_LABELS) + 1) // 2
                both = (pw[:-1] > 0) & (pw[1:] > 0)
                up, dn = both & (bv[1:] > bv[:-1]), both & (bv[1:] < bv[:-1])
                lo, hi = sp[1:] < 0, sp[1:] > 0
                red = (lo & up & (bv[:-1] == -4)) | (hi & dn & (bv[:-1] == 4))
                org = (lo & up & np.isin(bv[:-1], (-3, -2, -1))) | (hi & dn & np.isin(bv[:-1], (1, 2, 3)))
                assert not (red & org).any()
                xc[1:] |= (32 * red + 64 * org).astype(np.int8)
                IFP_REDN[0] += int(red.sum())
                IFP_ORGN[0] += int(org.sum())
            cols.append(xc)
        #   HIS 1111 *"if any of the individual lines are printing TO(exf), print "TO(exf)" under the TO:x AW:x row"*:
        #   per sum column, how many of its lines read TO(exf) - the code a ws1..ws15 cell prints as TO(exf)
        for _, tfs in SUMS:
            cols.append(np.sum([((ST[t][prt] == TA.TO) & exf_at(t)).astype(int) for t in tfs], 0))
        cols.extend(VWC)                         # HIS 1124/1125 the VWAP columns, the same in every state
        cols.extend(UD)                          # HIS 1116 the up/dn pair per line, the same in every state
        cols.append((sl & 0xFF).astype(np.uint8).view(np.int8))     # HIS 1115 SL%, the same in every state
        cols.append((sl >> 8).astype(np.int8))
        #   HIS 1119 `fdm3-small-trade` rides in bit 6 of the legMage byte - `lrg` set, `sml` clear
        if PIVOTS == 'two':                      # HIS 1122 *"Blank both"*: the page prints no sml / lrg either
            lrg = np.zeros(len(prt), bool)
            _chk = lrg
        elif not off:
            lrg = small_trade(CODE, side, prt, SMALL_MAX)
            #   THE CHECK, a second construction: each trade off this state's own trade list, its rows
            #   cut by the print bar, the lines seen accumulated row by row inside it
            _chk = np.zeros(len(prt), bool)
            for _o, _c, _s in TRS[(off, fl)]:
                _a, _z = np.searchsorted(prt, _o, 'left'), np.searchsorted(prt, _c, 'left')
                if _z > _a:
                    _h = np.stack([(CODE['ws%d' % t][_a:_z] & 7) == TO_EXF for t in SMALL_HI], 1)
                    _chk[_a:_z] = np.logical_or.accumulate(_h, 0).sum(1) > SMALL_MAX
            LRG_AF[(fl, xre)] = lrg
        else:
            #   HIS 1121 B: a carried trade counts from its OWN open, over its own run - the rows before it prints
            #   included, which the trade before it carries on the page
            lrg = small_trade_carried(OWN[(off, fl, xre)], CARRY[(off, fl)], prt, SMALL_MAX, EXM)
            #   THE CHECK, a second construction: a set of lines per trade, row by row, from its open
            _chk = np.zeros(len(prt), bool)
            for _k, (_o, _sh, _c, _s) in enumerate(CARRY[(off, fl)]):
                _ex = {t: EXM[(t, _s)] for t in SMALL_HI}
                seen = set()
                for _r in range(np.searchsorted(prt, _o, 'left'), np.searchsorted(prt, _c, 'left')):
                    _b = int(prt[_r])
                    seen |= {t for t in SMALL_HI if OWN[(off, fl, xre)][_k][t][_b - _o] == TA.TO and _ex[t][_b]}
                    if _b >= _sh:
                        _chk[_r] = len(seen) > SMALL_MAX
            #   and on the rows both views share it is the as-found trade's own `sml` / `lrg`
            _sh_rows = np.zeros(len(prt), bool)
            for (_o, _sh, _c, _s), (_o0, _c0, _s0) in zip(CARRY[(off, fl)], SP.pivot_set(trades, 0, bool(fl))):
                _sh_rows[np.searchsorted(prt, _sh, 'left'):np.searchsorted(prt, _c0, 'left')] = True
            assert np.array_equal(lrg[_sh_rows], LRG_AF[(fl, xre)][_sh_rows]), \
                ('HIS 1121 B: fdm3-small-trade differs from the as-found trade on a shared row', off, fl, xre)
        assert np.array_equal(_chk, lrg), ('fdm3-small-trade disagrees with its own check',
                                           off, fl, int((_chk != lrg).sum()))
        SMALL_ROWS[0] += int((side[prt] != 0).sum())
        SMALL_ROWS[1] += int(lrg.sum())
        for mn_k in mnr:                         # HIS 1119: the incoming leg's max Mage TF, 0 none
            assert int(mn_k.max()) < SMALL_LRG, 'legMage reaches the small-trade bit'
            cols.append((mn_k | np.where(lrg, SMALL_LRG, 0)).astype(np.int8))
        cols.append(side[prt])                   # HIS 1109: the time cell's 20% colour, red LOW, green HIGH
        mats[(off, fl, xre)] = np.ascontiguousarray(np.stack(cols, 1).astype(np.int8))
    #   HIS 1121 B, THE PAGE'S OWN INVARIANT: on every row a carried +15 trade shares with its as-found self - its first
    #   printed row to its own close - every byte is the as-found one. The one exception is that trade's FIRST printed
    #   row, where the cross code's flip marks (+4 +8 +16 +32) compare with the row above, and on +15 the row above
    #   prints the trade before it.
    _xo = len(base) + len(LINES) + 2 * len(SUMS)
    for (off, fl, xre), m in mats.items():
        if not off:
            continue
        rows, firsts = np.zeros(len(prt), bool), np.zeros(len(prt), bool)
        for (o, sh, c, s), (o0, c0, s0) in zip(CARRY[(off, fl)], SP.pivot_set(trades, 0, bool(fl))):
            a, z = int(np.searchsorted(prt, sh, 'left')), int(np.searchsorted(prt, c0, 'left'))
            if z > a:
                rows[a:z] = True
                firsts[a] = True
        X = m[rows].astype(np.int16) ^ mats[(0, fl, xre)][rows].astype(np.int16)
        X[np.ix_(firsts[rows], np.arange(_xo, _xo + len(LINES)))] &= ~60
        assert not X.any(), ('HIS 1121 B: a shared row differs from the as-found page', off, fl, xre,
                             int(X.any(1).sum()))
        CARRY_ROWS[0] += int(rows.sum())
    #   the towards/away runs are done: their cached setup is not needed to serve, and three pages share 23 GB
    TA._SETUP.clear()
    return ts[first], mats


T0 = time.time()
#   HIS 1117 LAYOUT, with the r-pred block gone. One place names the offsets and every check below
#   reads them, so a future insert moves one table and not a dozen expressions.
O_TA = 0                                        # the TO/AW code per line
O_TACNT = O_TA + len(LINES)                     # per sum, its TO count then its AW count
O_XC = O_TACNT + 2 * len(SUMS)                  # the cross code per line
O_TOEXF = O_XC + len(LINES)                     # per sum, how many of its lines read TO(exf)
O_VW = O_TOEXF + len(SUMS)                      # HIS 1124/1125 the VWAP block, 12 bytes per TF, none on fdm3-oracle
O_UD = O_VW + VW_BYTES                          # HIS 1116 the up/dn pair per line
O_SL = O_UD + len(LINES)                        # HIS 1115 SL% x 100, an int16
O_MNR = O_SL + 2                                # HIS 1119: one byte, the incoming leg's max Mage TF
assert O_MNR + len(MNR_TOPS) + 1 == STRIDE, (O_MNR, STRIDE)

#   HIS 1124 *"the reason for the memory control"*, his answer "Free start-up only": the page held 7.7 GB (6.4 GB in RAM,
#   1.3 GB in swap, 2026-11-24 19:37:19) to serve 29.9 MB of rows. build() runs in a FORKED CHILD, which hands back only
#   the row matrices and the start-up counts and exits, so every array the start-up made goes back to the operating
#   system with it. The child is a copy of this process, so it reads exactly what build() read here - every byte of
#   every row is the same. MINE, structural: the fork, and a pipe rather than a file.
_COUNTS = ('VW_NOTE', 'IFP_REDN', 'IFP_ORGN', 'IFP_BARE', 'IFP_INF', 'IFP_EXFN', 'SMALL_ROWS', 'CARRY_SHARED', 'CARRY_ROWS')


def build_in_child():
    """build() in a forked child. -> build()'s (row open ms, matrices), with FLAGGED and the _COUNTS lists set here."""
    import pickle
    import traceback
    global FLAGGED
    sys.stdout.flush(); sys.stderr.flush()
    rd, wr = os.pipe()
    pid = os.fork()
    if pid == 0:                                 # the child: build, send, exit without running anything else
        os.close(rd)
        code = 1
        try:
            res = build()
            #   HIS 1124 row cache: the child's inputs too - the modules, files and database reads build() reached
            out = (res, FLAGGED, {k: list(globals()[k]) for k in _COUNTS},
                   (_code_files(), sorted(_LOADED), sorted(_DBREADS.items())))
            with os.fdopen(wr, 'wb') as f:
                pickle.dump(out, f, protocol=pickle.HIGHEST_PROTOCOL)
            code = 0
        except BaseException:
            traceback.print_exc()
        finally:
            sys.stdout.flush(); sys.stderr.flush()
            os._exit(code)
    os.close(wr)
    with os.fdopen(rd, 'rb') as f:
        data = f.read()                          # read it all before waiting, so a full pipe cannot stall the child
    _, st = os.waitpid(pid, 0)
    if st != 0 or not data:
        raise SystemExit('the start-up child failed (wait status %d) - not serving' % st)
    res, FLAGGED, cnt, inputs = pickle.loads(data)
    for k in _COUNTS:
        globals()[k][:] = cnt[k]
    return res, inputs


#   HIS 1124 THE ROW CACHE: *"the rows are a small file - it should be kept on disk as well as in memory to avoid
#   downtime on small cosmetic changes or restarts"* / *"update the code and rebuild the optimised 8793 first, then
#   8795"*. One directory per page SETTINGS - every W_, FDM3_ and LG_ setting, the Python and numpy versions - under
#   ROWS_ROOT, holding the rows of every state, the start-up counts and a manifest of every input the start-up read.
#   A start-up READS it only when all of these are as they were: the source of every module of this repo the start-up
#   ran (compared as code: comments, docstrings and the page's HTML do not count, so a cosmetic edit keeps it), every
#   file numpy loaded (size and modified time), and every database read (re-run, its answer hashed). Anything else -
#   or FDM3_ROWS_REBUILD=1 - is a full start-up, which writes a new cache. FDM3_ROWS_CHECK=1 says which it would be
#   and stops. MINE, structural: the layout, the comparisons and the two settings' names. A cache is never written
#   when an input changed while the start-up ran.
ROWS_ROOT = '/home/joe/thecodes/optimus9/orchestration/.rpl_cache/fdm3_rows'   # beside the line caches, git-ignored
ROWS_VERSION = 1
REPO = '/home/joe/thecodes/'
ROWS_NOTE = ''


def _settings():
    """-> the page's settings, which name its cache directory."""
    env = {k: v for k, v in os.environ.items()
           if k.startswith(('W_', 'FDM3_', 'LG_')) and k not in ('FDM3_ROWS_CHECK', 'FDM3_ROWS_REBUILD')}
    return {'env': env, 'python': sys.version.split()[0], 'numpy': np.__version__}


def _rows_dir():
    return os.path.join(ROWS_ROOT, hashlib.sha1(json.dumps(_settings(), sort_keys=True).encode()).hexdigest()[:16])


def _code_hash(path):
    """A source file's code, without comments, docstrings or (in this file) the page's HTML. -> sha1 hex."""
    import ast
    with open(path) as f:
        tree = ast.parse(f.read())
    if os.path.realpath(path) == _SELF:
        tree.body = [n for n in tree.body if not (isinstance(n, ast.Assign) and len(n.targets) == 1
                                                  and getattr(n.targets[0], 'id', None) == 'PAGE')]
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.body \
                and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant) \
                and isinstance(n.body[0].value.value, str):
            n.body = n.body[1:] or [ast.Pass()]
    return hashlib.sha1(ast.dump(tree).encode()).hexdigest()


def _code_files():
    """-> every source file of this repo loaded in this process, real paths, sorted."""
    out = {_SELF}
    for m in list(sys.modules.values()):
        f = getattr(m, '__file__', None)
        if f and f.endswith('.py') and os.path.realpath(f).startswith(REPO):
            out.add(os.path.realpath(f))
    return sorted(out)


def _md5(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def rows_check():
    """Can this start-up read its cache. -> (manifest, None) or (None, the first reason it cannot)."""
    import ast
    d = _rows_dir()
    mp = os.path.join(d, 'manifest.json')
    if not os.path.exists(mp):
        return None, 'no row cache for these settings yet (%s)' % d
    with open(mp) as f:
        man = json.load(f)
    if man.get('version') != ROWS_VERSION:
        return None, 'the cache was written by row-cache version %s' % man.get('version')
    new = [f for f in _code_files() if f not in man['code']]
    if new:
        return None, '%d source file(s) loaded now that the cached start-up did not load, first %s' % (len(new), new[0])
    for f, h in man['code'].items():
        if not os.path.exists(f) or _code_hash(f) != h:
            return None, 'source changed: %s' % f
    for f, (size, mt) in man['data'].items():
        st = os.stat(f) if os.path.exists(f) else None
        if st is None or (st.st_size, st.st_mtime_ns) != (size, mt):
            return None, 'data file changed: %s' % f
    if man['db']:
        db = _DBMOD.DatabaseManager(**_db_config())
        db.connect()
        try:
            for sql, prm, h in man['db']:
                try:
                    got = _db_exec(db, sql, ast.literal_eval(prm), fetch=True)
                except Exception as e:                   # a read that cannot be re-run cannot be trusted
                    return None, 'a database read could not be re-run (%s): %s' % (e, sql[:80])
                if hashlib.sha1(repr(got).encode()).hexdigest() != h:
                    return None, 'a database read came back different: %s' % ' '.join(sql.split())[:100]
        finally:
            db.disconnect()
    for k, m5 in man['files'].items():
        if not os.path.exists(os.path.join(d, k)) or _md5(os.path.join(d, k)) != m5:
            return None, 'the cached rows file %s is damaged or missing' % k
    return man, None


def _db_config():
    _e = sys.stderr; sys.stderr = io.StringIO()
    try:
        from optimus9.config import get_db_config
    finally:
        sys.stderr = _e
    return get_db_config()


def rows_write(res, inputs, code0, built_s):
    """Write the cache for this page's settings. -> None, or why it was not written."""
    open_, mats = res
    files_c, loaded_c, db_c = inputs
    code = {}
    for f in sorted(set(files_c) | set(code0)):
        h = _code_hash(f)
        if (f in code0 and code0[f] != h) or (f not in code0 and os.stat(f).st_mtime_ns > T_START_NS):
            return 'source changed while the start-up ran: %s' % f
        code[f] = h
    data = {}
    for f in sorted(set(loaded_c) | _LOADED):
        if f.startswith(ROWS_ROOT):
            continue
        st = os.stat(f)
        if st.st_mtime_ns > T_START_NS:
            return 'data file changed while the start-up ran: %s' % f
        data[f] = [st.st_size, st.st_mtime_ns]
    d = _rows_dir()
    tmp = '%s.part.%d' % (d, os.getpid())
    os.makedirs(tmp)
    files, states = {}, []
    np.save(os.path.join(tmp, 'open.npy'), np.asarray(open_))
    files['open.npy'] = _md5(os.path.join(tmp, 'open.npy'))
    for (off, fl, xre), m in mats.items():
        k = 'rows_%d_%d_%s.npy' % (off, fl, xre)
        np.save(os.path.join(tmp, k), m)
        files[k] = _md5(os.path.join(tmp, k))
        states.append([off, fl, xre, k])
    man = {'version': ROWS_VERSION, 'settings': _settings(), 'built_at': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()), 'built_s': round(built_s, 1),
           'states': states, 'files': files, 'flagged': FLAGGED, 'counts': {k: list(globals()[k]) for k in _COUNTS},
           'code': code, 'data': data, 'db': [[sql, prm, h] for (sql, prm), h in sorted(dict(db_c).items())]}
    with open(os.path.join(tmp, 'manifest.json'), 'w') as f:
        json.dump(man, f, indent=1)
    if os.path.isdir(d):                         # the settings' old cache is stale by now: swap it out
        old = '%s.old.%d' % (d, os.getpid())
        os.rename(d, old)
        os.rename(tmp, d)
        shutil.rmtree(old)
    else:
        os.rename(tmp, d)
    return None


def rows_from_cache_or_build():
    """-> (row open ms, matrices), from the disk cache when every input is unchanged, else from a full start-up."""
    global FLAGGED, ROWS_NOTE
    man, why = (None, 'FDM3_ROWS_REBUILD=1') if ROWS_REBUILD else rows_check()
    if ROWS_CHECK:
        print('row cache %s: %s' % (_rows_dir(), 'WOULD BE READ, built %s' % man['built_at'] if man else 'would NOT be read - ' + why))
        sys.stdout.flush()
        raise SystemExit(0)
    if man is not None:
        d = _rows_dir()
        open_ = _np_load(os.path.join(d, 'open.npy'))
        mats = {(int(off), int(fl), xre): _np_load(os.path.join(d, k)) for off, fl, xre, k in man['states']}
        FLAGGED = man['flagged']
        for k in _COUNTS:
            globals()[k][:] = man['counts'][k]
        ROWS_NOTE = ('row cache READ from %s in %.1f s - its full start-up was %.1f s, %s; %d source files, %d data files '
                     'and %d database reads checked unchanged' % (d, time.time() - T0, man['built_s'], man['built_at'],
                                                                len(man['code']), len(man['data']), len(man['db'])))
        return open_, mats
    print('row cache: %s - a full start-up' % why)
    sys.stdout.flush()
    code0 = {f: _code_hash(f) for f in _code_files()}
    res, inputs = build_in_child()
    built_s = time.time() - T0
    nw = rows_write(res, inputs, code0, built_s)
    ROWS_NOTE = ('row cache NOT written: %s' % nw) if nw else ('row cache WRITTEN to %s after a %.1f s full start-up'
                                                              % (_rows_dir(), built_s))
    return res


OPEN, MATS = rows_from_cache_or_build()
RP = MATS[(0, 0, 'winner')]                     # the pivots as found, A locked, 23/77, his 1109 4B x race
assert all(m.shape == RP.shape for m in MATS.values()) and RP.shape[1] == STRIDE
assert all(np.array_equal(m[:, O_UD:O_UD + len(LINES)], RP[:, O_UD:O_UD + len(LINES)]) for m in MATS.values()), \
    'the r-pred bytes differ between the page states'
DAYS = []
for i, ms in enumerate(OPEN):
    d = time.strftime('%Y-%m-%d', time.gmtime(int(ms) // 1000))
    if not DAYS or DAYS[-1][0] != d:
        DAYS.append([d, i])
TAC = RP[:, O_TA:O_TA + len(LINES)]
U = lambda ms: time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(ms) // 1000))
META = json.dumps({
    'lines': LINES, 'mnr': MNR_LABELS[0], 'sums': [s for s, _ in SUMS], 'stride': STRIDE, 'rows': int(len(OPEN)), 't0': int(OPEN[0]), 'step': ROW_S * 1000,
    'days': DAYS, 'fence': FNC, 'abands': [b for b, _ in A_BANDS], 'flips': list(FLIPS),
    'mnrs': list(MNR_LABELS), 'mnrtops': list(MNR_TOPS),
    'shift': PIV_SHIFT, 'carry': 1, 'alock': list(A_LOCK), 'reset': FENCE_RESET_TO, 'rpred': RPRED_ON,
    'ifp': list(IFP_LABELS), 'ifpedges': list(IFP_EDGES), 'ifpdp': IFP_DP, 'ifpread': IFP_READ, 'ifpexf': int(IFP_EXF), 'untag': UNTAG, 'rcfg': R_CFG,
    'red4': list(RED4_TFS),                     # HIS 1122 the lines the red suffix reads
    #   HIS 1124 fdm3-htf-oracle: which page this is. htf 1 = no SL%, no legMage, no sums, no A buttons; the cross code's
    #   +64 is the orange b9 colour and +8 / +16 mark every column
    'page': PAGE_MODE, 'htf': int(HTF), 'title': 'fdm3-htf-oracle' if HTF else 'fdm3-oracle',
    'talift': list(TALIFT) if TALIFT else 'v4',   # HIS 1120 towards/away's lift-off (tolerance, hold), or v4's pair
    'tacodes': ['', 'TO(inf)', 'AW(inf)', 'TO(exf)', 'AW(exf)', '-(inf)', '-(exf)'],
    #   HIS 1119: TWO KEYS FOR THE PRODUCER, on purpose.
    #     `pivots`   the machine value, 'ws2Mage' or 'pooled'. The fdm3 probe switches on it, so it
    #                must stay exactly what FDM3_PIVOTS accepts and must never be prettied up.
    #     `pivlabel` what a PERSON reads - the button tooltips print it. Naming the timeframe here
    #                is what stops a tooltip saying ws2Mage on a page whose pivots are ws1's.
    'pivlabel': ('pooled ws%d' % int(SP.POOL_TF)) if PIVOTS == 'pooled' else 'two trades' if PIVOTS == 'two'
                else 'ws2Mage',
    'offs': list(OFFS),                         # HIS 1122: the two-trade page has no +15 set, so no +15 button
    'legblank': int(PIVOTS == 'two'),           # HIS 1122 *"Blank both"*: no legMage and no sml / lrg
    'mage50': MAGE50_PCT, 'smallmax': SMALL_MAX, 'smallbit': SMALL_LRG,
    #   WHERE EACH BLOCK STARTS, so a reader is told rather than deriving it. A derived offset is
    #   how oracle_rows came to hold a stale O_TA and read every TO/AW cell out of the wrong byte.
    'ta': O_TA, 'xc': O_XC, 'toexf': O_TOEXF, 'sl': O_SL, 'omnr': O_MNR,
    'xreopen': X_REOPEN, 'ereopen': E_REOPEN, 'xres': list(XRES), 'pivots': PIVOTS,
    #   HIS 1116: where the up/dn block starts, so a reader is told rather than re-deriving the layout
    'updn': O_UD,
    'vw': O_VW, 'vwtfs': list(VW_TFS)})        # HIS 1124/1125 where the VWAP block starts, and its TFs


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
            m = (MATS.get((int(q.get('off', 0)), int(q.get('flip', 0)), q.get('xre', 'winner')))
                 if _a == A_LOCK else None)
            if m is None:
                self.send_error(400, 'off must be one of %s, flip one of %s, xre one of %s, and '
                                     'alo / ahi the locked %s' % (OFFS, FLIPS, XRES, A_LOCK))
                return
            a = max(0, int(q['start'])); b = min(len(m), a + max(0, int(q['count'])))
            return self._send(m[a:b].tobytes(), 'application/octet-stream')    # STRIDE bytes per row
        return self._send(page().encode(), 'text/html; charset=utf-8')


def page():
    """-> the HTML, RE-READ FROM THIS FILE on every page load.

    A rebuild of the matrices costs ~11 minutes, and a cosmetic change touches only the HTML below.
    Re-reading it means a style or layout change is live on the next browser reload with no restart.
    It parses this file and takes the PAGE assignment's own string, so a half-saved file cannot be
    served: anything that does not parse falls back to the PAGE this process started with.
    MY CALL, structural - it changes no data and no byte of a row.
    """
    try:
        import ast as _ast
        with open(__file__) as f:
            for node in _ast.parse(f.read()).body:
                if (isinstance(node, _ast.Assign) and len(node.targets) == 1
                        and getattr(node.targets[0], 'id', None) == 'PAGE'
                        and isinstance(node.value, _ast.Constant)
                        and isinstance(node.value.value, str)):
                    return node.value.value
    except Exception as e:                       # a syntax error mid-save, or the file moved
        sys.stderr.write('page() fell back to the built-in HTML: %s\n' % e)
    return PAGE


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
/*   HIS 1118: *"move the buttons and the calenders to the bottom of the screen"*, so the data box is
     first in the column and this strip sits under it   */
.foot{display:flex;gap:18px;flex-wrap:wrap;align-items:flex-start;margin-top:10px}
.cal{display:flex;gap:18px;flex-wrap:wrap}
/*   HIS 1118: *"move these 2 lines under the buttons, using a table that is as wide as the buttons
     space"*. The buttons get their own box so the table can sit beneath them, and the table's width
     is set in JS from the button row itself - CSS cannot size a box from one child and its sibling
     from the box at the same time   */
.btns{display:flex;flex-direction:column;gap:6px}
/*   align-self keeps this row at the buttons' own width. Without it the column stretches it to
     the box, which on the first layout is as wide as the untamed text in the table below -
     and that width is what the table would then be pinned to   */
.btnrow{display:flex;gap:6px;flex-wrap:wrap;align-self:flex-start}
.info{table-layout:fixed;border-collapse:collapse;font-size:11px;color:var(--mut)}
.info td{padding:3px 5px;border:1px solid var(--line);font-variant-numeric:tabular-nums;
  word-break:break-word}
.mon{min-width:200px}
/*   HIS 1118: *"reduce all of the calender's fonts by 2px"* - the month name 12 -> 10, the weekday
     letters 10 -> 8, the day numbers 11 -> 9. The cell geometry is untouched: he asked for fonts   */
.mon b{display:block;font-size:10px;margin-bottom:3px}
.grid{display:grid;grid-template-columns:repeat(7,26px);gap:2px}
.grid span{font-size:8px;color:var(--mut);text-align:center}
.grid button{height:22px;border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:4px;
  font:9px system-ui,sans-serif;cursor:pointer;padding:0}
.grid button:hover{border-color:var(--sel)}
.grid button:disabled{color:var(--dis);border-color:transparent;cursor:default}
.grid button.on{background:var(--sel);border-color:var(--sel);color:var(--bg);font-weight:600}
.tog{align-self:flex-start;height:26px;padding:0 12px;border:1px solid var(--line);background:var(--bg);color:var(--fg);
  border-radius:4px;font:12px system-ui,sans-serif;cursor:pointer;white-space:nowrap}
.tog:hover{border-color:var(--sel)}
.tog.on{background:var(--sel);border-color:var(--sel);color:var(--bg);font-weight:600}
.tog:disabled{cursor:default;opacity:.7}   /* HIS 1117: a banked A button shows its position, no click */
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
/*   HIS 1124 *"Taller rows"*: fdm3-htf-oracle's VWAP cells print 6 lines, so its rows grow to 98 px and every 3-line
     cell sits centred in them   */
.tall .row{height:98px}
.tall .row div{height:97px}
.tall .row .t{line-height:97px}
.row div b.v{font-weight:600;font-size:10px;white-space:pre;color:var(--fg)}
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
.row div b span.r4{color:var(--red)}
.row div b span.o4{color:var(--org)}   /* HIS 1124 fdm3-htf-oracle: the orange b9 colour, the page's own orange */
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
<div class="box" id="box"><div class="inner"><div class="hd" id="hd"></div><div class="body" id="body"></div></div></div>
<div class="foot">
<div class="cal" id="cal"></div>
<div class="btns"><div class="btnrow" id="btnrow"></div>
<table class="info" id="info"><tr><td><span id="top">top row: -</span> <span id="held">cache: -</span>
<span id="err"></span></td></tr>
<tr><td id="what">fdm3-oracle - SL%, r-pred ws1 to ws15, M-no-rev, plus the ws16-22 and ws23-30 sums, emerging, on closed-prev ws1 bars, with towards/away</td></tr></table>
</div></div>
</div><script>
let RH = 50;            // row height, px - three lines: the number, TO / AW, then the crosses (HIS 1110); 98 on
                        // fdm3-htf-oracle with its 6-line VWAP cells, HIS 1124 *"Taller rows"*
const VWW = 104;        // px, a VWAP column - its widest line, "lo udist: -10.00" at 10px; MINE
const VWL = ['lo udist', 'lo vdist', 'lo ldist', 'hi udist', 'hi vdist', 'hi ldist'];   // HIS 1124 "Low VWAP on top"
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
let fitDeep = () => {};   // HIS 1124 on 8795, set in init - a no-op on every other page
const NB = '\u00a0';   // HIS 1110: the place holder line - a blank line keeps a cell's 3 lines aligned
let sel = -1;           // HIS 1110: the clicked row, highlighted; a click on another row moves it, on the same row clears it
let FLIP = 0;           // HIS 1113: 0 the pivots' sides as found, 1 every side flipped with the button on
let OFF = 0;            // HIS 1117: the pivot offset button - 0 the pivots as found, meta.shift minutes later
//   HIS 1118: the towards/away ws{TF}x race's re-open. 'winner' is his 1109 4B - the race re-opens only when
//   x crosses back over the line that won. 'any' is his B - it re-opens on crossing back over any of the three.
//   The button exists only where the server built both, which is the page started with FDM3_XRE_BUTTON=1.
let XRE = 'winner';
let ALO = 0, AHI = 0;   // HIS 1117: A is LOCKED, these take meta.alock and no button changes them

const fmt = ms => new Date(ms).toISOString().slice(0, 19).replace('T', ' ');

function fetchBlock(b) {
  const off = OFF, flip = FLIP, xre = XRE, key = off + ':' + flip + ':' + xre + ':' + b;   // each state keeps its own blocks
  if (b < 0 || b * BLOCK >= meta.rows || cache.has(key) || pending.has(key)) return;
  pending.add(key);
  fetch('rows?start=' + (b * BLOCK) + '&count=' + BLOCK + '&off=' + off + '&flip=' + flip + '&xre=' + xre +
        '&alo=' + ALO + '&ahi=' + AHI)
    .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.arrayBuffer(); })
    .then(buf => { pending.delete(key); cache.set(key, new Int8Array(buf)); evict(); schedule(); })
    .catch(e => { pending.delete(key); document.getElementById('err').textContent = 'fetch failed: ' + e.message; });
}
function getBlock(b) {
  const key = OFF + ':' + FLIP + ':' + XRE + ':' + b, a = cache.get(key);
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
      if (c === NL + 1 && !meta.htf) {   // HIS 1119 the leg's max Mage TF, between ws15 and the sums; none on htf
        //   one skinny cell, three lines like every data cell so the row stays aligned
        for (const _ of meta.mnrs) {
          const m = document.createElement('div'); m.n = document.createElement('span');
          m.ta = document.createElement('b'); m.xc = document.createElement('b'); m.append(m.n, m.ta, m.xc);
          el.appendChild(m); mcs.push(m);
        }
      }
      const d = document.createElement('div'); d.className = c ? '' : 't'; el.appendChild(d);
      if (!c && !meta.htf) {            // HIS 1115 SL%, right of the time; 3 lines like every data cell; none on htf
        slc = document.createElement('div'); slc.n = document.createElement('span');
        slc.ta = document.createElement('b'); slc.xc = document.createElement('b'); slc.append(slc.n, slc.ta, slc.xc);
        el.appendChild(slc);
      }
      if (c) { d.n = document.createElement('span'); d.ta = document.createElement('b'); d.append(d.n, d.ta); if (c > NL) d.ta.className = 's'; else d.n.className = 'ud'; }
      if (c) { d.xc = document.createElement('b'); d.xc.className = 'x'; d.append(d.xc); }   // HIS 1110 cross row, every cell
      cells.push(d);
    }
    const vws = [];                     // HIS 1124/1125 the VWAP cells, far right: six lines each
    for (const _ of (meta.vwtfs || [])) {
      const v = document.createElement('div'); v.ls = [];
      for (let q = 0; q < 6; q++) { const b = document.createElement('b'); b.className = 'v'; v.appendChild(b); v.ls.push(b); }
      el.appendChild(v); vws.push(v);
    }
    body.appendChild(el); pool.push({el, cells, mcs, slc, vws, i: -1, ok: false});
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
      //   HIS 1119: one byte per column now, not three. The value is the INCOMING leg's max Mage
      //   TF, stamped at this leg's open and the same on every row of it
      const b0 = o + NS - 1 - (p.mcs.length - k);
      const mb = blk ? blk[b0] : 0, mv = mb & 15;   // HIS 1119: bits 0-3 legMage, bit 6 small-trade
      const m = p.mcs[k];
      m.n.textContent = !blk ? '·' : mv > 0 ? 'ws' + mv : NB;
      //   HIS 1119 `fdm3-small-trade`: *"print it underneath the existing 'legmage' data"*, `sml` until
      //   more than meta.smallmax highband lines have printed TO(exf) in the trade, then `lrg`
      m.ta.textContent = blk && k === 0 && sd !== 0 && !meta.legblank ? (mb & meta.smallbit ? 'lrg' : 'sml') : NB;
      m.xc.textContent = NB;
      m.className = (blk ? 'mn' : 'w') + (k === 0 ? ' sx' : '');
    }
    //   HIS 1115 SL%: the mean abs price % of the gcws15b legs (final oob -> ib to final oob -> ib) ending in the last
    //   6 h, x 100 in two bytes; blank where there is none
    const sl = blk ? ((blk[o + NS - 5] << 8) | (blk[o + NS - 6] & 255)) : 0;
    if (p.slc) {                        // HIS 1124: fdm3-htf-oracle has no SL% column
      p.slc.n.textContent = !blk ? '·' : sl < 0 ? NB : (sl / 100).toFixed(2);
      p.slc.ta.textContent = NB; p.slc.xc.textContent = NB;
      p.slc.className = blk ? 'sl' : 'w';
    }
    for (let c = 0; c < NC; c++) {
      const d = p.cells[c + 1], sx = c === NL ? ' sx' : '';
      d.style.background = '';   // the pool reuses cells, so clear the last row's paint
      if (!blk) { d.n.textContent = '·'; d.ta.textContent = NB; d.xc.textContent = NB; d.className = 'w' + sx; continue; }
      if (c < NL) {                     // a wsf line
        //   HIS 1116: the top row prints the UP/DN pair. HIS 1117: its look-back is 180 s and 120 s,
        //   pinned to wall-clock time, so at 30 s rows that is 6 and 4 rows. A dead tie prints '-'
        const ud = blk[o + UD0 + c];
        d.n.textContent = UDW[ud & 3] + ' | ' + UDW[(ud >> 2) & 3];
        //   HIS 1118: the Mage's side of 50 paints the cell - green over 50.00, red under it, at his
        //   20%. Bits 4-5 of the same byte: 0 neither way, 1 over, 2 under. Exactly 50.00 and a bar
        //   with no value are both left plain.
        //   the strength is meta.mage50, so the page and the knobs file cannot drift apart
        const mg = (ud >> 4) & 3;
        d.style.background = (mg === 1 || mg === 2)
          ? 'color-mix(in srgb, var(--' + (mg === 1 ? 'grn' : 'red') + ') ' + meta.mage50 +
            '%, transparent)'
          : '';
        const s = blk[o + c];           // HIS 1109: TO or AW, bold - now the row's first block
        //   HIS 1117: *"drop the rpred coloring for all but the 2 combined columns"*, then *"I'm
        //   not using r-pred at all so it can be disabled"* - so NO cell carries a colour from it,
        //   the sums included, and the 55% AW background went with it: that class only ever shaded
        //   the red and the green
        d.className = '';
        //   HIS 1119 `fdm3-infence-power`: the code is bits 0-2, the power band is bits 3-5 held as
        //   band+1, so 0 prints a bare TO(inf). The suffix goes on a TO(inf) cell only
        //   HIS 1121 +4 and -4: nine bands on 8793, so the band+1 is bits 3-6
        const tc = s & 7, pw = (s >> 3) & 15;
        //   HIS 1119: the suffix goes on BOTH in-fence codes - TO(inf) is 1, AW(inf) is 2
        //   HIS 1120 *"non-tagged (eg "-")"*: a line with no tag inside a trade prints "-" when the page carries his
        //   counter-side-of-50 rule; outside a trade, or without the rule, it stays blank as before
        //   HIS 1120: "-(inf)" 5 and "-(exf)" 6 on the counter side of 50; "-(inf)" carries the band like TO(inf)
        //   HIS 1121 on 8793: TO(exf) 3, AW(exf) 4 and "-(exf)" 6 carry it too when meta.ifpexf is 1
        const sf = (tc === 1 || tc === 2 || tc === 5 || (meta.ifpexf && (tc === 3 || tc === 4 || tc === 6))) && pw
             ? meta.ifp[pw - 1] : '';   // HIS 1109 (inf) / (exf)
        //   HIS 1110: crossovers on a LOW target-side, crossunders on HIGH; X and E on one ws1 bar join, 4 spaces apart
        const xc = blk[o + NL + 2 * (NC - NL) + c];
        //   HIS 1121 on 8793: +32 = a ws2..ws15 line (HIS 1122, ws8..ws15 at 1121) leaving +4 or -4 - the suffix, sign and digit, in red; the tag keeps
        //   its white or grey
        //   HIS 1124 fdm3-htf-oracle: +64 = the orange b9 colour, a move against the target-side off 3, 2 or 1
        const bc = sf ? (xc & 32 ? 'r4' : xc & 64 ? 'o4' : '') : '';
        d.ta.textContent = (meta.tacodes[tc] || NB) + (bc ? '' : sf);
        if (bc) { const r = document.createElement('span'); r.className = bc; r.textContent = sf; d.ta.appendChild(r); }
        d.xc.textContent = [xc & 1 ? (sd < 0 ? 'X↑' : '↓X') : '', xc & 2 ? (sd < 0 ? '↑E' : '↓E') : '']
          .filter(Boolean).join('    ') || NB;
        d.ta.className = xc & 28 ? 'f' : 'g';  // HIS 1110: TO on the row before, AW on this one - white, this row only;
                                               // HIS 1111: every other TO/AW grey, on a -1/+1 cell too;
                                               // HIS 1113: ws1 only, TO(exf) after anything else - white, the same way;
                                               // HIS 1120: ws5 only, TO(inf) after TO(exf) - white, the same way
      } else {                          // a sum: its TO:x AW:x and TO(exf) lines, both towards/away
        //   HIS 1117: with r-pred off the sum has no number of its own, so its top line is blank and
        //   the other two keep their places - the cell's three lines stay aligned with a line cell's
        d.n.textContent = NB;
        d.className = sx.trim();
        const k = o + NL + 2 * (c - NL), to = blk[k], aw = blk[k + 1];
        d.ta.textContent = to < 0 ? NB : 'TO:' + to + '  AW:' + aw;   // HIS "TO:x  AW:x", the weekday size
        //   HIS 1111: "TO(exf)" under it when any of the column's lines reads TO(exf); the TO:x AW:x line's style.
        //   HIS 1113 *"add the count of TO(exf) lines, if TO(exf) is printing"*: "TO(exf):x"
        const tx = blk[o + 2 * NL + 2 * (NC - NL) + (c - NL)];
        d.xc.textContent = tx > 0 ? 'TO(exf):' + tx : NB;
        d.xc.className = 's';
      }
    }
    //   HIS 1124/1125 the VWAP cells: % x 100 as int16, low byte first; -32768 is no pair of anchors yet
    for (let k = 0; k < p.vws.length; k++) {
      const v = p.vws[k];
      v.className = (k === 0 ? 'sx' : '') + (blk ? '' : ' w');
      for (let q = 0; q < 6; q++) {
        if (!blk) { v.ls[q].textContent = q === 0 ? '·' : NB; continue; }
        const b = o + meta.vw + 12 * k + 2 * q, x = (blk[b + 1] << 8) | (blk[b] & 255);
        v.ls[q].textContent = x === -32768 ? NB : VWL[q] + ': ' + (x >= 0 ? '+' : '-') + (Math.abs(x) / 100).toFixed(2);
      }
    }
    p.i = i; p.ok = !!blk;
  }
  const t = meta.t0 + first * meta.step;
  document.getElementById('top').textContent = 'top row: ' + fmt(t);
  markDay(fmt(t).slice(0, 10));
  fitDeep();
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
    const nd = new Date(Date.UTC(y, m, 0)).getUTCDate();
    //   HIS 1118: *"the '31' in august can wrap around and sit on the top row, ie the top row will
    //   now print '31, , , , ,1,2'"*. Every month is laid out in 5 rows of 7, and a day that would
    //   have needed a 6th row goes to the same column in the FIRST row instead. It always fits:
    //   the spill is lead + nd - 35 cells and the first row has lead empty cells, and nd is never
    //   more than 35, so the spill can never reach the 1st of the month.
    const CELLS = 35;
    const cell = new Array(CELLS).fill(null);
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
      const p = lead + d - 1;
      const at = p < CELLS ? p : p - CELLS;
      if (cell[at]) throw new Error('two days want cell ' + at + ' of ' + ym);
      cell[at] = b;
    }
    for (const c of cell) g.appendChild(c || document.createElement('span'));
    mon.appendChild(g); cal.appendChild(mon);
  }
}
async function init() {
  meta = await (await fetch('meta')).json();
  NL = meta.lines.length; NC = NL + meta.sums.length; NS = meta.stride; UD0 = meta.updn;
  [ALO, AHI] = meta.alock;   // HIS 1117: A is locked, the page only reports it
  const hd = document.getElementById('hd');
  //   HIS 1124 fdm3-htf-oracle: *"replace all columns except `ws1 time`"* - the time, then his 16 columns
  if (meta.title) { document.title = meta.title; document.getElementById('what').textContent = meta.htf
    ? 'fdm3-htf-oracle - ws20 to ws30, ws45, ws60, ws90, ws120, ws240 on 1-minute rows, with towards/away and b9'
    : document.getElementById('what').textContent; }
  const NV = (meta.vwtfs || []).length;   // HIS 1124/1125 the VWAP columns, far right
  if (NV) { RH = 98; document.body.classList.add('tall'); }
  const heads = meta.htf ? ['ws1 time (UTC)'].concat(meta.lines, (meta.vwtfs || []).map(t => 'ws' + t + ' vw pct'))
                         : ['ws1 time (UTC)', 'SL%'].concat(meta.lines, meta.mnrs, meta.sums);
  for (const h of heads) { const d = document.createElement('div'); d.textContent = h; hd.appendChild(d); }
  if (NV) hd.children[1 + NL].className = 'sx';
  if (!meta.htf) { hd.children[NL + 2].className = 'sx'; hd.children[NL + 3].className = 'sx'; }
  body.style.height = (meta.rows * RH) + 'px';
  //   HIS 1111: no sideways bar. The lines stay CW; the time column takes what is left, then M-no-rev and the
  //   sums give way together
  //   HIS 1115 *"keep the table's existing columns at their current width, ie don't attempt to fill the lost column space"*:
  //   the box narrows by the two dropped columns, less the SL% column
  //   HIS 1117: the one wide M-no-rev column becomes two skinny ones
  const inner = box.firstElementChild;
  const tw = meta.htf ? TW + NL * CW + NV * VWW : TW + SLW + NC * CW + meta.mnrs.length * MNRW;
  inner.style.setProperty('--gt', meta.htf ? 'minmax(' + TMIN + 'px,1fr) repeat(' + NL + ',' + CW + 'px)'
                          + (NV ? ' repeat(' + NV + ',' + VWW + 'px)' : '')
    : 'minmax(' + TMIN + 'px,1fr) ' + SLW + 'px repeat(' + NL + ',' + CW + 'px) repeat(' +
      meta.mnrs.length + ',' + MNRW + 'px) repeat(' + (NC - NL) + ',minmax(' + SMIN + 'px,' + CW + 'px))');
  //   after the body's height, so the vertical scrollbar is in the box's width
  document.querySelector('.wrap').style.maxWidth = (tw + box.offsetWidth - box.clientWidth + 32) + 'px';
  buildCal();
  //   HIS 1113 *"add a button that flips the pivots directions, ie the green rows will become the red rows and vice
  //   versa"*, on the right of the calendars. No button changes the scroll position (his 1112 positioning rule):
  //   the rows on screen stay where they are and only their cells change
  //   HIS 1122 *"I'll use a button to flip between the 2 trades"*: on the two-trade page the same button, labelled
  //   with the trade on screen - short as found, long flipped
  const two = meta.pivots === 'two';
  const fp = document.createElement('button'); fp.className = 'tog'; fp.textContent = two ? 'short' : 'flip pivots';
  fp.title = two ? 'the short trade, target-side LOW, on every row; click for the long trade, target-side HIGH'
                 : 'flip the side of every ' + meta.pivlabel + ' pivot, so a HIGH pivot reads LOW and a LOW pivot HIGH; click again for the sides as found';
  fp.setAttribute('aria-pressed', 'false');
  fp.onclick = () => {
    FLIP = FLIP ? meta.flips[0] : meta.flips[1];
    fp.classList.toggle('on', FLIP > 0); fp.setAttribute('aria-pressed', String(FLIP > 0));
    if (two) {
      fp.textContent = FLIP > 0 ? 'long' : 'short';
      fp.title = FLIP > 0 ? 'the long trade, target-side HIGH, on every row; click for the short trade, target-side LOW'
                          : 'the short trade, target-side LOW, on every row; click for the long trade, target-side HIGH';
    }
    for (const p of pool) p.ok = false;
    schedule();
  };
  document.getElementById('btnrow').appendChild(fp);
  //   HIS 1115 *"create two buttons that A will be applied to - the first button shows A for ws1-ws6, and the second
  //   shows A for ws7-ws15"*. A: lift-off's window extreme off every bar of its span, not only the six samples. They
  //   combine with each other and with flip pivots
  //   HIS 1119: *"rebuild 8792 with a pivot +15 minute button , and drop pivot +30 button"*, ruled
  //   for all three pages. Every pivot meta.shift minutes later, so every pseudo trade
  //   opens and closes that much later on the same side. 15 at his 1112, 30 at his 1117, 15 again
  if ((meta.offs || [0, meta.shift]).length > 1) {   // HIS 1122: the two-trade page builds no +15 set
    const pb = document.createElement('button'); pb.className = 'tog';
    pb.textContent = 'pivots +' + meta.shift + ' min';
    pb.title = 'every ' + meta.pivlabel + ' pivot ' + meta.shift + ' minutes later; click again for the pivots as found';
    pb.setAttribute('aria-pressed', 'false');
    pb.onclick = () => {
      OFF = OFF ? 0 : meta.shift;
      pb.classList.toggle('on', OFF > 0); pb.setAttribute('aria-pressed', String(OFF > 0));
      for (const p of pool) p.ok = false;
      schedule();
    };
    document.getElementById('btnrow').appendChild(pb);
  }
  //   HIS 1118: *"the only way to answer is a button on 8791"* - whether his B reaches the
  //   towards/away ws{TF}x races (the 1112 row rule and the hunt samples) as well as the cross row.
  //   On = B. The cross row's own x bits are at B in every state; this button moves the TO/AW cells.
  if ((meta.xres || ['winner']).length > 1) {   // HIS 1119: the server builds one state, so no button
    const xb = document.createElement('button'); xb.className = 'tog';
    xb.textContent = 'towards/away x race = B';
    xb.title = 'the towards/away ws{TF}x race re-opens on crossing back over ANY of its three race lines (his B); '
             + 'click again for his 1109 4B, re-opening only over the line that won';
    xb.setAttribute('aria-pressed', 'false');
    xb.onclick = () => {
      XRE = XRE === 'winner' ? 'any' : 'winner';
      xb.classList.toggle('on', XRE === 'any'); xb.setAttribute('aria-pressed', String(XRE === 'any'));
      for (const p of pool) p.ok = false;
      schedule();
    };
    document.getElementById('btnrow').appendChild(xb);
  }
  //   HIS 1117 banked A: the two buttons show the locked positions and cannot be clicked
  for (const [i, band] of (meta.htf ? [] : meta.abands).entries()) {   // HIS 1124: no ws1-ws15 on htf, so no A
    const ab = document.createElement('button'); ab.className = 'tog'; ab.textContent = 'A ' + band;
    const on = meta.alock[i];
    ab.title = 'lift-off A on the ' + band + ' r lines: BANKED ' + (on ? 'on' : 'off') + ', not a button';
    ab.disabled = true;
    ab.classList.toggle('on', on > 0); ab.setAttribute('aria-pressed', String(on > 0));
    document.getElementById('btnrow').appendChild(ab);
  }
  //   HIS 1118 *"as wide as the buttons space"*: the table is sized from the button row, which can
  //   itself wrap at a narrow window, so it is re-measured on every resize
  //   HIS 1124 on 8795, his answer *"a dox no deeper than the calendars"*: its button row is one button wide, so the box
  //   widens from that width until its bottom is no lower than the calendars' bottom, or until it reaches the room right
  //   of the calendars. Between resizes it only ever widens, so the top row and cache text changing cannot shake it.
  //   8793 and 8794 keep his 1118 width alone. MINE: the 10 px step
  if (meta.htf) fitDeep = () => {
    const info = document.getElementById('info'), cal = document.getElementById('cal');
    const room = cal.parentElement.clientWidth - cal.offsetWidth - 18;   // 18 px, the strip's own gap
    let x = info.offsetWidth;
    while (info.getBoundingClientRect().bottom > cal.getBoundingClientRect().bottom + 0.5 && x + 10 <= room) {
      x += 10; info.style.width = x + 'px';
    }
  };
  const fitInfo = () => {
    const w = document.getElementById('btnrow').offsetWidth;
    if (w > 0) document.getElementById('info').style.width = w + 'px';
    fitDeep();
  };
  fitInfo();
  window.addEventListener('resize', fitInfo);
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
    print(ROWS_NOTE)                             # HIS 1124 the row cache: read, written, or why not
    print('CONTROL flagged cells %d, 1109 measurement %d: %s'
          % (FLAGGED, CONTROL_FLAGGED, 'MATCH' if FLAGGED == CONTROL_FLAGGED else 'DIFFERS'))
    for k, (label, _) in enumerate(SUMS):
        v = RP[:, len(LINES) + k].astype(int)
        print('%s: below 0 %d, at 0 %d, above 0 %d, min %d, max %d'
              % (label, (v < 0).sum(), (v == 0).sum(), (v > 0).sum(), v.min(), v.max()))
    print('towards/away cells: TO(inf) %d, AW(inf) %d, TO(exf) %d, AW(exf) %d, none %d'
          % tuple((TAC == k).sum() for k in (1, 2, 3, 4, 0)))
    _xc = RP[:, O_XC:O_XC + len(LINES)]
    print('cross row cells: X only %d, E only %d, both %d; race re-opens on x %s, on e %s'
          % tuple(list(int(((_xc & 3) == k).sum()) for k in (1, 2, 3)) + [X_REOPEN, E_REOPEN]))
    print('TO -> AW flip cells (white AW text): %d, %d of them on a -1/+1 cell'
          % (int((_xc & 4).astype(bool).sum()), int((_xc & 4).astype(bool).sum())))
    for _bit, _lines, _what in ((8, FLIP_TOX_LINES, 'flips into TO(exf) (white TO(exf) text)'),
                                (16, FLIP_TOINF_LINES, 'HIS 1120 TO(inf) after TO(exf) (white TO(inf) text)')):
        _js = [LINES.index(n) for n in _lines]
        _on = int((_xc[:, _js] & _bit).astype(bool).sum())
        print('%s %s: %d, other columns marked %d' % ('every column' if len(_lines) > 1 else _lines[0], _what, _on,
                                                       int((_xc & _bit).astype(bool).sum()) - _on))
    if HTF:                                      # HIS 1124 the b9 colours against the target-side
        print('HIS 1124 b9 colours on %s, against the target-side: short trade red %d, orange %d; every state red %d, '
              'orange %d' % (', '.join(LINES), int((_xc & 32).astype(bool).sum()), int((_xc & 64).astype(bool).sum()),
                             IFP_REDN[0], IFP_ORGN[0]))
        print('HIS 1124 fdm3-htf-oracle lines: %s %s; towards/away scenario 1 on %d TFs, a state on %s'
              % ('BUILT into' if HTF_USE[2] else 'read from', HTF_USE[0], len(TA_TFS), ', '.join(LINES)))
        for _n in VW_NOTE:
            print('HIS 1124/1125 VWAP %s' % _n)
    if not HTF:                                  # fdm3-oracle's own red rule
      print('HIS 1121 red suffix on ws%d..ws%d leaving +4 or -4: %s' % (RED4_TFS[0], RED4_TFS[-1],
        'ON, pivots as found %d cells (%s), every state %d' % (
            int((_xc & 32).astype(bool).sum()),
            ', '.join('%s %d' % (n, int((_xc[:, j] & 32).astype(bool).sum())) for j, n in enumerate(LINES)
                      if (_xc[:, j] & 32).any()), IFP_REDN[0]) if IFP_RED4 else 'off, no +4 or -4 on this page'))
    #   HIS 1117: with r-pred off there is no r-pred byte in the row, so the 1110 count of its
    #   -1/+1 cells on an AW line cannot be taken from the page any more. The 1109 control above
    #   still checks the producer on its own minute grid.
    #   HIS 1119: one byte per row, just before the side byte
    _MNR = [RP[:, STRIDE - 1 - (len(MNR_TOPS) - k)].astype(int) & 15 for k in range(len(MNR_TOPS))]
    for k, (label, _) in enumerate(SUMS):
        _ex = RP[:, O_TOEXF + k].astype(int)
        print('%s: rows printing TO(exf) %d of %d, most lines reading TO(exf) on one row %d'
              % (label, int((_ex > 0).sum()), len(_ex), int(_ex.max())))
    for _lab, _top, _mn in zip(MNR_LABELS, MNR_TOPS, _MNR):
        _legs = int((np.diff(RP[:, STRIDE - 1].astype(int)) != 0).sum()) + 1
        print('%s (ws1..ws%dMage, the INCOMING leg\'s max, carried): rows with a TF %d of %d, '
              'highest %d, legs on the page %d'
              % (_lab, _top, int((_mn > 0).sum()), len(_mn), int(_mn.max()), _legs))
    #   HIS 1118 the Mage's side of 50: bits 4-5 of each line's up/dn byte, counted over every cell
    _m50 = (RP[:, O_UD:O_UD + len(LINES)].astype(int) >> 4) & 3
    _thin = int(np.argmin((_m50 > 0).sum(0)))
    print('Mage side of 50 (ws1..ws%d, emerging, paints at %d%%): over 50.00 %d cells, under 50.00 '
          '%d, neither %d of %d; thinnest line %s, %d of %d cells painted'
          % (len(LINES), MAGE50_PCT, int((_m50 == 1).sum()), int((_m50 == 2).sum()), int((_m50 == 0).sum()),
             _m50.size, LINES[_thin], int((_m50[:, _thin] > 0).sum()), len(_m50)))
    print('pivots: %s' % PIVOTS)
    _lrg = (RP[:, O_MNR].astype(int) & SMALL_LRG) > 0
    print('fdm3-small-trade (max %d highband lines in TO(exf)): pivots as found, rows in a trade %d, lrg %d; '
          'every state, rows in a trade %d, lrg %d'
          % (SMALL_MAX, int((RP[:, STRIDE - 1] != 0).sum()), int(_lrg.sum()), SMALL_ROWS[0], SMALL_ROWS[1]))
    print('fdm3-infence-power: %d in-fence cells over every state - TO(inf), AW(inf) and HIS 1120 -(inf) - '
          '%d of them bare (%.2f%%), the band on the %s r - a line has no value until its warm-up ends'
          % (IFP_INF[0], IFP_BARE[0], 100.0 * IFP_BARE[0] / max(1, IFP_INF[0]), IFP_READ))
    print('HIS 1121 suffix on TO(exf), AW(exf) and -(exf): %s' % ('ON, %d cells over every state, %d of them bare'
                                                                   % tuple(IFP_EXFN) if IFP_EXF else 'off'))
    print('HIS 1120 "-" on the counter side of 50: %s' % ('ON, emerging r, strictly past %g' % UNTAG if UNTAG else 'off'))
    if len(OFFS) > 1:                            # HIS 1122: the two-trade page builds no +15 set
      print('HIS 1121 B pivots +%d: each trade runs from its own open to its close + %d min and prints from open + %d min; '
          'shared with the as-found states, %d bars of towards/away and %d page rows asserted equal, byte for byte '
          '(a trade\'s first printed row may differ only in its flip marks)'
          % (PIV_SHIFT, PIV_SHIFT, PIV_SHIFT, CARRY_SHARED[0], CARRY_ROWS[0]))
    print('HIS 1121 r config: %s' % (
        'the stored wsf r row %s, off the shared line cache' % (ln.SPEC['r'][0],) if R_USE is None else
        '%s (k_len|rsi|stc|src), ws1r..ws30r %s the separate cache %s; its ws30r control at the DB row matched '
        'exactly. The shared line cache, the DB row and v4\'s R_* knobs are not touched'
        % (R_USE[1]['kline'], 'BUILT into' if R_USE[2] else 'read from', R_USE[0])))
    print('HIS 1120 towards/away lift-off: %s' % ('tolerance %g r-points, hold %d bars - towards/away, the page\'s only lift-off reader'
                                                 % TALIFT if TALIFT else 'v4\'s banked pair, tolerance %g, hold %d'
                                                 % TA.lift_knobs()))
    print('fence: %d/%d, locked (HIS 1115). fence reset TO: %g/%g, banked (HIS 1117)'
          % (FNC, 100 - FNC, FENCE_RESET_TO, 100 - FENCE_RESET_TO))
    _lo, _hi = O_TA, O_TA + len(LINES)
    for (_off, _fl, _xre), _m in MATS.items():
        if (_off, _fl, _xre) == (0, 0, 'winner'):
            continue
        _tac = _m[:, _lo:_hi]
        print('pivots +%d min%s, x race re-opens on %s: rows whose target-side differs from the '
              'pivots as found %d of %d, cells that differ %d of %d; TO(inf) %d, AW(inf) %d, '
              'TO(exf) %d, AW(exf) %d'
              % ((_off, ', flipped' if _fl else '', _xre,
                  int((_m[:, STRIDE - 1] != RP[:, STRIDE - 1]).sum()), len(RP), int((_m != RP).sum()), RP.size)
                 + tuple(int((_tac == k).sum()) for k in (1, 2, 3, 4))))
        #   HIS 1117 banked A: there is no A-off state to compare against any more, so the per-column
        #   "cells A moved" line is gone with the buttons. Per column, what the pivot offset moved:
        _ref = MATS[(0, _fl, _xre)]
        _dc = (_m[:, _lo:_hi] != _ref[:, _lo:_hi]).sum(0)
        if _off:
            print('    TO/AW cells moved by the +%d min pivots, against the same flip at +0: %s'
                  % (_off, ', '.join('%s %d' % (n, int(c)) for n, c in zip(LINES, _dc) if c) or 'none'))
        #   HIS 1118 BUTTON: what B moves, against the same pivots and flip at his 1109 4B
        if _xre != 'winner':
            _b = MATS[(_off, _fl, 'winner')]
            _db = (_m[:, _lo:_hi] != _b[:, _lo:_hi]).sum(0)
            print('    TO/AW cells moved by B on the towards/away x race, against 4B at the same '
                  'pivots and flip: %d of %d; per column %s'
                  % (int(_db.sum()), len(RP) * len(LINES),
                     ', '.join('%s %d' % (n, int(c)) for n, c in zip(LINES, _db) if c) or 'none'))
    print('towards/away knobs (banked): ' + ' '.join('%s=%s' % (k, v) for k, v, _, _ in TA.KNOBS))
    print('open http://127.0.0.1:%d' % PORT)
    sys.stdout.flush()
    ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
