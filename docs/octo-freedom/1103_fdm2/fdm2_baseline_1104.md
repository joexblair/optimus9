# THE 1104 BASELINE - banked on his word, *"that's our baseline - bank it in"*

Every future change to fdm2 is measured against the numbers on this page. The machine that
produced them is commit `a3ab05c` on `causal/lookahead`, with no knob moved from what he banked.

## the machine, all 94 built days, the MAE 1.1% stop ON

| the read | value |
|---|---|
| legs | 898 |
| gross % | -18.365 |
| drag % | -177.374 |
| net % | -195.721 |
| gross per leg % | -0.0205 |
| the round trip a leg has to beat % | 0.1975 |
| days net above zero | 19 of 94 |
| legs ended by the stop | 362 of 898 |
| the MFE the legs offered, summed % | +870.371 |
| MFE per leg % | +0.9692 |
| the MAE the legs ran, summed % | 630.473 |
| MAE per leg % | 0.7021 |
| what the walk and the stop kept | -2.1% of the MFE |

## his four days, single-day runs

| the day | legs | stopped | gross % | drag % | net % | MFE captured |
|---|---|---|---|---|---|---|
| 2026-08-03 | 15 | 5 | -0.977 | -2.963 | -3.940 | -9.9% |
| 2026-09-15 | 10 | 1 | +15.231 | -1.975 | +13.256 | 61.5% |
| 2026-09-16 | 6 | 3 | -0.565 | -1.185 | -1.750 | -6.4% |
| 2026-09-17 | 19 | 8 | -2.150 | -3.753 | -5.902 | -15.6% |

THESE FOUR ARE THE CONTROL ROW of every sweep grid. `fdm2_arms.py` checks config 0 against
08-03 -3.940, 09-15 +13.256, 09-16 -1.750, 09-17 -5.902 and prints DRIFTED if any moves.

## the 09-15..09-17 chain, one continuous walk

| the read | value |
|---|---|
| legs | 34 |
| stopped | 12 |
| gross % | +12.821 |
| drag % | -6.715 |
| net % | +6.106 |
| MFE captured | 27.0% |

## the re-entry's openings, isolated, all 94 days

737 distinct opens from 1,201 signals, each scored against its own sweep-pivot leg, no walk and
no stop in the way.

| the read | value |
|---|---|
| MFE beat its own MAE | 502 of 737 |
| the MFE captured, median, of its own leg's swing | 64.6% |
| median MAE % | -0.380 |
| median MFE % | +0.746 |
| MAE past -1.10% before the leg turned | 141 of 737 |
| realised at the leg close, per open % | +0.6059 |
| opens whose realised cleared the round trip | 456 of 737 |

THE +0.6059% IS A CEILING, NOT A TRADEABLE NUMBER. sweep-pivots closes a leg with full hindsight by
its own ruling, and it is scoring only. What it establishes is that the ceiling sits well clear of
the 0.1975% round trip.

## the 449 swept configs

Seven grids over all 94 days: his 5 re-entry settings, the r config's trip, ws1b's band multiplier,
his TF replacement, every spec knob one at a time, his dynamic climb, and the start line's own
curve. 0 of 449 configs reached 0.1975% gross per leg and 0 netted positive.

| the best config found | value |
|---|---|
| what it is | the reversal climb from ws8, ceiling ws12, rung gate at 20/80, the live read |
| legs | 883 |
| gross % | +111.425 |
| net % | -62.972 |
| gross per leg % | +0.1262 |
| days net above zero | 31 of 94 |

## where the loss sits

| the stage | what it does with the move | measured |
|---|---|---|
| the opening | finds +0.9692% of MFE per leg, keeps 64.6% of its own leg's swing | yes |
| a hindsight exit at the leg close | keeps +0.6059% per open, 456 of 737 clear the round trip | yes |
| the rev-trade walk and the 1.1% stop | keeps -2.1% of the MFE, -0.0205% per leg | yes |

The opening is not the weak stage. The exit is, and it has never been swept as a mech.

## the files behind every number here

| the file | what is in it |
|---|---|
| sweep_1104_knobs.md | his 5 settings x his 8 days |
| sweep_1104_knobs_94d.md | the same 48 configs x all 94 days |
| sweep_1104_rtrip_94d.md, sweep_1104_rtrip2_94d.md | the r trip, and crossed with the read |
| sweep_1104_bmult_94d.md, sweep_1104_bmult2_94d.md | ws1b's multiplier, and crossed with the read |
| sweep_1104_tfpair_94d.md | his TF replacement |
| sweep_1104_curve_94d.md, sweep_1104_curve_report.md | every spec knob one at a time, and its report |
| sweep_1104_climb_94d.md | his dynamic climb |
| sweep_1104_startline_94d.md | the start line ws5..ws12 |
| sweep_1104_arms.md | the per-arm table per grid, his standing re-print |
| sweep_1104_handover.md | the night's narrative and what needs his ruling |
| sweep_1104_status.md | one line per watchdog wake |
