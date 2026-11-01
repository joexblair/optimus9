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
| 2026-08-14 08:09:40 | NO PASS | ws30 | - | none offered | ws30 25.67 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:10:55 | CADENCE | ws30 | - | none offered | t1 ws1b oob 09:07:15..09:10:50, ws1r reversed 09:10:25 during, stamp 09:10:25 \| rider ws30 6.12, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 09:14:10 | NO PASS | ws30 | - | none offered | ws30 9.90 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:31:20 | CADENCE | ws30 | - | none offered | t1 ws1b ib 09:30:55, ws1r reversed 09:31:20 inside the 120s grace, stamp 09:31:20 \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:01:40 | NO PASS | ws30 | - | none offered | ws30 18.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:41:20 | CADENCE | ws30 | - | none offered | t1 ws1b ib 10:41:15, ws1r reversed 10:41:20 inside the 120s grace, stamp 10:41:20 \| rider ws30 26.81, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:41:20 | EXHAUST | ws30 | - | - | t4 at a t1 cadence - rider ws30 26.81, no candidate on the whole board |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-14 10:41:20 |
| baton passes made | 2 |
| minutes from the arm to the verdict | 222.3 |
| the rider chain | ws8 > ws29 > ws30 |

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
| 2026-08-14 08:10:00 | NO PASS | ws30 | - | none offered | ws30 25.93 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:10:55 | CADENCE | ws30 | - | none offered | t1 ws1b oob 09:07:15..09:10:50, ws1r reversed 09:10:25 during, stamp 09:10:25 \| rider ws30 6.12, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 09:14:30 | NO PASS | ws30 | - | none offered | ws30 10.59 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:31:20 | CADENCE | ws30 | - | none offered | t1 ws1b ib 09:30:55, ws1r reversed 09:31:20 inside the 120s grace, stamp 09:31:20 \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:01:10 | NO PASS | ws30 | - | none offered | ws30 16.80 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:41:20 | CADENCE | ws30 | - | none offered | t1 ws1b ib 10:41:15, ws1r reversed 10:41:20 inside the 120s grace, stamp 10:41:20 \| rider ws30 26.81, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:41:20 | EXHAUST | ws30 | - | - | t4 at a t1 cadence - rider ws30 26.81, no candidate on the whole board |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-14 10:41:20 |
| baton passes made | 2 |
| minutes from the arm to the verdict | 222.3 |
| the rider chain | ws8 > ws29 > ws30 |

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
| 2026-08-14 08:16:35 | NO PASS | ws30 | - | none offered | ws30 25.76 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:10:55 | CADENCE | ws30 | - | none offered | t1 ws1b oob 09:07:15..09:10:50, ws1r reversed 09:10:25 during, stamp 09:10:25 \| rider ws30 6.12, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-14 09:21:05 | NO PASS | ws30 | - | none offered | ws30 6.12 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 09:31:20 | CADENCE | ws30 | - | none offered | t1 ws1b ib 09:30:55, ws1r reversed 09:31:20 inside the 120s grace, stamp 09:31:20 \| rider ws30 4.18, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 09:33:45 | NO PASS | ws30 | - | none offered | ws30 4.18 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-14 10:41:20 | CADENCE | ws30 | - | none offered | t1 ws1b ib 10:41:15, ws1r reversed 10:41:20 inside the 120s grace, stamp 10:41:20 \| rider ws30 26.81, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-14 10:41:20 | EXHAUST | ws30 | - | - | t4 at a t1 cadence - rider ws30 26.81, no candidate on the whole board |

| the read | value |
|---|---|
| the verdict | EXHAUST |
| the verdict bar | 2026-08-14 10:41:20 |
| baton passes made | 2 |
| minutes from the arm to the verdict | 222.3 |
| the rider chain | ws8 > ws29 > ws30 |

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
| 2026-08-14 10:41:20 | EXHAUST | ws30 | t4 at a t1 cadence - rider ws30 26.81, no candidate on the whole board |

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
| 2026-08-14 10:41:20 | EXHAUST | ws30 | t4 at a t1 cadence - rider ws30 26.81, no candidate on the whole board |

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
| 2026-08-14 10:41:20 | EXHAUST | ws30 | t4 at a t1 cadence - rider ws30 26.81, no candidate on the whole board |
