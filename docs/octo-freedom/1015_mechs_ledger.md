# 1015 — THE MECHS LEDGER

The register for the final review before the machine goes live. One row per mech. Every figure in
it comes from a run recorded in `1005_scoring/1015_ongoing_momentum.md`, which is the evidence
file; this is the index over it.

STRUCTURAL CHOICES, MINE, STATED: one row per mech; knobs listed separately from mechs because a
go-live review checks them separately; withdrawn claims kept visible rather than deleted, so a
reviewer can see what was retracted and why.

STATE VOCABULARY — existing project words, no new coinage:
  BANKED      the code default has moved and an off-ruled run refuses
  MEASURED    a run exists with its n stated. NO CODE, NO DEFAULT MOVED
  RULED OUT   measured and rejected
  PARKED      no code, no spec text, no explanation
  POI         Joe's tag. Surfaced for later, deliberately not built
  WITHDRAWN   a claim I made and retracted, with the cause

---

## A — THE MECHS

| # | the mech, in Joe's words where he gave them | state | the evidence, with n | what it still needs |
|---|---|---|---|---|
| A1 | the ex-fence level base rate — will ws{t}r reach 83 before falling under 50 | MEASURED | 207,360 bars, 2026-07-11 to 2026-07-22. 80-83 rising ~72%, 70-80 ~47%, 60-70 ~34%, 50-60 ~21%. Nearly TF-independent | nothing — it is the reference, not a mech |
| A2 | the bounce count — crossings of Mage 85 in the prior 30 min, as a continuation predictor | MEASURED | 11 timeframes. 0 bounces 32.3% to 62.6% reach ex-fence; 11+ bounces 13.8% to 25.8%. 0 beats 11+ on every line. n per cell 18 to 509 | a hold-out. The 0-bounce bin is thin above ws10 — n 31, 31, 23, 18 |
| A3 | "all of the ws{>1}Mages reversing inside the same high oob window" | MEASURED | high side 07-22 14:06:20: ws4Mage-ws12Mage top inside 25 s, all 11 of ws2-ws12 past oob 85. Low side: the equivalent is 24.67 min wide and 6 of 10 never reach oob 15 | the oob-at-the-turn filter, gap 19 |
| A4 | the matryoshka cascade ORDER, small TF leads large | RULED OUT | 135 H pivots. g5/g15/g30/ws1 all sit at 0.10-0.12 of their own firing gap, so they are equally aligned and differ only in firing rate. Only g5Mage's lead exceeds the shift surrogate; ws1Mage and ws4Mage lead LESS than chance | nothing. The ordering is a firing-rate artefact, Huth & Abergel Appendix B |
| A5 | the matr-rev conjunction — k of Joe's five lines crossing oob->ib inside a span W, as a PIVOT CONFIRMER | MEASURED | 135 H pivots. k5/W12: 52 events, 28.8% have an H pivot within 3 min before, against a 2.4% random-bar baseline and ~1 event per surrogate draw. k4/W24: 260 events, 18.8%, surrogate 15 events. Survives the null test at every k | k and W are unruled — gaps 13, 14 |
| A6 | the oob-at-the-turn filter — a joint turn marks a pivot only when the band is oob at the turn | MEASURED | ONE LEG PER SIDE. high 14:06:20, band oob, turn landed +0.00 min on the pivot, a 2.0158% reversal. low 14:30:25, band in-fence with minima 20.46-34.62, turn landed -30.58 min early, a 1.2916% bounce at 64.07% retracement | a base rate on both pivot kinds — gaps 17, 19 |
| A7 | the band-in-fence-at-the-cp read — ride instead of taking the cp | MEASURED | ONE LEG. at the 15:03:40 HIGH cp, 0 of 16 lines above ws1 were oob, all 43.47-58.30 and rising, and 16 of them topped AT the 15:29:30 price pivot. The cp was 25.83 min and 0.6545% early | a base rate — gap 22 |
| A8 | "ride the ws5Mage line from oob to oob" | MEASURED | ONE LEG. entry 14:14:55 as ws5Mage leaves high oob at 85.94. The target is reached 122.42 min later at 16:17:20, realising +1.6385%, MAE 0.0000%. It round-trips to +0.2109% in the middle | a base rate; and the oob target left 2.60 points against a +4.6026% ceiling |
| A9 | the matr-rev family as the ride's EXIT, CUMULATIVE reading | MEASURED | ONE LEG. 3 lines 14:22:15 +0.5706%; +ws2Mage 14:45:55 +1.3388%; +ws3Mage 16:18:50 +1.4630%; +ws4Mage and +ws5Mage do not move it — ws3Mage is the last member in | a base rate; and it loses to the oob target by 0.18 points |
| A10 | the matr-rev family as the ride's EXIT, SPANNED reading | MEASURED | ONE LEG. 5 lines at W 24 bars = 2 min fires 19:15:40, realises +2.0036%, MFE 2.1938%, MAE 0.0000% — beats the oob target by 0.37 points for 178.33 min of extra exposure. 6 and 7 lines fire later and realise less | a base rate; and gap 26 — cumulative and spanned give opposite verdicts |
| A11 | the ws5x OVER-cross race, targets boundary / r / Mage, at Joe's xwob 8 | MEASURED | ONE LEG. from the 16:18:50 detect: Mage conf 16:31:55 at +13.08 min, boundary and r conf 16:32:05 at +13.25 min. Realised +1.6746% / +1.6062% / +1.6062% | gap 28 — the finishing order IS the level order (ws5Mage 11.45 < boundary 15.00 < ws5r 17.83) and boundary and r tie exactly |
| A12 | the ws1r divergence at a cp, via `jig.anchor_floater` | MEASURED | high side, anchor 14:07:05: ws1r 70.76 vs floater 98.08 at 13:38:20, close +1.4066%, fired 1, BEARISH. The floater IS the false cp's hilltop. low side, anchor 14:26:20: ws1r 12.88 vs floater 5.69, close -0.5789%, fired -1, BULLISH, and correct — MAE -0.4198%, MFE +0.8664% | nothing new. `jig.divergence`'s oob-episode route does NOT fire at 14:06 — only the anchor_floater route does |
| A13 | matryoshka reversal used to CONFIRM a pivot before entry | MEASURED | ONE LEG. the 14:26:20 LOW cp alone: MAE -0.4198%, MFE +0.8664%, ratio 2.06. Waiting for 3 of 5 inside 1 min at 14:46:00: MAE -0.1465%, MFE +1.1433%, ratio 7.80, for 19.67 min of entry delay | a base rate. The 1-min span beat the 2-min span by SKIPPING a firing — a sample of one, gap 18 |
| A16 | the low-leg Mage bottoming order, uncapped — Joe 1015: *"this is your learnings realised. it's a mech to add to the ledger"* | MEASURED | ONE LEG, the 14:06:20 H to 14:55:05 L leg. g15Mage bottoms 14:15:50 at -15.88, g30Mage 14:24:25 at -2.19, ws1Mage 14:24:30 at -8.89, then TEN lines ws4 to ws30 bottom at exactly 14:30:25 — the same bar as the price low. ws2Mage 14:45:35, ws3Mage / ws12Mage / ws20Mage 14:55:05 | a base rate. It replaces the WITHDRAWN capped version in section D |
| A17 | at the ridden line's turn, the oob band's edge IS the ridden line | MEASURED | ONE LEG, the ws5Mage turn at 2026-07-22 18:20:55. All 7 lines faster than ws5 are at or past HIGH oob 85 — g5Mage 89.71, g15Mage 106.91, g30Mage 119.96, ws1Mage 112.90, ws2Mage 102.11, ws3Mage 104.35, ws4Mage 92.14. ws5Mage 70.93 is NOT oob, 14.07 short. All 12 slower lines are not oob, 30.80 to 70.34. The gap across the edge, ws4Mage to ws5Mage, is 21.21 points | a base rate. Whether the edge position is a usable read at the turn bar is unknown |
| A18 | the mass simultaneous turn at a price pivot, third instance | MEASURED | 17 of 20 lines make their leg high at 2026-07-22 18:20:55, which IS the H price pivot at the banked 0.9%, close 0.13693504, +1.2090% off the 17:26:45 low. The three exceptions: g5Mage turns +26.00 min LATER at 137.01, g15Mage +27.17 min later at 143.85, ws2Mage 39.83 min EARLIER. THE TWO FASTEST LINES OVERSHOOT THE PIVOT BY NEARLY HALF AN HOUR, which is the inverse of small-leads-large and consistent with A4 being ruled out | a base rate across all pivots. Three instances so far: 14:06:20 H, 14:30:25 L at 0.5%, 18:20:55 H |
| A19 | the NON-OOB band read — Joe 1015: *"don't use oob. if the TF lines less than ws5Mage (g5 to ws4) print mostly higher values, and the TF lines greater than ws5Mage (ws6 to ws60) print mostly lower values, then the next move is downward / the inverse is true"*, with his condition *"I _think_ this method only works when ws5Mage is infence"* | MEASURED | TWO BARS. 2026-07-22 17:48:00: g5-to-ws4 median 73.85 vs ws6-to-ws60 median 48.83, 84 of 84 pairs with the lower line above, ws5Mage 57.49 IN-FENCE, verdict DOWN. Next pivot H 18:20:55 +0.2185%, then L 19:13:15 -1.1535%. 2026-07-22 21:34:00: medians 28.01 vs 33.54, 33 of 84 pairs (39.3%), ws5Mage 39.73 IN-FENCE, verdict UP. Next pivot H 22:15:30 +0.9328% | the horizon. "the next move" is undefined - 17:48 goes +0.2185% the wrong way first, then -1.1535%. And separation strength did not predict immediacy: 100% clean at 17:48 went wrong first, 39.3% at 21:34 went right immediately |
| A20 | the confluence at 17:48 — Joe's hypothesis *"the non-oob oob band and the lineage EXHAUTION confluence each other"* plus his question *"has the turn-predictor recently fired?"* | MEASURED | ONE BAR. Four events inside 2 min: the 5-line HIGH-side matr-rev conjunction at 17:47:05 (span 60 bars = 5 min, all five of g15/g30/ws1/ws2/ws3 in); ws3x crossing UNDER ws3r at 17:48:00 with ws3r HIGH oob at 98.31, its oob 1.67 min old; the band separated 84 of 84 with ws5Mage in-fence at 17:48:00; the ws1cp-ib at 17:49:55 from the cps at 17:40:15 and 17:41:35. Members' own confs: ws3Mage 17:47:55 (0.08 min before), ws1Mage 17:47:30, g5Mage 17:47:05, ws2Mage 17:45:50, g30Mage 17:42:55, g15Mage 17:42:20 | a base rate. AND the span: the 5-line conjunction fires here ONLY at a 5-min span - at 1, 2 and 3 min it has not fired since 16:00. Gap 14 decides whether this confluence exists |
| A21 | the 17:48 band compared with the 18:20:55 band — the two are opposite structures | MEASURED | at 18:20:55, 7 lines faster than ws5 are at or past oob 85 and the 12 slower are not; ws5Mage is the edge. At 17:48:00 only ws2Mage (91.18) is past 85 — 19 of 20 are in-fence, and 0 of 20 are past 85 continuously from 17:46 to 18:16, half an hour. The split at 17:48 is a DIRECTION split at ws3: g5Mage through ws2Mage all FALLING, ws3Mage through ws60Mage all RISING | nothing. It answers Joe's question "do you see the same band split at ~17:48" with NO, and names what is there instead |
| A22 | "riding ws5Mage 101" — Joe's name, 1015, for the qualified set: the four confluence events plus the lineage exhaust, then the walk to low target-side | MEASURED | ONE LEG. Qualified at 2026-07-22 17:48 by A20's four events. The walk ends 18:32:55 when ws5Mage reaches the low oob at 14.79, 44.92 min. THE NEXT PIVOT the walk marks is L 2026-07-22 19:13:15 at 0.13506047. The SHORT from 17:48: MAE 0.2185%, MFE 1.1535%, MFE over MAE 5.28, realised +1.1535%. Entering at 17:48 beats the 17:49:55 ws1cp-ib, which gives MAE 0.4320% and +0.9428% | a base rate. AND the walk-end definition — gap 30 |
| A23b | EXHAUSTION'S PREMISE — Joe 1015: *"this statement can only apply to high-side. it's saying that at least one r line is HIGH oob, so exhaustion fires if a slower line has not made it to HIGH oob"*, and the inverse for LOW OOB | MEASURED, and it is in the code | ONE BAR, 2026-07-22 19:12:30, on the RULED config W_KICK=high. 0 of 30 r lines at HIGH oob; ws1r 9.50 and ws2r 7.54 at LOW oob. THE LONG, toward HIGH oob: ends 19:14:35 on "max jumpstart gap" - *"no line at or under ws7 went oob within 24 bars (2.0 min) of the handoff; the jumpstart never fired"*. NO EXHAUSTION TEST IS REACHED. THE SHORT, toward LOW oob: the jumpstart fires 19:12:35 on rider ws2, *"highest oob line at or under ws7, r 7.54"*, then EXHAUSTED on ws2 at 19:13:50 - ws3r 39.60 and ws4r 55.60 no momentum. The premise is enforced BY THE JUMPSTART, which requires an oob line | nothing. It is the mech as built |
| A23 | LINEAGE AS A CLOCK — `run_leg` sampled from successive bars, which measures how long a leg opened at that bar is carried | MEASURED | ONE LEG, the LONG side from the 2026-07-22 19:12:30 signal, sampled every 60 s for an hour. 19:12:30 to 19:21:30 all close in 2 bars. The first carry is 19:22:30, 90 bars = 7.50 min, +0.1798%, when ws2r goes 7.54 to 51.22. The longest is 19:57:30, 392 bars = 32.67 min, +0.7267%. CARRYING IS NOT BEING RIGHT: the 19:30:30 to 19:39:30 opens all carry, up to 113 bars, and every one realises negative, -0.12% to -0.26% | a base rate. And a ruling on whether a lineage carry is a confluence item at all, given the negative-carry window |
| A24 | the turn-predictor's ws1Mage gate — Joe 1015: *"the turn signal can only fire if ws1Mage is same-side oob"* | MEASURED | Applied as the literal reading: at the conjunction's fire bar ws1Mage is oob on the turn's own side, >= 85 HIGH or <= 15 LOW. SATISFIABLE - the conjunction can be driven by other members while ws1Mage is still extended, as at 17:47:05 where ws1Mage had not yet crossed to ib. DECISIVE at the 19:12:30 signal, where ws1Mage is 19.43 IN-FENCE and so a LOW-side turn signal is blocked | the alternate readings are not measured: ws1Mage oob anywhere inside the span, or ws1Mage required to be one of the k crossing members |
| A25 | the live forward test from the 18:45:35 exit — the next turn-predictor or ws5Mage oob, either side | MEASURED | ws5Mage reaching LOW oob at 12.87 on 2026-07-22 19:12:30 fired FIRST, +26.92 min. Every gated turn-predictor is later: HIGH 3-of-5 at 20:12:05 (+86.50 min), LOW 3-of-5 at 2026-07-23 01:38:40, HIGH 4-of-5 at 2026-07-23 04:23:15, LOW 5-of-5 at 2026-07-23 09:55:10, HIGH 5-of-5 at 2026-07-23 16:39:20. The signal bar is 0.75 min before the 19:13:15 L price pivot - the tightest arrival measured today, against 40.33 min on the previous leg. The band read 24 of 84 pairs (28.6%), verdict UP, and price rose +1.1773% to the 20:25:45 H pivot | a base rate. CONFIG: W_ARM=lastmile (Joe: *"doesn't rely on ws1cp"*) and W_KICK=off, which REQUIRED W_EXPERIMENT=1 because W_KICK is ruled `high` in lastmile mode (Joe 1013). The default has NOT moved |
| A14 | mom-xfer run against ws{some TF}Mage excursions instead of coiled events | POI | not built. The shape it would count is present: 2 timeframes (ws2, ws3) left the ride at 13:46:25 and are the 2 off the high end at the pivot | Joe's tag, 1015. Gaps 9, 10, 11 |
| A15 | the octo-sigs brought back into the walk | POI | HELD at Joe's word — *"not just yet"* | Joe's tag, 1015 |

NOTHING IN SECTION A IS BANKED. No code default moved today. No file under `1005_scoring/` was
edited except the evidence doc and this ledger.

---

## B — THE KNOBS IN PLAY, AND WHOSE THEY ARE

| knob | value | units | whose | where it comes from |
|---|---|---|---|---|
| oob_hi / oob_lo | 85 / 15 | r-points | Joe | `lazy_g_config`. oob ALWAYS means 15/85 |
| momo_fence_r | 17 | r-points | Joe | `lazy_g_config`. the ex-fence is 100-17 = 83 on the high side |
| boundary_xwob | 4 | bars = 20 s | Joe | `wsf_dtf_v3_config` section `ws1mage_rev`. Joe 0911 *"boundary:4"*. NOT in lazy_g_config |
| rev_wob | from `lazy_g_config` | steps | Joe | used by `_mage_rev`; superseded for this work by the oob->ib cross on Joe's 1015 clarification |
| lp_lr_swing_pct | 0.9 | % | Joe | `lr_config`. `find_pivots`'s ZigZag threshold |
| mom_xfer.count_min | 2 | timeframes | Joe | `wsf_dtf_v3_config` v8. Joe 0920 *"2 is arbitrary"* |
| momtf_dr | ws10, ws11, ws12 | timeframes | Joe | `docs/22_go_20260921/README.md` |
| handoff.ride_tf_hi | 4 | timeframe | Joe | `ride_to_max`'s ride ceiling |
| the matr-rev family's members | g15, g30, ws1, ws2, ws3 | lines | Joe | named 1015, extended by him to ws4 and ws5, which measured as no gain |
| the matr-rev span W | UNRULED | bars | — | gap 14. 12 bars = 1 min best on precision, 24 bars = 2 min best on precision-recall |
| the matr-rev k | UNRULED | lines | — | gap 13. 5 is the literal reading of *"they each"* |
| the ws5x xwob | 8 for this test | bars | Joe | his 1015 instruction. xwob 1 realises +1.8061% and xwob 2 +1.8085% against xwob 8's +1.6746% on the one leg. DEFAULT NOT MOVED |
| the bounce lookback | 360 bars = 30 min | bars | mine, diagnostic | gap 6. Chosen off Joe's *"~35 minutes"*; he has named no number |
| the pivot kind measured | H pivots | — | mine, diagnostic | gap 24. EVERY base rate in the evidence doc is high side only |

---

## C — THE OPEN GAPS, 1 TO 29

| # | the gap |
|---|---|
| 1 | which lines are "all of the ws{>1}Mages" — ws2/ws3 top 19.9 min early, ws4-ws12 inside 25 s |
| 2 | the width of "the same high oob window" |
| 3 | what "high oob" means on an unbounded Mage. RE-OPENED as the live filter in A6 |
| 4 | the lookback for "ws1Mage never dips past 50" |
| 5 | which TFs count toward "at least 2 r's in-fence" — a floor, not the selector |
| 6 | the bounce lookback. 30 min used, off Joe's "~35 minutes" |
| 7 | CLOSED — Joe 1015: the pivot is the top or bottom pxs value in a swing |
| 8 | whether the bounce count is read per line or on ws1 as the noise reference |
| 9 | which TF's Mage excursion mom-xfer reads |
| 10 | whether `momtf_dr` stays ws10/ws11/ws12 or becomes the ws2-ws12 band |
| 11 | whether an excursion is the oob entry, the oob exit, or the Mage top |
| 12 | CLOSED — the precision/recall curves are measured, forward and backward |
| 13 | k — how many of the five must cross |
| 14 | the span W |
| 15 | whether g5Mage joins the five. It is the worst line backward at 1.5x and adds 3373 firings |
| 16 | CLOSED — the update-rate null test ran. A4 ruled out, A5 survived |
| 17 | the high/low asymmetry. Every pivot base rate is H pivots only |
| 18 | the 1-min span beat the 2-min span by skipping a firing — a sample of one |
| 19 | the oob-at-the-turn filter needs the L-pivot base rate and an in-fence-versus-oob count |
| 20 | riding to the Mage top is not a mech. `ride_to_max` rides to a flat-run test-point |
| 21 | which TF gets ridden. 16 lines top on the same bar on the one leg measured |
| 22 | the base rate for "band above ws1 in-fence at the cp -> the cp is early" |
| 23 | whether the matr-rev is an exit or only a turn-predictor |
| 24 | the swing pct the pivots are read at. Joe reads structure at 0.5%; every table uses 0.9% |
| 25 | the family's membership |
| 26 | CUMULATIVE versus SPANNED. 0.54 points apart on the 5-line family, opposite verdicts |
| 27 | the family tops out at +2.0036% against a +4.6026% ceiling with 0.0000% MAE |
| 28 | the race targets are not independent — their order is their level order |
| 30 | what "low target-side" ends the walk at. The low oob (ex-fence 17 / oob 15, the same bar here) gives a 44.92 min walk ending 18:32:55 and marks the L pivot. Under 50 — Joe's own divergence-spec phrase — the walk ends 17:48:15, 15 seconds in, on a flicker: ws5Mage goes 49.73 then 52.77, 53.44, 47.70, 45.43, 50.51, 54.92 and on to 70.93 |
| 29 | two holds in one mech: xwob 8 for the ws5x cross, `boundary_xwob` 4 for the members |

---

## D — WITHDRAWN CLAIMS, kept visible for the review

| the claim I made | the cause | what replaced it |
|---|---|---|
| "all nine of ws4Mage-ws12Mage bottom at 14:24:30 in a 0-second window" | I capped the span at the 14:26:20 cp. Joe never specified it, and its edge became the headline | the real span is 14:30:25 to 14:55:05, 24.67 min. Ten lines from ws4 to ws30 bottom at 14:30:25, the same bar as the price low |
| "the BULLISH divergence at the LOW cp is wrong" | I scored it only to the next L pivot, which is the adverse leg by construction | MAE -0.4198%, MFE +0.8664%, ratio 2.06, closing +0.8664% at the next favourable swing. The divergence was right |
| "no single line is a pivot warning" | that was the FORWARD framing, which asks a confirming detector to forecast | backward, g30Mage is 3.9x and ws1Mage 4.1x the baseline |
| "the band that converges is ws1 to ws15, not the higher TFs" | measured on boundary crossings only | on the price-pivot measure ws20-ws60 are the best of all 17, topping on the pivot without ever going oob |
| "THE NEXT PIVOT is H 2026-07-22 18:20:55, +0.2185% the wrong way" | I marked the next pivot after the WALK START, 17:48. Joe said mark the next pivot after the WALK ENDS | the walk ends 2026-07-22 18:32:55 when ws5Mage reaches the low oob at 14.79. THE NEXT PIVOT is L 2026-07-22 19:13:15 at 0.13506047, -1.1535% from 17:48. The H at 18:20:55 sits INSIDE the walk, with ws5Mage at 70.93 still on the high side of 50 |
| "lineage refuses, 10 seconds in" at the 2026-07-22 19:12:30 signal | `run_leg` is an EXIT mech, so "refuses" was the wrong word | the mech that fired is `exhausted_cycle`, titled "THE LAST MILE'S EXHAUSTION", whose docstring quotes Joe 1013: *"the end is the EXHAUSTION event. I'm sure that this is the existing mech"*. The correct sentence: THE LAST-MILE EXHAUSTION FIRED |
| "at 19:12:30 lineage has nothing above ws1 to walk on" explained as a TIMING fact because the lines were near the bottom of their range | Joe 1015: *"isn't that the very definition of EXHAUSTION?"* - it is. And I explained it by POSITION while the mech decides on MOMENTUM. `towards_dr`'s own docstring: *"Nothing about the line's position is read - a line can be in-fence and still be heading to the target end"*. The trace said "no momentum" for both lines and I overrode it | ON THE RULED CONFIG THE LONG NEVER REACHES AN EXHAUSTION TEST - it ends 19:14:35 on "max jumpstart gap". See the next row |
| "the last-mile exhaustion fired at 19:12:30 because neither ws2 nor ws3 was momentum-true toward the HIGH board" | I ran `W_KICK=off` under `W_EXPERIMENT=1` and read its output as the machine's behaviour. The trace said what I had done: *"KICKSTART disabled, no oob test, lineage climbs from the bottom"*. With no oob test there is no established climb, so the exhaustion fired on an empty premise | on the RULED config W_KICK=high: the LONG ends on "max jumpstart gap"; the SHORT's jumpstart rides ws2 at LOW oob 7.54 and exhausts at 19:13:50 when ws3r 39.60 and ws4r 55.60 do not follow down |
| A23b as first banked, "the two established mechs disagree, reading the same two numbers" | the same off-ruled config | WITHDRAWN. On the ruled config the two AGREE: the SHORT's low-oob climb is exhausted because the slower lines did not follow, and the band rule says UP. Same conclusion by two routes |
| "the HIGH board" and "the LOW board" in every exhaustion statement | OOB replaced with "board" in my own wording during this session, and the record was made durable that way | the exhaustion test is an OOB test. HIGH OOB and LOW OOB. "Target board" remains Joe's term for the trade's target side; it is not the exhaustion test's word |
| the lag table's figures | indexed by the CROSS bar while reporting the CONF bar | conf-indexed: g30Mage 1.17, ws1Mage 2.08, ws2Mage 4.50, ws10Mage 128.58, ws12Mage 156.21 |

---

## E — THE RESEARCH, as spec intel only

104 agents, 22 sources, 25 claims verified: 9 confirmed, 16 refuted. None of it is a build input.

| source | what it gives us |
|---|---|
| Huth & Abergel, J. Empirical Finance 2014, DOI 10.1016/j.jempfin.2014.01.003 | Appendix B: a previous-tick estimator makes the more frequently updated series appear to lead with TRUE LEAD-LAG ZERO. This is what ruled out A4. Also their 3-layer protocol: score against random, then the lagger's own autocorrelation, then with the cost charged — their 60.3%/63.6% beat both baselines at p ~ 1e-11 and still returned -2.73/-3.44 bps net |
| Ren & Zhou, New J. Phys. 12 (2010) 075030 | recurrence-interval analysis, ~340,000 1-min points. The hazard of the next threshold event DECAYS with elapsed time; intervals cluster. Same sign as our A2 |
| Nyberg, Lizana & Ambjornsson, Phys. Rev. E 97, 032114 (2018) | crossing probability depends on the trajectory leading to it, and the deviation shows in the DISTRIBUTION OF THE NUMBER of crossings. A2's conditioning is formally licensed |
| Harman & Zuehlke, J. Econ. Finance 28(2) 2004, 147-154 | on identical run data the SIGN of duration dependence flipped with the hazard specification. Nothing of ours may become a hazard fit without this check |
| Hayashi & Koike, arXiv:1708.03992, SIAM J. Fin. Math. 9:1208-1248 | one lead-lag per dyadic scale band. One aggregate number hid a sign reversal across 2268 asset-days. Read the band, not a line |

NO PUBLISHED BASE RATE EXISTS for our A1 question. The only crypto Bollinger source conditions on
ex-post calendar epochs on 1-minute long-only BTC/USDT. Our own numbers are the only ones.

---

## F — JOE'S IDEAS, NOT PROVEN, WITH THE CONDITION THAT WOULD ACT ON THEM

| # | the idea, his words | the condition he set | state |
|---|---|---|---|
| F2 | *"the non-oob oob band and the lineage EXHAUTION confluence each other"* | tested at one bar, 17:48 - four events inside 2 min, see A20 | ONE BAR. Needs a count of how often the four co-occur across the 12 days |
| F1 | *"a 'good turn predictor' might need less 'predicting Mages' than an exit predictor"* | *"not proven, just an idea - if we find that the recent addition of ws3-5Mages breaks turn detection, then we'll act on my idea"* | NOT TESTED. The trigger is a turn-detection test with and without ws3Mage, ws4Mage, ws5Mage in the family. A9/A10 measured the EXIT side only: ws4Mage and ws5Mage added nothing to the exit, ws3Mage carried it past the oob target |

### What is already on the record that bears on F1

| finding | the number |
|---|---|
| A13, the turn side, 3 of 5 inside 1 min | MAE -0.1465%, MFE +1.1433%, ratio 7.80 at 14:46:00 |
| A9, the exit side, cumulative | ws3Mage is the member that carries it past 16:17:20; ws4Mage and ws5Mage move it 0.00 min |
| A10, the exit side, spanned | adding ws4Mage and ws5Mage moves the exit LATER and realises LESS: +1.8533% against +2.0036% |

So on the exit side the larger family already measured as neutral-to-worse. F1 predicts the turn
side will show the same or stronger. UNTESTED.

---

## G — THE ws5x CROSS HOLD, Joe 1015: *"I think the wob could be less - I was hoping for ~16:29"*

16:29 is NOT reachable by any xwob. There is exactly ONE over-cross per target between the
16:18:50 detect and 16:45, and each held 173 to 218 bars, so the 8-bar hold rejected nothing. The
floor is the cross bar itself.

| bar | ws5x | ws5r | ws5Mage |
|---|---|---|---|
| 2026-07-22 16:29:00 | -16.87 | 7.97 | 8.42 |
| 2026-07-22 16:30:00 | -14.47 | 7.97 | 4.01 |
| 2026-07-22 16:30:30 | -7.26 | 7.97 | 6.27 |
| 2026-07-22 16:31:00 | 9.20 | 11.98 | 10.66 |
| 2026-07-22 16:31:30 | 32.99 | 17.83 | 16.02 |

At 16:29:00 ws5x is 25.29 points BELOW its own Mage.

A smaller hold does pay, by 0.13 points, on the Mage target:

| xwob | conf bar | realised on the 14:14:55 SHORT |
|---|---|---|
| 1 | 2026-07-22 16:31:20 | +1.8061% |
| 2 | 2026-07-22 16:31:25 | +1.8085% |
| 3 | 2026-07-22 16:31:30 | +1.6937% |
| 4 | 2026-07-22 16:31:35 | +1.6620% |
| 6 | 2026-07-22 16:31:45 | +1.5614% |
| 8 | 2026-07-22 16:31:55 | +1.6746% |

xwob 2 is the best cell on this leg. THE DEFAULT IS NOT MOVED - the knob is Joe's.

---

## H — THE RIDE'S FULL PATH, for the go-live review

One leg, the 2026-07-22 14:14:55 SHORT. Every exit measured, in bar order.

| exit | bar | realised | MAE% |
|---|---|---|---|
| the 3-line matr-rev, cumulative | 2026-07-22 14:22:15 | +0.5706% | 0.0000% |
| the 4-line matr-rev, cumulative | 2026-07-22 14:45:55 | +1.3388% | 0.0000% |
| the oob-to-oob target | 2026-07-22 16:17:20 | +1.6385% | 0.0000% |
| the 5/6/7-line matr-rev, cumulative | 2026-07-22 16:18:50 | +1.4630% | 0.0000% |
| the ws5x over-cross, Mage target, xwob 2 | 2026-07-22 16:31:25 | +1.8085% | 0.0000% |
| the ws5x over-cross, Mage target, xwob 8 | 2026-07-22 16:31:55 | +1.6746% | 0.0000% |
| the ws5x over-cross, boundary and r, xwob 8 | 2026-07-22 16:32:05 | +1.6062% | 0.0000% |
| the ws5Mage turn at 70.93, 14.07 short of target side | 2026-07-22 18:20:55 | +0.8363% | 0.0000% |
| the 5-line matr-rev, spanned at 2 min | 2026-07-22 19:15:40 | +2.0036% | 0.0000% |
| the lowest close measured, to the end of 2026-07-23 | 2026-07-23 19:54:25 | +4.6026% | 0.0000% |

The entry bar is the high-water mark for 29.7 hours - MAE is 0.0000% at every exit. The best mech
exit is +2.0036%; the ceiling measured is +4.6026%.

---

## I — THE 1015/1016 LIVE WALK, banked

### The chain, six legs on 2026-07-22

| # | opens | side | how it opened | the exit | why | gross |
|---|---|---|---|---|---|---|
| 1 | 14:14:55 | SHORT | ws5Mage leaves HIGH oob at 85.94 | 16:31:55 | the ws5x over-cross of Mage, xwob 8 | +1.6746% |
| 2 | 17:48:00 | SHORT | the band 84 of 84 + ws3x under ws3r at 98.31 + the 17:49:55 cp-ib | 18:45:35 | the ws5x over-cross of Mage, xwob 8 | +1.0082% |
| 3 | 18:44:45 | LONG | the 18:30:25 LOW ws1cp, at its ib bar | 22:09:05 | the ws5x under-cross of the boundary, xwob 8 | +1.0087% |
| 4 | 19:12:30 | LONG | the LOW-side exhaustion signal, ws2r 7.54 oob, ws3r 39.60 and ws4r 55.60 in-fence | 22:09:05 | pyramided, cap 2 | +0.9980% |
| 5 | 22:09:55 | SHORT | ws5Mage enters HIGH oob at 86.25 | 23:20:05 | the ws5x over-cross of Mage, xwob 2 | +1.7160% |
| 6 | 22:10:35 | SHORT | ws5Mage re-enters HIGH oob at 85.15, accepted by Joe | 23:20:05 | pyramided, cap 2 | +1.7341% |
| **TOTAL** | | | | | | **+8.1396%** |

### A26 — THE x-CROSS ANCHOR. The sequence is not fixed.

| the anchor for the ws5x cross | total, xwob 2 | note |
|---|---|---|
| FREE, the first cross from the open | +1.6509% | the cross fires 2.08 to 21.92 min in, for near zero. Joe's *"x-crosses are fickle"* is confirmed by -4.3539% |
| the 5-of-5 matr-rev conjunction | +6.0049% | what was run. Best span 6-7 min at +6.1526% |
| **ws5Mage reaching the target-side oob** | **+8.0230%** | step 1 of Joe's own sequence, used as the anchor |

The established order - ws5Mage target-side oob, then the conjunction, then the x-cross - held on
legs 1, 2 and 3 and BROKE on leg 4, where the cross came 1.77 h BEFORE the conjunction.

ROOT CAUSE, measured: ws3Mage's LOW oob episode is 23:12:10 to 23:24:40 and the x-cross is
23:20:00, INSIDE it. ws3Mage's first confirmation is 23:26:10, 6.08 min after the cross. NO SPAN
FIXES THIS - the span governs the gap between confirmations, not whether a line has confirmed at
all. ws3Mage is the bottleneck with 3 confirmations in 3.7 h against g15Mage's 30.
Joe's large-price-move detection idea is NOT needed: the state is readable at the bar as "are all
five family members in-fence yet", and at 23:20:00 the answer was no.

THE ws5Mage-oob ANCHOR'S OWN TAIL, Joe's push: it fired on all 6 legs, 44.92 to 122.42 min after
each open, but the wait from a random bar is unbounded - median 70.33 min to LOW oob, 90th pct
288.58, 99th pct 501.83, longest in the 12 days 638.08 min.

### A27 — THE NON-OOB BAND, DISABLED at Joe's word 1016

Tested in-use across all six legs. Nothing improves.

| the band as | total | against the chain's +6.5813% at the time |
|---|---|---|
| A GATE at the entry | +3.8982% | -2.6831%. It BLOCKS legs 1 and 3, including the day's best |
| AN EXIT at the 42-pair threshold | +1.7585% | -4.8229%. It flips 1.08 min after leg 5's entry |
| AN EXIT at the band's extreme | +5.0569% | -1.5245%, and not implementable - the extreme is only knowable afterwards |

The band's strongest DISAGREEMENT of the day, 23 of 84 against leg 1's SHORT, was on the day's best
leg at +1.6746%. Its strongest agreement, 84 of 84 at leg 2, produced +1.0082%.
IT REMAINS A GOOD READ AT A BAR. It is not an authority over a trade. DISABLED.

### A28 — THE ws3r DIVERGENCE AS AN OVERRIDE of ws3Mage's extended oob hold

| the reading | verdict |
|---|---|
| as a LEVEL | cannot override. BULLISH from 23:12:50, 0.67 min into a 12.5-min hold, and on for all 17 reversals. All 17 share one floater bar, 22:44:15 |
| as a 1.5-MIN TRAJECTORY | turns positive at 23:19:30 - 0.83 min AFTER the price low and 0.50 min BEFORE the x-cross, and 6.67 min before ws3Mage's own confirmation. The slope reads only past bars, so it is causal |

THE WINDOW IS NARROW, not a plateau: 0.5 min and 1.0 min both fire BEFORE the price low, at
23:13:20 and 23:16:25. Only 1.5 and 2.0 min land after it. And the rising state is not sticky - the
1.5-min change goes negative again at 23:23:00 and 23:28:00, so a release must latch once.
THE 1.5 MIN WAS READ OFF THIS LEG. One leg.

### A29 — THE ws3r DIVERGENCE POPULATION, Joe's 1016 spec

ws3Mage reverses AND all 12 of ws1Mage..ws12Mage are oob AND `jig.anchor_floater` fires on ws3r
with the matching verdict. 2026-07-11 to 2026-07-22.

| the population | value |
|---|---|
| qualifying bars | 407 |
| EPISODES, keyed on the shared next-favourable-swing bar | 52 |
| days covered | 12 of 12 |
| median MAE% | 0.5664% |
| median MFE% | 0.8947% |
| median MFE over MAE | 1.60 |
| mean realised | +0.9993% |
| winners | 43 of 52, 82.7% |
| LONGs | 29, mean +0.8950% |
| SHORTs | 23, mean +1.1308% |

| k of 12 oob | episodes | median MFE over MAE | mean realised | winners |
|---|---|---|---|---|
| 12, his spec | 52 | 1.60 | +0.9993% | 82.7% |
| 9 | 85 | 2.57 | +1.0521% | 81.2% |
| 4 | 129 | 2.46 | +0.9726% | 82.2% |

TWO LIMITS, both stated to Joe:
  1 THE REALISED COLUMN IS THE MFE BY CONSTRUCTION. The exit is the next favourable swing pivot and
    at a favourable pivot the price IS the extreme. The Jig labels this frame NON-CAUSAL. The usable
    figure is the 1.60 median MFE-over-MAE, a shape, not a P&L.
  2 CONDITION 2 IS NOT DOING WORK. All-twelve cuts 129 episodes to 52 with no per-episode gain.
  3 THIS IS THE FULL 12 DAYS, not a held-out half.

### THE KNOBS ADDED 1015/1016

| knob | value | whose |
|---|---|---|
| the standdown after a trade prints | 48 bars = 4 min | Joe 1016. His logic, verbatim: *"if the pivot is still pivoting after 4 minutes then there's a lot of trading activity happening, which might indicate the end of a larger cycles momentum"*, and *"untested, possibly unsound"* |
| the same-target cap | 2 trades | Joe 1015 |
| the turn-predictor gate | ws1Mage same-side oob at the fire bar | Joe 1015 |
| the non-oob band | DISABLED | Joe 1016 |

The standdown earned its keep on leg 4: it suppressed three ws5Mage flicker triggers at 22:12:35,
22:13:30 and 22:13:55.

### NOT DECIDED, added 1015/1016

| # | the gap |
|---|---|
| 31 | WITHDRAWN. `LIN_LASTMILE_MAX_GAP` never closed anything - it ends the lineage walk, which is confluence |
| 32 | the pyramid's two members were different kinds, cp-sourced and exhaustion-sourced. Whether "max 2 same-target" means 2 of any kind or 2 per kind |
| 33 | the ws5Mage oob trigger has no hold. Six entries in six minutes on leg 4, bouncing 82.00 to 86.32 |
| 34 | the turn-predictor was already 5 of 5 at leg 4's start bar. Whether a leg may open on a conjunction that predates it |
| 35 | which established mech owns the exit. The ws5x race won legs 1-3, lost leg 4 as first measured, and won it once the anchor was corrected |
| 36 | the sequence held on 3 of 4 legs. Whether the conjunction is a PRECONDITION for the x-cross or just usually earlier |
| 37 | the ws3r divergence override - not ruled out. A28 |

## J. 1016 — the offsets sweep, and the g15Mage sampling idea

### J1. forced-seam vs raw, 420 arms, +A and +B over 3.0 to 13.0 min step 0.5
Joe: *"sweep the 2 forward timestamps, and sweep forced-seam vs raw. from 3 to 13, steps 0.5"*.
Control row raw +5.0/+10.0 reproduced +9.7570% on 07-22 — no cache drift.

    arms matching 4 of his 4 named bars   raw 26   forced seam 0
    arms matching 3 of 4                  raw 67   forced seam 0
    best 07-22 gross                      raw +13.1747%   seam +12.4495%
    arms with a collapsed read            —        seam 115 of 210

FORCED SEAM IS OUT. Snapping each read DOWN to the 5-minute grid is the only causal direction
(snapping up reads past `known_at`), and in 115 of 210 arms both offsets land in the same 5-minute
block, so the second difference is identically 0 and the verdict is forced to `reverse`. No seam
arm reaches even 3 of his 4 named bars at any offset pair in 3.0-13.0.

### J2. 94 built days, 2026-07-03 to 2026-10-04 — the offsets do not separate
The 12-day window put +6.5/+8.5 first at +25.9011% against the banked +14.9819%. 07-21 and 07-22
alone gave that arm +26.9620% — 104% of its total, the other 10 days netting -1.0609%. On all 94
days the ranking collapses:

    the 28 arms span +374.5005% to +437.6942%   a 16.9% spread on the mean
    win rate                                     69.6% to 71.0%
    days positive                                59 to 64 of 94
    +6.5/+8.5, the 12-day leader                 9th, +423.2880%
    +5.0/+10.0, BANKED                           6th, +425.9001%
    +7.5/+10.0, his own pair                     5th, +431.3323%
    +7.5/+9.5                                    1st, +437.6942%

NO KNEE. Gross cannot pick an arm. The only anchor left is his own four named bars, where the
banked +5.0/+10.0 scores 2 of 4 and every arm in the table above scores 4 of 4.
PROPOSED, NOT APPLIED: +7.5/+9.5 — his own +A value, 4 of 4 on his bars, 1st of 94 days.

### J3. the g15Mage ib-cross sampling idea — HIS BARS ARE ON THAT GRID
Joe: *"instead of a fixed width, collect samples on each g15Mage crossing back to ib (on the target
side). the logic: we're sampling at locations that are consistent within the market's cycles -this
needs an arm - it can come from ws5Mage crossing to target-side oob"*.

The producer already exists: `jig.oob_ib_cross` (Joe 0806), which returns (cross, conf, side) with
conf = the bar the cross is knowable. NO NEW PRODUCER NEEDED.

Armed at the ws5Mage HIGH-oob entry 2026-07-22 00:02:10, at the oob fence 85/15 with xwob 4 bars:
his two named continuance bars ARE g15Mage HIGH->ib crosses, exact to the second.
    cross  8   2026-07-22 00:35:00   his named continuance
    cross  9   2026-07-22 00:55:00   his named continuance
The ex-fence 83/17 gives 00:35:20 instead, so the OOB fence is the one that reproduces him.

    the pair STARTING at his 00:35   continuance 20 of 30   +2.59
    the pair ENDING   at his 00:35   reverse      6 of 30   -2.63
    the pair STARTING at his 00:55   continuance 30 of 30   +3.84
    the pair ENDING   at his 00:55   continuance 20 of 30   +2.59
So the FORWARD reading matches both of his bars and the backward reading matches one.

WHAT IT DOES NOT GIVE: a reverse near his ~01:08. The next cross after 01:09:40 is 01:29:15, so the
forward reading's reverse is knowable 2026-07-22 01:29:30 — 11 min past the 01:18:15 he named.
THE WAIT IS UNBOUNDED: 00:56:30 to 01:09:40 is 13.2 min, 01:09:40 to 01:29:15 is 19.6 min. The
banked mech's `known_at` is a fixed +10 min. No cap applied — Joe has not specified one.
The arm->cross reading is continuance on 13 of 13 crosses and discriminates nothing.

NOTHING BUILT. Six gaps are open and are Joe's; they are listed in section C.

### J4. 1016 — net of Bybit fees and slippage. THE RANKING INVERTS
Joe: *"now's a good time to include bybit and slippage drag and report a net. slippage is proven,
it's in the transcript somewhere"*. Located, nothing invented:

    0.1975% / trade  BANKED. 2 x 5.50 bps taker + 8.75 bps slippage RT at 22,000 coins
                     docs/octo-freedom/1005_knobs.md:39, docs/strat-3-r-oob/spec.md:77,
                     docs/mage_cascade_findings.md:307. "ONE orderbook measurement applied flat"
    0.177%  / trade  taker/taker measured live: fees 0.110% + slip 0.067% (3.35 bps/side,
                     project_o9live_desync_fix) - docs/arm_delay_book.md:117-128
    0.108%  / trade  taker/maker.  0.040% / trade  maker/maker. Same table
    16.06 USDT       flat dollar drag per trade at 22,000 coins - strat-3-r-oob/spec.md:78
TWO MEASURED SLIPPAGE FIGURES EXIST AND THEY DIFFER: 8.75 bps RT (banked) against 6.70 bps RT
(3.35/side, live). The banked, more conservative one is the headline below. NOT RECONCILED.

NET ON THE BANKED 0.1975%, 94 days. Drag gets its own column and its own dollar total.
    arm                                   gross       trades  drag      %gross  NET
    g15 ws5/fwd/ex/xwob1/step1          +399.7394%    1143  225.7425%   56.5%  +173.9969%
    g15 ws5/back/ex/xwob1/step1         +398.6336%    1151  227.3225%   57.0%  +171.3111%
    g15 ws5/back/ex/xwob1/step2         +386.6211%    1139  224.9525%   58.2%  +161.6686%
    FIXED +7.5/+9.5 proposed            +437.6942%    1539  303.9525%   69.4%  +133.7417%
    momxfer ws7,8,9 count2 true/rev/evt +327.6961%     989  195.3275%   59.6%  +132.3686%
    FIXED +5.0/+10.0 BANKED             +425.9001%    1520  300.2000%   70.5%  +125.7001%

THE GROSS RANKING WAS WRONG. On gross the banked fixed arm beat Joe's g15 grid by +26.16 pp; on net
the g15 grid beats it by +48.30 pp. Drag is 56.5% to 70.5% of gross, so the fixed arms' extra 396
trades do not pay for themselves. Joe's g15Mage ib-cross idea is the best NET arm measured.

HIS OPPOSING-SIDE VARIANT IS LOSS-MAKING NET: +81.37% to +163.96% gross against ~206-210% of drag,
so -105.93% to -125.87% net across all 16 of its arms.

THE CONCLUSION IS CONDITIONAL ON THE FILL MODEL. Under maker/maker the ordering flips back - the
fixed arm is +376.13% against the g15 grid's +354.02%, because 396 extra trades cost little when
drag is 0.040%. Post-only entry is recorded at docs/arm_delay_book.md:128 as *"the single largest
untested lever in this work"*, and it changes no signal.

### J5. 1016 — the causality repair, and `veto-on-momentum` banked

**THE CAUSALITY REPAIR.** Joe: *"repair the lookahead as needed"*. Found by the first dev-cache
test: the x-cross is searched BACKWARD from the conjunction fire, so its confirmation bar can sit
earlier than the fire — and an unheld turn-predictor event was stamped there. 2026-08-24 10:28:05
was recorded 26 bars = 130 s before its own fire at 10:30:15, and it opened a real trade.
The stamp now takes the LATER of the cross confirmation and the fire, the hold's start bar takes it
too, and an assert stops the run if any event is ever stamped before its own fire. Silent on all 94.

    gross  +399.7394% -> +408.8044%   trades 1143 -> 1142   net +173.9969% -> +183.2594%

IT WENT UP. I predicted a drop from the one trade I had looked at and was wrong — starting those
trades late means starting at a price that has already moved, and on balance it had moved the
machine's way. One trade is not a sample, which I had already been told twice the same day.

**`veto-on-momentum` — JOE NAMED IT.** *"the ws3 ws4 ws5 lines that we've chosen for the new
`veto-on-momentum`"*. An exit-side mech: the verdict's power to close the opposite side is
suspended while ws3r/ws4r/ws5r are travelling against it; the trade rides ws5r; the handover fires
when ws5Mage reaches the riding trade's target-side oob; bounce-pred walks and its reverse is the
exit. Lineage decides nothing — Joe: *"that was banning lineage as a decision route"*.

    gross  +408.8044% -> +423.4278%   trades 1142 -> 1146   net +183.2594% -> +197.0928%
    the veto fired 35 times over the 94 days

THE DRAWDOWN DID NOT MOVE, AND THAT IS WHAT HE ASKED IT FOR. mean MAE 1.3075% -> 1.3104%, worst MAE
15.3586% unchanged, trades over 5% MAE 51 unchanged, worst day -15.4539% unchanged. It is a GROSS
mech. The 2026-08-22 02:07:15 trade still takes its 5.78% adverse excursion.

**HIS PASS-50 CLAIM, MEASURED AND HELD.** *"it is very rare for a ws4r and ws5r line to leave its
source oob and then reverse and return to source oob without passing 50 first"*. My first count said
55-75% and called it the opposite way; that count treated fence jitter as a departure - half of its
"episodes" lasted 15 to 55 seconds. With his own two filters (a minimum time out, and a dwell so a
spike cannot count as a return) the rate is 9.3% at a 5-minute minimum. The decisive evidence: the
`passed 50` count is IDENTICAL at every minimum-time-out setting, so the filter never removes an
episode that passed 50 - every one it drops is a no-50 return.

**THE FLIP WAS MEASURED AND REJECTED.** Joe asked how many signals would do better flipped. The
pattern fires on 36 of 2799 events = 1.29% at a 20-min lookback, and flipping is a coin toss on
money (39.8% to 52.8% better across the lookbacks) while halving mean MAE. At 30 and 60 min it
destroys the gross: +21.19% -> +1.56%, +65.63% -> +25.50%. Holding beat both on his own example:
+10.17% gross with 1.70% MAE, against taking it (+6.56%/5.78%) and flipping it (+0.01%/0.24%).

**TERMINOLOGY FIXED, Joe 1016:** *"its "high oob" and "low oob". board refers to the full range
(0 to 100 for r, unlimited for MAge)"*. `low board` / `high board` / `target board` replaced with
`low oob` / `high oob` / `target-side oob` across 10 files and 20 lines. HIS SEVEN VERBATIM QUOTES
WERE NOT REWRITTEN - each now carries a note giving the current term. The source of the error was my
own memory file, named for the wrong word, which spread it into 9 repo files.

**THE `dev-cache`, JOE NAMED IT:** *"when I need this rebuilt for another window, I'll refer to it
as our `dev-cache`"*. `1005_scoring/_win3.py`. 0.24 s to load against a ~250 s rebuild; 548 arrays
over a 51,840-bar window; keyed on the window plus the banked knobs with a control re-checked on
load. Its first test found the causality fault above.
