# Exit Mechanism — Business Requirements (CFO view)

*Audience: CFO with a working understanding of the s-lines. Framing: capital, realized P&L, risk — grounded in a
review of the exit code (`lr_exit_v2`, `strand_rescue`, the live SL/TP path) and current live/backtest data (0708).*

---

## 1. Purpose (one line)
The **entry** decides *whether* we hold a position; the **exit** decides *how much of it we keep*. The exit's business
job is to **realize as much of each trade's favourable move as possible while capping the capital lost on adverse
moves** — i.e. to maximize expectancy per dollar risked. On the current book this is where realized P&L is won or lost.

## 2. How the exit works today (from the code)
The exit is the **entry cascade run in reverse** — same machine, pointed at the *favourable* extreme. Per trade it walks
four stages, on the trade's side:
1. **Arm** — `s5m` breaches OOB (the move is extended in our favour).
2. **Gate** — `s7r` predict-then-breaches (momentum confirmed).
3. **Unlatch** — `s5r` curls back (the move is rolling over).
4. **Finisher** — `s30a + s15a` confirm the turn → **EXIT** (a trend-reversal take-profit).

Plus two rules:
- **Shared take-profit (Option B):** a pyramided stack shares *one* reversal exit — when it fires for the held side,
  **all same-side legs close together.** Each leg also carries its own **−0.9% stop-loss** (`lp_lr_sl`), checked on the
  5-second close, **no time limit**.
- **Strand-rescue:** if a trade would stop out only because momentum (`s7r`) never showed up (a sideways market), it exits
  at the `s5r` curl instead of bleeding to the stop.

**Net:** the only planned exit is a **full trend-reversal**. There is **no profit target**, the stop rarely binds, and
positions can be held indefinitely.

## 3. Current financial behaviour (observed — the problem)
*Live evidence is a 12-hour, $500 paper window (directional, not conclusive); the 6-week backtest is the real evidence base.*
- **We give back winners.** With no profit target, a trade that reaches **+1%** is held through the reversal all the way
  back down. *led10: +1.0% → closed −1.2%* — a ~2.2% round-trip surrendered.
- **The stop does not protect.** The −0.9% stop is measured on 5-second closes, so a **fast drop skips it** (fires deep or
  not at all) and a **slow bleed sits just under it** for hours. Result: **0 stop-exits in 12h**, and realized losses ran
  to **−1.2% to −1.6%** — well past the intended 0.9%.
- **We hold dead capital.** No time limit → *led10 was held 2h17m* bleeding sideways, tying up leveraged capital with no
  live thesis, then closed on a late drop.
- **Aggregate:** 12 losing trades, **−$273 in 12h** on the paper book. The shape — *reach favourable excursion, surrender
  it* — is confirmed in the 6-week backtest, not just the live sample.

## 4. Business requirements (what the exit MUST do)
| # | Requirement | Business rationale |
|---|---|---|
| **R1** | **Bank favourable excursion** — realize a defined share of the peak gain without waiting for the full reversal (a profit target / faster finisher). | Stops handing back winners; converts unrealized gains into cash. |
| **R2** | **A stop that binds at its stated level** — react on mark/tick, not the 5s close, so realized loss ≈ intended loss regardless of drop speed. | Capital-at-risk is *known and bounded*; no −1.6% surprises on a 0.9% stop. |
| **R3** | **Release stalled capital** — exit positions that stall beyond a defined window. | Capital efficiency; leveraged margin should not sit idle-at-risk. |
| **R4** | **Per-position protection under pyramiding/hedge** — a weak leg stops out on its own merit; a strong leg's reversal must not drag a weak one out (nor vice-versa). | The shared-TP currently couples unrelated legs; each dollar should be protected on its own terms. |
| **R5** | **Causal & cost-aware** — decisions use only real-time information (no hindsight) and are measured net of fees + slippage (~0.18% round-trip). | Prevents look-ahead inflation (the prior era's paper edge was void); reflects realizable P&L. |

## 5. Success metrics (the CFO scorecard)
- **Expectancy per trade, net of cost** — the north star.
- **Win rate + average win vs average loss** — the give-back ratio (R1).
- **Realized MAE-tail (worst-decile loss)** — the capital-at-risk gauge (R2).
- **Max drawdown + time-in-market** — capital efficiency (R3).
- **Live-vs-backtest realized-P&L gap** — does live capture what the model promises?

## 6. Constraints & non-goals
- **Not an entry filter.** Entry quality is a separate workstream; this BRD is exit-only.
- **Causal-only is non-negotiable.** No closed-bar / look-ahead logic.
- **Every change proven by a 6-week A/B** — "different ≠ better"; a change ships only if expectancy and MAE-tail both hold.

## 7. The decision being asked
Approve **building and A/B-testing** the exit changes implied by R1–R4 (profit target, binding stop, time-out, per-leg
protection) against the 6-week window, with **go/no-go on expectancy + MAE-tail**, causal and cost-adjusted. The exit is
currently the **highest-leverage fix on realized P&L** — the entry book is roughly break-even-to-positive; the exit is
where the money is leaking.
