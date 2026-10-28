# the pseudo-closed line — BANKED 1028

Joe 1027 named it and asked for it:

> can we simply look back the width of the TF, at each emerging bar, and test the diff between the
> first value (one TF-width earlier) and the current bar's value? eg at 1432 testing ws13r, get the
> ws13r emerging value at 1419 and the ws13r emerging value at now, and create a psuedo ws13 closed
> bar?

> forge - lets make things easier for ourselves

and on 1028: *"I didn't ask you to bank everything pseudo_closed"* — so it is banked here.

## What it is

At every 5 s bar `t`, ws{T}r is computed on the bar sequence that **ends at t**: closes at `t`,
`t−T`, `t−2T`, … So the value at `t` is the CLOSED value of a ws{T} grid phased to close exactly at
`t`. Every bucket is complete; none is a forming bucket.

`pseudo_closed.series(close, tf_minutes, idx)` → the line at each bar in `idx`.

## Why the seam is a legitimate choice — his own argument

> if teadingview are using midnight as the offset for non-standarad lines, it backs the concept of
> choosing any seam

TV re-anchors non-day-divisor TFs to midnight rather than the epoch, so the seam is already a
choice. This picks the seam that closes at the bar being read.

## It is causal by construction

Every input is a close at or before `t`. No forming bucket, no forward read.

## The chain is the product's own, not retyped

| the piece | read out of |
|---|---|
| `k = SMA(Stoch(RSI(close, 5), 8), 7)` | `indicator_computer.f_k` |
| Wilder RMA, SMA-seeded, `prev = (prev*(n−1)+x)/n` | `indicator_computer._rma` |
| stoch, 50 where the range is 0 | `indicator_computer._stoch` |
| the param order `('k', rsi 5, stc 8, k_len 7, 'close')` | `line_config` — transposing it is silent and gives a different line |

## The knobs

| the knob | value | whose |
|---|---|---|
| `RSI_N` | 5 | the product's — `mech_lines(db,'wsf')` |
| `STC_N` | 8 | the product's |
| `K_N` | 7 | the product's |
| `BARS` | 120 TF bars of history per read | a WARMUP, mine, and `converged()` reports what doubling it changes |

## Validated — `validate.md`

| the test | the result |
|---|---|
| on bars where the midnight grid closes, it must EQUAL the product's closed read | **ws15r and ws16r are bit-exact, max diff 0.000000** — this proves the chain is the product's line |
| ws13r / ws14r at the same test | max diff 18.36 / 13.45, median 0.000032 / 0.000044, 254 / 237 bars over 0.01 |
| the warmup doubled, 120 → 240 | max change ~1e-8, i.e. float noise. BARS 120 is justified |

**THE ws13/ws14 GAP HAS ONE CAUSE AND IT IS A PROPERTY, NOT A DEFECT.** 1440 / 13 = 110.77 and
1440 / 14 = 102.86, so TV's midnight re-anchor gives those a SHORT final bucket each day. The
rolling seam steps back by exactly T and ignores the re-anchor, so the two diverge near midnight
and the RMA memory carries it forward. ws15 and ws16 divide 1440 evenly, which is why they are
exact. A rolling seam and a day-anchored seam cannot agree on a non-divisor TF; a hybrid is not
definable.

## What has NOT been tested on it — corrected 1028

| the grooming | measured on |
|---|---|
| the reversal wob, 8 → 32 | the EMERGING line |
| the cadence-sampled view | the EMERGING line |
| his 40/60 reversal fence | the EMERGING line |

The ONE pseudo-closed test — `leadtest.md` — was on the RAW line with no grooming: 1117 ex-fence
entries against the emerging read's 236, 83.0% unconfirmed against 63.6%. That was read as a
verdict on the line and it is not one; the groomed comparison has never been run.

## Files

| the file | what it is |
|---|---|
| `pseudo_closed.py` | the producer |
| `validate.py` / `validate.md` | the three tests above |
| `leadtest.py` / `leadtest.md` | ex-fence entry lead and unconfirmed rate, RAW |
| `revwob.py` / `revwob.md` | the reversal wob priced against the closed chart — EMERGING |
| `wob_both.py` / `wob_both.md` | static vs TF-relative wob — EMERGING |
| `perquery.py` / `perquery.md` | the per-query error at his real cadence bars — EMERGING |
| `cadview.py` / `cadview.md` | the cadence-sampled view — EMERGING |
| `fence40.py` / `fence40.md` | his 40/60 fence — EMERGING, cadence-sampled |
| `l2_em_vs_closed.md` | emerging vs closed reversal counts, ws13..ws16 |

## Open

| # | what is open | whose |
|---|---|---|
| 1 | the line has no name but this file's | his |
| 2 | whether lineage2 consumes it, and for which read — the ex-fence level, the reversal timing, or both | his |
| 3 | the groomed comparison: wob 32 + the cadence view + the 40/60 fence applied to pseudo-closed, against the same stack on emerging | mine to run once he rules 2 |
