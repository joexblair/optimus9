# 1026 — is live_seam's 104 h window long enough for its 21 lines?

Joe 1026: *"validate the warmup length. we're maxing at TF12 so the cache shouldn't be too heavy - there's notes about correct warmup sizing in the docs"*.

Method: `1001_warmup.md`'s.
- Every line is built at load span S, all ending at the same bar: 2026-10-26 21:15:05.
- Each is compared with a 2,268 h reference at identical timestamps. The reference starts at 2026-07-24 09:15:10, and 2,268 h is the backtest Jig's span, which 1001 also used.
- The table shows the worst |diff| over the last 720 bars (1 hour).
- Script: `warmup_check.py`.

| line | 14 h | 20 h | 28 h | 40 h | 56 h | 72 h | 104 h | 144 h |
|---|---|---|---|---|---|---|---|---|
| ws1b | 5.8e-09 | 8.7e-09 | 5.0e-09 | 8.7e-09 | 2.5e-09 | 5.8e-09 | 8.6e-09 | 6.5e-09 |
| ws1r | 2.8e-14 | 4.3e-14 | 4.3e-14 | 4.3e-14 | 4.3e-14 | 4.3e-14 | 5.7e-14 | 5.7e-14 |
| ws2r | 4.3e-14 | 4.3e-14 | 4.3e-14 | 4.3e-14 | 2.8e-14 | 2.8e-14 | 2.8e-14 | 4.3e-14 |
| ws3r | 3.6e-14 | 4.3e-14 | 3.6e-14 | 2.8e-14 | 2.8e-14 | 2.8e-14 | 3.6e-14 | 3.6e-14 |
| ws4r | 7.1e-14 | 7.1e-14 | 7.1e-14 | 7.1e-14 | 7.1e-14 | 7.1e-14 | 7.1e-14 | 7.1e-14 |
| ws5r | 8.2e-14 | 7.1e-14 | 7.1e-14 | 7.1e-14 | 7.1e-14 | 8.5e-14 | 8.5e-14 | 8.5e-14 |
| ws6r | 1.6e-11 | 1.4e-14 | 1.4e-14 | 1.4e-14 | 1.4e-14 | 1.4e-14 | 0.0e+00 | 1.4e-14 |
| ws7r | 3.5e-09 | 4.3e-14 | 2.1e-14 | 2.1e-14 | 2.1e-14 | 2.1e-14 | 3.6e-14 | 3.6e-14 |
| ws8r | 4.7e-08 | 6.9e-13 | 2.1e-14 | 2.1e-14 | 2.1e-14 | 2.1e-14 | 2.1e-14 | 2.1e-14 |
| ws9r | 5.1e-07 | 6.0e-11 | 4.3e-14 | 2.8e-14 | 2.8e-14 | 2.8e-14 | 2.8e-14 | 2.8e-14 |
| ws10r | 4.0e-06 | 6.1e-10 | 1.2e-13 | 2.8e-14 | 2.8e-14 | 2.8e-14 | 1.4e-14 | 0.0e+00 |
| ws11r | 1.8e-05 | 2.9e-09 | 1.4e-12 | 7.1e-14 | 5.7e-14 | 7.1e-14 | 7.1e-14 | 7.1e-14 |
| ws12r | 1.0e-04 | 1.2e-07 | 2.3e-11 | 2.8e-14 | 2.8e-14 | 2.8e-14 | 2.8e-14 | 2.8e-14 |
| ws5Mage | 7.1e-10 | 7.1e-10 | 7.1e-10 | 1.1e-09 | 7.1e-10 | 6.5e-10 | 7.1e-10 | 6.5e-10 |
| ws6Mage | 3.1e-10 | 3.3e-10 | 4.0e-10 | 3.4e-10 | 4.0e-10 | 4.0e-10 | 2.6e-10 | 3.0e-10 |
| ws7Mage | 2.3e-10 | 3.5e-10 | 2.7e-10 | 2.7e-10 | 3.5e-10 | 3.5e-10 | 3.5e-10 | 3.5e-10 |
| ws8Mage | 3.1e-10 | 2.4e-10 | 1.8e-10 | 2.5e-10 | 3.1e-10 | 3.2e-10 | 3.6e-10 | 2.5e-10 |
| ws9Mage | 1.8e-10 | 4.3e-10 | 1.8e-10 | 4.3e-10 | 1.8e-10 | 6.2e-11 | 2.3e-10 | 2.4e-10 |
| ws10Mage | 7.7e-11 | 1.4e-10 | 1.6e-10 | 1.6e-10 | 1.6e-10 | 2.1e-10 | 1.4e-10 | 7.7e-11 |
| ws11Mage | 1.1e-10 | 1.8e-10 | 1.8e-10 | 1.1e-10 | 1.1e-10 | 1.1e-10 | 1.8e-10 | 3.6e-11 |
| ws12Mage | 1.2e-10 | 6.2e-11 | 1.2e-10 | 1.2e-10 | 1.2e-10 | 1.2e-11 | 1.2e-10 | 5.0e-11 |
| pxs | 0.0e+00 | 0.0e+00 | 0.0e+00 | 0.0e+00 | 0.0e+00 | 0.0e+00 | 0.0e+00 | 0.0e+00 |

- **r lines** (k 5/8/7):
  - They carry a decaying seed error, so the needed span grows with the timeframe.
  - ws12r, the slowest line here, reaches the float floor (2.8e-14) at 40 h.
  - At 28 h it is 2.3e-11, and at 14 h 1.0e-04.
  - 1001's decay model, 0.8^(S·60/12 − 20), puts 1e-14 at 32.9 h.
- **b and Mage lines** (bb 49/0.95, bb 38/0.93):
  - They have no recursion, so window length makes no difference.
  - Every span measures between 1e-11 and 1e-08, including 14 h.
- **pxs** (DEMA(close, 2) on the full 5 s base) is exact at every span.
- **The running window**, lookback 24 h + warmup 80 h = 104 h (o9-live's), is 2.6 times the 40 h that ws12r needs.
- **Correction to my chat #5:** the 2.0e-07 I cited from `1001_rebuild_timing.md` is ws2x, rule#1's divergence line, which is not in this test. That table's Mage lines were ≤ 7.7e-09. Here, b is ≤ 8.7e-09 and Mage ≤ 1.1e-09.
- **Not measured:**
  - **Tape gaps:** a gap removes bars without removing hours.
  - **`towards`' reach-back:** `rule2_trajectory.opposed_extrema` walks back block by block while each block sets a new extreme. How far it reaches on this window is not measured.
