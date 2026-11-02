# THE t1 CADENCE LIST, 2026-09-03 05:00:00 .. 2026-09-03 05:40:00
# the new t1: gcws30b at wob 6 bars = 30 s | the r gate: ws1r past (44.0, 56.0) at its stamp
# the pre-1031 t1: ws1b at wob 12 bars = 60 s | the r gate: ws1r on the target side of 50

| the read | low side | high side |
|---|---|---|
| pre-1031 t1 cadences, ws1b wob 12, r past 50 | 0 | 1 |
| new t1, gcws30b wob 6, r past 56, grace on the CROSS bar | 2 | 0 |
| new t1, same but grace on the CONFIRM bar | 1 | 0 |
| the two grace arms differ by, low side | 1 bars only in CROSS, 0 only in CONFIRM |  |
| the two grace arms differ by, high side | | 0 only in CROSS, 0 only in CONFIRM |

## the grace-anchor diff, low side - 1 cadences differ

| the cadence bar | in the CROSS arm? | in the CONFIRM arm? | why |
|---|---|---|---|
| 2026-09-03 05:24:55 | YES | no | gcws30b back inside the 5.0 fence 05:24:00, ws1r reversed 05:24:15 inside the 120s grace from the cross bar 05:24:00, r 0.50 past the 44.0 fence, stamp 05:24:15, hold 6 bars, ib dwell 12 bars |

## the grace-anchor diff, high side - 0 cadences differ

| the two arms produce an identical cadence list on this side |
|---|
| no bar differs |

## the new t1 cadence list, low side, grace on the CROSS bar - 2 cadences

| the cadence bar | why |
|---|---|
| 2026-09-03 05:19:55 | gcws30b back inside the 5.0 fence 05:19:00, ws1r reversed 05:19:15 inside the 120s grace from the cross bar 05:19:00, r 39.27 past the 44.0 fence, stamp 05:19:15, hold 6 bars, ib dwell 12 bars |
| 2026-09-03 05:24:55 | gcws30b back inside the 5.0 fence 05:24:00, ws1r reversed 05:24:15 inside the 120s grace from the cross bar 05:24:00, r 0.50 past the 44.0 fence, stamp 05:24:15, hold 6 bars, ib dwell 12 bars |

## the new t1 cadence list, high side, grace on the CROSS bar - 0 cadences

| the cadence bar | why |
|---|---|


## gcws30b bar by bar, 2026-09-03 05:17:00 .. 2026-09-03 05:21:00 | the banked read is closed_prev | the t1 fence is (5.0, 95.0)

| the bar | gcws30b, the banked chart-matched read | at or below 5.0? | gcws30b on the every-bar read | at or below 5.0? | at or below the 15.0 oob either way? |
|---|---|---|---|---|---|
| 2026-09-03 05:17:00 | 24.67 | no | 18.39 | no | neither |
| 2026-09-03 05:17:05 | 24.67 | no | 16.35 | no | neither |
| 2026-09-03 05:17:10 | 24.67 | no | 16.86 | no | neither |
| 2026-09-03 05:17:15 | 24.67 | no | 15.85 | no | neither |
| 2026-09-03 05:17:20 | 24.67 | no | 14.84 | no | every-bar |
| 2026-09-03 05:17:25 | 24.67 | no | 14.84 | no | every-bar |
| 2026-09-03 05:17:30 | 14.84 | no | 16.24 | no | chart-matched |
| 2026-09-03 05:17:35 | 14.84 | no | 9.42 | no | both |
| 2026-09-03 05:17:40 | 14.84 | no | 5.17 | no | both |
| 2026-09-03 05:17:45 | 14.84 | no | 3.33 | YES | both |
| 2026-09-03 05:17:50 | 14.84 | no | 1.50 | YES | both |
| 2026-09-03 05:17:55 | 14.84 | no | 6.11 | no | both |
| 2026-09-03 05:18:00 | 6.11 | no | 8.91 | no | both |
| 2026-09-03 05:18:05 | 6.11 | no | 7.10 | no | both |
| 2026-09-03 05:18:10 | 6.11 | no | 3.98 | YES | both |
| 2026-09-03 05:18:15 | 6.11 | no | 2.23 | YES | both |
| 2026-09-03 05:18:20 | 6.11 | no | 1.36 | YES | both |
| 2026-09-03 05:18:25 | 6.11 | no | 2.66 | YES | both |
| 2026-09-03 05:18:30 | 2.66 | YES | 7.09 | no | both |
| 2026-09-03 05:18:35 | 2.66 | YES | 5.82 | no | both |
| 2026-09-03 05:18:40 | 2.66 | YES | 10.10 | no | both |
| 2026-09-03 05:18:45 | 2.66 | YES | 17.64 | no | chart-matched |
| 2026-09-03 05:18:50 | 2.66 | YES | 14.50 | no | both |
| 2026-09-03 05:18:55 | 2.66 | YES | 7.95 | no | both |
| 2026-09-03 05:19:00 | 7.95 | no | 10.42 | no | both |
| 2026-09-03 05:19:05 | 7.95 | no | 11.25 | no | both |
| 2026-09-03 05:19:10 | 7.95 | no | 12.09 | no | both |
| 2026-09-03 05:19:15 | 7.95 | no | 13.36 | no | both |
| 2026-09-03 05:19:20 | 7.95 | no | 13.36 | no | both |
| 2026-09-03 05:19:25 | 7.95 | no | 10.00 | no | both |
| 2026-09-03 05:19:30 | 10.00 | no | 14.28 | no | both |
| 2026-09-03 05:19:35 | 10.00 | no | 14.28 | no | both |
| 2026-09-03 05:19:40 | 10.00 | no | 12.64 | no | both |
| 2026-09-03 05:19:45 | 10.00 | no | 15.92 | no | chart-matched |
| 2026-09-03 05:19:50 | 10.00 | no | 14.28 | no | both |
| 2026-09-03 05:19:55 | 10.00 | no | 13.05 | no | both |
| 2026-09-03 05:20:00 | 13.05 | no | 15.67 | no | chart-matched |
| 2026-09-03 05:20:05 | 13.05 | no | 14.48 | no | both |
| 2026-09-03 05:20:10 | 13.05 | no | 10.16 | no | both |
| 2026-09-03 05:20:15 | 13.05 | no | 0.05 | YES | both |
| 2026-09-03 05:20:20 | 13.05 | no | 1.87 | YES | both |
| 2026-09-03 05:20:25 | 13.05 | no | 1.50 | YES | both |
| 2026-09-03 05:20:30 | 1.50 | YES | 1.07 | YES | both |
| 2026-09-03 05:20:35 | 1.50 | YES | 0.05 | YES | both |
| 2026-09-03 05:20:40 | 1.50 | YES | 1.76 | YES | both |
| 2026-09-03 05:20:45 | 1.50 | YES | -2.99 | YES | both |
| 2026-09-03 05:20:50 | 1.50 | YES | -0.97 | YES | both |
| 2026-09-03 05:20:55 | 1.50 | YES | -0.97 | YES | both |
| 2026-09-03 05:21:00 | -0.97 | YES | 0.07 | YES | both |
