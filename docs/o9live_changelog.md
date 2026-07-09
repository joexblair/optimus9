# o9-live tweak history

Timestamped log of tweaks **applied** to o9-live and ones **left in the dust** (with the reason). Big tweaks reference
their spec/memory rather than restate it (SRP). Newest first.

| date | tweak | status | reason | ref |
|---|---|---|---|---|
| 2026-07-09 | Exit **curl-cascade** — gate s7r breach-then-OOB-coarse-curl@105s + unlatch s5r coarse-curl@40s | **APPLIED** (fold to `lr_exit_v2` pending) | +1.2% v2_walk (6wk); signal-timing, robust under cost; captures more MFE on a confirmed reversal | [[project_exit_curl]], `docs/exit_brd.md`, `exit_curl_ab.py` |
| 2026-07-09 | Fixed **take-profit** overlay | **DROPPED** | Catastrophic (−23%→−100%): caps fat-tail winners; give-back savings dwarfed. win% climbs while PnL→0 | [[project_exit_curl]] |
| 2026-07-09 | **Trailing-stop** overlay (naive + armed) | **DROPPED** | Catastrophic (best −49%): crypto intra-move whip chops any price-based exit. **Rule: exits must be signal-based** | [[project_exit_curl]] |
| 2026-07-09 | **Time-out** / max-hold exit | **DROPPED** (untested) | Superseded by the future **consolidation-detector** (forced clean optimal exit), parked post-SG | — |
| 2026-07-08 | **Hedge mode** — fx_position positionIdx legs (exchange) + per-side strategy legs (client) | **SHIPPED** (cutover 2026-07-09) | Realizes overlapping opposite legs (recovers 515/1953 dropped entries = the ~18% premium); backtest-match | [[project_hedge_dynamic_risk]], `docs/hedge_mode_spec.md` |
| 2026-07-08 | **RiskGovernor** + `risk_config` (dynamic leverage / pyramid gate / exposure cap) | BUILT (not wired) | v2_walk-grounded: cap 16× (stack p99), dd steps 2%/3.5% (drawdown p90/p95) | [[project_hedge_dynamic_risk]], `docs/dynamic_risk_spec.md` |
| 2026-07-08 | **filler_invisible** default ON | CONFIRMED (already on since 0705) | Re-validated: quality-neutral vs OFF; TV-parity; the 24% live-churn was a warmup-edge artifact | [[project_filler_invisible]] |
| 2026-07-08 | Seam grace **301→2000ms** | INTERIM | Late ticks mutate the std-sensitive BB → live↔backtest desync; 2000ms cuts it to ~6%. Proper fix = finalized-bar read | [[project_o9live_desync_fix]] |
| 2026-07-08 | **arm_delay** producer | **VOIDED** | Confirmed look-ahead (forward scan can't be clamped causal); the look-ahead-era PnL is void | [[project_tide_exit]] |

## How to use
Add a row when a tweak lands in o9-live or is decided-against. Keep the `reason` to the one-line "why"; link the spec for
detail. This is the o9-live-specific decision trail (distinct from the backtest sweep logs like `exit_curl_ab.py`).
