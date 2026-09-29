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
