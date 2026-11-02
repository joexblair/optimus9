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
| 2026-08-14 06:59:00 | ARM | - | - | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 07:03:05 | RIDER | ws8 | - | - | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:03:25 | CADENCE | ws8 | - | ws9 12.89, ws10 7.98 | t1 gcws30b journey 06:59:30..07:03:20 reached 1.38 past the 5.0 fence, ws1r reversed 07:02:10 during, r 14.93 past the 44.0 fence, stamp 07:02:10, ib 15.0 cross 07:02:30 hold 6 bars, ib dwell 12 bars \| rider ws8 4.46, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:03:25 | BATON | ws8 | ws10 | ws9 12.89, ws10 7.98 | ws8 -> ws10, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:13:55 | CADENCE | ws10 | - | ws11 9.10 | t1 gcws30b journey 07:08:30..07:13:50 reached -40.53 past the 5.0 fence, ws1r reversed 07:13:15 during, r 37.66 past the 44.0 fence, stamp 07:13:15, ib 15.0 cross 07:13:00 hold 6 bars, ib dwell 12 bars \| rider ws10 0.40, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 07:13:55 | BATON | ws10 | ws11 | ws11 9.10 | ws10 -> ws11, at a t1 cadence, capped at ws18 by the jump bound 8 |
| 2026-08-14 07:35:55 | CADENCE | ws11 | - | ws12 11.17, ws13 3.33, ws14 3.21, ws15 9.04, ws16 9.62 | t1 gcws30b journey 07:32:30..07:35:50 reached -4.68 past the 5.0 fence, ws1r reversed 07:34:30 during, r 20.24 past the 44.0 fence, stamp 07:34:30, ib 15.0 cross 07:35:00 hold 6 bars, ib dwell 12 bars \| rider ws11 6.80, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:35:55 | BATON | ws11 | ws16 | ws12 11.17, ws13 3.33, ws14 3.21, ws15 9.04, ws16 9.62 | ws11 -> ws16, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 07:44:55 | CADENCE | ws16 | - | ws17 1.79 | t1 gcws30b journey 07:39:30..07:44:50 reached 3.51 past the 5.0 fence, ws1r reversed 07:43:30 during, r 43.70 past the 44.0 fence, stamp 07:43:30, ib 15.0 cross 07:44:00 hold 6 bars, ib dwell 12 bars \| rider ws16 4.38, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:44:55 | BATON | ws16 | ws17 | ws17 1.79 | ws16 -> ws17, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 08:10:10 | BATON | ws17 | ws19 | ws18 21.41, ws19 7.99 | ws17 -> ws19, between cadences, lin_hop 2 |
| 2026-08-14 08:16:55 | BATON | ws19 | ws21 | ws21 8.69 | ws19 -> ws21, between cadences, lin_hop 2 |
| 2026-08-14 08:26:10 | BATON | ws21 | ws23 | ws22 21.85, ws23 15.34 | ws21 -> ws23, between cadences, lin_hop 2 |
| 2026-08-14 08:28:00 | BATON | ws23 | ws25 | ws24 5.58, ws25 12.36 | ws23 -> ws25, between cadences, lin_hop 2 |
| 2026-08-14 08:35:10 | BATON | ws25 | ws27 | ws27 15.90 | ws25 -> ws27, between cadences, lin_hop 2 |
| 2026-08-14 08:35:55 | BATON | ws27 | ws28 | ws28 21.73 | ws27 -> ws28, between cadences, lin_hop 2 |
| 2026-08-14 08:48:30 | NO PASS | ws28 | - | none offered | ws28 17.33 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:11:55 | CADENCE | ws28 | - | ws29 21.09, ws30 6.12 | t1 gcws30b journey 09:05:00..09:11:50 reached 0.19 past the 5.0 fence, ws1r reversed 09:10:55 during, r 19.91 past the 44.0 fence, stamp 09:10:55, ib 15.0 cross 09:11:00 hold 6 bars, ib dwell 12 bars \| rider ws28 1.10, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 09:11:55 | BATON | ws28 | ws30 | ws29 21.09, ws30 6.12 | ws28 -> ws30, at a t1 cadence, capped at ws36 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 09:41:55 | CADENCE | ws30 | - | none offered | t1 gcws30b journey 09:32:00..09:41:50 reached 0.61 past the 5.0 fence, ws1r reversed 09:40:55 during, r 42.96 past the 44.0 fence, stamp 09:40:55, ib 15.0 cross 09:41:00 hold 6 bars, ib dwell 12 bars \| rider ws30 4.18, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 09:41:55 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:40 | NO PASS | ws30 | - | none offered | ws30 18.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:52:25 | CADENCE | ws30 | - | none offered | t1 gcws30b journey 10:47:00..10:52:20 reached -4.72 past the 5.0 fence, ws1r reversed 10:51:10 during, r 19.24 past the 44.0 fence, stamp 10:51:10, ib 15.0 cross 10:51:30 hold 6 bars, ib dwell 12 bars \| rider ws30 24.45, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 10:52:25 | TOP RESET | ws30 | ws4 | ws3 11.95, ws4 12.75 | ws30 24.45 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws4 |
| 2026-08-14 11:04:55 | CADENCE | ws4 | - | ws5 5.15, ws6 6.32 | t1 gcws30b journey 10:56:00..11:04:50 reached -11.18 past the 5.0 fence, ws1r reversed 11:02:10 during, r 33.41 past the 44.0 fence, stamp 11:02:10, ib 15.0 cross 11:04:00 hold 6 bars, ib dwell 12 bars \| rider ws4 2.47, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 11:04:55 | BATON | ws4 | ws6 | ws5 5.15, ws6 6.32 | ws4 -> ws6, at a t1 cadence, capped at ws12 by the jump bound 8 |
| 2026-08-14 11:16:55 | CADENCE | ws6 | - | ws7 2.07 | t1 gcws30b journey 11:12:00..11:16:50 reached -4.55 past the 5.0 fence, ws1r reversed 11:15:20 during, r 16.71 past the 44.0 fence, stamp 11:15:20, ib 15.0 cross 11:16:00 hold 6 bars, ib dwell 12 bars \| rider ws6 0.00, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 11:16:55 | BATON | ws6 | ws7 | ws7 2.07 | ws6 -> ws7, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-08-14 11:26:55 | BATON | ws7 | ws9 | ws8 16.17, ws9 19.08 | ws7 -> ws9, between cadences, lin_hop 2 |
| 2026-08-14 11:33:55 | BATON | ws9 | ws11 | ws11 14.15 | ws9 -> ws11, between cadences, lin_hop 2 |
| 2026-08-14 11:37:50 | NO PASS | ws11 | - | none offered | ws11 16.97 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:16:55 | CADENCE | ws11 | - | ws16 21.15, ws17 14.09 | t1 gcws30b journey 12:09:30..12:16:50 reached -48.25 past the 5.0 fence, ws1r reversed 12:15:35 during, r 21.43 past the 44.0 fence, stamp 12:15:35, ib 15.0 cross 12:16:00 hold 6 bars, ib dwell 12 bars \| rider ws11 34.42, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:16:55 | BATON | ws11 | ws17 | ws16 21.15, ws17 14.09 | ws11 -> ws17, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 12:25:45 | BATON | ws17 | ws18 | ws18 17.51 | ws17 -> ws18, between cadences, lin_hop 2 |
| 2026-08-14 12:32:20 | NO PASS | ws18 | - | none offered | ws18 16.43 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:49:25 | CADENCE | ws18 | - | ws19 22.01, ws20 19.14, ws23 9.99 | t1 gcws30b journey 12:46:00..12:49:20 reached -3.48 past the 5.0 fence, ws1r reversed 12:49:15 during, r 30.77 past the 44.0 fence, stamp 12:49:15, ib 15.0 cross 12:48:30 hold 6 bars, ib dwell 12 bars \| rider ws18 21.99, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 12:49:25 | BATON | ws18 | ws23 | ws19 22.01, ws20 19.14, ws23 9.99 | ws18 -> ws23, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 13:08:25 | CADENCE | ws23 | - | ws30 15.38 | t1 gcws30b journey 13:06:30..13:08:20 reached 4.99 past the 5.0 fence, ws1r reversed 13:07:20 during, r 17.42 past the 44.0 fence, stamp 13:07:20, ib 15.0 cross 13:07:30 hold 6 bars, ib dwell 12 bars \| rider ws23 3.75, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 13:08:25 | BATON | ws23 | ws30 | ws30 15.38 | ws23 -> ws30, at a t1 cadence, capped at ws31 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 13:28:55 | NO PASS | ws30 | - | none offered | ws30 26.30 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:11:55 | CADENCE | ws30 | - | none offered | t1 gcws30b journey 14:02:00..14:11:50 reached -41.17 past the 5.0 fence, ws1r reversed 14:10:55 during, r 26.21 past the 44.0 fence, stamp 14:10:55, ib 15.0 cross 14:11:00 hold 6 bars, ib dwell 12 bars \| rider ws30 34.52, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:11:55 | TOP RESET | ws30 | ws2 | ws2 21.61 | ws30 34.52 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-08-14 14:14:55 | NO PASS | ws2 | - | none offered | ws2 17.00 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 15:00:25 | CADENCE | ws2 | - | none offered | t1 gcws30b journey 14:55:30..15:00:20 reached -6.24 past the 5.0 fence, ws1r reversed 14:57:45 during, r 11.61 past the 44.0 fence, stamp 14:57:45, ib 15.0 cross 14:59:30 hold 6 bars, ib dwell 12 bars \| rider ws2 4.55, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 15:00:25 | HOLD | ws2 | - | - | rider ws2 4.55 oob - no action |
| 2026-08-14 15:05:00 | BATON | ws2 | ws3 | ws3 13.97 | ws2 -> ws3, between cadences, lin_hop 2 |
| 2026-08-14 15:06:55 | NO PASS | ws3 | - | none offered | ws3 20.78 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 16:49:55 | CADENCE | ws3 | - | ws4 18.29 | t1 gcws30b journey 16:46:30..16:49:50 reached -4.49 past the 5.0 fence, ws1r reversed 16:47:40 during, r 2.17 past the 44.0 fence, stamp 16:47:40, ib 15.0 cross 16:49:00 hold 6 bars, ib dwell 12 bars \| rider ws3 26.29, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 16:49:55 | BATON | ws3 | ws4 | ws4 18.29 | ws3 -> ws4, at a t1 cadence, capped at ws11 by the jump bound 8 |
| 2026-08-14 16:56:05 | BATON | ws4 | ws6 | ws5 8.25, ws6 8.81 | ws4 -> ws6, between cadences, lin_hop 2 |
| 2026-08-14 17:18:55 | BATON | ws6 | ws7 | ws7 15.22 | ws6 -> ws7, between cadences, lin_hop 2 |
| 2026-08-14 17:23:55 | BATON | ws7 | ws8 | ws8 16.93 | ws7 -> ws8, between cadences, lin_hop 2 |
| 2026-08-14 17:27:35 | NO PASS | ws8 | - | none offered | ws8 15.56 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 17:46:25 | CADENCE | ws8 | - | ws9 24.37 | t1 gcws30b journey 17:44:00..17:46:20 reached -18.45 past the 5.0 fence, ws1r reversed 17:46:10 during, r 19.13 past the 44.0 fence, stamp 17:46:10, ib 15.0 cross 17:45:30 hold 6 bars, ib dwell 12 bars \| rider ws8 36.65, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 17:46:25 | BATON | ws8 | ws9 | ws9 24.37 | ws8 -> ws9, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 18:06:55 | CADENCE | ws9 | - | ws11 16.95, ws12 13.23 | t1 gcws30b journey 17:50:30..18:06:50 reached -8.64 past the 5.0 fence, ws1r reversed 18:05:25 during, r 38.02 past the 44.0 fence, stamp 18:05:25, ib 15.0 cross 18:06:00 hold 6 bars, ib dwell 12 bars \| rider ws9 17.91, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 18:06:55 | BATON | ws9 | ws12 | ws11 16.95, ws12 13.23 | ws9 -> ws12, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-08-14 18:37:25 | CADENCE | ws12 | - | ws13 16.71, ws14 5.55, ws15 7.30, ws16 17.37 | t1 gcws30b journey 18:31:30..18:37:20 reached -24.30 past the 5.0 fence, ws1r reversed 18:36:15 during, r 1.10 past the 44.0 fence, stamp 18:36:15, ib 15.0 cross 18:36:30 hold 6 bars, ib dwell 12 bars \| rider ws12 6.36, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 18:37:25 | BATON | ws12 | ws16 | ws13 16.71, ws14 5.55, ws15 7.30, ws16 17.37 | ws12 -> ws16, at a t1 cadence, capped at ws20 by the jump bound 8 |
| 2026-08-14 19:09:25 | CADENCE | ws16 | - | ws17 8.88, ws18 17.65, ws19 10.54 | t1 gcws30b journey 18:59:00..19:09:20 reached -31.09 past the 5.0 fence, ws1r reversed 19:01:35 during, r 18.50 past the 44.0 fence, stamp 19:01:35, ib 15.0 cross 19:08:30 hold 6 bars, ib dwell 12 bars \| rider ws16 5.23, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 19:09:25 | BATON | ws16 | ws19 | ws17 8.88, ws18 17.65, ws19 10.54 | ws16 -> ws19, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 19:38:55 | BATON | ws19 | ws20 | ws20 18.32 | ws19 -> ws20, between cadences, lin_hop 2 |
| 2026-08-14 20:00:55 | BATON | ws20 | ws22 | ws21 29.66, ws22 21.06 | ws20 -> ws22, between cadences, lin_hop 2 |
| 2026-08-14 20:10:55 | NO PASS | ws22 | - | none offered | ws22 37.76 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 21:00:55 | CADENCE | ws22 | - | none offered | t1 gcws30b journey 20:56:30..21:00:50 reached -18.88 past the 5.0 fence, ws1r reversed 20:59:05 during, r 31.39 past the 44.0 fence, stamp 20:59:05, ib 15.0 cross 21:00:00 hold 6 bars, ib dwell 12 bars \| rider ws22 59.99, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 21:00:55 | EXHAUST | ws22 | - | - | t4 at a t1 cadence - rider ws22 59.99, no candidate at or below ws30 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-14 21:00:55 |
| baton passes made | 30 |
| minutes from the arm to the verdict | 841.9 |
| the rider chain | ws8 > ws10 > ws11 > ws16 > ws17 > ws19 > ws21 > ws23 > ws25 > ws27 > ws28 > ws30 > ws4 > ws6 > ws7 > ws9 > ws11 > ws17 > ws18 > ws23 > ws30 > ws2 > ws3 > ws4 > ws6 > ws7 > ws8 > ws9 > ws12 > ws16 > ws19 > ws20 > ws22 |

## MODE 'reversal' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | - | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 07:03:05 | RIDER | ws8 | - | - | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:03:25 | CADENCE | ws8 | - | ws9 12.89, ws10 7.98 | t1 gcws30b journey 06:59:30..07:03:20 reached 1.38 past the 5.0 fence, ws1r reversed 07:02:10 during, r 14.93 past the 44.0 fence, stamp 07:02:10, ib 15.0 cross 07:02:30 hold 6 bars, ib dwell 12 bars \| rider ws8 4.46, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:03:25 | BATON | ws8 | ws10 | ws9 12.89, ws10 7.98 | ws8 -> ws10, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:05:35 | NO PASS | ws10 | - | none offered | ws10 9.30 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 07:13:55 | CADENCE | ws10 | - | ws11 9.10 | t1 gcws30b journey 07:08:30..07:13:50 reached -40.53 past the 5.0 fence, ws1r reversed 07:13:15 during, r 37.66 past the 44.0 fence, stamp 07:13:15, ib 15.0 cross 07:13:00 hold 6 bars, ib dwell 12 bars \| rider ws10 0.40, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 07:13:55 | BATON | ws10 | ws11 | ws11 9.10 | ws10 -> ws11, at a t1 cadence, capped at ws18 by the jump bound 8 |
| 2026-08-14 07:35:55 | CADENCE | ws11 | - | ws12 11.17, ws13 3.33, ws14 3.21, ws15 9.04, ws16 9.62 | t1 gcws30b journey 07:32:30..07:35:50 reached -4.68 past the 5.0 fence, ws1r reversed 07:34:30 during, r 20.24 past the 44.0 fence, stamp 07:34:30, ib 15.0 cross 07:35:00 hold 6 bars, ib dwell 12 bars \| rider ws11 6.80, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:35:55 | BATON | ws11 | ws16 | ws12 11.17, ws13 3.33, ws14 3.21, ws15 9.04, ws16 9.62 | ws11 -> ws16, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 07:44:55 | CADENCE | ws16 | - | ws17 1.79 | t1 gcws30b journey 07:39:30..07:44:50 reached 3.51 past the 5.0 fence, ws1r reversed 07:43:30 during, r 43.70 past the 44.0 fence, stamp 07:43:30, ib 15.0 cross 07:44:00 hold 6 bars, ib dwell 12 bars \| rider ws16 4.38, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:44:55 | BATON | ws16 | ws17 | ws17 1.79 | ws16 -> ws17, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:52:35 | BATON | ws17 | ws18 | ws18 7.16 | ws17 -> ws18, between cadences, lin_hop 2 |
| 2026-08-14 08:06:55 | BATON | ws18 | ws19 | ws19 4.83 | ws18 -> ws19, between cadences, lin_hop 2 |
| 2026-08-14 08:09:45 | BATON | ws19 | ws21 | ws21 8.94 | ws19 -> ws21, between cadences, lin_hop 2 |
| 2026-08-14 08:10:10 | BATON | ws21 | ws22 | ws22 12.26 | ws21 -> ws22, between cadences, lin_hop 2 |
| 2026-08-14 08:10:20 | NO PASS | ws22 | - | none offered | ws22 12.34 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:11:55 | CADENCE | ws22 | - | ws23 20.32, ws24 5.08, ws25 12.91, ws26 23.95, ws27 10.41, ws28 1.10, ws29 21.09, ws30 6.12 | t1 gcws30b journey 09:05:00..09:11:50 reached 0.19 past the 5.0 fence, ws1r reversed 09:10:55 during, r 19.91 past the 44.0 fence, stamp 09:10:55, ib 15.0 cross 09:11:00 hold 6 bars, ib dwell 12 bars \| rider ws22 37.35, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:11:55 | BATON | ws22 | ws30 | ws23 20.32, ws24 5.08, ws25 12.91, ws26 23.95, ws27 10.41, ws28 1.10, ws29 21.09, ws30 6.12 | ws22 -> ws30, at a t1 cadence, capped at ws30 by the jump bound 8 |
| 2026-08-14 09:14:30 | NO PASS | ws30 | - | none offered | ws30 10.59 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:41:55 | CADENCE | ws30 | - | none offered | t1 gcws30b journey 09:32:00..09:41:50 reached 0.61 past the 5.0 fence, ws1r reversed 09:40:55 during, r 42.96 past the 44.0 fence, stamp 09:40:55, ib 15.0 cross 09:41:00 hold 6 bars, ib dwell 12 bars \| rider ws30 4.18, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 09:41:55 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:10 | NO PASS | ws30 | - | none offered | ws30 16.80 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:52:25 | CADENCE | ws30 | - | none offered | t1 gcws30b journey 10:47:00..10:52:20 reached -4.72 past the 5.0 fence, ws1r reversed 10:51:10 during, r 19.24 past the 44.0 fence, stamp 10:51:10, ib 15.0 cross 10:51:30 hold 6 bars, ib dwell 12 bars \| rider ws30 24.45, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 10:52:25 | TOP RESET | ws30 | ws4 | ws3 11.95, ws4 12.75 | ws30 24.45 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws4 |
| 2026-08-14 10:52:45 | NO PASS | ws4 | - | none offered | ws4 13.26 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 11:04:55 | CADENCE | ws4 | - | ws5 5.15, ws6 6.32 | t1 gcws30b journey 10:56:00..11:04:50 reached -11.18 past the 5.0 fence, ws1r reversed 11:02:10 during, r 33.41 past the 44.0 fence, stamp 11:02:10, ib 15.0 cross 11:04:00 hold 6 bars, ib dwell 12 bars \| rider ws4 2.47, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 11:04:55 | BATON | ws4 | ws6 | ws5 5.15, ws6 6.32 | ws4 -> ws6, at a t1 cadence, capped at ws12 by the jump bound 8 |
| 2026-08-14 11:16:55 | CADENCE | ws6 | - | ws7 2.07 | t1 gcws30b journey 11:12:00..11:16:50 reached -4.55 past the 5.0 fence, ws1r reversed 11:15:20 during, r 16.71 past the 44.0 fence, stamp 11:15:20, ib 15.0 cross 11:16:00 hold 6 bars, ib dwell 12 bars \| rider ws6 0.00, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 11:16:55 | BATON | ws6 | ws7 | ws7 2.07 | ws6 -> ws7, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-08-14 11:19:40 | NO PASS | ws7 | - | none offered | ws7 15.89 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:16:55 | CADENCE | ws7 | - | none offered | t1 gcws30b journey 12:09:30..12:16:50 reached -48.25 past the 5.0 fence, ws1r reversed 12:15:35 during, r 21.43 past the 44.0 fence, stamp 12:15:35, ib 15.0 cross 12:16:00 hold 6 bars, ib dwell 12 bars \| rider ws7 64.58, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:16:55 | EXHAUST | ws7 | - | - | t4 at a t1 cadence - rider ws7 64.58, no candidate at or below ws15 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-14 12:16:55 |
| baton passes made | 11 |
| minutes from the arm to the verdict | 317.9 |
| the rider chain | ws8 > ws10 > ws11 > ws16 > ws17 > ws18 > ws19 > ws21 > ws22 > ws30 > ws4 > ws6 > ws7 |

## MODE 'reversal+quarter' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | - | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 07:03:05 | RIDER | ws8 | - | - | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:03:25 | CADENCE | ws8 | - | ws9 12.89, ws10 7.98 | t1 gcws30b journey 06:59:30..07:03:20 reached 1.38 past the 5.0 fence, ws1r reversed 07:02:10 during, r 14.93 past the 44.0 fence, stamp 07:02:10, ib 15.0 cross 07:02:30 hold 6 bars, ib dwell 12 bars \| rider ws8 4.46, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:03:25 | BATON | ws8 | ws10 | ws9 12.89, ws10 7.98 | ws8 -> ws10, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:04:55 | NO PASS | ws10 | - | none offered | ws10 8.51 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 07:13:55 | CADENCE | ws10 | - | ws11 9.10 | t1 gcws30b journey 07:08:30..07:13:50 reached -40.53 past the 5.0 fence, ws1r reversed 07:13:15 during, r 37.66 past the 44.0 fence, stamp 07:13:15, ib 15.0 cross 07:13:00 hold 6 bars, ib dwell 12 bars \| rider ws10 0.40, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 07:13:55 | BATON | ws10 | ws11 | ws11 9.10 | ws10 -> ws11, at a t1 cadence, capped at ws18 by the jump bound 8 |
| 2026-08-14 07:35:55 | CADENCE | ws11 | - | ws12 11.17, ws13 3.33, ws14 3.21, ws15 9.04, ws16 9.62 | t1 gcws30b journey 07:32:30..07:35:50 reached -4.68 past the 5.0 fence, ws1r reversed 07:34:30 during, r 20.24 past the 44.0 fence, stamp 07:34:30, ib 15.0 cross 07:35:00 hold 6 bars, ib dwell 12 bars \| rider ws11 6.80, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:35:55 | BATON | ws11 | ws16 | ws12 11.17, ws13 3.33, ws14 3.21, ws15 9.04, ws16 9.62 | ws11 -> ws16, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 07:44:55 | CADENCE | ws16 | - | ws17 1.79 | t1 gcws30b journey 07:39:30..07:44:50 reached 3.51 past the 5.0 fence, ws1r reversed 07:43:30 during, r 43.70 past the 44.0 fence, stamp 07:43:30, ib 15.0 cross 07:44:00 hold 6 bars, ib dwell 12 bars \| rider ws16 4.38, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:44:55 | BATON | ws16 | ws17 | ws17 1.79 | ws16 -> ws17, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:55:55 | BATON | ws17 | ws19 | ws18 7.08, ws19 4.83 | ws17 -> ws19, between cadences, lin_hop 2 |
| 2026-08-14 08:13:35 | BATON | ws19 | ws21 | ws21 9.33 | ws19 -> ws21, between cadences, lin_hop 2 |
| 2026-08-14 08:14:30 | BATON | ws21 | ws22 | ws22 9.33 | ws21 -> ws22, between cadences, lin_hop 2 |
| 2026-08-14 08:14:55 | NO PASS | ws22 | - | none offered | ws22 9.02 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:11:55 | CADENCE | ws22 | - | ws23 20.32, ws24 5.08, ws25 12.91, ws26 23.95, ws27 10.41, ws28 1.10, ws29 21.09, ws30 6.12 | t1 gcws30b journey 09:05:00..09:11:50 reached 0.19 past the 5.0 fence, ws1r reversed 09:10:55 during, r 19.91 past the 44.0 fence, stamp 09:10:55, ib 15.0 cross 09:11:00 hold 6 bars, ib dwell 12 bars \| rider ws22 37.35, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:11:55 | BATON | ws22 | ws30 | ws23 20.32, ws24 5.08, ws25 12.91, ws26 23.95, ws27 10.41, ws28 1.10, ws29 21.09, ws30 6.12 | ws22 -> ws30, at a t1 cadence, capped at ws30 by the jump bound 8 |
| 2026-08-14 09:21:05 | NO PASS | ws30 | - | none offered | ws30 6.12 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:41:55 | CADENCE | ws30 | - | none offered | t1 gcws30b journey 09:32:00..09:41:50 reached 0.61 past the 5.0 fence, ws1r reversed 09:40:55 during, r 42.96 past the 44.0 fence, stamp 09:40:55, ib 15.0 cross 09:41:00 hold 6 bars, ib dwell 12 bars \| rider ws30 4.18, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 09:41:55 | HOLD | ws30 | - | - | rider ws30 4.18 oob - no action |
| 2026-08-14 10:07:45 | NO PASS | ws30 | - | none offered | ws30 18.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:52:25 | CADENCE | ws30 | - | none offered | t1 gcws30b journey 10:47:00..10:52:20 reached -4.72 past the 5.0 fence, ws1r reversed 10:51:10 during, r 19.24 past the 44.0 fence, stamp 10:51:10, ib 15.0 cross 10:51:30 hold 6 bars, ib dwell 12 bars \| rider ws30 24.45, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 10:52:25 | TOP RESET | ws30 | ws4 | ws3 11.95, ws4 12.75 | ws30 24.45 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws4 |
| 2026-08-14 10:52:50 | NO PASS | ws4 | - | none offered | ws4 13.26 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 11:04:55 | CADENCE | ws4 | - | ws5 5.15, ws6 6.32 | t1 gcws30b journey 10:56:00..11:04:50 reached -11.18 past the 5.0 fence, ws1r reversed 11:02:10 during, r 33.41 past the 44.0 fence, stamp 11:02:10, ib 15.0 cross 11:04:00 hold 6 bars, ib dwell 12 bars \| rider ws4 2.47, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 11:04:55 | BATON | ws4 | ws6 | ws5 5.15, ws6 6.32 | ws4 -> ws6, at a t1 cadence, capped at ws12 by the jump bound 8 |
| 2026-08-14 11:16:55 | CADENCE | ws6 | - | ws7 2.07 | t1 gcws30b journey 11:12:00..11:16:50 reached -4.55 past the 5.0 fence, ws1r reversed 11:15:20 during, r 16.71 past the 44.0 fence, stamp 11:15:20, ib 15.0 cross 11:16:00 hold 6 bars, ib dwell 12 bars \| rider ws6 0.00, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 11:16:55 | BATON | ws6 | ws7 | ws7 2.07 | ws6 -> ws7, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-08-14 11:20:30 | BATON | ws7 | ws8 | ws8 17.81 | ws7 -> ws8, between cadences, lin_hop 2 |
| 2026-08-14 11:20:45 | NO PASS | ws8 | - | none offered | ws8 16.71 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:16:55 | CADENCE | ws8 | - | ws16 21.15 | t1 gcws30b journey 12:09:30..12:16:50 reached -48.25 past the 5.0 fence, ws1r reversed 12:15:35 during, r 21.43 past the 44.0 fence, stamp 12:15:35, ib 15.0 cross 12:16:00 hold 6 bars, ib dwell 12 bars \| rider ws8 64.96, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:16:55 | BATON | ws8 | ws16 | ws16 21.15 | ws8 -> ws16, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 12:28:00 | BATON | ws16 | ws18 | ws17 11.04, ws18 10.82 | ws16 -> ws18, between cadences, lin_hop 2 |
| 2026-08-14 12:28:40 | NO PASS | ws18 | - | none offered | ws18 10.82 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:49:25 | CADENCE | ws18 | - | ws19 22.01, ws20 19.14, ws23 9.99 | t1 gcws30b journey 12:46:00..12:49:20 reached -3.48 past the 5.0 fence, ws1r reversed 12:49:15 during, r 30.77 past the 44.0 fence, stamp 12:49:15, ib 15.0 cross 12:48:30 hold 6 bars, ib dwell 12 bars \| rider ws18 21.99, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 12:49:25 | BATON | ws18 | ws23 | ws19 22.01, ws20 19.14, ws23 9.99 | ws18 -> ws23, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 12:55:40 | NO PASS | ws23 | - | none offered | ws23 13.81 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 13:08:25 | CADENCE | ws23 | - | ws30 15.38 | t1 gcws30b journey 13:06:30..13:08:20 reached 4.99 past the 5.0 fence, ws1r reversed 13:07:20 during, r 17.42 past the 44.0 fence, stamp 13:07:20, ib 15.0 cross 13:07:30 hold 6 bars, ib dwell 12 bars \| rider ws23 3.75, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 13:08:25 | BATON | ws23 | ws30 | ws30 15.38 | ws23 -> ws30, at a t1 cadence, capped at ws31 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 13:21:50 | NO PASS | ws30 | - | none offered | ws30 15.38 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:11:55 | CADENCE | ws30 | - | none offered | t1 gcws30b journey 14:02:00..14:11:50 reached -41.17 past the 5.0 fence, ws1r reversed 14:10:55 during, r 26.21 past the 44.0 fence, stamp 14:10:55, ib 15.0 cross 14:11:00 hold 6 bars, ib dwell 12 bars \| rider ws30 34.52, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:11:55 | TOP RESET | ws30 | ws2 | ws2 21.61 | ws30 34.52 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-08-14 14:14:55 | NO PASS | ws2 | - | none offered | ws2 17.00 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 15:00:25 | CADENCE | ws2 | - | none offered | t1 gcws30b journey 14:55:30..15:00:20 reached -6.24 past the 5.0 fence, ws1r reversed 14:57:45 during, r 11.61 past the 44.0 fence, stamp 14:57:45, ib 15.0 cross 14:59:30 hold 6 bars, ib dwell 12 bars \| rider ws2 4.55, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 15:00:25 | HOLD | ws2 | - | - | rider ws2 4.55 oob - no action |
| 2026-08-14 15:01:25 | NO PASS | ws2 | - | none offered | ws2 12.98 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 16:49:55 | CADENCE | ws2 | - | ws4 18.29 | t1 gcws30b journey 16:46:30..16:49:50 reached -4.49 past the 5.0 fence, ws1r reversed 16:47:40 during, r 2.17 past the 44.0 fence, stamp 16:47:40, ib 15.0 cross 16:49:00 hold 6 bars, ib dwell 12 bars \| rider ws2 14.29, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 16:49:55 | BATON | ws2 | ws4 | ws4 18.29 | ws2 -> ws4, at a t1 cadence, capped at ws10 by the jump bound 8 |
| 2026-08-14 16:56:15 | BATON | ws4 | ws6 | ws5 6.28, ws6 7.94 | ws4 -> ws6, between cadences, lin_hop 2 |
| 2026-08-14 17:01:15 | NO PASS | ws6 | - | none offered | ws6 14.55 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 17:46:25 | CADENCE | ws6 | - | ws9 24.37 | t1 gcws30b journey 17:44:00..17:46:20 reached -18.45 past the 5.0 fence, ws1r reversed 17:46:10 during, r 19.13 past the 44.0 fence, stamp 17:46:10, ib 15.0 cross 17:45:30 hold 6 bars, ib dwell 12 bars \| rider ws6 55.86, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 17:46:25 | BATON | ws6 | ws9 | ws9 24.37 | ws6 -> ws9, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-08-14 17:47:15 | NO PASS | ws9 | - | none offered | ws9 25.59 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 18:06:55 | CADENCE | ws9 | - | ws11 16.95, ws12 13.23 | t1 gcws30b journey 17:50:30..18:06:50 reached -8.64 past the 5.0 fence, ws1r reversed 18:05:25 during, r 38.02 past the 44.0 fence, stamp 18:05:25, ib 15.0 cross 18:06:00 hold 6 bars, ib dwell 12 bars \| rider ws9 17.91, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 18:06:55 | BATON | ws9 | ws12 | ws11 16.95, ws12 13.23 | ws9 -> ws12, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-08-14 18:37:25 | CADENCE | ws12 | - | ws13 16.71, ws14 5.55, ws15 7.30, ws16 17.37 | t1 gcws30b journey 18:31:30..18:37:20 reached -24.30 past the 5.0 fence, ws1r reversed 18:36:15 during, r 1.10 past the 44.0 fence, stamp 18:36:15, ib 15.0 cross 18:36:30 hold 6 bars, ib dwell 12 bars \| rider ws12 6.36, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 18:37:25 | BATON | ws12 | ws16 | ws13 16.71, ws14 5.55, ws15 7.30, ws16 17.37 | ws12 -> ws16, at a t1 cadence, capped at ws20 by the jump bound 8 |
| 2026-08-14 19:09:25 | CADENCE | ws16 | - | ws17 8.88, ws18 17.65, ws19 10.54 | t1 gcws30b journey 18:59:00..19:09:20 reached -31.09 past the 5.0 fence, ws1r reversed 19:01:35 during, r 18.50 past the 44.0 fence, stamp 19:01:35, ib 15.0 cross 19:08:30 hold 6 bars, ib dwell 12 bars \| rider ws16 5.23, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 19:09:25 | BATON | ws16 | ws19 | ws17 8.88, ws18 17.65, ws19 10.54 | ws16 -> ws19, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 19:32:30 | BATON | ws19 | ws20 | ws20 17.15 | ws19 -> ws20, between cadences, lin_hop 2 |
| 2026-08-14 19:32:50 | BATON | ws20 | ws22 | ws22 22.36 | ws20 -> ws22, between cadences, lin_hop 2 |
| 2026-08-14 19:36:45 | NO PASS | ws22 | - | none offered | ws22 22.13 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 21:00:55 | CADENCE | ws22 | - | none offered | t1 gcws30b journey 20:56:30..21:00:50 reached -18.88 past the 5.0 fence, ws1r reversed 20:59:05 during, r 31.39 past the 44.0 fence, stamp 20:59:05, ib 15.0 cross 21:00:00 hold 6 bars, ib dwell 12 bars \| rider ws22 59.99, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 21:00:55 | EXHAUST | ws22 | - | - | t4 at a t1 cadence - rider ws22 59.99, no candidate at or below ws30 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-14 21:00:55 |
| baton passes made | 23 |
| minutes from the arm to the verdict | 841.9 |
| the rider chain | ws8 > ws10 > ws11 > ws16 > ws17 > ws19 > ws21 > ws22 > ws30 > ws4 > ws6 > ws7 > ws8 > ws16 > ws18 > ws23 > ws30 > ws2 > ws4 > ws6 > ws9 > ws12 > ws16 > ws19 > ws20 > ws22 |

## MODE 'ib' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 06:59:00 | RETEST | - | ws1r 12.95 oob + ws2r 52.91 / ws3r 70.72 in - the gate opens; ws1r oob->ib cross 2026-08-14 07:02:10, wob 12, cadence at 2026-08-14 07:03:05 |
| 2026-08-14 07:03:05 | RIDER | ws8 | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:03:25 | CADENCE | ws8 | t1 gcws30b journey 06:59:30..07:03:20 reached 1.38 past the 5.0 fence, ws1r reversed 07:02:10 during, r 14.93 past the 44.0 fence, stamp 07:02:10, ib 15.0 cross 07:02:30 hold 6 bars, ib dwell 12 bars \| rider ws8 4.46, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:03:25 | BATON | ws8 | ws8 -> ws10, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:13:55 | LATCH1 | ws10 | latch 1 at the t1 cadence 2026-08-14 07:13:55, divergence state -1 |
| 2026-08-14 07:13:55 | CADENCE | ws10 | t1 gcws30b journey 07:08:30..07:13:50 reached -40.53 past the 5.0 fence, ws1r reversed 07:13:15 during, r 37.66 past the 44.0 fence, stamp 07:13:15, ib 15.0 cross 07:13:00 hold 6 bars, ib dwell 12 bars \| rider ws10 0.40, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 07:13:55 | BATON | ws10 | ws10 -> ws11, at a t1 cadence, capped at ws18 by the jump bound 8 |
| 2026-08-14 07:35:55 | LATCH1 | ws11 | latch 1 at the t1 cadence 2026-08-14 07:35:55, divergence state -1 |
| 2026-08-14 07:35:55 | CADENCE | ws11 | t1 gcws30b journey 07:32:30..07:35:50 reached -4.68 past the 5.0 fence, ws1r reversed 07:34:30 during, r 20.24 past the 44.0 fence, stamp 07:34:30, ib 15.0 cross 07:35:00 hold 6 bars, ib dwell 12 bars \| rider ws11 6.80, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:35:55 | BATON | ws11 | ws11 -> ws16, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 07:44:55 | LATCH1 | ws16 | latch 1 at the t1 cadence 2026-08-14 07:44:55, divergence state -1 |
| 2026-08-14 07:44:55 | CADENCE | ws16 | t1 gcws30b journey 07:39:30..07:44:50 reached 3.51 past the 5.0 fence, ws1r reversed 07:43:30 during, r 43.70 past the 44.0 fence, stamp 07:43:30, ib 15.0 cross 07:44:00 hold 6 bars, ib dwell 12 bars \| rider ws16 4.38, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:44:55 | BATON | ws16 | ws16 -> ws17, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 08:10:10 | BATON | ws17 | ws17 -> ws19, between cadences, lin_hop 2 |
| 2026-08-14 08:16:55 | BATON | ws19 | ws19 -> ws21, between cadences, lin_hop 2 |
| 2026-08-14 08:26:10 | BATON | ws21 | ws21 -> ws23, between cadences, lin_hop 2 |
| 2026-08-14 08:28:00 | BATON | ws23 | ws23 -> ws25, between cadences, lin_hop 2 |
| 2026-08-14 08:35:10 | BATON | ws25 | ws25 -> ws27, between cadences, lin_hop 2 |
| 2026-08-14 08:35:55 | BATON | ws27 | ws27 -> ws28, between cadences, lin_hop 2 |
| 2026-08-14 08:48:30 | NO PASS | ws28 | ws28 17.33 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:11:55 | LATCH1 | ws28 | latch 1 at the t1 cadence 2026-08-14 09:11:55, divergence state -1 |
| 2026-08-14 09:11:55 | CADENCE | ws28 | t1 gcws30b journey 09:05:00..09:11:50 reached 0.19 past the 5.0 fence, ws1r reversed 09:10:55 during, r 19.91 past the 44.0 fence, stamp 09:10:55, ib 15.0 cross 09:11:00 hold 6 bars, ib dwell 12 bars \| rider ws28 1.10, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 09:11:55 | BATON | ws28 | ws28 -> ws30, at a t1 cadence, capped at ws36 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 09:41:55 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:41:55, divergence state -1 |
| 2026-08-14 09:41:55 | CADENCE | ws30 | t1 gcws30b journey 09:32:00..09:41:50 reached 0.61 past the 5.0 fence, ws1r reversed 09:40:55 during, r 42.96 past the 44.0 fence, stamp 09:40:55, ib 15.0 cross 09:41:00 hold 6 bars, ib dwell 12 bars \| rider ws30 4.18, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 09:41:55 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:40 | NO PASS | ws30 | ws30 18.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:52:25 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 10:52:25, divergence state -1 |
| 2026-08-14 10:52:25 | CADENCE | ws30 | t1 gcws30b journey 10:47:00..10:52:20 reached -4.72 past the 5.0 fence, ws1r reversed 10:51:10 during, r 19.24 past the 44.0 fence, stamp 10:51:10, ib 15.0 cross 10:51:30 hold 6 bars, ib dwell 12 bars \| rider ws30 24.45, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 10:52:25 | TOP RESET | ws30 | ws30 24.45 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws4 |
| 2026-08-14 11:04:55 | LATCH1 | ws4 | latch 1 at the t1 cadence 2026-08-14 11:04:55, divergence state -1 |
| 2026-08-14 11:04:55 | CADENCE | ws4 | t1 gcws30b journey 10:56:00..11:04:50 reached -11.18 past the 5.0 fence, ws1r reversed 11:02:10 during, r 33.41 past the 44.0 fence, stamp 11:02:10, ib 15.0 cross 11:04:00 hold 6 bars, ib dwell 12 bars \| rider ws4 2.47, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 11:04:55 | BATON | ws4 | ws4 -> ws6, at a t1 cadence, capped at ws12 by the jump bound 8 |
| 2026-08-14 11:16:55 | LATCH1 | ws6 | latch 1 at the t1 cadence 2026-08-14 11:16:55, divergence state -1 |
| 2026-08-14 11:16:55 | CADENCE | ws6 | t1 gcws30b journey 11:12:00..11:16:50 reached -4.55 past the 5.0 fence, ws1r reversed 11:15:20 during, r 16.71 past the 44.0 fence, stamp 11:15:20, ib 15.0 cross 11:16:00 hold 6 bars, ib dwell 12 bars \| rider ws6 0.00, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 11:16:55 | BATON | ws6 | ws6 -> ws7, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-08-14 11:26:55 | BATON | ws7 | ws7 -> ws9, between cadences, lin_hop 2 |
| 2026-08-14 11:33:55 | BATON | ws9 | ws9 -> ws11, between cadences, lin_hop 2 |
| 2026-08-14 11:37:50 | NO PASS | ws11 | ws11 16.97 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:16:55 | LATCH1 | ws11 | latch 1 at the t1 cadence 2026-08-14 12:16:55, divergence state -1 |
| 2026-08-14 12:16:55 | CADENCE | ws11 | t1 gcws30b journey 12:09:30..12:16:50 reached -48.25 past the 5.0 fence, ws1r reversed 12:15:35 during, r 21.43 past the 44.0 fence, stamp 12:15:35, ib 15.0 cross 12:16:00 hold 6 bars, ib dwell 12 bars \| rider ws11 34.42, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:16:55 | BATON | ws11 | ws11 -> ws17, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 12:25:45 | BATON | ws17 | ws17 -> ws18, between cadences, lin_hop 2 |
| 2026-08-14 12:32:20 | NO PASS | ws18 | ws18 16.43 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:49:25 | CADENCE | ws18 | t1 gcws30b journey 12:46:00..12:49:20 reached -3.48 past the 5.0 fence, ws1r reversed 12:49:15 during, r 30.77 past the 44.0 fence, stamp 12:49:15, ib 15.0 cross 12:48:30 hold 6 bars, ib dwell 12 bars \| rider ws18 21.99, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 12:49:25 | BATON | ws18 | ws18 -> ws23, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 13:08:25 | LATCH1 | ws23 | latch 1 at the t1 cadence 2026-08-14 13:08:25, divergence state -1 |
| 2026-08-14 13:08:25 | CADENCE | ws23 | t1 gcws30b journey 13:06:30..13:08:20 reached 4.99 past the 5.0 fence, ws1r reversed 13:07:20 during, r 17.42 past the 44.0 fence, stamp 13:07:20, ib 15.0 cross 13:07:30 hold 6 bars, ib dwell 12 bars \| rider ws23 3.75, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 13:08:25 | BATON | ws23 | ws23 -> ws30, at a t1 cadence, capped at ws31 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 13:28:55 | NO PASS | ws30 | ws30 26.30 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:11:55 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 14:11:55, divergence state -1 |
| 2026-08-14 14:11:55 | CADENCE | ws30 | t1 gcws30b journey 14:02:00..14:11:50 reached -41.17 past the 5.0 fence, ws1r reversed 14:10:55 during, r 26.21 past the 44.0 fence, stamp 14:10:55, ib 15.0 cross 14:11:00 hold 6 bars, ib dwell 12 bars \| rider ws30 34.52, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:11:55 | TOP RESET | ws30 | ws30 34.52 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-08-14 14:14:55 | NO PASS | ws2 | ws2 17.00 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 15:00:25 | CADENCE | ws2 | t1 gcws30b journey 14:55:30..15:00:20 reached -6.24 past the 5.0 fence, ws1r reversed 14:57:45 during, r 11.61 past the 44.0 fence, stamp 14:57:45, ib 15.0 cross 14:59:30 hold 6 bars, ib dwell 12 bars \| rider ws2 4.55, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 15:00:25 | HOLD | ws2 | rider ws2 4.55 oob - no action |
| 2026-08-14 15:05:00 | BATON | ws2 | ws2 -> ws3, between cadences, lin_hop 2 |
| 2026-08-14 15:06:55 | NO PASS | ws3 | ws3 20.78 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 16:49:55 | LATCH1 | ws3 | latch 1 at the t1 cadence 2026-08-14 16:49:55, divergence state -1 |
| 2026-08-14 16:49:55 | CADENCE | ws3 | t1 gcws30b journey 16:46:30..16:49:50 reached -4.49 past the 5.0 fence, ws1r reversed 16:47:40 during, r 2.17 past the 44.0 fence, stamp 16:47:40, ib 15.0 cross 16:49:00 hold 6 bars, ib dwell 12 bars \| rider ws3 26.29, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 16:49:55 | BATON | ws3 | ws3 -> ws4, at a t1 cadence, capped at ws11 by the jump bound 8 |
| 2026-08-14 16:56:05 | BATON | ws4 | ws4 -> ws6, between cadences, lin_hop 2 |
| 2026-08-14 17:18:55 | BATON | ws6 | ws6 -> ws7, between cadences, lin_hop 2 |
| 2026-08-14 17:23:55 | BATON | ws7 | ws7 -> ws8, between cadences, lin_hop 2 |
| 2026-08-14 17:27:35 | NO PASS | ws8 | ws8 15.56 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 17:46:25 | LATCH1 | ws8 | latch 1 at the t1 cadence 2026-08-14 17:46:25, divergence state -1 |
| 2026-08-14 17:46:25 | CADENCE | ws8 | t1 gcws30b journey 17:44:00..17:46:20 reached -18.45 past the 5.0 fence, ws1r reversed 17:46:10 during, r 19.13 past the 44.0 fence, stamp 17:46:10, ib 15.0 cross 17:45:30 hold 6 bars, ib dwell 12 bars \| rider ws8 36.65, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 17:46:25 | BATON | ws8 | ws8 -> ws9, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 18:06:55 | LATCH1 | ws9 | latch 1 at the t1 cadence 2026-08-14 18:06:55, divergence state -1 |
| 2026-08-14 18:06:55 | CADENCE | ws9 | t1 gcws30b journey 17:50:30..18:06:50 reached -8.64 past the 5.0 fence, ws1r reversed 18:05:25 during, r 38.02 past the 44.0 fence, stamp 18:05:25, ib 15.0 cross 18:06:00 hold 6 bars, ib dwell 12 bars \| rider ws9 17.91, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 18:06:55 | BATON | ws9 | ws9 -> ws12, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-08-14 18:37:25 | LATCH1 | ws12 | latch 1 at the t1 cadence 2026-08-14 18:37:25, divergence state -1 |
| 2026-08-14 18:37:25 | CADENCE | ws12 | t1 gcws30b journey 18:31:30..18:37:20 reached -24.30 past the 5.0 fence, ws1r reversed 18:36:15 during, r 1.10 past the 44.0 fence, stamp 18:36:15, ib 15.0 cross 18:36:30 hold 6 bars, ib dwell 12 bars \| rider ws12 6.36, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 18:37:25 | BATON | ws12 | ws12 -> ws16, at a t1 cadence, capped at ws20 by the jump bound 8 |
| 2026-08-14 19:09:25 | CADENCE | ws16 | t1 gcws30b journey 18:59:00..19:09:20 reached -31.09 past the 5.0 fence, ws1r reversed 19:01:35 during, r 18.50 past the 44.0 fence, stamp 19:01:35, ib 15.0 cross 19:08:30 hold 6 bars, ib dwell 12 bars \| rider ws16 5.23, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 19:09:25 | BATON | ws16 | ws16 -> ws19, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 19:38:55 | BATON | ws19 | ws19 -> ws20, between cadences, lin_hop 2 |
| 2026-08-14 20:00:55 | BATON | ws20 | ws20 -> ws22, between cadences, lin_hop 2 |
| 2026-08-14 20:10:55 | NO PASS | ws22 | ws22 37.76 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 21:00:55 | CADENCE | ws22 | t1 gcws30b journey 20:56:30..21:00:50 reached -18.88 past the 5.0 fence, ws1r reversed 20:59:05 during, r 31.39 past the 44.0 fence, stamp 20:59:05, ib 15.0 cross 21:00:00 hold 6 bars, ib dwell 12 bars \| rider ws22 59.99, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 21:00:55 | EXHAUST | ws22 | t4 at a t1 cadence - rider ws22 59.99, no candidate at or below ws30 (the jump bound 8) |

## MODE 'reversal' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 06:59:00 | RETEST | - | ws1r 12.95 oob + ws2r 52.91 / ws3r 70.72 in - the gate opens; ws1r oob->ib cross 2026-08-14 07:02:10, wob 12, cadence at 2026-08-14 07:03:05 |
| 2026-08-14 07:03:05 | RIDER | ws8 | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:03:25 | CADENCE | ws8 | t1 gcws30b journey 06:59:30..07:03:20 reached 1.38 past the 5.0 fence, ws1r reversed 07:02:10 during, r 14.93 past the 44.0 fence, stamp 07:02:10, ib 15.0 cross 07:02:30 hold 6 bars, ib dwell 12 bars \| rider ws8 4.46, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:03:25 | BATON | ws8 | ws8 -> ws10, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:05:35 | NO PASS | ws10 | ws10 9.30 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 07:13:55 | LATCH1 | ws10 | latch 1 at the t1 cadence 2026-08-14 07:13:55, divergence state -1 |
| 2026-08-14 07:13:55 | CADENCE | ws10 | t1 gcws30b journey 07:08:30..07:13:50 reached -40.53 past the 5.0 fence, ws1r reversed 07:13:15 during, r 37.66 past the 44.0 fence, stamp 07:13:15, ib 15.0 cross 07:13:00 hold 6 bars, ib dwell 12 bars \| rider ws10 0.40, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 07:13:55 | BATON | ws10 | ws10 -> ws11, at a t1 cadence, capped at ws18 by the jump bound 8 |
| 2026-08-14 07:35:55 | LATCH1 | ws11 | latch 1 at the t1 cadence 2026-08-14 07:35:55, divergence state -1 |
| 2026-08-14 07:35:55 | CADENCE | ws11 | t1 gcws30b journey 07:32:30..07:35:50 reached -4.68 past the 5.0 fence, ws1r reversed 07:34:30 during, r 20.24 past the 44.0 fence, stamp 07:34:30, ib 15.0 cross 07:35:00 hold 6 bars, ib dwell 12 bars \| rider ws11 6.80, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:35:55 | BATON | ws11 | ws11 -> ws16, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 07:44:55 | LATCH1 | ws16 | latch 1 at the t1 cadence 2026-08-14 07:44:55, divergence state -1 |
| 2026-08-14 07:44:55 | CADENCE | ws16 | t1 gcws30b journey 07:39:30..07:44:50 reached 3.51 past the 5.0 fence, ws1r reversed 07:43:30 during, r 43.70 past the 44.0 fence, stamp 07:43:30, ib 15.0 cross 07:44:00 hold 6 bars, ib dwell 12 bars \| rider ws16 4.38, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:44:55 | BATON | ws16 | ws16 -> ws17, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:52:35 | BATON | ws17 | ws17 -> ws18, between cadences, lin_hop 2 |
| 2026-08-14 08:06:55 | BATON | ws18 | ws18 -> ws19, between cadences, lin_hop 2 |
| 2026-08-14 08:09:45 | BATON | ws19 | ws19 -> ws21, between cadences, lin_hop 2 |
| 2026-08-14 08:10:10 | BATON | ws21 | ws21 -> ws22, between cadences, lin_hop 2 |
| 2026-08-14 08:10:20 | NO PASS | ws22 | ws22 12.34 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:11:55 | LATCH1 | ws22 | latch 1 at the t1 cadence 2026-08-14 09:11:55, divergence state -1 |
| 2026-08-14 09:11:55 | CADENCE | ws22 | t1 gcws30b journey 09:05:00..09:11:50 reached 0.19 past the 5.0 fence, ws1r reversed 09:10:55 during, r 19.91 past the 44.0 fence, stamp 09:10:55, ib 15.0 cross 09:11:00 hold 6 bars, ib dwell 12 bars \| rider ws22 37.35, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:11:55 | BATON | ws22 | ws22 -> ws30, at a t1 cadence, capped at ws30 by the jump bound 8 |
| 2026-08-14 09:14:30 | NO PASS | ws30 | ws30 10.59 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:41:55 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:41:55, divergence state -1 |
| 2026-08-14 09:41:55 | CADENCE | ws30 | t1 gcws30b journey 09:32:00..09:41:50 reached 0.61 past the 5.0 fence, ws1r reversed 09:40:55 during, r 42.96 past the 44.0 fence, stamp 09:40:55, ib 15.0 cross 09:41:00 hold 6 bars, ib dwell 12 bars \| rider ws30 4.18, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 09:41:55 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 10:01:10 | NO PASS | ws30 | ws30 16.80 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:52:25 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 10:52:25, divergence state -1 |
| 2026-08-14 10:52:25 | CADENCE | ws30 | t1 gcws30b journey 10:47:00..10:52:20 reached -4.72 past the 5.0 fence, ws1r reversed 10:51:10 during, r 19.24 past the 44.0 fence, stamp 10:51:10, ib 15.0 cross 10:51:30 hold 6 bars, ib dwell 12 bars \| rider ws30 24.45, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 10:52:25 | TOP RESET | ws30 | ws30 24.45 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws4 |
| 2026-08-14 10:52:45 | NO PASS | ws4 | ws4 13.26 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 11:04:55 | LATCH1 | ws4 | latch 1 at the t1 cadence 2026-08-14 11:04:55, divergence state -1 |
| 2026-08-14 11:04:55 | CADENCE | ws4 | t1 gcws30b journey 10:56:00..11:04:50 reached -11.18 past the 5.0 fence, ws1r reversed 11:02:10 during, r 33.41 past the 44.0 fence, stamp 11:02:10, ib 15.0 cross 11:04:00 hold 6 bars, ib dwell 12 bars \| rider ws4 2.47, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 11:04:55 | BATON | ws4 | ws4 -> ws6, at a t1 cadence, capped at ws12 by the jump bound 8 |
| 2026-08-14 11:16:55 | LATCH1 | ws6 | latch 1 at the t1 cadence 2026-08-14 11:16:55, divergence state -1 |
| 2026-08-14 11:16:55 | CADENCE | ws6 | t1 gcws30b journey 11:12:00..11:16:50 reached -4.55 past the 5.0 fence, ws1r reversed 11:15:20 during, r 16.71 past the 44.0 fence, stamp 11:15:20, ib 15.0 cross 11:16:00 hold 6 bars, ib dwell 12 bars \| rider ws6 0.00, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 11:16:55 | BATON | ws6 | ws6 -> ws7, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-08-14 11:19:40 | NO PASS | ws7 | ws7 15.89 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:16:55 | LATCH1 | ws7 | latch 1 at the t1 cadence 2026-08-14 12:16:55, divergence state -1 |
| 2026-08-14 12:16:55 | CADENCE | ws7 | t1 gcws30b journey 12:09:30..12:16:50 reached -48.25 past the 5.0 fence, ws1r reversed 12:15:35 during, r 21.43 past the 44.0 fence, stamp 12:15:35, ib 15.0 cross 12:16:00 hold 6 bars, ib dwell 12 bars \| rider ws7 64.58, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:16:55 | EXHAUST | ws7 | t4 at a t1 cadence - rider ws7 64.58, no candidate at or below ws15 (the jump bound 8) |

## MODE 'reversal+quarter' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-08-14 06:59:00 | ARM | - | arm_at 2026-08-14 06:59:00 - the arm race is skipped, this bar IS the arm |
| 2026-08-14 06:59:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-08-14 06:59:00 | RETEST | - | ws1r 12.95 oob + ws2r 52.91 / ws3r 70.72 in - the gate opens; ws1r oob->ib cross 2026-08-14 07:02:10, wob 12, cadence at 2026-08-14 07:03:05 |
| 2026-08-14 07:03:05 | RIDER | ws8 | v4-arm-lineage-retest: the re-scan rides ws8 LATCHED, r 4.46 - the highest latched rung |
| 2026-08-14 07:03:25 | CADENCE | ws8 | t1 gcws30b journey 06:59:30..07:03:20 reached 1.38 past the 5.0 fence, ws1r reversed 07:02:10 during, r 14.93 past the 44.0 fence, stamp 07:02:10, ib 15.0 cross 07:02:30 hold 6 bars, ib dwell 12 bars \| rider ws8 4.46, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:03:25 | BATON | ws8 | ws8 -> ws10, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 07:04:55 | NO PASS | ws10 | ws10 8.51 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 07:13:55 | LATCH1 | ws10 | latch 1 at the t1 cadence 2026-08-14 07:13:55, divergence state -1 |
| 2026-08-14 07:13:55 | CADENCE | ws10 | t1 gcws30b journey 07:08:30..07:13:50 reached -40.53 past the 5.0 fence, ws1r reversed 07:13:15 during, r 37.66 past the 44.0 fence, stamp 07:13:15, ib 15.0 cross 07:13:00 hold 6 bars, ib dwell 12 bars \| rider ws10 0.40, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 07:13:55 | BATON | ws10 | ws10 -> ws11, at a t1 cadence, capped at ws18 by the jump bound 8 |
| 2026-08-14 07:35:55 | LATCH1 | ws11 | latch 1 at the t1 cadence 2026-08-14 07:35:55, divergence state -1 |
| 2026-08-14 07:35:55 | CADENCE | ws11 | t1 gcws30b journey 07:32:30..07:35:50 reached -4.68 past the 5.0 fence, ws1r reversed 07:34:30 during, r 20.24 past the 44.0 fence, stamp 07:34:30, ib 15.0 cross 07:35:00 hold 6 bars, ib dwell 12 bars \| rider ws11 6.80, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:35:55 | BATON | ws11 | ws11 -> ws16, at a t1 cadence, capped at ws19 by the jump bound 8 |
| 2026-08-14 07:44:55 | LATCH1 | ws16 | latch 1 at the t1 cadence 2026-08-14 07:44:55, divergence state -1 |
| 2026-08-14 07:44:55 | CADENCE | ws16 | t1 gcws30b journey 07:39:30..07:44:50 reached 3.51 past the 5.0 fence, ws1r reversed 07:43:30 during, r 43.70 past the 44.0 fence, stamp 07:43:30, ib 15.0 cross 07:44:00 hold 6 bars, ib dwell 12 bars \| rider ws16 4.38, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 07:44:55 | BATON | ws16 | ws16 -> ws17, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 07:55:55 | BATON | ws17 | ws17 -> ws19, between cadences, lin_hop 2 |
| 2026-08-14 08:13:35 | BATON | ws19 | ws19 -> ws21, between cadences, lin_hop 2 |
| 2026-08-14 08:14:30 | BATON | ws21 | ws21 -> ws22, between cadences, lin_hop 2 |
| 2026-08-14 08:14:55 | NO PASS | ws22 | ws22 9.02 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:11:55 | LATCH1 | ws22 | latch 1 at the t1 cadence 2026-08-14 09:11:55, divergence state -1 |
| 2026-08-14 09:11:55 | CADENCE | ws22 | t1 gcws30b journey 09:05:00..09:11:50 reached 0.19 past the 5.0 fence, ws1r reversed 09:10:55 during, r 19.91 past the 44.0 fence, stamp 09:10:55, ib 15.0 cross 09:11:00 hold 6 bars, ib dwell 12 bars \| rider ws22 37.35, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:11:55 | BATON | ws22 | ws22 -> ws30, at a t1 cadence, capped at ws30 by the jump bound 8 |
| 2026-08-14 09:21:05 | NO PASS | ws30 | ws30 6.12 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:41:55 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 09:41:55, divergence state -1 |
| 2026-08-14 09:41:55 | CADENCE | ws30 | t1 gcws30b journey 09:32:00..09:41:50 reached 0.61 past the 5.0 fence, ws1r reversed 09:40:55 during, r 42.96 past the 44.0 fence, stamp 09:40:55, ib 15.0 cross 09:41:00 hold 6 bars, ib dwell 12 bars \| rider ws30 4.18, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 09:41:55 | HOLD | ws30 | rider ws30 4.18 oob - no action |
| 2026-08-14 10:07:45 | NO PASS | ws30 | ws30 18.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:52:25 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 10:52:25, divergence state -1 |
| 2026-08-14 10:52:25 | CADENCE | ws30 | t1 gcws30b journey 10:47:00..10:52:20 reached -4.72 past the 5.0 fence, ws1r reversed 10:51:10 during, r 19.24 past the 44.0 fence, stamp 10:51:10, ib 15.0 cross 10:51:30 hold 6 bars, ib dwell 12 bars \| rider ws30 24.45, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 10:52:25 | TOP RESET | ws30 | ws30 24.45 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws4 |
| 2026-08-14 10:52:50 | NO PASS | ws4 | ws4 13.26 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 11:04:55 | LATCH1 | ws4 | latch 1 at the t1 cadence 2026-08-14 11:04:55, divergence state -1 |
| 2026-08-14 11:04:55 | CADENCE | ws4 | t1 gcws30b journey 10:56:00..11:04:50 reached -11.18 past the 5.0 fence, ws1r reversed 11:02:10 during, r 33.41 past the 44.0 fence, stamp 11:02:10, ib 15.0 cross 11:04:00 hold 6 bars, ib dwell 12 bars \| rider ws4 2.47, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 11:04:55 | BATON | ws4 | ws4 -> ws6, at a t1 cadence, capped at ws12 by the jump bound 8 |
| 2026-08-14 11:16:55 | LATCH1 | ws6 | latch 1 at the t1 cadence 2026-08-14 11:16:55, divergence state -1 |
| 2026-08-14 11:16:55 | CADENCE | ws6 | t1 gcws30b journey 11:12:00..11:16:50 reached -4.55 past the 5.0 fence, ws1r reversed 11:15:20 during, r 16.71 past the 44.0 fence, stamp 11:15:20, ib 15.0 cross 11:16:00 hold 6 bars, ib dwell 12 bars \| rider ws6 0.00, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 11:16:55 | BATON | ws6 | ws6 -> ws7, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-08-14 11:20:30 | BATON | ws7 | ws7 -> ws8, between cadences, lin_hop 2 |
| 2026-08-14 11:20:45 | NO PASS | ws8 | ws8 16.71 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:16:55 | LATCH1 | ws8 | latch 1 at the t1 cadence 2026-08-14 12:16:55, divergence state -1 |
| 2026-08-14 12:16:55 | CADENCE | ws8 | t1 gcws30b journey 12:09:30..12:16:50 reached -48.25 past the 5.0 fence, ws1r reversed 12:15:35 during, r 21.43 past the 44.0 fence, stamp 12:15:35, ib 15.0 cross 12:16:00 hold 6 bars, ib dwell 12 bars \| rider ws8 64.96, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 12:16:55 | BATON | ws8 | ws8 -> ws16, at a t1 cadence, capped at ws16 by the jump bound 8 |
| 2026-08-14 12:28:00 | BATON | ws16 | ws16 -> ws18, between cadences, lin_hop 2 |
| 2026-08-14 12:28:40 | NO PASS | ws18 | ws18 10.82 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 12:49:25 | CADENCE | ws18 | t1 gcws30b journey 12:46:00..12:49:20 reached -3.48 past the 5.0 fence, ws1r reversed 12:49:15 during, r 30.77 past the 44.0 fence, stamp 12:49:15, ib 15.0 cross 12:48:30 hold 6 bars, ib dwell 12 bars \| rider ws18 21.99, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 12:49:25 | BATON | ws18 | ws18 -> ws23, at a t1 cadence, capped at ws26 by the jump bound 8 |
| 2026-08-14 12:55:40 | NO PASS | ws23 | ws23 13.81 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 13:08:25 | LATCH1 | ws23 | latch 1 at the t1 cadence 2026-08-14 13:08:25, divergence state -1 |
| 2026-08-14 13:08:25 | CADENCE | ws23 | t1 gcws30b journey 13:06:30..13:08:20 reached 4.99 past the 5.0 fence, ws1r reversed 13:07:20 during, r 17.42 past the 44.0 fence, stamp 13:07:20, ib 15.0 cross 13:07:30 hold 6 bars, ib dwell 12 bars \| rider ws23 3.75, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 13:08:25 | BATON | ws23 | ws23 -> ws30, at a t1 cadence, capped at ws31 by the jump bound 8 - past the ws30 ladder top, so it does not bind |
| 2026-08-14 13:21:50 | NO PASS | ws30 | ws30 15.38 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 14:11:55 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-08-14 14:11:55, divergence state -1 |
| 2026-08-14 14:11:55 | CADENCE | ws30 | t1 gcws30b journey 14:02:00..14:11:50 reached -41.17 past the 5.0 fence, ws1r reversed 14:10:55 during, r 26.21 past the 44.0 fence, stamp 14:10:55, ib 15.0 cross 14:11:00 hold 6 bars, ib dwell 12 bars \| rider ws30 34.52, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 14:11:55 | TOP RESET | ws30 | ws30 34.52 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-08-14 14:14:55 | NO PASS | ws2 | ws2 17.00 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 15:00:25 | CADENCE | ws2 | t1 gcws30b journey 14:55:30..15:00:20 reached -6.24 past the 5.0 fence, ws1r reversed 14:57:45 during, r 11.61 past the 44.0 fence, stamp 14:57:45, ib 15.0 cross 14:59:30 hold 6 bars, ib dwell 12 bars \| rider ws2 4.55, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 15:00:25 | HOLD | ws2 | rider ws2 4.55 oob - no action |
| 2026-08-14 15:01:25 | NO PASS | ws2 | ws2 12.98 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 16:49:55 | LATCH1 | ws2 | latch 1 at the t1 cadence 2026-08-14 16:49:55, divergence state -1 |
| 2026-08-14 16:49:55 | CADENCE | ws2 | t1 gcws30b journey 16:46:30..16:49:50 reached -4.49 past the 5.0 fence, ws1r reversed 16:47:40 during, r 2.17 past the 44.0 fence, stamp 16:47:40, ib 15.0 cross 16:49:00 hold 6 bars, ib dwell 12 bars \| rider ws2 14.29, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 16:49:55 | BATON | ws2 | ws2 -> ws4, at a t1 cadence, capped at ws10 by the jump bound 8 |
| 2026-08-14 16:56:15 | BATON | ws4 | ws4 -> ws6, between cadences, lin_hop 2 |
| 2026-08-14 17:01:15 | NO PASS | ws6 | ws6 14.55 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 17:46:25 | LATCH1 | ws6 | latch 1 at the t1 cadence 2026-08-14 17:46:25, divergence state -1 |
| 2026-08-14 17:46:25 | CADENCE | ws6 | t1 gcws30b journey 17:44:00..17:46:20 reached -18.45 past the 5.0 fence, ws1r reversed 17:46:10 during, r 19.13 past the 44.0 fence, stamp 17:46:10, ib 15.0 cross 17:45:30 hold 6 bars, ib dwell 12 bars \| rider ws6 55.86, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 17:46:25 | BATON | ws6 | ws6 -> ws9, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-08-14 17:47:15 | NO PASS | ws9 | ws9 25.59 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 18:06:55 | LATCH1 | ws9 | latch 1 at the t1 cadence 2026-08-14 18:06:55, divergence state -1 |
| 2026-08-14 18:06:55 | CADENCE | ws9 | t1 gcws30b journey 17:50:30..18:06:50 reached -8.64 past the 5.0 fence, ws1r reversed 18:05:25 during, r 38.02 past the 44.0 fence, stamp 18:05:25, ib 15.0 cross 18:06:00 hold 6 bars, ib dwell 12 bars \| rider ws9 17.91, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-14 18:06:55 | BATON | ws9 | ws9 -> ws12, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-08-14 18:37:25 | LATCH1 | ws12 | latch 1 at the t1 cadence 2026-08-14 18:37:25, divergence state -1 |
| 2026-08-14 18:37:25 | CADENCE | ws12 | t1 gcws30b journey 18:31:30..18:37:20 reached -24.30 past the 5.0 fence, ws1r reversed 18:36:15 during, r 1.10 past the 44.0 fence, stamp 18:36:15, ib 15.0 cross 18:36:30 hold 6 bars, ib dwell 12 bars \| rider ws12 6.36, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-14 18:37:25 | BATON | ws12 | ws12 -> ws16, at a t1 cadence, capped at ws20 by the jump bound 8 |
| 2026-08-14 19:09:25 | CADENCE | ws16 | t1 gcws30b journey 18:59:00..19:09:20 reached -31.09 past the 5.0 fence, ws1r reversed 19:01:35 during, r 18.50 past the 44.0 fence, stamp 19:01:35, ib 15.0 cross 19:08:30 hold 6 bars, ib dwell 12 bars \| rider ws16 5.23, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-14 19:09:25 | BATON | ws16 | ws16 -> ws19, at a t1 cadence, capped at ws24 by the jump bound 8 |
| 2026-08-14 19:32:30 | BATON | ws19 | ws19 -> ws20, between cadences, lin_hop 2 |
| 2026-08-14 19:32:50 | BATON | ws20 | ws20 -> ws22, between cadences, lin_hop 2 |
| 2026-08-14 19:36:45 | NO PASS | ws22 | ws22 22.13 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 21:00:55 | CADENCE | ws22 | t1 gcws30b journey 20:56:30..21:00:50 reached -18.88 past the 5.0 fence, ws1r reversed 20:59:05 during, r 31.39 past the 44.0 fence, stamp 20:59:05, ib 15.0 cross 21:00:00 hold 6 bars, ib dwell 12 bars \| rider ws22 59.99, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 21:00:55 | EXHAUST | ws22 | t4 at a t1 cadence - rider ws22 59.99, no candidate at or below ws30 (the jump bound 8) |
