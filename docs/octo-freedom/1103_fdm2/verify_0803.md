# fdm2 | TAPE 1632960 bars, ends 2026-10-04 23:59:55 | RULED_OK True | the walk runs to 2026-10-04 23:59:55
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
| 2026-08-03 01:28:00 | WALK | cadence event, 10 of 27 lines printing ex-20/80 AND towards -> walk. the next cadence event is first (ws10x 2026-08-03 01:43:45 to ws10Mage) |
| 2026-08-03 01:42:00 | WALK | cadence event, 10 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x 2026-08-03 01:44:05 to ib) |
| 2026-08-03 01:44:05 | NO ACTION | ws10x-cadence to ib, 4 of 23 reversed since 2026-08-03 01:42:00 = 17.4% < 40% - no branch, wait for the next cadence |
| 2026-08-03 02:59:00 | WALK | cadence event, 3 of 27 lines printing ex-20/80 AND towards -> walk. the ws10x-cadence is first (ws10x 2026-08-03 03:01:35 to ws10Mage) |
| 2026-08-03 03:01:35 | REV-TRADE | ws10x-cadence to ws10Mage, 18 of 25 reversed since 2026-08-03 02:59:00 = 72.0% >= 50% at the cadence itself |

## the legs | every number carries the FDM_MAE_CAP 1.10% stop

| the open | the trade | the rev-trade signal | the exit | the exit kind | held min | MAE% | MFE% | realised% |
|---|---|---|---|---|---|---|---|---|
| 2026-08-03 00:41:35 | SHORT | 2026-08-03 03:01:35 | 2026-08-03 03:01:40 | rev-trade | 140.1 | 0.140 | 1.615 | +1.249 |

| the aggregate | value |
|---|---|
| legs | 1 |
| stopped | 0 |
| gross % | +1.249 |
| drag % | -0.198 (0.1975% round trip x 1 legs) |
| net % | +1.051 |
| MAE % total | 0.140 |
| MFE % total | 1.615 |
| MFE captured | 77.3% of MFE |
| held min, shortest .. longest | 140.1 .. 140.1 |

## his 08-03 cases through v4_fdm2 | ws10x hold FDM_X10_WOB 24 bars = 120 s | the reversal STAMP, population frozen at the ws10x-cadence

| the trade | target side | the cadence event | step 1 | the ws10x-cadence | which | reversed, STAMP | pct, STAMP | reversed, RAW lift bar | pct, RAW | the branch |
|---|---|---|---|---|---|---|---|---|---|---|
| 0702 | LOW | 2026-08-03 07:03:00 | 2 of 27 | 2026-08-03 07:12:20 | ib | 3 of 3 | 100.0% | 3 of 3 | 100.0% | REV-TRADE at the ws10x |
| 0702 | HIGH | 2026-08-03 09:12:00 | 3 of 27 | 2026-08-03 09:33:10 | ws10Mage | 10 of 11 | 90.9% | 10 of 11 | 90.9% | REV-TRADE at the ws10x |
| 1008 | HIGH | 2026-08-03 10:09:00 | 15 of 27 | 2026-08-03 10:11:55 | ws10Mage | 4 of 18 | 22.2% | 8 of 18 | 44.4% | no action |
| 1315 | LOW | 2026-08-03 13:16:00 | 6 of 27 | 2026-08-03 13:18:55 | ws10Mage | 5 of 6 | 83.3% | 3 of 6 | 50.0% | REV-TRADE at the ws10x |
| 1406 | HIGH | 2026-08-03 14:07:00 | 5 of 27 | 2026-08-03 14:15:45 | ib | 8 of 8 | 100.0% | 7 of 8 | 87.5% | REV-TRADE at the ws10x |
| 1644 | LOW | none in 2026-08-03 16:44:00 .. 2026-08-03 18:41:00 | - | - | - | - | - | - | - | - |
| 1841 | HIGH | 2026-08-03 18:42:00 | 10 of 27 | 2026-08-03 18:51:55 | ws10r | 9 of 12 | 75.0% | 10 of 12 | 83.3% | REV-TRADE at the ws10x |
| 1841 | HIGH | 2026-08-03 21:03:00 | 0 of 27 | 2026-08-03 21:10:35 | ws10r | 12 of 18 | 66.7% | 9 of 18 | 50.0% | REV-TRADE at the cadence event, 0 of 27 |
| 1841 | HIGH | 2026-08-03 23:01:00 | 3 of 27 | 2026-08-03 23:03:35 | ib | 7 of 21 | 33.3% | 7 of 21 | 33.3% | no action |
