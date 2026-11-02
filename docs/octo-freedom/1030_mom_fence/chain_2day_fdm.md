# THE CHAIN - FENCE 75/25, LADDER ws1..ws30, THE LATCH RELEASED ON LIFT
# WINDOW 2026-08-30 00:00:00 .. 2026-08-31 23:59:55 | TAPE 1632960 bars | RULED_OK True
# RMOM_FNC 75.0 -> (25.0, 75.0) | L2_MOM_MAXTF 30 | LIN2_EXFNC_LATCH_REL 'lift'
# the latch turns ON at an ex-fence cross held 4 bars = 20 s, and is released ONLY by that
#   line's own lift-off on the same side, stamped at lift + LIFT_WOB - 1 = lift + 7 bars = 35 s.
#   and its sampling RESTARTS at the latch-on bar - his 1030 ruling - so the lattice must refill before any release can print.
# the barrage no longer releases the latch on this arm. It is still a cadence, so the column stays.
# LIN2_COUNTER_OOB_ON 0 - his 1030 *"drop the opposing oob side forced exit"*. At 0 the ws1b counter-target-side
#   oob cadence is not produced at all, so no leg can exit on it. Its replacement is UNRULED - his own words.
# the open is 2026-08-29 23:53:55 SHORT, handed in - the router's fire bar off the lin2-reentry signal 2026-08-29 23:53:50
# the way back in after a stop: the fdm re-entry - gcws30b ex-95.0 window, closed by its ib cross at xwob 1, gate ws1r AND (ws2r or ws3r) past the 75.0 fence SEEN in the window
# the baton fence test reads: value. the stop is ON at LIN2_MAE_CAP 1.10%, with 3304 lin2-reentry signals as the way back in. drag 0.1975% per round trip, its own column and its own total.
# ts is the bar. pxs is that bar's close unless the row names an extreme. pct is signed to THIS leg.
# baton candidates: every candidate timeframe offered at that bar with its value. "none offered" = a hand-over attempt with no candidate inside lin_hop 2.
# exfnc ltchd: every ws1..ws30 line whose ex-fence latch is ON at that bar, on this leg's side.
# a row whose bar carried a cadence starts **CADENCE:**.

## THE CHAIN SUMMARY - one row per leg, chronological

| day | leg of that day | leg of the chain | the open | dir | the exit | ended by | held min | the rider chain | MAE % | MFE % | realised % | drag % | net % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-29 | 1 | 1 | 2026-08-29 23:53:55 | SHORT | 2026-08-30 07:35:55 | t1 | 462.0 | ws11 > ws19 > ws21 > ws23 > ws25 > ws27 > ws29 | 0.5088 | +3.4799 | +2.7371 | 0.1975 | +2.5396 |
| 2026-08-30 | 1 | 2 | 2026-08-30 07:36:00 | LONG | 2026-08-30 09:43:35 | STOP at 1.10% | 127.6 | ws12 > ws13 > ws15 > ws17 > ws19 > ws20 > ws22 > ws23 > ws30 | 1.1000 | +0.3295 | -1.1000 | 0.1975 | -1.2975 |
| 2026-08-30 | 2 | 3 | 2026-08-30 10:29:05 | SHORT | 2026-08-30 12:33:00 | STOP at 1.10% | 123.9 | ws3 > ws9 > ws10 > ws11 > ws13 > ws15 > ws17 > ws19 > ws21 > ws22 > ws27 > ws30 | 1.1000 | +0.4359 | -1.1000 | 0.1975 | -1.2975 |
| 2026-08-30 | 3 | 4 | 2026-08-30 13:00:35 | SHORT | 2026-08-30 13:18:40 | DIV REV-TRADE | 18.1 | - | 0.1092 | +0.6761 | +0.6189 | 0.1975 | +0.4214 |
| 2026-08-30 | 4 | 5 | 2026-08-30 13:18:45 | LONG | 2026-08-30 13:53:25 | t1 | 34.7 | ws1 > ws3 | 0.1256 | +1.9257 | +1.4390 | 0.1975 | +1.2415 |
| 2026-08-30 | 5 | 6 | 2026-08-30 13:53:30 | SHORT | 2026-08-30 21:04:55 | t1 | 431.4 | ws3 > ws9 > ws10 > ws11 > ws13 > ws15 > ws17 > ws19 > ws21 > ws22 > ws27 > ws30 | 0.9028 | +8.2899 | +6.9899 | 0.1975 | +6.7924 |
| 2026-08-30 | 6 | 7 | 2026-08-30 21:05:00 | LONG | 2026-08-30 22:24:25 | STOP at 1.10% | 79.4 | ws4 > ws6 > ws8 > ws10 > ws11 > ws12 > ws13 > ws15 > ws17 > ws19 > ws21 > ws23 | 1.1000 | +1.5252 | -1.1000 | 0.1975 | -1.2975 |
| 2026-08-30 | 7 | 8 | 2026-08-30 22:27:05 | LONG | 2026-08-30 22:30:20 | STOP at 1.10% | 3.2 | ws4 > ws6 > ws8 > ws10 > ws11 > ws12 > ws13 > ws15 > ws17 > ws19 > ws21 > ws23 | 1.1000 | +0.1512 | -1.1000 | 0.1975 | -1.2975 |
| 2026-08-31 | 1 | 9 | 2026-08-31 00:00:05 | SHORT | 2026-08-31 04:11:25 | t1 | 251.3 | ws16 | 0.6298 | +2.3016 | +1.1050 | 0.1975 | +0.9075 |
| 2026-08-31 | 2 | 10 | 2026-08-31 04:11:30 | LONG | 2026-08-31 04:15:10 | STOP at 1.10% | 3.7 | ws4 > ws6 > ws8 > ws10 > ws11 > ws12 > ws13 > ws15 > ws17 > ws19 > ws21 > ws23 | 1.1000 | +0.0232 | -1.1000 | 0.1975 | -1.2975 |
| 2026-08-31 | 3 | 11 | 2026-08-31 04:19:35 | LONG | 2026-08-31 10:31:00 | t1 | 371.4 | ws4 > ws6 > ws8 > ws10 > ws11 > ws12 > ws13 > ws15 > ws17 > ws19 > ws21 > ws23 | 0.1465 | +3.8040 | +2.1218 | 0.1975 | +1.9243 |
| 2026-08-31 | 4 | 12 | 2026-08-31 10:31:05 | SHORT | 2026-08-31 10:53:10 | STOP at 1.10% | 22.1 | ws30 | 1.1000 | +0.0804 | -1.1000 | 0.1975 | -1.2975 |
| 2026-08-31 | 5 | 13 | 2026-08-31 11:36:05 | LONG | 2026-08-31 12:41:15 | STOP at 1.10% | 65.2 | ws2 > ws3 | 1.1000 | +0.6991 | -1.1000 | 0.1975 | -1.2975 |
| 2026-08-31 | 6 | 14 | 2026-08-31 12:43:05 | LONG | 2026-08-31 16:14:25 | t1 | 211.3 | ws11 > ws12 | 0.8551 | +1.7564 | -0.1329 | 0.1975 | -0.3304 |
| 2026-08-31 | 7 | 15 | 2026-08-31 16:14:30 | SHORT | - | no exhaust | - | ws5 > ws7 > ws9 > ws10 > ws12 > ws13 > ws15 > ws17 > ws25 > ws27 > ws29 | - | - | - | - | - |
| TOTAL | | 14 scored legs | | | | | 2205.3 | | 10.9777 | +25.4782 | +7.1788 | 2.7650 | +4.4138 |

| the read | value |
|---|---|
| legs in the chain over the window | 15 |
| legs opening on 2026-08-29 | 1 |
| legs opening on 2026-08-30 | 7 |
| legs opening on 2026-08-31 | 7 |
| seconds to compute | 146.6 |
