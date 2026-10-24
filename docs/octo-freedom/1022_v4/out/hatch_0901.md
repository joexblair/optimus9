# THE MACHINE, mode 'hatch'. 2026-09-01 00:00:00 .. 2026-09-03 23:59:55
# order 'saviour,core,backstop', backstop fallback 'drop'. ONE position at a time.
# LIN_PASS 'ib', lookback floor ON at ws6, 39 backstop fires. RULED_OK True.

| the invisible trade | its target-side | the real trade it opens | detail |
|---|---|---|---|
| an invisible LONG | high | 2026-09-01 00:33:15 | cws1b 2026-09-01 00:04:00, arm 2026-09-01 00:26:00, ws2, exh 2026-09-01 00:33:10 |
| an invisible SHORT | low | 2026-09-01 02:25:25 | cws1b 2026-09-01 01:07:00, arm 2026-09-01 02:12:00, ws3, exh 2026-09-01 02:25:20 |

| the read | value |
|---|---|
| baton hand-offs the chain made | 104 |
| of those, the receiver arrived SPENT - the hatch fires | 22 |
| of those, ws5r AND ws6r both oob AT THE ANCHOR - his key setup | 8 |
| the lookback cannot reach behind the anchor | `first_rev_at_or_after(.., A, ..)` seeds every ST from A, so "already spent" ALWAYS means reversed DURING the walk |
| how stale the receiver was at the pass, median | 290 s |
| how stale the receiver was at the pass, max | 1005 s |

| what the hatch branch ITSELF did | hatch fires | of those on his setup |
|---|---|---|
| EXHAUST, second-new-rider not ex-fence | 8 | 1 |
| EXHAUST, second-new-rider spent too | 14 | 7 |
| the pass bar can never show ws5r oob | LIN_PASS is 'ib': the sender is IN bounds there |
| hand-offs blocked by the ws6 lookback floor | 76 |

| the anchor | mech | side | ws5r at the anchor | ws6r at the anchor | his setup | the oob run | hand-off | the pass bar | receiver r there | its reversal | stale by | the second walk resolves | what the hatch branch did | EXHAUST |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-01 01:16:20 | backstop | LOW oob | 3.47 | 6.93 | YES | ws4-ws6 | ws5 -> ws6 | 2026-09-01 01:35:30 | 11.64 | 2026-09-01 01:34:35 | 55 s | 2026-09-01 01:37:10 | EXHAUST, second-new-rider spent too | 2026-09-01 01:37:10 |
| 2026-09-01 06:26:20 | backstop | LOW oob | 11.42 | 18.98 | no | ws4-ws5 | ws6 -> ws7 | 2026-09-01 07:07:10 | 17.07 | 2026-09-01 06:27:45 | 2365 s | 2026-09-01 07:08:30 | EXHAUST, second-new-rider spent too | 2026-09-01 07:08:30 |
| 2026-09-01 08:08:00 | core | LOW oob | 22.96 | 28.85 | no | none | ws5 -> ws6 | 2026-09-01 08:35:55 | 11.01 | 2026-09-01 08:16:20 | 1175 s | 2026-09-01 08:37:10 | EXHAUST, second-new-rider spent too | 2026-09-01 08:37:10 |
| 2026-09-01 09:49:00 | backstop | HIGH oob | 86.17 | 90.40 | YES | ws5-ws9 | ws6 -> ws7 | 2026-09-01 10:04:50 | 85.20 | 2026-09-01 10:00:10 | 280 s | 2026-09-01 10:07:30 | EXHAUST, second-new-rider spent too | 2026-09-01 10:07:30 |
| 2026-09-01 13:00:00 | core | LOW oob | 10.74 | 0.00 | YES | ws5-ws10 | ws5 -> ws6 | 2026-09-01 13:08:40 | 12.14 | 2026-09-01 13:00:40 | 480 s | 2026-09-01 13:13:10 | EXHAUST, second-new-rider not ex-fence | 2026-09-01 13:13:10 |
| 2026-09-01 13:36:40 | backstop | HIGH oob | 97.44 | 88.03 | YES | ws4-ws6 | ws5 -> ws6 | 2026-09-01 13:54:05 | 92.41 | 2026-09-01 13:39:25 | 880 s | 2026-09-01 14:19:10 | EXHAUST, second-new-rider spent too | 2026-09-01 14:19:10 |
| 2026-09-01 15:02:00 | core | LOW oob | 35.97 | 40.92 | no | none | ws5 -> ws6 | 2026-09-01 15:25:55 | 10.16 | 2026-09-01 15:22:50 | 185 s | 2026-09-01 15:31:10 | EXHAUST, second-new-rider spent too | 2026-09-01 15:31:10 |
| 2026-09-01 17:59:05 | core | LOW oob | 33.49 | 53.96 | no | none | ws5 -> ws6 | 2026-09-01 18:42:10 | 0.00 | 2026-09-01 18:08:00 | 2050 s | 2026-09-01 18:50:30 | EXHAUST, second-new-rider not ex-fence | 2026-09-01 18:50:30 |
| 2026-09-01 19:15:00 | backstop | HIGH oob | 93.93 | 81.50 | no | ws4-ws5 | ws5 -> ws6 | 2026-09-01 19:39:10 | 89.58 | 2026-09-01 19:25:00 | 850 s | 2026-09-01 19:43:10 | EXHAUST, second-new-rider not ex-fence | 2026-09-01 19:43:10 |
| 2026-09-01 19:57:05 | core | LOW oob | 14.92 | 39.70 | no | ws2-ws5 | ws5 -> ws6 | 2026-09-01 20:15:55 | 4.49 | 2026-09-01 20:15:20 | 35 s | 2026-09-01 20:19:30 | EXHAUST, second-new-rider spent too | 2026-09-01 20:19:30 |
| 2026-09-02 02:37:45 | backstop | HIGH oob | 95.71 | 93.53 | YES | ws4-ws6 | ws5 -> ws6 | 2026-09-02 02:45:55 | 87.23 | 2026-09-02 02:41:05 | 290 s | 2026-09-02 03:35:25 | EXHAUST, second-new-rider spent too | 2026-09-02 03:35:25 |
| 2026-09-02 03:18:00 | core | HIGH oob | 95.91 | 94.44 | YES | ws3-ws10 | ws5 -> ws6 | 2026-09-02 03:33:10 | 84.93 | 2026-09-02 03:30:40 | 150 s | 2026-09-02 03:35:25 | EXHAUST, second-new-rider spent too | 2026-09-02 03:35:25 |
| 2026-09-02 03:59:10 | backstop | LOW oob | 14.95 | 25.35 | no | ws5-ws5 | ws6 -> ws7 | 2026-09-02 04:25:15 | 14.66 | 2026-09-02 04:20:00 | 315 s | 2026-09-02 04:32:50 | EXHAUST, second-new-rider not ex-fence | 2026-09-02 04:32:50 |
| 2026-09-02 12:48:05 | core | LOW oob | 33.33 | 33.33 | no | none | ws5 -> ws6 | 2026-09-02 13:05:55 | 10.04 | 2026-09-02 13:02:55 | 180 s | 2026-09-02 13:07:10 | EXHAUST, second-new-rider spent too | 2026-09-02 13:07:10 |
| 2026-09-02 21:27:10 | backstop | LOW oob | 13.25 | 29.51 | no | ws5-ws5 | ws5 -> ws6 | 2026-09-02 21:36:25 | 17.51 | 2026-09-02 21:27:45 | 520 s | 2026-09-02 21:37:35 | EXHAUST, second-new-rider not ex-fence | 2026-09-02 21:37:35 |
| 2026-09-03 03:23:00 | core | LOW oob | 27.32 | 31.98 | no | none | ws5 -> ws6 | 2026-09-03 03:33:10 | 7.38 | 2026-09-03 03:26:05 | 425 s | 2026-09-03 03:50:25 | EXHAUST, second-new-rider spent too | 2026-09-03 03:50:25 |
| 2026-09-03 03:42:55 | backstop | LOW oob | 11.02 | 7.63 | YES | ws4-ws8 | ws5 -> ws6 | 2026-09-03 03:50:45 | 17.30 | 2026-09-03 03:48:20 | 145 s | 2026-09-03 03:51:55 | EXHAUST, second-new-rider spent too | 2026-09-03 03:51:55 |
| 2026-09-03 05:51:05 | core | HIGH oob | 67.31 | 47.04 | no | none | ws5 -> ws6 | 2026-09-03 06:10:50 | 80.05 | 2026-09-03 06:10:25 | 25 s | 2026-09-03 06:12:00 | EXHAUST, second-new-rider not ex-fence | 2026-09-03 06:12:00 |
| 2026-09-03 10:58:00 | core | HIGH oob | 81.86 | 50.01 | no | none | ws5 -> ws6 | 2026-09-03 11:14:55 | 83.19 | 2026-09-03 11:04:05 | 650 s | 2026-09-03 11:49:25 | EXHAUST, second-new-rider not ex-fence | 2026-09-03 11:49:25 |
| 2026-09-03 11:03:30 | backstop | HIGH oob | 89.46 | 61.08 | no | ws3-ws5 | ws5 -> ws6 | 2026-09-03 11:14:55 | 83.19 | 2026-09-03 11:04:05 | 650 s | 2026-09-03 11:49:25 | EXHAUST, second-new-rider not ex-fence | 2026-09-03 11:49:25 |
| 2026-09-03 19:54:05 | core | LOW oob | 24.42 | 15.54 | no | none | ws5 -> ws6 | 2026-09-03 20:25:55 | 17.36 | 2026-09-03 20:09:10 | 1005 s | 2026-09-03 20:27:05 | EXHAUST, second-new-rider spent too | 2026-09-03 20:27:05 |
| 2026-09-03 20:08:35 | backstop | LOW oob | 3.16 | 3.83 | YES | ws4-ws8 | ws5 -> ws6 | 2026-09-03 20:25:55 | 17.36 | 2026-09-03 20:09:10 | 1005 s | 2026-09-03 20:27:05 | EXHAUST, second-new-rider spent too | 2026-09-03 20:27:05 |

