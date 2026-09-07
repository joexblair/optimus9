# consolidation spec

*Started 2026-09-03. Joe is the architect; the values in KNOBS are his unless a row says otherwise.
The research this rests on is `docs/consolidation_research_260903.json`; the orientation brief is
`docs/consolidation_session_prompt.md`.*

**THIS WORK IS UNREGISTERED.** It has no entry on `docs/task_register.md`. Whether it gets one, and
under what number, is Joe's call.

---

## the preamble, Joe 0903 verbatim

*"we need to build a consolidation detector, that wil be applied to a scalping strategy. the
scalping strategy uses BB%B and StochRSI lines, ranging from 15sec to 4 minutes"*

*"don't chase threads that rely on a TF larger than 10 minutes - they don't qualify as scalpers"*

*"the goal is to identify when consolidation is happening, so that we can make informed trading
decisions"*

*"we have no existing consolidation detection"* / *"this is a green-fields build"*

---

## the metric

The **Kaufman Efficiency Ratio**. It is the one primitive the 2026-09-03 research left standing;
variance-ratio, Hurst and Bollinger BandWidth were all killed (`docs/consolidation_research_260903.json`,
key `refuted`).

    KER_t(X, n) = |X_t - X_{t-n}| / sum_{i=t-n+1}^{t} |X_i - X_{i-1}|

| part | what it holds |
|---|---|
| numerator | how far the series ended up from where it was `n` bars ago. Straight-line distance |
| denominator | how far it actually travelled — every bar-to-bar move, absolute value, added up |
| range | 0 to 1, by the triangle inequality. Arithmetic, not a setting |
| 1.0 | walked straight there, no wasted motion |
| 0.0 | moved a long way, finished where it started. This is the consolidation end |
| causality | every index runs backward from `t`. The largest index anywhere in the formula is `t` |

---

## the band

Joe's 15 seconds to 4 minutes is six groups. All five roles exist at every one, all non-NULL on all
276,481 rows of `ws_line_bar`.

| Joe's timeframe | repo group | column prefix | own bars in the cache |
|---|---|---|---|
| 15 seconds | gcws15 | `wlb_g15…` | 92,161 |
| 30 seconds | gcws30 | `wlb_g30…` | 46,081 |
| 1 minute | ws1 | `wlb_ws1…` | 23,041 |
| 2 minutes | ws2 | `wlb_ws2…` | 11,521 |
| 3 minutes | ws3 | `wlb_ws3…` | 7,681 |
| 4 minutes | ws4 | `wlb_ws4…` | 5,761 |

- `ws10` and above are out of scope. Joe 0903: *"don't chase threads that rely on a TF larger than
  10 minutes - they don't qualify as scalpers"*.
- Prefix collision: `wlb_ws1r` is 1 minute, `wlb_ws10r` is 10, `wlb_ws12r` is 12. A `LIKE 'ws1%'`
  match catches all three.

---

## the input series

Joe 0903, asked whether the input should be a line or price: *"can we use both? if so, that is the
answer"*. Both. 30 line series and one price series.

### the 30 lines

Five roles per group. Every group uses the same five specs; only the timeframe changes. Read from
`mech_line_config`'s `wsf` rows by `build_ws_line_bar.py:81-82` — *"the five shared specs, read from
mech_line_config's wsf rows. One row per role; the timeframe on the row is discarded because every
timeframe uses the same spec."*

| role | type | parameters | what it is |
|---|---|---|---|
| `r` | StochRSI | k_len 7, rsi_len 5, stc_len 8 | the StochRSI line. Bounded 0 to 100 |
| `x` | BB %B | length 5, mult 0.35 | %B on a fast, tight band |
| `m` | BB %B | length 6, mult 0.40 | %B, fast |
| `Mage` | BB %B | length 38, mult 0.93 | %B, slow |
| `b` | BB %B | length 49, mult 0.95 | %B, slowest |

- `value_mode` is `emerging` on all 30. The line moves as its own bar builds; it is not held flat
  between own-bar closes.
- `src` is `close` on all 30.
- **%B is not bounded 0 to 100.** Measured over the cache, `ws1x` runs −64.29 to +164.29.
- **StochRSI is bounded 0 to 100** and touches both ends exactly.
- Joe 0903, asked which lines to start on: *"start with all 30 lines. we'll have a better idea of
  which to retain after a few walks have completed"*.

### the price series — `pxs`

Joe 0904: *"price is re-presented as `pxs`. FYI this is sourced from the jig"*.

- The sanctioned reader is `JigCache.pxs` — `optimus9/orchestration/rpl_cache.py:87`, comment
  *"event-tape px_smooth (DEMA close, filler-invisible)"*. Do not load the npz by hand.
- Built by `_px_smooth_evt`, `rpl_cache.py:59-69`: *"DEMA of the price src over EVENT bars only,
  forward-filled onto the full 5s grid (same filler-invisible discipline as the jig's lines)."*
- `pxsmooth_dema_src` = `close`, `pxsmooth_dema_len` = 2, read from `optimus9_system`.
- **`pxs` repeats on every filler bar** — a bar with no real trade carries the previous event bar's
  value by forward fill, so `|X_i − X_{i−1}|` is exactly zero there. Measured on 08-04: 11,149 of
  17,280 bars are event bars (64.5%), and `pxs` repeats on 6,131 of 17,279 transitions (35.5%).
  Inside Joe's 09:15-12:35 window the repeat share is 46.0%. This is by design and is measured, not
  reasoned — unlike the line repeats.
- `kline_collection.kc_close` (the raw 5-second close, 276,480 rows in the window) was the other
  causal option. Not chosen.

`pxs` carries no group dimension: `ker_n_unit` is `5sec`, so it is one series over the 5-second
grid, not six. 30 line series + `pxs` = 31.

---

## what is banked

`ker_line_bar`, built by `build_ker_line_bar.py`. Nothing existing is touched.

| column | holds |
|---|---|
| bar timestamp | the 5-second bar the reading sits on |
| series | the line name (`gcws15r` … `ws4b`) or the price series |
| `ker` | the ratio, 0 to 1. NULL when the window is flat |
| numerator | \|X_t − X_{t−n}\|, banked raw |
| denominator | Σ\|X_i − X_{i−1}\|, banked raw |

- **The value is banked, not the boolean.** The cutoff is applied at read time, so moving 0.28 to
  0.24 costs a query and not a rebuild.
- **A flat window banks NULL plus the raw numerator and denominator.** Nothing is destroyed. What a
  flat window should *read* is UNSET below.
- Rows with fewer than `n` prior bars bank NULL. A partial-window ratio is a different measurement.
- The run covers the whole cache — 276,481 rows, 2026-08-03 00:00:00 to 2026-08-19 00:00:00. No
  truncation.

---

## capture and analysis

Joe 0903: *"my instinct says capture per 5sec, and analyse at the close of the bar - if you're
looking at a TF2 bar, then you have 24 samples that may or may not look like consolidation when
grouped, sliced, and diced"*.

- **Capture: every 5-second bar.** One row per 5-second bar per series.
- **Analysis: at the close of the group's own bar.** A ws2 (2 minute = 120 second) bar spans 24
  five-second bars, so 24 KER samples group under it. A gcws15 bar spans 3. A ws4 bar spans 48.
- Joe prefaced this with *"I don't know"*. It is his instinct, not a settled rule.
- **How the 24 samples are grouped, sliced and diced is not specified.** Not built.

---

## KNOBS

| knob | value | what it does |
|---|---|---|
| `ker_n` | **UNSET** | the lookback length, in whatever `ker_n_unit` says. Joe has set the unit, not the count. Bounded to 2..1,919 by the labelled episodes' own lengths — see below. `ker_router_clean.py:29` runs n=144 on the s5m line — that was fitted for a size-router question, not this one, and does not carry over |
| `ker_n_unit` | **`5sec`** | which bars `ker_n` counts. `5sec` = the base grid every table sits on. `own_tf_bar` = the group's own bars, stepped by `wlb_<group>_newbar`. Joe 0903: *"5sec makes the most sense. create a new spec doc and add a knob (5sec or own TF bar) in the knobs section"*. The two are not the same measurement — at ws4, `ker_n` = 48 is 4 minutes of clock under `5sec` and 3.2 hours under `own_tf_bar` |
| `ker_input` | **all 30 lines + `pxs`** | which series get a KER. Joe 0903: *"start with all 30 lines"*. Joe 0904 set the price series: *"price is re-presented as `pxs`"*, sourced from the jig |
| `ker_cutoff` | **0.28** | below this the reading is called consolidation. Joe 0903: *"cutoff is a knob, so we can pick a starting point of .28 and adjust as needed"*. **FITTED, NOT MEASURED** — nothing in the verified research supplies a threshold, and the vendor spec for KER contains zero hits for "threshold", "default", "trend", "consolidat", "chop" or "rang". Applied at read time, so it is not in the row key |
| `ker_flat_window` | **UNSET** | what a window with zero total movement reads. 0.0, NULL, or something else. Joe 0903: *"I don't know yet. wait for actionable data then we can hone in"*. Deferred to read time — the builder banks NULL plus the raw parts, so his answer costs no rebuild |
| `ker_cutoff_scope` | **UNSET** | one `ker_cutoff` across all six groups, or one per group. Joe 0903: *"I don't know yet. wait for actionable data then we can hone in"*. Deferred to read time |

### the row key

`(bar_ms, series, ker_n, ker_n_unit, version)`. Unbound raises; there is no default. A sweep passes
a version and never reads the live bank. The shape is `momo_config`'s, per
`optimus9/compute/momo_config.py`.

`ker_cutoff`, `ker_flat_window` and `ker_cutoff_scope` are **not** in the key — none of them changes
a banked row, because the value is banked and the label is not.

### knobs this spec does not own

- the five line specs — `mech_line_config`, `wsf` rows, version 1.
- `pxsmooth_dema_src` / `pxsmooth_dema_len` — `optimus9_system`, currently `close` / 2.
- the 85 / 15 boundaries — `optimus9_system`. Nothing in this spec reads them yet.

---

## what is NOT specified

- `ker_n` — the count. Blocking.
- what a flat window reads.
- whether the cutoff is one number or six.
- how the per-5-second samples are grouped at own-bar close.
- whether BB%B or StochRSI carry a consolidation reading in their own right. Not one surviving claim
  in the research addresses either indicator as a consolidation measure.

---

## traps that are measured, not reasoned

### the lines repeat, and the reason is not measured

Over all 276,480 bar-to-bar transitions in `ws_line_bar`:

| line | own TF | repeats | repeat % | changes | changes on an own-bar-start row | changes between own-bar starts | longest identical run | mean identical run |
|---|---|---|---|---|---|---|---|---|
| gcws15r | 15 s | 144,217 | 52.2% | 132,263 | 58,393 | 73,870 | 161 bars = 805 s | 2.1 bars = 10.5 s |
| gcws15x | 15 s | 118,132 | 42.7% | 158,348 | 60,987 | 97,361 | 161 bars = 805 s | 1.7 bars = 8.5 s |
| gcws30r | 30 s | 158,045 | 57.2% | 118,435 | 30,282 | 88,153 | 161 bars = 805 s | 2.3 bars = 11.5 s |
| gcws30x | 30 s | 123,191 | 44.6% | 153,289 | 31,484 | 121,805 | 161 bars = 805 s | 1.8 bars = 9.0 s |
| ws1r | 60 s | 167,437 | 60.6% | 109,043 | 17,660 | 91,383 | 161 bars = 805 s | 2.5 bars = 12.5 s |
| ws1x | 60 s | 126,099 | 45.6% | 150,381 | 18,409 | 131,972 | 161 bars = 805 s | 1.8 bars = 9.0 s |
| ws2r | 120 s | 173,113 | 62.6% | 103,367 | 8,881 | 94,486 | 161 bars = 805 s | 2.7 bars = 13.5 s |
| ws2x | 120 s | 127,437 | 46.1% | 149,043 | 9,256 | 139,787 | 161 bars = 805 s | 1.9 bars = 9.5 s |
| ws3r | 180 s | 175,474 | 63.5% | 101,006 | 5,878 | 95,128 | 162 bars = 810 s | 2.7 bars = 13.5 s |
| ws3x | 180 s | 127,909 | 46.3% | 148,571 | 6,169 | 142,402 | 162 bars = 810 s | 1.9 bars = 9.5 s |
| ws4r | 240 s | 177,959 | 64.4% | 98,521 | 4,444 | 94,077 | 162 bars = 810 s | 2.8 bars = 14.0 s |
| ws4x | 240 s | 128,094 | 46.3% | 148,386 | 4,624 | 143,762 | 162 bars = 810 s | 1.9 bars = 9.5 s |

- **Consequence for KER.** The denominator sums 177,959 exactly-zero terms on `ws4r` over the full
  cache. `ker_n` in bars is not `ker_n` in clock time.
- **The reason for the repeats is NOT measured.** An earlier draft of the brief said a ws4 line only
  changes when a new 4-minute bar forms and is literally identical between updates. That is false —
  `ws4r` changes 98,521 times, and only 4,444 of those land on a `wlb_ws4_newbar` = 1 row. Do not
  substitute a second guess. If the mechanism matters to a design decision, measure it.

### StochRSI pins at the boundaries; %B does not

The `r` (StochRSI) line at every group, over all 276,481 rows:

| line | exactly 0.00 | exactly 100.00 | pinned share |
|---|---|---|---|
| gcws15r | 1,042 | 757 | 0.7% |
| gcws30r | 812 | 530 | 0.5% |
| ws1r | 1,130 | 597 | 0.6% |
| ws2r | 1,283 | 889 | 0.8% |
| ws3r | 851 | 558 | 0.5% |
| ws4r | 859 | 432 | 0.5% |

- When an `r` line is pinned for a whole window, numerator and denominator both go to zero and KER
  is 0/0. `ker_flat_window` is the knob that answers it.

The `x` (BB %B) line at every group, same 276,481 rows. It leaves the bands routinely and does not
pin:

| line | min | max |
|---|---|---|
| gcws15x | −64.29 | 164.29 |
| gcws30x | −64.29 | 164.29 |
| ws1x | −64.29 | 164.29 |
| ws2x | −64.25 | 164.11 |
| ws3x | −64.14 | 164.24 |
| ws4x | −64.24 | 164.02 |

### KER exists twice in this repo already, for a different question

- `ker_router_clean.py:29` — `def ker(a)`, run at n=144 on the s5m line, fitted for a size-router
  question.
- `live_strength_dig.py:26` — `def ker_spikes(arr)`.
- Both use `abs(d.sum()) / (abs(d).sum() + 1e-9)`. On a perfectly flat window that returns **0.0** —
  the maximum-consolidation reading — silently, out of a numerical guard. This spec does not inherit
  that. Neither file is touched.

---

## Joe's labelled consolidation windows

These are Joe's eyes on the tape. They are the only ground truth this spec has. **Effective-n = 3
episodes.** Bar counts are not sample sizes.

| id | window | duration | bars at the 5-second grid | Joe's words |
|---|---|---|---|---|
| E1 | 2026-08-04 09:15 → 12:35 | 200 min | 2,401 | 0904: *"there was consolidation betwee 08-04 09:15 (estimated) and 12:35 (estimated)"* |
| E2 | 2026-08-05 08:45 → 11:25 | 160 min | 1,921 | 0904: *"I can also see consolidation between 08-05 ~08:45 and ~11:25"* |
| E3 | 2026-08-05 18:30 → 23:00 | 270 min | 3,241 | 0904: *"and again between ~18:30 and 23:00"* |

- **Every edge is approximate.** Joe wrote "(estimated)" on E1 and "~" on both E2 and E3 edges.
- **The contrast span is 08-04 and 08-05.** Joe 0904: *"contrast against 08-04 and 08-05"*. Two
  days = 34,560 five-second bars.
- **Nothing is labelled NOT-consolidation.** Every bar in the contrast span that is not inside E1,
  E2 or E3 is *unlabelled*, not negative. Treating unlabelled as negative is an assumption and it
  must be stated wherever a separation figure is quoted.
- **2026-08-04 06:48:00-06:52:10 is NOT a consolidation window.** Joe 0904, asked directly: *"no it
  doesn't count"*. His `eyes_on_pine` rows pk 361-363 there — *"price went semi sideways for a few
  minutes after a solid sell-off"* — stand as a domTF handover read on ws14r and nothing else.
- **Any `ker_n` chosen by scoring against these three windows is FITTED, NOT MEASURED.** Say so
  every time it is quoted.

### the bounds this puts on `ker_n`, without any scoring

| bound | value | why |
|---|---|---|
| floor | `ker_n` ≥ 2 | at `ker_n` = 1 the numerator \|X_t − X_{t−1}\| and the denominator are the same quantity, so KER is 1.0 on every bar |
| ceiling | `ker_n` ≤ 1,919 | E2 is the shortest episode at 1,920 bars. A lookback longer than that reaches outside E2 on every bar inside it, so the numerator picks up what price did before 08:45 |

Both come from the episodes' own lengths. Neither is chosen.

---

## why all 31 series are computed

Joe 0904: *"all 31. I'm not saying that this is the final cut - I'm including all lines so that you
access to all of the data, from which you can choose the lines that are most useful to the mech"*.

- The line selection is delegated and is to be made from the data, not from preference.
- `ker_n` need not be one number across all 31. Nothing has established that it is.

---

## the NULLs in the line cache

The brief `docs/consolidation_session_prompt.md` §6 says *"all 30 lines are non-NULL on all 276,481
rows — verified"*. Measured 0904 over the whole cache, that is false.

| column | NULL rows |
|---|---|
| `wlb_g15x` | 106 |
| `wlb_g15m` | 9 |
| `wlb_g30x` | 23 |
| `wlb_g30m` | 1 |
| `wlb_ws1x` | 6 |
| `wlb_ws1m` | 1 |
| all 30 band columns together | **146** |

- Every NULL is in an `x` (BB %B length 5, mult 0.35) or `m` (BB %B length 6, mult 0.40) column at
  the three fastest groups. The 24 other band columns hold none.
- **A NULL must exclude the windows that contain it and nothing more.** `np.cumsum` propagates a NaN
  forward, so a naive running sum of `|X_i − X_{i−1}|` lets one NULL void every window after it.
  Carry a parallel cumulative count of NULL-touching steps and require it to be zero across the
  window. Substituting zero for the missing step invents a value and is not allowed.
- The reason for the NULLs is not measured.

---

## the first scan — what KER reads on Joe's three windows

Run 0904. Scored span 08-04 00:00:00 → 08-06 00:00:00 = 34,560 five-second bars; 7,563 inside E1,
E2 or E3, 26,997 outside and unlabelled. `ker_n` scanned at every integer from 2 to 1,919 on all 31
series. No cutoff applied in the scan. **Effective-n = 3 episodes.**

- **KER falls monotonically with `ker_n` on every one of the 31 series.** Median over all scored
  bars for `pxs`: 1.0000 at `ker_n` = 2, 0.2656 at 24, 0.1128 at 144, 0.0450 at 720, 0.0233 at
  1,919. The same shape holds for all 30 lines.
- **Below roughly `ker_n` = 100, KER reads HIGHER inside Joe's three windows than outside** — the
  opposite of the consolidation direction. `pxs`: median 0.3015 inside against 0.2555 outside at
  `ker_n` = 24; 0.2018 against 0.1828 at 48; 0.1389 against 0.1354 at 96.
- **The direction flips and stays flipped only on 12 of the 31 series.** It never stably flips on
  any gcws15 line, on four of five gcws30 lines, or on any `x` or `m` line at any group.
- **At every `ker_n` where the direction is correct, `ker_cutoff` = 0.28 labels almost everything.**
  At `ker_n` = 729 it labels 100.0% of the 7,563 inside bars and 100.0% of the 26,997 outside bars,
  on all seven series checked. At each series' flip point it labels 88% to 95% of both.
- The reason KER reads higher inside the windows at short `ker_n` is **not measured**.

---

## provenance

- Every figure in this document was measured against `ws_line_bar`, `kline_collection`,
  `mech_line_config` and `optimus9_system` on 2026-09-03. None has been validated by Joe.
- `ker_cutoff` = 0.28 is **fitted, not measured**, and must be labelled so wherever it is quoted.
- Joe's own consolidation reads are banked in `eyes_on_pine` — pk 352 and 354 (2026-08-04 09:23:15
  and 12:00:00, *"09:23 and 12:00 are in the middle of consolidation"*) and pk 361-363 (2026-08-04
  06:48:00 / 06:50:25 / 06:52:10, *"these are exactly correct - price went semi sideways for a few
  minutes after a solid sell-off"*). Both are point labels; neither bounds an episode. Any rule
  scored against them is fitted, not measured.
