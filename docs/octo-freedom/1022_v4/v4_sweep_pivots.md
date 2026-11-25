# `sweep-pivots` — BANKED 1024

Joe named it. The swing scale a sweep measures MFE against, with **no pivot pct to set**.

Joe 1024: *"let's make it a machine and lock down the spec. if there's knobs, make sure they're
visible"*, and before that: *"sweep-pivots feels like an honest improvement"*.

---

**GOAL** (his 1125): *"sweep-pivots' role is to detect extrema and label them as pivots"*.

## 1. Why it exists

Joe 1024: *"getting swings correctly dialed is the most load-bearing mech in a sweep - if we can't
rely on them then we produce false results"*.

Then: *"I'm going to hand it back to you and find a way to dynamically set it. fixing a pct has
never completley served us - now I feel like we have a way to automate it"*.

The banked exit rule measures MFE from the entry to *"the next favourable 2% pivot"*. That 2% is a
fixed pct, and one fixed pct can only ever match one swing size. `sweep-pivots` replaces it with a
boundary the lines themselves define.

---

## 2. The mech, his words

Joe 1024, across four messages:

> I'd be looking more at Mages crossing to ib across various TFs, maybe (ws3Mage, ws5Mage,
> ws10Mage, ws15, ws20, ws30). we can reliably predict that a mage crossing from oob to ib will
> always land on the MFE side.

> given that a sweep allows full lookahead, you can collect the swings and pivots from all of the
> noted Mages. when you have an event to test, see how many per-Mage-pivots are closest to the
> event. if you have multiple TF's Mages pivots that align with the event, then your likely at a
> larger swing and can use the higher TFs swing to more accurately gauge the MFE (instead of using
> a small swings MFE)

> instead of scoring after the event, why not pre-build the pivot data for all of the in-use Mages,
> then pick the pivot from the index based on same direction and closeness to the prior pivot

> start at the lowest TF and scan upwards. you should find a series of TFs printing the near-same
> distance from their own pivot to the event. the TF swing/pivot to pick should be the highest TF
> printing the lowest pct (between pivot and event)

And the two corrections that shaped it:

> it should be the prior pivot, if we're following my "opens on the MFE side" view

> not identical - the mages will all cross to ib in their own order, so the pct to event will always
> be near, not identical

---

## 3. The mech, as built

| the step | the mechanism |
|---|---|
| the index | every in-use Mage's oob -> ib crosses, bar-sorted, cached. `index()` |
| a leg | a cross, then the next OPPOSITE-side cross of the SAME Mage. Both ends mechanism-defined. `legs()` |
| a TF's pivot | that leg's extremum on the walk's side — the LOW of a leg a LOW cross opened |
| a TF's pct | the favourable-signed move from its pivot to the event. **From the EXTREMUM**, his *"extremum - that was a good call"* |
| the pick | the lowest \|pct\| across the TFs; on a tie within `SP_BAND`, the HIGHEST TF of that group |
| the swing | the picked TF's own leg, and the MFE measured inside it |

**The side mapping inverts.** A LONG wants price UP, so its leg is one opened by a LOW cross:
`side = -1`. `swing(bar, side)` has favourable = `-side`, so a caller passes `side = -d`.

**Lookahead is allowed here and only here.** Joe: *"given that a sweep allows full lookahead"*. A
leg is closed by a cross AFTER the event, so `scale` and `swing` read the future on purpose. They
are SCORING. No mech step may call them, and `v4_test_script`'s stage guard asserts that
separately — every mech function's signature is checked for a price-derived parameter at import.

---

## 4. The knobs — all six, and every value is a measurement

They live in `v4_knobs.py`, which refuses an off-ruled run unless `W_V4_EXPERIMENT=1`.
`v4_sweep_pivots.knobs()` prints the set any run used. The four-read pivots' three knobs live in
`v4_sweep_pivots.py` itself - §10b.

| the knob | value | what set it |
|---|---|---|
| `SP_PICK` | `lowest_pct` | his 1024 rule, verbatim above |
| `SP_BAND` | 0.0 pct points | his near-same band. 53.6% of 37,178 consecutive-pct gaps are **exactly 0** — TFs sharing a leg extremum — and p10 through p50 are all 0.0000 while p75 is 0.3705. So 0.0 already captures the clustering |
| `SP_CONTAIN` | 0, OFF | the event-inside-the-leg filter |
| `SP_XWOB` | 18 bars = 90 s | his *"introduce a wob 18 and retest"*. The only wob he named for this mech |
| `SP_ALIGN_S` | 300 s | his *"agreed on 300s"*. **UNREAD** under `SP_PICK` `lowest_pct` — it gates only the `window` arm, kept as the comparison |
| `SP_TFS` | `wide` | **THE ONE ITEM AWAITING HIS WORD** — see §7 |

---

## 5. What was measured, and what it says

### His claim holds

> we can reliably predict that a mage crossing from oob to ib will always land on the MFE side

Anchored on the PRIOR pivot — his correction — **82% to 93%** of Mage oob->ib crosses open on the
favourable side of the move's start, across every TF and every pivot pct from 0.5 to 2.2.

MEASURED FORWARD IT HAD READ 43% TO 59%, and that was my error, not his claim: the *next* pivot is
where the move ENDS, so measuring to it scored each cross against its own destination.

### The ladder is real, which is why there is no pct

Each Mage's own consecutive opposite-side crosses bracket a leg. The medians over the 94 days are
monotone with no inversions:

| the Mage | legs | median leg % | the px_smooth pct whose median leg matches |
|---|---|---|---|
| ws1Mage | 2,937 | 0.375% | 0.3% |
| ws2Mage | 1,564 | 0.606% | 0.3% |
| ws3Mage | 1,064 | 0.751% | 0.4% |
| ws5Mage | 649 | 1.007% | 0.6% |
| ws10Mage | 348 | 1.477% | 0.8% |
| ws15Mage | 228 | 1.831% | 1.0% |
| ws20Mage | 182 | 2.198% | 1.3% |
| ws30Mage | 116 | 2.633% | 1.5% |

The pct equivalents span 0.3% to 1.5%, so one fixed pct can match exactly one rung. That is
*"fixing a pct has never completley served us"*, in numbers.

### The event lands a QUARTER into its swing, whatever the size

This is the finding that locked the mech, from 5,323 events:

| the leg MFE band | events | median \|pct\| off the pivot | median share of the leg behind |
|---|---|---|---|
| 0.0 to 0.5% | 297 | 0.071% | 0.176 |
| 0.5 to 1.0% | 1,461 | 0.148% | 0.221 |
| 1.0 to 2.0% | 1,804 | 0.416% | 0.286 |
| 2.0 to 4.0% | 1,252 | 0.791% | 0.295 |
| 4.0% and up | 509 | 1.284% | 0.201 |

The distance off the pivot rises 18× across those bands while the share holds between 0.176 and
0.295. So the population median of 0.327% is not an error — it is a quarter of the median 1.397%
leg. **A bigger swing comes with a proportionally bigger pct, same quarter.**

| the sign read | of 5,323 events |
|---|---|
| the event fires BEFORE its pivot | 5,177 = 97.3% |
| the event is already FAVOURABLE of the pivot | 4,446 = 83.5% |
| exactly on the pivot | 54 = 1.0% |

**This is why his cluster-REACH rule was not built.** Reaching up a rung buys a bigger leg and a
proportionally bigger pct — the trade the band table appeared to show is an *identity*, not a cost,
so there is nothing for a reach value to optimise.

---

## 6. Three things measured and REJECTED, recorded so they are not re-proposed

| the idea | why it is out |
|---|---|
| tolerance-free **containment as the alignment rule** | ws30Mage becomes the highest marker on 2,350 of 5,323 events, 44.1%. Its legs run 14,157 s, so the rung wins by being WIDE, not by matching |
| **containment as a candidate filter**, `SP_CONTAIN` | right on the 3 events it was proposed against, wrong on 5,323: 2,198 events lose EVERY candidate, the median candidate count falls 8.0 -> 1.0, the median distance off the pivot goes 0.327% -> 1.157% and the worst 8.953% -> 26.146%. The 3 events all came from the 18, which were selected for a large grace move and therefore sit inside well-formed legs |
| a **wider `SP_BAND`** | monotone trade with no knee. 0.0 -> 0.5 moved within-0.25% 43.6% -> 28.8% and bought only +1.397% -> +1.802% of leg |

---

## 7. The one item awaiting his word: `SP_TFS`

His 1024 list was **six**: ws3Mage, ws5Mage, ws10Mage, ws15Mage, ws20Mage, ws30Mage.
**ws1Mage and ws2Mage are MINE.** Every measurement that justified banking ran on all eight, so the
banked value is the set that was RUN — banking the six would bank something never measured.

| the TF set | the 18-row check | median off the pivot |
|---|---|---|
| `wide`, all eight — BANKED | 17 of 18 scored under the `window` arm, 18 of 18 under `lowest_pct` | 0.013% |
| `his`, the six | 8 of 18 under `window` | 0.156% |

At `SP_ALIGN_S` 300 ws1Mage and ws2Mage are the scale TF on **41.0%** of events. Set
`W_V4_SP_TFS=his` to run his six, with `W_V4_EXPERIMENT=1` since it is off the bank.

---

## 8. The validation

### The 18 rows he called perfect

Joe 1024: *"all of these are perfect on `EXHAUST grace 180`"*.

| the read | value |
|---|---|
| scored | 18 of 18 |
| median distance off the pivot | 0.013% |
| worst | 0.114% |
| within 0.25% | 18 of 18 |

THE 18 ARE NOT REPRESENTATIVE and that is on the record: they were selected for a large grace move,
which picks events sitting on their extremum. The population sits a quarter in. I reported the
18-row result as validation before knowing this, and then built two enhancements on top of it.

### The ws5rbackstop sweep — his option 3

Joe 1024: *"recreate the ws5rbackstop sweep that we banked yesterday. that gives us a level of
comfort or discomfort, without interfering in our in-progress v4core to 'ws4r to ws1Mage ib' design
flow"*. The backstop is BANKED, so its trades owe nothing to the mech under design — which is the
circularity he caught: *"to be well placed the event needs to be preceeded by v4core, and that's a
circular reference"*.

12 of 27 configs ran; 15 line caches are gone from `.rpl_cache/lines` — every config with k_len 5
or rsi 7. Both key configs were present. Full table in `out/net_sp.md`.

| the reading | across all 12 configs |
|---|---|
| the stop rate falls | 27.2–31.0% -> 17.2–21.3%, no overlap between the ranges |
| the median MFE roughly halves | 1.550–1.733% -> 0.868–1.010% |
| gross falls | 25–30% on every config |
| the trade count | identical, except 1 row of 6,037 |

| rsi | stc | k_len | the MFE window | trades | stopped | stop rate | gross % | median MFE % |
|---|---|---|---|---|---|---|---|---|
| 6 | 8 | 6 — BANK | banked 2% pivot | 628 | 175 | 27.9% | +726.32 | +1.691 |
| 6 | 8 | 6 — BANK | sweep-pivots | 628 | 124 | 19.7% | +532.20 | +1.009 |
| 5 | 8 | 7 — DB row | banked 2% pivot | 387 | 112 | 28.9% | +397.56 | +1.573 |
| 5 | 8 | 7 — DB row | sweep-pivots | 387 | 69 | 17.8% | +317.17 | +0.913 |

**THIS DOES NOT SAY WHICH WINDOW IS RIGHT.** Both nets are scoring artefacts — the 90%-of-MFE leg
is not causal under either — so a smaller net is not a worse mech. What it says is that
`sweep-pivots` is stable across 12 line configs whose ws5r controls span 1.30 to 18.67.

The one anomalous row: on `5|7|6` the sweep-pivots arm has 621 trades against 622. One trade's leg
closes on its own entry bar, so there is no window to measure and the `hiB <= en + 1` guard drops
it. 1 of 6,037 rows.

---

## 9. Still open

| the item | state |
|---|---|
| `SP_TFS` | his word — §7 |
| scored on MACHINE events | never done. Every population so far is the in-test `ws4r -> ws1Mage ib` chain's or the backstop's. The circularity he named is unresolved |
| the 15 missing line caches | `RS.load` is read-only; rebuilding them was not authorised |
| `out/net.md`'s column labels | read `k \| rsi \| stc` but hold `(rsi, stc, k_len)` — the transposition this session found in `v4_rcfg_sweep.spec`, still live in that file's header |

## 10. The four-read pivots — HIS 1118, held here since his 1120 SRP ruling

HIS 1120: *"this isn't SRP.  the pivots can't belong in any fdm3 classes"* / *"sweep-pivots calls for a list of
pivots, and the +15 button is there to import a different set of pivots"* / *"the reason I called out SRP is the
lookahead rabbit hole that you and fdm3 were circuling"*. Until 2026-11-20 the rule below was section 2 of fdm3's
`1118_orac_exhaust.md`, its knobs sat in `fdm3_knobs.py`, its pine view was a mode of fdm3's `oracle_rows.py`, and two
fdm3 specs stated its causality differently. Every value is unchanged by the move.

### 10a. The rule

HIS 1118: *"bake the 4 lines into the sweep-pivots machine: every test uses all lines to decide if dwell is
qualified"*, then *"1, the longest"*, then *"2, it shouldn't matter - we're going from a 'final' cross to ib, to the
next 'final' cross to ib"*.

`v4_sweep_pivots.pooled_pivots()`:

| the step | what it does |
|---|---|
| the four reads | ws{tf}Mage emerging, ws{tf}Mage closed-prev, ws{tf}b emerging, ws{tf}b closed-prev |
| every read contributes | its own oob->ib crosses, each carrying the DWELL - how long that read held out of bounds immediately before the cross |
| the group | a run of consecutive SAME-SIDE crosses. No time tolerance: the group is the run, which is what he ruled |
| the gate | the run qualifies when the LONGEST dwell inside it reaches the dwell knob |
| the pivot | that run's FINAL cross to ib |
| after the gate | two surviving runs that then touch on the same side merge, again taking the last |
| the guards | two asserts - the pivots alternate side, and they are in order |

**WHY FOUR READS.** The emerging line flickers in and out of the fence, so a real 2.4 minute oob run measures as 0.1
on it while closed-prev measures the same move as 3.0. Taking the longest lets the steady read supply the dwell and
the fast read supply the bar.

**THE DWELL IS 0**, and it was 180 for one turn. His own self-validation killed it: *"for each pivot that you print,
wait for 2 more pivots to print, then look back at the extremes between each pair"*. His example - the real price
high between 12:02 and 13:45 on 09-28 is 12:55:20; at dwell 0 a HIGH pivot prints 13:00:00, 4.7 min after it, and a
180 s dwell deletes that pivot so 13:45:00 survives instead, 49.7 min late. Measured over 09-22..09-28:

| dwell | pivots | mean lag to the real extreme | median lag | worst lag | within 5 min |
|---|---|---|---|---|---|
| 0, BANKED | 218 | 7.0 min | 2.8 min | 83.0 min | 153 of 217 |
| 60 s | 178 | 8.4 min | 3.2 min | 83.0 min | 121 of 177 |
| 120 s | 138 | 11.8 min | 3.8 min | 160.8 min | 87 of 137 |
| 180 s | 122 | 13.0 min | 3.9 min | 160.8 min | 75 of 121 |
| 300 s | 88 | 14.0 min | 4.1 min | 160.8 min | 53 of 87 |

The POOLING and the final-cross collapse are what cut the noise, not the dwell: 3,006 pivots on the tape against the
9,257 crosses raw emerging ws1Mage makes.

**THE BANKED LEGS ARE UNTOUCHED.** `legs` keeps its own default - every cross opens a leg, it closes on the FIRST
opposite cross, legs overlap - and `pooled_pivots` is a new reader beside it. HIS 1118: *"don't rebuild it - create a
mode for this new mech so that the existing pivots remain untouched in any now or future fdm3-oracle updates"*.

### 10b. The knobs

They live in `v4_sweep_pivots.py`, beside the code, NOT in `v4_knobs.py` - that file is not touched, so they follow
`v4_lift_e`'s precedent: env `W_SP_<NAME>`, a ruled registry, and an off-ruled import refuses unless
`W_SP_EXPERIMENT=1`. `v4_sweep_pivots.knobs()` prints them with the six in §4.

| the knob | value | his words | was |
|---|---|---|---|
| `POOL_TF` | 1 | the four reads run on ws1 | fdm3 `ORAC_PIVOT_TF` |
| `POOL_DWELL_S` | 0 | *"ok for the dwell"* - his lag test, the table above | fdm3 `ORAC_PIVOT_DWELL_S` |
| `SET_SHIFT_MIN` | 15 | *"rebuild 8792 with a pivot +15 minute button , and drop pivot +30 button"* | fdm3 `ORACLE_SHIFT` |

### 10c. The sets a page imports

HIS 1120: *"the +15 button is there to import a different set of pivots"*, and the flip button *"same treatment"*.
`pivot_set(trades, shift_min, flip)` makes them from any pivot-trade list - `pooled_trades()` or towards/away's
ws2Mage `pseudo_trades`. The page's two buttons only pick which set it imports.

| the set | built by | pseudo trades on the tape |
|---|---|---|
| as found | `pooled_trades()` | 3,006 |
| every pivot +15 min | `pivot_set(trades, 15)` | 3,005 |
| every pivot's side flipped | `pivot_set(trades, 0, True)` | 3,006 |
| +15 min and flipped | `pivot_set(trades, 15, True)` | 3,005 |

A pseudo trade opens at a pivot's confirm bar and closes at the next pivot's; its target-side is MINUS the pivot's
side. +15 moves every open and close by the same amount and drops a trade that would open past the tape; flipped
keeps every bar and flips every target-side. All four sets are identical to the lists the fdm3-oracle page built
inline before the move (checked 2026-11-20).

**HIS 1121 *"B"* - THE +15 SET IS CARRIED ON THE PAGE.** He found the +15 button changing rows the as-found view
already showed (the 2026-09-14 22:18:25 down trade, rows 22:33:00 to 22:36:30), because the +15 set moved the
trade's OPEN as well as its close and towards/away restarted the hunt at the later open. His pick, B, as I put it to
him: the trade keeps its open and its hunt, only the close moves, and each next trade's first 15 min show the
previous trade carried on.

`carried_set(trades, shift_min, flip)` -> [(open, show, close, target-side)]: `open` is the trade's own open (its
towards/away run and hunt start there), `show` = open + 15 min (its first printed bar), `close` = its close + 15 min.
The print windows [show, close) are exactly `pivot_set`'s trades - asserted - so the target-side on every row is
unchanged. The page runs it through `towards_away.run_carried` (5 groups of trades that do not overlap on the pooled
pivots), and asserts that every byte of every row a carried trade shares with its as-found self is the as-found one,
except the flip marks on that trade's first printed row.

| checked on 8794, 2026-11-21 | pivots +15 | +15 flipped |
|---|---|---|
| towards/away runs | 5 | 5 |
| bars of towards/away asserted equal to as found, both states | 2,247,588 | |
| page rows asserted equal to as found, both states | 374,580 | |
| as-found states, bytes that differ from 8793 | 0 | 0 |
| +15 bytes that differ from 8793's +15 (the old set) | 225,129 | 614,533 |
| 2026-09-14 22:33:00 to 22:36:30, cells that differ from as found | 0 | |

### 10d. The lookahead - stated here, once

| the read | knowable at |
|---|---|
| a cross to ib | its confirm bar, 90 s after the cross (`SP_XWOB` 18 bars) |
| a pivot, its run's FINAL cross to ib | the confirm bar of the first qualifying opposite-side cross after it - `pooled_final()`. Until then a later same-side cross can still take its place |
| a pseudo trade's open and target-side | the bar its pivot is final |
| a pseudo trade's close | the bar the next pivot is final |

Measured 2026-11-20 over the tape, at the banked knobs:

| the gap from a pivot's confirm bar to the bar it is final | seconds |
|---|---|
| shortest | 5 |
| median | 940 |
| longest | 4,455 |
| pivots final at their own confirm bar | 0 of 3,005 |

His 2026-09-30 03:21 ws5 AW sits in the trade that opens 2026-09-30 02:24:40: its open is final at 02:32:50, and its
close at 03:55:25 is final at 04:07:25. So a reader inside a trade can be causal and the trade itself is not - his
1109 *"noted - it's not a realtime tool"*. A causality question about a page row splits by owner: this table answers
for the trade, and the page's own rules answer for the reads inside it.

### 10e. The pine view

HIS 1118: *"create a pine module that I can load on a TF1 pane and see your view of the pivots"*, *"useing only the
red and green bgcolors mech"*. `python3 v4_sweep_pivots.py pine 2026-09-22 2026-09-28 [out.pine]`; the default file
is `out/sweep_pivots_pooled.pine`. GREEN a LOW pivot (an outgoing LONG), RED a HIGH pivot (an outgoing SHORT), each on
the minute bar that holds its cross. Moved from fdm3's `oracle_rows.py pine` mode, which now prints this command; the
streams are identical (2026-09-30..10-01, 76 timestamps).

### 10f. Who imports them

| the importer | what it picks |
|---|---|
| fdm3-oracle, `FDM3_PIVOTS=pooled` (8792, 8788) | the pooled producer; its pivots +15 min and flip pivots buttons pick the set |
| orac-exhaust, fdm3's `oracle_rows.py` | the producer the page it reads reports in `/meta` `pivots` |

### 10g. The 1125 repair - the default, and the rules are the jig's

**BANKED 2026-11-25, THE MACHINE** - his *"bank this sweep-pivots update and make it the machine"*, after his read of the
2026-09-05 to 2026-09-07 ws5 table: *"I retract.  the times are correct"*.

HIS 1125: *"I've found a flaw in sweep-pivots"* / *"there aree cases when ws{TF}Mage prints oob after the actual pxs
pivot, resulting in a pivot that is not the extremum"* / *"sweep-pivots' role is to detect extrema and label them as
pivots"* / *"this isn't a new mode, it's a repair of the existing ib to ib mech"* (*"four read pivots"*) / *"make the
repaired mode the default for sweep pivots.  ensure everything is in the jig so that we are consistent in our
behaviour"*, and what moves: *"Everything"*.

The rule is `optimus9.analysis.jig.sweep_pivots`; `v4_sweep_pivots.pivots(tf)` only feeds it the tape.

| the step | what it does | whose |
|---|---|---|
| the four reads | ws{TF}Mage and ws{TF}b, each emerging and closed-prev, pooled oob->ib crosses, 90 s confirm (`SP_XWOB` 18), dwell 0 | his 1118, unchanged |
| found | the closed ws{TF}Mage closes in an oob coming from ib; that forms the OTHER side's pivot, knowable from the next 5 s bar | his 1125 *"the entry to an opposing oob validates the final ib"*, his answer *"ws{TF}Mage enters opposite oob"* |
| the candidate | the last four-read cross to ib of that side since the previous entry into the same oob, confirmed by the entry's close | his 1125 *"the mech looks back from 1245 to find the last oob to ib"* |
| held | walkback-to-lookforward - the jig's walk back to look forward (`mage_cascade_bar`, his 1017 walk) on TF-bar lows / highs, 3 TF-bars a jump (`SP_WALK_STEP`), a final 4-bar confirmation (`SP_WALK_CONF`), looking forward to the entry bar | his 1124 / 1125 |
| the 3-pivot scan | the most extreme 5 s price from the previous opposite pivot to the entry; more extreme than held - the pivot moves there | his 1125 *"scans for every extrema in the last 3 pivots"* |
| modified | the previous pivot must be the most extreme of its side between its two neighbours, the newest from the previous pivot to the entry; both re-checked until neither moves. A same-side entry re-forms the newest pivot instead of adding one, so sides alternate. A walk-back that reaches past the previous opposite pivot hands the choice to the scan | MINE, flagged until he rules |
| the pivot's bar | its EXTREMUM - every pseudo trade, leg, set and swing-scale rung opens there | his 1125 *"The extremum bar"* |

The banked `mage_cascade_bar` is unchanged: `confirm` and `to` default to None, and 48,000 banked calls compared with
the pre-repair jig differ on 0. `legs(mode='banked')` (the 1024 overlapping legs) and `legs(mode='last_cross')` (his
1118 leg mode, still asked for by fdm3's `ORAC_LEG_MODE`) stay as explicit modes; no default reads them.

Every count in sections 10a to 10f was measured BEFORE this repair. On the tape after it:

| | before the repair | repaired |
|---|---|---|
| ws1 pivots (the bank, `POOL_TF` 1) | 3,006 | 2,567 |
| ws2 pivots | 1,599 | 1,270 |
| ws5 pivots | 660 | 529 |
| towards/away's ws2Mage pseudo trades | 1,564 | 1,269 |

| ws5, repaired | pivots |
|---|---|
| the extremum set by walkback-to-lookforward | 293 |
| the extremum moved by the 3-pivot scan | 236 |
| of those, the walk-back reached past the previous opposite pivot | 0 |
| moved again after it was found | 7 |

---

## Related

`v4_sweep_pivots.py` · `v4_net_sp.py` · `v4_knobs.py` · `../../fdm3/1118_orac_exhaust.md` (imports §10) · `out/net_sp.md` · `out/mage_sweep_prior.md` ·
`out/mage_align.md` · `out/band_sweep.md` · `out/sweep_pivots_18.md`
