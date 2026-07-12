# trade_book — the per-trade record (0711)

`trade_book.py` → table `trade_book` (prefix `tb_`, cfg tag `ship_0711`), 158 trades / 62 days.
Supersedes `two_path_trades` (11 columns, aggregate-and-discard). **Every slice is now a query, not a
40-minute re-run** (ci_initiatives: "Persist the rows, never just the aggregate").

Config: T4 stack-climb arm on the 10..25 ladder · r = close|k_len 8|rsi 6 · divergence L24 K2 ·
exit rung 5 (`es5`). Causal, no caps. Every read via the jig.

## Standing rules set by Joe, 0711

- **NO net / PnL in any report until further notice. Every report is MAE and MFE.**
- **No sweeps until the bias machine is built and applied.** Every knob swept so far was fitted to
  whichever regime the window landed in. Sweeping now measures the market, not the machine.
- **Findings must be tagged** `[measured]` / `[read]` / `[inferred]`.
- Duplicates are **noted, not deleted** — `tb_n_arms` keeps convergence visible as data.

## Columns (39)

| group | columns |
|---|---|
| hunt → arm | `hunt_dt` `hunt_tf` `arm_dt` `apex_tf` `cancel_dt` `n_arms` `arm_mae` `arm_mfe` |
| gate → trade | `gate_dt` `gate_kind` (a/b/c/div) `hunt_arm_s` `arm_trade_s` `gate_trade_s` `held_s` |
| trade | `trade_dt` `side` `paths` `entry_px` `mae` `mfe` `mae_s` `mfe_s` `mfe_first` |
| exit | `exit_dt` `exit_px` `exit_kind` (arm/backstop/cap) |
| post-exit | `post_mae` `post_mfe` — 60 min past the exit. **DIAGNOSTIC ONLY, not live-legal.** |
| context @ entry | `r2` `r3` `r4` `r5` `votes_l` `votes_s` `vol30` |
| pnl | `gross` `net` — **persisted but NOT to be reported** (Joe 0711) |

## Findings [measured 0711, n=158]

**Whole book** — MAEmed 0.72 · MAEp90 3.18 · MAEmax 11.28 · MFEmed 0.65 · MFE/MAE 0.89 · MAE>2 22%

**Apex TF — holds out-of-sample and within each side.** The one structural finding of the day.
```
apex <=14   n=82   MAEmed 0.46   MFEmed 0.68   MFE/MAE 1.47   MAE>2 21%
apex >=15   n=76   MAEmed 1.03   MFEmed 0.56   MFE/MAE 0.55   MAE>2 24%
Spearman  apex vs MAE  rho +0.189 (t +2.40)  ·  apex vs MFE  rho -0.045 (t -0.56)
Held-out JUNE (unfitted):  <=14 MAEmed 0.54 / MFE/MAE 1.00  ·  >=15 MAEmed 1.43 / MFE/MAE 0.63
Within LONG:  0.42 vs 0.82   ·   Within SHORT:  0.60 vs 1.15
Confound (partial): apex>=15 holds 112m vs 80m median. Longer holds accrue more MAE — but they would
accrue more MFE too, and MFE does not rise. Defused, not eliminated.
```
**Joe's read (authoritative):** higher apex = a larger leg, as designed. The defect is **placement** —
`walk_stack` arms at stack-resolution with **no curl**, so the arm lands mid-leg, far from the swing.
Not "fading extended continuation" (my inference, withdrawn).

**Side**
```
LONG    n=75   MAEmed 0.55   MFE/MAE 1.24   MAE>2 20%
SHORT   n=83   MAEmed 0.92   MFE/MAE 0.62   MAE>2 24%   MAEmax 11.28
```

**Arm leg** (arm→entry adverse excursion — known *before* the fill)
```
arm_mae <0.25    n=114   MAEmed 0.74   MFE/MAE 0.91   MAE>2 22%
arm_mae >0.75    n= 16   MAEmed 1.53   MFE/MAE 0.37   MAE>2 38%
```

**Gate branch** — both 10%+ MAE monsters sit in `c` and `div`. Branch `b` has the tightest tail
(MAEmax 3.71, MAE>2 19%).

**Arms converged** — `n_arms=2` (n=5): MAEmed 1.44 vs 0.72 for singletons. Convergence is a hazard
signal, not a confluence bonus. Small n.

**Quiet tape** — `vol30 < 0.5` (n=6): MAEmed 0.15, MAE>2 = 0%. Cleanest cohort in the book.

**Bias segments** (Joe's 12 manual flips, 3 clusters; last flip of a cluster = one trade)
```
ALIGNED    n=31   MAEmed 0.61   MFE/MAE 1.23   MAE>2 10%
MALIGNED   n=52   MAEmed 0.80   MFE/MAE 0.69   MAE>2 25%
```
**But the pooled result is one cluster.** C1 shows no separation (0.40 vs 0.41; MFE/MAE *favours*
maligned). C2 shows no separation (0.90 vs 0.87; MAE>2 *favours* maligned). **All of it is C3**
(0.73 vs 1.56; MAE>2 0% vs 40%).
**Open confound:** inside the clusters LONG MAEmed 0.47 / MFE/MAE 1.52 vs SHORT 1.29 / 0.43. C3's
aligned cohort is mostly LONG. **The alignment signal and the side signal may be the same effect.**
Undecided — needs aligned-vs-maligned computed *within* each side.

## Withdrawn claims (0711)

- ~~"The backstop exit takes 110 exits and loses all the money"~~ — a **net** claim. On excursion the
  backstop has the *lower* median MAE (0.60 vs the arm exit's 1.25). The exit-kind cut is confounded by
  hold time (66m vs 189m median) and I do not trust it in either metric.
- ~~"Losers have no floor, median MAE 2.03%"~~ — used the MFE-first split, which is an outcome label,
  not a feature. Book-wide MAEmed is 0.72; MAE>2 is 22%.
- ~~"Apex TF — the sharpest separator in the table"~~ — that was max-minus-min of a 13-way split of 158
  trades with cells of n=1..27. The *coarse* split survives; the framing did not.
- ~~`walk_stack` "beats the curl/reversal latch decisively (net +0.215 vs -0.126 /trade, 20d)"~~ —
  single window, net-based. Flagged in the docstring (`arm_walk.py:170`). **The entire justification for
  T4 dropping the curl is unsupported.**

## Known bug (open, noted not fixed)

Same-arm trades are written twice when an arm near midnight is hunted by both adjacent day-windows —
6 rows of 158, byte-identical. Fix = key on `(arm_dt, trade_dt, side)`. Joe: note it, don't drop it.

## Next, when the freeze lifts

1. **Aligned-vs-maligned within each side** — settles whether the bias signal is the side signal. Cheap,
   no re-run, and it's the one thing that would change how the bias machine is judged.
2. **Curl-vs-no-curl arm A/B** on MAE/MFE over 62 days, per-cluster — the test the poisoned sweep never
   ran. Three arms: stack-arm (current) / stack-then-curl / curl-latch.
3. **Exit curl band width** (`7:2,14:4,999:6`) — the curl *is* live in `take_profit_ad`.
