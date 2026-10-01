# 1001 — the warmup `octo-freedom` needs, and why `StrategyLoop`'s 104 h is not arbitrary

Joe asked: *"was there a reasong for strategyLoop's large warmup? I don't mind - whatever warmup is
decided is ultimately from your wheelhouse; I'm guided by your wisdom to ensure the calcs are
stable"* — so the decision below is mine and it is anchored to a measurement, not to a preference.

**This report supersedes `1001_dr_convergence.md`'s "minimum window 15.83 h".** That number used
FIRST-FINITE as the criterion. First-finite is the wrong criterion, and the correction is 4.3x.

---

## 1 — WAS THERE A REASON FOR THE 104 h?

No measured one. It was a placeholder, and the commit that introduced it says so.

| where | what |
|---|---|
| `optimus9/live/strategy.py:23` | `buffer_hours=24, warmup_hours=80` — 104 h, the defaults |
| the commit, `26692af` | *"WIP: bounded-window reproduction fidelity still open (buffer/warmup/alignment) — not yet the live path"* |
| the same line's own comment | `# bounded window; must reproduce the backtest line values (pin by measure)` — an instruction to measure it later, unexecuted |
| `ops/run_o9live.py:37` | `buffer_hours=8, warmup_hours=6` = 14 h. Comment: *"sweep-measured floors lb=6h/wm=4h (+margin); reproduces 12/24 exactly. TODO DB-source"* |

So the 104 h was never sized; the 14 h WAS sized, but for the **v2 producer's** lines. The 0710
measurement behind it is `docs/arm_drift_rootcause.md`, and it is the right piece of work — it just
answers a different question than `octo-freedom` asks.

**The window arithmetic, so the spans below mean one thing.** `StrategyLoop.window` →
`bm.BiasWindow(lookback=buffer_hours, warmup=warmup_hours)`; `bl_detect.py:250-251` computes
`win_start = end − lookback·3600000` then `load_start = win_start − warmup·3600000`. The decision bar
is at `end`, so **the tape behind the decision bar is `lookback + warmup`** — one number. 8+6 = 14 h
live, 24+80 = 104 h at the defaults, and the backtest Jig passes `lookback = hours + warmup` for
40 + 2×1114 = **2,268 h**.

## 2 — WHY FIRST-FINITE WAS THE WRONG CRITERION

`[read]` `indicator_computer._rma:256` — Wilder's RMA, SMA-seeded, **recursive with `alpha = 1/n`**.
Role `r` is `('k', rsi=5, stc=8, k_len=7, 'close')` (`mech_lines(db,'wsf')`, read from the DB, not a
literal), so `n = rsi_len = 5` and the seed error decays as **0.8^N** in bars of that line's own
timeframe. A line can be finite and still carry its seed: 0710 measured **15.4 r-points** of seed
error on a finite `s5r`, which is more than the width of every fence `octo-freedom` owns.

Gloss of the terms, since they set every number below:
- `rsi_len = 5` — the RMA's period; the only recursive stage in the `k` chain. `alpha = 1/5`, so each new bar of the line's timeframe retains 0.8 of the old error.
- `stc_len = 8`, `k_len = 7` — the Stoch window and the SMA window. Both are finite-window, not recursive, so they cost a fixed 15 bars and then nothing.
- `pxsmooth_dema_len = 2` (`optimus9_system`) — the one other recursion in the path. At length 2 it converges in a handful of 5 s bars and never binds.
- `bb` roles (`m`, `Mage`, `b`, `x`) — rolling mean/std, no recursion. 0710 measured them window-invariant and so does this report.

## 3 — THE MEASUREMENT: WINDOW INVARIANCE, 0710's METHOD, THIS MACHINE'S LINES

Build each line at a load span S ending at the SAME right edge (`END_MS` = 2026-09-30 00:00, the
repo's `TAPE_END`), compare against the 2,268 h production cache at identical timestamps, report the
worst disagreement over the last hour of bars (720 bars at 5 s).

### max |diff| vs the 2,268 h reference, last hour of bars

| line | 14 h | 20 h | 28 h | 40 h | 56 h | 72 h | 104 h | 144 h |
|---|---|---|---|---|---|---|---|---|
| `ws1r` | 9.9e-14 | 9.9e-14 | 7.1e-14 | 9.9e-14 | 9.9e-14 | 7.1e-14 | 7.1e-14 | 9.9e-14 |
| `ws2r` | 4.3e-14 | 2.8e-14 | 4.3e-14 | 4.3e-14 | 2.8e-14 | 2.8e-14 | 2.8e-14 | 4.3e-14 |
| `ws3r` | 2.8e-14 | 2.8e-14 | 2.8e-14 | 2.8e-14 | 2.8e-14 | 2.8e-14 | 2.8e-14 | 4.3e-14 |
| `ws4r` | 5.7e-14 | 5.7e-14 | 5.0e-14 | 5.7e-14 | 5.7e-14 | 5.7e-14 | 5.0e-14 | 5.0e-14 |
| `ws7r` | 2.5e-09 | 3.6e-14 | 2.1e-14 | 2.1e-14 | 2.1e-14 | 2.1e-14 | 2.1e-14 | 0.0e+00 |
| `ws13r` | 2.5e-04 | 3.4e-07 | 3.8e-11 | 5.0e-14 | 5.0e-14 | 5.0e-14 | 5.0e-14 | 4.3e-14 |
| **`ws23r`** | **2.4e-02** | **7.3e-04** | **2.1e-05** | **4.8e-08** | **1.2e-13** | **1.4e-14** | **0.0e+00** | **1.1e-14** |
| `ws1Mage` | 2.6e-09 | 2.9e-09 | 2.6e-09 | 2.6e-09 | 4.4e-09 | 1.9e-09 | 4.4e-09 | 2.6e-09 |
| `ws5Mage` | 1.5e-10 | 3.3e-10 | 3.3e-10 | 3.3e-10 | 3.3e-10 | 3.4e-10 | 3.4e-10 | 3.3e-10 |
| `ws13m` | 9.3e-10 | 0.0e+00 | 6.1e-10 | 9.6e-10 | 9.6e-10 | 9.6e-10 | 9.3e-10 | 6.1e-10 |

- `ws23r` is the binding line. It is the slowest timeframe carrying the recursive `k` role.
- the `bb` roles sit at 1e-9 or below at EVERY span, including 14 h — window-invariant, as 0710 found.
- NaN bars in the last hour: **0 for every line at every span**, including 14 h. First-finiteness is satisfied everywhere here; it is not the constraint.
- `gcws30r` is also a `k` line with the same role spec, but `itf_seconds = 30` **seconds** (`vw_indicator_configs_live`), so it converges in minutes and never binds.

### the decay model, checked against the measurement

`|diff| ≈ 0.8^(S·60/tf − 20)`, where 20 = `rsi+stc+k_len` = the windowed stages' fixed cost.

| line | span | measured | model | ratio |
|---|---|---|---|---|
| `ws23r` | 14 h | 2.447e-02 | 2.505e-02 | 0.98 |
| `ws23r` | 20 h | 7.272e-04 | 7.621e-04 | 0.95 |
| `ws23r` | 28 h | 2.078e-05 | 7.237e-06 | 2.87 |
| `ws23r` | 40 h | 4.771e-08 | 6.697e-09 | 7.12 |
| `ws23r` | 56 h | 1.243e-13 | 6.038e-13 | 0.21 |
| `ws13r` | 14 h | 2.522e-04 | 4.746e-05 | 5.31 |
| `ws13r` | 28 h | 3.836e-11 | 2.597e-11 | 1.48 |
| `ws7r` | 14 h | 2.487e-09 | 2.037e-10 | 12.21 |

The model tracks the measurement within one order of magnitude across eleven orders of magnitude of
|diff|. **It is an envelope, not a formula for the exact value** — the measured number is a max over
720 bars and fluctuates around the envelope. Good enough to derive a span to the nearest few hours;
not good enough to quote a span to the hour.

### span derived from the model

| tolerance | `ws23` | `ws13` | `ws7` | `ws4` | `ws1` |
|---|---|---|---|---|---|
| 1e-03 | 19.53 | 11.04 | 5.94 | 3.40 | 0.85 |
| 1e-06 | 31.40 | 17.75 | 9.56 | 5.46 | 1.37 |
| 1e-09 | 43.27 | 24.46 | 13.17 | 7.52 | 1.88 |
| 1e-12 | 55.13 | 31.16 | 16.78 | 9.59 | 2.40 |
| 1e-14 | 63.04 | 35.63 | 19.19 | 10.96 | 2.74 |

## 4 — THE SECOND TERM: HOW FAR BACK THE STATE REACHES

`arm_state.warmup_from(mage, k, floor, mid)` walks back to the **last ws5Mage 50-cross** before it can
step, so that gap — not the arm episode — is the state's dependency depth. `MID = 50.0`
(`arm_state.py:1`), the line is `ws5Mage` (`arm_line` in config v4), and the walk's own counters
(`_turn`, `_departed`, `_fr_starts`) are path-dependent from the arm bar forward, which is why
`ws23r` has to be converged at the ARM bar and not merely at the decision bar.

| quantity | hours |
|---|---|
| **max gap between ws5Mage 50-crosses** | **9.43** |
| 99.9th percentile | 5.86 |
| 99th percentile | 2.88 |
| median | 0.01 |
| gaps >= 6 h | 16 of 15,799 |
| gaps >= 12 h | 0 of 15,799 |

15,800 crosses / 15,799 gaps over the 94.5-day tape. The longest: 2026-07-18 17:35:05 →
2026-07-19 03:00:40. This re-derives the 9.43 h already banked in `1001_dr_convergence.md`.

## 5 — THE MINIMUM SPAN, AND THE DECISION

The two terms stack, because the span has to put `ws23r`'s convergence BEFORE the earliest bar whose
`ws23r` value the walk reads, and that bar is the arm's reach-back, not the decision bar.

| tolerance on `ws23r` | `ws23r` span | + arm reach | **minimum total span** |
|---|---|---|---|
| 1e-13 — measured at 56 h | 59.09 h | 9.43 h | **68.52 h** |
| 1e-14 — the float floor | 63.04 h | 9.43 h | **72.47 h** |

| configured value | span | clears 72.47 h? |
|---|---|---|
| `ops/run_o9live.py:37` — `8 + 6` | 14 h | **NO — short by 5.2x.** `ws23r` differs from the backtest by 2.4e-02 r-points |
| `strategy.py:23` defaults — `24 + 80` | 104 h | **YES**, 1.43x. `ws23r` measures 0.000e+00 |

**THE DECISION: `octo-freedom`'s producer runs on `StrategyLoop`'s 104 h defaults. The 8/6 override
is not applied to it.**

Why this and not a tighter number:
- 104 h is the only **already-configured** value that clears the measured requirement. It needs no new constant and no new sweep.
- the tolerance is not a preference. At 104 h `ws23r` measures **0.000e+00** against the backtest, which is the standard `strategy.py`'s own docstring already sets: *"Window-ending-at-now == the backtest window → live == backtest by construction"*. At 14 h that sentence is false by 2.4e-02.
- 72 h would be marginal against the 72.47 h requirement. 96 h would clear it, but picking 96 over the existing 104 buys nothing measured and introduces a constant nobody has justified.
- the 14 h is not a safety margin away from wrong — it is **5.2x short**, and the failure mode has a precedent: the three overnight `ARM-DRIFT ... DISAPPEARED (window-invariance broken)` alerts of 0710 were this exact bug in the v2 stack, at 15.4 r-points.

## 6 — WHAT THIS DOES NOT MEASURE

- **Wall-clock cost of a 104 h window for `octo-freedom`'s producer.** Unmeasured. The only datum is v2's, from commit `26692af`: *"ctor 2.74s→0.45s (6h buffer); decide ~1s at a 3-4h buffer vs 7.8s"*. The live loop's budget is one 5 s bar. If 104 h does not fit in it, the fix is a faster producer or a cached-state producer — **not a shorter span**, because the span is the measured requirement. Somebody has to time it before o9-live runs.
- **Verdict equality, as opposed to value equality.** This measures how far the line VALUES diverge. It does not measure at which span the 9 validated 09-01 bars stop reproducing. A span below 72 h might reproduce all 9 anyway, because a 2.4e-02 error only flips a test when a value sits within 2.4e-02 of a fence. The acceptance test `report_leash_walk.py` is the instrument for that run and it has not been run at a short span.
- **The 9.43 h is an observed maximum over 94.5 days, not a bound.** 0 of 15,799 gaps reach 12 h. A quieter regime with a longer gap would need a longer span, and nothing here proves one cannot occur.
- **Tape gaps.** 0710: *"A tape gap that shortens the effective bar count eats into it."* The spans here are wall-clock hours; a gap removes bars without removing hours. Unmeasured for `octo-freedom`.

## 7 — WHAT I AM NOT TOUCHING

`ops/run_o9live.py:37` is the o9-live recon session's file and it is on the live path. This report is
the measurement and the decision; the edit is theirs to make, or Joe's to direct.

---

## ADDED 1001 — THE THIRD CARRIER, AND A CORRECTION TO MY `px` CITATION

Both from the o9-live recon session, chat #18.

### the correction: `px` is the full 5 s base, NOT the event tape

I cited `trade_walk.py:118` for the stop's price series. That docstring says *"`pxs` = DEMA(close, 2)
on the event tape"* and **the "event tape" clause is wrong**. Traced:

| step | what |
|---|---|
| `trade_walk.walk(..., px, ...)` | the stop reads `px[pos['open']]` (`:134`) |
| `sweep_v3_signal.py:111, 125` | `rig.px` comes from `BWT.load(db, self.Ct)` |
| `build_wsf_trades.py:124` | `px = np.asarray(J.px, float)` |
| `jig.py:1386` | `self.px = np.asarray(self.W.px, float)` |
| `bias_machine.py:121-123` | `det = BLDetect(...)` ; `base, ts, _ws, _x, px = det._setup(end)` |
| `bl_detect.py:260-261` | `px = IC.dema(IC.build_source(base, 'close'), 2)` — comment: *"global 5s DEMA … NOT the old primary-TF resample"* |

**TWO px SERIES EXIST AND THE WALK READS THE OTHER ONE.** `rpl_cache._px_smooth_evt:59-69` does build
an event-tape px_smooth — *"DEMA of the price src over EVENT bars only, forward-filled"* — and stores
it as `__pxs__` in the tape npz. `BWT.load` does not read it. Anything that reasons about the stop
from `__pxs__` is reasoning about a series the stop does not use.

- `trade_walk.py:118` and `MVP2.md:43-53` both carry the stale "event tape" wording. 12th statement of this class.

### the third carrier: `trade_walk`'s own book

Named by the recon session: a re-walk that starts flat matches the live book only once both were last
flat, so the span has to cover the longest NOT-FLAT stretch. Measured without the unwired producer.

**How it is bounded.** `trade_walk` closes on the first of three — the 0.70% stop, the dr-flip, an
opposing `sig_utc`. The dr-flip alone bounds it. The dr latch alternates strictly
(`trade_walk.py:105-110`: a change needs `d[k] != d[k-1]` and `d[k] != 0`, and it never returns to 0),
so a trade opened in stretch `i` closes at the FIRST BAR of stretch `i+2`; the worst case opens on
stretch `i`'s first bar. So the bound is **the max sum of two consecutive dr stretch lengths**, and
the stop and the `sig_utc` only ever close EARLIER.

| quantity | hours |
|---|---|
| longest SINGLE dr stretch | 7.19 |
| **longest TWO consecutive = the book's bound** | **8.03** |
| 99.9th pct | 7.25 |
| 99th pct | 5.27 |
| median | 1.60 |
| bound >= 9.43 h | 0 of 2,503 |
| bound >= 12 h | 0 of 2,503 |

The longest: opens 2026-08-27 02:24:25, closes 2026-08-27 10:26:25. `rig.DR` first latches non-zero at
bar 761 = 1.06 h into the tape; 2,504 stretches, 2,503 changes.

### THE SPAN IS UNCHANGED AT 72.47 h

| carrier | hours | binds? |
|---|---|---|
| `ws23r` convergence to the float floor | 63.04 | yes, the line term |
| arm reach-back (ws5Mage 50-cross gap) | 9.43 | **yes, the state term** |
| book not-flat bound (dr-flip only) | 8.03 | no — 1.40 h inside the arm |
| **total: `ws23r` + the larger state term** | **72.47** | |

**The two state carriers take the MAX, not the SUM.** Both reach BACK from the decision bar over the
same bars, so one span of 9.43 h of converged lines covers both. They would only add if one sat
before the other.

### STILL NOT MEASURED, and this one is theirs

The book bound above is derived from the dr series, which is correct for any opener. What is NOT
measured is **octo-freedom's own book** — how many trades its `WALK FIRES FROM` bars actually open and
how long they stay open. `report_leash_walk.py` and `leash_walk.py` have **0** references to
`trade_walk`, so nothing in the repo produces it. The recon session's figure for 09-01 is 13 trades
from a scratch script, which is a written record, not a re-derivable result.

### CORRECTED 1001 — THE BOOK BOUND WAS MEASURED ON THE WRONG SERIES. SAME NUMBER.

The section above measured the book on `rig.DR` (oob 85/15, no wob). **`trade_walk` reads `rig.DRW`
for this machine** — `NOTES_momtf_mechdev.md:447`, `trade_walk.walk(opens, rig.DRW, rig.px, min(opens),
B, mae_cap 0.70)`, under Joe's ruling at `:442-445`: *"the dr series stays as the report ran it (arm on
dr_latch.latch NO wob, rule#1 on latch_wob 8)"* and *"use the same logic that banked the 0.3991"*.
`trade_walk.py:151, 157` set the trade's dr from the series handed in, and the dr-flip that closes the
book reads that same series. Found by the recon session, chat #20.

Re-measured on `rig.DRW` — `latch_wob(ws1Mage, ws13m, wob=8 bars = 40 s, hi=75.0, lo=25.0)`:

| quantity | `rig.DR` (signal) | **`rig.DRW` (the book's)** |
|---|---|---|
| first non-zero bar | 761 = 1.06 h in | 758 = 1.05 h in |
| stretches | 2,504 | 2,518 |
| longest SINGLE stretch | 7.19 h | 6.14 h |
| **longest TWO consecutive = the bound** | **8.03 h** | **8.03 h** |
| 99.9th pct | 7.25 h | 6.89 h |
| 99th pct | 5.27 h | 5.15 h |
| median | 1.60 h | 1.59 h |
| pairs >= 9.43 h | 0 of 2,503 | **0 of 2,517** |
| pairs >= 12.28 h | 0 of 2,503 | 0 of 2,517 |

- the longest pair on `DRW`: opens 2026-08-27 02:24:55, closes 2026-08-27 10:27:00 — the same calendar event as `DR`'s, within 30 s.
- **the 12.28 h the recon session named as possible (2 x 6.14) is not reached.** The two longest `DRW` stretches are not adjacent, which is why the pair has to be measured rather than bounded by twice the single max.
- **precondition checked, not assumed:** the two-stretch construction needs strict alternation and no return to 0. On `DRW`: 0 stretches valued 0 after the first latch, 0 adjacent stretches with the same value. `latch_wob` is a different producer from the inline oob latch and the check was owed.

**THE SPAN IS STILL 72.47 h.** Binding state term = max(arm 9.43, book 8.03) = 9.43; plus `ws23r`
63.04. The 104 h default still clears it by 1.43x.

### RULED 1001 BY JOE — THE BOOK'S SERIES IS `rig.DR`, NOT `rig.DRW`

Joe, asked which series the live trade book reads: *"it's the dr in this report"* — the 28-banked-signals
report (`target / dr / ARM state / arm bar / ... / WALK FIRES FROM`).

That report's `dr` column is `rig.DR`, oob 85/15, no wob. Verified:

| where | what |
|---|---|
| `report_leash_walk.py:180` | `walk(lad, mage, rig.DR, rig.CC, mom_at, fr_at, rev, k0, k1, **knobs)` |
| `report_leash_walk.py:144-147` | the v4 `walk_dr_*` recipe rebuilt and asserted against `rig.DR` — 0 of 1,632,960 bars differ |
| `sweep_v3_signal.py:99-106` | `rig.DR` = ws1Mage and ws13m both past 85/15, inline, no wob |

**So the preceding section's `DRW` correction was right about the SCRATCH RUN and wrong about the live
book.** `NOTES_momtf_mechdev.md:447` hands `rig.DRW` to `trade_walk.walk`; the ruling says `rig.DR`.
The 8.03 h bound is identical on both series, so nothing about the span moves.

| window | bars where `DR` != `DRW` | of | |
|---|---|---|---|
| whole tape | 68,250 | 1,632,960 | 4.18% |
| 2026-09-01 | 717 | 17,280 | 4.15% |

| fires from | DR | DRW | same |
|---|---|---|---|
| 00:27:35 | +1 | +1 | yes |
| 02:40:35 | −1 | −1 | yes |
| 03:38:00 | +1 | +1 | yes |
| 09:02:15 | −1 | −1 | yes |
| 14:50:00 | +1 | +1 | yes |
| 17:59:25 | −1 | −1 | yes |
| 18:20:00 | −1 | −1 | yes |
| 22:24:10 | −1 | −1 | yes |
| 23:18:50 | −1 | −1 | yes |

- **0 of 9 validated bars disagree on the trade's dr.** Same direction, same open bar, either series.
- the **stop is unaffected** — it reads `pos['dr']`, fixed at the open (`trade_walk.py:157`). So is an opposing `sig_utc`.
- **only a dr-flip close can move**, being the one exit that reads the series bar by bar after the open (`trade_walk.py:144-146`). 717 bars of 09-01 disagree.
- **NOT MEASURED:** whether any banked 09-01 trade actually closed on a different bar. That needs the day re-walked on `rig.DR`, and it is Joe's call whether to re-bank the day's MAE/MFE.

### 1001 — `arm_dr` vs `rig.DR` AT THE FIRE BAR: 0 of 23 ON 09-01, BUT NOTHING ENFORCES IT

Raised by the o9-live recon session, chat #23: the signal's direction is `arm_dr` — the dr latched at
the bar the arm SET — while `trade_walk` opens on `dr[k]` at the OPEN bar (`trade_walk.py:151, 157`).
If `rig.DR` flips between the arm bar and the fire bar, the walk emits one side and the trade opens
the other.

**THE STRUCTURAL GAP IS REAL.** `leash_walk.py:227`:

    adr = w.arm.arm_dr if w.arm.live else int(d[k])

Everything downstream — the coil sign, `mom_at`, `fr_at`, `rev_mask` — takes `adr`. **There is no test
that `rig.DR[k] == arm_dr` at the fire bar.** The dr-consistency test inside `ArmState.step`
(`int(dr_prev) == d`, `arm_state.py:84`) governs only the 6-bar arming RUN; once `live` is True a dr
change does not cancel the arm — only a ws5Mage MID (50) cross does (`arm_state.py:70-74`).

**AND `arm_same_dr` DOES NOT CLOSE IT.** `trade_config.py:96` defines the row as *"the arm dr MUST
equal the signal dr"*, value `'1'`. `grep -rn arm_same_dr` returns exactly two hits: that definition
and `report_leash_walk.py:116`, which PRINTS it. **No code reads it as a condition.** It is not a
broken guard — the condition holds by construction, because `leash_walk.py:227` makes the signal's dr
BE the arm's dr. It is a no-op knob: set it to `0` and nothing changes. Second row of this class after
`walk_dr_wob` (printed, unreadable by `latch`, now exits 1).

**MEASURED on all 23 run-first bars of 09-01**, on the acceptance test's own tape (END_MS
2026-09-08), with `arm_dr` parsed from that passing run's `R|` rows:

| run | FIRES FROM | arm bar | arm_dr | rig.DR @ fire | agree | validated |
|---|---|---|---|---|---|---|
| 1 | 00:27:35 | 00:19:20 | +1 | +1 | yes | YES |
| 2 | 02:40:35 | 02:38:10 | −1 | −1 | yes | YES |
| 3 | 03:38:00 | 03:36:55 | +1 | +1 | yes | YES |
| 4 | 05:44:10 | 05:30:05 | +1 | +1 | yes | — |
| 5 | 07:00:40 | 06:57:25 | −1 | −1 | yes | — |
| 6 | 08:09:15 | 08:06:20 | −1 | −1 | yes | — |
| 7 | 08:12:45 | 08:06:20 | −1 | −1 | yes | — |
| 8 | 09:02:15 | 08:06:20 | −1 | −1 | yes | YES |
| 9 | 11:30:20 | 10:32:30 | +1 | +1 | yes | — |
| 10 | 11:34:15 | 10:32:30 | +1 | +1 | yes | — |
| 11 | 11:37:00 | 10:32:30 | +1 | +1 | yes | — |
| 12 | 13:05:25 | 13:01:55 | −1 | −1 | yes | — |
| 13 | 13:54:20 | 13:49:15 | +1 | +1 | yes | — |
| 14 | 14:50:00 | 14:48:00 | +1 | +1 | yes | YES |
| 15 | 15:13:00 | 15:10:50 | −1 | −1 | yes | — |
| 16 | 16:16:10 | 16:08:45 | −1 | −1 | yes | — |
| 17 | 16:21:20 | 16:08:45 | −1 | −1 | yes | — |
| 18 | 17:59:25 | 17:58:30 | −1 | −1 | yes | YES |
| 19 | 18:11:35 | 17:58:30 | −1 | −1 | yes | — |
| 20 | 18:20:00 | 17:58:30 | −1 | −1 | yes | YES |
| 21 | 22:24:10 | 21:10:15 | −1 | −1 | yes | YES |
| 22 | 23:18:50 | 21:10:15 | −1 | −1 | yes | YES |
| 23 | 23:27:20 | 21:10:15 | −1 | −1 | yes | — |

| result | |
|---|---|
| run-first bars where `rig.DR[fire] != arm_dr` | **0 of 23** |
| of those, validated bars | 0 of 9 |
| `arm_dr == rig.DR` at the ARM bar, every row | True |

- **this is one day, and it is not an invariant.** The longest arm-to-fire distance here is run 21 at
  21:10:15 → 22:24:10 = 1.23 h, and the arm episodes reach 9.43 h elsewhere on the tape. A flip
  inside a long arm is exactly the case 09-01 does not contain.
- the acceptance test passed on this run: mech 2768, cut 1673, emitted 1095, runs 23; 9 of 9 validated bars reproduced as run-first bars, 0 missing.
- **UNRESOLVED, and it is Joe's:** which dr opens the trade when the two differ. Nothing needs deciding for 09-01, because they never differ there.

---

## RULED 1001 — THE WINDOW IS APPROVED AT 104 h, AND IT IS A COLD-START FIGURE NOT A PER-BAR ONE

Joe 1001: *"window is approved"*, and in the same breath: *"#4 rebuilding 104h every 5 seconds is
illogical. surely the walk must have an evolving cache?"*

**He is right, and the two statements are consistent once the 72.47 h is read correctly.**

| what 72.47 h is | what it is NOT |
|---|---|
| how much history the STATE needs behind it to be correct — `ws23r` converged (63.04 h) plus the arm's reach-back (9.43 h) | an amount of work to redo every bar |

Once the state is warm, advancing one bar costs ONE BAR of work. Nothing in the measurement says
otherwise; the per-bar rebuild came from `StrategyLoop`'s stateless design, not from the span.

### THE COST OF REBUILDING, AND IT IS AN ESTIMATE NOT A MEASUREMENT

Commit `26692af`, the only datum: *"ctor 2.74s->0.45s (6h buffer); decide ~1s at a 3-4h buffer vs
7.8s"*. Scaling a ~1 s decide at a 3-4 h buffer to 104 h is **~26x, so roughly 26 s per bar against a
5 s budget**. **DERIVED BY PROPORTION, NOT TIMED.** The timed build is still owed (the recon session's
first item) and would replace this figure.

### WHY IT WAS STATELESS, WHICH IS THE THING THE CACHE GIVES UP

`strategy.py:1-6`: *"Stateless by design: each closed 5s bar, run the SAME backtest producer on a
bounded window ending at now, and read ONLY the latest bar. Window-ending-at-now == the backtest
window => live == backtest by construction; no latch state to desync, self-healing every bar."*
And `OPEN.md`'s decision 1 records Joe's own earlier ruling: **re-walk a bounded window every bar.**

- the stateless shape buys **self-healing**: a desynced state cannot persist, because there is no state.
- the 0710 `ARM-DRIFT ... DISAPPEARED (window-invariance broken)` alerts are the failure class it was built against.

### THE CACHE IS NOT A NEW MECHANISM — THE PRODUCERS ARE ALREADY STEPPERS

| component | already incremental? |
|---|---|
| the `k` and `bb` lines | yes — `indicator_computer.f_k_lookahead` / `f_bb_lookahead`: *"rolling state on the closed series, single-step update at each 5s using developing values"* |
| the arm | yes — `arm_state.ArmState.step(k, ...)`, and it **RAISES** on a non-consecutive bar: *"ArmState.step must be called on consecutive bars"* |
| the walk | yes — `leash_walk.LeashWalk.step(k, ...)`, same guard |
| the trade book | yes — `trade_walk.walk` is a single forward pass reading only `dr[k]` and `dr[k-1]` |

**So octo-freedom's machine is already written as a bar-at-a-time stepper.** The stateless re-walk
throws that away and rebuilds from `i0` each bar. `ArmState`'s consecutive-bar guard is actively
hostile to the stateless shape.

### THE SHAPE THIS IMPLIES, AND THE ONE THING IT OWES

1. ONE cold build at startup over **>= 72.47 h** — 104 h as approved gives 1.43x.
2. then `step()` forward one bar per 5 s bar, carrying `ArmState` / `LeashWalk` / the line state.
3. **the debt: a periodic cold rebuild compared against the carried state.** That is the recon of the
   cache, and it restores the self-healing the stateless design had for free. Its interval is a value
   and is NOT set here.

**THIS SUPERSEDES `OPEN.md`'s DECISION 1** (*"re-walk a bounded window every bar"*), which was Joe's
ruling. He raised the reversal himself; it is recorded here as proposed, not applied.
