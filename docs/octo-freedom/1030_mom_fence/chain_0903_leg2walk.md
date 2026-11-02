# THE CHAIN - FENCE 75/25, LADDER ws1..ws30, THE LATCH RELEASED ON LIFT
# WINDOW 2026-09-03 00:00:00 .. 2026-09-03 23:59:55 | TAPE 1632960 bars | RULED_OK True
# RMOM_FNC 75.0 -> (25.0, 75.0) | L2_MOM_MAXTF 30 | LIN2_EXFNC_LATCH_REL 'lift'
# the latch turns ON at an ex-fence cross held 4 bars = 20 s, and is released ONLY by that
#   line's own lift-off on the same side, stamped at lift + LIFT_WOB - 1 = lift + 7 bars = 35 s.
#   and its sampling RESTARTS at the latch-on bar - his 1030 ruling - so the lattice must refill before any release can print.
# the barrage no longer releases the latch on this arm. It is still a cadence, so the column stays.
# LIN2_COUNTER_OOB_ON 0 - his 1030 *"drop the opposing oob side forced exit"*. At 0 the ws1b counter-target-side
#   oob cadence is not produced at all, so no leg can exit on it. Its replacement is UNRULED - his own words.
# the open is 2026-09-03 00:37:00 LONG, handed in - W_OPEN, his own bar and side
# the way back in after a stop: NONE - the chain ends at its first stop
# the baton fence test reads: latch, released on lift. the stop is ON at LIN2_MAE_CAP 1.10%, with 0 lin2-reentry signals as the way back in. drag 0.1975% per round trip, its own column and its own total.
# ts is the bar. pxs is that bar's close unless the row names an extreme. pct is signed to THIS leg.
# baton candidates: every candidate timeframe offered at that bar with its value. "none offered" = a hand-over attempt with no candidate inside lin_hop 2.
# exfnc ltchd: every ws1..ws30 line whose ex-fence latch is ON at that bar, on this leg's side.
# a row whose bar carried a cadence starts **CADENCE:**.

## THE CHAIN SUMMARY - one row per leg, chronological

| day | leg of that day | leg of the chain | the open | dir | the exit | ended by | held min | the rider chain | MAE % | MFE % | realised % | drag % | net % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-03 | 1 | 1 | 2026-09-03 00:37:00 | LONG | 2026-09-03 01:36:00 | t1 | 59.0 | ws10 > ws15 | 0.1735 | +2.3198 | +1.8121 | 0.1975 | +1.6146 |
| 2026-09-03 | 2 | 2 | 2026-09-03 01:36:05 | SHORT | 2026-09-03 04:56:55 | STOP at 1.10% | 200.8 | ws5 > ws6 > ws8 > ws9 > ws10 > ws12 > ws17 > ws18 | 1.1000 | +0.9278 | -1.1000 | 0.1975 | -1.2975 |
| TOTAL | | 2 scored legs | | | | | 259.8 | | 1.2735 | +3.2475 | +0.7121 | 0.3950 | +0.3171 |

## 2026-09-03 leg 2 - SHORT   opens 2026-09-03 01:36:05   exits 2026-09-03 04:56:55 on STOP at 1.10%   held 200.8 min   MAE 1.1000   MFE 0.9278   realised -1.1000   net -1.2975

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-09-03 01:36:05 | >>> THIS LEG OPENS SHORT | - | 2: ws6,ws9 | last 19:39:30, 356.6 min ago | 0.158440 | -0.0000 |
| 2026-09-03 03:24:00 | ARM - ws4r: ws4r 8.52 oob | - | 3: ws1,ws3,ws4 | last 19:39:30, 464.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158580 | -0.0884 |
| 2026-09-03 03:24:00 | RETEST - ws1r 20.64 is not oob at the arm - the gate stays shut | - | 3: ws1,ws3,ws4 | last 19:39:30, 464.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158580 | -0.0884 |
| 2026-09-03 03:24:05 | NO RIDER - the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs | - | 3: ws1,ws3,ws4 | last 19:39:30, 464.6 min ago / counter-side 2026-09-03 03:15:55 | 0.158610 | -0.1073 |
| 2026-09-03 03:25:50 | LATCH1 - latch 1 at the t1 cadence 2026-09-03 03:25:50, divergence state -1 | - | 4: ws1,ws3,ws4,ws5 | last 19:39:30, 466.3 min ago / counter-side 2026-09-03 03:15:55 | 0.158780 | -0.2146 |
| 2026-09-03 03:25:50 | RIDER rider ws5 - t1 gcws30b oob 03:23:15..03:25:20, ws1r reversed 03:24:15 during, r 23.33 past the 44.0 fence, stamp 03:24:15, cross 03:25:25 hold 6 bars \| ws5 r 25.56 picked up at a cadence, no prior rider | - | 4: ws1,ws3,ws4,ws5 | last 19:39:30, 466.3 min ago / counter-side 2026-09-03 03:15:55 | 0.158780 | -0.2146 |
| 2026-09-03 03:30:50 | LATCH1 rider ws5 - latch 1 at the t1 cadence 2026-09-03 03:30:50, divergence state -1 | - | 3: ws2,ws5,ws6 | last 19:39:30, 471.3 min ago / counter-side 2026-09-03 03:15:55 | 0.158500 | -0.0379 |
| 2026-09-03 03:30:50 | **CADENCE:** CADENCE rider ws5 - t1 gcws30b oob 03:29:35..03:30:20, ws1r reversed 03:30:20 during, r 34.95 past the 44.0 fence, stamp 03:30:20, cross 03:30:25 hold 6 bars \| rider ws5 13.61, no-longer-exfence no, reversed no \| mage-cascade up | ws6: 16.84 | 3: ws2,ws5,ws6 | last 19:39:30, 471.3 min ago / counter-side 2026-09-03 03:15:55 | 0.158500 | -0.0379 |
| 2026-09-03 03:30:50 | **CADENCE:** BATON rider ws5 - ws5 -> ws6, at a t1 cadence, capped at ws13 by the jump bound 8 | ws6: 16.84 | 3: ws2,ws5,ws6 | last 19:39:30, 471.3 min ago / counter-side 2026-09-03 03:15:55 | 0.158500 | -0.0379 |
| 2026-09-03 03:39:15 | LATCH1 rider ws6 - latch 1 at the t1 cadence 2026-09-03 03:39:15, divergence state -1 | - | 3: ws6,ws7,ws8 | last 19:39:30, 479.8 min ago / counter-side 2026-09-03 03:15:55 | 0.158300 | +0.0884 |
| 2026-09-03 03:39:15 | **CADENCE:** CADENCE rider ws6 - t1 gcws30b ib 03:37:20, ws1r reversed 03:39:15 inside the 120s grace from the cross bar 03:37:20, r 30.02 past the 44.0 fence, stamp 03:39:15, hold 6 bars \| rider ws6 2.14, no-longer-exfence no, reversed yes \| mage-cascade up | ws7: 11.57, ws8: 22.86 | 3: ws6,ws7,ws8 | last 19:39:30, 479.8 min ago / counter-side 2026-09-03 03:15:55 | 0.158300 | +0.0884 |
| 2026-09-03 03:39:15 | **CADENCE:** BATON rider ws6 - ws6 -> ws8, at a t1 cadence, capped at ws14 by the jump bound 8 | ws7: 11.57, ws8: 22.86 | 3: ws6,ws7,ws8 | last 19:39:30, 479.8 min ago / counter-side 2026-09-03 03:15:55 | 0.158300 | +0.0884 |
| 2026-09-03 03:39:30 | LATCH1 rider ws8 - latch 1 at the t1 cadence 2026-09-03 03:39:30, divergence state -1 | - | 3: ws6,ws7,ws8 | last 19:39:30, 480.0 min ago / counter-side 2026-09-03 03:15:55 | 0.158270 | +0.1073 |
| 2026-09-03 03:39:30 | **CADENCE:** CADENCE rider ws8 - t1 gcws30b ib 03:39:05, ws1r reversed 03:39:15 inside the 120s grace from the cross bar 03:39:05, r 30.02 past the 44.0 fence, stamp 03:39:15, hold 6 bars \| rider ws8 22.86, no-longer-exfence no, reversed no \| mage-cascade up | none offered | 3: ws6,ws7,ws8 | last 19:39:30, 480.0 min ago / counter-side 2026-09-03 03:15:55 | 0.158270 | +0.1073 |
| 2026-09-03 03:39:30 | HOLD rider ws8 - rider ws8 22.86 ex-fence and not reversed - no action | - | 3: ws6,ws7,ws8 | last 19:39:30, 480.0 min ago / counter-side 2026-09-03 03:15:55 | 0.158270 | +0.1073 |
| 2026-09-03 03:49:35 | BATON rider ws8 - ws8 -> ws9, between cadences, lin_hop 2 | ws9: 24.09 | 1: ws9 | last 19:39:30, 490.1 min ago / counter-side 2026-09-03 03:15:55 | 0.158530 | -0.0568 |
| 2026-09-03 04:03:45 | BATON rider ws9 - ws9 -> ws10, between cadences, lin_hop 2 | ws10: 21.62 | 2: ws5,ws10 | last 19:39:30, 504.2 min ago / counter-side 2026-09-03 03:15:55 | 0.158650 | -0.1325 |
| 2026-09-03 04:22:55 | BATON rider ws10 - ws10 -> ws12, between cadences, lin_hop 2 | ws11: 20.38, ws12: 17.21 | 3: ws3,ws11,ws12 | last 19:39:30, 523.4 min ago / counter-side 2026-09-03 03:15:55 | 0.158250 | +0.1199 |
| 2026-09-03 04:35:20 | the favourable extreme - MFE 0.9278 | - | 8: ws5,ws10,ws12,ws13,ws14,ws15,ws16,ws17 | last 19:39:30, 535.8 min ago / counter-side 2026-09-03 03:15:55 | 0.156970 | +0.9278 |
| 2026-09-03 04:37:55 | LATCH1 rider ws12 - latch 1 at the t1 cadence 2026-09-03 04:37:55, divergence state -1 | - | 9: ws4,ws5,ws10,ws12,ws13,ws14,ws15,ws16,ws17 | last 19:39:30, 538.4 min ago / counter-side 2026-09-03 03:15:55 | 0.157610 | +0.5239 |
| 2026-09-03 04:37:55 | **CADENCE:** CADENCE rider ws12 - t1 gcws30b ib 04:37:30, ws1r reversed 04:37:45 inside the 120s grace from the cross bar 04:37:30, r 33.98 past the 44.0 fence, stamp 04:37:45, hold 6 bars \| rider ws12 13.56, no-longer-exfence no, reversed no \| mage-cascade down | ws13: 15.72, ws14: 21.45, ws15: 16.31, ws16: 14.34, ws17: 15.56 | 9: ws4,ws5,ws10,ws12,ws13,ws14,ws15,ws16,ws17 | last 19:39:30, 538.4 min ago / counter-side 2026-09-03 03:15:55 | 0.157610 | +0.5239 |
| 2026-09-03 04:37:55 | **CADENCE:** BATON rider ws12 - ws12 -> ws17, at a t1 cadence, capped at ws20 by the jump bound 8 | ws13: 15.72, ws14: 21.45, ws15: 16.31, ws16: 14.34, ws17: 15.56 | 9: ws4,ws5,ws10,ws12,ws13,ws14,ws15,ws16,ws17 | last 19:39:30, 538.4 min ago / counter-side 2026-09-03 03:15:55 | 0.157610 | +0.5239 |
| 2026-09-03 04:56:55 | the ADVERSE extreme - MAE 1.1235 | - | 6: ws4,ws13,ws16,ws17,ws18,ws19 | last 19:39:30, 557.4 min ago / counter-side 2026-09-03 03:15:55 | 0.160220 | -1.1235 |
| 2026-09-03 04:56:55 | THIS LEG CLOSES on STOP at 1.10%, realised -1.1000, drag 0.1975, net -1.2975 | - | 6: ws4,ws13,ws16,ws17,ws18,ws19 | last 19:39:30, 557.4 min ago / counter-side 2026-09-03 03:15:55 | 0.160170 | -1.0919 |
| 2026-09-03 05:32:35 | BATON rider ws17 - ws17 -> ws18, between cadences, lin_hop 2 | ws18: 26.65 | 5: ws15,ws16,ws18,ws20,ws22 | last 19:39:30, 593.1 min ago / counter-side 2026-09-03 03:15:55 | 0.158310 | +0.0820 |
| 2026-09-03 07:04:35 | NO PASS rider ws18 - ws18 70.62 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 1: ws22 | last 19:39:30, 685.1 min ago / counter-side 2026-09-03 03:15:55 | 0.161650 | -2.0260 |
| 2026-09-03 07:33:00 | **CADENCE:** CADENCE rider ws18 - t1 gcws30b oob 07:30:15..07:32:30, ws1r reversed 07:32:10 during, r 22.68 past the 44.0 fence, stamp 07:32:10, cross 07:32:35 hold 6 bars \| rider ws18 72.57, no-longer-exfence yes, reversed yes \| mage-cascade up | none offered | 4: ws1,ws3,ws6,ws7 | last 19:39:30, 713.5 min ago / counter-side 2026-09-03 07:15:45 | 0.160490 | -1.2939 |
| 2026-09-03 07:33:00 | **CADENCE:** EXHAUST rider ws18 - t4 at a t1 cadence - rider ws18 72.57, no candidate at or below ws26 (the jump bound 8) | - | 4: ws1,ws3,ws6,ws7 | last 19:39:30, 713.5 min ago / counter-side 2026-09-03 07:15:45 | 0.160490 | -1.2939 |

| the read | value |
|---|---|
| legs in the chain over the window | 2 |
| legs opening on 2026-09-03 | 2 |
| seconds to compute | 60.6 |
