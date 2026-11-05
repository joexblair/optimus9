# the matryoshka and the blast radius at the 2026-08-07 08:26:00 LOW cadence — MEASURED, nothing built

His 1105 ask: *"the lower lines are matryoshka, so ws7,8,9 are (literally) bound to their lead --how
would you code the matryoshka and it's ability to lead via the blast radius?"*, plus his two ideas:
auto-call the 5-minute walk at a cadence event, and notify that walk of *"lift-off's incoming
flatness"*.

Source: `/home/joe/.claude/jobs/7c82535c/tmp/matry0826.py` -> `matry0826.out`. One cadence event,
n = 1. The leg is the 2026-08-07 06:48:10 SHORT, target side LOW, stopped 12:11:35 at -1.100 with
the MAE 1.1 stop ON.

## HIS TWO WORDS HAVE HOMES, AND ONE HAS A SETTLED TEST THE CODE NEVER GOT

| the word | his words | where |
|---|---|---|
| matryoshka | *"a lower TF (~1 to ~4) r line will always stall or curl before the higher TFs ... a per-TF falling dominoes effect. ie, the LTFs are leading the way"* | `docs/wsf_setup_model.md` 3.12, 0824 |
| blast radius | *"each r line has a small 'blast radius'. this is why ws3 reacted to ws2, and it's also why ws5 will react to ws4"* | `docs/wsf_setup_model.md` 3.21.2, 0825 |
| the link | *"this is the mechanism under the matryoshka order in 3.12"* | same section |

His blast-radius test, from `docs/octo-freedom/fdm_spec_VERBATIM.md`: the lines within
`fdm-blst-rad-conf-tfs` 5 TFs of the highest ex-20/80-fence TF; 4 of those 5 must have reversed
since the prior same-side cadence window's OPENING bar; a pass prints exhaust and sends the
rev-trade. `fdm-blst-rad-conf-tfs` does not exist as a knob and no blast-radius code exists in
`v4_fdm2.py` - its docstring records the deletion.

## WHAT THE 08:26:00 BOARD ACTUALLY SAYS

| the finding | the numbers |
|---|---|
| lines with a LOW lift-off stamp in [06:48:10, 08:26:00] | **29 of 30**. Only ws29r has none |
| so "has it reversed" over a 97-minute span | saturated. It cannot discriminate |
| the unbroken chain from ws1 | ws1..ws28, which is the same saturation |
| his blast-radius set, ws6..ws10 | **5 of 5 reversed, so his test passes and exhaust prints** |
| the caveat on that pass | at this origin almost every set of 5 passes. n = 1 |

**THE ORIGIN IS THE LOAD-BEARING GAP.** 08:26:00 is the FIRST same-side cadence event in its trade,
so "the prior same-side cadence window's OPENING bar" does not exist and I fell back to the trade
open - 97 minutes. His spec names that fallback for the ws{>25}r lookback only, never for the blast
radius.

## ws7, ws8 AND ws9 READ `towards` ONLY BECAUSE CLOSED-PREV HAS NOT STEPPED

| the line | its state at 08:26:00 | its lift-off stamp (emerging) | its closed-prev distance from the LOW extremum |
|---|---|---|---|
| ws7r | towards | 2026-08-07 08:24:40 | 0.0000 |
| ws8r | towards | 2026-08-07 08:24:45 | 0.0000 |
| ws9r | towards | 2026-08-07 08:13:20 | 0.0000 |

All three had already lifted off on emerging before the cadence bar. `towards` is the closed-prev
staircase still sitting on its low, and a ws7 staircase steps once every 7 minutes.

## THE DOMINOES ARE IN THE DATA, IN THE LAST 85 SECONDS

| the stamp | the line |
|---|---|
| 2026-08-07 08:24:30 | ws1r |
| 2026-08-07 08:24:35 | ws4r |
| 2026-08-07 08:24:35 | ws6r |
| 2026-08-07 08:24:40 | ws7r |
| 2026-08-07 08:24:45 | ws8r |
| 2026-08-07 08:25:50 | ws10r |
| 2026-08-07 08:25:55 | ws3r |

ws1 -> ws4 -> ws6 -> ws7 -> ws8 -> ws10, ascending TF, inside 80 s. ws3r arrives last, out of order.
ws2r stamped 08:12:30 and ws5r 08:05:55, both long before.

**So the discriminator is the RECENCY of the stamps, not their existence.** What span counts as
recent is a value and it is his.

## THE FLATNESS IS ALREADY COMPUTED AND THROWN AWAY

`jig.at_extreme` returns `dist` - how far the newest sample sits off its sampled window extreme, in
r-points - and holds while `dist <= LIFT_TOL` 2.0. `lift_off` keeps only the bar the hold breaks;
`dist` and the length of the held run are discarded. Both are true AT the read bar, and the lift-off
is knowable only at bar + `LIFT_WOB` 8 - 1 = +7 bars = 35 s.

| the line | pinned at its extreme, bars | pinned, s | off its sampled extreme, r-points |
|---|---|---|---|
| ws9r | 122 | 610 | 0.0000 |
| ws12r | 70 | 350 | 0.0000 |
| ws13r | 79 | 395 | 0.0000 |
| ws14r | 92 | 460 | 0.0000 |
| ws17r | 157 | 785 | 0.0000 |
| ws18r | 92 | 460 | 0.0000 |
| ws19r | 145 | 725 | 0.0000 |
| ws21r | 94 | 470 | 0.0000 |
| ws22r | 109 | 545 | 0.0000 |
| ws25r | 109 | 545 | 0.0000 |
| ws26r | 88 | 440 | 0.0467 |
| ws27r | 94 | 470 | 0.0000 |
| ws28r | 94 | 470 | 0.0000 |
| ws29r | 100 | 500 | 0.0000 |

ws9r is the one that matters here: 610 s pinned dead on its sampled low, inside ws11's blast radius,
reading `towards`.

## WHAT I WOULD BUILD, AND THE 8 VALUES THAT ARE HIS

Nothing is built. The design: one jig producer fed the lift-off stamps the fdm2-wsxcad-director
already holds in `LN['LIFT']`, returning the recent-stamp run up the ladder and the blast-radius
count. It reads no lines, so it adds no cost and no causality surface.

| # | the gap | now measured as |
|---|---|---|
| 1 | the reversal origin with no prior same-side cadence window | the load-bearing one. The trade-open fallback saturates at 29 of 30 |
| 2 | does the 5-TF set count down only, or both ways | ws6..ws10 downward gives 5 of 5 |
| 3 | fire at the cadence event only, or at every bar of the auto-called walk | unmeasured |
| 4 | his name for the run up the ladder | mine was "the chain's reach" and it does not discriminate |
| 5 | what counts as flat - a `dist` threshold inside 2.0, or a held-bar count | ws9r is 122 bars at 0.0000 |
| 6 | does flatness gate or only report | his words were "adds strength" |
| 7 | which walk: `FDM_X10_GRACE_MIN` 5.0 min or `FDM_XCAD_WALK_MIN` 10.0 min | two candidates |
| 8 | every cadence event, or only a no-candidate one | unmeasured |
