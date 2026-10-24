# `sweep-pivots` — BANKED 1024

Joe named it. The swing scale a sweep measures MFE against, with **no pivot pct to set**.

Joe 1024: *"let's make it a machine and lock down the spec. if there's knobs, make sure they're
visible"*, and before that: *"sweep-pivots feels like an honest improvement"*.

---

## 1. Why it exists

Joe 1024: *"getting swings correctly dialed is the most load-bearing mech in a sweep - if we can't
rely on them then we produce false results"*.

Then: *"I'm going to hand it back to you and find a way to dynamically set it. fixing a pct has
never completley served us - now I feel like we have a way to automate it"*.

The banked exit rule measures MFE from the entry to *"the next favourable 2% pivot"*. That 2% is a
fixed pct, and one fixed pct can only ever match one swing size. `sweep-pivots` replaces it with a
boundary the lines themselves define.

---

## 2. The mech, his words

Joe 1024, across four messages:

> I'd be looking more at Mages crossing to ib across various TFs, maybe (ws3Mage, ws5Mage,
> ws10Mage, ws15, ws20, ws30). we can reliably predict that a mage crossing from oob to ib will
> always land on the MFE side.

> given that a sweep allows full lookahead, you can collect the swings and pivots from all of the
> noted Mages. when you have an event to test, see how many per-Mage-pivots are closest to the
> event. if you have multiple TF's Mages pivots that align with the event, then your likely at a
> larger swing and can use the higher TFs swing to more accurately gauge the MFE (instead of using
> a small swings MFE)

> instead of scoring after the event, why not pre-build the pivot data for all of the in-use Mages,
> then pick the pivot from the index based on same direction and closeness to the prior pivot

> start at the lowest TF and scan upwards. you should find a series of TFs printing the near-same
> distance from their own pivot to the event. the TF swing/pivot to pick should be the highest TF
> printing the lowest pct (between pivot and event)

And the two corrections that shaped it:

> it should be the prior pivot, if we're following my "opens on the MFE side" view

> not identical - the mages will all cross to ib in their own order, so the pct to event will always
> be near, not identical

---

## 3. The mech, as built

| the step | the mechanism |
|---|---|
| the index | every in-use Mage's oob -> ib crosses, bar-sorted, cached. `index()` |
| a leg | a cross, then the next OPPOSITE-side cross of the SAME Mage. Both ends mechanism-defined. `legs()` |
| a TF's pivot | that leg's extremum on the walk's side — the LOW of a leg a LOW cross opened |
| a TF's pct | the favourable-signed move from its pivot to the event. **From the EXTREMUM**, his *"extremum - that was a good call"* |
| the pick | the lowest \|pct\| across the TFs; on a tie within `SP_BAND`, the HIGHEST TF of that group |
| the swing | the picked TF's own leg, and the MFE measured inside it |

**The side mapping inverts.** A LONG wants price UP, so its leg is one opened by a LOW cross:
`side = -1`. `swing(bar, side)` has favourable = `-side`, so a caller passes `side = -d`.

**Lookahead is allowed here and only here.** Joe: *"given that a sweep allows full lookahead"*. A
leg is closed by a cross AFTER the event, so `scale` and `swing` read the future on purpose. They
are SCORING. No mech step may call them, and `v4_test_script`'s stage guard asserts that
separately — every mech function's signature is checked for a price-derived parameter at import.

---

## 4. The knobs — all six, and every value is a measurement

They live in `v4_knobs.py`, which refuses an off-ruled run unless `W_V4_EXPERIMENT=1`.
`v4_sweep_pivots.knobs()` prints the set any run used.

| the knob | value | what set it |
|---|---|---|
| `SP_PICK` | `lowest_pct` | his 1024 rule, verbatim above |
| `SP_BAND` | 0.0 pct points | his near-same band. 53.6% of 37,178 consecutive-pct gaps are **exactly 0** — TFs sharing a leg extremum — and p10 through p50 are all 0.0000 while p75 is 0.3705. So 0.0 already captures the clustering |
| `SP_CONTAIN` | 0, OFF | the event-inside-the-leg filter |
| `SP_XWOB` | 18 bars = 90 s | his *"introduce a wob 18 and retest"*. The only wob he named for this mech |
| `SP_ALIGN_S` | 300 s | his *"agreed on 300s"*. **UNREAD** under `SP_PICK` `lowest_pct` — it gates only the `window` arm, kept as the comparison |
| `SP_TFS` | `wide` | **THE ONE ITEM AWAITING HIS WORD** — see §7 |

---

## 5. What was measured, and what it says

### His claim holds

> we can reliably predict that a mage crossing from oob to ib will always land on the MFE side

Anchored on the PRIOR pivot — his correction — **82% to 93%** of Mage oob->ib crosses open on the
favourable side of the move's start, across every TF and every pivot pct from 0.5 to 2.2.

MEASURED FORWARD IT HAD READ 43% TO 59%, and that was my error, not his claim: the *next* pivot is
where the move ENDS, so measuring to it scored each cross against its own destination.

### The ladder is real, which is why there is no pct

Each Mage's own consecutive opposite-side crosses bracket a leg. The medians over the 94 days are
monotone with no inversions:

| the Mage | legs | median leg % | the px_smooth pct whose median leg matches |
|---|---|---|---|
| ws1Mage | 2,937 | 0.375% | 0.3% |
| ws2Mage | 1,564 | 0.606% | 0.3% |
| ws3Mage | 1,064 | 0.751% | 0.4% |
| ws5Mage | 649 | 1.007% | 0.6% |
| ws10Mage | 348 | 1.477% | 0.8% |
| ws15Mage | 228 | 1.831% | 1.0% |
| ws20Mage | 182 | 2.198% | 1.3% |
| ws30Mage | 116 | 2.633% | 1.5% |

The pct equivalents span 0.3% to 1.5%, so one fixed pct can match exactly one rung. That is
*"fixing a pct has never completley served us"*, in numbers.

### The event lands a QUARTER into its swing, whatever the size

This is the finding that locked the mech, from 5,323 events:

| the leg MFE band | events | median \|pct\| off the pivot | median share of the leg behind |
|---|---|---|---|
| 0.0 to 0.5% | 297 | 0.071% | 0.176 |
| 0.5 to 1.0% | 1,461 | 0.148% | 0.221 |
| 1.0 to 2.0% | 1,804 | 0.416% | 0.286 |
| 2.0 to 4.0% | 1,252 | 0.791% | 0.295 |
| 4.0% and up | 509 | 1.284% | 0.201 |

The distance off the pivot rises 18× across those bands while the share holds between 0.176 and
0.295. So the population median of 0.327% is not an error — it is a quarter of the median 1.397%
leg. **A bigger swing comes with a proportionally bigger pct, same quarter.**

| the sign read | of 5,323 events |
|---|---|
| the event fires BEFORE its pivot | 5,177 = 97.3% |
| the event is already FAVOURABLE of the pivot | 4,446 = 83.5% |
| exactly on the pivot | 54 = 1.0% |

**This is why his cluster-REACH rule was not built.** Reaching up a rung buys a bigger leg and a
proportionally bigger pct — the trade the band table appeared to show is an *identity*, not a cost,
so there is nothing for a reach value to optimise.

---

## 6. Three things measured and REJECTED, recorded so they are not re-proposed

| the idea | why it is out |
|---|---|
| tolerance-free **containment as the alignment rule** | ws30Mage becomes the highest marker on 2,350 of 5,323 events, 44.1%. Its legs run 14,157 s, so the rung wins by being WIDE, not by matching |
| **containment as a candidate filter**, `SP_CONTAIN` | right on the 3 events it was proposed against, wrong on 5,323: 2,198 events lose EVERY candidate, the median candidate count falls 8.0 -> 1.0, the median distance off the pivot goes 0.327% -> 1.157% and the worst 8.953% -> 26.146%. The 3 events all came from the 18, which were selected for a large grace move and therefore sit inside well-formed legs |
| a **wider `SP_BAND`** | monotone trade with no knee. 0.0 -> 0.5 moved within-0.25% 43.6% -> 28.8% and bought only +1.397% -> +1.802% of leg |

---

## 7. The one item awaiting his word: `SP_TFS`

His 1024 list was **six**: ws3Mage, ws5Mage, ws10Mage, ws15Mage, ws20Mage, ws30Mage.
**ws1Mage and ws2Mage are MINE.** Every measurement that justified banking ran on all eight, so the
banked value is the set that was RUN — banking the six would bank something never measured.

| the TF set | the 18-row check | median off the pivot |
|---|---|---|
| `wide`, all eight — BANKED | 17 of 18 scored under the `window` arm, 18 of 18 under `lowest_pct` | 0.013% |
| `his`, the six | 8 of 18 under `window` | 0.156% |

At `SP_ALIGN_S` 300 ws1Mage and ws2Mage are the scale TF on **41.0%** of events. Set
`W_V4_SP_TFS=his` to run his six, with `W_V4_EXPERIMENT=1` since it is off the bank.

---

## 8. The validation

### The 18 rows he called perfect

Joe 1024: *"all of these are perfect on `EXHAUST grace 180`"*.

| the read | value |
|---|---|
| scored | 18 of 18 |
| median distance off the pivot | 0.013% |
| worst | 0.114% |
| within 0.25% | 18 of 18 |

THE 18 ARE NOT REPRESENTATIVE and that is on the record: they were selected for a large grace move,
which picks events sitting on their extremum. The population sits a quarter in. I reported the
18-row result as validation before knowing this, and then built two enhancements on top of it.

### The ws5rbackstop sweep — his option 3

Joe 1024: *"recreate the ws5rbackstop sweep that we banked yesterday. that gives us a level of
comfort or discomfort, without interfering in our in-progress v4core to 'ws4r to ws1Mage ib' design
flow"*. The backstop is BANKED, so its trades owe nothing to the mech under design — which is the
circularity he caught: *"to be well placed the event needs to be preceeded by v4core, and that's a
circular reference"*.

12 of 27 configs ran; 15 line caches are gone from `.rpl_cache/lines` — every config with k_len 5
or rsi 7. Both key configs were present. Full table in `out/net_sp.md`.

| the reading | across all 12 configs |
|---|---|
| the stop rate falls | 27.2–31.0% -> 17.2–21.3%, no overlap between the ranges |
| the median MFE roughly halves | 1.550–1.733% -> 0.868–1.010% |
| gross falls | 25–30% on every config |
| the trade count | identical, except 1 row of 6,037 |

| rsi | stc | k_len | the MFE window | trades | stopped | stop rate | gross % | median MFE % |
|---|---|---|---|---|---|---|---|---|
| 6 | 8 | 6 — BANK | banked 2% pivot | 628 | 175 | 27.9% | +726.32 | +1.691 |
| 6 | 8 | 6 — BANK | sweep-pivots | 628 | 124 | 19.7% | +532.20 | +1.009 |
| 5 | 8 | 7 — DB row | banked 2% pivot | 387 | 112 | 28.9% | +397.56 | +1.573 |
| 5 | 8 | 7 — DB row | sweep-pivots | 387 | 69 | 17.8% | +317.17 | +0.913 |

**THIS DOES NOT SAY WHICH WINDOW IS RIGHT.** Both nets are scoring artefacts — the 90%-of-MFE leg
is not causal under either — so a smaller net is not a worse mech. What it says is that
`sweep-pivots` is stable across 12 line configs whose ws5r controls span 1.30 to 18.67.

The one anomalous row: on `5|7|6` the sweep-pivots arm has 621 trades against 622. One trade's leg
closes on its own entry bar, so there is no window to measure and the `hiB <= en + 1` guard drops
it. 1 of 6,037 rows.

---

## 9. Still open

| the item | state |
|---|---|
| `SP_TFS` | his word — §7 |
| scored on MACHINE events | never done. Every population so far is the in-test `ws4r -> ws1Mage ib` chain's or the backstop's. The circularity he named is unresolved |
| the 15 missing line caches | `RS.load` is read-only; rebuilding them was not authorised |
| `out/net.md`'s column labels | read `k \| rsi \| stc` but hold `(rsi, stc, k_len)` — the transposition this session found in `v4_rcfg_sweep.spec`, still live in that file's header |

## Related

`v4_sweep_pivots.py` · `v4_net_sp.py` · `v4_knobs.py` · `out/net_sp.md` · `out/mage_sweep_prior.md` ·
`out/mage_align.md` · `out/band_sweep.md` · `out/sweep_pivots_18.md`
