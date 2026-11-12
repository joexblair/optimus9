# towards/away, the 1109 update — BANKED and LIVE

GOAL: a better towards/away mech, with every decision anchored on the trade's target-side. Joe 1109: *"your next
task is to help me build a better towards/away mech, and we'll use the ws2Mage pivots to simulate a trade's
`target-side`"* and *"target-side is the anchor for all towards/away decisions"*. His one-sentence goal is not
stated yet; it goes on this line when he gives it.

| item | state |
|---|---|
| banked | 1109, *"bank the towards/away update"*. Knobs in `1109_towards_away/ta_knobs.py`; a run with any knob off the bank refuses unless `W_TA_EXPERIMENT=1` |
| live | 1109, *"make the machine live"*. In his sense: this is the towards/away mech we develop on. It is NOT wired into fdm2 or o9-live; nothing asked for that |
| code | `docs/octo-freedom/1109_towards_away/towards_away.py` (the mech), `ta_knobs.py` (its knobs) |
| output | the r-pred web UI, `docs/octo-freedom/1022_v4/out/rpred_ui.py`, port 8788 - section 7 |
| 1110 | the lift-off update and ws1-3 are BANKED and LIVE - section 10, his *"after that's validated, bank both mechs and make their configs the live machine"*. The lift-off spec is `1110_lift_off_e.md` |
| 1110 later | the flip at 50 - section 11, his *"the AW/TO logic needs refining"*. In the banked knobs as on (FLIP50 1) |

---

## 1. His spec, 1109, the towards/away parts

He moved one note OUT, on SRP: *"my update has accidentally pulled the lift-off mech in, and makes it look like a part
of the towards/away mech.  this is not SRP"* / *"here's the poorly placed note - it is a separate update for lift-off
mech, and does not apply to towards/away mech.   the common/shared artifact is the newly built ws{TF}e"*. That note
is section 8. What stays:

- *"build a new BB%B line named `e`, eg ws30e, with len 3, mult 0.5, src close. apply to ws4-ws30"*
- *"use the dynamic indicator config table: it saves you from creating 27 single lines"*
- *"emerging line values will now be captured when ws{TF}e crosses race:{boundary,Mage,r} (standard under or over
  cross rules)"*
- *"the r line's latest extremum is stored, regardless of being in or ex fence"*
- *"at the start of a trade, an r line is automatically tagged as towards"* / *"it will stay automatically tagged as
  towards until it reaches ex-20/80-fence on the target-side (or fails to reach ex-fence, more info below)"*
- *"after reaching ex-fence, towards is now affected by the mech's calculations"*
- *"extremum can be stored while an r line is infence, but it has no vote for the `away` line verdict in scenario 1"*
- *"do/don't use `fdm2-rline-enhance` mech to improve the results? I think no, but I'm pinning this here for possible
  testing.  Joe to decide if/when to test"*
- scenario 1: *"the r line's extrema will be stored in the same manner as the existing mech, and used to calculate
  away"*
- scenario 2: *"if a ws{TF}r line prints two infence samples (built by the e-cross sampling) which are within 2% of
  each other"* / *"IF there are >1 r lines within {knob:5} TFs **under** this TF, that are printing away while in
  ex-fence, or printing away  after having left ex-fence (during this trade)"* / *"store the extrema"* / *"declare
  this r line away"* / *"if the line turns back towards ex-fence, then it remains away until it supersedes the
  extrema (the same logic as the existing build)"*
- his examples: *"lowside 08-24 ~1400: ws11r is infence, ws6 to ws9/ws10 are all printing away after being
  ex-fence, or are still in ex-fence"* / *"highside 08-25 0328: ws13r is infence, so is ws12r. ws8 to ws11 are in
  various states of away"*
- the backtest: *"we will backtest without a derived trade"* / *"there are multiple ws2Mage pivots per side (eg 08-24
  1353 and 1404 on the low side, 1252 and 1314 on the highside). use the last/later pivot time to create the psuedo
  rev-trade signal"*

## 2. His answers, 1109

| # | the question | his answer |
|---|---|---|
| 2 | what gets scored, len 3 against len 2 | *"no action.  leave it on len3"*. The len-2 sweep is dropped |
| 3 | how long the e-cross must hold | 3A: no hold. The sample is taken on the cross bar |
| 4 | how often one ws{TF}e race samples | 4B: the first of the race lines only; the race re-opens once e crosses back over that line the other way |
| 5 | "partially building" a lift-off setup | *"this one is stashed for the lift-off update.  the answer is A"* - section 8 |
| 6 | which existing mech scenario 1 copies | *"the extremum is set by lift-offs reversal, which uses emerging"* |
| 7 | "within 2%" | 7A: within 2.0 r-points, the latest two samples |
| 8 | when scenario 2 is tested | 8A: on the bar of the second sample only |
| 9 | which extremum scenario 2 stores | 9B: the more target-side of the two samples |
| 10 | which r lines | 10A: ws4r to ws30r, the lines that have an e line. 1110: *"add ws1-3 to towards/away and liftoff, and update webUI"* - ws1r to ws30r |
| - | the 12 reads I took from precedent | none corrected |
| - | the line cache | *"update the cache"* - the e lines are cached (section 6) |

## 3. The mech, in firing order

| step | what happens |
|---|---|
| ws{TF}e | BB%B len 3, mult 0.5, src close, EMERGING, ws1..ws30, built from ONE row of `mech_line_config` (his indicator config spec, `docs/mech_line_config_spec.md`): mechanic `towards-away`, role `e`, 60..1800 s every 60 s, version 2 (1110; version 1 was ws4..ws30). Read from the line cache through v4_ws_e |
| the pseudo trade | sweep-pivots' ws2Mage legs; each leg's pivot is its most extreme tape close (low for a leg opened by a LOW cross). The LAST pivot of each same-side run is the pseudo rev-trade signal. A trade opens on one signal and runs to the next. Its target-side is the side of the run it closes on: a trade opened at a HIGH run's last pivot has a LOW target-side. LOOKAHEAD on purpose: a pivot is fixed only when its leg closes |
| auto-towards | at the trade's open every line is TO. A line stays TO while it has not reached ex-20/80 on the target-side this trade. Reached once, it stays reached for the trade |
| scenario 1 | the line has reached ex-20/80. Every target-side lift-off reversal on its emerging r stores its pivot's value at the reversal's stamp (lift bar + 7 bars = 35 s). Only an extremum whose value is ex-20/80 votes. The latest voting extremum makes the line AW from its stamp; the line is TO from the first bar its emerging r goes past that extremum toward the target-side |
| e-samples | ws{TF}e crosses its race lines: UNDER 85 / ws{TF}Mage / ws{TF}r on a HIGH target-side, OVER 15 / Mage / r on a LOW one. No hold. The first race line crossed wins; the race re-opens when e crosses back over it. The sample is ws{TF}r's emerging value on the cross bar |
| scenario 2 | the line has not reached ex-20/80. On the bar of a new sample: if it and the sample before it (this trade) are both in-fence and within 2.0 r-points, AND more than 1 of the 5 lines under it read AW in scenario 1, the more target-side sample is stored and the line is AW. It is TO from the first bar its emerging r goes past that extremum |
| the flip at 50 | 1110, scenario 1 and 2: an AW line whose emerging r has been on the far side of 50 (above on a LOW target-side, below on a HIGH one) since the AW started - the start bar counts - is TO from the first bar r is back on the target side of 50. The extremum is retired, as when r goes past it |

## 4. KNOBS — every one, including those not called out as knobs

### 4a. Banked in `ta_knobs.py` (env `W_TA_<NAME>`, off-bank refuses)

| knob | value | units | what it does | from |
|---|---|---|---|---|
| TF_LO | 1 | TF | the lowest r line with a state | his 1110 add ws1-3 (was 4, his 10A) |
| TF_HI | 30 | TF | the highest | his 10A |
| E_MECH | towards-away | config row | the ws{TF}e row's mechanic in `mech_line_config`. 1110: read from v4_ws_e, the line's one home, pinned here | MINE (the name), his words |
| E_VERSION | 2 | config version | the ws{TF}e row's version: len 3, ws1..ws30 | *"leave it on len3"*; his 1110 add ws1-3 |
| RACE | boundary, Mage, r | race lines | what ws{TF}e races to; the order a tie is reported in | his race:{boundary,Mage,r} |
| RACE_READ | closed_prev | read | how the r and Mage it races to are read | the standard race (v4_fdm2.x_race); my read, not corrected |
| E_STEP | 48 | bars = 240 s | his walk back to look forward's step, for the e-sample. 1110: read from v4_lift_e, pinned here | his 1110 1A |
| UNDER | 5 | TFs | how many TFs under the line scenario 2 reads | his {knob:5} |
| UNDER_GT | 1 | lines | scenario 2 needs MORE than this many of them AW | his ">1" |
| PAIR_PTS | 2.0 | r-points | how close the two samples must be | his 7A |
| SUPERSEDE | strict | rule | past the extremum ('strict') or at-or-past ('inclusive') ends AW | MINE |
| PIVOT_LINE | ws2Mage | line | the Mage whose sweep-pivots pivots make the pseudo trades | *"use ws2Mage pivots"* |
| FLIP50 | 1 | on/off | the flip at 50; 0 is the 1110 bank before it | his 1110 *"the AW/TO logic needs refining"* |
| FLIP50_LEVEL | 50.0 | r-points | the level r crosses | his "past 50" |
| FLIP50_READ | emerging | read | the r read for the 50 crosses | his 1110 answer (closed-prev was the other choice) |

### 4b. Read from their own homes (banked there, not re-declared)

| knob | value | units | home | used for |
|---|---|---|---|---|
| e: line type | BB%B | - | mech_line_config row | ws{TF}e |
| e: length | 3 | bars of the TF | mech_line_config row | ws{TF}e |
| e: mult | 0.5 | std devs | mech_line_config row | ws{TF}e |
| e: src | close | - | mech_line_config row | ws{TF}e |
| e: value mode | emerging | - | mech_line_config row | ws{TF}e |
| e: TF band | 240..1800 s, step 60 s | seconds | mech_line_config row | ws4e..ws30e |
| e: boundaries | 85 / 15, offset 0 | r-points | mech_line_config row | carried on the row |
| FDM_FNC_2080 | 20 | r-points | v4_knobs | the 20/80 fence: LOW at or below 20, HIGH at or above 80 |
| FDM_EXF_READ | either | read | v4_knobs | ex-20/80 by closed-prev OR the emerging extreme |
| FDM_EXF_EM_BARS | 12 | bars = 60 s | v4_knobs | the emerging extreme's span, ending at the bar |
| OOB_FNC | 15 | r-points | v4_knobs | the e race's boundary: 15 LOW / 85 HIGH |
| LIFT_PTS | 6 | samples | v4_knobs | lift-off's window |
| GAP_PER_TF | 2.8 | bars per TF-minute | v4_knobs | lift-off's sample gap, round(TF x 2.8) |
| LIFT_TOL | 2.0 | r-points | v4_knobs | how far off the window extreme lifts off |
| LIFT_WOB | 8 | bars = 40 s | v4_knobs | lift-off's hold; the stamp is lift + 7 bars |
| SP_XWOB | 18 | bars | v4_knobs | a ws2Mage oob->ib cross holds 18 bars (cross + 17 = 85 s) to confirm |
| r line | K 7\|5\|8\|close, emerging | - | mech_line_config `wsf` r | ws4r..ws30r, the same arrays as the cache |
| Mage line | BB 38\|0.93\|close, emerging | - | mech_line_config `wsf` Mage | the race's Mage, closed-prev per TF |
| pivot price | the tape's raw close | - | v4_backstop_trades.prices | the pivot inside each leg |
| E_CONTROL_SUM | 2174735698.786861 | sum | towards_away.py | the cached e lines' known-good total, checked every load |
| E_CONTROL_AT | 2026-08-25 03:28:00, ws30e 99.629759 | value | towards_away.py | a second known-good value, checked every load |

### 4c. Rules fixed in code (no knob; a change is a code change)

| rule | from |
|---|---|
| every line TO at the trade's open | his "automatically tagged as towards" |
| ex-20/80 reached once stays reached for the trade | his "after having left ex-fence (during this trade)" |
| scenario 1's extremum = the lift-off reversal's pivot value, on emerging r, stored at its stamp | his answer 6 |
| only an ex-20/80 extremum votes in scenario 1 | his "no vote" |
| the LATEST voting extremum governs | his "latest extremum" |
| e-cross: HIGH crosses UNDER, LOW crosses OVER | his "standard under or over cross rules" |
| e-cross has no hold | his 3A |
| first race line wins; re-opens on crossing back over it | his 4B |
| pair = the latest two samples this trade | his 7A |
| scenario 2 tested on the second sample's bar only | his 8A |
| scenario 2 stores the more target-side sample | his 9B |
| the pseudo signal = the last pivot of each same-side run | his "use the last/later pivot time" |
| a trade's target-side = the side of the run it closes on; the trade spans [signal, next signal) | MINE, accepted 1109 |
| each ws{TF}e pairs with its own ws{TF}r only | MINE, accepted 1109 |
| once superseded, an extremum is retired: TO until a newer one is stored | MINE |
| a newer qualifying scenario-2 pair replaces the stored extremum | MINE |
| a reversal votes only when its pivot is at or after the trade's open | MINE |
| two race lines crossed on one bar = one sample; re-opens on crossing back over either (84,990 such samples) | MINE |
| a sample is in-fence by its own value, same side | MINE |
| a scenario-2 line that reaches ex-20/80 moves to scenario 1 | MINE, accepted 1109 |
| each trade's race starts open | MINE |
| a line with no emerging r value at the bar has no read | MINE |
| fdm2-rline-enhance is not used | his pin |
| the flip at 50 covers scenario 1 and scenario 2 | his 1110 answer |
| an AW that starts with r already on the far side of 50 counts as "returned past 50" | his 1110 answer, after the ws1 2026-09-21 12:39:15 and ws6 2026-08-24 06:54:00 examples |
| after the flip at 50 the extremum is retired: TO until a newer one is stored | his 1110 answer, the same as going past it |
| the flip at 50 is strict both ways | MINE; no bar on ws1r..ws30r sits at exactly 50.00, emerging or closed-prev, so it moves nothing |
| every line reads TO on each trade's open bar - an assert in run() | his 1109 auto-towards; his 1110 *"make sure the update doesn't impact the "all lines start with TO at the beginning of a trade""* |

## 5. Checks, 1109

| check | result |
|---|---|
| e lines: cached arrays against a fresh in-memory build | max diff 0, NaN positions equal, 27 of 27 |
| e lines: ws30Mage control row built beside them | equal to the cached ws30Mage |
| line cache: existing files changed by the e write | 0 (27 new files) |
| ex-20/80 reader, vectorised, against v4_fdm2.ex2080_line | 2,400 sampled bars, 0 differ |
| the mech against a separate per-bar recompute (scalar reads, its own race and pair code) | 320 bars (120 at scenario-2 AW starts/ends), 0 mismatches |
| bank control: md5 over every state array, before and after the knobs were wired | identical: 1030342900d8992240c7c824a6679ced |
| bank control after the 1110 lift-off update (ws4..ws30) | 4c31b0d4f508b1f7527515d23fb74322 |
| bank control after ws1-3 were added, BANKED 1110 | 830d2d7d16fc177a706ff99f12a55c74 |
| web UI data against a fresh run | 136,079 rows, 0 mismatches |
| web UI (inf)/(exf) against the scalar reader | 8,400 cells, 0 mismatches |
| pseudo signals on 2026-08-24 against his validated ws2Mage table | 19 of 19 equal |
| trade init: trades whose first row reads TO on all 27 lines | 1,564 of 1,564. 2 trades are too short for a row (2026-07-13 14:18:10, 10 s; 2026-08-02 09:18:25, 15 s) |

| count, whole tape | value |
|---|---|
| ws2Mage pivots | 3,127 |
| pseudo trades | 1,564, the first opens 2026-07-02 14:33:45 |
| scenario-1 voting extrema | 53,859 |
| e-samples | 533,469 |
| scenario-2 triggers | 24,499 |

## 6. Open: his examples against the run

| example | line | his read | the run |
|---|---|---|---|
| 2026-08-24 ~14:00 LOW | ws6r to ws9r | away or still ex-fence | AW (ws6r-ws8r from 13:56-13:57; ws9r 14:01-14:02) |
| 2026-08-24 ~14:00 LOW | ws10r | away or still ex-fence | TO: reached ex-20/80 at 14:00:00, no lift-off reversal after it in the trade |
| 2026-08-24 ~14:00 LOW | ws11r | in-fence | TO: last samples 13:54:35 and 13:55:50 (42.15), 45 s before the first line under it read AW |
| 2026-08-25 03:28 HIGH | ws8r to ws10r | various states of away | AW |
| 2026-08-25 03:28 HIGH | ws11r | various states of away | TO: ex-fence, first voting reversal stored 03:40:35 |
| 2026-08-25 03:28 HIGH | ws12r | in-fence | AW 03:24:50 to 03:28:30, TO on the 03:28 row |
| 2026-08-25 03:28 HIGH | ws13r | in-fence | TO; first scenario-2 AW 03:34:00 |

## 7. The web UI build — notes

His 1109 ask, in rounds: *"the output of towards/away will be baked into the r-pred webUI. for each row, for each
field, print TO or AW below the number, in a bold font."*, the summary font, *"20% opaque the background color of
"ws1 time UTC", to show the trade direction (red for LOW target-side, green for HIGH target-side)"*, and *"append
`(inf)` or `(exf)` to the `TO` and `AW` labels (example "TO(exf)") to denote if a line is infence or exfence"*. His
read: *"this is a very helpful tool, and it's accurate"*.

| item | value |
|---|---|
| name | HIS 1111: *"name the webUI report: fdm2-diag1"* - BANKED 2026-11-12. The page title and heading carry it; the file (rpred_ui.py) and the o9-rpred-ui service keep their names |
| server | `docs/octo-freedom/1022_v4/out/rpred_ui.py [port]`, stdlib ThreadingHTTPServer on 127.0.0.1, default port 8788. The page is inline (the seam_stream.py pattern) |
| start-up | ~50 s: the r-pred matrix (~2 s) plus `towards_away.build()` with the e lines from the cache. Everything is held in memory; nothing is cached to disk by the UI, so a line change can never be served stale |
| a row | one ws1 bar, timed at its open (UTC) |
| the read bar | the row time + 60 s (12 bars): where closed-prev first shows that ws1 bar. r-pred, TO/AW and (inf)/(exf) are all read there |
| columns | ws1 time, gcws15, gcws30, ws1..ws12 (his wsf), then the ws13-ws20 and ws21-ws30 r-pred sums |
| r-pred cell | predict_breach(r, m, Mage), emerging: hi 85, lo 15, fence 70/30, tol 0. -1 red, +1 green; a missing input reads 0 (his "keep 0") |
| sum cells | red < 0, green > 0, orange at 0 |
| TO / AW | bold, 10 px, under the number, ws1..ws12 (his 1110 add ws1-3). gcws15 and gcws30 print none |
| (inf) / (exf) | ex-20/80 on the target-side at the read bar, by the banked reader the mech uses (closed-prev, or the emerging extreme of the 60 s to that bar) |
| sum labels | `TO:x  AW:x` at 10 px, the count of its lines reading TO and AW |
| time cell | 20% red for a LOW target-side, 20% green for HIGH; no colour before the first trade |
| a -1 / +1 on an AW line | HIS 1110: *"for the webUI - any r-pred signal that prints on an AW signal will need to print the fields background at 55% opaque"*. A line cell whose own line reads AW(inf) or AW(exf) at that bar: red or green at 55%, not 100%. The sums are unchanged. Whole tape: 73,286 of the 257,295 red/green cells (110,207 before the 1110 flip at 50) |
| row payload | 49 int8 per row (1110): 14 r-pred, 2 sums, 14 TO/AW codes (0 none, 1 TO(inf), 2 AW(inf), 3 TO(exf), 4 AW(exf)), 4 counts (-1 = no trade), 14 cross codes (0 none, 1 X, 2 E, 3 both, on the row's target-side), 1 target-side |
| the browser cache | 720-row blocks (12 h), 3 blocks ahead in the scroll direction and 1 behind, 60 blocks held, least recently used dropped, a calendar day's blocks fetched on hover |
| row height | 50 px (1110: three lines - the number, TO/AW, the crosses) |
| cross row | HIS 1110: *"the e-crosses and the x-crosses need to be printed on a row under the AW/TO data.  if the target is low side, print only the crossovers. inverted for high side.  center the text.  the format will be "X↑, ↓X, ↓E, ↑E". if ws{TF}e and ws{TF}x  fire on the same ws1 bar, print them together in the label with 4 spaces between them"*; his answer: the x-cross raw, no hold. jig.e_race_wins per side over the whole tape with v4_lift_e.race(tf, side) (15/85 boundary, closed-prev Mage, closed-prev r; first wins; re-opens on crossing back) and ws{TF}x or ws{TF}e (emerging) as the crossing line. A win prints on the row of the ws1 bar it lands in, [open, open + 60 s), in the row's target-side direction. MINE: X first in a joined label; the whole-tape race (lift-off's, not re-opened at a trade's open); ws1..ws12 only. Check: separate recompute on ws1, ws4, ws12, 408,237 cells, 0 mismatches. Whole tape: X only 180,522, E only 285,790, both 183,303 |
| control | CONTROL_FLAGGED 257,295 r-pred cells at -1/+1, printed MATCH at every start |
| cross row colour | HIS 1110: *"change the x/e cross row to a non-bright yellow font"*. Dark yellow, #a68a00 light / #c9a83a dark (MINE, the shades) |
| a clicked row | HIS 1110: *"make a row highlighted if I click on that row"*. A 16% blue tint and a 2 px blue outline. MINE: one row at a time; a click on another row moves it, on the same row clears it; not kept across a reload |
| the legend table | HIS 1110: *"for the webUI, drop the table that starts with"* the a-row line, *"so that the data frame can be bigger"*. Dropped from the page and from /meta. MINE: the data box takes the rest of the window under the calendar and the status line (it was 68% of the window), never under 320 px |
| the TO -> AW flip | HIS 1110: *"now I need to see when a TF flips from TO to AW"* / *"for those 2 fields in 1257, brighten the AW row"* / *"this is a one time application, ie the 'AW's in the following rows are treated normally"*. A ws1..ws12 cell that reads AW on its row and TO on the row before prints its AW text white (black in light mode), his answer "White text", on that row only. 34,149 flip cells over the tape; 4,848 sit on a -1/+1 cell, whose text is already white. MINE: the flag is made in the server, +4 on the cross code |
| the place holder line | HIS 1110: *"make a place holder line for the x/e cross row,  if there is no x/e data available"* / *"this is so that the row's 3 datasets are horizointally aligned"*. Every data cell prints 3 lines, blank where empty. MINE, from his aligned goal: gcws15 and gcws30 also get a blank TO/AW line and the two sums a blank cross line |
| ws13..ws15 columns, the new sums | HIS 1111: *"make ws13,ws14,ws15 their own columns, and populate them with the same datasets"* / *"the last 2 columns will now be ws16-22 and ws23-30"*, labelled without "sum" *"to make the columns thinner"* / *"the gcws15 to ws15 columns stay the same width as they are now"* / *"ws1 time can drop the year"*. Line columns 72.36 px (their 1110 width at the page's 1420 px cap, measured); sums -7..+7 and -8..+8. MINE: the sums also 72.36 px (widest text 52 px), the time column 116 px (text + the 32 px of room it had), the page widens to 1,540 px to hold the table. The 1109 control still checks gcws15..ws12: 257,295 |
| no sideways bar | HIS 1111: *"the frame has a horizontal scroll bar - that can be dropped"* / *"I've tested on multiple resolutions and the bar is still there"*. The box never scrolls sideways; gcws15..ws15 stay 72.36 px, the time column takes what is left (94 px at least) and the two sums give way next (56 px at least), so pixel rounding can't push the table over. MINE: a box under 1,436 px cuts off the right edge |
| grey TO/AW | HIS 1111: *"make the r-pred field's AW/TO inf/exf text grey, unless that field is reporting a AW flip"*. Every TO/AW line prints the 0 cells' grey, on a -1/+1 cell too; only the flip prints white (black in light mode) |
| M-no-rev | HIS 1111: *"add a column between ws15 and ws16-22 that shows when a target-side oob line has not reversed"*, *"and the field will print the **highest** TF"*, *"if there is no Mage qualifying, don't print anything in the field"*. His answers: ws1..ws30Mage; the rule his 1111 table of every change from 2026-09-21 15:44:00 used (*"I asked for the ui update based on that table's output"*) - closed-prev at or beyond 85/15 on the row's target-side, no lift-off reversal (emerging Mage, banked knobs, no e path) knowable at or after the cross INTO oob; a line back inside 85/15 drops out. Read at the row's print bar. MINE: the TF on the number line, weight 600. HIS 1111 *"if the field is populated, add the line's value to the text"*: the line's closed-prev value at the row's print bar (the value the oob test reads), 1 dp as his example - ws23:100.0. MINE: the widest text is 65.0 px, so the column gives way to 68 px at least and the table's least width is 1,504 px (was 1,436 before M-no-rev) |
| bold, brighter cross row | HIS 1111: *"update the x and e cross row:  make the text bold (and brighter if possible)"*. It was weight 700; now 900. Dark mode #c9a83a -> #ecc94b (MINE); light mode keeps #a68a00 |
| TO(exf) under the sums | HIS 1111 *"in the summary columns (16-22 and 22-30)"*: *"if any of the individual lines are printing TO(exf), print "TO(exf)" under the TO:x AW:x row"*. A line reads TO(exf) as a ws1..ws15 cell prints it - TO, and ex-20/80 on the row's target-side by the banked reader - at the row's print bar; ws16..ws22 for ws16-22, ws23..ws30 for ws23-30. It prints on the cell's third line, blank when none. MINE: the TO:x AW:x line's style (10 px, weight 700, the cell's white text), not the cross row's yellow |
| testing | headless Chrome on Windows reaches WSL localhost. `--virtual-time-budget` delays scroll events, so a probe page calls draw() itself |

## 8. NEXT: the lift-off update, kept separate (SRP)

His note, moved out of this mech: *"these ws{TF}e samples augment the lift-off samples"* - an e-sample lands at
(almost) the pxs pivot, so if ws{TF}e fires while *"lift-off is partially building a pre-fire six-sample reversal
setup (ie lines are flattened or printing away from target-side)"*, the e-cross closes the setup and *"lift-off can
print its reversal signal"*.

| item | state |
|---|---|
| "partially building" | his 5A: the line has stopped printing new target-side extremes (no further toward the target than one lift-off sample gap, TF x 2.8 bars, earlier) AND lift-off has not printed a reversal since that extreme |
| the e-cross | the same race as here: no hold, the first race line wins, re-opens on crossing back |
| his scoring | *"the scoring is (would lift-off still complete the same six-sample run and turn it into a reversal, without the early e-cross)"* |
| the e length | len 3 |

This mech CONSUMES lift-off's reversals for scenario 1, so the lift-off update will move scenario 1's states. The
bank control md5 above is the before.

## 10. The 1110 lift-off update - BANKED AND LIVE with ws1-3

His spec: *"when ws{TF}e crosses a racer, "walk back to look forward" for the time when ws{TF}e was most extreme,
before the cross. capture the ws{TF}r value at that time"* / *"-make that bar's value the new r extremum"* /
*"-if the following lift-off sample is less extreme (ie is closer to 50), then print the reversal"* / *"--this might
need a "minimum less extreme" knob - the data will tell us when I review the update"*. His hope: *"my hope is that
the AW fields that fire at 0159, will start printing earlier"*.

| his answer | the rule |
|---|---|
| 1A | the walk-back step is 48 bars = 240 s for every TF |
| 2B | every following lift-off sample (TF x 2.8 bars apart) until one is closer to 50, or r goes past the extremum |
| 3B | in towards/away, an e reversal's value is stored only when more extreme than the stored one (or none stored) |
| 4A | *"one e-sample **method** everywhere"*: the scenario-2 sample is ws{TF}r at the walk-back bar |
| 5A | an e reversal's value must be ex-20/80 to make the line AW in scenario 1 |
| 6B | in lift-off itself - every lift-off reader gets it, *"SRP rules"*; on for all at once, *"if they move, they move"* |
| gate | his 1109 5A gate stays (*"I see these as different things"*): r is NOT printing a new extreme on the cross bar (his 1B), and no reversal has stamped since r's extreme in lift-off's window |
| hold | none: the reversal prints on the sample's bar |

| where | what |
|---|---|
| jig.lift_off_e | the producer. jig.lift_off / lift_off_pivot take it as `e_path`; an e reversal's raw bar is stamp - (wob - 1) |
| v4_lift_e.py | its knobs (LIFT_E_ON 1, LIFT_E_STEP 48, LIFT_E_MIN_LESS 0.0, LIFT_E_RACE, LIFT_E_RACE_READ) and the e_path each v4 call passes |
| v4_ws_e.py | the ws{TF}e line's one home (config row, line cache, control numbers) |
| v4 readers wired | v4_fdm2, v4_fdm_reentry, v4_fast.revs, v4_lineage2, v4_l2_cadence, v4_l2_proxy, v4_lineage_trace, v4_saviour, v4_backstop. ws1..ws3 have no e line, so unchanged |
| caches keyed | v4_fast, v4_lineage2, v4_l2_cadence, v4_l2_proxy (in-process) and out/re_sigcache.py (disk) carry the e-path knobs |

## 11. The 1110 flip at 50

His spec: *"the AW/TO logic needs refining:"* / *"PER TRADE:"* / *"if a line has printed an extremum and is tagged as
away"* / *"if the line has returned past 50 (ie crossed to the counter target-side)"* / *"if the line returns to the
target-side of 50, the tag flips from away to toward"*, with his ws3 2026-08-25 example (*"at 1639, ws3 has crossed over
50 (away from target side)"* / *"at 1703, ws3 has crossed under 50 - it is tagged as towards"*). His note:
*"make sure the update doesn't impact the "all lines start with TO at the beginning of a trade""*.

| his answer | the rule |
|---|---|
| read | emerging ws{TF}r (FLIP50_READ). His example's crosses: over 50 at 16:37:50 emerging / 16:39:00 closed-prev; under 50 at 17:03:00 emerging / 17:06:00 closed-prev |
| which AW | scenario 1 and scenario 2 |
| an AW that starts on the far side of 50 | already counts: TO at r's first return to the target side |
| after the flip | the extremum is retired, TO until a newer one is stored |

| check, 1110 | result |
|---|---|
| FLIP50 0, in-process | md5 830d2d7d16fc177a706ff99f12a55c74, equal to the 1110 bank |
| FLIP50 1 (banked) | md5 5686002290c62c1c328612c049baedee |
| a separate bar-by-bar recompute: scalar reads, its own 50 walk | 760 bars, 0 mismatches: 240 AW->TO, 80 TO->AW, 120 scenario-2 bars, 120 trade opens, 200 random |
| trade-open bars reading AW, ws1..ws30 | 0 of 46,920, flip on and off; now an assert in run() |
| first web UI row of a trade reading AW, ws1..ws30 | 0 of 1,562 trades, flip on and off |
| AW 60 s after a trade's open | 11 line-trades, the same 11 with the flip off |
| his ws3 2026-08-25 | TO from 17:03:00; it was AW to the trade's close at 17:13:30 |
| web UI after the restart | TO/AW codes and counts: 0 cells differ from a fresh build. r-pred, sums, cross codes, side: 0 cells differ from before |

| ws1..ws30, whole tape | flip off | flip on |
|---|---|---|
| AW bars | 13,930,599 | 9,418,188 |
| bars AW -> TO | - | 4,532,595 |
| bars TO -> AW | - | 20,184 |

## 9. Not changed

- `fdm2-cad-mom-detector` and its four readers (the race's candidate picker, the cad walk's board test, the 50% test,
  fdm2-momo) still read the old detector.
- the xcross validator report keeps its own banked ws{TF}e at len 4 (`1107_sandbox_xcross/sandbox_knobs.py`).
- `fdm2-rline-enhance` - pinned, his to test.
