# The strategy, and what the recon must prove

## The rules, Joe 0929 verbatim

> "every ungated sig_utc timestamps create a trade reversal - ie it closes the existing trade and
> opens a new trade. it also opens a trade if there is no incoming trade, in contrast to the dr-flip
> mech"
>
> "rule#1 is applied to gate the non-trade sig_utc's"
>
> "dr-flip is the backstop - if a open trade did not reach a sig_utc before dr-flip, then dr_flip
> creates a trade reversal (closes and opens). dr-flip can only open a new trade if dr-flip needed to
> close an incoming (back-stopped) trade"

## The backstop is the flip BACK to the trade's own dr

Joe 0929, correcting a build that had it inverted:

> "trade 1 starts at +1dr, creating a SHORT trade. -dr1 is the target side for a SHORT trade, so
> SHORT must go deeper into -1dr to claim more profit. the true dr-flip backstop for a SHORT trade is
> when the trade leaves its target side (because no trade signal closed it) and climbs towards +1dr
> (the backstop dr-flip)"

A trade opened at dr **D** is working while the dr sits at **−D**. The backstop is the end of that
−D stretch — **two flips forward** from the open, not one. The inverted reading gave 37 trades on
09-01 against 22.

**A consequence, and it is the rule not a choice:** at a backstop the dr is D again, so the trade the
flip opens carries the **same direction** as the one it just closed. Joe has been shown this.

`dr +1 = SHORT, dr -1 = LONG`. Joe 0925: *"+dr = SHORT position, -dr = LONG postition"*.

## The knobs — all in `wsf_trade_config`, version 1

| name | value | source |
|---|---|---|
| `leash_instance` | v7 | Joe 0929: *"v7"* |
| `gate` | `rule1_gate.open` — the rule#1 leg OR the scenario leg | Joe 0929: *"using the gate that you validated in our shared sheet, col L"* |
| `same_bar_priority` | dr-flip | Joe 0929: *"same bar priority: dr-flip"* |
| `rule1_tol_min` | 7.0 total, so 42 bars each side | Joe 0924 |
| `rule1_fence_lo/hi` | 27.0 / 73.0 | Joe 0923 |
| `oob_lo/hi` | 15.0 / 85.0 | Joe 0913: *"oob is alwasy 15/85"* |
| `latch_tf` | 13 | Joe 0925 |
| `latch_wob` | 8 bars = 40 s | Joe 0926: *"we have to stick on 8"* |
| `mage_fence_lo/hi` | 25.0 / 75.0 | build_wsf_dtf_v3 |
| `div_tf` | 1 — the divergence runs on ws1r | Joe 0924 |
| `scenario_lines` | ws2r, ws3r, gcws30r | Joe 0924 |

**The knobs are NOT in `wsf_dtf_v3_config`, deliberately.** Spec §21.6: `leash_bank.knob_string` puts
the v3 config version inside `wsl_knobs`, so a bump would split the next leash write off from the
121-row bank. That consequence is Joe's to sanction and he has not. `wsf_trade_config` is a separate
table for exactly that reason.

## The reference backtest, banked

`build_wsf_trades.py` → table `wsf_trades`, key `wtc_v1_v7_rule1_gateopen`, window
`2026-09-01..2026-09-06`.

| | |
|---|---|
| trades | 142 closed, 1 still open |
| opened by sig_utc / dr-flip | 64 / 78 |
| closed by sig_utc / dr-flip | 63 / 79 |
| MFE > MAE | 76 of 142 |
| MAE mean / median / max | 0.809 / 0.425 / 5.811 |
| MFE mean / median / max | 1.062 / 0.739 / 4.987 |
| SHORT, n 81 | MAE mean 0.865, MFE mean 1.178, MFE > MAE 47 |
| LONG, n 61 | MAE mean 0.735, MFE mean 0.908, MFE > MAE 29 |

09-01 alone: 22 closed, 15 opened by sig_utc and 7 by dr-flip, MFE > MAE 11 of 22.

**No P&L.** Joe 0917 closed P&L and kept MAE/MFE. Do not reintroduce it.

## What the recon must prove

1. **Selection** — o9-live opens and closes on the same bars the backtest does.
2. **Causality** — the backtest's verdicts do not change when re-run later over the same bars. A
   verdict that moves is lookahead. Joe 0929: *"it every recon job, review the backtest's last 24
   hours and re-validate all validated o9-live trades (this re-validation will expose lookahead if
   there is any)"*.
3. **Cache integrity** — Joe 0929 chose the line-cache over a live tape deliberately: *"I'm going to
   say the line-cache because that organically gives us another test-point (ie, is cache and
   real-time kline collection in sync)"*.

**Price is out of scope for MVP1.** Joe 0929: *"no need to recon price yet, that will be MVP2"*.

## The timestamp gap is the point

Joe 0929: *"this is exactly what we're reconcilling. o9-live has no choice - it must use wall-clock"*.
The backtest is bar-indexed on the 5 s grid; o9-live stamps wall-clock. Mapping one to the other **is**
the test, not a nuisance to be papered over.
