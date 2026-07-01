# Exit v2 + bias filter — design & real-world grounding (0701)

Everything here is anchored to one real trade so ideas are easy to share: **06-17 18:46 SHORT** (FARTCOINUSDT).
Data window = the real-tick span 06-17 → 06-22 (n=266 v2 entries). See also `lr_cascade_design.md` (cascade
internals), `bias_mechanics_design.md` (bro-cross), `epoch_anchor_spec.md`.

## The running trade — 06-17 18:46 SHORT (threads through every section)
| moment | time | what |
|---|---|---|
| entry | 18:46:00 | short opens |
| favourable extreme reached | **19:05:35** | s5m breaches LO (the "given" — price is now genuinely favourable) |
| cascade gate opens | 19:37:05 | s7r finally predict-then-breaches — **32 min late** (the flaky prediction) |
| the curl | 19:37:10 | s5r flips up (reversal toward es) |

Exits it produced, three ways:
- **og_book** (corrected): **+1.70%** @ 19:05:35 · **cascade predict=False**: +2.1% @ 19:22 · **cascade predict=True**: +2.7% @ 19:37.

---

## 1. og_book — the entry-quality ruler (the corrected reference)
- **What:** `lr_exit(curl_fam=s7, exit_on=s30a_s15a, predict_gate=True, arm_gate=True)`. The old small-profit exit,
  gated so the finisher can't fire before the favourable **s5m breach** has happened.
- **Why the fix:** raw `lr_exit` fired the finisher whenever it liked — **69% of its exits had no s5m breach yet**
  (s5m only *blocked* the trigger, never *gated* it). `arm_gate=True` requires the breach first.
- **Numbers:** net **+66.5%**, win **66%**, avg **+0.250%** (n=266). [old un-gated: +59.8% / 75% — the 75% was
  early-profit-taking, not extra wins.] 18:46: +0.86% → **+1.70%**.
- **Role:** the STABLE, exit-agnostic ruler the bias dials against. **Not** the shipping exit — the cascade is.
- **Key fact (validated):** for the 137 wins that exited before their s5m breach, **137/137 breach favourable later**
  — the opposite-side s5m breach is a *given*; gating on it strengthens wins, never removes them. (It can lower
  *win%* — 75→66 — because the SL can hit *before* the breach on some; survivors are bigger, so net rises.)

## 2. Exit cascade (lr_exit_v2) — the entry machine pointed at the −es extreme
One machine, two polarities: entry fires on `es`, exit fires on `−es` (= `bd`). Shared `_finish` core (SRP).
```
exit-arm  s5m breach on bd            →   19:05:35
gate      {gate_fam}r predict-then-breach on bd (slip knob; predict on/off)   →   19:37:05
unlatch   s5r reversal toward es (the curl — s5r : s7r :: s2M : s3/s4)         →   19:37:10
finisher  _finish: latch s30a+s15a from the arm, delatch at the unlatch  →  exit = max(latched, unlatch)
```
- **Gate-line AB** (over 266): slower `s7r` = bigger rides + more culls (48%); faster `s6r`/`s5r` = fewer culls,
  lower net; **`s7r+slip20` = fewest culls (28%) at +50.8% net** (slip recovers near-OOB curls).
- **The flaky prediction (18:46 in the act):** `predict=True`'s s7r prediction lagged the breach by **32 min**
  (19:05→19:37), so the exit landed at a "seemingly random" point — wherever the prediction tripped. `predict=False`
  fires on the s7r breach itself (19:22). **The s7m/s7M multi sweep (84,700 combos already built) tunes this.**

## 3. Strand rescue — the 67 refugees  ⭐ NEW
- **Problem:** when **s7r never breaches**, the gate never opens and the trade rides to SL. This hits **67 trades
  = 25% of the book, 47% of all SLs** (predict=False: 142 SLs, 67 stranded).
- **Premise (validated):** ALL 67 had a favourable **s5r + s5M** curl *before* the SL — the price handed us a
  window, the s7r gate just wouldn't let us take it. None were lost causes.
- **Mechanism (Joe 0701) — two jobs, cleanly split:**
  - **s7r-momentum GATE (the "tractor beam"):** while s7r is being pulled toward the breach (outside a ~20/80
    fence AND still approaching), HOLD. Poll each **s15a cycle** (exit-side s15a breach → next exit-side s15a
    breach; lookback baked in). If s7r **recedes toward 50** (breach won't come) → **release** the gate; else wait
    another cycle.
  - **s5r + s5M reversal TRIGGER:** once released, s5r AND s5M reversing toward es opens the finisher → exit.
  - **SRP:** momentum *decides* (gate), reversal *fires* (trigger). The reversal alone is too loose (fast lines
    wiggle in any window); **the s7r gate is what turns "any wiggle" into "the real curl."**
  - **Gate-as-data:** the exit gate now has multiple openers (s7r-breach · s5r+s5M-when-s7r-recedes) → rows in a
    gate table (like `lr_gate`), not hardcoded branches.
- **Sizing:** **ceiling +60.7% swing** (−33.5% SL → +27.2% recovered, 98% win) — but this is the LOOSE upper bound
  (earliest wiggle, s7r gate not yet applied). **Real capture = a fraction; the built mechanism measures it.**

## 4. Bias entry-filter — the hb33 lever (sweep complete)
- **What:** the hb33 bro-cross bias (3 sets `hbhl33`/`hblo33`/`hbhi33`; first OOB Mage×min cross flips the state,
  clustered) → **reject against-grain entries** (`bias == −bd`) at entry, before the exit ever runs.
- **Sweep:** 84,700 combos = TF(9–36) × mage-len(19±5) × min-len(13±5) × hbhl33 mage-src(5) × min-src(5), scored
  as filtered **avg_ret + win** on og_book (`bias_grav_sweep.py`, ~31 min; reuses `bro_stream`/`bro_verdict`).
- **Result:** best config (tf26 / lenM24 / lenm9) **avg +0.389% / win 77% / kept 137** vs baseline +0.250 / 66% →
  **~2× total net-of-cost** (+26% vs +13%), ~4× per-trade.
- **Robustness:** **83,311 / 84,699 configs (98%) beat baseline** — rejecting a *random* half wouldn't, so the
  with-grain signal is genuinely informative (counter-trend entries are broadly worse). Top avg is a **16-way tie**
  → take *a* robust config, don't over-fit *the* config.
- **Caveat:** one 5-day window; out-of-sample validation owed. Vindicates the OG-book choice — it exposed a signal
  the cull-labels (50/50) hid.

## Two validated levers, and the open decisions
- **Lever A — bias entry-filter:** ~2× net-of-cost (sweep confirmed, robust).
- **Lever B — s7r-strand rescue:** 67 refugees, all with catchable curls (ceiling +60.7%, real TBD).
- **Likely relationship:** both may weed/rescue overlapping trades (against-grain entries that also strand) —
  worth measuring the intersection before stacking them.

**Open, to nail before/while building:**
1. Strand rescue: the s7r fence (20/80?), the exact "receding" test (Δ toward 50 over one s15a cycle?), the
   gate-as-data schema.
2. Build order: strand rescue vs bias filter first (or measure their overlap first).
3. Out-of-sample validation for both levers (2nd real-tick window).
