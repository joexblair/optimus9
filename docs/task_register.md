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
  - at `MOMO_FIXED_SAMPLES` = 21 the floor is gone: gap 10 s at timeframe 1, 25 s at 2, 35 s at 3.
    `build_ws_fin.py` sets 21 at import; the module default in `momo_gated.py` stays 0, so any
    ws-finisher script that does not set it inherits the floored version.
  - the stall's lattice IS the momentum lattice — `build_ws_fin.py:345-349` reads `MOMO_STEP_BARS`
    and `MOMO_SAMPLES` out of `momo_window(K_WINDOW 4 x TF)` and hands them straight to
    `jig.stall_mask(y, dr, n, step, samples)`.
  - two ways it can go, both Joe's call: set `MOMO_FIXED_SAMPLES` to 21 everywhere so the floor
    never applies, or leave the default and accept that timeframes 1 to 3 share one lattice.

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
