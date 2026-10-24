# THE STANDALONE TEST-SCRIPT, Joe 1023. 2026-09-01 01:16:20 .. 2026-09-01 07:15:00 (his cap)
# THE RACE: an instance is a ws4r reversal with *"ws4r oob or ws5r oob, as a race"*.
# the ws2Mage reversal detector is 'mage_rev', xwob 4. fork 2 the ws1r VALUE vs 50, K.side_of.
# fork 2b ws4r and ws1r reversals are lineage's own detector, v4_fast.revs = lift_off.
# the control: ws5r 2026-09-03 00:35:00 = 6.77 (the BANKED k6 rsi8 stc6 line; the
#   DB-ruled line reads 12.48 there - the pair is the drift check, not a mismatch).
# RULED_OK True. STAGE ONE banked 24 instances to out/test_script_bank.json with no price
#   series loaded; the PIVOT is find_pivots on px_smooth at 0.50%, UNRULED, and it is
#   read only in STAGE TWO. The stage guard asserts no mech function can take it.

| the read | value |
|---|---|
| instances - ws4r reversals winning the race | 24 |
| of those, LOW side | 16 |
| of those, HIGH side | 8 |
| the race won by ws4r alone | 9 |
| the race won by ws5r alone | 8 |
| the race won by both alone | 7 |
| instances that printed EXHAUST | 19 |

## the ws4r reversal 2026-09-01 01:16:20, LOW side, race won by both

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 01:16:20 | ws4r 6.91 oob True, ws5r 3.47 oob True, knowable 2026-09-01 01:16:55 |
| the next ws1r reversal, same side of 50 | 2026-09-01 01:27:30 | ws1r 14.24, side -1, knowable 2026-09-01 01:28:05 |
| the next ws2Mage same-side oob | 2026-09-01 01:29:20 | ws2Mage 13.39 |
| **EXHAUST, ws2Mage reversing xwob 4** | **2026-09-01 01:30:45** | _mage_rev sign +1, towards the middle |
| the banked lineage walk from the same anchor | 2026-09-01 01:37:10 | EXHAUST from ws4 |

## the ws4r reversal 2026-09-01 01:27:30, LOW side, race won by ws5r

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 01:27:30 | ws4r 19.93 oob False, ws5r 9.98 oob True, knowable 2026-09-01 01:28:05 |
| the next ws1r reversal, same side of 50 | 2026-09-01 01:29:00 | ws1r 30.11, side -1, knowable 2026-09-01 01:29:35 |
| the next ws2Mage same-side oob | 2026-09-01 01:29:35 | ws2Mage 7.79 |
| **EXHAUST, ws2Mage reversing xwob 4** | **2026-09-01 01:30:45** | _mage_rev sign +1, towards the middle |
| the banked lineage walk from the same anchor | 2026-09-01 01:37:10 | EXHAUST from ws4 |

## the ws4r reversal 2026-09-01 01:32:20, LOW side, race won by ws5r

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 01:32:20 | ws4r 23.64 oob False, ws5r 9.18 oob True, knowable 2026-09-01 01:32:55 |
| the next ws1r reversal, same side of 50 | 2026-09-01 01:47:25 | ws1r 40.88, side -1, knowable 2026-09-01 01:48:00 |
| the next ws2Mage same-side oob | 2026-09-01 02:06:15 | ws2Mage 9.53 |
| **EXHAUST, ws2Mage reversing xwob 4** | **2026-09-01 02:07:00** | _mage_rev sign +1, towards the middle |
| the banked lineage walk from the same anchor | 2026-09-01 02:25:20 | EXHAUST from ws4 |

## the ws4r reversal 2026-09-01 02:23:20, LOW side, race won by both

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 02:23:20 | ws4r 6.21 oob True, ws5r 11.48 oob True, knowable 2026-09-01 02:23:55 |
| the next ws1r reversal, same side of 50 | 2026-09-01 02:33:50 | ws1r 31.96, side -1, knowable 2026-09-01 02:34:25 |
| the next ws2Mage same-side oob | 2026-09-01 02:38:20 | ws2Mage 13.78 |
| **EXHAUST, ws2Mage reversing xwob 4** | **2026-09-01 02:40:15** | _mage_rev sign +1, towards the middle |
| the banked lineage walk from the same anchor | 2026-09-01 02:25:35 | EXHAUST from ws4 |

## the ws4r reversal 2026-09-01 02:31:25, LOW side, race won by ws5r

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 02:31:25 | ws4r 27.51 oob False, ws5r 13.91 oob True, knowable 2026-09-01 02:32:00 |
| the next ws1r reversal, same side of 50 | 2026-09-01 02:33:50 | ws1r 31.96, side -1, knowable 2026-09-01 02:34:25 |
| the next ws2Mage same-side oob | 2026-09-01 02:38:20 | ws2Mage 13.78 |
| **EXHAUST, ws2Mage reversing xwob 4** | **2026-09-01 02:40:15** | _mage_rev sign +1, towards the middle |
| the banked lineage walk from the same anchor | 2026-09-01 02:41:25 | EXHAUST from ws4 |

## the ws4r reversal 2026-09-01 03:13:00, HIGH side, race won by ws5r

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 03:13:00 | ws4r 78.69 oob False, ws5r 89.97 oob True, knowable 2026-09-01 03:13:35 |
| the next ws1r reversal, same side of 50 | 2026-09-01 03:17:20 | ws1r 78.22, side +1, knowable 2026-09-01 03:17:55 |
| the next ws2Mage same-side oob | 2026-09-01 03:30:50 | ws2Mage 91.97 |
| **EXHAUST, ws2Mage reversing xwob 4** | **2026-09-01 03:31:35** | _mage_rev sign -1, towards the middle |
| the banked lineage walk from the same anchor | 2026-09-01 03:25:15 | EXHAUST from ws4 |

## the ws4r reversal 2026-09-01 03:14:15, HIGH side, race won by ws5r

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 03:14:15 | ws4r 80.46 oob False, ws5r 90.20 oob True, knowable 2026-09-01 03:14:50 |
| the next ws1r reversal, same side of 50 | 2026-09-01 03:17:20 | ws1r 78.22, side +1, knowable 2026-09-01 03:17:55 |
| the next ws2Mage same-side oob | 2026-09-01 03:30:50 | ws2Mage 91.97 |
| **EXHAUST, ws2Mage reversing xwob 4** | **2026-09-01 03:31:35** | _mage_rev sign -1, towards the middle |
| the banked lineage walk from the same anchor | 2026-09-01 03:25:15 | EXHAUST from ws4 |

## the ws4r reversal 2026-09-01 03:17:15, HIGH side, race won by ws5r

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 03:17:15 | ws4r 80.48 oob False, ws5r 90.20 oob True, knowable 2026-09-01 03:17:50 |
| the next ws1r reversal, same side of 50 | 2026-09-01 03:20:25 | ws1r 64.83, side +1, knowable 2026-09-01 03:21:00 |
| the next ws2Mage same-side oob | 2026-09-01 03:30:50 | ws2Mage 91.97 |
| **EXHAUST, ws2Mage reversing xwob 4** | **2026-09-01 03:31:35** | _mage_rev sign -1, towards the middle |
| the banked lineage walk from the same anchor | 2026-09-01 03:25:15 | EXHAUST from ws4 |

## the ws4r reversal 2026-09-01 03:20:25, HIGH side, race won by ws5r

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 03:20:25 | ws4r 79.79 oob False, ws5r 85.71 oob True, knowable 2026-09-01 03:21:00 |
| the next ws1r reversal, same side of 50 | 2026-09-01 03:37:25 | ws1r 94.46, side +1, knowable 2026-09-01 03:38:00 |
| the next ws2Mage same-side oob | 2026-09-01 03:38:00 | ws2Mage 103.52 |
| **EXHAUST, ws2Mage reversing xwob 4** | **2026-09-01 03:38:35** | _mage_rev sign -1, towards the middle |
| the banked lineage walk from the same anchor | 2026-09-01 03:38:50 | EXHAUST from ws4 |

## the ws4r reversal 2026-09-01 04:01:50, LOW side, race won by ws4r

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 04:01:50 | ws4r 13.99 oob True, ws5r 28.97 oob False, knowable 2026-09-01 04:02:25 |
| the next ws1r reversal, same side of 50 | 2026-09-01 04:08:20 | ws1r 31.66, side -1, knowable 2026-09-01 04:08:55 |
| the next ws2Mage same-side oob | 2026-09-01 04:57:05 | ws2Mage 8.41 |
| **EXHAUST, ws2Mage reversing xwob 4** | **2026-09-01 04:57:25** | _mage_rev sign +1, towards the middle |
| the banked lineage walk from the same anchor | 2026-09-01 04:25:15 | EXHAUST from ws4 |

## the ws4r reversal 2026-09-01 04:08:20, LOW side, race won by both

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 04:08:20 | ws4r 9.41 oob True, ws5r 13.47 oob True, knowable 2026-09-01 04:08:55 |
| the next ws1r reversal, same side of 50 | 2026-09-01 04:09:40 | ws1r 31.28, side -1, knowable 2026-09-01 04:10:15 |
| the next ws2Mage same-side oob | 2026-09-01 04:57:05 | ws2Mage 8.41 |
| **EXHAUST, ws2Mage reversing xwob 4** | **2026-09-01 04:57:25** | _mage_rev sign +1, towards the middle |
| the banked lineage walk from the same anchor | 2026-09-01 04:25:15 | EXHAUST from ws4 |

## the ws4r reversal 2026-09-01 04:09:20, LOW side, race won by both

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 04:09:20 | ws4r 9.41 oob True, ws5r 13.47 oob True, knowable 2026-09-01 04:09:55 |
| the next ws1r reversal, same side of 50 | 2026-09-01 04:12:40 | ws1r 35.95, side -1, knowable 2026-09-01 04:13:15 |
| the next ws2Mage same-side oob | 2026-09-01 04:57:05 | ws2Mage 8.41 |
| **EXHAUST, ws2Mage reversing xwob 4** | **2026-09-01 04:57:25** | _mage_rev sign +1, towards the middle |
| the banked lineage walk from the same anchor | 2026-09-01 04:25:15 | EXHAUST from ws4 |

## the ws4r reversal 2026-09-01 04:12:00, LOW side, race won by both

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 04:12:00 | ws4r 13.61 oob True, ws5r 6.62 oob True, knowable 2026-09-01 04:12:35 |
| the next ws1r reversal, same side of 50 | 2026-09-01 04:12:40 | ws1r 35.95, side -1, knowable 2026-09-01 04:13:15 |
| the next ws2Mage same-side oob | 2026-09-01 04:57:05 | ws2Mage 8.41 |
| **EXHAUST, ws2Mage reversing xwob 4** | **2026-09-01 04:57:25** | _mage_rev sign +1, towards the middle |
| the banked lineage walk from the same anchor | 2026-09-01 04:25:15 | EXHAUST from ws4 |

## the ws4r reversal 2026-09-01 04:14:40, LOW side, race won by both

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 04:14:40 | ws4r 14.63 oob True, ws5r 6.65 oob True, knowable 2026-09-01 04:15:15 |
| the next ws1r reversal, same side of 50 | 2026-09-01 04:34:00 | ws1r 11.04, side -1, knowable 2026-09-01 04:34:35 |
| the next ws2Mage same-side oob | 2026-09-01 04:57:05 | ws2Mage 8.41 |
| **EXHAUST, ws2Mage reversing xwob 4** | **2026-09-01 04:57:25** | _mage_rev sign +1, towards the middle |
| the banked lineage walk from the same anchor | 2026-09-01 04:38:45 | EXHAUST from ws4 |

## the ws4r reversal 2026-09-01 05:45:10, HIGH side, race won by ws4r

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 05:45:10 | ws4r 94.46 oob True, ws5r 79.97 oob False, knowable 2026-09-01 05:45:45 |
| the next ws1r reversal, same side of 50 | 2026-09-01 05:58:20 | ws1r 53.76, side +1, knowable 2026-09-01 05:58:55 |
| the banked lineage walk from the same anchor | 2026-09-01 06:02:05 | EXHAUST from ws4 |
| the chain stopped | - | no same-side ws2Mage oob |

## the ws4r reversal 2026-09-01 05:47:40, HIGH side, race won by ws4r

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 05:47:40 | ws4r 95.22 oob True, ws5r 80.72 oob False, knowable 2026-09-01 05:48:15 |
| the next ws1r reversal, same side of 50 | 2026-09-01 05:58:20 | ws1r 53.76, side +1, knowable 2026-09-01 05:58:55 |
| the banked lineage walk from the same anchor | 2026-09-01 06:02:05 | EXHAUST from ws4 |
| the chain stopped | - | no same-side ws2Mage oob |

## the ws4r reversal 2026-09-01 05:48:40, HIGH side, race won by ws4r

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 05:48:40 | ws4r 95.18 oob True, ws5r 81.16 oob False, knowable 2026-09-01 05:49:15 |
| the next ws1r reversal, same side of 50 | 2026-09-01 05:58:20 | ws1r 53.76, side +1, knowable 2026-09-01 05:58:55 |
| the banked lineage walk from the same anchor | 2026-09-01 06:02:05 | EXHAUST from ws4 |
| the chain stopped | - | no same-side ws2Mage oob |

## the ws4r reversal 2026-09-01 05:50:05, HIGH side, race won by both

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 05:50:05 | ws4r 93.13 oob True, ws5r 90.05 oob True, knowable 2026-09-01 05:50:40 |
| the next ws1r reversal, same side of 50 | 2026-09-01 05:58:20 | ws1r 53.76, side +1, knowable 2026-09-01 05:58:55 |
| the banked lineage walk from the same anchor | 2026-09-01 06:29:25 | EXHAUST from ws4 |
| the chain stopped | - | no same-side ws2Mage oob |

## the ws4r reversal 2026-09-01 06:13:05, LOW side, race won by ws4r

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 06:13:05 | ws4r 12.72 oob True, ws5r 40.65 oob False, knowable 2026-09-01 06:13:40 |
| the next ws1r reversal, same side of 50 | 2026-09-01 06:25:45 | ws1r 8.34, side -1, knowable 2026-09-01 06:26:20 |
| the next ws2Mage same-side oob | 2026-09-01 06:50:35 | ws2Mage 14.55 |
| **EXHAUST, ws2Mage reversing xwob 4** | **2026-09-01 06:53:20** | _mage_rev sign +1, towards the middle |
| the banked lineage walk from the same anchor | 2026-09-01 06:18:10 | EXHAUST from ws4 |

## the ws4r reversal 2026-09-01 06:14:10, LOW side, race won by ws4r

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 06:14:10 | ws4r 12.25 oob True, ws5r 40.37 oob False, knowable 2026-09-01 06:14:45 |
| the next ws1r reversal, same side of 50 | 2026-09-01 06:25:45 | ws1r 8.34, side -1, knowable 2026-09-01 06:26:20 |
| the next ws2Mage same-side oob | 2026-09-01 06:50:35 | ws2Mage 14.55 |
| **EXHAUST, ws2Mage reversing xwob 4** | **2026-09-01 06:53:20** | _mage_rev sign +1, towards the middle |
| the banked lineage walk from the same anchor | 2026-09-01 06:18:10 | EXHAUST from ws4 |

## the ws4r reversal 2026-09-01 06:16:40, LOW side, race won by ws4r

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 06:16:40 | ws4r 12.53 oob True, ws5r 33.42 oob False, knowable 2026-09-01 06:17:15 |
| the next ws1r reversal, same side of 50 | 2026-09-01 06:25:45 | ws1r 8.34, side -1, knowable 2026-09-01 06:26:20 |
| the next ws2Mage same-side oob | 2026-09-01 06:50:35 | ws2Mage 14.55 |
| **EXHAUST, ws2Mage reversing xwob 4** | **2026-09-01 06:53:20** | _mage_rev sign +1, towards the middle |
| the banked lineage walk from the same anchor | 2026-09-01 07:08:30 | EXHAUST from ws4 |

## the ws4r reversal 2026-09-01 06:20:00, LOW side, race won by ws4r

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 06:20:00 | ws4r 11.38 oob True, ws5r 22.60 oob False, knowable 2026-09-01 06:20:35 |
| the next ws1r reversal, same side of 50 | 2026-09-01 06:25:45 | ws1r 8.34, side -1, knowable 2026-09-01 06:26:20 |
| the next ws2Mage same-side oob | 2026-09-01 06:50:35 | ws2Mage 14.55 |
| **EXHAUST, ws2Mage reversing xwob 4** | **2026-09-01 06:53:20** | _mage_rev sign +1, towards the middle |
| the banked lineage walk from the same anchor | 2026-09-01 07:08:30 | EXHAUST from ws4 |

## the ws4r reversal 2026-09-01 06:28:05, LOW side, race won by ws5r

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 06:28:05 | ws4r 15.76 oob False, ws5r 14.46 oob True, knowable 2026-09-01 06:28:40 |
| the next ws1r reversal, same side of 50 | 2026-09-01 06:40:55 | ws1r 20.25, side -1, knowable 2026-09-01 06:41:30 |
| the next ws2Mage same-side oob | 2026-09-01 06:50:35 | ws2Mage 14.55 |
| **EXHAUST, ws2Mage reversing xwob 4** | **2026-09-01 06:53:20** | _mage_rev sign +1, towards the middle |
| the banked lineage walk from the same anchor | 2026-09-01 06:33:20 | EXHAUST from ws4 |

## the ws4r reversal 2026-09-01 07:01:10, LOW side, race won by ws4r

| the step | the bar | the reading |
|---|---|---|
| ws4r reverses | 2026-09-01 07:01:10 | ws4r 13.54 oob True, ws5r 24.13 oob False, knowable 2026-09-01 07:01:45 |
| the next ws1r reversal, same side of 50 | 2026-09-01 07:14:35 | ws1r 20.17, side -1, knowable 2026-09-01 07:15:10 |
| the banked lineage walk from the same anchor | - | NO REVERSAL from ws4 |
| the chain stopped | - | no same-side ws2Mage oob |

## the scoring - STAGE TWO, on the banked bars

| the ws4r reversal | side | won by | the pivot | EXHAUST, this mech | %% off the pivot | lineage EXHAUST | %% off the pivot | earlier by |
|---|---|---|---|---|---|---|---|---|
| 2026-09-01 01:16:20 | LOW | both | 2026-09-01 01:31:15 | 2026-09-01 01:30:45 | +0.153% | 2026-09-01 01:37:10 | +0.760% | +385 s |
| 2026-09-01 01:27:30 | LOW | ws5r | 2026-09-01 01:31:15 | 2026-09-01 01:30:45 | +0.153% | 2026-09-01 01:37:10 | +0.760% | +385 s |
| 2026-09-01 01:32:20 | LOW | ws5r | 2026-09-01 02:40:00 | 2026-09-01 02:07:00 | +0.553% | 2026-09-01 02:25:20 | +0.575% | +1100 s |
| 2026-09-01 02:23:20 | LOW | both | 2026-09-01 02:40:00 | 2026-09-01 02:40:15 | +0.068% | 2026-09-01 02:25:35 | +0.541% | -880 s |
| 2026-09-01 02:31:25 | LOW | ws5r | 2026-09-01 02:40:00 | 2026-09-01 02:40:15 | +0.068% | 2026-09-01 02:41:25 | +0.063% | +70 s |
| 2026-09-01 03:13:00 | HIGH | ws5r | 2026-09-01 03:38:15 | 2026-09-01 03:31:35 | -0.652% | 2026-09-01 03:25:15 | -1.073% | -380 s |
| 2026-09-01 03:14:15 | HIGH | ws5r | 2026-09-01 03:38:15 | 2026-09-01 03:31:35 | -0.652% | 2026-09-01 03:25:15 | -1.073% | -380 s |
| 2026-09-01 03:17:15 | HIGH | ws5r | 2026-09-01 03:38:15 | 2026-09-01 03:31:35 | -0.652% | 2026-09-01 03:25:15 | -1.073% | -380 s |
| 2026-09-01 03:20:25 | HIGH | ws5r | 2026-09-01 03:38:15 | 2026-09-01 03:38:35 | -0.157% | 2026-09-01 03:38:50 | -0.286% | +15 s |
| 2026-09-01 04:01:50 | LOW | ws4r | 2026-09-01 04:13:25 | 2026-09-01 04:57:25 | +0.034% | 2026-09-01 04:25:15 | +0.340% | -1930 s |
| 2026-09-01 04:08:20 | LOW | both | 2026-09-01 04:13:25 | 2026-09-01 04:57:25 | +0.034% | 2026-09-01 04:25:15 | +0.340% | -1930 s |
| 2026-09-01 04:09:20 | LOW | both | 2026-09-01 04:13:25 | 2026-09-01 04:57:25 | +0.034% | 2026-09-01 04:25:15 | +0.340% | -1930 s |
| 2026-09-01 04:12:00 | LOW | both | 2026-09-01 04:13:25 | 2026-09-01 04:57:25 | +0.034% | 2026-09-01 04:25:15 | +0.340% | -1930 s |
| 2026-09-01 04:14:40 | LOW | both | 2026-09-01 04:58:10 | 2026-09-01 04:57:25 | +0.119% | 2026-09-01 04:38:45 | +0.363% | -1120 s |
| 2026-09-01 05:45:10 | HIGH | ws4r | 2026-09-01 06:17:15 | no same-side ws2Mage oob | - | 2026-09-01 06:02:05 | -0.045% | - |
| 2026-09-01 05:47:40 | HIGH | ws4r | 2026-09-01 06:17:15 | no same-side ws2Mage oob | - | 2026-09-01 06:02:05 | -0.045% | - |
| 2026-09-01 05:48:40 | HIGH | ws4r | 2026-09-01 06:17:15 | no same-side ws2Mage oob | - | 2026-09-01 06:02:05 | -0.045% | - |
| 2026-09-01 05:50:05 | HIGH | both | 2026-09-01 06:17:15 | no same-side ws2Mage oob | - | 2026-09-01 06:29:25 | -0.374% | - |
| 2026-09-01 06:13:05 | LOW | ws4r | 2026-09-01 06:24:20 | 2026-09-01 06:53:20 | -0.254% | 2026-09-01 06:18:10 | +1.045% | -2110 s |
| 2026-09-01 06:14:10 | LOW | ws4r | 2026-09-01 06:24:20 | 2026-09-01 06:53:20 | -0.254% | 2026-09-01 06:18:10 | +1.045% | -2110 s |
| 2026-09-01 06:16:40 | LOW | ws4r | 2026-09-01 06:24:20 | 2026-09-01 06:53:20 | -0.254% | 2026-09-01 07:08:30 | -0.384% | +910 s |
| 2026-09-01 06:20:00 | LOW | ws4r | 2026-09-01 06:24:20 | 2026-09-01 06:53:20 | -0.254% | 2026-09-01 07:08:30 | -0.384% | +910 s |
| 2026-09-01 06:28:05 | LOW | ws5r | 2026-09-01 07:14:05 | 2026-09-01 06:53:20 | +0.661% | 2026-09-01 06:33:20 | +1.591% | -1200 s |
| 2026-09-01 07:01:10 | LOW | ws4r | 2026-09-01 07:14:05 | no same-side ws2Mage oob | - | NO REVERSAL | - | - |

| the summary | value |
|---|---|
| instances | 24 |
| instances where both this mech and lineage printed EXHAUST | 19 |
| this mech, distance off the pivot, mean of 19 | 0.265% |
| lineage, distance off the pivot, mean of 19 | 0.652% |
| this mech closer on | 18 of 19 |
| the mech is earlier by, median | -380 s |
| the mech is earlier by, min | -2110 s |
| the mech is earlier by, max | +1100 s |
| instances that stopped: no same-side ws2Mage oob | 5 |
