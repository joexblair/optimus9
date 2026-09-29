# o9-live + fakeAPI recon — handover

Joe 0929: *"I want to get o9-live + fakeAPI online so that we can start troubleshooting any potential
non-causal issues"* and *"the goal for this next step is purely recon against backtest. I'll keep
improving the strategy in the background while o9-live is under review"*.

**This is a forward test against a fake exchange. It is not live trading.** Joe 0929: *"we're not
going 'online-live'. fakeAPI is our test-bed which o9-live connects to"*.

## The startup prompt

> Read every file in `docs/o9-live-recon/`, then `.claude/joes-convo-style.md` and
> `docs/staying_light.md`. Run the two commands under "Reproduce it before you trust it" in
> `README.md` and tell me whether they match the stated numbers.
>
> Then, in your own words: read back the four trade rules from `SPEC.md`, state the difference
> between a forward read and a deferred decision as `CAUSALITY.md` draws it, and tell me which of
> the five build steps in `CODE_MAP.md` you would do first and why.
>
> Do not write code until I answer.

## The files

| | |
|---|---|
| `SPEC.md` | the strategy, the knobs, and what a recon has to prove |
| `CODE_MAP.md` | what already exists, what is new, and the five things that are NOT built |
| `CAUSALITY.md` | the full audit, module by module, and the one trap that is still live |
| `RECON.md` | the recon procedure, the wake mechanism, and the 24-hour re-validation |
| `OPEN.md` | what Joe has ruled, what he has not, and the traps |

## The one-line state

The reference backtest is **built, banked and causal** — `build_wsf_trades.py` → `wsf_trades`,
**119 closed trades (120 rows, the last still open)** over 2026-09-01..09-06 at config v2. Every module from `build_wsf_dtf_v3` down to
`wsf_trades` has been walked for causality, and 0929 the whole sig_utc chain was **replayed in
realtime**: 121 of 121 moments, zero revisions, at a median 325 s emission latency that is in the
mech. o9-live and fakeAPI **exist and run**, but on a different strategy. The bridge between them is
the work.

Two things are open before the first recon job — `OPEN.md` items 2 and 8. Item 8 is the live one:
`coil_exit` emits `sig_conf` now (Joe ruled it 0929) but the 121 banked leash rows still hold the old
cross bars, so the reference below has not moved yet.

## Reproduce it before you trust it

```
python3 build_wsf_trades.py --day 2026-09-01        # 25 trades, MFE > MAE 13 of 25
python3 build_wsf_trades.py                          # 119 closed, MFE > MAE 68 of 119
```

Both must come out of the tape and the DB alone. A mismatch is a finding, not a nuisance — see
`RECON.md`.
