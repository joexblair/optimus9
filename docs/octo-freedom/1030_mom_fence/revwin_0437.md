# LINEAGE2 BATON CHAIN - THE ARM IS HANDED IN AT 2026-09-03 03:24:00, SIDE low
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
| 2026-09-03 03:24:00 | ARM | - | - | - | arm_at 2026-09-03 03:24:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 03:24:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 03:25:50 | RIDER | ws5 | - | - | t1 gcws30b oob 03:23:15..03:25:20, ws1r reversed 03:24:15 during, r 23.33 past the 44.0 fence, stamp 03:24:15, cross 03:25:25 hold 6 bars \| ws5 r 25.56 picked up at a cadence, no prior rider |
| 2026-09-03 03:30:50 | CADENCE | ws5 | - | ws6 16.84 | t1 gcws30b oob 03:29:35..03:30:20, ws1r reversed 03:30:20 during, r 34.95 past the 44.0 fence, stamp 03:30:20, cross 03:30:25 hold 6 bars \| rider ws5 13.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 03:30:50 | BATON | ws5 | ws6 | ws6 16.84 | ws5 -> ws6, at a t1 cadence, capped at ws13 by the jump bound 8 |
| 2026-09-03 03:39:15 | CADENCE | ws6 | - | ws7 11.57, ws8 22.86 | t1 gcws30b ib 03:37:20, ws1r reversed 03:39:15 inside the 120s grace from the cross bar 03:37:20, r 30.02 past the 44.0 fence, stamp 03:39:15, hold 6 bars \| rider ws6 2.14, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-09-03 03:39:15 | BATON | ws6 | ws8 | ws7 11.57, ws8 22.86 | ws6 -> ws8, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-09-03 03:39:30 | CADENCE | ws8 | - | none offered | t1 gcws30b ib 03:39:05, ws1r reversed 03:39:15 inside the 120s grace from the cross bar 03:39:05, r 30.02 past the 44.0 fence, stamp 03:39:15, hold 6 bars \| rider ws8 22.86, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 03:39:30 | HOLD | ws8 | - | - | rider ws8 22.86 ex-fence and not reversed - no action |
| 2026-09-03 03:49:35 | BATON | ws8 | ws9 | ws9 24.09 | ws8 -> ws9, between cadences, lin_hop 2 |
| 2026-09-03 04:03:45 | BATON | ws9 | ws10 | ws10 21.62 | ws9 -> ws10, between cadences, lin_hop 2 |
| 2026-09-03 04:22:55 | BATON | ws10 | ws12 | ws11 20.38, ws12 17.21 | ws10 -> ws12, between cadences, lin_hop 2 |
| 2026-09-03 04:37:55 | CADENCE | ws12 | - | ws13 15.72, ws14 21.45, ws15 16.31, ws16 14.34, ws17 15.56 | t1 gcws30b ib 04:37:30, ws1r reversed 04:37:45 inside the 120s grace from the cross bar 04:37:30, r 33.98 past the 44.0 fence, stamp 04:37:45, hold 6 bars \| rider ws12 13.56, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-09-03 04:37:55 | BATON | ws12 | ws17 | ws13 15.72, ws14 21.45, ws15 16.31, ws16 14.34, ws17 15.56 | ws12 -> ws17, at a t1 cadence, capped at ws20 by the jump bound 8 |
| 2026-09-03 05:32:35 | BATON | ws17 | ws18 | ws18 26.65 | ws17 -> ws18, between cadences, lin_hop 2 |
| 2026-09-03 07:04:35 | NO PASS | ws18 | - | none offered | ws18 70.62 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 07:33:00 | CADENCE | ws18 | - | none offered | t1 gcws30b oob 07:30:15..07:32:30, ws1r reversed 07:32:10 during, r 22.68 past the 44.0 fence, stamp 07:32:10, cross 07:32:35 hold 6 bars \| rider ws18 72.57, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-09-03 07:33:00 | EXHAUST | ws18 | - | - | t4 at a t1 cadence - rider ws18 72.57, no candidate at or below ws26 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-09-03 07:33:00 |
| baton passes made | 7 |
| minutes from the arm to the verdict | 249.0 |
| the rider chain | ws5 > ws6 > ws8 > ws9 > ws10 > ws12 > ws17 > ws18 |

## MODE 'reversal' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-09-03 03:24:00 | ARM | - | - | - | arm_at 2026-09-03 03:24:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 03:24:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 03:25:50 | RIDER | ws5 | - | - | t1 gcws30b oob 03:23:15..03:25:20, ws1r reversed 03:24:15 during, r 23.33 past the 44.0 fence, stamp 03:24:15, cross 03:25:25 hold 6 bars \| ws5 r 25.56 picked up at a cadence, no prior rider |
| 2026-09-03 03:30:50 | CADENCE | ws5 | - | ws6 16.84 | t1 gcws30b oob 03:29:35..03:30:20, ws1r reversed 03:30:20 during, r 34.95 past the 44.0 fence, stamp 03:30:20, cross 03:30:25 hold 6 bars \| rider ws5 13.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 03:30:50 | BATON | ws5 | ws6 | ws6 16.84 | ws5 -> ws6, at a t1 cadence, capped at ws13 by the jump bound 8 |
| 2026-09-03 03:33:05 | NO PASS | ws6 | - | none offered | ws6 20.68 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 03:39:15 | CADENCE | ws6 | - | ws7 11.57, ws8 22.86 | t1 gcws30b ib 03:37:20, ws1r reversed 03:39:15 inside the 120s grace from the cross bar 03:37:20, r 30.02 past the 44.0 fence, stamp 03:39:15, hold 6 bars \| rider ws6 2.14, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-09-03 03:39:15 | BATON | ws6 | ws8 | ws7 11.57, ws8 22.86 | ws6 -> ws8, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-09-03 03:39:30 | CADENCE | ws8 | - | none offered | t1 gcws30b ib 03:39:05, ws1r reversed 03:39:15 inside the 120s grace from the cross bar 03:39:05, r 30.02 past the 44.0 fence, stamp 03:39:15, hold 6 bars \| rider ws8 22.86, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 03:39:30 | HOLD | ws8 | - | - | rider ws8 22.86 ex-fence and not reversed - no action |
| 2026-09-03 03:49:55 | BATON | ws8 | ws9 | ws9 25.88 | ws8 -> ws9, between cadences, lin_hop 2 |
| 2026-09-03 03:50:10 | NO PASS | ws9 | - | none offered | ws9 25.53 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 04:37:55 | CADENCE | ws9 | - | ws10 15.79, ws12 13.56, ws13 15.72, ws14 21.45, ws15 16.31, ws16 14.34, ws17 15.56 | t1 gcws30b ib 04:37:30, ws1r reversed 04:37:45 inside the 120s grace from the cross bar 04:37:30, r 33.98 past the 44.0 fence, stamp 04:37:45, hold 6 bars \| rider ws9 30.74, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 04:37:55 | BATON | ws9 | ws17 | ws10 15.79, ws12 13.56, ws13 15.72, ws14 21.45, ws15 16.31, ws16 14.34, ws17 15.56 | ws9 -> ws17, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-09-03 04:47:50 | BATON | ws17 | ws19 | ws19 21.04 | ws17 -> ws19, between cadences, lin_hop 2 |
| 2026-09-03 04:50:20 | NO PASS | ws19 | - | none offered | ws19 22.26 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 07:33:00 | CADENCE | ws19 | - | none offered | t1 gcws30b oob 07:30:15..07:32:30, ws1r reversed 07:32:10 during, r 22.68 past the 44.0 fence, stamp 07:32:10, cross 07:32:35 hold 6 bars \| rider ws19 61.89, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-09-03 07:33:00 | EXHAUST | ws19 | - | - | t4 at a t1 cadence - rider ws19 61.89, no candidate at or below ws27 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-09-03 07:33:00 |
| baton passes made | 5 |
| minutes from the arm to the verdict | 249.0 |
| the rider chain | ws5 > ws6 > ws8 > ws9 > ws17 > ws19 |

## MODE 'reversal+quarter' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-09-03 03:24:00 | ARM | - | - | - | arm_at 2026-09-03 03:24:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 03:24:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 03:25:50 | RIDER | ws5 | - | - | t1 gcws30b oob 03:23:15..03:25:20, ws1r reversed 03:24:15 during, r 23.33 past the 44.0 fence, stamp 03:24:15, cross 03:25:25 hold 6 bars \| ws5 r 25.56 picked up at a cadence, no prior rider |
| 2026-09-03 03:30:50 | CADENCE | ws5 | - | ws6 16.84 | t1 gcws30b oob 03:29:35..03:30:20, ws1r reversed 03:30:20 during, r 34.95 past the 44.0 fence, stamp 03:30:20, cross 03:30:25 hold 6 bars \| rider ws5 13.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 03:30:50 | BATON | ws5 | ws6 | ws6 16.84 | ws5 -> ws6, at a t1 cadence, capped at ws13 by the jump bound 8 |
| 2026-09-03 03:33:40 | NO PASS | ws6 | - | none offered | ws6 21.43 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 03:39:15 | CADENCE | ws6 | - | ws7 11.57, ws8 22.86 | t1 gcws30b ib 03:37:20, ws1r reversed 03:39:15 inside the 120s grace from the cross bar 03:37:20, r 30.02 past the 44.0 fence, stamp 03:39:15, hold 6 bars \| rider ws6 2.14, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-09-03 03:39:15 | BATON | ws6 | ws8 | ws7 11.57, ws8 22.86 | ws6 -> ws8, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-09-03 03:39:30 | CADENCE | ws8 | - | none offered | t1 gcws30b ib 03:39:05, ws1r reversed 03:39:15 inside the 120s grace from the cross bar 03:39:05, r 30.02 past the 44.0 fence, stamp 03:39:15, hold 6 bars \| rider ws8 22.86, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 03:39:30 | HOLD | ws8 | - | - | rider ws8 22.86 ex-fence and not reversed - no action |
| 2026-09-03 03:51:00 | BATON | ws8 | ws9 | ws9 25.16 | ws8 -> ws9, between cadences, lin_hop 2 |
| 2026-09-03 03:51:30 | NO PASS | ws9 | - | none offered | ws9 25.03 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 04:37:55 | CADENCE | ws9 | - | ws10 15.79, ws12 13.56, ws13 15.72, ws14 21.45, ws15 16.31, ws16 14.34, ws17 15.56 | t1 gcws30b ib 04:37:30, ws1r reversed 04:37:45 inside the 120s grace from the cross bar 04:37:30, r 33.98 past the 44.0 fence, stamp 04:37:45, hold 6 bars \| rider ws9 30.74, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 04:37:55 | BATON | ws9 | ws17 | ws10 15.79, ws12 13.56, ws13 15.72, ws14 21.45, ws15 16.31, ws16 14.34, ws17 15.56 | ws9 -> ws17, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-09-03 04:51:10 | BATON | ws17 | ws19 | ws18 23.49, ws19 22.71 | ws17 -> ws19, between cadences, lin_hop 2 |
| 2026-09-03 04:54:10 | NO PASS | ws19 | - | none offered | ws19 27.55 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 07:33:00 | CADENCE | ws19 | - | none offered | t1 gcws30b oob 07:30:15..07:32:30, ws1r reversed 07:32:10 during, r 22.68 past the 44.0 fence, stamp 07:32:10, cross 07:32:35 hold 6 bars \| rider ws19 61.89, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-09-03 07:33:00 | EXHAUST | ws19 | - | - | t4 at a t1 cadence - rider ws19 61.89, no candidate at or below ws27 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-09-03 07:33:00 |
| baton passes made | 5 |
| minutes from the arm to the verdict | 249.0 |
| the rider chain | ws5 > ws6 > ws8 > ws9 > ws17 > ws19 |

## MODE 'ib' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 03:24:00 | ARM | - | arm_at 2026-09-03 03:24:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 03:24:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 03:24:00 | RETEST | - | ws1r 20.64 is not oob at the arm - the gate stays shut |
| 2026-09-03 03:25:50 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 03:25:50, divergence state -1 |
| 2026-09-03 03:25:50 | RIDER | ws5 | t1 gcws30b oob 03:23:15..03:25:20, ws1r reversed 03:24:15 during, r 23.33 past the 44.0 fence, stamp 03:24:15, cross 03:25:25 hold 6 bars \| ws5 r 25.56 picked up at a cadence, no prior rider |
| 2026-09-03 03:30:50 | LATCH1 | ws5 | latch 1 at the t1 cadence 2026-09-03 03:30:50, divergence state -1 |
| 2026-09-03 03:30:50 | CADENCE | ws5 | t1 gcws30b oob 03:29:35..03:30:20, ws1r reversed 03:30:20 during, r 34.95 past the 44.0 fence, stamp 03:30:20, cross 03:30:25 hold 6 bars \| rider ws5 13.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 03:30:50 | BATON | ws5 | ws5 -> ws6, at a t1 cadence, capped at ws13 by the jump bound 8 |
| 2026-09-03 03:39:15 | LATCH1 | ws6 | latch 1 at the t1 cadence 2026-09-03 03:39:15, divergence state -1 |
| 2026-09-03 03:39:15 | CADENCE | ws6 | t1 gcws30b ib 03:37:20, ws1r reversed 03:39:15 inside the 120s grace from the cross bar 03:37:20, r 30.02 past the 44.0 fence, stamp 03:39:15, hold 6 bars \| rider ws6 2.14, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-09-03 03:39:15 | BATON | ws6 | ws6 -> ws8, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-09-03 03:39:30 | LATCH1 | ws8 | latch 1 at the t1 cadence 2026-09-03 03:39:30, divergence state -1 |
| 2026-09-03 03:39:30 | CADENCE | ws8 | t1 gcws30b ib 03:39:05, ws1r reversed 03:39:15 inside the 120s grace from the cross bar 03:39:05, r 30.02 past the 44.0 fence, stamp 03:39:15, hold 6 bars \| rider ws8 22.86, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 03:39:30 | HOLD | ws8 | rider ws8 22.86 ex-fence and not reversed - no action |
| 2026-09-03 03:49:35 | BATON | ws8 | ws8 -> ws9, between cadences, lin_hop 2 |
| 2026-09-03 04:03:45 | BATON | ws9 | ws9 -> ws10, between cadences, lin_hop 2 |
| 2026-09-03 04:22:55 | BATON | ws10 | ws10 -> ws12, between cadences, lin_hop 2 |
| 2026-09-03 04:37:55 | LATCH1 | ws12 | latch 1 at the t1 cadence 2026-09-03 04:37:55, divergence state -1 |
| 2026-09-03 04:37:55 | CADENCE | ws12 | t1 gcws30b ib 04:37:30, ws1r reversed 04:37:45 inside the 120s grace from the cross bar 04:37:30, r 33.98 past the 44.0 fence, stamp 04:37:45, hold 6 bars \| rider ws12 13.56, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-09-03 04:37:55 | BATON | ws12 | ws12 -> ws17, at a t1 cadence, capped at ws20 by the jump bound 8 |
| 2026-09-03 05:32:35 | BATON | ws17 | ws17 -> ws18, between cadences, lin_hop 2 |
| 2026-09-03 07:04:35 | NO PASS | ws18 | ws18 70.62 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 07:33:00 | CADENCE | ws18 | t1 gcws30b oob 07:30:15..07:32:30, ws1r reversed 07:32:10 during, r 22.68 past the 44.0 fence, stamp 07:32:10, cross 07:32:35 hold 6 bars \| rider ws18 72.57, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-09-03 07:33:00 | EXHAUST | ws18 | t4 at a t1 cadence - rider ws18 72.57, no candidate at or below ws26 (the jump bound 8) |

## MODE 'reversal' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 03:24:00 | ARM | - | arm_at 2026-09-03 03:24:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 03:24:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 03:24:00 | RETEST | - | ws1r 20.64 is not oob at the arm - the gate stays shut |
| 2026-09-03 03:25:50 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 03:25:50, divergence state -1 |
| 2026-09-03 03:25:50 | RIDER | ws5 | t1 gcws30b oob 03:23:15..03:25:20, ws1r reversed 03:24:15 during, r 23.33 past the 44.0 fence, stamp 03:24:15, cross 03:25:25 hold 6 bars \| ws5 r 25.56 picked up at a cadence, no prior rider |
| 2026-09-03 03:30:50 | LATCH1 | ws5 | latch 1 at the t1 cadence 2026-09-03 03:30:50, divergence state -1 |
| 2026-09-03 03:30:50 | CADENCE | ws5 | t1 gcws30b oob 03:29:35..03:30:20, ws1r reversed 03:30:20 during, r 34.95 past the 44.0 fence, stamp 03:30:20, cross 03:30:25 hold 6 bars \| rider ws5 13.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 03:30:50 | BATON | ws5 | ws5 -> ws6, at a t1 cadence, capped at ws13 by the jump bound 8 |
| 2026-09-03 03:33:05 | NO PASS | ws6 | ws6 20.68 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 03:39:15 | LATCH1 | ws6 | latch 1 at the t1 cadence 2026-09-03 03:39:15, divergence state -1 |
| 2026-09-03 03:39:15 | CADENCE | ws6 | t1 gcws30b ib 03:37:20, ws1r reversed 03:39:15 inside the 120s grace from the cross bar 03:37:20, r 30.02 past the 44.0 fence, stamp 03:39:15, hold 6 bars \| rider ws6 2.14, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-09-03 03:39:15 | BATON | ws6 | ws6 -> ws8, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-09-03 03:39:30 | LATCH1 | ws8 | latch 1 at the t1 cadence 2026-09-03 03:39:30, divergence state -1 |
| 2026-09-03 03:39:30 | CADENCE | ws8 | t1 gcws30b ib 03:39:05, ws1r reversed 03:39:15 inside the 120s grace from the cross bar 03:39:05, r 30.02 past the 44.0 fence, stamp 03:39:15, hold 6 bars \| rider ws8 22.86, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 03:39:30 | HOLD | ws8 | rider ws8 22.86 ex-fence and not reversed - no action |
| 2026-09-03 03:49:55 | BATON | ws8 | ws8 -> ws9, between cadences, lin_hop 2 |
| 2026-09-03 03:50:10 | NO PASS | ws9 | ws9 25.53 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 04:37:55 | LATCH1 | ws9 | latch 1 at the t1 cadence 2026-09-03 04:37:55, divergence state -1 |
| 2026-09-03 04:37:55 | CADENCE | ws9 | t1 gcws30b ib 04:37:30, ws1r reversed 04:37:45 inside the 120s grace from the cross bar 04:37:30, r 33.98 past the 44.0 fence, stamp 04:37:45, hold 6 bars \| rider ws9 30.74, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 04:37:55 | BATON | ws9 | ws9 -> ws17, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-09-03 04:47:50 | BATON | ws17 | ws17 -> ws19, between cadences, lin_hop 2 |
| 2026-09-03 04:50:20 | NO PASS | ws19 | ws19 22.26 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 07:33:00 | CADENCE | ws19 | t1 gcws30b oob 07:30:15..07:32:30, ws1r reversed 07:32:10 during, r 22.68 past the 44.0 fence, stamp 07:32:10, cross 07:32:35 hold 6 bars \| rider ws19 61.89, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-09-03 07:33:00 | EXHAUST | ws19 | t4 at a t1 cadence - rider ws19 61.89, no candidate at or below ws27 (the jump bound 8) |

## MODE 'reversal+quarter' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 03:24:00 | ARM | - | arm_at 2026-09-03 03:24:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 03:24:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 03:24:00 | RETEST | - | ws1r 20.64 is not oob at the arm - the gate stays shut |
| 2026-09-03 03:25:50 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 03:25:50, divergence state -1 |
| 2026-09-03 03:25:50 | RIDER | ws5 | t1 gcws30b oob 03:23:15..03:25:20, ws1r reversed 03:24:15 during, r 23.33 past the 44.0 fence, stamp 03:24:15, cross 03:25:25 hold 6 bars \| ws5 r 25.56 picked up at a cadence, no prior rider |
| 2026-09-03 03:30:50 | LATCH1 | ws5 | latch 1 at the t1 cadence 2026-09-03 03:30:50, divergence state -1 |
| 2026-09-03 03:30:50 | CADENCE | ws5 | t1 gcws30b oob 03:29:35..03:30:20, ws1r reversed 03:30:20 during, r 34.95 past the 44.0 fence, stamp 03:30:20, cross 03:30:25 hold 6 bars \| rider ws5 13.61, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 03:30:50 | BATON | ws5 | ws5 -> ws6, at a t1 cadence, capped at ws13 by the jump bound 8 |
| 2026-09-03 03:33:40 | NO PASS | ws6 | ws6 21.43 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 03:39:15 | LATCH1 | ws6 | latch 1 at the t1 cadence 2026-09-03 03:39:15, divergence state -1 |
| 2026-09-03 03:39:15 | CADENCE | ws6 | t1 gcws30b ib 03:37:20, ws1r reversed 03:39:15 inside the 120s grace from the cross bar 03:37:20, r 30.02 past the 44.0 fence, stamp 03:39:15, hold 6 bars \| rider ws6 2.14, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-09-03 03:39:15 | BATON | ws6 | ws6 -> ws8, at a t1 cadence, capped at ws14 by the jump bound 8 |
| 2026-09-03 03:39:30 | LATCH1 | ws8 | latch 1 at the t1 cadence 2026-09-03 03:39:30, divergence state -1 |
| 2026-09-03 03:39:30 | CADENCE | ws8 | t1 gcws30b ib 03:39:05, ws1r reversed 03:39:15 inside the 120s grace from the cross bar 03:39:05, r 30.02 past the 44.0 fence, stamp 03:39:15, hold 6 bars \| rider ws8 22.86, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 03:39:30 | HOLD | ws8 | rider ws8 22.86 ex-fence and not reversed - no action |
| 2026-09-03 03:51:00 | BATON | ws8 | ws8 -> ws9, between cadences, lin_hop 2 |
| 2026-09-03 03:51:30 | NO PASS | ws9 | ws9 25.03 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 04:37:55 | LATCH1 | ws9 | latch 1 at the t1 cadence 2026-09-03 04:37:55, divergence state -1 |
| 2026-09-03 04:37:55 | CADENCE | ws9 | t1 gcws30b ib 04:37:30, ws1r reversed 04:37:45 inside the 120s grace from the cross bar 04:37:30, r 33.98 past the 44.0 fence, stamp 04:37:45, hold 6 bars \| rider ws9 30.74, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 04:37:55 | BATON | ws9 | ws9 -> ws17, at a t1 cadence, capped at ws17 by the jump bound 8 |
| 2026-09-03 04:51:10 | BATON | ws17 | ws17 -> ws19, between cadences, lin_hop 2 |
| 2026-09-03 04:54:10 | NO PASS | ws19 | ws19 27.55 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 07:33:00 | CADENCE | ws19 | t1 gcws30b oob 07:30:15..07:32:30, ws1r reversed 07:32:10 during, r 22.68 past the 44.0 fence, stamp 07:32:10, cross 07:32:35 hold 6 bars \| rider ws19 61.89, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-09-03 07:33:00 | EXHAUST | ws19 | t4 at a t1 cadence - rider ws19 61.89, no candidate at or below ws27 (the jump bound 8) |

## every low-side reversal of ws5 r .. ws10 r, 2026-09-03 04:32:55 .. 2026-09-03 04:47:55 - HIS WINDOW, the 2026-09-03 04:37:55 cadence minus 5 min to plus 10 min

| the reversal raw bar | the rung | its value at the raw bar | min from the cadence | the stamp, raw + 11 bars | its value at the stamp |
|---|---|---|---|---|---|
| 2026-09-03 04:37:20 | ws5 | 27.77 | -0.6 | 2026-09-03 04:38:15 | 31.51 |
| 2026-09-03 04:38:00 | ws6 | 39.18 | +0.1 | 2026-09-03 04:38:55 | 40.31 |
| 2026-09-03 04:44:05 | ws5 | 34.06 | +6.2 | 2026-09-03 04:45:00 | 48.14 |
| 2026-09-03 04:44:05 | ws8 | 36.60 | +6.2 | 2026-09-03 04:45:00 | 38.96 |
| 2026-09-03 04:44:10 | ws10 | 18.17 | +6.2 | 2026-09-03 04:45:05 | 22.57 |
| 2026-09-03 04:44:15 | ws7 | 33.59 | +6.3 | 2026-09-03 04:45:10 | 35.98 |
| 2026-09-03 04:44:35 | ws6 | 35.60 | +6.7 | 2026-09-03 04:45:30 | 37.39 |
| 2026-09-03 04:44:35 | ws9 | 31.67 | +6.7 | 2026-09-03 04:45:30 | 34.11 |

| the rung | reversals in the window | before the cadence | at or after it |
|---|---|---|---|
| ws5 | 2 | 1 | 1 |
| ws6 | 2 | 0 | 2 |
| ws7 | 1 | 0 | 1 |
| ws8 | 1 | 0 | 1 |
| ws9 | 1 | 0 | 1 |
| ws10 | 1 | 0 | 1 |
