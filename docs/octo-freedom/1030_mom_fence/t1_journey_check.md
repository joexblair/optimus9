# THE t1 CADENCE LIST, 2026-09-03 05:00:00 .. 2026-09-03 05:40:00
# the new t1: gcws30b at wob 6 bars = 30 s | the r gate: ws1r past (44.0, 56.0) at its stamp
# the pre-1031 t1: ws1b at wob 12 bars = 60 s | the r gate: ws1r on the target side of 50

| the read | low side | high side |
|---|---|---|
| pre-1031 t1 cadences, ws1b wob 12, r past 50 | 0 | 0 |
| new t1, gcws30b wob 6, r past 56, grace on the CROSS bar | 1 | 0 |
| new t1, same but grace on the CONFIRM bar | 1 | 0 |
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

## the new t1 cadence list, low side, grace on the CROSS bar - 1 cadences

| the cadence bar | why |
|---|---|
| 2026-09-03 05:25:25 | gcws30b journey 05:17:30..05:24:25 reached -4.51 past the 5.0 fence, ws1r reversed 05:24:15 during, r 0.50 past the 44.0 fence, stamp 05:24:15, ib 15.0 cross 05:24:30 hold 6 bars, ib dwell 12 bars |

## the new t1 cadence list, high side, grace on the CROSS bar - 0 cadences

| the cadence bar | why |
|---|---|

