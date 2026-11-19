# fdm3-infence-power

**GOAL: a TO(inf) cell should say HOW FAR from the fence the line sits, not only that it is inside
it.** The tag today is binary — in-fence or ex-fence — so a line at 50 and a line at 76 print the
same thing. The suffix makes the distance readable at a glance.

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

## 2. THE BANDS

Every edge is LOW-INCLUSIVE and read at 2dp, which is his own worked example: 62 to 73 means 62.00
to 72.99, so 62.00 opens the +1 band and 73.00 opens the next one.

| the value, 2dp | the cell prints | 2026-09-24 cells | share |
|---|---|---|---|
| under 23.00 | `TO(inf)-3` | 1290 | 5.6% |
| 23.00 to 27.99 | `TO(inf)-2` | 913 | 3.9% |
| 28.00 to 37.99 | `TO(inf)-1` | 3940 | 17.0% |
| 38.00 to 61.99 | `TO(inf)0` | 11677 | 50.4% |
| 62.00 to 72.99 | `TO(inf)+1` | 3869 | 16.7% |
| 73.00 to 76.99 | `TO(inf)+2` | 933 | 4.0% |
| 77.00 and over | `TO(inf)+3` | 552 | 2.4% |

**THE -3 AND +3 ARE HIS RULING, NOT HIS FIVE BANDS.** His five cover 23.00 to 76.99 and reached
21332 of the 23174 TO(inf) cells on 09-24 — 92.1%. The other 1842 cells, 7.9%, sat outside them
because **the ex-fence test reads the TARGET SIDE ONLY**: a HIGH target-side line is ex-fence only
at 77.00 and over, so a value of 0.05 is still in-fence and still prints TO(inf). The lowest value
on a TO(inf) cell that day was 0.05 and the highest 98.33. Shown the count, he chose two new bands
over extending the ends or printing bare.

## 3. THE VALUE

**The closed-prev r of that line at the row's print bar**, rounded to 2dp before it is placed.

Closed-prev is the banked chart-matched read: emerging is lift-off's read and lift-off's alone.
This is not a free choice — under the `either` ex-fence mode a cell is in-fence only when BOTH the
closed-prev value and the 60 s emerging extreme are in-fence, so both reads were available, and the
banked ruling picks between them.

## 4. WHAT CARRIES NO SUFFIX

| the cell | why |
|---|---|
| `AW(inf)` | his words name TO(inf) and nothing else |
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

**NO BYTE WAS ADDED.** The TO/AW code uses bits 0-2 and the band takes bits 3-5 of the same byte,
so the row is still 55 bytes and every page keeps its layout. Every reader of that byte masks with
7 to get the code — the probe's one reader does, and two asserts hold it: a TO(inf) cell must have
a value to band, and a band must never sit on a cell that is not TO(inf).

## 6. A BANDLESS TO(inf) CELL

A TO(inf) cell CAN print bare, and only in the tape's warm-up. A line has no closed-prev value
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

Those cells keep band 0 and print a bare `TO(inf)`. The invariant the code holds is the one that
can only break by fault: **a cell WITH a value must have a band.** Every build prints the count and
the share, so the warm-up stays visible instead of being asserted away.

## 7. CAUSAL

The band reads the line's own closed-prev value at the row's print bar and nothing later. It adds no
walk, no window and no forward read, so it is causal wherever the TO(inf) tag it decorates is.

## 8. OPEN

| the question | the state |
|---|---|
| does the suffix belong on `AW(inf)` too | not asked for; his words name TO(inf) |
| does any report or the Excel table need a band column | not asked for; the probe reads the band as `tapow` and nothing consumes it yet |
