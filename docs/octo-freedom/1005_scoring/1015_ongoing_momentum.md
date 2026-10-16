# 1015 — ongoing momentum on a BB%B line, and Joe's Mage-convergence reframe

## The scale question Joe raised

Joe 1014: *"I don't know how ex-fence works in a world that isn't normalised to a stochrsi K line"*.

`optimus9/constants.py`: *"A line is rescaled to [RSI_OVERSOLD, RSI_OVERBOUGHT], THEN OOB-detected
at [BOUNDARY_LO, BOUNDARY_HI]"* — RSI_OVERSOLD 30, RSI_OVERBOUGHT 70, oob 15/85.

Measured ranges, 2026-07-22 13:30–14:20:

| line | range | is the 83/17 ex-fence meaningful on it |
|---|---|---|
| ws1r | 1.44 to 98.08 | yes — r is rescaled then oob-detected |
| ws1Mage | 29.99 to 111.97 | no — unbounded |
| ws1x | −43.61 to 157.25 | no — unbounded |

So **ex-fence is an r fence** (`momo_fence_r` = 17 r-points, giving 83/17). Any read on Mage or x
must be a cross, a turn, or a rank inside the line's own range — never a level.

## THE BASE RATE — "will this line run to ex-fence?"

Population: every bar in 2026-07-11 00:00 to 2026-07-22 23:59:55, 207,360 bars, 5 s grid.
Target: does ws{t}r reach 83 before falling back under 50. Trial: the line is in the band and
rising over 12 bars (60 s).

| where the line already is | the rate to beat | spread ws1 to ws30 |
|---|---|---|
| 80–83, rising | ~72% | 63.3% to 78.5% |
| 70–80, rising | ~47% | 37.8% to 56.1% |
| 60–70, rising | ~34% | 26.0% to 43.7% |
| 50–60, rising | ~21% | 16.9% to 34.7% |

Level does nearly all the work; the timeframe barely matters.

The episode form of the same question — ws{t}r crosses 50, does it reach the ex-fence before
crossing 50 back — is far lower, because a 50-cross is mostly flicker (failed rides have a median
best of 51–54):

| line | HIGH rides | reached 83 | rate | LOW rides | reached 17 | rate |
|---|---|---|---|---|---|---|
| ws1 | 1925 | 495 | 25.7% | 1925 | 531 | 27.6% |
| ws4 | 827 | 121 | 14.6% | 826 | 142 | 17.2% |
| ws10 | 513 | 51 | 9.9% | 512 | 48 | 9.4% |
| ws30 | 205 | 18 | 8.8% | 205 | 22 | 10.7% |
| ws60 | 133 | 7 | 5.3% | 133 | 12 | 9.0% |

## WHICH SCALE-FREE READ BEATS THE BASE RATE

Same population, split one feature at a time. Level band 70–80, rising.

| line | base | n | ws4–ws12 Mage rising, 7+ | n | its own Mage in the top 10% of its own 720-bar range | n | ws4–ws12 Mage joint turn, 5+ set a 720-bar max in the last 24 bars | n | its own x over its own Mage | n |
|---|---|---|---|---|---|---|---|---|---|---|
| ws4 | 48.6% | 8496 | 47.4% | 7052 | 69.9% | 2513 | 66.0% | 1539 | 58.0% | 6010 |
| ws6 | 44.1% | 7694 | 43.4% | 6829 | 59.1% | 2110 | 60.0% | 1111 | 52.8% | 5244 |
| ws8 | 37.8% | 8266 | 37.1% | 7362 | 61.4% | 2166 | 59.9% | 1228 | 46.4% | 5545 |
| ws10 | 49.1% | 9354 | 48.4% | 8512 | 68.2% | 1865 | 72.8% | 1041 | 54.8% | 6255 |
| ws12 | 42.5% | 9115 | 41.1% | 8447 | 59.0% | 1163 | 55.0% | 776 | 48.3% | 5765 |

**"The band rising together" adds nothing** — it is at or below base in all 10 cells. Measured
before Joe's reframe arrived, and it is independent evidence against the matryoshka reading.

What works: a line's own position inside its own recent range, and the band's joint turn.

## JOE'S REFRAME, 1015

His words: *"maybe the mages converging (what we've been calling large-leg) is not about martyoshka
(smaller TF leading larger TF), but instead it's about trusting that all of the ws{>1}Mages will
continue to the same point. -we trust it because the ws1Mage never 'dips' past 50
(counter-target-side) in our 14:06 example. a dip past 50 (counter-target-side) is a mostly-correct
sign of impending weakness and reversal -instead of seeing a dip, we see all of the Mages reversing
inside the same high oob window, and at least 2 TFs' r's are infence to prove the weakness"*, and
*"one thing that stands out is the BEARISH divergence on ws1r, anchored on the final x-cross under
Mage at 14:06"*.

### Test 1 — the ws1Mage dip

| what | value |
|---|---|
| bars with ws1Mage under 50, 13:00–14:10 | 108 of 841 |
| ws1Mage minimum 13:00–14:10 | 13.66 at 13:01:30 |
| ws1Mage minimum 13:37–14:07:05 | **70.10** at 13:56:35 |

Holds inside the ride. The sub-50 bars are 13:00:00–13:12:55, 24 min before it starts.

### Test 2 — the shared high-oob window

| line | the bar it tops out, 13:00–14:10 | its value there | past oob 85 | its value at 14:06:20 |
|---|---|---|---|---|
| ws2Mage | 13:46:25 | 112.88 | yes | 98.10 |
| ws3Mage | 13:46:25 | 112.85 | yes | 106.64 |
| ws4Mage | 14:06:20 | 113.27 | yes | 113.27 |
| ws5Mage | 14:06:20 | 106.23 | yes | 106.23 |
| ws6Mage | 14:05:55 | 105.37 | yes | 101.83 |
| ws7Mage | 14:06:20 | 106.66 | yes | 106.66 |
| ws8Mage | 14:06:20 | 112.03 | yes | 112.03 |
| ws9Mage | 14:05:55 | 112.97 | yes | 107.36 |
| ws10Mage | 14:06:20 | 113.10 | yes | 113.10 |
| ws11Mage | 14:06:20 | 117.65 | yes | 117.65 |
| ws12Mage | 14:06:20 | 116.14 | yes | 116.14 |

ws4–ws12 reverse inside **25 seconds**. ws2 and ws3 topped **19.9 min earlier** and made a lower
high at 14:06. Every one of the 11 is past oob 85 at its own top, so "past 85" alone separates
nothing.

### Test 3 — the in-fence r count

| candidate bar | n of ws2r–ws12r in-fence (15–85) | which ones | n at or past oob 85 |
|---|---|---|---|
| 13:36:15 | 8 | ws2, ws3, ws7, ws8, ws9, ws10, ws11, ws12 | 3 |
| 13:37:00 | 8 | ws2, ws3, ws7, ws8, ws9, ws10, ws11, ws12 | 3 |
| 13:37:20 | 8 | ws2, ws3, ws7, ws8, ws9, ws10, ws11, ws12 | 3 |
| 13:47:10 | 5 | ws8, ws9, ws10, ws11, ws12 | 6 |
| 13:51:25 | 5 | ws2, ws8, ws9, ws11, ws12 | 6 |
| 14:00:05 | 3 | ws2, ws3, ws12 | 8 |
| 14:06:20 | 3 | ws2, ws3, ws12 | 8 |
| 14:07:05 | 3 | ws2, ws3, ws12 | 8 |

The COUNT does not select 14:06 — the false cp has more in-fence (8 vs 3). WHICH lines does: at
14:06 the in-fence set is ws2 and ws3, the same two whose Mages left the ride at 13:46:25.

### Test 4 — the BEARISH divergence on ws1r at the x-cross

`jig.anchor_floater(ws1r, raw close, dr +1, 14:07:05)`, Joe's 0912 four steps, not reinvented.

| step | bar | ws1r | raw close |
|---|---|---|---|
| anchor | 14:07:05 | 70.76 | 0.13875933 |
| pivot | 13:53:20 | 5.69 | 0.13741056 |
| floater | 13:38:20 | 98.08 | 0.13683466 |

| the verdict | value |
|---|---|
| ws1r, anchor minus floater | −27.32 |
| close, anchor minus floater | +0.00192467 = +1.4066% |
| fired | 1 |
| verdict | BEARISH |

The floater at 13:38:20, ws1r 98.08, IS the top of the hill the false cp sat on.

`jig.divergence`, the oob-episode route, does NOT fire at 14:06 — ws1r is 70.76 there, under oob
85, so no HIGH episode exists. It fires at 13:10:05, 13:39:55 and 13:40:55 instead. Only the
anchor_floater route anchored on the x-cross catches the 14:06 one.

## THE 48 CANDIDATE x-CROSSES, 07-22 13:20–14:30

ws1x crosses under ws1Mage 48 times. The level count does not pick 14:07:05 — 13:51:25 and
13:56:10 also sit at 8 of 11 past the high ex-fence, earlier. At 13:37:00 all 11 of ws2r–ws12r
are still rising over the last 5 min, and ws4Mage–ws12Mage sit at 35% to 47% of the high they go
on to make.

## NOT DECIDED — the concretions in the reframe

1. which lines are "all of the ws{>1}Mages" — ws2 and ws3 top 19.9 min early; ws4–ws12 is the set
   that converges
2. the width of "the same high oob window" — 25 s for ws4–ws12, 19.9 min if ws2/ws3 are in
3. what "high oob" means on an unbounded Mage — 85 was used and separates nothing here
4. the lookback over which "ws1Mage never dips past 50" is tested — a dip exists 24 min earlier
5. which TFs count toward "at least 2 TFs' r's are infence", and that the count is a floor, not
   the selector

## JOE'S BOUNCE THEORY, 1015

His words: *"the critical path is definitely the higher TF mages. I think the trick is to find the
TF that is not bouncing on the boundary (like ws1 is for ~35 minutes) -my theory: the higher the TF
Mage is, the less it bounces, and the closer we are to the pivot. I have no way to prove that on
TV's coarse view, but it feels logical given that ws1,2,3,4Mages are visibly bouncing on the
charts"*.

A BOUNCE = one crossing of the oob boundary 85 (high) or 15 (low), either direction. No knob.

### Claim 1, "the higher the TF, the less it bounces" — HOLDS, 12-day base rate

2026-07-11 00:00 to 2026-07-22 23:59:55, 207,360 bars, 5 s grid, 288.0 hours.

| line | crossings of 85 | per hour | crossings of 15 | per hour | both per hour |
|---|---|---|---|---|---|
| ws1Mage | 3007 | 10.44 | 3512 | 12.19 | 22.64 |
| ws2Mage | 2090 | 7.26 | 2614 | 9.08 | 16.33 |
| ws3Mage | 1740 | 6.04 | 1948 | 6.76 | 12.81 |
| ws4Mage | 1544 | 5.36 | 1816 | 6.31 | 11.67 |
| ws5Mage | 1440 | 5.00 | 1626 | 5.65 | 10.65 |
| ws6Mage | 1210 | 4.20 | 1414 | 4.91 | 9.11 |
| ws7Mage | 1086 | 3.77 | 1362 | 4.73 | 8.50 |
| ws8Mage | 1038 | 3.60 | 1174 | 4.08 | 7.68 |
| ws9Mage | 946 | 3.28 | 1236 | 4.29 | 7.58 |
| ws10Mage | 874 | 3.03 | 1086 | 3.77 | 6.81 |
| ws11Mage | 800 | 2.78 | 1174 | 4.08 | 6.85 |
| ws12Mage | 733 | 2.55 | 1012 | 3.51 | 6.06 |
| ws15Mage | 655 | 2.27 | 910 | 3.16 | 5.43 |
| ws20Mage | 457 | 1.59 | 744 | 2.58 | 4.17 |
| ws30Mage | 285 | 0.99 | 646 | 2.24 | 3.23 |
| ws45Mage | 359 | 1.25 | 718 | 2.49 | 3.74 |
| ws60Mage | 241 | 0.84 | 670 | 2.33 | 3.16 |

Monotonic from 22.64/h at ws1 to 3.16/h at ws60, with two small inversions (ws11 vs ws10,
ws45 vs ws30).

### Claim 1 on the 07-22 ride itself — DOES NOT HOLD

Crossings of Mage 85 in 13:30–14:10, 480 bars = 40 min.

| line | crossings of 85 | its last crossing before the pivot 14:06:20 | minutes before the pivot | direction |
|---|---|---|---|---|
| ws1Mage | 16 | 2026-07-22 14:04:35 | 1.75 | up through 85 |
| ws2Mage | 18 | 2026-07-22 14:04:05 | 2.25 | up through 85 |
| ws3Mage | 5 | 2026-07-22 13:40:55 | 25.42 | up through 85 |
| ws4Mage | 31 | 2026-07-22 13:57:35 | 8.75 | up through 85 |
| ws5Mage | 5 | 2026-07-22 14:03:05 | 3.25 | up through 85 |
| ws6Mage | 11 | 2026-07-22 14:04:05 | 2.25 | up through 85 |
| ws7Mage | 13 | 2026-07-22 14:04:05 | 2.25 | up through 85 |
| ws8Mage | 9 | 2026-07-22 14:03:05 | 3.25 | up through 85 |
| ws9Mage | 13 | 2026-07-22 14:03:05 | 3.25 | up through 85 |
| ws10Mage | 15 | 2026-07-22 14:03:05 | 3.25 | up through 85 |
| ws11Mage | 13 | 2026-07-22 14:02:50 | 3.50 | up through 85 |
| ws12Mage | 21 | 2026-07-22 14:03:00 | 3.33 | up through 85 |
| ws15Mage | 3 | 2026-07-22 14:03:05 | 3.25 | up through 85 |
| ws20Mage | 0 | none in 13:30–14:06:20 | - | - |
| ws30Mage | 0 | none | - | - |
| ws45Mage | 0 | none | - | - |
| ws60Mage | 0 | none | - | - |

ws4Mage bounces the MOST of all 17 lines, 31 times. ws1 at 16 crossings over a 34.6-min span is
the ~35 minutes Joe read off the chart.

ws20Mage to ws60Mage never reach 85 in this window at all — at the pivot they sit at 78.53, 68.00,
60.88, 48.19. The band that converges is ws1 to ws15, NOT "the higher TFs".

Every one of the 13 lines that does reach 85 has its last crossing UP through 85, and ten of them
land inside 14:02:50–14:04:35. They enter the window together and none leaves before the pivot.

### Claim 2, the bounce count AS A PREDICTOR — HOLDS on the ex-fence outcome

At every bar ws{t}Mage crosses UP through 85, count its crossings of 85 in the preceding 360 bars
(30 min), then measure whether ws{t}r reaches 83 before falling under 50. Causal on the split — the
count only looks back.

| line | bounces | n events | reaches the ex-fence |
|---|---|---|---|
| ws1 | 0 | 173 | 45.1% |
| ws1 | 1-2 | 179 | 40.8% |
| ws1 | 3-5 | 202 | 33.2% |
| ws1 | 6-10 | 441 | 30.2% |
| ws1 | 11+ | 509 | 19.3% |
| ws2 | 0 | 127 | 55.1% |
| ws2 | 1-2 | 130 | 47.7% |
| ws2 | 3-5 | 137 | 40.1% |
| ws2 | 6-10 | 310 | 25.5% |
| ws2 | 11+ | 341 | 17.9% |
| ws3 | 0 | 99 | 62.6% |
| ws3 | 1-2 | 110 | 48.2% |
| ws3 | 3-5 | 114 | 41.2% |
| ws3 | 6-10 | 254 | 32.7% |
| ws3 | 11+ | 293 | 16.4% |
| ws4 | 0 | 85 | 49.4% |
| ws4 | 1-2 | 100 | 42.0% |
| ws4 | 3-5 | 111 | 29.7% |
| ws4 | 6-10 | 208 | 33.2% |
| ws4 | 11+ | 268 | 17.2% |
| ws6 | 0 | 64 | 37.5% |
| ws6 | 1-2 | 77 | 31.2% |
| ws6 | 3-5 | 89 | 28.1% |
| ws6 | 6-10 | 160 | 38.8% |
| ws6 | 11+ | 215 | 19.5% |
| ws8 | 0 | 51 | 37.3% |
| ws8 | 1-2 | 60 | 30.0% |
| ws8 | 3-5 | 82 | 20.7% |
| ws8 | 6-10 | 145 | 28.3% |
| ws8 | 11+ | 181 | 13.8% |
| ws10 | 0 | 42 | 33.3% |
| ws10 | 1-2 | 49 | 28.6% |
| ws10 | 3-5 | 63 | 23.8% |
| ws10 | 6-10 | 100 | 25.0% |
| ws10 | 11+ | 183 | 21.3% |
| ws12 | 0 | 31 | 45.2% |
| ws12 | 1-2 | 43 | 32.6% |
| ws12 | 3-5 | 54 | 18.5% |
| ws12 | 6-10 | 98 | 21.4% |
| ws12 | 11+ | 140 | 25.0% |
| ws15 | 0 | 31 | 32.3% |
| ws15 | 1-2 | 36 | 22.2% |
| ws15 | 3-5 | 52 | 13.5% |
| ws15 | 6-10 | 71 | 22.5% |
| ws15 | 11+ | 137 | 21.9% |
| ws20 | 0 | 23 | 52.2% |
| ws20 | 1-2 | 35 | 31.4% |
| ws20 | 3-5 | 47 | 21.3% |
| ws20 | 6-10 | 62 | 29.0% |
| ws20 | 11+ | 61 | 19.7% |
| ws30 | 0 | 18 | 61.1% |
| ws30 | 1-2 | 27 | 37.0% |
| ws30 | 3-5 | 29 | 34.5% |
| ws30 | 6-10 | 37 | 29.7% |
| ws30 | 11+ | 31 | 25.8% |

Every line: 0 bounces beats 11+ bounces. Monotonic across all five bins on ws1, ws2, ws3, ws8,
ws20, ws30.

The zero-bounce bin is thin above ws10 — n 31, 31, 23, 18 on ws12, ws15, ws20, ws30.

### Claim 2b, "the closer we are to the pivot" — DOES NOT HOLD on the bounce count

Median bars from the oob entry to that line's own Mage top.

| line | bounces | n events | median bars to the Mage top | minutes |
|---|---|---|---|---|
| ws1 | 0 | 173 | 48 | 4.0 |
| ws1 | 11+ | 509 | 28 | 2.3 |
| ws3 | 0 | 99 | 79 | 6.6 |
| ws3 | 11+ | 293 | 69 | 5.8 |
| ws8 | 0 | 51 | 59 | 4.9 |
| ws8 | 11+ | 181 | 95 | 7.9 |
| ws10 | 0 | 42 | 62 | 5.2 |
| ws10 | 11+ | 183 | 102 | 8.5 |
| ws12 | 0 | 31 | 69 | 5.8 |
| ws12 | 11+ | 140 | 188 | 15.6 |
| ws30 | 0 | 18 | 29 | 2.4 |
| ws30 | 11+ | 31 | 73 | 6.1 |

Mixed. On ws8, ws10, ws12 and ws30 it runs the OTHER way - a clean entry has MORE run left, which
is the same fact as its higher ex-fence rate.

### Claim 2c, "closer to the pivot" measured on the Mage TOP instead — HOLDS

| what "closer to the pivot" is measured on | does the higher TF win |
|---|---|
| the line's own Mage top vs the band's pivot 14:06:20 | yes - ws4-ws12 top at 14:05:55/14:06:20; ws1 tops 26.5 min early at 13:39:50; ws2/ws3 20 min early at 13:46:25 |
| the line's last boundary crossing before the pivot | no - ws1 at 1.75 min and ws2 at 2.25 min are the CLOSEST; ws10-ws15 sit at 3.25-3.50 min |

## NOT DECIDED - the concretions in the bounce theory

6. the lookback over which bounces are counted. 360 bars = 30 min was used because Joe said
   "~35 minutes"; he has not named a number
7. what "the pivot" is - the line's own Mage top, the band's joint top, or the last boundary
   crossing. The three disagree and claim 2 flips sign between them
8. whether the bounce count is read on the line being judged, or on ws1 as the noise reference

## POI — Joe's tag, 1015. Two open points, not built, not knobbed, not stubbed.

Joe 1015, on the in-fence pair being the two lines that left the ride: *"ooohhh - you've reminded
me that we have mom-xfer up our sleeve. I feel like it did a good job for coil - now we can test
mom-xfer on ws{some TF}Mage excursions, rather than just the coiled events / we should be bringing
the octo-sigs back into the walk. not just yet, but keep it up our sleeve for later. tagged as
`POI` please"*.

| POI | what it is |
|---|---|
| mom-xfer on Mage excursions | run `mom_xfer` against ws{some TF}Mage excursions instead of only coiled events. The TF is unnamed |
| octo-sigs back into the walk | HELD at Joe's word - *"not just yet"* |

`mom_xfer` as it stands today, from `docs/22_go_20260921/README.md`: the first bar after
`wsl_sig_utc` where `mom_xfer.count_min` or more of the `momtf_dr` set have left it at the same
bar; the walk ends at the dr flip.
  `mom_xfer.count_min` = 2 timeframes, banked in `wsf_dtf_v3_config` v8. Joe 0920: *"2 is
  arbitrary. the more TFs I see leaving the dr mom, the more comfortable I'll be"*.
  `momtf_dr` = which of ws10, ws11, ws12 are momentum-true at `wsl_sig_utc` at the row's own dr.

WHY IT CONNECTS HERE. At the 07-22 14:06:20 pivot, exactly 2 of ws2r-ws12r are off the high end
other than ws12 - ws2r at 48.02 and ws3r at 50.18 - and those are the same two lines whose Mages
left the ride 19.9 min earlier at 13:46:25. Two timeframes leaving at the same bar is the shape
`mom_xfer.count_min` 2 already counts.

NOT DECIDED for this POI:
9.  which TF's Mage excursion mom-xfer reads - Joe wrote "ws{some TF}Mage"
10. whether `momtf_dr`'s ws10/ws11/ws12 membership stays, or becomes the ws2-ws12 band this
    measurement used
11. whether an excursion is the oob entry, the oob exit, or the Mage top

## GAP 7 RULED — Joe 1015: *"what 'closer to the pivot' is / the top or bottom pxs value in a swing"*

So the pivot is a PRICE pivot. Producer: `optimus9.compute.swing_detect.find_pivots` on the raw
close, pct 0.9 - his framing *"map the difference between each spike and trough, where the
difference is greater than 0.9%"*, banked as `lp_lr_swing_pct` 0.9. 3487 pivots over the tape.
Flagged NON-CAUSAL in the Jig, so everything below is a DIAGNOSTIC, not a signal.

Knob-free test: each pivot p sits in a leg bounded by its own neighbouring pivots. Inside that leg
take ws{t}Mage's max (H pivot) or min (L pivot); measure the distance from p.

### 14:06:20 IS a price pivot

| pivot | bar | kind | raw close |
|---|---|---|---|
| 591 | 2026-07-22 12:56:55 | L | 0.13483047 |
| 592 | 2026-07-22 14:06:20 | H | 0.13884016 |
| 593 | 2026-07-22 14:55:05 | L | 0.13604148 |
| 594 | 2026-07-22 15:29:30 | H | 0.13779866 |

The leg is 12:56:55 to 14:55:05.

| line | its Mage max inside that leg | at bar | minutes from the price pivot |
|---|---|---|---|
| ws1Mage | 111.97 | 2026-07-22 13:39:50 | -26.50 |
| ws2Mage | 112.88 | 2026-07-22 13:46:25 | -19.92 |
| ws3Mage | 112.85 | 2026-07-22 13:46:25 | -19.92 |
| ws4Mage | 113.27 | 2026-07-22 14:06:20 | +0.00 |
| ws5Mage | 106.23 | 2026-07-22 14:06:20 | +0.00 |
| ws6Mage | 105.37 | 2026-07-22 14:05:55 | -0.42 |
| ws7Mage | 106.66 | 2026-07-22 14:06:20 | +0.00 |
| ws8Mage | 112.03 | 2026-07-22 14:06:20 | +0.00 |
| ws9Mage | 112.97 | 2026-07-22 14:05:55 | -0.42 |
| ws10Mage | 113.10 | 2026-07-22 14:06:20 | +0.00 |
| ws11Mage | 117.65 | 2026-07-22 14:06:20 | +0.00 |
| ws12Mage | 116.14 | 2026-07-22 14:06:20 | +0.00 |
| ws15Mage | 112.20 | 2026-07-22 14:06:20 | +0.00 |
| ws20Mage | 78.53 | 2026-07-22 14:06:20 | +0.00 |
| ws30Mage | 68.00 | 2026-07-22 14:06:20 | +0.00 |
| ws45Mage | 60.88 | 2026-07-22 14:06:20 | +0.00 |
| ws60Mage | 48.19 | 2026-07-22 14:06:20 | +0.00 |

### CLAIM 2 UNDER THE RULING — HOLDS, monotonic, 271 pivots

2026-07-11 00:00 to 2026-07-22 23:59:55.

| line | n pivots | median minutes from the price pivot | mean | within 1 min | within 3 min |
|---|---|---|---|---|---|
| ws1Mage | 271 | 4.58 | 21.29 | 107 | 126 |
| ws2Mage | 271 | 0.67 | 18.62 | 142 | 150 |
| ws3Mage | 271 | 0.08 | 14.12 | 162 | 168 |
| ws4Mage | 271 | 0.08 | 15.12 | 164 | 171 |
| ws5Mage | 271 | 0.08 | 12.42 | 183 | 193 |
| ws6Mage | 271 | 0.08 | 13.51 | 188 | 195 |
| ws7Mage | 271 | 0.08 | 13.51 | 186 | 190 |
| ws8Mage | 271 | 0.08 | 13.71 | 182 | 190 |
| ws9Mage | 271 | 0.08 | 14.28 | 184 | 193 |
| ws10Mage | 271 | 0.00 | 10.74 | 201 | 210 |
| ws11Mage | 271 | 0.00 | 9.96 | 203 | 207 |
| ws12Mage | 271 | 0.00 | 9.17 | 211 | 215 |
| ws15Mage | 271 | 0.00 | 8.73 | 210 | 214 |
| ws20Mage | 271 | 0.00 | 9.07 | 214 | 220 |
| ws30Mage | 271 | 0.00 | 7.64 | 224 | 228 |
| ws45Mage | 271 | 0.00 | 7.82 | 226 | 229 |
| ws60Mage | 271 | 0.00 | 6.28 | 232 | 235 |

The within-1-min count rises at EVERY step, 107 to 232 - 39.5% to 85.6% of 271. Mean distance
falls 21.29 min to 6.28 min.

### CORRECTION to the 1015 bounce entry above

Earlier in this doc: *"The band that converges is ws1 to ws15, NOT 'the higher TFs'"*. That was
measured on boundary crossings, where ws20Mage to ws60Mage never reach 85 on 07-22. On the PRICE
PIVOT measure they are the best of all 17 lines - their extremes sit on the pivot at 78.53, 68.00,
60.88 and 48.19 without ever going oob. Locating the pivot and going oob are separate properties.

### WHAT THIS COSTS TO MAKE CAUSAL

The Mage extreme above is found inside a leg bounded by the NEXT price pivot - future information.
It proves the geometry, it is not a signal. A causal form has to detect that the Mage has already
turned, and the detection lag is unmeasured.

Gap 7 is CLOSED. Gaps 1-6 and 8-11 remain open.

## THE CASCADE — Joe 1015, matryoshka's second chance

His words: *"this is where matryoshka gets a chance to claw back some dignity: you should see the
reversal happen in a cascade from g15Mage to ws2-3Mage"*, then the clarification *"...as they each
cross from oob to ib"*.

THE EVENT IS THE oob->ib CROSS. Producer already in the Jig, not reinvented:
`jig.oob_ib_cross(line, hi, lo, xwob)` -> (cross bar, conf bar, side). oob = v >= hi or v <= lo;
ib = lo < v < hi STRICTLY; a cross is CONFIRMED once ib has held `xwob` bars, so conf = cross +
xwob - 1 is the bar it becomes KNOWABLE. Causal.
  oob 85/15. xwob = `boundary_xwob` 4 bars = 20 s, `wsf_dtf_v3_config` section `ws1mage_rev`,
  Joe 0911: *"use these values, reversal:2, boundary:4. both are knobs"*. It is NOT in
  lazy_g_config, so it is read from the v3 config seed.

LD's first argument is SECONDS: g5Mage = LD(5), g15Mage = LD(15), g30Mage = LD(30),
ws1Mage = LD(60), ws2Mage = LD(120). So the cascade runs small -> large.

### The 07-22 14:06:20 price pivot — g15Mage confirms first of the 11

| line | cross bar (first ib bar) | conf bar (knowable) | lag from the pivot, minutes |
|---|---|---|---|
| g15Mage | 2026-07-22 14:07:10 | 2026-07-22 14:07:25 | +1.08 |
| g30Mage | 2026-07-22 14:08:00 | 2026-07-22 14:08:15 | +1.92 |
| ws1Mage | 2026-07-22 14:08:00 | 2026-07-22 14:08:15 | +1.92 |
| ws2Mage | 2026-07-22 14:08:10 | 2026-07-22 14:08:25 | +2.08 |
| g5Mage | 2026-07-22 14:11:55 | 2026-07-22 14:12:10 | +5.83 |
| ws6Mage | 2026-07-22 14:13:00 | 2026-07-22 14:13:15 | +6.92 |
| ws3Mage | 2026-07-22 14:14:55 | 2026-07-22 14:15:10 | +8.83 |
| ws4Mage | 2026-07-22 14:15:05 | 2026-07-22 14:15:20 | +9.00 |
| ws8Mage | 2026-07-22 14:15:05 | 2026-07-22 14:15:20 | +9.00 |
| ws10Mage | 2026-07-22 14:15:05 | 2026-07-22 14:15:20 | +9.00 |
| ws12Mage | 2026-07-22 14:15:05 | 2026-07-22 14:15:20 | +9.00 |

### ALL 135 H pivots, 07-11 to 07-22 — the lag rises at EVERY step

| line | n pivots | median lag to the conf bar, minutes | mean | conf within 1 min | conf within 3 min |
|---|---|---|---|---|---|
| g5Mage | 135 | 0.50 | 2.11 | 110 | 114 |
| g15Mage | 135 | 0.83 | 3.50 | 83 | 118 |
| g30Mage | 135 | 1.25 | 4.36 | 57 | 114 |
| ws1Mage | 135 | 2.17 | 12.96 | 38 | 82 |
| ws2Mage | 135 | 4.58 | 32.58 | 25 | 51 |
| ws3Mage | 135 | 7.33 | 59.36 | 14 | 37 |
| ws4Mage | 135 | 10.83 | 66.57 | 14 | 34 |
| ws6Mage | 135 | 31.42 | 109.93 | 14 | 33 |
| ws8Mage | 135 | 80.92 | 184.86 | 12 | 25 |
| ws10Mage | 135 | 142.33 | 232.57 | 8 | 14 |
| ws12Mage | 135 | 166.00 | 263.32 | 10 | 16 |

### Who confirms first

| line | times it confirmed first of the 11 | times it confirmed last |
|---|---|---|
| g5Mage | 69 | 0 |
| g15Mage | 33 | 1 |
| g30Mage | 14 | 2 |
| ws1Mage | 3 | 1 |
| ws2Mage | 4 | 3 |
| ws3Mage | 5 | 5 |
| ws4Mage | 0 | 4 |
| ws6Mage | 2 | 9 |
| ws8Mage | 1 | 17 |
| ws10Mage | 1 | 30 |
| ws12Mage | 3 | 63 |

All 135 pivots had a cross on all 11 lines.
  g5 + g15 + g30 confirm first on 116 of 135 = 85.9%.
  ws12Mage confirms last on 63 of 135 = 46.7%.
  g5Mage never confirms last. ws4Mage never confirms first.

### THE TWO READINGS OF MATRYOSHKA, SETTLED SEPARATELY

| reading | verdict |
|---|---|
| the smaller TF leads on ONGOING MOMENTUM | DEAD. `band_up>=7` sits at or below the base rate in all 10 cells |
| the smaller TF leads on the REVERSAL | HOLDS. monotonic over 11 lines, 135 pivots |

### WHAT IS STILL MISSING BEFORE THIS IS A SIGNAL

The lag column above is honest - it walks FORWARD from the pivot. What is NOT measured is the
PRECISION: how often a g15Mage oob->ib confirmation fires when NO price pivot follows. In the
07-22 window g5Mage crossed 5 times in the 16 min before the pivot and g15Mage twice. A cascade
detector needs both halves.

12. the false-positive rate per line - of all oob->ib confirmations, how many are followed by a
    0.9% price pivot. NOT MEASURED, NOT RUN. Joe has not asked for it.

## GAP 12 MEASURED — Joe 1015 *"go for it"*

### The framing error, and its correction

I first measured precision FORWARD: from each oob->ib confirmation, is there an H price pivot
within 3 min AFTER it. Every line and every cascade cell sat at or near the 2.4% random-bar
baseline - best cell 5.1%.

That asks a CONFIRMING detector to forecast. The lag table in this same doc already measured these
confirmations landing 0.83 to 7.33 min AFTER the pivot, so a forward window is structurally near
zero for them by construction. The question a ws1cp needs is the BACKWARD one: when this fires,
has a price top just happened?

Both runs are kept below. The forward table is the wrong question, recorded so it is not re-asked.

### FORWARD (the wrong question) - from each confirmation to the NEXT H pivot

| line | n confirmations | within 1 min | within 3 min | within 10 min | within 30 min |
|---|---|---|---|---|---|
| g5Mage | 3373 | 1.5% | 4.1% | 12.1% | 29.7% |
| g15Mage | 2097 | 1.3% | 4.4% | 12.7% | 29.5% |
| g30Mage | 1455 | 1.0% | 4.8% | 13.3% | 31.8% |
| ws1Mage | 986 | 0.8% | 4.0% | 12.2% | 30.3% |
| ws2Mage | 669 | 1.2% | 4.5% | 13.9% | 32.3% |
| ws3Mage | 547 | 0.7% | 2.6% | 12.5% | 32.4% |
| ws4Mage | 457 | 1.1% | 2.4% | 9.6% | 28.7% |
| ws6Mage | 400 | 1.5% | 5.6% | 14.1% | 33.6% |
| ws8Mage | 328 | 0.9% | 3.7% | 12.3% | 31.7% |
| ws10Mage | 251 | 0.8% | 4.0% | 13.3% | 26.6% |
| ws12Mage | 228 | 1.3% | 3.1% | 9.6% | 25.9% |
| RANDOM BAR BASELINE | 206107 | 0.9% | 2.4% | 7.9% | 23.1% |

### BACKWARD, single line - when it confirms, how long since the last H pivot

| line | n confirmations | median minutes since the last H pivot | within 1 min | within 3 min | within 5 min | within 10 min |
|---|---|---|---|---|---|---|
| g5Mage | 3373 | 80.00 | 3.4% | 3.6% | 3.8% | 6.0% |
| g15Mage | 2097 | 86.42 | 4.1% | 6.6% | 6.7% | 7.0% |
| g30Mage | 1455 | 92.33 | 4.2% | 9.4% | 10.8% | 11.6% |
| ws1Mage | 986 | 97.92 | 4.0% | 9.9% | 13.3% | 18.6% |
| ws2Mage | 669 | 101.67 | 3.9% | 8.8% | 12.9% | 19.6% |
| ws3Mage | 547 | 93.92 | 2.7% | 8.0% | 12.6% | 21.0% |
| ws4Mage | 457 | 83.67 | 3.1% | 9.0% | 13.3% | 22.5% |
| ws6Mage | 400 | 58.42 | 3.5% | 9.8% | 15.0% | 22.8% |
| ws8Mage | 328 | 52.83 | 4.0% | 9.8% | 13.7% | 20.4% |
| ws10Mage | 251 | 36.33 | 3.6% | 7.6% | 12.7% | 22.3% |
| ws12Mage | 228 | 42.71 | 4.5% | 9.0% | 13.1% | 21.2% |
| RANDOM BAR BASELINE | 206748 | 74.58 | 0.8% | 2.4% | 4.0% | 7.9% |

g5Mage is the WORST line backward at 1.5x the baseline, despite being the fastest forward. It
fires 3373 times. g30Mage 3.9x and ws1Mage 4.1x are the best single lines.

### BACKWARD, THE CASCADE AS A CONJUNCTION — JOE'S MECH

His line set, his word *"they each"*. The event is stamped at the bar the k-th of the five
confirms, all k inside span W. Causal - nothing read past the stamp bar.

| k of 5 | span W bars | span minutes | n events | H pivot within 3 min before | precision | lift over 2.4% | recall of the 135 H pivots |
|---|---|---|---|---|---|---|---|
| 5 | 12 | 1.0 | 52 | 15 | 28.8% | 12.0x | 14 of 135 = 10.4% |
| 5 | 24 | 2.0 | 102 | 27 | 26.5% | 11.0x | 25 of 135 = 18.5% |
| 5 | 36 | 3.0 | 127 | 29 | 22.8% | 9.5x | 28 of 135 = 20.7% |
| 5 | 60 | 5.0 | 167 | 29 | 17.4% | 7.3x | 27 of 135 = 20.0% |
| 5 | 120 | 10.0 | 188 | 30 | 16.0% | 6.7x | 30 of 135 = 22.2% |
| 4 | 12 | 1.0 | 197 | 33 | 16.8% | 7.0x | 29 of 135 = 21.5% |
| 4 | 24 | 2.0 | 260 | 49 | 18.8% | 7.8x | 46 of 135 = 34.1% |
| 4 | 36 | 3.0 | 311 | 55 | 17.7% | 7.4x | 51 of 135 = 37.8% |
| 4 | 60 | 5.0 | 326 | 52 | 16.0% | 6.7x | 49 of 135 = 36.3% |
| 4 | 120 | 10.0 | 312 | 41 | 13.1% | 5.5x | 41 of 135 = 30.4% |
| 3 | 12 | 1.0 | 579 | 80 | 13.8% | 5.8x | 67 of 135 = 49.6% |
| 3 | 24 | 2.0 | 662 | 81 | 12.3% | 5.1x | 74 of 135 = 54.8% |
| 3 | 36 | 3.0 | 664 | 76 | 11.5% | 4.8x | 73 of 135 = 54.1% |
| 3 | 60 | 5.0 | 589 | 67 | 11.4% | 4.8x | 64 of 135 = 47.4% |
| 3 | 120 | 10.0 | 384 | 43 | 11.2% | 4.7x | 42 of 135 = 31.1% |

The conjunction beats every single line: 28.8% against ws1Mage's 9.9%.
Relaxing k costs precision and buys recall, monotonically.

### NOT DECIDED

13. k - how many of the five must cross. 5 is the literal reading of *"they each"*
14. the span W - 12 bars (1 min) is the best precision, 24 bars (2 min) the best precision-recall
    pair. Joe has named no span
15. whether the five lines stay g15/g30/ws1/ws2/ws3, or g5Mage joins. g5Mage is the worst single
    line backward, 1.5x, and adding it would add 3373 firings

## THE ONLINE RESEARCH — 1015, Joe offered, I took it

104 agents, 22 sources fetched, 110 claims extracted, top 25 adversarially verified: 9 confirmed,
16 refuted. Everything below is SPEC INTEL for Joe. None of it is a build input - the standing
rule is that the machine is built from his mechanisms only.

### THE FINDING THAT UNDERMINES OUR CASCADE RESULT

Huth & Abergel, "High Frequency Lead/lag Relationships - Empirical facts", Journal of Empirical
Finance 2014, DOI 10.1016/j.jempfin.2014.01.003. Confirmed 3-0, verbatim against the full text,
with an analytic proof in their Appendix B.

| the test | value |
|---|---|
| design | 2 synchronously correlated Brownian motions, rho 0.8, horizon 30,600 s, dt 5 |
| sampling | 2 independent Poisson grids at different intensities, 64 runs |
| true lead-lag | ZERO by construction |
| result | a naive previous-tick cross-correlation estimator makes the MORE FREQUENTLY UPDATED series appear to lead |

OUR EXPOSURE IS DIRECT. The cascade order measured in this doc -
  g5Mage, g15Mage, g30Mage, ws1Mage, ws2Mage, ws3Mage, ws4Mage, ws6Mage, ws8Mage, ws10Mage, ws12Mage
- is EXACTLY the update-rate order. ws12Mage cannot move until its own 12-min bar advances. The
monotonic lag ladder (0.50 min to 166.00 min) may be manufactured by update rate rather than by a
real propagation.

The Hayashi-Yoshida estimator removes the directional artefact but not spurious correlation mass
at non-zero lags.

### THE FINDING THAT RE-SCALES OUR LIFT

Huth & Abergel p.24, FCE (CAC 40 future) as leader against two Euronext Paris stocks. Their
protocol is three-layered: score against random, THEN against the lagger's own autocorrelation,
THEN with the cost of acting charged.

| metric | TOTF.PA | ESSI.PA |
|---|---|---|
| lead-lag directional accuracy | 60.3% | 63.6% |
| autocorrelation-only baseline | 56.7% | 59.0% |
| sample, 44 test days | 226,347 | 241,340 |
| p vs random | ~1e-16 | ~1e-16 |
| p vs autocorrelation | 2e-11 | 3e-7 |
| gross per trade, midquote | +0.40 bps | +0.54 bps |
| NET per trade, spread charged | -2.73 bps | -3.44 bps |
| average spread | 1.88 ticks | 2.83 ticks |

A signal that beat both baselines at p ~ 1e-11 still lost money.

RESTATING OUR OWN NUMBER against the fair baseline, from figures already in this doc:

| baseline | the cascade's 28.8% as a lift |
|---|---|
| random bar, 2.4% | 12.0x |
| ws1Mage alone, 9.9% | 2.9x |

### THE THREE FINDINGS THAT SUPPORT WHAT WE DID

| source | what it establishes | our counterpart |
|---|---|---|
| Ren & Zhou, New J. Phys. 12 (2010) 075030, peer-reviewed open access. 2 Chinese indices + 20 stocks, 1-min bars, ~340,000 points per series, event = return beyond q*sigma for q 2,3,4,5. Tail exponent delta 2.20/2.15 indices, 3.0 +/- 0.3 on 16 of 20 stocks. Hazard prefactor (delta-1) 1.15 to 2.9, strictly positive | recurrence-interval analysis. (a) conditional PDF of the interval given the preceding one, four equal-count bins - intervals CLUSTER, large follow large. (b) conditional hazard DECAYS with elapsed time since the last threshold event, the opposite sign to memoryless Poisson. Only the sign is robust; the functional form is fit-specific | the published analogue of our 30-min 85-crossing count, same sign |
| Nyberg, Lizana & Ambjornsson, Phys. Rev. E 97, 032114 (2018), DOI 10.1103/PhysRevE.97.032114 | for a correlated stationary process the per-step crossing probability depends on the trajectory leading up to it, and the deviation appears in the DISTRIBUTION OF THE NUMBER of crossings, not only the level. Establishes existence of path dependence, never its magnitude | conditioning on our bounce count is formally licensed, not a hack |
| Harman & Zuehlke, J. Economics and Finance 28(2) 2004, 147-154 | on IDENTICAL run data the measured SIGN of duration dependence flipped with the hazard specification: continuous + interval Weibull +0.308 to +0.695 (t 3.903 to 10.749) in all 16 cells; discrete Weibull -0.062 to -0.167 and discrete logistic -0.137 to -0.313, mostly insignificant. The authors decline to name a correct specification | our bounce result is a conditional rate split, not a parametric fit, so it is not exposed. Nothing of ours may become a hazard fit without this check |

### THE PART 1 GAP

No verified source measures continuation-vs-reversion of a bounded oscillator conditioned on a
CAUSALLY AVAILABLE indicator state. The only crypto Bollinger source found (SSRN 5775962,
BTC/USDT 2017-07 to 2022-03) partitions on ex-post calendar epochs - Bear 2018, Accumulation
2018-2020, Bull Run 2020-2021, Distribution 2021-2022 - none knowable at bar time, on 1-minute
bars, long-only, with no hit rates reported. It contains no %B, BandWidth, squeeze, re-crossing,
embedding/pinning or cross-timeframe content.

Our own numbers are the only ones.

### ALSO DOCUMENTED, NOT YET USED

Hayashi & Koike, arXiv:1708.03992 v4, companion peer-reviewed as SIAM J. Financial Mathematics
9:1208-1248 (2018). ONE lead-lag time per dyadic scale band, theta_j, the unique maximizer of a
scale-by-scale cross-covariance; public implementation `wllag` in the R package `yuima`.
  Their NASDAQ vs BATS result, 108 NASDAQ-100 stocks, 21 days, 2268 asset-days, 100 us
  resolution: j=1..3 (0.1-0.8 ms) median theta_j +0.20 to +0.30 ms, NASDAQ leads; j=4..7
  (0.8-12.8 ms) -0.30 to -1.30 ms, BATS leads. ONE AGGREGATE NUMBER HID A SIGN REVERSAL.
  Confirmed 2-1, single unreplicated study.
  The transferable warning: report a per-band lag ladder and test each band's sign.

### NOT DECIDED

16. the update-rate null test on our cascade - run the same cascade-order statistic on a surrogate
    with no true propagation, and see whether the monotonic ladder still appears. NOT RUN. This is
    the audit Huth & Abergel's Appendix B says any fast-leads-slow claim must pass

## GAP 16 MEASURED — the update-rate null test. Joe 1015 *"go"*

Two surrogates, both destroying alignment to the real pivots and both preserving each line's own
firing rate:
  SHIFT   each line's confirmation set rotated circularly inside the window by a random offset.
          Preserves firing rate AND the clustering of confirmations. The primary test.
  RANDOM  the 135 real H pivots replaced by 135 random bars. Preserves the line exactly.
REPS 400 draws per line on the lag ladder, 100 on the order statistic, 200 on the conjunction.
These are diagnostic precision choices, stated.

### CORRECTION to the lag table earlier in this doc

That run indexed "the first event at or after the pivot" by the CROSS bar and reported the CONF
bar. This run indexes by the CONF bar, which is the causal form - the event is only knowable at
conf. Corrected figures, use these:

| line | was | is |
|---|---|---|
| g30Mage | 1.25 | 1.17 |
| ws1Mage | 2.17 | 2.08 |
| ws2Mage | 4.58 | 4.50 |
| ws10Mage | 142.33 | 128.58 |
| ws12Mage | 166.00 | 156.21 |

### RESULT 1 - the clustering near real pivots is REAL on all 11 lines

| line | real median lag, minutes | SHIFT surrogate mean | 5th pct | 95th pct | verdict |
|---|---|---|---|---|---|
| g5Mage | 0.50 | 3.66 | 2.92 | 4.50 | real is SHORTER |
| g15Mage | 0.83 | 7.03 | 5.50 | 8.58 | real is SHORTER |
| g30Mage | 1.17 | 12.36 | 9.75 | 15.26 | real is SHORTER |
| ws1Mage | 2.08 | 22.99 | 17.66 | 28.67 | real is SHORTER |
| ws2Mage | 4.50 | 40.52 | 32.08 | 50.35 | real is SHORTER |
| ws3Mage | 7.33 | 60.34 | 44.58 | 75.68 | real is SHORTER |
| ws4Mage | 10.83 | 76.70 | 57.53 | 97.75 | real is SHORTER |
| ws6Mage | 31.42 | 109.62 | 82.24 | 141.13 | real is SHORTER |
| ws8Mage | 80.92 | 156.63 | 113.29 | 199.44 | real is SHORTER |
| ws10Mage | 128.58 | 206.45 | 166.33 | 251.43 | real is SHORTER |
| ws12Mage | 156.21 | 250.63 | 182.16 | 314.55 | real is SHORTER |

The RANDOM surrogate agrees on all 11: means 3.67 / 7.07 / 12.35 / 23.19 / 40.57 / 58.89 / 76.94 /
109.87 / 159.91 / 206.70 / 256.85, every real value below the 5th percentile.

### RESULT 2 - the ladder's SHAPE is firing rate. MY framing was the artefact.

| line | n confirmations | mean gap between its own confirmations, minutes | real median lag | real lag as a share of its own mean gap |
|---|---|---|---|---|
| g5Mage | 3373 | 5.12 | 0.50 | 0.10 |
| g15Mage | 2097 | 8.24 | 0.83 | 0.10 |
| g30Mage | 1455 | 11.88 | 1.17 | 0.10 |
| ws1Mage | 986 | 17.53 | 2.08 | 0.12 |
| ws2Mage | 669 | 25.83 | 4.50 | 0.17 |
| ws3Mage | 547 | 31.59 | 7.33 | 0.23 |
| ws4Mage | 457 | 37.81 | 10.83 | 0.29 |
| ws6Mage | 400 | 43.20 | 31.42 | 0.73 |
| ws8Mage | 328 | 52.68 | 80.92 | 1.54 |
| ws10Mage | 251 | 68.84 | 128.58 | 1.87 |
| ws12Mage | 228 | 75.79 | 156.21 | 2.06 |

g5Mage, g15Mage, g30Mage and ws1Mage all sit at 0.10 to 0.12. They are EQUALLY well aligned to
pivots and differ only in how often they fire. "g5 leads g15 leads g30 leads ws1" is firing rate,
exactly the Huth & Abergel Appendix B artefact.

### RESULT 3 - the order statistic. only g5Mage's lead beats chance.

| line | real: times it confirmed first of the 11 | surrogate mean of 100 draws | 5th pct | 95th pct | outside the band |
|---|---|---|---|---|---|
| g5Mage | 67 | 46.2 | 39 | 54 | YES |
| g15Mage | 28 | 26.2 | 20 | 35 | no |
| g30Mage | 15 | 17.3 | 12 | 24 | no |
| ws1Mage | 3 | 10.4 | 6 | 16 | YES, BELOW |
| ws2Mage | 5 | 7.2 | 3 | 12 | no |
| ws3Mage | 5 | 5.6 | 2 | 10 | no |
| ws4Mage | 0 | 5.0 | 2 | 8 | YES, BELOW |
| ws6Mage | 2 | 4.1 | 1 | 8 | no |
| ws8Mage | 1 | 3.5 | 1 | 6 | no |
| ws10Mage | 2 | 2.8 | 0 | 6 | no |
| ws12Mage | 2 | 2.4 | 1 | 5 | no |

My earlier "g5 + g15 + g30 confirm first on 116 of 135 = 85.9%" has a chance expectation of
46.2 + 26.2 + 17.3 = 89.7. The excess is real but small, and g15/g30 carry none of it.

### RESULT 4 - JOE'S CONJUNCTION SURVIVES, and strongly

| k of 5 | span W bars | real precision | real n events | surrogate precision mean | 5th pct | 95th pct | surrogate n events mean | verdict |
|---|---|---|---|---|---|---|---|---|
| 5 | 12 | 28.8% | 52 | 14.3% | 0.0% | 70.0% | 1 | TEST UNINFORMATIVE |
| 5 | 24 | 26.5% | 102 | 3.2% | 0.0% | 0.0% | 1 | real is HIGHER |
| 4 | 24 | 18.8% | 260 | 2.5% | 0.0% | 13.7% | 15 | real is HIGHER |
| 4 | 36 | 17.7% | 311 | 2.2% | 0.0% | 8.6% | 31 | real is HIGHER |
| 3 | 24 | 12.2% | 662 | 2.4% | 0.6% | 4.4% | 205 | real is HIGHER |

The k=5 / W=12 row is UNINFORMATIVE as a precision test: the surrogate produces a mean of 1 event
per draw, so there is no band to compare against.

That same number is the strongest finding in this doc. 52 real events against about 1 by chance.
Five lines crossing oob->ib inside one minute of each other is not something firing rate produces.
At k=4 / W=24 it is 260 real against 15.

### THE SPLIT

| claim | verdict |
|---|---|
| the Mage confirmations cluster on real price pivots | REAL, 11 of 11 lines, both surrogates |
| the smaller TF leads the larger in a cascade ORDER | ARTEFACT of firing rate for g15/g30/ws2/ws3; only g5Mage's lead exceeds chance, and ws1Mage/ws4Mage lead LESS than chance |
| the five lines crossing TOGETHER marks a price top | REAL, and the co-occurrence itself is 7x to 100x rarer by chance than observed |

Gap 16 is CLOSED. Gaps 1-6, 8-11 and 13-15 remain open.

## THE LOW-SIDE TEST — Joe 1015: *"from 14:06, walk forward to the low ws1cp and find the pivot's reversal"*

Producers, all existing: `_ibmech.IB.cps(a,b)` side -1 for the cp, `swing_detect.find_pivots(raw
close, 0.9)` for the pivot, `jig.oob_ib_cross` for the five-line crosses, `jig.anchor_floater`
for the divergence. The cp scan expands forward with NO horizon until it finds one.

### THE RESULT - the mech fails on this leg

| field | value |
|---|---|
| the LOW ws1cp | 2026-07-22 14:26:20 |
| minutes after the 14:06:20 H pivot | 20.00 |
| ws1r there | 12.88 |
| ws1Mage there | 4.66 |
| raw close there | 0.13661503 |
| the next L price pivot | 2026-07-22 14:55:05 |
| its raw close | 0.13604148 |
| minutes from the L pivot back to the cp | -28.75 |
| move, the H pivot to the L pivot | -0.00279868 = -2.0158% |
| move, the cp to the L pivot | -0.00057355 = -0.4198% |

The LOW cp fires 28.75 min BEFORE the price bottom, with 0.4198% still to fall.

### The nine-line Mage joint turn REPEATS, tighter, and lands 30.58 min early

| line | its minimum, 14:06:20 to the cp | at bar | minutes from the L pivot |
|---|---|---|---|
| ws4Mage | 44.98 | 2026-07-22 14:24:30 | -30.58 |
| ws5Mage | 41.13 | 2026-07-22 14:24:30 | -30.58 |
| ws6Mage | 37.97 | 2026-07-22 14:24:30 | -30.58 |
| ws7Mage | 37.45 | 2026-07-22 14:24:30 | -30.58 |
| ws8Mage | 36.09 | 2026-07-22 14:24:30 | -30.58 |
| ws9Mage | 34.75 | 2026-07-22 14:24:30 | -30.58 |
| ws10Mage | 33.46 | 2026-07-22 14:24:30 | -30.58 |
| ws11Mage | 35.04 | 2026-07-22 14:24:30 | -30.58 |
| ws12Mage | 34.70 | 2026-07-22 14:24:30 | -30.58 |

All nine in a 0-second window - tighter than the 25 s on the high side. On the high side the
cluster sat ON the price pivot, +0.00 min. Here it is 30.58 min before it. THE SIGNATURE IS NOT
SYMMETRIC ON THIS LEG.

### The conjunction CANNOT fire at k >= 4 - ws3Mage never goes LOW oob

| line | LOW-side oob->ib crosses, 14:06:20 to the cp | count |
|---|---|---|
| g15Mage | 14:17:35, 14:18:15, 14:22:05, 14:25:40 | 4 |
| g30Mage | 14:15:55, 14:17:20, 14:18:15 | 3 |
| ws1Mage | 14:22:00 | 1 |
| ws2Mage | none until 14:45:40 | 0 |
| ws3Mage | none at all | 0 |

| k of 5 | span W bars | the event bar | minutes from the L pivot | minutes from the LOW cp |
|---|---|---|---|---|
| 5 | 12 | none | - | - |
| 5 | 24 | none | - | - |
| 4 | 24 | none | - | - |
| 4 | 36 | none | - | - |
| 3 | 24 | 2026-07-22 14:32:15 | -22.83 | +5.92 |

### The divergence at the LOW cp fires BULLISH and is wrong

| step | bar | ws1r | raw close |
|---|---|---|---|
| anchor | 2026-07-22 14:26:20 | 12.88 | 0.13661503 |
| pivot | 2026-07-22 14:07:00 | 71.17 | 0.13880328 |
| floater | 2026-07-22 13:53:20 | 5.69 | 0.13741056 |

| the verdict | value |
|---|---|
| ws1r anchor minus floater | +7.19 |
| close anchor minus floater | -0.00079553 = -0.5789% |
| fired | -1 |
| verdict | BULLISH |
| what price did next | fell a further 0.4198% to the 14:55:05 bottom |

### THE ONE THING THAT HELD BOTH SIDES

The nine-line Mage joint turn LEADS the ws1cp on both legs:
  HIGH side - joint top 14:06:20, the x-cross under ws1Mage 14:07:05, lead 0.75 min
  LOW side  - joint bottom 14:24:30, the LOW ws1cp 14:26:20, lead 1.83 min

### NOT DECIDED

17. the high/low asymmetry. On the high side the nine-line joint turn sat ON the price pivot; on
    the low side it sat 30.58 min before it. One leg each - no base rate has been run on the low
    side, and the whole doc's pivot measurements above are H pivots only

### CORRECTION — Joe 1015: *"what makes you think it's wrong?"*

Nothing did. The entry above was scored only as far as the next L pivot, which is the ADVERSE leg
by construction. The Jig's own frame is MAE/MFE from entry to the NEXT FAVOURABLE swing
(`jig.score.entry_quality`, `lr_walk`). For a LONG that is the next H pivot.

| the LONG from the 14:26:20 LOW cp | value |
|---|---|
| entry close | 0.13661503 |
| the next favourable swing, H pivot 2026-07-22 15:29:30 | 0.13779866 |
| MAE% | -0.4198% at 2026-07-22 14:55:05 |
| MFE% | +0.8664% at 2026-07-22 15:29:30 |
| MFE over MAE | 2.06 |
| close at the favourable swing | +0.8664% |

The BULLISH divergence was RIGHT. The "-0.4198% still to fall" I reported is the MAE, not a
refutation. The line "and is wrong" earlier in this section is struck.

### ENHANCED — Joe 1015: *"enhance the result by using the matryoshaka reversal to confirm the pivot"*

Every LOW-side conjunction event on the leg, not only the first, each scored as its own entry bar.

| k of 5 | span W | the event bar | minutes from the L pivot | lines in | MAE% | MFE% | MFE over MAE | close at the favourable swing |
|---|---|---|---|---|---|---|---|---|
| - | - | the cp alone, 14:26:20 | -28.75 | - | -0.4198% | +0.8664% | 2.06 | +0.8664% |
| 3 | 12 bars = 1.0 min | 2026-07-22 14:46:00 | -9.08 | g15Mage, g30Mage, ws2Mage | -0.1465% | +1.1433% | 7.80 | +1.1433% |
| 3 | 24 bars = 2.0 min | 2026-07-22 14:32:15 | -22.83 | g15Mage, g30Mage, ws1Mage | -0.3889% | +0.8977% | 2.31 | +0.8977% |
| 3 | 24 bars = 2.0 min | 2026-07-22 14:46:00 | -9.08 | g15Mage, g30Mage, ws2Mage | -0.1465% | +1.1433% | 7.80 | +1.1433% |
| 4 | 24 bars | none on the leg | - | - | - | - | - | - |
| 4 | 36 bars | none on the leg | - | - | - | - | - | - |

| what the confirmation did | value |
|---|---|
| MAE, cp alone -> 1-min conjunction | -0.4198% -> -0.1465% |
| MFE, cp alone -> 1-min conjunction | +0.8664% -> +1.1433% |
| MFE over MAE | 2.06 -> 7.80 |
| entry delay it cost | 19.67 min |

The 1-minute span fires ONCE on the whole leg, on the good cluster, and skips the premature
14:32:15 one. The 2-minute span fires twice and its first firing is the worse entry.
k >= 4 is unreachable on the low side here because ws3Mage never goes LOW oob.

THIS IS ONE LEG. No base rate stands behind the 7.80.

### NOT DECIDED

18. the 1-minute span beat the 2-minute span on this leg by SKIPPING a firing. That is a
    sample of one. Gap 14 (the span) cannot be settled from it

## JOE'S PREDICTION TESTED — 1015: *"hunting for the high ws1cp after 14:46 might fail"*

### CONFIRMED. The HIGH cp fires early and the leg is a counter-trend bounce.

| field | value |
|---|---|
| the next HIGH ws1cp after 14:46:00 | 2026-07-22 15:03:40 |
| minutes after 14:46:00 | 17.67 |
| minutes from the 15:29:30 H pivot | -25.83 |
| its close vs the H pivot's close | -0.6545% |
| ws1r there | 88.18 |
| ws1Mage there | 93.29 |

| the SHORT from 15:03:40, scored to its next favourable swing | value |
|---|---|
| MAE% | 0.6588% at 2026-07-22 15:29:30 |
| MFE% | 1.2761% at 2026-07-22 16:26:05 |
| MFE over MAE | 1.94 |
| close at the favourable swing | +1.2761% |

It did not lose. It fired 25.83 min early and wore the whole 0.6588% rise into the pivot - the
same early-firing fault as the LOW cp.

### The pivot sequence, which is where the "smaller pullback" read is settled

| bar | kind | raw close | move from the previous pivot |
|---|---|---|---|
| 2026-07-22 12:56:55 | L | 0.13483047 | |
| 2026-07-22 14:06:20 | H | 0.13884016 | +2.9739% |
| 2026-07-22 14:55:05 | L | 0.13604148 | -2.0158% |
| 2026-07-22 15:29:30 | H | 0.13779866 | +1.2916% |
| 2026-07-22 16:26:05 | L | 0.13514982 | -1.9223% |
| 2026-07-22 16:39:15 | H | 0.13655608 | +1.0405% |
| 2026-07-22 17:26:45 | L | 0.13529929 | -0.9203% |
| 2026-07-22 18:20:55 | H | 0.13693504 | +1.2090% |
| 2026-07-22 19:13:15 | L | 0.13506047 | -1.3689% |

The bounce off 14:55:05 was +1.2916% against the -2.0158% drop into it, a 64.07% retracement.
16:26:05 at 0.13514982 is BELOW 14:55:05 at 0.13604148, so the larger structure kept going down.
The 14:46:00 LONG was a counter-trend entry and its +1.1433% MFE landed at 15:29:30, the top of
the bounce.

### *"never going low before the reversal is confluence of the reversal"* - the numbers

| line | its minimum, 14:06:20 to 14:55:05 | at bar | reached LOW oob 15 |
|---|---|---|---|
| g15Mage | -15.88 | 2026-07-22 14:15:50 | yes |
| g30Mage | -2.19 | 2026-07-22 14:24:25 | yes |
| ws1Mage | -8.89 | 2026-07-22 14:24:30 | yes |
| ws2Mage | 14.43 | 2026-07-22 14:45:35 | yes |
| ws3Mage | 29.40 | 2026-07-22 14:55:05 | NO |
| ws4Mage | 34.62 | 2026-07-22 14:30:25 | NO |
| ws6Mage | 27.88 | 2026-07-22 14:30:25 | NO |
| ws8Mage | 23.48 | 2026-07-22 14:30:25 | NO |
| ws10Mage | 21.16 | 2026-07-22 14:30:25 | NO |
| ws12Mage | 20.46 | 2026-07-22 14:55:05 | NO |

Six of ten never reached it. On the high side at 14:06:20, ALL ELEVEN of ws2Mage..ws12Mage were at
or past oob 85 at their own top.

### A SUGGESTION, and it is Joe's own clause - gap 3 re-opened

His 1015 reframe: *"we see all of the Mages reversing inside the same HIGH OOB WINDOW"*. This doc
logged that as gap 3 and recorded that 85 "separates nothing here", because on the high side every
line was past it. IT SEPARATES THE TWO SIDES:

| the leg | where the band's joint turn happened | where the turn landed vs the price pivot | what the leg was |
|---|---|---|---|
| high, 14:06:20 | all 11 lines at or past oob 85 | +0.00 min, ON the pivot | a 2.0158% reversal |
| low, 14:24:30 | 6 of 10 never reached oob 15, minima 20.46 to 34.62 | -30.58 min, early | a 1.2916% bounce, 64.07% retracement |

THE PROPOSAL: a joint turn counts as a pivot mark only when the band is OOB at the turn. An
in-fence joint turn marks a pullback, not a reversal.
  It is built from his words and a fence already banked. It needs no new mech.
  ONE LEG PER SIDE. Every pivot base rate in this doc is H pivots only. Nothing has been run that
  would hold this up.

### NOT DECIDED

19. the oob-at-the-turn filter above. Needs the L-pivot base rate (gap 17) and a count of how many
    joint turns are in-fence versus oob across the 12 days. NOT RUN

## RIDING A HIGHER TF MAGE TO THE PIVOT — Joe 1015

His question: *"so if 15:03 ws1cp isn't the pivot, what does your own observations and the research
tell you about climbing to the pivot by riding a higher TF Mage?"*

### At the 15:03:40 HIGH cp, 16 of 19 lines had not topped, and all 16 topped AT the price pivot

CAUSAL columns read only bars <= the cp. The topping bar is a forward OUTCOME, never a signal.

| line | its value at the cp | rising over the last 12 bars (60 s) | at or past oob 85 | the bar it tops | minutes from the 15:29:30 price pivot |
|---|---|---|---|---|---|
| g15Mage | 87.02 | yes | yes | 2026-07-22 15:20:25 | -9.08 |
| g30Mage | 100.69 | yes | yes | 2026-07-22 15:20:25 | -9.08 |
| ws1Mage | 93.29 | yes | yes | 2026-07-22 15:04:35 | -24.92 |
| ws2Mage | 44.19 | yes | no | 2026-07-22 15:29:30 | +0.00 |
| ws3Mage | 49.93 | yes | no | 2026-07-22 15:29:30 | +0.00 |
| ws4Mage | 56.85 | yes | no | 2026-07-22 15:29:30 | +0.00 |
| ws5Mage | 58.30 | yes | no | 2026-07-22 15:29:30 | +0.00 |
| ws6Mage | 54.96 | yes | no | 2026-07-22 15:29:30 | +0.00 |
| ws7Mage | 52.94 | yes | no | 2026-07-22 15:29:30 | +0.00 |
| ws8Mage | 51.59 | yes | no | 2026-07-22 15:29:30 | +0.00 |
| ws9Mage | 51.00 | yes | no | 2026-07-22 15:29:30 | +0.00 |
| ws10Mage | 50.72 | yes | no | 2026-07-22 15:29:30 | +0.00 |
| ws11Mage | 50.04 | yes | no | 2026-07-22 15:29:30 | +0.00 |
| ws12Mage | 50.11 | yes | no | 2026-07-22 15:29:30 | +0.00 |
| ws15Mage | 54.10 | yes | no | 2026-07-22 15:29:30 | +0.00 |
| ws20Mage | 43.47 | yes | no | 2026-07-22 15:29:30 | +0.00 |
| ws30Mage | 34.74 | yes | no | 2026-07-22 15:30:00 | +0.50 |
| ws45Mage | 26.24 | yes | no | 2026-07-22 15:29:30 | +0.00 |
| ws60Mage | 25.67 | yes | no | 2026-07-22 15:29:30 | +0.00 |

The three oob lines are the ws1cp's OWN lines and they are the three that top early. Every line
from ws2Mage up sits between 43.47 and 58.30 - mid-fence, not arrived.
The climb still to come at the cp was +0.6588% over 25.83 min.

### THE CAUSAL READ AT THE CP - the same oob/in-fence test, one level down

| the cp | the band above ws1 at the cp | what the cp was |
|---|---|---|
| 14:07:05 | 8 of 11 past the 83 ex-fence; all 11 past oob 85 at their own top | the pivot itself, +0.00 min |
| 15:03:40 | 0 of 16 oob, all 43.47 to 58.30 and rising | 25.83 min early, the ride still available |

THE READ: ride ws2 or higher to its top rather than taking the cp, whenever the band above ws1 is
in-fence and rising at the cp. The cp's own lines being oob while the band is not IS the tell that
the cp is a local event and not the pivot.

### WHAT THE RESEARCH ADDS

| source | what it says here |
|---|---|
| Huth & Abergel, Appendix B | the ridden line cannot confirm faster than its own update rate. ws30Mage is the only one of the 16 that missed the pivot bar, at +0.50 min, and it is the slowest that participated. The floor on a ride's timeliness is the ridden TF itself |
| Hayashi & Koike | do not collapse the ride to one line - carry a per-TF read, because one aggregate number hid a sign reversal. All 16 agree on this leg so it does not bite here, but it says read the BAND |
| Ren & Zhou | the hazard of the next threshold event DECAYS with elapsed time. The longer the band climbs without reaching oob, the lower the per-bar chance it crosses now - a ride gets safer to hold the longer it has run |
| our own bounce count | 0 bounces in the prior 30 min gives 45-62% to reach ex-fence. At 15:03:40 the ws2+ band is far from oob, so that read is not available on it yet |

### TWO THINGS STRAIGHT

- n = 1 LEG. No base rate stands behind "16 of 19 top at the pivot".
- `ride_to_max` already exists as Joe's mech for riding momentum-true lines up, with
  `handoff.ride_tf_hi` banked at 4 - but ITS TARGET IS A FLAT-RUN TEST-POINT, NOT THE MAGE TOP.
  It is adjacent, not the same thing. Riding to the Mage top is not currently a mech.

### NOT DECIDED

20. riding to the Mage top is not a mech. `ride_to_max` rides to a flat-run test-point. Whether
    the Mage top becomes a ride target is Joe's call
21. which TF is ridden. 16 lines top at the same bar on this leg, so the leg cannot choose
22. the base rate for "the band above ws1 is in-fence at the cp -> the cp is early". NOT RUN

## CORRECTION — the low-side joint-turn table was CAPPED by a span I chose

That table measured each line's minimum over [14:06:20, the 14:26:20 LOW cp] and reported all nine
of ws4Mage..ws12Mage bottoming at 14:24:30 in a 0-second window. Joe's 14:31 tip exposed it. The
span was mine, he never specified it, and its edge became the headline.

RE-MEASURED between the 14:06:20 H pivot and the 14:55:05 L pivot - the leg's own ends:

| line | corrected minimum | at bar | minutes from the 14:30:25 price low | reached LOW oob 15 | WAS reported as |
|---|---|---|---|---|---|
| g15Mage | -15.88 | 2026-07-22 14:15:50 | -14.58 | yes | - |
| g30Mage | -2.19 | 2026-07-22 14:24:25 | -6.00 | yes | - |
| ws1Mage | -8.89 | 2026-07-22 14:24:30 | -5.92 | yes | - |
| ws2Mage | 14.43 | 2026-07-22 14:45:35 | +15.17 | yes | - |
| ws3Mage | 29.40 | 2026-07-22 14:55:05 | +24.67 | NO | - |
| ws4Mage | 34.62 | 2026-07-22 14:30:25 | +0.00 | NO | 44.98 at 14:24:30 |
| ws5Mage | 31.07 | 2026-07-22 14:30:25 | +0.00 | NO | 41.13 at 14:24:30 |
| ws6Mage | 27.88 | 2026-07-22 14:30:25 | +0.00 | NO | 37.97 at 14:24:30 |
| ws7Mage | 26.79 | 2026-07-22 14:30:25 | +0.00 | NO | 37.45 at 14:24:30 |
| ws8Mage | 23.48 | 2026-07-22 14:30:25 | +0.00 | NO | 36.09 at 14:24:30 |
| ws9Mage | 22.09 | 2026-07-22 14:30:25 | +0.00 | NO | 34.75 at 14:24:30 |
| ws10Mage | 21.16 | 2026-07-22 14:30:25 | +0.00 | NO | 33.46 at 14:24:30 |
| ws11Mage | 21.73 | 2026-07-22 14:30:25 | +0.00 | NO | 35.04 at 14:24:30 |
| ws12Mage | 20.46 | 2026-07-22 14:55:05 | +24.67 | NO | 34.70 at 14:24:30 |
| ws15Mage | 20.47 | 2026-07-22 14:30:25 | +0.00 | NO | - |
| ws20Mage | 22.96 | 2026-07-22 14:55:05 | +24.67 | NO | - |
| ws30Mage | 18.77 | 2026-07-22 14:30:25 | +0.00 | NO | - |

The ws4..ws12 joint window is 14:30:25 to 14:55:05, 296 bars = 24.67 min. The "0-second window" is
WITHDRAWN.

What the uncapped data shows instead is the cascade, cleanly: g15Mage bottoms 14:15:50, g30Mage
14:24:25, ws1Mage 14:24:30, then TEN lines from ws4 to ws30 bottom at exactly 14:30:25 - the same
bar as the price low.

## THE ws5Mage oob-to-oob RIDE — Joe 1015

His spec: *"ride the ws5Mage line from oob to oob, and use matryoshka reversal to tell you when
ws5Mage will reverse (and pxs will follow)"*, with the tip *"the ~14:31 pivot will push ws5Mage
away from low oob, because of the upward pressure created by ws1Mage returning to ib under the
pressure of g30/15/30Mage (matr-rev)"*.

### HIS TIP IS RIGHT TO THE BAR

| field | value |
|---|---|
| the price low | 2026-07-22 14:30:25 at 0.13604401 |
| it is a pivot at swing pct | 0.5%, 0.3%, 0.2% - NOT at the banked 0.9% |
| ws5Mage's low | 31.07 at 2026-07-22 14:30:25 |
| short of LOW oob 15 by | 16.07 points |

| the matr-rev chain he named | bar | minutes to the next step |
|---|---|---|
| g30Mage low oob -> ib, conf | 2026-07-22 14:16:10 | +1.42 |
| g15Mage low oob -> ib, conf | 2026-07-22 14:17:50 | +4.42 |
| ws1Mage low oob -> ib, conf | 2026-07-22 14:22:15 | +8.17 |
| ws5Mage turns up | 2026-07-22 14:30:25 | +0.00 |
| the price low | 2026-07-22 14:30:25 | - |

### THE RIDE, SCORED. the entry is the bar ws5Mage LEAVES high oob, so a SHORT.

| exit | bar | close | MAE% | MFE% | realised at the exit |
|---|---|---|---|---|---|
| entry, ws5Mage at 85.94 | 2026-07-22 14:14:55 | 0.13808986 | - | - | - |
| B  matr-rev, ws1Mage back to ib | 2026-07-22 14:22:15 | 0.13730189 | 0.0000% | 0.7115% | +0.5706% |
| C  the ws5Mage turn | 2026-07-22 14:30:25 | 0.13604401 | 0.0000% | 1.4815% | +1.4815% |
| A  the oob-to-oob target, ws5Mage reaches LOW oob 15 | 2026-07-22 16:17:20 | - | 0.0000% | 1.6385% | +1.6385% |

The SHORT never goes adverse - MAE is 0.0000% on every exit, so MFE-over-MAE is undefined, not
large. The ride stays open 122.42 min to reach the oob target, and round-trips in the middle:
+1.4815% at 14:30:25, down to +0.2109% at 15:29:30, back to +1.6385% at 16:17:20.

### THE FINDING

The matr-rev called the ws5Mage turn 8.17 min ahead of it - his mech worked. But the turn was a
PAUSE, not the end of the ride: ws5Mage bottomed at 31.07, climbed, and reached LOW oob 15 at
16:17:20. Exiting on the matr-rev realised +0.5706% and left 1.07 points behind.

"When will ws5Mage reverse" and "when should the ride end" are not the same question. The mech
answers the first. Used as the second it cost 1.07 points on this leg.

ONE LEG. No base rate.

### NOT DECIDED

23. whether the matr-rev is an exit or only a turn-predictor. On this leg it was premature by
    1.07 points against the oob target
24. the swing pct the pivots are read at. Joe's 14:31 pivot exists at 0.5% and finer, not at the
    banked `lp_lr_swing_pct` 0.9. Every pivot measurement in this doc above uses 0.9

## THE MATR-REV FAMILY ENLARGED — Joe 1015: *"add ws2Mage to the matr-rev family and retest - that might be what you need to push forward from 16:17. if that doesn't achieve, add ws3Mage as well"*

The family's reversal is complete when every member has reversed. A member's reversal is its own
LOW-side oob->ib confirmation - `jig.oob_ib_cross(line, 85, 15, 4)`, sd < 0, the conf bar.
Two readings, both printed because Joe named no span:
  CUMULATIVE  the bar the LAST member confirms, from the ride's entry. No span.
  SPANNED     every member confirms inside a span W of each other.

The ride: entry 2026-07-22 14:14:55, the bar ws5Mage leaves high oob. A SHORT.
The oob-to-oob target: ws5Mage reaches LOW oob 15, at 2026-07-22 16:17:20.

### Each member's first low-side oob->ib confirmation after the entry

| member | its first conf bar after the entry | minutes after the entry | its minimum in the leg | reached LOW oob 15 |
|---|---|---|---|---|
| g30Mage | 2026-07-22 14:16:10 | +1.25 | -2.19 | yes |
| g15Mage | 2026-07-22 14:17:50 | +2.92 | -15.88 | yes |
| ws1Mage | 2026-07-22 14:22:15 | +7.33 | -8.89 | yes |
| ws2Mage | 2026-07-22 14:45:55 | +31.00 | 14.43 | yes |
| ws3Mage | 2026-07-22 16:18:50 | +123.92 | 29.40 | NO inside the leg; its first cross is 123.92 min out |

### CUMULATIVE — ws2Mage moves it, ws3Mage carries it past 16:17

| the family | the fire bar | minutes after the entry | vs the 16:17:20 oob target | MAE% | MFE% | realised |
|---|---|---|---|---|---|---|
| 3 lines, g15 g30 ws1 | 2026-07-22 14:22:15 | +7.33 | -115.08 min | 0.0000% | 0.7115% | +0.5706% |
| 4 lines, + ws2Mage | 2026-07-22 14:45:55 | +31.00 | -91.42 min | 0.0000% | 1.4815% | +1.3388% |
| 5 lines, + ws3Mage | 2026-07-22 16:18:50 | +123.92 | +1.50 min | 0.0000% | 1.6857% | +1.4630% |
| the oob-to-oob target itself | 2026-07-22 16:17:20 | +122.42 | - | 0.0000% | 1.6385% | +1.6385% |

ws2Mage alone moved the exit from +0.5706% to +1.3388%. ws3Mage carried it 1.50 min PAST
16:17:20. On the cumulative reading the oob target still wins by 0.18 points.

### SPANNED — requiring the family to reverse TOGETHER beats the oob target

| the family | span W | the fire bar | vs the 16:17:20 target | MAE% | MFE% | realised |
|---|---|---|---|---|---|---|
| the oob-to-oob target | - | 2026-07-22 16:17:20 | - | 0.0000% | 1.6385% | +1.6385% |
| 3 lines | 12 bars = 1.0 min | 2026-07-22 16:18:50 | +1.50 min | 0.0000% | 1.6857% | +1.4630% |
| 3 lines | 24 bars = 2.0 min | 2026-07-22 14:32:15 | -105.08 min | 0.0000% | 1.4815% | +1.0987% |
| 4 lines | 12 bars = 1.0 min | 2026-07-22 17:28:25 | +71.08 min | 0.0000% | 2.1291% | +1.8751% |
| 4 lines | 36 bars = 3.0 min | 2026-07-22 16:06:15 | -11.08 min | 0.0000% | 1.4834% | +1.1856% |
| 5 lines | 12 bars = 1.0 min | 2026-07-22 19:42:25 | +205.08 min | 0.0000% | 2.1938% | +1.8533% |
| 5 lines | 24 bars = 2.0 min | 2026-07-22 19:15:40 | +178.33 min | 0.0000% | 2.1938% | +2.0036% |
| 5 lines | 60 bars = 5.0 min | 2026-07-22 16:31:45 | +14.42 min | 0.0000% | 2.1291% | +1.5614% |
| 5 lines | 120 bars = 10.0 min | 2026-07-22 16:18:50 | +1.50 min | 0.0000% | 1.6857% | +1.4630% |

The SHORT's MAE is 0.0000% from 14:14:55 to 19:15:40 - price never traded back above the
0.13808986 entry close in those five hours.
The 5-line / 2-min exit gains 0.37 points over the oob target for 178.33 min of extra exposure.
The 3-line family with a 1-min span also reaches 16:18:50, so the span carries weight independently
of the membership.

ONE LEG. The span W is unruled - gap 14. These are forward outcomes, not a base rate.

### NOT DECIDED

25. the family's membership. Joe named g15/g30/ws1, then added ws2Mage, then ws3Mage. Whether
    g5Mage belongs is still gap 15
26. CUMULATIVE versus SPANNED. He named no span. The two readings differ by 0.54 points on the
    5-line family on this leg

## ws4Mage AND ws5Mage ADDED — Joe 1015: *"16:18 is good, but there's more to claim: add ws4 and ws5 Mages"*

### ws3Mage is still the last member in, so the cumulative exit does not move

| member | its first low-side oob->ib conf after the entry | minutes after the entry | vs the 16:17:20 target |
|---|---|---|---|
| g30Mage | 2026-07-22 14:16:10 | +1.25 | -121.17 min |
| g15Mage | 2026-07-22 14:17:50 | +2.92 | -119.50 min |
| ws1Mage | 2026-07-22 14:22:15 | +7.33 | -115.08 min |
| ws2Mage | 2026-07-22 14:45:55 | +31.00 | -91.42 min |
| ws4Mage | 2026-07-22 16:03:35 | +108.67 | -13.75 min |
| ws5Mage | 2026-07-22 16:18:35 | +123.67 | +1.25 min |
| ws3Mage | 2026-07-22 16:18:50 | +123.92 | +1.50 min |

| the family | the fire bar | vs the 16:17:20 target | MAE% | MFE% | realised |
|---|---|---|---|---|---|
| the oob-to-oob target itself | 2026-07-22 16:17:20 | - | 0.0000% | 1.6385% | +1.6385% |
| 4 lines, + ws2 | 2026-07-22 14:45:55 | -91.42 min | 0.0000% | 1.4815% | +1.3388% |
| 5 lines, + ws3 | 2026-07-22 16:18:50 | +1.50 min | 0.0000% | 1.6857% | +1.4630% |
| 6 lines, + ws4 | 2026-07-22 16:18:50 | +1.50 min | 0.0000% | 1.6857% | +1.4630% |
| 7 lines, + ws5 | 2026-07-22 16:18:50 | +1.50 min | 0.0000% | 1.6857% | +1.4630% |

### Spanned - adding them makes it slightly WORSE

| the family | span W | the fire bar | vs the target | MFE% | realised |
|---|---|---|---|---|---|
| 5 lines, + ws3 | 12 bars = 1.0 min | 2026-07-22 19:42:25 | +205.08 min | 2.1938% | +1.8533% |
| 5 lines, + ws3 | 24 bars = 2.0 min | 2026-07-22 19:15:40 | +178.33 min | 2.1938% | +2.0036% |
| 5 lines, + ws3 | 36 bars = 3.0 min | 2026-07-22 19:15:40 | +178.33 min | 2.1938% | +2.0036% |
| 5 lines, + ws3 | 60 bars = 5.0 min | 2026-07-22 16:31:45 | +14.42 min | 2.1291% | +1.5614% |
| 6 lines, + ws4 | 12 bars = 1.0 min | 2026-07-22 19:42:25 | +205.08 min | 2.1938% | +1.8533% |
| 6 lines, + ws4 | 24 bars = 2.0 min | 2026-07-22 19:42:25 | +205.08 min | 2.1938% | +1.8533% |
| 6 lines, + ws4 | 36 bars = 3.0 min | 2026-07-22 19:16:10 | +178.83 min | 2.1938% | +1.9469% |
| 7 lines, + ws5 | 12 bars = 1.0 min | 2026-07-22 19:42:25 | +205.08 min | 2.1938% | +1.8533% |
| 7 lines, + ws5 | 24 bars = 2.0 min | 2026-07-22 19:42:25 | +205.08 min | 2.1938% | +1.8533% |
| 7 lines, + ws5 | 36 bars = 3.0 min | 2026-07-22 19:16:10 | +178.83 min | 2.1938% | +1.9469% |

The bigger family needs a later moment when all 6 or 7 are aligned, and price was slightly higher
there. 5 lines at a 2-minute span is still the best cell at +2.0036%.

### HIS "MORE TO CLAIM" IS REAL, AND FAR BIGGER THAN THE FAMILY FINDS

| field | value |
|---|---|
| the lowest close after the entry, measured to the end of 2026-07-23 | 0.13173411 at 2026-07-23 19:54:25 |
| a SHORT exiting there | +4.6026% |
| the highest close anywhere after the entry | 0.13808986 - the entry bar itself |
| the ride's MAE over that 29.7 hours | 0.0000% |
| the best family exit | +2.0036% |
| left on the table | 2.60 points |

The 14:14:55 entry is the high-water mark for the next 29.7 hours. 4.6026% is available with ZERO
adverse excursion and no member of the matr-rev family, at any span tested, reaches past 2.0036%.

The 07-23 end is a window I chose to measure to, not a ruling. The true low may be later.

### NOT DECIDED

27. the matr-rev family tops out at +2.0036% against a +4.6026% ceiling with 0.0000% MAE. Whether
    the exit mech is the right place to claim the rest, or whether a different mech owns it, is
    Joe's call. ws4Mage and ws5Mage are ruled OUT of the family on this leg - they move the
    cumulative exit not at all and the spanned exit backwards

## THE ws5x OVER-CROSS RACE — Joe 1015: *"using an xwob8, what time after the 'g5 to ws5 reversal detect' does ws5x cross(over, because we're low side) [race: boundary,r,Mage]"*

THE START, the g5-to-ws5 reversal detect: the bar the LAST of g5Mage, g15Mage, g30Mage, ws1Mage,
ws2Mage, ws3Mage, ws4Mage, ws5Mage confirms its LOW-side oob->ib cross, counting from the ride's
2026-07-22 14:14:55 entry. CUMULATIVE reading.

| member | its first LOW-side oob->ib conf after the entry | minutes after the entry |
|---|---|---|
| g5Mage | 2026-07-22 14:16:10 | +1.25 |
| g30Mage | 2026-07-22 14:16:10 | +1.25 |
| g15Mage | 2026-07-22 14:17:50 | +2.92 |
| ws1Mage | 2026-07-22 14:22:15 | +7.33 |
| ws2Mage | 2026-07-22 14:45:55 | +31.00 |
| ws4Mage | 2026-07-22 16:03:35 | +108.67 |
| ws5Mage | 2026-07-22 16:18:35 | +123.67 |
| ws3Mage | 2026-07-22 16:18:50 | +123.92 |

| field | value |
|---|---|
| the g5-to-ws5 reversal detect | 2026-07-22 16:18:50 |
| the member that completed it | ws3Mage |
| ws5x there | -36.92 |
| ws5r there | 15.44 |
| ws5Mage there | 21.56 |
| raw close there | 0.13606968 |

THE EVENT: ws5x crossing OVER its target, held xwob 8 bars = 40 s. `jig.cross_wob` semantics
generalised from a scalar level to a target line - side = x > target, confirmed once the side has
held 8 consecutive bars, a single bar back across resets the run. conf = cross + 8 - 1. CAUSAL.
OVER, not under, because the leg is low side.

### THE ANSWER - +13.08 to +13.25 minutes after the detect

| the race | cross bar | conf bar | minutes from the detect | ws5x at the cross | the target's value there |
|---|---|---|---|---|---|
| 1. Mage, ws5Mage | 2026-07-22 16:31:20 | 2026-07-22 16:31:55 | +13.08 | 12.50 | 11.45 |
| 2. boundary, LOW oob 15 | 2026-07-22 16:31:30 | 2026-07-22 16:32:05 | +13.25 | 32.99 | 15.00 |
| 3. r, ws5r | 2026-07-22 16:31:30 | 2026-07-22 16:32:05 | +13.25 | 32.99 | 17.83 |

THE RACE IS DECIDED BY THE TARGETS' LEVELS, not by three independent mechanisms: ws5Mage 11.45 <
boundary 15.00 < ws5r 17.83, and a rising x crosses the lowest first. ws5x jumps from 12.50 at
16:31:20 to 32.99 at 16:31:30 - one 10 s move clears the boundary and r together, so those two
tie on the same cross bar.

### The exits, against the references already measured

| exit | bar | MAE% | MFE% | realised |
|---|---|---|---|---|
| Mage | 2026-07-22 16:31:55 | 0.0000% | 2.1291% | +1.6746% |
| boundary | 2026-07-22 16:32:05 | 0.0000% | 2.1291% | +1.6062% |
| r | 2026-07-22 16:32:05 | 0.0000% | 2.1291% | +1.6062% |
| the oob-to-oob target | 2026-07-22 16:17:20 | 0.0000% | 1.6385% | +1.6385% |
| the 5-line spanned family, 2-min span | 2026-07-22 19:15:40 | 0.0000% | 2.1938% | +2.0036% |

The x-cross race lands within 0.04 points of the oob target and 0.33 to 0.40 points below the
spanned family. MFE was already 2.1291% before the x-cross confirmed, so the exit gives back about
0.45 points. The 16:26:05 L price pivot at the banked 0.9% sits 5.83 min BEFORE the Mage conf.

### NOT DECIDED

28. the three race targets are not independent on this leg - their ORDER is their level order, and
    the boundary and r tie exactly. Whether the race is a real three-way mech or a level ordering
    needs a leg where ws5x rises slowly enough to separate them
29. xwob 8 is Joe's for this test. The matr-rev members use `boundary_xwob` 4. Two different holds
    are now in play in one mech
