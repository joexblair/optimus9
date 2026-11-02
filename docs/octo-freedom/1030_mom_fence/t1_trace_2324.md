# THE t1 CADENCE LIST, 2026-09-03 22:00:00 .. 2026-09-04 02:00:00
# the new t1: gcws30b at wob 6 bars = 30 s | the r gate: ws1r past (44.0, 56.0) at its stamp
# the pre-1031 t1: ws1b at wob 12 bars = 60 s | the r gate: ws1r on the target side of 50

| the read | low side | high side |
|---|---|---|
| pre-1031 t1 cadences, ws1b wob 12, r past 50 | 5 | 1 |
| new t1, gcws30b wob 6, r past 56, grace on the CROSS bar | 9 | 5 |
| new t1, same but grace on the CONFIRM bar | 9 | 5 |
| the two grace arms differ by, low side | 2 bars only in CROSS, 2 only in CONFIRM |  |
| the two grace arms differ by, high side | | 2 only in CROSS, 2 only in CONFIRM |

## the grace-anchor diff, low side - 4 cadences differ

| the cadence bar | in the CROSS arm? | in the CONFIRM arm? | why |
|---|---|---|---|
| 2026-09-03 22:48:25 | YES | no | gcws30b ib 22:48:00, ws1r reversed 22:48:15 inside the 120s grace from the cross bar 22:48:00, r 18.20 past the 44.0 fence, stamp 22:48:15, hold 6 bars |
| 2026-09-03 22:48:30 | no | YES | gcws30b ib 22:48:00, ws1r reversed 22:48:30 inside the 120s grace from the confirm bar 22:48:25, r 18.62 past the 44.0 fence, stamp 22:48:30, hold 6 bars |
| 2026-09-03 23:11:45 | YES | no | gcws30b ib 23:11:20, ws1r reversed 23:11:25 inside the 120s grace from the cross bar 23:11:20, r 20.62 past the 44.0 fence, stamp 23:11:25, hold 6 bars |
| 2026-09-03 23:12:15 | no | YES | gcws30b ib 23:11:20, ws1r reversed 23:12:15 inside the 120s grace from the confirm bar 23:11:45, r 22.03 past the 44.0 fence, stamp 23:12:15, hold 6 bars |

## the grace-anchor diff, high side - 4 cadences differ

| the cadence bar | in the CROSS arm? | in the CONFIRM arm? | why |
|---|---|---|---|
| 2026-09-03 23:28:30 | YES | no | gcws30b ib 23:28:05, ws1r reversed 23:28:15 inside the 120s grace from the cross bar 23:28:05, r 68.10 past the 56.0 fence, stamp 23:28:15, hold 6 bars |
| 2026-09-03 23:28:45 | no | YES | gcws30b ib 23:28:05, ws1r reversed 23:28:45 inside the 120s grace from the confirm bar 23:28:30, r 67.97 past the 56.0 fence, stamp 23:28:45, hold 6 bars |
| 2026-09-03 23:30:50 | YES | no | gcws30b ib 23:30:25, ws1r reversed 23:30:30 inside the 120s grace from the cross bar 23:30:25, r 90.15 past the 56.0 fence, stamp 23:30:30, hold 6 bars |
| 2026-09-03 23:31:00 | no | YES | gcws30b ib 23:30:25, ws1r reversed 23:31:00 inside the 120s grace from the confirm bar 23:30:50, r 75.32 past the 56.0 fence, stamp 23:31:00, hold 6 bars |

## the new t1 cadence list, low side, grace on the CROSS bar - 9 cadences

| the cadence bar | why |
|---|---|
| 2026-09-03 22:36:25 | gcws30b oob 22:31:40..22:35:55, ws1r reversed 22:34:40 during, r 10.09 past the 44.0 fence, stamp 22:34:40, cross 22:36:00 hold 6 bars |
| 2026-09-03 22:48:25 | gcws30b ib 22:48:00, ws1r reversed 22:48:15 inside the 120s grace from the cross bar 22:48:00, r 18.20 past the 44.0 fence, stamp 22:48:15, hold 6 bars |
| 2026-09-03 23:11:45 | gcws30b ib 23:11:20, ws1r reversed 23:11:25 inside the 120s grace from the cross bar 23:11:20, r 20.62 past the 44.0 fence, stamp 23:11:25, hold 6 bars |
| 2026-09-03 23:13:35 | gcws30b oob 23:12:55..23:13:05, ws1r reversed 23:13:00 during, r 19.06 past the 44.0 fence, stamp 23:13:00, cross 23:13:10 hold 6 bars |
| 2026-09-04 00:10:00 | gcws30b oob 00:06:30..00:09:30, ws1r reversed 00:09:00 during, r 8.51 past the 44.0 fence, stamp 00:09:00, cross 00:09:35 hold 6 bars |
| 2026-09-04 01:01:00 | gcws30b ib 01:00:05, ws1r reversed 01:01:00 inside the 120s grace from the cross bar 01:00:05, r 20.35 past the 44.0 fence, stamp 01:01:00, hold 6 bars |
| 2026-09-04 01:05:55 | gcws30b oob 01:04:20..01:05:25, ws1r reversed 01:05:00 during, r 22.02 past the 44.0 fence, stamp 01:05:00, cross 01:05:30 hold 6 bars |
| 2026-09-04 01:30:35 | gcws30b oob 01:29:05..01:30:05, ws1r reversed 01:30:05 during, r 9.76 past the 44.0 fence, stamp 01:30:05, cross 01:30:10 hold 6 bars |
| 2026-09-04 01:36:40 | gcws30b oob 01:33:35..01:36:10, ws1r reversed 01:35:25 during, r 5.14 past the 44.0 fence, stamp 01:35:25, cross 01:36:15 hold 6 bars |

## the new t1 cadence list, high side, grace on the CROSS bar - 5 cadences

| the cadence bar | why |
|---|---|
| 2026-09-03 23:28:30 | gcws30b ib 23:28:05, ws1r reversed 23:28:15 inside the 120s grace from the cross bar 23:28:05, r 68.10 past the 56.0 fence, stamp 23:28:15, hold 6 bars |
| 2026-09-03 23:30:50 | gcws30b ib 23:30:25, ws1r reversed 23:30:30 inside the 120s grace from the cross bar 23:30:25, r 90.15 past the 56.0 fence, stamp 23:30:30, hold 6 bars |
| 2026-09-03 23:33:35 | gcws30b ib 23:32:00, ws1r reversed 23:33:35 inside the 120s grace from the cross bar 23:32:00, r 67.33 past the 56.0 fence, stamp 23:33:35, hold 6 bars |
| 2026-09-04 00:34:30 | gcws30b ib 00:33:20, ws1r reversed 00:34:30 inside the 120s grace from the cross bar 00:33:20, r 87.84 past the 56.0 fence, stamp 00:34:30, hold 6 bars |
| 2026-09-04 00:43:00 | gcws30b oob 00:35:35..00:42:30, ws1r reversed 00:42:00 during, r 81.95 past the 56.0 fence, stamp 00:42:00, cross 00:42:35 hold 6 bars |


## the t1 read's own knobs, low side

| the knob | value | what it gates |
|---|---|---|
| LIN2_T1_B_LINE | gcws30b | the b line t1 reads |
| LIN2_T1_B_WOB | 6 bars = 30 s | the IB hold that CONFIRMS the cross |
| the oob fence | 15.0 / 85.0 | oob_ib_cross's own hi/lo - oob is 15/85 |
| LIN2_B1_OOB_DWELL | 0 bars = 0 s | the oob run must REACH this before it counts |
| LIN2_B1_HOLD | 0 bars = 0 s | a blip back to IB shorter than this still reads oob |
| LIN2_T1_R_FNC | 56.0 -> (44.0, 56.0) | ws1r at its stamp must be past 44.0 |
| L2_T1_GRACE_S | 120 s = 24 bars | the forward window for a late ws1r reversal |
| LIN2_T1_GRACE_AT | 'cross' | where that window starts |
| L2_CWS1R_WOB | 1 bars = 5 s | the ws1r lift-off's own hold - CAD._stamp adds this minus 1 to the raw bar. NOT LIFT_WOB 8 |

## every gcws30b oob->ib cross, low side, 2026-09-03 22:00:00 .. 2026-09-04 02:00:00 - the driver's own window

| the cross bar | the confirm bar | gcws30b at the cross | the run before | the HELD run ending at cross-1 | ws1r revs in that run | ws1r revs in the grace | the cadence | the first condition that fails |
|---|---|---|---|---|---|---|---|---|
| 2026-09-03 22:04:45 | 2026-09-03 22:05:10 | 15.75 | 22:04:15..22:04:40 raw | 22:04:15..22:04:40 | - | - | - | no ws1r reversal in the run or in the 120 s grace |
| 2026-09-03 22:15:00 | 2026-09-03 22:15:25 | 16.69 | 22:14:15..22:14:55 raw | 22:14:15..22:14:55 | - | - | - | no ws1r reversal in the run or in the 120 s grace |
| 2026-09-03 22:36:00 | 2026-09-03 22:36:25 | 21.24 | 22:31:40..22:35:55 raw | 22:31:40..22:35:55 | 22:33:00 r 6.69, 22:34:00 r 8.10, 22:34:15 r 6.47, 22:34:40 r 10.09 | - | 2026-09-03 22:36:25 |  |
| 2026-09-03 22:39:30 | 2026-09-03 22:39:55 | 15.94 | 22:39:25..22:39:25 raw | 22:39:25..22:39:25 | - | - | - | no ws1r reversal in the run or in the 120 s grace |
| 2026-09-03 22:48:00 | 2026-09-03 22:48:25 | 15.28 | 22:47:25..22:47:55 raw | 22:47:25..22:47:55 | - | 22:48:15 r 18.20, 22:48:30 r 18.62, 22:48:45 r 17.76, 22:49:00 r 18.00, 22:49:15 r 19.42, 22:49:35 r 16.79, 22:50:00 r 29.25 | 2026-09-03 22:48:25 |  |
| 2026-09-03 22:56:35 | 2026-09-03 22:57:00 | 15.43 | 22:54:05..22:56:30 raw | 22:54:05..22:56:30 | 22:56:30 r 56.84 INSIDE | - | - | every ws1r reversal is inside the 44.0 fence: 22:56:30 r 56.84 |
| 2026-09-03 23:11:20 | 2026-09-03 23:11:45 | 15.44 | 23:11:05..23:11:15 raw | 23:11:05..23:11:15 | - | 23:11:25 r 20.62, 23:12:15 r 22.03, 23:12:45 r 21.59, 23:13:00 r 19.06, 23:13:10 r 26.32 | 2026-09-03 23:11:45 |  |
| 2026-09-03 23:13:10 | 2026-09-03 23:13:35 | 28.03 | 23:12:55..23:13:05 raw | 23:12:55..23:13:05 | 23:13:00 r 19.06 | 23:13:55 r 19.06 | 2026-09-03 23:13:35 |  |
| 2026-09-03 23:14:35 | 2026-09-03 23:15:00 | 18.29 | 23:14:25..23:14:30 raw | 23:14:25..23:14:30 | - | - | - | no ws1r reversal in the run or in the 120 s grace |
| 2026-09-03 23:23:10 | 2026-09-03 23:23:35 | 17.04 | 23:22:50..23:23:05 raw | 23:22:50..23:23:05 | - | 23:23:15 r 59.19 INSIDE, 23:24:05 r 49.85 INSIDE, 23:24:25 r 51.65 INSIDE | - | every ws1r reversal is inside the 44.0 fence: 23:23:15 r 59.19, 23:24:05 r 49.85, 23:24:25 r 51.65 |
| 2026-09-03 23:24:00 | 2026-09-03 23:24:25 | 27.82 | 23:23:45..23:23:55 raw | 23:23:45..23:23:55 | - | 23:24:05 r 49.85 INSIDE, 23:24:25 r 51.65 INSIDE, 23:25:30 r 53.29 INSIDE, 23:25:50 r 53.29 INSIDE, 23:26:00 r 55.92 INSIDE | - | every ws1r reversal is inside the 44.0 fence: 23:24:05 r 49.85, 23:24:25 r 51.65, 23:25:30 r 53.29, 23:25:50 r 53.29, 23:26:00 r 55.92 |
| 2026-09-03 23:28:05 | 2026-09-03 23:28:30 | 84.65 | none | NONE | - | - | - | the run before the cross was on the high side |
| 2026-09-03 23:30:25 | 2026-09-03 23:30:50 | 83.64 | none | NONE | - | 23:31:35 r 78.49 INSIDE, 23:31:50 r 78.30 INSIDE, 23:32:25 r 67.40 INSIDE | - | the run before the cross was on the high side |
| 2026-09-03 23:32:00 | 2026-09-03 23:32:25 | 79.92 | none | NONE | - | 23:32:25 r 67.40 INSIDE, 23:32:45 r 68.34 INSIDE, 23:33:20 r 63.72 INSIDE | - | the run before the cross was on the high side |
| 2026-09-03 23:43:00 | 2026-09-03 23:43:25 | 84.35 | none | NONE | - | - | - | the run before the cross was on the high side |
| 2026-09-04 00:09:35 | 2026-09-04 00:10:00 | 28.58 | 00:06:30..00:09:30 raw | 00:06:30..00:09:30 | 00:09:00 r 8.51 | - | 2026-09-04 00:10:00 |  |
| 2026-09-04 00:25:40 | 2026-09-04 00:26:05 | 18.91 | 00:25:25..00:25:35 raw | 00:25:25..00:25:35 | - | - | - | no ws1r reversal in the run or in the 120 s grace |
| 2026-09-04 00:28:15 | 2026-09-04 00:28:40 | 21.81 | 00:26:30..00:28:10 raw | 00:26:30..00:28:10 | - | - | - | no ws1r reversal in the run or in the 120 s grace |
| 2026-09-04 00:33:20 | 2026-09-04 00:33:45 | 79.48 | none | NONE | - | - | - | the run before the cross was on the high side |
| 2026-09-04 00:42:35 | 2026-09-04 00:43:00 | 82.76 | none | NONE | - | 00:43:15 r 70.29 INSIDE | - | the run before the cross was on the high side |
| 2026-09-04 00:56:20 | 2026-09-04 00:56:45 | 15.39 | 00:56:10..00:56:15 raw | 00:56:10..00:56:15 | - | - | - | no ws1r reversal in the run or in the 120 s grace |
| 2026-09-04 01:00:05 | 2026-09-04 01:00:30 | 19.78 | 00:57:20..01:00:00 raw | 00:57:20..01:00:00 | - | 01:01:00 r 20.35, 01:01:25 r 19.13, 01:01:40 r 19.27 | 2026-09-04 01:01:00 |  |
| 2026-09-04 01:05:30 | 2026-09-04 01:05:55 | 15.67 | 01:04:20..01:05:25 raw | 01:04:20..01:05:25 | 01:04:25 r 16.38, 01:05:00 r 22.02 | - | 2026-09-04 01:05:55 |  |
| 2026-09-04 01:30:10 | 2026-09-04 01:30:35 | 15.85 | 01:29:05..01:30:05 raw | 01:29:05..01:30:05 | 01:30:05 r 9.76 | 01:31:00 r 18.04 | 2026-09-04 01:30:35 |  |
| 2026-09-04 01:36:15 | 2026-09-04 01:36:40 | 15.35 | 01:33:35..01:36:10 raw | 01:33:35..01:36:10 | 01:34:00 r 12.43, 01:35:00 r 5.14, 01:35:25 r 5.14 | - | 2026-09-04 01:36:40 |  |
| 2026-09-04 01:36:55 | 2026-09-04 01:37:20 | 19.98 | 01:36:45..01:36:50 raw | 01:36:45..01:36:50 | - | - | - | no ws1r reversal in the run or in the 120 s grace |
| 2026-09-04 01:41:00 | 2026-09-04 01:41:25 | 19.51 | 01:40:55..01:40:55 raw | 01:40:55..01:40:55 | - | 01:42:10 r 72.05 INSIDE, 01:42:45 r 71.69 INSIDE, 01:42:55 r 75.05 INSIDE | - | every ws1r reversal is inside the 44.0 fence: 01:42:10 r 72.05, 01:42:45 r 71.69, 01:42:55 r 75.05 |
| 2026-09-04 01:42:35 | 2026-09-04 01:43:00 | 16.75 | 01:42:25..01:42:30 raw | 01:42:25..01:42:30 | - | 01:42:45 r 71.69 INSIDE, 01:42:55 r 75.05 INSIDE, 01:43:50 r 67.72 INSIDE, 01:44:10 r 65.19 INSIDE | - | every ws1r reversal is inside the 44.0 fence: 01:42:45 r 71.69, 01:42:55 r 75.05, 01:43:50 r 67.72, 01:44:10 r 65.19 |
| 2026-09-04 01:48:50 | 2026-09-04 01:49:15 | 84.70 | none | NONE | - | - | - | the run before the cross was on the high side |
| 2026-09-04 01:59:00 | 2026-09-04 01:59:25 | 83.05 | none | NONE | - | 01:59:55 r 54.37 INSIDE, 02:00:15 r 46.80 INSIDE | - | the run before the cross was on the high side |

## gcws30b and ws1r bar by bar, 2026-09-03 23:18:00 .. 2026-09-03 23:30:00 - THESE BOUNDS ARE MINE

| the bar | gcws30b | IB? | raw oob? | HELD oob? | ws1r | a ws1r reversal raw bar? |
|---|---|---|---|---|---|---|
| 2026-09-03 23:18:00 | 27.44 | YES | no | no | 66.95 | - |
| 2026-09-03 23:18:05 | 32.05 | YES | no | no | 69.29 | - |
| 2026-09-03 23:18:10 | 32.05 | YES | no | no | 69.29 | - |
| 2026-09-03 23:18:15 | 39.40 | YES | no | no | 73.74 | - |
| 2026-09-03 23:18:20 | 37.39 | YES | no | no | 72.66 | - |
| 2026-09-03 23:18:25 | 37.39 | YES | no | no | 72.66 | - |
| 2026-09-03 23:18:30 | 37.39 | YES | no | no | 72.66 | - |
| 2026-09-03 23:18:35 | 37.39 | YES | no | no | 72.66 | - |
| 2026-09-03 23:18:40 | 40.61 | YES | no | no | 73.90 | - |
| 2026-09-03 23:18:45 | 29.60 | YES | no | no | 68.56 | - |
| 2026-09-03 23:18:50 | 35.76 | YES | no | no | 72.27 | - |
| 2026-09-03 23:18:55 | 35.76 | YES | no | no | 72.27 | - |
| 2026-09-03 23:19:00 | 36.34 | YES | no | no | 85.40 | - |
| 2026-09-03 23:19:05 | 36.34 | YES | no | no | 85.40 | - |
| 2026-09-03 23:19:10 | 32.89 | YES | no | no | 83.02 | - |
| 2026-09-03 23:19:15 | 32.89 | YES | no | no | 83.02 | - |
| 2026-09-03 23:19:20 | 35.65 | YES | no | no | 84.92 | - |
| 2026-09-03 23:19:25 | 31.52 | YES | no | no | 82.18 | - |
| 2026-09-03 23:19:30 | 31.52 | YES | no | no | 82.18 | - |
| 2026-09-03 23:19:35 | 32.30 | YES | no | no | 82.59 | - |
| 2026-09-03 23:19:40 | 30.25 | YES | no | no | 81.42 | - |
| 2026-09-03 23:19:45 | 35.05 | YES | no | no | 84.41 | - |
| 2026-09-03 23:19:50 | 35.05 | YES | no | no | 84.41 | - |
| 2026-09-03 23:19:55 | 34.36 | YES | no | no | 83.93 | - |
| 2026-09-03 23:20:00 | 32.47 | YES | no | no | 86.23 | - |
| 2026-09-03 23:20:05 | 31.77 | YES | no | no | 85.54 | - |
| 2026-09-03 23:20:10 | 31.08 | YES | no | no | 84.89 | - |
| 2026-09-03 23:20:15 | 33.86 | YES | no | no | 87.71 | - |
| 2026-09-03 23:20:20 | 32.47 | YES | no | no | 86.23 | - |
| 2026-09-03 23:20:25 | 32.47 | YES | no | no | 86.23 | - |
| 2026-09-03 23:20:30 | 32.47 | YES | no | no | 86.23 | - |
| 2026-09-03 23:20:35 | 33.93 | YES | no | no | 87.71 | - |
| 2026-09-03 23:20:40 | 32.54 | YES | no | no | 86.23 | - |
| 2026-09-03 23:20:45 | 33.23 | YES | no | no | 86.95 | - |
| 2026-09-03 23:20:50 | 32.54 | YES | no | no | 86.23 | - |
| 2026-09-03 23:20:55 | 36.02 | YES | no | no | 89.96 | - |
| 2026-09-03 23:21:00 | 41.48 | YES | no | no | 89.96 | - |
| 2026-09-03 23:21:05 | 47.85 | YES | no | no | 89.96 | - |
| 2026-09-03 23:21:10 | 40.78 | YES | no | no | 89.96 | - |
| 2026-09-03 23:21:15 | 41.48 | YES | no | no | 89.96 | - |
| 2026-09-03 23:21:20 | 41.48 | YES | no | no | 89.96 | - |
| 2026-09-03 23:21:25 | 40.78 | YES | no | no | 89.96 | - |
| 2026-09-03 23:21:30 | 40.78 | YES | no | no | 89.96 | - |
| 2026-09-03 23:21:35 | 39.24 | YES | no | no | 89.96 | - |
| 2026-09-03 23:21:40 | 34.27 | YES | no | no | 82.34 | - |
| 2026-09-03 23:21:45 | 37.82 | YES | no | no | 89.33 | YES, stamp 23:21:45 r 89.33 |
| 2026-09-03 23:21:50 | 33.56 | YES | no | no | 81.13 | - |
| 2026-09-03 23:21:55 | 27.25 | YES | no | no | 75.67 | - |
| 2026-09-03 23:22:00 | 31.66 | YES | no | no | 67.32 | - |
| 2026-09-03 23:22:05 | 30.96 | YES | no | no | 66.25 | - |
| 2026-09-03 23:22:10 | 30.96 | YES | no | no | 66.25 | - |
| 2026-09-03 23:22:15 | 28.16 | YES | no | no | 61.39 | - |
| 2026-09-03 23:22:20 | 21.95 | YES | no | no | 61.39 | - |
| 2026-09-03 23:22:25 | 19.24 | YES | no | no | 61.39 | - |
| 2026-09-03 23:22:30 | 22.31 | YES | no | no | 61.39 | - |
| 2026-09-03 23:22:35 | 22.31 | YES | no | no | 61.39 | - |
| 2026-09-03 23:22:40 | 18.89 | YES | no | no | 61.39 | - |
| 2026-09-03 23:22:45 | 18.89 | YES | no | no | 61.39 | - |
| 2026-09-03 23:22:50 | 14.18 | no | YES | YES | 61.39 | - |
| 2026-09-03 23:22:55 | 8.30 | no | YES | YES | 61.39 | - |
| 2026-09-03 23:23:00 | 12.51 | no | YES | YES | 49.64 | - |
| 2026-09-03 23:23:05 | 11.24 | no | YES | YES | 48.46 | - |
| 2026-09-03 23:23:10 | 17.04 | YES | no | no | 53.17 | - |
| 2026-09-03 23:23:15 | 28.45 | YES | no | no | 59.19 | YES, stamp 23:23:15 r 59.19 |
| 2026-09-03 23:23:20 | 23.69 | YES | no | no | 57.05 | - |
| 2026-09-03 23:23:25 | 21.68 | YES | no | no | 56.00 | - |
| 2026-09-03 23:23:30 | 30.25 | YES | no | no | 59.46 | - |
| 2026-09-03 23:23:35 | 28.86 | YES | no | no | 58.91 | - |
| 2026-09-03 23:23:40 | 22.71 | YES | no | no | 56.00 | - |
| 2026-09-03 23:23:45 | 12.15 | no | YES | YES | 48.46 | - |
| 2026-09-03 23:23:50 | 0.40 | no | YES | YES | 47.84 | - |
| 2026-09-03 23:23:55 | 2.19 | no | YES | YES | 47.84 | - |
| 2026-09-03 23:24:00 | 27.82 | YES | no | no | 50.06 | - |
| 2026-09-03 23:24:05 | 27.15 | YES | no | no | 49.85 | YES, stamp 23:24:05 r 49.85 |
| 2026-09-03 23:24:10 | 42.71 | YES | no | no | 51.65 | - |
| 2026-09-03 23:24:15 | 27.15 | YES | no | no | 49.85 | - |
| 2026-09-03 23:24:20 | 25.83 | YES | no | no | 49.40 | - |
| 2026-09-03 23:24:25 | 43.40 | YES | no | no | 51.65 | YES, stamp 23:24:25 r 51.65 |
| 2026-09-03 23:24:30 | 47.56 | YES | no | no | 51.65 | - |
| 2026-09-03 23:24:35 | 43.34 | YES | no | no | 51.65 | - |
| 2026-09-03 23:24:40 | 39.83 | YES | no | no | 51.65 | - |
| 2026-09-03 23:24:45 | 39.13 | YES | no | no | 51.65 | - |
| 2026-09-03 23:24:50 | 41.23 | YES | no | no | 51.65 | - |
| 2026-09-03 23:24:55 | 55.31 | YES | no | no | 51.65 | - |
| 2026-09-03 23:25:00 | 50.12 | YES | no | no | 51.95 | - |
| 2026-09-03 23:25:05 | 45.11 | YES | no | no | 50.93 | - |
| 2026-09-03 23:25:10 | 47.97 | YES | no | no | 51.50 | - |
| 2026-09-03 23:25:15 | 56.56 | YES | no | no | 53.29 | - |
| 2026-09-03 23:25:20 | 57.99 | YES | no | no | 53.29 | - |
| 2026-09-03 23:25:25 | 62.26 | YES | no | no | 53.29 | - |
| 2026-09-03 23:25:30 | 62.26 | YES | no | no | 53.29 | YES, stamp 23:25:30 r 53.29 |
| 2026-09-03 23:25:35 | 57.28 | YES | no | no | 53.29 | - |
| 2026-09-03 23:25:40 | 57.28 | YES | no | no | 53.29 | - |
| 2026-09-03 23:25:45 | 57.28 | YES | no | no | 53.29 | - |
| 2026-09-03 23:25:50 | 59.49 | YES | no | no | 53.29 | YES, stamp 23:25:50 r 53.29 |
| 2026-09-03 23:25:55 | 59.49 | YES | no | no | 53.29 | - |
| 2026-09-03 23:26:00 | 63.19 | YES | no | no | 55.92 | YES, stamp 23:26:00 r 55.92 |
| 2026-09-03 23:26:05 | 63.19 | YES | no | no | 55.92 | - |
| 2026-09-03 23:26:10 | 77.85 | YES | no | no | 55.92 | - |
| 2026-09-03 23:26:15 | 75.69 | YES | no | no | 55.92 | - |
| 2026-09-03 23:26:20 | 76.41 | YES | no | no | 55.92 | - |
| 2026-09-03 23:26:25 | 76.41 | YES | no | no | 55.92 | - |
| 2026-09-03 23:26:30 | 80.73 | YES | no | no | 55.92 | - |
| 2026-09-03 23:26:35 | 80.73 | YES | no | no | 55.92 | - |
| 2026-09-03 23:26:40 | 80.73 | YES | no | no | 55.92 | - |
| 2026-09-03 23:26:45 | 75.64 | YES | no | no | 55.92 | - |
| 2026-09-03 23:26:50 | 75.64 | YES | no | no | 55.92 | - |
| 2026-09-03 23:26:55 | 75.64 | YES | no | no | 55.92 | - |
| 2026-09-03 23:27:00 | 80.34 | YES | no | no | 57.14 | - |
| 2026-09-03 23:27:05 | 81.06 | YES | no | no | 57.14 | - |
| 2026-09-03 23:27:10 | 81.78 | YES | no | no | 57.14 | - |
| 2026-09-03 23:27:15 | 81.06 | YES | no | no | 57.14 | - |
| 2026-09-03 23:27:20 | 81.06 | YES | no | no | 57.14 | - |
| 2026-09-03 23:27:25 | 78.88 | YES | no | no | 57.14 | - |
| 2026-09-03 23:27:30 | 83.56 | YES | no | no | 57.14 | - |
| 2026-09-03 23:27:35 | 83.56 | YES | no | no | 57.14 | - |
| 2026-09-03 23:27:40 | 89.34 | no | no | no | 57.14 | - |
| 2026-09-03 23:27:45 | 92.85 | no | no | no | 57.14 | - |
| 2026-09-03 23:27:50 | 96.96 | no | no | no | 57.14 | - |
| 2026-09-03 23:27:55 | 96.96 | no | no | no | 57.14 | - |
| 2026-09-03 23:28:00 | 92.86 | no | no | no | 70.86 | YES, stamp 23:28:00 r 70.86 |
| 2026-09-03 23:28:05 | 84.65 | YES | no | no | 68.91 | - |
| 2026-09-03 23:28:10 | 84.65 | YES | no | no | 68.91 | - |
| 2026-09-03 23:28:15 | 80.41 | YES | no | no | 68.10 | - |
| 2026-09-03 23:28:20 | 84.65 | YES | no | no | 68.91 | - |
| 2026-09-03 23:28:25 | 84.65 | YES | no | no | 68.91 | - |
| 2026-09-03 23:28:30 | 84.56 | YES | no | no | 69.06 | - |
| 2026-09-03 23:28:35 | 84.56 | YES | no | no | 69.06 | - |
| 2026-09-03 23:28:40 | 84.56 | YES | no | no | 69.06 | - |
| 2026-09-03 23:28:45 | 78.98 | YES | no | no | 67.97 | - |
| 2026-09-03 23:28:50 | 76.14 | YES | no | no | 67.48 | - |
| 2026-09-03 23:28:55 | 76.14 | YES | no | no | 67.48 | - |
| 2026-09-03 23:29:00 | 87.95 | no | no | no | 79.08 | - |
| 2026-09-03 23:29:05 | 87.95 | no | no | no | 79.08 | - |
| 2026-09-03 23:29:10 | 98.54 | no | no | no | 80.03 | - |
| 2026-09-03 23:29:15 | 101.07 | no | no | no | 80.23 | - |
| 2026-09-03 23:29:20 | 99.81 | no | no | no | 80.13 | - |
| 2026-09-03 23:29:25 | 99.81 | no | no | no | 80.13 | - |
| 2026-09-03 23:29:30 | 99.81 | no | no | no | 80.13 | - |
| 2026-09-03 23:29:35 | 103.73 | no | no | no | 80.50 | - |
| 2026-09-03 23:29:40 | 98.20 | no | no | no | 80.08 | - |
| 2026-09-03 23:29:45 | 98.83 | no | no | no | 80.13 | - |
| 2026-09-03 23:29:50 | 98.83 | no | no | no | 80.13 | - |
| 2026-09-03 23:29:55 | 103.73 | no | no | no | 80.50 | - |
| 2026-09-03 23:30:00 | 96.25 | no | no | no | 92.40 | - |
