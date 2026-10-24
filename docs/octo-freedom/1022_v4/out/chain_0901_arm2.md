# THE MACHINE, mode 'chain'. 2026-09-01 00:00:00 .. 2026-09-01 23:59:55
# order 'saviour,core,backstop', backstop fallback 'drop'. ONE position at a time.
# LIN_PASS 'ib', lookback floor ON at ws6, 6 backstop fires. RULED_OK True.

| the invisible trade | its target-side | the real trade it opens | detail |
|---|---|---|---|
| an invisible LONG | high | 2026-09-01 00:33:05 | cws1b 2026-09-01 00:04:00, step2 arm 2026-09-01 00:26:00, ws2, exh 2026-09-01 00:33:00 |
| an invisible SHORT | low | 2026-09-01 01:37:15 | cws1b 2026-09-01 01:07:00, arm2 arm 2026-09-01 01:14:25, ws4, exh 2026-09-01 01:37:10 |

| # | the open | dir | by | detail |
|---|---|---|---|---|
| 1 | 2026-09-01 00:33:05 | SHORT | core STEP0 | cws1b 2026-09-01 00:04:00, step2 arm 2026-09-01 00:26:00, ws2, exh 2026-09-01 00:33:00 |
| 2 | 2026-09-01 01:37:15 | LONG | core | cws1b 2026-09-01 01:07:00, arm2 arm 2026-09-01 01:14:25, ws4, exh 2026-09-01 01:37:10 |
| 3 | 2026-09-01 03:34:30 | SHORT | core | cws1b 2026-09-01 03:15:00, arm2 arm 2026-09-01 03:34:25, ws4 NOT oob - immediate exhaust |
| 4 | 2026-09-01 06:57:30 | LONG | core | cws1b 2026-09-01 04:57:00, arm2 arm 2026-09-01 06:57:25, ws4 NOT oob - immediate exhaust |
| 5 | 2026-09-01 07:29:05 | SHORT | core | cws1b 2026-09-01 07:23:00, step2 arm 2026-09-01 07:23:00, ws3, exh 2026-09-01 07:29:00 |
| 6 | 2026-09-01 08:16:05 | LONG | core | cws1b 2026-09-01 08:06:00, step2 arm 2026-09-01 08:08:00, ws2, exh 2026-09-01 08:16:00 |
| 7 | 2026-09-01 10:07:35 | SHORT | backstop | fire 2026-09-01 09:49:35, ws5, exh 2026-09-01 10:07:30, SHORT |
| 8 | 2026-09-01 13:14:35 | LONG | core | cws1b 2026-09-01 12:36:00, step2 arm 2026-09-01 13:00:00, ws3, exh 2026-09-01 13:14:30 |
| 9 | 2026-09-01 13:50:30 | SHORT | core | cws1b 2026-09-01 13:31:00, arm2 arm 2026-09-01 13:50:25, ws4 NOT oob - immediate exhaust |
| 10 | 2026-09-01 15:15:15 | LONG | core | cws1b 2026-09-01 15:00:00, step2 arm 2026-09-01 15:02:00, ws2, exh 2026-09-01 15:15:10 |
| 11 | 2026-09-01 17:33:35 | SHORT | core | cws1b 2026-09-01 15:48:00, step2 arm 2026-09-01 17:30:00, ws3, exh 2026-09-01 17:33:30 |
| 12 | 2026-09-01 18:55:15 | LONG | core | cws1b 2026-09-01 17:59:00, step2 arm 2026-09-01 17:59:00, ws3, exh 2026-09-01 18:55:10 |
| 13 | 2026-09-01 19:43:15 | SHORT | backstop | fire 2026-09-01 19:32:45, ws4, exh 2026-09-01 19:43:10, SHORT |
| 14 | 2026-09-01 20:31:15 | LONG | core | cws1b 2026-09-01 19:57:00, step2 arm 2026-09-01 19:57:00, ws3, exh 2026-09-01 20:31:10 |
| - | - | - | the chain ends | saviour: NOT ARMED; core: NO REVERSAL from ws3, step2 arm 2026-09-01 23:48:00; backstop: no fire resolves |

| the read | value |
|---|---|
| trades | 14 |
| by core | 11 |
| by backstop | 2 |
| by core STEP0 | 1 |
