# mage-cascade — what we learnt, banked 2026-09-18

Joe 0918: *"I called on mage-cascade to solve a single trade, the 09-01 17:26:20 signal in the 122
report. the amount of effort needed to build cascade-mage properly is not worth 1 trade - so let's
bank what we have learnt about mage-cascade and we'll come back to refine it later."*

This is a research record, not a spec. Nothing here is shipped, nothing here is a knob, and no
producer was promoted out of scratch. The one instruction that governs a return to this work is in
§8 — **the whole measurement was built inside a dr frame and Joe's model is dr-free.**

---

## 1. the object

`optimus9/compute/ride_to_max.py:67`

    def cascade(M, k, dr, tf_lo=1, tf_hi=12):
        v     = [M[tf][k] for tf in 1..12]          the Mage ladder at bar k
        drop  = dr * (v[0] - v[-1])                 +ve = falls AWAY from dr as the tf rises
        wrong = count of the 11 steps running against that line
        spread= v.max() - v.min()

Route 3's own measurement. It reports and gates nothing. `drop` is antisymmetric in dr:
`drop(-dr) = -drop(dr)`, and `wrong(+dr) + wrong(-dr) = 11`.

## 2. why it was called on

Trade #14 of `ws1mage_rev_exit_122.txt` — **2026-09-01 17:26:20, dr +1**, opened as a sneaky-1 long
while the market was about to reverse down. Joe asked whether the cascade shape at that bar
predicted the reversal. Everything below came out of that one question.

## 3. Joe's own reading process, verbatim 0918

> *"here's my internal proicess: the first thing I look at is the lowest TF's value, and the highest
> TF's value (~90 to ~73). I can draw a mental downward line between those 2 numbers, making
> allowances for the bumps. then I check for ws1 to be oob. that's all I do for the Mages / the same
> mental process happens for the r's, but I ignore ws1r because it's laggy and moves alot regrdless
> of any scenario. the r lines are all slower to react, so I view them with a looser opinion. I have
> the same need for a imaginary downward line of r cascading, but I'm more tolerant of the r bumps
> than I am of the Mage bumps. the end result is lower TFs in oob (it can be any number of lower
> TF's in oob), and a cascade that ultimately falls away from the hi oob (for a bearish), or climbs
> away from (for a bullish) from the low oob"*

Rulings that followed, all 0918:

- *"treat r as confluence at-best. Mage is the primary"*
- *"probably the best use for r is 'is it generally facing the same direction as mage (falling or climbing)'"*
- *"you'll find cases where the bump counts are higher than you expect - that's when you look at the resulting market direction"*
- *"the source oob of Mage's line, which defines the lines heading"*
- *"this work is not calculated on dr - dr is only compared after the calculation has produced a
  decision based on the ladders direction (r and Mage values increasing or decreasing from top to
  bottom of the TF list), and its source-based trajectory direction. we compare dr at the end simply
  to decide if a main-trade signal is masquarading as sneaky-1 (or vice versa)"*

And from 0918 earlier, the weakness mechanic:

> *"the lower TF's (in this case: ws1,ws2) are oob. oob is where a Mage goes to complete the release
> of its momentum - ws1 and ws2 are ready to turn around. the lines above ws1,2 are not able to reach
> the high oob before ws1,2 reverse - their values are too far away. this is what causes the
> `weakness` (my term) - a lack of confluence forthcoming from the overarching lines. we know that
> higher overarhing lines set the trend when they make it to oob, and they lose the trend when they
> can't."*

## 4. the columns that were built

All dr-framed. See §8 — this is the defect.

| column | definition | note |
|---|---|---|
| `mfall` | `dr * (ws1Mage - ws12Mage)` | > 0 = ladder ends away from the oob end |
| `mbump` | steps of the 11 running against `mfall` | **dr +1 counts raw RISING steps, dr -1 counts raw FALLING steps** |
| `oob1` | ws1Mage oob on the dr side | oob is always 15 / 85 |
| `noob` | how many of ws1..ws12 Mage are at the dr-side oob | 0..12 |
| `rfall` | `dr * (ws2r - ws12r)` | ws1r ignored, Joe's ruling |
| `rbump` | steps of the 10 running against `rfall` | |
| `nr` | how many of ws3r..ws12r are AT the source oob now | the ARRIVED test |
| `reach` | `dr+1: max(ws3r..ws12r) - 85`, `dr-1: 15 - min(...)` | +ve = arrived |
| `nsame` / `nopp` | how many of ws3r..ws12r carry the same / opposite source oob | the STARTED test |
| `mvote` | how many of ws5..ws12 Mage share ws1Mage's source oob | 0..8 |
| `mat` | how many of ws5..ws12 Mage are AT that oob right now | 0..8 |

`source oob` of a line = the oob side it **last touched**, walking back with no cap.
Implemented as a forward-fill of the sign (`ffill_side`).

## 5. the event definition used

- **ws1Mage enters oob on the dr side and holds 3 bars (15 s).**
- dwell 3 is the jig's own `ws1mage_rev` `dwell_ok` leg, reused rather than invented.
- flicker without it: 44% of raw oob entries last <= 3 bars, 22% last exactly 1 bar.
- **this knob was never ruled on by Joe.** Every count below moves if it changes.
  At dwell 1 the window holds 19,956 entries; at dwell 3, 12,992; at dwell 12, 5,751.

Score, at every horizon: `fwd = (px[b + mins*12] - px[b]) / px[b] * 100 * dr`, 12 bars = 1 min at
the 5 s grid. Negative = price moved against dr.

## 6. the in-sample fit, and what it was worth

Window 2026-09-01 -> 2026-09-06. Object: the 122 trade opens of `ws1mage_rev_exit_122.txt`.

| gate | n | fwd 60m | p | fwd 120m | p | MAE 60m |
|---|---|---|---|---|---|---|
| ALL 122 | 122 | +0.013 | 0.4983 | -0.112 | 0.4949 | 0.859 |
| ws1 oob | 33 | -0.118 | 0.2454 | -0.300 | 0.2514 | 1.102 |
| mage falls > 0 | 98 | -0.011 | 0.4203 | -0.167 | 0.3652 | 0.855 |
| ws1 oob + mage falls | 31 | -0.106 | 0.2772 | -0.304 | 0.2456 | 1.071 |
| **+ bumps <= 2** | **11** | **-0.853** | **0.0067** | -0.951 | 0.0488 | 1.669 |
| **+ bumps <= 3** | **14** | **-0.765** | **0.0056** | -0.894 | 0.0401 | 1.532 |
| + bumps <= 4 | 22 | -0.388 | 0.0460 | -0.790 | 0.0280 | 1.322 |
| ws1 oob + falls >= 40 | 14 | -0.490 | 0.0517 | -1.098 | 0.0156 | 1.443 |

- ws1 oob alone p 0.2454. Mage falls alone p 0.4203. Both together p 0.2772. **None work alone.**
- the bump limit was what appeared to turn it on.
- **about 14 threshold combinations were tested and the thresholds were chosen after looking.**
  p 0.0056 across 14 looks is nearer 0.08.
- **this fit did not survive. See §7.**

## 7. the OOS result — the fitted gate reverses

Window **2026-06-10 -> 2026-09-01, 83 days**, entirely before the in-sample days.
12,992 ws1Mage oob entries (dr +1 6,243 / dr -1 6,749).

### the reversal, stated precisely

| gate `mage falls > 0 + bumps <= 2` | event | window | events | clusters | 60m |
|---|---|---|---|---|---|
| the fitted claim | 122 trade opens | IS 09-01 -> 09-06 | 11 | — | **-0.853** |
| same gate | ws1Mage oob entry | IS 09-01 -> 09-06 | 192 | 20 | **-0.023** |
| same gate | ws1Mage oob entry | OOS 08-26 -> 08-31 | 216 | 23 | **+0.209** |
| same gate | ws1Mage oob entry | OOS 06-10 -> 09-01 | 3,145 | 349 | **+0.020** |

Part of the reversal is the event definition and part is the window. Not all window.

### the bump table, OOS, `mage falls > 0`

`clusters` = events separated by more than 120 min. This is the sample size, not the event count.

| bumps | events | clusters | 30m | 45m | 60m | 90m | 120m | hit% 120m |
|---|---|---|---|---|---|---|---|---|
| 0 | 700 | 210 | -0.005 | -0.011 | -0.043 | +0.205 | +0.202 | 47% |
| 1 | 1,223 | 302 | -0.007 | -0.006 | +0.038 | +0.093 | +0.108 | 49% |
| 2 | 1,222 | 322 | +0.034 | +0.026 | +0.037 | +0.122 | +0.117 | 49% |
| 3 | 1,177 | 309 | -0.018 | -0.025 | -0.058 | -0.029 | -0.003 | 52% |
| 4 | 1,367 | 286 | +0.044 | +0.026 | +0.066 | +0.055 | +0.035 | 50% |
| 5 | 1,505 | 292 | +0.009 | -0.005 | +0.044 | -0.022 | +0.027 | 52% |
| 6 | 1,492 | 326 | +0.054 | +0.031 | +0.023 | +0.020 | +0.021 | 53% |
| 7 | 999 | 319 | +0.044 | +0.028 | +0.038 | +0.016 | +0.006 | 53% |
| **8** | **547** | **222** | -0.038 | -0.067 | **-0.135** | **-0.158** | **-0.238** | **58%** |
| **9** | **190** | **100** | +0.063 | -0.087 | **-0.206** | **-0.259** | **-0.352** | **61%** |
| 10 | 22 | 18 | +0.074 | +0.257 | -0.057 | -0.200 | -0.313 | 59% |
| 11 | 0 | 0 | — | — | — | — | — | — |

**The turn is at 8 of 11, and it is dr -1 only:**

| set | events | clusters | 30m | 45m | 60m | 90m | 120m | hit% 120m |
|---|---|---|---|---|---|---|---|---|
| bumps >= 8, **dr -1** | 411 | 127 | -0.077 | -0.197 | -0.337 | -0.400 | **-0.478** | **63%** |
| bumps >= 8, dr +1 | 348 | 117 | +0.070 | +0.096 | +0.070 | +0.071 | -0.021 | 54% |
| bumps <= 7, dr -1 | 5,108 | 265 | +0.003 | -0.018 | -0.014 | -0.005 | -0.026 | 51% |
| bumps <= 7, dr +1 | 4,577 | 270 | +0.041 | +0.040 | +0.064 | +0.106 | +0.147 | 50% |

Robustness of the `bumps >= 8, dr -1` set: median 120m **-0.461** against a mean of -0.478, so not
one fat tail. 51 of 81 days negative. Removing the best and worst day moves the both-dr figure from
-0.269 to -0.289. The top 8 negative days carry 83% of the sum.

**CAUTION, see §8:** `mbump` is defined by dr, so "bumps >= 8 at dr -1" and "bumps >= 8 at dr +1"
are two different raw geometries, not one measurement split by dr.

### what a high bump count actually is — the mean ladder

| set | Mage ws1 -> ws12, mean of each rung |
|---|---|
| dr -1, bumps >= 8 | 9.8, 20.7, 28.8, **31.6**, 31.2, 30.1, 28.4, 26.7, 24.9, 23.5, 22.3, 20.9 |
| dr -1, bumps <= 7 | 10.4, 17.4, 23.7, 28.4, 31.9, 34.5, 36.7, 38.6, 40.1, 41.7, 42.9, **43.7** |
| dr +1, bumps >= 8 | 90.4, 76.8, 69.0, **67.4**, 67.9, 69.1, 71.1, 73.0, 74.6, 76.2, 77.6, 78.5 |
| dr +1, bumps <= 7 | 90.1, 82.8, 76.4, 71.6, 67.6, 64.8, 62.3, 60.2, 58.2, 56.7, 55.5, **54.3** |

| set | r ws2 -> ws12, mean of each rung (ws1r ignored) |
|---|---|
| dr -1, bumps >= 8 | 27.9, 26.9, 30.5, 35.4, 40.2, 45.7, 49.1, 52.5, 57.3, 58.1, **59.8** |
| dr -1, bumps <= 7 | 31.7, 30.8, 30.8, 30.8, 31.6, 32.4, 33.7, 35.3, 36.3, 37.8, 38.9 |
| dr +1, bumps >= 8 | 69.3, 69.2, 66.5, 62.5, 58.0, 52.2, 49.5, 46.2, 43.3, 40.5, **40.3** |
| dr +1, bumps <= 7 | 67.8, 69.0, 68.8, 67.6, 66.8, 65.6, 64.6, 63.0, 62.1, 61.3, 60.2 |

- **bumps >= 8 is not a rough cascade. It is a ladder that turns over at ws4** — the mid-board, where
  Joe's blast-radius note (`docs/wsf_setup_model.md` 3.21.2) says momentum is lowest.
- bumps <= 7 is the clean monotone procession with no turn.
- at bumps >= 8 the **r ladder is the one cascading** (27.9 -> 59.8) while the Mage ladder humps. At
  bumps <= 7 r is nearly flat.

### the 5-day in-sample window disagrees with the 83-day OOS

| window | set | events | clusters | 60m | 120m | hit% 120m |
|---|---|---|---|---|---|---|
| OOS 06-10 -> 09-01 | bumps >= 8, dr -1 | 411 | 127 | -0.337 | **-0.478** | 63% |
| IS 09-01 -> 09-06 | bumps >= 8, dr -1 | 38 | **12** | +0.322 | **+0.340** | 45% |

## 8. THE DEFECT — everything above was calculated inside a dr frame

Joe 0918, verbatim:

> *"is dr used in the calculations? my view is that this work is not calculated on dr - dr is only
> compared after the calculation has produced a decision based on the ladders direction (r and Mage
> values increasing or decreasing from top to bottom of the TF list), and its source-based trajectory
> direction. we compare dr at the end simply to decide if a main-trade signal is masquarading as
> sneaky-1 (or vice versa)"*

He is right. dr is used at every stage:

| stage | the code | what dr does |
|---|---|---|
| the event | `oob1 = where(d>0, ws1Mage>=85, ws1Mage<=15)` | picks WHICH oob counts as an event |
| event filter | `base = oob1 & (DR!=0) & fin` | drops every bar where the latch never fired |
| episode grouping | `samedr[1:] = (DR[1:]==DR[:-1])` | breaks a run when dr flips, creating a new event |
| the dwell | `hold[:n-k] = base[k:] & (DR[k:]==DR[:n-k])` | the 3-bar dwell also requires dr to hold |
| `mfall` | `d * (ws1Mage - ws12Mage)` | signs the Mage ladder direction |
| `mbump` | `msteps = -diff(Mage)*d`, `(msteps<0).sum()` | decides which steps are bumps |
| `rfall` / `rbump` | same form | same |
| `noob`, `nr`, `reach`, `mat` | `where(d>0, ...>=85, ...<=15)` | picks the side |
| `nsame` / `nopp` / `mvote` | `(SRC == DR)`, `(SRC == -DR)` | dr IS the reference the sources compare to |
| the score | `... * dr` | signs the outcome |

### what the dr frame cost

| population, OOS window | events |
|---|---|
| ws1Mage enters **either** oob, dr-free (source = the side it entered) | **14,682** |
| source = hi 85 | 7,044 |
| source = lo 15 | 7,638 |
| dr agrees with the source side | 11,864 (81%) |
| dr **opposes** the source side | **2,818 (19%)** |
| dr never latched | 0 |
| what was built | 12,992 |

- requiring the oob side to match dr **discarded 2,818 entries, 19%**.
- 12,992 exceeds 11,864 because `samedr` **splits one oob dwell into two events** when dr flips
  partway through. dr both removes events and manufactures them.
- **the 2,818 discarded entries are exactly the population Joe's last sentence is about** — a
  main-trade signal masquerading as sneaky-1 or the reverse. They were excluded from every table.

### dr is not independent of ws1Mage

The latch is `dr_latch_wob(ws1Mage, ws13m, wob 8)`:

    up += 1 if (ws1Mage >= MAGE_HI and ws13m >= MAGE_HI) else 0     MAGE_HI = 75.0
    dn += 1 if (ws1Mage <= MAGE_LO and ws13m <= MAGE_LO) else 0     MAGE_LO = 25.0
    dr = +1 at up >= 8, -1 at dn >= 8

dr +1 already requires ws1Mage to have held >= 75 for 8 bars. That is why dr agrees with the source
side 81% of the time — **dr is partly a lagged restatement of the line the event tests.**

### the columns coincide only because of the filter

`oob1` forces ws1Mage's oob side to equal dr at every retained event, so "compared to dr" and
"compared to ws1Mage's source" are the same thing in this build. Lift the dr filter and `nsame`,
`nopp`, `mvote`, `mat` and `nr` become wrong.

### what a dr-free rebuild changes

| element | what was built | Joe's model |
|---|---|---|
| event | ws1Mage enters the oob **on the dr side** | ws1Mage enters **either** oob; the side it entered IS the source |
| ladder direction | dr-signed `mfall` | raw: are ws1..ws12 values increasing or decreasing down the TF list |
| bumps | steps against the dr-signed direction | steps against the **raw** ladder direction |
| r | dr-signed `rfall`, dr-referenced sources | raw r ladder direction, each line's own source oob |
| decision | never made — dr carried it | bearish or bullish, from the ladders plus source trajectory |
| score | `x dr` | raw price move % |
| dr | the frame for all of it | **a column compared at the end** |

## 9. the r tests — all three null

Every one of these was run inside the dr frame of §8, so none of them is evidence about a dr-free
reading. They are recorded so the same ground is not re-walked.

| test | definition | result | sample |
|---|---|---|---|
| **direction** | `rfall > 0` vs `<= 0` inside `bumps <= 2` | +0.040 vs -0.008 at 60m | 342 / 313 clusters |
| **ARRIVED** | >= 1 of ws3r..ws12r AT the source oob now | -0.011 vs -0.017 at 60m | 8,517 / 4,475 events |
| **STARTED** | ws3r..ws12r source oob = ws1Mage's, `nsame` | +0.003 (nsame>=8) vs +0.009 (nopp>=8) at 30m | 4,608 / 1,830 events |

- the direction test also came out at **84% agreement across all 122 in-sample trade opens** — r
  faces the same way as Mage almost always, so it has no filtering power as a gate.
- ARRIVED splits the population by 0.009 at 30m. STARTED splits it by 0.006. **STARTED is flatter
  than the tense it replaced**, despite being the more faithful instrument for Joe's frame.
- the weakness case stated properly — *they set out toward ws1Mage's extreme and none arrived*
  (`nopp >= 8 AND nr = 0`) — is +0.009 at 30m on 304 clusters, against +0.007 for those that arrived.
- no gradient in `nr` (0..10) and none in `reach` (short by 40 through past by 10).
- every one of ws3r..ws12r carries a source at every event — 0 of 10 unsourced — so
  `nsame + nopp = 10` always, and the two tables are one dataset read from opposite ends.

## 10. the Mage source-oob vote — the only column that moved a number

| set | events | clusters | 30m | 60m | 120m | cont% 60m | days cont |
|---|---|---|---|---|---|---|---|
| `mvote = 0 of 8` | 3,800 | 325 | +0.003 | +0.008 | +0.074 | 51% | 53% |
| `mvote = 8 of 8` | 5,252 | 236 | -0.027 | **-0.086** | -0.085 | 45% | 40% |
| `mat = 8 of 8` | 2,068 | 296 | -0.057 | **-0.128** | -0.128 | 45% | 39% |
| `ARRIVED + mvote >= 6` | 3,769 | 337 | -0.029 | **-0.108** | -0.090 | 45% | 37% |
| `ARRIVED + mvote <= 2` | 3,612 | 348 | +0.026 | +0.051 | +0.121 | 52% | 49% |
| `nopp >= 8 + mvote >= 6` | 921 | 204 | **-0.044** | — | — | 45% | 39% |
| `nopp >= 8 + mvote <= 2` | 643 | 197 | **+0.080** | — | — | 57% | 59% |

- the cumulative `mvote >= k` ladder descends monotonically: -0.013, -0.030, -0.051, -0.062, -0.086
  at 60m as k goes 0, 2, 4, 6, 8. It is the one monotone found in the whole exercise.
- inside `nopp >= 8`, the Mage vote moves the result by **0.124** while r's own state moves it by
  **0.002**. Whatever separation exists is on the Mage side, which is consistent with Joe's
  *"treat r as confluence at-best. Mage is the primary"*.
- **all of it is below the measured drag of 0.1975% per trade** (22,000 coins: 8.75 bps slippage
  round trip + 2 x 5.50 bps taker fee). The largest figure produced was -0.128.

## 11. the four worked examples

Chosen from the `ws1Mage oob + mage falls > 0 + bumps <= 2` bucket, taking the extremes in the
direction each window's own mean points. **A and B are in-sample and were NEVER in the 12,992-event
OOS set** — that was found in a sanity check and is easy to forget on return.

| field | A 09-01 17:26:20 | B 09-03 13:59:35 | C 08-27 07:41:30 | D 08-26 13:09:00 |
|---|---|---|---|---|
| window | IS | IS | OOS | OOS |
| in the 12,992 set? | **NO** | **NO** | yes | yes |
| dr | +1 | -1 | +1 | -1 |
| price at the bar | 0.17509 | 0.16255 | 0.20161 | 0.21024 |
| ws1Mage | 95.93 | 12.68 | 87.85 | 0.24 |
| ws12Mage | 34.63 | 78.00 | 25.26 | 70.21 |
| source oob | hi 85 | lo 15 | hi 85 | lo 15 |
| MAGE FALLS | +61.3 | +65.3 | +62.6 | +70.0 |
| mage bumps /11 | 2 | 1 | **0** | **0** |
| lower TFs oob /12 | 2 | 1 | 1 | 1 |
| ws2r | 71.42 | 14.20 | 76.21 | 33.67 |
| ws12r | 46.85 | 71.70 | 91.38 | 15.32 |
| r falls | +24.6 | +57.5 | -15.2 | -18.4 |
| r bumps /10 | 3 | 2 | 6 | 5 |
| `nr` ARRIVED /10 | 0 | 0 | 6 | 2 |
| `reach` | -3.45 | -14.02 | +9.91 | +8.43 |
| `nsame` /10 | 9 | 0 | 9 | 4 |
| `nopp` /10 | 1 | 10 | 1 | 6 |
| `mvote` /8 | **0** | **0** | **0** | **0** |
| `mat` /8 | **0** | **0** | **0** | **0** |
| move% 30m (x dr) | -0.753 | -1.188 | +2.046 | +1.328 |
| move% 45m (x dr) | -1.203 | -1.168 | +2.213 | +2.600 |
| move% 60m (x dr) | -2.279 | -4.329 | +2.535 | +2.895 |
| move% 120m (x dr) | -1.585 | -6.353 | +3.245 | +7.646 |
| raw price at 60m | -2.279% | +4.329% | +2.535% | -2.895% |

### the four ladders

`step` = `dr * -(next rung - this rung)`. Positive = the ladder keeps falling away from the oob end.
`*` marks a bump.

| tf | A Mage | A step | A r | B Mage | B step | B r | C Mage | C step | C r | D Mage | D step | D r |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ws1 | 95.93 | -3.56* | 63.69 | 12.68 | +18.96 | 17.57 | 87.85 | +13.63 | 72.78 | 0.24 | +19.76 | 23.39 |
| ws2 | 99.49 | +45.93 | 71.42 | 31.64 | +16.87 | 14.20 | 74.22 | +2.32 | 76.21 | 20.00 | +8.96 | 33.67 |
| ws3 | 53.56 | +4.29 | 70.23 | 48.51 | +8.10 | 35.53 | 71.90 | +11.47 | 48.62 | 28.96 | +10.26 | 48.30 |
| ws4 | 49.27 | +6.85 | 69.05 | 56.61 | +7.07 | 55.42 | 60.43 | +13.65 | 45.61 | 39.22 | +11.58 | 18.01 |
| ws5 | 42.42 | +4.80 | 81.31 | 63.68 | +3.52 | 62.86 | 46.78 | +7.24 | 55.16 | 50.81 | +5.45 | 10.89 |
| ws6 | 37.62 | +0.39 | 76.62 | 67.20 | +3.15 | 36.97 | 39.54 | +3.56 | 77.32 | 56.26 | +4.36 | 6.57 |
| ws7 | 37.23 | +0.15 | 81.55 | 70.35 | +0.66 | 41.10 | 35.98 | +2.73 | 86.22 | 60.62 | +1.57 | 25.12 |
| ws8 | 37.08 | +1.29 | 74.87 | 71.01 | +3.61 | 43.02 | 33.25 | +1.18 | 94.91 | 62.19 | +2.68 | 21.32 |
| ws9 | 35.79 | +1.85 | 77.21 | 74.62 | +1.50 | 29.02 | 32.07 | +2.08 | 94.24 | 64.87 | +1.83 | 27.02 |
| ws10 | 33.95 | +0.88 | 57.54 | 76.11 | -1.64* | 44.13 | 29.99 | +2.70 | 94.39 | 66.70 | +2.33 | 29.93 |
| ws11 | 33.06 | -1.57* | 48.72 | 74.48 | +3.52 | 48.11 | 27.29 | +2.03 | 88.38 | 69.03 | +1.18 | 29.96 |
| ws12 | 34.63 | — | 46.85 | 78.00 | — | 71.70 | 25.26 | — | 91.38 | 70.21 | — | 15.32 |

### what the four say, and do not say

- the **Mage columns are near-interchangeable**: all four fall +61.3 to +70.0 with 0 to 2 bumps.
  C and D are *cleaner* cascades than A and B by the fitted rule, and they went the other way.
- the four separate on r's trajectory relative to ws1Mage's source oob: A and B head **away** from
  it and 0 of ws3r..ws12r arrive; C and D head **toward** it and 6 and 2 arrive.
- **that separation does not generalise.** §9 tested it both tenses on 83 days and both are null.
- `mvote` and `mat` are 0 for all four, so the Mage vote of §10 does not distinguish them.
- **`nr` is the only column in the entire build that separates A from C**, at 0 against 6, and `nr`
  is null on the population.
- three of the four sit on the opposite side of their own `nsame` bucket mean.
- **ARRIVED matches the sign of all four** — nr = 0 bucket -0.002 with A and B negative, nr > 0
  bucket +0.007 with C and D positive — but at 0.002 and 0.007 against moves of 0.753 to 2.046,
  a factor of 100 to 300.

## 12. what is NOT banked

- no knob, no table, no spec section, no producer. Nothing was promoted out of scratch.
- `ride_to_max.cascade` is untouched.
- the scripts that produced every number above are preserved in `docs/mage_cascade/`, 20 files.
  They import from the live tree and read the cached lines, so they run as-is — **from inside that
  directory**, because several `exec` a sibling by relative path. Smoke-tested there on 0918.
  - `oosbump.py` is the prelude every later script `exec`s: DB config, line spec, tape, the 12 Mage
    and 12 r lines, the Jig price, the dr latch, and the vectorised read.
  - `stopsweep.py` is the 122-trade producer that `joeread.py` scores against.
  - the only hard-coded scratchpad path, in `joeread.py`, was rewritten to resolve beside the file.

## 13. the open items, for the return

1. **Rebuild dr-free.** §8 is the blocker. Raw ladder direction, per-line source oob, raw price
   score, dr compared at the end only. Nothing in §6, §7, §9 or §10 carries over until this is done.
2. **Rule the oob-entry dwell.** 3 bars was reused from `ws1mage_rev.dwell_ok`. Joe has not ruled
   on it and it moves every count (§5).
3. **Rule the source lookback.** "last touched oob" uses an unbounded backward walk. No cap was
   applied, per the standing rule. A capped version is a different measurement.
4. **The 2,818 excluded entries.** ws1Mage entering the oob opposite to dr — Joe's
   masquerading-signal population — has never been looked at, in data or on the pine.
5. **The ws4 turnover.** Both high-bump ladders turn at ws4, the mid-board. The link to the
   blast-radius note (`docs/wsf_setup_model.md` 3.21.2) is observed, not tested.
6. **Size against drag.** Every figure produced is below 0.1975% per trade. Nothing found here
   clears costs, and the hit rates sit at 45% to 63%.
7. **Joe has read A only.** 2026-09-01 17:26:20. B, C, D and the `mat = 8` population are unread
   on the pine.

## 14. the bars Joe has read

| bar | dr | Joe's verdict, 0918 |
|---|---|---|
| 2026-09-01 17:26:20 | +1 | *"lower TFs in OOB, and a procession that falls away from them"* — the bar that started this |
| 2026-09-02 16:24:30 | +1 | *"I disagree"* to my "not the same shape at all"; then *"it has lower TFs in OOB, and a procession that falls away from them"*. **He was right and I was wrong** — both bars have ws1 oob, both Mage ladders fall away, both r ladders fall away |
