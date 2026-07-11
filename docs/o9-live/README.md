# o9-live — arm-delay system spec

The strategy o9-live must implement, one doc per logical group. Goal (`handover_o9live_reconcile`):
backtest profitable ⇒ make o9-live MATCH it.

**Ground fact — causal / emerging-only** (`project_v2_lookahead`): a realtime engine only ever sees the
forming value; closed is the look-ahead that killed the live account. Never "use closed to match TV". **TV is
the source of truth**, synced on the *emerging* value, not by switching to closed. Every read goes through the
jig — no hand-rolled prediction, no hand-rolled curl, no hand-built line tuples.

**Sign convention** (Joe, confirmed): `es` = entry-side sign of the hunt, `bd` = trade direction = `−es`.
- `es = +1` → hunts a HIGH breach → `bd = −1` → **SHORT**.
- `es = −1` → hunts a LOW breach → `bd = +1` → **LONG**.

**Headline (20 days, 669 trades, day-block bootstrap):** gross mean **+0.1154%/trade**, 95% CI [+0.0409%,
+0.1799%], **P(gross>0) = 99.8%**, gross>0 on 70.3% of trades. A real edge, **smaller than the 0.20% cost**.
Break-even needs cost ≤ 0.1154%. Every price overlay and filter tested loses OOS; **maker fills are the only
lever that closes the gap without touching a signal.**

## Docs
1. [Arm ladder](./arm_ladder.md) — the hunt, the climb, the two-stage latch, the s5m override.
2. [Prediction & curl](./prediction_and_curl.md) — `predict_set`, the `tol` knob, the banded curl divisor.
3. [Finisher — the 6of9](./finisher_6of9.md) — qualifier vs trigger, the 9 = 3×3, breach vs oob anchor.
4. [Take-profit](./take_profit.md) — the exit-direction pipeline, 6of9 over fin_gate, the backstop.
5. [Arm cancel](./arm_cancel.md) — opposite s5m breach + the s2Mage cancel-stay.
6. [Jig API](./jig_api.md) — the one legal source; every primitive the machine reads.
7. [Tape & value hazards](./tape_hazards.md) — bar-open sawtooth, filler-invisible, ARM-DRIFT convergence.
8. [Cost & edge](./cost_and_edge.md) — the cost model and everything tested-and-killed.
9. [Constraints & open items](./constraints_and_open_items.md) — standing rules and the live fork list.

## Code
- `arm_walk.py` (repo root) — the reusable causal ladder (`Board`, `walk`, `tp_tf`, `take_profit`,
  `take_profit_ad`, `S5M_OVERRIDE`).
- `optimus9/analysis/lr_v2.py` — `fin_box_qualified`, `fin_unlatch_nof9`, `fin_unlatch`, `s_qualify(_parts)`.
- `optimus9/analysis/jig.py` — `causal.*` (live-legal) and `score.*` (harness).
- `optimus9/compute/breaching_line.py` — `predict_breach(..., tol=0.0)`.
- Producers/reports: `arm_trade.py`, `arm_report.py`, `arm_cancel_ab.py`, `arm_sweep.py`.
- Related: `finisher_lookback_spec.md`, `emerging_bar_open.md`, `arm_drift_rootcause.md`,
  `causal_lookahead_register.md`.
