# THE MACHINE, mode 'chain'. 2026-09-01 00:00:00 .. 2026-09-01 23:59:55
# order 'saviour,core,backstop', backstop fallback 'drop'. ONE position at a time.
# LIN_PASS 'ib', lookback floor ON at ws6, 6 backstop fires. RULED_OK True.

| the invisible trade | its target-side | the real trade it opens | detail |
|---|---|---|---|
| an invisible LONG | high | 2026-09-01 00:33:05 | cws1b 2026-09-01 00:04:00, arm 2026-09-01 00:26:00, ws2, exh 2026-09-01 00:33:00 |
| an invisible SHORT | low | 2026-09-01 02:25:25 | cws1b 2026-09-01 01:07:00, arm 2026-09-01 02:12:00, ws3, exh 2026-09-01 02:25:20 |

| # | the open | dir | by | detail |
|---|---|---|---|---|
| 1 | 2026-09-01 00:33:05 | SHORT | core STEP0 | cws1b 2026-09-01 00:04:00, arm 2026-09-01 00:26:00, ws2, exh 2026-09-01 00:33:00 |
| 2 | 2026-09-01 01:37:15 | LONG | backstop | fire 2026-09-01 01:16:55, ws4, exh 2026-09-01 01:37:10, LONG |
| 3 | 2026-09-01 04:29:00 | SHORT | core | cws1b 2026-09-01 03:15:00, arm 2026-09-01 04:26:00, ws2, exh 2026-09-01 04:28:55 |
| 4 | 2026-09-01 04:41:50 | LONG | saviour | fill 2026-09-01 04:41:45 |
| 5 | 2026-09-01 05:46:35 | SHORT | core | cws1b 2026-09-01 05:04:00, arm 2026-09-01 05:36:00, ws2, exh 2026-09-01 05:46:30 |
| 6 | 2026-09-01 05:52:25 | LONG | saviour | fill 2026-09-01 05:52:20 |
| 7 | 2026-09-01 07:29:05 | SHORT | core | cws1b 2026-09-01 07:23:00, arm 2026-09-01 07:23:05, ws3, exh 2026-09-01 07:29:00 |
| 8 | 2026-09-01 08:16:05 | LONG | core | cws1b 2026-09-01 08:06:00, arm 2026-09-01 08:08:00, ws2, exh 2026-09-01 08:16:00 |
| 9 | 2026-09-01 10:07:35 | SHORT | backstop | fire 2026-09-01 09:49:35, ws5, exh 2026-09-01 10:07:30, SHORT |
| 10 | 2026-09-01 13:14:35 | LONG | core | cws1b 2026-09-01 12:36:00, arm 2026-09-01 13:00:00, ws3, exh 2026-09-01 13:14:30 |
| 11 | 2026-09-01 14:17:40 | SHORT | backstop | fire 2026-09-01 13:37:15, ws4, exh 2026-09-01 14:17:35, SHORT |
| 12 | 2026-09-01 15:15:15 | LONG | core | cws1b 2026-09-01 15:00:00, arm 2026-09-01 15:02:00, ws2, exh 2026-09-01 15:15:10 |
| 13 | 2026-09-01 17:33:35 | SHORT | core | cws1b 2026-09-01 15:48:00, arm 2026-09-01 17:30:00, ws3, exh 2026-09-01 17:33:30 |
| 14 | 2026-09-01 18:55:15 | LONG | core | cws1b 2026-09-01 17:59:00, arm 2026-09-01 17:59:05, ws3, exh 2026-09-01 18:55:10 |
| 15 | 2026-09-01 19:08:15 | SHORT | saviour | fill 2026-09-01 19:08:10 |
| 16 | 2026-09-01 20:31:15 | LONG | core | cws1b 2026-09-01 19:57:00, arm 2026-09-01 19:57:05, ws3, exh 2026-09-01 20:31:10 |
| - | - | - | the chain ends | saviour: STAYS OPEN; core: NO REVERSAL from ws3, arm 2026-09-01 23:48:00; backstop: no fire resolves |

| the read | value |
|---|---|
| trades | 16 |
| by core | 9 |
| by backstop | 3 |
| by saviour | 3 |
| by core STEP0 | 1 |
