# Task register — carried forward (0707)

*The harness TaskList is session-scoped and won't auto-carry. This is the durable copy. New session: read this;
re-seed into the harness via TaskCreate if you want live tracking. Statuses as of 0707. IDs match the old session.*

**Active / near-term (the o9-live reconcile thread — see `handover_o9live_reconcile.md`):**
- **#54** [ACTIVE] o9-live under-fires vs backtest — look-ahead + realtime-fidelity gap. *Now = the reconcile: root is the EXIT (flip past SL), signals reconcile. Halted, $364.*
- **#55** [pending] Hedge mode — make o9-live match the backtest (independent long+short books). *Next in plan; review Bybit hedge-mode mechanics.*
- **#44** [pending] Wick-ignore for exit/SL price — live via Bybit index_price. *0707: reclassified — o9-live SL uses the bar CLOSE not a wick, so this doesn't apply to the −0.7 knife-edge; kept for a true index-price exit later.*
- **#9** [pending] Exit rule: take-the-money-and-run (>1% in 15s) — grind params. *Related to the exit work.*
- **#48** [pending] Daily o9↔Bybit reconciliation (o9_account tally vs exchange balance).

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
