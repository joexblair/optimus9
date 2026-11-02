# HIS ARM LIST - the first firing at or after each open, on the trade side
# gcws30b at or beyond (5.0, 95.0) held 6 bars = 30 s, AND (ws1r oob OR ws2r oob)
# oob 15.0/85.0 | ws3r OUT | the ruled check passes: True

| his open | side | HIS arm | the gcws30b arm alone fires | the gap to his | gcws30b there | ws1r | ws2r |
|---|---|---|---|---|---|---|---|
| 2026-09-03 01:36:05 | SHORT | 2026-09-03 04:37:55 | 2026-09-03 01:48:00 | -169.9 min | 4.37 | 24.60 | 14.58 |
| 2026-09-03 17:01:00 | LONG | 2026-09-03 17:16:00 | 2026-09-03 18:18:00 | +62.0 min | 107.51 | 90.89 | 92.04 |
| 2026-09-03 19:30:00 | SHORT | 2026-09-03 22:01:00 | 2026-09-03 20:00:55 | -120.1 min | 1.86 | 47.68 | 8.32 |
| 2026-09-03 23:24:00 | LONG | 2026-09-03 23:39:00 | 2026-09-03 23:30:00 | -9.0 min | 103.73 | 92.40 | 76.97 |
| 2026-09-03 23:43:00 | SHORT | 2026-09-04 00:07:00 | 2026-09-04 00:07:55 | +0.9 min | -43.33 | 10.71 | 17.06 |
| 2026-09-04 00:09:00 | LONG | 2026-09-04 00:36:00 | 2026-09-04 00:36:55 | +0.9 min | 99.72 | 92.34 | 61.76 |

| his open | side | HIS arm | the RACE fires | which condition | the gap to his | why |
|---|---|---|---|---|---|---|
| 2026-09-03 01:36:05 | SHORT | 2026-09-03 04:37:55 | 2026-09-03 01:48:00 | gcws30b+(ws1r|ws2r) | -169.9 min | gcws30b 4.37 at or beyond the 5.0/95.0 fence, held 6 bars, + ws2r oob (ws1r 24.60, ws2r 14.58) |
| 2026-09-03 17:01:00 | LONG | 2026-09-03 17:16:00 | 2026-09-03 18:18:00 | gcws30b+(ws1r|ws2r) | +62.0 min | gcws30b 107.51 at or beyond the 5.0/95.0 fence, held 6 bars, + ws1r and ws2r oob (ws1r 90.89, ws2r 92.04) |
| 2026-09-03 19:30:00 | SHORT | 2026-09-03 22:01:00 | 2026-09-03 19:56:00 | ws4r | -125.0 min | ws4r 11.81 oob |
| 2026-09-03 23:24:00 | LONG | 2026-09-03 23:39:00 | 2026-09-03 23:30:00 | gcws30b+(ws1r|ws2r) | -9.0 min | gcws30b 103.73 at or beyond the 5.0/95.0 fence, held 6 bars, + ws1r oob (ws1r 92.40, ws2r 76.97) |
| 2026-09-03 23:43:00 | SHORT | 2026-09-04 00:07:00 | 2026-09-04 00:07:55 | gcws30b+(ws1r|ws2r) | +0.9 min | gcws30b -43.33 at or beyond the 5.0/95.0 fence, held 6 bars, + ws1r oob (ws1r 10.71, ws2r 17.06) |
| 2026-09-04 00:09:00 | LONG | 2026-09-04 00:36:00 | 2026-09-04 00:36:55 | gcws30b+(ws1r|ws2r) | +0.9 min | gcws30b 99.72 at or beyond the 5.0/95.0 fence, held 6 bars, + ws1r oob (ws1r 92.34, ws2r 61.76) |
