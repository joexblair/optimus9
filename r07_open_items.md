# r07 — Open Items (parked from r06)

This is a working scratch doc. Items get folded into a proper change doc
when r07 closes. Add freely as discoveries happen.

---

## Carryover from r06 backlog

### Architectural
- **Consolidate `_persist_self_gated` and `_persist_gated`**: 90% duplicated.
  Single shared method with row-builder callback would eliminate the
  duplication that caused the MAE-miss bug to slip through (twice — once
  on first commit, once on VS Code revert).

- **ParameterGridBuilder yield-per-combo**: currently materializes full
  combo list in memory. For 32K+ grinds the overhead is real (filed as
  contributing to last night's OOM).

- **Sortino fix**: 1e-10 denominator threshold to prevent the
  `Sortino=7987390474373178` blow-up when very few losing trades.

- **DD model under HTF-gated execution**: AM v2's `_walk_equity`
  sequentially compounds; over-penalizes high-frequency combos that
  may be excellent HTF confirmation sources. Filed for redesign.

- **Two-stage vote evaluation** (curiosity-first stash, 2026-05-29):
  separate "loudness" (stage 1, denominator includes control) from
  "dominance" (stage 2, directional split only). Two thresholds.

  **Curiosity-first notes** (stashed for post-sweep A/B vs single-threshold):
  - **Problem this might solve**: the current model bundles two questions
    into one ratio — "is anything loud enough to consider?" and "which side
    dominates?" A thin bar with one-sided participation can produce a ratio
    above threshold even when the total evidence is sparse. Two-stage gates
    firing on BOTH "loud enough" (stage 1) AND "dominant enough" (stage 2).
  - **Stage 1 (loudness)**: total directional engagement vs total bar weight.
    Threshold: did sufficient evidence accumulate to even consider a signal?
    Denominator includes neutral + control (abstention drag).
  - **Stage 2 (dominance)**: among directional votes, how clear is the winner?
    Denominator excludes neutral. Threshold: directional split clear?
  - **Hypothesis**: fewer thin-bar fires (stage 1 catches them) AND fewer
    near-tie fires (stage 2 catches them) → cleaner signal clusters → better
    cluster_quality_score per the r08 KPI direction (cross-link: see the
    cluster_quality_score finding below).
  - **A/B test plan**: same grind combo set, single-threshold (current) vs
    two-stage. Compare signal count, win rate, cluster_quality_score. Run
    *after* the pm_additive sweep so we're A/B'ing on a known centroid.
  - **Stash status**: not blocking the current pm_additive sweep. r08 or
    very-late-r07, alongside cluster_quality_score scoring implementation.

- **AM v2 Stage 1 memory**: GROUP BY across all signals accumulates
  everything in MySQL memory + Python list. Streaming/chunking for
  grinds > 10K combos. Root cause of repeated post-grind OOM kills.

- **Archive util to slower SSD**: After each grind completes and analyze
  runs, mysqldump pk_signals + pk_outcomes for that or_pk to compressed
  CSV on `/mnt/archive/optimus9/`, then DELETE from MySQL. Keep
  `analysis_or<N>.csv` online.

- **Pk5sGateComputer dormancy annotation** (r07 close / Step 5 prep):
  When Step 4 ships and PKVoteMachine is the canonical home for
  vote-folding math, Pk5sGateComputer transitions from "library code
  with no current consumer" to "dormant historical class." Annotate
  with the project's established `DORMANT [GATE-STUB]` pattern (see
  Pine's gca5m/gcs5m comment as the model). Class stays in tree with
  a rationale-bearing docstring; future-Claude can read the dormancy
  note and understand "this was the multi-line-vote-as-gate pattern
  superseded by SnF's multi-line-vote-as-signal." Don't delete; annotate.

  Suggested docstring shape:
  ```python
  class Pk5sGateComputer:
      """
      DORMANT [r07]: 5s multi-line vote-as-gate pattern.

      Earlier design folded multi-line vote machine output into oob_side
      as a third gate alongside bny30M/p. Superseded by SnF (r08), which
      treats multi-line voting as the signal itself, not a gate. Vote-
      folding math extracted to PKVoteMachine (r07 Step 2); this class
      retained as a thin composer/reference until SnF lands. Safe to
      delete after SnF validates.
      """
  ```

  Pattern is consistent with the gca5m → mnm15 → bny30 gate evolution
  preserved in Pine: deprecated logic gets commented-with-rationale,
  not deleted. Future-readers can reason about why current code looks
  the way it does by reading the dormancy notes.

- **Logger rotation** (filed 2026-05-29): `logger.py` currently uses
  `logging.FileHandler` with unbounded growth. Three-line swap to
  `RotatingFileHandler(maxBytes=10*1024*1024, backupCount=5)` prevents
  disk fill on long sessions. Surfaced when stale supervisor handles
  confused the filesystem mid-run after `rm logs/*` — separate issue,
  same module. Small enough that CC can land it as a standalone commit
  if convenient; not blocking anything.

- **Lookback window sensitivity** (filed 2026-05-29): or47 (May 24-25)
  produced 54,983 signals; or48 (May 28-29, same tc_pk, same grid)
  produced 82,658 — 50% lift purely from market regime variance over
  a different 24h window. TV's independent backtest showed a similar
  40% lift over the same windows, confirming it's market reality not
  code drift. Implication: single-day grinds are regime-sensitive.
  Production grinds should default to longer lookback (3-7 days) or
  the analyze stage should average across multiple grinds to smooth
  out single-window noise. Real conversation when we get to production
  engine config defaults (r08).

### Pine
- **OOB gate emulation tuning as PRECURSOR**: dial in bny30M/p gates
  FIRST so the raw 5s data going into line-pattern recognition is
  sanitized. New tc_pk for gate tuning. Sweep bny30M/p indicator params,
  quality metric = regime separation. Then gca5m grinds run against
  validated gates.

- **dotenv migration**: existing scripts (`validate_centroid.py`)
  still use hardcoded-fallback env-var pattern. Migrate to
  `optimus9.config`.

- **Symmetric "Gated mode" log line in `_run_gated`** (DONE in r06)

### Hybrid pilot → Full Python (decision 2026-05-26)
**Path change**: hybrid Pine-alerts-to-Python-orders dropped. Full Python
is the production target. These items previously framed as "hybrid pilot
work" are now framed as **production engine work for r08+**:

- **DEMA cycle measurement util** (r08) — replaces hardcoded 0.4% SL with
  dynamic SL derived from local volatility/cycle.

- **FIB validation Phase 1 + 2** (r08).

- **HTF anchor quality ranking metric** (r07): `gross_banked` may not be
  the right ranking for "5s signals that HTFs can p-rev on." Possibly
  banked × signal_count_floor, or coverage × win_rate, or something
  TBD. Real question worth answering after PM additive grind.

- **PM tolerance separate from slope_floor** (r07): currently slope_floor
  acts as both "is this slope significant" and "PM match tightness."
  Conceptually different — split into two params, file as grind dim.

### Naming
- **`Pk5sGateComputer`**: doesn't actually compute a "gate" in the
  bny30 sense — it produces s5_pk_final transitions. Historical name.
  Rename when refactoring its internals.

- **"pool" terminology**: holdover from ancestor where multiple lines
  were dialed as a group. Now a "pool" = collection of settings
  (p_c, p_w, p_r, suppression, slope, multiplier, weight_close,
  weight_wide) that apply to ONE line. Drop or rename in r07/r08.

---

## New (r07 discoveries this session)

### Captured raw idea: pairwise/coalition voting model (2026-05-26, EOD drop)

**Status**: raw idea dropped by Joe at end-of-session. Captured verbatim
plus light Claude annotation. NOT to be analyzed or implemented until
the next session — Joe was signing off and this is "don't lose this
thought" preservation.

**Joe's pseudocode (verbatim)**:

```
can we make the voting system work like this (per probe):
create_pk = false
method votematching
    if both propose the same direction
        signal is made
        return (true, dir)
    else if the proposals are not aligned
        if the weights match
            return (false, null)
        if weighting calculation tiebreaker()
            return (true, more_'normalised-weighted'_line_ddir)

method weighting_calculation_tiebreaker()
    eg line 1 brought 8 to the fight, 2 line's weight is 5

    multiline_weigthing_mult = 1.5
    #multiline_weigthing_mult is used to bolster 2 or more lines that
     not beat a higher weighted line through sheer addtion. adding a
     weight to 2 or more lines agreeeing in direction gives them the
     potential advange they deserve for doubling down on their bet
    #usage: multiply the all line weights of an algined ground, then
     add them together.  if their combined enhanced weight > the other
     line (or, in fact, other multiple lines), then they win

    the goal is these scenario outcomes  NEEDS MORE PADDING,
    WEIGHT HAS TO BE INCLUDED FOR THE collaboration decisions
        {line1:8, line2:5}
        line 1 wins

        {line1:10, line2:5, line3:5}
        line 1 and 2 win if both agree
        line 2 and 3 win, if both agree
        line 1 and 3 win, if both agree

        {line1:14, line2:5, line3:5}   (14 < (5*1.5) +(5*1.5))
        line 1 and 2 win if both agree
        line 2 and 3 win, if both agree
        line 1 and 3 win, if both agree

        {line1:16, line2:5, line3:5}
        line 1 and 2 win if both agree
        line 2 and 3 lose, if both agree
        line 1 and 3 win, if both agree
```

**Claude's first-pass read** (for next-session pickup, not committing
to interpretation):

This isn't a tweak to PKVoteMachine — it's a fundamentally different
voting model. The current vote machine sums weighted contributions
into long_pts/short_pts/neutral_pts buckets, computes ratios against
active_w, and fires above threshold. **Joe's model is pairwise/coalition
resolution**: lines either agree (immediate signal) or disagree (tiebreaker
by enhanced weight). No bucket arithmetic, no thresholds, no ratios.

Key elements I'm seeing:
- **Agreement-first**: any two lines agreeing in direction = signal,
  regardless of weights. The "create_pk = false" line plus the agreement
  return suggests agreement IS the firing condition, not threshold-crossing.
- **multiline_weighting_mult (1.5)**: a coalition bonus. Two agreeing
  lines at weight=5 each become "effective" 5×1.5 + 5×1.5 = 15, which
  can beat a single line at weight=14. This is the "doubling down"
  bonus — agreement deserves more than just additive weight.
- **Scenario walking**: the {16, 5, 5} case shows the threshold —
  lines 2+3 at 5×1.5+5×1.5=15 lose to line 1 at 16. So coalition
  bonus has its limits.
- **"NEEDS MORE PADDING"**: Joe explicitly flagged this as not yet
  fully specified. The scenarios suggest the intent; the exact math
  is TBD.

**Open questions for next-session discussion**:
1. How does this interact with probe-level (close/wide) accumulation?
   Joe wrote "per probe" — meaning each probe has its own line vote?
   Or each line has its own probe vote?
2. What happens with 3+ lines all proposing different directions?
   The pseudocode handles agreement and pairwise disagreement;
   three-way splits aren't shown.
3. How do PM sentinels (state ±2) fit into agreement detection?
   PM_LONG and divergence +1 — same direction or different "votes"?
4. Does this replace PKVoteMachine entirely, or layer on top of it?
   (i.e., aggregate pool states with current machine, then pairwise
   resolve aggregate directions vs raw pool directions?)
5. The "(false, null)" return when weights match exactly — is that
   the intended outcome, or is there a fallback we haven't covered?

**Where this likely lives**:
- r08 work, alongside SnF multi-line architecture
- May supersede PKVoteMachine OR may compose with it (PKVoteMachine
  produces directional proposals, this new layer resolves them)
- The cluster_quality_score KPI (filed above) probably matters here —
  if cluster quality is the goal, agreement-based voting might produce
  cleaner clusters than threshold-based voting

**Not implementing tonight. Discussing next session when fresh.** Step
2 wiring (still queued) is unaffected — extracting PKVoteMachine as
designed is still the right move because:
- It cleans up Pk5sGateComputer regardless of which voting model wins
- A future PKMatchVoteMachine (or whatever we call this) is its own
  class with its own SRP boundary
- Both models can coexist while we test which produces better cluster
  quality

---

### Architectural finding: cluster_quality_score is the actual grind KPI (2026-05-26)

**What surfaced**: as we worked through why DD at the signal-grind
layer is a category error (see below), Joe articulated the actual
goal of the grind:

> "we look for signals around the swings, the more concentrated and
> closer to the swing, the higher the score. there's other metrics
> involved: testing clusters at a minimum distance (in pct) between
> swings, etc, etc"

This is a fundamentally different ranking metric from anything currently
measured. The grind has been ranking combos by gross_banked (which
assumes every signal is an independent trade) and constraining by DD
(category error). **The real KPI is the spatial/temporal quality of
signal clusters relative to local price swings.**

**Conceptual components**:
1. **Cluster concentration**: how tightly do signals bunch in time?
   8 arrows in 60s at a top scores higher than 8 arrows over 600s.
2. **Swing proximity**: how close is the cluster centroid to the
   actual local extreme? Arrows AT the swing peak > arrows 5 bars
   before > arrows 10 bars after.
3. **Swing significance filter**: only count swings above a minimum
   pct distance — 0.05% moves aren't tradeable, 0.4% moves are. The
   threshold is configurable; the metric only credits clusters near
   meaningful swings.
4. **Other metrics (Joe TBD)**: "etc, etc" — more dimensions to be
   articulated as the KPI matures.

**Why this is r08-bigger-than-r07**:
- A new analysis pass is needed (swing detection on kline data, then
  cluster-quality scoring per combo's signals).
- The grind itself doesn't change — still produces signals. What
  changes is what AnalyzeManager does with them.
- Multiple swing-detection algorithms (ZigZag, ATR-based, fractal,
  Fibonacci pivot) will produce different rankings. Algorithm choice
  becomes a real design decision.
- Validation gets harder — "did this combo produce good swing
  clusters?" requires defining "swing" precisely first.

**What this changes about the project's direction**:
- BL machine + HTF p-rev get clearer purpose: they're the entry-
  selection layer that picks precise entries from within a high-
  quality swarm. Grind produces swarms; filters pick entries.
- PROVEN replacement isn't about a single new combo — it's about a
  new ranking framework that surfaces a new combo.
- gross_banked stays as a tracked metric but loses primacy.

**Filed for r08 design session**:
- Swing-detection algorithm decision (ZigZag vs ATR vs fractal vs other)
- Cluster quality metric formula (how do "concentration" and "proximity"
  combine into one score?)
- Minimum swing pct configurability and default
- Whether cluster scoring happens during grind (per-combo) or
  post-grind (analyze stage)
- How cluster_quality_score interacts with existing metrics in the
  analysis CSV output

**Status**: insight captured, not yet implemented. The r07 vote machine
extract is unaffected — it's upstream of analysis. Step 2-4 proceed
as planned. r08 takes on the new KPI work.

---

### Architectural finding: DD at signal-grind layer is a category error (2026-05-26)

**What surfaced**: Joe's r06 dial-in CSV (27 combos) paired with TV
strategy results revealed a bimodal split:
- Low-DD cluster (DD 12-15%): ~600-700 Python signals, slope_floor=41
- High-DD cluster (DD 41-60%): 2,600-3,600 Python signals, slope_floor=13-21

The visual on TradingView (chart screenshot, this session) showed
high-signal-count combos producing **dense clusters of arrows AT
profitable price zones** — tops have short clusters, bottoms have
long clusters. The clusters give downstream filters (BL machine +
HTF p-rev) enough material to pick the optimal entry within each
swarm.

**The model**: signal density is the upstream goal. The grind produces
dense, well-placed signal arrows. BL machine + HTF p-rev filter the
swarm down to the precise entries to trade. **Realized DD is determined
at the filter/execution layer, not the signal-grind layer.**

**The error**: treating max_dd_pct from the grind as a quality metric
for signal combos. The grind's DD calculation assumes every signal is
an independent trade taken sequentially with full position size. Real
execution (TV strategy logic, future Python bot) absorbs many signals
into a single position — Python's 2,671 signals become TV's ~700 trades
on the same combo. The 4x signal density gives the filters more options;
it does NOT mean 4x the actual position-level losses.

**TV profit / PF caveat**: TV's PF column shows mostly <1.0 not because
the strategy is broken, but because the test environment uses near-
symmetric SL/TP. PF below 1.0 is mechanical from the test setup, not
a strategy-quality signal.

**Implications**:
1. **`dd_kill_switch=0.15` in AnalyzeManager is a category error**, not
   just a tunable threshold. It throws away combos where the real
   action is. Remove it from signal-grind analysis. DD belongs at the
   execution layer (position sizing, risk management in r08 production
   engine).
2. **PROVEN as a benchmark for grind output is obsolete.** It was the
   best combo under DD-constrained grind ranking — i.e., the best of
   a wrongly-filtered set. Need a new pointer to "best signal combo
   so far" with a ranking metric that captures density × quality at
   meaningful zones.
3. **Step 3 validation reference**: high-signal-count combo (e.g.
   len=6, pool_c=5, pool_w=23, pr=8, sf=21, src=close — 2,671 Py
   signals, 39% win) is a much better reference than PROVEN.
4. **The new mental model for signal combos**: maximize density at
   right zones; filter quality at execution.

**Filed for r07**:
- Remove `dd_kill_switch` binary filter from AnalyzeManager. Rank-only
  (or drop the metric entirely from the post-grind report).

**Filed for r08**:
- Composite ranking metric design. "Density × quality at meaningful
  zones" needs a quantifiable proxy. Candidates: gross_banked alone
  (current), win_pct × n_signals, win_pct × cluster_concentration_metric.
  Real conversation when we get there.
- New "best combo" tracking convention. Either rename PROVEN to
  PROVEN-r04 (its original era), or redefine PROVEN as "best-known
  signal combo of the current milestone."
- Production engine risk management at execution layer (position
  sizing, max concurrent exposure, account-level kill switches).
  This is where DD actually lives.

---

### Architectural finding: DD ceiling at 15% hides the real signals (2026-05-26) [SUPERSEDED]

*Earlier framing of the above finding. Preserved here briefly to make
the correction visible: the initial filing characterized high-DD combos
as "good combos we should trade directly." The corrected reading
(above) is that DD at the signal-grind layer is the wrong axis — the
grind measures signal density, execution layer handles DD.*

---

### Cleanup: `align_to_base` should always produce base-length output

**Where**: `optimus9/orchestration/optimizer_runner.py` line ~332 in `_build_line`.

**Current behavior**: when `ind_seconds == 5`, `_build_line` returns `line_raw`
directly without calling `align_to_base`. This produces a `line` array that's
shorter than `base_df` whenever `IndicatorComputer.resample` dropped bars
due to NaN opens (gaps in kline_collection). On 16,574-bar base data, gaps
are typically ~0.1-0.5% of bars (a few dozen).

**Original PKDetector behavior**: the per-bar loop `for i in range(upper + 1,
len(line))` only iterated over the line length, so dema was implicitly
truncated by index access. Worked silently.

**Vectorized PKStateComputer behavior (r07)**: explicitly truncates both
line and dema to `min(len(line), len(dema))` in compute() and detect().
Same end result, but the truncation is now in the wrong place — it should
happen once, upstream, in `_build_line`.

**Cleanup**:
1. Modify `_build_line` to always call `align_to_base`, even for `ind_seconds == 5`.
2. Drop the explicit truncation from `PKStateComputer.compute()` and `PKSignalDetector.detect()`.
3. Re-validate that signal counts match the pre-cleanup grind.

**Why now (r07)**: the vectorization made the length mismatch surface as a
broadcast error, which is healthier than the loop's silent tolerance. But
the truncation lives in the wrong class — it should be the caller's
responsibility to deliver aligned arrays, not each detector's job to handle
misalignment.

---

### Note: `dema[i - center]` wraparound (latent — would fire if loop bounds changed)

**Where**: `PKStateComputer.compute()` (and historical `PKDetector.detect()`),
in the per-bar slope calculation.

**Behavior**:
```python
for i in range(upper, n):
    if np.isnan(line[i]) or np.isnan(dema[i]) or np.isnan(dema[i - center]):
        continue
    ...
    price_slope = float(dema[i] - dema[i - center])
```

When `i < center`, `i - center` is negative. Python list/numpy negative
indexing wraps to the end of the array. So `dema[i - center]` for early
bars reads from the TAIL of the data instead of being NaN.

The `np.isnan(dema[i - center])` check usually passes (tail values are
real), so the loop proceeds and computes a meaningless price_slope
mixing the start and end of the dataset.

**Impact**:
- The Python loop iterates `for i in range(upper + 1, len(line))`, which
  starts at `i = upper + 1`. Since `upper = (bars + half) * multiplier`
  and `center = bars * multiplier`, the smallest `i - center` is
  `half * multiplier + 1` — always positive when `pool_range > 0`.
- So the wraparound **never actually fires in the original loop**. The
  bug is latent — `dema[i - center]` is always a valid forward index.
- The vectorized rewrite must preserve this by masking the first `upper`
  bars as NaN (same effective skip as `range(upper + 1, n)`), not by
  trusting `np.roll` alone.

**r07 vectorization parity decision** (Phase A, this session):
The vectorized PKStateComputer.compute() will preserve the loop's
effective behavior by:
1. Computing `np.roll(dema, center)` to get the shifted dema (wraparound
   wraparound is harmless because step 2 masks the affected bars).
2. Explicitly masking the first `upper` bars as NaN in the output, so
   the early bars where wraparound could have leaked are guaranteed not
   to produce signals — same as the loop's `range(upper + 1, n)` skip.

**Why preserve**: the immediate goal is exact signal-count + signal-set
parity with the Python-loop version (or_pk=44 reference). Fixing
anything in this layer AND vectorizing in one change would obscure
which contributed to any observed delta. Validation needs one variable
at a time.

**Followup (file as r07 item, post-vectorization)**:
The latent wraparound risk goes away if we ever lower the `range`
lower bound (e.g. for warmup-tolerant variants). Document explicitly
in the vectorized code why the first `upper` bars are NaN-masked,
so future-Claude doesn't "optimize" the mask away.

**Action**: do NOT clean up `np.roll(dema, center)` without re-validating.
The wraparound is intentional during r07's vectorization milestone.
Once the milestone closes, fix the bug as a separate tracked change.

---

### r08 SnF spec stub — architecture landed 2026-05-30

Architecture consensus from the 2026-05-30 design session (bounce-land-lock arc):

**Per-line library + temporal-coalition SnF + cluster overlay.** Per-line grinds
produce reusable per-line signal libraries; SnF simulator forms coalitions by
**temporal proximity of signal firings** (not by per-bar state-stream agreement);
cluster overlay scores emitted coalition streams against detected swings.

**The flow:**
```
[1] Per-line multi-D grind (intrinsic only — no PM dials)
      sweep:  len, mult, src, pool_c, pool_w, pool_range, sf, weights
      rank:   cluster_quality_score
      output: per-line library (top-N intrinsic centroids per line)
[2] SnF task picks N candidate lines from libraries
[3] SnF simulator (Python loop over pk_signals queries):
      for each (collection, x, pma, pms, multiline_weighting_mult):
        pull signals from each line in collection
        temporal-cluster by window = x bars
        coalition arithmetic (Support vs Friction, with bonus)
        score emitted stream via cluster overlay against significant swings
[4] Best (collection, x, pma, pms) → production candidate
```

**Key dials at the SnF layer:**
- **x (temporal window)** — bars within which signals form a coalition. *TF-dependent*: per-TF dial; HTF lines need different x than 5s lines because of their natural noise filtering.
- **pma / pms** — collection-level (PKVoteMachine treats them as single values across all probes). Per-line PM dials = (C) option from the 2026-05-30 design conversation, prohibitive without Bayesian opt.
- **multiline_weighting_mult** — Joe's coalition bonus per the original r07_open_items "pairwise voting" filing (above).

**SnFv2 enhancement: top-5 centroid combinatorial sweep.**
Each line offers its top-5 intrinsic centroids to the SnF simulator (not just its top-1). SnF sweeps the cross-product of collection compositions:
- N lines × 5 candidates each = 5^N compositions (N=4 → 625; N=6 → 15,625).
- Captures cross-line tuning where line A-at-centroid-3 + line B-at-centroid-1 outperforms everyone-at-top-1.

**Friction formula A/B (concrete plan, filed 2026-05-30):**
- **v1: friction = opposing signals only.** Lines that fire in the opposite direction within x bars; non-firing lines abstain entirely.
- **v2: friction = opposing signals + non-firing-line tax.** Adds a penalty for lines in the collection that are NOT firing in the cluster window (encodes "thin clusters are worse"). Requires per-bar state lookups at cluster-window moments.
- **Test plan**: implement v1, dial against grind data. If thin clusters score too highly (overrank vs visual assessment), add v2 as a switchable mode. A/B same SnF candidates under each, compare cluster_quality_score distributions.

**Swing-detection calibration:**
- **At 5s**: swing significance threshold is dialed empirically against "optimal clustering opportunities." NOT a fixed pct.
- **At HTF (TF4 and up)**: 0.9% becomes meaningful naturally because HTF inherently filters 5s noise. 0.9% maps to the trade-exit/reverse threshold from scalping discipline.
- **Auto-derive x per-asset**: Joe's idea — derive the natural temporal window for a 0.9% move per asset from historical kline data. Filed for **post-HTF inclusion** (probably r22-ish, far future). Meaningful deltas in a daily report.

**Multi-algo swing detection (3 algos in overlay):**
ZigZag + ATR pivot + fractal. Each parameterised on the same significance threshold (0.9% at HTF, dialed empirically at 5s). A combo that clusters well under ALL three is genuinely robust; one that scores under only one is suspect. Overlay reports per-algo + meta-score.

**State-stream lookup NOT needed for v1.** Per-line signals (`pk_signals` rows) are sufficient for temporal-coalition voting. State arrays would only be needed if v2 friction (non-firing-line tax) requires checking each non-firing line's state at cluster moments — and even then, only at signal-bar moments, not every bar.

### Background or_pk cleanup service via watched text file (filed 2026-05-30)

When an or_pk is dropped (e.g. `delete_test_config(N, 'force')`), the
FK cascade from `pk_signals` to `optimizer_runs` can exhaust MySQL's
lock table on big grinds — failed dropping tc_g2=104 with 76.5M signal
rows attached to or_pk=54 with `1206 (HY000): The total number of locks
exceeds the lock table size`.

**Idea (Joe, 2026-05-30)**: a small background service that watches a
plain text file (e.g. `~/thecodes/cleanup_orpks.txt`). The file holds
one or_pk per line. The service:

- Reads the file.
- For each or_pk, runs batched `DELETE FROM pk_signals WHERE pks_or_pk = N
  LIMIT 100000;` in a loop (waits a second between batches so other
  work isn't blocked).
- Removes the or_pk line from the file when done.
- Runs `OPTIMIZE TABLE` periodically to reclaim disk.

Same shape as systemd `klinecollect` — long-running, file-driven,
gentle. Means cleanup never blocks active grinds; "drop tc N" becomes
"echo or_pk into the file and forget."

Surfaced by the tc_g2=104 cleanup failure during the 1D-sweep setup
(2026-05-30). Not blocking; tc_g2=104 + or_pk=54's orphan signals can
sit there harmlessly until the service exists.

### Synthetic kline volatility model from real ticks (filed 2026-05-30, r07/r08)

Idea: now that the systemd `klinecollect` service is producing genuine
tick-derived 5s bars, characterize the volatility profile of the 11
intra-minute 5s bars within each 1-minute window — variance, range,
ordering tendencies, etc. — and pass that pattern into
`SyntheticBackfiller` to generate more realistic 5s bars when
backfilling from 1m sources.

Current synthetic backfill likely interpolates naively (uniform split
of 1m into 12 × 5s, similar OHLC values). Real data has real volatility.
A statistically-grounded synthetic model — even a loose one — would
make historical backfilled data closer to live-collected data, reducing
the "synthetic vs real" boundary effect that currently makes grinds on
older (synthetic) data character-different from grinds on recent (real)
data.

Scope:
- Analyze live-collected 5s bars to extract intra-minute volatility
  patterns (per-pair, possibly per-time-of-day).
- Encode the model (simple as a per-bar variance multiplier, or as
  rich as a learned distribution).
- Update `SyntheticBackfiller` to consume the model when generating
  5s bars from 1m.
- Validate: re-backfill an old period using the model; compare signal
  characteristics to live-collected periods of similar market regime.

Not blocking the current sweep — that runs on real data (7-day window
in the recent live-collected range per the 2026-05-30 sweep plan).

### Testing — review and enhance pytest cases (filed 2026-05-30)

OptimizerRunner orchestration has no unit tests. Add at minimum:

- **`_determine_signal_source`** (r07 dispatch reshape, commit `a01092a`):
  mock `_db.execute`, assert `'vote'` returned when an active `pk_5s` row
  exists for the tc, `'line'` otherwise.
- **AND composition polarity** (r07 commit `a01092a`): the strict AND in
  `_run_vote_sourced` requires `vote == −oob_side` (vote=+1 needs
  oob_side=-1; vote=-1 needs oob_side=+1). Polarity error here silently
  inverts every signal — a focused test locks the semantic in. Same
  family of risk as the boundary/signal sign-convention thing.
- **In-band blocking**: assert `oob_side=0` produces zero gated signals
  ("no gate, no trade" default per the bny30 correction 2026-05-30).
- **`Pk5sGateComputer.compute` pm_additive pass-through** (commit `faf82d2`):
  assert `params['pm_additive']` reaches the `PKVoteMachine` constructor
  (via mock + introspect, or via a vote machine that records its config).
- **Integration smoke against reference grinds**: with the
  `--start_ms/--end_ms` fixed-window args (commit `c42a685`) now in,
  reproducible reference grinds become viable as snapshot regression
  tests — same pattern that validated Step 3a byte-identical.

**Pre-existing failures** (filed 2026-05-30): `tests/test_analyze_manager.py`
has 2 reds on HEAD — `_compute_centroid() missing 2 required positional
arguments: 'params' and 'param_types'`. Stale test vs current signature.
Agreed to land a signature-alignment fix as its own commit (no logic
change). Not done yet.

## Done (r07, May 25-26)
- ✓ MAE pipeline restore in both `_persist_*` methods
- ✓ Pine `f_bb` 70/30 alignment
- ✓ bny30 gate emulation in Pine
- ✓ SRP refactor: PKDetector → PKStateComputer + PKGateFilter + PKSignalDetector
- ✓ Transition semantics (was per-bar)
- ✓ Cleanup of pk_signals/pk_outcomes (TRUNCATE + OPTIMIZE, reclaimed 156GB)
- ✓ Validation grind or_pk=44 (80 combos, 55,170 signals, 48% avg win)
- ✓ Reference snapshot script (`snapshot_pk_signals.py`)
- ✓ Vectorized PKStateComputer + PKSignalDetector (40s → 21s/80 combos)
- ✓ Length-mismatch workaround in PKStateComputer (proper fix open)
- ✓ Pine `request.security` tuple consolidation (4s → 2s/tweak)
- ✓ Vectorization validated against or44_reference (99.4% — accepted
  drift attributable to kline-window shift)
- ✓ Architecture decision: Pine → validation only, Python canonical
- ✓ Decision delay deleted from Python (apply ran + manual cleanup)
- ✓ Vote machine extract design doc
- ✓ Parallel Claude Code session validation of handover docs
  (5 contradictions found and fixed, multiple gaps closed)

---

## Working notes — vote machine extract (next: Step 2)

**Plan vocabulary note**: r07 originally used "Phase A/B/C" (Phase A =
vectorization, Phase B = PM additive in Python, Phase C = full
15,390-combo sweep). When the architecture conversation surfaced that
the gated path has no vote machine, the plan was re-scoped into
**Steps 1-5** in the design doc. The original Phases map onto the new
Steps loosely:
- Phase A → done (vectorization shipped before re-scope)
- Phase B → became Step 4 (pm_additive needs vote machine first)
- Phase C → becomes the post-Step-4 validation/exploration sweep

The Steps 1-5 model is the active plan. Phase A/B/C language is
retained only in historical context (e.g. the dema-wraparound note's
"Phase A vectorization parity" reference).

**Current state**: Step 1 (decision delay deletion) done.
**Next**: Step 2 (extract PKVoteMachine from Pk5sGateComputer).
**Design doc**: `r07_vote_machine_design.md`.

**Reference for Step 2 validation**: re-grind self-gated test, signal
count should match Step 1 output (post-decision-delay baseline). The
Step 2 extract is pure refactor — no behavior change.

**Post-Step-4 sweep** (formerly "Phase C"): full 15,390-combo sweep on
tc_pk=99 with both vote machine and PM additive active, PM additive
sweeping 0-1 in 0.125 steps. This is the real production-target grind
for gca5m.
