# The recon procedure

> **1001 — THE MACHINE CHANGED. READ `README.md`'s MACHINE SECTION BEFORE THIS FILE.**
> The signal is `WALK FIRES FROM`, from `optimus9/compute/leash_walk.py` + `arm_state.py`, knobs in
> `wsf_trade_config` **v4**, acceptance test `report_leash_walk.py`. Joe 1001: *"it is the only
> outcome that is stamped as ready for live trading"*.
>
> **THIS FILE WAS WRITTEN FOR THE v7 `wsl_sig_utc` CHAIN AND HAS NOT BEEN REWRITTEN.** Everything in
> it about the v7 producer, its five build steps, its numbers and its entry bar is the HISTORICAL
> RECORD. Where it tells you to build something, check it against the machine section first.


## The wake mechanism

Joe 0929: *"they will need to wake on every trade signal - I would build a o9-live trade-signal dump
to log and consume via a shell monitor"*.

**The dump.** o9-live appends one line per trade action to a dedicated log — not `o9live_run.log`,
which carries everything. One line, one action, append-only, never rewritten.

**THE FIELDS ARE RULED.** Joe 0929-late: *"I'm confirming the list so that the recon-loop can
start"*. Five fields, no more:

| field | why |
|---|---|
| wall-clock ms | what o9-live has. Joe 0929: *"o9-live has no choice - it must use wall-clock"* |
| action | `open` or `close` |
| side | `Buy` or `Sell` |
| reason | `sig_utc`, `dr-flip` or `stop` — the thing that fired |
| the bar it believes it acted on | so a bar-vs-wall-clock gap is visible without inference |

**Dropped, and why:**

| field | Joe 0929-late |
|---|---|
| the config key | *"this is too fringe to worry about. organically, we're going to reset o9-live on any change as a matter of course"* |
| the order id | it would let a log line be matched to the order o9-live actually sent to the exchange. *"maybe you just need to let it run without any further consideration... and handle it if it comes up"* |

Order type is **market** on both legs — Joe 0929-late. It is not a dump field because it cannot
vary in MVP1. Limit placement is `MVP2.md`.

**The monitor.** A shell loop that tails the dump and, on a new line, wakes a Claude session. The
session does one recon job and exits. Do not hold a session open across signals — a long-lived
session accumulates context and the point of the job is a clean comparison each time.

## The recon job, per trade action

1. Read the new dump lines.
2. Map each wall-clock stamp to a tape bar. **Record the gap.** That mapping is the test, not
   housekeeping.
3. **CORRECTED 1001 — this step used to say "Run `build_wsf_trades.py` over the window containing
   those bars", and `README.md`, `CAUSALITY.md:144` and `SPEC.md:234` all forbid that file.** It is a
   BANKER: it reads already-banked bars out of `wsf_leash` (15 s early, and `WIN_MS` pins it to
   09-01..09-06), so it cannot cover a recon window and it does not rebuild the chain.

   **The reference is `measure_live_stop.build(rig)`** — the chain rebuilt from the tape, sideways →
   v3 rows → moments → `release` → `resolve`, which is what produced 1,863 / 1,045 / 894 / +0.3911.
   Joe 1001, on what "reference" means: *"I'm assuming that 'reference' = the code that o9-live will
   adopt"*. It is, and these four are it:

   | step | the code o9-live adopts |
   |---|---|
   | the chain | `measure_live_stop.build(rig)` |
   | rule#1 | `sweep_v3_signal.Rig.gate_open(k)` |
   | the three racing exits | `optimus9/compute/trade_walk.walk()` |
   | the MAE/MFE rule | `measure_live_stop.score()` |

   **Adopting `measure_live_stop.build` adopts `fastverdict`**, because `Rig.sideways` calls
   `fastverdict.sideways_mask`. See `OPEN.md`'s trap on it — its own verifier does not exist.
4. Compare, in this order: **does a backtest trade exist on that bar** → **same side** → **same
   reason** (`sig_utc` vs `dr-flip`) → **same open/close role**.
5. Report every mismatch with both sides' numbers. A mismatch is the deliverable, not a failure.

Price is **out of scope** until MVP2. Joe 0929. `MVP2.md` carries the full MVP1/MVP2 line - price
recon, the exchange-resident stop backstop, limit orders and position size are all there.

## The latency the recon job must carry

`report_realtime_replay.py`, 0929: the chain runs in realtime, 121 of 121 moments, **zero
revisions**. What it costs is delay between the bar a `sig_utc` NAMES and the bar it can first be
EMITTED:

| rule | n | p25 | median | p75 | p90 | max | mean |
|---|---|---|---|---|---|---|---|
| eager | 121 | 0 s | 165 s | 440 s | 860 s | 4955 s | 405 s |
| settled | 121 | 0 s | 180 s | 440 s | 890 s | 4955 s | 416 s |

**It is bimodal and the median alone misleads.** A cold re-run on 0929-late returned **42**, not 41 -
re-run it and take your own number, do not quote either without running it. 41 of 121 rows emit at **exactly 0 s** — the moment
had already ended and the sig bar is the last event in the chain. All 11 `forward` rows and 30 of 62
`confirmed` rows sit there. The other 80 bind on the moment's END ROW and run a median 340 s; every
`lookback` and `gap` row is in that group by construction.

| what binds the emit bar | rows | median eager lag |
|---|---|---|
| the sig bar itself | 41 | 0 s |
| the moment end row | 80 | 340 s |

**This is in the mech, not the implementation.** o9-live will name the right bar, minutes after that
bar. Step 2 of the recon job records the wall-clock-to-bar gap; compare it against THIS table, not
against zero. A gap inside this distribution is the mech working. A gap outside it is a finding.

Re-run the replay whenever a producer in the chain changes.

## The 24-hour re-validation — the lookahead test

Joe 0929: *"it every recon job, review the backtest's last 24 hours and re-validate all validated
o9-live trades (this re-validation will expose lookahead if there is any)"*, and *"catching lookahead:
re-run from tape"*.

Every recon job, **re-run the backtest from the tape** over the last 24 hours and compare against the
verdicts stored at the previous recon.

- a verdict that **changes** when re-run over the same bars is **lookahead**. Nothing else produces
  that signature.
- a diff against stored verdicts alone catches drift but not lookahead. Joe chose the re-run.
- the cost is a full producer pass per recon. Joe sanctioned it.

**Store every verdict** with the config key and the tape/line cache key it was computed under. Without
the cache key, a changed line and a changed verdict are indistinguishable.

## The cache is deliberately the source

Joe 0929: *"tape vs line at recon time. I'm going to say the line-cache because that organically gives
us another test-point (ie, is cache and real-time kline collection in sync)"*.

So a third class of mismatch exists and is wanted: the cache and the realtime kline collection
disagreeing. Report it as its own category, not as a selection gap.

## The stop-loss check - Joe 0929

The strategy carries a **0.70% MAE cap applied as a stop**, and it fires on **381 of 894 trades = 42.6%**.
Joe: *"o9-live has a trading engine that might show faults in applying the stop-loss"*.

**The backtest's fill is the SPEC, not an idealisation.** Joe 0929: *"pxs is designed to handle
this well in advance of the trading machine -- this means that the stop does not increase to 0.85 -
it fills immediately on hitting the bar"*. **CORRECTED 1001 — this used to say `pxs` is DEMA(close, 2) on the EVENT tape. It is not.** The
series the stop and every MAE/MFE actually read traces as `Rig.px` -> `build_wsf_trades.load:123`
`np.asarray(J.px)` -> `jig.py:1387` `self.W.px` -> `BiasWindow.px` -> `bl_detect._setup:261`
`IC.dema(IC.build_source(base, 'close'), 2)` — **DEMA over the FULL 5 s base, filler bars
included**. The event-tape series DOES exist, as `__pxs__` in the rpl_cache npz
(`rpl_cache.py:59-69`, `_px_smooth_evt`), and three other scripts read it — but neither
`build_wsf_trades` nor the `Rig` does. `filler_invisible` 1 governs LINES
(`BiasWindow._lbase`), not `px`.

Both series are causal, so this is not a lookahead. It matters because the event-tape claim is what
licensed "intrabar movement is already resolved at the 5 s grid". **Do NOT model slippage — Joe
0929 ruled it — but do not justify that with a series the stop does not read.**

Every recon job must check, per stopped trade:

1. did o9-live place a stop at all, and at what level
2. is the level 0.70% of the ENTRY price, not of a later mark
3. the trigger bar in the backtest vs the bar o9-live acted on - they should be the SAME bar
4. did the engine act on the pxs bar, or rest an order at the exchange and fill elsewhere
5. whether a stop and an opposing sig_utc landed on the same bar - **RULED 0929-late: the STOP
   wins.** Joe, asked directly: *"use stop"*. If o9-live takes the signal instead, that is a stop
   mismatch, not a selection mismatch

A stop divergence is its own class. Do NOT fold it into `selection` - the signal was right and the
exit was not, which is a different fault with a different owner.

**THE STOP IS A LIVE EXIT IN THE BACKTEST AND IT MUST BE ONE IN o9-live.** `trade_walk.walk`
carries it: an open trade has three live exits - an opposing-dr sig_utc, the dr-flip backstop, and
the 0.70% stop - and ends at whichever fires FIRST. The others are cancelled. That is the OCO
mechanic, and it has a consequence for the engine:

**when a signal exit fills, o9-live must CANCEL the resting stop, and when the stop fills it must
cancel nothing but must go FLAT.** An orphaned stop left at the exchange will fire on a position
that no longer exists, or block the next entry. Check for orphans every recon job.

**After a stop the book is FLAT**, and a later sig_utc opens a new trade - 381 of 894 trades end on
the stop, so this path is exercised 42.6% of the time.

**CORRECTED 1001 — this paragraph used to state the opposite, and the opposite is false.** The value
0.70 **IS** a `wsf_trade_config` row: config **v3**, row `mae_cap` = 0.70, and it is also in the
trade key `wtc_v3_v7_rule1_gateopen_mae0.70`. There is **no** `MAE_CAP` constant in
`optimus9/compute/trade_walk.py` — line 72 of that file says so outright: *"THE CAP'S VALUE IS NOT
IN THIS FILE. Joe 0929-late: move MAE_CAP to the DB"*. `trade_walk.walk(..., mae_cap)` takes it as a
**required positional with no default** (`trade_walk.py:114`), so a caller that forgets it gets a
`TypeError`. Do not reintroduce the literal.

## Four mismatch classes, reported separately

| class | what it means |
|---|---|
| selection | o9-live and the backtest disagree about whether to trade a bar |
| causality | a backtest verdict changed on re-run over the same bars |
| cache | the line cache and realtime collection disagree about the bar's values |
| **stop** | the signal matched and the EXIT did not - level, timing, fill or priority |

Collapsing them into one "mismatch" number destroys the information the job exists to produce.
