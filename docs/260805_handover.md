# 0805 handover — s46 item 13 (momo) built, and what to pick up next

**Joe's next task: filter or flip the bad trades.** Everything below is context for that.

Read with: `docs/260802_s4_s6_strategy.md` — the s46 spec, now carrying the full knob register
(section headed "0805 — THE KNOB REGISTER").

---

## 1. THE ONE-LINE STATE

Item 13 (momo) is **built, causal, swept, and writing to both tables**. It is **NOT** in Joe's
production builders. `s46_window` is currently showing item 13's exits, updated by
`optimus9/analysis/build_s46_event.py`, not by `build_s46_window.py`.

---

## 2. WHERE THE CODE IS

| file | role |
|---|---|
| `optimus9/compute/momo_gated.py` | the momo INDICATOR — `build_exhv2.momo()` plus 3 curl gates |
| `optimus9/analysis/s46_momo.py` | item 13's MECHANIC — pure logic, no IO. `walk()` is the entry point |
| `optimus9/analysis/build_s46_event.py` | IO — writes `s46_event`, and re-scores `s46_window` |
| `optimus9/analysis/sweep_s46_momo.py` | the 49-config sweep (fence 2-8 x xwob 3-9) |
| `build_r7512.py` | banks r15/r22 at `7\|5\|12` + momo states, 07-24 -> 08-01 |
| `build_r3.py` | banks s3r (two R_SPEC variants) — from the FAILED curl-pred experiment |

`build_exhv2.py`, `build_s46.py`, `build_s46_window.py` are **UNMODIFIED**.

---

## 3. ITEM 13, AS BUILT

    ARM        per bar of the walk: the indicator returns momo(1) or curl(2), same bias, on s15r OR s22r
    HOLD       once armed the trade ignores its normal exit
    momo_exit  1) BOTH r beyond the fence, in the trade's direction     -> LATCHED
               2) EITHER r beyond the fence                             -> LATCHED
               both latched; the trade then closes at the NEXT qualifying s6x cross
    OPPOSING   the same curl state read against the INVERTED direction, on s15r AND s22r, same bar
    CURL       -> cancels the fence latch; closes at the next qualifying s6x cross
    UNARMED    item 15 unchanged — the next bias-side gated s6x cross, at EXIT_WOB 3

**ITEM 15's WORDING WAS WRONG IN THE OLD CHAIN.** It read "the first single bar where s6x crosses
back through s6Mage". The code ALSO requires the cross to HOLD that side for `XWOB` bars
(`sx_run_bars >= XWOB`, stamped at `+(XWOB-1)`). That hold test is what makes the forward-measured
`sx_run_bars` causal. My first `s46_event` build applied the stamp WITHOUT the filter — looser than
Joe's rule — and every exit bar in that run was affected. Fixed; `sx_series()` now derives both
from one `xwob` argument so they cannot drift apart.

Fence: `fence_lo = LO + s`, `fence_hi = 100 - LO - s`. At s=7 that is 22/78.

### the three curl gates (`momo_gated.py`)
`build_exhv2.momo()` tests alignment and a fit floor ONLY on its `momo` branch. Its `curl` branch had
neither. That armed 07-27 09:07:00 on a SHORT while s15r was RISING at slope +0.975, with qa +22.635
— a minimum, i.e. the down-curl had already ENDED, vertex at 0.259.

| gate | test | Joe's call |
|---|---|---|
| 1 | curl needs slope aligned with `dr`, same test `momo` uses | 0805 |
| 2 | arc = curl BEGINNING only. `dr -1` needs `qa < 0`; `dr +1` needs `qa > 0` | 0805 |
| 3 | QUADRATIC r2 >= `CURL_R2_MIN` 0.40 | 0805 |

`CURL_R2_MIN` 0.40 came from the errant 07-27 09:19:00 s22 bar, which scores 0.3238. Across the
2,289 bars already passing gates 1+2: min 0.1553 / p10 0.4157 / median 0.6735 / max 0.8719. It rests
on ONE event — sweep it.

---

## 4. RESULTS — 36 trades, 07-27 -> 07-29, fence 7, xwob 3

### ⚠ WHICH CONFIG IS IN `s46_window` RIGHT NOW: **`item13 A f7 x3`**
Check the **`sw_src`** column — it stamps every row. `build_s46_window.py`'s INSERT does not name
that column, so its rows take the DEFAULT `'item15'`. Mine writes `item13 <cfg> f<fence> x<xwob>`.
No edit to Joe's builder was needed.

### CUR vs A, same fence 7 / xwob 3, net of 0.110% round-trip taker

| cfg | lines | n | ret sum | net/trade | win | median hold |
|---|---|---|---|---|---|---|
| **CUR** | `10\|4\|11` both duties | 36 | **+24.62** | **+0.5740** | **75.0%** | 96 min |
| **A** | momo `10\|4\|11`, oob `7\|5\|12` | 36 | +11.57 | +0.2113 | 66.7% | **50 min** |

**A is WORSE on this window** — roughly half the net, 8 points of win rate, but holds cut ~48%.
Its momo column is bit-identical to CUR by construction; the whole difference is the oob duty
reaching the fence sooner on the faster line. A also latches branch 1) three times vs CUR's once
(momo_exit 27 vs 25), i.e. both r lines clear the fence far more often.

This is ONE 3-day window. The A/B question is not settled by it.

### the CUR numbers below (this is what section 5's per-trade table refers to)

`s46_window` held these before the A run. Net of 0.110% round-trip taker (repo standard: `replay.py:31`).

| | |
|---|---|
| n | 36 |
| ret sum | +24.62 |
| mean | +0.6840 |
| **net of taker** | **+0.5740/trade** |
| win rate | **75.0%** (27 of 36) |

**CONCENTRATION:** n=12 (+5.142), n=15 (+3.928), n=34 (+2.157) = **+11.23 of +24.62 — 46% from 3 of
36 trades.** Strip them and the other 33 average +0.405.

### the sweep (49 configs, `sweep_s46_momo.py`)

| fence | net mean, all rows | median hold |
|---|---|---|
| 2 (17/83) | +0.042 | 154 min |
| 3 (18/82) | +0.115 | 142 min |
| 4 (19/81) | +0.221 | 130 min |
| 6 (21/79) | +0.475 | 87 min |
| **7 (22/78)** | **+0.574** | 83 min |
| 8 (23/77) | +0.567 | 73 min |

- **fence is monotone 2->7 then flat.** 13.7x spread. This is the finding.
- **xwob is INERT** — 3 to 9 moves the mean by ~0.02 at every fence. It removes a knob.
- fence and hold length are the SAME knob seen from two sides: wider fence -> reached sooner ->
  shorter hold, and shorter holds are what improved the numbers.

### ITEM 15 (no-pyramiding) is the binding constraint

| fence 7, xwob 3 | n | net mean | net sum |
|---|---|---|---|
| all rows | 36 | +0.5740 | +20.7 |
| **item 15 applied** | **24** | **+0.3263** | **+7.8** |

12 of 36 entries blocked. Mean falls 43%, total falls 62%. Still ~3x the cost line.

---

## 5. JOE'S NEXT TASK — filter or flip

Joe 0805, on n=21 (07-28 11:03:25, dr -1, `sw_pk` 81): *"the real issue with this: the trade should
have been filtered or flipped"*. Item 13 armed 11:10:00, the opposing curl fired 12:45:15, the trade
then waited for a qualifying cross to 13:42:10 — 158.8 min, ret +1.887. It worked, but it should
never have been a short.

### the trades that look wrong, with price attached

| # | entry | dr | MAE | MFE | ret | Joe's note |
|---|---|---|---|---|---|---|
| 30 | 07-29 09:40:20 | +1 | 1.801 | **0.017** | **−1.543** | "no strength ... the market is sideways" |
| 19 | 07-28 07:47:20 | −1 | 1.977 | **0.076** | **−1.615** | s4r curling back into IB, no s4Mage to ride |
| 11 | 07-27 13:32:30 | −1 | **1.234** | **0.000** | −1.234 | unarmed; MFE never left zero |
| 22 | 07-28 12:27:15 | +1 | **3.207** | 1.635 | +0.702 | largest MAE in the set |

**MFE ~= 0 with a large MAE is the signature** — the trade never went favourable at all. n=30, n=19
and n=11 all show it. That is the population a filter should catch.

### the entry defect behind n=30 — the s4Mage pinhole

07-29 09:40:20 opened on a stretch of ONE 5 s bar: s4Mage reached **85.17**, i.e. **0.17 points**
past the 85 level, and fell back on the next bar. Both existing gates passed easily because they
measure the RUN-UP, not the breach: `sr_ib_bars` 475 = 39.6 min, `sr_s1hold` 109 = 9.1 min.

| stretch <= | all 13,633 stretches | after `>24 AND >24` (854 rows) |
|---|---|---|
| 1 bar (5 s) | 22.0% | **24.1% = 206 trades** |
| 6 bars (30 s) | 56.3% | 57.1% |
| 24 bars (120 s) | 78.0% | 76.1% |

**The gate moves the one-bar share 22.0% -> 24.1%: it does not select on breach quality at all.**

`S4HOLD_MIN` exists for this (`s46_momo.py`), **default 0 = OFF**, with `s4hold_entry()`. Turning it
on DELAYS entry to bar N of the stretch, which contradicts item 11's "no waiting, no confirmation" —
Joe's call, not made. **Do NOT use `sr_dwell_bars`**: it is `int(b - a + 1)`, the run's total length
measured forward. Lookahead.

### divergence — parked, and the doc is good

`docs/o9-live/divergence_research.md`, 290 lines, 0711. Joe 0805: *"leave divergence alone until s46
is updated and I've reviewed the output"*. He also called out §9's floater repair as
*"the most important repair we made"*.

- **Family A, slope-sign, production + causal**: `line_slope = line - peak`,
  `divergence +-1` when `sign(line_slope) != sign(price_slope)` and `|delta| > slope_floor`.
  `PM +-2` = signs AGREE = continuation, the OPPOSITE of divergence.
- **the floater** (`pk_state_computer.py`): roll a max and a min over `window = pool_range *
  multiplier`, shift BOTH forward by `lower = (bars - half) * multiplier` so the window ends before
  the current bar, then side-select — `line > midpoint` (50) takes the max, else the min.
- **§12 vote-gate, 20-day OOS**: `r L12 K3` (3-of-4) gives 4.1/day, MAE 0.75, MFE 1.53, **mfe_ok
  65%**; the loose 2-of-4 gives 25.4/day and 53%. Selectivity is the lever.
- **§12 corrects §9**: *"DEMA-smoothing the price slope DESTROYS it (MAE 0.15 -> 0.35-0.85). The raw
  price slope is correct."* `jig.py:293` agrees. **But `pk_state_computer` uses DEMA** — an
  unresolved discrepancy in the production path.
- **§15 standing warning**: *"THE +59.0% IS OVERFIT — DO NOT SHIP"*.
- Joe 0805 wants, when he returns to it: divergence at every s4Mage entry, mixing TF {4,5,6,8,10} x
  lines {r, Mage, m}, plus a NEW `bb 12|0.8|close`. Four knobs unset: `center`, `slope_floor`, `K`,
  and whether the new bb line votes or is the price proxy.

---

## 6. LOOSE ENDS — read before doing anything

1. **TWO BUILDERS WRITE `s46_window`** — `build_s46_window.py` (Joe's) writes the item-15 baseline;
   `build_s46_event.py` (mine) re-scores the same rows at item 13's exits. Running one still
   overwrites the other. **RESOLVED (Joe 0805): the `sw_src` column now stamps which** —
   `'item15'` by DEFAULT for Joe's INSERT, `'item13 <cfg> f<fence> x<xwob>'` from mine. Always
   check it before reading the table.
2. **The config in `s46_window` right now is MINE, not Joe's**: fence 7, xwob 3, cfg CUR. Chosen as
   the sweep maximum on 36 rows — best-of-49, which is selection.
3. **The npz line banks are in `$CLAUDE_JOB_DIR/tmp/`** — scratch, wiped on cleanup. A TODO is now
   in `build_s46_lines.py`'s docstring (Joe 0805, LOW PRIORITY: these should be databased, and
   `build_r7512.py` / `build_r3.py` should fold into that file). Banks:
   `lines_all.npz` (full tape, `10|4|11`), `r7512.npz` (07-24->08-01, `7|5|12`), `r3.npz` (failed
   experiment). Item 13 CANNOT run without `lines_all.npz`. Rebuild: `build_s46_lines.py`.
4. **`build_s46_window.py` has no access to the r lines.** It reads only `s46_px` and `s46_exit`.
   Putting item 13 in the production path needs the lines somewhere real. `build_s46.py` already
   holds `E[15]` / `E[22]` as full per-bar arrays at ceiling 120 and discards them — cheapest fix.
   Joe 0805 floated a dynamic IC table instead; the cost was never measured.
5. **`--cfg A` is now WIRED and RUN** (Joe 0805). `NPZ` is `{cfg: (momo_npz, oob_npz)}`; A reads
   momo from `lines_all.npz` and the fence/oob lines from `r7512.npz`, re-gridded onto the momo
   timebase. Result in section 4: **worse than CUR on this window** (+0.2113 vs +0.5740/trade) but
   holds ~48% shorter. One window; unsettled.
6. **`sw_curl_pred_ms` / `sw_curl_pred_utc` DROPPED** (Joe 0805). The curl-pred experiment is
   retired — handing over before 20/80 lands on an earlier s3 cycle, so the signal is early by
   >= 1 full revolution of s4r's travel. `build_r3.py` and `curl_pred*.py` remain on disk.
7. **`s46_momo` (1,100 rows) and `s46_momo_leg` (8,800 rows)** are from the earlier gate/race
   experiment — a DIFFERENT mechanic to item 13. Do not conflate. Item 13 writes `s46_event`.
8. **`sr_dwell_bars`, `sr_m4_min`, `sr_m4_max` in `s46_run` are LOOKAHEAD** — all three span forward
   to the run's end. `sr_ib_bars` (`ibrun[a-1]`) is causal and differs by one character of code.
9. **`7|7|12` r spec deferred** (Joe 0805: *"a sweep. I don't think we do the sweep now, we need more
   OOS before we make decisions"*).
10. **`sx_run_bars` units parked** — `EXIT_WOB` 3 is counted on the 5 s grid, so it debounces a
    6-minute line over 15 s, a fifth of one of its own bars. Joe: sweep after the mechanic is bedded.
11. **`s46_window` covers 07-27 -> 07-29 only.** The tape runs to 07-31, and `kline_collection` is
    live and past that. 36 rows over 3 days is the whole evidence base for everything in section 4.

---

## 7. THE VOIDED WORK — 0804, do not quote it

`sweep_s46_exit.py` had `s6_mode='fallback'`, which suppresses the s6 exit whenever the leg fires
anywhere in the future. NOT CAUSAL. Every leg result from 0804 ckpt 17 onward used it.

| | fallback (void) | race (causal) |
|---|---|---|
| x15M30 H2 +G30, walk-forward | +0.609/trade, t 2.26, 7/8 weeks | **−0.019/trade, t −0.23, 2/8** |
| same, unfiltered | +0.101, t 0.47 | −0.098, t −2.37 |

`docs/260804_handover.md` carries a VOID banner. `docs/260804_exit_permutation_notes.md` ckpt 40 has
the full damage. The entry-side knobs measured under it — `sr_x1` p70, the leg/H/gate grid — are
unproven, not disproven.

**The habit that caught it:** Joe asked "is this strictly causal?" of a mechanic I had already
shipped numbers for. Ask it of every mechanic, every time.
