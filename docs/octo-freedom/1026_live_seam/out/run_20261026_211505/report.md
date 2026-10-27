# live_seam - read A against read B on the live tape, 2026-10-26 21:15:10 to 2026-10-26 21:24:55

## The run

| item | value |
|---|---|
| live bars | 118 |
| first live bar | 2026-10-26 21:15:10 |
| last live bar | 2026-10-26 21:24:55 |
| seeded bars before it | 74880, 2026-10-22 13:15:10 to 2026-10-26 21:15:05 |
| window | lookback 24 h + warmup 80 h, o9-live's |
| filler_invisible | True |
| bars read after close, ms: min / median / max | 5301 / 5302 / 5303 |
| compute per bar, ms: min / median / max | 359 / 497 / 1432 |
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

The replay is one window ending 2026-10-26 21:24:55, emerging lines, `v4_closed_prev.series`. Tolerance 2.0e-07 is ac06c2's (#6). The max |diff| is reported pass or fail.

| line | bars compared | exactly equal | max abs diff | above 2.0e-07 | NaN mismatch | verdict |
|---|---|---|---|---|---|---|
| ws1b | 118 | 84 | 1.1e-09 | 0 | 0 | PASS |
| ws1r | 118 | 46 | 1.4e-14 | 0 | 0 | PASS |
| ws2r | 118 | 46 | 7.1e-15 | 0 | 0 | PASS |
| ws3r | 118 | 118 | 0.0e+00 | 0 | 0 | PASS |
| ws4r | 118 | 118 | 0.0e+00 | 0 | 0 | PASS |
| ws5r | 118 | 0 | 7.1e-15 | 0 | 0 | PASS |
| ws6r | 118 | 46 | 3.6e-15 | 0 | 0 | PASS |
| ws7r | 118 | 118 | 0.0e+00 | 0 | 0 | PASS |
| ws8r | 118 | 118 | 0.0e+00 | 0 | 0 | PASS |
| ws9r | 118 | 118 | 0.0e+00 | 0 | 0 | PASS |
| ws10r | 118 | 118 | 0.0e+00 | 0 | 0 | PASS |
| ws11r | 118 | 0 | 7.1e-15 | 0 | 0 | PASS |
| ws12r | 118 | 118 | 0.0e+00 | 0 | 0 | PASS |
| ws5Mage | 118 | 0 | 6.1e-10 | 0 | 0 | PASS |
| ws6Mage | 118 | 118 | 0.0e+00 | 0 | 0 | PASS |
| ws7Mage | 118 | 70 | 6.8e-11 | 0 | 0 | PASS |
| ws8Mage | 118 | 118 | 0.0e+00 | 0 | 0 | PASS |
| ws9Mage | 118 | 84 | 1.4e-10 | 0 | 0 | PASS |
| ws10Mage | 118 | 60 | 1.4e-10 | 0 | 0 | PASS |
| ws11Mage | 118 | 0 | 1.4e-10 | 0 | 0 | PASS |
| ws12Mage | 118 | 118 | 0.0e+00 | 0 | 0 | PASS |

### bars whose OHLCV changed on the tape after the live read: 0

## The firings, one row per pair, chronological

| event | pairs | both | A only | B only |
|---|---|---|---|---|
| #1 ws1b oob -> ib | 2 | 1 | 1 | 0 |
| #2 baton pass | 0 | 0 | 0 | 0 |
| #3 Mage into oob | 7 | 0 | 5 | 2 |
| #4 r into oob | 8 | 1 | 6 | 1 |

| event | lines | side | fired under | A bar | B bar | gap s | read A at A bar | read B at A bar | A dwell s | A survives close | A wob 12 | B dwell s | B survives close | B wob 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| #4 r into oob | ws6r | LOW | A only | 2026-10-26 21:15:30 | - | - | ws6r 14.91 | ws6r 18.75 | 5 | yes | no | - | - | - |
| #4 r into oob | ws6r | LOW | both | 2026-10-26 21:15:40 | 2026-10-26 21:18:00 | 140 | ws6r 14.91 | ws6r 18.75 | 140 | yes | yes | 360 | yes | yes |
| #3 Mage into oob | ws7Mage | LOW | A only | 2026-10-26 21:15:45 | - | - | ws7Mage 13.68 | ws7Mage 12.58 | 160 | no | yes | - | - | - |
| #3 Mage into oob | ws11Mage | LOW | A only | 2026-10-26 21:16:35 | - | - | ws11Mage 13.83 | ws11Mage 16.37 | 85 | run ended | yes | - | - | - |
| #4 r into oob | ws9r | LOW | A only | 2026-10-26 21:18:00 | - | - | ws9r 13.26 | ws9r 15.25 | 25 | run ended | no | - | - | - |
| #3 Mage into oob | ws6Mage | LOW | B only | - | 2026-10-26 21:18:00 | - | - | - | - | - | - | 360 | yes | yes |
| #3 Mage into oob | ws9Mage | LOW | B only | - | 2026-10-26 21:18:00 | - | - | - | - | - | - | >= 420 (run ended) | run ended | yes |
| #1 ws1b oob -> ib | ws1b | LOW | A only | 2026-10-26 21:18:25 | - | - | ws1b 16.23 | ws1b 0.77 | 5 | yes | no | - | - | - |
| #3 Mage into oob | ws7Mage | LOW | A only | 2026-10-26 21:18:30 | - | - | ws7Mage 14.86 | ws7Mage 12.58 | 5 | no | no | - | - | - |
| #3 Mage into oob | ws10Mage | LOW | A only | 2026-10-26 21:18:30 | - | - | ws10Mage 14.38 | ws10Mage 18.64 | 10 | no | no | - | - | - |
| #4 r into oob | ws5r | LOW | A only | 2026-10-26 21:18:30 | - | - | ws5r 15.00 | ws5r 15.00 | 10 | no | no | - | - | - |
| #4 r into oob | ws7r | LOW | A only | 2026-10-26 21:18:30 | - | - | ws7r 13.80 | ws7r 13.73 | 10 | no | no | - | - | - |
| #1 ws1b oob -> ib | ws1b | LOW | both | 2026-10-26 21:18:35 | 2026-10-26 21:19:00 | 25 | ws1b 15.64 | ws1b 0.77 | >= 385 (run ended) | yes | yes | >= 360 (run ended) | yes | yes |
| #4 r into oob | ws8r | LOW | B only | - | 2026-10-26 21:20:00 | - | - | - | - | - | - | >= 300 (run ended) | run ended | yes |
| #4 r into oob | ws8r | LOW | A only | 2026-10-26 21:20:05 | - | - | ws8r 12.19 | ws8r 11.39 | 40 | run ended | no | - | - | - |
| #4 r into oob | ws8r | LOW | A only | 2026-10-26 21:21:00 | - | - | ws8r 11.31 | ws8r 11.39 | >= 240 (run ended) | run ended | yes | - | - | - |
| #3 Mage into oob | ws5Mage | LOW | A only | 2026-10-26 21:23:00 | - | - | ws5Mage 14.90 | ws5Mage 19.54 | >= 120 (run ended) | yes | yes | - | - | - |

## Every #1 firing with the r ladder, chronological

ws1r..ws12r at the firing bar, on the read that fired. H = at or above the high fence (80), L = at or below the low fence (20), - = neither. Both sides are shown: this harness has no trade side.

| bar | read | side left | ws1r | ws2r | ws3r | ws4r | ws5r | ws6r | ws7r | ws8r | ws9r | ws10r | ws11r | ws12r |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-26 21:18:25 | A | LOW | 28.92 - | 27.34 - | 41.93 - | 30.65 - | 15.54 L | 24.41 - | 15.50 L | 11.39 L | 15.75 L | 16.26 L | 20.17 - | 31.17 - |
| 2026-10-26 21:18:35 | A | LOW | 28.92 - | 26.83 - | 41.66 - | 30.25 - | 15.00 L | 24.06 - | 14.95 L | 11.39 L | 15.52 L | 16.26 L | 19.79 L | 31.17 - |
| 2026-10-26 21:19:00 | B | LOW | 28.92 - | 13.30 L | 40.89 - | 36.07 - | 15.00 L | 13.31 L | 13.73 L | 15.08 L | 15.25 L | 26.05 - | 26.29 - | 39.59 - |

## Every pass bar of ws1r..ws4r, both reads, chronological

Rung scan: every rung above the handing line, as `line value ex-fence/towards` (y/n). The full scan is in out/events.jsonl. Reversals are on the EMERGING series in both reads, raw bar and stamp kept apart.

| bar | read | handing line | side | why | receiver | rung scan | handing rev raw | handing rev stamp | receiver rev raw | receiver rev stamp |
|---|---|---|---|---|---|---|---|---|---|---|

