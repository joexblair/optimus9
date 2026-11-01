# THE 2-DAY CHAIN - FENCE 75/25, LADDER ws1..ws20, THE LATCH RELEASED ON LIFT-OFF
# WINDOW 2026-08-30 00:00:00 .. 2026-08-31 23:59:55 | TAPE 1632960 bars | RULED_OK False
# RMOM_FNC 75.0 -> (25.0, 75.0) | L2_MOM_MAXTF 20 | LIN2_EXFNC_LATCH_REL 'lift'
# the latch turns ON at an ex-fence cross held 4 bars = 20 s, and is released ONLY by that
#   line's own lift-off on the same side, stamped at lift + LIFT_WOB - 1 = lift + 7 bars = 35 s.
#   and its sampling RESTARTS at the latch-on bar - his 1030 ruling - so the lattice must refill before any release can print.
# the barrage no longer releases the latch on this arm. It is still a cadence, so the column stays.
# LIN2_COUNTER_OOB_ON 0 - his 1030 *"drop the opposing oob side forced exit"*. At 0 the ws1b counter-target-side
#   oob cadence is not produced at all, so no leg can exit on it. Its replacement is UNRULED - his own words.
# the open is 2026-08-29 23:53:55 SHORT, handed in - the router's fire bar off the lin2-reentry signal 2026-08-29 23:53:50.
# the baton fence test reads: latch, released on lift. the 1.1% stop is OFF. drag 0.1975% per round trip, its own column and its own total.
# ts is the bar. pxs is that bar's close unless the row names an extreme. pct is signed to THIS leg.
# baton candidates: every candidate timeframe offered at that bar with its value. "none offered" = a hand-over attempt with no candidate inside lin_hop 2.
# exfnc ltchd: every ws1..ws20 line whose ex-fence latch is ON at that bar, on this leg's side.
# a row whose bar carried a cadence starts **CADENCE:**.

## THE CHAIN SUMMARY - one row per leg, chronological

| day | leg of that day | leg of the chain | the open | dir | the exit | ended by | held min | the rider chain | MAE % | MFE % | realised % | drag % | net % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-29 | 1 | 1 | 2026-08-29 23:53:55 | SHORT | 2026-08-30 01:59:55 | t2 | 126.0 | ws2 | 0.5088 | +1.9536 | +1.3940 | 0.1975 | +1.1965 |
| 2026-08-30 | 1 | 2 | 2026-08-30 02:00:00 | LONG | 2026-08-30 02:45:55 | t2 | 45.9 | ws6 | 0.3560 | +0.4024 | +0.0877 | 0.1975 | -0.1098 |
| 2026-08-30 | 2 | 3 | 2026-08-30 02:46:00 | SHORT | 2026-08-30 03:53:55 | t2 | 67.9 | ws18 | 0.3196 | +1.6238 | +1.2269 | 0.1975 | +1.0294 |
| 2026-08-30 | 3 | 4 | 2026-08-30 03:54:00 | LONG | 2026-08-30 05:10:10 | t1 | 76.2 | ws6 | 0.9864 | +0.4332 | +0.1461 | 0.1975 | -0.0514 |
| 2026-08-30 | 4 | 5 | 2026-08-30 05:10:15 | SHORT | 2026-08-30 09:41:35 | t1 | 271.3 | ws4 > ws6 > ws8 > ws10 > ws12 > ws13 | 1.0787 | +1.4540 | +1.1725 | 0.1975 | +0.9750 |
| 2026-08-30 | 5 | 6 | 2026-08-30 09:41:40 | LONG | 2026-08-30 10:12:55 | t2 | 31.2 | ws4 > ws5 | 0.4113 | +0.4008 | +0.1740 | 0.1975 | -0.0235 |
| 2026-08-30 | 6 | 7 | 2026-08-30 10:13:00 | SHORT | 2026-08-30 11:52:55 | t1 | 99.9 | ws20 | 0.6580 | +0.2158 | -0.0158 | 0.1975 | -0.2133 |
| 2026-08-30 | 7 | 8 | 2026-08-30 11:53:00 | LONG | 2026-08-30 12:03:55 | DIV REV-TRADE | 10.9 | - | 0.1263 | +0.4579 | +0.4421 | 0.1975 | +0.2446 |
| 2026-08-30 | 8 | 9 | 2026-08-30 12:04:00 | SHORT | 2026-08-30 13:16:10 | t2 | 72.2 | ws5 | 1.2786 | +0.0734 | -0.2568 | 0.1975 | -0.4543 |
| 2026-08-30 | 9 | 10 | 2026-08-30 13:16:15 | LONG | 2026-08-30 13:48:40 | retest | 32.4 | ws20 | 0.2456 | +1.6882 | +1.2596 | 0.1975 | +1.0621 |
| 2026-08-30 | 10 | 11 | 2026-08-30 13:48:45 | SHORT | 2026-08-30 14:39:25 | t1 | 50.7 | ws7 | 0.9600 | +1.4504 | +1.2130 | 0.1975 | +1.0155 |
| 2026-08-30 | 11 | 12 | 2026-08-30 14:39:30 | LONG | 2026-08-30 18:06:25 | t2 | 206.9 | ws9 | 3.6313 | +1.4630 | -2.0900 | 0.1975 | -2.2875 |
| 2026-08-30 | 12 | 13 | 2026-08-30 18:06:30 | SHORT | 2026-08-30 21:04:00 | t2 | 177.5 | ws16 | 0.8058 | +5.1283 | +3.7462 | 0.1975 | +3.5487 |
| 2026-08-30 | 13 | 14 | 2026-08-30 21:04:05 | LONG | 2026-08-30 22:02:55 | retest | 58.8 | ws17 | 0.5877 | +1.4858 | +0.8982 | 0.1975 | +0.7007 |
| 2026-08-30 | 14 | 15 | 2026-08-30 22:03:00 | SHORT | 2026-08-30 22:22:25 | DIV REV-TRADE | 19.4 | - | 0.0604 | +1.8188 | +1.6155 | 0.1975 | +1.4180 |
| 2026-08-30 | 15 | 16 | 2026-08-30 22:22:30 | LONG | 2026-08-31 00:19:55 | t2 | 117.4 | ws4 | 5.6130 | +0.1061 | -2.6473 | 0.1975 | -2.8448 |
| 2026-08-31 | 1 | 17 | 2026-08-31 00:20:00 | SHORT | 2026-08-31 01:09:15 | t1 | 49.2 | ws18 | 0.8319 | +0.2467 | -0.0287 | 0.1975 | -0.2262 |
| 2026-08-31 | 2 | 18 | 2026-08-31 01:09:20 | LONG | 2026-08-31 03:24:25 | t1 | 135.1 | ws4 | 2.1335 | +0.5965 | -0.8029 | 0.1975 | -1.0004 |
| 2026-08-31 | 3 | 19 | 2026-08-31 03:24:30 | SHORT | 2026-08-31 04:23:25 | t1 | 58.9 | ws16 | 0.7747 | +1.8444 | +1.2142 | 0.1975 | +1.0167 |
| 2026-08-31 | 4 | 20 | 2026-08-31 04:23:30 | LONG | 2026-08-31 04:57:20 | t2 | 33.8 | ws10 | 0.2926 | +0.6321 | +0.2692 | 0.1975 | +0.0717 |
| 2026-08-31 | 5 | 21 | 2026-08-31 04:57:25 | SHORT | 2026-08-31 08:23:55 | retest | 206.5 | ws5 | 3.2454 | +0.1868 | -2.1830 | 0.1975 | -2.3805 |
| 2026-08-31 | 6 | 22 | 2026-08-31 08:24:00 | LONG | 2026-08-31 10:43:30 | t1 | 139.5 | ws3 > ws5 | 0.8854 | +1.1653 | +0.0571 | 0.1975 | -0.1404 |
| 2026-08-31 | 7 | 23 | 2026-08-31 10:43:35 | SHORT | 2026-08-31 11:54:30 | t1 | 70.9 | ws20 | 0.7593 | +1.0904 | +0.7821 | 0.1975 | +0.5846 |
| 2026-08-31 | 8 | 24 | 2026-08-31 11:54:35 | LONG | 2026-08-31 13:04:55 | t2 | 70.3 | ws4 | 1.0300 | +1.1105 | -0.4316 | 0.1975 | -0.6291 |
| 2026-08-31 | 9 | 25 | 2026-08-31 13:05:00 | SHORT | 2026-08-31 15:21:35 | t1 | 136.6 | ws17 | 1.7799 | +0.8322 | +0.0809 | 0.1975 | -0.1166 |
| 2026-08-31 | 10 | 26 | 2026-08-31 15:21:40 | LONG | 2026-08-31 17:43:55 | t2 | 142.2 | ws2 > ws3 > ws13 | 0.5784 | +1.7293 | +1.2551 | 0.1975 | +1.0576 |
| 2026-08-31 | 11 | 27 | 2026-08-31 17:44:00 | SHORT | 2026-08-31 19:23:15 | t1 | 99.2 | ws5 | 3.6043 | +0.0685 | -1.1481 | 0.1975 | -1.3456 |
| 2026-08-31 | 12 | 28 | 2026-08-31 19:23:20 | LONG | 2026-08-31 21:37:00 | t1 | 133.7 | ws12 | 0.9092 | +0.9939 | +0.6664 | 0.1975 | +0.4689 |
| 2026-08-31 | 13 | 29 | 2026-08-31 21:37:05 | SHORT | 2026-08-31 22:21:50 | t1 | 44.8 | ws20 | 0.1683 | +1.0154 | +0.8471 | 0.1975 | +0.6496 |
| 2026-08-31 | 14 | 30 | 2026-08-31 22:21:55 | LONG | - | no exhaust | - | - | - | - | - | - | - |
| TOTAL | | 29 scored legs | | | | | 2785.6 | | 34.6205 | +31.6674 | +8.9436 | 5.7275 | +3.2161 |

## 2026-08-30 leg 1 - LONG   opens 2026-08-30 02:00:00   exits 2026-08-30 02:45:55 on t2   held 45.9 min   MAE 0.3560   MFE 0.4024   realised +0.0877   net -0.1098

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 02:00:00 | >>> THIS LEG OPENS LONG | - | 5: ws2,ws3,ws4,ws5,ws6 | last 14:28:50, 691.2 min ago | 0.193820 | +0.0000 |
| 2026-08-30 02:27:00 | the ADVERSE extreme - MAE 0.3560 | - | 1: ws6 | last 14:28:50, 718.2 min ago | 0.193130 | -0.3560 |
| 2026-08-30 02:42:00 | ARM - ws1b+ws1r: ws1b 108.27 + ws1r 89.24 oob, ws1b dwell 0 | - | 2: ws1,ws6 | last 14:28:50, 733.2 min ago / counter-side 2026-08-30 02:35:20 | 0.194450 | +0.3250 |
| 2026-08-30 02:42:00 | RIDER rider ws6 - ws6 r 51.01, the highest ex-fence | - | 2: ws1,ws6 | last 14:28:50, 733.2 min ago / counter-side 2026-08-30 02:35:20 | 0.194450 | +0.3250 |
| 2026-08-30 02:42:00 | RETEST - ws1r 89.24 oob + ws2r 61.29 / ws3r 52.08 in - the gate opens; ws1r oob->ib cross 2026-08-30 02:45:00, wob 12, cadence at 2026-08-30 02:45:55 | - | 2: ws1,ws6 | last 14:28:50, 733.2 min ago / counter-side 2026-08-30 02:35:20 | 0.194450 | +0.3250 |
| 2026-08-30 02:43:00 | the favourable extreme - MFE 0.4024 | - | 2: ws1,ws6 | last 14:28:50, 734.2 min ago / counter-side 2026-08-30 02:35:20 | 0.194600 | +0.4024 |
| 2026-08-30 02:45:55 | **CADENCE:** RIDER rider ws6 - v4-arm-lineage-retest: the re-scan rides ws6 46.10, the highest ex-fence | - | 1: ws6 | last 14:28:50, 737.1 min ago / counter-side 2026-08-30 02:35:20 | 0.193990 | +0.0877 |
| 2026-08-30 02:45:55 | **CADENCE:** EXHAUST rider ws6 - t2 ws1r ib cross 02:45:00 confirmed 02:45:55 at wob 12, ws1b 64.63 not oob, ws1b hold 0 \| mage-cascade down OPPOSES the LONG - rev-trade | - | 1: ws6 | last 14:28:50, 737.1 min ago / counter-side 2026-08-30 02:35:20 | 0.193990 | +0.0877 |
| 2026-08-30 02:45:55 | THIS LEG CLOSES on t2, realised +0.0877, drag 0.1975, net -0.1098 | - | 1: ws6 | last 14:28:50, 737.1 min ago / counter-side 2026-08-30 02:35:20 | 0.193990 | +0.0877 |

## 2026-08-30 leg 2 - SHORT   opens 2026-08-30 02:46:00   exits 2026-08-30 03:53:55 on t2   held 67.9 min   MAE 0.3196   MFE 1.6238   realised +1.2269   net +1.0294

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 02:46:00 | >>> THIS LEG OPENS SHORT | - | 2: ws18,ws20 | last 02:35:20, 10.7 min ago | 0.193990 | -0.0000 |
| 2026-08-30 02:53:00 | the ADVERSE extreme - MAE 0.3196 | - | 3: ws1,ws18,ws20 | last 02:35:20, 17.7 min ago | 0.194610 | -0.3196 |
| 2026-08-30 03:00:30 | ARM - ws1b+ws1r: ws1b 8.49 + ws1r 7.68 oob, ws1b dwell 0 | - | 4: ws1,ws2,ws15,ws18 | last 02:35:20, 25.2 min ago | 0.193210 | +0.4021 |
| 2026-08-30 03:00:30 | RIDER rider ws18 - ws18 r 19.17, the highest ex-fence | - | 4: ws1,ws2,ws15,ws18 | last 02:35:20, 25.2 min ago | 0.193210 | +0.4021 |
| 2026-08-30 03:00:30 | RETEST - ws2r 18.72 / ws3r 41.07 - not both inside the fence at the arm | - | 4: ws1,ws2,ws15,ws18 | last 02:35:20, 25.2 min ago | 0.193210 | +0.4021 |
| 2026-08-30 03:14:55 | the favourable extreme - MFE 1.6238 | - | 5: ws3,ws4,ws14,ws15,ws18 | last 02:35:20, 39.6 min ago | 0.190840 | +1.6238 |
| 2026-08-30 03:18:55 | NO PASS rider ws18 - ws18 22.04 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 2: ws5,ws14 | last 02:35:20, 43.6 min ago | 0.192250 | +0.8970 |
| 2026-08-30 03:42:55 | LATCH1 rider ws18 - latch 1 at the t2 cadence 2026-08-30 03:42:55, divergence state -1 | - | 4: ws1,ws18,ws19,ws20 | last 02:35:20, 67.6 min ago | 0.192430 | +0.8042 |
| 2026-08-30 03:42:55 | **CADENCE:** NO ACTION rider ws18 - t2 ws1r ib cross 03:42:00 confirmed 03:42:55 at wob 12, ws1b 43.12 not oob, ws1b hold 0 \| mage-cascade down matches the SHORT - no action, keep walking | - | 4: ws1,ws18,ws19,ws20 | last 02:35:20, 67.6 min ago | 0.192430 | +0.8042 |
| 2026-08-30 03:53:55 | LATCH1 rider ws18 - latch 1 at the t2 cadence 2026-08-30 03:53:55, divergence state -1 | - | 7: ws3,ws8,ws9,ws10,ws18,ws19,ws20 | last 02:35:20, 78.6 min ago | 0.191670 | +1.1959 |
| 2026-08-30 03:53:55 | **CADENCE:** EXHAUST rider ws18 - t2 ws1r ib cross 03:53:00 confirmed 03:53:55 at wob 12, ws1b 17.82 not oob, ws1b hold 0 \| LIN2_MATRY_WSF_TAKEOVER: rider ws18 is at or over ws7 and ws1 24.60 + ws2 27.45 are both under the target oob fence at 2026-08-30 03:53:55 (event anchor) - rev-trade | - | 7: ws3,ws8,ws9,ws10,ws18,ws19,ws20 | last 02:35:20, 78.6 min ago | 0.191670 | +1.1959 |
| 2026-08-30 03:53:55 | THIS LEG CLOSES on t2, realised +1.2269, drag 0.1975, net +1.0294 | - | 7: ws3,ws8,ws9,ws10,ws18,ws19,ws20 | last 02:35:20, 78.6 min ago | 0.191670 | +1.1959 |

## 2026-08-30 leg 3 - LONG   opens 2026-08-30 03:54:00   exits 2026-08-30 05:10:10 on t1   held 76.2 min   MAE 0.9864   MFE 0.4332   realised +0.1461   net -0.0514

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 03:54:00 | >>> THIS LEG OPENS LONG | - | 2: ws3,ws4 | last 14:28:50, 805.2 min ago / counter-side 2026-08-30 02:35:20 | 0.191610 | +0.0000 |
| 2026-08-30 04:47:20 | the ADVERSE extreme - MAE 0.9864 | - | none | last 14:28:50, 858.5 min ago / counter-side 2026-08-30 02:35:20 | 0.189720 | -0.9864 |
| 2026-08-30 05:03:15 | ARM - ws1b+ws1r: ws1b 99.46 + ws1r 85.53 oob, ws1b dwell 0 | - | 3: ws1,ws2,ws6 | last 14:28:50, 874.4 min ago / counter-side 2026-08-30 02:35:20 | 0.191660 | +0.0261 |
| 2026-08-30 05:03:15 | RIDER rider ws6 - ws6 r 76.23, the highest ex-fence | - | 3: ws1,ws2,ws6 | last 14:28:50, 874.4 min ago / counter-side 2026-08-30 02:35:20 | 0.191660 | +0.0261 |
| 2026-08-30 05:03:15 | RETEST - ws2r 75.45 / ws3r 64.71 - not both inside the fence at the arm | - | 3: ws1,ws2,ws6 | last 14:28:50, 874.4 min ago / counter-side 2026-08-30 02:35:20 | 0.191660 | +0.0261 |
| 2026-08-30 05:07:35 | the favourable extreme - MFE 0.4332 | - | 5: ws2,ws3,ws4,ws6,ws9 | last 14:28:50, 878.8 min ago / counter-side 2026-08-30 02:35:20 | 0.192440 | +0.4332 |
| 2026-08-30 05:10:10 | **CADENCE:** EXHAUST rider ws6 - t1 ws1b oob 05:01:15..05:10:05, ws1r reversed 05:05:25 during, stamp 05:05:25 \| mage-cascade down OPPOSES the LONG - rev-trade | - | 3: ws3,ws6,ws9 | last 14:28:50, 881.3 min ago / counter-side 2026-08-30 02:35:20 | 0.191880 | +0.1409 |
| 2026-08-30 05:10:10 | THIS LEG CLOSES on t1, realised +0.1461, drag 0.1975, net -0.0514 | - | 3: ws3,ws6,ws9 | last 14:28:50, 881.3 min ago / counter-side 2026-08-30 02:35:20 | 0.191880 | +0.1409 |

## 2026-08-31 leg 9 - SHORT   opens 2026-08-31 13:05:00   exits 2026-08-31 15:21:35 on t1   held 136.6 min   MAE 1.7799   MFE 0.8322   realised +0.0809   net -0.1166

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-31 13:05:00 | >>> THIS LEG OPENS SHORT | - | 4: ws7,ws8,ws15,ws17 | last 23:49:30, 795.5 min ago / counter-side 2026-08-31 07:29:25 | 0.173040 | -0.0000 |
| 2026-08-31 13:51:10 | the favourable extreme - MFE 0.8322 | - | 9: ws1,ws8,ws11,ws12,ws15,ws16,ws17,ws18,ws19 | last 23:49:30, 841.7 min ago / counter-side 2026-08-31 13:44:00 | 0.171600 | +0.8322 |
| 2026-08-31 14:44:05 | the ADVERSE extreme - MAE 1.7799 | - | 4: ws12,ws15,ws16,ws17 | last 23:49:30, 894.6 min ago / counter-side 2026-08-31 14:32:40 | 0.176120 | -1.7799 |
| 2026-08-31 15:10:10 | ARM - ws1b+ws1r: ws1b 12.13 + ws1r 10.03 oob, ws1b dwell 0 | - | 8: ws1,ws2,ws3,ws4,ws12,ws15,ws16,ws17 | last 23:49:30, 920.7 min ago / counter-side 2026-08-31 14:32:40 | 0.173430 | -0.2254 |
| 2026-08-31 15:10:10 | RIDER rider ws17 - ws17 r 58.87, the highest ex-fence | - | 8: ws1,ws2,ws3,ws4,ws12,ws15,ws16,ws17 | last 23:49:30, 920.7 min ago / counter-side 2026-08-31 14:32:40 | 0.173430 | -0.2254 |
| 2026-08-31 15:10:10 | RETEST - ws2r 16.55 / ws3r 15.61 - not both inside the fence at the arm | - | 8: ws1,ws2,ws3,ws4,ws12,ws15,ws16,ws17 | last 23:49:30, 920.7 min ago / counter-side 2026-08-31 14:32:40 | 0.173430 | -0.2254 |
| 2026-08-31 15:21:35 | **CADENCE:** EXHAUST rider ws17 - t1 ws1b oob 15:16:15..15:21:30, ws1r reversed 15:19:35 during, stamp 15:19:35 \| mage-cascade up OPPOSES the SHORT - rev-trade | - | 7: ws2,ws5,ws6,ws7,ws12,ws16,ws17 | last 23:49:30, 932.1 min ago / counter-side 2026-08-31 14:32:40 | 0.172780 | +0.1503 |
| 2026-08-31 15:21:35 | THIS LEG CLOSES on t1, realised +0.0809, drag 0.1975, net -0.1166 | - | 7: ws2,ws5,ws6,ws7,ws12,ws16,ws17 | last 23:49:30, 932.1 min ago / counter-side 2026-08-31 14:32:40 | 0.172780 | +0.1503 |

## 2026-08-31 leg 10 - LONG   opens 2026-08-31 15:21:40   exits 2026-08-31 17:43:55 on t2   held 142.2 min   MAE 0.5784   MFE 1.7293   realised +1.2551   net +1.0576

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-31 15:21:40 | >>> THIS LEG OPENS LONG | - | 2: ws15,ws18 | last 14:32:40, 49.0 min ago | 0.172900 | +0.0000 |
| 2026-08-31 16:26:35 | the ADVERSE extreme - MAE 0.5784 | - | none | last 14:32:40, 113.9 min ago | 0.171900 | -0.5784 |
| 2026-08-31 16:44:05 | ARM - ws1b+ws1r: ws1b 105.36 + ws1r 88.45 oob, ws1b dwell 0 | - | 2: ws1,ws2 | last 14:32:40, 131.4 min ago | 0.173620 | +0.4164 |
| 2026-08-31 16:44:05 | RIDER rider ws2 - ws2 r 85.71, the highest ex-fence | - | 2: ws1,ws2 | last 14:32:40, 131.4 min ago | 0.173620 | +0.4164 |
| 2026-08-31 16:44:05 | RETEST - ws2r 85.71 / ws3r 70.49 - not both inside the fence at the arm | - | 2: ws1,ws2 | last 14:32:40, 131.4 min ago | 0.173620 | +0.4164 |
| 2026-08-31 16:50:05 | BATON rider ws2 - ws2 -> ws3, between cadences, lin_hop 2 | ws3: 79.43 | 1: ws3 | last 14:32:40, 137.4 min ago | 0.173640 | +0.4280 |
| 2026-08-31 16:50:15 | NO PASS rider ws3 - ws3 80.63 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | none | last 14:32:40, 137.6 min ago | 0.173750 | +0.4916 |
| 2026-08-31 17:14:20 | LATCH1 rider ws3 - latch 1 at the t1 cadence 2026-08-31 17:14:20, divergence state +1 | - | 4: ws1,ws6,ws7,ws10 | last 14:32:40, 161.7 min ago | 0.174640 | +1.0064 |
| 2026-08-31 17:14:20 | **CADENCE:** NO ACTION rider ws3 - t1 ws1b ib 17:14:15, ws1r reversed 17:14:20 inside the 120s grace, stamp 17:14:20 \| mage-cascade up matches the LONG - no action, keep walking | - | 4: ws1,ws6,ws7,ws10 | last 14:32:40, 161.7 min ago | 0.174640 | +1.0064 |
| 2026-08-31 17:16:35 | LATCH1 rider ws3 - latch 1 at the t2 cadence 2026-08-31 17:16:35, divergence state +1 | - | 3: ws6,ws7,ws10 | last 14:32:40, 163.9 min ago | 0.174440 | +0.8907 |
| 2026-08-31 17:16:35 | **CADENCE:** NO ACTION rider ws3 - t2 ws1r ib cross 17:15:40 confirmed 17:16:35 at wob 12, ws1b 75.04 not oob, ws1b hold 0 \| mage-cascade up matches the LONG - no action, keep walking | - | 3: ws6,ws7,ws10 | last 14:32:40, 163.9 min ago | 0.174440 | +0.8907 |
| 2026-08-31 17:34:35 | LATCH1 rider ws3 - latch 1 at the t1 cadence 2026-08-31 17:34:35, divergence state +1 | - | 5: ws6,ws8,ws9,ws11,ws13 | last 14:32:40, 181.9 min ago | 0.174550 | +0.9543 |
| 2026-08-31 17:34:35 | **CADENCE:** NO ACTION rider ws3 - t1 ws1b ib 17:34:30, ws1r reversed 17:34:35 inside the 120s grace, stamp 17:34:35 \| mage-cascade up matches the LONG - no action, keep walking | - | 5: ws6,ws8,ws9,ws11,ws13 | last 14:32:40, 181.9 min ago | 0.174550 | +0.9543 |
| 2026-08-31 17:41:30 | the favourable extreme - MFE 1.7293 | - | 6: ws2,ws6,ws9,ws11,ws12,ws13 | last 14:32:40, 188.8 min ago | 0.175890 | +1.7293 |
| 2026-08-31 17:43:40 | LATCH1 rider ws3 - latch 1 at the t1 cadence 2026-08-31 17:43:40, divergence state +1 | - | 6: ws2,ws6,ws9,ws11,ws12,ws13 | last 14:32:40, 191.0 min ago | 0.175040 | +1.2377 |
| 2026-08-31 17:43:40 | **CADENCE:** CADENCE rider ws3 - t1 ws1b oob 17:36:45..17:43:35, ws1r reversed 17:42:55 during, stamp 17:42:55 \| rider ws3 55.85, no-longer-exfence yes, reversed yes \| mage-cascade neither | ws6: 57.95, ws9: 82.38, ws11: 89.31, ws12: 85.99, ws13: 85.71 | 6: ws2,ws6,ws9,ws11,ws12,ws13 | last 14:32:40, 191.0 min ago | 0.175040 | +1.2377 |
| 2026-08-31 17:43:40 | **CADENCE:** BATON rider ws3 - ws3 -> ws13, at a t1 cadence, whole board | ws6: 57.95, ws9: 82.38, ws11: 89.31, ws12: 85.99, ws13: 85.71 | 6: ws2,ws6,ws9,ws11,ws12,ws13 | last 14:32:40, 191.0 min ago | 0.175040 | +1.2377 |
| 2026-08-31 17:43:55 | LATCH1 rider ws13 - latch 1 at the t2 cadence 2026-08-31 17:43:55, divergence state +1 | - | 5: ws2,ws6,ws11,ws12,ws13 | last 14:32:40, 191.2 min ago | 0.175070 | +1.2551 |
| 2026-08-31 17:43:55 | **CADENCE:** EXHAUST rider ws13 - t2 ws1r ib cross 17:43:00 confirmed 17:43:55 at wob 12, ws1b 83.01 not oob, ws1b hold 0 \| LIN2_MATRY_WSF_TAKEOVER: rider ws13 is at or over ws7 and ws3 56.28 + ws4 52.26 are both under the target oob fence at 2026-08-31 17:43:55 (event anchor) - rev-trade | - | 5: ws2,ws6,ws11,ws12,ws13 | last 14:32:40, 191.2 min ago | 0.175070 | +1.2551 |
| 2026-08-31 17:43:55 | THIS LEG CLOSES on t2, realised +1.2551, drag 0.1975, net +1.0576 | - | 5: ws2,ws6,ws11,ws12,ws13 | last 14:32:40, 191.2 min ago | 0.175070 | +1.2551 |

## 2026-08-31 leg 11 - SHORT   opens 2026-08-31 17:44:00   exits 2026-08-31 19:23:15 on t1   held 99.2 min   MAE 3.6043   MFE 0.0685   realised -1.1481   net -1.3456

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-31 17:44:00 | >>> THIS LEG OPENS SHORT | - | 5: ws2,ws4,ws12,ws15,ws16 | last 23:49:30, 1074.5 min ago / counter-side 2026-08-31 14:32:40 | 0.175070 | -0.0000 |
| 2026-08-31 17:46:20 | the favourable extreme - MFE 0.0685 | - | 4: ws4,ws12,ws15,ws16 | last 23:49:30, 1076.8 min ago / counter-side 2026-08-31 14:32:40 | 0.174950 | +0.0685 |
| 2026-08-31 18:44:55 | the ADVERSE extreme - MAE 3.6043 | - | 1: ws16 | last 23:49:30, 1135.4 min ago / counter-side 2026-08-31 18:33:35 | 0.181380 | -3.6043 |
| 2026-08-31 19:12:00 | ARM - ws4r: ws4r 13.35 oob | - | 2: ws4,ws5 | last 23:49:30, 1162.5 min ago / counter-side 2026-08-31 18:33:35 | 0.178590 | -2.0106 |
| 2026-08-31 19:12:00 | RIDER rider ws5 - ws5 r 21.47, the highest ex-fence | - | 2: ws4,ws5 | last 23:49:30, 1162.5 min ago / counter-side 2026-08-31 18:33:35 | 0.178590 | -2.0106 |
| 2026-08-31 19:12:00 | RETEST - ws1r 52.51 is not oob at the arm - the gate stays shut | - | 2: ws4,ws5 | last 23:49:30, 1162.5 min ago / counter-side 2026-08-31 18:33:35 | 0.178590 | -2.0106 |
| 2026-08-31 19:23:15 | LATCH1 rider ws5 - latch 1 at the t1 cadence 2026-08-31 19:23:15, divergence state -1 | - | 6: ws2,ws4,ws5,ws6,ws7,ws8 | last 23:49:30, 1173.8 min ago / counter-side 2026-08-31 18:33:35 | 0.176980 | -1.0910 |
| 2026-08-31 19:23:15 | **CADENCE:** EXHAUST rider ws5 - t1 ws1b oob 19:19:10..19:23:10, ws1r reversed 19:22:05 during, stamp 19:22:05 \| mage-cascade up OPPOSES the SHORT - rev-trade | - | 6: ws2,ws4,ws5,ws6,ws7,ws8 | last 23:49:30, 1173.8 min ago / counter-side 2026-08-31 18:33:35 | 0.176980 | -1.0910 |
| 2026-08-31 19:23:15 | THIS LEG CLOSES on t1, realised -1.1481, drag 0.1975, net -1.3456 | - | 6: ws2,ws4,ws5,ws6,ws7,ws8 | last 23:49:30, 1173.8 min ago / counter-side 2026-08-31 18:33:35 | 0.176980 | -1.0910 |

| the read | value |
|---|---|
| legs in the chain over the two days | 30 |
| legs opening on 2026-08-30 | 15 |
| legs opening on 2026-08-31 | 14 |
| legs opening on 2026-08-29 | 1 |
| seconds to compute | 334.7 |
