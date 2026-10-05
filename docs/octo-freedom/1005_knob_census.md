# 1005 — THE KNOB CENSUS, and why "sweep every knob" splits into two jobs

Joe 1005: *"collect all knobs from all involved machines and sweep. gpu is an option. use small
increments (steps 0.1 or 0.05), and sample every result. find every relevant knob on the Jig and add
it to the soup. momentum is another."*

**43 knobs found.** Full-factorial at Joe's steps is **8.86e55 cells**. The number is the finding, so
it leads. Harness: `1005_scoring/sweep.py`. Hardware: RTX 3060 Ti 8 GB, cupy 14.1.1, 16 cores, 15 GB
free.

## THE SPLIT THAT DECIDES EVERYTHING — upstream vs downstream of the octo-sig walk

| layer | knobs | what a cell costs | full factorial | one-at-a-time |
|---|---|---|---|---|
| **DOWNSTREAM** — re-routes and re-scores CACHED signals | 11 | ~0.9 s CPU | 7.37e13 cells | **289 cells, 4.3 min** |
| **UPSTREAM** — changes WHICH signals fire, so every cell needs a full re-walk | 32 | **1,632 s = 27.2 min** (17 days x 96 s) | 1.2e42 cells | **1,337 cells = 606 h = 25.3 days** |
| both | **43** | — | **8.86e55** | 1,626 |

- a GPU does not rescue the upstream layer. The cost there is `report_leash_walk.py` re-walking the
  tape per cell, which is sequential Python over 17 days, not arithmetic.
- the GPU DOES help downstream, where the work is array arithmetic over the risk axis.

## THE 43 KNOBS

| # | knob | current | owner | layer | range | step | levels | source |
|---|---|---|---|---|---|---|---|---|
| 1 | swing_detect pct | 0.70 | MINE | D | 0.40 .. 2.00 | 0.05 | 33 | banked 1 % in `linelab_spec.md` s0 |
| 2 | stop / `mae_cap` | 0.80 | JOE | D | 0.30 .. 1.50 | 0.05 | 25 | `wsf_trade_config` v3 = 0.70 live |
| 3 | risk budget % | 2.00 | MINE | D | 0.50 .. 10.00 | 0.10 | 96 | my convention, no knee |
| 4 | pyramid cap | 0 | JOE | D | 0 .. 4 | 1 | 5 | Joe 1005 "drop the pyramid max" |
| 5 | mtd step-1 lookback bars | 48 | MINE | D | 12 .. 240 | 12 | 20 | measured knee |
| 6 | mtd TOL g15 bars | 3 | MINE | D | 0 .. 12 | 1 | 13 | line bar width |
| 7 | mtd TOL g30 bars | 6 | MINE | D | 0 .. 12 | 1 | 13 | line bar width |
| 8 | mtd oob fence | 85.0 | JOE | D | 70.0 .. 95.0 | 0.5 | 51 | oob is 15/85 |
| 9 | mtd rev_wob | 2 | JOE | D | 1 .. 6 | 1 | 6 | v3_config |
| 10 | `LAZY_G_D_GAP_MAX` | 4 | JOE | D | 0 .. 11 | 1 | 12 | Joe 1004, "arbitrary... add to spec for sweeping" |
| 11 | `AF_BLOCK` bars | 60 | JOE | D | 12 .. 180 | 12 | 15 | `jig.py:310` |
| 12 | `WS1MR_DWELL` | 3 | MINE | U | 1 .. 12 | 1 | 12 | `jig.py:142` |
| 13 | `WS1MR_REV_WOB` | 2 | JOE | U | 1 .. 6 | 1 | 6 | `jig.py:144` |
| 14 | `WS1MR_HOLD` | 4 | JOE | U | 1 .. 12 | 1 | 12 | `jig.py:145` |
| 15 | `SR_SAMPLES` | 3 | JOE | U | 2 .. 8 | 1 | 7 | `jig.py:464` |
| 16 | `SR_TOL` | 2.0 | MINE | U | 0.50 .. 5.00 | 0.05 | 91 | `jig.py:466`, "MINE, and unruled" |
| 17 | `SR_TEST` bars | 24 | JOE | U | 6 .. 60 | 6 | 10 | `jig.py:468` |
| 18 | `SR_FENCE` lo | 40.0 | JOE | U | 30.0 .. 50.0 | 0.5 | 41 | `jig.py:469` |
| 19 | `SR_FENCE` hi | 60.0 | JOE | U | 50.0 .. 70.0 | 0.5 | 41 | `jig.py:469` |
| 20 | `WSF_N` (of 12) | 9 | JOE | U | 6 .. 12 | 1 | 7 | `jig.py:1544` |
| 21 | `WSF_HANDICAP` | 0 | JOE | U | 0 .. 3 | 1 | 4 | `jig.py:1545` |
| 22 | `WSF_WS1_XWOB` | 1 | JOE | U | 0 .. 6 | 1 | 7 | `jig.py:1595` |
| 23 | `WMT_TF_LO` | 2 | JOE | U | 1 .. 6 | 1 | 6 | `jig.py:1804` |
| 24 | `WMT_TF_HI` | 12 | JOE | U | 8 .. 23 | 1 | 16 | `jig.py:1805` |
| 25 | `WMT_LOOKBACK_S` | 120 | JOE | U | 30 .. 300 | 30 | 10 | `jig.py:1812` |
| 26 | `STALL_N` | 6 | JOE | U | 2 .. 12 | 1 | 11 | Joe 0814 |
| 27 | rule#1 fence | 27.0 | JOE | U | 15.0 .. 40.0 | 0.5 | 51 | one of the four fences |
| 28 | r-momo fence | 17.0 | JOE | U | 5.0 .. 30.0 | 0.5 | 51 | one of the four fences |
| 29 | Mage fence | 25.0 | JOE | U | 15.0 .. 40.0 | 0.5 | 51 | one of the four fences |
| 30 | rig.DR fence | 85.0 | JOE | U | 70.0 .. 95.0 | 0.5 | 51 | `sweep_v3_signal.Rig.__init__:99-106` |
| 31 | `momo_slope_min` | 1.2 | JOE | U | 0.10 .. 5.00 | 0.05 | 99 | `momo_config` v1 |
| 32 | `momo_slack_ref` | 1.2 | JOE | U | 0.10 .. 5.00 | 0.05 | 99 | `momo_config` v1 |
| 33 | `momo_r2_min` | 0.7 | JOE | U | 0.00 .. 1.00 | 0.05 | 21 | `momo_config` v1 |
| 34 | `momo_window_min` | 60 | JOE | U | 15 .. 120 | 5 | 22 | `momo_config` v1 |
| 35 | `momo_step_min` | 5 | JOE | U | 1 .. 15 | 1 | 15 | `momo_config` v1 |
| 36 | `momo_fixed_samples` | 21 | JOE | U | 5 .. 41 | 1 | 37 | `momo_config` v1 |
| 37 | `k_window` | 6 | JOE | U | 1 .. 12 | 1 | 12 | `momo_config` v1 |
| 38 | `level_slack` | 13.9 | JOE | U | 0.0 .. 20.0 | 0.10 | 201 | `momo_config` v1 |
| 39 | `curl_arc_min` | 4.0 | JOE | U | 0.0 .. 15.0 | 0.05 | 301 | `momo_config` v1 |
| 40 | `curl_vtx_lo` | 0.05 | JOE | U | 0.00 .. 0.50 | 0.05 | 11 | `momo_config` v1 |
| 41 | `curl_vtx_hi` | 0.95 | JOE | U | 0.50 .. 1.00 | 0.05 | 11 | `momo_config` v1 |
| 42 | `curl_r2_min` | 0.4 | JOE | U | 0.00 .. 1.00 | 0.05 | 21 | `momo_config` v1 |
| 43 | `momo_seam` | off | JOE | U | off \| skip_r2 | — | 2 | `momo_core.py:49` |

- momentum is ONE bank per band (wsf 1..12, domtf 13..60, 61..120), all three currently carrying
  IDENTICAL values at v1. Sweeping them independently triples knobs 31-43 to 39 knobs.
- Joe's "steps 0.1 or 0.05" only applies to the continuous knobs. **19 of the 43 are integers**
  (bars, wob, TF indices, sample counts) where a 0.05 step has no meaning — those are stepped by 1
  or by their natural unit, named per row above.

## FIT / TEST — structural, so the sweep cannot quietly overfit

| set | days | why |
|---|---|---|
| FIT | the 10 already scored: 09-25..10-04 | every knob above was chosen against these |
| TEST | **7 random non-sequential days**: 07-23, 07-25, 08-06, 08-20, 08-30, 09-14, 09-17 | drawn `random.Random(8881005)` from the 84 complete unused days in 07-03..10-04, rejection-sampled so no two picks are adjacent and none is within 2 days of a FIT day. Min gap between picks 2; nearest FIT day 8 days away |

Every cell banks `fit_*`, `test_*` and `robust = min(fit_mean, test_mean)` — the banked objective from
`docs/linelab_spec.md` s2 (*"ROBUST = min(fitNet, testNet, ...) — nothing hides"*).

## HARNESS CORRECTNESS, checked before any cell was banked

`sweep.py` re-implements mtd + branch D so a knob can be moved. It reproduces the published figure
**exactly**: 10 days, dr-bias, no pyramid cap, stop 0.70 -> **+41.842** total, which is the figure
implied by the already-published flip table (+31.316 with-trend + +10.526 against-trend). 162 trades
either way.

## A CONSISTENCY DEFECT IN MY OWN EARLIER REPORTING, found by that check

| script | stop it ran at | what I published from it |
|---|---|---|
| `ninedays.py` | **0.70** (`CAP = 0.70`, line 18) | the 9-day +37.148, the -2.508 flip, the 10-day +47.546 and +5.704, the per-day tables, the leverage ceiling |
| `compound_db.py` | **0.80** (`STOP = 0.80`, line 44) | $888 -> $2,022.18, the drag tables, `lazyg_compound` |
| `stops_pyr.py` | both | the 0.70-vs-0.80 comparison, +47.124 |

`1005_knobs.md` section 2 names 0.80 as "the" stop. **Section 5's tables are at 0.70 and section 7's
are at 0.80**, and I did not say so when I published them. At stop 0.80 the same 10-day dr-bias total
is **+51.070**, not +41.842 — a 9.2 pp difference that the labelling hid.

The same defect reaches the leverage table sent to o9-live recon in chat #53: the trade outcomes
there are at stop 0.70 throughout, while the row labelled "2 % at the scored stop 0.80" used 0.80
only in the leverage divisor. That row needs re-scoring at 0.80 before it is used.

## WHAT IS HELD, AND WHY

- **the objective is Joe's.** Every cell is banked; nothing is ranked. Memory `mae-mfe-only` bias 2:
  *"Do not sweep and hand back 'the winner'."*
- **the 32 upstream knobs are not run.** One-at-a-time over them is 25.3 days of compute. Joe scopes
  which subset, or sets a time budget and I pick the cheapest informative slice and say which.

## THE 7 OOS WALKS — all complete

| day | walk secs | octo-sig rows |
|---|---|---|
| 2026-07-23 | 73 | 16 |
| 2026-07-25 | 80 | 28 |
| 2026-08-06 | 85 | 32 |
| 2026-08-20 | 93 | 32 |
| 2026-08-30 | 92 | 35 |
| 2026-09-14 | 91 | 30 |
| 2026-09-17 | 101 | 34 |
| **7 days** | **615** | **207** |

FIT carries 328 signals over 10 days; TEST carries 207 over 7. Signals live at
`1005_scoring/octosig/<day>.out`.

## A SECOND DEFECT FOUND BY THE HARNESS CHECK — and its magnitude

`ninedays.py:60` does `if f is None: continue` — it drops the WHOLE ROW when the **flipped** leg is
unresolved, so the dr-bias basis loses a row it could have scored. Line 72 does the reverse. The two
bases are supposed to be independent.

Measured on the 10 FIT days at stop 0.70, each basis on its own MAXIMAL set:

| basis | scoreable rows | total net % | mean |
|---|---|---|---|
| dr-bias | **162** | +41.842 | +0.2583 |
| flipped (stage 2 on with-trend) | **164** | +47.501 | +0.2896 |

- **dr-bias was NOT contaminated** — 162 is genuinely its maximal set, and +41.842 stands.
- the flipped basis was reported as **+47.546 on 162 rows**; its true maximal set is 164 rows at
  **+47.501**. The 2 dropped rows were slightly negative, so the published figure was **overstated
  by 0.045 pp**.
- **0.045 pp changes no conclusion.** The flip is still undecided. Recorded because the defect is
  structural, not because the number moved.

## THE CORRECTED LEVERAGE TABLE — each row scored at ITS OWN stop

Supersedes the table in chat #53, where every row's trade outcomes were at stop 0.70 while one row
was labelled 0.80. 10 FIT days, dr-bias, $888 start.

| rule | stop used | lev | trades | one worst trade | longest losing run | that run costs | final $ | max DD % |
|---|---|---|---|---|---|---|---|---|
| live now: fixed 66,000 coins | 0.70 | **13.595x** | 162 | 12.20 % | 6 | **54.19 %** | 70,254.95 | **60.41** |
| 2 % risk at the live stop 0.70 | 0.70 | **2.228x** | 162 | 2.00 % | 6 | 11.42 % | 2,172.82 | 11.23 |
| 2 % risk at the scored stop 0.80 | 0.80 | **2.005x** | 162 | 2.00 % | 6 | 11.42 % | **2,393.62** | 11.43 |
| max L for DD <= 25 %, stop 0.70 | 0.70 | **5.183x** | 162 | 4.65 % | 6 | 24.86 % | 6,360.51 | 25.00 |
| max L for DD <= 25 %, stop 0.80 | 0.80 | **4.674x** | 162 | 4.66 % | 6 | 24.91 % | 8,126.18 | 25.00 |

Changes from what was sent: the 0.80 row's final was **1,993.05 -> 2,393.62**, and the DD <= 25 %
leverage was **4.800x -> 5.183x (0.70) / 4.674x (0.80)**. The earlier 4.800x came through the
cross-drop path above.
