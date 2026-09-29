# Sweep log — 0929, improving the causal baseline

Joe 0929: *"sweep everything that touches, especially the span and slope_min"*, *"be granular with
your sweep steps"*, *"see if you can find more knobs in any of the moving parts, and keep sweeping
until you've exhausted every idea"*. He is away ~10 h; this file is the durable record so nothing is
lost if context rolls.

## THE BASELINE TO BEAT

Window 2026-09-01..2026-09-06, v7 instance, trade config v2, **entry at the emit bar** — the first
bar o9-live can act on.

| | trades | MFE > MAE | MAE mean | MFE mean | summed MAE | summed MFE | MFE−MAE |
|---|---|---|---|---|---|---|---|
| **whole book** | **118** | **65 (55.1%)** | **0.724** | **0.914** | 85.461 | 107.810 | **+22.349** |
| sig_utc opens | 66 | 42 (63.6%) | 0.721 | 1.120 | 47.559 | 73.945 | +26.386 |
| dr-flip opens | 52 | 23 (44.2%) | 0.729 | 0.651 | 37.902 | 33.865 | −4.037 |

The same mech entered at `wsl_sig_utc` — the CEILING, not achievable: 120 trades, 68 (56.7%),
MAE 0.714, MFE 0.963, MFE−MAE +29.919. The gap to the baseline is the emission latency.

## KNOB INVENTORY — `wsf_dtf_v3_config` v10, 55 knobs

Only TWO are flagged `wdc_fitted`, and they are the two Joe named:

| section | knob | value | owner | in key | fitted |
|---|---|---|---|---|---|
| v3_report | `momo_span_min` | 10 min | joe | yes | **YES** |
| v3_report | `momo_slope_min` | 0.4 | joe | yes | **YES** |

Everything else that plausibly moves the signal, by section:

| section | knob | value | owner | in key |
|---|---|---|---|---|
| v3_report | fence_lo / fence_hi | 25.0 / 75.0 | joe | yes |
| v3_report | tf_lo / tf_hi | 1 / 23 | joe | yes |
| v3_report | momo_bank_version | 1 | joe | yes |
| v3_report | xrace_hold | 5 | joe | no |
| stretchy_leash | support_min | 23 | **mine** | yes |
| stretchy_leash | coil_lines | ["gcws30","ws1"] | joe | yes |
| stretchy_leash | confirm_lag_s | 180 | joe | yes |
| stretchy_leash | lookback_s | 240 | joe | yes |
| stretchy_leash | gap_fill | 1 | joe | yes |
| stretchy_leash | exit_anchor | named_bar | joe | yes |
| ws1mage_rev | boundary_xwob | 4 | joe | yes |
| ws1mage_rev | rev_wob | 2 | joe | yes |
| ws1mage_rev | dwell | 3 | **mine** | yes |
| ws1mage_rev | sig_line | gcws30Mage | joe | yes |
| dr | oob_lo / oob_hi | 15.0 / 85.0 | joe | no |
| dr | dr_line_a / dr_line_b | ws1Mage / ws13m | joe | yes |
| anchor_floater | block | 60 bars | joe | yes |
| anchor_floater | dwell_min_per_tf | 1 | joe | yes |
| wsf_chain | momo_fence_r | 17 | joe | yes |
| wsf_chain | momo_xwob | 4 | joe | yes |
| wsf_chain | stall_n | 6 | joe | yes |
| wsf_chain | xcross_target | r | joe | yes |
| wsf_chain | tp_lookback_min | 4 | joe | no |
| mom_xfer | count_min | 2 | joe | yes |
| bands | band_wsf_lo / hi, band_dtf_lo / hi | 1/12, 13/23 | joe | no |
| momo_expiry | fence / return_bars / xwob | 50 / 3 / 5 | joe | no |
| ride_end | mage_dwell / r_wob | 12 / 3 | joe | no |
| handoff | ride_tf_hi | 4 | joe | no |

Plus the trade-side knobs in `wsf_trade_config` v2 (rule1 fence 27/73, rule1_back_min 7,
run_clamp window, latch_wob 8, mage fence 75/25, div_tf, oob 15/85).

And the momo BANK knobs, per TF, reachable via `momo_config`: `momo_slack_ref`, `momo_r2_min`,
`level_slack`, `momo_seam`, `momo_step_min`. `walk_mom_models` already carries Joe's own sweep
ladders for four of them:

    G_SLACK  40.0 down to 14.0 then 13.9   level_slack
    G_SREF   0.05 .. 1.20 step 0.05        momo_slack_ref
    G_SLOPE  0.05 .. 1.20 step 0.05        momo_slope_min
    G_SEAM   skip_r2 | off                 momo_seam

## RESULTS

(appended as each sweep lands)

## RESULT 1 — span x slope, interim at 57 of 182 configs

The harness reproduces the baseline EXACTLY at the banked config (span 10, slope 0.4):
118 trades, 65 (55.1%), MAE 0.724, MFE 0.914, NET +22.349. Every row below is scored the same
way — whole book, entry at the emit bar.

**`momo_span_min` 8 with `momo_slope_min` 0.10 beats the baseline on every measure at once**, and
on fewer trades:

| config | trades | MFE > MAE | MAE mean | MFE mean | NET | per trade |
|---|---|---|---|---|---|---|
| **baseline — span 10, slope 0.40** | 118 | 65 (55.1%) | 0.724 | 0.914 | +22.349 | +0.189 |
| **span 8, slope 0.10** | **104** | **67 (64.4%)** | **0.689** | **1.049** | **+37.514** | **+0.361** |
| span 8, slope 0.15 | 111 | 65 (58.6%) | 0.710 | 0.954 | +27.087 | +0.244 |
| span 8, slope 0.20 | 115 | 68 (59.1%) | 0.710 | 0.951 | +27.754 | +0.241 |
| span 5, slope 0.45 | 127 | 65 (51.2%) | 0.608 | 0.938 | +41.806 | +0.329 |
| span 4, slope 0.35 | 135 | 69 (51.1%) | 0.604 | 0.874 | +36.469 | +0.270 |

TWO DIFFERENT SHAPES IN THE DATA, and they are not the same trade:
  - **short span, mid slope** (4-5 / 0.35-0.50) — fires MORE (127-135 trades), MAE collapses to
    0.60, win rate FALLS to ~51%. The highest raw NET, paid for with 9-17 extra round-trips.
  - **span 8, low slope** (0.10-0.20) — fires LESS (104-115 trades), MAE holds near the baseline,
    MFE rises, win rate climbs to 58-64%. Dominant, not a trade-off.

slope 0.10 is the EDGE of the grid, so span 8 may not be the knee. A refinement grid around
span 6-9 x slope 0.02-0.25 in small steps is queued.

CAVEAT ON `NET`: it is summed MFE minus summed MAE, an excursion aggregate. MFE is the best
excursion, not a captured return. It is not P&L and must not be read as one. Trade count matters
independently: each trade pays a 0.1975% round-trip at 22,000 coins, so 104 trades pays 20.5 pp
against 118 trades' 23.3 pp.

## RESULT 2 — THE HOLDOUT KILLS IT. The span/slope sweep does not generalise.

The sweep is fitted on 2026-09-01..09-06. The holdout re-scores the same configs on
**2026-08-26..09-01** — six days of tape the sweep never saw. Same harness, same code, only the
window moves.

| span | slope | IS trades | IS win% | IS NET | OOS trades | OOS win% | OOS NET | win% drop |
|---|---|---|---|---|---|---|---|---|
| 7 | 0.10 | 114 | 50.0 | +9.445 | 123 | **57.7** | +37.499 | **+7.7** |
| 6 | 0.10 | 118 | 53.4 | +13.603 | 128 | **55.5** | +50.011 | **+2.1** |
| **8** | **0.10** | 104 | **64.4** | +37.514 | 118 | 54.2 | +10.268 | **−10.2** |
| 8 | 0.05 | 102 | 55.9 | +32.598 | 112 | 52.7 | +31.798 | −3.2 |
| 9 | 0.10 | 107 | 56.1 | +24.668 | 113 | 51.3 | +2.287 | −4.7 |
| 8 | 0.12 | 104 | 59.6 | +41.363 | 121 | 51.2 | +7.799 | −8.4 |
| 10 | 0.10 | 102 | 54.9 | +13.064 | 117 | 49.6 | +11.244 | −5.3 |
| **10** | **0.40** (banked) | 118 | 55.1 | +22.349 | 130 | 48.5 | +13.961 | −6.6 |
| 8 | 0.15 | 111 | 58.6 | +27.087 | 123 | 48.0 | +7.963 | −10.6 |
| 5 | 0.45 | 127 | 51.2 | +41.806 | 136 | 47.8 | +19.105 | −3.4 |
| 4 | 0.35 | 135 | 51.1 | +36.469 | 144 | 46.5 | −5.099 | −4.6 |
| 8 | 0.20 | 115 | 59.1 | +27.754 | 132 | 46.2 | +8.932 | −12.9 |

**The correlation between in-sample and out-of-sample is zero.**

| measure | value |
|---|---|
| paired configs | 12 |
| mean IS win% | 55.8 |
| mean OOS win% | 50.8 |
| mean drop | −5.0 |
| **Pearson r (IS win%, OOS win%)** | **−0.037** |
| **Spearman rho** | **−0.056** |
| Pearson r (IS net per trade, OOS net per trade) | **−0.442** |
| OOS rank of the in-sample winner | **3 of 12** |

READ IT PLAINLY:

- **span 8 / slope 0.10 was the best of 182 in-sample and is mid-pack out of sample.** 64.4% → 54.2%.
- the two best OOS configs, 7/0.10 and 6/0.10, were unremarkable in-sample at 50.0% and 53.4%.
- every config loses about 5 points moving to the earlier window — that part is regime, not
  overfitting; the banked config drops 6.6 too. The in-sample winner drops **twice** the average,
  which is the selection on top of the regime.
- a Pearson r of −0.037 means picking the in-sample best is **no better than picking at random**.
  The per-trade net correlation is outright negative.

**CONCLUSION: re-fitting `momo_span_min` and `momo_slope_min` on a 5-day window does not find a
better knob. It finds the noisiest cell in the grid.** Joe's banked 10 / 0.4 is not shown to be
wrong by this work — it is also not shown to be right. Nothing here is a reason to change it.

**PROTOCOL CHANGE, applied to everything that follows:** no config is reported as an improvement
unless it improves on BOTH windows. Every remaining grid is run twice and joined.

## RESULT 3 — the full tape changes the answer. `momo_slope_min` wants to be LOW.

The line cache holds **94.5 days**, 2026-06-05 to 2026-09-07. The 5-day window was the leash
bank's, not the data's. Re-run on three independent windows — W1 06-10..07-20 (40d),
W2 07-20..08-29 (40d), W3 08-29..09-08 (10d) — every config now scores **~2,000 trades** instead
of 118.

| span | slope | W1 % | W2 % | W3 % | mean | sd | net/trade | trades |
|---|---|---|---|---|---|---|---|---|
| **6** | **0.05** | 55.7 | 58.2 | 55.2 | **56.4** | 1.3 | **+0.215** | 1967 |
| **7** | **0.05** | 56.4 | 58.2 | 53.5 | **56.0** | 2.0 | **+0.230** | 1963 |
| 7 | 0.15 | 54.2 | 56.9 | 52.6 | 54.6 | 1.8 | +0.204 | 2055 |
| 5 | 0.05 | 52.4 | 59.4 | 51.1 | 54.3 | 3.6 | +0.196 | 2032 |
| 6 | 0.15 | 54.1 | 55.7 | 51.9 | 53.9 | 1.6 | +0.197 | 2076 |
| 6 | 0.10 | 55.0 | 55.3 | 51.3 | 53.9 | 1.8 | +0.187 | 2027 |
| 7 | 0.10 | 54.0 | 55.3 | 51.8 | 53.7 | 1.4 | +0.194 | 2013 |
| 5 | 0.10 | 51.9 | 58.8 | 50.0 | 53.5 | 3.8 | +0.186 | 2080 |
| 7 | 0.40 | 52.3 | 54.4 | 48.4 | 51.7 | 2.5 | +0.141 | 2181 |
| 6 | 0.40 | 52.2 | 53.9 | 48.6 | 51.6 | 2.2 | +0.141 | 2192 |
| 5 | 0.40 | 51.8 | 51.9 | 47.9 | 50.5 | 1.9 | +0.154 | 2232 |

**THIS IS A DIFFERENT KIND OF RESULT FROM RESULT 1.** That was one cell winning on one window.
This is a **monotone trend holding in three independent windows at three different spans**:

- at span 5, 6 AND 7, win% falls as `momo_slope_min` rises, from ~0.05 up to 0.80.
- the banked 0.40 sits near the bottom of its span's column every time.
- slope 0.05 beats slope 0.40 by **+5.9 points at span 6** (56.4 vs 50.5 at span 5, 56.4 vs 51.6
  at span 6, 56.0 vs 51.7 at span 7) and by **+0.07 net per trade**.
- the standard error on a proportion at ~2,000 trades is 1.1 points, so a 5-point gap is ~5 SE.
  Result 1's 9-point gap sat on 104 trades where the SE was 4.9 points.

0.05 is the EDGE of this grid, so the knee is not yet located. A `lowslope` grid at
0.002 .. 0.07 across spans 6, 7, 8 is running.

NOT YET A RECOMMENDATION. `momo_slope_min` is Joe's, flagged `wdc_fitted`, and was tuned against
his own eyeballed ws7r reading at ~05:36 on 08-25. Nothing here is banked or changed.

## RESULT 4 — FINAL. `momo_slope_min` has a real, monotone effect. The banked 0.4 is too high.

71 configs complete on all three windows. Pooled over the three windows — one trade counts once,
about 1,700–2,000 trades per config, 5,000–13,500 per slope level.

### The slope effect, pooled across ALL spans — the cleanest statement in the whole sweep

| `momo_slope_min` | configs | trades | win% | MAE mean | net/trade |
|---|---|---|---|---|---|
| 0.002 | 3 | 5,092 | 57.40 | 0.771 | +0.2246 |
| 0.005 | 3 | 5,285 | 57.12 | 0.767 | +0.1979 |
| 0.010 | 3 | 5,414 | 55.87 | 0.765 | +0.1769 |
| 0.020 | 3 | 5,484 | 56.55 | 0.743 | +0.2114 |
| **0.030** | 3 | 5,589 | **56.99** | 0.723 | **+0.2432** |
| **0.040** | 3 | 5,661 | 56.63 | 0.715 | **+0.2427** |
| 0.050 | 7 | 12,986 | 56.77 | 0.728 | +0.2303 |
| 0.070 | 3 | 5,821 | 55.20 | 0.714 | +0.2168 |
| 0.100 | 7 | 13,472 | 55.74 | 0.720 | +0.2053 |
| 0.150 | 6 | 12,054 | 54.96 | 0.699 | +0.2025 |
| 0.200 | 6 | 12,280 | 54.05 | 0.694 | +0.1909 |
| 0.300 | 6 | 12,647 | 53.25 | 0.691 | +0.1638 |
| **0.400** | 6 | 12,849 | **53.26** | 0.678 | **+0.1706** ← BANKED |
| 0.600 | 6 | 13,083 | 52.92 | 0.665 | +0.1741 |
| 0.800 | 6 | 13,208 | 52.96 | 0.663 | +0.1651 |

**Monotone from 0.03 to 0.80.** Win rate falls 57.0 → 53.0 and net/trade falls +0.243 → +0.165 as
the knob rises. Below 0.03 it flattens and gets noisier — 0.010 dips to 55.87 — so the knee sits at
**0.03–0.05**. The banked 0.40 sits in the lower third.

### Ranked by WORST window, so nothing is picked on a lucky sample

| span | slope | trades | pooled win% | worst window | net/trade | per-window |
|---|---|---|---|---|---|---|
| **6** | **0.03** | 1,912 | **57.58** | **56.3** | **+0.2588** | 56.3 / 58.8 / 57.6 |
| 8 | 0.10 | 1,905 | 57.17 | 55.8 | +0.2122 | 55.8 / 58.4 / 57.8 |
| 9 | 0.10 | 1,877 | 56.63 | 55.8 | +0.2020 | 56.2 / 57.2 / 55.8 |
| 12 | 0.05 | 1,646 | 59.42 | 55.6 | +0.2451 | 57.4 / 62.3 / 55.6 |
| 10 | 0.05 | 1,746 | 56.76 | 55.5 | +0.2126 | 56.0 / 57.8 / 55.5 |
| 6 | 0.05 | 1,967 | 56.79 | 55.2 | +0.2306 | 55.7 / 58.2 / 55.2 |
| **10** | **0.40** | 2,042 | **54.16** | **52.9** | **+0.1840** | 52.9 / 55.1 / 55.5 ← BANKED, **rank 47 of 71** |

`span 6 / slope 0.03` is the pick: highest worst-window, highest net/trade, and the tightest
per-window spread of any leader. On **fewer** trades than the banked config, 1,912 vs 2,042.

### The same configs on the 5-day baseline window, for continuity

| config | trades | MFE > MAE | MAE mean | MFE mean | NET |
|---|---|---|---|---|---|
| **banked — span 10, slope 0.40** | 118 | 65 (55.1%) | 0.724 | 0.914 | +22.349 |
| span 6, slope 0.03 | 102 | 59 (57.8%) | 0.766 | 1.023 | +26.184 |
| span 7, slope 0.04 | 106 | 56 (52.8%) | 0.799 | 0.972 | +18.416 |
| span 8, slope 0.10 | 104 | 67 (**64.4%**) | 0.689 | 1.049 | +37.514 |
| span 12, slope 0.05 | 94 | 55 (58.5%) | 0.856 | 0.994 | +12.905 |

**And there is the lesson in one row.** span 8 / 0.10 reads 64.4% on the 5-day window and 57.17%
pooled — the 5-day number was inflated by 7 points. span 6 / 0.03 reads 57.8% on 5 days and 57.58%
pooled — it says the same thing on every sample. That is the difference between a fitted cell and
a real effect.

## WHAT IS AND IS NOT ESTABLISHED

ESTABLISHED:
- `momo_slope_min` has a monotone effect on signal quality over 12,000+ trades per level, in the
  same direction on three independent windows and at every span from 5 to 14.
- the banked 0.40 is on the wrong side of it. Moving to 0.03–0.05 is worth about **+3.4 points of
  MFE > MAE and +0.075 net per trade, on fewer trades.**
- `momo_span_min` matters far less than the slope. Spans 6 to 12 are within ~1 point of each other
  at a fixed low slope; span 5 is slightly worse.

NOT ESTABLISHED, AND NOT TO BE READ AS A RECOMMENDATION:
- nothing is banked. `momo_slope_min` is Joe's knob, flagged `wdc_fitted`, and was set by sweeping
  until ws7r read `sideways` at his own eyeballed ~05:36 on 08-25. **That eyeball is a measurement
  and this sweep does not overrule it** — a lower slope may break the reading the knob was fitted
  to. That has not been checked.
- every number here is MAE/MFE excursion, not P&L. `net/trade` is summed MFE minus summed MAE per
  trade and is not a captured return.
- the whole sweep assumes the rest of the chain is held at the banked values. Interactions with
  `support_min`, the fence, the leash lags and the ws1mage_rev wobs are unswept on the full tape.

## RESULT 4a — the complete set, 85 configs. Conclusion unchanged; one figure corrected.

The `wide` grid finished after the Result 4 write-up (85 configs complete, was 71). The banked
config's own numbers are identical — pooled 54.16%, worst window 52.9%, net/trade +0.1840 — but the
comparison set grew, so:

**CORRECTION: the banked span 10 / slope 0.40 ranks 29 of 85, not 47 of 71.** The extra configs
were mostly high-slope cells that rank below it. Its measured performance did not change.

The slope effect on the complete set, pooled across all spans:

| `momo_slope_min` | configs | trades | win% | MAE mean | net/trade |
|---|---|---|---|---|---|
| 0.002 | 3 | 5,092 | 57.40 | 0.771 | +0.2246 |
| 0.010 | 3 | 5,414 | 55.87 | 0.765 | +0.1769 |
| 0.030 | 3 | 5,589 | 56.99 | 0.723 | +0.2432 |
| 0.040 | 3 | 5,661 | 56.63 | 0.715 | +0.2427 |
| **0.050** | 8 | **14,589** | **57.33** | 0.734 | **+0.2362** |
| 0.100 | 8 | 15,149 | 55.96 | 0.728 | +0.2055 |
| 0.150 | 8 | 15,569 | 55.55 | 0.714 | +0.2025 |
| 0.200 | 8 | 15,924 | 54.59 | 0.706 | +0.1915 |
| 0.300 | 8 | 16,423 | 53.99 | 0.698 | +0.1742 |
| **0.400** | 8 | 16,719 | **53.87** | 0.684 | **+0.1812** ← BANKED |
| 0.600 | 8 | 17,091 | 53.33 | 0.672 | +0.1803 |
| 0.800 | 8 | 17,370 | 53.28 | 0.667 | +0.1726 |

Slope 0.05 now carries 14,589 trades across 8 spans and reads 57.33% — **+3.5 points over the
banked 0.40 on a like-for-like pooled basis**. The monotone fall from 0.05 to 0.80 is intact.

Top by worst window is unchanged: **span 6 / slope 0.03**, pooled 57.58%, worst 56.3%,
net/trade +0.2588, per-window 56.3 / 58.8 / 57.6, on 1,912 trades against the banked 2,042.

## RESULT 5 — a SECOND monotone knob: the v3 row fence. And `support_min` is already at its ceiling.

Nine knob families re-run on the three-window protocol, one variable at a time from the banked
point. Pooled over the three windows.

### `fence_lo` / `fence_hi` — banked 25.0 / 75.0 — MONOTONE, tighter is better

| fence | trades | win% | worst window | net/trade | per-window |
|---|---|---|---|---|---|
| **10.0 / 90.0** | 1,559 | **60.23** | 54.8 | **+0.2790** | 59.2 / 62.5 / 54.8 |
| 12.5 / 87.5 | 1,661 | 58.10 | 51.6 | +0.1954 | 58.2 / 59.7 / 51.6 |
| 15.0 / 85.0 | 1,740 | 56.38 | 49.2 | +0.1746 | 56.0 / 58.5 / 49.2 |
| 20.0 / 80.0 | 1,903 | 55.07 | 50.9 | +0.1953 | 53.6 / 57.5 / 50.9 |
| 22.5 / 77.5 | 1,981 | 54.47 | 52.3 | +0.1803 | 53.1 / 56.4 / 52.3 |
| **25.0 / 75.0** | 2,042 | **54.16** | 52.9 | **+0.1840** | 52.9 / 55.1 / 55.5 ← BANKED |
| 30.0 / 70.0 | 2,139 | 53.53 | 52.1 | +0.1276 | 52.1 / 54.9 / 53.6 |
| 35.0 / 65.0 | 2,214 | 52.57 | 50.7 | +0.1324 | 50.7 / 54.8 / 50.8 |
| 40.0 / 60.0 | 2,276 | 52.02 | 47.3 | +0.1315 | 52.0 / 53.3 / 47.3 |

- pooled win% falls monotonically from 60.2 at 10/90 to 52.0 at 40/60. **+6.1 points over the
  banked 25/75**, on 24% FEWER trades (1,559 vs 2,042).
- mechanically obvious in hindsight: a tighter fence demands the line's `r` be further out of
  bounds before the row fires, so it admits fewer and stronger rows.
- **CAVEAT, and it matters:** on WORST window the picture is not monotone. 10/90 reads 54.8 but
  12.5 reads 51.6 and 15.0 reads 49.2, both BELOW the banked 52.9. The per-window spread at 10/90
  is wide (59.2 / 62.5 / 54.8). Pooled it is clean; per-window it is not.

### `support_min` — mine, banked 23 — ALREADY AT ITS CEILING

| support_min | trades | win% | net/trade |
|---|---|---|---|
| **23** | 2,042 | **54.16** | **+0.1840** ← BANKED, and the best |
| 22 | 2,115 | 53.62 | +0.1569 |
| 21 | 2,187 | 53.45 | +0.1342 |
| 20 | 2,231 | 52.44 | +0.1138 |
| 15 | 2,212 | 52.22 | +0.0505 |

Every value below 23 is worse, monotonically in net/trade. **23 is the maximum possible** — the
band is ws1..ws23, so 23 means every line must support. The knob is pinned at its strictest setting
and cannot go higher without widening the band.

### The leash knobs — FLAT, nothing to find

| knob | range swept | win% range |
|---|---|---|
| `confirm_lag_s` | 60 .. 600 s | 54.2 – 55.2 |
| `lookback_s` | 0 .. 720 s | 53.7 – 54.6 |
| `gap_fill` | 0 or 1 | 54.53 vs 54.16 |

All inside noise on ~2,000 trades. **Joe's 0917 "that 180s is required ... it's not negotiable"
costs nothing and gains nothing measurable** — the mech is insensitive to it across a 10x range.

### Do slope and fence compound?

Both findings cut trade count and lift win rate. They may be the same signal counted twice. A
`combo` grid — span 6/8 x slope 0.03/0.05/0.40 x fence 10/15/20/25, with BASE as control — is
running.

## RESULT 6 — SLOPE AND FENCE COMPOUND. The strongest configuration measured.

`combo` grid: span 6/8 x slope 0.03/0.05/0.40 x fence 10/15/20/25, all on three windows.

| span | slope | fence | trades | pooled win% | worst window | net/trade | per-window |
|---|---|---|---|---|---|---|---|
| 8 | 0.05 | 10.0 | 1,457 | **61.84** | 59.2 | +0.2816 | 59.5 / 64.6 / 59.2 |
| **8** | **0.03** | **10.0** | **1,444** | **61.57** | **60.3** | **+0.2948** | **60.3 / 63.0 / 60.4** |
| 6 | 0.03 | 10.0 | 1,493 | 59.48 | 51.2 | +0.2454 | 58.2 / 62.6 / 51.2 |
| 8 | 0.03 | 15.0 | 1,570 | 58.79 | 53.7 | +0.2395 | 57.0 / 61.7 / 53.7 |
| 8 | 0.40 | 10.0 | 1,611 | 57.98 | 53.6 | +0.1991 | 58.6 / 58.5 / 53.6 |
| 8 | 0.03 | 25.0 | 1,777 | 56.44 | 51.8 | +0.2210 | 54.7 / 59.3 / 51.8 |
| **8** | **0.40** | **25.0** | 2,109 | **54.77** | 52.6 | **+0.1960** | 54.6 / 55.4 / 52.6 |
| 6 | 0.40 | 25.0 | 2,192 | 52.55 | 48.6 | +0.1588 | 52.2 / 53.9 / 48.6 |

**The decomposition, from span 8 at the banked slope and fence:**

| change | pooled win% | delta |
|---|---|---|
| span 8, slope 0.40, fence 25 (banked knobs) | 54.77 | — |
| slope alone → 0.03 | 56.44 | **+1.67** |
| fence alone → 10 | 57.98 | **+3.21** |
| **both** | **61.57** | **+6.80** |

+1.67 and +3.21 sum to 4.88; together they deliver **6.80**. They do not merely stack, they are
**super-additive**. Whatever each knob is filtering, the intersection is cleaner than either alone.

**`span 8 / slope 0.03 / fence 10-90` is the strongest thing measured in this sweep:**

- pooled **61.57%** MFE > MAE against the banked **54.16%** — **+7.4 points**
- **worst window 60.3%** — the highest worst-window of any of the 109 configs tested
- per-window **60.3 / 63.0 / 60.4** — the tightest spread of any leader, and all three above 60
- net/trade **+0.2948** against the banked **+0.1840** — **+60%**
- on **1,444 trades against 2,042** — 29% fewer, so 29% less round-trip cost as well

fence 10 was the EDGE of the combo grid. An `edge` grid at fence 2.5 / 5.0 / 7.5 / 10.0 x
slope 0.02 / 0.03 / 0.05 x span 7 / 8 / 9 / 10 is running to find where it stops.

STILL NOT A RECOMMENDATION. Three things have to be true before any of this is worth banking, and
none has been checked:
1. that `momo_slope_min` at 0.03 still reproduces the ws7r `sideways` reading at ~05:36 on 08-25
   that the knob was fitted to — Joe's eyeball, and it outranks this sweep;
2. that a 10/90 fence is a mechanic Joe wants, not an artefact of demanding near-saturated `r`;
3. that MFE > MAE and net/trade are the objectives he is optimising, rather than something the
   excursion aggregate only proxies.

## RESULT 7 — the fence keeps paying to 2.5/97.5, and that is where I start doubting it

`edge` grid: span 7-10 x slope 0.02/0.03/0.05 x fence 2.5/5/7.5/10, three windows, 44 complete.

### Fence effect pooled across the edge grid

| fence | configs | trades | pooled win% | net/trade |
|---|---|---|---|---|
| **2.5 / 97.5** | 11 | 13,432 | **63.45** | **+0.3043** |
| 5.0 / 95.0 | 11 | 14,241 | 62.64 | +0.2853 |
| 7.5 / 92.5 | 11 | 15,097 | 60.76 | +0.2725 |
| 10.0 / 90.0 | 11 | 15,877 | 61.00 | +0.2686 |

### Top by worst window

| span | slope | fence | trades | pooled% | worst | net/trade | per-window |
|---|---|---|---|---|---|---|---|
| **10** | **0.02** | **2.5** | **1,204** | **66.20** | **65.2** | **+0.4110** | **65.2 / 66.7 / 68.7** |
| 10 | 0.03 | 2.5 | 1,204 | 64.87 | 62.0 | +0.3774 | 62.0 / 66.7 / 70.0 |
| 9 | 0.05 | 2.5 | 1,194 | 63.23 | 60.7 | +0.2898 | 61.5 / 65.3 / 60.7 |
| 8 | 0.03 | 10.0 | 1,444 | 61.57 | 60.3 | +0.2948 | 60.3 / 63.0 / 60.4 |
| 10 | 0.03 | 5.0 | 1,286 | 63.22 | 60.1 | +0.2920 | 60.1 / 65.7 / 65.6 |

**`span 10 / slope 0.02 / fence 2.5-97.5`: pooled 66.20%, worst window 65.2%, net/trade +0.4110,
per-window 65.2 / 66.7 / 68.7, on 1,204 trades.** Against the banked 54.16% / +0.1840 / 2,042 that
is +12.0 points, +123% net per trade, on 41% fewer trades.

### WHY I DO NOT BELIEVE THIS IS A KNOB SETTING

The numbers are real — 1,204 trades, all three windows above 65%, about 8 standard errors from the
banked. What I doubt is that it is still **Joe's mechanic**.

- the v3 row rule is *"the FIRST bar in that dr run where the line's r is `sideways` AND outside the
  fence"*, and Joe set that fence to 25/75 on 0910, raising it from 30/70.
- at **2.5 / 97.5** the test is no longer "outside the fence". It is "`r` is pinned at the extreme
  of its own 0-100 range". A StochRSI below 2.5 is saturated, not merely out of bounds.
- so this may not be a better setting of the fence. It may be a **different mechanic wearing the
  fence's name** — exhaustion at saturation rather than a fence exit.
- **oob is 15/85 everywhere else in this system.** 2.5 is not near any fence Joe has named.
- trade count falls 41%, from 2,042 to 1,204. Whatever this selects, there is much less of it.

A `limit` grid at fence 0.25 .. 2.5 is running. If win% keeps climbing as the fence approaches zero
while the trade count collapses, that confirms the reading above: it is finding saturation, not
tuning a fence. **That is a question for Joe to name, not for me to bank.**

## RESULT 8 — FINAL. The fence has a real knee at 2.0–2.5. My saturation doubt is refuted.

`limit` grid: span 8/10/12 x slope 0.02/0.03 x fence 0.25 .. 2.5, three windows, 36 configs.

| fence | configs | trades | pooled win% | net/trade | trades per config |
|---|---|---|---|---|---|
| 0.25 | 6 | 6,836 | 64.83 | +0.3026 | 1,139 |
| 0.50 | 6 | 6,895 | 64.99 | +0.3087 | 1,149 |
| 1.00 | 6 | 6,955 | 63.93 | +0.3313 | 1,159 |
| 1.50 | 6 | 6,981 | 64.80 | +0.3505 | 1,163 |
| **2.00** | 6 | 7,158 | 64.85 | **+0.3663** | 1,193 |
| 2.50 | 6 | 7,244 | 64.76 | +0.3473 | 1,207 |

**I predicted that if this were saturation-chasing, win% would keep climbing toward fence 0 while
the trade count collapsed. Neither happened.**

- win% is **FLAT** at 64–65% across the whole range 0.25 .. 2.5. It stopped improving at ~2.5.
- net/trade **peaks at fence 2.00** (+0.3663) and falls either side.
- the trade count barely moves — 1,139 to 1,207 per config, a 6% spread. It does not collapse.

That is a genuine knee, not an asymptote. **The fence effect runs from 40 down to about 2.5 and
then stops.** A knob with a measured knee is a knob; my saturation objection is answered and
withdrawn.

### Top by worst window, across everything measured (109+ configs)

| span | slope | fence | trades | pooled% | worst | net/trade | per-window |
|---|---|---|---|---|---|---|---|
| **10** | **0.02** | **2.50** | 1,204 | 66.20 | **65.2** | **+0.4110** | 65.2 / 66.7 / 68.7 |
| 12 | 0.03 | 2.50 | 1,193 | **66.39** | 64.0 | +0.4067 | 64.0 / 68.3 / 68.1 |
| 10 | 0.03 | 1.50 | 1,138 | 65.82 | 63.5 | +0.4006 | 63.5 / 67.9 / 67.3 |
| 12 | 0.02 | 2.50 | 1,182 | 65.74 | 63.4 | +0.3493 | 63.4 / 67.8 / 66.7 |
| 10 | 0.02 | 0.50 | 1,157 | 65.86 | 62.8 | +0.2927 | 63.8 / 68.4 / 62.8 |
| **10** | **0.40** | **25.0** | 2,042 | 54.16 | 52.9 | +0.1840 | 52.9 / 55.1 / 55.5 ← BANKED |

## THE BOTTOM LINE OF THE WHOLE SWEEP

| | banked | best measured | delta |
|---|---|---|---|
| `momo_span_min` | 10 | 10 | unchanged |
| `momo_slope_min` | **0.40** | **0.02** | |
| fence | **25.0 / 75.0** | **2.5 / 97.5** | |
| trades (3 windows) | 2,042 | 1,204 | −41% |
| pooled MFE > MAE | 54.16% | **66.20%** | **+12.0 pts** |
| worst window | 52.9% | **65.2%** | **+12.3 pts** |
| net / trade | +0.1840 | **+0.4110** | **+123%** |

Two knobs, both with measured knees, both reproducing on three independent windows, both cutting
trade count. `momo_span_min` is NOT one of them — 10 is as good as anything.

## WHAT JOE HAS TO RULE BEFORE ANY OF IT MOVES

1. **the eyeball.** `momo_slope_min` 0.4 and `momo_span_min` 10 were fitted by sweeping until ws7r
   read `sideways` at Joe's own ~05:36 on 08-25. **Does slope 0.02 still reproduce that reading?**
   Unchecked, and his eye outranks this sweep.
2. **the fence is his number.** He set 25/75 on 0910, raising it from 30/70. 2.5/97.5 is a
   different order of thing and `oob` is 15/85 everywhere else in this system. Whether a 2.5 fence
   is the mechanic he means is his to name.
3. **trade count falls 41%.** 1,204 against 2,042 over 90 days. Fewer, better signals — but he may
   want the coverage.
4. **MFE/MAE is not P&L.** `net/trade` is summed MFE minus summed MAE. It is excursion, not capture.

NOTHING IS BANKED. No table written, no config changed, no production file touched. The harness
writes to `docs/sweeps/*.jsonl` only.

## RESULT 9 — the remaining knob families. A third monotone knob, and two provably inert ones.

All nine families complete on three windows. Banked reference: 2,042 trades, 54.16%, net +0.1840.

### `momo_fixed_samples` — banked 21 — MONOTONE, and it runs AGAINST the "full dataset" intuition

The lattice is `samples` points spanning `momo_span_min`. At span 10 (120 bars): 21 samples = a
point every 6 bars; **121 samples = every bar, i.e. the full dataset**; 3 samples = every 60 bars.

| samples | step | trades | win% | worst window | net/trade |
|---|---|---|---|---|---|
| 3 | 60 bars | 1,767 | **57.50** | 48.7 | +0.2419 |
| 5 | 30 bars | 1,790 | 56.65 | 51.7 | +0.1911 |
| 7 | 20 bars | 1,819 | 57.06 | 51.2 | +0.2232 |
| **9** | **15 bars** | 1,856 | 55.77 | **55.5** | +0.2119 |
| 13 | 10 bars | 1,920 | 55.10 | 51.2 | +0.2077 |
| **21** | **6 bars** | 2,042 | **54.16** | 52.9 | **+0.1840** ← BANKED |
| 41 | 3 bars | 2,127 | 53.74 | 52.2 | +0.1891 |
| 61 | 2 bars | 2,210 | 51.36 | 50.4 | +0.1521 |
| **121** | **1 bar — every bar** | 2,304 | **51.09** | 46.7 | +0.1373 |

**Joe 0929 asked for "full datasets (as opposed to sampling)". On this knob the data says the
opposite.** Reading every bar — samples 121 — is the WORST setting in the family at 51.09%, and
win% falls monotonically as the lattice gets denser. The sparse lattice is not a shortcut; it is
doing work. A 3-point fit over 120 bars measures the window's overall tilt; a 121-point fit chases
every wiggle in it.

The honest pick in this family is **samples 9**, not 3: highest worst-window in the family at 55.5
(against the banked 52.9), while samples 3 has the family's WORST worst-window at 48.7 despite the
top pooled figure.

### `level_slack` (banked 13.9) and `momo_slack_ref` (banked = slope) — PROVABLY INERT

| level_slack | trades | win% | net/trade |
|---|---|---|---|
| 0.0, 5.0, 10.0, **13.9**, 18.0, 22.0 | 2,042 | 54.16 | +0.1840 |
| 28.0 | 2,046 | 54.20 | +0.1840 |
| 34.0 | 2,070 | 53.67 | +0.1733 |
| 40.0 | 2,112 | 52.98 | +0.1676 |

`momo_slack_ref` at 0.05, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0, 1.2 — **all nine byte-identical** at
2,042 / 54.16% / +0.1840.

**Why, read from the code and confirmed by where it breaks.** The level gate is
`r >= 50 - slack` at dr +1, and `slack = level_slack * trk`. But the v3 row ALSO requires `r`
outside the 25/75 fence. At dr +1 an `r` below 25 fails the level gate outright (25 < 50 − 22), so
only `r > 75` can ever produce a row — and `r > 75` clears the level gate for **any** slack up to
22. The fence dominates the level gate, so neither knob can move a verdict.

It starts to bite at exactly the predicted point: `level_slack` 28 gives `50 − 28 = 22`, so an `r`
between 22 and 25 now passes both tests and new rows appear — 2,046 instead of 2,042. The
explanation predicts the break point and the data lands on it.

**Consequence: `level_slack` and `momo_slack_ref` are dead knobs at the banked fence.** They would
only come alive if the fence moved above 50 − level_slack.

### `curl_arc_min` (banked 4.0) — FLAT

0.5 reads 54.94, banked 4.0 reads 54.16, and disabling the curl test entirely reads 54.23. The
whole family spans 53.5 – 54.9 on ~2,000 trades. Nothing to find.

### the `ws1mage_rev` wobs — Joe's values are at or near the best

| knob | banked | best swept | delta |
|---|---|---|---|
| `boundary_xwob` | 4 | 4 | none — 4 is the best of 1,2,3,4,5,6,8,10,12 |
| `rev_wob` | 2 | 8 (54.64 vs 54.16) | +0.5 pts, inside noise |
| `dwell` | 3 | 3 | none — 3 is the best of 1,2,3,4,6,8,12 |

`boundary_xwob` 4 and `dwell` 3 are already optimal. `rev_wob` 8 is half a point better than 2,
which is inside noise on 2,000 trades.

### `tfband` — INCOMPLETE

Only the control config completed; the tf_lo/tf_hi variants produced no trades or errored. **Not
measured.** Re-run needed if the TF band matters.
