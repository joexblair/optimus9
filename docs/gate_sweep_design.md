# Gate Sweep — Design (bny30M + bny30p optimisation)

**Status**: design landed 2026-05-31 (bounce-land arc, this session). Pre-code.
Update with corrections before building.

---

## TL;DR

The bny30 gate (bnyM + bnyp, AND-folded) conditions *when* a 5s PK is allowed
to fire. It has never been optimised — every per-line grind to date ran against
a hand-tuned gate, so per-line results are skewed by an un-dialled filter. The
gate is the **deepest root** in the stack: change it and the surviving signals
change, which forces a re-grind of everything downstream. So it's a **precursor**
to building any *keeper* per-line library or SnF collection.

The breakthrough this session: the gate has an **objective ground truth** that
the line grinds lack. We optimise it so its breach windows line up with the
windows where a trade can actually execute profitably — and "profitable" is
computable straight from price (no line, no probe centroid). The objective is
the **gate match score**; the profit target is **±0.9%**; a free byproduct is a
**winner-MAE histogram** that hands us an empirical stop floor we've never had.

---

## Why now (ordering)

Dependency direction is unambiguous:

```
gate (bnyM+bnyp) → conditions → per-line signals → per-line libraries → SnF coalition
```

The gate is upstream of even the cluster_quality_score scoring (scoring scores
*gated* signals). A `cluster_quality_score` deferral is safe because stored
signals stay put and we re-score later — but a **gate change alters the signals
themselves**, so it can't be patched after the fact; it forces a re-grind.
Therefore: dial the gate first, then build keeper libraries against it.

This matches the filed precursor (`r07_open_items.md`, Pine section: *"OOB gate
emulation tuning as PRECURSOR — dial in bny30M/p gates FIRST … then grinds run
against validated gates"*). What was missing there was the metric. It's defined
now (below), which is what unblocks the build.

---

## Terminology — lock this, kill "OOB long"

"OOB long" is ambiguous (lower-boundary-so-trade-is-long, vs higher-boundary-
where-a-long-finishes?). The codebase already has unambiguous words. Grounded in
`compute/indicator_computer.py:110-111` (classify) and
`orchestration/optimizer_runner.py:168-170` (the AND-composition):

| indicator position        | oob_side | code's name | enables |
|---------------------------|----------|-------------|---------|
| below the **low** boundary  | −1     | **LO breach** | **LONG**  |
| above the **high** boundary | +1     | **HI breach** | **SHORT** |
| in between (in-band)        |  0     | in-band       | nothing (blocked) |

So: **LO breach is the long-enabling state; HI breach is the short-enabling
state.** Strict polarity — `vote=+1` (long) requires `oob_side=−1`; `vote=−1`
(short) requires `oob_side=+1`; in-band blocks. Never write "OOB long" again.

---

## The objective — gate match score

### Profit partition P (the ground truth)

Forward-walk every 5s bar to the **first ±0.9% hit** (within horizon `H`):

- reaches **+0.9% before −0.9%** → **long-P**
- reaches **−0.9% before +0.9%** → **short-P**
- neither within `H` → **neither** (chop / no-trade)

This is **line-independent** — purely a property of price. The ±0.9% is both the
target *and* the implicit opposite-side bound, so **there is no separate stop
parameter**. It's self-correcting: a bar that only reaches +0.9% after a −3% dip
hit −0.9% first, so it is *not* long-P. Consequently **every long-P bar's max
adverse excursion is bounded under 0.9% by construction.**

The three-class partition (long-P / short-P / neither) maps exactly onto the
gate's three states (LO breach / HI breach / in-band) — that alignment is what
makes the score clean.

### The score

Painted-timeline definition (long side; short side symmetric):

```
gate match score = correct directional breaches / painted bars
  hit     = (gate LO ∧ long-P)  or  (gate HI ∧ short-P)
  painted = any bar where the gate breaches  OR  P is tradeable
  → both-silent bars (in-band ∧ neither) fall OUT of the denominator,
    so easy correct-silence can't inflate the score
  → wrong-side breaches (LO ∧ short-P) are painted-but-not-a-hit → penalised
```

This is intersection-over-union over `{gate breaches} ∪ {P tradeable}`. It
punishes **too-loose** (gate open with no profit → false-open grows the bottom)
and **too-tight** (profit there, gate shut → false-close grows the bottom) in a
single number. We call it the **gate match score**; "IoU" stays out of project
vocab.

`score == 1` ⇒ the gate breaches LO/HI on exactly the ±0.9%-reachable bars and
is in-band everywhere else.

**Polarity bridge (landmine — locked):** the gate's `oob_side` is *inverted* vs
trade direction. **LO breach (−1) enables LONG; HI breach (+1) enables SHORT**
(per `optimizer_runner` AND-composition: `vote=+1` long needs `oob_side=−1`).
`profit_partition` keeps natural trade polarity (long=+1, matching `pks_dir`).
So a hit is `gate == −P`, owned in one tested line in `gate_match_score.py`
(option (a), steelmanned 2026-05-31) — NOT by re-polarising the partition,
which would bury the inversion inside a general price primitive. The inversion
guard test fails loudly on any `gate == P` slip.

### Calibration guard

Watch **P saturation**: if ±0.9%-before-opposite is reachable at ~95% or ~5% of
bars, every gate config scores about the same and the metric can't discriminate.
Sanity-check P's coverage fraction before trusting a sweep; `H` (and, if ever
needed, the 0.9% threshold) is the lever to tune it.

### Granularity

bnyM/bnyp run at **30s**; the execution/P bars are **5s**. The gate is only 6×
coarser, so it tracks the envelope finely — no up-aggregation needed. Broadcast
the 30s breach masks down to 5s (gate state of the containing 30s bar held
across its 6 sub-bars) before scoring against the 5s P partition.

### Horizon H — the one residual knob

"First to ±0.9%" needs a *how long do we wait* bound, else chop drifts to 0.9%
hours later and gets mislabelled. `H` is gentler and more principled than a stop
— it's the scalp hold-time, and it's the "auto-derive x per asset (natural
temporal window for a 0.9% move)" idea already filed for far-future. Pin a
starting `H` empirically; revisit when auto-derive-x lands.

---

## Stop insight — the MAE histogram (free byproduct)

The same Stage-0 forward-walk that builds P records, for each winner, the **MAE
survived en route to its 0.9%** (bounded <0.9% by construction). Distribution of
those MAEs = the empirical stop floor: set the stop tighter than the high
percentile of winner-MAE and you knife that fraction of winners. We've never had
this because we only ever walked *signal* bars (sparse); walking *every* bar
gives the asset's full adverse-excursion structure, in one pass, for any stop.

Deliverable for now: **pure MAE histogram** (winner adverse-excursion
distribution). Richer cuts (MAE-over-time, MAE-vs-market-condition) deferred —
the market-condition cut later feeds the "match a gate to a market condition"
thread.

---

## The configs (grounded 2026-05-31)

```
bnyM (bny30M)  30s  BB   src=hl2    bb_len=58  bb_mult=1.24             bound 15/85
bnyp (bny30p)  30s  K    src=ohlc4  k_len=21  rsi_len=114  stc_len=105  bound 15/85
```

Boundaries **15/85 are gospel** — frozen as global constants (matches the
`indicator_computer.py` r08 note: high_b/low_b should be global system settings).

---

## Flow

```
[0] Precompute P  (once per window, reused by every combo)
      forward-walk every 5s bar → first ±0.9% hit within horizon H
      → per-bar class: long-P / short-P / neither
      → per winner, record MAE survived (bounded <0.9%)
      outputs: P partition (gate target) + MAE histogram (stop insight)

[1] Parallel scouts  (two ~10K sweeps, run concurrently)
      Scout A:  bnyM{bb_len, bb_mult, src} × bnyp{k_len, src}
      Scout B:  bnyp{k_len, rsi_len, stc_len}
      (each holds the other's dims at proven values; 15/85 frozen)
      per combo:
        build the two 30s series from params → LO / HI / in-band masks
        broadcast 30s masks down to 5s
        AND-compose → combined gate state per 5s bar
        score against P     (+ log each line's SOLO score as an AND-worth check)
      outputs: two response surfaces

[2] Read surfaces → bound the region
      where does match score peak, which dims actually move it,
      pick promising param ranges for the combined grind

[3] Combined grind  (the real one)
      one joint sweep over BOTH lines' params in the promising region
      (captures cross-subspace interaction the anchored scouts can't see)
      output: the optimised bnyM+bnyp gate config

deliverables
  • validated gate config → feeds every per-line grind + SnF
  • MAE histogram        → empirical stop floor
```

**Why parallel scouts (not sequential narrowing):** not a time-saver — an
intel-gather. Two independent slices reveal each subspace's sensitivity (does
source matter more than k_len? does rsi_len move the needle at all?) before we
commit budget to the combined grind. The one thing anchored scouts *can't* see
is **cross-subspace interaction** (best k_len may shift once bb_len moves) —
that's exactly what the combined grind [3] resolves. Cheap per combo (P
precomputed; each combo is two 30s series + a mask overlap), so 2×10K on 16
cores is comfortable.

---

## What's new to build (vs today)

- **Gate indicators computed per-combo from grid params.** Today `oob_side` is
  built once and fed into `OptimizerRunner`; the sweep needs the grind to build
  bnyM/bnyp from the combo's params, classify to LO/HI/in-band, AND-compose, and
  score. The pieces exist (`IndicatorComputer` + classify); they get driven from
  the grid instead of a fixed precompute. **This is the core structural change**
  (lives in `optimizer_runner.py`).
- **Configurable line-pair** — the gate is *not* hardcoded bnyM/bnyp; it's a
  swappable pair of indicator_configs. This is the abstraction SnF reuses.
- **Stage-0 ±0.9% forward-walk** — P partition + MAE recorder (new analysis
  pass, runs once per window).
- **Three-class match-score scorer** — the new metric + its solo-score
  diagnostic.

---

## This is the SnF machine, with a cleaner objective

The gate sweep is *structurally identical* to the SnF collection sweep: **pick N
lines from a library, sweep their params + composition, score against an
objective.** The gate just has the cleaner objective (price-intrinsic match
score vs SnF's fuzzier cluster_quality_score). So the gate sweep is the right
place to **build and prove the line-composition-sweep engine** — SnF then reuses
it with its own objective and a temporal-coalition composition instead of AND.

Build it generic from the start (swappable line-pair, pluggable objective) and
SnF inherits most of the machinery.

---

## Far-future (flagged, not now)

- **Gate-candidate library + daily pairing service.** Load gate-candidate lines
  into a table; a daily service pairs them and re-optimises the gate against
  fresh data. Same shape as the systemd `klinecollect` service — long-running,
  data-driven. (Joe, 2026-05-31.)
- **Gate ↔ market-condition routing.** Learn which gate config suits which
  market regime; select adaptively. Feeds off the MAE-vs-market-condition
  histogram cut. Far-future, post-HTF-ish.

---

## Corrections from the first real run (2026-05-31 evening)

Running the Scout-A MVP on live data corrected three things design-alone missed:

1. **Fold is OR, not AND.** The "simultaneously" framing was a mis-recollection;
   the rule is *either* bny30 line OOB. AND opened the gate only twice in 12h
   (bnyM/bnyp rarely co-OOB) and was blind to ~all swings; OR opens it ~20% and
   covers them. `IndicatorComputer.fold_gates` (OR) was the original production
   semantics all along. Runner default flipped to OR (commit bc4d63e).

2. **Stage 0 is ZigZag, not the forward-walk.** `profit_partition`'s ±0.9%
   first-cross fragmented ~7 real swings into ~140 tiny windows, wrecking every
   recall/precision number. Replaced by `swing_detect` (percentage zigzag,
   commit 0c721b2): 6 clean legs/12h vs 140. Calibrating basis (close vs
   high/low) + threshold against Pine ground truth (~7/6h).

3. **Metric is direction-agnostic.** Trading semantics (long/short, mean-rev vs
   momentum) were Claude's overlay and spawned a polarity detour. The real
   objective is plain region-overlap: `|filter open|` vs `|significant swing|`
   (IoU + recall/precision). The signed `gate_match_score` (gate==-P) is legacy;
   the live scorer is direction-agnostic. See [[feedback_data_not_trading]].

**Open finding:** bnyp's OOB ≈ the real swings (it's already a swing detector);
bnyM adds 37 brief blips. Under OR, bnyp gives recall, bnyM costs precision — so
the sweep's real job is judging whether bnyM's blips are signal or noise.

## Decisions locked (2026-05-31)

- Objective = **gate match score** (three-class IoU over painted bars).
- Profit target = **±0.9%**, symmetric → **no separate stop parameter**.
- P is **price-intrinsic** — no probe centroid (the "centroid helping a helper"
  voodoo is dropped; the signal-reachability check relocates for free to the
  real per-line grinds run against the dialled gate).
- Boundaries **15/85 frozen**.
- Stop deliverable = **pure MAE histogram** (for now).
- Sweep strategy = **two parallel ~10K scouts → combined grind**.
- Build **generic** (swappable line-pair, the SnF engine).

## Open / decide later

- `bb_mult` dimensionality + ranges → **decide after first runs** (Joe).
- Horizon `H` starting value → pin empirically.
- Combined-grind [3] region-selection: human-in-loop vs automated.
- Exact persistence of gate-sweep results (new table vs reuse optimizer_runs).

---

## v2 session findings — gate as a profitability filter (2026-05-31 night)

**The objective above (swing-coverage IoU) is SUPERSEDED.** Per the **project goal
— introduce compounding machines that filter raw PKs until we have a profitable
solution** (every gate we build is *applied in series*, never replaced; each shaves
noise until what survives is profitable) — the sweep was reframed to
**gate = sign-opposition filter on gca5m's vote-aggregated PK signals**, scored
by win-rate / F1 of admitted winners. Harness: `gate_signal_sweep.py` +
`gate_grind2.py` (Scout A/B) + `gate_validate.py` (cross-window robustness).

**Signal level (corrected mid-session):** the gate filters gca5m's
**vote-aggregated `s5_pk_final`** (Pk5sGateComputer → PKVoteMachine fold +
threshold 7.5), ~1,161/day — NOT the per-pool transition firehose (8,918/day,
~600× Pine's markers). p-rev sits **downstream** of the gate. gca5m centroid:
BB close/8/0.74, dema close/2, pools c7/w33/r6/sf17, weights 5/2, threshold 7.5,
pm_supp 0.4. Winner = flat ±threshold% (`profit_partition`: dir == partition class).

**What held up:**
- **M=58 is surgical — confirmed repeatedly.** The selective (purity) optimum
  keeps bnyM at len=58, just firming the band (mult 1.24→1.50). Joe's instinct
  was the whole answer.
- **bnyp role flips by metric** (as designed): fast `k_len` for recall, slow
  `k_len` + long `stc_len` for purity. `stc_len` is the real bnyp lever;
  `rsi_len` is weak.
- Two-metric split is clean: balanced (F1) = short/loose M + fast p (recall ~66%);
  selective (win-rate) = surgical M + slow p (high purity, low volume).

**The headline — what did NOT hold (`gate_validate`, 7/14/28d × 0.6/0.9/1.2%):**
- **The 3-day edges were overfit.** Candidate selective: **+8** win-rate at 3d →
  **+0.0 at 28d** at the 0.6% target.
- **At 0.6% (gca5m's target) the gate gives ~no durable win-rate edge**, and the
  current tuning consistently *hurts* (−1.1 to −1.4 across windows).
- **At 1.2% there is a small DURABLE positive edge** (current +1.2 to +2.0;
  candidate +0.5 to +2.8). The gate's real durable value is on the **big moves**.
- The current gate's sign **flips with target** (hurts at 0.6%, helps at 1.2%) —
  it's a big-move filter being judged on small moves.

**Conclusion / redirect:** win-rate-of-admitted is a *marginal* objective for the
gate — its durable value is concentrated on large moves, which a small-target
win-rate can't see. The win-rate candidate `M=58/1.50 + bnyp k80/rsi50/stc200` was **REJECTED**
(2026-05-31, visual AB on the GoalAlignment Pine overlay). It beat the old gate
+2–3pt on win-rate, but **bnyp k80 is too smooth/sluggish to do bnyp's actual
job** — getting OOB in time to back fast bnyM on swings where M has been-and-gone
before the 5s PK prints. Win-rate is blind to that temporal/structural backstop
role; Joe's eye caught it. **The gate is reverted to the trusted original
(ic_pk 2 bnyM 58/1.24/hl2, ic_pk 3 bnyp 21/114/105/ohlc4 = TV).** Further bny
optimisation is **parked until cluster_scoring + SnF** give a KPI that *sees* the
structural property. Final lesson: **win-rate was the wrong objective for this
gate — proven visually.** The build (GoalAlignment rig, `run.py validate_gate`,
boundary_slip, the live-config view) all stand and earned their keep. Next objective should be
**expectancy (weighted by move size)** or **post-p-rev traded outcomes**,
optimised on **≥14d windows** (3d overfits, dramatically).

**Open next steps (r08, fresh head):**
1. Re-objective to **expectancy / big-move recall** (not flat win-rate).
2. Bring **p-rev** into the loop — it's downstream of the gate and where signals
   become trades; the gate's true contribution is what it feeds p-rev.
3. The **combined grind** (Scout A ∩ B region) is only worth running under a
   durable objective on a long window.
4. Re-ask whether the gate's job is win-rate at all, vs regime-gating /
   drawdown-control / feeding p-rev.
