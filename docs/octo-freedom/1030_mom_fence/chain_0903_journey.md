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
| 2026-09-03 | 2 | 2 | 2026-09-03 02:37:30 | SHORT | 2026-09-03 06:34:10 | STOP at 1.10% | 236.7 | ws4 > ws5 > ws7 > ws8 > ws12 > ws14 > ws15 > ws17 | 1.1000 | +1.2767 | -1.1000 | 0.1975 | -1.2975 |
| TOTAL | | 2 scored legs | | | | | 357.1 | | 1.2735 | +3.8214 | +1.0720 | 0.3950 | +0.6770 |

## 2026-09-03 leg 1 - LONG   opens 2026-09-03 00:37:00   exits 2026-09-03 02:37:25 on t1   held 120.4 min   MAE 0.1735   MFE 2.5447   realised +2.1720   net +1.9745

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-09-03 00:37:00 | >>> THIS LEG OPENS LONG | - | 3: ws13,ws24,ws28 | last 15:45:35, 531.4 min ago / counter-side 2026-09-02 19:39:30 | 0.155620 | +0.0000 |
| 2026-09-03 01:01:30 | the ADVERSE extreme - MAE 0.1735 | - | 1: ws3 | last 15:45:35, 555.9 min ago / counter-side 2026-09-02 19:39:30 | 0.155350 | -0.1735 |
| 2026-09-03 01:08:30 | ARM - ws4r: ws4r 85.04 oob | - | 1: ws4 | last 15:45:35, 562.9 min ago / counter-side 2026-09-02 19:39:30 | 0.157460 | +1.1824 |
| 2026-09-03 01:08:30 | RETEST - ws1r 81.14 is not oob at the arm - the gate stays shut | - | 1: ws4 | last 15:45:35, 562.9 min ago / counter-side 2026-09-02 19:39:30 | 0.157460 | +1.1824 |
| 2026-09-03 01:08:35 | NO RIDER - the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs | - | 1: ws4 | last 15:45:35, 563.0 min ago / counter-side 2026-09-02 19:39:30 | 0.157460 | +1.1824 |
| 2026-09-03 01:10:55 | RIDER rider ws4 - t1 gcws30b journey 01:06:30..01:09:55 reached 125.83 past the 95.0 fence, ws1r reversed 01:09:55 during, r 81.14 past the 56.0 fence, stamp 01:09:55, ib 85.0 cross 01:10:00 hold 6 bars, ib dwell 12 bars \| ws4 r 82.73 picked up at a cadence, no prior rider | - | 2: ws1,ws4 | last 15:45:35, 565.3 min ago / counter-side 2026-09-02 19:39:30 | 0.157280 | +1.0667 |
| 2026-09-03 01:36:55 | BATON rider ws4 - ws4 -> ws6, between cadences, lin_hop 2 | ws5: 89.87, ws6: 90.51 | 3: ws4,ws5,ws6 | last 15:45:35, 591.3 min ago / counter-side 2026-09-02 19:39:30 | 0.157930 | +1.4844 |
| 2026-09-03 01:36:55 | LATCH1 rider ws6 - latch 1 at the t1 cadence 2026-09-03 01:36:55, divergence state +1 | - | 3: ws4,ws5,ws6 | last 15:45:35, 591.3 min ago / counter-side 2026-09-02 19:39:30 | 0.157930 | +1.4844 |
| 2026-09-03 01:36:55 | **CADENCE:** CADENCE rider ws6 - t1 gcws30b journey 01:33:00..01:35:55 reached 125.44 past the 95.0 fence, ws1r reversed 01:35:15 during, r 75.77 past the 56.0 fence, stamp 01:35:15, ib 85.0 cross 01:36:00 hold 6 bars, ib dwell 12 bars \| rider ws6 90.51, no-longer-exfence no, reversed no \| mage-cascade down | none offered | 3: ws4,ws5,ws6 | last 15:45:35, 591.3 min ago / counter-side 2026-09-02 19:39:30 | 0.157930 | +1.4844 |
| 2026-09-03 01:36:55 | HOLD rider ws6 - rider ws6 90.51 oob - no action | - | 3: ws4,ws5,ws6 | last 15:45:35, 591.3 min ago / counter-side 2026-09-02 19:39:30 | 0.157930 | +1.4844 |
| 2026-09-03 01:47:00 | BATON rider ws6 - ws6 -> ws7, between cadences, lin_hop 2 | ws7: 87.00 | 3: ws5,ws6,ws7 | last 15:45:35, 601.4 min ago / counter-side 2026-09-02 19:39:30 | 0.157790 | +1.3944 |
| 2026-09-03 01:48:05 | NO PASS rider ws7 - ws7 84.75 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 3: ws5,ws6,ws7 | last 15:45:35, 602.5 min ago / counter-side 2026-09-02 19:39:30 | 0.157650 | +1.3045 |
| 2026-09-03 02:35:10 | the favourable extreme - MFE 2.5447 | - | 3: ws1,ws3,ws4 | last 02:26:55, 8.2 min ago | 0.159580 | +2.5447 |
| 2026-09-03 02:37:25 | LATCH1 rider ws7 - latch 1 at the t1 cadence 2026-09-03 02:37:25, divergence state +1 | - | 2: ws3,ws4 | last 02:26:55, 10.5 min ago | 0.158940 | +2.1334 |
| 2026-09-03 02:37:25 | **CADENCE:** CADENCE rider ws7 - t1 gcws30b journey 02:33:30..02:36:25 reached 104.77 past the 95.0 fence, ws1r reversed 02:35:00 during, r 78.55 past the 56.0 fence, stamp 02:35:00, ib 85.0 cross 02:36:30 hold 6 bars, ib dwell 12 bars \| rider ws7 54.88, no-longer-exfence yes, reversed yes \| mage-cascade down | none offered | 2: ws3,ws4 | last 02:26:55, 10.5 min ago | 0.158940 | +2.1334 |
| 2026-09-03 02:37:25 | **CADENCE:** EXHAUST rider ws7 - t4 at a t1 cadence - rider ws7 54.88, no candidate at or below ws15 (the jump bound 8) | - | 2: ws3,ws4 | last 02:26:55, 10.5 min ago | 0.158940 | +2.1334 |
| 2026-09-03 02:37:25 | THIS LEG CLOSES on t1, realised +2.1720, drag 0.1975, net +1.9745 | - | 2: ws3,ws4 | last 02:26:55, 10.5 min ago | 0.158940 | +2.1334 |

## 2026-09-03 leg 2 - SHORT   opens 2026-09-03 02:37:30   exits 2026-09-03 06:34:10 on STOP at 1.10%   held 236.7 min   MAE 1.1000   MFE 1.2767   realised -1.1000   net -1.2975

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-09-03 02:37:30 | >>> THIS LEG OPENS SHORT | - | none | last 19:39:30, 418.0 min ago / counter-side 2026-09-03 02:26:55 | 0.159000 | -0.0000 |
| 2026-09-03 03:24:00 | ARM - ws4r: ws4r 8.52 oob | - | 3: ws1,ws3,ws4 | last 19:39:30, 464.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158580 | +0.2642 |
| 2026-09-03 03:24:00 | RETEST - ws1r 20.64 is not oob at the arm - the gate stays shut | - | 3: ws1,ws3,ws4 | last 19:39:30, 464.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158580 | +0.2642 |
| 2026-09-03 03:24:05 | NO RIDER - the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs | - | 3: ws1,ws3,ws4 | last 19:39:30, 464.6 min ago / counter-side 2026-09-03 03:15:55 | 0.158610 | +0.2453 |
| 2026-09-03 03:26:25 | LATCH1 - latch 1 at the t1 cadence 2026-09-03 03:26:25, divergence state -1 | - | 3: ws1,ws3,ws4 | last 19:39:30, 466.9 min ago / counter-side 2026-09-03 03:15:55 | 0.158860 | +0.0881 |
| 2026-09-03 03:26:25 | RIDER rider ws4 - t1 gcws30b journey 03:23:30..03:25:25 reached 2.23 past the 5.0 fence, ws1r reversed 03:25:25 during, r 20.64 past the 44.0 fence, stamp 03:25:25, ib 15.0 cross 03:25:30 hold 6 bars, ib dwell 12 bars \| ws4 r 11.63 picked up at a cadence, no prior rider | - | 3: ws1,ws3,ws4 | last 19:39:30, 466.9 min ago / counter-side 2026-09-03 03:15:55 | 0.158860 | +0.0881 |
| 2026-09-03 03:33:20 | BATON rider ws4 - ws4 -> ws5, between cadences, lin_hop 2 | ws5: 17.11 | 3: ws3,ws4,ws5 | last 19:39:30, 473.8 min ago / counter-side 2026-09-03 03:15:55 | 0.158780 | +0.1384 |
| 2026-09-03 03:49:00 | BATON rider ws5 - ws5 -> ws7, between cadences, lin_hop 2 | ws6: 16.07, ws7: 8.39 | 5: ws4,ws5,ws6,ws7,ws8 | last 19:39:30, 489.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158520 | +0.3019 |
| 2026-09-03 03:52:00 | BATON rider ws7 - ws7 -> ws8, between cadences, lin_hop 2 | ws8: 15.66 | 4: ws5,ws6,ws7,ws8 | last 19:39:30, 492.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158610 | +0.2453 |
| 2026-09-03 03:52:45 | NO PASS rider ws8 - ws8 17.49 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 4: ws5,ws6,ws7,ws8 | last 19:39:30, 493.2 min ago / counter-side 2026-09-03 03:15:55 | 0.158710 | +0.1824 |
| 2026-09-03 04:35:20 | the favourable extreme - MFE 1.2767 | - | 3: ws10,ws11,ws12 | last 19:39:30, 535.8 min ago / counter-side 2026-09-03 03:15:55 | 0.156970 | +1.2767 |
| 2026-09-03 04:38:55 | LATCH1 rider ws8 - latch 1 at the t1 cadence 2026-09-03 04:38:55, divergence state -1 | - | 3: ws10,ws11,ws12 | last 19:39:30, 539.4 min ago / counter-side 2026-09-03 03:15:55 | 0.157850 | +0.7233 |
| 2026-09-03 04:38:55 | **CADENCE:** CADENCE rider ws8 - t1 gcws30b journey 04:34:30..04:37:55 reached -17.54 past the 5.0 fence, ws1r reversed 04:37:45 during, r 41.21 past the 44.0 fence, stamp 04:37:45, ib 15.0 cross 04:38:00 hold 6 bars, ib dwell 12 bars \| rider ws8 38.91, no-longer-exfence yes, reversed yes \| mage-cascade down | ws10: 15.79, ws11: 23.77, ws12: 17.09 | 3: ws10,ws11,ws12 | last 19:39:30, 539.4 min ago / counter-side 2026-09-03 03:15:55 | 0.157850 | +0.7233 |
| 2026-09-03 04:38:55 | **CADENCE:** BATON rider ws8 - ws8 -> ws12, at a t1 cadence, capped at ws16 by the jump bound 8 | ws10: 15.79, ws11: 23.77, ws12: 17.09 | 3: ws10,ws11,ws12 | last 19:39:30, 539.4 min ago / counter-side 2026-09-03 03:15:55 | 0.157850 | +0.7233 |
| 2026-09-03 04:40:05 | BATON rider ws12 - ws12 -> ws14, between cadences, lin_hop 2 | ws14: 13.25 | 4: ws10,ws11,ws12,ws14 | last 19:39:30, 540.6 min ago / counter-side 2026-09-03 03:15:55 | 0.157710 | +0.8113 |
| 2026-09-03 04:45:10 | BATON rider ws14 - ws14 -> ws15, between cadences, lin_hop 2 | ws15: 6.62 | 5: ws10,ws11,ws12,ws14,ws15 | last 19:39:30, 545.7 min ago / counter-side 2026-09-03 03:15:55 | 0.158110 | +0.5597 |
| 2026-09-03 04:52:25 | BATON rider ws15 - ws15 -> ws17, between cadences, lin_hop 2 | ws16: 28.92, ws17: 27.06 | 6: ws12,ws13,ws14,ws15,ws16,ws17 | last 19:39:30, 552.9 min ago / counter-side 2026-09-03 03:15:55 | 0.159300 | -0.1887 |
| 2026-09-03 04:52:35 | NO PASS rider ws17 - ws17 27.06 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 6: ws12,ws13,ws14,ws15,ws16,ws17 | last 19:39:30, 553.1 min ago / counter-side 2026-09-03 03:15:55 | 0.159480 | -0.3019 |
| 2026-09-03 06:34:10 | the ADVERSE extreme - MAE 1.2138 | - | none | last 19:39:30, 654.7 min ago / counter-side 2026-09-03 03:15:55 | 0.160930 | -1.2138 |
| 2026-09-03 06:34:10 | THIS LEG CLOSES on STOP at 1.10%, realised -1.1000, drag 0.1975, net -1.2975 | - | none | last 19:39:30, 654.7 min ago / counter-side 2026-09-03 03:15:55 | 0.160810 | -1.1384 |
| 2026-09-03 07:33:55 | **CADENCE:** CADENCE rider ws17 - t1 gcws30b journey 07:30:30..07:32:55 reached -7.57 past the 5.0 fence, ws1r reversed 07:32:10 during, r 18.48 past the 44.0 fence, stamp 07:32:10, ib 15.0 cross 07:33:00 hold 6 bars, ib dwell 12 bars \| rider ws17 73.19, no-longer-exfence yes, reversed yes \| mage-cascade up | none offered | 4: ws2,ws3,ws6,ws7 | last 19:39:30, 714.4 min ago / counter-side 2026-09-03 07:15:45 | 0.160510 | -0.9497 |
| 2026-09-03 07:33:55 | **CADENCE:** EXHAUST rider ws17 - t4 at a t1 cadence - rider ws17 73.19, no candidate at or below ws25 (the jump bound 8) | - | 4: ws2,ws3,ws6,ws7 | last 19:39:30, 714.4 min ago / counter-side 2026-09-03 07:15:45 | 0.160510 | -0.9497 |

## 2026-09-03 leg 3 - THE CHAIN HAS NO SUCH LEG. 2026-09-03 carries 2 legs.

## 2026-09-03 leg 4 - THE CHAIN HAS NO SUCH LEG. 2026-09-03 carries 2 legs.

## 2026-09-03 leg 5 - THE CHAIN HAS NO SUCH LEG. 2026-09-03 carries 2 legs.

## 2026-09-03 leg 6 - THE CHAIN HAS NO SUCH LEG. 2026-09-03 carries 2 legs.

| the read | value |
|---|---|
| legs in the chain over the window | 2 |
| legs opening on 2026-09-03 | 2 |
| seconds to compute | 31.3 |
