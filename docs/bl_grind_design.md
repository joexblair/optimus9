# BL Machine Grind — Design (line-set + knob optimisation)

**Status**: planned 2026-06-06, autonomous pass while Joe rests. Pre-code,
recycling a known-good (the gate sweep). Interrogate before building.

---

## TL;DR

We have a working multi-line BL machine but we've only ever eyeballed *one*
config. A grind lets the **data pick the line set + knobs** against an objective,
instead of hand-tuning. The objective already exists and is price-intrinsic — the
**±0.9 % profit partition** from the gate sweep — and the BL combined-gate is
structurally the *same kind of thing* as the bny30 gate: a filter with an
objective ground truth that per-line grinds lack. So this is ~99 % a **recycle**
of `gate_sweep`, with the BL state machine plugged in where the AND-fold sits.

Free byproduct, same as the gate sweep: the **winner-MAE histogram** → an
empirical stop floor. This is the thread that pulls the data-stop (~0.68) toward
the trusted manual 0.33.

---

## Why this is the right next rung (and a clean recycle)

The gate-sweep design doc says it outright: *"This is the SnF machine with a
cleaner objective… pick N lines from a library, sweep their params + composition,
score against an objective. Build it generic, SnF inherits most of the
machinery."* The engine (`gate_sweep_runner`: swappable `template`, `_line_side`
masks, `_fold` composition, `run_sweep` loop) was **built generic on purpose**.

The BL grind is simply the **next consumer**:

```
gate sweep   : lines → AND-fold → breach mask    → score vs P   (window/IoU)
BL grind     : lines → BL machine → combined gate → score vs P   (event/gate-open)
SnF (later)  : lines → temporal coalition → SnF    → score vs cluster_quality
```

Same skeleton; the **composition** and the **scoring granularity** are what
differ. So most of the work is wiring the BL machine in as a pluggable fold —
not building a grind from scratch.

---

## The objective — leg-capture expectancy (NOT the PK partition)

**Correction (Joe, 2026-06-06):** the PK grind measures *per-timestamp*
profitability to a **fixed** ±0.9 % target. The BL machine emits a different
output — a **reversal call + the LEG it targets** — and that leg is the actual
swing (variable: 1 %, 5 %, …). Scoring BL gate-opens with the ±0.9 % partition
measures the wrong thing and *caps* the leg size, which is the very quantity the
BL exists to capture. So the partition / `label_winners` are the PK grind's
tools and **do not transfer** here.

### Ground truth: the swing legs (recycle `bl_review`)

The BL's claim is "a reversal leg starts here," so the truth is the **swing
structure** — `find_pivots(px_smooth, 0.9 %)` (0.9 % is the ZigZag *pivot*
sensitivity, not a trade target). `bl_review` already computes, per gate-open:

```
stop_pct   (req2) = adverse % to the prior/contra swing  (how far it ran wrong)
profit_pct (req3) = the LEG % to the next swing           (the move it opens for)
```

That **is** the BL objective, already built. The grind aggregates `bl_review`
across configs — no new ground-truth pass.

### The score: expectancy, not binary win-rate

Because the BL rides the leg, **leg size matters** — a gate-open catching a 4 %
leg ≫ one catching 1 %, even though both clear ±0.9 %. So per config, over its
gate-opens:

```
expectancy ≈ mean(profit_pct in the reversal dir)  −  mean(stop_pct paid)
reward_risk = mean(profit_pct) / mean(stop_pct)
recall      = swing reversals the gate-opens caught / total swing reversals
```

Optimise **expectancy** (or reward/risk) balanced against **recall** (don't miss
the big reversals). **Q1 (reframed):** expectancy, reward/risk, or a
Joe-weighted blend (a scalp may cap leg-ride and prefer reward/risk)?

### Stop floor (free byproduct — the `stop_pct` distribution)

The histogram of gate-open `stop_pct` (the *real* adverse-to-swing — it can
exceed 0.9 %, unlike the partition's bounded MAE) is the honest empirical stop
floor for BL-gated entries. This is the 0.68→0.33 lever, measured on the actual
adverse excursions rather than a flat-threshold bound.

---

## The sweep space

Three axes, biggest first:

1. **Line set** (the headline — "tune the line set"). Which of the candidate
   library (`bl_lines`: hb9b, mnm9m, b30b, s30r, s90b, …) are active, and in what
   combination. Adding a line makes the combined-gate *stricter* (min → all must
   be done), so this trades **frequency for consensus** — the core thing the grind
   discovers. Combinatorial; handled by scouts (below), not brute subsets.
2. **Per-line params** — `bb_mult` (Joe: tighter OOB for the bobbing BBs), `bb_len`,
   `src`, and for K lines `k_len/rsi_len/stc_len`. Same dims the gate sweep
   already sweeps via the `template.params` map.
3. **Machine knobs** — `curl_floor`, `curl_lookback`, `grace`, `pseudo_cross`,
   `fence_pad`, `bb_pad`, `exit2_ref`. Shared across K lines (the active
   `bl_config`). **Q2:** sweep these, or freeze at proven and let the line set +
   per-line params carry the grind? (Lean: freeze first pass — keep the space
   tractable; they're a second-order grind once the line set is bound.)

Boundaries 15/85 frozen gospel (constants), per the gate-sweep ruling.

---

## Flow (mirrors the gate sweep, one structural swap)

```
[0] Swings + per-gate-open legs   (recycle bl_review, once per window)
      find_pivots(px_smooth, 0.9%) → the swing legs; the swings ARE the horizon
      (no fixed ±0.9% wait). stop_pct dist over all gate-opens → the stop floor.

[1] Solo scouts   (one per candidate line, concurrent — the "combine-worth" check)
      run EACH line's BL machine alone → its gate-opens → expectancy / recall vs
      the swing legs → which lines individually earn their salt, which dims move them

[2] Read surfaces → shortlist lines + promising param ranges
      a line with a weak solo score may still earn a place if it lifts the
      COMBINED expectancy (consensus value the solo can't see) — flag those for [3]

[3] Combined grind   (the real one)
      sweep promising line subsets × their params (× knobs if Q2=yes), each combo:
        build each line's series from params → run() / run_bb()
        fold → combined-state min → gate-opens (all-lines-done transitions)
        score the gate-opens vs the swing legs (expectancy); log each line's solo
        expectancy (consensus check)
      → ranked surface → the optimised BL config + its stop_pct-derived stop

deliverables: validated BL config (line set + params) · MAE stop floor · per-line
              solo-vs-combined table (which lines actually pull their weight)
```

The only loop that's new is **[3]'s per-combo body** running the BL machine
instead of an AND-fold. `score_combo`/`run_sweep` scaffolding, the parallelism,
the surface-ranking — all recycled.

---

## Footwork (the recycle map)

```
NEED                          EXISTING                              CALL
──────────────────────────────────────────────────────────────────────────────
swing legs (ground truth)     find_pivots (bl_review already uses it)    REUSE
per-gate-open stop/profit     bl_review req2/3 (the BL objective, built) REUSE (aggregate it)
swappable line template       gate_sweep_runner.template + build_configs REUSE
per-combo sweep + ranking     run_sweep / score_combo                    REUSE (structure)
param grid                    ParameterGridBuilder.build                 REUSE
parallel fan-out              OptimizerRunner / the 16-core sweep        REUSE
build each line's series      IndicatorComputer (already in bl_detect._line) REUSE
─────────────────────────────────────────────────────────────────────────────
the COMPOSITION (the fold)    AND-fold (_fold)                           NEW: run BL machine
                                                                          (run/run_bb + combined min
                                                                          + gate-open extraction)
expectancy aggregate scorer   score_signals is win-rate/f1 (binary)      NEW small scorer: gate-opens'
                                                                          leg-capture expectancy / R:R
NOT REUSED                    compute_profit_partition / label_winners   ✗ PK grind's per-timestamp
                                                                          fixed-±0.9% tool — wrong output
```

So the genuinely new code is small and well-bounded: a **BL-machine fold**
(reuses `breaching_line` + the `bl_detect` per-line/combined logic — factor the
fold out of `report()` so the grind and the live detector share one path) and a
**gate-open expectancy scorer** (reuses `bl_review`'s stop_pct/profit_pct). The
load-bearing measure — the per-gate-open leg/adverse — is already built.

---

## Observations · ideas · tangents (bearing down)

- **The bobbing BB is a feature for the grind, not a bug.** mnm9m OOB ~40 % of the
  time made the all-done gate fire 112× — exactly the kind of over-loose config
  the f1's *recall-vs-precision* tension is built to punish/reward. The grind will
  naturally pull `bb_mult` up (tighter OOB) until the bobbing stops costing
  precision. So Joe's "tweak with bb_mult" *is* a grid axis, not a manual step.
- **Factor the fold out of `report()` first.** Right now the per-line-run +
  combined-fold lives inside `bl_detect.report()`. Pull it into a pure function
  `run_bl(families, base, ts, cfg) → (per_line_states, combined, gate_opens)` that
  both the live detector and the grind call. This is the Footwork tidy that makes
  the grind a thin wrapper — and it's the same "shared composition" the gate sweep
  needed (its "core structural change… build from grid params"). Do this as
  step 0; the grind falls out of it.
- **Solo-vs-combined is the real intel.** The deliverable isn't just "best
  config" — it's the table of *which lines lift the combined f1 and which are dead
  weight*. That's the line-library curation SnF will inherit. A line with a great
  solo score that doesn't lift the combined is redundant (correlated with an
  existing one); a weak solo that lifts the combined is a genuine diversifier.
  This is conviction-weight signal (#10) falling out for free.
- **The MAE histogram is the prize, quietly.** Every other output is a config; the
  winner-MAE distribution is *new knowledge about the asset* — the adverse-
  excursion structure of BL-gated entries. It directly informs the stop and is the
  empirical case for/against 0.33.
- **TOB plugs in here (post-SnF).** The trade-direction-at-gate-open question (3)
  is the TOB machine. Once it exists, the grind's "reversal_dir" gets richer (TOB
  may fire *at the breach*, not only the reversal) — the scorer's signal set
  becomes {gate-open reversals} ∪ {TOB breaches}. Design the scorer to take a
  signal *list* so TOB drops in without a rewrite.
- **Recall horizon coupling.** `H` (the ±0.9% wait bound) interacts with the BL
  machine's TF: hb9b is TF9 (slow), so its gate-opens are sparse and want a longer
  H; a 30s line wants a shorter one. **Q3:** one global H, or H scaled per the
  primary line's TF? (Lean: start global, watch P saturation as the gate-sweep
  guard warns; revisit if the slow lines look starved.)
- **Don't re-grind the gate underneath us.** The gca5m raw-pk (the SnF source) is
  itself gate-conditioned upstream. The BL grind optimises the BL gate, *not* the
  pk — keep the pk fixed (the proven gca5m) so the objective ground truth (price)
  isn't moving under two optimisations at once. (Mirrors the gate-sweep ordering
  ruling: dial one gate at a time.)

---

## Open questions (for Joe)

- **Q1 — objective:** f1 of (precision, recall), or a precision-weighted blend?
  A scalp may rationally prefer fewer, surer gate-opens (precision) over catching
  every reversal (recall). What's the win you're actually buying?
- **Q2 — knob sweep:** freeze the machine knobs at proven and grind the line set +
  per-line params first (tractable), or sweep knobs in the same pass?
- **Q3 — leg definition (replaces the dissolved horizon):** `profit_pct` = the
  *next single swing leg*, or ride further (next-N pivots / trail to a contra
  pivot)? The horizon knob is gone (swings self-bound); this is what's left of it.
- **Q4 — line-set search:** solo-scout → shortlist → combined (my plan), or do you
  already have a hunch which 2–3 lines are the spine (so we skip straight to the
  combined grind over their params)?
- **Q5 — what is a gate-open trade, exactly:** the reversal at the open (my
  assumption, matching bl_review req2/3), confirmed? Or does the trade fire on the
  *first line to breach* (the organic-trend reading) — which would change the
  signal set the scorer sees?

---

## Step 0 (the only prerequisite, and it's a tidy not a build)

Factor `run_bl(...)` out of `bl_detect.report()` → a pure composition the live
detector and the grind share. Then the grind is: `for combo in grid: run_bl →
gate_opens → label_winners → f1`. ~99 % recycle confirmed.
