# `g5extrema_lookback` — the sweep, and why it cannot answer the question. 1006

Joe asked for the sweep, then asked the question that invalidated the way I built it:
*"are sweeps inherently flawed? how do they handle early reversals on a large leg? that's our
typical MAE killer"*. Banked at his word: *"bank what we have"*.

## THE KNOB

| | |
|---|---|
| name | **`g5extrema_lookback`** — renamed 1006, Joe: *"mod the knob label - add `g5extrema`"* |
| was | `LOOKBACK_BARS`, one word from `rev_lookback` at the same 48 bars / 240 s, unrelated job |
| defined | `score39.py:43` |
| used | `score39.py:76` — **once** |
| its one job | how far back mtd step 1 searches for the **g5Mage oob extrema** |
| touches | the extrema bar -> the four Mage reads at TOL -> the route -> branch D |
| does NOT touch | the arm, the coil, the qualify, the race, the ws1mage-rev window |
| live value | **48 bars = 240 s** |

## THE END RESULT — three findings, in order of how much they matter

### 1. The knob cannot reach the early reversals. This survives every ruling.

| g5extrema | killers (MAE >= 1.8) | **arms behind them** | their mean adverse turns at 0.20 % |
|---|---|---|---|
| 6 | 35 | 13 | 8.37 |
| 24 | 31 | 15 | 8.58 |
| 36 | 33 | 15 | 8.52 |
| **48 live** | 34 | 15 | **8.00** |
| 60 | 35 | 15 | 7.97 |
| 96 | 36 | 15 | 8.28 |
| 168 | 39 | 15 | 8.18 |
| 240 | 39 | 15 | 8.18 |

- across a **40x** knob range the killers' mean adverse-turn count sits at **7.97 .. 8.58**.
- `arms_18` is **15 in 39 of 40 cells**, and **09-25 18:01:25 owns 6 or 7 of them in every cell**.
- WHY, measured: a row only moves if its SIDE flips, and the knob flips at most **46 of 394** sides.
  A row whose side is unchanged keeps the same entry bar, same exit and same turn count, so its MAE
  is byte-identical in every cell. The staircase belongs to the price path from a FIXED entry bar,
  and no value of this knob can move the entry bar.

### 2. The sweep's "best cell" was an artefact of which rows I counted.

| population ruling | best cell | mean MAE | traded rows there |
|---|---|---|---|
| A everything — my first pass | **24 bars** | 0.6076 | 394 |
| B CONFLUENCE only, all OPEN blocked | **6 bars** | 0.4907 | **114** |
| C CONFLUENCE + all OPEN fires | **6 bars** | 0.5752 | 235 |
| D CONFLUENCE + band claimed only | **6 bars** | 0.5014 | 137 |

- A disagrees with B, C and D. My first pass scored **all 394 rows in every cell**, including
  **159 BLOCKED rows at 6 bars**, so route changes - the knob's main effect - never left the
  population and were invisible to the mean.
- **120 of 397 rows (30 %) have no ruling**: OPEN neither 42, no r block 46, band claimed 32. Any
  aggregate over "traded rows" is one of four numbers until Joe rules them.
- NOT CIRCULAR, and this was Joe's own question: the knob is causal (`mtd(k)` reads only bars <= k),
  so a row it excludes is excluded by a rule that runs live, and judging a gate by what it keeps is
  what a gate is for. It is UNFALSIFIABLE, not circular. The fix is to report it PER RULING - the
  table above - never as a single best cell.
- and 6 bars only "wins" by trading **114 rows instead of 228**: 4 killer-arms instead of 13. That
  is volume for quality, the same shape the 1005 net-based sweep showed. It is not a gain.

### 3. What the knob DOES do, cleanly: it buys causality.

| g5extrema | src=fwd | r1 | r2 | neither | CONFLUENCE |
|---|---|---|---|---|---|
| 6 | **270** | 159 | 159 | 79 | 116 |
| 24 | 129 | 236 | 101 | 60 | 184 |
| **48 live** | **24** | 308 | 47 | 42 | 230 |
| 90 | 1 | 304 | 26 | 67 | 211 |
| 138+ | **0** | 273 | 20 | 104 | 180 |

- `src=fwd` is the branch whose verdict lands AFTER the signal. It falls **270 -> 24 -> 0**.
- r2 collapses **159 -> 47 -> 20** as r1 absorbs it: widening finds the oob extrema, so all four
  Mages read oob, so the row routes r1.
- `neither` has a floor of **40..46 bars between 30 and 72**, then climbs to 138 at 240.

## THE INSTRUMENT JOE SUPPLIED, AND A CORRECTION

Joe 1006: *"you could use swing_detect in a way that shows if there are multiple reversals on the
MAE side"*. Built as: adverse-side pivots between entry and the MAE extreme — H pivots for a SHORT,
L pivots for a LONG.

**MY FIRST BUILD OF IT WAS WRONG.** Counted at the 0.70 % scoring swing it can never exceed 1,
because `score` exits at the first favourable pivot and pivots alternate. I reported "the killers are
single sustained pushes, not staircases". **That was an artefact of the granularity.** At a finer
counting swing they are staircases:

| counting swing | killers mean turns to the MAE extreme | 0.70-1.8 | < 0.70 | separation |
|---|---|---|---|---|
| 0.10 % | 18.65 | 11.13 | 2.57 | 7.3x |
| **0.20 %** | **8.00** | 4.97 | **1.25** | **6.4x** |
| 0.30 % | 5.15 | 3.10 | 0.88 | 5.9x |
| 0.50 % | 2.26 | 1.45 | 0.51 | 4.4x |

The bucket table at 0.20 % is monotonic: **180 rows at 0..4 turns contain ZERO killers** (mean MAE
0.033 at 0 turns), and **every row at 23+ turns is a killer** (mean MAE 2.908 .. 4.387).
09-25 18:58:00 made **19 adverse reversals** before peaking at 20:34:30, MAE 4.445 over 106.3 min.

One counter-case, so the shape is not assumed: 10-02 **04:42:00** took MAE 3.780 in **3 turns over
9 minutes** — a genuine single push. There are two failure shapes, not one.

**THE CAUSAL FORM** is turns-SO-FAR from entry to the current bar, which is readable live and rises
as the staircase builds. Turns-to-the-MAE-extreme is a diagnostic only: the extreme is in the future
at the signal bar. The 0.10/0.20/0.30/0.50 ladder is MINE, not a measured knee.

## RULING FOR JOE

No value of `g5extrema_lookback` is recommended. The live **48** is not beaten by anything that is
not simply trading less, and the knob provably cannot touch the mechanism that produces the MAE.
The only clean reason to move it is CAUSALITY: `src=fwd` is 24 of 394 at 48 and 0 past 138 bars.
Whether that is worth the `neither` count rising 42 -> 104 is his call, not a sweep's.

## FILES
`1005_scoring/g5extrema_sweep.py` -> `g5sweep.out` (40 cells, route + status + mean/median MAE)
`1005_scoring/g5extrema_tail.py` -> `g5tail.out` (40 cells, rows_18 / arms_18 / mae_18 / worst / top arm)
the adverse-turn ladder -> `adverse_turns.out`

---

# THE MATRYOSHKA READ OF THE MAGE CASCADE — Joe 1006, PARKED

Joe asked whether I could see what the `os_mage_net` grade misses: *"if you consider the
matryoshkaic nature of faster lines, what do you see now in the mage cascade?"*

## 09-25 09:32:00, the anchor at 09:28:05

| ws | Mage |
|---|---|
| **ws1** | **106.8975** |
| ws2 | 94.8561 |
| **ws3** | **87.8215** |
| ws4 | 89.9240 |
| ws5 | 95.9524 |
| ws6 | 101.0092 |
| ws7 | 101.3329 |
| ws8 | 102.2915 |
| ws9 | 108.0409 |
| ws10 | 113.9913 |
| **ws11** | **115.6010** |
| ws12 | 110.5082 |

| the shape | value |
|---|---|
| `os_mage_net` = ws12 - ws1 | **+3.6107** -> read as "lifting" -> grade `with-trend` -> flip to LONG |
| the ladder's own spread | **27.7795** |
| monotone up the ladder | **NO** |
| ends (ws1, ws12) mean | **108.70** |
| middle (ws3, ws4) mean | **88.87** |
| the middle sits BELOW the ends by | **19.83** |
| fast half, ws1 -> ws3 | **-19.08** |
| slow half, ws6 -> ws11 | **+14.59**, monotone over six lines |

## WHAT THE NET CANNOT SEE

Joe's own words from 09-25 name the shape: **"Matryoshka — supported at the ends, absent in the
middle."** `os_mage_net` takes ws12 minus ws1 - **the two points a matryoshka holds UP** - gets
+3.61 out of a 27.78 spread, and calls it a lift. It is structurally blind to the only thing that
moved: the fast middle dropping out.

And the matryoshka says which way. **ws2/ws3/ws4 are the faster lines and have already rolled over
while ws9..ws12 are slower and still elevated because they lag.** Fast turning first with slow not
yet caught up is a down move in progress -> SHORT.

The outcome agrees, measured at swing 0.70:

| side | MAE | MFE | stretch |
|---|---|---|---|
| LONG, what the flip traded | **1.571** | 1.870 | 09:32 -> 11:12:40, 100 min |
| **SHORT, the dr-bias side** | **0.008** | **1.571** | 09:32 -> 10:04:05, 32 min |

## JOE'S SIZING READ — PARKED TO MVP3, HIS WORD

Joe 1006: *"the mage cascade from ws6 to ws12 is going upwards, while the fast lines are pressing
down. this split tells us that there is strong upward pressure, so the short position at 09:32 will
likely be a small trade"*, and the denominator: *"small relative to the bullish leg that it was on.
the whole leg was ~9%"*.

| | value |
|---|---|
| the SHORT's MFE | **1.571** |
| the bullish leg it fought, Joe's read | **~9 %** |
| the SHORT captured | **~17 % of the leg** |

NOT a claim about the mech. Joe 1006: *"for the updated mech, the size claim is less important at
the moment. it'll come in to play when we're sizing lots - MVP3 maybe"*. Banked here so MVP3 has the
number rather than a recollection. The ~9 % is Joe's read of the leg and has not been re-measured.

## HELD, AT JOE'S WORD

**mage-cascade as a text string in the table.** Joe 1006: *"this also shows that we need
mage-cascade as a text string in the table, but hold on that work for now - I might have more
adjustments coming"*. Not started.

## STILL JOE'S TO RULE, both surfaced by this row

| # | the question |
|---|---|
| 1 | a MINIMUM net before the grade may flip a side. 09:32 flipped on +3.61 inside a 27.78 spread |
| 2 | may a ONE-MEMBER D block fire at all. 09:32's block is ws1 alone, band [93.7208, 100.0000] |
