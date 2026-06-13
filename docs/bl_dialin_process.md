# BL line-pair dial-in — durable process

Tunes a **breach line + its support BB as a PAIR**, machine-native, ranked by **placement**
(smallest adverse swing to overcome), validated across **random** windows. Re-runnable;
tick each stage. Born from the s30r/s30M arc (2026-06-12) — corrected for two crossovers
(machine-native exit, placement-not-profit).

## Metric — NOT profit
- **Smallest adversarial swing to overcome** = max adverse % from entry *before* the curated
  ≥0.9% swing is captured. Lower = entry sits closer to the turn.
- **Filter: drop every trade needing > 0.44%** (keep the ≤0.44 placements — closest to the swing).
- Why not profit: this is a **turn-detector / placement component**; profit is the downstream
  HTF job. Swings are curated ≥0.9 (`swing_detect`), so placement is the honest lens. A low
  win% is **not** a bad combo — by elimination it means the **entry opened too far after the
  swing** → that is what the **lookback sweep** dials.

## The trade — machine-native (exit1/2/3 × `exit_mask`, NEVER bls state)
- **Entry** = bny30-bias-gated raw PK (gca5m fire-edge) admitted within **`c_bls3 ± lookback`**
  (mean-revert). `c_bls3` = combined cascade resolved = **gate open**; the ±window lets a
  PK that isn't time-synced to c_bls3 still **capitalize on the open gate**.
- **Exit** = the machine's *enabled* exit firing (`state→3`): `exit1` (support OOB→IB) /
  `exit2` (reversal-ref) / `exit3` (✕-toward-IB), gated by the per-line `exit_mask` bitmask
  (`exit1=1 exit2=2 exit3=4 exit4=8`). A **BB support exposes only `exit1`**.
- ⚠ The first s30 grind crossed bls `state ∈ {1,2,3}` into the exit role — bypassing `exit1`.
  This process reads the **real exit triggers**.

## Bias gate — ESSENTIAL
- bny30 **latched bias** on entries (−oob at the last IB→OOB breach, held through IB; keep
  only `dir==bias`). The bias **BB line is swappable** (bny30 → any other BB line).

## Swept dimensions — the pair + the mask + the lookback
- Breach K: `k_len / rsi_len / stc_len / src`
- Support BB: `bb_len / bb_mult / src`
- `exit_mask`: the bit combos (1, 4, 5, 7, …)
- **lookback** (`c_bls3 ± lookback` half-width): admits a non-time-synced PK to take the
  open gate — the goal is letting a PK that fires slightly before/after c_bls3 still capitalize.

## Windows
- **≥3 RANDOM days** from the past 42 (capped at the loaded tape, ~35d — supervisor backfill).
- **Fresh draw every run** (default — so you can't silently re-test stale days).
- **`--replay`** pins a prior draw for an apples-to-apples re-run (logs + reuses the days).

## Time budget — self-sizing
- `--budget <hours>`. First ~3 min: **speedtest** a small (combos × windows) sample →
  sec / combo-window. Then **model** grid-size × windows × top-candidates to fit the budget,
  keep ~10% margin, **log the chosen plan**.

## Stages — tick each run
1. ☐ **Grind** the pair + `exit_mask` + lookback · machine trade (breach→exit) · bias-gated · random windows.
2. ☐ **Placement** per trade (smallest adverse to overcome) · **drop > 0.44** · rank by lowest median adverse.
3. ☐ **Multi-window consistency** — keep combos robust across **all** windows; drop the overfits (caught slow-K).
4. ☐ **Least-profitable-exit-type** column — toggle each `exit_mask` bit, report which adds least → mask it off per line.
5. ☐ **Pre/post-swing guard** — free 2nd lens from the bl_ UTC columns (`swing_closest_dt` / `entry_dt` /
   `swing_adverse_dt`): was the entry pre or post the swing? (No cluster_scoring — that's downstream.)
6. ☐ **Champion → bl_ reports + pine recon** — both render the real `exit1/2/3 × exit_mask`.

## Out of scope here
- `cluster_scoring` (downstream keeper-library KPI).
- profit / fees (component = placement; profit lives in the HTF combination).
