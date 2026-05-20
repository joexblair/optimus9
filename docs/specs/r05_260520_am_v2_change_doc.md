# r05 Change Doc — Analyze Manager v2

**Status**: spec for alignment check, code to follow on approval

## TL;DR

Replace expectancy-only ranking with a two-stage ranker:
- **Stage 1**: top 100 combos by expectancy (statistical edge filter)
- **Stage 2**: re-rank those 100 by gross_banked, walked sequentially for real drawdown

Output simple console (top 20) + full CSV (top 100 with all metrics) + DD audit
(combos disqualified by DD that would have made the top 100).

---

## 🔄 Parked / Revisit (come back to after testing)

These were either deferred to a later round or chosen on intuition without data:

- **Stage 1 size = 100**: arbitrary. If data shows the 100th combo's edge is
  too thin, tighten to 50 or use `expectancy ≥ 0.5 × top_expectancy` instead.
- **DD threshold = 15%**: gut number. Re-tune after seeing DD distributions.
- **Gross banking (no fee adjustment)**: fine at current signal counts.
  Revisit when any line crosses ~500 sigs in a 3-day window — drag becomes
  non-trivial at that frequency.
- **Win rate > 95% flag**: heuristic. May need to be tighter (say >90%) once
  we see how many combos hit this naturally.
- **gcb5p (K) drop decision**: deferred until SnF affinity analysis confirms
  whether it adds independent signal or just echoes gca5o.
- **Centroid still computed**: kept in output as a directional hint, but no
  longer the "deployment recommendation." May retire entirely if PROVEN
  combo path is what we always end up using.
- **MAE not yet collected**: per-signal max adverse excursion (how deep
  winners dip before turning around). Needs swing_analyzer extension. Useful
  for stop refinement in r06.
- **K-line src collapse to close**: all 3 K lines picked src=close in their
  top-1. Could mean (a) close is genuinely best for K-line momentum, or (b)
  the grid's src dimension isn't useful for K lines. If consistent across
  re-grinds, lock src=close for K and remove from sweep.

---

## Stage 1 — Qualifier

**Goal**: shortlist combos with statistically real per-trade edge.

```
SELECT combos
FROM pk_signals + pk_outcomes
WHERE (won + stopped) >= 30                      -- min decided
ORDER BY expectancy DESC
LIMIT 100
```

Expectancy formula (unchanged from current AM):
```
expectancy = (won × avg_won_pct - stopped × stop_pct) / decided
```

If fewer than 100 combos qualify (small grinds), return all qualifiers.

---

## Stage 2 — Ranker

**Goal**: among edge-validated candidates, pick the one that builds the
most equity over the window.

For each Stage 1 combo:

1. **Pull the signal sequence** (ordered by timestamp):
   ```
   signal_pnl[i] = max_profit_pct[i]  if max_profit_pct[i] >= profit_zone
                   -stop_pct          if bars_to_stop[i] is not NULL
                   0                  otherwise (inconclusive)
   ```

2. **Walk the equity curve** ($1000 seed, full compound):
   ```
   equity[0] = 1000
   for i in signals:
       equity[i+1] = equity[i] × (1 + signal_pnl[i] / 100)
   ```

3. **Compute metrics**:
   - `gross_banked` = `equity[-1]`
   - `max_drawdown` = `max((peak[i] - equity[i]) / peak[i] for i in signals)`
     where `peak[i] = max(equity[0..i])`
   - `profit_factor` = `sum(positive PnL) / abs(sum(negative PnL))`
   - `sharpe` = `mean(pnl) / stdev(pnl)` (per-trade, annualization not
     applicable to event-driven series)
   - `sortino` = `mean(pnl) / stdev(negative pnl)`

4. **DD kill switch**: any combo with `max_drawdown > 15%` is flagged but
   not dropped from output — instead listed separately in a DD audit
   report so we can see what we'd be passing on.

5. **Sort qualifying combos by `gross_banked` DESC**, take top 20 for
   console display, full top 100 for CSV.

---

## Output formats

### Console (simple, readable)

```
TOP 20 — Stage 2 (gross_banked, DD ≤ 15%)
─────────────────────────────────────────────────────────────────────
  # | len | mult |  src    |  exp%   | win% | avg_won |  sigs | gross_bank
  1 |   8 | 0.74 | close   | +1.4130 | 88.2 | 1.6961  |    42 |  $1,790
  2 |  10 | 0.74 | hlcc4   | +1.3939 | 83.8 | 1.8011  |    48 |  $2,034
  ...
```

For K lines, substitute `len_rsi | len_stoch` for `mult`:
```
TOP 20 — Stage 2
  # | len | rsi | stc | src   | exp%    | win%  | avg_won | sigs | gross_bank
  1 |   5 |  35 |  96 | close | +2.0785 | 100.0 | 2.0785  |   32 |  $1,928 ⚠️
```

`⚠️` flag for `win_rate > 95%` (sanity check needed).

### CSV (full picture)

```
rank,len,mult,len_rsi,len_stoch,src,pool_c,pool_w,pool_range,slope_floor,
multiplier,n_signals,n_won,n_stopped,n_inconc,win_rate,avg_won_pct,
stop_pct,expectancy,gross_banked,max_drawdown,profit_factor,sharpe,
sortino,win95_flag,dd_killed
```

100 rows. Sorted by gross_banked.

### DD audit (when there are killed combos)

```
DD KILLED — combos that exceeded 15% drawdown but had top-100 expectancy
─────────────────────────────────────────────────────────────────────
  rank_pre | exp%   | gross_bank | max_dd | sigs | n_signals_until_peak
       8   | +1.32  | $2,140     | 18.4%  |  64  | 12
      15   | +1.18  | $1,820     | 22.1%  |  88  |  5
      ...
```

(rank_pre = where it WOULD have ranked in Stage 2 without DD filter)

This is the "what would we be passing on?" view. May find that some
high-DD combos have legit reasons we'd want to keep (e.g., DD early in
window, then 50 consecutive wins).

---

## Centroid logic

The **centroid** (current weighted-average of top 20 by expectancy)
remains in the output as a directional hint:

> *"Top combos cluster around len=8-10, pool_c=30-34, pool_w=60-78.
> Consider these regions for the next round's grid."*

But it's **no longer the recommendation**. The **PROVEN COMBO** is now
Stage 2 rank #1.

If Stage 2 rank #1 differs from centroid → both are valuable signals.
Centroid says where the parameter space is rich. Proven says what's
deployable today.

---

## validate_centroid.py — wiring with AM v2

Updates needed:

1. `_query_top_combo` becomes `_query_proven_combo`:
   - Runs Stage 1 + Stage 2 logic
   - Returns rank #1 by gross_banked among DD-qualifying combos
2. Add `--use_centroid` flag (defaults False) for users who want the
   directional centroid instead
3. CSV header includes full Stage 2 metrics for the proven combo
4. Pine emit unchanged

---

## Slope_floor sub-60 diagnostic — separate small SQL

Before we trust 60 as the lower bound, confirm with a fast probe:

```
tc: clone gcs5m_wide_gated, all params locked at gcs5m top-1
slope_floor: 15, 30, 45, 60, 75, 90  (6 values)
window: 15 days for sample mass
combos: 6
runtime: ~3 minutes
```

If sub-60 produces meaningful signals with expectancy > 0.5%, we widen
future grids' slope_floor range. If not, lock 60 as the floor.

---

## gca5M full wide grid — queued for after AM v2 lands

Same shape as the existing wide_6line BB grid:
- baseline: len=55, mult=0.92, src=ohlc4
- ranges: len(7) × src(5) × pool_c(13) × pool_w(11) × pool_range(3) × slope_floor(5)
- = 75,075 combos, ~3.75hr at 20K/hr
- bny30 AND-gated
- stop=0.71

---

## Re-grind queue post-AM-v2

Once AM v2 ships, re-analyze (NOT re-grind) all 6 existing or_pks
(20, 21, 22, 17, 18, 19) through the new ranker. Outputs:
- 6 new top-100 CSVs
- 6 new validate_centroid outputs (using AM v2 proven combos)
- 6 new Pine emits

Then full gca5M grind on tc_pk=N (the new gca5M tc), analyze through
AM v2, validate.

**End state**: 6 lines, each with a PROVEN combo from AM v2 ranker, each
with a validate_or<N>.csv showing per-signal timestamps and a .pine for TV.

---

## Open questions for Joe

1. **`gcs5r` 100% win flag handling**: a `⚠️` in console + a `win95_flag`
   column in CSV. Sound right? Or do you want stronger: e.g., 100%-win
   combos pushed to a separate sanity-check table?

2. **`gcb5p` drop**: weakest K line at +0.79% top-1 expectancy. Keep it
   in for SnF (affinity will tell us), or drop now? Lean: keep, evaluate
   in SnF.

3. **PROVEN COMBO display**: where in the analyze output should it go?
   Currently I'd put it RIGHT before the centroid section, with a clear
   "RECOMMENDED FOR DEPLOYMENT" label. Or do you want it at the top of
   the report, before the per-param sensitivity dump?

4. **Sequence-walking 100 combos × signals each**: per combo, walking
   the signal sequence costs O(n_signals) per combo, so ~100 × 100
   signals = 10K operations. Trivial. But if a combo has 2000 signals,
   the walk is 200K ops × 100 combos = 20M ops. Still fast in pandas/
   numpy. Just noting we're not materializing 100 equity curves
   forever — just computing the final metrics per combo.

5. **Re-analyze automation**: I can make analyze_manager accept
   `--or_pks=20,21,22,17,18,19` to batch-process. Or you can loop in
   bash. Either works — preference?

---

## What I'd code (in order, after your approval)

1. `analyze_manager.py` v2 — full replacement, with two-stage logic +
   walked equity + DD audit + new CSV output
2. `validate_centroid.py` v2 — uses Stage 2 ranker by default
3. SQL for sub-60 slope_floor diagnostic
4. SQL for gca5M wide grid (mirrors existing wide_6line shape)
5. (later) Pine multi-line stub framework

---

## Ready for your sign-off

Anything to adjust before I write code? Particular keen on (1) the DD
threshold of 15%, (2) the placement of PROVEN COMBO in the report, and
(3) whether `win95_flag` is the right way to surface the gcs5r-style
suspicion.
