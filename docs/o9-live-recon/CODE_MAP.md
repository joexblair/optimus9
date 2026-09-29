# What exists, what is new, and what is NOT built

## The headline

**o9-live and fakeAPI exist and run. They run a DIFFERENT strategy.**

`ops/run_o9live.py` wires `RealtimeDriver → O9LiveApp → BybitAdapter → fakeAPI` and its
`StrategyLoop` is constructed with `producer=v2_walk_ad` — the `bias_machine` / `lr_v2` /
`greenfield_cascade` chain. There is no wsf_leash, no rule#1 gate and no dr-flip backstop anywhere in
that path. Anyone reading `run_o9live.py` and assuming it already trades this strategy will be wrong.

## Built and banked this session — the reference side

| file | what it is |
|---|---|
| `optimus9/compute/dr_latch.py` | `latch` (no wob, the wsf_dtf_v3 producer) and `latch_wob` (Joe's 8). Lifted out of the parked `docs/mage_cascade/stopsweep.py` |
| `optimus9/compute/trade_walk.py` | the rules, pure — `walk()` and `mae_mfe()`. `backstop()` is **deleted**, do not expect it. No DB, no lines, no printing |
| `optimus9/compute/trade_config.py` | `wsf_trade_config`, **16 knobs at version 2 — the only version**. Each row carries Joe's own words as its source |
| `build_wsf_trades.py` | the only banker - loads the tape and lines, runs the gate, walks, writes `wsf_trades`. **It has NO STOP in it, so it does not produce this mech.** `--day`, `--drop`, `--md` |
| `optimus9/compute/rule1_gate.py` | the gate. Pre-existing, unchanged |
| **`sweep_mae_cap.py`** | **THE ONLY THING THAT PRODUCES THIS MECH.** 753 trades over 90 days, peak cap 0.70 at +0.3776/trade. Carries both 0929-late close rulings and the cap. **Zero DB writes - it prints, it does not bank** |
| `fastverdict.py` | vectorised `sideways`, proven 0 mismatches against `momo_g_why` over 8 TFs x 86,400 bars |
| `report_realtime_replay.py` | replays the sig_utc chain in realtime and reports revisions + latency. 0929: 121 of 121, zero revisions |

**Other scripts in the repo measure mechs WITHOUT the cap.** `sweep_v3_signal.py`,
`bank_emit_entry.py` and everything under `docs/sweeps/` are not this mech. They are not part of
this handover and their numbers do not belong in a report about it.

Reproducibility, and run these before trusting anything:

```
python3 sweep_mae_cap.py            # 753 trades over 90 days, peak cap 0.70 at +0.3776/trade
python3 report_realtime_replay.py   # the causality proof: 121 of 121, zero revisions
```

**Nothing in this repo banks this mech.** `sweep_mae_cap.py` produces it and prints it;
`build_wsf_trades.py` banks, and what it banks has no stop. Every row already in `wsf_trades` was
written before the cap and before the two close rules. **Do not run `build_wsf_trades.py` expecting
this mech, and do not compare o9-live against `wsf_trades`.** Building the banker for this mech is
the first thing the recon needs - see `OPEN.md`.

## Existing live infrastructure — read before building

| file | what it is |
|---|---|
| `ops/run_o9live.py` | the realtime entry point. Wires driver, app, adapter, fakeAPI. Its own line 28 labels the producer it runs *"'ad'=v2_walk_ad (look-ahead arm-delay)"* |
| `ops/e2e_o9live.py` | end-to-end: app → adapter → real HTTP → running fakeAPI → book-walk fill → `fx_position` |
| `ops/provision_o9live.py` | provisioning |
| `optimus9/live/strategy.py` | `StrategyLoop`. **Pluggable via `producer=`** |
| `optimus9/live/app.py`, `control.py`, `ledger.py`, `health.py`, `state_log.py` | the o9-live runtime |
| `optimus9/live/exchange.py` | `HmacSigner`, `BybitV5Client`, `BybitAdapter` |
| `optimus9/live/sizing.py` | `PositionSizer`, `TradeIntent` |
| `live/fake_api.py` | the Flask fake Bybit V5, default `127.0.0.1:8788` |
| `services/fakeapi/app.py` | the uvicorn fakeAPI `run_o9live.py` expects, with `O9_LIVE_BOOK=<symbol>`, `PK_DB_NAME=o9_live` |
| `tests/test_fakeapi_fill.py` | the fill-model test |
| `live_vs_backtest_trades.py` | **the precedent for this exact job**, written for the old strategy. Matches o9-live trades to backtest by entry time ±tol plus side |
| `recon_arm_events.py` | another recon precedent |

Logs sit at the repo root: `o9live_run.log`, `o9live_arm.log`, `o9live_ad.log`, `o9live.log`,
`fakeapi.log`.

`o9_live.o9_ledger` holds **988 rows from the old strategy**. Columns: `led_id, symbol, side, qty,
entry_px, exit_px, entry_order_id, exit_order_id, gross, net, fee, mae, reason, status, opened_ms,
closed_ms`. A recon must not treat those 988 as this strategy's trades.

## Causality

`CAUSALITY.md` carries the full audit — every module from `build_wsf_dtf_v3` down to `wsf_trades`,
plus the hand-walk. Two things from it that belong here:

- **`trade_walk.backstop()` is deleted.** It computed a trade's closing bar at open time from the
  stretch list — a future bar. `walk()` is a bar-by-bar loop now. Do not reintroduce the old shape.
- **`wsf_dtf_v3.wdv_run_bars` is forward-looking and has no consumer.** Anything that starts reading
  it inherits lookahead silently.

## The architecture that keeps it causal — already written down

`StrategyLoop`'s own docstring:

> "Stateless by design: each closed 5s bar, run the SAME backtest producer on a bounded window ending
> at now, and read ONLY the latest bar. Window-ending-at-now == the backtest window → live == backtest
> by construction; no latch state to desync, self-healing every bar."

The new producer must follow that shape. It is the single strongest defence against the lookahead
Joe wants exposed, and it already exists as a pattern in this codebase.

**THE SIGN CONVENTIONS ARE INVERTED.** `optimus9/live/strategy.py:5-6` says *"bd +1 = Buy/long,
bd -1 = Sell/short"*. This strategy is **`dr +1 = SHORT, dr -1 = LONG`**. A producer written for
`StrategyLoop` must flip the sign, and nothing in the live code says so.

## NOT built — the five things

1. **A wsf_leash producer for `StrategyLoop`.** A callable with the same contract as `v2_walk_ad`
   that, over a bounded window ending at now, returns this strategy's action for the latest bar.
   It has to reach `wsf_leash` signals, `rule1_gate`, `dr_latch.latch_wob` and `trade_walk`.
2. **The sig_utc producer chain running forward.** Joe 0929 named the chain:
   `build_wsf_dtf_v3` → `report_coil_exit` → `coil_exit.resolve` → `leash_bank`. The question is
   whether steps 1 and 2 run forward on a bounded window ending at now. §20.2's latency sits in
   step 2 — median 300 s, max 5000 s — and Joe 0929 ruled it acceptable for now: *"latency is ok
   for now. eventually we'll cherry-pick what we need from the classes and optimise"*.
3. **The trade-signal dump.** Joe 0929: *"I would build a o9-live trade-signal dump to log and consume
   via a shell monitor"*. Nothing writes one today.
4. **The shell monitor** that wakes a Claude session on each trade action.
5. **The recon job itself** — `RECON.md` has the procedure.

## Suggested order

1, then 3 and 4 together (they are small and they unblock every later loop), then 5, then 2 last
because it is the one that needs Joe.
