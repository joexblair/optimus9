# THE MACHINE, mode 'chain'. 2026-09-01 00:00:00 .. 2026-09-01 23:59:55
# order 'saviour,core,backstop', backstop fallback 'drop'. ONE position at a time.
# LIN_PASS 'ib', lookback floor ON at ws6, 19 backstop fires. RULED_OK False.

| the invisible trade | its target-side | the real trade it opens | detail |
|---|---|---|---|
| an invisible LONG | high | 2026-09-01 00:33:15 | cws1b 2026-09-01 00:04:00, arm 2026-09-01 00:26:00, ws2, exh 2026-09-01 00:33:10 |
| an invisible SHORT | low | 2026-09-01 02:40:45 | cws1b 2026-09-01 01:07:00, arm 2026-09-01 02:12:00, ws3, exh 2026-09-01 02:40:40 |

| # | the open | dir | by | detail |
|---|---|---|---|---|
| 1 | 2026-09-01 00:33:15 | SHORT | core STEP0 | cws1b 2026-09-01 00:04:00, arm 2026-09-01 00:26:00, ws2, exh 2026-09-01 00:33:10 |
| 2 | 2026-09-01 01:37:15 | LONG | backstop | fire 2026-09-01 01:16:55, ws4, exh 2026-09-01 01:37:10, LONG |
| 3 | 2026-09-01 03:25:20 | SHORT | backstop | fire 2026-09-01 03:13:55, ws5, exh 2026-09-01 03:25:15, SHORT |
| 4 | 2026-09-01 07:03:00 | LONG | core | cws1b 2026-09-01 04:57:00, arm 2026-09-01 06:58:00, ws2, exh 2026-09-01 07:02:55 |
| 5 | 2026-09-01 07:28:50 | SHORT | core | cws1b 2026-09-01 07:23:00, arm 2026-09-01 07:23:05, ws3, exh 2026-09-01 07:28:45 |
| 6 | 2026-09-01 08:31:15 | LONG | core | cws1b 2026-09-01 08:06:00, arm 2026-09-01 08:08:00, ws2, exh 2026-09-01 08:31:10 |
| 7 | 2026-09-01 10:07:35 | SHORT | backstop | fire 2026-09-01 09:49:35, ws5, exh 2026-09-01 10:07:30, SHORT |
| 8 | 2026-09-01 11:26:25 | LONG | backstop | fire 2026-09-01 11:17:30, ws5, exh 2026-09-01 11:26:20, LONG |
| 9 | 2026-09-01 11:31:15 | SHORT | core | cws1b 2026-09-01 11:26:25, arm 2026-09-01 11:26:30, ws2, exh 2026-09-01 11:31:10 |
| 10 | 2026-09-01 13:05:20 | LONG | core | cws1b 2026-09-01 12:36:00, arm 2026-09-01 13:00:00, ws3, exh 2026-09-01 13:05:15 |
| 11 | 2026-09-01 13:10:20 | SHORT | saviour | fill 2026-09-01 13:10:15 |
| 12 | 2026-09-01 14:19:15 | LONG | backstop | fire 2026-09-01 13:37:15, ws4, exh 2026-09-01 14:19:10, SHORT |
| 13 | 2026-09-01 17:41:00 | SHORT | core | cws1b 2026-09-01 15:48:00, arm 2026-09-01 17:30:00, ws3, exh 2026-09-01 17:40:55 |
| 14 | 2026-09-01 18:14:45 | LONG | core | cws1b 2026-09-01 17:59:00, arm 2026-09-01 17:59:05, ws3, exh 2026-09-01 18:14:40 |
| 15 | 2026-09-01 19:43:15 | SHORT | backstop | fire 2026-09-01 19:15:35, ws4, exh 2026-09-01 19:43:10, SHORT |
| 16 | 2026-09-01 20:04:55 | LONG | core | cws1b 2026-09-01 19:57:00, arm 2026-09-01 19:57:05, ws3, exh 2026-09-01 20:04:50 |
| - | - | - | the chain ends | saviour: NOT ARMED; core: NO REVERSAL from ws3, arm 2026-09-01 23:48:00; backstop: no fire resolves |

| the read | value |
|---|---|
| trades | 16 |
| by core | 8 |
| by backstop | 6 |
| by core STEP0 | 1 |
| by saviour | 1 |
