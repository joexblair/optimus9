# fdm2 | TAPE 1632960 bars, ends 2026-10-04 23:59:55 | RULED_OK True
# THE WALK RUNS 2026-07-02 12:00:00 .. 2026-10-04 23:59:55 - the whole tape
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


## the banked re-entry | the ws5/ws6 reversal walk | 2026-08-07 00:00:00 .. 2026-08-07 23:59:55
# the window is arm E: ws1b oob AND gcws30b ex-5/95, same side, paired with its own ws1b ib close
# the reversal read is closed_prev, the ws6r gate is ex2080, the ws5r fence is 20/80, the scan band is ws7..ws12, the ib close is IN the last-to-fire set
# the open is the signal bar + 1, the router's "just OPEN, 1 bar"
# NO STOP AND NO EXIT RULE ON THESE NUMBERS: the scale is sweep-pivots, from the open
# sweep-pivots: SP_PICK lowest_pct, SP_BAND 0.0, SP_CONTAIN 0, SP_XWOB 18, SP_ALIGN_S 300, SP_TFS wide

| the window open | the oob side | the window close, ws1b ib | the ws5 reversal | ws5r there | ws6r there | the ws6 branch | the ws6 reversal | the scan bar | in-fence ws7..ws12 | the last to fire | the signal bar | the trade | its open | MAE % | MFE % | the scale TF | the leg close | the leg MFE % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-07 06:53:00 | LOW | 2026-08-07 06:55:00 | 2026-08-07 07:10:35 | 17.07 | 43.41 | failed, scanned at once | - | 2026-08-07 07:10:35 | ws7, ws8, ws9, ws10, ws11, ws12 | HIS MOD - ws5x crossed ws5r 2026-08-07 06:56:45 and held 12 bars to 2026-08-07 06:57:40, ws5r 12.52 past 20, ws6r 63.92 in-fence | 2026-08-07 06:57:40 | LONG | 2026-08-07 06:57:45 | -0.265 | +0.374 | ws1Mage | 2026-08-07 07:20:50 | 0.641 |
| 2026-08-07 08:00:00 | LOW | 2026-08-07 08:01:00 | 2026-08-07 08:10:35 | 14.81 | 22.87 | failed, scanned at once | - | 2026-08-07 08:10:35 | ws8, ws9, ws10, ws11, ws12 | HIS MOD - ws5x crossed ws5r 2026-08-07 08:02:25 and held 12 bars to 2026-08-07 08:03:20, ws5r 8.88 past 20, ws6r 26.34 in-fence | 2026-08-07 08:03:20 | LONG | 2026-08-07 08:03:25 | -0.109 | +0.203 | ws1Mage | 2026-08-07 08:16:30 | 0.313 |
| 2026-08-07 08:43:00 | HIGH | 2026-08-07 08:51:00 | 2026-08-07 09:30:35 | 81.91 | 69.82 | failed, scanned at once | - | 2026-08-07 09:30:35 | ws10, ws11, ws12 | HIS MOD - ws5x crossed ws5r 2026-08-07 08:55:30 and held 12 bars to 2026-08-07 08:56:25, ws5r 84.69 past 80, ws6r 75.79 in-fence | 2026-08-07 08:56:25 | SHORT | 2026-08-07 08:56:30 | -1.153 | +0.693 | ws30Mage | 2026-08-07 14:20:20 | 1.309 |
| 2026-08-07 09:03:30 | HIGH | 2026-08-07 09:05:00 | 2026-08-07 09:30:35 | 81.91 | 69.82 | failed, scanned at once | - | 2026-08-07 09:30:35 | ws10, ws11, ws12 | the ws5 reversal | 2026-08-07 09:30:35 | SHORT | 2026-08-07 09:30:40 | -0.988 | +0.856 | ws30Mage | 2026-08-07 14:20:20 | 1.309 |
| 2026-08-07 09:09:00 | HIGH | 2026-08-07 09:10:00 | 2026-08-07 09:30:35 | 81.91 | 69.82 | failed, scanned at once | - | 2026-08-07 09:30:35 | ws10, ws11, ws12 | the ws5 reversal | 2026-08-07 09:30:35 | SHORT | 2026-08-07 09:30:40 | -0.988 | +0.856 | ws30Mage | 2026-08-07 14:20:20 | 1.309 |
| 2026-08-07 09:12:00 | HIGH | 2026-08-07 09:14:00 | 2026-08-07 09:30:35 | 81.91 | 69.82 | failed, scanned at once | - | 2026-08-07 09:30:35 | ws10, ws11, ws12 | the ws5 reversal | 2026-08-07 09:30:35 | SHORT | 2026-08-07 09:30:40 | -0.988 | +0.856 | ws30Mage | 2026-08-07 14:20:20 | 1.309 |
| 2026-08-07 09:25:30 | HIGH | 2026-08-07 09:27:00 | 2026-08-07 09:30:35 | 81.91 | 69.82 | failed, scanned at once | - | 2026-08-07 09:30:35 | ws10, ws11, ws12 | the ws5 reversal | 2026-08-07 09:30:35 | SHORT | 2026-08-07 09:30:40 | -0.988 | +0.856 | ws30Mage | 2026-08-07 14:20:20 | 1.309 |
| 2026-08-07 10:17:30 | LOW | 2026-08-07 10:19:00 | 2026-08-07 10:30:35 | 9.99 | 13.36 | held, waited | 2026-08-07 10:36:35 | 2026-08-07 10:36:35 | ws8, ws9, ws10, ws11, ws12 | the ws6 reversal | 2026-08-07 10:36:35 | LONG | 2026-08-07 10:36:40 | -0.334 | +0.350 | ws3Mage | 2026-08-07 11:10:40 | 0.522 |
| 2026-08-07 13:33:00 | HIGH | 2026-08-07 13:34:00 | 2026-08-07 13:50:35 | 86.63 | 95.20 | held, waited | 2026-08-07 13:54:35 | 2026-08-07 13:54:35 | ws8, ws9, ws10, ws11, ws12 | HIS MOD - ws6 waiting: ws6x crossed ws6r 2026-08-07 13:51:15 and held 12 bars to 2026-08-07 13:52:10, ws6r 94.07 past 80, ws7r 77.52 in-fence | 2026-08-07 13:52:10 | SHORT | 2026-08-07 13:52:15 | -0.256 | +0.769 | ws10Mage | 2026-08-07 13:07:10 | 0.823 |
| 2026-08-07 13:35:00 | HIGH | 2026-08-07 13:37:00 | 2026-08-07 13:50:35 | 86.63 | 95.20 | held, waited | 2026-08-07 13:54:35 | 2026-08-07 13:54:35 | ws8, ws9, ws10, ws11, ws12 | HIS MOD - ws6 waiting: ws6x crossed ws6r 2026-08-07 13:51:15 and held 12 bars to 2026-08-07 13:52:10, ws6r 94.07 past 80, ws7r 77.52 in-fence | 2026-08-07 13:52:10 | SHORT | 2026-08-07 13:52:15 | -0.256 | +0.769 | ws10Mage | 2026-08-07 13:07:10 | 0.823 |
| 2026-08-07 13:39:30 | HIGH | 2026-08-07 13:46:00 | 2026-08-07 13:50:35 | 86.63 | 95.20 | held, waited | 2026-08-07 13:54:35 | 2026-08-07 13:54:35 | ws8, ws9, ws10, ws11, ws12 | HIS MOD - ws6 waiting: ws6x crossed ws6r 2026-08-07 13:51:15 and held 12 bars to 2026-08-07 13:52:10, ws6r 94.07 past 80, ws7r 77.52 in-fence | 2026-08-07 13:52:10 | SHORT | 2026-08-07 13:52:15 | -0.256 | +0.769 | ws10Mage | 2026-08-07 13:07:10 | 0.823 |
| 2026-08-07 14:40:00 | LOW | 2026-08-07 14:41:00 | 2026-08-07 15:10:35 | 19.52 | 28.48 | failed, scanned at once | - | 2026-08-07 15:10:35 | ws7, ws9, ws11, ws12 | HIS MOD - ws5x crossed ws5r 2026-08-07 15:05:00 and held 12 bars to 2026-08-07 15:05:55, ws5r 7.37 past 20, ws6r 32.21 in-fence | 2026-08-07 15:05:55 | LONG | 2026-08-07 15:06:00 | -0.047 | +1.255 | ws2Mage | 2026-08-07 15:45:45 | 1.247 |
| 2026-08-07 14:44:30 | LOW | 2026-08-07 15:06:00 | 2026-08-07 15:10:35 | 19.52 | 28.48 | failed, scanned at once | - | 2026-08-07 15:10:35 | ws7, ws9, ws11, ws12 | HIS MOD - ws5x crossed ws5r 2026-08-07 15:05:00 and held 12 bars to 2026-08-07 15:05:55, ws5r 7.37 past 20, ws6r 32.21 in-fence | 2026-08-07 15:06:00 | LONG | 2026-08-07 15:06:05 | -0.063 | +1.239 | ws2Mage | 2026-08-07 15:45:45 | 1.247 |
| 2026-08-07 15:32:30 | HIGH | 2026-08-07 15:34:00 | 2026-08-07 15:50:35 | 96.15 | 97.48 | held, waited | 2026-08-07 15:54:35 | 2026-08-07 15:54:35 | ws9, ws10, ws11, ws12 | the ws6 reversal | 2026-08-07 15:54:35 | SHORT | 2026-08-07 15:54:40 | -0.611 | +0.071 | ws2Mage | 2026-08-07 16:57:50 | 0.678 |
| 2026-08-07 19:02:00 | HIGH | 2026-08-07 19:05:00 | 2026-08-07 19:30:35 | 89.24 | 78.37 | failed, scanned at once | - | 2026-08-07 19:30:35 | ws7, ws8, ws9, ws10, ws11, ws12 | HIS MOD - ws5x crossed ws5r 2026-08-07 19:20:45 and held 12 bars to 2026-08-07 19:21:40, ws5r 94.99 past 80, ws6r 58.07 in-fence | 2026-08-07 19:21:40 | SHORT | 2026-08-07 19:21:45 | -0.202 | +1.539 | ws10Mage | 2026-08-07 20:08:00 | 1.631 |
| 2026-08-07 19:15:00 | HIGH | 2026-08-07 19:21:00 | 2026-08-07 19:30:35 | 89.24 | 78.37 | failed, scanned at once | - | 2026-08-07 19:30:35 | ws7, ws8, ws9, ws10, ws11, ws12 | HIS MOD - ws5x crossed ws5r 2026-08-07 19:20:45 and held 12 bars to 2026-08-07 19:21:40, ws5r 94.99 past 80, ws6r 58.07 in-fence | 2026-08-07 19:21:40 | SHORT | 2026-08-07 19:21:45 | -0.202 | +1.539 | ws10Mage | 2026-08-07 20:08:00 | 1.631 |
| 2026-08-07 20:00:00 | LOW | 2026-08-07 20:12:00 | 2026-08-07 20:15:35 | 6.48 | 13.16 | held, waited | 2026-08-07 20:24:35 | 2026-08-07 20:24:35 | ws7, ws8, ws9, ws10, ws11, ws12 | HIS MOD - ws6 waiting: ws6x crossed ws6r 2026-08-07 20:21:45 and held 12 bars to 2026-08-07 20:22:40, ws6r 12.87 past 20, ws7r 24.35 in-fence | 2026-08-07 20:22:40 | LONG | 2026-08-07 20:22:45 | -0.976 | +0.039 | ws1Mage | 2026-08-07 21:17:10 | 1.192 |
| 2026-08-07 22:53:00 | HIGH | 2026-08-07 22:54:00 | 2026-08-07 23:20:35 | 82.76 | 91.44 | held, waited | 2026-08-07 23:24:35 | 2026-08-07 23:24:35 | ws7, ws9 | HIS MOD - ws6 waiting: ws6x crossed ws6r 2026-08-07 23:21:30 and held 12 bars to 2026-08-07 23:22:25, ws6r 89.41 past 80, ws7r 78.60 in-fence | 2026-08-07 23:22:25 | SHORT | 2026-08-07 23:22:30 | -0.024 | +0.405 | ws2Mage | 2026-08-07 23:32:15 | 0.469 |
| 2026-08-07 23:14:00 | HIGH | 2026-08-07 23:18:00 | 2026-08-07 23:20:35 | 82.76 | 91.44 | held, waited | 2026-08-07 23:24:35 | 2026-08-07 23:24:35 | ws7, ws9 | HIS MOD - ws6 waiting: ws6x crossed ws6r 2026-08-07 23:21:30 and held 12 bars to 2026-08-07 23:22:25, ws6r 89.41 past 80, ws7r 78.60 in-fence | 2026-08-07 23:22:25 | SHORT | 2026-08-07 23:22:30 | -0.024 | +0.405 | ws2Mage | 2026-08-07 23:32:15 | 0.469 |

| the population | value |
|---|---|
| re-entry signals in the span | 19 |
| of those, HIGH oob | 13 |
| of those, LOW oob | 6 |
| distinct open bars | 12 |
| last to fire was the ws5 reversal | 4 |
| last to fire was the ws6 reversal | 2 |
| last to fire was the ws1b ib close | 0 |
| ws6r held the gate so the walk waited | 8 |
| ws6r failed the gate so the scan ran at once | 11 |

| the MAE/MFE per DISTINCT open, the open bar to the leg close | value |
|---|---|
| distinct opens scored | 12 |
| sum MAE % | -5.030 |
| sum MFE % | +7.795 |
| median MAE % | -0.256 |
| median MFE % | +0.693 |
| worst MAE % | -1.153 |
| best MFE % | +1.539 |
| MFE > abs(MAE) | 8 of 12 |
| MAE past -1.10%, the fdm2 stop - NOT applied here | 1 of 12 |
| median leg MFE % | 1.192 |
| the MFE as a share of the leg MFE, median of 12 | 67.0% |
| the realised at the leg close, sum % | +4.962 |
| the realised at the leg close, per open % | +0.4135 |
| the round trip it has to beat % | 0.1975 |
| opens whose realised cleared the round trip | 8 of 12 |
| median realised % | +0.311 |
| the span | the open bar to the bar sweep-pivots ends the leg on - NOT a horizon chosen here |
