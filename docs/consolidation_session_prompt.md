# Consolidation detector — session brief

**Prepared 2026-09-03 for a second session. Written by the session that ran the research, so that
you can start working in your first reply rather than spending an hour orienting.**

Joe's words setting this up: *"we need to build a consolidation detector, that wil be applied to a
scalping strategy. the scalping strategy uses BB%B and StochRSI lines, ranging from 15sec to 4
minutes"* / *"don't chase threads that rely on a TF larger than 10 minutes - they don't qualify as
scalpers"* / *"the goal is to identify when consolidation is happening, so that we can make informed
trading decisions"* / *"we have no existing consolidation detection"* / *"this is a green-fields
build"*.

**THIS WORK IS UNREGISTERED.** An earlier draft of this brief said it was task #13 on
`docs/task_register.md`. It is not. Line 59 of that file reads *"#13 HTF overlap: does it raise
s30r's swing-follow rate"*, and `grep -i consolidat docs/task_register.md` returns exactly one hit
— line 85, *"#20 Consolidate pk machine spec into one doc"*, which is unrelated. The "#13" came
from the session-local Claude Code task list, which is a different list with its own numbering.
Whether this gets a register entry, and under what number, is Joe's call.

---

## 1. Who you are working with, and the rules that outrank everything

Joe is the architect and designer. You are the master coder. The roles are demarcated and he has
said so explicitly. Read `~/.claude/projects/-home-joe-thecodes/` memory and the `Joe's convo style`
hook that fires on every prompt — both are loaded automatically. The parts that will bite you first:

- **BUILD-GATE.** Before any code, config or DB edit, enumerate every unspecified concretion.
  Decide *structural* ones (SRP, precedent, measurable) and state the choice. **Escalate *value*
  ones to Joe and stop.** A threshold is a value judgement. A table name is structural.
- **Stop mid-task when you hit an unplanned decision.** Joe 0903: *"if you come to a unplanned
  decision while you code, stop and tell me what you see."* Announcing a decision as you make it is
  not asking.
- **Never infer.** If the spec does not say it, ask. Do not resolve an ambiguity by producing both.
- **No deletes.** Never drop or overwrite a table Joe owns. Build alongside under a new name.
  Joe 0827: *"if we add a new ingredient to support a decision that overrides an existing verdict,
  there is always a possibility that the new ingredient is malformed."*
- **No caps, horizons, windows or truncations** — in code OR in diagnostics — unless Joe specified
  them.
- **Every knob that changes rows goes in the unique key**, or an A/B overwrites itself.
- **Joe cannot see tool output.** Paste actual content into your message. A report that only exists
  in a tool result did not happen.
- **Effective-n.** No percentage without its episode count. Bar counts are not sample sizes.
- **A rule chosen by scoring against Joe's labels is FITTED, not measured.** Say so every time it
  is quoted.
- **Causal only.** No lookahead anywhere — not in code, and every *option* you offer must itself be
  causal. `docs/causal_lookahead_register.md` is the live register.

---

## 2. The one thing you are building

A **consolidation detector** for the 15-second-to-4-minute band, causal, running on the existing
line cache.

The research (below) ruled out three of the obvious ways to build one and left exactly one primitive
standing: the **Kaufman Efficiency Ratio**.

    KER_t(X, n) = |X_t - X_{t-n}| / sum_{i=t-n+1}^{t} |X_i - X_{i-1}|

- **Numerator** — how far the series ended up from where it was `n` bars ago. Straight-line distance.
- **Denominator** — how far it actually travelled: every bar-to-bar move, absolute, added up.
- **Bounded [0, 1]** by the triangle inequality. Not a setting — arithmetic.
- **1.0** = walked straight there, no wasted motion. **0.0** = moved a long way, finished where it
  started. Low KER is the consolidation signature.
- **Causal by construction.** Every index runs backward from `t`; the maximum index anywhere in the
  formula is `t`. Computable on closed bars with no lookahead.
- **Timeframe-agnostic.** The same formula computes identically at 15 s and at 4 min.

---

## 3. The cutoff — Joe has set a starting point

Joe 0903: *"cutoff is a knob, so we can pick a starting point of .28 and adjust as needed"*.

- **Start at KER < 0.28 = consolidation.** That is a knob, not a finding.
- Nothing in the verified research supplies a cutoff. The vendor spec for KER was grep-checked and
  contains **zero** hits for "threshold", "default", "trend", "consolidat", "chop", "rang".
- You **cannot** derive a cutoff from distributional theory — see finding 2 below. It has to come
  from our own bars.
- **The knob goes in the unique key of whatever you bank**, so a run at 0.24 lands alongside a run
  at 0.28 instead of on top of it.
- Do not change 0.28 on your own judgement. Propose, never apply. Joe's target protocol: hit a
  target with his mechanisms only; propose the knob change, never apply it, never dump the sweep.

---

## 4. The data — where it is and how to read it

**Base grid: 5 seconds.** Every bar in every table is a 5-second bar. This matters more than
anything else in this document — see the traps in section 8.

### The line cache table

`ws_line_bar` — 276,481 rows, `2026-08-03 00:00:00` to `2026-08-19 00:00:00`, one row per 5-second
bar, one column per line.

| column | holds |
|---|---|
| `wlb_ms`, `wlb_utc` | the bar's timestamp |
| `wlb_<group><role>` | the line value, e.g. `wlb_ws1r`, `wlb_g15x`, `wlb_ws4Mage` |
| `wlb_<group>_newbar` | 1 on bars that START a new bar of that group's own timeframe |

Group name prefixes: `g15` = gcws15, `g30` = gcws30, `ws1`..`ws27`, `ws30`, `ws45`, `ws60`.

### Reading it — the simple path

```sql
SELECT wlb_utc, wlb_g15r, wlb_g30r, wlb_ws1r, wlb_ws2r, wlb_ws3r, wlb_ws4r
FROM ws_line_bar
WHERE wlb_utc >= '2026-08-04 00:00:00' AND wlb_utc < '2026-08-05 00:00:00'
ORDER BY wlb_ms;
```

### Reading it — the fast path

The lines are also cached as numpy arrays over the whole tape. This is what every producer uses:

```python
import os, numpy as np
from optimus9.compute.line_config import KLine, override
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key
import build_momo_landed as B

# the r line (StochRSI) at timeframe tf, in minutes
rr = np.load(os.path.join(LINE_DIR, _line_key(END_MS, HOURS, WARMUP,
             override(tf * 60, KLine(**B.R_SPEC), 'emerging')) + '.npy'))

# the tape's own timestamps - use searchsorted on THIS to find a bar index
ts = np.load(os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP,
             {'src': <pxsmooth_dema_src>, 'len': <pxsmooth_dema_len>}) + '.npz'))['__ts__']
i = int(np.searchsorted(ts, ms_of_the_bar_you_want))
```

- `<pxsmooth_dema_src>` / `<pxsmooth_dema_len>` come from
  `SELECT pxsmooth_dema_src, pxsmooth_dema_len FROM optimus9_system WHERE sys_pk=1`.
- **The npy array spans the WHOLE tape, not your window.** Index it with `searchsorted` on `ts`.
  Taking `array[-len(rows):]` put a read 77,759 bars adrift once — about 4.5 days. Do not do it.

---

## 5. The line vocabulary — what Joe means by "BB%B and StochRSI"

Read from `mech_line_config`, the table `build_ws_line_bar.py` uses to fill `ws_line_bar`.
**The timeframe on the row is deliberately discarded** — `build_ws_line_bar.py:82-83`: *"the five
shared specs, read from mech_line_config's wsf rows. One row per role; the timeframe on the row is
discarded because every timeframe uses the same spec."* It then applies that one spec at every
group, gcws15 and gcws30 included.

**SO DO NOT READ THE TABLE'S OWN TIMEFRAME COLUMNS AS COVERAGE.** `mech_line_config` holds 7 rows:
`wsf` × 5 roles at `mlc_tf_lo` 60 s to `mlc_tf_hi` 480 s, and `domtf` × 2 roles (r and x only) at
780 s to 1620 s. No row names 15 s or 30 s. That is not a gap — those bands are covered by the
same wsf spec applied at their timeframe.

**A DIFFERENT PRODUCER USES A DIFFERENT SOURCE.** `optimus9/orchestration/build_ws_lines.py` builds
its cache through `overrides()` → `LineStore.resolve` → `vw_indicator_configs_live`, not through
`mech_line_config`. If you are reading `ws_line_bar`, mech_line_config is your source. If you are
reading that other cache, it is not.

Five roles per timeframe:

| role | type | parameters | what it is |
|---|---|---|---|
| `r` | StochRSI | k_len 7, rsi_len 5, stc_len 8 | **the StochRSI line.** Bounded 0 to 100 |
| `x` | BB %B | length 5, mult 0.35 | %B on a very fast, very tight band. **the fast partner** |
| `m` | BB %B | length 6, mult 0.40 | %B, fast |
| `Mage` | BB %B | length 38, mult 0.93 | %B, slow |
| `b` | BB %B | length 49, mult 0.95 | %B, slowest |

- Every timeframe uses the **same five specs**. Only the timeframe changes.
- `value_mode` is `emerging` on all of them.
- **%B is not bounded 0 to 100.** Measured over the whole cache: `ws1x` runs **−64.29 to +164.29**.
  It leaves the bands routinely.
- **StochRSI is bounded 0 to 100** and touches both ends exactly.

---

## 6. The scalping band, in repo names

Joe's 15 sec to 4 min maps to exactly six groups. All five roles exist at every one of them, and
**all 30 lines are non-NULL on all 276,481 rows** — verified.

| Joe's timeframe | repo group | column prefix |
|---|---|---|
| 15 seconds | gcws15 | `wlb_g15…` |
| 30 seconds | gcws30 | `wlb_g30…` |
| 1 minute | ws1 | `wlb_ws1…` |
| 2 minutes | ws2 | `wlb_ws2…` |
| 3 minutes | ws3 | `wlb_ws3…` |
| 4 minutes | ws4 | `wlb_ws4…` |

- **Do not use ws10 and above.** Joe: *"don't chase threads that rely on a TF larger than 10 minutes
  - they don't qualify as scalpers."* Note the collision hazard: `wlb_ws1r` is 1 minute,
  `wlb_ws10r` is 10 minutes, `wlb_ws12r` is 12. Prefix-matching on `ws1` catches all of them.

---

## 7. What the research settled — 9 confirmed, 9 killed

Run 2026-09-03: 5 search angles, 21 sources fetched, 104 claims extracted, 25 verified, 16
confirmed, 9 killed, 103 agents.

### Survived — build on these

| # | finding |
|---|---|
| 1 | **Bar counts are not sample sizes.** 360 non-overlapping 5-minute observations carry "a very small effective sample size"; a Newey-West correction with 90 lags leaves the statistic "far from being standard normally distributed". Absolute returns instead of squared reduce outlier sensitivity but do not repair the inference |
| 2 | **A variance-ratio consolidation call is badly size-distorted.** Under GARCH(1,1) 5-minute returns a TRUE constant-variance null "will reject in the majority of cases". A ratio of 2.43 is p = 6.5e-17 under F(359,359) and p = 0.082 under the correct simulated null. **Any cutoff must come from a simulated or empirical null, never from F or chi-square theory** |
| 3 | The paper's repair is a causal two-step normalisation using the **previous** day's volatilities. Its cautions transfer; its machinery (a 20/60-day structural-break test) does not |
| 4 | **H = 0.5 is the wrong trend/consolidation divider.** The finite-sample expectation of the rescaled-range Hurst exponent is always *above* 0.5 and falls with series length |
| 5 | **Hurst cannot gate a per-window call at scalping lengths.** Estimator sd 0.084 in H, ±0.17 at two sigma — one window cannot separate H = 0.5 from H = 0.6. Evidence base is 100% synthetic and starts at 512 observations |
| 6 | **KER is the one implementable causal primitive.** Formula in section 2. The vendor spec documents no range, no default length, no threshold |
| 7 | **Emit only on confirmed bar close.** On an unclosed bar the close is still mutable, so a detector can signal differently live than it does once historical. Costs one bar of latency |
| 8 | **Multi-timeframe plumbing has two opposite correct answers.** Higher-TF pulls need **both** the `[1]` offset and `lookahead_on`. Lower-TF pulls invert it — the flag silently selects *which intrabar* you get |
| 9 | **Pivot-boundary detectors are structurally late.** A pivot is not knowable on the bar it occurs. Already measured here — see `pivot_causal_lag.py` |

### Killed — do not re-import these

| vote | killed claim |
|---|---|
| 0-3 | 15s/30s clock bars manufacture artificial autocorrelation |
| 0-3 | One minute is the clean/contaminated boundary for microstructure noise |
| 0-3 | The volatility signature plot *drops* at ultra-high frequency, so 15s variance falsely reads as consolidation |
| 1-2 | Close-only bars structurally under-read intra-bar oscillation |
| 0-3 | A bar-timeout rate is itself a low-activity detector |
| 0-3 | High-frequency serial dependence is a sampling-frequency artefact |
| 0-3 | High-frequency realized variance measures the noise process, not true variance |
| 0-3 | There is an MSE-optimal bar size inside the 15s–4min band |
| 0-3 | **Bollinger BandWidth `((Upper − Lower) / Middle) × 100` is a scale-free consolidation number comparable across instruments and across the TF ladder** |

- The **entire microstructure-noise case against 15-second bars collapsed 0-3 four times over.**
  That removes the argument against 15s bars without supplying an argument for them. It is an open
  hole, not a cleared one, and it is decidable in-house against the 5-second base bar.
- **BandWidth's comparability did not survive.** If you reach for it because it comes free with the
  %B lines already running, know that its cross-timeframe comparability was refuted 0-3.

### Caveats the research raised about itself

- **Single-source concentration.** Findings 1-3 are one paper; 4-5 are one paper **with no
  empirical section — every result synthetic**; 7-9 are all TradingView's own docs.
- **Neither econometric paper touches BB%B or StochRSI.**
- **Nothing verified gives a number.** No threshold, no window, no output range for any metric.
- **Tooling hazard, caught in-session.** A WebFetch summary of the KER vendor page *fabricated* an
  "Output Range … choppy or ranging conditions" section that is not in the raw HTML. Treat fetch
  summaries of spec pages as unreliable; curl the raw page to check a negative.
- Findings 5 (partly), 8 (lower-TF half) and 9 were verified without a counter-search — the
  200-search budget ran out.

---

## 8. My notes — the traps I would want to know about before writing a line of code

These are measured this session, not recalled.

### 8.1 The lines repeat between their own timeframe's bar updates

The tape is a 5-second grid. On a large share of bars a line's value is **literally identical** to
the previous bar, so `|X_i - X_{i-1}|` is exactly zero.

**THE REASON IS NOT WHAT AN EARLIER DRAFT OF THIS BRIEF SAID.** It claimed a ws4 line only changes
when a new 4-minute bar forms. That is false and was measured false:

| ws4r over all 276,480 bar-to-bar transitions | count |
|---|---|
| transitions where ws4r changed | 98,521 |
| of those, landing on a `wlb_ws4_newbar = 1` row | **4,444** |
| of those, landing anywhere else | **94,077** |
| `wlb_ws4_newbar = 1` rows in total | 5,760 |

- `value_mode` is `emerging` on all 30 band lines, so a line moves **as its own bar builds**. It is
  not a step function held flat between own-bar closes.
- It does not even always move at its own bar start: only 4,444 of the 5,760 ws4 bar starts carry a
  change.
- **Why the other repeats happen is not measured.** Do not substitute another guess for the one
  this brief got wrong. If the mechanism matters to your design, measure it.

| line | bars identical to the previous bar | share of 276,481 |
|---|---|---|
| gcws15x | 118,132 | 42.7% |
| gcws15r | 144,217 | 52.2% |
| ws1x | 126,099 | 45.6% |
| ws1r | 167,437 | 60.6% |
| ws4x | 128,094 | 46.3% |
| ws4r | 177,959 | 64.4% |

- Longest run of identical `ws1r` values measured: **161 bars = 805 seconds**.
- **Consequence for KER:** the denominator is a sum over mostly-zero terms. A 48-bar lookback on the
  5-second grid is 4 minutes of clock but only a handful of actual line updates on a ws4 line.
- **This is the single easiest thing to get wrong.** `n` in the KER formula is in BARS. Decide
  deliberately whether you want `n` in 5-second bars, or in that line's own timeframe bars (using
  the `wlb_<group>_newbar` flag to step). They are not the same measurement and they will not give
  the same number.

### 8.2 StochRSI saturates; %B does not

| line | exactly 0.00 | exactly 100.00 | pinned share |
|---|---|---|---|
| gcws15r | 1,042 | 757 | 0.7% |
| ws1r | 1,130 | 597 | 0.6% |
| ws4r | 859 | 432 | 0.5% |

- When an `r` line is pinned at a boundary for a whole window, **both the numerator and the
  denominator go to zero** and KER is 0/0. Decide what that returns before it bites you. It is rare
  — under 1% of bars — but it is a real division-by-zero.
- `%B` lines run −64 to +164 and do not have this problem.

### 8.3 KER already exists in this repo, twice, for a different question

- `ker_router_clean.py:29` — `def ker(a)`, run at **n=144** on the s5m line. Its docstring: *"does
  s5m-KER split the s5m-arm's REAL trades by quality?"* It was fitted for a **size-router**
  question, not a consolidation read. Do not assume 144 is right here.
- `live_strength_dig.py` — a second implementation, on several lines.
- **Both feed KER a LINE, not price.** A line is already smoothed, which changes the denominator's
  path length and therefore the ratio's whole scale. No verified source says which input a
  consolidation detector should use. **This is an open question for Joe.**

### 8.4 The knob-bank precedent, built today

`momo_config` is the pattern for how a knob bank is done in this repo, and it is one day old:

- table `momo_config`, built by `build_momo_config.py`, read by `optimus9/compute/momo_config.py`.
- **Keyed on the line's own timeframe, not on a machine name** — bands `wsf` 1..12 and `domtf`
  13..60 do not overlap, so a caller passes the timeframe it already holds and never asserts a
  machine it could get wrong.
- Unbound raises. There is no default. A default is what let one machine silently run on another's
  numbers.
- **A sweep must pass a version.** Reading the live bank during a sweep means a live config change
  mid-run silently alters the run and nothing on the rows says so.
- If the consolidation detector needs knobs banked, follow this shape rather than inventing another.

### 8.5 The full knob inventory is in one place

`docs/ws-finisher_spec.md` → **KNOBS**. 38 knobs — the momentum bank, the dtf knobs and the wsf
knobs — each with its value, its owner file and the words that set it. Written 2026-09-03.

### 8.6 Two things that are NOT research, and should not be done in a research session

Findings 7 and 8 are a **grep across the 92 `.pine` files**, not an experiment. Finding 8 is the only
item in the whole research set that touches something already live: a higher-timeframe pull without
`[1]` + `lookahead_on` is a lookahead leak in running code, not a missing feature. Raise it with Joe
as its own piece of work rather than folding it into the detector build.

---

## 9. The three open questions Joe has not answered

He was asked and said: *"for the questions: I don't know - this is a green-fields build"*. So these
are open, and they are **his** to close, not yours.

1. **Line or price?** Both existing KER uses feed a line. A line is already smoothed. The choice
   changes the denominator's path length and the whole scale of the ratio.
2. **What window `n`, per timeframe?** And in which unit — 5-second bars, or the line's own
   timeframe bars?
3. **Do BB%B and StochRSI themselves carry a consolidation reading?** Not one surviving claim
   addresses either indicator as a consolidation measure. If %B hugging 0.5 or StochRSI cycling
   inside a band is the intended signal, it is entirely unevidenced.

---

## 10. What "done" looks like

Not a detector Joe has to accept or reject whole. A **shape he can rule on**:

- KER computed across the six band timeframes over the banked window, causally, on closed bars.
- The **distribution** of what it reads — so 0.28 can be placed against what the number actually
  does on our bars, rather than against theory that finding 2 forbids.
- Per-row detail banked to a DB table, with every knob in the unique key. The tables ARE the A/B
  mechanism in this repo.
- Numbers reported flat: no evaluative adjectives, no "improves", no framing a fix as a win. Joe:
  *"you're not here to make data look good. the data you see as not good, is exactly the data I need
  to make decisions: you will not hide it from me."*
- Every percentage carries its episode count.
- The cutoff labelled **fitted, not measured**, wherever it is quoted.

---

## 11. Reference index

| what | where |
|---|---|
| the full research result, with every evidence quote and source | `docs/consolidation_research_260903.json` — keys `findings`, `refuted`, `caveats`, `openQuestions`, `sources`, `stats`. Section 7 above is the summary; this file is the evidence |
| every knob in the system | `docs/ws-finisher_spec.md` → KNOBS |
| the task this sits under | `docs/task_register.md` → #13 |
| what has been sunset and why | `docs/sunset_register.md` |
| the causal / lookahead register | `docs/causal_lookahead_register.md` |
| the knob-bank pattern | `build_momo_config.py`, `optimus9/compute/momo_config.py` |
| existing KER code | `ker_router_clean.py:29`, `live_strength_dig.py` |
| the pivot confirmation lag, measured | `pivot_causal_lag.py` |
| the line specs | `mech_line_config` table, read via `optimus9/compute/line_config.py` `mech_lines(db, mech, version)` |
