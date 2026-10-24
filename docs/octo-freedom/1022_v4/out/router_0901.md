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
| trades opened | 32 |
| signals still HELD at the window end | 5 |

| # | the signal | the open | wait | dir | by | the close | MAE % | MFE % | detail |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-09-01 00:33:00 | 2026-09-01 00:33:05 | - | SHORT | core | 2026-09-01 01:37:15 | -0.662 | +1.207 | cws1b 2026-09-01 00:26:00, step2 arm 2026-09-01 00:26:00, ws2, exh 2026-09-01 00:33:00 |
| 2 | 2026-09-01 01:37:10 | 2026-09-01 01:37:15 | - | LONG | backstop | 2026-09-01 03:34:30 | -1.172 | +0.242 | fire 2026-09-01 01:16:55, ws4, exh 2026-09-01 01:37:10 |
| 3 | 2026-09-01 03:34:25 | 2026-09-01 03:34:30 | - | SHORT | core | 2026-09-01 04:28:55 | -0.344 | +0.688 | cws1b 2026-09-01 03:34:25, arm2 arm 2026-09-01 03:34:25, ws4 NOT oob - immediate exhaust |
| 4 | 2026-09-01 01:37:10 | 2026-09-01 04:28:55 | 171m45s | LONG | backstop | 2026-09-01 04:29:00 | -0.107 | +0.000 | fire 2026-09-01 01:18:40, ws4, exh 2026-09-01 01:37:10 |
| 5 | 2026-09-01 04:28:55 | 2026-09-01 04:29:00 | - | SHORT | core | 2026-09-01 04:41:45 | -0.057 | +0.339 | cws1b 2026-09-01 03:41:55, step2 arm 2026-09-01 04:26:00, ws2, exh 2026-09-01 04:28:55 |
| 6 | 2026-09-01 01:37:10 | 2026-09-01 04:41:45 | 184m35s | LONG | core | 2026-09-01 05:46:35 | -0.356 | +1.850 | cws1b 2026-09-01 01:14:25, arm2 arm 2026-09-01 01:14:25, ws4, exh 2026-09-01 01:37:10 |
| 7 | 2026-09-01 05:46:30 | 2026-09-01 05:46:35 | - | SHORT | core | 2026-09-01 05:52:20 | -0.234 | +0.201 | cws1b 2026-09-01 05:36:00, step2 arm 2026-09-01 05:36:00, ws2, exh 2026-09-01 05:46:30 |
| 8 | 2026-09-01 02:25:20 | 2026-09-01 05:52:20 | 207m00s | LONG | core | 2026-09-01 07:29:05 | -2.204 | +0.156 | cws1b 2026-09-01 02:12:00, step2 arm 2026-09-01 02:12:00, ws3, exh 2026-09-01 02:25:20 |
| 9 | 2026-09-01 07:29:00 | 2026-09-01 07:29:05 | - | SHORT | core | 2026-09-01 08:16:00 | -0.113 | +1.933 | cws1b 2026-09-01 07:23:00, step2 arm 2026-09-01 07:23:00, ws3, exh 2026-09-01 07:29:00 |
| 10 | 2026-09-01 04:41:45 | 2026-09-01 08:16:00 | 214m15s | LONG | saviour | 2026-09-01 10:07:35 | -1.986 | +0.057 | fill 2026-09-01 04:41:45, armed on the SHORT block opened 2026-09-01 04:29:00 |
| 11 | 2026-09-01 10:07:30 | 2026-09-01 10:07:35 | - | SHORT | backstop | 2026-09-01 10:26:30 | -1.062 | +0.040 | fire 2026-09-01 09:49:35, ws5, exh 2026-09-01 10:07:30 |
| 12 | 2026-09-01 05:52:20 | 2026-09-01 10:26:30 | 274m10s | LONG | saviour | 2026-09-01 10:26:35 | -0.074 | +0.034 | fill 2026-09-01 05:52:20, armed on the SHORT block opened 2026-09-01 05:46:35 |
| 13 | 2026-09-01 10:26:30 | 2026-09-01 10:26:35 | - | SHORT | core | 2026-09-01 10:49:50 | -1.201 | +0.057 | cws1b 2026-09-01 10:24:00, step2 arm 2026-09-01 10:24:00, ws2, exh 2026-09-01 10:26:30 |
| 14 | 2026-09-01 06:57:25 | 2026-09-01 10:49:50 | 232m25s | LONG | core | 2026-09-01 10:49:55 | -0.023 | +0.023 | cws1b 2026-09-01 06:57:25, arm2 arm 2026-09-01 06:57:25, ws4 NOT oob - immediate exhaust |
| 15 | 2026-09-01 10:49:50 | 2026-09-01 10:49:55 | - | SHORT | core | 2026-09-01 11:52:45 | -1.856 | +0.465 | cws1b 2026-09-01 10:30:00, step2 arm 2026-09-01 10:30:00, ws3, exh 2026-09-01 10:49:50 |
| 16 | 2026-09-01 08:16:00 | 2026-09-01 11:52:45 | 216m45s | LONG | core | 2026-09-01 11:52:45 | +0.000 | +0.017 | cws1b 2026-09-01 08:08:00, step2 arm 2026-09-01 08:08:00, ws2, exh 2026-09-01 08:16:00 |
| 17 | 2026-09-01 10:49:50 | 2026-09-01 11:52:45 | 62m55s | SHORT | core | 2026-09-01 13:14:35 | -0.370 | +3.226 | cws1b 2026-09-01 10:36:00, step2 arm 2026-09-01 10:36:00, ws3, exh 2026-09-01 10:49:50 |
| 18 | 2026-09-01 13:14:30 | 2026-09-01 13:14:35 | - | LONG | core | 2026-09-01 13:50:25 | -0.074 | +2.210 | cws1b 2026-09-01 13:00:00, step2 arm 2026-09-01 13:00:00, ws3, exh 2026-09-01 13:14:30 |
| 19 | 2026-09-01 11:52:45 | 2026-09-01 13:50:25 | 117m40s | SHORT | core | 2026-09-01 15:15:15 | -0.415 | +1.940 | cws1b 2026-09-01 10:42:55, step2 arm 2026-09-01 11:25:00, ws2, exh 2026-09-01 11:52:45 |
| 20 | 2026-09-01 15:15:10 | 2026-09-01 15:15:15 | - | LONG | core | 2026-09-01 16:28:40 | -1.628 | +0.922 | cws1b 2026-09-01 15:02:00, step2 arm 2026-09-01 15:02:00, ws2, exh 2026-09-01 15:15:10 |
| 21 | 2026-09-01 11:52:45 | 2026-09-01 16:28:40 | 275m55s | SHORT | core | 2026-09-01 16:28:45 | -0.006 | +0.011 | cws1b 2026-09-01 11:31:00, step2 arm 2026-09-01 11:31:00, ws3, exh 2026-09-01 11:52:45 |
| 22 | 2026-09-01 16:28:40 | 2026-09-01 16:28:45 | - | LONG | core | 2026-09-01 17:33:30 | -0.971 | +1.098 | cws1b 2026-09-01 15:12:55, step2 arm 2026-09-01 16:06:00, ws3, exh 2026-09-01 16:28:40 |
| 23 | 2026-09-01 11:52:45 | 2026-09-01 17:33:30 | 340m45s | SHORT | core | 2026-09-01 18:30:20 | -0.234 | +3.439 | cws1b 2026-09-01 11:35:00, step2 arm 2026-09-01 11:35:00, ws3, exh 2026-09-01 11:52:45 |
| 24 | 2026-09-01 18:30:15 | 2026-09-01 18:30:20 | - | LONG | core | 2026-09-01 18:30:20 | -0.076 | +0.000 | cws1b 2026-09-01 18:26:00, step2 arm 2026-09-01 18:26:00, ws3, exh 2026-09-01 18:30:15 |
| 25 | 2026-09-01 13:50:25 | 2026-09-01 18:30:20 | 279m55s | SHORT | core | 2026-09-01 18:30:25 | -0.017 | +0.076 | cws1b 2026-09-01 13:50:25, arm2 arm 2026-09-01 13:50:25, ws4 NOT oob - immediate exhaust |
| 26 | 2026-09-01 18:30:20 | 2026-09-01 18:30:25 | - | LONG | core | 2026-09-01 18:55:10 | -2.952 | +0.058 | cws1b 2026-09-01 18:20:00, step2 arm 2026-09-01 18:20:00, ws2, exh 2026-09-01 18:30:20 |
| 27 | 2026-09-01 14:17:35 | 2026-09-01 18:55:10 | 277m35s | SHORT | backstop | 2026-09-01 18:55:15 | +0.000 | +0.065 | fire 2026-09-01 13:37:15, ws4, exh 2026-09-01 14:17:35 |
| 28 | 2026-09-01 18:55:10 | 2026-09-01 18:55:15 | - | LONG | core | 2026-09-01 19:43:10 | -0.012 | +1.689 | cws1b 2026-09-01 16:25:55, step2 arm 2026-09-01 17:54:00, ws2, exh 2026-09-01 18:55:10 |
| 29 | 2026-09-01 18:55:10 | 2026-09-01 19:43:10 | 48m00s | LONG | core | 2026-09-01 19:43:15 | +0.000 | +0.017 | cws1b 2026-09-01 17:59:00, step2 arm 2026-09-01 17:59:00, ws3, exh 2026-09-01 18:55:10 |
| 30 | 2026-09-01 17:33:30 | 2026-09-01 19:43:10 | 129m40s | SHORT | core | 2026-09-01 19:43:10 | +0.000 | +0.000 | cws1b 2026-09-01 17:30:00, step2 arm 2026-09-01 17:30:00, ws3, exh 2026-09-01 17:33:30 |
| 31 | 2026-09-01 19:43:10 | 2026-09-01 19:43:15 | - | SHORT | backstop | 2026-09-01 20:31:10 | -0.081 | +1.198 | fire 2026-09-01 19:32:45, ws4, exh 2026-09-01 19:43:10 |
| 32 | 2026-09-01 18:55:10 | 2026-09-01 20:31:10 | 96m00s | LONG | core | still open | -2.752 | +0.258 | cws1b 2026-09-01 18:08:00, step2 arm 2026-09-01 18:08:00, ws3, exh 2026-09-01 18:55:10 |

# THE ROUTER'S OWN DECISIONS. Joe 1024 set the columns: the timestamp, the data passed
#   in, what the router did with it, and why it did that.
#   PASSED IN is the signal as the mech handed it over - its bar, its side, its mech.
#   WHY is the same-direction count AFTER the close against max_pyramid. That one
#   comparison is the only thing that decides OPEN or HOLD; nothing else refuses.

| the bar | passed in | what the router did | why |
|---|---|---|---|
| 2026-09-01 00:33:05 | 2026-09-01 00:33:00 HIGH core | opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 01:37:15 | 2026-09-01 01:37:10 LOW backstop | closed the SHORT opened 2026-09-01 00:33:05, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 01:37:15 | 2026-09-01 01:37:10 LOW backstop | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 01:37:15 fills it |
| 2026-09-01 01:37:15 | 2026-09-01 01:37:10 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 01:37:15 fills it |
| 2026-09-01 02:25:20 | 2026-09-01 01:37:10 LOW backstop | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 01:37:15 fills it |
| 2026-09-01 02:25:20 | 2026-09-01 01:37:10 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 01:37:15 fills it |
| 2026-09-01 02:25:25 | 2026-09-01 02:25:20 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 01:37:15 fills it |
| 2026-09-01 03:34:25 | 2026-09-01 01:37:10 LOW backstop | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 01:37:15 fills it |
| 2026-09-01 03:34:25 | 2026-09-01 01:37:10 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 01:37:15 fills it |
| 2026-09-01 03:34:25 | 2026-09-01 02:25:20 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 01:37:15 fills it |
| 2026-09-01 03:34:30 | 2026-09-01 03:34:25 HIGH core | closed the LONG opened 2026-09-01 01:37:15, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 04:28:55 | 2026-09-01 01:37:10 LOW backstop | closed the SHORT opened 2026-09-01 03:34:30, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 04:28:55 | 2026-09-01 01:37:10 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 04:28:55 fills it |
| 2026-09-01 04:28:55 | 2026-09-01 02:25:20 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 04:28:55 fills it |
| 2026-09-01 04:29:00 | 2026-09-01 04:28:55 HIGH core | closed the LONG opened 2026-09-01 04:28:55, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 04:41:45 | 2026-09-01 01:37:10 LOW core | closed the SHORT opened 2026-09-01 04:29:00, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 04:41:45 | 2026-09-01 02:25:20 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 04:41:45 fills it |
| 2026-09-01 04:41:50 | 2026-09-01 04:41:45 LOW saviour | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 04:41:45 fills it |
| 2026-09-01 05:46:30 | 2026-09-01 02:25:20 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 04:41:45 fills it |
| 2026-09-01 05:46:30 | 2026-09-01 04:41:45 LOW saviour | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 04:41:45 fills it |
| 2026-09-01 05:46:35 | 2026-09-01 05:46:30 HIGH core | closed the LONG opened 2026-09-01 04:41:45, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 05:52:20 | 2026-09-01 02:25:20 LOW core | closed the SHORT opened 2026-09-01 05:46:35, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 05:52:20 | 2026-09-01 04:41:45 LOW saviour | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 05:52:20 fills it |
| 2026-09-01 05:52:25 | 2026-09-01 05:52:20 LOW saviour | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 05:52:20 fills it |
| 2026-09-01 06:57:25 | 2026-09-01 04:41:45 LOW saviour | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 05:52:20 fills it |
| 2026-09-01 06:57:25 | 2026-09-01 05:52:20 LOW saviour | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 05:52:20 fills it |
| 2026-09-01 06:57:30 | 2026-09-01 06:57:25 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 05:52:20 fills it |
| 2026-09-01 07:29:00 | 2026-09-01 04:41:45 LOW saviour | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 05:52:20 fills it |
| 2026-09-01 07:29:00 | 2026-09-01 05:52:20 LOW saviour | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 05:52:20 fills it |
| 2026-09-01 07:29:00 | 2026-09-01 06:57:25 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 05:52:20 fills it |
| 2026-09-01 07:29:05 | 2026-09-01 07:29:00 HIGH core | closed the LONG opened 2026-09-01 05:52:20, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 08:16:00 | 2026-09-01 04:41:45 LOW saviour | closed the SHORT opened 2026-09-01 07:29:05, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 08:16:00 | 2026-09-01 05:52:20 LOW saviour | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 08:16:00 fills it |
| 2026-09-01 08:16:00 | 2026-09-01 06:57:25 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 08:16:00 fills it |
| 2026-09-01 08:16:05 | 2026-09-01 08:16:00 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 08:16:00 fills it |
| 2026-09-01 10:07:30 | 2026-09-01 05:52:20 LOW saviour | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 08:16:00 fills it |
| 2026-09-01 10:07:30 | 2026-09-01 06:57:25 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 08:16:00 fills it |
| 2026-09-01 10:07:30 | 2026-09-01 08:16:00 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 08:16:00 fills it |
| 2026-09-01 10:07:35 | 2026-09-01 10:07:30 HIGH backstop | closed the LONG opened 2026-09-01 08:16:00, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 10:26:30 | 2026-09-01 05:52:20 LOW saviour | closed the SHORT opened 2026-09-01 10:07:35, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 10:26:30 | 2026-09-01 06:57:25 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 10:26:30 fills it |
| 2026-09-01 10:26:30 | 2026-09-01 08:16:00 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 10:26:30 fills it |
| 2026-09-01 10:26:35 | 2026-09-01 10:26:30 HIGH core | closed the LONG opened 2026-09-01 10:26:30, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 10:49:50 | 2026-09-01 06:57:25 LOW core | closed the SHORT opened 2026-09-01 10:26:35, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 10:49:50 | 2026-09-01 08:16:00 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 10:49:50 fills it |
| 2026-09-01 10:49:55 | 2026-09-01 10:49:50 HIGH core | closed the LONG opened 2026-09-01 10:49:50, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 10:49:55 | 2026-09-01 10:49:50 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 10:49:55 fills it |
| 2026-09-01 11:52:45 | 2026-09-01 08:16:00 LOW core | closed the SHORT opened 2026-09-01 10:49:55, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 11:52:45 | 2026-09-01 10:49:50 HIGH core | closed the LONG opened 2026-09-01 11:52:45, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 11:52:50 | 2026-09-01 11:52:45 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 11:52:45 fills it |
| 2026-09-01 11:52:50 | 2026-09-01 11:52:45 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 11:52:45 fills it |
| 2026-09-01 11:52:50 | 2026-09-01 11:52:45 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 11:52:45 fills it |
| 2026-09-01 13:14:30 | 2026-09-01 11:52:45 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 11:52:45 fills it |
| 2026-09-01 13:14:30 | 2026-09-01 11:52:45 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 11:52:45 fills it |
| 2026-09-01 13:14:30 | 2026-09-01 11:52:45 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 11:52:45 fills it |
| 2026-09-01 13:14:35 | 2026-09-01 13:14:30 LOW core | closed the SHORT opened 2026-09-01 11:52:45, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 13:50:25 | 2026-09-01 11:52:45 HIGH core | closed the LONG opened 2026-09-01 13:14:35, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 13:50:25 | 2026-09-01 11:52:45 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 13:50:25 fills it |
| 2026-09-01 13:50:25 | 2026-09-01 11:52:45 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 13:50:25 fills it |
| 2026-09-01 13:50:30 | 2026-09-01 13:50:25 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 13:50:25 fills it |
| 2026-09-01 14:17:35 | 2026-09-01 11:52:45 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 13:50:25 fills it |
| 2026-09-01 14:17:35 | 2026-09-01 11:52:45 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 13:50:25 fills it |
| 2026-09-01 14:17:35 | 2026-09-01 13:50:25 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 13:50:25 fills it |
| 2026-09-01 14:17:40 | 2026-09-01 14:17:35 HIGH backstop | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 13:50:25 fills it |
| 2026-09-01 15:15:10 | 2026-09-01 11:52:45 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 13:50:25 fills it |
| 2026-09-01 15:15:10 | 2026-09-01 11:52:45 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 13:50:25 fills it |
| 2026-09-01 15:15:10 | 2026-09-01 13:50:25 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 13:50:25 fills it |
| 2026-09-01 15:15:10 | 2026-09-01 14:17:35 HIGH backstop | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 13:50:25 fills it |
| 2026-09-01 15:15:15 | 2026-09-01 15:15:10 LOW core | closed the SHORT opened 2026-09-01 13:50:25, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 16:28:40 | 2026-09-01 11:52:45 HIGH core | closed the LONG opened 2026-09-01 15:15:15, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 16:28:40 | 2026-09-01 11:52:45 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 16:28:40 fills it |
| 2026-09-01 16:28:40 | 2026-09-01 13:50:25 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 16:28:40 fills it |
| 2026-09-01 16:28:40 | 2026-09-01 14:17:35 HIGH backstop | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 16:28:40 fills it |
| 2026-09-01 16:28:45 | 2026-09-01 16:28:40 LOW core | closed the SHORT opened 2026-09-01 16:28:40, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 17:33:30 | 2026-09-01 11:52:45 HIGH core | closed the LONG opened 2026-09-01 16:28:45, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 17:33:30 | 2026-09-01 13:50:25 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 17:33:30 fills it |
| 2026-09-01 17:33:30 | 2026-09-01 14:17:35 HIGH backstop | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 17:33:30 fills it |
| 2026-09-01 17:33:35 | 2026-09-01 17:33:30 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 17:33:30 fills it |
| 2026-09-01 18:30:15 | 2026-09-01 13:50:25 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 17:33:30 fills it |
| 2026-09-01 18:30:15 | 2026-09-01 14:17:35 HIGH backstop | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 17:33:30 fills it |
| 2026-09-01 18:30:15 | 2026-09-01 17:33:30 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 17:33:30 fills it |
| 2026-09-01 18:30:20 | 2026-09-01 18:30:15 LOW core | closed the SHORT opened 2026-09-01 17:33:30, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 18:30:20 | 2026-09-01 13:50:25 HIGH core | closed the LONG opened 2026-09-01 18:30:20, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 18:30:20 | 2026-09-01 14:17:35 HIGH backstop | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 18:30:20 fills it |
| 2026-09-01 18:30:20 | 2026-09-01 17:33:30 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 18:30:20 fills it |
| 2026-09-01 18:30:25 | 2026-09-01 18:30:20 LOW core | closed the SHORT opened 2026-09-01 18:30:20, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 18:55:10 | 2026-09-01 14:17:35 HIGH backstop | closed the LONG opened 2026-09-01 18:30:25, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 18:55:10 | 2026-09-01 17:33:30 HIGH core | HELD the SHORT | 1 SHORT open of max 1 - the SHORT opened 2026-09-01 18:55:10 fills it |
| 2026-09-01 18:55:15 | 2026-09-01 18:55:10 LOW core | closed the SHORT opened 2026-09-01 18:55:10, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 18:55:15 | 2026-09-01 18:55:10 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 18:55:15 fills it |
| 2026-09-01 18:55:15 | 2026-09-01 18:55:10 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 18:55:15 fills it |
| 2026-09-01 19:43:10 | 2026-09-01 17:33:30 HIGH core | closed the LONG opened 2026-09-01 18:55:15, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 19:43:10 | 2026-09-01 18:55:10 LOW core | closed the SHORT opened 2026-09-01 19:43:10, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 19:43:10 | 2026-09-01 18:55:10 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 19:43:10 fills it |
| 2026-09-01 19:43:15 | 2026-09-01 19:43:10 HIGH backstop | closed the LONG opened 2026-09-01 19:43:10, then opened a SHORT | 0 SHORT open of max 1 |
| 2026-09-01 20:31:10 | 2026-09-01 18:55:10 LOW core | closed the SHORT opened 2026-09-01 19:43:15, then opened a LONG | 0 LONG open of max 1 |
| 2026-09-01 20:31:15 | 2026-09-01 20:31:10 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 20:31:10 fills it |
| 2026-09-01 20:31:15 | 2026-09-01 20:31:10 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 20:31:10 fills it |
| 2026-09-01 20:31:15 | 2026-09-01 20:31:10 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 20:31:10 fills it |
| 2026-09-01 20:54:25 | 2026-09-01 20:31:10 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 20:31:10 fills it |
| 2026-09-01 20:54:25 | 2026-09-01 20:31:10 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 20:31:10 fills it |
| 2026-09-01 20:54:25 | 2026-09-01 20:31:10 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 20:31:10 fills it |
| 2026-09-01 20:54:30 | 2026-09-01 20:54:25 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 20:31:10 fills it |
| 2026-09-01 21:19:45 | 2026-09-01 20:31:10 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 20:31:10 fills it |
| 2026-09-01 21:19:45 | 2026-09-01 20:31:10 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 20:31:10 fills it |
| 2026-09-01 21:19:45 | 2026-09-01 20:31:10 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 20:31:10 fills it |
| 2026-09-01 21:19:45 | 2026-09-01 20:54:25 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 20:31:10 fills it |
| 2026-09-01 21:19:50 | 2026-09-01 21:19:45 LOW core | HELD the LONG | 1 LONG open of max 1 - the LONG opened 2026-09-01 20:31:10 fills it |

# WHY EACH HELD SIGNAL WAITED. One row per refusal, recorded by the router at the bar
#   it refused. `blocked by` is the OPEN BAR of each trade that filled max_pyramid.

| # | the signal | refused at | wanted | blocked by | blocker | opened |
|---|---|---|---|---|---|---|
| 4 | 2026-09-01 01:37:10 | 2026-09-01 01:37:15 | LONG | 2026-09-01 01:37:15 | SIBLING |  |
|  |  | 2026-09-01 02:25:20 | LONG | 2026-09-01 01:37:15 | SIBLING |  |
|  |  | 2026-09-01 03:34:25 | LONG | 2026-09-01 01:37:15 | SIBLING | 2026-09-01 04:28:55 |
| 6 | 2026-09-01 01:37:10 | 2026-09-01 01:37:15 | LONG | 2026-09-01 01:37:15 | SIBLING |  |
|  |  | 2026-09-01 02:25:20 | LONG | 2026-09-01 01:37:15 | SIBLING |  |
|  |  | 2026-09-01 03:34:25 | LONG | 2026-09-01 01:37:15 | SIBLING |  |
|  |  | 2026-09-01 04:28:55 | LONG | 2026-09-01 04:28:55 | SIBLING | 2026-09-01 04:41:45 |
| 8 | 2026-09-01 02:25:20 | 2026-09-01 02:25:25 | LONG | 2026-09-01 01:37:15 | EARLIER LEG |  |
|  |  | 2026-09-01 03:34:25 | LONG | 2026-09-01 01:37:15 | EARLIER LEG |  |
|  |  | 2026-09-01 04:28:55 | LONG | 2026-09-01 04:28:55 | SIBLING |  |
|  |  | 2026-09-01 04:41:45 | LONG | 2026-09-01 04:41:45 | SIBLING |  |
|  |  | 2026-09-01 05:46:30 | LONG | 2026-09-01 04:41:45 | SIBLING | 2026-09-01 05:52:20 |
| 10 | 2026-09-01 04:41:45 | 2026-09-01 04:41:50 | LONG | 2026-09-01 04:41:45 | SIBLING |  |
|  |  | 2026-09-01 05:46:30 | LONG | 2026-09-01 04:41:45 | SIBLING |  |
|  |  | 2026-09-01 05:52:20 | LONG | 2026-09-01 05:52:20 | SIBLING |  |
|  |  | 2026-09-01 06:57:25 | LONG | 2026-09-01 05:52:20 | SIBLING |  |
|  |  | 2026-09-01 07:29:00 | LONG | 2026-09-01 05:52:20 | SIBLING | 2026-09-01 08:16:00 |
| 12 | 2026-09-01 05:52:20 | 2026-09-01 05:52:25 | LONG | 2026-09-01 05:52:20 | SIBLING |  |
|  |  | 2026-09-01 06:57:25 | LONG | 2026-09-01 05:52:20 | SIBLING |  |
|  |  | 2026-09-01 07:29:00 | LONG | 2026-09-01 05:52:20 | SIBLING |  |
|  |  | 2026-09-01 08:16:00 | LONG | 2026-09-01 08:16:00 | SIBLING |  |
|  |  | 2026-09-01 10:07:30 | LONG | 2026-09-01 08:16:00 | SIBLING | 2026-09-01 10:26:30 |
| 14 | 2026-09-01 06:57:25 | 2026-09-01 06:57:30 | LONG | 2026-09-01 05:52:20 | EARLIER LEG |  |
|  |  | 2026-09-01 07:29:00 | LONG | 2026-09-01 05:52:20 | EARLIER LEG |  |
|  |  | 2026-09-01 08:16:00 | LONG | 2026-09-01 08:16:00 | SIBLING |  |
|  |  | 2026-09-01 10:07:30 | LONG | 2026-09-01 08:16:00 | SIBLING |  |
|  |  | 2026-09-01 10:26:30 | LONG | 2026-09-01 10:26:30 | SIBLING | 2026-09-01 10:49:50 |
| 16 | 2026-09-01 08:16:00 | 2026-09-01 08:16:05 | LONG | 2026-09-01 08:16:00 | SIBLING |  |
|  |  | 2026-09-01 10:07:30 | LONG | 2026-09-01 08:16:00 | SIBLING |  |
|  |  | 2026-09-01 10:26:30 | LONG | 2026-09-01 10:26:30 | SIBLING |  |
|  |  | 2026-09-01 10:49:50 | LONG | 2026-09-01 10:49:50 | SIBLING | 2026-09-01 11:52:45 |
| 17 | 2026-09-01 10:49:50 | 2026-09-01 10:49:55 | SHORT | 2026-09-01 10:49:55 | SIBLING | 2026-09-01 11:52:45 |
| 19 | 2026-09-01 11:52:45 | 2026-09-01 11:52:50 | SHORT | 2026-09-01 11:52:45 | SIBLING |  |
|  |  | 2026-09-01 13:14:30 | SHORT | 2026-09-01 11:52:45 | SIBLING | 2026-09-01 13:50:25 |
| 21 | 2026-09-01 11:52:45 | 2026-09-01 11:52:50 | SHORT | 2026-09-01 11:52:45 | SIBLING |  |
|  |  | 2026-09-01 13:14:30 | SHORT | 2026-09-01 11:52:45 | SIBLING |  |
|  |  | 2026-09-01 13:50:25 | SHORT | 2026-09-01 13:50:25 | SIBLING |  |
|  |  | 2026-09-01 14:17:35 | SHORT | 2026-09-01 13:50:25 | SIBLING |  |
|  |  | 2026-09-01 15:15:10 | SHORT | 2026-09-01 13:50:25 | SIBLING | 2026-09-01 16:28:40 |
| 23 | 2026-09-01 11:52:45 | 2026-09-01 11:52:50 | SHORT | 2026-09-01 11:52:45 | SIBLING |  |
|  |  | 2026-09-01 13:14:30 | SHORT | 2026-09-01 11:52:45 | SIBLING |  |
|  |  | 2026-09-01 13:50:25 | SHORT | 2026-09-01 13:50:25 | SIBLING |  |
|  |  | 2026-09-01 14:17:35 | SHORT | 2026-09-01 13:50:25 | SIBLING |  |
|  |  | 2026-09-01 15:15:10 | SHORT | 2026-09-01 13:50:25 | SIBLING |  |
|  |  | 2026-09-01 16:28:40 | SHORT | 2026-09-01 16:28:40 | SIBLING | 2026-09-01 17:33:30 |
| 25 | 2026-09-01 13:50:25 | 2026-09-01 13:50:30 | SHORT | 2026-09-01 13:50:25 | SIBLING |  |
|  |  | 2026-09-01 14:17:35 | SHORT | 2026-09-01 13:50:25 | SIBLING |  |
|  |  | 2026-09-01 15:15:10 | SHORT | 2026-09-01 13:50:25 | SIBLING |  |
|  |  | 2026-09-01 16:28:40 | SHORT | 2026-09-01 16:28:40 | SIBLING |  |
|  |  | 2026-09-01 17:33:30 | SHORT | 2026-09-01 17:33:30 | SIBLING |  |
|  |  | 2026-09-01 18:30:15 | SHORT | 2026-09-01 17:33:30 | SIBLING | 2026-09-01 18:30:20 |
| 27 | 2026-09-01 14:17:35 | 2026-09-01 14:17:40 | SHORT | 2026-09-01 13:50:25 | EARLIER LEG |  |
|  |  | 2026-09-01 15:15:10 | SHORT | 2026-09-01 13:50:25 | EARLIER LEG |  |
|  |  | 2026-09-01 16:28:40 | SHORT | 2026-09-01 16:28:40 | SIBLING |  |
|  |  | 2026-09-01 17:33:30 | SHORT | 2026-09-01 17:33:30 | SIBLING |  |
|  |  | 2026-09-01 18:30:15 | SHORT | 2026-09-01 17:33:30 | SIBLING |  |
|  |  | 2026-09-01 18:30:20 | SHORT | 2026-09-01 18:30:20 | SIBLING | 2026-09-01 18:55:10 |
| 29 | 2026-09-01 18:55:10 | 2026-09-01 18:55:15 | LONG | 2026-09-01 18:55:15 | SIBLING | 2026-09-01 19:43:10 |
| 30 | 2026-09-01 17:33:30 | 2026-09-01 17:33:35 | SHORT | 2026-09-01 17:33:30 | SIBLING |  |
|  |  | 2026-09-01 18:30:15 | SHORT | 2026-09-01 17:33:30 | SIBLING |  |
|  |  | 2026-09-01 18:30:20 | SHORT | 2026-09-01 18:30:20 | SIBLING |  |
|  |  | 2026-09-01 18:55:10 | SHORT | 2026-09-01 18:55:10 | SIBLING | 2026-09-01 19:43:10 |
| 32 | 2026-09-01 18:55:10 | 2026-09-01 18:55:15 | LONG | 2026-09-01 18:55:15 | SIBLING |  |
|  |  | 2026-09-01 19:43:10 | LONG | 2026-09-01 19:43:10 | SIBLING | 2026-09-01 20:31:10 |

| the held signal | side | by | the bar it was refused | detail |
|---|---|---|---|---|
| 2026-09-01 20:31:10 | LOW | core | 2026-09-01 21:19:45 | cws1b 2026-09-01 18:45:55, step2 arm 2026-09-01 19:53:00, ws3, exh 2026-09-01 20:31:10 |
| 2026-09-01 20:31:10 | LOW | core | 2026-09-01 21:19:45 | cws1b 2026-09-01 19:57:00, step2 arm 2026-09-01 19:57:00, ws3, exh 2026-09-01 20:31:10 |
| 2026-09-01 20:31:10 | LOW | core | 2026-09-01 21:19:45 | cws1b 2026-09-01 20:02:00, step2 arm 2026-09-01 20:02:00, ws3, exh 2026-09-01 20:31:10 |
| 2026-09-01 20:54:25 | LOW | core | 2026-09-01 21:19:45 | cws1b 2026-09-01 20:51:00, step2 arm 2026-09-01 20:51:00, ws2, exh 2026-09-01 20:54:25 |
| 2026-09-01 21:19:45 | LOW | core | 2026-09-01 21:19:50 | cws1b 2026-09-01 21:16:00, step2 arm 2026-09-01 21:16:00, ws2, exh 2026-09-01 21:19:45 |
