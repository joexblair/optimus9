# LINEAGE2 BATON CHAIN - THE ARM IS HANDED IN AT 2026-09-03 15:03:00, SIDE high
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
| 2026-09-03 15:03:00 | ARM | - | - | - | arm_at 2026-09-03 15:03:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 15:03:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 15:39:55 | RIDER | ws30 | - | - | t1 gcws30b journey 15:31:30..15:39:50 reached 106.04 past the 95.0 fence, ws1r reversed 15:38:00 during, r 85.71 past the 56.0 fence, stamp 15:38:00, ib 85.0 cross 15:39:00 hold 6 bars, ib dwell 12 bars \| ws30 r 80.19 picked up at a cadence, no prior rider |
| 2026-09-03 16:03:55 | CADENCE | ws30 | - | none offered | t1 gcws30b journey 15:52:00..16:03:50 reached 121.81 past the 95.0 fence, ws1r reversed 16:00:00 during, r 81.36 past the 56.0 fence, stamp 16:00:00, ib 85.0 cross 16:03:00 hold 6 bars, ib dwell 12 bars \| rider ws30 78.54, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-09-03 16:03:55 | HOLD | ws30 | - | - | rider ws30 78.54 ex-fence and not reversed - no action |
| 2026-09-03 16:15:50 | NO PASS | ws30 | - | none offered | ws30 73.26 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 17:18:55 | CADENCE | ws30 | - | none offered | t1 gcws30b journey 17:16:00..17:18:50 reached 118.92 past the 95.0 fence, ws1r reversed 17:18:00 during, r 81.41 past the 56.0 fence, stamp 17:18:00, ib 85.0 cross 17:18:00 hold 6 bars, ib dwell 12 bars \| rider ws30 55.13, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 17:18:55 | TOP RESET | ws30 | ws2 | ws2 76.29 | ws30 55.13 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-09-03 17:20:45 | NO PASS | ws2 | - | none offered | ws2 72.01 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 18:12:25 | CADENCE | ws2 | - | none offered | t1 gcws30b journey 18:09:30..18:12:20 reached 101.38 past the 95.0 fence, ws1r reversed 18:12:00 during, r 76.59 past the 56.0 fence, stamp 18:12:00, ib 85.0 cross 18:11:30 hold 6 bars, ib dwell 12 bars \| rider ws2 68.98, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 18:12:25 | EXHAUST | ws2 | - | - | t4 at a t1 cadence - rider ws2 68.98, no candidate at or below ws10 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-09-03 18:12:25 |
| baton passes made | 0 |
| minutes from the arm to the verdict | 189.4 |
| the rider chain | ws30 > ws2 |

## MODE 'reversal' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-09-03 15:03:00 | ARM | - | - | - | arm_at 2026-09-03 15:03:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 15:03:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 15:39:55 | RIDER | ws30 | - | - | t1 gcws30b journey 15:31:30..15:39:50 reached 106.04 past the 95.0 fence, ws1r reversed 15:38:00 during, r 85.71 past the 56.0 fence, stamp 15:38:00, ib 85.0 cross 15:39:00 hold 6 bars, ib dwell 12 bars \| ws30 r 80.19 picked up at a cadence, no prior rider |
| 2026-09-03 16:03:55 | CADENCE | ws30 | - | none offered | t1 gcws30b journey 15:52:00..16:03:50 reached 121.81 past the 95.0 fence, ws1r reversed 16:00:00 during, r 81.36 past the 56.0 fence, stamp 16:00:00, ib 85.0 cross 16:03:00 hold 6 bars, ib dwell 12 bars \| rider ws30 78.54, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-09-03 16:03:55 | HOLD | ws30 | - | - | rider ws30 78.54 ex-fence and not reversed - no action |
| 2026-09-03 16:09:05 | NO PASS | ws30 | - | none offered | ws30 78.63 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 17:18:55 | CADENCE | ws30 | - | none offered | t1 gcws30b journey 17:16:00..17:18:50 reached 118.92 past the 95.0 fence, ws1r reversed 17:18:00 during, r 81.41 past the 56.0 fence, stamp 17:18:00, ib 85.0 cross 17:18:00 hold 6 bars, ib dwell 12 bars \| rider ws30 55.13, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 17:18:55 | TOP RESET | ws30 | ws2 | ws2 76.29 | ws30 55.13 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-09-03 17:20:15 | NO PASS | ws2 | - | none offered | ws2 72.76 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 18:12:25 | CADENCE | ws2 | - | none offered | t1 gcws30b journey 18:09:30..18:12:20 reached 101.38 past the 95.0 fence, ws1r reversed 18:12:00 during, r 76.59 past the 56.0 fence, stamp 18:12:00, ib 85.0 cross 18:11:30 hold 6 bars, ib dwell 12 bars \| rider ws2 68.98, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 18:12:25 | EXHAUST | ws2 | - | - | t4 at a t1 cadence - rider ws2 68.98, no candidate at or below ws10 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-09-03 18:12:25 |
| baton passes made | 0 |
| minutes from the arm to the verdict | 189.4 |
| the rider chain | ws30 > ws2 |

## MODE 'reversal+quarter' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-09-03 15:03:00 | ARM | - | - | - | arm_at 2026-09-03 15:03:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 15:03:05 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 15:39:55 | RIDER | ws30 | - | - | t1 gcws30b journey 15:31:30..15:39:50 reached 106.04 past the 95.0 fence, ws1r reversed 15:38:00 during, r 85.71 past the 56.0 fence, stamp 15:38:00, ib 85.0 cross 15:39:00 hold 6 bars, ib dwell 12 bars \| ws30 r 80.19 picked up at a cadence, no prior rider |
| 2026-09-03 16:03:55 | CADENCE | ws30 | - | none offered | t1 gcws30b journey 15:52:00..16:03:50 reached 121.81 past the 95.0 fence, ws1r reversed 16:00:00 during, r 81.36 past the 56.0 fence, stamp 16:00:00, ib 85.0 cross 16:03:00 hold 6 bars, ib dwell 12 bars \| rider ws30 78.54, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-09-03 16:03:55 | HOLD | ws30 | - | - | rider ws30 78.54 ex-fence and not reversed - no action |
| 2026-09-03 16:15:40 | NO PASS | ws30 | - | none offered | ws30 73.63 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 17:18:55 | CADENCE | ws30 | - | none offered | t1 gcws30b journey 17:16:00..17:18:50 reached 118.92 past the 95.0 fence, ws1r reversed 17:18:00 during, r 81.41 past the 56.0 fence, stamp 17:18:00, ib 85.0 cross 17:18:00 hold 6 bars, ib dwell 12 bars \| rider ws30 55.13, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 17:18:55 | TOP RESET | ws30 | ws2 | ws2 76.29 | ws30 55.13 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-09-03 17:20:15 | NO PASS | ws2 | - | none offered | ws2 72.76 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 18:12:25 | CADENCE | ws2 | - | none offered | t1 gcws30b journey 18:09:30..18:12:20 reached 101.38 past the 95.0 fence, ws1r reversed 18:12:00 during, r 76.59 past the 56.0 fence, stamp 18:12:00, ib 85.0 cross 18:11:30 hold 6 bars, ib dwell 12 bars \| rider ws2 68.98, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 18:12:25 | EXHAUST | ws2 | - | - | t4 at a t1 cadence - rider ws2 68.98, no candidate at or below ws10 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-09-03 18:12:25 |
| baton passes made | 0 |
| minutes from the arm to the verdict | 189.4 |
| the rider chain | ws30 > ws2 |

## MODE 'ib' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 15:03:00 | ARM | - | arm_at 2026-09-03 15:03:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 15:03:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 15:03:00 | RETEST | - | ws1r 41.06 is not oob at the arm - the gate stays shut |
| 2026-09-03 15:39:55 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 15:39:55, divergence state +1 |
| 2026-09-03 15:39:55 | RIDER | ws30 | t1 gcws30b journey 15:31:30..15:39:50 reached 106.04 past the 95.0 fence, ws1r reversed 15:38:00 during, r 85.71 past the 56.0 fence, stamp 15:38:00, ib 85.0 cross 15:39:00 hold 6 bars, ib dwell 12 bars \| ws30 r 80.19 picked up at a cadence, no prior rider |
| 2026-09-03 16:03:55 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-09-03 16:03:55, divergence state +1 |
| 2026-09-03 16:03:55 | CADENCE | ws30 | t1 gcws30b journey 15:52:00..16:03:50 reached 121.81 past the 95.0 fence, ws1r reversed 16:00:00 during, r 81.36 past the 56.0 fence, stamp 16:00:00, ib 85.0 cross 16:03:00 hold 6 bars, ib dwell 12 bars \| rider ws30 78.54, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-09-03 16:03:55 | HOLD | ws30 | rider ws30 78.54 ex-fence and not reversed - no action |
| 2026-09-03 16:15:50 | NO PASS | ws30 | ws30 73.26 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 17:18:55 | CADENCE | ws30 | t1 gcws30b journey 17:16:00..17:18:50 reached 118.92 past the 95.0 fence, ws1r reversed 17:18:00 during, r 81.41 past the 56.0 fence, stamp 17:18:00, ib 85.0 cross 17:18:00 hold 6 bars, ib dwell 12 bars \| rider ws30 55.13, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 17:18:55 | TOP RESET | ws30 | ws30 55.13 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-09-03 17:20:45 | NO PASS | ws2 | ws2 72.01 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 18:12:25 | CADENCE | ws2 | t1 gcws30b journey 18:09:30..18:12:20 reached 101.38 past the 95.0 fence, ws1r reversed 18:12:00 during, r 76.59 past the 56.0 fence, stamp 18:12:00, ib 85.0 cross 18:11:30 hold 6 bars, ib dwell 12 bars \| rider ws2 68.98, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 18:12:25 | EXHAUST | ws2 | t4 at a t1 cadence - rider ws2 68.98, no candidate at or below ws10 (the jump bound 8) |

## MODE 'reversal' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 15:03:00 | ARM | - | arm_at 2026-09-03 15:03:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 15:03:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 15:03:00 | RETEST | - | ws1r 41.06 is not oob at the arm - the gate stays shut |
| 2026-09-03 15:39:55 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 15:39:55, divergence state +1 |
| 2026-09-03 15:39:55 | RIDER | ws30 | t1 gcws30b journey 15:31:30..15:39:50 reached 106.04 past the 95.0 fence, ws1r reversed 15:38:00 during, r 85.71 past the 56.0 fence, stamp 15:38:00, ib 85.0 cross 15:39:00 hold 6 bars, ib dwell 12 bars \| ws30 r 80.19 picked up at a cadence, no prior rider |
| 2026-09-03 16:03:55 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-09-03 16:03:55, divergence state +1 |
| 2026-09-03 16:03:55 | CADENCE | ws30 | t1 gcws30b journey 15:52:00..16:03:50 reached 121.81 past the 95.0 fence, ws1r reversed 16:00:00 during, r 81.36 past the 56.0 fence, stamp 16:00:00, ib 85.0 cross 16:03:00 hold 6 bars, ib dwell 12 bars \| rider ws30 78.54, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-09-03 16:03:55 | HOLD | ws30 | rider ws30 78.54 ex-fence and not reversed - no action |
| 2026-09-03 16:09:05 | NO PASS | ws30 | ws30 78.63 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 17:18:55 | CADENCE | ws30 | t1 gcws30b journey 17:16:00..17:18:50 reached 118.92 past the 95.0 fence, ws1r reversed 17:18:00 during, r 81.41 past the 56.0 fence, stamp 17:18:00, ib 85.0 cross 17:18:00 hold 6 bars, ib dwell 12 bars \| rider ws30 55.13, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 17:18:55 | TOP RESET | ws30 | ws30 55.13 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-09-03 17:20:15 | NO PASS | ws2 | ws2 72.76 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 18:12:25 | CADENCE | ws2 | t1 gcws30b journey 18:09:30..18:12:20 reached 101.38 past the 95.0 fence, ws1r reversed 18:12:00 during, r 76.59 past the 56.0 fence, stamp 18:12:00, ib 85.0 cross 18:11:30 hold 6 bars, ib dwell 12 bars \| rider ws2 68.98, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 18:12:25 | EXHAUST | ws2 | t4 at a t1 cadence - rider ws2 68.98, no candidate at or below ws10 (the jump bound 8) |

## MODE 'reversal+quarter' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 15:03:00 | ARM | - | arm_at 2026-09-03 15:03:00 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 15:03:05 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 15:03:00 | RETEST | - | ws1r 41.06 is not oob at the arm - the gate stays shut |
| 2026-09-03 15:39:55 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 15:39:55, divergence state +1 |
| 2026-09-03 15:39:55 | RIDER | ws30 | t1 gcws30b journey 15:31:30..15:39:50 reached 106.04 past the 95.0 fence, ws1r reversed 15:38:00 during, r 85.71 past the 56.0 fence, stamp 15:38:00, ib 85.0 cross 15:39:00 hold 6 bars, ib dwell 12 bars \| ws30 r 80.19 picked up at a cadence, no prior rider |
| 2026-09-03 16:03:55 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-09-03 16:03:55, divergence state +1 |
| 2026-09-03 16:03:55 | CADENCE | ws30 | t1 gcws30b journey 15:52:00..16:03:50 reached 121.81 past the 95.0 fence, ws1r reversed 16:00:00 during, r 81.36 past the 56.0 fence, stamp 16:00:00, ib 85.0 cross 16:03:00 hold 6 bars, ib dwell 12 bars \| rider ws30 78.54, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-09-03 16:03:55 | HOLD | ws30 | rider ws30 78.54 ex-fence and not reversed - no action |
| 2026-09-03 16:15:40 | NO PASS | ws30 | ws30 73.63 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 17:18:55 | CADENCE | ws30 | t1 gcws30b journey 17:16:00..17:18:50 reached 118.92 past the 95.0 fence, ws1r reversed 17:18:00 during, r 81.41 past the 56.0 fence, stamp 17:18:00, ib 85.0 cross 17:18:00 hold 6 bars, ib dwell 12 bars \| rider ws30 55.13, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 17:18:55 | TOP RESET | ws30 | ws30 55.13 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws2 |
| 2026-09-03 17:20:15 | NO PASS | ws2 | ws2 72.76 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-03 18:12:25 | CADENCE | ws2 | t1 gcws30b journey 18:09:30..18:12:20 reached 101.38 past the 95.0 fence, ws1r reversed 18:12:00 during, r 76.59 past the 56.0 fence, stamp 18:12:00, ib 85.0 cross 18:11:30 hold 6 bars, ib dwell 12 bars \| rider ws2 68.98, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-09-03 18:12:25 | EXHAUST | ws2 | t4 at a t1 cadence - rider ws2 68.98, no candidate at or below ws10 (the jump bound 8) |

## the first high-side reversal of each rung at or after 2026-09-03 15:03:00 - no forward bound

| the rung | its value at 15:03:00 | the first reversal raw bar | min after 15:03:00 | its value at the raw bar | the stamp, raw + 11 bars | its value at the stamp |
|---|---|---|---|---|---|---|
| ws22 | 78.33 | 2026-09-03 15:03:50 | 0.8 | 76.83 | 2026-09-03 15:04:45 | 72.95 |
| ws23 | 80.86 | 2026-09-03 15:10:05 | 7.1 | 78.19 | 2026-09-03 15:11:00 | 77.59 |
| ws24 | 92.81 | 2026-09-03 15:45:05 | 42.1 | 90.08 | 2026-09-03 15:46:00 | 89.14 |
| ws25 | 68.30 | 2026-09-03 15:06:15 | 3.2 | 67.00 | 2026-09-03 15:07:10 | 65.57 |
| ws26 | 89.23 | 2026-09-03 15:10:55 | 7.9 | 85.57 | 2026-09-03 15:11:50 | 80.57 |
| ws27 | 94.53 | 2026-09-03 15:19:00 | 16.0 | 91.64 | 2026-09-03 15:19:55 | 90.16 |
| ws28 | 90.62 | 2026-09-03 15:08:00 | 5.0 | 87.50 | 2026-09-03 15:08:55 | 87.71 |
| ws29 | 88.43 | 2026-09-03 15:04:25 | 1.4 | 85.76 | 2026-09-03 15:05:20 | 85.98 |
| ws30 | 91.68 | 2026-09-03 15:06:45 | 3.8 | 87.94 | 2026-09-03 15:07:40 | 87.71 |
