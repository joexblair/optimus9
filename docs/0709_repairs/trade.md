# 0709 repairs — TRADE (stop · governor · sizing)

Milestones the bot must pass to be profitable. Source: the 0709 live arm probe (`O9_PRODUCER=arm`, 10:19→17:59,
28 closes, 10 legs open at stop) plus 42d backtest. Parent: `docs/arm_delay_research.md` (CLOSED) ·
`docs/dynamic_risk_spec.md`.

| mechanic | learnt | needs attention |
|---|---|---|
| **stop** | Only exit that exists in the probe. **20** stops of 28 closes. Label `0.900%`, realized mean **0.981%**. | **RESOLVED.** Gap is 0.081%: 0.047% bar-close granularity + 0.033% book-walk. Stop is not the leak. |
| **stop clustering** | **15 of 20 stops fire in 6 clusters.** Largest: 4 stops in 25s = **−$438** (29% of total loss). | Clusters are pyramid stacks dying together. Links sizing + governor. |
| **sizing** | `qty` pinned at the `66000` cap on **every** trade. Never dynamic. | `dynamic5x` never engaged; the cap is the real sizer. |
| **governor** | Built, tested, **not wired**. −$1,514 over 28 closes; equity `$500 → -$1,014`. | 10 legs open at stop. No exposure cap enforced. |

---

## 1. The stop — RESOLVED 0709. It costs 0.081% over its label, and it is not the leak.

**[read]** `strategy.py:100` — the trigger is the **closed bar**, per leg, from that leg's own entry:
```python
if (px_T - entry) / entry * 100.0 * d <= -sl:      # sl = lr.sl
```
**[measured]** `lr.sl = 0.9` (`lp_lr_sl = 0.9`). **[read]** the exit walks the real order book
(`services/fakeapi/fill.py` `OrderBookWalker.walk` → volume-weighted average fill).

### Decomposition, all 20 stops **[measured]**
```
realized  mean -0.981%   min -1.075%   max -0.859%   std 0.056
trigger   mean -0.947%   min -1.053%   max -0.908%   std 0.039     (label -0.900%)
slippage  mean -0.033%   min -0.153%   max +0.076%   std 0.059     favourable on 6 of 20
```
- **-0.047%** — bar-close granularity. The check runs once per 5s bar close, so price is already past the level
  when the stop fires.
- **-0.033%** — book-walk cost on 66,000 coins.
- The fee (~0.11% round trip) is inside `net`, not inside the `%` figures.

**The earlier reading — "-1.075% twice, therefore a computed level, not a distribution" — is refuted.** Two
trades coincided at three decimals. Six of twenty fills came in **better** than the bar close, which a computed
exit cannot do.

Count correction: `11:32:37` (+0.111%) is a single-leg **stack close**, not a stop. **20 stops, not 21.**

## 1b. Stops arrive in clusters — the real signal **[measured]**
```
10:48:17 -> 10:48:52   2 stops   35s
12:26:12 -> 12:27:12   2 stops   60s
12:38:32 -> 12:39:52   3 stops   80s
13:49:57 -> 13:50:02   2 stops    5s
15:35:17 -> 15:35:42   4 stops   25s     -114.97 · -104.36 · -112.53 · -106.27  =  -$438
15:39:17 -> 15:40:02   2 stops   45s
                       5 singles
```
**15 of 20 stops fire inside 6 clusters.** Each cluster is a stack of pyramided legs stopping out together on
one adverse move. The `15:35` cluster is **-$438 in 25 seconds — 29% of the run's entire loss.**

This joins three rows of this table into one mechanism:
- **stop** — well-behaved, 0.081% over label. Not the leak.
- **sizing** — every leg is 66,000 coins, so a 4-leg cluster loses `4 × ~$110` with no taper (§2).
- **governor** — the first-leg pyramid gate blocks the later legs of exactly these clusters (§3).

**Proposed fixes:**
- **(a)** Nothing on the stop itself. Its cost is measured and small.
- **(b)** Reduce the trigger granularity only if `0.047%` is judged worth a faster check (it is 48% of the gap).
- **(c)** The cluster is the target, not the stop. See §2 and §3.

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

**New evidence (0709 probe, §1b):** 15 of 20 stops fired in 6 clusters; the largest was **4 legs in 25 seconds
for -$438**. X3 measured the governor's effect on the **mean** and found it costs 22-47%. It never measured a
cluster. **A cluster is precisely the worst-episode event X3 could not see.**

**Proposed fixes, ordered:**
1. **X3b** — equity-drawdown path, max adverse excursion on the averaged position, worst single episode, depth
   under a *compounding* sizer. **Required before any governor decision.** Score the 6 clusters above with and
   without the first-leg gate: that is the governor's case, measured on the axis it was built for.
2. Re-derive `max_exposure_mult` from a **hedge** replay (the one-way sim understates hedge gross).
3. Wire `RiskGovernor` into `on_bar` — needs a high-water tracker on `o9_account`, a vol percentile, and the
   exposure input.
4. Re-run X3 on the **fixed arm**. Everything above was fitted on the breach-arm book.
