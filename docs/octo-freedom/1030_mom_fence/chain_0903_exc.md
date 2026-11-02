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
| 2026-09-03 | 1 | 1 | 2026-09-03 00:37:00 | LONG | 2026-09-03 02:37:25 | t1 | 120.4 | ws4 > ws6 > ws7 | 0.1735 | +2.5447 | +2.1720 | 0.1975 | +1.9745 |
| 2026-09-03 | 2 | 2 | 2026-09-03 02:37:30 | SHORT | 2026-09-03 04:38:55 | t1 | 121.4 | ws4 > ws5 > ws7 > ws8 > ws10 > ws12 | 0.5094 | +1.2767 | +0.7862 | 0.1975 | +0.5887 |
| 2026-09-03 | 3 | 3 | 2026-09-03 04:39:00 | LONG | 2026-09-03 05:54:25 | t1 | 75.4 | ws3 > ws5 | 0.3043 | +1.8320 | +1.6165 | 0.1975 | +1.4190 |
| 2026-09-03 | 4 | 4 | 2026-09-03 05:54:30 | SHORT | 2026-09-03 09:44:25 | t1 | 229.9 | ws7 > ws13 > ws14 > ws21 | 1.0792 | +0.6238 | +0.1934 | 0.1975 | -0.0041 |
| 2026-09-03 | 5 | 5 | 2026-09-03 09:44:30 | LONG | 2026-09-03 10:25:55 | STOP at 1.10% | 41.4 | ws4 > ws5 > ws7 > ws10 > ws12 > ws14 > ws17 > ws22 > ws27 > ws29 > ws30 | 1.1000 | +0.1500 | -1.1000 | 0.1975 | -1.2975 |
| TOTAL | | 5 scored legs | | | | | 588.6 | | 3.1664 | +6.4272 | +3.6680 | 0.9875 | +2.6805 |

## 2026-09-03 leg 1 - LONG   opens 2026-09-03 00:37:00   exits 2026-09-03 02:37:25 on t1   held 120.4 min   MAE 0.1735   MFE 2.5447   realised +2.1720   net +1.9745

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-09-03 00:37:00 | >>> THIS LEG OPENS LONG | - | 3: ws13,ws24,ws28 | last 15:45:35, 531.4 min ago / counter-side 2026-09-02 19:39:30 | 0.155620 | +0.0000 |
| 2026-09-03 01:01:30 | the ADVERSE extreme - MAE 0.1735 | - | 1: ws3 | last 15:45:35, 555.9 min ago / counter-side 2026-09-02 19:39:30 | 0.155350 | -0.1735 |
| 2026-09-03 01:08:30 | ARM - ws4r: ws4r 85.04 oob | - | 1: ws4 | last 15:45:35, 562.9 min ago / counter-side 2026-09-02 19:39:30 | 0.157460 | +1.1824 |
| 2026-09-03 01:08:30 | RETEST - ws1r 81.14 is not oob at the arm - the gate stays shut | - | 1: ws4 | last 15:45:35, 562.9 min ago / counter-side 2026-09-02 19:39:30 | 0.157460 | +1.1824 |
| 2026-09-03 01:08:35 | NO RIDER - the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs | - | 1: ws4 | last 15:45:35, 563.0 min ago / counter-side 2026-09-02 19:39:30 | 0.157460 | +1.1824 |
| 2026-09-03 01:10:55 | RIDER rider ws4 - t1 gcws30b journey 01:06:30..01:10:50 reached 125.83 past the 95.0 fence, ws1r reversed 01:10:50 during, r 82.91 past the 56.0 fence, stamp 01:10:50, ib 85.0 cross 01:10:00 hold 6 bars, ib dwell 12 bars \| ws4 r 82.73 picked up at a cadence, no prior rider | - | 2: ws1,ws4 | last 15:45:35, 565.3 min ago / counter-side 2026-09-02 19:39:30 | 0.157280 | +1.0667 |
| 2026-09-03 01:36:55 | BATON rider ws4 - ws4 -> ws6, between cadences, lin_hop 2 | ws5: 89.87, ws6: 90.51 | 3: ws4,ws5,ws6 | last 15:45:35, 591.3 min ago / counter-side 2026-09-02 19:39:30 | 0.157930 | +1.4844 |
| 2026-09-03 01:36:55 | LATCH1 rider ws6 - latch 1 at the t1 cadence 2026-09-03 01:36:55, divergence state +1 | - | 3: ws4,ws5,ws6 | last 15:45:35, 591.3 min ago / counter-side 2026-09-02 19:39:30 | 0.157930 | +1.4844 |
| 2026-09-03 01:36:55 | **CADENCE:** CADENCE rider ws6 - t1 gcws30b journey 01:32:00..01:36:50 reached 125.44 past the 95.0 fence, ws1r reversed 01:35:15 during, r 75.77 past the 56.0 fence, stamp 01:35:15, ib 85.0 cross 01:36:00 hold 6 bars, ib dwell 12 bars \| rider ws6 90.51, no-longer-exfence no, reversed no \| mage-cascade down | none offered | 3: ws4,ws5,ws6 | last 15:45:35, 591.3 min ago / counter-side 2026-09-02 19:39:30 | 0.157930 | +1.4844 |
| 2026-09-03 01:36:55 | HOLD rider ws6 - rider ws6 90.51 oob - no action | - | 3: ws4,ws5,ws6 | last 15:45:35, 591.3 min ago / counter-side 2026-09-02 19:39:30 | 0.157930 | +1.4844 |
| 2026-09-03 01:47:00 | BATON rider ws6 - ws6 -> ws7, between cadences, lin_hop 2 | ws7: 87.00 | 3: ws5,ws6,ws7 | last 15:45:35, 601.4 min ago / counter-side 2026-09-02 19:39:30 | 0.157790 | +1.3944 |
| 2026-09-03 01:48:05 | NO PASS rider ws7 - ws7 84.75 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 3: ws5,ws6,ws7 | last 15:45:35, 602.5 min ago / counter-side 2026-09-02 19:39:30 | 0.157650 | +1.3045 |
| 2026-09-03 02:35:10 | the favourable extreme - MFE 2.5447 | - | 3: ws1,ws3,ws4 | last 02:26:55, 8.2 min ago | 0.159580 | +2.5447 |
| 2026-09-03 02:37:25 | LATCH1 rider ws7 - latch 1 at the t1 cadence 2026-09-03 02:37:25, divergence state +1 | - | 2: ws3,ws4 | last 02:26:55, 10.5 min ago | 0.158940 | +2.1334 |
| 2026-09-03 02:37:25 | **CADENCE:** CADENCE rider ws7 - t1 gcws30b journey 02:31:00..02:37:20 reached 116.55 past the 95.0 fence, ws1r reversed 02:35:00 during, r 78.55 past the 56.0 fence, stamp 02:35:00, ib 85.0 cross 02:36:30 hold 6 bars, ib dwell 12 bars \| rider ws7 54.88, no-longer-exfence yes, reversed yes \| mage-cascade down | none offered | 2: ws3,ws4 | last 02:26:55, 10.5 min ago | 0.158940 | +2.1334 |
| 2026-09-03 02:37:25 | **CADENCE:** EXHAUST rider ws7 - t4 at a t1 cadence - rider ws7 54.88, no candidate at or below ws15 (the jump bound 8) | - | 2: ws3,ws4 | last 02:26:55, 10.5 min ago | 0.158940 | +2.1334 |
| 2026-09-03 02:37:25 | THIS LEG CLOSES on t1, realised +2.1720, drag 0.1975, net +1.9745 | - | 2: ws3,ws4 | last 02:26:55, 10.5 min ago | 0.158940 | +2.1334 |

## 2026-09-03 leg 2 - SHORT   opens 2026-09-03 02:37:30   exits 2026-09-03 04:38:55 on t1   held 121.4 min   MAE 0.5094   MFE 1.2767   realised +0.7862   net +0.5887

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-09-03 02:37:30 | >>> THIS LEG OPENS SHORT | - | none | last 19:39:30, 418.0 min ago / counter-side 2026-09-03 02:26:55 | 0.159000 | -0.0000 |
| 2026-09-03 02:57:20 | the ADVERSE extreme - MAE 0.5094 | - | none | last 19:39:30, 437.8 min ago / counter-side 2026-09-03 02:26:55 | 0.159810 | -0.5094 |
| 2026-09-03 03:24:00 | ARM - ws4r: ws4r 8.52 oob | - | 3: ws1,ws3,ws4 | last 19:39:30, 464.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158580 | +0.2642 |
| 2026-09-03 03:24:00 | RETEST - ws1r 20.64 is not oob at the arm - the gate stays shut | - | 3: ws1,ws3,ws4 | last 19:39:30, 464.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158580 | +0.2642 |
| 2026-09-03 03:24:05 | NO RIDER - the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs | - | 3: ws1,ws3,ws4 | last 19:39:30, 464.6 min ago / counter-side 2026-09-03 03:15:55 | 0.158610 | +0.2453 |
| 2026-09-03 03:26:25 | LATCH1 - latch 1 at the t1 cadence 2026-09-03 03:26:25, divergence state -1 | - | 3: ws1,ws3,ws4 | last 19:39:30, 466.9 min ago / counter-side 2026-09-03 03:15:55 | 0.158860 | +0.0881 |
| 2026-09-03 03:26:25 | RIDER rider ws4 - t1 gcws30b journey 03:23:30..03:26:20 reached 2.23 past the 5.0 fence, ws1r reversed 03:25:25 during, r 20.64 past the 44.0 fence, stamp 03:25:25, ib 15.0 cross 03:25:30 hold 6 bars, ib dwell 12 bars \| ws4 r 11.63 picked up at a cadence, no prior rider | - | 3: ws1,ws3,ws4 | last 19:39:30, 466.9 min ago / counter-side 2026-09-03 03:15:55 | 0.158860 | +0.0881 |
| 2026-09-03 03:33:20 | BATON rider ws4 - ws4 -> ws5, between cadences, lin_hop 2 | ws5: 17.11 | 3: ws3,ws4,ws5 | last 19:39:30, 473.8 min ago / counter-side 2026-09-03 03:15:55 | 0.158780 | +0.1384 |
| 2026-09-03 03:49:00 | BATON rider ws5 - ws5 -> ws7, between cadences, lin_hop 2 | ws6: 16.07, ws7: 8.39 | 5: ws4,ws5,ws6,ws7,ws8 | last 19:39:30, 489.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158520 | +0.3019 |
| 2026-09-03 03:52:00 | BATON rider ws7 - ws7 -> ws8, between cadences, lin_hop 2 | ws8: 15.66 | 4: ws5,ws6,ws7,ws8 | last 19:39:30, 492.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158610 | +0.2453 |
| 2026-09-03 03:52:45 | NO PASS rider ws8 - ws8 17.49 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 4: ws5,ws6,ws7,ws8 | last 19:39:30, 493.2 min ago / counter-side 2026-09-03 03:15:55 | 0.158710 | +0.1824 |
| 2026-09-03 04:23:25 | **CADENCE:** CADENCE rider ws8 - t1 gcws30b journey 04:14:00..04:23:20 reached -24.03 past the 5.0 fence, ws1r reversed 04:19:00 during, r 16.29 past the 44.0 fence, stamp 04:19:00, ib 15.0 cross 04:22:30 hold 6 bars, ib dwell 12 bars \| rider ws8 31.59, no-longer-exfence yes, reversed yes \| mage-cascade down | ws10: 15.92 | 2: ws2,ws10 | last 19:39:30, 523.9 min ago / counter-side 2026-09-03 03:15:55 | 0.158290 | +0.4465 |
| 2026-09-03 04:23:25 | **CADENCE:** BATON rider ws8 - ws8 -> ws10, at a t1 cadence, capped at ws16 by the jump bound 8 | ws10: 15.92 | 2: ws2,ws10 | last 19:39:30, 523.9 min ago / counter-side 2026-09-03 03:15:55 | 0.158290 | +0.4465 |
| 2026-09-03 04:27:20 | BATON rider ws10 - ws10 -> ws12, between cadences, lin_hop 2 | ws11: 17.58, ws12: 12.35 | 4: ws3,ws10,ws11,ws12 | last 19:39:30, 527.8 min ago / counter-side 2026-09-03 03:15:55 | 0.158310 | +0.4340 |
| 2026-09-03 04:35:20 | the favourable extreme - MFE 1.2767 | - | 3: ws10,ws11,ws12 | last 19:39:30, 535.8 min ago / counter-side 2026-09-03 03:15:55 | 0.156970 | +1.2767 |
| 2026-09-03 04:38:55 | NO PASS rider ws12 - ws12 17.09 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 3: ws10,ws11,ws12 | last 19:39:30, 539.4 min ago / counter-side 2026-09-03 03:15:55 | 0.157850 | +0.7233 |
| 2026-09-03 04:38:55 | LATCH1 rider ws12 - latch 1 at the t1 cadence 2026-09-03 04:38:55, divergence state -1 | - | 3: ws10,ws11,ws12 | last 19:39:30, 539.4 min ago / counter-side 2026-09-03 03:15:55 | 0.157850 | +0.7233 |
| 2026-09-03 04:38:55 | **CADENCE:** CADENCE rider ws12 - t1 gcws30b journey 04:34:30..04:38:50 reached -17.54 past the 5.0 fence, ws1r reversed 04:38:00 during, r 33.98 past the 44.0 fence, stamp 04:38:00, ib 15.0 cross 04:38:00 hold 6 bars, ib dwell 12 bars \| rider ws12 17.09, no-longer-exfence no, reversed yes \| mage-cascade down | none offered | 3: ws10,ws11,ws12 | last 19:39:30, 539.4 min ago / counter-side 2026-09-03 03:15:55 | 0.157850 | +0.7233 |
| 2026-09-03 04:38:55 | **CADENCE:** EXHAUST rider ws12 - t4 at a t1 cadence - rider ws12 17.09, no candidate at or below ws20 (the jump bound 8) | - | 3: ws10,ws11,ws12 | last 19:39:30, 539.4 min ago / counter-side 2026-09-03 03:15:55 | 0.157850 | +0.7233 |
| 2026-09-03 04:38:55 | THIS LEG CLOSES on t1, realised +0.7862, drag 0.1975, net +0.5887 | - | 3: ws10,ws11,ws12 | last 19:39:30, 539.4 min ago / counter-side 2026-09-03 03:15:55 | 0.157850 | +0.7233 |

## 2026-09-03 leg 3 - LONG   opens 2026-09-03 04:39:00   exits 2026-09-03 05:54:25 on t1   held 75.4 min   MAE 0.3043   MFE 1.8320   realised +1.6165   net +1.4190

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-09-03 04:39:00 | >>> THIS LEG OPENS LONG | - | none | last 03:15:55, 83.1 min ago | 0.157750 | +0.0000 |
| 2026-09-03 04:52:25 | ARM - gcws30b+(ws1r\|ws2r): gcws30b 99.67 at or beyond the 5.0/95.0 fence, held 6 bars, + ws1r oob (ws1r 96.86, ws2r 84.26) | - | 2: ws1,ws2 | last 03:15:55, 96.5 min ago | 0.159300 | +0.9826 |
| 2026-09-03 04:52:25 | RETEST - ws2r 84.26 / ws3r 67.59 - not both inside the fence at the arm | - | 2: ws1,ws2 | last 03:15:55, 96.5 min ago | 0.159300 | +0.9826 |
| 2026-09-03 04:52:30 | NO RIDER - the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs | - | 2: ws1,ws2 | last 03:15:55, 96.6 min ago | 0.159450 | +1.0777 |
| 2026-09-03 05:01:30 | the favourable extreme - MFE 1.8320 | - | 2: ws2,ws3 | last 03:15:55, 105.6 min ago | 0.160640 | +1.8320 |
| 2026-09-03 05:02:55 | LATCH1 - latch 1 at the t1 cadence 2026-09-03 05:02:55, divergence state +1 | - | 2: ws2,ws3 | last 03:15:55, 107.0 min ago | 0.160100 | +1.4897 |
| 2026-09-03 05:02:55 | RIDER rider ws3 - t1 gcws30b journey 04:51:30..05:02:50 reached 101.31 past the 95.0 fence, ws1r reversed 04:58:00 during, r 84.08 past the 56.0 fence, stamp 04:58:00, ib 85.0 cross 05:02:00 hold 6 bars, ib dwell 12 bars \| ws3 r 95.43 picked up at a cadence, no prior rider | - | 2: ws2,ws3 | last 03:15:55, 107.0 min ago | 0.160100 | +1.4897 |
| 2026-09-03 05:06:55 | BATON rider ws3 - ws3 -> ws5, between cadences, lin_hop 2 | ws4: 84.76, ws5: 89.22 | 4: ws2,ws3,ws4,ws5 | last 03:15:55, 111.0 min ago | 0.159780 | +1.2868 |
| 2026-09-03 05:10:55 | NO PASS rider ws5 - ws5 82.92 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 2: ws4,ws5 | last 03:15:55, 115.0 min ago | 0.159540 | +1.1347 |
| 2026-09-03 05:28:05 | the ADVERSE extreme - MAE 0.3043 | - | none | last 03:15:55, 132.2 min ago | 0.157270 | -0.3043 |
| 2026-09-03 05:54:25 | LATCH1 rider ws5 - latch 1 at the t1 cadence 2026-09-03 05:54:25, divergence state +1 | - | 2: ws1,ws3 | last 03:15:55, 158.5 min ago | 0.160250 | +1.5848 |
| 2026-09-03 05:54:25 | **CADENCE:** CADENCE rider ws5 - t1 gcws30b journey 05:50:00..05:54:20 reached 97.04 past the 95.0 fence, ws1r reversed 05:54:00 during, r 87.12 past the 56.0 fence, stamp 05:54:00, ib 85.0 cross 05:53:30 hold 6 bars, ib dwell 12 bars \| rider ws5 58.61, no-longer-exfence yes, reversed yes \| mage-cascade down | none offered | 2: ws1,ws3 | last 03:15:55, 158.5 min ago | 0.160250 | +1.5848 |
| 2026-09-03 05:54:25 | **CADENCE:** EXHAUST rider ws5 - t4 at a t1 cadence - rider ws5 58.61, no candidate at or below ws13 (the jump bound 8) | - | 2: ws1,ws3 | last 03:15:55, 158.5 min ago | 0.160250 | +1.5848 |
| 2026-09-03 05:54:25 | THIS LEG CLOSES on t1, realised +1.6165, drag 0.1975, net +1.4190 | - | 2: ws1,ws3 | last 03:15:55, 158.5 min ago | 0.160250 | +1.5848 |

## 2026-09-03 leg 4 - SHORT   opens 2026-09-03 05:54:30   exits 2026-09-03 09:44:25 on t1   held 229.9 min   MAE 1.0792   MFE 0.6238   realised +0.1934   net -0.0041

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-09-03 05:54:30 | >>> THIS LEG OPENS SHORT | - | none | last 19:39:30, 615.0 min ago / counter-side 2026-09-03 03:15:55 | 0.160300 | -0.0000 |
| 2026-09-03 07:32:05 | ARM - gcws30b+(ws1r\|ws2r): gcws30b -5.70 at or beyond the 5.0/95.0 fence, held 6 bars, + ws2r oob (ws1r 19.20, ws2r 14.04) | - | 5: ws1,ws2,ws3,ws6,ws7 | last 19:39:30, 712.6 min ago / counter-side 2026-09-03 07:15:45 | 0.160150 | +0.0936 |
| 2026-09-03 07:32:05 | RETEST - ws1r 19.20 is not oob at the arm - the gate stays shut | - | 5: ws1,ws2,ws3,ws6,ws7 | last 19:39:30, 712.6 min ago / counter-side 2026-09-03 07:15:45 | 0.160150 | +0.0936 |
| 2026-09-03 07:32:10 | NO RIDER - the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs | - | 5: ws1,ws2,ws3,ws6,ws7 | last 19:39:30, 712.7 min ago / counter-side 2026-09-03 07:15:45 | 0.160260 | +0.0250 |
| 2026-09-03 07:33:55 | RIDER rider ws7 - t1 gcws30b journey 07:30:30..07:33:50 reached -7.57 past the 5.0 fence, ws1r reversed 07:32:10 during, r 18.48 past the 44.0 fence, stamp 07:32:10, ib 15.0 cross 07:33:00 hold 6 bars, ib dwell 12 bars \| ws7 r 17.20 picked up at a cadence, no prior rider | - | 4: ws2,ws3,ws6,ws7 | last 19:39:30, 714.4 min ago / counter-side 2026-09-03 07:15:45 | 0.160510 | -0.1310 |
| 2026-09-03 07:40:00 | NO PASS rider ws7 - ws7 27.97 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 2: ws6,ws7 | last 19:39:30, 720.5 min ago / counter-side 2026-09-03 07:15:45 | 0.161480 | -0.7361 |
| 2026-09-03 08:07:55 | the ADVERSE extreme - MAE 1.0792 | - | 1: ws7 | last 19:39:30, 748.4 min ago / counter-side 2026-09-03 07:15:45 | 0.162030 | -1.0792 |
| 2026-09-03 08:41:55 | LATCH1 rider ws7 - latch 1 at the t1 cadence 2026-09-03 08:41:55, divergence state -1 | - | 2: ws4,ws13 | last 19:39:30, 782.4 min ago / counter-side 2026-09-03 07:15:45 | 0.160610 | -0.1934 |
| 2026-09-03 08:41:55 | **CADENCE:** CADENCE rider ws7 - t1 gcws30b journey 08:40:00..08:41:50 reached 1.93 past the 5.0 fence, ws1r reversed 08:40:30 during, r 31.86 past the 44.0 fence, stamp 08:40:30, ib 15.0 cross 08:41:00 hold 6 bars, ib dwell 12 bars \| rider ws7 51.01, no-longer-exfence yes, reversed yes \| mage-cascade up | ws13: 15.84 | 2: ws4,ws13 | last 19:39:30, 782.4 min ago / counter-side 2026-09-03 07:15:45 | 0.160610 | -0.1934 |
| 2026-09-03 08:41:55 | **CADENCE:** BATON rider ws7 - ws7 -> ws13, at a t1 cadence, capped at ws15 by the jump bound 8 | ws13: 15.84 | 2: ws4,ws13 | last 19:39:30, 782.4 min ago / counter-side 2026-09-03 07:15:45 | 0.160610 | -0.1934 |
| 2026-09-03 08:56:25 | LATCH1 rider ws13 - latch 1 at the t1 cadence 2026-09-03 08:56:25, divergence state -1 | - | 7: ws1,ws3,ws4,ws5,ws12,ws13,ws14 | last 19:39:30, 796.9 min ago / counter-side 2026-09-03 07:15:45 | 0.160340 | -0.0250 |
| 2026-09-03 08:56:25 | **CADENCE:** CADENCE rider ws13 - t1 gcws30b journey 08:51:30..08:56:20 reached -4.81 past the 5.0 fence, ws1r reversed 08:55:05 during, r 16.37 past the 44.0 fence, stamp 08:55:05, ib 15.0 cross 08:55:30 hold 6 bars, ib dwell 12 bars \| rider ws13 17.59, no-longer-exfence no, reversed yes \| mage-cascade down | ws14: 23.84 | 7: ws1,ws3,ws4,ws5,ws12,ws13,ws14 | last 19:39:30, 796.9 min ago / counter-side 2026-09-03 07:15:45 | 0.160340 | -0.0250 |
| 2026-09-03 08:56:25 | **CADENCE:** BATON rider ws13 - ws13 -> ws14, at a t1 cadence, capped at ws21 by the jump bound 8 | ws14: 23.84 | 7: ws1,ws3,ws4,ws5,ws12,ws13,ws14 | last 19:39:30, 796.9 min ago / counter-side 2026-09-03 07:15:45 | 0.160340 | -0.0250 |
| 2026-09-03 09:07:25 | LATCH1 rider ws14 - latch 1 at the t1 cadence 2026-09-03 09:07:25, divergence state -1 | - | 12: ws2,ws3,ws4,ws5,ws6,ws8,ws12,ws13,ws14,ws15,ws16,ws21 | last 19:39:30, 807.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159970 | +0.2059 |
| 2026-09-03 09:07:25 | **CADENCE:** CADENCE rider ws14 - t1 gcws30b journey 09:03:30..09:07:20 reached -2.12 past the 5.0 fence, ws1r reversed 09:06:15 during, r 23.54 past the 44.0 fence, stamp 09:06:15, ib 15.0 cross 09:06:30 hold 6 bars, ib dwell 12 bars \| rider ws14 17.68, no-longer-exfence no, reversed no \| mage-cascade down | ws15: 18.63, ws16: 21.01, ws21: 18.18 | 12: ws2,ws3,ws4,ws5,ws6,ws8,ws12,ws13,ws14,ws15,ws16,ws21 | last 19:39:30, 807.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159970 | +0.2059 |
| 2026-09-03 09:07:25 | **CADENCE:** BATON rider ws14 - ws14 -> ws21, at a t1 cadence, capped at ws22 by the jump bound 8 | ws15: 18.63, ws16: 21.01, ws21: 18.18 | 12: ws2,ws3,ws4,ws5,ws6,ws8,ws12,ws13,ws14,ws15,ws16,ws21 | last 19:39:30, 807.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159970 | +0.2059 |
| 2026-09-03 09:32:25 | LATCH1 rider ws21 - latch 1 at the t1 cadence 2026-09-03 09:32:25, divergence state -1 | - | 11: ws2,ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws19,ws21 | last 19:39:30, 832.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159790 | +0.3182 |
| 2026-09-03 09:32:25 | **CADENCE:** CADENCE rider ws21 - t1 gcws30b journey 09:30:00..09:32:20 reached -0.18 past the 5.0 fence, ws1r reversed 09:31:05 during, r 42.20 past the 44.0 fence, stamp 09:31:05, ib 15.0 cross 09:31:30 hold 6 bars, ib dwell 12 bars \| rider ws21 14.43, no-longer-exfence no, reversed yes \| mage-cascade down | none offered | 11: ws2,ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws19,ws21 | last 19:39:30, 832.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159790 | +0.3182 |
| 2026-09-03 09:32:25 | HOLD rider ws21 - rider ws21 14.43 oob - no action | - | 11: ws2,ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws19,ws21 | last 19:39:30, 832.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159790 | +0.3182 |
| 2026-09-03 09:33:50 | NO PASS rider ws21 - ws21 17.87 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 11: ws2,ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws19,ws21 | last 19:39:30, 834.3 min ago / counter-side 2026-09-03 07:15:45 | 0.160170 | +0.0811 |
| 2026-09-03 09:42:35 | the favourable extreme - MFE 0.6238 | - | 13: ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21 | last 19:39:30, 843.1 min ago / counter-side 2026-09-03 07:15:45 | 0.159300 | +0.6238 |
| 2026-09-03 09:44:25 | LATCH1 rider ws21 - latch 1 at the t1 cadence 2026-09-03 09:44:25, divergence state -1 | - | 13: ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21 | last 19:39:30, 844.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159930 | +0.2308 |
| 2026-09-03 09:44:25 | **CADENCE:** CADENCE rider ws21 - t1 gcws30b journey 09:41:30..09:44:20 reached -18.45 past the 5.0 fence, ws1r reversed 09:43:15 during, r 34.84 past the 44.0 fence, stamp 09:43:15, ib 15.0 cross 09:43:30 hold 6 bars, ib dwell 12 bars \| rider ws21 15.53, no-longer-exfence no, reversed yes \| mage-cascade up | none offered | 13: ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21 | last 19:39:30, 844.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159930 | +0.2308 |
| 2026-09-03 09:44:25 | **CADENCE:** EXHAUST rider ws21 - t4 at a t1 cadence - rider ws21 15.53, no candidate at or below ws29 (the jump bound 8) | - | 13: ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21 | last 19:39:30, 844.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159930 | +0.2308 |
| 2026-09-03 09:44:25 | THIS LEG CLOSES on t1, realised +0.1934, drag 0.1975, net -0.0041 | - | 13: ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21 | last 19:39:30, 844.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159930 | +0.2308 |

## 2026-09-03 leg 5 - LONG   opens 2026-09-03 09:44:30   exits 2026-09-03 10:25:55 on STOP at 1.10%   held 41.4 min   MAE 1.1000   MFE 0.1500   realised -1.1000   net -1.2975

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-09-03 09:44:30 | >>> THIS LEG OPENS LONG | - | none | last 07:15:45, 148.8 min ago | 0.159990 | +0.0000 |
| 2026-09-03 09:45:30 | the favourable extreme - MFE 0.1500 | - | none | last 07:15:45, 149.8 min ago | 0.160230 | +0.1500 |
| 2026-09-03 10:25:55 | the ADVERSE extreme - MAE 1.1313 | - | none | last 07:15:45, 190.2 min ago | 0.158180 | -1.1313 |
| 2026-09-03 10:25:55 | THIS LEG CLOSES on STOP at 1.10%, realised -1.1000, drag 0.1975, net -1.2975 | - | none | last 07:15:45, 190.2 min ago | 0.158210 | -1.1126 |
| 2026-09-03 10:53:00 | ARM - gcws30b+(ws1r\|ws2r): gcws30b 124.66 at or beyond the 5.0/95.0 fence, held 6 bars, + ws1r oob (ws1r 93.81, ws2r 59.71) | - | 1: ws1 | last 07:15:45, 217.2 min ago | 0.159440 | -0.3438 |
| 2026-09-03 10:53:00 | RETEST - ws1r 93.81 oob + ws2r 59.71 / ws3r 59.22 in - the gate opens; ws1r oob->ib cross 2026-09-03 10:58:50, wob 12, cadence at 2026-09-03 10:59:45 | - | 1: ws1 | last 07:15:45, 217.2 min ago | 0.159440 | -0.3438 |
| 2026-09-03 10:53:05 | NO RIDER - the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs | - | 1: ws1 | last 07:15:45, 217.3 min ago | 0.159430 | -0.3500 |
| 2026-09-03 10:59:45 | **CADENCE:** RIDER rider ws4 - v4-arm-lineage-retest: the re-scan rides ws4 LATCHED, r 84.97 - the highest latched rung | - | 3: ws1,ws2,ws4 | last 07:15:45, 224.0 min ago | 0.159980 | -0.0063 |
| 2026-09-03 11:01:25 | LATCH1 rider ws4 - latch 1 at the t1 cadence 2026-09-03 11:01:25, divergence state +1 | - | 4: ws2,ws3,ws4,ws5 | last 07:15:45, 225.7 min ago | 0.159700 | -0.1813 |
| 2026-09-03 11:01:25 | **CADENCE:** CADENCE rider ws4 - t1 gcws30b journey 10:52:00..11:01:20 reached 124.66 past the 95.0 fence, ws1r reversed 11:00:20 during, r 82.18 past the 56.0 fence, stamp 11:00:20, ib 85.0 cross 11:00:30 hold 6 bars, ib dwell 12 bars \| rider ws4 89.58, no-longer-exfence no, reversed no \| mage-cascade down | ws5: 81.40 | 4: ws2,ws3,ws4,ws5 | last 07:15:45, 225.7 min ago | 0.159700 | -0.1813 |
| 2026-09-03 11:01:25 | **CADENCE:** BATON rider ws4 - ws4 -> ws5, at a t1 cadence, capped at ws12 by the jump bound 8 | ws5: 81.40 | 4: ws2,ws3,ws4,ws5 | last 07:15:45, 225.7 min ago | 0.159700 | -0.1813 |
| 2026-09-03 11:11:50 | NO PASS rider ws5 - ws5 84.40 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 3: ws3,ws4,ws5 | last 07:15:45, 236.1 min ago | 0.159720 | -0.1688 |
| 2026-09-03 11:22:25 | LATCH1 rider ws5 - latch 1 at the t1 cadence 2026-09-03 11:22:25, divergence state +1 | - | 4: ws1,ws5,ws6,ws7 | last 07:15:45, 246.7 min ago | 0.159780 | -0.1313 |
| 2026-09-03 11:22:25 | **CADENCE:** CADENCE rider ws5 - t1 gcws30b journey 11:18:30..11:22:20 reached 107.67 past the 95.0 fence, ws1r reversed 11:21:30 during, r 74.01 past the 56.0 fence, stamp 11:21:30, ib 85.0 cross 11:21:30 hold 6 bars, ib dwell 12 bars \| rider ws5 68.55, no-longer-exfence no, reversed yes \| mage-cascade neither | ws6: 88.54, ws7: 90.63 | 4: ws1,ws5,ws6,ws7 | last 07:15:45, 246.7 min ago | 0.159780 | -0.1313 |
| 2026-09-03 11:22:25 | **CADENCE:** BATON rider ws5 - ws5 -> ws7, at a t1 cadence, capped at ws13 by the jump bound 8 | ws6: 88.54, ws7: 90.63 | 4: ws1,ws5,ws6,ws7 | last 07:15:45, 246.7 min ago | 0.159780 | -0.1313 |
| 2026-09-03 11:35:55 | LATCH1 rider ws7 - latch 1 at the t1 cadence 2026-09-03 11:35:55, divergence state +1 | - | 6: ws1,ws6,ws7,ws8,ws9,ws10 | last 07:15:45, 260.2 min ago | 0.160700 | +0.4438 |
| 2026-09-03 11:35:55 | **CADENCE:** CADENCE rider ws7 - t1 gcws30b journey 11:26:30..11:35:50 reached 112.73 past the 95.0 fence, ws1r reversed 11:34:45 during, r 89.48 past the 56.0 fence, stamp 11:34:45, ib 85.0 cross 11:35:00 hold 6 bars, ib dwell 12 bars \| rider ws7 95.09, no-longer-exfence no, reversed yes \| mage-cascade down | ws8: 89.60, ws9: 86.38, ws10: 86.87 | 6: ws1,ws6,ws7,ws8,ws9,ws10 | last 07:15:45, 260.2 min ago | 0.160700 | +0.4438 |
| 2026-09-03 11:35:55 | **CADENCE:** BATON rider ws7 - ws7 -> ws10, at a t1 cadence, capped at ws15 by the jump bound 8 | ws8: 89.60, ws9: 86.38, ws10: 86.87 | 6: ws1,ws6,ws7,ws8,ws9,ws10 | last 07:15:45, 260.2 min ago | 0.160700 | +0.4438 |
| 2026-09-03 12:00:55 | BATON rider ws10 - ws10 -> ws12, between cadences, lin_hop 2 | ws11: 87.68, ws12: 87.21 | 8: ws5,ws7,ws8,ws9,ws10,ws11,ws12,ws13 | last 07:15:45, 285.2 min ago | 0.160620 | +0.3938 |
| 2026-09-03 12:12:55 | BATON rider ws12 - ws12 -> ws14, between cadences, lin_hop 2 | ws13: 95.44, ws14: 93.89 | 7: ws1,ws8,ws10,ws11,ws12,ws13,ws14 | last 07:15:45, 297.2 min ago | 0.161550 | +0.9751 |
| 2026-09-03 12:35:55 | LATCH1 rider ws14 - latch 1 at the t1 cadence 2026-09-03 12:35:55, divergence state +1 | - | 8: ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws17 | last 07:15:45, 320.2 min ago | 0.161860 | +1.1688 |
| 2026-09-03 12:35:55 | **CADENCE:** CADENCE rider ws14 - t1 gcws30b journey 12:32:00..12:35:50 reached 126.71 past the 95.0 fence, ws1r reversed 12:35:45 during, r 63.52 past the 56.0 fence, stamp 12:35:45, ib 85.0 cross 12:35:00 hold 6 bars, ib dwell 12 bars \| rider ws14 90.17, no-longer-exfence no, reversed yes \| mage-cascade down | ws15: 87.12, ws16: 91.57, ws17: 95.75 | 8: ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws17 | last 07:15:45, 320.2 min ago | 0.161860 | +1.1688 |
| 2026-09-03 12:35:55 | **CADENCE:** BATON rider ws14 - ws14 -> ws17, at a t1 cadence, capped at ws22 by the jump bound 8 | ws15: 87.12, ws16: 91.57, ws17: 95.75 | 8: ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws17 | last 07:15:45, 320.2 min ago | 0.161860 | +1.1688 |
| 2026-09-03 13:00:25 | LATCH1 rider ws17 - latch 1 at the t1 cadence 2026-09-03 13:00:25, divergence state +1 | - | 14: ws1,ws2,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21,ws22 | last 07:15:45, 344.7 min ago | 0.162770 | +1.7376 |
| 2026-09-03 13:00:25 | **CADENCE:** CADENCE rider ws17 - t1 gcws30b journey 12:52:30..13:00:20 reached 103.19 past the 95.0 fence, ws1r reversed 12:58:55 during, r 97.31 past the 56.0 fence, stamp 12:58:55, ib 85.0 cross 12:59:30 hold 6 bars, ib dwell 12 bars \| rider ws17 95.11, no-longer-exfence no, reversed yes \| mage-cascade down | ws18: 86.09, ws19: 89.11, ws20: 91.93, ws21: 95.84, ws22: 96.99 | 14: ws1,ws2,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21,ws22 | last 07:15:45, 344.7 min ago | 0.162770 | +1.7376 |
| 2026-09-03 13:00:25 | **CADENCE:** BATON rider ws17 - ws17 -> ws22, at a t1 cadence, capped at ws25 by the jump bound 8 | ws18: 86.09, ws19: 89.11, ws20: 91.93, ws21: 95.84, ws22: 96.99 | 14: ws1,ws2,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21,ws22 | last 07:15:45, 344.7 min ago | 0.162770 | +1.7376 |
| 2026-09-03 13:30:55 | **CADENCE:** CADENCE rider ws22 - t1 gcws30b journey 13:26:30..13:30:50 reached 103.43 past the 95.0 fence, ws1r reversed 13:28:00 during, r 100.00 past the 56.0 fence, stamp 13:28:00, ib 85.0 cross 13:30:00 hold 6 bars, ib dwell 12 bars \| rider ws22 97.72, no-longer-exfence no, reversed yes \| mage-cascade down | ws23: 99.92, ws24: 93.45, ws26: 91.06, ws27: 90.00 | 17: ws1,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21,ws22,ws23,ws24,ws26,ws27 | last 07:15:45, 375.2 min ago | 0.163460 | +2.1689 |
| 2026-09-03 13:30:55 | **CADENCE:** BATON rider ws22 - ws22 -> ws27, at a t1 cadence, capped at ws30 by the jump bound 8 | ws23: 99.92, ws24: 93.45, ws26: 91.06, ws27: 90.00 | 17: ws1,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21,ws22,ws23,ws24,ws26,ws27 | last 07:15:45, 375.2 min ago | 0.163460 | +2.1689 |
| 2026-09-03 14:03:40 | BATON rider ws27 - ws27 -> ws29, between cadences, lin_hop 2 | ws28: 80.29, ws29: 74.00 | 12: ws13,ws16,ws18,ws22,ws23,ws24,ws25,ws26,ws27,ws28,ws29,ws30 | last 13:53:05, 10.6 min ago | 0.161590 | +1.0001 |
| 2026-09-03 14:03:55 | BATON rider ws29 - ws29 -> ws30, between cadences, lin_hop 2 | ws30: 74.17 | 12: ws13,ws16,ws18,ws22,ws23,ws24,ws25,ws26,ws27,ws28,ws29,ws30 | last 13:53:05, 10.8 min ago | 0.161750 | +1.1001 |
| 2026-09-03 14:35:05 | NO PASS rider ws30 - ws30 81.80 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 12: ws2,ws3,ws4,ws18,ws22,ws23,ws24,ws26,ws27,ws28,ws29,ws30 | last 13:53:05, 42.0 min ago | 0.164000 | +2.5064 |
| 2026-09-03 15:02:25 | LATCH1 rider ws30 - latch 1 at the t1 cadence 2026-09-03 15:02:25, divergence state +1 | - | 11: ws5,ws6,ws7,ws22,ws23,ws24,ws26,ws27,ws28,ws29,ws30 | last 13:53:05, 69.3 min ago | 0.169390 | +5.8754 |
| 2026-09-03 15:02:25 | **CADENCE:** CADENCE rider ws30 - t1 gcws30b journey 14:47:00..15:02:20 reached 141.72 past the 95.0 fence, ws1r reversed 15:00:20 during, r 68.48 past the 56.0 fence, stamp 15:00:20, ib 85.0 cross 15:01:30 hold 6 bars, ib dwell 12 bars \| rider ws30 92.48, no-longer-exfence no, reversed yes \| mage-cascade up | none offered | 11: ws5,ws6,ws7,ws22,ws23,ws24,ws26,ws27,ws28,ws29,ws30 | last 13:53:05, 69.3 min ago | 0.169390 | +5.8754 |
| 2026-09-03 15:02:25 | HOLD rider ws30 - rider ws30 92.48 oob - no action | - | 11: ws5,ws6,ws7,ws22,ws23,ws24,ws26,ws27,ws28,ws29,ws30 | last 13:53:05, 69.3 min ago | 0.169390 | +5.8754 |
| 2026-09-03 15:12:05 | NO PASS rider ws30 - ws30 84.27 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 11: ws7,ws8,ws9,ws22,ws23,ws24,ws26,ws27,ws28,ws29,ws30 | last 13:53:05, 79.0 min ago | 0.167340 | +4.5940 |
| 2026-09-03 15:39:55 | LATCH1 rider ws30 - latch 1 at the t1 cadence 2026-09-03 15:39:55, divergence state +1 | - | 9: ws1,ws2,ws23,ws24,ws26,ws27,ws28,ws29,ws30 | last 13:53:05, 106.8 min ago | 0.169670 | +6.0504 |
| 2026-09-03 15:39:55 | **CADENCE:** CADENCE rider ws30 - t1 gcws30b journey 15:31:30..15:39:50 reached 106.04 past the 95.0 fence, ws1r reversed 15:37:00 during, r 100.00 past the 56.0 fence, stamp 15:37:00, ib 85.0 cross 15:39:00 hold 6 bars, ib dwell 12 bars \| rider ws30 80.19, no-longer-exfence no, reversed yes \| mage-cascade down | none offered | 9: ws1,ws2,ws23,ws24,ws26,ws27,ws28,ws29,ws30 | last 13:53:05, 106.8 min ago | 0.169670 | +6.0504 |
| 2026-09-03 15:39:55 | **CADENCE:** TOP RESET EMPTY rider ws30 - ws30 80.19 is the ladder top and exhausted - the rider reset to 0 found no candidate at or below ws8 | none offered | 9: ws1,ws2,ws23,ws24,ws26,ws27,ws28,ws29,ws30 | last 13:53:05, 106.8 min ago | 0.169670 | +6.0504 |
| 2026-09-03 15:39:55 | **CADENCE:** EXHAUST rider ws30 - t4 at a t1 cadence - rider ws30 80.19, no candidate at or below ws38 (the jump bound 8) | - | 9: ws1,ws2,ws23,ws24,ws26,ws27,ws28,ws29,ws30 | last 13:53:05, 106.8 min ago | 0.169670 | +6.0504 |

## 2026-09-03 leg 6 - THE CHAIN HAS NO SUCH LEG. 2026-09-03 carries 5 legs.

## 2026-09-03 leg 7 - THE CHAIN HAS NO SUCH LEG. 2026-09-03 carries 5 legs.

## 2026-09-03 leg 8 - THE CHAIN HAS NO SUCH LEG. 2026-09-03 carries 5 legs.

| the read | value |
|---|---|
| legs in the chain over the window | 5 |
| legs opening on 2026-09-03 | 5 |
| seconds to compute | 56.7 |
