# THE t1 CADENCE LIST, 2026-09-03 00:00:00 .. 2026-09-04 23:59:55
# the new t1: gcws30b at wob 6 bars = 30 s | the r gate: ws1r past (44.0, 56.0) at its stamp
# the pre-1031 t1: ws1b at wob 12 bars = 60 s | the r gate: ws1r on the target side of 50

| the read | low side | high side |
|---|---|---|
| pre-1031 t1 cadences, ws1b wob 12, r past 50 | 43 | 49 |
| new t1, gcws30b wob 6, r past 56, grace on the CROSS bar | 102 | 95 |
| new t1, same but grace on the CONFIRM bar | 90 | 93 |
| the two grace arms differ by, low side | 44 bars only in CROSS, 30 only in CONFIRM |  |
| the two grace arms differ by, high side | | 25 only in CROSS, 24 only in CONFIRM |

## the grace-anchor diff, low side - 74 cadences differ

| the cadence bar | in the CROSS arm? | in the CONFIRM arm? | why |
|---|---|---|---|
| 2026-09-03 00:19:10 | YES | no | gcws30b ib 00:18:45, ws1r reversed 00:18:50 inside the 120s grace from the cross bar 00:18:45, r 22.28 past the 44.0 fence, stamp 00:18:50, hold 6 bars |
| 2026-09-03 00:19:40 | no | YES | gcws30b ib 00:18:45, ws1r reversed 00:19:40 inside the 120s grace from the confirm bar 00:19:10, r 22.76 past the 44.0 fence, stamp 00:19:40, hold 6 bars |
| 2026-09-03 00:31:00 | YES | no | gcws30b ib 00:30:35, ws1r reversed 00:30:45 inside the 120s grace from the cross bar 00:30:35, r 32.21 past the 44.0 fence, stamp 00:30:45, hold 6 bars |
| 2026-09-03 00:31:05 | no | YES | gcws30b ib 00:30:35, ws1r reversed 00:31:05 inside the 120s grace from the confirm bar 00:31:00, r 30.93 past the 44.0 fence, stamp 00:31:05, hold 6 bars |
| 2026-09-03 02:01:00 | YES | no | gcws30b ib 02:00:35, ws1r reversed 02:00:45 inside the 120s grace from the cross bar 02:00:35, r 39.31 past the 44.0 fence, stamp 02:00:45, hold 6 bars |
| 2026-09-03 03:22:40 | YES | no | gcws30b ib 03:22:15, ws1r reversed 03:22:30 inside the 120s grace from the cross bar 03:22:15, r 25.26 past the 44.0 fence, stamp 03:22:30, hold 6 bars |
| 2026-09-03 03:24:15 | no | YES | gcws30b ib 03:22:15, ws1r reversed 03:24:15 inside the 120s grace from the confirm bar 03:22:40, r 23.33 past the 44.0 fence, stamp 03:24:15, hold 6 bars |
| 2026-09-03 03:39:30 | YES | no | gcws30b ib 03:39:05, ws1r reversed 03:39:15 inside the 120s grace from the cross bar 03:39:05, r 30.02 past the 44.0 fence, stamp 03:39:15, hold 6 bars |
| 2026-09-03 03:39:45 | no | YES | gcws30b ib 03:39:05, ws1r reversed 03:39:45 inside the 120s grace from the confirm bar 03:39:30, r 28.73 past the 44.0 fence, stamp 03:39:45, hold 6 bars |
| 2026-09-03 04:37:55 | YES | no | gcws30b ib 04:37:30, ws1r reversed 04:37:45 inside the 120s grace from the cross bar 04:37:30, r 33.98 past the 44.0 fence, stamp 04:37:45, hold 6 bars |
| 2026-09-03 04:38:00 | no | YES | gcws30b ib 04:37:30, ws1r reversed 04:38:00 inside the 120s grace from the confirm bar 04:37:55, r 38.79 past the 44.0 fence, stamp 04:38:00, hold 6 bars |
| 2026-09-03 07:50:55 | YES | no | gcws30b ib 07:50:30, ws1r reversed 07:50:35 inside the 120s grace from the cross bar 07:50:30, r 2.55 past the 44.0 fence, stamp 07:50:35, hold 6 bars |
| 2026-09-03 07:52:35 | no | YES | gcws30b ib 07:50:30, ws1r reversed 07:52:35 inside the 120s grace from the confirm bar 07:50:55, r 19.00 past the 44.0 fence, stamp 07:52:35, hold 6 bars |
| 2026-09-03 08:45:00 | YES | no | gcws30b ib 08:44:35, ws1r reversed 08:44:55 inside the 120s grace from the cross bar 08:44:35, r 31.79 past the 44.0 fence, stamp 08:44:55, hold 6 bars |
| 2026-09-03 08:45:45 | no | YES | gcws30b ib 08:44:35, ws1r reversed 08:45:45 inside the 120s grace from the confirm bar 08:45:00, r 28.51 past the 44.0 fence, stamp 08:45:45, hold 6 bars |
| 2026-09-03 08:55:25 | YES | no | gcws30b ib 08:55:00, ws1r reversed 08:55:05 inside the 120s grace from the cross bar 08:55:00, r 23.36 past the 44.0 fence, stamp 08:55:05, hold 6 bars |
| 2026-09-03 09:04:50 | no | YES | gcws30b ib 09:02:25, ws1r reversed 09:04:50 inside the 120s grace from the confirm bar 09:02:50, r 30.57 past the 44.0 fence, stamp 09:04:50, hold 6 bars |
| 2026-09-03 10:15:05 | YES | no | gcws30b ib 10:14:40, ws1r reversed 10:15:05 inside the 120s grace from the cross bar 10:14:40, r 29.36 past the 44.0 fence, stamp 10:15:05, hold 6 bars |
| 2026-09-03 10:15:20 | no | YES | gcws30b ib 10:14:40, ws1r reversed 10:15:20 inside the 120s grace from the confirm bar 10:15:05, r 29.36 past the 44.0 fence, stamp 10:15:20, hold 6 bars |
| 2026-09-03 13:57:45 | YES | no | gcws30b ib 13:57:20, ws1r reversed 13:57:25 inside the 120s grace from the cross bar 13:57:20, r 27.21 past the 44.0 fence, stamp 13:57:25, hold 6 bars |
| 2026-09-03 13:58:45 | no | YES | gcws30b ib 13:57:20, ws1r reversed 13:58:45 inside the 120s grace from the confirm bar 13:57:45, r 19.92 past the 44.0 fence, stamp 13:58:45, hold 6 bars |
| 2026-09-03 16:24:20 | YES | no | gcws30b ib 16:23:55, ws1r reversed 16:24:00 inside the 120s grace from the cross bar 16:23:55, r 43.49 past the 44.0 fence, stamp 16:24:00, hold 6 bars |
| 2026-09-03 16:26:00 | no | YES | gcws30b ib 16:23:55, ws1r reversed 16:26:00 inside the 120s grace from the confirm bar 16:24:20, r 38.87 past the 44.0 fence, stamp 16:26:00, hold 6 bars |
| 2026-09-03 18:01:20 | YES | no | gcws30b ib 18:00:55, ws1r reversed 18:01:00 inside the 120s grace from the cross bar 18:00:55, r 40.71 past the 44.0 fence, stamp 18:01:00, hold 6 bars |
| 2026-09-03 19:52:30 | YES | no | gcws30b ib 19:52:05, ws1r reversed 19:52:15 inside the 120s grace from the cross bar 19:52:05, r 16.01 past the 44.0 fence, stamp 19:52:15, hold 6 bars |
| 2026-09-03 20:24:25 | YES | no | gcws30b ib 20:24:00, ws1r reversed 20:24:15 inside the 120s grace from the cross bar 20:24:00, r 26.43 past the 44.0 fence, stamp 20:24:15, hold 6 bars |
| 2026-09-03 20:24:45 | no | YES | gcws30b ib 20:24:00, ws1r reversed 20:24:45 inside the 120s grace from the confirm bar 20:24:25, r 28.47 past the 44.0 fence, stamp 20:24:45, hold 6 bars |
| 2026-09-03 20:38:05 | YES | no | gcws30b ib 20:37:40, ws1r reversed 20:37:50 inside the 120s grace from the cross bar 20:37:40, r 3.56 past the 44.0 fence, stamp 20:37:50, hold 6 bars |
| 2026-09-03 20:38:25 | no | YES | gcws30b ib 20:37:40, ws1r reversed 20:38:25 inside the 120s grace from the confirm bar 20:38:05, r 7.80 past the 44.0 fence, stamp 20:38:25, hold 6 bars |
| 2026-09-03 20:45:35 | YES | no | gcws30b ib 20:45:10, ws1r reversed 20:45:15 inside the 120s grace from the cross bar 20:45:10, r 26.36 past the 44.0 fence, stamp 20:45:15, hold 6 bars |
| 2026-09-03 20:45:45 | no | YES | gcws30b ib 20:45:10, ws1r reversed 20:45:45 inside the 120s grace from the confirm bar 20:45:35, r 29.13 past the 44.0 fence, stamp 20:45:45, hold 6 bars |
| 2026-09-03 21:07:25 | YES | no | gcws30b ib 21:07:00, ws1r reversed 21:07:20 inside the 120s grace from the cross bar 21:07:00, r 39.67 past the 44.0 fence, stamp 21:07:20, hold 6 bars |
| 2026-09-03 21:08:15 | no | YES | gcws30b ib 21:07:00, ws1r reversed 21:08:15 inside the 120s grace from the confirm bar 21:07:25, r 32.84 past the 44.0 fence, stamp 21:08:15, hold 6 bars |
| 2026-09-03 22:48:25 | YES | no | gcws30b ib 22:48:00, ws1r reversed 22:48:15 inside the 120s grace from the cross bar 22:48:00, r 18.20 past the 44.0 fence, stamp 22:48:15, hold 6 bars |
| 2026-09-03 22:48:30 | no | YES | gcws30b ib 22:48:00, ws1r reversed 22:48:30 inside the 120s grace from the confirm bar 22:48:25, r 18.62 past the 44.0 fence, stamp 22:48:30, hold 6 bars |
| 2026-09-03 23:11:45 | YES | no | gcws30b ib 23:11:20, ws1r reversed 23:11:25 inside the 120s grace from the cross bar 23:11:20, r 20.62 past the 44.0 fence, stamp 23:11:25, hold 6 bars |
| 2026-09-03 23:12:15 | no | YES | gcws30b ib 23:11:20, ws1r reversed 23:12:15 inside the 120s grace from the confirm bar 23:11:45, r 22.03 past the 44.0 fence, stamp 23:12:15, hold 6 bars |
| 2026-09-04 02:46:35 | YES | no | gcws30b ib 02:46:10, ws1r reversed 02:46:15 inside the 120s grace from the cross bar 02:46:10, r 28.69 past the 44.0 fence, stamp 02:46:15, hold 6 bars |
| 2026-09-04 02:46:45 | no | YES | gcws30b ib 02:46:10, ws1r reversed 02:46:45 inside the 120s grace from the confirm bar 02:46:35, r 27.52 past the 44.0 fence, stamp 02:46:45, hold 6 bars |
| 2026-09-04 03:40:35 | YES | no | gcws30b ib 03:40:10, ws1r reversed 03:40:15 inside the 120s grace from the cross bar 03:40:10, r 8.36 past the 44.0 fence, stamp 03:40:15, hold 6 bars |
| 2026-09-04 03:41:00 | no | YES | gcws30b ib 03:40:10, ws1r reversed 03:41:00 inside the 120s grace from the confirm bar 03:40:35, r 15.51 past the 44.0 fence, stamp 03:41:00, hold 6 bars |
| 2026-09-04 06:19:45 | YES | no | gcws30b ib 06:19:20, ws1r reversed 06:19:30 inside the 120s grace from the cross bar 06:19:20, r 5.44 past the 44.0 fence, stamp 06:19:30, hold 6 bars |
| 2026-09-04 06:20:00 | no | YES | gcws30b ib 06:19:20, ws1r reversed 06:20:00 inside the 120s grace from the confirm bar 06:19:45, r 7.18 past the 44.0 fence, stamp 06:20:00, hold 6 bars |
| 2026-09-04 07:52:50 | YES | no | gcws30b ib 07:52:25, ws1r reversed 07:52:50 inside the 120s grace from the cross bar 07:52:25, r 42.42 past the 44.0 fence, stamp 07:52:50, hold 6 bars |
| 2026-09-04 08:29:30 | YES | no | gcws30b ib 08:29:05, ws1r reversed 08:29:15 inside the 120s grace from the cross bar 08:29:05, r 23.43 past the 44.0 fence, stamp 08:29:15, hold 6 bars |
| 2026-09-04 08:37:25 | YES | no | gcws30b ib 08:37:00, ws1r reversed 08:37:15 inside the 120s grace from the cross bar 08:37:00, r 34.60 past the 44.0 fence, stamp 08:37:15, hold 6 bars |
| 2026-09-04 08:37:30 | no | YES | gcws30b ib 08:37:00, ws1r reversed 08:37:30 inside the 120s grace from the confirm bar 08:37:25, r 35.20 past the 44.0 fence, stamp 08:37:30, hold 6 bars |
| 2026-09-04 08:39:25 | YES | no | gcws30b ib 08:39:00, ws1r reversed 08:39:25 inside the 120s grace from the cross bar 08:39:00, r 38.16 past the 44.0 fence, stamp 08:39:25, hold 6 bars |
| 2026-09-04 08:39:40 | no | YES | gcws30b ib 08:39:00, ws1r reversed 08:39:40 inside the 120s grace from the confirm bar 08:39:25, r 38.16 past the 44.0 fence, stamp 08:39:40, hold 6 bars |
| 2026-09-04 08:40:55 | YES | no | gcws30b ib 08:40:30, ws1r reversed 08:40:35 inside the 120s grace from the cross bar 08:40:30, r 31.97 past the 44.0 fence, stamp 08:40:35, hold 6 bars |
| 2026-09-04 08:48:30 | YES | no | gcws30b ib 08:48:05, ws1r reversed 08:48:15 inside the 120s grace from the cross bar 08:48:05, r 32.30 past the 44.0 fence, stamp 08:48:15, hold 6 bars |
| 2026-09-04 08:49:30 | no | YES | gcws30b ib 08:48:05, ws1r reversed 08:49:30 inside the 120s grace from the confirm bar 08:48:30, r 38.07 past the 44.0 fence, stamp 08:49:30, hold 6 bars |
| 2026-09-04 10:04:00 | YES | no | gcws30b ib 10:03:35, ws1r reversed 10:03:40 inside the 120s grace from the cross bar 10:03:35, r 34.67 past the 44.0 fence, stamp 10:03:40, hold 6 bars |
| 2026-09-04 10:20:25 | YES | no | gcws30b ib 10:20:00, ws1r reversed 10:20:15 inside the 120s grace from the cross bar 10:20:00, r 34.71 past the 44.0 fence, stamp 10:20:15, hold 6 bars |
| 2026-09-04 10:20:45 | no | YES | gcws30b ib 10:20:00, ws1r reversed 10:20:45 inside the 120s grace from the confirm bar 10:20:25, r 36.62 past the 44.0 fence, stamp 10:20:45, hold 6 bars |
| 2026-09-04 10:58:20 | YES | no | gcws30b ib 10:57:55, ws1r reversed 10:58:20 inside the 120s grace from the cross bar 10:57:55, r 31.13 past the 44.0 fence, stamp 10:58:20, hold 6 bars |
| 2026-09-04 11:01:35 | YES | no | gcws30b ib 11:01:10, ws1r reversed 11:01:20 inside the 120s grace from the cross bar 11:01:10, r 42.46 past the 44.0 fence, stamp 11:01:20, hold 6 bars |
| 2026-09-04 11:03:15 | no | YES | gcws30b ib 11:01:10, ws1r reversed 11:03:15 inside the 120s grace from the confirm bar 11:01:35, r 31.41 past the 44.0 fence, stamp 11:03:15, hold 6 bars |
| 2026-09-04 11:03:20 | YES | no | gcws30b ib 11:02:55, ws1r reversed 11:03:15 inside the 120s grace from the cross bar 11:02:55, r 31.41 past the 44.0 fence, stamp 11:03:15, hold 6 bars |
| 2026-09-04 11:03:30 | no | YES | gcws30b ib 11:02:55, ws1r reversed 11:03:30 inside the 120s grace from the confirm bar 11:03:20, r 32.95 past the 44.0 fence, stamp 11:03:30, hold 6 bars |
| 2026-09-04 14:21:30 | YES | no | gcws30b ib 14:21:05, ws1r reversed 14:21:15 inside the 120s grace from the cross bar 14:21:05, r 43.17 past the 44.0 fence, stamp 14:21:15, hold 6 bars |
| 2026-09-04 16:19:25 | YES | no | gcws30b ib 16:19:00, ws1r reversed 16:19:05 inside the 120s grace from the cross bar 16:19:00, r 25.19 past the 44.0 fence, stamp 16:19:05, hold 6 bars |
| 2026-09-04 16:19:35 | no | YES | gcws30b ib 16:19:00, ws1r reversed 16:19:35 inside the 120s grace from the confirm bar 16:19:25, r 26.62 past the 44.0 fence, stamp 16:19:35, hold 6 bars |
| 2026-09-04 17:54:00 | YES | no | gcws30b ib 17:53:35, ws1r reversed 17:53:40 inside the 120s grace from the cross bar 17:53:35, r 20.02 past the 44.0 fence, stamp 17:53:40, hold 6 bars |
| 2026-09-04 18:32:00 | YES | no | gcws30b ib 18:31:35, ws1r reversed 18:31:45 inside the 120s grace from the cross bar 18:31:35, r 15.42 past the 44.0 fence, stamp 18:31:45, hold 6 bars |
| 2026-09-04 18:32:15 | no | YES | gcws30b ib 18:31:35, ws1r reversed 18:32:15 inside the 120s grace from the confirm bar 18:32:00, r 14.39 past the 44.0 fence, stamp 18:32:15, hold 6 bars |
| 2026-09-04 19:39:30 | YES | no | gcws30b ib 19:39:05, ws1r reversed 19:39:20 inside the 120s grace from the cross bar 19:39:05, r 10.44 past the 44.0 fence, stamp 19:39:20, hold 6 bars |
| 2026-09-04 20:08:55 | YES | no | gcws30b ib 20:08:30, ws1r reversed 20:08:40 inside the 120s grace from the cross bar 20:08:30, r 20.26 past the 44.0 fence, stamp 20:08:40, hold 6 bars |
| 2026-09-04 20:10:45 | no | YES | gcws30b ib 20:08:30, ws1r reversed 20:10:45 inside the 120s grace from the confirm bar 20:08:55, r 20.99 past the 44.0 fence, stamp 20:10:45, hold 6 bars |
| 2026-09-04 20:30:05 | YES | no | gcws30b ib 20:29:40, ws1r reversed 20:29:55 inside the 120s grace from the cross bar 20:29:40, r 31.11 past the 44.0 fence, stamp 20:29:55, hold 6 bars |
| 2026-09-04 20:42:25 | YES | no | gcws30b ib 20:42:00, ws1r reversed 20:42:25 inside the 120s grace from the cross bar 20:42:00, r 23.57 past the 44.0 fence, stamp 20:42:25, hold 6 bars |
| 2026-09-04 20:42:55 | no | YES | gcws30b ib 20:42:00, ws1r reversed 20:42:55 inside the 120s grace from the confirm bar 20:42:25, r 24.29 past the 44.0 fence, stamp 20:42:55, hold 6 bars |
| 2026-09-04 20:53:20 | YES | no | gcws30b ib 20:52:55, ws1r reversed 20:53:15 inside the 120s grace from the cross bar 20:52:55, r 42.07 past the 44.0 fence, stamp 20:53:15, hold 6 bars |
| 2026-09-04 23:56:30 | YES | no | gcws30b ib 23:56:05, ws1r reversed 23:56:20 inside the 120s grace from the cross bar 23:56:05, r 29.13 past the 44.0 fence, stamp 23:56:20, hold 6 bars |

## the grace-anchor diff, high side - 49 cadences differ

| the cadence bar | in the CROSS arm? | in the CONFIRM arm? | why |
|---|---|---|---|
| 2026-09-03 01:10:20 | YES | no | gcws30b ib 01:09:55, ws1r reversed 01:10:15 inside the 120s grace from the cross bar 01:09:55, r 83.60 past the 56.0 fence, stamp 01:10:15, hold 6 bars |
| 2026-09-03 01:10:50 | no | YES | gcws30b ib 01:09:55, ws1r reversed 01:10:50 inside the 120s grace from the confirm bar 01:10:20, r 81.95 past the 56.0 fence, stamp 01:10:50, hold 6 bars |
| 2026-09-03 02:15:25 | YES | no | gcws30b ib 02:15:00, ws1r reversed 02:15:15 inside the 120s grace from the cross bar 02:15:00, r 81.97 past the 56.0 fence, stamp 02:15:15, hold 6 bars |
| 2026-09-03 04:11:30 | YES | no | gcws30b ib 04:11:05, ws1r reversed 04:11:25 inside the 120s grace from the cross bar 04:11:05, r 65.29 past the 56.0 fence, stamp 04:11:25, hold 6 bars |
| 2026-09-03 04:50:45 | YES | no | gcws30b ib 04:50:20, ws1r reversed 04:50:30 inside the 120s grace from the cross bar 04:50:20, r 95.53 past the 56.0 fence, stamp 04:50:30, hold 6 bars |
| 2026-09-03 04:51:00 | no | YES | gcws30b ib 04:50:20, ws1r reversed 04:51:00 inside the 120s grace from the confirm bar 04:50:45, r 92.23 past the 56.0 fence, stamp 04:51:00, hold 6 bars |
| 2026-09-03 06:29:15 | YES | no | gcws30b ib 06:28:50, ws1r reversed 06:29:05 inside the 120s grace from the cross bar 06:28:50, r 65.58 past the 56.0 fence, stamp 06:29:05, hold 6 bars |
| 2026-09-03 06:30:00 | no | YES | gcws30b ib 06:28:50, ws1r reversed 06:30:00 inside the 120s grace from the confirm bar 06:29:15, r 72.32 past the 56.0 fence, stamp 06:30:00, hold 6 bars |
| 2026-09-03 07:43:00 | no | YES | gcws30b ib 07:40:40, ws1r reversed 07:43:00 inside the 120s grace from the confirm bar 07:41:05, r 91.13 past the 56.0 fence, stamp 07:43:00, hold 6 bars |
| 2026-09-03 09:13:20 | YES | no | gcws30b ib 09:12:55, ws1r reversed 09:13:00 inside the 120s grace from the cross bar 09:12:55, r 83.01 past the 56.0 fence, stamp 09:13:00, hold 6 bars |
| 2026-09-03 11:21:30 | YES | no | gcws30b ib 11:21:05, ws1r reversed 11:21:15 inside the 120s grace from the cross bar 11:21:05, r 83.00 past the 56.0 fence, stamp 11:21:15, hold 6 bars |
| 2026-09-03 12:49:45 | no | YES | gcws30b ib 12:49:05, ws1r reversed 12:49:45 inside the 120s grace from the confirm bar 12:49:30, r 57.93 past the 56.0 fence, stamp 12:49:45, hold 6 bars |
| 2026-09-03 13:42:40 | YES | no | gcws30b ib 13:42:15, ws1r reversed 13:42:25 inside the 120s grace from the cross bar 13:42:15, r 70.46 past the 56.0 fence, stamp 13:42:25, hold 6 bars |
| 2026-09-03 13:42:55 | no | YES | gcws30b ib 13:42:15, ws1r reversed 13:42:55 inside the 120s grace from the confirm bar 13:42:40, r 70.90 past the 56.0 fence, stamp 13:42:55, hold 6 bars |
| 2026-09-03 13:45:35 | YES | no | gcws30b ib 13:45:10, ws1r reversed 13:45:15 inside the 120s grace from the cross bar 13:45:10, r 80.75 past the 56.0 fence, stamp 13:45:15, hold 6 bars |
| 2026-09-03 16:49:40 | YES | no | gcws30b ib 16:49:15, ws1r reversed 16:49:20 inside the 120s grace from the cross bar 16:49:15, r 78.91 past the 56.0 fence, stamp 16:49:20, hold 6 bars |
| 2026-09-03 16:51:25 | no | YES | gcws30b ib 16:49:15, ws1r reversed 16:51:25 inside the 120s grace from the confirm bar 16:49:40, r 91.75 past the 56.0 fence, stamp 16:51:25, hold 6 bars |
| 2026-09-03 16:51:45 | YES | no | gcws30b ib 16:51:20, ws1r reversed 16:51:25 inside the 120s grace from the cross bar 16:51:20, r 91.75 past the 56.0 fence, stamp 16:51:25, hold 6 bars |
| 2026-09-03 17:27:35 | no | YES | gcws30b ib 17:25:15, ws1r reversed 17:27:35 inside the 120s grace from the confirm bar 17:25:40, r 56.41 past the 56.0 fence, stamp 17:27:35, hold 6 bars |
| 2026-09-03 19:05:35 | no | YES | gcws30b ib 19:03:30, ws1r reversed 19:05:35 inside the 120s grace from the confirm bar 19:03:55, r 58.39 past the 56.0 fence, stamp 19:05:35, hold 6 bars |
| 2026-09-03 19:25:10 | YES | no | gcws30b ib 19:24:45, ws1r reversed 19:25:00 inside the 120s grace from the cross bar 19:24:45, r 96.06 past the 56.0 fence, stamp 19:25:00, hold 6 bars |
| 2026-09-03 19:26:55 | no | YES | gcws30b ib 19:24:45, ws1r reversed 19:26:55 inside the 120s grace from the confirm bar 19:25:10, r 96.26 past the 56.0 fence, stamp 19:26:55, hold 6 bars |
| 2026-09-03 23:28:30 | YES | no | gcws30b ib 23:28:05, ws1r reversed 23:28:15 inside the 120s grace from the cross bar 23:28:05, r 68.10 past the 56.0 fence, stamp 23:28:15, hold 6 bars |
| 2026-09-03 23:28:45 | no | YES | gcws30b ib 23:28:05, ws1r reversed 23:28:45 inside the 120s grace from the confirm bar 23:28:30, r 67.97 past the 56.0 fence, stamp 23:28:45, hold 6 bars |
| 2026-09-03 23:30:50 | YES | no | gcws30b ib 23:30:25, ws1r reversed 23:30:30 inside the 120s grace from the cross bar 23:30:25, r 90.15 past the 56.0 fence, stamp 23:30:30, hold 6 bars |
| 2026-09-03 23:31:00 | no | YES | gcws30b ib 23:30:25, ws1r reversed 23:31:00 inside the 120s grace from the confirm bar 23:30:50, r 75.32 past the 56.0 fence, stamp 23:31:00, hold 6 bars |
| 2026-09-04 02:54:25 | YES | no | gcws30b ib 02:54:00, ws1r reversed 02:54:15 inside the 120s grace from the cross bar 02:54:00, r 88.90 past the 56.0 fence, stamp 02:54:15, hold 6 bars |
| 2026-09-04 02:54:30 | no | YES | gcws30b ib 02:54:00, ws1r reversed 02:54:30 inside the 120s grace from the confirm bar 02:54:25, r 90.53 past the 56.0 fence, stamp 02:54:30, hold 6 bars |
| 2026-09-04 04:30:25 | YES | no | gcws30b ib 04:30:00, ws1r reversed 04:30:20 inside the 120s grace from the cross bar 04:30:00, r 63.92 past the 56.0 fence, stamp 04:30:20, hold 6 bars |
| 2026-09-04 04:30:50 | no | YES | gcws30b ib 04:30:00, ws1r reversed 04:30:50 inside the 120s grace from the confirm bar 04:30:25, r 65.59 past the 56.0 fence, stamp 04:30:50, hold 6 bars |
| 2026-09-04 04:31:10 | YES | no | gcws30b ib 04:30:45, ws1r reversed 04:30:50 inside the 120s grace from the cross bar 04:30:45, r 65.59 past the 56.0 fence, stamp 04:30:50, hold 6 bars |
| 2026-09-04 04:32:45 | no | YES | gcws30b ib 04:30:45, ws1r reversed 04:32:45 inside the 120s grace from the confirm bar 04:31:10, r 57.49 past the 56.0 fence, stamp 04:32:45, hold 6 bars |
| 2026-09-04 05:22:05 | no | YES | gcws30b ib 05:20:00, ws1r reversed 05:22:05 inside the 120s grace from the confirm bar 05:20:25, r 65.91 past the 56.0 fence, stamp 05:22:05, hold 6 bars |
| 2026-09-04 05:59:55 | YES | no | gcws30b ib 05:59:30, ws1r reversed 05:59:45 inside the 120s grace from the cross bar 05:59:30, r 97.00 past the 56.0 fence, stamp 05:59:45, hold 6 bars |
| 2026-09-04 06:00:00 | no | YES | gcws30b ib 05:59:30, ws1r reversed 06:00:00 inside the 120s grace from the confirm bar 05:59:55, r 95.97 past the 56.0 fence, stamp 06:00:00, hold 6 bars |
| 2026-09-04 07:05:40 | YES | no | gcws30b ib 07:05:15, ws1r reversed 07:05:20 inside the 120s grace from the cross bar 07:05:15, r 75.71 past the 56.0 fence, stamp 07:05:20, hold 6 bars |
| 2026-09-04 08:00:35 | YES | no | gcws30b ib 08:00:10, ws1r reversed 08:00:15 inside the 120s grace from the cross bar 08:00:10, r 92.09 past the 56.0 fence, stamp 08:00:15, hold 6 bars |
| 2026-09-04 08:00:45 | no | YES | gcws30b ib 08:00:10, ws1r reversed 08:00:45 inside the 120s grace from the confirm bar 08:00:35, r 91.65 past the 56.0 fence, stamp 08:00:45, hold 6 bars |
| 2026-09-04 11:45:30 | YES | no | gcws30b ib 11:45:05, ws1r reversed 11:45:15 inside the 120s grace from the cross bar 11:45:05, r 73.11 past the 56.0 fence, stamp 11:45:15, hold 6 bars |
| 2026-09-04 11:46:45 | no | YES | gcws30b ib 11:45:05, ws1r reversed 11:46:45 inside the 120s grace from the confirm bar 11:45:30, r 69.44 past the 56.0 fence, stamp 11:46:45, hold 6 bars |
| 2026-09-04 12:20:35 | no | YES | gcws30b ib 12:18:30, ws1r reversed 12:20:35 inside the 120s grace from the confirm bar 12:18:55, r 58.33 past the 56.0 fence, stamp 12:20:35, hold 6 bars |
| 2026-09-04 13:41:20 | YES | no | gcws30b ib 13:40:55, ws1r reversed 13:41:15 inside the 120s grace from the cross bar 13:40:55, r 60.35 past the 56.0 fence, stamp 13:41:15, hold 6 bars |
| 2026-09-04 13:42:15 | no | YES | gcws30b ib 13:40:55, ws1r reversed 13:42:15 inside the 120s grace from the confirm bar 13:41:20, r 74.39 past the 56.0 fence, stamp 13:42:15, hold 6 bars |
| 2026-09-04 13:44:50 | YES | no | gcws30b ib 13:44:25, ws1r reversed 13:44:30 inside the 120s grace from the cross bar 13:44:25, r 79.59 past the 56.0 fence, stamp 13:44:30, hold 6 bars |
| 2026-09-04 13:45:00 | no | YES | gcws30b ib 13:44:25, ws1r reversed 13:45:00 inside the 120s grace from the confirm bar 13:44:50, r 88.50 past the 56.0 fence, stamp 13:45:00, hold 6 bars |
| 2026-09-04 15:27:30 | YES | no | gcws30b ib 15:27:05, ws1r reversed 15:27:15 inside the 120s grace from the cross bar 15:27:05, r 82.19 past the 56.0 fence, stamp 15:27:15, hold 6 bars |
| 2026-09-04 15:27:45 | no | YES | gcws30b ib 15:27:05, ws1r reversed 15:27:45 inside the 120s grace from the confirm bar 15:27:30, r 83.23 past the 56.0 fence, stamp 15:27:45, hold 6 bars |
| 2026-09-04 23:25:05 | YES | no | gcws30b ib 23:24:40, ws1r reversed 23:24:50 inside the 120s grace from the cross bar 23:24:40, r 72.70 past the 56.0 fence, stamp 23:24:50, hold 6 bars |
| 2026-09-04 23:26:00 | no | YES | gcws30b ib 23:24:40, ws1r reversed 23:26:00 inside the 120s grace from the confirm bar 23:25:05, r 71.29 past the 56.0 fence, stamp 23:26:00, hold 6 bars |

## the new t1 cadence list, low side, grace on the CROSS bar - 102 cadences

| the cadence bar | why |
|---|---|
| 2026-09-03 00:17:00 | gcws30b ib 00:15:55, ws1r reversed 00:17:00 inside the 120s grace from the cross bar 00:15:55, r 26.62 past the 44.0 fence, stamp 00:17:00, hold 6 bars |
| 2026-09-03 00:19:10 | gcws30b ib 00:18:45, ws1r reversed 00:18:50 inside the 120s grace from the cross bar 00:18:45, r 22.28 past the 44.0 fence, stamp 00:18:50, hold 6 bars |
| 2026-09-03 00:25:30 | gcws30b oob 00:20:00..00:25:00, ws1r reversed 00:21:20 during, r 21.21 past the 44.0 fence, stamp 00:21:20, cross 00:25:05 hold 6 bars |
| 2026-09-03 00:30:45 | gcws30b ib 00:28:50, ws1r reversed 00:30:45 inside the 120s grace from the cross bar 00:28:50, r 32.21 past the 44.0 fence, stamp 00:30:45, hold 6 bars |
| 2026-09-03 00:31:00 | gcws30b ib 00:30:35, ws1r reversed 00:30:45 inside the 120s grace from the cross bar 00:30:35, r 32.21 past the 44.0 fence, stamp 00:30:45, hold 6 bars |
| 2026-09-03 01:02:45 | gcws30b oob 01:01:20..01:02:15, ws1r reversed 01:02:15 during, r 36.20 past the 44.0 fence, stamp 01:02:15, cross 01:02:20 hold 6 bars |
| 2026-09-03 01:51:00 | gcws30b ib 01:49:50, ws1r reversed 01:51:00 inside the 120s grace from the cross bar 01:49:50, r 29.08 past the 44.0 fence, stamp 01:51:00, hold 6 bars |
| 2026-09-03 02:01:00 | gcws30b ib 02:00:35, ws1r reversed 02:00:45 inside the 120s grace from the cross bar 02:00:35, r 39.31 past the 44.0 fence, stamp 02:00:45, hold 6 bars |
| 2026-09-03 02:03:05 | gcws30b ib 02:02:00, ws1r reversed 02:03:05 inside the 120s grace from the cross bar 02:02:00, r 21.85 past the 44.0 fence, stamp 02:03:05, hold 6 bars |
| 2026-09-03 03:22:40 | gcws30b ib 03:22:15, ws1r reversed 03:22:30 inside the 120s grace from the cross bar 03:22:15, r 25.26 past the 44.0 fence, stamp 03:22:30, hold 6 bars |
| 2026-09-03 03:25:50 | gcws30b oob 03:23:15..03:25:20, ws1r reversed 03:24:15 during, r 23.33 past the 44.0 fence, stamp 03:24:15, cross 03:25:25 hold 6 bars |
| 2026-09-03 03:30:50 | gcws30b oob 03:29:35..03:30:20, ws1r reversed 03:30:20 during, r 34.95 past the 44.0 fence, stamp 03:30:20, cross 03:30:25 hold 6 bars |
| 2026-09-03 03:39:15 | gcws30b ib 03:37:20, ws1r reversed 03:39:15 inside the 120s grace from the cross bar 03:37:20, r 30.02 past the 44.0 fence, stamp 03:39:15, hold 6 bars |
| 2026-09-03 03:39:30 | gcws30b ib 03:39:05, ws1r reversed 03:39:15 inside the 120s grace from the cross bar 03:39:05, r 30.02 past the 44.0 fence, stamp 03:39:15, hold 6 bars |
| 2026-09-03 04:37:55 | gcws30b ib 04:37:30, ws1r reversed 04:37:45 inside the 120s grace from the cross bar 04:37:30, r 33.98 past the 44.0 fence, stamp 04:37:45, hold 6 bars |
| 2026-09-03 07:33:00 | gcws30b oob 07:30:15..07:32:30, ws1r reversed 07:32:10 during, r 22.68 past the 44.0 fence, stamp 07:32:10, cross 07:32:35 hold 6 bars |
| 2026-09-03 07:50:35 | gcws30b ib 07:49:05, ws1r reversed 07:50:35 inside the 120s grace from the cross bar 07:49:05, r 2.55 past the 44.0 fence, stamp 07:50:35, hold 6 bars |
| 2026-09-03 07:50:55 | gcws30b ib 07:50:30, ws1r reversed 07:50:35 inside the 120s grace from the cross bar 07:50:30, r 2.55 past the 44.0 fence, stamp 07:50:35, hold 6 bars |
| 2026-09-03 08:36:50 | gcws30b ib 08:36:20, ws1r reversed 08:36:50 inside the 120s grace from the cross bar 08:36:20, r 27.46 past the 44.0 fence, stamp 08:36:50, hold 6 bars |
| 2026-09-03 08:42:00 | gcws30b ib 08:40:30, ws1r reversed 08:42:00 inside the 120s grace from the cross bar 08:40:30, r 37.00 past the 44.0 fence, stamp 08:42:00, hold 6 bars |
| 2026-09-03 08:45:00 | gcws30b ib 08:44:35, ws1r reversed 08:44:55 inside the 120s grace from the cross bar 08:44:35, r 31.79 past the 44.0 fence, stamp 08:44:55, hold 6 bars |
| 2026-09-03 08:55:25 | gcws30b ib 08:55:00, ws1r reversed 08:55:05 inside the 120s grace from the cross bar 08:55:00, r 23.36 past the 44.0 fence, stamp 08:55:05, hold 6 bars |
| 2026-09-03 09:22:15 | gcws30b ib 09:20:50, ws1r reversed 09:22:15 inside the 120s grace from the cross bar 09:20:50, r 26.73 past the 44.0 fence, stamp 09:22:15, hold 6 bars |
| 2026-09-03 09:43:40 | gcws30b oob 09:41:15..09:43:10, ws1r reversed 09:42:55 during, r 34.84 past the 44.0 fence, stamp 09:42:55, cross 09:43:15 hold 6 bars |
| 2026-09-03 09:52:35 | gcws30b ib 09:51:10, ws1r reversed 09:52:35 inside the 120s grace from the cross bar 09:51:10, r 42.48 past the 44.0 fence, stamp 09:52:35, hold 6 bars |
| 2026-09-03 10:05:15 | gcws30b oob 10:02:00..10:04:45, ws1r reversed 10:03:45 during, r 43.84 past the 44.0 fence, stamp 10:03:45, cross 10:04:50 hold 6 bars |
| 2026-09-03 10:15:05 | gcws30b ib 10:14:40, ws1r reversed 10:15:05 inside the 120s grace from the cross bar 10:14:40, r 29.36 past the 44.0 fence, stamp 10:15:05, hold 6 bars |
| 2026-09-03 10:28:15 | gcws30b ib 10:26:35, ws1r reversed 10:28:15 inside the 120s grace from the cross bar 10:26:35, r 31.75 past the 44.0 fence, stamp 10:28:15, hold 6 bars |
| 2026-09-03 10:28:15 | gcws30b ib 10:27:25, ws1r reversed 10:28:15 inside the 120s grace from the cross bar 10:27:25, r 31.75 past the 44.0 fence, stamp 10:28:15, hold 6 bars |
| 2026-09-03 11:16:15 | gcws30b ib 11:15:05, ws1r reversed 11:16:15 inside the 120s grace from the cross bar 11:15:05, r 43.59 past the 44.0 fence, stamp 11:16:15, hold 6 bars |
| 2026-09-03 13:57:45 | gcws30b ib 13:57:20, ws1r reversed 13:57:25 inside the 120s grace from the cross bar 13:57:20, r 27.21 past the 44.0 fence, stamp 13:57:25, hold 6 bars |
| 2026-09-03 14:05:30 | gcws30b oob 14:00:00..14:05:00, ws1r reversed 14:04:30 during, r 11.29 past the 44.0 fence, stamp 14:04:30, cross 14:05:05 hold 6 bars |
| 2026-09-03 16:24:00 | gcws30b ib 16:22:25, ws1r reversed 16:24:00 inside the 120s grace from the cross bar 16:22:25, r 43.49 past the 44.0 fence, stamp 16:24:00, hold 6 bars |
| 2026-09-03 16:24:20 | gcws30b ib 16:23:55, ws1r reversed 16:24:00 inside the 120s grace from the cross bar 16:23:55, r 43.49 past the 44.0 fence, stamp 16:24:00, hold 6 bars |
| 2026-09-03 17:04:00 | gcws30b ib 17:03:00, ws1r reversed 17:04:00 inside the 120s grace from the cross bar 17:03:00, r 11.51 past the 44.0 fence, stamp 17:04:00, hold 6 bars |
| 2026-09-03 18:01:20 | gcws30b ib 18:00:55, ws1r reversed 18:01:00 inside the 120s grace from the cross bar 18:00:55, r 40.71 past the 44.0 fence, stamp 18:01:00, hold 6 bars |
| 2026-09-03 19:52:30 | gcws30b ib 19:52:05, ws1r reversed 19:52:15 inside the 120s grace from the cross bar 19:52:05, r 16.01 past the 44.0 fence, stamp 19:52:15, hold 6 bars |
| 2026-09-03 19:55:35 | gcws30b oob 19:54:50..19:55:05, ws1r reversed 19:54:55 during, r 24.93 past the 44.0 fence, stamp 19:54:55, cross 19:55:10 hold 6 bars |
| 2026-09-03 20:03:40 | gcws30b oob 20:00:10..20:03:10, ws1r reversed 20:03:00 during, r 40.45 past the 44.0 fence, stamp 20:03:00, cross 20:03:15 hold 6 bars |
| 2026-09-03 20:24:25 | gcws30b ib 20:24:00, ws1r reversed 20:24:15 inside the 120s grace from the cross bar 20:24:00, r 26.43 past the 44.0 fence, stamp 20:24:15, hold 6 bars |
| 2026-09-03 20:38:05 | gcws30b ib 20:37:40, ws1r reversed 20:37:50 inside the 120s grace from the cross bar 20:37:40, r 3.56 past the 44.0 fence, stamp 20:37:50, hold 6 bars |
| 2026-09-03 20:45:35 | gcws30b ib 20:45:10, ws1r reversed 20:45:15 inside the 120s grace from the cross bar 20:45:10, r 26.36 past the 44.0 fence, stamp 20:45:15, hold 6 bars |
| 2026-09-03 21:07:20 | gcws30b ib 21:06:15, ws1r reversed 21:07:20 inside the 120s grace from the cross bar 21:06:15, r 39.67 past the 44.0 fence, stamp 21:07:20, hold 6 bars |
| 2026-09-03 21:07:25 | gcws30b ib 21:07:00, ws1r reversed 21:07:20 inside the 120s grace from the cross bar 21:07:00, r 39.67 past the 44.0 fence, stamp 21:07:20, hold 6 bars |
| 2026-09-03 22:36:25 | gcws30b oob 22:31:40..22:35:55, ws1r reversed 22:34:40 during, r 10.09 past the 44.0 fence, stamp 22:34:40, cross 22:36:00 hold 6 bars |
| 2026-09-03 22:48:25 | gcws30b ib 22:48:00, ws1r reversed 22:48:15 inside the 120s grace from the cross bar 22:48:00, r 18.20 past the 44.0 fence, stamp 22:48:15, hold 6 bars |
| 2026-09-03 23:11:45 | gcws30b ib 23:11:20, ws1r reversed 23:11:25 inside the 120s grace from the cross bar 23:11:20, r 20.62 past the 44.0 fence, stamp 23:11:25, hold 6 bars |
| 2026-09-03 23:13:35 | gcws30b oob 23:12:55..23:13:05, ws1r reversed 23:13:00 during, r 19.06 past the 44.0 fence, stamp 23:13:00, cross 23:13:10 hold 6 bars |
| 2026-09-04 00:10:00 | gcws30b oob 00:06:30..00:09:30, ws1r reversed 00:09:00 during, r 8.51 past the 44.0 fence, stamp 00:09:00, cross 00:09:35 hold 6 bars |
| 2026-09-04 01:01:00 | gcws30b ib 01:00:05, ws1r reversed 01:01:00 inside the 120s grace from the cross bar 01:00:05, r 20.35 past the 44.0 fence, stamp 01:01:00, hold 6 bars |
| 2026-09-04 01:05:55 | gcws30b oob 01:04:20..01:05:25, ws1r reversed 01:05:00 during, r 22.02 past the 44.0 fence, stamp 01:05:00, cross 01:05:30 hold 6 bars |
| 2026-09-04 01:30:35 | gcws30b oob 01:29:05..01:30:05, ws1r reversed 01:30:05 during, r 9.76 past the 44.0 fence, stamp 01:30:05, cross 01:30:10 hold 6 bars |
| 2026-09-04 01:36:40 | gcws30b oob 01:33:35..01:36:10, ws1r reversed 01:35:25 during, r 5.14 past the 44.0 fence, stamp 01:35:25, cross 01:36:15 hold 6 bars |
| 2026-09-04 02:25:05 | gcws30b ib 02:24:35, ws1r reversed 02:25:05 inside the 120s grace from the cross bar 02:24:35, r 16.66 past the 44.0 fence, stamp 02:25:05, hold 6 bars |
| 2026-09-04 02:46:35 | gcws30b ib 02:46:10, ws1r reversed 02:46:15 inside the 120s grace from the cross bar 02:46:10, r 28.69 past the 44.0 fence, stamp 02:46:15, hold 6 bars |
| 2026-09-04 03:40:15 | gcws30b ib 03:38:20, ws1r reversed 03:40:15 inside the 120s grace from the cross bar 03:38:20, r 8.36 past the 44.0 fence, stamp 03:40:15, hold 6 bars |
| 2026-09-04 03:40:35 | gcws30b ib 03:40:10, ws1r reversed 03:40:15 inside the 120s grace from the cross bar 03:40:10, r 8.36 past the 44.0 fence, stamp 03:40:15, hold 6 bars |
| 2026-09-04 04:03:55 | gcws30b oob 03:57:00..04:03:25, ws1r reversed 04:03:00 during, r 21.30 past the 44.0 fence, stamp 04:03:00, cross 04:03:30 hold 6 bars |
| 2026-09-04 05:52:55 | gcws30b oob 05:47:50..05:52:25, ws1r reversed 05:51:45 during, r 25.16 past the 44.0 fence, stamp 05:51:45, cross 05:52:30 hold 6 bars |
| 2026-09-04 06:19:45 | gcws30b ib 06:19:20, ws1r reversed 06:19:30 inside the 120s grace from the cross bar 06:19:20, r 5.44 past the 44.0 fence, stamp 06:19:30, hold 6 bars |
| 2026-09-04 06:21:50 | gcws30b oob 06:20:00..06:21:20, ws1r reversed 06:20:55 during, r 7.18 past the 44.0 fence, stamp 06:20:55, cross 06:21:25 hold 6 bars |
| 2026-09-04 07:47:15 | gcws30b ib 07:45:55, ws1r reversed 07:47:15 inside the 120s grace from the cross bar 07:45:55, r 33.18 past the 44.0 fence, stamp 07:47:15, hold 6 bars |
| 2026-09-04 07:52:50 | gcws30b ib 07:52:25, ws1r reversed 07:52:50 inside the 120s grace from the cross bar 07:52:25, r 42.42 past the 44.0 fence, stamp 07:52:50, hold 6 bars |
| 2026-09-04 07:54:45 | gcws30b ib 07:53:55, ws1r reversed 07:54:45 inside the 120s grace from the cross bar 07:53:55, r 42.31 past the 44.0 fence, stamp 07:54:45, hold 6 bars |
| 2026-09-04 08:29:30 | gcws30b ib 08:29:05, ws1r reversed 08:29:15 inside the 120s grace from the cross bar 08:29:05, r 23.43 past the 44.0 fence, stamp 08:29:15, hold 6 bars |
| 2026-09-04 08:36:15 | gcws30b ib 08:34:20, ws1r reversed 08:36:15 inside the 120s grace from the cross bar 08:34:20, r 41.41 past the 44.0 fence, stamp 08:36:15, hold 6 bars |
| 2026-09-04 08:37:25 | gcws30b ib 08:37:00, ws1r reversed 08:37:15 inside the 120s grace from the cross bar 08:37:00, r 34.60 past the 44.0 fence, stamp 08:37:15, hold 6 bars |
| 2026-09-04 08:39:25 | gcws30b ib 08:39:00, ws1r reversed 08:39:25 inside the 120s grace from the cross bar 08:39:00, r 38.16 past the 44.0 fence, stamp 08:39:25, hold 6 bars |
| 2026-09-04 08:40:55 | gcws30b ib 08:40:30, ws1r reversed 08:40:35 inside the 120s grace from the cross bar 08:40:30, r 31.97 past the 44.0 fence, stamp 08:40:35, hold 6 bars |
| 2026-09-04 08:48:15 | gcws30b ib 08:46:45, ws1r reversed 08:48:15 inside the 120s grace from the cross bar 08:46:45, r 32.30 past the 44.0 fence, stamp 08:48:15, hold 6 bars |
| 2026-09-04 08:48:30 | gcws30b ib 08:48:05, ws1r reversed 08:48:15 inside the 120s grace from the cross bar 08:48:05, r 32.30 past the 44.0 fence, stamp 08:48:15, hold 6 bars |
| 2026-09-04 10:03:40 | gcws30b ib 10:02:50, ws1r reversed 10:03:40 inside the 120s grace from the cross bar 10:02:50, r 34.67 past the 44.0 fence, stamp 10:03:40, hold 6 bars |
| 2026-09-04 10:04:00 | gcws30b ib 10:03:35, ws1r reversed 10:03:40 inside the 120s grace from the cross bar 10:03:35, r 34.67 past the 44.0 fence, stamp 10:03:40, hold 6 bars |
| 2026-09-04 10:12:10 | gcws30b oob 10:06:00..10:11:40, ws1r reversed 10:11:30 during, r 15.06 past the 44.0 fence, stamp 10:11:30, cross 10:11:45 hold 6 bars |
| 2026-09-04 10:20:25 | gcws30b ib 10:20:00, ws1r reversed 10:20:15 inside the 120s grace from the cross bar 10:20:00, r 34.71 past the 44.0 fence, stamp 10:20:15, hold 6 bars |
| 2026-09-04 10:58:20 | gcws30b ib 10:57:55, ws1r reversed 10:58:20 inside the 120s grace from the cross bar 10:57:55, r 31.13 past the 44.0 fence, stamp 10:58:20, hold 6 bars |
| 2026-09-04 11:01:35 | gcws30b ib 11:01:10, ws1r reversed 11:01:20 inside the 120s grace from the cross bar 11:01:10, r 42.46 past the 44.0 fence, stamp 11:01:20, hold 6 bars |
| 2026-09-04 11:03:20 | gcws30b ib 11:02:55, ws1r reversed 11:03:15 inside the 120s grace from the cross bar 11:02:55, r 31.41 past the 44.0 fence, stamp 11:03:15, hold 6 bars |
| 2026-09-04 12:35:25 | gcws30b oob 12:30:00..12:34:55, ws1r reversed 12:33:30 during, r 30.70 past the 44.0 fence, stamp 12:33:30, cross 12:35:00 hold 6 bars |
| 2026-09-04 14:21:30 | gcws30b ib 14:21:05, ws1r reversed 14:21:15 inside the 120s grace from the cross bar 14:21:05, r 43.17 past the 44.0 fence, stamp 14:21:15, hold 6 bars |
| 2026-09-04 14:39:10 | gcws30b oob 14:37:35..14:38:40, ws1r reversed 14:38:20 during, r 20.82 past the 44.0 fence, stamp 14:38:20, cross 14:38:45 hold 6 bars |
| 2026-09-04 16:18:20 | gcws30b ib 16:17:50, ws1r reversed 16:18:20 inside the 120s grace from the cross bar 16:17:50, r 28.82 past the 44.0 fence, stamp 16:18:20, hold 6 bars |
| 2026-09-04 16:19:25 | gcws30b ib 16:19:00, ws1r reversed 16:19:05 inside the 120s grace from the cross bar 16:19:00, r 25.19 past the 44.0 fence, stamp 16:19:05, hold 6 bars |
| 2026-09-04 17:18:35 | gcws30b oob 17:14:45..17:18:05, ws1r reversed 17:17:30 during, r 31.49 past the 44.0 fence, stamp 17:17:30, cross 17:18:10 hold 6 bars |
| 2026-09-04 17:43:00 | gcws30b ib 17:41:15, ws1r reversed 17:43:00 inside the 120s grace from the cross bar 17:41:15, r 41.32 past the 44.0 fence, stamp 17:43:00, hold 6 bars |
| 2026-09-04 17:54:00 | gcws30b ib 17:53:35, ws1r reversed 17:53:40 inside the 120s grace from the cross bar 17:53:35, r 20.02 past the 44.0 fence, stamp 17:53:40, hold 6 bars |
| 2026-09-04 18:32:00 | gcws30b ib 18:31:35, ws1r reversed 18:31:45 inside the 120s grace from the cross bar 18:31:35, r 15.42 past the 44.0 fence, stamp 18:31:45, hold 6 bars |
| 2026-09-04 19:12:55 | gcws30b oob 19:09:45..19:12:25, ws1r reversed 19:11:00 during, r 4.52 past the 44.0 fence, stamp 19:11:00, cross 19:12:30 hold 6 bars |
| 2026-09-04 19:39:30 | gcws30b ib 19:39:05, ws1r reversed 19:39:20 inside the 120s grace from the cross bar 19:39:05, r 10.44 past the 44.0 fence, stamp 19:39:20, hold 6 bars |
| 2026-09-04 19:58:05 | gcws30b oob 19:57:05..19:57:35, ws1r reversed 19:57:20 during, r 16.03 past the 44.0 fence, stamp 19:57:20, cross 19:57:40 hold 6 bars |
| 2026-09-04 20:08:55 | gcws30b ib 20:08:30, ws1r reversed 20:08:40 inside the 120s grace from the cross bar 20:08:30, r 20.26 past the 44.0 fence, stamp 20:08:40, hold 6 bars |
| 2026-09-04 20:16:05 | gcws30b oob 20:11:45..20:15:35, ws1r reversed 20:15:15 during, r 32.09 past the 44.0 fence, stamp 20:15:15, cross 20:15:40 hold 6 bars |
| 2026-09-04 20:30:05 | gcws30b ib 20:29:40, ws1r reversed 20:29:55 inside the 120s grace from the cross bar 20:29:40, r 31.11 past the 44.0 fence, stamp 20:29:55, hold 6 bars |
| 2026-09-04 20:39:45 | gcws30b ib 20:38:05, ws1r reversed 20:39:45 inside the 120s grace from the cross bar 20:38:05, r 39.93 past the 44.0 fence, stamp 20:39:45, hold 6 bars |
| 2026-09-04 20:39:45 | gcws30b ib 20:38:55, ws1r reversed 20:39:45 inside the 120s grace from the cross bar 20:38:55, r 39.93 past the 44.0 fence, stamp 20:39:45, hold 6 bars |
| 2026-09-04 20:42:25 | gcws30b ib 20:42:00, ws1r reversed 20:42:25 inside the 120s grace from the cross bar 20:42:00, r 23.57 past the 44.0 fence, stamp 20:42:25, hold 6 bars |
| 2026-09-04 20:53:15 | gcws30b ib 20:51:45, ws1r reversed 20:53:15 inside the 120s grace from the cross bar 20:51:45, r 42.07 past the 44.0 fence, stamp 20:53:15, hold 6 bars |
| 2026-09-04 20:53:20 | gcws30b ib 20:52:55, ws1r reversed 20:53:15 inside the 120s grace from the cross bar 20:52:55, r 42.07 past the 44.0 fence, stamp 20:53:15, hold 6 bars |
| 2026-09-04 21:57:15 | gcws30b oob 21:51:55..21:56:45, ws1r reversed 21:56:00 during, r 4.83 past the 44.0 fence, stamp 21:56:00, cross 21:56:50 hold 6 bars |
| 2026-09-04 22:30:10 | gcws30b ib 22:29:15, ws1r reversed 22:30:10 inside the 120s grace from the cross bar 22:29:15, r 41.36 past the 44.0 fence, stamp 22:30:10, hold 6 bars |
| 2026-09-04 23:55:15 | gcws30b ib 23:54:15, ws1r reversed 23:55:15 inside the 120s grace from the cross bar 23:54:15, r 25.56 past the 44.0 fence, stamp 23:55:15, hold 6 bars |
| 2026-09-04 23:56:30 | gcws30b ib 23:56:05, ws1r reversed 23:56:20 inside the 120s grace from the cross bar 23:56:05, r 29.13 past the 44.0 fence, stamp 23:56:20, hold 6 bars |

## the new t1 cadence list, high side, grace on the CROSS bar - 95 cadences

| the cadence bar | why |
|---|---|
| 2026-09-03 00:00:25 | gcws30b oob 23:47:50..23:59:55, ws1r reversed 23:57:55 during, r 85.71 past the 56.0 fence, stamp 23:57:55, cross 00:00:00 hold 6 bars |
| 2026-09-03 01:10:20 | gcws30b ib 01:09:55, ws1r reversed 01:10:15 inside the 120s grace from the cross bar 01:09:55, r 83.60 past the 56.0 fence, stamp 01:10:15, hold 6 bars |
| 2026-09-03 01:16:25 | gcws30b ib 01:15:00, ws1r reversed 01:16:25 inside the 120s grace from the cross bar 01:15:00, r 75.40 past the 56.0 fence, stamp 01:16:25, hold 6 bars |
| 2026-09-03 01:36:00 | gcws30b oob 01:32:30..01:35:30, ws1r reversed 01:35:15 during, r 71.97 past the 56.0 fence, stamp 01:35:15, cross 01:35:35 hold 6 bars |
| 2026-09-03 02:15:25 | gcws30b ib 02:15:00, ws1r reversed 02:15:15 inside the 120s grace from the cross bar 02:15:00, r 81.97 past the 56.0 fence, stamp 02:15:15, hold 6 bars |
| 2026-09-03 02:19:25 | gcws30b oob 02:18:00..02:18:55, ws1r reversed 02:18:55 during, r 65.99 past the 56.0 fence, stamp 02:18:55, cross 02:19:00 hold 6 bars |
| 2026-09-03 02:51:05 | gcws30b ib 02:50:05, ws1r reversed 02:51:05 inside the 120s grace from the cross bar 02:50:05, r 72.26 past the 56.0 fence, stamp 02:51:05, hold 6 bars |
| 2026-09-03 02:51:45 | gcws30b ib 02:51:05, ws1r reversed 02:51:45 inside the 120s grace from the cross bar 02:51:05, r 76.31 past the 56.0 fence, stamp 02:51:45, hold 6 bars |
| 2026-09-03 02:54:00 | gcws30b ib 02:52:20, ws1r reversed 02:54:00 inside the 120s grace from the cross bar 02:52:20, r 65.01 past the 56.0 fence, stamp 02:54:00, hold 6 bars |
| 2026-09-03 02:59:10 | gcws30b oob 02:56:55..02:58:40, ws1r reversed 02:57:20 during, r 56.63 past the 56.0 fence, stamp 02:57:20, cross 02:58:45 hold 6 bars |
| 2026-09-03 03:15:20 | gcws30b ib 03:14:15, ws1r reversed 03:15:20 inside the 120s grace from the cross bar 03:14:15, r 67.68 past the 56.0 fence, stamp 03:15:20, hold 6 bars |
| 2026-09-03 04:11:30 | gcws30b ib 04:11:05, ws1r reversed 04:11:25 inside the 120s grace from the cross bar 04:11:05, r 65.29 past the 56.0 fence, stamp 04:11:25, hold 6 bars |
| 2026-09-03 04:50:45 | gcws30b ib 04:50:20, ws1r reversed 04:50:30 inside the 120s grace from the cross bar 04:50:20, r 95.53 past the 56.0 fence, stamp 04:50:30, hold 6 bars |
| 2026-09-03 04:58:50 | gcws30b oob 04:51:15..04:58:20, ws1r reversed 04:58:00 during, r 69.83 past the 56.0 fence, stamp 04:58:00, cross 04:58:25 hold 6 bars |
| 2026-09-03 05:53:40 | gcws30b oob 05:50:05..05:53:10, ws1r reversed 05:52:25 during, r 78.18 past the 56.0 fence, stamp 05:52:25, cross 05:53:15 hold 6 bars |
| 2026-09-03 06:27:45 | gcws30b ib 06:26:55, ws1r reversed 06:27:45 inside the 120s grace from the cross bar 06:26:55, r 72.30 past the 56.0 fence, stamp 06:27:45, hold 6 bars |
| 2026-09-03 06:29:15 | gcws30b ib 06:28:50, ws1r reversed 06:29:05 inside the 120s grace from the cross bar 06:28:50, r 65.58 past the 56.0 fence, stamp 06:29:05, hold 6 bars |
| 2026-09-03 06:30:55 | gcws30b ib 06:30:20, ws1r reversed 06:30:55 inside the 120s grace from the cross bar 06:30:20, r 67.76 past the 56.0 fence, stamp 06:30:55, hold 6 bars |
| 2026-09-03 06:31:30 | gcws30b ib 06:30:55, ws1r reversed 06:31:30 inside the 120s grace from the cross bar 06:30:55, r 68.28 past the 56.0 fence, stamp 06:31:30, hold 6 bars |
| 2026-09-03 06:40:25 | gcws30b oob 06:33:35..06:39:55, ws1r reversed 06:39:55 during, r 83.53 past the 56.0 fence, stamp 06:39:55, cross 06:40:00 hold 6 bars |
| 2026-09-03 07:06:25 | gcws30b oob 07:04:10..07:05:55, ws1r reversed 07:05:30 during, r 89.48 past the 56.0 fence, stamp 07:05:30, cross 07:06:00 hold 6 bars |
| 2026-09-03 09:13:00 | gcws30b ib 09:12:10, ws1r reversed 09:13:00 inside the 120s grace from the cross bar 09:12:10, r 83.01 past the 56.0 fence, stamp 09:13:00, hold 6 bars |
| 2026-09-03 09:13:20 | gcws30b ib 09:12:55, ws1r reversed 09:13:00 inside the 120s grace from the cross bar 09:12:55, r 83.01 past the 56.0 fence, stamp 09:13:00, hold 6 bars |
| 2026-09-03 10:50:20 | gcws30b ib 10:48:30, ws1r reversed 10:50:20 inside the 120s grace from the cross bar 10:48:30, r 64.53 past the 56.0 fence, stamp 10:50:20, hold 6 bars |
| 2026-09-03 11:00:45 | gcws30b oob 10:51:35..11:00:15, ws1r reversed 10:57:45 during, r 88.83 past the 56.0 fence, stamp 10:57:45, cross 11:00:20 hold 6 bars |
| 2026-09-03 11:21:30 | gcws30b ib 11:21:05, ws1r reversed 11:21:15 inside the 120s grace from the cross bar 11:21:05, r 83.00 past the 56.0 fence, stamp 11:21:15, hold 6 bars |
| 2026-09-03 11:35:10 | gcws30b oob 11:34:20..11:34:40, ws1r reversed 11:34:30 during, r 87.54 past the 56.0 fence, stamp 11:34:30, cross 11:34:45 hold 6 bars |
| 2026-09-03 12:35:10 | gcws30b oob 12:34:15..12:34:40, ws1r reversed 12:34:30 during, r 65.92 past the 56.0 fence, stamp 12:34:30, cross 12:34:45 hold 6 bars |
| 2026-09-03 12:37:50 | gcws30b oob 12:36:55..12:37:20, ws1r reversed 12:37:05 during, r 67.13 past the 56.0 fence, stamp 12:37:05, cross 12:37:25 hold 6 bars |
| 2026-09-03 12:49:30 | gcws30b ib 12:47:45, ws1r reversed 12:49:30 inside the 120s grace from the cross bar 12:47:45, r 57.25 past the 56.0 fence, stamp 12:49:30, hold 6 bars |
| 2026-09-03 12:49:30 | gcws30b ib 12:49:05, ws1r reversed 12:49:30 inside the 120s grace from the cross bar 12:49:05, r 57.25 past the 56.0 fence, stamp 12:49:30, hold 6 bars |
| 2026-09-03 12:57:15 | gcws30b ib 12:56:10, ws1r reversed 12:57:15 inside the 120s grace from the cross bar 12:56:10, r 92.25 past the 56.0 fence, stamp 12:57:15, hold 6 bars |
| 2026-09-03 12:59:25 | gcws30b oob 12:58:50..12:58:55, ws1r reversed 12:58:55 during, r 96.15 past the 56.0 fence, stamp 12:58:55, cross 12:59:00 hold 6 bars |
| 2026-09-03 13:41:30 | gcws30b ib 13:40:00, ws1r reversed 13:41:30 inside the 120s grace from the cross bar 13:40:00, r 56.87 past the 56.0 fence, stamp 13:41:30, hold 6 bars |
| 2026-09-03 13:42:40 | gcws30b ib 13:42:15, ws1r reversed 13:42:25 inside the 120s grace from the cross bar 13:42:15, r 70.46 past the 56.0 fence, stamp 13:42:25, hold 6 bars |
| 2026-09-03 13:45:15 | gcws30b ib 13:43:40, ws1r reversed 13:45:15 inside the 120s grace from the cross bar 13:43:40, r 80.75 past the 56.0 fence, stamp 13:45:15, hold 6 bars |
| 2026-09-03 13:45:35 | gcws30b ib 13:45:10, ws1r reversed 13:45:15 inside the 120s grace from the cross bar 13:45:10, r 80.75 past the 56.0 fence, stamp 13:45:15, hold 6 bars |
| 2026-09-03 16:49:40 | gcws30b ib 16:49:15, ws1r reversed 16:49:20 inside the 120s grace from the cross bar 16:49:15, r 78.91 past the 56.0 fence, stamp 16:49:20, hold 6 bars |
| 2026-09-03 16:51:45 | gcws30b ib 16:51:20, ws1r reversed 16:51:25 inside the 120s grace from the cross bar 16:51:20, r 91.75 past the 56.0 fence, stamp 16:51:25, hold 6 bars |
| 2026-09-03 17:50:10 | gcws30b oob 17:47:30..17:49:40, ws1r reversed 17:49:25 during, r 65.67 past the 56.0 fence, stamp 17:49:25, cross 17:49:45 hold 6 bars |
| 2026-09-03 18:11:45 | gcws30b oob 18:09:20..18:11:15, ws1r reversed 18:10:40 during, r 82.65 past the 56.0 fence, stamp 18:10:40, cross 18:11:20 hold 6 bars |
| 2026-09-03 18:19:05 | gcws30b oob 18:15:45..18:18:35, ws1r reversed 18:18:15 during, r 87.14 past the 56.0 fence, stamp 18:18:15, cross 18:18:40 hold 6 bars |
| 2026-09-03 18:54:35 | gcws30b oob 18:53:10..18:54:05, ws1r reversed 18:54:00 during, r 58.93 past the 56.0 fence, stamp 18:54:00, cross 18:54:10 hold 6 bars |
| 2026-09-03 19:00:00 | gcws30b ib 18:58:00, ws1r reversed 19:00:00 inside the 120s grace from the cross bar 18:58:00, r 71.42 past the 56.0 fence, stamp 19:00:00, hold 6 bars |
| 2026-09-03 19:00:50 | gcws30b oob 18:59:05..19:00:20, ws1r reversed 19:00:00 during, r 71.42 past the 56.0 fence, stamp 19:00:00, cross 19:00:25 hold 6 bars |
| 2026-09-03 19:06:50 | gcws30b oob 19:04:00..19:06:20, ws1r reversed 19:05:55 during, r 57.42 past the 56.0 fence, stamp 19:05:55, cross 19:06:25 hold 6 bars |
| 2026-09-03 19:25:00 | gcws30b ib 19:24:00, ws1r reversed 19:25:00 inside the 120s grace from the cross bar 19:24:00, r 96.06 past the 56.0 fence, stamp 19:25:00, hold 6 bars |
| 2026-09-03 19:25:10 | gcws30b ib 19:24:45, ws1r reversed 19:25:00 inside the 120s grace from the cross bar 19:24:45, r 96.06 past the 56.0 fence, stamp 19:25:00, hold 6 bars |
| 2026-09-03 19:28:25 | gcws30b oob 19:25:45..19:27:55, ws1r reversed 19:26:55 during, r 96.26 past the 56.0 fence, stamp 19:26:55, cross 19:28:00 hold 6 bars |
| 2026-09-03 21:15:35 | gcws30b oob 21:13:00..21:15:05, ws1r reversed 21:15:05 during, r 86.42 past the 56.0 fence, stamp 21:15:05, cross 21:15:10 hold 6 bars |
| 2026-09-03 21:38:55 | gcws30b oob 21:34:05..21:38:25, ws1r reversed 21:36:00 during, r 67.10 past the 56.0 fence, stamp 21:36:00, cross 21:38:30 hold 6 bars |
| 2026-09-03 23:28:30 | gcws30b ib 23:28:05, ws1r reversed 23:28:15 inside the 120s grace from the cross bar 23:28:05, r 68.10 past the 56.0 fence, stamp 23:28:15, hold 6 bars |
| 2026-09-03 23:30:50 | gcws30b ib 23:30:25, ws1r reversed 23:30:30 inside the 120s grace from the cross bar 23:30:25, r 90.15 past the 56.0 fence, stamp 23:30:30, hold 6 bars |
| 2026-09-03 23:33:35 | gcws30b ib 23:32:00, ws1r reversed 23:33:35 inside the 120s grace from the cross bar 23:32:00, r 67.33 past the 56.0 fence, stamp 23:33:35, hold 6 bars |
| 2026-09-04 00:34:30 | gcws30b ib 00:33:20, ws1r reversed 00:34:30 inside the 120s grace from the cross bar 00:33:20, r 87.84 past the 56.0 fence, stamp 00:34:30, hold 6 bars |
| 2026-09-04 00:43:00 | gcws30b oob 00:35:35..00:42:30, ws1r reversed 00:42:00 during, r 81.95 past the 56.0 fence, stamp 00:42:00, cross 00:42:35 hold 6 bars |
| 2026-09-04 02:54:25 | gcws30b ib 02:54:00, ws1r reversed 02:54:15 inside the 120s grace from the cross bar 02:54:00, r 88.90 past the 56.0 fence, stamp 02:54:15, hold 6 bars |
| 2026-09-04 03:05:15 | gcws30b oob 02:58:35..03:04:45, ws1r reversed 03:01:05 during, r 76.88 past the 56.0 fence, stamp 03:01:05, cross 03:04:50 hold 6 bars |
| 2026-09-04 04:21:40 | gcws30b oob 04:14:30..04:21:10, ws1r reversed 04:18:00 during, r 94.73 past the 56.0 fence, stamp 04:18:00, cross 04:21:15 hold 6 bars |
| 2026-09-04 04:30:25 | gcws30b ib 04:30:00, ws1r reversed 04:30:20 inside the 120s grace from the cross bar 04:30:00, r 63.92 past the 56.0 fence, stamp 04:30:20, hold 6 bars |
| 2026-09-04 04:31:10 | gcws30b ib 04:30:45, ws1r reversed 04:30:50 inside the 120s grace from the cross bar 04:30:45, r 65.59 past the 56.0 fence, stamp 04:30:50, hold 6 bars |
| 2026-09-04 05:24:00 | gcws30b ib 05:22:05, ws1r reversed 05:24:00 inside the 120s grace from the cross bar 05:22:05, r 69.49 past the 56.0 fence, stamp 05:24:00, hold 6 bars |
| 2026-09-04 05:26:40 | gcws30b oob 05:23:10..05:26:10, ws1r reversed 05:25:45 during, r 69.46 past the 56.0 fence, stamp 05:25:45, cross 05:26:15 hold 6 bars |
| 2026-09-04 05:59:55 | gcws30b ib 05:59:30, ws1r reversed 05:59:45 inside the 120s grace from the cross bar 05:59:30, r 97.00 past the 56.0 fence, stamp 05:59:45, hold 6 bars |
| 2026-09-04 07:05:40 | gcws30b ib 07:05:15, ws1r reversed 07:05:20 inside the 120s grace from the cross bar 07:05:15, r 75.71 past the 56.0 fence, stamp 07:05:20, hold 6 bars |
| 2026-09-04 07:15:45 | gcws30b oob 07:10:50..07:15:15, ws1r reversed 07:15:05 during, r 82.32 past the 56.0 fence, stamp 07:15:05, cross 07:15:20 hold 6 bars |
| 2026-09-04 07:43:15 | gcws30b oob 07:40:30..07:42:45, ws1r reversed 07:41:35 during, r 56.85 past the 56.0 fence, stamp 07:41:35, cross 07:42:50 hold 6 bars |
| 2026-09-04 08:00:15 | gcws30b ib 07:59:15, ws1r reversed 08:00:15 inside the 120s grace from the cross bar 07:59:15, r 92.09 past the 56.0 fence, stamp 08:00:15, hold 6 bars |
| 2026-09-04 08:00:35 | gcws30b ib 08:00:10, ws1r reversed 08:00:15 inside the 120s grace from the cross bar 08:00:10, r 92.09 past the 56.0 fence, stamp 08:00:15, hold 6 bars |
| 2026-09-04 08:15:30 | gcws30b ib 08:14:10, ws1r reversed 08:15:30 inside the 120s grace from the cross bar 08:14:10, r 58.05 past the 56.0 fence, stamp 08:15:30, hold 6 bars |
| 2026-09-04 08:52:50 | gcws30b oob 08:51:45..08:52:20, ws1r reversed 08:52:10 during, r 62.06 past the 56.0 fence, stamp 08:52:10, cross 08:52:25 hold 6 bars |
| 2026-09-04 09:00:25 | gcws30b oob 08:53:30..08:59:55, ws1r reversed 08:59:40 during, r 79.91 past the 56.0 fence, stamp 08:59:40, cross 09:00:00 hold 6 bars |
| 2026-09-04 09:18:00 | gcws30b ib 09:17:00, ws1r reversed 09:18:00 inside the 120s grace from the cross bar 09:17:00, r 63.73 past the 56.0 fence, stamp 09:18:00, hold 6 bars |
| 2026-09-04 11:10:05 | gcws30b oob 11:08:15..11:09:35, ws1r reversed 11:09:35 during, r 69.06 past the 56.0 fence, stamp 11:09:35, cross 11:09:40 hold 6 bars |
| 2026-09-04 11:14:55 | gcws30b oob 11:11:00..11:14:25, ws1r reversed 11:14:20 during, r 83.10 past the 56.0 fence, stamp 11:14:20, cross 11:14:30 hold 6 bars |
| 2026-09-04 11:16:40 | gcws30b ib 11:16:00, ws1r reversed 11:16:40 inside the 120s grace from the cross bar 11:16:00, r 61.00 past the 56.0 fence, stamp 11:16:40, hold 6 bars |
| 2026-09-04 11:35:30 | gcws30b oob 11:26:10..11:35:00, ws1r reversed 11:29:45 during, r 92.36 past the 56.0 fence, stamp 11:29:45, cross 11:35:05 hold 6 bars |
| 2026-09-04 11:45:30 | gcws30b ib 11:45:05, ws1r reversed 11:45:15 inside the 120s grace from the cross bar 11:45:05, r 73.11 past the 56.0 fence, stamp 11:45:15, hold 6 bars |
| 2026-09-04 12:21:35 | gcws30b oob 12:19:20..12:21:05, ws1r reversed 12:20:35 during, r 58.33 past the 56.0 fence, stamp 12:20:35, cross 12:21:10 hold 6 bars |
| 2026-09-04 13:41:20 | gcws30b ib 13:40:55, ws1r reversed 13:41:15 inside the 120s grace from the cross bar 13:40:55, r 60.35 past the 56.0 fence, stamp 13:41:15, hold 6 bars |
| 2026-09-04 13:44:05 | gcws30b ib 13:43:35, ws1r reversed 13:44:05 inside the 120s grace from the cross bar 13:43:35, r 83.95 past the 56.0 fence, stamp 13:44:05, hold 6 bars |
| 2026-09-04 13:44:50 | gcws30b ib 13:44:25, ws1r reversed 13:44:30 inside the 120s grace from the cross bar 13:44:25, r 79.59 past the 56.0 fence, stamp 13:44:30, hold 6 bars |
| 2026-09-04 13:51:00 | gcws30b oob 13:45:40..13:50:30, ws1r reversed 13:48:45 during, r 96.55 past the 56.0 fence, stamp 13:48:45, cross 13:50:35 hold 6 bars |
| 2026-09-04 15:27:30 | gcws30b ib 15:27:05, ws1r reversed 15:27:15 inside the 120s grace from the cross bar 15:27:05, r 82.19 past the 56.0 fence, stamp 15:27:15, hold 6 bars |
| 2026-09-04 15:42:00 | gcws30b ib 15:40:20, ws1r reversed 15:42:00 inside the 120s grace from the cross bar 15:40:20, r 69.12 past the 56.0 fence, stamp 15:42:00, hold 6 bars |
| 2026-09-04 15:48:00 | gcws30b oob 15:44:00..15:47:30, ws1r reversed 15:47:05 during, r 73.27 past the 56.0 fence, stamp 15:47:05, cross 15:47:35 hold 6 bars |
| 2026-09-04 15:49:40 | gcws30b oob 15:48:15..15:49:10, ws1r reversed 15:48:40 during, r 66.34 past the 56.0 fence, stamp 15:48:40, cross 15:49:15 hold 6 bars |
| 2026-09-04 16:38:15 | gcws30b oob 16:30:55..16:37:45, ws1r reversed 16:34:00 during, r 95.11 past the 56.0 fence, stamp 16:34:00, cross 16:37:50 hold 6 bars |
| 2026-09-04 16:54:00 | gcws30b oob 16:50:20..16:53:30, ws1r reversed 16:53:30 during, r 84.74 past the 56.0 fence, stamp 16:53:30, cross 16:53:35 hold 6 bars |
| 2026-09-04 18:08:30 | gcws30b oob 18:05:30..18:08:00, ws1r reversed 18:07:10 during, r 79.91 past the 56.0 fence, stamp 18:07:10, cross 18:08:05 hold 6 bars |
| 2026-09-04 21:43:10 | gcws30b oob 21:40:20..21:42:40, ws1r reversed 21:42:40 during, r 89.26 past the 56.0 fence, stamp 21:42:40, cross 21:42:45 hold 6 bars |
| 2026-09-04 22:44:10 | gcws30b oob 22:38:05..22:43:40, ws1r reversed 22:43:25 during, r 93.16 past the 56.0 fence, stamp 22:43:25, cross 22:43:45 hold 6 bars |
| 2026-09-04 23:15:00 | gcws30b oob 23:07:20..23:14:30, ws1r reversed 23:13:00 during, r 77.10 past the 56.0 fence, stamp 23:13:00, cross 23:14:35 hold 6 bars |
| 2026-09-04 23:25:05 | gcws30b ib 23:24:40, ws1r reversed 23:24:50 inside the 120s grace from the cross bar 23:24:40, r 72.70 past the 56.0 fence, stamp 23:24:50, hold 6 bars |
| 2026-09-04 23:38:50 | gcws30b ib 23:38:00, ws1r reversed 23:38:50 inside the 120s grace from the cross bar 23:38:00, r 73.43 past the 56.0 fence, stamp 23:38:50, hold 6 bars |

