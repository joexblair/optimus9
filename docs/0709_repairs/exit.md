# 0709 repairs — EXIT

Milestones the bot must pass to be profitable. Source: the 0709 live arm probe (`O9_PRODUCER=arm`, 10:19→17:59,
38 arms, 28 closes) plus 42d backtest. Parent: `docs/arm_delay_research.md` (CLOSED) · `docs/exit_brd.md`.

| mechanic | learnt | needs attention |
|---|---|---|
| **winners** | 8, all from an *opposing* arm's stack-close. **No profit mechanism exists.** | The arm alone has no edge. Expected — no gate, no finisher. |
| **stack-close** | One reversal exit closes the side's **whole** stack. Costs **35%** of the backtest book. | Not a bug — Bybit hedge mode holds ONE position per `positionIdx`. |
| **exit attribution** | 8 winners, only **4** `close` decisions recorded. | 20 lost audit rows ⇒ we cannot say what closed 4 winners. |

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

## 3. Exit attribution is missing

**[measured]** 28 closes. `o9_decision` holds `close: 4` and **zero** `close_leg` (the enum rejected them —
see `misc.md`). 8 winners exist; only 4 stack-closes were recorded. **We cannot attribute 4 winners' exits.**

That is the concrete cost of the schema bug: not lost trades — **lost causality of the exits**.

**Proposed fix:** run `migrate_decision_action.py`, then re-run any probe whose exit attribution matters.

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
