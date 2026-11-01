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
# the baton fence test reads: latch, released on lift. the stop is OFF. drag 0.1975% per round trip, its own column and its own total.
# ts is the bar. pxs is that bar's close unless the row names an extreme. pct is signed to THIS leg.
# baton candidates: every candidate timeframe offered at that bar with its value. "none offered" = a hand-over attempt with no candidate inside lin_hop 2.
# exfnc ltchd: every ws1..ws20 line whose ex-fence latch is ON at that bar, on this leg's side.
# a row whose bar carried a cadence starts **CADENCE:**.

## THE CHAIN SUMMARY - one row per leg, chronological

| day | leg of that day | leg of the chain | the open | dir | the exit | ended by | held min | the rider chain | MAE % | MFE % | realised % | drag % | net % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-29 | 1 | 1 | 2026-08-29 23:53:55 | SHORT | 2026-08-30 02:29:55 | t2 | 156.0 | ws2 > ws17 > ws19 > ws20 | 0.5088 | +1.9536 | +1.4347 | 0.1975 | +1.2372 |
| 2026-08-30 | 1 | 2 | 2026-08-30 02:30:00 | LONG | 2026-08-30 02:45:55 | t2 | 15.9 | ws6 | 0.2271 | +0.4439 | +0.1290 | 0.1975 | -0.0685 |
| 2026-08-30 | 2 | 3 | 2026-08-30 02:46:00 | SHORT | 2026-08-30 06:12:55 | t2 | 206.9 | ws18 > ws20 | 0.3196 | +2.2011 | +1.2166 | 0.1975 | +1.0191 |
| 2026-08-30 | 3 | 4 | 2026-08-30 06:13:00 | LONG | 2026-08-30 07:48:15 | t2 | 95.2 | ws19 > ws20 | 0.5740 | +1.2159 | -0.4488 | 0.1975 | -0.6463 |
| 2026-08-30 | 4 | 5 | 2026-08-30 07:48:20 | SHORT | 2026-08-30 09:45:20 | barrage | 117.0 | ws8 > ws10 > ws12 > ws13 > ws20 | 0.5452 | +1.0012 | +0.4770 | 0.1975 | +0.2795 |
| 2026-08-30 | 5 | 6 | 2026-08-30 09:45:25 | LONG | 2026-08-30 11:12:00 | t2 | 86.6 | ws4 > ws5 > ws6 > ws8 > ws10 > ws12 > ws13 | 0.2686 | +0.7163 | +0.3424 | 0.1975 | +0.1449 |
| 2026-08-30 | 6 | 7 | 2026-08-30 11:12:05 | SHORT | 2026-08-30 12:21:05 | t2 | 69.0 | ws20 | 0.9291 | +0.4987 | -0.5407 | 0.1975 | -0.7382 |
| 2026-08-30 | 7 | 8 | 2026-08-30 12:21:10 | LONG | 2026-08-30 12:35:10 | t2 | 14.0 | ws20 | 0.2506 | +0.9084 | -0.0209 | 0.1975 | -0.2184 |
| 2026-08-30 | 8 | 9 | 2026-08-30 12:35:15 | SHORT | 2026-08-30 13:23:05 | latch | 47.8 | ws5 > ws7 | 0.5222 | +0.2663 | -0.0366 | 0.1975 | -0.2341 |
| 2026-08-30 | 9 | 10 | 2026-08-30 13:23:10 | LONG | 2026-08-30 14:56:55 | t2 | 93.8 | ws20 | 0.3706 | +2.1037 | +0.5272 | 0.1975 | +0.3297 |
| 2026-08-30 | 10 | 11 | 2026-08-30 14:57:00 | SHORT | 2026-08-30 16:41:35 | t2 | 104.6 | ws20 | 0.8360 | +1.5059 | +0.3894 | 0.1975 | +0.1919 |
| 2026-08-30 | 11 | 12 | 2026-08-30 16:41:40 | LONG | 2026-08-30 19:55:25 | t2 | 193.8 | ws9 > ws11 | 7.3242 | +0.3805 | -5.6717 | 0.1975 | -5.8692 |
| 2026-08-30 | 12 | 13 | 2026-08-30 19:55:30 | SHORT | 2026-08-30 21:49:15 | t1 | 113.8 | ws9 > ws3 > ws4 > ws5 | 1.2158 | +1.6137 | +0.6853 | 0.1975 | +0.4878 |
| 2026-08-30 | 13 | 14 | 2026-08-30 21:49:20 | LONG | 2026-08-30 22:12:40 | latch | 23.3 | ws17 | 0.1781 | +1.8585 | +0.1781 | 0.1975 | -0.0194 |
| 2026-08-30 | 14 | 15 | 2026-08-30 22:12:45 | SHORT | 2026-08-30 22:22:25 | DIV REV-TRADE | 9.7 | - | 0.2444 | +0.7499 | +0.5444 | 0.1975 | +0.3469 |
| 2026-08-30 | 15 | 16 | 2026-08-30 22:22:30 | LONG | 2026-08-31 01:17:25 | t2 | 174.9 | ws4 > ws6 > ws7 > ws9 > ws11 > ws13 | 5.6130 | +0.1061 | -2.5412 | 0.1975 | -2.7387 |
| 2026-08-31 | 1 | 17 | 2026-08-31 01:17:30 | SHORT | 2026-08-31 02:57:05 | t1 | 99.6 | ws18 | 0.5158 | +2.2120 | +1.8510 | 0.1975 | +1.6535 |
| 2026-08-31 | 2 | 18 | 2026-08-31 02:57:10 | LONG | 2026-08-31 03:26:55 | t2 | 29.8 | ws4 > ws5 | 0.0000 | +1.0977 | +0.8933 | 0.1975 | +0.6958 |
| 2026-08-31 | 3 | 19 | 2026-08-31 03:27:00 | SHORT | 2026-08-31 04:23:25 | t1 | 56.4 | ws16 | 0.8681 | +1.7535 | +1.1227 | 0.1975 | +0.9252 |
| 2026-08-31 | 4 | 20 | 2026-08-31 04:23:30 | LONG | 2026-08-31 04:57:20 | t2 | 33.8 | ws10 | 0.2926 | +0.6321 | +0.2692 | 0.1975 | +0.0717 |
| 2026-08-31 | 5 | 21 | 2026-08-31 04:57:25 | SHORT | 2026-08-31 08:28:40 | latch | 211.2 | ws5 > ws7 | 3.2454 | +0.1868 | -2.6092 | 0.1975 | -2.8067 |
| 2026-08-31 | 6 | 22 | 2026-08-31 08:28:45 | LONG | 2026-08-31 13:04:55 | t2 | 276.2 | ws3 > ws5 > ws6 > ws8 > ws11 > ws12 > ws14 | 2.1560 | +0.7452 | -1.5644 | 0.1975 | -1.7619 |
| 2026-08-31 | 7 | 23 | 2026-08-31 13:05:00 | SHORT | 2026-08-31 15:21:35 | t1 | 136.6 | ws17 | 1.7799 | +0.8322 | +0.0809 | 0.1975 | -0.1166 |
| 2026-08-31 | 8 | 24 | 2026-08-31 15:21:40 | LONG | 2026-08-31 18:33:35 | barrage | 191.9 | ws2 > ws3 > ws13 > ws15 | 0.5784 | +3.4702 | +2.8571 | 0.1975 | +2.6596 |
| 2026-08-31 | 9 | 25 | 2026-08-31 18:33:40 | SHORT | 2026-08-31 19:23:55 | t2 | 50.2 | ws5 > ws8 | 1.9906 | +1.0121 | +0.3824 | 0.1975 | +0.1849 |
| 2026-08-31 | 10 | 26 | 2026-08-31 19:24:00 | LONG | 2026-08-31 21:37:00 | t1 | 133.0 | ws12 | 0.9539 | +0.9483 | +0.6209 | 0.1975 | +0.4234 |
| 2026-08-31 | 11 | 27 | 2026-08-31 21:37:05 | SHORT | 2026-08-31 22:21:50 | t1 | 44.8 | ws20 | 0.1683 | +1.0154 | +0.8471 | 0.1975 | +0.6496 |
| 2026-08-31 | 12 | 28 | 2026-08-31 22:21:55 | LONG | - | no exhaust | - | - | - | - | - | - | - |
| TOTAL | | 27 scored legs | | | | | 2785.8 | | 32.4761 | +31.4293 | +1.4154 | 5.3325 | -3.9171 |

| the read | value |
|---|---|
| legs in the chain over the two days | 28 |
| legs opening on 2026-08-30 | 15 |
| legs opening on 2026-08-31 | 12 |
| legs opening on 2026-08-29 | 1 |
| seconds to compute | 277.1 |
