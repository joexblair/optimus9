# strat-3-r-oob — what was measured

Window **09-01 00:00:00 → 09-06 00:00:00**. Produced by `scan.py`, output in `scan_20260925.txt`.
All knobs at the values in `spec.md`. **No knob has been tuned and no target was chased.**

## 1. The 28 episodes

`RETURN` is the position return at the earliest mage-rev **+ 33 minutes**, with
dr +1 = SHORT and dr −1 = LONG, so return = −(px move) × dr.

`xlsx row`, `gap m` and `tag C` come from `transfer/260924_strat_wsf_leash.xlsx`, matched to the
**nearest** `wsl_sig_utc`. **That mapping is mine** — only 1 of the 28 is an exact match.

| # | event bar | dr | position | ws1mage-rev | ws2mage-rev | ws3mage-rev | earliest | px move | RETURN | xlsx row | gap m | tag C |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 09-01 05:42:00 | +1 | SHORT | 05:43:20 | 05:43:20 | 05:43:20 | 05:43:20 | -0.764 | **+0.764** | 10 | +1.1 | t |
| 2 | 09-01 07:00:00 | -1 | LONG | 07:00:40 | 07:00:40 | 07:00:40 | 07:00:40 | +0.918 | **+0.918** | 11 | +14.8 | x |
| 3 | 09-01 07:24:00 | +1 | SHORT | 07:27:15 | 10:16:40 | 10:25:40 | 07:27:15 | -0.629 | **+0.629** | 13 | +3.0 | t |
| 4 | 09-01 15:10:10 | -1 | LONG | 15:11:15 | 15:11:15 | 15:11:15 | 15:11:15 | +0.855 | **+0.855** | 22 | -2.2 | t |
| 5 | 09-01 17:57:10 | -1 | LONG | 18:00:10 | 18:00:10 | 18:11:35 | 18:00:10 | -2.053 | **-2.053** | 27 | +2.8 | s |
| 6 | 09-01 20:03:00 | -1 | LONG | 20:05:05 | 20:29:00 | 20:49:10 | 20:05:05 | -0.195 | **-0.195** | 31 | -31.0 | t |
| 7 | 09-02 03:28:10 | +1 | SHORT | 03:29:20 | 03:29:20 | 03:29:20 | 03:29:20 | -0.571 | **+0.571** | 46 | +0.8 | t |
| 8 | 09-02 05:03:00 | -1 | LONG | 05:04:15 | 05:04:15 | 05:04:15 | 05:04:15 | +0.504 | **+0.504** | 49 | +3.2 | t |
| 9 | 09-02 05:06:00 | -1 | LONG | 05:06:30 | 05:06:30 | 05:06:30 | 05:06:30 | +0.571 | **+0.571** | 49 | +0.2 | t |
| 10 | 09-02 12:58:00 | -1 | LONG | 13:00:25 | 13:00:25 | 13:00:25 | 13:00:25 | +0.130 | **+0.130** | 61 | +2.2 | t |
| 11 | 09-02 16:21:00 | +1 | SHORT | 16:24:00 | 16:24:00 | 16:24:00 | 16:24:00 | -1.005 | **+1.005** | 66 | +2.8 | t |
| 12 | 09-02 17:09:00 | -1 | LONG | 17:10:35 | 17:10:35 | 17:10:35 | 17:10:35 | -1.256 | **-1.256** | 67 | +1.3 | s |
| 13 | 09-02 17:51:25 | +1 | SHORT | 17:53:45 | 20:26:30 | 20:26:30 | 17:53:45 | -2.100 | **+2.100** | 68 | +20.1 | t |
| 14 | 09-02 18:15:00 | -1 | LONG | 18:37:45 | 18:37:45 | 18:37:45 | 18:37:45 | +0.808 | **+0.808** | 69 | +0.0 | t |
| 15 | 09-02 19:30:00 | -1 | LONG | 19:31:35 | 19:31:35 | 19:31:35 | 19:31:35 | +0.787 | **+0.787** | 72 | -9.4 | t |
| 16 | 09-03 05:22:00 | -1 | LONG | 05:24:40 | 07:50:45 | 05:28:45 | 05:24:40 | +1.470 | **+1.470** | 78 | -32.6 | t |
| 17 | 09-03 06:39:00 | +1 | SHORT | 06:39:35 | 06:39:35 | 06:39:35 | 06:39:35 | +0.172 | **-0.172** | 79 | -12.1 | t |
| 18 | 09-03 14:03:00 | -1 | LONG | 14:04:45 | 14:04:45 | 20:03:25 | 14:04:45 | +1.297 | **+1.297** | 87 | +1.0 | t |
| 19 | 09-03 16:52:00 | +1 | SHORT | 16:53:40 | 17:18:05 | 17:49:40 | 16:53:40 | +0.351 | **-0.351** | 94 | -0.6 | t |
| 20 | 09-03 19:52:00 | -1 | LONG | 19:55:30 | 20:03:25 | 20:03:25 | 19:55:30 | -0.662 | **-0.662** | 99 | -24.8 | x |
| 21 | 09-03 22:13:00 | -1 | LONG | 22:14:15 | 22:14:15 | 22:14:15 | 22:14:15 | -1.114 | **-1.114** | none | -96.0 | — |
| 22 | 09-03 23:38:00 | +1 | SHORT | 23:40:50 | 23:41:55 | 00:42:15 | 23:40:50 | -0.171 | **+0.171** | none | +117.8 | — |
| 23 | 09-04 01:03:25 | -1 | LONG | 01:05:45 | 01:05:45 | 01:05:45 | 01:05:45 | -0.187 | **-0.187** | 101 | +32.3 | t |
| 24 | 09-04 10:11:00 | -1 | LONG | 10:11:45 | 10:11:45 | 10:11:45 | 10:11:45 | -0.300 | **-0.300** | 111 | +9.0 | t |
| 25 | 09-04 17:54:05 | -1 | LONG | 18:37:15 | 18:31:05 | 19:12:15 | 18:31:05 | +0.326 | **+0.326** | 120 | -1.1 | s |
| 26 | 09-05 02:06:00 | -1 | LONG | 02:08:55 | 02:08:55 | 02:08:55 | 02:08:55 | +0.422 | **+0.422** | 129 | +2.7 | t |
| 27 | 09-05 06:35:00 | +1 | SHORT | 06:36:55 | 06:36:55 | 06:36:55 | 06:36:55 | +1.090 | **-1.090** | 136 | -5.6 | s |
| 28 | 09-05 21:25:35 | +1 | SHORT | 21:28:20 | 00:23:25 | 00:23:25 | 21:28:20 | -0.029 | **+0.029** | 156 | +2.5 | t |

## 2. The outcome

| group | n | in profit | mean | median | min | max |
|---|---|---|---|---|---|---|
| all | **28** | **18** | +0.213% | +0.374% | −2.053 | +2.100 |
| dr −1, LONG | 18 | 11 | +0.129% | +0.374% | | |
| dr +1, SHORT | 10 | 7 | +0.366% | +0.371% | | |

## 3. Split by Joe's column C tag

| tag | n | in profit | mean | median | min | max |
|---|---|---|---|---|---|---|
| **t** | **20** | **15** | **+0.537%** | +0.571% | −0.351 | +2.100 |
| **s** | 4 | 1 | −1.018% | −1.173% | −2.053 | +0.326 |
| **x** | 2 | 1 | +0.128% | +0.128% | −0.662 | +0.918 |
| no row within 60 min | 2 | — | — | — | −1.114 | +0.171 |

Joe 0925: *"I can improve that stat: keep only my tag C `t` rows"*.

## 4. The cost check — tag `t` only, n = 20

| | clears | mean | median | sum | min | max |
|---|---|---|---|---|---|---|
| **GROSS** | 15 of 20 | +0.537% | +0.571% | +10.737% | −0.351 | +2.100 |
| **NET of 0.1975%** — the 22,000-coin measurement | **13 of 20** | **+0.339%** | +0.373% | **+6.787%** | −0.548 | +1.903 |
| **NET of 0.550%** — the 88,000-coin figure | 11 of 20 | **−0.013%** | +0.021% | −0.263% | −0.901 | +1.550 |

| | at 22,000 coins, px ≈ 0.17 |
|---|---|
| 0.1975% | 7.39 USDT per trade |
| 0.550% | 20.57 USDT per trade |

**At the banked 22,000-coin size it clears. At the 88,000-coin drag it does not.**

The 13 that clear the 22k drag: #1 +0.567, #3 +0.431, #4 +0.657, #7 +0.373, #8 +0.306,
#9 +0.373, #11 +0.807, #13 +1.903, #14 +0.611, #15 +0.590, #16 +1.272, #18 +1.099, #26 +0.224.

## 5. The swing_detect(2) confirmation — it does not work at this horizon

| | |
|---|---|
| minutes from the mage-rev to the next 2% pivot | min 1.5, **median 90.0**, mean 136.6, max 582.8 |
| pivots inside 33 min | **5 of 28** |
| pivot kind at dr −1 | L on 16 of 18 |
| pivot kind at dr +1 | 5 H / 5 L |

## 6. How rarely the state occurs

| | |
|---|---|
| bars scanned, 09-01 → 09-06 | 86,531 |
| bars with all three oob **simultaneously** | 463, in 46 runs |
| single-bar runs among those 46 | 12 |
| longest simultaneous run | 80 bars = 400 s, 09-02 17:52:20 → 17:58:55, dr +1 |
| **episodes under the 60 s tolerance** | **28** |
| of those, all three on the **same** bar | 24 of 28 — the tolerance only adds 4 |

## 7. Alignment with wsf_leash — the reason it was separated

| | |
|---|---|
| exact `wsl_sig_utc` matches | **1 of 28** — episode 14, 09-02 18:15:00 → xlsx row 69 |
| within 2 min | 8 of 28 |
| gap range | −96.0 to +117.8 min |
| mapped to a row with the **opposite** dr | 3 — episodes 6, 13, 20 |
| two episodes sharing one xlsx row | 8 and 9, both row 49 |

## 8. Every caveat, in one place

- **n = 20** on the headline. That is not a sample size for a per-trade mean.
- The `t` tag reached 20 of the 28 rows **across a gap I chose**; only 6 of those 20 are within
  2 min of a `wsl_sig_utc`.
- **+33 minutes is a fixed offset, not an exit.** No mechanic closes these positions.
- The window is **5 days, in-sample**. There is no OOS test.
- `min_travel` on the reversal producers is **0.0** everywhere. Joe 0925: *"the true threshold is
  in the OOS data"*.
- Three knobs in `spec.md` are **MINE and unruled**: the event bar, the mage-rev walk start, and
  taking the earliest of the three tfs.
