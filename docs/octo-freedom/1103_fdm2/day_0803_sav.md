# fdm2 | TAPE 1632960 bars, ends 2026-10-04 23:59:55 | RULED_OK True
# THE WALK RUNS 2026-08-03 00:00:00 .. 2026-08-03 23:59:55 - HIS one-day bound
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
| the re-entry signal bar | 2026-08-03 00:41:30 |
| the gcws30b window side | HIGH oob |
| the trade | SHORT |
| its target side | LOW |
| the open price bar | 2026-08-03 00:41:35 - the router's "just OPEN", 1 bar |
| why | gcws30b HIGH window 00:35:00..00:41:30, ws1r AND (ws2r or ws3r) seen past the 75.0 fence - ws1 00:35:00, ws2 00:36:00, ws3 00:36:00 - gate TRUE at the ib cross |

## leg 2026-08-03 00:41:35 | SHORT | target side LOW | fdm re-entry 2026-08-03 00:41:30

| the bar | the stage | why |
|---|---|---|
| 2026-08-03 00:41:35 | SAVIOUR STAYS OPEN | the cap @ 2026-08-03 00:41:35 to 2026-08-03 00:57:35: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-08-03 00:49:15 to 2026-08-03 00:49:25: 3 bars, peak 14.57, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-08-03 00:49:15 to 2026-08-03 00:49:25: 3 bars, peak 14.57 | the ws1r oob->ib cross @ 2026-08-03 00:49:35: ws1r 15.63, held 2 bars | the cascade anchor @ 2026-08-03 00:48:05: ws1Mage extremum, 90 s before the cross | the cascade at the stamp @ 2026-08-03 00:48:05: down | down | the low cluster ws1 to ws3, 3 lines, falling COUNTS | the high cluster ws1 to ws3, 3 lines, falling COUNTS | the end-to-end diff +19.30 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-08-03 00:49:35: ws1Mage 62.5827, no | branch A does not fire - branch B @ 2026-08-03 00:49:35: the cascade is not counter. walk to ws2r oob, inside the cap to 2026-08-03 00:57:35 | ws1Mage left the past-50 gate @ 2026-08-03 00:50:10: held 8 bars = 40 s, ws1Mage 77.2173 at the stamp | the ws1Mage target-side extrema anchor @ 2026-08-03 00:48:05: ws1Mage 50.8339, 125 s before the stamp | the routed cascade at the anchor @ 2026-08-03 00:48:05: down | down | the low cluster ws1 to ws3, 3 lines, falling COUNTS | the high cluster ws1 to ws3, 3 lines, falling COUNTS | the end-to-end diff +19.30 | zoom 2 rungs, min 3 lines | the route does not fire @ 2026-08-03 00:50:10: the cascade is not counter - the trade stays open, v4saviour is complete |
| 2026-08-03 01:28:00 | WALK | cadence event, 10 of 27 lines printing ex-20/80 AND towards -> walk. the next cadence event is first (ws10x crosses to ws10Mage 2026-08-03 01:41:50, the ws10x-cadence confirms 2026-08-03 01:43:45) |
| 2026-08-03 01:42:00 | WALK | cadence event, 10 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-08-03 01:42:10, the ws10x-cadence confirms 2026-08-03 01:44:05) |
| 2026-08-03 01:44:05 | NO ACTION | the ws10x-cadence - ws10x crossed to ib 2026-08-03 01:42:10 and confirmed here. 4 of 23 reversed since 2026-08-03 01:42:00 (event) = 17.4% < 40% - no branch, wait for the next cadence event |
| 2026-08-03 02:59:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10Mage 2026-08-03 02:59:40, the ws10x-cadence confirms 2026-08-03 03:01:35) |
| 2026-08-03 03:01:35 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10Mage 2026-08-03 02:59:40 and confirmed here. 18 of 25 reversed since 2026-08-03 02:59:00 (event) = 72.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-08-03 03:01:45 | LONG | target side HIGH | rev-trade 2026-08-03 03:01:35

| the bar | the stage | why |
|---|---|---|
| 2026-08-03 03:05:05 | SAVIOUR SAVIOUR REV | v4saviour SAVIOUR REV from ws1r | the cap @ 2026-08-03 03:01:45 to 2026-08-03 03:17:45: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-08-03 03:04:00 to 2026-08-03 03:04:55: 12 bars, peak 96.90, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-08-03 03:04:00 to 2026-08-03 03:04:55: 12 bars, peak 96.90 | the ws1r oob->ib cross @ 2026-08-03 03:05:05: ws1r 81.18, held 2 bars | the cascade anchor @ 2026-08-03 03:04:15: ws1Mage extremum, 50 s before the cross | the cascade at the stamp @ 2026-08-03 03:04:15: down | down | the low cluster ws1 to ws3, 3 lines, falling COUNTS | the high cluster ws1 to ws3, 3 lines, falling COUNTS | the end-to-end diff +43.99 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-08-03 03:05:05: ws1Mage 13.5226, no | branch A fires @ 2026-08-03 03:05:05: counter cascade and ws1Mage not past 50 - end the trade, rev-trade on the next bar |

## leg 2026-08-03 03:05:15 | SHORT | target side LOW | rev-trade 2026-08-03 03:05:05

| the bar | the stage | why |
|---|---|---|
| 2026-08-03 03:05:15 | SAVIOUR STAYS OPEN | the cap @ 2026-08-03 03:05:15 to 2026-08-03 03:21:15: 192 bars = 16 min from the open | no ws1r oob run on the target-side inside the cap @ 2026-08-03 03:21:15: the cap expired - the trade stays open |
| 2026-08-03 05:01:00 | REV-TRADE | cadence event, 0 of 27 lines ws4..ws30 printing ex-20/80 AND towards - his "if the answer is no, then rev-trade" |

## leg 2026-08-03 05:01:10 | LONG | target side HIGH | rev-trade 2026-08-03 05:01:00

| the bar | the stage | why |
|---|---|---|
| 2026-08-03 05:01:10 | SAVIOUR STAYS OPEN | the cap @ 2026-08-03 05:01:10 to 2026-08-03 05:17:10: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-08-03 05:09:15 to 2026-08-03 05:09:15: 1 bars, peak 85.45, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-08-03 05:09:15 to 2026-08-03 05:09:15: 1 bars, peak 85.45 | the ws1r oob->ib cross @ 2026-08-03 05:09:25: ws1r 71.16, held 2 bars | the cascade anchor @ 2026-08-03 05:08:30: ws1Mage extremum, 55 s before the cross | the cascade at the stamp @ 2026-08-03 05:08:30: up | up | the low cluster ws1 to ws3, 3 lines, rising COUNTS | the high cluster ws1 to ws3, 3 lines, rising COUNTS | the end-to-end diff -8.89 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-08-03 05:09:25: ws1Mage 20.8230, no | branch A does not fire - branch B @ 2026-08-03 05:09:25: the cascade is not counter. walk to ws2r oob, inside the cap to 2026-08-03 05:17:10 | ws1Mage left the past-50 gate @ 2026-08-03 05:10:00: held 8 bars = 40 s, ws1Mage 19.0517 at the stamp | the ws1Mage target-side extrema anchor @ 2026-08-03 05:08:30: ws1Mage 44.7660, 90 s before the stamp | the routed cascade at the anchor @ 2026-08-03 05:08:30: up | up | the low cluster ws1 to ws3, 3 lines, rising COUNTS | the high cluster ws1 to ws3, 3 lines, rising COUNTS | the end-to-end diff -8.89 | zoom 2 rungs, min 3 lines | the route does not fire @ 2026-08-03 05:10:00: the cascade is not counter - the trade stays open, v4saviour is complete |
| 2026-08-03 06:11:00 | WALK | cadence event, 4 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10r 2026-08-03 06:20:05, the ws10x-cadence confirms 2026-08-03 06:22:00) |
| 2026-08-03 06:22:00 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10r 2026-08-03 06:20:05 and confirmed here. 14 of 14 reversed since 2026-08-03 06:11:00 (event) = 100.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-08-03 06:22:10 | SHORT | target side LOW | rev-trade 2026-08-03 06:22:00

| the bar | the stage | why |
|---|---|---|
| 2026-08-03 06:26:15 | SAVIOUR SAVIOUR REV | v4saviour SAVIOUR REV from ws2r | the cap @ 2026-08-03 06:22:10 to 2026-08-03 06:38:10: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-08-03 06:22:10 to 2026-08-03 06:22:10: 1 bars, peak 14.54, 2 run(s) inside the cap | the ws1r cross is a flicker @ 2026-08-03 06:22:15: ws1r 16.51, back oob inside the 2-bar hold - not a cross, scan on | the ws1r oob run that crossed @ 2026-08-03 06:22:20 to 2026-08-03 06:22:35: 4 bars, peak 14.54 | the ws1r oob->ib cross @ 2026-08-03 06:22:45: ws1r 15.56, held 2 bars | the cascade anchor @ 2026-08-03 06:22:35: ws1Mage extremum, 10 s before the cross | the cascade at the stamp @ 2026-08-03 06:22:35: up | up | the low cluster ws1 to ws3, 3 lines, rising COUNTS | the high cluster ws1 to ws3, 3 lines, rising COUNTS | the end-to-end diff -10.33 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-08-03 06:22:45: ws1Mage 40.7169, YES | branch A does not fire - branch B @ 2026-08-03 06:22:45: ws1Mage is past 50 towards the target-side. walk to ws2r oob, inside the cap to 2026-08-03 06:38:10 | the ws2r oob run @ 2026-08-03 06:24:55 to 2026-08-03 06:26:05: 15 bars, peak 14.66 | the ws2r oob->ib cross @ 2026-08-03 06:26:15: ws2r 21.01, 143 bars inside the cap | the cascade anchor @ 2026-08-03 06:25:20: ws1Mage extremum, 55 s before the cross | the cascade at the stamp @ 2026-08-03 06:25:20: up | up | the low cluster ws1 to ws3, 3 lines, rising COUNTS | the high cluster ws1 to ws3, 3 lines, rising COUNTS | the end-to-end diff -14.55 | zoom 2 rungs, min 3 lines | ws2Mage past 50 towards the target-side @ 2026-08-03 06:26:15: ws2Mage 59.4880, no | branch B fires @ 2026-08-03 06:26:15: counter cascade and ws2Mage not past 50 - end the trade, rev-trade on the next bar |

## leg 2026-08-03 06:26:25 | LONG | target side HIGH | rev-trade 2026-08-03 06:26:15

| the bar | the stage | why |
|---|---|---|
| 2026-08-03 06:26:25 | SAVIOUR STAYS OPEN | the cap @ 2026-08-03 06:26:25 to 2026-08-03 06:42:25: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-08-03 06:33:20 to 2026-08-03 06:33:40: 5 bars, peak 87.34, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-08-03 06:33:20 to 2026-08-03 06:33:40: 5 bars, peak 87.34 | the ws1r oob->ib cross @ 2026-08-03 06:33:50: ws1r 84.98, held 2 bars | the cascade anchor @ 2026-08-03 06:32:50: ws1Mage extremum, 60 s before the cross | the cascade at the stamp @ 2026-08-03 06:32:50: up | up | the low cluster ws1 to ws3, 3 lines, rising COUNTS | the high cluster ws1 to ws3, 3 lines, rising COUNTS | the end-to-end diff -17.84 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-08-03 06:33:50: ws1Mage 44.5467, no | branch A does not fire - branch B @ 2026-08-03 06:33:50: the cascade is not counter. walk to ws2r oob, inside the cap to 2026-08-03 06:42:25 | ws1Mage left the past-50 gate @ 2026-08-03 06:34:25: held 8 bars = 40 s, ws1Mage 35.6866 at the stamp | the ws1Mage target-side extrema anchor @ 2026-08-03 06:32:25: ws1Mage 50.0000, 120 s before the stamp | the routed cascade at the anchor @ 2026-08-03 06:32:25: up | up | the low cluster ws1 to ws3, 3 lines, rising COUNTS | the high cluster ws1 to ws3, 3 lines, rising COUNTS | the end-to-end diff -17.84 | zoom 2 rungs, min 3 lines | the route does not fire @ 2026-08-03 06:34:25: the cascade is not counter - the trade stays open, v4saviour is complete |
| 2026-08-03 09:12:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10Mage 2026-08-03 09:31:15, the ws10x-cadence confirms 2026-08-03 09:33:10) |
| 2026-08-03 09:33:10 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10Mage 2026-08-03 09:31:15 and confirmed here. 10 of 14 reversed since 2026-08-03 09:12:00 (event) = 71.4% >= 50% at the ws10x-cadence bar itself |

## leg 2026-08-03 09:33:20 | SHORT | target side LOW | rev-trade 2026-08-03 09:33:10

| the bar | the stage | why |
|---|---|---|
| 2026-08-03 09:45:25 | SAVIOUR SAVIOUR REV | v4saviour SAVIOUR REV from ws1r | the cap @ 2026-08-03 09:33:20 to 2026-08-03 09:49:20: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-08-03 09:45:00 to 2026-08-03 09:45:15: 4 bars, peak 13.95, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-08-03 09:45:00 to 2026-08-03 09:45:15: 4 bars, peak 13.95 | the ws1r oob->ib cross @ 2026-08-03 09:45:25: ws1r 16.55, held 2 bars | the cascade anchor @ 2026-08-03 09:44:05: ws1Mage extremum, 80 s before the cross | the cascade at the stamp @ 2026-08-03 09:44:05: up | up | the low cluster ws1 to ws3, 3 lines, rising COUNTS | the high cluster ws1 to ws3, 3 lines, rising COUNTS | the end-to-end diff -19.92 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-08-03 09:45:25: ws1Mage 67.4904, no | branch A fires @ 2026-08-03 09:45:25: counter cascade and ws1Mage not past 50 - end the trade, rev-trade on the next bar |

## leg 2026-08-03 09:45:35 | LONG | target side HIGH | rev-trade 2026-08-03 09:45:25

| the bar | the stage | why |
|---|---|---|
| 2026-08-03 09:45:35 | SAVIOUR STAYS OPEN | the cap @ 2026-08-03 09:45:35 to 2026-08-03 10:01:35: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-08-03 09:52:00 to 2026-08-03 09:55:55: 48 bars, peak 99.92, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-08-03 09:52:00 to 2026-08-03 09:55:55: 48 bars, peak 99.92 | the ws1r oob->ib cross @ 2026-08-03 09:56:05: ws1r 73.83, held 2 bars | the cascade anchor @ 2026-08-03 09:54:25: ws1Mage extremum, 100 s before the cross | the cascade at the stamp @ 2026-08-03 09:54:25: down | down | the low cluster ws1 to ws3, 3 lines, falling COUNTS | the high cluster ws1 to ws3, 3 lines, falling COUNTS | the end-to-end diff +22.85 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-08-03 09:56:05: ws1Mage 90.3902, YES | branch A does not fire - branch B @ 2026-08-03 09:56:05: ws1Mage is past 50 towards the target-side. walk to ws2r oob, inside the cap to 2026-08-03 10:01:35 | the cap expired @ 2026-08-03 10:01:35: no ws2r cross and no ws1Mage route inside it - the trade stays open |
| 2026-08-03 10:09:00 | WALK | cadence event, 15 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10Mage 2026-08-03 10:10:00, the ws10x-cadence confirms 2026-08-03 10:11:55) |
| 2026-08-03 10:11:55 | NO ACTION | the ws10x-cadence - ws10x crossed to ws10Mage 2026-08-03 10:10:00 and confirmed here. 4 of 18 reversed since 2026-08-03 10:09:00 (event) = 22.2% < 40% - no branch, wait for the next cadence event |
| 2026-08-03 13:25:00 | WALK | cadence event, 1 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-08-03 13:25:45, the ws10x-cadence confirms 2026-08-03 13:27:40) |
| 2026-08-03 13:27:40 | NO ACTION | the ws10x-cadence - ws10x crossed to ib 2026-08-03 13:25:45 and confirmed here. 8 of 21 reversed since 2026-08-03 13:25:00 (event) = 38.1% < 40% - no branch, wait for the next cadence event |

## leg 2026-08-03 14:00:35 | SHORT | target side LOW | fdm re-entry 2026-08-03 14:00:30, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-08-03 14:10:10 | SAVIOUR SAVIOUR REV | v4saviour SAVIOUR REV from ws1r | the cap @ 2026-08-03 14:00:35 to 2026-08-03 14:16:35: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-08-03 14:10:00 to 2026-08-03 14:10:00: 1 bars, peak 14.26, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-08-03 14:10:00 to 2026-08-03 14:10:00: 1 bars, peak 14.26 | the ws1r oob->ib cross @ 2026-08-03 14:10:10: ws1r 16.14, held 2 bars | the cascade anchor @ 2026-08-03 14:09:30: ws1Mage extremum, 40 s before the cross | the cascade at the stamp @ 2026-08-03 14:09:30: up | up | the low cluster ws1 to ws3, 3 lines, rising COUNTS | the high cluster ws1 to ws3, 3 lines, rising COUNTS | the end-to-end diff -20.79 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-08-03 14:10:10: ws1Mage 69.8016, no | branch A fires @ 2026-08-03 14:10:10: counter cascade and ws1Mage not past 50 - end the trade, rev-trade on the next bar |

## leg 2026-08-03 14:10:20 | LONG | target side HIGH | rev-trade 2026-08-03 14:10:10

| the bar | the stage | why |
|---|---|---|
| 2026-08-03 14:10:20 | SAVIOUR STAYS OPEN | the cap @ 2026-08-03 14:10:20 to 2026-08-03 14:26:20: 192 bars = 16 min from the open | no ws1r oob run on the target-side inside the cap @ 2026-08-03 14:26:20: the cap expired - the trade stays open |

## leg 2026-08-03 16:44:05 | LONG | target side HIGH | fdm re-entry 2026-08-03 16:44:00, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-08-03 16:44:05 | SAVIOUR STAYS OPEN | the cap @ 2026-08-03 16:44:05 to 2026-08-03 17:00:05: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-08-03 16:49:00 to 2026-08-03 16:51:15: 28 bars, peak 98.50, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-08-03 16:49:00 to 2026-08-03 16:51:15: 28 bars, peak 98.50 | the ws1r oob->ib cross @ 2026-08-03 16:51:25: ws1r 83.18, held 2 bars | the cascade anchor @ 2026-08-03 16:50:00: ws1Mage extremum, 85 s before the cross | the cascade at the stamp @ 2026-08-03 16:50:00: down | down | the low cluster ws1 to ws3, 3 lines, falling COUNTS | the high cluster ws1 to ws3, 3 lines, falling COUNTS | the end-to-end diff +12.87 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-08-03 16:51:25: ws1Mage 68.1775, YES | branch A does not fire - branch B @ 2026-08-03 16:51:25: ws1Mage is past 50 towards the target-side. walk to ws2r oob, inside the cap to 2026-08-03 17:00:05 | the cap expired @ 2026-08-03 17:00:05: no ws2r cross and no ws1Mage route inside it - the trade stays open |
| 2026-08-03 17:17:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-08-03 17:20:25, the ws10x-cadence confirms 2026-08-03 17:22:20) |
| 2026-08-03 17:22:20 | NO ACTION | the ws10x-cadence - ws10x crossed to ib 2026-08-03 17:20:25 and confirmed here. 1 of 3 reversed since 2026-08-03 17:17:00 (event) = 33.3% < 40% - no branch, wait for the next cadence event |
| 2026-08-03 18:08:00 | WALK | cadence event, 6 of 27 lines printing ex-20/80 AND towards -> walk. the next cadence event is first (ws10x crosses to ws10Mage 2026-08-03 18:41:10, the ws10x-cadence confirms 2026-08-03 18:43:05) |
| 2026-08-03 18:11:00 | WALK | cadence event, 6 of 27 lines printing ex-20/80 AND towards -> walk. the next cadence event is first (ws10x crosses to ws10Mage 2026-08-03 18:41:10, the ws10x-cadence confirms 2026-08-03 18:43:05) |
| 2026-08-03 18:42:00 | WALK | cadence event, 10 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10r 2026-08-03 18:50:00, the ws10x-cadence confirms 2026-08-03 18:51:55) |
| 2026-08-03 18:51:55 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10r 2026-08-03 18:50:00 and confirmed here. 13 of 16 reversed since 2026-08-03 18:42:00 (event) = 81.2% >= 50% at the ws10x-cadence bar itself |

## leg 2026-08-03 18:52:05 | SHORT | target side LOW | rev-trade 2026-08-03 18:51:55

| the bar | the stage | why |
|---|---|---|
| 2026-08-03 18:52:05 | SAVIOUR STAYS OPEN | the cap @ 2026-08-03 18:52:05 to 2026-08-03 19:08:05: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-08-03 18:57:15 to 2026-08-03 19:01:55: 57 bars, peak 14.29, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-08-03 18:57:15 to 2026-08-03 19:01:55: 57 bars, peak 14.29 | the ws1r oob->ib cross @ 2026-08-03 19:02:05: ws1r 21.39, held 2 bars | the cascade anchor @ 2026-08-03 19:00:50: ws1Mage extremum, 75 s before the cross | the cascade at the stamp @ 2026-08-03 19:00:50: up | up | the low cluster ws1 to ws3, 3 lines, rising COUNTS | the high cluster ws1 to ws3, 3 lines, rising COUNTS | the end-to-end diff -53.03 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-08-03 19:02:05: ws1Mage 12.6537, YES | branch A does not fire - branch B @ 2026-08-03 19:02:05: ws1Mage is past 50 towards the target-side. walk to ws2r oob, inside the cap to 2026-08-03 19:08:05 | the cap expired @ 2026-08-03 19:08:05: no ws2r cross and no ws1Mage route inside it - the trade stays open |
| 2026-08-03 20:13:00 | WALK | cadence event, 7 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10r 2026-08-03 20:17:30, the ws10x-cadence confirms 2026-08-03 20:19:25) |
| 2026-08-03 20:19:25 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10r 2026-08-03 20:17:30 and confirmed here. 10 of 14 reversed since 2026-08-03 20:13:00 (event) = 71.4% >= 50% at the ws10x-cadence bar itself |

## leg 2026-08-03 20:19:35 | LONG | target side HIGH | rev-trade 2026-08-03 20:19:25

| the bar | the stage | why |
|---|---|---|
| 2026-08-03 20:19:45 | SAVIOUR SAVIOUR REV | v4saviour SAVIOUR REV from ws1r | the cap @ 2026-08-03 20:19:35 to 2026-08-03 20:35:35: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-08-03 20:19:35 to 2026-08-03 20:19:35: 1 bars, peak 88.89, 5 run(s) inside the cap | the ws1r oob run that crossed @ 2026-08-03 20:19:35 to 2026-08-03 20:19:35: 1 bars, peak 88.89 | the ws1r oob->ib cross @ 2026-08-03 20:19:45: ws1r 84.95, held 2 bars | the cascade anchor @ 2026-08-03 20:18:50: ws1Mage extremum, 55 s before the cross | the cascade at the stamp @ 2026-08-03 20:18:50: down | down | the low cluster ws1 to ws3, 3 lines, falling COUNTS | the high cluster ws1 to ws3, 3 lines, falling COUNTS | the end-to-end diff +14.56 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-08-03 20:19:45: ws1Mage 44.4543, no | branch A fires @ 2026-08-03 20:19:45: counter cascade and ws1Mage not past 50 - end the trade, rev-trade on the next bar |

## leg 2026-08-03 20:19:55 | SHORT | target side LOW | rev-trade 2026-08-03 20:19:45

| the bar | the stage | why |
|---|---|---|
| 2026-08-03 20:19:55 | SAVIOUR STAYS OPEN | the cap @ 2026-08-03 20:19:55 to 2026-08-03 20:35:55: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-08-03 20:32:00 to 2026-08-03 20:33:05: 14 bars, peak 13.53, 3 run(s) inside the cap | the ws1r oob run that crossed @ 2026-08-03 20:32:00 to 2026-08-03 20:33:05: 14 bars, peak 13.53 | the ws1r oob->ib cross @ 2026-08-03 20:33:15: ws1r 20.66, held 2 bars | the cascade anchor @ 2026-08-03 20:31:50: ws1Mage extremum, 85 s before the cross | the cascade at the stamp @ 2026-08-03 20:31:50: down | down | the low cluster ws1 to ws3, 3 lines, falling COUNTS | the high cluster ws1 to ws3, 3 lines, falling COUNTS | the end-to-end diff +16.87 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-08-03 20:33:15: ws1Mage 63.3019, no | branch A does not fire - branch B @ 2026-08-03 20:33:15: the cascade is not counter. walk to ws2r oob, inside the cap to 2026-08-03 20:35:55 | ws1Mage left the past-50 gate @ 2026-08-03 20:33:50: held 8 bars = 40 s, ws1Mage 50.3089 at the stamp | the ws1Mage target-side extrema anchor @ 2026-08-03 20:33:50: ws1Mage 50.3089, 0 s before the stamp | the routed cascade at the anchor @ 2026-08-03 20:33:50: down | down | the low cluster ws1 to ws3, 3 lines, falling COUNTS | the high cluster ws1 to ws3, 3 lines, falling COUNTS | the end-to-end diff +14.30 | zoom 2 rungs, min 3 lines | the route does not fire @ 2026-08-03 20:33:50: the cascade is not counter - the trade stays open, v4saviour is complete |
| 2026-08-03 20:55:00 | WALK | cadence event, 10 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10Mage 2026-08-03 20:56:55, the ws10x-cadence confirms 2026-08-03 20:58:50) |
| 2026-08-03 20:58:50 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10Mage 2026-08-03 20:56:55 and confirmed here. 11 of 16 reversed since 2026-08-03 20:55:00 (event) = 68.8% >= 50% at the ws10x-cadence bar itself |

## leg 2026-08-03 20:59:00 | LONG | target side HIGH | rev-trade 2026-08-03 20:58:50

| the bar | the stage | why |
|---|---|---|
| 2026-08-03 21:03:00 | REV-TRADE | cadence event, 0 of 27 lines ws4..ws30 printing ex-20/80 AND towards - his "if the answer is no, then rev-trade" |

## leg 2026-08-03 21:03:10 | SHORT | target side LOW | rev-trade 2026-08-03 21:03:00

| the bar | the stage | why |
|---|---|---|
| 2026-08-03 21:03:10 | SAVIOUR STAYS OPEN | the cap @ 2026-08-03 21:03:10 to 2026-08-03 21:19:10: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-08-03 21:07:00 to 2026-08-03 21:14:35: 92 bars, peak 14.13, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-08-03 21:07:00 to 2026-08-03 21:14:35: 92 bars, peak 14.13 | the ws1r oob->ib cross @ 2026-08-03 21:14:45: ws1r 15.98, held 2 bars | the cascade anchor @ 2026-08-03 21:12:45: ws1Mage extremum, 120 s before the cross | the cascade at the stamp @ 2026-08-03 21:12:45: down | down | the low cluster ws1 to ws3, 3 lines, falling COUNTS | the high cluster ws1 to ws3, 3 lines, falling COUNTS | the end-to-end diff +10.33 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-08-03 21:14:45: ws1Mage 33.5705, YES | branch A does not fire - branch B @ 2026-08-03 21:14:45: the cascade is not counter. walk to ws2r oob, inside the cap to 2026-08-03 21:19:10 | the ws2r oob run @ 2026-08-03 21:15:25 to 2026-08-03 21:16:40: 16 bars, peak 14.20 | the ws2r oob->ib cross @ 2026-08-03 21:16:50: ws2r 19.13, 28 bars inside the cap | the cascade anchor @ 2026-08-03 21:15:50: ws1Mage extremum, 60 s before the cross | the cascade at the stamp @ 2026-08-03 21:15:50: down | down | the low cluster ws1 to ws3, 3 lines, falling COUNTS | the high cluster ws1 to ws3, 3 lines, falling COUNTS | the end-to-end diff +11.57 | zoom 2 rungs, min 3 lines | ws2Mage past 50 towards the target-side @ 2026-08-03 21:16:50: ws2Mage 38.6472, YES | branch B does not fire @ 2026-08-03 21:16:50: the cascade is not counter - the trade stays open, v4saviour is complete |
| 2026-08-03 21:17:00 | WALK | cadence event, 7 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10r 2026-08-03 21:21:00, the ws10x-cadence confirms 2026-08-03 21:22:55) |
| 2026-08-03 21:22:55 | GRACE | the ws10x-cadence - ws10x crossed to ws10r 2026-08-03 21:21:00 and confirmed here. 4 of 9 reversed since 2026-08-03 21:17:00 (event) = 44.4% >= 40% -> grace walk 2026-08-03 21:23:00 .. 2026-08-03 21:27:55, 60 bars = 5.0 min, population frozen at 9 lines |
| 2026-08-03 21:23:35 | REV-TRADE | grace walk, 6 of 9 reversed since 2026-08-03 21:17:00 (event) = 66.7% >= 50% |

## leg 2026-08-03 21:23:45 | LONG | target side HIGH | rev-trade 2026-08-03 21:23:35

| the bar | the stage | why |
|---|---|---|
| 2026-08-03 21:23:45 | SAVIOUR STAYS OPEN | the cap @ 2026-08-03 21:23:45 to 2026-08-03 21:39:45: 192 bars = 16 min from the open | no ws1r oob run on the target-side inside the cap @ 2026-08-03 21:39:45: the cap expired - the trade stays open |

## leg 2026-08-03 22:56:05 | SHORT | target side LOW | fdm re-entry 2026-08-03 22:56:00, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-08-03 22:56:05 | SAVIOUR STAYS OPEN | the cap @ 2026-08-03 22:56:05 to 2026-08-03 23:12:05: 192 bars = 16 min from the open | the first ws1r oob run @ 2026-08-03 23:03:00 to 2026-08-03 23:07:55: 60 bars, peak 11.80, 1 run(s) inside the cap | the ws1r oob run that crossed @ 2026-08-03 23:03:00 to 2026-08-03 23:07:55: 60 bars, peak 11.80 | the ws1r oob->ib cross @ 2026-08-03 23:08:05: ws1r 21.90, held 2 bars | the cascade anchor @ 2026-08-03 23:07:25: ws1Mage extremum, 40 s before the cross | the cascade at the stamp @ 2026-08-03 23:07:25: down | down | the low cluster ws1 to ws3, 3 lines, falling COUNTS | the high cluster ws1 to ws3, 3 lines, falling COUNTS | the end-to-end diff +0.56 | zoom 2 rungs, min 3 lines | ws1Mage past 50 towards the target-side @ 2026-08-03 23:08:05: ws1Mage 55.4798, no | branch A does not fire - branch B @ 2026-08-03 23:08:05: the cascade is not counter. walk to ws2r oob, inside the cap to 2026-08-03 23:12:05 | ws1Mage left the past-50 gate @ 2026-08-03 23:08:40: held 8 bars = 40 s, ws1Mage 58.1899 at the stamp | the ws1Mage target-side extrema anchor @ 2026-08-03 23:07:40: ws1Mage 53.2072, 60 s before the stamp | the routed cascade at the anchor @ 2026-08-03 23:07:40: down | down | the low cluster ws1 to ws3, 3 lines, falling COUNTS | the high cluster ws1 to ws3, 3 lines, falling COUNTS | the end-to-end diff +0.33 | zoom 2 rungs, min 3 lines | the route does not fire @ 2026-08-03 23:08:40: the cascade is not counter - the trade stays open, v4saviour is complete |

## the 28 eligible lines at every ws10x-cadence | ws3..ws30

| the ws10x-cadence | the trade it was deciding | ex-20/80 at least once | contributed a reversal | silent - ex-fence but no reversal | never ex-fence |
|---|---|---|---|---|---|
| 2026-08-03 01:44:05 | 2026-08-03 00:41:35 SHORT | 23 of 28 - ws3, ws4, ws5, ws6, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 | 4 of 23 - ws19, ws21, ws22, ws24 | 19 - ws3, ws4, ws5, ws6, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws20, ws23, ws25, ws26, ws27, ws28, ws29, ws30 | 5 - ws7, ws8, ws9, ws10, ws11 |
| 2026-08-03 03:01:35 | 2026-08-03 00:41:35 SHORT | 25 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 | 18 of 25 - ws3, ws4, ws5, ws7, ws12, ws13, ws14, ws15, ws16, ws17, ws19, ws22, ws23, ws24, ws25, ws26, ws28, ws30 | 7 - ws6, ws8, ws18, ws20, ws21, ws27, ws29 | 3 - ws9, ws10, ws11 |
| 2026-08-03 06:22:00 | 2026-08-03 05:01:10 LONG | 14 of 28 - ws3, ws4, ws5, ws6, ws14, ws15, ws16, ws17, ws18, ws19, ws21, ws22, ws24, ws27 | 14 of 14 - ws3, ws4, ws5, ws6, ws14, ws15, ws16, ws17, ws18, ws19, ws21, ws22, ws24, ws27 | 0 - none | 14 - ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws20, ws23, ws25, ws26, ws28, ws29, ws30 |
| 2026-08-03 09:33:10 | 2026-08-03 06:26:25 LONG | 14 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10, ws11, ws14, ws15, ws24, ws27, ws30 | 10 of 14 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10, ws11, ws14 | 4 - ws15, ws24, ws27, ws30 | 14 - ws12, ws13, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws25, ws26, ws28, ws29 |
| 2026-08-03 10:11:55 | 2026-08-03 09:45:35 LONG | 18 of 28 - ws3, ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws19, ws20, ws21, ws24, ws29 | 4 of 18 - ws9, ws10, ws13, ws14 | 14 - ws3, ws6, ws7, ws8, ws11, ws12, ws15, ws16, ws17, ws19, ws20, ws21, ws24, ws29 | 10 - ws4, ws5, ws18, ws22, ws23, ws25, ws26, ws27, ws28, ws30 |
| 2026-08-03 13:27:40 | 2026-08-03 09:45:35 LONG | 21 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws24, ws29 | 8 of 21 - ws3, ws4, ws5, ws6, ws7, ws12, ws17, ws20 | 13 - ws8, ws9, ws10, ws11, ws13, ws14, ws15, ws16, ws18, ws19, ws21, ws24, ws29 | 7 - ws22, ws23, ws25, ws26, ws27, ws28, ws30 |
| 2026-08-03 17:22:20 | 2026-08-03 16:44:05 LONG | 3 of 28 - ws3, ws4, ws7 | 1 of 3 - ws7 | 2 - ws3, ws4 | 25 - ws5, ws6, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-08-03 18:51:55 | 2026-08-03 16:44:05 LONG | 16 of 28 - ws3, ws4, ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19 | 13 of 16 - ws3, ws4, ws6, ws7, ws9, ws10, ws11, ws12, ws14, ws15, ws16, ws17, ws19 | 3 - ws8, ws13, ws18 | 12 - ws5, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-08-03 20:19:25 | 2026-08-03 18:52:05 SHORT | 14 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16 | 10 of 14 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10, ws11, ws12 | 4 - ws13, ws14, ws15, ws16 | 14 - ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-08-03 20:58:50 | 2026-08-03 20:19:55 SHORT | 16 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws19 | 11 of 16 - ws5, ws6, ws8, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws19 | 5 - ws3, ws4, ws7, ws9, ws10 | 12 - ws18, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-08-03 21:22:55 | 2026-08-03 21:03:10 SHORT | 9 of 28 - ws11, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws22 | 4 of 9 - ws14, ws16, ws19, ws22 | 5 - ws11, ws15, ws17, ws18, ws20 | 19 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10, ws12, ws13, ws21, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-08-03 21:23:35 | 2026-08-03 21:03:10 SHORT | 9 of 28 - ws11, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws22 | 6 of 9 - ws14, ws15, ws16, ws17, ws19, ws22 | 3 - ws11, ws18, ws20 | 19 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10, ws12, ws13, ws21, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |

| the roll-up over 12 ws10x-cadences | value |
|---|---|
| eligible lines, every time | 28 |
| population, smallest .. largest | 3 .. 25 |
| population, mean | 15.2 |
| contributed, smallest .. largest | 1 .. 18 |
| contributed, mean | 8.6 |

| the line | times in the population | times it contributed |
|---|---|---|
| ws3 | 10 of 12 | 6 of 12 |
| ws4 | 9 of 12 | 6 of 12 |
| ws5 | 7 of 12 | 6 of 12 |
| ws6 | 9 of 12 | 6 of 12 |
| ws7 | 8 of 12 | 6 of 12 |
| ws8 | 7 of 12 | 3 of 12 |
| ws9 | 6 of 12 | 4 of 12 |
| ws10 | 6 of 12 | 4 of 12 |
| ws11 | 8 of 12 | 4 of 12 |
| ws12 | 7 of 12 | 5 of 12 |
| ws13 | 7 of 12 | 3 of 12 |
| ws14 | 11 of 12 | 8 of 12 |
| ws15 | 11 of 12 | 5 of 12 |
| ws16 | 10 of 12 | 6 of 12 |
| ws17 | 9 of 12 | 6 of 12 |
| ws18 | 7 of 12 | 1 of 12 |
| ws19 | 9 of 12 | 7 of 12 |
| ws20 | 6 of 12 | 1 of 12 |
| ws21 | 5 of 12 | 2 of 12 |
| ws22 | 5 of 12 | 5 of 12 |
| ws23 | 2 of 12 | 1 of 12 |
| ws24 | 6 of 12 | 3 of 12 |
| ws25 | 2 of 12 | 1 of 12 |
| ws26 | 2 of 12 | 1 of 12 |
| ws27 | 4 of 12 | 1 of 12 |
| ws28 | 2 of 12 | 1 of 12 |
| ws29 | 4 of 12 | 0 of 12 |
| ws30 | 3 of 12 | 1 of 12 |

## the legs | every number carries the FDM_MAE_CAP 1.10% stop

| the open | the trade | the rev-trade signal | the exit | the exit kind | held min | MAE% | MFE% | realised% |
|---|---|---|---|---|---|---|---|---|
| 2026-08-03 00:41:35 | SHORT | 2026-08-03 03:01:35 | 2026-08-03 03:01:40 | rev-trade | 140.1 | 0.140 | 1.615 | +1.249 |
| 2026-08-03 03:01:45 | LONG | 2026-08-03 03:05:05 | 2026-08-03 03:05:10 | saviour | 3.4 | 0.292 | 0.111 | -0.292 |
| 2026-08-03 03:05:15 | SHORT | 2026-08-03 05:01:00 | 2026-08-03 05:01:05 | rev-trade | 115.8 | 0.831 | 0.420 | -0.190 |
| 2026-08-03 05:01:10 | LONG | 2026-08-03 06:22:00 | 2026-08-03 06:22:05 | rev-trade | 80.9 | 0.174 | 0.601 | +0.174 |
| 2026-08-03 06:22:10 | SHORT | 2026-08-03 06:26:15 | 2026-08-03 06:26:20 | saviour | 4.2 | 0.118 | 0.024 | -0.063 |
| 2026-08-03 06:26:25 | LONG | 2026-08-03 09:33:10 | 2026-08-03 09:33:15 | rev-trade | 186.8 | 0.844 | 1.080 | +0.852 |
| 2026-08-03 09:33:20 | SHORT | 2026-08-03 09:45:25 | 2026-08-03 09:45:30 | saviour | 12.2 | 0.297 | -0.000 | -0.133 |
| 2026-08-03 09:45:35 | LONG | - | 2026-08-03 13:32:30 | STOP at 1.10% | 226.9 | 1.100 | 1.187 | -1.100 |
| 2026-08-03 14:00:35 | SHORT | 2026-08-03 14:10:10 | 2026-08-03 14:10:15 | saviour | 9.7 | 0.408 | 0.300 | -0.015 |
| 2026-08-03 14:10:20 | LONG | - | 2026-08-03 15:42:00 | STOP at 1.10% | 91.7 | 1.100 | 0.308 | -1.100 |
| 2026-08-03 16:44:05 | LONG | 2026-08-03 18:51:55 | 2026-08-03 18:52:00 | rev-trade | 127.9 | 0.008 | 3.703 | +2.599 |
| 2026-08-03 18:52:05 | SHORT | 2026-08-03 20:19:25 | 2026-08-03 20:19:30 | rev-trade | 87.4 | 0.334 | 0.607 | +0.356 |
| 2026-08-03 20:19:35 | LONG | 2026-08-03 20:19:45 | 2026-08-03 20:19:50 | saviour | 0.2 | 0.030 | 0.030 | -0.015 |
| 2026-08-03 20:19:55 | SHORT | 2026-08-03 20:58:50 | 2026-08-03 20:58:55 | rev-trade | 39.0 | 0.281 | 0.479 | -0.228 |
| 2026-08-03 20:59:00 | LONG | 2026-08-03 21:03:00 | 2026-08-03 21:03:05 | rev-trade | 4.1 | 0.205 | 0.311 | -0.182 |
| 2026-08-03 21:03:10 | SHORT | 2026-08-03 21:23:35 | 2026-08-03 21:23:40 | rev-trade | 20.5 | 0.000 | 0.592 | +0.220 |
| 2026-08-03 21:23:45 | LONG | - | 2026-08-03 22:06:05 | STOP at 1.10% | 42.3 | 1.100 | 0.015 | -1.100 |
| 2026-08-03 22:56:05 | SHORT | - | 2026-08-03 23:59:55 | no rev-trade before the walk's end | 63.8 | 0.661 | 0.692 | -0.578 |

| the aggregate | value |
|---|---|
| legs | 18 |
| stopped | 3 |
| gross % | +0.452 |
| drag % | -3.555 (0.1975% round trip x 18 legs) |
| net % | -3.103 |
| MAE % total | 7.924 |
| MFE % total | 12.074 |
| MFE captured | 3.7% of MFE |
| held min, shortest .. longest | 0.2 .. 226.9 |
