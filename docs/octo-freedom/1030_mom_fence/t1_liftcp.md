# THE t1 CADENCE LIST, 2026-09-03 05:30:00 .. 2026-09-03 07:30:00
# the new t1: gcws30b at wob 6 bars = 30 s | the r gate: ws1r past (44.0, 56.0) at its stamp
# the pre-1031 t1: ws1b at wob 12 bars = 60 s | the r gate: ws1r on the target side of 50

| the read | low side | high side |
|---|---|---|
| pre-1031 t1 cadences, ws1b wob 12, r past 50 | 0 | 2 |
| new t1, gcws30b wob 6, r past 56, grace on the CROSS bar | 0 | 3 |
| new t1, same but grace on the CONFIRM bar | 0 | 3 |
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

## the new t1 cadence list, low side, grace on the CROSS bar - 0 cadences

| the cadence bar | why |
|---|---|

## the new t1 cadence list, high side, grace on the CROSS bar - 3 cadences

| the cadence bar | why |
|---|---|
| 2026-09-03 05:55:00 | gcws30b journey 05:50:00..05:54:20 reached 97.04 past the 95.0 fence, back inside the 85.0 ib fence 05:53:30, ws1r reversed 05:55:00 inside the 120s grace from the cross bar 05:53:30, r 83.60 past the 56.0 fence, stamp 05:55:00, hold 6 bars, ib dwell 12 bars |
| 2026-09-03 06:42:25 | gcws30b journey 06:34:00..06:42:20 reached 124.19 past the 95.0 fence, ws1r reversed 06:41:00 during, r 70.67 past the 56.0 fence, stamp 06:41:00, ib 85.0 cross 06:41:30 hold 6 bars, ib dwell 12 bars |
| 2026-09-03 07:07:25 | gcws30b journey 07:04:30..07:07:20 reached 103.09 past the 95.0 fence, ws1r reversed 07:07:00 during, r 87.61 past the 56.0 fence, stamp 07:07:00, ib 85.0 cross 07:06:30 hold 6 bars, ib dwell 12 bars |

