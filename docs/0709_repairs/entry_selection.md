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

## What this bounds, and what it leaves open

**Bounded (do not repeat):**
- One-line entry filters on the value at the entry bar. `[measured]` at the noise floor.
- One-line entry filters on breach state, alone or in the three-way combination above. `[measured]` mean
  unchanged.
- `breach_rev` as a stand-alone entry gate. `[measured]` no signal at any line.
- The hb33 bias filter (`entry.md` §5). `[measured]` worse than baseline under both alignment stamps.

**Open:**
- The states are informative about **which exit fires** while being uninformative about **money**. A rule that
  cuts cheap stops also cuts fat winners. Any robust solution must separate those two, not trade one for the
  other.
- Multivariate combinations were not tested. 84 single states were screened; interactions were not.
- The stop is `0.90%` and 49.9% of trades hit it. That width was swept against the look-ahead book. With
  `avg winner +1.038%` and `avg loser -1.055%` nearly symmetric, a trade converted from stop to signal-exit is
  worth roughly two units. **Not yet swept on the causal book.**
- Entry TIMING (when within the setup) was not varied. Only entry SELECTION (which setups) was.
