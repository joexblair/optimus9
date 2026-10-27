# THE MACHINE, mode 'trace'. 2026-09-01 00:00:00 .. 2026-09-01 23:59:55
# order 'saviour,core,backstop', backstop fallback 'drop'. ONE position at a time.
# LIN_PASS 'ib', lookback floor ON at ws6, 6 backstop fires. RULED_OK False.

| the invisible trade | its target-side | the real trade it opens | detail |
|---|---|---|---|
| an invisible LONG | high | 2026-09-01 00:33:05 | cws1b 2026-09-01 00:04:00, step2 arm 2026-09-01 00:26:00, ws2, exh 2026-09-01 00:33:00 |
| an invisible SHORT | low | 2026-09-01 02:25:25 | cws1b 2026-09-01 01:07:00, step2 arm 2026-09-01 02:12:00, ws3, exh 2026-09-01 02:25:20 |

## the leg holding 2026-09-01 04:35:00: a SHORT opened 2026-09-01 04:29:00, target-side low

### saviour

| the step | the bar | the reading |
|---|---|---|
| the open | 2026-09-01 04:29:00 | ws5r 41.91, target-side low |
| the arm walkback, 30 min, the COUNTER-TARGET side (high) extremum | 2026-09-01 03:59:00 to 2026-09-01 04:29:00 | ws5r 41.91 at 2026-09-01 04:25:10, oob no -> armed |
| the cap | 2026-09-01 04:29:00 to 2026-09-01 04:45:00 | 192 bars = 16 min from the open |
| the first ws1r oob run | 2026-09-01 04:33:05 to 2026-09-01 04:34:10 | 14 bars, peak 13.91, 2 run(s) inside the cap |
| the ws1r oob run that crossed | 2026-09-01 04:33:05 to 2026-09-01 04:34:10 | 14 bars, peak 13.91 |
| the ws1r oob->ib cross | 2026-09-01 04:34:20 | ws1r 16.67, held 2 bars |
| the ws1r lift-off | 2026-09-01 04:25:35 | stamped 2026-09-01 04:26:10, 490 s before the cross |
| the cascade at the stamp | 2026-09-01 04:26:10 | neither | neither | the low cluster ws1 to ws3, 3 lines, falling | the high cluster ws10 to ws12, 3 lines, falling | the end-to-end diff +62.69 | zoom 2 rungs, min 4 lines |
| ws1Mage past 50 towards the target-side | 2026-09-01 04:34:20 | ws1Mage 74.2187, no |
| branch A does not fire - branch B | 2026-09-01 04:34:20 | the cascade is not counter. walk to ws2r oob, inside the cap to 2026-09-01 04:45:00 |
| ws1Mage left the past-50 gate | 2026-09-01 04:41:45 | held 8 bars = 40 s, ws1Mage 53.8548 at the stamp |
| the ws1Mage target-side extrema anchor | 2026-09-01 04:39:55 | ws1Mage 28.7787, 110 s before the stamp |
| the routed cascade at the anchor | 2026-09-01 04:39:55 | up | up | the low cluster ws1 to ws5, 5 lines, rising COUNTS | the high cluster ws10 to ws12, 3 lines, falling | the end-to-end diff -11.03 | zoom 2 rungs, min 4 lines |
| the route fires | 2026-09-01 04:41:45 | counter cascade and ws1Mage outside the gate - end the trade, rev-trade on the next bar |

| saviour's candidate | value |
|---|---|
| would open | 2026-09-01 04:41:50 |
| detail | fill 2026-09-01 04:41:45 |

### core

| the step | the bar | the reading |
|---|---|---|
| ws2 is the rider and reverses | 2026-09-01 07:00:05 | ws2r 14.14, knowable 2026-09-01 07:00:40 |
| ws2 walks to ib, dwell 5 bars | 2026-09-01 07:01:30 | crossed 2026-09-01 07:01:10, dwell proven 5 bars = 25 s |
| ws2 -> ws3, the receiver gate | 2026-09-01 07:01:30 | ws3r 15.71, ex-fence YES |
| ws3 takes the baton | 2026-09-01 07:01:30 | its reversal 2026-09-01 07:01:10 knowable 2026-09-01 07:01:45, below the ws6 lookback floor - no lookback test |
| the normal path | 2026-09-01 07:01:30 | ws3 waits for its own reversal |
| ws3 reverses | 2026-09-01 07:01:10 | ws3r 13.95, knowable 2026-09-01 07:01:45 |
| ws3 walks to ib, dwell 7 bars | 2026-09-01 07:02:40 | crossed 2026-09-01 07:02:10, dwell proven 7 bars = 35 s |
| ws3 -> ws4, the receiver gate | 2026-09-01 07:02:40 | ws4r 27.57, not ex-fence - EXHAUST |

| core's candidate | value |
|---|---|
| would open | 2026-09-01 07:02:45 |
| detail | cws1b 2026-09-01 04:57:00, step2 arm 2026-09-01 06:58:00, ws2, exh 2026-09-01 07:02:40 |

### backstop

| the step | the bar | the reading |
|---|---|---|
| - | - | no fire resolves |

| backstop's candidate | value |
|---|---|
| would open | none |
| detail | no fire resolves |

