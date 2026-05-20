# r05 — Multi-line ensemble calibration

**Round milestone**: join the 5s lines together in the most profitable way, using
weights and pools to blend the individual PKs for max combined results.

## State at session checkpoint

```
✓ Win-rate >100% bug             — fixed (decided = won + stopped in Python)
✓ Slope_floor diagnostic         — ungated active region found at 80-110
✓ Auto-analyze de-dup            — owned by run.py only
✓ bny30 gating API               — IndicatorComputer.compute_gate_mask (AND fold)
✓ Inspector --use_bny30          — flag + retention% header
✓ Schema: line_signals + ls_gated_in
✓ FoldManager skeleton           — tags ls_gated_in per fire
✓ Wide 6-line grid SQL           — 515K combos, bny30-gated, ~5hr parallel
► Run the 9-hour batch            — Joe's afk window
○ FoldManager: feed centroids    — wait for 6-line results
○ Affinity matrix + SnF          — wait for line_signals populated
○ MultilineOptimiser             — design phase, post-affinity
```

## Files shipped this round

### Code (replacements)
- `analyze_manager.py` — win-rate fix; OG row in TOP 20; dynamic line label
- `report_manager.py` — auto-analyze removed (run.py owns it); ReportExporter wrapped
- `indicator_computer.py` — `compute_gate_mask(db, ic_pks, base_df, fold='AND')` + `_fold_and`
- `fold_manager.py` — uses compute_gate_mask, tags `ls_gated_in` per fire
- `inspect_5s_baseline_signals.py` — `--use_bny30` flag with retention info

### SQL
- `r05_260518_line_signals_schema.sql` — `line_signal_runs` + `line_signals` (with `ls_gated_in`)
- `r05_260518_slope_diagnostic.sql` — 21-val slope_floor sweep 0-50
- `r05_260519_slope_diagnostic_hi.sql` — extension 50-150
- `r05_260519_wide_6line_grids.sql` — **the 9-hour batch**, 6 tcs, ~515K combos

### Superseded
- `r05_260519_indicator_computer_additions.py` — replaced by full `indicator_computer.py`

## Decisions and rationale

### Stop = 0.71 for 6-line calibration
r04 grinds at 0.60/0.71/0.95 showed near-identical centroids (sensitivity
±0.05% across stops). Stop choice doesn't drive param selection — it scales
absolute expectancy. Middle stop avoids extreme bias.

line_signals carries outcomes for all 3 stops side-by-side per row, so we
keep stop comparability for SnF affinity work without re-folding.

### bny30 fold = AND (conservative)
bny30M AND bny30p must both agree on direction. Filters false starts on
trending legs without adding signals. Joe's design intent: the gates are
present to prune, not to amplify.

### bny30 applied as post-hoc filter, not in PK generation
Raw 5s PKs stay accessible — preserves future pyramid logic which Joe noted
will need un-gated signals. Filter is downstream of fire generation.

### ls_gated_in column, not separate runs
A single fold captures both raw and gated subsets. Query via
`WHERE ls_gated_in = 1` for gated subset. No re-fold to compare.

### Slope_floor: 5 vals, range 60-180
Diagnostic (ungated) found 80-110 active for gcs5m. Under bny30 gating the
active region may shift (signals already filtered upstream). Wide grid
covers both the high-floor regime AND the possibility that gated runs
work better with lower floors.

### Equal-voice weights for all 6 lines
weight_close=5, weight_wide=2 for every line. Single-line testing doesn't
much depend on weight magnitude (no opposition to cancel against), but
uniform methodology keeps the calibration comparable across lines.

### Slope_floor active region needs context
The 0-50 diagnostic showed flat plateau then climb starting at 80. The
50-150 extension found expectancy peaking around 110 (with thinning signal
count past that). Joe's TV experiments suggested values like 11/33/15
worked — those align with the climb region. The naming is a misnomer:
slope_floor at 100+ is doing percentile-like filtering of slope magnitude,
not a literal absolute threshold.

## The 6 lines in scope

| ic_pk | label    | type | params                          | role             |
|-------|----------|------|---------------------------------|------------------|
| 4     | gcs5m    | BB   | len=12, mult=0.74, src=hlcc4    | medium responsive |
| 5     | gcb5M    | BB   | len=40, mult=1.00, src=hl2      | slow trend       |
| 6     | (gcb.p)  | K    | k=5, rsi=38, stc=29, hlc3       | medium k         |
| 7     | (gca.o)  | K    | k=4, rsi=9, stc=50, ohlc4       | ultra-fast k     |
| 8     | gca5m    | BB   | len=6, mult=0.74, close         | ultra-fast BB    |
| 9     | (gcs.r)  | K    | k=6, rsi=40, stc=96, hl2        | slow oscillator  |

ic_pks 1, 2, 3 are gates only this round: b6M (parked for later), bny30M
(gating), bny30p (gating).

Production designs three speed regimes (fast/medium/slow), each with one BB
and one K — cross-indicator-type confirmation per speed band. The SnF work
will surface this structure quantitatively via the affinity matrix.

## The 9-hour wide grind batch

### Per-line combo math
```
BB lines (ic 4, 5, 8):
  len(7) × src(5) × pool_c(13) × pool_w(11) × pool_range(3) × slope_floor(5)
  = 75,075 combos per line
  (gca5m: 6 effective len values, → ~64,350 combos)

K lines (ic 6, 7, 9):
  k_len(3) × rsi(3) × src(5) × pool_c(13) × pool_w(11) × pool_range(3) × slope_floor(5)
  = 96,525 combos per line

Total: ~515K combos across 6 lines
Parallel wall time: ~5hr at Joe's 20K/hr rate
```

### Apply

```bash
# Apply code
cp /mnt/user-data/outputs/indicator_computer.py     optimus9/compute/indicator_computer.py
cp /mnt/user-data/outputs/analyze_manager.py        optimus9/analysis/analyze_manager.py
cp /mnt/user-data/outputs/report_manager.py         optimus9/orchestration/report_manager.py
cp /mnt/user-data/outputs/fold_manager.py           optimus9/analysis/fold_manager.py
cp /mnt/user-data/outputs/inspect_5s_baseline_signals.py inspect_5s_baseline_signals.py

# Apply schemas
mysql ... < /mnt/user-data/outputs/r05_260518_line_signals_schema.sql
mysql ... < /mnt/user-data/outputs/r05_260519_wide_6line_grids.sql

# Note the 6 new tc_pks from the SELECT at end of the SQL.
# Then run all 6 in parallel (one terminal each):
python3 run.py start --tc_pk=<gcs5m_tc>      --lookback_days=3
python3 run.py start --tc_pk=<gcb5M_tc>      --lookback_days=3
python3 run.py start --tc_pk=<gca5m_tc>      --lookback_days=3
python3 run.py start --tc_pk=<gcb.p_tc>      --lookback_days=3
python3 run.py start --tc_pk=<gca.o_tc>      --lookback_days=3
python3 run.py start --tc_pk=<gcs.r_tc>      --lookback_days=3
```

## What happens after the batch finishes

1. **Auto-analyze fires per grind** (run.py hook) — produces top-20 + centroid per line
2. **Capture each line's centroid** — record in a centroids.json or similar for the next fold
3. **Run FoldManager** on the 6 centroids with the same 3-day window:
   ```python
   from optimus9.analysis.fold_manager import FoldManager
   FoldManager(db).run(
       tp_pk=1, lookback_days=3,
       centroids={4: {...}, 5: {...}, 6: {...}, 7: {...}, 8: {...}, 9: {...}},
       stops=[0.60, 0.71, 0.95],
       gating_on=True,  # bny30 AND fold
   )
   ```
4. **Verify line_signals populated**: `SELECT ls_ic_pk, ls_gated_in, COUNT(*) FROM line_signals GROUP BY ls_ic_pk, ls_gated_in`
5. **Affinity matrix queries** — run pairwise co-fire + lead/lag analysis at multiple windows
6. **MultilineOptimiser design** — based on affinity findings, propose weight vectors and test against combined signal expectancy

## Open architectural questions for after the batch

### Slope_floor naming and interpretation
Active region at 100+ means slope_floor isn't a literal slope threshold —
likely a percentile or scaled multiplier comparison. Worth digging into
the Pk5sGateComputer source to confirm and possibly rename. Not blocking.

### K-line stc_len sweep deferred
Each K-line's stc baseline is wildly different (29 / 50 / 96). Sweeping it
would multiply combo counts. For r05 we hold stc at baseline; if r06 shows
K-line centroids drifting suspiciously, we revisit.

### When does b6M re-enter
ic_pk=1 (b6M) is the higher-TF (6 minute) trend line. Joe noted it lands
in the ensemble "after 5s lines have passed their tests." After r05's
multi-line ensemble validates, b6M becomes the next addition — but as a
gate, not a vote contributor. Needs its own calibration round.

### Pyramid future MVP
Pyramid trades will need access to raw 5s PK signals (un-gated). The
current FoldManager already preserves these via `ls_gated_in=0` rows.
When pyramid arrives, it queries the raw subset.

## r05_todo carry-overs (open items)

From earlier in the round:
- Fold tool for compare — when compare path becomes slow, materialize
  `combo_summaries` aggregates per or_pk (~230x query reduction)
- Tickcollector debug log spam — cosmetic, fix during a quiet stretch
- ReportExporter schema drift — `pko_result` references dropped column;
  needs source patch (auto-analyze covers the user-visible function, so
  this is non-blocking)
- Pyramiding and `_can_long/_can_short` divergence — design-level park
- Architectural question parked from r04 — could b6m use only
  Pk5sGateComputer instead of PKDetector

## Decisions log (chronological)

1. AB validation Pine emitter shipped — confirms Python sim matches a
   known-good Pine source
2. Inspector ceiling=1.0 — caps banked profit at scalper-realistic level
3. Win-rate fix — `decided = won + stopped_ct`, computed in Python
4. OG line in TOP 20 — best combo matching xlsx baseline, labeled `og`
5. Slope_floor diagnostic — found 80-110 active region (ungated)
6. bny30 fold = AND — conservative, prunes false starts
7. compute_gate_mask generalized — reusable beyond ReportManager
8. ls_gated_in column — single fold captures raw + gated
9. (γ) inspector with retention header
10. Wide 6-line grids at 515K combos for 9-hour Joe-downtime window

## Goal forward

The 9-hour batch produces 6 calibrated line centroids under bny30 gating.
FoldManager runs those centroids, populating line_signals. Affinity matrix
analysis surfaces the support/friction structure. MultilineOptimiser uses
that structure to propose weight vectors that exploit the natural
ensemble dynamics — what Joe's intuition has been pointing at all round.

The eureka moment lives in the affinity matrix. The grinds and the
plumbing exist to put us in a position to see it.
