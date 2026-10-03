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
| | *"Mage 'moving away from dr' is the load bearing mech - if Mage is moving away from dr in branch A, lazy-g is predicting a pxs reversal"* |
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

## KNOBS TO SWEEP LATER

| knob | current | Joe's words / status |
|---|---|---|
| **branch B's fence** | unset | *"which fence, oob or mage-fence, is a knob to sweep later"*. oob is 15/85, the Mage fence is 25/75. **On the 6 branch B octo-sigs of 10-02 the choice FLIPS the sign**: at oob 4 qualify for −282.09, at 25/75 five qualify for +52.99, and the whole difference is the 12:58 trade (+335.08), which breaches oob at g15 (77.07) and passes 25/75 |
| **the anchor walk-back's pop-back tolerance** | 1 bar | the minimum that reaches Joe's confirmed 01:43:00 anchor. Not his number - he has not set one |
| the ladder cap | ws12 | **his**, from *"between g5 and ws12"*. Listed here only because a wider ladder is a thing a sweep could ask |
| Q1's "bumpy" threshold | none | no threshold is applied. Net direction only, as he specified |
| **`LAZY_G_WSF_TF_SPLIT`** | **ws5** | Joe 1003, branch C: *"I don't yet have a clean definition of the split between lower and higher wsf lines. we will set it to ws{knob:5}"*. **Whether ws5 itself sits in the LOWER or the HIGHER group is not stated** |
| **branch C's "common reversal" window** | **unset** | Joe: *"needs a window size that I don't have. it will be somewhere around 18:50"* |
| branch C's "in-fence" | unset | *"gone in-fence"* - same oob-or-Mage-fence question as branch B, and not separately ruled |

## WHAT IS MEASURED SO FAR — 10-02, the 25 live octo-sig

| population | trades | wins | net | per trade |
|---|---|---|---|---|
| all octo-sig | 25 | 6 | −1,046.86 | −41.87 |
| **branch A qualifies (Q1 AND Q2)** | **11** | 2 | **−798.97** | **−72.63** |
| branch B population (Q1 fails) | 6 | 3 | +226.25 | +37.71 |
| Q1 fires but no r swap — **UNNAMED by Joe** | 8 | 1 | −474.14 | −59.27 |

- branch A marks the octo-sigs that fail. Branch B's population is where the octo-sig works.
- **effective-n is tiny**: 11 / 6 / 8 on ONE day. Nothing here is a rate.
- the 8-trade group satisfies Q1 and not Q2, so it is neither branch A nor branch B. It has no name
  and no mech.
