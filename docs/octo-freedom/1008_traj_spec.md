# `traj` FOR A SLOW LINE — THE SPEC AS JOE RULED IT, 1008

Joe 1008, verbatim across four messages:

> *"there's an established mech for `traj` - see if you can track it down before we build"*
> *"it was designed for lower wsf lines, so 2 minutes worked well. now, we're apply to a much
> larger and slower line so the 2 minutes becomes less relevant. I'm proposing we use
> ({knob:2,'TRAJ_MULTI_TF_SAMP'} * TF-width) as a replacement"*
> *"important note on the lookback sampling - if there is a direction changed between the samples,
> we follow the tail"*
> *"fix the sampling, drop min_travel"*
> *"if the tail is flat, like we just saw in 15:26, then the mech needs to defer to the earlier
> samples"*
> *"'the tail' is the last mile. for the 13:33 decision, the tail could be from 13:00 to 13:33
> (this is another knob to add - your call on the label)"*
> *"thinking ahead: if the line has reversed during the TF*2.5 lookback, the tail must be
> completely inside the reversed 'section' of the line"*

## THE BASE MECH, UNCHANGED

`optimus9/compute/rule2_trajectory.py`, Joe 0924, task #22's first mechanism.

| the piece | value | provenance |
|---|---|---|
| the question | is this line travelling towards `dr` | Joe 0924 |
| the method | find the **dr-opposed extrema** behind the bar by a block walk, then measure travel from it | Joe 0924 *"look back across the line to find its dr-opposed extrema"* |
| `block` | 60 bars = 5 min | `AF_BLOCK`, `jig.py:310`, Joe 0924 *"look back in 5 minute windows"* |
| the walk's stop | the first block that does not improve the running best; empty blocks are SKIPPED | Joe 0921 |
| causality | every bar read is strictly before the test bar; the test bar is excluded | asserted in the module |

## WHAT CHANGES, 1008

| # | the change | from | to |
|---|---|---|---|
| 1 | the travel-duration threshold | `min_bars` 24 bars = 2 min, flat | **`TRAJ_MULTI_TF_SAMP` x TF-width** |
| 2 | the magnitude threshold | `min_travel`, unset at 0.0 | **DROPPED.** The sampling diff carries size and sign |
| 3 | which extrema wins when the samples change direction | the walk's running-best, i.e. the oldest improving extreme | **the TAIL** — the last mile |
| 4 | a flat tail | returned travel 0.0000 and the mech read NEITHER | **defer to the earlier samples** |
| 5 | a reversal inside the lookback | not considered | **the tail must sit wholly inside the reversed section** |

## WHY `min_travel` IS DROPPED, MEASURED

- it existed to filter dust: the module records `-7.105427357601002e-14` passing as trajectory on
  09-02, and 10% of 08-22's 440 ws60r travels are under **0.1678** r-points.
- the dust comes from the stop rule, not from the line. At **15:26:15** ws60r held **63.9604 for 124
  consecutive bars**, so blocks 1 and 2 tied, the walk stopped 10 min back, and travel was exactly
  **+0.0000** — a reading with no sign for any threshold to act on.
- Joe's UP at 15:26 is the step **50.8287 at 14:55 -> 63.9604 at 15:05**, `+13.1317`, which the walk
  never reached.
- fix the sampling and the diff between samples IS the travel. Its size and sign come free, so a
  separate magnitude knob is a patch over the stop rule rather than a mechanic.

## THE KNOB LABELS

| label | role | value |
|---|---|---|
| `TRAJ_MULTI_TF_SAMP` | the lookback span, as a multiple of the line's TF-width | Joe: 2 (he also wrote 2.5 — see OPEN 1) |
| `TRAJ_TAIL_TF_SAMP` | **MINE, for review.** the tail's span, as a multiple of TF-width | unset — see OPEN 2 |

`last mile` is NOT used as a label: it is task #4, `the ELIF "last mile"` mechanic, deferred by Joe
and recorded at `wsf_walk.md:651` and `wsf_setup_model.md:1160`. Reusing it would collide.
Joe named this one **the tail**, so the knob carries that word.

## SEVEN THINGS STILL OPEN — none is mine to decide

| # | the open question | why it matters, with the number |
|---|---|---|
| **1** | `TRAJ_MULTI_TF_SAMP` is **2** or **2.5**? | Joe wrote `{knob:2}` and then *"the TF*2.5 lookback"*. On ws60r that is 120 min vs 150 min of lookback |
| **2** | the tail's form: a fixed multiple of TF-width, or **from the start of the current TF bar to now**? | Joe's example 13:00->13:33 is 33 min, and 13:00 is also the top of the hour, i.e. the start of the forming 60-min bar. At 13:05 the two readings give a 5 min tail and a 30 min tail |
| **3** | does `block` scale with TF-width too? | it is 5 min, chosen for ws1-ws3. On ws60r a 5-min block is 1/12 of one TF bar, and it is what stopped the walk at 15:26 |
| **4** | what counts as **flat** — exactly equal, or a tolerance? | a tolerance is `min_travel` under another name. Exactly-equal is knob-free and it is what 15:26's 124 identical bars would hit |
| **5** | *"defer to the earlier samples"* — step back one block at a time until a non-flat sample, or jump straight to the whole-lookback extrema? | at 15:26 one block back is still 63.9604; the first non-flat sample is ~21 min back at 14:55 |
| **6** | the **reversed section**'s boundary — which bar starts it? | the candidates are the extrema bar itself, the first bar of the run that broke the prior direction, or the last same-direction sample |
| **7** | the whole lookback flat — what does `traj` return? | ws60r held one value for 50 min at 15:05-15:55. A 120-min lookback would still contain the 15:00 step, a 30-min tail would not |

## THE WORKED BAR, FOR REVIEW

2026-08-22 13:33:50, ws12r 14.2367 (low oob), ws60r 33.5798.

| the candidate extrema | ts | ws60r there | travel to 13:33:50 | min since | which |
|---|---|---|---|---|---|
| the LOW the UP read uses | 13:21:05 | 30.8080 | +2.7718 | 12.8 | the older |
| the HIGH the DOWN read uses | 13:30:50 | 35.0885 | -1.5087 | 3.0 | the more recent |

Joe's eyeball read is **UP**, off the climb from ~19.6 at 11:00. Under `TRAJ_TAIL_TF_SAMP` giving a
13:00->13:33 tail, the tail contains the 13:21:05 low AND the 13:30:50 high, so OPEN 5 and OPEN 6
decide which the tail reports.

## NOTHING IS BUILT

No code is written against this spec. Every ws60r number reported on 1008 - the 72.7%/36.2% pivot
separation, the 48-arm grid, the 40 gated pairs, the paired per-leg test and the 08-22..08-27 list -
used `step_dir`, the bar-to-bar reading Joe ruled out on 0924. All of it is void and must be
re-derived once the seven opens are closed.

---

# THE SEVEN OPENS, CLOSED BY JOE 1008/1009

| # | the ruling | status |
|---|---|---|
| 1 | `TRAJ_MULTI_TF_SAMP` — *"confirmed"* | the knob stands. Joe wrote **2** then **2.5**; both go in the sweep rather than one being picked |
| 2 | the tail's form — *"already covered"* | a knob, as a multiple of TF-width, truncated per #6. The "current forming TF bar" reading is OUT |
| 3 | *"5 minutes stays - it will catch more data to evaluate. this is also a knob"* | `block` 60 bars stays, and becomes a knob |
| 4 | *"exactly equal"* | flat = exactly equal. No tolerance, so no `min_travel` by another name |
| 5 | *"unsure - your preference"* | MINE: step back ONE sample at a time until a non-flat sample, staying inside the lookback. See below |
| 6 | *"the first sample that broke the prior direction, then confirmed on the following sample"* | the reversal is confirmed at sample i+1; the tail starts at sample i |
| 7 | the ws60Mage vs ws60r fallback, four cases | **SPECIFIED AND MEASURED — the model does not hold. See below** |

## THE AMBIGUITY #6 REMOVED, AND WHY IT MATTERED

Joe 1008: *"if the reversal happened 25 minutes before the event, then the tail is reduced to 25
minutes"*. So the reversal TRUNCATES the tail; it does not have to be contained by it.

Applied to RAW BARS this collapses to the reading Joe ruled out on 0924: ws60r makes **847 turns in
the 153 minutes** before 2026-08-22 13:33:50, the most recent at **13:33:45 — 5 seconds back**, so
the tail would truncate to one bar.

#6's *"the first SAMPLE"* is what prevents that. The mech runs on the 5-minute block samples, not
on bars: 847 raw turns become a handful of samples, and the block absorbs the wiggles. That is the
work `min_travel` was patching, which is why dropping it and fixing the sampling are one change.

## OPEN 5, MY DECISION, STATED SO IT CAN BE OVERTURNED

**Step back one sample at a time until a non-flat sample is found, and stop at the lookback bound.**

- it is the minimal rule: nothing new is introduced, and the lookback already bounds how far it goes.
- it preserves *"follow the tail"* — the NEAREST usable sample wins, not the furthest.
- the alternative, jumping straight to the whole-lookback extrema, discards the tail concept on
  exactly the bars the tail was invented for.
- at 2026-08-22 15:26:15 one sample back is still 63.9604; the first non-flat sample is ~21 min back
  at 14:55, value 50.8287, travel **+13.1317** — Joe's eyeball UP.

## OPEN 7 — THE SPEC IS CONSISTENT. THE MODEL IT RESTS ON IS NOT.

Joe's rule, in one line: **TRUE when the Mage's pull OPPOSES the oob side**, i.e.
`TRUE iff sign(ws60Mage - ws60r) == -(the oob side)`. All four of his cases agree with that, so
**the logic is not inverted** — checked case by case.

| ws60Mage vs ws60r | ws12r | Joe: does pxs reverse | Joe's RETURN | what the chain does |
|---|---|---|---|---|
| HIGHER | HIGH oob | no | FALSE | delegate to `>ws12r oob` |
| LOWER | HIGH oob | yes | **TRUE** | ws12r prints a trade signal on stalled / x-cross |
| LOWER | LOW oob | no | FALSE | delegate to `>ws12r oob` |
| HIGHER | LOW oob | yes | **TRUE** | ws12r prints a trade signal on stalled / x-cross |

**THE POLARITY HAZARD, NAMED:** Joe's `TRUE` is a REVERSAL answer. `rule2_trajectory.trajectory`'s
`True` is a CONTINUATION answer — "the line is travelling towards dr". They are OPPOSITE in sign.
Any single function returning both must negate one of them.

### THE TWO LINKS, MEASURED ACROSS 95 DAYS

| link 2 — *"pxs follows r"* | samples | sign(ws60r move) agrees with sign(pxs move) |
|---|---|---|
| 5 min ahead | 20,472 | **94.5%** |
| 15 min | 22,423 | **88.4%** |
| 30 min | 24,322 | **80.5%** |
| 60 min | 26,607 | 68.9% |
| 120 min | 26,875 | 69.0% |

| link 1 — *"the Mage is pulling r"* | samples | sign(Mage-r) agrees with sign(r move) | with \|Mage-r\| >= 10 |
|---|---|---|---|
| 5 min ahead | 20,311 | **50.7%** | 50.8% |
| 15 min | 22,245 | **50.6%** | 51.0% |
| 30 min | 24,128 | **50.7%** | 51.3% |
| 60 min | 26,391 | **49.7%** | 50.3% |
| 120 min | 26,647 | 51.1% | 52.4% |
| 180 min | 26,717 | 51.7% | 53.6% |

**Link 2 is strong. Link 1 is a coin flip**, including where the gap is widest.

### THE RULE END TO END, AT THE BARS IT WOULD FIRE ON

swing_detect 1.0% as the scorer, never an input.

| the bar | block | events | Joe TRUE | of those, DID reverse | Joe FALSE | reversed anyway | spread |
|---|---|---|---|---|---|---|---|
| the oob crossing | all | 3795 | 1723 | 39.6% | 2072 | 41.1% | **-1.5** |
| the oob crossing | fit | 1754 | 799 | 35.5% | 955 | 42.6% | **-7.1** |
| the oob crossing | hold | 2041 | 924 | 43.1% | 1117 | 39.8% | **+3.2** |
| the dwell-ending | all | 764 | 344 | 31.4% | 420 | 29.0% | **+2.3** |
| the dwell-ending | fit | 375 | 179 | 26.3% | 196 | 26.0% | **+0.2** |
| the dwell-ending | hold | 389 | 165 | 37.0% | 224 | 31.7% | **+5.3** |

- **the best spread is +5.3 points and the sign flips across the halves.** For scale, the void
  `step_dir` gate separated **36.4** points on the same events.
- the `TRUE mean pxs move against the oob side` is NEGATIVE on 11 of 12 rows, i.e. on the bars the
  rule calls a reversal, price on average kept going WITH the oob side.
- `ws60Mage == ws60r` exactly: **0 events**, so no tie case to rule.

### SO #7 IS SPECIFIED BUT NOT SUPPORTED

Nothing is built against it. The spec is recorded exactly as Joe wrote it, with the measurement
beside it, and the decision is his.
