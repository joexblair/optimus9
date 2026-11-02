# THE t1 CADENCE LIST, 2026-09-03 01:30:00 .. 2026-09-03 03:30:00
# the new t1: gcws30b at wob 6 bars = 30 s | the r gate: ws1r past (44.0, 56.0) at its stamp
# the pre-1031 t1: ws1b at wob 12 bars = 60 s | the r gate: ws1r on the target side of 50

| the read | low side | high side |
|---|---|---|
| pre-1031 t1 cadences, ws1b wob 12, r past 50 | 2 | 4 |
| new t1, gcws30b wob 6, r past 56, grace on the CROSS bar | 5 | 8 |
| new t1, same but grace on the CONFIRM bar | 4 | 7 |
| the two grace arms differ by, low side | 2 bars only in CROSS, 1 only in CONFIRM |  |
| the two grace arms differ by, high side | | 1 only in CROSS, 0 only in CONFIRM |

## the grace-anchor diff, low side - 3 cadences differ

| the cadence bar | in the CROSS arm? | in the CONFIRM arm? | why |
|---|---|---|---|
| 2026-09-03 02:01:00 | YES | no | gcws30b ib 02:00:35, ws1r reversed 02:00:45 inside the 120s grace from the cross bar 02:00:35, r 39.31 past the 44.0 fence, stamp 02:00:45, hold 6 bars |
| 2026-09-03 03:22:40 | YES | no | gcws30b ib 03:22:15, ws1r reversed 03:22:30 inside the 120s grace from the cross bar 03:22:15, r 25.26 past the 44.0 fence, stamp 03:22:30, hold 6 bars |
| 2026-09-03 03:24:15 | no | YES | gcws30b ib 03:22:15, ws1r reversed 03:24:15 inside the 120s grace from the confirm bar 03:22:40, r 23.33 past the 44.0 fence, stamp 03:24:15, hold 6 bars |

## the grace-anchor diff, high side - 1 cadences differ

| the cadence bar | in the CROSS arm? | in the CONFIRM arm? | why |
|---|---|---|---|
| 2026-09-03 02:15:25 | YES | no | gcws30b ib 02:15:00, ws1r reversed 02:15:15 inside the 120s grace from the cross bar 02:15:00, r 81.97 past the 56.0 fence, stamp 02:15:15, hold 6 bars |

## the new t1 cadence list, low side, grace on the CROSS bar - 5 cadences

| the cadence bar | why |
|---|---|
| 2026-09-03 01:51:00 | gcws30b ib 01:49:50, ws1r reversed 01:51:00 inside the 120s grace from the cross bar 01:49:50, r 29.08 past the 44.0 fence, stamp 01:51:00, hold 6 bars |
| 2026-09-03 02:01:00 | gcws30b ib 02:00:35, ws1r reversed 02:00:45 inside the 120s grace from the cross bar 02:00:35, r 39.31 past the 44.0 fence, stamp 02:00:45, hold 6 bars |
| 2026-09-03 02:03:05 | gcws30b ib 02:02:00, ws1r reversed 02:03:05 inside the 120s grace from the cross bar 02:02:00, r 21.85 past the 44.0 fence, stamp 02:03:05, hold 6 bars |
| 2026-09-03 03:22:40 | gcws30b ib 03:22:15, ws1r reversed 03:22:30 inside the 120s grace from the cross bar 03:22:15, r 25.26 past the 44.0 fence, stamp 03:22:30, hold 6 bars |
| 2026-09-03 03:25:50 | gcws30b oob 03:23:15..03:25:20, ws1r reversed 03:24:15 during, r 23.33 past the 44.0 fence, stamp 03:24:15, cross 03:25:25 hold 6 bars |

## the new t1 cadence list, high side, grace on the CROSS bar - 8 cadences

| the cadence bar | why |
|---|---|
| 2026-09-03 01:36:00 | gcws30b oob 01:32:30..01:35:30, ws1r reversed 01:35:15 during, r 71.97 past the 56.0 fence, stamp 01:35:15, cross 01:35:35 hold 6 bars |
| 2026-09-03 02:15:25 | gcws30b ib 02:15:00, ws1r reversed 02:15:15 inside the 120s grace from the cross bar 02:15:00, r 81.97 past the 56.0 fence, stamp 02:15:15, hold 6 bars |
| 2026-09-03 02:19:25 | gcws30b oob 02:18:00..02:18:55, ws1r reversed 02:18:55 during, r 65.99 past the 56.0 fence, stamp 02:18:55, cross 02:19:00 hold 6 bars |
| 2026-09-03 02:51:05 | gcws30b ib 02:50:05, ws1r reversed 02:51:05 inside the 120s grace from the cross bar 02:50:05, r 72.26 past the 56.0 fence, stamp 02:51:05, hold 6 bars |
| 2026-09-03 02:51:45 | gcws30b ib 02:51:05, ws1r reversed 02:51:45 inside the 120s grace from the cross bar 02:51:05, r 76.31 past the 56.0 fence, stamp 02:51:45, hold 6 bars |
| 2026-09-03 02:54:00 | gcws30b ib 02:52:20, ws1r reversed 02:54:00 inside the 120s grace from the cross bar 02:52:20, r 65.01 past the 56.0 fence, stamp 02:54:00, hold 6 bars |
| 2026-09-03 02:59:10 | gcws30b oob 02:56:55..02:58:40, ws1r reversed 02:57:20 during, r 56.63 past the 56.0 fence, stamp 02:57:20, cross 02:58:45 hold 6 bars |
| 2026-09-03 03:15:20 | gcws30b ib 03:14:15, ws1r reversed 03:15:20 inside the 120s grace from the cross bar 03:14:15, r 67.68 past the 56.0 fence, stamp 03:15:20, hold 6 bars |


## the t1 cadence list with gcws30b on each source, 2026-09-03 01:30:00 .. 2026-09-03 03:30:00

| the read | low side | high side |
|---|---|---|
| t1 cadences, gcws30b emerging | 5 | 8 |
| t1 cadences, gcws30b closed_prev | 5 | 8 |
| low side: bars only on emerging | 3 | |
| low side: bars only on closed_prev | 3 | |
| high side: bars only on emerging | 7 | |
| high side: bars only on closed_prev | 7 | |

## low side, gcws30b emerging - 5 t1 cadences

| the cadence bar | why |
|---|---|
| 2026-09-03 01:51:00 | gcws30b ib 01:49:50, ws1r reversed 01:51:00 inside the 120s grace from the cross bar 01:49:50, r 29.08 past the 44.0 fence, stamp 01:51:00, hold 6 bars |
| 2026-09-03 02:01:00 | gcws30b ib 02:00:35, ws1r reversed 02:00:45 inside the 120s grace from the cross bar 02:00:35, r 39.31 past the 44.0 fence, stamp 02:00:45, hold 6 bars |
| 2026-09-03 02:03:05 | gcws30b ib 02:02:00, ws1r reversed 02:03:05 inside the 120s grace from the cross bar 02:02:00, r 21.85 past the 44.0 fence, stamp 02:03:05, hold 6 bars |
| 2026-09-03 03:22:40 | gcws30b ib 03:22:15, ws1r reversed 03:22:30 inside the 120s grace from the cross bar 03:22:15, r 25.26 past the 44.0 fence, stamp 03:22:30, hold 6 bars |
| 2026-09-03 03:25:50 | gcws30b oob 03:23:15..03:25:20, ws1r reversed 03:24:15 during, r 23.33 past the 44.0 fence, stamp 03:24:15, cross 03:25:25 hold 6 bars |

## low side, gcws30b closed_prev - 5 t1 cadences

| the cadence bar | why |
|---|---|
| 2026-09-03 01:51:00 | gcws30b ib 01:50:00, ws1r reversed 01:51:00 inside the 120s grace from the cross bar 01:50:00, r 29.08 past the 44.0 fence, stamp 01:51:00, hold 6 bars |
| 2026-09-03 02:01:25 | gcws30b oob 02:00:30..02:00:55, ws1r reversed 02:00:45 during, r 39.31 past the 44.0 fence, stamp 02:00:45, cross 02:01:00 hold 6 bars |
| 2026-09-03 02:03:05 | gcws30b ib 02:02:30, ws1r reversed 02:03:05 inside the 120s grace from the cross bar 02:02:30, r 21.85 past the 44.0 fence, stamp 02:03:05, hold 6 bars |
| 2026-09-03 03:24:15 | gcws30b ib 03:22:30, ws1r reversed 03:24:15 inside the 120s grace from the cross bar 03:22:30, r 23.33 past the 44.0 fence, stamp 03:24:15, hold 6 bars |
| 2026-09-03 03:25:55 | gcws30b oob 03:23:30..03:25:25, ws1r reversed 03:25:25 during, r 17.16 past the 44.0 fence, stamp 03:25:25, cross 03:25:30 hold 6 bars |

## high side, gcws30b emerging - 8 t1 cadences

| the cadence bar | why |
|---|---|
| 2026-09-03 01:36:00 | gcws30b oob 01:32:30..01:35:30, ws1r reversed 01:35:15 during, r 71.97 past the 56.0 fence, stamp 01:35:15, cross 01:35:35 hold 6 bars |
| 2026-09-03 02:15:25 | gcws30b ib 02:15:00, ws1r reversed 02:15:15 inside the 120s grace from the cross bar 02:15:00, r 81.97 past the 56.0 fence, stamp 02:15:15, hold 6 bars |
| 2026-09-03 02:19:25 | gcws30b oob 02:18:00..02:18:55, ws1r reversed 02:18:55 during, r 65.99 past the 56.0 fence, stamp 02:18:55, cross 02:19:00 hold 6 bars |
| 2026-09-03 02:51:05 | gcws30b ib 02:50:05, ws1r reversed 02:51:05 inside the 120s grace from the cross bar 02:50:05, r 72.26 past the 56.0 fence, stamp 02:51:05, hold 6 bars |
| 2026-09-03 02:51:45 | gcws30b ib 02:51:05, ws1r reversed 02:51:45 inside the 120s grace from the cross bar 02:51:05, r 76.31 past the 56.0 fence, stamp 02:51:45, hold 6 bars |
| 2026-09-03 02:54:00 | gcws30b ib 02:52:20, ws1r reversed 02:54:00 inside the 120s grace from the cross bar 02:52:20, r 65.01 past the 56.0 fence, stamp 02:54:00, hold 6 bars |
| 2026-09-03 02:59:10 | gcws30b oob 02:56:55..02:58:40, ws1r reversed 02:57:20 during, r 56.63 past the 56.0 fence, stamp 02:57:20, cross 02:58:45 hold 6 bars |
| 2026-09-03 03:15:20 | gcws30b ib 03:14:15, ws1r reversed 03:15:20 inside the 120s grace from the cross bar 03:14:15, r 67.68 past the 56.0 fence, stamp 03:15:20, hold 6 bars |

## high side, gcws30b closed_prev - 8 t1 cadences

| the cadence bar | why |
|---|---|
| 2026-09-03 01:36:25 | gcws30b oob 01:33:00..01:35:55, ws1r reversed 01:35:15 during, r 71.97 past the 56.0 fence, stamp 01:35:15, cross 01:36:00 hold 6 bars |
| 2026-09-03 02:15:55 | gcws30b oob 02:14:00..02:15:25, ws1r reversed 02:15:25 during, r 80.86 past the 56.0 fence, stamp 02:15:25, cross 02:15:30 hold 6 bars |
| 2026-09-03 02:19:55 | gcws30b oob 02:18:30..02:19:25, ws1r reversed 02:18:55 during, r 65.99 past the 56.0 fence, stamp 02:18:55, cross 02:19:30 hold 6 bars |
| 2026-09-03 02:33:25 | gcws30b oob 02:31:00..02:32:55, ws1r reversed 02:32:45 during, r 63.15 past the 56.0 fence, stamp 02:32:45, cross 02:33:00 hold 6 bars |
| 2026-09-03 02:36:55 | gcws30b oob 02:33:30..02:36:25, ws1r reversed 02:35:00 during, r 66.84 past the 56.0 fence, stamp 02:35:00, cross 02:36:30 hold 6 bars |
| 2026-09-03 02:51:05 | gcws30b ib 02:50:30, ws1r reversed 02:51:05 inside the 120s grace from the cross bar 02:50:30, r 72.26 past the 56.0 fence, stamp 02:51:05, hold 6 bars |
| 2026-09-03 02:51:55 | gcws30b oob 02:51:00..02:51:25, ws1r reversed 02:51:05 during, r 72.26 past the 56.0 fence, stamp 02:51:05, cross 02:51:30 hold 6 bars |
| 2026-09-03 02:59:25 | gcws30b oob 02:55:30..02:58:55, ws1r reversed 02:57:20 during, r 56.63 past the 56.0 fence, stamp 02:57:20, cross 02:59:00 hold 6 bars |
