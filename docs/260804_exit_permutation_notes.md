# 0804 exit permutation run — running notes

Joe 0804: *"run as many permutations that you can muster across the full ~12wk window ... don't
sample, be precise. keep notes on what you add and what you remove"* and *"don't try to fit the
number - hold everything loose and light - any data is good data, we are not the jury until both you
and I have exposed it to the light and talked about it"*.

This file is the ledger. Every mechanic added, every mechanic removed, and **why** — including the
ones removed because our own measurements killed them rather than because they were awkward to build.

Scoring unlocked this run: **MAE and MFE**, plus `ret` at the exit bar. Joe 0804 lifted the MAE-only
restriction for this task after establishing that MAE cannot rank an exit (it is monotone in hold
length, so it ranks exits by earliness and nothing else).

---

## Population and baseline

| | |
|---|---|
| trades | 849 — every `s46_run` row passing gates 5 and 14 |
| span | 05-18 01:45 → 07-31 21:19, 74.8 days |
| baseline | `s6raw` — the live exit, s6x crossing s6Mage, lookback 72 bars, wob 3. **Unchanged.** |
| IS / OOS | chronological 50/50 by trade count, 424 / 425 |
| windows | 11 × 7-day non-overlapping, plus 21 × 7-day overlapping at 3.5-day stride |

---

## ADDED — exit legs

13 legs, each a (crossing line, target) pair. LONG closes on a DOWN cross, SHORT on UP —
`build_s46.py`'s own rule, unchanged.

| leg | crossing | target | note |
|---|---|---|---|
| x15b x15r x15M | s15x | boundary / s15r / s15Mage | |
| x22b x22r x22M | s22x | boundary / s22r / s22Mage | |
| x30b x30r x30M | s30x | boundary / s30r / s30Mage | s30 pair reached Joe's 04:00 mark in 0.83 native bars |
| x15r30 x22r30 | s15x, s22x | **s30r** | Joe: *"use a HTF to smooth the s15's volatility"* — s30r measured 4.6× narrower in range than s15r and halved the sub-3-bar blips on the s15 leg |
| x15M30 x22M30 | s15x, s22x | **s30Mage** | the Mage analogue of the same idea |

Lines are exhv2's own specs: `x` bb 4|0.37|close, `M` bb 37|0.70|close, `r` kline 10|4|11|close.

---

## ADDED — five confirmation mechanics, composable

All five act on the same crossed-side signal, so they can be combined freely.

### 1. Hysteresis `H` — the Schmitt trigger
Latch: set when `dd > +H`, clear when `dd < -H`. `H=0` degenerates to the plain cross.
**Why added**: a time debounce costs lag on *every* cross; an amplitude band costs nothing on a
decisive move and everything on a marginal one. Standard engineering answer to contact bounce.
**Known weakness, recorded before the run**: the 03:03:25 blip cleared its boundary by 0.572 points
and reverted in 2 bars; the 82-bar move at 03:07:20 cleared it by *the same* 0.572. So H alone cannot
separate those two. Kept because it is free and composes.
Grid: 0, 1, 2, 3, 5, 8, 13, 21 board points.

### 2. Clock wobble — the existing mechanic
`n` consecutive 5 s bars held. Unconditional lag of `n × 5` s.
Grid: 1, 2, 3, 6, 12, 24, 48, 96, 180, 360 bars.

### 3. Event wobble — count event bars, not clock bars
`n` bars carrying volume > 0, elapsed inside the run.
**Why added**: the decile census over 4,419 pierces put the busiest tenth of the tape at a **42.5%**
blip rate against **24.1%** in the quietest, `d10/d1 = 1.77` at every window from 1 to 22 min.
López de Prado: time bars oversample ~70% of low-activity periods and undersample volatile ones.
Grid: 1, 2, 3, 6, 12, 24, 48, 96 event bars.

### 4. Directional event wobble — run bars
Count only the event bars whose **tick rule** sign agrees with the exit direction.
**Why added**: run bars close on bursts of *one-sided* activity even when the other side is also
active; a plain event count cannot tell a one-sided burst from two-sided churn.
Grid: 1, 2, 3, 6, 12, 24, 48.

### 5. Volume clock, and signed-volume run
Cumulative traded volume inside the run, in multiples of the tape's median non-zero 5 s volume.
`dvol` is the same restricted to volume whose tick agrees with the exit direction.
**Why added mid-run**: see the correction below — the binary event flag turned out to be near-constant
over half the tape, while volume *magnitude* varies everywhere (median 401, p90 17,460).
Grid: vol 1,2,3,6,12,24,48,96 · dvol 1,2,3,6,12,24,48.

---

## ADDED — the momo gate (stage B)

`build_exhv2.momo()` state banked per bar, per TF, per direction. Joe 0804 locked the semantics:
**either** of the chosen TFs opens it, read every bar from entry, **curl counts as well as momo**.
While open, the s6 baseline is suppressed and the race legs are armed.

Swept: TF set {15} {22} {30} {15,22} {15,22,30} · states {momo} {momo,curl} · gate wobble 1/12/24/72
bars · s6 raced vs s6 as fallback only.

## ADDED — leg races (stage C)
Every subset of the six surviving legs, each at its own best mechanic. First leg to confirm wins.

## ADDED — price-path exits (stage D)
Joe's own inventory, **never built until this run**:
- item 12 — *"which TP would produce the most return if we had a 0.3 or 0.4 stop"*
- item 11 — *"> 0.75 MFE to the swing detect 1% pivot"*; `TRAIL` is its causal cousin

`TP` 0.15→3.00 · `STOP` 0.15→1.00 · `TRAIL` (give-back from running MFE) 0.10→1.00, each with a
`None` arm. TRAIL only arms once the trade is in profit, so it can never fire before the first
favourable bar. **No horizon cap** — the s6 baseline is always available as a terminator, so every
trade ends without a truncation being imposed.

---

## REMOVED — and why

| removed | reason |
|---|---|
| **Efficiency-ratio / KAMA adaptation** | Our own census kills it. `chop` (= 1/ER) separates blips from real moves at ratio **1.02** over 4,419 pierces. The literature's most-cited answer to this exact problem is contradicted by our measurement, so building it would be following a citation instead of data. |
| **Direction-change count as a regime gate** | Runs **backwards**: 41.7% blip rate in the calmest decile vs 25.4% in the choppiest, `d10/d1 = 0.61`. Falsifies the "ton of retests" reading outright. |
| **`chop` = path ÷ net as a gate** | 1.02 at 15 min, 0.99 at 3 min. Separates nothing. |
| **VPIN / order-flow toxicity** | `ticks` carries `tk_side` (signed volume) but only spans **07-28 → 07-31**, four days of a 75-day study. Cannot be tested at this scale. Noted for later. |
| **s15Mage / s22Mage from the *race*** | Joe 0804 pulled them while investigating the earlier-than-00:40 signal. They remain **banked** in `s46_momo_leg`, and `x15M`/`x22M` are still carried in this run's leg set as measurement — the removal was from the live race, not from the evidence. |
| **`xwob` as the sole answer to blips** | Measured dead end. On the 20-trade window MAE degraded monotonically with `xwob` (0.134 → 0.214) and by `xwob` 18 the mechanic was worse than doing nothing. The gain *was* the piercing. |
| **s6-as-a-racer in stages A/B/C** | Replaced with **s6-as-fallback**: s6 is used only when the leg never fires. Racing s6 means the leg can only ever pull the exit *earlier*, which silently forbids the hold-longer direction that is the entire point. |

---

## CORRECTIONS made during the run

1. **The event flag was near-constant.** Built from the jig's `base['volume'] > 0`, it read **1.000
   for the whole of May** and 0.676 in late July — a jig-window artefact. `kline_collection` says the
   true figure is **10.9% zero-volume bars** across the tape. Fixed by pulling `kc_volume` straight
   from the DB, and by adding the volume clock, which uses magnitude rather than a binary flag and
   therefore varies everywhere. Without this catch, mechanics 3 and 4 would have silently
   degenerated to the clock wobble over half the tape and been reported as "no different".

2. **`n` column collision.** `agg()` sets `n` = trade count; stage A was overwriting it with the
   wobble size, so every reported `n` was the knob, not the sample. Renamed to `wn`.

3. **Registry write race.** `linelab.register()` does a non-atomic `json.dump` of a shared registry
   at import time. Three parallel chunk builds read it mid-write and one died. Joe's `linelab.py` is
   **untouched** — worked around by staggering process launches 30 s apart. The bug is real and worth
   a separate atomic-write fix.

4. **Chunked line build.** One jig pass at TF30 over 75 days needs ~100 GB. Built in 19 chunks of
   4 days behind 2 days of warmup lead-in, stitched on `ts`. 48 h of lead-in against the 18.5 h a
   bb 37 at TF30 requires.

---

## Standing caveats

- IS/OOS is one chronological split. Any config selected on the full tape has been fitted twice.
- The 7-day window pass exists precisely because Joe expects OOS to stagnate: *"if the OOS results
  don't improve in a way that you were hoping for, that is data: it means we need to add new mechanics
  to sections of the full window."*
- No config in this run is a recommendation. The jury is Joe and me, after we have both looked.

---
---

# CHECKPOINT 1 — stages A/B/C/D/W complete, 04:29 → 05:10

Joe 0804: *"every turn has checkpoint documentation"*. Numbers, not verdicts.

## Baseline, full tape, 849 trades

| | n | MAE mn | MAE max | MFE mn | ret mn | ret sum | win% | hold |
|---|---|---|---|---|---|---|---|---|
| full | 849 | 0.253 | 1.234 | 0.466 | +0.007 | +6.4 | 37.0 | 153 |
| IS | 424 | 0.269 | 1.224 | 0.480 | −0.008 | −3.6 | 37.7 | 156 |
| OOS | 425 | 0.237 | 1.234 | 0.453 | +0.023 | +9.9 | 36.2 | 150 |

## Stage A — 4,160 configs, legs x mechanics x hysteresis

- best: `x15M30 H2 clock360` → ret +0.205, sum **+173.7**, MAE 1.159, MAE max 17.745, hold 2,156
- **beat baseline IS 99.2%; of those held OOS 9.6%; IS/OOS correlation −0.021**
- **mechanic marginals FLAT**: at n=1 clock +0.022 / event +0.022 / direv +0.023 / vol +0.019 / dvol +0.021
- **hysteresis FLAT**: H=0 +0.015 → H=21 +0.013 across 520 configs each
- **leg is what matters**: x30M +0.034, x22M +0.033, x15M +0.030 vs x30r −0.007, x22r +0.001
- all three Mage targets beat all three r targets and all three boundary targets

## Stage B — 480 gate configs

- best: `x15M30 H2 clock360 | G30 momo gw72` → ret **+0.432**, sum **+366.8**, MAE 1.920, hold 4,553
- **beat baseline IS 93.1%; of those held OOS 67.3%** (stage A was 9.6%)
- top config OOS (+0.432) **exceeds** its IS (+0.408)
- G30 dominates G22; G15 absent from top 25
- `momo` alone > `momo+curl` on ret; `momo+curl` runs MAE 1.454 vs 1.920 and hold 3,130 vs 4,553

## Stage C — 126 leg-subset races. STRICTLY HARMFUL, monotone.

| legs | best ret | best OOS ret |
|---|---|---|
| 1 | +0.205 | +0.183 |
| 2 | +0.174 | +0.114 |
| 3 | +0.146 | +0.063 |
| 4 | +0.134 | +0.035 |
| 5 | +0.110 | +0.021 |
| 6 | +0.093 | +0.018 |

A race takes the FIRST confirmation, so more legs can only pull the exit earlier. **Kills the
six-leg race construction built earlier in the session.**

## Stage D — 4,572 TP/stop/trail configs

- **STOP always costs**: none +0.039; 0.15 +0.009; 0.30 +0.016; 0.40 +0.020; 1.00 +0.030.
  Joe's item-12 question answered: a 0.3/0.4 stop costs ~half the return of no stop.
- **TP optimum 0.40–0.75**, peak 0.50 at +0.026 vs none +0.017
- **TRAIL (absolute) 0.50 best** at +0.035 vs none +0.021
- **TRAILF (proportional, fraction of MFE peak) FAILS**: 0.50 → +0.018, 0.90 → +0.020, vs none
  +0.023. The trade-journal literature's "50% pullback from MFE" rule is below no-trail here,
  though it gives the study's highest win rates (61.8%) by cutting holds to 17 bars.
- best: `x15M H8 clock360 | tp0.50` → ret +0.150, sum +127.5, **win 73.3%**, MAE 0.700, hold 730

## Stage W — 11 non-overlapping + 22 overlapping 7-day windows

- gated config beats baseline in **11 of 11** windows; ungated loses in w3 (−0.186) and w9 (−0.256)
- change points on the gated config:

| seg | from | to | n | ret mn | ret sum | win% |
|---|---|---|---|---|---|---|
| s2 | 05-31 16:41 | 06-04 00:17 | 41 | **−1.055** | **−43.3** | 41.5 |
| s4 | 06-13 21:12 | 06-15 10:01 | 21 | **+4.625** | **+97.1** | 85.7 |
| s6 | 06-21 18:01 | 07-11 19:35 | 234 | +0.786 | +184.0 | 61.5 |
| s7 | 07-12 11:42 | 07-31 21:19 | 224 | **+0.048** | **+10.8** | 52.7 |

**26% of the population sits after 07-12 and contributes 3% of the profit.**

---

# CHECKPOINT 2 — what changed on 07-12

Joe's gut was "volatile price swings". **Inverted by the data.**

| measure | PRE (625) | POST (224) | POST/PRE |
|---|---|---|---|
| ret mean % | +0.534 | +0.100 | 0.19 |
| ret sum % | +334.1 | +22.4 | 0.07 |
| win % | 59.0 | 49.6 | 0.84 |
| MAE mean % | 1.958 | 1.237 | 0.63 |
| MFE mean % | 2.399 | 1.391 | 0.58 |
| AVAILABLE MFE mean % | 2.558 | 1.615 | 0.63 |
| MFE captured / available % | 93.8 | 86.2 | 0.92 |
| px vol per 5 s bar % | 0.0481 | 0.0314 | **0.65** |
| px path length per day % | 478.5 | 302.3 | 0.63 |
| px range over period % | 71.9 | 29.7 | 0.41 |
| **median non-zero volume** | **6,403** | **2,098** | **0.33** |
| **zero-volume bars %** | **3.1** | **31.9** | **10.28** |
| G30 momo gate open % | 29.7 | 29.0 | 0.97 |
| trades / day | 11.4 | 11.5 | 1.01 |

- **volatility FELL 35%. Liquidity collapsed**: trade size −67%, empty bars 10.3×
- opportunity fell to 63%; capture held at 86–94%; **return fell to 19%**
- efficiency `ret ÷ MFE`: 0.223 → 0.072, a **68% collapse** beyond the shrinkage
- the liquidity drain **precedes** the change point — volume already halved by 07-05

---

# CHECKPOINT 3 — PRE/POST marginals. MY HYPOTHESIS FALSIFIED.

I predicted the pooled stage-A result hid the event/volume clocks, because PRE has only 3.1%
zero-volume bars. **Recomputed on POST (31.9% empty bars): still flat.**

Matched-n POST ret, all five mechanics within **0.005** at every n:

| n | clock | event | direv | vol | dvol |
|---|---|---|---|---|---|
| 1 | +0.002 | +0.002 | +0.004 | −0.001 | +0.001 |
| 12 | −0.008 | −0.009 | −0.008 | −0.007 | −0.007 |
| 48 | −0.004 | −0.001 | −0.020 | −0.019 | −0.019 |

**Verdict: sampling on activity instead of the clock does not help, even in the regime it was
designed for. The tangent is closed.** Cost: ~40 min of build time. Worth it — it removes an idea
that four separate literature sources endorsed.

## What DID flip at 07-12

| clock n | PRE ret | POST ret |
|---|---|---|
| 1 | +0.029 | +0.002 |
| 180 | +0.037 | −0.032 |
| **360** | **+0.074** | **−0.059** |

| leg | PRE ret | POST ret | PRE win% | POST win% |
|---|---|---|---|---|
| **x15M** | **+0.025** | **+0.042** | 40.3 | **40.5** |
| x22b | +0.026 | +0.018 | 34.6 | 31.5 |
| x15r30 | +0.023 | +0.017 | 37.3 | 34.4 |
| x15M30 | +0.029 | **−0.017** | 40.2 | 34.9 |
| x22M30 | +0.043 | −0.023 | 38.8 | 34.9 |
| **x30M** | **+0.066** | **−0.053** | 38.6 | 30.5 |

- **PRE/POST config-ret correlation −0.176** — configs that work before tend to FAIL after
- **x15M is the only leg materially positive in both**, and the only one whose win rate holds
- POST top-20 configs are **all x15M**, holds 284–359 bars (24–30 min), MAE 0.26–0.31
- the +366.8 headline is a PRE artefact and must not be carried forward

---

# NEXT THREAD — causal liquidity regime switch

Hypothesis: zero-volume-bar share and median trade size are measurable **at the entry bar** with no
lookahead, and conditioning the config on them recovers part of the June-scale edge.
Status: building.

---

# CHECKPOINT 4 — causal liquidity regime switch. HYPOTHESIS FALSIFIED.

`zero_48h` = trailing 48 h share of zero-volume bars, measured AT THE ENTRY BAR, no lookahead.

| feature | PRE mean | POST mean | ratio | AUC |
|---|---|---|---|---|
| zero_1h | 0.0324 | 0.3461 | 10.68 | 0.969 |
| zero_24h | 0.0274 | 0.3216 | 11.73 | 0.988 |
| **zero_48h** | **0.0255** | **0.3214** | **12.59** | **0.994** |
| mvol_48h | 16,908 | 8,217 | 0.49 | 0.030 |

**The detector works (AUC 0.994). The switch it enables does not.**

| rule | IS ret | OOS ret |
|---|---|---|
| always LIQUID (x15M30 H2 clock360 + G30) | +0.408 | **+0.432** |
| always THIN (x15M H13 clock12) | +0.033 | +0.026 |
| switch at ANY IS percentile 10→90 | +0.408 | **+0.244** |

Switching HALVES OOS. Reason: LIQUID beats THIN in every liquidity decile including the thinnest
(d10 median zero_48h 0.378: LIQUID +0.327 vs THIN +0.162). **The premise was wrong.**
Cost ~15 min. Worth it — closes the liquidity-conditional-exit question.

Correction logged: the leg marginal for x15M30 was −0.017 POST, but the TUNED config returns
**+0.100** POST, not negative. My "PRE artefact" phrasing overstated it.

New candidate surfaced: **MID = x15M H8 clock360 + G30** — PRE +0.390 / POST +0.183, against
x15M30's +0.534 / +0.100. Gives up 27% of PRE to nearly double POST.

---

# CHECKPOINT 5 — SANITY CHECK against the origin trade (Joe asked)

Origin: 07-29 03:03:15 SHORT. Joe's marks 04:00 (estimate) and 04:16.

| config | exit | ret % | vs 04:16 |
|---|---|---|---|
| BASELINE s6raw | 03:08:45 | −0.227 | −4035 s |
| **A x15M30 H2 clock360** | **04:14:55** | **+2.304** | **−65 s** |
| B A + G30 gate | 13:55:25 | +1.093 | +34765 s |
| THIN x15M H13 clock12 | 03:45:55 | +1.527 | −1805 s |

**The 12-week sweep's mean-return winner lands 65 s from Joe's hand-read exit, having never seen
this trade.** But the GATE — the thing that doubled the population return — holds it 10.9 hours and
gives back half the move. Population optimum and chart read disagree sharply on the one case we
both understand.

---

# CHECKPOINT 6 — what the gate actually does, trade by trade

- changes the exit on **319 of 849 = 37.6%**; of those **318 LATER, 1 earlier**. Purely hold-longer.
- entire +182.8 contribution: top 10 exits = 40.6%, top 20 = 72.8%; worst 20 = −111.8
- helps 196 (23.1%), hurts 123 (14.5%), **median delta +0.000**
- top contributors are NEAR-DUPLICATE TRADES SHARING ONE EXIT BAR:
  06-23 00:38 / 01:36 / 03:03 all exit 06:44:55 → +19.2 from one move
  06-01 00:04 / 00:10 / 00:13 all exit 21:21:10 → −14.8 from one move

---

# CHECKPOINT 7 — RE-SCORED PER EXIT BAR (Joe's standing memory, not applied until now)

| config | rows | ret sum ROW | exits | ret sum EXIT | n/exit | rows in dupes |
|---|---|---|---|---|---|---|
| BASELINE | 849 | +6.4 | 712 | +12.5 | 1.19 | 30.2% |
| A x15M30 H2 clock360 | 849 | +173.7 | 521 | +71.6 | 1.63 | 62.1% |
| **B A + G30** | 849 | **+356.4** | **360** | **+125.7** | **2.36** | **84.3%** |
| MID x15M H8 clock360 G30 | 849 | +284.5 | 381 | +108.1 | 2.23 | 82.1% |

**Gate delta falls from +182.8 (per row) to +54.1 (per exit) — 30% of what it looked like.**
The gate CAUSES the duplication: holding longer means more entries fall inside one open position.
**Ranking survives; magnitudes do not.** B's OOS still exceeds its IS per exit (+0.379 vs +0.326).

---

# CHECKPOINT 8 — mean vs median as a PnL number (Joe asked)

| config | n exits | mean | median | SUM | trim10 | t = mean/SE |
|---|---|---|---|---|---|---|
| BASELINE | 712 | +0.017 | **−0.112** | +12.5 | **−0.033** | **0.83** |
| A | 521 | +0.137 | **−0.149** | +71.6 | +0.044 | 1.80 |
| **B** | 360 | +0.349 | **+0.209** | +125.7 | +0.324 | **2.86** |
| MID | 381 | +0.284 | **+0.186** | +108.1 | +0.231 | **2.66** |
| THIN | 707 | +0.042 | **−0.112** | +29.3 | −0.018 | 1.50 |

- PnL is additive → **the SUM is the number**; mean is sum/n and carries the same information
- **median is the wrong thing to optimise and the right thing to check.** Baseline, A and THIN all
  have positive means with NEGATIVE medians — most exits lose and a few winners carry the total
- baseline top 1% of exits = **164.5% of its entire sum**. B's top 1% = 19.2%
- only B (t 2.86) and MID (t 2.66) clear t=2. **The baseline's own edge is indistinguishable from zero**
- compounding at 1×: B 125.7% → **218.8%** (right-skewed, helps); baseline 12.5% → 12.0%

**Standing rule adopted: report SUM, median, tail share and t together. Mean alone said the
baseline makes money; median, trimmed mean and t all say it does not.**

---
---

# CHECKPOINT 9 — THE DATA DEFECT. Read this before trusting anything above.

Joe 0804 asked whether the July anomaly was a kline problem. It was, and it invalidates the
PRE/POST framing that checkpoints 2, 3 and 4 are built on.

## Root cause — confirmed by source, not inferred

`SyntheticBackfiller` (optimus9/data/synthetic_backfiller.py) fetched Bybit **1 m** bars and split
each into twelve 5 s children via `SyntheticBarBuilder.split()`, which writes
**`unit_v = round(V / 12, 8)`** to every child. So its phantom bars carry **volume > 0**.

Its own docstring: *"SUNSET (Joe 2026-07-05): the 1m→12×5s split produces phantom flat filler bars
that drift oscillators into false reversals (o9-live 07-04, see project_filler_invisible)."*
Auto-backfill DISABLED at run.py:435-439.

`filler_invisible` (bias_machine.py:141-146) — the protection built for exactly this — keys on:

```python
_m = self.base['volume'].to_numpy(dtype=float) > 0    # real-trade bars only
```

**It therefore cannot see them.** It was written for BarBuilder's `V=0` carry-forwards.

`KlineSanitiser` then repaired the OHLC to TV truth, but its UPDATE (kline_sanitiser.py:116) sets
`kc_open/high/low/close` ONLY and never touches `kc_volume`.

## Exonerated — verified, not assumed

| component | evidence |
|---|---|
| BarBuilder | `open == prev close` in **100.00%** of 29,519 bars — a convention, not a fault. All 10 strategy sources are `src='close'`; close is **bit-exact** vs a raw-tick rebuild (100.00%, max \|Δ\| 0.0000%). Volume sums identical to the unit: 245,261,314 vs 245,261,314. Its no-trade bars are `V=0` and ARE correctly hidden. |
| KlineAuditor | read-only. 12-bar blocks share a close in **0.2%** of its window (a write-back would be ~100%). Tick agreement inside its window is 100% on close. |
| KlineSanitiser | remediation. The `flat` action is the correct gap-fill for bars TV omits (kline_sanitiser.py:92-98) — TV emits 26,257 bars where the 5 s grid has ~38,000. |

## The measured damage

| window | bars | flat OHLC | zero-vol | **flat + V>0 → fed to the lines as real** |
|---|---|---|---|---|
| 05-18 → 07-02 sanitised | 587,521 | 30.0% | **0.0%** | **175,970 = 30.0%** |
| 07-03 → 07-29 collector | 681,601 | 30.8% | 19.4% | 77,285 = 11.3% |
| 07-30 → 08-01 | 26,881 | 47.9% | 30.9% | 4,616 = 17.2% |

- all **95,171** sanitiser `flat` rows carry volume > 0, mean **7,366**
- the flat-bar RATE is the same in both halves (30.0% vs 30.8%) — only the filter's ability to see
  them differs
- **this is what the 07-12 change point found.** Not liquidity, not volatility, not the market

## Corrections to earlier checkpoints

1. CHECKPOINT 2's "liquidity collapsed 67%, empty bars 10.3×" — **artefact**. Volume in May–June is
   1 m volume divided by 12 (`.83333` decimals) or repeated (91.7% consecutive duplicates).
2. CHECKPOINT 4's `zero_48h` regime detector, AUC 0.994 — **detects the backfiller stopping**, not
   a market regime.
3. My "the sanitiser rewrote 89,171 closes" alarm — **backwards**. `old_c` was the synthetic ramp;
   `new_c` is TV truth. The sanitiser was repairing, not corrupting.
4. My "flat OHLC substitutes for volume" claim — **wrong**. In the clean window 12.8% of flat bars
   actually traded, all at one price.
5. CHECKPOINT 3's finding that the event/volume/run-bar clocks are flat — **SURVIVES**. That test
   was POST-only, on real collector volume.

## The fix

1. `kline_sanitiser.py` — on the `flat` branch only, also write `kc_volume = 0`. A carry-forward
   flat bar is by definition a no-trade bar. Do NOT zero volume on `tv` rows.
2. Retroactive: `UPDATE kline_collection SET kc_volume = 0` for the 95,171 `action='flat'`
   timestamps. **No CSVs needed for this part.**
3. **CLEAR `.rpl_cache` FIRST.** `cache_key`/`_tape_key` (rpl_cache.py:15-16, 30-31) hash only
   `end_ms|hours|warmup|pxs_cfg` — never the data. `__evt__` is the cached `volume > 0` array the
   fix changes. A rebuild would look clean, run fast, and reuse the contaminated tape.

## Reach of the fix

| consumer | event-tape? | fixed |
|---|---|---|
| all bb/kline lines via BiasWindow | yes, `filler_invisible` | **yes** |
| `pxs` via `_px_smooth_evt` (rpl_cache.py:59-64) | yes, same `volume > 0` test | **yes** |
| `s46_px` | yes, built the same way | yes, after rebuild |
| **`bl_detect.py:261` → `bl_states.px_smooth`** | **no evt mask at all** | **NO — separate defect** |

## Status of the 0804 permutation run

- price series: **sound** — TV truth where TV traded, carry-forward flat where it did not
- the leg ranking, the gate result, the per-exit rescoring: computed on a tape whose event mask was
  30% contaminated before 07-03 and 11% after. **Re-run required, ~40 min, after tasks 1-3.**
- the origin trade 07-29 03:03:15 sits in collector data — that result is unaffected

---
---

# CHECKPOINT 10 — THE REPAIR. Executed 0804 09:00-09:20 while Joe slept.

Joe delivered 21 TV CSVs to `transfer/kline_sanitise/260804_refit/` and handed over the con.

## Code changed — `optimus9/data/kline_sanitiser.py` (backup: $JB/tmp/kline_sanitiser.py.bak)

| # | change | why |
|---|---|---|
| 1 | `parse()` reads Volume **by column NAME**, not position | 21 of 33 files in `processed/` carry `BB1,BB2,K2` or `DEMA,BB1,BB2,K2` where Volume should be. `x[5]` would have imported a **Bollinger value as volume**. Missing → 0.0 |
| 2 | `_to_5s()` **sums** volume on 1s→5s aggregation | it previously dropped it |
| 3 | `flat` branch writes **`kc_volume = 0`** | a carry-forward bar is by definition a no-trade bar. THE FIX |
| 4 | `tv` rows carry the CSV's Volume on INSERT | `INSERT` previously hardcoded `kc_volume = 0`, which would have hidden EVERY bar of a deleted-and-reloaded range |
| 5 | `write_tv_volume` flag, default **False** | ESCALATED. Joe chose *"delete the rows before passing in the csv file"*, so it never engaged |
| 6 | `kline_sanitise_log` gains `old_v` / `new_v` | the file's own contract is "every change → log, reversible" |
| 7 | **writes batched** into chunked `executemany` | was 1 round-trip per bar ≈ 4k rows/min → the 16-file refit measured **2h+**. Now ~2 min. Same semantics |

## Data operations

| op | result |
|---|---|
| backup | `$JB/tmp/dbbak/kc_0625_0801.npz` — 656,640 rows of pre-change OHLCV |
| reload | 16 files (4 md5 duplicates + the 08-02→08-04 live-territory file skipped). Range deleted, then reconciled so every row is an INSERT carrying TV's volume. **580,334 deleted / 587,519 inserted** |
| retro | 05-18 → 06-25 has no refit CSV. Authority = `kline_sanitise_log`, latest action per timestamp. **106,396 bars** with latest action `flat` set to `kc_volume = 0` |
| cache | `.rpl_cache` deleted — **98 GB**, 23 line npz + 12 tape npz. Manifest at `$JB/tmp/cache_manifest.txt` |

## The measured repair — empty-bar share, the thing `filler_invisible` keys on

| window | before | **after** |
|---|---|---|
| 05-18 → 06-25 | **0.0%** | **16.4%** |
| 07-03 → 07-30 | 19.4% | **27.8%** |
| PRE/POST gap | 0.0 vs 31.9 | **16.4 vs 27.8** |

The residual gap is explained: May–June was genuinely more active (mean volume 14–54k vs 6–12k),
so it really does have fewer empty bars.

## Verified NOT residue

- only **10,683 of 87,683** remaining flat-with-volume bars sit in a ruler-line minute
- clean TV reloads show **35.0% / 36.2% / 78.6%** of flat bars carrying volume, so May–June's
  **45.6%** is normal. Those are genuine one-price trade bars, which TV reports too
- deleting cost **~94 real-volume bars across 27 days = 0.013%** (measured before deleting:
  208,211 DB-only bars, only 7,789 with volume, and 7,695 of those were the phantom `V/12`)

## Still open

- `bl_detect.py:261` computes `px_smooth` over the full base with **no evt mask** — separate defect,
  `bl_states.px_smooth` stays contaminated. Not touched
- `write_tv_volume` remains OFF — Joe's call if he wants TV volume overwriting collector volume on
  existing rows
- the daemon was **never stopped and the watch folder never used** — `reconcile()` was called
  directly, so `kline-sanitise.service` (PID 602) kept running the old module harmlessly

## Rebuild chain now running

1. `.rpl_cache` cleared ✔
2. `build_s46.py` — s46_px / s46_run / s46_exit / s46_revtrig, all built on the OLD tape ← running
3. `build_s46_lines.py` — 19 chunks of TF15/22/30 lines
4. `sweep_s46_exit.py --stage ALL` — the full A/B/C/D/W rerun

**Every number in checkpoints 1-8 was computed on the contaminated tape. The rerun replaces them.**

---
---

# CHECKPOINT 11 — THE CLEAN-TAPE RERUN. The repair changed almost nothing.

Sweep ran 09:42 → 09:53 on the rebuilt tape. 854 trades (was 849).

## Stage-by-stage, contaminated vs clean

| measure | contaminated | **clean** |
|---|---|---|
| baseline ret mean / sum | +0.007 / +6.4 | **+0.006 / +4.9** |
| baseline MAE mean | 0.253 | **0.254** |
| A best config | x15M30 H2 clock360 | **same, same rank** |
| A best ret mean / sum | +0.205 / +173.7 | **+0.194 / +165.7** |
| A beat baseline IS | 99.2% | **99.0%** |
| **A held OOS** | **9.6%** | **8.0%** |
| **A IS/OOS correlation** | **−0.021** | **−0.068** |
| B best ret | +0.432 | **+0.423** |
| **B held OOS** | **67.3%** | **57.9%** |
| C 1 leg / 6 legs best OOS | +0.183 / +0.018 | **+0.146 / +0.013** |
| D STOP none / 0.30 / 0.40 | +0.039 / +0.016 / +0.020 | **+0.035 / +0.015 / +0.018** |

**The baseline barely moved because it exits in ~13 min — filler bars never accumulate inside its
holding period. So the yardstick is unchanged and only the long-hold candidates could have moved.
They did not.**

## Mechanic marginals — FLAT for the third independent time

Clean tape, n=1: clock +0.017 · event +0.017 · direv +0.018 · vol +0.015 · dvol +0.016.
Spread 0.003 across all five. **Event clocks, run-bar clocks and volume clocks are definitively
dead.** Tested (1) pooled contaminated, (2) POST-only contaminated, (3) pooled clean.

## The 07-12 break is REAL, not a data artefact

| config, per exit | PRE mean | POST mean | PRE med | POST med |
|---|---|---|---|---|
| BASELINE | +0.012 | +0.028 | −0.123 | −0.096 |
| B x15M30 H2 c360 G30 | +0.408 | +0.145 | +0.301 | **−0.019** |
| x15M H13 c360 G30 | +0.280 | +0.168 | +0.192 | **+0.082** |

Baseline change points came back **bit-identical** to the contaminated run.
B's IS/OOS now nearly equal: **+0.364 / +0.350**.

---

# CHECKPOINT 12 — LIQUIDITY, REOPENED ON CLEAN DATA. Definitively closed.

Design note: zero-bar share is trustworthy everywhere now (flat bars zeroed from the log). Volume
MAGNITUDE is still synthetic before 06-25 (only flat rows were zeroed; tv rows keep V/12), so every
feature is built from ZERO-BAR SHARE, never volume size.

The causal trailing zero-share still separates the periods — 48 h window, PRE 0.1503 vs POST 0.3187,
**AUC 0.950**. But:

## The decisive test — terciles computed WITHIN each period

| config | period | thick | mid | thin |
|---|---|---|---|---|
| B gated | PRE | +0.346 | +0.711 | +0.527 |
| B gated | POST | +0.008 | +0.059 | **+0.201** |
| x15M H13 G30 | PRE | +0.344 | +0.365 | +0.167 |
| x15M H13 G30 | POST | +0.196 | +0.218 | **+0.298** |

- **no monotone relationship in either period**
- inside POST the THINNEST tercile is the BEST for both gated configs — opposite of the hypothesis
- ret↔liquidity correlation: **−0.021 pooled, +0.032 within-PRE, +0.075 within-POST**. Zero.

**VERDICT: 07-12 is a DATE BREAK. Liquidity is coincidental with it, not causal.**
Correction to checkpoints 2 and 4: I called the liquidity collapse entirely an artefact. The
MAGNITUDE was fake (0.0% empty bars is impossible) but PRE 16.4% vs POST 27.8% is real. Activity
genuinely fell 1.7×. It just does not explain the returns.

---

# CHECKPOINT 13 — DECOMPOSING THE BREAK. It is a WIN-RATE collapse.

## The tape got harder, not just smaller

| | PRE | POST | ratio |
|---|---|---|---|
| px vol per bar | 0.04793% | 0.03145% | 0.66 |
| daily path | 471.5% | 302.9% | 0.64 |
| available MFE (4.6 h) | 2.099% | 1.368% | 0.65 |
| available MAE (4.6 h) | 1.962% | 1.450% | 0.74 |
| **MFE:MAE ON OFFER** | **1.070** | **0.944** | **0.88** |

POST, the average trade has MORE adverse than favourable excursion available. The shape worsened,
not just the scale.

## Where each config loses

| config | period | ret mn | **win%** | W mean | L mean | **W:L** |
|---|---|---|---|---|---|---|
| B | PRE | +0.528 | **58.9** | +2.141 | −1.788 | **1.20** |
| B | POST | +0.089 | **49.1** | +1.359 | −1.137 | **1.20** |
| x15M H13 | PRE | +0.292 | **54.5** | +1.828 | −1.547 | 1.18 |
| x15M H13 | POST | +0.237 | **54.4** | +1.250 | −0.970 | **1.29** |

- **B's W:L is IDENTICAL at 1.20 in both halves.** Winner and loser sizes both fall ~0.63×, matching
  the tape exactly. The entire loss is **win rate: 58.9 → 49.1**
- **x15M H13's win rate is FLAT: 54.5 → 54.4**, and its W:L IMPROVES 1.18 → 1.29
- degradation: B −83% (+0.528 → +0.089), x15M H13 −19% (+0.292 → +0.237)

**This reverses the ranking. Ranking on pooled mean picks B; ranking on survival picks x15M H13.**

New objective adopted: WIN-RATE STABILITY across the break, not mean return. Sweep running.

---
---

# CHECKPOINT 14 — THE 05-31 EVENT. Bit-stable across the rebuild; a real, dated, hostile setup.

Joe quoted this from the contaminated run and asked whether it is still worth working on.
Re-derived on the clean tape, on TWO different configs:

| | contaminated B | clean B | clean x15M H13 |
|---|---|---|---|
| dates | 05-31 16:41 → 06-04 00:17 | **identical** | **identical** |
| n | 41 | **41** | **41** |
| ret sum | −43.3 | **−45.5** | **−41.9** |

Same 41 trades, same boundaries, after 587,519 bars were replaced and 106,396 zeroed.
**The most reproducible finding in the study.**

## What the 41 trades actually are

| | 05-31 event (41) | all other trades (813) |
|---|---|---|
| available MFE (4.6 h) | 1.635% | 1.917% |
| **available MAE** | **3.651%** | 1.733% |
| **MFE:MAE ON OFFER** | **0.448** | **1.106** |

The market offers **2.2× more adverse than favourable** movement to these entries. Direction split
is even (21 LONG / 20 SHORT), so it is not a one-sided trap.

Tape in the window: vol/bar **0.04884%** (vs 0.04424% average) · daily path **530.8%** (vs 430.5%) ·
net move **−6.84%** in 3.3 days · zero-vol **11.4%** (vs 19.6%). A fast, active, directional decline —
**more liquid than average**, which kills the liquidity reading a second time.

## THE BASELINE IS FINE IN IT

| config | n | sum | mean | win% | n/exit | hold |
|---|---|---|---|---|---|---|
| BASELINE | 41 | **+1.03** | +0.025 | 48.8 | 1.24 | 184 |
| B gated | 41 | **−45.50** | −1.110 | 39.0 | **2.41** | 6032 |
| x15M H13 | 41 | **−41.90** | −1.022 | 39.0 | 2.16 | 4818 |

The 15-minute exit MAKES MONEY here. Only the long holds are destroyed.

## Two exit bars carry almost all the damage

| entries | shared exit | each | total from ONE move |
|---|---|---|---|
| 06-03 21:35, 21:43, 06-04 00:14, 00:17 | 15:00:05 | −8.09 −7.96 −8.65 −8.62 | **−33.3** |
| 06-01 00:04, 00:10, 00:13, 03:07 | 21:21:10 | −5.82 −5.83 −5.85 −5.92 | **−23.4** |

---

# CHECKPOINT 15 — ITEM 15, NO-PYRAMIDING. Built for the first time. MAJOR NEGATIVE.

Joe's inventory item 15, specified 0803, never built. Rule: walk trades in time order, skip any
entry whose bar is <= the previous ACCEPTED trade's exit bar. Causal — only needs the open
position's own exit, known while holding.

| config | mode | n | sum | mean | median | win% | t |
|---|---|---|---|---|---|---|---|
| BASELINE | all rows | 854 | +4.9 | +0.006 | −0.110 | 36.9 | 0.31 |
| BASELINE | **no-pyramid** | 714 | **+11.9** | **+0.017** | −0.105 | 37.7 | **0.78** |
| B x15M30 H2 G30 | all rows | 854 | +350.8 | +0.411 | +0.251 | 56.3 | **4.63** |
| B | **no-pyramid** | **223** | +49.2 | +0.221 | **+0.001** | 50.2 | **1.22** |
| x15M H13 G30 | all rows | 854 | +236.6 | +0.277 | +0.185 | 54.4 | 3.56 |
| x15M H13 | **no-pyramid** | **257** | +27.8 | +0.108 | **+0.000** | 50.2 | **0.72** |
| MID x15M H8 G30 | all rows | 854 | +283.7 | +0.332 | +0.193 | 54.6 | 4.18 |
| MID | **no-pyramid** | **251** | +44.2 | +0.176 | **+0.017** | 50.6 | **1.15** |

- long-hold configs lose **74% of their population** — they hold 6 h and block their own re-entries
- **every median collapses to ~0.000; every t falls below 2**
- win rates all converge on **50.2–50.6%** — a coin
- **the BASELINE improves**: t 0.31 → 0.78, losing only 16% of rows

## It does NOT fix the 05-31 event

| config | mode | n | sum | mean | win% |
|---|---|---|---|---|---|
| B | all rows | 41 | −45.50 | −1.110 | 39.0 |
| B | no-pyramid | **6** | −24.57 | **−4.095** | **0.0** |
| x15M H13 | no-pyramid | 9 | −30.64 | −3.404 | **0.0** |
| MID x15M H8 | no-pyramid | **11** | **−11.12** | −1.011 | 36.4 |

Fewer, larger losses. Not a fix.

## PRE/POST/IS/OOS under no-pyramiding

| config | PRE | POST | IS | OOS | n |
|---|---|---|---|---|---|
| BASELINE | +0.012 | +0.028 | +0.001 | +0.032 | 714 |
| B | +0.247 | +0.147 | **−0.112** | **+0.581** | 223 |
| x15M H13 | +0.101 | +0.128 | +0.018 | +0.199 | 257 |
| MID | +0.235 | +0.021 | +0.191 | +0.160 | 251 |

**VERDICT: under a realistic one-position-at-a-time constraint, NO long-hold config is
statistically distinguishable from noise. The entire long-hold edge reported in checkpoints 1-13
depends on counting overlapping entries as separate trades.**

x15M H13 is the only one positive in all four splits, at +0.108 mean and t 0.72 over 257 trades.
That is the honest size of the result.

---
---

# CHECKPOINT 16 — ORACLE BOUND. The ENTRY is rich; the EXIT captures ~1-10% of it.

After checkpoint 15 killed the long-hold edge under the one-position constraint, the obvious question
is whether the entry signal is worth anything at all. Oracle = exit at the single best bar within H
bars. NON-CAUSAL by construction; it bounds what ANY exit rule could achieve.

| horizon | mode | n | sum | mean | median | t | win% |
|---|---|---|---|---|---|---|---|
| **15 min** | all rows | 854 | +378.4 | **+0.443** | +0.274 | 24.62 | **94.7** |
| 15 min | no-pyramid | 732 | +320.6 | +0.438 | +0.267 | 22.11 | 94.0 |
| 1 h | no-pyramid | 692 | +602.5 | +0.871 | +0.597 | 24.31 | 98.3 |
| 3 h | no-pyramid | 525 | **+774.7** | +1.476 | +1.035 | 22.55 | 98.9 |
| 6 h | no-pyramid | 364 | **+828.7** | +2.277 | +1.666 | 20.08 | 98.9 |
| 24 h | no-pyramid | 121 | +596.9 | +4.933 | +3.956 | 13.02 | 100.0 |

Worst-possible exit for context: **−0.767 at 1 h, −2.102 at 6 h**.

## CAPTURE — the headline

| | oracle | best real | capture |
|---|---|---|---|
| live baseline, 15 min, its own hold | **+0.443** | **+0.006** | **1.4%** |
| 6 h no-pyramid | +2.277 | +0.221 (B gated) | **9.7%** |
| 6 h no-pyramid | +2.277 | +0.108 (x15M H13) | 4.7% |

**94.7% of entries have favourable excursion available within 15 minutes.** The entry signal is not
the problem. Every configuration tested tonight sits in the bottom tenth of the −2.10 to +2.28 range
available at 6 hours.

## Where the opportunity peaks under the constraint

| horizon | trades surviving no-pyramid | oracle sum |
|---|---|---|
| 1 h | 692 | +602.5 |
| 3 h | 525 | +774.7 |
| **6 h** | **364** | **+828.7** |
| 24 h | 121 | +596.9 |

Beyond 6 h the one-position constraint destroys the population faster than the horizon adds
opportunity. **3-6 h is the band worth searching.**

**REFRAME: the s4Mage entry signal is rich and the exit is the binding constraint. That is the
opposite of where I would have pointed after checkpoint 15, and it is the reason to keep going.**

---
---

# CHECKPOINT 17 — STALL exit dead. TRAIL 0.20 clears t=2 under the one-position constraint.

New exit class tested: STALL = exit if no new favourable extreme for N bars (stagnation, not
retracement). NOT in stage D. swing_detect was checked first and rejected as redundant —
`find_pivots` confirms a pivot on a pct% reversal from the running extreme, which is mathematically
identical to the TRAIL mechanic already tested.

**STALL IS DEAD**: stall=None ties EXACTLY with stall=360/720/1440 on every base, so it never fires
at those settings. At 12-48 bars it fires and is slightly worse (though it lifts win% to 47.4%).

## TRAIL 0.20% — the first config tonight to clear t=2 under NO-PYRAMIDING

| config | n | sum | mean | median | t | win% | PRE | POST | IS | OOS | hold |
|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline + trail 0.20 | 798 | +13.2 | +0.016 | −0.055 | 1.59 | 39.5 | +0.027 | −0.014 | +0.016 | +0.017 | 55 |
| B x15M30 H2 c360 G30 + trail 0.20 | 754 | +27.8 | +0.037 | −0.041 | 2.91 | 42.3 | +0.040 | +0.027 | +0.021 | +0.053 | 130 |
| **x15M H13 c360 G30 + trail 0.20** | **758** | **+28.6** | **+0.038** | −0.041 | **3.02** | 42.3 | **+0.042** | **+0.027** | **+0.023** | **+0.053** | **122** |

## THE MECHANISM — population, not per-trade quality

| x15M H13 c360 G30 | n | sum | mean | t |
|---|---|---|---|---|
| no trail, no-pyramid | 257 | +27.8 | +0.108 | **0.72** |
| **+ trail 0.20, no-pyramid** | **758** | **+28.6** | +0.038 | **3.02** |

Same total return, 3x the trades, 4x the t. Hold collapses 3,261 -> 122 bars (10 min) so it stops
blocking its own re-entries.

**Under a one-position constraint a FAST exit beats a GOOD exit, because the binding resource is
time in the market.** This is the single most useful structural insight of the night and it is the
exact opposite of the direction every earlier stage pushed (clock360, 6-hour holds).

The leg still earns its place: +28.6 with leg+gate vs +13.2 for the bare baseline at the same trail.

CAVEAT: median still −0.041, win 42.3%. Most trades lose small; winners carry. And 0.20 was the
SMALLEST trail in the grid — the optimum may be tighter. Sweeping below it next.

---
---

# CHECKPOINT 18 — FEES KILL EVERYTHING. Checkpoint 17's headline is dead.

I ranked every config tonight on GROSS t. Priced against the repo's own standard
(replay.py:31 `taker_bps=5.5` => 0.110% round trip; bias_pk_backtest.py:8 and s30_exit_lever.py:7
both use 0.11% RT), the entire study produces nothing.

| config | n | hold | gross mean | gross t | NET taker mean | net t | net maker mean | maker t |
|---|---|---|---|---|---|---|---|---|
| baseline, no trail | 714 | 159 | +0.017 | 0.78 | −0.093 | −4.40 | −0.023 | −1.10 |
| baseline + trail 0.05 | 821 | 20 | +0.021 | 3.19 | −0.089 | −13.53 | −0.019 | −2.89 |
| **x15M H13 c360 G30 + trail 0.05** | 783 | 78 | +0.039 | **4.46** | **−0.071** | **−8.27** | −0.001 | −0.17 |
| x15M H13 + trail 0.50 | 698 | 309 | +0.061 | 2.50 | −0.049 | −2.00 | +0.021 | 0.86 |
| **x15M H13, NO trail** | 257 | 3517 | **+0.108** | 0.72 | **−0.002** | −0.01 | +0.068 | 0.46 |

## WHY THE t-STAT LIED

A tight trail produces a NARROW return distribution with a small positive mean. Subtracting a
CONSTANT 0.110% leaves the same narrow spread around a clearly negative mean. So:

  gross t +4.46  ->  net taker t −8.27

**The tighter the trail, the HIGHER the gross t and the WORSE the net.** High t from a tight
distribution is low variance, not edge. Every "best config" tonight was selected on this artefact.

The ranking fully INVERTS under fees: by net, the FEWEST/LONGEST trades win; by gross t the
MOST/SHORTEST did. Checkpoint 17's "fast exit beats good exit" is true only gross; it is exactly
backwards net.

## THE REAL CONSTRAINT

- gross mean must clear **0.110%**
- best exit tonight: **+0.108%** on 257 trades — short by 0.002 points
- oracle (checkpoint 16): **+2.277%** is physically present at 6h, no-pyramid

The gap is NOT fees. It is that no causal exit captures enough of a move that is demonstrably there.
94.7% of entries have favourable excursion within 15 min; the capture rate is 1.4-9.7%.

## WHAT THIS RETIRES
- STALL exit: never fires (checkpoint 17)
- swing_detect exit: mathematically identical to TRAIL, redundant
- tight TRAIL: gross-t artefact, worst net in the table
- ranking exits by t on gross returns: INVALID as done tonight. Every future table nets fees first.

## NEXT THREAD
Direction reverses: FEWER, LONGER, LARGER trades — not more/faster/smaller. That is an ENTRY
selection question (which trades to take), not an exit question. Test whether entries can be
filtered so the surviving population has gross mean well clear of 0.110%.

---
---

# CHECKPOINT 19 — THE STUDY IS UNDERPOWERED BY ~17x. This is why nothing separated.

Entry-side filter tested first (causal realised vol over the 30 min BEFORE entry, exit = x15M H13
c360 G30 no trail, no-pyramid, net of 0.110% taker):

| RV filter | thresh | n | gross mn | NET mn | t | PRE | POST | IS | OOS |
|---|---|---|---|---|---|---|---|---|---|
| none | — | 257 | +0.108 | −0.002 | −0.01 | −0.009 | +0.018 | −0.092 | +0.089 |
| rv >= p40 | 0.543 | 192 | +0.266 | **+0.156** | 0.85 | +0.112 | +0.323 | +0.092 | +0.223 |
| rv >= p50 | 0.597 | 173 | +0.250 | +0.140 | 0.71 | +0.073 | +0.474 | +0.034 | +0.261 |
| **rv >= p60** | 0.656 | 139 | +0.049 | **−0.061** | −0.26 | −0.155 | +0.436 | −0.240 | +0.136 |
| rv >= p70 | 0.729 | 113 | +0.194 | +0.084 | 0.32 | +0.061 | +0.213 | +0.013 | +0.156 |
| rv >= p80 | 0.823 | 81 | +0.237 | +0.127 | 0.36 | +0.094 | +0.315 | +0.228 | +0.024 |

NON-MONOTONE: p60 goes negative between two positive neighbours. That is the signature of noise, not
signal. Every t < 1. The RV filter does NOT deliver.

## POWER ANALYSIS — the actual explanation

n* = ((1.96+0.84)*sd / net_mean)^2 for 80% power, alpha 0.05, net of 0.110% taker.

| config | n | gross | sd | net mean | n* | weeks at this rate |
|---|---|---|---|---|---|---|
| baseline no trail | 714 | +0.017 | 0.567 | −0.093 | — | never |
| x15M H13 c360 G30 no trail | 257 | +0.108 | 2.390 | −0.002 | — | never |
| x15M H13 G30 trail 0.50 | 698 | +0.061 | 0.646 | −0.049 | — | never |
| x15M H13 G30 trail 0.05 | 783 | +0.039 | 0.242 | −0.071 | — | never |
| **x15M30 H2 c360 G30 no trail** | 223 | **+0.221** | 2.709 | **+0.111** | **4,701** | **253** |

Sensitivity for the best config (n=257, sd=2.390):

| to detect a net edge of | n* needed | weeks at this trade rate |
|---|---|---|
| +0.02%/trade | 111,929 | 5,226 |
| +0.05%/trade | 17,909 | 836 |
| +0.10%/trade | 4,477 | **209** |
| +0.20%/trade | 1,119 | 52 |
| +0.30%/trade | 497 | 23 |
| +0.50%/trade | 179 | **8** |

## THE FINDING

**Per-trade sd is 2.390%. The cost line is 0.110%. The noise is 22x the quantity being measured.**

12 weeks of this producer yields 223-257 no-pyramid trades. Detecting a +0.10%/trade edge needs
4,477 — we are short by ~17x. EVERY result tonight (OOS stagnation, the 07-12 break, the
non-monotone RV filter, the whole 8,320-config stage-D grid) is sampling noise around a quantity
too small to see at this n. That is not a failure of the mechanics; it is a failure of resolution.

**SOLE NET-POSITIVE CONFIG**: x15M30 H2 c360 G30, no trail, no-pyramid — gross +0.221, net +0.111
over 223 trades. It is the "B" config from the earlier stages. It is UNPROVEN (needs 253 weeks at
this rate) but it is the only one on the right side of the cost line.

## WHAT IS AND IS NOT WORTH DOING NEXT

NOT worth doing: more permutations on 12 weeks of data. The grid cannot resolve 0.11% at n=250.
Any "best config" it returns is selected on noise — which is exactly how checkpoint 17's t=4.46
arose and then inverted to −8.27.

Worth doing, in order:
1. Chase a BIGGER edge, not a better-tuned one. +0.30%/trade is provable in 23 weeks, +0.50% in 8.
   The oracle (ckpt 16) says +2.277% is physically present at 6h, so a large edge is not ruled out.
2. Variance reduction only counts if it does not cut the mean proportionally. The trail cuts sd
   2.390 -> 0.242 (10x) but cuts gross mean 0.108 -> 0.039 (2.8x) and the net gets WORSE, because
   the cost is a constant the mean must clear before variance matters.
3. Raise the trade rate without pyramiding — i.e. a different/faster entry producer. This is the
   only lever that attacks n directly.

NOTE: nopyr_sweep.py wrote only its baseline line (n 714, mean +0.017, t 0.78) before disconnecting;
no JSON. Superseded — checkpoints 18/19 answer its question directly and net of fees: NO config in
the family clears t=2 net, and the family cannot be resolved at this n regardless.

---
---

# CHECKPOINT 20 — every STOP fails for a provable reason. The prize is SELECTION, not exit.

Motivated by ckpt 19's arithmetic: weeks = n*/rate, and n* scales with sd^2, so cutting sd is
QUADRATIC while raising rate is only linear. A hard stop attacks both. Never tested tonight.

## THE STOP SWEEP — both levers fired, the edge died anyway

x15M30 H2 c360 G30, no-pyramid, net of 0.110% taker:

| stop | n | hold | gross mn | sd | NET mn | t | win% | n* | weeks |
|---|---|---|---|---|---|---|---|---|---|
| none | 223 | 4300 | **+0.221** | 2.709 | +0.111 | 0.61 | 47.5 | 4701 | 253 |
| 0.10 | **813** | 218 | −0.010 | **0.573** | −0.120 | −5.97 | **6.0** | — | never |
| 0.25 | 702 | 483 | −0.021 | 0.933 | −0.131 | −3.72 | 12.1 | — | never |
| 0.50 | 563 | 952 | −0.015 | 1.278 | −0.125 | −2.32 | 21.1 | — | never |
| 1.00 | 402 | 1746 | +0.118 | 1.881 | +0.008 | 0.09 | 32.8 | 384201 | 11469 |
| 3.00 | 271 | 3197 | +0.145 | 2.500 | +0.035 | 0.23 | 45.4 | 40718 | 1803 |

Rate up 3.6x (223->813), sd down 4.7x (2.709->0.573) — EXACTLY what the power arithmetic wanted —
and gross mean went +0.221 -> −0.010. 94% of entries breach 0.10% adverse. Same shape on x15M H13
(every stop level net-negative there, no exceptions). Mean recovers monotonically as the stop widens
back toward no-stop.

## WHY EVERY STOP FAILS — the general proof

| stop X | n breached | their MEAN EVENTUAL ret | stop books | holding better by |
|---|---|---|---|---|
| 0.50 | 167 | −0.261 | −0.50 | **+0.24** |
| 0.75 | 135 | −0.631 | −0.75 | +0.12 |
| 1.00 | 119 | −0.889 | −1.00 | +0.11 |
| 1.50 | 91 | −1.392 | −1.50 | +0.11 |
| 2.00 | 66 | −1.668 | −2.00 | +0.33 |
| 3.00 | 44 | −2.601 | −3.00 | **+0.40** |

**At EVERY level the mean eventual return of breached trades is BETTER than −X.** After breaching X
adversely the trade recovers, on average, to better than the stop price. The stop monetises the
excursion at its worst point. This is not a tuning failure — it predicts failure at ALL levels, so
the stop family is CLOSED, not un-optimised.

CORRECTION to my own phrasing earlier this turn: the left tail is NOT "load-bearing" (it loses
money — MAE>=3.00 returns −2.601). It is UNSTOPPABLE. Different claim.

## MAE BUCKETS — return is monotone in adverse excursion

| MAE bucket | n | mean MFE | mean ret | net ret | win% |
|---|---|---|---|---|---|
| 0.00-0.10 | 9 | 2.910 | +1.783 | +1.673 | 100.0 |
| 0.10-0.25 | 17 | 3.385 | **+2.122** | +2.012 | 94.1 |
| 0.25-0.50 | 27 | 2.404 | +1.387 | +1.277 | 77.8 |
| 0.50-0.75 | 32 | 2.375 | +1.300 | +1.190 | 62.5 |
| 0.75-1.00 | 16 | 2.339 | +1.284 | +1.174 | 56.2 |
| 1.00-1.50 | 28 | 2.508 | +0.749 | +0.639 | 46.4 |
| 1.50-2.00 | 25 | 1.102 | −0.665 | −0.775 | 20.0 |
| 2.00-3.00 | 22 | 1.796 | +0.199 | +0.089 | 36.4 |
| >= 3.00 | 44 | 1.424 | **−2.601** | −2.711 | 18.2 |

## THE PRIZE

| population | n | gross mn | NET mn | sd | net sum | n* | weeks |
|---|---|---|---|---|---|---|---|
| all trades | 223 | +0.221 | +0.111 | 2.709 | +24.7 | 4701 | 253 |
| never breached 0.50 | 56 | +1.657 | +1.547 | 1.860 | +86.6 | 11 | 2 |
| **never breached 1.50** | **132** | +1.333 | **+1.223** | 2.074 | **+161.4** | **23** | **2** |
| never breached 3.00 | 179 | +0.914 | +0.804 | 2.090 | +144.0 | 53 | 4 |

Trades that never breach 1.50% adverse earn +1.223 net over 132 trades — **provable in 2 WEEKS, not
253.** The set is NOT causally available (membership is known only at exit).

## THE QUESTION THIS REDUCES TO

**Is MAE predictable at ENTRY?** If any causal entry-time feature separates the eventual-MAE<1.50
group, the edge is ~11x the cost line and provable in weeks. If nothing predicts it, the producer is
finished and the answer to Joe's "is this still worth working on" is no.

This is a strictly better question than any exit permutation, because it is the only one whose
positive answer is resolvable with the data we already have.

---
---

# CHECKPOINT 21 — MAE is NOT predictable at entry. And the IS/OOS gap is a PERIOD effect.

## 21a. 18 causal entry-time features vs eventual MAE<1.50 (x15M30 H2, n=223, 132 good / 91 bad)

Every feature uses ONLY bars strictly before the entry bar. Split at each feature's median.

| feature | AUC | good% hi | net mn hi | net mn lo | IS hi | OOS hi |
|---|---|---|---|---|---|---|
| rvol_60m | 0.442 | 58.9 | +0.349 | −0.130 | −0.154 | +1.098 |
| ret_6m | 0.509 | 58.9 | +0.453 | −0.234 | +0.027 | +1.041 |
| rvol_6m | 0.491 | 57.1 | +0.297 | −0.077 | −0.101 | +0.912 |
| LN_M30 | 0.456 | 56.2 | −0.033 | +0.256 | −0.704 | +0.741 |
| LN_vol | 0.504 | 58.9 | −0.172 | +0.395 | −0.607 | +0.711 |
| ret_30m | 0.414 | 55.4 | +0.123 | +0.098 | −0.340 | +0.718 |

- baseline good rate **59.2%**; best split reaches **60.7%** — a 1.5-point lift on 223 trades
- all 18 AUCs fall in **0.414-0.549**. 0.500 = no information.
- `LN_ts` (AUC 0.549) is the TIMESTAMP — chronology, not a feature. Its IS_hi is nan because every
  high-timestamp trade is OOS by construction. EXCLUDED as a leak.
- features tested: rvol/ret at 6m/30m/60m/3h (ret direction-aligned), plus every banked line array
  (x/M/r at TF15/22/30) and volume, all shifted 1 bar.

**MAE is not predictable at entry.** The prize in ckpt 20 (+1.223 net, 2 weeks to prove) is not
reachable by selection on anything measured here.

## 21b. THE TELL — all 18 features show negative IS, positive OOS

A feature effect cannot be uniform across price volatility, every line value, AND traded volume.
Control: unconditional net by chronological half, NO feature split at all.

| config | n | net IS | net OOS | gap |
|---|---|---|---|---|
| baseline no trail | 714 | −0.108 | −0.079 | +0.029 |
| **x15M30 H2 c360 G30** | 223 | **−0.268** | **+0.486** | **+0.754** |
| x15M H13 c360 G30 | 257 | −0.106 | +0.101 | +0.206 |

## 21c. THE SAME TRADES BY CALENDAR WEEK

| week | n | net mean | net sum | win% |
|---|---|---|---|---|
| 05-14 | 8 | −1.188 | −9.5 | **0.0** |
| 05-21 | 24 | −0.166 | −4.0 | 50.0 |
| 05-28 | 15 | −1.159 | −17.4 | 26.7 |
| 06-04 | 22 | −0.236 | −5.2 | 54.5 |
| 06-11 | 22 | +0.186 | +4.1 | 54.5 |
| 06-18 | 24 | +0.222 | +5.3 | 41.7 |
| **06-25** | 21 | **+1.346** | **+28.3** | 61.9 |
| **07-02** | 21 | **+0.838** | **+17.6** | 57.1 |
| 07-09 | 18 | +0.167 | +3.0 | 50.0 |
| 07-16 | 20 | −0.026 | −0.5 | 40.0 |
| 07-23 | 21 | +0.171 | +3.6 | 52.4 |
| 07-30 | 7 | −0.083 | −0.6 | 42.9 |

**6 of 12 weeks net-positive — a coin flip.**
**Two weeks (06-25, 07-02) sum +45.9. The other TEN sum −21.2.** Remove them and the sole
net-positive config loses money. The +0.754 IS/OOS gap is those two weeks landing in the second half.

## VERDICT ON THE EXIT STUDY

Everything is now closed with a reason, not with a shrug:
- exit permutations (8,320 configs) — noise at n=250 (ckpt 19, underpowered ~17x)
- tight trail — gross-t artefact, inverts under fees (ckpt 18)
- STALL / swing_detect — never fires / redundant with TRAIL (ckpt 17)
- hard stop, ALL levels — breached trades recover to better than −X (ckpt 20), family closed
- entry filtering on RV — non-monotone noise (ckpt 19)
- entry filtering on 18 causal features — AUC 0.414-0.549 (ckpt 21a)
- the apparent edge — two weeks out of twelve (ckpt 21c)

The honest answer to "is this still worth working on": **not as an exit problem, and not by tuning.**
The producer's raw output does not clear 0.110% except in 2 of 12 weeks, and nothing measured at
entry time distinguishes those weeks in advance.

## LAST REMAINING SHOT FOR THIS PRODUCER
Do 06-25 and 07-02 share a REGIME that is detectable causally at week scale (not trade scale)? A
week-scale regime switch is a much weaker requirement than per-trade MAE prediction — it needs to
separate 2 weeks from 10, not 132 trades from 91. That is the next and last measurement.

---
---

# CHECKPOINT 22 — THE EDGE IS SHORT-SIDE ONLY. First result to survive the period test.

## 22a. week-scale regime — NOT detectable

Tape features (strategy-independent) vs the same trades' weekly net. n=12 weeks, so |r| must exceed
0.577 for p<0.05.

| feature | corr same week | corr PRIOR week |
|---|---|---|
| rvol | +0.444 | +0.454 |
| efficiency ratio | −0.326 | −0.342 |
| 1-lag autocorr | +0.265 | +0.253 |
| range | +0.342 | +0.190 |
| drift | +0.450 | +0.249 |

Nothing clears. Best is rvol prior-week at +0.454 vs a 0.577 bar. Week-scale regime detection FAILS.
But `drift` showed a shape: positive-drift weeks mean +0.211, negative-drift weeks −0.199 — which
led to the beta hypothesis below.

## 22b. ALPHA vs BETA — hypothesis WRONG, and the truth is sharper

| config | n | nLONG | net LONG | sum | nSHORT | net SHORT | sum |
|---|---|---|---|---|---|---|---|
| baseline no trail | 714 | 331 | −0.062 | −20.5 | 383 | −0.121 | −46.2 |
| **x15M30 H2 c360 G30** | 223 | 111 | −0.071 | −7.9 | 112 | **+0.291** | **+32.6** |
| x15M H13 c360 G30 | 257 | 125 | −0.133 | −16.6 | 132 | +0.122 | +16.1 |

Side split is 49.8% long — NOT a directional tilt. Beta benchmark over the same entry/exit bars:

| | n | mean | sum |
|---|---|---|---|
| strategy (signed) gross | 223 | +0.221 | +49.2 |
| always-long same bars | 223 | −0.182 | −40.6 |
| always-short same bars | 223 | +0.182 | +40.6 |

Regression strat_gross = alpha + beta*always_long:
  alpha **+0.2595**  se 0.1780  t +1.46
  beta   **+0.2135**  se 0.0656  t +3.25

Beta loading is real but SMALL AND UNHELPFUL: 0.2135 x −0.182 = −0.039. Alpha carried it, and its
point estimate +0.26 clears the 0.110 cost line by 2.4x (though t 1.46 is not significant).
corr(strategy gross, always-long) = +0.214.

## 22c. SHORT-SIDE ONLY — survives the period test

no-pyramiding RE-APPLIED after the side filter (dropping longs frees slots for shorts).

| stream | n | net mean | sum | t | IS | OOS | weeks+ | n* | weeks |
|---|---|---|---|---|---|---|---|---|---|
| **x15M30 H2 G30 SHORT** | 112 | **+0.291** | +32.6 | +1.29 | **+0.110** | **+0.472** | **8/12** | 528 | 57 |
| x15M30 H2 G30 LONG | 111 | −0.071 | −7.9 | −0.25 | −0.565 | +0.413 | 6/11 | — | never |
| x15M H13 G30 SHORT | 132 | +0.122 | +16.1 | +0.64 | +0.040 | +0.204 | 6/12 | 2531 | 230 |
| x15M H13 G30 LONG | 125 | −0.133 | −16.6 | −0.58 | −0.156 | −0.110 | 7/12 | — | never |
| **baseline SHORT (CONTROL)** | 383 | −0.121 | −46.2 | −4.62 | −0.138 | −0.103 | **0/12** | — | never |
| baseline LONG | 331 | −0.062 | −20.5 | −1.80 | −0.070 | −0.054 | 3/12 | — | never |

### x15M30 H2 SHORTS by calendar week

| week | n | net mean | net sum | win% |
|---|---|---|---|---|
| 05-14 | 6 | −1.240 | −7.4 | 0.0 |
| 05-21 | 11 | +0.614 | +6.8 | 63.6 |
| 05-28 | 7 | −0.531 | −3.7 | 28.6 |
| 06-04 | 10 | +0.415 | +4.1 | 60.0 |
| 06-11 | 9 | +0.669 | +6.0 | 55.6 |
| 06-18 | 17 | −0.081 | −1.4 | 35.3 |
| 06-25 | 7 | +1.891 | +13.2 | 71.4 |
| 07-02 | 8 | +0.941 | +7.5 | 62.5 |
| 07-09 | 11 | +0.253 | +2.8 | 54.5 |
| 07-16 | 10 | +0.318 | +3.2 | 40.0 |
| 07-23 | 13 | +0.214 | +2.8 | 61.5 |
| 07-30 | 3 | −0.436 | −1.3 | 33.3 |

### THE TWO-WEEK DEPENDENCY IS GONE

| | top-2 weeks | remaining 10 weeks |
|---|---|---|
| combined long+short | +45.9 | **−21.2** |
| **shorts only** | +20.8 | **+11.8** |

The combined config LOST money outside its two best weeks. Shorts-only makes +11.8 across the other
ten (+1.18/week) — it no longer depends on 06-25 and 07-02.

### WHY THIS IS CREDIBLE — the control

Bare-baseline SHORT is −0.121/trade with **0 of 12 weeks positive**. This tape did NOT simply reward
shorting. Adding the x15M30 leg + G30 gate turns a stream that lost in EVERY week into one that wins
in 8 of 12 and clears the cost line 2.6x. **The mechanic does the work, not the side.**

STILL UNPROVEN: t 1.29, n* 528 => 57 weeks at this rate. But this is the only result tonight that is
(1) net-positive after fees, (2) positive in BOTH halves, (3) positive with its best two weeks
removed, and (4) backed by a control that isolates the mechanic from the side.

## NEXT
Is x15M30 special on the short side, or does the gate rescue shorts across the whole leg family?
Sweep every leg x H x gate, SHORT-SIDE ONLY, ranked on (weeks-positive, net-ex-top-2). If many legs
show it, the finding is structural; if only x15M30 does, it is selection on 8,320 configs.

## CHECKPOINT 23 — short-side family sweep [LANDED — see below]

Running: all 13 legs x 8 H x gate{on,off}, clock360, SHORT SIDE ONLY, n>=25, no-pyramid re-applied
per side. 208 configs. Task bcbci8yga.

The question is SELECTION, not performance. x15M30 H2 was picked out of an 8,320-config grid, so its
8/12 positive weeks must be priced against the DISTRIBUTION of weeks-positive across the family, not
against zero. Reporting min/p25/median/p75/max of (weeks positive, net-ex-top-2, net mean) plus the
share of configs clearing weeks+ >= 8 AND ex-top2 > 0, and x15M30's rank within the family.

- if MANY legs clear both -> the short-side effect is STRUCTURAL and x15M30 is one instance of it
- if ONLY x15M30 clears -> it is selection on 8,320 configs and checkpoint 22 is retracted

---

# CHECKPOINT 23 RESULT — ckpt 22 CORRECTED, and its config-level claim RETRACTED.

## 23a. CORRECTION TO CHECKPOINT 22 — my own implementation error

ckpt 22 applied no-pyramiding across BOTH sides first, then subsetted the shorts. That describes a
strategy which runs longs purely to block positions and books only the shorts — NOT implementable.
The sweep does it correctly: side filter FIRST, then no-pyramid on the short-only stream.

| x15M30 H2 c360 G30, SHORT | n | net mean | net sum | weeks+ | ex-top2 |
|---|---|---|---|---|---|
| ckpt 22 (WRONG — double filter) | 112 | +0.291 | +32.6 | 8/12 | +11.8 |
| **ckpt 23 (CORRECT)** | **184** | **+0.178** | **+32.7** | **7/12** | **+7.0** |

Still net-positive and still ex-top2 positive, but materially weaker. Use the ckpt 23 row.

## 23b. THE SELECTION TEST — 208 configs, SHORT side, clock360, n>=25

| metric | min | p25 | median | p75 | max |
|---|---|---|---|---|---|
| weeks positive (of ~12) | 2 | 4 | **5** | 6 | 8 |
| net sum ex top-2 weeks | −60.48 | −40.43 | **−23.73** | −13.12 | **+6.97** |
| net mean/trade | −0.16 | −0.09 | **−0.04** | +0.03 | +0.18 |

- configs with weeks+ >= 8: **3 of 208 (1%)**
- configs with ex-top2 > 0: **7 of 208 (3%)**
- BOTH: **1 of 208 (0%)**
- **x15M30 H2 G=Y ranks 1 of 208 on ex-top2**, 4 of 208 on weeks+

The median config in this family is NEGATIVE on every metric. Being rank 1 of 208 on the metric I
selected on is exactly what selection looks like. **CHECKPOINT 22'S CONFIG-LEVEL CLAIM IS RETRACTED.**
x15M30 H2 short-side is not established as an edge; it is the maximum of a noisy 208-draw sample.

## 23c. Top 15 short-side by (weeks+, then ex-top2)

| leg | H | G | n | netmn | netsum | t | IS | OOS | wks+ | ex-top2 |
|---|---|---|---|---|---|---|---|---|---|---|
| x15M | 21.0 | Y | 207 | +0.114 | +23.6 | 0.71 | +0.138 | +0.090 | 8/12 | +3.8 |
| x15r30 | 13.0 | Y | 208 | +0.045 | +9.3 | 0.28 | +0.001 | +0.088 | 8/12 | −7.4 |
| x15b | 21.0 | Y | 226 | +0.009 | +2.0 | 0.06 | +0.016 | +0.002 | 8/12 | −10.2 |
| **x15M30** | 2.0 | Y | 184 | +0.178 | +32.7 | 0.87 | +0.277 | +0.078 | 7/12 | **+7.0** |
| x22M | 0.0 | Y | 191 | +0.180 | +34.3 | 0.97 | +0.231 | +0.128 | 7/12 | +5.0 |
| x15M | 13.0 | Y | 199 | +0.119 | +23.7 | 0.69 | +0.183 | +0.056 | 7/12 | +0.6 |
| x22M | 1.0 | Y | 192 | +0.147 | +28.3 | 0.81 | +0.200 | +0.095 | 7/12 | −1.8 |
| x22M30 | 3.0 | Y | 189 | +0.103 | +19.4 | 0.55 | +0.122 | +0.083 | 7/12 | −2.0 |
| x22M30 | 5.0 | Y | 189 | +0.115 | +21.7 | 0.61 | +0.157 | +0.073 | 7/12 | −2.3 |
| x22M30 | 0.0 | Y | 184 | +0.106 | +19.5 | 0.56 | +0.123 | +0.090 | 7/12 | −2.6 |
| x22M30 | 8.0 | Y | 196 | +0.101 | +19.8 | 0.57 | +0.125 | +0.078 | 7/12 | −2.6 |
| x22M | 2.0 | Y | 192 | +0.145 | +27.8 | 0.80 | +0.202 | +0.088 | 7/12 | −3.0 |
| x15M | 0.0 | Y | 187 | +0.150 | +28.0 | 0.77 | +0.275 | +0.026 | 7/12 | −3.1 |
| x15M | 8.0 | Y | 194 | +0.113 | +21.8 | 0.64 | +0.201 | +0.024 | 7/12 | −3.6 |
| x22M30 | 2.0 | Y | 188 | +0.097 | +18.2 | 0.52 | +0.108 | +0.085 | 7/12 | −3.8 |

## 23d. THE ONE THING IN THAT TABLE THAT IS NOT NOISE-SHAPED

**ALL 15 have the gate ON (G=Y).** Under a null, gate-on and gate-off should split the top 15 evenly
(the sweep contains both in equal number). They also cluster on M-crossing legs (x15M, x22M, x15M30,
x22M30) rather than b/r legs.

That is a claim about the GATE, not about any config — and it is testable PAIRED, where every config
is its own control: same leg, same H, same side, gate ON vs gate OFF. A paired test does not care
about the ranking and cannot be gamed by selection. Running now (ckpt 24).

---
---

# CHECKPOINT 24 — what "G30" actually is (read from source, not inferred)

The surviving hypothesis from ckpt 23d is about the GATE, so here is its exact definition before the
paired test lands. `G30` in every table tonight = `gate_open(L, dr, tfs=(30,), states=(1,), gwob=1)`.

```python
def gate_open(L, dr, tfs, states, gwob):          # sweep_s46_exit.py:220
    """momo gate: EITHER chosen TF in the chosen state set, held gwob consecutive bars."""
    tag = 'p' if dr > 0 else 'n'                  # 'p' = long direction, 'n' = short direction
    g = np.zeros(len(L['ts']), bool)
    for tf in tfs:
        v = L['g%d_%s' % (tf, tag)]               # banked int8, one state per 5 s bar
        for s in states:
            g |= (v == s)
    return run_len(g) >= max(1, gwob)
```

Every argument, with its role and CURRENT value:
- `tfs = (30,)` — TF30 only (the 30-tick/30-unit board). The 15 and 22 boards are NOT consulted.
- `states = (1,)` — state 1. From build_s46_lines.py:14 the int8 encoding is
  **0 none | 1 momo | 2 curl | 3 sideways**, so state 1 == `momo`. Curl (2) is NOT in the gate.
- `gwob = 1` — run-length requirement, in 5 s bars. At 1 this is "true on the current bar", i.e. no
  debounce at all.
- `tag` — resolves per trade side, so a SHORT reads `g30_n` (down-momo) and a LONG reads `g30_p`.

States come from `build_exhv2.momo()`, CALLED not copied (build_s46_lines.py:20) so MOMO_WINDOW_MIN /
CURL_ARC_MIN cannot fork.

## THE GATE DOES TWO THINGS, AND THE SECOND ONE IS NOT OBVIOUS

From `evaluate()` (sweep_s46_exit.py:250-274):

1. **ARM** — `start = a + first bar at/after entry where the gate is open`. The exit leg cannot fire
   before the gate opens. If it never opens, the trade is dropped entirely (`start = None`).

2. **VETO the baseline exit** — in the s6 branch:
   ```python
   if gate is None or not gate[dr][bi]:
       cand.append(bi); break
   ```
   s6's exit bar is only ACCEPTED when the gate is CLOSED. **While TF30 momo is running in the
   trade's direction, s6's exit signal is ignored and the trade keeps running.**

So G30 is not merely a filter on when the exit may arm — it is a **hold-longer mechanic**: it
suppresses the baseline exit for exactly as long as TF30 momo agrees with the trade. That is the
mechanically plausible reason the whole top-15 of ckpt 23c carries G=Y, and it is what the paired
test (ckpt 25) either confirms or kills.

Note this also means gate-on and gate-off configs do NOT trade the same population: gate-on drops
every trade whose gate never opens. The paired test reports n for both sides of each pair.

---
---

# CHECKPOINT 25 — THE PAIRED GATE TEST. First mechanic tonight to survive a proper control.

Same leg, same H, same side, gate ON vs gate OFF. 104 pairs per side (13 legs x 8 H). Every config
is its own control, so this cannot be gamed by ranking — unlike ckpt 22/23. Net of 0.110% taker,
no-pyramid re-applied per side.

## 25a. PAIRED DELTAS

| side | pairs | d(net mean) | gate-ON better in | d(weeks+) | d(ex-top2) | ON better on ex-top2 |
|---|---|---|---|---|---|---|
| **SHORT** | 104 | **+0.0734** | **104/104 (100%)** | +1.47 | +19.06 | **104/104** |
| LONG | 104 | +0.0306 | 77/104 (74%) | +1.69 | +14.94 | 98/104 |
| BOTH | 104 | +0.0428 | 77/104 (74%) | +1.80 | +16.64 | 83/104 |

## 25b. ABSOLUTE LEVELS (mean over all leg x H configs)

| side | gate | cfgs | net mean | weeks+ | ex-top2 | t |
|---|---|---|---|---|---|---|
| SHORT | **ON** | 104 | **+0.0111** | 6.03 | −16.92 | +0.033 |
| SHORT | off | 104 | **−0.0623** | 4.56 | −35.99 | −0.752 |
| LONG | ON | 104 | −0.1052 | 5.74 | −38.34 | −0.576 |
| LONG | off | 104 | −0.1358 | 4.05 | −53.27 | −1.210 |
| BOTH | ON | 104 | −0.0552 | 5.62 | −40.56 | −0.367 |
| BOTH | off | 104 | −0.0980 | 3.82 | −57.20 | −1.164 |

## 25c. WHAT IS ESTABLISHED

**The gate is a real mechanic.** It improves the short side in EVERY ONE of 104 leg x H combinations,
with zero exceptions, and helps shorts 2.4x more than longs (+0.0734 vs +0.0306). Unanimity across
the whole family is not the shape of selection — ckpt 23 showed the family median is negative, so
this is not a rising tide.

Mechanically consistent with ckpt 24: G30 suppresses s6's exit while TF30 momo runs in the trade's
direction. A hold-longer mechanic should help most where the move continues, and the short side is
where this producer's moves continue.

## 25d. WHAT IS NOT ESTABLISHED — two things I will NOT overclaim

1. **The paired t of +38.00 is meaningless as a significance test.** The 104 pairs share most of
   their underlying trades, so they are massively correlated. This is ONE effect measured 104 times,
   not 104 independent confirmations. The honest statement is the SIGN CONSISTENCY (104/104) plus
   the effect size (+0.0734/trade), not the t.
2. **The gate is NOT SUFFICIENT.** It lifts short-side net from −0.0623 to **+0.0111** — that is
   approximately break-even AFTER fees, not an edge. And the average gate-on short config still has
   **ex-top2 −16.92**: it loses money outside its best two weeks. weeks+ rises 4.56 -> 6.03, still
   only half the weeks.

## 25e. STANDING AFTER 25 CHECKPOINTS

| claim | status |
|---|---|
| exit permutations (8,320 cfgs) find an edge | DEAD — underpowered ~17x (ckpt 19) |
| tight TRAIL exit | DEAD — gross-t artefact, inverts under fees (ckpt 18) |
| STALL exit | DEAD — never fires (ckpt 17) |
| swing_detect exit | DEAD — identical to TRAIL (ckpt 17) |
| hard STOP, any level | DEAD — breached trades recover past −X (ckpt 20) |
| entry filter on realised vol | DEAD — non-monotone (ckpt 19) |
| entry filter on 18 causal features | DEAD — AUC 0.414-0.549 (ckpt 21) |
| week-scale regime detection | DEAD — best \|r\| 0.454 vs 0.577 bar (ckpt 22a) |
| long-bias / beta explanation | DEAD — 49.8% long, beta contribution −0.039 (ckpt 22b) |
| x15M30 H2 short-side is an edge | RETRACTED — rank 1 of 208 on its own metric (ckpt 23) |
| **G30 gate improves the short side** | **ESTABLISHED — 104/104 paired, +0.0734/trade (ckpt 25)** |
| **G30 gate is enough to trade** | **NO — lifts shorts only to +0.011 net, ex-top2 still −16.92** |

## NEXT
The gate is the one thing that works and it was never swept — every table tonight used exactly one
setting, `tfs=(30,) states=(1,) gwob=1`. Its three knobs are untouched:
- `tfs` — TF30 only; 15 and 22 never tried, nor combinations
- `states` — momo(1) only; **curl(2) is excluded**, and Joe said on 0803 "curl is as important as
  momo, so yes include it in the calcs". Never tested in the GATE.
- `gwob` — 1, i.e. NO debounce, on the noisiest possible signal

Sweeping the gate is the highest-value remaining measurement: it is the only mechanic with a clean
control behind it, and it is running at its least-tuned setting.

## CHECKPOINT 26 — gate knob sweep [LANDED]

Launched: 7 tfs x 3 states x 4 gwob = 84 gate configs, each scored as the MEAN across 8 leg x H
combos (x15M / x22M / x15M30 / x22M30 at H 2.0 and 13.0) = 672 evaluations. SHORT side only.
Script banked at $CLAUDE_JOB_DIR/tmp/gsweep.py, json to gsweep.json, log to gsweep.log.

Scored as a mean across a leg family, NOT as a single config, specifically so a winner cannot be a
best-of-N draw the way ckpt 22/23 was. Also reports the MARGINAL effect of each knob independently.

Baseline for every table tonight = tfs (30,) / momo / gwob 1.
The key untested arm is **curl**: states (2,) and (1,2). Joe 0803: "curl is as important as momo, so
yes include it in the calcs" — that was applied to the exit legs but NEVER to the gate.

---

# CHECKPOINT 26 RESULT — the gate was ALREADY at its optimum. Last open knob closed.

84 gate configs (7 tfs x 3 states x 4 gwob), each the MEAN across 8 leg x H combos, SHORT side,
net of 0.110% taker. Baseline used in every table tonight = tfs 30 / momo / gwob 1 -> netmn +0.1069,
weeks+ 6.88, ex-top2 −3.93.

**Only 3 of 84 configs beat the baseline, and by at most +0.0165.**

## 26a. TOP 8 BY NET MEAN

| tfs | states | gwob | meanN | net mean | vs base | weeks+ | ex-top2 | cfgs+ |
|---|---|---|---|---|---|---|---|---|
| 30 | momo | 48 | 182 | +0.1234 | +0.0165 | 6.50 | −3.34 | 8/8 |
| 30 | curl | 48 | 208 | +0.1228 | +0.0159 | 6.00 | −6.06 | 8/8 |
| 30 | momo | 3 | 193 | +0.1159 | +0.0090 | 7.00 | −2.24 | 8/8 |
| **30** | **momo** | **1** | 193 | **+0.1069** | **base** | 6.88 | −3.93 | 8/8 |
| 30 | momo | 12 | 187 | +0.1064 | −0.0005 | 6.50 | −5.12 | 8/8 |
| 30 | curl | 12 | 225 | +0.0971 | −0.0098 | 6.62 | −6.56 | 8/8 |
| 22 | curl | 3 | 244 | +0.0862 | −0.0207 | 6.50 | **−0.13** | 8/8 |
| 22 | curl | 1 | 246 | +0.0813 | −0.0256 | 6.50 | −0.65 | 8/8 |

## 26b. MARGINAL EFFECT OF EACH KNOB

| knob | value | cfgs | net mean | weeks+ | ex-top2 |
|---|---|---|---|---|---|
| tfs | **30** | 12 | **+0.0780** | 6.35 | **−9.85** |
| tfs | 15 | 12 | +0.0535 | 5.77 | −13.98 |
| tfs | 15/22 | 12 | +0.0433 | 6.08 | −13.51 |
| tfs | 22 | 12 | +0.0380 | 6.04 | −13.17 |
| tfs | 15/30 | 12 | +0.0299 | 5.95 | −16.60 |
| tfs | 15/22/30 | 12 | +0.0252 | 5.96 | −17.74 |
| tfs | 22/30 | 12 | **+0.0043** | 5.56 | −21.93 |
| states | **momo** | 28 | **+0.0469** | 5.98 | −14.82 |
| states | curl | 28 | +0.0436 | 5.83 | −14.63 |
| states | **momo+curl** | 28 | **+0.0262** | 6.07 | −16.32 |
| gwob | 1 | 21 | +0.0380 | 6.06 | −14.94 |
| gwob | 3 | 21 | +0.0399 | 6.07 | −14.60 |
| gwob | 12 | 21 | +0.0359 | 5.85 | −15.95 |
| gwob | 48 | 21 | +0.0418 | 5.86 | −15.53 |

## 26c. THREE FINDINGS

1. **TF30 alone is correct, and ADDING boards actively hurts.** 30 alone +0.0780; 22/30 collapses to
   +0.0043; 15/22/30 +0.0252. More voters make the gate LESS selective, not better informed. The
   original choice of `tfs=(30,)` was right for a reason, not by luck.
2. **Curl in the GATE does not help — the union is worse than either part.**
   momo +0.0469, curl +0.0436, **momo+curl +0.0262**. Curl ALONE is nearly as informative as momo
   alone, but OR-ing them opens the gate far more often (mean n 244-263 vs 182-208) and admits
   marginal trades. This is a specific NEGATIVE for applying Joe 0803 ("curl is as important as
   momo, so yes include it in the calcs") **to the gate** — it holds for the exit legs, where it was
   tested, but not here. Flagging for Joe rather than deciding it: the instruction was about the
   calcs generally, and this is one place it measures worse.
3. **gwob does nothing.** 48x variation in debounce moves net mean by 0.006 (+0.0359 to +0.0418).
   The gate's value is not in its timing, so the "no debounce on the noisiest signal" concern raised
   in ckpt 25's NEXT is answered: it does not matter.

## 26d. CAVEAT ON THE ABSOLUTE LEVEL

These 8 leg x H combos were drawn from ckpt 23c's top-15, so the baseline +0.1069 here is OPTIMISTIC
against the unbiased all-104 figure of +0.0111 (ckpt 25b). The MARGINAL comparisons in 26b are valid
— identical legs throughout, every knob varied against the same population — but the LEVEL is not an
unbiased estimate of what the gate earns.

## STANDING
The gate is real (ckpt 25: 104/104 paired) and is already optimally configured (ckpt 26). It is
still not sufficient: unbiased short-side net is +0.0111/trade with ex-top2 −16.92. There is no
remaining untuned knob in this strategy. Every mechanic in the 0802 s4/s6 inventory that was
testable tonight has now been tested and priced against fees.

---
---

# CHECKPOINT 27 — THE ENTRY THRESHOLDS. A ridge, and production sits off it.

Ckpt 19 said the only lever that changes the arithmetic is the ENTRY. Found it without building a
new producer: `sweep_s46_exit.load()` line 90 filters `s46_run` with
`sr_ib_bars>24 AND sr_s1hold>24` — two hardcoded thresholds, NEVER swept.

**s46_run holds 13,633 rows; the production filter keeps 854 (6.3%).** Enormous headroom.
The table also banks the full board at each entry (`sr_r/x/mm/mg` at 15 TFs, `sr_s4m`, `sr_s6mage`,
`sr_s6m`, `sr_init_bull/bear`) — a far richer entry-time feature set than the 18 used in ckpt 21.

Exit held FIXED at x15M30 H2 c360 G30 s6-fallback. SHORT side. Net of 0.110% taker. 49 cells.

## 27a. MARGINAL EFFECT OF s1hold, HOLDING ib FIXED (ex-top2)

| ib> | s1h>0 | s1h>6 | **s1h>12** | s1h>24 | s1h>48 | s1h>96 |
|---|---|---|---|---|---|---|
| 0 | −6.19 | +0.13 | −0.26 | +1.14 | −1.09 | −10.69 |
| 6 | −2.11 | +6.01 | **+12.12** | +9.93 | +3.53 | −11.09 |
| 12 | −3.99 | +5.19 | **+14.45** | +11.42 | +3.91 | −8.72 |
| 24 | −3.54 | +4.82 | **+14.82** | **+6.97 (PRODUCTION)** | +4.60 | +4.89 |
| 48 | −3.45 | +4.77 | **+18.72** | +10.51 | +4.44 | −8.35 |
| 96 | +6.47 | +5.55 | +0.90 | +0.33 | −9.64 | −6.23 |
| 192 | −3.19 | −7.06 | +0.17 | +0.58 | −17.35 | −17.87 |

- `s1hold>0` is NEGATIVE in all 7 ib settings. `s1hold>12` is positive in 6 of 7.
  **Clean INTERIOR optimum — not a boundary artefact.**
- ib in {6,12,24,48} at s1hold>12 all give **8/12 weeks** and ex-top2 **+12.12 to +18.72**. A
  PLATEAU across 4 consecutive settings, which is far more credible than a single cell.
- **Production (24,24) sits OFF the ridge.** s1hold 24 -> 12 at the same ib: +6.97 -> +14.82.

## 27b. HEADLINE CELLS

| cell | n | net mean | net sum | t | weeks+ | ex-top2 | weeks to prove |
|---|---|---|---|---|---|---|---|
| **ib>48, s1hold>12** | 207 | **+0.2517** | +52.1 | 1.31 | **8/12** | **+18.72** | **55** |
| ib>24, s1hold>12 | 210 | +0.2234 | +46.9 | 1.18 | 8/12 | +14.82 | 68 |
| ib>12, s1hold>12 | 211 | +0.1943 | +41.0 | 1.02 | 8/12 | +14.45 | 90 |
| ib>6, s1hold>12 | 216 | +0.1827 | +39.5 | 0.98 | 8/12 | +12.12 | 98 |
| **PRODUCTION ib>24,s1h>24** | 184 | +0.1779 | +32.7 | 0.87 | 7/12 | +6.97 | 123 |
| ib>12, s1hold>192 | 43 | **+0.9423** | +40.5 | 2.13 | 6/9 | +7.69 | **21** |
| ib>6, s1hold>192 | 51 | +0.7778 | +39.7 | **2.04** | 6/10 | +7.55 | 23 |

## 27c. WHY THIS IS NOT ckpt 23 ALL OVER AGAIN

**26 of 47 cells (55%) have ex-top2 > 0.** In ckpt 23's leg family it was **7 of 208 (3%)**.
When the majority of the grid is positive, being near the top is not the same act of selection as
being 1 of 208 in a grid whose median is negative. Combined with the interior optimum in s1hold and
the 4-wide plateau in ib, this is signal-shaped rather than max-of-noise-shaped.

## 27d. WHAT IS STILL NOT TRUE
- best t is **1.31** (or 2.13 at n=43). Nothing here is significant.
- best "weeks to prove" is 55 (or 21 for the small-n cell) — better than 253, still > 12.
- the exit was held fixed at a config that ckpt 23 showed was itself rank 1 of 208. The joint
  selection over entry x exit is not priced. A clean read needs the entry ridge re-tested against a
  RANDOM or MEDIAN exit, not the best one.

## NEXT
1. Re-run 27a with a MEDIAN exit instead of the best one, to strip the joint-selection concern.
2. `sr_s1hold` p50 is 0 and p75 is 29 — the ridge at >12 keeps roughly the top third. Worth knowing
   what s1hold IS mechanically before trusting it (it is banked by the producer, not by this study).
3. The 60+ banked board columns are the proper version of ckpt 21's failed MAE-prediction test.

---
---

# CHECKPOINT 28 — ckpt 27's ridge PARTLY WITHDRAWN. s1hold is real; the optimum at 12 is not.

Test: hold `ib>24` fixed, vary `s1hold`, and re-run across SIX exits — including the bare s6 exit
with no leg and no gate, which cannot have been selected on. SHORT side, net of 0.110% taker.
Cells = ex-top2 (net mean).

| exit | s1h>0 | s1h>6 | s1h>12 | s1h>24 | s1h>48 | s1h>96 |
|---|---|---|---|---|---|---|
| s6 bare (no leg, no gate) | −101.3 (−0.125) | −79.4 (−0.132) | −59.1 (−0.123) | −43.8 (−0.121) | −32.8 (−0.126) | −15.9 (−0.093) |
| x15M30 H2 +G30 [SELECTED] | −3.5 (+0.094) | +4.8 (+0.142) | **+14.8 (+0.223)** | +7.0 (+0.178) | +4.6 (+0.251) | +4.9 (+0.363) |
| x15M H13 +G30 | −11.7 (+0.036) | −8.6 (+0.045) | +7.3 (+0.136) | +0.6 (+0.119) | +8.6 (+0.250) | −1.1 (+0.291) |
| x22M H0 +G30 | −4.8 (+0.094) | −3.8 (+0.099) | **+15.6 (+0.216)** | +5.0 (+0.180) | **+16.9 (+0.330)** | +3.0 (+0.338) |
| x30r H5 +G30 | −40.2 (−0.083) | −33.8 (−0.070) | −14.8 (+0.030) | −22.5 (−0.032) | −9.7 (+0.041) | −13.4 (+0.070) |
| x15b H3 no gate | −71.3 (−0.129) | −69.2 (−0.125) | −53.2 (−0.092) | −47.1 (−0.120) | −31.3 (−0.081) | −7.9 (+0.020) |

## 28a. WHAT SURVIVES — s1hold is a genuine, exit-INDEPENDENT entry-quality filter

| s1hold> | mean ex-top2 over 6 exits | mean weeks+ | exits with ex>0 | bare s6 alone |
|---|---|---|---|---|
| 0 | −38.83 | 4.67 | 0/6 | −101.3 |
| 6 | −31.67 | 4.83 | 1/6 | −79.4 |
| 12 | −14.90 | 5.33 | 3/6 | −59.1 |
| 24 | −16.83 | 4.83 | 3/6 | −43.8 |
| 48 | −7.27 | 5.50 | 3/6 | −32.8 |
| 96 | **−5.07** | 5.83 | 2/6 | **−15.9** |

On the BARE s6 exit it is PERFECTLY MONOTONE: −101.3 -> −79.4 -> −59.1 -> −43.8 -> −32.8 -> −15.9.
No leg, no gate, nothing selected. **s1hold cannot be an artefact of the exit.**

## 28b. WHAT IS WITHDRAWN — the interior optimum at 12

Argmax s1hold by exit: **96, 12, 48, 48, 48, 96**. Only the SELECTED exit peaks at 12.
Ckpt 27a called this "a clean INTERIOR optimum — not a boundary artefact". **That claim is
WITHDRAWN.** It was a property of the exit it was measured against, exactly the joint-selection risk
flagged in ckpt 27d. The exit-independent truth is the weaker, simpler one: **higher s1hold is
monotonically better**, with no interior peak.

Ckpt 27's PLATEAU claim was over `ib` (4 consecutive values at s1h>12), which this test does not
address — it holds ib fixed. That claim stands untested, not refuted.

## 28c. THE EXIT IS ALSO NECESSARY — s1hold cannot rescue a bad one

| exit | ex-top2 at s1h>12 | weeks+ | ever positive? |
|---|---|---|---|
| x22M H0 +G30 | +15.6 | 9/12 | yes |
| x15M30 H2 +G30 | +14.8 | 8/12 | yes |
| x15M H13 +G30 | +7.3 | 7/12 | yes |
| x30r H5 +G30 | −14.8 | 5/12 | no |
| x15b H3 no gate | −53.2 | 3/12 | no |
| **s6 bare** | −59.1 | **0/12** | **no** |

The three that work are ALL M-crossing legs WITH the gate. The r-leg (x30r) and the b-leg (x15b,
ungated) never turn positive at any s1hold. This is the same family that ckpt 25 established by
paired control and that dominated ckpt 23c's top-15 — three independent lines now converge on
**M-crossing leg + G30 gate + high s1hold**.

## 28d. STANDING
- established: G30 gate (ckpt 25, 104/104 paired); s1hold as entry filter (ckpt 28a, monotone on an
  unselected exit); M-crossing legs required (ckpt 28c, 3 lines).
- withdrawn: x15M30 as THE config (ckpt 23); s1hold interior optimum at 12 (ckpt 28b).
- still true: nothing is statistically significant. Best t tonight is 1.31 at n=207.

## NEXT
1. Re-test ckpt 27's `ib` PLATEAU the same way — across the 6 exits — since that claim is still
   standing on the selected exit alone.
2. `sr_s1hold` is banked by the producer and I have not read what it MEASURES. Establish that before
   trusting it further; it is now load-bearing in the story.

---
---

# CHECKPOINT 29 — sr_s1hold DEFINED, and the ib PLATEAU re-tested: ib>48 is a REAL interior optimum.

## 29a. WHAT sr_s1hold ACTUALLY MEASURES (read from source — it is now load-bearing)

`build_s46.py:23` — **item 14** of Joe's numbered inventory:
> `sr_s1hold` item 14 - bars s1Mage held within 15 points of the breach boundary. Its length is the wob

`build_s46_window.py:9` gives the units:
> item 14  sr_s1hold > 24 bars = 120 s   s1Mage (bb 37|0.83|close @TF1) held within 15 board points

- **s1Mage** = `bb 37|0.83|close` @ TF1 — the fastest board's Mage line
- **15 points** — board-point distance from the breach boundary
- **units** — 5 s bars. 24 bars = 120 s. s1hold > 96 = 480 s = 8 min.

So s1hold counts how long the fastest board's Mage line HUGGED the breach boundary before breaking.
A coiling / consolidation measure: longer coil before the break. That "longer coil -> better trade"
works as an entry filter is mechanically coherent, and it is Joe's own item 14 — not a construct of
this study. (Joe's word for its length is "the wob".)

## 29b. THE ib RE-TEST — s1hold>12 fixed, ib varied, across all 6 exits. cells = ex-top2 (netmn)

| exit | ib>0 | ib>6 | ib>12 | ib>24 | ib>48 | ib>96 | ib>192 |
|---|---|---|---|---|---|---|---|
| s6 bare | −83.3 (−0.117) | −69.8 (−0.116) | −63.8 (−0.123) | −59.1 (−0.123) | −56.8 (−0.122) | −63.1 (−0.149) | −53.0 (−0.152) |
| x15M30 H2 +G30 | −0.3 (+0.108) | +12.1 (+0.183) | +14.4 (+0.194) | +14.8 (+0.223) | **+18.7 (+0.252)** | +0.9 (+0.175) | +0.2 (+0.142) |
| x15M H13 +G30 | −15.4 (+0.025) | +0.6 (+0.100) | +7.9 (+0.123) | +7.3 (+0.136) | **+11.1 (+0.159)** | +1.8 (+0.124) | −8.0 (+0.062) |
| x22M H0 +G30 | +1.5 (+0.123) | +12.0 (+0.181) | +14.7 (+0.194) | +15.6 (+0.216) | **+17.2 (+0.232)** | +4.5 (+0.183) | +2.5 (+0.160) |
| x30r H5 +G30 | −30.8 (−0.038) | −20.6 (−0.006) | −14.9 (+0.015) | −14.8 (+0.030) | **−3.7 (+0.081)** | −14.6 (+0.031) | −27.8 (−0.047) |
| x15b H3 nogate | −59.8 (−0.102) | −59.7 (−0.101) | −51.6 (−0.095) | −53.2 (−0.092) | **−44.4 (−0.070)** | −55.7 (−0.120) | −50.1 (−0.122) |

### exit-independent view

| ib> | mean ex-top2 | mean net mean | exits with ex>0 |
|---|---|---|---|
| 0 | −31.33 | −0.0001 | 1/6 |
| 6 | −20.91 | +0.0399 | 3/6 |
| 12 | −15.53 | +0.0513 | 3/6 |
| **24 (PRODUCTION)** | −14.90 | +0.0651 | 3/6 |
| **48** | **−9.65** | **+0.0887** | 3/6 |
| 96 | −21.03 | +0.0407 | 3/6 |
| 192 | −22.72 | +0.0071 | 2/6 |

## 29c. WHY THIS ONE IS WELL-CONTROLLED (unlike ckpt 28b's withdrawn s1hold optimum)

**ib>48 is the argmax for FIVE of six exits.** Argmax by exit: 192(s6 bare, negative throughout),
**48, 48, 48, 48, 48**.

The decisive part: the two NET-NEGATIVE exits agree. x30r H5 (peaks at −3.75) and x15b H3 ungated
(peaks at −44.39) never make money at any threshold, yet both still peak at ib>48. A threshold
preferred by mechanics that LOSE cannot be an artefact of selecting profitable ones.

Under a null of random argmax over 7 candidates, 5-of-6 agreement on one specific value is p ~ 0.002
(7 * C(6,5) * (1/7)^5 * (6/7)). **That p is inflated** because the six exits share most of their
underlying trades and are therefore correlated — the honest weight is carried by the two structurally
different, losing legs agreeing, not by the arithmetic.

Both metrics rise to ib>48 and fall on BOTH sides. **This is a true interior optimum**, which is
exactly what ckpt 28b showed s1hold>12 was NOT.

## 29d. TWO CONCRETE ENTRY FINDINGS

| threshold | production | measured better | evidence |
|---|---|---|---|
| `sr_ib_bars` | **> 24** | **> 48** | interior optimum, argmax for 5/6 exits incl. 2 losing ones (29c) |
| `sr_s1hold` | **> 24** | **higher** (48-96) | monotone on the unselected bare-s6 exit, −101.3 -> −15.9 (28a) |

NOT a recommendation to change production — that is Joe's call and these are 12-week measurements
with t < 1.4. Recording what the data says.

## 29e. STANDING AFTER 29 CHECKPOINTS
- **established**: G30 gate (104/104 paired, ckpt 25); s1hold as entry filter (monotone on an
  unselected exit, ckpt 28a); M-crossing legs required (3 independent lines, ckpt 28c);
  **ib>48 interior optimum** (5/6 exits incl. losers, ckpt 29c).
- **withdrawn**: x15M30 as THE config (ckpt 23); s1hold interior optimum at 12 (ckpt 28b);
  ckpt 22's short-side numbers (double-filter bug, ckpt 23a).
- **dead**: every exit mechanic in ckpt 25e's table.
- **still true**: NOTHING here is statistically significant. Best t tonight is 1.31 at n=207.

---
---

# CHECKPOINT 30 — the banked board columns. sr_x1 and sr_mg15 hold across all six exits.

Ckpt 21 asked "is MAE predictable at entry" with 18 features and said no. `s46_run` banks 60+ board
columns AT the entry bar (`sr_r/x/mm/mg` at 15 TFs, `sr_s4m`, `sr_s6mage`, `sr_s6m`,
`sr_init_bull/bear`, `sr_dwell_bars`, `sr_m4*`) — all causal. This is the proper version of that test.

Explicit TWO-STAGE design: screen on one exit, then validate survivors on all six.

## 30a. STAGE 1 SCREEN — x15M30 H2 +G30, ib>48, s1hold>12, SHORT, 207 trades, 58 columns

Baseline no split: n 207, netmn +0.2517, ex-top2 +18.72.

| feature | median | nHI | netmn HI | ex HI | wks+ | nLO | netmn LO | ex LO | wks+ |
|---|---|---|---|---|---|---|---|---|---|
| sr_mm30 | 1.09 | 104 | −0.2311 | −44.86 | 4/12 | 103 | +0.7392 | +40.21 | 10/12 |
| sr_x1 | −37.81 | 104 | +0.5921 | +26.31 | 9/12 | 103 | −0.0920 | −37.96 | 4/12 |
| sr_mm120 | 14.12 | 104 | +0.5521 | +25.09 | 10/12 | 103 | −0.0516 | −26.20 | 4/12 |
| sr_r1 | 27.91 | 104 | −0.1778 | −27.50 | 6/12 | 103 | +0.6854 | +22.99 | 7/12 |
| sr_mg120 | 33.80 | 104 | +0.4413 | +25.97 | 9/12 | 103 | +0.0602 | −19.54 | 3/12 |
| sr_dwell_bars | 4.00 | 108 | +0.4582 | +26.26 | 9/12 | 99 | +0.0264 | −17.67 | 5/12 |
| sr_mg15 | 27.59 | 104 | +0.4538 | +23.13 | 9/12 | 103 | +0.0477 | −9.65 | 7/12 |

58 columns on 207 trades WILL produce large gaps by chance. Nothing here is believed yet.

## 30b. STAGE 2 — do the splits hold on the other five exits?

| feature | HIGH better on net mean | d(net mean) range | d(ex-top2) |
|---|---|---|---|
| **sr_x1** | **6/6** | +0.046 to **+0.629** | +8.97 to **+68.94**, ALL positive |
| **sr_mg15** | **6/6** | +0.059 to +0.370 | +10.57 to +53.77, ALL positive |
| sr_dwell_bars | 5/6 | −0.018 to +0.194 | all 6 positive |
| sr_mg60 | 5/6 | −0.051 to +0.272 | 5 positive |
| sr_mg30 | 4/6 | −0.050 to +0.315 | 4 positive |
| sr_mm30 | 4/6 | −0.303 to +0.075 | 3 positive |
| **sr_mg120** | **1/6** | −0.217 to +0.110 | 4 positive |

### sr_x1 detail (the strongest)

| exit | netmn HI | netmn LO | d | ex HI | ex LO | d(ex) |
|---|---|---|---|---|---|---|
| s6 bare | −0.1011 | −0.1466 | +0.0455 | −26.96 | −35.93 | +8.97 |
| x15M30 H2 +G30 | +0.6482 | +0.0190 | +0.6292 | +45.78 | −23.16 | +68.94 |
| x15M H13 +G30 | +0.4336 | +0.0415 | +0.3921 | +28.24 | −20.13 | +48.37 |
| x22M H0 +G30 | +0.5377 | +0.0611 | +0.4766 | +34.50 | −16.04 | +50.54 |
| x30r H5 +G30 | +0.3418 | −0.1293 | +0.4712 | +12.99 | −35.07 | +48.05 |
| x15b H3 nogate | +0.0672 | −0.2406 | +0.3079 | −12.47 | −61.21 | +48.74 |

`sr_x1` = the `x` line (`bb 4|0.37`) at TF1, banked at the entry bar. For a SHORT, **higher x1 is
better** (median −37.52). It holds on the bare s6 exit and on both LOSING legs.

## 30c. TWO CORRECTIONS THIS TEST FORCED ON ME

1. **"All four Mage timeframes agree" was wrong.** I said that from the SCREEN. Across all six exits
   mg15 holds 6/6 but decays with timeframe: mg30 4/6, mg60 5/6, **mg120 1/6**. Fast Mage matters,
   slow Mage does not. The coherence I claimed was an artefact of the single screening exit.
2. **The screen's BIGGEST gap failed to replicate.** `sr_mm30` showed an 85-point split — the largest
   of 58 columns — and in stage 2 it FLIPS DIRECTION and holds only 4/6. Exactly the contamination
   predicted when the screen was run. This is evidence the two-stage design has discriminating power
   rather than rubber-stamping whatever the screen produced.

## 30d. THE CAVEAT I CANNOT DISSOLVE

The six exits share most of their underlying trades, so **6/6 is not six independent tests**. It
rules out "this is an artefact of the chosen exit" — which is what it was designed for — but it does
NOT establish the feature generalises. The genuinely independent axis is TIME, not exit.

## NEXT
Fit the split threshold on the FIRST half of the window and apply it, unchanged, to the SECOND half.
That is the only test left tonight whose failure mode is not shared-trade correlation. Run it on
sr_x1, sr_mg15 and sr_dwell_bars.

---
---

# CHECKPOINT 31 — TIME-SPLIT OOS, and CHECKPOINT 32 — THE FULL STACK. t 3.14 after fees.

## 31. TIME-SPLIT: threshold FIT on the first half, APPLIED unchanged to the second

537 short entries at ib>48, s1h>12. Split at **2026-06-24 15:46:20 UTC**.

| feature | OOS: HIGH better | IS effect (4 exits) | OOS effect (4 exits) | verdict |
|---|---|---|---|---|
| **sr_x1** | **4/4** | +0.05 / +0.38 / +0.39 / +0.27 | +0.06 / **+0.92** / **+0.61** / **+0.75** | positive in BOTH halves, all exits |
| **sr_mg15** | **4/4** | +0.05 / +0.14 / +0.02 / +0.22 | +0.05 / +0.18 / +0.41 / +0.38 | positive in BOTH halves, all exits |
| sr_dwell_bars | 4/4 | +0.08 / **−0.15** / **−0.15** / +0.05 | +0.09 / +0.45 / +0.31 / +0.34 | SIGN FLIPS — unstable |
| sr_mg60 | 3/4 | −0.00 / **−0.13** / **−0.53** / **−0.12** | −0.07 / +0.44 / +0.47 / +0.30 | SIGN FLIPS — unstable |

**sr_x1's effect GREW out of sample** (+0.378 -> +0.918 on x15M30; +0.275 -> +0.746 on x30r) — the
opposite of the overfitting signature — and it holds on the BARE s6 exit with no leg and no gate.

Two features "passing 4/4 OOS" are NOT equal: dwell_bars and mg60 pass only because they were
NEGATIVE in-sample and positive out. A sign flip is instability, not evidence. Only sr_x1 and
sr_mg15 are positive in both halves on every exit.

## 32. THE FULL STACK — one filter at a time, SHORT side, net of 0.110% taker

x1/mg15 thresholds fit on the FIRST HALF ONLY and never refit.

### exit = x15M30 H2 + G30 gate, s6-fallback

| entry filter | n | net mean | net sum | t | weeks+ | ex-top2 | IS | OOS | weeks* |
|---|---|---|---|---|---|---|---|---|---|
| production ib>24 s1h>24 | 184 | +0.1779 | +32.7 | 0.87 | 7/12 | +6.97 | +0.277 | +0.078 | 123 |
| + ib>48 | 177 | +0.2179 | +38.6 | 1.03 | 7/12 | +10.51 | +0.319 | +0.118 | 88 |
| + ib>48 s1h>12 | 207 | +0.2517 | +52.1 | 1.31 | 8/12 | +18.72 | +0.432 | +0.073 | 55 |
| **+ x1 >= −36.82** | **150** | **+0.6483** | **+97.2** | **3.14** | **10/12** | **+45.15** | +0.746 | **+0.551** | **10** |
| + x1 + mg15 >= 33.13 | 88 | +0.7662 | +67.4 | 3.22 | 8/12 | +27.63 | +0.744 | +0.789 | 9 |

### all three M-legs, at the x1 stack

| exit | n | net mean | net sum | t | weeks+ | ex-top2 | IS | OOS | weeks* |
|---|---|---|---|---|---|---|---|---|---|
| x15M30 H2 +G30 | 150 | +0.6483 | +97.2 | **3.14** | 10/12 | +45.15 | +0.746 | +0.551 | 10 |
| x22M H0 +G30 | 154 | +0.5370 | +82.7 | 2.73 | 10/12 | +33.86 | +0.650 | +0.424 | 13 |
| x15M H13 +G30 | 164 | +0.4616 | +75.7 | 2.67 | 8/12 | +26.16 | +0.490 | +0.433 | 13 |

### NEGATIVE CONTROL — same stack, LONG side (filters were fit on shorts)

| exit | n | net mean | t | weeks+ | ex-top2 |
|---|---|---|---|---|---|
| x15M30 H2 | 188 | **−0.1100** | −0.51 | 8/12 | −37.86 |
| x22M H0 | 198 | **−0.0818** | −0.43 | 7/12 | −39.34 |

The control PASSES: filters fit on shorts do not transfer to longs. This rules out a generic
"fewer trades = better" artefact, which would have lifted both sides.

## 32a. WHAT sr_x1 IS
`sr_x1` = the **x line (`bb 4|0.37`) at TF1**, banked at the entry bar by the producer. For a SHORT,
**higher x1 is better**; threshold −36.82 (fit on the first half; the second half's own median would
have been −37.81, so the two halves nearly agree on where the median sits).

## 32b. mg15 ADDS NOTHING
It cuts n by ~40% and LOWERS ex-top2 on all three legs (+45.15 -> +27.63, +33.86 -> +27.39,
+26.16 -> +7.53). It is redundant with x1. **The filter is x1 alone.**

## 32c. THREE CAVEATS, NOT BURIED
1. The x1 threshold was fit on FIRST-half data, so the **IS column (+0.746) is in-sample by
   construction. +0.551 OOS is the honest number.**
2. x1 survived a screen of **58 columns**. The ckpt 31 time-split is genuine OOS evidence for the
   THRESHOLD, but the CHOICE of x1 from 58 candidates is still selection-exposed.
3. One 12-week window, one instrument, one side. weeks* 10 means it is only just at the edge of
   provability with the data that exists.

## 32d. THE ARITHMETIC HAS CHANGED
Ckpt 19 said: sd 2.390, cost 0.110, n* 4,701, **253 weeks to prove**. With the x1 stack: n* implies
**10 weeks**. The binding constraint identified in ckpt 19 — "the entry is rich, the exit is
binding" — turned out to be half right: the exit family was closed (ckpt 25e), and the actual lever
was ENTRY SELECTION, exactly as ckpt 19's lever #3 predicted.

## STANDING
- **established**: G30 gate (104/104 paired); M-crossing legs required (3 lines); ib>48 interior
  optimum (5/6 exits incl. losers); s1hold monotone on an unselected exit; **sr_x1 as an entry
  filter (time-split OOS, effect grew, negative control passes)**.
- **withdrawn**: x15M30 as THE config; s1hold interior optimum at 12; ckpt 22's short-side numbers.
- **dead**: every exit mechanic in ckpt 25e.
- **new**: the full stack reaches t 3.14 net of fees, 10/12 weeks positive, on 150 trades.

---
---

# CHECKPOINT 33 — NULL CALIBRATION. Ambiguous, and I am not claiming the p-value.

Ran the IDENTICAL two-stage + time-split pipeline on ALL 60 banked columns, to price the fact that
x1 was CHOSEN from 58 candidates (ckpt 32c caveat 2). Bar = the one x1 cleared: consistent direction
in BOTH halves on ALL 4 exits.

| | value |
|---|---|
| columns tested | 60 |
| **columns clearing the bar** | **3 (5.0%)** |
| expected under an independent-coin null | 0.5 -> p ~ 0.014 |

| feature | exits | IS ok | OOS ok | dir | mean d(OOS) |
|---|---|---|---|---|---|
| **sr_x1** | 4 | 4 | 4 | HI | **+0.5835** |
| sr_ib_bars | 4 | 0 | 0 | LO | −0.2809 |
| sr_mg15 | 4 | 4 | 4 | HI | +0.2542 |

## 33a. WHY p ~ 0.014 IS NOT TRUSTWORTHY

That p assumes the 8 signs (4 exits x 2 halves) are independent coin flips. **They are not** — the
four exits share most of their underlying trades.

- exits INDEPENDENT: P(clear) = 2*(1/2)^8 = 0.78% -> expect 0.5 of 60 -> observed 3 is 6x chance
- exits PERFECTLY CORRELATED: effectively 2 flips, P(clear) = 2*(1/2)^2 = 50% -> **expect 30 of 60**
  -> observed 3 is far BELOW chance

The truth is between. 3 sits inside [0.5, 30]. **The null calibration does NOT establish
significance for sr_x1.** Recording this rather than quoting the flattering end of the range.

## 33b. WHAT IT DOES SHOW

Only 5% of columns clear, far below the 50% a correlated-exit null predicts. Most features FLIP
direction between halves — which is the fingerprint of the period effect established in ckpt 21b
(all 18 features there showed negative IS / positive OOS). The bar is genuinely hard to clear.

## 33c. AN UNPLANNED POSITIVE CONTROL

`sr_ib_bars` is one of the 3 clears, in the **LO** direction: within the already-filtered ib>48
population, LOWER ib is better. That is exactly what an INTERIOR OPTIMUM AT 48 predicts — and ckpt
29c established that peak independently, from 5-of-6 exit argmaxes including two LOSING exits.

The pipeline recovered a known-good feature in the direction that prior, independent evidence
requires. That is a positive control I did not design and got for free, and it is the strongest
reason to think the pipeline is measuring something rather than shuffling noise.

## 33d. HONEST STATUS OF sr_x1
- largest OOS effect of any of 60 columns (+0.5835, more than double the next)
- positive in both halves on all 4 exits incl. the bare s6 exit
- effect GREW out of sample (ckpt 31)
- negative control on the long side passes (ckpt 32)
- **but**: chosen from 58 candidates, and the null calibration cannot rule out chance at this
  correlation structure. It is a STRONG CANDIDATE, not an established edge.

## NEXT
Same discipline that was applied to `ib` in ckpt 29: is the x1 threshold a PLATEAU or a SPIKE? A
single working threshold on a screened feature is what a fluke looks like; a broad monotone response
across many thresholds is what a real one looks like.

---
---

# CHECKPOINT 34 — x1 IS A DOSE-RESPONSE, NOT A THRESHOLD. Strongest evidence of the night.

Ckpt 29's discipline applied to x1: plateau or spike? Population = ib>48, s1h>12, SHORT, 537 entries.

## 34a. NET MEAN (and t) BY x1 PERCENTILE CUTOFF

| keep x1 >= | thresh | s6 bare | x15M30 H2 | x22M H0 | x15M H13 | x30r H5 |
|---|---|---|---|---|---|---|
| p0 | −58.05 | −0.122 t−5.05 | +0.252 t1.31 | +0.232 t1.32 | +0.159 t0.99 | +0.081 t0.48 |
| p10 | −52.38 | −0.128 t−5.13 | +0.321 t1.64 | +0.270 t1.50 | +0.193 t1.19 | +0.108 t0.65 |
| p20 | −48.92 | −0.120 t−4.41 | +0.399 t2.06 | +0.318 t1.67 | +0.229 t1.34 | +0.154 t0.86 |
| p30 | −44.53 | −0.110 t−3.82 | +0.465 t2.38 | +0.365 t1.94 | +0.261 t1.51 | +0.217 t1.21 |
| p40 | −40.62 | −0.100 t−3.16 | +0.567 t2.97 | +0.450 t2.45 | +0.365 t2.18 | +0.294 t1.71 |
| p50 | −37.52 | −0.101 t−2.88 | +0.648 t3.16 | +0.538 t2.75 | +0.434 t2.41 | +0.342 t1.82 |
| p60 | −32.91 | −0.088 t−2.45 | +0.713 t3.20 | +0.585 t2.78 | +0.471 t2.52 | +0.340 t1.71 |
| **p70** | **−28.92** | **−0.072 t−1.73** | **+0.762 t2.99** | **+0.660 t2.75** | **+0.518 t2.45** | **+0.424 t1.89** |
| p80 | −24.44 | −0.049 t−0.88 | +0.612 t2.22 | +0.529 t2.06 | +0.375 t1.55 | +0.238 t1.04 |
| p90 | −17.02 | −0.154 t−2.88 | +0.563 t1.41 | +0.647 t1.78 | +0.582 t1.56 | +0.226 t0.75 |

## 34b. ex-top2 (weeks positive) BY x1 PERCENTILE

| keep x1 >= | s6 bare | x15M30 H2 | x22M H0 | x15M H13 | x30r H5 |
|---|---|---|---|---|---|
| p0 | −56.8 (0/12) | +18.7 (8/12) | +17.2 (9/12) | +11.1 (7/12) | −3.7 (6/12) |
| p20 | −46.2 (0/12) | +40.6 (9/12) | +26.2 (8/12) | +18.8 (7/12) | +3.0 (6/12) |
| p40 | −31.0 (1/12) | +40.6 (10/12) | +27.6 (9/12) | +21.4 (7/12) | +11.8 (8/12) |
| p50 | −27.0 (1/12) | +45.8 (10/12) | +34.5 (10/12) | +28.2 (8/12) | +13.0 (7/12) |
| **p60** | −21.1 (2/12) | **+53.2 (10/12)** | +36.1 (9/12) | +26.2 (8/12) | +11.8 (7/12) |
| **p70** | −16.7 (3/12) | +47.2 (10/12) | **+38.5 (9/12)** | **+29.5 (10/12)** | **+19.6 (8/12)** |
| p80 | −11.3 (2/12) | +22.3 (8/12) | +17.3 (8/12) | +9.1 (8/12) | −0.1 (9/12) |
| p90 | −8.9 (2/12) | −2.2 (7/12) | +2.3 (8/12) | −0.2 (7/12) | −5.0 (7/12) |

## 34c. WHY THIS IS THE STRONGEST RESULT OF THE NIGHT

**Monotone increasing from p0 to p70 on ALL FIVE exits, with no reversal anywhere.**
- the BARE s6 exit improves −0.122 -> −0.072 (no leg, no gate, nothing selected)
- **x30r H5, a leg that NEVER makes money, improves +0.081 -> +0.424 — a 5x gradient**
- ex-top2 improves monotonically on all 5 as well, and s6 bare goes 0/12 -> 3/12 weeks positive

A fluke threshold produces a SPIKE. This is a GRADIENT: more x1, more return, continuously, across
five mechanics that share nothing but the entries. Selection can manufacture a peak; it cannot
easily manufacture a monotone dose-response that also lifts the mechanics that lose money.

This is the answer to ckpt 33's ambiguity. The null calibration could not separate signal from
chance because it only asked "does one threshold work". The dose-response asks "does MORE of the
feature give MORE return", and the answer is yes, ten times over, on five exits.

## 34d. THE THRESHOLD I USED WAS CONSERVATIVE
−36.82 sits at **p50**. The response peaks at **p60-p70**:

| at p70 (x1 >= −28.92) | n | net mean | t | weeks+ | ex-top2 |
|---|---|---|---|---|---|
| x15M30 H2 +G30 | ~90 | **+0.762** | 2.99 | 10/12 | +47.2 |
| x22M H0 +G30 | ~92 | +0.660 | 2.75 | 9/12 | +38.5 |
| x15M H13 +G30 | ~97 | +0.518 | 2.45 | 10/12 | +29.5 |

Beyond p80 it collapses (p90: x15M30 +0.563 t1.41, ex-top2 −2.2) — an interior optimum, and the
decline is where sample size runs out.

## 34e. THE COMPLETE PICTURE AFTER 34 CHECKPOINTS

Everything that survived, each with the control that established it:

| finding | evidence |
|---|---|
| G30 momo gate helps the SHORT side | 104/104 paired leg x H, +0.0734/trade (ckpt 25) |
| gate is already optimally configured | 84-config sweep; only 3 beat it, by <=+0.0165 (ckpt 26) |
| M-crossing legs are required (not b, not r) | 3 independent lines (ckpt 23c, 25, 28c) |
| ib>48 is an interior optimum | argmax for 5/6 exits incl. 2 LOSING ones (ckpt 29c) |
| s1hold is a real entry filter | monotone on the unselected bare-s6 exit (ckpt 28a) |
| **sr_x1 is a dose-response entry filter** | **monotone p0->p70 on 5/5 exits incl. 2 losers (ckpt 34)** |
| the whole stack clears fees | t 3.14 net, 10/12 weeks, OOS +0.551 (ckpt 32) |
| long side does NOT work | negative control, −0.110 / −0.082 (ckpt 32) |

And what it cost: the exit family is closed (ckpt 25e lists 7 dead mechanics), three claims were
retracted (ckpt 23a, 28b, 33d), and the original framing — that this was an EXIT problem — was
wrong. It was an entry-selection problem the whole time, exactly as ckpt 19's lever #3 predicted.

---
---

# CHECKPOINT 35 — CAUSALITY AUDIT of s46_run. Three columns are LOOKAHEAD. The result is clean.

Joe's standing constraint: "our codebase is not at all lookahead-friendly" and "bank causal
timestamps first". Before trusting ckpt 30-34, verified every column used, from source.

## 35a. HOW THE LADDER IS BANKED — build_s46.py:257-261

```python
lad = []
for t_ in RUNGS:                 # RUNGS = [1,2,4,6,10,15,22,30,45,60,90,120]
    for _p, kk_ in LINES:        # LINES = [('r','r'),('x','x'),('mm','m'),('mg','M')]
        v_ = E[t_][kk_][a]       # indexed at `a` = the RUN START = the entry bar
        lad.append(float(v_) if np.isfinite(v_) else None)
```

`sr_x1` = `E[1]['x'][a]` — a POINT-IN-TIME read of the x line (`bb 4|0.37`) at TF1 on the entry bar.
No window, no forward span. **CAUSAL.**

## 35b. COLUMN-BY-COLUMN VERDICT

| column | code | causal? |
|---|---|---|
| `sr_x1`, `sr_mg15`, all 48 ladder cols | `E[t_][kk_][a]` | **YES** — read at the entry bar |
| `sr_ib_bars` | `int(ibrun[a-1])` | **YES** — strictly before entry; `ibrun` comment says "causal" |
| `sr_s1hold` | `int(S1H[sgn][a-1])` | **YES** — running count, read strictly before entry |
| `sr_alt` | `M4[prev[1]:a+1]` | **YES** — spans the PRIOR run only |
| `sr_s4m`, `sr_s6mage`, `sr_s6m`, `sr_m4`, `sr_px` | `...[a]` | **YES** — at the entry bar |
| `sr_init_bull/bear[90]` | `INIT[...][a]` | **YES** — at the entry bar |
| **`sr_dwell_bars`** | `int(b - a + 1)` | **NO — LOOKAHEAD.** the run's total length, known only at bar `b` |
| **`sr_m4_min`** | `seg = M4[a:b+1]; seg.min()` | **NO — LOOKAHEAD.** spans forward to `b` |
| **`sr_m4_max`** | `seg = M4[a:b+1]; seg.max()` | **NO — LOOKAHEAD.** spans forward to `b` |
| `sr_end_ms`, `sr_end_utc` | `ts[b]` | **NO** — but excluded from every test as metadata |

## 35c. WHAT THIS CONTAMINATED, AND WHAT IT DID NOT

**CONTAMINATED (must never be used as entry features):**
- `sr_dwell_bars` — I tested it in ckpt 30 and 31, where it "passed 4/4 OOS". I had already set it
  aside for SIGN-FLIPPING between halves (ckpt 31), but that was the wrong reason. The right reason
  is that **it cannot be known at entry**. Any result built on it is void.
- `sr_m4_min` — appeared in the ckpt 30a screen table (low half +0.4591, ex +29.48). Void.
- `sr_m4_max` — same construction, same verdict.

**NOT CONTAMINATED — the headline result stands:**
- the three columns that cleared ckpt 33's null calibration are `sr_x1`, `sr_ib_bars`, `sr_mg15` —
  **all causal.**
- `sr_dwell_bars` did NOT clear that bar, so it never entered the final finding.
- the ckpt 32 stack (ib>48, s1hold>12, x1>=−36.82) and the ckpt 34 dose-response use **only causal
  inputs**.

## 35d. WHY THE AUDIT WAS WORTH RUNNING
The lookahead columns sit in the SAME INSERT statement as the causal ones, with no naming convention
separating them. Nothing in the schema, the column names, or the table docs distinguishes
`sr_dwell_bars` (forward-looking) from `sr_ib_bars` (backward-looking) — the names are nearly
identical and one character of code (`b` vs `a-1`) is the whole difference. Anyone mining this table
in future will hit the same trap.

**RECOMMENDATION for Joe (not applied — his call):** the three forward-looking columns are legitimate
for post-hoc ANALYSIS of a completed run, which is presumably why they were banked. They are not
legitimate as entry features. Worth a comment at build_s46.py:257 marking the boundary, or a naming
convention (`sr_post_*`) so the distinction is visible at the query.

---
---

# CHECKPOINT 36 — WALK-FORWARD. The strongest honest validation. t 2.26 out of sample.

For each test week W: fit the x1 percentile threshold on ALL WEEKS BEFORE W, apply it unchanged to W.
Nothing from W or later touches the fit. Min 4 training weeks. SHORT, no-pyramid, ib>48 s1h>12,
net of 0.110% taker.

## 36a. POOLED WALK-FORWARD

| fit | exit | n | net mean | net sum | t | weeks > 0 |
|---|---|---|---|---|---|---|
| p50 | x15M30 H2 FILTERED | 104 | +0.4098 | +42.6 | 1.83 | 7/8 |
| p50 | x15M30 H2 unfiltered | 143 | +0.1006 | +14.4 | 0.47 | 4/8 |
| p60 | x15M30 H2 FILTERED | 96 | +0.5287 | +50.8 | 2.19 | 7/8 |
| **p70** | **x15M30 H2 FILTERED** | **83** | **+0.6085** | **+50.5** | **2.26** | **7/8** |
| p70 | x15M30 H2 unfiltered | 143 | +0.1006 | +14.4 | 0.47 | 4/8 |
| p70 | x22M H0 FILTERED | 85 | +0.5088 | +43.2 | 2.16 | 6/8 |
| p70 | x22M H0 unfiltered | 146 | +0.1252 | +18.3 | 0.71 | 6/8 |
| p70 | x15M H13 FILTERED | 89 | +0.3804 | +33.9 | 2.00 | 7/8 |
| p70 | x15M H13 unfiltered | 161 | +0.0545 | +8.8 | 0.35 | 4/8 |

**All three legs clear t >= 2.0 strictly out of sample, at 4-7x their unfiltered baseline.**
The threshold improves monotonically p50 -> p60 -> p70 in walk-forward too (+0.410, +0.529, +0.609),
matching the ckpt 34 dose-response measured in-sample.

## 36b. WEEK BY WEEK (p70, x15M30) — filtered vs all

| test week | n_train | n | filtered | unfiltered |
|---|---|---|---|---|
| 06-11 | 177 | 9 | +0.373 | +0.440 |
| 06-18 | 220 | 16 | +0.514 | +0.221 |
| 06-25 | 271 | 10 | **+1.900** | −0.161 |
| 07-02 | 318 | 11 | +0.795 | −0.220 |
| 07-09 | 373 | 10 | +0.504 | −0.004 |
| **07-16** | 419 | 12 | **−0.029** | **+0.422** |
| 07-23 | 472 | 11 | +0.505 | +0.117 |
| 07-30 | 524 | 4 | +0.232 | −0.320 |

## 36c. EX-TOP2 IN WALK-FORWARD — the metric that killed everything else

p70 x15M30: total +50.5 over 83 trades. Top-2 weeks (06-25 = +19.00, 07-02 = +8.75) = +27.75.
**Remaining 6 weeks: +22.75 over 62 trades = +0.367/trade net — 3.3x the 0.110 cost line.**

The two-week concentration that killed ckpt 22 is still present in magnitude, but the residual is
now solidly positive rather than −21.2.

## 36d. HONEST DELTAS
- in-sample t **3.14** (ckpt 32) -> walk-forward t **2.26**. The drop is the selection premium.
- **07-16 is a week where the filter actively UNDERPERFORMS** (−0.029 filtered vs +0.422 all). It is
  not universally better; it is better on average and in 7 of 8 weeks.
- 8 test weeks only (4 held back for training). n 83 at p70.

## 36e. THIS IS THE NUMBER TO QUOTE
Every earlier headline tonight was in-sample or exit-selected. **t 2.26, +0.609/trade net, 7/8 weeks
positive, +0.367/trade excluding the two best weeks — with the threshold never seeing the future.**
That is the deliverable.

---
---

# CHECKPOINT 37 — THE LONG SIDE. sr_x90 mirrors sr_x1, and the two sides tell ONE story.

The ckpt 32 "long side does not work" test used the SHORT-fitted threshold. That is not the same as
giving longs their own screen. Ran the full pipeline independently on longs.
**LOOKAHEAD columns (sr_dwell_bars, sr_m4_min, sr_m4_max) excluded by construction this time.**

## 37a. INDEPENDENT LONG SCREEN — best thresholds ib>24 s1h>48, 265 entries, 60 causal columns

8 columns clear the bar (13%) vs 3 (5%) on shorts. **More clears is NOT better evidence.**

| feature | dir | mean d(OOS) |
|---|---|---|
| sr_r6 | LO | −0.2735 |
| sr_m4 | HI | +0.2559 |
| sr_mg4 | HI | +0.2559 |
| sr_x90 | LO | −0.2361 |
| sr_mm1 | HI | +0.2343 |
| sr_s6mage | LO | −0.2213 |
| sr_mg6 | LO | −0.2213 |
| sr_mm22 | LO | −0.1575 |

**DUPLICATE COLUMNS FOUND**: `sr_m4` == `sr_mg4` (identical +0.2559) and `sr_s6mage` == `sr_mg6`
(identical −0.2213). The scalar columns are the SAME VALUES as ladder rungs — M4 is the Mage at TF4,
s6Mage is the Mage at TF6. So 8 clears are really ~6 distinct signals. Worth knowing before anyone
counts columns as independent evidence.

Largest long-side effect is 0.2735 against sr_x1's **0.5835** on shorts.

## 37b. THE DOSE-RESPONSE TEST SEPARATES THEM (again)

`sr_x90` (keep LO), net mean by cutoff:

| keep x90 <= | s6 bare | x15M30 H2 | x22M H0 | x15M H13 | x30r H5 |
|---|---|---|---|---|---|
| p90 | −0.013 | +0.246 | +0.158 | +0.100 | +0.096 |
| p80 | −0.004 | +0.320 | +0.240 | +0.186 | +0.194 |
| p60 | +0.046 | +0.571 | +0.363 | +0.452 | +0.368 |
| p50 | +0.051 | +0.819 | +0.631 | +0.664 | +0.639 |
| p20 | +0.052 | +0.833 | +0.777 | +0.782 | +0.400 |
| p10 | +0.139 | **+1.308** | **+1.436** | **+1.443** | **+0.851** |

Monotone across ALL FIVE exits incl. bare s6 and the LOSING x30r leg. Same signature as sr_x1.

**The others are SPIKES, i.e. noise:**
- `sr_m4`: rises to p40 (+0.470), FALLS to p80 (−0.078), jumps at p90 (+0.621). Not monotone.
- `sr_mm1`: peaks p50 (+0.295) then goes NEGATIVE (−0.098 at p80). Not monotone.
- `sr_r6`: monotone on x15M30 but x15M H13 goes +0.082 -> **−0.295** at p10. Mixed.

The dose-response test is discriminating, not rubber-stamping: 1 of 4 candidates passed it.

CAVEAT: at p10, n ~26 of 265. The largest numbers sit on the thinnest samples.

## 37c. THE TWO SIDES TELL ONE STORY

`x` is an oscillator. The two independent screens selected the SAME LINE FAMILY, in the directions a
fade-the-extreme mechanic requires:

| side | feature | better direction | reading |
|---|---|---|---|
| SHORT | sr_x1 | **HIGH** x | more overbought -> better short |
| LONG | sr_x90 | **LOW** x | more oversold -> better long |

This was NOT designed in. The long screen ran over all 60 columns with no knowledge of the short
result, and landed on the x family with the opposite sign. That is the kind of coherence that is
hard to get from noise — but the timeframes differ (TF1 vs TF90), which the fade story does not
explain and which a shared-noise story would not predict either.

## NEXT — a FALSIFIABLE PREDICTION
If "fade the x extreme" is the real mechanic, then it should be SYMMETRIC:
- `sr_x1` LOW should help LONGS (the mirror of the short finding)
- `sr_x90` HIGH should help SHORTS (the mirror of the long finding)
If both mirrors hold, the mechanic is established on 4 independent measurements. If neither holds,
then x1 and x90 are two unrelated flukes that happen to sit in the same column family, and ckpt 37c
is a coincidence I talked myself into.

---

# CHECKPOINT 38 — THE SYMMETRY TEST FAILS. Ckpt 37c RETRACTED.

The prediction was registered in advance (ckpt 37 NEXT) specifically so it could fail.

| test | tightening improved the number in | verdict |
|---|---|---|
| (known) sr_x1 HIGH -> SHORTS | **16 of 20** exit-steps | **HOLDS** |
| **MIRROR 1: sr_x1 LOW -> LONGS** | **8 of 20** | **FAILS** |
| MIRROR 2: sr_x90 HIGH -> SHORTS | 14 of 20 | mixed |
| (known) sr_x90 LOW -> LONGS | 14 of 20 | mixed |

### MIRROR 1 detail — the clean failure

| keep x1 <= | s6 bare | x15M30 H2 | x22M H0 | x15M H13 | x30r H5 |
|---|---|---|---|---|---|
| p90 | −0.074 | +0.180 | +0.130 | +0.066 | +0.061 |
| p70 | −0.090 | +0.271 | +0.316 | +0.139 | +0.223 |
| p50 | −0.111 | +0.184 | +0.323 | +0.131 | +0.195 |
| p30 | −0.158 | +0.175 | +0.354 | +0.112 | +0.015 |
| **p10** | −0.136 | **−0.189** | +0.008 | **−0.039** | +0.141 |

Tightening the filter makes it WORSE. On shorts, the identical operation on the identical column
makes it monotonically BETTER (16/20).

## RETRACTION OF CKPT 37c

"The two sides tell one story — both independently found the x family in the directions a
fade-the-extreme mechanic requires" is **RETRACTED**. The fade story predicts four relationships:
1 strong, 2 mixed, 1 outright negative. That is not a mechanic; that is one real finding (sr_x1 on
shorts) plus a pattern I read into the column names.

I flagged the risk when writing it ("a coincidence I talked myself into") and then tested it rather
than leaving it as narrative. This is the fourth retraction tonight (ckpt 23a, 28b, 33d, 38).

## WHAT STANDS
- **sr_x1 HIGH on SHORTS** — unchanged. Dose-response 16/20 (ckpt 34), walk-forward t 2.26 (ckpt 36).
- **sr_x90 LOW on LONGS** — a CANDIDATE only. Its own dose-response is monotone-ish (14/20) but its
  mirror does not hold, its largest numbers sit on n~26, and it has had no walk-forward.
- there is **no validated long-side filter**. Ckpt 32's "the long side does not work" survives, now
  tested properly (independent screen, not the short-fitted threshold).

---
---

# CHECKPOINT 39 — STOPPING DELIBERATELY. Rationale.

Deleting `.claude/autonomous.on` rather than running further tests on this window. This is a
reasoned stop, not exhaustion, and the reasoning is the same as the findings:

1. **Ckpt 19 measured that this window cannot resolve small effects**: per-trade sd 2.390 against a
   0.110 cost line, n~250, underpowered ~17x for a +0.10%/trade edge.
2. **Ckpt 18 showed exactly how that manufactures false results**: a gross t of +4.46 that is
   really −8.27 once fees are priced.
3. **Ckpt 23 showed what selection looks like here**: rank 1 of 208 on the metric it was selected
   with, in a family whose median is negative.
4. Having established all three, continuing to run marginal tests on the same 12 weeks would
   contradict my own findings and would more likely produce a fourth false positive than a finding.
   The remaining thread (a long-side walk-forward on sr_x90) rests on a candidate that FAILED its
   mirror test with its largest numbers at n~26.

Joe's standing instruction is "don't EVER try to make me happy — data is how I make decisions, don't
poison it." More mining here poisons it.

**NOT applied, deliberately** (BUILD-GATE — these are value judgements, Joe's call):
- the `sr_post_*` naming convention / comment marking the lookahead boundary at build_s46.py:257
- changing the production thresholds `sr_ib_bars>24` / `sr_s1hold>24` in
  `sweep_s46_exit.load()` (line 90) and `build_s46_window.py:81`
- adopting sr_x1 as a live filter

## THE DELIVERABLE
- `docs/260804_handover.md` — 157 lines, the readable version
- `docs/260804_exit_permutation_notes.md` — this file, 39 checkpoints, the full working record

## THE ONE-LINE ANSWER TO JOE'S QUESTION ("is this still worth working on?")
**Yes — but it was never an exit problem.** Every exit mechanic is dead with a stated reason. The
lever is entry selection: `sr_x1` HIGH on shorts, which in a strict walk-forward (threshold refit
weekly on past data only) gives **+0.609/trade net of fees, t 2.26, 7/8 weeks positive, and
+0.367/trade even with its two best weeks removed** — against an unfiltered baseline of +0.101 and
t 0.47.

---
---

# CHECKPOINT 40 — LOOKAHEAD IN THE EXIT. EVERY RESULT FROM CKPT 25 ONWARD IS VOID.

Joe 0804: "4 - this isn't causal". He is right.

## 40a. THE DEFECT — sweep_s46_exit.py:266

```python
if s6 is not None and not (s6_mode == 'fallback' and cand):
```
`cand` holds the leg's next fire bar ANYWHERE in the future (unbounded `searchsorted`). Under
`s6_mode='fallback'` the s6 exit is suppressed whenever the leg fires AT ALL. Standing at the s6
exit bar you cannot know whether the leg will fire 5,000 bars later. **NOT CAUSAL.**

`s6_mode='race'` — `b = min(cand)`, exit at whichever fires first — IS causal.

**I used 'fallback' for every number reported from ckpt 25 onward.**

## 40b. THE DAMAGE — walk-forward, x1 p70 refit weekly, item 15 applied, net 0.110% taker

| exit | s6_mode | n | net mean | net sum | t | weeks>0 |
|---|---|---|---|---|---|---|
| x15M30 H2 filtered | fallback | 83 | +0.6085 | +50.5 | 2.26 | 7/8 |
| **x15M30 H2 filtered** | **RACE** | 110 | **−0.0187** | −2.1 | **−0.23** | **2/8** |
| x22M H0 filtered | fallback | 85 | +0.5088 | +43.2 | 2.16 | 6/8 |
| **x22M H0 filtered** | **RACE** | 110 | **−0.0165** | −1.8 | **−0.21** | **2/8** |
| x15M H13 filtered | fallback | 89 | +0.3804 | +33.9 | 2.00 | 7/8 |
| **x15M H13 filtered** | **RACE** | 110 | **−0.0269** | −3.0 | **−0.33** | **2/8** |
| x15M30 H2 UNFILTERED | fallback | 143 | +0.1006 | +14.4 | 0.47 | 4/8 |
| x15M30 H2 UNFILTERED | RACE | 325 | **−0.0976** | −31.7 | −2.37 | 1/8 |
| x22M H0 UNFILTERED | RACE | 322 | −0.0912 | −29.4 | −2.24 | 1/8 |
| x15M H13 UNFILTERED | RACE | 325 | −0.0920 | −29.9 | −2.19 | 1/8 |

n rises 83 -> 110 under race because race exits earlier, so item 15 blocks fewer entries.

## 40c. WHAT SURVIVES

**Nothing is profitable.** One relative effect remains:

| x15M30 H2, RACE | n | net mean | t |
|---|---|---|---|
| unfiltered | 325 | −0.0976 | −2.37 |
| **+ x1 p70 filter** | 110 | **−0.0187** | −0.23 |

sr_x1 still moves the stream from significantly-negative to indistinguishable-from-zero
(+0.079/trade relative). That is the ONLY thing left of ckpt 30-36.

## 40d. VOIDED
- ckpt 32 stack (t 3.14), ckpt 34 dose-response magnitudes, ckpt 36 walk-forward (t 2.26)
- docs/260804_handover.md headline tables
- ckpt 25/26 gate results, ckpt 28/29 threshold results — all ran under 'fallback'

## 40e. CAUSALITY AUDIT OF ALL SEVEN KNOBS (source-verified)

| # | knob | causal? | evidence |
|---|---|---|---|
| 1 | ib / s1hold thresholds | **YES** | `ibrun[a-1]`, `S1H[sgn][a-1]` — read strictly before the entry bar |
| 2 | sr_x1 p70 refit weekly | **YES** | `E[1]['x'][a]` at the entry bar; threshold from prior weeks only |
| 3 | item 15 no-pyramiding | **YES** | previous accepted trade's exit bar, known before the next entry |
| 4 | s6_mode | **NO for 'fallback'** / YES for 'race' | sweep_s46_exit.py:266 |
| 5 | leg (x/M cross) | **YES** | `latch` uses `np.maximum.accumulate` (backward); `confirm` is a run-length; `edges` compares to the PREVIOUS bar |
| 6 | gate states | **YES** | `momo(r,dr,w)` samples `w - k*MOMO_STEP_BARS`, every index <= w |
| 7 | gate tfs | **YES** | same call |

Six of seven are clean. The seventh invalidated everything.

## 40f. JOE'S DECISIONS RECORDED (0804)
- **item 15 (no-pyramiding) — DISABLED as a question: it stays ON.** "pyramiding needs to be
  disabled". This is what every table already used. Item 16 of the 0803 spec is superseded.
- **knob 4 — 'race' only.** 'fallback' is retired as non-causal.
- **knob 6 — curl stays in.** "leave it on for now - I think there are other unbuilt mechanics that
  need to confluence curl." Gate states become (1,2). Measured worse alone (+0.0262 vs +0.0469
  momo-only) and that measurement is itself void under 40b — to be re-run under 'race'.
