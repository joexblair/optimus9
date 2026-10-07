# What Joe has ruled, what he has not, and the traps

## Ruled — do not re-ask

| | |
|---|---|
| instance | v7 |
| gate | the banked `rule1_gate.gate()['open']` — his sheet col L `code #1 gate`, 72 open / 49 closed |
| same-bar priority, dr-flip vs sig_utc | **the dr-flip wins** |
| **same-bar priority, stop vs opposing sig_utc** | **the STOP wins.** Joe 0929-late, asked directly: *"use stop"*. Flagged to him before the first recon job, and now closed |
| **order type** | **market**, both legs. Joe 0929-late: *"order type: market. MVP2 will develop the placement of limit orders"* |
| **the stop is client-side for MVP1** | Joe 0929-late, on a disconnect leaving the position naked: *"yes. that's MVP2 - we'll apply a larger stop with the exchange as a backstop"*. See `MVP2.md` |
| price recon | out of scope, MVP2 |
| lookahead test | re-run from the tape, not a diff against stored verdicts |
| tape vs line at recon | the line-cache, deliberately, as a second test-point |
| dr producer | `latch_wob` at `LATCH_W` 8. He reversed his own "no wob" instinct on the numbers. **THE v7 CHAIN'S.** `octo-freedom`'s walk and its trade book read `rig.DR`, oob 85/15 no wob (see *the trade book reads `rig.DR`* below); its rule#1 reads `latch_wob` |
| the backstop | the flip **back to** the trade's own dr, two flips forward |
| scratchpad | moved into the codebase, knobs in the DB. Done |
| ~~P&L~~ **REOPENED 1001** | Joe, asked whether "real pnl results" for o9-live extended to backtest reporting: *"both. the machine is now developed enough (ie we can make full loops of our mechs) to accurately interpret our results through the reality lens of P&L"*. `octo-freedom` closes the circuit - signal, gate, three exits, stop - so a P&L number prices a complete mech. **PERCENTAGE P&L per trade is reportable now; ABSOLUTE P&L needs a position size and `MVP2.md` item 4 says none is set.** Already-banked P&L (`docs/sneaky_trade_1_handover.md`, spec 17.3, the `sneaky_trade_1` table) is a completed record - do not restate it as current | ~~closed since 0917. MAE/MFE only~~ |
| **a sig_utc closes ONLY on an opposing dr** | Joe 0929-late, after spotting 09-01 03:40:05 (a SHORT) being closed by the 04:26:00 sig_utc (also a SHORT): *"trades must be first closed by an opposing dr signal, and secondly by a dr-flip if there is not opposing dr signal"*. A same-dr sig_utc is INERT - *"for now, it's inert"* |
| **the dr-flip backstop CLOSES but never OPENS** | Joe 0929-late: *"now we have the data I can see that dr-flip as an open is not helpful. the cost is accceptable - it gives us space to apply other mechs (lazy-g for example)"*. It still closes, or a trade would run to the next opposing signal whatever happened |
| **the MAE cap is 0.70%, and the stop is IN THE WALK** | Joe specified 0.9 on 0929, ruled 0.70 on the first ladder, then re-ruled it on the ladder re-walked with the stop live: *"retain 0.7% as the stop"*. `MFE-MAE` prints `-0.70` on a stopped trade |
| **the stop RACES the other exits** | Joe 0929-late: *"research how a stop is applied in trading - you'll learn that it's both: (at its signal or flip bar) OR (at the stop bar)"*. Three live exits, first to fire wins |
| **the cap goes in the KEY *and* in `wsf_trade_config`** | Joe 0929-late: *"put the cap in the key"*, then *"move MAE_CAP to the DB"*. Config **v3**, row `mae_cap` = 0.70, key `wtc_v3_v7_rule1_gateopen_mae0.70`. There is no hard-coded cap left in the code. **The v7 chain's key; `octo-freedom` loads v4, key `wtc_v4_v7_rule1_gateopen_mae0.70`, same `mae_cap` 0.70** |
| **only the MAE-capped mech is handed over** | Joe 0929-late: *"you should be handing over only the mech that the MAE cap was applied to"*. Anything measured without the cap - `docs/sweeps/`, every row in `wsf_trades`, every variant - is a **different mech**. It is not a baseline and not a comparison |
| **the 0929 knob sweep is out** | Joe 0929-late: *"ok, the sweep is definitely poisoned. let's go back to baseline"*. It ran before the cap and before the flip-open ruling. Do not use `docs/sweeps/` |
| the gate window | **backward-only. 7 min for the v7 chain; `octo-freedom`'s rule#1 is 5 min = 60 bars** (see *the walk's rule#1 lookback is 5.0 min*). Joe 0929: *"the -3.5 and + 3.5 logic is what's making it non-causal, so let's drop the forward"* |
| **`rule1_gate`'s WINDOW SHAPE is "v2"** | DISAMBIGUATED 1001 — this row used to read "the config \| v2 only" and collided with the `wsf_trade_config` **v3** row above it. They are two different things. "v2" here is `rule1_gate`'s backward-only window, which exists only as a docstring label (`rule1_gate.py:59`) — there is no code switch and no DB row for it. Joe 0929 dropped the v1 forward-window shape and its 166 banked rows after the A/B |
| ~~`wsf_trade_config` is v3, and ONLY v3~~ **SUPERSEDED 1001 — the machine is `octo-freedom`. See the machine section at the top of `README.md`.** The DB holds v2 (16 rows), v3 (18) and **v4 (36)**. `octo-freedom` loads v4; the v7 chain still loads v3. What stands: a bare `wtc_v2_...` key is the uncapped mech and is still forbidden. | the config object the code loads is `trade_config.load(db, TC.V)` with `V` = 3, 18 rows, key `wtc_v3_v7_rule1_gateopen_mae0.70`. A v2 config returns the bare `wtc_v2_v7_rule1_gateopen` — **the uncapped mech this package forbids**. If any doc says "config v2" without saying `rule1_gate`, it means the window shape, not this |
| a forward WAIT on a rejected sig bar | **rejected**. Joe 0929: *"no V3, just v2"*. It was causal and recovered all 7 lost opens, but 5 of 7 additions lose |
| the §20.2 latency | **accepted for now**. Joe 0929: *"latency is ok for now. eventually we'll cherry-pick what we need from the classes and optimise"* |
| ~~what the recon fires on~~ **SUPERSEDED 1001 by `THE MACHINE IS WALK FIRES FROM` above — the premise *"the new mech's bars can't be reproduced"* was falsified by the port** | ~~the banked v7 chain, unfiltered.~~ Joe 1001: *"so that we have more traffic to recon, the offline o9-live can fire on non-armed signals"*, then on being offered the alternative: *"it has to be the banked v7 chain - the new mech's bars can't be reproduced"*. The arm state of the mech in development is **not** a recon gate, and the recon's trade book stays comparable to the +0.3911 baseline |
| ~~rule#1's lookback for the recon~~ **SUPERSEDED 1001 — the machine is `octo-freedom`. See the machine section at the top of `README.md`.** `octo-freedom` reads **`walk_rule1_back_min` 5.0 min = 60 bars** from v4, and writing it did NOT void the bank — `TC.V` stays 3, v4 lands beside it. Still never OOS'd. | ~~`rule1_back_min` 7.0 from `wsf_trade_config` v3.~~ A 5-minute lookback was measured in mech-dev on 0930 (+0.4347 in-sample) but it is not in the config, not in `trade_config.key()`, and has never been OOS'd. Writing it to the DB would silently void the bank. The recon reads the config |
| **`confirm_lag_s` stays 180** | 165 was tested on 0930 and **loses both OOS windows**, −0.0058 and −0.0239 per trade. Rejected |
| **o9-live runs on LIVE TAPE, no caches** | Joe 1001: *"I'm expecting o9-live + fakeAPI to run on live tape - no caches"*. Verified: 0 references to `rpl_cache` or `.npz` in `optimus9/live/*.py` or `ops/run_o9live.py`. The line cache is a backtest device. It still matters for reproducing the backtest, which is what MVP1 matches against |
| ~~the REFERENCE o9-live adopts~~ **SUPERSEDED 1001 — the machine is `octo-freedom`. See the machine section at the top of `README.md`.** That row named the **v7 sig_utc chain**. `octo-freedom`'s reference is `optimus9/compute/leash_walk.py` + `arm_state.py` for the signal, `Rig.gate_open(k, 60)` for rule#1 — **NOT `gate_open(k)`, which resolves to 84 bars from v3** — and `trade_walk.walk()` for the exits. Acceptance test `report_leash_walk.py`. | ~~`measure_live_stop.build(rig)` for the chain, `Rig.gate_open(k)` for rule#1, `trade_walk.walk()` for the three exits, `measure_live_stop.score()` for MAE/MFE. **NOT `build_wsf_trades.py`** — that is a banker reading stale `wsf_leash` bars, pinned to 09-01..09-06. Joe 1001: *"'reference' = the code that o9-live will adopt"* |
| **MVP2 is out of the handover** | Joe 1001: *"keep MVP2 out of the handover - it's for our future dev, not for o9-live (yet)"*. `MVP2.md` is on disk but is not part of this package and its closing section is pre-0929 |
| **the fakeAPI/env defaults are whatever the last test left** | Joe 1001: *"use whatever is existing/leftover from the last o9-live + fakeAPI test. it's all immaterial - MVP1 for o9-live is ensuring the backtest signals matches the live signal"*. `ops/run_o9live.py:25-28` holds them: `O9_FAKEAPI_URL` **8098**, `O9_SYMBOL` **FARTCOINUSDT**, `O9_SIZE_MODE` **dynamic5x**, `O9_PRODUCER` **ad**. `CODE_MAP.md:56`'s 8788 is a DIFFERENT service (`live/fake_api.py`, the Flask one) — 8098 is the one `ops/e2e_o9live.py:21` uses. Size and symbol do not affect signal matching |
| **the walk's dr is the oob 15/85 NO-WOB latch, not `dr_latch`'s defaults** | Joe 1001: *"it needs to use whatever built my validated `WALK FIRES FROM` timestamps"*. That is the INLINE loop at `sweep_v3_signal.py:99-106` — ws1Mage + ws13m (hardcoded, NOT `latch_tf`) at **85/15**, no wob. `dr_latch.latch()`'s module defaults are **75/25** and give a different series. Banked as `walk_dr_*` in v4, and `report_leash_walk.py` REBUILDS it from those rows and asserts it: **0 of 1,632,960 bars differ**. rule#1 still reads `rig.DRW` — Mage 25/75, wob 8 — the documented v7 two-series split |
| **no extra non-armed signals** | Joe 1001: *"I'm dropping my request for extra non-armed signals"*. The walk emits only on an armed, dr-matched bar |
| **THE MACHINE IS NAMED `octo-freedom`** | Joe 1001: *"octo-freedom / it's now, it's the goal, and it's got a little bit of chinese numerology sneaked in the back pocket"*. Use the name in prose and docs. The module names and the config key `wtc_v4_v7_rule1_gateopen_mae0.70` still carry the old wording; renaming the KEY moves every banked row's key, so it waits on Joe |
| **THE MACHINE IS `WALK FIRES FROM`** | Joe 1001: *"there is no surviving mech that relies on `brk`"* and *"it is the only outcome that is stamped as ready for live trading"*. `optimus9/compute/leash_walk.py` + `arm_state.py`, knobs in `wsf_trade_config` **v4**, acceptance test `report_leash_walk.py`. The v7 `wsl_sig_utc` chain is the historical record |
| **`brk` IS OUT, WITH NO BACKSTOP** | Joe 1001: *"because we are in agreeance, and we are well aware that this is not a proven strategy, there is no need to hold on to `brk` as backstop"*. `release`, `moments`, `coil_exit`, `i1`, the four `actionable_*` and the four `via` branches are all out of the mech |
| **the walk's rule#1 lookback is 5.0 min** | Joe 1001, asked 5 or 7 for the config row: *"5"*. `walk_rule1_back_min` in v4. `rule1_back_min` stays 7.0 for the v7 chain. The 5-min value is load-bearing — it changes the gate on 4 of 17 sampled bars — and has **never been OOS d** |
| **`TC.V` STAYS 3** | bumping it to 4 would move `key()` for `sweep_v3_signal`, `measure_live_stop` and `build_wsf_trades`. Joe 1001 accepted this as stated. The walk loads `TC.WALK_V` explicitly |
| **MVP1's one job** | Joe 1001: *"MVP1 for o9-live is ensuring the backtest signals matches the live signal"*. Not edge, not size, not fills |
| **THE DRAG IS MEASURED LIVE AND ASSUMED IN THE BACKTEST. DO NOT COMPARE THE TWO NETS WITHOUT THIS ROW.** | Joe 1001: *"the good thing about o9-live is the drag becomes accurate - bybit's fees are set, slippage is measured by the orderbook's bps"*. The backtest's 0.1975% per trade is TWO different kinds of number and only one of them is real: |

| drag component | the BACKTEST | o9-live |
|---|---|---|
| taker fee | **2 x 5.50 bps = 11.0 bps**, a set rate (`docs/mage_cascade_findings.md:307`) | **the same set rate.** Identical, nothing to reconcile |
| slippage | **8.75 bps round trip** — ONE measurement, taken at 22,000 coins, applied FLAT to every trade regardless of size or book depth | **measured per fill from the orderbook, in bps, at the actual size** |
| total | 19.75 bps = **0.1975%** | fee + whatever the book gave, per trade |

**WHAT THAT MEANS WHEN P&L IS REPORTED ON BOTH SIDES.** A backtest net carries an assumed slippage;
an o9-live net carries a measured one. They are not the same quantity and a divergence between them
is not automatically a defect — it may be the book. **Report the two separately and say which drag
each carries.** The fee half is identical on both sides, so any drag divergence is slippage.

**THIS DOES NOT REOPEN SLIPPAGE MODELLING IN THE BACKTEST.** Joe 0929 ruled *"Do NOT model
slippage. Measure divergence FROM the spec"*, and `RECON.md` carries it. The two rulings are
consistent: do not invent a slippage model offline, DO read the real thing live. The backtest keeps
the flat 8.75 bps.

**AND IT IS NOT AN EXPLANATION.** A measured orderbook bps is evidence. Reaching for slippage to
explain a result nobody measured is the bias the P&L ban existed to stop — it locates failure
outside the mechanics instead of inside them.

| ruled 1001-1002, the live producer | |
|---|---|
| **signals become TRADE ACTIONS** | Joe 1001, asked whether MVP1's producer runs the three exits or emits signals only: *"yes - signals become trade actions, so that we see the o9-live mechs simulating real trading and real pnl results"*. **CONNECTED 1002:** `optimus9/live/octo_freedom.py` steps `trade_walk.TradeBook` bar by bar (`docs/octo-freedom/1002_live_producer.md`) |
| ~~the live walk re-walks a BOUNDED WINDOW every bar~~ **SUPERSEDED 1002 by shape B, the next row** | Joe 1001, on whether to carry state live instead: *"if it's dr related and one option has an inability to sync backtest to live, then we must take the other option (so that recon can be accurate)"*. MEASURED, and it makes the choice free: the longest unbroken dr stretch across the whole 94.5-day tape is **7.2 h** (5,175 bars) against **2,487** dr changes, median 0.7 h, p90 1.9 h, and **0 of 2,487** reach even 24 h. `StrategyLoop`'s 104-hour window therefore ALWAYS contains a dr change - 14x the longest stretch - so the bounded re-walk converges to the backtest's dr and keeps its self-healing property. Joe 1001: *"there will never be a 4 day stretch on an unbroken dr. prove me wrong"* - 0 of 2,487 reach 4 days |
| **shape B: carry the arm / walk / trade-book state from bar to bar; rebuild the lines every bar** | Joe 1002: *"B"*. Measured: a full 104 h rebuild ≈ 80 s per bar against a 5 s budget; the lines alone 1.27-1.45 s (`docs/octo-freedom/1001_rebuild_timing.md`). `optimus9/live/octo_freedom.py` |
| **the live window is 104 h** - 24 h lookback + 80 h warmup | Joe 1001: *"#3 window is approved"*. Minimum measured 72.47 h (`docs/octo-freedom/1001_warmup.md`). NOT `run_o9live.py`'s 8 + 6 h, which was sized for v2's lines |
| **the open label is `octo-sig`** | Joe 1001 (`docs/octo-freedom/1001_rewalk_on_ruled_dr.md`) |
| **the trade book reads `rig.DR`** - oob 85/15, no wob | Joe 1001: *"it's the dr in this report"* |
| **a trade opens on the ARM's dr** | Joe 1001: *"I think we do the same for dr"* |
| **a same-dr octo-sig while a trade is open: no pyramid** | Joe 1002: *"for this first MVP, no pyramid trades. note the signal for recon and keep walking"*. Dumped as `non-trading octo-sig` |
| **`non-trading octo-sig`** in the trade-signal dump | Joe 1002: *"technically it's an open without a close. can you notate (in the log) in a way that steers you towards reconcilling the non-trading octo-sig?"* An `open` line with that reason; no order, no close line follows |
| **startup: stay flat** | Joe 1002: *"stay flat. I'm assuming that you'll be walking the bars until a octo-sig prints. that's when the first trade will opened"*. The walk is rebuilt over the first window; the trade book starts empty at the first live bar |
| **a feed gap** | Joe 1002: opens inside a gap under 5 min are placed late, 5 min or more none - *"if the gap is less than 5 minutes, yes - place the trade"*, applied to the whole gap; closes fire as soon as known whatever the gap - *"if a close event fires in the gap, it needs to fire as soon as the event is known (after the gap)"* |
| **the recon's backtest trade list starts 24 h before o9-live's start bar** | Joe 1002: *"24 hours before"*, with *"the constant re-reviewing is to ensure that an established octo-sig doesn't move"* - the 24-hour re-validation, `RECON.md` |
| **PARKED TO MVP2: bars rewritten after the walk used them, the blip-triggered reset, the 1-minute octo-sig dwell** | Joe 1002: *"let's park the rewritten bars until MVP2. the critcal MVP1 task is recon - if we have tick or kline issues in that time, then we have real data to make decsions on"*; asked whether that covers the reset and the dwell: *"yes, create an errors log for fakeAPI and shell monitor the log"*. MVP1 RECORDS tick and kline issues in `o9live_errors.log` (`optimus9/live/feed_errors.py`) and acts on none. `MVP2.md` item 6 |
| **fresh ledger, 1002** | Joe 1002: *"flatten it, fresh ledger, start it now"*. The July Buy 66,000 was flattened, seven tables copied to `*_archive_1002`, then `/api/reset`. `docs/octo-freedom/1002_live_producer.md` |
| **fresh ledger, 1005** | Joe 1005: *"you're clear to full reset the usage data"*. 05:39:05 the Buy 66,000 (opened 04:37:25 @ 0.18180121) closed by the app's own `/api/flatten` @ 0.18312817, net +$74.33, which also halted the loop. Eight tables copied to `*_archive_1005`, every count matching: `o9_ledger` 62, `o9_decision` 54,593, `o9_forecast` 0, `fx_fill` 124, `fx_order` 124, `fx_position` 62, `o9_account` 1, `fx_fill_book` 82. Then `/api/reset` at 05:39:40 (equity $500, halted, fakeAPI `fx_*` cleared) and `fx_fill_book` truncated. Not archived: 3 `hold halted` decision rows, bars 05:39:25-05:39:35, written between the copy and the reset. Untouched: `o9_state_log`/`_line`, `octo_recon_*`, `diag_*`, `o9_control`. o9-live kept running (not restarted). Then Joe 1005 *"resume, and 888"*: `o9_account` equity set to $888, the start-equity default moved 500 -> 888 in `ui_server.py` and `ops/run_o9live.py`, the UI service restarted, trading resumed from bar 05:44:35 |
| **dynamic leverage, 1005** | Joe 1005: *"I don't know how to calculate - you can suggest a safe solution. our mate produced this table which looks healthy - can you code it so that the dynamic leverage is on point, every trade"*. Sizing mode `dynamic_leverage`: lev = (risk_pct / (n_live + 1)) / (stop_pct + drag_pct); coins = floor(min(max_order, lev x equity / price)). risk_pct **2.0** (my suggestion under Joe's delegation: the 2 %-risk convention, `1005_knobs.md` s3) and drag_pct **0.1975** live in `o9_control`; stop_pct is the book's own `mae_cap` (0.70) handed to the sizer at startup, so a stop ruling moves the leverage with it. Equity = `o9_account` (settled, closes only). Every open writes `o9_sizing` (inputs, lev_target, lev_applied, capped). o9-live restarted flat on the new code 06:04:56; mode switched 06:05. At $888 / 0.18291 = 2.228x, 10,818 coins. max_order 66,000 still binds above ~$5,400 equity. Not covered: a stop that FILLS past 0.70 risks more than 2 % (10-02 stop fills -0.94 / -0.93 / -1.68 %, chat #48) |
| **loop optimisation, 1005** | Joe 1005: *"hunt deeply for loop optimisations it's bobbing around 1800"*, then go via the resource chat (#55/#56). Four changes, each BIT-IDENTICAL: 244 arrays (the live window's base, px and every Inputs array) x 4 fixed bars 06:00-06:20 compared against the old code, 0 differ; 257 tests pass. (1) `BLDetect._setup(raw_pk_on=False)`: the raw pk BiasWindow discarded is no longer computed. (2) `KlineLoader.load_window(as_float=True)`: raw-cursor fetch, one float() per value, instead of dict rows of DECIMAL re-converted downstream. (3) `IC._ema` / `_rma`: the recursion on Python floats, same operations in the same order. (4) `IC._memo_resample`: LineReader shares one resample per timeframe across its lines. (1)+(2) are opt-in, on only in BiasWindow. Measured window+Inputs 1,476 -> 532 ms per bar; LIVE after the flat restart 06:54:13, decide 661-686 ms per bar (was ~1,500-2,150). Not done: fetching only new bars (it would miss bars the sanitiser or bar builder rewrite further back) |
| **Bybit 10006 at the top of the minute: accepted, 1007** | Joe 1007: *"you're the only caller to bybit. the first few seconds make sense, and as long as we can recover and backfill quickly there's really no issue"*. Measured 10-06/07: 243 `10006 Too many visits` replies to the kline auditor in 24 h, about 0.3 % of its ~86,400 public kline calls, most between second :05 and :20 of the minute; 217 of the 243 cleared on the first 1 s backoff. Bybit documents 600 requests per 5 s per IP (we run about 1/s) and 10018 or HTTP 403 for that limit, not 10006. Cost: 3 `1m incomplete` audit minutes in 3 days, tape complete each time. No change made |
| **tick sockets auto-restart, 1002** | Joe 1002: *"tick collect should auto restart on any tick freeze that dwells more than 60 seconds. there's 2 websockets in parallel so an offset is needed for the second"*. Then, asked: the second socket WRITES ticks (`stream.bytick.com`, his 0708 `docs/second_ws_spec.md`); offset *"10s is enough, but your call"* - 10 s, a shared gate; gap-fill after every reconnect YES; reconnect-wait reset (M1) NO; rebuilding the frozen bars NO; fakeAPI's book socket auto-restarts too. Earlier the same day: *"no auto reconnect yet"* - superseded by this row. `docs/octo-freedom/1002_outage_diagnostics.md` |
| **WAN reload, 1002** | Joe 1002: *"if the websocket reset makes no diff for another 50s, then restart the wan connection"*; *"SSH, one command"* (`pfSctl -c 'interface reload wan'`); *"Trades only, no limit. ... if the tick flow begins everytime the int is reset, then we have infra issues to troubleshoot"*. Do not add a limit. `docs/octo-freedom/1002_outage_diagnostics.md` |
| **restarts stay trades-only, 10-03** | Asked whether to restart a socket (and reload the WAN) only when Bybit also stops answering pings - the two quiet-market restarts of 10-03 21:53 / 22:41 had every ping answered. Joe 10-03: *"given there's no harm in restarting our websockets, and because there's always a possibility that a bybit host is up (the ping) but any other number of scenarios can break a stream, I'm inclined to leave it as-is"*. Do not gate restarts on pings. `docs/octo-freedom/1002_outage_diagnostics.md` |
| **sanitiser writes TV volume, 1002** | Joe 1002: *"yes to the volume overwrite"* - the 0804 escalation (`kline_sanitiser.py`). `kline_sanitise_service.py` passes `write_tv_volume=True`; with it on, a volume difference alone is a change. `docs/octo-freedom/1002_outage_diagnostics.md` |

## Not ruled — will need him

**Find an item by its name, not its number.** The numbers are stable but they are hard to search.

| # | the question, in one line | blocks |
|---|---|---|
| 1 | ~~can the signal chain run forward~~ | ANSWERED — it runs in realtime |
| 2 | ~~what fields go in the trade-signal dump~~ | **RULED 0929-late** - five fields, `RECON.md`'s wake mechanism. The reason values grew in 1002 (Ruled table) |
| 3 | position size for this strategy | MVP2 only |
| 4 | ~~what happens to the 988 old ledger rows~~ | **RULED 1002** - fresh ledger; the rows are in `o9_ledger_archive_1002` |
| 5 | ~~should wsl_sig_utc carry sig_conf~~ | RULED — it must |
| 6 | ~~may the book go flat~~ | SETTLED by the flip-open ruling — it does |
| 7 | re-bank the 121 leash rows at sig_conf | the leash bank |
| 8 | ~~build a banker for this mech~~ | CLOSED - `build_wsf_trades.py`, key `..._mae0.70` |
| 9 | ~~stop vs opposing sig_utc on the same bar~~ | RULED — the stop wins. Measured: never occurs |
| 10 | ~~does a stop END the trade~~ | CLOSED - it does, and it RACES the other two exits |
| 11 | ~~entry bar~~ | CLOSED - the mech enters on the sig bar. See the note under item 1 |
| 12 | ~~does "no `actionable_confirmed`" extend to the v7 chain's emit bar~~ | **RULED 1001 — yes, and it is a measured NO-OP** |
| 13 | ~~write `fastverdict.verify()` first~~ | **RULED 1001 — hand over with the gap stated** |
| 14 | ~~how far forward may `release` look for the coil tick-down~~ | **CLOSED 1001 — the bound stays `i1`. It was never an open question; the options were the writer's bias** |
| 15 | ~~must the live producer dedup `rev` bars~~ | **RULED 1001 — yes** |

**12. RULED 1001 — `actionable_confirmed` is out, and taking it out changes nothing.** Joe 1001:
*"the 0.3911 mech isn't what we're loading into o9-live, and I know we don't use
actionable_confirmed, so I guess the answer is yes"*.

It was flagged first because `sweep_v3_signal.py:234` reads it:

    e = max(brk, int(ex['rev']), int(coil_exit.fired(ex)[1]))

`fired()` returns whichever of the four `actionable_*` fields a moment set, so on a CONFIRMED moment
that IS `actionable_confirmed`. **Then it was measured, over all 32 moments on 09-01:**

| via | moments | emit bar IDENTICAL with the `fired()` term dropped |
|---|---|---|
| confirmed | 15 | 15 |
| gap | 9 | 9 |
| lookback | 7 | 7 |
| forward | 1 | 1 |
| **total** | **32** | **32** |

`rev` or `brk` always dominates the `fired()` term, so `max(brk, rev, fired(ex)[1])` ==
`max(brk, rev)` on every branch. **The term is redundant in the emit bar.** A live producer does not
need any `actionable_*` field to compute it. Nothing about the +0.3911 mech moves.

**13. RULED 1001 — hand over with the gap stated.** Joe: *"hand over with the gap stated"*. The gap
is below, unchanged. Treat any backtest-vs-live `sideways` mismatch as needing a `fastverdict` check
BEFORE it is treated as an o9-live defect.

**15. RULED 1001 — the live producer dedups `rev` bars.** Joe: *"yes, as long the reconciling
backtest matches, or knows to dedup on the fly"*. It does: `measure_live_stop.py:125` uses
`sig = set()`, collapsing 1,973 moments to 1,863 distinct bars over 90 days. Two moments CAN resolve
to one `rev` — measured on 09-01, the moments at 18:28:10 and 18:31:00 both resolve to 18:40:45. A
live producer that emits twice on that bar will not match.

**13. `fastverdict` has no verifier, and the recon's reference depends on it.** `fastverdict.py:7`:
*"IT IS NOT A SECOND IMPLEMENTATION UNTIL IT IS PROVEN IDENTICAL. verify() replays Joe's own path and
compares every bar. If the mismatch count is anything but zero, nothing here may be used."*

| check | result |
|---|---|
| `def verify` in `fastverdict.py` | **absent** |
| `def verify` anywhere in its git history | **absent** |
| importers of `fastverdict` | **1** — `sweep_v3_signal.py:31` |
| `sideways` references in `optimus9/live/*.py` and `ops/run_o9live.py` | **0** |
| the only proof on record | a commit message: 8 timeframes × 86,400 bars, zero mismatches |
| that proof's scope | **8 of 23 timeframes, 5 of 90 days** |

o9-live never calls it, so there is no live-code risk. The risk is that MVP1's whole job is matching
the live signal to the backtest signal, and the backtest side's `sideways` — step 1, the thing that
decides which bars become v3 rows and therefore every signal — comes from an implementation whose
own stated precondition was never met. A mismatch outside the proven 8 TFs / 5 days would be
**ambiguous**: o9-live wrong, or `fastverdict` wrong.

**14. CLOSED 1001 — the bound stays `i1`, and this was never an open question.** Joe 1001: *"the
answer is in the report that I validated. use whatever was built to create that report"*, then:
*"now that I re-read your explanation, I think you've reinserted a mech that I called out as
lookahead... have you let a bias find its way into the handover docs?"* He was right. This item
previously offered three bounds — `i1` (15 confirmed on 09-01), `brk-1` (30), unbounded (32) — and
described `brk-1` as "what a live walk naturally scans". **That framing is the bias and it is
withdrawn.** Three facts it was hiding:

| fact | evidence |
|---|---|
| a POSITIVE pick needs no bound at all — scan from `i0`, take the first confirmed turn-down | re-run on all 32 moments with the bound at `i1`, at `brk-1`, and at `i1 + 720` bars = 60 min: **0 of 15 picks moved** |
| the NEGATIVE verdict — "no release in this moment" — needs `i1`, which needs `brk` | `coil_moment.moments()`: *"a moment's `end` is only knowable when the next row prints"* |
| `release` returns its verdict at `t + lag_bars` under ANY bound | `coil_moment.py:67-75` — the bound does not touch the confirm window |
| widening the bound IS restrictive, on the population the row above does not count | the same re-run: **15 of 17** unconfirmed moments become confirmed at `brk-1`, 17 of 17 unbounded. 15 -> 30 -> 32 on 09-01 |

**CORRECTED 1001, a second time.** This block previously claimed *"`brk-1` and unbounded both need
`brk`"* — which implies `i1` does not, and it does — and *"the `i1` bound is the only one of the
three that yields a verdict at `pick + 180 s`"*, which belongs to the CONFIRMED branch, not to the
bound. It then concluded *"`i1` is both the causal bound and a non-restrictive one"* from the 0-of-15
figure, which is measured on the already-confirmed population only. That is the withdrawn bias with
its sign flipped: a claim measured on a population chosen to make it true.

**What stands:** Joe ruled the bound stays `i1`. A positive pick is reproducible with no bound. The
negative verdict needs `brk` whichever bound is used, which is why the emit bar is
`max(brk, rev, actionable)`.

**THE CHAIN THAT PRODUCED THE VALIDATED 09-01 REPORT DOES NOT USE `release()`** — which is what
Joe's *"use whatever was built to create that report"* points at. Verified by grep: its three
scripts contain **zero** references to `release`, `i1`, `brk`, `moments()` or `coil_exit`.
**Qualified 1001:** an earlier two-leg plan DID use `release` via `via = confirmed` — Joe dropped it
the same day: *"I'm dropping the idea of using actionable_confirmed in the new mech"*. The notes
still carry that measurement work; the mech as it stands does not. In place of the moment it carries an **arm episode**: set when
ws5Mage holds 25/75 on the dr side for 6 bars = 30 s, cancelled when ws5Mage crosses 50, tested as
`(Mg[k] - 50) * (Mg[k-1] - 50) < 0` — bar `k` and `k-1` only. In place of `release` it takes the
first bar at or after the arm where the combined coil ticks down. Both are decided at the bar, with
no end-of-run to wait for. See `docs/22_go_20260921/NOTES_momtf_mechdev.md`.

1. ~~**Whether the sig_utc producer chain can run forward.**~~ **ANSWERED 0929 — IT RUNS IN
   REALTIME.** Joe corrected the framing first: *"your 'run forward on a bounded window' sounds like
   lookahead, but you could just be saying 'run in realtime'"*. The second one.

   `report_realtime_replay.py` hands the producer only bars 0..k at every cutoff `k` — the v3 rows
   that have printed, the ws1mage-rev legs whose own `sig_conf` is at or before `k`, and
   `release(last_bar=k)` — and records what it would emit. The ladder is every v3 row bar in the
   window, 1179 of them, because that is when information arrives.

   | emission rule | moments emitted | of 121 historical | revisions | match history | differ |
   |---|---|---|---|---|---|
   | eager — emit as soon as the run breaks | 121 | 121 | **0** | 121 | 0 |
   | settled — wait for `k >= i1 + lag_bars` so `release`'s confirm window is never clipped | 121 | 121 | **0** | 121 | 0 |

   Zero revisions is the finding. An answer that changes after it was given is the only signature
   lookahead leaves, and there are none. `coil_moment.release`'s clipped-window hazard — *"A clipped
   window can only fail to disconfirm"* — does not fire on this window either: eager and settled
   agree on all 121.

   **The cost is latency, and it is in the mech.** Measured as (first emittable bar) − (the sig bar
   it names):

   | rule | n | p25 | median | p75 | p90 | max | mean |
   |---|---|---|---|---|---|---|---|
   | eager | 121 | 0 s | 165 s | 440 s | 860 s | 4955 s | 405 s |
   | settled | 121 | 0 s | 180 s | 440 s | 890 s | 4955 s | 416 s |

   Bimodal: **41 of 121 emit at exactly 0 s** (the sig bar is the last event — all 11 `forward` and
   30 of 62 `confirmed`); the other 80 bind on the moment's end row at a median 340 s.

   **CAVEAT on the 41.** A cold re-run of `report_realtime_replay.py` on 0929-late returned **42 of
   121 (34.7%)** for eager and 38 of 121 for settled. The 41 is what the run that produced the
   latency table printed. The two have not been reconciled. Re-run it and take the number your own
   run prints; do not quote 41 without re-running.

   o9-live will know each timestamp correctly, that far after the bar it points at. **A recon that
   does not carry this number will read the delay as a fault.** Re-run the replay whenever a
   producer in the chain changes.

   **TWO DIFFERENT THINGS, AND ONLY ONE IS SETTLED.**

   | | status |
   |---|---|
   | does the answer ever CHANGE | **SETTLED** - 121 of 121, zero revisions. No lookahead |
   | does the answer arrive LATE | **NOT settled** - Joe read the number and parked it |

   **WHAT CREATES THE LAG.** A v3 row prints when a sideways run reaches its sample count on a
   timeframe. Consecutive same-dr rows form a MOMENT. **You cannot know a moment has ended until a
   row prints that BREAKS it**, and that breaking row can be minutes after the moment's last row.
   The signal names a bar inside the moment, but the moment does not exist as an object until it
   is broken. `report_realtime_replay.emit_bar()` is `max(breaking row, rev, actionable)`.

   Two smaller contributors: `rev` needs its own confirmation, **+15 s**; and `actionable` on a
   confirmed release is the release bar **+180 s**, which is Joe's own `confirm_lag_s`.

   **WHAT HAS BEEN DONE TO CURTAIL IT: one thing.** Eager and settled emission were replayed side
   by side and gave **zero revisions and identical answers on all 121**, so the faster rule is
   proven safe. The `sig_conf` change ADDED 15 s - it was a correctness fix, not a
   speed one - and the backward-only gate window was a causality fix with no effect on lag.

   **CORRECTED 1001 — this used to say "Nothing else." A second thing was BANKED on 0930 and never
   reached this package.** Commit `7676ba6`, Joe: *"bank it"* — the CONFIRMED branch can emit
   WITHOUT the latch: **0 revisions in 1,036 moments** of 1,973, worth **+0.3352 -> +0.3495** at the
   emit bar, with the clip hazard closed by measurement (529 of 1,036 clippable, 0 revised). It is
   the one banked result that shortens the `brk` deferral, on over half the moments.

   **WHAT IT COSTS, measured over 90 days** (`measure_emit_entry.py`, 1,973 moments):

   | entry bar | rule#1 open | trades | net > 0 | stopped | net sum | net per trade |
   |---|---|---|---|---|---|---|
   | NAMED - the spec | 1,045 | 894 | 479 (53.6%) | 381 (42.6%) | +349.638 | **+0.3911** |
   | EAGER emit | 901 | 788 | 409 (51.9%) | 344 (43.7%) | +264.174 | **+0.3352** |
   | SETTLED emit | 900 | 785 | 408 (52.0%) | 339 (43.2%) | +274.443 | **+0.3496** |

   **The spec's number is measured at a bar o9-live cannot act on.** The gap is 0.056 to 0.071 per
   trade - 14% to 18% - plus 144 of 1,045 gated opens, because moving the bar moves what rule#1
   sees. Joe has NOT ruled the entry bar changed, so `SPEC.md` still states the named bar.

2. ~~**The dump's exact fields.** `RECON.md` suggests a set. It is a suggestion.~~ **RULED 0929-late** -
   `RECON.md` carries the five fields and Joe's words.

3. **Position size.** 22,000 coins is banked for sneaky-1. Nothing is set for this strategy. Not
   needed for MVP1 selection recon, needed the moment price enters. See `MVP2.md`.

4. ~~**What happens to the 988 old `o9_ledger` rows.**~~ **RULED 1002: fresh ledger.** The 988 rows are in
   `o9_live.o9_ledger_archive_1002`.

5. ~~**Whether `wsl_sig_utc` should carry `sig_conf`.**~~ **RULED 0929 — Joe: *"sig_conf is
   unconditional - it has to happen"*.** `coil_exit.py` now emits the conf bar on every branch that
   was handing back a cross bar. The SELECTION is still made on the cross; only the bar returned
   moves, and `boundary_xwob` 4 makes every move exactly 3 bars = 15 s.

   | branch | rows | `rev` moves | `actionable` moves |
   |---|---|---|---|
   | CONFIRMED | 62 | +3 bars | no — it is release bar + confirm_lag_s, not a mage-rev |
   | GAP | 23 | +3 bars | **+3 bars** — the cross was knowable by `base`, but acting ON it is still 15 s early |
   | FORWARD | 11 | +3 bars | no — it is `base` |
   | LOOKBACK | 25 | no | no — `_knowable` already required `sig_conf <= named` |

   96 of 121 `rev` values move; 23 of 121 `wsl_act_utc` values move, all on the GAP branch.

   **UNRECONCILED, and measure it before you quote it.** The branch table above gives LOOKBACK 25,
   while the trap at the bottom of this file says 23 rows are the moment's END ROW. The DB settles
   only the coarse split — `wsl_source` on the 121 v7 rows is **CONFIRM 62 / END 59**, and
   23 + 11 + 25 = 59, so the branch table is internally consistent with the bank. The 98/23 pair in
   the trap is not. Re-derive the per-branch `via` counts from `coil_exit.resolve` before acting.

6. **~~Whether the book may ever go flat.~~ IT NOW DOES.** This item used to say the book cannot go
   flat after the first trade, because every event is a reversal. **That was true before the
   dr-flip-never-opens ruling and is false now.** Under the ruling the book sits FLAT for 43.8 h of
   the 119.5 h 09-01..09-06 window — **36.6%**. Nothing is open for Joe here; the entry is kept so
   the old statement is not read as current.

7. **Re-banking the 121 `wsf_leash` rows at `sig_conf`.** `coil_exit.py` now emits the conf bar, but
   the 121 banked v7 rows still hold the **old cross bars**. `wsl_knobs` does not encode the change,
   so the unique key cannot tell the two shapes apart and a re-run would either collide or silently
   mix them. Joe's call: re-bank in place, bank alongside under a new knob-string, or leave the bank
   as the historical record and note the offset.

8. ~~**This mech has no banked trade table.**~~ **CLOSED 0929-late.** `trade_walk.walk` carries the
   stop, so `build_wsf_trades.py` produces and banks this mech.

   The key is **`wtc_v3_v7_rule1_gateopen_mae0.70`** and the cap is **also** a config row — Joe
   asked for both. A capped run can never land on the 332 uncapped rows. On those rows: *"they
   exist in a historical key so it shouldn't matter"* — they are left exactly as they are.

   **`wsf_trade_config` v3 = 18 rows**: v2's 16, plus `mae_cap` 0.70 and `stop_same_bar_priority`.
   It is a new version rather than an edit of v2 because the module's own contract says so —
   *"A knob change writes a new version and the trades land BESIDE the old ones, never over them."*
   v2's 16 rows stay as the knob set the historical rows were written under.

   **There is no hard-coded cap left in the code.** `trade_walk.walk`'s `mae_cap` is a required
   argument with no default; a caller that forgets it gets a `TypeError`.

9. ~~**Same-bar priority between the stop and an opposing sig_utc.**~~ **RULED 0929-late — Joe:
   *"use stop"*.** The stop wins, and it is in `trade_walk.walk`.

   **Measured over the 90-day window the tie never occurs:** 0 stop-and-flip and 0 stop-and-sig_utc
   collisions across all 381 stops. Both variants of the walk — stop bar closed to opens, and open
   allowed on the stop bar — produce identical output. The rule exists for a window that does
   collide, not for this one.

10. ~~**Does a stop END the trade?**~~ **RULED 0929-late. IT DOES, AND IT RACES THE OTHER TWO.**

    Joe corrected the framing first: *"research how a stop is applied in trading - you'll learn that
    it's both: (at its signal or flip bar) OR (at the stop bar)"*. A stop does not replace the other
    exits — an open trade carries three live exits and ends at whichever fires first.

    The cap used to be applied in scoring, so a stopped trade still ran to its signal/flip bar and
    the book stayed occupied. **No trade re-scores now** — a stopped trade is −0.70 either way — but
    its close bar moves earlier and the book frees up.

    | | measured over the 90 days |
    |---|---|
    | the book was held past the stop bar | median 1,177 bars = 98 min, max 4,421 bars = 6.1 h |
    | ungated sig_utc bars inside those windows | 216, across 158 of 311 |
    | trades | 753 → **894** |
    | net per trade | +0.3776 → **+0.3911** |

    The cap was then re-swept against the re-walked ladder and Joe re-ruled it: *"retain 0.7% as the
    stop"*. `SPEC.md` carries all 81 rungs.

11. ~~**The entry bar.**~~ **CLOSED 0929-late. The mech enters on the sig bar and its number stands.**

    An earlier version of this file called that number a "ceiling" and said it was not achievable.
    **That claim was imported from a measurement of a DIFFERENT mech** — `bank_emit_entry.py`, which
    has no cap. The capped mech has never been measured at any entry bar other than the sig bar, so
    there was no basis for the word. Removed.

    The 165 s emission latency is real, is measured, and is a **recon** number — see item 1 and
    `RECON.md`. Joe ruled it: *"latency is ok for now"*. It does not discount the mech's number.

## Traps

**THE TWO-LOADER TAPE TRAP — found 0930, fixed, and now guarded. Read this before touching any
multi-window script.** `sweep_v3_signal.Rig` loads the tape twice: `report_coil_exit.load()` gives
`ts`, and `build_wsf_trades.load()` gives the `r` lines rule#1 reads. `build_wsf_trades` does
`from ... build_ws_lines import END_MS, HOURS, WARMUP` — **by value, at import** — so a process that
changes `END_MS` and does not delete `build_wsf_trades` from `sys.modules` gets `r` lines off the
PREVIOUS tape while `ts` is on the new one. rule#1 then reads the lines at the wrong bars, silently,
and the gate moves by 2.3× on identical bars. `oos_confirm_lag.py` and `score_5day_windows.py` both
did exactly this. Both now reload it, and `Rig.__init__` raises `RuntimeError` on a bar-grid
mismatch. **The guard is the fix — do not remove it, and add `build_wsf_trades` to the reload list
of any new script that walks more than one window.**

**`coil_exit`'s SINGLE `actionable` KEY NO LONGER EXISTS — BREAKING API CHANGE, 0930.** It was split
into four fields and a reader function:

| what | detail |
|---|---|
| the four fields | `actionable_confirmed`, `actionable_lookback`, `actionable_gap`, `actionable_forward` — `coil_exit.py:53` |
| exactly one is set per moment | the other three are `None` |
| how to read it | `fired(ex)` returns `(field_name, bar)` — `coil_exit.py:75`. Never a bare number |
| why | Joe 0930: *"it needs to be split. I'd retain `actionable_` as a prefix and tack the mech's usage as the suffix"*. One key used to carry four unrelated events, so any statement about it was true on one branch and false on three |

**Anywhere this package still says "`actionable`" as a single key — e.g. the column headings in the
emit-bar section below — it is describing the pre-0930 shape. Code written to that description
raises `KeyError`.**

**SUPERSEDED 1001 — EVERY CLAUSE BELOW IS NOW FALSE.** The walk is `optimus9/compute/leash_walk.py`
+ `arm_state.py`, committed; its numbers are reproduced and ASSERTED by `report_leash_walk.py`
(exit 1 on a miss or on a shape change); and it IS the recon's machine, named `octo-freedom`. Struck
rather than deleted so a reader who saw it knows it moved.

~~THE MECH IN DEVELOPMENT IS NOT REPRODUCIBLE.~~ The arm / flat-run-race / `ws1mage-rev` chain
described in `docs/22_go_20260921/NOTES_momtf_mechdev.md` was walked in a job-scoped scratch
directory that will be deleted. Its numbers — 09-01 only — are a written record, not a checkable
result. It is not in the recon. If a future session needs those numbers, the mech has to be rebuilt
in the repo first.

**The gate trap is CLOSED too.** `rule1_gate` used to read `[k - tol, k + tol]` - 210 s of future -
and extend a run forward unbounded. Joe 0929 dropped the forward half: the window is now
`[k - 84 bars, k]`, 7 minutes back, and a run stops at the window edge. **Config v1 and its 166 rows are GONE** — Joe 0929
dropped them after the A/B, so v2 is the only shape that runs. Do not reintroduce a forward read.

**The backstop trap is CLOSED.** It used to be real: `trade_walk.backstop()` computed the closing bar
at open time from the stretch list, which is a future bar. Joe 0929: *"make this causal before we
handover to a new session. ie, IF this bar has dr-flip THEN"*. `walk()` is now a bar-by-bar loop
carrying `dr` and a `left` flag and reading only `dr[k]` and `dr[k-1]`. `backstop()` is deleted.
Do not reintroduce the old shape.

**`wsl_sig_utc` is the `sig` CROSS bar, not the `sig_conf`.** `sig_conf = sig + boundary_xwob − 1 =
sig + 3 bars = 15 s`. Comparing the banked column against `sig_conf` matches **0 of 121**, so when
you are checking what production banked, check against `sig`. **This is a description of the bank,
not an endorsement — see item 7.** Joe 0929 read the same fact as a defect and ruled on it.
The per-branch split of which rows are the moment's END ROW is **unreconciled — see item 5.**

**`wsf_leash` holds several rows on one sig bar.** 121 rows are 109 distinct bars over the window; on
09-01, 32 rows are 28 bars. Any count keyed on the bar collapses them. Say which you mean.

**`wsl_dr` is not the walk's dr.** `wsl_dr` is `latch` (no wob) read at the moment's **first** bar —
242 of 242. The walk's dr is `latch_wob` read live at the bar it starts from. They differ on 7 of 242
rows. §22.21 and §22.22. This is intended, not a bug to fix.

**EVERY ROW IN `wsf_trades` IS A MECH WITHOUT THE CAP.** 332 rows, 4 key/window groups, none of
them carrying the stop. Do not compare o9-live against any of them and do not quote their numbers.
See item 8.

**The two close rules are still not knobs.** `wsf_trade_config` v3 holds `mae_cap` and
`stop_same_bar_priority`, but the opposing-dr close and the flip-never-opens rule are in the walk's
code, not in the table. The **version** is what discriminates them: v3 means both rules plus the
stop. A v2 run and a v3 run cannot share a key.

**o9-live's `StrategyLoop` runs `v2_walk_ad` today.** Not this strategy, and `ops/run_o9live.py:28`
labels that producer *"'ad'=v2_walk_ad (look-ahead arm-delay)"*. See `CODE_MAP.md`.

**The sign conventions are inverted between the two codebases.** `optimus9/live/strategy.py:5-6`:
*"bd +1 = Buy/long, bd −1 = Sell/short"*. This strategy: **`dr +1 = SHORT, dr −1 = LONG`**. A
producer written for `StrategyLoop` must flip the sign. Nothing in the live code says so.

## Joe's standing rules for whoever picks this up

> "always be raw with me, and never infer. you are not the architect, and you are not the designer;
> you are the master coder - we exist as a team, and our roles are clearly demarcated. any time you
> need to make an unplanned decision while you code, stop and tell me what you see"

> "you're not here to make data look good. the data you see as not good, is exactly the data I need to
> make decisions: you will not hide it from me"

> "my requirement is that you use only the mecahnisms I've given you to try and hit a target. if you
> can't hit a full target, tell me why. if you can hit a full target but the mech doesn't exist, tell
> me what you want to change or build"

Also: no caps, windows or truncations he did not ask for; every hard-coded value belongs in the DB;
every figure goes in a table, never inline in a bullet; no percentage without its episode count; and
one `TL;DR:` line, only when there is a finding or a decision — the three closers were dropped 1001.

`.claude/joes-convo-style.md` is the full format contract. `docs/staying_light.md` is the other half.
