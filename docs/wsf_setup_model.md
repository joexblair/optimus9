# the ws-finisher SETUP MODEL

Opened 2026-08-20. Joe: *"this report will be your modelling template. the data I've shared with you
above, forms your initial view. no two `setup`s will be exactly the same so you must learn in ranges,
not in the specifics"*.

Three parts, in order:

1. **JOE'S WORDS** — verbatim, nothing paraphrased.
2. **THE RESEARCH** — verbatim from what was looked up, with sources.
3. **THE MODEL** — spec language, as understood today.

---
---

# PART 1 — JOE'S WORDS, VERBATIM

## 1.1 the stance

> I can only be accurate about the data in the csv file. anything beyond that (domTF,
> wsf-exhausted, x-cross trade signals) are outside of my view. currenlty we're doing our best to
> make the code and the csv interface, but it's a path that we don't need to take imho

> let's flip the stance: create snapshots at each of the csv d and f markers, and compare the d
> snapshots against the f snapshots to find the differences. when you boil that data down to a
> model, we can then look at how to integrate the other mechanics

> the goal is to be able to use the modelling data to match the csv tags

> the entire finisher logic relies on comparision between TFs. start again and build a full TF view
> of the data, per marker

## 1.2 which lines, and which of them carry momentum

> Mage and r - they are the only one's doing work between the (now-non-existant) trade signals

> r is the only line that uses momentum

> you also know that if momentum is true, then a trade cannot fire. this appears often for `d` tags,
> ie `d` is printed because momentum is true

> r-weakness is per-tf. if a TF's r line is IB, then tag that TF as weak. when the model is starting
> to take shape, we'll know how to best use r-weakness bassed on the inter-TF patterns it forms

> inter-TF diff is how we measure weak-mage and weak-r

## 1.3 the momentum rule, and its two corrections

FIRST FORM, then corrected twice. Both corrections are Joe's own.

> IF a momentum-true r line crosses into oob or stalls THEN it's momentum = false (or none). this
> needs to show up in the `verdict` column

The correction that deleted the 0817 wording:

> I've conflated terms. the first statement was meant to target r lines, but I've referred to it as
> if it were machine states
> --delete the 0817 note

The correction that introduced momo-fence-r:

> we need to shrink the fence: ws8 needs to be printing `OOB` at 08:02:50 so that it's momentum is
> none, but I don't want it to be global.
> create a new fence: momo-fence-r  100-{knob:17}

> here is the corrected spec
>   -IF a momentum-true r line leaves momo-fence-r or stalls THEN its momentum = false (or none).

## 1.4 heading, and r IB

> if r is moving towards dr, or away from it
> --this is a new request. I want to know if the r is "heading towards oob-cross/stall", or
> "heading away from oob-cross/stall"

> apply the fence to this mech

Then the correction that removed heading from r IB:

> I've made a judgement error: I can't rely on `heading` to support `r IB`. the reason: r lines
> cannot be relied on - sometimes they are crossing out of the fence later that wsf9of12, and
> sometimes they don't exit the fence at all
> --ws1 and ws2 should be printing yes in r IB. what do you need to change to make it fit?

On the fence that `r IB` tests:

> it's too soon to make a call on this

## 1.5 the read at 07:36:20

> r is `heading away` for TF1,2. r is `heading toward` for 3,4,5,6,7. ws8r is not over 50 (and rd =
> +1), therefore it is momentum = false and not engaged yet

And, on the lookahead in his own ws2 explanation:

> noted - I forgot about the lookahead

## 1.6 THE TEMPLATE — the read at 08:00:55 and 08:02:50

> these are a strong bearish reversal. markers to take note of:
> -ws8 is `away` and close to the fence. verdict is 'none', last-verdict was 'momo'.
> --this inidcates that ws8r has recently reversed (170s ago). when ws8r is in this state,
> wsf-exhaust is declared (per the existing rule).
> ---add a column to track the last-verdict
> -ws1,2,3 are all printing `r IB`, and the ws2/3 verdict is `none`. ws1 is the tail of ws2/ws3 , so
> ws1's momo verdict is less important while ws3 is printing `away` and `none`
> --context: in this particular case, ws1r has already travelled a full cycle (min extrema @
> ~07:58), while ws3r is just leaving the max extrema
> --weak r's (`r IB` = yes), and ws3r/ws2r travelling away from the extrema indicates weakness, and
> confluences the HTF markers
> -ws4,5,6 are all printing away, confirming the other line states
>
> -the next action after `wsf-exhaust`: walk forward. if ws{weak-mage}x-cross has printed, then
> create a trade signal
> --both 08:00:55 and 8:02:50 are strong setups (ws8r reversing, many aways, many ltf `r IB`s), and
> would be a candidate for overriding domTF BLOCK

> this report will be your modelling template. the data I've shared with you above, forms your
> initial view. no two `setup`s will be exactly the same so you must learn in ranges, not in the
> specifics

## 1.7 the rulings on the declaration, the override, and the walk forward

> 4. the rule applies only to ws8r, because 8 is the max finisher TF. curl is as good as momo, as
> long as the curl exits towards `dr`. "close to the fence" is to be derived

> 5. a confluence of the 3. `domTF-override` conditions will evolve with modelling

> 6. walk forward from wsf-exhaust. there's no limit, but there is a lookback caveat that needs to
> be handled coprrectly:
> --there are cases when the x-cross happens just before before ws{max-tf-with-momentum}r stalls or
> exits momo-fence-r. create a {knob:2}*TF-width lookback tolerance to capture and react to the
> missed cross
> ---why would the cross be missed? because we ignore x-crosses while wsf-momoc == true

> 7. search the entire window for more. you can apply the logic to both bearish and bullish signals

> 3. that's your call - I won't use it, but you likely will (the report is the model template)

On the x lines:

> do whatever you need to do. 'x X [Mage, b, boundary]' (race condition) is integral to the spec.
> x X r should be caclulated also

## 1.8 THE GOTCHA — 13:48:05 against 14:20:35

> there's a gotcha that you will come across at the 13:48:05 and 14:20:35 markers: ws8r is in `r IB`
> ----13:48 doesn't create a wsf-exhaust event - 14:20 creates it

> I see slighlty less than 19 turns leaving the fence on TV, but TF8 resolution doesn't show me the
> micro-movements.

And the differentiator, given after the two bars were measured:

> this is the differentiation - weak-mage-tf=none + all Mages are oob is far superior to the 13:48
> setup. all Mages out is a position of strength, so would be a dom-TF-override candidate

## 1.9 the older words this model still rests on

From `ws-finisher_spec.md`, Joe 0817:

> Mage's purpose is to travel from source oob to target oob, in an endless loop, matching the ebb
> and flow of pxs
>
> a smaller TF's Mage forms the tail of a higher TF's Mage
>
> when Mage is oob, it's strength will wane. this waning is the moment of weakness

> to find weakness, the code will scan the Mage values, upwards from TF1 to TF8, to find the first
> mage that is not OOB
>
> the first Mage that prints an IB value, is the weak-mage-tf

> if weak-mage-tf == None and domTF state is FREE, fire a trade signal        [rule C]

> (curl or momo) create wsf-momoc

> 'wsf-exhaust' and 'trade signal' are 2 parts of a dual latch. trade signal cannot fire unless
> wsf-exhaust has fired

> flow = wsf-momoc -> wsf-exhaust -> none -> wsf-momoc. 'none' occurs when a trade fires, or when
> domTF blocks (overrides excluded). wsf-momoc needs to be re-aquired after a none state

> let's rename "none" to `wsf-momo-none`

> all-in-bounds reset has to remain as the dual latch backstop, and now it is alsop the backstop for
> triggering a "none" state

---
---

# PART 2 — THE RESEARCH, VERBATIM

Looked up 0820 at Joe's instruction: *"research online: understand the usage of BB% and StochRSI"*.

## 2.1 Stochastic RSI — what the sources say

> Stochastic RSI is a momentum oscillator that measures the relative strength index (RSI) against
> its own high-low range over a specified period. The RSI is first calculated from price data, then
> this RSI value is processed through a stochastic calculation, producing a final Stoch RSI value
> that ranges between zero and one, or zero and 100, depending on the scale of the charting platform
> used.

> If the trader is using a 14-period StochRSI, they would collect the last 14 RSI readings. From
> those 14 RSI readings, the trader will note the highest RSI and the lowest RSI, which defines
> where the current RSI sits relative to the recent momentum.

> When the Stochastic RSI lines approach 100, this signals that the asset is in a strong uptrend and
> indicates that the RSI is near its highest point in the look-back period. When the indicator
> reaches 100, it's considered saturated or overbought, meaning the RSI is at its highest level
> within the lookback window.

> The standard Stochastic RSI settings are typically set to a 14-period lookback with three
> additional parameters: %K (often set to 3), %D (a smoothing parameter, usually set to 3), and the
> RSI length (typically 14). Compared to regular RSI, it is more responsive and can uncover intraday
> opportunities faster, but the accuracy is better when it is combined with trend filters and volume
> analysis.

Sources: [Tealstreet](https://www.tealstreet.io/indicators/stochastic-rsi) ·
[Alchemy Markets](https://alchemymarkets.com/education/indicators/stochastic-rsi/) ·
[TrendSpider](https://trendspider.com/learning-center/stochastic-rsi-understanding-the-basics/) ·
[TradingView](https://www.tradingview.com/scripts/stochasticrsi/)

## 2.2 Bollinger %B — what the sources say

> %B = (Price - Lower Band) / (Upper Band - Lower Band), which normalizes the price position within
> the bands on a 0-to-1 scale.

> The middle band is usually a simple 20-bars moving average, which serves as the base for the upper
> and lower bands. The Upper Band = Middle Band + 2 * standard deviation and Lower Band = Middle
> Band - 2 * standard deviation.

> The Bollinger Band indicator measures the volatility of closing prices. During periods of high
> volatility, the bands expand and during periods of low volatility, the bands contract.

> When Bollinger Bands are narrowing, we call that a squeeze and it's usually interpreted as a
> signal that a big market movement (volatility) may be coming.

> %B at 1.0 means price is at the upper band; 0.0 means at the lower band; 0.5 means at the middle
> band. Values above 1.0 or below 0.0 indicate price has moved outside the bands.

Sources: [StockCharts %B](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/b-indicator) ·
[TC2000](https://help.tc2000.com/m/69445/l/755844-bollinger-b) ·
[Volatility Box](https://volatilitybox.com/research/bollinger-bands-volatility/) ·
[TradingView](https://www.tradingview.com/scripts/bollingerbands/)

## 2.3 what follows for THESE settings

Joe's configs against the textbook defaults:

| | standard | Joe's | consequence |
|---|---|---|---|
| RSI length | 14 | **5** | a far jumpier input. RSI hits its own extremes often |
| stoch lookback | 14 | **8** | the extreme rolls out of the window sooner, so a pinned line un-pins sooner |
| smoothing | 3 | **7** | r is the average of **seven** stoch readings, not three |
| Bollinger length | 20 | **38** | a slower centre line |
| Bollinger multiplier | **2** | **0.93** | under one standard deviation |

The five mechanics that follow. These are derivations from the formulas above, not measurements:

**M-1. r's speed is capped, and the cap is knowable at the bar.**
r is the mean of the last seven stoch readings, so one new bar moves r by `(incoming − outgoing) ÷ 7`.
The largest possible single-bar move is `100 ÷ 7 = 14.29` points. The value LEAVING the window is
already known, so "what the next reading must beat for r to keep going" is a causal number.

**M-2. saturation has a clock.**
Stoch is 100 only while RSI sits at its own 8-bar high. Stop making new highs and the high sits
still, rolls out within 8 bars, and stoch must fall. A pinned r line therefore has a bounded life of
at most 8 of its own bars — 8 minutes on ws1r, 64 minutes on ws8r.

**M-3. the stoch denominator is a live amplifier, different on every line and every bar.**
`stoch = (rsi − min8) ÷ (max8 − min8) × 100`. A narrow RSI window makes tiny RSI moves swing stoch
hugely. Reconstructed at 08:02:50: ws2r's window width 21.28 so 1 RSI point was worth 4.70 stoch
points; ws8r's width 73.84 so 1 RSI point was worth 1.35. The same price move hit ws2r about 3.5x
harder. **That is not the timeframe — it is the current window width, and it changes bar to bar.**

**M-4. Mage at 0.93 standard deviations is built to saturate.**
At the standard 2 standard deviations price sits outside the bands roughly 5% of the time; at 0.93
it is roughly a third of the time. "Mage is out of bounds" is the NORMAL condition on these
settings. That is what makes Joe's preamble work — *"travel from source oob to target oob, in an
endless loop"*. The narrow band is what creates the loop.

**M-5. Mage can leave its band with no price move at all.**
The denominator is the band width, `2 × 0.93 × standard deviation`. Volatility contracts, the band
narrows, and %B climbs at constant price. A Mage crossing is therefore sometimes a volatility event
and sometimes a price event, and the two are separable.
This also explains the weak-mage scan mechanically: standard deviation grows with the square root of
the window, so the same price excursion produces a smaller Mage displacement as timeframe rises. The
scan up from ws1 finds **the first timeframe where the excursion stops being large relative to that
timeframe's own volatility**. That is Joe's *"a smaller TF's Mage forms the tail of a higher TF's
Mage"*, in numbers.

**CAVEAT ON M-3's NUMBERS.** The per-line widths above come from a direct reconstruction off the
5-second tape, which gave ws8r 73.10 against the banked 84.50. The production line goes through the
Jig — resample to the line's own timeframe, then RSI/stoch/SMA with a separate emerging-bar path.
The MECHANICS hold; the specific widths are indicative until reconstructed on the production path.

---
---

# PART 3 — THE MODEL, IN SPEC LANGUAGE

As understood 2026-08-20. Every rule below traces to Part 1.

## 3.0 scope

- the lines are **ws{tf}Mage** and **ws{tf}r**, tf 1 to 8. Nothing else.
- **only r carries momentum.**
- every test is read on **the bar's own side** — the direction the marker carries.
- the day in scope is 08-04.

## 3.1 THE FENCES — there are two, and they are not the same

| fence | value | what it governs |
|---|---|---|
| the boundary | 85 / 15, from `optimus9_system` | global. `wflb_oob`, the weak-mage scan, `r IB` |
| **momo-fence-r** | **83 / 17**, from `MOMO_FENCE_R` = 17 | the ws-finisher's momentum rule, and `heading` |

- momo-fence-r is Joe's `100-{knob:17}`.
- it is **not global**. Joe: *"I don't want it to be global"*.
- `r IB` still tests 85/15. Joe: *"it's too soon to make a call on this"*.

## 3.2 THE MOMENTUM RULE

    momentum-true  :=  the producer's verdict is momo
                       OR the verdict is curl AND the curl exits TOWARD the direction read

    IF momentum-true AND (the line has LEFT momo-fence-r OR the line is STALLED)
    THEN the verdict reads none

- reading: `state`, not `moment`. The line **is** outside or **is** stalled, for as long as it is.
- **THE CURL DIRECTION IS PART OF momentum-true.** Joe: *"curl is as good as momo, as long as the
  curl exits towards `dr`"*. A curl exiting against the read was never momentum-true, so there is
  nothing for the fence or the stall to take away.
- this is what separates Joe's two gotcha bars. See 3.6.

## 3.3 THE ws8r DECLARATION

    IF ws8r was momentum-true, and is no longer
    THEN wsf-exhaust is declared

- **ws8r only.** Joe: *"the rule applies only to ws8r, because 8 is the max finisher TF"*.
- "close to the fence" — DERIVED on 08-04 from the 19 ws8r turns that left momo-fence-r:
  range **0 to 7 points past the fence**, middle **1.16**, 84% inside 3 points. Joe's template bar
  08:02:50 sits at 1.50 points past, the 58th percentile.
- ws8r turned from momentum to none **130 times** on 08-04. Only **19** came from leaving the fence;
  **73** came from a stall and **38** from the fit turning with neither condition true.

## 3.3b THE wsf-model-report — the fixed format

Joe 0820: *"bank this format as wsf-model-report"*, with the columns given verbatim:

    line | r value | heading | r IB | verdict | stalled | 50 gate | blocked by 50 | last-verdict |
    last-verdict-dwell | Mage value | lb-mage-oob | weak-mage

Produced by `report_wsf_bar.py`. Columns are not added, removed or reordered without Joe's word.

### the banked format, 0821 — 20 columns

Joe 0821: *"update the report format and bank it. it needs to carry your specific data as well as
mine"*. Thirteen columns are Joe's, seven are mine, and the whole set is now the format:

    line | r value | heading | r IB | verdict | stalled | 50 gate | blocked by 50 |
    last-verdict | last-verdict-dwell | Mage value | lb-mage-oob | weak-mage |
    stoch now | stoch out | sat clock | sat left | RSI | RSI lo | RSI hi

| column | whose | what it holds |
|---|---|---|
| r value | Joe | ws{tf}r at this bar |
| heading | Joe | left momo-fence-r -> away; otherwise the sign of the momentum fit's slope |
| r IB | Joe | r inside the 85/15 boundary |
| verdict | Joe | the momentum verdict AFTER Joe's rule - momentum-true and outside the fence or stalled reads `none` |
| stalled | Joe | STALL_N 6 lattice samples with no new extreme |
| 50 gate | mine | the level the line had to reach. Starts at 50, slackens by up to LEVEL_SLACK 13.9 in proportion to how cleanly the line tracks |
| blocked by 50 | mine | yes when that gate is what turned the verdict to none |
| last-verdict | Joe | the verdict held BEFORE the current one |
| last-verdict-dwell | Joe | seconds since the verdict changed |
| Mage value | Joe | ws{tf}Mage at this bar |
| lb-mage-oob | Joe | Mage out of bounds now, or inside the 120 s tolerance |
| weak-mage | Joe | the one line the ws2-upward scan stops at |
| stoch now | mine | the DEVELOPING stoch reading, updated every 5 s |
| stoch out | mine | the oldest closed stoch still in the seven-bar average - what the next reading must beat |
| sat clock | mine | bars since RSI last SET its 8-bar extreme. The developing bar is bar 0 |
| sat left | mine | bars before that extreme must roll out |
| RSI | mine | RSI(5) on the developing bar |
| RSI lo / RSI hi | mine | the stoch denominator. hi minus lo is the amplifier |

THE JOIN MUST PIN EVERY KNOB ON BOTH TABLES. `wsf_line_bar` and `wsf_bar_tf` each hold several knob
sets side by side - that is what their unique keys are for - so a join pinning only some of them
returns one row per COMBINATION. Unpinned, this report printed four rows per line.

## 3.4 THE SETUP — what Joe's template looks like

From 1.6. Learn these as RANGES, not values.

| marker | at 08:02:50 | what it is |
|---|---|---|
| ws8r heading | away | the highest timeframe has turned |
| ws8r distance past the fence | 1.50 points | "close to the fence" |
| ws8r verdict / last-verdict | none / momo | the reversal, 170 s old |
| lines printing `r IB` | ws1, ws2, ws3, ws7, ws8 | weak r's |
| lines printing heading `away` | ws3, ws4, ws5, ws6, ws8 | confirming |
| weak-mage-tf | ws4 | the scan's answer |

Joe's own weighting of these:
- *"ws1 is the tail of ws2/ws3, so ws1's momo verdict is less important while ws3 is printing `away`
  and `none`"*
- *"weak r's (`r IB` = yes), and ws3r/ws2r travelling away from the extrema indicates weakness, and
  confluences the HTF markers"*
- *"ws4,5,6 are all printing away, confirming the other line states"*

## 3.5 THE domTF OVERRIDE

    domTF-override  :=  a confluence of THREE
                        1. ws8r reversing
                        2. the count of lines printing heading `away`
                        3. the count of lines printing `r IB`

- Joe: *"a confluence of the 3. `domTF-override` conditions will evolve with modelling"*.
- **A FOURTH, AND JOE CALLS IT SUPERIOR**: weak-mage-tf = NONE with all eight Mage lines out of
  bounds. Joe: *"weak-mage-tf=none + all Mages are oob is far superior to the 13:48 setup. all Mages
  out is a position of strength, so would be a dom-TF-override candidate"*.
- no thresholds are set on any of the counts. UNSET.

## 3.6 THE GOTCHA, RESOLVED — 13:48:05 against 14:20:35

Both read downward, fence 15. ws8r is inside the boundary at both.

| | 13:48:05 | 14:20:35 |
|---|---|---|
| ws8r | 26.22 | 29.21 |
| producer verdict | curl | sideways |
| **which way the curl ends** | **up** | **down** |
| exits toward the downward read | **no** | **yes** |
| stalled | yes | yes |
| weak-mage-tf | ws1, 6 of 8 Mage out | **NONE, 8 of 8 out** |
| wsf-exhaust | **no** | **yes** |

- every curl ws8r printed from 13:37:45 to 13:56:35 ended **up**, against the read.
- every curl from 14:01:30 on ended **down**, toward the read.
- so ws8r was never momentum-true before 13:48 and there was nothing to exhaust; it WAS
  momentum-true before 14:20 and the stall took it.
- **and the Mage picture separates them a second time**: 14:20 has all eight Mage lines out of
  bounds and no weak-mage-tf at all, which Joe calls a position of strength.

## 3.7 THE WALK FORWARD

    ON wsf-exhaust:
        walk forward with NO limit
        IF ws{weak-mage-tf}x has crossed [Mage, b, boundary]   -- a race, any one of the three
        THEN create a trade signal

        LOOKBACK TOLERANCE: {knob:2} x TF-width
        because x-crosses are IGNORED while wsf-momoc is true, a cross landing just before
        ws{max-tf-with-momentum}r stalls or leaves momo-fence-r would otherwise be missed

- `x X r` is to be calculated as well. Joe: *"x X r should be caclulated also"*.
- **BLOCKED.** `ws{tf}x` is not measured anywhere on this path. Register task #61, open since 0818.

## 3.8 THE STATE FLOW

    wsf-momoc  ->  wsf-exhaust  ->  wsf-momo-none  ->  wsf-momoc

- wsf-momo-none occurs on a trade fire, or when domTF blocks (overrides excluded).
- wsf-momoc must be re-acquired after a wsf-momo-none.
- the all-in-bounds reset is the backstop for the dual latch AND for wsf-momo-none.
- **NOT BUILT.** Five questions are open: what acquiring wsf-momoc means, whether the all-in-bounds
  reset fires wsf-momo-none, whether a domTF block is a moment or a stretch, the starting state, and
  whether one bar can hold two changes.
- `report_wsf_bar.py` prints a footer that reads ONE BAR and carries no history.

## 3.9 KNOBS

| knob | value | where |
|---|---|---|
| `MOMO_FENCE_R` | **17**, so the band is 83/17 | `build_wsf_line_bar.py`, in the unique key |
| `MOMO_KILL` | **state** | `build_wsf_line_bar.py`, in the unique key |
| `MOMO_FIXED_SAMPLES` | **21** | `momo_gated.py` module default, global since Joe 0820 |
| `K_WINDOW` | **4** | momentum window = 4 x tf minutes |
| `STALL_N` | **6** | lattice samples with no new extreme |
| `WMT_LOOKBACK_S` | **120 s** | the Mage tolerance on the weak-mage scan |
| the boundary | **85 / 15** | `optimus9_system` |
| `XCROSS_XWOB` | **5** | `build_wsf_x_cross.py`, in the unique key. 5 s bars x must HOLD on the far side before a crossing counts. 5 bars is the first value that reaches 20 s; 4 stops at 15, because a run of N bars spans (N-1) x 5 s. Measured on 4,426 runs: xwob 5 discards 1,770 (40.0%), the extra bar over 4 costs 263 (5.9%), and the curve has NO knee - it falls smoothly from 15.7% at one bar to 1.8% at twelve |
| the x-cross lookback | **2 x TF-width** | UNBUILT |
| the domTF-override thresholds | UNSET | — |

## 3.9b THE TAIL OF r, and the descending scan. Joe 0820

> the curl that your seeing at 13:48 is in-fact the follow on from a stall. the difference, is that
> the stall happened inisde the fence, instead of outside the fence
> --when a curl happens "inside the fence and close to the fence-edge" (range to be derived), its
> the TF's way of saying that momentum is waning at that TF, ie it is printing weakness
> -when you detect an HTF in weakness, it is the precursor to a reversal.
> --because the weak r is already `IB r` and `away`, we need to use a LTF r to build the tail of r,
> and complete the chain:
> --tail of r: r is a contiuous line that is seen microscopically when viewed at ws{<=1}r, and seen
> coarsely at the HTFs. the HTFs print a wide perspective of the r line, the LTFs handle the
> surgical nature of placing a profitabletrade
> ---search the TFs in reverse order (ie TF 8 to 1) until you find the lowest ws{TF}r that is tagged
> with momentum
> ---follow the reset process, and keep walking forward until you reach a TF that is tagged as
> `away`. (if a TF is marked as away, then we know that it is already aligned to the weak HTF, the
> very thing that we are trying to build the tail on)
> ---when "TF that is tagged as `away`" is detected, the previous TF will declare wsf-exhaust when
> it exits the fence or stalls
> ----ie at ~14:10: TF5 is IB (already weak), and TF4 is exiting momo-fence-r (not weak)

The fallback, given straight after:

> if your descending scan for a momentum produces a null result, then declare wsf-exhaust and trade
> on the ws{weak-mage-tf}x-cross

MEASURED: across the 121 markers, **0** have no r line carrying momentum at the marker bar, so the
fallback never fires at a marker. It can still fire between them.

### the range, left open

Joe 0820, after seeing that the middle inside-fence stall sits 19.87 points in:

> this tells us that we need a confluence. leave the range open for now, we'll have to review this
> when we have more data

Derived on 08-04 and held, not applied: 782 inside-fence stalls on momentum-true lines, middle
19.87 points inside the edge, with only 12.8% inside 5 points. On ws8r alone, 45 events, middle
22.79 points in; Joe's 13:37:30 example at 4.29 points sits in the closest 17.8%.

### what separates ws5 from ws4 at 14:10 — OPEN

Both carry momentum and both are inside 85/15, so `r IB` does not separate them. Two candidates:

| candidate | whose |
|---|---|
| distance from the fence edge — ws5 23.09 points in, ws4 2.52 points in | mine |
| `last-verdict` and `last-verdict-dwell` | Joe's instinct, 0820: *"without seeing the table, my instinct tells me that `last-verdict` and `last-verdict-dwell` would be more reliable"* |

## 3.9c THE WALK — the rule as tested, and how it scored. 0821

Joe 0821: *"starting at 00:00, walk forward. at each wsf9of12 event, create the report and run your
tests. --if you recognise the pattern ---stop walking, print the report, and tell me your verdict"*.

### the rule, exactly as run

    at each wsf9of12 event, read on the marker's own side:

      momentum-true := the producer says `momo`
                       OR it says `curl` AND the curl exits TOWARD the read

      the tail-builder := scanning ws8 DOWN to ws1, the LOWEST line that is momentum-true

      FIRE  if the tail-builder has LEFT momo-fence-r or IS STALLED on this bar
      FIRE  if NO line is momentum-true          (Joe's null-scan fallback)
      DELAY otherwise

### the first five events

| event | side | domTF | tail-builder | its state | verdict | Joe's tag |
|---|---|---|---|---|---|---|
| 00:08:20 | up | BLOCKED | ws1r | 70.77, inside the fence, not stalled | delay | f |
| 00:18:35 | down | FREE | ws2r | 19.94, inside the fence, not stalled | delay | d |
| 01:00:45 | down | BLOCKED | ws2r | 47.02, inside the fence, not stalled | delay | d |
| 01:05:35 | down | BLOCKED | ws2r | 37.19, inside the fence, not stalled | delay | f |
| **01:07:30** | down | BLOCKED | **ws3r** | **33.60, stalled** | **FIRE** | **f** |

### HOW TO SCORE AGAINST THE TAGS — Joe 0821

I first scored this 3 of 5, counting 00:08:20 and 01:05:35 as misses. Joe corrected it:

> you're too hard on yourself: 1:05 and 1:07 are the same price, therefore your call is perfect.
>
> 1:08 was only the starting trade that the code walk needed - your d verdict is perfect

Measured: 01:05:35 sits at 0.130874 and 01:07:30 at 0.130679 — **0.15% apart, 115 seconds apart**.
The same event, not two.

**THE TAGS MARK A SETUP, NOT A BAR.** Scoring them bar-exact manufactures misses that are not
misses. Two adjacent events at the same price are one event. The walk scored **5 of 5**.

### what the walk has NOT shown

Calling every one of those five `delay` would also have matched four of them. The only event that
separates the rule from that is 01:07:30. Five events is the whole sample.

### 01:07:30 — what the fire looked like

| what | value |
|---|---|
| ws8r, ws7r, ws6r | 0.00, 1.85, 1.08 against a 15 fence — all outside momo-fence-r, all stalled |
| their last-verdict | `momo` on all three, held 1,170 s / 1,110 s / 1,435 s |
| their saturation clocks | 0 with 7 bars left on all three — fresh extremes, stoch pinned at 0.00 |
| ws3r, the tail-builder | curl exiting **down** toward the read, so momentum-true; stalls on this bar, unstalled 30 s earlier at 01:07:00 |
| ws3r's position | 33.60, **inside** the fence |
| weak-mage-tf | ws4, only 3 of 8 Mage lines out — NOT the all-eight condition |

The stall is inside the fence, which at 13:48:05 Joe called weakness rather than exhaust. The
difference here is that ws3r **is** the tail-builder and the high timeframes are already spent
behind it.

## 3.9d THE TRIGGER, THE BOARD, AND THE BAND. Joe 0821

### the teaching

Joe 0821 exposed that the walk only ran at the 121 wsf9of12 timestamps - **0.70% of the day**, with
17,160 bars never looked at. His example:

> we need to add wsf-exhaust to the test's cadence, but we can't declare wsf-exhaust without the
> model data
> --without model-data:
> ---ws7r exits the fence, ws8r is in momo - the walk waits for ws8r to exit the fence
> --with model-data:
> ---ws7r exits the fence,
> ---Mage is weak at TF3 (the lower the TF, the more weak the market it),
> ---ws8r is `r IB` and far away from a fence exit (ie ws8r is too weak to catch up with ws7r)
> ---verdict: weak Mage and weak ws8r = wsf-exhaustion, exit on ws{weak-mage-tf}x-cross ~02:00

MEASURED at 01:57:15, read upward: ws7r crossed out at 83.63 carrying momo with a dwell of 0 s, and
ws8r sat at 55.05 inside the fence heading toward it - **29.95 points from an exit**. Joe's read
reproduces. (One difference: the weak-mage scan answers **ws1**, not ws3; ws3Mage at 70.70 is the
lowest Mage on the board, which is what Joe was reading.)

**THE TEACHING.** The declaration is not "line X does thing Y". A line exiting the fence or stalling
is the **trigger to LOOK**; the **board decides**. That is why 01:07:30 (tagged f) and 05:52:10
(tagged d) have IDENTICAL triggers and opposite answers - the difference was never in the trigger.

### the cadence

| | count on 08-04 |
|---|---|
| bars in the day | 17,281 |
| wsf9of12 signal bars | 121 |
| **fence exits carrying momentum** | **418** |
| **stall starts carrying momentum** | **1,025** |
| **total trigger events** | **1,443** |

Evaluating on the trigger costs 8% of evaluating every bar and has the same coverage for this
mechanic. The timing measurement says neither is a cost problem.

### the direction between signal bars — ANSWERED

A line's fence exit depends on which way it is read: ws7r at 83.63 is OUTSIDE momo-fence-r read
upward and INSIDE it read downward, same bar, same value. At a signal bar the marker carries a side;
between them nothing does.

Joe 0819, D11: *"to be more precise, it's the direction of the open position"*. So the read carries
the last marker's side forward. At 01:57:15 the standing side is UP, carried from 01:46:55, which
is the direction Joe's own read used.

### THE BAND — how a threshold is expressed until it is tuned

Joe 0821, on being asked for the board test in numbers:

> agreed, and honestly: neither can I. this is a modelling question, we will learn the values
> through trial and error.
> --for now and so that you have a level of context, create a 8 sized fence around the current
> non-thresholded values. ie, the "too weak to catchup" threshold becomes ~26 to ~34 (4 before and
> 4 after 29.95)

**THE CONVENTION: an untuned threshold is a BAND of the observed value plus or minus 4, 8 wide.**
Not a single number. Every threshold derived from a single observation is written this way until
trial and error narrows it.

| threshold | observed | the band |
|---|---|---|
| "too weak to catch up" — the highest momentum-carrying line's distance to its own fence | 29.95 at 01:57:15 | **26 to 34** |

## 3.11 IDEAS TO TEST AFTER THE FIRST WALK

Opened 0821 at Joe's instruction. Nothing in here is built, and nothing in here runs until the first
walk is complete and reported.

### idea 1 — the ws1Mage re-entry gate. Joe 0821

> the first idea: if wsf-exhaust is declared while ws1Mage is IB, code should walk forward until
> ws1Mage is dr-side oob and crossing back into IB

- so a declared wsf-exhaust does NOT release the x-cross hunt straight away when ws1Mage is inside
  bounds at the declaration.
- the walk instead waits for ws1Mage to go OUT of bounds on the direction's own side, and then
  cross back IN, before the hunt is allowed to fire.

WHAT EXISTS: `wsf_bar_tf` carries `wbt_mage`, `wbt_mage_oob` (out of bounds on that direction's side
at this bar) and `wbt_mage_ago_s` (seconds since it last was), per timeframe per direction, on all
17,281 bars. The out-and-back-in crossing itself is not built.

OPEN: whether the out-and-back needs an xwob hold of its own, and which boundary counts as IB here -
the global 85/15 or momo-fence-r at 83/17.

**Task #3** in the register.

## 3.10 WHAT IS NOT BUILT

| | state |
|---|---|
| the curl-direction test inside momentum-true | **DEFECT — 2,797 rows across 08-04 are wrongly momentum-true, 408 of them on ws8r** |
| the saturation clock, and the incoming threshold | cleared by Joe, not started. Must go through the Jig's resample path |
| splitting Mage crossings into price-driven and volatility-driven | cleared by Joe as my call, not started |
| `ws{tf}x` and its crossings | not measured anywhere. Blocks 3.7 |
| the three-state flow | five open questions. See 3.8 |
| the domTF-override thresholds | UNSET |
| searching the whole window for more setups | not started. Both directions, per Joe |

---

## THE REPORT IS NAMED — wsf-model-report, and its domTF sibling

Joe 0820 named this one: *"bank this format as wsf-model-report"*. Joe 0823 named the pair:
*"name both model reports (dtf and wsf), and add the format specs to documentation"*.

    wsf-model-report   ws1 to ws8.   Direction from the wsf9of12 signal's own side.
                       Footer: wsf-momoc / wsf-exhaust / wsf-momo-none.
    dtf-model-report   ws13 to ws27. Direction from the ws27x guide-wire excursion.
                       Footer: dtf-blocked / dtf-free.

ONE format, twenty columns, shared by both. The full spec and the domTF differences are in
docs/domTF-finisher_spec.md under "THE dtf-model-report". Joe 0823: *"this report will be based on
the existing wsf model report"*.

Joe 0823 on which of the seven added columns have earned their place: *"my memory thinks that you
didn't find a use from the stoch column, but the rsi data was useful. we'll understand the data
further as we uncover the flip moments and analyse the dtf report"*.

---

## WHAT wsf DOES WHEN dtf DELEGATES — Joe 0823

The handover contract. Joe 0823 dropped the domTF handoff as an event and replaced it with a
delegation: *"when dtf flips to dtf-free, it needs to delegate to wsf (who will manage the trade
creation)"*.

Joe 0823, the three questions wsf answers on delegation, verbatim:

> when dtf-free delegates to wsf, wsf will decide on 3 things
> 1) am I in trade? if I'm in trade, is the model telling me to exit or hold the trade
> 2) which way am I facing? wsf's dr will be set by the positioing of gcws30Mage, ws1Mage and
>    ws2Mage - if they are all > {100 - knob:20 fence} then dr = +1
> 3) what state am I in? wsf-momoc, wsf-momo-none, or wsf-exhaust
> --when wsf knows all 3, it can make a decision: hold and walk, or create a trade signal

Joe 0823 on why the delegated direction and domTF's carried direction need not agree: *"this is
also by design"*. Two of the three allowed exhaust events before 04:00 fire against the direction
domTF was last carrying - 01:52:15 at wsf dr +1 inside a dtf dr -1 free run, and 03:23:05 at wsf
dr -1 inside a dtf dr +1 free run. **wsf sets its own dr; it does not inherit domTF's.**

Joe 0823 on why a no-direction dtf bar reads free: *"this is by design, and it fits perfectly. wsf
needs to be able to handle the smaller trades without being blocked by dtf - the 02:18 scenario is
a perfect example of this"*.

### THE NEW FENCE — a THIRD one, and it is not 85/15

    {100 - knob:20} = 80
    gcws30Mage AND ws1Mage AND ws2Mage all above 80  ->  wsf dr = +1

The system fences are 85/15 and momo-fence-r is 83/17. This is a third, at 80.

### QUESTION 2, SETTLED 0823

    the fence            {100 - knob:20}  ->  80 / 20
    gcws30Mage AND ws1Mage AND ws2Mage ALL above 80   ->  wsf dr = +1
    gcws30Mage AND ws1Mage AND ws2Mage ALL below 20   ->  wsf dr = -1
    they do not all agree                             ->  NO dr. Capture the moment in a stub
    NO HOLD. There is no xwob on this reading

Joe 0823, answering each gap in turn:

| # | the gap | Joe's answer, verbatim |
|---|---|---|
| 1 | the dr -1 case | "I've described a fence: {100 - knob:20 fence}, therefore below 20 must be logical" |
| 2 | the three do not agree | "if the Mages don't agree then capture the moment in a stub and we can investigate" |
| 3 | does it need a hold | "when Mages reverse, profit begins to dwindle, and a hold just increases that loss of profit. no holds - the lines are either all outside the fence, or not at all" |
| 4 | does it replace the wsf9of12 side | "this is standalone reaction created when dtf delegates to wsf. wsf9of12 is a marker used by wsf to time wsf-level decisions" |

**IT IS A FENCE, NOT TWO THRESHOLDS.** Joe's answer to gap 1 is the reason: he gave one number,
{knob:20}, and a fence made from it. 80 and 20 are the same knob.

**NO HOLD IS A DELIBERATE CHOICE WITH A STATED COST.** Every other wsf crossing carries an xwob.
This one does not, and Joe's reason is that a hold spends profit: "when Mages reverse, profit
begins to dwindle, and a hold just increases that loss of profit".

**THE TWO wsf DIRECTIONS DO NOT COMPETE.** Gap 4 settles it: this reading is a standalone reaction
at the moment domTF delegates. The wsf9of12 signal keeps its own side and its own job - it is the
CLOCK that times wsf-level decisions, not the source of this dr.

### THE STUB — buildable, one choice outstanding

When the three Mage lines do not all sit on one side of the 80/20 fence, the moment is recorded and
nothing acts on it. Same shape as the shrink stub in build_ws_fin.py, Joe 0814: "create a stub, let
it tell us when it happen".

NOT SETTLED: whether the stub records **every bar** the three disagree, or **only the bars where
domTF delegates**. The two differ by orders of magnitude - delegation happens a handful of times a
day, disagreement could be most of it.

---

## 3.12 THE MATRYOSHKA ORDER — Joe 0824

Joe 0824, verbatim:

> a lower TF (~1 to ~4) r line will always stall or curl before the higher TFs - it's the matryoshka
> nature of lines sharing the same config. this means that when you see a collection of LTF r's in
> the 'away' state while some HTFs are still printing 'toward', and maybe with a larger verdict
> dwell, you can visualise the r line curling (reversing) in a per-TF falling dominoes effect. ie,
> the LTFs are leading the way

WHY IT MATTERS TO THE MODEL. Section 3.4 counts `away` lines as a flat total. This says the count is
not the whole signal - **WHICH** timeframes are away carries information the count throws away. A
board with ws1 to ws4 away and ws5 to ws8 still toward is a reversal in progress with the higher
timeframes still to fall. The same count spread differently is not the same setup.

It also explains why the order is guaranteed rather than incidental: every ws{n}r shares one config,
7|5|8|close, and differs only in bar width. A shorter bar reaches its turn first by construction.

WHAT THE SETUP ROW CARRIES BECAUSE OF THIS, none of it thresholded:

    away_tfs / toward_tfs   which lines, not just how many
    away_max_tf             the highest timeframe already away
    toward_min_tf           the lowest timeframe still toward
    ltf_away_n              of ws1..ws4, how many are away      <- Joe's "~1 to ~4"
    htf_toward_n            of ws5..ws8, how many are toward
    away_dwell_max          the largest last-verdict-dwell among the away lines. Joe: "and maybe
                            with a larger verdict dwell"

NO THRESHOLD IS SET ON ANY OF THEM. Joe 0823: "no two `setup`s will be exactly the same so you must
learn in ranges, not in the specifics" - the ranges come from his labels, not from me.

---

## 3.13 THE SETUP MODEL DATASET — built 0824

Joe 0824: *"store the template report as the first dataset, and add this new 00:13 dataset to expand
your knowledge"*, and *"going forward, I'll be working with you on training the model at each of the
validated dtf-free timestamps"*.

`build_wsf_setup_model.py` -> two tables. Nothing is recomputed; both are a query over
`wsf_line_bar` and `wsf_bar_tf`, the same join `report_wsf_bar.py` uses.

| table | grain | holds |
|---|---|---|
| `wsf_setup_board` | one row per setup x line | the 20 wsf-model-report columns, ws1..ws8 |
| `wsf_setup` | one row per setup | the derived features, Joe's verdict, his own words |

### THE FEATURES ARE JOE'S. NO THRESHOLD IS SET ON ANY OF THEM.

| feature | from |
|---|---|
| `away_n`, `away_tfs` | section 3.5 condition 2 |
| `rib_n`, `rib_tfs` | section 3.5 condition 3 |
| `ws8_heading` / `ws8_verdict` / `ws8_last` / `ws8_dwell` | section 3.5 condition 1, the reversal and its age |
| `ws8_past_fence` | Joe's *"close to the fence"*. Measured against **momo-fence-r 83/17**, not 85/15 |
| `weak_mage_tf`, `all_mage_oob` | section 3.5's fourth, which Joe rates superior |
| `toward_n/tfs`, `away_max_tf`, `toward_min_tf`, `ltf_away_n`, `htf_toward_n`, `away_dwell_max` | section 3.12, the matryoshka order |
| `state` | the wsf-model-report footer |
| **`verdict`, `strength`, `notes`** | **Joe. Not derived.** |

### THE TWO ROWS BANKED AT 0824

| setup | dr | verdict | ws8 heading | ws8 verdict / last | ws8 dwell | past fence | away | r IB | weak-mage | all Mage oob | state |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 08:02:50 | +1 | SHORT | away | none / momo | 155 s | 1.50 | 5 | 5 | ws4 | | wsf-momo-none |
| 00:13:00 | +1 | SHORT | away | sideways / — | 780 s | 2.21 | 6 | 7 | NONE | yes | wsf-exhaust |

**THE 08:02:50 ROW REPRODUCES JOE'S SECTION 3.4 EXACTLY** - away on ws3,4,5,6,8; r IB on
ws1,2,3,7,8; weak-mage ws4; ws8r past the fence by 1.50. That is the check that the derived features
are reading what Joe read.

**dr AT 08:02:50 IS +1, NOT -1.** Joe called it *"a strong bearish reversal"*, and bearish is SHORT,
and SHORT is dr +1. `ws_fin_9of12` stamps that bar +1 independently. Read at dr -1 the board shows
one `away` line instead of five - the template does not survive the wrong direction.

### WHAT SEPARATES THE TWO ROWS

Both are SHORT. They differ on every one of the template's four conditions:

    08:02:50   ws8r REVERSED - none, last-verdict momo, 155 s old.  weak-mage ws4.   away 5, r IB 5
    00:13:00   ws8r sideways, no last-verdict, 780 s.  weak-mage NONE + ALL Mage oob.  away 6, r IB 7

So the second row is the case where the FOURTH condition carries the setup on its own - Joe:
*"weak-mage-tf=none + all Mages are oob is far superior to the 13:48 setup"* - while the first
condition, the ws8r reversal, is absent.

### THE RISK, ON THE RECORD

Two labelled rows against 83 unlabelled delegation moments on 08-04 alone. Any rule fits two points.
The guard is the shape: six count-based features, every one Joe's, and **the honest test is 08-05
run cold**. In-sample agreement will not be reported as a result.

---

## 3.14 START HERE TOMORROW — 0825

Joe 0824: *"the 85 dtf-free events are validated, so we'll continue our wsf modelling on the next
timestamp (00:14:50) tomorrow"* and *"make sure you have good notes in the spec docs so that you can
hit the ground running and test what you've learnt"*.

### THE NEXT TIMESTAMP IS 00:14:50

That is `dtf_delegation` row 3. What the root table already says about it:

| field | value |
|---|---|
| delegated | 00:14:50 |
| the free run holds | **1,455 s = 24.3 min** |
| dtf dr carried in | **+1** |
| gcws30Mage / ws1Mage / ws2Mage | 39.84 / 62.38 / 76.00 |
| wsf facing at the bar | **none** — no line clears 80, none is below 20. A STUB row |
| last all-3-out bar | 00:12:10 at **dr +1**, lag **2m40s** |

### THE EXACT NEXT STEP

    python3 report_wsf_bar.py 00:14:50 up

Then read the board against section 3.4 and 3.12 BEFORE asking Joe anything. Joe 0824 on why:
he let the 00:13:00 call be wrong first, and *"you reviewed what you know about line positioning,
direction, and recent verdict changes and compared against the model ... and made a good call"*.

### WHAT I GOT WRONG AT 00:13:00, SO IT IS NOT REPEATED

- I read many `away` prints as the board turning against the trade. **They are Joe's CONFIRMING
  signature** — section 3.4, *"ws4,5,6 are all printing away, confirming the other line states"*, and
  the `away` count is condition 2 of the domTF-override.
- I read many `r IB` prints as nothing to lean on. **They are the weak r's the template counts as
  strength.**
- I read weak-mage NONE as a gap. **Joe rates all-Mages-out as SUPERIOR** to his own 13:48 setup.
- **dr +1 is SHORT.** Not LONG. The plus sign reads like "up" and that is the trap.

### THE THREE QUESTIONS wsf ANSWERS AT A DELEGATION, Joe 0823

    1) am I in trade? if in trade, does the model say exit or hold      <- NO TRADE STATE EXISTS YET
    2) which way am I facing?  the three Mage lines at 80/20, no hold   <- in dtf_delegation
    3) what state am I in?  wsf-momoc / wsf-momo-none / wsf-exhaust     <- the report's footer

Only 2 and 3 are answerable today. Question 1 has nothing built behind it.

### AFTER THE READ

`build_wsf_setup_model.py` holds the labelled setups in a `SETUPS` list at the top - utc, dr,
verdict, strength, notes. Add the row, run it, and both tables refresh.

### THE GUARD, and it is Joe's own

> *"no two `setup`s will be exactly the same so you must learn in ranges, not in the specifics"*

Three labelled rows after tomorrow, against 82 unlabelled delegation moments. **The honest test is
08-05 run cold.** In-sample agreement is not a result, and will not be reported as one.

## 3.15  0824 close — the 00:14:50 state row, and a mode Joe has asked for but not named

**Joe's correction to the 00:14:50 verdict block**, verbatim:

    │ state                       │ wsf-momo-none             │ wsf-momoc on the non-existant #2 gate │

**THE STATE FOR THIS BAR IS `wsf-momoc`.** Joe settled it and then had to say so twice. His own
words, 0824: *"I overrode the wsf-exhaust state for 00:14:50, and I printed wsf-momoc"*. My verdict
block had printed `wsf-exhaust`; that is what he struck out. The middle cell, `wsf-momo-none`, is
the reading you get IF gate 2 applies. The right-hand cell is the state that stands, and it stands
because gate 2 does not exist in the report path.

The verdict itself is unchanged and Joe agreed it: **SHORT, dr +1**.

**Joe's second call**, verbatim:

> "this is a happy accident - it shows me that the wsf-report would benefit from a curl-detection
> mode that excludes gate 2, so that the curl and its dr can contribute to your modelling"

NOTHING BUILT. Held at BUILD-GATE, task #6. The mode has no name yet — Joe names his mechanics.

**Correction banked here so it is not repeated.** On 0824 I called `wflb_verdict` being fed the
UNGATED verdict a defect and offered a one-line fix. It is not a defect. `build_wsf_line_bar.py`
line 18 records Joe 0818: *"wsf states are a continuous flow, to be queried when wsf9of12 fires.
for this reason, curl cannot be gated"*. The ungated feed is Joe's instruction. The fix is
withdrawn.

**The gate-by-gate reading at 00:14:50, dr +1** — the evidence behind Joe's state row:

| line | r | raw fit | gate 1 slope | gate 2 bend | gate 3 fit | bend | ends | killed | if gate 2 gone |
|---|---|---|---|---|---|---|---|---|---|
| ws1 | 13.61 | none | | | | −6.07 | | yes | — |
| ws2 | 46.17 | none | | | | −13.98 | | yes | — |
| ws3 | 73.02 | none | | | | −53.34 | | yes | — |
| ws4 | 77.55 | curl | REJECT | REJECT | pass | −55.77 | down | yes | none |
| ws5 | 80.51 | curl | pass | REJECT | pass | −41.03 | down | yes | curl |
| ws6 | 83.61 | curl | pass | REJECT | pass | −27.66 | down | yes | curl |
| ws7 | 71.31 | curl | pass | REJECT | pass | −27.31 | down | no | curl |
| ws8 | 86.48 | sideways | | | | −2.98 | | no | — |

Gate 2 asks, at dr +1, for a bend that ends UP. Every bend on this board ends DOWN, so gate 2
rejects all four curls. Gate 1 additionally rejects ws4 on its slope, so removing gate 2 alone
still leaves ws4 at none.

Every column needed to run the mode is already banked on all 276,496 rows — `wflb_aligned`,
`wflb_bend`, `wflb_bend_align`, `wflb_bendfit`, `wflb_curl_ends`. No rebuild.

### 3.15.1  wsf-curl-mode — Joe's six answers, and the measurement that stopped the build

**Joe 0824 named it: `wsf-curl-mode`.** His answers to the six concretions, verbatim:

| # | question | Joe |
|---|---|---|
| 1 | the name | **wsf-curl-mode** |
| 2 | gate 2 only, or gate 1 as well | "gate 2 only" |
| 3 | does momentum-kill apply | "yes. momentum flipping from true to false (your 'momentum-kill') is part of the line's lifecycle" |
| 4 | dtf-model-report too | "yes" |
| 5 | does curl_dr print on its rows | "no change to my 0824 rule" |
| 6 | does it feed the state footer | "indirectly, yes. the state footer is derived by you, based on your interpretation of all fields in the wsf-model-report" |

**BUILD HALTED AGAIN. Nothing written.** The reason is arithmetic, not preference.

    the report's `verdict` column = raw fit + momentum-kill.  NO gates at all.
    wsf-curl-mode as specified  = raw fit + gate 1 + gate 3 + momentum-kill.

wsf-curl-mode is therefore a **strict subset** of the column already in the report. It can only turn
a curl into a none. It can never surface a curl the report is currently hiding.

**Measured over all 276,496 banked rows, 08-04, both directions, ws1 to ws8:**

| population | bars | unbroken runs |
|---|---|---|
| raw fit says curl | 42,765 | |
| `verdict` prints curl (kill did not fire) | 10,181 | |
| wsf-curl-mode keeps the curl | 8,532 | |
| — of those, gate 2 alone rejects it (the bend points against dr) | 2,424 | 505 |
| wsf-curl-mode turns the curl to none | 1,649 | 348 |
| — gate 1, the slope points against dr | 770 | |
| — gate 3, the bend does not describe the window | 1,105 | |

The 2,424 bars in 505 runs are the population Joe's sentence points at — *"so that the curl and its
dr can contribute to your modelling"*. **They already print `curl` in the report today, and nothing
marks them.** wsf-curl-mode as specified does not mark them either; it removes 1,649 other bars.

Put to Joe, not decided: whether wsf-curl-mode is the narrowing filter he specified, or a marker on
the gate-2-rejected curl.

**Two facts found while scoping, both stated to Joe:**

1. `report_wsf_bar.py` lines 186-197 PRINT a footer line `STATE AT THIS BAR:` derived mechanically
   from the verdict column. It read `wsf-momoc` at 00:14:50, and `wsf-momoc` is the state Joe
   settled. The printed line and Joe's state AGREE at this bar. (This paragraph said the opposite
   until 0824 and was one of the three places the inverted reading survived.)
2. **There is no dtf-model-report script and no per-bar momentum table for ws13 to ws27.** The
   01:21:05 dtf-model-report was produced by ad-hoc query. Answer #4 lands in the format spec; it
   cannot land in code until that report exists.

### 3.15.2  corrections and scope, 0824 close

- **CORRECTION.** My 00:14:50 verdict block printed the state as **wsf-exhaust**. Joe overrode
  that, and the word he printed is **wsf-momoc**. My later sentence — "that printed line read
  wsf-momoc ... your correction to wsf-momo-none overrode it" — is backwards and is withdrawn.
- **SCOPE, Joe 0824**: *"leave dtf for now, we'll add the curl_dr/no-gate-2 logic when we need to.
  wsf is the primary focus for now"*. The dtf half of answer #4 is parked, not cancelled.
- **CONFIRMED, Joe 0824**: curl_dr is already derived from the momentum mechanism. It reads
  `wflb_curl_ends`, which is the sign of `wflb_bend` — the leading coefficient of the quadratic
  that `momo_core.momo_fit()` fits over the line's own window. It is banked on every row where the
  raw fit said curl, gates or no gates, which is all four lines at 00:14:50 including the three
  that print blank.

### 3.15.3  wsf-curl-mode — BUILT 0824

Joe 0824: *"why wouldn't you add the modes (no gate 2, curl_dr produced) to the momentum mech, and
call that mode into the wsf-model-report?"* then *"go for it"*. The halt in 3.15.1 is lifted; the
subset arithmetic there still stands and Joe has seen it.

**Where it lives.** `optimus9/compute/momo_gated.py` — the file that already holds Joe's 0805 gates.

    momo_g_why(r, dr, w, quad='auto', gate2=True)     gate2=False is wsf-curl-mode
    curl_gates(f, gate2=True)                          the three gates, lifted out, ONE home

`curl_gates` was lifted out of `momo_g_why` so a caller holding the MEASUREMENTS but not the series
runs the same gates instead of a copy. `report_wsf_bar.py` is that caller — it reads the five
banked fields back out of `wsf_line_bar` and hands them to the same function:

    aligned       the slope points with dr        wflb_aligned
    quad          a bend was measurable           wflb_bend_align IS NOT NULL
    quad_aligned  the bend points with dr         wflb_bend_align
    quad_r2       the bend's own r-squared        wflb_bendfit
    quad_why      why no bend                     not banked, optional

The fork this prevents already happened once, in `report_domtf_walk.py`.

**The default is `gate2=True`, so every existing caller is untouched** — build_ws_fin,
build_wsf_line_bar, jig, the s46 path.

**PROVEN, twice, over the whole banked set:**

| check | readings | mismatches |
|---|---|---|
| `curl_gates(gate2=True)` from banked fields vs banked `wflb_gated` | 276,496 | **0** |
| `momo_g_why()` re-run end to end vs banked `wflb_gated` and `wflb_ungated` | 276,496 | **0** |

**The report column.** `wsf-curl-mode`, placed immediately after `curl_dr`. It prints only on rows
where the producer's raw fit said curl — the rows the gates act on. Joe's momentum-kill is applied
first, per his 0824 call *"momentum flipping from true to false ... is part of the line's
lifecycle"*, so a killed curl reads `none` before any gate runs. Joe's 0824 curl_dr rule is
unchanged: curl_dr still prints only where `verdict` = curl.

**NOT banked to the database.** No column was added to `wsf_line_bar` and no rebuild was run. The
five inputs are already there, so the mode is a query-time reading.

**At 00:14:50, dr +1, the new column reads IDENTICALLY to `verdict`** — ws7 `curl`, ws4/ws5/ws6
`none`, the rest blank. That is the subset arithmetic in 3.15.1 showing up in the output: the
column can only ever turn a curl into a none, and at this bar the momentum-kill had already done it.

The printed footer line reads `wsf-momoc - momentum on ws7r`, and that is the state Joe settled
for this bar. See 3.15.

### 3.15.4  the wsf-model-report header is two lines, 0824

Joe 0824: *"print the column names on 2 lines so that the report fits in my screen"*.

- **No column is renamed.** Each name splits at its own hyphen or space, never mid-word:
  `r value` -> `r` / `value`, `curl_dr` -> `curl` / `dr`, `wsf-curl-mode` -> `wsf-curl` / `mode`,
  `blocked by 50` -> `blocked` / `by 50`, `last-verdict-dwell` -> `last-verdict` / `dwell`,
  `lb-mage-oob` -> `lb-mage` / `oob`, `RSI lo` -> `RSI` / `lo`, and so on. `heading`, `verdict`,
  `stalled` and `line` have no break point and stay on the top line.
- **Widths are now computed from the data**, not hardcoded padding. Each column is as wide as the
  widest of its two header halves and its own values.
- **257 characters wide before, 196 after** — 61 narrower, and one row per line is preserved.

## 3.16  MODELLING LESSON — r at the floor: momo behind it, none now

Joe 0824, verbatim, given at 08-04 00:52:30 on dr -1:

> "the HTF r lines are all low on the board while verdict is none, after verdict being momo.
> --this equates to 'r has dropped to the ~floor' (momo), and has nowhere to go (none)"

**The reading.** A high-timeframe r line sitting near the floor with `momo` as its LAST verdict and
`none` as its verdict now is not a line that failed to move. It is a line that already made the
move — `momo` is the travel, and `none` is the arrival. There is no board left in front of it.

**The board that produced the lesson**, 00:52:30, dr -1, fence 15:

| line | r value | verdict | last-verdict | last-verdict dwell |
|---|---|---|---|---|
| ws5 | 8.10 | none | momo | 1035 s |
| ws6 | 3.30 | none | momo | 520 s |
| ws7 | 8.55 | none | momo | 195 s |
| ws8 | 15.82 | none | momo | 255 s |

ws4 also carries `momo` behind a `none`, at r 33.73 with a 1215 s dwell — further from the floor
and the longest dwell on the board.

**Joe confirmed the state**: *"your verdict is correct - good work"* on `wsf-exhaust - no r line
from ws1 to ws8 carries momentum`.

**Why this is not the same as the ws1-ws3 group reading `none`.** ws1 77.38, ws2 73.28, ws3 47.26
also read `none`, but their last verdicts are `sideways`, `sideways` and `curl` - no travel behind
them. The lesson is the PAIR: floor position AND `momo` as the previous verdict. Either alone says
something different.

**Banked as setup row 4**, the first on dr -1. Verdict `hold and walk` - wsf has no direction of its
own at this bar because the delegation is a stub: gcws30Mage 58.95, ws1Mage 36.56, ws2Mage 30.23,
none of the three outside Joe's 80/20 fence.

Relates to 3.12, the matryoshka order - there the LOW timeframes lead. Here the HIGH timeframes are
the ones that have finished.

### 3.16.1  thread status, 0824 close

- **the pine read is closed.** Joe 0824: *"pine is outdated now - that read can be closed"*. The
  `eyes_on_pine` table was NOT edited - no row was named, and it is Joe's table. The open-coverage
  note about it stops being reported.
- **dormant, on Joe's word**: task #3 the ws1Mage re-entry gate, task #4 the ELIF "last mile"
  mechanic, task #5 the RESCUE_REJECTED_CURL question for dtf modelling, and the
  `build_dtf_delegation.py` opposition count that omits RESCUE_REJECTED_CURL.

## 3.17  MODELLING LESSON — what the stoch, sat and RSI columns actually say

Joe 0824: *"your understanding of the stochrsi calculations will help you understand the r lines,
and to make decisions. this is why you added the stoch, sat, and rsi columns"* and *"does anything
in the stoch/sat/rsi columns confluence your decision?"*

### 3.17.1  the correction that started it

Joe 0824: *"the LTFs (1,2,3) will often tangent away from pxs, when in an ongoing leg - this is why
you are seeing high values for the LTF r lines"*.

My 3.16 reading said ws1, ws2 and ws3 at 77.38 / 73.28 / 47.26 had "no travel behind them" because
their last verdicts were `sideways`, `sideways`, `curl`. **That is wrong and is withdrawn.** A high
LTF r during an ongoing leg is the low timeframe tangenting away from price, not an absence of
travel. The lesson in 3.16 stands on the HTF lines alone; the LTF contrast I drew does not.

### 3.17.2  r is a seven-bar mean, so its next step is already fixed

    r          = the mean of the last SEVEN closed stoch readings
    stoch now  = the DEVELOPING stoch, updated every 5 s
    stoch out  = the OLDEST closed stoch still in the seven, the one that leaves at the next close
    r at next close = r + (stoch now - stoch out) / 7

That last term is banked per line as `wsb_r_move`, in r units per bar of THAT line's timeframe.

Two readings of it are exact, not thresholded, because stoch is
`(RSI - RSI lo) / (RSI hi - RSI lo) x 100`:

- **stoch out = 0** — the reading leaving the window is already at the bottom. Whatever arrives is
  at least as big, so **r cannot fall**. Banked as `wss_only_rise_n`.
- **stoch out = 100** — the reading leaving is at the top. Whatever arrives is no bigger, so **r
  cannot rise**. Banked as `wss_only_fall_n`.

**This is the mechanical form of Joe's 3.16 lesson.** "r has dropped to the ~floor and has nowhere
to go" is `stoch out = 0` — the floor is already inside the window and about to leave.

### 3.17.3  what confluences, across all four labelled setups

| setup | dr | verdict | only rise | only fall | state |
|---|---|---|---|---|---|
| 00:13:00 | +1 | SHORT | 0 | 3 | wsf-exhaust |
| 00:14:50 | +1 | SHORT | 1 | 4 | wsf-momoc |
| 08:02:50 | +1 | SHORT | 2 | 3 | wsf-momo-none |
| 00:52:30 | -1 | hold and walk | **6** | **1** | wsf-exhaust |

**CORRECTED 0824, and the first reading was inverted.** I wrote that the marker separated the trades
from the hold. It does not. It tracks the SIDE of the trade, and it aligns with the trade at every
one of the four setups.

The direction, from Joe 0812 M7: *"its 100% obvious that a LONG trade will launch from a lo oob, and
inverse for SHORT"*. The trade launches FROM the exhaustion and faces the other way, so:

    dr +1 = SHORT, launched from lines high  ->  the trade wants r to FALL  ->  wants `only fall`
    dr -1 = LONG,  launched from lines low   ->  the trade wants r to RISE  ->  wants `only rise`

| setup | dr | side | the trade needs r to | lines that can ONLY go that way |
|---|---|---|---|---|
| 00:13:00 | +1 | SHORT | fall | 3 |
| 00:14:50 | +1 | SHORT | fall | 4 |
| 08:02:50 | +1 | SHORT | fall | 3 |
| 00:52:30 | -1 | LONG | **rise** | **6** |

**00:52:30 carries the strongest support of the four**, not the weakest. The marker never separated
a hold from a trade; it says how much of the board is mechanically committed to the trade's own
direction.

**n = 4.** All on 08-04, three of the four on dr +1. This is a candidate marker, not a rule, and it
will not be reported as a result until 08-05 runs cold.

### 3.17.4  the two SHORT shapes are opposite in the stoch columns

- **08:02:50** — six of eight lines at `sat clock` 0 and `sat left` 7: each just SET a fresh 8-bar
  RSI high on the developing bar. stoch now 100 on those six. r is pinned at the ceiling or still
  climbing. The peak is being made at this bar.
- **00:13:00 and 00:14:50** — `sat clock` 1 to 7, `sat left` 0 to 6: the high was set several bars
  ago and is rolling out. stoch now 0.00 on six of eight lines, so `wsb_r_move` is -12 to -14.3 r
  units per bar on those lines. The peak has passed and r is collapsing.

Both are SHORT. The stoch columns say WHERE IN THE MOVE the bar sits, which the r value alone does
not. Joe rated 08:02:50 **strong**; it is also the board with the highest mean `sat left`, 6.5
against 4.63, 4.38 and 3.63.

### 3.17.5  measured: which of these columns are direction-specific

Checked at 08-04 00:52:30 on both directions of the same bar:

| column | same for dr +1 and dr -1? |
|---|---|
| r | **same** |
| stoch now | **same** |
| stoch out | **same** |
| RSI, RSI lo, RSI hi | **same** |
| sat clock | **NO** - ws1 reads 0 at dr +1 and 7 at dr -1 |
| sat left | **NO** - ws1 reads 7 at dr +1 and 0 at dr -1 |

`sat clock` counts bars since the RSI last set its 8-bar extreme **on the side being read** - the
high at dr +1, the low at dr -1. Everything else on the board is one number read two ways.

### 3.17.6  a float-residue defect found and fixed

`stoch out` is exactly 0 or exactly 100 when the outgoing RSI was the window's low or high, but the
division leaves residue: 00:52:30 ws5 stored `1.4168726029049243e-14` and 08:02:50 ws6 stored
`99.99999999999999`. Raw equality missed both, undercounting `only_rise` by one and `only_fall` by
one. The test now rounds to six places. **That is not a knob** - the nearest genuine readings on the
same boards are 42.41 and 50.00, seven orders away.

## 3.18  UNPACKING 00:52:30 — "hold and walk" does not survive it

Joe 0824: *"I agreed with wsf-exhaust at 0:52 because ws8r exited the fence, but then I saw your
hold and walk verdict ... if you believe it's hold and walk, then lets unpack it"*.

### 3.18.1  Joe's reason for wsf-exhaust is confirmed in the data

ws8r, dr -1. momo-fence-r low = 17. The 85/15 boundary low = 15.

| time | ws8r | past 17 | held 4 bars | run | raw fit | verdict | last-verdict | dwell |
|---|---|---|---|---|---|---|---|---|
| 00:44:00 | 29.20 | no | no | 0 | momo | momo | none | 1105 s |
| 00:48:00 | 14.29 | yes | no | 1 | momo | momo | none | 1345 s |
| 00:48:50 | 15.29 | yes | **yes** | 11 | momo | **none** | momo | 35 s |
| 00:52:30 | 15.82 | yes | yes | 55 | momo | none | momo | 255 s |

- ws8r left momo-fence-r 17 and the exit CONFIRMED at 00:48:35 (four bars held).
- **the raw momentum fit still says `momo` at 00:52:30.** It is Joe's momentum-kill - a
  momentum-true line that leaves momo-fence-r reads none - that turns ws8r off.
- 24 bars in the 00:44-00:53 window sit below the 15 boundary. At 00:52:30 ws8r is 15.82, back
  just inside it.
- ws8r being the last line to turn off is what leaves no line carrying momentum, which is the
  `wsf-exhaust` footer. **Joe's reason holds exactly.**

### 3.18.2  the board is Joe's own template, mirrored to the low side

| marker | 08:02:50, Joe's template, rated **strong** | 00:52:30 |
|---|---|---|
| ws8 heading | away | away |
| ws8 verdict | none | none |
| ws8 last-verdict | momo | momo |
| ws8 dwell | 155 s | 255 s |
| ws8 past its fence by | 1.50 | 1.18 |
| `away` count | 5 | 5 |
| `r IB` count | 5 | 5 |
| weak-mage | ws4 | ws2 |

Joe's words on the template, spec 1.6: *"ws8r reversing, many aways, many ltf `r IB`s"*. **Every
marker matches.** The only difference is the side: 08:02:50 reads dr +1 and 00:52:30 reads dr -1.

### 3.18.3  the stoch columns back the trade, not the hold

Six of eight lines have `stoch out` = 0, so r cannot fall on them. At dr -1 the trade faces UP, so
those six are mechanically committed to the trade's own direction. **That is the strongest support
in the whole labelled set** - see the corrected 3.17.3.

### 3.18.4  so what was `hold and walk` resting on?

One thing only: **the stub.** Joe 0824 set wsf's facing from three lines - *"wsf's dr will be set by
the positioning of gcws30Mage, ws1Mage and ws2Mage - if they are all > {100 - knob:20 fence} then
dr = +1"* - and at 00:52:30 they read 58.95, 36.56 and 30.23, so none of the three answers.

**But that argument fails on its own terms**, because ALL THREE of the delegation setups are stubs:

| setup | gcws30Mage | ws1Mage | ws2Mage | stub | dtf dr | verdict I gave | Joe |
|---|---|---|---|---|---|---|---|
| 00:13:00 | 36.14 | 59.30 | 74.50 | yes | +1 | SHORT | agreed |
| 00:14:50 | 39.84 | 62.38 | 76.00 | yes | +1 | SHORT | agreed |
| 00:52:30 | 58.95 | 36.56 | 30.23 | yes | -1 | hold and walk | questioned |

At 00:13:00 and 00:14:50 I took the direction from dtf's dr and called the trade, and Joe agreed
both. At 00:52:30 I used the same stub to refuse one. **The stub cannot be a blocker on one bar and
not on the other two.**

08:02:50 is not a delegation moment at all - it is Joe's template bar, and it has no stub to consider.

### 3.18.5  the corrected verdict

**LONG, dr -1.** The board is the template mirrored, the state is wsf-exhaust which is the state
that lets a trade fire, and six of eight lines cannot travel against it.

**NOT CHANGED IN THE TABLE.** `wss_verdict` is Joe's label column and the row still reads
`hold and walk`. Joe's word changes it, not mine.

**WITHDRAWN 0824 - see 3.20.** The argument above rests on my claim that the three delegation
setups are the same case and that I answered the same blank two different ways. They are NOT the
same case. The 3-minute Mage lookback answers dr +1 at both 00:13:00 and 00:14:50 and answers
NOTHING at 00:52:30. `hold and walk` is right and the LONG verdict is withdrawn.

## 3.19  Joe's TF1:10 test — the 00:52:30 exhaust does not survive it

Joe 0824: *"I'm diving into your decision becuse I can see that if we extended wsf from TF1:8 to
TF1:10, then your hold and walk verdict would be correct -- you can see this for yourself: ws10r
creates an ib X oob at ~01:00"*.

### 3.19.1  Joe's read, measured

| line | drops to/below momo-fence-r 17 | value before | value after | crosses the 15 boundary |
|---|---|---|---|---|
| ws9r | 00:54:00 | 29.09 | 14.81 | 00:54:00 |
| ws10r | **01:00:00** | 29.55 | 15.27 | 01:10:00 |

**Joe said ~01:00 and it is 01:00:00 exactly.**

### 3.19.2  what the two extra lines do to the board at 00:52:30

| line | r at 00:52:30 | raw momentum fit | past momo-fence-r 17 | verdict |
|---|---|---|---|---|
| ws9r | 29.77 | **momo** | no | **momo** |
| ws10r | 30.80 | **momo** | no | **momo** |

**Both carry momentum.** With TF1:10 the footer at 00:52:30 is `wsf-momoc`, not `wsf-exhaust`, and
no trade can fire. **Joe's `hold and walk` is correct under TF1:10.**

Walking the momentum-kill forward - momo-fence-r 17, four bars held:

| time | ws9r | ws9 verdict | ws10r | ws10 verdict |
|---|---|---|---|---|
| 00:52:00 | 29.44 | momo | 30.50 | momo |
| 00:54:15 | 14.81 | **none** | 29.55 | momo |
| 01:00:00 | 14.81 | none | 15.27 | momo |
| 01:00:15 | 14.81 | none | 15.27 | **none** |

**First bar where neither ws9r nor ws10r carries momentum: 01:00:15.** Under TF1:10 the wsf-exhaust
lands there, not at 00:52:30.

### 3.19.3  Joe's flipside question - the ensuing x-cross

The x-cross method watches `ws{weak-mage-tf}x`. At 00:52:30 the weak-mage line is **ws2**.

| | time | target won |
|---|---|---|
| raw first touch | 00:53:55 | Mage |
| **confirmed, XCROSS_XWOB 5 held** | **01:00:15** | b |

The 00:53:55 touch lasted ONE bar - ws2x fell from 25.54 to -21.80 at the next bar and the race
went back to no winner. The cross that held is 01:00:15.

### 3.19.4  the convergence

    ws10r's momentum turns off      01:00:15
    the ensuing x-cross confirms    01:00:15

**Two independent mechanics land on the same bar.** ws10r is not in wsf today and played no part in
the x-cross calculation.

### 3.19.5  where this leaves the verdict

- **under wsf as it is built today, TF1 to TF8**: the board at 00:52:30 is `wsf-exhaust`, matches
  Joe's 08:02:50 template on every marker, and six of eight lines cannot travel against a LONG. The
  LONG verdict in 3.18.5 is WITHDRAWN on separate grounds - see 3.20 - but this board reading stands.
- **under TF1:10**: two more lines carry momentum at 00:52:30, the state is `wsf-momoc`, and
  `hold and walk` is right - with the trade arriving at 01:00:15.

**Whether wsf extends to TF10 is Joe's call and has not been made.** Nothing in the code changed.

## 3.20  the Mage lookback — built, banked, and consumed by nothing

Joe 0824: *"the stub should have been replaced with a mech that allows for those Mages to lookback
and discover the direction -- ie, every timestamp I'm passing to you now was orginally validated by
the now-missing mech"*.

### 3.20.1  it is not missing from the table. It is missing from the decision.

`build_dtf_delegation.py` line 68 carries the knob and Joe's own words:

    DDS_LOOKBACK_S = 180   # KNOB, Joe 0823: "restrict the lookback to 3 minutes"

and `dtf_delegation` holds three populated columns for it:

    dds_last_out_utc   the most recent bar where all three Mages were on ONE side of the 80/20 fence
    dds_last_out_dr    +1 if all three were above 80 at that bar, -1 if all three were below 20
    dds_lag_s          how long ago, in seconds

**What is missing is that nothing reads them.** `dds_wsf_dr` is still computed from the delegation
bar alone, so it is 0 on 84 of the 85 moments and `dds_stub` is still 1 on the same 84.

### 3.20.2  what the lookback would answer, across all 85 delegation moments

| | moments |
|---|---|
| all three Mages outside the fence AT the delegation bar | 1 |
| an all-three-out bar within the 180 s lookback | **22** |
| — of those, dr +1 (all three above 80) | 16, lags 0 s to 180 s |
| — of those, dr -1 (all three below 20) | 6, lags 50 s to 165 s |
| nothing within 180 s | 63 |

**23 of 85 get a facing once the lookback is consumed, against 1 today.**

### 3.20.3  the three modelling timestamps, checked against it

| setup | gcws30Mage | ws1Mage | ws2Mage | last all-3-out | its dr | lag | facing |
|---|---|---|---|---|---|---|---|
| 00:13:00 | 36.14 | 59.30 | 74.50 | 00:12:10 | **+1** | 0m50s | **SHORT** |
| 00:14:50 | 39.84 | 62.38 | 76.00 | 00:12:10 | **+1** | 2m40s | **SHORT** |
| 00:52:30 | 58.95 | 36.56 | 30.23 | **none** | — | — | **no facing** |

**Joe's read is confirmed.** Both SHORT calls he agreed are exactly what the lookback gives, and it
gives nothing at 00:52:30.

### 3.20.4  what this does to my 00:52:30 argument

My case for LONG in 3.18.4 was that the three setups are the same case and I answered the same
blank two different ways. **That claim is wrong and is withdrawn.** They are not the same case:

- at 00:13:00 and 00:14:50 the direction does not come from dtf's dr. It comes from the Mage
  lookback, which answers +1 at both.
- at 00:52:30 the lookback answers nothing. There is no facing to take.

**`hold and walk` at 00:52:30 is correct**, and for the reason Joe gave rather than the reason I
gave. It is now confirmed twice over - once by the TF1:10 test in 3.19, once by the lookback here.

### 3.20.5  what has NOT been built

Nothing changed in the code this turn. The concretions, for Joe:

1. does `dds_wsf_dr` take `dds_last_out_dr` when the lookback finds a bar?
2. does `dds_stub` go to 0 when the lookback answers, or stay 1 with the lookback recorded
   alongside? Joe 0823: *"the stub will capture only the dtf-free delegation moments"*.
3. does the 180 s knob stay at 180 s?
4. do the 63 moments with no answer stay stubs, or become something else?

### 3.20.6  what 03:53 and 03:54 show — the lookback hands over a dead condition

Joe 0824: *"what do you find at 03:53 and 03:54?"*

**The all-three-out run ENDS at 03:53:00.** gcws30Mage falls through the 80 fence:

| bar | gcws30Mage | ws1Mage | ws2Mage | all three above 80 |
|---|---|---|---|---|
| 03:52:50 | 90.29 | 93.93 | 92.32 | yes |
| **03:52:55** | **81.03** | **88.28** | **85.81** | **yes - the LAST bar of the run** |
| 03:53:00 | 79.35 | 85.22 | 85.23 | **no** |
| 03:53:05 | 71.35 | 80.74 | 79.90 | no |
| 03:53:30 | 60.86 | 75.36 | 73.48 | no |

03:52:55 is the bar the 3-minute lookback hands to the 03:55:20 delegation, 2m25s later. **By the
time that delegation fires, the condition has been dead for 2m20s and gcws30Mage has fallen from
81.03 to below 60.** This is the risk already flagged in 3.20.5 question 3, now with a number on it.

**Across the two minutes, 24 bars, dr +1:**

- **the state never changes.** wsf-momoc on every bar, ws5r ws6r and ws7r carrying throughout.
  ws7r joined since 03:50:20.
- **no verdict changes on any line.** Two heading changes only, both on ws3r: away to toward at
  03:54:40, back to away at 03:54:45.
- **the facing reads `none` on all 24 bars.**
- **the board drifts against a dr +1 trade.** Lines that can only RISE go from 3 to 4; lines that
  can only FALL stay at 2. A dr +1 trade needs r to fall.
- **the low timeframes are falling**: ws1r 40.52 to 28.68, ws3r 100.00 to 83.12, ws4r 95.25 to 90.70.
- **every Mage line is still out of bounds and weak-mage is NONE** on all 24 bars, so Joe's superior
  marker holds the whole way through while everything else deteriorates.

**No wsf-exhaust in the window, so no trade at either minute.**

## 3.21  MODELLING LESSON — depth, blast radius, and mid-board

Joe 0825, verbatim, both lessons:

> "you're right about depth, but the more we search for depth the less profit we claim. the
> wsf-model-report data is designed to predict depth, as best as it can. we can call our depth
> predictions with confidence because we are following the ebb and flow of predicatble human
> emotions - it's what drives the momentum calcs (stochrsi and BB%B). when the humans have given as
> much as they feel comfortable with, they start to back off; this is what we are reflecting in the
> report"

> "each r line has a small 'blast radius'. this is why ws3 reacted to ws2, and it's also why ws5
> will react to ws4: ws4 needs to release the momentum pressure it's holding on to (r=95), so it
> will fall (taking ws3 with it). ws4 will easily impact ws5, because ws5r is near-mid-board AND
> because ws7/8 are firmly in mid-board - mid-board is the space where momentum is the lowest, so
> while the LTFS are building up and releasing pressure, ws7/8 are treading water and waiting for
> something bigger to come along"

### 3.21.1  depth is IN the report, and waiting for more of it costs money

- **the report already predicts depth.** `stoch now`, `stoch out`, `sat clock` and `sat left` say
  how far r can travel and how long before it must - see 3.17.
- **so "I would not claim how far it falls" was the wrong answer.** The board carries a depth call
  and refusing to make it is a cost, not caution. Joe: *"the more we search for depth the less
  profit we claim"*.
- **why the call can be made with confidence, in Joe's terms**: the momentum calculations - stochrsi
  and BB%B - track how much people are willing to give before they back off. The report is a
  reading of that ebb and flow, not a statistical guess.

### 3.21.2  BLAST RADIUS - Joe's word, and it is SMALL

- **each r line affects its immediate neighbours on the ladder, not the whole board.** ws2 reaches
  ws3. ws4 reaches ws5. A line does not reach across the ladder.
- **this is the mechanism under the matryoshka order in 3.12.** The low timeframes lead, and they
  lead by passing the move along one step at a time.
- **a line at an extreme is HOLDING PRESSURE and must release it.** Joe on ws4 at 03:53:00: *"ws4
  needs to release the momentum pressure it's holding on to (r=95), so it will fall"*.
- **the release travels in both directions.** ws4 falling takes ws3 with it AND impacts ws5.

### 3.21.3  MID-BOARD - Joe's word for the space where momentum is lowest

- **mid-board is where a line has the least momentum.** A line sitting there is, in Joe's words,
  *"treading water and waiting for something bigger to come along"*.
- **it makes a line easy to move.** ws5r near-mid-board is why ws4's release reaches it easily.
- **a `momo` verdict on a mid-board line is the weakest kind of carry.** The line is in the
  lowest-momentum space on the board; it is holding the state up on nothing.
- **the practical read**: count where the carrying lines SIT, not just that they carry. Carriers at
  an extreme are holding real pressure. Carriers mid-board are not.

### 3.21.4  what this rewrites in the earlier notes

- **3.16 said a high-timeframe r at the floor with momo behind it has already made the move.** That
  stands, and mid-board now explains the middle case: a line neither at the floor nor at the
  ceiling has nothing stored either way.
- **3.20.6 recorded my read of 03:53 as "the facing dies".** Wrong twice over - the dr was there
  through the lookback, and the board was in a pressure release, not a stand-off.
- **a reading of 100.00 or 0.00 is a limit, and a limit is a turning point.** It is the maximum
  pressure a line can hold, not a strength reading.

### 3.21.5  the 03:53:00 verdict, rebuilt on 3.21 — and one caveat on the depth columns

**THE CAVEAT, measured.** `r move/bar` = (stoch now - stoch out) / 7 says what r does IF THE BAR
CLOSED NOW. It is exact for that instant and it does NOT survive a developing bar that keeps
moving. At 03:53:00 it read positive on six of eight lines; between 03:53:00 and 03:54:00 seven of
eight r values FELL, because the developing stoch collapsed inside the minute - ws1 82.89 to 12.00,
ws2 76.32 to 13.15, ws3 100.00 to 54.35, ws4 100.00 to 84.11.

**What IS robust is `stoch out`**, because it is a CLOSED reading and cannot change. At 03:53:00:

    cannot rise (stoch out = 100)   ws2r, ws3r
    cannot fall (stoch out = 0)     ws1r, ws6r, ws8r
    free either way                 ws4r, ws5r, ws7r

**The release chain at 03:53:00, read with blast radius and mid-board:**

| line | r | where it sits | what it is doing | its 8-bar extreme is protected for |
|---|---|---|---|---|
| ws2r | 81.60 | near its fence | turned 5 s ago, cannot rise, falling 3.38 per bar | 3 bars x 2 min = **6 min** |
| ws3r | 100.00 | AT the ceiling | cannot rise, no momentum for 645 s, inside ws2's radius | 7 bars x 3 min = 21 min |
| ws4r | 95.25 | near the ceiling | holding pressure, no momentum for 235 s, heading away | 7 bars x 4 min = 28 min |
| ws5r | 69.64 | near-mid-board | carrying, 720 s - the longest carry - inside ws4's radius | 7 bars x 5 min = 35 min |
| ws6r | 51.73 | mid-board | carrying, 300 s | 7 bars x 6 min = 42 min |
| ws7r | 49.04 | mid-board | carrying, **20 s** | 7 bars x 7 min = 49 min |
| ws8r | 44.18 | mid-board | sideways for **2180 s = 36 min** - treading water | 7 bars x 8 min = 56 min |

**THE VERDICT: SHORT, dr +1.**

- **the release has already started.** ws2r turned 5 seconds before the bar and cannot rise.
- **the two lines above it cannot hold.** ws3r is at the ceiling with no momentum for 645 s; ws4r
  holds 95.25 of pressure with no momentum for 235 s and is heading away.
- **all three lines carrying the state sit in or beside the lowest-momentum space on the board.**
  ws5r near-mid-board, ws6r and ws7r firmly mid-board, and ws7r acquired its carry 20 s ago.
- **ws8r has been sideways for 36 minutes.** It is not holding the move up; it is waiting.
- **the state reads wsf-momoc and the mechanic as built would hold.** This verdict overrides it, the
  same shape as Joe's 08:02:50 template being *"a candidate for overriding domTF BLOCK"*.

**DEPTH.** ws3r and ws4r each have the whole board beneath them and nothing stored to resist with.
ws2r's ceiling protection expires first, in 6 minutes, and it is the line that starts the chain.

## 3.22  THE MODEL AS IT STANDS, 0825 — and Joe's two new rules

### 3.22.1  the model, banked

**Question 2, which way am I facing.** `jig.wsf_facing_dr` on gcws30Mage, ws1Mage and ws2Mage
against the 80/20 fence, then `jig.wsf_dr_lookback` over 180 s. If there is no dr there is no
verdict - the board cannot be read at a direction. 00:52:30 and 04:45 are both refused on this
alone.

**Question 3, what state am I in.** The report footer. `wsf-exhaust` is the state that lets a trade
fire; `wsf-momoc` and `wsf-momo-none` do not.

**Then the board, in the order it actually decides things:**

1. **where the pressure sits.** A line at 100.00 or 0.00 is at a limit, and a limit is a turning
   point. A line near its fence with momentum that ended recently is holding pressure it must
   release - Joe 0825 on ws4 at 95.
2. **whether the pressure has anywhere to go.** 03:43:30 is a hold because the high timeframes had
   already spent themselves; 04:49:00 is a trade because they had not.
3. **where the carriers sit.** Mid-board is the lowest-momentum space, so a `momo` verdict there is
   the weakest kind of carry. Carriers mid-board do not defend the state.
4. **blast radius.** A line reaches its neighbours, not across the ladder. The trigger is a
   neighbour turning - ws2r turning 5 s before 03:53:00.
5. **what the board cannot do.** `stoch out` at 0 or 100 is a closed reading and cannot change.
   Count the lines mechanically committed to the trade's own direction. Six of eight at 00:53:15
   and 01:03:40 is the strongest seen; two of eight is the weakest.
6. **Joe's template markers** - ws8r reversing at its fence, the away count, the low-timeframe
   `r IB` count, weak-mage NONE with every Mage line out.
7. **the entry** is not the setup bar. It is the ws{weak-mage-tf}x cross that follows, and the
   weak-mage timeframe is re-read at each bar of the walk.

**What the model does NOT have**: an answer to question 1, am I in trade. Every verdict so far has
assumed flat. Joe's two rules below are the first part of that answer.

### 3.22.2  RULE 1 - pyramiding, maximum two trades

Joe 0825, verbatim: *"allows pyramiding, max 2 trades"*.

- **two slots.** A second entry is allowed while the first is open.
- **pyramiding means the same side**, so slot 2 only opens on the same dr as slot 1. That is the
  word's meaning and it is also what Rule 2 assumes - an OPPOSING dr is the thing that ends
  dormancy, which only makes sense if both open trades face the same way. STATED, not asked.

### 3.22.3  RULE 2 - both slots occupied, the walk goes dormant

Joe 0825, verbatim: *"if both trade slots are occupied, the walk will take no action/stay dormant
until an opposing (three-mage or wsf9of12) dr prints. keep it causal"*.

- **two sources wake it**, either one: the three-Mage dr (`jig.wsf_facing_dr` with the 180 s
  lookback) or the wsf9of12 signal's own side (`ws_fin_9of12.wsf_side`).
- **opposing** means the sign is the reverse of the open trades' dr.
- **causal**: both are read at their own bar. The three-Mage lookback only looks backward, and a
  wsf9of12 side exists at the bar it prints.

### 3.22.4  THREE THINGS JOE HAS NOT SAID, and one of them is implemented

1. **what CLOSES a slot.** Nothing in the model closes a position. **IMPLEMENTED AS: the opposing
   dr that ends dormancy also frees both slots** - because otherwise "dormant until an opposing dr
   prints" has no meaning, the walk would be dormant forever after the second trade. This is my
   reading of Joe's sentence, not his instruction, and it is the exit rule by default.
2. **what DISARMS a pending setup.** Joe's 1.6 says "walk forward" until the cross prints. As built
   the walk stays armed until it does, even if the state leaves wsf-exhaust in between. NOT ASKED.
3. **whether an opposing dr while only ONE slot is filled does anything.** Rule 2 names both slots
   occupied only. As built, one open trade plus an opposing dr does nothing. NOT ASKED.

### 3.22.5  the walk is BUILT, and Rule 1 as written costs the two trades Joe just confirmed

`build_wsf_walk.py` runs the causal forward walk over 08-04 and banks every event to `wsf_walk`.
Over 17,280 bars: **9 armed, 9 signals, 4 dormant stretches, 4 wakes.**

**THE PROBLEM, measured.** Slot 1 is taken at 00:25:15 at dr +1. Pyramiding is same-side, so every
dr -1 setup after it is blocked while that slot stays open - and Rule 2 only frees slots when BOTH
are occupied. The walk therefore arms nothing between **00:25:15 and 08:03:15, a stretch of 7h38m**.

Inside that stretch there are **39 separate trade-ready periods, all of them dr -1**, including:

| first bar | dr | ends |
|---|---|---|
| 00:53:15 | -1 | 00:54:15 |
| 00:58:15 | -1 | 00:58:25 |
| 00:59:20 | -1 | 00:59:25 |
| **01:03:40** | **-1** | 01:04:10 |
| 01:06:30 | -1 | 01:06:35 |

**00:53:15 and 01:03:40 are the two Joe just confirmed** - *"that's a well placed trade"* and
*"good"*. As the rules are written they never happen.

**This is concretion 3 in 3.22.4, and it is load-bearing.** Joe's Rule 2 names both slots occupied.
It says nothing about ONE slot occupied and an opposing dr arriving. Three readings, all Joe's to
pick, none of them built:

1. **as written** - same-side only, one slot filled, opposing setups blocked. Costs 39 periods.
2. **an opposing dr frees a single open slot too**, then the walk re-arms on the new side.
3. **slot 2 may be opposite** - but then it is not pyramiding and Rule 2's wake test has two
   directions to compare against.

### 3.22.6  the slot accounting, settled 0825

Joe 0825, verbatim, the two calls:

> "1:06:30 shouldn't print, because the 2nd wsf-exhaust event is already locked in and waiting for
> its x-cross trade signal --this means the pyramid mech needs to hold 2 slots for wsf-exhaust, as
> well as 2 slots for open positions <- this is only my guess at the logic - the build logic is
> your call"

> "all open trades (1 or 2) are closed by the next opposing dr trade"

**ONE POOL OF TWO SLOTS. My call, and the reason.** Each slot is either ARMED - a wsf-exhaust locked
in and walking forward for its cross - or OPEN, once that cross has printed. A slot moves armed to
open and is never both.

- **not 2 armed plus 2 open**, which is Joe's guess: with one open trade and two armed setups, both
  armed can convert, and that is three open against *"max 2 trades"*. The second conversion would
  have to be blocked and discarded, which is worse than never arming it. One pool cannot overfill.
- **it gives Joe the behaviour he asked for.** At 01:06:30 the pool holds one open trade from
  01:02:35 and one armed setup from 00:58:15, so nothing new arms.

**CLOSING.** An opposing dr closes ALL open trades, one or two - Joe's words. **MY ADDITION, STATED:
it also CLEARS ARMED SLOTS.** An armed setup faces the direction that has just been contradicted, so
walking it forward would enter against the new dr. Not Joe's instruction.

**A DEFECT THE FIRST RUN EXPOSED, and the fix.** Arming ran on every bar of a wsf-exhaust, and a
wsf-exhaust runs for many consecutive bars - so BOTH slots filled from ONE event, five seconds
apart: 00:53:15 and 00:53:20. Two setups five seconds apart is one event, not a pyramid. **Arming is
now the RISING EDGE** of "a dr is present and the state is wsf-exhaust". The pair becomes 00:53:15
and 00:58:15 - two separate events.

**THE RESULT over 17,280 bars: 19 armed, 14 signals, 7 dormant stretches, 7 closes.** The 7h38m dead
stretch is gone - the close rule frees the pool at 00:18:35 and the walk arms at 00:53:15, which is
the trade Joe confirmed.

    00:53:15  armed   dr -1                     0 open, 1 armed
    00:58:15  armed   dr -1                     0 open, 2 armed
    01:02:35  signal  ws3x crossed boundary     1 open, 1 armed
    01:15:25  signal  ws4x crossed Mage         2 open, 0 armed  -> dormant
    01:34:05  close   opposing dr +1 from wsf9of12, after 1120 s dormant

**Both trades Joe confirmed now appear**: 00:53:15 arms and fires at 01:02:35, and 01:03:40 is
correctly silent because the 00:58:15 setup already holds the second slot.

**Nine of the fourteen signals are pyramids** - a same-side second entry while the first is open.
