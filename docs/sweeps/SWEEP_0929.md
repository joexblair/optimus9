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
