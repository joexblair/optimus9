# o9-live dynamic risk — RiskGovernor spec (Joe 0708)

**Why (Joe's words).** "Risk protects the bank at all times — we should be able to dial up the risk factor as we learn."
The live pyramid ran unbounded (~40× peak, gives back on a tail). Two levers: **dynamic pyramiding** (scale + gate the
adds) and **dynamic leverage** (drawdown + vol to start). Both are *strategy-side risk*, distinct from the exchange
([[hedge_mode_spec]]) and from signal generation.

## SRP: a NEW single-responsibility class, not an extension
Risk assessment is its own responsibility. It must NOT be baked into the sizer or the strategy:
- **StrategyLoop** keeps DECIDING — emits `open`/`add`/`close` intents (unchanged).
- **PositionSizer** keeps SIZING — turns an intent + a *given* factor into orders (unchanged shape; today `leverage` is a
  constant ctor arg — the governor will supply it per-bar instead).
- **RiskGovernor** (new) — given account + market state, returns a **RiskVerdict**. It computes; it does not decide, size,
  or execute. It feeds the sizer (factor) and gates the add-intent stream.

```
intents (decide) ──▶ RiskGate.apply(verdict, intents) ──▶ sizer.size(intent, factor) ──▶ adapter ──▶ exchange
                          ▲
        RiskGovernor.assess(equity, drawdown, vol, open_exposure, context) ──▶ RiskVerdict
```
The `RiskGate` step is a thin seam between decide and size: it drops vetoed adds and stamps each surviving intent with the
factor. An A/B "governor on/off" is then a real fork (feed vs not), never a fused branch.

## RiskVerdict (the contract — event, not baked)
- `leverage_factor: float` — replaces the sizer's constant `leverage` (dynamic leverage).
- `add_allowed: bool` — pyramid gate (veto new adds).
- `max_exposure: float` — the total-exposure cap the hedge-mode realization needs ([[project_o9live_desync_fix]]).
- (extensible — new risk outputs are new fields, consumers read what they want.)

## Dynamic leverage — drawdown + vol (start)
- `leverage_factor = base_appetite × f_dd(drawdown) × f_vol(vol)` — deleverage as drawdown deepens / vol spikes (protect
  the bank), lever up in calm/low-drawdown. Curve shape is **config/DB-sourced**, never hardcoded.
- **`base_appetite` is the single "dial up as we learn" knob** (one DB value scales the whole curve).

## Dynamic pyramiding — scale + gate
- **Scale:** adds inherit `leverage_factor` → smaller adds under stress (rides the same sizer path).
- **Gate:** `add_allowed=False` when `open_exposure ≥ max_exposure`, or under drawdown/vol kill-thresholds. The gate is
  applied to the *intent stream* at `RiskGate`, not inside strategy's signal logic (SRP — strategy still emits the add).
- **Bank floor:** `max_exposure` is a hard cap + a deep-drawdown deleverage/halt — "protects the bank at all times."

## Future hook (Joe's item 3 — DON'T build now, leave the seam)
Leverage will later weight by **line positioning + fib** (a trade at the top of a large potential leg gets more leverage
than a small swing). So `assess(..., context)` takes an optional `context` (line-position / fib read) that today
contributes a neutral 1.0. The fib/line reader is a shared future substrate with [[fib_error_close_spec]] — build once,
consume twice. Seam only now; no fib logic yet (self-watchdog: future = future).

## Config / DB (never hardcode)
- `base_appetite`, `f_dd`/`f_vol` curve params, `max_exposure`, drawdown window, vol measure → all DB-sourced (extend
  `lp_config` or a `risk_config` table). The governor holds no literals.

## RESOLVED — medium baseline, locked in `risk_config` (Joe 0708)
All values live in the `risk_config` (name, val, note) table — the governor holds no literals. `insert_risk_config.py`
seeds them; tune with `UPDATE`, no code. The five forks, decided:
1. **Exposure unit** → **equity-multiple** (`max_exposure_mult`). Self-scales with the bank.
2. **Drawdown reference** → **high-water peak, realized + open-leg MtM** (`dd_ref=hwm_mtm`) — reacts before the stop fires.
3. **Vol measure** → **s30 BB-band width, normalized vs a 500-bar window** (`vol_source=s30_bbw`, `vol_window`) — reuses an
   existing line; coarse = steady.
4. **Curve shape** → **hard step-thresholds** (`dd_step1/2`, `dd_halt`, `vol_hi_*`) — legible while dialling in.
5. **Stress response** → **taper then veto** (`add_mode=taper`) — adds shrink by the factor; hard-veto only at the cap / halt.

### The cap is DATA-DERIVED (not a guess)
`risk_stack_dist.py` replayed the shipping producer (v2_walk_ad) through the one-way pyramid model over 30d / 893 episodes:
**60% single-leg; median 1.5×, p90 5.8×, p95 10×, p99 16.5×, max 30×** gross exposure; pyramid depth p99 = 5 adds, max 7.
`max_exposure_mult = 16.0` (p99) clips the 16–30× runaway tail, leaves 99% of productive episodes untouched, and keeps
headroom for hedge legs. **CAVEAT: one-way understates hedge gross — re-derive from a hedge replay once [[hedge_mode_spec]]
lands.** Tighter alternative if we want more protection: 10× (p95).

`base_leverage=5.0` (validated dynamic5x) and `base_appetite=1.0` (the master "dial up as we learn" scalar) stay the
untouched money-making path — the governor only *deleverages/gates under stress and caps the tail*.

## STATUS (Joe 0708) — BUILT + tested, NOT wired
- **`optimus9/live/risk.py`** — `RiskGovernor.assess(equity, drawdown_pct, vol_pctile, open_exposure_mult) → RiskVerdict
  {leverage, open_allowed, add_allowed, max_exposure, reason}`; `RiskGate.apply(verdict, intents)` drops vetoed opens/adds,
  closes/reduces always survive. Reads risk_config (no literals). 8 tests green (`test_live_risk.py`).
- **Thresholds are ALL v2_walk-grounded now** (`risk_stack_dist.py` + `risk_drawdown_dist.py`): cap 16× (stack p99);
  `dd_step1=2.0%` (equity-drawdown p90), `dd_step2=3.5%` (p95). My earlier hand-picked 5/10/15% were too loose
  (5% ≈ p97 → would rarely fire). `dd_halt=10%` is the ONE non-derivable value — a **risk-appetite knob** placed in the
  p95→p99 gap (3.5%→21%) to catch runs before the fat tail; the taper (×0.25 by 3.5%) already bleeds the bank slowly, so
  halt is a backstop. Tighter = more protective / cuts more recoverable runs (backtest recovered from 33% unchecked);
  looser = rides more / risks deeper damage.
- **NOT wired into `on_bar` yet** (deploy step). The wiring layer must compute the three inputs:
  - `drawdown_pct` — needs a **high-water tracker** on `o9_account` (currently holds equity/realized_total, not peak) →
    `(hwm − (equity + open-leg MtM)) / hwm`.
  - `vol_pctile` — s30 band width over `vol_window` bars, percentile-ranked (from the BiasWindow).
  - `open_exposure_mult` — Σ open-leg notional / equity (from the exchange positions).
  Then: `intents → RiskGate.apply(verdict, ·) → sizer.leverage = verdict.leverage → execute`. Changes live behaviour →
  Joe's go, at the hedge cutover ([[hedge_mode_spec]]).
