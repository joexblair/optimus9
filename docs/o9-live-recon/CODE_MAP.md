# What exists, what is new, and what is NOT built

> **1001 — THE MACHINE CHANGED. READ `README.md`'s MACHINE SECTION BEFORE THIS FILE.**
> The signal is `WALK FIRES FROM`, from `optimus9/compute/leash_walk.py` + `arm_state.py`, knobs in
> `wsf_trade_config` **v4**, acceptance test `report_leash_walk.py`. Joe 1001: *"it is the only
> outcome that is stamped as ready for live trading"*.
>
> **THIS FILE WAS WRITTEN FOR THE v7 `wsl_sig_utc` CHAIN AND HAS NOT BEEN REWRITTEN.** Everything in
> it about the v7 producer, its five build steps, its numbers and its entry bar is the HISTORICAL
> RECORD. Where it tells you to build something, check it against the machine section first.
>
> **1002 — `octo-freedom`'s live producer is BUILT AND RUNNING:** `docs/octo-freedom/1002_live_producer.md`.
> The five-things list below carries its status.


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
| `optimus9/compute/trade_config.py` | `wsf_trade_config`, **18 knobs at version 3**. v2's 16 plus `mae_cap` 0.70 and `stop_same_bar_priority`. v2's rows stay as the uncapped mech's knob set. Each row carries Joe's own words |
| `build_wsf_trades.py` | the banker. Loads the tape and lines, runs the gate, walks with the stop live, writes `wsf_trades`. **It reads its signal bars FROM `wsf_leash`**, so until the 121 rows are re-banked at `sig_conf` it is on bars 15 s early, and it cannot cover more than 09-01..09-06. `--day`, `--drop`, `--md` |
| `optimus9/compute/rule1_gate.py` | the gate. Pre-existing, unchanged |
| **`sweep_live_stop.py`** | the cap ladder, all 80 rungs re-walked from the tape with the stop live. The 0.70 rung is 894 trades / +0.3911 per trade. Prints, does not bank |
| `measure_live_stop.py` | what the stop being live changes: the freed windows, the signals inside them, and the same-bar collision counts |
| `sweep_mae_cap.py` | the FIRST cap ladder - the cap applied in scoring over one fixed trade set of 753. **Superseded by `sweep_live_stop.py`.** Kept because it is where the 0.70 ruling was first made |
| `fastverdict.py` | vectorised `sideways`, proven 0 mismatches against `momo_g_why` over 8 TFs x 86,400 bars |
| `report_realtime_replay.py` | replays the sig_utc chain in realtime and reports revisions + latency. 0929: 121 of 121, zero revisions |

**Other scripts in the repo measure mechs WITHOUT the cap.** `sweep_v3_signal.py`,
`bank_emit_entry.py` and everything under `docs/sweeps/` are not this mech. They are not part of
this handover and their numbers do not belong in a report about it.

Reproducibility, and run these before trusting anything:

```
python3 sweep_live_stop.py          # the cap ladder, 81 rungs. The 0.70 rung is 894 / +0.3911
python3 report_realtime_replay.py   # the causality proof: 121 of 121, zero revisions
```

**`build_wsf_trades.py` banks under its own key**, so it cannot collide with the 332 uncapped rows
already in `wsf_trades`. Those rows were written before the stop and before the two close rules;
they are history and o9-live must not be compared against them.

**But it is not yet producing this mech.** It takes its signal bars from `wsf_leash`, and that bank
holds the pre-`sig_conf` cross bars. The re-bank is ruled and not done.

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

`o9_live.o9_ledger` held **988 rows from the old strategy** until the 1002 fresh ledger; they are in
`o9_ledger_archive_1002`. Columns: `led_id, symbol, side, qty,
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

**THAT QUOTED CLAIM IS FALSE FOR `latch_wob`, AND `latch_wob` IS THE v7 `trade_walk`'s dr. Flagged 1001.**
(CORRECTED 1002: `octo-freedom`'s walk and trade book read `rig.DR`, the 85/15 no-wob latch; its rule#1
reads `latch_wob`. Both are path-dependent from their start bar. Under shape B the producer carries
them; the 104 h window covers the longest measured reset gap, `docs/octo-freedom/1001_warmup.md`.)
`dr_latch.latch_wob` is PATH-DEPENDENT from its `i0`: `cur`, `up` and `dn` start at 0 and only move
when a run reaches `wob` 8 bars = 40 s, so `dr[k]` is a function of all history since `i0`. The
backtest calls it over the whole 94.5-day tape (`sweep_v3_signal.py:106-109`). Live,
`StrategyLoop.window()` builds a `BiasWindow(lookback=24, warmup=80)` = a **104-hour** tape
(`strategy.py:23, 39`). Whenever the most recent latching run predates the live window's start, the
two sides carry a different `dr` with **both sides causal** — and the recon would class it as
`selection`. `strategy.py:28`'s own comment already says *"bounded window; must reproduce the
backtest line values (pin by measure)"*. It has not been measured for this strategy. **Measure it
before the first recon job.**

The new producer must follow that shape. It is the single strongest defence against the lookahead
Joe wants exposed, and it already exists as a pattern in this codebase.

**THE SIGN CONVENTIONS ARE INVERTED.** `optimus9/live/strategy.py:5-6` says *"bd +1 = Buy/long,
bd -1 = Sell/short"*. This strategy is **`dr +1 = SHORT, dr -1 = LONG`**. A producer written for
`StrategyLoop` must flip the sign, and nothing in the live code says so.

## The five things — status 1002

| # | thing | 1002 |
|---|---|---|
| 1 | the producer | **BUILT, as its own decide layer**, not a `StrategyLoop` producer: `optimus9/live/octo_loop.py` + `octo_freedom.py` + `octo_inputs.py`; `O9_PRODUCER=octo` in `ops/run_o9live.py`. Running since 1002 ~01:41 UTC |
| 2 | the v7 sig_utc chain running forward | **NOT NEEDED** - the v7 chain is not the machine (`README.md`) |
| 3 | the trade-signal dump | **BUILT** - `optimus9/live/trade_signal_dump.py`, `o9live_trade_signal_dump.log` |
| 4 | the shell monitor | **BUILT** - `octo_recon --watch` runs a job per dump line; a session watches `o9live_recon.log` and `o9live_errors.log` |
| 5 | the recon job | **BUILT** - `optimus9/live/octo_recon.py`; first run 1002 02:20 UTC: 0 mismatches, 3 actions matched |

The v7 list as it was written, for the record:


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

~~1, then 3 and 4 together, then 5, then 2 last~~ - 1 and 3 are built, 2 is not needed; see the
status table above.
