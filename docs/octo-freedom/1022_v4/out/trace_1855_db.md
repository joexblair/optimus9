# THE MACHINE, mode 'trace'. 2026-09-01 00:00:00 .. 2026-09-01 23:59:55
# order 'saviour,core,backstop', backstop fallback 'drop'. ONE position at a time.
# LIN_PASS 'ib', lookback floor ON at ws6, 6 backstop fires. RULED_OK True.

| the invisible trade | its target-side | the real trade it opens | detail |
|---|---|---|---|
| an invisible LONG | high | 2026-09-01 00:33:05 | cws1b 2026-09-01 00:04:00, arm 2026-09-01 00:26:00, ws2, exh 2026-09-01 00:33:00 |
| an invisible SHORT | low | 2026-09-01 02:25:25 | cws1b 2026-09-01 01:07:00, arm 2026-09-01 02:12:00, ws3, exh 2026-09-01 02:25:20 |

## the leg holding 2026-09-01 19:00:00: a LONG opened 2026-09-01 18:55:15, target-side high

### saviour

| the step | the bar | the reading |
|---|---|---|
| the open | 2026-09-01 18:55:15 | ws5r 47.99, target-side high |
| the arm, ws5r oob on the COUNTER-TARGET side (low) | 2026-09-01 18:55:15 | ws5r oob no -> armed |
| the cap | 2026-09-01 18:55:15 to 2026-09-01 19:11:15 | 192 bars = 16 min from the open |
| the first ws1r oob run | 2026-09-01 18:55:20 to 2026-09-01 18:55:55 | 8 bars, peak 89.90, 1 run(s) inside the cap |
| the ws1r oob run that crossed | 2026-09-01 18:55:20 to 2026-09-01 18:55:55 | 8 bars, peak 89.90 |
| the ws1r oob->ib cross | 2026-09-01 18:56:05 | ws1r 75.62, held 2 bars |
| the ws1r lift-off | 2026-09-01 18:54:35 | stamped 2026-09-01 18:55:10, 55 s before the cross |
| the cascade at the stamp | 2026-09-01 18:55:10 | down | down | the low cluster ws1 to ws12, 12 lines, falling COUNTS | the high cluster ws1 to ws12, 12 lines, falling COUNTS | the end-to-end diff +52.38 | zoom 2 rungs, min 4 lines |
| ws1Mage past 50 towards the target-side | 2026-09-01 18:56:05 | ws1Mage 57.3960, YES |
| branch A does not fire - branch B | 2026-09-01 18:56:05 | ws1Mage is past 50 towards the target-side. walk to ws2r oob, inside the cap to 2026-09-01 19:11:15 |
| the ws2r oob run | 2026-09-01 19:06:15 to 2026-09-01 19:08:00 | 22 bars, peak 96.74 |
| the ws2r oob->ib cross | 2026-09-01 19:08:10 | ws2r 78.15, 37 bars inside the cap |
| the ws2r lift-off | 2026-09-01 19:02:40 | stamped 2026-09-01 19:03:15, 295 s before the cross |
| the cascade at the stamp | 2026-09-01 19:03:15 | down | down | the low cluster ws1 to ws12, 12 lines, falling COUNTS | the high cluster ws1 to ws12, 12 lines, falling COUNTS | the end-to-end diff +58.76 | zoom 2 rungs, min 4 lines |
| ws2Mage past 50 towards the target-side | 2026-09-01 19:08:10 | ws2Mage 49.3883, no |
| branch B fires | 2026-09-01 19:08:10 | counter cascade and ws2Mage not past 50 - end the trade, rev-trade on the next bar |

| saviour's candidate | value |
|---|---|
| would open | 2026-09-01 19:08:15 |
| detail | fill 2026-09-01 19:08:10 |

### core

| the step | the bar | the reading |
|---|---|---|
| ws3 is the rider and reverses | 2026-09-01 23:51:05 | ws3r 90.82, knowable 2026-09-01 23:51:40 |
| ws3 walks to ib, dwell 7 bars | 2026-09-01 23:54:30 | crossed 2026-09-01 23:54:00, dwell proven 7 bars = 35 s |
| ws3 -> ws4, the receiver gate | 2026-09-01 23:54:30 | ws4r 100.00, ex-fence YES |
| ws4 has no oob-anchored reversal in the data | 2026-09-01 23:54:30 | not knowable at this bar - NO REVERSAL, no trade |

| core's candidate | value |
|---|---|
| would open | none |
| detail | NO REVERSAL from ws3, arm 2026-09-01 23:48:00 |

### backstop

| the step | the bar | the reading |
|---|---|---|
| ws4 is the rider and reverses | 2026-09-01 19:32:10 | ws4r 91.17, knowable 2026-09-01 19:32:45 |
| ws4 walks to ib, dwell 10 bars | 2026-09-01 19:39:00 | crossed 2026-09-01 19:38:15, dwell proven 10 bars = 50 s |
| ws4 -> ws5, the receiver gate | 2026-09-01 19:39:00 | ws5r 80.37, ex-fence YES |
| ws5 takes the baton | 2026-09-01 19:39:00 | its reversal 2026-09-01 19:32:10 knowable 2026-09-01 19:32:45, below the ws6 lookback floor - no lookback test |
| the normal path | 2026-09-01 19:39:00 | ws5 waits for its own reversal |
| ws5 reverses | 2026-09-01 19:32:10 | ws5r 92.40, knowable 2026-09-01 19:32:45 |
| ws5 walks to ib, dwell 12 bars | 2026-09-01 19:39:10 | crossed 2026-09-01 19:38:15, dwell proven 12 bars = 60 s |
| ws5 -> ws6, the receiver gate | 2026-09-01 19:39:10 | ws6r 88.83, ex-fence YES |
| ws6 takes the baton | 2026-09-01 19:39:10 | its reversal 2026-09-01 19:32:30 knowable 2026-09-01 19:33:05, FOUND in its lookback |
| the SECOND walk to ib on ws6 | 2026-09-01 19:43:10 | dwell 15 bars, held 15 bars = 75 s |
| ws6 -> ws7, the receiver gate | 2026-09-01 19:43:10 | ws7r 76.86, not ex-fence - EXHAUST |

| backstop's candidate | value |
|---|---|
| would open | 2026-09-01 19:43:15 |
| detail | fire 2026-09-01 19:32:45, ws4, exh 2026-09-01 19:43:10, SHORT |

