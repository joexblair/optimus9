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

## 2026-08-30 leg 13 - LONG   opens 2026-08-30 21:04:05   exits 2026-08-30 22:02:55 on retest   held 58.8 min   MAE 0.5877   MFE 1.4858   realised +0.8982   net +0.7007

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 21:04:05 | >>> THIS LEG OPENS LONG | - | 2: ws6,ws9 | last 16:19:30, 284.6 min ago / counter-side 2026-08-30 19:07:55 | 0.180370 | +0.0000 |
| 2026-08-30 21:48:05 | the ADVERSE extreme - MAE 0.5877 | - | 7: ws3,ws9,ws10,ws11,ws13,ws15,ws16 | last 16:19:30, 328.6 min ago / counter-side 2026-08-30 19:07:55 | 0.179310 | -0.5877 |
| 2026-08-30 21:59:15 | ARM - ws1b+ws1r: ws1b 103.18 + ws1r 97.10 oob, ws1b dwell 0 | - | 9: ws1,ws3,ws9,ws10,ws11,ws13,ws15,ws16,ws17 | last 16:19:30, 339.8 min ago / counter-side 2026-08-30 19:07:55 | 0.182160 | +0.9924 |
| 2026-08-30 21:59:15 | RIDER rider ws17 - ws17 r 79.42, the highest ex-fence | - | 9: ws1,ws3,ws9,ws10,ws11,ws13,ws15,ws16,ws17 | last 16:19:30, 339.8 min ago / counter-side 2026-08-30 19:07:55 | 0.182160 | +0.9924 |
| 2026-08-30 21:59:15 | RETEST - ws1r 97.10 oob + ws2r 60.57 / ws3r 40.02 in - the gate opens; ws1r oob->ib cross 2026-08-30 22:02:00, wob 12, cadence at 2026-08-30 22:02:55 | - | 9: ws1,ws3,ws9,ws10,ws11,ws13,ws15,ws16,ws17 | last 16:19:30, 339.8 min ago / counter-side 2026-08-30 19:07:55 | 0.182160 | +0.9924 |
| 2026-08-30 22:01:40 | the favourable extreme - MFE 1.4858 | - | 8: ws3,ws9,ws10,ws12,ws13,ws15,ws16,ws17 | last 16:19:30, 342.2 min ago / counter-side 2026-08-30 19:07:55 | 0.183050 | +1.4858 |
| 2026-08-30 22:02:55 | **CADENCE:** RIDER rider ws17 - v4-arm-lineage-retest: the re-scan rides ws17 79.42, the highest ex-fence | - | 9: ws2,ws3,ws9,ws10,ws12,ws13,ws15,ws16,ws17 | last 16:19:30, 343.4 min ago / counter-side 2026-08-30 19:07:55 | 0.182100 | +0.9591 |
| 2026-08-30 22:02:55 | LATCH1 rider ws17 - latch 1 at the retest cadence 2026-08-30 22:02:55, divergence state +1 | - | 9: ws2,ws3,ws9,ws10,ws12,ws13,ws15,ws16,ws17 | last 16:19:30, 343.4 min ago / counter-side 2026-08-30 19:07:55 | 0.182100 | +0.9591 |
| 2026-08-30 22:02:55 | **CADENCE:** EXHAUST rider ws17 - retest ws1r 97.10 oob + ws2r 60.57 / ws3r 40.02 in - the gate opens; ws1r oob->ib cross 2026-08-30 22:02:00, wob 12, cadence at 2026-08-30 22:02:55 \| mage-cascade down OPPOSES the LONG - rev-trade | - | 9: ws2,ws3,ws9,ws10,ws12,ws13,ws15,ws16,ws17 | last 16:19:30, 343.4 min ago / counter-side 2026-08-30 19:07:55 | 0.182100 | +0.9591 |
| 2026-08-30 22:02:55 | THIS LEG CLOSES on retest, realised +0.8982, drag 0.1975, net +0.7007 | - | 9: ws2,ws3,ws9,ws10,ws12,ws13,ws15,ws16,ws17 | last 16:19:30, 343.4 min ago / counter-side 2026-08-30 19:07:55 | 0.182100 | +0.9591 |

| the read | value |
|---|---|
| legs in the chain over the two days | 30 |
| legs opening on 2026-08-30 | 15 |
| legs opening on 2026-08-31 | 14 |
| legs opening on 2026-08-29 | 1 |
| seconds to compute | 299.7 |
