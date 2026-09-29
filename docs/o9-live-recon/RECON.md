# The recon procedure

## The wake mechanism

Joe 0929: *"they will need to wake on every trade signal - I would build a o9-live trade-signal dump
to log and consume via a shell monitor"*.

**The dump.** o9-live appends one line per trade action to a dedicated log — not `o9live_run.log`,
which carries everything. One line, one action, append-only, never rewritten. Suggested fields, and
they are a suggestion not a ruling:

| field | why |
|---|---|
| wall-clock ms | what o9-live has. Joe 0929: *"o9-live has no choice - it must use wall-clock"* |
| action | `open` or `close` |
| side | `Buy` or `Sell` |
| reason | `sig_utc` or `dr-flip` — the thing that fired |
| the bar it believes it acted on | so a bar-vs-wall-clock gap is visible without inference |
| the config key | `wtc_v1_v7_rule1_gateopen`, so a knob change is never silently mixed in |
| `led_id` | to join to `o9_live.o9_ledger` |

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

Price is **out of scope** until MVP2. Joe 0929.

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

## Three mismatch classes, reported separately

| class | what it means |
|---|---|
| selection | o9-live and the backtest disagree about whether to trade a bar |
| causality | a backtest verdict changed on re-run over the same bars |
| cache | the line cache and realtime collection disagree about the bar's values |

Collapsing them into one "mismatch" number destroys the information the job exists to produce.
