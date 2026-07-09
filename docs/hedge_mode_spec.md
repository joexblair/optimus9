# fakeAPI hedge-mode conversion — spec (Joe 0708)

**Why.** Align the paper exchange with backtest potential: v2_walk books overlapping opposite-side legs (pseudo-hedge).
A one-way net can't hold both → the ~18% hedge-premium is unrealizable ([[project_backtest_hedge_premium]]). Hedge mode
holds **two independent legs** per symbol → the overlapping legs become real, closing the gap to backtest PnL.
Joe's call: **explicit `positionIdx`** (1=long, 2=short) — more control than reduceOnly-inference.

## The seam
Today the one-way net lives in `FxStore.open_position(symbol)` (one open row/symbol) + `MatchingEngine.submit`
(same-side→pyramid, opposite→reduce). Hedge mode = **key positions by `(symbol, position_idx)`**; each leg pyramids and
reduces on its own. SRP boundaries are unchanged — Store = persistence, Engine = arithmetic on the *addressed* leg.

## Changes

### Schema — `fx_position`
- Add `position_idx TINYINT NOT NULL` (1=long, 2=short). Two rows/symbol can be `status='open'` simultaneously
  (one per idx). Partial unique on `(symbol, position_idx)` where open.

### FxStore
- `open_position(symbol)` → **`open_leg(symbol, position_idx)`** (the only structural change; the one-way callers pass the idx).
- `create_position(..., position_idx)` — persist the idx. `grow_position`/`reduce_position` unchanged (operate on `position_id`).

### MatchingEngine.submit(symbol, side, qty, position_idx, reduce_only, ...)
Route by `position_idx`, decide grow-vs-reduce by **`reduce_only`** (not side-vs-net — the leg direction is fixed by idx):
- **`reduce_only=False`** → OPEN/ADD the addressed leg (create if none, else pyramid-reweight). Validate side matches leg
  direction (idx1↔Buy, idx2↔Sell).
- **`reduce_only=True`** → REDUCE/close the addressed leg, realize PnL. Realized direction is the **leg's** direction
  (idx1 long: profit when exit>entry; idx2 short: reverse) — read from `position_idx`, no longer inferred from the net.
- Validate closing side (idx1 closes Sell, idx2 closes Buy).

This is *more* explicit than today's inference and removes the "opposite side means reduce" ambiguity that hedge mode breaks.

### app.py (Bybit v5 contract)
- `/v5/order/create` — read `positionIdx` from body, pass to `submit`.
- `/v5/position/list` — return **both** legs (list ≤2), each with its idx.
- `/v5/position/set-leverage` — accept `positionIdx` (Bybit allows per-leg leverage). Stub still returns OK.
- (Optional) honour a position-mode setter; the mock can otherwise assume hedge mode always on.
- `/dev/reset` unchanged (TRUNCATE covers the new column).

## Client side (o9-live) — positionIdx belongs in the EXCHANGE ADAPTER, not the sizer
- **Keep `Order`/`PositionSizer` exchange-agnostic** (no `positionIdx` field). positionIdx is a Bybit-contract detail →
  the **fake (and real Bybit) adapter** derives it: open/add → idx by side (Buy=1, Sell=2); close/reduce → the held leg's
  idx + `reduceOnly=True`. SRP: sizing stays generic; the adapter owns the venue mapping.
- This is the ONE behavioural change o9-live needs for hedge mode; the risk logic (dynamic pyramid/leverage) is a
  separate spec ([[dynamic_risk_spec]]).

## Test/validation
- Unit: two legs open at once; each pyramids + reduces independently; realized PnL per leg correct both directions.
- Recon: replay a v2_walk window that books overlapping legs → fakeAPI holds both → realized PnL matches the
  hedge-premium-inclusive backtest (removes the ~18% haircut). See [[handover_o9live_reconcile]].

## STATUS (Joe 0708) — BUILT + validated, NOT deployed
- **Exchange side** (commit 8826016): schema+migration, FxStore.open_leg, MatchingEngine per-leg submit, app both-legs,
  BybitAdapter positionIdx. Tests green.
- **Client side** (commit 11fbcbb): StrategyLoop.intents = independent per-side legs (opposite entries open the other
  leg, no longer dropped); O9Ledger.record_close_side; O9LiveApp.position() both legs. Tests green (24 hedge-related).
- **Entry reconcile** (`reconcile_hedge_entries.py`, 30d): TRADES MATCH ✓ — hedge reproduces all 1953 static entries,
  0 drops; one-way was dropping **515 (26%)** overlapping legs = the premium. DATA: tape carries **2.7% V=0 synthetic
  filler** (known [[project_filler_invisible]] issue) — flagged; open question whether it shifts the entries (filler_invisible A/B).
- **Deploy gate:** o9_live untouched, no restart. Cutover = stop loop → `migrate_hedge_mode.py o9_live` → restart in
  hedge mode (natural home: the SG box). Re-derive `max_exposure_mult` from a hedge replay then ([[dynamic_risk_spec]]).
