# The recon procedure

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
3. Run `build_wsf_trades.py` over the window containing those bars.
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
it fills immediately on hitting the bar"*. `pxs` is DEMA(close, 2) on the EVENT tape - a bar exists
where volume occurred, a filler bar carries the previous value forward - so intrabar movement is
already resolved at the 5 s grid. **Do NOT model slippage. Measure divergence FROM the spec.**

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
the stop, so this path is exercised 42.6% of the time. The value 0.70 is not a `wsf_trade_config`
row; it is `MAE_CAP` in `optimus9/compute/trade_walk.py` and it is in the trade key.

## Four mismatch classes, reported separately

| class | what it means |
|---|---|
| selection | o9-live and the backtest disagree about whether to trade a bar |
| causality | a backtest verdict changed on re-run over the same bars |
| cache | the line cache and realtime collection disagree about the bar's values |
| **stop** | the signal matched and the EXIT did not - level, timing, fill or priority |

Collapsing them into one "mismatch" number destroys the information the job exists to produce.
