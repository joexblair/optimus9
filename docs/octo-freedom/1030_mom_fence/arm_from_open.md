# HIS ARM LIST - the first firing at or after each open, on the trade side
# gcws30b at or beyond (5.0, 95.0) held 6 bars = 30 s, AND ws1r oob, AND ws2r oob
# oob 15.0/85.0 | ws3r OUT | the ruled check passes: True

| his open | side | HIS arm | the gcws30b arm alone fires | the gap to his | gcws30b there | ws1r | ws2r |
|---|---|---|---|---|---|---|---|
| 2026-09-03 17:01:00 | LONG | 2026-09-03 17:16:00 | 2026-09-03 18:18:00 | +62.0 min | 102.49 | 90.89 | 92.04 |
| 2026-09-03 19:30:00 | SHORT | 2026-09-03 22:01:00 | 2026-09-03 22:13:00 | +12.0 min | 1.99 | 12.11 | 12.61 |
| 2026-09-03 23:24:00 | LONG | 2026-09-03 23:39:00 | 2026-09-03 23:38:00 | -1.0 min | 99.81 | 87.06 | 97.69 |
| 2026-09-03 23:43:00 | SHORT | 2026-09-04 00:07:00 | 2026-09-04 00:08:25 | +1.4 min | -14.15 | 1.61 | 14.79 |
| 2026-09-04 00:09:00 | LONG | 2026-09-04 00:36:00 | 2026-09-04 00:40:00 | +4.0 min | 91.72 | 86.37 | 89.29 |

| his open | side | HIS arm | the RACE fires | which condition | the gap to his | why |
|---|---|---|---|---|---|---|
| 2026-09-03 17:01:00 | LONG | 2026-09-03 17:16:00 | 2026-09-03 18:18:00 | gcws30b+ws1r+ws2r | +62.0 min | gcws30b 102.49 at or beyond the 5.0/95.0 fence, held 6 bars, + ws1r 90.89 + ws2r 92.04 oob |
| 2026-09-03 19:30:00 | SHORT | 2026-09-03 22:01:00 | 2026-09-03 19:56:00 | ws4r | -125.0 min | ws4r 11.81 oob |
| 2026-09-03 23:24:00 | LONG | 2026-09-03 23:39:00 | 2026-09-03 23:38:00 | gcws30b+ws1r+ws2r | -1.0 min | gcws30b 99.81 at or beyond the 5.0/95.0 fence, held 6 bars, + ws1r 87.06 + ws2r 97.69 oob |
| 2026-09-03 23:43:00 | SHORT | 2026-09-04 00:07:00 | 2026-09-04 00:08:25 | gcws30b+ws1r+ws2r | +1.4 min | gcws30b -14.15 at or beyond the 5.0/95.0 fence, held 6 bars, + ws1r 1.61 + ws2r 14.79 oob |
| 2026-09-04 00:09:00 | LONG | 2026-09-04 00:36:00 | 2026-09-04 00:40:00 | gcws30b+ws1r+ws2r | +4.0 min | gcws30b 91.72 at or beyond the 5.0/95.0 fence, held 6 bars, + ws1r 86.37 + ws2r 89.29 oob |
