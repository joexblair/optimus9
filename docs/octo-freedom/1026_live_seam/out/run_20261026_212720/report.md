# live_seam - read A against read B on the live tape, 2026-10-26 21:27:25 to 2026-10-27 01:27:20

## The run

| item | value |
|---|---|
| live bars | 2880 |
| first live bar | 2026-10-26 21:27:25 |
| last live bar | 2026-10-27 01:27:20 |
| seeded bars before it | 74880, 2026-10-22 13:27:25 to 2026-10-26 21:27:20 |
| window | lookback 24 h + warmup 80 h, o9-live's |
| filler_invisible | True |
| bars read after close, ms: min / median / max | 5301 / 5302 / 5314 |
| compute per bar, ms: min / median / max | 343 / 449 / 1211 |
| bars with a compute error | 0 |
| missing bars on the tape | 0 |

- pairing rule: An A firing pairs with the first B firing of the same event, lines and side that comes after it and before the next A firing of that same event, lines and side. Otherwise it is "A only"; a B firing no A firing claims is "B only". (Mine, accepted by ac06c2 #6.)
- #3 and #4: the firing bar is the RAW cross bar. Joe 1026: *"take a wob, or the raw cross bar - capture both"*.
- dwell s = consecutive 5 s bars the state holds from the firing bar, x 5, on the series the firing came from.
- survives to bucket close = the state at that TF's next bucket close, the bar at next seam - 5 s.
  On the B series this is "yes" by construction: B is constant inside a bucket.
- wob 12 = held >= 12 bars = 60 s. Joe's named value, *"spitballing only"*. It gates nothing.
- #1 carries the same three columns; its state is ib. #2 carries none: a pass reads two lines and two
  conditions, so which state a dwell would measure is not defined. #2 stays on the raw pass bar.

## Read B, live against the replay

The replay is one window ending 2026-10-27 01:27:20, emerging lines, `v4_closed_prev.series`. Tolerance 2.0e-07 is ac06c2's (#6). The max |diff| is reported pass or fail.

| line | bars compared | exactly equal | max abs diff | above 2.0e-07 | NaN mismatch | verdict |
|---|---|---|---|---|---|---|
| ws1b | 2880 | 1776 | 1.1e-08 | 0 | 0 | PASS |
| ws1r | 2880 | 1493 | 2.8e-14 | 0 | 0 | PASS |
| ws2r | 2880 | 1704 | 2.8e-14 | 0 | 0 | PASS |
| ws3r | 2880 | 1481 | 2.1e-14 | 0 | 0 | PASS |
| ws4r | 2880 | 2736 | 1.4e-14 | 0 | 0 | PASS |
| ws5r | 2880 | 1860 | 1.4e-14 | 0 | 0 | PASS |
| ws6r | 2880 | 1841 | 1.4e-14 | 0 | 0 | PASS |
| ws7r | 2880 | 2040 | 2.8e-14 | 0 | 0 | PASS |
| ws8r | 2880 | 2304 | 1.4e-14 | 0 | 0 | PASS |
| ws9r | 2880 | 2448 | 2.8e-14 | 0 | 0 | PASS |
| ws10r | 2880 | 2760 | 7.1e-15 | 0 | 0 | PASS |
| ws11r | 2880 | 1452 | 1.4e-14 | 0 | 0 | PASS |
| ws12r | 2880 | 2160 | 1.4e-14 | 0 | 0 | PASS |
| ws5Mage | 2880 | 1289 | 1.6e-09 | 0 | 0 | PASS |
| ws6Mage | 2880 | 1368 | 1.8e-09 | 0 | 0 | PASS |
| ws7Mage | 2880 | 1133 | 1.0e-09 | 0 | 0 | PASS |
| ws8Mage | 2880 | 1632 | 9.0e-10 | 0 | 0 | PASS |
| ws9Mage | 2880 | 1620 | 6.2e-10 | 0 | 0 | PASS |
| ws10Mage | 2880 | 1529 | 4.7e-10 | 0 | 0 | PASS |
| ws11Mage | 2880 | 1435 | 4.9e-10 | 0 | 0 | PASS |
| ws12Mage | 2880 | 1440 | 3.4e-10 | 0 | 0 | PASS |

### bars whose OHLCV changed on the tape after the live read: 0

## The firings, one row per pair, chronological

| event | pairs | both | A only | B only |
|---|---|---|---|---|
| #1 ws1b oob -> ib | 30 | 11 | 19 | 0 |
| #2 baton pass | 134 | 23 | 102 | 9 |
| #3 Mage into oob | 76 | 14 | 62 | 0 |
| #4 r into oob | 76 | 17 | 59 | 0 |

| event | lines | side | fired under | A bar | B bar | gap s | read A at A bar | read B at A bar | A dwell s | A survives close | A wob 12 | B dwell s | B survives close | B wob 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| #3 Mage into oob | ws5Mage | LOW | A only | 2026-10-26 21:27:40 | - | - | ws5Mage 12.98 | ws5Mage 9.86 | 25 | no | no | - | - | - |
| #2 baton pass (oob -> ib) | ws8r -> ws9r | LOW | A only | 2026-10-26 21:28:15 | - | - | ws8r 16.03; ws9r 18.72 | ws8r 10.40; ws9r 17.08 | - | - | - | - | - | - |
| #1 ws1b oob -> ib | ws1b | HIGH | A only | 2026-10-26 21:34:55 | - | - | ws1b 84.52 | ws1b 63.82 | 5 | yes | no | - | - | - |
| #1 ws1b oob -> ib | ws1b | HIGH | both | 2026-10-26 21:41:00 | 2026-10-26 21:42:00 | 60 | ws1b 84.65 | ws1b 86.60 | 105 | yes | yes | 60 | yes | yes |
| #2 baton pass (oob -> ib + ex-fence -> in-fence) | ws1r -> ws2r | HIGH | both | 2026-10-26 21:41:00 | 2026-10-26 21:42:00 | 60 | ws1r 71.43; ws2r 91.37 | ws1r 85.71; ws2r 95.37 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws3r -> ws4r | HIGH | A only | 2026-10-26 21:41:35 | - | - | ws3r 84.16; ws4r 85.69 | ws3r 89.67; ws4r 75.82 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib + ex-fence -> in-fence) | ws2r -> ws3r | HIGH | both | 2026-10-26 21:42:00 | 2026-10-26 21:44:00 | 120 | ws2r 75.39; ws3r 82.68 | ws2r 89.67; ws3r 84.16 | - | - | - | - | - | - |
| #1 ws1b oob -> ib | ws1b | HIGH | both | 2026-10-26 21:43:00 | 2026-10-26 21:44:00 | 60 | ws1b 84.84 | ws1b 85.18 | 115 | yes | yes | 60 | yes | yes |
| #1 ws1b oob -> ib | ws1b | HIGH | both | 2026-10-26 21:45:00 | 2026-10-26 21:46:00 | 60 | ws1b 83.75 | ws1b 87.57 | 110 | yes | yes | 60 | yes | yes |
| #4 r into oob | ws5r | HIGH | both | 2026-10-26 21:45:00 | 2026-10-26 21:50:00 | 300 | ws5r 86.69 | ws5r 74.91 | 480 | yes | yes | 600 | yes | yes |
| #2 baton pass (oob -> ib) | ws3r -> ws4r | HIGH | A only | 2026-10-26 21:45:25 | - | - | ws3r 84.82; ws4r 82.73 | ws3r 85.29; ws4r 86.70 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws3r -> ws4r | HIGH | A only | 2026-10-26 21:45:40 | - | - | ws3r 84.41; ws4r 82.33 | ws3r 85.29; ws4r 86.70 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws4r -> ws5r | HIGH | A only | 2026-10-26 21:47:00 | - | - | ws4r 84.95; ws5r 88.17 | ws4r 86.70; ws5r 74.91 | - | - | - | - | - | - |
| #3 Mage into oob | ws5Mage | HIGH | both | 2026-10-26 21:47:05 | 2026-10-26 21:50:00 | 175 | ws5Mage 95.35 | ws5Mage 75.73 | 295 | yes | yes | 300 | yes | yes |
| #4 r into oob | ws6r | HIGH | A only | 2026-10-26 21:48:00 | - | - | ws6r 86.26 | ws6r 80.73 | 245 | no | yes | - | - | - |
| #2 baton pass (oob -> ib) | ws3r -> ws4r | HIGH | A only | 2026-10-26 21:48:40 | - | - | ws3r 84.10; ws4r 86.72 | ws3r 90.67; ws4r 86.44 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws3r -> ws4r | HIGH | A only | 2026-10-26 21:49:20 | - | - | ws3r 83.76; ws4r 86.55 | ws3r 90.67; ws4r 86.44 | - | - | - | - | - | - |
| #1 ws1b oob -> ib | ws1b | HIGH | A only | 2026-10-26 21:51:00 | - | - | ws1b 83.65 | ws1b 86.79 | 10 | yes | no | - | - | - |
| #2 baton pass (oob -> ib + ex-fence -> in-fence) | ws3r -> ws4r | HIGH | A only | 2026-10-26 21:51:00 | - | - | ws3r 78.29; ws4r 86.89 | ws3r 85.87; ws4r 86.44 | - | - | - | - | - | - |
| #1 ws1b oob -> ib | ws1b | HIGH | A only | 2026-10-26 21:51:15 | - | - | ws1b 84.77 | ws1b 86.79 | 35 | yes | no | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws3r -> ws4r | HIGH | A only | 2026-10-26 21:51:15 | - | - | ws3r 79.81; ws4r 87.42 | ws3r 85.87; ws4r 86.44 | - | - | - | - | - | - |
| #1 ws1b oob -> ib | ws1b | HIGH | both | 2026-10-26 21:51:55 | 2026-10-26 21:52:00 | 5 | ws1b 84.02 | ws1b 86.79 | 2315 | yes | yes | 2340 | yes | yes |
| #2 baton pass (ex-fence -> in-fence) | ws3r -> ws4r | HIGH | both | 2026-10-26 21:51:55 | 2026-10-26 21:54:00 | 125 | ws3r 78.79; ws4r 87.07 | ws3r 85.87; ws4r 86.44 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws4r -> ws5r | HIGH | A only | 2026-10-26 21:52:15 | - | - | ws4r 84.96; ws5r 87.24 | ws4r 87.07; ws5r 88.84 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws4r -> ws5r | HIGH | A only | 2026-10-26 21:52:35 | - | - | ws4r 84.96; ws5r 87.24 | ws4r 87.07; ws5r 88.84 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws4r -> ws5r | HIGH | A only | 2026-10-26 21:52:50 | - | - | ws4r 83.65; ws5r 85.90 | ws4r 87.07; ws5r 88.84 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws5r -> ws6r | HIGH | A only | 2026-10-26 21:53:00 | - | - | ws5r 83.90; ws6r 82.17 | ws5r 88.84; ws6r 80.73 | - | - | - | - | - | - |
| #4 r into oob | ws5r | HIGH | A only | 2026-10-26 21:53:10 | - | - | ws5r 90.05 | ws5r 88.84 | 30 | yes | no | - | - | - |
| #3 Mage into oob | ws5Mage | HIGH | A only | 2026-10-26 21:53:10 | - | - | ws5Mage 85.55 | ws5Mage 89.09 | 5 | no | no | - | - | - |
| #4 r into oob | ws6r | HIGH | A only | 2026-10-26 21:53:10 | - | - | ws6r 85.75 | ws6r 80.73 | 5 | no | no | - | - | - |
| #2 baton pass (oob -> ib) | ws4r -> ws5r | HIGH | both | 2026-10-26 21:53:20 | 2026-10-26 21:56:00 | 160 | ws4r 84.29; ws5r 86.55 | ws4r 87.07; ws5r 88.84 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws5r -> ws6r | HIGH | A only | 2026-10-26 21:53:40 | - | - | ws5r 84.99; ws6r 82.84 | ws5r 88.84; ws6r 80.73 | - | - | - | - | - | - |
| #4 r into oob | ws5r | HIGH | A only | 2026-10-26 21:54:05 | - | - | ws5r 85.14 | ws5r 88.84 | 85 | yes | yes | - | - | - |
| #4 r into oob | ws6r | HIGH | both | 2026-10-26 21:54:05 | 2026-10-26 22:00:00 | 355 | ws6r 90.73 | ws6r 82.84 | 355 | yes | yes | 360 | yes | yes |
| #2 baton pass (oob -> ib) | ws5r -> ws6r | HIGH | both | 2026-10-26 21:55:30 | 2026-10-26 22:00:00 | 270 | ws5r 84.28; ws6r 89.54 | ws5r 85.14; ws6r 82.84 | - | - | - | - | - | - |
| #4 r into oob | ws7r | HIGH | A only | 2026-10-26 21:56:30 | - | - | ws7r 85.36 | ws7r 75.94 | 55 | yes | no | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws4r -> ws5r | HIGH | both | 2026-10-26 21:56:30 | 2026-10-26 22:00:00 | 210 | ws4r 67.04; ws5r 84.14 | ws4r 81.32; ws5r 85.14 | - | - | - | - | - | - |
| #4 r into oob | ws7r | HIGH | A only | 2026-10-26 21:57:40 | - | - | ws7r 85.47 | ws7r 75.94 | 25 | yes | no | - | - | - |
| #4 r into oob | ws7r | HIGH | A only | 2026-10-26 21:59:15 | - | - | ws7r 85.47 | ws7r 75.94 | 20 | yes | no | - | - | - |
| #2 baton pass (oob -> ib + ex-fence -> in-fence) | ws6r -> ws7r | HIGH | both | 2026-10-26 22:00:00 | 2026-10-26 22:06:00 | 360 | ws6r 79.70; ws7r 84.95 | ws6r 89.00; ws7r 75.94 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws1r -> ws2r | LOW | A only | 2026-10-26 22:01:05 | - | - | ws1r 17.36; ws2r 7.82 | ws1r 3.60; ws2r 16.68 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws1r -> ws2r | LOW | both | 2026-10-26 22:02:00 | 2026-10-26 22:03:00 | 60 | ws1r 31.64; ws2r 4.74 | ws1r 17.36; ws2r 7.82 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws1r -> ws2r | LOW | B only | - | 2026-10-26 22:02:00 | - | - | - | - | - | - | - | - | - |
| #4 r into oob | ws7r | HIGH | both | 2026-10-26 22:02:15 | 2026-10-26 22:03:00 | 45 | ws7r 86.27 | ws7r 75.94 | 50 | yes | no | 420 | yes | yes |
| #2 baton pass (ex-fence -> in-fence) | ws5r -> ws6r | HIGH | B only | - | 2026-10-26 22:05:00 | - | - | - | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws2r -> ws3r | LOW | A only | 2026-10-26 22:06:00 | - | - | ws2r 20.37; ws3r 18.04 | ws2r 15.89; ws3r 30.85 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws2r -> ws3r | LOW | A only | 2026-10-26 22:08:05 | - | - | ws2r 20.11; ws3r 17.05 | ws2r 16.55; ws3r 30.85 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws2r -> ws3r | LOW | A only | 2026-10-26 22:10:00 | - | - | ws2r 20.57; ws3r 8.84 | ws2r 17.83; ws3r 18.33 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws2r -> ws3r | LOW | A only | 2026-10-26 22:12:05 | - | - | ws2r 21.32; ws3r 12.19 | ws2r 17.83; ws3r 8.84 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws2r -> ws3r | LOW | A only | 2026-10-26 22:12:35 | - | - | ws2r 20.41; ws3r 11.29 | ws2r 17.83; ws3r 8.84 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws1r -> ws2r | LOW | A only | 2026-10-26 22:15:30 | - | - | ws1r 20.43; ws2r 17.83 | ws1r 23.75; ws2r 17.83 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws2r -> ws3r | LOW | both | 2026-10-26 22:15:50 | 2026-10-26 22:16:00 | 10 | ws2r 21.29; ws3r 14.98 | ws2r 17.83; ws3r 8.84 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws3r -> ws4r | LOW | A only | 2026-10-26 22:16:25 | - | - | ws3r 15.49; ws4r 9.82 | ws3r 8.84; ws4r 19.38 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws2r -> ws3r | LOW | A only | 2026-10-26 22:16:35 | - | - | ws2r 17.88; ws3r 17.56 | ws2r 20.91; ws3r 8.84 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws2r -> ws3r | LOW | both | 2026-10-26 22:17:55 | 2026-10-26 22:20:00 | 125 | ws2r 16.17; ws3r 16.46 | ws2r 20.91; ws3r 8.84 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws3r -> ws4r | LOW | A only | 2026-10-26 22:17:55 | - | - | ws3r 16.46; ws4r 10.95 | ws3r 8.84; ws4r 19.38 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws3r -> ws4r | LOW | both | 2026-10-26 22:18:00 | 2026-10-26 22:21:00 | 180 | ws3r 23.27; ws4r 9.82 | ws3r 16.46; ws4r 19.38 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws3r -> ws4r | LOW | B only | - | 2026-10-26 22:18:00 | - | - | - | - | - | - | - | - | - |
| #4 r into oob | ws9r | HIGH | A only | 2026-10-26 22:21:10 | - | - | ws9r 85.17 | ws9r 82.20 | 20 | no | no | - | - | - |
| #4 r into oob | ws9r | HIGH | A only | 2026-10-26 22:23:40 | - | - | ws9r 85.03 | ws9r 82.20 | 5 | no | no | - | - | - |
| #1 ws1b oob -> ib | ws1b | LOW | A only | 2026-10-26 22:31:25 | - | - | ws1b 16.81 | ws1b 10.89 | 5 | no | no | - | - | - |
| #1 ws1b oob -> ib | ws1b | LOW | both | 2026-10-26 22:32:05 | 2026-10-26 22:33:00 | 55 | ws1b 16.62 | ws1b 10.84 | 1760 | yes | yes | 1740 | yes | yes |
| #4 r into oob | ws6r | LOW | A only | 2026-10-26 22:36:35 | - | - | ws6r 14.16 | ws6r 22.00 | 200 | no | yes | - | - | - |
| #4 r into oob | ws6r | LOW | A only | 2026-10-26 22:40:05 | - | - | ws6r 14.04 | ws6r 22.00 | 110 | no | yes | - | - | - |
| #4 r into oob | ws6r | LOW | both | 2026-10-26 22:42:05 | 2026-10-26 22:48:00 | 355 | ws6r 10.37 | ws6r 16.36 | 355 | yes | yes | 720 | yes | yes |
| #2 baton pass (oob -> ib) | ws2r -> ws3r | HIGH | A only | 2026-10-26 22:52:25 | - | - | ws2r 82.62; ws3r 82.72 | ws2r 86.55; ws3r 72.65 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws2r -> ws3r | HIGH | A only | 2026-10-26 22:52:55 | - | - | ws2r 78.88; ws3r 80.98 | ws2r 86.55; ws3r 72.65 | - | - | - | - | - | - |
| #4 r into oob | ws6r | LOW | A only | 2026-10-26 22:53:25 | - | - | ws6r 12.44 | ws6r 12.44 | 95 | yes | yes | - | - | - |
| #4 r into oob | ws6r | LOW | A only | 2026-10-26 22:56:25 | - | - | ws6r 12.44 | ws6r 12.44 | 5 | no | no | - | - | - |
| #3 Mage into oob | ws5Mage | LOW | A only | 2026-10-26 23:02:05 | - | - | ws5Mage 13.31 | ws5Mage 56.39 | 5 | yes | no | - | - | - |
| #3 Mage into oob | ws6Mage | LOW | A only | 2026-10-26 23:02:05 | - | - | ws6Mage 12.29 | ws6Mage 53.48 | 15 | yes | no | - | - | - |
| #3 Mage into oob | ws7Mage | LOW | A only | 2026-10-26 23:02:05 | - | - | ws7Mage 14.59 | ws7Mage 51.37 | 5 | yes | no | - | - | - |
| #3 Mage into oob | ws8Mage | LOW | A only | 2026-10-26 23:02:05 | - | - | ws8Mage 14.31 | ws8Mage 38.38 | 5 | yes | no | - | - | - |
| #3 Mage into oob | ws5Mage | LOW | A only | 2026-10-26 23:02:15 | - | - | ws5Mage 14.45 | ws5Mage 56.39 | 5 | yes | no | - | - | - |
| #3 Mage into oob | ws5Mage | LOW | both | 2026-10-26 23:02:40 | 2026-10-26 23:05:00 | 140 | ws5Mage 12.18 | ws5Mage 56.39 | 220 | yes | yes | 300 | yes | yes |
| #3 Mage into oob | ws6Mage | LOW | both | 2026-10-26 23:02:40 | 2026-10-26 23:06:00 | 200 | ws6Mage 11.21 | ws6Mage 53.48 | 220 | yes | yes | 360 | yes | yes |
| #3 Mage into oob | ws7Mage | LOW | both | 2026-10-26 23:02:40 | 2026-10-26 23:06:00 | 200 | ws7Mage 13.58 | ws7Mage 51.37 | 220 | yes | yes | 420 | yes | yes |
| #3 Mage into oob | ws8Mage | LOW | both | 2026-10-26 23:02:40 | 2026-10-26 23:04:00 | 80 | ws8Mage 13.47 | ws8Mage 38.38 | 230 | yes | yes | 480 | yes | yes |
| #3 Mage into oob | ws9Mage | LOW | A only | 2026-10-26 23:03:00 | - | - | ws9Mage 11.97 | ws9Mage 36.98 | 45 | yes | no | - | - | - |
| #3 Mage into oob | ws10Mage | LOW | A only | 2026-10-26 23:03:00 | - | - | ws10Mage 13.75 | ws10Mage 40.21 | 30 | no | no | - | - | - |
| #3 Mage into oob | ws11Mage | LOW | A only | 2026-10-26 23:03:00 | - | - | ws11Mage 14.58 | ws11Mage 36.25 | 20 | no | no | - | - | - |
| #3 Mage into oob | ws12Mage | LOW | A only | 2026-10-26 23:03:00 | - | - | ws12Mage 11.84 | ws12Mage 38.52 | 45 | no | no | - | - | - |
| #3 Mage into oob | ws11Mage | LOW | A only | 2026-10-26 23:03:25 | - | - | ws11Mage 14.31 | ws11Mage 36.25 | 5 | no | no | - | - | - |
| #3 Mage into oob | ws9Mage | LOW | A only | 2026-10-26 23:04:00 | - | - | ws9Mage 12.86 | ws9Mage 36.98 | 20 | yes | no | - | - | - |
| #3 Mage into oob | ws10Mage | LOW | A only | 2026-10-26 23:04:00 | - | - | ws10Mage 14.53 | ws10Mage 40.21 | 5 | no | no | - | - | - |
| #3 Mage into oob | ws12Mage | LOW | A only | 2026-10-26 23:04:00 | - | - | ws12Mage 12.64 | ws12Mage 38.52 | 20 | no | no | - | - | - |
| #3 Mage into oob | ws10Mage | LOW | A only | 2026-10-26 23:04:10 | - | - | ws10Mage 14.53 | ws10Mage 40.21 | 5 | no | no | - | - | - |
| #3 Mage into oob | ws9Mage | LOW | both | 2026-10-26 23:04:50 | 2026-10-26 23:06:00 | 70 | ws9Mage 14.07 | ws9Mage 36.98 | 70 | yes | yes | 540 | yes | yes |
| #3 Mage into oob | ws12Mage | LOW | A only | 2026-10-26 23:04:50 | - | - | ws12Mage 13.71 | ws12Mage 38.52 | 80 | no | yes | - | - | - |
| #3 Mage into oob | ws10Mage | LOW | A only | 2026-10-26 23:05:00 | - | - | ws10Mage 14.79 | ws10Mage 40.21 | 25 | no | no | - | - | - |
| #3 Mage into oob | ws11Mage | LOW | A only | 2026-10-26 23:05:10 | - | - | ws11Mage 14.58 | ws11Mage 36.25 | 15 | no | no | - | - | - |
| #3 Mage into oob | ws8Mage | LOW | A only | 2026-10-26 23:06:40 | - | - | ws8Mage 14.46 | ws8Mage 9.34 | 40 | no | no | - | - | - |
| #3 Mage into oob | ws6Mage | LOW | A only | 2026-10-26 23:06:45 | - | - | ws6Mage 14.72 | ws6Mage 2.33 | 25 | no | no | - | - | - |
| #3 Mage into oob | ws5Mage | LOW | A only | 2026-10-26 23:06:50 | - | - | ws5Mage 14.14 | ws5Mage 2.98 | 20 | no | no | - | - | - |
| #3 Mage into oob | ws7Mage | LOW | A only | 2026-10-26 23:06:55 | - | - | ws7Mage 14.19 | ws7Mage 5.27 | 15 | no | no | - | - | - |
| #1 ws1b oob -> ib | ws1b | LOW | both | 2026-10-26 23:07:20 | 2026-10-26 23:08:00 | 40 | ws1b 18.52 | ws1b 1.94 | 1340 | yes | yes | 1320 | yes | yes |
| #2 baton pass (oob -> ib + ex-fence -> in-fence) | ws2r -> ws3r | HIGH | A only | 2026-10-26 23:24:00 | - | - | ws2r 77.84; ws3r 81.57 | ws2r 87.06; ws3r 70.30 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws2r -> ws3r | HIGH | A only | 2026-10-26 23:24:20 | - | - | ws2r 79.94; ws3r 82.36 | ws2r 87.06; ws3r 70.30 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib + ex-fence -> in-fence) | ws2r -> ws3r | HIGH | A only | 2026-10-26 23:26:00 | - | - | ws2r 73.21; ws3r 83.70 | ws2r 85.61; ws3r 70.30 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws2r -> ws3r | HIGH | A only | 2026-10-26 23:27:30 | - | - | ws2r 84.15; ws3r 90.66 | ws2r 85.61; ws3r 83.53 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws2r -> ws3r | HIGH | A only | 2026-10-26 23:28:55 | - | - | ws2r 81.88; ws3r 90.66 | ws2r 85.61; ws3r 83.53 | - | - | - | - | - | - |
| #1 ws1b oob -> ib | ws1b | HIGH | A only | 2026-10-26 23:31:00 | - | - | ws1b 84.38 | ws1b 87.37 | 40 | no | no | - | - | - |
| #2 baton pass (oob -> ib) | ws2r -> ws3r | HIGH | A only | 2026-10-26 23:31:10 | - | - | ws2r 83.42; ws3r 92.29 | ws2r 85.61; ws3r 90.66 | - | - | - | - | - | - |
| #1 ws1b oob -> ib | ws1b | HIGH | both | 2026-10-26 23:32:00 | 2026-10-26 23:33:00 | 60 | ws1b 80.83 | ws1b 85.72 | 115 | yes | yes | 60 | yes | yes |
| #2 baton pass (oob -> ib) | ws2r -> ws3r | HIGH | A only | 2026-10-26 23:32:00 | - | - | ws2r 82.56; ws3r 93.72 | ws2r 89.03; ws3r 90.66 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws2r -> ws3r | HIGH | A only | 2026-10-26 23:32:05 | - | - | ws2r 74.74; ws3r 89.38 | ws2r 89.03; ws3r 90.66 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws3r -> ws4r | HIGH | A only | 2026-10-26 23:33:05 | - | - | ws3r 84.55; ws4r 85.01 | ws3r 91.40; ws4r 78.85 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws1r -> ws2r | HIGH | A only | 2026-10-26 23:34:00 | - | - | ws1r 79.50; ws2r 89.48 | ws1r 82.20; ws2r 89.03 | - | - | - | - | - | - |
| #3 Mage into oob | ws5Mage | HIGH | both | 2026-10-26 23:34:15 | 2026-10-26 23:35:00 | 45 | ws5Mage 91.82 | ws5Mage 74.27 | 3545 | yes | yes | 3900 | yes | yes |
| #3 Mage into oob | ws6Mage | HIGH | both | 2026-10-26 23:34:15 | 2026-10-26 23:36:00 | 105 | ws6Mage 90.80 | ws6Mage 73.18 | 3565 | yes | yes | 4320 | yes | yes |
| #3 Mage into oob | ws8Mage | HIGH | both | 2026-10-26 23:34:15 | 2026-10-26 23:36:00 | 105 | ws8Mage 90.41 | ws8Mage 60.99 | 4375 | yes | yes | 4800 | yes | yes |
| #3 Mage into oob | ws7Mage | HIGH | both | 2026-10-26 23:34:20 | 2026-10-26 23:41:00 | 400 | ws7Mage 87.34 | ws7Mage 72.73 | 4200 | yes | yes | 4080 | yes | yes |
| #4 r into oob | ws5r | HIGH | both | 2026-10-26 23:35:00 | 2026-10-26 23:40:00 | 300 | ws5r 89.61 | ws5r 76.31 | 1825 | yes | yes | 3000 | yes | yes |
| #3 Mage into oob | ws9Mage | HIGH | both | 2026-10-26 23:36:40 | 2026-10-26 23:42:00 | 320 | ws9Mage 85.97 | ws9Mage 54.12 | 4230 | yes | yes | 4320 | yes | yes |
| #2 baton pass (oob -> ib) | ws1r -> ws2r | HIGH | A only | 2026-10-26 23:40:45 | - | - | ws1r 84.15; ws2r 95.28 | ws1r 91.59; ws2r 100.00 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib + ex-fence -> in-fence) | ws1r -> ws2r | HIGH | both | 2026-10-26 23:41:00 | 2026-10-26 23:42:00 | 60 | ws1r 72.36; ws2r 96.17 | ws1r 86.64; ws2r 100.00 | - | - | - | - | - | - |
| #4 r into oob | ws6r | HIGH | both | 2026-10-26 23:42:00 | 2026-10-26 23:48:00 | 360 | ws6r 92.16 | ws6r 78.17 | 1980 | yes | yes | 2520 | yes | yes |
| #2 baton pass (oob -> ib) | ws2r -> ws3r | HIGH | A only | 2026-10-26 23:42:00 | - | - | ws2r 82.20; ws3r 93.73 | ws2r 93.58; ws3r 94.01 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws2r -> ws3r | HIGH | A only | 2026-10-26 23:42:05 | - | - | ws2r 79.30; ws3r 90.10 | ws2r 93.58; ws3r 94.01 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws2r -> ws3r | HIGH | A only | 2026-10-26 23:42:50 | - | - | ws2r 79.30; ws3r 91.85 | ws2r 93.58; ws3r 94.01 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws2r -> ws3r | HIGH | A only | 2026-10-26 23:43:25 | - | - | ws2r 84.90; ws3r 95.06 | ws2r 93.58; ws3r 94.01 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib + ex-fence -> in-fence) | ws2r -> ws3r | HIGH | A only | 2026-10-26 23:44:00 | - | - | ws2r 78.05; ws3r 95.06 | ws2r 86.80; ws3r 94.01 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws2r -> ws3r | HIGH | A only | 2026-10-26 23:44:45 | - | - | ws2r 75.04; ws3r 95.06 | ws2r 86.80; ws3r 94.01 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws2r -> ws3r | HIGH | both | 2026-10-26 23:45:30 | 2026-10-26 23:46:00 | 30 | ws2r 79.88; ws3r 96.12 | ws2r 86.80; ws3r 95.06 | - | - | - | - | - | - |
| #1 ws1b oob -> ib | ws1b | HIGH | A only | 2026-10-26 23:45:50 | - | - | ws1b 84.71 | ws1b 86.94 | 5 | no | no | - | - | - |
| #1 ws1b oob -> ib | ws1b | HIGH | A only | 2026-10-26 23:46:00 | - | - | ws1b 84.54 | ws1b 85.68 | 5 | no | no | - | - | - |
| #1 ws1b oob -> ib | ws1b | HIGH | A only | 2026-10-26 23:46:20 | - | - | ws1b 84.85 | ws1b 85.68 | 25 | no | no | - | - | - |
| #1 ws1b oob -> ib | ws1b | HIGH | A only | 2026-10-26 23:46:50 | - | - | ws1b 84.22 | ws1b 85.68 | 5 | no | no | - | - | - |
| #1 ws1b oob -> ib | ws1b | HIGH | A only | 2026-10-26 23:47:00 | - | - | ws1b 84.99 | ws1b 85.17 | 25 | no | no | - | - | - |
| #4 r into oob | ws7r | HIGH | both | 2026-10-26 23:48:00 | 2026-10-26 23:55:00 | 420 | ws7r 91.85 | ws7r 77.57 | 2360 | yes | yes | 2400 | yes | yes |
| #3 Mage into oob | ws10Mage | HIGH | A only | 2026-10-26 23:48:00 | - | - | ws10Mage 85.04 | ws10Mage 79.55 | 5 | no | no | - | - | - |
| #3 Mage into oob | ws10Mage | HIGH | A only | 2026-10-26 23:48:20 | - | - | ws10Mage 87.14 | ws10Mage 79.55 | 15 | no | no | - | - | - |
| #1 ws1b oob -> ib | ws1b | HIGH | both | 2026-10-26 23:48:35 | 2026-10-26 23:49:00 | 25 | ws1b 84.35 | ws1b 86.81 | 1240 | yes | yes | 1260 | yes | yes |
| #2 baton pass (oob -> ib) | ws3r -> ws4r | HIGH | A only | 2026-10-26 23:49:20 | - | - | ws3r 82.69; ws4r 92.69 | ws3r 96.12; ws4r 98.01 | - | - | - | - | - | - |
| #3 Mage into oob | ws10Mage | HIGH | A only | 2026-10-26 23:51:00 | - | - | ws10Mage 85.44 | ws10Mage 79.18 | 30 | yes | no | - | - | - |
| #3 Mage into oob | ws10Mage | HIGH | A only | 2026-10-26 23:52:00 | - | - | ws10Mage 85.78 | ws10Mage 79.18 | 120 | yes | yes | - | - | - |
| #4 r into oob | ws8r | HIGH | both | 2026-10-26 23:52:00 | 2026-10-27 00:00:00 | 480 | ws8r 94.09 | ws8r 79.80 | 2400 | yes | yes | 2400 | yes | yes |
| #3 Mage into oob | ws10Mage | HIGH | A only | 2026-10-26 23:54:05 | - | - | ws10Mage 85.44 | ws10Mage 79.18 | 20 | yes | no | - | - | - |
| #3 Mage into oob | ws10Mage | HIGH | both | 2026-10-26 23:55:50 | 2026-10-27 00:00:00 | 250 | ws10Mage 89.73 | ws10Mage 79.18 | 285 | yes | yes | 3600 | yes | yes |
| #2 baton pass (oob -> ib + ex-fence -> in-fence) | ws4r -> ws5r | HIGH | A only | 2026-10-26 23:56:00 | - | - | ws4r 79.92; ws5r 98.95 | ws4r 89.58; ws5r 98.03 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws4r -> ws5r | HIGH | A only | 2026-10-26 23:58:20 | - | - | ws4r 79.92; ws5r 98.95 | ws4r 89.58; ws5r 98.03 | - | - | - | - | - | - |
| #4 r into oob | ws9r | HIGH | both | 2026-10-27 00:00:00 | 2026-10-27 00:09:00 | 540 | ws9r 97.21 | ws9r 83.66 | 1625 | yes | yes | 1620 | yes | yes |
| #2 baton pass (ex-fence -> in-fence) | ws4r -> ws5r | HIGH | both | 2026-10-27 00:00:00 | 2026-10-27 00:04:00 | 240 | ws4r 69.00; ws5r 94.34 | ws4r 83.29; ws5r 98.95 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws4r -> ws5r | HIGH | B only | - | 2026-10-27 00:00:00 | - | - | - | - | - | - | - | - | - |
| #3 Mage into oob | ws10Mage | HIGH | A only | 2026-10-27 00:00:50 | - | - | ws10Mage 85.66 | ws10Mage 89.40 | 100 | yes | yes | - | - | - |
| #4 r into oob | ws10r | HIGH | A only | 2026-10-27 00:01:05 | - | - | ws10r 85.71 | ws10r 75.26 | 15 | yes | no | - | - | - |
| #2 baton pass (oob -> ib) | ws10r -> ws11r | HIGH | A only | 2026-10-27 00:01:20 | - | - | ws10r 83.99; ws11r 81.24 | ws10r 75.26; ws11r 71.15 | - | - | - | - | - | - |
| #4 r into oob | ws10r | HIGH | A only | 2026-10-27 00:01:30 | - | - | ws10r 85.53 | ws10r 75.26 | 30 | yes | no | - | - | - |
| #2 baton pass (oob -> ib) | ws10r -> ws11r | HIGH | A only | 2026-10-27 00:02:00 | - | - | ws10r 84.81; ws11r 81.90 | ws10r 75.26; ws11r 71.15 | - | - | - | - | - | - |
| #4 r into oob | ws10r | HIGH | A only | 2026-10-27 00:02:05 | - | - | ws10r 85.53 | ws10r 75.26 | 5 | yes | no | - | - | - |
| #2 baton pass (oob -> ib) | ws10r -> ws11r | HIGH | A only | 2026-10-27 00:02:10 | - | - | ws10r 84.99; ws11r 82.04 | ws10r 75.26; ws11r 71.15 | - | - | - | - | - | - |
| #3 Mage into oob | ws10Mage | HIGH | A only | 2026-10-27 00:02:35 | - | - | ws10Mage 85.01 | ws10Mage 89.40 | 2775 | yes | yes | - | - | - |
| #4 r into oob | ws10r | HIGH | A only | 2026-10-27 00:02:40 | - | - | ws10r 85.34 | ws10r 75.26 | 100 | yes | yes | - | - | - |
| #3 Mage into oob | ws12Mage | HIGH | A only | 2026-10-27 00:03:35 | - | - | ws12Mage 85.69 | ws12Mage 82.33 | 25 | yes | no | - | - | - |
| #3 Mage into oob | ws11Mage | HIGH | A only | 2026-10-27 00:03:40 | - | - | ws11Mage 85.13 | ws11Mage 78.54 | 5 | yes | no | - | - | - |
| #2 baton pass (oob -> ib) | ws10r -> ws11r | HIGH | A only | 2026-10-27 00:04:20 | - | - | ws10r 84.99; ws11r 82.04 | ws10r 75.26; ws11r 71.15 | - | - | - | - | - | - |
| #4 r into oob | ws10r | HIGH | A only | 2026-10-27 00:04:35 | - | - | ws10r 85.34 | ws10r 75.26 | 50 | yes | no | - | - | - |
| #2 baton pass (oob -> ib) | ws10r -> ws11r | HIGH | A only | 2026-10-27 00:05:25 | - | - | ws10r 84.47; ws11r 81.63 | ws10r 75.26; ws11r 71.15 | - | - | - | - | - | - |
| #4 r into oob | ws5r | HIGH | A only | 2026-10-27 00:05:40 | - | - | ws5r 88.94 | ws5r 97.97 | 275 | yes | yes | - | - | - |
| #4 r into oob | ws10r | HIGH | A only | 2026-10-27 00:05:50 | - | - | ws10r 85.53 | ws10r 75.26 | 45 | yes | no | - | - | - |
| #2 baton pass (oob -> ib) | ws10r -> ws11r | HIGH | A only | 2026-10-27 00:06:35 | - | - | ws10r 84.81; ws11r 81.90 | ws10r 75.26; ws11r 71.15 | - | - | - | - | - | - |
| #4 r into oob | ws10r | HIGH | both | 2026-10-27 00:06:40 | 2026-10-27 00:10:00 | 200 | ws10r 85.71 | ws10r 75.26 | 1445 | yes | yes | 1800 | yes | yes |
| #3 Mage into oob | ws12Mage | HIGH | A only | 2026-10-27 00:07:20 | - | - | ws12Mage 89.74 | ws12Mage 82.33 | 40 | yes | no | - | - | - |
| #3 Mage into oob | ws11Mage | HIGH | A only | 2026-10-27 00:07:20 | - | - | ws11Mage 88.05 | ws11Mage 78.54 | 10 | yes | no | - | - | - |
| #3 Mage into oob | ws12Mage | HIGH | both | 2026-10-27 00:08:20 | 2026-10-27 00:12:00 | 220 | ws12Mage 89.46 | ws12Mage 82.33 | 1920 | yes | yes | 2880 | yes | yes |
| #3 Mage into oob | ws11Mage | HIGH | both | 2026-10-27 00:08:20 | 2026-10-27 00:11:00 | 160 | ws11Mage 87.79 | ws11Mage 78.54 | 2330 | yes | yes | 2640 | yes | yes |
| #1 ws1b oob -> ib | ws1b | HIGH | both | 2026-10-27 00:10:00 | 2026-10-27 00:11:00 | 60 | ws1b 83.73 | ws1b 86.26 | 85 | yes | yes | 60 | yes | yes |
| #4 r into oob | ws5r | HIGH | A only | 2026-10-27 00:10:55 | - | - | ws5r 85.68 | ws5r 97.97 | 945 | yes | yes | - | - | - |
| #4 r into oob | ws11r | HIGH | both | 2026-10-27 00:11:00 | 2026-10-27 00:22:00 | 660 | ws11r 96.89 | ws11r 82.60 | 1320 | yes | yes | 1320 | yes | yes |
| #1 ws1b oob -> ib | ws1b | HIGH | A only | 2026-10-27 00:14:50 | - | - | ws1b 83.94 | ws1b 90.23 | 5 | no | no | - | - | - |
| #1 ws1b oob -> ib | ws1b | HIGH | A only | 2026-10-27 00:15:00 | - | - | ws1b 82.06 | ws1b 85.12 | 45 | no | no | - | - | - |
| #2 baton pass (oob -> ib) | ws6r -> ws7r | HIGH | A only | 2026-10-27 00:15:00 | - | - | ws6r 84.21; ws7r 89.49 | ws6r 95.35; ws7r 95.76 | - | - | - | - | - | - |
| #4 r into oob | ws6r | HIGH | A only | 2026-10-27 00:15:10 | - | - | ws6r 86.92 | ws6r 95.35 | 20 | yes | no | - | - | - |
| #4 r into oob | ws6r | HIGH | A only | 2026-10-27 00:15:45 | - | - | ws6r 92.89 | ws6r 95.35 | 195 | yes | yes | - | - | - |
| #4 r into oob | ws6r | HIGH | A only | 2026-10-27 00:19:45 | - | - | ws6r 85.47 | ws6r 95.35 | 10 | yes | no | - | - | - |
| #4 r into oob | ws6r | HIGH | A only | 2026-10-27 00:20:05 | - | - | ws6r 90.74 | ws6r 95.35 | 25 | yes | no | - | - | - |
| #4 r into oob | ws6r | HIGH | A only | 2026-10-27 00:20:40 | - | - | ws6r 87.73 | ws6r 95.35 | 10 | yes | no | - | - | - |
| #4 r into oob | ws6r | HIGH | A only | 2026-10-27 00:21:00 | - | - | ws6r 92.66 | ws6r 95.35 | 225 | yes | yes | - | - | - |
| #4 r into oob | ws12r | HIGH | both | 2026-10-27 00:24:00 | 2026-10-27 00:36:00 | 720 | ws12r 98.11 | ws12r 83.83 | 1390 | yes | yes | 1440 | yes | yes |
| #2 baton pass (oob -> ib) | ws6r -> ws7r | HIGH | A only | 2026-10-27 00:24:45 | - | - | ws6r 83.90; ws7r 95.76 | ws6r 89.51; ws7r 95.76 | - | - | - | - | - | - |
| #4 r into oob | ws6r | HIGH | A only | 2026-10-27 00:25:05 | - | - | ws6r 85.14 | ws6r 89.51 | 15 | no | no | - | - | - |
| #2 baton pass (oob -> ib) | ws6r -> ws7r | HIGH | A only | 2026-10-27 00:25:20 | - | - | ws6r 84.70; ws7r 95.76 | ws6r 89.51; ws7r 95.76 | - | - | - | - | - | - |
| #1 ws1b oob -> ib | ws1b | HIGH | both | 2026-10-27 00:26:25 | 2026-10-27 00:27:00 | 35 | ws1b 82.46 | ws1b 87.77 | 1615 | yes | yes | 1860 | yes | yes |
| #2 baton pass (oob -> ib) | ws4r -> ws5r | HIGH | A only | 2026-10-27 00:26:30 | - | - | ws4r 82.56; ws5r 87.53 | ws4r 82.66; ws5r 98.84 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws4r -> ws5r | HIGH | both | 2026-10-27 00:26:40 | 2026-10-27 00:28:00 | 80 | ws4r 74.67; ws5r 84.74 | ws4r 82.66; ws5r 98.84 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws6r -> ws7r | HIGH | A only | 2026-10-27 00:26:40 | - | - | ws6r 75.23; ws7r 91.46 | ws6r 89.51; ws7r 95.76 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws9r -> ws10r | HIGH | A only | 2026-10-27 00:27:05 | - | - | ws9r 84.61; ws10r 95.61 | ws9r 93.42; ws10r 100.00 | - | - | - | - | - | - |
| #4 r into oob | ws7r | HIGH | A only | 2026-10-27 00:27:25 | - | - | ws7r 85.06 | ws7r 95.76 | 10 | yes | no | - | - | - |
| #4 r into oob | ws7r | HIGH | A only | 2026-10-27 00:27:50 | - | - | ws7r 85.06 | ws7r 95.76 | 10 | yes | no | - | - | - |
| #4 r into oob | ws9r | HIGH | A only | 2026-10-27 00:28:55 | - | - | ws9r 85.70 | ws9r 93.42 | 25 | no | no | - | - | - |
| #2 baton pass (oob -> ib) | ws9r -> ws10r | HIGH | A only | 2026-10-27 00:29:20 | - | - | ws9r 84.39; ws10r 95.42 | ws9r 93.42; ws10r 100.00 | - | - | - | - | - | - |
| #4 r into oob | ws9r | HIGH | A only | 2026-10-27 00:30:35 | - | - | ws9r 85.06 | ws9r 93.42 | 5 | no | no | - | - | - |
| #2 baton pass (oob -> ib) | ws9r -> ws10r | HIGH | A only | 2026-10-27 00:30:40 | - | - | ws9r 82.53; ws10r 85.99 | ws9r 93.42; ws10r 94.32 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws10r -> ws11r | HIGH | A only | 2026-10-27 00:30:45 | - | - | ws10r 84.65; ws11r 92.96 | ws10r 94.32; ws11r 96.89 | - | - | - | - | - | - |
| #4 r into oob | ws10r | HIGH | A only | 2026-10-27 00:31:10 | - | - | ws10r 86.27 | ws10r 94.32 | 120 | no | yes | - | - | - |
| #4 r into oob | ws9r | HIGH | A only | 2026-10-27 00:31:40 | - | - | ws9r 85.06 | ws9r 93.42 | 15 | no | no | - | - | - |
| #2 baton pass (oob -> ib) | ws1r -> ws2r | LOW | A only | 2026-10-27 00:31:40 | - | - | ws1r 15.07; ws2r 15.42 | ws1r 9.45; ws2r 27.69 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws9r -> ws10r | HIGH | A only | 2026-10-27 00:31:55 | - | - | ws9r 84.18; ws10r 87.26 | ws9r 93.42; ws10r 94.32 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws1r -> ws2r | LOW | A only | 2026-10-27 00:32:00 | - | - | ws1r 17.34; ws2r 10.18 | ws1r 13.66; ws2r 14.59 | - | - | - | - | - | - |
| #4 r into oob | ws9r | HIGH | A only | 2026-10-27 00:32:35 | - | - | ws9r 85.06 | ws9r 93.42 | 20 | no | no | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws1r -> ws2r | LOW | A only | 2026-10-27 00:32:45 | - | - | ws1r 20.12; ws2r 12.47 | ws1r 13.66; ws2r 14.59 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws9r -> ws10r | HIGH | A only | 2026-10-27 00:32:55 | - | - | ws9r 84.18; ws10r 87.26 | ws9r 93.42; ws10r 94.32 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws1r -> ws2r | LOW | A only | 2026-10-27 00:33:00 | - | - | ws1r 22.35; ws2r 8.18 | ws1r 16.87; ws2r 14.59 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws1r -> ws2r | LOW | B only | - | 2026-10-27 00:33:00 | - | - | - | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws11r -> ws12r | HIGH | A only | 2026-10-27 00:33:00 | - | - | ws11r 84.53; ws12r 93.37 | ws11r 94.40; ws12r 83.83 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws10r -> ws11r | HIGH | A only | 2026-10-27 00:33:10 | - | - | ws10r 84.39; ws11r 83.80 | ws10r 94.32; ws11r 94.40 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws9r -> ws10r | HIGH | A only | 2026-10-27 00:33:20 | - | - | ws9r 79.82; ws10r 82.22 | ws9r 93.42; ws10r 94.32 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws9r -> ws10r | HIGH | both | 2026-10-27 00:33:40 | 2026-10-27 00:36:00 | 140 | ws9r 79.49; ws10r 81.77 | ws9r 93.42; ws10r 94.32 | - | - | - | - | - | - |
| #3 Mage into oob | ws5Mage | HIGH | A only | 2026-10-27 00:34:00 | - | - | ws5Mage 85.77 | ws5Mage 90.75 | 50 | yes | no | - | - | - |
| #3 Mage into oob | ws6Mage | HIGH | A only | 2026-10-27 00:34:00 | - | - | ws6Mage 86.78 | ws6Mage 92.17 | 160 | yes | yes | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws1r -> ws2r | LOW | both | 2026-10-27 00:34:00 | 2026-10-27 00:35:00 | 60 | ws1r 25.45; ws2r 5.48 | ws1r 16.87; ws2r 8.18 | - | - | - | - | - | - |
| #3 Mage into oob | ws5Mage | HIGH | A only | 2026-10-27 00:34:55 | - | - | ws5Mage 85.08 | ws5Mage 90.75 | 5 | yes | no | - | - | - |
| #4 r into oob | ws10r | HIGH | A only | 2026-10-27 00:35:20 | - | - | ws10r 85.17 | ws10r 94.32 | 5 | no | no | - | - | - |
| #2 baton pass (oob -> ib) | ws10r -> ws11r | HIGH | A only | 2026-10-27 00:35:25 | - | - | ws10r 84.91; ws11r 84.16 | ws10r 94.32; ws11r 94.40 | - | - | - | - | - | - |
| #3 Mage into oob | ws5Mage | HIGH | A only | 2026-10-27 00:35:35 | - | - | ws5Mage 86.18 | ws5Mage 85.08 | 65 | no | yes | - | - | - |
| #4 r into oob | ws10r | HIGH | A only | 2026-10-27 00:35:35 | - | - | ws10r 86.85 | ws10r 94.32 | 65 | no | yes | - | - | - |
| #4 r into oob | ws11r | HIGH | A only | 2026-10-27 00:35:35 | - | - | ws11r 85.49 | ws11r 94.40 | 55 | no | no | - | - | - |
| #2 baton pass (oob -> ib) | ws2r -> ws3r | LOW | A only | 2026-10-27 00:36:05 | - | - | ws2r 16.01; ws3r 7.34 | ws2r 8.07; ws3r 17.76 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws11r -> ws12r | HIGH | A only | 2026-10-27 00:36:30 | - | - | ws11r 84.91; ws12r 89.01 | ws11r 94.40; ws12r 93.91 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws10r -> ws11r | HIGH | A only | 2026-10-27 00:36:40 | - | - | ws10r 84.91; ws11r 84.16 | ws10r 94.32; ws11r 94.40 | - | - | - | - | - | - |
| #3 Mage into oob | ws5Mage | HIGH | A only | 2026-10-27 00:37:25 | - | - | ws5Mage 85.96 | ws5Mage 85.08 | 15 | no | no | - | - | - |
| #3 Mage into oob | ws6Mage | HIGH | A only | 2026-10-27 00:37:25 | - | - | ws6Mage 86.16 | ws6Mage 89.27 | 15 | yes | no | - | - | - |
| #4 r into oob | ws10r | HIGH | A only | 2026-10-27 00:37:25 | - | - | ws10r 86.56 | ws10r 94.32 | 15 | no | no | - | - | - |
| #4 r into oob | ws11r | HIGH | A only | 2026-10-27 00:37:25 | - | - | ws11r 85.29 | ws11r 94.40 | 5 | no | no | - | - | - |
| #2 baton pass (oob -> ib) | ws11r -> ws12r | HIGH | A only | 2026-10-27 00:37:30 | - | - | ws11r 84.53; ws12r 88.69 | ws11r 94.40; ws12r 93.91 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws10r -> ws11r | HIGH | A only | 2026-10-27 00:37:40 | - | - | ws10r 84.91; ws11r 84.16 | ws10r 94.32; ws11r 94.40 | - | - | - | - | - | - |
| #3 Mage into oob | ws5Mage | HIGH | A only | 2026-10-27 00:37:45 | - | - | ws5Mage 85.96 | ws5Mage 85.08 | 115 | no | yes | - | - | - |
| #3 Mage into oob | ws6Mage | HIGH | A only | 2026-10-27 00:37:45 | - | - | ws6Mage 86.16 | ws6Mage 89.27 | 115 | yes | yes | - | - | - |
| #4 r into oob | ws10r | HIGH | A only | 2026-10-27 00:37:45 | - | - | ws10r 86.56 | ws10r 94.32 | 115 | no | yes | - | - | - |
| #4 r into oob | ws11r | HIGH | A only | 2026-10-27 00:37:45 | - | - | ws11r 85.29 | ws11r 94.40 | 5 | no | no | - | - | - |
| #2 baton pass (oob -> ib) | ws11r -> ws12r | HIGH | A only | 2026-10-27 00:37:50 | - | - | ws11r 84.72; ws12r 88.85 | ws11r 94.40; ws12r 93.91 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws2r -> ws3r | LOW | A only | 2026-10-27 00:38:00 | - | - | ws2r 15.19; ws3r 4.52 | ws2r 12.34; ws3r 17.76 | - | - | - | - | - | - |
| #4 r into oob | ws11r | HIGH | A only | 2026-10-27 00:38:10 | - | - | ws11r 85.29 | ws11r 94.40 | 85 | no | yes | - | - | - |
| #2 baton pass (oob -> ib) | ws2r -> ws3r | LOW | A only | 2026-10-27 00:38:10 | - | - | ws2r 16.05; ws3r 4.52 | ws2r 12.34; ws3r 17.76 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws2r -> ws3r | LOW | A only | 2026-10-27 00:38:40 | - | - | ws2r 20.36; ws3r 8.90 | ws2r 12.34; ws3r 17.76 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws11r -> ws12r | HIGH | A only | 2026-10-27 00:39:35 | - | - | ws11r 84.72; ws12r 88.85 | ws11r 94.40; ws12r 93.91 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws10r -> ws11r | HIGH | A only | 2026-10-27 00:39:40 | - | - | ws10r 83.15; ws11r 82.93 | ws10r 94.32; ws11r 94.40 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws10r -> ws11r | HIGH | both | 2026-10-27 00:40:00 | 2026-10-27 00:50:00 | 600 | ws10r 67.04; ws11r 81.48 | ws10r 81.33; ws11r 94.40 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws10r -> ws11r | HIGH | B only | - | 2026-10-27 00:40:00 | - | - | - | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws2r -> ws3r | LOW | A only | 2026-10-27 00:40:05 | - | - | ws2r 16.75; ws3r 6.77 | ws2r 11.61; ws3r 7.34 | - | - | - | - | - | - |
| #3 Mage into oob | ws12Mage | HIGH | A only | 2026-10-27 00:40:25 | - | - | ws12Mage 86.24 | ws12Mage 92.20 | 385 | yes | yes | - | - | - |
| #2 baton pass (oob -> ib) | ws2r -> ws3r | LOW | A only | 2026-10-27 00:40:25 | - | - | ws2r 17.57; ws3r 6.77 | ws2r 11.61; ws3r 7.34 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws2r -> ws3r | LOW | both | 2026-10-27 00:41:00 | 2026-10-27 00:42:00 | 60 | ws2r 23.93; ws3r 6.77 | ws2r 11.61; ws3r 7.34 | - | - | - | - | - | - |
| #3 Mage into oob | ws6Mage | HIGH | A only | 2026-10-27 00:41:15 | - | - | ws6Mage 85.55 | ws6Mage 89.27 | 110 | yes | yes | - | - | - |
| #3 Mage into oob | ws5Mage | HIGH | A only | 2026-10-27 00:41:40 | - | - | ws5Mage 85.44 | ws5Mage 81.18 | 85 | no | yes | - | - | - |
| #4 r into oob | ws11r | HIGH | A only | 2026-10-27 00:41:40 | - | - | ws11r 86.50 | ws11r 94.40 | 95 | no | yes | - | - | - |
| #2 baton pass (oob -> ib) | ws11r -> ws12r | HIGH | A only | 2026-10-27 00:43:15 | - | - | ws11r 84.72; ws12r 88.85 | ws11r 94.40; ws12r 93.91 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws11r -> ws12r | HIGH | both | 2026-10-27 00:44:00 | 2026-10-27 00:55:00 | 660 | ws11r 69.16; ws12r 87.63 | ws11r 83.45; ws12r 93.91 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws11r -> ws12r | HIGH | B only | - | 2026-10-27 00:44:00 | - | - | - | - | - | - | - | - | - |
| #3 Mage into oob | ws7Mage | HIGH | A only | 2026-10-27 00:44:30 | - | - | ws7Mage 85.07 | ws7Mage 93.30 | 5 | no | no | - | - | - |
| #3 Mage into oob | ws7Mage | HIGH | A only | 2026-10-27 00:44:40 | - | - | ws7Mage 85.29 | ws7Mage 93.30 | 15 | no | no | - | - | - |
| #3 Mage into oob | ws7Mage | HIGH | A only | 2026-10-27 00:45:00 | - | - | ws7Mage 85.07 | ws7Mage 93.30 | 5 | no | no | - | - | - |
| #3 Mage into oob | ws7Mage | HIGH | A only | 2026-10-27 00:45:15 | - | - | ws7Mage 85.07 | ws7Mage 93.30 | 90 | no | yes | - | - | - |
| #3 Mage into oob | ws8Mage | HIGH | A only | 2026-10-27 00:47:20 | - | - | ws8Mage 85.78 | ws8Mage 90.94 | 40 | yes | no | - | - | - |
| #4 r into oob | ws12r | HIGH | A only | 2026-10-27 00:47:20 | - | - | ws12r 85.03 | ws12r 93.91 | 40 | yes | no | - | - | - |
| #3 Mage into oob | ws9Mage | HIGH | A only | 2026-10-27 00:47:25 | - | - | ws9Mage 85.51 | ws9Mage 90.11 | 50 | no | no | - | - | - |
| #3 Mage into oob | ws12Mage | HIGH | A only | 2026-10-27 00:47:45 | - | - | ws12Mage 85.52 | ws12Mage 92.20 | 15 | yes | no | - | - | - |
| #3 Mage into oob | ws11Mage | HIGH | A only | 2026-10-27 00:47:45 | - | - | ws11Mage 86.52 | ws11Mage 89.18 | 25 | no | no | - | - | - |
| #3 Mage into oob | ws10Mage | HIGH | A only | 2026-10-27 00:49:10 | - | - | ws10Mage 86.36 | ws10Mage 95.29 | 50 | yes | no | - | - | - |
| #4 r into oob | ws5r | LOW | A only | 2026-10-27 00:50:20 | - | - | ws5r 14.65 | ws5r 28.94 | 120 | no | yes | - | - | - |
| #4 r into oob | ws5r | LOW | A only | 2026-10-27 00:53:15 | - | - | ws5r 14.65 | ws5r 28.94 | 55 | no | no | - | - | - |
| #1 ws1b oob -> ib | ws1b | LOW | A only | 2026-10-27 00:53:45 | - | - | ws1b 17.04 | ws1b 26.93 | 230 | yes | yes | - | - | - |
| #4 r into oob | ws6r | LOW | both | 2026-10-27 00:54:00 | 2026-10-27 01:00:00 | 360 | ws6r 10.70 | ws6r 24.06 | 745 | yes | yes | >= 1645 (run ended) | yes | yes |
| #2 baton pass (oob -> ib) | ws5r -> ws6r | LOW | A only | 2026-10-27 00:54:10 | - | - | ws5r 15.58; ws6r 11.26 | ws5r 28.94; ws6r 24.06 | - | - | - | - | - | - |
| #3 Mage into oob | ws10Mage | HIGH | A only | 2026-10-27 00:54:25 | - | - | ws10Mage 85.55 | ws10Mage 85.33 | 5 | no | no | - | - | - |
| #3 Mage into oob | ws10Mage | HIGH | A only | 2026-10-27 00:54:45 | - | - | ws10Mage 87.03 | ws10Mage 85.33 | 130 | no | yes | - | - | - |
| #3 Mage into oob | ws8Mage | HIGH | A only | 2026-10-27 00:55:00 | - | - | ws8Mage 85.09 | ws8Mage 88.34 | 25 | no | no | - | - | - |
| #3 Mage into oob | ws11Mage | HIGH | A only | 2026-10-27 00:55:00 | - | - | ws11Mage 85.76 | ws11Mage 84.00 | 35 | no | no | - | - | - |
| #4 r into oob | ws5r | LOW | both | 2026-10-27 00:55:00 | 2026-10-27 01:00:00 | 300 | ws5r 7.04 | ws5r 17.39 | 670 | yes | yes | 600 | yes | yes |
| #2 baton pass (oob -> ib) | ws4r -> ws5r | LOW | A only | 2026-10-27 00:56:15 | - | - | ws4r 15.05; ws5r 6.01 | ws4r 8.29; ws5r 17.39 | - | - | - | - | - | - |
| #3 Mage into oob | ws11Mage | HIGH | A only | 2026-10-27 00:56:20 | - | - | ws11Mage 85.54 | ws11Mage 84.00 | 25 | no | no | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws2r -> ws3r | LOW | A only | 2026-10-27 00:59:10 | - | - | ws2r 20.14; ws3r 6.05 | ws2r 24.80; ws3r 8.87 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws2r -> ws3r | LOW | A only | 2026-10-27 01:02:05 | - | - | ws2r 20.10; ws3r 6.38 | ws2r 15.42; ws3r 6.05 | - | - | - | - | - | - |
| #1 ws1b oob -> ib | ws1b | LOW | both | 2026-10-27 01:02:10 | 2026-10-27 01:03:00 | 50 | ws1b 16.31 | ws1b 8.59 | 930 | yes | yes | 1080 | yes | yes |
| #2 baton pass (oob -> ib) | ws4r -> ws5r | LOW | both | 2026-10-27 01:02:40 | 2026-10-27 01:04:00 | 80 | ws4r 15.39; ws5r 9.63 | ws4r 8.29; ws5r 3.11 | - | - | - | - | - | - |
| #4 r into oob | ws7r | LOW | both | 2026-10-27 01:03:00 | 2026-10-27 01:10:00 | 420 | ws7r 12.36 | ws7r 24.68 | >= 1465 (run ended) | yes | yes | >= 1045 (run ended) | yes | yes |
| #2 baton pass (oob -> ib) | ws3r -> ws4r | LOW | B only | - | 2026-10-27 01:03:00 | - | - | - | - | - | - | - | - | - |
| #3 Mage into oob | ws10Mage | HIGH | A only | 2026-10-27 01:03:15 | - | - | ws10Mage 85.88 | ws10Mage 75.55 | 10 | no | no | - | - | - |
| #4 r into oob | ws8r | LOW | A only | 2026-10-27 01:04:05 | - | - | ws8r 14.42 | ws8r 28.71 | 130 | yes | yes | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws4r -> ws5r | LOW | both | 2026-10-27 01:04:05 | 2026-10-27 01:08:00 | 235 | ws4r 24.93; ws5r 9.07 | ws4r 15.96; ws5r 3.11 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws5r -> ws6r | LOW | A only | 2026-10-27 01:06:10 | - | - | ws5r 15.85; ws6r 11.07 | ws5r 6.31; ws6r 4.87 | - | - | - | - | - | - |
| #3 Mage into oob | ws10Mage | HIGH | A only | 2026-10-27 01:06:20 | - | - | ws10Mage 87.34 | ws10Mage 75.55 | 45 | no | no | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws5r -> ws6r | LOW | A only | 2026-10-27 01:06:20 | - | - | ws5r 20.59; ws6r 14.78 | ws5r 6.31; ws6r 4.87 | - | - | - | - | - | - |
| #3 Mage into oob | ws11Mage | HIGH | A only | 2026-10-27 01:06:25 | - | - | ws11Mage 85.36 | ws11Mage 78.78 | 15 | no | no | - | - | - |
| #2 baton pass (oob -> ib) | ws6r -> ws7r | LOW | A only | 2026-10-27 01:06:25 | - | - | ws6r 15.30; ws7r 14.30 | ws6r 4.87; ws7r 24.68 | - | - | - | - | - | - |
| #4 r into oob | ws6r | LOW | A only | 2026-10-27 01:06:40 | - | - | ws6r 14.78 | ws6r 4.87 | 320 | yes | yes | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws5r -> ws6r | LOW | A only | 2026-10-27 01:06:50 | - | - | ws5r 20.16; ws6r 14.24 | ws5r 6.31; ws6r 4.87 | - | - | - | - | - | - |
| #4 r into oob | ws8r | LOW | A only | 2026-10-27 01:07:05 | - | - | ws8r 14.99 | ws8r 28.71 | 45 | yes | no | - | - | - |
| #4 r into oob | ws5r | LOW | A only | 2026-10-27 01:07:10 | - | - | ws5r 14.73 | ws5r 6.31 | 25 | no | no | - | - | - |
| #2 baton pass (oob -> ib) | ws5r -> ws6r | LOW | A only | 2026-10-27 01:07:35 | - | - | ws5r 15.85; ws6r 11.07 | ws5r 6.31; ws6r 4.87 | - | - | - | - | - | - |
| #4 r into oob | ws8r | LOW | A only | 2026-10-27 01:08:00 | - | - | ws8r 14.42 | ws8r 28.71 | 75 | yes | yes | - | - | - |
| #4 r into oob | ws5r | LOW | A only | 2026-10-27 01:08:05 | - | - | ws5r 13.21 | ws5r 6.31 | 65 | no | yes | - | - | - |
| #2 baton pass (oob -> ib) | ws5r -> ws6r | LOW | A only | 2026-10-27 01:09:10 | - | - | ws5r 16.11; ws6r 11.27 | ws5r 6.31; ws6r 4.87 | - | - | - | - | - | - |
| #4 r into oob | ws8r | LOW | both | 2026-10-27 01:09:20 | 2026-10-27 01:12:00 | 160 | ws8r 14.62 | ws8r 28.71 | >= 1085 (run ended) | yes | yes | >= 925 (run ended) | yes | yes |
| #4 r into oob | ws5r | LOW | A only | 2026-10-27 01:09:30 | - | - | ws5r 14.73 | ws5r 6.31 | 5 | no | no | - | - | - |
| #2 baton pass (oob -> ib) | ws5r -> ws6r | LOW | A only | 2026-10-27 01:09:35 | - | - | ws5r 16.11; ws6r 11.27 | ws5r 6.31; ws6r 4.87 | - | - | - | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws5r -> ws6r | LOW | both | 2026-10-27 01:10:00 | 2026-10-27 01:15:00 | 300 | ws5r 26.27; ws6r 10.67 | ws5r 16.11; ws6r 4.87 | - | - | - | - | - | - |
| #2 baton pass (oob -> ib) | ws5r -> ws6r | LOW | B only | - | 2026-10-27 01:10:00 | - | - | - | - | - | - | - | - | - |
| #4 r into oob | ws9r | LOW | A only | 2026-10-27 01:12:00 | - | - | ws9r 14.10 | ws9r 27.27 | 20 | yes | no | - | - | - |
| #2 baton pass (oob -> ib) | ws6r -> ws7r | LOW | A only | 2026-10-27 01:12:00 | - | - | ws6r 17.76; ws7r 8.80 | ws6r 10.67; ws7r 10.91 | - | - | - | - | - | - |
| #4 r into oob | ws9r | LOW | A only | 2026-10-27 01:12:25 | - | - | ws9r 14.26 | ws9r 27.27 | 160 | yes | yes | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws6r -> ws7r | LOW | A only | 2026-10-27 01:15:05 | - | - | ws6r 20.27; ws7r 11.63 | ws6r 10.67; ws7r 10.91 | - | - | - | - | - | - |
| #4 r into oob | ws9r | LOW | both | 2026-10-27 01:15:20 | 2026-10-27 01:21:00 | 340 | ws9r 14.72 | ws9r 27.27 | >= 725 (run ended) | yes | yes | >= 385 (run ended) | run ended | yes |
| #4 r into oob | ws6r | LOW | A only | 2026-10-27 01:16:40 | - | - | ws6r 14.64 | ws6r 10.67 | 95 | yes | yes | - | - | - |
| #1 ws1b oob -> ib | ws1b | LOW | A only | 2026-10-27 01:17:55 | - | - | ws1b 16.38 | ws1b 27.50 | 165 | yes | yes | - | - | - |
| #2 baton pass (oob -> ib) | ws6r -> ws7r | LOW | A only | 2026-10-27 01:18:15 | - | - | ws6r 16.75; ws7r 7.32 | ws6r 12.36; ws7r 7.32 | - | - | - | - | - | - |
| #4 r into oob | ws6r | LOW | A only | 2026-10-27 01:20:00 | - | - | ws6r 14.92 | ws6r 12.36 | 250 | yes | yes | - | - | - |
| #4 r into oob | ws10r | LOW | A only | 2026-10-27 01:20:25 | - | - | ws10r 14.75 | ws10r 28.69 | >= 420 (run ended) | run ended | yes | - | - | - |
| #2 baton pass (oob -> ib) | ws6r -> ws7r | LOW | A only | 2026-10-27 01:24:10 | - | - | ws6r 15.41; ws7r 6.22 | ws6r 11.19; ws7r 7.32 | - | - | - | - | - | - |
| #1 ws1b oob -> ib | ws1b | LOW | A only | 2026-10-27 01:24:15 | - | - | ws1b 15.05 | ws1b -6.34 | 5 | no | no | - | - | - |
| #1 ws1b oob -> ib | ws1b | LOW | A only | 2026-10-27 01:25:00 | - | - | ws1b 17.92 | ws1b 7.32 | 35 | no | no | - | - | - |
| #1 ws1b oob -> ib | ws1b | LOW | A only | 2026-10-27 01:25:45 | - | - | ws1b 17.32 | ws1b 7.32 | 10 | no | no | - | - | - |
| #1 ws1b oob -> ib | ws1b | LOW | A only | 2026-10-27 01:26:15 | - | - | ws1b 18.28 | ws1b 14.36 | 35 | no | no | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws6r -> ws7r | LOW | A only | 2026-10-27 01:26:20 | - | - | ws6r 21.00; ws7r 9.35 | ws6r 11.19; ws7r 7.32 | - | - | - | - | - | - |
| #1 ws1b oob -> ib | ws1b | LOW | A only | 2026-10-27 01:27:00 | - | - | ws1b 15.23 | ws1b 14.75 | >= 25 (run ended) | run ended | run ended | - | - | - |
| #2 baton pass (ex-fence -> in-fence) | ws6r -> ws7r | LOW | A only | 2026-10-27 01:27:10 | - | - | ws6r 20.03; ws7r 8.80 | ws6r 11.19; ws7r 7.32 | - | - | - | - | - | - |

## Every #1 firing with the r ladder, chronological

ws1r..ws12r at the firing bar, on the read that fired. H = at or above the high fence (80), L = at or below the low fence (20), - = neither. Both sides are shown: this harness has no trade side.

| bar | read | side left | ws1r | ws2r | ws3r | ws4r | ws5r | ws6r | ws7r | ws8r | ws9r | ws10r | ws11r | ws12r |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-26 21:34:55 | A | HIGH | 93.53 H | 86.78 H | 75.39 - | 68.05 - | 49.83 - | 52.48 - | 51.06 - | 24.69 - | 22.24 - | 31.58 - | 28.70 - | 37.92 - |
| 2026-10-26 21:41:00 | A | HIGH | 71.43 - | 91.37 H | 85.70 H | 86.58 H | 73.35 - | 66.45 - | 58.05 - | 38.97 - | 36.53 - | 37.50 - | 39.45 - | 40.40 - |
| 2026-10-26 21:42:00 | B | HIGH | 71.43 - | 89.67 H | 84.16 H | 75.82 - | 62.34 - | 66.45 - | 58.05 - | 24.69 - | 22.24 - | 31.58 - | 28.70 - | 37.92 - |
| 2026-10-26 21:43:00 | A | HIGH | 49.11 - | 78.05 - | 84.55 H | 87.19 H | 73.92 - | 80.73 H | 67.29 - | 38.97 - | 36.53 - | 38.09 - | 40.01 - | 40.40 - |
| 2026-10-26 21:44:00 | B | HIGH | 47.81 - | 77.35 - | 84.16 H | 86.70 H | 62.34 - | 66.45 - | 58.05 - | 38.97 - | 22.24 - | 31.58 - | 28.70 - | 37.92 - |
| 2026-10-26 21:45:00 | A | HIGH | 27.32 - | 67.54 - | 86.57 H | 83.63 H | 86.69 H | 80.73 H | 67.29 - | 47.32 - | 49.36 - | 38.46 - | 40.13 - | 40.40 - |
| 2026-10-26 21:46:00 | B | HIGH | 24.46 - | 64.79 - | 85.29 H | 86.70 H | 74.91 - | 66.45 - | 58.05 - | 38.97 - | 36.53 - | 31.58 - | 28.70 - | 37.92 - |
| 2026-10-26 21:51:00 | A | HIGH | 51.94 - | 38.19 - | 78.29 - | 86.89 H | 89.83 H | 85.63 H | 80.00 H | 47.32 - | 49.96 - | 54.67 - | 53.84 - | 41.19 - |
| 2026-10-26 21:51:15 | A | HIGH | 54.24 - | 39.51 - | 79.81 - | 87.42 H | 90.51 H | 86.00 H | 80.42 H | 47.32 - | 49.96 - | 55.21 - | 54.18 - | 41.52 - |
| 2026-10-26 21:51:55 | A | HIGH | 52.67 - | 38.62 - | 78.79 - | 87.07 H | 90.05 H | 85.75 H | 80.14 H | 47.32 - | 49.96 - | 54.85 - | 53.95 - | 41.30 - |
| 2026-10-26 21:52:00 | B | HIGH | 52.67 - | 38.62 - | 85.87 H | 87.07 H | 88.84 H | 80.73 H | 67.29 - | 47.32 - | 36.53 - | 40.92 - | 40.13 - | 40.40 - |
| 2026-10-26 22:31:25 | A | LOW | 15.93 L | 61.52 - | 53.21 - | 20.48 - | 24.37 - | 19.09 L | 33.47 - | 59.90 - | 66.31 - | 55.75 - | 69.55 - | 59.16 - |
| 2026-10-26 22:32:05 | A | LOW | 17.88 L | 50.10 - | 52.69 - | 22.78 - | 23.75 - | 19.09 L | 32.92 - | 46.50 - | 66.31 - | 55.75 - | 69.35 - | 58.98 - |
| 2026-10-26 22:33:00 | B | LOW | 20.43 - | 61.52 - | 53.21 - | 20.48 - | 26.12 - | 28.71 - | 46.82 - | 59.90 - | 80.59 H | 65.03 - | 69.55 - | 53.54 - |
| 2026-10-26 23:07:20 | A | LOW | 19.63 L | 26.10 - | 44.78 - | 55.62 - | 52.29 - | 28.58 - | 36.76 - | 31.03 - | 25.27 - | 28.47 - | 40.49 - | 41.76 - |
| 2026-10-26 23:08:00 | B | LOW | 19.63 L | 25.29 - | 51.91 - | 54.93 - | 55.18 - | 22.08 - | 34.71 - | 30.64 - | 26.45 - | 36.69 - | 43.50 - | 56.04 - |
| 2026-10-26 23:31:00 | A | HIGH | 76.92 - | 89.03 H | 95.28 H | 78.85 - | 76.31 - | 78.17 - | 70.90 - | 63.38 - | 42.74 - | 52.37 - | 54.41 - | 52.46 - |
| 2026-10-26 23:32:00 | A | HIGH | 79.43 - | 82.56 H | 93.72 H | 87.55 H | 75.71 - | 77.64 - | 70.90 - | 63.38 - | 42.74 - | 51.69 - | 54.41 - | 52.46 - |
| 2026-10-26 23:33:00 | B | HIGH | 74.33 - | 89.03 H | 91.40 H | 78.85 - | 76.31 - | 63.89 - | 62.39 - | 53.28 - | 42.74 - | 42.72 - | 49.18 - | 45.33 - |
| 2026-10-26 23:45:50 | A | HIGH | 23.85 - | 72.51 - | 95.35 H | 95.77 H | 97.72 H | 92.46 H | 77.57 - | 79.10 - | 69.38 - | 63.71 - | 62.85 - | 57.76 - |
| 2026-10-26 23:46:00 | A | HIGH | 16.55 L | 64.21 - | 96.12 H | 98.01 H | 98.37 H | 92.46 H | 77.57 - | 79.80 - | 69.38 - | 64.13 - | 62.85 - | 57.76 - |
| 2026-10-26 23:46:20 | A | HIGH | 17.32 L | 64.62 - | 96.12 H | 98.01 H | 98.44 H | 92.46 H | 77.57 - | 79.80 - | 69.38 - | 64.13 - | 62.85 - | 57.76 - |
| 2026-10-26 23:46:50 | A | HIGH | 15.72 L | 63.78 - | 96.12 H | 97.54 H | 98.30 H | 92.46 H | 77.57 - | 79.66 - | 69.38 - | 64.13 - | 62.85 - | 57.76 - |
| 2026-10-26 23:47:00 | A | HIGH | 23.78 - | 66.77 - | 96.12 H | 98.01 H | 98.64 H | 92.46 H | 77.57 - | 79.80 - | 69.38 - | 64.13 - | 62.85 - | 57.76 - |
| 2026-10-26 23:48:35 | A | HIGH | 34.39 - | 54.89 - | 94.28 H | 99.03 H | 98.64 H | 97.37 H | 91.57 H | 79.80 - | 69.38 - | 64.13 - | 62.85 - | 64.42 - |
| 2026-10-26 23:49:00 | B | HIGH | 29.23 - | 68.48 - | 96.12 H | 98.01 H | 96.22 H | 92.46 H | 77.57 - | 73.18 - | 57.03 - | 52.37 - | 54.41 - | 57.76 - |
| 2026-10-27 00:10:00 | A | HIGH | 56.63 - | 55.93 - | 44.71 - | 74.96 - | 93.60 H | 95.35 H | 95.76 H | 100.00 H | 100.00 H | 99.54 H | 82.60 H | 71.88 - |
| 2026-10-27 00:11:00 | B | HIGH | 53.31 - | 48.35 - | 34.39 - | 74.96 - | 97.97 H | 95.35 H | 93.95 H | 100.00 H | 97.95 H | 85.71 H | 82.60 H | 64.72 - |
| 2026-10-27 00:14:50 | A | HIGH | 77.23 - | 69.48 - | 44.24 - | 65.21 - | 97.97 H | 86.23 H | 90.56 H | 100.00 H | 100.00 H | 100.00 H | 96.89 H | 82.26 H |
| 2026-10-27 00:15:00 | A | HIGH | 62.95 - | 68.06 - | 46.46 - | 63.14 - | 90.17 H | 84.21 H | 89.49 H | 100.00 H | 100.00 H | 100.00 H | 96.89 H | 81.91 H |
| 2026-10-27 00:26:25 | A | HIGH | 19.76 L | 39.15 - | 47.79 - | 85.02 H | 89.43 H | 81.47 H | 95.76 H | 98.34 H | 97.63 H | 100.00 H | 98.50 H | 97.71 H |
| 2026-10-27 00:27:00 | B | HIGH | 19.76 L | 53.43 - | 46.81 - | 82.66 H | 98.84 H | 89.51 H | 95.76 H | 100.00 H | 93.42 H | 100.00 H | 96.89 H | 83.83 H |
| 2026-10-27 00:53:45 | A | LOW | 35.47 - | 31.75 - | 4.28 L | 2.59 L | 14.65 L | 24.06 - | 35.58 - | 43.00 - | 54.77 - | 52.76 - | 69.16 - | 72.11 - |
| 2026-10-27 01:02:10 | A | LOW | 20.95 - | 22.73 - | 7.99 L | 10.73 L | 5.32 L | 2.64 L | 23.74 - | 28.71 - | 40.48 - | 39.51 - | 54.88 - | 58.66 - |
| 2026-10-27 01:03:00 | B | LOW | 26.76 - | 15.42 L | 15.14 L | 8.29 L | 3.11 L | 9.77 L | 24.68 - | 43.00 - | 41.47 - | 52.76 - | 69.16 - | 72.11 - |
| 2026-10-27 01:17:55 | A | LOW | 32.79 - | 74.77 - | 66.37 - | 51.00 - | 30.41 - | 12.36 L | 7.32 L | 0.14 L | 12.98 L | 27.73 - | 26.31 - | 46.14 - |
| 2026-10-27 01:24:15 | A | LOW | 36.94 - | 40.82 - | 54.96 - | 56.61 - | 32.78 - | 19.21 L | 8.34 L | 0.14 L | 5.28 L | 14.41 L | 26.31 - | 34.19 - |
| 2026-10-27 01:25:00 | A | LOW | 35.63 - | 41.04 - | 55.19 - | 56.83 - | 35.29 - | 19.42 L | 8.46 L | 0.14 L | 5.28 L | 14.41 L | 26.31 - | 34.26 - |
| 2026-10-27 01:25:45 | A | LOW | 35.46 - | 40.82 - | 54.96 - | 56.61 - | 34.96 - | 19.21 L | 8.34 L | 0.14 L | 5.28 L | 14.41 L | 26.31 - | 34.19 - |
| 2026-10-27 01:26:15 | A | LOW | 39.91 - | 35.75 - | 54.73 - | 56.38 - | 34.62 - | 19.00 L | 8.22 L | 0.14 L | 5.28 L | 14.41 L | 26.31 - | 34.12 - |
| 2026-10-27 01:27:00 | A | LOW | 50.14 - | 34.10 - | 49.39 - | 54.69 - | 32.08 - | 17.42 L | 7.34 L | 0.14 L | 5.28 L | 14.41 L | 26.31 - | 33.62 - |

## Every pass bar of ws1r..ws11r, both reads, chronological

Rung scan: every rung above the handing line, as `line value ex-fence/towards` (y/n). The full scan is in out/events.jsonl. Reversals are on the EMERGING series in both reads, raw bar and stamp kept apart.

| bar | read | handing line | side | why | receiver | rung scan | handing rev raw | handing rev stamp | receiver rev raw | receiver rev stamp |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-26 21:28:15 | A | ws8r | LOW | oob -> ib | ws9r | ws9r 18.72 y/y; ws10r 19.21 y/y; ws11r 27.31 n/y; ws12r 27.50 n/y | 2026-10-26 21:20:10 | 2026-10-26 21:20:45 | 2026-10-26 21:18:45 | 2026-10-26 21:19:20 |
| 2026-10-26 21:28:40 | A | ws10r | LOW | ex-fence -> in-fence | none | ws11r 28.70 n/y; ws12r 29.97 n/y | 2026-10-26 21:28:05 | 2026-10-26 21:28:40 | - | - |
| 2026-10-26 21:28:45 | A | ws8r | LOW | ex-fence -> in-fence | none | ws9r 20.74 n/y; ws10r 23.59 n/y; ws11r 28.70 n/y; ws12r 31.81 n/y | 2026-10-26 21:28:00 | 2026-10-26 21:28:35 | - | - |
| 2026-10-26 21:28:45 | A | ws9r | LOW | ex-fence -> in-fence | none | ws10r 23.59 n/y; ws11r 28.70 n/y; ws12r 31.81 n/y | 2026-10-26 21:28:00 | 2026-10-26 21:28:35 | - | - |
| 2026-10-26 21:30:00 | B | ws10r | LOW | ex-fence -> in-fence | none | ws11r 22.34 n/y; ws12r 31.17 n/y | 2026-10-26 21:28:05 | 2026-10-26 21:28:40 | - | - |
| 2026-10-26 21:30:15 | A | ws2r | HIGH | oob -> ib | none | ws3r 62.09 n/y; ws4r 53.76 n/y; ws5r 48.33 n/y; ws6r 51.36 n/y; ws7r 51.06 n/y; ws8r 22.01 n/y; ws9r 20.74 n/y; ws10r 24.44 n/y; ws11r 28.70 n/y; ws12r 31.81 n/n | 2026-10-26 21:23:00 | 2026-10-26 21:23:35 | - | - |
| 2026-10-26 21:32:00 | A | ws2r | HIGH | oob -> ib | none | ws3r 63.21 n/y; ws4r 68.05 n/y; ws5r 49.56 n/y; ws6r 52.29 n/y; ws7r 51.06 n/y; ws8r 24.24 n/y; ws9r 21.55 n/y; ws10r 26.19 n/y; ws11r 28.70 n/y; ws12r 33.47 n/n | 2026-10-26 21:23:00 | 2026-10-26 21:23:35 | - | - |
| 2026-10-26 21:36:00 | B | ws8r | LOW | oob -> ib + ex-fence -> in-fence | none | ws9r 22.24 n/y; ws10r 27.10 n/y; ws11r 22.34 n/y; ws12r 37.92 n/y | 2026-10-26 21:28:00 | 2026-10-26 21:28:35 | - | - |
| 2026-10-26 21:36:00 | B | ws9r | LOW | ex-fence -> in-fence | none | ws10r 27.10 n/y; ws11r 22.34 n/y; ws12r 37.92 n/y | 2026-10-26 21:28:00 | 2026-10-26 21:28:35 | - | - |
| 2026-10-26 21:41:00 | A | ws1r | HIGH | oob -> ib + ex-fence -> in-fence | ws2r | ws2r 91.37 y/y; ws3r 85.70 y/y; ws4r 86.58 y/y; ws5r 73.35 n/y; ws6r 66.45 n/y; ws7r 58.05 n/y; ws8r 38.97 n/y; ws9r 36.53 n/y; ws10r 37.50 n/y; ws11r 39.45 n/y; ws12r 40.40 n/y | 2026-10-26 21:40:00 | 2026-10-26 21:40:35 | 2026-10-26 21:23:00 | 2026-10-26 21:23:35 |
| 2026-10-26 21:41:35 | A | ws3r | HIGH | oob -> ib | ws4r | ws4r 85.69 y/y; ws5r 72.51 n/y; ws6r 66.45 n/y; ws7r 58.05 n/y; ws8r 38.97 n/y; ws9r 36.53 n/y; ws10r 36.64 n/y; ws11r 38.61 n/y; ws12r 40.40 n/y | 2026-10-26 21:40:30 | 2026-10-26 21:41:05 | 2026-10-26 21:23:00 | 2026-10-26 21:23:35 |
| 2026-10-26 21:42:00 | A | ws2r | HIGH | oob -> ib + ex-fence -> in-fence | ws3r | ws3r 82.68 y/y; ws4r 85.49 y/y; ws5r 72.31 n/y; ws6r 80.39 y/y; ws7r 66.96 n/y; ws8r 38.97 n/y; ws9r 36.53 n/y; ws10r 36.44 n/y; ws11r 38.41 n/y; ws12r 40.40 n/y | 2026-10-26 21:40:30 | 2026-10-26 21:41:05 | 2026-10-26 21:40:30 | 2026-10-26 21:41:05 |
| 2026-10-26 21:42:00 | B | ws1r | HIGH | oob -> ib + ex-fence -> in-fence | ws2r | ws2r 89.67 y/y; ws3r 84.16 y/y; ws4r 75.82 n/y; ws5r 62.34 n/y; ws6r 66.45 n/y; ws7r 58.05 n/y; ws8r 24.69 n/y; ws9r 22.24 n/y; ws10r 31.58 n/y; ws11r 28.70 n/y; ws12r 37.92 n/y | 2026-10-26 21:40:00 | 2026-10-26 21:40:35 | 2026-10-26 21:40:30 | 2026-10-26 21:41:05 |
| 2026-10-26 21:42:00 | B | ws3r | HIGH | oob -> ib | none | ws4r 75.82 n/y; ws5r 62.34 n/y; ws6r 66.45 n/y; ws7r 58.05 n/y; ws8r 24.69 n/y; ws9r 22.24 n/y; ws10r 31.58 n/y; ws11r 28.70 n/y; ws12r 37.92 n/y | 2026-10-26 21:40:30 | 2026-10-26 21:41:05 | - | - |
| 2026-10-26 21:42:05 | A | ws4r | HIGH | oob -> ib | none | ws5r 71.75 n/y; ws6r 79.43 n/y; ws7r 66.03 n/y; ws8r 38.79 n/y; ws9r 36.41 n/y; ws10r 35.86 n/y; ws11r 37.85 n/y; ws12r 40.23 n/y | 2026-10-26 21:23:00 | 2026-10-26 21:23:35 | - | - |
| 2026-10-26 21:42:05 | A | ws6r | HIGH | ex-fence -> in-fence | none | ws7r 66.03 n/y; ws8r 38.79 n/y; ws9r 36.41 n/y; ws10r 35.86 n/y; ws11r 37.85 n/y; ws12r 40.23 n/y | 2026-10-26 21:13:00 | 2026-10-26 21:13:35 | - | - |
| 2026-10-26 21:44:00 | A | ws4r | HIGH | oob -> ib | none | ws5r 73.24 n/y; ws6r 80.73 y/y; ws7r 67.29 n/y; ws8r 46.94 n/y; ws9r 36.53 n/y; ws10r 37.39 n/y; ws11r 39.34 n/y; ws12r 40.40 n/y | 2026-10-26 21:23:00 | 2026-10-26 21:23:35 | - | - |
| 2026-10-26 21:44:00 | B | ws2r | HIGH | oob -> ib + ex-fence -> in-fence | ws3r | ws3r 84.16 y/y; ws4r 86.70 y/y; ws5r 62.34 n/y; ws6r 66.45 n/y; ws7r 58.05 n/y; ws8r 38.97 n/y; ws9r 22.24 n/y; ws10r 31.58 n/y; ws11r 28.70 n/y; ws12r 37.92 n/y | 2026-10-26 21:40:30 | 2026-10-26 21:41:05 | 2026-10-26 21:40:30 | 2026-10-26 21:41:05 |
| 2026-10-26 21:45:25 | A | ws3r | HIGH | oob -> ib | ws4r | ws4r 82.73 y/y; ws5r 85.56 y/y; ws6r 80.73 y/y; ws7r 67.29 n/y; ws8r 47.13 n/y; ws9r 48.48 n/y; ws10r 37.50 n/y; ws11r 39.45 n/y; ws12r 40.40 n/y | 2026-10-26 21:40:30 | 2026-10-26 21:41:05 | 2026-10-26 21:44:00 | 2026-10-26 21:44:35 |
| 2026-10-26 21:45:40 | A | ws3r | HIGH | oob -> ib | ws4r | ws4r 82.33 y/y; ws5r 85.30 y/y; ws6r 80.73 y/y; ws7r 67.29 n/y; ws8r 46.76 n/y; ws9r 48.27 n/y; ws10r 37.28 n/y; ws11r 39.23 n/y; ws12r 40.40 n/y | 2026-10-26 21:40:30 | 2026-10-26 21:41:05 | 2026-10-26 21:44:00 | 2026-10-26 21:44:35 |
| 2026-10-26 21:46:50 | A | ws1r | LOW | oob -> ib | none | ws2r 56.96 n/y; ws3r 89.15 n/y; ws4r 85.16 n/y; ws5r 88.34 n/n; ws6r 80.73 n/n; ws7r 67.29 n/n; ws8r 47.32 n/n; ws9r 49.96 n/n; ws10r 40.92 n/n; ws11r 40.13 n/n; ws12r 40.40 n/n | 2026-10-26 21:37:55 | 2026-10-26 21:38:30 | - | - |
| 2026-10-26 21:47:00 | A | ws1r | LOW | ex-fence -> in-fence | none | ws2r 56.52 n/y; ws3r 88.89 n/y; ws4r 84.95 n/y; ws5r 88.17 n/n; ws6r 80.73 n/n; ws7r 67.29 n/n; ws8r 47.32 n/n; ws9r 49.96 n/n; ws10r 40.76 n/n; ws11r 40.13 n/n; ws12r 40.40 n/n | 2026-10-26 21:37:55 | 2026-10-26 21:38:30 | - | - |
| 2026-10-26 21:47:00 | A | ws4r | HIGH | oob -> ib | ws5r | ws5r 88.17 y/y; ws6r 80.73 y/y; ws7r 67.29 n/y; ws8r 47.32 n/y; ws9r 49.96 n/y; ws10r 40.76 n/y; ws11r 40.13 n/y; ws12r 40.40 n/y | 2026-10-26 21:44:00 | 2026-10-26 21:44:35 | 2026-10-26 21:23:00 | 2026-10-26 21:23:35 |
| 2026-10-26 21:48:00 | B | ws1r | LOW | ex-fence -> in-fence | none | ws2r 59.37 n/y; ws3r 90.67 n/n; ws4r 86.44 n/y; ws5r 74.91 n/n; ws6r 80.73 n/n; ws7r 58.05 n/n; ws8r 38.97 n/n; ws9r 36.53 n/n; ws10r 31.58 n/n; ws11r 28.70 n/y; ws12r 40.40 n/y | 2026-10-26 21:46:40 | 2026-10-26 21:47:15 | - | - |
| 2026-10-26 21:48:40 | A | ws3r | HIGH | oob -> ib | ws4r | ws4r 86.72 y/y; ws5r 88.65 y/y; ws6r 85.51 y/y; ws7r 67.29 n/y; ws8r 47.32 n/y; ws9r 49.96 n/y; ws10r 40.92 n/y; ws11r 40.13 n/y; ws12r 41.08 n/y | 2026-10-26 21:48:00 | 2026-10-26 21:48:35 | 2026-10-26 21:44:00 | 2026-10-26 21:44:35 |
| 2026-10-26 21:49:20 | A | ws3r | HIGH | oob -> ib | ws4r | ws4r 86.55 y/y; ws5r 88.60 y/y; ws6r 85.39 y/y; ws7r 79.74 n/y; ws8r 47.32 n/y; ws9r 49.96 n/y; ws10r 40.92 n/y; ws11r 53.62 n/y; ws12r 40.98 n/y | 2026-10-26 21:48:00 | 2026-10-26 21:48:35 | 2026-10-26 21:44:00 | 2026-10-26 21:44:35 |
| 2026-10-26 21:49:20 | A | ws7r | HIGH | ex-fence -> in-fence | none | ws8r 47.32 n/y; ws9r 49.96 n/y; ws10r 40.92 n/y; ws11r 53.62 n/y; ws12r 40.98 n/y | 2026-10-26 21:25:45 | 2026-10-26 21:26:20 | - | - |
| 2026-10-26 21:51:00 | A | ws3r | HIGH | oob -> ib + ex-fence -> in-fence | ws4r | ws4r 86.89 y/y; ws5r 89.83 y/y; ws6r 85.63 y/y; ws7r 80.00 y/y; ws8r 47.32 n/y; ws9r 49.96 n/y; ws10r 54.67 n/y; ws11r 53.84 n/y; ws12r 41.19 n/y | 2026-10-26 21:48:00 | 2026-10-26 21:48:35 | 2026-10-26 21:44:00 | 2026-10-26 21:44:35 |
| 2026-10-26 21:51:15 | A | ws3r | HIGH | ex-fence -> in-fence | ws4r | ws4r 87.42 y/y; ws5r 90.51 y/y; ws6r 86.00 y/y; ws7r 80.42 y/y; ws8r 47.32 n/y; ws9r 49.96 n/y; ws10r 55.21 n/y; ws11r 54.18 n/y; ws12r 41.52 n/y | 2026-10-26 21:48:00 | 2026-10-26 21:48:35 | 2026-10-26 21:44:00 | 2026-10-26 21:44:35 |
| 2026-10-26 21:51:55 | A | ws3r | HIGH | ex-fence -> in-fence | ws4r | ws4r 87.07 y/y; ws5r 90.05 y/y; ws6r 85.75 y/y; ws7r 80.14 y/y; ws8r 47.32 n/y; ws9r 49.96 n/y; ws10r 54.85 n/y; ws11r 53.95 n/y; ws12r 41.30 n/y | 2026-10-26 21:48:00 | 2026-10-26 21:48:35 | 2026-10-26 21:44:00 | 2026-10-26 21:44:35 |
| 2026-10-26 21:52:00 | A | ws7r | HIGH | ex-fence -> in-fence | none | ws8r 56.47 n/y; ws9r 49.96 n/y; ws10r 54.16 n/y; ws11r 53.51 n/y; ws12r 40.87 n/y | 2026-10-26 21:25:45 | 2026-10-26 21:26:20 | - | - |
| 2026-10-26 21:52:05 | A | ws6r | HIGH | oob -> ib | none | ws7r 79.23 n/y; ws8r 55.99 n/y; ws9r 49.96 n/y; ws10r 53.67 n/y; ws11r 53.19 n/y; ws12r 40.56 n/y | 2026-10-26 21:13:00 | 2026-10-26 21:13:35 | - | - |
| 2026-10-26 21:52:15 | A | ws4r | HIGH | oob -> ib | ws5r | ws5r 87.24 y/y; ws6r 84.17 y/y; ws7r 78.39 n/y; ws8r 54.96 n/y; ws9r 49.96 n/y; ws10r 52.63 n/y; ws11r 52.49 n/y; ws12r 39.88 n/y | 2026-10-26 21:44:00 | 2026-10-26 21:44:35 | 2026-10-26 21:23:00 | 2026-10-26 21:23:35 |
| 2026-10-26 21:52:35 | A | ws4r | HIGH | oob -> ib | ws5r | ws5r 87.24 y/y; ws6r 84.17 y/y; ws7r 78.39 n/y; ws8r 54.96 n/y; ws9r 49.96 n/y; ws10r 52.63 n/y; ws11r 52.49 n/y; ws12r 39.88 n/y | 2026-10-26 21:44:00 | 2026-10-26 21:44:35 | 2026-10-26 21:23:00 | 2026-10-26 21:23:35 |
| 2026-10-26 21:52:50 | A | ws4r | HIGH | oob -> ib | ws5r | ws5r 85.90 y/y; ws6r 83.38 y/y; ws7r 77.53 n/y; ws8r 53.93 n/y; ws9r 49.96 n/y; ws10r 51.57 n/y; ws11r 51.75 n/y; ws12r 39.16 n/y | 2026-10-26 21:52:10 | 2026-10-26 21:52:45 | 2026-10-26 21:52:05 | 2026-10-26 21:52:40 |
| 2026-10-26 21:53:00 | A | ws5r | HIGH | oob -> ib | ws6r | ws6r 82.17 y/y; ws7r 76.20 n/y; ws8r 52.38 n/y; ws9r 48.37 n/y; ws10r 50.00 n/y; ws11r 50.61 n/y; ws12r 38.04 n/y | 2026-10-26 21:52:05 | 2026-10-26 21:52:40 | 2026-10-26 21:13:00 | 2026-10-26 21:13:35 |
| 2026-10-26 21:53:15 | A | ws6r | HIGH | oob -> ib | none | ws7r 78.51 n/y; ws8r 55.10 n/y; ws9r 49.96 n/y; ws10r 52.77 n/y; ws11r 52.59 n/y; ws12r 39.97 n/y | 2026-10-26 21:13:00 | 2026-10-26 21:13:35 | - | - |
| 2026-10-26 21:53:15 | A | ws7r | HIGH | ex-fence -> in-fence | none | ws8r 55.10 n/y; ws9r 49.96 n/y; ws10r 52.77 n/y; ws11r 52.59 n/y; ws12r 39.97 n/y | 2026-10-26 21:25:45 | 2026-10-26 21:26:20 | - | - |
| 2026-10-26 21:53:20 | A | ws4r | HIGH | oob -> ib | ws5r | ws5r 86.55 y/y; ws6r 83.77 y/y; ws7r 77.95 n/y; ws8r 54.43 n/y; ws9r 49.96 n/y; ws10r 52.08 n/y; ws11r 52.11 n/y; ws12r 39.51 n/y | 2026-10-26 21:52:10 | 2026-10-26 21:52:45 | 2026-10-26 21:52:05 | 2026-10-26 21:52:40 |
| 2026-10-26 21:53:40 | A | ws5r | HIGH | oob -> ib | ws6r | ws6r 82.84 y/y; ws7r 76.93 n/y; ws8r 53.22 n/y; ws9r 49.24 n/y; ws10r 50.86 n/y; ws11r 51.24 n/y; ws12r 38.66 n/y | 2026-10-26 21:52:05 | 2026-10-26 21:52:40 | 2026-10-26 21:13:00 | 2026-10-26 21:13:35 |
| 2026-10-26 21:54:00 | B | ws3r | HIGH | oob -> ib + ex-fence -> in-fence | ws4r | ws4r 87.07 y/y; ws5r 88.84 y/y; ws6r 82.84 y/y; ws7r 67.29 n/y; ws8r 47.32 n/y; ws9r 49.24 n/y; ws10r 40.92 n/y; ws11r 40.13 n/y; ws12r 40.40 n/y | 2026-10-26 21:48:00 | 2026-10-26 21:48:35 | 2026-10-26 21:53:15 | 2026-10-26 21:53:50 |
| 2026-10-26 21:55:30 | A | ws5r | HIGH | oob -> ib | ws6r | ws6r 89.54 y/y; ws7r 75.94 n/y; ws8r 52.09 n/y; ws9r 61.37 n/y; ws10r 49.70 n/y; ws11r 50.38 n/y; ws12r 37.82 n/y | 2026-10-26 21:53:15 | 2026-10-26 21:53:50 | 2026-10-26 21:53:20 | 2026-10-26 21:53:55 |
| 2026-10-26 21:56:00 | B | ws4r | HIGH | oob -> ib | ws5r | ws5r 85.14 y/y; ws6r 82.84 y/y; ws7r 75.94 n/y; ws8r 47.32 n/y; ws9r 49.24 n/y; ws10r 40.92 n/y; ws11r 40.13 n/y; ws12r 40.40 n/y | 2026-10-26 21:53:15 | 2026-10-26 21:53:50 | 2026-10-26 21:53:15 | 2026-10-26 21:53:50 |
| 2026-10-26 21:56:30 | A | ws4r | HIGH | ex-fence -> in-fence | ws5r | ws5r 84.14 y/y; ws6r 89.45 y/y; ws7r 85.36 y/y; ws8r 51.99 n/y; ws9r 61.25 n/y; ws10r 49.61 n/y; ws11r 50.31 n/y; ws12r 37.74 n/y | 2026-10-26 21:53:15 | 2026-10-26 21:53:50 | 2026-10-26 21:53:15 | 2026-10-26 21:53:50 |
| 2026-10-26 21:57:25 | A | ws7r | HIGH | oob -> ib | none | ws8r 51.53 n/y; ws9r 60.68 n/y; ws10r 49.14 n/y; ws11r 49.95 n/y; ws12r 37.39 n/y | 2026-10-26 21:53:20 | 2026-10-26 21:53:55 | - | - |
| 2026-10-26 21:58:05 | A | ws7r | HIGH | oob -> ib | none | ws8r 51.44 n/y; ws9r 60.57 n/y; ws10r 49.05 n/y; ws11r 49.88 n/y; ws12r 37.33 n/y | 2026-10-26 21:53:20 | 2026-10-26 21:53:55 | - | - |
| 2026-10-26 21:59:35 | A | ws7r | HIGH | oob -> ib | none | ws8r 51.53 n/y; ws9r 60.68 n/y; ws10r 49.14 n/y; ws11r 49.95 n/y; ws12r 37.39 n/y | 2026-10-26 21:53:20 | 2026-10-26 21:53:55 | - | - |
| 2026-10-26 22:00:00 | A | ws5r | HIGH | ex-fence -> in-fence | none | ws6r 79.70 n/y; ws7r 84.95 y/y; ws8r 60.30 n/y; ws9r 60.79 n/y; ws10r 57.46 n/y; ws11r 54.59 n/y; ws12r 46.29 n/y | 2026-10-26 21:53:15 | 2026-10-26 21:53:50 | - | - |
| 2026-10-26 22:00:00 | A | ws6r | HIGH | oob -> ib + ex-fence -> in-fence | ws7r | ws7r 84.95 y/y; ws8r 60.30 n/y; ws9r 60.79 n/y; ws10r 57.46 n/y; ws11r 54.59 n/y; ws12r 46.29 n/y | 2026-10-26 21:53:20 | 2026-10-26 21:53:55 | 2026-10-26 21:53:20 | 2026-10-26 21:53:55 |
| 2026-10-26 22:00:00 | B | ws4r | HIGH | ex-fence -> in-fence | ws5r | ws5r 83.43 y/y; ws6r 89.00 y/y; ws7r 75.94 n/y; ws8r 51.53 n/y; ws9r 49.24 n/y; ws10r 49.14 n/y; ws11r 49.95 n/y; ws12r 37.39 n/y | 2026-10-26 21:53:15 | 2026-10-26 21:53:50 | 2026-10-26 21:53:15 | 2026-10-26 21:53:50 |
| 2026-10-26 22:00:00 | B | ws5r | HIGH | oob -> ib | ws6r | ws6r 89.00 y/y; ws7r 75.94 n/y; ws8r 51.53 n/y; ws9r 49.24 n/y; ws10r 49.14 n/y; ws11r 49.95 n/y; ws12r 37.39 n/y | 2026-10-26 21:53:15 | 2026-10-26 21:53:50 | 2026-10-26 21:53:20 | 2026-10-26 21:53:55 |
| 2026-10-26 22:01:05 | A | ws1r | LOW | oob -> ib | ws2r | ws2r 7.82 y/y; ws3r 34.24 n/y; ws4r 52.75 n/y; ws5r 69.14 n/y; ws6r 78.64 n/y; ws7r 84.29 n/n; ws8r 59.57 n/n; ws9r 60.05 n/n; ws10r 56.72 n/n; ws11r 54.01 n/n; ws12r 45.72 n/n | 2026-10-26 21:59:15 | 2026-10-26 21:59:50 | 2026-10-26 21:46:40 | 2026-10-26 21:47:15 |
| 2026-10-26 22:02:00 | A | ws1r | LOW | ex-fence -> in-fence | ws2r | ws2r 4.74 y/y; ws3r 34.55 n/y; ws4r 52.98 n/y; ws5r 69.40 n/y; ws6r 79.70 n/y; ws7r 84.95 n/n; ws8r 60.30 n/n; ws9r 60.79 n/y; ws10r 57.46 n/n; ws11r 54.59 n/n; ws12r 46.29 n/n | 2026-10-26 22:01:05 | 2026-10-26 22:01:40 | 2026-10-26 21:46:40 | 2026-10-26 21:47:15 |
| 2026-10-26 22:02:00 | B | ws1r | LOW | oob -> ib | ws2r | ws2r 7.82 y/y; ws3r 43.01 n/y; ws4r 67.04 n/y; ws5r 83.43 n/y; ws6r 89.00 n/n; ws7r 75.94 n/n; ws8r 51.53 n/n; ws9r 49.24 n/n; ws10r 49.14 n/n; ws11r 49.95 n/n; ws12r 37.39 n/y | 2026-10-26 22:01:05 | 2026-10-26 22:01:40 | 2026-10-26 21:46:40 | 2026-10-26 21:47:15 |
| 2026-10-26 22:03:00 | B | ws1r | LOW | ex-fence -> in-fence | ws2r | ws2r 7.82 y/y; ws3r 39.60 n/y; ws4r 67.04 n/y; ws5r 83.43 n/y; ws6r 89.00 n/n; ws7r 86.60 n/n; ws8r 51.53 n/n; ws9r 63.18 n/n; ws10r 49.14 n/n; ws11r 49.95 n/n; ws12r 37.39 n/y | 2026-10-26 22:01:05 | 2026-10-26 22:01:40 | 2026-10-26 22:02:15 | 2026-10-26 22:02:50 |
| 2026-10-26 22:03:05 | A | ws7r | HIGH | oob -> ib | none | ws8r 61.61 n/y; ws9r 76.28 n/y; ws10r 58.78 n/y; ws11r 55.63 n/y; ws12r 47.39 n/y | 2026-10-26 22:00:15 | 2026-10-26 22:00:50 | - | - |
| 2026-10-26 22:03:25 | A | ws7r | HIGH | ex-fence -> in-fence | none | ws8r 61.23 n/y; ws9r 75.52 n/y; ws10r 58.40 n/y; ws11r 55.33 n/y; ws12r 47.07 n/y | 2026-10-26 22:00:15 | 2026-10-26 22:00:50 | - | - |
| 2026-10-26 22:04:00 | A | ws2r | LOW | oob -> ib | none | ws3r 33.08 n/y; ws4r 46.27 n/y; ws5r 73.37 n/y; ws6r 81.82 n/y; ws7r 80.92 n/n; ws8r 61.75 n/n; ws9r 76.61 n/n; ws10r 58.92 n/n; ws11r 55.75 n/n; ws12r 47.52 n/n | 2026-10-26 22:02:15 | 2026-10-26 22:02:50 | - | - |
| 2026-10-26 22:04:30 | A | ws7r | HIGH | ex-fence -> in-fence | none | ws8r 61.31 n/y; ws9r 75.67 n/y; ws10r 58.48 n/y; ws11r 55.39 n/y; ws12r 47.14 n/y | 2026-10-26 22:03:05 | 2026-10-26 22:03:40 | - | - |
| 2026-10-26 22:04:50 | A | ws6r | HIGH | ex-fence -> in-fence | none | ws7r 78.45 n/y; ws8r 60.48 n/y; ws9r 74.31 n/y; ws10r 57.64 n/y; ws11r 54.73 n/y; ws12r 46.44 n/y | 2026-10-26 22:00:00 | 2026-10-26 22:00:35 | - | - |
| 2026-10-26 22:05:00 | B | ws5r | HIGH | ex-fence -> in-fence | ws6r | ws6r 89.00 y/y; ws7r 86.60 y/y; ws8r 51.53 n/y; ws9r 63.18 n/y; ws10r 49.14 n/y; ws11r 49.95 n/y; ws12r 37.39 n/y | 2026-10-26 22:00:00 | 2026-10-26 22:00:35 | 2026-10-26 22:00:00 | 2026-10-26 22:00:35 |
| 2026-10-26 22:05:35 | A | ws2r | LOW | oob -> ib | none | ws3r 30.36 n/y; ws4r 44.10 n/y; ws5r 58.14 n/y; ws6r 80.72 n/y; ws7r 79.31 n/n; ws8r 60.99 n/n; ws9r 75.10 n/n; ws10r 58.16 n/n; ws11r 55.13 n/n; ws12r 46.87 n/n | 2026-10-26 22:02:15 | 2026-10-26 22:02:50 | - | - |
| 2026-10-26 22:05:50 | A | ws2r | LOW | oob -> ib | none | ws3r 30.60 n/y; ws4r 44.30 n/y; ws5r 58.41 n/y; ws6r 80.83 n/y; ws7r 79.46 n/n; ws8r 61.07 n/n; ws9r 75.24 n/n; ws10r 58.24 n/n; ws11r 55.20 n/n; ws12r 46.94 n/n | 2026-10-26 22:02:15 | 2026-10-26 22:02:50 | - | - |
| 2026-10-26 22:06:00 | A | ws2r | LOW | ex-fence -> in-fence | ws3r | ws3r 18.04 y/y; ws4r 43.71 n/y; ws5r 57.58 n/y; ws6r 68.81 n/y; ws7r 79.02 n/n; ws8r 60.83 n/n; ws9r 74.83 n/n; ws10r 57.99 n/n; ws11r 55.00 n/n; ws12r 46.73 n/n | 2026-10-26 22:05:25 | 2026-10-26 22:06:00 | 2026-10-26 22:02:15 | 2026-10-26 22:02:50 |
| 2026-10-26 22:06:00 | A | ws6r | HIGH | ex-fence -> in-fence | none | ws7r 79.02 n/y; ws8r 60.83 n/y; ws9r 74.83 n/y; ws10r 57.99 n/y; ws11r 55.00 n/y; ws12r 46.73 n/y | 2026-10-26 22:00:00 | 2026-10-26 22:00:35 | - | - |
| 2026-10-26 22:06:00 | B | ws2r | LOW | oob -> ib | none | ws3r 30.85 n/y; ws4r 57.54 n/y; ws5r 69.91 n/y; ws6r 80.95 n/y; ws7r 86.60 n/n; ws8r 51.53 n/n; ws9r 63.18 n/n; ws10r 49.14 n/n; ws11r 49.95 n/n; ws12r 37.39 n/y | 2026-10-26 22:05:25 | 2026-10-26 22:06:00 | - | - |
| 2026-10-26 22:06:00 | B | ws6r | HIGH | oob -> ib | ws7r | ws7r 86.60 y/y; ws8r 51.53 n/y; ws9r 63.18 n/y; ws10r 49.14 n/y; ws11r 49.95 n/y; ws12r 37.39 n/y | 2026-10-26 22:00:00 | 2026-10-26 22:00:35 | 2026-10-26 22:03:05 | 2026-10-26 22:03:40 |
| 2026-10-26 22:08:05 | A | ws2r | LOW | ex-fence -> in-fence | ws3r | ws3r 17.05 y/y; ws4r 33.54 n/y; ws5r 56.05 n/y; ws6r 67.59 n/y; ws7r 78.31 n/n; ws8r 68.79 n/n; ws9r 74.19 n/n; ws10r 57.55 n/n; ws11r 54.66 n/n; ws12r 46.37 n/n | 2026-10-26 22:05:25 | 2026-10-26 22:06:00 | 2026-10-26 22:02:15 | 2026-10-26 22:02:50 |
| 2026-10-26 22:10:00 | A | ws2r | LOW | ex-fence -> in-fence | ws3r | ws3r 8.84 y/y; ws4r 33.08 n/y; ws5r 42.06 n/y; ws6r 67.13 n/y; ws7r 74.27 n/y; ws8r 68.57 n/n; ws9r 73.95 n/n; ws10r 65.37 n/n; ws11r 54.51 n/n; ws12r 46.22 n/n | 2026-10-26 22:05:25 | 2026-10-26 22:06:00 | 2026-10-26 22:02:15 | 2026-10-26 22:02:50 |
| 2026-10-26 22:10:00 | B | ws7r | HIGH | oob -> ib + ex-fence -> in-fence | none | ws8r 59.88 n/y; ws9r 63.18 n/y; ws10r 57.14 n/y; ws11r 49.95 n/y; ws12r 37.39 n/y | 2026-10-26 22:03:05 | 2026-10-26 22:03:40 | - | - |
| 2026-10-26 22:12:00 | B | ws6r | HIGH | ex-fence -> in-fence | none | ws7r 77.78 n/y; ws8r 59.88 n/y; ws9r 71.73 n/y; ws10r 57.14 n/y; ws11r 54.66 n/y; ws12r 44.56 n/y | 2026-10-26 22:00:00 | 2026-10-26 22:00:35 | - | - |
| 2026-10-26 22:12:05 | A | ws2r | LOW | ex-fence -> in-fence | ws3r | ws3r 12.19 y/y; ws4r 20.93 n/y; ws5r 41.34 n/y; ws6r 53.70 n/y; ws7r 72.07 n/y; ws8r 66.81 n/n; ws9r 81.09 n/n; ws10r 63.58 n/n; ws11r 62.98 n/n; ws12r 52.35 n/n | 2026-10-26 22:10:00 | 2026-10-26 22:10:35 | 2026-10-26 22:02:15 | 2026-10-26 22:02:50 |
| 2026-10-26 22:12:05 | A | ws4r | LOW | ex-fence -> in-fence | none | ws5r 41.34 n/y; ws6r 53.70 n/y; ws7r 72.07 n/y; ws8r 66.81 n/n; ws9r 81.09 n/n; ws10r 63.58 n/n; ws11r 62.98 n/n; ws12r 52.35 n/n | 2026-10-26 22:02:15 | 2026-10-26 22:02:50 | - | - |
| 2026-10-26 22:12:35 | A | ws2r | LOW | ex-fence -> in-fence | ws3r | ws3r 11.29 y/y; ws4r 20.51 n/y; ws5r 41.34 n/y; ws6r 53.34 n/y; ws7r 71.81 n/y; ws8r 66.60 n/n; ws9r 80.87 n/n; ws10r 63.37 n/n; ws11r 62.81 n/n; ws12r 52.18 n/n | 2026-10-26 22:10:00 | 2026-10-26 22:10:35 | 2026-10-26 22:02:15 | 2026-10-26 22:02:50 |
| 2026-10-26 22:12:35 | A | ws4r | LOW | ex-fence -> in-fence | none | ws5r 41.34 n/y; ws6r 53.34 n/y; ws7r 71.81 n/y; ws8r 66.60 n/n; ws9r 80.87 n/n; ws10r 63.37 n/n; ws11r 62.81 n/n; ws12r 52.18 n/n | 2026-10-26 22:02:15 | 2026-10-26 22:02:50 | - | - |
| 2026-10-26 22:12:50 | A | ws9r | HIGH | ex-fence -> in-fence | none | ws10r 62.60 n/y; ws11r 62.18 n/y; ws12r 51.47 n/y | 2026-10-26 22:07:15 | 2026-10-26 22:07:50 | - | - |
| 2026-10-26 22:15:30 | A | ws1r | LOW | ex-fence -> in-fence | ws2r | ws2r 17.83 y/y; ws3r 12.40 y/y; ws4r 19.38 y/y; ws5r 30.86 n/y; ws6r 52.38 n/y; ws7r 69.38 n/y; ws8r 64.71 n/y; ws9r 78.70 n/n; ws10r 61.47 n/n; ws11r 61.21 n/n; ws12r 50.44 n/n | 2026-10-26 22:01:05 | 2026-10-26 22:01:40 | 2026-10-26 22:10:00 | 2026-10-26 22:10:35 |
| 2026-10-26 22:15:50 | A | ws2r | LOW | ex-fence -> in-fence | ws3r | ws3r 14.98 y/y; ws4r 19.38 y/y; ws5r 32.43 n/y; ws6r 52.38 n/y; ws7r 70.29 n/y; ws8r 65.41 n/y; ws9r 79.48 n/n; ws10r 62.17 n/n; ws11r 61.81 n/n; ws12r 51.08 n/n | 2026-10-26 22:10:00 | 2026-10-26 22:10:35 | 2026-10-26 22:02:15 | 2026-10-26 22:02:50 |
| 2026-10-26 22:16:00 | B | ws2r | LOW | ex-fence -> in-fence | ws3r | ws3r 8.84 y/y; ws4r 19.38 y/y; ws5r 41.34 n/y; ws6r 66.66 n/y; ws7r 77.78 n/y; ws8r 65.33 n/n; ws9r 71.73 n/n; ws10r 57.14 n/n; ws11r 54.66 n/n; ws12r 44.56 n/n | 2026-10-26 22:10:00 | 2026-10-26 22:10:35 | 2026-10-26 22:02:15 | 2026-10-26 22:02:50 |
| 2026-10-26 22:16:25 | A | ws3r | LOW | oob -> ib | ws4r | ws4r 9.82 y/y; ws5r 32.74 n/y; ws6r 52.38 n/y; ws7r 70.51 n/y; ws8r 71.19 n/n; ws9r 79.67 n/n; ws10r 62.34 n/n; ws11r 61.96 n/n; ws12r 51.24 n/n | 2026-10-26 22:15:30 | 2026-10-26 22:16:05 | 2026-10-26 22:02:15 | 2026-10-26 22:02:50 |
| 2026-10-26 22:16:35 | A | ws2r | LOW | oob -> ib | ws3r | ws3r 17.56 y/y; ws4r 12.23 y/y; ws5r 34.04 n/y; ws6r 52.96 n/y; ws7r 71.56 n/y; ws8r 72.31 n/n; ws9r 80.64 n/n; ws10r 63.17 n/n; ws11r 62.65 n/n; ws12r 52.00 n/n | 2026-10-26 22:10:00 | 2026-10-26 22:10:35 | 2026-10-26 22:15:30 | 2026-10-26 22:16:05 |
| 2026-10-26 22:17:10 | A | ws9r | HIGH | ex-fence -> in-fence | none | ws10r 61.77 n/y; ws11r 61.47 n/y; ws12r 50.72 n/y | 2026-10-26 22:07:15 | 2026-10-26 22:07:50 | - | - |
| 2026-10-26 22:17:55 | A | ws2r | LOW | oob -> ib | ws3r | ws3r 16.46 y/y; ws4r 10.95 y/y; ws5r 33.34 n/y; ws6r 52.38 n/y; ws7r 57.27 n/y; ws8r 71.71 n/n; ws9r 80.07 n/n; ws10r 62.69 n/n; ws11r 62.25 n/n; ws12r 51.55 n/n | 2026-10-26 22:16:30 | 2026-10-26 22:17:05 | 2026-10-26 22:15:30 | 2026-10-26 22:16:05 |
| 2026-10-26 22:17:55 | A | ws3r | LOW | oob -> ib | ws4r | ws4r 10.95 y/y; ws5r 33.34 n/y; ws6r 52.38 n/y; ws7r 57.27 n/y; ws8r 71.71 n/n; ws9r 80.07 n/n; ws10r 62.69 n/n; ws11r 62.25 n/n; ws12r 51.55 n/n | 2026-10-26 22:15:30 | 2026-10-26 22:16:05 | 2026-10-26 22:02:15 | 2026-10-26 22:02:50 |
| 2026-10-26 22:18:00 | A | ws3r | LOW | ex-fence -> in-fence | ws4r | ws4r 9.82 y/y; ws5r 32.74 n/y; ws6r 38.09 n/y; ws7r 57.27 n/y; ws8r 71.19 n/n; ws9r 79.67 n/n; ws10r 62.34 n/n; ws11r 61.96 n/n; ws12r 51.24 n/n | 2026-10-26 22:15:30 | 2026-10-26 22:16:05 | 2026-10-26 22:02:15 | 2026-10-26 22:02:50 |
| 2026-10-26 22:18:00 | A | ws9r | HIGH | ex-fence -> in-fence | none | ws10r 62.34 n/y; ws11r 61.96 n/y; ws12r 51.24 n/y | 2026-10-26 22:07:15 | 2026-10-26 22:07:50 | - | - |
| 2026-10-26 22:18:00 | B | ws3r | LOW | oob -> ib | ws4r | ws4r 19.38 y/y; ws5r 41.34 n/y; ws6r 52.38 n/y; ws7r 71.56 n/y; ws8r 65.33 n/n; ws9r 71.73 n/n; ws10r 57.14 n/n; ws11r 54.66 n/n; ws12r 44.56 n/n | 2026-10-26 22:15:30 | 2026-10-26 22:16:05 | 2026-10-26 22:02:15 | 2026-10-26 22:02:50 |
| 2026-10-26 22:19:20 | A | ws2r | LOW | ex-fence -> in-fence | none | ws3r 25.18 n/n; ws4r 11.99 y/y; ws5r 33.90 n/y; ws6r 39.03 n/y; ws7r 57.27 n/y; ws8r 72.19 n/n; ws9r 80.53 n/n; ws10r 63.07 n/y; ws11r 62.57 n/n; ws12r 51.91 n/n | 2026-10-26 22:17:55 | 2026-10-26 22:18:30 | - | - |
| 2026-10-26 22:20:00 | B | ws2r | LOW | ex-fence -> in-fence | ws3r | ws3r 16.46 y/y; ws4r 12.94 y/y; ws5r 34.43 n/y; ws6r 52.38 n/y; ws7r 71.56 n/y; ws8r 65.33 n/n; ws9r 71.73 n/n; ws10r 63.47 n/n; ws11r 54.66 n/n; ws12r 44.56 n/n | 2026-10-26 22:17:55 | 2026-10-26 22:18:30 | 2026-10-26 22:15:30 | 2026-10-26 22:16:05 |
| 2026-10-26 22:20:40 | A | ws4r | LOW | oob -> ib | none | ws5r 27.33 n/y; ws6r 41.42 n/y; ws7r 59.64 n/y; ws8r 73.47 n/n; ws9r 81.82 n/n; ws10r 67.16 n/n; ws11r 63.61 n/y; ws12r 52.94 n/n | 2026-10-26 22:19:20 | 2026-10-26 22:19:55 | - | - |
| 2026-10-26 22:21:00 | A | ws4r | LOW | ex-fence -> in-fence | none | ws5r 28.47 n/y; ws6r 42.89 n/y; ws7r 61.28 n/y; ws8r 74.27 n/n; ws9r 84.58 n/n; ws10r 68.30 n/n; ws11r 64.51 n/n; ws12r 53.62 n/n | 2026-10-26 22:19:20 | 2026-10-26 22:19:55 | - | - |
| 2026-10-26 22:21:00 | B | ws3r | LOW | ex-fence -> in-fence | ws4r | ws4r 12.94 y/y; ws5r 34.43 n/y; ws6r 52.38 n/y; ws7r 71.56 n/y; ws8r 65.33 n/n; ws9r 82.20 n/n; ws10r 63.47 n/n; ws11r 54.66 n/n; ws12r 44.56 n/n | 2026-10-26 22:15:30 | 2026-10-26 22:16:05 | 2026-10-26 22:19:20 | 2026-10-26 22:19:55 |
| 2026-10-26 22:21:30 | A | ws9r | HIGH | oob -> ib | none | ws10r 67.69 n/y; ws11r 64.00 n/y; ws12r 53.25 n/y | 2026-10-26 22:07:15 | 2026-10-26 22:07:50 | - | - |
| 2026-10-26 22:22:10 | A | ws1r | HIGH | oob -> ib | none | ws2r 47.02 n/y; ws3r 32.66 n/y; ws4r 14.23 n/y; ws5r 26.00 n/n; ws6r 39.68 n/n; ws7r 57.74 n/n; ws8r 72.54 n/y; ws9r 81.49 y/y; ws10r 65.82 n/y; ws11r 71.66 n/y; ws12r 52.18 n/y | 2026-10-26 22:08:00 | 2026-10-26 22:08:35 | - | - |
| 2026-10-26 22:22:15 | A | ws4r | LOW | oob -> ib | none | ws5r 27.19 n/y; ws6r 41.24 n/y; ws7r 59.44 n/y; ws8r 73.37 n/n; ws9r 82.83 n/n; ws10r 67.02 n/n; ws11r 72.52 n/n; ws12r 52.86 n/n | 2026-10-26 22:19:20 | 2026-10-26 22:19:55 | - | - |
| 2026-10-26 22:23:35 | A | ws4r | LOW | ex-fence -> in-fence | none | ws5r 28.59 n/y; ws6r 43.04 n/y; ws7r 61.45 n/y; ws8r 74.36 n/n; ws9r 84.73 n/n; ws10r 68.42 n/n; ws11r 73.69 n/n; ws12r 53.69 n/n | 2026-10-26 22:19:20 | 2026-10-26 22:19:55 | - | - |
| 2026-10-26 22:23:45 | A | ws9r | HIGH | oob -> ib | none | ws10r 68.18 n/y; ws11r 73.49 n/y; ws12r 53.54 n/y | 2026-10-26 22:07:15 | 2026-10-26 22:07:50 | - | - |
| 2026-10-26 22:24:00 | B | ws4r | LOW | oob -> ib + ex-fence -> in-fence | none | ws5r 34.43 n/y; ws6r 42.74 n/y; ws7r 61.11 n/y; ws8r 74.19 n/n; ws9r 82.20 n/n; ws10r 63.47 n/n; ws11r 63.71 n/n; ws12r 53.54 n/n | 2026-10-26 22:19:20 | 2026-10-26 22:19:55 | - | - |
| 2026-10-26 22:25:00 | A | ws1r | HIGH | oob -> ib + ex-fence -> in-fence | none | ws2r 60.97 n/y; ws3r 45.25 n/y; ws4r 27.11 n/y; ws5r 28.77 n/y; ws6r 30.75 n/n; ws7r 48.18 n/n; ws8r 63.34 n/y; ws9r 82.48 y/y; ws10r 66.74 n/y; ws11r 72.29 n/y; ws12r 61.47 n/y | 2026-10-26 22:24:25 | 2026-10-26 22:25:00 | - | - |
| 2026-10-26 22:25:30 | A | ws1r | HIGH | ex-fence -> in-fence | none | ws2r 60.64 n/y; ws3r 44.98 n/y; ws4r 26.79 n/y; ws5r 28.52 n/y; ws6r 30.57 n/n; ws7r 47.98 n/n; ws8r 63.17 n/y; ws9r 82.30 y/y; ws10r 66.59 n/y; ws11r 72.18 n/y; ws12r 61.38 n/y | 2026-10-26 22:24:25 | 2026-10-26 22:25:00 | - | - |
| 2026-10-26 22:26:00 | B | ws1r | HIGH | oob -> ib + ex-fence -> in-fence | none | ws2r 57.71 n/y; ws3r 36.58 n/y; ws4r 20.02 n/y; ws5r 27.73 n/n; ws6r 42.74 n/n; ws7r 61.11 n/n; ws8r 74.19 n/y; ws9r 82.20 y/y; ws10r 63.47 n/y; ws11r 63.71 n/y; ws12r 53.54 n/y | 2026-10-26 22:24:25 | 2026-10-26 22:25:00 | - | - |
| 2026-10-26 22:26:45 | A | ws9r | HIGH | ex-fence -> in-fence | none | ws10r 64.33 n/y; ws11r 70.55 n/y; ws12r 60.03 n/y | 2026-10-26 22:25:20 | 2026-10-26 22:25:55 | - | - |
| 2026-10-26 22:29:00 | A | ws9r | HIGH | ex-fence -> in-fence | none | ws10r 64.44 n/y; ws11r 70.64 n/y; ws12r 60.10 n/y | 2026-10-26 22:25:20 | 2026-10-26 22:25:55 | - | - |
| 2026-10-26 22:30:00 | A | ws9r | HIGH | ex-fence -> in-fence | none | ws10r 56.03 n/y; ws11r 70.07 n/y; ws12r 59.61 n/y | 2026-10-26 22:25:20 | 2026-10-26 22:25:55 | - | - |
| 2026-10-26 22:31:25 | A | ws1r | LOW | oob -> ib | none | ws2r 61.52 n/y; ws3r 53.21 n/n; ws4r 20.48 n/y; ws5r 24.37 n/y; ws6r 19.09 y/y; ws7r 33.47 n/y; ws8r 59.90 n/y; ws9r 66.31 n/y; ws10r 55.75 n/y; ws11r 69.55 n/n; ws12r 59.16 n/n | 2026-10-26 22:15:30 | 2026-10-26 22:16:05 | - | - |
| 2026-10-26 22:32:05 | A | ws1r | LOW | oob -> ib | none | ws2r 50.10 n/y; ws3r 52.69 n/n; ws4r 22.78 n/y; ws5r 23.75 n/y; ws6r 19.09 y/y; ws7r 32.92 n/y; ws8r 46.50 n/y; ws9r 66.31 n/y; ws10r 55.75 n/y; ws11r 69.35 n/n; ws12r 58.98 n/n | 2026-10-26 22:15:30 | 2026-10-26 22:16:05 | - | - |
| 2026-10-26 22:32:15 | A | ws1r | LOW | ex-fence -> in-fence | none | ws2r 52.79 n/y; ws3r 53.96 n/n; ws4r 25.60 n/y; ws5r 25.26 n/y; ws6r 19.09 y/y; ws7r 34.17 n/y; ws8r 47.62 n/y; ws9r 66.31 n/y; ws10r 55.75 n/y; ws11r 69.84 n/n; ws12r 59.41 n/n | 2026-10-26 22:15:30 | 2026-10-26 22:16:05 | - | - |
| 2026-10-26 22:33:00 | B | ws1r | LOW | oob -> ib + ex-fence -> in-fence | none | ws2r 61.52 n/y; ws3r 53.21 n/n; ws4r 20.48 n/y; ws5r 26.12 n/y; ws6r 28.71 n/y; ws7r 46.82 n/y; ws8r 59.90 n/y; ws9r 80.59 n/y; ws10r 65.03 n/n; ws11r 69.55 n/n; ws12r 53.54 n/n | 2026-10-26 22:32:05 | 2026-10-26 22:32:40 | - | - |
| 2026-10-26 22:34:15 | A | ws6r | LOW | ex-fence -> in-fence | none | ws7r 36.58 n/y; ws8r 49.80 n/y; ws9r 66.65 n/y; ws10r 58.28 n/y; ws11r 69.88 n/y; ws12r 60.55 n/n | 2026-10-26 22:22:15 | 2026-10-26 22:22:50 | - | - |
| 2026-10-26 22:35:20 | A | ws6r | LOW | ex-fence -> in-fence | none | ws7r 36.84 n/y; ws8r 50.05 n/y; ws9r 67.31 n/y; ws10r 58.76 n/y; ws11r 70.12 n/y; ws12r 60.71 n/y | 2026-10-26 22:22:15 | 2026-10-26 22:22:50 | - | - |
| 2026-10-26 22:35:50 | A | ws6r | LOW | ex-fence -> in-fence | none | ws7r 36.97 n/y; ws8r 50.16 n/y; ws9r 67.63 n/y; ws10r 58.99 n/y; ws11r 70.24 n/y; ws12r 60.79 n/y | 2026-10-26 22:22:15 | 2026-10-26 22:22:50 | - | - |
| 2026-10-26 22:39:00 | B | ws9r | HIGH | ex-fence -> in-fence | none | ws10r 65.03 n/y; ws11r 69.55 n/y; ws12r 60.87 n/y | 2026-10-26 22:25:20 | 2026-10-26 22:25:55 | - | - |
| 2026-10-26 22:39:55 | A | ws6r | LOW | oob -> ib | none | ws7r 32.77 n/y; ws8r 49.80 n/y; ws9r 53.21 n/y; ws10r 58.28 n/y; ws11r 69.88 n/y; ws12r 67.79 n/n | 2026-10-26 22:22:15 | 2026-10-26 22:22:50 | - | - |
| 2026-10-26 22:40:05 | A | ws1r | HIGH | ex-fence -> in-fence | none | ws2r 52.98 n/y; ws3r 61.48 n/y; ws4r 50.33 n/y; ws5r 45.49 n/y; ws6r 14.04 n/n; ws7r 31.44 n/n; ws8r 39.00 n/n; ws9r 52.02 n/n; ws10r 44.00 n/y; ws11r 69.25 n/y; ws12r 67.33 n/y | 2026-10-26 22:24:25 | 2026-10-26 22:25:00 | - | - |
| 2026-10-26 22:41:00 | B | ws1r | HIGH | ex-fence -> in-fence | none | ws2r 50.75 n/y; ws3r 66.22 n/y; ws4r 41.94 n/y; ws5r 38.52 n/y; ws6r 22.00 n/n; ws7r 35.74 n/n; ws8r 49.80 n/n; ws9r 66.31 n/y; ws10r 58.28 n/y; ws11r 69.55 n/y; ws12r 60.87 n/y | 2026-10-26 22:40:05 | 2026-10-26 22:40:40 | - | - |
| 2026-10-26 22:41:55 | A | ws6r | LOW | oob -> ib | none | ws7r 33.27 n/y; ws8r 40.00 n/y; ws9r 53.96 n/y; ws10r 44.99 n/y; ws11r 70.12 n/y; ws12r 67.99 n/n | 2026-10-26 22:22:15 | 2026-10-26 22:22:50 | - | - |
| 2026-10-26 22:48:00 | A | ws6r | LOW | oob -> ib | none | ws7r 29.27 n/y; ws8r 42.10 n/y; ws9r 43.39 n/y; ws10r 45.65 n/y; ws11r 59.84 n/y; ws12r 54.26 n/y | 2026-10-26 22:22:15 | 2026-10-26 22:22:50 | - | - |
| 2026-10-26 22:48:15 | A | ws6r | LOW | ex-fence -> in-fence | none | ws7r 29.84 n/y; ws8r 42.88 n/y; ws9r 44.28 n/y; ws10r 46.28 n/y; ws11r 60.21 n/y; ws12r 54.79 n/y | 2026-10-26 22:22:15 | 2026-10-26 22:22:50 | - | - |
| 2026-10-26 22:48:40 | A | ws6r | LOW | ex-fence -> in-fence | none | ws7r 30.11 n/y; ws8r 43.26 n/y; ws9r 44.71 n/y; ws10r 46.58 n/y; ws11r 60.39 n/y; ws12r 55.05 n/y | 2026-10-26 22:47:55 | 2026-10-26 22:48:30 | - | - |
| 2026-10-26 22:49:10 | A | ws6r | LOW | ex-fence -> in-fence | none | ws7r 30.91 n/y; ws8r 44.34 n/y; ws9r 45.93 n/y; ws10r 47.42 n/y; ws11r 60.93 n/y; ws12r 55.80 n/y | 2026-10-26 22:47:55 | 2026-10-26 22:48:30 | - | - |
| 2026-10-26 22:50:20 | A | ws6r | LOW | ex-fence -> in-fence | none | ws7r 30.65 n/y; ws8r 43.99 n/y; ws9r 45.53 n/y; ws10r 36.02 n/y; ws11r 60.75 n/y; ws12r 55.56 n/y | 2026-10-26 22:47:55 | 2026-10-26 22:48:30 | - | - |
| 2026-10-26 22:50:50 | A | ws2r | HIGH | oob -> ib | none | ws3r 72.65 n/y; ws4r 60.15 n/y; ws5r 65.28 n/y; ws6r 20.08 n/y; ws7r 29.84 n/n; ws8r 42.88 n/n; ws9r 44.28 n/n; ws10r 34.98 n/n; ws11r 60.21 n/n; ws12r 54.79 n/y | 2026-10-26 22:45:25 | 2026-10-26 22:46:00 | - | - |
| 2026-10-26 22:52:25 | A | ws2r | HIGH | oob -> ib | ws3r | ws3r 82.72 y/y; ws4r 66.74 n/y; ws5r 69.26 n/y; ws6r 26.72 n/y; ws7r 39.15 n/n; ws8r 45.37 n/n; ws9r 47.05 n/n; ws10r 37.32 n/n; ws11r 61.43 n/n; ws12r 56.51 n/y | 2026-10-26 22:45:25 | 2026-10-26 22:46:00 | 2026-10-26 22:45:40 | 2026-10-26 22:46:15 |
| 2026-10-26 22:52:55 | A | ws1r | HIGH | ex-fence -> in-fence | none | ws2r 78.88 n/y; ws3r 80.98 y/y; ws4r 64.16 n/y; ws5r 64.06 n/y; ws6r 18.94 n/y; ws7r 36.48 n/n; ws8r 42.49 n/n; ws9r 43.84 n/n; ws10r 34.66 n/n; ws11r 60.03 n/n; ws12r 54.53 n/y | 2026-10-26 22:43:30 | 2026-10-26 22:44:05 | - | - |
| 2026-10-26 22:52:55 | A | ws2r | HIGH | ex-fence -> in-fence | ws3r | ws3r 80.98 y/y; ws4r 64.16 n/y; ws5r 64.06 n/y; ws6r 18.94 n/y; ws7r 36.48 n/n; ws8r 42.49 n/n; ws9r 43.84 n/n; ws10r 34.66 n/n; ws11r 60.03 n/n; ws12r 54.53 n/y | 2026-10-26 22:45:25 | 2026-10-26 22:46:00 | 2026-10-26 22:45:40 | 2026-10-26 22:46:15 |
| 2026-10-26 22:53:25 | A | ws3r | HIGH | ex-fence -> in-fence | none | ws4r 62.30 n/y; ws5r 56.63 n/y; ws6r 12.44 n/y; ws7r 34.44 n/y; ws8r 39.73 n/n; ws9r 40.76 n/n; ws10r 32.86 n/n; ws11r 58.63 n/n; ws12r 53.70 n/y | 2026-10-26 22:45:40 | 2026-10-26 22:46:15 | - | - |
| 2026-10-26 22:54:00 | A | ws1r | HIGH | ex-fence -> in-fence | none | ws2r 62.35 n/y; ws3r 61.92 n/y; ws4r 61.14 n/y; ws5r 54.97 n/y; ws6r 13.48 n/y; ws7r 33.14 n/y; ws8r 37.94 n/y; ws9r 40.39 n/n; ws10r 32.86 n/n; ws11r 57.60 n/n; ws12r 53.70 n/y | 2026-10-26 22:43:30 | 2026-10-26 22:44:05 | - | - |
| 2026-10-26 22:54:00 | B | ws2r | HIGH | oob -> ib + ex-fence -> in-fence | none | ws3r 72.87 n/y; ws4r 60.94 n/y; ws5r 60.63 n/y; ws6r 12.44 n/n; ws7r 33.46 n/y; ws8r 40.00 n/n; ws9r 53.96 n/n; ws10r 47.15 n/n; ws11r 69.25 n/y; ws12r 67.99 n/y | 2026-10-26 22:52:25 | 2026-10-26 22:53:00 | - | - |
| 2026-10-26 22:55:00 | A | ws6r | LOW | oob -> ib | none | ws7r 35.00 n/y; ws8r 40.50 n/y; ws9r 41.58 n/y; ws10r 33.18 n/y; ws11r 47.90 n/y; ws12r 53.70 n/y | 2026-10-26 22:47:55 | 2026-10-26 22:48:30 | - | - |
| 2026-10-26 22:55:00 | B | ws1r | HIGH | ex-fence -> in-fence | none | ws2r 74.66 n/n; ws3r 72.87 n/y; ws4r 60.94 n/y; ws5r 54.97 n/y; ws6r 12.44 n/n; ws7r 33.46 n/y; ws8r 40.00 n/n; ws9r 53.96 n/n; ws10r 47.15 n/n; ws11r 57.79 n/y; ws12r 67.99 n/y | 2026-10-26 22:54:00 | 2026-10-26 22:54:35 | - | - |
| 2026-10-26 22:56:30 | A | ws6r | LOW | oob -> ib | none | ws7r 33.91 n/n; ws8r 38.31 n/y; ws9r 40.39 n/y; ws10r 32.86 n/y; ws11r 46.88 n/y; ws12r 53.70 n/y | 2026-10-26 22:47:55 | 2026-10-26 22:48:30 | - | - |
| 2026-10-26 22:57:40 | A | ws6r | LOW | ex-fence -> in-fence | none | ws7r 35.87 n/n; ws8r 41.62 n/y; ws9r 30.11 n/y; ws10r 34.04 n/y; ws11r 48.61 n/y; ws12r 53.98 n/y | 2026-10-26 22:56:30 | 2026-10-26 22:57:05 | - | - |
| 2026-10-26 23:00:00 | B | ws6r | LOW | oob -> ib + ex-fence -> in-fence | none | ws7r 37.76 n/y; ws8r 38.99 n/y; ws9r 40.39 n/y; ws10r 36.69 n/y; ws11r 57.79 n/y; ws12r 56.04 n/y | 2026-10-26 22:57:25 | 2026-10-26 22:58:00 | - | - |
| 2026-10-26 23:04:35 | A | ws2r | LOW | ex-fence -> in-fence | none | ws3r 52.76 n/y; ws4r 52.37 n/y; ws5r 55.18 n/y; ws6r 22.08 n/n; ws7r 34.71 n/n; ws8r 26.92 n/y; ws9r 26.45 n/y; ws10r 28.47 n/y; ws11r 43.50 n/y; ws12r 41.76 n/y | 2026-10-26 22:57:40 | 2026-10-26 22:58:15 | - | - |
| 2026-10-26 23:06:10 | A | ws2r | LOW | ex-fence -> in-fence | none | ws3r 39.71 n/y; ws4r 51.00 n/y; ws5r 47.45 n/y; ws6r 23.70 n/y; ws7r 32.47 n/y; ws8r 25.20 n/y; ws9r 19.96 y/y; ws10r 28.47 n/y; ws11r 35.54 n/y; ws12r 41.76 n/y | 2026-10-26 22:57:40 | 2026-10-26 22:58:15 | - | - |
| 2026-10-26 23:06:15 | A | ws9r | LOW | ex-fence -> in-fence | none | ws10r 28.47 n/y; ws11r 36.76 n/y; ws12r 41.76 n/y | 2026-10-26 22:59:05 | 2026-10-26 22:59:40 | - | - |
| 2026-10-26 23:07:00 | A | ws1r | LOW | oob -> ib | none | ws2r 22.14 n/y; ws3r 41.26 n/y; ws4r 52.37 n/y; ws5r 48.88 n/y; ws6r 25.14 n/y; ws7r 33.71 n/y; ws8r 26.92 n/y; ws9r 21.54 n/y; ws10r 28.47 n/y; ws11r 36.99 n/y; ws12r 41.76 n/y | 2026-10-26 23:06:15 | 2026-10-26 23:06:50 | - | - |
| 2026-10-26 23:08:00 | A | ws1r | LOW | ex-fence -> in-fence | none | ws2r 32.47 n/y; ws3r 45.94 n/y; ws4r 52.70 n/y; ws5r 53.48 n/y; ws6r 29.78 n/y; ws7r 37.84 n/y; ws8r 32.45 n/y; ws9r 26.55 n/y; ws10r 28.47 n/y; ws11r 41.72 n/y; ws12r 41.76 n/y | 2026-10-26 23:07:00 | 2026-10-26 23:07:35 | - | - |
| 2026-10-26 23:08:00 | B | ws1r | LOW | oob -> ib | none | ws2r 25.29 n/y; ws3r 51.91 n/y; ws4r 54.93 n/y; ws5r 55.18 n/y; ws6r 22.08 n/y; ws7r 34.71 n/y; ws8r 30.64 n/y; ws9r 26.45 n/y; ws10r 36.69 n/y; ws11r 43.50 n/y; ws12r 56.04 n/y | 2026-10-26 23:07:00 | 2026-10-26 23:07:35 | - | - |
| 2026-10-26 23:08:00 | B | ws2r | LOW | ex-fence -> in-fence | none | ws3r 51.91 n/y; ws4r 54.93 n/y; ws5r 55.18 n/y; ws6r 22.08 n/y; ws7r 34.71 n/y; ws8r 30.64 n/y; ws9r 26.45 n/y; ws10r 36.69 n/y; ws11r 43.50 n/y; ws12r 56.04 n/y | 2026-10-26 23:06:15 | 2026-10-26 23:06:50 | - | - |
| 2026-10-26 23:09:00 | B | ws1r | LOW | ex-fence -> in-fence | none | ws2r 25.29 n/y; ws3r 44.78 n/y; ws4r 54.93 n/y; ws5r 55.18 n/y; ws6r 22.08 n/y; ws7r 34.71 n/y; ws8r 30.64 n/y; ws9r 26.45 n/y; ws10r 36.69 n/y; ws11r 43.50 n/y; ws12r 56.04 n/y | 2026-10-26 23:07:00 | 2026-10-26 23:07:35 | - | - |
| 2026-10-26 23:16:00 | A | ws1r | HIGH | oob -> ib + ex-fence -> in-fence | none | ws2r 68.79 n/y; ws3r 57.24 n/y; ws4r 50.71 n/n; ws5r 61.03 n/y; ws6r 40.09 n/y; ws7r 50.12 n/y; ws8r 37.13 n/y; ws9r 32.37 n/y; ws10r 29.79 n/n; ws11r 45.63 n/y; ws12r 40.69 n/n | 2026-10-26 23:02:30 | 2026-10-26 23:03:05 | - | - |
| 2026-10-26 23:16:55 | A | ws1r | HIGH | ex-fence -> in-fence | none | ws2r 67.64 n/y; ws3r 56.04 n/y; ws4r 49.79 n/y; ws5r 60.00 n/y; ws6r 39.22 n/y; ws7r 49.29 n/y; ws8r 36.09 n/y; ws9r 31.45 n/y; ws10r 27.99 n/n; ws11r 44.86 n/y; ws12r 38.74 n/n | 2026-10-26 23:16:00 | 2026-10-26 23:16:35 | - | - |
| 2026-10-26 23:17:00 | B | ws1r | HIGH | oob -> ib + ex-fence -> in-fence | none | ws2r 57.72 n/y; ws3r 48.53 n/y; ws4r 54.76 n/y; ws5r 56.47 n/y; ws6r 30.71 n/y; ws7r 39.24 n/y; ws8r 33.57 n/y; ws9r 30.13 n/y; ws10r 28.47 n/n; ws11r 44.86 n/y; ws12r 41.76 n/n | 2026-10-26 23:16:00 | 2026-10-26 23:16:35 | - | - |
| 2026-10-26 23:21:00 | A | ws2r | HIGH | oob -> ib | none | ws3r 69.35 n/y; ws4r 60.14 n/y; ws5r 60.71 n/y; ws6r 51.92 n/y; ws7r 61.82 n/y; ws8r 51.06 n/y; ws9r 33.95 n/y; ws10r 39.71 n/y; ws11r 48.85 n/y; ws12r 44.34 n/n | 2026-10-26 23:00:00 | 2026-10-26 23:00:35 | - | - |
| 2026-10-26 23:22:05 | A | ws2r | HIGH | oob -> ib | none | ws3r 69.13 n/y; ws4r 59.95 n/y; ws5r 60.55 n/y; ws6r 51.82 n/y; ws7r 61.68 n/y; ws8r 50.90 n/y; ws9r 33.95 n/y; ws10r 39.51 n/y; ws11r 48.72 n/y; ws12r 44.08 n/n | 2026-10-26 23:00:00 | 2026-10-26 23:00:35 | - | - |
| 2026-10-26 23:24:00 | A | ws2r | HIGH | oob -> ib + ex-fence -> in-fence | ws3r | ws3r 81.57 y/y; ws4r 60.93 n/y; ws5r 60.26 n/y; ws6r 62.51 n/y; ws7r 61.41 n/y; ws8r 50.60 n/y; ws9r 41.55 n/y; ws10r 39.11 n/y; ws11r 48.46 n/y; ws12r 48.51 n/y | 2026-10-26 23:22:00 | 2026-10-26 23:22:35 | 2026-10-26 23:00:05 | 2026-10-26 23:00:40 |
| 2026-10-26 23:24:20 | A | ws2r | HIGH | ex-fence -> in-fence | ws3r | ws3r 82.36 y/y; ws4r 61.60 n/y; ws5r 60.71 n/y; ws6r 63.08 n/y; ws7r 61.82 n/y; ws8r 51.06 n/y; ws9r 42.05 n/y; ws10r 39.71 n/y; ws11r 48.85 n/y; ws12r 49.36 n/y | 2026-10-26 23:23:45 | 2026-10-26 23:24:20 | 2026-10-26 23:00:05 | 2026-10-26 23:00:40 |
| 2026-10-26 23:26:00 | A | ws2r | HIGH | oob -> ib + ex-fence -> in-fence | ws3r | ws3r 83.70 y/y; ws4r 62.76 n/y; ws5r 74.76 n/y; ws6r 63.89 n/y; ws7r 62.53 n/y; ws8r 51.87 n/y; ws9r 42.74 n/y; ws10r 40.78 n/y; ws11r 49.18 n/y; ws12r 50.87 n/y | 2026-10-26 23:23:45 | 2026-10-26 23:24:20 | 2026-10-26 23:00:05 | 2026-10-26 23:00:40 |
| 2026-10-26 23:27:30 | A | ws2r | HIGH | oob -> ib | ws3r | ws3r 90.66 y/y; ws4r 64.57 n/y; ws5r 76.31 n/y; ws6r 63.89 n/y; ws7r 70.82 n/y; ws8r 53.28 n/y; ws9r 42.74 n/y; ws10r 42.72 n/y; ws11r 49.18 n/y; ws12r 52.46 n/y | 2026-10-26 23:25:40 | 2026-10-26 23:26:15 | 2026-10-26 23:00:05 | 2026-10-26 23:00:40 |
| 2026-10-26 23:28:55 | A | ws2r | HIGH | oob -> ib | ws3r | ws3r 90.66 y/y; ws4r 78.07 n/y; ws5r 76.31 n/y; ws6r 63.89 n/y; ws7r 70.90 n/y; ws8r 62.78 n/y; ws9r 42.74 n/y; ws10r 42.72 n/y; ws11r 53.95 n/y; ws12r 52.46 n/y | 2026-10-26 23:25:40 | 2026-10-26 23:26:15 | 2026-10-26 23:00:05 | 2026-10-26 23:00:40 |
| 2026-10-26 23:31:10 | A | ws2r | HIGH | oob -> ib | ws3r | ws3r 92.29 y/y; ws4r 78.85 n/y; ws5r 75.14 n/y; ws6r 77.13 n/y; ws7r 70.90 n/y; ws8r 63.38 n/y; ws9r 42.74 n/y; ws10r 51.05 n/y; ws11r 54.41 n/y; ws12r 52.46 n/y | 2026-10-26 23:25:40 | 2026-10-26 23:26:15 | 2026-10-26 23:00:05 | 2026-10-26 23:00:40 |
| 2026-10-26 23:32:00 | A | ws2r | HIGH | oob -> ib | ws3r | ws3r 93.72 y/y; ws4r 87.55 y/y; ws5r 75.71 n/y; ws6r 77.64 n/y; ws7r 70.90 n/y; ws8r 63.38 n/y; ws9r 42.74 n/y; ws10r 51.69 n/y; ws11r 54.41 n/y; ws12r 52.46 n/y | 2026-10-26 23:25:40 | 2026-10-26 23:26:15 | 2026-10-26 23:00:05 | 2026-10-26 23:00:40 |
| 2026-10-26 23:32:05 | A | ws2r | HIGH | ex-fence -> in-fence | ws3r | ws3r 89.38 y/y; ws4r 84.76 y/y; ws5r 73.94 n/y; ws6r 76.03 n/y; ws7r 70.90 n/y; ws8r 63.38 n/y; ws9r 42.74 n/y; ws10r 49.68 n/y; ws11r 54.41 n/y; ws12r 52.46 n/y | 2026-10-26 23:25:40 | 2026-10-26 23:26:15 | 2026-10-26 23:00:05 | 2026-10-26 23:00:40 |
| 2026-10-26 23:32:05 | A | ws4r | HIGH | oob -> ib | none | ws5r 73.94 n/y; ws6r 76.03 n/y; ws7r 70.90 n/y; ws8r 63.38 n/y; ws9r 42.74 n/y; ws10r 49.68 n/y; ws11r 54.41 n/y; ws12r 52.46 n/y | 2026-10-26 23:22:05 | 2026-10-26 23:22:40 | - | - |
| 2026-10-26 23:33:05 | A | ws3r | HIGH | oob -> ib | ws4r | ws4r 85.01 y/y; ws5r 74.10 n/y; ws6r 76.18 n/y; ws7r 70.90 n/y; ws8r 63.38 n/y; ws9r 56.36 n/y; ws10r 49.86 n/y; ws11r 54.41 n/y; ws12r 52.46 n/y | 2026-10-26 23:32:05 | 2026-10-26 23:32:40 | 2026-10-26 23:22:05 | 2026-10-26 23:22:40 |
| 2026-10-26 23:34:00 | A | ws1r | HIGH | ex-fence -> in-fence | ws2r | ws2r 89.48 y/y; ws3r 92.13 y/y; ws4r 89.22 y/y; ws5r 76.31 n/y; ws6r 78.17 n/y; ws7r 73.05 n/y; ws8r 63.38 n/y; ws9r 57.03 n/y; ws10r 52.37 n/y; ws11r 54.41 n/y; ws12r 52.46 n/y | 2026-10-26 23:32:05 | 2026-10-26 23:32:40 | 2026-10-26 23:32:00 | 2026-10-26 23:32:35 |
| 2026-10-26 23:40:45 | A | ws1r | HIGH | oob -> ib | ws2r | ws2r 95.28 y/y; ws3r 94.01 y/y; ws4r 96.15 y/y; ws5r 95.58 y/y; ws6r 78.17 n/y; ws7r 73.05 n/y; ws8r 73.18 n/y; ws9r 57.03 n/y; ws10r 63.44 n/y; ws11r 62.85 n/y; ws12r 57.76 n/y | 2026-10-26 23:38:20 | 2026-10-26 23:38:55 | 2026-10-26 23:32:00 | 2026-10-26 23:32:35 |
| 2026-10-26 23:41:00 | A | ws1r | HIGH | oob -> ib + ex-fence -> in-fence | ws2r | ws2r 96.17 y/y; ws3r 94.01 y/y; ws4r 96.51 y/y; ws5r 95.79 y/y; ws6r 78.17 n/y; ws7r 77.44 n/y; ws8r 73.18 n/y; ws9r 57.03 n/y; ws10r 63.57 n/y; ws11r 62.85 n/y; ws12r 57.76 n/y | 2026-10-26 23:38:20 | 2026-10-26 23:38:55 | 2026-10-26 23:32:00 | 2026-10-26 23:32:35 |
| 2026-10-26 23:42:00 | A | ws2r | HIGH | oob -> ib | ws3r | ws3r 93.73 y/y; ws4r 94.79 y/y; ws5r 94.76 y/y; ws6r 92.16 y/y; ws7r 76.83 n/y; ws8r 73.18 n/y; ws9r 69.14 n/y; ws10r 62.92 n/y; ws11r 62.85 n/y; ws12r 57.76 n/y | 2026-10-26 23:40:45 | 2026-10-26 23:41:20 | 2026-10-26 23:32:05 | 2026-10-26 23:32:40 |
| 2026-10-26 23:42:00 | B | ws1r | HIGH | oob -> ib + ex-fence -> in-fence | ws2r | ws2r 93.58 y/y; ws3r 94.01 y/y; ws4r 96.29 y/y; ws5r 90.59 y/y; ws6r 78.17 n/y; ws7r 73.05 n/y; ws8r 63.38 n/y; ws9r 57.03 n/y; ws10r 52.37 n/y; ws11r 54.41 n/y; ws12r 52.46 n/y | 2026-10-26 23:40:45 | 2026-10-26 23:41:20 | 2026-10-26 23:40:45 | 2026-10-26 23:41:20 |
| 2026-10-26 23:42:05 | A | ws2r | HIGH | ex-fence -> in-fence | ws3r | ws3r 90.10 y/y; ws4r 92.90 y/y; ws5r 93.63 y/y; ws6r 91.30 y/y; ws7r 76.14 n/y; ws8r 73.18 n/y; ws9r 68.48 n/y; ws10r 62.19 n/y; ws11r 62.41 n/y; ws12r 57.76 n/y | 2026-10-26 23:40:45 | 2026-10-26 23:41:20 | 2026-10-26 23:32:05 | 2026-10-26 23:32:40 |
| 2026-10-26 23:42:50 | A | ws2r | HIGH | ex-fence -> in-fence | ws3r | ws3r 91.85 y/y; ws4r 93.82 y/y; ws5r 94.18 y/y; ws6r 91.72 y/y; ws7r 76.48 n/y; ws8r 73.18 n/y; ws9r 68.81 n/y; ws10r 62.55 n/y; ws11r 62.74 n/y; ws12r 57.76 n/y | 2026-10-26 23:40:45 | 2026-10-26 23:41:20 | 2026-10-26 23:32:05 | 2026-10-26 23:32:40 |
| 2026-10-26 23:43:25 | A | ws2r | HIGH | oob -> ib | ws3r | ws3r 95.06 y/y; ws4r 95.46 y/y; ws5r 95.16 y/y; ws6r 92.46 y/y; ws7r 77.07 n/y; ws8r 73.18 n/y; ws9r 69.38 n/y; ws10r 63.18 n/y; ws11r 62.85 n/y; ws12r 57.76 n/y | 2026-10-26 23:40:45 | 2026-10-26 23:41:20 | 2026-10-26 23:32:05 | 2026-10-26 23:32:40 |
| 2026-10-26 23:44:00 | A | ws2r | HIGH | oob -> ib + ex-fence -> in-fence | ws3r | ws3r 95.06 y/y; ws4r 97.54 y/y; ws5r 96.67 y/y; ws6r 92.46 y/y; ws7r 77.57 n/y; ws8r 79.66 n/y; ws9r 69.38 n/y; ws10r 64.13 n/y; ws11r 62.85 n/y; ws12r 57.76 n/y | 2026-10-26 23:40:45 | 2026-10-26 23:41:20 | 2026-10-26 23:32:05 | 2026-10-26 23:32:40 |
| 2026-10-26 23:44:45 | A | ws2r | HIGH | ex-fence -> in-fence | ws3r | ws3r 95.06 y/y; ws4r 96.63 y/y; ws5r 96.44 y/y; ws6r 92.46 y/y; ws7r 77.57 n/y; ws8r 79.37 n/y; ws9r 69.38 n/y; ws10r 63.98 n/y; ws11r 62.85 n/y; ws12r 57.76 n/y | 2026-10-26 23:40:45 | 2026-10-26 23:41:20 | 2026-10-26 23:32:05 | 2026-10-26 23:32:40 |
| 2026-10-26 23:45:30 | A | ws2r | HIGH | ex-fence -> in-fence | ws3r | ws3r 96.12 y/y; ws4r 98.01 y/y; ws5r 98.44 y/y; ws6r 92.46 y/y; ws7r 77.57 n/y; ws8r 79.80 n/y; ws9r 69.38 n/y; ws10r 64.13 n/y; ws11r 62.85 n/y; ws12r 57.76 n/y | 2026-10-26 23:40:45 | 2026-10-26 23:41:20 | 2026-10-26 23:32:05 | 2026-10-26 23:32:40 |
| 2026-10-26 23:46:00 | B | ws2r | HIGH | oob -> ib + ex-fence -> in-fence | ws3r | ws3r 95.06 y/y; ws4r 98.01 y/y; ws5r 96.22 y/y; ws6r 78.17 n/y; ws7r 73.05 n/y; ws8r 73.18 n/y; ws9r 57.03 n/y; ws10r 52.37 n/y; ws11r 54.41 n/y; ws12r 52.46 n/y | 2026-10-26 23:40:45 | 2026-10-26 23:41:20 | 2026-10-26 23:32:05 | 2026-10-26 23:32:40 |
| 2026-10-26 23:46:10 | A | ws1r | LOW | ex-fence -> in-fence | none | ws2r 67.09 n/y; ws3r 96.12 n/n; ws4r 98.01 n/n; ws5r 98.64 n/n; ws6r 92.46 n/n; ws7r 77.57 n/n; ws8r 79.80 n/n; ws9r 69.38 n/n; ws10r 64.13 n/n; ws11r 62.85 n/n; ws12r 57.76 n/n | 2026-10-26 23:39:00 | 2026-10-26 23:39:35 | - | - |
| 2026-10-26 23:47:00 | A | ws1r | LOW | ex-fence -> in-fence | none | ws2r 66.77 n/y; ws3r 96.12 n/n; ws4r 98.01 n/n; ws5r 98.64 n/n; ws6r 92.46 n/n; ws7r 77.57 n/n; ws8r 79.80 n/n; ws9r 69.38 n/n; ws10r 64.13 n/n; ws11r 62.85 n/n; ws12r 57.76 n/n | 2026-10-26 23:39:00 | 2026-10-26 23:39:35 | - | - |
| 2026-10-26 23:48:00 | B | ws1r | LOW | ex-fence -> in-fence | none | ws2r 68.48 n/y; ws3r 96.12 n/n; ws4r 98.01 n/n; ws5r 96.22 n/n; ws6r 92.46 n/n; ws7r 77.57 n/n; ws8r 73.18 n/n; ws9r 57.03 n/n; ws10r 52.37 n/n; ws11r 54.41 n/n; ws12r 57.76 n/y | 2026-10-26 23:47:00 | 2026-10-26 23:47:35 | - | - |
| 2026-10-26 23:49:20 | A | ws3r | HIGH | oob -> ib | ws4r | ws4r 92.69 y/y; ws5r 97.72 y/y; ws6r 94.01 y/y; ws7r 89.58 y/y; ws8r 79.10 n/y; ws9r 69.38 n/y; ws10r 63.71 n/y; ws11r 62.85 n/y; ws12r 62.28 n/y | 2026-10-26 23:48:40 | 2026-10-26 23:49:15 | 2026-10-26 23:41:50 | 2026-10-26 23:42:25 |
| 2026-10-26 23:51:00 | A | ws3r | HIGH | oob -> ib | none | ws4r 96.39 y/n; ws5r 98.22 y/y; ws6r 96.01 y/y; ws7r 90.78 y/y; ws8r 79.80 n/y; ws9r 83.66 y/y; ws10r 75.26 n/y; ws11r 71.15 n/y; ws12r 63.57 n/y | 2026-10-26 23:48:40 | 2026-10-26 23:49:15 | - | - |
| 2026-10-26 23:51:30 | A | ws3r | HIGH | ex-fence -> in-fence | none | ws4r 94.44 y/n; ws5r 97.92 y/y; ws6r 94.97 y/y; ws7r 90.16 y/y; ws8r 79.80 n/y; ws9r 83.66 y/y; ws10r 75.26 n/y; ws11r 71.15 n/y; ws12r 62.91 n/y | 2026-10-26 23:48:40 | 2026-10-26 23:49:15 | - | - |
| 2026-10-26 23:54:00 | A | ws3r | HIGH | ex-fence -> in-fence | none | ws4r 86.99 y/n; ws5r 98.03 y/y; ws6r 94.61 y/y; ws7r 90.28 y/y; ws8r 94.09 y/y; ws9r 83.66 y/y; ws10r 75.26 n/y; ws11r 71.15 n/y; ws12r 63.04 n/y | 2026-10-26 23:48:40 | 2026-10-26 23:49:15 | - | - |
| 2026-10-26 23:54:00 | B | ws3r | HIGH | oob -> ib | none | ws4r 94.44 y/n; ws5r 98.22 y/y; ws6r 96.01 y/y; ws7r 77.57 n/y; ws8r 79.80 n/y; ws9r 69.38 n/y; ws10r 64.13 n/y; ws11r 62.85 n/y; ws12r 57.76 n/y | 2026-10-26 23:48:40 | 2026-10-26 23:49:15 | - | - |
| 2026-10-26 23:54:05 | A | ws1r | LOW | ex-fence -> in-fence | none | ws2r 24.06 n/y; ws3r 67.91 n/y; ws4r 87.74 n/y; ws5r 98.22 n/y; ws6r 95.89 n/y; ws7r 90.78 n/n; ws8r 94.09 n/n; ws9r 83.66 n/n; ws10r 75.26 n/n; ws11r 71.15 n/n; ws12r 63.57 n/n | 2026-10-26 23:52:00 | 2026-10-26 23:52:35 | - | - |
| 2026-10-26 23:55:50 | A | ws1r | LOW | oob -> ib + ex-fence -> in-fence | none | ws2r 29.04 n/y; ws3r 71.90 n/y; ws4r 89.71 n/y; ws5r 98.95 n/n; ws6r 96.93 n/y; ws7r 95.05 n/n; ws8r 94.09 n/n; ws9r 83.66 n/n; ws10r 75.26 n/n; ws11r 71.15 n/n; ws12r 64.72 n/n | 2026-10-26 23:52:00 | 2026-10-26 23:52:35 | - | - |
| 2026-10-26 23:56:00 | A | ws4r | HIGH | oob -> ib + ex-fence -> in-fence | ws5r | ws5r 98.95 y/y; ws6r 96.56 y/y; ws7r 94.71 y/y; ws8r 94.09 y/y; ws9r 83.66 y/y; ws10r 75.26 n/y; ws11r 71.15 n/y; ws12r 64.72 n/y | 2026-10-26 23:51:30 | 2026-10-26 23:52:05 | 2026-10-26 23:00:50 | 2026-10-26 23:01:25 |
| 2026-10-26 23:56:00 | B | ws1r | LOW | ex-fence -> in-fence | none | ws2r 28.75 n/y; ws3r 80.56 n/y; ws4r 89.58 n/y; ws5r 98.03 n/y; ws6r 96.01 n/n; ws7r 90.28 n/n; ws8r 79.80 n/n; ws9r 69.38 n/n; ws10r 64.13 n/n; ws11r 62.85 n/n; ws12r 57.76 n/n | 2026-10-26 23:52:00 | 2026-10-26 23:52:35 | - | - |
| 2026-10-26 23:57:00 | B | ws3r | HIGH | ex-fence -> in-fence | none | ws4r 89.58 y/n; ws5r 98.03 y/y; ws6r 96.01 y/y; ws7r 90.28 y/y; ws8r 79.80 n/y; ws9r 69.38 n/y; ws10r 64.13 n/y; ws11r 62.85 n/y; ws12r 57.76 n/y | 2026-10-26 23:48:40 | 2026-10-26 23:49:15 | - | - |
| 2026-10-26 23:58:20 | A | ws4r | HIGH | ex-fence -> in-fence | ws5r | ws5r 98.95 y/y; ws6r 96.56 y/y; ws7r 94.71 y/y; ws8r 94.09 y/y; ws9r 83.66 y/y; ws10r 75.26 n/y; ws11r 71.15 n/y; ws12r 64.72 n/y | 2026-10-26 23:51:30 | 2026-10-26 23:52:05 | 2026-10-26 23:00:50 | 2026-10-26 23:01:25 |
| 2026-10-27 00:00:00 | A | ws4r | HIGH | ex-fence -> in-fence | ws5r | ws5r 94.34 y/y; ws6r 92.98 y/y; ws7r 91.95 y/y; ws8r 98.66 y/y; ws9r 97.21 y/y; ws10r 84.81 y/y; ws11r 81.90 y/y; ws12r 71.00 n/y | 2026-10-26 23:51:30 | 2026-10-26 23:52:05 | 2026-10-26 23:00:50 | 2026-10-26 23:01:25 |
| 2026-10-27 00:00:00 | B | ws4r | HIGH | oob -> ib | ws5r | ws5r 98.95 y/y; ws6r 96.86 y/y; ws7r 94.98 y/y; ws8r 94.09 y/y; ws9r 83.66 y/y; ws10r 75.26 n/y; ws11r 71.15 n/y; ws12r 64.72 n/y | 2026-10-26 23:51:30 | 2026-10-26 23:52:05 | 2026-10-26 23:00:50 | 2026-10-26 23:01:25 |
| 2026-10-27 00:01:20 | A | ws10r | HIGH | oob -> ib | ws11r | ws11r 81.24 y/y; ws12r 70.18 n/y | 2026-10-26 23:22:20 | 2026-10-26 23:22:55 | 2026-10-26 22:44:05 | 2026-10-26 22:44:40 |
| 2026-10-27 00:02:00 | A | ws10r | HIGH | oob -> ib | ws11r | ws11r 81.90 y/y; ws12r 71.00 n/y | 2026-10-26 23:22:20 | 2026-10-26 23:22:55 | 2026-10-26 22:44:05 | 2026-10-26 22:44:40 |
| 2026-10-27 00:02:10 | A | ws10r | HIGH | oob -> ib | ws11r | ws11r 82.04 y/y; ws12r 71.17 n/y | 2026-10-26 23:22:20 | 2026-10-26 23:22:55 | 2026-10-26 22:44:05 | 2026-10-26 22:44:40 |
| 2026-10-27 00:03:45 | A | ws4r | HIGH | ex-fence -> in-fence | none | ws5r 98.95 y/n; ws6r 96.77 y/n; ws7r 95.34 y/y; ws8r 100.00 y/y; ws9r 97.95 y/y; ws10r 85.71 y/y; ws11r 82.60 y/y; ws12r 71.88 n/y | 2026-10-26 23:51:30 | 2026-10-26 23:52:05 | - | - |
| 2026-10-27 00:04:00 | B | ws4r | HIGH | ex-fence -> in-fence | ws5r | ws5r 98.95 y/y; ws6r 96.86 y/y; ws7r 94.98 y/y; ws8r 94.09 y/y; ws9r 83.66 y/y; ws10r 75.26 n/y; ws11r 71.15 n/y; ws12r 64.72 n/y | 2026-10-26 23:51:30 | 2026-10-26 23:52:05 | 2026-10-27 00:00:00 | 2026-10-27 00:00:35 |
| 2026-10-27 00:04:20 | A | ws10r | HIGH | oob -> ib | ws11r | ws11r 82.04 y/y; ws12r 71.17 n/y | 2026-10-26 23:22:20 | 2026-10-26 23:22:55 | 2026-10-26 22:44:05 | 2026-10-26 22:44:40 |
| 2026-10-27 00:05:25 | A | ws5r | HIGH | oob -> ib | none | ws6r 92.14 y/n; ws7r 91.28 y/y; ws8r 98.16 y/y; ws9r 96.94 y/y; ws10r 84.47 y/y; ws11r 81.63 y/y; ws12r 70.67 n/y | 2026-10-27 00:00:00 | 2026-10-27 00:00:35 | - | - |
| 2026-10-27 00:05:25 | A | ws10r | HIGH | oob -> ib | ws11r | ws11r 81.63 y/y; ws12r 70.67 n/y | 2026-10-26 23:22:20 | 2026-10-26 23:22:55 | 2026-10-26 22:44:05 | 2026-10-26 22:44:40 |
| 2026-10-27 00:06:35 | A | ws10r | HIGH | oob -> ib | ws11r | ws11r 81.90 y/y; ws12r 71.00 n/y | 2026-10-26 23:22:20 | 2026-10-26 23:22:55 | 2026-10-26 22:44:05 | 2026-10-26 22:44:40 |
| 2026-10-27 00:10:15 | A | ws5r | HIGH | oob -> ib | none | ws6r 95.35 y/n; ws7r 95.76 y/y; ws8r 100.00 y/y; ws9r 100.00 y/y; ws10r 97.76 y/y; ws11r 82.60 y/y; ws12r 71.88 n/y | 2026-10-27 00:05:25 | 2026-10-27 00:06:00 | - | - |
| 2026-10-27 00:14:15 | A | ws1r | HIGH | oob -> ib | none | ws2r 74.63 n/y; ws3r 51.17 n/y; ws4r 72.27 n/y; ws5r 97.97 y/y; ws6r 92.89 y/y; ws7r 94.05 y/y; ws8r 100.00 y/y; ws9r 100.00 y/y; ws10r 100.00 y/y; ws11r 96.89 y/y; ws12r 83.42 y/y | 2026-10-27 00:10:15 | 2026-10-27 00:10:50 | - | - |
| 2026-10-27 00:14:20 | A | ws1r | HIGH | ex-fence -> in-fence | none | ws2r 71.59 n/y; ws3r 47.14 n/y; ws4r 68.18 n/y; ws5r 97.97 y/n; ws6r 89.07 y/y; ws7r 92.06 y/y; ws8r 100.00 y/y; ws9r 100.00 y/y; ws10r 100.00 y/y; ws11r 96.89 y/y; ws12r 82.76 y/y | 2026-10-27 00:10:15 | 2026-10-27 00:10:50 | - | - |
| 2026-10-27 00:15:00 | A | ws6r | HIGH | oob -> ib | ws7r | ws7r 89.49 y/y; ws8r 100.00 y/y; ws9r 100.00 y/y; ws10r 100.00 y/y; ws11r 96.89 y/y; ws12r 81.91 y/y | 2026-10-27 00:14:15 | 2026-10-27 00:14:50 | 2026-10-27 00:14:20 | 2026-10-27 00:14:55 |
| 2026-10-27 00:15:00 | B | ws1r | HIGH | oob -> ib + ex-fence -> in-fence | none | ws2r 67.15 n/y; ws3r 46.39 n/y; ws4r 74.96 n/n; ws5r 97.97 y/n; ws6r 95.35 y/y; ws7r 95.76 y/y; ws8r 100.00 y/y; ws9r 97.95 y/y; ws10r 85.71 y/y; ws11r 82.60 y/y; ws12r 71.88 n/y | 2026-10-27 00:14:15 | 2026-10-27 00:14:50 | - | - |
| 2026-10-27 00:15:30 | A | ws6r | HIGH | oob -> ib | none | ws7r 88.13 y/n; ws8r 100.00 y/y; ws9r 100.00 y/y; ws10r 100.00 y/y; ws11r 96.89 y/y; ws12r 81.44 y/y | 2026-10-27 00:14:15 | 2026-10-27 00:14:50 | - | - |
| 2026-10-27 00:18:35 | A | ws2r | HIGH | oob -> ib | none | ws3r 57.60 n/y; ws4r 77.83 n/n; ws5r 98.42 y/y; ws6r 87.73 y/n; ws7r 95.76 y/n; ws8r 100.00 y/y; ws9r 97.63 y/y; ws10r 100.00 y/y; ws11r 96.89 y/y; ws12r 83.83 y/y | 2026-10-27 00:06:00 | 2026-10-27 00:06:35 | - | - |
| 2026-10-27 00:19:00 | A | ws6r | HIGH | oob -> ib | none | ws7r 95.76 y/n; ws8r 100.00 y/y; ws9r 96.21 y/y; ws10r 100.00 y/y; ws11r 96.89 y/y; ws12r 83.83 y/y | 2026-10-27 00:14:15 | 2026-10-27 00:14:50 | - | - |
| 2026-10-27 00:19:20 | A | ws2r | HIGH | ex-fence -> in-fence | none | ws3r 51.88 n/y; ws4r 77.36 n/y; ws5r 98.42 y/y; ws6r 81.06 y/n; ws7r 95.76 y/n; ws8r 100.00 y/y; ws9r 95.07 y/y; ws10r 100.00 y/y; ws11r 96.89 y/y; ws12r 83.83 y/y | 2026-10-27 00:18:35 | 2026-10-27 00:19:10 | - | - |
| 2026-10-27 00:19:55 | A | ws6r | HIGH | oob -> ib | none | ws7r 95.76 y/n; ws8r 100.00 y/y; ws9r 96.21 y/y; ws10r 100.00 y/y; ws11r 96.89 y/y; ws12r 83.83 y/y | 2026-10-27 00:18:30 | 2026-10-27 00:19:05 | - | - |
| 2026-10-27 00:20:00 | A | ws2r | HIGH | ex-fence -> in-fence | none | ws3r 54.40 n/y; ws4r 82.66 y/y; ws5r 98.84 y/y; ws6r 84.38 y/n; ws7r 95.76 y/n; ws8r 100.00 y/y; ws9r 96.56 y/y; ws10r 100.00 y/y; ws11r 96.89 y/y; ws12r 83.83 y/y | 2026-10-27 00:18:35 | 2026-10-27 00:19:10 | - | - |
| 2026-10-27 00:20:30 | A | ws6r | HIGH | oob -> ib | none | ws7r 95.76 y/n; ws8r 100.00 y/y; ws9r 96.56 y/y; ws10r 100.00 y/y; ws11r 96.89 y/y; ws12r 83.83 y/y | 2026-10-27 00:18:30 | 2026-10-27 00:19:05 | - | - |
| 2026-10-27 00:20:50 | A | ws6r | HIGH | oob -> ib | none | ws7r 95.76 y/n; ws8r 100.00 y/y; ws9r 96.04 y/y; ws10r 99.75 y/y; ws11r 96.89 y/y; ws12r 83.83 y/y | 2026-10-27 00:20:15 | 2026-10-27 00:20:50 | - | - |
| 2026-10-27 00:21:45 | A | ws2r | HIGH | ex-fence -> in-fence | none | ws3r 47.88 n/y; ws4r 82.66 y/y; ws5r 98.84 y/y; ws6r 93.98 y/n; ws7r 95.76 y/y; ws8r 100.00 y/y; ws9r 99.58 y/y; ws10r 100.00 y/y; ws11r 96.89 y/y; ws12r 83.83 y/y | 2026-10-27 00:18:35 | 2026-10-27 00:19:10 | - | - |
| 2026-10-27 00:21:55 | A | ws2r | HIGH | ex-fence -> in-fence | none | ws3r 47.73 n/y; ws4r 82.66 y/y; ws5r 98.84 y/y; ws6r 93.31 y/n; ws7r 95.76 y/y; ws8r 100.00 y/y; ws9r 99.38 y/y; ws10r 100.00 y/y; ws11r 96.89 y/y; ws12r 83.83 y/y | 2026-10-27 00:18:35 | 2026-10-27 00:19:10 | - | - |
| 2026-10-27 00:22:00 | B | ws2r | HIGH | ex-fence -> in-fence | none | ws3r 52.45 n/y; ws4r 77.80 n/y; ws5r 98.42 y/y; ws6r 95.35 y/y; ws7r 95.76 y/y; ws8r 100.00 y/y; ws9r 100.00 y/y; ws10r 100.00 y/y; ws11r 96.89 y/y; ws12r 71.88 n/y | 2026-10-27 00:18:35 | 2026-10-27 00:19:10 | - | - |
| 2026-10-27 00:24:45 | A | ws6r | HIGH | oob -> ib | ws7r | ws7r 95.76 y/y; ws8r 100.00 y/y; ws9r 98.58 y/y; ws10r 100.00 y/y; ws11r 99.32 y/y; ws12r 98.11 y/y | 2026-10-27 00:23:40 | 2026-10-27 00:24:15 | 2026-10-27 00:14:20 | 2026-10-27 00:14:55 |
| 2026-10-27 00:25:20 | A | ws6r | HIGH | oob -> ib | ws7r | ws7r 95.76 y/y; ws8r 100.00 y/y; ws9r 100.00 y/y; ws10r 100.00 y/y; ws11r 100.00 y/y; ws12r 98.11 y/y | 2026-10-27 00:23:40 | 2026-10-27 00:24:15 | 2026-10-27 00:14:20 | 2026-10-27 00:14:55 |
| 2026-10-27 00:26:00 | A | ws1r | LOW | ex-fence -> in-fence | none | ws2r 41.81 n/y; ws3r 51.42 n/y; ws4r 88.95 n/n; ws5r 99.03 n/n; ws6r 84.60 n/y; ws7r 95.76 n/n; ws8r 100.00 n/n; ws9r 100.00 n/n; ws10r 100.00 n/n; ws11r 100.00 n/n; ws12r 98.11 n/n | 2026-10-27 00:21:00 | 2026-10-27 00:21:35 | - | - |
| 2026-10-27 00:26:30 | A | ws4r | HIGH | oob -> ib | ws5r | ws5r 87.53 y/y; ws6r 80.05 y/n; ws7r 95.76 y/y; ws8r 97.27 y/y; ws9r 97.26 y/y; ws10r 100.00 y/y; ws11r 98.19 y/y; ws12r 97.44 y/y | 2026-10-27 00:14:15 | 2026-10-27 00:14:50 | 2026-10-27 00:10:00 | 2026-10-27 00:10:35 |
| 2026-10-27 00:26:40 | A | ws4r | HIGH | ex-fence -> in-fence | ws5r | ws5r 84.74 y/y; ws6r 75.23 n/n; ws7r 91.46 y/y; ws8r 90.17 y/y; ws9r 94.75 y/y; ws10r 97.88 y/y; ws11r 96.03 y/y; ws12r 95.63 y/y | 2026-10-27 00:14:15 | 2026-10-27 00:14:50 | 2026-10-27 00:10:00 | 2026-10-27 00:10:35 |
| 2026-10-27 00:26:40 | A | ws5r | HIGH | oob -> ib | none | ws6r 75.23 n/n; ws7r 91.46 y/y; ws8r 90.17 y/y; ws9r 94.75 y/y; ws10r 97.88 y/y; ws11r 96.03 y/y; ws12r 95.63 y/y | 2026-10-27 00:10:00 | 2026-10-27 00:10:35 | - | - |
| 2026-10-27 00:26:40 | A | ws6r | HIGH | ex-fence -> in-fence | ws7r | ws7r 91.46 y/y; ws8r 90.17 y/y; ws9r 94.75 y/y; ws10r 97.88 y/y; ws11r 96.03 y/y; ws12r 95.63 y/y | 2026-10-27 00:23:40 | 2026-10-27 00:24:15 | 2026-10-27 00:14:20 | 2026-10-27 00:14:55 |
| 2026-10-27 00:27:05 | A | ws9r | HIGH | oob -> ib | ws10r | ws10r 95.61 y/y; ws11r 94.64 y/y; ws12r 94.48 y/y | 2026-10-27 00:26:25 | 2026-10-27 00:27:00 | 2026-10-26 23:22:20 | 2026-10-26 23:22:55 |
| 2026-10-27 00:27:20 | A | ws7r | HIGH | oob -> ib | none | ws8r 85.71 y/n; ws9r 83.96 y/y; ws10r 95.04 y/y; ws11r 94.29 y/y; ws12r 94.19 y/y | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 | - | - |
| 2026-10-27 00:27:35 | A | ws7r | HIGH | oob -> ib | none | ws8r 85.71 y/n; ws9r 84.18 y/y; ws10r 95.23 y/y; ws11r 94.40 y/y; ws12r 94.29 y/y | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 | - | - |
| 2026-10-27 00:28:00 | A | ws7r | HIGH | oob -> ib + ex-fence -> in-fence | none | ws8r 85.71 y/n; ws9r 83.96 y/y; ws10r 95.04 y/y; ws11r 94.29 y/y; ws12r 94.19 y/y | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 | - | - |
| 2026-10-27 00:28:00 | B | ws4r | HIGH | ex-fence -> in-fence | ws5r | ws5r 98.84 y/y; ws6r 89.51 y/n; ws7r 85.06 y/y; ws8r 100.00 y/y; ws9r 93.42 y/y; ws10r 100.00 y/y; ws11r 96.89 y/y; ws12r 83.83 y/y | 2026-10-27 00:26:25 | 2026-10-27 00:27:00 | 2026-10-27 00:26:25 | 2026-10-27 00:27:00 |
| 2026-10-27 00:28:55 | A | ws1r | LOW | oob -> ib | none | ws2r 29.99 n/y; ws3r 39.45 n/y; ws4r 66.72 n/y; ws5r 84.74 n/n; ws6r 75.23 n/y; ws7r 76.32 n/y; ws8r 90.17 n/y; ws9r 85.70 n/y; ws10r 97.88 n/y; ws11r 96.03 n/n; ws12r 95.63 n/n | 2026-10-27 00:21:00 | 2026-10-27 00:21:35 | - | - |
| 2026-10-27 00:29:20 | A | ws9r | HIGH | oob -> ib | ws10r | ws10r 95.42 y/y; ws11r 94.52 y/y; ws12r 94.39 y/y | 2026-10-27 00:26:25 | 2026-10-27 00:27:00 | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 |
| 2026-10-27 00:30:00 | A | ws5r | HIGH | ex-fence -> in-fence | none | ws6r 62.78 n/n; ws7r 70.78 n/n; ws8r 85.71 y/n; ws9r 82.53 y/n; ws10r 85.99 y/y; ws11r 93.49 y/y; ws12r 93.55 y/y | 2026-10-27 00:26:25 | 2026-10-27 00:27:00 | - | - |
| 2026-10-27 00:30:00 | B | ws5r | HIGH | oob -> ib | none | ws6r 75.23 n/n; ws7r 85.06 y/n; ws8r 100.00 y/y; ws9r 93.42 y/y; ws10r 94.32 y/y; ws11r 96.89 y/y; ws12r 83.83 y/y | 2026-10-27 00:26:25 | 2026-10-27 00:27:00 | - | - |
| 2026-10-27 00:30:00 | B | ws6r | HIGH | oob -> ib + ex-fence -> in-fence | none | ws7r 85.06 y/n; ws8r 100.00 y/y; ws9r 93.42 y/y; ws10r 94.32 y/y; ws11r 96.89 y/y; ws12r 83.83 y/y | 2026-10-27 00:23:40 | 2026-10-27 00:24:15 | - | - |
| 2026-10-27 00:30:20 | A | ws2r | LOW | oob -> ib | none | ws3r 24.96 n/y; ws4r 64.75 n/y; ws5r 71.45 n/y; ws6r 63.76 n/y; ws7r 74.54 n/y; ws8r 85.80 n/y; ws9r 84.61 n/y; ws10r 87.42 n/y; ws11r 94.64 n/n; ws12r 94.48 n/n | 2026-10-27 00:15:45 | 2026-10-27 00:16:20 | - | - |
| 2026-10-27 00:30:40 | A | ws9r | HIGH | oob -> ib | ws10r | ws10r 85.99 y/y; ws11r 93.49 y/y; ws12r 93.55 y/y | 2026-10-27 00:26:25 | 2026-10-27 00:27:00 | 2026-10-27 00:29:15 | 2026-10-27 00:29:50 |
| 2026-10-27 00:30:45 | A | ws10r | HIGH | oob -> ib | ws11r | ws11r 92.96 y/y; ws12r 93.11 y/y | 2026-10-27 00:29:15 | 2026-10-27 00:29:50 | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 |
| 2026-10-27 00:31:40 | A | ws1r | LOW | oob -> ib | ws2r | ws2r 15.42 y/y; ws3r 25.31 n/y; ws4r 65.14 n/y; ws5r 71.71 n/y; ws6r 64.02 n/y; ws7r 74.89 n/y; ws8r 86.55 n/y; ws9r 85.06 n/y; ws10r 87.58 n/y; ws11r 94.88 n/n; ws12r 94.68 n/n | 2026-10-27 00:21:00 | 2026-10-27 00:21:35 | 2026-10-27 00:15:45 | 2026-10-27 00:16:20 |
| 2026-10-27 00:31:40 | A | ws2r | LOW | oob -> ib | none | ws3r 25.31 n/y; ws4r 65.14 n/y; ws5r 71.71 n/y; ws6r 64.02 n/y; ws7r 74.89 n/y; ws8r 86.55 n/y; ws9r 85.06 n/y; ws10r 87.58 n/y; ws11r 94.88 n/n; ws12r 94.68 n/n | 2026-10-27 00:15:45 | 2026-10-27 00:16:20 | - | - |
| 2026-10-27 00:31:55 | A | ws9r | HIGH | oob -> ib | ws10r | ws10r 87.26 y/y; ws11r 94.40 y/y; ws12r 94.29 y/y | 2026-10-27 00:26:25 | 2026-10-27 00:27:00 | 2026-10-27 00:29:15 | 2026-10-27 00:29:50 |
| 2026-10-27 00:32:00 | A | ws1r | LOW | oob -> ib | ws2r | ws2r 10.18 y/y; ws3r 24.78 n/y; ws4r 54.67 n/y; ws5r 71.32 n/y; ws6r 63.63 n/y; ws7r 74.37 n/y; ws8r 71.58 n/y; ws9r 84.39 n/y; ws10r 87.35 n/y; ws11r 94.52 n/y; ws12r 94.39 n/n | 2026-10-27 00:21:00 | 2026-10-27 00:21:35 | 2026-10-27 00:15:45 | 2026-10-27 00:16:20 |
| 2026-10-27 00:32:00 | A | ws8r | HIGH | oob -> ib + ex-fence -> in-fence | none | ws9r 84.39 y/n; ws10r 87.35 y/y; ws11r 94.52 y/y; ws12r 94.39 y/y | 2026-10-27 00:26:30 | 2026-10-27 00:27:05 | - | - |
| 2026-10-27 00:32:45 | A | ws1r | LOW | ex-fence -> in-fence | ws2r | ws2r 12.47 y/y; ws3r 25.97 n/y; ws4r 56.24 n/y; ws5r 72.21 n/y; ws6r 64.51 n/y; ws7r 75.55 n/y; ws8r 72.57 n/y; ws9r 85.35 n/y; ws10r 87.88 n/y; ws11r 95.38 n/y; ws12r 95.09 n/n | 2026-10-27 00:31:30 | 2026-10-27 00:32:05 | 2026-10-27 00:15:45 | 2026-10-27 00:16:20 |
| 2026-10-27 00:32:55 | A | ws9r | HIGH | oob -> ib | ws10r | ws10r 87.26 y/y; ws11r 94.40 y/y; ws12r 94.29 y/y | 2026-10-27 00:26:25 | 2026-10-27 00:27:00 | 2026-10-27 00:29:15 | 2026-10-27 00:29:50 |
| 2026-10-27 00:33:00 | A | ws1r | LOW | ex-fence -> in-fence | ws2r | ws2r 8.18 y/y; ws3r 17.76 y/y; ws4r 54.42 n/y; ws5r 70.45 n/y; ws6r 62.78 n/y; ws7r 70.78 n/y; ws8r 71.43 n/y; ws9r 82.15 n/y; ws10r 85.44 n/y; ws11r 84.53 n/y; ws12r 93.37 n/n | 2026-10-27 00:31:30 | 2026-10-27 00:32:05 | 2026-10-27 00:15:45 | 2026-10-27 00:16:20 |
| 2026-10-27 00:33:00 | A | ws11r | HIGH | oob -> ib | ws12r | ws12r 93.37 y/y | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 | 2026-10-27 00:29:40 | 2026-10-27 00:30:15 |
| 2026-10-27 00:33:00 | B | ws1r | LOW | oob -> ib | ws2r | ws2r 14.59 y/y; ws3r 24.60 n/y; ws4r 64.54 n/y; ws5r 84.74 n/y; ws6r 75.23 n/y; ws7r 85.06 n/y; ws8r 85.71 n/y; ws9r 93.42 n/y; ws10r 94.32 n/y; ws11r 94.40 n/y; ws12r 83.83 n/n | 2026-10-27 00:31:30 | 2026-10-27 00:32:05 | 2026-10-27 00:15:45 | 2026-10-27 00:16:20 |
| 2026-10-27 00:33:10 | A | ws10r | HIGH | oob -> ib | ws11r | ws11r 83.80 y/y; ws12r 93.02 y/y | 2026-10-27 00:29:15 | 2026-10-27 00:29:50 | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 |
| 2026-10-27 00:33:20 | A | ws9r | HIGH | ex-fence -> in-fence | ws10r | ws10r 82.22 y/y; ws11r 82.27 y/y; ws12r 92.30 y/y | 2026-10-27 00:26:25 | 2026-10-27 00:27:00 | 2026-10-27 00:29:15 | 2026-10-27 00:29:50 |
| 2026-10-27 00:33:40 | A | ws9r | HIGH | ex-fence -> in-fence | ws10r | ws10r 81.77 y/y; ws11r 81.95 y/y; ws12r 92.14 y/y | 2026-10-27 00:26:25 | 2026-10-27 00:27:00 | 2026-10-27 00:29:15 | 2026-10-27 00:29:50 |
| 2026-10-27 00:34:00 | A | ws1r | LOW | ex-fence -> in-fence | ws2r | ws2r 5.48 y/y; ws3r 17.76 y/y; ws4r 54.42 n/y; ws5r 70.45 n/y; ws6r 62.78 n/y; ws7r 70.78 n/y; ws8r 71.43 n/y; ws9r 81.03 n/y; ws10r 83.88 n/y; ws11r 83.45 n/y; ws12r 92.86 n/n | 2026-10-27 00:31:30 | 2026-10-27 00:32:05 | 2026-10-27 00:15:45 | 2026-10-27 00:16:20 |
| 2026-10-27 00:35:00 | B | ws1r | LOW | ex-fence -> in-fence | ws2r | ws2r 8.18 y/y; ws3r 24.60 n/y; ws4r 64.54 n/y; ws5r 70.45 n/y; ws6r 75.23 n/y; ws7r 70.78 n/y; ws8r 85.71 n/y; ws9r 93.42 n/y; ws10r 94.32 n/y; ws11r 94.40 n/y; ws12r 83.83 n/n | 2026-10-27 00:34:00 | 2026-10-27 00:34:35 | 2026-10-27 00:15:45 | 2026-10-27 00:16:20 |
| 2026-10-27 00:35:00 | B | ws5r | HIGH | ex-fence -> in-fence | none | ws6r 75.23 n/n; ws7r 70.78 n/n; ws8r 85.71 y/n; ws9r 93.42 y/y; ws10r 94.32 y/y; ws11r 94.40 y/y; ws12r 83.83 y/y | 2026-10-27 00:26:25 | 2026-10-27 00:27:00 | - | - |
| 2026-10-27 00:35:00 | B | ws7r | HIGH | oob -> ib + ex-fence -> in-fence | none | ws8r 85.71 y/n; ws9r 93.42 y/y; ws10r 94.32 y/y; ws11r 94.40 y/y; ws12r 83.83 y/y | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 | - | - |
| 2026-10-27 00:35:25 | A | ws10r | HIGH | oob -> ib | ws11r | ws11r 84.16 y/y; ws12r 93.20 y/y | 2026-10-27 00:29:15 | 2026-10-27 00:29:50 | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 |
| 2026-10-27 00:36:00 | A | ws9r | HIGH | ex-fence -> in-fence | none | ws10r 87.35 y/n; ws11r 86.58 y/y; ws12r 89.98 y/y | 2026-10-27 00:26:25 | 2026-10-27 00:27:00 | - | - |
| 2026-10-27 00:36:00 | B | ws9r | HIGH | oob -> ib | ws10r | ws10r 94.32 y/y; ws11r 94.40 y/y; ws12r 93.91 y/y | 2026-10-27 00:26:25 | 2026-10-27 00:27:00 | 2026-10-27 00:29:15 | 2026-10-27 00:29:50 |
| 2026-10-27 00:36:05 | A | ws2r | LOW | oob -> ib | ws3r | ws3r 7.34 y/y; ws4r 42.86 n/y; ws5r 60.50 n/y; ws6r 51.88 n/y; ws7r 62.14 n/y; ws8r 72.44 n/y; ws9r 70.53 n/y; ws10r 87.80 n/y; ws11r 87.02 n/y; ws12r 90.33 n/y | 2026-10-27 00:15:45 | 2026-10-27 00:16:20 | 2026-10-27 00:24:00 | 2026-10-27 00:24:35 |
| 2026-10-27 00:36:30 | A | ws11r | HIGH | oob -> ib | ws12r | ws12r 89.01 y/y | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 | 2026-10-27 00:35:20 | 2026-10-27 00:35:55 |
| 2026-10-27 00:36:40 | A | ws10r | HIGH | oob -> ib | ws11r | ws11r 84.16 y/y; ws12r 88.38 y/y | 2026-10-27 00:29:15 | 2026-10-27 00:29:50 | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 |
| 2026-10-27 00:37:30 | A | ws11r | HIGH | oob -> ib | ws12r | ws12r 88.69 y/y | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 | 2026-10-27 00:35:20 | 2026-10-27 00:35:55 |
| 2026-10-27 00:37:40 | A | ws10r | HIGH | oob -> ib | ws11r | ws11r 84.16 y/y; ws12r 88.38 y/y | 2026-10-27 00:29:15 | 2026-10-27 00:29:50 | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 |
| 2026-10-27 00:37:50 | A | ws11r | HIGH | oob -> ib | ws12r | ws12r 88.85 y/y | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 | 2026-10-27 00:35:20 | 2026-10-27 00:35:55 |
| 2026-10-27 00:38:00 | A | ws2r | LOW | oob -> ib | ws3r | ws3r 4.52 y/y; ws4r 40.13 n/y; ws5r 58.63 n/y; ws6r 49.95 n/y; ws7r 59.84 n/y; ws8r 71.43 n/y; ws9r 69.05 n/y; ws10r 85.71 n/y; ws11r 84.72 n/y; ws12r 88.85 n/y | 2026-10-27 00:35:35 | 2026-10-27 00:36:10 | 2026-10-27 00:24:00 | 2026-10-27 00:24:35 |
| 2026-10-27 00:38:10 | A | ws2r | LOW | oob -> ib | ws3r | ws3r 4.52 y/y; ws4r 40.13 n/y; ws5r 59.02 n/y; ws6r 49.95 n/y; ws7r 60.32 n/y; ws8r 71.43 n/y; ws9r 69.05 n/y; ws10r 86.56 n/y; ws11r 85.29 n/y; ws12r 89.33 n/y | 2026-10-27 00:35:35 | 2026-10-27 00:36:10 | 2026-10-27 00:24:00 | 2026-10-27 00:24:35 |
| 2026-10-27 00:38:40 | A | ws2r | LOW | ex-fence -> in-fence | ws3r | ws3r 8.90 y/y; ws4r 44.35 n/y; ws5r 61.26 n/y; ws6r 52.97 n/y; ws7r 63.10 n/y; ws8r 73.47 n/y; ws9r 71.47 n/y; ws10r 88.36 n/y; ws11r 87.56 n/y; ws12r 90.76 n/y | 2026-10-27 00:35:35 | 2026-10-27 00:36:10 | 2026-10-27 00:24:00 | 2026-10-27 00:24:35 |
| 2026-10-27 00:39:35 | A | ws11r | HIGH | oob -> ib | ws12r | ws12r 88.85 y/y | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 | 2026-10-27 00:35:20 | 2026-10-27 00:35:55 |
| 2026-10-27 00:39:40 | A | ws10r | HIGH | oob -> ib | ws11r | ws11r 82.93 y/y; ws12r 87.35 y/y | 2026-10-27 00:29:15 | 2026-10-27 00:29:50 | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 |
| 2026-10-27 00:40:00 | A | ws10r | HIGH | ex-fence -> in-fence | ws11r | ws11r 81.48 y/y; ws12r 86.13 y/y | 2026-10-27 00:29:15 | 2026-10-27 00:29:50 | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 |
| 2026-10-27 00:40:00 | B | ws8r | HIGH | oob -> ib + ex-fence -> in-fence | none | ws9r 83.34 y/n; ws10r 81.33 y/y; ws11r 94.40 y/y; ws12r 93.91 y/y | 2026-10-27 00:26:30 | 2026-10-27 00:27:05 | - | - |
| 2026-10-27 00:40:00 | B | ws10r | HIGH | oob -> ib | ws11r | ws11r 94.40 y/y; ws12r 93.91 y/y | 2026-10-27 00:29:15 | 2026-10-27 00:29:50 | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 |
| 2026-10-27 00:40:05 | A | ws2r | LOW | oob -> ib | ws3r | ws3r 6.77 y/y; ws4r 29.25 n/y; ws5r 43.40 n/y; ws6r 49.95 n/y; ws7r 58.06 n/y; ws8r 57.55 n/y; ws9r 69.05 n/y; ws10r 67.49 n/y; ws11r 82.11 n/y; ws12r 86.66 n/y | 2026-10-27 00:35:35 | 2026-10-27 00:36:10 | 2026-10-27 00:38:35 | 2026-10-27 00:39:10 |
| 2026-10-27 00:40:25 | A | ws2r | LOW | oob -> ib | ws3r | ws3r 6.77 y/y; ws4r 29.48 n/y; ws5r 43.57 n/y; ws6r 49.95 n/y; ws7r 58.06 n/y; ws8r 57.68 n/y; ws9r 69.05 n/y; ws10r 67.63 n/y; ws11r 82.27 n/y; ws12r 86.79 n/y | 2026-10-27 00:35:35 | 2026-10-27 00:36:10 | 2026-10-27 00:38:35 | 2026-10-27 00:39:10 |
| 2026-10-27 00:41:00 | A | ws2r | LOW | ex-fence -> in-fence | ws3r | ws3r 6.77 y/y; ws4r 31.23 n/y; ws5r 44.97 n/y; ws6r 49.95 n/y; ws7r 58.99 n/y; ws8r 58.79 n/y; ws9r 69.05 n/y; ws10r 68.82 n/y; ws11r 83.80 n/y; ws12r 88.08 n/y | 2026-10-27 00:40:25 | 2026-10-27 00:41:00 | 2026-10-27 00:38:35 | 2026-10-27 00:39:10 |
| 2026-10-27 00:42:00 | B | ws2r | LOW | oob -> ib + ex-fence -> in-fence | ws3r | ws3r 8.23 y/y; ws4r 40.13 n/y; ws5r 57.14 n/y; ws6r 51.12 n/y; ws7r 61.48 n/y; ws8r 71.43 n/y; ws9r 83.34 n/y; ws10r 81.33 n/y; ws11r 94.40 n/y; ws12r 93.91 n/n | 2026-10-27 00:40:25 | 2026-10-27 00:41:00 | 2026-10-27 00:38:35 | 2026-10-27 00:39:10 |
| 2026-10-27 00:43:15 | A | ws11r | HIGH | oob -> ib | ws12r | ws12r 88.85 y/y | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 | 2026-10-27 00:35:20 | 2026-10-27 00:35:55 |
| 2026-10-27 00:44:00 | A | ws11r | HIGH | ex-fence -> in-fence | ws12r | ws12r 87.63 y/y | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 | 2026-10-27 00:35:20 | 2026-10-27 00:35:55 |
| 2026-10-27 00:44:00 | B | ws11r | HIGH | oob -> ib | ws12r | ws12r 93.91 y/y | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 | 2026-10-27 00:35:20 | 2026-10-27 00:35:55 |
| 2026-10-27 00:45:00 | B | ws9r | HIGH | ex-fence -> in-fence | none | ws10r 81.33 y/n; ws11r 83.45 y/y; ws12r 93.91 y/y | 2026-10-27 00:26:25 | 2026-10-27 00:27:00 | - | - |
| 2026-10-27 00:50:00 | A | ws1r | LOW | oob -> ib | none | ws2r 33.79 n/y; ws3r 5.27 y/y; ws4r 2.59 y/y; ws5r 15.04 y/y; ws6r 24.06 n/y; ws7r 36.60 n/y; ws8r 43.00 n/y; ws9r 54.77 n/y; ws10r 53.04 n/y; ws11r 69.16 n/y; ws12r 72.11 n/y | 2026-10-27 00:40:00 | 2026-10-27 00:40:35 | - | - |
| 2026-10-27 00:50:00 | B | ws10r | HIGH | ex-fence -> in-fence | ws11r | ws11r 83.45 y/y; ws12r 86.39 y/y | 2026-10-27 00:29:15 | 2026-10-27 00:29:50 | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 |
| 2026-10-27 00:51:35 | A | ws1r | LOW | oob -> ib | none | ws2r 32.73 n/y; ws3r 4.71 y/y; ws4r 2.59 y/y; ws5r 14.65 y/y; ws6r 24.06 n/y; ws7r 35.85 n/y; ws8r 43.00 n/y; ws9r 54.77 n/y; ws10r 52.76 n/y; ws11r 69.16 n/y; ws12r 72.11 n/y | 2026-10-27 00:40:00 | 2026-10-27 00:40:35 | - | - |
| 2026-10-27 00:51:50 | A | ws1r | LOW | oob -> ib | none | ws2r 32.73 n/y; ws3r 5.13 y/y; ws4r 2.59 y/y; ws5r 14.65 y/y; ws6r 24.06 n/y; ws7r 35.98 n/y; ws8r 43.00 n/y; ws9r 54.77 n/y; ws10r 52.76 n/y; ws11r 69.16 n/y; ws12r 72.11 n/y | 2026-10-27 00:51:05 | 2026-10-27 00:51:40 | - | - |
| 2026-10-27 00:52:00 | B | ws1r | LOW | oob -> ib | none | ws2r 32.73 n/y; ws3r 5.27 y/y; ws4r 2.59 y/y; ws5r 28.94 n/y; ws6r 38.34 n/y; ws7r 48.42 n/y; ws8r 57.28 n/y; ws9r 69.05 n/y; ws10r 67.04 n/y; ws11r 83.45 n/y; ws12r 86.39 n/y | 2026-10-27 00:51:05 | 2026-10-27 00:51:40 | - | - |
| 2026-10-27 00:52:05 | A | ws1r | LOW | ex-fence -> in-fence | none | ws2r 33.55 n/y; ws3r 6.31 y/y; ws4r 3.73 y/y; ws5r 14.65 y/y; ws6r 24.06 n/y; ws7r 36.36 n/y; ws8r 43.00 n/y; ws9r 54.77 n/y; ws10r 52.76 n/y; ws11r 69.16 n/y; ws12r 72.11 n/y | 2026-10-27 00:51:05 | 2026-10-27 00:51:40 | - | - |
| 2026-10-27 00:52:20 | A | ws5r | LOW | oob -> ib | none | ws6r 24.06 n/y; ws7r 36.60 n/y; ws8r 43.00 n/y; ws9r 54.77 n/y; ws10r 53.04 n/y; ws11r 69.16 n/y; ws12r 72.11 n/y | 2026-10-27 00:41:30 | 2026-10-27 00:42:05 | - | - |
| 2026-10-27 00:53:00 | B | ws1r | LOW | ex-fence -> in-fence | none | ws2r 32.73 n/y; ws3r 5.27 y/y; ws4r 2.59 y/y; ws5r 28.94 n/y; ws6r 38.34 n/y; ws7r 48.42 n/y; ws8r 57.28 n/y; ws9r 69.05 n/y; ws10r 67.04 n/y; ws11r 83.45 n/y; ws12r 86.39 n/y | 2026-10-27 00:51:05 | 2026-10-27 00:51:40 | - | - |
| 2026-10-27 00:54:10 | A | ws5r | LOW | oob -> ib | ws6r | ws6r 11.26 y/y; ws7r 36.95 n/y; ws8r 43.00 n/y; ws9r 41.70 n/y; ws10r 53.45 n/y; ws11r 69.16 n/y; ws12r 72.11 n/y | 2026-10-27 00:41:30 | 2026-10-27 00:42:05 | 2026-10-27 00:21:00 | 2026-10-27 00:21:35 |
| 2026-10-27 00:55:00 | B | ws11r | HIGH | ex-fence -> in-fence | ws12r | ws12r 86.39 y/y | 2026-10-27 00:26:40 | 2026-10-27 00:27:15 | 2026-10-27 00:35:20 | 2026-10-27 00:35:55 |
| 2026-10-27 00:56:15 | A | ws4r | LOW | oob -> ib | ws5r | ws5r 6.01 y/y; ws6r 12.83 y/y; ws7r 26.55 n/y; ws8r 29.25 n/y; ws9r 43.05 n/y; ws10r 55.00 n/y; ws11r 55.02 n/y; ws12r 72.11 n/y | 2026-10-27 00:54:10 | 2026-10-27 00:54:45 | 2026-10-27 00:41:30 | 2026-10-27 00:42:05 |
| 2026-10-27 00:59:10 | A | ws2r | LOW | ex-fence -> in-fence | ws3r | ws3r 6.05 y/y; ws4r 8.29 y/y; ws5r 3.11 y/y; ws6r 9.77 y/y; ws7r 23.74 n/y; ws8r 28.71 n/y; ws9r 40.48 n/y; ws10r 52.76 n/y; ws11r 54.88 n/y; ws12r 72.11 n/y | 2026-10-27 00:54:45 | 2026-10-27 00:55:20 | 2026-10-27 00:54:00 | 2026-10-27 00:54:35 |
| 2026-10-27 01:02:05 | A | ws1r | LOW | oob -> ib | none | ws2r 20.10 n/y; ws3r 6.38 y/y; ws4r 9.56 y/y; ws5r 4.26 y/y; ws6r 2.00 y/y; ws7r 23.74 n/y; ws8r 28.71 n/y; ws9r 40.48 n/y; ws10r 39.01 n/y; ws11r 54.88 n/y; ws12r 58.25 n/y | 2026-10-27 00:51:05 | 2026-10-27 00:51:40 | - | - |
| 2026-10-27 01:02:05 | A | ws2r | LOW | ex-fence -> in-fence | ws3r | ws3r 6.38 y/y; ws4r 9.56 y/y; ws5r 4.26 y/y; ws6r 2.00 y/y; ws7r 23.74 n/y; ws8r 28.71 n/y; ws9r 40.48 n/y; ws10r 39.01 n/y; ws11r 54.88 n/y; ws12r 58.25 n/y | 2026-10-27 00:54:45 | 2026-10-27 00:55:20 | 2026-10-27 00:54:00 | 2026-10-27 00:54:35 |
| 2026-10-27 01:02:10 | A | ws1r | LOW | ex-fence -> in-fence | none | ws2r 22.73 n/y; ws3r 7.99 y/y; ws4r 10.73 y/y; ws5r 5.32 y/y; ws6r 2.64 y/y; ws7r 23.74 n/y; ws8r 28.71 n/y; ws9r 40.48 n/y; ws10r 39.51 n/y; ws11r 54.88 n/y; ws12r 58.66 n/y | 2026-10-27 00:51:05 | 2026-10-27 00:51:40 | - | - |
| 2026-10-27 01:02:40 | A | ws4r | LOW | oob -> ib | ws5r | ws5r 9.63 y/y; ws6r 5.20 y/y; ws7r 24.13 n/y; ws8r 28.71 n/y; ws9r 40.87 n/y; ws10r 41.61 n/y; ws11r 54.88 n/y; ws12r 60.45 n/y | 2026-10-27 00:54:10 | 2026-10-27 00:54:45 | 2026-10-27 00:41:30 | 2026-10-27 00:42:05 |
| 2026-10-27 01:02:45 | A | ws3r | LOW | oob -> ib | none | ws4r 17.18 y/n; ws5r 11.31 y/y; ws6r 6.20 y/y; ws7r 25.27 n/y; ws8r 28.71 n/y; ws9r 42.03 n/y; ws10r 42.46 n/y; ws11r 54.88 n/y; ws12r 61.22 n/y | 2026-10-27 01:02:10 | 2026-10-27 01:02:45 | - | - |
| 2026-10-27 01:03:00 | A | ws3r | LOW | ex-fence -> in-fence | none | ws4r 17.51 y/n; ws5r 11.62 y/y; ws6r 6.38 y/y; ws7r 12.36 y/y; ws8r 28.71 n/y; ws9r 29.14 n/y; ws10r 42.62 n/y; ws11r 54.88 n/y; ws12r 61.36 n/y | 2026-10-27 01:02:10 | 2026-10-27 01:02:45 | - | - |
| 2026-10-27 01:03:00 | B | ws3r | LOW | oob -> ib | ws4r | ws4r 8.29 y/y; ws5r 3.11 y/y; ws6r 9.77 y/y; ws7r 24.68 n/y; ws8r 43.00 n/y; ws9r 41.47 n/y; ws10r 52.76 n/y; ws11r 69.16 n/y; ws12r 72.11 n/y | 2026-10-27 01:02:10 | 2026-10-27 01:02:45 | 2026-10-27 01:02:10 | 2026-10-27 01:02:45 |
| 2026-10-27 01:04:00 | B | ws2r | LOW | ex-fence -> in-fence | none | ws3r 15.14 y/n; ws4r 15.96 y/y; ws5r 3.11 y/y; ws6r 9.77 y/y; ws7r 24.68 n/y; ws8r 28.71 n/y; ws9r 41.47 n/y; ws10r 52.76 n/y; ws11r 69.16 n/y; ws12r 72.11 n/y | 2026-10-27 01:02:05 | 2026-10-27 01:02:40 | - | - |
| 2026-10-27 01:04:00 | B | ws4r | LOW | oob -> ib | ws5r | ws5r 3.11 y/y; ws6r 9.77 y/y; ws7r 24.68 n/y; ws8r 28.71 n/y; ws9r 41.47 n/y; ws10r 52.76 n/y; ws11r 69.16 n/y; ws12r 72.11 n/y | 2026-10-27 01:02:10 | 2026-10-27 01:02:45 | 2026-10-27 01:02:10 | 2026-10-27 01:02:45 |
| 2026-10-27 01:04:05 | A | ws4r | LOW | ex-fence -> in-fence | ws5r | ws5r 9.07 y/y; ws6r 4.87 y/y; ws7r 10.39 y/y; ws8r 14.42 y/y; ws9r 27.18 n/y; ws10r 41.33 n/y; ws11r 54.88 n/y; ws12r 60.21 n/y | 2026-10-27 01:02:10 | 2026-10-27 01:02:45 | 2026-10-27 01:02:10 | 2026-10-27 01:02:45 |
| 2026-10-27 01:06:00 | B | ws3r | LOW | ex-fence -> in-fence | none | ws4r 15.96 y/n; ws5r 6.31 y/y; ws6r 4.87 y/y; ws7r 24.68 n/y; ws8r 28.71 n/y; ws9r 41.47 n/y; ws10r 52.76 n/y; ws11r 54.88 n/y; ws12r 72.11 n/y | 2026-10-27 01:02:10 | 2026-10-27 01:02:45 | - | - |
| 2026-10-27 01:06:10 | A | ws5r | LOW | oob -> ib | ws6r | ws6r 11.07 y/y; ws7r 10.78 y/y; ws8r 14.42 y/y; ws9r 27.56 n/y; ws10r 41.70 n/y; ws11r 41.15 n/y; ws12r 60.53 n/y | 2026-10-27 01:02:10 | 2026-10-27 01:02:45 | 2026-10-27 01:05:35 | 2026-10-27 01:06:10 |
| 2026-10-27 01:06:15 | A | ws8r | LOW | oob -> ib | none | ws9r 29.14 n/y; ws10r 42.62 n/y; ws11r 42.51 n/y; ws12r 61.36 n/y | 2026-10-27 00:41:50 | 2026-10-27 00:42:25 | - | - |
| 2026-10-27 01:06:20 | A | ws5r | LOW | ex-fence -> in-fence | ws6r | ws6r 14.78 y/y; ws7r 13.86 y/y; ws8r 17.72 y/y; ws9r 30.54 n/y; ws10r 43.50 n/y; ws11r 43.78 n/y; ws12r 62.17 n/y | 2026-10-27 01:02:10 | 2026-10-27 01:02:45 | 2026-10-27 01:05:35 | 2026-10-27 01:06:10 |
| 2026-10-27 01:06:25 | A | ws6r | LOW | oob -> ib | ws7r | ws7r 14.30 y/y; ws8r 18.21 y/y; ws9r 30.95 n/y; ws10r 43.76 n/y; ws11r 44.17 n/y; ws12r 62.42 n/y | 2026-10-27 01:05:35 | 2026-10-27 01:06:10 | 2026-10-27 00:54:45 | 2026-10-27 00:55:20 |
| 2026-10-27 01:06:50 | A | ws5r | LOW | ex-fence -> in-fence | ws6r | ws6r 14.24 y/y; ws7r 13.39 y/y; ws8r 17.20 y/y; ws9r 30.10 n/y; ws10r 43.22 n/y; ws11r 43.38 n/y; ws12r 61.91 n/y | 2026-10-27 01:02:10 | 2026-10-27 01:02:45 | 2026-10-27 01:05:35 | 2026-10-27 01:06:10 |
| 2026-10-27 01:07:35 | A | ws5r | LOW | oob -> ib | ws6r | ws6r 11.07 y/y; ws7r 10.78 y/y; ws8r 14.42 y/y; ws9r 27.56 n/y; ws10r 41.70 n/y; ws11r 41.15 n/y; ws12r 60.53 n/y | 2026-10-27 01:02:10 | 2026-10-27 01:02:45 | 2026-10-27 01:05:35 | 2026-10-27 01:06:10 |
| 2026-10-27 01:07:50 | A | ws8r | LOW | oob -> ib | none | ws9r 28.60 n/y; ws10r 42.30 n/y; ws11r 42.04 n/y; ws12r 61.07 n/y | 2026-10-27 01:06:20 | 2026-10-27 01:06:55 | - | - |
| 2026-10-27 01:08:00 | B | ws4r | LOW | ex-fence -> in-fence | ws5r | ws5r 6.31 y/y; ws6r 4.87 y/y; ws7r 24.68 n/y; ws8r 28.71 n/y; ws9r 41.47 n/y; ws10r 52.76 n/y; ws11r 54.88 n/y; ws12r 72.11 n/y | 2026-10-27 01:02:10 | 2026-10-27 01:02:45 | 2026-10-27 01:02:10 | 2026-10-27 01:02:45 |
| 2026-10-27 01:09:10 | A | ws5r | LOW | oob -> ib | ws6r | ws6r 11.27 y/y; ws7r 10.91 y/y; ws8r 14.42 y/y; ws9r 27.71 n/y; ws10r 41.79 n/y; ws11r 41.28 n/y; ws12r 60.61 n/y | 2026-10-27 01:08:35 | 2026-10-27 01:09:10 | 2026-10-27 01:05:35 | 2026-10-27 01:06:10 |
| 2026-10-27 01:09:15 | A | ws8r | LOW | oob -> ib | none | ws9r 28.60 n/y; ws10r 42.30 n/y; ws11r 42.04 n/y; ws12r 61.07 n/y | 2026-10-27 01:06:20 | 2026-10-27 01:06:55 | - | - |
| 2026-10-27 01:09:35 | A | ws5r | LOW | oob -> ib | ws6r | ws6r 11.27 y/y; ws7r 10.91 y/y; ws8r 14.42 y/y; ws9r 27.71 n/y; ws10r 41.79 n/y; ws11r 41.28 n/y; ws12r 60.61 n/y | 2026-10-27 01:08:35 | 2026-10-27 01:09:10 | 2026-10-27 01:05:35 | 2026-10-27 01:06:10 |
| 2026-10-27 01:10:00 | A | ws5r | LOW | ex-fence -> in-fence | ws6r | ws6r 10.67 y/y; ws7r 7.37 y/y; ws8r 14.42 y/y; ws9r 27.27 n/y; ws10r 30.42 n/y; ws11r 40.87 n/y; ws12r 60.37 n/y | 2026-10-27 01:08:35 | 2026-10-27 01:09:10 | 2026-10-27 01:05:35 | 2026-10-27 01:06:10 |
| 2026-10-27 01:10:00 | B | ws5r | LOW | oob -> ib | ws6r | ws6r 4.87 y/y; ws7r 10.91 y/y; ws8r 28.71 n/y; ws9r 41.47 n/y; ws10r 41.79 n/y; ws11r 54.88 n/y; ws12r 72.11 n/y | 2026-10-27 01:08:35 | 2026-10-27 01:09:10 | 2026-10-27 01:05:35 | 2026-10-27 01:06:10 |
| 2026-10-27 01:12:00 | A | ws6r | LOW | oob -> ib | ws7r | ws7r 8.80 y/y; ws8r 1.42 y/y; ws9r 14.10 y/y; ws10r 31.14 n/y; ws11r 41.67 n/y; ws12r 49.23 n/y | 2026-10-27 01:05:35 | 2026-10-27 01:06:10 | 2026-10-27 01:06:20 | 2026-10-27 01:06:55 |
| 2026-10-27 01:12:20 | A | ws9r | LOW | oob -> ib | none | ws10r 31.75 n/y; ws11r 42.40 n/y; ws12r 49.77 n/y | 2026-10-27 01:06:20 | 2026-10-27 01:06:55 | - | - |
| 2026-10-27 01:15:00 | B | ws5r | LOW | ex-fence -> in-fence | ws6r | ws6r 10.67 y/y; ws7r 10.91 y/y; ws8r 14.42 y/y; ws9r 27.27 n/y; ws10r 41.79 n/y; ws11r 54.88 n/y; ws12r 60.37 n/y | 2026-10-27 01:08:35 | 2026-10-27 01:09:10 | 2026-10-27 01:05:35 | 2026-10-27 01:06:10 |
| 2026-10-27 01:15:05 | A | ws6r | LOW | ex-fence -> in-fence | ws7r | ws7r 11.63 y/y; ws8r 3.62 y/y; ws9r 15.95 y/y; ws10r 32.39 n/y; ws11r 43.17 n/y; ws12r 50.35 n/y | 2026-10-27 01:05:35 | 2026-10-27 01:06:10 | 2026-10-27 01:06:20 | 2026-10-27 01:06:55 |
| 2026-10-27 01:15:05 | A | ws9r | LOW | oob -> ib | none | ws10r 32.39 n/y; ws11r 43.17 n/y; ws12r 50.35 n/y | 2026-10-27 01:06:20 | 2026-10-27 01:06:55 | - | - |
| 2026-10-27 01:16:15 | A | ws2r | HIGH | oob -> ib + ex-fence -> in-fence | none | ws3r 74.99 n/y; ws4r 60.36 n/y; ws5r 38.69 n/y; ws6r 17.07 n/y; ws7r 8.03 n/y; ws8r 0.81 n/n; ws9r 13.60 n/n; ws10r 30.82 n/n; ws11r 41.28 n/y; ws12r 48.94 n/n | 2026-10-27 01:12:50 | 2026-10-27 01:13:25 | - | - |
| 2026-10-27 01:18:00 | B | ws2r | HIGH | oob -> ib + ex-fence -> in-fence | none | ws3r 66.37 n/y; ws4r 47.72 n/y; ws5r 28.01 n/y; ws6r 12.36 n/y; ws7r 7.32 n/n; ws8r 14.42 n/n; ws9r 27.27 n/n; ws10r 41.79 n/n; ws11r 40.59 n/n; ws12r 60.37 n/n | 2026-10-27 01:16:15 | 2026-10-27 01:16:50 | - | - |
| 2026-10-27 01:18:15 | A | ws6r | LOW | oob -> ib | ws7r | ws7r 7.32 y/y; ws8r 0.14 y/y; ws9r 12.98 y/y; ws10r 29.23 n/y; ws11r 26.31 n/y; ws12r 47.55 n/y | 2026-10-27 01:05:35 | 2026-10-27 01:06:10 | 2026-10-27 01:06:20 | 2026-10-27 01:06:55 |
| 2026-10-27 01:24:10 | A | ws6r | LOW | oob -> ib | ws7r | ws7r 6.22 y/y; ws8r 0.14 y/y; ws9r 5.28 y/y; ws10r 14.41 y/y; ws11r 26.31 n/y; ws12r 33.01 n/y | 2026-10-27 01:18:05 | 2026-10-27 01:18:40 | 2026-10-27 01:06:20 | 2026-10-27 01:06:55 |
| 2026-10-27 01:26:20 | A | ws6r | LOW | ex-fence -> in-fence | ws7r | ws7r 9.35 y/y; ws8r 0.14 y/y; ws9r 5.28 y/y; ws10r 14.41 y/y; ws11r 26.31 n/y; ws12r 34.79 n/y | 2026-10-27 01:24:10 | 2026-10-27 01:24:45 | 2026-10-27 01:06:20 | 2026-10-27 01:06:55 |
| 2026-10-27 01:27:10 | A | ws6r | LOW | ex-fence -> in-fence | ws7r | ws7r 8.80 y/y; ws8r 0.14 y/y; ws9r 5.28 y/y; ws10r 14.41 y/y; ws11r 26.31 n/y; ws12r 34.46 n/y | 2026-10-27 01:24:10 | 2026-10-27 01:24:45 | 2026-10-27 01:06:20 | 2026-10-27 01:06:55 |

