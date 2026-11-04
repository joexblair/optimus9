# the 1104 overnight sweep - handover

He went offline at 2026-11-04 07:1x UTC with the sweep running. Everything below is readable from
the files in this directory; nothing here depends on a session being alive.

## what the machine is, on disk, right now

The banked re-entry is his 1104 ws5/ws6 reversal walk, commit `a3ab05c` on `causal/lookahead`:

- the window opens where ws1b is oob AND gcws30b is ex-5/95, same side, and it is PAIRED with its
  own ws1b ib close
- walk forward to the FIRST ws5 reversal after the open, on the window's side, read on the
  chart-matched line, stamped 35 s after the lift
- ws5r must be ex-20/80 at that reversal, else the window produces nothing
- ws6r at or past 20/80 there sends the walk on to the ws6 reversal; inside the fence it scans at once
- the scan needs one of ws7r..ws12r strictly inside 20/80
- the trade opens 1 bar after the LAST of: the ws5 reversal, the ws6 reversal, the ws1b ib close

NOTHING WAS MOVED OFF THAT DEFAULT TONIGHT. Every sweep arm is an env override.

## the number that matters

| config 0, the banked machine, over all 94 days | value |
|---|---|
| legs | 898 |
| gross % | -18.365 |
| drag % | -177.374 |
| net % | -195.721 |
| gross per leg % | -0.0205 |
| the round trip it has to beat % | 0.1975 |
| days net above zero | 19 of 94 |
| his 8 days net % | -0.345 |
| the other 86 days net % | -195.376 |

The mech's per-leg gross edge is the wall: the best arm over 94 days - the live reversal read with
ws5r's fence at 20/80 and the scan to ws12 - grosses +0.0604% per leg against a 0.1975% round trip.
No knob in the grid closes that gap on its own.

## the files

| the file | what is in it |
|---|---|
| sweep_1104_knobs.md | his 5 re-entry settings x his 8 days, 48 configs |
| sweep_1104_knobs_94d.md | the same 48 configs x all 94 days |
| sweep_1104_rtrip_94d.md | the 27 r trips, his ranges, at the banked settings |
| sweep_1104_bmult_94d.md | ws1b's 5 band multipliers |
| sweep_1104_tfpair_94d.md | his "replace ws5 and ws6 with higher TFs, and scan higher than ws12" |
| sweep_1104_curve_94d.md | every knob in the spec, one at a time, 103 rungs over 24 knobs |
| sweep_1104_arms.md | the per-arm table per grid, his standing re-print ask |
| sweep_1104_status.md | one timestamped line per watchdog wake |

Every grid's config 0 is the ruled machine and `fdm2_arms.py` checks it against 2026-08-03 -3.940,
2026-09-15 +13.256, 2026-09-16 -1.750, 2026-09-17 -5.902 before printing a single arm. A DRIFTED
line means that grid is void.

## how to re-run anything

    cd /home/joe/thecodes/docs/octo-freedom/1103_fdm2
    W_V4_EXPERIMENT=1 W_FDM2_SWEEP_GRID=<knobs|rtrip|bmult|tfpair|curve> \
      W_FDM2_SWEEP_DAYS=/home/joe/.claude/jobs/7c82535c/tmp/all_days.txt \
      W_FDM2_SWEEP_OUT=sweep_1104_<grid>_94d.md python3 fdm2_sweep.py
    python3 fdm2_arms.py sweep_1104_<grid>_94d.md

The day lists are /home/joe/.claude/jobs/7c82535c/tmp/all_days.txt (94 days, 2026-07-02 left out
because the tape starts 12:00:00 that day) and sweep_days.txt (his 4 plus the 4 drawn at seed
20261104: 2026-07-29, 2026-08-14, 2026-08-20, 2026-09-25).

## what is NOT swept, and why

- v4saviour's five settings, while the saviour is off. They become a stage only if the saviour-on
  rung shows something
- the oob fence, settled by his standing "oob ALWAYS means 15/85"
- minutes-to-bars, arithmetic rather than a judgement
- the three per-timeframe FUNCTIONS the spec flags - the lift-off's sampling gap, the towards block
  width, the towards age floor. Each is a function of the timeframe, not one value, so its shape
  has to be ruled before it can be swept. THAT IS AN OPEN ASK FOR HIM.

## the first thing to put in front of him

The 94-day result against the 8-day result. The 8 days said the live reversal read was worth
+351% summed over its 24 configs; the 94 days say every arm is negative and the drag is the wall.
The direction he was given at 06:30 UTC did not survive the wider tape, and that is the finding.

## the r trip and ws1b's multiplier, both over 94 days

Neither rescues the machine. Every rung is deeply negative; the spread is real but it never crosses
zero.

| the rung | all 94 net % | legs |
|---|---|---|
| the best r trip, (rsi 4, stoch range 7, stoch len 7) | -121.284 | 755 |
| the banked r trip, (5, 8, 7) | -195.721 | 898 |
| the worst r trip, (5, 9, 7) | -204.794 | 928 |
| the best ws1b multiplier, 0.90 | -164.949 | 905 |
| the banked ws1b multiplier, 0.95 | -195.721 | 898 |
| the worst ws1b multiplier, 1.00 | -187.829 | 866 |

So the r config is worth about 75 percentage points across its 27 rungs and ws1b's multiplier about
31 across its 5, against a 196-point hole. Both are second-order next to the per-leg gross edge.

## his TF replacement, stage 7, over 94 days

*"replace ws5 and ws6 with higher TFs, and scan higher than ws12"*. 88 of the 112 configs ran; the
rest were REFUSED by the mech's own assert, a pair whose gate sits at or above the scan ceiling.

| the pair | gross per leg % | legs | all 94 net % |
|---|---|---|---|
| (5, 6), his spec | +0.0271 | 14293 | -2435.171 |
| (7, 8) | +0.0656 | 12629 | -1665.912 |
| (8, 9) | +0.0644 | 12312 | -1638.987 |
| (10, 11) | -0.0271 | 10696 | -2402.812 |
| (12, 13) | +0.0334 | 8942 | -1467.126 |
| (15, 16) | +0.0485 | 6932 | -1032.808 |
| (20, 21) | +0.0163 | 3738 | -677.388 |

The best single config is the pair (8, 9) with the scan to ws12 on the live read: +0.1193% gross per
leg over 862 legs, net -67.434%, positive on 29 of 94 days. The best net is the pair (20, 21), scan
ceiling 24, chart-matched, at -42.914% - and that is thin, 287 legs over 94 days.

STILL NO ARM CLEARS THE DRAG. +0.1193% gross per leg against a 0.1975% round trip is the closest
anything has come, and it is 60% of the way there. Lifting the pair off ws5/ws6 is worth roughly
double the per-leg gross, which is the biggest single move any knob has shown tonight.

On the 4 days he had never seen, (7, 8) is +195.753% and (8, 9) +84.825% against (5, 6) at -13.677%.

## his dynamic climb, stage 11, over 94 days

*"it might be a dynamic mech - ride upwards through the TFs until you reach a tf showing the in
fence r line, then open the trade"*. 108 configs, both readings of his sentence as arms.

| the arm | all 94 net % | legs |
|---|---|---|
| the climb off, the banked ws5/ws6 mech | -4321.605 | 25791 |
| the climb reading each rung at one bar | -4870.059 | 29601 |
| the climb waiting for each rung's own reversal | -4332.285 | 26947 |
| the line it starts from, ws5 | -5372.037 | 33846 |
| the line it starts from, ws8 | -3543.694 | 27557 |
| the line it starts from, ws10 | -4608.218 | 20936 |

THE BEST SINGLE CONFIG OF THE WHOLE NIGHT, by gross per leg:

| the config | value |
|---|---|
| the climb | waits for each rung's own reversal |
| the ceiling | ws12 |
| the rung gate | at 20/80 |
| the reversal read | live |
| the line it starts from | ws8 |
| legs | 883 |
| gross % | +111.425 |
| net % | -62.972 |
| gross per leg % | +0.1262 |
| days net above zero | 31 of 94 |

+0.1262% per leg against the 0.1975% round trip is 64% of the way there, and it beats the fixed
pair's best (+0.1193%) by a hair. The climb itself is worth little; the START LINE is what moves -
ws8 against ws5 is the same lever the TF-pair grid found.

## stages 8 and 9

They refused on the first attempt, correctly: the reversal read had been set in the environment,
which moves the code default, and the control assert will not let config 0 be anything but the
banked machine. Re-run with the read as a grid slot instead.

## THE MORNING ANSWER, every grid of the night in one table

437 configs with 200 or more legs, over all 94 days, every one of them with the MAE 1.1 stop on.

| the round trip a config has to beat | 0.1975% |
|---|---|
| configs whose gross per leg reached it | 0 of 437 |
| configs with a positive net | 0 of 437 |

| gross per leg % | the grid | legs | gross % | net % | days net>0 | the config |
|---|---|---|---|---|---|---|
| +0.1262 | climb | 883 | +111.425 | -62.972 | 31 of 94 | the reversal climb from ws8, ceiling ws12, rung gate at 20/80, live read |
| +0.1199 | climb | 765 | +91.686 | -59.398 | 30 of 94 | the same, rung gate oob |
| +0.1193 | tfpair | 862 | +102.815 | -67.434 | 29 of 94 | the pair (8, 9), scan to ws12, live read |
| +0.1138 | tfpair | 727 | +82.727 | -60.853 | 28 of 94 | the pair (7, 8), scan to ws12, chart-matched read |
| +0.1092 | rtrip2 | 1150 | +125.631 | -101.496 | 34 of 94 | the r trip (4, 7, 6), live read |
| -0.0205 | the banked machine | 898 | -18.365 | -195.721 | 19 of 94 | ws5/ws6, chart-matched, scan to ws12 |

THE ONE LEVER THE NIGHT FOUND is the LINE THE WALK STARTS FROM. ws8 instead of ws5 takes the
per-leg gross from -0.0205% to +0.1193% with the same number of legs. Everything else - the climb
mechanism, the scan ceiling, the r trip, ws1b's multiplier, all 24 spec knobs one at a time - moves
it by a fraction of that, and nothing combines to clear the drag.

Stage 12 gives that lever its own curve: the start line at ws5 through ws12, both climb arms, at the
best config above. It is the last thing running.

## what needs HIS ruling, in order

1. The start line. His spec says ws5; the tape says ws8 and the curve from stage 12 will say
   whether it keeps climbing. Nothing moves without his word.
2. The reversal read. His 1104 ruling was chart-matched; every grid of the night says live
   (emerging), which is also what every other lift-off in the machine already uses.
3. The drag. No arm of any mech he has specified clears 0.1975% per leg. Either the per-leg move
   has to get bigger or the leg count has to come down, and both are his calls.

## stage 12: the start line's own curve, and a correction to the night's reading

At the banked chart-matched read, the curve is NOT a trend. It is bumpy:

| the start line | the climb | legs | gross % | net % | gross per leg % | days net>0 |
|---|---|---|---|---|---|---|
| ws5, his spec | off | 898 | -18.365 | -195.721 | -0.0205 | 19 of 94 |
| ws5 | reversal | 877 | +11.064 | -162.145 | +0.0126 | 20 of 94 |
| ws6 | off | 822 | +30.898 | -131.447 | +0.0376 | 25 of 94 |
| ws6 | reversal | 828 | +57.432 | -106.092 | +0.0694 | 25 of 94 |
| ws7 | off | 727 | +82.727 | -60.853 | +0.1138 | 28 of 94 |
| ws7 | reversal | 743 | +78.227 | -68.514 | +0.1053 | 27 of 94 |
| ws8 | off | 618 | +17.706 | -104.350 | +0.0287 | 24 of 94 |
| ws8 | reversal | 648 | +22.230 | -105.753 | +0.0343 | 22 of 94 |
| ws9 | off | 447 | +46.015 | -42.273 | +0.1029 | 26 of 94 |
| ws9 | reversal | 532 | +42.136 | -62.939 | +0.0792 | 26 of 94 |
| ws10 | off | 297 | -18.915 | -77.583 | -0.0637 | 19 of 94 |
| ws10 | reversal | 350 | -8.619 | -77.750 | -0.0246 | 23 of 94 |

ws11 and ws12 are absent: the gate line is the start line + 1, so with the ceiling at ws12 those
rungs trip the mech's own assert and are refused.

THE CORRECTION I OWE THE EARLIER READING. I reported "the lever is the start line, ws8 over ws5"
off the climb and TF-pair grids. The curve says the band ws6..ws9 all beat ws5, but the ranking
INSIDE that band is not stable: ws8 is the best rung at the live read and ws7 at the chart-matched
read, with ws8 falling to +0.0287 here. Picking one rung on one grid would be fitting the noise.
What survives is the band, not the rung.

AND THE SECOND HALF OF THE HONEST READING: the net improves as the start line rises mostly because
the LEG COUNT FALLS - 898 legs at ws5 against 447 at ws9. Less trading, less drag. The per-leg gross
still never reaches 0.1975% anywhere in 449 configs.

## THE NIGHT'S STRONGEST RESULT: the opening is sound and the exit is where it is lost

Two runs over all 94 days, the same 737 distinct re-entry openings, differing only in what ends
the trade.

| what ends the trade | per open or leg % | the round trip | opens or legs clearing it |
|---|---|---|---|
| the bar sweep-pivots ends the leg on, no rev-trade, no stop | +0.6059 | 0.1975 | 456 of 737 |
| the machine's own rev-trade and 1.1% stop | -0.0205 | 0.1975 | 0 of 898 legs |

| the opening's own quality, 737 distinct opens over 94 days | value |
|---|---|
| MFE beat its own MAE | 502 of 737 |
| the MFE captured, median, of the leg's own MFE | 64.6% |
| median realised at the leg close | +0.395% |
| sum realised at the leg close | +446.578% |
| MAE past -1.10% before the leg turned | 141 of 737 |

THE CAVEAT THAT MUST TRAVEL WITH THE +0.6059%: sweep-pivots closes a leg with FULL HINDSIGHT - its
own module says so, *"given that a sweep allows full lookahead"*, and it is scoring only. So
+0.6059% per open is NOT a tradeable number. It is the CEILING a causal exit would be chasing, and
it says the ceiling is well clear of the round trip.

| the stage | what it does with the move | measured |
|---|---|---|
| the opening | finds +0.9692% of MFE per leg, captures 64.6% of its own leg's swing | yes |
| a hindsight exit at the leg close | keeps +0.6059% per open, 456 of 737 clear the round trip | yes |
| the machine's rev-trade walk and 1.1% stop | keeps -2.1% of the MFE, -0.0205% per leg | yes |

So the gap between +0.6059% and -0.0205% is the exit mech's to close, and 0.1975% of that gap is
only the round trip. NOTHING in the night's 449 configs touched the exit: the rev-trade walk and
the stop were swept one knob at a time in the coverage grid and never as a mech.

THE QUESTION FOR HIM, and it is the only one that matters now: the exit. The opening does not need
fixing.
