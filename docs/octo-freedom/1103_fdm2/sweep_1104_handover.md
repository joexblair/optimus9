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
