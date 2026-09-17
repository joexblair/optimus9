# sneaky-trade-1 — handover to the o9-live session

**Written 2026-09-17.** Joe named the mechanic, set every threshold in it, and ruled on every fork.
This document is complete enough to work from with no prior context.

**The task for the receiving session, in Joe's words:**

> *"the new session will be tasked with replacing the existing o9-live loop with sneaky-1's mech,
>  and running backtest reconcilliation every hour"*

---

## 1. WHAT IT IS

One trade per test-point. It opens on a `ws1x` crossing, closes on a `gcws30mage-rev`, and runs
for a median 17 minutes. Every step is decidable at the bar it fires on — nothing reads forward.

**The entry and the exit ARE the measured bars.** Joe 0917: *"your MAE and MFE results are baked
on known-good causal events, so that becomes sneaky-1's entry and exit signals"*. The excursion
figures were always measured between the crossing and the rev; those two bars are the orders.

---

## 2. THE DIRECTION — read this before anything else

| dr | sneaky-trade-1 |
|---|---|
| **+1** | **LONG** |
| **-1** | **SHORT** |

Scored `* dr`: profit when price moves in the +dr direction.

**Spec 17.2's dr-bias rule says dr +1 = SHORT. IT DOES NOT APPLY HERE.** That rule governs other
mechanics that launch from the dr side. Joe ruled this explicitly, 0916:

> *"when you reach a test-point (the moment when the sneaky trade signals), you will enter a long
>  position if dr is +1, and short if dr is -1. this is all you need to consider - don't be swayed
>  by the other potential activities that might be reliant on dr"*

I inverted this twice by re-deriving it from the dr-bias rule. Joe caught it both times. **Do not
re-derive it. Read `st1_side` from the table.**

---

## 3. THE SIGNAL CHAIN

Producer: `optimus9/compute/sneaky_trade_1.py`. It owns no threshold; every gate arrives as an
argument.

| # | step | rule | knob |
|---|---|---|---|
| 1 | the dr stretch | latch change to latch change. The latch sets the dr, NOT the start bar | — |
| 2 | the test-point | `optimus9/compute/test_points.py` — established wsNMage oob anchor, 4-minute look-back, one per stretch per timeframe | `tp_lookback_min` 4 min |
| 3 | the ladder | the highest of ws2..ws4 carrying momentum at the test-point. `hi` | `handoff.ride_tf_hi` 4 |
| 4 | the fence exit | the carrying line's r crosses beyond 17/83 on the dr side | `momo_fence_r` 17 |
| 5 | **the CLOSE** | the FIRST `gcws30mage-rev` at or after the fence exit, before the dr flip | — |
| 6 | **the OPEN** | the first bar after the test-point where `ws1x`, having been oob on the OPPOSING dr side (15/85), returns IN BOUNDS. Must land BEFORE step 5, else no trade | — |

### The close is causal, and it did not used to be

It was the leash's **maximum coil** — `argmax` over every rev in the window. That is the global
maximum of an oscillating series (60.1% of windows carry 2+ local peaks, median 2, max 11), so it
is only knowable once the window has ended. A proper causal peak detector agrees with it on **0.7%
of rows**. Joe 0915 asked for three picks — *"test all 3: filter, time, size"* — and **size is the
one that cannot be built**. If the sandbox disagrees with the report on the exit bar, this is the
first thing to check.

### The open must not read the close

An earlier build searched the crossing up to the close bar, which let a later close admit opens
that should not exist. The open's only bound is the dr flip.

---

## 4. THE GATE — this is the entry condition, not a filter

All three read at the test-point, before anything opens.

| test | condition |
|---|---|
| `drop` >= 50 | the dr-signed Mage cascade drop, ws1Mage minus ws12Mage |
| `src` is ws1 or ws2 | the test-point came from the 1- or 2-minute line |
| `hi` == ws4 | the carrying line is the 4-minute line |

**Ungated the mechanic loses.** The drag is a flat 16.06 USDT per trade at 22,000 coins and the
median move across all rows is +0.288% against the 0.550% needed to clear it. 73% of rows never
clear the drag; the gate lifts that to 44.2%.

Chosen on block 1 of three time blocks, never reading blocks 2 and 3.

**Gates tested and REJECTED** — do not re-add without re-testing:

| gate | why not |
|---|---|
| `climb` (ladder climbed) | redundant — implied once `hi` is ws4 and `src` is ws1 or ws2 |
| `drop >= 39.1` (route 3's floor) | marginal sign flips: -0.08 / +3.39 / +1.61 across blocks |
| `wrong <= 1` (route 3's own gate) | fails in all four contexts, block 2 negative every time |
| r weakness, either direction | context-dependent, not directional: -8.19 ungated, +10.16 gated, 16 trades/block |
| dr -1 only | sign reverses by context |
| any stop-loss | swept over the full observed range on pxs at 5 s. Every binding level loses, monotonically. At 0.05% the win rate is 8.3% |
| momentum above ws4 | true on 100% of rows, winners and losers alike. No discrimination |

---

## 5. SIZING AND COST

| item | value | source |
|---|---|---|
| size | **22,000 coins**, fixed. On a staggered pair that is 22,000 EACH | Joe 0916 / 0917 |
| drag | **0.55%** of notional, round trip | Joe 0916, his own prior calculation |
| pyramid | **max 2** concurrent | Joe 0916, verified held-out 0917 |
| ride ceiling | **4** | Joe 0915, verified against 5 on 0917 |
| stop | **none** | swept, every binding level loses |

Leverage does not multiply the result — the coin count is fixed, so USDT P&L per trade is fixed.
Leverage only gates whether the margin fits. At ~$0.17 that is ~6.2x for one position, ~12.5x for
two on a 600 USDT balance.

---

## 6. THE EVIDENCE

87 days, 2026-06-10 to 2026-09-04, three equal-time blocks. Selection read block 1 ONLY.

| block | window | trades | mean net | wins | end bal from 600 | maxDD |
|---|---|---|---|---|---|---|
| 1 CHOSEN ON | 06-10 -> 07-08 | 92 | +7.03 | 48.9% | 1,247.00 | -6.43% |
| 2 HELD OUT | 07-09 -> 08-06 | 72 | +3.52 | 40.3% | 853.29 | -12.34% |
| 3 HELD OUT | 08-07 -> 09-04 | 91 | +12.03 | 64.8% | 1,694.83 | -12.21% |
| **HELD OUT 2+3** | | **163** | **+8.27** | | | |
| ALL 87 DAYS | | 255 | +7.82 | 52.2% | **2,595.12** | **-7.33%** |
| ALL 87 DAYS, staggered | | 255 | +7.78 | 52.2% | 2,584.77 | -7.28% |

**It is the only configuration tested whose held-out mean exceeds its selection block.** It ranked
11th of 15 on block 1 — a block-1 selection would have discarded it. Every candidate block 1
preferred degraded out of sample.

Block 2 is the weak month: +3.52 per trade, 40.3% wins, -12.34% drawdown. That is what a bad month
looks like and it is still positive.

---

## 7. THE TABLE — what the reconciler reads

`sneaky_trade_1`, built by `build_sneaky_trade_1.py`. **1,772 rows banked, 255 taken**, covering
2026-06-10 to 2026-09-04.

Key: `(st1_tp_bar, st1_src)`.

| column | what |
|---|---|
| `st1_tp_bar`, `st1_src` | the key. Test-point bar index and sourcing timeframe |
| `st1_tp_utc` | the test-point, for a chart |
| `st1_dr`, `st1_side` | the dr, and LONG/SHORT already derived. **Read `st1_side`, do not re-derive** |
| `st1_hi` | the carrying timeframe |
| `st1_drop`, `st1_wrong` | the cascade at the test-point |
| `st1_fx_bar`, `st1_fx_utc` | the fence exit |
| `st1_open_bar`, `st1_open_utc`, `st1_open_px` | **the ENTRY** |
| `st1_close_bar`, `st1_close_utc`, `st1_close_px` | **the EXIT** |
| `st1_mins` | open to close |
| `st1_mae_pct`, `st1_mfe_pct`, `st1_move_pct` | pxs at EVERY 5 s bar, in the dr direction |
| `st1_slot` | 0 = first order at this open/close pair, 1 = the second, staggered one 5 s bar at both ends |
| `st1_taken` | the gate verdict |
| `st1_why` | why a row was declined |

**EVERY signal is banked, including declined ones.** A reconciler needs to see a signal that should
NOT have traded as much as one that should — an extra fill is as much a break as a missing one.

Prices are **pxs** = DEMA(close, len 2) on the 5 s grid, read at EVERY bar. Sampling it every 30 s
was a defect and is fixed. Raw high/low runs 0.624% deeper at the median — that gap is the spike
content pxs exists to remove, so **pxs is the right lens for the signal and raw is the right lens
for margin and liquidation**.

---

## 8. THE RECONCILIATION CONTRACT — Joe 0917

It is two lines. Joe: *"surely it just needs the entry and exit timestamps to align with the
underlying events that cause them, possibly with a 30 second tolerance"* — and he is right.

```
1  a fill MATCHES a signal when its timestamp is within 30 s of that signal's
   st1_open_bar (for an entry) or st1_close_bar (for an exit)
2  a fill with no signal inside 30 s is an EXTRA
   a taken signal with no fill inside 30 s is a MISS
```

Everything else is a case to investigate, which is the receiving session's job — not a list to
pre-enumerate.

### Why 30 s is safe, measured

| | n | gap between consecutive bars, seconds: min / p1 / p5 / median |
|---|---|---|
| OPEN bars, taken rows | 216 | 20 / 142 / 439 / **22,805** |
| CLOSE bars, taken rows | 191 | 3,530 / 4,524 / 7,276 / 27,255 |

| tolerance | taken OPEN bars with another taken OPEN inside it |
|---|---|
| 5 s | 0 of 216 |
| 15 s | 0 of 216 |
| **30 s** | **1 of 216** |
| 60 s | 1 of 216 |

The median gap between taken opens is six hours. At 30 s exactly one pair is ambiguous. Tightening
to 15 s removes it; loosening to 60 s adds nothing new.

### THE THIRD LINE — the duplicate count. Joe 0917: *"agreed"*

Timestamp alignment cannot catch this, and it fires on day one.

```
3  REPORT, every run: the number of taken signals sharing an identical open AND close bar
```

**39 of the 255 taken signals share their open and close bar with another taken signal.** Same
timestamps, two or three separate signals — one move found by two or three timeframes. Timestamp
alignment calls all of them a match and cannot tell you whether live should have placed 1 order or
3.

```sql
SELECT st1_open_bar, st1_close_bar, COUNT(*) n, GROUP_CONCAT(st1_src) srcs
FROM sneaky_trade_1 WHERE st1_taken = 1
GROUP BY st1_open_bar, st1_close_bar HAVING n > 1;
```

### SETTLED, Joe 0917 — TWO orders, staggered 5 s at BOTH ends

> *"create the entries 5 seconds apart"* / *"stagger the exits as well. I've staggered to contain
>  slippage, so it makes sense to treat both ends"*

Two taken signals can land on the same open bar AND the same close bar. It is **always exactly
two**, always sourced by ws1 and ws2, always carrying ws4. 39 occurrences in 87 days — one every
2.2 days. They are **TWO orders**, and the second one — whose test-point came later — opens and
closes **one 5 s bar after the first**.

`st1_slot` carries it: 0 is the first order, 1 is the second. The bars in the table are already
staggered, so a reconciler reads them as written.

| version | trades | wins | mean net | total net | maxDD |
|---|---|---|---|---|---|
| same bar | 255 | 52.2% | +7.82 | +1,995.12 | -7.33% |
| entry staggered only | 255 | 52.2% | +7.80 | +1,989.66 | -7.28% |
| exit staggered only | 255 | 52.2% | +7.80 | +1,990.23 | -7.33% |
| **BOTH ends** | **255** | **52.2%** | **+7.78** | **+1,984.77** | **-7.28%** |

Cost **-10.34 USDT over 87 days, 0.52% of the total.** That is **price drift only** — the collision
it avoids is NOT in the 0.55% drag, which was measured on single fills. The stagger pays for itself
if the collision costs more than **0.27 USDT per pair**.

**Measure the real collision cost once fills exist.** It cannot be measured from the tape, and it
is the number that says whether the -10.34 was worth paying.

## 8b. CONFIRMED AS-IS — Joe 0917: *"the other items are confirmed"*

Deferred by Joe 0916, *"agreed that the others will surface as needed"*:

| item | note |
|---|---|
| the 0.55% drag | measured at 88,000 coins, not 22,000. Joe: *"accepting it is ok"* |
| warm-up state at session start | the lines and the dr latch must be warm before the first stretch is usable |
| the order type that closes at a dr flip | **SETTLED, Joe 0917: an exit order.** Not a new position, not a reversal |
| the leverage setting on the fake API | ~6.2x for one position, ~12.5x for two |

---

## 9. TRAPS — things that were wrong and were fixed

| trap | what it looked like |
|---|---|
| the dr-bias rule applied to sneaky-1 | inverts every row. MAE and MFE swap. Caught twice |
| `argmax` on the leash for the close | not causal. A sandbox cannot reproduce it |
| the open searched up to the close | lookahead leaking backwards. 17.8% of rows appear or vanish |
| MAE/MFE sampled every 30 s | understated the excursion. Read pxs at every 5 s bar |
| a sweep with no criteria set first | 3,618 combinations ranked with no trade floor produced 14-trade winners with 100% win rates |
| a cap or a floor nobody asked for | Joe 0916: *"don't use caps anywhere. real life trading has no take-backs - you commit and hang on"* |

---

## 10. FILES

| file | what |
|---|---|
| `optimus9/compute/sneaky_trade_1.py` | the producer |
| `optimus9/compute/test_points.py` | the test-point producer |
| `build_sneaky_trade_1.py` | builds the table |
| `docs/wsf_dtf_v3_spec.md` §17.3 | the spec |
| `sneaky_trade_1` (db) | the signals |
| `wsf_dtf_v3_config` (db) | the knobs, v6, 45 rows |
