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
| next | the SEPARATE lift-off update, his *"we'll apply the lift-off updates next"* - section 8 |

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
| 10 | which r lines | 10A: ws4r to ws30r, the lines that have an e line |
| - | the 12 reads I took from precedent | none corrected |
| - | the line cache | *"update the cache"* - the e lines are cached (section 6) |

## 3. The mech, in firing order

| step | what happens |
|---|---|
| ws{TF}e | BB%B len 3, mult 0.5, src close, EMERGING, ws4..ws30, built from ONE row of `mech_line_config` (his indicator config spec, `docs/mech_line_config_spec.md`): mechanic `towards-away`, role `e`, 240..1800 s every 60 s, version 1. Read from the line cache |
| the pseudo trade | sweep-pivots' ws2Mage legs; each leg's pivot is its most extreme tape close (low for a leg opened by a LOW cross). The LAST pivot of each same-side run is the pseudo rev-trade signal. A trade opens on one signal and runs to the next. Its target-side is the side of the run it closes on: a trade opened at a HIGH run's last pivot has a LOW target-side. LOOKAHEAD on purpose: a pivot is fixed only when its leg closes |
| auto-towards | at the trade's open every line is TO. A line stays TO while it has not reached ex-20/80 on the target-side this trade. Reached once, it stays reached for the trade |
| scenario 1 | the line has reached ex-20/80. Every target-side lift-off reversal on its emerging r stores its pivot's value at the reversal's stamp (lift bar + 7 bars = 35 s). Only an extremum whose value is ex-20/80 votes. The latest voting extremum makes the line AW from its stamp; the line is TO from the first bar its emerging r goes past that extremum toward the target-side |
| e-samples | ws{TF}e crosses its race lines: UNDER 85 / ws{TF}Mage / ws{TF}r on a HIGH target-side, OVER 15 / Mage / r on a LOW one. No hold. The first race line crossed wins; the race re-opens when e crosses back over it. The sample is ws{TF}r's emerging value on the cross bar |
| scenario 2 | the line has not reached ex-20/80. On the bar of a new sample: if it and the sample before it (this trade) are both in-fence and within 2.0 r-points, AND more than 1 of the 5 lines under it read AW in scenario 1, the more target-side sample is stored and the line is AW. It is TO from the first bar its emerging r goes past that extremum |

## 4. KNOBS — every one, including those not called out as knobs

### 4a. Banked in `ta_knobs.py` (env `W_TA_<NAME>`, off-bank refuses)

| knob | value | units | what it does | from |
|---|---|---|---|---|
| TF_LO | 4 | TF | the lowest r line with a state | his 10A |
| TF_HI | 30 | TF | the highest | his 10A |
| E_MECH | towards-away | config row | the ws{TF}e row's mechanic in `mech_line_config` | MINE (the name), his words |
| E_VERSION | 1 | config version | the ws{TF}e row's version: len 3 | *"leave it on len3"* |
| RACE | boundary, Mage, r | race lines | what ws{TF}e races to; the order a tie is reported in | his race:{boundary,Mage,r} |
| RACE_READ | closed_prev | read | how the r and Mage it races to are read | the standard race (v4_fdm2.x_race); my read, not corrected |
| UNDER | 5 | TFs | how many TFs under the line scenario 2 reads | his {knob:5} |
| UNDER_GT | 1 | lines | scenario 2 needs MORE than this many of them AW | his ">1" |
| PAIR_PTS | 2.0 | r-points | how close the two samples must be | his 7A |
| SUPERSEDE | strict | rule | past the extremum ('strict') or at-or-past ('inclusive') ends AW | MINE |
| PIVOT_LINE | ws2Mage | line | the Mage whose sweep-pivots pivots make the pseudo trades | *"use ws2Mage pivots"* |

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

## 5. Checks, 1109

| check | result |
|---|---|
| e lines: cached arrays against a fresh in-memory build | max diff 0, NaN positions equal, 27 of 27 |
| e lines: ws30Mage control row built beside them | equal to the cached ws30Mage |
| line cache: existing files changed by the e write | 0 (27 new files) |
| ex-20/80 reader, vectorised, against v4_fdm2.ex2080_line | 2,400 sampled bars, 0 differ |
| the mech against a separate per-bar recompute (scalar reads, its own race and pair code) | 320 bars (120 at scenario-2 AW starts/ends), 0 mismatches |
| bank control: md5 over every state array, before and after the knobs were wired | identical: 1030342900d8992240c7c824a6679ced |
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
| server | `docs/octo-freedom/1022_v4/out/rpred_ui.py [port]`, stdlib ThreadingHTTPServer on 127.0.0.1, default port 8788. The page is inline (the seam_stream.py pattern) |
| start-up | ~50 s: the r-pred matrix (~2 s) plus `towards_away.build()` with the e lines from the cache. Everything is held in memory; nothing is cached to disk by the UI, so a line change can never be served stale |
| a row | one ws1 bar, timed at its open (UTC) |
| the read bar | the row time + 60 s (12 bars): where closed-prev first shows that ws1 bar. r-pred, TO/AW and (inf)/(exf) are all read there |
| columns | ws1 time, gcws15, gcws30, ws1..ws12 (his wsf), then the ws13-ws20 and ws21-ws30 r-pred sums |
| r-pred cell | predict_breach(r, m, Mage), emerging: hi 85, lo 15, fence 70/30, tol 0. -1 red, +1 green; a missing input reads 0 (his "keep 0") |
| sum cells | red < 0, green > 0, orange at 0 |
| TO / AW | bold, 10 px, under the number, ws4..ws12 only (his 10A). gcws15, gcws30, ws1..ws3 print none |
| (inf) / (exf) | ex-20/80 on the target-side at the read bar, by the banked reader the mech uses (closed-prev, or the emerging extreme of the 60 s to that bar) |
| sum labels | `TO:x  AW:x` at 10 px, the count of its lines reading TO and AW |
| time cell | 20% red for a LOW target-side, 20% green for HIGH; no colour before the first trade |
| row payload | 35 int8 per row: 14 r-pred, 2 sums, 14 TO/AW codes (0 none, 1 TO(inf), 2 AW(inf), 3 TO(exf), 4 AW(exf)), 4 counts (-1 = no trade), 1 target-side |
| the browser cache | 720-row blocks (12 h), 3 blocks ahead in the scroll direction and 1 behind, 60 blocks held, least recently used dropped, a calendar day's blocks fetched on hover |
| row height | 38 px |
| control | CONTROL_FLAGGED 257,295 r-pred cells at -1/+1, printed MATCH at every start |
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

## 9. Not changed

- `fdm2-cad-mom-detector` and its four readers (the race's candidate picker, the cad walk's board test, the 50% test,
  fdm2-momo) still read the old detector.
- the xcross validator report keeps its own banked ws{TF}e at len 4 (`1107_sandbox_xcross/sandbox_knobs.py`).
- `fdm2-rline-enhance` - pinned, his to test.
