# the wsf walk — ingredients, recipe, honed skills

**THE SINGLE SOURCE OF TRUTH FOR THE WALK.** Joe 0827: *"we need to have the ingredients, recipe
and honed skills in a specific wsf walk documnent, so that you have a single source of truth"*.

## how to read this document

Joe 0827, the risk he named: *"this is risky: there's contradicting data in the transcript, as an
output of the tuning"* and *"if you can keep it clean and retain only the final per-skill decisions
then we should be ok, but I'll need you to make a sensible call on this"*.

| rule | what it means here |
|---|---|
| final decisions only | where a rule was revised, only the LAST version is stated. A superseded version is named in a footnote and never restated as active |
| Joe's words or nothing | every rule carries Joe's verbatim quote and the date. No quote means it is not his rule |
| my calls are labelled | anything of mine sits under **MINE, STATED**. It is never mixed into Joe's rules |
| unresolved goes to OPEN | where two of Joe's statements still conflict, section 5 holds it. Not resolved here |
| one fact, one home | this document holds the RULE — what fires. `docs/ws-finisher_spec.md` holds the PRODUCER — how the number is computed and the knob value. Neither restates the other |

**THE CALLS I MADE ON WHICH VERSION IS FINAL** are listed in section 6, so every one can be
overruled in a single pass.

---

# 1. the ingredients

Joe 0825 asked for the full list: *"list all of your model ingredients. for each ingredient, tell me
how you applied it and how it contributed to your verdict. no shortcuts, no lookahead."* That list
ran to 36. Section 1.5 carries every addition Joe has made since.

## 1.1 the three questions the walk asks at every bar

| # | the question | how it is answered | status |
|---|---|---|---|
| 1 | am I in trade | the pyramid slots, from `wsf_walk` | built |
| 2 | which way am I facing | the three-Mage dr — see 1.2 | built |
| 3 | what state am I in | wsf-momoc / wsf-momo-none / wsf-exhaust, the report footer | built |

Joe 0823 set the three. Question 1 had no mechanic when the list was written; the pyramid slots
answered it on 0825.

## 1.2 the three-Mage dr

| | |
|---|---|
| the lines | gcws30Mage, ws1Mage, ws2Mage |
| the fence | 80 / 20. Joe 0823: `100-{knob:20}` |
| dr +1 | all three at or above 80 |
| dr −1 | all three at or below 20 |
| anything else | no answer at that bar |
| the lookback | `DR_LOOKBACK_S` = 180 s = 36 bars at the 5 s grid, BACKWARD only |
| the producer | `jig.wsf_facing_dr` then `jig.wsf_dr_lookback` |

Joe 0823 on holds: *"no holds - the lines are either all outside the fence, or not at all"*.

**THE LATCH.** Joe 0826: *"the walk will retain the last known dr, ie dr +1 @ 01:58"*. The walk
holds the last dr it was given until a new one prints. The dtf-free delegation's own three-mage-lb
test is separate and is run live at delegation, unchanged.

## 1.3 the per-line columns the walk reads

One row per line, ws1r to ws12r, at the bar, in the direction dr names.

| # | column | what it holds |
|---|---|---|
| 4 | r value | ws{tf}r, 0 to 100 |
| 5 | heading | away / toward / flat, against momo-fence-r |
| 6 | r IB | the line is inside the 85/15 boundary |
| 7 | verdict | momo / curl / sideways / none. **The wsf verdict**, after the momentum-kill |
| 8 | curl_dr | the direction a curl ends, where the verdict is curl |
| 9 | wsf-curl-mode | the curl reading with gate 2 excluded. Joe 0824 |
| 10 | stalled | STALL_N 6 lattice samples with no new extreme |
| 11 | 50 gate | the tracking-weighted level |
| 12 | blocked by 50 | the level gate rejected the verdict |
| 13 | last-verdict | the verdict before the current one |
| 14 | last-verdict-dwell | seconds since the verdict changed |
| 15 | Mage value | ws{tf}Mage, 0 to 100 |
| 16 | lb-mage-oob | the Mage was out of bounds inside the 120 s tolerance |
| 17 | weak-mage | this line is the weak-mage-tf — see 1.4 |
| 18 | stoch now | the stoch reading entering r's window |
| 19 | stoch out | the reading LEAVING r's window at this line's next close |
| 20 | sat clock | bars the line has been saturated |
| 21 | sat left | bars of depth remaining |
| 22-24 | RSI, RSI lo, RSI hi | the stoch inputs |

**`stoch_out_extreme`, ingredient 19's use.** `stoch out` = 0 means r cannot fall at the next close;
`stoch out` = 100 means r cannot rise. Rounded to 6 places to clear float residue — not a knob.

## 1.4 weak-mage-tf

| | |
|---|---|
| the scan | ws2Mage upward to ws12Mage, in order |
| the answer | the FIRST Mage that was not out of bounds at any bar inside the lookback |
| the lookback | `WMT_LOOKBACK_S` = 120 s = 24 bars at the 5 s grid |
| the floor | `WMT_TF_LO` = 2. Joe 0821: *"reduce the range for weak-mage-tf"* |
| the ceiling | `WMT_TF_HI` = 12. Joe 0826: *"weak-mage-tf scan is now TF2 to TF12"* |
| no answer | every Mage was out of bounds inside the window. That is a RESULT, and rule C applies |

Joe 0817: *"the first Mage that prints an IB value, is the weak-mage-tf"*.

### one truth, Joe 0831

Joe 0831: *"move it to the jig so that we have a single truth"*.

Before the move the mechanic lived in two places that did not import from each other, and the two
had drifted. `optimus9/analysis/jig.py` carried `WMT_LOOKBACK_S` 120 s and `WMT_TFS` TF1..TF8 — the
0817 range. `build_wsf_bar_tf.py` carried its own `WMT_LOOKBACK_S` 120 s and `WMT_TF_LO` 2 /
`WMT_TF_HI` 12 — the 0826 range. Joe's 0826 range change had reached one file and not the other.

| | |
|---|---|
| where the knobs live now | `optimus9/analysis/jig.py`, the ws-FINISHER block. Nothing else declares them |
| the per-bar producer | `jig.weak_mage_tf` — one bar, returns `(weak_tf, detail)` |
| the every-bar producer | `jig.weak_mage_tf_series` — added 0831, returns `(oob, ago, tol, wmt)` over the full cache |
| who imports them | `build_wsf_bar_tf.py` and `build_ws_finisher.py`. Neither declares a knob of its own |
| `WMT_SAME_SIDE` | **FIXED at True**, Joe 0831: *"W3, fixed as True"*. It is no longer a knob and is not in any unique key |

**PROVEN, not asserted.** `wsf_bar_tf` was rebuilt through the jig producer and every one of the
**414,744 rows** compared against a snapshot taken before the move: 0 keys lost, 0 keys gained,
and **0 rows changed** on `wbt_weak_mage_tf`, `wbt_mage_oob`, `wbt_mage_ago_s` and
`wbt_mage_oob_tol`.

**THE 120-SECOND TOLERANCE IS WEAK-MAGE'S AND NOTHING ELSE.** Joe 0831 asked whether it belonged
to three-mage. It does not, and never has. Three-mage's dr lookback is `DR_LOOKBACK_S` = **180 s**
in `build_wsf_walk_events.py`, from Joe 0823: *"restrict the lookback to 3 minutes"*. Two knobs,
two values, two mechanics, no shared code path.

### the scan range is in ws_fin_weak_mage's unique key, Joe 0831

Joe 0831, W1: *"keep alongside"*. W2, on adding the range to the key: *"do it"*.

Making the jig the single truth pushes the 0826 range TF2..TF12 onto `build_ws_finisher.py`, whose
table `ws_fin_weak_mage` held 121 rows built at the 0817 range TF1..TF8 — the rows carrying the
four bars Joe read himself to settle the rule. The old key was
`(wfm_lookback_s, wfm_same_side, wfm_hi, wfm_lo, wfm_utc)`, which does not mention the range, so a
rebuild would have overwritten them.

| | |
|---|---|
| the key now | `(wfm_lookback_s, wfm_same_side, wfm_hi, wfm_lo, wfm_tf_lo, wfm_tf_hi, wfm_utc)` |
| the existing 121 rows | stamped `wfm_tf_lo` 1 / `wfm_tf_hi` 8 — what they were actually built at |
| the new 121 rows | `wfm_tf_lo` 2 / `wfm_tf_hi` 12 |
| the DELETE | pins the range, so a rebuild at one range cannot reach rows at another |
| the per-timeframe columns | `wfm_tf1..wfm_tf12` and `wfm_tf1_ago..wfm_tf12_ago` all exist, so both ranges fit the same table |

| range | rows | no weak-mage-tf | rule C fires |
|---|---|---|---|
| TF1 to TF8 | 121 | 30 | 12 |
| TF2 to TF12 | 121 | 23 | 12 |

**JOE'S FOUR 0817 BARS READ THE SAME ON BOTH RANGES.**

| utc | dr | TF1-8 | TF2-12 |
|---|---|---|---|
| 10:53:35 | +1 | TF8 | TF8 |
| 11:34:00 | −1 | TF2 | TF2 |
| 08:02:50 | +1 | TF4 | TF4 |
| 04:49:15 | +1 | None | None |

## 1.5 the additions Joe has made since the 36-item list

### the baton, Joe 0825

> *"the model flips a momo line to none so that a higher TF can organically hold the momo baton, if
> that higher TF is already in momo. if we don't set the line to none, then you lose some visibility
> of the baton holder's impact"*

wsf-exhaust is the baton DROPPED.

**THE CAVEAT, Joe 0825**: *"while an HTF(s) is/are in momo and travelling towards the fence's edge,
LTFs can flip back into a momo state. you currently have a proven way to handle this, and I don't
think it should change"*.

### the maxTF declaration, Joe 0819

> *"when ws8r stalls or crosses to oob, wsf-exhaustion is declared"*
> *"ws8r is the highest TF, so the wsf-exhaust signal is created when ws8r stalls or crosses into oob"*
> *"it needs to be carrying momentum before it"*

Read today through the verdict column, per Joe 0821: the maxTF line's verdict flips momo -> none.
**ws8 was the ceiling on 0819. The ceiling is 12 from Joe 0826.** Full entry in
`docs/ws-finisher_spec.md`, section *the maxTF declaration, Joe 0819*.

### which TF prints the ungated x-cross, Joe 0828

Joe's replacement process for choosing the forced x-cross timeframe, verbatim:

> *-if any TF prints a x-cross while an r line is outside of momo-fence-r*
> *--gate the cross, hold the signal*
> *--tag the highest TF that is outside of momo-fence-r*
> *--if ws{highest_TF}r - ws{highest_TF +1}r < 15 (ie highTF+1 is close to highTF, so has potential*
> *continue the momentum and exit the fence )*
> *---then ws{highest_TF +1}x will print the ungated cross*
> *--ELSE ws{highest_TF}x will print the ungated cross*
> *--if the the TF holding the gated x-cross (from row 1) == the TF designated to print the ungated*
> *cross, then the ungated cross is print the held x-cross*

**THE PROMOTE IS ONE STEP PER CROSS, AND THAT IS THE DESIGN. Joe 0829, verbatim:**

> *"when a higher line takes over, the walk continues. on the next x-cross, the test is repeated
> and potentially finds a new htf that has exited the fence"*

The climb up the timeframes is not a loop inside one bar. Each x-cross runs the test once, moves
the designated line at most one timeframe up, and the walk carries on; the next x-cross runs the
test again against whatever has exited the fence by then. The code already does this - `des` is
`h + 1` or `h`, never an iteration - so this records the intent, it does not change the mechanic.

**THE FENCE IS NOT A LEVER. Joe 0829, verbatim:**

> *"I've learnt the fence is not a lever - let's stick with 83/17"*

`MOMO_FENCE_R` stays at 17, so momo-fence-r stays 83 at the top and 17 at the bottom. Two other
values were built and measured against the 24 forced-flagged rows and against the 00:00-08:00 walk,
both landing alongside 83/17 under their own knob signatures:

| fence | of the 24 rows, unchanged | worst gap to Joe's estimate | of the 23 events to 08:00, kept |
|---|---|---|---|
| 83 / 17 | - | 47m40s | - |
| 80 / 20 | 18 of 24 | 17m25s | 21 of 23 |
| 70 / 30 | 7 of 24 | 15m00s | 12 of 23 |

Joe 0829 on 70/30: *"70/30 usn't the right move"*.

**JOE'S RULINGS ON THE READINGS, 0828:**

| the reading | Joe |
|---|---|
| the gap is ABSOLUTE, not signed | *"yes you're right. the gap is absolute"*. A signed test fires on every dr -1 bar, because the highest line outside the fence sits BELOW its neighbour |
| the H+1 line must be momentum-true | *"good catch - yes, the H+1 line needs momentum-true"*. This reverses my literal reading, which had no momentum test |
| the cross target is a knob | *"add this as a knob - we'll chose the better option later, when we sweep"*. `XCROSS_TARGET` = `r` (x crosses its own r) or `race` (Mage, b, boundary) |
| the gap is a knob | `HIGH_TF_GAP` = 15, Joe's first guess |

**MINE, STATED**: if the highest line outside the fence is the ceiling ws12 there is no ws13, so the
designated timeframe stays ws12. And when the designated timeframe is not among the bar's crossers,
the walk goes forward to that line's own x-cross at the same hold.

**VALIDATED BY JOE, 0828: 24 OF 24.** Run over every row in
`transfer/0804_wsf-exhaust_timestamps.csv` carrying `x-cross_forced_wsf-exhaust = yes`. Joe:
*"I'm glad you kept the dropped rows, because now they're firing perfectly. in fact, all 24 rows
are perfect"*.

**THE FIVE DROPPED ROWS ARE BACK IN.** Joe 0826 had retired 04:45, 13:21, 14:19, 19:26 and 21:26 -
*"those 5 unmatched timestamps are highlighting my inaccurate human-ness. drop the 5 from memory -
they will need different ingredients"*. His 0828 statement supersedes it: they fire correctly under
this process and the different ingredient is this one.

**NOT BUILT.** The process lives only in a scratch experiment reading banked columns. It is not in
`build_wsf_walk_events.py`, neither knob is in any knob signature, and nothing is banked.

### the x-cross forced wsf-exhaust, Joe 0825

> *"because ws8r is mid-board, and ws7r's verdict is recently none (ie has just left the fence), AND
> ws7r was crossed, ws8r is confirming that it cannot carry its momentum past the fence"*
> *"because the x-cross created the wsf-exhaust event, it will simultaeneously create a trade signal"*

| condition | Joe's words |
|---|---|
| a line P past the 85/15 fence reading `none` | *"past the fence with `none` state"* |
| a HIGHER line holding momentum INSIDE the fence | *"it needs to have a higher momentum=true TF (eg ws8) inside the fence while the crossed (lower, eg 7) line is outside the fence"* |
| P's own x crosses P's own r | measured against Joe's 19 labelled events — nearer on 17 of 19 |
| on fire | *"any open positions are closed and the first pyramid slot is opened"* |
| many lines past the fence | *"create a race condition"* |
| does it re-fire if r continues | *"no ... the mechanisms will need to re-start when dr is captured"* |
| it coexists with the weak-mage cross | *"both exist, side by side"* |

**THE 65/35 MID-BOARD FENCE IS DEFUNCT.** Joe 0825: *"I was wrong: it's not always mid-board, it
just needs to be inside the fence"*. `MID_FENCE_KNOB` = 35 is recorded and not consumed.

### big-hammer - the forced exhaust's own trade signal, Joe 0829

> *"if wsf-forced-exhaust fires, then the trade prints at the same time"*

The same rule Joe stated on 0825 and which never reached the code:

> *"because the x-cross created the wsf-exhaust event, it will simultaeneously create a trade
> signal"*

**JOE'S RULINGS, 0829, verbatim:**

- which line the trade rides: *"confirmed - the trade rides the designated line that created the
  wsf-forced-exhaust"* - not the weak-mage line. The two disagree on 38 of the day's 43 forced
  events.
- the route's name: *"call it big-hammer"*. `wes_route` takes a third value alongside `weak-mage`
  and `rule-c`.
- the cross target: *"use x crosses r for now. we have the race option prepared as a sweep - I
  asked for it to go in the knobs section earlier today/late last night"* - `XCROSS_TARGET` = 'r',
  the sweep is task #2.
- weak-mage-tf on a forced event: *"weak-mage is decoration only when a forced exhaust happens"* -
  still read and still banked as an ingredient, no longer selects the line.

**THE IN-FLIGHT GATE CONSEQUENCE, measured before the build.** A forced exhaust's flight window
collapses to zero, so events behind it are no longer suppressed. Across the full day that released
exactly ONE event, 11:54:05, and it fired into a full pool and opened nothing. Joe 0829:
*"is this really a problem, or do the 2 trade slots handle your concern?"* - the slots handle it.
The other 37 gated events are held by `maxtf` or `plain` exhausts, whose flights are unchanged.

**BUILT 0829** in `build_wsf_walk_events.py` (the signal block) and `report_wsf_bar.py` (the
x-cross footnote). Run 5 of the full day at the unchanged knob signature; run 4 kept beside it as
the before. 43 of 71 events route `big-hammer`, all at lag 0, all on the designated line, all with
`wes_target` = 'r'. 0 events lost, 1 added, 0 non-forced trade bars moved.

### heading, the extrema, and the two new columns, Joe 0829

> *"I've always thought that `toward` means the line is heading towards the oob, and `away` means
> that the line has gone as far as it can into oob, printed an extrema, and is now moving `away`
> from the extrema"*
> *"this is how it needs to be shaped - it provides rich data about the lines recent path"*

> *"knowing if it failed oob is important information; it tells us that the line does not have the
> same momentum power as a line that sprang from oob"*

> *"add the last 2 columns (`lowest r`, and `at`) to wsf-model-report. call them `extrema r` and
> `extrema dwell`"*

**WHAT IT REPLACED.** The old `heading` read the slope's sign and called any line outside
momo-fence-r `away`. Its own docstring said `MY RULE, fitted to Joe's read at 07:36:20`. At
10:40:25 it printed the exact inverse of Joe's definition on all twelve lines - away 8 / toward 4
where the definition gives toward 8 / away 4.

**JOE'S RULINGS, 0829, verbatim, one per concretion:**

| | ruling |
|---|---|
| C1 which fence is oob | *"momo-fence-r"* - 83 / 17, not the 85/15 boundary |
| C2 must a line have reached oob | *"no - it can be away if it heading away from an extrema. the two new report columns will fill the gaps"* |
| C3 what marks the extrema | *"using `stall` makes the most sense - it's an established mech that we can rely on"* |
| C4 when `away` ends | *"a line will lose away status when it is tagged as momentum-true (ie, it's travelled far enough start a new cycle)"* |
| C5 never-oob and falling | *"`heading` == `toward`. any decision that includes heading must have `verdict`'s input as well"* |
| C6 does `flat` survive | *"I don't think so. I've never seen it printed on a exhaust report, so it can't have a value-add to the mech"* |
| C7 which extreme | *"the true extreme"* - not the stall lattice's sampled one |
| C8 dwell in seconds | *"agreed"* |
| C9 how the move off is tested | *"r now vs r then"* |
| C10 must the stall be genuine | *"yes - a genuine `stalled` event. your scenario 'ws1 to ws8 all sit at 0 to 5 samples' would need to be reviewed on the next walk bar"* |

**C10 IS SUPERSEDED BY MOMO_STALL_DELAY, Joe 0829.** After seeing what the stall costs:

> *"now I see the downfall of using stall - 300 seconds consumes a lot of potential profit. if
> your reading `toward` while it is truly heading away, your recipe will be muddied"*
> *"what are our options?"*
> *"option 2: create a {knob:5} MOMO_STALL_DELAY (25 seconds)"*
> *"ELAPSE"*

`MOMO_STALL_DELAY` = 5 bars = 25 s at the 5 s grid. `away` prints once r has been off its extrema
for that many bars. The stall no longer gates it; `stalled` stays on the board as ingredient 9 and
stops deciding this column.

**ELAPSE, NOT RESET.** The clock runs from the turn and only a NEW extrema restarts it. A wobble
back onto the extrema does not un-happen a turn. I first built it the other way, on the
`MOMO_XWOB` 4 / `wflb_mfr_run` precedent, and that was wrong: that hold asks "is the line outside
the fence NOW", where a return genuinely cancels the state; this one asks "did the line turn",
where it does not.

Measured over 08-04, both dr, TF1 to TF12, on 3,064 turns:

| reading | printed away | never printed | median lag | worst lag |
|---|---|---|---|---|
| the stall | 1,940 | 1,124 - 36.7% | 0m00s | 14m25s |
| reset | 1,815 | 1,249 - 40.8% | 0m20s | 19m40s |
| **elapse** | **1,961** | **1,103 - 36.0%** | **0m20s** | **0m20s** |

The reset reading was worse than the stall it replaced on both counts. Elapse beats the stall on
both and has no tail.

**THE 36% FLOOR SURVIVES EVERY READING.** More than a third of turns still never print `away`,
because C4's momentum-true boundary resets the cycle before the hold completes. Neither the knob
value nor the counting rule touches that.

**`MOMO_STALL_DELAY` IS NOT IN ANY KNOB SIGNATURE.** `heading` is ingredient 4, home
`report_wsf_bar`, NOT BANKED, so nothing banked reads it. The day a test reads `heading`, it must
go into the walk's signature or the A/B overwrites itself. MINE, STATED.

**HEADING IS NOT IN THE RECIPE YET, AND THAT IS DELIBERATE. Joe 0829:**

> *"I think it's integral to the decision making, but we need to model it first. we can't model it
> until I've validated the full day, which is currently in-play"*

Task #12. None of the three declaring tests reads `heading`, and neither does the signal. Run 6
reproduces run 5 byte-identically across all 71 events, so the whole reshape changes no verdict, no
signal, no trade and no slot. It is built and idle, like the other seventeen banked-and-unread
ingredients.

**C5's SECOND CLAUSE IS A STANDING RULE, NOT A COLUMN RULE.** Any future test that reads `heading`
must read `verdict` alongside it. Nothing reads `heading` today.

**WHY C7 MATTERS.** The stall lattice samples every 22 to 29 bars on the high timeframes, so its
extreme is a lattice point and not the line's real one. At 10:40:25 the lattice put ws9's extreme
at 38.19 where the true low was 22.13, and ws11's lattice extreme predated its real low by 18
minutes because the lattice sampled past it.

**MINE, STATED, three:**
- a line with no momentum-true bar since `WIN_FROM` starts its cycle at `WIN_FROM`. That is where
  the data begins and there is nothing earlier to read.
- a line that is momentum-true AT the bar starts its cycle there, so `extrema r` is its own r and
  `extrema dwell` is 0 s. That is C4 applied to the current bar, not a special case.
- `r now` exactly equal to `extrema r` has not moved off it, so it reads `toward`. With `flat` gone
  under C6 there is nowhere else for a tie to land.

**BUILT 0829** in `report_wsf_bar.py` - the `heading()` producer and a new `extrema()` producer.
Report-only: ingredient 4 `heading` has home `report_wsf_bar` and is NOT BANKED, and the two new
columns join it there. No walk change, no knob signature change, no re-run.

### the dr is set by wsf9of12, Joe 0829

> *"start using wsf9of12 to primarily set the walk's dr. the three mage lb will be secondary (ie
> wsf9of12 will override it)"*
> *"three-mage was created specifically for dtf-free events. I let it bleed into wsf, which was
> useful at the time but now I see we are missing trades because three-mage is to restricive for
> wsf ops"*
> *"I can tell you that 08-04 starts the day on dr +1"*

**WHY IT MATTERS - THE WALK WAS BLIND ON TWO THIRDS OF THE DAY.** The walk skips a bar outright
when the dr reads 0: no test, no state update. The three-Mage dr read 0 on **11,213 of 17,280
bars**, so the walk read 6,067 bars, 35.1% of 08-04.

Worse, `prev_top` and `was_on` only advance on a bar the walk reads. The maxTF test compares
ws12's verdict against the last bar the walk read, not the bar before. **8 of the 71 events were
declared across a skipped stretch** - the worst spanning 5h01m20s, during which ws12 changed
verdict 24 times and flipped from momentum to none on ten separate occasions. Joe 0829: *"this is
very concerning. how did you find the wsf-exhaust moments if your ignoring so many bars?"*

**JOE'S RULINGS, 0829, verbatim:**

| | ruling |
|---|---|
| G1 what happens between markers | *"the dr is set and latched by wsf9of12. between markers, nothing changes to dr"* |
| G2 the dr 0 bars | *"G1 answers this"* |
| G3a before the first marker | *"use the last marker from 08-03"* - there is no 08-03 in any table, so `DR_SEED` +1 stands in its place, on his word: *"08-04 starts the day on dr +1"*. It agrees with the first marker, 00:08:20 at +1 |
| G3b is three-Mage retired | *"not removed entirely. it won't show any activity before we integrate wsf with dtf"* |
| G3c how long the latch holds | *"'forever' is too dramatic. 'until the next wsf9of12' is more precise"* |
| G3d DR_LOOKBACK_S and MAGE_KNOB | *"not dead - dormant until a later time"* |
| G4 the signature change | *"I doubt it will make a considerable change - if anything, we'll see more rows breaking current runs of monotonic same-sided dr rows"* - confirmed: 121 markers, 27 side changes. The new rows come from bars the walk could not see, not from a flapping dr |

**THE VARIANT PIN IS MINE, STATED.** `ws_fin_9of12` stores 4 knob variants for the day.
`HO_RULE='median'` and `LINE_HCAP='ws1b:1'` is the pair `report_wsf_bar.py` already pins - the walk
and the report must not read different markers.

**THE RESULT, three-Mage against wsf9of12, both full-day, unchanged tests:**

| | three-Mage dr | wsf9of12 dr |
|---|---|---|
| bars the walk read | 6,067 | 17,280 |
| events banked | 71 | 210 |
| declared by forced | 43 | 141 |
| declared by maxtf | 17 | 31 |
| declared by plain | 9 | 32 |
| dr +1 | 48 | 116 |
| dr -1 | **23** | **94** |
| pool actions - a slot opened | 20 | 49 |

**BOTH MISSES JOE FOUND BY EYE ARE NOW DECLARED.** *"~03:20 dr -1 is missing"* - the new walk fires
03:25:45, 03:30:20 and 03:38:30. The ~10:38 held cross that was stranded when the walk stopped
seeing dr -1 bars now fires at 10:44:50, the bar ws6 actually crossed.

**AGAINST JOE'S OWN VERDICTS ON THE OLD WALK:** 12 of 14 `valid` kept, 6 of 7 held-for-dtf kept,
2 of 2 `fail` kept. The two `valid` events lost are 01:13:35 and 03:43:15, both on the list of 8
declared across a skipped stretch. 03:43:15 did not vanish - ws12 had already gone to `none` at
03:38:30 on the dr -1 board, and the new walk declares at that bar instead, 4m45s earlier.

**forced IS NO LONGER ALWAYS THE SOLE TEST.** Under three-Mage it never combined; under wsf9of12
two events do - 07:25:10 `plain,forced` and 18:33:15 `maxtf,forced`. Both route big-hammer, since
the code branches on `'forced' in tests`. I told Joe the opposite when he ruled C1 on big-hammer,
and his ruling still applies cleanly to both.

**BUILT 0829** in `build_wsf_walk_events.py`. The signature now ends `_dr9s+1_hrmedian_lhws1b:1`,
so every earlier run stands untouched under its own signature.

### the trade slots, Joe 0825

> *"1. allows pyramiding, max 2 trades. 2. if both trade slots are occupied, the walk will take no
> action/stay dormant until an opposing (three-mage or wsf9of12) dr prints. keep it causal"*
> *"all open trades (1 or 2) are closed by the next opposing dr trade"*
> *"did the model verdict a short signal + x-cross at 01:34:05? that's the only thing that should
> close trades"*

### the ladder ceiling, Joe 0826

> *"wsf is limited to TF12. 13 to 27 belongs to dtf, which is not our current task"*

### the dtf-free assumption, Joe 0826

> *"for the duration of our wsf modelling, assume that dtf-free == true"*

### the 0825 board lessons

| lesson | Joe's words |
|---|---|
| depth | `sat left` says how long before r must move. Refusing to call depth is a cost |
| blast radius | *"each r line has a small 'blast radius'"* — a line reaches its neighbours on the ladder, not across it |
| mid-board | *"mid-board is the space where momentum is the lowest"* |
| limits | a reading of 100.00 or 0.00 is a turning point, not a strength reading |
| the HTF floor | *"the HTF r lines are all low on the board while verdict is none, after verdict being momo ... r has dropped to the ~floor (momo), and has nowhere to go (none)"* |
| the LTF tangent | *"the LTFs (1,2,3) will often tangent away from pxs, when in an ongoing leg"* |
| the matryoshka | ws1-ws4 away with ws5-ws8 still toward is not the same setup as the same count spread differently |

---

# 2. the recipe

The order the walk applies the ingredients at a bar. Every test reads that bar or earlier.

```
    1  DIRECTION      the three-Mage dr, latched. No dr and no latch -> no verdict at this bar.

    2  THE BOARD      read ws1r to ws12r at that dr: verdict, r value, fence position.

    3  THE EXHAUST    a  the maxTF declaration - ws12r was carrying momentum and its verdict
                         flips to none.  Nothing below ws12 is read.
                      b  the plain wsf-exhaust - no line ws1 to ws12 reads momo or curl.
                      c  the x-cross forced exhaust - conditions in 1.5.
                      Any one of the three declares wsf-exhaust. LATCH 1 SET.

    4  THE LINE       weak-mage-tf, scanned ws2Mage upward to ws12Mage, READ AT THE EXHAUST BAR.
                      an answer  -> watch ws{weak-mage-tf}x
                      no answer  -> rule C: watch ws2x
                      THE TIMEFRAME IS FIXED HERE and is NOT re-read on the walk forward.
                      Joe 0828: "reads weak-mage-tf at the exhaust bar and watches that line
                      forward -- this is the correct option"

    5  THE CROSS      walk forward. The trade signal fires when the watched x crosses its target.
                      The target is the race: Mage, b or boundary, first to cross wins.
                      dr +1 -> x crosses UNDER.   dr -1 -> x crosses OVER.
                      XCROSS_XWOB = 5 bars = 20 s hold before it counts.  LATCH 2 SET.

    5b THE GATE       an exhaust that has fired is walking forward for its own cross. Anything
                      that fires strictly between the exhaust bar and its cross bar is SUPPRESSED -
                      no event row, no ingredients, no pool move.
                      A FORCED EXHAUST IS NOT GATED. Joe 0828: "gate any events that fire between
                      an exhaust event, and the x-cross event. if it's a forced-exhaust, then
                      there is no gate applied".

    6  THE SLOT       the trade signal opens a pyramid slot. Max 2.
                      Both slots occupied -> dormant until an opposing dr prints.
                      Open trades close only on the FULL opposing chain: an opposing wsf-exhaust
                      walked forward to its own x-cross.

    7  THE STATE      after a trade fires the state is wsf-momo-none. wsf-momoc must be
                      re-acquired before the next cycle.
```

**THE DUAL LATCH, Joe 0819**: *"'wsf-exhaust' and 'trade signal' are 2 parts of a dual latch. trade
signal cannot fire unless wsf-exhaust has fired"*.

**RULE C, Joe 0817 as corrected 0826**: *"if weak-mage-tf == None and domTF state is FREE, fire a
trade signal on the next ws2x-cross"*.

**WHICH LINE THE CROSS IS WATCHED ON, Joe 0821**: *"you should be looking for the cross in
weak-make-tf, not the 'highest TF carrying momentum' TF"*.

**WHEN THAT LINE IS PICKED, Joe 0828**: *"reads weak-mage-tf at the exhaust bar and watches that
line forward -- this is the correct option"*. The timeframe is fixed at the exhaust bar. Reading it
again at each forward bar named ws2x at 00:25:15 where the fixed reading named ws12x at 00:15:10,
from the same data - that was `report_wsf_bar.py`, corrected 0828.

---

# 3. the honed skills

A skill is listed here only where a signal it produced was confirmed. The source is
`domtf_wsf_report` — Joe 0826: *"will show you the sanctioned wsf-exhaust events"* — which holds
27 distinct wsf-exhaust events on 08-04.

| skill | sanctioned events | Joe's confirming words |
|---|---|---|
| the maxTF declaration | 4 | *"when ws8r stalls or crosses to oob, wsf-exhaustion is declared"* |
| the r-line fence exit | 6 | *"IF a momentum-true r line crosses into oob or stalls THEN it's momentum = false (or none)"* |
| the x-cross | 17 | *"'x X [MAge,b,boundary]' (race condition) is integral to the spec"* |
| weak-mage-tf | named on 25 of 27 | *"the first Mage that prints an IB value, is the weak-mage-tf"* |
| x-cross direction | all 27 | *"x-cross direction: you've nailed it"* |
| the three-Mage dr | all 27 | *"every timestamp I'm passing to you now was orginally validated by the now-missing mech"* |

**HOW THE 27 WERE DERIVED, and what that limits them to.** `build_wsf_exhaust_bar.py` took Joe's 37
hand-timed estimates and searched an 8-minute window before each one for a qualifying mechanic.
They are Joe's times SNAPPED TO A BAR, not events a walk found on its own.

**THE CSV IS RETIRED AS A TRUTH SET. Joe 0827, verbatim:** *"delete the csv from memory. I've chosen
08-04 for its array of differing scenarios, so we'll continue with the same playing field"*.

`transfer/0804_wsf-exhaust_timestamps.csv` is no longer read to score, select between rule variants,
or steer a walk. The file is untouched on disk; what is retired is its use. The 27 rows above stay
in this section as the RECORD of what has been confirmed - they are not a target to hit.

**CORRECTNESS IS JOE'S CALL, NOT A CALCULATION HERE. Joe 0827, verbatim:** *"it might seem
measurable, but without MAE and MFE (which I'm withholding intentionally) you can't make a call on
correctness. delegate the measuring to me while we train the model"*. Nothing in this document or in
the tables states whether an event was right. The tables record what fired and what was read; Joe
supplies the verdict.

## the confirmed events, maxTF 12

Joe's confirmations against the current walk. `wee_confirmed` and `wee_xc_confirmed` are his columns
on `wsf_exhaust_event`; this is what they hold.

| bar | dr | declared by | x-cross | line | Joe's words |
|---|---|---|---|---|---|
| 00:02:30 | +1 | maxtf, plain | 00:15:10 | ws12 | *"bank your 00:02:30 wsf-exhaust as confirmed. x-cross is also confirmed"* |
| 00:58:25 | −1 | forced | 01:02:35 | ws3 | *"bank your 00:58:25 wsf-exhaust as confirmed. x-cross is also confirmed"* |
| 01:13:35 | −1 | maxtf, plain | 01:15:25 | ws4 | *"01:13:35 is confirmed. bank your validation"* |

These are the FIRST events confirmed at maxTF 12 and they are the only standing evidence. The 27
sanctioned events above were built at maxTF 8 and Joe ruled them void 0827.

## Joe's in-conversation confirmations

| what he confirmed | his words, verbatim |
|---|---|
| x-cross direction | *"x-cross direction: you've nailed it"* |
| 00:13:00 verdict, dr +1 SHORT | *"your decision is correct: dr +1 = SHORT trade signal"* |
| 00:14:50 verdict | *"I agree"*, with his state override to wsf-momo-none |
| 00:52:30 wsf-exhaust | *"your verdict is correct - good work"* |
| 00:52:30 hold and walk | *"your hold and walk verdict was strongly validated"* |
| 00:53:15 wsf-exhaust | *"you're correct."* |
| 01:00:15 x-cross trade time | *"01:00:15 is a good time to place a trade"* |
| 01:02:35 x-cross trade signal | *"that's a well placed trade"* |
| 01:34:05 wake | *"that's better. now that you have your wake @ 01:34:05"* |
| 01:40:55 wsf-momoc | *"your state is correctly set at wsf-momoc at 01:40:55"* |
| 01:59:20 ws7x cross | *"we'll keep the 01:59:20 cross because ws7r was outside of the fence at the time of the cross"* |
| 02:18:15 with no dtf direction | *"this is by design, and it fits perfectly"* |
| 02:48:15 wsf-exhaust | *"02:48 is perfect"* |
| 03:43:30 and 03:50:20 verdicts | *"both correct"* |
| 03:45:30 stall reading | *"03:45:30 is a well placed trade signal"* |
| 03:53 re-creation | *"good work"* |

---

# 4. MINE, STATED

Decisions in the walk that are mine, not Joe's. Each is here so it can be overruled.

| # | the decision | why |
|---|---|---|
| M1 | ONE POOL of 2 slots, each armed or open, rather than 2 armed plus 2 open | Joe's guess was 2 and 2. With one open and two armed, both armed can convert to three open, against *"max 2 trades"*. One pool cannot overfill |
| M2 | an opposing dr trade CLEARS armed slots as well as closing open ones | an armed setup faces a direction that has just been contradicted |
| M3 | arming on the RISING EDGE of a wsf-exhaust stretch | arming on every bar filled both slots 5 s apart from one event |
| M4 | the x-cross race tie-break is the LOWEST timeframe | Joe set the race, not the tie |
| M5 | the watched x on the forced exhaust is the CROSSED line's own x | Joe guessed the confirmer's x. His own 19 labelled events put the crossed line's x nearer on 17 of 19, exact at 10:57:00 |
| M6 | the maxTF declaration sits BESIDE the plain all-lines test, not instead of it | both were live in Joe's 0819 flow. **Not confirmed by Joe** |

---

# 5. OPEN — Joe's ruling needed

| # | the question | why it is open |
|---|---|---|
| O1 | does the x-cross forced exhaust need its confirmer to have finished its own trip | Joe 0825 requires a higher momentum line inside the fence to PROVE exhaustion. Joe 0826 says ws12 carrying EXTENDS the walk. Both from the same board |
| O2 | the stall-TF ratchet | Joe 0819: *"stall TF values can only increase (eg a ws6r stall event cannot happen after a ws7r stall)"*. Never built, never withdrawn |
| O3 | the latch reset | Joe 0819: *"latch 1 and 2 reset on a trade fire, or when all ws{current-max-tf-with-momentum} lines are IB"*. Never built |
| O4 | the one-shot re-arm on the forced exhaust | re-arming on any live three-Mage print is loose. Joe's restart wording is *"keep walking until dr"* |
| O5 | the fresh board after a trade signal | Joe 0826 asked for the test. Three settings measured, none chosen |
| O6 | wsf-momoc re-acquisition | Joe 0820 named the flow; five questions on it are open in the spec |
| O7 | the ELIF last mile | task #4, deferred by Joe |
| O8 | the 4th table - events the walk fired or missed because an ingredient is not built | Joe asked what it would be for. Its correctness column is HIS, not mine - MAE and MFE are withheld. Not built |
| O9 | pyramids - two trades firing together | Joe 0828: *"there is a deeper spec needed to handle 2 trades that fire together; if we place 2 standard sized trades together, we'll create unwanted slippage"*. Task #7 carries his verbatim text and the trace. Nothing in the walk or the tables carries trade size |

---

# 6. banking rules for the walk's tables, Joe 0827

Every place two of Joe's statements exist and this document states one of them.

**NOTHING IS DELETED.** Joe, verbatim: *"no deletes - here's the reason why: if we add a new
ingredient to support a decision that overrides an existing verdict, there is always a possibility
that the new ingredient is malformed. if we have a history of its usage, we can 1) easily compare
the facts needed to repair (or enhance) that ingredient and 2) be sure that we have not broken an
earlier confirmed wsf-exhaust event"*.

Every run of `build_wsf_walk_events.py` appends under a new `wee_run` number at the same knob
signature. The children hang off the parent by foreign key, so a run's ingredient usage and its
signals stay attached to that run.

**EVERY READER PINS THE SIGNATURE.** `wee_run` restarts at 1 for each knob signature, so
`MAX(wee_run)` on its own picks the highest run number across ALL signatures — a different walk.
Any query that means "the latest run" must carry `wee_knobs = SIG` in both the outer filter and
the sub-select. `report_wsf_bar.py` imports `SIG` from `build_wsf_walk_events.py` rather than
restating it: the walk owns the signature, the report joins to it.

**THE TABLES ARE RELATIONAL.** Joe 0827: *"the tables should be relational, joined by FKs"*.
`wsf_event_ingredient` and `wsf_event_signal` carry only `wei_event_pk` / `wes_event_pk`, foreign
keys to `wsf_exhaust_event.wee_pk`. The bar, the dr and the knobs live on the parent alone.

**THE FLAT FIRST CUT IS KEPT.** The three tables built before the FK change were RENAMED to
`wsf_exhaust_event_v0`, `wsf_event_ingredient_v0` and `wsf_event_signal_v0`, not dropped. 150 events
and 6,600 ingredient rows still stand there.

---

# 7. THE CALLS I MADE ON WHICH VERSION IS FINAL

| what | earlier version | version stated here | why |
|---|---|---|---|
| rule C | *"fire a trade signal"* at the exhaust bar, 0817 | *"fire a trade signal on the next ws2x-cross"*, 0826 | Joe corrected it explicitly on 0826 |
| the weak-mage scan range | TF1 to TF8, then TF2 to TF8 | TF2 to TF12 | Joe 0821 then Joe 0826 |
| the ladder ceiling | TF1 to TF8 | TF1 to TF12 | Joe 0826 |
| the forced exhaust's fence test | *"ws8r is mid-board"* and the 65/35 fence | *"it just needs to be inside the fence"* | Joe 0825: *"I was wrong"* |
| the watched x | Joe's guess, the confirmer's x | the crossed line's own x | measured against Joe's 19 events, 17 of 19 |
| the single confirmer | Joe proposed highest-exited minus 1 | highest-exited plus 1 | Joe's set scored 0 of 19 against 15 of 19 |
| wsf-exhaust's definition | *"stall OR reverse OR cross into oob"*, 0817 | the momentum-kill in the verdict column, 0821 | Joe 0821: *"delete the 0817 note"* |
| the per-line vs machine state | *"states will be assigned per r line"*, 0818 | momentum is per line; wsf-momoc and wsf-exhaust are machine states over all lines | Joe 0819: *"the product of calculations on all of the lines"* |
