# 1001 — what is open, read from the strategy-side handover

Written 2026-10-01 by the session that ran the o9-live recon validation (`1001_recon_validation.md`),
after Joe handed it the strategy-side prompt in `1001_handover_to_next_session.md`. Read: that
handover, `.claude/joes-convo-style.md`, `docs/staying_light.md`, `docs/octo-freedom/README.md`,
`NOTES_momtf_mechdev.md`, `docs/task_register.md`, and the memory notes the handover names
(`mae-mfe-only`, `strictest-standard-bias`, `announcing-is-not-asking`). Repo at `4c162a9`.

**STATUS 1002:** a dated snapshot. Every item below is now ruled, built or parked, and the record of
which is `docs/o9-live-recon/OPEN.md`'s Ruled table and `1002_live_producer.md`; this file is not
updated further.

**Nothing below has been started.** Joe chooses. The workmate session responds — append under
`## Replies` at the end, or post in `docs/octo-freedom/chat/` (see its `README.md`).

## The handover's open list — none of it applied yet

| # | item | state in the repo at `4c162a9` |
|---|---|---|
| 1 | 11 doc statements that contradict the code | all 11 unchanged. `OPEN.md:16`, `:24` and `:27` are still not struck through; `CODE_MAP.md:97`, `trade_walk.py:5` and `:119` unchanged. One more of the same kind, added 1001: `walk_mom_models.py:176` names `optimus9/compute/dl_latch.py`, which does not exist (the module is `dr_latch.py`) |
| 2 | the two doc-vs-doc conflicts Joe said to fix | unchanged, at new line numbers. The dump's fields are "not ruled" at `OPEN.md:79` and `:261` but "RULED" at `RECON.md:21`. "Three closers" is at `OPEN.md:447` |
| 3 | 14 of 37 single-rule mutations pass every check; 5 more are caught only by the one-day acceptance test | Joe's gate: more validated days first |
| 4 | `rig.DRW` (rule#1's dr: 75/25, wob 8) stretch distribution | not measured. `rig.DR`'s figures for comparison: longest unbroken stretch 7.2 h, 2,487 changes |
| 5 | lazy-g | not built. Joe's gate: more days first |
| 6 | MVP2 item 5, the dr fence + wob sweep | not run. The 0926 wob-8 ruling was measured on the 75/25 series, not the oob 15/85 one |
| 7 | the `sig_conf` re-bank of the 121 `wsf_leash` rows | ruled 0929 ("rebank in place"), not applied. `arm_state.py`, `leash_walk.py` and `report_leash_walk.py` have 0 references to `wsf_leash` |
| 8 | `walk_rule1_back_min` 5.0 min | never tested on held-out days |
| 9 | `fastverdict.py` has no `verify()` | the gap is stated, as Joe ruled. Its `sideways_mask` is never called on octo-freedom's path; its only caller is `Rig.sideways`, which only the v7 chain's `sweep_v3_signal.run` uses |

## From the recon validation — not on the handover's list

| item | state |
|---|---|
| the Phase 3 report | was in chat and a Claude Docs page only. **Filed 1001** as `docs/octo-freedom/1001_recon_validation.md` |
| the mutation harness and its results | was in the job's scratch dir only. **Filed 1001** as `docs/octo-freedom/1001_recon_validation/` — byte-identical (sha256 checked), `unit.py BASE` and `unit.py L17` re-run from the new location and match the stored rows |

- Neither is committed.

## What `OPEN.md` now says about the three Phase 3 decisions

| decision | what `OPEN.md` now says |
|---|---|
| 1 — re-walk a window each bar, or carry the state | Joe ruled: re-walk a bounded window every bar |
| 2 — window length | no ruling from Joe. The previous session measured `rig.DR` against StrategyLoop's 104 h window: longest stretch 7.2 h, 0 of 2,487 stretches reach 24 h. `rig.DRW` was not measured (item 4) |
| 3 — signals only, or run the exits too | Joe ruled: signals become trade actions. P&L is reported as a percentage only, because no position size is set |

- Per the handover, building the WALK FIRES FROM producer is the o9-live session's work and not on this list.
- ADDED 1001: the 104 h is StrategyLoop's default. `ops/run_o9live.py:37` runs 8 h lookback + 6 h
  warmup = 14 h. The workmate's `1001_dr_convergence.md` puts the longest interval between ws5Mage
  50-crosses (what resets the arm) at 9.43 h, which is longer than the 8 h lookback.

## Task-register numbers that don't line up

| number | the conflict |
|---|---|
| #24 | the handover says "in_progress, and it is this work". In `docs/task_register.md`, #24 is "BL re-engage revive BB-twitch-faked exit", marked completed 0706 |
| #7 | used twice: "bl_review combo selection" (BL list) and "review pyramids — two trades firing together" (0828) |
| #22 | used twice: "Check kline + kline_audit services" (infra list) and "mage-cascade, PARKED 0918" |

- The register has no entry for any of the 9 handover items. Its newest section is dated 0918.
- Open question: is the handover's #24 a number from that session's own task list?

## Still open in the register (the top half's statuses are as of 0707)

| register section | numbers still open |
|---|---|
| o9-live reconcile, 0707 | #54 (active), #55, #44, #9, #48 |
| ws-finisher / domTF | #60 (Joe holds the start), #61 |
| BL / bias / lines | #7, #10, #11, #13, #14, #15, #16, #17, #18, #21, #26, #36, #37 (in progress), #40, #42, #43 |
| arm / cascade | #50, #51, #52, #53, #56, #57, #58 (largely done), #59 |
| infra / tape / services | #19, #20, #22, #23, #27, #28, #30, #31, #34, #35, #38, #39, #41, #46, #47 |
| domTF setup model, 0824 (Joe's) | #62 to #68 |
| #7 pyramids, 0828 | no sizing model exists |
| #22 mage-cascade | parked 0918; it has to be rebuilt without dr before anything else |

TL;DR: none of the 9 handover items has been applied; the recon report and its harness are now filed
here, uncommitted; #24, #7 and #22 each point at more than one task.

## Replies
