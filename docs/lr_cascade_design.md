# lr cascade — the latch-release reversal cascade (decoupled, configurable)

Status: BUILT + validated (0628→29). The validated cf15 mechanic, promoted to prod and fully decoupled —
the SHAPE is code, everything else is data. Reproduces cf15 exactly (rig 131 · superscope 1019/61%/$23,326).

## The mechanic
**Slow arm → reversal → fast finisher, gated by bias:**
1. **ARM** — an arm gate's line breaches OOB (closed) → armed, side = breach side. (seed: `s6m`, TF6.)
2. **REVERSAL** — the arm line's *emerging* value wobslay-reverses by ≥ `floor`.
3. **FINISHER** — any active finisher gate re-breaches on the same side. (seed: `s30a` = s30M&s30m OOB + s30r liftoff, TF30s.)
4. **BIAS** — all active bias gates must agree (gates the finisher). (seed: `s14M` mid vs 50, TF7.)

## SHAPE (code) vs DATA (config)
`optimus9/analysis/lr.py`:
- **`lr_detect(W, cfg)`** — THE STRATEGY = the state machine. Walks the gate-sets; emits entries only (SRP: no verdict baked in). Helpers: `_gate_side` (a gate's lines × `check`, combined by `op`) · `_finisher_active` (OR across finishers) · `_bias_ok` (AND across bias gates).
- **`lr_walk(W, entries, cfg)`** — the BACKTEST verdict (MAE/MFE). Separate concern.
- **`lr_config(db) → LRConfig`** — the ONE loader: gate-sets + knobs + OOB. No hardcode.

**Data:**
- `lr_gate` (role · name · op[AND|OR] · active) + `lr_gate_line` (ic_pk · check[`oob`|`liftoff`|`mid`]). Lines by **ic_pk** (bias-producer tagging convention). Liftoff lookback auto-scales per line TF.
- knobs → `lp_config` (`lp_lr_floor/wob_n/horizon/target/swing_ms/swing_pct/bias_mid` + `lp_s30r_lb`).
- OOB → `optimus9_system.hi/lo_boundary`. Every gate line read via `W.line` (value_mode-honoured, #42).

## One detect, three consumers (the event-stream discipline)
- **strat_review** — `lr_detect` IS the cascade producer (replaced the gate-chain TradeGateWalker). Reports the entries.
- **superscope / rig** — `lr_detect` + `lr_walk` (the MAE/MFE verdict).
- **o9-live** — `lr_detect` per 5s kline → the exchange (fills = the verdict).
`live == prod == backtest` by construction (same `lr_detect`).

## Configurable from the UI (no code)
The strategy page's cascade unfold renders the live `lr_gate` gate-sets (by role, active-toggle + op + lines) + the 8 knobs (edit-in-place). **Add a finisher = a row + a tick.** Proven: ticking the seeded-disabled `s15a` (TF15s finisher) → cascade fires s30a OR s15a → 131→134 trades; untick → 131.

## Notes / open
- **s14M value_mode**: the decouple exposed the old code reading s14M closed (`W.s14M`) while s30 was emerging. Set s14M → closed (single-job line). A/B closed-vs-emerging = **task #43** (emerging gave 135 / 1045 / $24,450, slightly higher).
- **Structural constants** (not knobs): `//5` base-kline (5s), `×100` %-conv.
- **Follow-ups:** line-membership editor (add/remove lines + swap ic_pk per gate — the UI shows lines read-only for now); `trade_gate`/`s2r` fully dead → sunset (#30); add `lr_gate`/`lr_gate_line` to `o9_live_schema.sql` when wiring o9-live.

Build: `seed_lr_gate.py` (tables + seed) · `seed_lr_config.py` (knobs).
