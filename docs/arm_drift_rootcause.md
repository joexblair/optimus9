# ARM-DRIFT root cause (0710) — the r-lines need 12 hours to converge

Three `ARM-DRIFT ... DISAPPEARED (window-invariance broken)` alerts fired overnight:

```
07-09 21:10:45 gone  ->  07-09 21:08:35 appeared   (2m10s earlier)
07-10 01:23:55 gone  ->  07-10 01:14:35 appeared   (9m20s earlier)
07-10 01:14:35 gone                                 (the same arm, oscillating)
```

## What it is NOT

**Not the tape.** Every `recon` row either side is `CLEAN (maxdiff=0)`.

**Not the Bollinger lines.** `[measured]` 24h window vs 30h window, same right edge, 82,080 overlapping
bars:

```
line     max |diff|   bars >1e-9   bars >1e-6   bars >1e-3
s5m       7.9e-08        15658            0            0
s5M       4.9e-09         1209            0            0
s15M      2.4e-07        28436            0            0
s30M      6.5e-08        13818            0            0
s2M       6.3e-09         1236            0            0
```

## What it IS

The `r` lines are **not window-invariant**:

```
s5r       1.539e+01        6756         3817         2384
s3r       1.721e+01        4373         3257         1790
```

Up to **15.4 points** on `s5r` and **17.2** on `s3r`. And every one of those disagreements lives in the
first twelve hours of the data:

```
--- s5r : |diff| by hours since the overlap start ---
   hours    bars     max|d|    mean|d|   >1e-3
   0-12     8640  1.539e+01  4.049e-01    2384
  12-24     8640  4.973e-10  1.457e-11       0
  24-36     8640  2.842e-14  5.863e-15       0
   ...                                        0
```

`[read]` `indicator_computer._rma:256` — Wilder's RMA, SMA-seeded, recursive with `alpha = 1/n`.
`f_k_lookahead` feeds RSI through it with `rsi_len = 6`. `(5/6)^144 = 4e-12`, and 144 five-minute bars is
**12 hours**. The number matches to the hour. The BB lines have no recursion and converge in one window.

## Consequences

**o9-live is NOT affected.** `[measured]` the decision bar (14h from the window head: `buffer_hours=8`,
`warmup_hours=6`, `ops/run_o9live.py:37`), worst error over six decision instants vs a 114h reference:

```
cfg (lb+wm)             s5r          s3r          s4r          s5m          s2M
8h+6h=14h  (LIVE)  5.173e-12    1.421e-14    2.842e-14    1.039e-09    5.618e-11
8h+10h=18h         1.421e-14    1.421e-14    1.421e-14    0.000e+00    3.222e-10
```
14h > 12h. Two hours of margin. A tape gap that shortens the effective bar count eats into it.

**`recon_arm_daemon.py` is reporting on its own window head.** It runs `LB_H=14, WM_H=6` (20 h) and
recomputes the whole 20h arm set each pass, with `STABLE_MS = 2 * 3600 * 1000` to exclude the "warmup
zone". **2 hours is 6x too small.** Arms 2–12 hours old sit in the unconverged head, so they appear and
disappear as the window slides. All three alerts land in that band.

`STABLE_MS` is a monitor threshold. Widening it is Joe's call, not the assistant's. The natural value is
derived, not chosen: `ceil(rsi_len * ~24 bars) * slowest_TF`, which for `rsi_len=6` on a 5-minute line is
12 hours.

## A separate, smaller problem: `_mage_rev` has no epsilon

`[read]` `lr_v2._mage_rev:280` — `ss = np.where(np.isnan(dd), 0, np.sign(dd))`. A step of `+1e-15` counts
as a real up-step and extends a wob run.

`[measured]` over 82,080 bars: `s5r` has **460 steps in the open interval `(0, 1e-9)`** and **378 reversal
fires land on one**. An epsilon collapses the cross-window disagreement:

```
   eps       s5m         s5r         s5M        s15M       s30M
  0e+00   125/29864   857/19810   716/29237   43/26352   73/28054
  1e-12   125         137         716         43         73
  1e-09   127         137         712         41         73
```

`s5r` drops `857 -> 137`. The residual (and all of `s5M`'s 716) is the warmup head above, not the sign of
a dust-sized step.

Within one window `_mage_rev` is deterministic, so this is a **backtest/live reconciliation hazard, not a
live one**. It is a change to a core producer on the live path and belongs to Joe.
