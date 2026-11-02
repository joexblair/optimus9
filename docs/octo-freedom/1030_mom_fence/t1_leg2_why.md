# THE t1 CADENCE LIST, 2026-09-03 02:37:30 .. 2026-09-03 06:34:10
# the new t1: gcws30b at wob 6 bars = 30 s | the r gate: ws1r past (44.0, 56.0) at its stamp
# the pre-1031 t1: ws1b at wob 12 bars = 60 s | the r gate: ws1r on the target side of 50

| the read | low side | high side |
|---|---|---|
| pre-1031 t1 cadences, ws1b wob 12, r past 50 | 2 | 0 |
| new t1, gcws30b wob 6, r past 56, grace on the CROSS bar | 2 | 4 |
| new t1, same but grace on the CONFIRM bar | 2 | 4 |
| the two grace arms differ by, low side | 0 bars only in CROSS, 0 only in CONFIRM |  |
| the two grace arms differ by, high side | | 0 only in CROSS, 0 only in CONFIRM |

## the grace-anchor diff, low side - 0 cadences differ

| the two arms produce an identical cadence list on this side |
|---|
| no bar differs |

## the grace-anchor diff, high side - 0 cadences differ

| the two arms produce an identical cadence list on this side |
|---|
| no bar differs |

## the new t1 cadence list, low side, grace on the CROSS bar - 2 cadences

| the cadence bar | why |
|---|---|
| 2026-09-03 03:26:25 | gcws30b journey 03:23:30..03:25:25 reached 2.23 past the 5.0 fence, ws1r reversed 03:25:25 during, r 20.64 past the 44.0 fence, stamp 03:25:25, ib 15.0 cross 03:25:30 hold 6 bars, ib dwell 12 bars |
| 2026-09-03 04:38:55 | gcws30b journey 04:34:30..04:37:55 reached -17.54 past the 5.0 fence, ws1r reversed 04:37:45 during, r 41.21 past the 44.0 fence, stamp 04:37:45, ib 15.0 cross 04:38:00 hold 6 bars, ib dwell 12 bars |

## the new t1 cadence list, high side, grace on the CROSS bar - 4 cadences

| the cadence bar | why |
|---|---|
| 2026-09-03 02:59:55 | gcws30b journey 02:55:30..02:58:55 reached 100.03 past the 95.0 fence, ws1r reversed 02:58:45 during, r 56.77 past the 56.0 fence, stamp 02:58:45, ib 85.0 cross 02:59:00 hold 6 bars, ib dwell 12 bars |
| 2026-09-03 05:54:25 | gcws30b journey 05:50:00..05:53:25 reached 97.04 past the 95.0 fence, ws1r reversed 05:53:15 during, r 78.37 past the 56.0 fence, stamp 05:53:15, ib 85.0 cross 05:53:30 hold 6 bars, ib dwell 12 bars |
| 2026-09-03 06:25:55 | gcws30b journey 06:24:00..06:24:55 reached 95.90 past the 95.0 fence, ws1r reversed 06:24:35 during, r 56.94 past the 56.0 fence, stamp 06:24:35, ib 85.0 cross 06:25:00 hold 6 bars, ib dwell 12 bars |
| 2026-09-03 06:27:55 | gcws30b journey 06:26:30..06:26:55 reached 103.44 past the 95.0 fence, back inside the 85.0 ib fence 06:27:00, ws1r reversed 06:27:45 inside the 120s grace from the cross bar 06:27:00, r 64.63 past the 56.0 fence, stamp 06:27:45, hold 6 bars, ib dwell 12 bars |


## gcws30b bar by bar, 2026-09-03 05:28:00 .. 2026-09-03 05:40:00 | the banked read is closed_prev | the t1 fence is (5.0, 95.0)

| the bar | gcws30b, the banked chart-matched read | at or below 5.0? | ib, strictly inside 15.0..85.0? | the ib run so far, bars | the 6-bar hold met? | gcws30b on the every-bar read | ib there? |
|---|---|---|---|---|---|---|---|
| 2026-09-03 05:28:00 | 8.28 | no | no | 0 | no | 8.49 | no |
| 2026-09-03 05:28:05 | 8.28 | no | no | 0 | no | 8.95 | no |
| 2026-09-03 05:28:10 | 8.28 | no | no | 0 | no | 8.25 | no |
| 2026-09-03 05:28:15 | 8.28 | no | no | 0 | no | 8.25 | no |
| 2026-09-03 05:28:20 | 8.28 | no | no | 0 | no | 9.66 | no |
| 2026-09-03 05:28:25 | 8.28 | no | no | 0 | no | 9.89 | no |
| 2026-09-03 05:28:30 | 9.89 | no | no | 0 | no | 16.47 | YES |
| 2026-09-03 05:28:35 | 9.89 | no | no | 0 | no | 17.19 | YES |
| 2026-09-03 05:28:40 | 9.89 | no | no | 0 | no | 19.38 | YES |
| 2026-09-03 05:28:45 | 9.89 | no | no | 0 | no | 19.14 | YES |
| 2026-09-03 05:28:50 | 9.89 | no | no | 0 | no | 20.36 | YES |
| 2026-09-03 05:28:55 | 9.89 | no | no | 0 | no | 17.19 | YES |
| 2026-09-03 05:29:00 | 17.19 | no | YES | 1 | no | 19.73 | YES |
| 2026-09-03 05:29:05 | 17.19 | no | YES | 2 | no | 23.42 | YES |
| 2026-09-03 05:29:10 | 17.19 | no | YES | 3 | no | 23.42 | YES |
| 2026-09-03 05:29:15 | 17.19 | no | YES | 4 | no | 26.41 | YES |
| 2026-09-03 05:29:20 | 17.19 | no | YES | 5 | no | 24.66 | YES |
| 2026-09-03 05:29:25 | 17.19 | no | YES | 6 | YES | 23.17 | YES |
| 2026-09-03 05:29:30 | 23.17 | no | YES | 7 | YES | 26.69 | YES |
| 2026-09-03 05:29:35 | 23.17 | no | YES | 8 | YES | 25.94 | YES |
| 2026-09-03 05:29:40 | 23.17 | no | YES | 9 | YES | 26.69 | YES |
| 2026-09-03 05:29:45 | 23.17 | no | YES | 10 | YES | 26.69 | YES |
| 2026-09-03 05:29:50 | 23.17 | no | YES | 11 | YES | 28.21 | YES |
| 2026-09-03 05:29:55 | 23.17 | no | YES | 12 | YES | 26.69 | YES |
| 2026-09-03 05:30:00 | 26.69 | no | YES | 13 | YES | 27.11 | YES |
| 2026-09-03 05:30:05 | 26.69 | no | YES | 14 | YES | 29.39 | YES |
| 2026-09-03 05:30:10 | 26.69 | no | YES | 15 | YES | 29.65 | YES |
| 2026-09-03 05:30:15 | 26.69 | no | YES | 16 | YES | 30.67 | YES |
| 2026-09-03 05:30:20 | 26.69 | no | YES | 17 | YES | 34.77 | YES |
| 2026-09-03 05:30:25 | 26.69 | no | YES | 18 | YES | 35.54 | YES |
| 2026-09-03 05:30:30 | 35.54 | no | YES | 19 | YES | 35.69 | YES |
| 2026-09-03 05:30:35 | 35.54 | no | YES | 20 | YES | 35.69 | YES |
| 2026-09-03 05:30:40 | 35.54 | no | YES | 21 | YES | 36.73 | YES |
| 2026-09-03 05:30:45 | 35.54 | no | YES | 22 | YES | 37.78 | YES |
| 2026-09-03 05:30:50 | 35.54 | no | YES | 23 | YES | 38.83 | YES |
| 2026-09-03 05:30:55 | 35.54 | no | YES | 24 | YES | 37.52 | YES |
| 2026-09-03 05:31:00 | 37.52 | no | YES | 25 | YES | 36.04 | YES |
| 2026-09-03 05:31:05 | 37.52 | no | YES | 26 | YES | 38.71 | YES |
| 2026-09-03 05:31:10 | 37.52 | no | YES | 27 | YES | 41.12 | YES |
| 2026-09-03 05:31:15 | 37.52 | no | YES | 28 | YES | 40.85 | YES |
| 2026-09-03 05:31:20 | 37.52 | no | YES | 29 | YES | 40.85 | YES |
| 2026-09-03 05:31:25 | 37.52 | no | YES | 30 | YES | 35.24 | YES |
| 2026-09-03 05:31:30 | 35.24 | no | YES | 31 | YES | 35.37 | YES |
| 2026-09-03 05:31:35 | 35.24 | no | YES | 32 | YES | 35.92 | YES |
| 2026-09-03 05:31:40 | 35.24 | no | YES | 33 | YES | 34.56 | YES |
| 2026-09-03 05:31:45 | 35.24 | no | YES | 34 | YES | 35.37 | YES |
| 2026-09-03 05:31:50 | 35.24 | no | YES | 35 | YES | 37.27 | YES |
| 2026-09-03 05:31:55 | 35.24 | no | YES | 36 | YES | 38.36 | YES |
| 2026-09-03 05:32:00 | 38.36 | no | YES | 37 | YES | 41.53 | YES |
| 2026-09-03 05:32:05 | 38.36 | no | YES | 38 | YES | 41.53 | YES |
| 2026-09-03 05:32:10 | 38.36 | no | YES | 39 | YES | 41.53 | YES |
| 2026-09-03 05:32:15 | 38.36 | no | YES | 40 | YES | 42.37 | YES |
| 2026-09-03 05:32:20 | 38.36 | no | YES | 41 | YES | 40.97 | YES |
| 2026-09-03 05:32:25 | 38.36 | no | YES | 42 | YES | 40.97 | YES |
| 2026-09-03 05:32:30 | 40.97 | no | YES | 43 | YES | 40.97 | YES |
| 2026-09-03 05:32:35 | 40.97 | no | YES | 44 | YES | 42.48 | YES |
| 2026-09-03 05:32:40 | 40.97 | no | YES | 45 | YES | 43.91 | YES |
| 2026-09-03 05:32:45 | 40.97 | no | YES | 46 | YES | 43.91 | YES |
| 2026-09-03 05:32:50 | 40.97 | no | YES | 47 | YES | 45.35 | YES |
| 2026-09-03 05:32:55 | 40.97 | no | YES | 48 | YES | 46.50 | YES |
| 2026-09-03 05:33:00 | 46.50 | no | YES | 49 | YES | 48.96 | YES |
| 2026-09-03 05:33:05 | 46.50 | no | YES | 50 | YES | 50.74 | YES |
| 2026-09-03 05:33:10 | 46.50 | no | YES | 51 | YES | 49.85 | YES |
| 2026-09-03 05:33:15 | 46.50 | no | YES | 52 | YES | 49.85 | YES |
| 2026-09-03 05:33:20 | 46.50 | no | YES | 53 | YES | 49.85 | YES |
| 2026-09-03 05:33:25 | 46.50 | no | YES | 54 | YES | 49.85 | YES |
| 2026-09-03 05:33:30 | 49.85 | no | YES | 55 | YES | 48.84 | YES |
| 2026-09-03 05:33:35 | 49.85 | no | YES | 56 | YES | 48.84 | YES |
| 2026-09-03 05:33:40 | 49.85 | no | YES | 57 | YES | 48.84 | YES |
| 2026-09-03 05:33:45 | 49.85 | no | YES | 58 | YES | 48.84 | YES |
| 2026-09-03 05:33:50 | 49.85 | no | YES | 59 | YES | 48.84 | YES |
| 2026-09-03 05:33:55 | 49.85 | no | YES | 60 | YES | 50.94 | YES |
| 2026-09-03 05:34:00 | 50.94 | no | YES | 61 | YES | 56.00 | YES |
| 2026-09-03 05:34:05 | 50.94 | no | YES | 62 | YES | 52.66 | YES |
| 2026-09-03 05:34:10 | 50.94 | no | YES | 63 | YES | 54.79 | YES |
| 2026-09-03 05:34:15 | 50.94 | no | YES | 64 | YES | 58.12 | YES |
| 2026-09-03 05:34:20 | 50.94 | no | YES | 65 | YES | 61.15 | YES |
| 2026-09-03 05:34:25 | 50.94 | no | YES | 66 | YES | 59.03 | YES |
| 2026-09-03 05:34:30 | 59.03 | no | YES | 67 | YES | 62.34 | YES |
| 2026-09-03 05:34:35 | 59.03 | no | YES | 68 | YES | 61.42 | YES |
| 2026-09-03 05:34:40 | 59.03 | no | YES | 69 | YES | 58.04 | YES |
| 2026-09-03 05:34:45 | 59.03 | no | YES | 70 | YES | 60.50 | YES |
| 2026-09-03 05:34:50 | 59.03 | no | YES | 71 | YES | 60.19 | YES |
| 2026-09-03 05:34:55 | 59.03 | no | YES | 72 | YES | 61.11 | YES |
| 2026-09-03 05:35:00 | 61.11 | no | YES | 73 | YES | 64.62 | YES |
| 2026-09-03 05:35:05 | 61.11 | no | YES | 74 | YES | 64.62 | YES |
| 2026-09-03 05:35:10 | 61.11 | no | YES | 75 | YES | 60.55 | YES |
| 2026-09-03 05:35:15 | 61.11 | no | YES | 76 | YES | 68.34 | YES |
| 2026-09-03 05:35:20 | 61.11 | no | YES | 77 | YES | 68.34 | YES |
| 2026-09-03 05:35:25 | 61.11 | no | YES | 78 | YES | 64.93 | YES |
| 2026-09-03 05:35:30 | 64.93 | no | YES | 79 | YES | 65.66 | YES |
| 2026-09-03 05:35:35 | 64.93 | no | YES | 80 | YES | 67.56 | YES |
| 2026-09-03 05:35:40 | 64.93 | no | YES | 81 | YES | 66.61 | YES |
| 2026-09-03 05:35:45 | 64.93 | no | YES | 82 | YES | 68.19 | YES |
| 2026-09-03 05:35:50 | 64.93 | no | YES | 83 | YES | 64.70 | YES |
| 2026-09-03 05:35:55 | 64.93 | no | YES | 84 | YES | 66.93 | YES |
| 2026-09-03 05:36:00 | 66.93 | no | YES | 85 | YES | 70.02 | YES |
| 2026-09-03 05:36:05 | 66.93 | no | YES | 86 | YES | 70.66 | YES |
| 2026-09-03 05:36:10 | 66.93 | no | YES | 87 | YES | 72.25 | YES |
| 2026-09-03 05:36:15 | 66.93 | no | YES | 88 | YES | 68.10 | YES |
| 2026-09-03 05:36:20 | 66.93 | no | YES | 89 | YES | 68.10 | YES |
| 2026-09-03 05:36:25 | 66.93 | no | YES | 90 | YES | 70.02 | YES |
| 2026-09-03 05:36:30 | 70.02 | no | YES | 91 | YES | 68.98 | YES |
| 2026-09-03 05:36:35 | 70.02 | no | YES | 92 | YES | 68.98 | YES |
| 2026-09-03 05:36:40 | 70.02 | no | YES | 93 | YES | 70.28 | YES |
| 2026-09-03 05:36:45 | 70.02 | no | YES | 94 | YES | 73.83 | YES |
| 2026-09-03 05:36:50 | 70.02 | no | YES | 95 | YES | 76.06 | YES |
| 2026-09-03 05:36:55 | 70.02 | no | YES | 96 | YES | 76.06 | YES |
| 2026-09-03 05:37:00 | 76.06 | no | YES | 97 | YES | 68.88 | YES |
| 2026-09-03 05:37:05 | 76.06 | no | YES | 98 | YES | 68.88 | YES |
| 2026-09-03 05:37:10 | 76.06 | no | YES | 99 | YES | 66.91 | YES |
| 2026-09-03 05:37:15 | 76.06 | no | YES | 100 | YES | 71.82 | YES |
| 2026-09-03 05:37:20 | 76.06 | no | YES | 101 | YES | 70.52 | YES |
| 2026-09-03 05:37:25 | 76.06 | no | YES | 102 | YES | 70.52 | YES |
| 2026-09-03 05:37:30 | 70.52 | no | YES | 103 | YES | 70.52 | YES |
| 2026-09-03 05:37:35 | 70.52 | no | YES | 104 | YES | 70.21 | YES |
| 2026-09-03 05:37:40 | 70.52 | no | YES | 105 | YES | 72.51 | YES |
| 2026-09-03 05:37:45 | 70.52 | no | YES | 106 | YES | 75.11 | YES |
| 2026-09-03 05:37:50 | 70.52 | no | YES | 107 | YES | 75.11 | YES |
| 2026-09-03 05:37:55 | 70.52 | no | YES | 108 | YES | 75.11 | YES |
| 2026-09-03 05:38:00 | 75.11 | no | YES | 109 | YES | 74.66 | YES |
| 2026-09-03 05:38:05 | 75.11 | no | YES | 110 | YES | 74.33 | YES |
| 2026-09-03 05:38:10 | 75.11 | no | YES | 111 | YES | 73.67 | YES |
| 2026-09-03 05:38:15 | 75.11 | no | YES | 112 | YES | 73.02 | YES |
| 2026-09-03 05:38:20 | 75.11 | no | YES | 113 | YES | 72.69 | YES |
| 2026-09-03 05:38:25 | 75.11 | no | YES | 114 | YES | 73.02 | YES |
| 2026-09-03 05:38:30 | 73.02 | no | YES | 115 | YES | 73.30 | YES |
| 2026-09-03 05:38:35 | 73.02 | no | YES | 116 | YES | 71.33 | YES |
| 2026-09-03 05:38:40 | 73.02 | no | YES | 117 | YES | 73.30 | YES |
| 2026-09-03 05:38:45 | 73.02 | no | YES | 118 | YES | 76.24 | YES |
| 2026-09-03 05:38:50 | 73.02 | no | YES | 119 | YES | 74.93 | YES |
| 2026-09-03 05:38:55 | 73.02 | no | YES | 120 | YES | 74.93 | YES |
| 2026-09-03 05:39:00 | 74.93 | no | YES | 121 | YES | 75.11 | YES |
| 2026-09-03 05:39:05 | 74.93 | no | YES | 122 | YES | 76.42 | YES |
| 2026-09-03 05:39:10 | 74.93 | no | YES | 123 | YES | 74.46 | YES |
| 2026-09-03 05:39:15 | 74.93 | no | YES | 124 | YES | 75.44 | YES |
| 2026-09-03 05:39:20 | 74.93 | no | YES | 125 | YES | 74.78 | YES |
| 2026-09-03 05:39:25 | 74.93 | no | YES | 126 | YES | 74.78 | YES |
| 2026-09-03 05:39:30 | 74.78 | no | YES | 127 | YES | 73.09 | YES |
| 2026-09-03 05:39:35 | 74.78 | no | YES | 128 | YES | 73.09 | YES |
| 2026-09-03 05:39:40 | 74.78 | no | YES | 129 | YES | 74.08 | YES |
| 2026-09-03 05:39:45 | 74.78 | no | YES | 130 | YES | 74.08 | YES |
| 2026-09-03 05:39:50 | 74.78 | no | YES | 131 | YES | 71.76 | YES |
| 2026-09-03 05:39:55 | 74.78 | no | YES | 132 | YES | 72.75 | YES |
| 2026-09-03 05:40:00 | 72.75 | no | YES | 133 | YES | 72.75 | YES |
