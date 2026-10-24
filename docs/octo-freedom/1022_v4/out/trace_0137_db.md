# THE MACHINE, mode 'trace'. 2026-09-01 00:00:00 .. 2026-09-01 23:59:55
# order 'saviour,core,backstop', backstop fallback 'drop'. ONE position at a time.
# LIN_PASS 'ib', lookback floor ON at ws6, 6 backstop fires. RULED_OK True.

| the invisible trade | its target-side | the real trade it opens | detail |
|---|---|---|---|
| an invisible LONG | high | 2026-09-01 00:33:05 | cws1b 2026-09-01 00:04:00, arm 2026-09-01 00:26:00, ws2, exh 2026-09-01 00:33:00 |
| an invisible SHORT | low | 2026-09-01 02:25:25 | cws1b 2026-09-01 01:07:00, arm 2026-09-01 02:12:00, ws3, exh 2026-09-01 02:25:20 |

## the leg holding 2026-09-01 01:00:00: a SHORT opened 2026-09-01 00:33:05, target-side low

### saviour

| the step | the bar | the reading |
|---|---|---|
| the open | 2026-09-01 00:33:05 | ws5r 89.58, target-side low |
| the arm, ws5r oob on the COUNTER-TARGET side (high) | 2026-09-01 00:33:05 | ws5r oob YES -> NOT ARMED |

| saviour's candidate | value |
|---|---|
| would open | none |
| detail | NOT ARMED |

### core

| the step | the bar | the reading |
|---|---|---|
| ws3 is the rider and reverses | 2026-09-01 02:14:55 | ws3r 6.34, knowable 2026-09-01 02:15:30 |
| ws3 walks to ib, dwell 7 bars | 2026-09-01 02:21:30 | crossed 2026-09-01 02:21:00, dwell proven 7 bars = 35 s |
| ws3 -> ws4, the receiver gate | 2026-09-01 02:21:30 | ws4r 12.46, ex-fence YES |
| ws4 takes the baton | 2026-09-01 02:21:30 | its reversal 2026-09-01 02:23:20 knowable 2026-09-01 02:23:55, below the ws6 lookback floor - no lookback test |
| the normal path | 2026-09-01 02:21:30 | ws4 waits for its own reversal |
| ws4 reverses | 2026-09-01 02:23:20 | ws4r 11.96, knowable 2026-09-01 02:23:55 |
| ws4 walks to ib, dwell 10 bars | 2026-09-01 02:25:20 | crossed 2026-09-01 02:24:35, dwell proven 10 bars = 50 s |
| ws4 -> ws5, the receiver gate | 2026-09-01 02:25:20 | ws5r 29.55, not ex-fence - EXHAUST |

| core's candidate | value |
|---|---|
| would open | 2026-09-01 02:25:25 |
| detail | cws1b 2026-09-01 01:07:00, arm 2026-09-01 02:12:00, ws3, exh 2026-09-01 02:25:20 |

### backstop

| the step | the bar | the reading |
|---|---|---|
| ws4 is the rider and reverses | 2026-09-01 01:17:50 | ws4r 7.28, knowable 2026-09-01 01:18:25 |
| ws4 walks to ib, dwell 10 bars | 2026-09-01 01:20:45 | crossed 2026-09-01 01:20:00, dwell proven 10 bars = 50 s |
| ws4 -> ws5, the receiver gate | 2026-09-01 01:20:45 | ws5r 10.63, ex-fence YES |
| ws5 takes the baton | 2026-09-01 01:20:45 | its reversal 2026-09-01 01:16:20 knowable 2026-09-01 01:16:55, below the ws6 lookback floor - no lookback test |
| the normal path | 2026-09-01 01:20:45 | ws5 waits for its own reversal |
| ws5 reverses | 2026-09-01 01:16:20 | ws5r 11.57, knowable 2026-09-01 01:16:55 |
| ws5 walks to ib, dwell 12 bars | 2026-09-01 01:35:25 | crossed 2026-09-01 01:34:30, dwell proven 12 bars = 60 s |
| ws5 -> ws6, the receiver gate | 2026-09-01 01:35:25 | ws6r 11.28, ex-fence YES |
| ws6 takes the baton | 2026-09-01 01:35:25 | its reversal 2026-09-01 01:34:00 knowable 2026-09-01 01:34:35, FOUND in its lookback |
| the SECOND walk to ib on ws6 | 2026-09-01 01:37:10 | dwell 15 bars, held 15 bars = 75 s |
| ws6 -> ws7, the receiver gate | 2026-09-01 01:37:10 | ws7r 9.60, ex-fence YES |
| ws7 is the second-new-rider | 2026-09-01 01:37:10 | its reversal 2026-09-01 01:18:40 knowable 2026-09-01 01:19:15, FOUND in its lookback |
| EXHAUST | 2026-09-01 01:37:10 | the second-new-rider carried a reversal too |

| backstop's candidate | value |
|---|---|
| would open | 2026-09-01 01:37:15 |
| detail | fire 2026-09-01 01:16:55, ws4, exh 2026-09-01 01:37:10, LONG |

