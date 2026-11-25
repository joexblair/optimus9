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

### 3a. THE EMERGING READ, ON 8788 (his 1120)

> "duplicate 8792 onto 8788, with one change: AW(inf) cells get the same 7 in-fence bands as
> TO(inf), and all 14 bands use emerging bars instead of closed-prev"

**THE READ IS THE KNOB `INFENCE_READ`** in `fdm3_knobs.py`: `closed_prev` on the bank, `emerging`
on 8788, which runs it as an off-ruled page (`W_FDM3_EXPERIMENT=1 W_FDM3_INFENCE_READ=emerging`,
plus 8792's `FDM3_ROW_S=30 FDM3_PIVOTS=pooled`). The knob existed before 1120 but the page never read
it; it reads it now, and `/meta` publishes it as `ifpread`. The AW(inf) half of his ask was already
on 8792. **ONLY THE SUFFIX MOVES**: the TO/AW code and its ex-fence test are untouched.

MINE: the emerging value is the line's emerging r at the row's print bar - the same 5 s bar the
cell's code is read at - and not the 60 s emerging extreme the ex-fence test also reads.

8788 against 8792, every row, 2026-11-20:

| state | bytes outside the TO/AW block that differ | TO/AW codes that differ | in-fence cells | suffixes that differ | TO(inf) | AW(inf) | bare on 8788 | bare on 8792 |
|---|---|---|---|---|---|---|---|---|
| pivots as found | 0 | 0 | 3048753 | 1369424 | 1175379 | 194045 | 0 | 134 |
| +15 min | 0 | 0 | 2942394 | 1315602 | 1035195 | 280407 | 0 | 125 |
| flipped | 0 | 0 | 3595386 | 1487785 | 1233547 | 254238 | 0 | 155 |
| +15 min, flipped | 0 | 0 | 3701297 | 1541410 | 1387976 | 153434 | 0 | 140 |

2026-09-24, pivots as found, each suffix's range of the value it was placed on, read off the tape:

| the cell prints | 8788 cells, emerging r | its range | 8792 cells, closed-prev r | its range |
|---|---|---|---|---|
| `TO(inf)-3` | 1338 | 0.00 .. 22.99 | 1932 | 0.00 .. 22.93 |
| `TO(inf)-2` | 1508 | 23.00 .. 27.98 | 1268 | 23.06 .. 27.98 |
| `TO(inf)-1` | 4595 | 28.00 .. 37.99 | 4452 | 28.07 .. 37.96 |
| `TO(inf)0` | 13593 | 38.00 .. 61.99 | 13498 | 38.01 .. 61.98 |
| `TO(inf)+1` | 5097 | 62.00 .. 72.99 | 4553 | 62.00 .. 72.97 |
| `TO(inf)+2` | 1353 | 73.00 .. 76.99 | 1280 | 73.11 .. 76.90 |
| `TO(inf)+3` | 1462 | 77.00 .. 100.00 | 1963 | 77.05 .. 100.00 |
| `AW(inf)-3` | 113 | 0.54 .. 22.91 | 92 | 1.14 .. 22.93 |
| `AW(inf)-2` | 248 | 23.11 .. 27.99 | 246 | 23.26 .. 27.94 |
| `AW(inf)-1` | 557 | 28.02 .. 37.97 | 573 | 28.02 .. 37.98 |
| `AW(inf)0` | 1331 | 38.01 .. 61.98 | 1453 | 38.02 .. 61.98 |
| `AW(inf)+1` | 750 | 62.01 .. 72.98 | 589 | 62.04 .. 72.97 |
| `AW(inf)+2` | 206 | 73.00 .. 76.87 | 259 | 73.11 .. 76.90 |
| `AW(inf)+3` | 116 | 77.20 .. 98.54 | 109 | 77.43 .. 98.54 |

The 8792 column equals the as-built table in section 2, cell for cell.

### 3b. THE PER-MINUTE READ, AND THE (exf) SUFFIX, ON 8793 (his 1121)

> "shut 8791 down - the hold 1 tol 0.67 isn't useful
> the next job will clone 8792, and spin it up on 8793 with this change:
> instead of the 7 bands updating on closed-prev, I now want them to all update per closed-prev minute
> eg, ws12 will now print 12 updates over 12 minutes, instead of 1 update per 12 minutes"

Then, while 8793 was starting:

> "we'll add the suffix to TO/AW(exf) now.  this addition will serve to  highlight diffs between the
> closed-prev derived 'exf', and the more granular 1m seams.  confirm you understand what I'm expecting
> from this change"

His answers: 8793 only, and "-(exf)" carries it too.

**THE VALUE IS `INFENCE_READ` = `closed_prev_minute`**: the line's emerging r at the last 5 s bar of
the last CLOSED MINUTE - the closed-prev arithmetic at 60 s on every line, midnight grid. ws1 reads
what it read on 8792; ws2..ws15 step once a minute instead of once per own bar.

**THE (exf) SUFFIX IS `EXF_SUFFIX` = 1**: the same band of the same value goes on `TO(exf)`,
`AW(exf)` and `-(exf)`. Read with the 23/77 fence, a cell whose 1 m value agrees with its `(exf)` tag
prints the far band on its target side - `+3` (77.00 and over) on a HIGH target side, `-3` (under
23.00) on a LOW one. Any other suffix on an `(exf)` cell is a cell where the tag and the 1 m value
disagree.

**THE (exf) TAG IS NOT CLOSED-PREV ALONE**, and he should read the diffs knowing it: a cell is
`(exf)` when the line's closed-prev value at its OWN timeframe is past 23/77, OR its emerging value
was past 23/77 on any 5 s bar of the last 60 s (v4 knobs `FDM_EXF_READ` 'either',
`FDM_EXF_EM_BARS` 12). Neither the tag nor any TO/AW code moves on 8793.

**THE OTHER DIRECTION PRINTS ONLY BY ROUNDING.** An `(inf)` cell's last-closed-minute bar sits inside
that same 60 s window, so its value cannot be past 23/77 on the target side. 35 `(inf)` cells (as
found) still print the far band, and all 35 are values within 0.005 of the edge that round to it at
2dp - 76.9983 prints `+3` while the `(exf)` test reads it as under 77.

The process: `FDM3_ROW_S=30 FDM3_PIVOTS=pooled W_FDM3_EXPERIMENT=1 W_FDM3_UNTAG50=1
W_FDM3_INFENCE_READ=closed_prev_minute W_FDM3_EXF_SUFFIX=1`, an off-ruled page. The probe's page
check pins both keys, so orac-exhaust refuses 8793 on the bank.

8793 with the per-minute read alone, against 8792, every row, 2026-11-21:

| state | bytes outside the TO/AW block that differ | TO/AW codes that differ | in-fence cells | bands that differ from 8792 | bands off the per-minute tape read | bare on 8793 | bare on 8792 |
|---|---|---|---|---|---|---|---|
| pivots as found | 0 | 0 | 3048753 | 1093141 | 0 | 10 | 134 |
| flipped | 0 | 0 | 3595386 | 1168609 | 0 | 13 | 155 |
| +15 min | 0 | 0 | 2942394 | 1033530 | 0 | 11 | 125 |
| +15 min, flipped | 0 | 0 | 3701297 | 1228072 | 0 | 12 | 140 |

Pivots as found, per line:

| the line | in-fence cells | bands that differ from 8792 |
|---|---|---|
| ws1 | 196977 | 0 |
| ws2 | 189588 | 43368 |
| ws3 | 187317 | 57595 |
| ws4 | 191579 | 66475 |
| ws5 | 196315 | 71820 |
| ws6 | 199749 | 75605 |
| ws7 | 203072 | 79580 |
| ws8 | 204477 | 82381 |
| ws9 | 206380 | 85664 |
| ws10 | 209418 | 86243 |
| ws11 | 210315 | 87165 |
| ws12 | 210978 | 87398 |
| ws13 | 213856 | 89232 |
| ws14 | 213246 | 90715 |
| ws15 | 215486 | 89900 |

8793 with both, against 8792, every row, 2026-11-21 - the per-minute table above holds unchanged
(every in-fence band matches the per-minute tape read in both 8793 builds), and the (exf) cells read:

| state | (exf) cells | bands off the per-minute tape read | far band on the target side - agrees with (exf) | any other suffix - disagrees | bare |
|---|---|---|---|---|---|
| pivots as found | 1028615 | 0 | 862247 | 166364 | 4 |
| flipped | 481982 | 0 | 306648 | 175333 | 1 |
| +15 min | 1134734 | 0 | 923577 | 211154 | 3 |
| +15 min, flipped | 375831 | 0 | 245296 | 130533 | 2 |

The start-up line agrees: 3021162 (exf) cells over every state, 10 bare (warm-up). Bytes outside
the TO/AW block, and every TO/AW code, equal 8792's in all 4 states. CONTROL MATCH 257295.

The first disagreeing ws12 cell on 2026-09-30, pivots as found: the row 2026-09-30 00:23:30 prints
`TO(exf)-2`. Its print bar is 00:24:00, where ws12's emerging r is 12.64 - past 23 on the LOW side,
so the 60 s half of the test made it `(exf)`; ws12's own closed-prev (26.31) and its last closed
minute (00:23:55, 26.31) are both in-fence.

### 3c. THE +4 AND -4 BANDS, ON 8793 (his 1121)

> "update 8793
> add  +4 and -4 ranges.  100-92  for '+4' and 0-8 for '-4'
> adjust +3 and -3 to fit accordingly"

Then, while 8793 was starting:

> "confirm that these will update on the new 1 minute seams"

**THE EDGES ARE `INFENCE_EDGES` = 8, 23, 28, 38, 62, 73, 77, 92 on 8793**, read low-inclusive at 2dp
by his own section 2 rule. The bank keeps the six edges of section 2. The value is the one section 3b
names - `INFENCE_READ` = `closed_prev_minute` - so the -4 and +4 step on the same 1 minute seams as
every other band. Only the placement of the value moved.

| the value, 2dp | the suffix on 8793 | on 8792 and the bank |
|---|---|---|
| 0.00 to 7.99 | -4 | -3 |
| 8.00 to 22.99 | -3 | -3 |
| 23.00 to 27.99 | -2 | -2 |
| 28.00 to 37.99 | -1 | -1 |
| 38.00 to 61.99 | 0 | 0 |
| 62.00 to 72.99 | +1 | +1 |
| 73.00 to 76.99 | +2 | +2 |
| 77.00 to 91.99 | +3 | +3 |
| 92.00 and over | +4 | +3 |

**THE BAND BITS ARE 3-6 ON A NINE-BAND PAGE.** The band is held as band+1, so +4 is 9 and needs bit
6. Bit 7 stays clear (the largest byte is -(exf)+4, 78). Every band read masks with 15; on a
seven-band page bit 6 is never set, so 8792 and 8788 read what they read. The labels follow the
edge count: 2n edges print -n .. +n.

**AS BUILT AND VERIFIED on 8793**, every state, each band re-derived from the tape: the 60 s
closed-prev of the line's emerging r at the row's print bar, placed on the nine edges. A band move
counts where the row before and this row both carry a suffix and the two differ; a row whose print
bar opens a minute is a row opening at :30.

| state | banded cells | off the tape read | bare | -4 | -3 | +3 | +4 | band moves, print bar opens a minute | band moves, any other row |
|---|---|---|---|---|---|---|---|---|---|
| pivots as found | 4077368 | 0 | 14 | 126316 | 475268 | 458438 | 108918 | 371529 | 0 |
| flipped | 4077368 | 0 | 14 | 126316 | 475268 | 458438 | 108918 | 371529 | 0 |
| +15 min | 4077128 | 0 | 14 | 126316 | 475246 | 458438 | 108918 | 371505 | 0 |
| +15 min flipped | 4077128 | 0 | 14 | 126316 | 475246 | 458438 | 108918 | 371505 | 0 |

Bytes outside the TO/AW block, and every TO/AW code, equal 8792's in all 4 states.

**THE RED SUFFIX (his 1121):**

> "for coloring: when a highband line (ws8-15) flips from +4 to +3, or from -4 to -3, print the 3 in red"

His answers: "Yes, suffix alone" - the tag on either row does not matter; "+3 / -3, sign and digit"
- the whole suffix is red and the tag keeps its white or grey; "Yes, any drop off ±4" - red on
whatever suffix a row lands on after a +4 or -4.

- on ws8 to ws15, a row is red when:
  - the row before printed +4 and this row prints a suffix under +4
  - OR the row before printed -4 and this row prints a suffix over -4
- that row only; the row before is the row directly above, whichever pseudo trade it is in - the
  TO -> AW flip's own rule
- +32 in the line's cross code; only a page with his +4 and -4 sets it, so a seven-band page never
  does

| state | red cells | +4 -> +3 | -4 -> -3 | a drop past ±3 | off the re-derive | red off ws8-ws15 |
|---|---|---|---|---|---|---|
| pivots as found | 6975 | 3267 | 3708 | 0 | 0 | 0 |
| flipped | 6975 | 3267 | 3708 | 0 | 0 | 0 |
| +15 min | 6975 | 3267 | 3708 | 0 | 0 | 0 |
| +15 min flipped | 6975 | 3267 | 3708 | 0 | 0 | 0 |

| line, pivots as found | red cells |
|---|---|
| ws8 | 1116 |
| ws9 | 935 |
| ws10 | 946 |
| ws11 | 940 |
| ws12 | 856 |
| ws13 | 791 |
| ws14 | 718 |
| ws15 | 673 |

ws12, pivots as found: the row 2026-07-03 16:39:00 prints `TO(exf)-4` on its last closed minute
6.61; the row 2026-07-03 16:39:30 reads 9.59 at its print bar 2026-07-03 16:40:00 and prints
`TO(exf)` with a red `-3`.

**HIS 1122 - ws2 TO ws15:**

> "there is a red colouring applied to hband (high band lines) when 4 flips to 3.  expand the red colour mech's coverage to include ws2-ws15"

The rule above is unchanged; only its lines move, from ws8..ws15 to ws2..ws15 (`RED4_TFS` in the
page, the lines the red suffix reads). The counts above are the 1121 page's, ws8..ws15 on the pooled
pivots and the 1-minute read. The machine's own are in section 3d.

### 3d. THE 30 s SEAM, AND THE RED ON ws2-ws15, ON THE MACHINE (his 1122)

> "instead of testing values on the 1 minute seam (current behaviour for all TFs), now the seam will be every 30sec.  it should fire at x:25 and x:55 so that oracel has the most current data"

**`INFENCE_READ` = `closed_prev_30s`, BANKED 1122** (the name is mine): the closed-prev arithmetic
at 30 s on every line's emerging r - the value at the last 5 s bar of the last closed 30 s slot,
the x:25 or x:55 bar. A row's print bar opens at x:00 or x:30, so every row reads the bar just
before it. The suffix on TO(exf), AW(exf) and -(exf) reads the same value. Nothing else on the page
moves: the TO/AW code, its ex-fence test and every other read are as they were.

**AS BUILT AND VERIFIED on 8793**, 2026-11-22, against 8794 (the same page on the 1-minute read
with the red on ws8..ws15), both trades, every row, each band re-derived from the tape (r 6,6,9):

| check | short | long |
|---|---|---|
| meta keys that differ from 8794 | the band read alone | the band read alone |
| rows read at a bar at second 25 | 136080 | 136080 |
| rows read at a bar at second 55 | 136079 | 136079 |
| rows x lines where the read is not the bar just before the print bar | 0 | 0 |
| bytes outside the TO/AW and cross blocks that differ from 8794 | 0 | 0 |
| TO/AW codes that differ from 8794 | 0 | 0 |
| cross bits other than the red one that differ from 8794 | 0 | 0 |
| banded-code cells | 4078124 | 4078124 |
| bands off the 30 s tape read | 0 | 0 |
| bare cells (warm-up) | 15 | 15 |
| cells whose band differs from 8794 | 353295 | 353295 |

| band moves between two rows | 8793, 30 s seam | 8794, 1-minute seam |
|---|---|---|
| on a row whose print bar opens at second 00 | 167610 | 394691 |
| on a row whose print bar opens at second 30 | 353280 | 0 |

The lines are the fdm3 knob `RED4_LINES`, 2-15 on the bank. 8794 runs beside 8793 since 2026-11-22
19:12:45 with `RED4_LINES` 8-15 and `INFENCE_READ` `closed_prev_minute`, his answer *"As it was"*; against
8793 its band moves and red cells per line equal the 8794 columns below, every one.

The red suffix, re-derived from the page's own suffix text row by row on ws2..ws15:

| check | short | long |
|---|---|---|
| red cells | 31224 | 31224 |
| +4 -> +3 | 15009 | 15009 |
| +4 -> +2 | 47 | 47 |
| -4 -> -3 | 16120 | 16120 |
| -4 -> -2 | 48 | 48 |
| off the re-derive | 0 | 0 |
| red on ws1 | 0 | 0 |

| line | red cells, 8794 (ws8..ws15, 1-minute read) | red cells, 8793 (ws2..ws15, 30 s read) |
|---|---|---|
| ws1 | 0 | 0 |
| ws2 | 0 | 4378 |
| ws3 | 0 | 3458 |
| ws4 | 0 | 3011 |
| ws5 | 0 | 2586 |
| ws6 | 0 | 2346 |
| ws7 | 0 | 2158 |
| ws8 | 1557 | 2043 |
| ws9 | 1406 | 1897 |
| ws10 | 1283 | 1724 |
| ws11 | 1287 | 1725 |
| ws12 | 1214 | 1641 |
| ws13 | 1140 | 1494 |
| ws14 | 1069 | 1425 |
| ws15 | 988 | 1338 |

ws3, the short trade, from 4 rows before its first red cell:

| row | print bar | bar it reads | value it reads | 8793 cell | red | 8794 cell |
|---|---|---|---|---|---|---|
| 2026-07-02 14:54:30 | 2026-07-02 14:55:00 | 2026-07-02 14:54:55 | 6.71 | TO(exf)-4 |  | TO(exf)-4 |
| 2026-07-02 14:55:00 | 2026-07-02 14:55:30 | 2026-07-02 14:55:25 | 6.71 | TO(exf)-4 |  | TO(exf)-4 |
| 2026-07-02 14:55:30 | 2026-07-02 14:56:00 | 2026-07-02 14:55:55 | 7.18 | TO(exf)-4 |  | TO(exf)-4 |
| 2026-07-02 14:56:00 | 2026-07-02 14:56:30 | 2026-07-02 14:56:25 | 7.34 | TO(exf)-4 |  | TO(exf)-4 |
| 2026-07-02 14:56:30 | 2026-07-02 14:57:00 | 2026-07-02 14:56:55 | 8.84 | TO(exf)-3 | yes | TO(exf)-3 |
| 2026-07-02 14:57:00 | 2026-07-02 14:57:30 | 2026-07-02 14:57:25 | 7.06 | TO(exf)-4 |  | TO(exf)-3 |
| 2026-07-02 14:57:30 | 2026-07-02 14:58:00 | 2026-07-02 14:57:55 | 10.42 | TO(exf)-3 | yes | TO(exf)-3 |
| 2026-07-02 14:58:00 | 2026-07-02 14:58:30 | 2026-07-02 14:58:25 | 10.61 | AW(exf)-3 |  | AW(exf)-3 |


### 3e. THE b9 COLOURS ON fdm3-htf-oracle (his 1124)

His words: *"I'm now refering to the 9 bands as `b9`"* / *"the red b9 coloring that applies to +/-4 flips to +/-3 will be
extended"* / *"a (+/-) 4 to 3 change will still be coloured in red"* / *"for any of (+/-) 3 to 2, 2 to 1, 1 to 0,  where
the change has moved to a band that is counter trade (existing behaviour), the number will be coloured orange"*. His
answers: counter trade is *"Against the trade's side"*, *"Red against trade only"*, *"Orange on any such move"*.

| the row's trade | the move from the row before | colour |
|---|---|---|
| short (target-side LOW) | up, off -4 | red |
| short | up, off -3, -2 or -1 | orange |
| long (target-side HIGH) | down, off +4 | red |
| long | down, off +3, +2 or +1 | orange |

- Both rows must carry a b9 suffix; the tag on either row does not matter (the 1121 red's own rule).
- fdm3-htf-oracle only, on all 16 of its columns. fdm3-oracle (8793) keeps its 1121/1122 red: off +/-4 on both trades,
  ws2-ws15.
- In the cross code: +32 red, +64 orange.

Checks on 8795, serving 2026-11-24 20:24:41, every cell re-derived from the tape and the cells' own suffixes:

| check | short | long |
|---|---|---|
| b9 cells | 2,162,468 | 2,162,468 |
| b9 off the tape re-derive (30 s closed-prev of the 6,6,9 r, at the x:55 bar) | 0 | 0 |
| bare (no value yet, warm-up) | 15 | 15 |
| red cells | 5,370 | 5,171 |
| red off the re-derive | 0 | 0 |
| orange cells | 30,524 | 33,228 |
| orange off the re-derive | 0 | 0 |

| move | short | long |
|---|---|---|
| red -4 -> -3 | 5,366 | - |
| red -4 -> -2 | 4 | - |
| orange -3 -> -2 | 8,448 | - |
| orange -3 -> -1 | 1,311 | - |
| orange -3 -> 0 | 71 | - |
| orange -2 -> -1 | 8,937 | - |
| orange -2 -> 0 | 575 | - |
| orange -1 -> 0 | 11,182 | - |
| red +4 -> +3 | - | 5,167 |
| red +4 -> +2 | - | 4 |
| orange +3 -> +2 | - | 9,109 |
| orange +3 -> +1 | - | 1,733 |
| orange +3 -> 0 | - | 46 |
| orange +2 -> +1 | - | 9,534 |
| orange +2 -> 0 | - | 407 |
| orange +1 -> 0 | - | 12,399 |

- No coloured move crossed 0 in one row: none lands on the other sign.

## 4. WHAT CARRIES NO SUFFIX

| the cell | why |
|---|---|
| `TO(exf)`, `AW(exf)`, `-(exf)` | ex-fence by definition, so there is no in-fence distance to report - EXCEPT on 8793, where his 1121 `EXF_SUFFIX` puts the band on them, section 3b |
| a blank cell | no state |
| the ws16-22 and ws23-30 sums | they print a COUNT of lines, not one line's text, so there is no one value to band |

## 5. WHERE IT LIVES

| the piece | where |
|---|---|
| the bands and the labels | `IFP_EDGES`, `IFP_LABELS`, `IFP_DP` in `fdm3_oracle.py`; since his 1121 the edges come from the knob `INFENCE_EDGES` and the labels from their count |
| the banked knobs | `INFENCE_EDGES`, `INFENCE_DP`, `INFENCE_READ` in `fdm3_knobs.py`; the page reads `INFENCE_READ` through `fdm3_knobs_shim` since his 1120, and `EXF_SUFFIX` since his 1121 (1 on the bank since 1121). On the machine since 1122: the nine edges, `INFENCE_READ` = `closed_prev_30s` (section 3d), `EXF_SUFFIX` 1 |
| the band bits | bits 3-5 of each line's TO/AW byte, held as band+1 so 0 means no value; bits 3-6 on the nine bands (his 1121 +4 and -4, section 3c), banked 1121 |
| the text | the one place the page turns that byte into words |
| the bank check | the probe refuses a page whose edges, 2dp or read differ from the bank. A page built before `ifpread` existed read closed-prev, so a missing key counts as that |

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
