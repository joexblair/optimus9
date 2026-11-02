# LINEAGE2 BATON CHAIN - THE ARM IS HANDED IN AT 2026-09-03 04:39:05, SIDE high
# TAPE 1632960 bars | B 2026-10-04 23:59:55, the last tape bar, no end bound | RULED_OK True

| the setting | value | what it is |
|---|---|---|
| the r fence | 75.0 -> (25.0, 75.0) | his 25/75 |
| the ladder top | ws30 | his max-lineage-TF ws30 |
| the per-line ex-fence latch | OFF | his 1101 "disable the latch" |
| the ex-fence read's source | closed_prev | his 1101 "closed_prev only for exiting fences" |
| the oob read's source | emerging | he put oob in neither category - both arms built |
| the oob->ib cross's source | emerging | his gut, with the other arm built |
| the TF floor for the chart-matched read | ws1 | his "ws1{any} and gcws1{any} stay on emerging" |
| reversal detection | emerging, always | his "keeping the lift-off on emerging allows us to capture those much needed 0445 reversal timestamps" |
| the latch's on-edge hold | 4 bars = 20 s | an ex-fence cross must hold this |
| what releases the latch | 'lift' | the latched line's own lift-off, and nothing else - his 1031 spec line |
| the baton path's oob reads at depth | 0 | the banked arm |
| the hops a baton may make | 2 | rider -> candidate, between cadences |
| the cross hold on a pass | 12 bars = 60 s | mode 'ib' only |
| the reversal hold | 12 bars = 60 s | modes 'reversal' and 'reversal+quarter' |
| a quarter of the TF width | 0.25 x TF x 12 bars | ws22 -> 66 bars = 330 s |
| the ws1b counter-oob exit | 0 | 0 = his 1030 "drop the opposing oob side forced exit" |
| ws1b's oob dwell | 0 bars | his value 12 is not banked |
| pseudo-closed | 99 | 99 = off, the banked arm |
| the cadence types that may decide | t1 | his 1031 filter |
| the latch RE-LATCH | ON, at cadences only | his 1031 mech: a lift-off that printed ex-fence, the line never reaching in-fence since, and the value back at or beyond that lift-off value |
| the rider jump bound | 8 TFs | his 1031 rule, from a rider of 0 at the arm |
| the retest gate | ON | it holds the walk's start either way; only its cadence is filtered |
| the barrage mech | ON | |
| the 2-staged cadence latch | ON | |
| t3 | OFF | |
| the ladder-top rider reset | ON | his 1031 trick: at the top rung's exhaust the rider resets to 0 and re-scans, capped by the jump bound. No limit on repeats |
| the mage cascade | DISABLED | his 1031 "completely disable the mage cascade" - at 0 neither the OPPOSES exhaust nor the MATCHES no-action fires. Its verdict is still PRINTED in the cadence rows, as data |
| the stop | not applied - this is a walk, not a scored leg |  |

## MODE 'ib' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-09-03 04:39:05 | ARM | - | - | - | arm_at 2026-09-03 04:39:05 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 04:39:10 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 05:02:55 | RIDER | ws3 | - | - | t1 gcws30b journey 04:51:30..05:02:50 reached 101.31 past the 95.0 fence, ws1r reversed 04:59:00 during, r 69.80 past the 56.0 fence, stamp 04:59:00, ib 85.0 cross 05:02:00 hold 6 bars, ib dwell 12 bars \| ws3 r 95.43 picked up at a cadence, no prior rider |
| 2026-09-03 05:06:55 | BATON | ws3 | ws5 | ws4 84.76, ws5 89.22 | ws3 -> ws5, between cadences, lin_hop 2 |
| 2026-09-03 05:10:55 | NO PASS | ws5 | - | none offered | ws5 82.92 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 05:55:00 | CADENCE | ws5 | - | none offered | t1 gcws30b journey 05:50:00..05:54:20 reached 97.04 past the 95.0 fence, back inside the 85.0 ib fence 05:53:30, ws1r reversed 05:55:00 inside the 120s grace from the cross bar 05:53:30, r 83.60 past the 56.0 fence, stamp 05:55:00, hold 6 bars, ib dwell 12 bars \| rider ws5 72.90, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 05:55:00 | EXHAUST | ws5 | - | - | t4 at a t1 cadence - rider ws5 72.90, no candidate at or below ws13 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-09-03 05:55:00 |
| baton passes made | 1 |
| minutes from the arm to the verdict | 75.9 |
| the rider chain | ws3 > ws5 |

## MODE 'reversal' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-09-03 04:39:05 | ARM | - | - | - | arm_at 2026-09-03 04:39:05 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 04:39:10 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 05:02:55 | RIDER | ws3 | - | - | t1 gcws30b journey 04:51:30..05:02:50 reached 101.31 past the 95.0 fence, ws1r reversed 04:59:00 during, r 69.80 past the 56.0 fence, stamp 04:59:00, ib 85.0 cross 05:02:00 hold 6 bars, ib dwell 12 bars \| ws3 r 95.43 picked up at a cadence, no prior rider |
| 2026-09-03 05:03:50 | NO PASS | ws3 | - | none offered | ws3 95.38 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 05:55:00 | CADENCE | ws3 | - | none offered | t1 gcws30b journey 05:50:00..05:54:20 reached 97.04 past the 95.0 fence, back inside the 85.0 ib fence 05:53:30, ws1r reversed 05:55:00 inside the 120s grace from the cross bar 05:53:30, r 83.60 past the 56.0 fence, stamp 05:55:00, hold 6 bars, ib dwell 12 bars \| rider ws3 96.36, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-09-03 05:55:00 | HOLD | ws3 | - | - | rider ws3 96.36 oob - no action |
| 2026-09-03 06:01:00 | BATON | ws3 | ws4 | ws4 89.10 | ws3 -> ws4, between cadences, lin_hop 2 |
| 2026-09-03 06:25:00 | NO PASS | ws4 | - | none offered | ws4 28.92 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 06:42:25 | CADENCE | ws4 | - | ws7 77.54, ws8 84.33, ws9 85.39 | t1 gcws30b journey 06:34:00..06:42:20 reached 124.19 past the 95.0 fence, ws1r reversed 06:41:00 during, r 70.67 past the 56.0 fence, stamp 06:41:00, ib 85.0 cross 06:41:30 hold 6 bars, ib dwell 12 bars \| rider ws4 77.91, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 06:42:25 | BATON | ws4 | ws9 | ws7 77.54, ws8 84.33, ws9 85.39 | ws4 -> ws9, at a t1 cadence, capped at ws12 by the jump bound 8 |
| 2026-09-03 06:49:20 | BATON | ws9 | ws11 | ws11 80.92 | ws9 -> ws11, between cadences, lin_hop 2 |
| 2026-09-03 06:50:30 | BATON | ws11 | ws12 | ws12 72.61 | ws11 -> ws12, between cadences, lin_hop 2 |
| 2026-09-03 06:51:25 | BATON | ws12 | ws14 | ws14 82.33 | ws12 -> ws14, between cadences, lin_hop 2 |
| 2026-09-03 07:07:25 | CADENCE | ws14 | - | none offered | t1 gcws30b journey 07:04:30..07:07:20 reached 103.09 past the 95.0 fence, ws1r reversed 07:07:00 during, r 87.61 past the 56.0 fence, stamp 07:07:00, ib 85.0 cross 07:06:30 hold 6 bars, ib dwell 12 bars \| rider ws14 85.37, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-09-03 07:07:25 | HOLD | ws14 | - | - | rider ws14 85.37 oob - no action |
| 2026-09-03 07:11:05 | NO PASS | ws14 | - | none offered | ws14 81.43 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 07:44:25 | CADENCE | ws14 | - | ws17 68.42, ws18 85.58, ws20 78.23, ws22 86.79 | t1 gcws30b journey 07:39:30..07:44:20 reached 101.19 past the 95.0 fence, ws1r reversed 07:44:00 during, r 85.12 past the 56.0 fence, stamp 07:44:00, ib 85.0 cross 07:43:30 hold 6 bars, ib dwell 12 bars \| rider ws14 61.67, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 07:44:25 | BATON | ws14 | ws22 | ws17 68.42, ws18 85.58, ws20 78.23, ws22 86.79 | ws14 -> ws22, at a t1 cadence, capped at ws22 by the jump bound 8 |
| 2026-09-03 07:48:05 | BATON | ws22 | ws24 | ws23 77.85, ws24 69.94 | ws22 -> ws24, between cadences, lin_hop 2 |
| 2026-09-03 08:11:25 | HOLD | ws24 | - | - | ws25..ws26 is lin_hop 2 reach from rider ws24 and 1 of it is ex-fence and printing towards at a t1 cadence - ws26 85.62 - the tests are concluded and the walk goes to the next cadence |
| 2026-09-03 08:14:00 | BATON | ws24 | ws26 | ws26 81.22 | ws24 -> ws26, between cadences, lin_hop 2 |
| 2026-09-03 08:18:40 | NO PASS | ws26 | - | none offered | ws26 79.12 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 11:01:25 | CADENCE | ws26 | - | none offered | t1 gcws30b journey 10:52:00..11:01:20 reached 124.66 past the 95.0 fence, ws1r reversed 11:01:00 during, r 69.11 past the 56.0 fence, stamp 11:01:00, ib 85.0 cross 11:00:30 hold 6 bars, ib dwell 12 bars \| rider ws26 9.97, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 11:01:25 | EXHAUST | ws26 | - | - | t4 at a t1 cadence - rider ws26 9.97, no candidate at or below ws34 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-09-03 11:01:25 |
| baton passes made | 8 |
| minutes from the arm to the verdict | 382.3 |
| the rider chain | ws3 > ws4 > ws9 > ws11 > ws12 > ws14 > ws22 > ws24 > ws26 |

## MODE 'reversal+quarter' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-09-03 04:39:05 | ARM | - | - | - | arm_at 2026-09-03 04:39:05 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 04:39:10 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 05:02:55 | RIDER | ws3 | - | - | t1 gcws30b journey 04:51:30..05:02:50 reached 101.31 past the 95.0 fence, ws1r reversed 04:59:00 during, r 69.80 past the 56.0 fence, stamp 04:59:00, ib 85.0 cross 05:02:00 hold 6 bars, ib dwell 12 bars \| ws3 r 95.43 picked up at a cadence, no prior rider |
| 2026-09-03 05:03:50 | NO PASS | ws3 | - | none offered | ws3 95.38 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 05:55:00 | CADENCE | ws3 | - | none offered | t1 gcws30b journey 05:50:00..05:54:20 reached 97.04 past the 95.0 fence, back inside the 85.0 ib fence 05:53:30, ws1r reversed 05:55:00 inside the 120s grace from the cross bar 05:53:30, r 83.60 past the 56.0 fence, stamp 05:55:00, hold 6 bars, ib dwell 12 bars \| rider ws3 96.36, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-09-03 05:55:00 | HOLD | ws3 | - | - | rider ws3 96.36 oob - no action |
| 2026-09-03 06:01:00 | BATON | ws3 | ws4 | ws4 89.10 | ws3 -> ws4, between cadences, lin_hop 2 |
| 2026-09-03 06:01:05 | NO PASS | ws4 | - | none offered | ws4 88.85 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 06:42:25 | CADENCE | ws4 | - | ws7 77.54, ws8 84.33, ws9 85.39 | t1 gcws30b journey 06:34:00..06:42:20 reached 124.19 past the 95.0 fence, ws1r reversed 06:41:00 during, r 70.67 past the 56.0 fence, stamp 06:41:00, ib 85.0 cross 06:41:30 hold 6 bars, ib dwell 12 bars \| rider ws4 77.91, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 06:42:25 | BATON | ws4 | ws9 | ws7 77.54, ws8 84.33, ws9 85.39 | ws4 -> ws9, at a t1 cadence, capped at ws12 by the jump bound 8 |
| 2026-09-03 06:50:40 | BATON | ws9 | ws11 | ws11 77.48 | ws9 -> ws11, between cadences, lin_hop 2 |
| 2026-09-03 06:52:20 | BATON | ws11 | ws12 | ws12 74.37 | ws11 -> ws12, between cadences, lin_hop 2 |
| 2026-09-03 06:53:30 | BATON | ws12 | ws14 | ws14 81.62 | ws12 -> ws14, between cadences, lin_hop 2 |
| 2026-09-03 07:07:25 | CADENCE | ws14 | - | none offered | t1 gcws30b journey 07:04:30..07:07:20 reached 103.09 past the 95.0 fence, ws1r reversed 07:07:00 during, r 87.61 past the 56.0 fence, stamp 07:07:00, ib 85.0 cross 07:06:30 hold 6 bars, ib dwell 12 bars \| rider ws14 85.37, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-09-03 07:07:25 | HOLD | ws14 | - | - | rider ws14 85.37 oob - no action |
| 2026-09-03 07:13:40 | NO PASS | ws14 | - | none offered | ws14 86.25 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 07:44:25 | CADENCE | ws14 | - | ws17 68.42, ws18 85.58, ws20 78.23, ws22 86.79 | t1 gcws30b journey 07:39:30..07:44:20 reached 101.19 past the 95.0 fence, ws1r reversed 07:44:00 during, r 85.12 past the 56.0 fence, stamp 07:44:00, ib 85.0 cross 07:43:30 hold 6 bars, ib dwell 12 bars \| rider ws14 61.67, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 07:44:25 | BATON | ws14 | ws22 | ws17 68.42, ws18 85.58, ws20 78.23, ws22 86.79 | ws14 -> ws22, at a t1 cadence, capped at ws22 by the jump bound 8 |
| 2026-09-03 07:52:40 | BATON | ws22 | ws24 | ws23 74.31, ws24 68.21 | ws22 -> ws24, between cadences, lin_hop 2 |
| 2026-09-03 08:11:25 | HOLD | ws24 | - | - | ws25..ws26 is lin_hop 2 reach from rider ws24 and 1 of it is ex-fence and printing towards at a t1 cadence - ws26 85.62 - the tests are concluded and the walk goes to the next cadence |
| 2026-09-03 08:19:05 | BATON | ws24 | ws26 | ws26 79.12 | ws24 -> ws26, between cadences, lin_hop 2 |
| 2026-09-03 08:24:15 | BATON | ws26 | ws28 | ws28 87.98 | ws26 -> ws28, between cadences, lin_hop 2 |
| 2026-09-03 08:30:00 | BATON | ws28 | ws29 | ws29 86.70 | ws28 -> ws29, between cadences, lin_hop 2 |
| 2026-09-03 08:36:55 | NO PASS | ws29 | - | none offered | ws29 81.39 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 11:01:25 | CADENCE | ws29 | - | none offered | t1 gcws30b journey 10:52:00..11:01:20 reached 124.66 past the 95.0 fence, ws1r reversed 11:01:00 during, r 69.11 past the 56.0 fence, stamp 11:01:00, ib 85.0 cross 11:00:30 hold 6 bars, ib dwell 12 bars \| rider ws29 20.78, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 11:01:25 | EXHAUST | ws29 | - | - | t4 at a t1 cadence - rider ws29 20.78, no candidate at or below ws37 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-09-03 11:01:25 |
| baton passes made | 10 |
| minutes from the arm to the verdict | 382.3 |
| the rider chain | ws3 > ws4 > ws9 > ws11 > ws12 > ws14 > ws22 > ws24 > ws26 > ws28 > ws29 |

## MODE 'ib' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 04:39:05 | ARM | - | arm_at 2026-09-03 04:39:05 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 04:39:10 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 04:39:05 | RETEST | - | ws1r 37.50 is not oob at the arm - the gate stays shut |
| 2026-09-03 05:02:55 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 05:02:55, divergence state +1 |
| 2026-09-03 05:02:55 | RIDER | ws3 | t1 gcws30b journey 04:51:30..05:02:50 reached 101.31 past the 95.0 fence, ws1r reversed 04:59:00 during, r 69.80 past the 56.0 fence, stamp 04:59:00, ib 85.0 cross 05:02:00 hold 6 bars, ib dwell 12 bars \| ws3 r 95.43 picked up at a cadence, no prior rider |
| 2026-09-03 05:06:55 | BATON | ws3 | ws3 -> ws5, between cadences, lin_hop 2 |
| 2026-09-03 05:10:55 | NO PASS | ws5 | ws5 82.92 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 05:55:00 | LATCH1 | ws5 | latch 1 at the t1 cadence 2026-09-03 05:55:00, divergence state +1 |
| 2026-09-03 05:55:00 | CADENCE | ws5 | t1 gcws30b journey 05:50:00..05:54:20 reached 97.04 past the 95.0 fence, back inside the 85.0 ib fence 05:53:30, ws1r reversed 05:55:00 inside the 120s grace from the cross bar 05:53:30, r 83.60 past the 56.0 fence, stamp 05:55:00, hold 6 bars, ib dwell 12 bars \| rider ws5 72.90, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 05:55:00 | EXHAUST | ws5 | t4 at a t1 cadence - rider ws5 72.90, no candidate at or below ws13 (the jump bound 8) |

## MODE 'reversal' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 04:39:05 | ARM | - | arm_at 2026-09-03 04:39:05 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 04:39:10 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 04:39:05 | RETEST | - | ws1r 37.50 is not oob at the arm - the gate stays shut |
| 2026-09-03 05:02:55 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 05:02:55, divergence state +1 |
| 2026-09-03 05:02:55 | RIDER | ws3 | t1 gcws30b journey 04:51:30..05:02:50 reached 101.31 past the 95.0 fence, ws1r reversed 04:59:00 during, r 69.80 past the 56.0 fence, stamp 04:59:00, ib 85.0 cross 05:02:00 hold 6 bars, ib dwell 12 bars \| ws3 r 95.43 picked up at a cadence, no prior rider |
| 2026-09-03 05:03:50 | NO PASS | ws3 | ws3 95.38 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 05:55:00 | LATCH1 | ws3 | latch 1 at the t1 cadence 2026-09-03 05:55:00, divergence state +1 |
| 2026-09-03 05:55:00 | CADENCE | ws3 | t1 gcws30b journey 05:50:00..05:54:20 reached 97.04 past the 95.0 fence, back inside the 85.0 ib fence 05:53:30, ws1r reversed 05:55:00 inside the 120s grace from the cross bar 05:53:30, r 83.60 past the 56.0 fence, stamp 05:55:00, hold 6 bars, ib dwell 12 bars \| rider ws3 96.36, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-09-03 05:55:00 | HOLD | ws3 | rider ws3 96.36 oob - no action |
| 2026-09-03 06:01:00 | BATON | ws3 | ws3 -> ws4, between cadences, lin_hop 2 |
| 2026-09-03 06:25:00 | NO PASS | ws4 | ws4 28.92 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 06:42:25 | LATCH1 | ws4 | latch 1 at the t1 cadence 2026-09-03 06:42:25, divergence state +1 |
| 2026-09-03 06:42:25 | CADENCE | ws4 | t1 gcws30b journey 06:34:00..06:42:20 reached 124.19 past the 95.0 fence, ws1r reversed 06:41:00 during, r 70.67 past the 56.0 fence, stamp 06:41:00, ib 85.0 cross 06:41:30 hold 6 bars, ib dwell 12 bars \| rider ws4 77.91, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 06:42:25 | BATON | ws4 | ws4 -> ws9, at a t1 cadence, capped at ws12 by the jump bound 8 |
| 2026-09-03 06:49:20 | BATON | ws9 | ws9 -> ws11, between cadences, lin_hop 2 |
| 2026-09-03 06:50:30 | BATON | ws11 | ws11 -> ws12, between cadences, lin_hop 2 |
| 2026-09-03 06:51:25 | BATON | ws12 | ws12 -> ws14, between cadences, lin_hop 2 |
| 2026-09-03 07:07:25 | CADENCE | ws14 | t1 gcws30b journey 07:04:30..07:07:20 reached 103.09 past the 95.0 fence, ws1r reversed 07:07:00 during, r 87.61 past the 56.0 fence, stamp 07:07:00, ib 85.0 cross 07:06:30 hold 6 bars, ib dwell 12 bars \| rider ws14 85.37, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-09-03 07:07:25 | HOLD | ws14 | rider ws14 85.37 oob - no action |
| 2026-09-03 07:11:05 | NO PASS | ws14 | ws14 81.43 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 07:44:25 | CADENCE | ws14 | t1 gcws30b journey 07:39:30..07:44:20 reached 101.19 past the 95.0 fence, ws1r reversed 07:44:00 during, r 85.12 past the 56.0 fence, stamp 07:44:00, ib 85.0 cross 07:43:30 hold 6 bars, ib dwell 12 bars \| rider ws14 61.67, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 07:44:25 | BATON | ws14 | ws14 -> ws22, at a t1 cadence, capped at ws22 by the jump bound 8 |
| 2026-09-03 07:48:05 | BATON | ws22 | ws22 -> ws24, between cadences, lin_hop 2 |
| 2026-09-03 08:11:25 | LATCH1 | ws24 | latch 1 at the t1 cadence 2026-09-03 08:11:25, divergence state +1 |
| 2026-09-03 08:11:25 | HOLD | ws24 | ws25..ws26 is lin_hop 2 reach from rider ws24 and 1 of it is ex-fence and printing towards at a t1 cadence - ws26 85.62 - the tests are concluded and the walk goes to the next cadence |
| 2026-09-03 08:14:00 | BATON | ws24 | ws24 -> ws26, between cadences, lin_hop 2 |
| 2026-09-03 08:18:40 | NO PASS | ws26 | ws26 79.12 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 11:01:25 | LATCH1 | ws26 | latch 1 at the t1 cadence 2026-09-03 11:01:25, divergence state +1 |
| 2026-09-03 11:01:25 | CADENCE | ws26 | t1 gcws30b journey 10:52:00..11:01:20 reached 124.66 past the 95.0 fence, ws1r reversed 11:01:00 during, r 69.11 past the 56.0 fence, stamp 11:01:00, ib 85.0 cross 11:00:30 hold 6 bars, ib dwell 12 bars \| rider ws26 9.97, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 11:01:25 | EXHAUST | ws26 | t4 at a t1 cadence - rider ws26 9.97, no candidate at or below ws34 (the jump bound 8) |

## MODE 'reversal+quarter' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 04:39:05 | ARM | - | arm_at 2026-09-03 04:39:05 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 04:39:10 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 04:39:05 | RETEST | - | ws1r 37.50 is not oob at the arm - the gate stays shut |
| 2026-09-03 05:02:55 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 05:02:55, divergence state +1 |
| 2026-09-03 05:02:55 | RIDER | ws3 | t1 gcws30b journey 04:51:30..05:02:50 reached 101.31 past the 95.0 fence, ws1r reversed 04:59:00 during, r 69.80 past the 56.0 fence, stamp 04:59:00, ib 85.0 cross 05:02:00 hold 6 bars, ib dwell 12 bars \| ws3 r 95.43 picked up at a cadence, no prior rider |
| 2026-09-03 05:03:50 | NO PASS | ws3 | ws3 95.38 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 05:55:00 | LATCH1 | ws3 | latch 1 at the t1 cadence 2026-09-03 05:55:00, divergence state +1 |
| 2026-09-03 05:55:00 | CADENCE | ws3 | t1 gcws30b journey 05:50:00..05:54:20 reached 97.04 past the 95.0 fence, back inside the 85.0 ib fence 05:53:30, ws1r reversed 05:55:00 inside the 120s grace from the cross bar 05:53:30, r 83.60 past the 56.0 fence, stamp 05:55:00, hold 6 bars, ib dwell 12 bars \| rider ws3 96.36, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-09-03 05:55:00 | HOLD | ws3 | rider ws3 96.36 oob - no action |
| 2026-09-03 06:01:00 | BATON | ws3 | ws3 -> ws4, between cadences, lin_hop 2 |
| 2026-09-03 06:01:05 | NO PASS | ws4 | ws4 88.85 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 06:42:25 | LATCH1 | ws4 | latch 1 at the t1 cadence 2026-09-03 06:42:25, divergence state +1 |
| 2026-09-03 06:42:25 | CADENCE | ws4 | t1 gcws30b journey 06:34:00..06:42:20 reached 124.19 past the 95.0 fence, ws1r reversed 06:41:00 during, r 70.67 past the 56.0 fence, stamp 06:41:00, ib 85.0 cross 06:41:30 hold 6 bars, ib dwell 12 bars \| rider ws4 77.91, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 06:42:25 | BATON | ws4 | ws4 -> ws9, at a t1 cadence, capped at ws12 by the jump bound 8 |
| 2026-09-03 06:50:40 | BATON | ws9 | ws9 -> ws11, between cadences, lin_hop 2 |
| 2026-09-03 06:52:20 | BATON | ws11 | ws11 -> ws12, between cadences, lin_hop 2 |
| 2026-09-03 06:53:30 | BATON | ws12 | ws12 -> ws14, between cadences, lin_hop 2 |
| 2026-09-03 07:07:25 | CADENCE | ws14 | t1 gcws30b journey 07:04:30..07:07:20 reached 103.09 past the 95.0 fence, ws1r reversed 07:07:00 during, r 87.61 past the 56.0 fence, stamp 07:07:00, ib 85.0 cross 07:06:30 hold 6 bars, ib dwell 12 bars \| rider ws14 85.37, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-09-03 07:07:25 | HOLD | ws14 | rider ws14 85.37 oob - no action |
| 2026-09-03 07:13:40 | NO PASS | ws14 | ws14 86.25 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 07:44:25 | CADENCE | ws14 | t1 gcws30b journey 07:39:30..07:44:20 reached 101.19 past the 95.0 fence, ws1r reversed 07:44:00 during, r 85.12 past the 56.0 fence, stamp 07:44:00, ib 85.0 cross 07:43:30 hold 6 bars, ib dwell 12 bars \| rider ws14 61.67, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 07:44:25 | BATON | ws14 | ws14 -> ws22, at a t1 cadence, capped at ws22 by the jump bound 8 |
| 2026-09-03 07:52:40 | BATON | ws22 | ws22 -> ws24, between cadences, lin_hop 2 |
| 2026-09-03 08:11:25 | LATCH1 | ws24 | latch 1 at the t1 cadence 2026-09-03 08:11:25, divergence state +1 |
| 2026-09-03 08:11:25 | HOLD | ws24 | ws25..ws26 is lin_hop 2 reach from rider ws24 and 1 of it is ex-fence and printing towards at a t1 cadence - ws26 85.62 - the tests are concluded and the walk goes to the next cadence |
| 2026-09-03 08:19:05 | BATON | ws24 | ws24 -> ws26, between cadences, lin_hop 2 |
| 2026-09-03 08:24:15 | BATON | ws26 | ws26 -> ws28, between cadences, lin_hop 2 |
| 2026-09-03 08:30:00 | BATON | ws28 | ws28 -> ws29, between cadences, lin_hop 2 |
| 2026-09-03 08:36:55 | NO PASS | ws29 | ws29 81.39 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 11:01:25 | LATCH1 | ws29 | latch 1 at the t1 cadence 2026-09-03 11:01:25, divergence state +1 |
| 2026-09-03 11:01:25 | CADENCE | ws29 | t1 gcws30b journey 10:52:00..11:01:20 reached 124.66 past the 95.0 fence, ws1r reversed 11:01:00 during, r 69.11 past the 56.0 fence, stamp 11:01:00, ib 85.0 cross 11:00:30 hold 6 bars, ib dwell 12 bars \| rider ws29 20.78, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 11:01:25 | EXHAUST | ws29 | t4 at a t1 cadence - rider ws29 20.78, no candidate at or below ws37 (the jump bound 8) |

## the 180 s = 36 bar window after each cadence he named | away is `not towards` | the values are emerging

| the cadence | its side | the rung | its first AWAY bar | min from the cadence | away at the window end? | its first reversal bar, the detector | oob at the window end? | its value at the cadence | at the window end |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-03 05:02:55 | high | ws1 | 2026-09-03 05:02:55 | +0.0 | YES | - | no | 33.11 | 15.61 |
| 2026-09-03 05:02:55 | high | ws2 | 2026-09-03 05:02:55 | +0.0 | YES | - | no | 85.71 | 81.62 |
| 2026-09-03 05:02:55 | high | ws3 | - | - | no | 2026-09-03 05:03:30 | YES | 95.43 | 87.33 |
| 2026-09-03 05:29:55 | low | ws1 | 2026-09-03 05:29:55 | +0.0 | YES | 2026-09-03 05:32:30 | no | 61.39 | 81.47 |
| 2026-09-03 05:29:55 | low | ws2 | 2026-09-03 05:29:55 | +0.0 | YES | - | no | 9.50 | 38.07 |
| 2026-09-03 05:29:55 | low | ws3 | 2026-09-03 05:30:50 | +0.9 | YES | - | no | 4.83 | 19.11 |
| 2026-09-03 05:55:00 | high | ws1 | 2026-09-03 05:55:30 | +0.5 | YES | 2026-09-03 05:55:15 | no | 72.17 | 56.10 |
| 2026-09-03 05:55:00 | high | ws2 | 2026-09-03 05:55:00 | +0.0 | no | - | no | 68.09 | 65.27 |
| 2026-09-03 05:55:00 | high | ws3 | - | - | no | - | YES | 96.36 | 96.36 |

| the cadence | its side | ws1..ws3 that reversed in the window | ws1..ws3 away at the end | ws4r oob at the end? | the pattern, by his rule | pxs at the cadence | at the window end | the move over the window | OUTCOME ONLY, never a mech input: the move over the 36 bars past the window |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-03 05:02:55 | high | 1 of 3 | 2 of 3 | ws4r is OUT - his 1101 "remove ws4r" | matryoshka: more than 1 AWAY | 0.160100 | 0.159640 | -0.2873% | +0.0814% |
| 2026-09-03 05:29:55 | low | 1 of 3 | 3 of 3 | ws4r is OUT - his 1101 "remove ws4r" | matryoshka: more than 1 AWAY | 0.157870 | 0.158410 | +0.3421% | +0.3283% |
| 2026-09-03 05:55:00 | high | 1 of 3 | 1 of 3 | ws4r is OUT - his 1101 "remove ws4r" | not met: 1 or fewer AWAY | 0.160190 | 0.160320 | +0.0812% | -0.1684% |
