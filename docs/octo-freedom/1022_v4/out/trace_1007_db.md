# THE MACHINE, mode 'trace'. 2026-09-01 00:00:00 .. 2026-09-01 23:59:55
# order 'saviour,core,backstop', backstop fallback 'drop'. ONE position at a time.
# LIN_PASS 'ib', lookback floor ON at ws6, 6 backstop fires. RULED_OK True.

| the invisible trade | its target-side | the real trade it opens | detail |
|---|---|---|---|
| an invisible LONG | high | 2026-09-01 00:33:05 | cws1b 2026-09-01 00:04:00, arm 2026-09-01 00:26:00, ws2, exh 2026-09-01 00:33:00 |
| an invisible SHORT | low | 2026-09-01 02:25:25 | cws1b 2026-09-01 01:07:00, arm 2026-09-01 02:12:00, ws3, exh 2026-09-01 02:25:20 |

## the leg holding 2026-09-01 09:00:00: a LONG opened 2026-09-01 08:16:05, target-side high

### saviour

| the step | the bar | the reading |
|---|---|---|
| the open | 2026-09-01 08:16:05 | ws5r 16.05, target-side high |
| the arm, ws5r oob on the COUNTER-TARGET side (low) | 2026-09-01 08:16:05 | ws5r oob no -> armed |
| the cap | 2026-09-01 08:16:05 to 2026-09-01 08:32:05 | 192 bars = 16 min from the open |
| no ws1r oob run on the target-side inside the cap | 2026-09-01 08:32:05 | the cap expired - the trade stays open |

| saviour's candidate | value |
|---|---|
| would open | none |
| detail | STAYS OPEN |

### core

| the step | the bar | the reading |
|---|---|---|
| ws2 is the rider and reverses | 2026-09-01 10:25:35 | ws2r 86.07, knowable 2026-09-01 10:26:10 |
| ws2 walks to ib, dwell 5 bars | 2026-09-01 10:26:30 | crossed 2026-09-01 10:26:10, dwell proven 5 bars = 25 s |
| ws2 -> ws3, the receiver gate | 2026-09-01 10:26:30 | ws3r 66.32, not ex-fence - EXHAUST |

| core's candidate | value |
|---|---|
| would open | 2026-09-01 10:26:35 |
| detail | cws1b 2026-09-01 09:44:00, arm 2026-09-01 10:24:00, ws2, exh 2026-09-01 10:26:30 |

### backstop

| the step | the bar | the reading |
|---|---|---|
| ws5 is the rider and reverses | 2026-09-01 09:49:00 | ws5r 85.46, knowable 2026-09-01 09:49:35 |
| ws5 walks to ib, dwell 12 bars | 2026-09-01 09:50:55 | crossed 2026-09-01 09:50:00, dwell proven 12 bars = 60 s |
| ws5 -> ws6, the receiver gate | 2026-09-01 09:50:55 | ws6r 86.02, ex-fence YES |
| ws6 takes the baton | 2026-09-01 09:50:55 | its reversal 2026-09-01 09:59:45 knowable 2026-09-01 10:00:20, not yet in its lookback |
| the normal path | 2026-09-01 09:50:55 | ws6 waits for its own reversal |
| ws6 reverses | 2026-09-01 09:59:45 | ws6r 89.76, knowable 2026-09-01 10:00:20 |
| ws6 walks to ib, dwell 15 bars | 2026-09-01 10:03:30 | crossed 2026-09-01 10:02:20, dwell proven 15 bars = 75 s |
| ws6 -> ws7, the receiver gate | 2026-09-01 10:03:30 | ws7r 88.17, ex-fence YES |
| ws7 takes the baton | 2026-09-01 10:03:30 | its reversal 2026-09-01 09:59:50 knowable 2026-09-01 10:00:25, FOUND in its lookback |
| the SECOND walk to ib on ws7 | 2026-09-01 10:07:30 | dwell 17 bars, held 17 bars = 85 s |
| ws7 -> ws8, the receiver gate | 2026-09-01 10:07:30 | ws8r 93.59, ex-fence YES |
| ws8 is the second-new-rider | 2026-09-01 10:07:30 | its reversal 2026-09-01 10:04:25 knowable 2026-09-01 10:05:00, FOUND in its lookback |
| EXHAUST | 2026-09-01 10:07:30 | the second-new-rider carried a reversal too |

| backstop's candidate | value |
|---|---|
| would open | 2026-09-01 10:07:35 |
| detail | fire 2026-09-01 09:49:35, ws5, exh 2026-09-01 10:07:30, SHORT |

