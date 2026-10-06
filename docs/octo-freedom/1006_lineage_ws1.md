# THE ws1-ANCHORED LINEAGE — BUILT 1006, HALTED ON ONE DEFINITION

Joe's spec, 1006, verbatim:

> *"for the lineage to qualify legal, it needs to be measured from ws1 and jump no more than 2 higher
> TFs to find the next TF with momentum"*
> *"TF numbers. eg, ws1 can only look to ws2 and ws3 for a baton pass"*
> *"os_legal_succ should be a confirmation of the lineage - if its 1, we can act on os_stalled_now and
> os_new_stalls"*
> *"I know the spec doesn't include ws1r at the moment, but this example shows me that we need it as
> an anchor"*

## WHAT IS BUILT

| piece | where | state |
|---|---|---|
| `LIN_HOP` = 2, `LIN_ANCHOR` = ws1, `LIN_TF` = ws1..ws12 | `octosig_db.py` | built |
| `lineage(mt_at)` — walk up from ws1, hop <= 2, repeat | `octosig_db.py` | built |
| `r_band(v, d)` — 'O' oob / 'x' between fences / '.' in-fence, dr-sided | `octosig_db.py` | built |
| `baton.MT12` — mom-true over ws1..ws12, `TFS` untouched | `baton.py` | built |
| 18 new columns | `octosig_rulings` | ALTERed in, populated |
| 09-25 smoke build, 39 rows | knob key `...\|lineage-ws1` | done |
| 12-day rebuild | — | **NOT RUN — held on the question below** |

`baton.py`'s own report is **byte-identical** before and after the MT12 addition (225 lines, diff
rc=0). `TFS` stays `range(3, 24)`, so `os_stalled_n`, `os_momtrue_n`, the "of 21" denominator and the
baton chain did not move.

## THE NEW COLUMNS

| column | what it holds |
|---|---|
| `os_lin_chain` | the realised walk, e.g. `ws1 > ws3` |
| `os_lin_top` / `os_lin_len` / `os_lin_broke_at` | where it reached, how many TFs, the TF it could not hop past |
| `os_lin_mt` / `os_lin_mt_hi` | every mom-true TF in ws1..ws12, and the highest |
| `os_legal_succ` | REDEFINED — 1 = the chain reached `os_lin_mt_hi`, 0 = momentum stranded above a gap > 2, NULL = no mom-true TF at all |
| `os_r_ladder` | 12 characters, ws1..ws12: `O` oob, `x` between 83 and 85, `.` in-fence |
| `os_r_ws1` / `os_r_oob_top` / `os_r_between_n` | the anchor's r, the highest oob TF, the count in the band |
| `os_casc_str` | the Mage cascade ws1..ws12 as text, 1 dp, comma separated |
| `os_casc_mid_end` | mean(ws3,ws4) minus mean(ws1,ws12). NEGATIVE = the matryoshka V |
| `os_casc_fast` / `os_casc_slow` | ws3-ws1 and ws11-ws6 |
| `os_casc_spread` / `os_casc_argmin` / `os_casc_argmax` / `os_casc_monotone` | the ladder's shape |

Anchor for all of them: the **routing anchor** — the lookback-g5extrema bar, or the fwd-g5extrema
bar when the lookback found none. The same bar mtd and branch D read.

## THE TWO BARS JOE READ

### 11:28:15, anchor 11:27:10, dr +1

| TF | r | band | mom-true | Mage |
|---|---|---|---|---|
| ws1 | 79.89 | . | Y | 102.42 |
| ws2 | 56.57 | . | - | 111.68 |
| ws3 | 80.64 | . | Y | 112.80 |
| ws4 | 76.89 | . | - | 125.44 |
| ws5 | 68.07 | . | - | 125.36 |
| ws6 | 81.99 | . | - | 113.85 |
| ws7 | 86.94 | O | - | 108.65 |
| ws8 | 94.40 | O | Y | 113.13 |
| ws9 | 97.14 | O | Y | 109.80 |
| ws10 | 83.27 | x | Y | 114.78 |
| ws11 | 74.54 | . | Y | 117.74 |
| ws12 | 73.01 | . | Y | 113.16 |

Joe's read: *"ws9 oob, ws10 is between ex-fence and oob, and ws11 and ws12 are infence"* — **exact
match on all four lines**, at the anchor AND at os_ts.

Joe's read of the lineage: *"my view sees 11:28's lineage incrementing in steps of 1 and 2 (legal)"*.
The built chain is `ws1 > ws3`, `os_legal_succ` 0 — ws3 to ws8 is a 5-TF gap in mom-true.

### 09:32:00, anchor 09:28:05, dr +1

| TF | r | band | mom-true | Mage |
|---|---|---|---|---|
| ws1 | 93.72 | O | Y | 106.90 |
| ws2 | 54.88 | . | Y | 94.86 |
| ws3 | 45.57 | . | - | 87.82 |
| ws4 | 50.80 | . | - | 89.92 |
| ws5 | 48.65 | . | - | 95.95 |
| ws6 | 48.55 | . | - | 101.01 |
| ws7 | 48.03 | . | - | 101.33 |
| ws8 | 38.80 | . | - | 102.29 |
| ws9 | 52.68 | . | - | 108.04 |
| ws10 | 61.80 | . | - | 113.99 |
| ws11 | 74.82 | . | - | 115.60 |
| ws12 | 79.77 | . | - | 110.51 |

Joe's read: *"ws1 is the strongest line, so market reverses because ws2 and ws3 are infence"* — the
band column agrees, ws1 is the only `O` and ws2/ws3 are `.`.
The built chain is `ws1 > ws2`, `os_legal_succ` 1 — because **momo_g_why calls ws2 mom-true at r
54.88**.

## THE HALT

Two readings of *"the next TF with momentum"* are both defensible and they disagree:

| reading | what it is | 09:32 chain | 11:28 chain |
|---|---|---|---|
| **A — mom-true** | `momo_g_why` state in (`momo`, `curl`); the project's existing definition everywhere | `ws1 > ws2` | `ws1 > ws3` |
| **B — the r band** | r at or beyond the ex-fence (83 / 17); the words Joe used in both reads | `ws1` | `ws1` |

Measured over 09-25, 39 octo-sigs: **the two chains are identical on 14 rows and differ on 25.**

Neither reproduces *"11:28's lineage incrementing in steps of 1 and 2"*. Under A the ws1 walk stops
at ws3; under B it never leaves ws1. The contiguous run Joe is describing at 11:28 is **ws8-ws9-ws10-
ws11-ws12** — the top of the ladder, not a walk from ws1.

**Open for Joe's ruling:**
1. Is "momentum" in the lineage mom-true (A), or the r band (B), or a third thing?
2. At 11:28 the picture he is reading sits at the oob line and its peers, not at ws1. Is the lineage
   anchored at ws1 ALWAYS, or anchored at ws1 only when ws1 is the oob line?

Both readings are banked as columns (`os_lin_mt` for A, `os_r_ladder` for B) so either answer is a
query, not a rebuild.

## ALSO HELD

Joe 1006: *"a logic update is needed for the mech (09:32)"*, referring to the matryoshka read. The
rule itself has not been named. `os_mage_net` is **unchanged**; the shape is banked as data
(`os_casc_*`) and nothing reads it yet.

`os_casc_mid_end` on the two bars: 09:32 **-19.83** (the V, middle below the ends), 11:28 **+11.33**
(the inverse). Banked, not acted on.

## LAST, AT JOE'S WORD

The forward-walk mech — walk until the oob line stalls, retest its peers, and if the picture is
unchanged place a signal on the next g5Mage and g15Mage same-side oob reversing. Joe 1006: *"leave
this mech-build to last. build everything else, then we'll carefully craft it so that it matches my
vision"*.
