# 1007 — the >ws12 baton mech

Joe's spec, his rulings, and what leg 8 measured. Knobs are durable in `ws12_baton_config` v1
(19 rows, key `ws12_baton_config.v1`), seeded by `seed_ws12_baton_config.py`.

Scripts: `_chain9.py` (the ceiling rule in the chain), `_ws12mech.py` (branches 1 and 2),
`_rrev_xwob.py` (the r-reversal trigger and the xwob sweep), `_three_filters.py` (the three
proposed filters), `_leg8_lines.py` (leg 8 line by line), `_dip50.py` (the dip and its dwell).

---

## 1. THE CEILING RULE

Joe 1007: *"add this rule - if ws12r crosses into oob, then extend the max TF to ws23"* /
*"this is a per leg mech"*.

- the ceiling starts at **ws12** (`lazy_g_config` ladder.band_hi) at every leg OPEN
- on the first bar of the leg where **ws12r CROSSES into oob on the leg's own dr side** — over 85
  for a LONG leg, under 15 for a SHORT one — the ceiling latches to **ws23** and holds for the rest
  of that leg
- PER LEG: the next leg opens back at ws12
- it bounds the kickstart's scan AND the baton's candidate range. The baton still hops at most
  `lin_hop` 2 TF numbers and still never goes backwards
- the x-cross reads `ws{rider+1}r` and `ws{rider+2}r`, so at the extended ceiling that is ws24r and
  ws25r. Both lines exist in the cache, finite on every bar of 09-25

MEASURED, leg 8 (09-25, LONG, open 08:10:00):

| what | before the rule | after the rule |
|---|---|---|
| exit | 09:17:55, ws12 stall | 10:25:00, ws23 x-cross |
| realised | +2.3668 | +2.6342 |
| hold | 67.9 min | 135.0 min |
| baton | ws9 → ws11 → ws12 | ws9 → ws11 → ws12 → ws13 → ws14 → ws15 → ws17 → ws18 → ws19 → ws21 → ws22 → ws23 |

- the latch fired at **08:24:05** (ws12r 84.83 → 85.20), 1.9 min *before* the baton reached ws11
- legs 1-7 of the 02:48:50 chain are **unchanged**: 0 of 8 legs latched, ws12r never crossed into
  oob on any of them
- across the 26 octo-sig-seeded chains, **12 of 100 legs latched**

---

## 2. THE DELAY THE RULE EXPOSED

Joe 1007: *"at 10:25, we've overshot the pivot at 09:32 and lost ~0.9 profit - that's what set me
on this quest"*.

The pivot is **09:28:25 at +3.7353** (swing_detect `find_pivots` at the banked `swing` 1.25). The
give-back is **1.1011**, not ~0.9 — the ~0.9 came from the highest *traced event* bar, which was
the wrong unit.

| ts | +min | pct | event |
|---|---|---|---|
| 09:28:25 | +78.4 | +3.7353 | PIVOT H — also the leg's MFE bar |
| 09:35:00 | +85.0 | +3.4213 | ws23 becomes the rider (ws23r 85.71 oob) |
| 09:38:55 | +88.9 | +3.0204 | ws23x under BOTH ws24r and ws25r — the cross itself |
| 10:23:25 | +133.4 | +2.3507 | ws24r still 89.09 — oob, the gate still shut |
| 10:24:00 | +134.0 | +2.4107 | ws24r 77.13 in-fence |
| 10:25:00 | +135.0 | +2.6342 | ws25r 78.82 in-fence — both in-fence, EXIT fires |

- **the cross was not the delay.** It was true from 09:38:55, 46.1 min before the exit
- **ws24r is the binding gate: 0 in-fence bars out of 573** between 09:36:00 and 10:23:25
- the two costs split unevenly: the 10.5 min from pivot to cross cost **0.7149**; the 46.1 min
  waiting for both targets in-fence cost **0.3862**
- **ws23 never stalled** in 135 min. Its stall sampling is step 83 bars = 415 s x 21 samples = a
  **138.3 min window**, and `stall_n` 6 consecutive samples means **41.5 min with no new extreme**.
  It cannot print inside a 135-min leg. This is held task #60 arriving at ws23.

The delay per rider band, 49 x-cross legs over 12 days, measured from each leg's own MFE bar:

| rider band | x-cross legs | delay med min | give-back med | give-back total |
|---|---|---|---|---|
| ws1-ws2 | 12 | +2.0 | +0.3216 | +3.7100 |
| ws3-ws6 | 12 | +2.1 | +0.4099 | +5.1733 |
| ws7-ws12 | 17 | +5.4 | +0.4718 | +11.9411 |
| ws13-ws23 | 8 | +8.3 | +0.6765 | +5.7958 |

- both the median delay and the median give-back rise with the band. The max does not separate
- the "delay from the target pivot" measure is **unusable at swing 1.25** — pivots are rare enough
  that the first favourable pivot after the open often lands after the exit (three ws13 legs at
  −587.6, −357.0 and −220.2 min). Only the MFE-bar measure carries the question

---

## 3. THE MECH — Joe's spec verbatim

```
over ws12 baton mech dev
-apply this logic after ws12r is oob for >6 minutes
--if ws12x-crosses ws12r inside the first 6 minutes, the cross is the trade signal
--wait for ws1Mage to "dip" over/under 50.  if +dr, then Mage will cross under 50, inverted for -dr
---#this is the signal that pressure is weakening
---start divergence testing for ws1r and ws2r, test at each ws1mage-rev
---if divergence is found, create an exit
```

### Joe's rulings on it

| # | ruling | verbatim |
|---|---|---|
| 1 | the first-6-min cross is read counter-dr | *"counter-dr. eg if +dr, x crosses under"* |
| 2 | ws1r and ws2r combine with OR | *"OR"* |
| 3 | every mage-rev test is dr aligned | *"all mage-rev tests are dr aligned: +dr requires a hi oob Mage"* |
| 4 | the trigger moves off ws1mage-rev | *"let's drop ws1mage-rev and replace it with ws1r-reversing for the ws1 divergence test, and ws2r-reversing for its divergence test"* |
| 5 | the x-cross marks the reversal | *"what I see consitently is a ws{tf being tested}x crossing under (for +dr) its r at the time that r is reversing (which makes sense - BBs lead Ks)"* |
| 6 | the dip takes a dwell | *"we use a dwell > 12 bars"* / *"I'm good with dwelling the dip"* |

Ruling 3 settles what `jig.ws1mage_rev` left open — its `rev` array is direction-unfiltered by
design (*"Joe said 'ws1 Mage reversing' and never ruled on it"*). A test bar must be in `rev` AND
in `dwell_ok`, which is the producer's own dr-side oob run.

---

## 4. WHAT LEG 8 MEASURED

### branch 1 — no fire

- no counter-dr ws12x cross of ws12r inside the first 6 min of the oob run

### branch 2, before the dwell — fires 61.7 min early

| trigger | first | min from pivot | pct |
|---|---|---|---|
| ws1mage-rev + divergence (the original) | 08:58:10 | −30.2 | +2.7898 |
| ws1r reversing + divergence | 08:13:35 | −74.8 | +0.3728 |
| ws2r reversing + divergence | 08:20:15 | −68.2 | +0.9458 |
| ws2r reversing + divergence + x under r | 08:26:45 | −61.7 | +1.5038 |
| **+ dip dwell > 12 bars** | **09:32:15** | **+3.8** | **+3.4555** |

- the original `ws1mage-rev` trigger **undershot by 30.2 min**, and its exit bar was chosen by ws2r
  stepping over 50 — `anchor_floater` step 1 refuses an anchor below 50 at dr +1, so the 2-min
  line's update step picked the bar
- **ws1r never fired once** on leg 8, at 90.49-99.69 across every test bar. Under an AND reading
  there is no exit at all. Ruling 2 is what produces one
- ws1r is unusable alone as a trigger: **144 reversals in 135 min**, the divergence firing at the
  4th
- **51 of 135 ws2r reversals carry a divergence; 25 of those also have x under r.** 09:32:15 is one
  of 25, not the first — the dwell is what makes it first

### the exit, with the dwell

- **09:32:15 at +3.4555** — ws2r 74.05, ws2x 54.91 under it, fired +1 off floater 09:07:05,
  d_osc −20.94
- **0.2798** below the pivot, **+0.8213** above the x-cross exit's +2.6342

---

## 5. THE xwob ON THE x-CROSS

Joe 1007: *"what xwob would we need to correclty pick the x-cross that pushes r into a reversal?"*

| xwob bars | seconds | ws1 crosses | ws1 spurious | ws2 crosses | ws2 spurious |
|---|---|---|---|---|---|
| 1 | 5 | 73 | 22 | 34 | 6 |
| 2 | 10 | 54 | 10 | 29 | 5 |
| 3 | 15 | 41 | 3 | 28 | 5 |
| 4 | 20 | 32 | 1 | 25 | 4 |
| 6 | 30 | 27 | **0** | 19 | 2 |
| 8 | 40 | 22 | **0** | 17 | **0** |
| 12 | 60 | 19 | 0 | 14 | 0 |

- **`x_rev_xwob` 8 bars = 40 s** is the smallest value that drives spurious crosses to 0 on both
  lines. ws1 gets there at 6; ws2 needs 8
- above 8 the cross count keeps falling with no spurious left to remove, so 8 is the knee
- **ruling 5 is in the numbers**: at xwob 8 the median lag from cross to reversal is **+5 s on ws2
  and +10 s on ws1**. The cross leads
- the nuance: **the cross is sufficient, not necessary.** At xwob 8, 122 of 144 ws1 reversals and
  118 of 135 ws2 reversals have no cross at all

---

## 6. THE DIP AND ITS DWELL

| dip bar | min from pivot | ws1Mage | run bars | run min | dwell > 12? |
|---|---|---|---|---|---|
| 08:49:55 | −38.5 | 49.87 | 9 | 0.8 | no |
| 08:50:45 | −37.7 | 48.93 | 1 | 0.1 | no |
| 09:17:30 | −10.9 | 49.57 | 1 | 0.1 | no |
| 09:17:50 | −10.6 | 47.80 | 7 | 0.6 | no |
| 09:20:10 | −8.2 | 48.24 | 44 | 3.7 | **YES** |
| 09:40:30 | +12.1 | 47.61 | 513 | 42.8 | YES |
| 10:23:20 | +54.9 | 48.23 | 1 | 0.1 | no |
| 10:23:30 | +55.1 | 49.65 | 1 | 0.1 | no |

- the gate opens at **09:21:05** (09:20:10 confirmed after 12 bars) and the next qualifying bar is
  **09:32:15**
- **the dwell value is not pinned by this leg.** The runs are 9, 1, 1, 7, 44, 513, 1, 1 bars, so
  any threshold from **9 to 43** gives the identical answer. Joe's 12 is inside that band and the
  data cannot yet distinguish it from 10 or 40. Joe 1007: *"it looks like we can go higher - that's
  good to know when we target more examples"*
- the dip my first run took was **08:49:55 with a 45 s dwell** — the shortest of the five — and
  ws1Mage climbed 49.52 → 94.15 in the 8 minutes after it

---

## 7. REJECTED AND UNTESTED

### `div_floor` — REJECTED, measured inverted

| abs d_osc floor | bars in | first survivor | min from pivot | target first? |
|---|---|---|---|---|
| 0 | 25 | 08:26:45 | −61.7 | no |
| 15 | 21 | 08:33:20 | −55.1 | no |
| 25 | 9 | 08:33:20 | −55.1 | no |
| 40 | 4 | 08:34:00 | −54.4 | no |

- the target's |d_osc| is **20.94**; the false early ones are **28.57, 41.36, 45.35**. A floor
  removes the target before it removes them. 0 of 10 floor values put the target first
- on this leg the divergence magnitude carries no information about which bar is right

### `floater_oob` — UNTESTED

- Joe 1007: *"we require the floater to be oob (I think this is already in-spec)"*
- **it is in-spec for `divergence()`, not for `anchor_floater()`.** `divergence` builds both
  lookbacks from consecutive same-side **oob episodes**, so its extremes are oob by construction.
  `anchor_floater` filters step 3 on *"the dr side of 50"* and its docstring states *"No fence: the
  85/15 in `divergence` plays no part here"*
- Joe 1007 on that: *"there's context for that `no fence` statement in the docs - I think I was
  referring to lines higher than ws1 and ws2 (maybe ws4 at the time)"*
- the filter removed **0 of 25** bars on leg 8: every floater was already oob (100.00 for the
  thirteen before 09:30, 95.00 for the 09:32-09:38 cluster). Left at 0 = OFF, untested rather than
  validated

---

## 8. THE g30 FINISHER QUESTION

Joe 1007: *"if the g30 'finisher' (my coined) event happens at or just before the ws{TF}Mage has
reversed, is that event actioned on or does the mech walk forward to find the next g30 event"*

| path | what happens to a g30 cross at or just before the Mage reversal |
|---|---|
| `leash_walk` (the octo-sig) | ACTIONED — there is no anchor ordering at all |
| `mage_rev_walk`, `sig_lookback` 0 | SKIPPED — the walk takes the next g30 event |
| `mage_rev_walk`, `sig_lookback` 24 | ACTIONED — a cross up to 120 s before the anchor qualifies |

- the octo-sig path never had the problem. `leash_walk.rev_lookback_mask` is a per-bar window mask
  — bar `k` is True when a g30 cross sits in `[k − lookback, k]` and its `sig_conf` is at or before
  `k`. The Mage reversal is not part of that test
- `mage_rev_walk` orders `dwell_ok → rev (anchor) → sig` and selects `s > b − lb`. At
  `sig_lookback` 0, the producer's **default**, that is `s > b` — strictly after the anchor
- it has already bitten, and the docstring records it: 09-02 18:15:00, g30 `sig` 5 s before the
  anchor, skipped, next one **22.5 min later**
- a cross landing exactly on the anchor bar passes at any lookback ≥ 1 and fails at 0
- **the only caller in the repo passes 48 bars = 4 min, not Joe's 24 = 2 min.** `entry_ab.py:102`
  uses `sig_lookback = lookback_s // 5` with `lookback_s` 240, printed as "MATCHED" to the rev
  lookback — one knob serving two different allowances
- `sig_lookback` was **in no config table**. It is now `ws12_baton_config` mage_rev.sig_lookback_bars = 24

---

## 9. OPEN

| # | question | why it is open |
|---|---|---|
| 1 | does the mech stay armed after ws12r leaves oob? | ws12r's run ended 08:44:45; the 09:20:10 dip is 35.4 min later. My build keeps looking forward with no re-check. If arming dies with the oob run, the only dip on leg 8 is 08:49:55 |
| 2 | `rrev_wob` for r | carried over as 2 from the Mage knob. It sets how many reversals exist at all — 144 on ws1r, 135 on ws2r in 135 min |
| 3 | `oob_gate_run` consecutive or cumulative | a single 10 s gap at 08:26:20 split leg 8's run and moved the gate 2.4 min later |
| 4 | the leg's dr or the tape's per-bar dr | every test here reads the LEG's d, on precedent. The tape's dr flipped to −1 at 10:02 inside leg 8 |
| 5 | n = 1 | every number in sections 4-7 is one leg. The 12-day population is section 2 only |

---

## 10. ALSO BANKED 1007

- **the sanctioned set is `with-trend` only**, 53 rows over 12 days. Joe 1007: *"we haven't
  sanctioned `no r block`"*, so its 45 rows neither seed a chain nor force an exit
- **the MAE review stop**: a leg closes AT the first bar its adverse excursion from its own open
  exceeds 1.1%, and the chain halts there. Read per leg, which is the project's unit for MAE
- **a target-dr sanctioned octo-sig is a mandatory exit and entry.** Joe 1007: *"if a leg is met by
  a target dr sanctioned octo-sig, then you must accept it as a exit and enter timestamp"*. It
  fired 6 times in 101 legs for −0.5961; 6 of the 7 legs where the alternation fought the tape dr
  open at one of these bars
- **the stash is in LIMBO**, not adopted: *"we're keeping this in limbo for now - it might be
  useful later"*. Measured +5.0400 on vs +5.1380 off over 30 chains
- **the tape is CONTIGUOUS** — 1,632,960 bars x 5 s from 07-02 12:00:00 to 10-04 23:59:55. The
  day-end bound in `_chain_os.py` was an invented truncation and ended 2 of 30 chains for no reason
  in the data
- **the one-time kickstart**: the momentum read picks the STARTING rider, then the established
  lineage walk owns it. Joe 1007: *"I meant for ws2Mage momentum detection as a one-time thing to
  kickstart the established lineage walk"*. It restored leg 1 to +0.9501 and legs 1-7 to +4.1310
- **`score39`'s tape is cwd-sensitive.** From `1005_scoring` with `LG_TAPE_END=2026-10-05` it is
  1,632,960 bars to 10-04 23:59:55; from another directory it silently resolves to 1,630,780 bars
  to 10-03 20:58:15
