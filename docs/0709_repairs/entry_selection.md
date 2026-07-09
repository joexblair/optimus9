# 0709 repairs — ENTRY SELECTION (open)

**STATUS: OPEN.** A more robust solution is planned. Nothing here is closed; the negative results below bound
the search, they do not end it.

The 42-day causal book (breach arm, `lp_arm_bigleg=0`) loses because it wins **42.1%** against a **50.4%**
breakeven. Half the trades die at the stop; the other half exit on signal at `+0.83%` and 84% win. The deficit
is trade **selection**.

Scripts: `entry_separator.py` · `entry_state_separator.py` · `entry_state_filter_ab.py`.
Window: 42d, `now - 1h` pinned, cost 0.20% round trip, `strand_rescue` excluded.

---

## The population

```
entries 3306   signal-exits 1657   stops 1649   baseline exit-rate 50.1%
mean/trade -0.1740%   win 42.1%   breakeven 50.4%   stop 49.9%
avg winner +1.038%    avg loser -1.055%
```

---

## 1. Line VALUE at the entry bar carries almost nothing

21 lines × 3 forms (side-signed, distance from the middle of the board, raw) = 63 tests. Score = probability a
random signal-exit outranks a random stop. `0.500` is no information.

```
feature              score   1st half  2nd half   same side?
s7M (signed)         0.535     0.542     0.528       yes
s5M (signed)         0.535     0.544     0.526       yes
s4M (signed)         0.533     0.546     0.519       yes
s3M (signed)         0.532     0.547     0.517       yes
s4r |dist 50|        0.470     0.470     0.470       yes
s7r raw              0.528     0.525     0.531       yes
```

- **Noise floor: the best of 63 tests on n=3306 lands near `0.53` by chance.** The best observed is `0.535`.
- The four slow Mage lines cluster and all point the same way (Mage aligned with the trade slightly favours a
  signal exit). They are one piece of information counted four times.
- `s4r` distance-from-middle is the most *stable* (`0.470` in both halves) and is `0.030` from chance.

**[measured] No single line value at the entry bar predicts whether a trade stops out.**

---

## 2. Line STATE does predict the exit — Joe's hypothesis, confirmed

Joe: *"it might be if you let the lines breach, and/or let them breach and reverse."* Four binary states per
line at the entry bar, side-signed to the trade (`LB` = 60 bars, reversal confirmation 2 bars):

| state | meaning |
|---|---|
| `oob_with` | the line is outside the boundary on the trade's own side |
| `oob_against` | outside on the opposite side |
| `swept_with` | travelled directly from the opposite extreme to this one, no retrace (a latch) |
| `breach_rev` | was outside on the trade's side within the lookback AND has since turned back |

```
line   state          n     exit% on  exit% off    1st     2nd    both sides?
s7M    oob_against   228      38.6%      51.0%    43.8%   33.6%      yes
s4r    oob_with      500      44.8%      51.1%    44.2%   45.4%      yes
s7M    oob_with      806      55.2%      48.5%    53.6%   56.9%      yes
s5M    oob_with      654      54.4%      49.1%    52.6%   56.3%      yes
s3M    swept_with   1759      53.6%      46.2%    54.4%   52.6%      yes
s4M    oob_with      903      53.5%      48.9%    54.2%   52.8%      yes
s2m    breach_rev    337      52.5%      49.8%    54.5%   50.3%      yes
```

- **`s7M oob_against` is the strongest.** When the 7-minute Mage sits outside the boundary on the side *opposed*
  to the trade, the trade stops out **61.4%** of the time. Holds in both halves.
- `breach_rev` — the breach-then-reverse state — appears once in the top 14 (`s2m`, `52.5%` vs `49.8%`) and
  drifts toward baseline in the second half. **It carries nothing at any line.**
- 84 states were screened; the split-half columns are the guard.

---

## 3. The state predicts the exit. It does not predict money.

```
                       n     net       mean      win    breakeven  stop    halves (mean)
baseline             3309  -575.86%  -0.1740%   42.1%    50.4%    49.9%   -0.1764 / -0.1717
R1 reject s7M_against 3081  -530.88%  -0.1723%   42.7%    51.1%    49.0%   -0.1724 / -0.1722
R2 reject s4r_with    2809  -452.37%  -0.1610%   43.0%    50.8%    48.9%   -0.1505 / -0.1716
R3 keep only s7M_with  807  -145.69%  -0.1805%   44.4%    54.1%    44.9%   -0.2101 / -0.1507
R1+R2                 2664  -442.12%  -0.1660%   43.4%    51.5%    48.4%   -0.1587 / -0.1732
R1+R2+R3               763  -135.78%  -0.1780%   44.7%    54.3%    44.7%   -0.2166 / -0.1404
```

- **Every rule raises win rate. Every rule raises breakeven by more.**
- `R1+R2+R3`: win `42.1% → 44.7%`, stop `49.9% → 44.7%`, breakeven `50.4% → 54.3%`. Mean per trade unchanged at
  `-0.178%`.
- The kept trades have smaller winners. The two effects cancel.
- **Mean per trade sits at `-0.17%` in every subset**, including the 763-trade slice.

**The loss is uniform.** Cutting the book by any of these states removes trades, not deficit.

---

---

## 4. Stop width — no width saves this book

`stop_sweep_causal.py`. Entries computed once; only the exit varies. `lr.sl = 0.90%` was swept against the
look-ahead book.

**Prediction (before the run):** the stops sit hard against the boundary (MAE p90 `1.015%` vs a `0.90%` stop).
Widening to `1.1-1.3%` should convert stops into signal exits and lift the mean, then degrade once the converted
losers cost more than the recovered winners.

**REFUTED.** No optimum. The mean improves monotonically as the stop widens, and the best row is the stop off.

```
stop%      n       net       mean      win%    be%    stop%   avgW     halves (mean)
0.50    3308   -569.80%  -0.1722%   31.7%   41.3%   65.1%  +1.053%  -0.1796 / -0.1649
0.70    3308   -585.20%  -0.1769%   37.4%   46.5%   57.1%  +1.046%  -0.1767 / -0.1771
0.90    3308   -572.73%  -0.1731%   42.1%   50.4%   49.8%  +1.038%  -0.1761 / -0.1702
1.10    3308   -537.21%  -0.1624%   45.6%   52.9%   43.4%  +1.039%  -0.1808 / -0.1440
1.30    3308   -518.34%  -0.1567%   47.9%   54.8%   37.9%  +1.038%  -0.1917 / -0.1217
1.50    3308   -516.93%  -0.1563%   49.5%   56.1%   33.2%  +1.035%  -0.1970 / -0.1155
2.00    3308   -466.35%  -0.1410%   51.8%   57.6%   23.4%  +1.037%  -0.1949 / -0.0871
3.00    3308   -454.58%  -0.1374%   53.3%   58.8%   12.8%  +1.026%  -0.1911 / -0.0838
off     3308   -423.00%  -0.1279%   53.7%   58.8%    0.0%  +1.031%  -0.1662 / -0.0896   <- ceiling, never a config
```

- `0.90%` is not even a local optimum; `0.70%` is worse than both neighbours. The surface is noisy below 1%.
- **With no stop at all the book still loses `-0.1279%` per trade.**
- Win rate climbs `31.7% -> 53.7%`; breakeven climbs `41.3% -> 58.8%`. The losers absorb whatever the stop
  stops absorbing.
- Second halves improve as the stop widens while first halves worsen. **The book is not stationary across 42d.**

---

## 5. Arm at the 5-minute seam — removes trades, not deficit

`seam_arm_ab.py`. Joe: *measure the s5m breach at the 5-minute emerging bar seam, not the first 5s bar that
breached.* Only the `s5m` arm is re-sampled; the `s5r` divergence arm is untouched. 1-min and 2-min seams added
to test whether any effect scales with the seam or appears only at one width.

**Prediction (before the run):** fewer entries; median adverse excursion falls; average winner stays pinned near
`+1.03%`; mean improves but stays negative.

**Entries fell as predicted. Nothing else moved.**

```
                 n      net       mean      win%   be%   stop%   avgW      avgL      MAE p50
every 5s bar   3309  -573.19%  -0.1732%  42.1%  50.4%  49.8%  +1.038%  -1.055%   0.895%
1-min seam     2981  -547.09%  -0.1835%  41.9%  50.7%  50.1%  +1.027%  -1.058%   0.900%
2-min seam     2791  -503.70%  -0.1805%  42.0%  50.6%  50.1%  +1.033%  -1.056%   0.900%
5-min seam     2601  -451.16%  -0.1735%  42.3%  50.6%  49.8%  +1.032%  -1.056%   0.890%
```

- Entries `3309 -> 2601` (−21%). Mean per trade `-0.1732% -> -0.1735%`. The 1-min and 2-min seams are **worse**
  than both ends — no monotone trend, so no mechanism.
- **Median adverse excursion unchanged** (`0.895% -> 0.890%`). Entry quality did not lift.
- The 708 entries the seam removes have the same expectancy as the ones it keeps.

---

## The invariant

`avgW` has now held at **`+1.03%`** across:
- 9 stop widths, including no stop at all
- 4 arm samplings (5s, 1min, 2min, 5min seams)
- 6 entry-state filters (`entry_state_filter_ab.py`)

**Nothing moves the average winner.** `[measured]` The exit caps it.

**PARKED (Joe, 0709):** revisit after the correct arm-delay spec exists. Until then, entry-side work on this
book measures the same invariant from new angles.

---

## What this bounds, and what it leaves open

**Bounded (do not repeat):**
- One-line entry filters on the value at the entry bar. `[measured]` at the noise floor.
- One-line entry filters on breach state, alone or in the three-way combination above. `[measured]` mean
  unchanged.
- `breach_rev` as a stand-alone entry gate. `[measured]` no signal at any line.
- The hb33 bias filter (`entry.md` §5). `[measured]` worse than baseline under both alignment stamps.

**Also bounded (added after the stop and seam sweeps):**
- Stop width, `0.5%` to no stop. `[measured]` no optimum; the book loses at every width.
- Arm sampled at the 1 / 2 / 5-minute seam. `[measured]` removes 21% of entries, moves the mean by 0.0003%.

**Open:**
- The states are informative about **which exit fires** while being uninformative about **money**. A rule that
  cuts cheap stops also cuts fat winners. Any robust solution must separate those two, not trade one for the
  other.
- Multivariate combinations were not tested. 84 single states were screened; interactions were not.
- **The exit caps the winner at `+1.03%`.** Every entry-side lever tried so far runs into that ceiling. The
  next question is whether the ceiling is the exit signal's timing or the exit signal itself. **Not yet tested.**
- Entry TIMING (when within the setup) was not varied. Only entry SELECTION (which setups) was.
- **Blocked on the correct arm-delay spec (Joe, 0709).** Entry-side work resumes when it exists.
