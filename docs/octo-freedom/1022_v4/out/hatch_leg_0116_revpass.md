# THE MACHINE, mode 'trace'. 2026-09-01 00:00:00 .. 2026-09-03 23:59:55
# order 'saviour,core,backstop', backstop fallback 'drop'. ONE position at a time.
# LIN_PASS 'reversal', lookback floor ON at ws6, 39 backstop fires. RULED_OK False.

| the invisible trade | its target-side | the real trade it opens | detail |
|---|---|---|---|
| an invisible LONG | high | 2026-09-01 00:43:25 | cws1b 2026-09-01 00:04:00, arm 2026-09-01 00:26:00, ws2, exh 2026-09-01 00:43:20 |
| an invisible SHORT | low | 2026-09-01 02:24:45 | cws1b 2026-09-01 01:07:00, arm 2026-09-01 02:12:00, ws3, exh 2026-09-01 02:24:40 |

## the leg holding 2026-09-01 01:35:30: a SHORT opened 2026-09-01 00:43:25, target-side low

### saviour

| the step | the bar | the reading |
|---|---|---|
| the open | 2026-09-01 00:43:25 | ws5r 64.61, target-side low |
| the arm, ws5r oob on the COUNTER-TARGET side (high) | 2026-09-01 00:43:25 | ws5r oob no -> armed |
| the cap | 2026-09-01 00:43:25 to 2026-09-01 00:59:25 | 192 bars = 16 min from the open |
| the first ws1r oob run | 2026-09-01 00:55:00 to 2026-09-01 00:59:50 | 59 bars, peak 12.46, 1 run(s) inside the cap |
| the ws1r oob->ib cross | 2026-09-01 01:00:00 | ws1r 34.91, past the cap at 2026-09-01 00:59:25 - the trade stays open |

| saviour's candidate | value |
|---|---|
| would open | none |
| detail | STAYS OPEN |

### core

| the step | the bar | the reading |
|---|---|---|
| ws3 is the rider and reverses | 2026-09-01 02:19:50 | ws3r 7.74, knowable 2026-09-01 02:20:25 |
| the baton passes ON ws3 reversing | 2026-09-01 02:20:25 | his 1022 rule - no ib walk on the normal path |
| ws3 -> ws4, the receiver gate | 2026-09-01 02:20:25 | ws4r 3.71, ex-fence YES |
| ws4 takes the baton | 2026-09-01 02:20:25 | its reversal 2026-09-01 02:23:20 knowable 2026-09-01 02:23:55, below the ws6 lookback floor - no lookback test |
| the normal path | 2026-09-01 02:20:25 | ws4 waits for its own reversal |
| ws4 reverses | 2026-09-01 02:23:20 | ws4r 6.21, knowable 2026-09-01 02:23:55 |
| the baton passes ON ws4 reversing | 2026-09-01 02:23:55 | his 1022 rule - no ib walk on the normal path |
| ws4 -> ws5, the receiver gate | 2026-09-01 02:23:55 | ws5r 13.23, ex-fence YES |
| ws5 takes the baton | 2026-09-01 02:23:55 | its reversal 2026-09-01 02:24:05 knowable 2026-09-01 02:24:40, below the ws6 lookback floor - no lookback test |
| the normal path | 2026-09-01 02:23:55 | ws5 waits for its own reversal |
| ws5 reverses | 2026-09-01 02:24:05 | ws5r 12.99, knowable 2026-09-01 02:24:40 |
| the baton passes ON ws5 reversing | 2026-09-01 02:24:40 | his 1022 rule - no ib walk on the normal path |
| ws5 -> ws6, the receiver gate | 2026-09-01 02:24:40 | ws6r 27.50, not ex-fence - EXHAUST |

| core's candidate | value |
|---|---|
| would open | 2026-09-01 02:24:45 |
| detail | cws1b 2026-09-01 01:07:00, arm 2026-09-01 02:12:00, ws3, exh 2026-09-01 02:24:40 |

### backstop

| the step | the bar | the reading |
|---|---|---|
| ws4 is the rider and reverses | 2026-09-01 01:16:20 | ws4r 6.91, knowable 2026-09-01 01:16:55 |
| the baton passes ON ws4 reversing | 2026-09-01 01:16:55 | his 1022 rule - no ib walk on the normal path |
| ws4 -> ws5, the receiver gate | 2026-09-01 01:16:55 | ws5r 3.85, ex-fence YES |
| ws5 takes the baton | 2026-09-01 01:16:55 | its reversal 2026-09-01 01:16:20 knowable 2026-09-01 01:16:55, below the ws6 lookback floor - no lookback test |
| the normal path | 2026-09-01 01:16:55 | ws5 waits for its own reversal |
| ws5 reverses | 2026-09-01 01:16:20 | ws5r 3.47, knowable 2026-09-01 01:16:55 |
| the baton passes ON ws5 reversing | 2026-09-01 01:16:55 | his 1022 rule - no ib walk on the normal path |
| ws5 -> ws6, the receiver gate | 2026-09-01 01:16:55 | ws6r 6.93, ex-fence YES |
| ws6 takes the baton | 2026-09-01 01:16:55 | its reversal 2026-09-01 01:34:00 knowable 2026-09-01 01:34:35, not yet in its lookback |
| the normal path | 2026-09-01 01:16:55 | ws6 waits for its own reversal |
| ws6 reverses | 2026-09-01 01:34:00 | ws6r 5.25, knowable 2026-09-01 01:34:35 |
| the baton passes ON ws6 reversing | 2026-09-01 01:34:35 | his 1022 rule - no ib walk on the normal path |
| ws6 -> ws7, the receiver gate | 2026-09-01 01:34:35 | ws7r 3.96, ex-fence YES |
| ws7 takes the baton | 2026-09-01 01:34:35 | its reversal 2026-09-01 01:18:40 knowable 2026-09-01 01:19:15, FOUND in its lookback |
| the SECOND walk to ib on ws7 | 2026-09-01 01:39:20 | dwell 17 bars, held 17 bars = 85 s |
| ws7 -> ws8, the receiver gate | 2026-09-01 01:39:20 | ws8r 18.54, ex-fence YES |
| ws8 is the second-new-rider | 2026-09-01 01:39:20 | its reversal 2026-09-01 01:34:45 knowable 2026-09-01 01:35:20, FOUND in its lookback |
| EXHAUST | 2026-09-01 01:39:20 | the second-new-rider carried a reversal too |

| backstop's candidate | value |
|---|---|
| would open | 2026-09-01 01:39:25 |
| detail | fire 2026-09-01 01:16:55, ws4, exh 2026-09-01 01:39:20, LONG |

