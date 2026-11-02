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
# the baton fence test reads: value. the stop is ON at LIN2_MAE_CAP 1.10%, with 0 lin2-reentry signals as the way back in. drag 0.1975% per round trip, its own column and its own total.
# ts is the bar. pxs is that bar's close unless the row names an extreme. pct is signed to THIS leg.
# baton candidates: every candidate timeframe offered at that bar with its value. "none offered" = a hand-over attempt with no candidate inside lin_hop 2.
# exfnc ltchd: every ws1..ws30 line whose ex-fence latch is ON at that bar, on this leg's side.
# a row whose bar carried a cadence starts **CADENCE:**.

## THE CHAIN SUMMARY - one row per leg, chronological

| day | leg of that day | leg of the chain | the open | dir | the exit | ended by | held min | the rider chain | MAE % | MFE % | realised % | drag % | net % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-03 | 1 | 1 | 2026-09-03 00:37:00 | LONG | 2026-09-03 02:33:25 | t1 | 116.4 | ws4 > ws6 > ws7 | 0.1735 | +2.4933 | +2.1463 | 0.1975 | +1.9488 |
| 2026-09-03 | 2 | 2 | 2026-09-03 02:33:30 | SHORT | 2026-09-03 05:19:25 | t1 | 165.9 | ws4 > ws5 > ws7 > ws8 > ws10 > ws12 | 1.0569 | +1.2519 | +0.0440 | 0.1975 | -0.1535 |
| 2026-09-03 | 3 | 3 | 2026-09-03 05:19:30 | LONG | 2026-09-03 06:25:25 | t1 | 65.9 | ws3 > ws4 | 1.0196 | +1.1329 | +0.7615 | 0.1975 | +0.5640 |
| 2026-09-03 | 4 | 4 | 2026-09-03 06:25:30 | SHORT | 2026-09-03 08:07:00 | STOP at 1.10% | 101.5 | ws7 > ws13 > ws14 > ws16 > ws21 | 1.1000 | +0.1374 | -1.1000 | 0.1975 | -1.2975 |
| TOTAL | | 4 scored legs | | | | | 449.8 | | 3.3499 | +5.0154 | +1.8518 | 0.7900 | +1.0618 |

## 2026-09-03 leg 1 - LONG   opens 2026-09-03 00:37:00   exits 2026-09-03 02:33:25 on t1   held 116.4 min   MAE 0.1735   MFE 2.4933   realised +2.1463   net +1.9488

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-09-03 00:37:00 | >>> THIS LEG OPENS LONG | - | 3: ws13,ws24,ws28 | last 15:45:35, 531.4 min ago / counter-side 2026-09-02 19:39:30 | 0.155620 | +0.0000 |
| 2026-09-03 01:01:30 | the ADVERSE extreme - MAE 0.1735 | - | 1: ws3 | last 15:45:35, 555.9 min ago / counter-side 2026-09-02 19:39:30 | 0.155350 | -0.1735 |
| 2026-09-03 01:08:30 | ARM - ws4r: ws4r 85.04 oob | - | 2: ws1,ws4 | last 15:45:35, 562.9 min ago / counter-side 2026-09-02 19:39:30 | 0.157460 | +1.1824 |
| 2026-09-03 01:08:30 | RETEST - ws1r 81.14 is not oob at the arm - the gate stays shut | - | 2: ws1,ws4 | last 15:45:35, 562.9 min ago / counter-side 2026-09-02 19:39:30 | 0.157460 | +1.1824 |
| 2026-09-03 01:08:35 | NO RIDER - the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs | - | 2: ws1,ws4 | last 15:45:35, 563.0 min ago / counter-side 2026-09-02 19:39:30 | 0.157460 | +1.1824 |
| 2026-09-03 01:09:55 | RIDER rider ws4 - t1 gcws30b back inside the 95.0 fence 01:08:30, ws1r reversed 01:09:55 inside the 120s grace from the cross bar 01:08:30, r 82.91 past the 56.0 fence, stamp 01:09:55, hold 6 bars \| ws4 r 84.23 picked up at a cadence, no prior rider | - | 2: ws1,ws4 | last 15:45:35, 564.3 min ago / counter-side 2026-09-02 19:39:30 | 0.157400 | +1.1438 |
| 2026-09-03 01:10:25 | **CADENCE:** CADENCE rider ws4 - t1 gcws30b past the 95.0 fence 01:09:30..01:09:55, ws1r reversed 01:09:55 during, r 82.91 past the 56.0 fence, stamp 01:09:55, cross 01:10:00 hold 6 bars \| rider ws4 82.14, no-longer-exfence no, reversed no \| mage-cascade down | none offered | 2: ws1,ws4 | last 15:45:35, 564.8 min ago / counter-side 2026-09-02 19:39:30 | 0.157230 | +1.0346 |
| 2026-09-03 01:10:25 | HOLD rider ws4 - rider ws4 82.14 ex-fence and not reversed - no action | - | 2: ws1,ws4 | last 15:45:35, 564.8 min ago / counter-side 2026-09-02 19:39:30 | 0.157230 | +1.0346 |
| 2026-09-03 01:10:50 | NO PASS rider ws4 - ws4 82.49 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 2: ws1,ws4 | last 15:45:35, 565.2 min ago / counter-side 2026-09-02 19:39:30 | 0.157260 | +1.0538 |
| 2026-09-03 01:35:55 | LATCH1 rider ws4 - latch 1 at the t1 cadence 2026-09-03 01:35:55, divergence state +1 | - | 3: ws4,ws5,ws6 | last 15:45:35, 590.3 min ago / counter-side 2026-09-02 19:39:30 | 0.158450 | +1.8185 |
| 2026-09-03 01:35:55 | **CADENCE:** CADENCE rider ws4 - t1 gcws30b past the 95.0 fence 01:34:00..01:35:25, ws1r reversed 01:35:15 during, r 71.97 past the 56.0 fence, stamp 01:35:15, cross 01:35:30 hold 6 bars \| rider ws4 87.26, no-longer-exfence no, reversed yes \| mage-cascade down | ws5: 92.71, ws6: 94.93 | 3: ws4,ws5,ws6 | last 15:45:35, 590.3 min ago / counter-side 2026-09-02 19:39:30 | 0.158450 | +1.8185 |
| 2026-09-03 01:35:55 | **CADENCE:** BATON rider ws4 - ws4 -> ws6, at a t1 cadence, capped at ws12 by the jump bound 8 | ws5: 92.71, ws6: 94.93 | 3: ws4,ws5,ws6 | last 15:45:35, 590.3 min ago / counter-side 2026-09-02 19:39:30 | 0.158450 | +1.8185 |
| 2026-09-03 01:47:00 | BATON rider ws6 - ws6 -> ws7, between cadences, lin_hop 2 | ws7: 87.00 | 3: ws5,ws6,ws7 | last 15:45:35, 601.4 min ago / counter-side 2026-09-02 19:39:30 | 0.157790 | +1.3944 |
| 2026-09-03 01:48:05 | NO PASS rider ws7 - ws7 84.75 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 3: ws5,ws6,ws7 | last 15:45:35, 602.5 min ago / counter-side 2026-09-02 19:39:30 | 0.157650 | +1.3045 |
| 2026-09-03 02:32:25 | the favourable extreme - MFE 2.4933 | - | 2: ws3,ws4 | last 02:26:55, 5.5 min ago | 0.159500 | +2.4933 |
| 2026-09-03 02:33:25 | LATCH1 rider ws7 - latch 1 at the t1 cadence 2026-09-03 02:33:25, divergence state +1 | - | 2: ws3,ws4 | last 02:26:55, 6.5 min ago | 0.159030 | +2.1912 |
| 2026-09-03 02:33:25 | **CADENCE:** CADENCE rider ws7 - t1 gcws30b past the 95.0 fence 02:31:30..02:32:55, ws1r reversed 02:32:45 during, r 63.15 past the 56.0 fence, stamp 02:32:45, cross 02:33:00 hold 6 bars \| rider ws7 48.56, no-longer-exfence yes, reversed yes \| mage-cascade down | none offered | 2: ws3,ws4 | last 02:26:55, 6.5 min ago | 0.159030 | +2.1912 |
| 2026-09-03 02:33:25 | **CADENCE:** EXHAUST rider ws7 - t4 at a t1 cadence - rider ws7 48.56, no candidate at or below ws15 (the jump bound 8) | - | 2: ws3,ws4 | last 02:26:55, 6.5 min ago | 0.159030 | +2.1912 |
| 2026-09-03 02:33:25 | THIS LEG CLOSES on t1, realised +2.1463, drag 0.1975, net +1.9488 | - | 2: ws3,ws4 | last 02:26:55, 6.5 min ago | 0.159030 | +2.1912 |

## 2026-09-03 leg 2 - SHORT   opens 2026-09-03 02:33:30   exits 2026-09-03 05:19:25 on t1   held 165.9 min   MAE 1.0569   MFE 1.2519   realised +0.0440   net -0.1535

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-09-03 02:33:30 | >>> THIS LEG OPENS SHORT | - | none | last 19:39:30, 414.0 min ago / counter-side 2026-09-03 02:26:55 | 0.158960 | -0.0000 |
| 2026-09-03 03:24:00 | ARM - ws4r: ws4r 8.52 oob | - | 3: ws1,ws3,ws4 | last 19:39:30, 464.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158580 | +0.2391 |
| 2026-09-03 03:24:00 | RETEST - ws1r 20.64 is not oob at the arm - the gate stays shut | - | 3: ws1,ws3,ws4 | last 19:39:30, 464.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158580 | +0.2391 |
| 2026-09-03 03:24:05 | NO RIDER - the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs | - | 3: ws1,ws3,ws4 | last 19:39:30, 464.6 min ago / counter-side 2026-09-03 03:15:55 | 0.158610 | +0.2202 |
| 2026-09-03 03:25:25 | LATCH1 - latch 1 at the t1 cadence 2026-09-03 03:25:25, divergence state -1 | - | 3: ws1,ws3,ws4 | last 19:39:30, 465.9 min ago / counter-side 2026-09-03 03:15:55 | 0.158690 | +0.1699 |
| 2026-09-03 03:25:25 | RIDER rider ws4 - t1 gcws30b past the 5.0 fence 03:24:00..03:24:55, ws1r reversed 03:24:15 during, r 23.33 past the 44.0 fence, stamp 03:24:15, cross 03:25:00 hold 6 bars \| ws4 r 9.72 picked up at a cadence, no prior rider | - | 3: ws1,ws3,ws4 | last 19:39:30, 465.9 min ago / counter-side 2026-09-03 03:15:55 | 0.158690 | +0.1699 |
| 2026-09-03 03:33:20 | BATON rider ws4 - ws4 -> ws5, between cadences, lin_hop 2 | ws5: 17.11 | 3: ws3,ws4,ws5 | last 19:39:30, 473.8 min ago / counter-side 2026-09-03 03:15:55 | 0.158780 | +0.1132 |
| 2026-09-03 03:49:00 | BATON rider ws5 - ws5 -> ws7, between cadences, lin_hop 2 | ws6: 16.07, ws7: 8.39 | 5: ws4,ws5,ws6,ws7,ws8 | last 19:39:30, 489.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158520 | +0.2768 |
| 2026-09-03 03:52:00 | BATON rider ws7 - ws7 -> ws8, between cadences, lin_hop 2 | ws8: 15.66 | 4: ws5,ws6,ws7,ws8 | last 19:39:30, 492.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158610 | +0.2202 |
| 2026-09-03 03:52:45 | NO PASS rider ws8 - ws8 17.49 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 4: ws5,ws6,ws7,ws8 | last 19:39:30, 493.2 min ago / counter-side 2026-09-03 03:15:55 | 0.158710 | +0.1573 |
| 2026-09-03 04:17:55 | LATCH1 rider ws8 - latch 1 at the t1 cadence 2026-09-03 04:17:55, divergence state -1 | - | 3: ws1,ws2,ws10 | last 19:39:30, 518.4 min ago / counter-side 2026-09-03 03:15:55 | 0.158140 | +0.5159 |
| 2026-09-03 04:17:55 | **CADENCE:** CADENCE rider ws8 - t1 gcws30b past the 5.0 fence 04:15:00..04:17:25, ws1r reversed 04:16:50 during, r 25.16 past the 44.0 fence, stamp 04:16:50, cross 04:17:30 hold 6 bars \| rider ws8 29.38, no-longer-exfence yes, reversed yes \| mage-cascade up | ws10: 18.59 | 3: ws1,ws2,ws10 | last 19:39:30, 518.4 min ago / counter-side 2026-09-03 03:15:55 | 0.158140 | +0.5159 |
| 2026-09-03 04:17:55 | **CADENCE:** BATON rider ws8 - ws8 -> ws10, at a t1 cadence, capped at ws16 by the jump bound 8 | ws10: 18.59 | 3: ws1,ws2,ws10 | last 19:39:30, 518.4 min ago / counter-side 2026-09-03 03:15:55 | 0.158140 | +0.5159 |
| 2026-09-03 04:23:05 | NO PASS rider ws10 - ws10 15.92 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 2: ws2,ws10 | last 19:39:30, 523.6 min ago / counter-side 2026-09-03 03:15:55 | 0.158290 | +0.4215 |
| 2026-09-03 04:35:20 | the favourable extreme - MFE 1.2519 | - | 3: ws10,ws11,ws12 | last 19:39:30, 535.8 min ago / counter-side 2026-09-03 03:15:55 | 0.156970 | +1.2519 |
| 2026-09-03 04:37:30 | LATCH1 rider ws10 - latch 1 at the t1 cadence 2026-09-03 04:37:30, divergence state -1 | - | 3: ws10,ws11,ws12 | last 19:39:30, 538.0 min ago / counter-side 2026-09-03 03:15:55 | 0.157620 | +0.8430 |
| 2026-09-03 04:37:30 | **CADENCE:** CADENCE rider ws10 - t1 gcws30b back inside the 5.0 fence 04:36:00, ws1r reversed 04:37:30 inside the 120s grace from the cross bar 04:36:00, r 34.10 past the 44.0 fence, stamp 04:37:30, hold 6 bars \| rider ws10 15.79, no-longer-exfence no, reversed yes \| mage-cascade down | ws11: 22.00, ws12: 13.72 | 3: ws10,ws11,ws12 | last 19:39:30, 538.0 min ago / counter-side 2026-09-03 03:15:55 | 0.157620 | +0.8430 |
| 2026-09-03 04:37:30 | **CADENCE:** BATON rider ws10 - ws10 -> ws12, at a t1 cadence, capped at ws18 by the jump bound 8 | ws11: 22.00, ws12: 13.72 | 3: ws10,ws11,ws12 | last 19:39:30, 538.0 min ago / counter-side 2026-09-03 03:15:55 | 0.157620 | +0.8430 |
| 2026-09-03 04:37:30 | **CADENCE:** CADENCE rider ws12 - t1 gcws30b back inside the 5.0 fence 04:37:00, ws1r reversed 04:37:30 inside the 120s grace from the cross bar 04:37:00, r 34.10 past the 44.0 fence, stamp 04:37:30, hold 6 bars \| rider ws12 13.72, no-longer-exfence no, reversed no \| mage-cascade down | none offered | 3: ws10,ws11,ws12 | last 19:39:30, 538.0 min ago / counter-side 2026-09-03 03:15:55 | 0.157620 | +0.8430 |
| 2026-09-03 04:37:30 | HOLD rider ws12 - rider ws12 13.72 oob - no action | - | 3: ws10,ws11,ws12 | last 19:39:30, 538.0 min ago / counter-side 2026-09-03 03:15:55 | 0.157620 | +0.8430 |
| 2026-09-03 04:38:55 | NO PASS rider ws12 - ws12 17.09 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 3: ws10,ws11,ws12 | last 19:39:30, 539.4 min ago / counter-side 2026-09-03 03:15:55 | 0.157850 | +0.6983 |
| 2026-09-03 05:01:30 | the ADVERSE extreme - MAE 1.0569 | - | 3: ws15,ws16,ws17 | last 19:39:30, 562.0 min ago / counter-side 2026-09-03 03:15:55 | 0.160640 | -1.0569 |
| 2026-09-03 05:19:25 | **CADENCE:** CADENCE rider ws12 - t1 gcws30b back inside the 5.0 fence 05:19:00, ws1r reversed 05:19:15 inside the 120s grace from the cross bar 05:19:00, r 34.20 past the 44.0 fence, stamp 05:19:15, hold 6 bars \| rider ws12 49.12, no-longer-exfence yes, reversed yes \| mage-cascade down | none offered | 1: ws2 | last 19:39:30, 579.9 min ago / counter-side 2026-09-03 03:15:55 | 0.158840 | +0.0755 |
| 2026-09-03 05:19:25 | **CADENCE:** EXHAUST rider ws12 - t4 at a t1 cadence - rider ws12 49.12, no candidate at or below ws20 (the jump bound 8) | - | 1: ws2 | last 19:39:30, 579.9 min ago / counter-side 2026-09-03 03:15:55 | 0.158840 | +0.0755 |
| 2026-09-03 05:19:25 | THIS LEG CLOSES on t1, realised +0.0440, drag 0.1975, net -0.1535 | - | 1: ws2 | last 19:39:30, 579.9 min ago / counter-side 2026-09-03 03:15:55 | 0.158840 | +0.0755 |

## 2026-09-03 leg 3 - LONG   opens 2026-09-03 05:19:30   exits 2026-09-03 06:25:25 on t1   held 65.9 min   MAE 1.0196   MFE 1.1329   realised +0.7615   net +0.5640

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-09-03 05:19:30 | >>> THIS LEG OPENS LONG | - | 1: ws5 | last 03:15:55, 123.6 min ago | 0.158890 | +0.0000 |
| 2026-09-03 05:28:05 | the ADVERSE extreme - MAE 1.0196 | - | none | last 03:15:55, 132.2 min ago | 0.157270 | -1.0196 |
| 2026-09-03 05:52:00 | ARM - ws4r: ws4r 87.74 oob | - | 3: ws1,ws2,ws3 | last 03:15:55, 156.1 min ago | 0.160360 | +0.9252 |
| 2026-09-03 05:52:00 | RETEST - ws1r 81.09 is not oob at the arm - the gate stays shut | - | 3: ws1,ws2,ws3 | last 03:15:55, 156.1 min ago | 0.160360 | +0.9252 |
| 2026-09-03 05:52:05 | NO RIDER - the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs | - | 3: ws1,ws2,ws3 | last 03:15:55, 156.2 min ago | 0.160340 | +0.9126 |
| 2026-09-03 05:52:55 | LATCH1 - latch 1 at the t1 cadence 2026-09-03 05:52:55, divergence state +1 | - | 3: ws1,ws2,ws3 | last 03:15:55, 157.0 min ago | 0.160210 | +0.8308 |
| 2026-09-03 05:52:55 | RIDER rider ws3 - t1 gcws30b past the 95.0 fence 05:51:30..05:52:25, ws1r reversed 05:52:25 during, r 78.18 past the 56.0 fence, stamp 05:52:25, cross 05:52:30 hold 6 bars \| ws3 r 96.36 picked up at a cadence, no prior rider | - | 3: ws1,ws2,ws3 | last 03:15:55, 157.0 min ago | 0.160210 | +0.8308 |
| 2026-09-03 05:59:20 | the favourable extreme - MFE 1.1329 | - | 2: ws3,ws4 | last 03:15:55, 163.4 min ago | 0.160690 | +1.1329 |
| 2026-09-03 06:03:50 | BATON rider ws3 - ws3 -> ws4, between cadences, lin_hop 2 | ws4: 87.86 | 2: ws3,ws4 | last 03:15:55, 167.9 min ago | 0.160120 | +0.7741 |
| 2026-09-03 06:04:55 | NO PASS rider ws4 - ws4 75.07 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 2: ws3,ws4 | last 03:15:55, 169.0 min ago | 0.159990 | +0.6923 |
| 2026-09-03 06:25:25 | LATCH1 rider ws4 - latch 1 at the t1 cadence 2026-09-03 06:25:25, divergence state +1 | - | 1: ws14 | last 03:15:55, 189.5 min ago | 0.160210 | +0.8308 |
| 2026-09-03 06:25:25 | **CADENCE:** CADENCE rider ws4 - t1 gcws30b past the 95.0 fence 06:24:30..06:24:55, ws1r reversed 06:24:35 during, r 62.38 past the 56.0 fence, stamp 06:24:35, cross 06:25:00 hold 6 bars \| rider ws4 32.29, no-longer-exfence yes, reversed yes \| mage-cascade down | none offered | 1: ws14 | last 03:15:55, 189.5 min ago | 0.160210 | +0.8308 |
| 2026-09-03 06:25:25 | **CADENCE:** EXHAUST rider ws4 - t4 at a t1 cadence - rider ws4 32.29, no candidate at or below ws12 (the jump bound 8) | - | 1: ws14 | last 03:15:55, 189.5 min ago | 0.160210 | +0.8308 |
| 2026-09-03 06:25:25 | THIS LEG CLOSES on t1, realised +0.7615, drag 0.1975, net +0.5640 | - | 1: ws14 | last 03:15:55, 189.5 min ago | 0.160210 | +0.8308 |

## 2026-09-03 leg 4 - SHORT   opens 2026-09-03 06:25:30   exits 2026-09-03 08:07:00 on STOP at 1.10%   held 101.5 min   MAE 1.1000   MFE 0.1374   realised -1.1000   net -1.2975

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-09-03 06:25:30 | >>> THIS LEG OPENS SHORT | - | 1: ws3 | last 19:39:30, 646.0 min ago / counter-side 2026-09-03 03:15:55 | 0.160100 | -0.0000 |
| 2026-09-03 07:32:05 | ARM - gcws30b+(ws1r\|ws2r): gcws30b -5.70 at or beyond the 5.0/95.0 fence, held 6 bars, + ws2r oob (ws1r 19.20, ws2r 14.04) | - | 5: ws1,ws2,ws3,ws6,ws7 | last 19:39:30, 712.6 min ago / counter-side 2026-09-03 07:15:45 | 0.160150 | -0.0312 |
| 2026-09-03 07:32:05 | RETEST - ws1r 19.20 is not oob at the arm - the gate stays shut | - | 5: ws1,ws2,ws3,ws6,ws7 | last 19:39:30, 712.6 min ago / counter-side 2026-09-03 07:15:45 | 0.160150 | -0.0312 |
| 2026-09-03 07:32:10 | NO RIDER - the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs | - | 5: ws1,ws2,ws3,ws6,ws7 | last 19:39:30, 712.7 min ago / counter-side 2026-09-03 07:15:45 | 0.160260 | -0.0999 |
| 2026-09-03 07:32:55 | RIDER rider ws7 - t1 gcws30b past the 5.0 fence 07:30:30..07:32:25, ws1r reversed 07:32:10 during, r 22.68 past the 44.0 fence, stamp 07:32:10, cross 07:32:30 hold 6 bars \| ws7 r 17.20 picked up at a cadence, no prior rider | - | 4: ws2,ws3,ws6,ws7 | last 19:39:30, 713.4 min ago / counter-side 2026-09-03 07:15:45 | 0.160490 | -0.2436 |
| 2026-09-03 07:40:00 | NO PASS rider ws7 - ws7 27.97 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 2: ws6,ws7 | last 19:39:30, 720.5 min ago / counter-side 2026-09-03 07:15:45 | 0.161480 | -0.8620 |
| 2026-09-03 07:50:05 | the favourable extreme - MFE 0.1374 | - | 3: ws1,ws6,ws9 | last 19:39:30, 730.6 min ago / counter-side 2026-09-03 07:15:45 | 0.159880 | +0.1374 |
| 2026-09-03 08:07:00 | the ADVERSE extreme - MAE 1.1118 | - | 1: ws7 | last 19:39:30, 747.5 min ago / counter-side 2026-09-03 07:15:45 | 0.161880 | -1.1118 |
| 2026-09-03 08:07:00 | THIS LEG CLOSES on STOP at 1.10%, realised -1.1000, drag 0.1975, net -1.2975 | - | 1: ws7 | last 19:39:30, 747.5 min ago / counter-side 2026-09-03 07:15:45 | 0.161840 | -1.0868 |
| 2026-09-03 08:42:00 | LATCH1 rider ws7 - latch 1 at the t1 cadence 2026-09-03 08:42:00, divergence state -1 | - | 3: ws3,ws4,ws13 | last 19:39:30, 782.5 min ago / counter-side 2026-09-03 07:15:45 | 0.160660 | -0.3498 |
| 2026-09-03 08:42:00 | **CADENCE:** CADENCE rider ws7 - t1 gcws30b back inside the 5.0 fence 08:40:30, ws1r reversed 08:42:00 inside the 120s grace from the cross bar 08:40:30, r 37.00 past the 44.0 fence, stamp 08:42:00, hold 6 bars \| rider ws7 51.52, no-longer-exfence yes, reversed yes \| mage-cascade up | ws13: 16.88 | 3: ws3,ws4,ws13 | last 19:39:30, 782.5 min ago / counter-side 2026-09-03 07:15:45 | 0.160660 | -0.3498 |
| 2026-09-03 08:42:00 | **CADENCE:** BATON rider ws7 - ws7 -> ws13, at a t1 cadence, capped at ws15 by the jump bound 8 | ws13: 16.88 | 3: ws3,ws4,ws13 | last 19:39:30, 782.5 min ago / counter-side 2026-09-03 07:15:45 | 0.160660 | -0.3498 |
| 2026-09-03 08:54:25 | LATCH1 rider ws13 - latch 1 at the t1 cadence 2026-09-03 08:54:25, divergence state -1 | - | 7: ws1,ws3,ws4,ws5,ws12,ws13,ws14 | last 19:39:30, 794.9 min ago / counter-side 2026-09-03 07:15:45 | 0.160400 | -0.1874 |
| 2026-09-03 08:54:25 | **CADENCE:** CADENCE rider ws13 - t1 gcws30b past the 5.0 fence 08:52:00..08:53:55, ws1r reversed 08:53:40 during, r 16.63 past the 44.0 fence, stamp 08:53:40, cross 08:54:00 hold 6 bars \| rider ws13 18.50, no-longer-exfence no, reversed yes \| mage-cascade down | ws14: 24.52 | 7: ws1,ws3,ws4,ws5,ws12,ws13,ws14 | last 19:39:30, 794.9 min ago / counter-side 2026-09-03 07:15:45 | 0.160400 | -0.1874 |
| 2026-09-03 08:54:25 | **CADENCE:** BATON rider ws13 - ws13 -> ws14, at a t1 cadence, capped at ws21 by the jump bound 8 | ws14: 24.52 | 7: ws1,ws3,ws4,ws5,ws12,ws13,ws14 | last 19:39:30, 794.9 min ago / counter-side 2026-09-03 07:15:45 | 0.160400 | -0.1874 |
| 2026-09-03 09:04:55 | LATCH1 rider ws14 - latch 1 at the t1 cadence 2026-09-03 09:04:55, divergence state -1 | - | 11: ws2,ws3,ws4,ws5,ws6,ws8,ws12,ws13,ws14,ws15,ws16 | last 19:39:30, 805.4 min ago / counter-side 2026-09-03 07:15:45 | 0.160170 | -0.0437 |
| 2026-09-03 09:04:55 | **CADENCE:** CADENCE rider ws14 - t1 gcws30b back inside the 5.0 fence 09:04:30, ws1r reversed 09:04:50 inside the 120s grace from the cross bar 09:04:30, r 30.57 past the 44.0 fence, stamp 09:04:50, hold 6 bars \| rider ws14 23.44, no-longer-exfence no, reversed no \| mage-cascade down | ws15: 18.63, ws16: 23.22 | 11: ws2,ws3,ws4,ws5,ws6,ws8,ws12,ws13,ws14,ws15,ws16 | last 19:39:30, 805.4 min ago / counter-side 2026-09-03 07:15:45 | 0.160170 | -0.0437 |
| 2026-09-03 09:04:55 | **CADENCE:** BATON rider ws14 - ws14 -> ws16, at a t1 cadence, capped at ws22 by the jump bound 8 | ws15: 18.63, ws16: 23.22 | 11: ws2,ws3,ws4,ws5,ws6,ws8,ws12,ws13,ws14,ws15,ws16 | last 19:39:30, 805.4 min ago / counter-side 2026-09-03 07:15:45 | 0.160170 | -0.0437 |
| 2026-09-03 09:06:55 | LATCH1 rider ws16 - latch 1 at the t1 cadence 2026-09-03 09:06:55, divergence state -1 | - | 12: ws2,ws3,ws4,ws5,ws6,ws8,ws12,ws13,ws14,ws15,ws16,ws21 | last 19:39:30, 807.4 min ago / counter-side 2026-09-03 07:15:45 | 0.160060 | +0.0250 |
| 2026-09-03 09:06:55 | **CADENCE:** CADENCE rider ws16 - t1 gcws30b past the 5.0 fence 09:06:00..09:06:25, ws1r reversed 09:06:15 during, r 25.94 past the 44.0 fence, stamp 09:06:15, cross 09:06:30 hold 6 bars \| rider ws16 21.98, no-longer-exfence no, reversed no \| mage-cascade down | ws21: 19.03 | 12: ws2,ws3,ws4,ws5,ws6,ws8,ws12,ws13,ws14,ws15,ws16,ws21 | last 19:39:30, 807.4 min ago / counter-side 2026-09-03 07:15:45 | 0.160060 | +0.0250 |
| 2026-09-03 09:06:55 | **CADENCE:** BATON rider ws16 - ws16 -> ws21, at a t1 cadence, capped at ws24 by the jump bound 8 | ws21: 19.03 | 12: ws2,ws3,ws4,ws5,ws6,ws8,ws12,ws13,ws14,ws15,ws16,ws21 | last 19:39:30, 807.4 min ago / counter-side 2026-09-03 07:15:45 | 0.160060 | +0.0250 |
| 2026-09-03 09:33:50 | NO PASS rider ws21 - ws21 17.87 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 11: ws2,ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws19,ws21 | last 19:39:30, 834.3 min ago / counter-side 2026-09-03 07:15:45 | 0.160170 | -0.0437 |
| 2026-09-03 09:43:25 | LATCH1 rider ws21 - latch 1 at the t1 cadence 2026-09-03 09:43:25, divergence state -1 | - | 13: ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21 | last 19:39:30, 843.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159880 | +0.1374 |
| 2026-09-03 09:43:25 | **CADENCE:** CADENCE rider ws21 - t1 gcws30b past the 5.0 fence 09:41:30..09:42:55, ws1r reversed 09:42:55 during, r 34.84 past the 44.0 fence, stamp 09:42:55, cross 09:43:00 hold 6 bars \| rider ws21 15.12, no-longer-exfence no, reversed yes \| mage-cascade up | none offered | 13: ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21 | last 19:39:30, 843.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159880 | +0.1374 |
| 2026-09-03 09:43:25 | **CADENCE:** EXHAUST rider ws21 - t4 at a t1 cadence - rider ws21 15.12, no candidate at or below ws29 (the jump bound 8) | - | 13: ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21 | last 19:39:30, 843.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159880 | +0.1374 |

| the read | value |
|---|---|
| legs in the chain over the window | 4 |
| legs opening on 2026-09-03 | 4 |
| seconds to compute | 47.6 |
