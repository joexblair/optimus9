# octo-v4 — `v4saviour`

Started 2026-10-22. Split from `v4_spec.md` at Joe's word, 1022:
*"good analysis.  action the split"*. The board, the side rule, `rev-trade` and the knob bank
are in `v4_bank.md`; `v4-lineage` is in `v4_lineage.md`. His verbatim text is CARRIED here,
never retyped.

Joe's times carry no colons: `1305` is 13:05. His estimates are +/- 5 minutes.

---

## 1. The handover, verbatim

Joe 1022, verbatim, unedited:

```
mech: `v4saviour`
-if the first ws1r oob prints on the target-side AND that oob is the first excursion after a trade opened while ws5r was NOT oob 
--if ws1r crosses from oob to ib AND mage cascade prints a counter target-side verdict (ie target-side is high, cascade verdict:DOWN. target-side low, cascade UP)
---then end the trade, and open a reversal trade. (example 09-01 2125 ends the LONG and opens a SHORT) 
--else if if ws1r crosses to ib AND mage cascade DOES NOT prints a counter target-side verdict
---then walk to ws2r target-side oob, CAP: {knob:10, `V4_SAV_WS2_OOB_TEST`} minutes 
----if V4_SAV_WS2_OOB_TEST expires, no action needed - the open trade stays open, v4saviour is complete 
---if ws2r crosses to ib AND mage cascade prints a counter target-side verdict
----then end the trade, and open a reversal trade. 
---else the open trade stays open, v4saviour is complete  
EXAMPLES
-09-01 2059 and 2125 were both reversed because mage cascade qualified
-09-02 1215 and 1630 left the trade open because mage cascade failed to qualify
```

Joe 1022, added UNDER his line `---then walk to ws2r target-side oob, CAP: {knob:10,
`V4_SAV_WS2_OOB_TEST`} minutes`, unedited. His original handover block above is UNALTERED; this is
carried as its own block rather than spliced into his verbatim text:

```
---IF any ws1Mage bar lands outside of the past-50-gate (wob 8), route to the ws1r mage-cascade test.  mage-cascade test is anchored on the most recent target-side extrema
----EXAMPLE 09-01 2059, ws1r defers to ws2r. 2101 ws1Mage prints confirmed below 50. last target-side ws1Mage extrema at 2100. test mage-cascade anchored on 2100
```

So inside the branch-B walk, the ws1r test can be RE-ENTERED: if ws1Mage leaves the past-50 gate and
stays out for 8 bars, the ws1r cascade runs again - this time anchored on the most recent
target-side ws1Mage extrema, which is `jig.mage_cascade_bar(ws1Mage, stamp, target_side)` in mode
'extrema', his own 1017 producer. That anchor is NOT the lift-off anchor #25 ruled for the r-driven
reads; this route is Mage-driven and he named its anchor explicitly.

### The knob

| the knob | value | units | Joe's words |
|---|---|---|---|
| `V4_SAV_WS2_OOB_TEST` | 10 | minutes = 120 bars | *"CAP: {knob:10, `V4_SAV_WS2_OOB_TEST`} minutes"* |

This is the only cap in v4 and it is HIS. Nothing else in the mech is bounded.

### The mage cascade is already built and ruled

`optimus9/analysis/jig.py`, Joe 1017, every part his. NOT a v3 mech - it predates v3 and survives it.

| the producer | what it does |
|---|---|
| `mage_cascade_bar(line, bar, side, mode='extrema')` | picks the ONE bar. Coarse walk back in 4-min gaps to a same-side turn, then the line's true extreme FORWARD of it, ending at the event bar. Unbounded walk |
| `mage_cascade(mg, bar)` | the ladder ws1..ws12 read at that one bar -> `verdict` 'up', 'down' or 'neither'. The LOW cluster wins when both count. No dr in or out |

| the cascade knob | value | note |
|---|---|---|
| `MC_GAP` | 48 bars = 4 min | Joe's own number, 1017 |
| `MC_ZOOM` | 2 rungs | Joe 1017: *"keep it tight for now"* - still the provisional width he said he would tune |
| `MC_MIN` | 4 lines | *"4 or more consecutive TFs"* |
| `MC_TF_LO` / `MC_TF_HI` | 1 / 12 | wsf. A low cluster starts at ws1, a high cluster ends at ws12, middle clusters discarded |

### All four of Joe's examples match, measured

ws1r oob 15/85, the oob->ib cross unwobbed, `mage_cascade_bar` mode 'extrema' with side = the oob
side, window +/- 10 min around his time.

| his example | target-side implied | the ws1r oob run | the oob->ib cross | ws1r | the cascade verdict | counter to the target-side | his outcome | matches |
|---|---|---|---|---|---|---|---|---|
| 09-01 2059 | high | 20:56:00 .. 20:58:55 | 2026-09-01 20:59:00 | 81.44 | down | YES | reversed | YES, +0 s |
| 09-01 2125 | high | 21:24:20 .. 21:25:10 | 2026-09-01 21:25:15 | 81.86 | down | YES | reversed | YES, +15 s |
| 09-02 1215 | low | 12:14:10 .. 12:15:20 | 2026-09-02 12:15:25 | 20.73 | down | no - low needs up | left open | YES, +25 s |
| 09-02 1630 | low | 16:28:00 .. 16:30:40 | 2026-09-02 16:30:45 | 15.05 | down | no - low needs up | left open | YES, +45 s |

The target-side column is DERIVED from his outcomes, not given. 2125 he stated (*"ends the LONG"*);
the other three follow from which verdict would have had to be counter.

The cascade traces at those four crosses:

| his example | the cascade why |
|---|---|
| 09-01 2059 | down \| the low cluster ws1 to ws4, 4 lines, falling COUNTS \| the high cluster ws4 to ws12, 9 lines, falling COUNTS \| the end-to-end diff +54.27 |
| 09-01 2125 | down \| the low cluster ws1 to ws4, 4 lines, falling COUNTS \| the high cluster ws4 to ws12, 9 lines, falling COUNTS \| the end-to-end diff +60.14 |
| 09-02 1215 | down \| the low cluster ws1 to ws3, 3 lines, rising \| the high cluster ws2 to ws12, 11 lines, falling COUNTS \| the end-to-end diff +6.27 |
| 09-02 1630 | down \| the low cluster ws1 to ws5, 5 lines, falling COUNTS \| the high cluster ws10 to ws12, 3 lines, falling \| the end-to-end diff +8.40 |

09-02 1215 is the one to keep an eye on: its LOW cluster is rising at 3 lines, one short of `MC_MIN`
4, so the HIGH cluster's falling verdict wins and the trade stays open. At `MC_MIN` 3 the verdict
would invert to `up`, which IS counter to a low target-side, and that trade would reverse.

ws2r at the same four crosses, for the branch-B walk:

| his example | ws2r at the cross | ws2r already oob |
|---|---|---|
| 09-01 2059 | 51.57 | no |
| 09-01 2125 | 59.06 | no |
| 09-02 1215 | 32.69 | no |
| 09-02 1630 | 64.47 | no |

---

## 2. The contract, the skeleton

Joe 1022: *"the v4saviour class will consume this data from an external source, so (albeit in
reverse) we're building a SRP skeleton by testing"*. This records the interface the tests have
forced out so far, so the external source has a target to meet.

### What it consumes

| the input | type | who owns it | ruled |
|---|---|---|---|
| `open_bar` | a grid bar | the open mech, #17, held back | the bar the trade opened on |
| `target_side` | +1 high, -1 low | the TRADE, by Joe #4: LONG = high, SHORT = low | AN INPUT, NEVER A DERIVATION |
| `R` | {1: ws1r, 2: ws2r, 5: ws5r} | the line cache | the three lines the mech reads |
| `MG` | {tf: ws{tf}Mage} for 1..12 | the line cache | the cascade's ladder |

THE SIDE IS AN INPUT, NEVER A DERIVATION. Banked 1022 after I derived it instead of reading it:
Joe asked for *"a trade opens on the low side ws5r reversal near 09-06 2220"*, I ran "low-side
reversal" through rev-trade's polarity to LONG / target-side HIGH, and v4saviour returned SAVIOUR REV
off the wrong side. On his stated LOW side it returns NOT ARMED. `walk` does not compute the side
and must never be given a computed one.

### What it returns

| the verdict | when |
|---|---|
| `NOT ARMED` | ws5r was target-side oob at the open, so the arm cannot fire |
| `SAVIOUR REV` | a counter cascade at the ws1r ib cross (branch A) or the ws2r ib cross (branch B) |
| `STAYS OPEN` | no counter cascade, or the cap expired, or no ws1r oob run followed the open |

### Three things the testing cannot reach, and they are gaps

| # | the gap | why testing hides it |
|---|---|---|
| 40 | #32 "once per trade" has NO OWNER. `walk` holds no state - called twice on the same open it returns the same verdict twice. Whether the caller or v4saviour enforces once-per-trade is unspecified | a test calls it once |
| 41 | the input INVARIANTS are unstated. Must `target_side` be constant for the trade's life? May `open_bar` land in the warmup where the lines are NaN? May it land mid-excursion? | a hand-picked test supplies only valid inputs |
| 42 | BRANCH B HAS NEVER EXECUTED. No test has reached the ws2r walk or the `SAV_WS2_OOB_TEST` cap. The 09-06 2220 test stopped at the arm; the four 09-01 / 09-02 examples were measured by hand, not through `walk` | the chosen timestamps decide which paths run |

42 needs a test whose ws1r ib cross has a non-counter cascade, so the walk goes on to ws2r.

---

## 3. Its own rulings

| # | the rule | Joe's words |
|---|---|---|
| 21 | the first ws1r oob after the trade open | *"21, yes - this aligns with the examples"* |
| 22 | "excursion" is the ws1r oob run | *"22, oob"* |
| 23 | the oob->ib cross holds `SAV_IB_XWOB` 2 bars | *"23, 2"* |
| 24 | VOID - no side enters the cascade once the Mage-extrema walk is dropped | - |
| 25 | the cascade bar comes from where the r reversals print, not `mage_cascade_bar`'s extrema walk | *"25, not extrema - measure where the r reversals print"* |
| 25b | MOOT - the print is the usable event, so the bar is the lift-off STAMP | *"when i say "print" about anything, I'll always be refering to the usable event. this question is moot"* |
| 26 | `MC_ZOOM` 2 is a knob | *"26, 2 knob"* |
| 27 | the cap starts at the ws1r ib cross | *"27, ws1r ib cross"* |
| 28 | the cap includes the final ws2r ib cross | *"28, the cap includes the final ws2r ib cross"* |
| 29 | the ws2r cascade read is the same producer, side and mode | *"29, same same same"* |
| 30 | the reversal is a `rev-trade` | *"30, rev-trade"* |
| 31 | v4saviour has priority over v4-lineage | *"31, v4saviour priority"* |
| 32 | once per trade | *"32, once per trade"*, and *"40. accept the first open signal.  we'll build pyramid logic at a later time"* - the OWNER is the trade mech, not v4saviour |
| 33 | the first ws1r oob only, causal | *"33, first - everything we do is causal"* |
| - | THE ARM reads ws5r on the TARGET-side | *"ws5r is target-side oob"* |

### The arm, and how its side was settled

Joe's arm says only *"a trade opened while ws5r was NOT oob"*. The side was the one thing that
changed the verdict. On the 2026-09-06 22:21:50 open ws5r is 12.11 - LOW oob and NOT high oob:

| the read | ws5r oob? | v4saviour's return |
|---|---|---|
| ws5r's own side | YES | NOT ARMED |
| the target-side | depends on the trade's side | either |

Both were run and put to him rather than chosen. With his stated LOW target-side, ws5r IS
target-side oob and the verdict is **NOT ARMED**.

### Resolved by construction, not by a ruling

`lift_off`'s `side` is the target-side in v4saviour, because #21 fixes the ws1r oob to the
target-side. The two cannot differ, so it needs no ruling of its own.

---

## 4. The 09-06 2220 test

| the field | value |
|---|---|
| the ws5r low-side reversal | 2026-09-06 22:21:10 |
| its stamp, bar + `LIFT_WOB` - 1 | 2026-09-06 22:21:45 |
| the trade opens, stamp + 1 | 2026-09-06 22:21:50 |
| the target-side | LOW, Joe's stated side |
| ws5r at the open | 12.11 |
| ws5r target-side oob | YES |
| **v4saviour** | **NOT ARMED** |

ws5r never leaves low oob in the 13 bars around the open - 10.51 to 12.11 - so the arm cannot fire
on any bar near it.

---

## 5. To do

| # | the item | status |
|---|---|---|
| 42 | BRANCH B HAS NEVER EXECUTED. No test has reached the ws2r walk or the `SAV_WS2_OOB_TEST` cap. It needs a test whose ws1r ib cross gives a NON-counter cascade | Joe 1022: *"branch B is rare but real. it'll show up when it needs to"* |

Not a gate item and not a spec gap - a coverage fact about this mech's own code.

The gate is otherwise EMPTY. Every knob is banked and nothing in v4saviour is unruled.
