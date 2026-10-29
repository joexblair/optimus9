# THE ws1b CROSSINGS, JUDGED ONLY ON BARS AT OR BEFORE EACH ONE
# ws1b is the live read. the line is 85.

| the read | value |
|---|---|
| crossings in, 2026-08-29 23:50:00 to 23:57:00 | 2 |
| crossing 1 | 2026-08-29 23:53:50, ws1b 81.82, previous bar 85.19 |
| crossing 2 | 2026-08-29 23:56:00, ws1b 82.65, previous bar 86.75 |

## each crossing, per hold, using only the bars inside its own hold window

| the crossing | the hold | the window it reads | every bar under 85? | confirmed at | the values in the window |
|---|---|---|---|---|---|
| 2026-08-29 23:53:50 | 1 bar = 5 s | 2026-08-29 23:53:50 .. 2026-08-29 23:53:50 | yes | 2026-08-29 23:53:50 | 81.82 |
| 2026-08-29 23:53:50 | 3 bars = 15 s | 2026-08-29 23:53:50 .. 2026-08-29 23:54:00 | yes | 2026-08-29 23:54:00 | 81.82, 81.82, 81.24 |
| 2026-08-29 23:53:50 | 12 bars = 60 s | 2026-08-29 23:53:50 .. 2026-08-29 23:54:45 | yes | 2026-08-29 23:54:45 | 81.82, 81.82, 81.24, 80.76, 80.76, 80.76, 78.34, 78.34, 78.34, 78.34, 77.86, 77.86 |
| 2026-08-29 23:56:00 | 1 bar = 5 s | 2026-08-29 23:56:00 .. 2026-08-29 23:56:00 | yes | 2026-08-29 23:56:00 | 82.65 |
| 2026-08-29 23:56:00 | 3 bars = 15 s | 2026-08-29 23:56:00 .. 2026-08-29 23:56:10 | yes | 2026-08-29 23:56:10 | 82.65, 78.92, 78.92 |
| 2026-08-29 23:56:00 | 12 bars = 60 s | 2026-08-29 23:56:00 .. 2026-08-29 23:56:55 | yes | 2026-08-29 23:56:55 | 82.65, 78.92, 78.92, 78.92, 77.03, 77.03, 77.03, 77.03, 77.03, 77.03, 77.03, 77.03 |

| the read | value |
|---|---|
| what a 1-bar hold needs | the crossing bar itself |
| what a 3-bar hold needs | the crossing bar and the 2 after it |
| what a 12-bar hold needs | the crossing bar and the 11 after it |
| what NONE of them needs | any bar beyond the hold window |
