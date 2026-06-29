# lr cascade — the latch-release reversal cascade (decoupled, configurable)

Status: BUILT + decoupled (0628→29). The SHAPE is code, everything else is data. **Re-spec'd 0629** off the
stale cf15 snapshot: **bias dropped from the cascade** (set upstream, no place here), **s2r restored** as a
clearance gate. This is the raw pl-cascade.

## The mechanic
**Slow arm → reversal → fast finisher, cleared by gate(s):**
1. **ARM** — an arm gate's line breaches OOB (closed) → armed, side = breach side. (seed: `s6m`, TF6.)
2. **REVERSAL** — the arm line's *emerging* value wobslay-reverses by ≥ `floor`.
3. **FINISHER** — any active finisher gate re-breaches on the same side. (seed: `s30a` = s30M&s30m OOB + s30r lookback-19, TF30s.)
4. **GATE** — all active gate clearances must pass to fire. (seed: `s2r` lookback-11, TF2 — same side; prevents the finisher triggering early.)

NO bias in pl-cascade — bias is set upstream. (The old `s14M` mid-vs-50 was a trial Joe disabled weeks ago that lingered in cf15 and got faithfully reproduced — the drift that triggered this re-spec.)

## SHAPE (code) vs DATA (config)
`optimus9/analysis/lr.py`:
- **`lr_detect(W, cfg)`** — THE STRATEGY = the state machine. Walks the gate-sets; emits entries only (SRP: no verdict baked in). Helpers: `_gate_side` (a gate's lines × `check`, combined by `op`) · `_finisher_active` (OR across finishers) · `_gate_ok` (AND across gate-role clearances).
- **`lr_walk(W, entries, cfg)`** — the BACKTEST verdict (MAE/MFE). Separate concern.
- **`lr_config(db) → LRConfig`** — the ONE loader: gate-sets + knobs + OOB. No hardcode.

**Data:**
- `lr_gate` (role[`arm`|`finisher`|`gate`] · name · op[AND|OR] · active) + `lr_gate_line` (ic_pk · check[`oob`|`lookback`|`mid`] · per-line `lrgl_lookback`). Lines by **ic_pk**. The `lookback` window auto-scales per line TF.
- **Per-line lookbacks** on `lr_gate_line.lrgl_lookback` (s2r 11 · s30r 19 · s15r 19; null → falls back to `lp_s30r_lb`). The exit overrides all to `lp_lr_exit_rlb`.
- knobs → `lp_config` (`lp_lr_floor/wob_n/horizon/target/swing_ms/swing_pct` + `lp_s30r_lb` default).
- OOB → `optimus9_system.hi/lo_boundary`. Every gate line read via `W.line` (value_mode-honoured, #42).

## One detect, three consumers (the event-stream discipline)
- **strat_review** — `lr_detect` IS the cascade producer (replaced the gate-chain TradeGateWalker). Reports the entries.
- **superscope / rig** — `lr_detect` + `lr_walk` (the MAE/MFE verdict).
- **o9-live** — `lr_detect` per 5s kline → the exchange (fills = the verdict).
`live == prod == backtest` by construction (same `lr_detect`).

## Configurable from the UI (no code)
The strategy page's cascade unfold renders the live `lr_gate` gate-sets (by role, active-toggle + op + lines) + the 8 knobs (edit-in-place). **Add a finisher = a row + a tick.** Proven: ticking the seeded-disabled `s15a` (TF15s finisher) → cascade fires s30a OR s15a (more entries); untick → back. Same for the `s2r` gate (tick to clear-gate the finisher).

## Notes / open
- **PnL ground rule (0629):** no $ / PnL figures discussed without a stop loss applied — winners-only ceilings are banned (they're what masked the entry problem). So this doc carries counts, not $.
- **s2r role:** a `gate` (clearance) *for now* — Joe's open question is gate vs arming mechanism. Same-side `lookback`-11.
- **Structural constants** (not knobs): `//5` base-kline (5s), `×100` %-conv.
- **Follow-ups:** line-membership editor (add/remove lines + swap ic_pk per gate — UI shows lines read-only); `trade_gate` dead → sunset (#30); add `lr_gate`/`lr_gate_line` to `o9_live_schema.sql` when wiring o9-live; `seed_lr_gate.py` to be reconciled with the 0629 re-spec (migration in `migrate_lr_pl_cascade.py`).

Build: `seed_lr_gate.py` (tables + seed) · `seed_lr_config.py` (knobs).
