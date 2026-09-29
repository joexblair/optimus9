# The mech being handed over

**ONE MECHANISM IS HANDED OVER: the one the MAE cap was applied to.** Joe 0929-late: *"you should be
handing over only the mech that the MAE cap was applied to"*.

Anything measured without the cap is a **different mech**. It is not a baseline, not a target and not
a comparison. If a number in this package is not from the capped mech, it is a mistake — say so.

## The mech, end to end

| stage | what it is |
|---|---|
| signal | `wsf_leash` v7 `wsl_sig_utc`, from the banked `wsf_dtf_v3` knobs — span 10, slope 0.40, fence 25/75, samples 21, tf 1..23, support_min 23 |
| gate | `rule1_gate` config v2 — backward-only `[k-84 bars, k]` = 7 min, a run clamped at the window edge |
| entry | **the sig bar** — the bar the signal names |
| close #1 | an **opposing-dr** `sig_utc`. A same-dr `sig_utc` is INERT |
| close #2 | the **dr-flip backstop**, if no opposing signal came first. It CLOSES and the book goes flat |
| stop | **MAE cap 0.70%** — the trade ends at the first bar its adverse excursion reaches it |
| same-bar, flip vs signal | the **dr-flip** wins |
| same-bar, stop vs opposing signal | the **STOP** wins |
| order type | **market**, both legs |
| score | MAE/MFE as percentages of entry. **NO P&L** — Joe 0917 |

`dr +1 = SHORT, dr -1 = LONG`. Joe 0925: *"+dr = SHORT position, -dr = LONG postition"*.

## The numbers — 90 days of line cache, 2026-06-10 .. 2026-09-08

Produced by `python3 sweep_mae_cap.py`.

| | |
|---|---|
| sig bars | 1,863 |
| pass rule#1 | 1,045 |
| **trades** | **753** |
| net > 0 | 409 of 753 = 54.3% |
| stopped at the cap | 311 of 753 = 41.3% |
| MAE sum | 334.677 |
| net sum | +284.313 |
| **net per trade** | **+0.3776** |

Entry is the bar the signal NAMES. That is the spec, it is what these numbers measure, and the
measurement is sound.

**Separately**, `report_realtime_replay.py` measures how long after that bar the chain can first
EMIT the timestamp — a median 165 s. Joe 0929 read that and ruled: *"latency is ok for now"*. It is
a **recon** number: it tells the recon job what wall-clock-to-bar gap is normal so a normal gap is
not read as a fault. `RECON.md` carries it. **It is not a discount on the figures above.**

## The cap is 0.70 and the choice is not knife-edge

Joe specified 0.9 on 0929, was shown a 0.05-step sweep from 0.05 to 4.00 over the 90 days, and ruled
**0.70** — the peak on net per trade.

| cap % | trades | net > 0 | stopped | net per trade |
|---|---|---|---|---|
| 0.40 | 753 | 321 (42.6%) | 425 (56.4%) | +0.3037 |
| 0.60 | 753 | 382 (50.7%) | 350 (46.5%) | +0.3553 |
| **0.70** | **753** | **409 (54.3%)** | **311 (41.3%)** | **+0.3776** |
| 0.80 | 753 | 418 (55.5%) | 291 (38.6%) | +0.3689 |
| 0.90 | 753 | 426 (56.6%) | 266 (35.3%) | +0.3585 |
| 1.10 | 753 | 445 (59.1%) | 219 (29.1%) | +0.3655 |
| 2.20 | 753 | 464 (61.6%) | 102 (13.5%) | +0.2794 |
| no cap | 753 | 468 (62.2%) | 0 | +0.1464 |

- 0.55 to 0.95 is a plateau — every value inside it is within 0.04 per trade of the peak.
- every cap from 0.15 up beats no cap.
- `net > 0 %` and `net per trade` **disagree across the whole ladder**. The win count climbs to 62.2%
  at no cap while the per-trade peaks at 0.70. A tighter cap turns would-be winners into `-cap`
  losses but kills the big losers faster. **Rank on net per trade. Joe ruled 0.70 on that basis.**
- **the trade count is 753 at every cap.** The cap changes the SCORE, not the walk. That is a real
  property of the code and it has a consequence — see `OPEN.md`, *does a stop end the trade*.

## The knobs

All in `wsf_trade_config`, **version 2, the only version**. Each row carries Joe's own words.

| name | value | source |
|---|---|---|
| `leash_instance` | v7 | Joe 0929: *"v7"* |
| `gate` | `rule1_gate.open` — the rule#1 leg OR the scenario leg | Joe 0929: *"using the gate that you validated in our shared sheet, col L"* |
| `same_bar_priority` | dr-flip | Joe 0929: *"same bar priority: dr-flip"* |
| `rule1_back_min` | **7.0 — minutes BACK, 84 bars** | Joe 0929: *"inside of the last {knob:7} minutes"* |
| `rule1_fwd_min` | **0 — causal** | Joe 0929: *"let's drop the forward"* |
| `rule1_run_clamp` | **window — a run stops at the window edge** | Joe 0929 |
| `rule1_fence_lo/hi` | 27.0 / 73.0 | Joe 0923 |
| `oob_lo/hi` | 15.0 / 85.0 | Joe 0913: *"oob is alwasy 15/85"* |
| `latch_tf` | 13 | Joe 0925 |
| `latch_wob` | 8 bars = 40 s | Joe 0926: *"we have to stick on 8"* |
| `mage_fence_lo/hi` | 25.0 / 75.0 | build_wsf_dtf_v3 |
| `div_tf` | 1 — the divergence runs on ws1r | Joe 0924 |
| `scenario_lines` | ws2r, ws3r, gcws30r | Joe 0924 |

**THE CAP IS NOT A KNOB.** `mae_cap` is not a row in this table. 0.70 emerges at runtime as the peak
inside `sweep_mae_cap.py`. Neither are the two close rules. So `trade_config.key()` —
`wtc_v%d_%s_%s % (version, leash_instance, gate)` — **cannot tell this mech apart from the one
without the cap.** That is `OPEN.md`, *no banked trade table for this mech*.

**The knobs are NOT in `wsf_dtf_v3_config`, deliberately.** Spec §21.6: `leash_bank.knob_string` puts
the v3 config version inside `wsl_knobs`, so a bump would split the next leash write off from the
121-row bank. That consequence is Joe's to sanction and he has not.

## THE GAP: this mech has no banked trade table

`sweep_mae_cap.py` has **zero** DB writes. It computes the 753 trades in memory and prints.

`build_wsf_trades.py` is the only banker, and **it does not produce this mech** — it has no stop in
it, because `trade_walk.walk` has no stop in it.

| what exists | what it is |
|---|---|
| `sweep_mae_cap.py` output | the capped mech, 753 trades, printed, **not banked** |
| every row in `wsf_trades` | a **different mech** — no cap. Do not compare against it |

**So the recon has nothing banked to compare o9-live against.** Building that is work, and which key
it lands under is Joe's. See `OPEN.md`.

## What the recon must prove

1. **Selection** — o9-live opens and closes on the same bars this mech does.
2. **Causality** — the verdicts do not change when re-run later over the same bars. A verdict that
   moves is lookahead. Joe 0929: *"it every recon job, review the backtest's last 24 hours and
   re-validate all validated o9-live trades (this re-validation will expose lookahead if there is
   any)"*.
3. **Cache integrity** — Joe 0929 chose the line-cache over a live tape deliberately: *"I'm going to
   say the line-cache because that organically gives us another test-point (ie, is cache and
   real-time kline collection in sync)"*.
4. **The stop** — level, timing, fill and priority. `RECON.md` has the per-trade checks.

**Price is out of scope.** Joe 0929: *"no need to recon price yet, that will be MVP2"*. `MVP2.md`.

## The timestamp gap is the point

Joe 0929: *"this is exactly what we're reconcilling. o9-live has no choice - it must use wall-clock"*.
The backtest is bar-indexed on the 5 s grid; o9-live stamps wall-clock. Mapping one to the other **is**
the test, not a nuisance to be papered over.
