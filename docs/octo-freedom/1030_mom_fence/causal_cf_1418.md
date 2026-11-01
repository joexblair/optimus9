# LINEAGE2 BATON CHAIN - THE ARM IS HANDED IN AT 2026-08-14 06:59:00, SIDE low
# TAPE 1632960 bars | B 2026-08-14 14:18:00, the last tape bar, no end bound | RULED_OK False

| the setting | value | what it is |
|---|---|---|
| the r fence | 75.0 -> (25.0, 75.0) | his 25/75 |
| the ladder top | ws30 | his max-lineage-TF ws30 |
| the per-line ex-fence latch | ON | his "latch enabled" |
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
| 2026-08-14 06:59:00 | ARM | - | - | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 07:03:05 | RIDER | ws8 | - | - | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:03:05 | CADENCE | ws8 | - | ws9 13.11, ws11 24.61 | t1 ws1b oob 06:59:40..07:02:05, ws1r reversed 07:00:55 during, stamp 07:00:55 \| rider ws8 4.46, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 07:03:05 | BATON | ws8 | ws11 | ws9 13.11, ws11 24.61 | ws8 -> ws11, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:15:10 | CADENCE | ws11 | - | ws12 13.90, ws13 20.95, ws14 16.88, ws16 22.31 | t1 ws1b oob 07:13:35..07:14:10, ws1r reversed 07:14:00 during, stamp 07:14:00 \| rider ws11 9.10, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:15:10 | BATON | ws11 | ws16 | ws12 13.90, ws13 20.95, ws14 16.88, ws16 22.31 | ws11 -> ws16, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 07:35:30 | CADENCE | ws16 | - | ws17 16.07, ws18 18.32 | t1 ws1b oob 07:32:15..07:34:30, ws1r reversed 07:34:30 during, stamp 07:34:30 \| rider ws16 9.72, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 07:35:30 | BATON | ws16 | ws18 | ws17 16.07, ws18 18.32 | ws16 -> ws18, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:47:20 | CADENCE | ws18 | - | ws19 15.43, ws20 22.92, ws21 15.06, ws22 16.37 | t1 ws1b ib 07:45:30, ws1r reversed 07:47:20 inside the 120s grace, stamp 07:47:20 \| rider ws18 17.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:47:20 | BATON | ws18 | ws22 | ws19 15.43, ws20 22.92, ws21 15.06, ws22 16.37 | ws18 -> ws22, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 08:10:00 | BATON | ws22 | ws24 | ws23 19.09, ws24 20.02 | ws22 -> ws24, between cadences, lin_hop 2 |
| 2026-08-14 08:30:10 | NO PASS | ws24 | - | none offered | ws24 7.89 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:11:50 | CADENCE | ws24 | - | ws27 10.12, ws28 1.10, ws29 20.58, ws30 6.12 | t1 ws1b oob 09:07:15..09:10:50, ws1r reversed 09:10:25 during, stamp 09:10:25 \| rider ws24 4.84, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:11:50 | BATON | ws24 | ws30 | ws27 10.12, ws28 1.10, ws29 20.58, ws30 6.12 | ws24 -> ws30, at a t1 cadence, capped at ws32 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 09:14:10 | NO PASS | ws30 | - | none offered | ws30 9.90 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:31:50 | CADENCE | ws30 | - | none offered | t1 ws1b ib 09:30:55, ws1r reversed 09:31:20 inside the 120s grace, stamp 09:31:20 \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:31:50 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:40 | NO PASS | ws30 | - | none offered | ws30 18.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:42:10 | CADENCE | ws30 | - | none offered | t1 ws1b ib 10:41:15, ws1r reversed 10:41:20 inside the 120s grace, stamp 10:41:20 \| rider ws30 27.07, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:42:10 | TOP RESET | ws30 | ws7 | ws1 34.77, ws2 8.34, ws3 7.09, ws7 67.48 | ws30 27.07 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws7 |
| 2026-08-14 10:52:05 | CADENCE | ws7 | - | none offered | t1 ws1b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, stamp 10:48:55 \| rider ws7 44.37, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 10:52:05 | HOLD | ws7 | - | - | rider ws7 44.37 ex-fence and not reversed - no action |
| 2026-08-14 11:17:45 | CADENCE | ws7 | - | ws8 11.35, ws9 15.39 | t1 ws1b oob 11:09:10..11:16:45, ws1r reversed 11:15:20 during, stamp 11:15:20 \| rider ws7 2.07, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 11:17:45 | BATON | ws7 | ws9 | ws8 11.35, ws9 15.39 | ws7 -> ws9, at a t1 cadence, capped at ws15 by the jump bound 8 |
| 2026-08-14 11:19:20 | NO PASS | ws9 | - | none offered | ws9 18.29 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:24:10 | CADENCE | ws9 | - | ws14 37.10, ws16 21.56, ws17 14.34 | t1 ws1b oob 12:11:10..12:23:10, ws1r reversed 12:15:35 during, stamp 12:15:35 \| rider ws9 72.63, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:24:10 | BATON | ws9 | ws17 | ws14 37.10, ws16 21.56, ws17 14.34 | ws9 -> ws17, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-08-14 12:25:20 | BATON | ws17 | ws19 | ws18 17.15, ws19 26.61 | ws17 -> ws19, between cadences, lin_hop 2 |
| 2026-08-14 12:50:25 | NO PASS | ws19 | - | none offered | ws19 28.56 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:18:00 | CADENCE | ws19 | - | none offered | t1 ws1b oob 14:11:25..14:17:00, ws1r reversed 14:16:45 during, stamp 14:16:45 \| rider ws19 63.66, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:18:00 | EXHAUST | ws19 | - | - | t4 at a t1 cadence - rider ws19 63.66, no candidate at or below ws27 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-14 14:18:00 |
| baton passes made | 9 |
| minutes from the arm to the verdict | 439.0 |
| the rider chain | ws8 > ws11 > ws16 > ws18 > ws22 > ws24 > ws30 > ws7 > ws9 > ws17 > ws19 |

## MODE 'reversal' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | - | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 07:03:05 | RIDER | ws8 | - | - | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:03:05 | CADENCE | ws8 | - | ws9 13.11, ws11 24.61 | t1 ws1b oob 06:59:40..07:02:05, ws1r reversed 07:00:55 during, stamp 07:00:55 \| rider ws8 4.46, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 07:03:05 | BATON | ws8 | ws11 | ws9 13.11, ws11 24.61 | ws8 -> ws11, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:15:10 | CADENCE | ws11 | - | ws12 13.90, ws13 20.95, ws14 16.88, ws16 22.31 | t1 ws1b oob 07:13:35..07:14:10, ws1r reversed 07:14:00 during, stamp 07:14:00 \| rider ws11 9.10, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:15:10 | BATON | ws11 | ws16 | ws12 13.90, ws13 20.95, ws14 16.88, ws16 22.31 | ws11 -> ws16, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 07:35:30 | CADENCE | ws16 | - | ws17 16.07, ws18 18.32 | t1 ws1b oob 07:32:15..07:34:30, ws1r reversed 07:34:30 during, stamp 07:34:30 \| rider ws16 9.72, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 07:35:30 | BATON | ws16 | ws18 | ws17 16.07, ws18 18.32 | ws16 -> ws18, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:47:20 | CADENCE | ws18 | - | ws19 15.43, ws20 22.92, ws21 15.06, ws22 16.37 | t1 ws1b ib 07:45:30, ws1r reversed 07:47:20 inside the 120s grace, stamp 07:47:20 \| rider ws18 17.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:47:20 | BATON | ws18 | ws22 | ws19 15.43, ws20 22.92, ws21 15.06, ws22 16.37 | ws18 -> ws22, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 07:50:10 | NO PASS | ws22 | - | none offered | ws22 19.89 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:11:50 | CADENCE | ws22 | - | ws23 20.09, ws24 4.84, ws27 10.12, ws28 1.10, ws29 20.58, ws30 6.12 | t1 ws1b oob 09:07:15..09:10:50, ws1r reversed 09:10:25 during, stamp 09:10:25 \| rider ws22 36.57, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:11:50 | BATON | ws22 | ws30 | ws23 20.09, ws24 4.84, ws27 10.12, ws28 1.10, ws29 20.58, ws30 6.12 | ws22 -> ws30, at a t1 cadence, capped at ws30 by the jump bound 8 |
| 2026-08-14 09:14:30 | NO PASS | ws30 | - | none offered | ws30 10.59 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:31:50 | CADENCE | ws30 | - | none offered | t1 ws1b ib 09:30:55, ws1r reversed 09:31:20 inside the 120s grace, stamp 09:31:20 \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:31:50 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:10 | NO PASS | ws30 | - | none offered | ws30 16.80 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:42:10 | CADENCE | ws30 | - | none offered | t1 ws1b ib 10:41:15, ws1r reversed 10:41:20 inside the 120s grace, stamp 10:41:20 \| rider ws30 27.07, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:42:10 | TOP RESET | ws30 | ws7 | ws1 34.77, ws2 8.34, ws3 7.09, ws7 67.48 | ws30 27.07 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws7 |
| 2026-08-14 10:52:05 | CADENCE | ws7 | - | none offered | t1 ws1b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, stamp 10:48:55 \| rider ws7 44.37, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 10:52:05 | HOLD | ws7 | - | - | rider ws7 44.37 ex-fence and not reversed - no action |
| 2026-08-14 11:17:45 | CADENCE | ws7 | - | ws8 11.35, ws9 15.39 | t1 ws1b oob 11:09:10..11:16:45, ws1r reversed 11:15:20 during, stamp 11:15:20 \| rider ws7 2.07, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 11:17:45 | BATON | ws7 | ws9 | ws8 11.35, ws9 15.39 | ws7 -> ws9, at a t1 cadence, capped at ws15 by the jump bound 8 |
| 2026-08-14 11:20:00 | NO PASS | ws9 | - | none offered | ws9 18.99 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:24:10 | CADENCE | ws9 | - | ws14 37.10, ws16 21.56, ws17 14.34 | t1 ws1b oob 12:11:10..12:23:10, ws1r reversed 12:15:35 during, stamp 12:15:35 \| rider ws9 72.63, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:24:10 | BATON | ws9 | ws17 | ws14 37.10, ws16 21.56, ws17 14.34 | ws9 -> ws17, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-08-14 12:25:40 | BATON | ws17 | ws19 | ws18 17.51, ws19 26.96 | ws17 -> ws19, between cadences, lin_hop 2 |
| 2026-08-14 12:26:20 | BATON | ws19 | ws20 | ws20 22.45 | ws19 -> ws20, between cadences, lin_hop 2 |
| 2026-08-14 12:30:15 | BATON | ws20 | ws22 | ws22 21.31 | ws20 -> ws22, between cadences, lin_hop 2 |
| 2026-08-14 12:56:10 | BATON | ws22 | ws24 | ws24 19.38 | ws22 -> ws24, between cadences, lin_hop 2 |
| 2026-08-14 13:13:05 | NO PASS | ws24 | - | none offered | ws24 23.29 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:18:00 | CADENCE | ws24 | - | none offered | t1 ws1b oob 14:11:25..14:17:00, ws1r reversed 14:16:45 during, stamp 14:16:45 \| rider ws24 40.44, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:18:00 | EXHAUST | ws24 | - | - | t4 at a t1 cadence - rider ws24 40.44, no candidate at or below ws32 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-14 14:18:00 |
| baton passes made | 11 |
| minutes from the arm to the verdict | 439.0 |
| the rider chain | ws8 > ws11 > ws16 > ws18 > ws22 > ws30 > ws7 > ws9 > ws17 > ws19 > ws20 > ws22 > ws24 |

## MODE 'reversal+quarter' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | - | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 07:03:05 | RIDER | ws8 | - | - | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:03:05 | CADENCE | ws8 | - | ws9 13.11, ws11 24.61 | t1 ws1b oob 06:59:40..07:02:05, ws1r reversed 07:00:55 during, stamp 07:00:55 \| rider ws8 4.46, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 07:03:05 | BATON | ws8 | ws11 | ws9 13.11, ws11 24.61 | ws8 -> ws11, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:15:10 | CADENCE | ws11 | - | ws12 13.90, ws13 20.95, ws14 16.88, ws16 22.31 | t1 ws1b oob 07:13:35..07:14:10, ws1r reversed 07:14:00 during, stamp 07:14:00 \| rider ws11 9.10, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:15:10 | BATON | ws11 | ws16 | ws12 13.90, ws13 20.95, ws14 16.88, ws16 22.31 | ws11 -> ws16, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 07:35:30 | CADENCE | ws16 | - | ws17 16.07, ws18 18.32 | t1 ws1b oob 07:32:15..07:34:30, ws1r reversed 07:34:30 during, stamp 07:34:30 \| rider ws16 9.72, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 07:35:30 | BATON | ws16 | ws18 | ws17 16.07, ws18 18.32 | ws16 -> ws18, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:47:20 | CADENCE | ws18 | - | ws19 15.43, ws20 22.92, ws21 15.06, ws22 16.37 | t1 ws1b ib 07:45:30, ws1r reversed 07:47:20 inside the 120s grace, stamp 07:47:20 \| rider ws18 17.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:47:20 | BATON | ws18 | ws22 | ws19 15.43, ws20 22.92, ws21 15.06, ws22 16.37 | ws18 -> ws22, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 07:54:45 | NO PASS | ws22 | - | none offered | ws22 19.97 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:11:50 | CADENCE | ws22 | - | ws23 20.09, ws24 4.84, ws27 10.12, ws28 1.10, ws29 20.58, ws30 6.12 | t1 ws1b oob 09:07:15..09:10:50, ws1r reversed 09:10:25 during, stamp 09:10:25 \| rider ws22 36.57, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:11:50 | BATON | ws22 | ws30 | ws23 20.09, ws24 4.84, ws27 10.12, ws28 1.10, ws29 20.58, ws30 6.12 | ws22 -> ws30, at a t1 cadence, capped at ws30 by the jump bound 8 |
| 2026-08-14 09:21:05 | NO PASS | ws30 | - | none offered | ws30 6.12 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:31:50 | CADENCE | ws30 | - | none offered | t1 ws1b ib 09:30:55, ws1r reversed 09:31:20 inside the 120s grace, stamp 09:31:20 \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:31:50 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 09:33:45 | NO PASS | ws30 | - | none offered | ws30 4.18 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:42:10 | CADENCE | ws30 | - | none offered | t1 ws1b ib 10:41:15, ws1r reversed 10:41:20 inside the 120s grace, stamp 10:41:20 \| rider ws30 27.07, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:42:10 | TOP RESET | ws30 | ws7 | ws1 34.77, ws2 8.34, ws3 7.09, ws7 67.48 | ws30 27.07 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws7 |
| 2026-08-14 10:52:05 | CADENCE | ws7 | - | none offered | t1 ws1b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, stamp 10:48:55 \| rider ws7 44.37, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 10:52:05 | HOLD | ws7 | - | - | rider ws7 44.37 ex-fence and not reversed - no action |
| 2026-08-14 11:17:45 | CADENCE | ws7 | - | ws8 11.35, ws9 15.39 | t1 ws1b oob 11:09:10..11:16:45, ws1r reversed 11:15:20 during, stamp 11:15:20 \| rider ws7 2.07, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 11:17:45 | BATON | ws7 | ws9 | ws8 11.35, ws9 15.39 | ws7 -> ws9, at a t1 cadence, capped at ws15 by the jump bound 8 |
| 2026-08-14 11:21:20 | NO PASS | ws9 | - | none offered | ws9 17.24 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:24:10 | CADENCE | ws9 | - | ws14 37.10, ws16 21.56, ws17 14.34 | t1 ws1b oob 12:11:10..12:23:10, ws1r reversed 12:15:35 during, stamp 12:15:35 \| rider ws9 72.63, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:24:10 | BATON | ws9 | ws17 | ws14 37.10, ws16 21.56, ws17 14.34 | ws9 -> ws17, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-08-14 12:29:00 | BATON | ws17 | ws19 | ws18 10.82, ws19 18.63 | ws17 -> ws19, between cadences, lin_hop 2 |
| 2026-08-14 12:30:10 | BATON | ws19 | ws20 | ws20 22.63 | ws19 -> ws20, between cadences, lin_hop 2 |
| 2026-08-14 12:34:20 | BATON | ws20 | ws22 | ws22 21.75 | ws20 -> ws22, between cadences, lin_hop 2 |
| 2026-08-14 13:00:45 | BATON | ws22 | ws24 | ws24 17.45 | ws22 -> ws24, between cadences, lin_hop 2 |
| 2026-08-14 13:18:10 | NO PASS | ws24 | - | none offered | ws24 12.81 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:18:00 | CADENCE | ws24 | - | none offered | t1 ws1b oob 14:11:25..14:17:00, ws1r reversed 14:16:45 during, stamp 14:16:45 \| rider ws24 40.44, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:18:00 | EXHAUST | ws24 | - | - | t4 at a t1 cadence - rider ws24 40.44, no candidate at or below ws32 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-14 14:18:00 |
| baton passes made | 11 |
| minutes from the arm to the verdict | 439.0 |
| the rider chain | ws8 > ws11 > ws16 > ws18 > ws22 > ws30 > ws7 > ws9 > ws17 > ws19 > ws20 > ws22 > ws24 |

## MODE 'ib' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 06:59:00 | RETEST | - | ws1r 12.95 oob + ws2r 52.91 / ws3r 70.72 in - the gate opens; ws1r oob->ib cross 2026-08-14 07:02:10, wob 12, cadence at 2026-08-14 07:03:05 |
| 2026-08-14 07:03:05 | RIDER | ws8 | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:03:05 | CADENCE | ws8 | t1 ws1b oob 06:59:40..07:02:05, ws1r reversed 07:00:55 during, stamp 07:00:55 \| rider ws8 4.46, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 07:03:05 | BATON | ws8 | ws8 -> ws11, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:15:10 | LATCH1 | ws11 | latch 1 at the t1 cadence 2026-08-14 07:15:10, divergence state -1 |
| 2026-08-14 07:15:10 | CADENCE | ws11 | t1 ws1b oob 07:13:35..07:14:10, ws1r reversed 07:14:00 during, stamp 07:14:00 \| rider ws11 9.10, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:15:10 | BATON | ws11 | ws11 -> ws16, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 07:35:30 | LATCH1 | ws16 | latch 1 at the t1 cadence 2026-08-14 07:35:30, divergence state -1 |
| 2026-08-14 07:35:30 | CADENCE | ws16 | t1 ws1b oob 07:32:15..07:34:30, ws1r reversed 07:34:30 during, stamp 07:34:30 \| rider ws16 9.72, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 07:35:30 | BATON | ws16 | ws16 -> ws18, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:47:20 | LATCH1 | ws18 | latch 1 at the t1 cadence 2026-08-14 07:47:20, divergence state -1 |
| 2026-08-14 07:47:20 | CADENCE | ws18 | t1 ws1b ib 07:45:30, ws1r reversed 07:47:20 inside the 120s grace, stamp 07:47:20 \| rider ws18 17.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:47:20 | BATON | ws18 | ws18 -> ws22, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 08:10:00 | BATON | ws22 | ws22 -> ws24, between cadences, lin_hop 2 |
| 2026-08-14 08:30:10 | NO PASS | ws24 | ws24 7.89 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:11:50 | LATCH1 | ws24 | latch 1 at the t1 cadence 2026-08-14 09:11:50, divergence state -1 |
| 2026-08-14 09:11:50 | CADENCE | ws24 | t1 ws1b oob 09:07:15..09:10:50, ws1r reversed 09:10:25 during, stamp 09:10:25 \| rider ws24 4.84, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:11:50 | BATON | ws24 | ws24 -> ws30, at a t1 cadence, capped at ws32 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 09:14:10 | NO PASS | ws30 | ws30 9.90 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:31:50 | CADENCE | ws30 | t1 ws1b ib 09:30:55, ws1r reversed 09:31:20 inside the 120s grace, stamp 09:31:20 \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:31:50 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:40 | NO PASS | ws30 | ws30 18.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:42:10 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 10:42:10, divergence state -1 |
| 2026-08-14 10:42:10 | CADENCE | ws30 | t1 ws1b ib 10:41:15, ws1r reversed 10:41:20 inside the 120s grace, stamp 10:41:20 \| rider ws30 27.07, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:42:10 | TOP RESET | ws30 | ws30 27.07 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws7 |
| 2026-08-14 10:52:05 | LATCH1 | ws7 | latch 1 at the t1 cadence 2026-08-14 10:52:05, divergence state -1 |
| 2026-08-14 10:52:05 | CADENCE | ws7 | t1 ws1b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, stamp 10:48:55 \| rider ws7 44.37, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 10:52:05 | HOLD | ws7 | rider ws7 44.37 ex-fence and not reversed - no action |
| 2026-08-14 11:17:45 | LATCH1 | ws7 | latch 1 at the t1 cadence 2026-08-14 11:17:45, divergence state -1 |
| 2026-08-14 11:17:45 | CADENCE | ws7 | t1 ws1b oob 11:09:10..11:16:45, ws1r reversed 11:15:20 during, stamp 11:15:20 \| rider ws7 2.07, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 11:17:45 | BATON | ws7 | ws7 -> ws9, at a t1 cadence, capped at ws15 by the jump bound 8 |
| 2026-08-14 11:19:20 | NO PASS | ws9 | ws9 18.29 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:24:10 | CADENCE | ws9 | t1 ws1b oob 12:11:10..12:23:10, ws1r reversed 12:15:35 during, stamp 12:15:35 \| rider ws9 72.63, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:24:10 | BATON | ws9 | ws9 -> ws17, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-08-14 12:25:20 | BATON | ws17 | ws17 -> ws19, between cadences, lin_hop 2 |
| 2026-08-14 12:50:25 | NO PASS | ws19 | ws19 28.56 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:18:00 | CADENCE | ws19 | t1 ws1b oob 14:11:25..14:17:00, ws1r reversed 14:16:45 during, stamp 14:16:45 \| rider ws19 63.66, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:18:00 | EXHAUST | ws19 | t4 at a t1 cadence - rider ws19 63.66, no candidate at or below ws27 (the jump bound 8) |

## MODE 'reversal' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 06:59:00 | RETEST | - | ws1r 12.95 oob + ws2r 52.91 / ws3r 70.72 in - the gate opens; ws1r oob->ib cross 2026-08-14 07:02:10, wob 12, cadence at 2026-08-14 07:03:05 |
| 2026-08-14 07:03:05 | RIDER | ws8 | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:03:05 | CADENCE | ws8 | t1 ws1b oob 06:59:40..07:02:05, ws1r reversed 07:00:55 during, stamp 07:00:55 \| rider ws8 4.46, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 07:03:05 | BATON | ws8 | ws8 -> ws11, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:15:10 | LATCH1 | ws11 | latch 1 at the t1 cadence 2026-08-14 07:15:10, divergence state -1 |
| 2026-08-14 07:15:10 | CADENCE | ws11 | t1 ws1b oob 07:13:35..07:14:10, ws1r reversed 07:14:00 during, stamp 07:14:00 \| rider ws11 9.10, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:15:10 | BATON | ws11 | ws11 -> ws16, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 07:35:30 | LATCH1 | ws16 | latch 1 at the t1 cadence 2026-08-14 07:35:30, divergence state -1 |
| 2026-08-14 07:35:30 | CADENCE | ws16 | t1 ws1b oob 07:32:15..07:34:30, ws1r reversed 07:34:30 during, stamp 07:34:30 \| rider ws16 9.72, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 07:35:30 | BATON | ws16 | ws16 -> ws18, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:47:20 | LATCH1 | ws18 | latch 1 at the t1 cadence 2026-08-14 07:47:20, divergence state -1 |
| 2026-08-14 07:47:20 | CADENCE | ws18 | t1 ws1b ib 07:45:30, ws1r reversed 07:47:20 inside the 120s grace, stamp 07:47:20 \| rider ws18 17.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:47:20 | BATON | ws18 | ws18 -> ws22, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 07:50:10 | NO PASS | ws22 | ws22 19.89 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:11:50 | LATCH1 | ws22 | latch 1 at the t1 cadence 2026-08-14 09:11:50, divergence state -1 |
| 2026-08-14 09:11:50 | CADENCE | ws22 | t1 ws1b oob 09:07:15..09:10:50, ws1r reversed 09:10:25 during, stamp 09:10:25 \| rider ws22 36.57, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:11:50 | BATON | ws22 | ws22 -> ws30, at a t1 cadence, capped at ws30 by the jump bound 8 |
| 2026-08-14 09:14:30 | NO PASS | ws30 | ws30 10.59 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:31:50 | CADENCE | ws30 | t1 ws1b ib 09:30:55, ws1r reversed 09:31:20 inside the 120s grace, stamp 09:31:20 \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:31:50 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:10 | NO PASS | ws30 | ws30 16.80 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:42:10 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 10:42:10, divergence state -1 |
| 2026-08-14 10:42:10 | CADENCE | ws30 | t1 ws1b ib 10:41:15, ws1r reversed 10:41:20 inside the 120s grace, stamp 10:41:20 \| rider ws30 27.07, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:42:10 | TOP RESET | ws30 | ws30 27.07 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws7 |
| 2026-08-14 10:52:05 | LATCH1 | ws7 | latch 1 at the t1 cadence 2026-08-14 10:52:05, divergence state -1 |
| 2026-08-14 10:52:05 | CADENCE | ws7 | t1 ws1b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, stamp 10:48:55 \| rider ws7 44.37, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 10:52:05 | HOLD | ws7 | rider ws7 44.37 ex-fence and not reversed - no action |
| 2026-08-14 11:17:45 | LATCH1 | ws7 | latch 1 at the t1 cadence 2026-08-14 11:17:45, divergence state -1 |
| 2026-08-14 11:17:45 | CADENCE | ws7 | t1 ws1b oob 11:09:10..11:16:45, ws1r reversed 11:15:20 during, stamp 11:15:20 \| rider ws7 2.07, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 11:17:45 | BATON | ws7 | ws7 -> ws9, at a t1 cadence, capped at ws15 by the jump bound 8 |
| 2026-08-14 11:20:00 | NO PASS | ws9 | ws9 18.99 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:24:10 | CADENCE | ws9 | t1 ws1b oob 12:11:10..12:23:10, ws1r reversed 12:15:35 during, stamp 12:15:35 \| rider ws9 72.63, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:24:10 | BATON | ws9 | ws9 -> ws17, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-08-14 12:25:40 | BATON | ws17 | ws17 -> ws19, between cadences, lin_hop 2 |
| 2026-08-14 12:26:20 | BATON | ws19 | ws19 -> ws20, between cadences, lin_hop 2 |
| 2026-08-14 12:30:15 | BATON | ws20 | ws20 -> ws22, between cadences, lin_hop 2 |
| 2026-08-14 12:56:10 | BATON | ws22 | ws22 -> ws24, between cadences, lin_hop 2 |
| 2026-08-14 13:13:05 | NO PASS | ws24 | ws24 23.29 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:18:00 | CADENCE | ws24 | t1 ws1b oob 14:11:25..14:17:00, ws1r reversed 14:16:45 during, stamp 14:16:45 \| rider ws24 40.44, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:18:00 | EXHAUST | ws24 | t4 at a t1 cadence - rider ws24 40.44, no candidate at or below ws32 (the jump bound 8) |

## MODE 'reversal+quarter' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 06:59:00 | RETEST | - | ws1r 12.95 oob + ws2r 52.91 / ws3r 70.72 in - the gate opens; ws1r oob->ib cross 2026-08-14 07:02:10, wob 12, cadence at 2026-08-14 07:03:05 |
| 2026-08-14 07:03:05 | RIDER | ws8 | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:03:05 | CADENCE | ws8 | t1 ws1b oob 06:59:40..07:02:05, ws1r reversed 07:00:55 during, stamp 07:00:55 \| rider ws8 4.46, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 07:03:05 | BATON | ws8 | ws8 -> ws11, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:15:10 | LATCH1 | ws11 | latch 1 at the t1 cadence 2026-08-14 07:15:10, divergence state -1 |
| 2026-08-14 07:15:10 | CADENCE | ws11 | t1 ws1b oob 07:13:35..07:14:10, ws1r reversed 07:14:00 during, stamp 07:14:00 \| rider ws11 9.10, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:15:10 | BATON | ws11 | ws11 -> ws16, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 07:35:30 | LATCH1 | ws16 | latch 1 at the t1 cadence 2026-08-14 07:35:30, divergence state -1 |
| 2026-08-14 07:35:30 | CADENCE | ws16 | t1 ws1b oob 07:32:15..07:34:30, ws1r reversed 07:34:30 during, stamp 07:34:30 \| rider ws16 9.72, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 07:35:30 | BATON | ws16 | ws16 -> ws18, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:47:20 | LATCH1 | ws18 | latch 1 at the t1 cadence 2026-08-14 07:47:20, divergence state -1 |
| 2026-08-14 07:47:20 | CADENCE | ws18 | t1 ws1b ib 07:45:30, ws1r reversed 07:47:20 inside the 120s grace, stamp 07:47:20 \| rider ws18 17.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:47:20 | BATON | ws18 | ws18 -> ws22, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 07:54:45 | NO PASS | ws22 | ws22 19.97 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:11:50 | LATCH1 | ws22 | latch 1 at the t1 cadence 2026-08-14 09:11:50, divergence state -1 |
| 2026-08-14 09:11:50 | CADENCE | ws22 | t1 ws1b oob 09:07:15..09:10:50, ws1r reversed 09:10:25 during, stamp 09:10:25 \| rider ws22 36.57, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:11:50 | BATON | ws22 | ws22 -> ws30, at a t1 cadence, capped at ws30 by the jump bound 8 |
| 2026-08-14 09:21:05 | NO PASS | ws30 | ws30 6.12 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:31:50 | CADENCE | ws30 | t1 ws1b ib 09:30:55, ws1r reversed 09:31:20 inside the 120s grace, stamp 09:31:20 \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:31:50 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 09:33:45 | NO PASS | ws30 | ws30 4.18 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:42:10 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 10:42:10, divergence state -1 |
| 2026-08-14 10:42:10 | CADENCE | ws30 | t1 ws1b ib 10:41:15, ws1r reversed 10:41:20 inside the 120s grace, stamp 10:41:20 \| rider ws30 27.07, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:42:10 | TOP RESET | ws30 | ws30 27.07 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws7 |
| 2026-08-14 10:52:05 | LATCH1 | ws7 | latch 1 at the t1 cadence 2026-08-14 10:52:05, divergence state -1 |
| 2026-08-14 10:52:05 | CADENCE | ws7 | t1 ws1b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, stamp 10:48:55 \| rider ws7 44.37, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 10:52:05 | HOLD | ws7 | rider ws7 44.37 ex-fence and not reversed - no action |
| 2026-08-14 11:17:45 | LATCH1 | ws7 | latch 1 at the t1 cadence 2026-08-14 11:17:45, divergence state -1 |
| 2026-08-14 11:17:45 | CADENCE | ws7 | t1 ws1b oob 11:09:10..11:16:45, ws1r reversed 11:15:20 during, stamp 11:15:20 \| rider ws7 2.07, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 11:17:45 | BATON | ws7 | ws7 -> ws9, at a t1 cadence, capped at ws15 by the jump bound 8 |
| 2026-08-14 11:21:20 | NO PASS | ws9 | ws9 17.24 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:24:10 | CADENCE | ws9 | t1 ws1b oob 12:11:10..12:23:10, ws1r reversed 12:15:35 during, stamp 12:15:35 \| rider ws9 72.63, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:24:10 | BATON | ws9 | ws9 -> ws17, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-08-14 12:29:00 | BATON | ws17 | ws17 -> ws19, between cadences, lin_hop 2 |
| 2026-08-14 12:30:10 | BATON | ws19 | ws19 -> ws20, between cadences, lin_hop 2 |
| 2026-08-14 12:34:20 | BATON | ws20 | ws20 -> ws22, between cadences, lin_hop 2 |
| 2026-08-14 13:00:45 | BATON | ws22 | ws22 -> ws24, between cadences, lin_hop 2 |
| 2026-08-14 13:18:10 | NO PASS | ws24 | ws24 12.81 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:18:00 | CADENCE | ws24 | t1 ws1b oob 14:11:25..14:17:00, ws1r reversed 14:16:45 during, stamp 14:16:45 \| rider ws24 40.44, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:18:00 | EXHAUST | ws24 | t4 at a t1 cadence - rider ws24 40.44, no candidate at or below ws32 (the jump bound 8) |
