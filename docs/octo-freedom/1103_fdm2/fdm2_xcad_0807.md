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
| 2026-08-07 11:50:00 | REV-TRADE | the director found no candidate - no line is away with its 2 lines above towards. His "no candidates = rev-trade" || ws1b excursion 2026-08-07 11:45:00..2026-08-07 11:49:55, the nestle is ws1Mage 3.37 deeper than ws2r 14.37 at 2026-08-07 11:45:00 |

## leg 2026-08-07 11:50:10 | LONG | target side HIGH | rev-trade 2026-08-07 11:50:00

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 12:15:00 | REV-TRADE | the director found no candidate - no line is away with its 2 lines above towards. His "no candidates = rev-trade" || ws1b excursion 2026-08-07 12:10:00..2026-08-07 12:14:55, the nestle is ws1Mage 103.85 deeper than ws2r 98.97 at 2026-08-07 12:10:00 |

## leg 2026-08-07 12:15:10 | SHORT | target side LOW | rev-trade 2026-08-07 12:15:00

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 13:07:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws4 (ws4r is the highest away line and ws5, ws6 are towards and ex-20/80). the ws4x-cadence is first (ws4x crosses to ws4r 2026-08-07 13:09:25, the ws4x-cadence confirms 2026-08-07 13:11:20) || ws1b excursion 2026-08-07 12:57:00..2026-08-07 13:06:55, the nestle is ws1Mage -5.78 deeper than ws1r 13.36 at 2026-08-07 13:02:00 |
| 2026-08-07 13:11:20 | SEAM | the director's seam read from 2026-08-07 13:11:20 - ws6 is the highest ex-20/80 towards line, so the 2 above it are ws7, ws8. the ws1 seam+15s bar 2026-08-07 13:12:10 - ws7, ws8 away and no ex-20/80 line towards (tagged) |
| 2026-08-07 13:12:10 | REV-TRADE | the director - the ws1 seam+15s bar 2026-08-07 13:12:10 - ws7, ws8 away and no ex-20/80 line towards (tagged) |

## leg 2026-08-07 13:12:20 | LONG | target side HIGH | rev-trade 2026-08-07 13:12:10

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 13:37:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws2 (ws2r is the highest away line and ws3, ws4 are towards and ex-20/80). the next cadence event is first (ws2x crosses to ws2r 2026-08-07 13:45:30, the ws2x-cadence confirms 2026-08-07 13:47:25) || ws1b excursion 2026-08-07 13:35:00..2026-08-07 13:36:55, the nestle is ws1Mage 89.87 deeper than ws3r 89.31 at 2026-08-07 13:35:00, ws3Mage RESCUED - the both window opened 2026-08-07 13:35:00, ws3r reached 90.10 and ws3Mage reached 63.10 |
| 2026-08-07 13:46:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws2 (ws2r is the highest away line and ws3, ws4 are towards and ex-20/80). the ws2x-cadence is first (ws2x crosses to ws2Mage 2026-08-07 14:00:50, the ws2x-cadence confirms 2026-08-07 14:02:45) || ws1b excursion 2026-08-07 13:39:00..2026-08-07 13:45:55, the nestle is ws1Mage 95.36 deeper than ws3r 88.32 at 2026-08-07 13:40:00, ws3Mage RESCUED - the both window opened 2026-08-07 13:39:30, ws3r reached 90.13 and ws3Mage reached 67.24 |
| 2026-08-07 14:02:45 | SEAM | the director's seam read from 2026-08-07 14:02:45 - ws6 is the highest ex-20/80 towards line, so the 2 above it are ws7, ws8. the ws1 seam+15s bar 2026-08-07 14:03:10 - ws7, ws8 away and no ex-20/80 line towards (tagged) |
| 2026-08-07 14:03:10 | REV-TRADE | the director - the ws1 seam+15s bar 2026-08-07 14:03:10 - ws7, ws8 away and no ex-20/80 line towards (tagged) |

## leg 2026-08-07 14:03:20 | SHORT | target side LOW | rev-trade 2026-08-07 14:03:10

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 14:20:00 | REV-TRADE | the director found no candidate - no line is away with its 2 lines above towards. His "no candidates = rev-trade" || ws1b excursion 2026-08-07 14:12:00..2026-08-07 14:19:55, the nestle is ws1Mage -3.25 deeper than ws2r 14.87 at 2026-08-07 14:12:00 |

## leg 2026-08-07 14:20:10 | LONG | target side HIGH | rev-trade 2026-08-07 14:20:00

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 14:20:10 | NO CADENCE EVENT | no cadence event on the HIGH side from the open to 2026-08-07 23:59:55 |

## leg 2026-08-07 15:10:40 | LONG | target side HIGH | fdm re-entry 2026-08-07 15:10:35, window side LOW

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 16:11:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws8 (ws8r is the highest away line and ws9, ws10 are towards and ex-20/80). the ws8x-cadence is first (ws8x crosses to ws8r 2026-08-07 16:15:35, the ws8x-cadence confirms 2026-08-07 16:17:30) || ws1b excursion 2026-08-07 16:07:00..2026-08-07 16:10:55, the nestle is ws1Mage 99.71 deeper than ws1r 97.33 at 2026-08-07 16:08:00, ws3Mage RESCUED - the both window opened 2026-08-07 15:32:30, ws3r reached 95.76 and ws3Mage reached 74.83 |
| 2026-08-07 16:17:30 | SEAM | the director's seam read from 2026-08-07 16:17:30 - ws10 is the highest ex-20/80 towards line, so the 2 above it are ws11, ws12. the seam+15s bar 2026-08-07 16:18:10 failed (ws11, ws12 of the 2 lines above are not away yet) and the 10.0 min walk to 2026-08-07 16:28:10 never passed |
| 2026-08-07 16:17:30 | REV-TRADE | the ws8x-cadence - ws8x crossed to ws8r 2026-08-07 16:15:35 and confirmed here. 7 of 8 reversed since 2026-08-07 16:11:00 (event) = 87.5% >= 50% at the race bar itself |

## leg 2026-08-07 16:17:40 | SHORT | target side LOW | rev-trade 2026-08-07 16:17:30

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 17:04:00 | REV-TRADE | the director found no candidate - no line is away with its 2 lines above towards. His "no candidates = rev-trade" || ws1b excursion 2026-08-07 16:57:00..2026-08-07 17:03:55, the nestle is ws1Mage 8.71 deeper than ws1r 11.53 at 2026-08-07 16:58:00 |

## leg 2026-08-07 17:04:10 | LONG | target side HIGH | rev-trade 2026-08-07 17:04:00

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 18:10:00 | REV-TRADE | the director found no candidate - no line is away with its 2 lines above towards. His "no candidates = rev-trade" || ws1b excursion 2026-08-07 17:59:00..2026-08-07 18:09:55, the nestle is ws1Mage 95.56 deeper than ws1r 85.71 at 2026-08-07 18:00:00 |

## leg 2026-08-07 18:10:10 | SHORT | target side LOW | rev-trade 2026-08-07 18:10:00

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 18:42:00 | WALK | cadence event, 1 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws2 (ws2r is the highest away line and ws3, ws4 are towards and ex-20/80). the next cadence event is first (ws2x crosses to ws2r 2026-08-07 18:45:40, the ws2x-cadence confirms 2026-08-07 18:47:35) || ws1b excursion 2026-08-07 18:41:00..2026-08-07 18:41:55, the nestle is ws1Mage -8.45 deeper than ws1r 10.08 at 2026-08-07 18:41:00, ws3Mage RESCUED - the both window opened 2026-08-07 18:41:00, ws3r reached 13.32 and ws3Mage reached 38.78 |
| 2026-08-07 18:46:00 | WALK | cadence event, 2 of 27 lines printing ex-20/80 AND towards -> walk. the race runs on ws2 (ws2r is the highest away line and ws3, ws4 are towards and ex-20/80). the ws2x-cadence is first (ws2x crosses to ws2Mage 2026-08-07 18:47:00, the ws2x-cadence confirms 2026-08-07 18:48:55) || ws1b excursion 2026-08-07 18:43:00..2026-08-07 18:45:55, the nestle is ws1Mage -1.10 deeper than ws3r 13.32 at 2026-08-07 18:43:00, ws3Mage RESCUED - the both window opened 2026-08-07 18:43:00, ws3r reached 11.36 and ws3Mage reached 30.63 |
| 2026-08-07 18:48:55 | SEAM | the director's seam read from 2026-08-07 18:48:55 - ws5 is the highest ex-20/80 towards line, so the 2 above it are ws6, ws7. the seam+15s bar 2026-08-07 18:50:10 failed (ws6, ws7 of the 2 lines above are not away yet) and the 10.0 min walk to 2026-08-07 19:00:10 never passed |
| 2026-08-07 18:48:55 | REV-TRADE | the ws2x-cadence - ws2x crossed to ws2Mage 2026-08-07 18:47:00 and confirmed here. 3 of 3 reversed since 2026-08-07 18:46:00 (event) = 100.0% >= 50% at the race bar itself |

## leg 2026-08-07 18:49:05 | LONG | target side HIGH | rev-trade 2026-08-07 18:48:55

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
| 2026-08-07 20:12:00 | REV-TRADE | the director found no candidate - no line is away with its 2 lines above towards. His "no candidates = rev-trade" || ws1b excursion 2026-08-07 20:00:00..2026-08-07 20:11:55, the nestle is ws1Mage -7.95 deeper than ws1r 14.29 at 2026-08-07 20:05:00 |

## leg 2026-08-07 20:12:10 | LONG | target side HIGH | rev-trade 2026-08-07 20:12:00

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 20:12:10 | NO CADENCE EVENT | no cadence event on the HIGH side from the open to 2026-08-07 23:59:55 |

## leg 2026-08-07 23:24:40 | SHORT | target side LOW | fdm re-entry 2026-08-07 23:24:35, window side HIGH

| the bar | the stage | why |
|---|---|---|
| 2026-08-07 23:24:40 | NO CADENCE EVENT | no cadence event on the LOW side from the open to 2026-08-07 23:59:55 |

## the 28 eligible lines at every ws10x-cadence | ws3..ws30

| the ws10x-cadence | the trade it was deciding | ex-20/80 at least once | contributed a reversal | silent - ex-fence but no reversal | never ex-fence |
|---|---|---|---|---|---|
| 2026-08-07 16:17:30 | 2026-08-07 15:10:40 LONG | 8 of 28 - ws3, ws4, ws5, ws6, ws7, ws8, ws9, ws10 | 7 of 8 - ws3, ws4, ws6, ws7, ws8, ws9, ws10 | 1 - ws5 | 20 - ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |
| 2026-08-07 18:48:55 | 2026-08-07 18:10:10 SHORT | 3 of 28 - ws3, ws4, ws5 | 3 of 3 - ws3, ws4, ws5 | 0 - none | 25 - ws6, ws7, ws8, ws9, ws10, ws11, ws12, ws13, ws14, ws15, ws16, ws17, ws18, ws19, ws20, ws21, ws22, ws23, ws24, ws25, ws26, ws27, ws28, ws29, ws30 |

| the roll-up over 2 ws10x-cadences | value |
|---|---|
| eligible lines, every time | 28 |
| population, smallest .. largest | 3 .. 8 |
| population, mean | 5.5 |
| contributed, smallest .. largest | 3 .. 7 |
| contributed, mean | 5.0 |

| the line | times in the population | times it contributed |
|---|---|---|
| ws3 | 2 of 2 | 2 of 2 |
| ws4 | 2 of 2 | 2 of 2 |
| ws5 | 2 of 2 | 1 of 2 |
| ws6 | 1 of 2 | 1 of 2 |
| ws7 | 1 of 2 | 1 of 2 |
| ws8 | 1 of 2 | 1 of 2 |
| ws9 | 1 of 2 | 1 of 2 |
| ws10 | 1 of 2 | 1 of 2 |
| ws11 | 0 of 2 | 0 of 2 |
| ws12 | 0 of 2 | 0 of 2 |
| ws13 | 0 of 2 | 0 of 2 |
| ws14 | 0 of 2 | 0 of 2 |
| ws15 | 0 of 2 | 0 of 2 |
| ws16 | 0 of 2 | 0 of 2 |
| ws17 | 0 of 2 | 0 of 2 |
| ws18 | 0 of 2 | 0 of 2 |
| ws19 | 0 of 2 | 0 of 2 |
| ws20 | 0 of 2 | 0 of 2 |
| ws21 | 0 of 2 | 0 of 2 |
| ws22 | 0 of 2 | 0 of 2 |
| ws23 | 0 of 2 | 0 of 2 |
| ws24 | 0 of 2 | 0 of 2 |
| ws25 | 0 of 2 | 0 of 2 |
| ws26 | 0 of 2 | 0 of 2 |
| ws27 | 0 of 2 | 0 of 2 |
| ws28 | 0 of 2 | 0 of 2 |
| ws29 | 0 of 2 | 0 of 2 |
| ws30 | 0 of 2 | 0 of 2 |

## the legs | every number carries the FDM_MAE_CAP 1.10% stop

| the open | the trade | the rev-trade signal | the exit | the exit kind | held min | MAE% | MFE% | realised% |
|---|---|---|---|---|---|---|---|---|
| 2026-08-07 07:10:40 | LONG | 2026-08-07 08:51:00 | 2026-08-07 08:51:05 | rev-trade | 100.4 | 0.506 | 0.257 | -0.047 |
| 2026-08-07 08:51:10 | SHORT | 2026-08-07 11:50:00 | 2026-08-07 11:50:05 | rev-trade | 178.9 | 0.795 | 0.179 | +0.070 |
| 2026-08-07 11:50:10 | LONG | 2026-08-07 12:15:00 | 2026-08-07 12:15:05 | rev-trade | 24.9 | 0.055 | 1.092 | +0.725 |
| 2026-08-07 12:15:10 | SHORT | 2026-08-07 13:12:10 | 2026-08-07 13:12:15 | rev-trade | 57.1 | 0.619 | 1.176 | +0.782 |
| 2026-08-07 13:12:20 | LONG | 2026-08-07 14:03:10 | 2026-08-07 14:03:15 | rev-trade | 50.9 | 0.055 | 0.655 | +0.289 |
| 2026-08-07 14:03:20 | SHORT | 2026-08-07 14:20:00 | 2026-08-07 14:20:05 | rev-trade | 16.8 | 0.000 | 1.065 | +0.389 |
| 2026-08-07 14:20:10 | LONG | - | 2026-08-07 14:51:50 | STOP at 1.10% | 31.7 | 1.100 | 0.187 | -1.100 |
| 2026-08-07 15:10:40 | LONG | 2026-08-07 16:17:30 | 2026-08-07 16:17:35 | rev-trade | 66.9 | 0.102 | 0.849 | +0.629 |
| 2026-08-07 16:17:40 | SHORT | 2026-08-07 17:04:00 | 2026-08-07 17:04:05 | rev-trade | 46.4 | 0.312 | 0.734 | +0.422 |
| 2026-08-07 17:04:10 | LONG | 2026-08-07 18:10:00 | 2026-08-07 18:10:05 | rev-trade | 65.9 | 0.549 | 0.549 | +0.384 |
| 2026-08-07 18:10:10 | SHORT | 2026-08-07 18:48:55 | 2026-08-07 18:49:00 | rev-trade | 38.8 | 0.023 | 0.539 | +0.359 |
| 2026-08-07 18:49:05 | LONG | 2026-08-07 19:05:00 | 2026-08-07 19:05:05 | rev-trade | 16.0 | 0.102 | 0.510 | +0.337 |
| 2026-08-07 19:05:10 | SHORT | - | 2026-08-07 19:17:00 | STOP at 1.10% | 11.8 | 1.100 | 0.008 | -1.100 |
| 2026-08-07 19:30:40 | SHORT | 2026-08-07 20:12:00 | 2026-08-07 20:12:05 | rev-trade | 41.4 | 0.187 | 1.563 | +1.097 |
| 2026-08-07 20:12:10 | LONG | - | 2026-08-07 21:51:20 | STOP at 1.10% | 99.2 | 1.100 | 0.134 | -1.100 |
| 2026-08-07 23:24:40 | SHORT | - | 2026-08-07 23:59:55 | no rev-trade before the walk's end | 35.2 | 0.302 | 0.429 | -0.207 |

| the aggregate | value |
|---|---|
| legs | 16 |
| stopped | 3 |
| gross % | +1.929 |
| drag % | -3.160 (0.1975% round trip x 16 legs) |
| net % | -1.231 |
| MAE % total | 6.907 |
| MFE % total | 9.927 |
| MFE captured | 19.4% of MFE |
| held min, shortest .. longest | 11.8 .. 178.9 |

## the fdm2-wsxcad-director | one row per cadence event | FDM_XCAD_ON 1
# the candidate is `fdm-conf-xcross-candidate`, HIS knob name: the highest line
# printing away while the 2 lines above it print towards AND ex-20/80
# FDM_XCAD_RULE B, FDM_XCAD_EXF 0, FDM_XCAD_FRM confirm, FDM_XCAD_TAG_AT event
# the seam read is the next ws1 seam + 15s = 3 bars, then a 10.0 min walk that truncates on the first pass
# the reversal gate spans the cadence window open to the confirmed cross bar, FDM_XCAD_REV_FROM window
# no candidate means FDM_XCAD_NONE rev-trade
# every value is closed-prev at the cadence event and EMERGING at the seam re-read

| the cadence event | the incoming trade | its own side | the cadence window opened | the candidate | the lines above it | ex-20/80 at the event | towards at the event | the ex-20/80 towards lines | clause one tests | the x cross | the x confirm | which target | the rev-trade bar | the seam verdict | the rev-trade bar on the other clause-two reading | why | the ws10 race confirm, for comparison |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-07 08:51:00 | 2026-08-07 07:10:40 LONG | HIGH, upwards | 2026-08-07 08:43:00 | none | - | 0 of 30 | 3 of 30 | - | - | - | - | - | 2026-08-07 08:51:00 | REV-TRADE at the event, FDM_XCAD_NONE | - | no line is away with its 2 lines above towards | 2026-08-07 09:53:40 |
| 2026-08-07 11:50:00 | 2026-08-07 08:51:10 SHORT | LOW, downwards | 2026-08-07 11:45:00 | none | - | 2 of 30 | 2 of 30 | - | - | - | - | - | 2026-08-07 11:50:00 | REV-TRADE at the event, FDM_XCAD_NONE | - | no line is away with its 2 lines above towards | 2026-08-07 11:56:40 |
| 2026-08-07 12:15:00 | 2026-08-07 11:50:10 LONG | HIGH, upwards | 2026-08-07 12:10:00 | none | - | 3 of 30 | 20 of 30 | - | - | - | - | - | 2026-08-07 12:15:00 | REV-TRADE at the event, FDM_XCAD_NONE | - | no line is away with its 2 lines above towards | 2026-08-07 12:21:55 |
| 2026-08-07 13:07:00 | 2026-08-07 12:15:10 SHORT | LOW, downwards | 2026-08-07 12:57:00 | ws4r | ws5, ws6 | 4 of 30 | 24 of 30 | ws5, ws6 | ws7, ws8 | 2026-08-07 13:09:25 | 2026-08-07 13:11:20 | ws4r | 2026-08-07 13:12:10 | REV-TRADE | 2026-08-07 13:12:10 | the ws1 seam+15s bar 2026-08-07 13:12:10 - ws7, ws8 away and no ex-20/80 line towards (tagged) | 2026-08-07 13:11:50 |
| 2026-08-07 13:37:00 | 2026-08-07 13:12:20 LONG | HIGH, upwards | 2026-08-07 13:35:00 | ws2r | ws3, ws4 | 4 of 30 | 19 of 30 | ws3, ws4, ws5 | ws6, ws7 | 2026-08-07 13:45:30 | 2026-08-07 13:47:25 | ws2r | - | held | - | the seam+15s bar 2026-08-07 13:48:10 failed (ws7 of the 2 lines above are not away yet) and the 10.0 min walk to 2026-08-07 13:58:10 never passed | 2026-08-07 14:00:20 |
| 2026-08-07 13:46:00 | 2026-08-07 13:12:20 LONG | HIGH, upwards | 2026-08-07 13:39:00 | ws2r | ws3, ws4 | 4 of 30 | 20 of 30 | ws3, ws4, ws6 | ws7, ws8 | 2026-08-07 14:00:50 | 2026-08-07 14:02:45 | ws2Mage | 2026-08-07 14:03:10 | REV-TRADE | 2026-08-07 14:03:10 | the ws1 seam+15s bar 2026-08-07 14:03:10 - ws7, ws8 away and no ex-20/80 line towards (tagged) | 2026-08-07 14:00:20 |
| 2026-08-07 14:20:00 | 2026-08-07 14:03:20 SHORT | LOW, downwards | 2026-08-07 14:12:00 | none | - | 2 of 30 | 22 of 30 | - | - | - | - | - | 2026-08-07 14:20:00 | REV-TRADE at the event, FDM_XCAD_NONE | - | no line is away with its 2 lines above towards | 2026-08-07 14:42:15 |
| 2026-08-07 16:11:00 | 2026-08-07 15:10:40 LONG | HIGH, upwards | 2026-08-07 16:07:00 | ws8r | ws9, ws10 | 4 of 30 | 21 of 30 | ws9, ws10 | ws11, ws12 | 2026-08-07 16:15:35 | 2026-08-07 16:17:30 | ws8r | - | held | - | the seam+15s bar 2026-08-07 16:18:10 failed (ws11, ws12 of the 2 lines above are not away yet) and the 10.0 min walk to 2026-08-07 16:28:10 never passed | 2026-08-07 16:18:50 |
| 2026-08-07 17:04:00 | 2026-08-07 16:17:40 SHORT | LOW, downwards | 2026-08-07 16:57:00 | none | - | 2 of 30 | 17 of 30 | - | - | - | - | - | 2026-08-07 17:04:00 | REV-TRADE at the event, FDM_XCAD_NONE | - | no line is away with its 2 lines above towards | 2026-08-07 17:41:05 |
| 2026-08-07 18:10:00 | 2026-08-07 17:04:10 LONG | HIGH, upwards | 2026-08-07 17:59:00 | none | - | 2 of 30 | 15 of 30 | - | - | - | - | - | 2026-08-07 18:10:00 | REV-TRADE at the event, FDM_XCAD_NONE | - | no line is away with its 2 lines above towards | 2026-08-07 18:16:05 |
| 2026-08-07 18:42:00 | 2026-08-07 18:10:10 SHORT | LOW, downwards | 2026-08-07 18:41:00 | ws2r | ws3, ws4 | 2 of 30 | 22 of 30 | ws3, ws4 | ws5, ws6 | 2026-08-07 18:45:40 | 2026-08-07 18:47:35 | ws2r | - | held | - | the seam+15s bar 2026-08-07 18:48:10 failed (ws6 of the 2 lines above are not away yet) and the 10.0 min walk to 2026-08-07 18:58:10 never passed | 2026-08-07 18:56:50 |
| 2026-08-07 18:46:00 | 2026-08-07 18:10:10 SHORT | LOW, downwards | 2026-08-07 18:43:00 | ws2r | ws3, ws4 | 3 of 30 | 22 of 30 | ws3, ws4, ws5 | ws6, ws7 | 2026-08-07 18:47:00 | 2026-08-07 18:48:55 | ws2Mage | - | held | - | the seam+15s bar 2026-08-07 18:50:10 failed (ws6, ws7 of the 2 lines above are not away yet) and the 10.0 min walk to 2026-08-07 19:00:10 never passed | 2026-08-07 18:56:50 |
| 2026-08-07 19:05:00 | 2026-08-07 18:49:05 LONG | HIGH, upwards | 2026-08-07 19:02:00 | none | - | 1 of 30 | 25 of 30 | - | - | - | - | - | 2026-08-07 19:05:00 | REV-TRADE at the event, FDM_XCAD_NONE | - | no line is away with its 2 lines above towards | 2026-08-07 19:32:00 |
| 2026-08-07 20:12:00 | 2026-08-07 19:30:40 SHORT | LOW, downwards | 2026-08-07 20:00:00 | none | - | 4 of 30 | 19 of 30 | - | - | - | - | - | 2026-08-07 20:12:00 | REV-TRADE at the event, FDM_XCAD_NONE | - | no line is away with its 2 lines above towards | 2026-08-07 20:45:20 |

## the emerging values his update 2 collected, per cadence event
# read at the seam+15s bar, or at the bar the 10.0 min walk truncated on
# `at the cadence event` is what "tagged" means - a clause-one line already away there is asking nothing new of itself
# the gap is the side extremum since the trade opened, minus the emerging value

| the cadence event | the bar read | the clause | the line | its emerging value | its own target-side extremum | that extreme was set | the gap | its last reversal | ex-20/80 here | at the cadence event | here |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-07 13:07:00 | 2026-08-07 13:12:10 | one - the 2 above | ws7r | 29.3028 | 15.0303 | 2026-08-07 13:04:00 | +14.2725 | 2026-08-07 13:10:00 | no | towards | away |
| 2026-08-07 13:07:00 | 2026-08-07 13:12:10 | one - the 2 above | ws8r | 33.0598 | 25.7909 | 2026-08-07 13:04:00 | +7.2689 | 2026-08-07 13:10:00 | no | towards | away |
| 2026-08-07 13:07:00 | 2026-08-07 13:12:10 | two - the ex-20/80 towards lines | ws5r | 38.4428 | 13.7706 | 2026-08-07 13:00:15 | +24.6722 | 2026-08-07 13:10:00 | no | towards | away |
| 2026-08-07 13:07:00 | 2026-08-07 13:12:10 | two - the ex-20/80 towards lines | ws6r | 25.9681 | 2.2858 | 2026-08-07 13:06:00 | +23.6823 | 2026-08-07 13:10:00 | no | towards | away |
| 2026-08-07 13:37:00 | 2026-08-07 13:48:10 | one - the 2 above | ws6r | 90.2155 | 98.0322 | 2026-08-07 13:42:00 | +7.8167 | 2026-08-07 13:46:50 | yes | towards | away |
| 2026-08-07 13:37:00 | 2026-08-07 13:48:10 | one - the 2 above | ws7r | 89.4519 | - | - | - | - | yes | towards | towards |
| 2026-08-07 13:37:00 | 2026-08-07 13:48:10 | two - the ex-20/80 towards lines | ws3r | 70.6302 | 95.3962 | 2026-08-07 13:45:05 | +24.7660 | 2026-08-07 13:46:20 | no | towards | away |
| 2026-08-07 13:37:00 | 2026-08-07 13:48:10 | two - the ex-20/80 towards lines | ws4r | 73.1037 | 95.3817 | 2026-08-07 13:40:00 | +22.2781 | 2026-08-07 13:46:05 | no | towards | away |
| 2026-08-07 13:37:00 | 2026-08-07 13:48:10 | two - the ex-20/80 towards lines | ws5r | 85.3888 | 94.5223 | 2026-08-07 13:45:05 | +9.1335 | 2026-08-07 13:46:05 | yes | towards | away |
| 2026-08-07 13:46:00 | 2026-08-07 14:03:10 | one - the 2 above | ws7r | 86.4483 | 96.2157 | 2026-08-07 13:53:05 | +9.7674 | 2026-08-07 14:00:00 | yes | towards | away |
| 2026-08-07 13:46:00 | 2026-08-07 14:03:10 | one - the 2 above | ws8r | 74.7871 | 77.2104 | 2026-08-07 13:58:00 | +2.4233 | 2026-08-07 14:01:35 | no | towards | away |
| 2026-08-07 13:46:00 | 2026-08-07 14:03:10 | two - the ex-20/80 towards lines | ws3r | 15.5584 | 95.3962 | 2026-08-07 13:45:05 | +79.8378 | 2026-08-07 13:46:20 | no | towards | away |
| 2026-08-07 13:46:00 | 2026-08-07 14:03:10 | two - the ex-20/80 towards lines | ws4r | 36.8123 | 95.3817 | 2026-08-07 13:40:00 | +58.5694 | 2026-08-07 13:46:05 | no | towards | away |
| 2026-08-07 13:46:00 | 2026-08-07 14:03:10 | two - the ex-20/80 towards lines | ws6r | 75.4605 | 98.0322 | 2026-08-07 13:42:00 | +22.5717 | 2026-08-07 13:54:35 | no | towards | away |
| 2026-08-07 16:11:00 | 2026-08-07 16:18:10 | one - the 2 above | ws11r | 85.4184 | - | - | - | - | yes | towards | towards |
| 2026-08-07 16:11:00 | 2026-08-07 16:18:10 | one - the 2 above | ws12r | 84.2088 | - | - | - | - | yes | towards | towards |
| 2026-08-07 16:11:00 | 2026-08-07 16:18:10 | two - the ex-20/80 towards lines | ws9r | 82.4228 | 92.0452 | 2026-08-07 16:13:25 | +9.6225 | 2026-08-07 16:17:15 | yes | towards | away |
| 2026-08-07 16:11:00 | 2026-08-07 16:18:10 | two - the ex-20/80 towards lines | ws10r | 89.1655 | 95.0495 | 2026-08-07 16:10:00 | +5.8840 | 2026-08-07 16:17:20 | yes | towards | away |
| 2026-08-07 18:42:00 | 2026-08-07 18:48:10 | one - the 2 above | ws5r | 19.9052 | 14.8112 | 2026-08-07 18:45:00 | +5.0939 | 2026-08-07 18:46:35 | yes | towards | away |
| 2026-08-07 18:42:00 | 2026-08-07 18:48:10 | one - the 2 above | ws6r | 28.1750 | - | - | - | - | no | towards | towards |
| 2026-08-07 18:42:00 | 2026-08-07 18:48:10 | two - the ex-20/80 towards lines | ws3r | 25.3282 | 11.3645 | 2026-08-07 18:42:00 | +13.9637 | 2026-08-07 18:46:05 | no | towards | away |
| 2026-08-07 18:42:00 | 2026-08-07 18:48:10 | two - the ex-20/80 towards lines | ws4r | 14.3129 | 5.6031 | 2026-08-07 18:44:40 | +8.7098 | 2026-08-07 18:46:10 | yes | towards | away |
| 2026-08-07 18:46:00 | 2026-08-07 18:50:10 | one - the 2 above | ws6r | 32.6004 | - | - | - | - | no | towards | towards |
| 2026-08-07 18:46:00 | 2026-08-07 18:50:10 | one - the 2 above | ws7r | 39.6737 | - | - | - | - | no | away | towards |
| 2026-08-07 18:46:00 | 2026-08-07 18:50:10 | two - the ex-20/80 towards lines | ws3r | 29.1859 | 11.3645 | 2026-08-07 18:43:00 | +17.8215 | 2026-08-07 18:46:05 | no | towards | away |
| 2026-08-07 18:46:00 | 2026-08-07 18:50:10 | two - the ex-20/80 towards lines | ws4r | 18.7083 | 5.6031 | 2026-08-07 18:44:40 | +13.1052 | 2026-08-07 18:46:10 | yes | towards | away |
| 2026-08-07 18:46:00 | 2026-08-07 18:50:10 | two - the ex-20/80 towards lines | ws5r | 25.6054 | 14.8112 | 2026-08-07 18:45:00 | +10.7941 | 2026-08-07 18:48:50 | no | towards | away |

| the director roll-up | value |
|---|---|
| legs walked | 16 |
| cadence events | 14 |
| events with a candidate | 6 |
| events with no candidate | 8 |
| events whose seam read or walk sent a rev-trade | 2 |
