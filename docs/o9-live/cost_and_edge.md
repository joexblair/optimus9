# Cost & edge

> [o9-live arm-delay spec](./README.md) · **causal / emerging-only**.
> `ledger.py`, `arm_sweep.py`.

## Cost model
VIP0 fees taker **0.055%/side**, maker **0.020%/side** (`ledger.py:58`, `taker_bps=5.5` = fee, not slippage);
slippage **~3.35 bps/side**. Break-even **0.1154%** (CI 0.0409–0.1799).

```
fill          fees    slip    cost     net mean     verdict
taker/taker  0.110%  0.067%  0.177%   -0.0616%     loses
taker/maker  0.075%  0.034%  0.108%   +0.0069%     ~break-even
maker/maker  0.040%  0.000%  0.040%   +0.0754%     wins clean
harness EST                  0.200%   -0.0846%
```

Read the book with a ~18% hedge-premium haircut for one-way planning. **Maker (post-only) entry is the only
lever that closes the gap and changes no signal** — needs a fill-probability model (a resting bid that never
fills = a missed trade). Deferred, Joe's call.

## The edge (20 days, 669 trades, day-block bootstrap)
Gross mean **+0.1154%/trade**, 95% CI [+0.0409%, +0.1799%], **P(gross>0) = 99.8%**, gross>0 on 70.3% of
trades. A real edge, smaller than the 0.20% cost. The s3s4 gate + finishers add **+0.088%/trade and +8.5 win
points on every one of 9 days** (kept). Reports run **without s3s4** while Joe tames the arm events for it
("without s3s4 is perfect"); the 21 ARMED-not-qualified arms are the taming target.

## Tested and killed (don't re-propose without new data)
- **`apex >= 7` filter** — +0.0499% on 9 days, **−0.0581% on 20 days.** Every filter flips sign OOS; 9 days was
  a lucky slice.
- **`MFE@10m` bail** — worse in every (N,X) cell; derived from an outcome-selected set.
- **`tpTF == apex` warning** — backwards and sign-flips OOS.
- **`cap` as a lever** — the "100% win at 30 min" was a **survivorship bug** (`arm_trade.py:112` dropped
  unresolved trades instead of marking to market); guarded, the effect vanished. Then Joe: caps deleted
  entirely.
- **Every hard stop loses** — none +0.1154%; the worst 5% drag the mean −0.1487% but stopping costs more than
  they take. Same as `project_exit_curl`. Price overlays are catastrophic on this book.
- **`lr_exit_v2`** — same mean as the interim TP, 15 pts worse win, worse worst-day, holds 2× longer.
- **Knob sweeps flat** — `m_mult` 0.44–0.62, `bands`, `tol`, `m_len` all span +0.145% to +0.177% gross; none
  reaches the 0.20% cost.
- **Pyramid legs are KEPT** — 20 legs 65% win gross +0.2713% vs 44 masters 45.5% gross +0.1571% (a leg = a
  second same-side arm while the first is open = confirmation, prices closer to the turn). Disabling pyramids
  worsens the book. But two days disagree in sign (n=10/side/day) — real but not yet leanable.
