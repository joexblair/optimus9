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
