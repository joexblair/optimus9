# LINEAGE2 BATON CHAIN - THE ARM IS HANDED IN AT 2026-09-03 22:01:15, SIDE low
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
| 2026-09-03 22:01:15 | ARM | - | - | - | arm_at 2026-09-03 22:01:15 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 22:01:20 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 22:36:25 | EXHAUST | - | - | - | t1 gcws30b oob 22:31:40..22:35:55, ws1r reversed 22:34:40 during, r 10.09 past the 44.0 fence, stamp 22:34:40, cross 22:36:00 hold 6 bars \| divergence -1 bullish with a low target side, anchored on the cadence bar 2026-09-03 22:36:25 - rev-trade (raw state -1) |

| the read | value |
|---|---|
| the verdict | DIV REV-TRADE |
| the verdict bar | 2026-09-03 22:36:25 |
| baton passes made | 0 |
| minutes from the arm to the verdict | 35.2 |
| the rider chain | - |

## MODE 'reversal' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-09-03 22:01:15 | ARM | - | - | - | arm_at 2026-09-03 22:01:15 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 22:01:20 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 22:36:25 | EXHAUST | - | - | - | t1 gcws30b oob 22:31:40..22:35:55, ws1r reversed 22:34:40 during, r 10.09 past the 44.0 fence, stamp 22:34:40, cross 22:36:00 hold 6 bars \| divergence -1 bullish with a low target side, anchored on the cadence bar 2026-09-03 22:36:25 - rev-trade (raw state -1) |

| the read | value |
|---|---|
| the verdict | DIV REV-TRADE |
| the verdict bar | 2026-09-03 22:36:25 |
| baton passes made | 0 |
| minutes from the arm to the verdict | 35.2 |
| the rider chain | - |

## MODE 'reversal+quarter' - the baton passes and the exhaust

| the bar | the stage | from rider | to rider | the candidates offered | why |
|---|---|---|---|---|---|
| 2026-09-03 22:01:15 | ARM | - | - | - | arm_at 2026-09-03 22:01:15 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 22:01:20 | NO RIDER | - | - | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 22:36:25 | EXHAUST | - | - | - | t1 gcws30b oob 22:31:40..22:35:55, ws1r reversed 22:34:40 during, r 10.09 past the 44.0 fence, stamp 22:34:40, cross 22:36:00 hold 6 bars \| divergence -1 bullish with a low target side, anchored on the cadence bar 2026-09-03 22:36:25 - rev-trade (raw state -1) |

| the read | value |
|---|---|
| the verdict | DIV REV-TRADE |
| the verdict bar | 2026-09-03 22:36:25 |
| baton passes made | 0 |
| minutes from the arm to the verdict | 35.2 |
| the rider chain | - |

## MODE 'ib' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 22:01:15 | ARM | - | arm_at 2026-09-03 22:01:15 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 22:01:20 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 22:01:15 | RETEST | - | ws2r 24.47 / ws3r 11.06 - not both inside the fence at the arm |
| 2026-09-03 22:36:25 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 22:36:25, divergence state -1 |
| 2026-09-03 22:36:25 | EXHAUST | - | t1 gcws30b oob 22:31:40..22:35:55, ws1r reversed 22:34:40 during, r 10.09 past the 44.0 fence, stamp 22:34:40, cross 22:36:00 hold 6 bars \| divergence -1 bullish with a low target side, anchored on the cadence bar 2026-09-03 22:36:25 - rev-trade (raw state -1) |

## MODE 'reversal' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 22:01:15 | ARM | - | arm_at 2026-09-03 22:01:15 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 22:01:20 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 22:01:15 | RETEST | - | ws2r 24.47 / ws3r 11.06 - not both inside the fence at the arm |
| 2026-09-03 22:36:25 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 22:36:25, divergence state -1 |
| 2026-09-03 22:36:25 | EXHAUST | - | t1 gcws30b oob 22:31:40..22:35:55, ws1r reversed 22:34:40 during, r 10.09 past the 44.0 fence, stamp 22:34:40, cross 22:36:00 hold 6 bars \| divergence -1 bullish with a low target side, anchored on the cadence bar 2026-09-03 22:36:25 - rev-trade (raw state -1) |

## MODE 'reversal+quarter' - every row of the walk

| the bar | the stage | rider | why |
|---|---|---|---|
| 2026-09-03 22:01:15 | ARM | - | arm_at 2026-09-03 22:01:15 - the arm race is skipped, this bar IS the arm |
| 2026-09-03 22:01:20 | NO RIDER | - | the arm starts with rider 0 - his 1031 rule, jump bound 8 TFs |
| 2026-09-03 22:01:15 | RETEST | - | ws2r 24.47 / ws3r 11.06 - not both inside the fence at the arm |
| 2026-09-03 22:36:25 | LATCH1 | - | latch 1 at the t1 cadence 2026-09-03 22:36:25, divergence state -1 |
| 2026-09-03 22:36:25 | EXHAUST | - | t1 gcws30b oob 22:31:40..22:35:55, ws1r reversed 22:34:40 during, r 10.09 past the 44.0 fence, stamp 22:34:40, cross 22:36:00 hold 6 bars \| divergence -1 bullish with a low target side, anchored on the cadence bar 2026-09-03 22:36:25 - rev-trade (raw state -1) |
