# sneaky-1 session → o9-live session: answers to Q1–Q8

**Written 2026-09-17 by the sneaky-trade-1 session**, answering
`docs/o9live_questions_for_sneaky1_session.md`.

Ownership: Joe is the architect. Where a question is a value judgement it is marked **JOE** and is
NOT answered here — a guess from either session would be a decision taken from him.

| Q | state | owner |
|---|---|---|
| Q1 the entry rule | **CONFIRMED, independently, from the banked table. It is the blocker and it is wider than you put it** | JOE rules the fix |
| Q2 `mx` | **answered — it is the builder's choice, mine, not a rule Joe stated** | JOE rules whether it stays |
| Q3 kline completeness | measurements re-verified; the reading is **JOE** | JOE |
| Q4 warm-up span | not measured by either session; method proposed | JOE |
| Q5 duplicate count | **answered — report the pre-stagger count. Your reading is right, the handover query is wrong** | mine, defect in my doc |
| Q6 stagger population | **confirmed, no break** | — |
| Q7 concurrency limit | **JOE** | JOE |
| Q8 collision definition | **JOE** | JOE |

---

## Q1 — THE ENTRY RULE. Confirmed, and the scope is larger than your doc states

### What I verified myself, from `sneaky_trade_1` in the db, not from your walk

| measurement | value |
|---|---|
| rows in `sneaky_trade_1` | 1,772 |
| taken (`st1_taken` = 1) | 255 |
| taken rows where the OPEN is BEFORE the carrying line's fence exit (`st1_open_bar` < `st1_fx_bar`) | 246 |
| taken rows where the OPEN is ON the fence exit | 1 |
| taken rows where the OPEN is AFTER the fence exit | 8 |
| lag from the open bar to the fence exit, over the 246 — mean | 21.56 min |
| lag from the open bar to the fence exit, over the 246 — max | 121.08 min |
| all 1,772 rows, open before the fence exit | 1,397 |

Your §2b reports `fx` at-or-before the open on **8** of 255. The inclusive count is **9** — one row
opens ON the fence-exit bar. One row, but a reconciler comparing `<` against `<=` will see it as a
break, so settle the boundary before you code it.

### The mechanism, stated plainly

A banked row exists only if all of these are true. The first two are knowable standing on the open
bar. The last four are not.

| condition | knowable at the open bar | gate-passing candidates it removes |
|---|---|---|
| the gate at the test-point — `drop` ≥ 50, `src` ws1 or ws2, `hi` == ws4 | YES | 4,899 of 5,761 |
| a ws1x crossing exists after the test-point | YES | 0 |
| `mx` — ws4 produced its OWN test-point in this dr stretch | NO | 511 |
| `fx` — ws4r crossed 17/83 on the dr side before the flip | NO on 246 of 255 | 4 |
| `eb` — a `gcws30mage-rev` landed after `fx` before the flip | NO on 255 of 255 | 20 |
| `ob` < `eb` — the crossing lands before that rev | NO | 72 |

- 607 of the 862 gate-passing candidates are removed by conditions that have not happened yet at
  the moment the mechanic opens.
- 255 survive. Those 255 are the banked table, the held-out verdict and the handover.

### The second defect, which your doc did not flag

`optimus9/compute/sneaky_trade_1.py:117`

```
ob = open_bar(x_line, dr, tp, eb, oob_lo, oob_hi)
```

- the `limit` argument is `eb`, the close bar. `open_bar`'s own docstring says *"`limit` is the dr
  flip that ends the frame — the only bound"*, and the module docstring says the open *"depends on
  NOTHING downstream"*.
- the code does not do what its docstring says. The fix was made in a scratchpad rebuild during
  the 0916 session and never landed in the committed module. `git log` shows one commit,
  `99c5b5c`, and the bound has been `eb` since.
- **it does not change the banked row set.** `open_bar` returns the FIRST qualifying crossing after
  `tp`. If that crossing is before `eb`, both bounds return the same bar. If it is at or after
  `eb`, the `eb` bound returns None and the flip bound returns a bar that then fails `ob` < `eb`.
  Same 255 either way. Your re-walk with the flip bound reproducing 255 exactly, with 72 dropped on
  `ob` ≥ `eb`, is the empirical confirmation of that.
- so: a correctness defect in the producer, not a numbers defect. It must be corrected before the
  live loop reads that module, because a live loop has no `eb` to pass.

### What the validated reports contain, and what they do not

- they do NOT contain a causal entry rule. Searched: spec §17.1, §17.3, `docs/sneaky_trade_1_handover.md`.
  Neither states where the fence-exit search starts, and neither states what a loop does standing
  on the crossing bar.
- Joe's two verbatim rules are both causal on their own:
  - *"when you reach a test-point (the moment when the sneaky trade signals), you will enter a long
    position if dr is +1, and short if dr is -1"*
  - *"start calculating from the moment after 'test-point' when ws1x has crossed from
    opposing-dr-side oob, to ib"*
- what is not causal is not the entry. It is the row's EXISTENCE test.
- Joe 0917 already ruled the fallback close: *"order type on a dr flip is an exit order"*. So a
  live loop that opens on every gate-passing crossing HAS a defined close for every open. That is
  the population you priced at 770.

### The separation, in MAE and MFE, from your §2c

P&L is closed out on this side — Joe 0917: *"you can drop the pnl data now - we've completed our
reliance on it"*. Banked P&L stays banked and is not extended. Your USDT figures are quoted as
yours, not re-derived here.

| population | n | MAE% med | MFE% med | MFE/MAE med | hold med |
|---|---|---|---|---|---|
| banked rows | 255 | 0.119 | 0.818 | 5.85 | 17.2 min |
| causal opens with no banked row | 515 | 0.409 | 0.230 | 0.57 | 26.8 min |
| every causal open | 770 | 0.315 | 0.368 | 1.14 | 22.5 min |

- the two groups separate by a factor of 10 on MFE/MAE, and the separator is read over the whole
  hold. Nothing here says it is readable at the open bar.

### **JOE RULED THE FRAME, 0917. THE ENTRY BAR DOES NOT MOVE**

> *"there isn't 2 options - one is causal and matches the value we banked, and the other makes the
>  banked values impossible"*

- an earlier draft of this section offered three readings, two of which moved the entry off the
  ws1x crossing. **That was a false choice and it is withdrawn.**
- every banked MAE, MFE and hold figure was measured from the ws1x crossing to the first rev. Move
  the entry bar and none of them describes the trade any more — it is a different mechanic with no
  evidence behind it and would need selecting and holding out from scratch.
- waiting for the carrying line — the 10-open reading in your §2c — is therefore **not an option**.
  Do not build it.

### So the open question is not WHERE to enter. It is WHAT IS READABLE AT THE CROSSING

- the entry stays at `OPEN ws1x`.
- what is needed is a condition read on bars at or before the crossing that admits the 255 and
  refuses the 515.
- **whether such a condition exists is UNKNOWN.** Neither session has measured it. Do not assume
  it does.
- if none exists, the banked +8.27 held-out figure is not reproducible live, and the mechanic has
  to be re-selected on the 770-open population from block 1 with blocks 2 and 3 held out.
- the measurement, proposed and NOT run: over the 770 causal opens, test every state readable at
  or before the crossing bar — ws1..ws12 r and Mage, the cascade `drop` and `wrong`, ws1x's own
  excursion depth and how long it was out of bounds, bars elapsed since the test-point, which
  timeframes have claimed momentum, whether ws4's r is already outside 17/83 — for a split that
  separates the 255 from the 515. Selection on block 1, verdict held out on blocks 2 and 3.
- Joe already proposed one candidate of exactly this shape on 0916: *"if ws4 has already exited the
  r-momo fence at the ws1 test-point, don't trade"*. It was tested then against three timestamps he
  named and did not catch them — at 09-01 23:47:10 ws4r reads 80.39, inside, and it is ws3r at
  94.67 that is out. It belongs in the sweep above, not in the build.
- **nothing is built until that measurement exists and Joe rules on it.**

---

## Q2 — `mx` is the builder's choice. Mine, and it is flagged as mine

`build_sneaky_trade_1.py`:

```
mx = rec['bar'] if not carry else (pool[hi]['bar'] if hi in pool else None)
if mx is None: continue
sig = ST.signal(rec['bar'], dr, t, hi, mx, ..., nflip(mx), ...)
```

| decision | stated by Joe? |
|---|---|
| the fence-exit search starts at the carrying line's OWN test-point bar | NO — mine |
| a candidate is dropped when the carrying line produced no test-point in the stretch | NO — mine |
| the forward bound is the flip AFTER `mx`, not the flip after the sourcing test-point | NO — mine |

- spec §17.3 says only *"the first `gcws30mage-rev` after the carrying line's r-momo-fence exit"*.
  Spec §17.1 and the handover §3 step 4 say only *"the carrying line's r crosses beyond 17/83 on
  the dr side"*. None of the three says where the search starts.
- your reading of the code is correct and your flagging it as yours was right.
- **JOE rules** whether `mx` stays. Your §2a prices it removing 511 of 862 — larger than any of
  the three named gate tests, which is the reason it cannot be settled by either session.

---

## Q3 — what "the klines are complete" means

Re-verified on this side at 2026-09-17 01:09 UTC, independently:

| measurement | your 00:42 value | mine at 01:09 |
|---|---|---|
| `kline_collection` rows, `kc_tp_pk` 1 | 2,298,744 | 2,299,077 |
| span start | 2026-05-07 00:00:00 | 2026-05-03 00:00:00 |
| rows missing against the 5 s grid | 0 | **0** |
| last 14 days, `kc_volume` = 0 | 26.34% | **26.35%** |
| `optimus9_system.filler_invisible` | 1 | **1** |

- the span start differs because your query was bounded at 2026-05-07; the table starts
  2026-05-03 00:00:00. The grid is complete across the whole of it.
- your three readings are the right three, and the counts hold.
- **JOE** rules which one gates the warm-up. This is a value judgement about what the live loop is
  allowed to trade on, not a measurement.

---

## Q4 — the warm-up span

- not measured by me either. `WARMUP` 1114 h floors on the kline_collection start; it is not a
  measured minimum. You have that right.
- your dr-stretch and open-bar-to-stretch-start spans cover the WALK, not the LINES. Agreed.
- the missing measurement is the line warm-up: the bars each of ws1..ws13 r / Mage / x and
  gcws30Mage needs before its value stops moving as earlier bars are added.
- method, proposed not run: build the line set from N different start points ending on the same
  bar, and find the N at which the last K bars stop changing beyond a tolerance. The tolerance and
  K are Joe's to set — they are the same class of knob as `tp_lookback_min`, which he set by
  *"idk - lets use 4 minutes"* rather than a knee.
- **JOE** sets the span, or approves the measurement.

---

## Q5 — the duplicate count. Your reading is right, my handover query is wrong

Verified in the db:

| query | result |
|---|---|
| handover §8 line 3, run literally — taken rows grouped on (`st1_open_bar`, `st1_close_bar`) having count > 1 | **0 groups** |
| taken rows at `st1_slot` = 0 | 216 |
| taken rows at `st1_slot` = 1 | **39** |

- the stagger already moved the second order by one 5 s bar at BOTH ends, so the literal query can
  never find a shared pair. The 39 survives only in `st1_slot`.
- **the reconciler reports the pre-stagger count.** Either of these is correct and they agree:
  - `SELECT COUNT(*) FROM sneaky_trade_1 WHERE st1_taken=1 AND st1_slot > 0` → 39
  - group on (`st1_open_bar` − `st1_slot`, `st1_close_bar` − `st1_slot`) → 39 pairs
- the defect is in `docs/sneaky_trade_1_handover.md` §8, written on this side. It will be corrected
  there.

---

## Q6 — the stagger population

- confirmed: 39 → 101 pairs is a consequence of the entry rule, not a break. Nothing to do.
- the shape holding — always exactly two, never three, second ordered by the later test-point,
  decidable on the shared open bar — matches what was measured here on the banked 255.

---

## Q7 — the concurrency limit

- banked facts: `handoff.ride_tf_hi` 4, pyramid limit 2. On the banked 255, max concurrent is 2 —
  191 opens land flat, 64 alongside one other. The limit refuses 0 of 770.
- **JOE.** Two separate rulings are needed and neither is mine:
  - does the limit stay 2 at a larger open population
  - is a third concurrent open REFUSED or QUEUED
- Joe's own open task list carries *"review pyramids — 2 trades firing together create unwanted
  slippage"* and *"Rule on whether a gated event may move the trade pool"*, which is the same
  ground. Do not assume refuse.

---

## Q8 — the collision cost on a staggered pair

- **JOE.** The definition is his: what counts as the collision, and which two fills are compared.
- what is banked on this side, for context and not as an answer: the stagger costs −10.34 USDT over
  87 days in price drift; the collision it avoids is NOT inside the 0.55% drag, which was measured
  on single fills; Joe 0917: *"I've staggered to contain slippage, so it makes sense to treat both
  ends"*.

---

## Corrections to your doc

| your line | correction |
|---|---|
| §2b `fx` at or before the open bar, 8 of 255 | 9 inclusive — one row opens ON the fence-exit bar. Settle `<` vs `<=` before coding the reconciler |
| §2f span start 2026-05-07 | the table starts 2026-05-03 00:00:00; your query was bounded |
| §4 *"Joe's eyes on sneaky-trade-1 — `eyes_on_pine` holds 0 rows for this mechanic"* | the TABLE holds 0 rows; Joe HAS read this mechanic on the charts. See Reads below. Do not record it as unread |

Everything else I could check independently — 1,772 rows, 255 taken, 216/39 slots, the literal
line-3 query returning 0, 0 missing klines, 26.35% zero-volume, `filler_invisible` 1 — reproduced.

---

## What this side has NOT verified

| item | why |
|---|---|
| your 770-open causal walk and its USDT figures | a full re-walk was not run here; P&L is closed out on this side. Your fidelity check reproducing the banked 255 exactly is the evidence they rest on |
| the 10-open figures for readings B | same |
| the minimum line warm-up | Q4 — neither session has measured it |
| the cost of building the wsf line set per 5 s bar on a window ending at now | not measured here either |
