# SnF research log — can line *relationships* improve the s3m signal?

**Status:** Phase 1 complete (overnight, 0624). Verdict reached: **no robust line-relationship
edge found.** The individual lines pay (+2.0–2.5 EV each); their *combinations* do not add
out-of-sample value. Full trail below so the result is reproducible and the dead branches stay dead.

## The question
The 6-line `snf_compare` showed each line is individually profitable but they barely co-fire. Joe's
thread: is there a *relationship* — voting, sequencing, confluence — that lifts the s3m signal (the
high-volume minor) above its solo +2.4 EV? Target metric throughout: **total pnl** (placement MFE).
Rigor throughout: **walk-forward** (train windows 1–5, test 6–9); never trust in-sample sparkle.

## What was tested, and what each said
1. **Simultaneous voting (support/friction).** `snf_rows`. Support is **flat across pnl tails**
   (high 1.04 / mid 1.15 / low 1.08) — agreement does not discriminate winners from losers. Dead.
2. **2-support coalition.** A genuine sweet spot — exactly 2 lines agreeing → **54% hit** (vs 34%
   solo), inverted-U (3+ degrades = redundancy ceiling). But the *extreme* winners aren't
   coalition-driven, and it doesn't lift total pnl. A quality lens, not an edge.
3. **Sequencing `s3m → s12maj`.** Fast primes slow-Major: primed s12maj +3.69 vs +1.78 un-primed.
   Real, but it's a **sizing/confidence signal, not a gate** — gating to it *cuts* total pnl
   (fewer trades). And the "bleed" was the *opposite* of intuition: s3m-alone is fine (+2.43);
   only s3m fires that *precede* an s12 peak underperform (+0.55), and those are unflaggable live.
4. **Line-positioning confluence (the deep search).** 37 candidate lines (m/M/r, TF≥3).
   - **Singles:** no robust validator. s22r looked spectacular IS (+5.39) → collapsed OOS (+0.54).
   - **Groups (3–4 line, W-swept 24→180 min, ~66k combos):** *every* top-IS group, at *every*
     lookback, flips **negative OOS**. Textbook overfit demonstrated at scale (45k groups → the
     in-sample winner is pure multiple-testing lottery).
   - **Capstone — IS↔OOS lift correlation = +0.26, 91% sign-keep.** Looked like a *negative*
     (avoid/continuation) signal. On scrutiny it **dissolved**: weak (+0.35 MFE), and it *reverses
     by metric* (confluence-present flips have lower MFE but higher hit-rate). A metric artifact.

## Verdict
The relationship-hunting is **exhausted**: voting, sequencing, and confluence each fail to add a
robust, tradeable, total-pnl edge to s3m out-of-sample. **The edge is the individual lines.** Any
combination strategy should expect to *inherit* their EV, not amplify it.

## Why this is trustworthy (not just "we didn't find it")
Walk-forward caught every overfit before it could fool us (len=40 earlier, s22r, the 66k groups).
The IS↔OOS correlation capstone is the load-bearing test — it prevented a premature negative *and*
a false positive. The negative is **measured**, not assumed.

## Artifacts (reusable)
- `snf_compare.py` / table — 6 osc lines, bias-pk outcomes, current window + `grind` (9 windows).
- `snf_rows` (DB) — per-row 6-line states + pnl across 9 windows; substrate for any re-cut.
- `snf_conf_bars` (DB) — per s3m-flip, each of 36 lines' bars-since-OOB-same-side; the confluence
  dataset (sweep any W / group size in seconds, no rebuild).
- engine seams added for this: `BiasConfig.trigger_src/trigger_len/trigger_mult/osc_from_trigger`,
  `_entry.s3_lookback`, `placements` returns `mae`. blp6m/M/r = ic_pk 68/69/70.

## Realized-metric addendum (0625) — the big reframe
Re-ran on a **realized** metric (win = hit +0.9, else the trade's value is its *natural* stop, no
forced −0.4) — Joe's "let the stop be the decider." It changes everything, and *down* to honest size:
- **MFE overstated ~10×.** Realized EV is ~**+0.1 to +0.2 / trade**, not the +2.4 the MFE metric showed.
- **Stop-sweep (9 windows, 269 trades):** realized EV is *positive at every stop* and **rises with a
  WIDER stop** (−0.30→+0.09 … −2.0→+0.21, win 33%→76%). The extra wins a loose stop captures outweigh
  the fatter losers — but it's a **high-win / fat-tail** profile (24% lose −2.0). Risk-adjusted may
  favour tighter; that's the open question, not raw EV.
- ⚠ **Process catch:** I first over-swung off a single-window outlier ("the stop is the edge,
  s3m is break-even") + a miscalculated −0.4 EV. The proper 9-window sweep corrected me. Rail working.
- **Win-MAE split:** ~**90% of s3m wins are DEEP** (dived past −0.5 before paying). NO LP group
  produces consistently clean (<0.5 MAE) wins — clean wins (~10%) are too rare to be group-selectable.
- **s6m ≈ s3m** (93% deep, EV +0.166): two different oscs, identical deep-drawdown fate ⇒ **the
  drawdown lives in the s3-gate→s30-wob CASCADE (the entry), not the bias osc.** *The entry is the lever.*
- Artifacts: `pine_wins_emit.py` (re-framed wins, green=clean/red=deep, param s3m|s6m), the realized
  stop-sweep. The s3m signal is *modestly* profitable; improving it = entry/exit work, not signal-combos.

## Methodology catch + the right metric (0624) — load-bearing
- **`s18M+blp6m` is the lowest-avg-MAE confluence** among 0.9-MFE wins (IS |MAE| 1.08 vs 1.53 baseline;
  OOS 1.42 vs 1.63 — attenuates but doesn't reverse). **Joe confirms it as a known-good confluence
  from domain knowledge** → it's real, not fishing.
- **Why it only surfaced on the Nth cut:** every prior ranking used the WRONG metric (MFE-lift,
  realized-EV, clean-fraction≥70%) — none scores `s18M+blp6m`. **The right lens is avg-win-MAE
  (drawdown-cleanliness), not MFE or EV.** A confluence's value is "supports the bias update = win with
  a shallow MAE," i.e. tradeable on a tight stop.
- **What MAE actually measures (Joe, 0624) — the mechanism:** a deep win-MAE = **bls flipped to
  state 3 *before* price reached the swing** (premature entry); price runs adverse to the swing, then
  pays. The stop depth is the market saying "get closer to the swing." So **avg-win-MAE = a
  swing-proximity / bls→3-earliness measure**, and the low-MAE confluences (`s18M+blp6m`) mark
  swing-proximity → they're candidate **entry-timing gates** that would hold bls→3 until near the swing.
  This sharpens "drawdown is in the cascade" to "drawdown = premature bls→3." ⚠ Before proposing gate
  mechanics: READ the bls state-3 trip condition, don't infer it.
- ⚠ **Sampling-bias catch (Joe's probe):** we ran ~8 cuts over thousands of groups, all checking the
  SAME windows 5–8 as "OOS" → metric-shopping + a contaminated hold-out. Selecting the group that looks
  best on a reused OOS *is* slow-motion fitting. The discharge here was Joe's independent knowledge, not
  the stats. **Fix = ONE comprehensive, stored, long-running confluence dataset** (rank every confluence
  by avg-win-MAE once, indisputable) instead of ad-hoc re-cuts. That dataset is the next defined work.

## Open threads (NOT closed by this)
- **Entry/exit is the live frontier** (per the addendum) — the deep-drawdown is a cascade property;
  #36 (TF-scaled exit) is promoted from next-week to relevant.
- The **flip-count / continuation pattern** — never backtested; pin resolved (discrete entry = the
  existing line-positioning cascade), still needs the "what reset does" pin before building.
- **Risk-adjusted stop** — raw EV says wider; Sharpe-like may say tighter. Untested.

See [[project_snf]].
