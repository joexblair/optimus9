# Arm-delay spec 0709 — the book, and what is and isn't real (0710)

Tools: `arm_walk.py` (the walk) · `arm_case.py` (one hunt) · `arm_batch.py` (a window) · `arm_seq.py`
(deduped arms + MAE/MFE) · `arm_trade.py` (the full flow) · `arm_days.py` (N days) · `arm_sweep.py`
(one knob, worst-day scored) · `arm_filters.py` (post-hoc filters).

All reads go through `optimus9.analysis.jig`. Prediction is `predict_breach` with an explicit `tol`
(default `0.0` = the spec). Nothing hand-rolled.

## The flow as built

```
HUNT      an s5m IB->OOB crossing at a 300s seam.  s5m = bb 8|0.65|ohlc4, emerging
          (Joe named the value 0710; it is the ONE hardcoded config, pending a sweep into indicator_configs).
apex      starts at TF5.  Climbs only AT the apex's r coarse curl, when the TF above has predicted or breached.
curl seam TF/div, banded: tf<=7 -> TF/2 · 8..14 -> TF/4 · >14 -> TF/6
ARM       LATCH, no expiry: the apex's r and the TF above are both OOB and both have curled.
          (`htf-quiet` is a no-op — keep walking.)
GATE      lr_v2.gate_open (reasons a / b / c) from the arm bar.
FINISHER  lr_v2.s_qualify (s15a, s30a) -> fin_gate.  The trade bar.
TP        scan up from the arm TF until an r is not OOB; the last OOB TF is the TP TF.
          Follow that TF's mini to the far side; exit on its first reversal while OOB there.
```

## The 9-day book

`[measured]` 2026-07-01 .. 2026-07-09, 292 arms, cost 0.20% round-trip.

```
producer=arm     (no gate, no finisher)   -0.1180%/trade  win 54.5%  gross +0.0820%  days+ 4/9
producer=gate    (gate + finishers)       -0.0296%/trade  win 63.0%  gross +0.1704%  days+ 5/9
```

The gate + finishers add **+0.088%/trade and +8.5 points of win rate**, and they help on all nine days.
Both books still lose to cost: gross `+0.17%` against `0.20%`.

Per day (gate):
```
07-01  -0.3161%   07-02  -0.2021%   07-03  -0.0421%   07-04  +0.0648%   07-05  +0.0167%
07-06  +0.0357%   07-07  +0.0367%   07-08  +0.2099%   07-09  -0.1043%
```

Apex distribution, 292 arms: `TF5 x108 · TF6 x117 · TF7 x47 · TF8 x9 · TF9 x7 · TF10 x2 · TF11 x1 · TF12 x1`.

## REFUTED — do not re-propose

- **The `MFE@10m` bail.** Every `(N, X)` cell is worse than doing nothing. `N=10m X=0.20%` takes the book
  from `-0.0296%` to `-0.0630%` and days-positive from `5/9` to `2/9`. It was derived from the
  negative-gross rows — a set selected on outcome. It cuts the slow winners.
- **"`tpTF == apex` warns of a dead move."** Backwards. Trades where the ladder above the arm *was*
  awake do WORSE: `tpTF > apex`, n=50, `-0.0918%/trade`, worst day `-1.4121%`.
- **`cap` as a lever.** `cap=30` scored `+0.506%/trade at 100% win` — entirely a survivorship bug in
  `arm_trade.py`: a trade whose exit never fired inside `cap` was *dropped from the book*. With the
  guard (mark to market at `cap`), `cap=30` is `-0.0192%` at 53.6% win. `cap` does nothing.

## The one filter that survives

```
apex TF >= 6   n=184  -0.0221%  win 65.8%  days+ 6/9
apex TF >= 7   n=67   +0.0499%  win 70.1%  days+ 6/9   worst day -0.4687%   gross +0.25%
apex TF >= 8   n=20   -0.0364%  win 65.0%  days+ 4/8
```

The only positive cell in the filter table. It is not "higher is better" — TF8+ turns negative again.
67 trades over 9 days. **Untested out of sample.**

## Open

- Does `apex >= 7` hold on 20+ days?
- `lr_exit_v2` vs the far-side-mini TP.
- The `m_len` / `m_mult` / `tol` / `bands` sweeps (worst-day scored).
- The stale hunt: with no cancel, a hunt from 18:45 armed at 21:00 on lines that had nothing to do with
  it. `s5m` in-bounds for N consecutive seams is the natural bound, and it is one knob.
- `docs/emerging_bar_open.md` — one in five OOB crossings lands on the higher-TF bar open. Every
  round-number timestamp in this work sits on one.
