# 1001 — how long each of octo-freedom's state-carriers runs before it resets

Joe 1001: *"do 4"* — open item 4 was `rig.DRW`'s stretch distribution. All **three** state-carriers
are measured here, not just `DRW`, because the live window length is the o9-live session's decision 2
and it needs all three: a bounded window reproduces the backtest only if it reaches back past the
last reset of **every** carrier the walk reads.

## How to re-run it

    python3 $CLAUDE_JOB_DIR/tmp/conv.py

The script is scratch and will be deleted with the job. It reads the stamped mechdev array cache
(`mechdev_rig.load(expect_end_ms=2026-09-08)`), takes `rig.DR`, `rig.DRW` and `ws5Mage`, and splits
each into runs of a constant value. **To re-derive it from the repo alone**, build
`sweep_v3_signal.Rig` on any window and apply the same run-splitting to `rig.DR`, `rig.DRW` and the
sign of `ws5Mage - 50`. No knob is involved beyond the ones below.

| knob | value | source |
|---|---|---|
| tape | 2026-06-05 12:00:00 → 2026-09-07 23:59:55, 1,632,960 bars = 94.5 days | `build_ws_lines.TAPE_END` 2026-09-08, a FIXED 94.5-day width anchored on its end |
| `mage_fence_lo` / `_hi` | 25.0 / 75.0 | `wsf_trade_config`, read at runtime |
| `latch_tf` | 13 | same |
| `latch_wob` | 8 bars = 40 s | same |
| the walk's dr fence | 85 / 15 — **oob** | hardcoded inline, `sweep_v3_signal.py:103-104` |

## The three carriers

| carrier | what it is | what resets it |
|---|---|---|
| `rig.DR` | the **walk's** dr — ws1Mage + ws13m both past 85 or both past 15, **no wob** | a dr change |
| `rig.DRW` | **rule#1's** dr — the same pair at Mage 75 / 25, **wob 8** | a dr change |
| `ArmState` | the arm — ws5Mage past 75 or 25 on the dr side for 6 bars = 30 s | a **ws5Mage 50-cross**, which clears every field |

## `rig.DR` — the walk's dr

| measure | value |
|---|---|
| runs at a non-zero dr | 2,487 |
| **longest** | 5,175 bars = **7.19 h** |
| median | 510 bars = 0.71 h |
| p90 | 1,386 bars = 1.93 h |
| p99 | 2,536 bars = 3.52 h |
| runs ≥ 8 h | **0 of 2,487** |
| leading dr == 0 run | 743 bars = 1.0 h, before the first latch |

| rank | from | to | bars | hours | dr |
|---|---|---|---|---|---|
| 1 | 07-31 21:17:10 | 08-01 04:28:20 | 5,175 | 7.19 | +1 |
| 2 | 07-18 19:16:25 | 07-19 00:27:40 | 3,736 | 5.19 | +1 |
| 3 | 06-14 18:39:15 | 06-14 23:33:25 | 3,531 | 4.90 | +1 |
| 4 | 07-22 02:37:35 | 07-22 07:15:20 | 3,334 | 4.63 | −1 |
| 5 | 08-09 11:46:45 | 08-09 16:23:05 | 3,317 | 4.61 | +1 |

## `rig.DRW` — rule#1's dr. THIS WAS OPEN ITEM 4

| measure | value |
|---|---|
| runs at a non-zero dr | 2,507 |
| **longest** | 4,421 bars = **6.14 h** |
| median | 514 bars = 0.71 h |
| p90 | 1,338 bars = 1.86 h |
| p99 | 2,482 bars = 3.45 h |
| runs ≥ 8 h | **0 of 2,507** |
| leading dr == 0 run | 764 bars = 1.1 h |

| rank | from | to | bars | hours | dr |
|---|---|---|---|---|---|
| 1 | 07-31 21:08:05 | 08-01 03:16:25 | 4,421 | 6.14 | +1 |
| 2 | 07-18 19:17:30 | 07-19 00:28:10 | 3,729 | 5.18 | +1 |
| 3 | 06-14 18:40:40 | 06-14 23:33:35 | 3,516 | 4.88 | +1 |
| 4 | 07-22 02:37:50 | 07-22 07:21:35 | 3,406 | 4.73 | −1 |
| 5 | 08-27 02:24:55 | 08-27 06:55:20 | 3,246 | 4.51 | −1 |

**`DRW` runs SHORTER than `DR`, not longer.** 6.14 h against 7.19 h, and 2,507 runs against 2,487.
The wob suppresses short latching runs, so `DRW` moves the latch on fewer occasions — but the
stretches it does produce are tighter, because the two fences disagree about where a stretch starts
and ends. The two series' top stretches sit on the same calendar days, nine minutes apart at rank 1.

## `ArmState` — the reset interval, ws5Mage 50-crosses

| measure | value |
|---|---|
| 50-crosses on the tape | 15,899 |
| **longest gap between crosses** | 6,787 bars = **9.43 h** |
| median | **6 bars = 0.01 h = 30 s** |
| p90 | 152 bars = 0.21 h |
| p99 | 2,158 bars = 3.00 h |
| gaps ≥ 8 h | **3 of 15,900** |
| gaps ≥ 12 h | **0 of 15,900** |

| rank | from | to | bars | hours |
|---|---|---|---|---|
| 1 | 07-18 17:35:05 | 07-19 03:00:35 | 6,787 | 9.43 |
| 2 | 07-24 07:33:15 | 07-24 16:20:40 | 6,330 | 8.79 |
| 3 | 08-08 00:52:25 | 08-08 09:23:05 | 6,129 | 8.51 |
| 4 | 07-18 04:08:25 | 07-18 12:00:20 | 5,664 | 7.87 |
| 5 | 06-10 16:08:05 | 06-10 23:28:40 | 5,288 | 7.34 |

**ws5Mage crosses 50 a median 30 s apart** — 15,899 times in 94.5 days. The arm's state is almost
always a few bars old.

## THE BINDING NUMBER

| carrier | longest run, bars | longest run, hours | fits in a 104 h window |
|---|---|---|---|
| `rig.DR` — the walk's dr | 5,175 | 7.19 | YES |
| `rig.DRW` — rule#1's dr | 4,421 | 6.14 | YES |
| **`ArmState`** | **6,787** | **9.43** | YES |
| **the longest across all three** | **6,787** | **9.43 h = 0.39 days** | — |

**`ArmState` binds, not either dr.** I expected the dr to bind and it does not — the arm's reset
interval is the longest of the three by 2.2 h, because a 50-cross is a stricter reset condition than
a dr change.

### CORRECTED 1001 — THE LIVE WINDOW IS 14 h, NOT 104 h, AND THE COVER IS THIN

This section first compared against `StrategyLoop`'s **defaults** — `buffer_hours` 24 + `warmup_hours`
80 = 104 h (`optimus9/live/strategy.py:23`) — and reported 11.0× headroom. **o9-live does not use the
defaults.** `ops/run_o9live.py:37` passes `buffer_hours=8, warmup_hours=6`, and
`bl_detect.py:250-251` loads `end − (lookback + warmup)` hours, so the live tape is **14 h**. Found
by the o9-live recon session.

| carrier | longest run | cover at 104 h | cover at **14 h — what o9-live actually builds** |
|---|---|---|---|
| `rig.DR` | 7.19 h | 14.46x | 1.95x |
| `rig.DRW` | 6.14 h | 16.94x | 2.28x |
| **`ArmState`** | **9.43 h** | 11.03x | **1.48x** |
| **binding** | **9.43 h** | **11.03x** | **1.48x** |

**1.48x is the number, not 1.9x and not 11x.** The recon session's own message put the cover at 1.9x,
which is `rig.DR`'s — but the ARM binds, so the binding cover is 1.48x.

**AND THE 14 h WAS NEVER SIZED FOR CARRYING STATE.** The comment at `run_o9live.py:37` says
*"sweep-measured floors lb=6h/wm=4h (+margin); reproduces 12/24 exactly"* — measured for the **v2
producer's line warmup**, not for state convergence, and not for `octo-freedom` at all. Nobody has
sized a window for these three carriers.

**What 1.48x means.** A 14 h window covers the longest arm gap OBSERVED in 94.5 days with 4.6 h to
spare. It is not a proof: one quieter regime with a 14 h+ stretch between ws5Mage 50-crosses and the
live arm would carry a state the backtest does not, silently, and the recon would report it as
`selection`. 104 h would carry 11.03x. Which window `octo-freedom`'s producer gets is Joe's call.

## 1001 — THE WARMUP THE LINES NEED, AND THE 14 h CONFIG FAILS ON BOTH COUNTS

The o9-live recon session, chat #8: the 14 h is **8 h lookback + 6 h warmup**, and the warmup sits
BEFORE `win_start` to let lines settle — so the walkable span may be 8 h, not 14, and 8 h is less
than `ArmState`'s 9.43 h. It named the blocking unknown: nobody has measured how much warmup
`octo-freedom`'s lines need. Measured here — the FIRST FINITE BAR of every line the walk reads, on
the same 94.5-day tape.

| line | role | used by | first finite | bars | hours |
|---|---|---|---|---|---|
| `ws23` | r | momTF bucket + flat-runs | 06-05 18:24:00 | 4,608 | **6.40** |
| `ws22` | r | same | 06-05 17:58:00 | 4,296 | 5.97 |
| `ws21` | r | same | 06-05 17:51:00 | 4,212 | 5.85 |
| `ws20` | r | same | 06-05 17:40:00 | 4,080 | 5.67 |
| `ws18` / `ws19` | r | same | 06-05 17:06:00 | 3,672 | 5.10 |
| `ws5` | Mage | **the arm** | 06-05 15:05:00 | 2,220 | 3.08 |
| `ws13` | m | the dr pair | 06-05 13:00:00 | 720 | 1.00 |
| `ws1` | Mage | the dr pair + `coil_lines` | 06-05 12:37:00 | 444 | 0.62 |
| `ws3` | r | rule#1 leg | 06-05 12:51:00 | 612 | 0.85 |
| `ws2` | r | rule#1 leg | 06-05 12:34:00 | 408 | 0.57 |
| `gcws30` | Mage | `coil_lines` | 06-05 12:18:30 | 222 | 0.31 |
| `ws1` | r | rule#1 leg | 06-05 12:17:00 | 204 | 0.28 |
| `gcws30` | r | rule#1 scenario | 06-05 12:08:30 | 102 | 0.14 |

28 lines checked, ws4..ws23 all present. **`ws23r` binds the warmup at 6.40 h.**

### THE CURRENT CONFIG FAILS TWICE

| check | needed | available at `buffer_hours=8, warmup_hours=6` | verdict |
|---|---|---|---|
| warmup, so every line is finite at `win_start` | **6.40 h** (`ws23r`) | **6.00 h** | **SHORT BY 0.40 h.** `ws23r` is not finite at `win_start`, so the momTF bucket and the flat-run pool read NaN for ws23 at the window's start |
| walkable span, so the arm's state is covered | **9.43 h** (`ArmState`'s longest gap) | 14 − 6.40 = **7.60 h** | **DOES NOT COVER — 0.81x** |

### THE MINIMUM WINDOW

| component | hours |
|---|---|
| warmup the lines need | 6.40 |
| walkable span the arm needs | 9.43 |
| **minimum total** | **15.83** |
| the current config | 14.00 — short by **1.83 h**, and its 6 h warmup is itself short by 0.40 h |
| `StrategyLoop`'s defaults, 24 + 80 | 104.00 |

**6.40 h IS A FLOOR, NOT THE RIGHT WARMUP.** This measures when a line becomes FINITE. A line can be
finite and not yet equal the value it would carry with more history — that is convergence, and it is
NOT measured here. The real warmup is at or above 6.40 h, and sizing it is its own job.

**`run_o9live.py:37`'s 8/6 was never sized for this.** Its comment reads *"sweep-measured floors
lb=6h/wm=4h (+margin); reproduces 12/24 exactly"* — the **v2 producer's** line warmup, a different
line set, and no state carriers at all.

## WHAT WAS NOT MEASURED

| item | why it is absent |
|---|---|
| any tape but this one | 94.5 days ending 2026-09-08. A different regime could run longer; nothing here says it cannot |
| the `LeashWalk` per-episode fields (`_turn`, `_qual`, `_fr_starts`, `_departed`) | they reset on each new arm, so the arm's interval bounds them. Not measured separately |
| whether 104 h is the right window | that is the o9-live session's decision 2 and Joe has not ruled it. This gives the floor it has to clear, not the choice |
| the cost of a 104 h window per bar | not measured. It is 74,880 bars of line building every 5 s |

TL;DR: `rig.DRW`'s longest run is 6.14 h over 2,507 runs, shorter than `rig.DR`'s 7.19 h — but
`ArmState` binds at **9.43 h**, and o9-live's real window is **14 h**, which covers it by only
**1.48x** and was never sized for carrying state.

---

## SUPERSEDED 1001 — "MINIMUM TOTAL 15.83 h" IS WRONG. THE NUMBER IS 72.47 h

See `docs/octo-freedom/1001_warmup.md` for the measurement. What was wrong here:

| what this doc said | what it should have said |
|---|---|
| the warmup term is **6.40 h** — `ws23r`'s FIRST FINITE bar | the warmup term is **63.04 h** — the span at which `ws23r` stops disagreeing with the backtest. First-finite was the wrong criterion |
| minimum total **15.83 h** | minimum total **72.47 h** (63.04 + 9.43) |
| "the current config fails twice", short by 0.40 h and at 0.81x | it fails once, and by **5.2x**: 14 h vs 72.47 h |
| 104 h clears the floor by 11.03x | 104 h clears it by **1.43x** |

**The structure of the sum was right; the first term was wrong by 9.85x.** `indicator_computer._rma`
is recursive with `alpha = 1/rsi_len`, so role `r` carries its SMA seed forward as `0.8^N` in bars of
its own timeframe. A finite line is not a converged line — 0710 measured 15.4 r-points of seed error
on a finite `s5r` (`docs/arm_drift_rootcause.md`). Measured at 14 h, `ws23r` differs from the
backtest by **2.4e-02** r-points; at 104 h it differs by **0.000e+00**.

The two rows above that this does NOT change: `ArmState` still binds the state term at **9.43 h**
(re-derived in `1001_warmup.md` as the max ws5Mage 50-cross gap, 15,799 gaps), and the `bb` roles are
still window-invariant at every span down to 14 h.
