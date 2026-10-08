# Task register — carried forward (0707)

*The harness TaskList is session-scoped and won't auto-carry. This is the durable copy. New session: read this;
re-seed into the harness via TaskCreate if you want live tracking. Statuses as of 0707. IDs match the old session.*

**Active / near-term (the o9-live reconcile thread — see `handover_o9live_reconcile.md`):**
- **#54** [ACTIVE] o9-live under-fires vs backtest — look-ahead + realtime-fidelity gap. *Now = the reconcile: root is the EXIT (flip past SL), signals reconcile. Halted, $364.*
- **#55** [pending] Hedge mode — make o9-live match the backtest (independent long+short books). *Next in plan; review Bybit hedge-mode mechanics.*
- **#44** [pending] Wick-ignore for exit/SL price — live via Bybit index_price. *0707: reclassified — o9-live SL uses the bar CLOSE not a wick, so this doesn't apply to the −0.7 knife-edge; kept for a true index-price exit later.*
- **#9** [pending] Exit rule: take-the-money-and-run (>1% in 15s) — grind params. *Related to the exit work.*
- **#48** [pending] Daily o9↔Bybit reconciliation (o9_account tally vs exchange balance).

**Pending — ws-finisher / domTF (see `handover_wsf.md`, `handover_momo_refactor.md`, `ws-finisher_spec.md`):**
- **#60** [pending — Joe holds the start] The sampling width for the wsf stall, timeframes 1 to 8.
  Joe 0817: *"domTF and wsf stall logic are the same. the only difference would be in the sampling
  interval - less width for smaller TFs"* and *"we'll need to tune it based on the results. I don't
  know what results I'm looking for yet"*. Joe 0818: *"it is too early for 5 to be considered. I'll
  let you know when we need to adjust sampling"*. **Do not start until Joe says so.**
  - the measurement that opens it: at the module default `MOMO_FIXED_SAMPLES` = 0 (0 = the gap
    between lattice points stays at `MOMO_STEP_MIN` = 5 minutes and the point count is whatever the
    window divided by that gives), timeframes 1, 2 and 3 all get the same lattice — 2 points, 300
    seconds apart. "Less width for smaller TFs" has nothing to act on below timeframe 4. At
    timeframe 1 that 2-point lattice spans 5.0 minutes against a 4-minute window.
  - at `momo_fixed_samples` = 21 the floor is gone: gap 10 s at timeframe 1, 25 s at 2, 35 s at 3.
  - the stall's lattice IS the momentum lattice — `build_ws_fin.py` reads `MOMO_STEP_BARS` and
    `MOMO_SAMPLES` out of `momo_window(k_window x TF)` and hands them straight to
    `jig.stall_mask(y, dr, n, step, samples)`.
  - **SUPERSEDED 0903, the closing question is gone.** This entry used to end "two ways it can go,
    both Joe's call: set `MOMO_FIXED_SAMPLES` to 21 everywhere, or leave the default and accept
    that timeframes 1 to 3 share one lattice." There is no default any more. Every momentum knob
    moved to the `momo_config` table, `momo_fixed_samples` is 21 in both banks, and an unbound call
    raises instead of falling back. The two statements this entry made about where the value came
    from — that `build_ws_fin.py` sets 21 at import and that `momo_gated.py` defaults to 0 — are
    both false as of 0903. **What is still open is unchanged: the sampling WIDTH for TF1-8.**

- **#61** [pending] Sweep the ws{weak-mage-tf}x cross target — the line the fast partner has to
  cross before a trade signal is created. Joe 0818: *"I'm not sure if we x-cross m, or x-cross
  [Mage,boundary,b]"* and *"use ' x X [MAge,b,boundary]' for now"* and *"add a sweep task for all
  3"*.
  - the three targets to sweep:
    - `x X r` — the fast partner crosses ws{weak-mage-tf}r. This is what the first draft said
    - `x X m` — the fast partner crosses ws{weak-mage-tf}m
    - `x X [Mage, b, boundary]` — CURRENT SETTING per Joe 0818
  - open inside the third target: whether the cross must be of ALL of Mage, b and the boundary, or
    ANY one of them. Not asked yet.
  - the cross direction, Joe 0818 verbatim: *"x crosses over if dr==-1, and x crosses under if
    dr==1"*. Read as: bias down -> the trade fires when the fast partner crosses UP over the
    target; bias up -> it fires when it crosses DOWN under the target. NOT YET CONFIRMED by Joe.
  - blocked on: nothing measures ws{tf}x at all. The lines are cached for timeframes 1 to 8 but
    `wsf_line_bar` holds only the r lines.

**Completed (0706 or earlier):**
- #8 cbls3 lookback back-only vs ±window · #12 s30r/s30M swing-line dial-in grind · #24 BL re-engage revive BB-twitch-faked exit · #25 re-cast BL re-engage on 5s via wobble_slayer · #29 hb9M src hl2 vs close · #32 bias machine on s22r bls3 · #33 per-bl_line emerging-vs-closed flag · #45 re-clone s5 @ multi 0.65 vs s7 exits · #49 integration tests must not write live o9_live DB.

**Pending — BL / bias / lines:**
- #7 bl_review combo selection: active-combo table
- #10 bl_review: add c_bls, bny30 bias, lookback-made-trade columns
- #11 Companion report: group-level BL analytics
- #13 HTF overlap: does it raise s30r's swing-follow rate
- #14 bl_dialin durable-process grind (7h) + staged analysis
- #15 Fix OOB→OOB side-flip bug in breaching_line state machine
- #16 Make bny30M a swappable line (gate stays "bny30 gate")
- #17 Source BNY30 gate config from ic (versioned), not the hardcoded constant
- #18 Re-grind lookback trades with a WIDER lookback sweep
- #21 Reconcile the BL line-positioning BRD with code (curl/exit gating, exit3 staging)
- #26 Grind BL support BB src (hb{tf}M) + wobble n/strict vs reliable prediction
- #36 Trade-exit: scale the exit-line TF with the pk-source TF (SnF)
- #37 [in_progress] Bias machine additional mechanics
- #40 BiasState producer weighting/priority (reopen if needed)
- #42 value_mode + anchor: make ALL line consumers honor the per-line toggle
- #43 A/B s14M value_mode for the lr bias gate (closed vs emerging)

**Pending — arm / cascade (much of this was explored + shelved 0706 — see handover before re-running):**
- #50 s5m len 6-vs-8 isolated A/B
- #51 Revisit arm-delay research ideas (divergence confirm · crossover trigger · leg-amplitude gate)
- #52 Arm-delay pre-o9-live validation (look-ahead audit · OOS · overlap accounting)
- #53 arm_unlatch_lookback knob (conditional build)
- #56 A/B arm-unlatch reversal line: s5Mage vs s7Mage
- #57 Arm base-trigger: s5m reversal (spec) vs s5m breach (validated build)
- #58 Arm producers read _line (non-causal) not W.line (emerging) — look-ahead root *(largely done: #58 flip committed 40f13b8; exit-side `_finisher_signal` still on `_line`)*
- #59 A/B sweep wob values: event-tape vs index-tape counting

**Pending — infra / tape / services / cleanup:**
- #19 Tick collector: detect non-tradeable index wicks
- #20 Consolidate pk machine spec into one doc
- #22 Check kline + kline_audit services (insert load, correctness)
- #23 Apply MySQL conf proposals after bl/bias is baked
- #27 Realtime line-calc systemd service (active BL + bias lines per 5s print)
- #28 Slow-burn: migrate global OOB 85/15 from constants.py → optimus9_system.hi/lo_boundary
- #30 Periodic dead-code cleanup (sunset register — review before deleting)
- #31 Durable spec + process for grind-result storage (tame the ~16-table sprawl)
- #34 Seed/migrate trade_gate + trade_gate_line (reproducible on a fresh DB)
- #35 Audit all class default values + hoist to the DB (no-hardcode sweep)
- #38 Indicator config spec/readme
- #39 Detect institutional super-wicks (flow markers, setup precursors)
- #41 Synthetic tape patches — re-backfill with wiggle or flag
- #46 Check GPU support opportunities (sweep eval hot path)
- #47 gcs5/gcs1 finishers → replace s30Mage-wob (first post-infra job)

**New (fell out of 0706, not yet formal tasks):** state-log double-logging bug (arm written 2–10×/bar) · ~9% arm over-fire · sunset the orphaned st5 + s1m/s1r seeds · o9-live pyramid/hedge sizing to match backtest.

---

## 0903 — the momentum knobs became a per-machine bank

Joe: *"I want the settings to be global per machine, ie dtf and wsf will have their own config"* /
*"it seems like now is right for a SRP refactor"* / *"whatever SRP tells you. we have a no
hardcoding rule"*.

- **the bank.** `momo_config` table, `build_momo_config.py`, read by `optimus9/compute/momo_config.py`.
  Eleven knobs, one bank per machine, **keyed on the line's own timeframe**: `wsf` 1..12, `domtf`
  13..60. A caller passes the timeframe it already holds and never names a machine.
- **`momo_core` and `momo_gated` own no numbers.** All eleven ship as `None`; an unbound call raises
  a plain error naming the file and the two lines needed to bind. There is deliberately no default —
  a default is what let one machine run on another's values.
- **proven value-neutral.** `verify_momo_refactor.py`, old code from git `5a9c604` against new, both
  sides frozen on the 0818 numbers: **473,976 + 216,378 comparisons, 0 mismatches**. A 150-row
  report also came out byte-identical through the new path.
- **twelve files converted.** `build_ws_fin`, `build_wsf_line_bar`, `build_wsf_event_mark`,
  `build_wsf_marker_snapshot`, `build_wsf_walk_events`, `report_wsf_bar`, `report_domtf_walk`,
  `build_momo_landed`, `build_handoff`, `verify_momo_refactor`. `optimus9/analysis/domtf.py` and
  `build_wsf_ingredient.py` needed no change. `build_momo_landed` and `build_handoff` run TF8..33,
  which crosses both bands, so they bind per timeframe.
- **three knobs changed value**, baked in by Joe: `k_window` 4 -> **6**, `momo_slope_min` 1.0 ->
  **1.2**, `momo_r2_min` 0.50 -> **0.70**. Chosen by a 75-setting grid scored against eight
  eyeballed 08-04 pivots on **ws20r only**. **FITTED, NOT MEASURED.**
- **four silences fixed.** The 50 gate was implemented twice, once following the shared knobs and
  once on `report_wsf_bar`'s own copies, so the gate printed differed from the gate applied by up to
  ~1 point; `momo_core.level_gate()` now owns it and both callers use it. Three files assigned
  `MOMO_FIXED_SAMPLES` over whatever a caller had bound. `build_ws_fin._tag_one` passed one knob to
  its worker processes and inherited the other ten by fork.
- **sunset**, Joe: RPL (*"RPL is sunsetted"*), the s46 path (*"s46 is dead"*), `build_ws_momo`
  (*"sunset build_ws_momo"*). None binds a bank; none is expected to run.
- **the A/B**, Joe: *"wsf_event_mark is our current state - let's get an AB on that"* and
  *"duplicate the table before re-keying"*. `wsf_event_mark_ab`, 281 events x 2 knob sets, keyed on
  the momentum knob set so both readings live side by side. **187 of 281 readings changed** —
  68.2% of the 154 he marked `poor`, 62.5% of the 56 `good`, 66.2% of the 71 unmarked. Joe 0903:
  *"the AB changes are accepted"*.
- **all knobs are now listed in one place**: `docs/ws-finisher_spec.md` -> KNOBS. Joe: *"dtf and wsf
  knobs will both live in the wsf spec"*.

---

## 0824 — the domTF repair and the setup model

**Where the work stands.** The domTF mechanic was lifted out of `build_ws_fin.py` into
`optimus9/analysis/domtf.py` and its direction, state and delegation were re-specified by Joe.
The wsf setup model has its first two labelled rows.

**Live and settled:**
- `optimus9/analysis/domtf.py` — the domTF mechanic, one home. `blocking_at` is the verdict lifted
  verbatim from `build_ws_fin.py` (0 mismatches at all 121 signal bars, and 0 against the banked
  rows). `build_ws_fin.py` imports it.
- the guide-wire is **ws13x**, 85/15, 6-bar hold, `guide_wire_dr`. dr -1 while low out of bounds,
  +1 while high, 0 between. It does NOT latch — Joe 0823 reverted the latch experiment.
- **dtf-blocked / dtf-free replaces the handoff as an event.** Joe 0823: *"we're dropping the
  handoff mech. wsf will now query the state whenever it makes a trade decision"*.
- **minimum held 25 s.** A state under that does not happen; neighbours merge through it.
  50 runs → 35 before 04:00 on 08-04.
- **a dtf-free row carries the dr of the blocked state it ended.**
- **the wsf facing direction**, `jig.wsf_facing_dr`: gcws30Mage, ws1Mage and ws2Mage all above 80 →
  dr +1, all below 20 → dr -1, otherwise no dr and a stub row. No hold.
- **dr +1 = SHORT, dr -1 = LONG.** Joe 0824, confirming a call at 00:13:00.

**Tables built 0823-0824:**

| table | what it holds |
|---|---|
| `domtf_wsf_report` | the chronological domTF flips + validated wsf-exhaust events |
| `domtf_x_excursion` | one row per x-line excursion, ws27x / ws20x / ws14x, 272 rows |
| `dtf_state_flip` | Joe's labelled dtf state flips |
| `dtf_delegation` | 85 delegation moments on 08-04 with the wsf facing reading. **84 are stub rows** |
| `wsf_setup_board` | one row per setup x line, the 20 wsf-model-report columns |
| `wsf_setup` | one row per setup, the derived features and Joe's verdict |

**OPEN, and they are Joe's:**
- **#62 the nested-opposition rule vs modelling.** It fires on 28 of 121 signals and provably missed
  the lines Joe named on the bar it was written for (03:53:00: he named ws15r-ws18r, the machinery
  reads all four as none in both directions). Replacing it needs labels.
- **#63 the domTF state has no minimum hold beyond the 25 s gate**, and the momentum still flickers —
  six state changes in the 13 minutes from 03:50:10.
- **#64 `x-cross_forced_wsf-exhaust` has no meaning on a dtf row.** The column exists and is blank.
- **#65 three wsf-exhaust rows lost to the rising-edge fix** — 07:21, 09:19, 22:24, all ELIF rows.
  They depend on task #4, the ELIF mechanic, which Joe deferred.
- **#66 the 3-minute facing lookback lets a facing survive its own reversal.** 00:13:00 is the first
  concrete case. Joe's no-hold reason argues against it; the lookback is his and unmeasured.
- **#67 the setup model has 2 labelled rows against 83 unlabelled delegation moments.** The honest
  test is 08-05 run cold. In-sample agreement is not a result.
- **#68 "do we need to add this to dtf modelling?"** — the RESCUE_REJECTED_CURL pretext, verbatim, in
  `docs/dtf_htf_curl_question.md`. Joe 0824: *"the modelling plan for dtf that we've agreed on in
  principle (earlier today) might use this dtf HTF curl data, but not in the way that I originally
  considered"*. Carries two sub-items: Joe's unbuilt sideways-vote idea (ws13/14/15 rated above
  ws22+, band edge unset — *"the tuning process will expose it"*), and the fact that
  `build_dtf_delegation.py` omits the rescue.

**SETTLED 0824:**
- **the 85 dtf-free events are VALIDATED.** Joe: *"the 85 dtf-free events are validated"*.
  `dtf_delegation` is the ROOT TABLE — every `wsf_setup` row traces to a `dds_seq`.
- **next session starts at 00:14:50**, delegation row 3. See `docs/wsf_setup_model.md` section 3.14,
  which carries the exact command, what the root table already says about that bar, and the four
  things misread at 00:13:00 so they are not repeated.

## #7 review pyramids - two trades firing together, Joe 0828

Joe, verbatim: *"there is a deeper spec needed to handle 2 trades that fire together; if we place 2
standard sized trades together, we'll create unwanted slippage"*.

MEASURED, the case that raised it. Trace of the walk 00:00 to 01:13:35 before the gate:

    12  00:58:25  dr -1  forced  watch ws3  cross 01:02:35  opposing dr - closed the pool, took slot 1
    13  00:59:50  dr -1  forced  watch ws3  cross 01:02:35  took slot 2 of 2

Two forced exhausts 85 s apart, both fixing ws3 as the weak-mage line, both resolving to the SAME
cross at 01:02:35. Two trade slots, one x-cross timestamp.

THE 0828 GATE DOES NOT FIX IT. The in-flight gate suppresses a maxtf or plain exhaust firing between
an exhaust and its cross. A forced exhaust fires through it, on Joe's word, so 00:59:50 still fires
and the duplicate stands. That duplicate is what this task exists to spec.

OPEN. No sizing model exists. `MAX_TRADES` = 2 is Joe 0825: *"allows pyramiding, max 2 trades"*.
Nothing in the walk or the tables carries trade size, and slippage is not modelled anywhere.

## #22 mage-cascade — PARTIALLY UNPARKED 1007. The direction half is live; the tolerance half stays parked

**1007 UPDATE.** Joe asked *"do you feel confident to unpark #22 and use it for the A/B?"* and the
answer was yes to one half only.

**UNPARKED — the direction read.** `ws12Mage > ws1Mage`, which is Joe's §3 verbatim 0918: *"the
first thing I look at is the lowest TF's value, and the highest TF's value ... I can draw a mental
downward line between those 2 numbers"*. It references NO dr, so the blocker below is satisfied by
construction, and it carries zero knobs. It is live in `ws12_baton_config` v1 as the re-entry gate
and scored +13.3928 over 09-25 and 09-26 against +9.2482 for "all Mages above 50".

**STILL PARKED — the tolerance read.** The bump count and every threshold:
- §7: bumps >= 8 / dr -1 was +0.340 on 12 clusters in-sample against **-0.478 on 127 clusters OOS**
- §3's *"making allowances for the bumps"* - the allowance size is exactly what was fitted
- §9: all three r tests null on 83 days, so no r-trajectory component
- the ladder peak TF is unruled and noisy: ws5, ws9, ws9, ws4, ws12 across five measured bars

**TWO 0918 SHAPE FINDINGS CONFIRMED on the 1007/1008 bars**, both dr-free:
- §7's `clusters` as the effective-n device - the re-entry returns arrive in bursts, so 08:11's
  three bars are ONE event sampled three times
- §8's hump-at-the-mid-board versus the monotone procession - it separates 08:11 (peak ws5, falls
  32-34 points to ws12) from 11:19 / 11:22 / 08:46 (climbing all the way), and §8's "at bumps >= 8
  the r ladder cascades while the Mage humps" holds on all three 08:11 bars and neither 11:x bar

See `docs/octo-freedom/1007_ws12_baton.md` §12 and §13.

## The original 0918 park, kept verbatim

Joe 0918, verbatim: *"I'm reviewing the charts and I see there is a lot more to unravel before we
can turn mage-cascade into a reliable mech. I called on mage-cascade to solve a single trade, the
09-01 17:26:20 signal in the 122 report. the amount of effort needed to build cascade-mage properly
is not worth 1 trade - so let's bank what we have learnt about mage-cascade and we'll come back to
refine it later."*

BANKED IN FULL: `docs/mage_cascade_findings.md`. Scripts preserved in `docs/mage_cascade/`.

THE BLOCKER, and the first thing to do on return — Joe 0918: *"this work is not calculated on dr -
dr is only compared after the calculation has produced a decision based on the ladders direction
(r and Mage values increasing or decreasing from top to bottom of the TF list), and its source-based
trajectory direction. we compare dr at the end simply to decide if a main-trade signal is
masquarading as sneaky-1 (or vice versa)"*.

Every number in the findings doc was computed inside a dr frame — the event definition, the dwell,
the episode grouping, all eleven ladder columns, and the score sign. Requiring ws1Mage's oob side to
match dr discarded 2,818 of 14,682 entries (19%), and the dr-flip rule split single oob dwells into
extra events. `mbump` counts raw RISING steps at dr +1 and raw FALLING steps at dr -1, so the two dr
tables describe different raw geometries. The dr latch fires on ws1Mage >= 75 held 8 bars, so dr is
partly a lagged restatement of the line the event tests — it agrees with the source side 81% of the
time.

NOTHING IN THE FINDINGS DOC CARRIES OVER UNTIL THE dr-FREE REBUILD IS DONE. The OOS nulls on
ARRIVED and STARTED, the bumps >= 8 dr -1 result, and the Mage source-oob vote are all dr-framed.

STATE ON PARKING:
- the in-sample gate (`ws1 oob + mage falls > 0 + bumps <= 2`, 60m -0.853 on n=11) **reversed OOS**
  to +0.020 on 3,145 events over 83 days.
- OOS found the turn at 8 of 11 bumps, dr -1 only: 120m -0.478 on 127 clusters, 63% hit. A high bump
  count is a ladder that turns over at ws4, the mid-board, not a rough cascade.
- every r test is null: direction (+0.040 vs -0.008), ARRIVED (-0.011 vs -0.017), STARTED (+0.003 vs
  +0.009). STARTED is flatter than ARRIVED despite being the more faithful instrument.
- the only monotone found is the ws5..ws12 Mage source-oob vote: -0.013 -> -0.086 at 60m as the
  threshold goes 0 -> 8. `mat = 8 of 8` gives -0.128 at 60m on 296 clusters.
- **every figure is below the measured drag of 0.1975% per trade.** Nothing here clears costs.

OPEN, in order: (1) rebuild dr-free; (2) rule the oob-entry dwell, currently 3 bars borrowed from
`ws1mage_rev.dwell_ok`; (3) rule the source lookback, currently uncapped; (4) look at the 2,818
excluded entries — the masquerading-signal population; (5) test the ws4 turnover against the
blast-radius note in `wsf_setup_model.md` 3.21.2; (6) Joe has read one bar, 09-01 17:26:20.

## #69 refactor the lookahead out of sight — Joe 1001

Joe 1001: *"add a refactor job to remove `brk` and any other lookahead from the leash code so that
it's out of sight, out of mind"*. Raised after `brk` re-entered a live argument for the second time
in one session (`docs/octo-freedom/1001_rewalk_on_ruled_dr.md`).

- **#69** [pending] Put the ruled-out lookahead beyond reach of the leash code. **MEASURED FIRST, and
  the finding changes the job: there is no lookahead CODE in the leash module.** Every hit is a
  docstring saying so.

| file | hits | what they actually are |
|---|---|---|
| `leash_walk.py:34-36` | `release`, `moments`, `coil_exit.resolve`, `i1`, `brk`, `actionable_*` | the *"WHAT IS NOT HERE, AND WHY"* block — the record of Joe's ruling |
| `leash_walk.py:4` | `brk` | Joe quoted: *"because our verified strategy uses `WALK FIRES FROM` as our one and only signal"* |
| `leash_walk.py:28`, `:193` | `coil_exit` | **LOAD-BEARING.** `rev_lookback_mask` is held against `coil_exit._knowable` by `test_leash_walk.py` Q2 — 3,000 bars, 0 disagree |
| `arm_state.py:143` | `actionable` | why Joe 0930 split `coil_exit`'s single `actionable` key into four |
| `leash_walk.py:207, 208, 226` | `i1` | the walk's own bar-range parameter. Nothing to do with a moment's end |

**SO THE TENSION, AND IT IS JOE'S TO RESOLVE:** "out of sight, out of mind" applied literally would
delete (a) the written record of his own ruling and (b) a test's reference implementation. Neither is
lookahead; both are the proof that lookahead is absent.

**WHERE THE RESIDUE ACTUALLY IS** — files that still COMPUTE a `brk`-based emit bar:

| file | lines | note |
|---|---|---|
| `sweep_v3_signal.py` | `:16`, `:242-243` | `brk = m['brk'] if m['brk'] is not None else m['i1']` then `max(brk, rev, fired)`. **This module provides `Rig` to `report_leash_walk.py`** — not on the walk's path, which takes only `rig.DR`, `rig.CC`, `rig.lines`, `rig.gate_open` |
| `bank_emit_entry.py` | `:5`, `:86-87` | the banker. Also the only copy missing the same-dr-inert clause |
| `compare_rowfree.py` | `:91-92` | same formula |
| `measure_no_brk.py` | throughout | **LEAVE IT.** It is the script that measured the drop; removing `brk` destroys the evidence for dropping it |
| `tide_wireframe.py:155,163`, `lr_exit_test.py:32` | — | unrelated: an `anchor='brk'` string and a local variable |

**The job, as scoped by the above:** quarantine the emit-bar formula so the leash side cannot reach
it, rather than deleting text. The candidate is a single owner for `max(brk, rev, fired)` that the v7
chain imports and the leash code does not, which also fixes the three-way duplication of that formula.
Not started. Joe rules on the docstring question before any edit.

---

## 1005 — the lazy-g routing / scoring open list lives in its own register

Added 2026-10-05. The register's newest section before this was 0918, so the 1005 items would have
been invisible here. They are NOT duplicated into this file — the single durable list is
**`docs/octo-freedom/1005_knobs.md` section 5**, with an owner per row. Summary of what is open:

| item | state |
|---|---|
| `neither` = BLOCK · `no fire` = BLOCK · D empty-block = BLOCK | all three **invert between 09-25 and 09-26** (+3/-1, 0/0, +1/-5). None is a one-day call. Joe's to rule |
| the stall-contiguity gate | Joe's own 07:57 verdict mechanism. He has not been able to name the knob. UNBUILT |
| **the baton lineage rule — a defect in `baton.py:125`** | `rider = max(c)`, so there is no lineage at all. 41 of 139 passes on 09-25 had no legal successor within +-3 TF and the chain jumped anyway. Invalidates the `riding`/`traj` columns in both `transfer/*baton_stall_octosig*.txt` (both files now carry a CORRECTION header). Three values open: the hop window, the no-successor case, whether a downward pass counts |
| `LAZY_G_D_GAP_MAX` 4 | Joe's, explicitly arbitrary, flagged for sweeping. Not swept |
| the stop: 0.70 live vs 0.80 scored | **a deliberate divergence.** `wsf_trade_config` v3 runs `mae_cap` 0.70; 0.80 beat it by +9.186 pp over 9 days. Two points is not a sweep — the knee is unlocated. Do not reconcile without Joe |
| swing_detect 0.70 vs the banked 1 % | mine, named. `docs/linelab_spec.md` s0 records 1 % as locked by Joe |
| the 2.0 % risk budget | mine. Return AND drawdown are both near-linear in it — no knee, so it is a convention |
| mtd population B | the ws1mage-rev + ws1r oob events walked bar by bar. NEVER RUN |
| branch B and C agree/disagree direction | unruled |
| held-out days | **NONE.** All 9 days (09-25..10-03) are in-sample for every knob |
| pyramids (#7 above) | still open, and now measured: with the cap dropped, **max 4 concurrent legs**, both-legs-open 16.5-18.2 % of total open time |

Results: `docs/octo-freedom/1005_scored_outcomes.md`. Runnable chain + the 298 octo-sig inputs:
`docs/octo-freedom/1005_scoring/`. Per-trade P&L: MySQL `lazyg_compound`.

---

## #62 THE 1008 SWEEP — WHAT IS MEASURED AND WHAT IS NOT. ADDED 1008.

Nine hours of unattended sweeping over the full 95-day tape. Full detail in
`docs/octo-freedom/1007_ws12_baton.md` §25-§33 and the summary section at its end.

**THE THREE CHANGES I WOULD MAKE**, together -4.0151 over 95 days with fit -0.7897 / hold -3.2254,
MFE/MAE 1.06, and every component passing an out-of-sample test:

| the change | from | to |
|---|---|---|
| `mae_stop_pct` | 1.1 | **2.5** |
| the walk's x-cross exit | live | **OFF** (`W_NOX=1`, the switch already exists) |
| `reent_xwob` | 6 | **18** |

**THE CHAIN STILL DOES NOT PAY ITS FEES.** -0.0029 per leg against a 0.11 round trip, and slippage
is unset on top. No config measured clears it out of sample.

**WHAT IS SETTLED AND NEEDS NO FURTHER SWEEPING:** the `r`, `Mage` and `x` line specs (32 variants,
**0** beat the live spec on both halves), the baton pass `oob` (`stalled` is 34.19 worse, worst
MFE/MAE at 0.82), gate A over gate B (8.37), `oob_hi`/`oob_lo` 85/15, `dip_fence` 53,
`dip_dwell_bars` 6.

**WHAT HAS NO MEASURED VALUE, ONLY A MEASURED UNCERTAINTY** - each picks the opposite value on the
two halves of the tape: `ceil_trig_tf` (fit 8, hold 12 - Joe's), `stall_n` (fit 6, hold 4),
`rrev_wob` (fit 2, hold 1), `oob_gate_fence` (+34.21 in one context, -14.17 in another).

**STILL UNTOUCHED AND STILL HELD:** #60 (the stall sampling width, TFs 1-8) and #61 (the x-cross
TARGET - x X r vs x X m vs x X Mage/b/boundary). The 1008 sweep moved the x LINE's own spec, never
the target.

**THE HARNESS IS BUILT AND VERIFIED** for tomorrow's sweep, in `docs/octo-freedom/1005_scoring/`:
`_cfgworker.py` (one knob config -> per-day realised, so any block scores from one run),
`_lineworker.py` (one line variant, r / Mage / x), `_buildlines.py` and `_buildlinesx.py` (line
variants, with an **assert** that the cache window matches score39's), `_holdout.py`, `_sweep.py`,
`_sweep2.py`, `_overnight.py`, `_onedaydecisions.py`. Chain runs parallelise cleanly at `-P 6` on
the 16 cores; the line BUILDS must stay sequential.

**THE METHOD LESSON, measured three times:** one-at-a-time bests do not compose. The granular
centroid collapsed the chain to 441 legs at -29.30 where each of its five knobs improved alone.
Any future sweep needs its winner re-measured as a whole, and a hold-out block that chooses nothing.

---

## #61 CLOSED 1008 — THE x-CROSS TARGET IS SWEPT, AND ARM B IS BANKED

25 arms over 95 days: target role (`r` / `m` / `Mage` / `b` / the ex-fence LEVEL) x target TFs
(h+1 AND h+2 / h+1 only / h itself) x the in-fence test on the target (on / off). `mae_stop_pct`
2.5, `reent_xwob` 18, everything else banked. Output `xt.jsonl`, driver
`docs/octo-freedom/1005_scoring/_xtarget.py`.

**BANKED, on Joe 1008 "go for B":**

| knob | from | to | what it means |
|---|---|---|---|
| `x_tgt_role` | `r` | **`b`** | the line the rider's x must cross. `b` is bb 49/0.95, the slowest of the five wsf roles; `r` is k 5/8/7 |
| `x_tgt_tfs` | `both` | **`next`** | h+1 only, not h+1 AND h+2 |
| `x_tgt_fence` | 1 | **0** | the target no longer has to be in-fence |
| `mae_stop_pct` | 1.1 | **2.5** | B's measured context; Joe 1008's goal is to bring it back down by relocating the opens that need it |
| `reent_xwob` | 6 | **18** | B's measured context. 90 s of ws1x hold |

**VERIFIED**: the seeded build reproduces the arm exactly — fit **+0.7510**, hold **+4.0797**,
all-95 **+4.8307**, 1623 legs, 201 stops, MFE/MAE 0.9527.

| the choice | all-95 NET | MFE/MAE | legs | stops |
|---|---|---|---|---|
| A — the x-cross OFF (`W_NOX=1`) | -4.0149 | **1.0649** | 1404 | 166 |
| **B — the x-cross on ws{h+1}b, no in-fence** | **+4.8307** | 0.9527 | 1623 | 201 |
| as built — the x-cross on ws{h+1}r AND ws{h+2}r, in-fence | -25.6072 | 0.9346 | 1647 | 203 |

**WHAT GENERALISES AND WHAT DOES NOT, stated so the knobs are not over-read:**

| the claim | the evidence |
|---|---|
| B is the fit-half winner, chosen without the hold block | rank **1 of 25** on fit alone |
| the fit ranking itself transfers | **no** — Spearman fit vs hold across the 25 arms is **-0.137** |
| the in-fence test OFF is a pattern, not a pick | mean hold NET **-4.9272** across the 12 arms with it off vs **-20.3635** across the 12 with it on. It REVERSES on fit (-32.82 vs -22.18) |
| `b` is the right target line at role level | **no** — `b`'s mean hold NET is the worst of the four roles (-19.24); `r`'s is the best (-3.74). B's strength is arm-specific |

**B IS THE STRUCTURAL CHOICE, NOT A PROVEN SCORE.** +4.83 over 95 days is +0.003 per leg against a
0.11 drag. It is banked because it keeps 979 tunable exits that A deletes, and because it is the
only arm that is positive on both halves after being picked on one. Nothing here says it will hold.
