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

- **NO PIERCE.** Joe 1007: *"the pierces aren't important to the mech"*; Joe 1008: *"I advised you
  to drop the pierce. delete it from every doc and the code"*. **A HOLD IS THE WHOLE SIGNAL** - the
  router no longer asks whether ws1x came from the other side of ws1r.
- **the hold, LONG**: ws1x sits AT OR ABOVE ws1r for `reent_xwob` 6 bars.
- **the hold, SHORT** - THE MIRROR, Joe 1008 *"apply the mirror"*: ws1x sits AT OR BELOW ws1r for
  `reent_xwob` 6 bars.
- **the branches cannot collide** - ws1x cannot be both sides of ws1r - so the chain takes whichever
  conf bar comes first. FIRST-TO-FIRE IS MINE, stated so it can be flipped.
- **conf = return + xwob - 1**, the first bar the return is knowable, and the only bar a re-entry
  can be placed on.
- **`reent_xwob` 6, not 8**: the 11:19:05 hold runs 6 bars and not 8, so 8 falls back to 11:14:30 -
  5.9 min early at 0.6697 worse. **It is its own knob since 1008** - §23. Over 95 days 6 measured
  1.5572 WORSE than 8, so this one-episode ruling is contradicted at scale and is open.

### THE TWO GATES A/B'd

| | gate |
|---|---|
| **A**, LONG | ws1r <= `momo_fence_r` 17 at the hold's first bar, AND ws12Mage > ws1Mage at conf |
| **A**, SHORT | ws1r >= 100 - `momo_fence_r` = 83 at the hold's first bar, AND ws12Mage < ws1Mage at conf |
| **B**, LONG | every Mage ws1..ws12 > 50 at conf. No ws1r fence - Joe said *"only require"* |
| **B**, SHORT | every Mage ws1..ws12 < 50 at conf |

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

---

## 15. THE NAKED LINEAGE WALK AT EVERY OPEN — THE WHOLE CHAIN, 09-25 + 09-26

Joe 1008: *"now we need to test the entire chain for 'lineage walking towards dr to optimise the
trade entry'"*, with his three rulings:

| # | the ruling, verbatim | how it is built |
|---|---|---|
| 1 | *"every open"* | the walk runs from every bar the chain would have entered on, with no exception |
| 2 | *"native, ie we don't mangle the side"* | the trade's side is untouched - the alternation for an alternation open, +1 for a re-entry open. Only the walk's FRAME comes from dr |
| 3 | *"the walk runs from the re-entry's conf bar - no lineage walk for an optimised opening"* | the ws1x hold / `reent_xwob` 6 router is untouched and still picks the conf bar; the walk starts FROM it |

- the walk's frame is `int(DRv[k])`, the tape dr at the open bar - Joe's *"towards dr"*.
- while naked there is **no MAE and no 1.10 stop**. Nothing is open, so nothing can be stopped.
- the entered leg runs the unchanged composed mech: `C.run_leg(landing, native side)`.
- the naked walk is **the lineage walk only** - arm, KICKSTART, baton, then `final stalled` or
  `x-cross`, ws12r ceiling rule live. It does not carry the >ws12 handover, which exists to exit an
  open position. MY STRUCTURAL CALL; it is the walk that produced 15:55:05 in §14b.

### THE RESULT

| arm | legs | positive | stops | re-entries | last exit | running MAE | running MFE | MFE/MAE | realised as scored | realised at -1.10 | minutes naked | entry improvement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| arm 0 — baseline, no walk | 43 | 29 | 12 | 12 | 09-26 20:09:10 | 21.4877 | 41.1325 | **1.91** | **+13.3928** | +14.2207 | 0.0 | +0.0000 |
| arm 1 — naked walk, no landing ends it | 23 | 12 | 9 | 8 | 09-26 20:40:00 | 12.2899 | 14.8420 | 1.21 | **-0.3915** | +0.1173 | **1255.6** | **-0.9054** |
| arm 2 — naked walk, no landing enters at the open | 23 | 12 | 9 | 8 | 09-26 20:40:00 | 12.2899 | 14.8420 | 1.21 | -0.3915 | +0.1173 | 1255.6 | -0.9054 |

| arm | day | legs | positive | stops | MAE | MFE | MFE/MAE | realised | minutes naked |
|---|---|---|---|---|---|---|---|---|---|
| arm 0 | 2026-09-25 | 25 | 17 | 6 | 11.8959 | 27.8113 | 2.34 | +10.0229 | 0.0 |
| arm 0 | 2026-09-26 | 18 | 12 | 6 | 9.5917 | 13.3212 | 1.39 | +3.3699 | 0.0 |
| arm 1 | 2026-09-25 | 11 | 5 | 5 | 6.8846 | 7.2865 | 1.06 | **-1.4826** | 692.0 |
| arm 1 | 2026-09-26 | 12 | 7 | 4 | 5.4053 | 7.5555 | 1.40 | +1.0911 | 563.6 |

- **the one gap the rulings left open turned out to be moot.** `dr` was **0 at 0 of 23 opens** and
  the walk **landed at 23 of 23**, so arms 1 and 2 are the same chain, figure for figure.
- **legs fall 43 -> 23** and **1255.6 min is spent flat** - 43.6% of the 2880 min in the two days.
- **the entry improvement is NEGATIVE on net, -0.9054 across 23 legs.** The walk lands on a worse
  entry more often than a better one.
- **the stop rate rises**: 9 of 23 legs (39.1%) against 12 of 43 (27.9%).
- **MFE/MAE falls 1.91 -> 1.21.**

### THE MECH DOES NOT REACH ITS OWN MOTIVATING CASE

| what | arm 0 | arm 1 |
|---|---|---|
| 15:41:00 is | an **open** - the walk in §14b runs FROM it and lands 15:55:05 at +1.7476 | a **landing** - the walk starts at 14:43:55, frame dr −1, and lands ON 15:41:00 |
| the entry at 15:41:00 | taken, stopped 15:50:40 at -1.2981 | taken, 0.5225% **worse** than 14:43:55, stopped 15:50:40 |

- **the walk at every open moves the walk one leg EARLIER than the case that motivated it.** Under
  arm 1 the leg before 15:41 is never held, so 15:41:00 arrives as a landing bar instead of an open
  bar, and the §14b gain is not available.
- §14b's +3.0457 swing needs the walk to start AT 15:41:00, which requires the leg before it to be
  held exactly as the baseline holds it.

### THE WORST AND BEST SINGLE LEGS, ARM 1

| leg | side | the walk starts | frame dr | entry bar | naked min | entry better by % | exit | why | realised contribution |
|---|---|---|---|---|---|---|---|---|---|
| 9 | LONG | 09-25 17:31:55 | −1 | 21:27:40 | **235.8** | **-3.4812** | 21:58:20 | mae breach | -1.2767 |
| 5 | LONG | 09-25 08:48:55 | +1 | 10:25:00 | 96.1 | -0.8814 | 10:56:40 | x-cross | +1.0355 |
| 6 | SHORT | 09-25 10:56:40 | +1 | 11:41:35 | 44.9 | **+3.5022** | 12:27:05 | x-cross | +1.9245 |
| 20 | LONG | 09-26 11:46:35 | +1 | 14:17:35 | 151.0 | +0.1139 | 16:07:25 | >ws12 divergence on ws1r | +2.4479 |

- leg 9 walks **235.8 min** to an entry **3.4812% worse** and then takes the stop. It is the single
  largest cost in the arm.
- leg 6 is the single largest gain and it comes from a **+3.5022% better entry** - the same
  mechanism that costs leg 9.

**HALTED.** The mech is built, run and banked as specified. Where it goes next is Joe's: the
measured fact is that *"every open"* relocates the walk one leg upstream of the case it was built
for, and the chain gives back 13.7843 of realised to do it.

---

## 16. THE INVERSION TEST — 10:56:40 AND 04:41:00, WALKED UPWARD

Joe 1008: *"my perspective on the inversion: I think code is walking a downward lineage when it
should be walking upward (to improve the entry)"* / on 10:56:40: *"this needs exactly the spec I
just laid out - it must lineage walk upward so that it does not attract mae1.1"*.

**THE FRAME RULE, PER JOE:** *"the direction of the x cross is defined by the trade"*. A downward
cross is `d > 0` in the code, so a **SHORT trade walks on frame +1** and a LONG trade on frame −1 -
**the frame is the inverse of the trade side.** Arm 1 took the frame from `int(DRv[k])` instead.

**BOTH BARS ARE SHORT AND BOTH HAVE dr +1, so at these two bars the two frame rules AGREE.** The
walk already ran on frame +1 at both. The frame rules differ on 6 of the 23 arm-1 legs, which is
still unmeasured.

### 10:56:40 — THE SPEC IS ALREADY IN THE CHAIN, AND IT IS ARM 1's BEST LEG

| ts | +min | event | pxs | pct from 10:56:40 | pct from entry |
|---|---|---|---|---|---|
| 10:56:40 | +0.0 | WALK STARTS — naked, nothing open | 0.190005 | +0.0000 | — |
| 11:06:30 | +9.8 | walk: armed — ws2Mage 88.86 crosses into oob | 0.190883 | -0.4618 | — |
| 11:06:30 | +9.8 | walk: KICKSTART — rider ws8 (r 87.91 hi oob) | 0.190883 | -0.4618 | — |
| 11:15:00 | +18.3 | walk: baton -> ws9 oob (r 93.90) | 0.193406 | -1.7899 | — |
| 11:30:00 | +33.3 | walk: baton -> ws10 oob (r 88.17) | 0.199043 | **-4.7563** | — |
| 11:41:35 | +44.9 | LANDING — x-cross on ws10 (targets ws11r 73.89, ws12r 76.02, both in-fence) | 0.196660 | -3.5022 | — |
| 11:41:35 | +44.9 | **ENTER SHORT** | 0.196660 | **-3.5022** | +0.0000 |
| 12:16:40 | +80.0 | exit-armed — ws2Mage under 15 (14.64) | 0.191439 | -0.7544 | +2.6548 |
| 12:16:40 | +80.0 | KICKSTART — rider ws7 (r 13.23 oob, ceiling ws12) | 0.191439 | -0.7544 | +2.6548 |
| 12:24:00 | +87.3 | baton -> ws8 oob (r 3.27) | 0.192052 | -1.0769 | +2.3432 |
| 12:27:00 | +90.3 | baton -> ws9 oob (r 14.25) | 0.192709 | -1.4228 | +2.0090 |
| 12:27:05 | +90.4 | **EXIT — x-cross on ws9** | 0.192875 | -1.5103 | **+1.9245** |

| ts | +min | event | pxs | pct |
|---|---|---|---|---|
| 10:56:40 | +0.0 | OPEN SHORT — the baseline, no walk | 0.190005 | +0.0000 |
| 11:07:45 | +11.1 | MAE BREACH 1.1504% over 1.10% | 0.192191 | **-1.1504** |

- **the walk rides UPWARD**: 0.190005 at the start to 0.199043 at the ws10 baton, **+4.76% of price
  against the SHORT while nothing is open.** The SHORT then enters 3.5022% higher.
- **-1.1504 becomes +1.9245, a +3.0749 swing, and the 1.10 stop never fires.**
- **10:56:40 IS THE SAME BAR IN BOTH CHAINS - the previous leg's exit - and the two chains do
  different things with it:**

| chain | what 10:56:40 is | the entry | the exit | result |
|---|---|---|---|---|
| **arm 0**, the baseline, and **§12's stop list Joe is reviewing** | the leg's OPEN bar | 10:56:40 at 0.190005 | 11:07:45 | **mae breach, -1.1504** |
| **arm 1**, §15's naked walk | leg 6's WALK START - nothing is opened | 11:41:35 at 0.196660 | 12:27:05 | x-cross, **+1.9245** |

- §12's stop table and §15's arm-1 table are both correct. 10:56:40 is a stop in the baseline and
  is not a stop in arm 1, because arm 1 never opens a position at that bar.
- **the arm is what makes it work.** With `exit-armed` REMOVED the walk lands 10:58:00 (+1.3 min)
  at an entry **0.0087% worse** and takes the same stop at 11:07:45 for **-1.1592**.

| the walk at 10:56:40 | the arm | landing | +min | entry pxs | SHORT entry better by % | what landed it |
|---|---|---|---|---|---|---|
| frame +1, Joe's | live | 11:41:35 | +44.9 | 0.196660 | **+3.5022** | x-cross on ws10 |
| frame +1, Joe's | removed | 10:58:00 | +1.3 | 0.189989 | -0.0087 | x-cross on ws6 |
| frame −1, the inverse | live | 12:27:05 | +90.4 | 0.192875 | +1.5103 | x-cross on ws9 |
| frame −1, the inverse | removed | 11:01:10 | +4.5 | 0.190074 | +0.0362 | x-cross on ws1 |

### 04:41:00 — JOE'S LADDER READ, CLAUSE BY CLAUSE

| the claim | the test | the value at 04:41:00 | holds? |
|---|---|---|---|
| ws1r is hi oob | ws1r >= 85 | **100.00** | **YES** |
| ws1x has crossed under r | ws1x < ws1r | **104.81 vs 100.00** | **no — x is OVER r** |
| ws2r is in-fence | 17 < ws2r < 83 | 70.97 | YES |
| ws3r is in-fence | 17 < ws3r < 83 | 78.84 | YES |
| the lineage stops at ws1 | neither ws2r nor ws3r oob on frame +1 | in-fence / in-fence | **YES** |
| the x-cross fires on ws1, zero bars | xcond(ws1) on frame +1 | ws1x 104.81 vs ws2r 70.97, ws3r 78.84 | **no** |

- **five of the six clauses hold.** The one that does not is the cross itself: at 04:41:00 ws1x
  **104.81** sits ABOVE ws1r 100.00, so the downward cross has not happened on that bar.
- **the 103.0 min delay is the ARM, not the frame.** `ws2Mage is 117.03 at 04:41:00` - already past
  its own 85 fence - and the arm needs a **CROSSING** into oob. ws2Mage has to leave oob and come
  back before the walk can pick any rider, which does not happen until **06:20:05, +99.1 min**.
- this is the same shape as §13's never-armed legs, from the other side: there ws2Mage was 46-85
  points SHORT of its fence; here it is already PAST it.
- **04:41:00 was never a losing leg.** The baseline exits 05:16:15 on an x-cross at **+1.0132**. The
  walk's entry is **0.6202% worse** and it realises **+0.5839** - the walk costs 0.4293 here.
- on frame +1 at 04:41 the price goes **DOWN** (0.185031 -> 0.183884) while at 10:56:40 the same
  frame goes **UP**. The frame sets which fence the r lines are tested against; it does not set the
  direction the price then takes.

**WHAT THE MEASUREMENT SAYS ABOUT THE INVERSION.** At both bars the walk already used frame +1,
which is both `dr` and the inverse of the SHORT side, so neither bar shows a frame inversion. At
10:56:40 the walk rode upward and produced exactly the asked-for outcome. At 04:41:00 the walk's
problem is the arm's CROSSING test against a line already past its fence. **The 6 legs where `dr`
and the inverse-of-side rules disagree are not yet measured** - that is where a frame inversion
could still be hiding.

---

## 17. THE FRAME RULE IMPLEMENTED — THE WHOLE CHAIN, FIVE ARMS

Joe 1008: *"you're reporting to me the thing that I just asked to be implemented, but I haven't
seen the confirmation that the work was done"*.

**THE CHANGE, one line in `_nakedchain.run_chain_naked`:**

```python
    fr = (int(DRv[k]) or d) if frame == 'dr' else -d
```

- `frame='dr'` is arms 1 and 2 as §15 ran them: the tape dr at the open bar.
- `frame='inv'` is **arms 3 and 4, Joe's rule**: `-d`, the **inverse of the trade side**. A SHORT
  trade (side −1) walks on frame +1, because *"the direction of the x cross is defined by the trade
  - it's a SHORT trade, so the cross is downward"* and a downward cross is `d > 0` in the code.
- additive: the `dr` arms are kept, not replaced.

| arm | legs | positive | stops | re-entries | last exit | running MAE | running MFE | MFE/MAE | realised as scored | realised at -1.10 | minutes naked | entry improvement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| arm 0 — baseline, no walk | 43 | 29 | 12 | 12 | 09-26 20:09:10 | 21.4877 | 41.1325 | **1.91** | **+13.3928** | +14.2207 | 0.0 | +0.0000 |
| arm 1 — frame dr, no landing ends it | 23 | 12 | 9 | 8 | 09-26 20:40:00 | 12.2899 | 14.8420 | 1.21 | -0.3915 | +0.1173 | 1255.6 | **-0.9054** |
| arm 2 — frame dr, no landing enters at the open | 23 | 12 | 9 | 8 | 09-26 20:40:00 | 12.2899 | 14.8420 | 1.21 | -0.3915 | +0.1173 | 1255.6 | -0.9054 |
| arm 3 — **frame = inverse of the side**, no landing ends it | 21 | 11 | 10 | 9 | 09-26 20:40:00 | 14.0879 | 13.2439 | 0.94 | **-2.4789** | -1.9307 | 1034.7 | **+1.3540** |
| arm 4 — frame = inverse of the side, no landing enters at the open | 21 | 11 | 10 | 9 | 09-26 20:40:00 | 14.0879 | 13.2439 | 0.94 | -2.4789 | -1.9307 | 1034.7 | +1.3540 |

| arm | day | legs | positive | stops | MAE | MFE | MFE/MAE | realised | minutes naked |
|---|---|---|---|---|---|---|---|---|---|
| arm 0 | 2026-09-25 | 25 | 17 | 6 | 11.8959 | 27.8113 | 2.34 | +10.0229 | 0.0 |
| arm 0 | 2026-09-26 | 18 | 12 | 6 | 9.5917 | 13.3212 | 1.39 | +3.3699 | 0.0 |
| arm 1 | 2026-09-25 | 11 | 5 | 5 | 6.8846 | 7.2865 | 1.06 | -1.4826 | 692.0 |
| arm 1 | 2026-09-26 | 12 | 7 | 4 | 5.4053 | 7.5555 | 1.40 | +1.0911 | 563.6 |
| arm 3 | 2026-09-25 | 10 | 5 | 5 | 6.9801 | 7.5851 | 1.09 | -1.2099 | 767.6 |
| arm 3 | 2026-09-26 | 11 | 6 | 5 | 7.1079 | 5.6589 | 0.80 | -1.2689 | 267.1 |

### THE INVERSION WAS REAL IN THE ENTRY COLUMN, AND THE FRAME RULE FIXES IT

| what moved | frame dr | frame = inverse of the side | the change |
|---|---|---|---|
| entry improvement, summed | **-0.9054** | **+1.3540** | **+2.2594** |
| realised as scored | -0.3915 | -2.4789 | **-2.0874** |
| legs | 23 | 21 | -2 |
| stops | 9 | 10 | +1 |
| MFE/MAE | 1.21 | 0.94 | -0.27 |
| minutes naked | 1255.6 | 1034.7 | -220.9 |

- **the frame rule does exactly what it was aimed at: the entries stop being net-worse and become
  net-better, by 2.2594 across the chain.**
- **realised still falls.** The entry is one of four things the walk changes - it also changes which
  bar each leg starts from, the leg count, and the time spent flat. The loss is not in the frame.
- **the legs where the two frame rules agree are identical**, including both bars Joe reviewed:
  10:56:40 is leg 6 in both arms (+3.5022 entry, exit 12:27:05) and 04:41:00 is leg 2 in both
  (-0.6202 entry, exit 06:40:30).

### THE LEGS THE FRAME RULE MOVED MOST, ARM 3

| leg | side | the walk starts | frame dr | entry bar | naked min | entry better by % | exit | why |
|---|---|---|---|---|---|---|---|---|
| 6 | SHORT | 09-25 10:56:40 | +1 | 11:41:35 | 44.9 | **+3.5022** | 12:27:05 | x-cross |
| 19 | SHORT | 09-26 14:17:35 | +1 | 15:45:15 | 87.7 | **+2.2295** | 16:25:40 | final stalled |
| 11 | LONG | 09-26 02:55:50 | −1 | 03:21:25 | 25.6 | +0.5837 | 04:10:00 | x-cross |
| 5 | LONG | 09-25 08:48:55 | −1 | 10:17:05 | 88.2 | -0.5724 | 10:56:40 | x-cross |
| 10 | LONG | 09-25 22:27:35 | −1 | 23:52:25 | 84.8 | -0.6364 | 00:37:25 | mae breach |
| 9 | LONG | 09-25 17:31:55 | −1 | 21:27:40 | **235.8** | **-3.4812** | 21:58:20 | mae breach |

- **leg 9 is the single largest cost in BOTH arms and the frame rule cannot touch it**: it is a LONG
  on a dr −1 bar, so `dr` and the inverse-of-side give the same −1. 235.8 min naked to an entry
  3.4812% worse, then the stop.
- leg 19, 09-26 14:17:35, is the gain the `dr` frame did not get: **+2.2295** on a SHORT.

---

## 18. THE ws2 OVERRIDE AND THE REVERSED LINEAGE

Joe 1008: *"we'll create a ws2 override, because `walking to a better opening` uses lineage walk in
a different way, for a different purpose / -walking to a better entry does not need ws2: ws2 was
introduced to get the trade started, to collect the big MFE / -optimising an entry carries no
aspirations for a big trade - it just needs to move an open signal that is misplaced on the board /
-waiting for ws2Mage will almost always ride over the optimal position, for 2 reasons: --1, the
signal relocations are small --2, the very purpose of `walking the lineage walk to a more optimised
location` requires the lineage to operate in reverse"*.

### THE MECH, AND THE THREE READS THAT FIX IT

| part | the rule | why this reading |
|---|---|---|
| the ws2 override | `exit-armed` is GONE. No ws2Mage gate at all. | Joe's words, verbatim |
| the rider | the **top of the unbroken oob run from ws1** on the walk's frame | not max(oob): at 04:41 max(oob) is **ws10** while Joe read **ws1** |
| the baton | **DOWNWARD** - an oob TF within `lin_hop` 2 below the rider, taken as far as it goes on the same bar. ws1 is the floor. | *"the lineage to operate in reverse"* |
| the landing | the bar the downward lineage runs out on | Joe's *"zero bars"*, stated at 04:41 and again at 17:31 |

| Joe's read | the ladder | what this mech gives |
|---|---|---|
| 04:41:00, frame +1 — *"the lineage stops at ws1 ... it walks zero bars"* | ws1r 100.00 oob, ws2r 70.97 in-fence → run is [ws1] | rider ws1, nothing below → **ZERO BARS** |
| 17:31:55, frame −1 — *"zero bars, because there is no DOWNWARD lineage after ws2r"* | ws1r 12.80 and ws2r 3.19 oob, ws3r 39.57 in-fence → run is [ws1, ws2] | rider ws2, baton down to ws1 → **ZERO BARS** |
| 15:41:00, frame −1 — the §14b case that must relocate | ws1r 26.71 in-fence → the run is **EMPTY** | no rider → **the walk WAITS** |

- **the reduction, a consequence and not a choice**: the run is contiguous FROM ws1, so ws1 is
  always in it, the baton always reaches ws1, and the lineage always runs out there. **The mech
  lands on the first bar where ws1r is oob on the walk's frame.**
- **confirmed in the run, not asserted**: `lineage exhausted below ws1` is what landed **29 of 29
  legs**. `final stalled` and `x-cross` are never reached.

### THE RESULT

| arm | legs | positive | stops | re-entries | last exit | running MAE | running MFE | MFE/MAE | realised as scored | realised at -1.10 | minutes naked | entry improvement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| arm 0 — baseline, no walk | 43 | 29 | 12 | 12 | 09-26 20:09:10 | 21.4877 | 41.1325 | **1.91** | **+13.3928** | +14.2207 | 0.0 | +0.0000 |
| arm 1 — frame dr, no landing ends it | 23 | 12 | 9 | 8 | 09-26 20:40:00 | 12.2899 | 14.8420 | 1.21 | -0.3915 | +0.1173 | 1255.6 | -0.9054 |
| arm 3 — frame = inverse of the side | 21 | 11 | 10 | 9 | 09-26 20:40:00 | 14.0879 | 13.2439 | 0.94 | -2.4789 | -1.9307 | 1034.7 | +1.3540 |
| **arm 5 — REVERSED + ws2 override, frame = inverse of the side** | **29** | **18** | **8** | 7 | 09-26 20:09:10 | 17.2674 | 21.5827 | 1.25 | **+3.2694** | +4.2699 | **528.3** | +0.0185 |
| arm 6 — REVERSED + ws2 override, frame = dr | 27 | 17 | 9 | 8 | 09-26 20:09:10 | 14.6256 | 18.9806 | 1.30 | +2.2872 | +3.2258 | 545.8 | +0.9419 |

| arm | day | legs | positive | stops | MAE | MFE | MFE/MAE | realised | minutes naked |
|---|---|---|---|---|---|---|---|---|---|
| arm 0 | 2026-09-25 | 25 | 17 | 6 | 11.8959 | 27.8113 | 2.34 | +10.0229 | 0.0 |
| arm 0 | 2026-09-26 | 18 | 12 | 6 | 9.5917 | 13.3212 | 1.39 | +3.3699 | 0.0 |
| arm 5 | 2026-09-25 | 17 | 10 | 5 | 8.8735 | 15.5640 | 1.75 | +3.3372 | 206.9 |
| arm 5 | 2026-09-26 | 12 | 8 | 3 | 8.3938 | 6.0187 | 0.72 | -0.0679 | 321.4 |
| arm 6 | 2026-09-25 | 16 | 10 | 6 | 8.3785 | 13.3970 | 1.60 | +2.5591 | 247.7 |
| arm 6 | 2026-09-26 | 11 | 7 | 3 | 6.2472 | 5.5836 | 0.89 | -0.2720 | 298.0 |

| what moved, arm 1 -> arm 5 | arm 1, forward + ws2 arm | arm 5, reversed + ws2 override | the change |
|---|---|---|---|
| realised as scored | -0.3915 | **+3.2694** | **+3.6609** |
| legs | 23 | 29 | +6 |
| stops | 9 | 8 | -1 |
| minutes naked | 1255.6 | **528.3** | **-727.3** |
| MFE/MAE | 1.21 | 1.25 | +0.04 |

- **arm 5 is the first walk arm that is positive.** It is still **-10.1234** under arm 0's +13.3928.
- **the relocations are small, as Joe said they would be**: **14 of the 29 legs land at 0.0 min**,
  and 528.3 min flat across two days against the forward walk's 1255.6.

### THE TWO BARS JOE REVIEWED, UNDER THE REVERSED WALK

| bar | arm | the walk | entry | exit | leg MAE | leg MFE | realised |
|---|---|---|---|---|---|---|---|
| 09-25 17:31:55 | arm 1, forward | 235.8 min naked, lands 21:27:40 | -3.4812 | 21:58:20 | 1.1000 | 0.0000 | **-1.2767** |
| 09-25 17:31:55 | **arm 5, reversed** | **0.0 min — ZERO BARS** | +0.0000 | 18:59:10 | **0.0000** | **3.1380** | **+1.1253** |
| 09-25 10:56:40 | arm 1, forward | 44.9 min naked, lands 11:41:35 | +3.5022 | 12:27:05 | 0.4377 | 3.9665 | **+1.9245** |
| 09-25 10:56:40 | **arm 5, reversed** | 11.3 min, lands 11:08:00 | +1.3629 | 11:23:25 | **1.1000** | 0.0000 | **-1.1000** |

- **17:31:55 is fixed exactly as Joe called it**: zero bars, and the LONG then runs to 18:59:10 on a
  >ws12 divergence with **leg MAE 0.0000 and MFE 3.1380**.
- **10:56:40 is lost.** The reversed walk relocates 11.3 min instead of 44.9, enters 1.3629% better
  instead of 3.5022%, and takes the stop at 11:23:25. The forward walk's 44.9 min was what carried
  that bar.
- that trade is the open question the reversed mech creates: **ws1r oob arrives early enough to help
  17:31 and too early to help 10:56.**

---

## 19. JOE'S TEST, THE WEAKNESS MECHANISM, AND THE TURN DETECTOR

### THE SELF-TEST, AND IT FAILS

Joe 1008: *"before you show it to me, test yourself first. the test is simple: is the pxs of the
open signal located at or near a pivot that supports my trade (eg low pxs pivot for a LONG trade)?
if yes, no lineage walk is needed, if no walk the lineage path that takes me to a better pxs (ie go
lower in pxs if the open is a LONG trade). if the lineage walk takes you to a higher pxs (ie with
the LONG trade), the lineage walk is facing the wrong direction"*.

| the outcome | legs | what it means |
|---|---|---|
| no walk — zero bars | **14** | the open signal was left alone. Cannot help or hurt. |
| moved BETTER | 7 | the walk found a better pxs. The direction was right. |
| **moved WORSE — WRONG DIRECTION** | **8** | **FAILS Joe's test.** |

- *"most open signals don't need to move"* **holds**: 14 of 29 are zero bars.
- 15 relocated; **8 of those 15 moved the wrong way.** Summed entry improvement +0.0185 - the 7 good
  moves and the 8 bad ones nearly cancel.
- **the frame is not the fault.** The opposite frame won only 6 of 15, and on legs 9, 18, 25 and 28
  the frame in use fails the test AND the opposite frame is worse still.
- the walk hit the span's best pxs on **5 of 15** legs.
- **leg 18, 09-26 00:27:10, is the cleanest failure**: the open bar already held the best pxs in the
  span and the walk moved off it anyway, landing 0.7707% worse.

### THE MECHANISM, IN JOE'S WORDS

Joe 1008: *"this is why I called out the direction of pxs - it can only go down to satisfy a LONG
entry, but a r line that doesn't reach the bottom is weak, and weak lets pxs climb"*.

And the case that showed it, Joe 1008: *"10:17 walked down to the reversl of ws1r at 10:21. at 10:21
it was infence - that's the end of the walk"*.

| 09-25 10:17:05, LONG, frame −1 | the value |
|---|---|
| ws1r minimum, 10:17:05 → 10:25:00 | **19.95 at 10:20:05** |
| the oob-low fence my landing rule waits for | 15 |
| did ws1r reach it? | **no — it turned back up 4.95 points short** |
| so the rule waited | to **10:36:05, 19.0 min past the turn** |
| the LONG entry there | **-0.5702** |
| the best LONG entry in the span | +0.1627 at 10:18:00 |
| the LONG entry at Joe's 10:21 | ≈ -0.02 |

- **the terminus is the rider's TURN, not its arrival at oob.** In-fence is what makes the turn
  terminal: a line that turns while still inside the fences has no extension left to give, and by
  Joe's mechanism that weakness is precisely what lets pxs climb back against the entry.
- the §18 landing rule - the first bar ws1r is oob on the frame - **waits for an arrival that may
  never come.** At 10:17 it came 4.95 points short and cost 19 minutes and 0.5702% of entry.

### THE TURN DETECTOR — `rrev_wob` 5 IS THE ONLY VALUE THAT REPRODUCES JOE'S 10:21

`_mage_rev(ws1r, rrev_wob 2)` as banked fires **23 turns in the 8 minutes after 10:17:05, 12 of them
UP, the first at 10:17:10** - one bar after the open. It cannot isolate the turn Joe reads.

| rrev_wob | seconds | the first UP turn after 10:17:05 | +min | LONG entry better by % | UP turns in the 8 min window |
|---|---|---|---|---|---|
| 2, as banked | 10 | 10:17:10 | +0.1 | -0.0299 | 12 |
| 4 | 20 | 10:18:50 | +1.6 | **+0.0891** | 5 |
| **5** | **25** | **10:20:30** | **+3.4** | **-0.0234** | **3** |
| 6 | 30 | 10:22:20 | +4.9 | +0.0801 | 3 |
| 11 | 55 | 10:22:45 | +5.3 | +0.0199 | 2 |
| 12 | 60 | 10:25:15 | +8.2 | -0.3732 | 1 |
| 15 | 75 | 10:43:40 | +26.6 | -1.0664 | 0 |

- **wob 5 is the only value in 2..40 that lands inside 10:20:00-10:22:00**, Joe's read. It lands
  10:20:30 and cuts the UP turns from 12 to 3.
- **wob 6 to 11 is a six-value plateau**, all landing 10:22:20-10:22:45, entry +0.0801 down to
  +0.0199. It is the widest stable band and the first POSITIVE entry.
- **wob 12 is the cliff**: the landing jumps 2.5 min and the entry falls to -0.3732, and by wob 15
  it is -1.0664.

**RULED BY JOE: `ent_rev_wob` 4.** He said *"rrev_wob 5"* and then *"sorry - typo. use 4"*. At 4 the
10:17 turn lands **10:18:50, +1.6 min, entry +0.0891** - the best LONG entry of every value in 2..40.
It is banked in `ws12_baton_config` v1 as `rev.ent_rev_wob`, owner joe. **The banked `rrev_wob` 2 is
untouched and still serves the >ws12 divergence - a second knob for a second mech.**

---

## 20. THE TURN WALK — `ent_rev_wob` 4, AND THE CHAIN

The §19 landing rule, built. No ws2Mage arm, no baton, no oob requirement: the walk watches **ws1r**
and lands on its **first TURN against the walk's travel**, by `_mage_rev(ws1r, ent_rev_wob 4)`. On
frame −1 the downward travel ends on a turn UP; on frame +1 the upward travel ends on a turn DOWN,
reusing `_chain10`'s own `WANT` convention.

| arm | legs | positive | stops | re-entries | last exit | running MAE | running MFE | MFE/MAE | realised as scored | realised at -1.10 | minutes naked | entry improvement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| arm 0 — baseline, no walk | 43 | 29 | 12 | 12 | 09-26 20:09:10 | 21.4877 | 41.1325 | **1.91** | **+13.3928** | +14.2207 | 0.0 | +0.0000 |
| arm 5 — reversed lineage + ws2 override | 29 | 18 | 8 | 7 | 09-26 20:09:10 | 17.2674 | 21.5827 | 1.25 | +3.2694 | +4.2699 | 528.3 | +0.0185 |
| arm 7 — **TURN walk, wob 4**, frame = inverse of the side | 36 | 24 | 12 | 12 | 09-26 20:09:10 | 21.3500 | 30.8514 | 1.45 | +6.9682 | +7.3850 | **46.2** | -3.3229 |
| arm 8 — **TURN walk, wob 4**, frame = dr | 39 | 28 | 11 | 11 | 09-26 20:09:10 | 22.1919 | 35.9626 | 1.62 | **+12.1798** | +12.7108 | **62.9** | -3.6620 |
| arm 7 at wob 5, for the knob comparison | 37 | 26 | 11 | 11 | 09-26 20:09:15 | 21.2774 | 32.5237 | 1.53 | +9.3419 | +9.7060 | 61.1 | -3.3787 |
| arm 8 at wob 5, for the knob comparison | 39 | 28 | 11 | 11 | 09-26 20:09:15 | 21.5190 | 35.7834 | 1.66 | +12.0026 | +12.5398 | 79.3 | -3.6223 |

### PER DAY, WHICH IS WHERE THE RESULT ACTUALLY LIVES

| arm | day | legs | positive | stops | MAE | MFE | MFE/MAE | realised | minutes naked |
|---|---|---|---|---|---|---|---|---|---|
| arm 0 | 2026-09-25 | 25 | 17 | 6 | 11.8959 | 27.8113 | 2.34 | +10.0229 | 0.0 |
| arm 0 | 2026-09-26 | 18 | 12 | 6 | 9.5917 | 13.3212 | 1.39 | +3.3699 | 0.0 |
| arm 7 | 2026-09-25 | 24 | **19** | **5** | 11.8805 | 26.1420 | 2.20 | **+11.3371** | 35.9 |
| arm 7 | 2026-09-26 | 12 | 5 | 7 | 9.4695 | 4.7094 | 0.50 | **-4.3689** | 10.3 |
| arm 8 | 2026-09-25 | 26 | **21** | **5** | 12.5112 | 29.4441 | **2.35** | **+14.1056** | 43.1 |
| arm 8 | 2026-09-26 | 13 | 7 | 6 | 9.6807 | 6.5185 | 0.67 | **-1.9258** | 19.8 |

- **arm 8 BEATS the baseline on 09-25 by +4.0827** (+14.1056 against +10.0229), with 21 of 26 legs
  positive against 17 of 25, one fewer stop, and MFE/MAE 2.35 against 2.34.
- **arm 8 LOSES 09-26 by 5.2957** (-1.9258 against +3.3699).
- **two days is not a sample.** The direction is not called here; both days are reported and the
  aggregate is the weaker number of the two readings, not a verdict.
- the relocations are now tiny: **46.2 and 62.9 minutes flat across two days**, against the forward
  walk's 1255.6. Joe: *"the signal relocations are small"*.

### THE 10:17 CASE, REPRODUCED IN THE CHAIN

| leg | side | the walk starts | frame | entry bar | naked min | entry better by % | what landed the walk | exit | why | realised |
|---|---|---|---|---|---|---|---|---|---|---|
| 10 | LONG | 09-25 10:17:05 | −1 | **10:18:50** | **1.8** | **+0.0891** | ws1r turns UP (rrev_wob 4) at r 42.56, in-fence | 10:56:40 | x-cross | +1.1427 |
| 17 | LONG | 09-25 15:41:00 | −1 | 15:46:25 | 5.4 | **+0.6912** | ws1r turns UP (rrev_wob 4) at r 66.12, in-fence | 16:33:10 | final stalled | +1.9043 |
| 11 | SHORT | 09-25 10:56:40 | +1 | 10:56:45 | 0.1 | +0.0189 | ws1r turns DOWN (rrev_wob 4) at r 56.50, in-fence | 11:07:45 | **mae breach** | -1.1000 |
| 19 | LONG | 09-25 17:32:35 | −1 | 17:34:55 | 2.3 | +0.0609 | ws1r turns UP (rrev_wob 4) at r 39.37, in-fence | 18:59:10 | >ws12 divergence | +1.7005 |

- **10:17:05 lands exactly where the knob measurement said it would**: 10:18:50, +0.0891.
- **15:41:00 is +0.6912 better on entry** and the leg makes +1.9043 against the baseline's -1.2981.
- **10:56:40 relocates only 0.1 min and still takes the stop.** The turn fires immediately there.

### THE TEST THAT STILL FAILS

**Entry improvement is still NEGATIVE on net: -3.6620 on arm 8, -3.3229 on arm 7.** By Joe's own
test the walk is still landing on the wrong side of the open pxs more often than not, and yet
realised on 09-25 now beats the baseline. Those two facts sit together and are not reconciled.

- a labelling note, not a defect: the `what landed the walk` column reports the fence state **on the
  walk's own frame**. Leg 14's *"r 97.81, in-fence"* is on frame −1, where in-fence means "not at
  the LOW fence". The same value is hi oob on frame +1.

---

## 21. 15:41 CONFIRMED, AND THE FULL WINDOW — 95 DAYS

Joe 1008: *"what happened to the 15:41 signal? it was on my stopped list and the reason I bought up
the idea of walking signals for optimisation"* / *"honestly, I'm not sure if this is a valualble
mech. after 15:41 is confirmed, let's test across the full window"*.

### 15:41 IS CONFIRMED

| | the walk | entry bar | entry better by % | exit | why | leg MAE | leg MFE | realised |
|---|---|---|---|---|---|---|---|---|
| **the turn walk, arm 8 leg 17** | 5.4 min naked | 15:46:25 | **+0.6912** | 16:33:10 | final stalled | 0.6919 | 1.9470 | **+1.9043** |
| the baseline at the same bar | none | 15:41:00 | +0.0000 | 15:50:40 | **mae breach** | 1.1000 | 0.0000 | **-1.2981** |

- **+3.2024 on the bar that started this**, and the 1.10 stop never fires.

### JOE'S NO-OP CONFLUENCE, BUILT

Joe 1008 on arm-8 leg 1: *"we could confluence that further by looking at ws1r's trajectory +
infence. in this case it's upward so the walk is immediately a no-op"*.

- the walk's travel is the frame's sign: frame −1 travels DOWN and ends on a turn UP; frame +1
  travels UP and ends on a turn DOWN.
- **no-op when ws1r's trajectory is AGAINST the travel AND ws1r is in-fence on the frame.** Both
  halves are needed; against-the-travel alone is a wiggle, and in-fence is what says no extension is
  in progress to ride. **Zero new knobs.**
- trajectory is the sign of (ws1r now − ws1r at its last step change), the same reading as §13's
  `step_dir`, so it needs no lookback window.
- **it does not cover leg 2's shape** (04:41:00, ws1r pinned at 100.00 hi oob): that leg is at the
  extreme, not in-fence, so the test never fires on it.

### THE FULL WINDOW — 2026-07-02 TO 2026-10-04, 95 DAYS, THE WHOLE CONTIGUOUS TAPE

MY READING of *"the full window"*, stated so it can be corrected: the whole tape, 1,632,960 bars at
5 s, seeded at its first bar with side +1. The chain needs no octo-sig to open, so nothing restricts
it to the 12 days carrying sanctioned rows.

| arm | legs | positive | stops | re-entries | running MAE | running MFE | MFE/MAE | realised as scored | minutes naked | entry improvement | legs not moved |
|---|---|---|---|---|---|---|---|---|---|---|---|
| arm 0 — baseline, no walk | 1542 | 914 | 501 | 501 | 954.6954 | 1036.4465 | 1.09 | **+76.3108** | 0.0 | +0.0000 | 1542 |
| **arm 8 — TURN walk, frame dr** | 1513 | 908 | **475** | 475 | 935.8284 | 1019.9250 | 1.09 | **+91.1220** | 2366.8 | -5.4948 | **63** |
| arm 9 — TURN walk, frame dr **+ Joe's confluence** | 1518 | 899 | 490 | 490 | 941.6690 | 1018.7519 | 1.08 | **+71.2483** | 948.9 | -4.9350 | **929** |
| arm 10 — TURN walk, frame = inverse of the side + confluence | 1525 | 914 | 487 | 487 | 945.4821 | 1034.7770 | 1.09 | +83.7766 | 1379.6 | -15.0313 | 725 |

| arm | days | days it BEAT the baseline | days it LOST | realised vs the baseline |
|---|---|---|---|---|
| arm 8 | 95 | **50** | 45 | **+14.8112** |
| arm 9 | 95 | 40 | **55** | **-5.0625** |
| arm 10 | 95 | 36 | 59 | +7.4658 |

### THE EDGE IS FIVE DAYS, NOT NINETY-FIVE

| the measure | arm 8 against the baseline |
|---|---|
| total over 95 days | **+14.8109** |
| days positive / negative | **50 / 45**, none equal |
| **median daily delta** | **+0.0671** |
| the best 5 days contribute | **+37.6929** |
| the worst 5 days contribute | **-29.6443** |
| **the total without the best 5 days** | **-22.8820** |

| rank | day | arm 8 − arm 0 |
|---|---|---|
| best 1 | 2026-07-06 | **+10.4569** |
| best 2 | 2026-08-27 | +8.9328 |
| best 3 | 2026-08-28 | +8.0777 |
| best 4 | 2026-09-22 | +5.1854 |
| best 5 | 2026-09-19 | +5.0401 |
| worst 1 | 2026-09-16 | **-7.9256** |
| worst 2 | 2026-08-30 | -6.2006 |
| worst 3 | 2026-09-20 | -5.4644 |
| worst 4 | 2026-09-26 | -5.2957 |
| worst 5 | 2026-08-26 | -4.7580 |

### WHAT THE 95 DAYS SAY

- **the whole +14.8112 is carried by 5 of 95 days.** Removing them leaves **-22.8820**. The median
  day is **+0.0671** - effectively zero.
- **50 of 95 days positive** is a 52.6% day rate on an n of 95.
- **arm 8 does remove 26 stops**, 475 against 501, and that is distributed rather than concentrated.
- **the version that matches Joe's design intent loses.** arm 9 leaves **929 of 1518 legs
  untouched** - his *"most open signals don't need to move"* - and comes in at **-5.0625 against the
  baseline**. arm 8 moves **1450 of 1513** legs by a median of about 1.6 min each and is the only
  arm with a positive total.
- **the entry improvement is NEGATIVE on every walk arm**: -5.4948, -4.9350, -15.0313. Joe's pxs
  test is failed across 95 days, not just across two.

**NOTHING IS RULED HERE.** Joe asked *"I'm not sure if this is a valuable mech"* and the 95-day
answer is: it is not a distributed edge, it is five days; and the shape he designed - leave most
signals alone - is the shape that loses.

---

## 22. 2026-09-22, CHAIN 0 — THE WORST STOP DAY IN SEPTEMBER OR OCTOBER

Joe 1008: *"sticking with chain 0, pick the day in september or october that has the most stops and
show them in the standard timestamped-rows event table"*.

**2026-09-22: 12 stops on 18 legs, realised -7.4220.** The next worst are 09-21 at 11 stops and
09-18 / 09-29 at 9. Across the 34 September-October days chain 0 takes **209 stops**.

| leg | side | open | exit | hold min | why | handover | leg MAE | leg MFE | realised | running MAE | running MFE | running realised |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1326 | SHORT | 00:15:15 | 00:27:20 | 12.1 | mae breach | — | 1.1000 | 0.0000 | -1.1131 | 1.1000 | 0.0000 | -1.1131 |
| 1327 | LONG | 01:00:40 | 01:05:10 | 4.5 | mae breach | — | 1.1000 | 0.0000 | -1.1653 | 2.2000 | 0.0000 | -2.2784 |
| 1328 | LONG | 04:17:10 | 04:57:30 | 40.3 | mae breach | **04:23:20** | 1.1000 | 0.0000 | -1.1111 | 3.3000 | 0.0000 | -3.3894 |
| 1329 | LONG | 05:57:55 | 06:21:15 | 23.3 | mae breach | — | 1.1000 | 0.0000 | -1.1100 | 4.4000 | 0.0000 | -4.4994 |
| 1330 | LONG | 07:21:50 | 07:55:00 | 33.2 | x-cross | — | 0.0000 | 2.0130 | **+1.4959** | 4.4000 | 2.0130 | -3.0036 |
| 1331 | SHORT | 07:55:00 | 08:26:30 | 31.5 | final stalled | — | 0.5194 | 1.7540 | **+1.6470** | 4.9194 | 3.7670 | -1.3566 |
| 1332 | LONG | 08:26:30 | 08:33:35 | 7.1 | mae breach | — | 1.1000 | 0.0000 | -1.1339 | 6.0194 | 3.7670 | -2.4905 |
| 1333 | LONG | 10:09:55 | 10:25:35 | 15.7 | mae breach | — | 1.1000 | 0.0000 | -1.1708 | 7.1194 | 3.7670 | -3.6613 |
| 1334 | LONG | 12:44:45 | 13:06:50 | 22.1 | x-cross | — | 0.0569 | 1.4395 | +0.9517 | 7.1763 | 5.2064 | -2.7096 |
| 1335 | SHORT | 13:06:50 | 14:05:10 | 58.3 | x-cross | — | 0.7480 | 1.1398 | +0.5862 | 7.9243 | 6.3462 | -2.1234 |
| 1336 | LONG | 14:05:10 | 14:15:20 | 10.2 | x-cross | — | 0.4489 | 1.0289 | +0.7601 | 8.3732 | 7.3751 | -1.3633 |
| 1337 | SHORT | 14:15:20 | 14:22:00 | 6.7 | x-cross | — | 0.0000 | 1.4134 | +0.7855 | 8.3732 | 8.7885 | -0.5778 |
| 1338 | LONG | 14:22:00 | 14:30:55 | 8.9 | mae breach | — | 1.1000 | 0.0000 | -1.1247 | 9.4732 | 8.7885 | -1.7026 |
| 1339 | LONG | 15:55:40 | 16:11:05 | 15.4 | mae breach | — | 1.1000 | 0.0000 | -1.1486 | 10.5732 | 8.7885 | -2.8511 |
| 1340 | LONG | 18:31:05 | 18:48:50 | 17.8 | mae breach | — | 1.1000 | 0.0000 | -1.1326 | 11.6732 | 8.7885 | -3.9837 |
| 1341 | LONG | 20:10:50 | 21:12:50 | 62.0 | mae breach | — | 1.1000 | 0.0000 | -1.1099 | 12.7732 | 8.7885 | -5.0936 |
| 1342 | LONG | 21:16:15 | 21:21:30 | 5.2 | mae breach | — | 1.1000 | 0.0000 | -1.2268 | 13.8732 | 8.7885 | -6.3204 |
| 1343 | LONG | 23:32:15 | 23:42:20 | 10.1 | mae breach | — | 1.1000 | 0.0000 | -1.1016 | 14.9732 | 8.7885 | **-7.4220** |

| the stop bar | re-entry conf | gap min | the ws1x return bar |
|---|---|---|---|
| 00:27:20 | 09-22 01:00:40 | 33.3 | 01:00:05 |
| 01:05:10 | 09-22 04:17:10 | **192.0** | 04:16:35 |
| 04:57:30 | 09-22 05:57:55 | 60.4 | 05:57:20 |
| 06:21:15 | 09-22 07:21:50 | 60.6 | 07:21:15 |
| 08:33:35 | 09-22 10:09:55 | 96.3 | 10:09:20 |
| 10:25:35 | 09-22 12:44:45 | 139.2 | 12:44:10 |
| 14:30:55 | 09-22 15:55:40 | 84.8 | 15:55:05 |
| 16:11:05 | 09-22 18:31:05 | 140.0 | 18:30:30 |
| 18:48:50 | 09-22 20:10:50 | 82.0 | 20:10:15 |
| 21:12:50 | 09-22 21:16:15 | **3.4** | 21:15:40 |
| 21:21:30 | 09-22 23:32:15 | 130.8 | 23:31:40 |
| 23:42:20 | 09-23 00:29:35 | 47.2 | 00:29:00 |

### WHAT THE 12 EVENT TABLES SHOW

- **11 of the 12 stops have NO WALK EVENTS AT ALL.** Only **04:17:10** arms: ws2Mage over 85 at
  04:18:30, KICKSTART rider ws12 at r 100.00, HANDOVER at 04:23:20, a 50 dip at 04:44:50 and the
  CEILING at 04:48:10 - and it still stops. **18:31:05** carries a CEILING row at +0.1 min and no
  arm. The other ten open and breach with nothing in between.
- this is §13's never-armed finding at 95-day scale, on the worst day: the stop fires before the
  mech has anything to say.
- **11 of the 12 stops are LONG.** Only 00:15:15 is SHORT. The 6 positive legs split 4 LONG / 2
  SHORT.
- **the 6 positive legs sit in two clusters**, 07:21:50-08:26:30 and 12:44:45-14:22:00, and every
  one of them exits on `x-cross` or `final stalled`. Outside those two windows the day is all stops.
- **the fastest re-entry on the day fails immediately**: the 21:12:50 stop re-enters at 21:16:15, a
  3.4 min gap, and breaches again at 21:21:30 for the day's largest overshoot, **-1.2268**.
- the 192.0 min gap after the 01:05:10 stop is the longest; the router sat out 3.2 hours.
- running MAE **14.9732** against running MFE **8.7885** - MFE/MAE **0.59** on the day, against
  1.09 over the 95.

---

## 23. THE KNOBS SEPARATED, AND WHAT OPENS THE STOPS

### THE DEFECT, FOUND IN MY OWN OUTPUT

`_chain_2day.py:31` read `XWOB = int(C.W['x_rev_xwob'])` = **8**. That knob is the x-cross that
precedes the r reversal in the **>ws12 divergence mech**, on ws1/ws2, owner mine, fitted=1. The
**re-entry router's hold** was ruled at **6** in §12 - *"xwob 6, not 8: the 11:19:05 return holds 6
bars and not 8, so xwob 8 falls back to 11:14:30 - 5.9 min early at 0.6697 worse"*. I wired one mech
to the other mech's knob, and §12 and §15 both wrote "`x_rev_xwob` 6 router", naming it at a value
it never held.

Joe 1008: *"defintely separate them"*. **`reent_xwob` 6 is now its own knob** in
`ws12_baton_config` v1, section `reentry`, owner joe. `x_rev_xwob` 8 is untouched.

### WHAT THE SEPARATION COST

| chain 0, 95 days | at the old hold 8 | at `reent_xwob` 6 | the change |
|---|---|---|---|
| legs | 1542 | **1627** | +85 |
| positive | 914 | 957 | +43 |
| stops | 501 | **533** | +32 |
| stop rate | 32.5% | 32.8% | +0.3 pt |
| running MAE | 954.6947 | 1010.1553 | +55.46 |
| running MFE | 1036.4464 | 1096.9700 | +60.52 |
| MFE/MAE | 1.09 | 1.09 | 0.00 |
| realised | **+76.3109** | **+74.7537** | **-1.5572** |
| realised per leg | +0.049488 | +0.045946 | -0.003542 |

- **6 is worse than 8 over 95 days**, by 1.5572, and it is thinner per leg. §12 chose 6 on **one
  episode** (the 11:19:05 return) where it was 0.6697 better. The 95-day reading reverses that.
- 29,688 ws1x returns exist on the whole tape at hold 6.

### JOE'S SUSPICION — "a lot of the stops in the full window are re-entry"

| how the open bar was chosen | legs | positive | stops | stop rate | MAE | MFE | MFE/MAE | realised | realised per leg |
|---|---|---|---|---|---|---|---|---|---|
| re-entry open | 533 | 299 | **181** | **34.0%** | 332.1390 | 398.3005 | **1.20** | +25.0098 | +0.046923 |
| alternation | 1093 | 657 | **352** | **32.2%** | 676.9390 | 696.3592 | 1.03 | +47.7570 | +0.043693 |
| seed | 1 | 1 | 0 | 0.0% | 1.0773 | 2.3104 | 2.14 | +1.9870 | +1.986986 |
| ALL LEGS | 1627 | 957 | 533 | 32.8% | 1010.1553 | 1096.9700 | 1.09 | +74.7537 | +0.045946 |

| how the stopped leg was opened | stops | share of all stops |
|---|---|---|
| alternation | 352 | **66.0%** |
| re-entry open | 181 | **34.0%** |

- **the suspicion does not hold.** Re-entry opens are **32.8% of legs** and **34.0% of stops** - the
  same share. Their stop RATE is 34.0% against the alternation legs' 32.2%, a 1.8 point difference.
- **re-entry opens are the BETTER half on quality**: MFE/MAE **1.20** against 1.03, and +0.046923
  realised per leg against +0.043693.
- **the stop is not a re-entry problem. It is a chain-wide problem**: roughly one leg in three
  stops regardless of how its open bar was chosen.

| the re-entry opens that stopped | value |
|---|---|
| count | 181 |
| fastest stop | **0.2 min**, 2026-08-22 18:02:55 |
| median hold to the stop | 26.7 min |
| slowest stop | 212.6 min, 2026-07-07 01:04:50 |
| stopped within 10 min | 27 of 181 (14.9%) |

| how the open bar was chosen | side | legs | stops | stop rate | realised |
|---|---|---|---|---|---|
| re-entry open | LONG | 533 | 181 | 34.0% | +25.0098 |
| alternation | LONG | 434 | 127 | **29.3%** | +17.5107 |
| alternation | SHORT | 659 | 225 | 34.1% | +30.2463 |

- **every re-entry open is LONG** - the router forces `d = +1`, which is §12's open question.
- the lowest stop rate on the board is **alternation LONG at 29.3%**; the highest are the two 34%
  buckets. A forced-LONG re-entry stops 4.7 points more often than an alternation LONG.

---

## 24. THE PIERCE DELETED, THE ROUTER MIRRORED

Joe 1008: *"I advised you to drop the pierce. delete it from every doc and the code"* / *"apply the
mirror"*.

### WHAT THE ROUTER IS NOW

| the step | LONG branch | SHORT branch |
|---|---|---|
| the pierce | **GONE** | **GONE** |
| the hold | ws1x sits **at or above** ws1r for `reent_xwob` **6** bars | ws1x sits **at or below** ws1r for 6 bars |
| conf | the hold's first bar + 5 = **25 s later**, the only bar a re-entry can be placed on | same |
| the fence, at the hold's first bar | ws1r **<= 17** (`momo_fence_r`) | ws1r **>= 83** (100 − `momo_fence_r`) |
| the Mage line, at conf | ws12Mage **>** ws1Mage | ws12Mage **<** ws1Mage |
| the open | **LONG** | **SHORT** |

- **a hold is the whole signal.** The router no longer asks whether ws1x came from the other side.
- **the branches cannot collide** - ws1x cannot be both sides of ws1r - so the chain takes whichever
  conf bar comes first. FIRST-TO-FIRE IS MINE, stated so it can be flipped.
- **the invariant is an assert, not a comment**: every hold bar must sit on the side its branch
  claims, or the run fails.
- ws1x holds on the whole tape: **29,541 one-sided -> 59,229 with both branches.**

### THE THREE STATES OF THE ROUTER, 95 DAYS, CHAIN 0

| the router | legs | positive | stops | stop rate | MAE | MFE | MFE/MAE | realised | per leg |
|---|---|---|---|---|---|---|---|---|---|
| the inverted bug, long-only, pierce required | 1627 | 957 | 533 | 32.8% | 1010.1553 | 1096.9700 | 1.09 | +74.7537 | +0.045946 |
| the spec's recovery hold, long-only, pierce required | 1755 | 1022 | 587 | 33.4% | 1097.1429 | 1162.9352 | 1.06 | +44.7233 | +0.025483 |
| **no pierce, MIRRORED** | **2201** | **1296** | **731** | **33.2%** | 1372.4413 | 1510.5120 | **1.10** | **+95.1818** | +0.043245 |

- **the mirror recovers everything the fix cost and more**: +44.7233 -> **+95.1818**, a **+50.46**
  swing, and **+20.43** above even the inverted bug's number.
- MFE/MAE **1.10**, the best of the three.
- the stop rate is unchanged at **33.2%** - the mirror adds legs, not risk per leg.

| how the open bar was chosen | side | legs | stops | stop rate | realised |
|---|---|---|---|---|---|
| re-entry open | LONG | 411 | 146 | 35.5% | +12.8508 |
| re-entry open | **SHORT** | **320** | 118 | **36.9%** | **+3.2375** |
| alternation | LONG | 708 | 212 | **29.9%** | +39.3811 |
| alternation | SHORT | 761 | 255 | 33.5% | +37.7254 |

- **the SHORT branch fires 320 times and earns +3.2375** - thin per leg, but it is 320 legs the
  router could not place before.
- re-entry opens are now **731 of 2201 legs (33.2%)** and **264 of 731 stops (36.1%)**.
- the lowest stop rate on the board is still **alternation LONG at 29.9%**; the highest is the new
  **re-entry SHORT at 36.9%**.

| the re-entry opens that stopped | value |
|---|---|
| count | 264 |
| fastest stop | 0.2 min, 2026-08-26 12:32:45 |
| median hold to the stop | 26.2 min |
| slowest stop | 195.2 min, 2026-09-11 23:49:35 |
| stopped within 10 min | 52 of 264 (19.7%) |

### WHAT WAS DELETED

- **the spec**: §12's *"the pierce: ws1x drops below ws1r. NO WOB"* bullet is replaced by **NO
  PIERCE**, carrying Joe's 1007 *"the pierces aren't important to the mech"* and his 1008 ruling.
  The gate-A and gate-B tables now carry both branches. Every *"ws1x pierce / return / `x_rev_xwob`
  6 router"* phrase is now *"ws1x hold / `reent_xwob` 6 router"* - the old phrase also named the
  wrong knob, per §23.
- **the code**: `pierce_of()` deleted from `_opens0922.py` and `_reent0922.py`, the pierce assert
  dropped from `_chain_2day.py`, and the pierce columns removed from both report tables.
- **kept on purpose**: `_pierce0810.py` and `_retest0849.py` are the 1007 measurements that led to
  the ruling. They are history, not the live mech, and the spec's file list says so.
- **also noted in §12**: `reent_xwob` 6 was chosen on ONE episode where it beat 8 by 0.6697. Over 95
  days 6 measures **1.5572 worse** than 8. That ruling is contradicted at scale and is open.

---

## 25. THE 95-DAY SWEEPS, AND THE COST COLUMN

Joe 1008: *"sweep all of the knobs we have"* / *"reducing legs is important too - the bybit fess and
slippage need to be contained if we can"* / *"agreed - combined sweep"* / *"we should have a knob for
>12 oob"* / *"ceil_trig_tf: sweep 13 and 14 as well"*.

### THE COST COLUMN, WHICH CHANGES EVERY VERDICT

| the item | value |
|---|---|
| `fee_per_leg` | **0.11 %**, Joe 1007 *"0.11 is bybit's fees"*, a round trip |
| drag | legs x 0.11, **its own column and its own total** |
| slippage | **UNSET.** Joe named it separately and it has no measured value |

- **the banked chain is net -151.9472** over 95 days: gross +78.5028 on 2095 legs against a drag of
  -230.4500. **The drag is 2.9x the gross.**
- every verdict below is on NET AFTER DRAG, and ranked on **realised per leg** where leg counts
  differ, because a total rewards a knob for simply trading more.

### WHICH KNOBS ARE LIVE

**11 of the 23** move chain 0's rows. `ceil_scope`, `oob_gate_run`, `sig_dir`, `dip_confirm`,
`div_combine`, `div_floor`, `floater_oob`, `dr_aligned`, `x_rev_xwob` and `sig_lookback_bars` are
hardcoded behaviour, OFF, or read by nothing. `sig_window_bars` is live but branch 1 is RECORDED and
not acted on, so it changes no outcome.

- **`dip_mid` is now DEAD.** All five swept values gave identical results to six decimals: the band
  Joe specified in §24 replaced the single level, and `dip_mid` 50 no longer changes an outcome.

### THE STAGED RESULT

| stage | the config | legs | stops | stop rate | MFE/MAE | gross | drag | NET |
|---|---|---|---|---|---|---|---|---|
| banked | — | 2095 | 714 | 34.1% | 1.10 | +78.5028 | -230.4500 | **-151.9472** |
| stage 1, a 36-run grid on four knobs | `mae_stop_pct` 2.5, `dip_dwell_bars` 6, `reent_xwob` 18, `lin_hop` 2 | 1647 | 203 | 12.3% | 0.93 | +155.5627 | -181.1700 | **-25.6073** |
| stage 2, every remaining knob against it | + `ceil_trig_tf` 8 | 1578 | 194 | 12.3% | 0.94 | +164.0113 | -173.5800 | **-9.5687** |
| stage 3, composing stage 2's improvers | + `momo_fence_r` 20.0, `rrev_wob` 1, `stall_n` 4, `div_lines` ws1r,ws2r,ws3r | 1636 | 205 | 12.5% | 0.92 | **+184.0227** | -179.9600 | **+4.0627** |

- **banked -151.9472 -> +4.0627, a +156.01 swing**, on 1636 legs against 2095 and a stop rate of
  **12.5%** against 34.1%.
- **49 won / 46 lost** on days. Barely distributed, and seven knobs are fitted to 95 days with
  **no hold-out**.
- MFE/MAE falls **1.10 -> 0.92**: the config holds losers longer relative to winners, which is what
  a 2.5 stop does.

### `oob_gate_fence` — THE NEW KNOB, AND THE ONLY ONE THAT CROSSED ZERO ALONE

Joe 1008: *"we should have a knob for >12 oob"*. The 72-bar gate, the branch-1 window and the
ceiling trigger were all borrowing the GLOBAL oob 15/85 out of `lazy_g` - the same shape as
`reent_xwob` borrowing `x_rev_xwob`. `oob_gate_fence` 15.0 reproduces the old behaviour exactly.

| value | the ws12r test | legs | stops | MFE/MAE | gross | drag | NET | days won / lost |
|---|---|---|---|---|---|---|---|---|
| 5 | r <= 5 or r >= 95 | 1714 | 203 | 0.93 | +161.4671 | -188.5400 | -27.0729 | 45 / 39 |
| **10** | **r <= 10 or r >= 90** | 1631 | 194 | 0.95 | **+182.4522** | -179.4100 | **+3.0422** | **36 / 30** |
| 15, banked | r <= 15 or r >= 85 | 1578 | 194 | 0.94 | +164.0113 | -173.5800 | -9.5687 | — |
| 20 | r <= 20 or r >= 80 | 1511 | 192 | 0.93 | +136.9109 | -166.2100 | -29.2991 | 34 / 43 |
| 40 | r <= 40 or r >= 60 | 1271 | 175 | 1.01 | +112.6336 | -139.8100 | -27.1764 | 44 / 51 |

- a single peak at **10**, and it was the first positive number in the whole sweep.

### `ceil_trig_tf` — ws13 AND ws14 ARE THE WORST VALUES ON THE BOARD

| the trigger line | at fence 15, NET | at fence 10, NET | handovers at fence 15 |
|---|---|---|---|
| ws8r | **+4.0627** | -16.5204 | **177** |
| ws10r | -13.7984 | **+1.0142** | 129 |
| ws11r | -17.3932 | -7.9155 | 120 |
| ws12r, banked | -15.2756 | -35.4603 | 106 |
| **ws13r** | **-41.4109** | -49.2631 | 97 |
| **ws14r** | **-84.4694** | -66.5088 | 105 |
| ws15r | -47.4608 | -47.6320 | 107 |
| ws20r | -64.7262 | -35.9128 | 124 |

- **ws14r at fence 15 is the worst row anywhere**: gross +102.5306, MFE/MAE 0.86, net -84.4694.
- **the fence and the TF trade against each other.** Tightening the fence from 15 to 10 moves the
  best trigger UP from ws8 to ws10. They are not additive.
- **the gross tracks the HANDOVER count, not the leg count** - legs sit between 1636 and 1777 across
  the whole table while handovers run 49 to 177.
- **`ceil_trig_tf` 8 is an INTERACTION, not a standalone improvement.** At the banked config ws12 is
  the best trigger and ws8 is 0.005012 per leg worse; ws8 only wins once `mae_stop_pct` is 2.5 and
  `reent_xwob` is 18.
- **the mech's name no longer describes it.** `ceil_trig_tf` 8 puts BOTH the handover gate and the
  ceiling trigger on **ws8r**, while the base ceiling stays ws12 and the extended one ws23. What the
  ">ws12 oob mech" is called now is Joe's to say.

### `mae_stop_pct` 2.5 IS A REAL PEAK, NOT A GRID EDGE

| value | legs | stops | stop rate | MFE/MAE | gross | NET | vs 2.5 | days won / lost |
|---|---|---|---|---|---|---|---|---|
| **2.5** | 1636 | 205 | 12.5% | 0.92 | **+184.0227** | **+4.0627** | — | — |
| 2.75 | 1596 | 184 | 11.5% | 0.89 | +157.1483 | -18.4117 | -22.4744 | **22 / 62** |
| 3.0 | 1562 | 164 | 10.5% | 0.86 | +124.9896 | -46.8304 | -50.8931 | 30 / 55 |
| 4.0 | 1494 | 97 | 6.5% | 0.81 | +123.9698 | -40.3702 | -44.4329 | 37 / 49 |
| 5.0 | 1446 | 56 | 3.9% | 0.76 | +94.8930 | -64.1670 | -68.2297 | 32 / 53 |

- 2.5 and 1.8 were the top of the original grid and both won, so the edge was extended. **2.5 holds
  and 2.75 loses 62 days to 22.**

---

## 26. THE HOLD-OUT — THE DIRECTION HOLDS, THE MAGNITUDE IS ONE THIRD OF THE TAPE

I raised the no-hold-out problem myself in §25 and Joe handed me the con for nine hours, so this is
the first thing built with it. Every knob in §25 was fitted to the same 95 days that scored it.

**THREE SPLITS, because one split is a choice and three is a measurement.** The chain is NOT
restarted per block - it runs once over the whole tape and each leg is attributed to the block its
OPEN bar falls in, Joe's *"day is the block unit"*. Restarting would seed a different chain in each
block and the two would not be comparable.

| the block | days | banked NET | best NET | the delta | delta per leg | days best won / lost | verdict |
|---|---|---|---|---|---|---|---|
| ALL 95 DAYS | 95 | -151.9472 | **+4.0627** | +156.0100 | +0.075012 | 49 / 46 | best wins |
| HALVES — fit, days 1-47 | 47 | -58.4806 | -32.6645 | +25.8161 | +0.020286 | 21 / 26 | best wins |
| **HALVES — hold, days 48-95** | 48 | -93.4666 | **+36.7273** | **+130.1939** | **+0.124312** | **28 / 20** | best wins |
| INTERLEAVE — fit, odd days | 48 | -48.4812 | **+15.7299** | +64.2111 | +0.066068 | 26 / 22 | best wins |
| INTERLEAVE — hold, even days | 47 | -103.4661 | -11.6672 | +91.7989 | +0.082966 | 23 / 24 | best wins |
| **THIRDS — first** | 31 | -32.8155 | **-38.4333** | **-5.6178** | **-0.021632** | **12 / 19** | **BANKED WINS** |
| **THIRDS — middle** | 32 | -48.6396 | **+73.3737** | **+122.0133** | **+0.195327** | 19 / 13 | best wins |
| THIRDS — last | 32 | -70.4922 | -30.8777 | +39.6145 | +0.037733 | 18 / 14 | best wins |

### WHAT IT SAYS

- **the direction holds out of sample: 7 of 8 blocks.** The §25 config beats the banked one almost
  everywhere, including on days that were never used to pick anything.
- **the honest forward test is the best block.** Days 48-95 were not used to choose a single knob,
  and there the delta is **+130.1939** and the config is **net +36.7273** - the only large positive
  on the board, at 28 days won to 20.
- **the magnitude is one third of the tape.** The middle third alone carries **+122.0133 of the
  +156.0100**, 78% of the whole improvement from 32 of 95 days, at **+0.195327 per leg** against
  +0.075012 overall.
- **the first third is the one loss**: -38.4333 against the banked -32.8155, 12 days won to 19.
- **only 3 of the 8 blocks are net POSITIVE for the config at all** - halves-hold, interleave-fit
  and thirds-middle. Five are still net negative after drag.
- the stop rate is the most stable thing in the table: **8.3% to 16.4%** across every block against
  the banked 26.3% to 40.5%.

**THE READING, and it is not a flattering one:** this is the shape of a config that is **right about
direction and overfit on magnitude**. The 2.5 stop and the ws8 trigger genuinely reduce stops
everywhere; the claim that the chain clears fees rests on 32 days.

---

## 27. THE OVERNIGHT RUN — THE CENTROID, THE WORST STOP DAY, AND THE LEGS THAT NEED THE BIG STOP

Joe 1008: *"when you have a centroid, make very granular steps (eg 1, 0.05) around each knob to lock
it in. in the morning I'll want to see the day with the most stops, and the five day window which
holds the trades that need such a large stop loss"* / *"you've got 9 hours from now ... be thorough,
the time is yours and so is the con"*.

### `mae_stop_pct` 2.5 AND `reent_xwob` 18 WERE GRID EDGES. BOTH HOLD.

| knob | the extension | result |
|---|---|---|
| `mae_stop_pct` | 2.5 / 2.75 / 3.0 / 3.25 / 3.5 / 4.0 / 5.0 | **2.5 is a real peak.** 2.75 loses **62 days to 22**; 5.0 is net -64.17 |
| `reent_xwob` | 18 / 22 / 26 / 32 / 40 / 60 | 18 holds |

### THE GRANULAR PASS, AND WHY THE CENTROID DOES NOT COMPOSE

| knob | the staged best | its own granular best | its granular net |
|---|---|---|---|
| `oob_gate_fence` | 15.0 | **18.0** | **+34.2129** |
| `oob_gate_bars` | 72 | **48** | **+26.7289** |
| `ceil_trig_tf` | 8 | **5** | — |
| `dip_dwell_bars` | 6 | **8** | — |
| `dip_fence` | 53.0 | **51.0** | — |
| `mae_stop_pct`, `reent_xwob`, `lin_hop`, `stall_n`, `rrev_wob`, `momo_fence_r`, `ceil_hi`, `div_lines` | — | unchanged | — |

- `oob_gate_fence` **16 / 17 / 18** is a **three-value plateau** at +34.17 / +33.56 / +34.21 with gross
  +209 to +211 - the widest stable band found anywhere, and **+30.15 above the 15.0 in use**.

| | legs | stops | stop rate | MFE/MAE | gross | drag | NET |
|---|---|---|---|---|---|---|---|
| the staged winner | 1636 | 205 | 12.5% | 0.92 | +184.0227 | -179.9600 | **+4.0627** |
| **the composed centroid** | **441** | 119 | 27.0% | 1.09 | +19.2124 | -48.5100 | **-29.2976** |

- **five knobs each improved alone and together they collapse the chain to 441 legs** - it runs out
  of re-entries and ends early. The script locked the staged winner for the two reports.
- **a one-at-a-time sweep cannot be added up.** That is now measured twice: §25 stage 2 -> stage 3,
  and here.

### THE DAY WITH THE MOST STOPS: 2026-08-22, AND IT IS PROFITABLE

| day | legs | stops | stop rate | realised |
|---|---|---|---|---|
| **2026-08-22** | 28 | **9** | 32.1% | **+14.7836** |
| 2026-08-25 | 23 | 6 | 26.1% | -2.4229 |
| 2026-09-21 | 22 | 6 | 27.3% | -4.3027 |
| 2026-09-29 | 20 | 6 | 30.0% | -5.7528 |
| 2026-08-21 | 21 | 5 | 23.8% | +5.8976 |

- **the worst stop day of the 95 is one of the better days for realised.** 9 stops cost it roughly
  23 and one leg - the 04:44:20 SHORT - returned **+12.6290** on its own.
- **every stop on that day overshot 2.5**: measured MAE 2.5216, 2.6045, 2.6134, 2.6220, 2.6850 and
  **3.3446**. The stop bounds the trigger, not the fill, and the worst overshoot is **0.84**.

### THE LEGS THAT NEED THE LARGE STOP — AND AS A GROUP THEY LOSE

A leg NEEDS the big stop when its own measured MAE went past the old 1.10 and it still came home,
so a 1.10 stop would have killed it and the 2.50 stop kept it.

| the measure | value |
|---|---|
| legs that need the large stop | **331** |
| their share of all legs | **20.2% of 1636** |
| **their summed realised** | **-22.6437** |
| the whole chain's realised | +184.0227 |
| their share of the gross | **-12.3%** |
| their largest measured MAE | 2.4994 |
| their median measured MAE | 1.5388 |

- **the 2.5 stop's gain is NOT that it rescues winners.** The 331 legs it keeps alive lose **-22.64**
  between them - about **-0.068 each**.
- **the gain is that they are not charged 1.10 each.** -0.068 against -1.10 per leg across 331 legs
  is where the stop's whole edge comes from, and it is an arithmetic saving, not a selection skill.

| the five-day window | legs needing it | their realised | the window's whole realised | their share |
|---|---|---|---|---|
| **2026-08-18 to 2026-08-22** | 22 | **+33.3997** | +43.2294 | **77.3%** |
| 2026-08-20 to 2026-08-24 | 22 | +32.0486 | +58.5487 | 54.7% |
| 2026-08-19 to 2026-08-23 | 21 | +31.6591 | +51.7894 | 61.1% |
| 2026-08-21 to 2026-08-25 | 22 | +26.3258 | +47.8826 | 55.0% |
| 2026-08-22 to 2026-08-26 | 23 | +25.9577 | +47.6996 | 54.4% |

- **2026-08-18 to 2026-08-22 is the window Joe asked for**: 22 legs needing the big stop carry
  **77.3%** of everything the window made.
- its biggest two are a **315.6 min** SHORT from 08-19 21:36:35 at MAE 2.2327 -> **+5.1510**, and a
  **477.3 min** LONG from 08-20 02:52:10 at MAE 2.2579 -> **+3.8320**. Both exit on the >ws12
  divergence and both would have been stopped twice over at 1.10.
- **across the whole tape these legs lose; inside this window they ARE the profit.** Every window in
  the top five sits in the same 11 days of August.

---

## 28. THE REFIT — 97 CONFIGS, CHOSEN ON DAYS 1-47, SCORED ON 48-95

§26 scored the already-fitted config on a hold block, which is the weak form of the test: the config
had already seen all 95 days. This is the strong form. **97 configs ran over the whole tape with
their per-day realised kept, and only days 1-47 were allowed to choose.**

### DOES THE SEARCH GENERALISE?

| the question | the answer |
|---|---|
| configs | 97 |
| **Spearman rank correlation, fit vs hold** | **+0.195** |
| the fit winner's rank on hold | **33 of 97** |
| the hold winner's rank on fit | 12 of 97 |
| the fit winner's NET on hold | **+4.3757** |
| the best possible NET on hold | +49.9777 |
| the banked control's NET on hold | **-93.4667** |
| **what choosing on fit bought, on hold** | **+97.8424** |
| what perfect hindsight would have bought | +143.4444 |
| **configs beating the banked control on hold** | **89 of 97 (92%)** |

### WHICH KNOBS SURVIVE THE SPLIT

| knob | fit-best | hold-best | verdict | the hold-best's mean hold NET |
|---|---|---|---|---|
| `mae_stop_pct` | **2.5** | **2.5** | **AGREE** | **+8.0894** - the only positive mean of any value of any knob |
| `reent_xwob` | **18** | **18** | **AGREE** | -11.4498 |
| `oob_gate_fence` | **15.0** | **15.0** | **AGREE** | -26.0345 |
| `ceil_trig_tf` | 8 | **12** | **DISAGREE** | -21.3633 against ws8's -32.9772 |
| `stall_n` | 6 | **4** | **DISAGREE** | -7.5925 against 6's -46.7480 |
| `rrev_wob` | 2 | **1** | **DISAGREE** | -24.2735 against 2's -30.0669 |

### WHAT IT SAYS, AND IT IS THE FINDING OF THE NIGHT

- **the gain is from LEAVING 1.1, not from finding a good config.** 92% of the grid beats the banked
  control on the hold block, and `mae_stop_pct` 2.5 is the only value of any knob with a positive
  mean hold net. The +97.84 is a floor effect.
- **`ceil_trig_tf` 12 - Joe's original - wins on the hold half.** ws8 wins only on fit. §25 already
  flagged ws8 as *"an INTERACTION, not a standalone improvement"*; the split confirms it. The
  ">ws12 oob mech" keeps its name.
- **3 of 6 knobs reverse across the split.** `ceil_trig_tf`, `stall_n` and `rrev_wob` each pick the
  opposite value on the two halves, so none of the three has a measured value yet - only a measured
  uncertainty.
- **Spearman +0.195.** The search is better than a coin flip and not much better. Fit's rank 1 is
  hold's rank 33, and hold's rank 1 was only fit's rank 12.
- the one structural result that is stable everywhere: **the stop rate.** Every config in the grid
  runs 8% to 16% where the banked one runs 26% to 40%.

---

## 29. WHAT ACTUALLY SURVIVES — TWO KNOB CHANGES

The §28 split left three knobs winning on both halves: `mae_stop_pct` 2.5, `reent_xwob` 18 and
`oob_gate_fence` 15.0. **The third is already the banked value**, so the whole surviving result is
**two changes**.

| config | the changes from banked | ALL 95 NET | fit 1-47 | **hold 48-95** | third 1 | third 2 | third 3 |
|---|---|---|---|---|---|---|---|
| **A** banked | — | **-151.9469** | -58.4802 | **-93.4667** | -32.8152 | -48.6394 | -70.4923 |
| **B** | `mae_stop_pct` 2.5 | -48.6437 | -28.3490 | -20.2947 | -22.0793 | **+29.7219** | -56.2863 |
| **C** | + `reent_xwob` 18 — **the survivors** | **-25.6072** | -36.6819 | **+11.0747** | -29.3109 | **+30.5678** | -26.8641 |
| **D** | the §25 seven-knob winner | **+4.0625** | -32.6649 | **+36.7274** | -38.4336 | **+73.3738** | -30.8777 |
| **E** | C + `dip_fence` 50.5 | -88.4127 | -48.2719 | -40.1408 | -23.9787 | -0.4353 | -63.9987 |
| **F** | C + `oob_gate_fence` 18.0 | -39.7805 | -38.6160 | -1.1645 | -27.3146 | +27.9305 | -40.3964 |

### THE FIVE READS

- **ONE KNOB CARRIES TWO THIRDS OF IT.** `mae_stop_pct` 1.1 -> 2.5 alone moves net **+103.30** of the
  +156.01. The other six knobs in §25's winner are worth +52.71 between them.
- **C is the defensible config.** Two changes, both knobs that won on BOTH halves, and it is the
  only configuration here whose every component passed an out-of-sample test. Hold **+11.0747**.
- **D's hold score is contaminated and must not be quoted as out-of-sample.** D was chosen using all
  95 days, hold block included. The §28 refit's genuinely blind winner scored **+4.3757** on hold,
  not +36.73.
- **`oob_gate_fence` 18.0 does not survive.** It measured +34.21 in the granular pass at D's config
  and is **14.17 WORSE than C** once the other knobs return to banked. An interaction, not a value -
  the third one found tonight.
- **nothing is positive outside the middle third.** Every positive number in the table is third 2.
  Thirds 1 and 3 are negative for all six configs, banked included.

### WHAT I WOULD PUT IN FRONT OF JOE

**Two knob changes, and no more:**

| knob | banked | proposed | why it is the only pair I will defend |
|---|---|---|---|
| `mae_stop_pct` | 1.1 | **2.5** | wins on fit AND hold; the only value of any knob with a positive mean hold net (+8.0894); 2.75 loses 62 days to 22 so it is a real peak, not an edge |
| `reent_xwob` | 6 | **18** | wins on fit AND hold; the curve is flat 2-12 and steps up only at 18 |

- that pair takes the chain from **-151.9469 to -25.6072** over 95 days and from **-93.4667 to
  +11.0747** on the hold half.
- **it is still net negative over the full tape.** Two changes do not make this chain pay for its
  fees, and nothing measured tonight does so out of sample.
- the stop rate falls **34.1% -> 12.3%**, and that is the only structural result stable across every
  block and every config tested.

---

## 30. THE r AND Mage LINE SPECS — JOE'S ARE CONFIRMED

Joe 1008: *"if you want to sweep the Mage and r configs, go for it"*.

**THE LIVE SPECS, read from `mech_lines(db, 'wsf')` and not from literals:**

| role | spec | what it is |
|---|---|---|
| `r` | `('k', 5, 8, 7, 'close')` | a stochastic-K, rsi 5, stc 8, k_len 7 |
| `Mage` | `('bb', 38, 0.93, 'close')` | Bollinger %B, length 38, mult 0.93 |

**21 variants built and scored**, one knob at a time around each live spec: r at rsi 3/4/6/8, stc
5/6/10/14 and k_len 4/5/9/12; Mage at length 24/30/48/60 and mult 0.85/0.90/1.00/1.10. 420 line
files, built in 6 minutes, then 22 chain runs in parallel across the 16 cores.

### THE WHOLE-TAPE RESULT

| line | variants beating LIVE on net | variants beating it in all three thirds |
|---|---|---|
| `r` | **1 of 12** - stc=10, +12.09 against +4.06 | **0 of 12** |
| `Mage` | **1 of 8** - len=60, +15.46 against +4.06 | **0 of 8** |

### THE SPLIT KILLS BOTH

| line | variant | fit NET | hold NET | hold net per leg | hold legs | hold stop rate |
|---|---|---|---|---|---|---|
| `r` | **LIVE** | -32.6649 | **+36.7274** | +0.043107 | 852 | 16.4% |
| `r` | stc=10 | -14.5711 | **+26.6570** | +0.029784 | 895 | 16.4% |
| `Mage` | **LIVE** | -32.6649 | **+36.7274** | +0.043107 | 852 | 16.4% |
| `Mage` | len=60 | -21.5571 | **+37.0138** | **+0.059412** | **623** | 20.4% |

- **`r` stc=10 was a fit-half artefact.** It gains +18.09 on fit and gives back **10.07** on hold.
- **`Mage` len=60 is a dead heat**: +0.2864 of hold net on **27% fewer legs** and a better per-leg
  number, against a worse stop rate. +0.29 over 48 days is noise.
- **Joe's r and Mage specs are confirmed at or above every variant measured, out of sample.** This
  is the one place tonight where the banked value is simply right.

### A DEFECT OF MINE, CAUGHT BY ITS OWN CONTROL ROW

The first run of this sweep built all 421 lines through `build_wsf_role_lines`, which inherits
`build_ws_lines`' `END_MS` at **2026-09-30**, while `score39` keys on `LG_TAPE_END` at
**2026-10-05**. The cache key is `md5(end|hours|warmup|spec)`, so the same spec at a different
window is a **different file**:

| | ws1r cache key |
|---|---|
| score39, end 1791158400000 | `dedc3afc8c29d63937f0` |
| the builder, end 1790726400000 | `5ee41b83d3a29ce1a33d` |

Every file was a real, correctly built r line. None was the line the chain reads. Right shape, right
length, plausible values, no exception - **the sweep's LIVE control row scored -113.3843 where the
identical config scores +4.0627, and that is the only signal that existed.** The builder's own
docstring names the hazard and exposes `WSF_TAPE_END` for it.

`_buildlines.py` now **asserts** the LIVE key equals score39's at import, with both windows in the
message. The first 22 results are kept as `lines_WRONGWINDOW.jsonl` and are not comparable to
anything.

---

## 31. THE x LINE — THE MOST RESPONSIVE, AND STILL NOTHING SURVIVES BOTH HALVES

The x line had never been swept. It drives the lineage walk's x-cross exit (`xcond`, `xund`) AND the
re-entry router's hold, so both the exit and the open move with it.

**THIS IS NOT TASK #61.** That is the x-cross TARGET - x X r against x X m against
x X Mage / b / boundary - and it stays untouched. This is the x LINE's own spec,
`('bb', 5, 0.35, 'close')`: Bollinger %B, length 5, mult 0.35.

| the spec | variant | legs | stops | stop rate | MFE/MAE | ALL 95 NET | fit NET | hold NET | hold net per leg | beats LIVE on hold? |
|---|---|---|---|---|---|---|---|---|---|---|
| `('bb', 4, 0.35)` | len=4 | 1677 | 214 | 12.8% | 0.911 | **+18.8572** | -45.7403 | **+64.5975** | +0.073323 | **YES** |
| `('bb', 5, 0.20)` | mult=0.20 | 1600 | 200 | 12.5% | 0.933 | **+16.7596** | **-5.2174** | +21.9770 | +0.026607 | no |
| `('bb', 5, 0.28)` | mult=0.28 | 1607 | 201 | 12.5% | 0.920 | +4.5622 | -16.8146 | +21.3768 | +0.025786 | no |
| `('bb', 5, 0.35)` | **LIVE** | 1636 | 205 | 12.5% | 0.915 | +4.0625 | -32.6649 | +36.7274 | +0.043107 | — |
| `('bb', 7, 0.35)` | len=7 | 1557 | 190 | 12.2% | 0.930 | +1.8059 | **-3.3889** | +5.1948 | +0.006429 | no |
| `('bb', 5, 0.45)` | mult=0.45 | 1669 | 213 | 12.8% | 0.905 | +0.9413 | -47.6245 | **+48.5658** | +0.055631 | **YES** |
| `('bb', 3, 0.35)` | len=3 | 1701 | 225 | 13.2% | 0.867 | -5.6434 | -59.8860 | **+54.2426** | +0.061153 | **YES** |
| `('bb', 5, 0.60)` | mult=0.60 | 1692 | 222 | 13.1% | 0.884 | -19.9670 | -64.9414 | **+44.9744** | +0.050195 | **YES** |
| `('bb', 9, 0.35)` | len=9 | 1390 | 171 | 12.3% | 0.921 | -44.1399 | -23.0848 | -21.0551 | -0.030383 | no |
| `('bb', 12, 0.35)` | len=12 | 1049 | 131 | 12.5% | 0.887 | -80.5114 | -33.7644 | -46.7470 | -0.099462 | no |

- the control passes: LIVE **+4.0627**.
- **4 of 9 beat LIVE on the hold block** - len=4 by **+27.87** - and **4 of 9 beat it on the fit
  block**. **The two sets are DISJOINT. Nothing beats LIVE on both halves.**
- `x` len=4 is the largest single hold-block improvement found anywhere tonight, and it is
  **13.08 worse on fit**. The mirror image of `r` stc=10.

### A HYPOTHESIS OF MINE, TESTED AND WRONG

I thought the fit/hold split was a leg-count effect - that fit rewards fewer legs and hold rewards
more. **Measured across all 32 line variants it is not:**

| the question | the answer |
|---|---|
| variants | 32 |
| **Pearson r, legs vs (hold gross - fit gross)** | **-0.038** |
| Pearson r, legs vs fit gross | +0.261 |
| Pearson r, legs vs hold gross | +0.068 |

### WHAT THE 32 VARIANTS DO SAY

- **hold gross beats fit gross for 29 of the 32**, from +1.59 to +122.16. The four exceptions are
  all at a grid extreme: `x` len=12, `r` rsi=8, `Mage` len=30 and `Mage` len=24.
- **the hold half is simply a better half for this chain, nearly regardless of spec.** LIVE's own
  hold-minus-fit gap is **+76.87**, mid-pack among 32.
- so the variants that "beat LIVE on hold" are the ones that AMPLIFY a regime difference, not the
  ones with a better mech. `x` len=3 has the largest gap at **+122.16** and the worst MFE/MAE at
  0.867.
- across r, Mage and x - **32 variants, 29 of them changes - not one beats the live spec on both
  halves.** Every one of Joe's three line specs stands.

---

## 32. THE THREE ONE-DAY DECISIONS, RE-MEASURED OVER 95 DAYS

Three banked decisions each rested on a single episode. All three are now measured over the whole
tape, held at §29's two surviving knobs - `mae_stop_pct` 2.5 and `reent_xwob` 18, everything else
banked - because that is the config I would actually defend.

| the arm | ALL 95 NET | fit NET | hold NET | MFE/MAE | legs | stops | stop rate |
|---|---|---|---|---|---|---|---|
| **A** gate A, pass `oob`, x-cross live — **banked** | -25.6072 | -36.6819 | **+11.0747** | 0.93 | 1647 | 203 | 12.3% |
| **B** gate B instead of A | -33.9760 | -46.1661 | +12.1901 | 0.96 | 1759 | 213 | 12.1% |
| **C** baton pass `stalled` instead of `oob` | **-59.7962** | -45.9743 | -13.8219 | **0.82** | 1671 | 215 | 12.9% |
| **D** stall-only exit, x-cross **OFF** | **-4.0151** | **-0.7897** | -3.2254 | **1.06** | **1404** | 166 | 11.8% |

| the decision | what chose it | the 95-day verdict |
|---|---|---|
| gate A vs gate B | §12, **2 days**: +13.3928 against +9.2482 | **CONFIRMED.** A beats B by 8.37 |
| the baton pass, `oob` vs `stalled` | §15 swap 2, **1 day**: -4.6905 for stalled. Joe's tag ruling put `oob` in | **CONFIRMED, strongly.** `oob` beats `stalled` by **34.19**, and `stalled` carries the worst MFE/MAE measured anywhere tonight at 0.82 |
| the walk's exit, x-cross vs stall-only | §15 swap 1, **1 leg**: +0.6115 for stall-only on 08:10. §14 measured the OPPOSITE on 15:41 by 1.2550 | **REVERSED.** Stall-only is **+21.59** better |

### WHY D IS THE ROBUST ONE AND NOT JUST THE BIGGEST

- **it is the only arm consistent across both halves**: -0.7897 on fit and -3.2254 on hold. A swings
  from -36.68 to +11.07, which is the pattern every other result tonight has shown.
- **MFE/MAE 1.06, the best number of any config measured tonight**, against A's 0.93. Turning the
  x-cross off stops cutting winners short.
- **243 fewer legs** - 1404 against 1647 - so **-26.73 of drag** disappears with it.
- the exit mix shows the mechanism: the x-cross's **961** exits are replaced by **1019 `final
  stalled` + 185 ws1r divergences**, so switching it off lets the >ws12 divergence fire **twice as
  often, 89 -> 185**. The x-cross was pre-empting the mech that was built to take those exits.

| the arm | exits by kind |
|---|---|
| A, banked | x-cross 961, final stalled 384, mae breach 203, >ws12 ws1r 89, >ws12 ws2r 10 |
| **D, stall-only** | **final stalled 1019, >ws12 ws1r 185, mae breach 166, >ws12 ws2r 34** |
| C, pass stalled | final stalled 1000, x-cross 374, mae breach 215, >ws12 ws1r 73, >ws12 ws2r 9 |
| B, gate B | x-cross 1034, final stalled 378, mae breach 213, >ws12 ws1r 119, >ws12 ws2r 15 |

**THIS IS THE ONE I WOULD PUT IN FRONT OF JOE AHEAD OF ANY KNOB.** `W_NOX=1` is a one-character
switch that already exists in `_chain10`, it was built for exactly this question in §15, and it is
worth more than every knob change except `mae_stop_pct` - with a BETTER MFE/MAE and fewer legs,
which is the opposite of the trade-off every knob made.
