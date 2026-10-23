# A CAUSALITY AUDIT of v4-ws5rbackstop + v4-lineage + the scoring. banked k5 rsi8 stc7.
# RULED_OK True. the full tape, 1632960 bars = 94 days. 367 trades.
# every number below is MEASURED on those trades.

## 1  the entry against the bar the ws5r reversal becomes knowable

# the backstop stamps its reversal at rev + LIFT_WOB - 1 = rev + 7 bars = 35 s.
# the lineage walk is handed the RAW rev bar, so it may resolve before that stamp.

| test | trades | share % |
|---|---|---|
| entry at or before the reversal stamp | 0 | 0.0 |
| entry at or before the backstop fire bar | 0 | 0.0 |
| entry strictly after the fire bar | 367 | 100.0 |

| statistic | bars | seconds |
|---|---|---|
| entry minus stamp, min | 12 | 60 |
| entry minus stamp, median | 210 | 1050 |
| entry minus fire, min | 1 | 5 |
| entry minus fire, median | 206 | 1030 |

## 2  the ib dwell is proven on future bars

# F.ib_cross returns the CROSS bar k but requires the run to hold int(TF x 2.5) bars,
#   which is only known at k + need - 1. The walk acts on k.

| statistic | bars | seconds |
|---|---|---|
| the final rider dwell, min | 12 | 60 |
| the final rider dwell, median | 15 | 75 |
| the final rider dwell, max | 25 | 125 |
| the unknowable lead, median = dwell - 1 | 14 | 70 |

| the final rider TF | trades |
|---|---|
| ws5 | 117 |
| ws6 | 153 |
| ws7 | 67 |
| ws8 | 24 |
| ws9 | 5 |
| ws10 | 1 |

## 3  concurrent positions, and opposite directions held at once

# rev-trade means a new signal FLIPS the position. The ledger holds each trade to its own
#   pivot instead, so positions overlap.

| test | count |
|---|---|
| overlapping trade pairs | 112 |
| overlapping pairs in OPPOSITE directions | 22 |
| the hold, median bars | 834 |
| the hold, max bars | 13823 |
| the hold, max seconds | 69115 |

## 4  the -1.100% stop is tested on CLOSES, not on the bar lows

# v4_equity.ledger builds its excursion from close only. The klines high and low are read
#   by v4_backstop_trades.prices and are NOT used by the ledger.

| test | trades | share % |
|---|---|---|
| stopped, measured on closes | 109 | 29.7 |
| stopped, measured on the bar lows and highs | 118 | 32.2 |
| trades the intrabar stop would have caught and the close test missed | 9 | 2.5 |

| reading | gross % | drag at 0.1975% | NET % |
|---|---|---|---|
| close only, as reported | +379.96 | 72.48 | +307.47 |
| the bar lows and highs | +352.42 | 72.48 | +279.94 |

| reading | net USDT at 22000 coins |
|---|---|
| close only, as reported | +10261.38 |
| the bar lows and highs | +9276.52 |
| the difference | -984.86 |

## 5  trades whose excursion runs to the end of the tape

| test | count |
|---|---|
| exits booked at the segment end, no 90% level and no stop | 0 |
| the last trade entry | 2026-10-04 16:12:40 |
| the last trade exit | 2026-10-04 21:31:35 |
| the tape end | 2026-10-04 23:59:55 |
