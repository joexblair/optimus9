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
| 2026-08-31 | 10 | 26 | 2026-08-31 15:21:40 | LONG | 2026-08-31 18:33:35 | barrage | 191.9 | ws2 > ws3 > ws13 > ws15 | 0.5784 | +3.4702 | +2.8571 | 0.1975 | +2.6596 |
| 2026-08-31 | 11 | 27 | 2026-08-31 18:33:40 | SHORT | 2026-08-31 19:23:15 | t1 | 49.6 | ws5 | 1.9906 | +1.0121 | +0.4274 | 0.1975 | +0.2299 |
| 2026-08-31 | 12 | 28 | 2026-08-31 19:23:20 | LONG | 2026-08-31 21:37:00 | t1 | 133.7 | ws12 | 0.9092 | +0.9939 | +0.6664 | 0.1975 | +0.4689 |
| 2026-08-31 | 13 | 29 | 2026-08-31 21:37:05 | SHORT | 2026-08-31 22:21:50 | t1 | 44.8 | ws20 | 0.1683 | +1.0154 | +0.8471 | 0.1975 | +0.6496 |
| 2026-08-31 | 14 | 30 | 2026-08-31 22:21:55 | LONG | - | no exhaust | - | - | - | - | - | - | - |
| TOTAL | | 29 scored legs | | | | | 2785.6 | | 33.0067 | +34.3519 | +12.1212 | 5.7275 | +6.3937 |

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
| 2026-08-30 03:53:55 | **CADENCE:** EXHAUST rider ws18 - t2 ws1r ib cross 03:53:00 confirmed 03:53:55 at wob 12, ws1b 17.82 not oob, ws1b hold 0 \| LIN2_MATRY_WSF_TAKEOVER: rider ws18 is at or over ws15 and ws1 24.60 + ws2 27.45 are both under the target oob fence at 2026-08-30 03:53:55 (event anchor) - rev-trade | - | 7: ws3,ws8,ws9,ws10,ws18,ws19,ws20 | last 02:35:20, 78.6 min ago | 0.191670 | +1.1959 |
| 2026-08-30 03:53:55 | THIS LEG CLOSES on t2, realised +1.2269, drag 0.1975, net +1.0294 | - | 7: ws3,ws8,ws9,ws10,ws18,ws19,ws20 | last 02:35:20, 78.6 min ago | 0.191670 | +1.1959 |

## 2026-08-30 leg 4 - SHORT   opens 2026-08-30 05:10:15   exits 2026-08-30 09:41:35 on t1   held 271.3 min   MAE 1.0787   MFE 1.4540   realised +1.1725   net +0.9750

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 05:10:15 | >>> THIS LEG OPENS SHORT | - | 2: ws8,ws12 | last 02:35:20, 154.9 min ago | 0.191890 | -0.0000 |
| 2026-08-30 06:59:15 | the ADVERSE extreme - MAE 1.0787 | - | none | last 02:35:20, 263.9 min ago | 0.193960 | -1.0787 |
| 2026-08-30 07:24:20 | ARM - ws4r: ws4r 6.72 oob | - | 3: ws2,ws3,ws4 | last 02:35:20, 289.0 min ago | 0.192250 | -0.1876 |
| 2026-08-30 07:24:20 | RIDER rider ws4 - ws4 r 6.72, the highest ex-fence | - | 3: ws2,ws3,ws4 | last 02:35:20, 289.0 min ago | 0.192250 | -0.1876 |
| 2026-08-30 07:24:20 | RETEST - ws2r 18.89 / ws3r 12.22 - not both inside the fence at the arm | - | 3: ws2,ws3,ws4 | last 02:35:20, 289.0 min ago | 0.192250 | -0.1876 |
| 2026-08-30 07:44:35 | BATON rider ws4 - ws4 -> ws6, between cadences, lin_hop 2 | ws5: 3.81, ws6: 4.22 | 5: ws2,ws5,ws6,ws7,ws8 | last 02:35:20, 309.2 min ago | 0.191070 | +0.4273 |
| 2026-08-30 07:45:45 | BATON rider ws6 - ws6 -> ws8, between cadences, lin_hop 2 | ws7: 4.73, ws8: 14.38 | 3: ws2,ws7,ws8 | last 02:35:20, 310.4 min ago | 0.191340 | +0.2866 |
| 2026-08-30 07:54:25 | BATON rider ws8 - ws8 -> ws10, between cadences, lin_hop 2 | ws10: 22.72 | 2: ws10,ws11 | last 02:35:20, 319.1 min ago | 0.191690 | +0.1042 |
| 2026-08-30 08:10:35 | BATON rider ws10 - ws10 -> ws12, between cadences, lin_hop 2 | ws11: 13.64, ws12: 23.58 | 5: ws6,ws9,ws11,ws12,ws13 | last 02:35:20, 335.2 min ago | 0.191250 | +0.3335 |
| 2026-08-30 08:18:40 | BATON rider ws12 - ws12 -> ws13, between cadences, lin_hop 2 | ws13: 15.18 | 3: ws6,ws11,ws13 | last 02:35:20, 343.3 min ago | 0.191600 | +0.1511 |
| 2026-08-30 08:19:00 | NO PASS rider ws13 - ws13 15.18 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 3: ws6,ws11,ws13 | last 02:35:20, 343.7 min ago | 0.191600 | +0.1511 |
| 2026-08-30 09:40:50 | the favourable extreme - MFE 1.4540 | - | 7: ws4,ws10,ws13,ws15,ws17,ws18,ws20 | last 02:35:20, 425.5 min ago | 0.189100 | +1.4540 |
| 2026-08-30 09:41:35 | LATCH1 rider ws13 - latch 1 at the t1 cadence 2026-08-30 09:41:35, divergence state -1 | - | 7: ws4,ws10,ws13,ws15,ws17,ws18,ws20 | last 02:35:20, 426.2 min ago | 0.189570 | +1.2090 |
| 2026-08-30 09:41:35 | **CADENCE:** EXHAUST rider ws13 - t1 ws1b oob 09:41:25..09:41:30, ws1r reversed 09:41:30 during, stamp 09:41:30 \| mage-cascade up OPPOSES the SHORT - rev-trade | - | 7: ws4,ws10,ws13,ws15,ws17,ws18,ws20 | last 02:35:20, 426.2 min ago | 0.189570 | +1.2090 |
| 2026-08-30 09:41:35 | THIS LEG CLOSES on t1, realised +1.1725, drag 0.1975, net +0.9750 | - | 7: ws4,ws10,ws13,ws15,ws17,ws18,ws20 | last 02:35:20, 426.2 min ago | 0.189570 | +1.2090 |

## 2026-08-30 leg 6 - SHORT   opens 2026-08-30 10:13:00   exits 2026-08-30 11:52:55 on t1   held 99.9 min   MAE 0.6580   MFE 0.2158   realised -0.0158   net -0.2133

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 10:13:00 | >>> THIS LEG OPENS SHORT | - | 5: ws1,ws14,ws15,ws16,ws17 | last 10:06:00, 7.0 min ago | 0.189970 | -0.0000 |
| 2026-08-30 11:10:10 | the ADVERSE extreme - MAE 0.6580 | - | 6: ws2,ws14,ws16,ws17,ws19,ws20 | last 10:06:00, 64.2 min ago | 0.191220 | -0.6580 |
| 2026-08-30 11:44:00 | ARM - ws4r: ws4r 13.46 oob | - | 6: ws1,ws6,ws7,ws16,ws19,ws20 | last 10:06:00, 98.0 min ago | 0.190050 | -0.0421 |
| 2026-08-30 11:44:00 | RIDER rider ws20 - ws20 r 69.90, the highest ex-fence | - | 6: ws1,ws6,ws7,ws16,ws19,ws20 | last 10:06:00, 98.0 min ago | 0.190050 | -0.0421 |
| 2026-08-30 11:44:00 | RETEST - ws1r 69.17 is not oob at the arm - the gate stays shut | - | 6: ws1,ws6,ws7,ws16,ws19,ws20 | last 10:06:00, 98.0 min ago | 0.190050 | -0.0421 |
| 2026-08-30 11:48:30 | the favourable extreme - MFE 0.2158 | - | 9: ws1,ws3,ws4,ws5,ws6,ws7,ws8,ws16,ws20 | last 10:06:00, 102.5 min ago | 0.189560 | +0.2158 |
| 2026-08-30 11:52:55 | LATCH1 rider ws20 - latch 1 at the t1 cadence 2026-08-30 11:52:55, divergence state -1 | - | 8: ws1,ws5,ws6,ws7,ws8,ws9,ws16,ws20 | last 10:06:00, 106.9 min ago | 0.189760 | +0.1105 |
| 2026-08-30 11:52:55 | **CADENCE:** EXHAUST rider ws20 - t1 ws1b oob 11:51:45..11:52:50, ws1r reversed 11:52:45 during, stamp 11:52:45 \| mage-cascade up OPPOSES the SHORT - rev-trade | - | 8: ws1,ws5,ws6,ws7,ws8,ws9,ws16,ws20 | last 10:06:00, 106.9 min ago | 0.189760 | +0.1105 |
| 2026-08-30 11:52:55 | THIS LEG CLOSES on t1, realised -0.0158, drag 0.1975, net -0.2133 | - | 8: ws1,ws5,ws6,ws7,ws8,ws9,ws16,ws20 | last 10:06:00, 106.9 min ago | 0.189760 | +0.1105 |

## 2026-08-31 leg 2 - LONG   opens 2026-08-31 01:09:20   exits 2026-08-31 03:24:25 on t1   held 135.1 min   MAE 2.1335   MFE 0.5965   realised -0.8029   net -1.0004

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-31 01:09:20 | >>> THIS LEG OPENS LONG | - | 6: ws4,ws13,ws14,ws15,ws16,ws17 | last 16:19:30, 529.8 min ago / counter-side 2026-08-30 23:49:30 | 0.174360 | +0.0000 |
| 2026-08-31 01:20:20 | the favourable extreme - MFE 0.5965 | - | 9: ws8,ws9,ws14,ws15,ws16,ws17,ws18,ws19,ws20 | last 16:19:30, 540.8 min ago / counter-side 2026-08-30 23:49:30 | 0.175400 | +0.5965 |
| 2026-08-31 02:52:30 | the ADVERSE extreme - MAE 2.1335 | - | 4: ws14,ws17,ws19,ws20 | last 16:19:30, 633.0 min ago / counter-side 2026-08-30 23:49:30 | 0.170640 | -2.1335 |
| 2026-08-31 03:20:00 | ARM - ws4r: ws4r 93.01 oob | - | 1: ws4 | last 16:19:30, 660.5 min ago / counter-side 2026-08-30 23:49:30 | 0.172460 | -1.0897 |
| 2026-08-31 03:20:00 | RIDER rider ws4 - ws4 r 93.01, the highest ex-fence | - | 1: ws4 | last 16:19:30, 660.5 min ago / counter-side 2026-08-30 23:49:30 | 0.172460 | -1.0897 |
| 2026-08-31 03:20:00 | RETEST - ws1r 54.36 is not oob at the arm - the gate stays shut | - | 1: ws4 | last 16:19:30, 660.5 min ago / counter-side 2026-08-30 23:49:30 | 0.172460 | -1.0897 |
| 2026-08-31 03:24:25 | LATCH1 rider ws4 - latch 1 at the t1 cadence 2026-08-31 03:24:25, divergence state +1 | - | 2: ws1,ws4 | last 16:19:30, 664.9 min ago / counter-side 2026-08-30 23:49:30 | 0.172930 | -0.8201 |
| 2026-08-31 03:24:25 | **CADENCE:** EXHAUST rider ws4 - t1 ws1b ib 03:23:55, ws1r reversed 03:24:25 inside the 120s grace, stamp 03:24:25 \| mage-cascade down OPPOSES the LONG - rev-trade | - | 2: ws1,ws4 | last 16:19:30, 664.9 min ago / counter-side 2026-08-30 23:49:30 | 0.172930 | -0.8201 |
| 2026-08-31 03:24:25 | THIS LEG CLOSES on t1, realised -0.8029, drag 0.1975, net -1.0004 | - | 2: ws1,ws4 | last 16:19:30, 664.9 min ago / counter-side 2026-08-30 23:49:30 | 0.172930 | -0.8201 |

## 2026-08-31 leg 4 - LONG   opens 2026-08-31 04:23:30   exits 2026-08-31 04:57:20 on t2   held 33.8 min   MAE 0.2926   MFE 0.6321   realised +0.2692   net +0.0717

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-31 04:23:30 | >>> THIS LEG OPENS LONG | - | 3: ws1,ws3,ws10 | last 16:19:30, 724.0 min ago / counter-side 2026-08-30 23:49:30 | 0.170860 | +0.0000 |
| 2026-08-31 04:46:35 | the ADVERSE extreme - MAE 0.2926 | - | 1: ws10 | last 16:19:30, 747.1 min ago / counter-side 2026-08-30 23:49:30 | 0.170360 | -0.2926 |
| 2026-08-31 04:53:35 | ARM - ws4r: ws4r 85.45 oob | - | 3: ws1,ws4,ws10 | last 16:19:30, 754.1 min ago / counter-side 2026-08-30 23:49:30 | 0.171470 | +0.3570 |
| 2026-08-31 04:53:35 | RIDER rider ws10 - ws10 r 36.08, the highest ex-fence | - | 3: ws1,ws4,ws10 | last 16:19:30, 754.1 min ago / counter-side 2026-08-30 23:49:30 | 0.171470 | +0.3570 |
| 2026-08-31 04:53:35 | RETEST - ws1r 85.41 oob + ws2r 32.17 / ws3r 66.20 in - the gate opens; ws1r oob->ib cross 2026-08-31 04:56:25, wob 12, cadence at 2026-08-31 04:57:20 | - | 3: ws1,ws4,ws10 | last 16:19:30, 754.1 min ago / counter-side 2026-08-30 23:49:30 | 0.171470 | +0.3570 |
| 2026-08-31 04:56:15 | the favourable extreme - MFE 0.6321 | - | 3: ws1,ws4,ws10 | last 16:19:30, 756.8 min ago / counter-side 2026-08-30 23:49:30 | 0.171940 | +0.6321 |
| 2026-08-31 04:57:20 | **CADENCE:** RIDER rider ws10 - v4-arm-lineage-retest: the re-scan rides ws10 35.10, the highest ex-fence | - | 1: ws10 | last 16:19:30, 757.8 min ago / counter-side 2026-08-30 23:49:30 | 0.171300 | +0.2575 |
| 2026-08-31 04:57:20 | LATCH1 rider ws10 - latch 1 at the t2 cadence 2026-08-31 04:57:20, divergence state +1 | - | 1: ws10 | last 16:19:30, 757.8 min ago / counter-side 2026-08-30 23:49:30 | 0.171300 | +0.2575 |
| 2026-08-31 04:57:20 | **CADENCE:** EXHAUST rider ws10 - t2 ws1r ib cross 04:56:25 confirmed 04:57:20 at wob 12, ws1b 52.95 not oob, ws1b hold 0 \| mage-cascade down OPPOSES the LONG - rev-trade | - | 1: ws10 | last 16:19:30, 757.8 min ago / counter-side 2026-08-30 23:49:30 | 0.171300 | +0.2575 |
| 2026-08-31 04:57:20 | THIS LEG CLOSES on t2, realised +0.2692, drag 0.1975, net +0.0717 | - | 1: ws10 | last 16:19:30, 757.8 min ago / counter-side 2026-08-30 23:49:30 | 0.171300 | +0.2575 |

## 2026-08-31 leg 6 - LONG   opens 2026-08-31 08:24:00   exits 2026-08-31 10:43:30 on t1   held 139.5 min   MAE 0.8854   MFE 1.1653   realised +0.0571   net -0.1404

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-31 08:24:00 | >>> THIS LEG OPENS LONG | - | 5: ws12,ws14,ws15,ws17,ws18 | last 07:29:25, 54.6 min ago | 0.175060 | +0.0000 |
| 2026-08-31 08:42:30 | the favourable extreme - MFE 1.1653 | - | 6: ws2,ws3,ws12,ws15,ws17,ws18 | last 07:29:25, 73.1 min ago | 0.177100 | +1.1653 |
| 2026-08-31 10:03:00 | the ADVERSE extreme - MAE 0.8854 | - | 2: ws18,ws19 | last 07:29:25, 153.6 min ago | 0.173510 | -0.8854 |
| 2026-08-31 10:40:10 | ARM - ws1b+ws1r: ws1b 101.25 + ws1r 87.99 oob, ws1b dwell 0 | - | 3: ws1,ws2,ws3 | last 07:29:25, 190.8 min ago | 0.175090 | +0.0171 |
| 2026-08-31 10:40:10 | RIDER rider ws3 - ws3 r 81.49, the highest ex-fence | - | 3: ws1,ws2,ws3 | last 07:29:25, 190.8 min ago | 0.175090 | +0.0171 |
| 2026-08-31 10:40:10 | RETEST - ws2r 82.99 / ws3r 81.49 - not both inside the fence at the arm | - | 3: ws1,ws2,ws3 | last 07:29:25, 190.8 min ago | 0.175090 | +0.0171 |
| 2026-08-31 10:41:10 | BATON rider ws3 - ws3 -> ws5, between cadences, lin_hop 2 | ws5: 80.68 | 3: ws1,ws2,ws5 | last 07:29:25, 191.8 min ago | 0.174810 | -0.1428 |
| 2026-08-31 10:43:30 | LATCH1 rider ws5 - latch 1 at the t1 cadence 2026-08-31 10:43:30, divergence state +1 | - | 4: ws1,ws2,ws5,ws6 | last 07:29:25, 194.1 min ago | 0.175190 | +0.0743 |
| 2026-08-31 10:43:30 | **CADENCE:** EXHAUST rider ws5 - t1 ws1b ib 10:41:45, ws1r reversed 10:43:30 inside the 120s grace, stamp 10:43:30 \| mage-cascade down OPPOSES the LONG - rev-trade | - | 4: ws1,ws2,ws5,ws6 | last 07:29:25, 194.1 min ago | 0.175190 | +0.0743 |
| 2026-08-31 10:43:30 | THIS LEG CLOSES on t1, realised +0.0571, drag 0.1975, net -0.1404 | - | 4: ws1,ws2,ws5,ws6 | last 07:29:25, 194.1 min ago | 0.175190 | +0.0743 |

| the read | value |
|---|---|
| legs in the chain over the two days | 30 |
| legs opening on 2026-08-30 | 15 |
| legs opening on 2026-08-31 | 14 |
| legs opening on 2026-08-29 | 1 |
| seconds to compute | 1064.5 |
