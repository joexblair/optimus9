# EMERGING against CLOSED on the banked mechs. the full tape, 1632960 bars = 94 days.
# RULED_OK True. max_pyramid 2. drag 0.1975%. 22000 coins. start USDT 500.00.
# THE EXIT: a stopped trade at -1.100%, a positive at 90% of its MFE, bar-ordered,
#   on CLOSE prices either way - the value_mode is the LINES, not the price series.
# THE SPLIT: sweep 2026-07-02 12:00:00 .. 2026-08-31 23:59:55, hold-out 2026-09-01 00:00:00 .. 2026-10-04 23:59:55.
# the r trips are the legacy tuple slots (rsi, stc, k_len) - NOT (k, rsi, stc).

# THE CONTROL ROW, both modes, both trips. ws5r at 2026-09-03 00:35:00.

| the trip | emerging ws5r | closed ws5r | known-good |
|---|---|---|---|
| the bank (6, 8, 6) | 6.77 | 11.74 | emerging 6.77 |
| the previous bank (5, 8, 7) | 12.48 | 17.12 | emerging 12.48 |

# THE SIGNAL COUNTS. the trade list the lines produce, before any scoring.

| the leg | backstop fires | accepted trades | after max_pyramid 2 |
|---|---|---|---|
| the bank, emerging | 1086 | 598 | 543 |
| the bank, closed | 250 | 214 | 210 |
| the previous bank, emerging | 602 | 367 | 347 |
| the previous bank, closed | 116 | 106 | 106 |

# THE FULL TAPE

| the cell | trades | wins | win rate % | net USDT | net % | worst DD USDT | net / worst DD | profit factor | worst losing run |
|---|---|---|---|---|---|---|---|---|---|
| the bank, emerging | 543 | 366 | 67.4 | +19485.67 | +556.84 | 312.69 | 62.32 | 3.92 | 6, -261.54 |
| the bank, closed | 210 | 158 | 75.2 | +9945.34 | +285.20 | 118.75 | 83.75 | 5.32 | 2, -118.75 |
| the previous bank, emerging | 347 | 225 | 64.8 | +9581.36 | +285.26 | 292.29 | 32.78 | 2.95 | 5, -250.22 |
| the previous bank, closed | 106 | 81 | 76.4 | +5114.23 | +145.43 | 132.58 | 38.57 | 5.89 | 3, -132.58 |

# THE SWEEP HALF

| the cell | trades | wins | win rate % | net USDT | net % | worst DD USDT | net / worst DD | profit factor | worst losing run |
|---|---|---|---|---|---|---|---|---|---|
| the bank, emerging | 334 | 234 | 70.1 | +12018.62 | +356.58 | 199.49 | 60.25 | 4.28 | 4, -157.41 |
| the bank, closed | 127 | 99 | 78.0 | +5680.09 | +168.81 | 118.75 | 47.83 | 5.78 | 2, -118.75 |
| the previous bank, emerging | 217 | 147 | 67.7 | +6511.39 | +202.12 | 292.29 | 22.28 | 3.51 | 4, -237.11 |
| the previous bank, closed | 67 | 47 | 70.1 | +2395.87 | +71.84 | 132.58 | 18.07 | 3.80 | 3, -132.58 |

# THE HOLD-OUT HALF

| the cell | trades | wins | win rate % | net USDT | net % | worst DD USDT | net / worst DD | profit factor | worst losing run |
|---|---|---|---|---|---|---|---|---|---|
| the bank, emerging | 209 | 132 | 63.2 | +7467.05 | +200.26 | 312.69 | 23.88 | 3.48 | 6, -261.54 |
| the bank, closed | 83 | 59 | 71.1 | +4265.24 | +116.39 | 103.95 | 41.03 | 4.84 | 2, -103.22 |
| the previous bank, emerging | 130 | 78 | 60.0 | +3069.97 | +83.14 | 290.39 | 10.57 | 2.33 | 5, -250.22 |
| the previous bank, closed | 39 | 34 | 87.2 | +2718.36 | +73.59 | 97.52 | 27.88 | 15.44 | 2, -97.52 |

# THE EXPOSURE, full tape, after max_pyramid 2.

| the leg | max concurrent | peak open notional USDT | the bar it peaks on |
|---|---|---|---|
| the bank, emerging | 2 | 9438.00 | 2026-08-27 01:06:00 |
| the bank, closed | 2 | 7837.28 | 2026-09-29 20:14:35 |
| the previous bank, emerging | 2 | 9443.28 | 2026-08-27 00:58:05 |
| the previous bank, closed | 2 | 6534.44 | 2026-07-12 01:51:05 |
# took 30 s
