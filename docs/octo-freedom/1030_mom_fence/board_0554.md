# LINEAGE2 BATON CHAIN - THE ARM IS HANDED IN AT 2026-09-03 04:39:00, SIDE high
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
| 2026-09-03 04:39:00 | ARM | - | - | - | arm_at 2026-09-03 04:39:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 04:39:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 05:02:55 | RIDER | ws3 | - | - | t1 gcws30b journey 04:51:30..05:02:50 reached 101.31 past the 95.0 fence, ws1r reversed 04:58:00 during, r 84.08 past the 56.0 fence, stamp 04:58:00, ib 85.0 cross 05:02:00 hold 6 bars, ib dwell 12 bars \| ws3 r 95.43 picked up at a cadence, no prior rider |
| 2026-09-03 05:06:55 | BATON | ws3 | ws5 | ws4 84.76, ws5 89.22 | ws3 -> ws5, between cadences, lin_hop 2 |
| 2026-09-03 05:10:55 | NO PASS | ws5 | - | none offered | ws5 82.92 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 05:54:25 | CADENCE | ws5 | - | none offered | t1 gcws30b journey 05:50:00..05:54:20 reached 97.04 past the 95.0 fence, ws1r reversed 05:54:00 during, r 87.12 past the 56.0 fence, stamp 05:54:00, ib 85.0 cross 05:53:30 hold 6 bars, ib dwell 12 bars \| rider ws5 58.61, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 05:54:25 | EXHAUST | ws5 | - | - | t4 at a t1 cadence - rider ws5 58.61, no candidate at or below ws13 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-09-03 05:54:25 |
| baton passes made | 1 |
| minutes from the arm to the verdict | 75.4 |
| the rider chain | ws3 > ws5 |

## MODE 'reversal' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-09-03 04:39:00 | ARM | - | - | - | arm_at 2026-09-03 04:39:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 04:39:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 05:02:55 | RIDER | ws3 | - | - | t1 gcws30b journey 04:51:30..05:02:50 reached 101.31 past the 95.0 fence, ws1r reversed 04:58:00 during, r 84.08 past the 56.0 fence, stamp 04:58:00, ib 85.0 cross 05:02:00 hold 6 bars, ib dwell 12 bars \| ws3 r 95.43 picked up at a cadence, no prior rider |
| 2026-09-03 05:03:50 | NO PASS | ws3 | - | none offered | ws3 95.38 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 05:54:25 | CADENCE | ws3 | - | none offered | t1 gcws30b journey 05:50:00..05:54:20 reached 97.04 past the 95.0 fence, ws1r reversed 05:54:00 during, r 87.12 past the 56.0 fence, stamp 05:54:00, ib 85.0 cross 05:53:30 hold 6 bars, ib dwell 12 bars \| rider ws3 96.36, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-09-03 05:54:25 | HOLD | ws3 | - | - | rider ws3 96.36 oob - no action |
| 2026-09-03 06:01:00 | BATON | ws3 | ws4 | ws4 89.10 | ws3 -> ws4, between cadences, lin_hop 2 |
| 2026-09-03 06:25:00 | NO PASS | ws4 | - | none offered | ws4 28.92 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 06:25:55 | CADENCE | ws4 | - | none offered | t1 gcws30b journey 06:24:00..06:25:50 reached 95.90 past the 95.0 fence, ws1r reversed 06:24:35 during, r 56.94 past the 56.0 fence, stamp 06:24:35, ib 85.0 cross 06:25:00 hold 6 bars, ib dwell 12 bars \| rider ws4 35.84, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 06:25:55 | EXHAUST | ws4 | - | - | t4 at a t1 cadence - rider ws4 35.84, no candidate at or below ws12 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-09-03 06:25:55 |
| baton passes made | 1 |
| minutes from the arm to the verdict | 106.9 |
| the rider chain | ws3 > ws4 |

## MODE 'reversal+quarter' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-09-03 04:39:00 | ARM | - | - | - | arm_at 2026-09-03 04:39:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 04:39:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 05:02:55 | RIDER | ws3 | - | - | t1 gcws30b journey 04:51:30..05:02:50 reached 101.31 past the 95.0 fence, ws1r reversed 04:58:00 during, r 84.08 past the 56.0 fence, stamp 04:58:00, ib 85.0 cross 05:02:00 hold 6 bars, ib dwell 12 bars \| ws3 r 95.43 picked up at a cadence, no prior rider |
| 2026-09-03 05:03:50 | NO PASS | ws3 | - | none offered | ws3 95.38 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 05:54:25 | CADENCE | ws3 | - | none offered | t1 gcws30b journey 05:50:00..05:54:20 reached 97.04 past the 95.0 fence, ws1r reversed 05:54:00 during, r 87.12 past the 56.0 fence, stamp 05:54:00, ib 85.0 cross 05:53:30 hold 6 bars, ib dwell 12 bars \| rider ws3 96.36, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-09-03 05:54:25 | HOLD | ws3 | - | - | rider ws3 96.36 oob - no action |
| 2026-09-03 06:01:00 | BATON | ws3 | ws4 | ws4 89.10 | ws3 -> ws4, between cadences, lin_hop 2 |
| 2026-09-03 06:01:05 | NO PASS | ws4 | - | none offered | ws4 88.85 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 06:25:55 | CADENCE | ws4 | - | none offered | t1 gcws30b journey 06:24:00..06:25:50 reached 95.90 past the 95.0 fence, ws1r reversed 06:24:35 during, r 56.94 past the 56.0 fence, stamp 06:24:35, ib 85.0 cross 06:25:00 hold 6 bars, ib dwell 12 bars \| rider ws4 35.84, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 06:25:55 | EXHAUST | ws4 | - | - | t4 at a t1 cadence - rider ws4 35.84, no candidate at or below ws12 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-09-03 06:25:55 |
| baton passes made | 1 |
| minutes from the arm to the verdict | 106.9 |
| the rider chain | ws3 > ws4 |

## MODE 'ib' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 04:39:00 | ARM | - | arm_at 2026-09-03 04:39:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 04:39:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 04:39:00 | RETEST | - | ws1r 38.47 is not oob at the arm - the gate stays shut |
| 2026-09-03 05:02:55 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 05:02:55, divergence state +1 |
| 2026-09-03 05:02:55 | RIDER | ws3 | t1 gcws30b journey 04:51:30..05:02:50 reached 101.31 past the 95.0 fence, ws1r reversed 04:58:00 during, r 84.08 past the 56.0 fence, stamp 04:58:00, ib 85.0 cross 05:02:00 hold 6 bars, ib dwell 12 bars \| ws3 r 95.43 picked up at a cadence, no prior rider |
| 2026-09-03 05:06:55 | BATON | ws3 | ws3 -> ws5, between cadences, lin_hop 2 |
| 2026-09-03 05:10:55 | NO PASS | ws5 | ws5 82.92 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 05:54:25 | LATCH1 | ws5 | latch 1 at the t1 cadence 2026-09-03 05:54:25, divergence state +1 |
| 2026-09-03 05:54:25 | CADENCE | ws5 | t1 gcws30b journey 05:50:00..05:54:20 reached 97.04 past the 95.0 fence, ws1r reversed 05:54:00 during, r 87.12 past the 56.0 fence, stamp 05:54:00, ib 85.0 cross 05:53:30 hold 6 bars, ib dwell 12 bars \| rider ws5 58.61, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 05:54:25 | EXHAUST | ws5 | t4 at a t1 cadence - rider ws5 58.61, no candidate at or below ws13 (the jump bound 8) |

## MODE 'reversal' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 04:39:00 | ARM | - | arm_at 2026-09-03 04:39:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 04:39:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 04:39:00 | RETEST | - | ws1r 38.47 is not oob at the arm - the gate stays shut |
| 2026-09-03 05:02:55 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 05:02:55, divergence state +1 |
| 2026-09-03 05:02:55 | RIDER | ws3 | t1 gcws30b journey 04:51:30..05:02:50 reached 101.31 past the 95.0 fence, ws1r reversed 04:58:00 during, r 84.08 past the 56.0 fence, stamp 04:58:00, ib 85.0 cross 05:02:00 hold 6 bars, ib dwell 12 bars \| ws3 r 95.43 picked up at a cadence, no prior rider |
| 2026-09-03 05:03:50 | NO PASS | ws3 | ws3 95.38 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 05:54:25 | LATCH1 | ws3 | latch 1 at the t1 cadence 2026-09-03 05:54:25, divergence state +1 |
| 2026-09-03 05:54:25 | CADENCE | ws3 | t1 gcws30b journey 05:50:00..05:54:20 reached 97.04 past the 95.0 fence, ws1r reversed 05:54:00 during, r 87.12 past the 56.0 fence, stamp 05:54:00, ib 85.0 cross 05:53:30 hold 6 bars, ib dwell 12 bars \| rider ws3 96.36, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-09-03 05:54:25 | HOLD | ws3 | rider ws3 96.36 oob - no action |
| 2026-09-03 06:01:00 | BATON | ws3 | ws3 -> ws4, between cadences, lin_hop 2 |
| 2026-09-03 06:25:00 | NO PASS | ws4 | ws4 28.92 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 06:25:55 | LATCH1 | ws4 | latch 1 at the t1 cadence 2026-09-03 06:25:55, divergence state +1 |
| 2026-09-03 06:25:55 | CADENCE | ws4 | t1 gcws30b journey 06:24:00..06:25:50 reached 95.90 past the 95.0 fence, ws1r reversed 06:24:35 during, r 56.94 past the 56.0 fence, stamp 06:24:35, ib 85.0 cross 06:25:00 hold 6 bars, ib dwell 12 bars \| rider ws4 35.84, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 06:25:55 | EXHAUST | ws4 | t4 at a t1 cadence - rider ws4 35.84, no candidate at or below ws12 (the jump bound 8) |

## MODE 'reversal+quarter' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 04:39:00 | ARM | - | arm_at 2026-09-03 04:39:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 04:39:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 04:39:00 | RETEST | - | ws1r 38.47 is not oob at the arm - the gate stays shut |
| 2026-09-03 05:02:55 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 05:02:55, divergence state +1 |
| 2026-09-03 05:02:55 | RIDER | ws3 | t1 gcws30b journey 04:51:30..05:02:50 reached 101.31 past the 95.0 fence, ws1r reversed 04:58:00 during, r 84.08 past the 56.0 fence, stamp 04:58:00, ib 85.0 cross 05:02:00 hold 6 bars, ib dwell 12 bars \| ws3 r 95.43 picked up at a cadence, no prior rider |
| 2026-09-03 05:03:50 | NO PASS | ws3 | ws3 95.38 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 05:54:25 | LATCH1 | ws3 | latch 1 at the t1 cadence 2026-09-03 05:54:25, divergence state +1 |
| 2026-09-03 05:54:25 | CADENCE | ws3 | t1 gcws30b journey 05:50:00..05:54:20 reached 97.04 past the 95.0 fence, ws1r reversed 05:54:00 during, r 87.12 past the 56.0 fence, stamp 05:54:00, ib 85.0 cross 05:53:30 hold 6 bars, ib dwell 12 bars \| rider ws3 96.36, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-09-03 05:54:25 | HOLD | ws3 | rider ws3 96.36 oob - no action |
| 2026-09-03 06:01:00 | BATON | ws3 | ws3 -> ws4, between cadences, lin_hop 2 |
| 2026-09-03 06:01:05 | NO PASS | ws4 | ws4 88.85 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 06:25:55 | LATCH1 | ws4 | latch 1 at the t1 cadence 2026-09-03 06:25:55, divergence state +1 |
| 2026-09-03 06:25:55 | CADENCE | ws4 | t1 gcws30b journey 06:24:00..06:25:50 reached 95.90 past the 95.0 fence, ws1r reversed 06:24:35 during, r 56.94 past the 56.0 fence, stamp 06:24:35, ib 85.0 cross 06:25:00 hold 6 bars, ib dwell 12 bars \| rider ws4 35.84, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 06:25:55 | EXHAUST | ws4 | t4 at a t1 cadence - rider ws4 35.84, no candidate at or below ws12 (the jump bound 8) |

## the board at 2026-09-03 05:54:25, side high | rider ws5 | the candidate band is ws6..ws13

| the rung | its r value | oob at 15.0/85.0? | past the 25.0/75.0 fence? | reversed since the bar before? | above the rider? | inside the jump band? |
|---|---|---|---|---|---|---|
| ws1 | 84.66 | no | YES | no | no | no |
| ws2 | 68.52 | no | no | no | no | no |
| ws3 | 96.36 | YES | YES | no | no | no |
| ws4 | 87.00 | YES | no | no | no | no |
| ws5 | 58.61 | no | no | no | no | no |
| ws6 | 55.56 | no | no | no | YES | YES |
| ws7 | 46.46 | no | no | no | YES | YES |
| ws8 | 48.93 | no | no | no | YES | YES |
| ws9 | 54.77 | no | no | no | YES | YES |
| ws10 | 58.60 | no | no | no | YES | YES |
| ws11 | 73.00 | no | no | no | YES | YES |
| ws12 | 68.10 | no | no | no | YES | YES |
| ws13 | 54.57 | no | no | no | YES | YES |
| ws14 | 66.64 | no | no | no | YES | no |
| ws15 | 39.96 | no | no | no | YES | no |
| ws16 | 54.39 | no | no | no | YES | no |
| ws17 | 39.95 | no | no | no | YES | no |
| ws18 | 40.59 | no | no | no | YES | no |
| ws19 | 37.98 | no | no | no | YES | no |
| ws20 | 40.36 | no | no | no | YES | no |
| ws21 | 52.21 | no | no | no | YES | no |
| ws22 | 40.25 | no | no | no | YES | no |
| ws23 | 40.29 | no | no | no | YES | no |
| ws24 | 48.17 | no | no | no | YES | no |
| ws25 | 46.04 | no | no | no | YES | no |
| ws26 | 55.94 | no | no | no | YES | no |
| ws27 | 49.98 | no | no | no | YES | no |
| ws28 | 62.27 | no | no | no | YES | no |
| ws29 | 55.98 | no | no | no | YES | no |
| ws30 | 51.20 | no | no | no | YES | no |

| the read | value |
|---|---|
| the oob read's source | emerging |
| the ex-fence read's source | closed_prev |
| rungs oob on this side | 2 |
| rungs ex-fence on this side | 2 |
