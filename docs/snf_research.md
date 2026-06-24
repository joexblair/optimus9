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

## Open threads (NOT closed by this)
- The **flip-count / continuation pattern** (treat early s3 shorts as long-resets until the Nth) —
  never backtested; it needs Joe's two pins (what "reset" does · always-in vs discrete entry).
- **Metric question:** every test used MFE (potential). A *realized* (target/stop) metric might
  rank things differently — the confluence's higher-hit/lower-MFE split hints at it. Worth a look.
- **Trade-exit #36** (exit-line TF scales with pk-source TF) — independent, still live.

See [[project_snf]].
