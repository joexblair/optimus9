# RPL Sweep — Specification

## 0. READ BEFORE FIRING THE SWEEPS (0729) — live-config state, verified against the DB

### 0.1 There are TWO baselines and the newest is NOT live

| `rc_name` | created | knobs | status |
|---|---|---|---|
| `baseline` | 2026-07-19 | **39** | **LIVE** — confirmed by runtime `R.FH` 70.0 / `R.FL` 30.0 / `R.WOBN` 9 / `TFS` 1..90 |
| `r12_rpl` | 2026-07-23 | 26 | evo-sweep elite (*"r12 climb/RPL elite (cyc1 14d)"*). **NOT live.** |

**Selecting by `rc_created_dt DESC` picks up `r12_rpl` and silently changes the engine.** Select by
`rc_name`. This is a real trap — it caught me once tonight and only the runtime cross-check exposed it.

### 0.2 What promoting `r12_rpl` would move — 9 knobs

```
wob_n                       9   -> 7      <-- IS the confirmation lag: 40s -> 30s, every cross ts moves
fence (fh/fl)          70/30   -> 65/37
xcp_bnd_offset              4   -> 3      near_ib width
anti                     50.0   -> 55
latch_depth                 5   -> 6
latch_dwell                 2   -> 1
delegate_tf_floor           1   -> 2
exit_tf_floor               4   -> 3
finisher_s1r_boundary_slip 25   -> 30
```

Plus line-config overrides `r12_rpl` carries and `baseline` does not: `s2.r.stc` 8, `s8.r.rsi` 6,
`htf.r.k_len` **9**, `htf.r.stc` 12, `s2.x.length` 5, `s8.x.length` 6, `htf.x.length` 4,
`s2.mn.mult` 0.43, `s2_top` 3, `s8_top` 10, `hi_bound` 85.0, `lo_bound` **14**.

**`wob_n` 9→7 is the one to watch.** It is the `cross_wob` hold, so it *is* the 40 s confirmation lag
(`bp50.md` §1). Changing it moves every confirmed-cross timestamp in the system and invalidates any
entry-price measurement taken under the old value.

**The pin disagrees with the elite by one knob:** `build_rpl_6of9.MINI` has `htf.r.k_len` **10**,
`r12_rpl` has **9**. The other three pinned values (`s2.r.stc` 8, `s8.r.rsi` 6, `htf.r.stc` 12) match
exactly. `MINI` is in a GATED file — re-pin only on Joe's explicit instruction.

### 0.3 Inventory audit — 25 knobs checked, 0 mismatched

The hand-written knob inventory verifies clean against the live `baseline` row. Two notes:

- `fence_hi` / `fence_lo` are stored **nested** as `fence: {fh: 70.0, fl: 30.0}`, not as flat keys.
- boundary lives in `optimus9_system`, not `rpl_config`: `hi_boundary` 85.0 · `lo_boundary` 15.0.

**12 live knobs are absent from the inventory** — all from the retest / divergence / gcs5 work in the
last three commits, so the inventory predates them:

```
retest_vote_tfs [1,2]   retest_vote_min 3   retest_min_ib_sec 120   retest_proximity_pct 0.2
div_horizon_ms 1800000  div_net_min 3       gcs5_r_tol 4
carry_ms 120000         override_latch_ms 300000  s1s2_confirm_tol_ms 240000
s2_tf_sec 120           vmin 8.0
```

`vmin` 8.0 is confirmed **dead** — seeded in config, read by nothing (`bp50.md` §10.2). It is the
fingerprint of a predictive design that was specced and never wired. Do not sweep it expecting movement.

### 0.4 Cache selection — the sweep will silently drop the sell-off otherwise

Two line caches are on disk, keyed by `end_ms`. **Select per job.**

| tape | span | `end_ms` | use for |
|---|---|---|---|
| `fb3c8372` | 04-28 06:34 → 06-13 23:59 | `build_rpl_6of9.JUNE_END` | **the sell-off window** (05-21/22/24/27) and everything in `bp50.md` §13–§15 |
| `fe809b09` | **06-01 08:00 → 07-22 23:59** | ms(7,23) | recent tape |

The window is **fixed-length ~51.7 days** (= Joe's spec'd *"52 day warmup"*), so moving `end_ms` slides
it rather than extending it. **`fe809b09` excludes 05-18 → 05-31.** Sweeping the sell-off on it drops
the regime being swept for. See handover task #13.

---

The tuning machine for the rpl flip-chain (and, by design, for dialing in other coins).
Every decision below carries the **verbatim pretext** — Joe's own words from the build — so intent is never lost in translation. Quotes are marked `❝ … ❞`.

> ❝ fun fact: when we've built this sweep tool, it'll be the tool we'll use to dial in other coins ❞
> ❝ this sweep tool ... it'll be the tool we'll use to dial in other coins ❞

Ground rule inherited from the whole project: **causal / emerging values only** — closed values are the o9-live failure. The sweep scores only what a realtime engine could have known.

---

## 1. What gets swept — the flip-chain

`run_chain` walks a day flip-to-flip from one seed. Every flip is first-class: an **RC (rollercoaster) reversal** or a **climb**. The sweep never touches the flip logic itself — it tunes the **knobs** and **line configs** the chain reads.

> ❝ the rollercoaster flips are as valid as the non-rollercoasters. they need their own rr_walk id, x-cross-pred, flip_finisher, etc. the only difference: we won't place a pyramid trade on a rollercoaster trade ❞

RC vs climb is a first-class split in the metric too (see §3).

> ❝ logic says that the RC window ends at the beginning of the full sized trade following the rollercoaster ❞

---

## 2. The metric — how a config is scored

**The trade is the chain.** A leg = flip_i → flip_{i+1}; the exit of one trade is the entry of the next. There is no separate exit signal.

> ❝ the exit is the flip sgianl - we trade in a chain ❞

**MFE/MAE are the reporting lens; the flip cycle is the trade.**

> ❝ MAE and MFE for reporting, and the flip cycle for trading ❞

**Objective** = `median(MFE − MAE)` per window, **MINIMAX over the windows** (push the worst window's edge up). Not net/PnL — MAE/MFE only.

### 2.1 Swing yardstick — `swing_detect @ 0.5%`

MFE/MAE inside a leg are measured with `find_pivots` (the canonical ZigZag producer, what `jig.score.swings` calls — never hand-rolled). Only confirmed ≥ pct% swings count; sub-pct wiggles score 0.

The yardstick must be small enough to register the smallest rollercoaster.

> ❝ maybe 0.5% - I'm not sure. we need to cover the smallest roller coaster ❞

[measured] RC-leg amplitudes: min 0.142%, band [0.4,0.5) empty, [0.5,0.6) holds 8 RC legs → **0.5% is the knee** (0.6% dropped 8 RCs; 1.5% saturated the median to 0). History: 1.5% → 0.6% → **0.5%**.

### 2.2 Everything runs on px_smooth EVENT bars

> ❝ technically - it might work better using px_smooth over price ❞
> ❝ everything needs to run on px_smooth events ❞

`px_smooth` = DEMA of the price source over EVENT bars only (volume>0), forward-filled — filler-invisible. The metric slices `ts[ei]` / `pxs[ei]` (event bars), never the ffilled index tape. Index-tape slicing flattened swings (win0 median 0.01 vs event-bar 0.462 at the same knobs).

### 2.3 RC / climb split in the report

> ❝ extend the report: RC MAE MFE and non-RC MAE MFE ❞

`_leg_net` carries the `rc` flag per leg; fitness returns OVERALL + RC + climb MFE/MAE. Stored as `re_mfe/re_mae`, `re_mfe_rc/re_mae_rc`, `re_mfe_cl/re_mae_cl`. [measured] the drawdown lives in the **climb** legs (MAE ~1.2 vs RC ~0.5) — the afternoon overrun.

### 2.4 before-MFE MAE (QUEUED — Joe 0722, confirmed)

MAE must be the heat **before** the trade goes favorable, not the whole-leg worst (which includes post-peak give-back).

> ❝ there's code somewhere that makes allowances for positions that open on the MFE side of the swing. confirm this is enabled ❞
> ❝ swing is at 01:11:00. MAE is obviously on the left of the swing. if we print a flip-finisher event after the swing, then we are on the MFE side. the code needs to recognise that the first swing the walk encounters is MFE ❞

Fix: MAE = worst adverse from entry **only up to the MFE index**. Pre-entry (left-of-swing) is already excluded (the leg segment starts at the finisher's ts). An MFE-side entry (first swing favorable) then correctly shows MAE ≈ 0.

Status: **queued, not yet in the run** — it will drop MAE further once wired. The RC MAE improvement seen so far (§2.6) is from the RC/RPL split + line evolution, not this fix.

### 2.5 Two config sets — RC mechanics vs RPL mechanics

The sweep does not corner one config — it corners **two**, each optimized for its own mechanic family.

> ❝ go until you've cornered 2 sets of configs: one for all of RC's mechanics, one for all of RPL's mechanics ❞
> ❝ I'm dropping the 20 hour cap - go until you corner the best config for RC and RPL ❞

`fitness` takes the minimax on the **objective's legs only**: OBJECTIVE `'rc'` scores the RC (rollercoaster) legs, `'climb'` scores the RPL/climb legs (per-window median of that leg-type's MFE−MAE, minimax over windows). `__main__` runs the RC evo to convergence, then the climb evo. Both are **uncapped** (`max_rounds=200`) — they stop on the corner (every knob stable 2 rounds → 30-day finals), not a clock. Every `rpl_evo` row is tagged `re_objective`, so both config sets sit side by side in the DB. The pulse renders a table (rows RC / RPL; cols MFE | MAE | net | minimax | round | sweeps), each row scored on its own leg-type.

### 2.6 Empirical (RC config, in flight)

RC objective, round 2: RC **MAE 0.604 → 0.341**, net **+0.126 → +0.378**. The lever was **HTF lines** — the RC config reached into the trend-band line tuning (`htf.r.k_len` 5→9, `htf.x.length` 5→6) to tighten rollercoaster drawdown. Instrumental: the **RC/RPL objective split** (a cleaner target than the pooled metric) and the line dimension co-evolving with the knobs. (Cross-round minimax is on different random windows — read the MAE/net drop as the signal, not the raw minimax number.)

---

## 3. Windows — universal, random, 11 × 24h

Windows are **not** a subset dimension. Each round randomly draws a fresh set; a knob only survives if it keeps winning across different draws (anti-overfit).

> ❝ not window-subsets, knob-subsets. windows are universal - each sweep will randomly pick 11 x 24 hour windows, from the last 2 months ❞

- **11 × 24h** windows, drawn from the last ~2 months (capped to the ~51-day tape).
- **Finals:** once knobs stop moving, the last 2 rounds re-score the semi-final configs on **30-day** windows.

> ❝ the final 2 sweeps after the knobs stop moving, will sweep the semi-final configs on 30 day windows ❞

---

## 4. Knob-subsets & groups — tight ranges, DB-driven

A **subset** = one knob (or line param) with a **very tight range** so each group sweep is quick.

> ❝ the knob-subsets will have very tight ranges, eg [3,4,5,], so that the subset groups are not long running ❞

**The definitions live in DB tables** — code reads them to build the evolutions; the collateral benefit is coverage validation.

> ❝ every knob-subset and group should be built in a db table(s). code will use the db to build the evolutions, and we get the collateral benefit of final coverage validation ❞

Tables:
- **`rpl_knob_subset`** — `ks_knob`, `ks_values` (JSON range), `ks_kind` (knob | boundary | line), `ks_active`.
- **`rpl_evo_group`** — `eg_subsets` (JSON list of ≤3 subset ids), `eg_active`. Groups are pure-kind (cheap vs line) for the concurrency split.
- **`rpl_evo`** — per group-sweep: top-3 config + `re_minimax` + the split MFE/MAE (the evidence).

> ❝ store the results of each group sweep in a db table: their top 3 centroid configs, and the MAE MFE results that prove the centroid choice. the db table is for my benefit - it helps me check that we're testing in the way that I envision it ❞

### 4.1 Dynamic subsets (QUEUED)

> ❝ don't keep static subsets. for each evo, swap out at least 3 knobs ❞

Each evo rotates `ks_active` — deactivate ≥3, activate ≥3 from a pool bigger than the active set. A knob earns adoption only across different active-set contexts.

### 4.2 Granularity (open question, cheap to A/B via DB)

> ❝ I wonder if 45 subsets of 16 knobs would be more effective and efficient if we use 90 subsets of 8 knobs ❞

Finding: the branch-descent is **coordinate descent** (one param at a time from the seed), so group SIZE is a parallelism dial, not an interaction dial — combinations accrue via the global re-seed across rounds. The real levers: subset RESOLUTION (finer = better) and #groups ≈ cores (16). Bigger groups only pay off if a within-group GRID (real interaction capture) is wanted for a few suspected-interacting knobs.

---

## 5. The evolutionary algorithm

> ❝ define many small subsets, use parallelism to sweep subsets in groups of 3, find the top 3 centroid configs for each group, plug those configs into new random-subset groups, and use parallelism to sweep the groups of 3 subsets, find the top 3 centroid configs for each group, etc, etc until every knob stays the same for 2 more group sweeps ❞

Per round:
1. Draw the 11×24h windows (universal).
2. Each group runs a **branch-descent** — perturb each of its (≤3) subsets one param at a time from the seeded centroids, score on the round's windows, keep the **top-3 by fitness**.

> ❝ by fitness ❞
> ❝ no random sampling - everything is precise. each group runs a branch-descent (perturb each knob/line param one at a time from the seeded centroids) scored on its 3 subsets → keeps its best 3 ❞

3. Pool all groups' top-3 → the new centroid population.
4. **Distributed seeding:** each group branches from ONE centroid (round-robin over the top-3), not all 3 — keeps 1 seed/group = round-1 pace, still plugs all top-3 into the new groups.

> ❝ distributed ❞

5. Converge when **every knob is unchanged for 2 more rounds**, then run the 30-day finals.

Scale expectation:

> ❝ I expect that there will be more than 500 sweeps run by the end of this process of mixing and matching through levels of evolution ❞

`SELECT COUNT(DISTINCT re_round, re_group)` gives the exact sweep count; coverage checks every DB group was swept and every subset value tested.

**Cross-round caveat:** per-round minimax is on different random windows, so it is NOT directly comparable — "best-so-far by minimax" flatters whichever round drew easy windows. Read convergence from **config stability**, not the number.

> NOTE (0723): §5 above describes the original random-window/minimax algorithm. It has since been **superseded** — see §5.1 and the `project_rpl_evo` memory. Live design: fixed 32-window panel, **coarse→fine** (12-win then 32-win, deterministic line rotation keeping 1/3 of params/round), **train MAE/MFE NET (not minimax) drives adoption** (advance only on positive net, else static), **VAL + minimax are diagnostics** (soft spots = confluence gaps), **compose-and-adopt** (all improving rotations graft into one measured config).

### 5.1 OOS checkpoint & fork detection (Joe 0723)

**Why:** we drill the small (coarse) window to stagnation. A rapid train-net jump is exactly when the config risks overfitting that small window. We need a **banked checkpoint** to answer *"is this config full-window-worthy?"* — and if not, to locate the **fork** (the rotation where train-cornering stopped generalizing) so we attack there.

> ❝ we need to bank an oos cycle next … we'll keep drilling on our small window until stagnation. if the fresh oos report shows that the config is not full-window-worthy, then we know where the fork took place and we can attack accordingly ❞
> ❝ the oos report needs to get banked everytime net has jumped by 0.5 in 2 cycles ❞
> ❝ I'll need the candidate line configs also ❞

**Trigger (DUAL, Joe 0723):** per objective, whichever comes first —
1. **JUMP** — adopted train-net rises **≥ 0.5 over 2 cycles** (`net[r] − net[r−2] ≥ 0.5`), or
2. **PERIODIC** — **every 3rd round** of a cycle (3-round floor so the cycle does real work first).

*Why the second was needed:* the jump alone **never armed**. Cycle 1 ran three rounds in +0.03…+0.28 increments while the IS/OOS gap ballooned to **0.83 (5× tol)** — the jump watches IS *velocity*, but the failure mode is IS/OOS *divergence*. The periodic check lets the **gap itself** route the branch.

**Action (banked):**
1. Score the current elite on the **full 32-window PANEL** (the "full window", OOS relative to the 6 coarse-train windows).
2. **Bank** it to `rpl_evo` with `re_scope='oos'`, `re_round=r` — the full candidate config (incl. line params) lives in `re_config`.
3. Log a timestamped line: the 2-cycle net jump, the **full-window net vs train net**, and the **candidate line drift** (the line params that differ from baseline — the config being tested).

**Fork:** a checkpoint whose full-window net **falls vs the previous OOS bank** while train-net kept rising ⇒ **FORK** — overfit began between the last-good bank and this one. **Verdict** = *full-window-worthy* if the latest OOS net stays positive and ≳ half the train net.

`SELECT * FROM rpl_evo WHERE re_scope='oos' ORDER BY re_round` reads the banked checkpoint series; the fork is the first row where OOS net turns down.

### 5.2 Self-managing fork recovery — beam search (Joe 0723, QUEUED)

Turn the OOS checkpoint into a **self-healing loop**: when the greedy best path overfits, back up and let the runner-up centroids compete on OOS.

> ❝ IF a new OOS report shows less overall value than the prior report — revert to the last checkpoint, spawn 2 coarse sweeps using the 2nd and 3rd best centroids — if there's only 2 threads in use, the 4th best centroid gets to hitch a ride on it. the end result will be 3 OOS reports, then we choose the best and run the loop ❞

**Mechanism:**
1. On an OOS checkpoint whose full-window net is **< the prior checkpoint's** (fork confirmed): **revert** the mainline elite to the last-good checkpoint config.
2. **Branch** from the last-good rotation's **ranked centroids** (its candidate configs sorted by train-net): spawn a coarse sweep from the **2nd** and **3rd** best; add the **4th** if a worker thread is free.
3. Each branch drills coarse to stagnation and produces its **own OOS report** → **3 OOS reports** (best-so-far + branches).
4. **Choose the highest full-window (OOS) net** → that becomes the mainline → continue the loop.

**Determinism dividend:** centroids need NOT be banked pre-emptively — at a fork the last-good rotation is **re-derived exactly** (fixed panel + deterministic rotation) to recover its ranked 2nd/3rd/4th centroids.

**RAM constraint (this box, 17 GB):** each coarse branch runs the 3-way line pool (~8 GB); 3 concurrent branches ≈ 24 GB > 17. So branches run **sequentially** (or ≤2 concurrent) — same 3 OOS reports, produced serially. The "4th hitches a ride" parallelism unlocks only if the WSL RAM ceiling is raised (§8.2).

**Build note:** implement AFTER the first real OOS checkpoints land, so the branch logic is written against observed fork behaviour rather than blind.

### 5.3 Auto-managing loop — the hunt for the agnostic IS/OOS config (Joe 0723)

**Goal:** stop optimising *fit* and start optimising *agnosticism* — converge on the config whose **IS and OOS net are ~in sync** (e.g. within ~0.15%). A config that doesn't care which days trained it is the one that survives live.

> ❝ we create a new training window that contains fresh random lines, and holding that window fast as the fresh sweeps evolve, in their hunt for the agnostic OS/IS config ❞

**CRITICAL distinction (why this is safe):** the window is drawn **once and FROZEN for the whole cycle**. The original design's failure was re-drawing **every round**, which made fitness non-comparable round-to-round (net-variance ~0.5 on an unchanged config) and destroyed elitism. Frozen-per-cycle keeps elitism/determinism fully intact; only the *cycle boundary* changes ground.

**The loop:**

> ❝ create a training window with fresh random days / run the sweep cycle against the training window / if net >0.5 in 2 cycles → run an OOS report / if the OOS shows imbalance between IS and OOS → goto start / if the OOS is worse than the last → revert to last checkpoint and spawn the top 2 losing centroids / if OOS and IS are ~in sync, bank the checkpoint and keep on truckin' ❞

```
START: draw fresh random-day training window (FROZEN for the cycle)
  └─ sweep cycle (corner TRAIN net; elitism valid — window is fixed)
      └─ TRIGGER: train-net jumped >0.5 over 2 cycles → run OOS report
          ├─ IS/OOS IMBALANCED  (|IS − OOS| > TOL)  → GOTO START (fresh window)
          ├─ else OOS < last bank                   → REVERT to last checkpoint,
          │                                            spawn top-2 losing centroids (§5.2)
          └─ else IN SYNC (|IS − OOS| ≤ TOL)        → BANK checkpoint, continue
```

Branches partition cleanly: *in sync* is the complement of *imbalance*, so the middle branch fires only when the config generalises consistently **but at a lower level than the last bank** — a bad search direction (revert+branch), as distinct from a mined-out window (fresh ground).

**`AUTO_BRANCH = False` — restrictions deleted while we characterise (Joe 0723).**

> ❝ I don't think we have a benchmark yet: we don't know for sure if config will increase very fast (ie, the first run), or if it's a slow burner. we don't know which would be OOS/IS friendly, so we need to delete any restrictions ❞

Terminating a cycle at the first imbalance (round 3) would **prune the slow-burner class before we can observe it** — a config whose IS/OOS converge over 8–10 rounds never gets to show it. So the checkpoint currently **records every decision but does not act**: cycles run to natural stagnation and we capture the **full IS/OOS trajectory per window**. Flip `AUTO_BRANCH` to `True` to re-arm the branch actions once the banked data says what to select for. **Nothing in the durable OOS log is lost either way** — the decision column is written regardless.

**Not a benchmark:** the first checkpoint (6-win coarse, IS +0.843 / OOS +0.198, gap 0.645) is **one datapoint from one window**, recorded as data — NOT a target to beat. Whether fast-rising or slow-burning configs are more IS/OOS-friendly is an open question the trajectories are meant to answer.

**Parameters to pin:**
| param | proposed | meaning |
|---|---|---|
| `TOL` | **0.15%** | \|IS−OOS\| net within this = "in sync" |
| IS window | 6 × 24h fresh random days | frozen per cycle |
| OOS set | days disjoint from the IS window | never touched by the cycle's search |
| stop | in-sync **and** stagnated | the agnostic config is found |

**Relation to existing phases:** this loop **replaces the fixed-panel coarse phase** as the exploration engine. The 32-window fine phase and the 30-day held-out TEST remain as final validation. Note fine's OOS read is *contaminated* (its train set is a subset of the 32-window panel), so fine alone cannot answer the agnostic question — that is precisely the hole this loop fills.

### 5.4 Full-tape failscan — the confluence work-list, baked into the loop (Joe 0723)

**What.** The sweep's soft-spots only ever see the fixed 10-day OOS block, so the failure-window candidate pool is small and static. The **failscan** (`rpl_failscan.snapshot`) instead scores the CURRENT cornered elite across **every 24h window of the whole tape** (46 windows), ranks by net, and banks to `rpl_failscan` (append-only, tagged snap/cycle/round/isdays). The worst windows are where the mechanics genuinely don't cover — i.e. where confluences need building. It **evolves as IS windows are swapped out over cycles**; the pulse reads the latest snapshot as an appendix.

**When it runs — the rule (baked into `run()`, deferred-pending form, Joe 0724):** the refresh is **RAM-gated** (`_ram_avail_gb() ≥ FAILSCAN_RAM_GB`, default 8 GB) but the **trigger is decoupled from the execution window** via a `_fs_dirty` pending flag:

- **The real constraint is RAM headroom, not round phase.** Failscan needs ~3 GB (one L0, scored sequentially); the sweep peaks ~15–18 GB during the *cheap* phase (5 concurrent COW L0s), ~4–10 GB elsewhere. A direct `avail` check measures the constraint instead of proxying it with "between rounds."
- **Usefulness is aligned with cornering.** A failscan is only worth taking on a ~**cornered elite**, which exists at **phase-convergence** — so convergence sets the pending flag. It then executes the first time RAM is clear, snapshotting the carried-forward (near-cornered) elite.

**⚠ Why the old "run-at-convergence-or-skip" rule wedged (and the fix):** the previous rule fired the gated check *only* at convergence and, on RAM-fail, skipped until the *next* convergence. It assumed "convergence = low-RAM (no pool up)" — but that's empirically **false**: the dying cycle's pool plus the fresh cycle spinning up keep RAM tight (~7 GB) at *every* convergence, while the RAM-clear windows (13–19 GB) fall *mid-cycle between rounds*, never coinciding with a convergence trigger. So the gate failed every cycle and the snapshot **froze for 3 cycles**. The fix (`_try_failscan`): convergence sets `_fs_dirty=True` (seeded True so cyc1 gets one); the **top of every round** retries the pending refresh at that pool-idle, RAM-clear moment; success clears the flag → runs ~once per cycle. Asymmetry still holds — a stale snapshot is minor, an OOM loses the run — so the gate stays strict; only the *when* is now "next RAM-clear round-top after a convergence," not "the convergence instant or never."

**Safety of calling mid-run:** `snapshot()` applies each elite via `e._enter` and **save/restores** engine state (`R.L0`/knobs) around every objective, so the sweep's live elite is untouched on return. The `rpl_evo_sweep → rpl_failscan` import is **lazy** (inside the hook) to break the `rpl_failscan → rpl_evo_sweep` circular. Still runnable standalone: `python3 -m optimus9.orchestration.rpl_failscan` (prints worst-5 per objective).

**Long-term:** this *is* the "have the sweep emit its own failscan" fix — never stale, never contending. Applies to the **next run**; a process already mid-flight imported the old module and won't pick it up until restart.

### 5.5 Two OOS rules added (Joe 0724)

**(a) 2-adoption OOS-regression bank-and-bail.** Complements the over-corner diagnosis: don't grind a window once a config that *was* good starts giving OOS back. OOS moves **only on adoption** (an IS-net advance; static rounds hold it flat), so this is tracked in **adoptions, not calendar rounds** (`oos_adopt[o]`). When **two consecutive adoptions each drop OOS by more than `OOS_REGRESS_FLOOR` (0.02)** — and the **peak OOS was profitable** (`> MIN_OOS_NET`; a never-good config regressing is the *imbalanced/mined-out* path, not this one) — the sweep **banks the peak-OOS config** (reverts `elite[o]` to it, sets `last_bank`/`last_good`) and returns `oos_regress_fresh` → a fresh window. Why 2 (not 1 or 3): validated on the run's own history — cyc3 climb drained OOS +0.287→+0.219→+0.160 (two consecutive down-adoptions → *fires*, banks the +0.287 peak, saves ~5 wasted grind rounds), while cyc4 climb dipped once +0.211→+0.149 then recovered to +0.220 IN SYNC (*one* down-adoption → correctly does **not** fire). 1 is twitchy on the jittery 10-day block; 3 lets a full corner's worth drain first. This turns a slice of `AUTO_BRANCH` **on** for the OOS-regression case only (it is observe-only otherwise).

**(b) OOS·32 end-of-cycle scan → KPI dashboard.** The per-round OOS is the clean **disjoint 10-day block** (`OOS·10d`, VAL). The KPI dashboard also carries **`OOS·32` / `gap·32`** columns — the cornered elite scored over the **32 tape-spanning `PANEL` windows**, which *overlap* the IS window and are therefore the **contaminated wide OOS** (a deliberately different, wider read). It's computed inside `_try_failscan` (so it shares the deferred, RAM-clear, once-per-cycle refresh with the failscan — `fitness()` restores knobs/L0, live elite untouched) and banked to **`rpl_oos32`** `(cycle, round, objective, is_net, oos32, gap32)`. The columns sit **empty (`—`) every pulse until the cycle's scan completes**, then the pulse reads the latest row per objective. Clean 10d still drives the `verdict`; 32 is the contamination-aware comparison.

### 5.6 Is the improving OOS earned skill or selection artifact? (Joe 0725)

> ❝ if the centroid is being passed into the new random training window, and the OOS32 results are gently improving, why are you labelling it as bad? be raw with me — don't aim to make me happy ❞

Carryover is real (`_phase` re-baselines the **carried** elite on each fresh window; a bail sets `elite` to the banked peak-OOS config which then carries). The question is whether the improving OOS is earned generalization or the fixed-block ratchet flattering itself. The `rpl_oos32` trajectory settles it — and it splits by objective. **Verbatim finding (from the pulse exchange):**

climb is genuinely generalizing — my "artifact" label is just wrong here. OOS·32 went negative to positive (−0.014 → +0.101), the gap narrowed (0.353 → 0.123), and at c2.r6 its IS is −0.023 while OOS·32 is +0.101 — it's performing better out-of-sample than in-sample. Nothing about fitting the fixed 10-day block produces that. OOS·32 is not the bail's target; it rising while the gap closes is the textbook signature of earned skill. You're right, and the carryover is propagating a genuinely better config, not a block-overfit one.

RC is the one with the mild overfit lean — and only RC. OOS·32 is still positive and up (+0.092 → +0.142), but the gap·32 widened 0.016 → 0.251, and IS outran OOS·32 ~5.7× (IS +0.285 vs OOS·32 +0.050 over the same span). That's IS improving faster than generalization — a lean, not a collapse. Still not "bad"; OOS·32 hasn't turned down.

Why I got it wrong, plainly: I anchored on the design's whole reason-for-being (avoid over-cornering) and pattern-matched carryover + fixed block → overfit, then led with that story instead of letting OOS·32 update me. That's me performing rigor — "warn about overfit" sounds careful — rather than reading the numbers. The numbers are more favorable than I said, especially for climb.

What actually survives of my concern, right-sized:
- The structural risk is real — OOS·10d is a soft optimization target via the bail, so it will always flatter itself. That's a design fact, not a verdict on current results.
- RC's widening gap·32 is the one live thing to watch — if OOS·32 turns down while IS climbs, that's the lean becoming real overfit.
- Caveats that keep me from calling it proven: only 3 checkpoints (small), and OOS·32 windows overlap IS so it's not a pristine hold-out. "Gently improving" on 3 points isn't yet a trend.

So: more earned skill than I credited — decisively for climb, with RC on a watch. Not "mostly artifact."

**Instrumented, not narrated:** the pulse KPI dashboard now renders a **per-cycle OOS·32 / gap·32 trajectory** (both objectives, every banked `rpl_oos32` row) so the earned-skill-vs-lean read is a measured line, not a story. RC's lean = `gap·32` trending up while `OOS·32` flattens/falls; climb's earned skill = `OOS·32` up and `gap·32` down.

---

### 5.7 MEASUREMENT-FOUNDATION GUARD at centroid promotion (Joe 0729) — NOT BUILT, task #14

> Joe 0729: *"this logic should be baked into the rpl evo sweep machine. there is a process that
> decides which centroid to promote at the start of each round — I think this would be the home for it."*

**The failure this prevents.** A fitness number is only comparable to another fitness number if both
were measured on the same foundation. Two things can move that foundation **without any knob under
sweep changing**, and neither is currently recorded on an `rpl_evo` row:

1. **Which `rpl_config` baseline is live.** `baseline` (39 knobs) and `r12_rpl` (26 knobs) differ on
   **9 knobs** (§0.2). One is `wob_n` **9 → 7** — the `cross_wob` hold, which *is* the 40 s
   confirmation lag. Change it and every confirmed-cross timestamp in the system moves, so every
   entry price moves, so MFE/MAE move. A round scored after that shift is not comparable to the round
   before it, and nothing in the output says so.
2. **Which line cache the tape came from.** Two tapes are on disk, keyed by `end_ms`: `fb3c8372`
   (04-28 → 06-13) and `fe809b09` (06-01 → 07-22). The window is fixed-length ~51.7 days, so moving
   `end_ms` **slides** it rather than extending it (§0.4). Score two rounds on different tapes and the
   comparison is between two different markets, not two configs.

**Why this section is the home for it.** The promotion step is the only place where a config measured
in round *r* is compared against one measured in round *r−1* — §5 step 4 (*distributed seeding*: each
group branches from ONE centroid, round-robin over the top-3) and §5.1 (the OOS checkpoint, which
banks the elite and reads the trajectory across rounds). Every cross-round comparison in the machine
funnels through those two points. A guard anywhere else is decoration.

**Precedent — the doc already recognises exactly this class of error, for one axis only.** §5's
cross-round caveat: *"per-round minimax is on different random windows, so it is NOT directly
comparable."* Windows were identified as a foundation that shifts; config and cache were not. This is
the same bug on two more axes.

**Design sketch — stamp, then assert.**

- **Stamp.** Every `rpl_evo` row carries a **foundation fingerprint** written at score time, not at
  read time. Minimum contents:
  - `rc_name` of the live baseline **plus a hash of its resolved knob JSON** — the name alone is not
    enough, because `upsert_config` can mutate a row in place under the same name.
  - the tape identity: `end_ms`, `hours`, `warmup`, `pxs_cfg`, and the resulting tape key (the
    `_tape_key` md5 already computed in `rpl_cache.py`).
  - the engine revision already tracked as `rr_engine_rev`.
  - the analysis floor (`build_exhaust.ANALYSIS_START`, currently 05-18) and `swing_pct` (2.0), since
    both silently change what a leg is.
- **Assert at promotion.** Before a centroid from round *r* is compared against, or seeded from, a
  centroid banked under a different fingerprint:
  - **DECIDED (Joe 0729): HALT.** *"halt so I can review in-situ and make a call."* On fingerprint
    mismatch the round stops and waits. Do **not** auto re-score the incumbent onto the new
    foundation — that silently rewrites the comparison Joe wants to inspect, and the whole point of
    the guard is that a foundation change is a decision, not a housekeeping step.
  - the diff itself must be printed — which knobs moved, which tape changed — not just "fingerprint
    mismatch".
- **Surface it in the pulse.** The KPI dashboard already renders the OOS·32 / gap·32 trajectory as a
  measured line rather than a story (§5.6). The fingerprint belongs there too: a foundation change
  mid-cycle should be visible as a marked discontinuity in the trajectory, so a step in the numbers is
  never read as a result when it is a re-baselining.

**Related trap, same root cause (§0.1).** Selecting the live config by `rc_created_dt DESC` picks up
`r12_rpl` — an un-promoted evo elite — and reconfigures the engine. Select by `rc_name`. The guard
above would catch this after the fact; selecting by name prevents it.

**Status: note only, no code.** Joe 0729: *"no code now, just a detailed note in the spec doc."*

---

## 6. Parallelism & the cache

**CPU-only fork pool** — CUDA contexts don't survive `fork()`, and forked workers inherit L0 copy-on-write. Cheap (knob/boundary) groups run 8-way (COW-shared L0); **line** groups run 2-way (each rebuilds L0 → memory-bound).

### 6.1 Per-line cache

> ❝ how are you handling the cache updates when line configs evolve? ❞

Content-addressed: each line is cached by its **resolved spec** (TF + config). A changed config → new key → fresh build of just that band's lines; unchanged lines → cache hit. No invalidation logic, no staleness possible, bit-identical to a monolithic build. Writes are **atomic** (temp + `os.replace`) so parallel workers can't tear a file. Full 360-line builds OOM → build in memory-safe batches (BATCH_MAX=24; ~23s fixed Jig cost dominates). Single-line changes are pre-populated serially before the parallel phase; novel **combos** (a centroid's accumulated line change + a new perturbation) are built on-demand once, then cached. Cache growth = the combo-tell.

---

## 7. The knobs

Current active set: 16 cheap knobs + 27 per-band line params + 2 band edges = **45 subsets**.

> ❝ add all of them ❞
> ❝ pad it out by scanning the entire transcript and find any reference to knob or sweep. you have 20 hours to play with, so let's make rich ❞

### 7.1 Cheap knobs (call-time monkeypatch)
| knob | attr | what it does |
|---|---|---|
| finisher_s1r_boundary_slip | FIN_S1R_SLIP | s1r offside tolerance at the s30 finisher |
| finisher_s30r_boundary_slip | FIN_S30R_SLIP | s30r near-boundary slip |
| finisher_s30r_near_dwell | FIN_NEAR_DWELL | s30r near-boundary hold |
| latch_depth | LATCH_DEPTH | s30M finishing-latch depth beyond OOB |
| latch_dwell | LATCH_DWELL | s30M latch hold |
| exit_tf_floor | EXIT_TF_FLOOR | option-1 counter-trend exit TF floor |
| delegate_offset | DELOFF | provisional delegate = max(floor, tf − offset) |
| delegate_tf_floor | DELFLOOR | delegate floor |
| wob_n | WOBN | provisional x−r cross wob count |
| anti | ANTI | s2r engage threshold |
| **xcp_tf_floor** | FLOOR | x-cross-pred look-back TF floor |
| **xcp_bnd_offset** | BND4 | x-cross-pred near-boundary threshold |

**xcp_tf_floor** — the sole mover of the first pooled sweep: 19 → 12 lifted minimax −0.810 → −0.498. Adopted (DB). [measured] floor 12 is a strict superset of 15/30 — lowering it *adds* valid flips, never swaps them.

**xcp_bnd_offset** — added on request:
> ❝ add the x-cross-pred threshold ❞
> ❝ I thought xcp_bnd_offset was measured in thousands ❞

Grounded: it's on the 0–100 oscillator scale (r within N of the 85/15 boundary), not thousands — the only ms-scale tolerance is `s1s2_confirm_tol_ms`.

**Not wired (measured, 0 refs in run_chain):** carry_ms, div_horizon_ms, div_net_min, override_latch_ms, s2_tf_sec, vmin. `retest_*` affect only `retest_scan` (0-delta on the flip metric). `gcs5_r_tol` is dead (never read since gcs5 went pure-latch).

### 7.2 Boundary (P-recompute)
hi_bound, lo_bound, fence_hi, fence_lo — feed `predict_breach` → baked P. `score()` recomputes P in place when a boundary knob is touched (90 vectorised calls; GPU-batched 12–18×), restores pristine P after.

### 7.3 Line params (per band, L0 rebuild)
Cycle groups: **s2-cycle {s1,s2}, s8-cycle {s3–s8}, HTF {s9+}**, each with its own r/x/m/M config; band edges (s2_top, s8_top) are swept.

> ❝ you might want to split the shared configs into their cycle groups, and dial them out ❞
> ❝ and sweep the cycle group's perimeters ❞
> ❝ a) yes to start with. if the sweep detects different TFs for the perimiters then the tests will need resweeping — b) all of them — c) yes ❞

Config key = `band.line.param` (tokens `mn`/`mj` for the m/M lines to dodge MySQL's case-insensitive collation). Adopted so far: s8/HTF `r.rsi` 5→4, s8 `m.length` 6→8 (−0.498 → −0.254).

---

## 8. Code evolutions (performance)

### 8.1 GPU / perf port
> ❝ there's gpu onboard - start working on a port ❞
> ❝ yes and yes ❞

RTX 3060 Ti, 8 GB, CUDA 12.8, cupy 14.1.1. Landed (all bit-identical):
- **cross_wob vectorised** — was a per-bar Python loop over 892k bars → `maximum.accumulate` run-length. **13×**. Live causal seam (o9-live benefits).
- **predict_breach** → elementwise (`pred_hi − pred_lo`) + xp-agnostic input coerce — batches over a (90,N) TF-stack, runs on cupy, no fork, no cupy import in the producer.
- **fx crossing masks precomputed** in `build_lines` (were rebuilt for all 90 TFs every `_climb_flip` call). run_chain **14000 → 5089 ms/window (2.75×)**, flips byte-identical.
- **GPU-batched P recompute** wired into the sweep's boundary path (f64 resident stacks, bit-identical, **12–18×**), CPU fallback so a GPU error can't kill the run. NB: measured that in the evo's line eval, **run_chain is 86% of the cost, build_lines 14%** — so scoping the L0 rebuild is not worth it; the cost is intrinsic to running real chains.

### 8.2 WSL memory
> ❝ how do we change the WSL limit? ❞

Host RAM 15 → 18 GB via `C:\Users\Administrator\.wslconfig` (`memory=18GB, swap=8GB`). The launcher is **Administrator** (whoami authoritative; ntuser.dat mtime misled first). GPU 999 MiB baseline = Windows host, not freeable from Linux.

### 8.3 DB-backed config
Knobs live in `rpl_config 'baseline'`; adopting a swept value = edit `rpl_seed_baseline.py` THEN RUN it to seed the DB (a .py edit alone is inert). Line-config adoption needs the per-band `_ovr` engine rework (held for Joe).

---

## 9. x-cross-pred — the tip of the sword

> ❝ thanks for upgrading x-cross-pred - it truly is the tip of the sword ❞
> ❝ I've been thinking about the threshold for x-cross-pred 4:int. I can't see how the complexitys of velocity and angles can be boiled down to a threshold carrying only 3 options ❞

[read] `xcp_bnd_offset` gates **position only** — no velocity/angle. [measured] shallow crosses are the losers (leg net −0.286% vs steep +0.056%; corr +0.16 — a FLOOR, not a fine score). **Steepness gate** (min |x−r| slope at the cross, cutting shallow grazes) is QUEUED for the next honing pass — a mechanism add, pairs with the positional gate + persistence.

---

## 10. wob suite — QUEUED

> ❝ do we have separate wob knobs for the full suite of lines: the 4 lines multiplied across the TF cycle groups ❞
> ❝ 100% ❞

[read] Today the line breaches (`oob_climb`, r≥boundary) are **instant, zero wob** across all TFs/groups; the only wob in the system is the delegate x−r cross (WOBN) + s30M latch (latch_dwell) + s30r near (near_dwell). Building **12 knobs (`wob_r/wob_x/wob_m/wob_M` × s2/s8/HTF)** = a mechanism add: replace instant breach with a wob-debounced breach, tunable per line per band. **INVARIANT: wob=1 must reproduce the instant breach bit-identical.** Aimed at the climb-leg MAE (s8-cycle breaches fire on first poke).

---

## 10b. `xcp_bnd_offset` — ROLLED BACK to 4, sweep it later (0728)

Tried manually at **5** on 06-13 (widening `near_ib` from `r > 81` to `r > 80`) to admit a genuine s89
exhaustion at 22:42:15 whose r was 80.4 — a 0.6-point miss. **It never reached it**: an earlier cross fires
first, so the widening bought nothing on that day and cost a trade.

The failure mode is the one to remember, because it is not a timing effect. Chain `0613_10` had **no
exhaustion at all** under `bnd 4` — a `release` chain firing on the bp50 A/B path. Widening the gate
**admitted an exhaustion at 23:20:05, flipping the chain from `release` to `takeover`**; the RPL path then
produced no finisher before its cap at 23:48:45, so the trade vanished. A gate loosening silently re-routes
chains between the two paths, and the destination path can fail where the source path succeeded.

**Rolled back to 4.** Already present in `rpl_knob_subset` (`ks_id 9`, values `[3, 4, 5]`, active) so the evo
sweep will explore it properly — with an OOS window rather than one day, and with the release/takeover
re-routing visible in the results. Do not hand-tune it again.

Detail + the full tried-and-rejected list: `docs/bp50.md` §10.6.

---

## 11. Honing roadmap (next pass, after convergence)

0. **before-MFE MAE** (§2.4) — confirmed.
1. **x-cross-pred steepness gate** (§9).
2. **12-knob per-band wob suite** (§10).
3. **`xcp_bnd_offset` sweep** (§10b) — rolled back to 4 pending a proper multi-window sweep.
4. **Dynamic subsets** — swap ≥3 knobs/evo (§4.1).
5. **Finer/smaller groups** — resolution up, groups ≈ cores (§4.2).

---

## 12. Pulse report format (Joe 0722–26)

The running sweep is monitored by a recurring interim **pulse** (cron `/loop`, ~15 min). It has a FIXED shape — retain it verbatim even when firing off-cadence. Terse throughout, MAE/MFE front and centre.

### 12.1 Lead — the MILESTONE framing (always first, mandatory)

> "Corner train hard; the val windows it FAILS on tell me where to build confluences." ADOPTION = **TRAIN MAE/MFE NET (MFE−MAE)**, advance only on positive net, else static. **Minimax + val = DIAGNOSTICS.**

### 12.2 MANDATORY MAE/MFE table + script-built KPI dashboard

- The **MAE/MFE table appears in EVERY pulse**, no exceptions, whatever the phase. Rows RC & RPL; cols `MFE | MAE | net(MFE−MAE) | val-net | val-mm`. Source: the latest `[HH:MM:SS] rN adopted MAE/MFE` one-liner + the latest `round N` line's `vnet`/`vmm`.
- The **KPI dashboard is SCRIPT-BUILT — never hand-built or hand-marked.** (The recurring failure was hand-highlighting cells that hadn't changed and omitting the formal dashboard.) Fire `python3 /home/joe/thecodes/build_kpi.py` and paste its stdout verbatim. Cols `leg | MFE | MAE | net(IS) | oos10 | oos7 | val-mm | maximin`, rows RC & RPL(climb).
  - **Sources, authoritative per cell:** MFE/MAE ← latest `adopted MAE/MFE`; net(IS)/oos10/val-mm ← latest `round N` (`tnet`/`vnet`/`vmm`); **oos7 = the clean disjoint-7 read from `rpl_oos32.o32_oos32`, latest WRITE (`ORDER BY o32_ts`, not round — an old run leaves higher-round rows in the same cycle)**; **maximin = `min(net, oos10, oos7)`** = the rotating-driver bank target, annotated `✅ (all +)` / `(split)` / `(all −)`.
  - **Per-cell change-highlight is automatic:** each cell is diffed vs the prior build (state file `/home/joe/thecodes/.rpl_kpi_state.json`) at 3-dp, so an unchanged value can NEVER spuriously light up; changed cells render `▲` (rose) / `▼` (fell), unchanged bare. First run after a state wipe = baseline (no glyphs).

### 12.3 Sections (terse)

§1 alive (PID, RAM/OOM) · §2 progress (latest `round N [phase k/10 line: PARAMS]`, adopted `tnet` gain/static, FLAG `⚠ NET REGRESSION`) · §3 OOS checkpoints (jump|periodic, IS vs OOS + gap vs `SYNC_TOL`, verdict `IN SYNC` / `IMBALANCED` / `OOS UNPROFITABLE` / `⚠ OOS REGRESSION` + candidate line drift) · §4 VAL soft spots (else fine-phase) · §5 cycle (number + IS days, `AGNOSTIC CONFIG FOUND`) · §6 centroid pool · §7 knobs & ranges (markers `▲` = live this round / `→ n` = holding centroid) · §8 messy windows · §9 APPENDIX failure-scan (the confluence work-list; **always caveat <4-trade windows as statistically thin — rank by net WITH a trade floor, not net alone**; note snapshot staleness vs current cycle/round).

### 12.4 MEAN, not median (pulse reporting)

The pulse **reports MEAN** MAE/MFE. This is deliberately distinct from the §2 scoring **objective** (`median(MFE − MAE)`, minimax over windows): §2 governs what the sweep OPTIMISES, the pulse REPORTS the mean for the human read. Do not conflate the two.

### 12.5 CLOSE — the "Net:" riff (mandatory)

Every pulse closes with a one-paragraph **"Net:"** — what actually moved this pulse, the honest read (over-corner / generalizing / bail / hold), any cross-thread aside, then a short sign-off. The editorial voice: measured, **non-defensive** (stay wary of the self-narrative — it's the trapdoor to bias). The same "Net:" muscle carries to off-pulse design riffs: lead with the finding, own the call, flag the cost.

---

## 13. Files

- `optimus9/orchestration/rpl_evo_sweep.py` — the evolutionary parallel sweep (the beast).
- `optimus9/orchestration/rpl_sweep.py` — the branching pooled sweep (superseded by the evo for the joint fixed point; still the boundary/P-recompute reference).
- `optimus9/orchestration/rpl_cache.py` — per-line cache (`cache_jig_perline`) + atomic writes.
- `optimus9/orchestration/rpl_walk.py` — the flip-chain engine (`run_chain`, `build_lines`, `_ovr`).
- `optimus9/orchestration/rpl_seed_baseline.py` — the DB config seed (run to adopt).
- Tables: `rpl_knob_subset`, `rpl_evo_group`, `rpl_evo`, `rpl_config`.
