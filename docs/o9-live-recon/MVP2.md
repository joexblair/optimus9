# strat-wsf-leash — MVP2

What MVP1 deliberately leaves out, and why. **Nothing in this file is MVP1 work.** It exists so the
o9-live+fakeAPI session can tell a deferral from a gap, and so a deferred item is not quietly
re-scoped into the recon.

Joe 0929: *"the goal for this next step is purely recon against backtest. I'll keep improving the
strategy in the background while o9-live is under review"*.

## The MVP1 / MVP2 line

| | MVP1 | MVP2 |
|---|---|---|
| what is compared | **selection** — does o9-live trade the same bar, same side, same reason | price, fill and P&L |
| the exchange | fakeAPI only | unchanged for MVP2 unless Joe says otherwise |
| order type | **market** | limit placement |
| the 0.70% stop | **client-side, in the engine** | plus a LARGER exchange-resident backstop |
| position size | not needed — selection does not price | required |
| scoring | MAE/MFE percentages of entry. NO P&L — Joe 0917 | unchanged until Joe reopens P&L |

## The four MVP2 items

### 1. Price recon

Joe 0929: *"no need to recon price yet, that will be MVP2"*.

MVP1 compares **whether** a bar was traded, on **which** side, for **which** reason. It does not
compare entry price, exit price, fill price or slippage. `RECON.md`'s four mismatch classes —
`selection`, `causality`, `cache`, `stop` — are all reachable without price. `stop` compares the
**bar** the stop fired on, not the price it filled at.

**What MVP2 adds:** a fifth class. Entry/exit price divergence between o9-live's fills and the
backtest's `pxs` reads, reported separately from selection, exactly as the other four are.

**ONE CHECK IN PARTICULAR, AND IT IS NOT IN MVP1's LIST.** The stop is a percentage of the ENTRY
price, and the two sides do not agree on what the entry price is:

| | what "entry" is |
|---|---|
| the backtest | `pxs` at the sig bar - `DEMA(close, 2)` on the event tape. A smoothed value, not a traded price |
| o9-live | the actual fill of a market order |

Different starting numbers give different stop PRICES from the same 0.70%. `RECON.md`'s stop check
#2 verifies o9-live uses its own entry rather than a later mark; **nothing compares o9-live's entry
against the backtest's.** That comparison is a price comparison, so it is MVP2 — but it was absent
rather than deferred until this was written down.

### 2. The exchange-resident stop backstop

Joe 0929-late, on the finding that a client-side-only stop leaves a position naked through a
disconnect: *"yes. that's MVP2 - we'll apply a larger stop with the exchange as a backstop"*.

**MVP1 state:** the 0.70% stop is held by the engine, client-side. If o9-live disconnects while a
position is open, nothing at the exchange closes it.

**MVP2 shape:** two stops, not one.

| stop | where | level | fires |
|---|---|---|---|
| the strategy stop | client-side, in the engine | **0.70% of entry** — Joe ruled it 0929 | normally, on the `pxs` bar |
| the backstop | resting at the exchange | **LARGER — value NOT specified** | only when the engine is not there |

**UNSPECIFIED, and it is Joe's:** how much larger. It is a level, not a structure, so it does not
get decided here. It needs the same treatment the 0.70% got — a sweep, a ladder, and Joe reading it.

**The constraint that makes it safe:** the backstop must be far enough out that it NEVER fires
ahead of the 0.70% client stop in normal operation. If it does, o9-live exits at a level the
backtest has no concept of, and every stop-class comparison in `RECON.md` becomes noise. The
backstop is a disconnect device, not a second strategy knob.

### 3. Limit order placement

Joe 0929-late: *"order type: market. MVP2 will develop the placement of limit orders"*.

**MVP1 state:** every open and every close is a **market** order. That is what makes the selection
recon clean — a market order fills, so a missing trade in o9-live is a selection fault and nothing
else. A resting limit that does not fill would be indistinguishable from a signal that never fired.

**What MVP2 has to answer, and none of it is decided:**

- where the limit rests relative to the `pxs` bar
- what happens to an unfilled limit when the next signal arrives
- whether an unfilled limit counts as a trade for recon purposes
- whether the stop is also a limit, or stays market

### 4. Position size

`OPEN.md` item 3. 22,000 coins is banked for **sneaky-1**. **Nothing is set for this strategy.**

Not needed for MVP1 — selection does not price. Needed the moment price enters, which is item 1.

## What MVP2 inherits and must not re-litigate

These are ruled. They do not reopen because price enters.

| | |
|---|---|
| a sig_utc closes ONLY on an opposing dr | a same-dr sig_utc is INERT |
| the dr-flip backstop CLOSES but never OPENS | Joe 0929-late |
| the MAE cap is **0.70%**, applied as a STOP | Joe read the 0.05-step sweep and ruled it |
| same-bar, dr-flip vs sig_utc | **the dr-flip wins** |
| same-bar, stop vs opposing sig_utc | **the STOP wins** — Joe 0929-late |
| the backtest's fill is the SPEC | `pxs` resolves intrabar. Do NOT model slippage |
| P&L | closed since 0917. MAE/MFE only |

## The one thing that must be settled BEFORE MVP1 runs, not in MVP2

**Does a stop free the book?**

In the backtest a stopped trade does not release the position — the trade count is 753 at every cap
from 0.05 to 4.00 and at no cap, because the cap is applied in **scoring**, not in the walk. If
o9-live exits at the stop and is then flat, a later same-dr sig_utc — currently INERT, because a
position is open — will open a trade the backtest never has.

**Selection then diverges by construction, and the recon reports it as a selection fault that is
really a bookkeeping difference.** This is not an MVP2 item. It is unruled and it is in MVP1's path.
See `OPEN.md`.
