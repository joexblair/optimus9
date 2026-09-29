# The strategy, and what the recon must prove

> **READ THIS FIRST. THE RULES BELOW WERE SUPERSEDED ON 0929-late.**
>
> The verbatim quotes in the next two sections are Joe's words from 0929-EARLY and they are kept
> because they are the origin of the mech. **They are not what the code does.** Three rulings landed
> after them:
>
> | | |
> |---|---|
> | a sig_utc closes ONLY on an opposing dr | a same-dr sig_utc is INERT |
> | the dr-flip backstop CLOSES but never OPENS | the book goes flat instead |
> | the MAE cap is 0.70%, applied as a STOP | `MFE-MAE` prints `-0.70` when hit |
>
> Plus, same day: **the stop wins a same-bar tie with an opposing sig_utc**, and **order type is
> market**. `OPEN.md`'s **Ruled** table is the current statement. Everything in *The reference
> backtest, banked* below is the **PRE-RULING** shape — see `OPEN.md` item 8.

## The rules, Joe 0929-EARLY verbatim — SUPERSEDED, kept as the origin

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

**The walk is strictly causal.** `trade_walk.walk()` is a bar-by-bar loop carrying the trade's own dr
and a `left` flag, reading only `dr[k]` and `dr[k-1]`. At each bar: if `dr[k] == -D` set `left`; if
`left and dr[k] == D and dr[k] != dr[k-1]` this bar is the backstop; otherwise if the bar is an
ungated sig_utc, reverse. The flip is tested first, which is Joe's same-bar priority.

**~~A consequence, and it is the rule not a choice:~~ SUPERSEDED 0929-late.** It used to read: at a
backstop the dr is D again, so the trade the flip opens carries the same direction as the one it just
closed. Joe was shown exactly that and ruled it out: *"now we have the data I can see that dr-flip as
an open is not helpful"*. **The flip CLOSES and the book goes flat.**

`dr +1 = SHORT, dr -1 = LONG`. Joe 0925: *"+dr = SHORT position, -dr = LONG postition"*.

## The knobs — all in `wsf_trade_config`, **version 2, the only version**

**None of the three 0929-late rulings is a knob, and none is in the key.** `trade_config.key()` is
`wtc_v%d_%s_%s % (version, leash_instance, gate)`, so a pre-ruling and a post-ruling run land on the
**same key**. `mae_cap` is not a row in the table; 0.70 emerges at runtime in `sweep_mae_cap.py`.
See `OPEN.md` item 8.

| name | value | source |
|---|---|---|
| `leash_instance` | v7 | Joe 0929: *"v7"* |
| `gate` | `rule1_gate.open` — the rule#1 leg OR the scenario leg | Joe 0929: *"using the gate that you validated in our shared sheet, col L"* |
| `same_bar_priority` | dr-flip | Joe 0929: *"same bar priority: dr-flip"* |
| `rule1_back_min` | **7.0 — minutes BACK, 84 bars** | Joe 0929: *"inside of the last {knob:7} minutes"* |
| `rule1_fwd_min` | **0 — causal** | Joe 0929: *"let's drop the forward"* |
| `rule1_run_clamp` | **window — a run stops at the window edge** | Joe 0929 |
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

## The reference backtest, banked — **PRE-RULING. DO NOT USE AS A TARGET.**

**Every figure in this section reproduces exactly against `wsf_trades`, and `wsf_trades` is the
superseded shape.** Of the 120 banked rows: **43 of 67 sig_utc closes are same-dr** (now INERT) and
**52 opens are dr-flip opens** (now deleted). `trade_walk.walk` carries both rulings as of 0929-late,
so `build_wsf_trades.py` **no longer reproduces the numbers below**. They are the historical record.
See `OPEN.md` item 8.

`build_wsf_trades.py` → table `wsf_trades`, window `2026-09-01..2026-09-06`. Key `wtc_v2_v7_rule1_gateopen` —
**one config version only**. Joe 0929 dropped v1 and its 166 rows once he had the A/B.

| | |
|---|---|
| sig bars gated out of 109 | 41 |
| trades | **119 closed, 1 still open** — 120 banked rows |
| opened by / closed by | sig_utc 67, dr-flip 52 — the same split both ways |
| MFE > MAE | **68 of 119 = 57.1%** |
| MAE mean / median / max | 0.698 / 0.348 / 3.359 |
| MFE mean / median / max | 0.991 / 0.738 / 6.517 |
| SHORT (dr +1) | n 55, MAE mean 0.716, MFE mean 1.070, MFE > MAE 34 |
| LONG (dr −1) | n 64, MAE mean 0.683, MFE mean 0.923, MFE > MAE 34 |

**THE WALK ENDS AT THE WINDOW EDGE, 2026-09-06 00:00.** It used to end at the last bar of the tape,
two days past the label the rows carry. That added 25 trades: 24 opening after the edge, all dr +1,
all dr-flip-to-dr-flip with no signal left on the tape to close them, plus the trade opened by the
last v7 signal (09-05 21:28:05) which is now reported STILL OPEN instead of closed on the 09-06
00:17:15 flip. Anything quoting **144 trades / MFE > MAE 83 / MAE 0.783 / MFE 1.111** is the old
end-of-tape number: 119 + those 25 reconciles it exactly.

09-01 alone: **25 closed, 18 opened by sig_utc and 7 by dr-flip, MFE > MAE 13 of 25.**

### Two variants that were measured and rejected

| variant | what it was | why it went |
|---|---|---|
| the old gate window, `[k-42, k+42]` | 142 trades, MFE > MAE 76 of 142 = 53.5% — measured end-of-tape, before the window fix | **not causal** — read 210 s of future. Joe 0929 dropped the forward half. v2 also scores better on all four headline measures, but that was a bonus, not the reason |
| a 3-minute forward WAIT on a rejected sig bar | 151 trades, MFE > MAE 84 of 151 = 55.6% — measured end-of-tape, before the window fix | causal, and it recovered all 7 sig_utc opens the old window was catching — but 5 of the 7 additions lose, and 5 have MFE under 0.4%, inside the 0.1975% round-trip banked at 22,000 coins. Joe 0929: *"no V3, just v2"* |

Do not rebuild either without Joe asking.

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
See `MVP2.md` for the full MVP1/MVP2 line, including the exchange-resident stop backstop and limit
order placement.

## The timestamp gap is the point

Joe 0929: *"this is exactly what we're reconcilling. o9-live has no choice - it must use wall-clock"*.
The backtest is bar-indexed on the 5 s grid; o9-live stamps wall-clock. Mapping one to the other **is**
the test, not a nuisance to be papered over.
