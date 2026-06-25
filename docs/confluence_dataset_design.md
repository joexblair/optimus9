# Confluence dataset — design (concept run)

## Why
The indisputable substrate. Rank every line-confluence by **swing-proximity** — built once, stored,
long-running — so no future question re-cuts a contaminated hold-out (the methodology trap from
`snf_research.md`). The metric is named and mechanism-grounded: avg-win-MAE = how early bls→3 fires
relative to the swing; a confluence that marks swing-proximity → shallow MAE → tradeable on a tight stop.

## The metric (locked)
**"Does a group's OOB-cross *near a bias update* predict that the update's trade runs a shallow MAE?"**
The same-side-of-50 **rating** is computed + stored for *post-dictal* analysis — it is NOT a gate.

## Scope
- **Concept run** (this build): the **11 itf=30s lines** (`b30M b30b b30m bny30M bny30p s30M s30m s30r
  s90M s90b s90m`) → C(11,3)+C(11,4) = **495 groups**, **one window** (0611→0618), **s3m bias stream**.
- **Full run** (later): all 65 lines (720k groups, multi-window). Concept run measures the real
  row-multiplier that sizes the buffer pool before that load.

## Boundaries (locked)
OOB = the **global** `optimus9_system.hi_boundary`/`lo_boundary` (85/15). Not the per-line `ic_*_boundary`
(uniformly 85/15 today, being sunsetted). Concept run reads `optimus9_system` directly — no view dependency.

## Pipeline — 3 stages, SRP-split

### 1. groups
`cf_group(group_pk PK, sz TINYINT, members VARCHAR UNIQUE)` + `cf_group_member(group_pk, ic_pk)` —
the member child carries the index that fans a pair-cross to its groups.

### 2. pair-cross pre-walk (compute once, fan to groups)
Walk the window at 30s. For each of the **C(11,2)=55 pairs**, a **cross** = the two lines swap order
while **both are OOB on the same side** (both >85 = hi-breach, or both <15 = lo-breach):
- `cf_pair_cross(pair_cross_pk PK, ic_a, ic_b, cross_ms, breach ENUM('hi','lo'), val_a, val_b)`

Then fan each pair-cross to every group containing the pair, computing the **rating** = (# of the
group's lines on the breach side of 50) / group size:
- `cf_cross(cross_pk PK, group_pk, pair_cross_pk, cross_ms, breach, rating, n_aligned, n_total)`
- `cf_cross_line(cross_pk, ic_pk, val)` — all the group's line values at `cross_ms` (Joe: "store the
  values of all lines in the group"). [FORK B: normalized child vs a JSON column — see below]
- rating examples (confirmed): 3-line all-aligned 1.0 · 1-against 0.66 · 4-line 2-against 0.5.
- Index: `cf_cross(group_pk, cross_ms)`, `cf_cross(cross_ms)`.

### 3. bias-walk (x swept 0..4, stored per-x)
For each **s3m bias update**: its cascade trade's **MAE** = the metric target. For each `x` in 0..4
(flt_half: ±x 30s bars, cap 4 = 9-bar window), find the groups with ≥1 cross in `[bias_ms ± x·30s]`:
- `cf_bias_walk(walk_pk PK, bias_ms, bias_dir, bias_mae, group_pk, x, n_crosses, mean_rating,
  best_rating, nearest_bars)` — sparse: a row only when a group has a cross in the ±x window.
- Index: `cf_bias_walk(group_pk, x)`, `cf_bias_walk(bias_ms)`.

## DoD
All three tables populated for the concept run, AND the metric is computable end-to-end: per group,
the avg `bias_mae` of bias updates whose cross fell within ±x → rank the 495 groups by swing-proximity,
per x. Proves the cross/rating/x-sweep logic, the indexing, and the real storage shape before scaling.

## Forks resolved
A — bias stream = **s3m** (a parameter, swept later). B — `cf_cross_line` = **normalized child**.

## Concept run — results + the scale wall (0624, `concept_run.py`)
**Pipeline validated end-to-end.** 495 groups · 30,668 pair-crosses · **1.38M `cf_cross`** ·
**5.24M `cf_cross_line`** · 28,257 bias-walk rows (27 traded updates). Metric computable — top
swing-proximity groups rank cleanly (s30r/s30m/s90M cluster; **descriptive only** — n=4–6, one
window, not walk-forward validated).

⚠ **SCALE WALL (the concept run's real job).** The per-group fan is the bottleneck: 11 lines / one
window already = 1.38M cross-rows + 5.24M line-values. The full 65-line run projects to **~2.3 BILLION
`cf_cross`** (2,080 pairs × ~2,016-group fan × cross density) — infeasible to materialize.

**REDESIGN for the full run:** `cf_cross` (per-group) is an unnecessary intermediate — the bias-walk
needs only *which group had a pair-cross near a bias update*, derivable from **`cf_pair_cross` +
`cf_group_member`** directly. Store pair-crosses (~1.16M, feasible); compute the rating **on-demand**
for the sparse bias-walk-relevant crosses only. The fan moves to the sparse bias-walk stage, never
materialized whole. The concept-run's per-group `cf_cross` stays as the *validation* artifact.
MySQL-conf sizing waits for this redesign (no point tuning for a 2.3B-row table we shouldn't build).

## Analysis outputs (regenerated each run)
- **`vw_cf_walk`** — joined view; `bias_ms`→`FROM_UNIXTIME` (UTC), floats 2dp. Carries the 3D test:
  `side_ok`, `s30a_present`, `mfe_ok`, `eff_mae`. Point Excel here for raw (group × x × MAE).
- **`cf_walk_summary`** — per (group, x): `n`, `avg_abs_mae`, **`avg_abs_eff_mae`** (3D-injected),
  `avg_rating`. Compare the two MAE columns to see the 3D nod's effect.

## 3D test → eff_mae (`cf_bias`, on `swing_detect`)
Per traded bias update: `side_ok` (leading side of its leg, leg-bounded walk) · `s30a_present` (s30M &
s30m OOB at the pinnacle + s30r OOB within `lp_config.lp_s30r_lb`=19, for its lift-off) · `mfe_ok`
(post-bias favourable move to the **next favourable pivot** ≥ 0.9%). `eff_mae = (side_ok AND mfe_ok) ?
0 : bias_mae` — a zero for bias updates that rode a clean swing but entered late, so the slow-bias value
isn't buried by the entry-MAE. s30a **recorded, not gated**. ⚠ `find_pivots` stalls on a leading NaN —
ffill `close30` first. Stage-1: 27 traded · s30a 21 · side_ok 10 · mfe_ok 11 · 2 injected (eff 1.63 / raw 1.74).

See [[snf_research]], [[project_snf]].
