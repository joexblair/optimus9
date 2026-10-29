# THE LEG REPORT - ALL FOUR LINES LIVE, THE EX-FENCE LATCH ON, ws1b HOLD 0
# WINDOW 2026-08-30 00:00:00 .. 2026-08-30 23:59:55 | TAPE 1632960 bars | RULED_OK True
# prev-close is OUT of the walk: ws1b, ws1r, ws1Mage and ws2Mage are all the live read.
# the ex-fence latch hold is 4 bars = 20 s. the ws1b hold is 0 - his "wob 0 until we sweep".
# the open is 2026-08-29 23:53:55 SHORT, the router fire bar off the lin2-reentry signal 2026-08-29 23:53:50.
# the 1.1% stop is OFF. drag 0.1975% per round trip, its own column and its own total.
# baton candidates: every candidate timeframe offered at that bar with its value.
# "none offered" is a hand-over attempt with no candidate inside lin_hop 2.
# exfnc ltchd: every ws1..ws12 line whose ex-fence latch is ON at that bar, on this leg's side.
# barrage: the most recent barrage on this leg's side at or before that bar, and the counter-side one when it is newer.
# a row whose bar carried a cadence starts **CADENCE:**.

## leg 1 of 15 - 2026-08-29 SHORT   opens 2026-08-29 23:53:55   exits 2026-08-30 02:27:50 on t1   MAE 0.5088   MFE 1.9536   realised +1.5415   held 153.9 min   CONTINUITY: the chain opens here

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-29 23:53:55 | >>> THIS LEG OPENS SHORT | - | 7: ws2,ws5,ws6,ws7,ws8,ws9,ws11 | last 04:23:10, 1170.8 min ago / counter-side 14:28:50 | 0.196560 | -0.0000 |
| 2026-08-30 00:18:15 | the ADVERSE extreme - MAE 0.5088 | - | 6: ws2,ws6,ws7,ws8,ws9,ws11 | last 04:23:10, 1195.1 min ago / counter-side 14:28:50 | 0.197560 | -0.5088 |
| 2026-08-30 01:01:00 | ARM - cws1b+cws1r: cws1b 2.06 + cws1r 10.24 oob | - | 7: ws1,ws2,ws6,ws7,ws8,ws9,ws11 | last 04:23:10, 1237.8 min ago / counter-side 14:28:50 | 0.195190 | +0.6970 |
| 2026-08-30 01:01:00 | RIDER rider cws11 - cws11 r 33.33, the highest ex-fence | - | 7: ws1,ws2,ws6,ws7,ws8,ws9,ws11 | last 04:23:10, 1237.8 min ago / counter-side 14:28:50 | 0.195190 | +0.6970 |
| 2026-08-30 01:01:00 | RETEST - cws1r 10.24 oob + cws2r 23.07 / cws3r 36.91 in - the gate opens; cws1r oob->ib cross 2026-08-30 01:03:35, wob 12, cadence at 2026-08-30 01:04:30 | - | 7: ws1,ws2,ws6,ws7,ws8,ws9,ws11 | last 04:23:10, 1237.8 min ago / counter-side 14:28:50 | 0.195190 | +0.6970 |
| 2026-08-30 01:04:30 | **CADENCE:** RIDER rider cws11 - v4-arm-lineage-retest: the re-scan rides cws11 33.33, the highest ex-fence | - | 7: ws1,ws2,ws6,ws7,ws8,ws9,ws11 | last 04:23:10, 1241.3 min ago / counter-side 14:28:50 | 0.195260 | +0.6614 |
| 2026-08-30 01:16:50 | the favourable extreme - MFE 1.9536 | - | 10: ws1,ws2,ws3,ws4,ws5,ws6,ws7,ws8,ws9,ws11 | last 04:23:10, 1253.7 min ago / counter-side 14:28:50 | 0.192720 | +1.9536 |
| 2026-08-30 01:20:50 | LATCH1 rider cws11 - latch 1 at the t1 cadence 2026-08-30 01:20:50, divergence state -1 | - | 11: ws1,ws2,ws3,ws4,ws5,ws6,ws7,ws8,ws9,ws10,ws11 | last 04:23:10, 1257.7 min ago / counter-side 14:28:50 | 0.193890 | +1.3584 |
| 2026-08-30 01:20:50 | **CADENCE:** NO ACTION rider cws11 - t1 cws1b oob 01:15:45..01:20:45, cws1r reversed 01:19:15 during, stamp 01:19:15 \| mage-cascade down matches the SHORT - no action, keep walking | - | 11: ws1,ws2,ws3,ws4,ws5,ws6,ws7,ws8,ws9,ws10,ws11 | last 04:23:10, 1257.7 min ago / counter-side 14:28:50 | 0.193890 | +1.3584 |
| 2026-08-30 01:23:55 | NO ACTION rider cws11 - latch latch 2: rider cws11 reversed raw 2026-08-30 01:20:10 stamp 2026-08-30 01:21:05, no candidate inside lin_hop, support ws8 raw 2026-08-30 01:22:50 stamp 2026-08-30 01:23:45, ws9 raw 2026-08-30 01:23:00 stamp 2026-08-30 01:23:55, ws10 raw 2026-08-30 01:22:20 stamp 2026-08-30 01:23:15 \| latch 1 at the t1 cadence 2026-08-30 01:20:50, divergence state -1 \| mage-cascade down matches the SHORT - no action, keep walking | - | 11: ws1,ws2,ws3,ws4,ws5,ws6,ws7,ws8,ws9,ws10,ws11 | last 04:23:10, 1260.8 min ago / counter-side 14:28:50 | 0.194290 | +1.1549 |
| 2026-08-30 01:45:55 | **CADENCE:** NO ACTION rider cws11 - t2 cws1r ib cross 01:45:00 confirmed 01:45:55 at wob 12, cws1b 60.31 not oob, ws1b hold 0 \| mage-cascade down matches the SHORT - no action, keep walking | - | 9: ws1,ws5,ws6,ws7,ws8,ws9,ws10,ws11,ws12 | last 04:23:10, 1282.8 min ago / counter-side 14:28:50 | 0.194680 | +0.9565 |
| 2026-08-30 01:59:55 | LATCH1 rider cws11 - latch 1 at the t2 cadence 2026-08-30 01:59:55, divergence state -1 | - | 10: ws1,ws2,ws5,ws6,ws7,ws8,ws9,ws10,ws11,ws12 | last 04:23:10, 1296.8 min ago / counter-side 14:28:50 | 0.193910 | +1.3482 |
| 2026-08-30 01:59:55 | **CADENCE:** NO ACTION rider cws11 - t2 cws1r ib cross 01:59:00 confirmed 01:59:55 at wob 12, cws1b 39.39 not oob, ws1b hold 0 \| mage-cascade down matches the SHORT - no action, keep walking | - | 10: ws1,ws2,ws5,ws6,ws7,ws8,ws9,ws10,ws11,ws12 | last 04:23:10, 1296.8 min ago / counter-side 14:28:50 | 0.193910 | +1.3482 |
| 2026-08-30 02:16:05 | LATCH1 rider cws11 - latch 1 at the t1 cadence 2026-08-30 02:16:05, divergence state -1 | - | 9: ws1,ws2,ws3,ws7,ws8,ws9,ws10,ws11,ws12 | last 04:23:10, 1312.9 min ago / counter-side 14:28:50 | 0.193750 | +1.4296 |
| 2026-08-30 02:16:05 | **CADENCE:** NO ACTION rider cws11 - t1 cws1b ib 02:15:55, cws1r reversed 02:16:05 inside the 120s grace, stamp 02:16:05 \| mage-cascade down matches the SHORT - no action, keep walking | - | 9: ws1,ws2,ws3,ws7,ws8,ws9,ws10,ws11,ws12 | last 04:23:10, 1312.9 min ago / counter-side 14:28:50 | 0.193750 | +1.4296 |
| 2026-08-30 02:27:50 | **CADENCE:** EXHAUST rider cws11 - t1 cws1b ib 02:27:35, cws1r reversed 02:27:50 inside the 120s grace, stamp 02:27:50 \| mage-cascade up OPPOSES the SHORT - rev-trade | - | 9: ws1,ws2,ws3,ws7,ws8,ws9,ws10,ws11,ws12 | last 04:23:10, 1324.7 min ago / counter-side 14:28:50 | 0.193530 | +1.5415 |
| 2026-08-30 02:27:50 | THIS LEG CLOSES on t1, realised +1.5415 | - | 9: ws1,ws2,ws3,ws7,ws8,ws9,ws10,ws11,ws12 | last 04:23:10, 1324.7 min ago / counter-side 14:28:50 | 0.193530 | +1.5415 |

## leg 2 of 15 - 2026-08-30 LONG   opens 2026-08-30 02:27:55   exits 2026-08-30 02:45:55 on t2   MAE 0.1188   MFE 0.5529   realised +0.2377   held 18.0 min   CONTINUITY: 1 bar after leg 1 exit 2026-08-30 02:27:50

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 02:27:55 | >>> THIS LEG OPENS LONG | - | 3: ws4,ws5,ws6 | last 14:28:50, 719.1 min ago | 0.193530 | +0.0000 |
| 2026-08-30 02:36:00 | the ADVERSE extreme - MAE 0.1188 | - | 2: ws4,ws6 | last 14:28:50, 727.2 min ago / counter-side 02:35:20 | 0.193300 | -0.1188 |
| 2026-08-30 02:42:00 | ARM - cws1b+cws1r: cws1b 108.27 + cws1r 89.24 oob | - | 3: ws1,ws4,ws6 | last 14:28:50, 733.2 min ago / counter-side 02:35:20 | 0.194450 | +0.4754 |
| 2026-08-30 02:42:00 | RIDER rider cws6 - cws6 r 51.01, the highest ex-fence | - | 3: ws1,ws4,ws6 | last 14:28:50, 733.2 min ago / counter-side 02:35:20 | 0.194450 | +0.4754 |
| 2026-08-30 02:42:00 | RETEST - cws1r 89.24 oob + cws2r 61.29 / cws3r 52.08 in - the gate opens; cws1r oob->ib cross 2026-08-30 02:45:00, wob 12, cadence at 2026-08-30 02:45:55 | - | 3: ws1,ws4,ws6 | last 14:28:50, 733.2 min ago / counter-side 02:35:20 | 0.194450 | +0.4754 |
| 2026-08-30 02:43:00 | the favourable extreme - MFE 0.5529 | - | 3: ws1,ws4,ws6 | last 14:28:50, 734.2 min ago / counter-side 02:35:20 | 0.194600 | +0.5529 |
| 2026-08-30 02:45:55 | **CADENCE:** RIDER rider cws6 - v4-arm-lineage-retest: the re-scan rides cws6 46.10, the highest ex-fence | - | 3: ws1,ws4,ws6 | last 14:28:50, 737.1 min ago / counter-side 02:35:20 | 0.193990 | +0.2377 |
| 2026-08-30 02:45:55 | **CADENCE:** EXHAUST rider cws6 - t2 cws1r ib cross 02:45:00 confirmed 02:45:55 at wob 12, cws1b 64.63 not oob, ws1b hold 0 \| mage-cascade down OPPOSES the LONG - rev-trade | - | 3: ws1,ws4,ws6 | last 14:28:50, 737.1 min ago / counter-side 02:35:20 | 0.193990 | +0.2377 |
| 2026-08-30 02:45:55 | THIS LEG CLOSES on t2, realised +0.2377 | - | 3: ws1,ws4,ws6 | last 14:28:50, 737.1 min ago / counter-side 02:35:20 | 0.193990 | +0.2377 |

## leg 3 of 15 - 2026-08-30 SHORT   opens 2026-08-30 02:46:00   exits 2026-08-30 04:41:00 on t1   MAE 0.3196   MFE 2.0568   realised +1.6393   held 115.0 min   CONTINUITY: 1 bar after leg 2 exit 2026-08-30 02:45:55

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 02:46:00 | >>> THIS LEG OPENS SHORT | - | 1: ws5 | last 02:35:20, 10.7 min ago | 0.193990 | -0.0000 |
| 2026-08-30 02:53:00 | the ADVERSE extreme - MAE 0.3196 | - | 2: ws1,ws5 | last 02:35:20, 17.7 min ago | 0.194610 | -0.3196 |
| 2026-08-30 03:00:30 | ARM - cws1b+cws1r: cws1b 8.49 + cws1r 7.68 oob | - | 3: ws1,ws2,ws5 | last 02:35:20, 25.2 min ago | 0.193210 | +0.4021 |
| 2026-08-30 03:00:30 | RIDER rider cws5 - cws5 r 46.75, the highest ex-fence | - | 3: ws1,ws2,ws5 | last 02:35:20, 25.2 min ago | 0.193210 | +0.4021 |
| 2026-08-30 03:00:30 | RETEST - cws2r 18.72 / cws3r 41.07 - not both inside the fence at the arm | - | 3: ws1,ws2,ws5 | last 02:35:20, 25.2 min ago | 0.193210 | +0.4021 |
| 2026-08-30 03:42:55 | LATCH1 rider cws5 - latch 1 at the t2 cadence 2026-08-30 03:42:55, divergence state -1 | - | 3: ws1,ws4,ws5 | last 02:35:20, 67.6 min ago | 0.192430 | +0.8042 |
| 2026-08-30 03:42:55 | **CADENCE:** NO ACTION rider cws5 - t2 cws1r ib cross 03:42:00 confirmed 03:42:55 at wob 12, cws1b 43.12 not oob, ws1b hold 0 \| mage-cascade down matches the SHORT - no action, keep walking | - | 3: ws1,ws4,ws5 | last 02:35:20, 67.6 min ago | 0.192430 | +0.8042 |
| 2026-08-30 03:53:55 | LATCH1 rider cws5 - latch 1 at the t2 cadence 2026-08-30 03:53:55, divergence state -1 | - | 6: ws1,ws2,ws4,ws5,ws8,ws10 | last 02:35:20, 78.6 min ago | 0.191670 | +1.1959 |
| 2026-08-30 03:53:55 | **CADENCE:** CADENCE rider cws5 - t2 cws1r ib cross 03:53:00 confirmed 03:53:55 at wob 12, cws1b 17.82 not oob, ws1b hold 0 \| rider cws5 62.26, no-longer-exfence no, reversed no \| mage-cascade neither | cws8: 23.30, cws10: 18.27 | 6: ws1,ws2,ws4,ws5,ws8,ws10 | last 02:35:20, 78.6 min ago | 0.191670 | +1.1959 |
| 2026-08-30 03:53:55 | **CADENCE:** BATON rider cws5 - ws5 -> ws10, at a t2 cadence, whole board | cws8: 23.30, cws10: 18.27 | 6: ws1,ws2,ws4,ws5,ws8,ws10 | last 02:35:20, 78.6 min ago | 0.191670 | +1.1959 |
| 2026-08-30 04:40:00 | the favourable extreme - MFE 2.0568 | - | 6: ws4,ws5,ws8,ws10,ws11,ws12 | last 02:35:20, 124.7 min ago | 0.190000 | +2.0568 |
| 2026-08-30 04:41:00 | **CADENCE:** EXHAUST rider cws10 - t1 cws1b oob 04:39:20..04:40:55, cws1r reversed 04:40:55 during, stamp 04:40:55 \| mage-cascade up OPPOSES the SHORT - rev-trade | - | 6: ws4,ws5,ws8,ws10,ws11,ws12 | last 02:35:20, 125.7 min ago | 0.190910 | +1.5877 |
| 2026-08-30 04:41:00 | THIS LEG CLOSES on t1, realised +1.6393 | - | 6: ws4,ws5,ws8,ws10,ws11,ws12 | last 02:35:20, 125.7 min ago | 0.190910 | +1.5877 |

## leg 4 of 15 - 2026-08-30 LONG   opens 2026-08-30 04:41:05   exits 2026-08-30 05:10:10 on t1   MAE 0.5712   MFE 0.8543   realised +0.5660   held 29.1 min   CONTINUITY: 1 bar after leg 3 exit 2026-08-30 04:41:00

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 04:41:05 | >>> THIS LEG OPENS LONG | - | 4: ws1,ws2,ws3,ws6 | last 14:28:50, 852.2 min ago / counter-side 02:35:20 | 0.190810 | +0.0000 |
| 2026-08-30 04:47:20 | the ADVERSE extreme - MAE 0.5712 | - | 4: ws1,ws2,ws3,ws6 | last 14:28:50, 858.5 min ago / counter-side 02:35:20 | 0.189720 | -0.5712 |
| 2026-08-30 05:03:15 | ARM - cws1b+cws1r: cws1b 99.46 + cws1r 85.53 oob | - | 3: ws1,ws2,ws6 | last 14:28:50, 874.4 min ago / counter-side 02:35:20 | 0.191660 | +0.4455 |
| 2026-08-30 05:03:15 | RIDER rider cws6 - cws6 r 76.23, the highest ex-fence | - | 3: ws1,ws2,ws6 | last 14:28:50, 874.4 min ago / counter-side 02:35:20 | 0.191660 | +0.4455 |
| 2026-08-30 05:03:15 | RETEST - cws1r 85.53 oob + cws2r 75.45 / cws3r 64.71 in - the gate opens; cws1r oob->ib cross 2026-08-30 05:06:00, wob 12, cadence at 2026-08-30 05:06:55 | - | 3: ws1,ws2,ws6 | last 14:28:50, 874.4 min ago / counter-side 02:35:20 | 0.191660 | +0.4455 |
| 2026-08-30 05:06:55 | **CADENCE:** RIDER rider cws6 - v4-arm-lineage-retest: the re-scan rides cws6 75.59, the highest ex-fence | - | 4: ws1,ws2,ws4,ws6 | last 14:28:50, 878.1 min ago / counter-side 02:35:20 | 0.191900 | +0.5712 |
| 2026-08-30 05:07:35 | the favourable extreme - MFE 0.8543 | - | 4: ws1,ws2,ws4,ws6 | last 14:28:50, 878.8 min ago / counter-side 02:35:20 | 0.192440 | +0.8543 |
| 2026-08-30 05:10:10 | **CADENCE:** EXHAUST rider cws6 - t1 cws1b oob 05:01:15..05:10:05, cws1r reversed 05:05:25 during, stamp 05:05:25 \| mage-cascade down OPPOSES the LONG - rev-trade | - | 5: ws1,ws2,ws3,ws4,ws6 | last 14:28:50, 881.3 min ago / counter-side 02:35:20 | 0.191880 | +0.5608 |
| 2026-08-30 05:10:10 | THIS LEG CLOSES on t1, realised +0.5660 | - | 5: ws1,ws2,ws3,ws4,ws6 | last 14:28:50, 881.3 min ago / counter-side 02:35:20 | 0.191880 | +0.5608 |

## leg 5 of 15 - 2026-08-30 SHORT   opens 2026-08-30 05:10:15   exits 2026-08-30 09:41:35 on t1   MAE 1.0787   MFE 1.4540   realised +1.1725   held 271.3 min   CONTINUITY: 1 bar after leg 4 exit 2026-08-30 05:10:10

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 05:10:15 | >>> THIS LEG OPENS SHORT | - | 5: ws5,ws8,ws10,ws11,ws12 | last 02:35:20, 154.9 min ago | 0.191890 | -0.0000 |
| 2026-08-30 06:59:15 | the ADVERSE extreme - MAE 1.0787 | - | 1: ws3 | last 02:35:20, 263.9 min ago | 0.193960 | -1.0787 |
| 2026-08-30 07:24:20 | ARM - cws4r: cws4r 6.72 oob | - | 3: ws1,ws2,ws3 | last 02:35:20, 289.0 min ago | 0.192250 | -0.1876 |
| 2026-08-30 07:24:20 | RIDER rider cws3 - cws3 r 12.22, the highest ex-fence | - | 3: ws1,ws2,ws3 | last 02:35:20, 289.0 min ago | 0.192250 | -0.1876 |
| 2026-08-30 07:24:20 | RETEST - cws2r 18.89 / cws3r 12.22 - not both inside the fence at the arm | - | 3: ws1,ws2,ws3 | last 02:35:20, 289.0 min ago | 0.192250 | -0.1876 |
| 2026-08-30 07:28:10 | BATON rider cws3 - ws3 -> ws5, between cadences, lin_hop 2 | cws4: 6.72, cws5: 14.87 | 5: ws1,ws2,ws3,ws4,ws5 | last 02:35:20, 292.8 min ago | 0.191760 | +0.0677 |
| 2026-08-30 07:54:10 | BATON rider cws5 - ws5 -> ws7, between cadences, lin_hop 2 | cws7: 13.52 | 8: ws2,ws3,ws4,ws5,ws6,ws7,ws8,ws10 | last 02:35:20, 318.8 min ago | 0.191710 | +0.0938 |
| 2026-08-30 07:56:55 | BATON rider cws7 - ws7 -> ws8, between cadences, lin_hop 2 | cws8: 15.93 | 7: ws3,ws4,ws5,ws6,ws7,ws8,ws10 | last 02:35:20, 321.6 min ago | 0.191640 | +0.1303 |
| 2026-08-30 08:03:15 | BATON rider cws8 - ws8 -> ws10, between cadences, lin_hop 2 | cws10: 13.08 | 6: ws4,ws5,ws6,ws7,ws8,ws10 | last 02:35:20, 327.9 min ago | 0.191690 | +0.1042 |
| 2026-08-30 08:10:55 | BATON rider cws10 - ws10 -> ws11, between cadences, lin_hop 2 | cws11: 13.89 | 7: ws5,ws6,ws7,ws8,ws9,ws10,ws11 | last 02:35:20, 335.6 min ago | 0.191300 | +0.3075 |
| 2026-08-30 08:15:55 | BATON rider cws11 - ws11 -> ws12, between cadences, lin_hop 2 | cws12: 12.78 | 8: ws5,ws6,ws7,ws8,ws9,ws10,ws11,ws12 | last 02:35:20, 340.6 min ago | 0.191420 | +0.2449 |
| 2026-08-30 09:03:40 | NO PASS rider cws12 - cws12 20.25 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 8: ws4,ws5,ws7,ws8,ws9,ws10,ws11,ws12 | last 02:35:20, 388.3 min ago | 0.190650 | +0.6462 |
| 2026-08-30 09:40:50 | the favourable extreme - MFE 1.4540 | - | 8: ws4,ws5,ws7,ws8,ws9,ws10,ws11,ws12 | last 02:35:20, 425.5 min ago | 0.189100 | +1.4540 |
| 2026-08-30 09:41:35 | LATCH1 rider cws12 - latch 1 at the t1 cadence 2026-08-30 09:41:35, divergence state -1 | - | 8: ws4,ws5,ws7,ws8,ws9,ws10,ws11,ws12 | last 02:35:20, 426.2 min ago | 0.189570 | +1.2090 |
| 2026-08-30 09:41:35 | **CADENCE:** EXHAUST rider cws12 - t1 cws1b oob 09:41:25..09:41:30, cws1r reversed 09:41:30 during, stamp 09:41:30 \| mage-cascade up OPPOSES the SHORT - rev-trade | - | 8: ws4,ws5,ws7,ws8,ws9,ws10,ws11,ws12 | last 02:35:20, 426.2 min ago | 0.189570 | +1.2090 |
| 2026-08-30 09:41:35 | THIS LEG CLOSES on t1, realised +1.1725 | - | 8: ws4,ws5,ws7,ws8,ws9,ws10,ws11,ws12 | last 02:35:20, 426.2 min ago | 0.189570 | +1.2090 |

## leg 6 of 15 - 2026-08-30 LONG   opens 2026-08-30 09:41:40   exits 2026-08-30 10:12:55 on t2   MAE 0.4113   MFE 0.4008   realised +0.1740   held 31.2 min   CONTINUITY: 1 bar after leg 5 exit 2026-08-30 09:41:35

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 09:41:40 | >>> THIS LEG OPENS LONG | - | 4: ws1,ws2,ws3,ws6 | last 14:28:50, 1152.8 min ago / counter-side 02:35:20 | 0.189640 | +0.0000 |
| 2026-08-30 09:43:35 | the ADVERSE extreme - MAE 0.4113 | - | 4: ws1,ws2,ws3,ws6 | last 14:28:50, 1154.8 min ago / counter-side 02:35:20 | 0.188860 | -0.4113 |
| 2026-08-30 10:10:05 | ARM - cws1b+cws1r: cws1b 106.30 + cws1r 86.09 oob | - | 4: ws2,ws3,ws4,ws6 | last 14:28:50, 1181.2 min ago / counter-side 10:06:00 | 0.190200 | +0.2953 |
| 2026-08-30 10:10:05 | RIDER rider cws6 - cws6 r 70.93, the highest ex-fence | - | 4: ws2,ws3,ws4,ws6 | last 14:28:50, 1181.2 min ago / counter-side 10:06:00 | 0.190200 | +0.2953 |
| 2026-08-30 10:10:05 | RETEST - cws1r 86.09 oob + cws2r 63.89 / cws3r 67.97 in - the gate opens; cws1r oob->ib cross 2026-08-30 10:12:00, wob 12, cadence at 2026-08-30 10:12:55 | - | 4: ws2,ws3,ws4,ws6 | last 14:28:50, 1181.2 min ago / counter-side 10:06:00 | 0.190200 | +0.2953 |
| 2026-08-30 10:10:50 | the favourable extreme - MFE 0.4008 | - | 5: ws1,ws2,ws3,ws4,ws6 | last 14:28:50, 1182.0 min ago / counter-side 10:06:00 | 0.190400 | +0.4008 |
| 2026-08-30 10:12:55 | **CADENCE:** RIDER rider cws6 - v4-arm-lineage-retest: the re-scan rides cws6 74.18, the highest ex-fence | - | 5: ws1,ws2,ws3,ws4,ws6 | last 14:28:50, 1184.1 min ago / counter-side 10:06:00 | 0.189980 | +0.1793 |
| 2026-08-30 10:12:55 | LATCH1 rider cws6 - latch 1 at the t2 cadence 2026-08-30 10:12:55, divergence state +1 | - | 5: ws1,ws2,ws3,ws4,ws6 | last 14:28:50, 1184.1 min ago / counter-side 10:06:00 | 0.189980 | +0.1793 |
| 2026-08-30 10:12:55 | **CADENCE:** EXHAUST rider cws6 - t2 cws1r ib cross 10:12:00 confirmed 10:12:55 at wob 12, cws1b 77.01 not oob, ws1b hold 0 \| mage-cascade down OPPOSES the LONG - rev-trade | - | 5: ws1,ws2,ws3,ws4,ws6 | last 14:28:50, 1184.1 min ago / counter-side 10:06:00 | 0.189980 | +0.1793 |
| 2026-08-30 10:12:55 | THIS LEG CLOSES on t2, realised +0.1740 | - | 5: ws1,ws2,ws3,ws4,ws6 | last 14:28:50, 1184.1 min ago / counter-side 10:06:00 | 0.189980 | +0.1793 |

## leg 7 of 15 - 2026-08-30 SHORT   opens 2026-08-30 10:13:00   exits 2026-08-30 11:52:55 on t1   MAE 0.6580   MFE 0.2158   realised -0.0158   held 99.9 min   CONTINUITY: 1 bar after leg 6 exit 2026-08-30 10:12:55

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 10:13:00 | >>> THIS LEG OPENS SHORT | - | none | last 10:06:00, 7.0 min ago | 0.189970 | -0.0000 |
| 2026-08-30 11:10:10 | the ADVERSE extreme - MAE 0.6580 | - | 2: ws2,ws3 | last 10:06:00, 64.2 min ago | 0.191220 | -0.6580 |
| 2026-08-30 11:44:00 | ARM - cws4r: cws4r 13.46 oob | - | 3: ws1,ws2,ws3 | last 10:06:00, 98.0 min ago | 0.190050 | -0.0421 |
| 2026-08-30 11:44:00 | RIDER rider cws3 - cws3 r 24.72, the highest ex-fence | - | 3: ws1,ws2,ws3 | last 10:06:00, 98.0 min ago | 0.190050 | -0.0421 |
| 2026-08-30 11:44:00 | RETEST - cws1r 69.17 is not oob at the arm - the gate stays shut | - | 3: ws1,ws2,ws3 | last 10:06:00, 98.0 min ago | 0.190050 | -0.0421 |
| 2026-08-30 11:48:30 | the favourable extreme - MFE 0.2158 | - | 7: ws1,ws2,ws3,ws4,ws5,ws6,ws7 | last 10:06:00, 102.5 min ago | 0.189560 | +0.2158 |
| 2026-08-30 11:52:55 | LATCH1 rider cws3 - latch 1 at the t1 cadence 2026-08-30 11:52:55, divergence state -1 | - | 8: ws1,ws2,ws3,ws4,ws5,ws6,ws7,ws9 | last 10:06:00, 106.9 min ago | 0.189760 | +0.1105 |
| 2026-08-30 11:52:55 | **CADENCE:** EXHAUST rider cws3 - t1 cws1b oob 11:51:45..11:52:50, cws1r reversed 11:52:45 during, stamp 11:52:45 \| mage-cascade up OPPOSES the SHORT - rev-trade | - | 8: ws1,ws2,ws3,ws4,ws5,ws6,ws7,ws9 | last 10:06:00, 106.9 min ago | 0.189760 | +0.1105 |
| 2026-08-30 11:52:55 | THIS LEG CLOSES on t1, realised -0.0158 | - | 8: ws1,ws2,ws3,ws4,ws5,ws6,ws7,ws9 | last 10:06:00, 106.9 min ago | 0.189760 | +0.1105 |

## leg 8 of 15 - 2026-08-30 LONG   opens 2026-08-30 11:53:00   exits 2026-08-30 12:03:55 on DIV REV-TRADE   MAE 0.1263   MFE 0.4579   realised +0.4421   held 10.9 min   CONTINUITY: 1 bar after leg 7 exit 2026-08-30 11:52:55

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 11:53:00 | >>> THIS LEG OPENS LONG | - | 4: ws8,ws10,ws11,ws12 | last 14:28:50, 1284.2 min ago / counter-side 10:06:00 | 0.190000 | +0.0000 |
| 2026-08-30 11:53:00 | the ADVERSE extreme - MAE 0.1263 | - | 4: ws8,ws10,ws11,ws12 | last 14:28:50, 1284.2 min ago / counter-side 10:06:00 | 0.189760 | -0.1263 |
| 2026-08-30 12:03:55 | ARM - cws2Mage+cws2r: cws2Mage 90.48 + cws2r 92.13 oob | - | 7: ws1,ws2,ws3,ws8,ws10,ws11,ws12 | last 14:28:50, 1295.1 min ago / counter-side 10:06:00 | 0.190850 | +0.4474 |
| 2026-08-30 12:03:55 | DIV - cws1r divergence +1 bearish \| anchor_floater state +1 divergence, SHORT | - | 7: ws1,ws2,ws3,ws8,ws10,ws11,ws12 | last 14:28:50, 1295.1 min ago / counter-side 10:06:00 | 0.190850 | +0.4474 |
| 2026-08-30 12:03:55 | the favourable extreme - MFE 0.4579 | - | 7: ws1,ws2,ws3,ws8,ws10,ws11,ws12 | last 14:28:50, 1295.1 min ago / counter-side 10:06:00 | 0.190870 | +0.4579 |
| 2026-08-30 12:03:55 | THIS LEG CLOSES on DIV REV-TRADE, realised +0.4421 | - | 7: ws1,ws2,ws3,ws8,ws10,ws11,ws12 | last 14:28:50, 1295.1 min ago / counter-side 10:06:00 | 0.190850 | +0.4474 |

## leg 9 of 15 - 2026-08-30 SHORT   opens 2026-08-30 12:04:00   exits 2026-08-30 13:16:10 on t2   MAE 1.2786   MFE 0.0734   realised -0.2568   held 72.2 min   CONTINUITY: 1 bar after leg 8 exit 2026-08-30 12:03:55

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 12:04:00 | >>> THIS LEG OPENS SHORT | - | 5: ws4,ws5,ws6,ws7,ws9 | last 10:06:00, 118.0 min ago | 0.190840 | -0.0000 |
| 2026-08-30 12:04:10 | the favourable extreme - MFE 0.0734 | - | 5: ws4,ws5,ws6,ws7,ws9 | last 10:06:00, 118.2 min ago | 0.190700 | +0.0734 |
| 2026-08-30 12:33:15 | the ADVERSE extreme - MAE 1.2786 | - | 3: ws2,ws7,ws9 | last 10:06:00, 147.2 min ago | 0.193280 | -1.2786 |
| 2026-08-30 13:12:40 | ARM - cws1b+cws1r: cws1b 10.06 + cws1r 10.76 oob | - | 5: ws1,ws2,ws3,ws5,ws9 | last 10:06:00, 186.7 min ago | 0.191120 | -0.1467 |
| 2026-08-30 13:12:40 | RIDER rider cws9 - cws9 r 47.66, the highest ex-fence | - | 5: ws1,ws2,ws3,ws5,ws9 | last 10:06:00, 186.7 min ago | 0.191120 | -0.1467 |
| 2026-08-30 13:12:40 | RETEST - cws1r 10.76 oob + cws2r 32.83 / cws3r 56.89 in - the gate opens; cws1r oob->ib cross 2026-08-30 13:15:15, wob 12, cadence at 2026-08-30 13:16:10 | - | 5: ws1,ws2,ws3,ws5,ws9 | last 10:06:00, 186.7 min ago | 0.191120 | -0.1467 |
| 2026-08-30 13:16:10 | **CADENCE:** RIDER rider cws9 - v4-arm-lineage-retest: the re-scan rides cws9 47.66, the highest ex-fence | - | 5: ws1,ws2,ws3,ws5,ws9 | last 10:06:00, 190.2 min ago | 0.191270 | -0.2253 |
| 2026-08-30 13:16:10 | LATCH1 rider cws9 - latch 1 at the t2 cadence 2026-08-30 13:16:10, divergence state -1 | - | 5: ws1,ws2,ws3,ws5,ws9 | last 10:06:00, 190.2 min ago | 0.191270 | -0.2253 |
| 2026-08-30 13:16:10 | **CADENCE:** EXHAUST rider cws9 - t2 cws1r ib cross 13:15:15 confirmed 13:16:10 at wob 12, cws1b 17.60 not oob, ws1b hold 0 \| mage-cascade up OPPOSES the SHORT - rev-trade | - | 5: ws1,ws2,ws3,ws5,ws9 | last 10:06:00, 190.2 min ago | 0.191270 | -0.2253 |
| 2026-08-30 13:16:10 | THIS LEG CLOSES on t2, realised -0.2568 | - | 5: ws1,ws2,ws3,ws5,ws9 | last 10:06:00, 190.2 min ago | 0.191270 | -0.2253 |

## leg 10 of 15 - 2026-08-30 LONG   opens 2026-08-30 13:16:15   exits 2026-08-30 15:45:30 on cws1b counter-oob   MAE 0.2456   MFE 2.2317   realised -0.0314   held 149.2 min   CONTINUITY: 1 bar after leg 9 exit 2026-08-30 13:16:10

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 13:16:15 | >>> THIS LEG OPENS LONG | - | 7: ws4,ws6,ws7,ws8,ws10,ws11,ws12 | last 14:28:50, 1367.4 min ago / counter-side 10:06:00 | 0.191330 | +0.0000 |
| 2026-08-30 13:36:00 | the ADVERSE extreme - MAE 0.2456 | - | 8: ws1,ws2,ws4,ws6,ws8,ws10,ws11,ws12 | last 14:28:50, 1387.2 min ago / counter-side 10:06:00 | 0.190860 | -0.2456 |
| 2026-08-30 13:45:00 | ARM - cws1b+cws1r: cws1b 101.82 + cws1r 93.06 oob | - | 7: ws1,ws2,ws4,ws8,ws10,ws11,ws12 | last 14:28:50, 1396.2 min ago / counter-side 10:06:00 | 0.192910 | +0.8258 |
| 2026-08-30 13:45:00 | RIDER rider cws12 - cws12 r 53.64, the highest ex-fence | - | 7: ws1,ws2,ws4,ws8,ws10,ws11,ws12 | last 14:28:50, 1396.2 min ago / counter-side 10:06:00 | 0.192910 | +0.8258 |
| 2026-08-30 13:45:00 | RETEST - cws1r 93.06 oob + cws2r 66.08 / cws3r 70.44 in - the gate opens; cws1r oob->ib cross 2026-08-30 13:47:45, wob 12, cadence at 2026-08-30 13:48:40 | - | 7: ws1,ws2,ws4,ws8,ws10,ws11,ws12 | last 14:28:50, 1396.2 min ago / counter-side 10:06:00 | 0.192910 | +0.8258 |
| 2026-08-30 13:48:40 | **CADENCE:** RIDER rider cws12 - v4-arm-lineage-retest: the re-scan rides cws12 56.91, the highest ex-fence | - | 7: ws1,ws2,ws4,ws8,ws10,ws11,ws12 | last 14:28:50, 1399.8 min ago / counter-side 10:06:00 | 0.193750 | +1.2648 |
| 2026-08-30 13:58:40 | the favourable extreme - MFE 2.2317 | - | 8: ws1,ws2,ws3,ws4,ws8,ws10,ws11,ws12 | last 14:28:50, 1409.8 min ago / counter-side 10:06:00 | 0.195600 | +2.2317 |
| 2026-08-30 14:00:00 | LATCH1 rider cws12 - latch 1 at the t1 cadence 2026-08-30 14:00:00, divergence state +1 | - | 8: ws1,ws2,ws3,ws4,ws8,ws10,ws11,ws12 | last 14:28:50, 1411.2 min ago / counter-side 10:06:00 | 0.194550 | +1.6830 |
| 2026-08-30 14:00:00 | **CADENCE:** NO ACTION rider cws12 - t1 cws1b oob 13:54:30..13:59:55, cws1r reversed 13:59:50 during, stamp 13:59:50 \| mage-cascade up matches the LONG - no action, keep walking | - | 8: ws1,ws2,ws3,ws4,ws8,ws10,ws11,ws12 | last 14:28:50, 1411.2 min ago / counter-side 10:06:00 | 0.194550 | +1.6830 |
| 2026-08-30 14:03:20 | LATCH1 rider cws12 - latch 1 at the t1 cadence 2026-08-30 14:03:20, divergence state +1 | - | 8: ws1,ws2,ws3,ws4,ws8,ws10,ws11,ws12 | last 14:28:50, 1414.5 min ago / counter-side 10:06:00 | 0.195000 | +1.9182 |
| 2026-08-30 14:03:20 | **CADENCE:** NO ACTION rider cws12 - t1 cws1b ib 14:02:00, cws1r reversed 14:03:20 inside the 120s grace, stamp 14:03:20 \| mage-cascade up matches the LONG - no action, keep walking | - | 8: ws1,ws2,ws3,ws4,ws8,ws10,ws11,ws12 | last 14:28:50, 1414.5 min ago / counter-side 10:06:00 | 0.195000 | +1.9182 |
| 2026-08-30 14:06:30 | NO ACTION rider cws12 - latch latch 2: rider cws12 reversed raw 2026-08-30 14:05:35 stamp 2026-08-30 14:06:30, no candidate inside lin_hop, support ws9 raw 2026-08-30 14:04:05 stamp 2026-08-30 14:05:00, ws10 raw 2026-08-30 14:04:05 stamp 2026-08-30 14:05:00, ws11 raw 2026-08-30 14:04:05 stamp 2026-08-30 14:05:00 \| latch 1 at the t1 cadence 2026-08-30 14:03:20, divergence state +1 \| mage-cascade up matches the LONG - no action, keep walking | - | 7: ws2,ws3,ws4,ws8,ws10,ws11,ws12 | last 14:28:50, 1417.7 min ago / counter-side 10:06:00 | 0.194100 | +1.4478 |
| 2026-08-30 14:15:55 | LATCH1 rider cws12 - latch 1 at the t2 cadence 2026-08-30 14:15:55, divergence state +1 | - | 9: ws1,ws2,ws3,ws4,ws6,ws8,ws10,ws11,ws12 | last 14:28:50, 1427.1 min ago / counter-side 10:06:00 | 0.195010 | +1.9234 |
| 2026-08-30 14:15:55 | **CADENCE:** NO ACTION rider cws12 - t2 cws1r ib cross 14:15:00 confirmed 14:15:55 at wob 12, cws1b 72.52 not oob, ws1b hold 0 \| mage-cascade up matches the LONG - no action, keep walking | - | 9: ws1,ws2,ws3,ws4,ws6,ws8,ws10,ws11,ws12 | last 14:28:50, 1427.1 min ago / counter-side 10:06:00 | 0.195010 | +1.9234 |
| 2026-08-30 14:20:45 | NO ACTION rider cws12 - latch latch 2: rider cws12 reversed raw 2026-08-30 14:05:35 stamp 2026-08-30 14:06:30, no candidate inside lin_hop, support ws9 raw 2026-08-30 14:19:00 stamp 2026-08-30 14:19:55, ws10 raw 2026-08-30 14:18:10 stamp 2026-08-30 14:19:05, ws11 raw 2026-08-30 14:19:50 stamp 2026-08-30 14:20:45 \| latch 1 at the t2 cadence 2026-08-30 14:15:55, divergence state +1 \| mage-cascade up matches the LONG - no action, keep walking | - | 8: ws2,ws3,ws4,ws6,ws8,ws10,ws11,ws12 | last 14:28:50, 1431.9 min ago / counter-side 10:06:00 | 0.192690 | +0.7108 |
| 2026-08-30 14:27:20 | **CADENCE:** CADENCE rider cws12 - cws1b counter-oob cws1b 14.95 entered the LOW oob 14:27:20 \| rider cws12 45.46, no-longer-exfence no, reversed no \| mage-cascade up | none offered | 6: ws4,ws6,ws8,ws10,ws11,ws12 | last 14:28:50, 1438.5 min ago / counter-side 10:06:00 | 0.192000 | +0.3502 |
| 2026-08-30 14:27:20 | HOLD rider cws12 - rider cws12 45.46 ex-fence and not reversed - no action | - | 6: ws4,ws6,ws8,ws10,ws11,ws12 | last 14:28:50, 1438.5 min ago / counter-side 10:06:00 | 0.192000 | +0.3502 |
| 2026-08-30 14:30:30 | **CADENCE:** CADENCE rider cws12 - cws1b counter-oob cws1b 14.49 entered the LOW oob 14:30:30 \| rider cws12 45.46, no-longer-exfence no, reversed no \| mage-cascade up | none offered | 6: ws4,ws6,ws8,ws10,ws11,ws12 | last 14:28:50, 1441.7 min ago / counter-side 10:06:00 | 0.192050 | +0.3763 |
| 2026-08-30 14:30:30 | HOLD rider cws12 - rider cws12 45.46 ex-fence and not reversed - no action | - | 6: ws4,ws6,ws8,ws10,ws11,ws12 | last 14:28:50, 1441.7 min ago / counter-side 10:06:00 | 0.192050 | +0.3763 |
| 2026-08-30 14:34:00 | **CADENCE:** CADENCE rider cws12 - cws1b counter-oob cws1b 14.50 entered the LOW oob 14:34:00 \| rider cws12 45.46, no-longer-exfence no, reversed no \| mage-cascade up | none offered | 6: ws1,ws6,ws8,ws10,ws11,ws12 | last 14:28:50, 1445.2 min ago / counter-side 10:06:00 | 0.191930 | +0.3136 |
| 2026-08-30 14:34:00 | HOLD rider cws12 - rider cws12 45.46 ex-fence and not reversed - no action | - | 6: ws1,ws6,ws8,ws10,ws11,ws12 | last 14:28:50, 1445.2 min ago / counter-side 10:06:00 | 0.191930 | +0.3136 |
| 2026-08-30 14:39:15 | **CADENCE:** CADENCE rider cws12 - cws1b counter-oob cws1b 14.37 entered the LOW oob 14:39:15 \| rider cws12 44.04, no-longer-exfence no, reversed no \| mage-cascade up | none offered | 6: ws1,ws6,ws8,ws10,ws11,ws12 | last 14:28:50, 1450.4 min ago / counter-side 10:06:00 | 0.191250 | -0.0418 |
| 2026-08-30 14:39:15 | HOLD rider cws12 - rider cws12 44.04 ex-fence and not reversed - no action | - | 6: ws1,ws6,ws8,ws10,ws11,ws12 | last 14:28:50, 1450.4 min ago / counter-side 10:06:00 | 0.191250 | -0.0418 |
| 2026-08-30 14:56:55 | **CADENCE:** NO ACTION rider cws12 - t2 cws1r ib cross 14:56:00 confirmed 14:56:55 at wob 12, cws1b 49.04 not oob, ws1b hold 0 \| mage-cascade up matches the LONG - no action, keep walking | - | 6: ws1,ws2,ws8,ws10,ws11,ws12 | last 14:28:50, 1468.1 min ago / counter-side 10:06:00 | 0.192620 | +0.6742 |
| 2026-08-30 15:09:30 | **CADENCE:** NO ACTION rider cws12 - t1 cws1b ib 15:09:20, cws1r reversed 15:09:30 inside the 120s grace, stamp 15:09:30 \| mage-cascade up matches the LONG - no action, keep walking | - | 5: ws2,ws3,ws10,ws11,ws12 | last 14:28:50, 1480.7 min ago / counter-side 10:06:00 | 0.192440 | +0.5801 |
| 2026-08-30 15:14:45 | **CADENCE:** CADENCE rider cws12 - cws1b counter-oob cws1b 11.62 entered the LOW oob 15:14:45 \| rider cws12 24.71, no-longer-exfence no, reversed no \| mage-cascade up | none offered | 3: ws2,ws3,ws12 | last 14:28:50, 1485.9 min ago / counter-side 10:06:00 | 0.191020 | -0.1620 |
| 2026-08-30 15:14:45 | HOLD rider cws12 - rider cws12 24.71 ex-fence and not reversed - no action | - | 3: ws2,ws3,ws12 | last 14:28:50, 1485.9 min ago / counter-side 10:06:00 | 0.191020 | -0.1620 |
| 2026-08-30 15:16:20 | **CADENCE:** CADENCE rider cws12 - cws1b counter-oob cws1b 10.38 entered the LOW oob 15:16:20 \| rider cws12 24.45, no-longer-exfence no, reversed no \| mage-cascade up | none offered | 3: ws2,ws3,ws12 | last 14:28:50, 1487.5 min ago / counter-side 10:06:00 | 0.190900 | -0.2247 |
| 2026-08-30 15:16:20 | HOLD rider cws12 - rider cws12 24.45 ex-fence and not reversed - no action | - | 3: ws2,ws3,ws12 | last 14:28:50, 1487.5 min ago / counter-side 10:06:00 | 0.190900 | -0.2247 |
| 2026-08-30 15:24:15 | NO PASS rider cws12 - cws12 17.14 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 3: ws1,ws2,ws3 | last 14:28:50, 1495.4 min ago / counter-side 10:06:00 | 0.191790 | +0.2404 |
| 2026-08-30 15:45:30 | **CADENCE:** EXHAUST rider cws12 - cws1b counter-oob cws1b 10.61 entered the LOW oob 15:45:30 \| mage-cascade down OPPOSES the LONG - rev-trade | - | 2: ws2,ws3 | last 14:28:50, 1516.7 min ago / counter-side 10:06:00 | 0.191300 | -0.0157 |
| 2026-08-30 15:45:30 | THIS LEG CLOSES on cws1b counter-oob, realised -0.0314 | - | 2: ws2,ws3 | last 14:28:50, 1516.7 min ago / counter-side 10:06:00 | 0.191300 | -0.0157 |

## leg 11 of 15 - 2026-08-30 SHORT   opens 2026-08-30 15:45:35   exits 2026-08-30 16:13:05 on cws1b counter-oob   MAE 0.7947   MFE 0.8313   realised -0.7581   held 27.5 min   CONTINUITY: 1 bar after leg 10 exit 2026-08-30 15:45:30

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 15:45:35 | >>> THIS LEG OPENS SHORT | - | 10: ws1,ws4,ws5,ws6,ws7,ws8,ws9,ws10,ws11,ws12 | last 10:06:00, 339.6 min ago | 0.191270 | -0.0000 |
| 2026-08-30 15:46:45 | ARM - cws2Mage+cws2r: cws2Mage 14.43 + cws2r 14.65 oob | - | 11: ws1,ws2,ws4,ws5,ws6,ws7,ws8,ws9,ws10,ws11,ws12 | last 10:06:00, 340.8 min ago | 0.191100 | +0.0889 |
| 2026-08-30 15:46:45 | DIV - cws1r divergence none \| anchor_floater state +2 PM, trend SHORT | - | 11: ws1,ws2,ws4,ws5,ws6,ws7,ws8,ws9,ws10,ws11,ws12 | last 10:06:00, 340.8 min ago | 0.191100 | +0.0889 |
| 2026-08-30 15:46:45 | RIDER rider cws12 - cws12 r 17.61, the highest ex-fence | - | 11: ws1,ws2,ws4,ws5,ws6,ws7,ws8,ws9,ws10,ws11,ws12 | last 10:06:00, 340.8 min ago | 0.191100 | +0.0889 |
| 2026-08-30 15:46:45 | RETEST - cws1r 17.14 is not oob at the arm - the gate stays shut | - | 11: ws1,ws2,ws4,ws5,ws6,ws7,ws8,ws9,ws10,ws11,ws12 | last 10:06:00, 340.8 min ago | 0.191100 | +0.0889 |
| 2026-08-30 15:56:35 | the favourable extreme - MFE 0.8313 | - | 12: ws1,ws2,ws3,ws4,ws5,ws6,ws7,ws8,ws9,ws10,ws11,ws12 | last 10:06:00, 350.6 min ago | 0.189680 | +0.8313 |
| 2026-08-30 16:13:05 | **CADENCE:** CADENCE rider cws12 - cws1b counter-oob cws1b 85.23 entered the HIGH oob 16:13:05 \| rider cws12 38.70, no-longer-exfence no, reversed yes \| mage-cascade down | none offered | 11: ws1,ws3,ws4,ws5,ws6,ws7,ws8,ws9,ws10,ws11,ws12 | last 10:06:00, 367.1 min ago | 0.192650 | -0.7215 |
| 2026-08-30 16:13:05 | **CADENCE:** EXHAUST rider cws12 - t4 at a cws1b counter-oob cadence - rider cws12 38.70, no candidate inside lin_hop 2 | - | 11: ws1,ws3,ws4,ws5,ws6,ws7,ws8,ws9,ws10,ws11,ws12 | last 10:06:00, 367.1 min ago | 0.192650 | -0.7215 |
| 2026-08-30 16:13:05 | the ADVERSE extreme - MAE 0.7947 | - | 11: ws1,ws3,ws4,ws5,ws6,ws7,ws8,ws9,ws10,ws11,ws12 | last 10:06:00, 367.1 min ago | 0.192790 | -0.7947 |
| 2026-08-30 16:13:05 | THIS LEG CLOSES on cws1b counter-oob, realised -0.7581 | - | 11: ws1,ws3,ws4,ws5,ws6,ws7,ws8,ws9,ws10,ws11,ws12 | last 10:06:00, 367.1 min ago | 0.192650 | -0.7215 |

## leg 12 of 15 - 2026-08-30 LONG   opens 2026-08-30 16:13:10   exits 2026-08-30 18:06:25 on t2   MAE 4.2964   MFE 0.7628   realised -2.7657   held 113.2 min   CONTINUITY: 1 bar after leg 11 exit 2026-08-30 16:13:05

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 16:13:10 | >>> THIS LEG OPENS LONG | - | 1: ws2 | last 14:28:50, 1544.3 min ago / counter-side 10:06:00 | 0.192720 | +0.0000 |
| 2026-08-30 16:15:35 | the favourable extreme - MFE 0.7628 | - | 2: ws2,ws3 | last 14:28:50, 1546.8 min ago / counter-side 10:06:00 | 0.194190 | +0.7628 |
| 2026-08-30 17:24:35 | the ADVERSE extreme - MAE 4.2964 | - | 1: ws9 | last 16:19:30, 65.1 min ago | 0.184440 | -4.2964 |
| 2026-08-30 18:04:00 | ARM - cws4r: cws4r 86.94 oob | - | 3: ws1,ws2,ws4 | last 16:19:30, 104.5 min ago | 0.187950 | -2.4751 |
| 2026-08-30 18:04:00 | RIDER rider cws4 - cws4 r 86.94, the highest ex-fence | - | 3: ws1,ws2,ws4 | last 16:19:30, 104.5 min ago | 0.187950 | -2.4751 |
| 2026-08-30 18:04:00 | RETEST - cws1r 98.56 oob + cws2r 68.10 / cws3r 77.62 in - the gate opens; cws1r oob->ib cross 2026-08-30 18:05:30, wob 12, cadence at 2026-08-30 18:06:25 | - | 3: ws1,ws2,ws4 | last 16:19:30, 104.5 min ago | 0.187950 | -2.4751 |
| 2026-08-30 18:06:25 | **CADENCE:** RIDER rider cws4 - v4-arm-lineage-retest: the re-scan rides cws4 84.36, the highest ex-fence | - | 3: ws1,ws2,ws4 | last 16:19:30, 106.9 min ago | 0.187510 | -2.7034 |
| 2026-08-30 18:06:25 | **CADENCE:** EXHAUST rider cws4 - t2 cws1r ib cross 18:05:30 confirmed 18:06:25 at wob 12, cws1b 51.77 not oob, ws1b hold 0 \| mage-cascade down OPPOSES the LONG - rev-trade | - | 3: ws1,ws2,ws4 | last 16:19:30, 106.9 min ago | 0.187510 | -2.7034 |
| 2026-08-30 18:06:25 | THIS LEG CLOSES on t2, realised -2.7657 | - | 3: ws1,ws2,ws4 | last 16:19:30, 106.9 min ago | 0.187510 | -2.7034 |

## leg 13 of 15 - 2026-08-30 SHORT   opens 2026-08-30 18:06:30   exits 2026-08-30 21:04:00 on t2   MAE 0.8058   MFE 5.1283   realised +3.7462   held 177.5 min   CONTINUITY: 1 bar after leg 12 exit 2026-08-30 18:06:25

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 18:06:30 | >>> THIS LEG OPENS SHORT | - | 9: ws3,ws5,ws6,ws7,ws8,ws9,ws10,ws11,ws12 | last 10:06:00, 480.5 min ago / counter-side 16:19:30 | 0.187390 | -0.0000 |
| 2026-08-30 18:52:00 | the ADVERSE extreme - MAE 0.8058 | - | 4: ws1,ws9,ws10,ws12 | last 10:06:00, 526.0 min ago / counter-side 16:19:30 | 0.188900 | -0.8058 |
| 2026-08-30 19:16:00 | ARM - cws4r: cws4r 14.46 oob | - | none | last 19:07:55, 8.1 min ago | 0.187560 | -0.0907 |
| 2026-08-30 19:16:00 | RETEST - cws1r 56.12 is not oob at the arm - the gate stays shut | - | none | last 19:07:55, 8.1 min ago | 0.187560 | -0.0907 |
| 2026-08-30 19:16:05 | NO RIDER - no cws1..cws12 r is ex-fence at the arm bar + 5s - the walk continues, t3 and t4 stay reachable | - | none | last 19:07:55, 8.2 min ago | 0.187560 | -0.0907 |
| 2026-08-30 19:45:25 | the favourable extreme - MFE 5.1283 | - | 6: ws1,ws2,ws3,ws4,ws5,ws6 | last 19:07:55, 37.5 min ago | 0.177780 | +5.1283 |
| 2026-08-30 20:35:55 | **CADENCE:** NO ACTION - t2 cws1r ib cross 20:35:00 confirmed 20:35:55 at wob 12, cws1b 35.26 not oob, ws1b hold 0 \| mage-cascade down matches the SHORT - no action, keep walking | - | 6: ws1,ws2,ws6,ws7,ws9,ws10 | last 19:07:55, 88.0 min ago | 0.181040 | +3.3887 |
| 2026-08-30 21:04:00 | LATCH1 - latch 1 at the t2 cadence 2026-08-30 21:04:00, divergence state -1 | - | 5: ws1,ws3,ws6,ws9,ws10 | last 19:07:55, 116.1 min ago | 0.180330 | +3.7675 |
| 2026-08-30 21:04:00 | **CADENCE:** EXHAUST - t2 cws1r ib cross 21:03:05 confirmed 21:04:00 at wob 12, cws1b 18.35 not oob, ws1b hold 0 \| mage-cascade up OPPOSES the SHORT - rev-trade | - | 5: ws1,ws3,ws6,ws9,ws10 | last 19:07:55, 116.1 min ago | 0.180330 | +3.7675 |
| 2026-08-30 21:04:00 | THIS LEG CLOSES on t2, realised +3.7462 | - | 5: ws1,ws3,ws6,ws9,ws10 | last 19:07:55, 116.1 min ago | 0.180330 | +3.7675 |

## leg 14 of 15 - 2026-08-30 LONG   opens 2026-08-30 21:04:05   exits 2026-08-30 22:22:25 on cws1b counter-oob   MAE 0.9370   MFE 1.4858   realised -0.7318   held 78.3 min   CONTINUITY: 1 bar after leg 13 exit 2026-08-30 21:04:00

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 21:04:05 | >>> THIS LEG OPENS LONG | - | 6: ws2,ws4,ws5,ws7,ws8,ws11 | last 16:19:30, 284.6 min ago / counter-side 19:07:55 | 0.180370 | +0.0000 |
| 2026-08-30 21:59:15 | ARM - cws1b+cws1r: cws1b 103.18 + cws1r 97.10 oob | - | 6: ws1,ws3,ws5,ws7,ws8,ws11 | last 16:19:30, 339.8 min ago / counter-side 19:07:55 | 0.182160 | +0.9924 |
| 2026-08-30 21:59:15 | RIDER rider cws11 - cws11 r 74.01, the highest ex-fence | - | 6: ws1,ws3,ws5,ws7,ws8,ws11 | last 16:19:30, 339.8 min ago / counter-side 19:07:55 | 0.182160 | +0.9924 |
| 2026-08-30 21:59:15 | RETEST - cws1r 97.10 oob + cws2r 60.57 / cws3r 40.02 in - the gate opens; cws1r oob->ib cross 2026-08-30 22:02:00, wob 12, cadence at 2026-08-30 22:02:55 | - | 6: ws1,ws3,ws5,ws7,ws8,ws11 | last 16:19:30, 339.8 min ago / counter-side 19:07:55 | 0.182160 | +0.9924 |
| 2026-08-30 22:01:40 | the favourable extreme - MFE 1.4858 | - | 6: ws1,ws3,ws5,ws7,ws8,ws11 | last 16:19:30, 342.2 min ago / counter-side 19:07:55 | 0.183050 | +1.4858 |
| 2026-08-30 22:02:55 | **CADENCE:** RIDER rider cws11 - v4-arm-lineage-retest: the re-scan rides cws11 73.73, the highest ex-fence | - | 6: ws1,ws3,ws5,ws7,ws8,ws11 | last 16:19:30, 343.4 min ago / counter-side 19:07:55 | 0.182100 | +0.9591 |
| 2026-08-30 22:22:25 | **CADENCE:** EXHAUST rider cws11 - cws1b counter-oob cws1b 13.89 entered the LOW oob 22:22:25 \| mage-cascade down OPPOSES the LONG - rev-trade | - | 5: ws3,ws5,ws7,ws8,ws11 | last 16:19:30, 362.9 min ago / counter-side 19:07:55 | 0.179050 | -0.7318 |
| 2026-08-30 22:22:25 | the ADVERSE extreme - MAE 0.9370 | - | 5: ws3,ws5,ws7,ws8,ws11 | last 16:19:30, 362.9 min ago / counter-side 19:07:55 | 0.178680 | -0.9370 |
| 2026-08-30 22:22:25 | THIS LEG CLOSES on cws1b counter-oob, realised -0.7318 | - | 5: ws3,ws5,ws7,ws8,ws11 | last 16:19:30, 362.9 min ago / counter-side 19:07:55 | 0.179050 | -0.7318 |

## leg 15 of 15 - 2026-08-30 LONG   opens 2026-08-30 22:22:30   NO EXIT to the window end   CONTINUITY: 1 bar after leg 14 exit 2026-08-30 22:22:25

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 22:22:30 | >>> THIS LEG OPENS LONG | - | 5: ws3,ws5,ws7,ws8,ws11 | last 16:19:30, 363.0 min ago / counter-side 19:07:55 | 0.179050 | +0.0000 |
| 2026-08-30 22:22:30 | NOTE NO ARM - no arm to the window end | - | 5: ws3,ws5,ws7,ws8,ws11 | last 16:19:30, 363.0 min ago / counter-side 19:07:55 | 0.179050 | +0.0000 |

## the MAE / MFE aggregate over every leg

| leg | the open | dir | the exit | ended by | held min | the rider chain | MAE % | MFE % | realised % | drag % | net % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-08-29 23:53:55 | SHORT | 2026-08-30 02:27:50 | t1 | 153.9 | ws11 | 0.5088 | +1.9536 | +1.5415 | 0.1975 | +1.3440 |
| 2 | 2026-08-30 02:27:55 | LONG | 2026-08-30 02:45:55 | t2 | 18.0 | ws6 | 0.1188 | +0.5529 | +0.2377 | 0.1975 | +0.0402 |
| 3 | 2026-08-30 02:46:00 | SHORT | 2026-08-30 04:41:00 | t1 | 115.0 | ws5 > ws10 | 0.3196 | +2.0568 | +1.6393 | 0.1975 | +1.4418 |
| 4 | 2026-08-30 04:41:05 | LONG | 2026-08-30 05:10:10 | t1 | 29.1 | ws6 | 0.5712 | +0.8543 | +0.5660 | 0.1975 | +0.3685 |
| 5 | 2026-08-30 05:10:15 | SHORT | 2026-08-30 09:41:35 | t1 | 271.3 | ws3 > ws5 > ws7 > ws8 > ws10 > ws11 > ws12 | 1.0787 | +1.4540 | +1.1725 | 0.1975 | +0.9750 |
| 6 | 2026-08-30 09:41:40 | LONG | 2026-08-30 10:12:55 | t2 | 31.2 | ws6 | 0.4113 | +0.4008 | +0.1740 | 0.1975 | -0.0235 |
| 7 | 2026-08-30 10:13:00 | SHORT | 2026-08-30 11:52:55 | t1 | 99.9 | ws3 | 0.6580 | +0.2158 | -0.0158 | 0.1975 | -0.2133 |
| 8 | 2026-08-30 11:53:00 | LONG | 2026-08-30 12:03:55 | DIV REV-TRADE | 10.9 | - | 0.1263 | +0.4579 | +0.4421 | 0.1975 | +0.2446 |
| 9 | 2026-08-30 12:04:00 | SHORT | 2026-08-30 13:16:10 | t2 | 72.2 | ws9 | 1.2786 | +0.0734 | -0.2568 | 0.1975 | -0.4543 |
| 10 | 2026-08-30 13:16:15 | LONG | 2026-08-30 15:45:30 | cws1b counter-oob | 149.2 | ws12 | 0.2456 | +2.2317 | -0.0314 | 0.1975 | -0.2289 |
| 11 | 2026-08-30 15:45:35 | SHORT | 2026-08-30 16:13:05 | cws1b counter-oob | 27.5 | ws12 | 0.7947 | +0.8313 | -0.7581 | 0.1975 | -0.9556 |
| 12 | 2026-08-30 16:13:10 | LONG | 2026-08-30 18:06:25 | t2 | 113.2 | ws4 | 4.2964 | +0.7628 | -2.7657 | 0.1975 | -2.9632 |
| 13 | 2026-08-30 18:06:30 | SHORT | 2026-08-30 21:04:00 | t2 | 177.5 | - | 0.8058 | +5.1283 | +3.7462 | 0.1975 | +3.5487 |
| 14 | 2026-08-30 21:04:05 | LONG | 2026-08-30 22:22:25 | cws1b counter-oob | 78.3 | ws11 | 0.9370 | +1.4858 | -0.7318 | 0.1975 | -0.9293 |
| 15 | 2026-08-30 22:22:30 | LONG | - | no exit | - | - | - | - | - | - | - |
| TOTAL 14 legs | | | | | 1347.4 | | 12.1509 | +18.4593 | +4.9598 | 2.7650 | +2.1948 |

| the read | value |
|---|---|
| legs with an exit | 14 of 15 |
| legs net-positive after drag | 7 of 14 |
| exits on the barrage | 0 |
| MFE collected | 26.9% |
| summed drag in its own right | 2.7650% over 14 round trips |
| legs with no bars, exit before open | 1 |
| seconds to compute | 214.1 |
