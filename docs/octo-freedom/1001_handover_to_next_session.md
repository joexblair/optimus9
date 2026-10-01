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
| the o9-live recon session | handed over, validated the port twice, filed its Phase 3 report, cleared to build the `WALK FIRES FROM` producer with `trade_walk` wired in |
| **P&L** | **REOPENED 1001** for backtest reporting AND o9-live. Percentage only — absolute needs a position size and none is set |
| the drag demarcation | written into `OPEN.md`, `MVP2.md` item 1 and `RECON.md`. Fee identical both sides, slippage assumed offline and measured live |
| `all_wsf_flatrun_grid` | re-gridded to 4-min anchors, 720 rows, both halves populated |
| task #24 | in_progress, and it is this work |

## WHAT IS OPEN, ON MY SIDE

| # | item | why it matters |
|---|---|---|
| 1 | **11 doc statements that contradict the code**, found by the recon session's validator. 4 are in `OPEN.md`'s Ruled table **unstruck** — `:16` (`latch_wob` is the walk's dr — it is not), `:27` (gate window 7 min — rule#1 reads 5), `:24` (config v3 — the walk loads v4), plus `CODE_MAP.md:97`. Also `README.md:142` (the knobs are not all v4), `README.md:144` (no repo code feeds the walk into `trade_walk`), `CAUSALITY.md:33`, `trade_walk.py:5` and `:119`, and two `NOTES` miscounts | the Ruled table is what a session is told is authoritative. Joe accepted the findings; the fixes are mine |
| 2 | the two NOT-ASKED-FOR conflicts: the dump's fields "not ruled" (`OPEN.md:55, 237`) vs "RULED" (`RECON.md:21`), and `OPEN.md:423` still saying "three closers" | Joe said fix both |
| 3 | **14 of 37 single-rule mutations get past every check**, and 5 more are caught only by the one-day acceptance test | the only thing that closes them is more validated days. Joe's gate: *"lazy-g will come after we've reviewed more days in the table you've built"* |
| 4 | `rig.DRW`'s stretch distribution is **unmeasured** | `rig.DR`'s longest unbroken stretch is 7.2 h over 2,487 changes, which is what settled the bounded-window ruling. `DRW` is at 75/25 wob 8 and nobody has measured it |
| 5 | **lazy-g** | Joe's name for the mech that carries the non-armed signals. Not built. His gate is more days first |
| 6 | MVP2 item 5, the **dr fence + wob sweep** | the 0926 *"we have to stick on 8"* ruling was measured on the 75/25 series, not the oob 15/85 one Joe calls his dr |
| 7 | the `sig_conf` re-bank of the 121 `wsf_leash` rows | Joe ruled *"rebank in place"* on 0929. Still un-applied. It is the 15 s |
| 8 | `walk_rule1_back_min` 5.0 min | Joe's ruling, load-bearing (changes the gate on 4 of 17 sampled bars), **never OOS'd** |
| 9 | `fastverdict.py` has no `verify()` | its own docstring names one. Proven on 8 of 23 timeframes, 5 of 90 days. Joe ruled: hand over with the gap stated |

## THE TRAPS THAT COST TIME

| trap | what to do |
|---|---|
| **the two-loader tape** | `Rig` loads the tape twice and `build_wsf_trades` binds `END_MS` **by value at import**. Any script walking more than one window must delete it from `sys.modules` after changing `END_MS`. `Rig.__init__` raises on a bar-grid mismatch — that guard is the fix |
| **`TAPE_END` is 2026-09-30 in the repo** | every banked number was measured at **2026-09-08**, and the tape is a FIXED 94.5-day width anchored on its END, so moving the end moves the start. `report_leash_walk.py` pins it for its own run |
| **numbers that live outside the repo** | three sets were lost or nearly lost this session: the grid's 20 `_bars` columns, v4's `walk_dr_*` rows, and the 09-01 MAE/MFE from a scratch `mae.py`. If a number cannot be re-derived from the repo it is a written record, not a result |
| **four fences, and they are not interchangeable** | oob 15/85 · Mage 25/75 · rule#1 27/73 · r-momo 17/83. `oob` in Joe's vocabulary is ALWAYS 15/85 |
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

**The check that caught the most:** before saving any file, ask — is every number traceable to a
command in this session; is the standard I am applying mine rather than Joe's or the code's; does
any sentence frame a non-causal option as the baseline; any evaluative adjective on a result; any
aggregate claim that should be per-case. The fourth and fifth catch the most.

**With P&L back on, bias 1 gets a new surface.** A number is easier to dress up and easier to run
down. The memory note `mae-mfe-only` keeps the ban's history for exactly this reason.
