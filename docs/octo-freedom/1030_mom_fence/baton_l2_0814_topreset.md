# LINEAGE2 BATON CHAIN - THE ARM IS HANDED IN AT 2026-08-14 06:59:00, SIDE low
# TAPE 1632960 bars | B 2026-10-04 23:59:55, the last tape bar, no end bound | RULED_OK False

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
| 2026-08-14 07:14:15 | CADENCE | ws8 | - | ws10 0.40, ws11 9.10, ws12 14.43, ws13 20.95, ws14 17.61, ws16 22.91, ws27 16.67, ws28 23.02, ws29 14.48 | t1 ws1b oob 07:13:35..07:14:10, ws1r reversed 07:14:00 during, stamp 07:14:00 \| rider ws8 9.22, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 07:14:15 | BATON | ws8 | ws29 | ws10 0.40, ws11 9.10, ws12 14.43, ws13 20.95, ws14 17.61, ws16 22.91, ws27 16.67, ws28 23.02, ws29 14.48 | ws8 -> ws29, at a t1 cadence, whole board |
| 2026-08-14 07:20:10 | NO PASS | ws29 | - | none offered | ws29 15.75 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 07:34:35 | CADENCE | ws29 | - | ws30 23.27 | t1 ws1b oob 07:32:15..07:34:30, ws1r reversed 07:34:30 during, stamp 07:34:30 \| rider ws29 14.08, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 07:34:35 | BATON | ws29 | ws30 | ws30 23.27 | ws29 -> ws30, at a t1 cadence, whole board |
| 2026-08-14 07:47:20 | CADENCE | ws30 | - | none offered | t1 ws1b ib 07:45:30, ws1r reversed 07:47:20 inside the 120s grace, stamp 07:47:20 \| rider ws30 23.27, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:47:20 | HOLD | ws30 | - | - | rider ws30 23.27 ex-fence and not reversed - no action |
| 2026-08-14 08:09:40 | NO PASS | ws30 | - | none offered | ws30 25.67 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:10:55 | CADENCE | ws30 | - | none offered | t1 ws1b oob 09:07:15..09:10:50, ws1r reversed 09:10:25 during, stamp 09:10:25 \| rider ws30 6.12, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 09:10:55 | HOLD | ws30 | - | - | rider ws30 6.12 oob - no action |
| 2026-08-14 09:14:10 | NO PASS | ws30 | - | none offered | ws30 9.90 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:31:20 | CADENCE | ws30 | - | none offered | t1 ws1b ib 09:30:55, ws1r reversed 09:31:20 inside the 120s grace, stamp 09:31:20 \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:31:20 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:40 | NO PASS | ws30 | - | none offered | ws30 18.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:41:20 | CADENCE | ws30 | - | none offered | t1 ws1b ib 10:41:15, ws1r reversed 10:41:20 inside the 120s grace, stamp 10:41:20 \| rider ws30 26.81, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:41:20 | TOP RESET | ws30 | ws7 | ws1 23.50, ws2 12.96, ws3 7.55, ws7 67.48 | ws30 26.81 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws7 |
| 2026-08-14 10:51:10 | CADENCE | ws7 | - | ws23 47.53, ws24 29.21, ws27 41.06 | t1 ws1b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, stamp 10:48:55 \| rider ws7 43.38, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 10:51:10 | BATON | ws7 | ws27 | ws23 47.53, ws24 29.21, ws27 41.06 | ws7 -> ws27, at a t1 cadence, whole board |
| 2026-08-14 11:16:50 | CADENCE | ws27 | - | ws28 24.22, ws30 18.88 | t1 ws1b oob 11:09:10..11:16:45, ws1r reversed 11:15:20 during, stamp 11:15:20 \| rider ws27 39.31, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 11:16:50 | BATON | ws27 | ws30 | ws28 24.22, ws30 18.88 | ws27 -> ws30, at a t1 cadence, whole board |
| 2026-08-14 11:42:35 | NO PASS | ws30 | - | none offered | ws30 18.32 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:23:15 | CADENCE | ws30 | - | none offered | t1 ws1b oob 12:11:10..12:23:10, ws1r reversed 12:15:35 during, stamp 12:15:35 \| rider ws30 14.70, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:23:15 | HOLD | ws30 | - | - | rider ws30 14.70 oob - no action |
| 2026-08-14 12:32:20 | NO PASS | ws30 | - | none offered | ws30 17.92 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:17:05 | CADENCE | ws30 | - | none offered | t1 ws1b oob 14:11:25..14:17:00, ws1r reversed 14:16:45 during, stamp 14:16:45 \| rider ws30 34.67, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:17:05 | TOP RESET | ws30 | ws4 | ws3 23.11, ws4 21.94 | ws30 34.67 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws4 |
| 2026-08-14 14:22:45 | NO PASS | ws4 | - | none offered | ws4 20.81 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 17:53:20 | CADENCE | ws4 | - | ws9 17.91, ws11 16.95, ws12 13.67 | t1 ws1b ib 17:53:10, ws1r reversed 17:53:20 inside the 120s grace, stamp 17:53:20 \| rider ws4 31.74, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 17:53:20 | BATON | ws4 | ws12 | ws9 17.91, ws11 16.95, ws12 13.67 | ws4 -> ws12, at a t1 cadence, whole board |
| 2026-08-14 18:39:50 | BATON | ws12 | ws14 | ws13 14.77, ws14 5.55 | ws12 -> ws14, between cadences, lin_hop 2 |
| 2026-08-14 18:49:15 | CADENCE | ws14 | - | ws15 6.25, ws16 10.31, ws17 18.68, ws18 22.34, ws19 16.23 | t1 ws1b ib 18:48:45, ws1r reversed 18:49:15 inside the 120s grace, stamp 18:49:15 \| rider ws14 3.84, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 18:49:15 | BATON | ws14 | ws19 | ws15 6.25, ws16 10.31, ws17 18.68, ws18 22.34, ws19 16.23 | ws14 -> ws19, at a t1 cadence, whole board |
| 2026-08-14 19:09:15 | CADENCE | ws19 | - | ws20 19.13, ws22 19.02 | t1 ws1b oob 18:58:45..19:09:10, ws1r reversed 19:01:35 during, stamp 19:01:35 \| rider ws19 10.54, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 19:09:15 | BATON | ws19 | ws22 | ws20 19.13, ws22 19.02 | ws19 -> ws22, at a t1 cadence, whole board |
| 2026-08-14 19:31:50 | BATON | ws22 | ws24 | ws23 27.24, ws24 30.10 | ws22 -> ws24, between cadences, lin_hop 2 |
| 2026-08-14 19:54:25 | NO PASS | ws24 | - | none offered | ws24 30.48 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 21:52:40 | CADENCE | ws24 | - | none offered | t1 ws1b ib 21:52:25, ws1r reversed 21:52:40 inside the 120s grace, stamp 21:52:40 \| rider ws24 69.42, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-14 21:52:40 | EXHAUST | ws24 | - | - | t4 at a t1 cadence - rider ws24 69.42, no candidate on the whole board |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-14 21:52:40 |
| baton passes made | 9 |
| minutes from the arm to the verdict | 893.7 |
| the rider chain | ws8 > ws29 > ws30 > ws7 > ws27 > ws30 > ws4 > ws12 > ws14 > ws19 > ws22 > ws24 |

## MODE 'reversal' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | - | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 07:03:05 | RIDER | ws8 | - | - | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:13:35 | NO PASS | ws8 | - | none offered | ws8 8.41 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 07:14:15 | CADENCE | ws8 | - | ws10 0.40, ws11 9.10, ws12 14.43, ws13 20.95, ws14 17.61, ws16 22.91, ws27 16.67, ws28 23.02, ws29 14.48 | t1 ws1b oob 07:13:35..07:14:10, ws1r reversed 07:14:00 during, stamp 07:14:00 \| rider ws8 9.22, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 07:14:15 | BATON | ws8 | ws29 | ws10 0.40, ws11 9.10, ws12 14.43, ws13 20.95, ws14 17.61, ws16 22.91, ws27 16.67, ws28 23.02, ws29 14.48 | ws8 -> ws29, at a t1 cadence, whole board |
| 2026-08-14 07:34:35 | CADENCE | ws29 | - | ws30 23.27 | t1 ws1b oob 07:32:15..07:34:30, ws1r reversed 07:34:30 during, stamp 07:34:30 \| rider ws29 14.08, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 07:34:35 | BATON | ws29 | ws30 | ws30 23.27 | ws29 -> ws30, at a t1 cadence, whole board |
| 2026-08-14 07:47:20 | CADENCE | ws30 | - | none offered | t1 ws1b ib 07:45:30, ws1r reversed 07:47:20 inside the 120s grace, stamp 07:47:20 \| rider ws30 23.27, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:47:20 | HOLD | ws30 | - | - | rider ws30 23.27 ex-fence and not reversed - no action |
| 2026-08-14 08:10:00 | NO PASS | ws30 | - | none offered | ws30 25.93 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:10:55 | CADENCE | ws30 | - | none offered | t1 ws1b oob 09:07:15..09:10:50, ws1r reversed 09:10:25 during, stamp 09:10:25 \| rider ws30 6.12, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 09:10:55 | HOLD | ws30 | - | - | rider ws30 6.12 oob - no action |
| 2026-08-14 09:14:30 | NO PASS | ws30 | - | none offered | ws30 10.59 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:31:20 | CADENCE | ws30 | - | none offered | t1 ws1b ib 09:30:55, ws1r reversed 09:31:20 inside the 120s grace, stamp 09:31:20 \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:31:20 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:10 | NO PASS | ws30 | - | none offered | ws30 16.80 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:41:20 | CADENCE | ws30 | - | none offered | t1 ws1b ib 10:41:15, ws1r reversed 10:41:20 inside the 120s grace, stamp 10:41:20 \| rider ws30 26.81, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:41:20 | TOP RESET | ws30 | ws7 | ws1 23.50, ws2 12.96, ws3 7.55, ws7 67.48 | ws30 26.81 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws7 |
| 2026-08-14 10:51:10 | CADENCE | ws7 | - | ws23 47.53, ws24 29.21, ws27 41.06 | t1 ws1b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, stamp 10:48:55 \| rider ws7 43.38, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 10:51:10 | BATON | ws7 | ws27 | ws23 47.53, ws24 29.21, ws27 41.06 | ws7 -> ws27, at a t1 cadence, whole board |
| 2026-08-14 11:16:50 | CADENCE | ws27 | - | ws28 24.22, ws30 18.88 | t1 ws1b oob 11:09:10..11:16:45, ws1r reversed 11:15:20 during, stamp 11:15:20 \| rider ws27 39.31, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 11:16:50 | BATON | ws27 | ws30 | ws28 24.22, ws30 18.88 | ws27 -> ws30, at a t1 cadence, whole board |
| 2026-08-14 11:44:45 | NO PASS | ws30 | - | none offered | ws30 19.61 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:23:15 | CADENCE | ws30 | - | none offered | t1 ws1b oob 12:11:10..12:23:10, ws1r reversed 12:15:35 during, stamp 12:15:35 \| rider ws30 14.70, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:23:15 | HOLD | ws30 | - | - | rider ws30 14.70 oob - no action |
| 2026-08-14 12:32:20 | NO PASS | ws30 | - | none offered | ws30 17.92 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:17:05 | CADENCE | ws30 | - | none offered | t1 ws1b oob 14:11:25..14:17:00, ws1r reversed 14:16:45 during, stamp 14:16:45 \| rider ws30 34.67, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:17:05 | TOP RESET | ws30 | ws4 | ws3 23.11, ws4 21.94 | ws30 34.67 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws4 |
| 2026-08-14 14:18:00 | NO PASS | ws4 | - | none offered | ws4 24.07 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 17:53:20 | CADENCE | ws4 | - | ws9 17.91, ws11 16.95, ws12 13.67 | t1 ws1b ib 17:53:10, ws1r reversed 17:53:20 inside the 120s grace, stamp 17:53:20 \| rider ws4 31.74, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 17:53:20 | BATON | ws4 | ws12 | ws9 17.91, ws11 16.95, ws12 13.67 | ws4 -> ws12, at a t1 cadence, whole board |
| 2026-08-14 18:40:10 | BATON | ws12 | ws14 | ws13 15.93, ws14 6.17 | ws12 -> ws14, between cadences, lin_hop 2 |
| 2026-08-14 18:49:15 | CADENCE | ws14 | - | ws15 6.25, ws16 10.31, ws17 18.68, ws18 22.34, ws19 16.23 | t1 ws1b ib 18:48:45, ws1r reversed 18:49:15 inside the 120s grace, stamp 18:49:15 \| rider ws14 3.84, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 18:49:15 | BATON | ws14 | ws19 | ws15 6.25, ws16 10.31, ws17 18.68, ws18 22.34, ws19 16.23 | ws14 -> ws19, at a t1 cadence, whole board |
| 2026-08-14 19:09:15 | CADENCE | ws19 | - | ws20 19.13, ws22 19.02 | t1 ws1b oob 18:58:45..19:09:10, ws1r reversed 19:01:35 during, stamp 19:01:35 \| rider ws19 10.54, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 19:09:15 | BATON | ws19 | ws22 | ws20 19.13, ws22 19.02 | ws19 -> ws22, at a t1 cadence, whole board |
| 2026-08-14 19:21:55 | BATON | ws22 | ws24 | ws23 24.31, ws24 27.13 | ws22 -> ws24, between cadences, lin_hop 2 |
| 2026-08-14 19:22:15 | NO PASS | ws24 | - | none offered | ws24 28.20 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 21:52:40 | CADENCE | ws24 | - | none offered | t1 ws1b ib 21:52:25, ws1r reversed 21:52:40 inside the 120s grace, stamp 21:52:40 \| rider ws24 69.42, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-14 21:52:40 | EXHAUST | ws24 | - | - | t4 at a t1 cadence - rider ws24 69.42, no candidate on the whole board |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-14 21:52:40 |
| baton passes made | 9 |
| minutes from the arm to the verdict | 893.7 |
| the rider chain | ws8 > ws29 > ws30 > ws7 > ws27 > ws30 > ws4 > ws12 > ws14 > ws19 > ws22 > ws24 |

## MODE 'reversal+quarter' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | - | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 07:03:05 | RIDER | ws8 | - | - | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:14:15 | CADENCE | ws8 | - | ws10 0.40, ws11 9.10, ws12 14.43, ws13 20.95, ws14 17.61, ws16 22.91, ws27 16.67, ws28 23.02, ws29 14.48 | t1 ws1b oob 07:13:35..07:14:10, ws1r reversed 07:14:00 during, stamp 07:14:00 \| rider ws8 9.22, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 07:14:15 | BATON | ws8 | ws29 | ws10 0.40, ws11 9.10, ws12 14.43, ws13 20.95, ws14 17.61, ws16 22.91, ws27 16.67, ws28 23.02, ws29 14.48 | ws8 -> ws29, at a t1 cadence, whole board |
| 2026-08-14 07:34:35 | CADENCE | ws29 | - | ws30 23.27 | t1 ws1b oob 07:32:15..07:34:30, ws1r reversed 07:34:30 during, stamp 07:34:30 \| rider ws29 14.08, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 07:34:35 | BATON | ws29 | ws30 | ws30 23.27 | ws29 -> ws30, at a t1 cadence, whole board |
| 2026-08-14 07:47:20 | CADENCE | ws30 | - | none offered | t1 ws1b ib 07:45:30, ws1r reversed 07:47:20 inside the 120s grace, stamp 07:47:20 \| rider ws30 23.27, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:47:20 | HOLD | ws30 | - | - | rider ws30 23.27 ex-fence and not reversed - no action |
| 2026-08-14 08:16:35 | NO PASS | ws30 | - | none offered | ws30 25.76 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:10:55 | CADENCE | ws30 | - | none offered | t1 ws1b oob 09:07:15..09:10:50, ws1r reversed 09:10:25 during, stamp 09:10:25 \| rider ws30 6.12, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 09:10:55 | HOLD | ws30 | - | - | rider ws30 6.12 oob - no action |
| 2026-08-14 09:21:05 | NO PASS | ws30 | - | none offered | ws30 6.12 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:31:20 | CADENCE | ws30 | - | none offered | t1 ws1b ib 09:30:55, ws1r reversed 09:31:20 inside the 120s grace, stamp 09:31:20 \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:31:20 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 09:33:45 | NO PASS | ws30 | - | none offered | ws30 4.18 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:41:20 | CADENCE | ws30 | - | none offered | t1 ws1b ib 10:41:15, ws1r reversed 10:41:20 inside the 120s grace, stamp 10:41:20 \| rider ws30 26.81, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:41:20 | TOP RESET | ws30 | ws7 | ws1 23.50, ws2 12.96, ws3 7.55, ws7 67.48 | ws30 26.81 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws7 |
| 2026-08-14 10:51:10 | CADENCE | ws7 | - | ws23 47.53, ws24 29.21, ws27 41.06 | t1 ws1b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, stamp 10:48:55 \| rider ws7 43.38, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 10:51:10 | BATON | ws7 | ws27 | ws23 47.53, ws24 29.21, ws27 41.06 | ws7 -> ws27, at a t1 cadence, whole board |
| 2026-08-14 11:16:50 | CADENCE | ws27 | - | ws28 24.22, ws30 18.88 | t1 ws1b oob 11:09:10..11:16:45, ws1r reversed 11:15:20 during, stamp 11:15:20 \| rider ws27 39.31, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 11:16:50 | BATON | ws27 | ws30 | ws28 24.22, ws30 18.88 | ws27 -> ws30, at a t1 cadence, whole board |
| 2026-08-14 11:51:20 | NO PASS | ws30 | - | none offered | ws30 19.82 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:23:15 | CADENCE | ws30 | - | none offered | t1 ws1b oob 12:11:10..12:23:10, ws1r reversed 12:15:35 during, stamp 12:15:35 \| rider ws30 14.70, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:23:15 | HOLD | ws30 | - | - | rider ws30 14.70 oob - no action |
| 2026-08-14 12:38:55 | NO PASS | ws30 | - | none offered | ws30 14.70 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:17:05 | CADENCE | ws30 | - | none offered | t1 ws1b oob 14:11:25..14:17:00, ws1r reversed 14:16:45 during, stamp 14:16:45 \| rider ws30 34.67, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:17:05 | TOP RESET | ws30 | ws4 | ws3 23.11, ws4 21.94 | ws30 34.67 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws4 |
| 2026-08-14 14:18:05 | NO PASS | ws4 | - | none offered | ws4 24.07 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 17:53:20 | CADENCE | ws4 | - | ws9 17.91, ws11 16.95, ws12 13.67 | t1 ws1b ib 17:53:10, ws1r reversed 17:53:20 inside the 120s grace, stamp 17:53:20 \| rider ws4 31.74, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 17:53:20 | BATON | ws4 | ws12 | ws9 17.91, ws11 16.95, ws12 13.67 | ws4 -> ws12, at a t1 cadence, whole board |
| 2026-08-14 18:42:15 | BATON | ws12 | ws14 | ws14 4.55 | ws12 -> ws14, between cadences, lin_hop 2 |
| 2026-08-14 18:49:15 | CADENCE | ws14 | - | ws15 6.25, ws16 10.31, ws17 18.68, ws18 22.34, ws19 16.23 | t1 ws1b ib 18:48:45, ws1r reversed 18:49:15 inside the 120s grace, stamp 18:49:15 \| rider ws14 3.84, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 18:49:15 | BATON | ws14 | ws19 | ws15 6.25, ws16 10.31, ws17 18.68, ws18 22.34, ws19 16.23 | ws14 -> ws19, at a t1 cadence, whole board |
| 2026-08-14 19:09:15 | CADENCE | ws19 | - | ws20 19.13, ws22 19.02 | t1 ws1b oob 18:58:45..19:09:10, ws1r reversed 19:01:35 during, stamp 19:01:35 \| rider ws19 10.54, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 19:09:15 | BATON | ws19 | ws22 | ws20 19.13, ws22 19.02 | ws19 -> ws22, at a t1 cadence, whole board |
| 2026-08-14 19:26:30 | BATON | ws22 | ws24 | ws23 25.30, ws24 28.14 | ws22 -> ws24, between cadences, lin_hop 2 |
| 2026-08-14 19:27:20 | NO PASS | ws24 | - | none offered | ws24 28.60 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 21:52:40 | CADENCE | ws24 | - | none offered | t1 ws1b ib 21:52:25, ws1r reversed 21:52:40 inside the 120s grace, stamp 21:52:40 \| rider ws24 69.42, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-14 21:52:40 | EXHAUST | ws24 | - | - | t4 at a t1 cadence - rider ws24 69.42, no candidate on the whole board |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-14 21:52:40 |
| baton passes made | 9 |
| minutes from the arm to the verdict | 893.7 |
| the rider chain | ws8 > ws29 > ws30 > ws7 > ws27 > ws30 > ws4 > ws12 > ws14 > ws19 > ws22 > ws24 |

## MODE 'ib' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 06:59:00 | RETEST | - | ws1r 12.95 oob + ws2r 52.91 / ws3r 70.72 in - the gate opens; ws1r oob->ib cross 2026-08-14 07:02:10, wob 12, cadence at 2026-08-14 07:03:05 |
| 2026-08-14 07:03:05 | RIDER | ws8 | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:14:15 | LATCH1 | ws8 | latch 1 at the t1 cadence 2026-08-14 07:14:15, divergence state -1 |
| 2026-08-14 07:14:15 | CADENCE | ws8 | t1 ws1b oob 07:13:35..07:14:10, ws1r reversed 07:14:00 during, stamp 07:14:00 \| rider ws8 9.22, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 07:14:15 | BATON | ws8 | ws8 -> ws29, at a t1 cadence, whole board |
| 2026-08-14 07:20:10 | NO PASS | ws29 | ws29 15.75 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 07:34:35 | LATCH1 | ws29 | latch 1 at the t1 cadence 2026-08-14 07:34:35, divergence state -1 |
| 2026-08-14 07:34:35 | CADENCE | ws29 | t1 ws1b oob 07:32:15..07:34:30, ws1r reversed 07:34:30 during, stamp 07:34:30 \| rider ws29 14.08, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 07:34:35 | BATON | ws29 | ws29 -> ws30, at a t1 cadence, whole board |
| 2026-08-14 07:47:20 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 07:47:20, divergence state -1 |
| 2026-08-14 07:47:20 | CADENCE | ws30 | t1 ws1b ib 07:45:30, ws1r reversed 07:47:20 inside the 120s grace, stamp 07:47:20 \| rider ws30 23.27, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:47:20 | HOLD | ws30 | rider ws30 23.27 ex-fence and not reversed - no action |
| 2026-08-14 08:09:40 | NO PASS | ws30 | ws30 25.67 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:10:55 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:10:55, divergence state -1 |
| 2026-08-14 09:10:55 | CADENCE | ws30 | t1 ws1b oob 09:07:15..09:10:50, ws1r reversed 09:10:25 during, stamp 09:10:25 \| rider ws30 6.12, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 09:10:55 | HOLD | ws30 | rider ws30 6.12 oob - no action |
| 2026-08-14 09:14:10 | NO PASS | ws30 | ws30 9.90 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:31:20 | CADENCE | ws30 | t1 ws1b ib 09:30:55, ws1r reversed 09:31:20 inside the 120s grace, stamp 09:31:20 \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:31:20 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:40 | NO PASS | ws30 | ws30 18.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:41:20 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 10:41:20, divergence state -1 |
| 2026-08-14 10:41:20 | CADENCE | ws30 | t1 ws1b ib 10:41:15, ws1r reversed 10:41:20 inside the 120s grace, stamp 10:41:20 \| rider ws30 26.81, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:41:20 | TOP RESET | ws30 | ws30 26.81 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws7 |
| 2026-08-14 10:51:10 | LATCH1 | ws7 | latch 1 at the t1 cadence 2026-08-14 10:51:10, divergence state -1 |
| 2026-08-14 10:51:10 | CADENCE | ws7 | t1 ws1b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, stamp 10:48:55 \| rider ws7 43.38, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 10:51:10 | BATON | ws7 | ws7 -> ws27, at a t1 cadence, whole board |
| 2026-08-14 11:16:50 | LATCH1 | ws27 | latch 1 at the t1 cadence 2026-08-14 11:16:50, divergence state -1 |
| 2026-08-14 11:16:50 | CADENCE | ws27 | t1 ws1b oob 11:09:10..11:16:45, ws1r reversed 11:15:20 during, stamp 11:15:20 \| rider ws27 39.31, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 11:16:50 | BATON | ws27 | ws27 -> ws30, at a t1 cadence, whole board |
| 2026-08-14 11:42:35 | NO PASS | ws30 | ws30 18.32 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:23:15 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 12:23:15, divergence state -1 |
| 2026-08-14 12:23:15 | CADENCE | ws30 | t1 ws1b oob 12:11:10..12:23:10, ws1r reversed 12:15:35 during, stamp 12:15:35 \| rider ws30 14.70, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:23:15 | HOLD | ws30 | rider ws30 14.70 oob - no action |
| 2026-08-14 12:32:20 | NO PASS | ws30 | ws30 17.92 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:17:05 | CADENCE | ws30 | t1 ws1b oob 14:11:25..14:17:00, ws1r reversed 14:16:45 during, stamp 14:16:45 \| rider ws30 34.67, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:17:05 | TOP RESET | ws30 | ws30 34.67 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws4 |
| 2026-08-14 14:22:45 | NO PASS | ws4 | ws4 20.81 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 17:53:20 | LATCH1 | ws4 | latch 1 at the t1 cadence 2026-08-14 17:53:20, divergence state -1 |
| 2026-08-14 17:53:20 | CADENCE | ws4 | t1 ws1b ib 17:53:10, ws1r reversed 17:53:20 inside the 120s grace, stamp 17:53:20 \| rider ws4 31.74, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 17:53:20 | BATON | ws4 | ws4 -> ws12, at a t1 cadence, whole board |
| 2026-08-14 18:39:50 | BATON | ws12 | ws12 -> ws14, between cadences, lin_hop 2 |
| 2026-08-14 18:49:15 | CADENCE | ws14 | t1 ws1b ib 18:48:45, ws1r reversed 18:49:15 inside the 120s grace, stamp 18:49:15 \| rider ws14 3.84, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 18:49:15 | BATON | ws14 | ws14 -> ws19, at a t1 cadence, whole board |
| 2026-08-14 19:09:15 | CADENCE | ws19 | t1 ws1b oob 18:58:45..19:09:10, ws1r reversed 19:01:35 during, stamp 19:01:35 \| rider ws19 10.54, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 19:09:15 | BATON | ws19 | ws19 -> ws22, at a t1 cadence, whole board |
| 2026-08-14 19:31:50 | BATON | ws22 | ws22 -> ws24, between cadences, lin_hop 2 |
| 2026-08-14 19:54:25 | NO PASS | ws24 | ws24 30.48 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 21:52:40 | LATCH1 | ws24 | latch 1 at the t1 cadence 2026-08-14 21:52:40, divergence state -1 |
| 2026-08-14 21:52:40 | CADENCE | ws24 | t1 ws1b ib 21:52:25, ws1r reversed 21:52:40 inside the 120s grace, stamp 21:52:40 \| rider ws24 69.42, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-14 21:52:40 | EXHAUST | ws24 | t4 at a t1 cadence - rider ws24 69.42, no candidate on the whole board |

## MODE 'reversal' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 06:59:00 | RETEST | - | ws1r 12.95 oob + ws2r 52.91 / ws3r 70.72 in - the gate opens; ws1r oob->ib cross 2026-08-14 07:02:10, wob 12, cadence at 2026-08-14 07:03:05 |
| 2026-08-14 07:03:05 | RIDER | ws8 | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:13:35 | NO PASS | ws8 | ws8 8.41 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 07:14:15 | LATCH1 | ws8 | latch 1 at the t1 cadence 2026-08-14 07:14:15, divergence state -1 |
| 2026-08-14 07:14:15 | CADENCE | ws8 | t1 ws1b oob 07:13:35..07:14:10, ws1r reversed 07:14:00 during, stamp 07:14:00 \| rider ws8 9.22, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 07:14:15 | BATON | ws8 | ws8 -> ws29, at a t1 cadence, whole board |
| 2026-08-14 07:34:35 | LATCH1 | ws29 | latch 1 at the t1 cadence 2026-08-14 07:34:35, divergence state -1 |
| 2026-08-14 07:34:35 | CADENCE | ws29 | t1 ws1b oob 07:32:15..07:34:30, ws1r reversed 07:34:30 during, stamp 07:34:30 \| rider ws29 14.08, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 07:34:35 | BATON | ws29 | ws29 -> ws30, at a t1 cadence, whole board |
| 2026-08-14 07:47:20 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 07:47:20, divergence state -1 |
| 2026-08-14 07:47:20 | CADENCE | ws30 | t1 ws1b ib 07:45:30, ws1r reversed 07:47:20 inside the 120s grace, stamp 07:47:20 \| rider ws30 23.27, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:47:20 | HOLD | ws30 | rider ws30 23.27 ex-fence and not reversed - no action |
| 2026-08-14 08:10:00 | NO PASS | ws30 | ws30 25.93 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:10:55 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:10:55, divergence state -1 |
| 2026-08-14 09:10:55 | CADENCE | ws30 | t1 ws1b oob 09:07:15..09:10:50, ws1r reversed 09:10:25 during, stamp 09:10:25 \| rider ws30 6.12, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 09:10:55 | HOLD | ws30 | rider ws30 6.12 oob - no action |
| 2026-08-14 09:14:30 | NO PASS | ws30 | ws30 10.59 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:31:20 | CADENCE | ws30 | t1 ws1b ib 09:30:55, ws1r reversed 09:31:20 inside the 120s grace, stamp 09:31:20 \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:31:20 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:10 | NO PASS | ws30 | ws30 16.80 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:41:20 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 10:41:20, divergence state -1 |
| 2026-08-14 10:41:20 | CADENCE | ws30 | t1 ws1b ib 10:41:15, ws1r reversed 10:41:20 inside the 120s grace, stamp 10:41:20 \| rider ws30 26.81, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:41:20 | TOP RESET | ws30 | ws30 26.81 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws7 |
| 2026-08-14 10:51:10 | LATCH1 | ws7 | latch 1 at the t1 cadence 2026-08-14 10:51:10, divergence state -1 |
| 2026-08-14 10:51:10 | CADENCE | ws7 | t1 ws1b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, stamp 10:48:55 \| rider ws7 43.38, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 10:51:10 | BATON | ws7 | ws7 -> ws27, at a t1 cadence, whole board |
| 2026-08-14 11:16:50 | LATCH1 | ws27 | latch 1 at the t1 cadence 2026-08-14 11:16:50, divergence state -1 |
| 2026-08-14 11:16:50 | CADENCE | ws27 | t1 ws1b oob 11:09:10..11:16:45, ws1r reversed 11:15:20 during, stamp 11:15:20 \| rider ws27 39.31, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 11:16:50 | BATON | ws27 | ws27 -> ws30, at a t1 cadence, whole board |
| 2026-08-14 11:44:45 | NO PASS | ws30 | ws30 19.61 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:23:15 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 12:23:15, divergence state -1 |
| 2026-08-14 12:23:15 | CADENCE | ws30 | t1 ws1b oob 12:11:10..12:23:10, ws1r reversed 12:15:35 during, stamp 12:15:35 \| rider ws30 14.70, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:23:15 | HOLD | ws30 | rider ws30 14.70 oob - no action |
| 2026-08-14 12:32:20 | NO PASS | ws30 | ws30 17.92 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:17:05 | CADENCE | ws30 | t1 ws1b oob 14:11:25..14:17:00, ws1r reversed 14:16:45 during, stamp 14:16:45 \| rider ws30 34.67, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:17:05 | TOP RESET | ws30 | ws30 34.67 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws4 |
| 2026-08-14 14:18:00 | NO PASS | ws4 | ws4 24.07 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 17:53:20 | LATCH1 | ws4 | latch 1 at the t1 cadence 2026-08-14 17:53:20, divergence state -1 |
| 2026-08-14 17:53:20 | CADENCE | ws4 | t1 ws1b ib 17:53:10, ws1r reversed 17:53:20 inside the 120s grace, stamp 17:53:20 \| rider ws4 31.74, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 17:53:20 | BATON | ws4 | ws4 -> ws12, at a t1 cadence, whole board |
| 2026-08-14 18:40:10 | BATON | ws12 | ws12 -> ws14, between cadences, lin_hop 2 |
| 2026-08-14 18:49:15 | CADENCE | ws14 | t1 ws1b ib 18:48:45, ws1r reversed 18:49:15 inside the 120s grace, stamp 18:49:15 \| rider ws14 3.84, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 18:49:15 | BATON | ws14 | ws14 -> ws19, at a t1 cadence, whole board |
| 2026-08-14 19:09:15 | CADENCE | ws19 | t1 ws1b oob 18:58:45..19:09:10, ws1r reversed 19:01:35 during, stamp 19:01:35 \| rider ws19 10.54, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 19:09:15 | BATON | ws19 | ws19 -> ws22, at a t1 cadence, whole board |
| 2026-08-14 19:21:55 | BATON | ws22 | ws22 -> ws24, between cadences, lin_hop 2 |
| 2026-08-14 19:22:15 | NO PASS | ws24 | ws24 28.20 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 21:52:40 | LATCH1 | ws24 | latch 1 at the t1 cadence 2026-08-14 21:52:40, divergence state -1 |
| 2026-08-14 21:52:40 | CADENCE | ws24 | t1 ws1b ib 21:52:25, ws1r reversed 21:52:40 inside the 120s grace, stamp 21:52:40 \| rider ws24 69.42, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-14 21:52:40 | EXHAUST | ws24 | t4 at a t1 cadence - rider ws24 69.42, no candidate on the whole board |

## MODE 'reversal+quarter' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 06:59:00 | RETEST | - | ws1r 12.95 oob + ws2r 52.91 / ws3r 70.72 in - the gate opens; ws1r oob->ib cross 2026-08-14 07:02:10, wob 12, cadence at 2026-08-14 07:03:05 |
| 2026-08-14 07:03:05 | RIDER | ws8 | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:14:15 | LATCH1 | ws8 | latch 1 at the t1 cadence 2026-08-14 07:14:15, divergence state -1 |
| 2026-08-14 07:14:15 | CADENCE | ws8 | t1 ws1b oob 07:13:35..07:14:10, ws1r reversed 07:14:00 during, stamp 07:14:00 \| rider ws8 9.22, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 07:14:15 | BATON | ws8 | ws8 -> ws29, at a t1 cadence, whole board |
| 2026-08-14 07:34:35 | LATCH1 | ws29 | latch 1 at the t1 cadence 2026-08-14 07:34:35, divergence state -1 |
| 2026-08-14 07:34:35 | CADENCE | ws29 | t1 ws1b oob 07:32:15..07:34:30, ws1r reversed 07:34:30 during, stamp 07:34:30 \| rider ws29 14.08, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 07:34:35 | BATON | ws29 | ws29 -> ws30, at a t1 cadence, whole board |
| 2026-08-14 07:47:20 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 07:47:20, divergence state -1 |
| 2026-08-14 07:47:20 | CADENCE | ws30 | t1 ws1b ib 07:45:30, ws1r reversed 07:47:20 inside the 120s grace, stamp 07:47:20 \| rider ws30 23.27, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:47:20 | HOLD | ws30 | rider ws30 23.27 ex-fence and not reversed - no action |
| 2026-08-14 08:16:35 | NO PASS | ws30 | ws30 25.76 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:10:55 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:10:55, divergence state -1 |
| 2026-08-14 09:10:55 | CADENCE | ws30 | t1 ws1b oob 09:07:15..09:10:50, ws1r reversed 09:10:25 during, stamp 09:10:25 \| rider ws30 6.12, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 09:10:55 | HOLD | ws30 | rider ws30 6.12 oob - no action |
| 2026-08-14 09:21:05 | NO PASS | ws30 | ws30 6.12 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:31:20 | CADENCE | ws30 | t1 ws1b ib 09:30:55, ws1r reversed 09:31:20 inside the 120s grace, stamp 09:31:20 \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:31:20 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 09:33:45 | NO PASS | ws30 | ws30 4.18 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:41:20 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 10:41:20, divergence state -1 |
| 2026-08-14 10:41:20 | CADENCE | ws30 | t1 ws1b ib 10:41:15, ws1r reversed 10:41:20 inside the 120s grace, stamp 10:41:20 \| rider ws30 26.81, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:41:20 | TOP RESET | ws30 | ws30 26.81 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws7 |
| 2026-08-14 10:51:10 | LATCH1 | ws7 | latch 1 at the t1 cadence 2026-08-14 10:51:10, divergence state -1 |
| 2026-08-14 10:51:10 | CADENCE | ws7 | t1 ws1b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, stamp 10:48:55 \| rider ws7 43.38, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 10:51:10 | BATON | ws7 | ws7 -> ws27, at a t1 cadence, whole board |
| 2026-08-14 11:16:50 | LATCH1 | ws27 | latch 1 at the t1 cadence 2026-08-14 11:16:50, divergence state -1 |
| 2026-08-14 11:16:50 | CADENCE | ws27 | t1 ws1b oob 11:09:10..11:16:45, ws1r reversed 11:15:20 during, stamp 11:15:20 \| rider ws27 39.31, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 11:16:50 | BATON | ws27 | ws27 -> ws30, at a t1 cadence, whole board |
| 2026-08-14 11:51:20 | NO PASS | ws30 | ws30 19.82 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:23:15 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 12:23:15, divergence state -1 |
| 2026-08-14 12:23:15 | CADENCE | ws30 | t1 ws1b oob 12:11:10..12:23:10, ws1r reversed 12:15:35 during, stamp 12:15:35 \| rider ws30 14.70, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:23:15 | HOLD | ws30 | rider ws30 14.70 oob - no action |
| 2026-08-14 12:38:55 | NO PASS | ws30 | ws30 14.70 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:17:05 | CADENCE | ws30 | t1 ws1b oob 14:11:25..14:17:00, ws1r reversed 14:16:45 during, stamp 14:16:45 \| rider ws30 34.67, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:17:05 | TOP RESET | ws30 | ws30 34.67 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws4 |
| 2026-08-14 14:18:05 | NO PASS | ws4 | ws4 24.07 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 17:53:20 | LATCH1 | ws4 | latch 1 at the t1 cadence 2026-08-14 17:53:20, divergence state -1 |
| 2026-08-14 17:53:20 | CADENCE | ws4 | t1 ws1b ib 17:53:10, ws1r reversed 17:53:20 inside the 120s grace, stamp 17:53:20 \| rider ws4 31.74, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 17:53:20 | BATON | ws4 | ws4 -> ws12, at a t1 cadence, whole board |
| 2026-08-14 18:42:15 | BATON | ws12 | ws12 -> ws14, between cadences, lin_hop 2 |
| 2026-08-14 18:49:15 | CADENCE | ws14 | t1 ws1b ib 18:48:45, ws1r reversed 18:49:15 inside the 120s grace, stamp 18:49:15 \| rider ws14 3.84, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 18:49:15 | BATON | ws14 | ws14 -> ws19, at a t1 cadence, whole board |
| 2026-08-14 19:09:15 | CADENCE | ws19 | t1 ws1b oob 18:58:45..19:09:10, ws1r reversed 19:01:35 during, stamp 19:01:35 \| rider ws19 10.54, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 19:09:15 | BATON | ws19 | ws19 -> ws22, at a t1 cadence, whole board |
| 2026-08-14 19:26:30 | BATON | ws22 | ws22 -> ws24, between cadences, lin_hop 2 |
| 2026-08-14 19:27:20 | NO PASS | ws24 | ws24 28.60 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 21:52:40 | LATCH1 | ws24 | latch 1 at the t1 cadence 2026-08-14 21:52:40, divergence state -1 |
| 2026-08-14 21:52:40 | CADENCE | ws24 | t1 ws1b ib 21:52:25, ws1r reversed 21:52:40 inside the 120s grace, stamp 21:52:40 \| rider ws24 69.42, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-14 21:52:40 | EXHAUST | ws24 | t4 at a t1 cadence - rider ws24 69.42, no candidate on the whole board |
