# LINEAGE2 BATON CHAIN - THE ARM IS HANDED IN AT 2026-09-03 00:36:00, SIDE high
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
| 2026-09-03 00:36:00 | ARM | - | - | - | arm_at 2026-09-03 00:36:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 00:36:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 01:36:55 | RIDER | ws6 | - | - | t1 gcws30b journey 01:32:00..01:36:50 reached 125.44 past the 95.0 fence, ws1r reversed 01:36:00 during, r 69.64 past the 56.0 fence, stamp 01:36:00, ib 85.0 cross 01:36:00 hold 6 bars, ib dwell 12 bars \| ws6 r 90.51 picked up at a cadence, no prior rider |
| 2026-09-03 01:47:00 | BATON | ws6 | ws7 | ws7 87.00 | ws6 -> ws7, between cadences, lin_hop 2 |
| 2026-09-03 01:48:05 | NO PASS | ws7 | - | none offered | ws7 84.75 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 02:37:25 | CADENCE | ws7 | - | none offered | t1 gcws30b journey 02:31:00..02:37:20 reached 116.55 past the 95.0 fence, ws1r reversed 02:36:00 during, r 68.60 past the 56.0 fence, stamp 02:36:00, ib 85.0 cross 02:36:30 hold 6 bars, ib dwell 12 bars \| rider ws7 54.88, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 02:37:25 | EXHAUST | ws7 | - | - | t4 at a t1 cadence - rider ws7 54.88, no candidate at or below ws15 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-09-03 02:37:25 |
| baton passes made | 1 |
| minutes from the arm to the verdict | 121.4 |
| the rider chain | ws6 > ws7 |

## MODE 'reversal' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-09-03 00:36:00 | ARM | - | - | - | arm_at 2026-09-03 00:36:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 00:36:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 01:36:55 | RIDER | ws6 | - | - | t1 gcws30b journey 01:32:00..01:36:50 reached 125.44 past the 95.0 fence, ws1r reversed 01:36:00 during, r 69.64 past the 56.0 fence, stamp 01:36:00, ib 85.0 cross 01:36:00 hold 6 bars, ib dwell 12 bars \| ws6 r 90.51 picked up at a cadence, no prior rider |
| 2026-09-03 01:44:00 | BATON | ws6 | ws7 | ws7 89.83 | ws6 -> ws7, between cadences, lin_hop 2 |
| 2026-09-03 01:47:05 | NO PASS | ws7 | - | none offered | ws7 86.83 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 02:37:25 | CADENCE | ws7 | - | none offered | t1 gcws30b journey 02:31:00..02:37:20 reached 116.55 past the 95.0 fence, ws1r reversed 02:36:00 during, r 68.60 past the 56.0 fence, stamp 02:36:00, ib 85.0 cross 02:36:30 hold 6 bars, ib dwell 12 bars \| rider ws7 54.88, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 02:37:25 | EXHAUST | ws7 | - | - | t4 at a t1 cadence - rider ws7 54.88, no candidate at or below ws15 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-09-03 02:37:25 |
| baton passes made | 1 |
| minutes from the arm to the verdict | 121.4 |
| the rider chain | ws6 > ws7 |

## MODE 'reversal+quarter' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-09-03 00:36:00 | ARM | - | - | - | arm_at 2026-09-03 00:36:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 00:36:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 01:36:55 | RIDER | ws6 | - | - | t1 gcws30b journey 01:32:00..01:36:50 reached 125.44 past the 95.0 fence, ws1r reversed 01:36:00 during, r 69.64 past the 56.0 fence, stamp 01:36:00, ib 85.0 cross 01:36:00 hold 6 bars, ib dwell 12 bars \| ws6 r 90.51 picked up at a cadence, no prior rider |
| 2026-09-03 01:44:35 | BATON | ws6 | ws7 | ws7 89.83 | ws6 -> ws7, between cadences, lin_hop 2 |
| 2026-09-03 01:47:55 | NO PASS | ws7 | - | none offered | ws7 82.72 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 02:37:25 | CADENCE | ws7 | - | none offered | t1 gcws30b journey 02:31:00..02:37:20 reached 116.55 past the 95.0 fence, ws1r reversed 02:36:00 during, r 68.60 past the 56.0 fence, stamp 02:36:00, ib 85.0 cross 02:36:30 hold 6 bars, ib dwell 12 bars \| rider ws7 54.88, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 02:37:25 | EXHAUST | ws7 | - | - | t4 at a t1 cadence - rider ws7 54.88, no candidate at or below ws15 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-09-03 02:37:25 |
| baton passes made | 1 |
| minutes from the arm to the verdict | 121.4 |
| the rider chain | ws6 > ws7 |

## MODE 'ib' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 00:36:00 | ARM | - | arm_at 2026-09-03 00:36:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 00:36:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 00:36:00 | RETEST | - | ws1r 32.65 is not oob at the arm - the gate stays shut |
| 2026-09-03 01:36:55 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 01:36:55, divergence state +1 |
| 2026-09-03 01:36:55 | RIDER | ws6 | t1 gcws30b journey 01:32:00..01:36:50 reached 125.44 past the 95.0 fence, ws1r reversed 01:36:00 during, r 69.64 past the 56.0 fence, stamp 01:36:00, ib 85.0 cross 01:36:00 hold 6 bars, ib dwell 12 bars \| ws6 r 90.51 picked up at a cadence, no prior rider |
| 2026-09-03 01:47:00 | BATON | ws6 | ws6 -> ws7, between cadences, lin_hop 2 |
| 2026-09-03 01:48:05 | NO PASS | ws7 | ws7 84.75 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 02:37:25 | LATCH1 | ws7 | latch 1 at the t1 cadence 2026-09-03 02:37:25, divergence state +1 |
| 2026-09-03 02:37:25 | CADENCE | ws7 | t1 gcws30b journey 02:31:00..02:37:20 reached 116.55 past the 95.0 fence, ws1r reversed 02:36:00 during, r 68.60 past the 56.0 fence, stamp 02:36:00, ib 85.0 cross 02:36:30 hold 6 bars, ib dwell 12 bars \| rider ws7 54.88, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 02:37:25 | EXHAUST | ws7 | t4 at a t1 cadence - rider ws7 54.88, no candidate at or below ws15 (the jump bound 8) |

## MODE 'reversal' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 00:36:00 | ARM | - | arm_at 2026-09-03 00:36:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 00:36:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 00:36:00 | RETEST | - | ws1r 32.65 is not oob at the arm - the gate stays shut |
| 2026-09-03 01:36:55 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 01:36:55, divergence state +1 |
| 2026-09-03 01:36:55 | RIDER | ws6 | t1 gcws30b journey 01:32:00..01:36:50 reached 125.44 past the 95.0 fence, ws1r reversed 01:36:00 during, r 69.64 past the 56.0 fence, stamp 01:36:00, ib 85.0 cross 01:36:00 hold 6 bars, ib dwell 12 bars \| ws6 r 90.51 picked up at a cadence, no prior rider |
| 2026-09-03 01:44:00 | BATON | ws6 | ws6 -> ws7, between cadences, lin_hop 2 |
| 2026-09-03 01:47:05 | NO PASS | ws7 | ws7 86.83 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 02:37:25 | LATCH1 | ws7 | latch 1 at the t1 cadence 2026-09-03 02:37:25, divergence state +1 |
| 2026-09-03 02:37:25 | CADENCE | ws7 | t1 gcws30b journey 02:31:00..02:37:20 reached 116.55 past the 95.0 fence, ws1r reversed 02:36:00 during, r 68.60 past the 56.0 fence, stamp 02:36:00, ib 85.0 cross 02:36:30 hold 6 bars, ib dwell 12 bars \| rider ws7 54.88, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 02:37:25 | EXHAUST | ws7 | t4 at a t1 cadence - rider ws7 54.88, no candidate at or below ws15 (the jump bound 8) |

## MODE 'reversal+quarter' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 00:36:00 | ARM | - | arm_at 2026-09-03 00:36:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 00:36:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 00:36:00 | RETEST | - | ws1r 32.65 is not oob at the arm - the gate stays shut |
| 2026-09-03 01:36:55 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 01:36:55, divergence state +1 |
| 2026-09-03 01:36:55 | RIDER | ws6 | t1 gcws30b journey 01:32:00..01:36:50 reached 125.44 past the 95.0 fence, ws1r reversed 01:36:00 during, r 69.64 past the 56.0 fence, stamp 01:36:00, ib 85.0 cross 01:36:00 hold 6 bars, ib dwell 12 bars \| ws6 r 90.51 picked up at a cadence, no prior rider |
| 2026-09-03 01:44:35 | BATON | ws6 | ws6 -> ws7, between cadences, lin_hop 2 |
| 2026-09-03 01:47:55 | NO PASS | ws7 | ws7 82.72 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 02:37:25 | LATCH1 | ws7 | latch 1 at the t1 cadence 2026-09-03 02:37:25, divergence state +1 |
| 2026-09-03 02:37:25 | CADENCE | ws7 | t1 gcws30b journey 02:31:00..02:37:20 reached 116.55 past the 95.0 fence, ws1r reversed 02:36:00 during, r 68.60 past the 56.0 fence, stamp 02:36:00, ib 85.0 cross 02:36:30 hold 6 bars, ib dwell 12 bars \| rider ws7 54.88, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 02:37:25 | EXHAUST | ws7 | t4 at a t1 cadence - rider ws7 54.88, no candidate at or below ws15 (the jump bound 8) |
