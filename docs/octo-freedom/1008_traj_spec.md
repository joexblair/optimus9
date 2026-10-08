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
