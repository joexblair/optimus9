# HIS ARM LIST - the first firing at or after each open, on the trade side
# gcws30b at or beyond (5.0, 95.0) held 6 bars = 30 s, AND (ws1r oob OR ws2r oob)
# oob 15.0/85.0 | ws3r OUT | the ruled check passes: True

| his open | side | HIS arm | the gcws30b arm alone fires | the gap to his | gcws30b there | ws1r | ws2r |
|---|---|---|---|---|---|---|---|
| 2026-09-03 01:36:05 | SHORT | 2026-09-03 04:37:55 | 2026-09-03 05:20:40 | +42.8 min | 1.76 | 26.66 | 4.33 |
| 2026-09-03 17:01:00 | LONG | 2026-09-03 17:16:00 | 2026-09-03 17:17:25 | +1.4 min | 118.92 | 86.66 | 79.69 |
| 2026-09-03 19:30:00 | SHORT | 2026-09-03 22:01:00 | 2026-09-03 20:00:35 | -120.4 min | -0.55 | 47.68 | 8.32 |
| 2026-09-03 23:24:00 | LONG | 2026-09-03 23:39:00 | 2026-09-03 23:30:00 | -9.0 min | 96.25 | 92.40 | 76.97 |
| 2026-09-03 23:43:00 | SHORT | 2026-09-04 00:07:00 | 2026-09-04 00:07:30 | +0.5 min | -22.12 | 10.71 | 17.06 |
| 2026-09-04 00:09:00 | LONG | 2026-09-04 00:36:00 | 2026-09-04 00:36:40 | +0.7 min | 101.14 | 92.34 | 61.76 |

| his open | side | HIS arm | the RACE fires | which condition | the gap to his | why |
|---|---|---|---|---|---|---|
| 2026-09-03 01:36:05 | SHORT | 2026-09-03 04:37:55 | 2026-09-03 03:24:00 | ws4r | -73.9 min | ws4r 8.52 oob |
| 2026-09-03 17:01:00 | LONG | 2026-09-03 17:16:00 | 2026-09-03 17:17:25 | gcws30b+(ws1r|ws2r) | +1.4 min | gcws30b 118.92 at or beyond the 5.0/95.0 fence, held 6 bars, + ws1r oob (ws1r 86.66, ws2r 79.69) |
| 2026-09-03 19:30:00 | SHORT | 2026-09-03 22:01:00 | 2026-09-03 19:56:00 | ws4r | -125.0 min | ws4r 11.81 oob |
| 2026-09-03 23:24:00 | LONG | 2026-09-03 23:39:00 | 2026-09-03 23:30:00 | gcws30b+(ws1r|ws2r) | -9.0 min | gcws30b 96.25 at or beyond the 5.0/95.0 fence, held 6 bars, + ws1r oob (ws1r 92.40, ws2r 76.97) |
| 2026-09-03 23:43:00 | SHORT | 2026-09-04 00:07:00 | 2026-09-04 00:07:30 | gcws30b+(ws1r|ws2r) | +0.5 min | gcws30b -22.12 at or beyond the 5.0/95.0 fence, held 6 bars, + ws1r oob (ws1r 10.71, ws2r 17.06) |
| 2026-09-04 00:09:00 | LONG | 2026-09-04 00:36:00 | 2026-09-04 00:36:40 | gcws30b+(ws1r|ws2r) | +0.7 min | gcws30b 101.14 at or beyond the 5.0/95.0 fence, held 6 bars, + ws1r oob (ws1r 92.34, ws2r 61.76) |
