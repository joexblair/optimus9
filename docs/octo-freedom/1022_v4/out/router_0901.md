# THE ROUTER. Joe 1024. 2026-09-01 00:00:00 .. 2026-09-01 23:59:55. max_pyramid 1.
# the mechs produce SIGNALS; the router owns the fire, the direction, the pyramid test
#   and the close-all rule. RULED_OK True.
# the control: ws5r 2026-09-03 00:35:00 = 12.48, expected 12.48

| the read | value |
|---|---|
| signals from core | 30 |
| signals from backstop | 5 |
| signals from saviour | 0 |
| signals routed | 35 |
| trades opened | 14 |
| signals DROPPED by the pyramid test | 21 |

| # | the signal | the open | dir | by | the close | MAE % | MFE % | detail |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-09-01 00:33:00 | 2026-09-01 00:33:05 | SHORT | core | 2026-09-01 01:37:15 | -0.662 | +1.207 | cws1b 2026-09-01 00:26:00, step2 arm 2026-09-01 00:26:00, ws2, exh 2026-09-01 00:33:00 |
| 2 | 2026-09-01 01:37:10 | 2026-09-01 01:37:15 | LONG | backstop | 2026-09-01 03:34:30 | -1.172 | +0.242 | fire 2026-09-01 01:16:55, ws4, exh 2026-09-01 01:37:10 |
| 3 | 2026-09-01 03:34:25 | 2026-09-01 03:34:30 | SHORT | core | 2026-09-01 06:57:30 | -1.437 | +0.930 | cws1b 2026-09-01 03:34:25, arm2 arm 2026-09-01 03:34:25, ws4 NOT oob - immediate exhaust |
| 4 | 2026-09-01 06:57:25 | 2026-09-01 06:57:30 | LONG | core | 2026-09-01 07:29:05 | -0.415 | +1.392 | cws1b 2026-09-01 06:57:25, arm2 arm 2026-09-01 06:57:25, ws4 NOT oob - immediate exhaust |
| 5 | 2026-09-01 07:29:00 | 2026-09-01 07:29:05 | SHORT | core | 2026-09-01 08:16:05 | -0.113 | +1.933 | cws1b 2026-09-01 07:23:00, step2 arm 2026-09-01 07:23:00, ws3, exh 2026-09-01 07:29:00 |
| 6 | 2026-09-01 08:16:00 | 2026-09-01 08:16:05 | LONG | core | 2026-09-01 10:07:35 | -1.986 | +0.046 | cws1b 2026-09-01 08:08:00, step2 arm 2026-09-01 08:08:00, ws2, exh 2026-09-01 08:16:00 |
| 7 | 2026-09-01 10:07:30 | 2026-09-01 10:07:35 | SHORT | backstop | 2026-09-01 13:14:35 | -3.566 | +0.294 | fire 2026-09-01 09:49:35, ws5, exh 2026-09-01 10:07:30 |
| 8 | 2026-09-01 13:14:30 | 2026-09-01 13:14:35 | LONG | core | 2026-09-01 13:50:30 | -0.074 | +2.210 | cws1b 2026-09-01 13:00:00, step2 arm 2026-09-01 13:00:00, ws3, exh 2026-09-01 13:14:30 |
| 9 | 2026-09-01 13:50:25 | 2026-09-01 13:50:30 | SHORT | core | 2026-09-01 15:15:15 | -0.392 | +1.962 | cws1b 2026-09-01 13:50:25, arm2 arm 2026-09-01 13:50:25, ws4 NOT oob - immediate exhaust |
| 10 | 2026-09-01 15:15:10 | 2026-09-01 15:15:15 | LONG | core | 2026-09-01 17:33:35 | -1.924 | +0.922 | cws1b 2026-09-01 15:02:00, step2 arm 2026-09-01 15:02:00, ws2, exh 2026-09-01 15:15:10 |
| 11 | 2026-09-01 17:33:30 | 2026-09-01 17:33:35 | SHORT | core | 2026-09-01 18:30:20 | -0.234 | +3.439 | cws1b 2026-09-01 17:30:00, step2 arm 2026-09-01 17:30:00, ws3, exh 2026-09-01 17:33:30 |
| 12 | 2026-09-01 18:30:15 | 2026-09-01 18:30:20 | LONG | core | 2026-09-01 19:43:15 | -2.992 | +0.746 | cws1b 2026-09-01 18:26:00, step2 arm 2026-09-01 18:26:00, ws3, exh 2026-09-01 18:30:15 |
| 13 | 2026-09-01 19:43:10 | 2026-09-01 19:43:15 | SHORT | backstop | 2026-09-01 20:31:15 | -0.081 | +1.198 | fire 2026-09-01 19:32:45, ws4, exh 2026-09-01 19:43:10 |
| 14 | 2026-09-01 20:31:10 | 2026-09-01 20:31:15 | LONG | core | still open | -2.752 | +0.258 | cws1b 2026-09-01 18:45:55, step2 arm 2026-09-01 19:53:00, ws3, exh 2026-09-01 20:31:10 |

# THE ROUTER'S OWN DECISIONS. Joe 1024 set the columns: the timestamp, the data passed
#   in, what the router did with it, and why it did that.
#   PASSED IN is the signal as the mech handed it over - its bar, its side, its mech.
#   WHY is the same-direction count AFTER the close against max_pyramid. That one
#   comparison is the only thing that decides OPEN or DROP; nothing else refuses.

| the bar | passed in | what the router did | why |
|---|---|---|---|
| 2026-09-01 00:33:05 | 2026-09-01 00:33:00 HIGH core | opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 01:37:15 | 2026-09-01 01:37:10 LOW backstop | closed the SHORT opened 2026-09-01 00:33:05, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 01:37:15 | 2026-09-01 01:37:10 LOW backstop | DROPPED the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 01:37:15 fills it |
| 2026-09-01 01:37:15 | 2026-09-01 01:37:10 LOW core | DROPPED the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 01:37:15 fills it |
| 2026-09-01 02:25:25 | 2026-09-01 02:25:20 LOW core | DROPPED the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 01:37:15 fills it |
| 2026-09-01 03:34:30 | 2026-09-01 03:34:25 HIGH core | closed the LONG opened 2026-09-01 01:37:15, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 04:29:00 | 2026-09-01 04:28:55 HIGH core | DROPPED the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 03:34:30 fills it |
| 2026-09-01 05:46:35 | 2026-09-01 05:46:30 HIGH core | DROPPED the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 03:34:30 fills it |
| 2026-09-01 06:57:30 | 2026-09-01 06:57:25 LOW core | closed the SHORT opened 2026-09-01 03:34:30, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 07:29:05 | 2026-09-01 07:29:00 HIGH core | closed the LONG opened 2026-09-01 06:57:30, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 08:16:05 | 2026-09-01 08:16:00 LOW core | closed the SHORT opened 2026-09-01 07:29:05, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 10:07:35 | 2026-09-01 10:07:30 HIGH backstop | closed the LONG opened 2026-09-01 08:16:05, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 10:26:35 | 2026-09-01 10:26:30 HIGH core | DROPPED the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 10:07:35 fills it |
| 2026-09-01 10:49:55 | 2026-09-01 10:49:50 HIGH core | DROPPED the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 10:07:35 fills it |
| 2026-09-01 10:49:55 | 2026-09-01 10:49:50 HIGH core | DROPPED the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 10:07:35 fills it |
| 2026-09-01 11:52:50 | 2026-09-01 11:52:45 HIGH core | DROPPED the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 10:07:35 fills it |
| 2026-09-01 11:52:50 | 2026-09-01 11:52:45 HIGH core | DROPPED the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 10:07:35 fills it |
| 2026-09-01 11:52:50 | 2026-09-01 11:52:45 HIGH core | DROPPED the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 10:07:35 fills it |
| 2026-09-01 13:14:35 | 2026-09-01 13:14:30 LOW core | closed the SHORT opened 2026-09-01 10:07:35, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 13:50:30 | 2026-09-01 13:50:25 HIGH core | closed the LONG opened 2026-09-01 13:14:35, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 14:17:40 | 2026-09-01 14:17:35 HIGH backstop | DROPPED the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 13:50:30 fills it |
| 2026-09-01 15:15:15 | 2026-09-01 15:15:10 LOW core | closed the SHORT opened 2026-09-01 13:50:30, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 16:28:45 | 2026-09-01 16:28:40 LOW core | DROPPED the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 15:15:15 fills it |
| 2026-09-01 17:33:35 | 2026-09-01 17:33:30 HIGH core | closed the LONG opened 2026-09-01 15:15:15, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 18:30:20 | 2026-09-01 18:30:15 LOW core | closed the SHORT opened 2026-09-01 17:33:35, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 18:30:25 | 2026-09-01 18:30:20 LOW core | DROPPED the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 18:30:20 fills it |
| 2026-09-01 18:55:15 | 2026-09-01 18:55:10 LOW core | DROPPED the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 18:30:20 fills it |
| 2026-09-01 18:55:15 | 2026-09-01 18:55:10 LOW core | DROPPED the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 18:30:20 fills it |
| 2026-09-01 18:55:15 | 2026-09-01 18:55:10 LOW core | DROPPED the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 18:30:20 fills it |
| 2026-09-01 19:43:15 | 2026-09-01 19:43:10 HIGH backstop | closed the LONG opened 2026-09-01 18:30:20, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 20:31:15 | 2026-09-01 20:31:10 LOW core | closed the SHORT opened 2026-09-01 19:43:15, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 20:31:15 | 2026-09-01 20:31:10 LOW core | DROPPED the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 20:31:15 fills it |
| 2026-09-01 20:31:15 | 2026-09-01 20:31:10 LOW core | DROPPED the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 20:31:15 fills it |
| 2026-09-01 20:54:30 | 2026-09-01 20:54:25 LOW core | DROPPED the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 20:31:15 fills it |
| 2026-09-01 21:19:50 | 2026-09-01 21:19:45 LOW core | DROPPED the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 20:31:15 fills it |

# THE SIGNALS THE PYRAMID TEST DROPPED. Each was acted on once, at its own bar + 1,
#   and refused. There is no queue, so none of these is retried.

| the signal | side | by | the bar it was refused | detail |
|---|---|---|---|---|
| 2026-09-01 01:37:10 | LOW | backstop | 2026-09-01 01:37:15 | fire 2026-09-01 01:18:40, ws4, exh 2026-09-01 01:37:10 |
| 2026-09-01 01:37:10 | LOW | core | 2026-09-01 01:37:15 | cws1b 2026-09-01 01:14:25, arm2 arm 2026-09-01 01:14:25, ws4, exh 2026-09-01 01:37:10 |
| 2026-09-01 02:25:20 | LOW | core | 2026-09-01 02:25:25 | cws1b 2026-09-01 02:12:00, step2 arm 2026-09-01 02:12:00, ws3, exh 2026-09-01 02:25:20 |
| 2026-09-01 04:28:55 | HIGH | core | 2026-09-01 04:29:00 | cws1b 2026-09-01 03:41:55, step2 arm 2026-09-01 04:26:00, ws2, exh 2026-09-01 04:28:55 |
| 2026-09-01 05:46:30 | HIGH | core | 2026-09-01 05:46:35 | cws1b 2026-09-01 05:36:00, step2 arm 2026-09-01 05:36:00, ws2, exh 2026-09-01 05:46:30 |
| 2026-09-01 10:26:30 | HIGH | core | 2026-09-01 10:26:35 | cws1b 2026-09-01 10:24:00, step2 arm 2026-09-01 10:24:00, ws2, exh 2026-09-01 10:26:30 |
| 2026-09-01 10:49:50 | HIGH | core | 2026-09-01 10:49:55 | cws1b 2026-09-01 10:30:00, step2 arm 2026-09-01 10:30:00, ws3, exh 2026-09-01 10:49:50 |
| 2026-09-01 10:49:50 | HIGH | core | 2026-09-01 10:49:55 | cws1b 2026-09-01 10:36:00, step2 arm 2026-09-01 10:36:00, ws3, exh 2026-09-01 10:49:50 |
| 2026-09-01 11:52:45 | HIGH | core | 2026-09-01 11:52:50 | cws1b 2026-09-01 10:42:55, step2 arm 2026-09-01 11:25:00, ws2, exh 2026-09-01 11:52:45 |
| 2026-09-01 11:52:45 | HIGH | core | 2026-09-01 11:52:50 | cws1b 2026-09-01 11:31:00, step2 arm 2026-09-01 11:31:00, ws3, exh 2026-09-01 11:52:45 |
| 2026-09-01 11:52:45 | HIGH | core | 2026-09-01 11:52:50 | cws1b 2026-09-01 11:35:00, step2 arm 2026-09-01 11:35:00, ws3, exh 2026-09-01 11:52:45 |
| 2026-09-01 14:17:35 | HIGH | backstop | 2026-09-01 14:17:40 | fire 2026-09-01 13:37:15, ws4, exh 2026-09-01 14:17:35 |
| 2026-09-01 16:28:40 | LOW | core | 2026-09-01 16:28:45 | cws1b 2026-09-01 15:12:55, step2 arm 2026-09-01 16:06:00, ws3, exh 2026-09-01 16:28:40 |
| 2026-09-01 18:30:20 | LOW | core | 2026-09-01 18:30:25 | cws1b 2026-09-01 18:20:00, step2 arm 2026-09-01 18:20:00, ws2, exh 2026-09-01 18:30:20 |
| 2026-09-01 18:55:10 | LOW | core | 2026-09-01 18:55:15 | cws1b 2026-09-01 16:25:55, step2 arm 2026-09-01 17:54:00, ws2, exh 2026-09-01 18:55:10 |
| 2026-09-01 18:55:10 | LOW | core | 2026-09-01 18:55:15 | cws1b 2026-09-01 17:59:00, step2 arm 2026-09-01 17:59:00, ws3, exh 2026-09-01 18:55:10 |
| 2026-09-01 18:55:10 | LOW | core | 2026-09-01 18:55:15 | cws1b 2026-09-01 18:08:00, step2 arm 2026-09-01 18:08:00, ws3, exh 2026-09-01 18:55:10 |
| 2026-09-01 20:31:10 | LOW | core | 2026-09-01 20:31:15 | cws1b 2026-09-01 19:57:00, step2 arm 2026-09-01 19:57:00, ws3, exh 2026-09-01 20:31:10 |
| 2026-09-01 20:31:10 | LOW | core | 2026-09-01 20:31:15 | cws1b 2026-09-01 20:02:00, step2 arm 2026-09-01 20:02:00, ws3, exh 2026-09-01 20:31:10 |
| 2026-09-01 20:54:25 | LOW | core | 2026-09-01 20:54:30 | cws1b 2026-09-01 20:51:00, step2 arm 2026-09-01 20:51:00, ws2, exh 2026-09-01 20:54:25 |
| 2026-09-01 21:19:45 | LOW | core | 2026-09-01 21:19:50 | cws1b 2026-09-01 21:16:00, step2 arm 2026-09-01 21:16:00, ws2, exh 2026-09-01 21:19:45 |
