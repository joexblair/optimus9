# v4_reentry A/B, 2026-08-28 00:00:00 .. 2026-08-29 23:59:55. base ws5Mage/cws5Mage, ladder to 12.
# the SPEC ladder is EMERGING; the CLOSED ladder is his 1026 experiment.

| the ladder | oob runs | median run | 1-bar runs | runs under 1 min | reentry signals | signals from runs under 1 min |
|---|---|---|---|---|---|---|
| EMERGING | 206 | 6 bars = 30 s | 41 | 138 | 53 | 44 |
| CLOSED | 35 | 120 bars = 600 s | 0 | 0 | 6 | 0 |

# HIS FOUR EXAMPLES, nearest run under each ladder

| his example | the ladder | the nearest ib cross | side | run length | verdict | gap |
|---|---|---|---|---|---|---|
| 2026-08-28 11:25:00 | EMERGING | 2026-08-28 11:26:10 | HIGH | 53 bars = 265 s | reentry | +70 s |
| 2026-08-28 11:25:00 | CLOSED | 2026-08-28 11:25:00 | HIGH | 120 bars = 600 s | reentry | +0 s |
| 2026-08-28 15:00:00 | EMERGING | 2026-08-28 14:58:35 | HIGH | 73 bars = 365 s | BLOCKED by ws6,7,8,9,10,11 | -85 s |
| 2026-08-28 15:00:00 | CLOSED | 2026-08-28 15:05:00 | HIGH | 180 bars = 900 s | BLOCKED by ws7,8,11 | +300 s |
| 2026-08-29 00:10:00 | EMERGING | 2026-08-29 00:13:15 | HIGH | 80 bars = 400 s | BLOCKED by ws6,7,8,9,10,11,12 | +195 s |
| 2026-08-29 00:10:00 | CLOSED | 2026-08-29 00:10:00 | HIGH | 180 bars = 900 s | BLOCKED by ws6,9,10 | +0 s |
| 2026-08-29 02:35:00 | EMERGING | 2026-08-29 02:38:35 | LOW | 262 bars = 1310 s | BLOCKED by ws6,7,8,9,10,11,12 | +215 s |
| 2026-08-29 02:35:00 | CLOSED | 2026-08-29 02:35:00 | LOW | 240 bars = 1200 s | BLOCKED by ws6,7,10,11,12 | +0 s |

# THE CLOSED LADDER'S SIGNALS

| the SIGNAL | side | the oob run from | to | run length |
|---|---|---|---|---|
| 2026-08-28 05:50:00 | HIGH | 2026-08-28 05:40:00 | 2026-08-28 05:49:55 | 120 bars = 600 s |
| 2026-08-28 07:55:00 | LOW | 2026-08-28 07:50:00 | 2026-08-28 07:54:55 | 60 bars = 300 s |
| 2026-08-28 11:25:00 | HIGH | 2026-08-28 11:15:00 | 2026-08-28 11:24:55 | 120 bars = 600 s |
| 2026-08-29 11:35:00 | HIGH | 2026-08-29 11:15:00 | 2026-08-29 11:34:55 | 240 bars = 1200 s |
| 2026-08-29 21:05:00 | LOW | 2026-08-29 21:00:10 | 2026-08-29 21:04:55 | 58 bars = 290 s |
| 2026-08-29 23:50:00 | HIGH | 2026-08-29 23:45:00 | 2026-08-29 23:49:55 | 60 bars = 300 s |
