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
| 2026-09-03 | 1 | 1 | 2026-09-03 00:37:00 | LONG | 2026-09-03 02:37:25 | t1 | 120.4 | ws6 > ws7 | 0.1735 | +2.5447 | +2.1720 | 0.1975 | +1.9745 |
| 2026-09-03 | 2 | 2 | 2026-09-03 02:37:30 | SHORT | 2026-09-03 04:39:00 | t1 | 121.5 | ws10 > ws12 | 0.5094 | +1.2767 | +0.8365 | 0.1975 | +0.6390 |
| 2026-09-03 | 3 | 3 | 2026-09-03 04:39:05 | LONG | 2026-09-03 05:55:00 | t1 | 75.9 | ws3 > ws5 | 0.2537 | +1.8837 | +1.5983 | 0.1975 | +1.4008 |
| 2026-09-03 | 4 | 4 | 2026-09-03 05:55:05 | SHORT | 2026-09-03 08:07:35 | STOP at 1.10% | 132.5 | ws7 > ws13 > ws15 > ws16 > ws18 > ws20 > ws22 > ws24 > ws26 > ws28 > ws29 | 1.1000 | +0.3309 | -1.1000 | 0.1975 | -1.2975 |
| TOTAL | | 4 scored legs | | | | | 450.3 | | 2.0366 | +6.0359 | +3.5067 | 0.7900 | +2.7167 |

## 2026-09-03 leg 1 - LONG   opens 2026-09-03 00:37:00   exits 2026-09-03 02:37:25 on t1   held 120.4 min   MAE 0.1735   MFE 2.5447   realised +2.1720   net +1.9745

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-09-03 00:37:00 | >>> THIS LEG OPENS LONG | - | 3: ws13,ws24,ws28 | last 15:45:35, 531.4 min ago / counter-side 2026-09-02 19:39:30 | 0.155620 | +0.0000 |
| 2026-09-03 01:01:30 | the ADVERSE extreme - MAE 0.1735 | - | 1: ws3 | last 15:45:35, 555.9 min ago / counter-side 2026-09-02 19:39:30 | 0.155350 | -0.1735 |
| 2026-09-03 01:08:30 | ARM - ws4r: ws4r 85.04 oob | - | 1: ws4 | last 15:45:35, 562.9 min ago / counter-side 2026-09-02 19:39:30 | 0.157460 | +1.1824 |
| 2026-09-03 01:08:30 | RETEST - ws1r 81.14 is not oob at the arm - the gate stays shut | - | 1: ws4 | last 15:45:35, 562.9 min ago / counter-side 2026-09-02 19:39:30 | 0.157460 | +1.1824 |
| 2026-09-03 01:08:35 | NO RIDER - the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs | - | 1: ws4 | last 15:45:35, 563.0 min ago / counter-side 2026-09-02 19:39:30 | 0.157460 | +1.1824 |
| 2026-09-03 01:36:55 | LATCH1 - latch 1 at the t1 cadence 2026-09-03 01:36:55, divergence state +1 | - | 3: ws4,ws5,ws6 | last 15:45:35, 591.3 min ago / counter-side 2026-09-02 19:39:30 | 0.157930 | +1.4844 |
| 2026-09-03 01:36:55 | RIDER rider ws6 - t1 gcws30b journey 01:32:00..01:36:50 reached 125.44 past the 95.0 fence, ws1r reversed 01:36:00 during, r 69.64 past the 56.0 fence, stamp 01:36:00, ib 85.0 cross 01:36:00 hold 6 bars, ib dwell 12 bars \| ws6 r 90.51 picked up at a cadence, no prior rider | - | 3: ws4,ws5,ws6 | last 15:45:35, 591.3 min ago / counter-side 2026-09-02 19:39:30 | 0.157930 | +1.4844 |
| 2026-09-03 01:47:00 | BATON rider ws6 - ws6 -> ws7, between cadences, lin_hop 2 | ws7: 87.00 | 3: ws5,ws6,ws7 | last 15:45:35, 601.4 min ago / counter-side 2026-09-02 19:39:30 | 0.157790 | +1.3944 |
| 2026-09-03 01:48:05 | NO PASS rider ws7 - ws7 84.75 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 3: ws5,ws6,ws7 | last 15:45:35, 602.5 min ago / counter-side 2026-09-02 19:39:30 | 0.157650 | +1.3045 |
| 2026-09-03 02:35:10 | the favourable extreme - MFE 2.5447 | - | 3: ws1,ws3,ws4 | last 02:26:55, 8.2 min ago | 0.159580 | +2.5447 |
| 2026-09-03 02:37:25 | LATCH1 rider ws7 - latch 1 at the t1 cadence 2026-09-03 02:37:25, divergence state +1 | - | 2: ws3,ws4 | last 02:26:55, 10.5 min ago | 0.158940 | +2.1334 |
| 2026-09-03 02:37:25 | **CADENCE:** CADENCE rider ws7 - t1 gcws30b journey 02:31:00..02:37:20 reached 116.55 past the 95.0 fence, ws1r reversed 02:36:00 during, r 68.60 past the 56.0 fence, stamp 02:36:00, ib 85.0 cross 02:36:30 hold 6 bars, ib dwell 12 bars \| rider ws7 54.88, no-longer-exfence yes, reversed yes \| mage-cascade down | none offered | 2: ws3,ws4 | last 02:26:55, 10.5 min ago | 0.158940 | +2.1334 |
| 2026-09-03 02:37:25 | **CADENCE:** EXHAUST rider ws7 - t4 at a t1 cadence - rider ws7 54.88, no candidate at or below ws15 (the jump bound 8) | - | 2: ws3,ws4 | last 02:26:55, 10.5 min ago | 0.158940 | +2.1334 |
| 2026-09-03 02:37:25 | THIS LEG CLOSES on t1, realised +2.1720, drag 0.1975, net +1.9745 | - | 2: ws3,ws4 | last 02:26:55, 10.5 min ago | 0.158940 | +2.1334 |

## 2026-09-03 leg 2 - SHORT   opens 2026-09-03 02:37:30   exits 2026-09-03 04:39:00 on t1   held 121.5 min   MAE 0.5094   MFE 1.2767   realised +0.8365   net +0.6390

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-09-03 02:37:30 | >>> THIS LEG OPENS SHORT | - | none | last 19:39:30, 418.0 min ago / counter-side 2026-09-03 02:26:55 | 0.159000 | -0.0000 |
| 2026-09-03 02:57:20 | the ADVERSE extreme - MAE 0.5094 | - | none | last 19:39:30, 437.8 min ago / counter-side 2026-09-03 02:26:55 | 0.159810 | -0.5094 |
| 2026-09-03 03:24:00 | ARM - ws4r: ws4r 8.52 oob | - | 3: ws1,ws3,ws4 | last 19:39:30, 464.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158580 | +0.2642 |
| 2026-09-03 03:24:00 | RETEST - ws1r 20.64 is not oob at the arm - the gate stays shut | - | 3: ws1,ws3,ws4 | last 19:39:30, 464.5 min ago / counter-side 2026-09-03 03:15:55 | 0.158580 | +0.2642 |
| 2026-09-03 03:24:05 | NO RIDER - the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs | - | 3: ws1,ws3,ws4 | last 19:39:30, 464.6 min ago / counter-side 2026-09-03 03:15:55 | 0.158610 | +0.2453 |
| 2026-09-03 04:23:25 | RIDER rider ws10 - t1 gcws30b journey 04:14:00..04:23:20 reached -24.03 past the 5.0 fence, ws1r reversed 04:20:00 during, r 22.22 past the 44.0 fence, stamp 04:20:00, ib 15.0 cross 04:22:30 hold 6 bars, ib dwell 12 bars \| ws10 r 15.92 picked up at a cadence, no prior rider | - | 2: ws2,ws10 | last 19:39:30, 523.9 min ago / counter-side 2026-09-03 03:15:55 | 0.158290 | +0.4465 |
| 2026-09-03 04:27:20 | BATON rider ws10 - ws10 -> ws12, between cadences, lin_hop 2 | ws11: 17.58, ws12: 12.35 | 4: ws3,ws10,ws11,ws12 | last 19:39:30, 527.8 min ago / counter-side 2026-09-03 03:15:55 | 0.158310 | +0.4340 |
| 2026-09-03 04:35:20 | the favourable extreme - MFE 1.2767 | - | 3: ws10,ws11,ws12 | last 19:39:30, 535.8 min ago / counter-side 2026-09-03 03:15:55 | 0.156970 | +1.2767 |
| 2026-09-03 04:38:55 | NO PASS rider ws12 - ws12 17.09 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 3: ws10,ws11,ws12 | last 19:39:30, 539.4 min ago / counter-side 2026-09-03 03:15:55 | 0.157850 | +0.7233 |
| 2026-09-03 04:39:00 | LATCH1 rider ws12 - latch 1 at the t1 cadence 2026-09-03 04:39:00, divergence state -1 | - | 3: ws10,ws11,ws12 | last 19:39:30, 539.5 min ago / counter-side 2026-09-03 03:15:55 | 0.157750 | +0.7862 |
| 2026-09-03 04:39:00 | **CADENCE:** CADENCE rider ws12 - t1 gcws30b journey 04:34:30..04:38:50 reached -17.54 past the 5.0 fence, back inside the 15.0 ib fence 04:38:00, ws1r reversed 04:39:00 inside the 120s grace from the cross bar 04:38:00, r 39.75 past the 44.0 fence, stamp 04:39:00, hold 6 bars, ib dwell 12 bars \| rider ws12 15.72, no-longer-exfence no, reversed yes \| mage-cascade down | none offered | 3: ws10,ws11,ws12 | last 19:39:30, 539.5 min ago / counter-side 2026-09-03 03:15:55 | 0.157750 | +0.7862 |
| 2026-09-03 04:39:00 | **CADENCE:** EXHAUST rider ws12 - t4 at a t1 cadence - rider ws12 15.72, no candidate at or below ws20 (the jump bound 8) | - | 3: ws10,ws11,ws12 | last 19:39:30, 539.5 min ago / counter-side 2026-09-03 03:15:55 | 0.157750 | +0.7862 |
| 2026-09-03 04:39:00 | THIS LEG CLOSES on t1, realised +0.8365, drag 0.1975, net +0.6390 | - | 3: ws10,ws11,ws12 | last 19:39:30, 539.5 min ago / counter-side 2026-09-03 03:15:55 | 0.157750 | +0.7862 |

## 2026-09-03 leg 3 - LONG   opens 2026-09-03 04:39:05   exits 2026-09-03 05:55:00 on t1   held 75.9 min   MAE 0.2537   MFE 1.8837   realised +1.5983   net +1.4008

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-09-03 04:39:05 | >>> THIS LEG OPENS LONG | - | none | last 03:15:55, 83.2 min ago | 0.157670 | +0.0000 |
| 2026-09-03 04:52:25 | ARM - gcws30b+(ws1r\|ws2r): gcws30b 99.67 at or beyond the 5.0/95.0 fence, held 6 bars, + ws1r oob (ws1r 96.86, ws2r 84.26) | - | 2: ws1,ws2 | last 03:15:55, 96.5 min ago | 0.159300 | +1.0338 |
| 2026-09-03 04:52:25 | RETEST - ws2r 84.26 / ws3r 67.59 - not both inside the fence at the arm | - | 2: ws1,ws2 | last 03:15:55, 96.5 min ago | 0.159300 | +1.0338 |
| 2026-09-03 04:52:30 | NO RIDER - the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs | - | 2: ws1,ws2 | last 03:15:55, 96.6 min ago | 0.159450 | +1.1289 |
| 2026-09-03 05:01:30 | the favourable extreme - MFE 1.8837 | - | 2: ws2,ws3 | last 03:15:55, 105.6 min ago | 0.160640 | +1.8837 |
| 2026-09-03 05:02:55 | LATCH1 - latch 1 at the t1 cadence 2026-09-03 05:02:55, divergence state +1 | - | 2: ws2,ws3 | last 03:15:55, 107.0 min ago | 0.160100 | +1.5412 |
| 2026-09-03 05:02:55 | RIDER rider ws3 - t1 gcws30b journey 04:51:30..05:02:50 reached 101.31 past the 95.0 fence, ws1r reversed 04:59:00 during, r 69.80 past the 56.0 fence, stamp 04:59:00, ib 85.0 cross 05:02:00 hold 6 bars, ib dwell 12 bars \| ws3 r 95.43 picked up at a cadence, no prior rider | - | 2: ws2,ws3 | last 03:15:55, 107.0 min ago | 0.160100 | +1.5412 |
| 2026-09-03 05:06:55 | BATON rider ws3 - ws3 -> ws5, between cadences, lin_hop 2 | ws4: 84.76, ws5: 89.22 | 4: ws2,ws3,ws4,ws5 | last 03:15:55, 111.0 min ago | 0.159780 | +1.3382 |
| 2026-09-03 05:10:55 | NO PASS rider ws5 - ws5 82.92 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 2: ws4,ws5 | last 03:15:55, 115.0 min ago | 0.159540 | +1.1860 |
| 2026-09-03 05:28:05 | the ADVERSE extreme - MAE 0.2537 | - | none | last 03:15:55, 132.2 min ago | 0.157270 | -0.2537 |
| 2026-09-03 05:55:00 | LATCH1 rider ws5 - latch 1 at the t1 cadence 2026-09-03 05:55:00, divergence state +1 | - | 2: ws1,ws3 | last 03:15:55, 159.1 min ago | 0.160190 | +1.5983 |
| 2026-09-03 05:55:00 | **CADENCE:** CADENCE rider ws5 - t1 gcws30b journey 05:50:00..05:54:20 reached 97.04 past the 95.0 fence, back inside the 85.0 ib fence 05:53:30, ws1r reversed 05:55:00 inside the 120s grace from the cross bar 05:53:30, r 83.60 past the 56.0 fence, stamp 05:55:00, hold 6 bars, ib dwell 12 bars \| rider ws5 72.90, no-longer-exfence yes, reversed yes \| mage-cascade down | none offered | 2: ws1,ws3 | last 03:15:55, 159.1 min ago | 0.160190 | +1.5983 |
| 2026-09-03 05:55:00 | **CADENCE:** EXHAUST rider ws5 - t4 at a t1 cadence - rider ws5 72.90, no candidate at or below ws13 (the jump bound 8) | - | 2: ws1,ws3 | last 03:15:55, 159.1 min ago | 0.160190 | +1.5983 |
| 2026-09-03 05:55:00 | THIS LEG CLOSES on t1, realised +1.5983, drag 0.1975, net +1.4008 | - | 2: ws1,ws3 | last 03:15:55, 159.1 min ago | 0.160190 | +1.5983 |

## 2026-09-03 leg 4 - SHORT   opens 2026-09-03 05:55:05   exits 2026-09-03 08:07:35 on STOP at 1.10%   held 132.5 min   MAE 1.1000   MFE 0.3309   realised -1.1000   net -1.2975

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-09-03 05:55:05 | >>> THIS LEG OPENS SHORT | - | none | last 19:39:30, 615.6 min ago / counter-side 2026-09-03 03:15:55 | 0.160190 | -0.0000 |
| 2026-09-03 06:00:10 | the favourable extreme - MFE 0.3309 | - | none | last 19:39:30, 620.7 min ago / counter-side 2026-09-03 03:15:55 | 0.159660 | +0.3309 |
| 2026-09-03 07:32:05 | ARM - gcws30b+(ws1r\|ws2r): gcws30b -5.70 at or beyond the 5.0/95.0 fence, held 6 bars, + ws2r oob (ws1r 19.20, ws2r 14.04) | - | 5: ws1,ws2,ws3,ws6,ws7 | last 19:39:30, 712.6 min ago / counter-side 2026-09-03 07:15:45 | 0.160150 | +0.0250 |
| 2026-09-03 07:32:05 | RETEST - ws1r 19.20 is not oob at the arm - the gate stays shut | - | 5: ws1,ws2,ws3,ws6,ws7 | last 19:39:30, 712.6 min ago / counter-side 2026-09-03 07:15:45 | 0.160150 | +0.0250 |
| 2026-09-03 07:32:10 | NO RIDER - the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs | - | 5: ws1,ws2,ws3,ws6,ws7 | last 19:39:30, 712.7 min ago / counter-side 2026-09-03 07:15:45 | 0.160260 | -0.0437 |
| 2026-09-03 07:33:55 | RIDER rider ws7 - t1 gcws30b journey 07:30:30..07:33:50 reached -7.57 past the 5.0 fence, ws1r reversed 07:33:00 during, r 28.24 past the 44.0 fence, stamp 07:33:00, ib 15.0 cross 07:33:00 hold 6 bars, ib dwell 12 bars \| ws7 r 17.20 picked up at a cadence, no prior rider | - | 4: ws2,ws3,ws6,ws7 | last 19:39:30, 714.4 min ago / counter-side 2026-09-03 07:15:45 | 0.160510 | -0.1998 |
| 2026-09-03 07:40:00 | NO PASS rider ws7 - ws7 27.97 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 2: ws6,ws7 | last 19:39:30, 720.5 min ago / counter-side 2026-09-03 07:15:45 | 0.161480 | -0.8053 |
| 2026-09-03 08:07:35 | the ADVERSE extreme - MAE 1.1237 | - | 1: ws7 | last 19:39:30, 748.1 min ago / counter-side 2026-09-03 07:15:45 | 0.161990 | -1.1237 |
| 2026-09-03 08:07:35 | THIS LEG CLOSES on STOP at 1.10%, realised -1.1000, drag 0.1975, net -1.2975 | - | 1: ws7 | last 19:39:30, 748.1 min ago / counter-side 2026-09-03 07:15:45 | 0.161990 | -1.1237 |
| 2026-09-03 08:43:00 | LATCH1 rider ws7 - latch 1 at the t1 cadence 2026-09-03 08:43:00, divergence state -1 | - | 3: ws3,ws4,ws13 | last 19:39:30, 783.5 min ago / counter-side 2026-09-03 07:15:45 | 0.160670 | -0.2996 |
| 2026-09-03 08:43:00 | **CADENCE:** CADENCE rider ws7 - t1 gcws30b journey 08:40:00..08:41:50 reached 1.93 past the 5.0 fence, back inside the 15.0 ib fence 08:41:00, ws1r reversed 08:43:00 inside the 120s grace from the cross bar 08:41:00, r 37.29 past the 44.0 fence, stamp 08:43:00, hold 6 bars, ib dwell 12 bars \| rider ws7 51.62, no-longer-exfence yes, reversed yes \| mage-cascade up | ws13: 17.08 | 3: ws3,ws4,ws13 | last 19:39:30, 783.5 min ago / counter-side 2026-09-03 07:15:45 | 0.160670 | -0.2996 |
| 2026-09-03 08:43:00 | **CADENCE:** BATON rider ws7 - ws7 -> ws13, at a t1 cadence, capped at ws15 by the jump bound 8 | ws13: 17.08 | 3: ws3,ws4,ws13 | last 19:39:30, 783.5 min ago / counter-side 2026-09-03 07:15:45 | 0.160670 | -0.2996 |
| 2026-09-03 08:56:25 | LATCH1 rider ws13 - latch 1 at the t1 cadence 2026-09-03 08:56:25, divergence state -1 | - | 7: ws1,ws3,ws4,ws5,ws12,ws13,ws14 | last 19:39:30, 796.9 min ago / counter-side 2026-09-03 07:15:45 | 0.160340 | -0.0936 |
| 2026-09-03 08:56:25 | **CADENCE:** HOLD rider ws13 - ws14..ws15 is lin_hop 2 reach from rider ws13 and 1 of it is ex-fence and printing towards at a t1 cadence - ws14 23.84 - the tests are concluded and the walk goes to the next cadence | - | 7: ws1,ws3,ws4,ws5,ws12,ws13,ws14 | last 19:39:30, 796.9 min ago / counter-side 2026-09-03 07:15:45 | 0.160340 | -0.0936 |
| 2026-09-03 09:07:10 | BATON rider ws13 - ws13 -> ws15, between cadences, lin_hop 2 | ws14: 18.26, ws15: 18.63 | 12: ws2,ws3,ws4,ws5,ws6,ws8,ws12,ws13,ws14,ws15,ws16,ws21 | last 19:39:30, 807.7 min ago / counter-side 2026-09-03 07:15:45 | 0.160030 | +0.0999 |
| 2026-09-03 09:07:25 | LATCH1 rider ws15 - latch 1 at the t1 cadence 2026-09-03 09:07:25, divergence state -1 | - | 12: ws2,ws3,ws4,ws5,ws6,ws8,ws12,ws13,ws14,ws15,ws16,ws21 | last 19:39:30, 807.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159970 | +0.1373 |
| 2026-09-03 09:07:25 | **CADENCE:** HOLD rider ws15 - ws16..ws17 is lin_hop 2 reach from rider ws15 and 1 of it is ex-fence and printing towards at a t1 cadence - ws16 21.01 - the tests are concluded and the walk goes to the next cadence | - | 12: ws2,ws3,ws4,ws5,ws6,ws8,ws12,ws13,ws14,ws15,ws16,ws21 | last 19:39:30, 807.9 min ago / counter-side 2026-09-03 07:15:45 | 0.159970 | +0.1373 |
| 2026-09-03 09:16:40 | BATON rider ws15 - ws15 -> ws16, between cadences, lin_hop 2 | ws16: 28.68 | 7: ws6,ws12,ws13,ws14,ws15,ws16,ws21 | last 19:39:30, 817.2 min ago / counter-side 2026-09-03 07:15:45 | 0.160810 | -0.3870 |
| 2026-09-03 09:34:20 | NO PASS rider ws16 - ws16 17.03 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 11: ws2,ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws19,ws21 | last 19:39:30, 834.8 min ago / counter-side 2026-09-03 07:15:45 | 0.160310 | -0.0749 |
| 2026-09-03 09:45:00 | LATCH1 rider ws16 - latch 1 at the t1 cadence 2026-09-03 09:45:00, divergence state -1 | - | 13: ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21 | last 19:39:30, 845.5 min ago / counter-side 2026-09-03 07:15:45 | 0.159950 | +0.1498 |
| 2026-09-03 09:45:00 | **CADENCE:** HOLD rider ws16 - ws17..ws18 is lin_hop 2 reach from rider ws16 and 2 of it is ex-fence and printing towards at a t1 cadence - ws17 24.24, ws18 16.64 - the tests are concluded and the walk goes to the next cadence | - | 13: ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21 | last 19:39:30, 845.5 min ago / counter-side 2026-09-03 07:15:45 | 0.159950 | +0.1498 |
| 2026-09-03 09:46:00 | BATON rider ws16 - ws16 -> ws18, between cadences, lin_hop 2 | ws17: 25.61, ws18: 17.74 | 13: ws9,ws10,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21 | last 19:39:30, 846.5 min ago / counter-side 2026-09-03 07:15:45 | 0.160080 | +0.0687 |
| 2026-09-03 10:53:10 | BATON rider ws18 - ws18 -> ws20, between cadences, lin_hop 2 | ws19: 15.41, ws20: 11.84 | 19: ws6,ws8,ws11,ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21,ws22,ws23,ws24,ws25,ws26,ws28 | last 19:39:30, 913.7 min ago / counter-side 2026-09-03 07:15:45 | 0.159410 | +0.4869 |
| 2026-09-03 11:00:55 | BATON rider ws20 - ws20 -> ws22, between cadences, lin_hop 2 | ws22: 26.19 | 16: ws12,ws13,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21,ws22,ws23,ws24,ws25,ws26,ws28 | last 19:39:30, 921.4 min ago / counter-side 2026-09-03 07:15:45 | 0.159710 | +0.2996 |
| 2026-09-03 11:05:30 | BATON rider ws22 - ws22 -> ws24, between cadences, lin_hop 2 | ws23: 12.33, ws24: 14.69 | 15: ws12,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21,ws22,ws23,ws24,ws25,ws26,ws28 | last 19:39:30, 926.0 min ago / counter-side 2026-09-03 07:15:45 | 0.159670 | +0.3246 |
| 2026-09-03 11:09:55 | BATON rider ws24 - ws24 -> ws26, between cadences, lin_hop 2 | ws25: 15.51, ws26: 10.97 | 17: ws1,ws12,ws14,ws15,ws16,ws17,ws18,ws19,ws20,ws21,ws22,ws23,ws24,ws25,ws26,ws28,ws29 | last 19:39:30, 930.4 min ago / counter-side 2026-09-03 07:15:45 | 0.159950 | +0.1498 |
| 2026-09-03 11:16:55 | BATON rider ws26 - ws26 -> ws28, between cadences, lin_hop 2 | ws27: 14.52, ws28: 18.45 | 14: ws2,ws17,ws18,ws19,ws20,ws21,ws22,ws23,ws24,ws25,ws26,ws27,ws28,ws29 | last 19:39:30, 937.4 min ago / counter-side 2026-09-03 07:15:45 | 0.159590 | +0.3746 |
| 2026-09-03 11:40:55 | BATON rider ws28 - ws28 -> ws29, between cadences, lin_hop 2 | ws29: 30.15 | 7: ws23,ws24,ws25,ws26,ws27,ws28,ws29 | last 19:39:30, 961.4 min ago / counter-side 2026-09-03 07:15:45 | 0.160960 | -0.4807 |
| 2026-09-03 14:06:25 | **CADENCE:** CADENCE rider ws29 - t1 gcws30b journey 13:59:30..14:06:20 reached -2.13 past the 5.0 fence, ws1r reversed 14:06:00 during, r 17.26 past the 44.0 fence, stamp 14:06:00, ib 15.0 cross 14:05:30 hold 6 bars, ib dwell 12 bars \| rider ws29 76.20, no-longer-exfence yes, reversed no \| mage-cascade up | none offered | 3: ws1,ws2,ws3 | last 19:39:30, 1106.9 min ago / counter-side 2026-09-03 13:53:05 | 0.162080 | -1.1798 |
| 2026-09-03 14:06:25 | **CADENCE:** EXHAUST rider ws29 - exhaust at a t1 cadence - rider ws29 76.20, no candidate at or below ws37 (the jump bound 8) | - | 3: ws1,ws2,ws3 | last 19:39:30, 1106.9 min ago / counter-side 2026-09-03 13:53:05 | 0.162080 | -1.1798 |

## 2026-09-03 leg 5 - THE CHAIN HAS NO SUCH LEG. 2026-09-03 carries 4 legs.

| the read | value |
|---|---|
| legs in the chain over the window | 4 |
| legs opening on 2026-09-03 | 4 |
| seconds to compute | 49.0 |
