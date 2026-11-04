# fdm2 | TAPE 1632960 bars, ends 2026-10-04 23:59:55 | RULED_OK True
# THE WALK RUNS 2026-08-07 00:00:00 .. 2026-08-07 23:59:55 - HIS one-day bound
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
| the re-entry signal bar | 2026-08-07 07:10:35 |
| the gcws30b window side | LOW oob |
| the trade | LONG |
| its target side | HIGH |
| the open price bar | 2026-08-07 07:10:40 - the router's "just OPEN", 1 bar |
| why | LOW window 06:53:00..06:55:00, 2.0 min, opened on both. ws5 reversed 07:10:35 at 17.07, ex-20/80. ws6r 43.41 fails the ex2080 gate. in-fence ws7..ws12: ws7, ws8, ws9, ws10, ws11, ws12. last to fire the ws5 reversal |

## leg 2026-08-07 07:10:40 | LONG | target side HIGH | fdm re-entry 2026-08-07 07:10:35

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 08:51:00 | REV-TRADE | cadence event, 0 of 27 lines ws4..ws30 printing ex-20/80 AND towards - his "if the answer is no, then rev-trade" || ws1b excursion 2026-08-07 08:43:00..2026-08-07 08:50:55, the nestle is ws1Mage 96.42 deeper than ws1r 87.26 at 2026-08-07 08:49:00 |

## leg 2026-08-07 08:51:10 | SHORT | target side LOW | rev-trade 2026-08-07 08:51:00

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 11:50:00 | WALK | cadence event, 1 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-08-07 11:54:45, the ws10x-cadence confirms 2026-08-07 11:56:40) || ws1b excursion 2026-08-07 11:45:00..2026-08-07 11:49:55, the nestle is ws1Mage 3.37 deeper than ws2r 14.37 at 2026-08-07 11:45:00 |
| 2026-08-07 11:56:40 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-08-07 11:54:45 and confirmed here. 7 of 8 reversed since 2026-08-07 11:50:00 (event) = 87.5% >= 50% at the ws10x-cadence bar itself |

## leg 2026-08-07 11:56:50 | LONG | target side HIGH | rev-trade 2026-08-07 11:56:40

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 12:15:00 | WALK | cadence event, 1 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-08-07 12:20:00, the ws10x-cadence confirms 2026-08-07 12:21:55) || ws1b excursion 2026-08-07 12:10:00..2026-08-07 12:14:55, the nestle is ws1Mage 103.85 deeper than ws2r 98.97 at 2026-08-07 12:10:00 |
| 2026-08-07 12:21:55 | NO ACTION | the ws10x-cadence - ws10x crossed to ib 2026-08-07 12:20:00 and confirmed here. 1 of 3 reversed since 2026-08-07 12:15:00 (event) = 33.3% < 40% - no branch, wait for the next cadence event |
| 2026-08-07 13:37:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the next cadence event is first (ws10x crosses to ib 2026-08-07 13:58:25, the ws10x-cadence confirms 2026-08-07 14:00:20) || ws1b excursion 2026-08-07 13:35:00..2026-08-07 13:36:55, the nestle is ws1Mage 89.87 deeper than ws3r 89.31 at 2026-08-07 13:35:00, ws3Mage RESCUED - the both window opened 2026-08-07 13:35:00, ws3r reached 90.10 and ws3Mage reached 63.10 |
| 2026-08-07 13:46:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-08-07 13:58:25, the ws10x-cadence confirms 2026-08-07 14:00:20) || ws1b excursion 2026-08-07 13:39:00..2026-08-07 13:45:55, the nestle is ws1Mage 95.36 deeper than ws3r 88.32 at 2026-08-07 13:40:00, ws3Mage RESCUED - the both window opened 2026-08-07 13:39:30, ws3r reached 90.13 and ws3Mage reached 67.24 |
| 2026-08-07 14:00:20 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-08-07 13:58:25 and confirmed here. 6 of 6 reversed since 2026-08-07 13:46:00 (event) = 100.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-08-07 14:00:30 | SHORT | target side LOW | rev-trade 2026-08-07 14:00:20

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 14:20:00 | WALK | cadence event, 1 of 27 lines printing ex-20/80 AND towards -> walk. the next cadence event is first (ws10x crosses to ws10Mage 2026-08-07 14:40:20, the ws10x-cadence confirms 2026-08-07 14:42:15) || ws1b excursion 2026-08-07 14:12:00..2026-08-07 14:19:55, the nestle is ws1Mage -3.25 deeper than ws2r 14.87 at 2026-08-07 14:12:00 |
| 2026-08-07 14:41:00 | REV-TRADE | cadence event, 0 of 27 lines ws4..ws30 printing ex-20/80 AND towards - his "if the answer is no, then rev-trade" || ws1b excursion 2026-08-07 14:40:00..2026-08-07 14:40:55, the nestle is ws1Mage -0.61 deeper than ws1r 6.87 at 2026-08-07 14:40:00 |

## leg 2026-08-07 14:41:10 | LONG | target side HIGH | rev-trade 2026-08-07 14:41:00

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 16:11:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10r 2026-08-07 16:16:55, the ws10x-cadence confirms 2026-08-07 16:18:50) || ws1b excursion 2026-08-07 16:07:00..2026-08-07 16:10:55, the nestle is ws1Mage 99.71 deeper than ws1r 97.33 at 2026-08-07 16:08:00, ws3Mage RESCUED - the both window opened 2026-08-07 15:32:30, ws3r reached 95.76 and ws3Mage reached 74.83 |
| 2026-08-07 16:18:50 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10r 2026-08-07 16:16:55 and confirmed here. 7 of 8 reversed since 2026-08-07 16:11:00 (event) = 87.5% >= 50% at the ws10x-cadence bar itself |

## leg 2026-08-07 16:19:00 | SHORT | target side LOW | rev-trade 2026-08-07 16:18:50

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 17:04:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the next cadence event is first (ws10x crosses to ib 2026-08-07 17:39:10, the ws10x-cadence confirms 2026-08-07 17:41:05) || ws1b excursion 2026-08-07 16:57:00..2026-08-07 17:03:55, the nestle is ws1Mage 8.71 deeper than ws1r 11.53 at 2026-08-07 16:58:00 |
| 2026-08-07 17:17:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-08-07 17:39:10, the ws10x-cadence confirms 2026-08-07 17:41:05) || ws1b excursion 2026-08-07 17:11:00..2026-08-07 17:16:55, the nestle is ws1Mage 7.88 deeper than ws1r 8.78 at 2026-08-07 17:16:00 |
| 2026-08-07 17:41:05 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-08-07 17:39:10 and confirmed here. 6 of 6 reversed since 2026-08-07 17:17:00 (event) = 100.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-08-07 17:41:15 | LONG | target side HIGH | rev-trade 2026-08-07 17:41:05

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 18:10:00 | WALK | cadence event, 1 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ib 2026-08-07 18:14:10, the ws10x-cadence confirms 2026-08-07 18:16:05) || ws1b excursion 2026-08-07 17:59:00..2026-08-07 18:09:55, the nestle is ws1Mage 95.56 deeper than ws1r 85.71 at 2026-08-07 18:00:00 |
| 2026-08-07 18:16:05 | REV-TRADE | the ws10x-cadence - ws10x crossed to ib 2026-08-07 18:14:10 and confirmed here. 2 of 2 reversed since 2026-08-07 18:10:00 (event) = 100.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-08-07 18:16:15 | SHORT | target side LOW | rev-trade 2026-08-07 18:16:05

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 18:42:00 | WALK | cadence event, 1 of 27 lines printing ex-20/80 AND towards -> walk. the next cadence event is first (ws10x crosses to ws10Mage 2026-08-07 18:54:55, the ws10x-cadence confirms 2026-08-07 18:56:50) || ws1b excursion 2026-08-07 18:41:00..2026-08-07 18:41:55, the nestle is ws1Mage -8.45 deeper than ws1r 10.08 at 2026-08-07 18:41:00, ws3Mage RESCUED - the both window opened 2026-08-07 18:41:00, ws3r reached 13.32 and ws3Mage reached 38.78 |
| 2026-08-07 18:46:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10Mage 2026-08-07 18:54:55, the ws10x-cadence confirms 2026-08-07 18:56:50) || ws1b excursion 2026-08-07 18:43:00..2026-08-07 18:45:55, the nestle is ws1Mage -1.10 deeper than ws3r 13.32 at 2026-08-07 18:43:00, ws3Mage RESCUED - the both window opened 2026-08-07 18:43:00, ws3r reached 11.36 and ws3Mage reached 30.63 |
| 2026-08-07 18:56:50 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10Mage 2026-08-07 18:54:55 and confirmed here. 3 of 3 reversed since 2026-08-07 18:46:00 (event) = 100.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-08-07 18:57:00 | LONG | target side HIGH | rev-trade 2026-08-07 18:56:50

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 19:05:00 | REV-TRADE | cadence event, 0 of 27 lines ws4..ws30 printing ex-20/80 AND towards - his "if the answer is no, then rev-trade" || ws1b excursion 2026-08-07 19:02:00..2026-08-07 19:04:55, the nestle is ws1Mage 106.04 deeper than ws1r 97.31 at 2026-08-07 19:02:00 |

## leg 2026-08-07 19:05:10 | SHORT | target side LOW | rev-trade 2026-08-07 19:05:00

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 19:05:10 | NO CADENCE EVENT | no cadence event on the LOW side from the open to 2026-08-07 23:59:55 |

## leg 2026-08-07 19:30:40 | SHORT | target side LOW | fdm re-entry 2026-08-07 19:30:35, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 20:12:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x crosses to ws10Mage 2026-08-07 20:43:25, the ws10x-cadence confirms 2026-08-07 20:45:20) || ws1b excursion 2026-08-07 20:00:00..2026-08-07 20:11:55, the nestle is ws1Mage -7.95 deeper than ws1r 14.29 at 2026-08-07 20:05:00 |
| 2026-08-07 20:45:20 | REV-TRADE | the ws10x-cadence - ws10x crossed to ws10Mage 2026-08-07 20:43:25 and confirmed here. 7 of 7 reversed since 2026-08-07 20:12:00 (event) = 100.0% >= 50% at the ws10x-cadence bar itself |

## leg 2026-08-07 20:45:30 | LONG | target side HIGH | rev-trade 2026-08-07 20:45:20

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 20:45:30 | NO CADENCE EVENT | no cadence event on the HIGH side from the open to 2026-08-07 23:59:55 |

## leg 2026-08-07 23:24:40 | SHORT | target side LOW | fdm re-entry 2026-08-07 23:24:35, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 23:24:40 | NO CADENCE EVENT | no cadence event on the LOW side from the open to 2026-08-07 23:59:55 |

## the 28 eligible lines at every ws10x-cadence | ws3..ws30

| the ws10x-cadence | the trade it was deciding | ex-20/80 at least once | contributed a reversal | silent - ex-fence but no reversal | never ex-fence |
|---|---|---|---|---|---|
| 2026-08-07 11:56:40 | 2026-08-07 08:51:10 SHORT | 8 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10 | 7 of 8 - ws3, ws4, ws5, ws6, ws7, ws8, ws9 | 1 - ws10 | 20 - ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-08-07 12:21:55 | 2026-08-07 11:56:50 LONG | 3 of 28 - ws3, ws4, ws30 | 1 of 3 - ws4 | 2 - ws3, ws30 | 25 - ws5, ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29 |
| 2026-08-07 14:00:20 | 2026-08-07 11:56:50 LONG | 6 of 28 - ws3, ws4, ws5, ws6, ws7, ws30 | 6 of 6 - ws3, ws4, ws5, ws6, ws7, ws30 | 0 - none | 22 - ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29 |
| 2026-08-07 16:18:50 | 2026-08-07 14:41:10 LONG | 8 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10 | 7 of 8 - ws3, ws4, ws6, ws7, ws8, ws9, ws10 | 1 - ws5 | 20 - ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-08-07 17:41:05 | 2026-08-07 16:19:00 SHORT | 6 of 28 - ws3, ws6, ws7, ws8, ws9, ws11 | 6 of 6 - ws3, ws6, ws7, ws8, ws9, ws11 | 0 - none | 22 - ws4, ws5, ws10, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-08-07 18:16:05 | 2026-08-07 17:41:15 LONG | 2 of 28 - ws4, ws5 | 2 of 2 - ws4, ws5 | 0 - none | 26 - ws3, ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-08-07 18:56:50 | 2026-08-07 18:16:15 SHORT | 3 of 28 - ws3, ws4, ws5 | 3 of 3 - ws3, ws4, ws5 | 0 - none | 25 - ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-08-07 20:45:20 | 2026-08-07 19:30:40 SHORT | 7 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws10 | 7 of 7 - ws3, ws4, ws5, ws6, ws7, ws8, ws10 | 0 - none | 21 - ws9, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |

| the roll-up over 8 ws10x-cadences | value |
|---|---|
| eligible lines, every time | 28 |
| population, smallest .. largest | 2 .. 8 |
| population, mean | 5.4 |
| contributed, smallest .. largest | 1 .. 7 |
| contributed, mean | 4.9 |

| the line | times in the population | times it contributed |
|---|---|---|
| ws3 | 7 of 8 | 6 of 8 |
| ws4 | 7 of 8 | 7 of 8 |
| ws5 | 6 of 8 | 5 of 8 |
| ws6 | 5 of 8 | 5 of 8 |
| ws7 | 5 of 8 | 5 of 8 |
| ws8 | 4 of 8 | 4 of 8 |
| ws9 | 3 of 8 | 3 of 8 |
| ws10 | 3 of 8 | 2 of 8 |
| ws11 | 1 of 8 | 1 of 8 |
| ws12 | 0 of 8 | 0 of 8 |
| ws13 | 0 of 8 | 0 of 8 |
| ws14 | 0 of 8 | 0 of 8 |
| ws15 | 0 of 8 | 0 of 8 |
| ws16 | 0 of 8 | 0 of 8 |
| ws17 | 0 of 8 | 0 of 8 |
| ws18 | 0 of 8 | 0 of 8 |
| ws19 | 0 of 8 | 0 of 8 |
| ws20 | 0 of 8 | 0 of 8 |
| ws21 | 0 of 8 | 0 of 8 |
| ws22 | 0 of 8 | 0 of 8 |
| ws23 | 0 of 8 | 0 of 8 |
| ws24 | 0 of 8 | 0 of 8 |
| ws25 | 0 of 8 | 0 of 8 |
| ws26 | 0 of 8 | 0 of 8 |
| ws27 | 0 of 8 | 0 of 8 |
| ws28 | 0 of 8 | 0 of 8 |
| ws29 | 0 of 8 | 0 of 8 |
| ws30 | 2 of 8 | 1 of 8 |

## the legs | every number carries the FDM_MAE_CAP 1.10% stop

| the open | the trade | the rev-trade signal | the exit | the exit kind | held min | MAE% | MFE% | realised% |
|---|---|---|---|---|---|---|---|---|
| 2026-08-07 07:10:40 | LONG | 2026-08-07 08:51:00 | 2026-08-07 08:51:05 | rev-trade | 100.4 | 0.506 | 0.257 | -0.047 |
| 2026-08-07 08:51:10 | SHORT | 2026-08-07 11:56:40 | 2026-08-07 11:56:45 | rev-trade | 185.6 | 0.795 | 0.179 | -0.179 |
| 2026-08-07 11:56:50 | LONG | 2026-08-07 14:00:20 | 2026-08-07 14:00:25 | rev-trade | 123.6 | 0.692 | 1.112 | +0.086 |
| 2026-08-07 14:00:30 | SHORT | 2026-08-07 14:41:00 | 2026-08-07 14:41:05 | rev-trade | 40.6 | 0.054 | 1.096 | +0.777 |
| 2026-08-07 14:41:10 | LONG | 2026-08-07 16:18:50 | 2026-08-07 16:18:55 | rev-trade | 97.8 | 1.058 | 0.541 | +0.157 |
| 2026-08-07 16:19:00 | SHORT | 2026-08-07 17:41:05 | 2026-08-07 17:41:10 | rev-trade | 82.2 | 0.454 | 0.868 | +0.266 |
| 2026-08-07 17:41:15 | LONG | 2026-08-07 18:16:05 | 2026-08-07 18:16:10 | rev-trade | 34.9 | 0.353 | 0.525 | +0.173 |
| 2026-08-07 18:16:15 | SHORT | 2026-08-07 18:56:50 | 2026-08-07 18:56:55 | rev-trade | 40.7 | 0.125 | 0.313 | -0.031 |
| 2026-08-07 18:57:00 | LONG | 2026-08-07 19:05:00 | 2026-08-07 19:05:05 | rev-trade | 8.1 | 0.000 | 0.345 | +0.172 |
| 2026-08-07 19:05:10 | SHORT | - | 2026-08-07 19:17:00 | STOP at 1.10% | 11.8 | 1.100 | 0.008 | -1.100 |
| 2026-08-07 19:30:40 | SHORT | 2026-08-07 20:45:20 | 2026-08-07 20:45:25 | rev-trade | 74.8 | 0.187 | 2.178 | +1.493 |
| 2026-08-07 20:45:30 | LONG | - | 2026-08-07 21:59:05 | STOP at 1.10% | 73.6 | 1.100 | 0.174 | -1.100 |
| 2026-08-07 23:24:40 | SHORT | - | 2026-08-07 23:59:55 | no rev-trade before the walk's end | 35.2 | 0.302 | 0.429 | -0.207 |

| the aggregate | value |
|---|---|
| legs | 13 |
| stopped | 2 |
| gross % | +0.460 |
| drag % | -2.567 (0.1975% round trip x 13 legs) |
| net % | -2.108 |
| MAE % total | 6.726 |
| MFE % total | 8.024 |
| MFE captured | 5.7% of MFE |
| held min, shortest .. longest | 8.1 .. 185.6 |

## the fdm2-wsxcad-director | one row per cadence event | FDM_XCAD_ON 0
# the candidate is `fdm-conf-xcross-candidate`, HIS knob name: the highest line
# printing away while the 2 lines above it print towards AND ex-20/80
# FDM_XCAD_RULE B, FDM_XCAD_EXF 0, FDM_XCAD_FRM confirm, FDM_XCAD_TAG_AT event
# the seam read is the next ws1 seam + 15s = 3 bars, then a 10.0 min walk that truncates on the first pass
# the reversal gate spans the cadence window open to the confirmed cross bar, FDM_XCAD_REV_FROM window
# no candidate means FDM_XCAD_NONE rev-trade
# every value is closed-prev at the cadence event and EMERGING at the seam re-read

| the cadence event | the incoming trade | its own side | the cadence window opened | the candidate | the lines above it | ex-20/80 at the event | towards at the event | the x cross | the x confirm | which target | the seam+15s bar | the seam verdict | the rev-trade bar | why | the ws10 race confirm, for comparison |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-07 08:51:00 | 2026-08-07 07:10:40 LONG | HIGH, upwards | 2026-08-07 08:43:00 | none | - | 0 of 30 | 3 of 30 | - | - | - | - | - | rev-trade at the event, FDM_XCAD_NONE | no line is away with its 2 lines above towards | - |
| 2026-08-07 11:50:00 | 2026-08-07 08:51:10 SHORT | LOW, downwards | 2026-08-07 11:45:00 | none | - | 2 of 30 | 2 of 30 | - | - | - | - | - | rev-trade at the event, FDM_XCAD_NONE | no line is away with its 2 lines above towards | 2026-08-07 11:56:40 |
| 2026-08-07 12:15:00 | 2026-08-07 11:56:50 LONG | HIGH, upwards | 2026-08-07 12:10:00 | none | - | 3 of 30 | 22 of 30 | - | - | - | - | - | rev-trade at the event, FDM_XCAD_NONE | no line is away with its 2 lines above towards | 2026-08-07 12:21:55 |
| 2026-08-07 13:37:00 | 2026-08-07 11:56:50 LONG | HIGH, upwards | 2026-08-07 13:35:00 | none | - | 4 of 30 | 2 of 30 | - | - | - | - | - | rev-trade at the event, FDM_XCAD_NONE | no line is away with its 2 lines above towards | 2026-08-07 14:00:20 |
| 2026-08-07 13:46:00 | 2026-08-07 11:56:50 LONG | HIGH, upwards | 2026-08-07 13:39:00 | none | - | 4 of 30 | 3 of 30 | - | - | - | - | - | rev-trade at the event, FDM_XCAD_NONE | no line is away with its 2 lines above towards | 2026-08-07 14:00:20 |
| 2026-08-07 14:20:00 | 2026-08-07 14:00:30 SHORT | LOW, downwards | 2026-08-07 14:12:00 | none | - | 2 of 30 | 22 of 30 | - | - | - | - | - | rev-trade at the event, FDM_XCAD_NONE | no line is away with its 2 lines above towards | - |
| 2026-08-07 14:41:00 | 2026-08-07 14:00:30 SHORT | LOW, downwards | 2026-08-07 14:40:00 | none | - | 1 of 30 | 19 of 30 | - | - | - | - | - | rev-trade at the event, FDM_XCAD_NONE | no line is away with its 2 lines above towards | - |
| 2026-08-07 16:11:00 | 2026-08-07 14:41:10 LONG | HIGH, upwards | 2026-08-07 16:07:00 | ws8r | ws9, ws10 | 4 of 30 | 16 of 30 | 2026-08-07 16:15:35 | 2026-08-07 16:17:30 | ws8r | - | held | - | the seam+15s bar 2026-08-07 16:18:10 failed (ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws21, ws22, ws23, ws28, ws30 of the 16 tagged lines are not away yet) and the 10.0 min walk to 2026-08-07 16:18:55 never passed | 2026-08-07 16:18:50 |
| 2026-08-07 17:04:00 | 2026-08-07 16:19:00 SHORT | LOW, downwards | 2026-08-07 16:57:00 | none | - | 2 of 30 | 17 of 30 | - | - | - | - | - | rev-trade at the event, FDM_XCAD_NONE | no line is away with its 2 lines above towards | 2026-08-07 17:41:05 |
| 2026-08-07 17:17:00 | 2026-08-07 16:19:00 SHORT | LOW, downwards | 2026-08-07 17:11:00 | ws7r | ws8, ws9 | 3 of 30 | 10 of 30 | 2026-08-07 17:17:55 | 2026-08-07 17:19:50 | ws7r | - | held | - | the seam+15s bar 2026-08-07 17:20:10 failed (ws10, ws13, ws20, ws21, ws22, ws23 of the 10 tagged lines are not away yet) and the 10.0 min walk to 2026-08-07 17:30:10 never passed | 2026-08-07 17:41:05 |
| 2026-08-07 18:10:00 | 2026-08-07 17:41:15 LONG | HIGH, upwards | 2026-08-07 17:59:00 | none | - | 2 of 30 | 21 of 30 | - | - | - | - | - | rev-trade at the event, FDM_XCAD_NONE | no line is away with its 2 lines above towards | 2026-08-07 18:16:05 |
| 2026-08-07 18:42:00 | 2026-08-07 18:16:15 SHORT | LOW, downwards | 2026-08-07 18:41:00 | ws2r | ws3, ws4 | 2 of 30 | 24 of 30 | 2026-08-07 18:45:40 | 2026-08-07 18:47:35 | ws2r | - | held | - | the seam+15s bar 2026-08-07 18:48:10 failed (ws6, ws7, ws8, ws9, ws10, ws11, ws13, ws16, ws17, ws19, ws20, ws21, ws22, ws23, ws26, ws27, ws28, ws29, ws30 of the 24 tagged lines are not away yet) and the 10.0 min walk to 2026-08-07 18:56:55 never passed | 2026-08-07 18:56:50 |
| 2026-08-07 18:46:00 | 2026-08-07 18:16:15 SHORT | LOW, downwards | 2026-08-07 18:43:00 | ws2r | ws3, ws4 | 3 of 30 | 24 of 30 | 2026-08-07 18:47:00 | 2026-08-07 18:48:55 | ws2Mage | - | held | - | the seam+15s bar 2026-08-07 18:50:10 failed (ws6, ws7, ws8, ws9, ws11, ws13, ws21, ws23, ws25, ws27, ws28, ws29 of the 24 tagged lines are not away yet) and the 10.0 min walk to 2026-08-07 18:56:55 never passed | 2026-08-07 18:56:50 |
| 2026-08-07 19:05:00 | 2026-08-07 18:57:00 LONG | HIGH, upwards | 2026-08-07 19:02:00 | none | - | 1 of 30 | 27 of 30 | - | - | - | - | - | rev-trade at the event, FDM_XCAD_NONE | no line is away with its 2 lines above towards | - |
| 2026-08-07 20:12:00 | 2026-08-07 19:30:40 SHORT | LOW, downwards | 2026-08-07 20:00:00 | none | - | 4 of 30 | 19 of 30 | - | - | - | - | - | rev-trade at the event, FDM_XCAD_NONE | no line is away with its 2 lines above towards | 2026-08-07 20:45:20 |

| the director roll-up | value |
|---|---|
| legs walked | 13 |
| cadence events | 15 |
| events with a candidate | 4 |
| events with no candidate | 11 |
| events whose seam read or walk sent a rev-trade | 0 |
