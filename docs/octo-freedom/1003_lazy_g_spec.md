# lazy-g — the spec as Joe has given it, 1003

Joe's words are quoted. Everything not quoted is a reading of them, marked as such.

## THE THREE STAGES

Joe 1003: *"I'm introducing it in 3 stages"*.

| stage | his words |
|---|---|
| 1 | *"confluencing octa-sig decisions"* |
| 2 | *"flipping early-reversal-octa-sig-events to a continuation trade (pyramid)"* |
| 3 | *"creating lazy-g trade signals"* |

## TERMINOLOGY — SUB-WSF

Joe 1003: *"I'll refer to g30,15,5 as sub-wsf, as a subset of wsf"*.

| name | timeframe |
|---|---|
| g5 | **5 seconds** — `gcws5`, built into the line cache 1003, NOT in the indicator registry |
| g15 | **15 seconds** — `gcws15`, registered |
| g30 | **30 seconds** — `gcws30`, registered |

## THE ANCHOR, SHARED BY BOTH BRANCHES

Joe 1003: *"when octo-sig prints, walk back to g5's (gcws5) same-dr oob extrema to start the
calculation"*, and *"all tests are taken from the g5 extrema"*.

- CONFIRMED by Joe on his own example: octo-sig 01:45, g5 extrema **01:43:00 at g5Mage −1.64**.
- the walk back must cross a brief pop back inside the fence: one bar at 01:43:10 reads **16.55**,
  1.55 above the 15 fence, between the signal and his confirmed extrema. **How much of a pop-back is
  tolerated is a knob** — see below. 1 bar is the minimum that reaches his anchor.

## THE LADDER

Joe 1003: *"for each wsf TF above g5"*, and *"a straight line between g5 and ws12"*.

**g5, g15, g30, ws1 .. ws12.** The cap is his, in his own sentence.

## BRANCH A — two qualifiers, BOTH required

Joe 1003: *"Q2 and Q1 are both required to qualify"*.

| | his words |
|---|---|
| Q1 | *"for each wsf TF above g5, the ws{higher-tfs}Mage values are creating a bumpy cascade that moves away from dr"* |
| | *"Mage 'moving away from dr' is the load bearing mech"* |
| | *"'bumpy' = the Mage-value cascade is not required to be a straight line between g5 and ws12"* |
| Q2 | *"somewhere along the TF cascade, `r` swaps it's relative positioning with `Mage`"* |
| | *"eg `r` is above `Mage` at TF g5/g15, and flips to r under Mage at TF ws6"* |

**"away from dr" in his orientation**, which is the one to use:
- dr −1 is a LONG; the dr side is the LOW side; **away = Mage RISES up the ladder**. His example:
  g5Mage −1.64 -> ws12Mage 37.89.
- dr +1 is a SHORT; the dr side is the HIGH side; **away = Mage FALLS up the ladder**.
- **do NOT restate this as a signed product.** Doing so flipped the sign of both his figures 1003 and
  he called it: *"this is upside down - you've changed my numbers to suit your bias"*.

**"somewhere" means anywhere.** Joe 1003, when offered first/last/floor conditions: *"this feels like
you've already built a bias ... stay true to my words"*. Any swap in g5..ws12 satisfies Q2.

## DIRECTION — WHAT AGREE AND DISAGREE MEAN

Joe 1003: *"re 'disagree', I take that to mean "not providing confluence to the trade". example (for
branch A): a mage cascade is printing decreasing values as from lower TF to higher TF, and the trade
signal opened a LONG trade, the mage-cascade direction and the trade direction 'disagree'"*.

| the cascade, lower TF -> higher TF | the trade | verdict |
|---|---|---|
| decreasing | LONG (dr -1) | **disagree** - his example, verbatim |
| increasing | LONG (dr -1) | **agree** - increasing IS "away from dr" on dr -1, so Q1 fires |

**READING, mine:** on branch A, Q1 firing and agree are the same statement. "Away from dr" is the
cascade pointing the same way as the trade, so Q1 passing = confluence, Q1 failing = disagree. Joe's
example is the Q1-failing case and he named it disagree.

**NOT RULED:** branch B and branch C have no agree/disagree direction. Joe's definition is general but
his example is marked *"(for branch A)"*, and B's test is a LEVEL test with *"no requirement on
direction or shape"*. B and C rows stay `unruled` until he sets one.

**NOT RULED:** whether Q2 carries a direction of its own. His example cites the cascade direction only,
so Q2 is treated here as a qualifier with no direction - it gates branch A, it does not point.

## THE OUTCOME — A PXS REVERSAL IS NOT PART OF THE MECH

Joe 1003: *"a pxs reversal is the outcome of the mech if the trade and lazy-g are 'pointing' in the
same direction. pxs reversal is not part of the mech"*.

- so a pxs reversal is what branch A **predicts** when it agrees. It is never a test, never a
  qualifier, and never a column in a qualification report.
- CORRECTED 1003: this spec first carried *"lazy-g is predicting a pxs reversal"* inside Q1's mech
  rows, and the 10-02 report turned it into a `disagree` verdict on every branch A row. Both were
  wrong - the first put an outcome inside the mech, the second inverted the direction.

## BRANCH B — all the Mages ex-fence on the dr side

Joe 1003: *"moving towards dr isn't a requirement of branch B. branch B needs all of the Mages
ex-fence on dr-side. they don't need to create a pattern"*.

- so the test is a LEVEL test at the g5 extrema bar, TF by TF, with **no requirement on direction or
  shape**.
- CORRECTED 1003: this section first described branch B as *"the cascade moves toward dr"*, which was
  my characterisation of the data and not his rule.

## BRANCH C — the lower wsf lines leading the higher wsf Mages

Joe 1003: *"19:16 is a new branch C. the lower wsf lines are `leading` the higher wsf Mages"*.

**THE SPLIT between lower and higher is a knob.** His words: *"I don't yet have a clean definition of
the split between lower and higher wsf lines. we will set it to ws{knob:5, `LAZY_G_WSF_TF_SPLIT`}"*.

**WHEN IT ENGAGES**, his words: *"branch c will engage when a lookback of the wsf Mages discovers
1) a common reversal of the Mages and 2) lower wsf Mages that have gone in-fence and are creating a
`cascade away from dr` pattern that continues to pull the higher wsf Mages towards in-fence"*.

**THE WINDOW IS NOT SET.** Joe: *"common reversal needs a window size that I don't have. it will be
somewhere around 18:50"* — for the 19:16 octo-sig, whose g5 extrema is 19:16:05.

### BRANCH C'S ANCHOR — RULED 1003: carry the extrema in memory

Joe offered two ways and chose the second: *"or, to reduce overal live-loop cost - store the last
known ws12Mage extrema on this dr in memory"*, then *"I prefer option2, bake it"*.

**THE RULE.** Carry the running ws12Mage extreme for the CURRENT dr. On the dr side: the minimum for
dr −1, the maximum for dr +1. **Reset when dr flips.** At an octo-sig, the carried extreme IS branch
C's anchor, and the walk runs from it to the octo-sig bar.

- costs one comparison per bar. No pivot, no 10-minute walk-back, no span search.
- it fits shape B, which already carries state per bar, so it adds nothing to the live loop.

**THE OPTION NOT TAKEN, and why it is worth recording.** Joe's first offer was *"lookback and locate
the pivot / walk back another 10 minutes (the floater) / find the ws12Mage extrema between the floater
and octo-sig"*. Measured against the 19:16 case it reaches the 18:47:35 anchor only from the
SECOND-LAST confirmed pivot (18:56:45), because `swing_detect.find_pivots` *"appends the final running
extreme as provisional"* — so "the last pivot" is always the current bar and the walk-back collapses
to the last 10 minutes.

- **the pivot does genuinely mark the reversal** though: there is a pxs **L** pivot at **18:47:40**,
  five seconds after the ws12Mage trough at 18:47:35. The idea was sound; the selection rule was the
  problem.
- **"floater" is OVERLOADED.** `jig.anchor_floater` (Joe 0912) defines a floater as an **r extrema
  found by a three-step lookback**. Branch C's floater was a flat 10 minutes back from a pivot. Two
  different things, one word. Option 2 removes the collision by needing neither.

### THE TWO CONCEPTS CARRIED FORWARD, and ONLY these two

Joe 1003: *"that mech ultimately failed so I don't want to resurrect it and muddy the spec that we're
building out of its ashes. having an understanding of matryoshka and blast radius is all we need to
bring forward into branch C"*.

**SO `Mage-ladder-weakness`, `wsf_mage_ladder`, `wml_spread` AND `wml_weak` ARE OUT.** They are the
failed mech. Not a measure, not a baseline, not a starting point. Do not reach for `wml_spread` as a
convenient one-number summary of a cascade - that is the resurrection, and it was one step away 1003.

| concept | Joe's words |
|---|---|
| **matryoshka** | 0824: *"a lower TF (~1 to ~4) r line will always stall or curl before the higher TFs - it's the matryoshka nature of lines sharing the same config ... you can visualise the r line curling (reversing) in a per-TF falling dominoes effect. ie, the LTFs are leading the way"*. The order is guaranteed, not incidental: every line shares one config and differs only in bar width, so a shorter bar reaches its turn first by construction |
| **blast radius** | 0825: *"each r line has a small blast radius"* — a line reaches its NEIGHBOURS on the ladder, not across it |

- branch C says *"leading"*, which is the matryoshka order read on **Mage** rather than on `r`.
- blast radius is why *"continues to pull the higher wsf Mages towards in-fence"* is a neighbour-by-neighbour statement, not a whole-ladder one.

## PARKED FOR STAGE 3 — THE FORWARD WALK AND THE dr GATE

Joe 1003, after walking 02:11 forward: *"you've highlighted something I didn't see, and now I know
it's too early for me to introduce this idea. if you're curious, it's the dr that I didn't consider,
so the signal was always going to be reversed. ie, if dr was -1 (not +1) then the lifting cascade at
02:23:10 would create a LONG open signal"*, and *"being able to reliably react to that scenario is
stage 3 dev, and we'll need to figure out a sensible way to override the dr gate that doesn't break
anything else"*.

**NOT BUILT. NOT A STAGE 1 MECH.** Recorded so the walk and its numbers are not re-derived.

The procedure he gave, verbatim: *"walk forward from 02:11 until both g30r and g15r are low oob, then
walk to g5Mage returning infence, then test for lazy-g"*.

| step | result on 02:11 (a SHORT, dr +1) |
|---|---|
| 1 — both g30r and g15r low oob (<=15) | **02:22:30**, g15r 8.20, g30r 11.10 |
| 2 — g5Mage returns in-fence, oob 15/85 | **02:23:10**, g5Mage 15.50 (ex-fence at 02:23:05, 13.49) |
| 2 — g5Mage returns in-fence, Mage 25/75 | **02:23:35**, g5Mage 33.20 (ex-fence at 02:23:30, 22.86) |
| the cascade at 02:23:10 | g5Mage 15.50 -> ws12Mage 59.93 = **lifting** |
| Q1 away, dr-signed on dr +1 | **-44.42** |
| Q2 | CROSS |
| furthest rung from dr | **g30 at 100.19**, then g15 at 90.83. ws12 is the NEAREST at 25.07 |

- the lifting cascade is a LONG signal. The octo-sig at 02:11 was a SHORT, so the dr gate made the
  verdict a disagree by construction - Joe's point above.
- stage 3's requirement, in his words: *"a sensible way to override the dr gate that doesn't break
  anything else"*. No mech exists for this.

## OPEN DEFECT — Q1 READS 2 OF THE 15 RUNGS

Joe 1003: *"reading only 2 of the rungs is risky: there's always potential for a less than ws12Mage TF
to print a higher extrema"*.

**CONFIRMED on 10-02, and it is the common case, not the edge case.**

| measured at the 25 walk-back anchors | count |
|---|---|
| a rung below ws12 prints a MORE extreme Mage than ws12 | **19 of 25** |
| ws12 is itself the most extreme rung | 6 of 25 |
| largest overshoot hidden by the endpoint pair | **+46.59** at 12:58, where g15Mage 77.07 is the extreme and ws12Mage reads 123.66 |
| next largest | +32.42 (04:50, ws1), +31.12 (04:30, g15), +29.09 (19:16, ws2), +27.96 (04:53, g5) |

- `Q1 away` as implemented is `ws12Mage - g5Mage`, dr-signed. The 13 rungs between them are not in
  the number, so a cascade that lifts, collapses mid-ladder and lifts again scores the same as a
  clean one.
- **NOT RULED:** what replaces the endpoint pair. Options are all unmeasured and none is his yet.
- **`Q1 away` is my column name, not Joe's word.** His sentence is *"a bumpy cascade that moves away
  from dr"*. Awaiting his name for the measurement.

## KNOBS TO SWEEP LATER

| knob | current | Joe's words / status |
|---|---|---|
| **branch B's fence** | unset | *"which fence, oob or mage-fence, is a knob to sweep later"*. oob is 15/85, the Mage fence is 25/75. **On the 6 branch B octo-sigs of 10-02 the choice FLIPS the sign**: at oob 4 qualify for −282.09, at 25/75 five qualify for +52.99, and the whole difference is the 12:58 trade (+335.08), which breaches oob at g15 (77.07) and passes 25/75 |
| **the anchor walk-back's pop-back tolerance** | 1 bar | the minimum that reaches Joe's confirmed 01:43:00 anchor. Not his number - he has not set one |
| the ladder cap | ws12 | **his**, from *"between g5 and ws12"*. Listed here only because a wider ladder is a thing a sweep could ask |
| Q1's "bumpy" threshold | none | no threshold is applied. Net direction only, as he specified |
| **`LAZY_G_WSF_TF_SPLIT`** | **ws5** | Joe 1003, branch C: *"I don't yet have a clean definition of the split between lower and higher wsf lines. we will set it to ws{knob:5}"*. **Whether ws5 itself sits in the LOWER or the HIGHER group is not stated** |
| ~~branch C's "common reversal" window~~ | **CLOSED 1003** | superseded. Joe: *"branch C isn't so much interested in the actual reversal, and highly interested in the walk that follows - its trigger is based on the lower wsf TFs leading the higher wsf TFs in the walk up to octa-sig"*. No window is needed: the carried ws12Mage extrema IS the walk's start |
| **all tolerances** | **unset, deliberately** | Joe 1003: *"I feel it's too early to set them. we'll hone them with experience"*. Nothing in this spec applies one |
| branch C's "in-fence" | unset | *"gone in-fence"* - same oob-or-Mage-fence question as branch B, and not separately ruled |

## WHAT IS MEASURED SO FAR — 10-02, the 25 live octo-sig

| population | trades | wins | net | per trade |
|---|---|---|---|---|
| all octo-sig | 25 | 6 | −1,046.86 | −41.87 |
| **branch A qualifies (Q1 AND Q2)** | **11** | 2 | **−798.97** | **−72.63** |
| branch B population (Q1 fails) | 6 | 3 | +226.25 | +37.71 |
| Q1 fires but no r swap — **UNNAMED by Joe** | 8 | 1 | −474.14 | −59.27 |

- branch A, under the direction ruled 1003, AGREES with all 11 of those octo-sigs. 8 of the 11 hit the
  0.70% stop, so on 10-02 branch A's confluence pointed at the losing side. One day, n=11.
- **effective-n is tiny**: 11 / 6 / 8 on ONE day. Nothing here is a rate.
- the 8-trade group satisfies Q1 and not Q2, so it is neither branch A nor branch B. It has no name
  and no mech.

## PARKED FOR A FUTURE MVP — PEGGED r AS HIGHER-TF PRESSURE

Joe 1004, on the 88 stall episodes from 10-03 00:13:00: *"it's relentless becuase it's the top of a
ws45r (45 minute) cycle - lot's of consolidation going on"*, and *"fun fact - when r lines sit pegged
for a length, they're signalling that a higher TF is applying upward pressure (or downward if it's
-1dr). maybe in a future MVP, we'll unpack that and see if we can capitalise on it somehow"*.

**NOT BUILT. NOT MEASURED.** His read, recorded as his.

| what the observation explains | the measured fact it attaches to |
|---|---|
| the relentless flicker is a ws45r cycle top | ws14 stalls 88 times between 10-03 00:13:00 and the tape end, episodes 2-12 alternating 2.6 min / 0.9 min with 30 s gaps, ws14r pinned at its own stale high 99.85 |
| pegged r = a higher TF pushing in the dr direction | at 00:13:00 three TFs read EXACTLY 100.00 - ws18, ws19, ws23 - and none of them is stalled; 16 of 21 TFs in ws3..ws23 are stalled somewhere in 00:08..00:18 |

What a future MVP would need, so it is not re-derived:

| ingredient | status |
|---|---|
| `ws45r` in the line cache | **NOT BUILT.** The r spec is `(('k', 5, 8, 7, 'close'), 'emerging')`; a 45 min line is one `override(2700, ...)` build |
| a momo bank for tf 45 | **EXISTS.** `momo_bank(db, 45)` resolves to the **domtf** band 13-60, `k_window` 6, so the window would be 270 min. No new config needed |
| the stall producer | `jig.stall_mask` with `STALL_N` 6 (Joe 0814). Already used here |
| "pegged for a length" | **NO MECH.** The stall measures "no new extreme for 6 lattice samples", which is not the same as "sitting on one value". A peg test does not exist |

## LOCKED IN — THE WALK TO THE 00:13 STALL (Joe 1004)

Joe's words, verbatim, locked at his instruction *"lock this in for me"*:

> *"we reached the stall at 00:13 through this walk: +1dr 22:30, octa-sig. ws4 has momentum so
> octa-sig is squashed / walk forward from 22:30, continue consuming the higher mom-true TFs as they
> print. / 23:32, next +1dr octa-sig. ws13 momentum picks up the baton, then passes to the next baton
> when it is `stalled` / 00:13, ws14 has been holding the baton and is now stalled. a test (yet to be
> defined) decides if the ws{3,5,6,7,11,12}r matryoshka leads have created enough proof to reverse now
> (because the stalls are all in matryoshkic-sync), or maybe this test would want to walk forward and
> capture ws 10 at 00:18. we won't know how to build the magical multi-stall-end-of-a-large-leg test
> until we've seen more examples"*

**THE TEST DOES NOT EXIST.** His own words: *"yet to be defined"*, and *"we won't know how to build
[it] until we've seen more examples"*. Nothing here is built. Do not build it on one example.

### The mom-true set at each moment of his walk, measured. dr +1, ws3..ws23, `momo_g(...)[0] in ('momo','curl')`

| moment | bar | mom-true set | highest = the baton |
|---|---|---|---|
| his 22:30 | 10-02 22:30:00 | ws3, ws21, ws22, ws23 | ws23 |
| the 22:32 octo-sig | 10-02 22:32:05 | ws22, ws23 | ws23 |
| the 23:32 anchor | 10-02 23:31:20 | ws10, ws11, ws13, ws15 | ws15 |
| the 23:32 octo-sig | 10-02 23:32:25 | ws4, ws10, ws11, ws13 | **ws13** |
| ws14 regains mom-true | 10-02 23:48:50 | ws4, ws5, ws7, ws10, ws12, ws13, ws14 | **ws14** |
| ws14 stalls | 10-03 00:13:00 | ws13, ws14, ws16 | ws16 |
| ws10 stalls | 10-03 00:18:00 | ws13, ws14, ws16 | ws16 |

### WHAT VERIFIED

| his claim | measured |
|---|---|
| 23:32, ws13 picks up the baton | **YES.** ws13 is the highest mom-true TF at the 23:32:25 octo-sig bar |
| the baton passes on when the holder stalls | **YES in sequence.** ws15 held it at the 23:31:20 anchor and dropped 5 s later; ws13 took it; ws14 took it at 23:48:50 and stalls at 00:13:00 |
| the ws{3,5,6,7,11,12}r matryoshka leads are all stalled, in sync | **YES, all six.** Stall starts: ws3 00:03:25, ws5 00:04:15, ws6 00:06:10, ws7 00:07:30, ws11 00:10:00, ws12 00:07:20. 16 of 21 TFs are stalled somewhere in 00:08..00:18 |
| ws10 is available 5 min later | **YES.** ws10's stall starts 00:18:00 |

### WHAT DID NOT VERIFY — three departures, flagged not corrected

| his claim | what the data says |
|---|---|
| *"+1dr 22:30, octa-sig ... squashed"* | **no squashed octo-sig found at 22:30.** The o9_ledger holds exactly three rows between 22:00 and 23:59: octo-sig 22:32:05 (Sell, -109.97), 23:32:25 (-120.26), 23:54:20 (-108.70). The 22:32 one FIRED and traded. 22:30:00 is that trade's g5 oob extrema, not a signal time. `o9_state_log` has 0 rows in 22:20..22:40 and logs the `s` family, not octo-freedom, so no squash record exists to check |
| *"ws4 has momentum"* at 22:30 | **ws4 is `none`** at both 22:30:00 and 22:32:05. The mom-true TFs at 22:30:00 are ws3 (curl), ws21, ws22, ws23. ws3 is `none` by 22:32:05 |
| *"00:13, ws14 has been holding the baton"* | **ws14 is mom-true and is the one that stalls, but it is not the highest.** ws16 is, on a `curl` held since 00:03:55. ws14 was the top rung from 23:48:50 until ws16 arrived |

- the departures do not touch the idea. The six matryoshka leads stalling in sync is the load-bearing
  observation and it holds exactly as he described it.
- **OPEN, his:** whether "the baton" means the highest mom-true TF (how it is measured above) or
  something else. ws16 holding it at 00:13 depends entirely on that definition.

## THE BATON WALK ON 09-25 00:00..12:00 — THE CHAIN BREAK BRACKETS THE LOW

Joe 1004 asked for the stall + baton report with the octo-sig interleaved. dr +1, ws3..ws23,
`STALL_N` 6, 63 batons, 19 octo-sig rows. Built by `baton.py` from the rpl line cache; the octo-sig
rows come from `report_leash_walk.py --day 2026-09-25 --tape-end 2026-10-04` (v4 knobs, dr recipe
reproduced rig.DR on 0 of 1,630,780 bars differing).

| what | bar | pxs |
|---|---|---|
| window start | 00:00:00 | 0.184926 |
| pxs LOW | **07:13:45** | **0.181817** |
| pxs high | 11:35:40 | 0.199407 |

**THE RESULT.** The chain broke for ~37 minutes straight across the low:

| measure | value |
|---|---|
| broken span | rows 21-50, **06:45:10 .. 07:22:35** |
| rows in it with `mom-true` = 0 (nothing to pass the baton to) | **21 of 30** |
| rides in it | 0.1-0.8 min flickers, none longer than 3.5 min |
| the pxs low sits INSIDE it | row 44, 07:09:05, reads exactly 0.181817 |
| deepest stall | **20 of 21** at 07:18:25, +0.51% above the low |

**THE OCTO-SIG DOES NOT OVERLAP IT.** Last signal before the break: 03:32:35. First after: 07:59:20,
36 min after the chain recovered. Zero octo-sig inside the 37-minute break.

**THE OCTO-SIG CLUSTER FIRES AT THE OPPOSITE CONDITION.**

| | the chain break 06:45-07:22 | the octo-sig cluster 08:26-08:40 |
|---|---|---|
| stalled | 10 -> 20 of 21 | **1 -> 4 of 21** |
| mom-true | 0 on 21 of 30 rows | **14 -> 16 of 21** |
| pxs after | turned up from 0.181817 | ran to 0.199407 |

- **READING, mine:** on this window the chain break marks the TURN and the octo-sig cluster marks the
  RUN that follows it. They are ~70 min apart and never co-occur. One window.
- this is the 3rd leg walked (10-02 down, 10-01 round trip, 09-25 morning). The chain break has now
  bracketed or near-missed the turn on 10-02 (inside, dr +1), 10-01 (local low inside, dr +1) and
  09-25 (inside, dr +1). **The dr frame is still unruled** - see the correction note above.

## WHAT A STALL CLUSTER MEANS — Joe's wording, 1004

My phrasing was *"11 of 21 TFs stalled at some point in that 45-minute interval"*, which is a count
with no mech behind it. Joe tightened it:

> *"most of the wsf lines are stalling, indicating that the whip-end of the matryoshka line is
> reversing and attempting to pull the dtf lines around"*

**USE THIS WORDING.** The count is the evidence; the sentence is the mechanic.

Measured at the 09-25 03:30:05 octo-sig, which is what he read it off:

| measure | value |
|---|---|
| stall ONSETS since the prior row (02:45:10, 45 min back) | **58** |
| distinct TFs producing them | **11 of 21** — ws3, ws4, ws5, ws6, ws7, ws9, ws10, ws11, ws13, ws14, ws16 |
| stalled STATE at the signal bar | 5 of 21 |
| mom-true at the signal bar | 13 of 21 |

- the 5-of-21 state is a one-bar snapshot and is NOT the confluence. The 58 onsets across 11 TFs is.
- **COMING:** Joe 1004 — *"I'll be introducing a new `mtd` mech soon that confluences the 03:32:20
  `ws1mage-rev + r oob` event"*. Not specified, not built. 03:32:20 is event 4 of the 15 qualifying
  off-book events on 09-25 (dr -1, ws1r 14.78 EX lo, ws1Mage 24.81, gcws30Mage 26.04).

## BRANCH D — THE r-CASCADE, with the mage-cascade as a trend grade. Joe 1004

Joe named it D. Introduced off the 09-25 02:12 and 03:30 octo-sigs.

### D.1 THE PREMISE — Joe verbatim, 1004

> *"02:12 introduces a new mech/branch, for which you will need to interogate ws1 and ws2. you can
> see that at 02:12, ws2r and ws3r are hi oob, while each higher ws{wsf-TF}r 'falls' away from hi oob
> in a cascade. ie ws3r was the last TF to have enough momentum to exit the oob fence, and the TFs
> above ws3 lack the strength"*
> *"this is a known pattern, and represents the same action as the mage cascade"*
> *"the mage-cascade prints in the higher wsf TFs to confirm that higher lines want to travel
> downward"*

On 03:30, same branch:
> *"03:30 is confluenced, for the same r-cascade reason as 02:12. the r-cascade begins with ws3r
> lifting. there is no mage-cascade lifting away at 03:30, telling us that we are trading against a
> trend"*

### D.2 WHAT FIRES IT

| | |
|---|---|
| the firing condition | **the r-cascade.** 03:30 has no mage-cascade and Joe still called it confluenced |
| the mage-cascade | **a grade, not a gate** - present = with-trend, absent = against-trend |
| branch D's verdict | **confluence.** Joe called both 02:12 and 03:30 confluenced. Unlike B and C, D has a direction |
| against-trend consequence | *"should create a smaller sized position to handled slippage costs"* - **MVP2**, not this build |
| magnitude thresholds | **none.** Joe 1004: *"unlikely. the mech needs lines to be under or over the starting block"* - the test is positional, not magnitude |

### D.3 THE SIX RULINGS, Joe 1004

| # | question | his ruling |
|---|---|---|
| 1 | must the ex-fence block be contiguous? | **no.** But the gap must be meaningful: *"the gap between 2 and 10 is too large to be meaningful. 'meaningful' means has a voice to the mech's outcome ... if the gap was 2 (eg ws2 jumps to ws5) then I'll want to look at it and make a call based on the wider picture of that particular bar. I don't know the gap's minimum yet, so I'm choosing 4 as an arbitrary knob"* |
| 2 | is ws1 in the ladder? | **yes, most definitely.** *"on lookback, you'll find that ws1 is leading ws2 (blast radius, matryoshka) when it returns to ib at ~02:07. the mech needs to check for this scenario using a divergence test, and a lookback test. if either are true, then ws1 is accepted. if ws1r is found in the lookback or div then the mech needs to claim the ws1r extrema value, not the 02:12 value"* |
| 3 | can the cascade lift again at the top? | *"I don't know yet. my current view to be strawmanned: so long as the higher TFs are not printing a value that's between ws1 and the weak r, then the higher TFs have no claim"* |
| 4 | which mage-cascade definition? | **no-op.** *"I was concise: there should be no task attached"* - the 1003 "failed mech" remark carries no block, and task #22 is not a gate on this |
| 5 | magnitude thresholds? | see D.2 - none |
| 6 | the name | **D** |

**WHICH ws1r EXTREMA** - Joe 1004, asked directly between the floater, the pivot and the 02:12 value:
> *"the floater, ie the moment when ws1r completed its purpose"*

### D.4 KNOBS

| knob | value | status |
|---|---|---|
| **`LAZY_G_D_GAP_MAX`** | **4** | Joe's, explicitly arbitrary: *"I'm choosing 4 as an arbitrary knob (add to spec for sweeping)"*. **SWEEP IT** |
| the fence | oob 15/85 | from the r ex-fence reading. Not separately ruled for D |
| divergence producer | `jig.anchor_floater` + `jig.divergence` | existing, Joe 0912. `AF_BLOCK` 60 bars = 5 min |
| the lookback test | **NOT DEFINED BY JOE** | see D.6 |

### D.5 MEASURED AT 02:12:10, dr +1 - every ruling checked

| ruling | measured |
|---|---|
| ws2r and ws3r hi oob | **ws2 98.22, ws3 91.06, and ws4 86.59** - three TFs ex-fence, not two. The last to exit is **ws4**, not ws3 |
| the r-cascade falls above it | ws4 86.59 -> ws5 79.43 -> ws6 64.11 -> ws7 46.69 -> ws9 30.40, a **-56.19** fall over five rungs |
| the mage-cascade confirms downward | **Mage net ws1->ws12 -39.23**, biggest step ws6->ws7 **-22.0**. dr +1, so -39.23 is AWAY from dr |
| ws1 leads ws2 on the ib return | **CONFIRMED.** ws1r's last ex-fence bar is 02:08:45 (85.81), back IB at **02:08:50** (83.05). ws2, ws3, ws4 are STILL ex-fence at 02:12:10 |
| Joe said ~02:07 | actual **02:08:50**, 1.8 min out |
| the divergence test on ws1r | **FIRES.** `anchor_floater` -> `fired: 1` |
| the anchor | bar 1479026 = **02:12:10**, ws1r 62.92, px 0.187556 |
| the pivot (dr-opposed extreme) | bar 1479017 = **02:11:25**, ws1r 49.06, 0.8 min back |
| **the floater (Joe's claimed value)** | bar 1478929 = **02:04:05**, ws1r **93.52**, px 0.186817, **8.1 min back** |
| `d_osc` / `d_px` / blocks | **-30.60** / **+0.000739** / 3 blocks walked |
| the independent `divergence` producer | bearish **+1 confirmed at 02:08:45** - the same bar ws1r last left the fence |

**Q3's STRAWMAN SURVIVES.** Band = [ws1r, weakest ex-fence] = [62.92, 86.59] at the 02:12 value:

| TF | r | inside the band | claim |
|---|---|---|---|
| ws5 | 79.43 | INSIDE | has a claim |
| ws6 | 64.11 | INSIDE | has a claim |
| ws7..ws12 | 46.69, 47.28, 30.40, 42.04, 42.27, 50.99 | all outside, all BELOW | no claim |

- the **ws9->ws12 lift (30.40 -> 50.99) stays below 62.92**, so it is outside the band and has no
  claim. **The top-end lift does NOT break the cascade** under his rule.
- **under the ruled floater value 93.52** the band becomes [86.59, 93.52] and the only TF inside is
  ws3 (91.06), which is already in the ex-fence block. So at 02:12 **no higher TF has a claim at all**.

### D.6 STILL OPEN

| open | detail |
|---|---|
| ~~the "lookback test"~~ | **DEFINED by Joe 1004.** *"the lookback needs to find the extrema of ws1r. this means looking back in 5 minute increments (same as the divergence lookback mech) until a extrema is exposed"*. That is the step-3 BACKWARD BLOCK WALK of `jig.anchor_floater` - `AF_BLOCK` 60 bars = 300 s = 5 min, walking back until a block adds no new extreme. **So the two tests share one producer and differ in strictness**: the DIVERGENCE test needs `fired` (price makes a further extreme while the oscillator does not), the LOOKBACK test needs only that the block walk EXPOSES an extrema at all. That is what makes his OR meaningful - a strong test and a weak one. **The strictness split is MY READING of why both exist; the 5-minute block walk is his word.** My earlier candidate - the ib-return lead - is WRONG and is struck |
| gap measurement | `LAZY_G_D_GAP_MAX` 4 - is the gap the COUNT OF SKIPPED TFs (ws2->ws5 = 2 skipped) or the TF-number difference (ws2->ws5 = 3)? His example *"if the gap was 2 (eg ws2 jumps to ws5)"* says **skipped count**, which is my reading of his arithmetic, not a separate ruling |
| ws2's role | Joe said *"interogate ws1 and ws2"*. ws1's role is ruled (D.3 #2). **ws2 has no separate rule** - it is currently just the bottom of the ex-fence block |

## THE CASCADE — LOCKED IN, 1004. READ THIS BEFORE TOUCHING ANY CASCADE MECH

Joe 1004: *"bank your understanding of the cascade with clear detail so that its locked in"*. Written
after I wrongly flagged mtd.r2 as inverted. It was not; the error was mine, twice over in two days.

### THE ONE RULE — direction of travel up the TF ladder

| the cascade, read LOW TF -> HIGH TF | confluences |
|---|---|
| **lifting** (values rise up the ladder) | **LONG** |
| **falling** (values fall up the ladder) | **SHORT** |

Joe 1004, verbatim: *"if the mage cascade is 'lifting' the values from g5 to ws12 it can only
confluence a LONG trade. both the LONG trade and the mage cascade are 'lifting' upwards"* and *"if
the mage cascade is 'falling', ie ws12 has a high value and g5 has a lower value, then only a SHORT
can be confluenced (because the SHORT is falling)"*.

**VALIDATED 25 of 25** on the 10-02 live octo-sig. Nothing about this rule is inferred.

### AWAY FROM dr vs TOWARDS dr — the two phrasings, and the trade each yields

dr is the BIAS frame: **dr +1 = SHORT, dr -1 = LONG** ([[dr-plus-one-is-short]]). The dr SIDE is the
high side at dr +1 and the low side at dr -1.

| dr | dr side | **AWAY** from dr | that cascade confluences | **TOWARDS** dr | that cascade confluences |
|---|---|---|---|---|---|
| **+1** | high | the cascade **FALLS** | **SHORT** = the dr-side trade | the cascade **LIFTS** | **LONG** = the opposite trade |
| **-1** | low | the cascade **LIFTS** | **LONG** = the dr-side trade | the cascade **FALLS** | **SHORT** = the opposite trade |

- **AWAY from dr always yields the dr-side trade.** This is branch A's Q1.
- **TOWARDS dr always yields the OPPOSITE trade.** This is mtd.r2.
- Both are the SAME single lifting/falling rule. Neither is an inversion of the other.

**THE MISTAKE I MADE, so it is not repeated:** I compared mtd.r2's CASCADE direction against the
dr-bias TRADE side and called it a conflict. Those are two different quantities. A cascade "facing
dr" is a statement about the lines, not about which trade the dr implies.

**THE OTHER MISTAKE, 1003:** I restated *"Mage moving away from dr"* as *"Mage x dr decreasing"*,
which flipped the sign of both of Joe's figures (-1.6 -> +1.6, 70.5 -> -70.5). Joe: *"this is upside
down - you've changed my numbers to suit your bias"*. **NEVER restate a cascade as a signed
product.** Report the raw low-TF and high-TF values and the word lifting or falling.

**A dr-SIGNED COLUMN HIDES THE DIRECTION.** `Q1 away` is `(ws12 - ws1) x -dr`, so a positive value
means lifting on a LONG and falling on a SHORT. Joe read 02:11's `+36.03` as a lift and asked why a
SHORT was being confluenced; it was a 36.03-point FALL. **Always print the raw pair beside any
dr-signed cascade number.**

### MEASURED BOTH WAYS ON 10-02, all 25

| group | n | the cascade's confluenced side vs the trade that fired |
|---|---|---|
| cascade AWAY from dr (`Q1 away > 0`) | 14 | the cascade confluences the trade that fired |
| cascade TOWARDS dr (`Q1 away <= 0`) | 11 | the cascade confluences the OPPOSITE of the trade that fired |
| agreement between the two readings | **25 of 25** | |

Worked example, 04:30, a SHORT on dr +1: g5Mage **98.71** -> ws12Mage **122.79** = **lifting**, so
the cascade confluences a **LONG** while a SHORT fired. `Q1 away` reads **-24.08** (towards dr). That
SHORT lost **-124.87**.

## mtd — THE MAGE-TREND-DETECTOR, Joe 1004

Joe 1004: *"07:59 is blocked because of a new `mage-trend-detector` (`mtd`) mech"*.

| | |
|---|---|
| what it tests | *"the likelihood of an overarching trend continuing. in practical terms, `mtd` is deployed to gate early reversals"* |
| where it sits | *"the priority branch, ie the first gate test in the octo-sig confluencing machine"* - it runs BEFORE A, B, C and D |
| its lines | **g5, g15, g30, ws1** |

### THE NAMES, Joe 1004 — TENTATIVE, his word is "maybe"

> *"lazy-g is the machine in my eyes. maybe me split it into lazy-g and lazy-g-conf. lazy-g is what
> creates the ~04:41 and ~06:13 trades"*

| name | what it is |
|---|---|
| **lazy-g** | the machine that CREATES trades - the off-book ~04:41 / ~06:13 ones. His stage 3 |
| **lazy-g-conf** | the confluencing machine - mtd first, then branches A/B/C/D, gating octo-sig. His stage 1 |

**NOT FINAL.** He said *"maybe"*. Do not rename files or code on this yet.

### mtd STEP 1 — find the most extreme point from dr

**THE LOOKBACK, Joe 1004.** His flow:

> *"from a bar that is 4 minutes before the signal (07:55) / find the oob extrema between that bar
> and the signal (07:59) / if no oob extrema is found, the lookback test is disqualified and the walk
> walks forward"*

**CORRECTED by Joe 1004, and the correction is the whole point of the two numbers:**

> *"4 minutes is the wide angled view of the 2 minute lookback. we use 4 minutes so that it is easy
> to spot an extrema anywhere in the 2 minute lookback"*

| | |
|---|---|
| **THE MECH'S WINDOW** | **2 minutes = 24 bars** at the 5 s grid, from signal-2min to the signal bar. THIS is what the test reads |
| **THE DISPLAY WINDOW** | **4 minutes = 48 bars**, signal-4min to the signal bar. REPORTING ONLY, so an extrema sitting near the 2 min edge is visible in context |
| what it looks for | the **opposing-dr** g5Mage oob extrema inside the **2 minute** window |
| no existing mech is needed | it is a plain window scan. Joe 1004: *"if you can't find the mech then I've probably conflated"* - he had. `opposed_extrema` walks 5-min blocks and is NOT this |
| on no-find | the lookback test is **disqualified** and the walk walks forward |

- **MY ERROR, corrected in place:** I first recorded the 4 minutes as the mech's window and wrote
  that it superseded the 2 minutes. It does not. The mech is 2 minutes; 4 minutes is how it is drawn.
- for a 07:59:20 signal: the mech reads **07:57:20 -> 07:59:20**, the report draws
  **07:55:20 -> 07:59:20**.

**THE FORWARD WALK, Joe 1004:**
> *"walk forward to a opposing-dr g5Mage oob and keep walking to the g5Mage reversal, wob 2. this is
> the forward-walked extrema"*

- `wob 2` matches `rev_wob` 2 in v3_config, so `jig._mage_rev` takes it unchanged.
- **NO CAP** on how far forward it walks. None given, and none is to be invented.
- **THE WALK DEFERS THE DECISION, AND THE TRADE MOVES WITH IT.** Joe 1004, correcting me after I
  called the forward walk non-causal because 07:59's verdict only lands at 08:05: *"I disagree. my
  words, 'the walk walks', therefore we trade at 08:05"*. The signal bar is NOT the decision bar.
  Every bar the walk reads is the current bar, so there is **no lookahead anywhere** - the entry
  simply happens later than the octo-sig that started the walk.
  **MY ERROR:** I assumed a gate must resolve on the signal bar. It does not.

### mtd STEP 2 — the micro mage-cascade, and the two routes

> *"at the chosen (lookback or forward-walked) extrema, measure the Mage values for the 4 `mtd lines`"*

| route | condition | outcome |
|---|---|---|
| **mtd.r1** | *"all 4 Mages are oob, denoting that there is a coil ready to release"*. **OPPOSING-dr oob**, Joe 1004 | *"delegate to the r-cascade and mage-cascade branch"* = **branch D** |
| **mtd.r2** | *"the 3 Mages above g5 create a cascade towards dr"* - g15, g30, ws1. **NET**, not monotone, Joe 1004 | *"confluence a octo-signal that faces dr. eg, +1dr: confluence only a LONG trade octo-sig, -1dr confluence only a SHORT trade octo-sig"* |

**mtd.r2's trade side is CORRECT AS WRITTEN** and follows the one cascade rule above: towards dr on
dr +1 is a LIFT, and a lift confluences a LONG. See the locked-in cascade section.

### STILL OPEN

| open | detail |
|---|---|
| the forward walk's no-find outcome | Joe 1004: *"let's review no-find when it appears in the walk"*. Deferred by him, not by me |
| whether `lazy-g` / `lazy-g-conf` is the final split | his word is *"maybe"* |
| the 07:59 testcase | he says mtd blocks it. Not yet verified - that is the next measurement |
