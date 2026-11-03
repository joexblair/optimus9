# fdm2 | TAPE 1632960 bars, ends 2026-10-04 23:59:55 | RULED_OK True
# THE WALK RUNS 2026-09-15 00:00:00 .. 2026-09-15 23:59:55 - HIS one-day bound
# THE STOP IS ON: FDM_MAE_CAP 1.10% adverse from the open, his "yes, move it to default"

| the knob | value | what it is |
|---|---|---|
| FDM_FNC_2080 | 20 | his "fdm-20-80-fnc" - step 1 AND the population. "ex" includes oob |
| FDM_STEP1_ABOVE_TF | 3 | step 1 scans STRICTLY above this TF, so ws4..ws30 = 27 lines |
| FDM_POP_LO | 3 | the reversal population floor, so ws3..ws30 = 28 before the filter |
| FDM_M3_FNC | 25 | ws3Mage's fence in the preamble, 25 -> 25/75 |
| FDM_X10_WOB | 24 | the ws10x race hold, bars. His 1103 "use 24" |
| FDM_X10_GRACE_PCT | 40 | his "fdm-ws10x-cad-grace" - the grace walk's floor, % |
| FDM_X10_TRADE_PCT | 50 | the grace walk's rev-trade threshold, % |
| FDM_X10_GRACE_MIN | 5 | the grace walk's length, minutes |
| FDM_MAE_CAP | 1.1 | the stop, % adverse from the open |
| FDM_X10_FRM | cross | must the race CROSS follow the cadence event, or only its CONFIRM |
| FDM_REV_FROM | event | where the reversal count starts: the cadence event bar, or that event's window open |
| LIFT_WOB | 8 | the lift-off hold; the reversal STAMP is lift + 7 bars = 35 s |

| the open | value |
|---|---|
| the re-entry signal bar | 2026-09-15 00:36:30 |
| the gcws30b window side | HIGH oob |
| the trade | SHORT |
| its target side | LOW |
| the open price bar | 2026-09-15 00:36:35 - the router's "just OPEN", 1 bar |
| why | gcws30b HIGH window 00:33:30..00:36:30, ws1r AND (ws2r or ws3r) seen past the 75.0 fence - ws1 00:35:20, ws2 00:34:05, ws3 00:33:30 - gate TRUE at the ib cross |

## leg 2026-09-15 00:36:35 | SHORT | target side LOW | fdm re-entry 2026-09-15 00:36:30

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 00:36:35 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 00:36:35 to 2026-09-15 00:52:35: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-09-15 00:46:25 to 2026-09-15 00:47:10: 10 bars, peak 14.31, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-09-15 00:46:25 to 2026-09-15 00:47:10: 10 bars, peak 14.31 | the ws1r oob->ib cross @ 2026-09-15 00:47:20: ws1r 18.29, held 2 bars | the cascade anchor @ 2026-09-15 00:47:15: ws1Mage extremum, 5 s before the cross | the cascade at the stamp @ 2026-09-15 00:47:15: down | down | the low cluster ws1 to ws3, 3 lines, falling COUNTS | the high cluster ws1 to ws3, 3 lines, falling COUNTS | the end-to-end diff +3.04 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-09-15 00:47:20: ws1Mage 14.9875, YES | branch A does not fire - branch B @ 2026-09-15 00:47:20: the cascade is not counter. walk to ws2r oob, inside the cap to 2026-09-15 00:52:35 | the cap expired @ 2026-09-15 00:52:35: no ws2r cross and no ws1Mage route inside it - the trade stays open |
| 2026-09-15 01:03:00 | WALK | cadence event, 5 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-15 01:20:00, the ws10x-cadence confirms 2026-09-15 01:21:55) |
| 2026-09-15 01:21:55 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-09-15 01:20:00 and confirmed here. 14 of 17 reversed since 2026-09-15 01:03:00 (event) = 82.4% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-15 01:22:05 | LONG | target side HIGH | rev-trade 2026-09-15 01:21:55

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 01:22:05 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 01:22:05 to 2026-09-15 01:38:05: 192 bars = 16 min from the open | no ws1r oob run on the target-side inside the cap @ 2026-09-15 01:38:05: the cap expired - the trade stays open |

## leg 2026-09-15 03:17:05 | LONG | target side HIGH | fdm re-entry 2026-09-15 03:17:00, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 03:25:10 | SAVIOUR SAVIOUR REV | v4saviour SAVIOUR REV from ws1r | the cap @ 2026-09-15 03:17:05 to 2026-09-15 03:33:05: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-09-15 03:22:00 to 2026-09-15 03:25:00: 37 bars, peak 100.00, 2 run(s) inside the cap | the ws1r oob run that crossed @ 2026-09-15 03:22:00 to 2026-09-15 03:25:00: 37 bars, peak 100.00 | the ws1r oob->ib cross @ 2026-09-15 03:25:10: ws1r 84.01, held 2 bars | the cascade anchor @ 2026-09-15 03:23:25: ws1Mage extremum, 105 s before the cross | the cascade at the stamp @ 2026-09-15 03:23:25: down | down | the low cluster ws1 to ws3, 3 lines, falling COUNTS | the high cluster ws1 to ws3, 3 lines, falling COUNTS | the end-to-end diff +21.89 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-09-15 03:25:10: ws1Mage 31.1770, no | branch A fires @ 2026-09-15 03:25:10: counter cascade and ws1Mage not past 50 - end the trade, rev-trade on the next bar |

## leg 2026-09-15 03:25:20 | SHORT | target side LOW | rev-trade 2026-09-15 03:25:10

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 03:25:20 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 03:25:20 to 2026-09-15 03:41:20: 192 bars = 16 min from the open | no ws1r oob run on the target-side inside the cap @ 2026-09-15 03:41:20: the cap expired - the trade stays open |
| 2026-09-15 04:41:00 | REV-TRADE | cadence event, 0 of 27 lines ws4..ws30 printing ex-20/80 AND towards - his "if the answer is no, then rev-trade" |

## leg 2026-09-15 04:41:10 | LONG | target side HIGH | rev-trade 2026-09-15 04:41:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 04:50:30 | SAVIOUR SAVIOUR REV | v4saviour SAVIOUR REV from ws1r | the cap @ 2026-09-15 04:41:10 to 2026-09-15 04:57:10: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-09-15 04:45:00 to 2026-09-15 04:50:20: 65 bars, peak 96.67, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-09-15 04:45:00 to 2026-09-15 04:50:20: 65 bars, peak 96.67 | the ws1r oob->ib cross @ 2026-09-15 04:50:30: ws1r 82.39, held 2 bars | the cascade anchor @ 2026-09-15 04:49:30: ws1Mage extremum, 60 s before the cross | the cascade at the stamp @ 2026-09-15 04:49:30: down | down | the low cluster ws1 to ws3, 3 lines, falling COUNTS | the high cluster ws1 to ws3, 3 lines, falling COUNTS | the end-to-end diff +3.76 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-09-15 04:50:30: ws1Mage 44.9594, no | branch A fires @ 2026-09-15 04:50:30: counter cascade and ws1Mage not past 50 - end the trade, rev-trade on the next bar |

## leg 2026-09-15 04:50:40 | SHORT | target side LOW | rev-trade 2026-09-15 04:50:30

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 04:50:40 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 04:50:40 to 2026-09-15 05:06:40: 192 bars = 16 min from the open | no ws1r oob run on the target-side inside the cap @ 2026-09-15 05:06:40: the cap expired - the trade stays open |
| 2026-09-15 05:21:00 | REV-TRADE | cadence event, 0 of 27 lines ws4..ws30 printing ex-20/80 AND towards - his "if the answer is no, then rev-trade" |

## leg 2026-09-15 05:21:10 | LONG | target side HIGH | rev-trade 2026-09-15 05:21:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 05:21:10 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 05:21:10 to 2026-09-15 05:37:10: 192 bars = 16 min from the open | no ws1r oob run on the target-side inside the cap @ 2026-09-15 05:37:10: the cap expired - the trade stays open |
| 2026-09-15 09:03:00 | WALK | cadence event, 6 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-15 09:10:50, the ws10x-cadence confirms 2026-09-15 09:12:45) |
| 2026-09-15 09:12:45 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-09-15 09:10:50 and confirmed here. 6 of 12 reversed since 2026-09-15 09:03:00 (event) = 50.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-15 09:12:55 | SHORT | target side LOW | rev-trade 2026-09-15 09:12:45

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 09:14:45 | SAVIOUR SAVIOUR REV | v4saviour SAVIOUR REV from ws1r | the cap @ 2026-09-15 09:12:55 to 2026-09-15 09:28:55: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-09-15 09:14:00 to 2026-09-15 09:14:35: 8 bars, peak 13.76, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-09-15 09:14:00 to 2026-09-15 09:14:35: 8 bars, peak 13.76 | the ws1r oob->ib cross @ 2026-09-15 09:14:45: ws1r 17.28, held 2 bars | the cascade anchor @ 2026-09-15 09:14:15: ws1Mage extremum, 30 s before the cross | the cascade at the stamp @ 2026-09-15 09:14:15: up | up | the low cluster ws1 to ws3, 3 lines, rising COUNTS | the high cluster ws1 to ws3, 3 lines, rising COUNTS | the end-to-end diff -14.86 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-09-15 09:14:45: ws1Mage 67.4657, no | branch A fires @ 2026-09-15 09:14:45: counter cascade and ws1Mage not past 50 - end the trade, rev-trade on the next bar |

## leg 2026-09-15 09:14:55 | LONG | target side HIGH | rev-trade 2026-09-15 09:14:45

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 09:14:55 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 09:14:55 to 2026-09-15 09:30:55: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-09-15 09:27:10 to 2026-09-15 09:27:50: 9 bars, peak 91.47, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-09-15 09:27:10 to 2026-09-15 09:27:50: 9 bars, peak 91.47 | the ws1r oob->ib cross @ 2026-09-15 09:28:00: ws1r 71.40, held 2 bars | the cascade anchor @ 2026-09-15 09:27:15: ws1Mage extremum, 45 s before the cross | the cascade at the stamp @ 2026-09-15 09:27:15: up | up | the low cluster ws1 to ws3, 3 lines, rising COUNTS | the high cluster ws1 to ws3, 3 lines, rising COUNTS | the end-to-end diff -11.31 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-09-15 09:28:00: ws1Mage 57.0636, YES | branch A does not fire - branch B @ 2026-09-15 09:28:00: the cascade is not counter. walk to ws2r oob, inside the cap to 2026-09-15 09:30:55 | the cap expired @ 2026-09-15 09:30:55: no ws2r cross and no ws1Mage route inside it - the trade stays open |
| 2026-09-15 09:41:00 | WALK | cadence event, 12 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10r 2026-09-15 09:55:00, the ws10x-cadence confirms 2026-09-15 09:56:55) |
| 2026-09-15 09:56:55 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10r 2026-09-15 09:55:00 and confirmed here. 14 of 18 reversed since 2026-09-15 09:41:00 (event) = 77.8% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-15 09:57:05 | SHORT | target side LOW | rev-trade 2026-09-15 09:56:55

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 10:07:55 | SAVIOUR SAVIOUR REV | v4saviour SAVIOUR REV from ws2r | the cap @ 2026-09-15 09:57:05 to 2026-09-15 10:13:05: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-09-15 10:00:00 to 2026-09-15 10:00:55: 12 bars, peak 14.70, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-09-15 10:00:00 to 2026-09-15 10:00:55: 12 bars, peak 14.70 | the ws1r oob->ib cross @ 2026-09-15 10:01:05: ws1r 18.34, held 2 bars | the cascade anchor @ 2026-09-15 09:59:05: ws1Mage extremum, 120 s before the cross | the cascade at the stamp @ 2026-09-15 09:59:05: up | up | the low cluster ws1 to ws3, 3 lines, rising COUNTS | the high cluster ws1 to ws3, 3 lines, rising COUNTS | the end-to-end diff -31.05 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-09-15 10:01:05: ws1Mage 39.6531, YES | branch A does not fire - branch B @ 2026-09-15 10:01:05: ws1Mage is past 50 towards the target-side. walk to ws2r oob, inside the cap to 2026-09-15 10:13:05 | the ws2r oob run @ 2026-09-15 10:07:40 to 2026-09-15 10:07:45: 2 bars, peak 14.31 | the ws2r oob->ib cross @ 2026-09-15 10:07:55: ws2r 16.61, 62 bars inside the cap | the cascade anchor @ 2026-09-15 10:07:40: ws1Mage extremum, 15 s before the cross | the cascade at the stamp @ 2026-09-15 10:07:40: up | up | the low cluster ws1 to ws3, 3 lines, rising COUNTS | the high cluster ws1 to ws3, 3 lines, rising COUNTS | the end-to-end diff -41.33 | zoom 2 rungs, min 3 lines | ws2Mage past 50 towards the target-side @ 2026-09-15 10:07:55: ws2Mage 56.9800, no | branch B fires @ 2026-09-15 10:07:55: counter cascade and ws2Mage not past 50 - end the trade, rev-trade on the next bar |

## leg 2026-09-15 10:08:05 | LONG | target side HIGH | rev-trade 2026-09-15 10:07:55

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 10:08:05 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 10:08:05 to 2026-09-15 10:24:05: 192 bars = 16 min from the open | no ws1r oob run on the target-side inside the cap @ 2026-09-15 10:24:05: the cap expired - the trade stays open |

## leg 2026-09-15 11:59:35 | SHORT | target side LOW | fdm re-entry 2026-09-15 11:59:30, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 11:59:35 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 11:59:35 to 2026-09-15 12:15:35: 192 bars = 16 min from the open | no ws1r oob run on the target-side inside the cap @ 2026-09-15 12:15:35: the cap expired - the trade stays open |

## leg 2026-09-15 12:57:35 | SHORT | target side LOW | fdm re-entry 2026-09-15 12:57:30, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 13:00:10 | SAVIOUR SAVIOUR REV | v4saviour SAVIOUR REV from ws1r | the cap @ 2026-09-15 12:57:35 to 2026-09-15 13:13:35: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-09-15 13:00:00 to 2026-09-15 13:00:00: 1 bars, peak 14.80, 3 run(s) inside the cap | the ws1r oob run that crossed @ 2026-09-15 13:00:00 to 2026-09-15 13:00:00: 1 bars, peak 14.80 | the ws1r oob->ib cross @ 2026-09-15 13:00:10: ws1r 18.58, held 2 bars | the cascade anchor @ 2026-09-15 12:58:20: ws1Mage extremum, 110 s before the cross | the cascade at the stamp @ 2026-09-15 12:58:20: up | up | the low cluster ws1 to ws3, 3 lines, rising COUNTS | the high cluster ws1 to ws3, 3 lines, rising COUNTS | the end-to-end diff -19.09 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-09-15 13:00:10: ws1Mage 71.9319, no | branch A fires @ 2026-09-15 13:00:10: counter cascade and ws1Mage not past 50 - end the trade, rev-trade on the next bar |

## leg 2026-09-15 13:00:20 | LONG | target side HIGH | rev-trade 2026-09-15 13:00:10

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 13:00:20 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 13:00:20 to 2026-09-15 13:16:20: 192 bars = 16 min from the open | no ws1r oob run on the target-side inside the cap @ 2026-09-15 13:16:20: the cap expired - the trade stays open |

## leg 2026-09-15 13:40:35 | LONG | target side HIGH | fdm re-entry 2026-09-15 13:40:30, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 13:40:35 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 13:40:35 to 2026-09-15 13:56:35: 192 bars = 16 min from the open | no ws1r oob run on the target-side inside the cap @ 2026-09-15 13:56:35: the cap expired - the trade stays open |

## leg 2026-09-15 14:44:05 | LONG | target side HIGH | fdm re-entry 2026-09-15 14:44:00, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 14:44:05 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 14:44:05 to 2026-09-15 15:00:05: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-09-15 14:57:00 to 2026-09-15 15:00:55: 48 bars, peak 100.00, 1 run(s) inside the cap | the ws1r oob->ib cross @ 2026-09-15 15:01:05: ws1r 75.26, past the cap at 2026-09-15 15:00:05 - the trade stays open |

## leg 2026-09-15 15:30:05 | SHORT | target side LOW | fdm re-entry 2026-09-15 15:30:00, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 15:30:05 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 15:30:05 to 2026-09-15 15:46:05: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-09-15 15:32:00 to 2026-09-15 15:33:05: 14 bars, peak 14.03, 5 run(s) inside the cap | the ws1r cross is a flicker @ 2026-09-15 15:33:10: ws1r 15.33, back oob inside the 2-bar hold - not a cross, scan on | the ws1r oob run that crossed @ 2026-09-15 15:33:15 to 2026-09-15 15:33:25: 3 bars, peak 14.75 | the ws1r oob->ib cross @ 2026-09-15 15:33:35: ws1r 17.16, held 2 bars | the cascade anchor @ 2026-09-15 15:32:35: ws1Mage extremum, 60 s before the cross | the cascade at the stamp @ 2026-09-15 15:32:35: down | down | the low cluster ws1 to ws3, 3 lines, falling COUNTS | the high cluster ws1 to ws3, 3 lines, falling COUNTS | the end-to-end diff +18.94 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-09-15 15:33:35: ws1Mage 76.5437, no | branch A does not fire - branch B @ 2026-09-15 15:33:35: the cascade is not counter. walk to ws2r oob, inside the cap to 2026-09-15 15:46:05 | ws1Mage left the past-50 gate @ 2026-09-15 15:34:10: held 8 bars = 40 s, ws1Mage 67.4915 at the stamp | the ws1Mage target-side extrema anchor @ 2026-09-15 15:34:10: ws1Mage 67.4915, 0 s before the stamp | the routed cascade at the anchor @ 2026-09-15 15:34:10: down | down | the low cluster ws1 to ws3, 3 lines, falling COUNTS | the high cluster ws1 to ws3, 3 lines, falling COUNTS | the end-to-end diff +16.34 | zoom 2 rungs, min 3 lines | the route does not fire @ 2026-09-15 15:34:10: the cascade is not counter - the trade stays open, v4saviour is complete |
| 2026-09-15 17:14:00 | REV-TRADE | cadence event, 0 of 27 lines ws4..ws30 printing ex-20/80 AND towards - his "if the answer is no, then rev-trade" |

## leg 2026-09-15 17:14:10 | LONG | target side HIGH | rev-trade 2026-09-15 17:14:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 17:18:05 | SAVIOUR SAVIOUR REV | v4saviour SAVIOUR REV from ws1r | the cap @ 2026-09-15 17:14:10 to 2026-09-15 17:30:10: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-09-15 17:16:20 to 2026-09-15 17:17:55: 20 bars, peak 89.28, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-09-15 17:16:20 to 2026-09-15 17:17:55: 20 bars, peak 89.28 | the ws1r oob->ib cross @ 2026-09-15 17:18:05: ws1r 80.48, held 2 bars | the cascade anchor @ 2026-09-15 17:17:25: ws1Mage extremum, 40 s before the cross | the cascade at the stamp @ 2026-09-15 17:17:25: down | down | the low cluster ws1 to ws3, 3 lines, falling COUNTS | the high cluster ws1 to ws3, 3 lines, falling COUNTS | the end-to-end diff +0.03 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-09-15 17:18:05: ws1Mage 31.8143, no | branch A fires @ 2026-09-15 17:18:05: counter cascade and ws1Mage not past 50 - end the trade, rev-trade on the next bar |

## leg 2026-09-15 17:18:15 | SHORT | target side LOW | rev-trade 2026-09-15 17:18:05

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 17:18:15 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 17:18:15 to 2026-09-15 17:34:15: 192 bars = 16 min from the open | no ws1r oob run on the target-side inside the cap @ 2026-09-15 17:34:15: the cap expired - the trade stays open |

## leg 2026-09-15 17:39:05 | SHORT | target side LOW | fdm re-entry 2026-09-15 17:39:00, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 17:46:05 | SAVIOUR SAVIOUR REV | v4saviour SAVIOUR REV from ws1r | the cap @ 2026-09-15 17:39:05 to 2026-09-15 17:55:05: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-09-15 17:42:00 to 2026-09-15 17:45:55: 48 bars, peak 13.07, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-09-15 17:42:00 to 2026-09-15 17:45:55: 48 bars, peak 13.07 | the ws1r oob->ib cross @ 2026-09-15 17:46:05: ws1r 25.48, held 2 bars | the cascade anchor @ 2026-09-15 17:44:05: ws1Mage extremum, 120 s before the cross | the cascade at the stamp @ 2026-09-15 17:44:05: up | up | the low cluster ws1 to ws3, 3 lines, rising COUNTS | the high cluster ws1 to ws3, 3 lines, rising COUNTS | the end-to-end diff -14.10 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-09-15 17:46:05: ws1Mage 73.0728, no | branch A fires @ 2026-09-15 17:46:05: counter cascade and ws1Mage not past 50 - end the trade, rev-trade on the next bar |

## leg 2026-09-15 17:46:15 | LONG | target side HIGH | rev-trade 2026-09-15 17:46:05

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 17:46:15 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 17:46:15 to 2026-09-15 18:02:15: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-09-15 17:51:00 to 2026-09-15 17:52:15: 16 bars, peak 97.74, 2 run(s) inside the cap | the ws1r oob run that crossed @ 2026-09-15 17:51:00 to 2026-09-15 17:52:15: 16 bars, peak 97.74 | the ws1r oob->ib cross @ 2026-09-15 17:52:25: ws1r 82.05, held 2 bars | the cascade anchor @ 2026-09-15 17:51:30: ws1Mage extremum, 55 s before the cross | the cascade at the stamp @ 2026-09-15 17:51:30: up | up | the low cluster ws1 to ws3, 3 lines, rising COUNTS | the high cluster ws1 to ws3, 3 lines, rising COUNTS | the end-to-end diff -17.72 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-09-15 17:52:25: ws1Mage 74.7396, YES | branch A does not fire - branch B @ 2026-09-15 17:52:25: the cascade is not counter. walk to ws2r oob, inside the cap to 2026-09-15 18:02:15 | the cap expired @ 2026-09-15 18:02:15: no ws2r cross and no ws1Mage route inside it - the trade stays open |

## leg 2026-09-15 18:25:35 | LONG | target side HIGH | fdm re-entry 2026-09-15 18:25:30, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 18:25:35 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 18:25:35 to 2026-09-15 18:41:35: 192 bars = 16 min from the open | no ws1r oob run on the target-side inside the cap @ 2026-09-15 18:41:35: the cap expired - the trade stays open |

## leg 2026-09-15 18:51:35 | LONG | target side HIGH | fdm re-entry 2026-09-15 18:51:30, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 18:58:05 | SAVIOUR SAVIOUR REV | v4saviour SAVIOUR REV from ws1r | the cap @ 2026-09-15 18:51:35 to 2026-09-15 19:07:35: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-09-15 18:55:00 to 2026-09-15 18:57:55: 36 bars, peak 100.00, 3 run(s) inside the cap | the ws1r oob run that crossed @ 2026-09-15 18:55:00 to 2026-09-15 18:57:55: 36 bars, peak 100.00 | the ws1r oob->ib cross @ 2026-09-15 18:58:05: ws1r 83.12, held 2 bars | the cascade anchor @ 2026-09-15 18:56:15: ws1Mage extremum, 110 s before the cross | the cascade at the stamp @ 2026-09-15 18:56:15: down | down | the low cluster ws1 to ws3, 3 lines, falling COUNTS | the high cluster ws1 to ws3, 3 lines, falling COUNTS | the end-to-end diff +22.34 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-09-15 18:58:05: ws1Mage 36.0510, no | branch A fires @ 2026-09-15 18:58:05: counter cascade and ws1Mage not past 50 - end the trade, rev-trade on the next bar |

## leg 2026-09-15 18:58:15 | SHORT | target side LOW | rev-trade 2026-09-15 18:58:05

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 18:58:15 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 18:58:15 to 2026-09-15 19:14:15: 192 bars = 16 min from the open | no ws1r oob run on the target-side inside the cap @ 2026-09-15 19:14:15: the cap expired - the trade stays open |

## leg 2026-09-15 19:30:35 | LONG | target side HIGH | fdm re-entry 2026-09-15 19:30:30, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 19:30:35 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 19:30:35 to 2026-09-15 19:46:35: 192 bars = 16 min from the open | no ws1r oob run on the target-side inside the cap @ 2026-09-15 19:46:35: the cap expired - the trade stays open |
| 2026-09-15 21:00:00 | WALK | cadence event, 1 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-15 21:00:30, the ws10x-cadence confirms 2026-09-15 21:02:25) |
| 2026-09-15 21:02:25 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-09-15 21:00:30 and confirmed here. 4 of 5 reversed since 2026-09-15 21:00:00 (event) = 80.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-15 21:02:35 | SHORT | target side LOW | rev-trade 2026-09-15 21:02:25

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 21:03:25 | SAVIOUR SAVIOUR REV | v4saviour SAVIOUR REV from ws1r | the cap @ 2026-09-15 21:02:35 to 2026-09-15 21:18:35: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-09-15 21:03:10 to 2026-09-15 21:03:15: 2 bars, peak 14.18, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-09-15 21:03:10 to 2026-09-15 21:03:15: 2 bars, peak 14.18 | the ws1r oob->ib cross @ 2026-09-15 21:03:25: ws1r 15.69, held 2 bars | the cascade anchor @ 2026-09-15 21:02:30: ws1Mage extremum, 55 s before the cross | the cascade at the stamp @ 2026-09-15 21:02:30: up | up | the low cluster ws1 to ws3, 3 lines, rising COUNTS | the high cluster ws1 to ws3, 3 lines, rising COUNTS | the end-to-end diff -6.00 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-09-15 21:03:25: ws1Mage 66.4020, no | branch A fires @ 2026-09-15 21:03:25: counter cascade and ws1Mage not past 50 - end the trade, rev-trade on the next bar |

## leg 2026-09-15 21:03:35 | LONG | target side HIGH | rev-trade 2026-09-15 21:03:25

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 21:03:35 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 21:03:35 to 2026-09-15 21:19:35: 192 bars = 16 min from the open | no ws1r oob run on the target-side inside the cap @ 2026-09-15 21:19:35: the cap expired - the trade stays open |

## leg 2026-09-15 21:31:05 | LONG | target side HIGH | fdm re-entry 2026-09-15 21:31:00, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 21:31:05 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 21:31:05 to 2026-09-15 21:47:05: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-09-15 21:43:00 to 2026-09-15 21:43:45: 10 bars, peak 87.52, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-09-15 21:43:00 to 2026-09-15 21:43:45: 10 bars, peak 87.52 | the ws1r oob->ib cross @ 2026-09-15 21:43:55: ws1r 84.36, held 2 bars | the cascade anchor @ 2026-09-15 21:43:15: ws1Mage extremum, 40 s before the cross | the cascade at the stamp @ 2026-09-15 21:43:15: up | up | the low cluster ws1 to ws3, 3 lines, rising COUNTS | the high cluster ws1 to ws3, 3 lines, rising COUNTS | the end-to-end diff -1.83 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-09-15 21:43:55: ws1Mage 43.2628, no | branch A does not fire - branch B @ 2026-09-15 21:43:55: the cascade is not counter. walk to ws2r oob, inside the cap to 2026-09-15 21:47:05 | ws1Mage left the past-50 gate @ 2026-09-15 21:44:30: held 8 bars = 40 s, ws1Mage 44.6343 at the stamp | the ws1Mage target-side extrema anchor @ 2026-09-15 21:43:30: ws1Mage 45.1510, 60 s before the stamp | the routed cascade at the anchor @ 2026-09-15 21:43:30: up | up | the low cluster ws1 to ws3, 3 lines, rising COUNTS | the high cluster ws1 to ws3, 3 lines, rising COUNTS | the end-to-end diff -2.35 | zoom 2 rungs, min 3 lines | the route does not fire @ 2026-09-15 21:44:30: the cascade is not counter - the trade stays open, v4saviour is complete |

## leg 2026-09-15 22:59:35 | SHORT | target side LOW | fdm re-entry 2026-09-15 22:59:30, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 22:59:35 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 22:59:35 to 2026-09-15 23:15:35: 192 bars = 16 min from the open | no ws1r oob run on the target-side inside the cap @ 2026-09-15 23:15:35: the cap expired - the trade stays open |

## leg 2026-09-15 23:12:35 | SHORT | target side LOW | fdm re-entry 2026-09-15 23:12:30, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 23:12:35 | SAVIOUR STAYS OPEN | the cap @ 2026-09-15 23:12:35 to 2026-09-15 23:28:35: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-09-15 23:28:00 to 2026-09-15 23:28:25: 6 bars, peak 11.39, 2 run(s) inside the cap | the ws1r cross is a flicker @ 2026-09-15 23:28:30: ws1r 15.04, back oob inside the 2-bar hold - not a cross, scan on | the ws1r oob->ib cross @ 2026-09-15 23:34:05: ws1r 25.65, past the cap at 2026-09-15 23:28:35 - the trade stays open |

## the 28 eligible lines at every ws10x-cadence | ws3..ws30

| the ws10x-cadence | the trade it was deciding | ex-20/80 at least once | contributed a reversal | silent - ex-fence but no reversal | never ex-fence |
|---|---|---|---|---|---|
| 2026-09-15 01:21:55 | 2026-09-15 00:36:35 SHORT | 17 of 28 - ws3, ws4, ws5, ws6, ws14, ws15, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 | 14 of 17 - ws3, ws4, ws5, ws6, ws14, ws15, ws20, ws21, ws22, ws23, ws24, ws25, ws29, ws30 | 3 - ws26, ws27, ws28 | 11 - ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws16, ws17, ws18, ws19 |
| 2026-09-15 09:12:45 | 2026-09-15 05:21:10 LONG | 12 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws13, ws14, ws16, ws24, ws27, ws28 | 6 of 12 - ws3, ws4, ws5, ws6, ws7, ws13 | 6 - ws8, ws14, ws16, ws24, ws27, ws28 | 16 - ws9, ws10, ws11, ws12, ws15, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws25, ws26, ws29, ws30 |
| 2026-09-15 09:56:55 | 2026-09-15 09:14:55 LONG | 18 of 28 - ws3, ws5, ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws22, ws27 | 14 of 18 - ws3, ws5, ws6, ws7, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws18, ws19 | 4 - ws8, ws17, ws22, ws27 | 10 - ws4, ws20, ws21, ws23, ws24, ws25, ws26, ws28, ws29, ws30 |
| 2026-09-15 21:02:25 | 2026-09-15 19:30:35 LONG | 5 of 28 - ws3, ws4, ws5, ws7, ws8 | 4 of 5 - ws4, ws5, ws7, ws8 | 1 - ws3 | 23 - ws6, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |

| the roll-up over 4 ws10x-cadences | value |
|---|---|
| eligible lines, every time | 28 |
| population, smallest .. largest | 5 .. 18 |
| population, mean | 13.0 |
| contributed, smallest .. largest | 4 .. 14 |
| contributed, mean | 9.5 |

| the line | times in the population | times it contributed |
|---|---|---|
| ws3 | 4 of 4 | 3 of 4 |
| ws4 | 3 of 4 | 3 of 4 |
| ws5 | 4 of 4 | 4 of 4 |
| ws6 | 3 of 4 | 3 of 4 |
| ws7 | 3 of 4 | 3 of 4 |
| ws8 | 3 of 4 | 1 of 4 |
| ws9 | 1 of 4 | 1 of 4 |
| ws10 | 1 of 4 | 1 of 4 |
| ws11 | 1 of 4 | 1 of 4 |
| ws12 | 1 of 4 | 1 of 4 |
| ws13 | 2 of 4 | 2 of 4 |
| ws14 | 3 of 4 | 2 of 4 |
| ws15 | 2 of 4 | 2 of 4 |
| ws16 | 2 of 4 | 1 of 4 |
| ws17 | 1 of 4 | 0 of 4 |
| ws18 | 1 of 4 | 1 of 4 |
| ws19 | 1 of 4 | 1 of 4 |
| ws20 | 1 of 4 | 1 of 4 |
| ws21 | 1 of 4 | 1 of 4 |
| ws22 | 2 of 4 | 1 of 4 |
| ws23 | 1 of 4 | 1 of 4 |
| ws24 | 2 of 4 | 1 of 4 |
| ws25 | 1 of 4 | 1 of 4 |
| ws26 | 1 of 4 | 0 of 4 |
| ws27 | 3 of 4 | 0 of 4 |
| ws28 | 2 of 4 | 0 of 4 |
| ws29 | 1 of 4 | 1 of 4 |
| ws30 | 1 of 4 | 1 of 4 |

## the legs | every number carries the FDM_MAE_CAP 1.10% stop

| the open | the trade | the rev-trade signal | the exit | the exit kind | held min | MAE% | MFE% | realised% |
|---|---|---|---|---|---|---|---|---|
| 2026-09-15 00:36:35 | SHORT | 2026-09-15 01:21:55 | 2026-09-15 01:22:00 | rev-trade | 45.4 | 0.270 | 0.811 | +0.471 |
| 2026-09-15 01:22:05 | LONG | - | 2026-09-15 03:11:40 | STOP at 1.10% | 109.6 | 1.100 | 0.209 | -1.100 |
| 2026-09-15 03:17:05 | LONG | 2026-09-15 03:25:10 | 2026-09-15 03:25:15 | saviour | 8.2 | 0.021 | 0.402 | +0.261 |
| 2026-09-15 03:25:20 | SHORT | 2026-09-15 04:41:00 | 2026-09-15 04:41:05 | rev-trade | 75.8 | 0.541 | 0.323 | +0.035 |
| 2026-09-15 04:41:10 | LONG | 2026-09-15 04:50:30 | 2026-09-15 04:50:35 | saviour | 9.4 | 0.000 | 0.267 | +0.162 |
| 2026-09-15 04:50:40 | SHORT | 2026-09-15 05:21:00 | 2026-09-15 05:21:05 | rev-trade | 30.4 | 0.246 | 0.983 | +0.547 |
| 2026-09-15 05:21:10 | LONG | 2026-09-15 09:12:45 | 2026-09-15 09:12:50 | rev-trade | 231.7 | 0.896 | 0.741 | +0.339 |
| 2026-09-15 09:12:55 | SHORT | 2026-09-15 09:14:45 | 2026-09-15 09:14:50 | saviour | 1.9 | 0.000 | 0.077 | +0.021 |
| 2026-09-15 09:14:55 | LONG | 2026-09-15 09:56:55 | 2026-09-15 09:57:00 | rev-trade | 42.1 | 0.141 | 0.640 | +0.302 |
| 2026-09-15 09:57:05 | SHORT | 2026-09-15 10:07:55 | 2026-09-15 10:08:00 | saviour | 10.9 | 0.077 | 0.231 | +0.063 |
| 2026-09-15 10:08:05 | LONG | - | 2026-09-15 11:32:45 | STOP at 1.10% | 84.7 | 1.100 | 0.133 | -1.100 |
| 2026-09-15 11:59:35 | SHORT | - | 2026-09-15 12:54:05 | STOP at 1.10% | 54.5 | 1.100 | 0.057 | -1.100 |
| 2026-09-15 12:57:35 | SHORT | 2026-09-15 13:00:10 | 2026-09-15 13:00:15 | saviour | 2.7 | 0.077 | 0.203 | -0.000 |
| 2026-09-15 13:00:20 | LONG | - | 2026-09-15 13:37:55 | STOP at 1.10% | 37.6 | 1.100 | 0.813 | -1.100 |
| 2026-09-15 13:40:35 | LONG | - | 2026-09-15 14:35:20 | STOP at 1.10% | 54.8 | 1.100 | 0.706 | -1.100 |
| 2026-09-15 14:44:05 | LONG | - | 2026-09-15 14:51:35 | STOP at 1.10% | 7.5 | 1.100 | 0.231 | -1.100 |
| 2026-09-15 15:30:05 | SHORT | 2026-09-15 17:14:00 | 2026-09-15 17:14:05 | rev-trade | 104.0 | 0.504 | 1.108 | +0.618 |
| 2026-09-15 17:14:10 | LONG | 2026-09-15 17:18:05 | 2026-09-15 17:18:10 | saviour | 4.0 | 0.150 | 0.150 | -0.029 |
| 2026-09-15 17:18:15 | SHORT | - | 2026-09-15 17:32:15 | STOP at 1.10% | 14.0 | 1.100 | 0.021 | -1.100 |
| 2026-09-15 17:39:05 | SHORT | 2026-09-15 17:46:05 | 2026-09-15 17:46:10 | saviour | 7.1 | 0.098 | 0.640 | +0.148 |
| 2026-09-15 17:46:15 | LONG | - | 2026-09-15 18:17:40 | STOP at 1.10% | 31.4 | 1.100 | 0.760 | -1.100 |
| 2026-09-15 18:25:35 | LONG | - | 2026-09-15 18:37:00 | STOP at 1.10% | 11.4 | 1.100 | 1.462 | -1.100 |
| 2026-09-15 18:51:35 | LONG | 2026-09-15 18:58:05 | 2026-09-15 18:58:10 | saviour | 6.6 | 0.322 | 2.602 | +1.525 |
| 2026-09-15 18:58:15 | SHORT | - | 2026-09-15 19:17:40 | STOP at 1.10% | 19.4 | 1.100 | 0.840 | -1.100 |
| 2026-09-15 19:30:35 | LONG | 2026-09-15 21:02:25 | 2026-09-15 21:02:30 | rev-trade | 91.9 | 1.087 | 1.271 | +0.404 |
| 2026-09-15 21:02:35 | SHORT | 2026-09-15 21:03:25 | 2026-09-15 21:03:30 | saviour | 0.9 | 0.358 | 0.051 | -0.358 |
| 2026-09-15 21:03:35 | LONG | - | 2026-09-15 21:28:10 | STOP at 1.10% | 24.6 | 1.100 | 0.270 | -1.100 |
| 2026-09-15 21:31:05 | LONG | - | 2026-09-15 22:23:25 | STOP at 1.10% | 52.3 | 1.100 | 0.530 | -1.100 |
| 2026-09-15 22:59:35 | SHORT | - | 2026-09-15 23:09:10 | STOP at 1.10% | 9.6 | 1.100 | 0.058 | -1.100 |
| 2026-09-15 23:12:35 | SHORT | - | 2026-09-15 23:59:55 | no rev-trade before the walk's end | 47.3 | 0.517 | 0.870 | +0.676 |

| the aggregate | value |
|---|---|
| legs | 30 |
| stopped | 13 |
| gross % | -9.115 |
| drag % | -5.925 (0.1975% round trip x 30 legs) |
| net % | -15.040 |
| MAE % total | 19.607 |
| MFE % total | 17.461 |
| MFE captured | -52.2% of MFE |
| held min, shortest .. longest | 0.9 .. 231.7 |
