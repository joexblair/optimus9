# bl_review — alchemy-mode BRD (the trading-solution melding ground)

**Status:** Define/Scope (0626). Captures Joe's BRD verbatim-in-intent + interrogation. NOT yet built —
open questions below must resolve first.

## Why / the goal
We're in **alchemy mode**: melding the moving parts into a trading solution. bl_review is re-jigged **in
stages** to reach one clear number — the **total PnL of every `xm45m`-wob-initiated trade**. Layers of
gates integrate into bl_review so only the **correct** xm45m wobs are left **ungated** → a trade is created.

## Design philosophy (the unlock)
We do NOT try to capture the exact reversal moment to trade it — that was the long, stressful dead-end.
Instead: **bias sets the scene** (strong line reversals = strong market opposition = the trend state),
and a *separate* mechanism — **lp cascade** — rides the wave. SRP at the strategy level: bias has one job
(direction/scene), lp cascade has one job (entry/ride). The two together do effortlessly what one
mechanism strained to do. The strategy is, in a way, self-managing.

## The trade model
- A trade is **created** in bl_review when an xm45m wob survives all gates.
- The trade **exits via a process outside this BRD** (the exit machine — separate). Its **PnL is recorded
  on the xm45m wob row that initiated it.**
- End result: a **chronological view** of the actions that allowed a trade to fire + the data to
  understand profitability (PnL on the wob rows).
- **The feedback loop:** we read the report — **especially the stop losses** — to find and improve gaps
  in the gate machines. A bad stop = a gate that should have blocked that trade.

## Gate architecture
Gates layer in front of the xm45m wob. An xm45m wob that fails any gate **prints no row** (it never
became a trade). **Gate layering lives in DB table(s)** (the `trade_gate` mechanism) — **bl_review is
simply the OUTPUT of strategy creation**, not where gates are hand-coded. Staged integration; measure PnL
after each gate lands.
- **Per-gate `is_active` flag** (the existing `tg_active` pattern): each gate row toggles on/off in the DB
  → stage gates in/out and A/B them without code. "Add a gate = a row; toggle = a flag."

### Gate — lp cascade (the gate CLOSEST to xm45min wob)
The real entry cascade (a version of the test cascade, NOT scaffolding): **`s6m → xm45a → gcs15a →
xm45min wob`**. It is the **last** gate before the wob fires. The other gates (bias, etc.) sit in front
of it. The **gravity** producer's reversal trigger + bias update **pass THROUGH the lp cascade** — the
actual *moment* of both the reversal trigger and the bias update is **at the xm45m wob** (the cascade's
final stage), not at the gravity-detection bar.

## Gate 1 — the bias machine (DIRECTION gate)
Bias controls the direction a trade can be placed: **an xm45m wob CANNOT fire against bias** → no row.
The bias machine is a **composite**: it consumes direction events from several producers, all feeding the
agnostic `BiasState` (most-recent-wins). Producers (each = its own SRP unit, the #37 work-list):

- **bias pk** — BUILT, proven (`pk_bias_events`). Advises bias state.
- **bias lp bro-cross** — BUILT, mostly proven (weave-cease emerging cross, n=6, OOB-gated,
  `cf_bro_emerg`). Advises bias state. ← wiring this in is the current task.
- **bias lp gravity** — a slow BB **hangs back** while a fast BB + fast K breach the **opposite** side
  (e.g. `s22Mage=80, s14m=−5, s14r=12`). Statistically → a reversal + a bias flip. **Dual-output**
  (reversal trigger + bias update), but **both pass THROUGH the lp cascade** and *realize at the xm45m
  wob* — not at the gravity-detection bar.
- **bias bl-state-change** — fires on a flip **to 1** AND a flip **to 3** (prediction-captured breaches
  produce the same bls:1). Polarity (RESOLVED): **flip-to-1 → bias = `breach_dir`** (momentum into the
  breach); **flip-to-3 → bias = `−breach_dir`** (the reversal). Table: HI→1 BULL / HI→3 BEAR / LO→1 BEAR /
  LO→3 BULL. Extends the current `bls3_bias_events` (which only did →3) with the →1 momentum half.
  - **State 2** (curl): no bias impact. **Re-engage 3→1**: follows the flip-to-1 rule → a fresh bias update.
  - **Line: `s22r` only** (support `s14m`) — no others needed; LTF lines would poison the bias.
  - **Why it works (the key insight):** s22r is slow, so its breach (often mid-leg, or prediction-captured)
    = the trend is *established*. Two payoffs: (1) headroom to still grab a ~0.9% momentum trade, (2) the
    important one — it snaps bias to the **correct trend state, overriding errant pk bias** that fights the
    trend. Merge stays **most-recent-wins** for now (no weighting — the data flows naturally; #40 reopens
    it if errant pk re-overrides).
- **bias neutral mechanic** — TBC. Disables trade entry during **transition** periods (e.g. `hb16min`
  OOB and waiting for an lp-weakness decision).
- **bias FIFO** — TBC.
- **bias lp weakness** — TBC.

## Staging (proposed — confirm order)
1. **Wire the bias seam** [Open Q4]: bl_review's `bny30_bias` must read `BiasState`, not the old stored
   `bl_states.bny30_bias` (`bny30_latched_bias` in bl_detect). Today only alchemy_report feeds BiasState;
   bl_review reads the legacy column. *Lean:* migrate bl_detect to source bny30_bias from BiasState (one
   source of truth, completes #32).
2. **Bias gate v1** = pk + bro-cross producers → direction gate on xm45m wobs → measure trade PnL.
3. Add **gravity**, then **bl-state-change** producers (each a stage; re-read PnL/stops).
4. The **TBC** mechanics (neutral, FIFO, weakness) as they're specced.

## bl_review schema changes (this task)
- New row on a bias state change: `event = 'bro_x_bias'`.
- Rename `bb_main` → `bb_mage`; add `bb_min`. [Open Q5: for `bro_x_bias` rows = the bro mage/min values;
  for existing BL rows, `bb_mage` = old `bb_main` (exit_support), `bb_min` = null? Confirm generalization.]
- **`bny30_bias` retired** ("Barny's done his work — pasture"). New column **`bias_state`**, sourced from
  **`BiasState`**. The legacy `bny30_latched_bias` path is no longer read by bl_review. (Resolves Q4.)

## Open questions — ALL RESOLVED (build-ready)
- Q1 gates = DB tables (+ per-gate `is_active`); bl_review = output.
- Q2 gravity through cascade, realizes at wob.
- Q3 bl-state-change polarity (both transitions, s22r-only, most-recent-wins; #40 reopens weighting).
- Q4 bny30 → `bias_state` column from BiasState.
- **Q5** — `bb_mage`/`bb_min` = the source-relevant pair: `bro_x_bias` rows → bro mage/min; existing BL
  rows → `bb_mage` (old `bb_main`/exit_support) + `bb_min` null.
- **Cluster** — bro-cross suppresses **same-direction only** within 30 min (an opposite signal = a real
  reversal = new cluster, fires immediately). NOT a flat 30-min suppress-all.
- **N** = **6** — `lp_bro_wob=6` (set 0626; the winner, fires ~30s earlier, aligns with s6a + xm45m wob).

## Build stages (Decompose — build-ready)
1. **Seam:** bl_review `bny30_bias` → new `bias_state` column sourced from `BiasState`.
2. **Bias gate v1:** producers pk + bro-cross → direction gate on xm45m wobs → measure trade PnL/stops.
3. Add **gravity**, then **bl-state-change** (s22r) producers — each a stage, re-read stops.
4. **TBC** mechanics (neutral, FIFO, weakness) as specced.
Each gate = a `trade_gate` row + `is_active` flag (stage/AB without code).

See [[project_bias_meld]] (TradeGateWalker), [[project_bias_machine]], [[bias_machine_eval_constraints]],
docs/bias_mechanics_design.md (#37 producer mechanics).
