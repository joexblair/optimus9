# Arm cancel — opposite s5m breach + the s2Mage cancel-stay

> [o9-live arm-delay spec](./README.md) · **causal / emerging-only**, every read via the jig.
> `arm_report.cancel_bar` · `arm_cancel_ab.py`.

The arm's natural life ends at the **next opposite-side `s5m` breach** (a HI breach cancels a long arm and
vice-versa). No fixed deadline.

- The old **no-prediction cancel** (`s{apex}m returns IB without an r prediction`) is **dead code** once
  permission is checked at the prediction seam; `cancel_on` (apex vs s5m) is a dead fork (16/17 hunts are
  still TF5 at cancel, so `s{apex}m` *is* `s5m`).
- An **opposite-side ARM** would be a stronger cancel than the breach — but `[measured]` one never arrives
  while a position is open (the TP always fires first); skip/flip/close policies are byte-identical. Nothing to
  cancel. (Open idea, not adopted.)

## s2Mage cancel-stay (Joe 0711, CANONICAL)
If `s2Mage` reverses toward `es` within `stay_win` (=60 bars = 300s) after an opposite-side `s5m` breach,
**stay** the cancellation (the arm survives the twitch) — skip that breach and test the next. `s2Mage = 60s,
37|0.72|hlcc4, emerging`, boundary-agnostic; the stay reads `causal.reversal(s2Mage, wob=1)`. **Baked as the
default cancel** in `arm_report.py` (`--cancel stay`, default; `--cancel base` reverts for A/B). `[measured]`
last 24h vs baseline: 2 NEW (13:55 MFE 2.93, 18:57 MFE 1.29), 0 LOST, 5 unchanged; MAE p50 0.06→0.07. Purely
additive — a stayed arm is a superset of the baseline's life, so it can't kill a baseline trade.

**Observed stickiness (open):** raw wob=1 `s2Mage` flips often, so within 300s of almost any opposite breach it
has a toward-`es` reversal → the stay skips most breaches and a **non-trading** arm runs to a non-stayed breach
or tape-end (arm→cancel MAE/MFE 2–5% vs ~0.2% under `base`). Trades are unaffected (the 6of9 fires long before
the far cancel), but this is the [stale-hunt hazard](./arm_ladder.md#stale-hunt-hazard-open) in a new place —
a coarse-curled `s2Mage` (vs the raw slope-flip) is the likely tightening.

## Why cancel-on-breach, not the permission drop
At `s5m = 8|0.65|ohlc4` the permission-cancel kills the hunt at seam 2 before `s5r` predicts (zero arms). The
book runs the opposite-breach cancel instead — see [arm_ladder](./arm_ladder.md#s5m-override--the-one-sanctioned-hardcode).
