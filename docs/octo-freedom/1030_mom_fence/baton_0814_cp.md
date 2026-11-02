# LINEAGE2 BATON CHAIN - THE ARM IS HANDED IN AT 2026-08-14 06:59:00, SIDE low
# TAPE 1632960 bars | B 2026-10-04 23:59:55, the last tape bar, no end bound | RULED_OK True

| the setting | value | what it is |
|---|---|---|
| the r fence | 75.0 -> (25.0, 75.0) | his 25/75 |
| the ladder top | ws30 | his max-lineage-TF ws30 |
| the per-line ex-fence latch | OFF | his 1101 "disable the latch" |
| the ex-fence read's source | closed_prev | his 1101 "closed_prev only for exiting fences" |
| the oob read's source | emerging | he put oob in neither category - both arms built |
| the oob->ib cross's source | emerging | his gut, with the other arm built |
| the TF floor for the chart-matched read | ws2 | his "ws1{any} and gcws1{any} stay on emerging" |
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
| 2026-08-14 06:59:00 | ARM | - | - | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 07:03:05 | RIDER | ws8 | - | - | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:13:05 | CADENCE | ws8 | - | ws9 17.07, ws10 0.40, ws11 9.12 | t1 gcws30b ib 07:12:40, ws1r reversed 07:13:00 inside the 120s grace from the cross bar 07:12:40, r 36.68 past the 44.0 fence, stamp 07:13:00, hold 6 bars \| rider ws8 10.75, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:13:05 | BATON | ws8 | ws11 | ws9 17.07, ws10 0.40, ws11 9.12 | ws8 -> ws11, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:35:00 | CADENCE | ws11 | - | ws12 11.52, ws13 3.33, ws14 3.21, ws15 9.04, ws16 9.72 | t1 gcws30b oob 07:32:10..07:34:30, ws1r reversed 07:34:30 during, r 17.51 past the 44.0 fence, stamp 07:34:30, cross 07:34:35 hold 6 bars \| rider ws11 6.80, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:35:00 | BATON | ws11 | ws16 | ws12 11.52, ws13 3.33, ws14 3.21, ws15 9.04, ws16 9.72 | ws11 -> ws16, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 07:45:05 | CADENCE | ws16 | - | ws17 1.79 | t1 gcws30b ib 07:43:30, ws1r reversed 07:45:05 inside the 120s grace from the cross bar 07:43:30, r 28.99 past the 44.0 fence, stamp 07:45:05, hold 6 bars \| rider ws16 4.43, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:45:05 | BATON | ws16 | ws17 | ws17 1.79 | ws16 -> ws17, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 08:10:10 | BATON | ws17 | ws19 | ws18 21.41, ws19 7.99 | ws17 -> ws19, between cadences, lin_hop 2 |
| 2026-08-14 08:16:55 | BATON | ws19 | ws21 | ws21 8.69 | ws19 -> ws21, between cadences, lin_hop 2 |
| 2026-08-14 08:25:20 | CADENCE | ws21 | - | ws22 9.02, ws24 4.57, ws25 10.94 | t1 gcws30b ib 08:24:55, ws1r reversed 08:25:05 inside the 120s grace from the cross bar 08:24:55, r 36.16 past the 44.0 fence, stamp 08:25:05, hold 6 bars \| rider ws21 16.07, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 08:25:20 | BATON | ws21 | ws25 | ws22 9.02, ws24 4.57, ws25 10.94 | ws21 -> ws25, at a t1 cadence, capped at ws29 by the jump bound 8 |
| 2026-08-14 08:35:10 | BATON | ws25 | ws27 | ws27 15.90 | ws25 -> ws27, between cadences, lin_hop 2 |
| 2026-08-14 08:35:55 | BATON | ws27 | ws28 | ws28 21.73 | ws27 -> ws28, between cadences, lin_hop 2 |
| 2026-08-14 08:48:30 | NO PASS | ws28 | - | none offered | ws28 17.33 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:36:20 | CADENCE | ws28 | - | ws30 4.18 | t1 gcws30b ib 09:35:00, ws1r reversed 09:36:20 inside the 120s grace from the cross bar 09:35:00, r 16.75 past the 44.0 fence, stamp 09:36:20, hold 6 bars \| rider ws28 1.10, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 09:36:20 | BATON | ws28 | ws30 | ws30 4.18 | ws28 -> ws30, at a t1 cadence, capped at ws36 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 09:39:30 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 09:37:40, ws1r reversed 09:39:30 inside the 120s grace from the cross bar 09:37:40, r 43.97 past the 44.0 fence, stamp 09:39:30, hold 6 bars \| rider ws30 4.18, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 09:39:30 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 09:41:20 | CADENCE | ws30 | - | none offered | t1 gcws30b oob 09:38:15..09:40:50, ws1r reversed 09:39:30 during, r 43.97 past the 44.0 fence, stamp 09:39:30, cross 09:40:55 hold 6 bars \| rider ws30 4.18, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 09:41:20 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:40 | NO PASS | ws30 | - | none offered | ws30 18.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:28:20 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 10:27:55, ws1r reversed 10:28:00 inside the 120s grace from the cross bar 10:27:55, r 4.45 past the 44.0 fence, stamp 10:28:00, hold 6 bars \| rider ws30 17.09, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 10:28:20 | TOP RESET | ws30 | ws1 | ws1 6.37 | ws30 17.09 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws1 |
| 2026-08-14 10:30:15 | NO PASS | ws1 | - | none offered | ws1 30.89 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:51:35 | CADENCE | ws1 | - | ws2 14.29, ws3 9.27, ws4 6.62 | t1 gcws30b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, r 35.89 past the 44.0 fence, stamp 10:48:55, cross 10:51:10 hold 6 bars \| rider ws1 26.63, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-14 10:51:35 | BATON | ws1 | ws4 | ws2 14.29, ws3 9.27, ws4 6.62 | ws1 -> ws4, at a t1 cadence, capped at ws9 by the jump bound 8 |
| 2026-08-14 11:16:00 | CADENCE | ws4 | - | ws5 6.86, ws6 0.00, ws7 2.07 | t1 gcws30b oob 11:11:30..11:15:30, ws1r reversed 11:15:20 during, r 8.28 past the 44.0 fence, stamp 11:15:20, cross 11:15:35 hold 6 bars \| rider ws4 0.00, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 11:16:00 | BATON | ws4 | ws7 | ws5 6.86, ws6 0.00, ws7 2.07 | ws4 -> ws7, at a t1 cadence, capped at ws12 by the jump bound 8 |
| 2026-08-14 11:26:55 | BATON | ws7 | ws9 | ws8 16.17, ws9 19.08 | ws7 -> ws9, between cadences, lin_hop 2 |
| 2026-08-14 11:33:55 | BATON | ws9 | ws11 | ws11 14.15 | ws9 -> ws11, between cadences, lin_hop 2 |
| 2026-08-14 11:37:50 | NO PASS | ws11 | - | none offered | ws11 16.97 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:02:25 | CADENCE | ws11 | - | ws12 32.25 | t1 gcws30b ib 12:02:00, ws1r reversed 12:02:25 inside the 120s grace from the cross bar 12:02:00, r 27.60 past the 44.0 fence, stamp 12:02:25, hold 6 bars \| rider ws11 32.71, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 12:02:25 | BATON | ws11 | ws12 | ws12 32.25 | ws11 -> ws12, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 12:16:00 | CADENCE | ws12 | - | ws16 22.22, ws17 14.61 | t1 gcws30b oob 12:14:20..12:15:30, ws1r reversed 12:14:45 during, r 19.40 past the 44.0 fence, stamp 12:14:45, cross 12:15:35 hold 6 bars \| rider ws12 31.53, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:16:00 | BATON | ws12 | ws17 | ws16 22.22, ws17 14.61 | ws12 -> ws17, at a t1 cadence, capped at ws20 by the jump bound 8 |
| 2026-08-14 12:25:45 | BATON | ws17 | ws18 | ws18 17.51 | ws17 -> ws18, between cadences, lin_hop 2 |
| 2026-08-14 12:32:20 | NO PASS | ws18 | - | none offered | ws18 16.43 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:46:35 | CADENCE | ws18 | - | ws19 20.59, ws20 18.22, ws23 9.99 | t1 gcws30b ib 12:46:10, ws1r reversed 12:46:15 inside the 120s grace from the cross bar 12:46:10, r 37.62 past the 44.0 fence, stamp 12:46:15, hold 6 bars \| rider ws18 20.14, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 12:46:35 | BATON | ws18 | ws23 | ws19 20.59, ws20 18.22, ws23 9.99 | ws18 -> ws23, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 12:48:30 | CADENCE | ws23 | - | ws30 14.70 | t1 gcws30b oob 12:46:45..12:48:00, ws1r reversed 12:47:55 during, r 31.66 past the 44.0 fence, stamp 12:47:55, cross 12:48:05 hold 6 bars \| rider ws23 9.99, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 12:48:30 | BATON | ws23 | ws30 | ws30 14.70 | ws23 -> ws30, at a t1 cadence, capped at ws31 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 12:50:50 | NO PASS | ws30 | - | none offered | ws30 16.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 13:03:10 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 13:02:30, ws1r reversed 13:03:10 inside the 120s grace from the cross bar 13:02:30, r 22.36 past the 44.0 fence, stamp 13:03:10, hold 6 bars \| rider ws30 15.38, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 13:03:10 | HOLD | ws30 | - | - | rider ws30 15.38 ex-fence and not reversed - no action |
| 2026-08-14 13:28:55 | NO PASS | ws30 | - | none offered | ws30 26.30 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:07:20 | CADENCE | ws30 | - | none offered | t1 gcws30b oob 14:04:20..14:06:50, ws1r reversed 14:06:45 during, r 17.33 past the 44.0 fence, stamp 14:06:45, cross 14:06:55 hold 6 bars \| rider ws30 34.89, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:07:20 | TOP RESET | ws30 | ws1 | ws1 14.01 | ws30 34.89 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws1 |
| 2026-08-14 14:08:55 | BATON | ws1 | ws2 | ws2 19.40 | ws1 -> ws2, between cadences, lin_hop 2 |
| 2026-08-14 14:11:20 | CADENCE | ws2 | - | none offered | t1 gcws30b oob 14:10:05..14:10:50, ws1r reversed 14:10:30 during, r 28.27 past the 44.0 fence, stamp 14:10:30, cross 14:10:55 hold 6 bars \| rider ws2 22.01, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 14:11:20 | EXHAUST | ws2 | - | - | t4 at a t1 cadence - rider ws2 22.01, no candidate at or below ws10 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-14 14:11:20 |
| baton passes made | 19 |
| minutes from the arm to the verdict | 432.3 |
| the rider chain | ws8 > ws11 > ws16 > ws17 > ws19 > ws21 > ws25 > ws27 > ws28 > ws30 > ws1 > ws4 > ws7 > ws9 > ws11 > ws12 > ws17 > ws18 > ws23 > ws30 > ws1 > ws2 |

## MODE 'reversal' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | - | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 07:03:05 | RIDER | ws8 | - | - | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:13:05 | CADENCE | ws8 | - | ws9 17.07, ws10 0.40, ws11 9.12 | t1 gcws30b ib 07:12:40, ws1r reversed 07:13:00 inside the 120s grace from the cross bar 07:12:40, r 36.68 past the 44.0 fence, stamp 07:13:00, hold 6 bars \| rider ws8 10.75, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:13:05 | BATON | ws8 | ws11 | ws9 17.07, ws10 0.40, ws11 9.12 | ws8 -> ws11, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:35:00 | CADENCE | ws11 | - | ws12 11.52, ws13 3.33, ws14 3.21, ws15 9.04, ws16 9.72 | t1 gcws30b oob 07:32:10..07:34:30, ws1r reversed 07:34:30 during, r 17.51 past the 44.0 fence, stamp 07:34:30, cross 07:34:35 hold 6 bars \| rider ws11 6.80, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:35:00 | BATON | ws11 | ws16 | ws12 11.52, ws13 3.33, ws14 3.21, ws15 9.04, ws16 9.72 | ws11 -> ws16, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 07:45:05 | CADENCE | ws16 | - | ws17 1.79 | t1 gcws30b ib 07:43:30, ws1r reversed 07:45:05 inside the 120s grace from the cross bar 07:43:30, r 28.99 past the 44.0 fence, stamp 07:45:05, hold 6 bars \| rider ws16 4.43, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:45:05 | BATON | ws16 | ws17 | ws17 1.79 | ws16 -> ws17, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:52:35 | BATON | ws17 | ws18 | ws18 7.16 | ws17 -> ws18, between cadences, lin_hop 2 |
| 2026-08-14 08:06:55 | BATON | ws18 | ws19 | ws19 4.83 | ws18 -> ws19, between cadences, lin_hop 2 |
| 2026-08-14 08:09:45 | BATON | ws19 | ws21 | ws21 8.94 | ws19 -> ws21, between cadences, lin_hop 2 |
| 2026-08-14 08:10:10 | BATON | ws21 | ws22 | ws22 12.26 | ws21 -> ws22, between cadences, lin_hop 2 |
| 2026-08-14 08:10:20 | NO PASS | ws22 | - | none offered | ws22 12.34 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 08:25:20 | CADENCE | ws22 | - | ws24 4.57, ws25 10.94, ws30 23.37 | t1 gcws30b ib 08:24:55, ws1r reversed 08:25:05 inside the 120s grace from the cross bar 08:24:55, r 36.16 past the 44.0 fence, stamp 08:25:05, hold 6 bars \| rider ws22 9.02, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 08:25:20 | BATON | ws22 | ws30 | ws24 4.57, ws25 10.94, ws30 23.37 | ws22 -> ws30, at a t1 cadence, capped at ws30 by the jump bound 8 |
| 2026-08-14 08:37:30 | NO PASS | ws30 | - | none offered | ws30 25.54 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:36:20 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 09:35:00, ws1r reversed 09:36:20 inside the 120s grace from the cross bar 09:35:00, r 16.75 past the 44.0 fence, stamp 09:36:20, hold 6 bars \| rider ws30 4.18, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 09:36:20 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 09:39:30 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 09:37:40, ws1r reversed 09:39:30 inside the 120s grace from the cross bar 09:37:40, r 43.97 past the 44.0 fence, stamp 09:39:30, hold 6 bars \| rider ws30 4.18, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 09:39:30 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 09:41:20 | CADENCE | ws30 | - | none offered | t1 gcws30b oob 09:38:15..09:40:50, ws1r reversed 09:39:30 during, r 43.97 past the 44.0 fence, stamp 09:39:30, cross 09:40:55 hold 6 bars \| rider ws30 4.18, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 09:41:20 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:10 | NO PASS | ws30 | - | none offered | ws30 16.80 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:28:20 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 10:27:55, ws1r reversed 10:28:00 inside the 120s grace from the cross bar 10:27:55, r 4.45 past the 44.0 fence, stamp 10:28:00, hold 6 bars \| rider ws30 17.09, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 10:28:20 | TOP RESET | ws30 | ws1 | ws1 6.37 | ws30 17.09 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws1 |
| 2026-08-14 10:28:55 | NO PASS | ws1 | - | none offered | ws1 5.55 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:51:35 | CADENCE | ws1 | - | ws2 14.29, ws3 9.27, ws4 6.62 | t1 gcws30b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, r 35.89 past the 44.0 fence, stamp 10:48:55, cross 10:51:10 hold 6 bars \| rider ws1 26.63, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-14 10:51:35 | BATON | ws1 | ws4 | ws2 14.29, ws3 9.27, ws4 6.62 | ws1 -> ws4, at a t1 cadence, capped at ws9 by the jump bound 8 |
| 2026-08-14 10:52:45 | NO PASS | ws4 | - | none offered | ws4 13.26 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 11:16:00 | CADENCE | ws4 | - | ws5 6.86, ws6 0.00, ws7 2.07 | t1 gcws30b oob 11:11:30..11:15:30, ws1r reversed 11:15:20 during, r 8.28 past the 44.0 fence, stamp 11:15:20, cross 11:15:35 hold 6 bars \| rider ws4 0.00, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 11:16:00 | BATON | ws4 | ws7 | ws5 6.86, ws6 0.00, ws7 2.07 | ws4 -> ws7, at a t1 cadence, capped at ws12 by the jump bound 8 |
| 2026-08-14 11:19:40 | NO PASS | ws7 | - | none offered | ws7 15.89 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:02:25 | CADENCE | ws7 | - | ws12 32.25 | t1 gcws30b ib 12:02:00, ws1r reversed 12:02:25 inside the 120s grace from the cross bar 12:02:00, r 27.60 past the 44.0 fence, stamp 12:02:25, hold 6 bars \| rider ws7 79.53, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:02:25 | BATON | ws7 | ws12 | ws12 32.25 | ws7 -> ws12, at a t1 cadence, capped at ws15 by the jump bound 8 |
| 2026-08-14 12:12:20 | NO PASS | ws12 | - | none offered | ws12 29.50 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:16:00 | CADENCE | ws12 | - | ws16 22.22, ws17 14.61 | t1 gcws30b oob 12:14:20..12:15:30, ws1r reversed 12:14:45 during, r 19.40 past the 44.0 fence, stamp 12:14:45, cross 12:15:35 hold 6 bars \| rider ws12 31.53, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:16:00 | BATON | ws12 | ws17 | ws16 22.22, ws17 14.61 | ws12 -> ws17, at a t1 cadence, capped at ws20 by the jump bound 8 |
| 2026-08-14 12:25:40 | BATON | ws17 | ws18 | ws18 17.51 | ws17 -> ws18, between cadences, lin_hop 2 |
| 2026-08-14 12:32:15 | NO PASS | ws18 | - | none offered | ws18 16.43 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:46:35 | CADENCE | ws18 | - | ws19 20.59, ws20 18.22, ws23 9.99 | t1 gcws30b ib 12:46:10, ws1r reversed 12:46:15 inside the 120s grace from the cross bar 12:46:10, r 37.62 past the 44.0 fence, stamp 12:46:15, hold 6 bars \| rider ws18 20.14, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 12:46:35 | BATON | ws18 | ws23 | ws19 20.59, ws20 18.22, ws23 9.99 | ws18 -> ws23, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 12:48:30 | CADENCE | ws23 | - | ws30 14.70 | t1 gcws30b oob 12:46:45..12:48:00, ws1r reversed 12:47:55 during, r 31.66 past the 44.0 fence, stamp 12:47:55, cross 12:48:05 hold 6 bars \| rider ws23 9.99, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 12:48:30 | BATON | ws23 | ws30 | ws30 14.70 | ws23 -> ws30, at a t1 cadence, capped at ws31 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 13:03:10 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 13:02:30, ws1r reversed 13:03:10 inside the 120s grace from the cross bar 13:02:30, r 22.36 past the 44.0 fence, stamp 13:03:10, hold 6 bars \| rider ws30 15.38, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 13:03:10 | HOLD | ws30 | - | - | rider ws30 15.38 ex-fence and not reversed - no action |
| 2026-08-14 13:15:15 | NO PASS | ws30 | - | none offered | ws30 21.28 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:07:20 | CADENCE | ws30 | - | none offered | t1 gcws30b oob 14:04:20..14:06:50, ws1r reversed 14:06:45 during, r 17.33 past the 44.0 fence, stamp 14:06:45, cross 14:06:55 hold 6 bars \| rider ws30 34.89, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:07:20 | TOP RESET | ws30 | ws1 | ws1 14.01 | ws30 34.89 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws1 |
| 2026-08-14 14:08:55 | BATON | ws1 | ws2 | ws2 19.40 | ws1 -> ws2, between cadences, lin_hop 2 |
| 2026-08-14 14:11:20 | CADENCE | ws2 | - | none offered | t1 gcws30b oob 14:10:05..14:10:50, ws1r reversed 14:10:30 during, r 28.27 past the 44.0 fence, stamp 14:10:30, cross 14:10:55 hold 6 bars \| rider ws2 22.01, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 14:11:20 | EXHAUST | ws2 | - | - | t4 at a t1 cadence - rider ws2 22.01, no candidate at or below ws10 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-14 14:11:20 |
| baton passes made | 16 |
| minutes from the arm to the verdict | 432.3 |
| the rider chain | ws8 > ws11 > ws16 > ws17 > ws18 > ws19 > ws21 > ws22 > ws30 > ws1 > ws4 > ws7 > ws12 > ws17 > ws18 > ws23 > ws30 > ws1 > ws2 |

## MODE 'reversal+quarter' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | - | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 07:03:05 | RIDER | ws8 | - | - | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:13:05 | CADENCE | ws8 | - | ws9 17.07, ws10 0.40, ws11 9.12 | t1 gcws30b ib 07:12:40, ws1r reversed 07:13:00 inside the 120s grace from the cross bar 07:12:40, r 36.68 past the 44.0 fence, stamp 07:13:00, hold 6 bars \| rider ws8 10.75, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:13:05 | BATON | ws8 | ws11 | ws9 17.07, ws10 0.40, ws11 9.12 | ws8 -> ws11, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:35:00 | CADENCE | ws11 | - | ws12 11.52, ws13 3.33, ws14 3.21, ws15 9.04, ws16 9.72 | t1 gcws30b oob 07:32:10..07:34:30, ws1r reversed 07:34:30 during, r 17.51 past the 44.0 fence, stamp 07:34:30, cross 07:34:35 hold 6 bars \| rider ws11 6.80, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:35:00 | BATON | ws11 | ws16 | ws12 11.52, ws13 3.33, ws14 3.21, ws15 9.04, ws16 9.72 | ws11 -> ws16, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 07:45:05 | CADENCE | ws16 | - | ws17 1.79 | t1 gcws30b ib 07:43:30, ws1r reversed 07:45:05 inside the 120s grace from the cross bar 07:43:30, r 28.99 past the 44.0 fence, stamp 07:45:05, hold 6 bars \| rider ws16 4.43, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:45:05 | BATON | ws16 | ws17 | ws17 1.79 | ws16 -> ws17, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:55:55 | BATON | ws17 | ws19 | ws18 7.08, ws19 4.83 | ws17 -> ws19, between cadences, lin_hop 2 |
| 2026-08-14 08:13:35 | BATON | ws19 | ws21 | ws21 9.33 | ws19 -> ws21, between cadences, lin_hop 2 |
| 2026-08-14 08:14:30 | BATON | ws21 | ws22 | ws22 9.33 | ws21 -> ws22, between cadences, lin_hop 2 |
| 2026-08-14 08:14:55 | NO PASS | ws22 | - | none offered | ws22 9.02 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 08:25:20 | CADENCE | ws22 | - | ws24 4.57, ws25 10.94, ws30 23.37 | t1 gcws30b ib 08:24:55, ws1r reversed 08:25:05 inside the 120s grace from the cross bar 08:24:55, r 36.16 past the 44.0 fence, stamp 08:25:05, hold 6 bars \| rider ws22 9.02, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 08:25:20 | BATON | ws22 | ws30 | ws24 4.57, ws25 10.94, ws30 23.37 | ws22 -> ws30, at a t1 cadence, capped at ws30 by the jump bound 8 |
| 2026-08-14 08:44:05 | NO PASS | ws30 | - | none offered | ws30 21.05 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:36:20 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 09:35:00, ws1r reversed 09:36:20 inside the 120s grace from the cross bar 09:35:00, r 16.75 past the 44.0 fence, stamp 09:36:20, hold 6 bars \| rider ws30 4.18, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 09:36:20 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 09:39:30 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 09:37:40, ws1r reversed 09:39:30 inside the 120s grace from the cross bar 09:37:40, r 43.97 past the 44.0 fence, stamp 09:39:30, hold 6 bars \| rider ws30 4.18, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 09:39:30 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 09:41:20 | CADENCE | ws30 | - | none offered | t1 gcws30b oob 09:38:15..09:40:50, ws1r reversed 09:39:30 during, r 43.97 past the 44.0 fence, stamp 09:39:30, cross 09:40:55 hold 6 bars \| rider ws30 4.18, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 09:41:20 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 10:07:45 | NO PASS | ws30 | - | none offered | ws30 18.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:28:20 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 10:27:55, ws1r reversed 10:28:00 inside the 120s grace from the cross bar 10:27:55, r 4.45 past the 44.0 fence, stamp 10:28:00, hold 6 bars \| rider ws30 17.09, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 10:28:20 | TOP RESET | ws30 | ws1 | ws1 6.37 | ws30 17.09 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws1 |
| 2026-08-14 10:28:55 | NO PASS | ws1 | - | none offered | ws1 5.55 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:51:35 | CADENCE | ws1 | - | ws2 14.29, ws3 9.27, ws4 6.62 | t1 gcws30b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, r 35.89 past the 44.0 fence, stamp 10:48:55, cross 10:51:10 hold 6 bars \| rider ws1 26.63, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-14 10:51:35 | BATON | ws1 | ws4 | ws2 14.29, ws3 9.27, ws4 6.62 | ws1 -> ws4, at a t1 cadence, capped at ws9 by the jump bound 8 |
| 2026-08-14 10:52:50 | NO PASS | ws4 | - | none offered | ws4 13.26 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 11:16:00 | CADENCE | ws4 | - | ws5 6.86, ws6 0.00, ws7 2.07 | t1 gcws30b oob 11:11:30..11:15:30, ws1r reversed 11:15:20 during, r 8.28 past the 44.0 fence, stamp 11:15:20, cross 11:15:35 hold 6 bars \| rider ws4 0.00, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 11:16:00 | BATON | ws4 | ws7 | ws5 6.86, ws6 0.00, ws7 2.07 | ws4 -> ws7, at a t1 cadence, capped at ws12 by the jump bound 8 |
| 2026-08-14 11:20:30 | BATON | ws7 | ws8 | ws8 17.81 | ws7 -> ws8, between cadences, lin_hop 2 |
| 2026-08-14 11:20:45 | NO PASS | ws8 | - | none offered | ws8 16.71 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:02:25 | CADENCE | ws8 | - | ws12 32.25 | t1 gcws30b ib 12:02:00, ws1r reversed 12:02:25 inside the 120s grace from the cross bar 12:02:00, r 27.60 past the 44.0 fence, stamp 12:02:25, hold 6 bars \| rider ws8 76.60, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:02:25 | BATON | ws8 | ws12 | ws12 32.25 | ws8 -> ws12, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 12:03:00 | NO PASS | ws12 | - | none offered | ws12 34.88 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:16:00 | CADENCE | ws12 | - | ws16 22.22, ws17 14.61 | t1 gcws30b oob 12:14:20..12:15:30, ws1r reversed 12:14:45 during, r 19.40 past the 44.0 fence, stamp 12:14:45, cross 12:15:35 hold 6 bars \| rider ws12 31.53, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:16:00 | BATON | ws12 | ws17 | ws16 22.22, ws17 14.61 | ws12 -> ws17, at a t1 cadence, capped at ws20 by the jump bound 8 |
| 2026-08-14 12:29:00 | BATON | ws17 | ws18 | ws18 10.82 | ws17 -> ws18, between cadences, lin_hop 2 |
| 2026-08-14 12:35:50 | NO PASS | ws18 | - | none offered | ws18 15.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:46:35 | CADENCE | ws18 | - | ws19 20.59, ws20 18.22, ws23 9.99 | t1 gcws30b ib 12:46:10, ws1r reversed 12:46:15 inside the 120s grace from the cross bar 12:46:10, r 37.62 past the 44.0 fence, stamp 12:46:15, hold 6 bars \| rider ws18 20.14, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 12:46:35 | BATON | ws18 | ws23 | ws19 20.59, ws20 18.22, ws23 9.99 | ws18 -> ws23, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 12:48:30 | CADENCE | ws23 | - | ws30 14.70 | t1 gcws30b oob 12:46:45..12:48:00, ws1r reversed 12:47:55 during, r 31.66 past the 44.0 fence, stamp 12:47:55, cross 12:48:05 hold 6 bars \| rider ws23 9.99, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 12:48:30 | BATON | ws23 | ws30 | ws30 14.70 | ws23 -> ws30, at a t1 cadence, capped at ws31 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 13:03:10 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 13:02:30, ws1r reversed 13:03:10 inside the 120s grace from the cross bar 13:02:30, r 22.36 past the 44.0 fence, stamp 13:03:10, hold 6 bars \| rider ws30 15.38, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 13:03:10 | HOLD | ws30 | - | - | rider ws30 15.38 ex-fence and not reversed - no action |
| 2026-08-14 13:21:50 | NO PASS | ws30 | - | none offered | ws30 15.38 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:07:20 | CADENCE | ws30 | - | none offered | t1 gcws30b oob 14:04:20..14:06:50, ws1r reversed 14:06:45 during, r 17.33 past the 44.0 fence, stamp 14:06:45, cross 14:06:55 hold 6 bars \| rider ws30 34.89, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:07:20 | TOP RESET | ws30 | ws1 | ws1 14.01 | ws30 34.89 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws1 |
| 2026-08-14 14:08:55 | BATON | ws1 | ws2 | ws2 19.40 | ws1 -> ws2, between cadences, lin_hop 2 |
| 2026-08-14 14:11:20 | CADENCE | ws2 | - | none offered | t1 gcws30b oob 14:10:05..14:10:50, ws1r reversed 14:10:30 during, r 28.27 past the 44.0 fence, stamp 14:10:30, cross 14:10:55 hold 6 bars \| rider ws2 22.01, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 14:11:20 | EXHAUST | ws2 | - | - | t4 at a t1 cadence - rider ws2 22.01, no candidate at or below ws10 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-14 14:11:20 |
| baton passes made | 16 |
| minutes from the arm to the verdict | 432.3 |
| the rider chain | ws8 > ws11 > ws16 > ws17 > ws19 > ws21 > ws22 > ws30 > ws1 > ws4 > ws7 > ws8 > ws12 > ws17 > ws18 > ws23 > ws30 > ws1 > ws2 |

## MODE 'ib' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 06:59:00 | RETEST | - | ws1r 12.95 oob + ws2r 52.91 / ws3r 70.72 in - the gate opens; ws1r oob->ib cross 2026-08-14 07:02:10, wob 12, cadence at 2026-08-14 07:03:05 |
| 2026-08-14 07:03:05 | RIDER | ws8 | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:13:05 | LATCH1 | ws8 | latch 1 at the t1 cadence 2026-08-14 07:13:05, divergence state -1 |
| 2026-08-14 07:13:05 | CADENCE | ws8 | t1 gcws30b ib 07:12:40, ws1r reversed 07:13:00 inside the 120s grace from the cross bar 07:12:40, r 36.68 past the 44.0 fence, stamp 07:13:00, hold 6 bars \| rider ws8 10.75, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:13:05 | BATON | ws8 | ws8 -> ws11, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:35:00 | LATCH1 | ws11 | latch 1 at the t1 cadence 2026-08-14 07:35:00, divergence state -1 |
| 2026-08-14 07:35:00 | CADENCE | ws11 | t1 gcws30b oob 07:32:10..07:34:30, ws1r reversed 07:34:30 during, r 17.51 past the 44.0 fence, stamp 07:34:30, cross 07:34:35 hold 6 bars \| rider ws11 6.80, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:35:00 | BATON | ws11 | ws11 -> ws16, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 07:45:05 | LATCH1 | ws16 | latch 1 at the t1 cadence 2026-08-14 07:45:05, divergence state -1 |
| 2026-08-14 07:45:05 | CADENCE | ws16 | t1 gcws30b ib 07:43:30, ws1r reversed 07:45:05 inside the 120s grace from the cross bar 07:43:30, r 28.99 past the 44.0 fence, stamp 07:45:05, hold 6 bars \| rider ws16 4.43, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:45:05 | BATON | ws16 | ws16 -> ws17, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 08:10:10 | BATON | ws17 | ws17 -> ws19, between cadences, lin_hop 2 |
| 2026-08-14 08:16:55 | BATON | ws19 | ws19 -> ws21, between cadences, lin_hop 2 |
| 2026-08-14 08:25:20 | CADENCE | ws21 | t1 gcws30b ib 08:24:55, ws1r reversed 08:25:05 inside the 120s grace from the cross bar 08:24:55, r 36.16 past the 44.0 fence, stamp 08:25:05, hold 6 bars \| rider ws21 16.07, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 08:25:20 | BATON | ws21 | ws21 -> ws25, at a t1 cadence, capped at ws29 by the jump bound 8 |
| 2026-08-14 08:35:10 | BATON | ws25 | ws25 -> ws27, between cadences, lin_hop 2 |
| 2026-08-14 08:35:55 | BATON | ws27 | ws27 -> ws28, between cadences, lin_hop 2 |
| 2026-08-14 08:48:30 | NO PASS | ws28 | ws28 17.33 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:36:20 | LATCH1 | ws28 | latch 1 at the t1 cadence 2026-08-14 09:36:20, divergence state -1 |
| 2026-08-14 09:36:20 | CADENCE | ws28 | t1 gcws30b ib 09:35:00, ws1r reversed 09:36:20 inside the 120s grace from the cross bar 09:35:00, r 16.75 past the 44.0 fence, stamp 09:36:20, hold 6 bars \| rider ws28 1.10, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 09:36:20 | BATON | ws28 | ws28 -> ws30, at a t1 cadence, capped at ws36 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 09:39:30 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:39:30, divergence state -1 |
| 2026-08-14 09:39:30 | CADENCE | ws30 | t1 gcws30b ib 09:37:40, ws1r reversed 09:39:30 inside the 120s grace from the cross bar 09:37:40, r 43.97 past the 44.0 fence, stamp 09:39:30, hold 6 bars \| rider ws30 4.18, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 09:39:30 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 09:41:20 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:41:20, divergence state -1 |
| 2026-08-14 09:41:20 | CADENCE | ws30 | t1 gcws30b oob 09:38:15..09:40:50, ws1r reversed 09:39:30 during, r 43.97 past the 44.0 fence, stamp 09:39:30, cross 09:40:55 hold 6 bars \| rider ws30 4.18, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 09:41:20 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:40 | NO PASS | ws30 | ws30 18.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:28:20 | CADENCE | ws30 | t1 gcws30b ib 10:27:55, ws1r reversed 10:28:00 inside the 120s grace from the cross bar 10:27:55, r 4.45 past the 44.0 fence, stamp 10:28:00, hold 6 bars \| rider ws30 17.09, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 10:28:20 | TOP RESET | ws30 | ws30 17.09 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws1 |
| 2026-08-14 10:30:15 | NO PASS | ws1 | ws1 30.89 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:51:35 | LATCH1 | ws1 | latch 1 at the t1 cadence 2026-08-14 10:51:35, divergence state -1 |
| 2026-08-14 10:51:35 | CADENCE | ws1 | t1 gcws30b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, r 35.89 past the 44.0 fence, stamp 10:48:55, cross 10:51:10 hold 6 bars \| rider ws1 26.63, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-14 10:51:35 | BATON | ws1 | ws1 -> ws4, at a t1 cadence, capped at ws9 by the jump bound 8 |
| 2026-08-14 11:16:00 | LATCH1 | ws4 | latch 1 at the t1 cadence 2026-08-14 11:16:00, divergence state -1 |
| 2026-08-14 11:16:00 | CADENCE | ws4 | t1 gcws30b oob 11:11:30..11:15:30, ws1r reversed 11:15:20 during, r 8.28 past the 44.0 fence, stamp 11:15:20, cross 11:15:35 hold 6 bars \| rider ws4 0.00, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 11:16:00 | BATON | ws4 | ws4 -> ws7, at a t1 cadence, capped at ws12 by the jump bound 8 |
| 2026-08-14 11:26:55 | BATON | ws7 | ws7 -> ws9, between cadences, lin_hop 2 |
| 2026-08-14 11:33:55 | BATON | ws9 | ws9 -> ws11, between cadences, lin_hop 2 |
| 2026-08-14 11:37:50 | NO PASS | ws11 | ws11 16.97 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:02:25 | CADENCE | ws11 | t1 gcws30b ib 12:02:00, ws1r reversed 12:02:25 inside the 120s grace from the cross bar 12:02:00, r 27.60 past the 44.0 fence, stamp 12:02:25, hold 6 bars \| rider ws11 32.71, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 12:02:25 | BATON | ws11 | ws11 -> ws12, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 12:16:00 | LATCH1 | ws12 | latch 1 at the t1 cadence 2026-08-14 12:16:00, divergence state -1 |
| 2026-08-14 12:16:00 | CADENCE | ws12 | t1 gcws30b oob 12:14:20..12:15:30, ws1r reversed 12:14:45 during, r 19.40 past the 44.0 fence, stamp 12:14:45, cross 12:15:35 hold 6 bars \| rider ws12 31.53, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:16:00 | BATON | ws12 | ws12 -> ws17, at a t1 cadence, capped at ws20 by the jump bound 8 |
| 2026-08-14 12:25:45 | BATON | ws17 | ws17 -> ws18, between cadences, lin_hop 2 |
| 2026-08-14 12:32:20 | NO PASS | ws18 | ws18 16.43 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:46:35 | LATCH1 | ws18 | latch 1 at the t1 cadence 2026-08-14 12:46:35, divergence state -1 |
| 2026-08-14 12:46:35 | CADENCE | ws18 | t1 gcws30b ib 12:46:10, ws1r reversed 12:46:15 inside the 120s grace from the cross bar 12:46:10, r 37.62 past the 44.0 fence, stamp 12:46:15, hold 6 bars \| rider ws18 20.14, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 12:46:35 | BATON | ws18 | ws18 -> ws23, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 12:48:30 | LATCH1 | ws23 | latch 1 at the t1 cadence 2026-08-14 12:48:30, divergence state -1 |
| 2026-08-14 12:48:30 | CADENCE | ws23 | t1 gcws30b oob 12:46:45..12:48:00, ws1r reversed 12:47:55 during, r 31.66 past the 44.0 fence, stamp 12:47:55, cross 12:48:05 hold 6 bars \| rider ws23 9.99, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 12:48:30 | BATON | ws23 | ws23 -> ws30, at a t1 cadence, capped at ws31 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 12:50:50 | NO PASS | ws30 | ws30 16.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 13:03:10 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 13:03:10, divergence state -1 |
| 2026-08-14 13:03:10 | CADENCE | ws30 | t1 gcws30b ib 13:02:30, ws1r reversed 13:03:10 inside the 120s grace from the cross bar 13:02:30, r 22.36 past the 44.0 fence, stamp 13:03:10, hold 6 bars \| rider ws30 15.38, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 13:03:10 | HOLD | ws30 | rider ws30 15.38 ex-fence and not reversed - no action |
| 2026-08-14 13:28:55 | NO PASS | ws30 | ws30 26.30 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:07:20 | CADENCE | ws30 | t1 gcws30b oob 14:04:20..14:06:50, ws1r reversed 14:06:45 during, r 17.33 past the 44.0 fence, stamp 14:06:45, cross 14:06:55 hold 6 bars \| rider ws30 34.89, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:07:20 | TOP RESET | ws30 | ws30 34.89 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws1 |
| 2026-08-14 14:08:55 | BATON | ws1 | ws1 -> ws2, between cadences, lin_hop 2 |
| 2026-08-14 14:11:20 | LATCH1 | ws2 | latch 1 at the t1 cadence 2026-08-14 14:11:20, divergence state -1 |
| 2026-08-14 14:11:20 | CADENCE | ws2 | t1 gcws30b oob 14:10:05..14:10:50, ws1r reversed 14:10:30 during, r 28.27 past the 44.0 fence, stamp 14:10:30, cross 14:10:55 hold 6 bars \| rider ws2 22.01, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 14:11:20 | EXHAUST | ws2 | t4 at a t1 cadence - rider ws2 22.01, no candidate at or below ws10 (the jump bound 8) |

## MODE 'reversal' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 06:59:00 | RETEST | - | ws1r 12.95 oob + ws2r 52.91 / ws3r 70.72 in - the gate opens; ws1r oob->ib cross 2026-08-14 07:02:10, wob 12, cadence at 2026-08-14 07:03:05 |
| 2026-08-14 07:03:05 | RIDER | ws8 | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:13:05 | LATCH1 | ws8 | latch 1 at the t1 cadence 2026-08-14 07:13:05, divergence state -1 |
| 2026-08-14 07:13:05 | CADENCE | ws8 | t1 gcws30b ib 07:12:40, ws1r reversed 07:13:00 inside the 120s grace from the cross bar 07:12:40, r 36.68 past the 44.0 fence, stamp 07:13:00, hold 6 bars \| rider ws8 10.75, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:13:05 | BATON | ws8 | ws8 -> ws11, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:35:00 | LATCH1 | ws11 | latch 1 at the t1 cadence 2026-08-14 07:35:00, divergence state -1 |
| 2026-08-14 07:35:00 | CADENCE | ws11 | t1 gcws30b oob 07:32:10..07:34:30, ws1r reversed 07:34:30 during, r 17.51 past the 44.0 fence, stamp 07:34:30, cross 07:34:35 hold 6 bars \| rider ws11 6.80, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:35:00 | BATON | ws11 | ws11 -> ws16, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 07:45:05 | LATCH1 | ws16 | latch 1 at the t1 cadence 2026-08-14 07:45:05, divergence state -1 |
| 2026-08-14 07:45:05 | CADENCE | ws16 | t1 gcws30b ib 07:43:30, ws1r reversed 07:45:05 inside the 120s grace from the cross bar 07:43:30, r 28.99 past the 44.0 fence, stamp 07:45:05, hold 6 bars \| rider ws16 4.43, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:45:05 | BATON | ws16 | ws16 -> ws17, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:52:35 | BATON | ws17 | ws17 -> ws18, between cadences, lin_hop 2 |
| 2026-08-14 08:06:55 | BATON | ws18 | ws18 -> ws19, between cadences, lin_hop 2 |
| 2026-08-14 08:09:45 | BATON | ws19 | ws19 -> ws21, between cadences, lin_hop 2 |
| 2026-08-14 08:10:10 | BATON | ws21 | ws21 -> ws22, between cadences, lin_hop 2 |
| 2026-08-14 08:10:20 | NO PASS | ws22 | ws22 12.34 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 08:25:20 | CADENCE | ws22 | t1 gcws30b ib 08:24:55, ws1r reversed 08:25:05 inside the 120s grace from the cross bar 08:24:55, r 36.16 past the 44.0 fence, stamp 08:25:05, hold 6 bars \| rider ws22 9.02, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 08:25:20 | BATON | ws22 | ws22 -> ws30, at a t1 cadence, capped at ws30 by the jump bound 8 |
| 2026-08-14 08:37:30 | NO PASS | ws30 | ws30 25.54 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:36:20 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:36:20, divergence state -1 |
| 2026-08-14 09:36:20 | CADENCE | ws30 | t1 gcws30b ib 09:35:00, ws1r reversed 09:36:20 inside the 120s grace from the cross bar 09:35:00, r 16.75 past the 44.0 fence, stamp 09:36:20, hold 6 bars \| rider ws30 4.18, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 09:36:20 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 09:39:30 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:39:30, divergence state -1 |
| 2026-08-14 09:39:30 | CADENCE | ws30 | t1 gcws30b ib 09:37:40, ws1r reversed 09:39:30 inside the 120s grace from the cross bar 09:37:40, r 43.97 past the 44.0 fence, stamp 09:39:30, hold 6 bars \| rider ws30 4.18, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 09:39:30 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 09:41:20 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:41:20, divergence state -1 |
| 2026-08-14 09:41:20 | CADENCE | ws30 | t1 gcws30b oob 09:38:15..09:40:50, ws1r reversed 09:39:30 during, r 43.97 past the 44.0 fence, stamp 09:39:30, cross 09:40:55 hold 6 bars \| rider ws30 4.18, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 09:41:20 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:10 | NO PASS | ws30 | ws30 16.80 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:28:20 | CADENCE | ws30 | t1 gcws30b ib 10:27:55, ws1r reversed 10:28:00 inside the 120s grace from the cross bar 10:27:55, r 4.45 past the 44.0 fence, stamp 10:28:00, hold 6 bars \| rider ws30 17.09, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 10:28:20 | TOP RESET | ws30 | ws30 17.09 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws1 |
| 2026-08-14 10:28:55 | NO PASS | ws1 | ws1 5.55 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:51:35 | LATCH1 | ws1 | latch 1 at the t1 cadence 2026-08-14 10:51:35, divergence state -1 |
| 2026-08-14 10:51:35 | CADENCE | ws1 | t1 gcws30b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, r 35.89 past the 44.0 fence, stamp 10:48:55, cross 10:51:10 hold 6 bars \| rider ws1 26.63, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-14 10:51:35 | BATON | ws1 | ws1 -> ws4, at a t1 cadence, capped at ws9 by the jump bound 8 |
| 2026-08-14 10:52:45 | NO PASS | ws4 | ws4 13.26 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 11:16:00 | LATCH1 | ws4 | latch 1 at the t1 cadence 2026-08-14 11:16:00, divergence state -1 |
| 2026-08-14 11:16:00 | CADENCE | ws4 | t1 gcws30b oob 11:11:30..11:15:30, ws1r reversed 11:15:20 during, r 8.28 past the 44.0 fence, stamp 11:15:20, cross 11:15:35 hold 6 bars \| rider ws4 0.00, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 11:16:00 | BATON | ws4 | ws4 -> ws7, at a t1 cadence, capped at ws12 by the jump bound 8 |
| 2026-08-14 11:19:40 | NO PASS | ws7 | ws7 15.89 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:02:25 | CADENCE | ws7 | t1 gcws30b ib 12:02:00, ws1r reversed 12:02:25 inside the 120s grace from the cross bar 12:02:00, r 27.60 past the 44.0 fence, stamp 12:02:25, hold 6 bars \| rider ws7 79.53, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:02:25 | BATON | ws7 | ws7 -> ws12, at a t1 cadence, capped at ws15 by the jump bound 8 |
| 2026-08-14 12:12:20 | NO PASS | ws12 | ws12 29.50 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:16:00 | LATCH1 | ws12 | latch 1 at the t1 cadence 2026-08-14 12:16:00, divergence state -1 |
| 2026-08-14 12:16:00 | CADENCE | ws12 | t1 gcws30b oob 12:14:20..12:15:30, ws1r reversed 12:14:45 during, r 19.40 past the 44.0 fence, stamp 12:14:45, cross 12:15:35 hold 6 bars \| rider ws12 31.53, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:16:00 | BATON | ws12 | ws12 -> ws17, at a t1 cadence, capped at ws20 by the jump bound 8 |
| 2026-08-14 12:25:40 | BATON | ws17 | ws17 -> ws18, between cadences, lin_hop 2 |
| 2026-08-14 12:32:15 | NO PASS | ws18 | ws18 16.43 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:46:35 | LATCH1 | ws18 | latch 1 at the t1 cadence 2026-08-14 12:46:35, divergence state -1 |
| 2026-08-14 12:46:35 | CADENCE | ws18 | t1 gcws30b ib 12:46:10, ws1r reversed 12:46:15 inside the 120s grace from the cross bar 12:46:10, r 37.62 past the 44.0 fence, stamp 12:46:15, hold 6 bars \| rider ws18 20.14, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 12:46:35 | BATON | ws18 | ws18 -> ws23, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 12:48:30 | LATCH1 | ws23 | latch 1 at the t1 cadence 2026-08-14 12:48:30, divergence state -1 |
| 2026-08-14 12:48:30 | CADENCE | ws23 | t1 gcws30b oob 12:46:45..12:48:00, ws1r reversed 12:47:55 during, r 31.66 past the 44.0 fence, stamp 12:47:55, cross 12:48:05 hold 6 bars \| rider ws23 9.99, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 12:48:30 | BATON | ws23 | ws23 -> ws30, at a t1 cadence, capped at ws31 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 13:03:10 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 13:03:10, divergence state -1 |
| 2026-08-14 13:03:10 | CADENCE | ws30 | t1 gcws30b ib 13:02:30, ws1r reversed 13:03:10 inside the 120s grace from the cross bar 13:02:30, r 22.36 past the 44.0 fence, stamp 13:03:10, hold 6 bars \| rider ws30 15.38, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 13:03:10 | HOLD | ws30 | rider ws30 15.38 ex-fence and not reversed - no action |
| 2026-08-14 13:15:15 | NO PASS | ws30 | ws30 21.28 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:07:20 | CADENCE | ws30 | t1 gcws30b oob 14:04:20..14:06:50, ws1r reversed 14:06:45 during, r 17.33 past the 44.0 fence, stamp 14:06:45, cross 14:06:55 hold 6 bars \| rider ws30 34.89, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:07:20 | TOP RESET | ws30 | ws30 34.89 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws1 |
| 2026-08-14 14:08:55 | BATON | ws1 | ws1 -> ws2, between cadences, lin_hop 2 |
| 2026-08-14 14:11:20 | LATCH1 | ws2 | latch 1 at the t1 cadence 2026-08-14 14:11:20, divergence state -1 |
| 2026-08-14 14:11:20 | CADENCE | ws2 | t1 gcws30b oob 14:10:05..14:10:50, ws1r reversed 14:10:30 during, r 28.27 past the 44.0 fence, stamp 14:10:30, cross 14:10:55 hold 6 bars \| rider ws2 22.01, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 14:11:20 | EXHAUST | ws2 | t4 at a t1 cadence - rider ws2 22.01, no candidate at or below ws10 (the jump bound 8) |

## MODE 'reversal+quarter' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 06:59:00 | RETEST | - | ws1r 12.95 oob + ws2r 52.91 / ws3r 70.72 in - the gate opens; ws1r oob->ib cross 2026-08-14 07:02:10, wob 12, cadence at 2026-08-14 07:03:05 |
| 2026-08-14 07:03:05 | RIDER | ws8 | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:13:05 | LATCH1 | ws8 | latch 1 at the t1 cadence 2026-08-14 07:13:05, divergence state -1 |
| 2026-08-14 07:13:05 | CADENCE | ws8 | t1 gcws30b ib 07:12:40, ws1r reversed 07:13:00 inside the 120s grace from the cross bar 07:12:40, r 36.68 past the 44.0 fence, stamp 07:13:00, hold 6 bars \| rider ws8 10.75, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:13:05 | BATON | ws8 | ws8 -> ws11, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:35:00 | LATCH1 | ws11 | latch 1 at the t1 cadence 2026-08-14 07:35:00, divergence state -1 |
| 2026-08-14 07:35:00 | CADENCE | ws11 | t1 gcws30b oob 07:32:10..07:34:30, ws1r reversed 07:34:30 during, r 17.51 past the 44.0 fence, stamp 07:34:30, cross 07:34:35 hold 6 bars \| rider ws11 6.80, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:35:00 | BATON | ws11 | ws11 -> ws16, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 07:45:05 | LATCH1 | ws16 | latch 1 at the t1 cadence 2026-08-14 07:45:05, divergence state -1 |
| 2026-08-14 07:45:05 | CADENCE | ws16 | t1 gcws30b ib 07:43:30, ws1r reversed 07:45:05 inside the 120s grace from the cross bar 07:43:30, r 28.99 past the 44.0 fence, stamp 07:45:05, hold 6 bars \| rider ws16 4.43, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:45:05 | BATON | ws16 | ws16 -> ws17, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:55:55 | BATON | ws17 | ws17 -> ws19, between cadences, lin_hop 2 |
| 2026-08-14 08:13:35 | BATON | ws19 | ws19 -> ws21, between cadences, lin_hop 2 |
| 2026-08-14 08:14:30 | BATON | ws21 | ws21 -> ws22, between cadences, lin_hop 2 |
| 2026-08-14 08:14:55 | NO PASS | ws22 | ws22 9.02 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 08:25:20 | CADENCE | ws22 | t1 gcws30b ib 08:24:55, ws1r reversed 08:25:05 inside the 120s grace from the cross bar 08:24:55, r 36.16 past the 44.0 fence, stamp 08:25:05, hold 6 bars \| rider ws22 9.02, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 08:25:20 | BATON | ws22 | ws22 -> ws30, at a t1 cadence, capped at ws30 by the jump bound 8 |
| 2026-08-14 08:44:05 | NO PASS | ws30 | ws30 21.05 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:36:20 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:36:20, divergence state -1 |
| 2026-08-14 09:36:20 | CADENCE | ws30 | t1 gcws30b ib 09:35:00, ws1r reversed 09:36:20 inside the 120s grace from the cross bar 09:35:00, r 16.75 past the 44.0 fence, stamp 09:36:20, hold 6 bars \| rider ws30 4.18, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 09:36:20 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 09:39:30 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:39:30, divergence state -1 |
| 2026-08-14 09:39:30 | CADENCE | ws30 | t1 gcws30b ib 09:37:40, ws1r reversed 09:39:30 inside the 120s grace from the cross bar 09:37:40, r 43.97 past the 44.0 fence, stamp 09:39:30, hold 6 bars \| rider ws30 4.18, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 09:39:30 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 09:41:20 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:41:20, divergence state -1 |
| 2026-08-14 09:41:20 | CADENCE | ws30 | t1 gcws30b oob 09:38:15..09:40:50, ws1r reversed 09:39:30 during, r 43.97 past the 44.0 fence, stamp 09:39:30, cross 09:40:55 hold 6 bars \| rider ws30 4.18, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 09:41:20 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 10:07:45 | NO PASS | ws30 | ws30 18.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:28:20 | CADENCE | ws30 | t1 gcws30b ib 10:27:55, ws1r reversed 10:28:00 inside the 120s grace from the cross bar 10:27:55, r 4.45 past the 44.0 fence, stamp 10:28:00, hold 6 bars \| rider ws30 17.09, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 10:28:20 | TOP RESET | ws30 | ws30 17.09 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws1 |
| 2026-08-14 10:28:55 | NO PASS | ws1 | ws1 5.55 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:51:35 | LATCH1 | ws1 | latch 1 at the t1 cadence 2026-08-14 10:51:35, divergence state -1 |
| 2026-08-14 10:51:35 | CADENCE | ws1 | t1 gcws30b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, r 35.89 past the 44.0 fence, stamp 10:48:55, cross 10:51:10 hold 6 bars \| rider ws1 26.63, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-14 10:51:35 | BATON | ws1 | ws1 -> ws4, at a t1 cadence, capped at ws9 by the jump bound 8 |
| 2026-08-14 10:52:50 | NO PASS | ws4 | ws4 13.26 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 11:16:00 | LATCH1 | ws4 | latch 1 at the t1 cadence 2026-08-14 11:16:00, divergence state -1 |
| 2026-08-14 11:16:00 | CADENCE | ws4 | t1 gcws30b oob 11:11:30..11:15:30, ws1r reversed 11:15:20 during, r 8.28 past the 44.0 fence, stamp 11:15:20, cross 11:15:35 hold 6 bars \| rider ws4 0.00, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 11:16:00 | BATON | ws4 | ws4 -> ws7, at a t1 cadence, capped at ws12 by the jump bound 8 |
| 2026-08-14 11:20:30 | BATON | ws7 | ws7 -> ws8, between cadences, lin_hop 2 |
| 2026-08-14 11:20:45 | NO PASS | ws8 | ws8 16.71 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:02:25 | CADENCE | ws8 | t1 gcws30b ib 12:02:00, ws1r reversed 12:02:25 inside the 120s grace from the cross bar 12:02:00, r 27.60 past the 44.0 fence, stamp 12:02:25, hold 6 bars \| rider ws8 76.60, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:02:25 | BATON | ws8 | ws8 -> ws12, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 12:03:00 | NO PASS | ws12 | ws12 34.88 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:16:00 | LATCH1 | ws12 | latch 1 at the t1 cadence 2026-08-14 12:16:00, divergence state -1 |
| 2026-08-14 12:16:00 | CADENCE | ws12 | t1 gcws30b oob 12:14:20..12:15:30, ws1r reversed 12:14:45 during, r 19.40 past the 44.0 fence, stamp 12:14:45, cross 12:15:35 hold 6 bars \| rider ws12 31.53, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:16:00 | BATON | ws12 | ws12 -> ws17, at a t1 cadence, capped at ws20 by the jump bound 8 |
| 2026-08-14 12:29:00 | BATON | ws17 | ws17 -> ws18, between cadences, lin_hop 2 |
| 2026-08-14 12:35:50 | NO PASS | ws18 | ws18 15.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:46:35 | LATCH1 | ws18 | latch 1 at the t1 cadence 2026-08-14 12:46:35, divergence state -1 |
| 2026-08-14 12:46:35 | CADENCE | ws18 | t1 gcws30b ib 12:46:10, ws1r reversed 12:46:15 inside the 120s grace from the cross bar 12:46:10, r 37.62 past the 44.0 fence, stamp 12:46:15, hold 6 bars \| rider ws18 20.14, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 12:46:35 | BATON | ws18 | ws18 -> ws23, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 12:48:30 | LATCH1 | ws23 | latch 1 at the t1 cadence 2026-08-14 12:48:30, divergence state -1 |
| 2026-08-14 12:48:30 | CADENCE | ws23 | t1 gcws30b oob 12:46:45..12:48:00, ws1r reversed 12:47:55 during, r 31.66 past the 44.0 fence, stamp 12:47:55, cross 12:48:05 hold 6 bars \| rider ws23 9.99, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 12:48:30 | BATON | ws23 | ws23 -> ws30, at a t1 cadence, capped at ws31 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 13:03:10 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 13:03:10, divergence state -1 |
| 2026-08-14 13:03:10 | CADENCE | ws30 | t1 gcws30b ib 13:02:30, ws1r reversed 13:03:10 inside the 120s grace from the cross bar 13:02:30, r 22.36 past the 44.0 fence, stamp 13:03:10, hold 6 bars \| rider ws30 15.38, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 13:03:10 | HOLD | ws30 | rider ws30 15.38 ex-fence and not reversed - no action |
| 2026-08-14 13:21:50 | NO PASS | ws30 | ws30 15.38 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:07:20 | CADENCE | ws30 | t1 gcws30b oob 14:04:20..14:06:50, ws1r reversed 14:06:45 during, r 17.33 past the 44.0 fence, stamp 14:06:45, cross 14:06:55 hold 6 bars \| rider ws30 34.89, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:07:20 | TOP RESET | ws30 | ws30 34.89 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws1 |
| 2026-08-14 14:08:55 | BATON | ws1 | ws1 -> ws2, between cadences, lin_hop 2 |
| 2026-08-14 14:11:20 | LATCH1 | ws2 | latch 1 at the t1 cadence 2026-08-14 14:11:20, divergence state -1 |
| 2026-08-14 14:11:20 | CADENCE | ws2 | t1 gcws30b oob 14:10:05..14:10:50, ws1r reversed 14:10:30 during, r 28.27 past the 44.0 fence, stamp 14:10:30, cross 14:10:55 hold 6 bars \| rider ws2 22.01, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 14:11:20 | EXHAUST | ws2 | t4 at a t1 cadence - rider ws2 22.01, no candidate at or below ws10 (the jump bound 8) |
