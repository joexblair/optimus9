# 1119 - small pseudo trades on 8792 and his 4 mechs, 2026-09-24

GOAL (his): *"what I need is a way to predict if a TOexf line will convert to AW, based on the 4 mechs and their states"*.

His steps: *"to gather this data, you'll start with finding the psuedo-trades that print mostly mid-board in the highband.  this is a sign of a small trade, the game in which our Fu is not yet strong"* /
*"next, find the last AW flips from both highband and lowband (if they exist), and walk back along the trade to hunt for a loose interpretation of my 4 mech's scenarios"* /
*"for each small trade that you analyse, report (in a table) the counts of the 4 mechs. add a short-form commentary column if you observe anything that feels important"* /
*"x/e cluster can be minimum 4"* / *"for the reporting, the table will need data on the last TOexf flip, for both lowband and highband"* - his pick: the TO(exf) into AW flip.

READ ONLY: the 8792 page (30 s rows, pooled four-read pivots, flip 0, pivots as found), decoded off /meta and checked with the workmate (sidegig chat #66, #68). Scratch code: scratchpad small_trades/small0924.py, table2.py.

## The readings - MINE unless marked his

| what | the reading |
|---|---|
| small trade | over 50% of its ws8-15 TO(inf) cells read -1, 0 or +1 (his "mostly") |
| 1) x/e cluster | ws1-7 lines with an x or e cross in the 3 rows ending on the row; present at 4 or more - HIS 1119 minimum 4 |
| 2) highband mid-board | ws8-15 cells reading TO(inf)-1, 0 or +1 on the row; present at 5 or more of 8 |
| 3) incumbent colour | the target-side colour, red (Mage under 50.00) on LOW, green on HIGH; ws1-15 cells in it on the row against the trade's high so far; present when under that high |
| 4) AW flips near cluster | ws1-15 lines flipping TO into AW on the cluster's 3 rows or the 2 rows before them; present at 1 or more |
| last TO(exf) into AW | the last row in the band where a line reads TO(exf) on the row before and AW(inf) or AW(exf) on the row |
| walk-back | from the row before that flip, row by row back to the trade's first row; the walk-back row is the first one with all four present |

## The trades on 2026-09-24 and the small-trade read

| trade opens | trade closes | target-side | rows | ws8-15 TO(inf) cells | of them -1, 0 or +1 | share | small |
|---|---|---|---|---|---|---|---|
| 2026-09-23 23:47:25 | 2026-09-24 00:35:25 | HIGH | 96 | 765 | 692 | 90.5% | yes |
| 2026-09-24 00:35:25 | 2026-09-24 00:57:25 | LOW | 44 | 305 | 305 | 100.0% | yes |
| 2026-09-24 00:57:25 | 2026-09-24 01:39:25 | HIGH | 84 | 672 | 532 | 79.2% | yes |
| 2026-09-24 01:39:25 | 2026-09-24 02:13:25 | LOW | 68 | 422 | 402 | 95.3% | yes |
| 2026-09-24 02:13:25 | 2026-09-24 02:58:25 | HIGH | 90 | 626 | 556 | 88.8% | yes |
| 2026-09-24 02:58:25 | 2026-09-24 04:24:25 | LOW | 172 | 1101 | 697 | 63.3% | yes |
| 2026-09-24 04:24:25 | 2026-09-24 05:17:25 | HIGH | 106 | 784 | 350 | 44.6% | no |
| 2026-09-24 05:17:25 | 2026-09-24 06:08:15 | LOW | 102 | 802 | 591 | 73.7% | yes |
| 2026-09-24 06:08:15 | 2026-09-24 07:02:25 | HIGH | 108 | 857 | 825 | 96.3% | yes |
| 2026-09-24 07:02:25 | 2026-09-24 07:08:25 | LOW | 12 | 96 | 96 | 100.0% | yes |
| 2026-09-24 07:08:25 | 2026-09-24 08:09:50 | HIGH | 123 | 558 | 548 | 98.2% | yes |
| 2026-09-24 08:09:50 | 2026-09-24 10:16:25 | LOW | 253 | 718 | 613 | 85.4% | yes |
| 2026-09-24 10:16:25 | 2026-09-24 11:18:35 | HIGH | 125 | 675 | 491 | 72.7% | yes |
| 2026-09-24 11:18:35 | 2026-09-24 12:03:35 | LOW | 90 | 720 | 144 | 20.0% | no |
| 2026-09-24 12:03:35 | 2026-09-24 12:27:25 | HIGH | 47 | 297 | 181 | 60.9% | yes |
| 2026-09-24 12:27:25 | 2026-09-24 12:37:20 | LOW | 20 | 138 | 92 | 66.7% | yes |
| 2026-09-24 12:37:20 | 2026-09-24 13:42:25 | HIGH | 130 | 845 | 773 | 91.5% | yes |
| 2026-09-24 13:42:25 | 2026-09-24 13:56:25 | LOW | 28 | 224 | 76 | 33.9% | no |
| 2026-09-24 13:56:25 | 2026-09-24 14:37:25 | HIGH | 82 | 292 | 280 | 95.9% | yes |
| 2026-09-24 14:37:25 | 2026-09-24 15:05:10 | LOW | 56 | 448 | 270 | 60.3% | yes |
| 2026-09-24 15:05:10 | 2026-09-24 15:52:00 | HIGH | 93 | 744 | 639 | 85.9% | yes |
| 2026-09-24 15:52:00 | 2026-09-24 16:16:25 | LOW | 49 | 303 | 247 | 81.5% | yes |
| 2026-09-24 16:16:25 | 2026-09-24 16:44:25 | HIGH | 56 | 382 | 288 | 75.4% | yes |
| 2026-09-24 16:44:25 | 2026-09-24 18:08:45 | LOW | 169 | 996 | 925 | 92.9% | yes |
| 2026-09-24 18:08:45 | 2026-09-24 18:40:45 | HIGH | 64 | 510 | 144 | 28.2% | no |
| 2026-09-24 18:40:45 | 2026-09-24 18:50:25 | LOW | 19 | 76 | 74 | 97.4% | yes |
| 2026-09-24 18:50:25 | 2026-09-24 18:59:50 | HIGH | 19 | 144 | 98 | 68.1% | yes |
| 2026-09-24 18:59:50 | 2026-09-24 19:07:00 | LOW | 14 | 110 | 84 | 76.4% | yes |
| 2026-09-24 19:07:00 | 2026-09-24 19:37:25 | HIGH | 61 | 453 | 423 | 93.4% | yes |
| 2026-09-24 19:37:25 | 2026-09-24 20:27:25 | LOW | 100 | 782 | 656 | 83.9% | yes |
| 2026-09-24 20:27:25 | 2026-09-24 21:03:45 | HIGH | 73 | 584 | 526 | 90.1% | yes |
| 2026-09-24 21:03:45 | 2026-09-24 21:17:25 | LOW | 27 | 165 | 150 | 90.9% | yes |
| 2026-09-24 21:17:25 | 2026-09-24 21:37:25 | HIGH | 40 | 319 | 231 | 72.4% | yes |
| 2026-09-24 21:37:25 | 2026-09-24 22:49:25 | LOW | 144 | 487 | 452 | 92.8% | yes |
| 2026-09-24 22:49:25 | 2026-09-25 01:20:25 | HIGH | 302 | 1124 | 603 | 53.6% | yes |

## The small trades, one row per trade and band

| trade opens | target-side | highband mid-board | band | last AW flip, lines (read the row before) | last TO(exf) into AW, lines | min before the trade closes | walk-back row | lead, min | 1) x/e cluster | 2) highband mid-board | 3) incumbent colour | 4) AW flips near cluster | TO(exf) lines on the walk-back row -> AW at | commentary |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-23 23:47:25 | HIGH | 90% | highband | 2026-09-24 00:33:30 ws8 (TO(inf)+1) | - | - | - | - | - | - | - | - | - |  |
| 2026-09-23 23:47:25 | HIGH | 90% | lowband | 2026-09-24 00:33:30 ws1 (TO(exf)) | 2026-09-24 00:33:30 ws1 | 1.9 | 2026-09-24 00:24:30 | 9.0 | 5 (ws1, ws2, ws4, ws5, ws6) | 8 of 8 | 12 of 15, high 15 | 1 (ws1) | - | no line reads TO(exf) on the walk-back row |
| 2026-09-24 00:35:25 | LOW | 100% | highband | 2026-09-24 00:46:00 ws10 (TO(inf)-1), ws14 (TO(inf)-1) | - | - | - | - | - | - | - | - | - |  |
| 2026-09-24 00:35:25 | LOW | 100% | lowband | 2026-09-24 00:56:30 ws4 (TO(exf)), ws7 (TO(exf)) | 2026-09-24 00:56:30 ws4, ws7 | 0.9 | not found | - | - | - | - | - | - | not found: 3) red at its high 15 on all 43 rows walked |
| 2026-09-24 00:57:25 | HIGH | 79% | highband | - | - | - | - | - | - | - | - | - | - |  |
| 2026-09-24 00:57:25 | HIGH | 79% | lowband | 2026-09-24 01:38:00 ws5 (TO(exf)) | 2026-09-24 01:38:00 ws5 | 1.4 | 2026-09-24 01:37:30 | 0.5 | 6 (ws1, ws2, ws3, ws4, ws5, ws6) | 7 of 8 | 11 of 15, high 15 | 2 (ws1, ws2) | ws5 2026-09-24 01:38:00 |  |
| 2026-09-24 01:39:25 | LOW | 95% | highband | 2026-09-24 02:10:00 ws8 (TO(inf)-1) | 2026-09-24 01:52:30 ws15 | 20.9 | 2026-09-24 01:45:30 | 7.0 | 6 (ws2, ws3, ws4, ws5, ws6, ws7) | 6 of 8 | 9 of 15, high 15 | 1 (ws1) | ws11 2026-09-24 01:48:00, ws15 2026-09-24 01:52:30 |  |
| 2026-09-24 01:39:25 | LOW | 95% | lowband | 2026-09-24 02:12:30 ws6 (TO(exf)) | 2026-09-24 02:12:30 ws6 | 0.9 | 2026-09-24 01:45:30 | 27.0 | 6 (ws2, ws3, ws4, ws5, ws6, ws7) | 6 of 8 | 9 of 15, high 15 | 1 (ws1) | ws11 2026-09-24 01:48:00, ws15 2026-09-24 01:52:30 | 3) red 15 of 15 on every row from 2026-09-24 01:46:00 to the last row 2026-09-24 02:12:30 |
| 2026-09-24 02:13:25 | HIGH | 89% | highband | 2026-09-24 02:47:30 ws12 (TO(inf)0) | - | - | - | - | - | - | - | - | - |  |
| 2026-09-24 02:13:25 | HIGH | 89% | lowband | 2026-09-24 02:57:00 ws5 (TO(exf)) | 2026-09-24 02:57:00 ws5 | 1.4 | 2026-09-24 02:26:00 | 31.0 | 4 (ws1, ws4, ws5, ws6) | 7 of 8 | 13 of 15, high 15 | 1 (ws2) | - |  |
| 2026-09-24 02:58:25 | LOW | 63% | highband | 2026-09-24 04:21:30 ws9 (TO(exf)) | 2026-09-24 04:21:30 ws9 | 2.9 | 2026-09-24 04:06:30 | 15.0 | 6 (ws2, ws3, ws4, ws5, ws6, ws7) | 5 of 8 | 11 of 15, high 15 | 1 (ws7) | ws3 2026-09-24 04:07:00, ws6 2026-09-24 04:07:00, ws9 2026-09-24 04:07:00, ws10 no | ws10 TO(exf) does not convert; ws3, ws6, ws9 convert on the next row |
| 2026-09-24 02:58:25 | LOW | 63% | lowband | 2026-09-24 04:07:00 ws3 (TO(exf)), ws6 (TO(exf)) | 2026-09-24 04:07:00 ws3, ws6 | 17.4 | 2026-09-24 04:06:30 | 0.5 | 6 (ws2, ws3, ws4, ws5, ws6, ws7) | 5 of 8 | 11 of 15, high 15 | 1 (ws7) | ws3 2026-09-24 04:07:00, ws6 2026-09-24 04:07:00, ws9 2026-09-24 04:07:00, ws10 no |  |
| 2026-09-24 05:17:25 | LOW | 74% | highband | 2026-09-24 06:01:00 ws8 (TO(inf)0) | - | - | - | - | - | - | - | - | - |  |
| 2026-09-24 05:17:25 | LOW | 74% | lowband | 2026-09-24 06:07:00 ws4 (TO(inf)-1) | 2026-09-24 06:04:00 ws5, ws6, ws7 | 4.2 | 2026-09-24 06:03:30 | 0.5 | 7 (ws1, ws2, ws3, ws4, ws5, ws6, ws7) | 7 of 8 | 1 of 15, high 7 | 2 (ws2, ws3) | ws4 2026-09-24 06:07:00, ws5 2026-09-24 06:04:00, ws6 2026-09-24 06:04:00, ws7 2026-09-24 06:04:00 | 3) red never above 7 of 15 in the trade |
| 2026-09-24 06:08:15 | HIGH | 96% | highband | 2026-09-24 07:01:00 ws9 (TO(inf)0) | - | - | - | - | - | - | - | - | - |  |
| 2026-09-24 06:08:15 | HIGH | 96% | lowband | 2026-09-24 07:01:30 ws7 (TO(exf)) | 2026-09-24 07:01:30 ws7 | 0.9 | 2026-09-24 07:01:00 | 0.5 | 7 (ws1, ws2, ws3, ws4, ws5, ws6, ws7) | 6 of 8 | 14 of 15, high 15 | 3 (ws6, ws8, ws9) | ws7 2026-09-24 07:01:30 |  |
| 2026-09-24 07:02:25 | LOW | 100% | highband | - | - | - | - | - | - | - | - | - | - |  |
| 2026-09-24 07:02:25 | LOW | 100% | lowband | 2026-09-24 07:06:30 ws1 (TO(exf)) | 2026-09-24 07:06:30 ws1 | 1.9 | not found | - | - | - | - | - | - | not found: 4) 0 of 9 rows walked |
| 2026-09-24 07:08:25 | HIGH | 98% | highband | 2026-09-24 08:08:30 ws15 (TO(inf)+1) | 2026-09-24 08:06:30 ws13 | 3.3 | 2026-09-24 07:13:30 | 53.0 | 6 (ws1, ws2, ws3, ws4, ws6, ws7) | 7 of 8 | 14 of 15, high 15 | 1 (ws1) | - |  |
| 2026-09-24 07:08:25 | HIGH | 98% | lowband | 2026-09-24 08:04:00 ws1 (TO(inf)0) | 2026-09-24 07:55:30 ws1 | 14.3 | 2026-09-24 07:13:30 | 42.0 | 6 (ws1, ws2, ws3, ws4, ws6, ws7) | 7 of 8 | 14 of 15, high 15 | 1 (ws1) | - |  |
| 2026-09-24 08:09:50 | LOW | 85% | highband | 2026-09-24 10:15:00 ws12 (TO(exf)) | 2026-09-24 10:15:00 ws12 | 1.4 | 2026-09-24 08:33:00 | 102.0 | 4 (ws1, ws4, ws5, ws6) | 6 of 8 | 14 of 15, high 15 | 2 (ws6, ws10) | ws4 2026-09-24 08:38:00, ws9 2026-09-24 09:01:30 |  |
| 2026-09-24 08:09:50 | LOW | 85% | lowband | 2026-09-24 10:10:30 ws1 (TO(exf)) | 2026-09-24 10:10:30 ws1 | 5.9 | 2026-09-24 08:33:00 | 97.5 | 4 (ws1, ws4, ws5, ws6) | 6 of 8 | 14 of 15, high 15 | 2 (ws6, ws10) | ws4 2026-09-24 08:38:00, ws9 2026-09-24 09:01:30 |  |
| 2026-09-24 10:16:25 | HIGH | 73% | highband | 2026-09-24 11:18:00 ws9 (TO(exf)) | 2026-09-24 11:18:00 ws9 | 0.6 | 2026-09-24 10:55:00 | 23.0 | 7 (ws1, ws2, ws3, ws4, ws5, ws6, ws7) | 5 of 8 | 3 of 15, high 4 | 3 (ws1, ws4, ws13) | ws7 no, ws11 no | 3) green never above 6 of 15 in the trade; ws7, ws11 still TO(exf) at the close |
| 2026-09-24 10:16:25 | HIGH | 73% | lowband | 2026-09-24 11:16:30 ws4 (TO(exf)) | 2026-09-24 11:16:30 ws4 | 2.1 | 2026-09-24 10:55:00 | 21.5 | 7 (ws1, ws2, ws3, ws4, ws5, ws6, ws7) | 5 of 8 | 3 of 15, high 4 | 3 (ws1, ws4, ws13) | ws7 no, ws11 no |  |
| 2026-09-24 12:03:35 | HIGH | 61% | highband | 2026-09-24 12:26:30 ws15 (TO(exf)) | 2026-09-24 12:26:30 ws15 | 0.9 | 2026-09-24 12:26:00 | 0.5 | 7 (ws1, ws2, ws3, ws4, ws5, ws6, ws7) | 5 of 8 | 7 of 15, high 8 | 4 (ws1, ws3, ws4, ws5) | ws15 2026-09-24 12:26:30 |  |
| 2026-09-24 12:03:35 | HIGH | 61% | lowband | 2026-09-24 12:25:30 ws1 (TO(exf)), ws3 (TO(exf)), ws4 (TO(exf)), ws5 (TO(exf)) | 2026-09-24 12:25:30 ws1, ws3, ws4, ws5 | 1.9 | not found | - | - | - | - | - | - | not found: 2) present on 4 of 44 rows walked; 4 lines convert on one row |
| 2026-09-24 12:27:25 | LOW | 67% | highband | - | - | - | - | - | - | - | - | - | - |  |
| 2026-09-24 12:27:25 | LOW | 67% | lowband | 2026-09-24 12:34:30 ws1 (TO(exf)) | 2026-09-24 12:34:30 ws1 | 2.8 | not found | - | - | - | - | - | - | not found: 4) 0 of 15 rows walked |
| 2026-09-24 12:37:20 | HIGH | 91% | highband | 2026-09-24 13:41:30 ws8 (TO(exf)) | 2026-09-24 13:41:30 ws8 | 0.9 | 2026-09-24 12:47:00 | 54.5 | 4 (ws1, ws2, ws4, ws5) | 6 of 8 | 5 of 15, high 6 | 1 (ws1) | - |  |
| 2026-09-24 12:37:20 | HIGH | 91% | lowband | 2026-09-24 13:40:30 ws7 (TO(exf)) | 2026-09-24 13:40:30 ws7 | 1.9 | 2026-09-24 12:47:00 | 53.5 | 4 (ws1, ws2, ws4, ws5) | 6 of 8 | 5 of 15, high 6 | 1 (ws1) | - |  |
| 2026-09-24 13:56:25 | HIGH | 96% | highband | 2026-09-24 14:36:30 ws12 (TO(exf)) | 2026-09-24 14:36:30 ws12 | 0.9 | not found | - | - | - | - | - | - | not found: 3) green at its high 15 on all 81 rows walked |
| 2026-09-24 13:56:25 | HIGH | 96% | lowband | 2026-09-24 14:36:00 ws5 (TO(exf)) | 2026-09-24 14:36:00 ws5 | 1.4 | not found | - | - | - | - | - | - | not found: 3) green at its high 15 on all 80 rows walked |
| 2026-09-24 14:37:25 | LOW | 60% | highband | - | - | - | - | - | - | - | - | - | - |  |
| 2026-09-24 14:37:25 | LOW | 60% | lowband | 2026-09-24 15:04:30 ws4 (TO(exf)) | 2026-09-24 15:04:30 ws4 | 0.7 | 2026-09-24 15:03:00 | 1.5 | 5 (ws1, ws3, ws5, ws6, ws7) | 7 of 8 | 4 of 15, high 5 | 2 (ws4, ws5) | - |  |
| 2026-09-24 15:05:10 | HIGH | 86% | highband | - | - | - | - | - | - | - | - | - | - |  |
| 2026-09-24 15:05:10 | HIGH | 86% | lowband | 2026-09-24 15:51:00 ws5 (TO(exf)) | 2026-09-24 15:51:00 ws5 | 1.0 | 2026-09-24 15:30:30 | 20.5 | 7 (ws1, ws2, ws3, ws4, ws5, ws6, ws7) | 7 of 8 | 13 of 15, high 15 | 1 (ws3) | ws2 2026-09-24 15:32:30, ws4 2026-09-24 15:32:30 |  |
| 2026-09-24 15:52:00 | LOW | 82% | highband | 2026-09-24 16:15:00 ws14 (TO(inf)-1) | - | - | - | - | - | - | - | - | - |  |
| 2026-09-24 15:52:00 | LOW | 82% | lowband | 2026-09-24 16:14:30 ws3 (TO(exf)) | 2026-09-24 16:14:30 ws3 | 1.9 | 2026-09-24 16:09:30 | 5.0 | 5 (ws1, ws2, ws3, ws4, ws5) | 5 of 8 | 3 of 15, high 4 | 1 (ws14) | ws2 2026-09-24 16:10:30, ws3 2026-09-24 16:14:30, ws12 no, ws15 no | lowband ws2, ws3 convert; highband ws12, ws15 do not |
| 2026-09-24 16:16:25 | HIGH | 75% | highband | 2026-09-24 16:32:30 ws10 (TO(inf)+1) | - | - | - | - | - | - | - | - | - |  |
| 2026-09-24 16:16:25 | HIGH | 75% | lowband | 2026-09-24 16:43:00 ws1 (TO(exf)) | 2026-09-24 16:43:00 ws1 | 1.4 | not found | - | - | - | - | - | - | not found: 3) green at its high 15 on all 54 rows walked |
| 2026-09-24 16:44:25 | LOW | 93% | highband | 2026-09-24 18:00:30 ws14 (TO(inf)0), ws15 (TO(inf)-1) | 2026-09-24 17:57:30 ws9, ws13 | 11.2 | 2026-09-24 17:35:00 | 22.5 | 6 (ws1, ws2, ws3, ws4, ws5, ws7) | 7 of 8 | 6 of 15, high 7 | 2 (ws9, ws10) | ws4 2026-09-24 17:44:30, ws7 2026-09-24 17:47:00, ws8 2026-09-24 17:47:00 |  |
| 2026-09-24 16:44:25 | LOW | 93% | lowband | 2026-09-24 18:06:30 ws1 (TO(exf)), ws6 (TO(exf)) | 2026-09-24 18:06:30 ws1, ws6 | 2.2 | 2026-09-24 17:35:00 | 31.5 | 6 (ws1, ws2, ws3, ws4, ws5, ws7) | 7 of 8 | 6 of 15, high 7 | 2 (ws9, ws10) | ws4 2026-09-24 17:44:30, ws7 2026-09-24 17:47:00, ws8 2026-09-24 17:47:00 |  |
| 2026-09-24 18:40:45 | LOW | 97% | highband | 2026-09-24 18:47:00 ws12 (TO(exf)), ws13 (TO(exf)) | 2026-09-24 18:47:00 ws12, ws13 | 3.4 | not found | - | - | - | - | - | - | not found: 2) 0 of 13 rows walked |
| 2026-09-24 18:40:45 | LOW | 97% | lowband | - | - | - | - | - | - | - | - | - | - |  |
| 2026-09-24 18:50:25 | HIGH | 68% | highband | - | - | - | - | - | - | - | - | - | - |  |
| 2026-09-24 18:50:25 | HIGH | 68% | lowband | 2026-09-24 18:55:00 ws6 (TO(exf)) | 2026-09-24 18:55:00 ws6 | 4.8 | 2026-09-24 18:54:30 | 0.5 | 7 (ws1, ws2, ws3, ws4, ws5, ws6, ws7) | 6 of 8 | 8 of 15, high 9 | 2 (ws1, ws7) | ws6 2026-09-24 18:55:00 |  |
| 2026-09-24 18:59:50 | LOW | 76% | highband | 2026-09-24 19:05:30 ws12 (TO(inf)-2) | - | - | - | - | - | - | - | - | - |  |
| 2026-09-24 18:59:50 | LOW | 76% | lowband | 2026-09-24 19:06:00 ws1 (TO(exf)) | 2026-09-24 19:06:00 ws1 | 1.0 | not found | - | - | - | - | - | - | not found: 4) 1 of 13 rows walked |
| 2026-09-24 19:07:00 | HIGH | 93% | highband | 2026-09-24 19:35:30 ws9 (TO(exf)) | 2026-09-24 19:35:30 ws9 | 1.9 | 2026-09-24 19:27:30 | 8.0 | 5 (ws1, ws2, ws3, ws4, ws6) | 8 of 8 | 13 of 15, high 15 | 1 (ws4) | ws2 2026-09-24 19:28:00, ws3 2026-09-24 19:35:30, ws4 2026-09-24 19:35:30, ws6 2026-09-24 19:35:30 |  |
| 2026-09-24 19:07:00 | HIGH | 93% | lowband | 2026-09-24 19:35:30 ws3 (TO(exf)), ws4 (TO(exf)), ws5 (TO(exf)), ws6 (TO(exf)), ws7 (TO(exf)) | 2026-09-24 19:35:30 ws3, ws4, ws5, ws6, ws7 | 1.9 | 2026-09-24 19:27:30 | 8.0 | 5 (ws1, ws2, ws3, ws4, ws6) | 8 of 8 | 13 of 15, high 15 | 1 (ws4) | ws2 2026-09-24 19:28:00, ws3 2026-09-24 19:35:30, ws4 2026-09-24 19:35:30, ws6 2026-09-24 19:35:30 | 5 lines convert on one row |
| 2026-09-24 19:37:25 | LOW | 84% | highband | 2026-09-24 20:25:30 ws9 (TO(inf)-1) | - | - | - | - | - | - | - | - | - |  |
| 2026-09-24 19:37:25 | LOW | 84% | lowband | 2026-09-24 20:22:30 ws7 (TO(exf)) | 2026-09-24 20:22:30 ws7 | 4.9 | 2026-09-24 20:22:00 | 0.5 | 7 (ws1, ws2, ws3, ws4, ws5, ws6, ws7) | 7 of 8 | 14 of 15, high 15 | 1 (ws10) | ws7 2026-09-24 20:22:30 |  |
| 2026-09-24 20:27:25 | HIGH | 90% | highband | - | - | - | - | - | - | - | - | - | - |  |
| 2026-09-24 20:27:25 | HIGH | 90% | lowband | 2026-09-24 21:02:30 ws5 (TO(exf)) | 2026-09-24 21:02:30 ws5 | 1.2 | 2026-09-24 20:54:30 | 8.0 | 7 (ws1, ws2, ws3, ws4, ws5, ws6, ws7) | 7 of 8 | 1 of 15, high 6 | 2 (ws4, ws5) | - |  |
| 2026-09-24 21:03:45 | LOW | 91% | highband | 2026-09-24 21:10:30 ws12 (TO(inf)-1) | - | - | - | - | - | - | - | - | - |  |
| 2026-09-24 21:03:45 | LOW | 91% | lowband | 2026-09-24 21:08:30 ws1 (TO(exf)) | 2026-09-24 21:08:30 ws1 | 8.9 | not found | - | - | - | - | - | - | not found: 4) 0 of 10 rows walked |
| 2026-09-24 21:17:25 | HIGH | 72% | highband | 2026-09-24 21:31:00 ws9 (TO(inf)+1) | - | - | - | - | - | - | - | - | - |  |
| 2026-09-24 21:17:25 | HIGH | 72% | lowband | 2026-09-24 21:36:00 ws7 (TO(inf)+1) | 2026-09-24 21:22:30 ws1 | 14.9 | not found | - | - | - | - | - | - | not found: 4) 0 of 11 rows walked |
| 2026-09-24 21:37:25 | LOW | 93% | highband | 2026-09-24 22:37:00 ws10 (TO(exf)) | 2026-09-24 22:37:00 ws10 | 12.4 | not found | - | - | - | - | - | - | not found: 3) red at its high 15 on all 120 rows walked |
| 2026-09-24 21:37:25 | LOW | 93% | lowband | 2026-09-24 22:48:00 ws2 (TO(exf)), ws3 (TO(inf)-1) | 2026-09-24 22:48:00 ws2 | 1.4 | not found | - | - | - | - | - | - | not found: 3) red at its high 15 on all 142 rows walked |
| 2026-09-24 22:49:25 | HIGH | 54% | highband | 2026-09-25 01:19:30 ws11 (TO(exf)), ws13 (TO(exf)) | 2026-09-25 01:19:30 ws11, ws13 | 0.9 | 2026-09-24 23:40:30 | 99.0 | 4 (ws4, ws5, ws6, ws7) | 7 of 8 | 0 of 15, high 2 | 1 (ws6) | ws8 2026-09-24 23:41:00 | 3) green high only 2 by the walk-back row |
| 2026-09-24 22:49:25 | HIGH | 54% | lowband | 2026-09-25 01:12:00 ws4 (TO(inf)0) | 2026-09-25 01:07:30 ws2 | 12.9 | 2026-09-24 23:40:30 | 87.0 | 4 (ws4, ws5, ws6, ws7) | 7 of 8 | 0 of 15, high 2 | 1 (ws6) | ws8 2026-09-24 23:41:00 |  |

## Counts

| band | rows with a TO(exf) into AW flip | of them 2.0 min or less before the trade closes | 5.0 min or less |
|---|---|---|---|
| highband | 13 | 7 | 10 |
| lowband | 30 | 18 | 24 |

| walk-back | band rows |
|---|---|
| all four present on a row before the flip | 30 |
| not found | 13 |
| no TO(exf) into AW flip in the band | 19 |

- the trade's close is the next pooled pivot's confirm bar, 90 s after its cross - the pseudo trade, not a realtime read
- OPEN: which artefact printed his 2026-09-24 02:11:30 lineage2 exhaust. It is not orac-exhaust (fires 03:07:30, 07:23:30, 07:45:30 on 09-24 - workmate #68)

## His 1119 correction to the small-trade read

*"0258 was anything but small, so this tells me that my criteria is inadequate."* / *"the other marker is the count of distinct lines printing TO(exf) during the trade - I think anthing more the 1 line in TO(exf) during the trade would make the trade 'not small'"*,
then his ruling *"highband lines printing TO(exf) during the trade:  2 is the max for a small trade."* - the rows over 2 are culled.
The tables above used the old >50% mid-board read and are superseded for the trade list.

- OPEN, his: the travel marker's numbers (ranges per line, lines per trade), and whether the >50% mid-board read stays
- "ranges travelled" (MINE): a line's lowest to highest TO(inf) range, both ends counted, of the 7 (-3 to +3)

| trade opens | target-side | highband lines travelling 4+ of the 7 ranges | old mid-board share |
|---|---|---|---|
| 2026-09-23 23:47:25 | HIGH | 0 of 8 | 90% |
| 2026-09-24 00:35:25 | LOW | 0 of 8 | 100% |
| 2026-09-24 00:57:25 | HIGH | 0 of 8 | 79% |
| 2026-09-24 01:39:25 | LOW | 0 of 8 | 95% |
| 2026-09-24 05:17:25 | LOW | 3 of 8 | 74% |
| 2026-09-24 06:08:15 | HIGH | 0 of 8 | 96% |
| 2026-09-24 07:02:25 | LOW | 0 of 8 | 100% |
| 2026-09-24 11:18:35 | LOW | 5 of 8 | 20% |
| 2026-09-24 12:27:25 | LOW | 0 of 8 | 67% |
| 2026-09-24 13:42:25 | LOW | 0 of 8 | 34% |
| 2026-09-24 14:37:25 | LOW | 2 of 8 | 60% |
| 2026-09-24 15:05:10 | HIGH | 1 of 8 | 86% |
| 2026-09-24 16:16:25 | HIGH | 0 of 8 | 75% |
| 2026-09-24 18:08:45 | HIGH | 3 of 8 | 28% |
| 2026-09-24 18:50:25 | HIGH | 0 of 8 | 68% |
| 2026-09-24 18:59:50 | LOW | 0 of 8 | 76% |
| 2026-09-24 19:07:00 | HIGH | 1 of 8 | 93% |
| 2026-09-24 19:37:25 | LOW | 2 of 8 | 84% |
| 2026-09-24 20:27:25 | HIGH | 0 of 8 | 90% |
| 2026-09-24 21:17:25 | HIGH | 0 of 8 | 72% |

## His 1119 fdm3-small-trade - the causal form

*"there's no differentiation here.  this means the TOexf prints are the decider"* / *"can you turn this small-trade detector into a causal mech?  it would have to evolve with the walk - the resting state is `small-trade` until the mech(s) prove `large-trade`"*.
His picks: 8792 first, then the walk; *"print it underneath the existing 'legmage' data.  the labels will be `sml` and `lrg`"*; hold to the trade's close; name fdm3-small-trade, knob fdm3-small-trade-max-toexf = 2.

- per row: distinct ws8-15 lines reading TO(exf) on any row from the trade's first row to this one; `lrg` above 2, held to the close
- encoding: bit 6 of the legMage byte (the workmate's call, sidegig chat #70); row stays 55 bytes
- BUILT IN SCRATCH ONLY (scratchpad small_trade_page/): page, knobs, shim, reader. Not ported - the workmate put to Joe who builds it, since the page is theirs (chat #70)
- offline check on 8792's served rows, pivots as found: 35 trades on 09-24, 20 `sml` at the close, 0 disagree with the whole-trade count

## Live on 8792 (his "you can overwrite 8792" / "and stop the other instances")

- ported into fdm3_oracle.py, fdm3_knobs.py, fdm3_knobs_shim.py, oracle_rows.py - NOT committed
- 8792 restarted from the repo file: 615.6 s, CONTROL MATCH 257295, the per-trade second-construction assert passed in all 4 states
- against the saved old 8792, all 4 states: 0 bytes differ outside the legMage byte, 0 in legMage bits 0-5
- 09-24, pivots as found: 35 trades, 20 sml on their last row, 0 disagree with the whole-trade count
- stopped: 8789, 8790, 8791. 8788 is the systemd unit, still up (needs his password)
