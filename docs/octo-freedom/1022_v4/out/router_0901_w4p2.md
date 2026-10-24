# THE ROUTER. Joe 1024. 2026-09-01 00:00:00 .. 2026-09-01 23:59:55. max_pyramid 2.
# the mechs produce SIGNALS; the router owns the fire, the direction, the pyramid test
#   and the close-all rule. RULED_OK False.
# the control: ws5r 2026-09-03 00:35:00 = 12.48, expected 12.48

| the read | value |
|---|---|
| signals from core | 30 |
| signals from backstop | 5 |
| signals from saviour | 4 |
|   of those, saviour generation 1 | 4 |
| signals routed | 39 |
| trades opened | 27 |
| signals DROPPED by the pyramid test | 12 |

| # | the signal | the open | dir | by | the close | MAE % | MFE % | detail |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-09-01 00:33:00 | 2026-09-01 00:33:05 | SHORT | core | 2026-09-01 01:37:15 | -0.662 | +1.207 | step2 arm 00:26:00, ws2 |
| 2 | 2026-09-01 01:37:10 | 2026-09-01 01:37:15 | LONG | backstop | 2026-09-01 03:34:30 | -1.172 | +0.242 | fire 01:16:55, ws4 |
| 3 | 2026-09-01 01:37:10 | 2026-09-01 01:37:15 | LONG | backstop | 2026-09-01 03:34:30 | -1.172 | +0.242 | fire 01:18:40, ws4 |
| 4 | 2026-09-01 03:34:25 | 2026-09-01 03:34:30 | SHORT | core | 2026-09-01 04:41:50 | -0.344 | +0.688 | arm2 arm 03:34:25, ws4 NOT oob - immediate exhaust |
| 5 | 2026-09-01 04:28:55 | 2026-09-01 04:29:00 | SHORT | core | 2026-09-01 04:41:50 | -0.057 | +0.339 | step2 arm 04:26:00, ws2 |
| 6 | 2026-09-01 04:41:45 | 2026-09-01 04:41:50 | LONG | saviour | 2026-09-01 05:59:00 | -0.328 | +1.879 | armed on the HIGH core signal 04:28:55 |
| 7 | 2026-09-01 05:58:55 | 2026-09-01 05:59:00 | SHORT | core | 2026-09-01 06:57:30 | -0.067 | +1.881 | step2 arm 05:36:00, ws2 |
| 8 | 2026-09-01 06:57:25 | 2026-09-01 06:57:30 | LONG | core | 2026-09-01 07:29:05 | -0.415 | +1.392 | arm2 arm 06:57:25, ws4 NOT oob - immediate exhaust |
| 9 | 2026-09-01 07:29:00 | 2026-09-01 07:29:05 | SHORT | core | 2026-09-01 08:16:05 | -0.113 | +1.933 | step2 arm 07:23:00, ws3 |
| 10 | 2026-09-01 08:16:00 | 2026-09-01 08:16:05 | LONG | core | 2026-09-01 10:07:35 | -1.986 | +0.046 | step2 arm 08:08:00, ws2 |
| 11 | 2026-09-01 10:07:30 | 2026-09-01 10:07:35 | SHORT | backstop | 2026-09-01 13:14:35 | -3.566 | +0.294 | fire 09:49:35, ws5 |
| 12 | 2026-09-01 10:26:30 | 2026-09-01 10:26:35 | SHORT | core | 2026-09-01 13:14:35 | -2.659 | +1.167 | step2 arm 10:24:00, ws2 |
| 13 | 2026-09-01 13:14:30 | 2026-09-01 13:14:35 | LONG | core | 2026-09-01 13:50:30 | -0.074 | +2.210 | step2 arm 13:00:00, ws3 |
| 14 | 2026-09-01 13:50:25 | 2026-09-01 13:50:30 | SHORT | core | 2026-09-01 15:28:55 | -0.392 | +1.962 | arm2 arm 13:50:25, ws4 NOT oob - immediate exhaust |
| 15 | 2026-09-01 14:17:35 | 2026-09-01 14:17:40 | SHORT | backstop | 2026-09-01 15:28:55 | -0.943 | +1.270 | fire 13:37:15, ws4 |
| 16 | 2026-09-01 15:28:50 | 2026-09-01 15:28:55 | LONG | core | 2026-09-01 17:33:35 | -2.268 | +0.567 | step2 arm 15:02:00, ws2 |
| 17 | 2026-09-01 16:37:35 | 2026-09-01 16:37:40 | LONG | core | 2026-09-01 17:33:35 | -0.098 | +1.477 | step2 arm 16:06:00, ws3 |
| 18 | 2026-09-01 17:33:30 | 2026-09-01 17:33:35 | SHORT | core | 2026-09-01 18:13:20 | -0.234 | +1.602 | step2 arm 17:30:00, ws3 |
| 19 | 2026-09-01 18:13:15 | 2026-09-01 18:13:20 | LONG | core | 2026-09-01 19:43:15 | -3.949 | +0.006 | step2 arm 17:54:00, ws2 |
| 20 | 2026-09-01 18:13:15 | 2026-09-01 18:13:20 | LONG | core | 2026-09-01 19:43:15 | -3.949 | +0.006 | step2 arm 17:59:00, ws3 |
| 21 | 2026-09-01 19:43:10 | 2026-09-01 19:43:15 | SHORT | backstop | 2026-09-01 20:50:20 | -0.081 | +1.367 | fire 19:32:45, ws4 |
| 22 | 2026-09-01 20:50:15 | 2026-09-01 20:50:20 | LONG | core | 2026-09-01 21:02:00 | -0.435 | +0.541 | step2 arm 19:53:00, ws3 |
| 23 | 2026-09-01 20:50:15 | 2026-09-01 20:50:20 | LONG | core | 2026-09-01 21:02:00 | -0.435 | +0.541 | step2 arm 19:57:00, ws3 |
| 24 | 2026-09-01 21:01:55 | 2026-09-01 21:02:00 | SHORT | saviour | 2026-09-01 21:19:50 | -0.294 | +1.627 | armed on the LOW core signal 20:50:15 |
| 25 | 2026-09-01 21:01:55 | 2026-09-01 21:02:00 | SHORT | saviour | 2026-09-01 21:19:50 | -0.294 | +1.627 | armed on the LOW core signal 20:54:25 |
| 26 | 2026-09-01 21:19:45 | 2026-09-01 21:19:50 | LONG | core | 2026-09-01 21:24:55 | -0.196 | +0.457 | step2 arm 21:16:00, ws2 |
| 27 | 2026-09-01 21:24:50 | 2026-09-01 21:24:55 | SHORT | saviour | still open | -0.189 | +1.883 | armed on the LOW core signal 21:19:45 |

# THE ROUTER'S OWN DECISIONS. Joe 1024 set the columns: the timestamp, the data passed
#   in, what the router did with it, and why it did that.
#   PASSED IN is the signal as the mech handed it over - its bar, its side, its mech.
#   WHY is the same-direction count AFTER the close against max_pyramid. That one
#   comparison is the only thing that decides OPEN or DROP; nothing else refuses.

| the bar | passed in | what the router did | why |
|---|---|---|---|
| 2026-09-01 00:33:05 | 2026-09-01 00:33:00 HIGH core | opened a SHORT | 0 SHORT open of max 2 |
| 2026-09-01 01:37:15 | 2026-09-01 01:37:10 LOW backstop | closed the SHORT opened 2026-09-01 00:33:05, then opened a LONG | 0 LONG open of max 2 |
| 2026-09-01 01:37:15 | 2026-09-01 01:37:10 LOW backstop | opened a LONG | 1 LONG open of max 2 |
| 2026-09-01 01:37:15 | 2026-09-01 01:37:10 LOW core | DROPPED the LONG | 2 LONG open of max 2 - the LONG opened 2026-09-01 01:37:15, 2026-09-01 01:37:15 fills it |
| 2026-09-01 02:40:45 | 2026-09-01 02:40:40 LOW core | DROPPED the LONG | 2 LONG open of max 2 - the LONG opened 2026-09-01 01:37:15, 2026-09-01 01:37:15 fills it |
| 2026-09-01 03:34:30 | 2026-09-01 03:34:25 HIGH core | closed the LONG opened 2026-09-01 01:37:15, 2026-09-01 01:37:15, then opened a SHORT | 0 SHORT open of max 2 |
| 2026-09-01 04:29:00 | 2026-09-01 04:28:55 HIGH core | opened a SHORT | 1 SHORT open of max 2 |
| 2026-09-01 04:41:50 | 2026-09-01 04:41:45 LOW saviour | closed the SHORT opened 2026-09-01 03:34:30, 2026-09-01 04:29:00, then opened a LONG | 0 LONG open of max 2 |
| 2026-09-01 05:59:00 | 2026-09-01 05:58:55 HIGH core | closed the LONG opened 2026-09-01 04:41:50, then opened a SHORT | 0 SHORT open of max 2 |
| 2026-09-01 06:57:30 | 2026-09-01 06:57:25 LOW core | closed the SHORT opened 2026-09-01 05:59:00, then opened a LONG | 0 LONG open of max 2 |
| 2026-09-01 07:29:05 | 2026-09-01 07:29:00 HIGH core | closed the LONG opened 2026-09-01 06:57:30, then opened a SHORT | 0 SHORT open of max 2 |
| 2026-09-01 08:16:05 | 2026-09-01 08:16:00 LOW core | closed the SHORT opened 2026-09-01 07:29:05, then opened a LONG | 0 LONG open of max 2 |
| 2026-09-01 10:07:35 | 2026-09-01 10:07:30 HIGH backstop | closed the LONG opened 2026-09-01 08:16:05, then opened a SHORT | 0 SHORT open of max 2 |
| 2026-09-01 10:26:35 | 2026-09-01 10:26:30 HIGH core | opened a SHORT | 1 SHORT open of max 2 |
| 2026-09-01 11:24:15 | 2026-09-01 11:24:10 HIGH core | DROPPED the SHORT | 2 SHORT open of max 2 - the SHORT opened 2026-09-01 10:07:35, 2026-09-01 10:26:35 fills it |
| 2026-09-01 11:24:15 | 2026-09-01 11:24:10 HIGH core | DROPPED the SHORT | 2 SHORT open of max 2 - the SHORT opened 2026-09-01 10:07:35, 2026-09-01 10:26:35 fills it |
| 2026-09-01 11:48:45 | 2026-09-01 11:48:40 HIGH core | DROPPED the SHORT | 2 SHORT open of max 2 - the SHORT opened 2026-09-01 10:07:35, 2026-09-01 10:26:35 fills it |
| 2026-09-01 11:48:45 | 2026-09-01 11:48:40 HIGH core | DROPPED the SHORT | 2 SHORT open of max 2 - the SHORT opened 2026-09-01 10:07:35, 2026-09-01 10:26:35 fills it |
| 2026-09-01 11:48:45 | 2026-09-01 11:48:40 HIGH core | DROPPED the SHORT | 2 SHORT open of max 2 - the SHORT opened 2026-09-01 10:07:35, 2026-09-01 10:26:35 fills it |
| 2026-09-01 13:14:35 | 2026-09-01 13:14:30 LOW core | closed the SHORT opened 2026-09-01 10:07:35, 2026-09-01 10:26:35, then opened a LONG | 0 LONG open of max 2 |
| 2026-09-01 13:50:30 | 2026-09-01 13:50:25 HIGH core | closed the LONG opened 2026-09-01 13:14:35, then opened a SHORT | 0 SHORT open of max 2 |
| 2026-09-01 14:17:40 | 2026-09-01 14:17:35 HIGH backstop | opened a SHORT | 1 SHORT open of max 2 |
| 2026-09-01 15:28:55 | 2026-09-01 15:28:50 LOW core | closed the SHORT opened 2026-09-01 13:50:30, 2026-09-01 14:17:40, then opened a LONG | 0 LONG open of max 2 |
| 2026-09-01 16:37:40 | 2026-09-01 16:37:35 LOW core | opened a LONG | 1 LONG open of max 2 |
| 2026-09-01 17:33:35 | 2026-09-01 17:33:30 HIGH core | closed the LONG opened 2026-09-01 15:28:55, 2026-09-01 16:37:40, then opened a SHORT | 0 SHORT open of max 2 |
| 2026-09-01 18:13:20 | 2026-09-01 18:13:15 LOW core | closed the SHORT opened 2026-09-01 17:33:35, then opened a LONG | 0 LONG open of max 2 |
| 2026-09-01 18:13:20 | 2026-09-01 18:13:15 LOW core | opened a LONG | 1 LONG open of max 2 |
| 2026-09-01 18:13:20 | 2026-09-01 18:13:15 LOW core | DROPPED the LONG | 2 LONG open of max 2 - the LONG opened 2026-09-01 18:13:20, 2026-09-01 18:13:20 fills it |
| 2026-09-01 18:30:20 | 2026-09-01 18:30:15 LOW core | DROPPED the LONG | 2 LONG open of max 2 - the LONG opened 2026-09-01 18:13:20, 2026-09-01 18:13:20 fills it |
| 2026-09-01 18:30:25 | 2026-09-01 18:30:20 LOW core | DROPPED the LONG | 2 LONG open of max 2 - the LONG opened 2026-09-01 18:13:20, 2026-09-01 18:13:20 fills it |
| 2026-09-01 19:43:15 | 2026-09-01 19:43:10 HIGH backstop | closed the LONG opened 2026-09-01 18:13:20, 2026-09-01 18:13:20, then opened a SHORT | 0 SHORT open of max 2 |
| 2026-09-01 20:50:20 | 2026-09-01 20:50:15 LOW core | closed the SHORT opened 2026-09-01 19:43:15, then opened a LONG | 0 LONG open of max 2 |
| 2026-09-01 20:50:20 | 2026-09-01 20:50:15 LOW core | opened a LONG | 1 LONG open of max 2 |
| 2026-09-01 20:50:20 | 2026-09-01 20:50:15 LOW core | DROPPED the LONG | 2 LONG open of max 2 - the LONG opened 2026-09-01 20:50:20, 2026-09-01 20:50:20 fills it |
| 2026-09-01 20:54:30 | 2026-09-01 20:54:25 LOW core | DROPPED the LONG | 2 LONG open of max 2 - the LONG opened 2026-09-01 20:50:20, 2026-09-01 20:50:20 fills it |
| 2026-09-01 21:02:00 | 2026-09-01 21:01:55 HIGH saviour | closed the LONG opened 2026-09-01 20:50:20, 2026-09-01 20:50:20, then opened a SHORT | 0 SHORT open of max 2 |
| 2026-09-01 21:02:00 | 2026-09-01 21:01:55 HIGH saviour | opened a SHORT | 1 SHORT open of max 2 |
| 2026-09-01 21:19:50 | 2026-09-01 21:19:45 LOW core | closed the SHORT opened 2026-09-01 21:02:00, 2026-09-01 21:02:00, then opened a LONG | 0 LONG open of max 2 |
| 2026-09-01 21:24:55 | 2026-09-01 21:24:50 HIGH saviour | closed the LONG opened 2026-09-01 21:19:50, then opened a SHORT | 0 SHORT open of max 2 |

# THE SIGNALS THE PYRAMID TEST DROPPED. Each was acted on once, at its own bar + 1,
#   and refused. There is no queue, so none of these is retried.

| the signal | side | by | the bar it was refused | detail |
|---|---|---|---|---|
| 2026-09-01 01:37:10 | LOW | core | 2026-09-01 01:37:15 | arm2 arm 01:14:25, ws4 |
| 2026-09-01 02:40:40 | LOW | core | 2026-09-01 02:40:45 | step2 arm 02:12:00, ws3 |
| 2026-09-01 11:24:10 | HIGH | core | 2026-09-01 11:24:15 | step2 arm 10:30:00, ws3 |
| 2026-09-01 11:24:10 | HIGH | core | 2026-09-01 11:24:15 | step2 arm 10:36:00, ws3 |
| 2026-09-01 11:48:40 | HIGH | core | 2026-09-01 11:48:45 | step2 arm 11:25:00, ws2 |
| 2026-09-01 11:48:40 | HIGH | core | 2026-09-01 11:48:45 | step2 arm 11:31:00, ws3 |
| 2026-09-01 11:48:40 | HIGH | core | 2026-09-01 11:48:45 | step2 arm 11:35:00, ws3 |
| 2026-09-01 18:13:15 | LOW | core | 2026-09-01 18:13:20 | step2 arm 18:08:00, ws3 |
| 2026-09-01 18:30:15 | LOW | core | 2026-09-01 18:30:20 | step2 arm 18:26:00, ws3 |
| 2026-09-01 18:30:20 | LOW | core | 2026-09-01 18:30:25 | step2 arm 18:20:00, ws2 |
| 2026-09-01 20:50:15 | LOW | core | 2026-09-01 20:50:20 | step2 arm 20:02:00, ws3 |
| 2026-09-01 20:54:25 | LOW | core | 2026-09-01 20:54:30 | step2 arm 20:51:00, ws2 |
