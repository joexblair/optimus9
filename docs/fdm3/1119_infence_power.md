# fdm3-infence-power

**GOAL: an in-fence cell should say HOW FAR from the fence the line sits, not only that it is inside
it.** The tag was binary — in-fence or ex-fence — so a line at 50 and a line at 76 printed the same
thing. The suffix makes the distance readable at a glance.

**IT COVERS BOTH IN-FENCE CODES: `TO(inf)` and `AW(inf)`.** He asked for TO(inf) first and added
AW(inf) the same day.

HIS NAME for this mech, 2026-11-19: `fdm3-infence-power`.

## 1. HIS WORDS, verbatim

> "new mech: fdm3-infence-power
> for every TO(inf) line, add a suffix based on these critreria
> if the line's value is between 38 and 62, print TO(inf)0
> if between 28 and 38, print TO(inf)-1
> 23 to 28, TO(inf)-2
> 62 to 73, TO(inf)+1
> 73 to 77, TO(inf)+2
>
> all values are 2dp: eg 62 to 73 is actually 62.00 to 72.99"

Then, the same day, widening it:

> "I have a small job for you: in the same manner as TO(inf), add the (+2,+1,0,-1,-2) suffixs to
> AW(inf). same ranges"

## 2. THE BANDS

Every edge is LOW-INCLUSIVE and read at 2dp, which is his own worked example: 62 to 73 means 62.00
to 72.99, so 62.00 opens the +1 band and 73.00 opens the next one.

| the value, 2dp | the suffix | the TO(inf) cell prints | the AW(inf) cell prints |
|---|---|---|---|
| under 23.00 | -3 | `TO(inf)-3` | `AW(inf)-3` |
| 23.00 to 27.99 | -2 | `TO(inf)-2` | `AW(inf)-2` |
| 28.00 to 37.99 | -1 | `TO(inf)-1` | `AW(inf)-1` |
| 38.00 to 61.99 | 0 | `TO(inf)0` | `AW(inf)0` |
| 62.00 to 72.99 | +1 | `TO(inf)+1` | `AW(inf)+1` |
| 73.00 to 76.99 | +2 | `TO(inf)+2` | `AW(inf)+2` |
| 77.00 and over | +3 | `TO(inf)+3` | `AW(inf)+3` |

**THE -3 AND +3 ARE HIS RULING, NOT HIS FIVE BANDS.** His five cover 23.00 to 76.99. He ruled the
extra two for TO(inf), and then again for AW(inf) when the same gap was measured there.

**WHY A GAP EXISTS AT ALL: the ex-fence test reads the TARGET SIDE ONLY.** A HIGH target-side line
is ex-fence only at 77.00 and over, so a value of 0.05 is still in-fence and still prints an
in-fence tag. That is the whole cause, and it affects both tags identically.

| the measurement that produced his ruling | TO(inf) | AW(inf) |
|---|---|---|
| cells on 09-24, measured before the build | 23174 | 3321 |
| inside his five bands | 21332, 92.1% | 3120, 93.9% |
| outside them, so bare without his extra two | **1842, 7.9%** | **201, 6.1%** |
| the lowest value on such a cell | 0.05 | 1.14 |
| the highest | 98.33 | 98.54 |

**AS BUILT AND VERIFIED on 09-24, reading 8792** — each range checked against the line's own value
read off the tape, so a band that crossed an edge would show here:

| the cell prints | cells | the value range it holds |
|---|---|---|
| `TO(inf)-3` | 1932 | 0.00 .. 22.93 |
| `TO(inf)-2` | 1268 | 23.06 .. 27.98 |
| `TO(inf)-1` | 4452 | 28.07 .. 37.96 |
| `TO(inf)0` | 13498 | 38.01 .. 61.98 |
| `TO(inf)+1` | 4553 | 62.00 .. 72.97 |
| `TO(inf)+2` | 1280 | 73.11 .. 76.90 |
| `TO(inf)+3` | 1963 | 77.05 .. 100.00 |
| `AW(inf)-3` | 92 | 1.14 .. 22.93 |
| `AW(inf)-2` | 246 | 23.26 .. 27.94 |
| `AW(inf)-1` | 573 | 28.02 .. 37.98 |
| `AW(inf)0` | 1453 | 38.02 .. 61.98 |
| `AW(inf)+1` | 589 | 62.04 .. 72.97 |
| `AW(inf)+2` | 259 | 73.11 .. 76.90 |
| `AW(inf)+3` | 109 | 77.43 .. 98.54 |

28946 of 28946 TO(inf) and 3321 of 3321 AW(inf) cells carry a suffix, and 0 suffixes sit on a cell
that is neither. The TO(inf) counts here are larger than the pre-build measurement above because
that one was taken on 8791's ws2Mage pivot trades and this one is 8792's pooled ws1 ones - a
different target-side on many rows, so a different tag on many cells.

## 3. THE VALUE

**The closed-prev r of that line at the row's print bar**, rounded to 2dp before it is placed.

Closed-prev is the banked chart-matched read: emerging is lift-off's read and lift-off's alone.
This is not a free choice — under the `either` ex-fence mode a cell is in-fence only when BOTH the
closed-prev value and the 60 s emerging extreme are in-fence, so both reads were available, and the
banked ruling picks between them.

## 4. WHAT CARRIES NO SUFFIX

| the cell | why |
|---|---|
| `TO(exf)`, `AW(exf)` | ex-fence by definition, so there is no in-fence distance to report |
| a blank cell | no state |
| the ws16-22 and ws23-30 sums | they print a COUNT of lines, not one line's text, so there is no one value to band |

## 5. WHERE IT LIVES

| the piece | where |
|---|---|
| the bands and the labels | `IFP_EDGES`, `IFP_LABELS`, `IFP_DP` in `fdm3_oracle.py` |
| the banked knobs | `INFENCE_EDGES`, `INFENCE_DP`, `INFENCE_READ` in `fdm3_knobs.py` |
| the band bits | bits 3-5 of each line's TO/AW byte, held as band+1 so 0 means no value |
| the text | the one place the page turns that byte into words |
| the bank check | the probe refuses a page whose edges or 2dp differ from the bank |

**NO BYTE WAS ADDED, AND NONE WAS ADDED FOR AW(inf) EITHER.** The TO/AW code uses bits 0-2 and the
band takes bits 3-5 of the same byte, so the row is still 55 bytes and every page keeps its layout.
**One cell is never both `TO(inf)` and `AW(inf)`**, so the two tags SHARE those three bits and the
code in bits 0-2 says which tag the number belongs to.

Every reader of that byte masks with 7 to get the code — the probe's one reader does — and two
asserts hold the mech: an in-fence cell with a value must have a band, and a band must never sit on
a cell that is neither `TO(inf)` nor `AW(inf)`.

## 6. A BANDLESS IN-FENCE CELL

A `TO(inf)` or `AW(inf)` cell CAN print bare, and only in the tape's warm-up. A line has no closed-prev value
until its first bar closes, and the first pseudo trade opens at 2026-07-02 14:33:45 — before ws8
and above have one.

| the line | bars with no closed-prev value | its last such bar |
|---|---|---|
| ws1 | 216 | 2026-07-02 12:17:55 |
| ws2 | 432 | 2026-07-02 12:35:55 |
| ws3 | 648 | 2026-07-02 12:53:55 |
| ws4 | 864 | 2026-07-02 13:11:55 |
| ws5 | 1080 | 2026-07-02 13:29:55 |
| ws6 | 1296 | 2026-07-02 13:47:55 |
| ws7 | 1440 | 2026-07-02 13:59:55 |
| ws8 | 1728 | 2026-07-02 14:23:55 |
| ws9 | 1944 | 2026-07-02 14:41:55 |
| ws10 | 2160 | 2026-07-02 14:59:55 |
| ws11 | 2316 | 2026-07-02 15:12:55 |
| ws12 | 2592 | 2026-07-02 15:35:55 |
| ws13 | 2748 | 2026-07-02 15:48:55 |
| ws14 | 2952 | 2026-07-02 16:05:55 |
| ws15 | 3240 | 2026-07-02 16:29:55 |

Those cells keep band 0 and print their tag with nothing after it. The invariant the code holds is
the one that can only break by fault: **an in-fence cell WITH a value must have a band.** Every build prints the count and
the share, so the warm-up stays visible instead of being asserted away. On 8792 that line reads
13287830 in-fence cells over every state, 554 of them bare - 0.00%.

## 7. CAUSAL

The band reads the line's own closed-prev value at the row's print bar and nothing later. It adds no
walk, no window and no forward read, so it is causal wherever the TO(inf) tag it decorates is.

## 8. OPEN

| the question | the state |
|---|---|
| does the suffix belong on `AW(inf)` too | **RULED AND BUILT.** He asked for it the same day; shown that his five ranges left 201 of 09-24's 3321 AW(inf) cells bare, he ruled the same seven bands |
| does any report or the Excel table need a band column | not asked for; the probe reads the band as `tapow` and nothing consumes it yet |
