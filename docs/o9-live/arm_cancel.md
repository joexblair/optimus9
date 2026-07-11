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

## s2Mage cancel-stay (Joe 0711, open A/B)
If `s2Mage` reverses toward `es` in the window after an opposite-side `s5m` breach, **stay** the cancellation
(the arm survives the twitch). `s2Mage = 60s, 37|0.72|hlcc4, emerging`, boundary-agnostic. `[measured]`
recovers exactly 13:55 and 18:57 (2 new, 0 lost, 5 baseline unchanged). `arm_cancel_ab.py`. Whether one
opposite breach is a real cancel or a twitch the arm should survive is Joe's verdict, pending.

## Why cancel-on-breach, not the permission drop
At `s5m = 8|0.65|ohlc4` the permission-cancel kills the hunt at seam 2 before `s5r` predicts (zero arms). The
book runs the opposite-breach cancel instead — see [arm_ladder](./arm_ladder.md#s5m-override--the-one-sanctioned-hardcode).
