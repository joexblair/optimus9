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
| 2026-09-03 | 2 | 2 | 2026-09-03 02:37:30 | SHORT | 2026-09-03 05:29:55 | t1 | 172.4 | ws4 > ws5 > ws7 > ws8 | 1.0314 | +1.2767 | +0.7233 | 0.1975 | +0.5258 |
| 2026-09-03 | 3 | 3 | 2026-09-03 05:30:00 | LONG | 2026-09-03 06:25:55 | t1 | 55.9 | ws3 > ws4 | 0.0127 | +1.7992 | +1.5521 | 0.1975 | +1.3546 |
| 2026-09-03 | 4 | 4 | 2026-09-03 06:26:00 | SHORT | 2026-09-03 09:44:25 | t1 | 198.4 | ws7 > ws13 > ws15 > ws16 > ws21 | 1.0792 | +0.6238 | +0.1934 | 0.1975 | -0.0041 |
| 2026-09-03 | 5 | 5 | 2026-09-03 09:44:30 | LONG | 2026-09-03 10:25:55 | STOP at 1.10% | 41.4 | ws4 > ws5 > ws6 > ws14 > ws16 > ws18 > ws20 > ws22 > ws24 > ws26 > ws28 > ws30 | 1.1000 | +0.1500 | -1.1000 | 0.1975 | -1.2975 |
| TOTAL | | 5 scored legs | | | | | 588.6 | | 3.3968 | +6.3944 | +3.5407 | 0.9875 | +2.5532 |

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

## 2026-09-03 leg 2 - SHORT   opens 2026-09-03 02:37:30   exits 2026-09-03 05:29:55 on t1   held 172.4 min   MAE 1.0314   MFE 1.2767   realised +0.7233   net +0.5258

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-09-03 02:37:30 | >>> THIS LEG OPENS SHORT | - | none | last 19:39:30, 418.0 min ago / counter-side 2026-09-03 02:26:55 | 0.159000 | -0.0000 |
| 2026-09-03 03:24:00 | ARM - ws4r: ws4r 8.52 oob | - | 3: ws1,ws3,ws4 | last 19:39:30, 464.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158580 | +0.2642 |
| 2026-09-03 03:24:00 | RETEST - ws1r 20.64 is not oob at the arm - the gate stays shut | - | 3: ws1,ws3,ws4 | last 19:39:30, 464.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158580 | +0.2642 |
| 2026-09-03 03:24:05 | NO RIDER - the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs | - | 3: ws1,ws3,ws4 | last 19:39:30, 464.6 min ago / counter-side 2026-09-03 03:15:55 | 0.158610 | +0.2453 |
| 2026-09-03 03:26:25 | LATCH1 - latch 1 at the t1 cadence 2026-09-03 03:26:25, divergence state -1 | - | 3: ws1,ws3,ws4 | last 19:39:30, 466.9 min ago / counter-side 2026-09-03 03:15:55 | 0.158860 | +0.0881 |
| 2026-09-03 03:26:25 | RIDER rider ws4 - t1 gcws30b journey 03:23:30..03:26:20 reached 2.23 past the 5.0 fence, ws1r reversed 03:25:25 during, r 20.64 past the 44.0 fence, stamp 03:25:25, ib 15.0 cross 03:25:30 hold 6 bars, ib dwell 12 bars \| ws4 r 11.63 picked up at a cadence, no prior rider | - | 3: ws1,ws3,ws4 | last 19:39:30, 466.9 min ago / counter-side 2026-09-03 03:15:55 | 0.158860 | +0.0881 |
| 2026-09-03 03:33:20 | BATON rider ws4 - ws4 -> ws5, between cadences, lin_hop 2 | ws5: 17.11 | 3: ws3,ws4,ws5 | last 19:39:30, 473.8 min ago / counter-side 2026-09-03 03:15:55 | 0.158780 | +0.1384 |
| 2026-09-03 03:49:00 | BATON rider ws5 - ws5 -> ws7, between cadences, lin_hop 2 | ws6: 16.07, ws7: 8.39 | 5: ws4,ws5,ws6,ws7,ws8 | last 19:39:30, 489.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158520 | +0.3019 |
| 2026-09-03 03:52:00 | BATON rider ws7 - ws7 -> ws8, between cadences, lin_hop 2 | ws8: 15.66 | 4: ws5,ws6,ws7,ws8 | last 19:39:30, 492.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158610 | +0.2453 |
| 2026-09-03 03:52:45 | NO PASS rider ws8 - ws8 17.49 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 4: ws5,ws6,ws7,ws8 | last 19:39:30, 493.2 min ago / counter-side 2026-09-03 03:15:55 | 0.158710 | +0.1824 |
| 2026-09-03 04:23:25 | **CADENCE:** HOLD rider ws8 - ws9..ws10 is lin_hop 2 reach from rider ws8 and 1 of it is ex-fence and printing towards at a t1 cadence - ws10 15.92 - the tests are concluded and the walk goes to the next cadence | - | 2: ws2,ws10 | last 19:39:30, 523.9 min ago / counter-side 2026-09-03 03:15:55 | 0.158290 | +0.4465 |
| 2026-09-03 04:35:20 | the favourable extreme - MFE 1.2767 | - | 3: ws10,ws11,ws12 | last 19:39:30, 535.8 min ago / counter-side 2026-09-03 03:15:55 | 0.156970 | +1.2767 |
| 2026-09-03 04:38:55 | LATCH1 rider ws8 - latch 1 at the t1 cadence 2026-09-03 04:38:55, divergence state -1 | - | 3: ws10,ws11,ws12 | last 19:39:30, 539.4 min ago / counter-side 2026-09-03 03:15:55 | 0.157850 | +0.7233 |
| 2026-09-03 04:38:55 | **CADENCE:** HOLD rider ws8 - ws9..ws10 is lin_hop 2 reach from rider ws8 and 1 of it is ex-fence and printing towards at a t1 cadence - ws10 15.79 - the tests are concluded and the walk goes to the next cadence | - | 3: ws10,ws11,ws12 | last 19:39:30, 539.4 min ago / counter-side 2026-09-03 03:15:55 | 0.157850 | +0.7233 |
| 2026-09-03 05:01:30 | the ADVERSE extreme - MAE 1.0314 | - | 3: ws15,ws16,ws17 | last 19:39:30, 562.0 min ago / counter-side 2026-09-03 03:15:55 | 0.160640 | -1.0314 |
| 2026-09-03 05:29:55 | LATCH1 rider ws8 - latch 1 at the t1 cadence 2026-09-03 05:29:55, divergence state -1 | - | 4: ws2,ws3,ws18,ws19 | last 19:39:30, 590.4 min ago / counter-side 2026-09-03 03:15:55 | 0.157870 | +0.7107 |
| 2026-09-03 05:29:55 | **CADENCE:** CADENCE rider ws8 - t1 gcws30b journey 05:17:30..05:29:50 reached -4.51 past the 5.0 fence, ws1r reversed 05:24:15 during, r 0.50 past the 44.0 fence, stamp 05:24:15, ib 15.0 cross 05:29:00 hold 6 bars, ib dwell 12 bars \| rider ws8 57.07, no-longer-exfence yes, reversed yes \| mage-cascade down | none offered | 4: ws2,ws3,ws18,ws19 | last 19:39:30, 590.4 min ago / counter-side 2026-09-03 03:15:55 | 0.157870 | +0.7107 |
| 2026-09-03 05:29:55 | **CADENCE:** EXHAUST rider ws8 - t4 at a t1 cadence - rider ws8 57.07, no candidate at or below ws16 (the jump bound 8) | - | 4: ws2,ws3,ws18,ws19 | last 19:39:30, 590.4 min ago / counter-side 2026-09-03 03:15:55 | 0.157870 | +0.7107 |
| 2026-09-03 05:29:55 | THIS LEG CLOSES on t1, realised +0.7233, drag 0.1975, net +0.5258 | - | 4: ws2,ws3,ws18,ws19 | last 19:39:30, 590.4 min ago / counter-side 2026-09-03 03:15:55 | 0.157870 | +0.7107 |

## 2026-09-03 leg 3 - LONG   opens 2026-09-03 05:30:00   exits 2026-09-03 06:25:55 on t1   held 55.9 min   MAE 0.0127   MFE 1.7992   realised +1.5521   net +1.3546

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-09-03 05:30:00 | >>> THIS LEG OPENS LONG | - | none | last 03:15:55, 134.1 min ago | 0.157850 | +0.0000 |
| 2026-09-03 05:30:00 | the ADVERSE extreme - MAE 0.0127 | - | none | last 03:15:55, 134.1 min ago | 0.157830 | -0.0127 |
| 2026-09-03 05:52:00 | ARM - ws4r: ws4r 87.74 oob | - | 2: ws2,ws3 | last 03:15:55, 156.1 min ago | 0.160360 | +1.5901 |
| 2026-09-03 05:52:00 | RETEST - ws1r 81.09 is not oob at the arm - the gate stays shut | - | 2: ws2,ws3 | last 03:15:55, 156.1 min ago | 0.160360 | +1.5901 |
| 2026-09-03 05:52:05 | NO RIDER - the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs | - | 2: ws2,ws3 | last 03:15:55, 156.2 min ago | 0.160340 | +1.5774 |
| 2026-09-03 05:54:25 | LATCH1 - latch 1 at the t1 cadence 2026-09-03 05:54:25, divergence state +1 | - | 2: ws1,ws3 | last 03:15:55, 158.5 min ago | 0.160250 | +1.5204 |
| 2026-09-03 05:54:25 | RIDER rider ws3 - t1 gcws30b journey 05:50:00..05:54:20 reached 97.04 past the 95.0 fence, ws1r reversed 05:54:00 during, r 87.12 past the 56.0 fence, stamp 05:54:00, ib 85.0 cross 05:53:30 hold 6 bars, ib dwell 12 bars \| ws3 r 96.36 picked up at a cadence, no prior rider | - | 2: ws1,ws3 | last 03:15:55, 158.5 min ago | 0.160250 | +1.5204 |
| 2026-09-03 05:59:20 | the favourable extreme - MFE 1.7992 | - | 2: ws3,ws4 | last 03:15:55, 163.4 min ago | 0.160690 | +1.7992 |
| 2026-09-03 06:03:50 | BATON rider ws3 - ws3 -> ws4, between cadences, lin_hop 2 | ws4: 87.86 | 2: ws3,ws4 | last 03:15:55, 167.9 min ago | 0.160120 | +1.4381 |
| 2026-09-03 06:04:55 | NO PASS rider ws4 - ws4 75.07 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 2: ws3,ws4 | last 03:15:55, 169.0 min ago | 0.159990 | +1.3557 |
| 2026-09-03 06:25:55 | LATCH1 rider ws4 - latch 1 at the t1 cadence 2026-09-03 06:25:55, divergence state +1 | - | 1: ws14 | last 03:15:55, 190.0 min ago | 0.160290 | +1.5458 |
| 2026-09-03 06:25:55 | **CADENCE:** CADENCE rider ws4 - t1 gcws30b journey 06:24:00..06:25:50 reached 95.90 past the 95.0 fence, ws1r reversed 06:24:35 during, r 56.94 past the 56.0 fence, stamp 06:24:35, ib 85.0 cross 06:25:00 hold 6 bars, ib dwell 12 bars \| rider ws4 35.84, no-longer-exfence yes, reversed yes \| mage-cascade down | none offered | 1: ws14 | last 03:15:55, 190.0 min ago | 0.160290 | +1.5458 |
| 2026-09-03 06:25:55 | **CADENCE:** EXHAUST rider ws4 - t4 at a t1 cadence - rider ws4 35.84, no candidate at or below ws12 (the jump bound 8) | - | 1: ws14 | last 03:15:55, 190.0 min ago | 0.160290 | +1.5458 |
| 2026-09-03 06:25:55 | THIS LEG CLOSES on t1, realised +1.5521, drag 0.1975, net +1.3546 | - | 1: ws14 | last 03:15:55, 190.0 min ago | 0.160290 | +1.5458 |

## 2026-09-03 leg 4 - SHORT   opens 2026-09-03 06:26:00   exits 2026-09-03 09:44:25 on t1   held 198.4 min   MAE 1.0792   MFE 0.6238   realised +0.1934   net -0.0041

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-09-03 06:26:00 | >>> THIS LEG OPENS SHORT | - | 1: ws3 | last 19:39:30, 646.5 min ago / counter-side 2026-09-03 03:15:55 | 0.160300 | -0.0000 |
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
| 2026-09-03 08:56:25 | **CADENCE:** HOLD rider ws13 - ws14..ws15 is lin_hop 2 reach from rider ws13 and 1 of it is ex-fence and printing towards at a t1 cadence - ws14 23.84 - the tests are concluded and the walk goes to the next cadence | - | 7: ws1,ws3,ws4,ws5,ws12,ws13,ws14 | last 19:39:30, 796.9 min ago / counter-side 2026-09-03 07:15:45 | 0.160340 | -0.0250 |
| 2026-09-03 09:07:10 | BATON rider ws13 - ws13 -> ws15, between cadences, lin_hop 2 | ws14: 18.26, ws15: 18.63 | 12: ws2,ws3,ws4,ws5,ws6,ws8,ws12,ws13,ws14,ws15,ws16,ws21 | last 19:39:30, 807.7 min ago / counter-side 2026-09-03 07:15:45 | 0.160030 | +0.1684 |
| 2026-09-03 09:07:25 | LATCH1 rider ws15 - latch 1 at the t1 cadence 2026-09-03 09:07:25, divergence state -1 | - | 12: ws2,ws3,ws4,ws5,ws6,ws8,ws12,ws13,ws14,ws15,ws16,ws21 | last 19:39:30, 807.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159970 | +0.2059 |
| 2026-09-03 09:07:25 | **CADENCE:** HOLD rider ws15 - ws16..ws17 is lin_hop 2 reach from rider ws15 and 1 of it is ex-fence and printing towards at a t1 cadence - ws16 21.01 - the tests are concluded and the walk goes to the next cadence | - | 12: ws2,ws3,ws4,ws5,ws6,ws8,ws12,ws13,ws14,ws15,ws16,ws21 | last 19:39:30, 807.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159970 | +0.2059 |
| 2026-09-03 09:16:40 | BATON rider ws15 - ws15 -> ws16, between cadences, lin_hop 2 | ws16: 28.68 | 7: ws6,ws12,ws13,ws14,ws15,ws16,ws21 | last 19:39:30, 817.2 min ago / counter-side 2026-09-03 07:15:45 | 0.160810 | -0.3182 |
| 2026-09-03 09:32:25 | LATCH1 rider ws16 - latch 1 at the t1 cadence 2026-09-03 09:32:25, divergence state -1 | - | 11: ws2,ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws19,ws21 | last 19:39:30, 832.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159790 | +0.3182 |
| 2026-09-03 09:32:25 | **CADENCE:** CADENCE rider ws16 - t1 gcws30b journey 09:30:00..09:32:20 reached -0.18 past the 5.0 fence, ws1r reversed 09:31:05 during, r 42.20 past the 44.0 fence, stamp 09:31:05, ib 15.0 cross 09:31:30 hold 6 bars, ib dwell 12 bars \| rider ws16 12.84, no-longer-exfence no, reversed no \| mage-cascade down | ws19: 16.52, ws21: 14.43 | 11: ws2,ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws19,ws21 | last 19:39:30, 832.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159790 | +0.3182 |
| 2026-09-03 09:32:25 | **CADENCE:** BATON rider ws16 - ws16 -> ws21, at a t1 cadence, capped at ws24 by the jump bound 8 | ws19: 16.52, ws21: 14.43 | 11: ws2,ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws19,ws21 | last 19:39:30, 832.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159790 | +0.3182 |
| 2026-09-03 09:33:50 | NO PASS rider ws21 - ws21 17.87 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 11: ws2,ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws19,ws21 | last 19:39:30, 834.3 min ago / counter-side 2026-09-03 07:15:45 | 0.160170 | +0.0811 |
| 2026-09-03 09:42:35 | the favourable extreme - MFE 0.6238 | - | 13: ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21 | last 19:39:30, 843.1 min ago / counter-side 2026-09-03 07:15:45 | 0.159300 | +0.6238 |
| 2026-09-03 09:44:25 | LATCH1 rider ws21 - latch 1 at the t1 cadence 2026-09-03 09:44:25, divergence state -1 | - | 13: ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21 | last 19:39:30, 844.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159930 | +0.2308 |
| 2026-09-03 09:44:25 | **CADENCE:** CADENCE rider ws21 - t1 gcws30b journey 09:41:30..09:44:20 reached -18.45 past the 5.0 fence, ws1r reversed 09:43:15 during, r 34.84 past the 44.0 fence, stamp 09:43:15, ib 15.0 cross 09:43:30 hold 6 bars, ib dwell 12 bars \| rider ws21 15.53, no-longer-exfence no, reversed yes \| mage-cascade up | none offered | 13: ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21 | last 19:39:30, 844.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159930 | +0.2308 |
| 2026-09-03 09:44:25 | **CADENCE:** EXHAUST rider ws21 - t4 at a t1 cadence - rider ws21 15.53, no candidate at or below ws29 (the jump bound 8) | - | 13: ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21 | last 19:39:30, 844.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159930 | +0.2308 |
| 2026-09-03 09:44:25 | THIS LEG CLOSES on t1, realised +0.1934, drag 0.1975, net -0.0041 | - | 13: ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21 | last 19:39:30, 844.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159930 | +0.2308 |

| the read | value |
|---|---|
| legs in the chain over the window | 5 |
| legs opening on 2026-09-03 | 5 |
| seconds to compute | 54.5 |
