# "-" on the counter side of 50

**GOAL: a line prints a TO or AW tag only while its r is on the target side of 50.** On the
counter side it prints "-", the trade's open included, so TO is earned rather than handed out.

HIS NAME for this rule: pending. The knob is `UNTAG50` in `fdm3_knobs.py` until he names it.

## 1. HIS WORDS, verbatim

> "8788 is good.  the next build will impact the AW and TO states, and be built on 8792
>
> now all lines will be non-tagged (eg "-") if they are on the counter side of 50 (not the fence)
> -this inculdes the start of a trade - TO must be "earnt" at the start of the trade if the line is already on target side, otherwise it it non-tagged"

Then, on the first build, which printed a bare "-":

> "I only asked for an update on TO, but now the whole row has been replaced with a "-"
> I still need to see the ([inf,exf])[the 7 bands]  data"

## 2. HIS ANSWERS, 2026-11-20

| the question | his answer |
|---|---|
| what "earnt" means at the trade's open | the side of 50 decides: a line on the target side prints TO, one on the counter side prints "-" and earns TO when it crosses to the target side |
| which r is tested against 50 | the emerging r |
| does a line printing "-" still count toward scenario 2's lines-under test | no - a line printing "-" is not printing away |
| which in-fence suffix the new 8792 carries | closed-prev, as before. 8788 keeps the emerging suffix |
| on the second pass: which tag does the "-" replace | TO and AW both. The (inf)/(exf) and the 7-band suffix stay: `-(inf)-1`, `-(exf)` |

## 3. THE RULE AS BUILT

- **Strictly** on the counter side: under 50.00 on a HIGH target-side, over 50.00 on a LOW one.
- **50, not the fence**: the flip, the 50 reset and void keep reading `fdm3-fence-reset-TO`'s
  33/67 line. Only the "-" reads 50.
- **A mask over the existing states**, plus the one scenario-2 exclusion. A line back on the target
  side prints whatever state it holds there.
- **The "-" replaces the TO or AW word only.** The cell keeps its fence tag and its band: `-(inf)-1`,
  `-(exf)`. Two new codes in bits 0-2, 5 `-(inf)` and 6 `-(exf)`; `-(inf)` carries the band in bits
  3-5 like TO(inf). Neither is a TO or AW state, so every count of TO, AW, TO(exf) or AW(exf) skips it.
- **Only inside a trade** and only on a page carrying the rule. Outside a trade a cell stays blank.
- **All lines**: ws16-30 are masked too, so the ws16-22 and ws23-30 columns count only tagged lines.

| the piece | where |
|---|---|
| the mask and the scenario-2 exclusion | `towards_away.run(..., untag=)` - None is the run as banked |
| the switch | `UNTAG50` in `fdm3_knobs.py`, 0 on the bank. 8792 runs it at 1 as an off-ruled page |
| the page | `fdm3_oracle.py` passes `untag=50.0`, publishes `/meta` `untag`, prints "-" |
| the bank check | `oracle_rows.py` pins `untag`: a bank run of orac-exhaust or setups REFUSES 8792 until he banks it, or the run sets `W_FDM3_EXPERIMENT=1` |

## 4. AS BUILT AND VERIFIED, 8792, 2026-11-20

Start-up 636.3 s, CONTROL MATCH 257,295. Checked against the 8792 rows saved before the rebuild and
against the emerging r read off the tape at each row's print bar.

| state | in-trade cells | on the counter side of 50 | of them "-" | on the target side | of them tagged |
|---|---|---|---|---|---|
| pivots as found | 4077368 | 1555569 | 1555569 | 2521799 | 2521799 |
| +15 min | 4077128 | 1440450 | 1440450 | 2636678 | 2636678 |
| flipped | 4077368 | 2521799 | 2521799 | 1555569 | 1555569 |
| +15 min, flipped | 4077128 | 2636678 | 2636678 | 1440450 | 1440450 |

Pivots as found, old 8792 -> new 8792:

| old | new | cells | the side of 50 |
|---|---|---|---|
| TO(inf) | - | 1372602 | counter |
| AW(inf) | - | 182957 | counter |
| TO(exf) | - | 3 | counter |
| AW(exf) | - | 7 | counter |
| AW(inf) | TO(inf) | 4388 | target - scenario 2 without the "-" lines under it |
| TO(inf) | AW(inf) | 53 | target - scenario 2 without the "-" lines under it |

| the page's other columns, pivots as found | cells that differ |
|---|---|
| TO:x AW:x sums | 346111 |
| TO -> AW flip marks | 1141 |
| x / e crosses | 0 |
| TO(exf) sums | 0 |
| up/dn and the Mage colour | 0 |
| SL% | 0 |
| legMage | 0 |
| `sml` / `lrg` | 0 |
| target-side | 0 |

The first row of each trade, pivots as found - 3002 trades x 15 lines:

| prints | cells |
|---|---|
| - | 29578 |
| TO(inf) | 11935 |
| TO(exf) | 3480 |
| AW(inf) | 10 - the old 8792 had the same 10 |

A line coming back from "-" to a tag inside the same trade, pivots as found:

| it printed before the "-" | it prints on return | times |
|---|---|---|
| "-" since the trade's first row | TO(inf) | 22096 |
| "-" since the trade's first row | TO(exf) | 2 |
| TO(inf) | TO(inf) | 26770 |
| TO(inf) | AW(inf) | 1 |
| TO(exf) | TO(inf) | 110 |
| AW(inf) | AW(inf) | 10512 |
| AW(inf) | TO(inf) | 30 |
| AW(exf) | AW(inf) | 260 |
| AW(exf) | TO(inf) | 4 |

**AN AW THAT DIPS UNDER 50 COMES BACK AS AW.** The AW -> TO flip on 8792 reads the 33/67 line, so a
HIGH target-side AW line that falls under 50 and climbs back prints AW between 50 and 67, and TO
from its first bar back over 67. Not ruled on - read off the code, not chosen.

### 4a. THE SECOND PASS - the "-" keeps its fence tag and band, 2026-11-20

Start-up 610.5 s, CONTROL MATCH 257,295. Against the first pass every byte is equal except the "-"
cells' codes; against the old 8792 each "-" cell carries the fence tag and band the old page printed.

| state | "-" cells | -(inf) | -(exf) | -(inf) on an old in-fence cell, same band | -(exf) on an old ex-fence cell | -(inf) with no band, warm-up |
|---|---|---|---|---|---|---|
| pivots as found | 1555569 | 1555559 | 10 | 1555559 | 10 | 89 |
| +15 min | 1440450 | 1440441 | 9 | 1440441 | 9 | 82 |
| flipped | 2521799 | 2521793 | 6 | 2521793 | 6 | 91 |
| +15 min, flipped | 2636678 | 2636671 | 7 | 2636671 | 7 | 86 |

Pivots as found, by band:

| the cell prints | cells |
|---|---|
| `-(inf)-3` | 194016 |
| `-(inf)-2` | 92918 |
| `-(inf)-1` | 230049 |
| `-(inf)0` | 526150 |
| `-(inf)+1` | 248656 |
| `-(inf)+2` | 71464 |
| `-(inf)+3` | 192217 |
| `-(exf)` | 10 |

## 5. OPEN

| the question | the state |
|---|---|
| his name for the rule | pending |
| bank it | not asked for. 8792 runs it off the bank |
| an AW coming back from "-" prints AW | shown to him 2026-11-20, no ruling |
