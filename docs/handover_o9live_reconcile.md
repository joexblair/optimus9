# Handover — o9-live ⇄ backtest reconciliation (0707)

*Written for a fresh session. Read this, then MEMORY.md loads the ledger. o9-live is HALTED and safe.*

## THE SINGULAR GOAL (Joe, 0707 — do not re-frame it)
**If the backtest shows profitable PnL, the o9-live problem is that o9-live does NOT match the backtest.**
Not "find a realizable one-way strategy", not "make o9-live hit X%". The **backtest is the spec**; every o9-live
mechanic reconciles *to* it. (I drifted into "realizable strategy" framing yesterday — Joe corrected it. Don't repeat.)

## CURRENT o9-live STATE
- **HALTED, flat, equity $364** (was $500; bled −27% on a 15× pyramid before I flatten+halted it). `o9_control.halted=1`.
- **DO NOT RESUME** until the exit + sizing reconcile to the backtest (below).
- Config live: **`lp_arm_mode=0` (s5m arm)**, **`lp_lr_sl=0.9`**, producer **`v2_walk_ad`** (arm-delay).
- Processes (relaunch commands — pids change): 
  - loop `O9_PRODUCER=ad setsid python3 ops/run_o9live.py >> o9live_run.log 2>&1 & disown`
  - UI `setsid python3 -m uvicorn optimus9.live.ui_server:app --host 0.0.0.0 --port 8099 >> ui_server.log 2>&1 & disown`
  - fakeAPI runs on :8098 (no restart needed).
  - **The loop reloads ALL lp_config at startup** — audit `lp_arm_mode`/`lp_lr_sl` before any restart (I once restarted onto the stale s5Mage arm by accident).
- Resume path when ready: `curl -XPOST :8099/api/resume`. Clean reset: `curl -XPOST :8099/api/reset` (now also wipes the event stream).

## THE PLAN (next steps, in order, with reasons)
0. **FIRST JOB (Joe's ask): an alert that fires whenever o9-live ARMS.** Poll `o9_live.o9_state_log` for new
   `state='arm'` rows (dedup by kline_ms — see the double-logging bug below); emit a notification with es/price/kline_ms.
   Model it on `ops/monitor_closed_trades.py` / `ops/o9_healthcheck.py`. **Why:** lets us test the event-mismatch
   theories in near-realtime instead of post-hoc — watch a live arm, diff it against the backtest at that bar.
1. **Build a clean Source-of-Truth backtest.** `build_v2_walk.py` uses **`v2_walk`**, but o9-live runs **`v2_walk_ad`**
   — the "SoT" table is BOTH stale ($177, 06-25→07-05) AND the wrong producer. **There is no clean SoT right now.**
   Decide the producer (almost certainly **`v2_walk_ad`, to match o9-live**), rebuild the table with `arm_mode=s5m` +
   current window. Everything downstream reconciles to this.
2. **Review Bybit hedge mode (Joe's ask) + does it match the backtest's conditions?** The backtest books overlapping
   **opposite-side** trades (long+short at once) a one-way account can't. Hedge mode (#55, independent long+short
   books) is how o9-live could hold them. Research the real Bybit hedge-mode mechanics (margin, position modes) and
   list the gaps that remain even with it: sizing/margin under simultaneous positions, MAX_LOT binding, fills/slippage,
   exit ordering.
3. **Diff o9-live vs the SoT, mechanic by mechanic.** Same-side pyramid should MATCH (Bybit auto-pyramids). The
   **exit is the known break** (flip closing at −1.37% past the 0.9% SL). Opposite-side overlap needs hedge (#55).

## CONCEPTS RUN & DISCARDED YESTERDAY (don't redo — held lightly, tested, dropped)
- **s5Mage / st5Mage@10min / s3Mage as the ARM** (replacing s5m breach): all **breakeven** through the v2 walk;
  s5m breach wins because it fires ~10× more and compounds. Arm placement was never the bottleneck.
- **s1a-gate / s3s4-integration** for the arm: engineered but redundant / didn't reach the target.
- **KER (Kaufman efficiency) entry-router**: validated on `v2_walk` (55%→68%) BUT **redundant with `v2_walk_ad`**
  (the arm-delay already filters to 71%). Useless on the SL too. Shelved. It was diagnostic, not a lever.
- **Waypoint funnel (r-OOB confluence) + confluenced r/m-divergence as EXITS**: dead — `lr_exit_v2`'s curl beats them.
- **KER-adaptive stop-loss**: dead (SL inert in backtest; tightening weak trades hurts −8×).
- **"Widen the SL fixes #54"** (I shipped `lp_lr_sl`→0.9): necessary but **INCOMPLETE** — the real gap is execution.
- **"Cap the pyramid"** — WRONG. **Bybit auto-pyramids** (a same-side add = merged into one position). The pyramid
  is *correct* Bybit behaviour and matches the backtest's overlapping same-side trades. The blowup was the EXIT, not the pyramid.

## WHAT STANDS (validated findings)
- **#54 root:** o9-live 33% vs backtest 67% is **execution, not signals.** Matched trades had identical entries
  (px diff +0.004%); live loses because the exit stops/flips winners the backtest's `strand_rescue` banks.
- **Signals reconcile:** on the clean-base window, **bt-only=0** (o9-live fires every backtest arm, in-sync ~5s).
  ~9% real over-fire + a **state-log double-logging bug** (same arm kline_ms written 2–10×; dedup by kline_ms).
- **The backtest's 45.6× is ~80% overlap-dependent** (single-position = 9.5×). Those overlaps = Bybit pyramids/hedges.
- Scripts (in repo root, uncommitted): `live_vs_backtest_events.py`, `live_vs_backtest_trades.py`, `ker_*.py`,
  `divergence_v2.py`, `waypoint_*.py`. Engine: `strategy.py:65-101` (exit/pyramid), `sizing.py`, `build_v2_walk.py`.

## HOW WE WORK (read these — the flow is load-bearing, not preference)
- `docs/korero_working_relationship.md` — the working register (bullets, brevity is CARE, lead with the answer).
- `docs/staying_light.md` — self-support; "self-judgement is not a tool; build the tool." Ego-drop on catches.
- `docs/ci_initiatives.md` — CI disciplines; read at init.
- `MEMORY.md` — the ledger (auto-loads). Key: `project_o9live_exit_lever` has the full #54 chain + this reset.
- **The non-negotiables:** causal/emerging only (never closed). Surface forks, don't infer load-bearing choices —
  Joe's read is ground truth, the data is the arbiter. Never hardcode (DB). Autonomous commit when right (granular,
  green, to main). When the data contradicts what I built, welcome the catch — no ego ledger.

## LOOSE ENDS / HOUSEKEEPING
- Orphaned DB seeds (Joe's call to sunset): `s1m`/`s1r` (dropped s1a test), `st` series + `st5m/st5M/st5r` + itf_pk 27.
- Stale s5Mage knobs: `lp_arm_wob=7`, `arm_line` (commits 4533bfb/7adf5e8) — harmless (arm_mode=0 → unused).
- `~15 scratch analysis scripts` in the repo root — candidates for a `scratch/` dir or the sunset register.
- Bugs found, not yet fixed: the arm double-logging (2–10× per bar), the ~9% arm over-fire.
