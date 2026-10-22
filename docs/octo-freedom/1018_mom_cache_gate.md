# 1018 — the momentum cache for octo-v3: what exists, what blocks, what is unspecified

Joe 1018: *"you mentioned using gpu to build the momentum cache. we'll need it tomorrow, all
g15-30 and ws1-60"* / *"we'll need the away and toward tags"*

BUILD-GATE. Nothing built, nothing moved, no code written. Every concretion below is listed, not
decided, except the two marked MINE.

## 1. What I actually said about the GPU, for the record

> "The large array work that *would* suit the GPU — the line builds, the mom-true masks, the
> r/Mage/x ladders — is already built once and cached to `.npy`."

So the mom-true masks were named as GPU-suitable. The walk itself was not: `anchor_floater` was
3.3% of a walk, the other 96.7% being octo2's python event loop.

## 2. The lines that exist on disk — `optimus9/orchestration/.rpl_cache/lines`

| the band Joe asked for | lines present | lines absent |
|---|---|---|
| g15 to g30 | g15, g30 | g20, g25 |
| ws1 to ws60 | ws1-ws30, ws45, ws60 (32 TFs) | ws31-ws44, ws46-ws59 (28 TFs) |

- every present TF has all five roles: r, Mage, x, m, b.
- also present outside the ask: g5 (r, Mage only), g60 (all five).
- a momentum cache cannot be built where there is no line. The line build is a PREREQUISITE, a
  separate job from the mask build.

## 3. BLOCKER — the momo knob bank has no band below timeframe 1

`momo_bank(db, 0)` raises `LookupError: momo_config has no bank covering timeframe 0`.

| the band in `momo_config` | tf_lo | tf_hi | k_window | momo window = k_window x tf |
|---|---|---|---|---|
| band 1 | 1 | 12 | 6 | 6 min at ws1, 72 min at ws12 |
| band 2 | 13 | 60 | 6 | 90 min at ws15, 360 min at ws60 |
| a g line | — | — | — | NO BAND. `int(0.25)` = 0 |

g15 and g30 have no `k_window` and no slope / r2 / curl gates. Nothing can be measured on them
until a bank covers them.

## 4. The measured CPU cost, r role only, both sides, 1,632,960 bars

Timed on 2,000 real `momo_g` calls at bar 900,000, per timeframe.

| the tf | k_window | momo window | calls/s | projected, 1 TF x 2 sides |
|---|---|---|---|---|
| ws1 | 6 | 6 min | 13,378 | 244 s = 4.1 min |
| ws12 | 6 | 72 min | 14,599 | 224 s = 3.7 min |
| ws30 | 6 | 180 min | 5,766 | 566 s = 9.4 min |
| ws60 | 6 | 360 min | 19,007 | 172 s = 2.9 min |

- the rate is NOT monotonic in the window: ws30 is the slowest and ws60 the fastest. UNEXPLAINED.
  I have not read the reason and will not guess one.
- only 4 timeframes were timed. The mean of the 4 is 301 s per TF.

## 5. The scale, from that mean

| the set | TFs | roles | serial hours | on 16 cores |
|---|---|---|---|---|
| the 32 ws TFs that have lines | 32 | r only | 2.7 h | ~10 min |
| the 32, all five roles | 32 | 5 | 13.4 h | ~50 min |
| the full ask, ws1-ws60 + g15-g30 | 64 | r only | 5.4 h | ~20 min |
| the full ask, all five roles | 64 | 5 | 26.8 h | ~1.7 h |

Hardware: 16 cores, 23 GB RAM, RTX 3060 Ti with 7.47 GB free, CuPy 14.1.1.

Storage is not a constraint. 35 masks on disk now total 1.2 MB; 320 masks project to ~11 MB.

## 6. The away / toward tags

The rule is Joe 0829, implemented in `report_wsf_bar.heading(dr, held, extrema_r, momentum_true)`:

> "`toward` means the line is heading towards the oob, and `away` means that the line has gone as
> far as it can into oob, printed an extrema, and is now moving `away` from the extrema"

    if momentum_true:        return 'toward'     # C4 - a new cycle has started
    if extrema_r is None:    return 'toward'
    return 'away' if held >= MOMO_STALL_DELAY else 'toward'

`MOMO_STALL_DELAY` = 5 bars of the 5 s grid = 25 s, Joe 0829: *"create a {knob:5}
MOMO_STALL_DELAY (25 seconds)"*. FLAT across every timeframe as written.

Three inputs per bar per TF per side: `momentum_true` (the mask from S4), `extrema_r` (the
same-side extrema since the last mom-true bar), `held` (5 s bars since the line turned off that
extrema, elapse-counted, no reset).

BLOCKER — its current input producer reads the `wsf_line_bar` DB table:

| `wsf_line_bar` | value |
|---|---|
| rows | 3,732,552 |
| covers | 2026-08-25 00:00:00 to 2026-08-28 00:00:00 |
| timeframes | 1 to 12 only |
| knob sets | 3 |

3 days of 94, and TF1-12 of the 64 asked for. The table cannot serve this cache.

## 7. The two I would decide, stated not asked

- **MINE: recompute the extrema / held walk from the `.npy` arrays, not from `wsf_line_bar`.** The
  0829 rule needs only r, the extrema walk and the mom-true mask - all three are arrays. Reading a
  3-day TF1-12 DB table would silently truncate 91 days and 52 timeframes. Structural, precedent
  exists (`_momtrue` already works off `SC.LD`).
- **MINE: the mask cache must move off the job temp dir.** It now lives at
  `/home/joe/.claude/jobs/6eb9931e/tmp/momt_cache` - 35 files, 1.2 MB, inside a DELETABLE scratch
  directory belonging to a finished session. Target: a durable path beside the line cache. The
  keys do not change, so every mask on disk stays valid. NOT MOVED YET.

## 8. The gate — Joe's to rule, nothing started until he does

| # | the question | why it is his |
|---|---|---|
| 1 | g15-30: is the set {g15, g30}, or do g20 and g25 need a line build first? | the TF set is his |
| 2 | ws1-60: 28 TFs have no lines. Build them, or is the set ws1-ws30 + ws45 + ws60? | the TF set is his |
| 3 | which ROLES per TF - r only, as today, or r/Mage/x/m/b? | 5x the work, 5x the cache |
| 4 | which momo bank governs a sub-minute line - the 1-12 band, or a new band with its own knobs? | a knob value |
| 5 | does `MOMO_STALL_DELAY` stay 25 s flat on ws60, or scale with the timeframe? | a knob value |
| 6 | GPU or 16-core CPU - see below | where the risk sits |

## 9. On the GPU, raw

The measured numbers say the GPU is not needed for this.

| the route | wall clock, 64 TFs x 5 roles | what is at risk |
|---|---|---|
| 16-core CPU, multiprocess | ~1.7 h | nothing. Same banked `momo_g`, byte-identical to today |
| GPU rewrite | minutes, once correct | a SECOND implementation of a banked mech |

A GPU mask means re-deriving `momo_core.verdict` plus Joe's 0805 curl gates as batched array work.
That is a parallel implementation of a mech that is already banked, so no number off it is usable
until a 0-mismatch parity proof against the CPU path exists - 1,632,960 bars x both sides x every
TF, not a slice. The 1008 and 1014 cache-drift failures were both silent, and both were caught by
a control row, not by inspection.

My recommendation: 16-core CPU first, because it delivers tomorrow with zero reimplementation
risk. Keep the GPU for the work that has no CPU route - and say so when one appears.
