# fdm2 | TAPE 1632960 bars, ends 2026-10-04 23:59:55 | RULED_OK True
# THE WALK RUNS 2026-09-15 00:00:00 .. 2026-09-17 23:59:55 - HIS one-day bound
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
| the re-entry signal bar | 2026-09-15 00:41:00 |
| the gcws30b window side | HIGH oob |
| the trade | SHORT |
| its target side | LOW |
| the open price bar | 2026-09-15 00:41:05 - the router's "just OPEN", 1 bar |
| why | HIGH window 00:33:30..00:41:00, 7.5 min, opened on both and closed on ws1b, ws1r AND (ws2r or ws3r) seen past the 75.0 fence - ws1 00:35:20, ws2 00:34:05, ws3 00:33:30 - gate TRUE at the close |

## leg 2026-09-15 00:41:05 | SHORT | target side LOW | fdm re-entry 2026-09-15 00:41:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 01:03:00 | WALK | cadence event, 5 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-15 01:20:00, the ws10x-cadence confirms 2026-09-15 01:21:55) || ws1b excursion 2026-09-15 01:01:00..2026-09-15 01:02:55, the nestle is ws1Mage 8.59 deeper than ws2r 13.01 at 2026-09-15 01:01:00 |
| 2026-09-15 01:21:55 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-09-15 01:20:00 and confirmed here. 13 of 16 reversed since 2026-09-15 01:03:00 (event) = 81.2% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-15 01:22:05 | LONG | target side HIGH | rev-trade 2026-09-15 01:21:55

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 02:43:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10Mage 2026-09-15 02:47:00, the ws10x-cadence confirms 2026-09-15 02:48:55) || ws1b excursion 2026-09-15 02:42:00..2026-09-15 02:42:55, the nestle is ws1Mage 88.27 deeper than ws3r 85.37 at 2026-09-15 02:42:00, ws3Mage RESCUED - the both window opened 2026-09-15 02:40:00, ws3r reached 85.37 and ws3Mage reached 73.73 |
| 2026-09-15 02:48:55 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10Mage 2026-09-15 02:47:00 and confirmed here. 3 of 4 reversed since 2026-09-15 02:43:00 (event) = 75.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-15 02:49:05 | SHORT | target side LOW | rev-trade 2026-09-15 02:48:55

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 03:20:00 | WALK | cadence event, 4 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10Mage 2026-09-15 03:20:35, the ws10x-cadence confirms 2026-09-15 03:22:30) || ws1b excursion 2026-09-15 03:02:00..2026-09-15 03:19:55, the nestle is ws1Mage -10.95 deeper than ws1r 12.89 at 2026-09-15 03:05:00 |
| 2026-09-15 03:22:30 | NO ACTION | the ws10x-cadence - ws10x crossed to ws10Mage 2026-09-15 03:20:35 and confirmed here. 3 of 8 reversed since 2026-09-15 03:20:00 (event) = 37.5% < 40% - no branch, wait for the next cadence event |
| 2026-09-15 04:41:00 | REV-TRADE | cadence event, 0 of 27 lines ws4..ws30 printing ex-20/80 AND towards - his "if the answer is no, then rev-trade" || ws1b excursion 2026-09-15 04:37:00..2026-09-15 04:40:55, the nestle is ws1Mage -7.40 deeper than ws2r 10.47 at 2026-09-15 04:38:00 |

## leg 2026-09-15 04:41:10 | LONG | target side HIGH | rev-trade 2026-09-15 04:41:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 05:59:00 | WALK | cadence event, 1 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-15 06:10:15, the ws10x-cadence confirms 2026-09-15 06:12:10) || ws1b excursion 2026-09-15 05:53:00..2026-09-15 05:58:55, the nestle is ws1Mage 111.11 deeper than ws2r 93.87 at 2026-09-15 05:53:00, ws3Mage RESCUED - the both window opened 2026-09-15 05:53:00, ws3r reached 94.67 and ws3Mage reached 69.16 |
| 2026-09-15 06:12:10 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-09-15 06:10:15 and confirmed here. 3 of 5 reversed since 2026-09-15 05:59:00 (event) = 60.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-15 06:12:20 | SHORT | target side LOW | rev-trade 2026-09-15 06:12:10

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 07:04:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10Mage 2026-09-15 07:17:05, the ws10x-cadence confirms 2026-09-15 07:19:00) || ws1b excursion 2026-09-15 06:53:00..2026-09-15 07:03:55, the nestle is ws1Mage -23.59 deeper than ws1r 4.29 at 2026-09-15 06:55:00 |
| 2026-09-15 07:19:00 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10Mage 2026-09-15 07:17:05 and confirmed here. 6 of 6 reversed since 2026-09-15 07:04:00 (event) = 100.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-15 07:19:10 | LONG | target side HIGH | rev-trade 2026-09-15 07:19:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 08:45:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the next cadence event is first (ws10x crosses to ib 2026-09-15 09:10:50, the ws10x-cadence confirms 2026-09-15 09:12:45) || ws1b excursion 2026-09-15 08:43:00..2026-09-15 08:44:55, the nestle is ws1Mage 94.63 deeper than ws3r 92.34 at 2026-09-15 08:43:00, ws3Mage RESCUED - the both window opened 2026-09-15 08:43:00, ws3r reached 92.34 and ws3Mage reached 69.42 |
| 2026-09-15 09:03:00 | WALK | cadence event, 6 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-15 09:10:50, the ws10x-cadence confirms 2026-09-15 09:12:45) || ws1b excursion 2026-09-15 08:57:00..2026-09-15 09:02:55, the nestle is ws1Mage 100.57 deeper than ws1r 92.55 at 2026-09-15 08:57:00 |
| 2026-09-15 09:12:45 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-09-15 09:10:50 and confirmed here. 6 of 9 reversed since 2026-09-15 09:03:00 (event) = 66.7% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-15 09:12:55 | SHORT | target side LOW | rev-trade 2026-09-15 09:12:45

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 11:40:00 | WALK | cadence event, 6 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10Mage 2026-09-15 11:50:55, the ws10x-cadence confirms 2026-09-15 11:52:50) || ws1b excursion 2026-09-15 11:19:00..2026-09-15 11:39:55, the nestle is ws1Mage -1.68 deeper than ws3r 11.35 at 2026-09-15 11:24:00 |
| 2026-09-15 11:52:50 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10Mage 2026-09-15 11:50:55 and confirmed here. 11 of 13 reversed since 2026-09-15 11:40:00 (event) = 84.6% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-15 11:53:00 | LONG | target side HIGH | rev-trade 2026-09-15 11:52:50

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 12:25:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-15 12:30:35, the ws10x-cadence confirms 2026-09-15 12:32:30) || ws1b excursion 2026-09-15 12:12:00..2026-09-15 12:24:55, the nestle is ws1Mage 107.30 deeper than ws3r 99.38 at 2026-09-15 12:14:00 |
| 2026-09-15 12:32:30 | NO ACTION | the ws10x-cadence - ws10x crossed to ib 2026-09-15 12:30:35 and confirmed here. 1 of 4 reversed since 2026-09-15 12:25:00 (event) = 25.0% < 40% - no branch, wait for the next cadence event |
| 2026-09-15 12:58:00 | WALK | cadence event, 1 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-15 13:22:05, the ws10x-cadence confirms 2026-09-15 13:24:00) || ws1b excursion 2026-09-15 12:53:00..2026-09-15 12:57:55, the nestle is ws1Mage 119.99 deeper than ws1r 100.00 at 2026-09-15 12:55:00 |
| 2026-09-15 13:24:00 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-09-15 13:22:05 and confirmed here. 9 of 9 reversed since 2026-09-15 12:58:00 (event) = 100.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-15 13:24:10 | SHORT | target side LOW | rev-trade 2026-09-15 13:24:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 13:41:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the next cadence event is first (ws10x crosses to ib 2026-09-15 13:53:55, the ws10x-cadence confirms 2026-09-15 13:55:50) || ws1b excursion 2026-09-15 13:36:00..2026-09-15 13:40:55, the nestle is ws1Mage 0.24 deeper than ws3r 3.16 at 2026-09-15 13:36:00 |
| 2026-09-15 13:48:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-15 13:53:55, the ws10x-cadence confirms 2026-09-15 13:55:50) || ws1b excursion 2026-09-15 13:42:00..2026-09-15 13:47:55, the nestle is ws2Mage 4.92 deeper than ws3r 8.04 at 2026-09-15 13:44:00 |
| 2026-09-15 13:55:50 | GRACE | the ws10x-cadence - ws10x crossed to ib 2026-09-15 13:53:55 and confirmed here. 2 of 5 reversed since 2026-09-15 13:48:00 (event) = 40.0% >= 40% -> grace walk 2026-09-15 13:55:55 .. 2026-09-15 14:00:50, 60 bars = 5.0 min, population frozen at 5 lines |
| 2026-09-15 13:56:00 | REV-TRADE | grace walk, 3 of 5 reversed since 2026-09-15 13:48:00 (event) = 60.0% >= 50% |

## leg 2026-09-15 13:56:10 | LONG | target side HIGH | rev-trade 2026-09-15 13:56:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 13:56:10 | NO CADENCE EVENT | no cadence event on the HIGH side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-15 14:55:05 | LONG | target side HIGH | fdm re-entry 2026-09-15 14:55:00, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 17:42:00 | WALK | cadence event, 1 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-15 17:59:20, the ws10x-cadence confirms 2026-09-15 18:01:15) || ws1b excursion 2026-09-15 17:32:00..2026-09-15 17:41:55, the nestle is ws1Mage 97.01 deeper than ws1r 85.53 at 2026-09-15 17:32:00 |
| 2026-09-15 18:01:15 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-09-15 17:59:20 and confirmed here. 15 of 18 reversed since 2026-09-15 17:42:00 (event) = 83.3% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-15 18:01:25 | SHORT | target side LOW | rev-trade 2026-09-15 18:01:15

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 18:29:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10Mage 2026-09-15 18:50:00, the ws10x-cadence confirms 2026-09-15 18:51:55) || ws1b excursion 2026-09-15 18:17:00..2026-09-15 18:28:55, the nestle is ws1Mage -5.84 deeper than ws3r 4.31 at 2026-09-15 18:17:00, ws3Mage RESCUED - the both window opened 2026-09-15 18:17:00, ws3r reached 2.89 and ws3Mage reached 31.16 |
| 2026-09-15 18:51:55 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10Mage 2026-09-15 18:50:00 and confirmed here. 6 of 6 reversed since 2026-09-15 18:29:00 (event) = 100.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-15 18:52:05 | LONG | target side HIGH | rev-trade 2026-09-15 18:51:55

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 21:00:00 | WALK | cadence event, 1 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-15 21:00:30, the ws10x-cadence confirms 2026-09-15 21:02:25) || ws1b excursion 2026-09-15 20:50:00..2026-09-15 20:59:55, the nestle is ws1Mage 115.86 deeper than ws2r 94.73 at 2026-09-15 20:50:00 |
| 2026-09-15 21:02:25 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-09-15 21:00:30 and confirmed here. 4 of 5 reversed since 2026-09-15 21:00:00 (event) = 80.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-15 21:02:35 | SHORT | target side LOW | rev-trade 2026-09-15 21:02:25

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 22:03:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-15 22:10:15, the ws10x-cadence confirms 2026-09-15 22:12:10) || ws1b excursion 2026-09-15 21:59:00..2026-09-15 22:02:55, the nestle is ws1Mage -4.31 deeper than ws1r 13.15 at 2026-09-15 21:59:00 |
| 2026-09-15 22:12:10 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-09-15 22:10:15 and confirmed here. 3 of 6 reversed since 2026-09-15 22:03:00 (event) = 50.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-15 22:12:20 | LONG | target side HIGH | rev-trade 2026-09-15 22:12:10

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 23:00:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the next cadence event is first (ws10x crosses to ib 2026-09-15 23:30:00, the ws10x-cadence confirms 2026-09-15 23:31:55) || ws1b excursion 2026-09-15 22:52:00..2026-09-15 22:59:55, the nestle is ws2Mage 92.43 deeper than ws3r 86.13 at 2026-09-15 22:52:00 |
| 2026-09-15 23:22:00 | WALK | cadence event, 8 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-15 23:30:00, the ws10x-cadence confirms 2026-09-15 23:31:55) || ws1b excursion 2026-09-15 23:01:00..2026-09-15 23:21:55, the nestle is ws1Mage 94.14 deeper than ws3r 88.16 at 2026-09-15 23:06:00 |
| 2026-09-15 23:31:55 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-09-15 23:30:00 and confirmed here. 9 of 9 reversed since 2026-09-15 23:22:00 (event) = 100.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-15 23:32:05 | SHORT | target side LOW | rev-trade 2026-09-15 23:31:55

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 01:01:00 | WALK | cadence event, 9 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10r 2026-09-16 01:10:25, the ws10x-cadence confirms 2026-09-16 01:12:20) || ws1b excursion 2026-09-16 00:50:00..2026-09-16 01:00:55, the nestle is ws1Mage -3.35 deeper than ws3r 12.25 at 2026-09-16 00:51:00 |
| 2026-09-16 01:12:20 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10r 2026-09-16 01:10:25 and confirmed here. 9 of 12 reversed since 2026-09-16 01:01:00 (event) = 75.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-16 01:12:30 | LONG | target side HIGH | rev-trade 2026-09-16 01:12:20

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 01:12:30 | NO CADENCE EVENT | no cadence event on the HIGH side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-16 01:46:05 | LONG | target side HIGH | fdm re-entry 2026-09-16 01:46:00, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 02:41:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-16 02:50:00, the ws10x-cadence confirms 2026-09-16 02:51:55) || ws1b excursion 2026-09-16 02:30:00..2026-09-16 02:40:55, the nestle is ws1Mage 95.25 deeper than ws3r 85.73 at 2026-09-16 02:31:00, ws3Mage RESCUED - the both window opened 2026-09-15 23:09:30, ws3r reached 100.00 and ws3Mage reached 107.58 |
| 2026-09-16 02:51:55 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-09-16 02:50:00 and confirmed here. 5 of 7 reversed since 2026-09-16 02:41:00 (event) = 71.4% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-16 02:52:05 | SHORT | target side LOW | rev-trade 2026-09-16 02:51:55

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 05:10:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10r 2026-09-16 05:21:15, the ws10x-cadence confirms 2026-09-16 05:23:10) || ws1b excursion 2026-09-16 05:03:00..2026-09-16 05:09:55, the nestle is ws1Mage -13.41 deeper than ws3r 10.27 at 2026-09-16 05:03:00 |
| 2026-09-16 05:23:10 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10r 2026-09-16 05:21:15 and confirmed here. 5 of 6 reversed since 2026-09-16 05:10:00 (event) = 83.3% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-16 05:23:20 | LONG | target side HIGH | rev-trade 2026-09-16 05:23:10

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 05:46:00 | WALK | cadence event, 1 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10r 2026-09-16 05:51:35, the ws10x-cadence confirms 2026-09-16 05:53:30) || ws1b excursion 2026-09-16 05:45:00..2026-09-16 05:45:55, the nestle is ws1Mage 91.75 deeper than ws1r 86.09 at 2026-09-16 05:45:00, ws3Mage RESCUED - the both window opened 2026-09-16 04:23:30, ws3r reached 90.59 and ws3Mage reached 117.06 |
| 2026-09-16 05:53:30 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10r 2026-09-16 05:51:35 and confirmed here. 4 of 5 reversed since 2026-09-16 05:46:00 (event) = 80.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-16 05:53:40 | SHORT | target side LOW | rev-trade 2026-09-16 05:53:30

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 06:41:00 | REV-TRADE | cadence event, 0 of 27 lines ws4..ws30 printing ex-20/80 AND towards - his "if the answer is no, then rev-trade" || ws1b excursion 2026-09-16 06:36:00..2026-09-16 06:40:55, the nestle is ws1Mage -11.78 deeper than ws2r 11.96 at 2026-09-16 06:38:00 |

## leg 2026-09-16 06:41:10 | LONG | target side HIGH | rev-trade 2026-09-16 06:41:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 07:07:00 | REV-TRADE | cadence event, 0 of 27 lines ws4..ws30 printing ex-20/80 AND towards - his "if the answer is no, then rev-trade" || ws1b excursion 2026-09-16 07:02:00..2026-09-16 07:06:55, the nestle is ws1Mage 107.60 deeper than ws1r 88.24 at 2026-09-16 07:02:00 |

## leg 2026-09-16 07:07:10 | SHORT | target side LOW | rev-trade 2026-09-16 07:07:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 08:11:00 | WALK | cadence event, 4 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-16 08:16:35, the ws10x-cadence confirms 2026-09-16 08:18:30) || ws1b excursion 2026-09-16 08:04:00..2026-09-16 08:10:55, the nestle is ws1Mage -13.77 deeper than ws1r 10.76 at 2026-09-16 08:06:00 |
| 2026-09-16 08:18:30 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-09-16 08:16:35 and confirmed here. 6 of 8 reversed since 2026-09-16 08:11:00 (event) = 75.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-16 08:18:40 | LONG | target side HIGH | rev-trade 2026-09-16 08:18:30

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 10:49:00 | WALK | cadence event, 4 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10Mage 2026-09-16 10:52:05, the ws10x-cadence confirms 2026-09-16 10:54:00) || ws1b excursion 2026-09-16 10:43:00..2026-09-16 10:48:55, the nestle is ws1Mage 95.38 deeper than ws1r 92.08 at 2026-09-16 10:48:00 |
| 2026-09-16 10:54:00 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10Mage 2026-09-16 10:52:05 and confirmed here. 11 of 13 reversed since 2026-09-16 10:49:00 (event) = 84.6% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-16 10:54:10 | SHORT | target side LOW | rev-trade 2026-09-16 10:54:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 12:34:00 | WALK | cadence event, 1 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-16 12:49:10, the ws10x-cadence confirms 2026-09-16 12:51:05) || ws1b excursion 2026-09-16 12:26:00..2026-09-16 12:33:55, the nestle is ws1Mage 8.47 deeper than ws3r 14.37 at 2026-09-16 12:30:00 |
| 2026-09-16 12:51:05 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-09-16 12:49:10 and confirmed here. 6 of 6 reversed since 2026-09-16 12:34:00 (event) = 100.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-16 12:51:15 | LONG | target side HIGH | rev-trade 2026-09-16 12:51:05

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 12:51:15 | NO CADENCE EVENT | no cadence event on the HIGH side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-16 13:52:05 | SHORT | target side LOW | fdm re-entry 2026-09-16 13:52:00, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 14:16:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the next cadence event is first (ws10x crosses to ws10Mage 2026-09-16 14:20:00, the ws10x-cadence confirms 2026-09-16 14:21:55) || ws1b excursion 2026-09-16 14:09:00..2026-09-16 14:15:55, the nestle is ws1Mage 6.31 deeper than ws2r 9.56 at 2026-09-16 14:11:00 |
| 2026-09-16 14:21:00 | WALK | cadence event, 4 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10Mage 2026-09-16 14:24:40, the ws10x-cadence confirms 2026-09-16 14:26:35) || ws1b excursion 2026-09-16 14:20:00..2026-09-16 14:20:55, the nestle is ws2Mage 7.17 deeper than ws3r 9.68 at 2026-09-16 14:20:00 |
| 2026-09-16 14:26:35 | GRACE | the ws10x-cadence - ws10x crossed to ws10Mage 2026-09-16 14:24:40 and confirmed here. 3 of 7 reversed since 2026-09-16 14:21:00 (event) = 42.9% >= 40% -> grace walk 2026-09-16 14:26:40 .. 2026-09-16 14:31:35, 60 bars = 5.0 min, population frozen at 7 lines |
| 2026-09-16 14:26:40 | REV-TRADE | grace walk, 5 of 7 reversed since 2026-09-16 14:21:00 (event) = 71.4% >= 50% |

## leg 2026-09-16 14:26:50 | LONG | target side HIGH | rev-trade 2026-09-16 14:26:40

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 14:26:50 | NO CADENCE EVENT | no cadence event on the HIGH side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-16 15:35:05 | LONG | target side HIGH | fdm re-entry 2026-09-16 15:35:00, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 15:35:05 | NO CADENCE EVENT | no cadence event on the HIGH side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-16 17:54:05 | LONG | target side HIGH | fdm re-entry 2026-09-16 17:54:00, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 18:15:00 | WALK | cadence event, 1 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-16 18:21:15, the ws10x-cadence confirms 2026-09-16 18:23:10) || ws1b excursion 2026-09-16 18:04:00..2026-09-16 18:14:55, the nestle is ws1Mage 103.42 deeper than ws2r 93.23 at 2026-09-16 18:04:00 |
| 2026-09-16 18:23:10 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-09-16 18:21:15 and confirmed here. 1 of 2 reversed since 2026-09-16 18:15:00 (event) = 50.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-16 18:23:20 | SHORT | target side LOW | rev-trade 2026-09-16 18:23:10

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 18:23:20 | NO CADENCE EVENT | no cadence event on the LOW side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-16 21:45:05 | LONG | target side HIGH | fdm re-entry 2026-09-16 21:45:00, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 21:45:05 | NO CADENCE EVENT | no cadence event on the HIGH side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-16 22:57:05 | LONG | target side HIGH | fdm re-entry 2026-09-16 22:57:00, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 23:32:00 | WALK | cadence event, 1 of 27 lines printing ex-20/80 AND towards -> walk. the next cadence event is first (ws10x crosses to ib 2026-09-17 00:04:10, the ws10x-cadence confirms 2026-09-17 00:06:05) || ws1b excursion 2026-09-16 23:17:00..2026-09-16 23:31:55, the nestle is ws1Mage 108.76 deeper than ws2r 91.08 at 2026-09-16 23:18:00 |
| 2026-09-16 23:36:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-17 00:04:10, the ws10x-cadence confirms 2026-09-17 00:06:05) || ws1b excursion 2026-09-16 23:34:00..2026-09-16 23:35:55, the nestle is ws2Mage 96.91 deeper than ws3r 93.14 at 2026-09-16 23:34:00 |
| 2026-09-17 00:06:05 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-09-17 00:04:10 and confirmed here. 7 of 7 reversed since 2026-09-16 23:36:00 (event) = 100.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-17 00:06:15 | SHORT | target side LOW | rev-trade 2026-09-17 00:06:05

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 00:57:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10r 2026-09-17 01:06:40, the ws10x-cadence confirms 2026-09-17 01:08:35) || ws1b excursion 2026-09-17 00:56:00..2026-09-17 00:56:55, the nestle is ws1Mage 4.34 deeper than ws2r 6.51 at 2026-09-17 00:56:00, ws3Mage RESCUED - the both window opened 2026-09-16 22:51:00, ws3r reached 0.69 and ws3Mage reached 12.13 |
| 2026-09-17 01:08:35 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10r 2026-09-17 01:06:40 and confirmed here. 4 of 4 reversed since 2026-09-17 00:57:00 (event) = 100.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-17 01:08:45 | LONG | target side HIGH | rev-trade 2026-09-17 01:08:35

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 01:40:00 | WALK | cadence event, 10 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10Mage 2026-09-17 01:50:00, the ws10x-cadence confirms 2026-09-17 01:51:55) || ws1b excursion 2026-09-17 01:26:00..2026-09-17 01:39:55, the nestle is ws1Mage 119.84 deeper than ws3r 85.39 at 2026-09-17 01:26:00 |
| 2026-09-17 01:51:55 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10Mage 2026-09-17 01:50:00 and confirmed here. 13 of 16 reversed since 2026-09-17 01:40:00 (event) = 81.2% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-17 01:52:05 | SHORT | target side LOW | rev-trade 2026-09-17 01:51:55

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 02:25:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-17 02:26:00, the ws10x-cadence confirms 2026-09-17 02:27:55) || ws1b excursion 2026-09-17 02:12:00..2026-09-17 02:24:55, the nestle is ws1Mage 4.38 deeper than ws1r 12.89 at 2026-09-17 02:12:00 |
| 2026-09-17 02:27:55 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-09-17 02:26:00 and confirmed here. 4 of 4 reversed since 2026-09-17 02:25:00 (event) = 100.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-17 02:28:05 | LONG | target side HIGH | rev-trade 2026-09-17 02:27:55

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 02:48:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-17 03:13:00, the ws10x-cadence confirms 2026-09-17 03:14:55) || ws1b excursion 2026-09-17 02:43:00..2026-09-17 02:47:55, the nestle is ws1Mage 96.76 deeper than ws2r 91.61 at 2026-09-17 02:43:00 |
| 2026-09-17 03:14:55 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-09-17 03:13:00 and confirmed here. 6 of 7 reversed since 2026-09-17 02:48:00 (event) = 85.7% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-17 03:15:05 | SHORT | target side LOW | rev-trade 2026-09-17 03:14:55

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 03:15:05 | NO CADENCE EVENT | no cadence event on the LOW side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-17 03:40:05 | SHORT | target side LOW | fdm re-entry 2026-09-17 03:40:00, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 03:40:05 | NO CADENCE EVENT | no cadence event on the LOW side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-17 05:33:05 | SHORT | target side LOW | fdm re-entry 2026-09-17 05:33:00, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 05:33:05 | NO CADENCE EVENT | no cadence event on the LOW side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-17 06:43:05 | SHORT | target side LOW | fdm re-entry 2026-09-17 06:43:00, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 06:43:05 | NO CADENCE EVENT | no cadence event on the LOW side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-17 09:45:05 | LONG | target side HIGH | fdm re-entry 2026-09-17 09:45:00, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 09:45:05 | NO CADENCE EVENT | no cadence event on the HIGH side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-17 11:47:05 | LONG | target side HIGH | fdm re-entry 2026-09-17 11:47:00, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 12:03:00 | REV-TRADE | cadence event, 0 of 27 lines ws4..ws30 printing ex-20/80 AND towards - his "if the answer is no, then rev-trade" || ws1b excursion 2026-09-17 12:02:00..2026-09-17 12:02:55, the nestle is ws1Mage 101.84 deeper than ws1r 98.19 at 2026-09-17 12:02:00 |

## leg 2026-09-17 12:03:10 | SHORT | target side LOW | rev-trade 2026-09-17 12:03:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 12:03:10 | NO CADENCE EVENT | no cadence event on the LOW side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-17 13:15:05 | LONG | target side HIGH | fdm re-entry 2026-09-17 13:15:00, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 13:15:05 | NO CADENCE EVENT | no cadence event on the HIGH side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-17 13:43:05 | LONG | target side HIGH | fdm re-entry 2026-09-17 13:43:00, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 13:43:05 | NO CADENCE EVENT | no cadence event on the HIGH side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-17 15:47:05 | SHORT | target side LOW | fdm re-entry 2026-09-17 15:47:00, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 15:47:05 | NO CADENCE EVENT | no cadence event on the LOW side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-17 17:10:05 | SHORT | target side LOW | fdm re-entry 2026-09-17 17:10:00, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 18:42:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-17 18:47:45, the ws10x-cadence confirms 2026-09-17 18:49:40) || ws1b excursion 2026-09-17 18:34:00..2026-09-17 18:41:55, the nestle is ws1Mage -6.13 deeper than ws1r 14.39 at 2026-09-17 18:39:00 |
| 2026-09-17 18:49:40 | NO ACTION | the ws10x-cadence - ws10x crossed to ib 2026-09-17 18:47:45 and confirmed here. 2 of 6 reversed since 2026-09-17 18:42:00 (event) = 33.3% < 40% - no branch, wait for the next cadence event |
| 2026-09-17 19:03:00 | WALK | cadence event, 1 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-09-17 19:21:35, the ws10x-cadence confirms 2026-09-17 19:23:30) || ws1b excursion 2026-09-17 19:02:00..2026-09-17 19:02:55, the nestle is ws2Mage 10.79 deeper than ws1r 13.90 at 2026-09-17 19:02:00 |
| 2026-09-17 19:23:30 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-09-17 19:21:35 and confirmed here. 6 of 9 reversed since 2026-09-17 19:03:00 (event) = 66.7% >= 50% at the ws10x-cadence bar itself |

## leg 2026-09-17 19:23:40 | LONG | target side HIGH | rev-trade 2026-09-17 19:23:30

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 19:23:40 | NO CADENCE EVENT | no cadence event on the HIGH side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-17 22:51:05 | SHORT | target side LOW | fdm re-entry 2026-09-17 22:51:00, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 22:51:05 | NO CADENCE EVENT | no cadence event on the LOW side from the open to 2026-09-17 23:59:55 |

## the 28 eligible lines at every ws10x-cadence | ws3..ws30

| the ws10x-cadence | the trade it was deciding | ex-20/80 at least once | contributed a reversal | silent - ex-fence but no reversal | never ex-fence |
|---|---|---|---|---|---|
| 2026-09-15 01:21:55 | 2026-09-15 00:41:05 SHORT | 16 of 28 - ws3, ws4, ws5, ws6, ws14, ws15, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 | 13 of 16 - ws3, ws4, ws5, ws6, ws14, ws15, ws21, ws22, ws23, ws24, ws25, ws29, ws30 | 3 - ws26, ws27, ws28 | 12 - ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws16, ws17, ws18, ws19, ws20 |
| 2026-09-15 02:48:55 | 2026-09-15 01:22:05 LONG | 4 of 28 - ws3, ws7, ws8, ws9 | 3 of 4 - ws3, ws7, ws8 | 1 - ws9 | 24 - ws4, ws5, ws6, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-15 03:22:30 | 2026-09-15 02:49:05 SHORT | 8 of 28 - ws3, ws5, ws19, ws24, ws25, ws28, ws29, ws30 | 3 of 8 - ws3, ws5, ws24 | 5 - ws19, ws25, ws28, ws29, ws30 | 20 - ws4, ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws20, ws21, ws22, ws23, ws26, ws27 |
| 2026-09-15 06:12:10 | 2026-09-15 04:41:10 LONG | 5 of 28 - ws3, ws4, ws5, ws14, ws24 | 3 of 5 - ws5, ws14, ws24 | 2 - ws3, ws4 | 23 - ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-15 07:19:00 | 2026-09-15 06:12:20 SHORT | 6 of 28 - ws3, ws4, ws5, ws6, ws7, ws8 | 6 of 6 - ws3, ws4, ws5, ws6, ws7, ws8 | 0 - none | 22 - ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-15 09:12:45 | 2026-09-15 07:19:10 LONG | 9 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws13, ws16, ws27 | 6 of 9 - ws3, ws4, ws5, ws6, ws7, ws13 | 3 - ws8, ws16, ws27 | 19 - ws9, ws10, ws11, ws12, ws14, ws15, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws28, ws29, ws30 |
| 2026-09-15 11:52:50 | 2026-09-15 09:12:55 SHORT | 13 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws15, ws16 | 11 of 13 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws11, ws12, ws15, ws16 | 2 - ws10, ws13 | 15 - ws14, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-15 12:32:30 | 2026-09-15 11:53:00 LONG | 4 of 28 - ws3, ws4, ws5, ws6 | 1 of 4 - ws6 | 3 - ws3, ws4, ws5 | 24 - ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-15 13:24:00 | 2026-09-15 11:53:00 LONG | 9 of 28 - ws3, ws4, ws5, ws6, ws7, ws9, ws10, ws11, ws12 | 9 of 9 - ws3, ws4, ws5, ws6, ws7, ws9, ws10, ws11, ws12 | 0 - none | 19 - ws8, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-15 13:55:50 | 2026-09-15 13:24:10 SHORT | 5 of 28 - ws3, ws4, ws5, ws6, ws8 | 2 of 5 - ws5, ws8 | 3 - ws3, ws4, ws6 | 23 - ws7, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-15 13:56:00 | 2026-09-15 13:24:10 SHORT | 5 of 28 - ws3, ws4, ws5, ws6, ws8 | 3 of 5 - ws5, ws6, ws8 | 2 - ws3, ws4 | 23 - ws7, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-15 18:01:15 | 2026-09-15 14:55:05 LONG | 18 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21 | 15 of 18 - ws4, ws5, ws6, ws7, ws8, ws9, ws11, ws12, ws14, ws15, ws16, ws17, ws18, ws20, ws21 | 3 - ws3, ws13, ws19 | 10 - ws10, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-15 18:51:55 | 2026-09-15 18:01:25 SHORT | 6 of 28 - ws3, ws4, ws5, ws6, ws7, ws8 | 6 of 6 - ws3, ws4, ws5, ws6, ws7, ws8 | 0 - none | 22 - ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-15 21:02:25 | 2026-09-15 18:52:05 LONG | 5 of 28 - ws3, ws4, ws5, ws7, ws8 | 4 of 5 - ws4, ws5, ws7, ws8 | 1 - ws3 | 23 - ws6, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-15 22:12:10 | 2026-09-15 21:02:35 SHORT | 6 of 28 - ws4, ws5, ws6, ws7, ws22, ws25 | 3 of 6 - ws4, ws7, ws22 | 3 - ws5, ws6, ws25 | 22 - ws3, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws23, ws24, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-15 23:31:55 | 2026-09-15 22:12:20 LONG | 9 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10, ws11 | 9 of 9 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10, ws11 | 0 - none | 19 - ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-16 01:12:20 | 2026-09-15 23:32:05 SHORT | 12 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14 | 9 of 12 - ws3, ws4, ws5, ws6, ws8, ws9, ws10, ws11, ws13 | 3 - ws7, ws12, ws14 | 16 - ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-16 02:51:55 | 2026-09-16 01:46:05 LONG | 7 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws9 | 5 of 7 - ws3, ws4, ws5, ws6, ws7 | 2 - ws8, ws9 | 21 - ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-16 05:23:10 | 2026-09-16 02:52:05 SHORT | 6 of 28 - ws3, ws4, ws5, ws6, ws7, ws8 | 5 of 6 - ws4, ws5, ws6, ws7, ws8 | 1 - ws3 | 22 - ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-16 05:53:30 | 2026-09-16 05:23:20 LONG | 5 of 28 - ws3, ws23, ws25, ws26, ws29 | 4 of 5 - ws3, ws23, ws25, ws29 | 1 - ws26 | 23 - ws4, ws5, ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws24, ws27, ws28, ws30 |
| 2026-09-16 08:18:30 | 2026-09-16 07:07:10 SHORT | 8 of 28 - ws3, ws4, ws6, ws9, ws12, ws23, ws24, ws26 | 6 of 8 - ws3, ws4, ws6, ws9, ws12, ws26 | 2 - ws23, ws24 | 20 - ws5, ws7, ws8, ws10, ws11, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws25, ws27, ws28, ws29, ws30 |
| 2026-09-16 10:54:00 | 2026-09-16 08:18:40 LONG | 13 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10, ws11, ws15, ws17, ws18, ws19 | 11 of 13 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10, ws15, ws18, ws19 | 2 - ws11, ws17 | 15 - ws12, ws13, ws14, ws16, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-16 12:51:05 | 2026-09-16 10:54:10 SHORT | 6 of 28 - ws3, ws4, ws5, ws6, ws7, ws10 | 6 of 6 - ws3, ws4, ws5, ws6, ws7, ws10 | 0 - none | 22 - ws8, ws9, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-16 14:26:35 | 2026-09-16 13:52:05 SHORT | 7 of 28 - ws3, ws4, ws5, ws14, ws17, ws20, ws21 | 3 of 7 - ws3, ws4, ws14 | 4 - ws5, ws17, ws20, ws21 | 21 - ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws15, ws16, ws18, ws19, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-16 14:26:40 | 2026-09-16 13:52:05 SHORT | 7 of 28 - ws3, ws4, ws5, ws14, ws17, ws20, ws21 | 5 of 7 - ws3, ws4, ws5, ws14, ws20 | 2 - ws17, ws21 | 21 - ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws15, ws16, ws18, ws19, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-16 18:23:10 | 2026-09-16 17:54:05 LONG | 2 of 28 - ws3, ws4 | 1 of 2 - ws4 | 1 - ws3 | 26 - ws5, ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-17 00:06:05 | 2026-09-16 22:57:05 LONG | 7 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws9 | 7 of 7 - ws3, ws4, ws5, ws6, ws7, ws8, ws9 | 0 - none | 21 - ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-17 01:08:35 | 2026-09-17 00:06:15 SHORT | 4 of 28 - ws3, ws4, ws5, ws6 | 4 of 4 - ws3, ws4, ws5, ws6 | 0 - none | 24 - ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-17 01:51:55 | 2026-09-17 01:08:45 LONG | 16 of 28 - ws3, ws4, ws5, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws25, ws26, ws27 | 13 of 16 - ws4, ws5, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws25, ws26 | 3 - ws3, ws14, ws27 | 12 - ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws24, ws28, ws29, ws30 |
| 2026-09-17 02:27:55 | 2026-09-17 01:52:05 SHORT | 4 of 28 - ws3, ws4, ws5, ws6 | 4 of 4 - ws3, ws4, ws5, ws6 | 0 - none | 24 - ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-17 03:14:55 | 2026-09-17 02:28:05 LONG | 7 of 28 - ws3, ws4, ws5, ws6, ws25, ws29, ws30 | 6 of 7 - ws3, ws4, ws5, ws6, ws29, ws30 | 1 - ws25 | 21 - ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws26, ws27, ws28 |
| 2026-09-17 18:49:40 | 2026-09-17 17:10:05 SHORT | 6 of 28 - ws3, ws4, ws5, ws6, ws7, ws9 | 2 of 6 - ws7, ws9 | 4 - ws3, ws4, ws5, ws6 | 22 - ws8, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-17 19:23:30 | 2026-09-17 17:10:05 SHORT | 9 of 28 - ws3, ws4, ws5, ws6, ws7, ws9, ws11, ws13, ws15 | 6 of 9 - ws3, ws4, ws5, ws6, ws9, ws15 | 3 - ws7, ws11, ws13 | 19 - ws8, ws10, ws12, ws14, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |

| the roll-up over 33 ws10x-cadences | value |
|---|---|
| eligible lines, every time | 28 |
| population, smallest .. largest | 2 .. 18 |
| population, mean | 7.7 |
| contributed, smallest .. largest | 1 .. 15 |
| contributed, mean | 5.9 |

| the line | times in the population | times it contributed |
|---|---|---|
| ws3 | 32 of 33 | 22 of 33 |
| ws4 | 30 of 33 | 25 of 33 |
| ws5 | 29 of 33 | 25 of 33 |
| ws6 | 24 of 33 | 21 of 33 |
| ws7 | 18 of 33 | 16 of 33 |
| ws8 | 15 of 33 | 13 of 33 |
| ws9 | 12 of 33 | 10 of 33 |
| ws10 | 6 of 33 | 5 of 33 |
| ws11 | 7 of 33 | 5 of 33 |
| ws12 | 5 of 33 | 4 of 33 |
| ws13 | 5 of 33 | 2 of 33 |
| ws14 | 7 of 33 | 5 of 33 |
| ws15 | 6 of 33 | 6 of 33 |
| ws16 | 4 of 33 | 3 of 33 |
| ws17 | 5 of 33 | 2 of 33 |
| ws18 | 3 of 33 | 3 of 33 |
| ws19 | 4 of 33 | 2 of 33 |
| ws20 | 4 of 33 | 3 of 33 |
| ws21 | 5 of 33 | 3 of 33 |
| ws22 | 3 of 33 | 3 of 33 |
| ws23 | 4 of 33 | 3 of 33 |
| ws24 | 4 of 33 | 3 of 33 |
| ws25 | 6 of 33 | 3 of 33 |
| ws26 | 4 of 33 | 2 of 33 |
| ws27 | 3 of 33 | 0 of 33 |
| ws28 | 2 of 33 | 0 of 33 |
| ws29 | 4 of 33 | 3 of 33 |
| ws30 | 3 of 33 | 2 of 33 |

## the legs | every number carries the FDM_MAE_CAP 1.10% stop

| the open | the trade | the rev-trade signal | the exit | the exit kind | held min | MAE% | MFE% | realised% |
|---|---|---|---|---|---|---|---|---|
| 2026-09-15 00:41:05 | SHORT | 2026-09-15 01:21:55 | 2026-09-15 01:22:00 | rev-trade | 40.9 | 0.076 | 0.872 | +0.533 |
| 2026-09-15 01:22:05 | LONG | 2026-09-15 02:48:55 | 2026-09-15 02:49:00 | rev-trade | 86.9 | 0.550 | 0.209 | -0.258 |
| 2026-09-15 02:49:05 | SHORT | 2026-09-15 04:41:00 | 2026-09-15 04:41:05 | rev-trade | 112.0 | 0.405 | 1.117 | +0.754 |
| 2026-09-15 04:41:10 | LONG | 2026-09-15 06:12:10 | 2026-09-15 06:12:15 | rev-trade | 91.1 | 0.816 | 0.415 | -0.169 |
| 2026-09-15 06:12:20 | SHORT | 2026-09-15 07:19:00 | 2026-09-15 07:19:05 | rev-trade | 66.8 | 0.197 | 1.085 | +0.296 |
| 2026-09-15 07:19:10 | LONG | 2026-09-15 09:12:45 | 2026-09-15 09:12:50 | rev-trade | 113.7 | 0.784 | 0.671 | +0.445 |
| 2026-09-15 09:12:55 | SHORT | 2026-09-15 11:52:50 | 2026-09-15 11:52:55 | rev-trade | 160.0 | 0.647 | 0.985 | +0.696 |
| 2026-09-15 11:53:00 | LONG | 2026-09-15 13:24:00 | 2026-09-15 13:24:05 | rev-trade | 91.1 | 0.050 | 1.834 | +1.126 |
| 2026-09-15 13:24:10 | SHORT | 2026-09-15 13:56:00 | 2026-09-15 13:56:05 | rev-trade | 31.9 | 0.105 | 1.961 | +0.735 |
| 2026-09-15 13:56:10 | LONG | - | 2026-09-15 14:35:15 | STOP at 1.10% | 39.1 | 1.100 | 0.635 | -1.100 |
| 2026-09-15 14:55:05 | LONG | 2026-09-15 18:01:15 | 2026-09-15 18:01:20 | rev-trade | 186.2 | 0.354 | 3.460 | +2.629 |
| 2026-09-15 18:01:25 | SHORT | 2026-09-15 18:51:55 | 2026-09-15 18:52:00 | rev-trade | 50.6 | 0.535 | 8.247 | +5.620 |
| 2026-09-15 18:52:05 | LONG | 2026-09-15 21:02:25 | 2026-09-15 21:02:30 | rev-trade | 130.4 | 0.380 | 2.781 | +1.901 |
| 2026-09-15 21:02:35 | SHORT | 2026-09-15 22:12:10 | 2026-09-15 22:12:15 | rev-trade | 69.7 | 0.680 | 1.463 | +1.141 |
| 2026-09-15 22:12:20 | LONG | 2026-09-15 23:31:55 | 2026-09-15 23:32:00 | rev-trade | 79.7 | 0.821 | 3.477 | +2.737 |
| 2026-09-15 23:32:05 | SHORT | 2026-09-16 01:12:20 | 2026-09-16 01:12:25 | rev-trade | 100.3 | 0.317 | 1.795 | +1.434 |
| 2026-09-16 01:12:30 | LONG | - | 2026-09-16 01:40:30 | STOP at 1.10% | 28.0 | 1.100 | 0.256 | -1.100 |
| 2026-09-16 01:46:05 | LONG | 2026-09-16 02:51:55 | 2026-09-16 02:52:00 | rev-trade | 65.9 | 0.871 | 1.099 | +0.738 |
| 2026-09-16 02:52:05 | SHORT | 2026-09-16 05:23:10 | 2026-09-16 05:23:15 | rev-trade | 151.2 | 0.967 | 0.557 | -0.146 |
| 2026-09-16 05:23:20 | LONG | 2026-09-16 05:53:30 | 2026-09-16 05:53:35 | rev-trade | 30.2 | 0.271 | 0.285 | -0.241 |
| 2026-09-16 05:53:40 | SHORT | 2026-09-16 06:41:00 | 2026-09-16 06:41:05 | rev-trade | 47.4 | 0.491 | 0.418 | +0.117 |
| 2026-09-16 06:41:10 | LONG | 2026-09-16 07:07:00 | 2026-09-16 07:07:05 | rev-trade | 25.9 | 0.066 | 0.807 | +0.499 |
| 2026-09-16 07:07:10 | SHORT | 2026-09-16 08:18:30 | 2026-09-16 08:18:35 | rev-trade | 71.4 | 0.066 | 1.315 | +0.804 |
| 2026-09-16 08:18:40 | LONG | 2026-09-16 10:54:00 | 2026-09-16 10:54:05 | rev-trade | 155.4 | 0.243 | 1.347 | +0.641 |
| 2026-09-16 10:54:10 | SHORT | 2026-09-16 12:51:05 | 2026-09-16 12:51:10 | rev-trade | 117.0 | 1.017 | 0.812 | +0.358 |
| 2026-09-16 12:51:15 | LONG | - | 2026-09-16 13:10:30 | STOP at 1.10% | 19.2 | 1.100 | 0.088 | -1.100 |
| 2026-09-16 13:52:05 | SHORT | 2026-09-16 14:26:40 | 2026-09-16 14:26:45 | rev-trade | 34.7 | 0.015 | 1.791 | +1.192 |
| 2026-09-16 14:26:50 | LONG | - | 2026-09-16 15:29:40 | STOP at 1.10% | 62.8 | 1.100 | 0.318 | -1.100 |
| 2026-09-16 15:35:05 | LONG | - | 2026-09-16 17:42:50 | STOP at 1.10% | 127.8 | 1.100 | 1.059 | -1.100 |
| 2026-09-16 17:54:05 | LONG | 2026-09-16 18:23:10 | 2026-09-16 18:23:15 | rev-trade | 29.2 | 0.293 | 4.672 | +2.358 |
| 2026-09-16 18:23:20 | SHORT | - | 2026-09-16 18:43:05 | STOP at 1.10% | 19.8 | 1.100 | 2.580 | -1.100 |
| 2026-09-16 21:45:05 | LONG | - | 2026-09-16 22:51:40 | STOP at 1.10% | 66.6 | 1.100 | 0.706 | -1.100 |
| 2026-09-16 22:57:05 | LONG | 2026-09-17 00:06:05 | 2026-09-17 00:06:10 | rev-trade | 69.1 | 0.409 | 2.797 | +2.165 |
| 2026-09-17 00:06:15 | SHORT | 2026-09-17 01:08:35 | 2026-09-17 01:08:40 | rev-trade | 62.4 | 0.954 | 0.218 | -0.444 |
| 2026-09-17 01:08:45 | LONG | 2026-09-17 01:51:55 | 2026-09-17 01:52:00 | rev-trade | 43.2 | 0.377 | 1.631 | +1.182 |
| 2026-09-17 01:52:05 | SHORT | 2026-09-17 02:27:55 | 2026-09-17 02:28:00 | rev-trade | 35.9 | 0.029 | 1.613 | +1.011 |
| 2026-09-17 02:28:05 | LONG | 2026-09-17 03:14:55 | 2026-09-17 03:15:00 | rev-trade | 46.9 | 0.311 | 1.317 | +0.999 |
| 2026-09-17 03:15:05 | SHORT | - | 2026-09-17 03:29:25 | STOP at 1.10% | 14.3 | 1.100 | 0.115 | -1.100 |
| 2026-09-17 03:40:05 | SHORT | - | 2026-09-17 03:57:15 | STOP at 1.10% | 17.2 | 1.100 | 0.071 | -1.100 |
| 2026-09-17 05:33:05 | SHORT | - | 2026-09-17 06:08:35 | STOP at 1.10% | 35.5 | 1.100 | 0.098 | -1.100 |
| 2026-09-17 06:43:05 | SHORT | - | 2026-09-17 08:55:10 | STOP at 1.10% | 132.1 | 1.100 | 0.539 | -1.100 |
| 2026-09-17 09:45:05 | LONG | - | 2026-09-17 10:16:05 | STOP at 1.10% | 31.0 | 1.100 | 0.233 | -1.100 |
| 2026-09-17 11:47:05 | LONG | 2026-09-17 12:03:00 | 2026-09-17 12:03:05 | rev-trade | 16.0 | 0.208 | 1.010 | +0.678 |
| 2026-09-17 12:03:10 | SHORT | - | 2026-09-17 12:26:35 | STOP at 1.10% | 23.4 | 1.100 | 0.213 | -1.100 |
| 2026-09-17 13:15:05 | LONG | - | 2026-09-17 13:40:05 | STOP at 1.10% | 25.0 | 1.100 | 0.810 | -1.100 |
| 2026-09-17 13:43:05 | LONG | - | 2026-09-17 15:05:50 | STOP at 1.10% | 82.8 | 1.100 | 2.564 | -1.100 |
| 2026-09-17 15:47:05 | SHORT | - | 2026-09-17 17:03:15 | STOP at 1.10% | 76.2 | 1.100 | 0.229 | -1.100 |
| 2026-09-17 17:10:05 | SHORT | 2026-09-17 19:23:30 | 2026-09-17 19:23:35 | rev-trade | 133.5 | 0.885 | 0.748 | +0.474 |
| 2026-09-17 19:23:40 | LONG | - | 2026-09-17 22:18:25 | STOP at 1.10% | 174.8 | 1.100 | 0.607 | -1.100 |
| 2026-09-17 22:51:05 | SHORT | - | 2026-09-17 23:59:55 | no rev-trade before the walk's end | 68.8 | 0.918 | 0.311 | -0.690 |

| the aggregate | value |
|---|---|
| legs | 50 |
| stopped | 17 |
| gross % | +12.615 |
| drag % | -9.875 (0.1975% round trip x 50 legs) |
| net % | +2.740 |
| MAE % total | 33.807 |
| MFE % total | 64.241 |
| MFE captured | 19.6% of MFE |
| held min, shortest .. longest | 14.3 .. 186.2 |

## each day's contribution | a leg counts on the day it OPENED

| the day | legs | stopped | gross %% | drag %% | net %% | MAE %% | MFE %% | MFE captured | rescued cadences |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-15 | 16 | 1 | +18.523 | -3.160 | +15.363 | 7.818 | 31.007 | 59.7% | 4 |
| 2026-09-16 | 17 | 6 | +1.883 | -3.357 | -1.474 | 11.307 | 20.908 | 9.0% | 2 |
| 2026-09-17 | 17 | 10 | -7.791 | -3.357 | -11.149 | 14.682 | 12.327 | -63.2% | 1 |

## his trade-setup table | jig.towards_away on EMERGING values, exact gap, no tolerance
# `towards` means the line is AT its own rolling target-side extremum since the anchor
# `away` means the gap from that extremum is positive - FOR A SHORT, value minus the
# running minimum; FOR A LONG, the running maximum minus value
# the anchor is the incoming trade's open, or the re-entry window's open
# ex-20/80 stays on the chart-matched read, his standing rule for a fence

| the signal bar | the setup | the incoming trade | the outgoing trade | the outgoing realised %% | the anchor | towards the incoming way, ws1-ws30 | its longest run | ex-20/80 the incoming way, ws1-ws30 | its longest run | towards the incoming way, ws25-ws30 | ex-20/80 the incoming way, ws25-ws30 | towards the outgoing way, ws1-ws30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-15 01:21:55 | incoming trade based | SHORT | LONG | -0.258 | 2026-09-15 00:41:05 | 3 of 30 | 2, ws27-ws28 | 13 of 30 | 9, ws22-ws30 | 3 of 6 | 6 of 6 | 0 of 30 |
| 2026-09-15 04:41:00 | incoming trade based | SHORT | LONG | -0.169 | 2026-09-15 02:49:05 | 0 of 30 | 0, ws1-ws1 | 1 of 30 | 1, ws2-ws2 | 0 of 6 | 0 of 6 | 2 of 30 |
| 2026-09-15 13:56:00 | incoming trade based | SHORT | LONG | -1.100 | 2026-09-15 13:24:10 | 1 of 30 | 1, ws11-ws11 | 3 of 30 | 2, ws5-ws6 | 0 of 6 | 0 of 6 | 4 of 30 |
| 2026-09-16 01:12:20 | incoming trade based | SHORT | LONG | -1.100 | 2026-09-15 23:32:05 | 9 of 30 | 2, ws15-ws16 | 10 of 30 | 10, ws5-ws14 | 1 of 6 | 0 of 6 | 0 of 30 |
| 2026-09-16 02:51:55 | incoming trade based | LONG | SHORT | -0.146 | 2026-09-16 01:46:05 | 2 of 30 | 1, ws11-ws11 | 5 of 30 | 5, ws5-ws9 | 0 of 6 | 0 of 6 | 0 of 30 |
| 2026-09-16 05:23:10 | incoming trade based | SHORT | LONG | -0.241 | 2026-09-16 02:52:05 | 0 of 30 | 0, ws1-ws1 | 1 of 30 | 1, ws8-ws8 | 0 of 6 | 0 of 6 | 0 of 30 |
| 2026-09-16 12:51:05 | incoming trade based | SHORT | LONG | -1.100 | 2026-09-16 10:54:10 | 6 of 30 | 3, ws27-ws29 | 1 of 30 | 1, ws6-ws6 | 4 of 6 | 0 of 6 | 1 of 30 |
| 2026-09-16 14:26:40 | incoming trade based | SHORT | LONG | -1.100 | 2026-09-16 13:52:05 | 5 of 30 | 2, ws25-ws26 | 6 of 30 | 3, ws3-ws5 | 4 of 6 | 0 of 6 | 0 of 30 |
| 2026-09-16 15:35:00 | re-entry based | none - a re-entry | LONG | -1.100 | 2026-09-16 15:29:00 | 11 of 30 | 5, ws23-ws27 | 0 of 30 | 0, ws1-ws1 | 3 of 6 | 0 of 6 | 11 of 30 |
| 2026-09-16 18:23:10 | incoming trade based | LONG | SHORT | -1.100 | 2026-09-16 17:54:05 | 3 of 30 | 2, ws23-ws24 | 1 of 30 | 1, ws4-ws4 | 1 of 6 | 0 of 6 | 1 of 30 |
| 2026-09-16 21:45:00 | re-entry based | none - a re-entry | LONG | -1.100 | 2026-09-16 21:39:00 | 11 of 30 | 4, ws16-ws19 | 1 of 30 | 1, ws27-ws27 | 1 of 6 | 1 of 6 | 11 of 30 |
| 2026-09-17 00:06:05 | incoming trade based | LONG | SHORT | -0.444 | 2026-09-16 22:57:05 | 0 of 30 | 0, ws1-ws1 | 3 of 30 | 3, ws7-ws9 | 0 of 6 | 0 of 6 | 0 of 30 |
| 2026-09-17 03:14:55 | incoming trade based | LONG | SHORT | -1.100 | 2026-09-17 02:28:05 | 0 of 30 | 0, ws1-ws1 | 2 of 30 | 1, ws6-ws6 | 0 of 6 | 1 of 6 | 0 of 30 |
| 2026-09-17 03:40:00 | re-entry based | none - a re-entry | SHORT | -1.100 | 2026-09-17 03:26:00 | 3 of 30 | 2, ws1-ws2 | 0 of 30 | 0, ws1-ws1 | 0 of 6 | 0 of 6 | 3 of 30 |
| 2026-09-17 05:33:00 | re-entry based | none - a re-entry | SHORT | -1.100 | 2026-09-17 05:26:00 | 4 of 30 | 1, ws1-ws1 | 0 of 30 | 0, ws1-ws1 | 2 of 6 | 0 of 6 | 4 of 30 |
| 2026-09-17 06:43:00 | re-entry based | none - a re-entry | SHORT | -1.100 | 2026-09-17 06:41:00 | 12 of 30 | 5, ws22-ws26 | 0 of 30 | 0, ws1-ws1 | 4 of 6 | 0 of 6 | 12 of 30 |
| 2026-09-17 09:45:00 | re-entry based | none - a re-entry | LONG | -1.100 | 2026-09-17 09:44:00 | 15 of 30 | 6, ws23-ws28 | 6 of 30 | 3, ws27-ws29 | 4 of 6 | 4 of 6 | 15 of 30 |
| 2026-09-17 12:03:00 | incoming trade based | LONG | SHORT | -1.100 | 2026-09-17 11:47:05 | 15 of 30 | 7, ws8-ws14 | 2 of 30 | 2, ws1-ws2 | 0 of 6 | 0 of 6 | 0 of 30 |
| 2026-09-17 13:15:00 | re-entry based | none - a re-entry | LONG | -1.100 | 2026-09-17 13:09:00 | 4 of 30 | 2, ws29-ws30 | 0 of 30 | 0, ws1-ws1 | 2 of 6 | 0 of 6 | 4 of 30 |
| 2026-09-17 13:43:00 | re-entry based | none - a re-entry | LONG | -1.100 | 2026-09-17 13:36:00 | 9 of 30 | 4, ws27-ws30 | 0 of 30 | 0, ws1-ws1 | 5 of 6 | 0 of 6 | 9 of 30 |
| 2026-09-17 15:47:00 | re-entry based | none - a re-entry | SHORT | -1.100 | 2026-09-17 15:37:00 | 2 of 30 | 2, ws1-ws2 | 1 of 30 | 1, ws25-ws25 | 0 of 6 | 1 of 6 | 2 of 30 |
| 2026-09-17 19:23:30 | incoming trade based | SHORT | LONG | -1.100 | 2026-09-17 17:10:05 | 8 of 30 | 3, ws21-ws23 | 3 of 30 | 1, ws11-ws11 | 2 of 6 | 0 of 6 | 0 of 30 |
| 2026-09-17 22:51:00 | re-entry based | none - a re-entry | SHORT | -0.690 | 2026-09-17 22:37:00 | 0 of 30 | 0, ws1-ws1 | 7 of 30 | 4, ws25-ws28 | 0 of 6 | 5 of 6 | 0 of 30 |
