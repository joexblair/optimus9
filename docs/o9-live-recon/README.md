# o9-live + fakeAPI recon — handover

Joe 0929: *"I want to get o9-live + fakeAPI online so that we can start troubleshooting any potential
non-causal issues"* and *"the goal for this next step is purely recon against backtest. I'll keep
improving the strategy in the background while o9-live is under review"*.

**This is a forward test against a fake exchange. It is not live trading.** Joe 0929: *"we're not
going 'online-live'. fakeAPI is our test-bed which o9-live connects to"*.

## The startup prompt

> Read every file in `docs/o9-live-recon/`. Then read `SPEC.md`'s rule list back to me in your own
> words, and tell me which of the five build steps in `CODE_MAP.md` you would do first and why.
> Do not write code until I answer.

## The files

| | |
|---|---|
| `SPEC.md` | the strategy, the knobs, and what a recon has to prove |
| `CODE_MAP.md` | what already exists, what is new, and the five things that are NOT built |
| `RECON.md` | the recon procedure, the wake mechanism, and the 24-hour re-validation |
| `OPEN.md` | what Joe has ruled, what he has not, and the traps |

## The one-line state

The reference backtest is **built and banked** — `build_wsf_trades.py` → `wsf_trades`, 142 trades
over 2026-09-01..09-06. o9-live and fakeAPI **exist and run**, but on a different strategy. The
bridge between them is the work.
