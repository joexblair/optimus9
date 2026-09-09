# The TF2-23 walk

**THE MECHANIC HAS NO NAME.** Joe has called it "the mech" and "the walk". Every filename and
heading here is a placeholder — rename on his word, do not coin one.

Joe 0909, given as six numbered steps. This doc records the steps, every concretion that had to be
settled to run them, who settled each one, and what is still open.

---

## 1. Joe's six steps, verbatim

> all times are eyeballed and estimated
> starting from 08-25 00:18
> setting dr from ws2Mage oob + ws13m oob
>
> 1. walk forward until ws1r is oob
>    -examples: 00:39, 01:35, 01:59, 03:28, 04:21, 05:09, 06:58
> 2. when ws1r enters oob, scan upwards through TF2-23, and tag the lines that have same dr momentum
>    -the lines must be clean (refer the latest definition of clean/dirty)
> 3. when a tagged line is oob and stalled/sideways, add a timestamped row
>    -locate the next 2 highest TF whose r is inside the fence
>    --print the TF and its r value in column `wk-tf-1` and column `wk-tf-2`, using this format "{TF}:{r value}"
> 4. scan for momentum, in reverse from TF23 to {the oob TF+1}
> 5. walk forward,
> 6. repeat 3,4,5 until the highest TF holding momentum reports an x cross m
>    -the x-cross-m must complete while Mage is closer to 50. eg post x-cross-m values are 0 and 1, and Mage is 12 for dr -1

Superseded by Joe 0909 later the same day: **dr uses ws1Mage, not ws2Mage.**

---

## 2. The rules as built, with provenance

| rule | value | source |
|---|---|---|
| start | 08-25 00:18 | Joe 0909 |
| window | the WALK is contained to 08-25 | Joe 0909, "contain the walk to 08-25" |
| warm-up | verdicts and the clean latch computed from 08-23 00:00 | mine — the latch and the 21-sample verdict need history before 00:18. Joe contained the walk, not the warm-up |
| dr source | ws1Mage AND ws13m | Joe 0909, "replace ws2Mage with ws1Mage" |
| dr rule | both oob on the SAME side; the previous dr holds until that happens | Joe 0909, "both oob, both same side. until that happens, the previous dr value holds" |
| fence | 83 / 17, from `MOMO_FENCE_R` = 17 | Joe 0909 |
| oob | the dr-side boundary — 85 at dr +1, 15 at dr -1 | standing convention |
| clean | a dirty line goes clean when its r is INSIDE the fence and its verdict advances to `momo` or `curl` | Joe 0909, "clean is applied when a dirty line's state advances to momo or curl" + "a dirty line must be inside the fence and converted to momo or curl" |
| clean/dirty instance | NOT the 0731 rpl/exhv2 producer | Joe 0909, "we're not using the rpl logic" |
| momentum-true | verdict `momo` or `curl` from `momo_g_why` at that bar's dr | established |
| stalled/sideways | verdict `sideways` | established |
| advance | the next row needs a HIGHER tagged TF oob + sideways | Joe 0909 |
| exit | the highest CLEAN momentum-true TF has its x cross its m, with Mage strictly closer to 50 than both x and m | Joe 0909, "yes" to clean-only |
| x-cross-m direction | dr -1 x crosses OVER m; dr +1 x crosses UNDER m | Joe 0909, "if dr -1, x crosses over" |
| restart | the walk restarts after the x-cross-m event; walks chain and do not overlap | Joe 0909, "the walk re-starts after the x-cross-m event" |
| xwob, x-cross-m | 12 bars = 60 s | Joe 0909, "increase the x cross m wob to 12" |
| xwob, everything else | 6 bars = 30 s | Joe 0909, "that xwob change was specific to x cross m only" |

### The Mage condition

Joe's example — "post x-cross-m values are 0 and 1, and Mage is 12 for dr -1" — was **withdrawn**
by him 0909 ("I accidentaly infered an inverted view of the logic because of my incorrect
(inverted) values for x and m"). The condition is built from his words, not the numbers:
`|Mage - 50| < |x - 50|` AND `|Mage - 50| < |m - 50|`, on the crossing line's own timeframe.

### The clean latch

Clean **latches**. This is MINE, not Joe's. Step 3 requires a tagged (clean) line to be **oob**;
tagging requires clean; clean requires **inside the fence**. A line cannot be inside the fence and
oob at the same instant, so a live state test makes step 3 unreachable. The latch is the only
reading under which step 3 fires at all.

No dirtying event was ever specified, so the latch is monotonic. **Measured consequence:** all 22
timeframes are clean at 00:18 and still clean at 08-26 00:00. Step 2's clean requirement and the
clean-only exit therefore include and exclude nothing in every run to date.

---

## 3. What is still MINE and unruled

| item | what I did | the alternative reading |
|---|---|---|
| **step 1 discretisation** | "walk forward until ws1r is oob" is a state. I take the rising edge of a 6-bar hold, one walk per edge | the first bar ws1r is beyond the boundary, no hold |
| **the clean latch** | latches, never resets | a live state test — which makes step 3 unreachable |
| **mid-walk dr flip** | nothing applied; the walk continues and each row carries the dr at its own bar | abort the walk, or re-tag |
| **strict vs inclusive oob** | ws1r's trigger uses `cross_wob`, which is strictly beyond the boundary. The tagged-line oob test in step 3 uses at-or-above | make them consistent either way |

Joe's eyeballed step-1 examples against the built construction, 08-25:

| Joe's estimate | built | note |
|---|---|---|
| 00:39 | 00:39:45 | walk 1 |
| 01:35 | 01:35:25 | walk 2 — appeared only after the ws1Mage dr change |
| 01:59 | none | nearest is walk 2's exit at 01:59:00 |
| 03:28 | 03:28:35 | walk 3 |
| 04:21 | 04:20:25 | walk 4 |
| 05:09 | 05:09:15 | walk 5 |
| 06:58 | 06:48:25 | walk 7 |

Both are measurements. The disagreement is open.

---

## 4. Lines the mechanic needs

`r`, `x`, `m`, `Mage` at every timeframe 2..23, plus `ws1r` and `ws1Mage`, plus `ws13m`.
The registry (`vw_indicator_configs_live`) carries TF1-10, 12, 15 and 22 only; the rest were built
by `build_wsf_role_lines.py` at the wsf role specs. 92 role lines are cached at the 09-08 key.

Momentum verdicts are cached per dr source — `st_0823_0826_<dr source>.npz`. **The dr source is
part of the key.** Verdicts are computed at each bar's dr, so a different dr rule is a different
verdict set; keying on the bar range alone silently reuses the wrong verdicts.

---

## 5. Results to date, 08-25, dr from ws1Mage + ws13m

| item | value |
|---|---|
| ws1r oob confirming edges | 47 |
| walks after chaining | 24 |
| exit events on 08-25 | 71 |
| rows | 8 |
| walks emitting 2 rows | 1 (walk 16) |
| dr flips on 08-25 | 31 |
| clean timeframes at 00:18 | 22 of 22 |

The eight rows:

| walk | row utc | dr | oob tf | r | sw bars | wk-tf-1 | wk-tf-2 | hi clean mom tf |
|---|---|---|---|---|---|---|---|---|
| 2 | 01:54:20 | -1 | 5 | 1.12 | 1 | 11:22.01 | 12:18.91 | 16 |
| 5 | 05:16:10 | +1 | 4 | 87.03 | 1 | 6:81.30 | 7:66.14 | 8 |
| 10 | 09:43:20 | +1 | 4 | 90.68 | 1 | 6:79.31 | 7:65.74 | 18 |
| 16 | 17:46:40 | +1 | 3 | 87.15 | 1 | 5:77.82 | 6:72.20 | 13 |
| 16 | 17:56:05 | +1 | 4 | 96.48 | 1 | 5:82.39 | 8:80.75 | 14 |
| 20 | 20:47:35 | -1 | 2 | 4.17 | 1 | 4:33.83 | 5:43.69 | 22 |
| 21 | 22:17:05 | +1 | 6 | 95.21 | 1 | 11:74.96 | 12:72.92 | 19 |
| 24 | 23:46:10 | -1 | 4 | 13.59 | 1 | 6:20.73 | 8:20.37 | 11 |

Every row has a sideways run of exactly 1 bar = 5 s.

**Joe 0909, on the first four rows:** *"the mech is starting to shape up - the first 4 rows are
exiting at good times"*. That is his read, and it stands.

**Joe 0909, on walk 5's exit at 05:28:40 tf 13:** *"the x-cross-m exit fires too early. it's not a
fault in the build - it is a new mechanism that I've been expecting to build"*. The mechanism does
not exist yet.

### Superseded configurations

Numbers from these are void, not context:

| configuration | walks | rows |
|---|---|---|
| dr ws2Mage, x-cross-m wob 2, overlapping walks | 47 | 4 |
| dr ws2Mage, x-cross-m wob 12, overlapping walks | 47 | 7 |
| dr ws2Mage, x-cross-m wob 12, chained walks | 23 | 4 |
| dr ws1Mage, x-cross-m wob 12, chained walks | 24 | 8 |

---

## 6. Open

1. Rule the step-1 discretisation. Every walk count and row count depends on it.
2. Name a dirtying event, or the clean test stays inert.
3. Rule what a mid-walk dr flip does. Walk 20 hit one.
4. Rule strict vs inclusive on the oob boundary tests.
5. The mechanic that walk 5's early exit calls for does not exist.
6. Name the mechanic.
