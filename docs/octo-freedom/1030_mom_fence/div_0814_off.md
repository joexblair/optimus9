# LINEAGE2 BATON CHAIN - THE ARM IS HANDED IN AT 2026-08-14 06:59:00, SIDE low
# TAPE 1632960 bars | B 2026-10-04 23:59:55, the last tape bar, no end bound | RULED_OK True

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
| 2026-08-14 07:13:05 | CADENCE | ws8 | - | ws10 0.40, ws11 9.12, ws12 14.92, ws13 20.95, ws16 23.48 | t1 gcws30b ib 07:12:40, ws1r reversed 07:13:00 inside the 120s grace from the cross bar 07:12:40, r 36.68 past the 44.0 fence, stamp 07:13:00, hold 6 bars \| rider ws8 10.75, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 07:13:05 | BATON | ws8 | ws16 | ws10 0.40, ws11 9.12, ws12 14.92, ws13 20.95, ws16 23.48 | ws8 -> ws16, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:35:00 | CADENCE | ws16 | - | ws17 16.07, ws18 18.32 | t1 gcws30b oob 07:32:10..07:34:30, ws1r reversed 07:34:30 during, r 17.51 past the 44.0 fence, stamp 07:34:30, cross 07:34:35 hold 6 bars \| rider ws16 9.72, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 07:35:00 | BATON | ws16 | ws18 | ws17 16.07, ws18 18.32 | ws16 -> ws18, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:45:05 | CADENCE | ws18 | - | ws19 15.43, ws20 22.92, ws21 15.06, ws22 16.37 | t1 gcws30b ib 07:43:30, ws1r reversed 07:45:05 inside the 120s grace from the cross bar 07:43:30, r 28.99 past the 44.0 fence, stamp 07:45:05, hold 6 bars \| rider ws18 17.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:45:05 | BATON | ws18 | ws22 | ws19 15.43, ws20 22.92, ws21 15.06, ws22 16.37 | ws18 -> ws22, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 08:10:00 | BATON | ws22 | ws24 | ws23 19.09, ws24 20.02 | ws22 -> ws24, between cadences, lin_hop 2 |
| 2026-08-14 08:25:20 | CADENCE | ws24 | - | ws25 10.94, ws30 23.37 | t1 gcws30b ib 08:24:55, ws1r reversed 08:25:05 inside the 120s grace from the cross bar 08:24:55, r 36.16 past the 44.0 fence, stamp 08:25:05, hold 6 bars \| rider ws24 4.57, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 08:25:20 | BATON | ws24 | ws30 | ws25 10.94, ws30 23.37 | ws24 -> ws30, at a t1 cadence, capped at ws32 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 09:14:10 | NO PASS | ws30 | - | none offered | ws30 9.90 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:36:20 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 09:35:00, ws1r reversed 09:36:20 inside the 120s grace from the cross bar 09:35:00, r 16.75 past the 44.0 fence, stamp 09:36:20, hold 6 bars \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-14 09:36:20 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 09:39:30 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 09:37:40, ws1r reversed 09:39:30 inside the 120s grace from the cross bar 09:37:40, r 43.97 past the 44.0 fence, stamp 09:39:30, hold 6 bars \| rider ws30 4.18, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-14 09:39:30 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 09:41:20 | CADENCE | ws30 | - | none offered | t1 gcws30b oob 09:38:15..09:40:50, ws1r reversed 09:39:30 during, r 43.97 past the 44.0 fence, stamp 09:39:30, cross 09:40:55 hold 6 bars \| rider ws30 4.18, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-14 09:41:20 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:40 | NO PASS | ws30 | - | none offered | ws30 18.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:28:20 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 10:27:55, ws1r reversed 10:28:00 inside the 120s grace from the cross bar 10:27:55, r 4.45 past the 44.0 fence, stamp 10:28:00, hold 6 bars \| rider ws30 17.09, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:28:20 | TOP RESET | ws30 | ws2 | ws1 6.37, ws2 22.67 | ws30 17.09 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-08-14 10:36:35 | BATON | ws2 | ws3 | ws3 19.41 | ws2 -> ws3, between cadences, lin_hop 2 |
| 2026-08-14 10:51:35 | CADENCE | ws3 | - | ws4 6.62, ws5 16.16, ws7 42.95 | t1 gcws30b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, r 35.89 past the 44.0 fence, stamp 10:48:55, cross 10:51:10 hold 6 bars \| rider ws3 9.27, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 10:51:35 | BATON | ws3 | ws7 | ws4 6.62, ws5 16.16, ws7 42.95 | ws3 -> ws7, at a t1 cadence, capped at ws11 by the jump bound 8 |
| 2026-08-14 11:16:00 | CADENCE | ws7 | - | ws8 11.35, ws9 12.32 | t1 gcws30b oob 11:11:30..11:15:30, ws1r reversed 11:15:20 during, r 8.28 past the 44.0 fence, stamp 11:15:20, cross 11:15:35 hold 6 bars \| rider ws7 2.07, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 11:16:00 | BATON | ws7 | ws9 | ws8 11.35, ws9 12.32 | ws7 -> ws9, at a t1 cadence, capped at ws15 by the jump bound 8 |
| 2026-08-14 11:19:20 | NO PASS | ws9 | - | none offered | ws9 18.29 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:02:25 | CADENCE | ws9 | - | ws14 25.30, ws17 23.23 | t1 gcws30b ib 12:02:00, ws1r reversed 12:02:25 inside the 120s grace from the cross bar 12:02:00, r 27.60 past the 44.0 fence, stamp 12:02:25, hold 6 bars \| rider ws9 67.46, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:02:25 | BATON | ws9 | ws17 | ws14 25.30, ws17 23.23 | ws9 -> ws17, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-08-14 12:16:00 | CADENCE | ws17 | - | ws18 25.32 | t1 gcws30b oob 12:14:20..12:15:30, ws1r reversed 12:14:45 during, r 19.40 past the 44.0 fence, stamp 12:14:45, cross 12:15:35 hold 6 bars \| rider ws17 14.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 12:16:00 | BATON | ws17 | ws18 | ws18 25.32 | ws17 -> ws18, at a t1 cadence, capped at ws25 by the jump bound 8 |
| 2026-08-14 12:25:15 | BATON | ws18 | ws20 | ws19 27.83, ws20 24.52 | ws18 -> ws20, between cadences, lin_hop 2 |
| 2026-08-14 12:46:35 | CADENCE | ws20 | - | ws22 16.71, ws23 9.99 | t1 gcws30b ib 12:46:10, ws1r reversed 12:46:15 inside the 120s grace from the cross bar 12:46:10, r 37.62 past the 44.0 fence, stamp 12:46:15, hold 6 bars \| rider ws20 18.22, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 12:46:35 | BATON | ws20 | ws23 | ws22 16.71, ws23 9.99 | ws20 -> ws23, at a t1 cadence, capped at ws28 by the jump bound 8 |
| 2026-08-14 12:48:30 | CADENCE | ws23 | - | ws24 15.90, ws30 14.70 | t1 gcws30b oob 12:46:45..12:48:00, ws1r reversed 12:47:55 during, r 31.66 past the 44.0 fence, stamp 12:47:55, cross 12:48:05 hold 6 bars \| rider ws23 9.99, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 12:48:30 | BATON | ws23 | ws30 | ws24 15.90, ws30 14.70 | ws23 -> ws30, at a t1 cadence, capped at ws31 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 12:50:50 | NO PASS | ws30 | - | none offered | ws30 16.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 13:03:10 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 13:02:30, ws1r reversed 13:03:10 inside the 120s grace from the cross bar 13:02:30, r 22.36 past the 44.0 fence, stamp 13:03:10, hold 6 bars \| rider ws30 15.38, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 13:03:10 | TOP RESET | ws30 | ws2 | ws1 22.36, ws2 55.03 | ws30 15.38 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-08-14 13:12:25 | NO PASS | ws2 | - | none offered | ws2 27.80 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:07:20 | CADENCE | ws2 | - | none offered | t1 gcws30b oob 14:04:20..14:06:50, ws1r reversed 14:06:45 during, r 17.33 past the 44.0 fence, stamp 14:06:45, cross 14:06:55 hold 6 bars \| rider ws2 19.06, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 14:07:20 | EXHAUST | ws2 | - | - | t4 at a t1 cadence - rider ws2 19.06, no candidate at or below ws10 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-14 14:07:20 |
| baton passes made | 13 |
| minutes from the arm to the verdict | 428.3 |
| the rider chain | ws8 > ws16 > ws18 > ws22 > ws24 > ws30 > ws2 > ws3 > ws7 > ws9 > ws17 > ws18 > ws20 > ws23 > ws30 > ws2 |

## MODE 'reversal' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | - | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 07:03:05 | RIDER | ws8 | - | - | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:13:05 | CADENCE | ws8 | - | ws10 0.40, ws11 9.12, ws12 14.92, ws13 20.95, ws16 23.48 | t1 gcws30b ib 07:12:40, ws1r reversed 07:13:00 inside the 120s grace from the cross bar 07:12:40, r 36.68 past the 44.0 fence, stamp 07:13:00, hold 6 bars \| rider ws8 10.75, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 07:13:05 | BATON | ws8 | ws16 | ws10 0.40, ws11 9.12, ws12 14.92, ws13 20.95, ws16 23.48 | ws8 -> ws16, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:35:00 | CADENCE | ws16 | - | ws17 16.07, ws18 18.32 | t1 gcws30b oob 07:32:10..07:34:30, ws1r reversed 07:34:30 during, r 17.51 past the 44.0 fence, stamp 07:34:30, cross 07:34:35 hold 6 bars \| rider ws16 9.72, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 07:35:00 | BATON | ws16 | ws18 | ws17 16.07, ws18 18.32 | ws16 -> ws18, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:45:05 | CADENCE | ws18 | - | ws19 15.43, ws20 22.92, ws21 15.06, ws22 16.37 | t1 gcws30b ib 07:43:30, ws1r reversed 07:45:05 inside the 120s grace from the cross bar 07:43:30, r 28.99 past the 44.0 fence, stamp 07:45:05, hold 6 bars \| rider ws18 17.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:45:05 | BATON | ws18 | ws22 | ws19 15.43, ws20 22.92, ws21 15.06, ws22 16.37 | ws18 -> ws22, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 07:50:10 | NO PASS | ws22 | - | none offered | ws22 19.89 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 08:25:20 | CADENCE | ws22 | - | ws23 16.53, ws24 4.57, ws25 10.94, ws30 23.37 | t1 gcws30b ib 08:24:55, ws1r reversed 08:25:05 inside the 120s grace from the cross bar 08:24:55, r 36.16 past the 44.0 fence, stamp 08:25:05, hold 6 bars \| rider ws22 9.02, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 08:25:20 | BATON | ws22 | ws30 | ws23 16.53, ws24 4.57, ws25 10.94, ws30 23.37 | ws22 -> ws30, at a t1 cadence, capped at ws30 by the jump bound 8 |
| 2026-08-14 08:37:30 | NO PASS | ws30 | - | none offered | ws30 25.54 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:36:20 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 09:35:00, ws1r reversed 09:36:20 inside the 120s grace from the cross bar 09:35:00, r 16.75 past the 44.0 fence, stamp 09:36:20, hold 6 bars \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-14 09:36:20 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 09:39:30 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 09:37:40, ws1r reversed 09:39:30 inside the 120s grace from the cross bar 09:37:40, r 43.97 past the 44.0 fence, stamp 09:39:30, hold 6 bars \| rider ws30 4.18, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-14 09:39:30 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 09:41:20 | CADENCE | ws30 | - | none offered | t1 gcws30b oob 09:38:15..09:40:50, ws1r reversed 09:39:30 during, r 43.97 past the 44.0 fence, stamp 09:39:30, cross 09:40:55 hold 6 bars \| rider ws30 4.18, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-14 09:41:20 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:10 | NO PASS | ws30 | - | none offered | ws30 16.80 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:28:20 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 10:27:55, ws1r reversed 10:28:00 inside the 120s grace from the cross bar 10:27:55, r 4.45 past the 44.0 fence, stamp 10:28:00, hold 6 bars \| rider ws30 17.09, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:28:20 | TOP RESET | ws30 | ws2 | ws1 6.37, ws2 22.67 | ws30 17.09 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-08-14 10:36:55 | BATON | ws2 | ws3 | ws3 18.29 | ws2 -> ws3, between cadences, lin_hop 2 |
| 2026-08-14 10:51:35 | CADENCE | ws3 | - | ws4 6.62, ws5 16.16, ws7 42.95 | t1 gcws30b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, r 35.89 past the 44.0 fence, stamp 10:48:55, cross 10:51:10 hold 6 bars \| rider ws3 9.27, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 10:51:35 | BATON | ws3 | ws7 | ws4 6.62, ws5 16.16, ws7 42.95 | ws3 -> ws7, at a t1 cadence, capped at ws11 by the jump bound 8 |
| 2026-08-14 11:16:00 | CADENCE | ws7 | - | ws8 11.35, ws9 12.32 | t1 gcws30b oob 11:11:30..11:15:30, ws1r reversed 11:15:20 during, r 8.28 past the 44.0 fence, stamp 11:15:20, cross 11:15:35 hold 6 bars \| rider ws7 2.07, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 11:16:00 | BATON | ws7 | ws9 | ws8 11.35, ws9 12.32 | ws7 -> ws9, at a t1 cadence, capped at ws15 by the jump bound 8 |
| 2026-08-14 11:20:00 | NO PASS | ws9 | - | none offered | ws9 18.99 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:02:25 | CADENCE | ws9 | - | ws14 25.30, ws17 23.23 | t1 gcws30b ib 12:02:00, ws1r reversed 12:02:25 inside the 120s grace from the cross bar 12:02:00, r 27.60 past the 44.0 fence, stamp 12:02:25, hold 6 bars \| rider ws9 67.46, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:02:25 | BATON | ws9 | ws17 | ws14 25.30, ws17 23.23 | ws9 -> ws17, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-08-14 12:16:00 | CADENCE | ws17 | - | ws18 25.32 | t1 gcws30b oob 12:14:20..12:15:30, ws1r reversed 12:14:45 during, r 19.40 past the 44.0 fence, stamp 12:14:45, cross 12:15:35 hold 6 bars \| rider ws17 14.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 12:16:00 | BATON | ws17 | ws18 | ws18 25.32 | ws17 -> ws18, at a t1 cadence, capped at ws25 by the jump bound 8 |
| 2026-08-14 12:25:05 | BATON | ws18 | ws20 | ws19 27.83, ws20 24.52 | ws18 -> ws20, between cadences, lin_hop 2 |
| 2026-08-14 12:25:35 | NO PASS | ws20 | - | none offered | ws20 23.87 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:46:35 | CADENCE | ws20 | - | ws22 16.71, ws23 9.99 | t1 gcws30b ib 12:46:10, ws1r reversed 12:46:15 inside the 120s grace from the cross bar 12:46:10, r 37.62 past the 44.0 fence, stamp 12:46:15, hold 6 bars \| rider ws20 18.22, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 12:46:35 | BATON | ws20 | ws23 | ws22 16.71, ws23 9.99 | ws20 -> ws23, at a t1 cadence, capped at ws28 by the jump bound 8 |
| 2026-08-14 12:48:30 | CADENCE | ws23 | - | ws24 15.90, ws30 14.70 | t1 gcws30b oob 12:46:45..12:48:00, ws1r reversed 12:47:55 during, r 31.66 past the 44.0 fence, stamp 12:47:55, cross 12:48:05 hold 6 bars \| rider ws23 9.99, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 12:48:30 | BATON | ws23 | ws30 | ws24 15.90, ws30 14.70 | ws23 -> ws30, at a t1 cadence, capped at ws31 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 13:03:10 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 13:02:30, ws1r reversed 13:03:10 inside the 120s grace from the cross bar 13:02:30, r 22.36 past the 44.0 fence, stamp 13:03:10, hold 6 bars \| rider ws30 15.38, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 13:03:10 | TOP RESET | ws30 | ws2 | ws1 22.36, ws2 55.03 | ws30 15.38 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-08-14 13:12:45 | NO PASS | ws2 | - | none offered | ws2 27.80 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:07:20 | CADENCE | ws2 | - | none offered | t1 gcws30b oob 14:04:20..14:06:50, ws1r reversed 14:06:45 during, r 17.33 past the 44.0 fence, stamp 14:06:45, cross 14:06:55 hold 6 bars \| rider ws2 19.06, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 14:07:20 | EXHAUST | ws2 | - | - | t4 at a t1 cadence - rider ws2 19.06, no candidate at or below ws10 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-14 14:07:20 |
| baton passes made | 12 |
| minutes from the arm to the verdict | 428.3 |
| the rider chain | ws8 > ws16 > ws18 > ws22 > ws30 > ws2 > ws3 > ws7 > ws9 > ws17 > ws18 > ws20 > ws23 > ws30 > ws2 |

## MODE 'reversal+quarter' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | - | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 07:03:05 | RIDER | ws8 | - | - | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:13:05 | CADENCE | ws8 | - | ws10 0.40, ws11 9.12, ws12 14.92, ws13 20.95, ws16 23.48 | t1 gcws30b ib 07:12:40, ws1r reversed 07:13:00 inside the 120s grace from the cross bar 07:12:40, r 36.68 past the 44.0 fence, stamp 07:13:00, hold 6 bars \| rider ws8 10.75, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 07:13:05 | BATON | ws8 | ws16 | ws10 0.40, ws11 9.12, ws12 14.92, ws13 20.95, ws16 23.48 | ws8 -> ws16, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:35:00 | CADENCE | ws16 | - | ws17 16.07, ws18 18.32 | t1 gcws30b oob 07:32:10..07:34:30, ws1r reversed 07:34:30 during, r 17.51 past the 44.0 fence, stamp 07:34:30, cross 07:34:35 hold 6 bars \| rider ws16 9.72, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 07:35:00 | BATON | ws16 | ws18 | ws17 16.07, ws18 18.32 | ws16 -> ws18, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:45:05 | CADENCE | ws18 | - | ws19 15.43, ws20 22.92, ws21 15.06, ws22 16.37 | t1 gcws30b ib 07:43:30, ws1r reversed 07:45:05 inside the 120s grace from the cross bar 07:43:30, r 28.99 past the 44.0 fence, stamp 07:45:05, hold 6 bars \| rider ws18 17.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:45:05 | BATON | ws18 | ws22 | ws19 15.43, ws20 22.92, ws21 15.06, ws22 16.37 | ws18 -> ws22, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 07:54:45 | NO PASS | ws22 | - | none offered | ws22 19.97 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 08:25:20 | CADENCE | ws22 | - | ws23 16.53, ws24 4.57, ws25 10.94, ws30 23.37 | t1 gcws30b ib 08:24:55, ws1r reversed 08:25:05 inside the 120s grace from the cross bar 08:24:55, r 36.16 past the 44.0 fence, stamp 08:25:05, hold 6 bars \| rider ws22 9.02, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 08:25:20 | BATON | ws22 | ws30 | ws23 16.53, ws24 4.57, ws25 10.94, ws30 23.37 | ws22 -> ws30, at a t1 cadence, capped at ws30 by the jump bound 8 |
| 2026-08-14 08:44:05 | NO PASS | ws30 | - | none offered | ws30 21.05 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:36:20 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 09:35:00, ws1r reversed 09:36:20 inside the 120s grace from the cross bar 09:35:00, r 16.75 past the 44.0 fence, stamp 09:36:20, hold 6 bars \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-14 09:36:20 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 09:39:30 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 09:37:40, ws1r reversed 09:39:30 inside the 120s grace from the cross bar 09:37:40, r 43.97 past the 44.0 fence, stamp 09:39:30, hold 6 bars \| rider ws30 4.18, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-14 09:39:30 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 09:41:20 | CADENCE | ws30 | - | none offered | t1 gcws30b oob 09:38:15..09:40:50, ws1r reversed 09:39:30 during, r 43.97 past the 44.0 fence, stamp 09:39:30, cross 09:40:55 hold 6 bars \| rider ws30 4.18, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-14 09:41:20 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 10:07:45 | NO PASS | ws30 | - | none offered | ws30 18.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:28:20 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 10:27:55, ws1r reversed 10:28:00 inside the 120s grace from the cross bar 10:27:55, r 4.45 past the 44.0 fence, stamp 10:28:00, hold 6 bars \| rider ws30 17.09, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:28:20 | TOP RESET | ws30 | ws2 | ws1 6.37, ws2 22.67 | ws30 17.09 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-08-14 10:36:55 | BATON | ws2 | ws3 | ws3 18.29 | ws2 -> ws3, between cadences, lin_hop 2 |
| 2026-08-14 10:51:35 | CADENCE | ws3 | - | ws4 6.62, ws5 16.16, ws7 42.95 | t1 gcws30b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, r 35.89 past the 44.0 fence, stamp 10:48:55, cross 10:51:10 hold 6 bars \| rider ws3 9.27, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 10:51:35 | BATON | ws3 | ws7 | ws4 6.62, ws5 16.16, ws7 42.95 | ws3 -> ws7, at a t1 cadence, capped at ws11 by the jump bound 8 |
| 2026-08-14 11:16:00 | CADENCE | ws7 | - | ws8 11.35, ws9 12.32 | t1 gcws30b oob 11:11:30..11:15:30, ws1r reversed 11:15:20 during, r 8.28 past the 44.0 fence, stamp 11:15:20, cross 11:15:35 hold 6 bars \| rider ws7 2.07, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 11:16:00 | BATON | ws7 | ws9 | ws8 11.35, ws9 12.32 | ws7 -> ws9, at a t1 cadence, capped at ws15 by the jump bound 8 |
| 2026-08-14 11:21:20 | NO PASS | ws9 | - | none offered | ws9 17.24 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:02:25 | CADENCE | ws9 | - | ws14 25.30, ws17 23.23 | t1 gcws30b ib 12:02:00, ws1r reversed 12:02:25 inside the 120s grace from the cross bar 12:02:00, r 27.60 past the 44.0 fence, stamp 12:02:25, hold 6 bars \| rider ws9 67.46, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:02:25 | BATON | ws9 | ws17 | ws14 25.30, ws17 23.23 | ws9 -> ws17, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-08-14 12:16:00 | CADENCE | ws17 | - | ws18 25.32 | t1 gcws30b oob 12:14:20..12:15:30, ws1r reversed 12:14:45 during, r 19.40 past the 44.0 fence, stamp 12:14:45, cross 12:15:35 hold 6 bars \| rider ws17 14.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 12:16:00 | BATON | ws17 | ws18 | ws18 25.32 | ws17 -> ws18, at a t1 cadence, capped at ws25 by the jump bound 8 |
| 2026-08-14 12:28:40 | BATON | ws18 | ws20 | ws19 17.57, ws20 19.98 | ws18 -> ws20, between cadences, lin_hop 2 |
| 2026-08-14 12:29:40 | BATON | ws20 | ws22 | ws22 19.25 | ws20 -> ws22, between cadences, lin_hop 2 |
| 2026-08-14 12:46:35 | CADENCE | ws22 | - | ws23 9.99, ws30 14.70 | t1 gcws30b ib 12:46:10, ws1r reversed 12:46:15 inside the 120s grace from the cross bar 12:46:10, r 37.62 past the 44.0 fence, stamp 12:46:15, hold 6 bars \| rider ws22 16.71, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 12:46:35 | BATON | ws22 | ws30 | ws23 9.99, ws30 14.70 | ws22 -> ws30, at a t1 cadence, capped at ws30 by the jump bound 8 |
| 2026-08-14 12:48:30 | CADENCE | ws30 | - | none offered | t1 gcws30b oob 12:46:45..12:48:00, ws1r reversed 12:47:55 during, r 31.66 past the 44.0 fence, stamp 12:47:55, cross 12:48:05 hold 6 bars \| rider ws30 14.70, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 12:48:30 | HOLD | ws30 | - | - | rider ws30 14.70 oob - no action |
| 2026-08-14 13:03:10 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 13:02:30, ws1r reversed 13:03:10 inside the 120s grace from the cross bar 13:02:30, r 22.36 past the 44.0 fence, stamp 13:03:10, hold 6 bars \| rider ws30 15.38, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 13:03:10 | TOP RESET | ws30 | ws2 | ws1 22.36, ws2 55.03 | ws30 15.38 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-08-14 13:12:45 | NO PASS | ws2 | - | none offered | ws2 27.80 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:07:20 | CADENCE | ws2 | - | none offered | t1 gcws30b oob 14:04:20..14:06:50, ws1r reversed 14:06:45 during, r 17.33 past the 44.0 fence, stamp 14:06:45, cross 14:06:55 hold 6 bars \| rider ws2 19.06, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 14:07:20 | EXHAUST | ws2 | - | - | t4 at a t1 cadence - rider ws2 19.06, no candidate at or below ws10 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-14 14:07:20 |
| baton passes made | 12 |
| minutes from the arm to the verdict | 428.3 |
| the rider chain | ws8 > ws16 > ws18 > ws22 > ws30 > ws2 > ws3 > ws7 > ws9 > ws17 > ws18 > ws20 > ws22 > ws30 > ws2 |

## MODE 'ib' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 06:59:00 | RETEST | - | ws1r 12.95 oob + ws2r 52.91 / ws3r 70.72 in - the gate opens; ws1r oob->ib cross 2026-08-14 07:02:10, wob 12, cadence at 2026-08-14 07:03:05 |
| 2026-08-14 07:03:05 | RIDER | ws8 | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:13:05 | LATCH1 | ws8 | latch 1 at the t1 cadence 2026-08-14 07:13:05, divergence state -1 |
| 2026-08-14 07:13:05 | CADENCE | ws8 | t1 gcws30b ib 07:12:40, ws1r reversed 07:13:00 inside the 120s grace from the cross bar 07:12:40, r 36.68 past the 44.0 fence, stamp 07:13:00, hold 6 bars \| rider ws8 10.75, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 07:13:05 | BATON | ws8 | ws8 -> ws16, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:35:00 | LATCH1 | ws16 | latch 1 at the t1 cadence 2026-08-14 07:35:00, divergence state -1 |
| 2026-08-14 07:35:00 | CADENCE | ws16 | t1 gcws30b oob 07:32:10..07:34:30, ws1r reversed 07:34:30 during, r 17.51 past the 44.0 fence, stamp 07:34:30, cross 07:34:35 hold 6 bars \| rider ws16 9.72, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 07:35:00 | BATON | ws16 | ws16 -> ws18, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:45:05 | LATCH1 | ws18 | latch 1 at the t1 cadence 2026-08-14 07:45:05, divergence state -1 |
| 2026-08-14 07:45:05 | CADENCE | ws18 | t1 gcws30b ib 07:43:30, ws1r reversed 07:45:05 inside the 120s grace from the cross bar 07:43:30, r 28.99 past the 44.0 fence, stamp 07:45:05, hold 6 bars \| rider ws18 17.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:45:05 | BATON | ws18 | ws18 -> ws22, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 08:10:00 | BATON | ws22 | ws22 -> ws24, between cadences, lin_hop 2 |
| 2026-08-14 08:25:20 | CADENCE | ws24 | t1 gcws30b ib 08:24:55, ws1r reversed 08:25:05 inside the 120s grace from the cross bar 08:24:55, r 36.16 past the 44.0 fence, stamp 08:25:05, hold 6 bars \| rider ws24 4.57, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 08:25:20 | BATON | ws24 | ws24 -> ws30, at a t1 cadence, capped at ws32 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 09:14:10 | NO PASS | ws30 | ws30 9.90 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:36:20 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:36:20, divergence state -1 |
| 2026-08-14 09:36:20 | CADENCE | ws30 | t1 gcws30b ib 09:35:00, ws1r reversed 09:36:20 inside the 120s grace from the cross bar 09:35:00, r 16.75 past the 44.0 fence, stamp 09:36:20, hold 6 bars \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-14 09:36:20 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 09:39:30 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:39:30, divergence state -1 |
| 2026-08-14 09:39:30 | CADENCE | ws30 | t1 gcws30b ib 09:37:40, ws1r reversed 09:39:30 inside the 120s grace from the cross bar 09:37:40, r 43.97 past the 44.0 fence, stamp 09:39:30, hold 6 bars \| rider ws30 4.18, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-14 09:39:30 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 09:41:20 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:41:20, divergence state -1 |
| 2026-08-14 09:41:20 | CADENCE | ws30 | t1 gcws30b oob 09:38:15..09:40:50, ws1r reversed 09:39:30 during, r 43.97 past the 44.0 fence, stamp 09:39:30, cross 09:40:55 hold 6 bars \| rider ws30 4.18, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-14 09:41:20 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:40 | NO PASS | ws30 | ws30 18.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:28:20 | CADENCE | ws30 | t1 gcws30b ib 10:27:55, ws1r reversed 10:28:00 inside the 120s grace from the cross bar 10:27:55, r 4.45 past the 44.0 fence, stamp 10:28:00, hold 6 bars \| rider ws30 17.09, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:28:20 | TOP RESET | ws30 | ws30 17.09 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-08-14 10:36:35 | BATON | ws2 | ws2 -> ws3, between cadences, lin_hop 2 |
| 2026-08-14 10:51:35 | LATCH1 | ws3 | latch 1 at the t1 cadence 2026-08-14 10:51:35, divergence state -1 |
| 2026-08-14 10:51:35 | CADENCE | ws3 | t1 gcws30b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, r 35.89 past the 44.0 fence, stamp 10:48:55, cross 10:51:10 hold 6 bars \| rider ws3 9.27, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 10:51:35 | BATON | ws3 | ws3 -> ws7, at a t1 cadence, capped at ws11 by the jump bound 8 |
| 2026-08-14 11:16:00 | LATCH1 | ws7 | latch 1 at the t1 cadence 2026-08-14 11:16:00, divergence state -1 |
| 2026-08-14 11:16:00 | CADENCE | ws7 | t1 gcws30b oob 11:11:30..11:15:30, ws1r reversed 11:15:20 during, r 8.28 past the 44.0 fence, stamp 11:15:20, cross 11:15:35 hold 6 bars \| rider ws7 2.07, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 11:16:00 | BATON | ws7 | ws7 -> ws9, at a t1 cadence, capped at ws15 by the jump bound 8 |
| 2026-08-14 11:19:20 | NO PASS | ws9 | ws9 18.29 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:02:25 | CADENCE | ws9 | t1 gcws30b ib 12:02:00, ws1r reversed 12:02:25 inside the 120s grace from the cross bar 12:02:00, r 27.60 past the 44.0 fence, stamp 12:02:25, hold 6 bars \| rider ws9 67.46, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:02:25 | BATON | ws9 | ws9 -> ws17, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-08-14 12:16:00 | LATCH1 | ws17 | latch 1 at the t1 cadence 2026-08-14 12:16:00, divergence state -1 |
| 2026-08-14 12:16:00 | CADENCE | ws17 | t1 gcws30b oob 12:14:20..12:15:30, ws1r reversed 12:14:45 during, r 19.40 past the 44.0 fence, stamp 12:14:45, cross 12:15:35 hold 6 bars \| rider ws17 14.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 12:16:00 | BATON | ws17 | ws17 -> ws18, at a t1 cadence, capped at ws25 by the jump bound 8 |
| 2026-08-14 12:25:15 | BATON | ws18 | ws18 -> ws20, between cadences, lin_hop 2 |
| 2026-08-14 12:46:35 | LATCH1 | ws20 | latch 1 at the t1 cadence 2026-08-14 12:46:35, divergence state -1 |
| 2026-08-14 12:46:35 | CADENCE | ws20 | t1 gcws30b ib 12:46:10, ws1r reversed 12:46:15 inside the 120s grace from the cross bar 12:46:10, r 37.62 past the 44.0 fence, stamp 12:46:15, hold 6 bars \| rider ws20 18.22, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 12:46:35 | BATON | ws20 | ws20 -> ws23, at a t1 cadence, capped at ws28 by the jump bound 8 |
| 2026-08-14 12:48:30 | LATCH1 | ws23 | latch 1 at the t1 cadence 2026-08-14 12:48:30, divergence state -1 |
| 2026-08-14 12:48:30 | CADENCE | ws23 | t1 gcws30b oob 12:46:45..12:48:00, ws1r reversed 12:47:55 during, r 31.66 past the 44.0 fence, stamp 12:47:55, cross 12:48:05 hold 6 bars \| rider ws23 9.99, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 12:48:30 | BATON | ws23 | ws23 -> ws30, at a t1 cadence, capped at ws31 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 12:50:50 | NO PASS | ws30 | ws30 16.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 13:03:10 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 13:03:10, divergence state -1 |
| 2026-08-14 13:03:10 | CADENCE | ws30 | t1 gcws30b ib 13:02:30, ws1r reversed 13:03:10 inside the 120s grace from the cross bar 13:02:30, r 22.36 past the 44.0 fence, stamp 13:03:10, hold 6 bars \| rider ws30 15.38, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 13:03:10 | TOP RESET | ws30 | ws30 15.38 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-08-14 13:12:25 | NO PASS | ws2 | ws2 27.80 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:07:20 | CADENCE | ws2 | t1 gcws30b oob 14:04:20..14:06:50, ws1r reversed 14:06:45 during, r 17.33 past the 44.0 fence, stamp 14:06:45, cross 14:06:55 hold 6 bars \| rider ws2 19.06, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 14:07:20 | EXHAUST | ws2 | t4 at a t1 cadence - rider ws2 19.06, no candidate at or below ws10 (the jump bound 8) |

## MODE 'reversal' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 06:59:00 | RETEST | - | ws1r 12.95 oob + ws2r 52.91 / ws3r 70.72 in - the gate opens; ws1r oob->ib cross 2026-08-14 07:02:10, wob 12, cadence at 2026-08-14 07:03:05 |
| 2026-08-14 07:03:05 | RIDER | ws8 | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:13:05 | LATCH1 | ws8 | latch 1 at the t1 cadence 2026-08-14 07:13:05, divergence state -1 |
| 2026-08-14 07:13:05 | CADENCE | ws8 | t1 gcws30b ib 07:12:40, ws1r reversed 07:13:00 inside the 120s grace from the cross bar 07:12:40, r 36.68 past the 44.0 fence, stamp 07:13:00, hold 6 bars \| rider ws8 10.75, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 07:13:05 | BATON | ws8 | ws8 -> ws16, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:35:00 | LATCH1 | ws16 | latch 1 at the t1 cadence 2026-08-14 07:35:00, divergence state -1 |
| 2026-08-14 07:35:00 | CADENCE | ws16 | t1 gcws30b oob 07:32:10..07:34:30, ws1r reversed 07:34:30 during, r 17.51 past the 44.0 fence, stamp 07:34:30, cross 07:34:35 hold 6 bars \| rider ws16 9.72, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 07:35:00 | BATON | ws16 | ws16 -> ws18, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:45:05 | LATCH1 | ws18 | latch 1 at the t1 cadence 2026-08-14 07:45:05, divergence state -1 |
| 2026-08-14 07:45:05 | CADENCE | ws18 | t1 gcws30b ib 07:43:30, ws1r reversed 07:45:05 inside the 120s grace from the cross bar 07:43:30, r 28.99 past the 44.0 fence, stamp 07:45:05, hold 6 bars \| rider ws18 17.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:45:05 | BATON | ws18 | ws18 -> ws22, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 07:50:10 | NO PASS | ws22 | ws22 19.89 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 08:25:20 | CADENCE | ws22 | t1 gcws30b ib 08:24:55, ws1r reversed 08:25:05 inside the 120s grace from the cross bar 08:24:55, r 36.16 past the 44.0 fence, stamp 08:25:05, hold 6 bars \| rider ws22 9.02, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 08:25:20 | BATON | ws22 | ws22 -> ws30, at a t1 cadence, capped at ws30 by the jump bound 8 |
| 2026-08-14 08:37:30 | NO PASS | ws30 | ws30 25.54 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:36:20 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:36:20, divergence state -1 |
| 2026-08-14 09:36:20 | CADENCE | ws30 | t1 gcws30b ib 09:35:00, ws1r reversed 09:36:20 inside the 120s grace from the cross bar 09:35:00, r 16.75 past the 44.0 fence, stamp 09:36:20, hold 6 bars \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-14 09:36:20 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 09:39:30 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:39:30, divergence state -1 |
| 2026-08-14 09:39:30 | CADENCE | ws30 | t1 gcws30b ib 09:37:40, ws1r reversed 09:39:30 inside the 120s grace from the cross bar 09:37:40, r 43.97 past the 44.0 fence, stamp 09:39:30, hold 6 bars \| rider ws30 4.18, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-14 09:39:30 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 09:41:20 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:41:20, divergence state -1 |
| 2026-08-14 09:41:20 | CADENCE | ws30 | t1 gcws30b oob 09:38:15..09:40:50, ws1r reversed 09:39:30 during, r 43.97 past the 44.0 fence, stamp 09:39:30, cross 09:40:55 hold 6 bars \| rider ws30 4.18, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-14 09:41:20 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:10 | NO PASS | ws30 | ws30 16.80 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:28:20 | CADENCE | ws30 | t1 gcws30b ib 10:27:55, ws1r reversed 10:28:00 inside the 120s grace from the cross bar 10:27:55, r 4.45 past the 44.0 fence, stamp 10:28:00, hold 6 bars \| rider ws30 17.09, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:28:20 | TOP RESET | ws30 | ws30 17.09 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-08-14 10:36:55 | BATON | ws2 | ws2 -> ws3, between cadences, lin_hop 2 |
| 2026-08-14 10:51:35 | LATCH1 | ws3 | latch 1 at the t1 cadence 2026-08-14 10:51:35, divergence state -1 |
| 2026-08-14 10:51:35 | CADENCE | ws3 | t1 gcws30b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, r 35.89 past the 44.0 fence, stamp 10:48:55, cross 10:51:10 hold 6 bars \| rider ws3 9.27, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 10:51:35 | BATON | ws3 | ws3 -> ws7, at a t1 cadence, capped at ws11 by the jump bound 8 |
| 2026-08-14 11:16:00 | LATCH1 | ws7 | latch 1 at the t1 cadence 2026-08-14 11:16:00, divergence state -1 |
| 2026-08-14 11:16:00 | CADENCE | ws7 | t1 gcws30b oob 11:11:30..11:15:30, ws1r reversed 11:15:20 during, r 8.28 past the 44.0 fence, stamp 11:15:20, cross 11:15:35 hold 6 bars \| rider ws7 2.07, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 11:16:00 | BATON | ws7 | ws7 -> ws9, at a t1 cadence, capped at ws15 by the jump bound 8 |
| 2026-08-14 11:20:00 | NO PASS | ws9 | ws9 18.99 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:02:25 | CADENCE | ws9 | t1 gcws30b ib 12:02:00, ws1r reversed 12:02:25 inside the 120s grace from the cross bar 12:02:00, r 27.60 past the 44.0 fence, stamp 12:02:25, hold 6 bars \| rider ws9 67.46, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:02:25 | BATON | ws9 | ws9 -> ws17, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-08-14 12:16:00 | LATCH1 | ws17 | latch 1 at the t1 cadence 2026-08-14 12:16:00, divergence state -1 |
| 2026-08-14 12:16:00 | CADENCE | ws17 | t1 gcws30b oob 12:14:20..12:15:30, ws1r reversed 12:14:45 during, r 19.40 past the 44.0 fence, stamp 12:14:45, cross 12:15:35 hold 6 bars \| rider ws17 14.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 12:16:00 | BATON | ws17 | ws17 -> ws18, at a t1 cadence, capped at ws25 by the jump bound 8 |
| 2026-08-14 12:25:05 | BATON | ws18 | ws18 -> ws20, between cadences, lin_hop 2 |
| 2026-08-14 12:25:35 | NO PASS | ws20 | ws20 23.87 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:46:35 | LATCH1 | ws20 | latch 1 at the t1 cadence 2026-08-14 12:46:35, divergence state -1 |
| 2026-08-14 12:46:35 | CADENCE | ws20 | t1 gcws30b ib 12:46:10, ws1r reversed 12:46:15 inside the 120s grace from the cross bar 12:46:10, r 37.62 past the 44.0 fence, stamp 12:46:15, hold 6 bars \| rider ws20 18.22, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 12:46:35 | BATON | ws20 | ws20 -> ws23, at a t1 cadence, capped at ws28 by the jump bound 8 |
| 2026-08-14 12:48:30 | LATCH1 | ws23 | latch 1 at the t1 cadence 2026-08-14 12:48:30, divergence state -1 |
| 2026-08-14 12:48:30 | CADENCE | ws23 | t1 gcws30b oob 12:46:45..12:48:00, ws1r reversed 12:47:55 during, r 31.66 past the 44.0 fence, stamp 12:47:55, cross 12:48:05 hold 6 bars \| rider ws23 9.99, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 12:48:30 | BATON | ws23 | ws23 -> ws30, at a t1 cadence, capped at ws31 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 13:03:10 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 13:03:10, divergence state -1 |
| 2026-08-14 13:03:10 | CADENCE | ws30 | t1 gcws30b ib 13:02:30, ws1r reversed 13:03:10 inside the 120s grace from the cross bar 13:02:30, r 22.36 past the 44.0 fence, stamp 13:03:10, hold 6 bars \| rider ws30 15.38, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 13:03:10 | TOP RESET | ws30 | ws30 15.38 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-08-14 13:12:45 | NO PASS | ws2 | ws2 27.80 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:07:20 | CADENCE | ws2 | t1 gcws30b oob 14:04:20..14:06:50, ws1r reversed 14:06:45 during, r 17.33 past the 44.0 fence, stamp 14:06:45, cross 14:06:55 hold 6 bars \| rider ws2 19.06, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 14:07:20 | EXHAUST | ws2 | t4 at a t1 cadence - rider ws2 19.06, no candidate at or below ws10 (the jump bound 8) |

## MODE 'reversal+quarter' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 06:59:00 | RETEST | - | ws1r 12.95 oob + ws2r 52.91 / ws3r 70.72 in - the gate opens; ws1r oob->ib cross 2026-08-14 07:02:10, wob 12, cadence at 2026-08-14 07:03:05 |
| 2026-08-14 07:03:05 | RIDER | ws8 | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:13:05 | LATCH1 | ws8 | latch 1 at the t1 cadence 2026-08-14 07:13:05, divergence state -1 |
| 2026-08-14 07:13:05 | CADENCE | ws8 | t1 gcws30b ib 07:12:40, ws1r reversed 07:13:00 inside the 120s grace from the cross bar 07:12:40, r 36.68 past the 44.0 fence, stamp 07:13:00, hold 6 bars \| rider ws8 10.75, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 07:13:05 | BATON | ws8 | ws8 -> ws16, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:35:00 | LATCH1 | ws16 | latch 1 at the t1 cadence 2026-08-14 07:35:00, divergence state -1 |
| 2026-08-14 07:35:00 | CADENCE | ws16 | t1 gcws30b oob 07:32:10..07:34:30, ws1r reversed 07:34:30 during, r 17.51 past the 44.0 fence, stamp 07:34:30, cross 07:34:35 hold 6 bars \| rider ws16 9.72, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 07:35:00 | BATON | ws16 | ws16 -> ws18, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:45:05 | LATCH1 | ws18 | latch 1 at the t1 cadence 2026-08-14 07:45:05, divergence state -1 |
| 2026-08-14 07:45:05 | CADENCE | ws18 | t1 gcws30b ib 07:43:30, ws1r reversed 07:45:05 inside the 120s grace from the cross bar 07:43:30, r 28.99 past the 44.0 fence, stamp 07:45:05, hold 6 bars \| rider ws18 17.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:45:05 | BATON | ws18 | ws18 -> ws22, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 07:54:45 | NO PASS | ws22 | ws22 19.97 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 08:25:20 | CADENCE | ws22 | t1 gcws30b ib 08:24:55, ws1r reversed 08:25:05 inside the 120s grace from the cross bar 08:24:55, r 36.16 past the 44.0 fence, stamp 08:25:05, hold 6 bars \| rider ws22 9.02, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 08:25:20 | BATON | ws22 | ws22 -> ws30, at a t1 cadence, capped at ws30 by the jump bound 8 |
| 2026-08-14 08:44:05 | NO PASS | ws30 | ws30 21.05 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:36:20 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:36:20, divergence state -1 |
| 2026-08-14 09:36:20 | CADENCE | ws30 | t1 gcws30b ib 09:35:00, ws1r reversed 09:36:20 inside the 120s grace from the cross bar 09:35:00, r 16.75 past the 44.0 fence, stamp 09:36:20, hold 6 bars \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-14 09:36:20 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 09:39:30 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:39:30, divergence state -1 |
| 2026-08-14 09:39:30 | CADENCE | ws30 | t1 gcws30b ib 09:37:40, ws1r reversed 09:39:30 inside the 120s grace from the cross bar 09:37:40, r 43.97 past the 44.0 fence, stamp 09:39:30, hold 6 bars \| rider ws30 4.18, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-14 09:39:30 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 09:41:20 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:41:20, divergence state -1 |
| 2026-08-14 09:41:20 | CADENCE | ws30 | t1 gcws30b oob 09:38:15..09:40:50, ws1r reversed 09:39:30 during, r 43.97 past the 44.0 fence, stamp 09:39:30, cross 09:40:55 hold 6 bars \| rider ws30 4.18, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-14 09:41:20 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 10:07:45 | NO PASS | ws30 | ws30 18.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:28:20 | CADENCE | ws30 | t1 gcws30b ib 10:27:55, ws1r reversed 10:28:00 inside the 120s grace from the cross bar 10:27:55, r 4.45 past the 44.0 fence, stamp 10:28:00, hold 6 bars \| rider ws30 17.09, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:28:20 | TOP RESET | ws30 | ws30 17.09 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-08-14 10:36:55 | BATON | ws2 | ws2 -> ws3, between cadences, lin_hop 2 |
| 2026-08-14 10:51:35 | LATCH1 | ws3 | latch 1 at the t1 cadence 2026-08-14 10:51:35, divergence state -1 |
| 2026-08-14 10:51:35 | CADENCE | ws3 | t1 gcws30b oob 10:48:35..10:51:05, ws1r reversed 10:48:55 during, r 35.89 past the 44.0 fence, stamp 10:48:55, cross 10:51:10 hold 6 bars \| rider ws3 9.27, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 10:51:35 | BATON | ws3 | ws3 -> ws7, at a t1 cadence, capped at ws11 by the jump bound 8 |
| 2026-08-14 11:16:00 | LATCH1 | ws7 | latch 1 at the t1 cadence 2026-08-14 11:16:00, divergence state -1 |
| 2026-08-14 11:16:00 | CADENCE | ws7 | t1 gcws30b oob 11:11:30..11:15:30, ws1r reversed 11:15:20 during, r 8.28 past the 44.0 fence, stamp 11:15:20, cross 11:15:35 hold 6 bars \| rider ws7 2.07, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 11:16:00 | BATON | ws7 | ws7 -> ws9, at a t1 cadence, capped at ws15 by the jump bound 8 |
| 2026-08-14 11:21:20 | NO PASS | ws9 | ws9 17.24 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:02:25 | CADENCE | ws9 | t1 gcws30b ib 12:02:00, ws1r reversed 12:02:25 inside the 120s grace from the cross bar 12:02:00, r 27.60 past the 44.0 fence, stamp 12:02:25, hold 6 bars \| rider ws9 67.46, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:02:25 | BATON | ws9 | ws9 -> ws17, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-08-14 12:16:00 | LATCH1 | ws17 | latch 1 at the t1 cadence 2026-08-14 12:16:00, divergence state -1 |
| 2026-08-14 12:16:00 | CADENCE | ws17 | t1 gcws30b oob 12:14:20..12:15:30, ws1r reversed 12:14:45 during, r 19.40 past the 44.0 fence, stamp 12:14:45, cross 12:15:35 hold 6 bars \| rider ws17 14.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 12:16:00 | BATON | ws17 | ws17 -> ws18, at a t1 cadence, capped at ws25 by the jump bound 8 |
| 2026-08-14 12:28:40 | BATON | ws18 | ws18 -> ws20, between cadences, lin_hop 2 |
| 2026-08-14 12:29:40 | BATON | ws20 | ws20 -> ws22, between cadences, lin_hop 2 |
| 2026-08-14 12:46:35 | LATCH1 | ws22 | latch 1 at the t1 cadence 2026-08-14 12:46:35, divergence state -1 |
| 2026-08-14 12:46:35 | CADENCE | ws22 | t1 gcws30b ib 12:46:10, ws1r reversed 12:46:15 inside the 120s grace from the cross bar 12:46:10, r 37.62 past the 44.0 fence, stamp 12:46:15, hold 6 bars \| rider ws22 16.71, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 12:46:35 | BATON | ws22 | ws22 -> ws30, at a t1 cadence, capped at ws30 by the jump bound 8 |
| 2026-08-14 12:48:30 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 12:48:30, divergence state -1 |
| 2026-08-14 12:48:30 | CADENCE | ws30 | t1 gcws30b oob 12:46:45..12:48:00, ws1r reversed 12:47:55 during, r 31.66 past the 44.0 fence, stamp 12:47:55, cross 12:48:05 hold 6 bars \| rider ws30 14.70, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 12:48:30 | HOLD | ws30 | rider ws30 14.70 oob - no action |
| 2026-08-14 13:03:10 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 13:03:10, divergence state -1 |
| 2026-08-14 13:03:10 | CADENCE | ws30 | t1 gcws30b ib 13:02:30, ws1r reversed 13:03:10 inside the 120s grace from the cross bar 13:02:30, r 22.36 past the 44.0 fence, stamp 13:03:10, hold 6 bars \| rider ws30 15.38, no-longer-exfence yes, reversed no \| mage-cascade up |
| 2026-08-14 13:03:10 | TOP RESET | ws30 | ws30 15.38 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-08-14 13:12:45 | NO PASS | ws2 | ws2 27.80 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:07:20 | CADENCE | ws2 | t1 gcws30b oob 14:04:20..14:06:50, ws1r reversed 14:06:45 during, r 17.33 past the 44.0 fence, stamp 14:06:45, cross 14:06:55 hold 6 bars \| rider ws2 19.06, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 14:07:20 | EXHAUST | ws2 | t4 at a t1 cadence - rider ws2 19.06, no candidate at or below ws10 (the jump bound 8) |
