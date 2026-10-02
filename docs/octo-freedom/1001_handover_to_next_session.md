# Handover to the next session on Joe's side of the work

Written 2026-10-01 by the session that built `octo-freedom` and handed it to the o9-live recon
session. This is for a fresh session continuing **the strategy work with Joe** — not for the o9-live
build, which has its own prompt at `docs/o9-live-recon/README.md` under `## The startup prompt`.

---

## THE PROMPT

> You are the master coder on `octo-freedom` in `/home/joe/thecodes`, branch `causal/lookahead`.
> Joe is the architect and the designer. Read these before anything else:
>
> | file | what it is |
> |---|---|
> | `.claude/joes-convo-style.md` | how to write to Joe. **One `TL;DR:` line, no three closers** — changed 1001 |
> | `docs/staying_light.md` | the house rules on scope and weight |
> | `docs/octo-freedom/README.md` | the machine in one table, and where reports live |
> | `docs/octo-freedom/1001_warmup.md` | the span: why 104 h, and the three carriers behind 72.47 h |
> | `docs/octo-freedom/1001_rewalk_on_ruled_dr.md` | the dr rulings, the `octo-sig` label, the walk-copy divergence |
> | `docs/octo-freedom/1001_rebuild_timing.md` | the recon session's timing — why shape B, measured |
> | `docs/22_go_20260921/NOTES_momtf_mechdev.md` | the day-by-day record, Joe's rulings quoted verbatim |
> | `docs/task_register.md` | the numbered task list he refers to by number |
> | your memory directory's `MEMORY.md` | ~50 one-line pointers; read the ones the task touches |
>
> **Joe's standing instruction, verbatim, and it governs everything:**
>
> *"we're in science mode, so always be raw with me and never infer. you are not the architect, and
> you are not the designer; you are the master coder - we exist as a team, and our roles are clearly
> demarcated. if you come to a unplanned decision while you code, stop and tell me what you see.
> develop principled code guided by SRP / when we're doing science, my absolute requirement is that
> you use only the mecahnisms I've given you to try and hit a target (if I've given you target). if
> you can't hit a full target, tell me why. if you can hit a full target but the mech doesn't exist,
> tell me what you want to change or build. you're not here to make data look good. the data you
> see as not good, is exactly the data I need to make decisions: you'll promise to not hide it from
> me"*
>
> **Then tell him what you understand to be open, and wait.** Do not start on the list below without
> him choosing.

---

## WHERE THINGS STAND

| thing | state |
|---|---|
| `octo-freedom` | validated, in the repo, acceptance test passes. 9 signal bars on 09-01, **one day only** |
| the o9-live recon session | **BUILDING, 1002.** Joe gave the go-ahead. `optimus9/live/octo_freedom.py` and `octo_inputs.py` exist, uncommitted; `trade_walk.py` and `leash_walk.py` modified by them. **The acceptance test has NOT been re-run against their edits** |
| the live shape | **B, ruled 1002 on measured timing.** Carry `ArmState` / `LeashWalk` / the trade book; rebuild the lines every bar. A (rebuild everything) is ~80 s against a 5 s budget. `1001_rebuild_timing.md` |
| the window | **104 h, approved by Joe 1002.** Minimum measured 72.47 h = `ws23r` 63.04 h convergence + the arm's 9.43 h reach-back. The book's own bound is 8.03 h, inside the arm |
| the recon reference | **RULED 1002: `leash_walk` + `arm_state`, not the v7 chain.** Joe: *"A is the only choice - causal all the way"*. `fastverdict` and `moments`/`release`/`coil_exit.resolve`/`i1`/`brk` all left the live path with it |
| **P&L** | **REOPENED 1001** for backtest reporting AND o9-live. Percentage only — absolute needs a position size and none is set |
| the drag demarcation | written into `OPEN.md`, `MVP2.md` item 1 and `RECON.md`. Fee identical both sides, slippage assumed offline and measured live |
| `all_wsf_flatrun_grid` | re-gridded to 4-min anchors, 720 rows, both halves populated |
| task numbering | **CORRECTED 1001.** This row said "task #24 \| in_progress, and it is this work". Wrong: `docs/task_register.md:53` has **#24 = "BL re-engage revive BB-twitch-faked exit"**, completed 0706. The #24 I meant is the SESSION's own task list (the harness one), a different number space from the register's. Caught by the recon session. **The register has no entry for any of the 9 open items above, and its newest section is dated 0918** — and #7 and #22 are each doubled in it too |

## WHAT IS OPEN, ON MY SIDE — REVISED 1002

**Joe's next job is lazy-g.** His words closing 1001: *"I'll be back for lazy-g dev soon"*. Everything
below is what is still open around it.

| # | item | state |
|---|---|---|
| 1 | doc statements that contradict the code | **PARTLY DONE.** `RECON.md` is fixed (step 3's chain row, step 4's reason list, the struck `fastverdict` paragraph, the rule#1 row). `build_wsf_trades.py:18` struck. **Still open:** `OPEN.md:16`, `:24`, `:27`, `CODE_MAP.md:97`, `README.md:142`, `:144`, `CAUSALITY.md:33`, `trade_walk.py:5`, and the two `NOTES` miscounts |
| 2 | the two NOT-ASKED-FOR conflicts | unchanged. `OPEN.md`'s dump-fields row and its "three closers" line |
| 3 | 14 of 37 single-rule mutations pass every check | unchanged. Joe's gate: more validated days. **This is what gates lazy-g** |
| 4 | ~~`rig.DRW`'s stretch distribution unmeasured~~ | **CLOSED 1002.** Longest single stretch 6.14 h, longest two consecutive (the book's bound) 8.03 h, 2,518 stretches. `1001_rewalk_on_ruled_dr.md` |
| 5 | **lazy-g** | not built. **JOE'S NEXT JOB.** His 1001 ruling: *"lazy-g sits BESIDE rule#1, not behind it"*. The 4 non-armed signals it carries on 09-01 are 05:01:30, 07:27:15, 12:41:45, 17:27:50 |
| 6 | the dr fence + wob sweep | **RE-AIMED 1002.** Joe: *"fence25 and the wob are destined for a sweep at the end of octo-freedom's MVP2"* — a DIFFERENT MVP2 from `docs/o9-live-recon/MVP2.md` item 5. wob 8 and fence 25/75 banked unchanged meanwhile; wob 7 would hold +1.2032 and move the backstop earlier, but the 6->7 step is one trade on one day |
| 7 | the `sig_conf` re-bank of the 121 `wsf_leash` rows | **STILL OPEN, and 1002 sharpened why.** The rebuilt chain is NOT 15 s early — `coil_exit.first_forward:112` returns `sc[k]`. **The 15 s belongs to the BANKED `wsl_sig_utc` rows only**, which is exactly what this re-bank fixes. Joe ruled *"rebank in place"* 0929 |
| 8 | `walk_rule1_back_min` 5.0 min | unchanged, **never OOS'd**. And note the trap it caused: `gate_open(k)` with no second argument resolves to `rule1_back_min` 7.0 = 84 bars from v3 |
| 9 | ~~`fastverdict.py` has no `verify()`~~ | **NO LONGER A LIVE RISK, 1002.** It left the adopted path with `measure_live_stop.build`; `octo-freedom` never calls `.sideways()`. Still a true fact about `fastverdict` |
| 10 | **NEW — the walk-copy divergence** | `bank_emit_entry.walk_no_flip_open` is the only one of five copies missing Joe's 0929 same-dr-inert clause. It fired on **18 of the 36 `sig_utc` closes** in the 67 rows it banked, 5 of them same-bar close-and-reopen. **PARKED by Joe** — zero recon impact. Re-banking is his call and goes BESIDE the rows, never over |
| 11 | **NEW — task #69**, the lookahead quarantine | registered 1001. The leash code has NO lookahead code, only the docstring proving it; the `brk` emit-bar formula lives in `sweep_v3_signal.py:242-243`, `bank_emit_entry.py:86-87`, `compare_rowfree.py:91-92`. Joe rules on the docstring question before any edit |
| 12 | **NEW — `octo-sig` + the open's dr into `trade_walk`** | Joe ruled the label `octo-sig` and that the ARM's dr governs the open. Two optional arguments, defaulting to today's behaviour so the v7 callers do not move. The recon session is building it |

## THE TRAPS THAT COST TIME

| trap | what to do |
|---|---|
| **the two-loader tape** | `Rig` loads the tape twice and `build_wsf_trades` binds `END_MS` **by value at import**. Any script walking more than one window must delete it from `sys.modules` after changing `END_MS`. `Rig.__init__` raises on a bar-grid mismatch — that guard is the fix |
| **`TAPE_END` is 2026-09-30 in the repo** | every banked number was measured at **2026-09-08**, and the tape is a FIXED 94.5-day width anchored on its END, so moving the end moves the start. `report_leash_walk.py` pins it for its own run |
| **numbers that live outside the repo** | three sets were lost or nearly lost this session: the grid's 20 `_bars` columns, v4's `walk_dr_*` rows, and the 09-01 MAE/MFE from a scratch `mae.py`. If a number cannot be re-derived from the repo it is a written record, not a result |
| **four fences, and they are not interchangeable** | oob 15/85 · Mage 25/75 · rule#1 27/73 · r-momo 17/83. `oob` in Joe's vocabulary is ALWAYS 15/85 |
| **a truncated grep is not a result** | twice in one day I piped `grep` to `head`, saw no hit, and stated a count. `opened_by='sig_utc'` is at **5** sites not 4, and `brk` IS in `sweep_v3_signal.py:242-243`. Count with `grep -c` or no `head` |
| **TWO px SERIES, and the stop reads the other one** | `rpl_cache._px_smooth_evt:59-69` builds an EVENT-tape px_smooth into the tape npz as `__pxs__`. `BWT.load:124` never reads it — it takes `J.px`, which is `bl_detect._setup:261`'s DEMA(close,2) over the FULL 5 s base. Anything reasoning about the stop from `__pxs__` has the wrong series |
| **FIVE copies of the trade walk** | `trade_walk.walk` plus `walk_no_flip_open` in `sweep_v3_signal`, `bank_emit_entry` and `sweep_mae_cap`, plus `measure_live_stop.walk`. Four carry Joe's same-dr-inert clause; `bank_emit_entry`'s does not. A signature change reaches none of the copies |
| **two dr series in one machine** | the walk reads `rig.DR` (oob 85/15, no wob, inline at `sweep_v3_signal.py:99-106`); rule#1 reads `rig.DRW` (Mage 75/25, wob 8). `dr_latch.latch()`'s module defaults are 75/25 — pass `hi=85.0, lo=15.0` for the walk's series |

## MY OWN BIASES, MEASURED THIS SESSION

Read these before the first substantive reply. Each recurred, and Joe caught each one.

| # | the bias | the instance |
|---|---|---|
| 1 | **measuring Joe's banked work against the strictest conceivable standard and reporting the shortfall as a defect** — four times in one day | framed the bank's 15 confirmed releases as "the artefact" and a wider-bound 30 as "the causal truth"; wrote a cost table for a discipline already in the code; put a non-causal scan bound in the handover as "what a live walk naturally scans"; labelled the entry bar LOOKAHEAD on a count that overstated it by 8 of 23 rows. Memory: `strictest-standard-bias` |
| 2 | **building a results table from memory instead of from the file** | fabricated cells — *"oob 15/85 \| 4 of 6"* when the run said 1 of 6 — and built a conclusion on them. The direction is the tell: it made my own choice look viable. Memory: `tables-from-the-file-not-memory` |
| 3 | **claiming a proof that does not exist** | cited a `test_arm_state.py` that I had not written, which is exactly `fastverdict.verify()`'s failure. Caught by my own per-file check before Joe saw it |
| 4 | **stale sentences surviving the code that falsifies them** | five statements in the handover contradicted the machine within hours of my writing both. The validator found them, not me |
| 5 | **announcing a decision instead of asking** | BUILD-GATE means stop BEFORE the unplanned decision. Telling Joe as I run it takes the decision from him. Memory: `announcing-is-not-asking` |

### ADDED 1002 — ONE BIAS RECURRED THREE TIMES IN ONE DAY

| # | the bias | the instances |
|---|---|---|
| 6 | **writing from a docstring instead of the code it describes** | three times. (a) `brk` re-entered a live argument from `bank_emit_entry.py`, a banker I had just read, on a path where `brk` has 0 occurrences — and *"raising a mechanism in order to dismiss it"* was the tell. (b) wrote `Rig.gate_open(k)` into `RECON.md` when the bare call resolves to 84 bars, after authoring the docstring that warns about exactly that. (c) cited `build_wsf_trades.py:18` as authority for a `sig_conf` defect that does not exist — and `CAUSALITY.md:174` had the correct statement all along. Memory: `dropped-mech-reentry` |
| 7 | **taking the majority as the reference** | called `bank_emit_entry`'s walk copy DIVERGENT because two others agreed, without reading the ruling. The conclusion survived — `trade_walk.py:12-22` does carry it — but by luck, not method |
| 8 | **a denominator that flattered the finding** | published "18 of 67 = 23.9%" for the divergence. The 67 rows hold only 36 `sig_utc` closes, and the test only applies to those. It is **18 of 36 = 50%**. Also published a floor of "at least 16" resting on a skip count I never ran |

**Joe, on all of it:** *"no burden — you're working in a codebase that historically changed tack on a
whim (my doing) in short intervals."* He is right, and the count supports him: ~14 stale doc
statements were found in one day. **The docstrings are a LAGGING index; the code is the only one that
is not.** The fix is one habit, not vigilance — grep the file you are about to cite.

**The check that caught the most:** before saving any file, ask — is every number traceable to a
command in this session; is the standard I am applying mine rather than Joe's or the code's; does
any sentence frame a non-causal option as the baseline; any evaluative adjective on a result; any
aggregate claim that should be per-case. The fourth and fifth catch the most.

**With P&L back on, bias 1 gets a new surface.** A number is easier to dress up and easier to run
down. The memory note `mae-mfe-only` keeps the ban's history for exactly this reason.
