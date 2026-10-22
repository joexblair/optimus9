# octo-v3 — the spec as Joe has ruled it, 1018

Greenfield. Nothing is carried from octo2 unless Joe names it. Every line below is his ruling or a
measurement; where a concretion is unruled it is listed in §9 and the code leaves the column NULL.

## 1. The knobs he named

| the knob | default | what it is |
|---|---|---|
| `v3_min_tf` | 1 (60 s) | the TF controlling the signal cadence |
| `v3_rmom_fnc` | 80 | the fence testing whether an `r` is close enough to oob to be predicted |
| `v3_mage_fnc` | 75 | the fence testing whether a `Mage` is close enough to oob to be predicted |

Both fences are MIRRORED, Joe 1018 *"1 and 2: yes"*: 80 reads (20, 80) and 75 reads (25, 75), the
same shape as `momo_fence_r` 17 -> (17, 83). The TRADE SIDE picks the end, set once at the open -
a LONG hunts the HIGH oob, a SHORT the LOW (Joe 1016). oob is always 15/85.

## 2. The wobs, each anchored to a value he had already banked

| the wob | bars | secs | what it gates | where it came from |
|---|---|---|---|---|
| oob dwell | 3 | 15 | ws{min_tf}b's oob run, the required leg | his `WS1MR_DWELL` |
| test-point xwob | 4 | 20 | ws{min_tf}Mage's ib hold | his `WS1MR_HOLD`, ruled 0911 for this cross |
| step1 wob | 3 | 15 | an `r` RETURNING to ib or in-fence | Joe 1018 *"6 step1's wob: 3"* |
| r xwob to oob | 8 | 40 | an `r` run crossing TO oob counts as an excursion | Joe 1018 |
| x-cross xwob | TF x 1.5 | — | the x cutting its targets | Joe 1018 |
| away confirmation | 12 | 60 | the leader's direction must hold | Joe 1018 *"walk forward 12 bars"* |

## 3. The chain

1. **the arm / required leg** — ws{min_tf}b reaches oob on the trade's side, dwell 3. REQUIRED,
   Joe 1018 *"3: required"*. Nothing fires before it.
2. **the test-point** — ws{min_tf}Mage crosses to ib, xwob 4. His marker verbatim.
3. **the extrema** — walk back to look forward, same side, for the ws{min_tf}Mage extrema.
   `jig.mage_cascade_bar` mode `extrema`, 48-bar coarse gap, his own 1017 producer.
4. **rider-tf** — set AT THE FIRST test-point: the highest wsf `r` in oob; else the highest
   mom-true wsf `r`; else defer to routing, which is not built. Joe 1018, 5a. Bound to wsf 1-12.
5. **mrider-tf** — the highest wsf `Mage` BETWEEN the fence and oob. NOT LATCHED, Joe 1018:
   *"mrider's are not latched - they qualify only between ex-fence and oob"*.
6. **the race** — every `r` that is oob at the test-point races to its OWN ib, step1 wob 3. The
   WINNER carries lineage (Joe 1018 *"#12, the race's winner"*) and a tie goes to the HIGHER TF
   (*"#13, the higherTF is the tie breaker"*). THE RACE WINNER AND THE RIDER ARE DIFFERENT LINES -
   Joe 1018: *"this is important for the lineage spec, and the octov3 spec"*.
7. **step2** — at the winner's step1 bar ONLY (*"8, only on the step1 bar"*), winner+1 or winner+2
   must be ex-fence on the SAME side (*"7, same side"*). Qualifies -> the baton passes.
   Disqualified -> EXHAUST.
8. **the mrider override** — EXHAUST does not end the leg while an mrider is qualified. Joe 1018:
   *"when they are qualified, we predict continuance and walk to the next testpoint"*.
9. **the verdict** — the next test-point same-side -> the prediction held. Not same-side -> exit,
   and the exit races MAE: above 1.1 the leg's MFE is set to 0.

## 4. The hanging-excursion problem and its three race conditions

Joe 1018: *"the problem with an r line positioned between ex-fence and oob: there's the potential
for 'cross from oob to ib' to never happen on this excursion - the code will just keep walking and
land on a stop"*. Three conditions get around it:

| the condition | what it reads |
|---|---|
| (a) | the faster `r` lines that have ALREADY been oob in this excursion are moving `away` from the test-point side, making a matryoshka pattern. They are the WHIP leading the baton-passee |
| (b) | the "in between" `r` line returns to in-fence, step1 wob 3 |
| (c) | an x-cross, xwob TF x 1.5, that cuts through ws{TF}r while ws{TF}r IS oob AND through ws{TF+1}r while ws{TF+1}r is NOT oob |

(c) IS A SIMULTANEITY, Joe 1018: *"'TF oob' while 'TF+1 between oob and ex-fence' while 'tf+1
x-crosses both TF and TF+1' = EXHAUST. without an mrider, the leg ends and SHORT opens"*. The x is
the TF+1 line's, and it cuts the values of BOTH TF and TF+1.

THE BATON-PASSEE'S OWN DIRECTION IS NOT A CONDITION. Joe 1018: *"if anything, ws4r printing away
is just further confirmation ... if the baton-passee wants to agree or disagree with the faster
lines exhibiting matryoshka behaviour, it makes no difference to the faster lines - they're still
the whip, the leader of the baton-passee that's stuck between 2 fences"*.

## 5. THE SAMPLING WIDTH DEFECT, found 1018 and ruled

`traj`'s block is `W_VOTE_TRAJ_MULT 2 x TF x 12` bars, so ws3's block is 72 bars = 360 s. The
2026-09-03 00:06:00 reading proved that unusable for (a):

| ws3r at 2026-09-03 00:06:00 | 20 s samples | the 6 min samples |
|---|---|---|
| dir | **-1** | +1 |
| travel | **-14.6982** | +13.6980 |

ws3r went 94.65 -> 84.35 inside one 72-bar block, so a -14.28 fall registered as a +8.37 rise: the
sampler compared a 6-min-old sample to a 12-min-old one and never saw the turn. Joe 1018: *"there
has to be a flaw somewhere - ws3 fell under 85 at 00:06:00, so it can't be +1"* / *"these are fast
lines - the samples need to be closer"*.

At 20 s samples every line reads away, confirmed for all 12 bars:

| the tf | ws{tf}r at 00:06:00 | dir at 20 s | travel at 20 s | dir at 2 x TF x 12 | that block |
|---|---|---|---|---|---|
| ws1 | 20.11 | -1 | -4.3525 | -1 | 120 s |
| ws2 | 71.43 | -1 | -14.2857 | -1 | 240 s |
| ws3 | 84.35 | -1 | -14.6982 | **+1** | 360 s |
| ws4 | 82.49 | -1 | -3.2362 | **+1** | 480 s |

This is register task #60, *"wsf stall sampling width, timeframes 1 to 8"*, surfacing in (a).

## 6. The worked leg — 2026-09-02 22:16:30 LONG

| seq | the arm / oob leg | the test-point | the extrema | rider | mrider | race winner | step1 | step2 | the print | predict | next tp | same side |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-09-02 23:06:20 | 2026-09-02 23:15:30 | 2026-09-02 23:11:35 | ws2 | ws1 | ws2 | 2026-09-02 23:16:00 | no | EXHAUST | CONTINUANCE | 2026-09-03 00:00:40 | YES |
| 2 | 2026-09-02 23:48:40 | 2026-09-03 00:00:40 | 2026-09-02 23:56:45 | — | ws12 | ws3 | 2026-09-03 00:06:00 | YES | BATON PASSES | BATON | 2026-09-03 00:31:05 | NO - exit |

seq 2's departures under r xwob 8, which discards both of ws4r's touches (3 bars and 6 bars):

| the order | the line | the departure |
|---|---|---|
| 1 | ws1r | 2026-09-02 23:58:00 |
| 2 | ws2r | 2026-09-03 00:06:00 |
| 3 | ws3r | 2026-09-03 00:06:00 |

the three race conditions on seq 2, all measured from the arm 2026-09-02 23:48:40:

| the condition | fires at | secs from the arm | vs the step1 bar |
|---|---|---|---|
| (c) the simultaneity, ws4x under both ws3r and ws4r, held 6 | 2026-09-03 00:04:40 | 960 | -80 s |
| (b) ws4r returns under the fence 80, wob 3 | 2026-09-03 00:06:25 | 1065 | +25 s |
| (a) all three leaders away, 20 s samples, 12-bar confirmation | 2026-09-03 00:06:00 | 1040 | 0 s |

(c) fires first and 80 s BEFORE lineage's own step1 bar. The mrider at that bar is ws1 and ws12, so
the leg continues rather than ending - ws12Mage claiming mrider is what keeps it alive.

THE OUTCOME CHECK, lookahead and not part of any causal read: ws4r never exceeds its 82.49, falls
to 1.59, and regains oob only at 2026-09-03 01:08:30, 3,750 s later.

## 7. ws12Mage and mrider

Joe 1018: *"ws12 can't claim mrider is this scenario, because there are no faster Mages claiming
mrider. this is not the only reason to block ws12 as mrider, but I don't yet have a well-formed
definition to explain why ws12Mage can't be the mrider -- we'll evolve this definition by building
the chain"*.

WHAT HE DOES READ THERE, his words, recorded and NOT coded: *"ws12Mage can claim weakness though:
-all faster lines except ws1 are high oob -ws4 to ws1 are all below their extrema, indicating a
reversal --a revesal is the symptom of weakness"*.

## 8. x-cross direction

HIGH oob -> x crosses UNDER its target. LOW oob -> x crosses OVER. Read the OOB SIDE, never `dr`.
Joe 1018, correcting a 0821 phrasing that keyed on `dr` and inverted this reading on a HIGH-oob
excursion inside a LONG.

## 9. Unruled — every one is a NULL column until he rules it

| # | the question |
|---|---|
| 9 | which anchor the leg's MAE/MFE runs from - the trade open or the test-point that started the leg. On seq 2 that is 0.2454 against 1.5761 |
| 10 | rider-tf at the SECOND test-point - re-seed or carry |
| 11 | step2 when winner+2 falls outside wsf, as it does for a winner at ws11 or ws12 |
| 14 | why ws12Mage cannot claim mrider - §7 |
| 19 | how many of the already-oob leaders must read away. On seq 2 all three do at 20 s samples, so this example does not bind |
| 23 | the sampling block: flat 20 s for every TF, or still scaled - 20 s is what §5 measured |

## 10. The sampling width, banked 1018

Joe 1018: *"23: scaled. sweep it to find the sweet spot. ie, where it still creates a -1 for
ws3r"* then, on the caveat that it is one excursion and one line, *"noted. to be adjusted as
needed - bank your suggested width"*.

    v3_traj_k = 12       # BARS of block per TF-MINUTE. block = v3_traj_k * TF bars

| the tf | the block at K 12 | secs |
|---|---|---|
| ws1 | 12 bars | 60 |
| ws2 | 24 bars | 120 |
| ws3 | 36 bars | 180 |
| ws4 | 48 bars | 240 |
| ws12 | 144 bars | 720 |

MINE, AND WHY THIS VALUE: K 12 is the largest block at which ws3r still reads -1 at
2026-09-03 00:06:00 - the knee is between K 12 (travel -8.9040) and K 13 (+0.6994). The widest
width that still sees the turn is the one that keeps the most history, so the knee itself is the
anchor rather than a preference.

WHAT IT IS NOT: a swept population. One excursion, one line. From 00:06:05 onward EVERY K from 1
to 15 reads -1, so the knob buys 5 s of earliness on the first bar and changes no verdict after it.
Joe has it as adjustable, not ruled.

THE OLD FORM IT REPLACES: `W_VOTE_TRAJ_MULT 2 x TF x 12` = K 24, which put ws3's block at 360 s and
printed +1 through the fall.

## 11. The ws1r / ws2r walk-forward — a test-point with no oob `r` line

Joe 1019, after LEG 1 closed empty at 2026-09-03 01:10:20: *"LEG 1 closed to early - it highlights
the need to treat ws1r and ws2r differently"*.

THE MECH, his words across three messages:

> at a testpoint: if ws1r and ws2r have trajectory towards testpoint side, walk forward until
> either crosses to oob, or crosses from ex-fence to infence (the backup)

> the mech: at test-point, walk forward on both ws1 and ws2 if they are showing trajectory towards
> test-point side. both have the chance to reach oob. if either leaves their fence and recturns to
> infence (with xwob), then exhaustion can be declared

> my returning to infence rule doesnt give ws2 a fighting chance.  drop ws1 from the infence rule

> now that ws2r has made it oob, the mech disarms so that lineage can take over.  this needs to
> happen when ws2r crosses to oob

So:

| the leg | what it watches | the wob |
|---|---|---|
| the gate | ws1r AND ws2r trajectory towards the test-point side, K 12 blocks | — |
| ws1r reaches oob | the good outcome | r xwob to oob, 8 |
| ws2r reaches oob | the good outcome AND **THE DISARM** | r xwob to oob, 8 |
| ws2r leaves its fence and returns to in-fence | the ONLY exhaustion | the r return wob, 3 |
| ws1r leaves its fence and returns to in-fence | **NOT IN THE RULE** - dropped, it did not give ws2 a fighting chance | — |

THE DISARM IS WHAT ENDS THE MECH. On ws2r crossing to oob the walk-forward stops and lineage owns
the leg; the ws2r in-fence exhaustion is no longer armed after it.

## 12. The 2026-09-03 01:07:00 LONG, walked end to end

| the bar | what happens |
|---|---|
| 2026-09-03 01:07:00 | the arm - ws1b high oob, 42 bars |
| 2026-09-03 01:07:25 | the ws1Mage extrema, 119.5676 |
| 2026-09-03 01:10:20 | the test-point, ws1Mage ib xwob 4, knowable 01:10:35. NO wsf r is oob |
| 2026-09-03 01:10:20 | ws1r 82.86 dir +1, ws2r 67.97 dir +1 - both towards, so the walk goes forward |
| 2026-09-03 01:11:05 | ws1r reaches oob at 85.47 |
| 2026-09-03 01:14:00 | ws2r reaches oob at 92.43 - **THE MECH DISARMS, lineage takes over** |
| 2026-09-03 01:22:00 | ws2r crosses back to ib at 81.32; ws3r 93.00 -> BATON PASSES to ws3 |
| 2026-09-03 01:27:00 | ws3 -> ws4, ws4r 89.68 |
| 2026-09-03 01:32:20 | ws4 -> ws5, ws5r 91.72 |
| 2026-09-03 01:40:00 | ws5 -> ws6, ws6r 97.62 |
| 2026-09-03 01:45:25 | ws6 -> ws7, ws7r 87.54 |
| 2026-09-03 01:47:10 | ws7 EXHAUSTS - ws8r 75.41 and ws9r 64.54 both under 80 |
| 2026-09-03 01:47:10 | mrider ws12 qualifies, so the leg continues |
| 2026-09-03 01:49:15 | the next test-point is LOW side - not same side, so the leg EXITS and a SHORT opens |

THE DISARM RESOLVES THE ORDERING QUESTION I RAISED. Without it, ws2r's ib cross at 01:22:00 and its
fence return at 01:22:05 would be a 5 s race. The disarm fires at 01:14:00, 480 s earlier, so the
fence-return rule is not armed when either bar arrives and there is no race to adjudicate.

## 13. mrider excludes ws1 and ws2

Joe 1019: *"exclude ws1 and ws2 from mrider"*. The candidate band is ws3-ws12.

Measured effect on the 2026-09-03 00:32:00 SHORT: mrider was ws1 at the test-point and ws1/ws2 at
the step1 bar; both become NONE. step2 qualified on its own there, so the leg was unaffected.

## 14. away / toward — the Mage-perspective rule

Joe 1019, verbatim:

> if the TF's mage is above 50 then the perspective is HIGH - a line climbing is toward, a line
> falling is away
> inverse for TF's Mage under 50: climbing is away and falling is toward

| the input | where it comes from |
|---|---|
| the perspective | the TF's own Mage against 50. Above = HIGH, at or below = LOW |
| the direction | the MAGE's trajectory. Joe 1019: *"Mage is the best source of direction - there's no lag"* |
| a flat Mage | holds the previous tag. Joe 1019: *"35 - hold the previous tag"* |
| the sampling | K 12 bars per TF-minute, S10 |

Built as `jig.away_toward` and `jig.away_toward_series`. EVERY `r` LINE IS TAGGED, Joe 1019: *"its
important to tag the `r` lines with away or toward"*. The tag is read on the LINE'S OWN travelling
side, not the leg's - Joe 1019: *"33: the lines own travelling side"*.

Measured, ws1-ws12, 326,196 samples at every 60th bar: TOWARD 53.08%, AWAY 46.84%, the Mage flat
and the previous tag held on 0.08%. The flat rate rises with the timeframe, ws1 never to ws12 0.21%.

A RULE OF MINE THAT FAILED, recorded: take the side whose `held` counter is smaller. It read ws1r
right and ws5r backwards - ws5r was falling 92.58 -> 63.44 and it called the travel HIGH, because
`held` counts bars since a line TURNED OFF an extreme, which is staleness and not direction.

THE dr COLLISION, flagged: `momo_core`, `momo_gpu.extrema_walk` and `report_wsf_bar.heading` all
read dr -1 as the LOW side, while the banked trade frame has dr -1 = LONG = the HIGH oob. Opposite.
Anything carrying a value between them must flip it.

## 15. The END validation, when the EXHAUST lands on the wrong side

Joe 1019: *"the 01:47:20 EXHAUST has not landed on the target-side, so we need to validate the END
before letting it print"*.

THE GATE, his words: *"for this 'EXHAUST on the wrong side' to qualify, ws1Mage must be ex-fence on
the counter-target-side"* and *"END has printed when ws1Mage is on counter-target side, and ws1Mage
is counter-target side ex-fence"*. Both legs, read at the END print.

| the step | what it does |
|---|---|
| 1 | the gate - ws1Mage on the counter-target side of 50 AND ex-fence on it |
| 2 | the mage-cascade must print a verdict toward the target side |
| 3 | ws1r is walked forward until it crosses to in-fence, or - if it reaches oob - until it returns to ib |
| 4 | the cascade is RETESTED at that bar. Still toward the target -> the trade stays open. Not -> END, and walk to the next arm before opening the next trade |

WHILE THE CASCADE POINTS AT THE TARGET SIDE, A COUNTER-SIDE TEST-POINT CANNOT FIRE. Joe 1019:
*"because the mage-cascade is towards target-side, the counter-side test-point cannot fire"*. A
TARGET-side test-point fires on its own merit and the cascade has no say in it.

Worked on the 2026-09-03 LONG:

| the bar | what happened |
|---|---|
| 2026-09-03 01:47:10 | ws7 EXHAUSTS. ws1Mage 18.3320 - counter-side and ex-fence, so the gate opens |
| 2026-09-03 01:47:20 | the cascade prints `up`: the ws3-ws12 cluster, 10 lines, diff -58.1334 |
| 2026-09-03 01:49:00 | ws1r drops 9.47 in one bar to 16.27, through the low fence 20 |
| 2026-09-03 01:49:10 | ws1r reaches the low oob at 14.65 |
| 2026-09-03 01:49:20 | it returns to ib at 15.34. The walk ends - 120 s after the exhaust |
| 2026-09-03 01:49:20 | the cascade RETESTS `up`, diff -56.8345. THE LONG STAYS OPEN |
| 2026-09-03 02:00:40, 02:02:00, 02:02:55 | three LOW-side test-points, all SUPPRESSED |

## 16. The arm is consumed on claim

Joe 1019, on seeing a test-point with no ws1b run behind it: *"please fix that"* / *"43: 6"* /
*"44. confirmed"*.

| the rule | value |
|---|---|
| the ws1b oob dwell | **6 bars = 30 s** |
| which arm a test-point may claim | the MOST RECENT qualifying ws1b oob run at or before it |
| reuse | none. An arm is consumed by the first test-point that claims it |
| a test-point whose most recent arm is consumed | is NOT a test-point |

THE BACKWARD REACH WAS MY BUG, recorded: a first implementation let a test-point skip past consumed
arms to find an older unclaimed one, which had 2026-09-03 02:19:00 claiming an arm from 00:04:50,
8,050 s back. The arm must be the most recent one, full stop.

Measured on the 2026-09-03 LONG, HIGH-side test-points in 01:07:00 to 03:30:00: 14 ws1Mage ib
crosses, **9 valid**. Every valid one sits 65 to 330 s behind its arm; every dropped one sits 435 to
3,305 s behind an arm already claimed. Dropped: 02:19:00, 02:25:55, 02:29:00, 02:56:40, 03:14:50.

## 17. v3-class-pred1 — the momentum-holding read

Joe 1019 named it, after reading the 02:19:00 ladder: *"mrider qual and r mom-true are all signs of
predicted momentum, and in this report we have most of our first 9 lines showing a drive to walk
higher ... a mech that can read this data and see the lines are holding their momentum would be
excellent"*.

| the part | my label | what it is |
|---|---|---|
| the per-line flag | `pred1_sign` | the line's Mage is in the mrider band, OR its r is mom-true |
| the run length | `pred1_reach` | the contiguous run of carriers anchored at ws1 |
| the gap tolerance | — | 2 misses, and they may NOT be consecutive. Joe 1019: *"2, but they can't be consecutive TFs"* |
| the threshold | — | NOT SET. See below |

At 2026-09-03 02:19:00: carriers ws1,2,3,4,6,7,8,9,11 - 8 of the first 9. `pred1_reach` is ws4 at
0 gaps, ws9 at 1, **ws11 at 2 non-consecutive** (the misses are ws5 and ws10).

The distribution, LONG high side, every 60th bar, 27,133 samples:

| the reach | share | at this or higher |
|---|---|---|
| ws12 | 1.75% | 1.75% |
| ws11 | 0.62% | 2.37% |
| ws9 | 0.93% | 4.13% |
| ws6 | 2.21% | 9.48% |
| ws4 | 4.86% | 18.13% |
| ws1 | 15.87% | 56.42% |
| none | 43.58% | 100.00% |

WHAT AN INCORRECT THRESHOLD DOES, measured on the leg's own 8 same-side test-points: ws4 and ws6
both HOLD 7 of 8, so the mech stops discriminating; ws12 RELEASES at 02:19:00, the bar the ladder
reached ws11, which is the early-close fault again. ws6 -> ws8 is where the behaviour changes, 7 of
8 holds becoming 5 of 8. The band ws8 to ws11 behaves identically on this leg, so this leg cannot
separate them.

### IT IS NOT A PEAK DETECTOR. TESTED AND FAILED.

Joe 1019: *"02:58, where all columns are RELEASE, is literally the peak. so whatever key created
that, needs to be tested on other swings. if it produces the same results then we're onto a
winner"*. It does not.

| the comparison | mean reach | median | share <= ws3 |
|---|---|---|---|
| AT the 1,727 swing highs, 0.9 pct pivots | 2.86 | 2.0 | 67.9% |
| a baseline sample of 1,357 bars | 1.79 | 1.0 | 83.9% |

`pred1_reach` is HIGHER at swing highs than at ordinary bars, not collapsed. A low reach is more
common AWAY from a peak. The ws2 at 02:58:45 is the commonest reading on the tape, not a key.
The nearest 0.9 pct high pivot to 02:58:45 is 02:57:25, 80 s earlier.

The momentum-HOLDING claim is untouched by this - it is a different question and is not yet tested.

## 18. Side detection relies on ws1Mage only

Joe 1019, closing the pivot-estimate exercise: *"all of those times were pivot estimates. there's
no basis for them. it's ok, we'll park this for now. the key thing to be banked is the reliance
only on ws1mage for side detection"*.

| what ws1Mage decides | where |
|---|---|
| the test-point marker and ITS SIDE | `ws{v3_min_tf}Mage` crossing to ib, xwob 4. The side of the oob run it left IS the side |
| the leg's own side | set once at the open, and compared against each test-point's side |
| the counter-target END gate | ws1Mage on the counter side of 50 AND ex-fence on it |

## 19. The away/toward PERSPECTIVE moved to ws2Mage, and why

Joe 1019: *"use ws2Mage instead, before we look at a wob"*.

THE FAULT IT FIXED. ws1Mage crossed 50 five times in 80 s around 2026-09-02 23:31, and because the
perspective is shared by the whole ladder, every one of the twelve tags inverted on each crossing
with NO line changing direction:

| the bar | ws1Mage | persp | the 12 Mage dirs | TOWARD | AWAY |
|---|---|---|---|---|---|
| 23:30:55 | 69.11 | HIGH | -1 -1 +1 +1 +1 +1 +1 -1 +1 +1 +1 +1 | 9 | 3 |
| 23:31:00 | 47.34 | LOW | -1 x11, +1 | 11 | 1 |
| 23:31:10 | 51.55 | HIGH | -1 x10, +1 +1 | 2 | 10 |
| 23:31:15 | 43.14 | LOW | -1 x12 | 12 | 0 |
| 23:31:25 | 53.23 | HIGH | -1 x6, +1, -1 x3, +1 +1 | 3 | 9 |

Joe 1019, on seeing it: *"that's a very fast flip. it questions the sampling"*. The sampling of the
DIRECTIONS was fine - ten of twelve held -1 throughout. The perspective line was the fault.

| the perspective line, 23:05 to 02:30 | 50-crossings | tag-count flips | min | max |
|---|---|---|---|---|
| ws1Mage | 48 | 179 | 0.64 | 119.57 |
| ws2Mage | **20** | 161 | 15.35 | 119.62 |
| ws3Mage | 20 | 166 | 18.22 | 124.58 |

Under ws2Mage the 23:31 window holds HIGH throughout - ws2Mage spans 57.53 to 81.49 there, never
near 50 - and the count reads what the directions say: 11 or 12 AWAY steadily. Neither reference
bar moves: 23:05:55 stays 11/1 with reach ws1, and 2026-09-03 02:19:00 stays 12/0 with reach ws11.

WHAT IS STILL OPEN. ws2Mage crosses 50 twenty times in the same window, so the inversion is rarer
but not gone - the 2026-09-03 00:21:00 bar flips 0/12 to 12/0 with no line turning. 161 of the
flips remain, and they are the count oscillating around 6/6 rather than the perspective inverting.
A wob on the 50 crossing is Joe's next candidate: *"before we look at a wob"*.

## 20. The AWAY>=7 excursion count, measured and PARKED

Joe 1019 asked for the flip to AWAY >= 7 after each of eight times, then withdrew the times: *"all
of those times were pivot estimates. there's no basis for them"*.

What the measurement left behind, perspective ws2Mage, 2026-09-02 23:00 to 2026-09-03 05:40:

| the reading | value |
|---|---|
| AWAY >= 7 excursions | 88 |
| of those, 12 bars or longer | 20 |
| the longest | 147 bars = 735 s, from 2026-09-03 00:07:50 |
| the first sustained flip after 00:00 | 00:07:50, after a 4-bar false start at 00:07:15 |

AN ARM GATE WAS TRIED AND RETURNED NOTHING. Gating an excursion to start at or after the
test-point's arm left 0 of 88 on all eight times, because the arm-to-test-point window is seconds
to minutes wide and no excursion starts inside it. Recorded so it is not retried blind.

THE PIVOT TIMES COULD NOT BE REPRODUCED. Joe's *"~01:59 arm for the 02:09 test"*: at 01:59:00 ws1b
is 21.71, in bounds and not an arm; the first LOW ws1b run reaching dwell 6 is 02:01:35; and there
is no ws1Mage ib cross at 02:09 at all - the nearest are 02:02:55 LOW and 02:19:00 HIGH. 02:09 is
itself an arm in the data, ws1b 12.14 LOW oob for 7 bars.

## 21. THE COLLISION TO RESOLVE

S18 banks side detection on ws1Mage. S19 banks the away/toward perspective on ws2Mage. Both are
Joe's words from the same exchange. They are only consistent if "side detection" means the
test-point's side and the leg's side - NOT the away/toward perspective, which is a different
reading of a different question. Recorded as a question rather than resolved, because choosing
between them is a value call.
