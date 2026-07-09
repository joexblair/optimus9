# 0709 repairs — TRADE (stop · governor · sizing)

Milestones the bot must pass to be profitable. Source: the 0709 live arm probe (`O9_PRODUCER=arm`, 10:19→17:59,
28 closes, 10 legs open at stop) plus 42d backtest. Parent: `docs/arm_delay_research.md` (CLOSED) ·
`docs/dynamic_risk_spec.md`.

| mechanic | learnt | needs attention |
|---|---|---|
| **stop** | Only exit that exists in the probe. 20 stop-outs of 28 closes. Level `0.90%`, realized `~1.075%`. | The stop costs ~17% more than its label. **Unexplained gap.** |
| **sizing** | `qty` pinned at the `66000` cap on **every** trade. Never dynamic. | `dynamic5x` never engaged; the cap is the real sizer. |
| **governor** | Built, tested, **not wired**. −$1,514 over 28 closes; equity `$500 → -$1,014`. | 10 legs open at stop. No exposure cap enforced. |

---

## 1. The stop overshoots its label

**[read]** `strategy.py:100` — the trigger is the **closed bar**, per leg, from that leg's own entry:
```python
if (px_T - entry) / entry * 100.0 * d <= -sl:      # sl = lr.sl
```
**[measured]** `lr.sl = 0.9` (`lp_lr_sl = 0.9`).

### Example — two stops, identical realized loss **[measured]**
```
14:23:12 -> 15:35:17  Buy   0.14706055 -> 0.14547942   -1.075%   fee 10.62  net -114.97   notional $9,706
13:49:27 -> 13:51:07  Sell  0.14595684 -> 0.14752534   -1.075%   fee 10.65  net -114.17   notional $9,633
```
Two different sides, two different durations (72 min vs 100 s), **the same −1.075%**.

**The 0.175% gap is not explained.** Candidates, none measured:
- overshoot between 5s closes (the trigger reads a *closed* bar; price can be past the level when it fires),
- `OrderBookWalker` fill cost on 66,000 coins against the synthetic book,
- the fee (≈0.11% round trip) already sits in `net`, not in the `%` figure above — so it is **not** the fee.

That two independent trades land on the same figure to 3 d.p. suggests a **level**, not a distribution.
**[inferred]** Something is computing the exit price from the trigger rather than walking the book. Unverified.

**Proposed fixes:**
- **(a)** Measure it first: log `px_T` at trigger, the intended level, and the fill, for every stop. One column
  each. Until then the stop's true cost is unknown.
- **(b)** If it is book-walk cost: it scales with `qty`, and `qty` is pinned at the cap (§2). Shrinking size
  shrinks the stop's overshoot.
- **(c)** If it is a computed level: it is a bug, and every stop-loss number we have quoted is 17% optimistic.

---

## 2. Sizing never engaged

**[measured]** All 28 closed trades and all 10 open legs have `qty = 66000` — the `max_order` cap. Notional
~$9,500–9,700 at FARTCOIN's price. `dynamic5x` sizes off equity, but the cap binds first, so **the cap is the
sizer** and equity never modulated a single order.

**Consequence:** the account went `$500 → -$1,014` with orders that never shrank as it fell. A paper exchange
does not liquidate; a real one would have, long before −$1,014.

**Proposed fixes:**
- **(a)** Cap must be **relative** (a multiple of equity), not absolute, or `dynamic5x` is decorative.
- **(b)** Liquidation modelling in `fakeAPI` — a paper account that can go to −$1,014 teaches nothing about
  survival.

---

## 3. The governor — built, not wired

**[read]** `optimus9/live/risk.py` — `RiskGovernor.assess()` → `RiskVerdict{leverage, open_allowed,
add_allowed, max_exposure, reason}`; `RiskGate.apply()` drops vetoed opens/adds, closes always survive. Knobs in
`risk_config` (14 rows, `max_exposure_mult = 16.0` derived from the p99 of the v2_walk stack). **Never called
from `on_bar`.**

### Example — 0709 hedge run, the pyramid that made the case **[measured]**
```
0709_05  Sell  entry 0.14344   SL  -21.07
0709_06  Sell  entry 0.14355   SL  -21.45      each leg added at a WORSE price
0709_07  Sell  entry 0.14374   SL  -21.91      than the one before it
0709_08  Sell  entry 0.14386   SL  -21.92
0709_09  Sell  entry 0.14390   SL  -21.69
                                    -------
                                    -$108 of that session's -$144
```
Joe's rule — **pyramid only further along the leg** — blocks all four adds at any tolerance
(`risk.leg_further_along`, reference = the **first** leg).

**But X3 says the gate costs money.** **[measured]** 42d, unit notional:
```
per-leg exit  : off 0.514 | tol 0.00 0.270 (-47%) | tol 0.30 0.402 (-22%)   depth 16 -> 14
stack-close   : off 0.334 | tol 0.00 0.216 (-35%) | tol 0.30 0.320 ( -4%)   depth 11 -> 11
```
The governor destroys net at **every** tolerance in **both** columns, and improves monotonically as it
approaches doing nothing. **It blocks 930 legs and does not reduce max depth at all** under stack-close.
The drawdown-added legs carry **positive** expectancy on this book: adding into drawdown *amplifies a good
entry* more than it deepens a bad one.

**X3 measured the MEAN. The governor is a VARIANCE reducer.** No drawdown path, no worst-episode, no
risk-of-ruin. `net` can neither convict nor acquit it. **Do not cite X3 as "the governor is bad."**

**Proposed fixes, ordered:**
1. **X3b** — equity-drawdown path, max adverse excursion on the averaged position, worst single episode, depth
   under a *compounding* sizer. **Required before any governor decision.**
2. Re-derive `max_exposure_mult` from a **hedge** replay (the one-way sim understates hedge gross).
3. Wire `RiskGovernor` into `on_bar` — needs a high-water tracker on `o9_account`, a vol percentile, and the
   exposure input.
4. Re-run X3 on the **fixed arm**. Everything above was fitted on the breach-arm book.
