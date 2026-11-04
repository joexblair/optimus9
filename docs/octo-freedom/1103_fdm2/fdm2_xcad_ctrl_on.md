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
| the re-entry signal bar | 2026-09-15 08:50:35 |
| the gcws30b window side | HIGH oob |
| the trade | SHORT |
| its target side | LOW |
| the open price bar | 2026-09-15 08:50:40 - the router's "just OPEN", 1 bar |
| why | HIGH window 08:40:00..08:41:00, 1.0 min, opened on both. ws5 reversed 08:50:35 at 82.07, ex-20/80. ws6r 77.75 fails the ex2080 gate. in-fence ws7..ws12: ws7, ws8, ws9, ws10, ws11, ws12. last to fire the ws5 reversal |

## leg 2026-09-15 08:50:40 | SHORT | target side LOW | fdm re-entry 2026-09-15 08:50:35

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 11:40:00 | WALK | cadence event, 6 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws11 (ws11r is the highest away line and ws12, ws13 are towards and ex-20/80). the ws11x-cadence is first (ws11x crosses to ws11r 2026-09-15 11:51:30, the ws11x-cadence confirms 2026-09-15 11:53:25) || ws1b excursion 2026-09-15 11:19:00..2026-09-15 11:39:55, the nestle is ws1Mage -1.68 deeper than ws3r 11.35 at 2026-09-15 11:24:00 |
| 2026-09-15 11:53:25 | SEAM | the director's seam read from 2026-09-15 11:53:25 - ws13 is the highest ex-20/80 towards line, so the 2 above it are ws14, ws15. the seam+15s bar 2026-09-15 11:54:10 failed (ws13 are ex-20/80 AND towards (tagged), so no rev-trade) and the 10.0 min walk to 2026-09-15 12:04:10 never passed |
| 2026-09-15 11:53:25 | REV-TRADE | the ws11x-cadence - ws11x crossed to ws11r 2026-09-15 11:51:30 and confirmed here. 12 of 13 reversed since 2026-09-15 11:40:00 (event) = 92.3% >= 50% at the race bar itself |

## leg 2026-09-15 11:53:35 | LONG | target side HIGH | rev-trade 2026-09-15 11:53:25

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 12:25:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws3 (ws3r is the highest away line and ws4, ws5 are towards and ex-20/80). the ws3x-cadence is first (ws3x crosses to ws3r 2026-09-15 12:27:45, the ws3x-cadence confirms 2026-09-15 12:29:40) || ws1b excursion 2026-09-15 12:12:00..2026-09-15 12:24:55, the nestle is ws1Mage 107.30 deeper than ws3r 99.38 at 2026-09-15 12:14:00 |
| 2026-09-15 12:29:40 | SEAM | the director's seam read from 2026-09-15 12:29:40 - ws6 is the highest ex-20/80 towards line, so the 2 above it are ws7, ws8. the seam+15s bar 2026-09-15 12:30:10 failed (ws7, ws8 of the 2 lines above are not away yet) and the 10.0 min walk to 2026-09-15 12:40:10 never passed |
| 2026-09-15 12:29:40 | NO ACTION | the ws3x-cadence - ws3x crossed to ws3r 2026-09-15 12:27:45 and confirmed here. 1 of 4 reversed since 2026-09-15 12:25:00 (event) = 25.0% < 40% - no branch, wait for the next cadence event |
| 2026-09-15 12:58:00 | REV-TRADE | the director found no candidate - no line is away with its 2 lines above towards. His "no candidates = rev-trade" || ws1b excursion 2026-09-15 12:53:00..2026-09-15 12:57:55, the nestle is ws1Mage 119.99 deeper than ws1r 100.00 at 2026-09-15 12:55:00 |

## leg 2026-09-15 12:58:10 | SHORT | target side LOW | rev-trade 2026-09-15 12:58:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 13:41:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws1 (ws1r is the highest away line and ws2, ws3 are towards and ex-20/80). the next cadence event is first (ws1x crosses to ws1Mage 2026-09-15 13:47:25, the ws1x-cadence confirms 2026-09-15 13:49:20) || ws1b excursion 2026-09-15 13:36:00..2026-09-15 13:40:55, the nestle is ws1Mage 0.24 deeper than ws3r 3.16 at 2026-09-15 13:36:00 |
| 2026-09-15 13:48:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws4 (ws4r is the highest away line and ws5, ws6 are towards and ex-20/80). the ws4x-cadence is first (ws4x crosses to ws4r 2026-09-15 13:51:05, the ws4x-cadence confirms 2026-09-15 13:53:00) || ws1b excursion 2026-09-15 13:42:00..2026-09-15 13:47:55, the nestle is ws2Mage 4.92 deeper than ws3r 8.04 at 2026-09-15 13:44:00 |
| 2026-09-15 13:53:00 | SEAM | the director's seam read from 2026-09-15 13:53:00 - ws6 is the highest ex-20/80 towards line, so the 2 above it are ws7, ws8. the seam+15s bar 2026-09-15 13:54:10 failed (ws7, ws8 of the 2 lines above are not away yet) and the 10.0 min walk to 2026-09-15 14:04:10 never passed |
| 2026-09-15 13:53:00 | NO ACTION | the ws4x-cadence - ws4x crossed to ws4r 2026-09-15 13:51:05 and confirmed here. 0 of 5 reversed since 2026-09-15 13:48:00 (event) = 0.0% < 40% - no branch, wait for the next cadence event |
| 2026-09-15 14:55:00 | WALK | cadence event, 4 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws3 (ws3r is the highest away line and ws4, ws5 are towards and ex-20/80). the ws3x-cadence is first (ws3x crosses to ws3r 2026-09-15 14:56:15, the ws3x-cadence confirms 2026-09-15 14:58:10) || ws1b excursion 2026-09-15 14:33:00..2026-09-15 14:54:55, the nestle is ws1Mage -13.37 deeper than ws1r 13.29 at 2026-09-15 14:33:00 |
| 2026-09-15 14:58:10 | SEAM | the director's seam read from 2026-09-15 14:58:10 - ws12 is the highest ex-20/80 towards line, so the 2 above it are ws13, ws14. the ws1 seam+15s bar 2026-09-15 14:59:10 - ws13, ws14 away and no ex-20/80 line towards (tagged) |
| 2026-09-15 14:59:10 | REV-TRADE | the director - the ws1 seam+15s bar 2026-09-15 14:59:10 - ws13, ws14 away and no ex-20/80 line towards (tagged) |

## leg 2026-09-15 14:59:20 | LONG | target side HIGH | rev-trade 2026-09-15 14:59:10

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 17:42:00 | REV-TRADE | the director found no candidate - no line is away with its 2 lines above towards. His "no candidates = rev-trade" || ws1b excursion 2026-09-15 17:32:00..2026-09-15 17:41:55, the nestle is ws1Mage 97.01 deeper than ws1r 85.53 at 2026-09-15 17:32:00 |

## leg 2026-09-15 17:42:10 | SHORT | target side LOW | rev-trade 2026-09-15 17:42:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 18:29:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws3 (ws3r is the highest away line and ws4, ws5 are towards and ex-20/80). the ws3x-cadence is first (ws3x crosses to ws3r 2026-09-15 18:30:45, the ws3x-cadence confirms 2026-09-15 18:32:40) || ws1b excursion 2026-09-15 18:17:00..2026-09-15 18:28:55, the nestle is ws1Mage -5.84 deeper than ws3r 4.31 at 2026-09-15 18:17:00, ws3Mage RESCUED - the both window opened 2026-09-15 18:17:00, ws3r reached 2.89 and ws3Mage reached 31.16 |
| 2026-09-15 18:32:40 | SEAM | the director's seam read from 2026-09-15 18:32:40 - ws5 is the highest ex-20/80 towards line, so the 2 above it are ws6, ws7. the ws1 seam+15s bar 2026-09-15 18:33:10 - ws6, ws7 away and no ex-20/80 line towards (tagged) |
| 2026-09-15 18:33:10 | REV-TRADE | the director - the ws1 seam+15s bar 2026-09-15 18:33:10 - ws6, ws7 away and no ex-20/80 line towards (tagged) |

## leg 2026-09-15 18:33:20 | LONG | target side HIGH | rev-trade 2026-09-15 18:33:10

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 18:33:20 | NO CADENCE EVENT | no cadence event on the HIGH side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-15 18:54:40 | LONG | target side HIGH | fdm re-entry 2026-09-15 18:54:35, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 21:00:00 | REV-TRADE | the director found no candidate - no line is away with its 2 lines above towards. His "no candidates = rev-trade" || ws1b excursion 2026-09-15 20:50:00..2026-09-15 20:59:55, the nestle is ws1Mage 115.86 deeper than ws2r 94.73 at 2026-09-15 20:50:00 |

## leg 2026-09-15 21:00:10 | SHORT | target side LOW | rev-trade 2026-09-15 21:00:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-15 22:03:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws4 (ws4r is the highest away line and ws5, ws6 are towards and ex-20/80). the ws4x-cadence is first (ws4x crosses to ws4Mage 2026-09-15 22:06:55, the ws4x-cadence confirms 2026-09-15 22:08:50) || ws1b excursion 2026-09-15 21:59:00..2026-09-15 22:02:55, the nestle is ws1Mage -4.31 deeper than ws1r 13.15 at 2026-09-15 21:59:00 |
| 2026-09-15 22:08:50 | SEAM | the director's seam read from 2026-09-15 22:08:50 - ws6 is the highest ex-20/80 towards line, so the 2 above it are ws7, ws8. the seam+15s bar 2026-09-15 22:09:10 failed (ws7, ws8 of the 2 lines above are not away yet) and the 10.0 min walk to 2026-09-15 22:19:10 never passed |
| 2026-09-15 22:08:50 | NO ACTION | the ws4x-cadence - ws4x crossed to ws4Mage 2026-09-15 22:06:55 and confirmed here. 1 of 5 reversed since 2026-09-15 22:03:00 (event) = 20.0% < 40% - no branch, wait for the next cadence event |

## leg 2026-09-16 00:36:40 | SHORT | target side LOW | fdm re-entry 2026-09-16 00:36:35, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 01:01:00 | WALK | cadence event, 9 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws4 (ws4r is the highest away line and ws5, ws6 are towards and ex-20/80). the ws4x-cadence is first (ws4x crosses to ws4r 2026-09-16 01:10:15, the ws4x-cadence confirms 2026-09-16 01:12:10) || ws1b excursion 2026-09-16 00:50:00..2026-09-16 01:00:55, the nestle is ws1Mage -3.35 deeper than ws3r 12.25 at 2026-09-16 00:51:00 |
| 2026-09-16 01:12:10 | SEAM | the director's seam read from 2026-09-16 01:12:10 - ws13 is the highest ex-20/80 towards line, so the 2 above it are ws14, ws15. the seam+15s bar 2026-09-16 01:13:10 failed (ws14, ws15 of the 2 lines above are not away yet) and the 10.0 min walk to 2026-09-16 01:23:10 never passed |
| 2026-09-16 01:12:10 | REV-TRADE | the ws4x-cadence - ws4x crossed to ws4r 2026-09-16 01:10:15 and confirmed here. 9 of 12 reversed since 2026-09-16 01:01:00 (event) = 75.0% >= 50% at the race bar itself |

## leg 2026-09-16 01:12:20 | LONG | target side HIGH | rev-trade 2026-09-16 01:12:10

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 01:12:20 | NO CADENCE EVENT | no cadence event on the HIGH side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-16 09:18:40 | SHORT | target side LOW | fdm re-entry 2026-09-16 09:18:35, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 12:34:00 | REV-TRADE | the director found no candidate - no line is away with its 2 lines above towards. His "no candidates = rev-trade" || ws1b excursion 2026-09-16 12:26:00..2026-09-16 12:33:55, the nestle is ws1Mage 8.47 deeper than ws3r 14.37 at 2026-09-16 12:30:00 |

## leg 2026-09-16 12:34:10 | LONG | target side HIGH | rev-trade 2026-09-16 12:34:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 12:34:10 | NO CADENCE EVENT | no cadence event on the HIGH side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-16 18:00:40 | LONG | target side HIGH | fdm re-entry 2026-09-16 18:00:35, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 18:15:00 | REV-TRADE | the director found no candidate - no line is away with its 2 lines above towards. His "no candidates = rev-trade" || ws1b excursion 2026-09-16 18:04:00..2026-09-16 18:14:55, the nestle is ws1Mage 103.42 deeper than ws2r 93.23 at 2026-09-16 18:04:00 |

## leg 2026-09-16 18:15:10 | SHORT | target side LOW | rev-trade 2026-09-16 18:15:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 19:28:00 | REV-TRADE | the director found no candidate - no line is away with its 2 lines above towards. His "no candidates = rev-trade" || ws1b excursion 2026-09-16 19:25:00..2026-09-16 19:27:55, the nestle is ws1Mage 2.60 deeper than ws3r 6.56 at 2026-09-16 19:27:00, ws3Mage RESCUED - the both window opened 2026-09-16 17:43:00, ws3r reached 6.20 and ws3Mage reached -18.53 |

## leg 2026-09-16 19:28:10 | LONG | target side HIGH | rev-trade 2026-09-16 19:28:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 21:01:00 | WALK | cadence event, 6 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws22 (ws22r is the highest away line and ws23, ws24 are towards and ex-20/80). the next cadence event is first (ws22x crosses to ws22r 2026-09-16 21:23:00, the ws22x-cadence confirms 2026-09-16 21:24:55) || ws1b excursion 2026-09-16 20:59:00..2026-09-16 21:00:55, the nestle is ws1Mage 92.66 deeper than ws2r 87.34 at 2026-09-16 20:59:00 |
| 2026-09-16 21:03:00 | WALK | cadence event, 6 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws22 (ws22r is the highest away line and ws23, ws24 are towards and ex-20/80). the ws22x-cadence is first (ws22x crosses to ws22r 2026-09-16 21:23:00, the ws22x-cadence confirms 2026-09-16 21:24:55) || ws1b excursion 2026-09-16 21:02:00..2026-09-16 21:02:55, the nestle is ws1Mage 94.21 deeper than ws2r 85.67 at 2026-09-16 21:02:00 |
| 2026-09-16 21:24:55 | SEAM | the director's seam read from 2026-09-16 21:24:55 - ws25 is the highest ex-20/80 towards line, so the 2 above it are ws26, ws27. the seam+15s bar 2026-09-16 21:26:10 failed (ws23 are ex-20/80 AND towards (tagged), so no rev-trade) and the 10.0 min walk to 2026-09-16 21:36:10 never passed |
| 2026-09-16 21:24:55 | REV-TRADE | the ws22x-cadence - ws22x crossed to ws22r 2026-09-16 21:23:00 and confirmed here. 11 of 12 reversed since 2026-09-16 21:03:00 (event) = 91.7% >= 50% at the race bar itself |

## leg 2026-09-16 21:25:05 | SHORT | target side LOW | rev-trade 2026-09-16 21:24:55

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 21:45:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws3 (ws3r is the highest away line and ws4, ws5 are towards and ex-20/80). the ws3x-cadence is first (ws3x crosses to ws3r 2026-09-16 21:56:45, the ws3x-cadence confirms 2026-09-16 21:58:40) || ws1b excursion 2026-09-16 21:39:00..2026-09-16 21:44:55, the nestle is ws1Mage 3.96 deeper than ws3r 14.61 at 2026-09-16 21:42:00 |
| 2026-09-16 21:58:40 | SEAM | the director's seam read from 2026-09-16 21:58:40 - ws6 is the highest ex-20/80 towards line, so the 2 above it are ws7, ws8. the ws1 seam+15s bar 2026-09-16 21:59:10 - ws7, ws8 away and no ex-20/80 line towards (tagged) |
| 2026-09-16 21:59:10 | REV-TRADE | the director - the ws1 seam+15s bar 2026-09-16 21:59:10 - ws7, ws8 away and no ex-20/80 line towards (tagged) |

## leg 2026-09-16 21:59:20 | LONG | target side HIGH | rev-trade 2026-09-16 21:59:10

| the bar | the stage | why |
|---|---|---|
| 2026-09-16 21:59:20 | NO CADENCE EVENT | no cadence event on the HIGH side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-17 00:00:40 | SHORT | target side LOW | fdm re-entry 2026-09-17 00:00:35, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 00:57:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws1 (ws1r is the highest away line and ws2, ws3 are towards and ex-20/80). the ws1x-cadence is first (ws1x crosses to ws1Mage 2026-09-17 01:03:00, the ws1x-cadence confirms 2026-09-17 01:04:55) || ws1b excursion 2026-09-17 00:56:00..2026-09-17 00:56:55, the nestle is ws1Mage 4.34 deeper than ws2r 6.51 at 2026-09-17 00:56:00, ws3Mage RESCUED - the both window opened 2026-09-16 22:51:00, ws3r reached 0.69 and ws3Mage reached 12.13 |
| 2026-09-17 01:04:55 | SEAM | the director's seam read from 2026-09-17 01:04:55 - ws5 is the highest ex-20/80 towards line, so the 2 above it are ws6, ws7. the seam+15s bar 2026-09-17 01:06:10 failed (ws6, ws7 of the 2 lines above are not away yet) and the 10.0 min walk to 2026-09-17 01:16:10 never passed |
| 2026-09-17 01:04:55 | REV-TRADE | the ws1x-cadence - ws1x crossed to ws1Mage 2026-09-17 01:03:00 and confirmed here. 2 of 3 reversed since 2026-09-17 00:57:00 (event) = 66.7% >= 50% at the race bar itself |

## leg 2026-09-17 01:05:05 | LONG | target side HIGH | rev-trade 2026-09-17 01:04:55

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 01:40:00 | WALK | cadence event, 10 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws18 (ws18r is the highest away line and ws19, ws20 are towards and ex-20/80). the ws18x-cadence is first (ws18x crosses to ws18Mage 2026-09-17 01:53:00, the ws18x-cadence confirms 2026-09-17 01:54:55) || ws1b excursion 2026-09-17 01:26:00..2026-09-17 01:39:55, the nestle is ws1Mage 119.84 deeper than ws3r 85.39 at 2026-09-17 01:26:00 |
| 2026-09-17 01:54:55 | SEAM | the director's seam read from 2026-09-17 01:54:55 - ws25 is the highest ex-20/80 towards line, so the 2 above it are ws26, ws27. the ws1 seam+15s bar 2026-09-17 01:56:10 - ws26, ws27 away and no ex-20/80 line towards (tagged) |
| 2026-09-17 01:56:10 | REV-TRADE | the director - the ws1 seam+15s bar 2026-09-17 01:56:10 - ws26, ws27 away and no ex-20/80 line towards (tagged) |

## leg 2026-09-17 01:56:20 | SHORT | target side LOW | rev-trade 2026-09-17 01:56:10

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 02:25:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws3 (ws3r is the highest away line and ws4, ws5 are towards and ex-20/80). the ws3x-cadence is first (ws3x crosses to ws3Mage 2026-09-17 02:25:15, the ws3x-cadence confirms 2026-09-17 02:27:10) || ws1b excursion 2026-09-17 02:12:00..2026-09-17 02:24:55, the nestle is ws1Mage 4.38 deeper than ws1r 12.89 at 2026-09-17 02:12:00 |
| 2026-09-17 02:27:10 | SEAM | the director's seam read from 2026-09-17 02:27:10 - ws6 is the highest ex-20/80 towards line, so the 2 above it are ws7, ws8. the ws1 seam+15s bar 2026-09-17 02:28:10 - ws7, ws8 away and no ex-20/80 line towards (tagged) |
| 2026-09-17 02:28:10 | REV-TRADE | the director - the ws1 seam+15s bar 2026-09-17 02:28:10 - ws7, ws8 away and no ex-20/80 line towards (tagged) |

## leg 2026-09-17 02:28:20 | LONG | target side HIGH | rev-trade 2026-09-17 02:28:10

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 02:48:00 | REV-TRADE | the director found no candidate - no line is away with its 2 lines above towards. His "no candidates = rev-trade" || ws1b excursion 2026-09-17 02:43:00..2026-09-17 02:47:55, the nestle is ws1Mage 96.76 deeper than ws2r 91.61 at 2026-09-17 02:43:00 |

## leg 2026-09-17 02:48:10 | SHORT | target side LOW | rev-trade 2026-09-17 02:48:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 02:48:10 | NO CADENCE EVENT | no cadence event on the LOW side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-17 04:12:40 | SHORT | target side LOW | fdm re-entry 2026-09-17 04:12:35, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 04:25:00 | WALK | cadence event, 1 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws1 (ws1r is the highest away line and ws2, ws3 are towards and ex-20/80). the ws1x-cadence is first (ws1x crosses to ws1Mage 2026-09-17 04:26:05, the ws1x-cadence confirms 2026-09-17 04:28:00) || ws1b excursion 2026-09-17 04:23:00..2026-09-17 04:24:55, the nestle is ws1Mage 5.24 deeper than ws2r 7.48 at 2026-09-17 04:23:00, ws3Mage RESCUED - the both window opened 2026-09-17 02:13:00, ws3r reached 1.54 and ws3Mage reached 20.34 |
| 2026-09-17 04:28:00 | SEAM | the director's seam read from 2026-09-17 04:28:00 - ws4 is the highest ex-20/80 towards line, so the 2 above it are ws5, ws6. the seam+15s bar 2026-09-17 04:29:10 failed (ws5, ws6 of the 2 lines above are not away yet) and the 10.0 min walk to 2026-09-17 04:39:10 never passed |
| 2026-09-17 04:28:00 | REV-TRADE | the ws1x-cadence - ws1x crossed to ws1Mage 2026-09-17 04:26:05 and confirmed here. 2 of 2 reversed since 2026-09-17 04:25:00 (event) = 100.0% >= 50% at the race bar itself |

## leg 2026-09-17 04:28:10 | LONG | target side HIGH | rev-trade 2026-09-17 04:28:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 04:54:00 | REV-TRADE | cadence event, 0 of 27 lines ws4..ws30 printing ex-20/80 AND towards - his "if the answer is no, then rev-trade" || ws1b excursion 2026-09-17 04:51:00..2026-09-17 04:53:55, the nestle is ws1Mage 96.36 deeper than ws2r 94.37 at 2026-09-17 04:51:00 |

## leg 2026-09-17 04:54:10 | SHORT | target side LOW | rev-trade 2026-09-17 04:54:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 04:54:10 | NO CADENCE EVENT | no cadence event on the LOW side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-17 10:24:40 | LONG | target side HIGH | fdm re-entry 2026-09-17 10:24:35, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 12:03:00 | REV-TRADE | cadence event, 0 of 27 lines ws4..ws30 printing ex-20/80 AND towards - his "if the answer is no, then rev-trade" || ws1b excursion 2026-09-17 12:02:00..2026-09-17 12:02:55, the nestle is ws1Mage 101.84 deeper than ws1r 98.19 at 2026-09-17 12:02:00 |

## leg 2026-09-17 12:03:10 | SHORT | target side LOW | rev-trade 2026-09-17 12:03:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 12:03:10 | NO CADENCE EVENT | no cadence event on the LOW side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-17 12:42:40 | SHORT | target side LOW | fdm re-entry 2026-09-17 12:42:35, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 13:15:00 | WALK | cadence event, 4 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws3 (ws3r is the highest away line and ws4, ws5 are towards and ex-20/80). the ws3x-cadence is first (ws3x crosses to ws3Mage 2026-09-17 13:17:35, the ws3x-cadence confirms 2026-09-17 13:19:30) || ws1b excursion 2026-09-17 13:09:00..2026-09-17 13:14:55, the nestle is ws2Mage 6.18 deeper than ws1r 9.77 at 2026-09-17 13:13:00 |
| 2026-09-17 13:19:30 | SEAM | the director's seam read from 2026-09-17 13:19:30 - ws29 is the highest ex-20/80 towards line, so the 2 above it are ws30. the seam+15s bar 2026-09-17 13:20:10 failed (ws30 of the 1 lines above are not away yet) and the 10.0 min walk to 2026-09-17 13:30:10 never passed |
| 2026-09-17 13:19:30 | REV-TRADE | the ws3x-cadence - ws3x crossed to ws3Mage 2026-09-17 13:17:35 and confirmed here. 5 of 10 reversed since 2026-09-17 13:15:00 (event) = 50.0% >= 50% at the race bar itself |

## leg 2026-09-17 13:19:40 | LONG | target side HIGH | rev-trade 2026-09-17 13:19:30

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 13:19:40 | NO CADENCE EVENT | no cadence event on the HIGH side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-17 14:20:40 | SHORT | target side LOW | fdm re-entry 2026-09-17 14:20:35, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 14:20:40 | NO CADENCE EVENT | no cadence event on the LOW side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-17 15:18:40 | LONG | target side HIGH | fdm re-entry 2026-09-17 15:18:35, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 15:47:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws2 (ws2r is the highest away line and ws3, ws4 are towards and ex-20/80). the ws2x-cadence is first (ws2x crosses to ws2Mage 2026-09-17 16:05:50, the ws2x-cadence confirms 2026-09-17 16:07:45) || ws1b excursion 2026-09-17 15:37:00..2026-09-17 15:46:55, the nestle is ws1Mage 113.28 deeper than ws1r 96.98 at 2026-09-17 15:37:00, ws3Mage RESCUED - the both window opened 2026-09-17 15:42:00, ws3r reached 94.39 and ws3Mage reached 61.65 |
| 2026-09-17 16:07:45 | SEAM | the director's seam read from 2026-09-17 16:07:45 - ws5 is the highest ex-20/80 towards line, so the 2 above it are ws6, ws7. the ws1 seam+15s bar 2026-09-17 16:08:10 - ws6, ws7 away and no ex-20/80 line towards (tagged) |
| 2026-09-17 16:08:10 | REV-TRADE | the director - the ws1 seam+15s bar 2026-09-17 16:08:10 - ws6, ws7 away and no ex-20/80 line towards (tagged) |

## leg 2026-09-17 16:08:20 | SHORT | target side LOW | rev-trade 2026-09-17 16:08:10

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 16:08:20 | NO CADENCE EVENT | no cadence event on the LOW side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-17 17:36:40 | SHORT | target side LOW | fdm re-entry 2026-09-17 17:36:35, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 18:42:00 | REV-TRADE | the director found no candidate - no line is away with its 2 lines above towards. His "no candidates = rev-trade" || ws1b excursion 2026-09-17 18:34:00..2026-09-17 18:41:55, the nestle is ws1Mage -6.13 deeper than ws1r 14.39 at 2026-09-17 18:39:00 |

## leg 2026-09-17 18:42:10 | LONG | target side HIGH | rev-trade 2026-09-17 18:42:00

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 18:42:10 | NO CADENCE EVENT | no cadence event on the HIGH side from the open to 2026-09-17 23:59:55 |

## leg 2026-09-17 22:36:40 | LONG | target side HIGH | fdm re-entry 2026-09-17 22:36:35, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 22:51:00 | WALK | cadence event, 1 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws2 (ws2r is the highest away line and ws3, ws4 are towards and ex-20/80). the ws2x-cadence is first (ws2x crosses to ws2Mage 2026-09-17 22:53:10, the ws2x-cadence confirms 2026-09-17 22:55:05) || ws1b excursion 2026-09-17 22:37:00..2026-09-17 22:50:55, the nestle is ws1Mage 107.70 deeper than ws1r 87.49 at 2026-09-17 22:37:00, ws3Mage RESCUED - the both window opened 2026-09-17 22:37:00, ws3r reached 95.35 and ws3Mage reached 75.15 |
| 2026-09-17 22:55:05 | SEAM | the director's seam read from 2026-09-17 22:55:05 - ws4 is the highest ex-20/80 towards line, so the 2 above it are ws5, ws6. the seam+15s bar 2026-09-17 22:56:10 failed (ws5, ws6 of the 2 lines above are not away yet) and the 10.0 min walk to 2026-09-17 23:06:10 never passed |
| 2026-09-17 22:55:05 | REV-TRADE | the ws2x-cadence - ws2x crossed to ws2Mage 2026-09-17 22:53:10 and confirmed here. 1 of 2 reversed since 2026-09-17 22:51:00 (event) = 50.0% >= 50% at the race bar itself |

## leg 2026-09-17 22:55:15 | SHORT | target side LOW | rev-trade 2026-09-17 22:55:05

| the bar | the stage | why |
|---|---|---|
| 2026-09-17 22:55:15 | NO CADENCE EVENT | no cadence event on the LOW side from the open to 2026-09-17 23:59:55 |

## the 28 eligible lines at every ws10x-cadence | ws3..ws30

| the ws10x-cadence | the trade it was deciding | ex-20/80 at least once | contributed a reversal | silent - ex-fence but no reversal | never ex-fence |
|---|---|---|---|---|---|
| 2026-09-15 11:53:25 | 2026-09-15 08:50:40 SHORT | 13 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws15, ws16 | 12 of 13 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws15, ws16 | 1 - ws13 | 15 - ws14, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-15 12:29:40 | 2026-09-15 11:53:35 LONG | 4 of 28 - ws3, ws4, ws5, ws6 | 1 of 4 - ws6 | 3 - ws3, ws4, ws5 | 24 - ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-15 13:53:00 | 2026-09-15 12:58:10 SHORT | 5 of 28 - ws3, ws4, ws5, ws6, ws8 | 0 of 5 - none | 5 - ws3, ws4, ws5, ws6, ws8 | 23 - ws7, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-15 22:08:50 | 2026-09-15 21:00:10 SHORT | 5 of 28 - ws4, ws5, ws6, ws22, ws25 | 1 of 5 - ws22 | 4 - ws4, ws5, ws6, ws25 | 23 - ws3, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws23, ws24, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-16 01:12:10 | 2026-09-16 00:36:40 SHORT | 12 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14 | 9 of 12 - ws3, ws4, ws5, ws6, ws8, ws9, ws10, ws11, ws13 | 3 - ws7, ws12, ws14 | 16 - ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-16 21:24:55 | 2026-09-16 19:28:10 LONG | 12 of 28 - ws3, ws4, ws5, ws10, ws12, ws19, ws20, ws23, ws24, ws25, ws27, ws29 | 11 of 12 - ws3, ws4, ws5, ws10, ws12, ws19, ws20, ws24, ws25, ws27, ws29 | 1 - ws23 | 16 - ws6, ws7, ws8, ws9, ws11, ws13, ws14, ws15, ws16, ws17, ws18, ws21, ws22, ws26, ws28, ws30 |
| 2026-09-17 01:04:55 | 2026-09-17 00:00:40 SHORT | 3 of 28 - ws3, ws4, ws5 | 2 of 3 - ws3, ws4 | 1 - ws5 | 25 - ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-17 04:28:00 | 2026-09-17 04:12:40 SHORT | 2 of 28 - ws3, ws4 | 2 of 2 - ws3, ws4 | 0 - none | 26 - ws5, ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-09-17 13:19:30 | 2026-09-17 12:42:40 SHORT | 10 of 28 - ws3, ws4, ws5, ws6, ws7, ws24, ws25, ws26, ws28, ws29 | 5 of 10 - ws3, ws4, ws5, ws6, ws26 | 5 - ws7, ws24, ws25, ws28, ws29 | 18 - ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws27, ws30 |
| 2026-09-17 22:55:05 | 2026-09-17 22:36:40 LONG | 2 of 28 - ws3, ws4 | 1 of 2 - ws3 | 1 - ws4 | 26 - ws5, ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |

| the roll-up over 10 ws10x-cadences | value |
|---|---|
| eligible lines, every time | 28 |
| population, smallest .. largest | 2 .. 13 |
| population, mean | 6.8 |
| contributed, smallest .. largest | 0 .. 12 |
| contributed, mean | 4.4 |

| the line | times in the population | times it contributed |
|---|---|---|
| ws3 | 9 of 10 | 7 of 10 |
| ws4 | 10 of 10 | 6 of 10 |
| ws5 | 8 of 10 | 4 of 10 |
| ws6 | 6 of 10 | 4 of 10 |
| ws7 | 3 of 10 | 1 of 10 |
| ws8 | 3 of 10 | 2 of 10 |
| ws9 | 2 of 10 | 2 of 10 |
| ws10 | 3 of 10 | 3 of 10 |
| ws11 | 2 of 10 | 2 of 10 |
| ws12 | 3 of 10 | 2 of 10 |
| ws13 | 2 of 10 | 1 of 10 |
| ws14 | 1 of 10 | 0 of 10 |
| ws15 | 1 of 10 | 1 of 10 |
| ws16 | 1 of 10 | 1 of 10 |
| ws17 | 0 of 10 | 0 of 10 |
| ws18 | 0 of 10 | 0 of 10 |
| ws19 | 1 of 10 | 1 of 10 |
| ws20 | 1 of 10 | 1 of 10 |
| ws21 | 0 of 10 | 0 of 10 |
| ws22 | 1 of 10 | 1 of 10 |
| ws23 | 1 of 10 | 0 of 10 |
| ws24 | 2 of 10 | 1 of 10 |
| ws25 | 3 of 10 | 1 of 10 |
| ws26 | 1 of 10 | 1 of 10 |
| ws27 | 1 of 10 | 1 of 10 |
| ws28 | 1 of 10 | 0 of 10 |
| ws29 | 2 of 10 | 1 of 10 |
| ws30 | 0 of 10 | 0 of 10 |

## the legs | every number carries the FDM_MAE_CAP 1.10% stop

| the open | the trade | the rev-trade signal | the exit | the exit kind | held min | MAE% | MFE% | realised% |
|---|---|---|---|---|---|---|---|---|
| 2026-09-15 08:50:40 | SHORT | 2026-09-15 11:53:25 | 2026-09-15 11:53:30 | rev-trade | 182.8 | 1.024 | 0.614 | +0.226 |
| 2026-09-15 11:53:35 | LONG | 2026-09-15 12:58:00 | 2026-09-15 12:58:05 | rev-trade | 64.5 | 0.127 | 1.514 | +0.920 |
| 2026-09-15 12:58:10 | SHORT | 2026-09-15 14:59:10 | 2026-09-15 14:59:15 | rev-trade | 121.1 | 0.827 | 4.284 | +2.594 |
| 2026-09-15 14:59:20 | LONG | 2026-09-15 17:42:00 | 2026-09-15 17:42:05 | rev-trade | 162.8 | 0.417 | 3.058 | +2.108 |
| 2026-09-15 17:42:10 | SHORT | 2026-09-15 18:33:10 | 2026-09-15 18:33:15 | rev-trade | 51.1 | 0.824 | 1.282 | +1.163 |
| 2026-09-15 18:33:20 | LONG | - | 2026-09-15 18:37:05 | STOP at 1.10% | 3.8 | 1.100 | 0.314 | -1.100 |
| 2026-09-15 18:54:40 | LONG | 2026-09-15 21:00:00 | 2026-09-15 21:00:05 | rev-trade | 125.4 | 0.920 | 1.442 | +1.016 |
| 2026-09-15 21:00:10 | SHORT | - | 2026-09-15 23:08:30 | STOP at 1.10% | 128.3 | 1.100 | 2.339 | -1.100 |
| 2026-09-16 00:36:40 | SHORT | 2026-09-16 01:12:10 | 2026-09-16 01:12:15 | rev-trade | 35.6 | 0.319 | 1.096 | +0.762 |
| 2026-09-16 01:12:20 | LONG | - | 2026-09-16 01:40:30 | STOP at 1.10% | 28.2 | 1.100 | 0.285 | -1.100 |
| 2026-09-16 09:18:40 | SHORT | 2026-09-16 12:34:00 | 2026-09-16 12:34:05 | rev-trade | 195.4 | 1.076 | 0.732 | +0.146 |
| 2026-09-16 12:34:10 | LONG | - | 2026-09-16 13:10:30 | STOP at 1.10% | 36.3 | 1.100 | 0.051 | -1.100 |
| 2026-09-16 18:00:40 | LONG | 2026-09-16 18:15:00 | 2026-09-16 18:15:05 | rev-trade | 14.4 | 0.925 | 4.000 | +2.537 |
| 2026-09-16 18:15:10 | SHORT | 2026-09-16 19:28:00 | 2026-09-16 19:28:05 | rev-trade | 72.9 | 0.853 | 3.127 | +2.004 |
| 2026-09-16 19:28:10 | LONG | 2026-09-16 21:24:55 | 2026-09-16 21:25:00 | rev-trade | 116.8 | 0.521 | 2.508 | +1.355 |
| 2026-09-16 21:25:05 | SHORT | 2026-09-16 21:59:10 | 2026-09-16 21:59:15 | rev-trade | 34.2 | 0.448 | 0.441 | -0.367 |
| 2026-09-16 21:59:20 | LONG | - | 2026-09-16 22:02:35 | STOP at 1.10% | 3.2 | 1.100 | 0.117 | -1.100 |
| 2026-09-17 00:00:40 | SHORT | 2026-09-17 01:04:55 | 2026-09-17 01:05:00 | rev-trade | 64.3 | 0.719 | 0.450 | +0.269 |
| 2026-09-17 01:05:05 | LONG | 2026-09-17 01:56:10 | 2026-09-17 01:56:15 | rev-trade | 51.2 | 0.022 | 2.098 | +1.056 |
| 2026-09-17 01:56:20 | SHORT | 2026-09-17 02:28:10 | 2026-09-17 02:28:15 | rev-trade | 31.9 | 0.324 | 1.052 | +0.418 |
| 2026-09-17 02:28:20 | LONG | 2026-09-17 02:48:00 | 2026-09-17 02:48:05 | rev-trade | 19.8 | 0.326 | 1.303 | +0.774 |
| 2026-09-17 02:48:10 | SHORT | - | 2026-09-17 03:28:35 | STOP at 1.10% | 40.4 | 1.100 | 0.079 | -1.100 |
| 2026-09-17 04:12:40 | SHORT | 2026-09-17 04:28:00 | 2026-09-17 04:28:05 | rev-trade | 15.4 | 0.113 | 0.545 | +0.311 |
| 2026-09-17 04:28:10 | LONG | 2026-09-17 04:54:00 | 2026-09-17 04:54:05 | rev-trade | 25.9 | 0.475 | 1.071 | +0.766 |
| 2026-09-17 04:54:10 | SHORT | - | 2026-09-17 05:28:20 | STOP at 1.10% | 34.2 | 1.100 | 0.120 | -1.100 |
| 2026-09-17 10:24:40 | LONG | 2026-09-17 12:03:00 | 2026-09-17 12:03:05 | rev-trade | 98.4 | 0.498 | 0.982 | +0.650 |
| 2026-09-17 12:03:10 | SHORT | - | 2026-09-17 12:26:35 | STOP at 1.10% | 23.4 | 1.100 | 0.213 | -1.100 |
| 2026-09-17 12:42:40 | SHORT | 2026-09-17 13:19:30 | 2026-09-17 13:19:35 | rev-trade | 36.9 | 0.254 | 1.199 | +0.857 |
| 2026-09-17 13:19:40 | LONG | - | 2026-09-17 13:39:45 | STOP at 1.10% | 20.1 | 1.100 | 0.622 | -1.100 |
| 2026-09-17 14:20:40 | SHORT | - | 2026-09-17 14:27:10 | STOP at 1.10% | 6.5 | 1.100 | -0.000 | -1.100 |
| 2026-09-17 15:18:40 | LONG | 2026-09-17 16:08:10 | 2026-09-17 16:08:15 | rev-trade | 49.6 | 0.365 | 2.029 | +1.706 |
| 2026-09-17 16:08:20 | SHORT | - | 2026-09-17 17:04:40 | STOP at 1.10% | 56.3 | 1.100 | 0.614 | -1.100 |
| 2026-09-17 17:36:40 | SHORT | 2026-09-17 18:42:00 | 2026-09-17 18:42:05 | rev-trade | 65.4 | 0.547 | 1.081 | +0.616 |
| 2026-09-17 18:42:10 | LONG | - | 2026-09-17 22:11:20 | STOP at 1.10% | 209.2 | 1.100 | 0.441 | -1.100 |
| 2026-09-17 22:36:40 | LONG | 2026-09-17 22:55:05 | 2026-09-17 22:55:10 | rev-trade | 18.5 | 0.021 | 0.367 | +0.014 |
| 2026-09-17 22:55:15 | SHORT | - | 2026-09-17 23:23:40 | STOP at 1.10% | 28.4 | 1.100 | 0.048 | -1.100 |

| the aggregate | value |
|---|---|
| legs | 36 |
| stopped | 13 |
| gross % | +7.602 |
| drag % | -7.110 (0.1975% round trip x 36 legs) |
| net % | +0.492 |
| MAE % total | 26.247 |
| MFE % total | 41.520 |
| MFE captured | 18.3% of MFE |
| held min, shortest .. longest | 3.2 .. 209.2 |

## each day's contribution | a leg counts on the day it OPENED

| the day | legs | stopped | gross % | drag % | net % | MAE % | MFE % | MFE captured | rescued cadences |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-15 | 8 | 2 | +5.827 | -1.580 | +4.247 | 6.340 | 14.848 | 39.2% | 1 |
| 2026-09-16 | 9 | 3 | +3.138 | -1.778 | +1.360 | 7.443 | 12.357 | 25.4% | 1 |
| 2026-09-17 | 19 | 8 | -1.363 | -3.753 | -5.115 | 12.464 | 14.315 | -9.5% | 4 |
