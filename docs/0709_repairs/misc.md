# 0709 repairs — MISC (tape · schema · tooling · my instruments)

Milestones the bot must pass to be profitable. Source: the 0709 live arm probe (`O9_PRODUCER=arm`, 10:19→17:59)
plus the causal audit. Parent: `docs/arm_delay_research.md` (CLOSED) · `docs/causal_lookahead_register.md`.

| mechanic | learnt | needs attention |
|---|---|---|
| **tape** | 37 of 38 arm bars re-derive bit-exact. `DRIFT=0`, `DISCREPANCY=0`. | Nothing. Klines are stable. |
| **arm→trade audit** | 38 arms → 38 trades. But **20** `close_leg` errors. | `o9_decision.action` enum. Migration staged, NOT run. |
| **detector (mine)** | 1 `ARM-DRIFT` — my own warmup-edge artifact. 0 since. | Nothing. |
| **tooling** | `replay.py` replayed the wrong producer, truncated live tables by default, and is one-way. | Fixed (E2, E3). E6 (one-way vs hedge) open. |

---

## 1. The tape is stable — the question that most needed answering

**[measured]** `recon_arm_daemon.py` recorded, per arm event, all 21 lines at the bar's **open** (bar−1 close)
and **close** — 42 columns — then re-derived that bar from the klines *as they are now*, window pinned to the
same bar so window growth cannot confound it.

```
o9_recon   38 rows   10:19:00 -> 17:59:40   CLEAN=37   DRIFT=0   DISCREPANCY=0
```

**No late tick, no backfill, no sanitiser write moved a closed bar during 7h40m.** Given
`project_synthetic_tape_patches` and `project_frozen_tape_failure`, this was not assumed. It is now measured.

**Needs attention:** none. Keep the daemon as the standing tape guard for future probes.

---

## 2. `o9_decision.action` — a live bug the rig found in 20 minutes

**[read]** `app.py:76` writes `act = "close_leg"` on every option-B per-leg SL close. `app.py:67` branches on
`"reduce"`. The enum held neither:
```sql
action ENUM('open_long','open_short','add','close','hold')      -- before
```
**[measured]** 20 occurrences of `1265 Data truncated for column 'action'` over 4,903 bars.

**What it cost.** The exception propagates out of `_execute`, so any **remaining intents on that bar are
skipped** — with hedge legs, a stop on one side can silently drop an open on the other. The position itself
closes (`record_close_leg` runs *before* `log_decision`), so **no trade was lost**: 38 arms → 38 trades.

**What it did cost: nothing recoverable.** `[measured]` The exit mechanism is encoded in `exit_order_id`
cardinality — a stack close places ONE order for the whole side, a per-leg stop places its own. 24 exit orders
closed 28 legs: **3 orders closed >1 leg (the stack closes, all 3 winners), 21 closed a single leg (20 stops +
1 near-flat win)**. All 8 winners attributed without the audit table.

`20 per-leg SL closes = 20 errors.` Exact match, no residue. `3 multi-leg + 1 single-leg = the 4 recorded
'close' rows.` The audit row is a convenience; **the order cardinality is the record.**

**FIXED 2026-07-09 19:14 UTC** (`migrate_decision_action.py`, Joe authorised):
```
before: enum('open_long','open_short','add','close','hold')
after : enum('open_long','open_short','add','close','close_leg','reduce','hold')
```
Additive, idempotent, run with the loop live. `docs/o9_live_schema.sql` matches. Errors since the 19:10:43
seam: **0**.

---

## 3. My own instruments produced two false alarms

Both fired in the first minute of the rig, and **both would have read as the signal we were hunting.**

- **`SKIP` on every arm.** `BiasWindow` admits a bar whose *open* is ≤ `now`, so the window edge sat one bar
  past the arm. Fixed by indexing the bar directly — legal because every line is emerging/causal, so a value at
  bar `j` cannot depend on bars after `j`.
- **`ARM-DRIFT` at `07-08 14:51`.** The window **slides**; that arm sat in the warmup zone where EMA/RMA seeds
  shift as the left edge moves. Fixed with a 2h stability floor (`STABLE_MS`).

**[measured]** After the fixes: `ARM-DRIFT = 0` across the whole run.

**Needs attention:** none, but the lesson is durable — **a detector must be measured against a known-good run
before its output is treated as evidence.**

---

## 3b. `find_pivots` returned `[]` on any series with a leading NaN — FIXED 2026-07-09

**[read]** `swing_detect.find_pivots` seeded its running extremes at index 0. `BiasWindow.px` carries **2 NaN
warmup bars**, so every comparison against the running extreme was `False`, `trend` never left 0, and the
function returned an **empty list with no error**. Two bars were enough.

`[measured]` On the cleaned 42d array: **2,065 pivots** at the 0.9% threshold. Before the fix: **0**.

Fixed by seeding at the first finite bar, skipping non-finite bars in the walk, and anchoring the prepended
pivot at that bar rather than index 0. Verified: identical pivots with and without a leading NaN, offset by the
skipped bars. Suite 205 pass.

**Consumers to re-check:** `lr_walk` (MFE/MAE entry-quality scoring), `bl_grind`'s swing scoring,
`swing_mask`, `compare_pivots`, the gate-sweep Stage-0 labels. Any of them that passed a raw window read an
empty pivot list. **Whether any live number was affected is unmeasured.**

---

## 4. Tooling defects found while auditing

| id | site | state |
|---|---|---|
| **E2** | `replay.py:35` replayed `v2_walk`, not `v2_walk_ad`. Every conclusion ever drawn from it described a machine we do not run. | **FIXED** (`e50812d`) |
| **E3** | `replay.py` `truncate=True` by default, and its own `__main__` sets `database="o9_live"` — running the module wiped the live paper account's exchange books while `o9_ledger` survived. | **FIXED** (`db5280f` era; default now `False`) |
| **E6** | `replay.py` is a **one-way** harness (`open_leg(idx=None)`, *"opposite side while holding — skip"*). Live is hedge mode. **The tool cannot represent the machine it validates.** | **OPEN** |
| **E5** | Stack arithmetic existed twice. `stack_model.PositionStack` extracted (`3004d33`), mirrors `MatchingEngine` exactly, 14 tests. | Repoint `risk_stack_dist.py` at it. **Deeper, open:** should `MatchingEngine` itself call `stack_model`? |
| **B1** | `value_mode` default disagrees with itself: `closed` in `bias_machine.py:78`, `emerging` in `bl_detect.py:237`. A new line inherits look-ahead depending on which reads it. | **OPEN.** All 21 cascade lines are currently `emerging` (DB-verified). |
| **B2** | `lr_v2.py:226` `s30M_wob` reads a closed `_line`. Zero callers. | Dead. A trap for whoever rewires it. |

---

## 5. Settled — do not re-litigate

- **[measured]** All 21 cascade lines are `value_mode='emerging'`.
- **[measured]** The RSI 70/30 rescale is **per-bar with fixed constant endpoints** — not a full-series
  normalisation. Long-standing suspect, cleared.
- **[read]** `f_bb_lookahead` / `lookahead_resample` are **causal** despite the names (`cummax`/`cummin` *within*
  the window). The name is a lie in the safe direction.
- **[measured]** No `.shift(-n)`, `[::-1]`, `center=True`, `bfill`, or `interpolate` anywhere in `compute/`.
- **[measured]** `closed` mode is **stale** at the live edge, not future. It leaks only in the vectorized
  backtest (via `resample`'s window-open stamp). The `emerging` mandate buys **backtest honesty**, not live
  safety.
- **[measured]** The align-stamp fix (`ALIGN_CLOSE_STAMP`) is **gate-mask-only**: 42d A/B, all 21 cascade lines
  bit-identical, 2632 entries unchanged. The `bny30M`/`bny30p` gate-sweep numbers still owe an A/B.
