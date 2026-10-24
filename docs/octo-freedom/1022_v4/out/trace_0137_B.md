# THE SIGNALS THAT LANDED ON 2026-09-01 01:37:10. Joe 1024.
# the producers are the router's own; each walk is re-run through v4_fast.walk's events
#   hook. RULED_OK False. the control: ws5r 2026-09-03 00:35:00 = 12.48, expected 12.48

| the signal | side | by | its walk started | detail |
|---|---|---|---|---|
| 2026-09-01 01:37:10 | LOW | core | 2026-09-01 01:14:25 | arm2 arm 01:14:25, ws4 |
| 2026-09-01 01:37:10 | LOW | backstop | 2026-09-01 01:16:20 | fire 01:16:55, ws4 |
| 2026-09-01 01:37:10 | LOW | backstop | 2026-09-01 01:18:05 | fire 01:18:40, ws4 |

## core LOW, walk from ws4 starting 2026-09-01 01:14:25 -> EXHAUST 2026-09-01 01:37:10

| the baton bar | from | to | the receiver r value | its reversal stamp | second walk |
|---|---|---|---|---|---|
| 2026-09-01 01:20:45 | ws4 | ws5 | 10.63 oob | 2026-09-01 01:16:55 | - |
| 2026-09-01 01:35:25 | ws5 | ws6 | 11.28 oob | 2026-09-01 01:34:35 | 2026-09-01 01:37:10 |

## backstop LOW, walk from ws4 starting 2026-09-01 01:16:20, fire 2026-09-01 01:16:55 -> EXHAUST 2026-09-01 01:37:10

| the baton bar | from | to | the receiver r value | its reversal stamp | second walk |
|---|---|---|---|---|---|
| 2026-09-01 01:20:45 | ws4 | ws5 | 10.63 oob | 2026-09-01 01:16:55 | - |
| 2026-09-01 01:35:25 | ws5 | ws6 | 11.28 oob | 2026-09-01 01:34:35 | 2026-09-01 01:37:10 |

## backstop LOW, walk from ws4 starting 2026-09-01 01:18:05, fire 2026-09-01 01:18:40 -> EXHAUST 2026-09-01 01:37:10

| the baton bar | from | to | the receiver r value | its reversal stamp | second walk |
|---|---|---|---|---|---|
| 2026-09-01 01:29:20 | ws4 | ws5 | 10.81 oob | 2026-09-01 01:18:40 | - |
| 2026-09-01 01:35:25 | ws5 | ws6 | 11.28 oob | 2026-09-01 01:34:35 | 2026-09-01 01:37:10 |

# THE 5-SECOND ROWS, 2026-09-01 01:14:25 .. 2026-09-01 01:37:10. r values on the SWEEP config (rsi 5, stc 8, k_len 7).
# a value is tagged against the LOW side, which is the side all these signals carry.

| the bar | ws1r | ws2r | ws3r | ws4r | ws5r | ws6r |
|---|---|---|---|---|---|---|
| 2026-09-01 01:14:25 | 10.14 oob | 21.11 in-fence | 15.74 ex-fence | 7.94 oob | 9.02 oob | 10.53 oob |
| 2026-09-01 01:14:30 | 9.19 oob | 21.11 in-fence | 15.74 ex-fence | 7.94 oob | 9.02 oob | 10.53 oob |
| 2026-09-01 01:14:35 | 9.46 oob | 21.11 in-fence | 15.74 ex-fence | 7.94 oob | 9.02 oob | 10.53 oob |
| 2026-09-01 01:14:40 | 9.19 oob | 21.11 in-fence | 15.74 ex-fence | 7.94 oob | 9.02 oob | 10.53 oob |
| 2026-09-01 01:14:45 | 9.84 oob | 21.11 in-fence | 15.74 ex-fence | 7.94 oob | 9.02 oob | 10.53 oob |
| 2026-09-01 01:14:50 | 10.46 oob | 21.11 in-fence | 15.74 ex-fence | 7.94 oob | 9.02 oob | 10.53 oob |
| 2026-09-01 01:14:55 | 12.08 oob | 21.57 in-fence | 15.74 ex-fence | 7.94 oob | 9.02 oob | 10.53 oob |
| 2026-09-01 01:15:00 | 14.58 oob | 22.87 in-fence | 16.98 ex-fence | 7.94 oob | 9.58 oob | 10.53 oob |
| 2026-09-01 01:15:05 | 16.87 ex-fence | 23.88 in-fence | 17.95 ex-fence | 7.94 oob | 10.03 oob | 10.53 oob |
| 2026-09-01 01:15:10 | 11.26 oob | 21.34 in-fence | 15.74 ex-fence | 7.94 oob | 9.02 oob | 10.53 oob |
| 2026-09-01 01:15:15 | 10.51 oob | 21.11 in-fence | 15.74 ex-fence | 7.94 oob | 9.02 oob | 10.53 oob |
| 2026-09-01 01:15:20 | 10.51 oob | 21.11 in-fence | 15.74 ex-fence | 7.94 oob | 9.02 oob | 10.53 oob |
| 2026-09-01 01:15:25 | 11.43 oob | 21.57 in-fence | 15.74 ex-fence | 7.94 oob | 9.02 oob | 10.53 oob |
| 2026-09-01 01:15:30 | 11.43 oob | 21.57 in-fence | 15.74 ex-fence | 7.94 oob | 9.02 oob | 10.53 oob |
| 2026-09-01 01:15:35 | 11.43 oob | 21.57 in-fence | 15.74 ex-fence | 7.94 oob | 9.02 oob | 10.53 oob |
| 2026-09-01 01:15:40 | 17.72 ex-fence | 24.26 in-fence | 18.33 ex-fence | 7.94 oob | 10.21 oob | 10.53 oob |
| 2026-09-01 01:15:45 | 15.99 ex-fence | 23.48 in-fence | 17.57 ex-fence | 7.94 oob | 9.85 oob | 10.53 oob |
| 2026-09-01 01:15:50 | 15.06 ex-fence | 23.08 in-fence | 17.18 ex-fence | 7.94 oob | 9.67 oob | 10.53 oob |
| 2026-09-01 01:15:55 | 15.06 ex-fence | 23.08 in-fence | 17.18 ex-fence | 7.94 oob | 9.67 oob | 10.53 oob |
| 2026-09-01 01:16:00 | 21.91 in-fence | 24.47 in-fence | 17.18 ex-fence | 3.06 oob | 9.67 oob | 10.53 oob |
| 2026-09-01 01:16:05 | 21.91 in-fence | 24.47 in-fence | 17.18 ex-fence | 3.06 oob | 9.67 oob | 10.53 oob |
| 2026-09-01 01:16:10 | 21.91 in-fence | 24.47 in-fence | 17.18 ex-fence | 3.06 oob | 9.67 oob | 10.53 oob |
| 2026-09-01 01:16:15 | 27.35 in-fence | 26.62 in-fence | 18.87 ex-fence | 4.70 oob | 10.46 oob | 10.53 oob |
| 2026-09-01 01:16:20 | 27.35 in-fence | 29.45 in-fence | 21.22 in-fence | 6.87 oob | 11.57 oob | 10.53 oob |
| 2026-09-01 01:16:25 | 27.35 in-fence | 33.47 in-fence | 24.83 in-fence | 10.01 oob | 13.32 oob | 10.53 oob |
| 2026-09-01 01:16:30 | 27.35 in-fence | 33.47 in-fence | 24.83 in-fence | 10.01 oob | 13.32 oob | 10.53 oob |
| 2026-09-01 01:16:35 | 27.35 in-fence | 32.22 in-fence | 23.67 in-fence | 9.03 oob | 12.76 oob | 10.53 oob |
| 2026-09-01 01:16:40 | 27.35 in-fence | 32.22 in-fence | 23.67 in-fence | 9.03 oob | 12.76 oob | 10.53 oob |
| 2026-09-01 01:16:45 | 27.35 in-fence | 31.15 in-fence | 22.71 in-fence | 8.19 oob | 12.29 oob | 10.53 oob |
| 2026-09-01 01:16:50 | 27.35 in-fence | 31.15 in-fence | 22.71 in-fence | 8.19 oob | 12.29 oob | 10.53 oob |
| 2026-09-01 01:16:55 | 27.35 in-fence | 30.33 in-fence | 21.98 in-fence | 7.55 oob | 11.94 oob | 10.53 oob |
| 2026-09-01 01:17:00 | 36.83 in-fence | 27.70 in-fence | 19.75 ex-fence | 5.52 oob | 10.87 oob | 10.53 oob |
| 2026-09-01 01:17:05 | 36.83 in-fence | 27.70 in-fence | 19.75 ex-fence | 5.52 oob | 10.87 oob | 10.53 oob |
| 2026-09-01 01:17:10 | 37.03 in-fence | 27.90 in-fence | 19.92 ex-fence | 5.68 oob | 10.95 oob | 10.53 oob |
| 2026-09-01 01:17:15 | 37.03 in-fence | 27.90 in-fence | 19.92 ex-fence | 5.68 oob | 10.95 oob | 10.53 oob |
| 2026-09-01 01:17:20 | 37.03 in-fence | 27.90 in-fence | 19.92 ex-fence | 5.68 oob | 10.95 oob | 10.53 oob |
| 2026-09-01 01:17:25 | 38.59 in-fence | 29.26 in-fence | 21.06 in-fence | 6.73 oob | 11.50 oob | 10.53 oob |
| 2026-09-01 01:17:30 | 38.59 in-fence | 29.26 in-fence | 21.06 in-fence | 6.73 oob | 11.50 oob | 10.53 oob |
| 2026-09-01 01:17:35 | 40.15 in-fence | 30.83 in-fence | 22.42 in-fence | 7.94 oob | 12.15 oob | 10.53 oob |
| 2026-09-01 01:17:40 | 40.15 in-fence | 30.50 in-fence | 22.13 in-fence | 7.68 oob | 12.01 oob | 10.53 oob |
| 2026-09-01 01:17:45 | 40.15 in-fence | 30.33 in-fence | 21.98 in-fence | 7.55 oob | 11.94 oob | 10.53 oob |
| 2026-09-01 01:17:50 | 39.61 in-fence | 29.98 in-fence | 21.68 in-fence | 7.28 oob | 11.79 oob | 10.53 oob |
| 2026-09-01 01:17:55 | 39.61 in-fence | 29.98 in-fence | 21.68 in-fence | 7.28 oob | 11.79 oob | 10.53 oob |
| 2026-09-01 01:18:00 | 49.79 in-fence | 21.55 in-fence | 21.15 in-fence | 5.52 oob | 10.87 oob | 4.23 oob |
| 2026-09-01 01:18:05 | 53.70 in-fence | 26.44 in-fence | 25.37 in-fence | 9.37 oob | 12.95 oob | 6.95 oob |
| 2026-09-01 01:18:10 | 53.70 in-fence | 29.98 in-fence | 29.53 in-fence | 12.27 oob | 14.72 oob | 10.64 oob |
| 2026-09-01 01:18:15 | 53.70 in-fence | 29.98 in-fence | 28.94 in-fence | 11.87 oob | 14.46 oob | 10.13 oob |
| 2026-09-01 01:18:20 | 53.70 in-fence | 29.49 in-fence | 28.32 in-fence | 11.44 oob | 14.19 oob | 9.59 oob |
| 2026-09-01 01:18:25 | 53.70 in-fence | 29.61 in-fence | 28.45 in-fence | 11.52 oob | 14.24 oob | 9.70 oob |
| 2026-09-01 01:18:30 | 53.70 in-fence | 28.84 in-fence | 27.68 in-fence | 10.98 oob | 13.91 oob | 9.02 oob |
| 2026-09-01 01:18:35 | 53.70 in-fence | 28.00 in-fence | 26.86 in-fence | 10.41 oob | 13.56 oob | 8.29 oob |
| 2026-09-01 01:18:40 | 53.70 in-fence | 29.36 in-fence | 28.20 in-fence | 11.35 oob | 14.13 oob | 9.48 oob |
| 2026-09-01 01:18:45 | 53.70 in-fence | 29.36 in-fence | 28.20 in-fence | 11.35 oob | 14.13 oob | 9.48 oob |
| 2026-09-01 01:18:50 | 53.70 in-fence | 28.84 in-fence | 27.68 in-fence | 10.98 oob | 13.91 oob | 9.02 oob |
| 2026-09-01 01:18:55 | 53.70 in-fence | 28.97 in-fence | 27.81 in-fence | 11.08 oob | 13.97 oob | 9.14 oob |
| 2026-09-01 01:19:00 | 67.99 in-fence | 29.23 in-fence | 28.07 in-fence | 11.26 oob | 14.08 oob | 9.37 oob |
| 2026-09-01 01:19:05 | 67.99 in-fence | 29.98 in-fence | 29.41 in-fence | 12.19 oob | 14.67 oob | 10.54 oob |
| 2026-09-01 01:19:10 | 67.99 in-fence | 29.98 in-fence | 29.30 in-fence | 12.11 oob | 14.61 oob | 10.44 oob |
| 2026-09-01 01:19:15 | 67.99 in-fence | 29.61 in-fence | 28.45 in-fence | 11.52 oob | 14.24 oob | 9.70 oob |
| 2026-09-01 01:19:20 | 67.99 in-fence | 29.74 in-fence | 28.57 in-fence | 11.61 oob | 14.30 oob | 9.81 oob |
| 2026-09-01 01:19:25 | 67.99 in-fence | 29.49 in-fence | 28.32 in-fence | 11.44 oob | 14.19 oob | 9.59 oob |
| 2026-09-01 01:19:30 | 66.62 in-fence | 28.14 in-fence | 27.00 in-fence | 10.51 oob | 13.62 oob | 8.41 oob |
| 2026-09-01 01:19:35 | 66.62 in-fence | 28.14 in-fence | 27.00 in-fence | 10.51 oob | 13.62 oob | 8.41 oob |
| 2026-09-01 01:19:40 | 67.05 in-fence | 28.43 in-fence | 27.27 in-fence | 10.70 oob | 13.74 oob | 8.66 oob |
| 2026-09-01 01:19:45 | 67.05 in-fence | 28.43 in-fence | 27.27 in-fence | 10.70 oob | 13.74 oob | 8.66 oob |
| 2026-09-01 01:19:50 | 67.99 in-fence | 29.10 in-fence | 27.94 in-fence | 11.17 oob | 14.02 oob | 9.25 oob |
| 2026-09-01 01:19:55 | 67.99 in-fence | 29.10 in-fence | 27.94 in-fence | 11.17 oob | 14.02 oob | 9.25 oob |
| 2026-09-01 01:20:00 | 81.14 in-fence | 41.32 in-fence | 28.20 in-fence | 23.93 in-fence | 10.95 oob | 9.48 oob |
| 2026-09-01 01:20:05 | 81.14 in-fence | 41.32 in-fence | 28.57 in-fence | 24.43 in-fence | 11.15 oob | 9.81 oob |
| 2026-09-01 01:20:10 | 81.14 in-fence | 41.32 in-fence | 28.70 in-fence | 24.59 in-fence | 11.22 oob | 9.92 oob |
| 2026-09-01 01:20:15 | 81.14 in-fence | 41.32 in-fence | 28.07 in-fence | 23.76 in-fence | 10.88 oob | 9.37 oob |
| 2026-09-01 01:20:20 | 81.14 in-fence | 41.32 in-fence | 28.32 in-fence | 24.10 in-fence | 11.02 oob | 9.59 oob |
| 2026-09-01 01:20:25 | 80.82 in-fence | 41.12 in-fence | 27.81 in-fence | 23.43 in-fence | 10.75 oob | 9.14 oob |
| 2026-09-01 01:20:30 | 80.20 in-fence | 40.72 in-fence | 27.54 in-fence | 23.13 in-fence | 10.63 oob | 8.90 oob |
| 2026-09-01 01:20:35 | 80.20 in-fence | 40.72 in-fence | 27.54 in-fence | 23.13 in-fence | 10.63 oob | 8.90 oob |
| 2026-09-01 01:20:40 | 80.20 in-fence | 40.72 in-fence | 27.54 in-fence | 23.13 in-fence | 10.63 oob | 8.90 oob |
| 2026-09-01 01:20:45 | 80.20 in-fence | 40.72 in-fence | 27.54 in-fence | 23.13 in-fence | 10.63 oob | 8.90 oob |
| 2026-09-01 01:20:50 | 80.20 in-fence | 40.72 in-fence | 27.54 in-fence | 23.13 in-fence | 10.63 oob | 8.90 oob |
| 2026-09-01 01:20:55 | 79.06 in-fence | 39.96 in-fence | 27.00 in-fence | 22.55 in-fence | 10.41 oob | 8.41 oob |
| 2026-09-01 01:21:00 | 83.34 in-fence | 37.20 in-fence | 34.25 in-fence | 20.35 in-fence | 9.52 oob | 6.06 oob |
| 2026-09-01 01:21:05 | 85.17 in-fence | 38.42 in-fence | 35.29 in-fence | 21.33 in-fence | 9.92 oob | 7.23 oob |
| 2026-09-01 01:21:10 | 88.09 in-fence | 40.15 in-fence | 36.76 in-fence | 22.69 in-fence | 10.46 oob | 8.54 oob |
| 2026-09-01 01:21:15 | 87.86 in-fence | 39.96 in-fence | 36.59 in-fence | 22.55 in-fence | 10.41 oob | 8.41 oob |
| 2026-09-01 01:21:20 | 88.30 in-fence | 40.33 in-fence | 36.94 in-fence | 22.83 in-fence | 10.52 oob | 8.66 oob |
| 2026-09-01 01:21:25 | 88.30 in-fence | 40.33 in-fence | 36.94 in-fence | 22.83 in-fence | 10.52 oob | 8.66 oob |
| 2026-09-01 01:21:30 | 89.63 in-fence | 41.32 in-fence | 38.08 in-fence | 23.93 in-fence | 10.95 oob | 9.48 oob |
| 2026-09-01 01:21:35 | 88.09 in-fence | 40.15 in-fence | 36.76 in-fence | 22.69 in-fence | 10.46 oob | 8.54 oob |
| 2026-09-01 01:21:40 | 88.09 in-fence | 40.15 in-fence | 36.76 in-fence | 22.69 in-fence | 10.46 oob | 8.54 oob |
| 2026-09-01 01:21:45 | 89.10 in-fence | 41.12 in-fence | 37.60 in-fence | 23.43 in-fence | 10.75 oob | 9.14 oob |
| 2026-09-01 01:21:50 | 90.03 in-fence | 41.32 in-fence | 39.27 in-fence | 25.22 in-fence | 11.48 oob | 10.34 oob |
| 2026-09-01 01:21:55 | 90.03 in-fence | 41.32 in-fence | 38.54 in-fence | 24.43 in-fence | 11.15 oob | 9.81 oob |
| 2026-09-01 01:22:00 | 94.49 in-fence | 51.02 in-fence | 37.44 in-fence | 23.28 in-fence | 10.69 oob | 9.02 oob |
| 2026-09-01 01:22:05 | 90.12 in-fence | 48.24 in-fence | 35.16 in-fence | 21.20 in-fence | 9.87 oob | 7.09 oob |
| 2026-09-01 01:22:10 | 88.05 in-fence | 46.73 in-fence | 33.88 in-fence | 20.01 in-fence | 9.37 oob | 5.58 oob |
| 2026-09-01 01:22:15 | 89.89 in-fence | 48.08 in-fence | 35.02 in-fence | 21.08 in-fence | 9.82 oob | 6.95 oob |
| 2026-09-01 01:22:20 | 89.67 in-fence | 47.92 in-fence | 34.89 in-fence | 20.95 in-fence | 9.76 oob | 6.80 oob |
| 2026-09-01 01:22:25 | 89.67 in-fence | 47.92 in-fence | 34.89 in-fence | 20.95 in-fence | 9.76 oob | 6.80 oob |
| 2026-09-01 01:22:30 | 92.21 in-fence | 49.63 in-fence | 36.29 in-fence | 22.26 in-fence | 10.29 oob | 8.16 oob |
| 2026-09-01 01:22:35 | 92.21 in-fence | 49.63 in-fence | 36.29 in-fence | 22.26 in-fence | 10.29 oob | 8.16 oob |
| 2026-09-01 01:22:40 | 90.60 in-fence | 48.57 in-fence | 35.43 in-fence | 21.46 in-fence | 9.97 oob | 7.37 oob |
| 2026-09-01 01:22:45 | 88.82 in-fence | 47.31 in-fence | 34.37 in-fence | 20.47 in-fence | 9.56 oob | 6.21 oob |
| 2026-09-01 01:22:50 | 88.82 in-fence | 47.31 in-fence | 34.37 in-fence | 20.47 in-fence | 9.56 oob | 6.21 oob |
| 2026-09-01 01:22:55 | 89.89 in-fence | 48.08 in-fence | 35.02 in-fence | 21.08 in-fence | 9.82 oob | 6.95 oob |
| 2026-09-01 01:23:00 | 75.61 in-fence | 46.87 in-fence | 34.00 in-fence | 20.12 in-fence | 9.42 oob | 5.74 oob |
| 2026-09-01 01:23:05 | 75.61 in-fence | 47.16 in-fence | 34.25 in-fence | 20.35 in-fence | 9.52 oob | 6.06 oob |
| 2026-09-01 01:23:10 | 75.61 in-fence | 46.46 in-fence | 33.64 in-fence | 19.79 ex-fence | 9.28 oob | 5.26 oob |
| 2026-09-01 01:23:15 | 75.61 in-fence | 45.93 in-fence | 33.18 in-fence | 19.35 ex-fence | 9.09 oob | 4.58 oob |
| 2026-09-01 01:23:20 | 75.61 in-fence | 46.32 in-fence | 33.53 in-fence | 19.68 ex-fence | 9.23 oob | 5.09 oob |
| 2026-09-01 01:23:25 | 75.61 in-fence | 46.32 in-fence | 33.53 in-fence | 19.68 ex-fence | 9.23 oob | 5.09 oob |
| 2026-09-01 01:23:30 | 75.61 in-fence | 46.87 in-fence | 34.00 in-fence | 20.12 in-fence | 9.42 oob | 5.74 oob |
| 2026-09-01 01:23:35 | 75.61 in-fence | 46.87 in-fence | 34.00 in-fence | 20.12 in-fence | 9.42 oob | 5.74 oob |
| 2026-09-01 01:23:40 | 75.61 in-fence | 46.87 in-fence | 34.00 in-fence | 20.12 in-fence | 9.42 oob | 5.74 oob |
| 2026-09-01 01:23:45 | 75.61 in-fence | 46.87 in-fence | 34.00 in-fence | 20.12 in-fence | 9.42 oob | 5.74 oob |
| 2026-09-01 01:23:50 | 75.61 in-fence | 46.32 in-fence | 33.53 in-fence | 19.68 ex-fence | 9.23 oob | 5.09 oob |
| 2026-09-01 01:23:55 | 75.61 in-fence | 46.32 in-fence | 33.53 in-fence | 19.68 ex-fence | 9.23 oob | 5.09 oob |
| 2026-09-01 01:24:00 | 61.87 in-fence | 51.92 in-fence | 32.45 in-fence | 24.09 in-fence | 8.87 oob | 3.02 oob |
| 2026-09-01 01:24:05 | 61.87 in-fence | 51.92 in-fence | 32.45 in-fence | 24.09 in-fence | 8.87 oob | 3.02 oob |
| 2026-09-01 01:24:10 | 61.87 in-fence | 50.96 in-fence | 31.58 in-fence | 23.26 in-fence | 8.57 oob | 2.91 oob |
| 2026-09-01 01:24:15 | 61.87 in-fence | 50.83 in-fence | 31.46 in-fence | 23.15 in-fence | 8.53 oob | 2.91 oob |
| 2026-09-01 01:24:20 | 61.87 in-fence | 50.46 in-fence | 31.11 in-fence | 22.82 in-fence | 8.41 oob | 2.91 oob |
| 2026-09-01 01:24:25 | 61.87 in-fence | 50.46 in-fence | 31.11 in-fence | 22.82 in-fence | 8.41 oob | 2.91 oob |
| 2026-09-01 01:24:30 | 61.87 in-fence | 50.46 in-fence | 31.11 in-fence | 22.82 in-fence | 8.41 oob | 2.91 oob |
| 2026-09-01 01:24:35 | 61.87 in-fence | 50.34 in-fence | 31.00 in-fence | 22.72 in-fence | 8.37 oob | 2.91 oob |
| 2026-09-01 01:24:40 | 61.87 in-fence | 50.46 in-fence | 31.11 in-fence | 22.82 in-fence | 8.41 oob | 2.91 oob |
| 2026-09-01 01:24:45 | 61.87 in-fence | 49.44 in-fence | 30.15 in-fence | 21.91 in-fence | 8.06 oob | 2.91 oob |
| 2026-09-01 01:24:50 | 61.87 in-fence | 49.44 in-fence | 30.15 in-fence | 21.91 in-fence | 8.06 oob | 2.91 oob |
| 2026-09-01 01:24:55 | 61.87 in-fence | 49.44 in-fence | 30.15 in-fence | 21.91 in-fence | 8.06 oob | 2.91 oob |
| 2026-09-01 01:25:00 | 47.58 in-fence | 48.54 in-fence | 29.27 in-fence | 21.09 in-fence | 12.31 oob | 2.91 oob |
| 2026-09-01 01:25:05 | 47.58 in-fence | 48.54 in-fence | 29.27 in-fence | 21.09 in-fence | 12.31 oob | 2.91 oob |
| 2026-09-01 01:25:10 | 47.58 in-fence | 48.64 in-fence | 29.37 in-fence | 21.17 in-fence | 12.41 oob | 2.91 oob |
| 2026-09-01 01:25:15 | 47.58 in-fence | 48.64 in-fence | 29.37 in-fence | 21.17 in-fence | 12.41 oob | 2.91 oob |
| 2026-09-01 01:25:20 | 47.58 in-fence | 48.18 in-fence | 28.91 in-fence | 20.74 in-fence | 11.91 oob | 2.91 oob |
| 2026-09-01 01:25:25 | 47.58 in-fence | 47.92 in-fence | 28.65 in-fence | 20.50 in-fence | 11.63 oob | 2.91 oob |
| 2026-09-01 01:25:30 | 47.58 in-fence | 49.03 in-fence | 29.75 in-fence | 21.53 in-fence | 12.82 oob | 2.91 oob |
| 2026-09-01 01:25:35 | 47.58 in-fence | 48.09 in-fence | 28.83 in-fence | 20.66 in-fence | 11.82 oob | 2.91 oob |
| 2026-09-01 01:25:40 | 47.58 in-fence | 48.09 in-fence | 28.83 in-fence | 20.66 in-fence | 11.82 oob | 2.91 oob |
| 2026-09-01 01:25:45 | 47.58 in-fence | 48.09 in-fence | 28.83 in-fence | 20.66 in-fence | 11.82 oob | 2.91 oob |
| 2026-09-01 01:25:50 | 47.58 in-fence | 48.09 in-fence | 28.83 in-fence | 20.66 in-fence | 11.82 oob | 2.91 oob |
| 2026-09-01 01:25:55 | 47.58 in-fence | 48.09 in-fence | 28.83 in-fence | 20.66 in-fence | 11.82 oob | 2.91 oob |
| 2026-09-01 01:26:00 | 33.30 in-fence | 50.92 in-fence | 28.74 in-fence | 20.58 in-fence | 11.72 oob | 2.91 oob |
| 2026-09-01 01:26:05 | 33.30 in-fence | 49.56 in-fence | 27.62 in-fence | 19.51 ex-fence | 10.46 oob | 2.91 oob |
| 2026-09-01 01:26:10 | 33.30 in-fence | 49.56 in-fence | 27.62 in-fence | 19.51 ex-fence | 10.46 oob | 2.91 oob |
| 2026-09-01 01:26:15 | 33.30 in-fence | 50.50 in-fence | 28.40 in-fence | 20.26 in-fence | 11.35 oob | 2.91 oob |
| 2026-09-01 01:26:20 | 34.01 in-fence | 51.52 in-fence | 29.00 in-fence | 20.83 in-fence | 12.01 oob | 2.91 oob |
| 2026-09-01 01:26:25 | 33.30 in-fence | 50.92 in-fence | 28.74 in-fence | 20.58 in-fence | 11.72 oob | 2.91 oob |
| 2026-09-01 01:26:30 | 33.30 in-fence | 49.23 in-fence | 27.32 in-fence | 19.23 ex-fence | 10.12 oob | 2.91 oob |
| 2026-09-01 01:26:35 | 33.30 in-fence | 48.09 in-fence | 26.12 in-fence | 17.55 ex-fence | 8.06 oob | 2.91 oob |
| 2026-09-01 01:26:40 | 33.30 in-fence | 48.18 in-fence | 26.38 in-fence | 18.34 ex-fence | 9.03 oob | 2.91 oob |
| 2026-09-01 01:26:45 | 33.30 in-fence | 48.32 in-fence | 26.51 in-fence | 18.46 ex-fence | 9.18 oob | 2.91 oob |
| 2026-09-01 01:26:50 | 33.30 in-fence | 48.53 in-fence | 26.70 in-fence | 18.65 ex-fence | 9.41 oob | 2.91 oob |
| 2026-09-01 01:26:55 | 33.30 in-fence | 48.83 in-fence | 26.97 in-fence | 18.90 ex-fence | 9.72 oob | 2.91 oob |
| 2026-09-01 01:27:00 | 25.74 in-fence | 50.40 in-fence | 30.77 in-fence | 20.18 in-fence | 11.25 oob | 2.91 oob |
| 2026-09-01 01:27:05 | 24.17 in-fence | 49.74 in-fence | 28.99 in-fence | 19.66 ex-fence | 10.63 oob | 2.91 oob |
| 2026-09-01 01:27:10 | 24.88 in-fence | 50.01 in-fence | 29.77 in-fence | 19.88 ex-fence | 10.89 oob | 2.91 oob |
| 2026-09-01 01:27:15 | 22.03 in-fence | 49.06 in-fence | 26.77 in-fence | 19.10 ex-fence | 9.96 oob | 2.91 oob |
| 2026-09-01 01:27:20 | 22.88 in-fence | 49.31 in-fence | 27.63 in-fence | 19.30 ex-fence | 10.21 oob | 2.91 oob |
| 2026-09-01 01:27:25 | 22.88 in-fence | 49.31 in-fence | 27.63 in-fence | 19.30 ex-fence | 10.21 oob | 2.91 oob |
| 2026-09-01 01:27:30 | 25.74 in-fence | 50.40 in-fence | 30.77 in-fence | 20.18 in-fence | 11.25 oob | 2.91 oob |
| 2026-09-01 01:27:35 | 25.74 in-fence | 50.40 in-fence | 30.77 in-fence | 20.18 in-fence | 11.25 oob | 2.91 oob |
| 2026-09-01 01:27:40 | 25.74 in-fence | 50.40 in-fence | 30.77 in-fence | 20.18 in-fence | 11.25 oob | 2.91 oob |
| 2026-09-01 01:27:45 | 26.54 in-fence | 50.81 in-fence | 31.73 in-fence | 20.50 in-fence | 11.63 oob | 2.91 oob |
| 2026-09-01 01:27:50 | 26.35 in-fence | 50.70 in-fence | 31.49 in-fence | 20.42 in-fence | 11.53 oob | 2.91 oob |
| 2026-09-01 01:27:55 | 26.35 in-fence | 50.70 in-fence | 31.49 in-fence | 20.42 in-fence | 11.53 oob | 2.91 oob |
| 2026-09-01 01:28:00 | 20.66 in-fence | 54.75 in-fence | 35.19 in-fence | 28.85 in-fence | 13.25 oob | 2.91 oob |
| 2026-09-01 01:28:05 | 19.25 ex-fence | 52.48 in-fence | 33.53 in-fence | 27.05 in-fence | 12.41 oob | 2.91 oob |
| 2026-09-01 01:28:10 | 19.25 ex-fence | 52.48 in-fence | 33.53 in-fence | 27.05 in-fence | 12.41 oob | 2.91 oob |
| 2026-09-01 01:28:15 | 17.78 ex-fence | 50.19 in-fence | 31.96 in-fence | 25.32 in-fence | 11.72 oob | 2.91 oob |
| 2026-09-01 01:28:20 | 21.43 in-fence | 56.02 in-fence | 36.17 in-fence | 29.89 in-fence | 14.17 oob | 2.91 oob |
| 2026-09-01 01:28:25 | 21.43 in-fence | 56.02 in-fence | 36.17 in-fence | 29.89 in-fence | 14.17 oob | 2.91 oob |
| 2026-09-01 01:28:30 | 21.43 in-fence | 56.02 in-fence | 36.17 in-fence | 29.89 in-fence | 14.17 oob | 2.91 oob |
| 2026-09-01 01:28:35 | 21.43 in-fence | 56.02 in-fence | 36.17 in-fence | 29.89 in-fence | 14.17 oob | 2.91 oob |
| 2026-09-01 01:28:40 | 21.98 in-fence | 56.97 in-fence | 36.92 in-fence | 30.68 in-fence | 14.87 oob | 2.91 oob |
| 2026-09-01 01:28:45 | 19.81 ex-fence | 53.37 in-fence | 34.17 in-fence | 27.74 in-fence | 12.72 oob | 2.91 oob |
| 2026-09-01 01:28:50 | 20.66 in-fence | 54.75 in-fence | 35.19 in-fence | 28.85 in-fence | 13.25 oob | 2.91 oob |
| 2026-09-01 01:28:55 | 20.66 in-fence | 54.75 in-fence | 35.19 in-fence | 28.85 in-fence | 13.25 oob | 2.91 oob |
| 2026-09-01 01:29:00 | 27.21 in-fence | 53.94 in-fence | 34.59 in-fence | 28.19 in-fence | 12.93 oob | 2.91 oob |
| 2026-09-01 01:29:05 | 26.17 in-fence | 52.78 in-fence | 33.75 in-fence | 27.28 in-fence | 12.51 oob | 2.91 oob |
| 2026-09-01 01:29:10 | 25.69 in-fence | 52.17 in-fence | 33.31 in-fence | 26.81 in-fence | 12.31 oob | 2.91 oob |
| 2026-09-01 01:29:15 | 25.69 in-fence | 52.17 in-fence | 33.31 in-fence | 26.81 in-fence | 12.31 oob | 2.91 oob |
| 2026-09-01 01:29:20 | 22.53 in-fence | 48.74 in-fence | 29.51 in-fence | 23.92 in-fence | 10.81 oob | 2.91 oob |
| 2026-09-01 01:29:25 | 20.26 in-fence | 48.74 in-fence | 25.55 in-fence | 22.40 in-fence | 9.48 oob | 2.91 oob |
| 2026-09-01 01:29:30 | 19.78 ex-fence | 48.74 in-fence | 25.11 in-fence | 22.07 in-fence | 9.18 oob | 2.91 oob |
| 2026-09-01 01:29:35 | 19.67 ex-fence | 48.74 in-fence | 25.00 in-fence | 21.98 in-fence | 9.10 oob | 2.91 oob |
| 2026-09-01 01:29:40 | 20.14 in-fence | 48.74 in-fence | 25.43 in-fence | 22.32 in-fence | 9.41 oob | 2.91 oob |
| 2026-09-01 01:29:45 | 20.14 in-fence | 48.74 in-fence | 25.43 in-fence | 22.32 in-fence | 9.41 oob | 2.91 oob |
| 2026-09-01 01:29:50 | 19.90 ex-fence | 48.74 in-fence | 25.21 in-fence | 22.15 in-fence | 9.25 oob | 2.91 oob |
| 2026-09-01 01:29:55 | 19.90 ex-fence | 48.74 in-fence | 25.21 in-fence | 22.15 in-fence | 9.25 oob | 2.91 oob |
| 2026-09-01 01:30:00 | 29.13 in-fence | 44.27 in-fence | 29.13 in-fence | 23.03 in-fence | 11.72 oob | 4.64 oob |
| 2026-09-01 01:30:05 | 28.25 in-fence | 43.43 in-fence | 28.15 in-fence | 22.76 in-fence | 11.12 oob | 4.14 oob |
| 2026-09-01 01:30:10 | 24.54 in-fence | 41.26 in-fence | 25.21 in-fence | 21.29 in-fence | 8.67 oob | 2.91 oob |
| 2026-09-01 01:30:15 | 25.55 in-fence | 41.26 in-fence | 25.30 in-fence | 21.90 in-fence | 9.39 oob | 2.91 oob |
| 2026-09-01 01:30:20 | 24.54 in-fence | 41.26 in-fence | 25.21 in-fence | 21.29 in-fence | 8.67 oob | 2.91 oob |
| 2026-09-01 01:30:25 | 24.42 in-fence | 41.26 in-fence | 25.21 in-fence | 21.21 in-fence | 8.59 oob | 2.91 oob |
| 2026-09-01 01:30:30 | 24.90 in-fence | 41.26 in-fence | 25.21 in-fence | 21.51 in-fence | 8.93 oob | 2.91 oob |
| 2026-09-01 01:30:35 | 24.90 in-fence | 41.26 in-fence | 25.21 in-fence | 21.51 in-fence | 8.93 oob | 2.91 oob |
| 2026-09-01 01:30:40 | 27.31 in-fence | 42.53 in-fence | 27.13 in-fence | 22.49 in-fence | 10.51 oob | 3.62 oob |
| 2026-09-01 01:30:45 | 29.69 in-fence | 44.81 in-fence | 29.76 in-fence | 23.22 in-fence | 12.11 oob | 4.96 oob |
| 2026-09-01 01:30:50 | 29.96 in-fence | 45.08 in-fence | 30.07 in-fence | 23.32 in-fence | 12.30 oob | 5.11 oob |
| 2026-09-01 01:30:55 | 28.84 in-fence | 44.00 in-fence | 28.81 in-fence | 22.94 in-fence | 11.52 oob | 4.47 oob |
| 2026-09-01 01:31:00 | 37.01 in-fence | 42.84 in-fence | 27.47 in-fence | 22.58 in-fence | 10.72 oob | 3.80 oob |
| 2026-09-01 01:31:05 | 35.22 in-fence | 41.26 in-fence | 25.21 in-fence | 21.67 in-fence | 9.11 oob | 2.91 oob |
| 2026-09-01 01:31:10 | 34.04 in-fence | 41.26 in-fence | 25.21 in-fence | 21.00 in-fence | 8.47 oob | 2.91 oob |
| 2026-09-01 01:31:15 | 34.04 in-fence | 41.26 in-fence | 25.21 in-fence | 21.00 in-fence | 8.47 oob | 2.91 oob |
| 2026-09-01 01:31:20 | 35.67 in-fence | 41.26 in-fence | 25.30 in-fence | 21.90 in-fence | 9.39 oob | 2.91 oob |
| 2026-09-01 01:31:25 | 34.94 in-fence | 41.26 in-fence | 25.21 in-fence | 21.51 in-fence | 8.93 oob | 2.91 oob |
| 2026-09-01 01:31:30 | 33.92 in-fence | 41.26 in-fence | 25.21 in-fence | 20.92 in-fence | 8.47 oob | 2.91 oob |
| 2026-09-01 01:31:35 | 35.83 in-fence | 41.26 in-fence | 25.44 in-fence | 21.98 in-fence | 9.48 oob | 2.91 oob |
| 2026-09-01 01:31:40 | 35.98 in-fence | 41.26 in-fence | 25.57 in-fence | 22.07 in-fence | 9.57 oob | 2.91 oob |
| 2026-09-01 01:31:45 | 36.31 in-fence | 41.59 in-fence | 26.07 in-fence | 22.23 in-fence | 9.88 oob | 3.09 oob |
| 2026-09-01 01:31:50 | 36.31 in-fence | 41.59 in-fence | 26.07 in-fence | 22.23 in-fence | 9.88 oob | 3.09 oob |
| 2026-09-01 01:31:55 | 36.15 in-fence | 41.26 in-fence | 25.70 in-fence | 22.15 in-fence | 9.67 oob | 2.91 oob |
| 2026-09-01 01:32:00 | 43.88 in-fence | 28.26 in-fence | 26.07 in-fence | 24.18 in-fence | 9.88 oob | 3.09 oob |
| 2026-09-01 01:32:05 | 41.50 in-fence | 27.85 in-fence | 25.21 in-fence | 22.82 in-fence | 8.67 oob | 2.91 oob |
| 2026-09-01 01:32:10 | 41.98 in-fence | 27.85 in-fence | 25.21 in-fence | 23.09 in-fence | 8.93 oob | 2.91 oob |
| 2026-09-01 01:32:15 | 41.98 in-fence | 27.85 in-fence | 25.21 in-fence | 23.09 in-fence | 8.93 oob | 2.91 oob |
| 2026-09-01 01:32:20 | 45.84 in-fence | 30.17 in-fence | 27.81 in-fence | 25.61 in-fence | 10.92 oob | 3.97 oob |
| 2026-09-01 01:32:25 | 45.84 in-fence | 30.17 in-fence | 27.81 in-fence | 25.61 in-fence | 10.92 oob | 3.97 oob |
| 2026-09-01 01:32:30 | 46.21 in-fence | 30.52 in-fence | 28.15 in-fence | 25.88 in-fence | 11.12 oob | 4.14 oob |
| 2026-09-01 01:32:35 | 49.40 in-fence | 33.67 in-fence | 31.27 in-fence | 28.44 in-fence | 13.05 oob | 5.72 oob |
| 2026-09-01 01:32:40 | 49.40 in-fence | 33.67 in-fence | 31.27 in-fence | 28.44 in-fence | 13.05 oob | 5.72 oob |
| 2026-09-01 01:32:45 | 47.90 in-fence | 32.18 in-fence | 29.76 in-fence | 27.20 in-fence | 12.11 oob | 4.96 oob |
| 2026-09-01 01:32:50 | 50.43 in-fence | 36.01 in-fence | 33.75 in-fence | 30.49 in-fence | 14.65 oob | 7.00 oob |
| 2026-09-01 01:32:55 | 50.43 in-fence | 36.24 in-fence | 34.01 in-fence | 30.71 in-fence | 14.82 oob | 7.13 oob |
| 2026-09-01 01:33:00 | 61.01 in-fence | 31.54 in-fence | 39.72 in-fence | 26.69 in-fence | 11.72 oob | 4.64 oob |
| 2026-09-01 01:33:05 | 60.83 in-fence | 31.21 in-fence | 39.56 in-fence | 26.42 in-fence | 11.52 oob | 4.47 oob |
| 2026-09-01 01:33:10 | 60.83 in-fence | 31.21 in-fence | 39.56 in-fence | 26.42 in-fence | 11.52 oob | 4.47 oob |
| 2026-09-01 01:33:15 | 59.83 in-fence | 29.05 in-fence | 38.64 in-fence | 24.76 in-fence | 10.30 oob | 3.45 oob |
| 2026-09-01 01:33:20 | 59.99 in-fence | 29.43 in-fence | 38.79 in-fence | 25.05 in-fence | 10.51 oob | 3.62 oob |
| 2026-09-01 01:33:25 | 61.01 in-fence | 31.54 in-fence | 39.72 in-fence | 26.69 in-fence | 11.72 oob | 4.64 oob |
| 2026-09-01 01:33:30 | 61.01 in-fence | 31.54 in-fence | 39.72 in-fence | 26.69 in-fence | 11.72 oob | 4.64 oob |
| 2026-09-01 01:33:35 | 61.01 in-fence | 31.54 in-fence | 39.72 in-fence | 26.69 in-fence | 11.72 oob | 4.64 oob |
| 2026-09-01 01:33:40 | 60.15 in-fence | 29.80 in-fence | 38.94 in-fence | 25.33 in-fence | 10.72 oob | 3.80 oob |
| 2026-09-01 01:33:45 | 60.15 in-fence | 29.80 in-fence | 38.94 in-fence | 25.33 in-fence | 10.72 oob | 3.80 oob |
| 2026-09-01 01:33:50 | 60.15 in-fence | 29.80 in-fence | 38.94 in-fence | 25.33 in-fence | 10.72 oob | 3.80 oob |
| 2026-09-01 01:33:55 | 61.01 in-fence | 31.54 in-fence | 39.72 in-fence | 26.69 in-fence | 11.72 oob | 4.64 oob |
| 2026-09-01 01:34:00 | 66.43 in-fence | 22.86 in-fence | 40.55 in-fence | 27.96 in-fence | 12.68 oob | 5.42 oob |
| 2026-09-01 01:34:05 | 68.96 in-fence | 24.86 in-fence | 41.63 in-fence | 29.38 in-fence | 13.78 oob | 6.31 oob |
| 2026-09-01 01:34:10 | 68.56 in-fence | 24.55 in-fence | 41.44 in-fence | 29.15 in-fence | 13.60 oob | 6.16 oob |
| 2026-09-01 01:34:15 | 70.04 in-fence | 28.35 in-fence | 44.94 in-fence | 32.14 in-fence | 15.97 ex-fence | 8.02 oob |
| 2026-09-01 01:34:20 | 70.04 in-fence | 26.87 in-fence | 43.12 in-fence | 30.92 in-fence | 14.99 oob | 7.26 oob |
| 2026-09-01 01:34:25 | 70.04 in-fence | 26.87 in-fence | 43.12 in-fence | 30.92 in-fence | 14.99 oob | 7.26 oob |
| 2026-09-01 01:34:30 | 70.04 in-fence | 28.58 in-fence | 45.23 in-fence | 32.33 in-fence | 16.13 ex-fence | 8.14 oob |
| 2026-09-01 01:34:35 | 70.04 in-fence | 29.46 in-fence | 46.35 in-fence | 33.09 in-fence | 16.76 ex-fence | 8.62 oob |
| 2026-09-01 01:34:40 | 70.04 in-fence | 29.87 in-fence | 46.88 in-fence | 33.46 in-fence | 17.07 ex-fence | 8.85 oob |
| 2026-09-01 01:34:45 | 70.04 in-fence | 30.83 in-fence | 48.16 in-fence | 34.35 in-fence | 17.81 ex-fence | 9.40 oob |
| 2026-09-01 01:34:50 | 70.04 in-fence | 30.83 in-fence | 48.16 in-fence | 34.35 in-fence | 17.81 ex-fence | 9.40 oob |
| 2026-09-01 01:34:55 | 70.04 in-fence | 30.83 in-fence | 48.16 in-fence | 34.35 in-fence | 17.81 ex-fence | 9.40 oob |
| 2026-09-01 01:35:00 | 75.73 in-fence | 31.54 in-fence | 48.29 in-fence | 35.51 in-fence | 29.71 in-fence | 10.14 oob |
| 2026-09-01 01:35:05 | 75.73 in-fence | 31.19 in-fence | 48.29 in-fence | 34.69 in-fence | 28.72 in-fence | 9.62 oob |
| 2026-09-01 01:35:10 | 75.73 in-fence | 31.19 in-fence | 48.29 in-fence | 34.69 in-fence | 28.72 in-fence | 9.62 oob |
| 2026-09-01 01:35:15 | 75.73 in-fence | 31.54 in-fence | 48.29 in-fence | 35.83 in-fence | 30.09 in-fence | 10.34 oob |
| 2026-09-01 01:35:20 | 75.73 in-fence | 31.54 in-fence | 48.29 in-fence | 36.44 in-fence | 32.07 in-fence | 11.37 oob |
| 2026-09-01 01:35:25 | 75.73 in-fence | 31.54 in-fence | 48.29 in-fence | 36.44 in-fence | 31.90 in-fence | 11.28 oob |
| 2026-09-01 01:35:30 | 75.73 in-fence | 31.54 in-fence | 48.29 in-fence | 36.44 in-fence | 32.08 in-fence | 11.46 oob |
| 2026-09-01 01:35:35 | 75.73 in-fence | 31.54 in-fence | 48.29 in-fence | 36.44 in-fence | 32.08 in-fence | 12.06 oob |
| 2026-09-01 01:35:40 | 75.73 in-fence | 31.54 in-fence | 48.29 in-fence | 36.44 in-fence | 32.08 in-fence | 12.22 oob |
| 2026-09-01 01:35:45 | 75.73 in-fence | 31.54 in-fence | 48.29 in-fence | 36.44 in-fence | 32.08 in-fence | 12.85 oob |
| 2026-09-01 01:35:50 | 75.73 in-fence | 31.54 in-fence | 48.29 in-fence | 36.44 in-fence | 32.08 in-fence | 13.99 oob |
| 2026-09-01 01:35:55 | 75.73 in-fence | 31.54 in-fence | 48.29 in-fence | 36.44 in-fence | 32.08 in-fence | 13.51 oob |
| 2026-09-01 01:36:00 | 83.33 in-fence | 37.30 in-fence | 56.15 in-fence | 50.34 in-fence | 32.08 in-fence | 23.61 in-fence |
| 2026-09-01 01:36:05 | 83.13 in-fence | 37.14 in-fence | 56.00 in-fence | 50.22 in-fence | 32.08 in-fence | 23.53 in-fence |
| 2026-09-01 01:36:10 | 83.13 in-fence | 37.14 in-fence | 56.00 in-fence | 50.22 in-fence | 32.08 in-fence | 23.53 in-fence |
| 2026-09-01 01:36:15 | 83.96 in-fence | 37.81 in-fence | 56.64 in-fence | 50.72 in-fence | 32.08 in-fence | 24.31 in-fence |
| 2026-09-01 01:36:20 | 83.96 in-fence | 37.81 in-fence | 56.64 in-fence | 50.72 in-fence | 32.08 in-fence | 24.31 in-fence |
| 2026-09-01 01:36:25 | 83.96 in-fence | 37.81 in-fence | 56.64 in-fence | 50.72 in-fence | 32.08 in-fence | 24.39 in-fence |
| 2026-09-01 01:36:30 | 83.96 in-fence | 37.81 in-fence | 56.64 in-fence | 50.72 in-fence | 32.08 in-fence | 24.31 in-fence |
| 2026-09-01 01:36:35 | 83.96 in-fence | 37.81 in-fence | 56.64 in-fence | 50.72 in-fence | 32.08 in-fence | 24.14 in-fence |
| 2026-09-01 01:36:40 | 83.96 in-fence | 37.81 in-fence | 56.64 in-fence | 50.72 in-fence | 32.08 in-fence | 25.18 in-fence |
| 2026-09-01 01:36:45 | 83.96 in-fence | 37.81 in-fence | 56.64 in-fence | 50.72 in-fence | 32.08 in-fence | 25.18 in-fence |
| 2026-09-01 01:36:50 | 83.96 in-fence | 37.81 in-fence | 56.64 in-fence | 50.72 in-fence | 32.08 in-fence | 25.18 in-fence |
| 2026-09-01 01:36:55 | 83.96 in-fence | 37.81 in-fence | 56.64 in-fence | 50.72 in-fence | 32.08 in-fence | 25.18 in-fence |
| 2026-09-01 01:37:00 | 87.72 in-fence | 37.81 in-fence | 56.64 in-fence | 50.72 in-fence | 32.08 in-fence | 24.64 in-fence |
| 2026-09-01 01:37:05 | 89.31 in-fence | 37.81 in-fence | 56.64 in-fence | 50.72 in-fence | 32.08 in-fence | 26.30 in-fence |
| 2026-09-01 01:37:10 | 89.31 in-fence | 37.81 in-fence | 56.64 in-fence | 50.72 in-fence | 32.08 in-fence | 25.90 in-fence |
