# LINEAGE2 BATON CHAIN - THE ARM IS HANDED IN AT 2026-09-03 22:01:15, SIDE low
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
| 2026-09-03 22:01:15 | ARM | - | - | - | arm_at 2026-09-03 22:01:15 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 22:01:20 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 22:36:25 | RIDER | ws30 | - | - | t1 gcws30b oob 22:31:40..22:35:55, ws1r reversed 22:34:40 during, r 10.09 past the 44.0 fence, stamp 22:34:40, cross 22:36:00 hold 6 bars \| ws30 r 4.64 picked up at a cadence, no prior rider |
| 2026-09-03 22:48:25 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 22:48:00, ws1r reversed 22:48:15 inside the 120s grace from the cross bar 22:48:00, r 18.20 past the 44.0 fence, stamp 22:48:15, hold 6 bars \| rider ws30 4.64, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 22:48:25 | HOLD | ws30 | - | - | rider ws30 4.64 oob - no action |
| 2026-09-03 23:11:45 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 23:11:20, ws1r reversed 23:11:25 inside the 120s grace from the cross bar 23:11:20, r 20.62 past the 44.0 fence, stamp 23:11:25, hold 6 bars \| rider ws30 4.64, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-09-03 23:11:45 | HOLD | ws30 | - | - | rider ws30 4.64 oob - no action |
| 2026-09-03 23:13:35 | CADENCE | ws30 | - | none offered | t1 gcws30b oob 23:12:55..23:13:05, ws1r reversed 23:13:00 during, r 19.06 past the 44.0 fence, stamp 23:13:00, cross 23:13:10 hold 6 bars \| rider ws30 4.64, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 23:13:35 | HOLD | ws30 | - | - | rider ws30 4.64 oob - no action |
| 2026-09-03 23:30:35 | NO PASS | ws30 | - | none offered | ws30 6.82 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-04 00:10:00 | CADENCE | ws30 | - | none offered | t1 gcws30b oob 00:06:30..00:09:30, ws1r reversed 00:09:00 during, r 8.51 past the 44.0 fence, stamp 00:09:00, cross 00:09:35 hold 6 bars \| rider ws30 21.01, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-09-04 00:10:00 | TOP RESET | ws30 | ws8 | ws8 87.30 | ws30 21.01 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws8 |
| 2026-09-04 00:10:10 | NO PASS | ws8 | - | none offered | ws8 87.18 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-04 01:01:00 | CADENCE | ws8 | - | none offered | t1 gcws30b ib 01:00:05, ws1r reversed 01:01:00 inside the 120s grace from the cross bar 01:00:05, r 20.35 past the 44.0 fence, stamp 01:01:00, hold 6 bars \| rider ws8 46.24, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-09-04 01:01:00 | EXHAUST | ws8 | - | - | t4 at a t1 cadence - rider ws8 46.24, no candidate at or below ws16 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-09-04 01:01:00 |
| baton passes made | 0 |
| minutes from the arm to the verdict | 179.8 |
| the rider chain | ws30 > ws8 |

## MODE 'reversal' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-09-03 22:01:15 | ARM | - | - | - | arm_at 2026-09-03 22:01:15 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 22:01:20 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 22:36:25 | RIDER | ws30 | - | - | t1 gcws30b oob 22:31:40..22:35:55, ws1r reversed 22:34:40 during, r 10.09 past the 44.0 fence, stamp 22:34:40, cross 22:36:00 hold 6 bars \| ws30 r 4.64 picked up at a cadence, no prior rider |
| 2026-09-03 22:48:25 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 22:48:00, ws1r reversed 22:48:15 inside the 120s grace from the cross bar 22:48:00, r 18.20 past the 44.0 fence, stamp 22:48:15, hold 6 bars \| rider ws30 4.64, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 22:48:25 | HOLD | ws30 | - | - | rider ws30 4.64 oob - no action |
| 2026-09-03 23:11:45 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 23:11:20, ws1r reversed 23:11:25 inside the 120s grace from the cross bar 23:11:20, r 20.62 past the 44.0 fence, stamp 23:11:25, hold 6 bars \| rider ws30 4.64, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-09-03 23:11:45 | HOLD | ws30 | - | - | rider ws30 4.64 oob - no action |
| 2026-09-03 23:13:35 | CADENCE | ws30 | - | none offered | t1 gcws30b oob 23:12:55..23:13:05, ws1r reversed 23:13:00 during, r 19.06 past the 44.0 fence, stamp 23:13:00, cross 23:13:10 hold 6 bars \| rider ws30 4.64, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 23:13:35 | HOLD | ws30 | - | - | rider ws30 4.64 oob - no action |
| 2026-09-03 23:32:05 | NO PASS | ws30 | - | none offered | ws30 6.82 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-04 00:10:00 | CADENCE | ws30 | - | none offered | t1 gcws30b oob 00:06:30..00:09:30, ws1r reversed 00:09:00 during, r 8.51 past the 44.0 fence, stamp 00:09:00, cross 00:09:35 hold 6 bars \| rider ws30 21.01, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-09-04 00:10:00 | TOP RESET | ws30 | ws8 | ws8 87.30 | ws30 21.01 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws8 |
| 2026-09-04 00:10:30 | NO PASS | ws8 | - | none offered | ws8 87.30 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-04 01:01:00 | CADENCE | ws8 | - | none offered | t1 gcws30b ib 01:00:05, ws1r reversed 01:01:00 inside the 120s grace from the cross bar 01:00:05, r 20.35 past the 44.0 fence, stamp 01:01:00, hold 6 bars \| rider ws8 46.24, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-09-04 01:01:00 | EXHAUST | ws8 | - | - | t4 at a t1 cadence - rider ws8 46.24, no candidate at or below ws16 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-09-04 01:01:00 |
| baton passes made | 0 |
| minutes from the arm to the verdict | 179.8 |
| the rider chain | ws30 > ws8 |

## MODE 'reversal+quarter' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-09-03 22:01:15 | ARM | - | - | - | arm_at 2026-09-03 22:01:15 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 22:01:20 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 22:36:25 | RIDER | ws30 | - | - | t1 gcws30b oob 22:31:40..22:35:55, ws1r reversed 22:34:40 during, r 10.09 past the 44.0 fence, stamp 22:34:40, cross 22:36:00 hold 6 bars \| ws30 r 4.64 picked up at a cadence, no prior rider |
| 2026-09-03 22:48:25 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 22:48:00, ws1r reversed 22:48:15 inside the 120s grace from the cross bar 22:48:00, r 18.20 past the 44.0 fence, stamp 22:48:15, hold 6 bars \| rider ws30 4.64, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 22:48:25 | HOLD | ws30 | - | - | rider ws30 4.64 oob - no action |
| 2026-09-03 23:11:45 | CADENCE | ws30 | - | none offered | t1 gcws30b ib 23:11:20, ws1r reversed 23:11:25 inside the 120s grace from the cross bar 23:11:20, r 20.62 past the 44.0 fence, stamp 23:11:25, hold 6 bars \| rider ws30 4.64, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-09-03 23:11:45 | HOLD | ws30 | - | - | rider ws30 4.64 oob - no action |
| 2026-09-03 23:13:35 | CADENCE | ws30 | - | none offered | t1 gcws30b oob 23:12:55..23:13:05, ws1r reversed 23:13:00 during, r 19.06 past the 44.0 fence, stamp 23:13:00, cross 23:13:10 hold 6 bars \| rider ws30 4.64, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 23:13:35 | HOLD | ws30 | - | - | rider ws30 4.64 oob - no action |
| 2026-09-03 23:38:40 | NO PASS | ws30 | - | none offered | ws30 12.65 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-04 00:10:00 | CADENCE | ws30 | - | none offered | t1 gcws30b oob 00:06:30..00:09:30, ws1r reversed 00:09:00 during, r 8.51 past the 44.0 fence, stamp 00:09:00, cross 00:09:35 hold 6 bars \| rider ws30 21.01, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-09-04 00:10:00 | TOP RESET | ws30 | ws8 | ws8 87.30 | ws30 21.01 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws8 |
| 2026-09-04 00:11:35 | NO PASS | ws8 | - | none offered | ws8 86.93 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-04 01:01:00 | CADENCE | ws8 | - | none offered | t1 gcws30b ib 01:00:05, ws1r reversed 01:01:00 inside the 120s grace from the cross bar 01:00:05, r 20.35 past the 44.0 fence, stamp 01:01:00, hold 6 bars \| rider ws8 46.24, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-09-04 01:01:00 | EXHAUST | ws8 | - | - | t4 at a t1 cadence - rider ws8 46.24, no candidate at or below ws16 (the jump bound 8) |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-09-04 01:01:00 |
| baton passes made | 0 |
| minutes from the arm to the verdict | 179.8 |
| the rider chain | ws30 > ws8 |

## MODE 'ib' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 22:01:15 | ARM | - | arm_at 2026-09-03 22:01:15 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 22:01:20 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 22:01:15 | RETEST | - | ws2r 24.47 / ws3r 11.06 - not both inside the fence at the arm |
| 2026-09-03 22:36:25 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 22:36:25, divergence state -1 |
| 2026-09-03 22:36:25 | RIDER | ws30 | t1 gcws30b oob 22:31:40..22:35:55, ws1r reversed 22:34:40 during, r 10.09 past the 44.0 fence, stamp 22:34:40, cross 22:36:00 hold 6 bars \| ws30 r 4.64 picked up at a cadence, no prior rider |
| 2026-09-03 22:48:25 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-09-03 22:48:25, divergence state -1 |
| 2026-09-03 22:48:25 | CADENCE | ws30 | t1 gcws30b ib 22:48:00, ws1r reversed 22:48:15 inside the 120s grace from the cross bar 22:48:00, r 18.20 past the 44.0 fence, stamp 22:48:15, hold 6 bars \| rider ws30 4.64, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 22:48:25 | HOLD | ws30 | rider ws30 4.64 oob - no action |
| 2026-09-03 23:11:45 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-09-03 23:11:45, divergence state -1 |
| 2026-09-03 23:11:45 | CADENCE | ws30 | t1 gcws30b ib 23:11:20, ws1r reversed 23:11:25 inside the 120s grace from the cross bar 23:11:20, r 20.62 past the 44.0 fence, stamp 23:11:25, hold 6 bars \| rider ws30 4.64, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-09-03 23:11:45 | HOLD | ws30 | rider ws30 4.64 oob - no action |
| 2026-09-03 23:13:35 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-09-03 23:13:35, divergence state -1 |
| 2026-09-03 23:13:35 | CADENCE | ws30 | t1 gcws30b oob 23:12:55..23:13:05, ws1r reversed 23:13:00 during, r 19.06 past the 44.0 fence, stamp 23:13:00, cross 23:13:10 hold 6 bars \| rider ws30 4.64, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 23:13:35 | HOLD | ws30 | rider ws30 4.64 oob - no action |
| 2026-09-03 23:30:35 | NO PASS | ws30 | ws30 6.82 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-04 00:10:00 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-09-04 00:10:00, divergence state -1 |
| 2026-09-04 00:10:00 | CADENCE | ws30 | t1 gcws30b oob 00:06:30..00:09:30, ws1r reversed 00:09:00 during, r 8.51 past the 44.0 fence, stamp 00:09:00, cross 00:09:35 hold 6 bars \| rider ws30 21.01, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-09-04 00:10:00 | TOP RESET | ws30 | ws30 21.01 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws8 |
| 2026-09-04 00:10:10 | NO PASS | ws8 | ws8 87.18 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-04 01:01:00 | LATCH1 | ws8 | latch 1 at the t1 cadence 2026-09-04 01:01:00, divergence state -1 |
| 2026-09-04 01:01:00 | CADENCE | ws8 | t1 gcws30b ib 01:00:05, ws1r reversed 01:01:00 inside the 120s grace from the cross bar 01:00:05, r 20.35 past the 44.0 fence, stamp 01:01:00, hold 6 bars \| rider ws8 46.24, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-09-04 01:01:00 | EXHAUST | ws8 | t4 at a t1 cadence - rider ws8 46.24, no candidate at or below ws16 (the jump bound 8) |

## MODE 'reversal' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 22:01:15 | ARM | - | arm_at 2026-09-03 22:01:15 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 22:01:20 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 22:01:15 | RETEST | - | ws2r 24.47 / ws3r 11.06 - not both inside the fence at the arm |
| 2026-09-03 22:36:25 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 22:36:25, divergence state -1 |
| 2026-09-03 22:36:25 | RIDER | ws30 | t1 gcws30b oob 22:31:40..22:35:55, ws1r reversed 22:34:40 during, r 10.09 past the 44.0 fence, stamp 22:34:40, cross 22:36:00 hold 6 bars \| ws30 r 4.64 picked up at a cadence, no prior rider |
| 2026-09-03 22:48:25 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-09-03 22:48:25, divergence state -1 |
| 2026-09-03 22:48:25 | CADENCE | ws30 | t1 gcws30b ib 22:48:00, ws1r reversed 22:48:15 inside the 120s grace from the cross bar 22:48:00, r 18.20 past the 44.0 fence, stamp 22:48:15, hold 6 bars \| rider ws30 4.64, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 22:48:25 | HOLD | ws30 | rider ws30 4.64 oob - no action |
| 2026-09-03 23:11:45 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-09-03 23:11:45, divergence state -1 |
| 2026-09-03 23:11:45 | CADENCE | ws30 | t1 gcws30b ib 23:11:20, ws1r reversed 23:11:25 inside the 120s grace from the cross bar 23:11:20, r 20.62 past the 44.0 fence, stamp 23:11:25, hold 6 bars \| rider ws30 4.64, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-09-03 23:11:45 | HOLD | ws30 | rider ws30 4.64 oob - no action |
| 2026-09-03 23:13:35 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-09-03 23:13:35, divergence state -1 |
| 2026-09-03 23:13:35 | CADENCE | ws30 | t1 gcws30b oob 23:12:55..23:13:05, ws1r reversed 23:13:00 during, r 19.06 past the 44.0 fence, stamp 23:13:00, cross 23:13:10 hold 6 bars \| rider ws30 4.64, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 23:13:35 | HOLD | ws30 | rider ws30 4.64 oob - no action |
| 2026-09-03 23:32:05 | NO PASS | ws30 | ws30 6.82 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-04 00:10:00 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-09-04 00:10:00, divergence state -1 |
| 2026-09-04 00:10:00 | CADENCE | ws30 | t1 gcws30b oob 00:06:30..00:09:30, ws1r reversed 00:09:00 during, r 8.51 past the 44.0 fence, stamp 00:09:00, cross 00:09:35 hold 6 bars \| rider ws30 21.01, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-09-04 00:10:00 | TOP RESET | ws30 | ws30 21.01 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws8 |
| 2026-09-04 00:10:30 | NO PASS | ws8 | ws8 87.30 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-04 01:01:00 | LATCH1 | ws8 | latch 1 at the t1 cadence 2026-09-04 01:01:00, divergence state -1 |
| 2026-09-04 01:01:00 | CADENCE | ws8 | t1 gcws30b ib 01:00:05, ws1r reversed 01:01:00 inside the 120s grace from the cross bar 01:00:05, r 20.35 past the 44.0 fence, stamp 01:01:00, hold 6 bars \| rider ws8 46.24, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-09-04 01:01:00 | EXHAUST | ws8 | t4 at a t1 cadence - rider ws8 46.24, no candidate at or below ws16 (the jump bound 8) |

## MODE 'reversal+quarter' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 22:01:15 | ARM | - | arm_at 2026-09-03 22:01:15 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 22:01:20 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 22:01:15 | RETEST | - | ws2r 24.47 / ws3r 11.06 - not both inside the fence at the arm |
| 2026-09-03 22:36:25 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 22:36:25, divergence state -1 |
| 2026-09-03 22:36:25 | RIDER | ws30 | t1 gcws30b oob 22:31:40..22:35:55, ws1r reversed 22:34:40 during, r 10.09 past the 44.0 fence, stamp 22:34:40, cross 22:36:00 hold 6 bars \| ws30 r 4.64 picked up at a cadence, no prior rider |
| 2026-09-03 22:48:25 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-09-03 22:48:25, divergence state -1 |
| 2026-09-03 22:48:25 | CADENCE | ws30 | t1 gcws30b ib 22:48:00, ws1r reversed 22:48:15 inside the 120s grace from the cross bar 22:48:00, r 18.20 past the 44.0 fence, stamp 22:48:15, hold 6 bars \| rider ws30 4.64, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 22:48:25 | HOLD | ws30 | rider ws30 4.64 oob - no action |
| 2026-09-03 23:11:45 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-09-03 23:11:45, divergence state -1 |
| 2026-09-03 23:11:45 | CADENCE | ws30 | t1 gcws30b ib 23:11:20, ws1r reversed 23:11:25 inside the 120s grace from the cross bar 23:11:20, r 20.62 past the 44.0 fence, stamp 23:11:25, hold 6 bars \| rider ws30 4.64, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-09-03 23:11:45 | HOLD | ws30 | rider ws30 4.64 oob - no action |
| 2026-09-03 23:13:35 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-09-03 23:13:35, divergence state -1 |
| 2026-09-03 23:13:35 | CADENCE | ws30 | t1 gcws30b oob 23:12:55..23:13:05, ws1r reversed 23:13:00 during, r 19.06 past the 44.0 fence, stamp 23:13:00, cross 23:13:10 hold 6 bars \| rider ws30 4.64, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-09-03 23:13:35 | HOLD | ws30 | rider ws30 4.64 oob - no action |
| 2026-09-03 23:38:40 | NO PASS | ws30 | ws30 12.65 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-04 00:10:00 | LATCH1 | ws30 | latch 1 at the t1 cadence 2026-09-04 00:10:00, divergence state -1 |
| 2026-09-04 00:10:00 | CADENCE | ws30 | t1 gcws30b oob 00:06:30..00:09:30, ws1r reversed 00:09:00 during, r 8.51 past the 44.0 fence, stamp 00:09:00, cross 00:09:35 hold 6 bars \| rider ws30 21.01, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-09-04 00:10:00 | TOP RESET | ws30 | ws30 21.01 is the ladder top and exhausted - the rider resets to 0 and re-scans capped at ws8 by the jump bound, taking ws8 |
| 2026-09-04 00:11:35 | NO PASS | ws8 | ws8 86.93 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-09-04 01:01:00 | LATCH1 | ws8 | latch 1 at the t1 cadence 2026-09-04 01:01:00, divergence state -1 |
| 2026-09-04 01:01:00 | CADENCE | ws8 | t1 gcws30b ib 01:00:05, ws1r reversed 01:01:00 inside the 120s grace from the cross bar 01:00:05, r 20.35 past the 44.0 fence, stamp 01:01:00, hold 6 bars \| rider ws8 46.24, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-09-04 01:01:00 | EXHAUST | ws8 | t4 at a t1 cadence - rider ws8 46.24, no candidate at or below ws16 (the jump bound 8) |

## ws4r sampled every 1 min and HELD, 2026-09-03 04:30:00 .. 2026-09-03 04:40:00

| the sample bar | ws4r, held from here | the move from the last sample | at or below the 15.0 oob? | past the 25.0 fence? |
|---|---|---|---|---|
| 2026-09-03 04:30:00 | 42.29 | - | no | no |
| 2026-09-03 04:31:00 | 45.90 | +3.61 | no | no |
| 2026-09-03 04:32:00 | 39.74 | -6.16 | no | no |
| 2026-09-03 04:33:00 | 43.14 | +3.40 | no | no |
| 2026-09-03 04:34:00 | 33.78 | -9.36 | no | no |
| 2026-09-03 04:35:00 | 31.94 | -1.84 | no | no |
| 2026-09-03 04:36:00 | 23.39 | -8.56 | no | YES |
| 2026-09-03 04:37:00 | 23.13 | -0.26 | no | YES |
| 2026-09-03 04:38:00 | 28.24 | +5.11 | no | no |
| 2026-09-03 04:39:00 | 27.86 | -0.38 | no | no |
| 2026-09-03 04:40:00 | 34.25 | +6.39 | no | no |

## ws4r sampled every 2 min and HELD, 2026-09-03 04:30:00 .. 2026-09-03 04:40:00

| the sample bar | ws4r, held from here | the move from the last sample | at or below the 15.0 oob? | past the 25.0 fence? |
|---|---|---|---|---|
| 2026-09-03 04:30:00 | 42.29 | - | no | no |
| 2026-09-03 04:32:00 | 39.74 | -2.55 | no | no |
| 2026-09-03 04:34:00 | 33.78 | -5.95 | no | no |
| 2026-09-03 04:36:00 | 23.39 | -10.40 | no | YES |
| 2026-09-03 04:38:00 | 28.24 | +4.85 | no | no |
| 2026-09-03 04:40:00 | 34.25 | +6.01 | no | no |

## the bar the reset scan reads, for comparison - NOT part of either series above

| the bar | ws4r | at or below the 15.0 oob? | past the 25.0 fence? |
|---|---|---|---|
| 2026-09-03 04:37:55 | 24.86 | no | YES |
