# Fib / line-positioning early-error close — spec STUB (Joe 0708, research-later)

**Status: STUB.** Idea captured, NOT designed. Joe: "use line positioning and fib to decide if we've made an error and
need to close trades early — this new idea should be its own spec; we'll research it further at the time."

## The idea
A THIRD exit reason, distinct from the two we have:
- current TP: shared s7r-reversal cascade (`exit`/`strand`) — the whole stack.
- current SL: per-leg −sl% from each leg's entry.
- **NEW: `error_close`** — line positioning + fib retracement/extension say the trade was a *mistake* (entered against
  the developing structure) → close early, before the per-leg SL, to cut the loss cheaper than the stop.

## Why its own spec
It's an error-DETECTION mechanic (was this entry wrong?), not a profit-taking or fixed-stop mechanic. Different question,
different inputs (fib levels, line position within a leg), different verdict. Fusing it into `lr_exit_v2` would conflate
"take profit / stop out" with "abort a bad entry" — SRP says separate producer, own exit reason, fed into the same intent
stream as an independent verdict the executor can toggle.

## Shared dependency to design once
The **fib / line-positioning reader** (where is price within the current potential leg? which fib level?) is *also* the
future input to dynamic leverage ([[dynamic_risk_spec]] item 3 — bigger leg → more leverage). Build the reader once as a
shared substrate; the risk governor consumes it for sizing, this spec consumes it for the error verdict.

## To research at the time (not now)
- What defines "the leg" for fib anchoring (which swing hi/lo, which TF)? Causal/emerging only — no closed-bar fib.
- Which retracement/extension levels flag an error vs normal noise.
- Interaction with the per-leg SL (does error_close pre-empt it, or is it a separate faster stop?).
- Does it close the whole stack or just the offending leg?

No build until Joe opens this thread.
