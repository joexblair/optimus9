# 0709 repairs — EXIT

Milestones the bot must pass to be profitable. Source: the 0709 live arm probe (`O9_PRODUCER=arm`, 10:19→17:59,
38 arms, 28 closes) plus 42d backtest. Parent: `docs/arm_delay_research.md` (CLOSED) · `docs/exit_brd.md`.

| mechanic | learnt | needs attention |
|---|---|---|
| **winners** | 8, all from an *opposing* arm's stack-close. **No profit mechanism exists.** | The arm alone has no edge. Expected — no gate, no finisher. |
| **stack-close** | One reversal exit closes the side's **whole** stack. Costs **35%** of the backtest book. | Not a bug — Bybit hedge mode holds ONE position per `positionIdx`. |
| **exit attribution** | **Recovered.** `exit_order_id` cardinality encodes the mechanism. All 8 winners = the 3 stack closes (+1 near-flat). | None. The audit row was a convenience, not the record. |

---

## 1. There is no profit mechanism

**[measured]** In the probe the arm producer has **no exit signal at all**. The only things that close a trade
are (a) the per-leg stop and (b) an *opposing* arm's stack-close. A winner is therefore not banked — it is
**interrupted**.

### Example — 07-09, a winner and a loser, same magnitude **[measured]**
```
11:36:37 -> 12:50:07  Buy  0.14380024 -> 0.14549280   +1.177%   net  +101.21
14:23:12 -> 15:35:17  Buy  0.14706055 -> 0.14547942   -1.075%   net  -114.97
```
Both ~1.07% moves. One is called a win, one a loss. **The exit chose neither.** 20 of 28 closes were stops.

**Why this matters:** the exit is where the money is. From the earlier exit work — backtest signal-exits average
**+1.060%** with MFE p50 **1.225%**, while live's best of 13 (0708 hedge run) was **+0.36%**. Live surrenders
~0.8% per winner.

**Proposed fix:** the arm probe was never supposed to have an exit. **Restore the full cascade** (gate →
finishers) and re-measure. Do not read exit conclusions from this probe.

---

## 2. Stack-close — the exchange, not a bug

**[read]** `strategy.py:92-94`: *"SHARED take-profit: a REAL reversal exit for THIS side at T → close this
side's WHOLE stack."* **[read]** `engine.py:55,64`: an add re-weights `avg_entry`; a close realizes
`bd*(px - avg_entry)*qty`. **There are no legs at the exchange** — one averaged position per `positionIdx`.
`o9_ledger`'s per-leg rows are bookkeeping. You cannot exit leg 3 and hold leg 1.

### Example — 0709 hedge run, three legs one price **[measured]**
```
0709_02  Buy   exit_px = 0.14365786
0709_03  Buy   exit_px = 0.14365786    <- one exit signal, three legs closed
0709_04  Buy   exit_px = 0.14365786
0709_10  Sell  exit_px = 0.14496807
0709_11  Sell  exit_px = 0.14496807
0709_12  Sell  exit_px = 0.14496807
```

**[measured]** X3, 42d, 2628 trades, unit notional: per-leg exit `0.514` → stack-close `0.334`. **−35.0%.**
A third of `v2_walk`'s edge was priced on 2,628 independent exits a real account cannot take.

**Proposed fixes:**
- **(a)** Price every backtest under `stack_model` semantics. The number, not the fiction.
- **(b)** Bybit accepts **partial `reduceOnly`**, so "exit one leg's worth" is approximately executable — but the
  PnL strikes against the **averaged entry**, not that leg's entry. It narrows E1; it does not dissolve it.
  **Untested.**
- **(c)** Design exits for an averaged position from the start, rather than porting a per-leg model.

---

## 3. Exit attribution — RECOVERED

`exit_order_id` **cardinality** encodes the mechanism, independent of the audit table. A stack close places ONE
order for the whole side (`record_close_side`), so N legs share one `exit_order_id`. A per-leg stop places its
own order (`record_close_leg`), so it appears alone.

**[measured]** 24 exit orders closing 28 legs:
```
 3 orders closed >1 leg  -> STACK CLOSES: 2 + 2 + 3 legs
                            net +149.46 (10:49:27) · +192.33 (12:50:07) · +238.78 (15:55:27)   ALL WIN
21 orders closed  1 leg  -> 20 losses (the stops) + 1 near-flat win (+0.09, 11:32:37)
```

**All 8 winners are the 7 legs inside the 3 stack closes, plus one $0.09 single-leg close.** Nothing is missing.

`3 multi-leg closes + 1 single-leg close = the 4 recorded 'close' decisions.` The arithmetic was always
consistent — an earlier reading compared a count of *decisions* against a count of *trades*, and a stack close
is **one decision closing N legs**.

**The finding underneath:** every real winner in 7h40m came from being **interrupted by an opposing arm**. The
machine has no mechanism of its own for banking a profit. 20 of 28 closes (71%) were stops.

**Proposed fix:** run `migrate_decision_action.py` so the audit is complete — but note the record was
reconstructible without it. Do not treat `o9_decision` as the source of truth for exit mechanism; the order
cardinality is.

---

## 4. Carried forward from the exit work (not re-measured on the new arm)

- **[measured]** Curl-cascade (gate `s7r` breach-then-OOB-curl @105s + unlatch `s5r` coarse-curl @40s) = **+1.4%**
  keeper on `v2_walk`. Shipped, DB-driven.
- **[measured]** **Every** price overlay is catastrophic: TP −23% @1.5% down to −100% @0.3%; naive trail −84%
  → −100%; best armed trail (arm 0.7 / trail 0.5) −48.6%. Crypto's intra-move whip truncates the fat-tail
  winners that carry the compounding book. **Exits must be signal-based.**
- **[read]** `strand_rescue` **is** on the live path (`strategy.py:81` wraps `lr_exit_v2`; `:92` treats
  `'strand'` as a real exit). It is gated on the completed `x[6]=='SL'`. **Open and unexamined:** can a rescue
  *execute* live, when the SL order already went out at bar `k < T`?

**All of the above were fitted on the breach-arm book.** Re-baseline before trusting any of them.
