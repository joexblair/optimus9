# 1018 — the momentum cache, banked. 32 timeframes, GPU, parity proved

Joe 1018, the six rulings: *"1 & 2, the lines: use the lines in the `present` column"* / *"3, r
only"* / *"4, not needed"* / *"5, scale"* / *"6, gpu"* / *"the scale: B"*

## 1. What was built

| the piece | where |
|---|---|
| the GPU mirror of `momo_gated.momo_g`, mom-true only | `optimus9/compute/momo_gpu.py` |
| the 32-timeframe builder, mask + away/toward tags | `optimus9/compute/build_momo_cache.py` |
| the banked cache, 64 files, 168 MB | `optimus9/orchestration/.rpl_cache/momt` |

| the set | value |
|---|---|
| timeframes | ws1-ws30, ws45, ws60 = 32 |
| role | r only, Joe 1018 |
| sides | both, +1 and -1 |
| tape | 1,632,960 bars, EM 1791158400000, HOURS 40, WARMUP 1114 |
| g15 / g30 | OUT. No momo bank covers a sub-minute timeframe and Joe ruled one *"not needed"* |

## 2. THE PARITY PROOF — the price of the GPU ruling, paid

| the proof | value |
|---|---|
| timeframes compared | 32 of 32 |
| bar-comparisons | 104,509,440 |
| TOTAL mismatches | **0** |
| verdict | the GPU path matches CPU `momo_g` bar for bar |

The CPU reference is a separate full-tape run of `momo_gated.momo_g` per timeframe per side, 8
processes, ~20 min wall clock, slowest ws60 at 653 s. Every count below is identical on both paths.

## 3. The speed, measured

| the route | 32 timeframes, both sides, full tape |
|---|---|
| GPU masks | 28.7 s |
| the away/toward walk, python, literal mirror of Joe 0829 | 108.0 s |
| CPU reference, 8 processes | ~20 min |
| CPU reference, serial equivalent | ~2.9 h |

## 4. The grid and the counts, per timeframe

| the tf | window | stride | bend bars | stall delay | mom-true +1 | mom-true -1 | away +1 | away -1 |
|---|---|---|---|---|---|---|---|---|
| ws1 | 6 min | 4 | 72 | 60 bars = 5 min | 439962 | 442894 | 572217 | 566594 |
| ws2 | 12 min | 7 | 144 | 120 bars = 10 min | 437906 | 440320 | 549729 | 544635 |
| ws3 | 18 min | 11 | 216 | 180 bars = 15 min | 439865 | 442354 | 555548 | 546618 |
| ws4 | 24 min | 14 | 288 | 240 bars = 20 min | 434874 | 442211 | 544608 | 538983 |
| ws5 | 30 min | 18 | 360 | 300 bars = 25 min | 436816 | 443178 | 546623 | 547217 |
| ws6 | 36 min | 22 | 432 | 360 bars = 30 min | 435355 | 439020 | 554108 | 543004 |
| ws7 | 42 min | 25 | 504 | 420 bars = 35 min | 434877 | 437239 | 547136 | 539741 |
| ws8 | 48 min | 29 | 576 | 480 bars = 40 min | 431225 | 438084 | 556316 | 545614 |
| ws9 | 54 min | 32 | 648 | 540 bars = 45 min | 430345 | 436095 | 560528 | 537580 |
| ws10 | 60 min | 36 | 720 | 600 bars = 50 min | 439462 | 441799 | 553277 | 520179 |
| ws11 | 66 min | 40 | 792 | 660 bars = 55 min | 436801 | 443136 | 549583 | 515584 |
| ws12 | 72 min | 43 | 864 | 720 bars = 60 min | 427668 | 444581 | 562869 | 522679 |
| ws13 | 78 min | 47 | 936 | 780 bars = 65 min | 434443 | 443512 | 549538 | 519711 |
| ws14 | 84 min | 50 | 1008 | 840 bars = 70 min | 431071 | 436720 | 546380 | 533657 |
| ws15 | 90 min | 54 | 1080 | 900 bars = 75 min | 431692 | 428387 | 558156 | 535327 |
| ws16 | 96 min | 58 | 1152 | 960 bars = 80 min | 428313 | 436005 | 546758 | 531656 |
| ws17 | 102 min | 61 | 1224 | 1020 bars = 85 min | 422293 | 437512 | 541282 | 546860 |
| ws18 | 108 min | 65 | 1296 | 1080 bars = 90 min | 430099 | 434344 | 551335 | 554224 |
| ws19 | 114 min | 68 | 1368 | 1140 bars = 95 min | 429609 | 434317 | 567516 | 539277 |
| ws20 | 120 min | 72 | 1440 | 1200 bars = 100 min | 434063 | 432099 | 557334 | 542425 |
| ws21 | 126 min | 76 | 1512 | 1260 bars = 105 min | 435804 | 440051 | 540285 | 536259 |
| ws22 | 132 min | 79 | 1584 | 1320 bars = 110 min | 430903 | 431578 | 529065 | 539352 |
| ws23 | 138 min | 83 | 1656 | 1380 bars = 115 min | 436244 | 425942 | 548345 | 557062 |
| ws24 | 144 min | 86 | 1728 | 1440 bars = 120 min | 424680 | 422728 | 551174 | 566661 |
| ws25 | 150 min | 90 | 1800 | 1500 bars = 125 min | 430315 | 431177 | 530763 | 558507 |
| ws26 | 156 min | 94 | 1872 | 1560 bars = 130 min | 427453 | 431754 | 543480 | 545115 |
| ws27 | 162 min | 97 | 1944 | 1620 bars = 135 min | 432574 | 436325 | 544374 | 548702 |
| ws28 | 168 min | 101 | 2016 | 1680 bars = 140 min | 438907 | 432272 | 541950 | 550689 |
| ws29 | 174 min | 104 | 2088 | 1740 bars = 145 min | 444385 | 433736 | 547482 | 542564 |
| ws30 | 180 min | 108 | 2160 | 1800 bars = 150 min | 453227 | 434610 | 526983 | 561394 |
| ws45 | 270 min | 162 | 3240 | 2700 bars = 225 min | 449628 | 424790 | 504350 | 550618 |
| ws60 | 360 min | 216 | 4320 | 3600 bars = 300 min | 440907 | 422965 | 516284 | 560829 |

## 5. The knobs in the key

| the knob | value | what it is |
|---|---|---|
| `k_window` | 6 | the momo window = `k_window` x tf, minutes |
| `momo_fixed_samples` | 21 | the straight-fit sample count |
| `momo_step_min` | 5 | unused while fixed_samples > 0, in the key anyway |
| `momo_window_min` | 60 | the bank's own default, overridden per tf |
| `momo_slope_min` | 1.2 | the flat / sloped split |
| `momo_slack_ref` | 1.2 | the slope earning full level slack |
| `momo_r2_min` | 0.7 | the straightness floor, sloped branch |
| `momo_seam` | off | so the seam excuse cannot fire |
| `level_slack` | 13.9 | the 50-gate slackens by `level_slack` x trk |
| `curl_arc_min` | 4.0 | the bend height a curl must reach |
| `curl_r2_min` | 0.4 | gate 3, the bend's own r2 floor |
| `curl_vtx_lo` / `curl_vtx_hi` | 0.05 / 0.95 | the turning point sits inside the window |
| gate2 | True | momo_gated's default, every CPU caller's |

Both banks are version 1 and every value is identical: band 1-12 is mech `wsf`, band 13-60 is
mech `domtf`.

## 6. The away / toward tags

The rule is `report_wsf_bar.heading`, Joe 0829, unchanged:

    if momentum_true:      return 'toward'     # C4 - a new cycle has started
    if extrema_r is None:  return 'toward'
    return 'away' if held >= MOMO_STALL_DELAY else 'toward'

| the scale | Joe 1018: reading B |
|---|---|
| the hold | five of the LINE'S OWN candles |
| in bars | `5 * tf * 12` on the 5 s grid |
| ws1 | 60 bars = 5 min. THIS MOVES ws1 off the 25 s banked 0829 - Joe's ruling |
| ws12 | 720 bars = 60 min |
| ws60 | 3,600 bars = 300 min |

TWO FILES PER TIMEFRAME. `momt_ws<tf>_<key>.npz` holds the mask, keyed on the momentum knobs.
`tag_ws<tf>_<key>.npz` holds `away`, `ex_r`, `ex_bar` and `held`, keyed on the momentum knobs AND
the stall delay. `held` is banked as a RAW BAR COUNT, so a later ruling on the scale rebuilds the
tags in 108 s and never touches a mask.

NO WINDOW ON THE EXTREMA WALK. The DB producer bounded its segment with a `WIN_FROM` knob; the
segment here runs from the last mom-true bar with nothing in front of it, per Joe's rule that no
window enters the code unless he set one.

## 7. What is stated, not asked

| the call | the reason |
|---|---|
| float64 end to end | the verdict is threshold comparisons; fp32 moves them |
| direct dot products for the bend, no prefix sums | a prefix-sum difference over 4,320 bars loses the digits `curl_r2_min` reads |
| the bend fitted only where flat AND level | that is `momo_fit`'s own `quad='auto'`, not an optimisation |
| the extrema walk stays a python loop | a literal mirror of Joe's 0829 producer; 108 s for all 32 |
| the cache sits in `.rpl_cache/momt` | beside the line cache, off the deletable job temp dir |
| the segment resets on the GATED mom-true mask | `_momtrue` uses the gated verdict; the DB producer read `wflb_verdict`, whose gating I have not read |

## 8. Open

| the item | state |
|---|---|
| g15 / g30 | out, under *"4, not needed"*. Say the word if that meant "use the 1-12 band" |
| the 28 ws timeframes with no lines | out. A line build is a separate job |
| `momo_fixed_samples` 21 on a 21-point fit | the floors 0.7 and 0.4 were set against a 12-point fit. Pre-existing, task #1, not touched here |

---

# 1018 — the 09-01..09-05 dev-cache, and what the extra pad day exposed

Joe 1018: *"build a supplementary dev-cache for 09-03 and 09-04"* then *"add 09-02 to the devcache"*

| the cache | window | bars | key | events | closed trades |
|---|---|---|---|---|---|
| the 4-day | 2026-09-02 00:00:00 .. 2026-09-05 23:59:55 | 69,120 | `97b555bb6161186eed71` | 138 | 74 |
| the 5-day | 2026-09-01 00:00:00 .. 2026-09-05 23:59:55 | 86,400 | `c560c806366626ab054d` | 165 | 89 |

Both are kept - the window is in the key.

## Where the two disagree on the SAME days

| the day | 4-day events | 5-day events | 4-day trades | 5-day trades |
|---|---|---|---|---|
| 2026-09-02 | 39 | 39 | 25 | 24 |
| 2026-09-03 | 36 | 37 | 16 | 16 |
| 2026-09-04 | 31 | 31 | 17 | 17 |
| 2026-09-05 | 32 | 32 | 16 | 16 |

### 1. 2026-09-02 01:40:25 LONG exists in the 4-day build and NOT in the 5-day. MEASURED CAUSE.

`O2.CAP` = 2, the pyramid cap, trades per side. At 01:40:25 the 5-day build already holds two LONGs:

| the live LONG | armed | exits |
|---|---|---|
| carried in from the pad day | 2026-09-01 23:28:55 | 2026-09-02 01:48:20 |
| inside the window either way | 2026-09-02 00:36:25 | 2026-09-02 01:50:45 |

The 4-day build cannot see the first of those, so it holds one LONG and admits 01:40:25. The event
count on 09-02 is 39 in BOTH builds, so this is the pool, not event generation.

### 2. 2026-09-03 02:18:55 SHORT exists in the 5-day build and NOT in the 4-day. MEASURED CAUSE,
### and it carries a staleness finding.

The event's own note, read from the cache:

    the fire was 2026-09-01 11:30:40, the cross ran forward, confirmed 2026-09-01 11:51:35

The fire bar is on 2026-09-01, which the 4-day window does not contain. So the event is absent
there because its information lies outside the window.

| the stamp gap | value |
|---|---|
| the fire | 2026-09-01 11:30:40 |
| the confirmation | 2026-09-01 11:51:35 |
| the event | 2026-09-03 02:18:55 |
| fire to event | 139,695 s = 27,939 bars = 38.80 h |

NOT LOOKAHEAD - the information precedes the event, which is the right order. It is STALENESS: an
event stamped 38.8 h after the fire that produced it. `_win3`'s `lookahead_bars` field exists to
catch the negative case; this is the same field strongly positive, and no knob bounds it.

### 3. 2026-09-03 02:41:40 SHORT exists in the 4-day build and NOT in the 5-day.

Both builds exit at 2026-09-03 04:38:35. The 5-day build fills 02:18:55 instead, at +0.3927%
against the 4-day's +1.0252% on 02:41:40. The pyramid cap is 2 and 01:36:05 SHORT is live in both,
so the 02:18:55 fill occupies the slot 02:41:40 would have taken.
