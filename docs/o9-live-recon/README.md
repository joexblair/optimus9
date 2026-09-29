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
> Then, in your own words: read back the trade rules from `OPEN.md`'s **Ruled** table — that table,
> not `SPEC.md`'s narrative, is what the code does — state the difference
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
| `MVP2.md` | what MVP1 deliberately leaves out, and why. **Not MVP1 work** |

## The one-line state

**THE STRATEGY CHANGED SUBSTANTIALLY ON 0929-late. Everything below supersedes the older numbers
still present in this package.** Three rulings from Joe and one defect he caught:

| | |
|---|---|
| a sig_utc closes ONLY on an opposing dr | a same-dr sig_utc is INERT |
| the dr-flip backstop CLOSES but never OPENS | the book goes flat instead |
| MAE is capped at **0.70%** and the cap is a STOP | `MFE-MAE` prints `-0.70` when hit |

**ANYTHING MEASURED WITHOUT THE CAP IS A DIFFERENT MECH** and is not in this package. Joe 0929-late:
*"you should be handing over only the mech that the MAE cap was applied to"*.

Three more rulings landed 0929-late, after the above:

| | |
|---|---|
| same-bar, stop vs opposing sig_utc | **the STOP wins** — Joe: *"use stop"* |
| order type | **market**, both legs. Limit placement is MVP2 |
| the stop is client-side for MVP1 | a LARGER exchange-resident backstop is MVP2 |

**THE MACHINE, as handed over:**

    signal      wsf_leash v7 `wsl_sig_utc`, from the banked wsf_dtf_v3 knobs
                span 10, slope 0.40, fence 25/75, samples 21, tf 1..23, support_min 23
    gate        rule1_gate config v2 - backward-only [k-84 bars, k], run clamped at the edge
    walk        trade_walk.walk - THREE live exits racing each other, first to fire wins:
                an opposing-dr sig_utc, the dr-flip backstop, and the stop. The flip never opens
    entry       the sig bar - the bar the signal NAMES
    stop        MAE cap 0.70% of entry, IN THE WALK. Joe specified 0.9 on 0929, ruled 0.70 on the
                first ladder, then re-ruled it on the re-walked ladder: "retain 0.7% as the stop"
    key         wtc_v3_v7_rule1_gateopen_mae0.70 - the cap is IN the key, Joe 0929-late
    score       MAE/MFE percentages of entry. NO P&L - Joe 0917

**THE NUMBERS, 90 days of line cache, 2026-06-10 .. 2026-09-08:**

| | |
|---|---|
| sig bars | 1,863 |
| pass rule#1 | 1,045 |
| **trades** | **894** |
| net > 0 | 479 (53.6%) |
| stopped at the cap | 381 (42.6%) |
| MAE sum | 403.022 |
| net sum | +349.638 |
| **net per trade** | **+0.3911** |

| closed by | n | of 894 |
|---|---|---|
| stop | 381 | 42.6% |
| dr-flip | 362 | 40.5% |
| sig_utc | 151 | 16.9% |

**Entry is the sig bar — the bar the signal NAMES.** That is the spec and it is what these numbers
measure.

**The stop RACES the other two exits; it does not replace them.** No trade re-scores because of it -
a stopped trade is -0.70 either way. What moves is its CLOSE BAR, and therefore when the book frees
up. The book used to be held a median 98 minutes past the stop bar, with 216 ungated sig_utc bars
sitting inside those windows, INERT because a position was open. Freeing them is worth 753 -> 894
trades and +0.3776 -> +0.3911 per trade.

**The cap was re-ruled against a re-walked ladder.** The first ladder scored one fixed trade set of
753 at every rung; with the stop live every rung has its own trade population, so all 80 rungs were
re-walked from the tape. Joe: *"retain 0.7% as the stop"*. `SPEC.md` carries all 81 rungs.

- net per trade peaks at cap 1.25, +0.3928 on 843 trades. **0.70 sits 0.4% below it.**
- net sum peaks at cap **0.70**, +349.638. It is the best rung on that measure.
- the band 0.70 to 1.30 spreads only 0.012 per trade. There is no knee in it.
- `net > 0 %` rises monotonically to 62.2% with no stop, where net per trade is worst.
  **Ranking on win% picks the worst mech on the board.**

Causality is unchanged and still holds: every module from `build_wsf_dtf_v3` down has been walked,
and the sig_utc chain was replayed in realtime on 0929 - 121 of 121 moments, zero revisions, median
165 s emission latency that is in the mech.

o9-live and fakeAPI **exist and run**, but on a different strategy. The bridge is the work.

**`docs/sweeps/` measures a mech without the MAE cap. It is not this mech. Do not use it.** Joe
0929-late: *"ok, the sweep is definitely poisoned. let's go back to baseline"* and *"you should be
handing over only the mech that the MAE cap was applied to"*.

## Reproduce it before you trust it

```
python3 sweep_live_stop.py        # the cap ladder, 81 rungs. The 0.70 rung is 894 / +0.3911
python3 report_realtime_replay.py # the causality proof: 121 of 121, zero revisions
python3 build_wsf_trades.py       # the same mech, banked. IT WRITES - read OPEN.md first
```

`build_wsf_trades.py` banks under `wtc_v3_v7_rule1_gateopen_mae0.70`. The 332 rows already in
`wsf_trades` under the bare keys are an **uncapped** mech - history, not a comparison.

Both must come out of the tape and the DB alone. A mismatch is a finding, not a nuisance — see
`RECON.md`.
