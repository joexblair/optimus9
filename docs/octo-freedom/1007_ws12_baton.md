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

---

## 11. THE FULL 09-25 SCAN, AND THE 21:48 RULING

Joe 1007: *"scan 09-25 and find all of the ws12r oob >6 minutes. walk the process and share what
you see"*. Scripts: `_scan0925.py` (the full scan), `_scan0925_mm.py` (the walked timestamps and
MAE/MFE), `_dive2148.py` (21:48 bar by bar), `_pegging.py` (the HTF pegging measure).

**77 ws12r oob runs on the day across both fences. 11 pass `oob_gate_bars` 72.** 9 hi (+dr), 2 lo.

| oob from | dr | gate | branch 1 | 50 dip | confirm | exit | on | MAE% | MFE% | realised |
|---|---|---|---|---|---|---|---|---|---|---|
| 00:12:05 | +1 | 00:18:10 | — | 00:26:25 | 00:27:20 | 00:42:00 | ws1r | 0.3635 | 0.4624 | +0.3486 |
| 00:36:40 | +1 | 00:42:45 | — | 00:44:05 | 00:45:00 | 00:45:10 | ws2r | 0.4551 | 0.0000 | −0.4332 |
| 01:00:55 | +1 | 01:07:00 | — | 01:22:30 | 01:23:25 | 02:09:45 | ws1r | 1.1901 | 0.4877 | +0.1970 |
| 08:26:25 | +1 | 08:32:30 | — | 09:20:10 | 09:21:05 | 09:29:10 | ws1r | 0.0000 | 2.2602 | +2.1810 |
| 08:48:00 | +1 | 08:54:05 | — | 09:20:10 | 09:21:05 | 09:29:10 | ws1r | 0.0030 | 1.4436 | +1.3651 |
| 13:18:35 | −1 | 13:24:40 | — | 14:30:55 | 14:31:50 | 14:45:50 | ws1r | 0.7984 | 3.7035 | +2.0958 |
| 17:41:25 | +1 | 17:47:30 | — | 18:37:20 | 18:38:15 | 18:59:10 | ws1r | 0.3630 | 2.0224 | +1.1610 |
| 17:59:00 | +1 | 18:05:05 | — | 18:37:20 | 18:38:15 | 18:59:10 | ws1r | 0.1230 | 1.6411 | +0.7829 |
| 18:28:15 | +1 | 18:34:20 | 18:31:05 | 18:37:20 | 18:38:15 | 18:59:10 | ws1r | 0.4679 | 0.2867 | +0.0688 |
| 21:48:00 | −1 | 21:54:05 | 21:48:40 | 22:05:00 | 22:05:55 | 23:22:45 | ws1r | 2.5199 | 1.1633 | −2.0706 |
| 23:12:00 | +1 | 23:18:05 | 23:12:20 | 23:19:05 | 23:20:00 | — | — | — | — | — |

- **8 of 10 exits realised positive — 80%.** 7 of 11 ended MFE > MAE.
- **THIS IS THE LAST MILE.** Joe 1007: *"we're only reporting on the last mile (if you think about
  it, we already walked to the ws12 oob moment holding an open trade)"*. The trade is already open
  and already in profit by the oob moment, so every MAE/MFE above is the tail, not the trade.
- MAE/MFE run from the GATE bar. Branch 1 gave a real open on only 3 of 11, so on the other 8 the
  gate bar is a stand-in - mine, and said here rather than per row.
- **11 runs yield only 7 distinct exits.** 08:26:25 and 08:48:00 share the 09:20:10 dip and exit
  together at 09:29:10; 17:41:25, 17:59:00 and 18:28:15 all share 18:37:20 and exit at 18:59:10.
  Anything that counts per run double-counts.
- **reading B kills 7 of 11** (spec open #1): only 00:36:40, 18:28:15, 21:48:00 and 23:12:00 have a
  dip starting inside the oob run. Leg 8's dip is 35.4 min after its run ended.
- **1 of 11 never exits**: 23:12:00 finds no qualifying reversal before the day end.
- the MFE/MAE ratio is unstable at tiny MAE - 08:48:00 prints 483.66 at MAE 0.0030 and 08:26:25
  prints `inf` at MAE exactly 0. Read the two columns, not the ratio.

### 21:48 — RULED, accepted as it stands

Joe 1007: *"I've checked the three and there's no easy discriminator. we accept 21:48 as it is, the
1.1 stop fires at ~22:18"*.

| what | ts | +min | pct |
|---|---|---|---|
| ws12r oob from | 21:48:00 | −6.1 | +0.0654 |
| branch 1 cross | 21:48:40 | −5.4 | +0.0213 |
| gate bar | 21:54:05 | +0.0 | +0.0000 |
| MFE | 21:58:20 | +4.2 | +1.1633 |
| 50 dip | 22:05:00 | +10.9 | −0.0087 |
| dip confirmed | 22:05:55 | +11.8 | −0.0343 |
| **EXIT — mae 1.1** | **22:17:15** | **+23.2** | **−1.1061** |

Joe 1007 corrected the row: *"EXIT is 22:18, cause: mae1.1"*. The stop IS the exit on this run, not
a counterfactual beside it. What the mech would have done without the stop is recorded below for
the diagnosis only - it is not this run's exit.

| not the exit — the mech's own path past the stop | ts | +min | pct |
|---|---|---|---|
| MAE | 23:16:45 | +82.7 | −2.5199 |
| the mech's ws1r exit | 23:22:45 | +88.7 | −2.0706 |

- **the exit is 22:17:15 at −1.1061, on `mae_stop_pct` 1.10.** No new mech is needed; the banked
  stop is what closes this run, 65.5 min before the mech's own divergence exit would have.
- the realised for this run is therefore **−1.1061, not −2.0706**. Every table above that shows
  −2.0706 for 21:48:00 is the no-stop reading.
- **the divergence held the exit off, not the x-cross.** 166 reversal bars between the confirm and
  the exit: 165 blocked, **164 of them by no divergence at all**. Only 38 were blocked by x not
  being over r, and every one of those was also blocked by the divergence.
- the exit was not even the best bar available: the best pct at any reversal bar in that window was
  **−2.5038 at 23:17:40**. Every bar was worse than the gate.
- **the arming sequence is slower than this leg's favourable window**: the MFE came at +4.2 min and
  the mech's earliest possible exit was the confirm at +11.8 min.
- ws12r is **91.90 at the exit** against **5.65 at the oob start** — the mech held a SHORT while its
  own trigger line crossed the whole range to the opposite fence.

### HTF pegging — measured, and it is not a discriminator

Joe 1007 named it: *"ws12Mage ... stayed higher than 50 after travelling from a high oob at 20:24.
that's my definition of HTF pegging"*.

- the oob visit **ends 20:59:10**, not 20:24 - ws12Mage was hi-oob for **663 bars** from 20:01:40.
- *"stayed higher than 50"* is absolute: **0 of 1724 bars below 50** from 20:59:10 to the exit, with
  a floor of **53.07 at 21:58:20 — the trade's own MFE bar**.
- **pegged at the gate: 3 of 11** - 13:18:35, 17:41:25, 21:48:00. Only 1 of the 3 has MAE > MFE, and
  the other two are the day's **highest MFE (13:18:35, 3.7035)** and its **third-highest (17:41:25,
  2.0224)**. As a filter it would discard two of the best runs.
- of the 4 runs with MAE > MFE, **only 1 is pegged**.
- the stricter *pegged through to the exit* reading isolates 21:48 alone - **1 of 11**, which fits
  perfectly and proves nothing.
- Joe checked the three and ruled: no easy discriminator. The stop carries it.
- **the cascade half is untested**: *"the peak of a mage cascade/mage ladder"* has no ruled
  producer and task #22 is parked. Everything above is the ws12Mage line only.
- the three 00:xx runs show no ws12Mage oob visit because my lookback stops at the day start; their
  last visit is probably on 09-24.

---

## 12. THE RE-ENTRY MECH, AND THE TWO-DAY A/B

Joe 1007: *"I'm keen to bake it in so that the chain is complete for the day. what do you need?"* ->
*"the only way to find the answer is to walk forward after an mae1.1 and A/B the 2 options"* ->
*"I say we continue the chain to the end of 09-26 and review"*.

Scripts: `_reentry_ab.py` (09-25), `_chain_2day.py` (09-25 + 09-26, both options, the stopped-trade
tables), `_reentry_x.py` / `_reentry_x2.py` (the cross and the gates), `_pierce0810.py`,
`_retest0849.py`, `_returns_align.py`, `_casc_shape.py`.

### THE CROSS — Joe's, and the wob is on the return leg only

Joe 1007: *"we're only wobbing the cross back towards 50. this makes it possible to allow a thin
ws1x spike to pierce down through ws1r before reversing back towards 50"*.

- **the pierce**: ws1x drops below ws1r. NO WOB - a thin spike qualifies. The 08:46:15 pierce is
  **2 bars** and the 08:11:20 pierce is **1 bar**; both returned with long runs.
- **the return**: ws1x crosses back above ws1r and HOLDS `x_rev_xwob` bars.
- **conf = return + xwob - 1**, the first bar the return is knowable, and the only bar a re-entry
  can be placed on.
- **xwob 6, not 8**: the 11:19:05 return holds 6 bars and not 8, so xwob 8 falls back to 11:14:30 -
  5.9 min early at 0.6697 worse.

### THE TWO GATES A/B'd

| | gate |
|---|---|
| **A** | ws1r <= `momo_fence_r` 17 at the RETURN bar, AND ws12Mage > ws1Mage at conf |
| **B** | every Mage ws1..ws12 > 50 at conf. No ws1r fence - Joe said *"only require"* |

| option | legs | positive | stops | re-entries | last exit | MAE | MFE | MFE/MAE | realised | at -1.10 |
|---|---|---|---|---|---|---|---|---|---|---|
| **A** | 43 | 29 | 12 | 12 | 09-26 20:09:10 | 21.4877 | 41.1325 | **1.91** | **+13.3928** | +14.2207 |
| **B** | 40 | 23 | 10 | 10 | 09-26 18:10:55 | 19.9127 | 33.7764 | 1.70 | +9.2482 | +9.8904 |

| option | day | legs | positive | stops | MAE | MFE | MFE/MAE | realised |
|---|---|---|---|---|---|---|---|---|
| A | 09-25 | 25 | 17 | 6 | 11.8959 | 27.8113 | 2.34 | +10.0229 |
| A | 09-26 | 18 | 12 | 6 | 9.5917 | 13.3212 | 1.39 | +3.3699 |
| B | 09-25 | 24 | 15 | 6 | 12.1010 | 23.9253 | 1.98 | +7.3481 |
| B | 09-26 | 16 | 8 | 4 | 7.8118 | 9.8511 | 1.26 | +1.9001 |

- **A leads on both days** and its edge widens from +1.5758 on 09-25 alone to **+4.1446** over two.
- 09-26 is the weaker day for both: MFE/MAE 2.34 -> 1.39 (A) and 1.98 -> 1.26 (B).
- **neither gate accepts 08:11** - A rejects on the fence (ws1r 25-26) and on the line
  (ws12M < ws1M); B rejects on **ws11 and ws12 Mage sitting below 50** (47-49 and 45-47). Joe's
  *"2% of gain between 08:11 and 08:46"* is left on the table by both.
- **neither gate reaches Joe's 08:10 bar.** A waits to 08:48:55, B to 08:30:55.
- A's 11:07:45 re-entry lands **11:20:45 - 15 seconds before Joe's 11:21:00 hand-pick**.
- B sits out **293.8 min** after the 13:22:35 stop against A's 81.3, which is where most of A's edge
  on 09-25 is made.

### #22, PARTIALLY UNPARKED

Joe 1007: *"do you feel confident to unpark #22 and use it for the A/B?"*

**Unparked: the direction half.** `ws12Mage > ws1Mage` - Joe's §3 verbatim 0918, *"the first thing I
look at is the lowest TF's value, and the highest TF's value ... I can draw a mental downward line
between those 2 numbers"*. It references **no dr**, which is the parked condition satisfied by
construction, and it has **zero knobs**.

**Still parked: the tolerance half.** The bump count and every threshold.
- `mage_cascade_findings.md` §7: bumps >= 8 / dr -1 was **+0.340 on 12 clusters in-sample** against
  **-0.478 on 127 clusters OOS**.
- §3's *"making allowances for the bumps"* - the allowance size is exactly what was fitted.
- §9: all three r tests null on 83 days, so no r-trajectory component.
- the peak TF is unruled and noisy: ws5, ws9, ws9, ws4, ws12 across five measured bars.

The 0918 shape findings DO apply and were confirmed on these bars:
- **`clusters` is the effective-n device** (§7, *"events separated by more than 120 min"*), and the
  re-entry returns arrive the same way: 08:11's three bars sit at ws1r 25.05 / 26.02 / 25.76 with
  4 of 11 rising steps on all three - **one event sampled three times**.
- **§8's hump-at-the-mid-board versus the monotone procession** separates the episodes. 08:11 peaks
  at ws5 and falls 32-34 points to ws12; 11:19 / 11:22 and 08:46 climb the whole way. On Joe's
  ws1-vs-ws12 line: **08:11 is -20.58, 11:x is +23.35 and +29.76, 08:46:25 is +33.07**.
- **§8's "at bumps >= 8 the r ladder cascades while the Mage humps"** holds on all three 08:11 bars
  and neither 11:x bar.

### THE STOPS — 14 distinct, and they are all the same shape

| day | side | open | exit | hold min | realised | overshoot past 1.10 |
|---|---|---|---|---|---|---|
| 09-25 | SHORT | 10:56:40 | 11:07:45 | 11.1 | -1.1504 | 0.0504 |
| 09-25 | LONG | 12:27:05 | 13:22:35 | 55.5 | -1.2224 | 0.1224 |
| 09-25 | LONG | 15:41:00 | 15:50:40 | 9.7 | -1.2981 | **0.1981** |
| 09-25 | SHORT | 18:59:10 | 20:01:55 | 62.8 | -1.1938 | 0.0938 |
| 09-25 | LONG | 21:27:40 | 21:58:20 | 30.7 | -1.2767 | 0.1767 |
| 09-25 | SHORT | 22:28:25 | 22:35:15 | 6.8 | -1.1523 | 0.0523 |
| 09-25 | LONG | 23:52:25 | 00:37:25 | 45.0 | -1.1625 | 0.0625 |
| 09-26 | LONG | 04:30:55 | 06:02:35 | 91.7 | -1.1088 | 0.0088 |
| 09-26 | LONG | 09:06:00 | 09:17:05 | 11.1 | -1.1685 | 0.0685 |
| 09-26 | LONG | 11:46:35 | 13:17:10 | 90.6 | -1.1228 | 0.0228 |
| 09-26 | LONG | 12:05:25 | 13:17:20 | 71.9 | -1.1044 | 0.0044 |
| 09-26 | SHORT | 14:17:35 | 14:36:30 | 18.9 | -1.1270 | 0.0270 |
| 09-26 | LONG | 16:25:40 | 18:10:55 | 105.2 | -1.1025 | 0.0025 |
| 09-26 | LONG | 18:37:00 | 20:09:10 | 92.2 | -1.1047 | 0.0047 |

- **A STOPPED LEG IS A LEG THAT NEVER ARMED.** Across all 22 stopped legs in both chains there are
  **0** occurrences of `exit-armed`, `KICKSTART`, `baton`, `HANDOVER`, `CEILING` or `50 dip`. Every
  event table is three rows: OPEN, MAE BREACH, EXIT. **No leg that armed was ever stopped.**
- Joe 1007 on seeing it: *"it seems that every one of them reversed instead of riding a >ws12 wave
  that the mech was built to handle. now I get to find why"* - **the why is his, open**.
- hold times run **6.8 to 105.2 min**: a leg can bleed for 1h 45m with no mech event at all.
- **11 of the 14 are LONG.**
- **the stop bounds the TRIGGER, not the FILL.** The exit is the first bar past 1.10 at that bar's
  price, so the loss is 1.10 plus one bar of movement. Overshoot across 22 stops: **min 0.0025,
  median 0.0523, max 0.1981**. Nothing in the knob bounds it.
- **no account figure exists**: position size is unset, so the wipeout question Joe raised
  (*"could a large MAE wipe out the account in one trade?"*) cannot be answered in account terms.

### THE SCORING CONVENTION, AND WHERE IT IS NOT APPLIED

Joe 1007: *"if mae1.1 was hit, then MFE is zero and MAE is 1.1"*.

- **running MAE takes 1.1000 and running MFE takes 0.0000** on a stop. Applied.
- **running realised does NOT** - it carries the measured overshoot. Flagged twice, unruled.
- at the convention: A **+14.2207**, B **+9.8904**. The +4.1 gap between them is unchanged.
- the argument each way, flat: as scored, realised is the only column tied to a fill; at -1.1000 it
  is consistent with the other two and a single 5 s bar's volatility stays out of the P&L.

### OPEN AFTER THIS SECTION

| # | question |
|---|---|
| 1 | why do 12 of 43 legs open and never arm? JOE'S - *"now I get to find why"* |
| 2 | does `realised` take -1.1000 on a stop, or the measured fill? |
| 3 | is 1.10 the right size? The stops are all never-armed legs, so tightening it changes no arm |
| 4 | the re-entry is LONG-only; the mirrored SHORT is unbuilt (spec open #3) |
| 5 | neither gate reaches 08:10. The reopen mech's own definition is still Joe's two bars, not code |

---

## 13. WHY THE NEVER-ARMED LEGS NEVER ARMED — THE LINE STATE AT THEIR OPENS

Joe 1007 took the `why` and asked for the raw state: *"I'll take this one - the never-armed legs'
line state at their opens"*, plus three measures he named. Scripts: `_neverarmed.py`, `_peg2.py`,
`_joereads.py`, `_front.py`, `_low3.py`, `_overlay.py`.

### THE ARM WAS NEVER CLOSE

| day | side | open | dr | ws2Mage | to its arm fence | ws1r | ws12r |
|---|---|---|---|---|---|---|---|
| 09-25 | SHORT | 10:56:40 | +1 | 76.88 | −61.9 | 56.50 | 31.90 |
| 09-25 | LONG | 12:27:05 | −1 | 29.58 | −55.4 | 97.81 | 37.94 |
| 09-25 | LONG | 15:41:00 | −1 | 27.51 | −57.5 | 26.71 | 60.87 |
| 09-25 | SHORT | 18:59:10 | +1 | 61.30 | −46.3 | 76.81 | 85.47 |
| 09-25 | LONG | 21:27:40 | −1 | 25.99 | −59.0 | 72.47 | 33.92 |
| 09-25 | SHORT | 22:28:25 | +1 | 85.70 | −70.7 | 4.34 | 38.77 |
| 09-26 | LONG | 04:30:55 | −1 | 11.91 | −73.1 | 0.37 | 52.99 |
| 09-26 | LONG | 09:06:00 | −1 | 25.13 | −59.9 | 35.41 | 29.82 |
| 09-26 | LONG | 11:46:35 | +1 | 33.59 | −51.4 | 9.39 | 62.63 |
| 09-26 | SHORT | 14:17:35 | +1 | 70.80 | −55.8 | 69.09 | 66.14 |
| 09-26 | LONG | 16:25:40 | −1 | 11.06 | −73.9 | 43.42 | 34.86 |
| 09-26 | LONG | 18:37:00 | −1 | 0.25 | −84.8 | 2.48 | 3.83 |

- **ws2Mage sits 46.3 to 84.8 points from its own arm fence at every open.** Not one leg was within
  reach. The arm is not marginal on these legs; it is absent.
- the leg's own side and the tape's dr **disagree on 7 of the 12**.
- on the leg's side the r ladder is outside oob and ex-fence from ws1 or ws2 on all 12, and **7 of
  12 have no TF in ws1..ws30 still inside**. On the TAPE's dr the same ladder reaches ws17-ws30.

### THE ARRIVED BAND AND ITS FRONT — the fuzzy object

Joe 1008 corrected a rigid read: *"ws10/11/12 belonged to a specific example. it could be
ws14/15/16, or ws9/10, or so-on. use a more fuzzy approach"*.

| open | dr | arrived band | front | trough | next 3 above | their distance to the ex-fence |
|---|---|---|---|---|---|---|
| 10:56:40 | +1 | ws6-ws30 | ws30 | ws29 | — at the top | — |
| 12:27:05 | −1 | ws6-ws9 | ws9 | ws7 | ws10, ws11, ws12 | 13.1, 18.1, 20.9 |
| 15:41:00 | −1 | ws4-ws30 | ws30 | ws29 | — at the top | — |
| 18:59:10 | +1 | ws12-ws28 | ws28 | ws24 | ws29, ws30 | 4.2, 17.3 |
| 21:27:40 | −1 | ws5-ws9 | ws9 | ws7 | ws10, ws11, ws12 | 14.0, 13.4, 16.9 |
| 22:28:25 | +1 | ws3-ws4 | ws4 | ws3 | ws5, ws6, ws7 | 3.1, 2.9, 25.8 |
| 04:30:55 | −1 | ws1-ws2 | ws2 | ws1 | ws3, ws4, ws5 | 6.3, 36.3, 31.3 |
| 09:06:00 | −1 | ws3 | ws3 | ws3 | ws4, ws5, ws6 | 5.3, 21.6, 22.6 |
| 11:46:35 | +1 | ws17 | ws17 | ws17 | ws18, ws19, ws20 | 5.6, 7.4, 16.0 |
| 14:17:35 | +1 | ws6-ws8 | ws8 | ws7 | ws9, ws10, ws11 | 7.5, 12.9, 27.2 |
| 16:25:40 | −1 | ws2 | ws2 | ws2 | ws3, ws4, ws5 | 23.1, 31.9, 17.3 |
| 18:37:00 | −1 | ws1-ws23 | ws23 | ws18 | ws24, ws25, ws26 | 0.2, 5.5, 11.3 |

- **the front sits anywhere from ws2 to ws30**; ws10/11/12 is simply the band above a ws9 front, and
  only 12:27 and 21:27 have one.
- **8 of 12 bands are unbroken, and 10 of 12 are NOT rooted at ws1** - the band is a travelling
  block in the middle of the ladder, not a tide rising from the bottom.
- **the ladder trough sits inside or at the edge of the band on every leg.** It is the band's centre.

### PEGGING CARRIES TWO MEANINGS, AND BOTH READ AS A GRADIENT

| the object | where it lives | what it looks like |
|---|---|---|
| the 10:56 read | the LOW TFs | a CLIFF in the counter-visit recency gradient |
| the 12:27 read | the HIGH TFs | a FRONT in the time-since-the-fence gradient |

- Joe 1007 at 10:56: *"Mage has not crossed into counter-dr ex-fence before returning to dr
  ex-fence"* - a NON-VISIT. The ws1-anchored test reproduces his **ws3**.
- Joe 1007 at 12:27: *"coming off a high ex-fence pegging that started at ~08:14"* - a LONG
  RESIDENCE, and at dr -1 the high fence IS the counter side, so those Mages did visit it.
- **THE ws1-ANCHORED TEST, as ruled by his worked example:**
  - anchor = ws1Mage's most recent counter-dr ex-fence bar at or before the open
  - pegged(t) = ws{t}Mage has NO counter-dr ex-fence bar in [anchor, open]
  - the answer = the lowest pegged TF. Knob-free, and reproduces ws3 at 10:56:40.
- **the low three, both legs, is the usable comparison Joe pointed at:**

| open | dr | counter side | ws1 | ws2 | ws3 | shape |
|---|---|---|---|---|---|---|
| 10:56:40 | +1 | LOW ≤17 | 48.1 min | 40.5 min | **195.2 min** | a cliff at ws3, 4.8× |
| 12:27:05 | −1 | HIGH ≥83 | 51.2 min | 45.8 min | 39.8 min | even, ~5 min steps |

- at 12:27 the de-pegging front on the high TFs is at **ws17**: ws10-ws16 left the high fence
  11.5-14.1 min before the open, ws17 0.7 min before, ws18-ws24 are still on it.

### THE FUZZY OVERLAY — three templates against the other nine

Six tests, all signs/orderings/TF-proximity, never absolute levels: the ws1r→ws12r direction, the
ws3x→ws12x direction, the ws3m→ws12m direction, the arrival front within 3 TFs, whether the arrived
band is unbroken, and the ws1/ws2/ws3 recency shape.

| template | near-match | side | dr | matched | the tests that did NOT match |
|---|---|---|---|---|---|
| 12:27:05 | 21:27:40 | LONG | −1 | **5 of 6** | recency shape |
| 21:27:40 | 12:27:05 | LONG | −1 | **5 of 6** | recency shape |
| 12:27:05 | 09:06:00 | LONG | −1 | 4 of 6 | front within 3, recency shape |
| 21:27:40 | 09:06:00 | LONG | −1 | 4 of 6 | front within 3, recency shape |
| 21:27:40 | 04:30:55 | LONG | −1 | 4 of 6 | ws1r→ws12r direction, front within 3 |
| 10:56:40 | 14:17:35 | SHORT | +1 | 4 of 6 | front within 3, band unbroken |
| 10:56:40 | 16:25:40 | LONG | −1 | 4 of 6 | front within 3, band unbroken |

- **12:27 ↔ 21:27 is mutual at 5 of 6**, missing only the recency shape: 12:27 is even steps
  (51.2 / 45.8 / 39.8), 21:27 is all three equal (41.9 / 41.9 / 41.9). Joe's own note on the
  difference: *"ws1r has dominated the lineage walk at 21:27 and the short trade is opened
  immediately"*.
- **the arrival front is the test that fails most** - 6 of the 7 near-misses. It moves far more
  between legs than the ladder directions do.
- the 4-of-6 line for "near-match" is MINE; the per-test grid is in the run.

### MY OWN DEFECTS IN THIS SECTION, ALL FOUND AND FIXED

- **the first pegging coding was degenerate**: it found the previous dr-ex-fence BAR rather than
  EPISODE, so ws1Mage's 10 s chatter made the window vacuous. It returned ws1 on 11 of 12 legs and
  failed Joe's ws3 self-check.
- **the angle column was `nan`** where a leave move's extreme sat on the fence bar - no move at all.
  Excluded and counted: 10 of 60 on the never-armed legs, 34 of 155 on the armed.
- **the recency shape discarded ties as `n/a`**, which threw away 4 of 12 legs including 21:27,
  where all three TFs touched the counter fence on the SAME bar - the tightest matryoshka there is.
- **`F1`..`F6` was coined shorthand that only existed in a docstring.** Joe: *"replace the jargon so
  that I'm able to help. I can't find a table anywhere that explains F{x}"*. The tests now carry
  plain names and the run prints its own legend.
- the only surviving thresholds of mine in this section: the 2.00 r-point turn detector on the leave
  move, and the 3× ratio that separates "even steps" from "one big step".

### STILL OPEN FROM THIS SECTION

| # | question |
|---|---|
| 1 | which "pegging" the mech takes - the low-TF non-visit, the high-TF residence, or both as separate mechs |
| 2 | why 12 of 43 legs open with ws2Mage 46-85 points from its arm fence. JOE'S |
| 3 | the arrival front moves more than anything else between legs - is it the discriminator or the noise |

---

## 14. 15:41 AND ws6 — THE WALK ALREADY GETS THERE, ON THE OTHER FRAME

> **READ §14b FIRST.** Joe corrected the frame of §14 and §14a: the walk is **naked**, and the bar
> it lands on is a **LONG ENTRY**, not the exit of a short. Every `SHORT realised` figure in §14
> and §14a is an **entry improvement**, not a trade. Nothing else in them changes.

Joe 1008: *"tell me if there's a method that would lneage walk 15:41 to the more optimised bar at
-dr ws6x-cross or stall (I can't recall if we're using x-cross or stall 😆)"*.

### WHICH ONE THE MECH USES — BOTH, AND THE STALL IS TESTED FIRST

`_chain10.run_leg`, in source order inside the per-bar loop:

```python
        if ST[(rider, d)][j]:                       # 'final stalled'  — tested FIRST
            return j, 'final stalled', ...
        if (not NOX) and xcond(rider, j, d):        # 'x-cross'        — tested SECOND
            return j, 'x-cross', ...
```

Both are live exits; on the same bar the stall wins. `W_NOX=1` is the switch that leaves the stall
alone, and that is swap 1 — **+0.6115 like-for-like on the 08:10 chain, MAE 3.5312 against 4.9518**.
**On 15:41 the ranking inverts: the x-cross beats the stall by 1.2550.** One leg each way, so the
swap is still unsettled and §12's open question stands.

### WHY 15:41 NEVER REACHED ws6: IT NEVER ARMED ON ITS OWN SIDE

The leg opened **LONG on a dr −1 tape**, and every r line at the open is low:

| TF | r | at d +1 (LONG) | at d −1 (SHORT) | ws{TF}Mage |
|---|---|---|---|---|
| ws1 | 26.71 | in-fence | in-fence | 24.22 |
| ws2 | 32.83 | in-fence | in-fence | **27.51** |
| ws3 | 18.98 | in-fence | in-fence | 35.21 |
| ws4 | 11.74 | in-fence | **oob** | 32.00 |
| ws5 | 26.76 | in-fence | in-fence | 30.50 |
| ws6 | 35.93 | in-fence | in-fence | 27.33 |
| ws12 | 60.87 | in-fence | in-fence | 27.70 |

Nothing on the `d +1` column is oob, so there is no KICKSTART to make and no rider to carry a baton.
The arm is the gate in front of all of it, and **ws2Mage 27.51 is 57.5 points from the ≥85 it needs
on the leg's side** — the never-armed figure already banked in §13.

### THE SAME WALK, THE SAME KNOBS, THE OTHER FRAME

| ts | +min | event | pxs | pct |
|---|---|---|---|---|
| 15:41:00 | +0.0 | OPEN | 0.187001 | +0.0000 |
| 15:41:35 | +0.6 | exit-armed — ws2Mage under 15 (14.72) | 0.186480 | +0.2782 |
| 15:41:35 | +0.6 | KICKSTART — rider ws4 (r 9.65 oob, ceiling ws12) | 0.186480 | +0.2782 |
| 15:45:00 | +4.0 | baton -> ws5 oob (r 5.38) | 0.185533 | +0.7848 |
| 15:54:00 | +13.0 | baton -> ws6 oob (r 5.90) | 0.185270 | +0.9255 |
| 15:55:05 | +14.1 | **EXIT — x-cross on ws6** | 0.185994 | **+0.5382** |

**ws4 → ws5 → ws6, two baton passes, and the ws6 x-cross is the exit.** No new mech, no new knob,
no change to `lin_hop` or the ceiling. The arm fires **35 seconds** after the open against 52.1 min
on the leg's own side.

### EVERY CANDIDATE BAR, AND WHAT IT IS WORTH

| the test | frame | first fire | +min | LONG realised | LONG MAE | SHORT realised | SHORT MAE | fires to tape end |
|---|---|---|---|---|---|---|---|---|
| ws2Mage arms the walk | d +1 | 16:33:05 | +52.1 | +1.2009 | 1.3782 | -1.2009 | 1.2424 | 978 |
| ws2Mage arms the walk | d −1 | **15:41:35** | +0.6 | -0.2782 | 0.2782 | +0.2782 | 0.0000 | 1036 |
| ws6 stall (stall_n 6) | d +1 | 15:41:05 | +0.1 | -0.0430 | 0.0430 | +0.0430 | 0.0000 | 99819 |
| ws6 stall (stall_n 6) | d −1 | 16:05:00 | +24.0 | +0.7168 | 1.3782 | **-0.7168** | 1.2424 | 97939 |
| ws6 x-cross, the walk's exit test | d +1 | 15:41:05 | +0.1 | -0.0430 | 0.0430 | +0.0430 | 0.0000 | 70269 |
| ws6 x-cross, the walk's exit test | d −1 | **15:55:05** | +14.1 | -0.5382 | 1.3782 | **+0.5382** | 0.0000 | 70633 |
| ws6x crosses ws6r | d +1 | 15:54:15 | +13.2 | -0.8358 | 1.3782 | +0.8358 | 0.0000 | 2680 |
| ws6x crosses ws6r | d −1 | 15:54:10 | +13.2 | -0.7063 | 1.3782 | +0.7063 | 0.0000 | 2681 |

- the walk exits on the FIRST fire, so the first-fire column is the only one it could ever take.
- the stall and `xcond` are **states**, not crossings, which is why they count in the tens of
  thousands of bars; `ws6x crosses ws6r` is an event and counts 2681. Nothing is truncated - the
  counts run to the tape end at 23:59:55.
- **the ws6 stall on d −1 arrives 9.9 min after the x-cross and 1.2550 worse.** On this leg the
  x-cross is the one carrying it.

| frame | 1.10 stop | +min | realised at the stop | overshoot |
|---|---|---|---|---|
| LONG, as the chain ran it | 15:50:40 | +9.7 | **-1.2981** | 0.1981 |
| SHORT, the −dr frame | 16:03:35 | +22.6 | -1.1180 | 0.0180 |

The SHORT frame's stop sits at 16:03:35, **8.5 min after the walk has already exited**, and the
SHORT's MAE to 15:55:05 is **0.0000** - the trade is never adverse for a single bar. Against the
LONG leg's -1.2981 the leg swings **+1.8363**.

### THE TWO METHODS, AND WHAT IS NOT SPECIFIED

**Method 1 — take the open's side from the tape dr.** `d = int(DRv[k])` in place of `d = -d`. At
15:41 that is −1 and the walk does everything above. Needs **no new mech and no new knob**; it is
one line. It also changes the side of every alternation open in the chain, so it is not a 15:41 fix.

**Method 2 — take the side from whichever ws2Mage arm crosses first.** Both sides' arm tests already
exist in `run_leg`. At 15:41 the −1 arm is 15:41:35 and the +1 arm is 16:33:05, a 51.5 min gap. It
uses only the walk's own mech, but the leg is open for those 35 seconds with no side set, and
**nothing in the spec says what an always-in-market chain holds in that window.** That is the gap.

**HALTED HERE.** Which frame an alternation open takes is a chain rule, not a walk rule, and it is
Joe's. Both methods are stated so either can be run; neither is applied.

### §14a — THE SAME EXIT SOURCED FROM ws4x AND ws5x

Joe 1008: *"what time does the x-cross happen if it's source from ws4x?"*

| the test | first fire | +min | pxs | SHORT realised | SHORT MAE | inside that TF's rider window? | fires to tape end |
|---|---|---|---|---|---|---|---|
| xcond(ws4) — the walk's exit test | 15:58:20 | +17.3 | 0.187330 | -0.1758 | 0.1758 | no | 68567 |
| ws4x crosses ws4r | **15:44:40** | +3.7 | 0.185699 | **+0.6963** | 0.0000 | YES | 3129 |
| ws4 stall (stall_n 6) | 15:55:10 | +14.2 | 0.186013 | +0.5282 | 0.0000 | no | 100351 |
| xcond(ws5) — the walk's exit test | 15:58:20 | +17.3 | 0.187330 | -0.1758 | 0.1758 | no | 69112 |
| ws5x crosses ws5r | **15:45:35** | +4.6 | 0.185685 | **+0.7037** | 0.0000 | YES | 2820 |
| ws5 stall (stall_n 6) | 15:59:40 | +18.7 | 0.187724 | -0.3867 | 0.4294 | no | 99642 |
| xcond(ws6) — the walk's exit test | 15:55:05 | +14.1 | 0.185994 | +0.5382 | 0.0000 | YES | 70633 |
| ws6x crosses ws6r | 15:54:10 | +13.2 | 0.185680 | +0.7063 | 0.0000 | YES | 2681 |
| ws6 stall (stall_n 6) | 16:05:00 | +24.0 | 0.188341 | -0.7168 | 1.2424 | no | 97939 |

- rider windows on the dr −1 walk: **ws4 15:41:35-15:45:00, ws5 15:45:00-15:54:00, ws6
  15:54:00-15:55:05**. The walk tests only the CURRENT rider, so a `no` is unreachable without a
  different baton rule.
- **xcond(ws4) cannot fire while ws4 is the rider.** dr −1 needs ws4x ABOVE both ws5r and ws6r. At
  the open bar ws4x 38.06 was above ws5r 26.76 and ws6r 35.93 - **true at 15:41:00** - but 35 s
  later at the KICKSTART bar ws4x had collapsed to 12.53 and it stays below both targets for the
  whole window, going as low as −18.23 at 15:43:45 against ws5r 19.57 and ws6r 32.33.
- xcond(ws4) and xcond(ws5) fire on the **same bar, 15:58:20**, 3.3 min after the walk has already
  exited, at −0.1758.
- **all three `x crosses its own r` bars land within 0.0100 of each other**: ws4 +0.6963, ws5
  +0.7037, ws6 +0.7063. All three beat the xcond(ws6) exit the walk took at +0.5382 by 0.16-0.17.
  That is **task #61** - the x-cross target sweep - and it is not proposed here.

### §14b — THE WALK IS NAKED, AND THE LANDING BAR IS A LONG ENTRY

Joe 1008: *"the purpose of the lineage walk is not to create a SHORT trade and ride it. it's sole
job in this context is to walk naked to a bar that is more optimised for the LONG trade. ie, we're
not flipping short and long"*.

- 15:41:00 is the bar the chain would have entered **LONG** on, pxs 0.187001.
- the walk runs on the dr −1 frame carrying **NO POSITION**. There is **no MAE while it walks**, and
  the 1.10 stop cannot fire on a flat book.
- the LONG is entered at whatever bar the walk lands on.
- every `SHORT realised` figure in §14 and §14a is **the entry improvement**: a LONG entered 0.5382%
  lower is 0.5382% better off at every later bar. It is not realised P&L.

| LONG entry bar | +min from 15:41 | entry pxs | entry better by % | what put the walk there | the LONG exits | hold min | why | leg MAE | leg MFE | realised |
|---|---|---|---|---|---|---|---|---|---|---|
| 15:41:00 | +0.0 | 0.187001 | +0.0000 | no walk — enter LONG immediately (the chain as built) | 15:50:40 | 9.7 | **mae breach** | 1.1000 | 0.0000 | **-1.2981** |
| 15:44:40 | +3.7 | 0.185699 | +0.6963 | ws4x crosses ws4r, inside the ws4 rider window | 16:33:10 | 48.5 | final stalled | 0.6867 | 1.9523 | **+1.9096** |
| 15:45:35 | +4.6 | 0.185685 | +0.7037 | ws5x crosses ws5r, inside the ws5 rider window | 16:33:10 | 47.6 | final stalled | 0.6793 | 1.9599 | **+1.9172** |
| 15:54:10 | +13.2 | 0.185680 | +0.7063 | ws6x crosses ws6r, inside the ws6 rider window | 16:33:10 | 39.0 | final stalled | 0.3195 | 1.9626 | **+1.9199** |
| 15:55:05 | +14.1 | 0.185994 | +0.5382 | xcond(ws6) — the walk's own exit test, what it takes | 16:33:10 | 38.1 | final stalled | **0.0000** | 1.7902 | **+1.7476** |
| 15:58:20 | +17.3 | 0.187330 | -0.1758 | xcond(ws4) and xcond(ws5), both outside their rider windows | 16:33:10 | 34.8 | final stalled | 0.4468 | 1.0647 | +1.0224 |
| 16:05:00 | +24.0 | 0.188341 | -0.7168 | ws6 stall (stall_n 6) | 16:33:10 | 28.2 | final stalled | 0.9815 | 0.4807 | +0.4798 |

- **all six landing bars exit on the same bar, 16:33:10 `final stalled`.** The LONG's own arm is
  ws2Mage crossing over 85 at 16:33:05, and the rider it kickstarts stalls on the next bar.
- **the walk's own rule - x-cross or stall, first to fire - lands 15:55:05 and the LONG makes
  +1.7476 with MAE 0.0000.** Against the -1.2981 stop that is a **+3.0457 swing on one leg.**
- **the stop never gets the chance to fire**, because nothing is open between 15:41:00 and the
  landing bar. The walk's 14.1 min of flat replaces the 9.7 min that lost 1.2981.
- `x crosses its own r` lands 0.9 min earlier at 15:54:10 and is 0.1723 better at +1.9199. Task #61.
- the two landing bars that arrive AFTER the move - 15:58:20 and 16:05:00 - still beat the stop, at
  +1.0224 and +0.4798, on a worse entry than 15:41:00 itself.
