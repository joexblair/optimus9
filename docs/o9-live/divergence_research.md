# Divergence detection — methods survey (research, Joe 0711)

Research before building. Goal: detect price↔oscillator divergences to anchor peaks/troughs; benchmark
against `swing_detect`. **Causal / emerging-only** is the live constraint that rules methods in or out.

## 1. What a divergence is
A disagreement between price's swing structure and an oscillator's swing structure — momentum waning while
price extends (reversal), or momentum leading while price pauses (continuation).

## 2. The four canonical types
| type | price | oscillator | reads as |
|---|---|---|---|
| **regular bearish** | higher high | lower high | top → short |
| **regular bullish** | lower low | higher low | bottom → long |
| **hidden bearish** | lower high | higher high | continuation short (downtrend) |
| **hidden bullish** | higher low | lower low | continuation long (uptrend) |

Regular = reversal (the entry case here). Hidden = trend-continuation.

## 3. Every divergence detector is two independent choices

### Axis A — how to locate the EXTREMES (anchors)
1. **Price pivots, retrace-confirmed** — `find_pivots`/`swing_detect`: a high confirmed when price falls pct%
   off the running max. **NON-CAUSAL** at the pivot index (the extreme is only known after the retrace).
   The reference/"truth", illegal live.
2. **Oscillator reversal** — the oscillator turns (`_mage_rev` wob≥1 fires ±1 at the confirmation bar).
   **CAUSAL**. Anchors on momentum, not price. *(Joe's proposed anchor: `s4Mage` OOB + `s4r` reversal.)*
3. **Fractal / n-bar extreme** — a high above N bars each side. NON-CAUSAL unless the right side is 0.
4. **Rolling-window extreme** — trailing max/min. CAUSAL but noisy (re-extends constantly).
5. **Zigzag** — pivots + amplitude + time filter.
6. **OOB breach-return** — the oscillator crossing back inside from OOB as the anchor. CAUSAL, coarse.

### Axis B — how to COMPARE the two sequences at the anchors
1. **Peak-to-peak / trough-to-trough (classic)** — compare the two most recent same-type extremes:
   price HH & osc LH → bearish. Discrete, simple, anchor-sensitive.
2. **Slope / linear-regression** — fit a line to price and to the oscillator over the same window; divergence
   = opposite slope signs. Continuous, robust to exact anchor placement, CAUSAL over a trailing window.
3. **Trendline-break** — draw the oscillator's trendline through its last two extremes; confirm when price
   breaks its own trendline the opposite way.
4. **Rate-of-change ratio** — Δprice vs Δoscillator between anchors; the *magnitude* of disagreement.
5. **Rolling correlation** — price↔oscillator correlation over a window going negative.
6. **Signed-area / integral** — compare the area under price vs oscillator between anchors.

## 4. Which oscillator
- **RSI-family (the r-lines `s2r`/`s4r`/`s5r` — Stoch-RSI here).** Bounded [0,100] → OOB gating is natural.
- MACD / MACD-histogram (unbounded — best for slope divergence).
- Stochastic %K/%D · Momentum/ROC · CCI · MFI (volume-weighted).
- **TF of the oscillator is the noise dial:** a fast r (`s2r`) diverges often (noise); a slow r (`s4r`)
  diverges rarely (signal). Multi-r agreement (`s2r` AND `s4r`) is a noise filter (Joe's ask).

## 5. Gating / quality filters
- **OOB requirement** (`s4Mage` OOB) — only count extremes formed at a momentum extreme. Removes mid-range
  chop. *(Joe's gate.)*
- **Lookback bound** — only compare anchors within N bars/legs; a divergence across hours is stale.
- **Amplitude threshold** — price move ≥ X% between anchors, else it's noise.
- **Class A/B/C** (Bulkowski): A = clean HH+LH (strongest) · B = double-top price + lower osc · C = HH +
  double-top osc.
- **Multi-oscillator confluence** (`s2r` ∧ `s4r`) · **higher-TF bias alignment**.

## 6. Causality — the live constraint (what rules methods in/out)
- **Price pivots are NON-CAUSAL** (confirmed on retrace) — a look-ahead; legal only for the `swing_detect`
  benchmark, never live.
- **Oscillator-reversal anchors** (`s4r` `_mage_rev`, wob≥1) are **CAUSAL** — confirm after the turn. This is
  *why* Joe anchors on `s4r`, not price pivots.
- **Slope/regression over a trailing window** is CAUSAL.
- The trade-off: a causal anchor **lags** the true extreme — that lag is exactly the placement penalty the
  MAE/MFE-vs-`swing_detect` comparison will measure.

## 7. Joe's proposed method, placed in the taxonomy
- **Anchor:** oscillator-reversal, OOB-gated (A.2 + OOB filter) — CAUSAL.
- **Compare:** peak-to-peak classic (B.1) on `s4r` AND `s2r` — multi-oscillator.
- **Oscillator:** Stoch-RSI r-lines; slow (`s4`) anchor + fast (`s2`) confirm.
- **Benchmark:** `swing_detect` pivots (non-causal reference of the "true" turns).
- Build notes: `_mage_rev(s4r, wob)` fires ±1 at the turn bar (peak = down-turn −1, trough = up-turn +1);
  `s4Mage` is NOT in the DB → needs override `bb 37|0.72|ohlc4` @ itf 240s (spec Mage {2,3,4}).

## 8. The fork menu (what to A/B once the frame is picked)
- **anchor line:** `s4r` vs `s5r` vs `s3r`; wob 1 vs 2.
- **OOB gate:** side-matched (peak↔high-OOB) vs either-side vs no gate.
- **compare method:** classic peak-to-peak vs slope-regression (B.1 vs B.2).
- **oscillator agreement:** `s4r`-only vs `s4r`∧`s2r` vs `s4r`∨`s2r`.
- **type:** regular-only vs regular+hidden.
- **anchor-pair lookback bound** · **amplitude threshold**.

## 9. Existing system precedents — TWO divergence families already coexist (do not conflate)

### Family A — slope-sign divergence (±1), the PRODUCTION one (live-wired, CAUSAL)
The core of the whole PK / vote machine. **Never HH/LH** — it compares slopes:
- `price_slope = dema[i] − dema[i−center]` (DEMA lookback slope); `line_slope = line − rolling_peak`
  (osc minus its trailing max/min).
- **Divergence `±1`** = `sign(line_slope) ≠ sign(price_slope)` and `|Δ| > slope_floor`.
- **PM `±2`** = signs AGREE = "Price Match" = trend continuation (the *opposite* of divergence).
- Code: `pk_state_computer.compute` (:119-155) · `pk5s_gate_computer._pk_state_from_slopes` (:284-300) ·
  consumed by `pk_vote_machine.aggregate` (:151-186, PM suppresses the opposing vote 40%) ·
  `bias_machine.verdict_pk` (:551-560, anchored on osc-reversal events not a rolling window).
- Glossary (`r07_status.md`): `±1 = divergence (slopes disagree)`, `±2 = PM (slopes agree)`.

### Family B — peak-to-peak EPISODE divergence (true HH/LH), research-only (CAUSAL)
**This is your proposed method, and it already exists.** `divergence_exit.py` / `divergence_v2.py`:
- Anchor = an **OOB episode** (a maximal run of `r≥85` or `r≤15`). Price extreme = `px` at the osc-extreme
  bar (`argmax/argmin` of r over the run) — price sampled at the oscillator's extreme, not an independent
  pivot. Confirms **at episode END** (`sig[eb], eb=j−1`).
- Compare consecutive same-side episodes: `price HH & osc LH` (bearish) / `price LL & osc HH` (bullish) —
  the exact `(cmp_price, cmp_osc)` tuples. **Only regular divergence is coded; no hidden variant.**
- Multi-line confluence `K` over a trailing `WIN=60` (`s1r..s4r`). `divergence_v2.py` also A/Bs **m-lines as
  oscillators** vs r-lines, and curl-only vs div.
- **The one difference from your ask:** the existing anchor confirms at **episode end** (r leaves OOB); your
  anchor is the **s4r reversal while s4Mage OOB** — which fires *earlier* (at the turn, before r exits the
  band) = tighter, less-lagged placement. That's the novel refinement to A/B.

### The "s5r = divergence arm" is NEITHER of the above
`s5r_arm` (lr_v2:21-40) = s5r sitting OOB on the side *opposing* the breach (fence 70/30) when s4m breaches
the leg side → "Stoch-RSI veers off a leg as momentum slows." An OOB-opposing anchor, not a HH/LH or slope
comparison. Disambiguate.

### Causal turn primitives available (reuse, don't reinvent)
`_mage_rev(line, wob)` (±1 at the turn bar) · `_slope_flip` · `_curl_detect`/`coarse` · `bias_machine.trigs`
(3-point local extrema). Non-causal reference only via `jig.score.swings`=`find_pivots` + `lr_walk`
(entry_quality MAE/MFE to next favourable swing). `pivot_causal_lag.py` already quantifies the pivot→
confirmation lag (~pct%) — the placement penalty a causal anchor pays.

### Recommendation
Don't fork: **reuse `divergence_exit.py`'s episode engine**, add your `s4Mage-OOB + s4r-reversal` anchor as
an earlier-confirm variant, and A/B (i) anchor: reversal vs episode-end, (ii) compare: peak-to-peak vs the
production slope-sign ±1, (iii) osc agreement: `s4r`-only vs `s4r∧s2r`, all scored MAE/MFE against
`swing_detect`.

## 10. Empirical results (24h, MAE/MFE via `score.entry_quality` to next favourable swing)

Benchmark ceiling `swing_detect`: MAE 0.04 / MFE 1.81 / mfe_ok 91% (non-causal — enters AT the pivot).

**Finding 1 — coincidence needs a SHARED anchor.** Per-line oscillator anchors (each line's own OOB
episode / reversal) put s2r and s4r extremes at *different bars*, so "both diverge at once" almost never
co-occurs: episode-coincidence n=0 at every tolerance; reversal-coincidence fires but MFE<MAE. The classic
fix is one shared anchor read by both oscillators.

**Finding 2 — a causal shared anchor works.** `s{tf}Mage` reversal (`_mage_rev` wob1) as the shared anchor,
reading `s2r`+`s4r` at the turn vs the previous same-kind turn:
- **both-diverge > single > either** (MFE/MAE 1.9 vs 1.65 vs 1.42; mfe_ok 58% vs 51% vs 46%) — the confluence
  genuinely filters.
- **anchor TF is near-invariant** (s2..s7 Mage all ~1.82–1.93) — they reverse around the same price turns.

**Finding 3 — the OOB gate HURTS.** Requiring the anchor Mage OOB on the turn side (the original
`s4Mage OOB` spec) cuts MFE/MAE from ~1.9 to ~1.0 and drops n ~4×. Drop it.

**Finding 4 — the magnitude filter is the lever.** Requiring BOTH r to drop ≥ `mag` points between anchors
(a) strips r-**saturation flats** (r pinned at 85/15 reads as a false equal-high, which inflated n to 662),
and (b) lifts quality: `mag≥6` → **MFE/MAE 2.13–2.19, MAE 0.65–0.67, MFE 1.43–1.44, n≈31 (24h, ~1.3/hr),
mfe_ok 55%**. wob 0≡1 (slope-flip = 1-step); wob 2 worse; lookback-bound no effect.

**24h winner (causal):** `s4Mage`/`s3Mage` reversal (wob1) · both `s2r`+`s4r` drop ≥6 pts · **no OOB gate**.
Harness `scratchpad/div_lab*.py`.

## 11. 20-day OOS — the 24h oversold it (honest verdict)
| cfg | n/day | MAE | MFE | MFE/MAE | mfe_ok |
|---|---|---|---|---|---|
| swing_detect (non-causal ceiling) | 47 | 0.15 | 1.82 | 12.5 | **89%** |
| s4Mage-rev both mag≥6 | 29 | 0.72 | 1.18 | **1.64** | **48%** |
| s4Mage-rev both mag≥10 | 14 | 0.66 | 1.19 | 1.81 | 47% |

- **The Mage-reversal divergence is a WEAK causal ENTRY.** 20-day MFE/MAE 1.64 (24h showed 2.13 — a lucky
  window), and **mfe_ok ≈ 48% = a coin flip on which side of the next swing it enters**. Higher `mag` lifts
  the ratio but not the side-accuracy.
- **The concept is sound; the causal proxy is the weak link.** Non-causal `pivot-both` = mfe_ok **100%**, so
  both-diverge genuinely marks turns — but every CAUSAL anchor tried marks *the turn* only ~half the time
  (the reversal fires on mid-move wiggles too). The confirmed-pivot anchor can't rescue it: its entry lands
  ~`pct%` (≈0.9%) past the extreme, a worse MAE floor than the Mage-rev's 0.65%.
- **Reframe:** `divergence_exit.py` built this family as an **EXIT** (favorable-side divergence = the move
  exhausting → bank), not an entry. As a standalone reversal *entry*, coincident s2r+s4r divergence is a
  **modest confirmation/filter, not a primary trigger.** Its likely home is confirming/timing an arm or exit,
  not standing alone.

**Untested (deliberately parked):** the signal used as an EXIT (its original design).

## 12. Family-A vote-gate — the stronger framing (Joe 0711)

Joe's reframe: divergence belongs in **s3s4**, not as a standalone entry. Per emerging bar, gated on **any r
OOB**, each of `s2r/s3r/s4r/s5r` casts a **slope-sign divergence vote** (the production
`Pk5sGateComputer._pk_state_from_slopes`: `sign(line_slope) != sign(price_slope)`). **≥K votes = the LTF votes
create a reversal** → trade the **next s30a+s15a**.

**The finisher is the load-bearing piece.** `fin_gate` (forward-only) gives MAE ~0.8; the arm-delay's
**`fin_unlatch`** (7×30s box lookback + next s15a) collapses it — Joe's "minimal MAE" prediction:

| finisher | cfg | n (13h) | MAE | MFE | MFE/MAE | ok |
|---|---|---|---|---|---|---|
| fin_gate | r L12 K3 | 15 | 0.52 | 1.27 | 2.46 | 60% |
| **fin_unlatch** | r L12 K3 | 5 | **0.15** | 1.29 | **8.72** | 60% |

**20-day OOS** (the 13h MAE 0.15 was small-sample; OOS it's 0.75, but side-accuracy is the real win):

| cfg | n/day | MAE | MFE | MFE/MAE | mfe_ok |
|---|---|---|---|---|---|
| swing_detect (ceiling) | 47 | 0.15 | 1.82 | 12.49 | 89% |
| **r L12 K3 (3-of-4 vote)** | 4.1 | 0.75 | 1.53 | **2.04** | **65%** |
| r L12 K2 (2-of-4) | 25.4 | 0.84 | 1.31 | 1.56 | 53% |

- **mfe_ok 65%** — the first divergence variant with real side-accuracy (peak-to-peak sat at ~48%).
- **Selectivity is the lever again:** the strict 3-of-4 vote (4.1/day) beats the loose 2-of-4 (25/day) — same
  pattern as the arm-delay.
- **DEMA-smoothing the price slope DESTROYS it** (MAE 0.15 → 0.35–0.85). The raw price slope is correct.
- **Unreproduced:** Joe's `07-10 23:32` entry fires in NO config (there the r-lines *rise*, so no r-vote is
  possible; only the M-lines fall, and the M-family is weak everywhere). No mechanism found — left open.

## 13. TWO PATHS off an armed event (Joe 0711) — the payoff

Off the **T4 arm** (stack-climb 10→25, s10m kickoff), two independent gates, **no race — both trade**:
- **path A:** arm → divergence vote-gate → `fin_unlatch` → trade
- **path B:** arm → **s3s4 gate** (`gate_open`) → `fin_unlatch` → trade

20 days, causal, no caps, exit = real AD-TP:

| path | n | n/day | net/trade | total | MAE | MFE | win |
|---|---|---|---|---|---|---|---|
| s3s4 | 126 | 6.3 | +0.183 | +23.0 | 1.12 | 1.24 | 57% |
| divergence | 45 | 2.2 | +0.155 | +7.0 | 1.22 | 1.12 | 53% |
| **union (both trade)** | **170** | **8.5** | **+0.174** | **+29.5** | 1.15 | 1.21 | 56% |
| union (race — whichever first) | 151 | 7.5 | +0.149 | +22.6 | | | |

- **Both paths are independently net-positive**, and letting both fire is **additive: +29.5% / 20 days**.
  Racing them dilutes (+22.6) — the race swaps good s3s4 trades for earlier div ones.
- Beats the T4 arm book alone on total (+26.9% at 125 trades) by trading more at slightly lower per-trade
  quality.

**Open:** big combo sweep of the s2r/s3r/s4r line configs (5 sources × k_len × rsi) × vote knobs (L/K/floor).
`s5r` held at DB default — it is shared with the TP exit ladder, so sweeping it would move the exit and
confound the measurement; it needs its own pass.
