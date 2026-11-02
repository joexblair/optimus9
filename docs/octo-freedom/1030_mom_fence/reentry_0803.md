# LINEAGE2 BATON CHAIN - THE ARM IS HANDED IN AT 2026-08-03 00:34:45, SIDE high
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
| 2026-08-03 00:34:45 | ARM | - | - | - | arm_at 2026-08-03 00:34:45 - the arm race is skipped, this bar IS the arm |
| 2026-08-03 00:34:50 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-03 00:42:25 | HOLD | - | - | - | ws1..ws2 is lin_hop 2 reach from rider ws0 and 1 of it is ex-fence and printing towards at a t1 cadence - ws2 99.33 - the tests are concluded and the walk goes to the next cadence |
| 2026-08-03 03:20:25 | RIDER | ws6 | - | - | t1 gcws30b journey 03:18:00..03:20:20 reached 96.44 past the 95.0 fence, ws1r reversed 03:20:00 during, r 69.86 past the 56.0 fence, stamp 03:20:00, ib 85.0 cross 03:19:30 hold 6 bars, ib dwell 12 bars \| ws6 r 83.76 picked up at a cadence, no prior rider |
| 2026-08-03 03:38:40 | BATON | ws6 | ws8 | ws8 82.28 | ws6 -> ws8, between cadences, lin_hop 2 |
| 2026-08-03 03:47:20 | BATON | ws8 | ws10 | ws9 75.95, ws10 77.59 | ws8 -> ws10, between cadences, lin_hop 2 |
| 2026-08-03 03:59:55 | NO PASS | ws10 | - | none offered | ws10 80.11 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 04:24:55 | HOLD | ws10 | - | - | ws11..ws12 is lin_hop 2 reach from rider ws10 and 2 of it is ex-fence and printing towards at a t1 cadence - ws11 91.61, ws12 89.08 - the tests are concluded and the walk goes to the next cadence |
| 2026-08-03 04:42:35 | BATON | ws10 | ws12 | ws11 92.51, ws12 89.08 | ws10 -> ws12, between cadences, lin_hop 2 |
| 2026-08-03 04:48:50 | BATON | ws12 | ws14 | ws13 86.09, ws14 89.49 | ws12 -> ws14, between cadences, lin_hop 2 |
| 2026-08-03 04:54:55 | BATON | ws14 | ws16 | ws15 83.60, ws16 86.79 | ws14 -> ws16, between cadences, lin_hop 2 |
| 2026-08-03 04:59:25 | BATON | ws16 | ws18 | ws17 87.67, ws18 86.81 | ws16 -> ws18, between cadences, lin_hop 2 |
| 2026-08-03 05:10:15 | BATON | ws18 | ws19 | ws19 82.58 | ws18 -> ws19, between cadences, lin_hop 2 |
| 2026-08-03 05:10:20 | NO PASS | ws19 | - | none offered | ws19 82.58 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 06:05:55 | CADENCE | ws19 | - | ws24 84.51, ws25 78.77 | t1 gcws30b journey 05:57:30..06:05:50 reached 140.20 past the 95.0 fence, ws1r reversed 06:05:00 during, r 76.68 past the 56.0 fence, stamp 06:05:00, ib 85.0 cross 06:05:00 hold 6 bars, ib dwell 12 bars \| rider ws19 77.75, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-03 06:05:55 | BATON | ws19 | ws25 | ws24 84.51, ws25 78.77 | ws19 -> ws25, at a t1 cadence, capped at ws27 by the jump bound 8 |
| 2026-08-03 06:37:20 | BATON | ws25 | ws27 | ws27 75.87 | ws25 -> ws27, between cadences, lin_hop 2 |
| 2026-08-03 06:40:05 | BATON | ws27 | ws29 | ws28 71.81, ws29 80.32 | ws27 -> ws29, between cadences, lin_hop 2 |
| 2026-08-03 06:47:00 | BATON | ws29 | ws30 | ws30 76.31 | ws29 -> ws30, between cadences, lin_hop 2 |
| 2026-08-03 07:00:55 | NO PASS | ws30 | - | none offered | ws30 68.29 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 07:29:00 | CADENCE | ws30 | - | none offered | t1 gcws30b journey 07:24:00..07:27:50 reached 100.27 past the 95.0 fence, back inside the 85.0 ib fence 07:27:00, ws1r reversed 07:29:00 inside the 120s grace from the cross bar 07:27:00, r 82.07 past the 56.0 fence, stamp 07:29:00, hold 6 bars, ib dwell 12 bars \| rider ws30 74.42, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-03 07:29:00 | HOLD | ws30 | - | - | rider ws30 74.42 ex-fence and not reversed - no action |
| 2026-08-03 07:30:10 | NO PASS | ws30 | - | none offered | ws30 67.82 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 07:38:00 | CADENCE | ws30 | - | none offered | t1 gcws30b journey 07:33:00..07:37:20 reached 100.94 past the 95.0 fence, back inside the 85.0 ib fence 07:36:30, ws1r reversed 07:38:00 inside the 120s grace from the cross bar 07:36:30, r 60.97 past the 56.0 fence, stamp 07:38:00, hold 6 bars, ib dwell 12 bars \| rider ws30 71.49, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-03 07:38:00 | TOP RESET | ws30 | ws4 | ws3 88.94, ws4 79.14 | ws30 71.49 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws4 |
| 2026-08-03 07:45:05 | BATON | ws4 | ws6 | ws6 80.38 | ws4 -> ws6, between cadences, lin_hop 2 |
| 2026-08-03 08:00:55 | NO PASS | ws6 | - | none offered | ws6 69.00 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 08:12:25 | HOLD | ws6 | - | - | ws7..ws8 is lin_hop 2 reach from rider ws6 and 1 of it is ex-fence and printing towards at a t1 cadence - ws8 82.10 - the tests are concluded and the walk goes to the next cadence |
| 2026-08-03 09:07:55 | CADENCE | ws6 | - | ws10 76.41, ws14 80.04 | t1 gcws30b journey 08:55:30..09:07:50 reached 117.19 past the 95.0 fence, ws1r reversed 09:03:00 during, r 82.80 past the 56.0 fence, stamp 09:03:00, ib 85.0 cross 09:07:00 hold 6 bars, ib dwell 12 bars \| rider ws6 92.50, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-03 09:07:55 | BATON | ws6 | ws14 | ws10 76.41, ws14 80.04 | ws6 -> ws14, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-08-03 09:41:25 | HOLD | ws14 | - | - | ws15..ws16 is lin_hop 2 reach from rider ws14 and 2 of it is ex-fence and printing towards at a t1 cadence - ws15 85.70, ws16 83.05 - the tests are concluded and the walk goes to the next cadence |
| 2026-08-03 09:56:55 | HOLD | ws14 | - | - | ws15..ws16 is lin_hop 2 reach from rider ws14 and 2 of it is ex-fence and printing towards at a t1 cadence - ws15 85.70, ws16 83.20 - the tests are concluded and the walk goes to the next cadence |
| 2026-08-03 10:16:55 | BATON | ws14 | ws16 | ws16 90.01 | ws14 -> ws16, between cadences, lin_hop 2 |
| 2026-08-03 10:25:00 | BATON | ws16 | ws18 | ws17 91.01, ws18 89.57 | ws16 -> ws18, between cadences, lin_hop 2 |
| 2026-08-03 10:30:55 | BATON | ws18 | ws19 | ws19 81.20 | ws18 -> ws19, between cadences, lin_hop 2 |
| 2026-08-03 10:47:00 | BATON | ws19 | ws21 | ws21 77.09 | ws19 -> ws21, between cadences, lin_hop 2 |
| 2026-08-03 10:51:55 | NO PASS | ws21 | - | none offered | ws21 63.13 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 12:13:55 | CADENCE | ws21 | - | none offered | t1 gcws30b journey 12:09:00..12:13:50 reached 116.42 past the 95.0 fence, ws1r reversed 12:12:00 during, r 90.25 past the 56.0 fence, stamp 12:12:00, ib 85.0 cross 12:13:00 hold 6 bars, ib dwell 12 bars \| rider ws21 24.29, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-03 12:13:55 | EXHAUST | ws21 | - | - | exhaust at a t1 cadence - rider ws21 24.29, no candidate at or below ws29 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-03 12:13:55 |
| baton passes made | 17 |
| minutes from the arm to the verdict | 699.2 |
| the rider chain | ws6 > ws8 > ws10 > ws12 > ws14 > ws16 > ws18 > ws19 > ws25 > ws27 > ws29 > ws30 > ws4 > ws6 > ws14 > ws16 > ws18 > ws19 > ws21 |

## MODE 'reversal' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-08-03 00:34:45 | ARM | - | - | - | arm_at 2026-08-03 00:34:45 - the arm race is skipped, this bar IS the arm |
| 2026-08-03 00:34:50 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-03 00:42:25 | HOLD | - | - | - | ws1..ws2 is lin_hop 2 reach from rider ws0 and 1 of it is ex-fence and printing towards at a t1 cadence - ws2 99.33 - the tests are concluded and the walk goes to the next cadence |
| 2026-08-03 03:20:25 | RIDER | ws6 | - | - | t1 gcws30b journey 03:18:00..03:20:20 reached 96.44 past the 95.0 fence, ws1r reversed 03:20:00 during, r 69.86 past the 56.0 fence, stamp 03:20:00, ib 85.0 cross 03:19:30 hold 6 bars, ib dwell 12 bars \| ws6 r 83.76 picked up at a cadence, no prior rider |
| 2026-08-03 03:21:55 | NO PASS | ws6 | - | none offered | ws6 82.36 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 04:24:55 | CADENCE | ws6 | - | ws9 85.43, ws10 84.07, ws11 91.61, ws12 89.08, ws13 94.87, ws14 90.26 | t1 gcws30b journey 04:21:00..04:24:50 reached 100.43 past the 95.0 fence, ws1r reversed 04:24:00 during, r 62.08 past the 56.0 fence, stamp 04:24:00, ib 85.0 cross 04:24:00 hold 6 bars, ib dwell 12 bars \| rider ws6 82.53, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-03 04:24:55 | BATON | ws6 | ws14 | ws9 85.43, ws10 84.07, ws11 91.61, ws12 89.08, ws13 94.87, ws14 90.26 | ws6 -> ws14, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-08-03 04:28:55 | BATON | ws14 | ws15 | ws15 91.06 | ws14 -> ws15, between cadences, lin_hop 2 |
| 2026-08-03 04:46:05 | BATON | ws15 | ws16 | ws16 94.30 | ws15 -> ws16, between cadences, lin_hop 2 |
| 2026-08-03 04:49:15 | BATON | ws16 | ws18 | ws17 93.08, ws18 93.28 | ws16 -> ws18, between cadences, lin_hop 2 |
| 2026-08-03 04:53:10 | NO PASS | ws18 | - | none offered | ws18 90.20 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 06:05:55 | HOLD | ws18 | - | - | ws19..ws20 is lin_hop 2 reach from rider ws18 and 1 of it is ex-fence and printing towards at a t1 cadence - ws19 77.75 - the tests are concluded and the walk goes to the next cadence |
| 2026-08-03 06:19:30 | BATON | ws18 | ws19 | ws19 74.19 | ws18 -> ws19, between cadences, lin_hop 2 |
| 2026-08-03 07:25:10 | NO PASS | ws19 | - | none offered | ws19 39.39 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 07:29:00 | CADENCE | ws19 | - | none offered | t1 gcws30b journey 07:24:00..07:27:50 reached 100.27 past the 95.0 fence, back inside the 85.0 ib fence 07:27:00, ws1r reversed 07:29:00 inside the 120s grace from the cross bar 07:27:00, r 82.07 past the 56.0 fence, stamp 07:29:00, hold 6 bars, ib dwell 12 bars \| rider ws19 38.28, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-03 07:29:00 | EXHAUST | ws19 | - | - | t4 at a t1 cadence - rider ws19 38.28, no candidate at or below ws27 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-03 07:29:00 |
| baton passes made | 5 |
| minutes from the arm to the verdict | 414.2 |
| the rider chain | ws6 > ws14 > ws15 > ws16 > ws18 > ws19 |

## MODE 'reversal+quarter' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-08-03 00:34:45 | ARM | - | - | - | arm_at 2026-08-03 00:34:45 - the arm race is skipped, this bar IS the arm |
| 2026-08-03 00:34:50 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-03 00:42:25 | HOLD | - | - | - | ws1..ws2 is lin_hop 2 reach from rider ws0 and 1 of it is ex-fence and printing towards at a t1 cadence - ws2 99.33 - the tests are concluded and the walk goes to the next cadence |
| 2026-08-03 03:20:25 | RIDER | ws6 | - | - | t1 gcws30b journey 03:18:00..03:20:20 reached 96.44 past the 95.0 fence, ws1r reversed 03:20:00 during, r 69.86 past the 56.0 fence, stamp 03:20:00, ib 85.0 cross 03:19:30 hold 6 bars, ib dwell 12 bars \| ws6 r 83.76 picked up at a cadence, no prior rider |
| 2026-08-03 03:22:30 | NO PASS | ws6 | - | none offered | ws6 81.12 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 04:24:55 | CADENCE | ws6 | - | ws9 85.43, ws10 84.07, ws11 91.61, ws12 89.08, ws13 94.87, ws14 90.26 | t1 gcws30b journey 04:21:00..04:24:50 reached 100.43 past the 95.0 fence, ws1r reversed 04:24:00 during, r 62.08 past the 56.0 fence, stamp 04:24:00, ib 85.0 cross 04:24:00 hold 6 bars, ib dwell 12 bars \| rider ws6 82.53, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-03 04:24:55 | BATON | ws6 | ws14 | ws9 85.43, ws10 84.07, ws11 91.61, ws12 89.08, ws13 94.87, ws14 90.26 | ws6 -> ws14, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-08-03 04:31:30 | BATON | ws14 | ws15 | ws15 92.71 | ws14 -> ws15, between cadences, lin_hop 2 |
| 2026-08-03 04:48:55 | BATON | ws15 | ws16 | ws16 92.50 | ws15 -> ws16, between cadences, lin_hop 2 |
| 2026-08-03 04:52:20 | BATON | ws16 | ws18 | ws17 90.73, ws18 90.34 | ws16 -> ws18, between cadences, lin_hop 2 |
| 2026-08-03 04:56:45 | NO PASS | ws18 | - | none offered | ws18 88.54 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 06:05:55 | HOLD | ws18 | - | - | ws19..ws20 is lin_hop 2 reach from rider ws18 and 1 of it is ex-fence and printing towards at a t1 cadence - ws19 77.75 - the tests are concluded and the walk goes to the next cadence |
| 2026-08-03 06:23:05 | NO PASS | ws18 | - | none offered | ws18 70.64 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 07:29:00 | CADENCE | ws18 | - | none offered | t1 gcws30b journey 07:24:00..07:27:50 reached 100.27 past the 95.0 fence, back inside the 85.0 ib fence 07:27:00, ws1r reversed 07:29:00 inside the 120s grace from the cross bar 07:27:00, r 82.07 past the 56.0 fence, stamp 07:29:00, hold 6 bars, ib dwell 12 bars \| rider ws18 48.01, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-03 07:29:00 | EXHAUST | ws18 | - | - | t4 at a t1 cadence - rider ws18 48.01, no candidate at or below ws26 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-03 07:29:00 |
| baton passes made | 4 |
| minutes from the arm to the verdict | 414.2 |
| the rider chain | ws6 > ws14 > ws15 > ws16 > ws18 |

## MODE 'ib' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-08-03 00:34:45 | ARM | - | arm_at 2026-08-03 00:34:45 - the arm race is skipped, this bar IS the arm |
| 2026-08-03 00:34:50 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-03 00:34:45 | RETEST | - | ws1r 79.10 is not oob at the arm - the gate stays shut |
| 2026-08-03 00:42:25 | HOLD | - | ws1..ws2 is lin_hop 2 reach from rider ws0 and 1 of it is ex-fence and printing towards at a t1 cadence - ws2 99.33 - the tests are concluded and the walk goes to the next cadence |
| 2026-08-03 03:20:25 | RIDER | ws6 | t1 gcws30b journey 03:18:00..03:20:20 reached 96.44 past the 95.0 fence, ws1r reversed 03:20:00 during, r 69.86 past the 56.0 fence, stamp 03:20:00, ib 85.0 cross 03:19:30 hold 6 bars, ib dwell 12 bars \| ws6 r 83.76 picked up at a cadence, no prior rider |
| 2026-08-03 03:38:40 | BATON | ws6 | ws6 -> ws8, between cadences, lin_hop 2 |
| 2026-08-03 03:47:20 | BATON | ws8 | ws8 -> ws10, between cadences, lin_hop 2 |
| 2026-08-03 03:59:55 | NO PASS | ws10 | ws10 80.11 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 04:24:55 | LATCH1 | ws10 | latch 1 at the t1 cadence 2026-08-03 04:24:55, divergence state +1 |
| 2026-08-03 04:24:55 | HOLD | ws10 | ws11..ws12 is lin_hop 2 reach from rider ws10 and 2 of it is ex-fence and printing towards at a t1 cadence - ws11 91.61, ws12 89.08 - the tests are concluded and the walk goes to the next cadence |
| 2026-08-03 04:42:35 | BATON | ws10 | ws10 -> ws12, between cadences, lin_hop 2 |
| 2026-08-03 04:48:50 | BATON | ws12 | ws12 -> ws14, between cadences, lin_hop 2 |
| 2026-08-03 04:54:55 | BATON | ws14 | ws14 -> ws16, between cadences, lin_hop 2 |
| 2026-08-03 04:59:25 | BATON | ws16 | ws16 -> ws18, between cadences, lin_hop 2 |
| 2026-08-03 05:10:15 | BATON | ws18 | ws18 -> ws19, between cadences, lin_hop 2 |
| 2026-08-03 05:10:20 | NO PASS | ws19 | ws19 82.58 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 06:05:55 | LATCH1 | ws19 | latch 1 at the t1 cadence 2026-08-03 06:05:55, divergence state +1 |
| 2026-08-03 06:05:55 | CADENCE | ws19 | t1 gcws30b journey 05:57:30..06:05:50 reached 140.20 past the 95.0 fence, ws1r reversed 06:05:00 during, r 76.68 past the 56.0 fence, stamp 06:05:00, ib 85.0 cross 06:05:00 hold 6 bars, ib dwell 12 bars \| rider ws19 77.75, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-03 06:05:55 | BATON | ws19 | ws19 -> ws25, at a t1 cadence, capped at ws27 by the jump bound 8 |
| 2026-08-03 06:37:20 | BATON | ws25 | ws25 -> ws27, between cadences, lin_hop 2 |
| 2026-08-03 06:40:05 | BATON | ws27 | ws27 -> ws29, between cadences, lin_hop 2 |
| 2026-08-03 06:47:00 | BATON | ws29 | ws29 -> ws30, between cadences, lin_hop 2 |
| 2026-08-03 07:00:55 | NO PASS | ws30 | ws30 68.29 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 07:29:00 | CADENCE | ws30 | t1 gcws30b journey 07:24:00..07:27:50 reached 100.27 past the 95.0 fence, back inside the 85.0 ib fence 07:27:00, ws1r reversed 07:29:00 inside the 120s grace from the cross bar 07:27:00, r 82.07 past the 56.0 fence, stamp 07:29:00, hold 6 bars, ib dwell 12 bars \| rider ws30 74.42, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-03 07:29:00 | HOLD | ws30 | rider ws30 74.42 ex-fence and not reversed - no action |
| 2026-08-03 07:30:10 | NO PASS | ws30 | ws30 67.82 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 07:38:00 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-03 07:38:00, divergence state +1 |
| 2026-08-03 07:38:00 | CADENCE | ws30 | t1 gcws30b journey 07:33:00..07:37:20 reached 100.94 past the 95.0 fence, back inside the 85.0 ib fence 07:36:30, ws1r reversed 07:38:00 inside the 120s grace from the cross bar 07:36:30, r 60.97 past the 56.0 fence, stamp 07:38:00, hold 6 bars, ib dwell 12 bars \| rider ws30 71.49, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-03 07:38:00 | TOP RESET | ws30 | ws30 71.49 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws4 |
| 2026-08-03 07:45:05 | BATON | ws4 | ws4 -> ws6, between cadences, lin_hop 2 |
| 2026-08-03 08:00:55 | NO PASS | ws6 | ws6 69.00 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 08:12:25 | LATCH1 | ws6 | latch 1 at the t1 cadence 2026-08-03 08:12:25, divergence state +1 |
| 2026-08-03 08:12:25 | HOLD | ws6 | ws7..ws8 is lin_hop 2 reach from rider ws6 and 1 of it is ex-fence and printing towards at a t1 cadence - ws8 82.10 - the tests are concluded and the walk goes to the next cadence |
| 2026-08-03 09:07:55 | LATCH1 | ws6 | latch 1 at the t1 cadence 2026-08-03 09:07:55, divergence state +1 |
| 2026-08-03 09:07:55 | CADENCE | ws6 | t1 gcws30b journey 08:55:30..09:07:50 reached 117.19 past the 95.0 fence, ws1r reversed 09:03:00 during, r 82.80 past the 56.0 fence, stamp 09:03:00, ib 85.0 cross 09:07:00 hold 6 bars, ib dwell 12 bars \| rider ws6 92.50, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-03 09:07:55 | BATON | ws6 | ws6 -> ws14, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-08-03 09:41:25 | LATCH1 | ws14 | latch 1 at the t1 cadence 2026-08-03 09:41:25, divergence state +1 |
| 2026-08-03 09:41:25 | HOLD | ws14 | ws15..ws16 is lin_hop 2 reach from rider ws14 and 2 of it is ex-fence and printing towards at a t1 cadence - ws15 85.70, ws16 83.05 - the tests are concluded and the walk goes to the next cadence |
| 2026-08-03 09:56:55 | LATCH1 | ws14 | latch 1 at the t1 cadence 2026-08-03 09:56:55, divergence state +1 |
| 2026-08-03 09:56:55 | HOLD | ws14 | ws15..ws16 is lin_hop 2 reach from rider ws14 and 2 of it is ex-fence and printing towards at a t1 cadence - ws15 85.70, ws16 83.20 - the tests are concluded and the walk goes to the next cadence |
| 2026-08-03 10:16:55 | BATON | ws14 | ws14 -> ws16, between cadences, lin_hop 2 |
| 2026-08-03 10:25:00 | BATON | ws16 | ws16 -> ws18, between cadences, lin_hop 2 |
| 2026-08-03 10:30:55 | BATON | ws18 | ws18 -> ws19, between cadences, lin_hop 2 |
| 2026-08-03 10:47:00 | BATON | ws19 | ws19 -> ws21, between cadences, lin_hop 2 |
| 2026-08-03 10:51:55 | NO PASS | ws21 | ws21 63.13 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 12:13:55 | LATCH1 | ws21 | latch 1 at the t1 cadence 2026-08-03 12:13:55, divergence state +1 |
| 2026-08-03 12:13:55 | CADENCE | ws21 | t1 gcws30b journey 12:09:00..12:13:50 reached 116.42 past the 95.0 fence, ws1r reversed 12:12:00 during, r 90.25 past the 56.0 fence, stamp 12:12:00, ib 85.0 cross 12:13:00 hold 6 bars, ib dwell 12 bars \| rider ws21 24.29, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-03 12:13:55 | EXHAUST | ws21 | exhaust at a t1 cadence - rider ws21 24.29, no candidate at or below ws29 (the jump bound 8) |

## MODE 'reversal' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-08-03 00:34:45 | ARM | - | arm_at 2026-08-03 00:34:45 - the arm race is skipped, this bar IS the arm |
| 2026-08-03 00:34:50 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-03 00:34:45 | RETEST | - | ws1r 79.10 is not oob at the arm - the gate stays shut |
| 2026-08-03 00:42:25 | HOLD | - | ws1..ws2 is lin_hop 2 reach from rider ws0 and 1 of it is ex-fence and printing towards at a t1 cadence - ws2 99.33 - the tests are concluded and the walk goes to the next cadence |
| 2026-08-03 03:20:25 | RIDER | ws6 | t1 gcws30b journey 03:18:00..03:20:20 reached 96.44 past the 95.0 fence, ws1r reversed 03:20:00 during, r 69.86 past the 56.0 fence, stamp 03:20:00, ib 85.0 cross 03:19:30 hold 6 bars, ib dwell 12 bars \| ws6 r 83.76 picked up at a cadence, no prior rider |
| 2026-08-03 03:21:55 | NO PASS | ws6 | ws6 82.36 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 04:24:55 | LATCH1 | ws6 | latch 1 at the t1 cadence 2026-08-03 04:24:55, divergence state +1 |
| 2026-08-03 04:24:55 | CADENCE | ws6 | t1 gcws30b journey 04:21:00..04:24:50 reached 100.43 past the 95.0 fence, ws1r reversed 04:24:00 during, r 62.08 past the 56.0 fence, stamp 04:24:00, ib 85.0 cross 04:24:00 hold 6 bars, ib dwell 12 bars \| rider ws6 82.53, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-03 04:24:55 | BATON | ws6 | ws6 -> ws14, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-08-03 04:28:55 | BATON | ws14 | ws14 -> ws15, between cadences, lin_hop 2 |
| 2026-08-03 04:46:05 | BATON | ws15 | ws15 -> ws16, between cadences, lin_hop 2 |
| 2026-08-03 04:49:15 | BATON | ws16 | ws16 -> ws18, between cadences, lin_hop 2 |
| 2026-08-03 04:53:10 | NO PASS | ws18 | ws18 90.20 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 06:05:55 | LATCH1 | ws18 | latch 1 at the t1 cadence 2026-08-03 06:05:55, divergence state +1 |
| 2026-08-03 06:05:55 | HOLD | ws18 | ws19..ws20 is lin_hop 2 reach from rider ws18 and 1 of it is ex-fence and printing towards at a t1 cadence - ws19 77.75 - the tests are concluded and the walk goes to the next cadence |
| 2026-08-03 06:19:30 | BATON | ws18 | ws18 -> ws19, between cadences, lin_hop 2 |
| 2026-08-03 07:25:10 | NO PASS | ws19 | ws19 39.39 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 07:29:00 | CADENCE | ws19 | t1 gcws30b journey 07:24:00..07:27:50 reached 100.27 past the 95.0 fence, back inside the 85.0 ib fence 07:27:00, ws1r reversed 07:29:00 inside the 120s grace from the cross bar 07:27:00, r 82.07 past the 56.0 fence, stamp 07:29:00, hold 6 bars, ib dwell 12 bars \| rider ws19 38.28, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-03 07:29:00 | EXHAUST | ws19 | t4 at a t1 cadence - rider ws19 38.28, no candidate at or below ws27 (the jump bound 8) |

## MODE 'reversal+quarter' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-08-03 00:34:45 | ARM | - | arm_at 2026-08-03 00:34:45 - the arm race is skipped, this bar IS the arm |
| 2026-08-03 00:34:50 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-03 00:34:45 | RETEST | - | ws1r 79.10 is not oob at the arm - the gate stays shut |
| 2026-08-03 00:42:25 | HOLD | - | ws1..ws2 is lin_hop 2 reach from rider ws0 and 1 of it is ex-fence and printing towards at a t1 cadence - ws2 99.33 - the tests are concluded and the walk goes to the next cadence |
| 2026-08-03 03:20:25 | RIDER | ws6 | t1 gcws30b journey 03:18:00..03:20:20 reached 96.44 past the 95.0 fence, ws1r reversed 03:20:00 during, r 69.86 past the 56.0 fence, stamp 03:20:00, ib 85.0 cross 03:19:30 hold 6 bars, ib dwell 12 bars \| ws6 r 83.76 picked up at a cadence, no prior rider |
| 2026-08-03 03:22:30 | NO PASS | ws6 | ws6 81.12 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 04:24:55 | LATCH1 | ws6 | latch 1 at the t1 cadence 2026-08-03 04:24:55, divergence state +1 |
| 2026-08-03 04:24:55 | CADENCE | ws6 | t1 gcws30b journey 04:21:00..04:24:50 reached 100.43 past the 95.0 fence, ws1r reversed 04:24:00 during, r 62.08 past the 56.0 fence, stamp 04:24:00, ib 85.0 cross 04:24:00 hold 6 bars, ib dwell 12 bars \| rider ws6 82.53, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-03 04:24:55 | BATON | ws6 | ws6 -> ws14, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-08-03 04:31:30 | BATON | ws14 | ws14 -> ws15, between cadences, lin_hop 2 |
| 2026-08-03 04:48:55 | BATON | ws15 | ws15 -> ws16, between cadences, lin_hop 2 |
| 2026-08-03 04:52:20 | BATON | ws16 | ws16 -> ws18, between cadences, lin_hop 2 |
| 2026-08-03 04:56:45 | NO PASS | ws18 | ws18 88.54 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 06:05:55 | LATCH1 | ws18 | latch 1 at the t1 cadence 2026-08-03 06:05:55, divergence state +1 |
| 2026-08-03 06:05:55 | HOLD | ws18 | ws19..ws20 is lin_hop 2 reach from rider ws18 and 1 of it is ex-fence and printing towards at a t1 cadence - ws19 77.75 - the tests are concluded and the walk goes to the next cadence |
| 2026-08-03 06:23:05 | NO PASS | ws18 | ws18 70.64 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-03 07:29:00 | CADENCE | ws18 | t1 gcws30b journey 07:24:00..07:27:50 reached 100.27 past the 95.0 fence, back inside the 85.0 ib fence 07:27:00, ws1r reversed 07:29:00 inside the 120s grace from the cross bar 07:27:00, r 82.07 past the 56.0 fence, stamp 07:29:00, hold 6 bars, ib dwell 12 bars \| rider ws18 48.01, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-03 07:29:00 | EXHAUST | ws18 | t4 at a t1 cadence - rider ws18 48.01, no candidate at or below ws26 (the jump bound 8) |
