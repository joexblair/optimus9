# 1002 — octo-freedom's live producer, shape B: built, and being proven against 09-01

Joe's rulings this build implements, all 1001–1002:

| ruling | Joe | where it lives in code |
|---|---|---|
| shape B: carry the walk / arm / trade book; rebuild lines each bar | *"B"* | `optimus9/live/octo_freedom.py` |
| the window: 104 h = 24 h lookback + 80 h warmup | *"#3 window is approved"* | `octo_freedom.LOOKBACK_H, WARMUP_H` |
| the open label | `octo-sig` | `octo_freedom.LABEL` → `TradeBook(label=)` |
| the trade book reads the walk's dr, `rig.DR` | *"it's the dr in this report"* | `Inputs.DR` → `TradeBook.step(d_k, d_prev)` |
| a trade opens on the arm's dr | *"I think we do the same for dr"* | `TradeBook.step(signal_dr=arm_dr)` |
| a same-dr octo-sig while a trade is open | *"for this first MVP, no pyramid trades. note the signal for recon and keep walking"* | `TradeBook.step` returns `('inert', k, dr)` |
| startup | *"stay flat ... walking the bars until a octo-sig prints. that's when the first trade will opened"* | `OctoFreedom.advance`: the walk is rebuilt over the first window; `TradeBook` is created at the first live bar |
| the recon's backtest trade list starts 24 h before o9-live's start bar | *"24 hours before"* | not in this build; the recon job's |

## What changed in existing code

| file | change | proof it moves nothing that already exists |
|---|---|---|
| `optimus9/compute/trade_walk.py` | `TradeBook`: the rules as a stepper; `walk()` drives it. Optional `label`, `open_dr`, `noted`; defaults are the pre-1002 behaviour. The `px` docstring's "event tape" corrected to the full 5 s base | `1002_live_producer/regress_trade_walk.py`: the committed `walk` (git `08190c7`) vs the new one, 5,000 random cases, 28,731 trades, closers sig_utc 8,563 / dr-flip 3,284 / stop 16,884, **0 mismatches**. `tests/test_trade_walk.py` T1–T5 pass |
| `optimus9/compute/leash_walk.py` | the per-bar dr routing moved from inside `walk()` into `step_bar()`, which both `walk()` and the live producer call | `report_leash_walk.py` re-run: **M\|PASS**, 2768 / 1673 / 1095 / 23, 9 of 9 validated bars. `tests/test_leash_walk.py`: 7 OK |
| `docs/octo-freedom/1001_recon_validation/muts.py` | mutation L24 repointed to the moved line | all 37 mutation strings and 3 probes re-checked against the current source |

## What is new

| file | job |
|---|---|
| `optimus9/live/octo_inputs.py` | `OctoConfig` reads every knob once, from the same sources the backtest reads. `Inputs` builds, from one live `BiasWindow`, the arrays `Rig` and `report_leash_walk` build from the cache: arm Mage, `DR`, `DRW`, combined coil, r ladder, seam masks, rev masks, rule#1's seven lines, `px`. `gate_open` is `Rig.gate_open` on those arrays. `line_overrides` builds the 12 lines that are not in `vw_indicator_configs_live` with the cache's own recipe |
| `optimus9/live/octo_freedom.py` | `OctoFreedom`: the carried `LeashWalk` and `TradeBook`; `window(end_ms)` builds the 104 h window; `advance(inp, live_from_ts)` steps every new bar → one record per bar: walk passed / rule#1 passed / WALK FIRES FROM / arm bar and dr / the trade book's events. The bar number fed to the steppers is `ts // 5000`, so a hole in the tape raises instead of being stepped over |
| `tests/test_trade_walk.py` | T1 `walk()` = a hand-driven `TradeBook`; T2 `open_dr` sets the side; T3 a same-dr signal is noted and inert; T4 the label names the opener and an opposing close, default unchanged; T5 refuses a skipped bar |
| `1002_live_producer/regress_trade_walk.py` | the regression above |
| `1002_live_producer/replay_0901.py` | the proof: 09-01 decided bar by bar on the live path, a fresh 104 h `BiasWindow` from DB klines at every bar, the window's last bar ASSERTED to be the bar being decided. The whole day is asserted against the acceptance test's numbers |

## The o9-live side, built 1002

| file | job | proof |
|---|---|---|
| `optimus9/live/octo_loop.py` | the decide layer `O9LiveApp` calls: `window(now_ms)`, `intents(W, positions, legs)`, and the health hooks the portal reads. Maps the book's events to orders: dr +1 = Sell, dr -1 = Buy; a reversal closes then opens; a same-dr octo-sig places nothing and is dumped as `non-trading octo-sig`; a feed gap under 5 min places its opens late, 5 min or more places none (dumped as `non-trading octo-sig`), closes are placed whatever the gap; a position on the exchange at startup stops it | `tests/test_octo_loop.py` L1-L6 pass |
| `optimus9/live/trade_signal_dump.py` | the trade-signal dump: the five ruled fields, one JSON line per action, `o9live_trade_signal_dump.log`. Reasons: `octo-sig`, `dr-flip`, `stop`, `non-trading octo-sig` (Joe 1002: *"technically it's an open without a close"*) | L6: every line carries the five fields only |
| `optimus9/live/feed_errors.py` | the MVP1 errors log, `o9live_errors.log`: every non-`live`/`match` `kline_audit` verdict for FARTCOINUSDT, `klinecollect.service` WARNING/ERROR/CRITICAL and backfill lines, ERROR/Traceback lines from `fakeapi.log` and `o9live_octo.log`. Copies; changes none of the services. `wait --since N` is the shell monitor | scratch test: an INFO line ignored, an ERROR line captured. RUNNING since 2026-10-02 01:34 UTC, PID 1577934; this session monitors it |
| `ops/run_o9live.py` | `O9_PRODUCER=octo` builds `OctoLoop` (104 h window) instead of `StrategyLoop`. The default is unchanged (`ad`) | compiles |

Joe 1002 parked to MVP2: bars the bar builder rewrites after the walk used them, the blip-triggered
reset, and the 1-minute octo-sig dwell. MVP1 records tick and kline issues in the errors log and acts
on none of them.

**WHAT THE LAST TEST LEFT ON THE FAKE EXCHANGE, read 1002:**

| table | state |
|---|---|
| `o9_live.fx_position` | 268 rows; **1 open: id 268, Buy 66,000, opened 2026-07-21 ~10:35 UTC** |
| `o9_live.o9_ledger` | 988 rows; **1 open: led_id 988, Buy 66,000, entry_px 0.13995940, reason `entry`** (v2) |
| `o9_live.o9_control` | mode `fixed`, max_order 66,000, split 1, halted 0, flatten_req 0 |

`OctoLoop` will not start on that open position. Clearing it, and what happens to the 988 ledger rows
(`OPEN.md` item 4), are Joe's.

## The 09-01 replay

| run | bars | result |
|---|---|---|
| slice 00:20:00 → 00:35:00 | 181 | WALK FIRES FROM **00:27:35, arm 00:19:20, dr +1** — the acceptance test's run 1, exactly. 46 bars passed the walk and rule#1 = run 1's 46 bars. Trade book opened `octo-sig` at 00:27:35, dr +1. Startup bar 37.4 s (window + 104 h walk rebuild); then ~1.6 s per bar. 5 min 16 s wall |
| the whole day, 00:00:00 → 23:59:55 | 17,280 | **PASS** (`M|PASS`, ended 2026-10-02 09:30 UTC). MECH 2768 / cut 1673 / EMITTED 1095 / runs 23, equal to the acceptance test. The 23 WALK FIRES FROM bars, each with its arm bar and dr, equal the acceptance test's list. The 9 validated bars are among them. Trade book: 17 closed, 5 same-dr signals noted, 1 open at the day's end. 30,787 s wall = 1.78 s per bar. Log `1002_live_producer/replay_0901.full.log`, rows `replay_0901.000000-235955.jsonl` |

```
cd /home/joe/thecodes/docs/octo-freedom/1002_live_producer
python3 regress_trade_walk.py                    # 0 mismatches vs git 08190c7
python3 replay_0901.py --from 00:20:00 --to 00:35:00
setsid nohup python3 replay_0901.py > replay_0901.full.log 2>&1 &     # the whole day
cd /home/joe/thecodes && python3 tests/test_trade_walk.py && python3 report_leash_walk.py
```

## Facts found while building

| fact | where |
|---|---|
| a signal on a bar where the dr is still 0 opens a dr-0 trade that nothing closes; every later signal is then inert. Pre-1002 behaviour too. octo-freedom cannot reach it: the arm cannot set on dr 0 (`arm_state.py:83`) and every octo-sig opens on the arm's dr | `trade_walk.py`, the open branch |
| the bar builder prints a 5 s bar at seam + 500 ms and REWRITES the last 3 bars every cycle to absorb late ticks. o9-live reads at seam + 700 ms. A bar the walk has stepped can change up to ~15 s later | `bar_builder.py:49-50, 73-112`; `run_o9live.py:45` |
| the driver hands o9-live only the NEWEST bar each cycle. After a feed gap, `advance` steps every missed bar, and their trade events surface at once, after their bar | `driver.py:27-44`; `octo_freedom.advance` |
| `StrategyLoop.intents` is a two-book, pyramiding model with v2's exits; octo-freedom needs its own decide layer, not a `_PRODUCERS` entry | `strategy.py:69-109` |

## The four held questions — ANSWERED 1002

| # | question | Joe 1002 | where it lives |
|---|---|---|---|
| 1 | where a noted same-dr octo-sig is written | *"technically it's an open without a close. can you notate (in the log) in a way that steers you towards reconcilling the non-trading octo-sig?"* | an `open` dump line, reason `non-trading octo-sig` - `trade_signal_dump.py`, `octo_loop.py` |
| 2 | which blips fire the reset | PARKED to MVP2 with the reset itself; *"yes, create an errors log for fakeAPI and shell monitor the log"* | `feed_errors.py` → `o9live_errors.log`; `MVP2.md` item 6 |
| 3 | bars rewritten after the walk used them | *"let's park the rewritten bars until MVP2"* | `MVP2.md` item 6 |
| 4 | an event on a bar the driver skipped | *"if the gap is less than 5 minutes, yes - place the trade"*, applied to the whole gap, for opens; *"if a close event fires in the gap, it needs to fire as soon as the event is known (after the gap)"* | `octo_loop.LATE_OPEN_MS`; `tests/test_octo_loop.py` L4 |

## Not measured

| not measured | why it matters |
|---|---|
| trades on the live path vs the backtest's, 09-01 | the replay records them; the backtest side (trade_walk on `Rig` arrays, `octo-sig`, arm dr, `rig.DR`) is not run yet |
| the producer inside o9-live's app loop | the decide layer that turns records into orders is not built; it waits on held items 1 and 4 |
| a v7 real-data regression of `trade_walk` | the random-case regression covers the code paths; the 90-day v7 run (894 / +0.3911) was not re-run |

## STARTED 1002 ~01:41 UTC — Joe: *"flatten it, fresh ledger, start it now"*

| step | command / result |
|---|---|
| fakeAPI | `O9_LIVE_BOOK=FARTCOINUSDT PK_DB_NAME=o9_live python3 -m uvicorn services.fakeapi.app:app --host 127.0.0.1 --port 8098 >> fakeapi.log` |
| portal UI | `python3 -m uvicorn optimus9.live.ui_server:app --host 0.0.0.0 --port 8099 >> ui_server.log` |
| flatten | the July Buy 66,000 closed through `BybitAdapter.place(Order('Sell', 66000, reduce_only=True))` @ **0.17566347**, order `fx-3cb716acd0fd43a8a28f6c98b4bf1618`; ledger leg 988 closed by `record_close_side`, decision logged `operator_flatten 1002` |
| archive, before the reset | `o9_ledger` 988, `o9_decision` 201,283, `o9_forecast` 0, `fx_fill` 1,601, `fx_order` 1,601, `fx_position` 268, `o9_account` 1 → each copied to `<table>_archive_1002`; every count matches |
| fresh ledger | `POST :8099/api/reset` (the existing reset): `o9_ledger` / `o9_decision` / `o9_forecast` / `fx_*` at 0 rows, equity $500, halted |
| o9-live | `O9_PRODUCER=octo python3 -u ops/run_o9live.py >> o9live_octo.log`, then `POST :8099/api/resume`. `-u` because the driver's per-bar lines are unflushed `print`s; the first start without it was stopped by PID before any bar decided |
| first bars | startup bar `decide=47599ms` (104 h walk rebuild); then 1,668–2,041 ms per bar; the bars missed during startup were stepped by `advance` |
| monitors | `o9live_errors.log` (watcher PID 1577934) and `o9live_trade_signal_dump.log`, both watched by the o9-live session |

The portal's top-right mech-state table reads the v2 cascade grid; `OctoLoop.state_mask` returns an
empty grid, so that table shows nothing for octo-freedom (Joe 1002 expected this).

## THE RECON JOB, built 1002 — Joe: *"yes thanks"*

`optimus9/live/octo_recon.py`; monitor `python3 -m optimus9.live.octo_recon --watch` (detached, one job
per new dump line); results `o9live_recon.log` and `o9_live.octo_recon_run` / `_verdict` / `_mismatch`.

| part | what it compares |
|---|---|
| reference | the octo-freedom chain (`OctoFreedom`, the live producer's own code) over ONE window: trade book from 24 h before o9-live's first live bar (Joe 1002), 104 h warmup behind that, to the newest closed bar. Lines from the DB tape at recon time, the cache's recipe |
| A. signals | every reference WALK FIRES FROM bar vs every bar with a live `open` dump line |
| B. actions | the live dump vs the book o9-live SHOULD have run: empty at its first live bar (stay flat), the reference's signals, the same rules |
| C. pre-start | Joe's 24-h-earlier list vs that live-start book; differences are the stay-flat ruling at work, labelled |
| causality | each job's verdicts vs the previous job's on the same bars; a moved verdict is written, flagged when it sits within 3 bars of the previous job's end (a bar rewrite is possible there) |
| cache | NOT MEASURED: o9-live does not record the values it decided on |

**First run, 2026-10-02 02:20 UTC:** live start 01:42:35, book start 10-01 01:42:35, tape 92,613 bars,
75 s. Signals 0 mismatches. Actions 3 matched (open Buy 01:45:05; close Buy + open Sell 02:11:35),
0 mismatched. Pre-start 1: at 01:45:05 Joe's 24-h-earlier list was already holding a dr -1 trade, so
the octo-sig there was same-dr and opened nothing; the live book, empty at start, opened it.

`tests/test_octo_recon.py` R1-R3 hold the expectation rules.

**RAISED TO JOE:** `OPEN.md` / `RECON.md` rule the line cache as the recon's source (Joe 0929). The
cache ends 09-30; the job recomputes from the DB tape at recon time instead. Whether that meets the
ruling is his.
