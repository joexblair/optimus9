# cws1b CROSSING TO THE COUNTER TARGET-SIDE OOB - where it lands in the walks. 2026-08-30 00:00:00 .. 2026-09-03 23:59:55,
#   first side HIGH. A MEASUREMENT: no cadence is built, nothing in the walk is changed.
# the cross: cws1b CLOSED entering oob 15/85 on the side opposite the target. No wob.
# L2_T3_ON 1 | L2_LIN_HOP 2 | L2_MOM_MAXTF 12 | ex-fence 20/80 | RULED_OK True
# the control: ws5r 2026-09-03 00:35:00 = 12.48, expected 12.48

| the read | value |
|---|---|
| walks in the window | 60 |
| walks that armed and exhausted | 59 |
| cadence firings, arm..exhaust | 69 |
| walks with at least one firing | 27 |
| firings with no rider | 0 |

| the cadence bar | the walk armed | target side | cws1b closed | the rider | the rider r | rider ex-fence | rider oob | rider reversed since the last decision | candidates on the whole board | candidates inside lin_hop 2 | what the cadence would do | the walk exhausts today |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-30 00:59:00 | 2026-08-30 00:17:00 | HIGH | 1.28 | cws1 | 24.71 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-08-30 01:26:00 |
| 2026-08-30 01:05:00 | 2026-08-30 00:17:00 | HIGH | 13.29 | cws1 | 38.09 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-08-30 01:26:00 |
| 2026-08-30 10:09:00 | 2026-08-30 07:24:20 | LOW | 100.70 | cws12 | 35.42 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-08-30 11:01:00 |
| 2026-08-30 10:19:00 | 2026-08-30 07:24:20 | LOW | 91.60 | cws12 | 49.70 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-08-30 11:01:00 |
| 2026-08-30 10:22:00 | 2026-08-30 07:24:20 | LOW | 105.07 | cws12 | 49.70 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-08-30 11:01:00 |
| 2026-08-30 10:47:10 | 2026-08-30 07:24:20 | LOW | 85.15 | cws12 | 70.91 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-08-30 11:01:00 |
| 2026-08-30 11:32:00 | 2026-08-30 11:10:00 | HIGH | 12.90 | cws12 | 68.58 | no | no | no | none | none | EXHAUST | 2026-08-30 12:02:00 |
| 2026-08-30 11:35:10 | 2026-08-30 11:10:00 | HIGH | 8.20 | cws12 | 68.58 | no | no | no | none | none | EXHAUST | 2026-08-30 12:02:00 |
| 2026-08-30 11:46:00 | 2026-08-30 11:10:00 | HIGH | 13.16 | cws12 | 54.30 | no | no | no | none | none | EXHAUST | 2026-08-30 12:02:00 |
| 2026-08-30 11:50:00 | 2026-08-30 11:10:00 | HIGH | 13.44 | cws12 | 48.61 | no | no | no | none | none | EXHAUST | 2026-08-30 12:02:00 |
| 2026-08-30 16:13:00 | 2026-08-30 14:36:00 | LOW | 92.25 | cws12 | 38.70 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-08-30 16:13:00 |
| 2026-08-30 19:21:00 | 2026-08-30 18:33:00 | HIGH | 14.16 | cws8 | 66.72 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-08-30 19:54:00 |
| 2026-08-30 22:22:00 | 2026-08-30 21:59:00 | HIGH | 8.34 | cws1 | 50.06 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-08-30 22:59:00 |
| 2026-08-30 22:27:00 | 2026-08-30 21:59:00 | HIGH | 13.24 | cws1 | 22.65 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-08-30 22:59:00 |
| 2026-08-30 22:30:00 | 2026-08-30 21:59:00 | HIGH | 12.95 | cws1 | 50.39 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-08-30 22:59:00 |
| 2026-08-30 22:36:00 | 2026-08-30 21:59:00 | HIGH | 13.88 | cws1 | 53.47 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-08-30 22:59:00 |
| 2026-08-30 22:50:00 | 2026-08-30 21:59:00 | HIGH | 12.63 | cws1 | 9.06 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-08-30 22:59:00 |
| 2026-08-31 01:08:00 | 2026-08-31 00:12:00 | HIGH | 14.76 | cws12 | 94.69 | yes | yes | no | none | none | HOLD - the rider is oob | 2026-08-31 02:16:00 |
| 2026-08-31 01:34:00 | 2026-08-31 00:12:00 | HIGH | 10.61 | cws12 | 85.45 | yes | yes | yes | none | none | HOLD - the rider is oob | 2026-08-31 02:16:00 |
| 2026-08-31 01:38:00 | 2026-08-31 00:12:00 | HIGH | 10.57 | cws12 | 71.17 | no | no | no | none | none | EXHAUST | 2026-08-31 02:16:00 |
| 2026-08-31 01:44:00 | 2026-08-31 00:12:00 | HIGH | 14.60 | cws12 | 71.17 | no | no | no | none | none | EXHAUST | 2026-08-31 02:16:00 |
| 2026-08-31 01:46:05 | 2026-08-31 00:12:00 | HIGH | 7.93 | cws12 | 71.17 | no | no | no | none | none | EXHAUST | 2026-08-31 02:16:00 |
| 2026-08-31 04:05:00 | 2026-08-31 03:20:00 | HIGH | 11.62 | cws11 | 85.95 | yes | yes | no | none | none | HOLD - the rider is oob | 2026-08-31 04:27:00 |
| 2026-08-31 04:08:00 | 2026-08-31 03:20:00 | HIGH | 10.48 | cws11 | 85.95 | yes | yes | yes | none | none | HOLD - the rider is oob | 2026-08-31 04:27:00 |
| 2026-08-31 04:12:00 | 2026-08-31 03:20:00 | HIGH | 14.18 | cws11 | 85.95 | yes | yes | yes | none | none | HOLD - the rider is oob | 2026-08-31 04:27:00 |
| 2026-08-31 10:38:10 | 2026-08-31 09:08:00 | LOW | 97.67 | cws12 | 30.26 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-08-31 11:29:00 |
| 2026-08-31 10:42:05 | 2026-08-31 09:08:00 | LOW | 91.40 | cws12 | 30.26 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-08-31 11:29:00 |
| 2026-08-31 10:51:05 | 2026-08-31 09:08:00 | LOW | 96.58 | cws12 | 42.86 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-08-31 11:29:00 |
| 2026-08-31 11:18:00 | 2026-08-31 09:08:00 | LOW | 87.59 | cws12 | 67.23 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-08-31 11:29:00 |
| 2026-08-31 12:38:00 | 2026-08-31 12:20:00 | HIGH | 11.19 | cws4 | 32.25 | no | no | no | none | none | EXHAUST | 2026-08-31 13:04:00 |
| 2026-08-31 12:48:00 | 2026-08-31 12:20:00 | HIGH | 13.46 | cws4 | 4.76 | no | no | no | none | none | EXHAUST | 2026-08-31 13:04:00 |
| 2026-08-31 12:53:00 | 2026-08-31 12:20:00 | HIGH | 13.99 | cws4 | 4.47 | no | no | no | none | none | EXHAUST | 2026-08-31 13:04:00 |
| 2026-08-31 20:13:00 | 2026-08-31 19:12:00 | LOW | 88.06 | cws12 | 17.48 | yes | no | yes | none | none | EXHAUST, t4 tag | 2026-08-31 21:08:00 |
| 2026-09-01 00:04:00 | 2026-08-31 22:08:05 | LOW | 100.29 | cws8 | 77.99 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-01 00:36:00 |
| 2026-09-01 00:10:00 | 2026-08-31 22:08:05 | LOW | 87.25 | cws8 | 81.18 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-01 00:36:00 |
| 2026-09-01 13:31:00 | 2026-09-01 12:12:00 | LOW | 86.36 | cws12 | 21.29 | no | no | no | none | none | EXHAUST | 2026-09-01 13:59:00 |
| 2026-09-01 13:48:00 | 2026-09-01 12:12:00 | LOW | 94.81 | cws12 | 49.70 | no | no | no | none | none | EXHAUST | 2026-09-01 13:59:00 |
| 2026-09-01 15:00:00 | 2026-09-01 14:04:00 | HIGH | -18.11 | cws12 | 61.36 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-01 15:19:00 |
| 2026-09-01 15:48:00 | 2026-09-01 15:19:05 | LOW | 87.22 | cws8 | 39.40 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-01 16:26:00 |
| 2026-09-01 15:51:00 | 2026-09-01 15:19:05 | LOW | 86.20 | cws8 | 39.40 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-01 16:26:00 |
| 2026-09-01 17:59:00 | 2026-09-01 17:24:00 | HIGH | 11.23 | cws9 | 73.45 | no | no | no | none | none | EXHAUST | 2026-09-01 18:56:00 |
| 2026-09-01 18:01:00 | 2026-09-01 17:24:00 | HIGH | 14.78 | cws9 | 61.25 | no | no | no | none | none | EXHAUST | 2026-09-01 18:56:00 |
| 2026-09-01 18:04:00 | 2026-09-01 17:24:00 | HIGH | 14.00 | cws9 | 61.25 | no | no | no | none | none | EXHAUST | 2026-09-01 18:56:00 |
| 2026-09-01 18:08:00 | 2026-09-01 17:24:00 | HIGH | 5.82 | cws9 | 61.25 | no | no | no | none | none | EXHAUST | 2026-09-01 18:56:00 |
| 2026-09-01 18:13:00 | 2026-09-01 17:24:00 | HIGH | 13.07 | cws9 | 47.45 | no | no | no | none | none | EXHAUST | 2026-09-01 18:56:00 |
| 2026-09-01 18:15:00 | 2026-09-01 17:24:00 | HIGH | 0.48 | cws9 | 47.45 | no | no | no | none | none | EXHAUST | 2026-09-01 18:56:00 |
| 2026-09-01 18:36:00 | 2026-09-01 17:24:00 | HIGH | -6.75 | cws9 | 6.41 | no | no | no | none | none | EXHAUST | 2026-09-01 18:56:00 |
| 2026-09-01 18:42:00 | 2026-09-01 17:24:00 | HIGH | 12.26 | cws9 | 6.41 | no | no | no | none | none | EXHAUST | 2026-09-01 18:56:00 |
| 2026-09-02 04:09:00 | 2026-09-02 02:16:00 | HIGH | 9.50 | cws12 | 78.58 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-02 04:25:00 |
| 2026-09-02 04:16:00 | 2026-09-02 02:16:00 | HIGH | -2.52 | cws12 | 64.30 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-02 04:25:00 |
| 2026-09-02 04:22:00 | 2026-09-02 02:16:00 | HIGH | 12.53 | cws12 | 64.30 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-02 04:25:00 |
| 2026-09-02 06:03:00 | 2026-09-02 05:36:00 | HIGH | 1.56 | cws5 | 53.67 | no | no | yes | ws9 | none | BATON -> ws9 | 2026-09-02 06:45:00 |
| 2026-09-02 06:13:00 | 2026-09-02 05:36:00 | HIGH | 8.86 | cws5 | 36.12 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-02 06:45:00 |
| 2026-09-02 06:30:00 | 2026-09-02 05:36:00 | HIGH | 9.57 | cws5 | 21.40 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-02 06:45:00 |
| 2026-09-02 10:41:00 | 2026-09-02 10:18:00 | HIGH | -7.22 | cws3 | 44.28 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-02 11:39:00 |
| 2026-09-02 14:30:00 | 2026-09-02 13:45:00 | HIGH | 4.48 | cws8 | 71.63 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-02 15:21:00 |
| 2026-09-02 14:32:00 | 2026-09-02 13:45:00 | HIGH | 13.99 | cws8 | 61.67 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-02 15:21:00 |
| 2026-09-02 14:53:05 | 2026-09-02 13:45:00 | HIGH | 14.93 | cws8 | 43.83 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-02 15:21:00 |
| 2026-09-02 14:58:00 | 2026-09-02 13:45:00 | HIGH | 10.05 | cws8 | 32.49 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-02 15:21:00 |
| 2026-09-02 15:07:00 | 2026-09-02 13:45:00 | HIGH | 6.50 | cws8 | 20.84 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-02 15:21:00 |
| 2026-09-02 19:25:00 | 2026-09-02 18:56:00 | HIGH | 1.05 | cws5 | 46.89 | no | no | no | none | none | EXHAUST | 2026-09-02 19:46:00 |
| 2026-09-02 23:04:00 | 2026-09-02 22:04:00 | LOW | 89.81 | cws9 | 31.02 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-02 23:37:00 |
| 2026-09-02 23:06:00 | 2026-09-02 22:04:00 | LOW | 95.93 | cws9 | 45.30 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-02 23:37:00 |
| 2026-09-02 23:27:00 | 2026-09-02 22:04:00 | LOW | 86.17 | cws9 | 64.47 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-02 23:37:00 |
| 2026-09-03 00:33:00 | 2026-09-02 23:48:00 | HIGH | 10.64 | cws12 | 62.51 | no | no | yes | none | none | EXHAUST, t4 tag | 2026-09-03 00:45:00 |
| 2026-09-03 04:10:00 | 2026-09-03 03:24:00 | LOW | 93.91 | cws8 | 25.20 | no | no | yes | ws10 | ws10 | BATON -> ws10 | 2026-09-03 04:40:00 |
| 2026-09-03 05:26:00 | 2026-09-03 04:51:00 | HIGH | 14.67 | cws5 | 39.45 | no | no | no | none | none | EXHAUST | 2026-09-03 05:39:00 |
| 2026-09-03 08:06:00 | 2026-09-03 07:48:00 | LOW | 93.31 | cws7 | 29.78 | no | no | no | none | none | EXHAUST | 2026-09-03 08:19:00 |
| 2026-09-03 21:20:00 | 2026-09-03 19:56:00 | LOW | 102.58 | cws12 | 16.14 | yes | no | yes | none | none | EXHAUST, t4 tag | 2026-09-03 21:29:00 |

| what the cadence would do | firings |
|---|---|
| BATON | 2 |
| EXHAUST | 62 |
| HOLD | 5 |

| the read | value |
|---|---|
| firings that would EXHAUST the walk | 62 |
| of those, earlier than the walk exhausts today | 61 |
| median seconds earlier | 1680 |
| the largest, seconds earlier | 3480 |

## 2026-08-30 00:59:00 - the board, target side HIGH, rider cws1, cws1b 1.28

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 24.71 | no | no | yes | no | yes | no |
| ws2 | 34.51 | no | no | no | yes | yes | no |
| ws3 | 51.20 | no | no | no | yes | yes | no |
| ws4 | 40.38 | no | no | yes | yes | no | no |
| ws5 | 32.76 | no | no | no | yes | no | no |
| ws6 | 29.52 | no | no | no | yes | no | no |
| ws7 | 51.15 | no | no | no | yes | no | no |
| ws8 | 42.33 | no | no | no | yes | no | no |
| ws9 | 31.78 | no | no | no | yes | no | no |
| ws10 | 39.81 | no | no | no | yes | no | no |
| ws11 | 33.33 | no | no | no | yes | no | no |
| ws12 | 52.94 | no | no | yes | yes | no | no |

## 2026-08-30 01:05:00 - the board, target side HIGH, rider cws1, cws1b 13.29

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 38.09 | no | no | yes | no | yes | no |
| ws2 | 17.14 | no | no | no | yes | yes | no |
| ws3 | 33.85 | no | no | no | yes | yes | no |
| ws4 | 30.99 | no | no | no | yes | no | no |
| ws5 | 27.47 | no | no | no | yes | no | no |
| ws6 | 25.86 | no | no | no | yes | no | no |
| ws7 | 40.47 | no | no | no | yes | no | no |
| ws8 | 33.34 | no | no | no | yes | no | no |
| ws9 | 29.04 | no | no | no | yes | no | no |
| ws10 | 29.94 | no | no | no | yes | no | no |
| ws11 | 33.33 | no | no | no | yes | no | no |
| ws12 | 38.66 | no | no | no | yes | no | no |

## 2026-08-30 10:09:00 - the board, target side LOW, rider cws12, cws1b 100.70

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 71.80 | no | no | no | no | yes | no |
| ws2 | 63.89 | no | no | no | no | yes | no |
| ws3 | 67.97 | no | no | no | no | yes | no |
| ws4 | 81.84 | no | no | no | no | yes | no |
| ws5 | 67.58 | no | no | no | no | yes | no |
| ws6 | 70.93 | no | no | no | no | yes | no |
| ws7 | 63.23 | no | no | no | no | yes | no |
| ws8 | 59.50 | no | no | no | no | yes | no |
| ws9 | 56.88 | no | no | no | no | yes | no |
| ws10 | 46.11 | no | no | no | no | yes | no |
| ws11 | 22.91 | no | no | no | no | yes | no |
| ws12 | 35.42 | no | no | no | no | yes | no |

## 2026-08-30 10:19:00 - the board, target side LOW, rider cws12, cws1b 91.60

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 48.49 | no | no | yes | no | yes | no |
| ws2 | 65.50 | no | no | no | no | yes | no |
| ws3 | 79.20 | no | no | no | no | yes | no |
| ws4 | 78.68 | no | no | yes | no | yes | no |
| ws5 | 73.76 | no | no | no | no | yes | no |
| ws6 | 83.24 | no | no | no | no | yes | no |
| ws7 | 71.32 | no | no | no | no | yes | no |
| ws8 | 73.79 | no | no | no | no | yes | no |
| ws9 | 57.88 | no | no | no | no | yes | no |
| ws10 | 54.05 | no | no | no | no | yes | no |
| ws11 | 36.83 | no | no | no | no | yes | no |
| ws12 | 49.70 | no | no | no | no | yes | no |

## 2026-08-30 10:22:00 - the board, target side LOW, rider cws12, cws1b 105.07

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 67.78 | no | no | no | no | yes | no |
| ws2 | 60.82 | no | no | yes | no | yes | no |
| ws3 | 86.98 | no | no | no | no | yes | no |
| ws4 | 78.68 | no | no | yes | no | yes | no |
| ws5 | 81.70 | no | no | no | no | yes | no |
| ws6 | 83.24 | no | no | no | no | yes | no |
| ws7 | 71.32 | no | no | no | no | yes | no |
| ws8 | 73.79 | no | no | no | no | yes | no |
| ws9 | 65.01 | no | no | no | no | yes | no |
| ws10 | 64.53 | no | no | no | no | yes | no |
| ws11 | 36.83 | no | no | no | no | yes | no |
| ws12 | 49.70 | no | no | no | no | yes | no |

## 2026-08-30 10:47:10 - the board, target side LOW, rider cws12, cws1b 85.15

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 76.28 | no | no | no | no | yes | no |
| ws2 | 41.86 | no | no | no | no | yes | no |
| ws3 | 20.36 | no | no | yes | no | yes | no |
| ws4 | 48.81 | no | no | yes | no | yes | no |
| ws5 | 64.57 | no | no | yes | no | yes | no |
| ws6 | 84.74 | no | no | yes | no | yes | no |
| ws7 | 86.46 | no | no | yes | no | yes | no |
| ws8 | 88.16 | no | no | no | no | yes | no |
| ws9 | 74.45 | no | no | no | no | yes | no |
| ws10 | 87.28 | no | no | no | no | yes | no |
| ws11 | 58.71 | no | no | no | no | yes | no |
| ws12 | 70.91 | no | no | no | no | yes | no |

## 2026-08-30 11:32:00 - the board, target side HIGH, rider cws12, cws1b 12.90

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 40.08 | no | no | yes | no | yes | no |
| ws2 | 28.77 | no | no | no | no | yes | no |
| ws3 | 47.79 | no | no | no | no | yes | no |
| ws4 | 47.20 | no | no | yes | no | yes | no |
| ws5 | 44.00 | no | no | no | no | yes | no |
| ws6 | 28.06 | no | no | no | no | yes | no |
| ws7 | 42.46 | no | no | no | no | yes | no |
| ws8 | 44.73 | no | no | no | no | yes | no |
| ws9 | 54.08 | no | no | no | no | yes | no |
| ws10 | 55.95 | no | no | no | no | yes | no |
| ws11 | 67.13 | no | no | yes | no | yes | no |
| ws12 | 68.58 | no | no | no | no | yes | no |

## 2026-08-30 11:35:10 - the board, target side HIGH, rider cws12, cws1b 8.20

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 35.79 | no | no | yes | no | yes | no |
| ws2 | 24.27 | no | no | no | no | yes | no |
| ws3 | 33.51 | no | no | no | no | yes | no |
| ws4 | 47.20 | no | no | no | no | yes | no |
| ws5 | 38.69 | no | no | no | no | yes | no |
| ws6 | 28.06 | no | no | no | no | yes | no |
| ws7 | 28.43 | no | no | no | no | yes | no |
| ws8 | 44.73 | no | no | no | no | yes | no |
| ws9 | 43.31 | no | no | no | no | yes | no |
| ws10 | 55.95 | no | no | no | no | yes | no |
| ws11 | 52.84 | no | no | no | no | yes | no |
| ws12 | 68.58 | no | no | no | no | yes | no |

## 2026-08-30 11:46:00 - the board, target side HIGH, rider cws12, cws1b 13.16

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 63.50 | no | no | yes | no | yes | no |
| ws2 | 54.74 | no | no | yes | no | yes | no |
| ws3 | 28.22 | no | no | yes | no | yes | no |
| ws4 | 12.52 | no | no | no | no | yes | no |
| ws5 | 12.15 | no | no | no | no | yes | no |
| ws6 | 23.22 | no | no | no | no | yes | no |
| ws7 | 22.31 | no | no | no | no | yes | no |
| ws8 | 23.46 | no | no | no | no | yes | no |
| ws9 | 29.02 | no | no | no | no | yes | no |
| ws10 | 44.39 | no | no | no | no | yes | no |
| ws11 | 42.52 | no | no | no | no | yes | no |
| ws12 | 54.30 | no | no | no | no | yes | no |

## 2026-08-30 11:50:00 - the board, target side HIGH, rider cws12, cws1b 13.44

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 31.31 | no | no | no | no | yes | no |
| ws2 | 71.07 | no | no | yes | no | yes | no |
| ws3 | 33.81 | no | no | yes | no | yes | no |
| ws4 | 12.52 | no | no | no | no | yes | no |
| ws5 | 6.91 | no | no | no | no | yes | no |
| ws6 | 20.88 | no | no | no | no | yes | no |
| ws7 | 21.75 | no | no | no | no | yes | no |
| ws8 | 23.46 | no | no | no | no | yes | no |
| ws9 | 29.02 | no | no | no | no | yes | no |
| ws10 | 37.30 | no | no | no | no | yes | no |
| ws11 | 42.52 | no | no | no | no | yes | no |
| ws12 | 48.61 | no | no | no | no | yes | no |

## 2026-08-30 16:13:00 - the board, target side LOW, rider cws12, cws1b 92.25

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 24.94 | no | no | yes | no | yes | no |
| ws2 | 84.49 | no | no | yes | no | yes | no |
| ws3 | 72.48 | no | no | no | no | yes | no |
| ws4 | 62.59 | no | no | no | no | yes | no |
| ws5 | 50.45 | no | no | no | no | yes | no |
| ws6 | 38.29 | no | no | yes | no | yes | no |
| ws7 | 46.52 | no | no | no | no | yes | no |
| ws8 | 58.04 | no | no | no | no | yes | no |
| ws9 | 51.51 | no | no | no | no | yes | no |
| ws10 | 44.54 | no | no | no | no | yes | no |
| ws11 | 36.39 | no | no | no | no | yes | no |
| ws12 | 38.70 | no | no | no | no | yes | no |

## 2026-08-30 19:21:00 - the board, target side HIGH, rider cws8, cws1b 14.16

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 21.60 | no | no | no | no | yes | no |
| ws2 | 48.51 | no | no | no | no | yes | no |
| ws3 | 45.91 | no | no | yes | no | yes | no |
| ws4 | 21.06 | no | no | no | no | yes | no |
| ws5 | 23.46 | no | no | no | no | yes | no |
| ws6 | 33.27 | no | no | no | no | yes | no |
| ws7 | 64.02 | no | no | no | no | yes | no |
| ws8 | 66.72 | no | no | no | no | yes | no |
| ws9 | 63.14 | no | no | yes | yes | yes | no |
| ws10 | 68.51 | no | no | yes | yes | yes | no |
| ws11 | 76.57 | no | no | no | yes | no | no |
| ws12 | 59.53 | no | no | yes | yes | no | no |

## 2026-08-30 22:22:00 - the board, target side HIGH, rider cws1, cws1b 8.34

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 50.06 | no | no | yes | no | yes | no |
| ws2 | 10.29 | no | no | no | yes | yes | no |
| ws3 | 22.35 | no | no | no | yes | yes | no |
| ws4 | 43.78 | no | no | no | yes | no | no |
| ws5 | 36.56 | no | no | yes | yes | no | no |
| ws6 | 38.67 | no | no | no | yes | no | no |
| ws7 | 41.74 | no | no | no | yes | no | no |
| ws8 | 45.76 | no | no | yes | yes | no | no |
| ws9 | 45.44 | no | no | no | yes | no | no |
| ws10 | 51.17 | no | no | no | yes | no | no |
| ws11 | 51.42 | no | no | no | yes | no | no |
| ws12 | 63.83 | no | no | no | yes | no | no |

## 2026-08-30 22:27:00 - the board, target side HIGH, rider cws1, cws1b 13.24

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 22.65 | no | no | no | no | yes | no |
| ws2 | 12.37 | no | no | yes | yes | yes | no |
| ws3 | 7.33 | no | no | no | yes | yes | no |
| ws4 | 29.50 | no | no | no | yes | no | no |
| ws5 | 38.86 | no | no | yes | yes | no | no |
| ws6 | 36.21 | no | no | no | yes | no | no |
| ws7 | 36.00 | no | no | no | yes | no | no |
| ws8 | 31.89 | no | no | no | yes | no | no |
| ws9 | 45.44 | no | no | no | yes | no | no |
| ws10 | 51.17 | no | no | no | yes | no | no |
| ws11 | 51.42 | no | no | no | yes | no | no |
| ws12 | 58.19 | no | no | no | yes | no | no |

## 2026-08-30 22:30:00 - the board, target side HIGH, rider cws1, cws1b 12.95

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 50.39 | no | no | yes | no | yes | no |
| ws2 | 27.79 | no | no | yes | yes | yes | no |
| ws3 | 10.85 | no | no | yes | yes | yes | no |
| ws4 | 20.51 | no | no | no | yes | no | no |
| ws5 | 25.96 | no | no | no | yes | no | no |
| ws6 | 32.61 | no | no | no | yes | no | no |
| ws7 | 36.00 | no | no | no | yes | no | no |
| ws8 | 31.89 | no | no | no | yes | no | no |
| ws9 | 32.44 | no | no | no | yes | no | no |
| ws10 | 41.56 | no | no | no | yes | no | no |
| ws11 | 51.42 | no | no | no | yes | no | no |
| ws12 | 58.19 | no | no | no | yes | no | no |

## 2026-08-30 22:36:00 - the board, target side HIGH, rider cws1, cws1b 13.88

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 53.47 | no | no | no | no | yes | no |
| ws2 | 39.79 | no | no | yes | yes | yes | no |
| ws3 | 17.94 | no | no | yes | yes | yes | no |
| ws4 | 21.04 | no | no | yes | yes | no | no |
| ws5 | 22.44 | no | no | no | yes | no | no |
| ws6 | 19.83 | no | no | no | yes | no | no |
| ws7 | 34.05 | no | no | no | yes | no | no |
| ws8 | 29.40 | no | no | no | yes | no | no |
| ws9 | 32.44 | no | no | no | yes | no | no |
| ws10 | 41.56 | no | no | no | yes | no | no |
| ws11 | 43.71 | no | no | no | yes | no | no |
| ws12 | 54.47 | no | no | no | yes | no | no |

## 2026-08-30 22:50:00 - the board, target side HIGH, rider cws1, cws1b 12.63

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 9.06 | no | no | no | no | yes | no |
| ws2 | 34.52 | no | no | no | yes | yes | no |
| ws3 | 34.13 | no | no | yes | yes | yes | no |
| ws4 | 23.18 | no | no | yes | yes | no | no |
| ws5 | 25.08 | no | no | yes | yes | no | no |
| ws6 | 5.70 | no | no | no | yes | no | no |
| ws7 | 12.49 | no | no | no | yes | no | no |
| ws8 | 15.11 | no | no | no | yes | no | no |
| ws9 | 28.81 | no | no | yes | yes | no | no |
| ws10 | 31.18 | no | no | yes | yes | no | no |
| ws11 | 29.47 | no | no | no | yes | no | no |
| ws12 | 40.18 | no | no | no | yes | no | no |

## 2026-08-31 01:08:00 - the board, target side HIGH, rider cws12, cws1b 14.76

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 27.46 | no | no | yes | no | yes | no |
| ws2 | 7.47 | no | no | no | no | yes | no |
| ws3 | 42.41 | no | no | yes | no | yes | no |
| ws4 | 39.15 | no | no | no | no | yes | no |
| ws5 | 55.31 | no | no | no | no | yes | no |
| ws6 | 53.29 | no | no | no | no | yes | no |
| ws7 | 77.70 | no | no | no | no | yes | no |
| ws8 | 79.38 | no | no | no | no | yes | no |
| ws9 | 85.60 | yes | yes | yes | no | yes | no |
| ws10 | 86.13 | yes | yes | yes | no | yes | no |
| ws11 | 85.57 | yes | yes | yes | no | yes | no |
| ws12 | 94.69 | yes | yes | yes | no | yes | no |

## 2026-08-31 01:34:00 - the board, target side HIGH, rider cws12, cws1b 10.61

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 12.44 | no | no | yes | no | yes | no |
| ws2 | 32.76 | no | no | no | no | yes | no |
| ws3 | 54.46 | no | no | yes | no | yes | no |
| ws4 | 32.47 | no | no | yes | no | yes | no |
| ws5 | 30.75 | no | no | no | no | yes | no |
| ws6 | 18.70 | no | no | no | no | yes | no |
| ws7 | 42.55 | no | no | no | no | yes | no |
| ws8 | 57.92 | no | no | no | no | yes | no |
| ws9 | 51.41 | no | no | no | no | yes | no |
| ws10 | 70.54 | no | no | no | no | yes | no |
| ws11 | 71.46 | no | no | no | no | yes | no |
| ws12 | 85.45 | yes | yes | yes | no | yes | no |

## 2026-08-31 01:38:00 - the board, target side HIGH, rider cws12, cws1b 10.57

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 47.96 | no | no | yes | no | yes | no |
| ws2 | 26.89 | no | no | yes | no | yes | no |
| ws3 | 49.38 | no | no | no | no | yes | no |
| ws4 | 36.56 | no | no | yes | no | yes | no |
| ws5 | 36.73 | no | no | yes | no | yes | no |
| ws6 | 21.35 | no | no | yes | no | yes | no |
| ws7 | 28.27 | no | no | no | no | yes | no |
| ws8 | 46.42 | no | no | no | no | yes | no |
| ws9 | 51.41 | no | no | no | no | yes | no |
| ws10 | 70.54 | no | no | no | no | yes | no |
| ws11 | 71.46 | no | no | no | no | yes | no |
| ws12 | 71.17 | no | no | no | no | yes | no |

## 2026-08-31 01:44:00 - the board, target side HIGH, rider cws12, cws1b 14.60

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 58.52 | no | no | yes | no | yes | no |
| ws2 | 37.57 | no | no | yes | no | yes | no |
| ws3 | 36.04 | no | no | no | no | yes | no |
| ws4 | 24.59 | no | no | no | no | yes | no |
| ws5 | 38.10 | no | no | yes | no | yes | no |
| ws6 | 19.49 | no | no | yes | no | yes | no |
| ws7 | 28.27 | no | no | no | no | yes | no |
| ws8 | 32.13 | no | no | no | no | yes | no |
| ws9 | 38.44 | no | no | no | no | yes | no |
| ws10 | 56.25 | no | no | no | no | yes | no |
| ws11 | 57.46 | no | no | no | no | yes | no |
| ws12 | 71.17 | no | no | no | no | yes | no |

## 2026-08-31 01:46:05 - the board, target side HIGH, rider cws12, cws1b 7.93

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 48.21 | no | no | no | no | yes | no |
| ws2 | 37.57 | no | no | yes | no | yes | no |
| ws3 | 23.27 | no | no | no | no | yes | no |
| ws4 | 24.59 | no | no | no | no | yes | no |
| ws5 | 31.89 | no | no | yes | no | yes | no |
| ws6 | 19.49 | no | no | yes | no | yes | no |
| ws7 | 16.42 | no | no | no | no | yes | no |
| ws8 | 32.13 | no | no | no | no | yes | no |
| ws9 | 38.44 | no | no | no | no | yes | no |
| ws10 | 56.25 | no | no | no | no | yes | no |
| ws11 | 57.46 | no | no | no | no | yes | no |
| ws12 | 71.17 | no | no | no | no | yes | no |

## 2026-08-31 04:05:00 - the board, target side HIGH, rider cws11, cws1b 11.62

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 6.80 | no | no | yes | no | yes | no |
| ws2 | 16.53 | no | no | no | no | yes | no |
| ws3 | 47.48 | no | no | no | no | yes | no |
| ws4 | 66.97 | no | no | no | no | yes | no |
| ws5 | 65.80 | no | no | no | no | yes | no |
| ws6 | 80.91 | yes | no | no | no | yes | no |
| ws7 | 72.30 | no | no | no | no | yes | no |
| ws8 | 82.79 | yes | no | no | no | yes | no |
| ws9 | 73.67 | no | no | yes | no | yes | no |
| ws10 | 86.19 | yes | yes | yes | no | yes | no |
| ws11 | 85.95 | yes | yes | yes | no | yes | no |
| ws12 | 76.18 | no | no | yes | yes | yes | no |

## 2026-08-31 04:08:00 - the board, target side HIGH, rider cws11, cws1b 10.48

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 28.29 | no | no | yes | no | yes | no |
| ws2 | 6.75 | no | no | yes | no | yes | no |
| ws3 | 33.19 | no | no | no | no | yes | no |
| ws4 | 54.85 | no | no | no | no | yes | no |
| ws5 | 65.80 | no | no | no | no | yes | no |
| ws6 | 69.79 | no | no | no | no | yes | no |
| ws7 | 72.30 | no | no | no | no | yes | no |
| ws8 | 69.94 | no | no | no | no | yes | no |
| ws9 | 73.67 | no | no | yes | no | yes | no |
| ws10 | 86.19 | yes | yes | yes | no | yes | no |
| ws11 | 85.95 | yes | yes | yes | no | yes | no |
| ws12 | 76.18 | no | no | yes | yes | yes | no |

## 2026-08-31 04:12:00 - the board, target side HIGH, rider cws11, cws1b 14.18

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 76.48 | no | no | yes | no | yes | no |
| ws2 | 15.00 | no | no | yes | no | yes | no |
| ws3 | 8.95 | no | no | no | no | yes | no |
| ws4 | 40.56 | no | no | no | no | yes | no |
| ws5 | 51.51 | no | no | no | no | yes | no |
| ws6 | 56.31 | no | no | no | no | yes | no |
| ws7 | 58.02 | no | no | no | no | yes | no |
| ws8 | 69.94 | no | no | no | no | yes | no |
| ws9 | 64.15 | no | no | yes | no | yes | no |
| ws10 | 71.90 | no | no | yes | no | yes | no |
| ws11 | 85.95 | yes | yes | yes | no | yes | no |
| ws12 | 76.18 | no | no | yes | yes | yes | no |

## 2026-08-31 10:38:10 - the board, target side LOW, rider cws12, cws1b 97.67

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 67.05 | no | no | no | no | yes | no |
| ws2 | 82.99 | no | no | no | no | yes | no |
| ws3 | 75.47 | no | no | no | no | yes | no |
| ws4 | 84.70 | no | no | no | no | yes | no |
| ws5 | 67.51 | no | no | no | no | yes | no |
| ws6 | 64.38 | no | no | no | no | yes | no |
| ws7 | 64.86 | no | no | no | no | yes | no |
| ws8 | 42.16 | no | no | no | no | yes | no |
| ws9 | 48.16 | no | no | no | no | yes | no |
| ws10 | 28.57 | no | no | no | no | yes | no |
| ws11 | 34.56 | no | no | no | no | yes | no |
| ws12 | 30.26 | no | no | no | no | yes | no |

## 2026-08-31 10:42:05 - the board, target side LOW, rider cws12, cws1b 91.40

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 68.12 | no | no | yes | no | yes | no |
| ws2 | 76.80 | no | no | yes | no | yes | no |
| ws3 | 85.59 | no | no | no | no | yes | no |
| ws4 | 84.70 | no | no | no | no | yes | no |
| ws5 | 81.80 | no | no | no | no | yes | no |
| ws6 | 78.67 | no | no | no | no | yes | no |
| ws7 | 64.86 | no | no | no | no | yes | no |
| ws8 | 56.45 | no | no | no | no | yes | no |
| ws9 | 60.70 | no | no | no | no | yes | no |
| ws10 | 42.86 | no | no | no | no | yes | no |
| ws11 | 34.56 | no | no | no | no | yes | no |
| ws12 | 30.26 | no | no | no | no | yes | no |

## 2026-08-31 10:51:05 - the board, target side LOW, rider cws12, cws1b 96.58

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 62.07 | no | no | yes | no | yes | no |
| ws2 | 78.13 | no | no | yes | no | yes | no |
| ws3 | 88.01 | no | no | yes | no | yes | no |
| ws4 | 97.29 | no | no | no | no | yes | no |
| ws5 | 90.19 | no | no | no | no | yes | no |
| ws6 | 82.25 | no | no | no | no | yes | no |
| ws7 | 87.71 | no | no | no | no | yes | no |
| ws8 | 70.73 | no | no | no | no | yes | no |
| ws9 | 74.99 | no | no | no | no | yes | no |
| ws10 | 57.14 | no | no | no | no | yes | no |
| ws11 | 47.90 | no | no | no | no | yes | no |
| ws12 | 42.86 | no | no | no | no | yes | no |

## 2026-08-31 11:18:00 - the board, target side LOW, rider cws12, cws1b 87.59

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 79.73 | no | no | no | no | yes | no |
| ws2 | 68.14 | no | no | no | no | yes | no |
| ws3 | 39.84 | no | no | yes | no | yes | no |
| ws4 | 42.93 | no | no | yes | no | yes | no |
| ws5 | 60.60 | no | no | yes | no | yes | no |
| ws6 | 56.42 | no | no | yes | no | yes | no |
| ws7 | 93.15 | no | no | no | no | yes | no |
| ws8 | 91.98 | no | no | no | no | yes | no |
| ws9 | 86.56 | no | no | yes | no | yes | no |
| ws10 | 83.53 | no | no | no | no | yes | no |
| ws11 | 76.18 | no | no | no | no | yes | no |
| ws12 | 67.23 | no | no | no | no | yes | no |

## 2026-08-31 12:38:00 - the board, target side HIGH, rider cws4, cws1b 11.19

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 54.07 | no | no | no | no | yes | no |
| ws2 | 51.83 | no | no | yes | no | yes | no |
| ws3 | 16.46 | no | no | no | no | yes | no |
| ws4 | 32.25 | no | no | no | no | yes | no |
| ws5 | 45.82 | no | no | no | yes | yes | no |
| ws6 | 61.73 | no | no | yes | yes | yes | no |
| ws7 | 52.64 | no | no | yes | yes | no | no |
| ws8 | 33.21 | no | no | yes | yes | no | no |
| ws9 | 40.62 | no | no | yes | yes | no | no |
| ws10 | 21.97 | no | no | no | yes | no | no |
| ws11 | 23.15 | no | no | no | yes | no | no |
| ws12 | 34.69 | no | no | no | yes | no | no |

## 2026-08-31 12:48:00 - the board, target side HIGH, rider cws4, cws1b 13.46

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 72.64 | no | no | yes | no | yes | no |
| ws2 | 28.85 | no | no | no | no | yes | no |
| ws3 | 18.28 | no | no | yes | no | yes | no |
| ws4 | 4.76 | no | no | no | no | yes | no |
| ws5 | 18.64 | no | no | no | yes | yes | no |
| ws6 | 35.70 | no | no | no | yes | yes | no |
| ws7 | 48.30 | no | no | yes | yes | no | no |
| ws8 | 31.62 | no | no | yes | yes | no | no |
| ws9 | 41.01 | no | no | yes | yes | no | no |
| ws10 | 21.97 | no | no | no | yes | no | no |
| ws11 | 23.15 | no | no | no | yes | no | no |
| ws12 | 30.32 | no | no | no | yes | no | no |

## 2026-08-31 12:53:00 - the board, target side HIGH, rider cws4, cws1b 13.99

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 59.27 | no | no | no | no | yes | no |
| ws2 | 36.42 | no | no | yes | no | yes | no |
| ws3 | 16.29 | no | no | yes | no | yes | no |
| ws4 | 4.47 | no | no | no | no | yes | no |
| ws5 | 7.25 | no | no | no | yes | yes | no |
| ws6 | 35.70 | no | no | no | yes | yes | no |
| ws7 | 38.23 | no | no | no | yes | no | no |
| ws8 | 31.62 | no | no | no | yes | no | no |
| ws9 | 41.01 | no | no | yes | yes | no | no |
| ws10 | 23.74 | no | no | yes | yes | no | no |
| ws11 | 27.85 | no | no | yes | yes | no | no |
| ws12 | 30.32 | no | no | no | yes | no | no |

## 2026-08-31 20:13:00 - the board, target side LOW, rider cws12, cws1b 88.06

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 50.80 | no | no | yes | no | yes | no |
| ws2 | 55.45 | no | no | yes | no | yes | no |
| ws3 | 89.60 | no | no | yes | no | yes | no |
| ws4 | 94.19 | no | no | no | no | yes | no |
| ws5 | 83.22 | no | no | no | no | yes | no |
| ws6 | 71.79 | no | no | no | no | yes | no |
| ws7 | 57.02 | no | no | no | no | yes | no |
| ws8 | 34.80 | no | no | no | no | yes | no |
| ws9 | 22.06 | no | no | no | no | yes | no |
| ws10 | 26.38 | no | no | yes | no | yes | no |
| ws11 | 16.57 | yes | no | yes | no | yes | no |
| ws12 | 17.48 | yes | no | yes | no | yes | no |

## 2026-09-01 00:04:00 - the board, target side LOW, rider cws8, cws1b 100.29

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 54.26 | no | no | no | no | yes | no |
| ws2 | 75.06 | no | no | no | no | yes | no |
| ws3 | 43.92 | no | no | no | no | yes | no |
| ws4 | 46.67 | no | no | yes | no | yes | no |
| ws5 | 53.42 | no | no | no | no | yes | no |
| ws6 | 68.32 | no | no | no | no | yes | no |
| ws7 | 63.74 | no | no | no | no | yes | no |
| ws8 | 77.99 | no | no | yes | no | yes | no |
| ws9 | 70.93 | no | no | no | yes | yes | no |
| ws10 | 52.80 | no | no | no | yes | yes | no |
| ws11 | 64.32 | no | no | no | yes | no | no |
| ws12 | 59.12 | no | no | no | yes | no | no |

## 2026-09-01 00:10:00 - the board, target side LOW, rider cws8, cws1b 87.25

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 51.50 | no | no | yes | no | yes | no |
| ws2 | 76.40 | no | no | yes | no | yes | no |
| ws3 | 59.24 | no | no | no | no | yes | no |
| ws4 | 50.86 | no | no | no | no | yes | no |
| ws5 | 58.16 | no | no | no | no | yes | no |
| ws6 | 71.45 | no | no | no | no | yes | no |
| ws7 | 68.94 | no | no | no | no | yes | no |
| ws8 | 81.18 | no | no | no | no | yes | no |
| ws9 | 82.59 | no | no | no | yes | yes | no |
| ws10 | 59.96 | no | no | no | yes | yes | no |
| ws11 | 64.32 | no | no | no | yes | no | no |
| ws12 | 59.12 | no | no | no | yes | no | no |

## 2026-09-01 13:31:00 - the board, target side LOW, rider cws12, cws1b 86.36

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 70.74 | no | no | no | no | yes | no |
| ws2 | 63.04 | no | no | yes | no | yes | no |
| ws3 | 92.69 | no | no | no | no | yes | no |
| ws4 | 97.81 | no | no | no | no | yes | no |
| ws5 | 85.16 | no | no | no | no | yes | no |
| ws6 | 65.61 | no | no | no | no | yes | no |
| ws7 | 52.76 | no | no | no | no | yes | no |
| ws8 | 51.97 | no | no | no | no | yes | no |
| ws9 | 41.27 | no | no | no | no | yes | no |
| ws10 | 35.55 | no | no | no | no | yes | no |
| ws11 | 26.57 | no | no | no | no | yes | no |
| ws12 | 21.29 | no | no | no | no | yes | no |

## 2026-09-01 13:48:00 - the board, target side LOW, rider cws12, cws1b 94.81

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 82.67 | no | no | no | no | yes | no |
| ws2 | 45.00 | no | no | yes | no | yes | no |
| ws3 | 63.74 | no | no | yes | no | yes | no |
| ws4 | 78.50 | no | no | yes | no | yes | no |
| ws5 | 91.71 | no | no | yes | no | yes | no |
| ws6 | 91.68 | no | no | no | no | yes | no |
| ws7 | 88.67 | no | no | no | no | yes | no |
| ws8 | 77.03 | no | no | no | no | yes | no |
| ws9 | 69.84 | no | no | no | no | yes | no |
| ws10 | 49.83 | no | no | no | no | yes | no |
| ws11 | 51.21 | no | no | no | no | yes | no |
| ws12 | 49.70 | no | no | no | no | yes | no |

## 2026-09-01 15:00:00 - the board, target side HIGH, rider cws12, cws1b -18.11

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 24.94 | no | no | yes | no | yes | no |
| ws2 | 22.00 | no | no | no | no | yes | no |
| ws3 | 40.93 | no | no | no | no | yes | no |
| ws4 | 47.75 | no | no | no | no | yes | no |
| ws5 | 39.22 | no | no | yes | no | yes | no |
| ws6 | 38.56 | no | no | no | no | yes | no |
| ws7 | 38.69 | no | no | no | no | yes | no |
| ws8 | 21.50 | no | no | no | no | yes | no |
| ws9 | 52.78 | no | no | no | no | yes | no |
| ws10 | 38.91 | no | no | no | no | yes | no |
| ws11 | 71.98 | no | no | no | no | yes | no |
| ws12 | 61.36 | no | no | yes | no | yes | no |

## 2026-09-01 15:48:00 - the board, target side LOW, rider cws8, cws1b 87.22

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 74.38 | no | no | no | no | yes | no |
| ws2 | 58.52 | no | no | yes | no | yes | no |
| ws3 | 70.03 | no | no | yes | no | yes | no |
| ws4 | 88.74 | no | no | no | no | yes | no |
| ws5 | 73.90 | no | no | no | no | yes | no |
| ws6 | 63.58 | no | no | no | no | yes | no |
| ws7 | 48.35 | no | no | no | no | yes | no |
| ws8 | 39.40 | no | no | no | no | yes | no |
| ws9 | 27.82 | no | no | yes | yes | yes | no |
| ws10 | 33.54 | no | no | no | yes | yes | no |
| ws11 | 38.48 | no | no | yes | yes | no | no |
| ws12 | 37.60 | no | no | yes | yes | no | no |

## 2026-09-01 15:51:00 - the board, target side LOW, rider cws8, cws1b 86.20

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 67.00 | no | no | yes | no | yes | no |
| ws2 | 66.39 | no | no | no | no | yes | no |
| ws3 | 56.36 | no | no | yes | no | yes | no |
| ws4 | 88.74 | no | no | no | no | yes | no |
| ws5 | 80.93 | no | no | no | no | yes | no |
| ws6 | 63.58 | no | no | no | no | yes | no |
| ws7 | 48.35 | no | no | no | no | yes | no |
| ws8 | 39.40 | no | no | no | no | yes | no |
| ws9 | 27.82 | no | no | yes | yes | yes | no |
| ws10 | 33.28 | no | no | yes | yes | yes | no |
| ws11 | 38.48 | no | no | yes | yes | no | no |
| ws12 | 37.60 | no | no | yes | yes | no | no |

## 2026-09-01 17:59:00 - the board, target side HIGH, rider cws9, cws1b 11.23

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 6.65 | no | no | no | no | yes | no |
| ws2 | 5.53 | no | no | no | no | yes | no |
| ws3 | 13.54 | no | no | no | no | yes | no |
| ws4 | 14.86 | no | no | no | no | yes | no |
| ws5 | 40.35 | no | no | no | no | yes | no |
| ws6 | 58.39 | no | no | no | no | yes | no |
| ws7 | 58.58 | no | no | no | no | yes | no |
| ws8 | 60.74 | no | no | no | no | yes | no |
| ws9 | 73.45 | no | no | no | no | yes | no |
| ws10 | 56.04 | no | no | no | yes | yes | no |
| ws11 | 47.18 | no | no | yes | yes | yes | no |
| ws12 | 56.88 | no | no | yes | yes | no | no |

## 2026-09-01 18:01:00 - the board, target side HIGH, rider cws9, cws1b 14.78

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 29.98 | no | no | yes | no | yes | no |
| ws2 | 5.93 | no | no | yes | no | yes | no |
| ws3 | 15.55 | no | no | yes | no | yes | no |
| ws4 | 6.65 | no | no | no | no | yes | no |
| ws5 | 26.07 | no | no | no | no | yes | no |
| ws6 | 44.11 | no | no | no | no | yes | no |
| ws7 | 58.58 | no | no | no | no | yes | no |
| ws8 | 52.31 | no | no | no | no | yes | no |
| ws9 | 61.25 | no | no | no | no | yes | no |
| ws10 | 50.64 | no | no | no | yes | yes | no |
| ws11 | 47.18 | no | no | yes | yes | yes | no |
| ws12 | 50.70 | no | no | yes | yes | no | no |

## 2026-09-01 18:04:00 - the board, target side HIGH, rider cws9, cws1b 14.00

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 53.61 | no | no | yes | no | yes | no |
| ws2 | 6.53 | no | no | yes | no | yes | no |
| ws3 | 11.27 | no | no | no | no | yes | no |
| ws4 | 11.21 | no | no | yes | no | yes | no |
| ws5 | 26.07 | no | no | no | no | yes | no |
| ws6 | 44.11 | no | no | no | no | yes | no |
| ws7 | 58.58 | no | no | no | no | yes | no |
| ws8 | 52.31 | no | no | no | no | yes | no |
| ws9 | 61.25 | no | no | no | no | yes | no |
| ws10 | 50.64 | no | no | no | yes | yes | no |
| ws11 | 47.18 | no | no | no | yes | yes | no |
| ws12 | 50.70 | no | no | yes | yes | no | no |

## 2026-09-01 18:08:00 - the board, target side HIGH, rider cws9, cws1b 5.82

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 53.46 | no | no | yes | no | yes | no |
| ws2 | 24.55 | no | no | yes | no | yes | no |
| ws3 | 13.84 | no | no | yes | no | yes | no |
| ws4 | 7.52 | no | no | yes | no | yes | no |
| ws5 | 11.78 | no | no | no | no | yes | no |
| ws6 | 29.82 | no | no | no | no | yes | no |
| ws7 | 44.29 | no | no | no | no | yes | no |
| ws8 | 38.02 | no | no | no | no | yes | no |
| ws9 | 61.25 | no | no | no | no | yes | no |
| ws10 | 50.64 | no | no | no | yes | yes | no |
| ws11 | 47.18 | no | no | no | yes | yes | no |
| ws12 | 50.70 | no | no | yes | yes | no | no |

## 2026-09-01 18:13:00 - the board, target side HIGH, rider cws9, cws1b 13.07

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 29.40 | no | no | yes | no | yes | no |
| ws2 | 30.58 | no | no | yes | no | yes | no |
| ws3 | 20.55 | no | no | yes | no | yes | no |
| ws4 | 6.79 | no | no | yes | no | yes | no |
| ws5 | 9.65 | no | no | no | no | yes | no |
| ws6 | 16.78 | no | no | no | no | yes | no |
| ws7 | 30.00 | no | no | no | no | yes | no |
| ws8 | 38.02 | no | no | no | no | yes | no |
| ws9 | 47.45 | no | no | no | no | yes | no |
| ws10 | 45.00 | no | no | no | yes | yes | no |
| ws11 | 41.01 | no | no | no | yes | yes | no |
| ws12 | 45.59 | no | no | no | yes | no | no |

## 2026-09-01 18:15:00 - the board, target side HIGH, rider cws9, cws1b 0.48

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 23.64 | no | no | no | no | yes | no |
| ws2 | 27.63 | no | no | yes | no | yes | no |
| ws3 | 20.55 | no | no | yes | no | yes | no |
| ws4 | 6.79 | no | no | yes | no | yes | no |
| ws5 | 1.09 | no | no | no | no | yes | no |
| ws6 | 16.78 | no | no | no | no | yes | no |
| ws7 | 30.00 | no | no | no | no | yes | no |
| ws8 | 38.02 | no | no | no | no | yes | no |
| ws9 | 47.45 | no | no | no | no | yes | no |
| ws10 | 45.00 | no | no | no | yes | yes | no |
| ws11 | 41.01 | no | no | no | yes | yes | no |
| ws12 | 45.59 | no | no | no | yes | no | no |

## 2026-09-01 18:36:00 - the board, target side HIGH, rider cws9, cws1b -6.75

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 50.85 | no | no | yes | no | yes | no |
| ws2 | 41.78 | no | no | yes | no | yes | no |
| ws3 | 27.47 | no | no | yes | no | yes | no |
| ws4 | 0.00 | no | no | no | no | yes | no |
| ws5 | 0.98 | no | no | no | no | yes | no |
| ws6 | 0.00 | no | no | no | no | yes | no |
| ws7 | 0.00 | no | no | no | no | yes | no |
| ws8 | 4.40 | no | no | no | no | yes | no |
| ws9 | 6.41 | no | no | no | no | yes | no |
| ws10 | 16.43 | no | no | no | yes | yes | no |
| ws11 | 22.37 | no | no | no | yes | yes | no |
| ws12 | 26.10 | no | no | no | yes | no | no |

## 2026-09-01 18:42:00 - the board, target side HIGH, rider cws9, cws1b 12.26

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 44.77 | no | no | yes | no | yes | no |
| ws2 | 53.62 | no | no | yes | no | yes | no |
| ws3 | 52.89 | no | no | yes | no | yes | no |
| ws4 | 14.29 | no | no | yes | no | yes | no |
| ws5 | 6.74 | no | no | yes | no | yes | no |
| ws6 | 0.00 | no | no | no | no | yes | no |
| ws7 | 9.48 | no | no | yes | no | yes | no |
| ws8 | 10.25 | no | no | yes | no | yes | no |
| ws9 | 6.41 | no | no | no | no | yes | no |
| ws10 | 16.67 | no | no | yes | yes | yes | no |
| ws11 | 14.59 | no | no | no | yes | yes | no |
| ws12 | 26.10 | no | no | no | yes | no | no |

## 2026-09-02 04:09:00 - the board, target side HIGH, rider cws12, cws1b 9.50

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 7.26 | no | no | no | no | yes | no |
| ws2 | 44.20 | no | no | no | no | yes | no |
| ws3 | 38.35 | no | no | yes | no | yes | no |
| ws4 | 22.29 | no | no | yes | no | yes | no |
| ws5 | 15.28 | no | no | no | no | yes | no |
| ws6 | 6.07 | no | no | no | no | yes | no |
| ws7 | 25.46 | no | no | no | no | yes | no |
| ws8 | 24.80 | no | no | no | no | yes | no |
| ws9 | 43.07 | no | no | no | no | yes | no |
| ws10 | 61.29 | no | no | no | no | yes | no |
| ws11 | 63.64 | no | no | no | no | yes | no |
| ws12 | 78.58 | no | no | no | no | yes | no |

## 2026-09-02 04:16:00 - the board, target side HIGH, rider cws12, cws1b -2.52

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 20.79 | no | no | yes | no | yes | no |
| ws2 | 6.42 | no | no | no | no | yes | no |
| ws3 | 27.64 | no | no | no | no | yes | no |
| ws4 | 17.62 | no | no | no | no | yes | no |
| ws5 | 12.43 | no | no | yes | no | yes | no |
| ws6 | 6.07 | no | no | no | no | yes | no |
| ws7 | 11.17 | no | no | no | no | yes | no |
| ws8 | 10.51 | no | no | no | no | yes | no |
| ws9 | 28.78 | no | no | no | no | yes | no |
| ws10 | 47.01 | no | no | no | no | yes | no |
| ws11 | 49.36 | no | no | no | no | yes | no |
| ws12 | 64.30 | no | no | no | no | yes | no |

## 2026-09-02 04:22:00 - the board, target side HIGH, rider cws12, cws1b 12.53

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 72.20 | no | no | yes | no | yes | no |
| ws2 | 45.97 | no | no | yes | no | yes | no |
| ws3 | 20.20 | no | no | no | no | yes | no |
| ws4 | 14.88 | no | no | no | no | yes | no |
| ws5 | 11.60 | no | no | yes | no | yes | no |
| ws6 | 7.72 | no | no | yes | no | yes | no |
| ws7 | 12.17 | no | no | yes | no | yes | no |
| ws8 | 10.51 | no | no | no | no | yes | no |
| ws9 | 14.50 | no | no | no | no | yes | no |
| ws10 | 33.82 | no | no | no | no | yes | no |
| ws11 | 49.36 | no | no | no | no | yes | no |
| ws12 | 64.30 | no | no | no | no | yes | no |

## 2026-09-02 06:03:00 - the board, target side HIGH, rider cws5, cws1b 1.56

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 19.92 | no | no | yes | no | yes | no |
| ws2 | 38.26 | no | no | no | no | yes | no |
| ws3 | 29.42 | no | no | no | no | yes | no |
| ws4 | 62.20 | no | no | no | no | yes | no |
| ws5 | 53.67 | no | no | no | no | yes | no |
| ws6 | 60.60 | no | no | no | yes | yes | no |
| ws7 | 74.55 | no | no | yes | yes | yes | no |
| ws8 | 73.12 | no | no | yes | yes | no | no |
| ws9 | 83.27 | yes | no | yes | yes | no | no |
| ws10 | 66.68 | no | no | yes | yes | no | no |
| ws11 | 62.72 | no | no | yes | yes | no | no |
| ws12 | 51.27 | no | no | yes | yes | no | no |

## 2026-09-02 06:13:00 - the board, target side HIGH, rider cws5, cws1b 8.86

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 79.65 | no | no | yes | no | yes | no |
| ws2 | 22.46 | no | no | yes | no | yes | no |
| ws3 | 8.75 | no | no | no | no | yes | no |
| ws4 | 37.04 | no | no | no | no | yes | no |
| ws5 | 36.12 | no | no | no | no | yes | no |
| ws6 | 43.88 | no | no | no | yes | yes | no |
| ws7 | 48.98 | no | no | no | yes | yes | no |
| ws8 | 61.52 | no | no | no | yes | no | no |
| ws9 | 73.56 | no | no | yes | yes | no | no |
| ws10 | 70.12 | no | no | yes | yes | no | no |
| ws11 | 62.72 | no | no | yes | yes | no | no |
| ws12 | 51.03 | no | no | yes | yes | no | no |

## 2026-09-02 06:30:00 - the board, target side HIGH, rider cws5, cws1b 9.57

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 41.73 | no | no | no | no | yes | no |
| ws2 | 52.74 | no | no | no | no | yes | no |
| ws3 | 60.82 | no | no | yes | no | yes | no |
| ws4 | 27.78 | no | no | yes | no | yes | no |
| ws5 | 21.40 | no | no | yes | no | yes | no |
| ws6 | 6.25 | no | no | no | yes | yes | no |
| ws7 | 29.65 | no | no | no | yes | yes | no |
| ws8 | 38.28 | no | no | no | yes | no | no |
| ws9 | 58.06 | no | no | no | yes | no | no |
| ws10 | 54.10 | no | no | no | yes | no | no |
| ws11 | 59.82 | no | no | yes | yes | no | no |
| ws12 | 51.03 | no | no | no | yes | no | no |

## 2026-09-02 10:41:00 - the board, target side HIGH, rider cws3, cws1b -7.22

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 39.59 | no | no | yes | no | yes | no |
| ws2 | 4.15 | no | no | no | no | yes | no |
| ws3 | 44.28 | no | no | no | no | yes | no |
| ws4 | 53.63 | no | no | no | yes | yes | no |
| ws5 | 57.56 | no | no | no | yes | yes | no |
| ws6 | 65.83 | no | no | yes | yes | no | no |
| ws7 | 66.12 | no | no | yes | yes | no | no |
| ws8 | 64.05 | no | no | no | yes | no | no |
| ws9 | 70.88 | no | no | yes | yes | no | no |
| ws10 | 54.04 | no | no | yes | yes | no | no |
| ws11 | 42.34 | no | no | yes | yes | no | no |
| ws12 | 56.92 | no | no | yes | yes | no | no |

## 2026-09-02 14:30:00 - the board, target side HIGH, rider cws8, cws1b 4.48

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 31.19 | no | no | yes | no | yes | no |
| ws2 | 33.12 | no | no | yes | no | yes | no |
| ws3 | 17.92 | no | no | yes | no | yes | no |
| ws4 | 19.09 | no | no | no | no | yes | no |
| ws5 | 24.83 | no | no | no | no | yes | no |
| ws6 | 40.37 | no | no | no | no | yes | no |
| ws7 | 57.95 | no | no | no | no | yes | no |
| ws8 | 71.63 | no | no | no | no | yes | no |
| ws9 | 70.55 | no | no | yes | yes | yes | no |
| ws10 | 68.65 | no | no | yes | yes | yes | no |
| ws11 | 49.65 | no | no | yes | yes | no | no |
| ws12 | 65.98 | no | no | yes | yes | no | no |

## 2026-09-02 14:32:00 - the board, target side HIGH, rider cws8, cws1b 13.99

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 45.57 | no | no | yes | no | yes | no |
| ws2 | 27.44 | no | no | no | no | yes | no |
| ws3 | 17.92 | no | no | yes | no | yes | no |
| ws4 | 8.47 | no | no | no | no | yes | no |
| ws5 | 24.83 | no | no | no | no | yes | no |
| ws6 | 40.37 | no | no | no | no | yes | no |
| ws7 | 57.95 | no | no | no | no | yes | no |
| ws8 | 61.67 | no | no | no | no | yes | no |
| ws9 | 70.55 | no | no | yes | yes | yes | no |
| ws10 | 68.65 | no | no | yes | yes | yes | no |
| ws11 | 49.65 | no | no | yes | yes | no | no |
| ws12 | 65.98 | no | no | yes | yes | no | no |

## 2026-09-02 14:53:05 - the board, target side HIGH, rider cws8, cws1b 14.93

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 0.65 | no | no | no | no | yes | no |
| ws2 | 44.27 | no | no | no | no | yes | no |
| ws3 | 50.07 | no | no | no | no | yes | no |
| ws4 | 35.96 | no | no | yes | no | yes | no |
| ws5 | 29.43 | no | no | yes | no | yes | no |
| ws6 | 16.79 | no | no | no | no | yes | no |
| ws7 | 36.62 | no | no | no | no | yes | no |
| ws8 | 43.83 | no | no | no | no | yes | no |
| ws9 | 55.18 | no | no | no | yes | yes | no |
| ws10 | 54.78 | no | no | no | yes | yes | no |
| ws11 | 28.19 | no | no | no | yes | no | no |
| ws12 | 58.38 | no | no | no | yes | no | no |

## 2026-09-02 14:58:00 - the board, target side HIGH, rider cws8, cws1b 10.05

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 47.41 | no | no | yes | no | yes | no |
| ws2 | 15.92 | no | no | no | no | yes | no |
| ws3 | 40.47 | no | no | no | no | yes | no |
| ws4 | 35.96 | no | no | yes | no | yes | no |
| ws5 | 29.43 | no | no | yes | no | yes | no |
| ws6 | 12.36 | no | no | no | no | yes | no |
| ws7 | 27.96 | no | no | no | no | yes | no |
| ws8 | 32.49 | no | no | no | no | yes | no |
| ws9 | 55.18 | no | no | no | yes | yes | no |
| ws10 | 54.78 | no | no | no | yes | yes | no |
| ws11 | 28.19 | no | no | no | yes | no | no |
| ws12 | 58.38 | no | no | no | yes | no | no |

## 2026-09-02 15:07:00 - the board, target side HIGH, rider cws8, cws1b 6.50

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 62.90 | no | no | yes | no | yes | no |
| ws2 | 40.26 | no | no | yes | no | yes | no |
| ws3 | 14.61 | no | no | no | no | yes | no |
| ws4 | 37.25 | no | no | yes | no | yes | no |
| ws5 | 30.49 | no | no | yes | no | yes | no |
| ws6 | 19.51 | no | no | yes | no | yes | no |
| ws7 | 19.08 | no | no | no | no | yes | no |
| ws8 | 20.84 | no | no | no | no | yes | no |
| ws9 | 41.35 | no | no | no | yes | yes | no |
| ws10 | 40.49 | no | no | no | yes | yes | no |
| ws11 | 22.63 | no | no | no | yes | no | no |
| ws12 | 44.09 | no | no | no | yes | no | no |

## 2026-09-02 19:25:00 - the board, target side HIGH, rider cws5, cws1b 1.05

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 23.91 | no | no | yes | no | yes | no |
| ws2 | 14.29 | no | no | no | no | yes | no |
| ws3 | 22.97 | no | no | no | no | yes | no |
| ws4 | 49.08 | no | no | no | no | yes | no |
| ws5 | 46.89 | no | no | no | no | yes | no |
| ws6 | 67.12 | no | no | yes | yes | yes | no |
| ws7 | 67.34 | no | no | yes | yes | yes | no |
| ws8 | 54.18 | no | no | yes | yes | no | no |
| ws9 | 43.86 | no | no | yes | yes | no | no |
| ws10 | 46.82 | no | no | no | yes | no | no |
| ws11 | 40.15 | no | no | no | yes | no | no |
| ws12 | 39.22 | no | no | no | yes | no | no |

## 2026-09-02 23:04:00 - the board, target side LOW, rider cws9, cws1b 89.81

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 82.48 | no | no | no | no | yes | no |
| ws2 | 49.08 | no | no | no | no | yes | no |
| ws3 | 33.23 | no | no | yes | no | yes | no |
| ws4 | 59.74 | no | no | yes | no | yes | no |
| ws5 | 68.03 | no | no | no | no | yes | no |
| ws6 | 57.91 | no | no | no | no | yes | no |
| ws7 | 53.22 | no | no | no | no | yes | no |
| ws8 | 52.36 | no | no | no | no | yes | no |
| ws9 | 31.02 | no | no | no | no | yes | no |
| ws10 | 43.42 | no | no | yes | yes | yes | no |
| ws11 | 43.42 | no | no | no | yes | yes | no |
| ws12 | 48.14 | no | no | no | yes | no | no |

## 2026-09-02 23:06:00 - the board, target side LOW, rider cws9, cws1b 95.93

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 81.77 | no | no | yes | no | yes | no |
| ws2 | 63.36 | no | no | no | no | yes | no |
| ws3 | 36.82 | no | no | yes | no | yes | no |
| ws4 | 59.74 | no | no | yes | no | yes | no |
| ws5 | 73.54 | no | no | no | no | yes | no |
| ws6 | 72.19 | no | no | no | no | yes | no |
| ws7 | 65.05 | no | no | no | no | yes | no |
| ws8 | 52.36 | no | no | no | no | yes | no |
| ws9 | 45.30 | no | no | no | no | yes | no |
| ws10 | 43.42 | no | no | yes | yes | yes | no |
| ws11 | 51.92 | no | no | no | yes | yes | no |
| ws12 | 48.14 | no | no | no | yes | no | no |

## 2026-09-02 23:27:00 - the board, target side LOW, rider cws9, cws1b 86.17

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 76.56 | no | no | no | no | yes | no |
| ws2 | 38.84 | no | no | yes | no | yes | no |
| ws3 | 63.56 | no | no | yes | no | yes | no |
| ws4 | 77.41 | no | no | no | no | yes | no |
| ws5 | 76.88 | no | no | no | no | yes | no |
| ws6 | 73.83 | no | no | yes | no | yes | no |
| ws7 | 68.43 | no | no | yes | no | yes | no |
| ws8 | 74.69 | no | no | no | no | yes | no |
| ws9 | 64.47 | no | no | no | no | yes | no |
| ws10 | 65.04 | no | no | no | yes | yes | no |
| ws11 | 66.20 | no | no | no | yes | yes | no |
| ws12 | 58.97 | no | no | no | yes | no | no |

## 2026-09-03 00:33:00 - the board, target side HIGH, rider cws12, cws1b 10.64

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 30.71 | no | no | yes | no | yes | no |
| ws2 | 4.11 | no | no | no | no | yes | no |
| ws3 | 9.04 | no | no | yes | no | yes | no |
| ws4 | 6.35 | no | no | no | no | yes | no |
| ws5 | 24.27 | no | no | no | no | yes | no |
| ws6 | 39.63 | no | no | no | no | yes | no |
| ws7 | 48.41 | no | no | no | no | yes | no |
| ws8 | 44.90 | no | no | no | no | yes | no |
| ws9 | 50.47 | no | no | no | no | yes | no |
| ws10 | 53.32 | no | no | no | no | yes | no |
| ws11 | 48.98 | no | no | no | no | yes | no |
| ws12 | 62.51 | no | no | no | no | yes | no |

## 2026-09-03 04:10:00 - the board, target side LOW, rider cws8, cws1b 93.91

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 54.89 | no | no | no | no | yes | no |
| ws2 | 31.94 | no | no | yes | no | yes | no |
| ws3 | 65.25 | no | no | yes | no | yes | no |
| ws4 | 68.25 | no | no | no | no | yes | no |
| ws5 | 52.30 | no | no | no | no | yes | no |
| ws6 | 57.39 | no | no | no | no | yes | no |
| ws7 | 42.05 | no | no | no | no | yes | no |
| ws8 | 25.20 | no | no | yes | no | yes | no |
| ws9 | 26.66 | no | no | yes | yes | yes | no |
| ws10 | 18.59 | yes | no | yes | yes | yes | yes |
| ws11 | 26.17 | no | no | yes | yes | no | no |
| ws12 | 31.49 | no | no | yes | yes | no | no |

## 2026-09-03 05:26:00 - the board, target side HIGH, rider cws5, cws1b 14.67

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 28.65 | no | no | yes | no | yes | no |
| ws2 | 3.23 | no | no | no | no | yes | no |
| ws3 | 1.10 | no | no | no | no | yes | no |
| ws4 | 28.77 | no | no | no | no | yes | no |
| ws5 | 39.45 | no | no | no | no | yes | no |
| ws6 | 53.39 | no | no | no | yes | yes | no |
| ws7 | 55.25 | no | no | yes | yes | yes | no |
| ws8 | 55.16 | no | no | no | yes | no | no |
| ws9 | 49.73 | no | no | yes | yes | no | no |
| ws10 | 48.00 | no | no | yes | yes | no | no |
| ws11 | 49.70 | no | no | yes | yes | no | no |
| ws12 | 47.67 | no | no | yes | yes | no | no |

## 2026-09-03 08:06:00 - the board, target side LOW, rider cws7, cws1b 93.31

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 87.89 | no | no | yes | no | yes | no |
| ws2 | 76.57 | no | no | no | no | yes | no |
| ws3 | 39.71 | no | no | yes | no | yes | no |
| ws4 | 59.03 | no | no | no | no | yes | no |
| ws5 | 49.14 | no | no | no | no | yes | no |
| ws6 | 41.19 | no | no | no | no | yes | no |
| ws7 | 29.78 | no | no | no | no | yes | no |
| ws8 | 41.95 | no | no | no | yes | yes | no |
| ws9 | 41.54 | no | no | yes | yes | yes | no |
| ws10 | 43.25 | no | no | yes | yes | no | no |
| ws11 | 35.04 | no | no | yes | yes | no | no |
| ws12 | 36.35 | no | no | yes | yes | no | no |

## 2026-09-03 21:20:00 - the board, target side LOW, rider cws12, cws1b 102.58

| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider | inside lin_hop | a candidate |
|---|---|---|---|---|---|---|---|
| ws1 | 40.31 | no | no | yes | no | yes | no |
| ws2 | 82.98 | no | no | no | no | yes | no |
| ws3 | 63.09 | no | no | no | no | yes | no |
| ws4 | 67.50 | no | no | yes | no | yes | no |
| ws5 | 71.44 | no | no | yes | no | yes | no |
| ws6 | 58.43 | no | no | no | no | yes | no |
| ws7 | 39.43 | no | no | no | no | yes | no |
| ws8 | 55.74 | no | no | no | no | yes | no |
| ws9 | 50.93 | no | no | no | no | yes | no |
| ws10 | 29.60 | no | no | no | no | yes | no |
| ws11 | 30.12 | no | no | no | no | yes | no |
| ws12 | 16.14 | yes | no | no | no | yes | no |
