# wsf-dtf-v3 — tuning spec

Opened 0913 on Joe's word: *"keep these 2 timestamps as targets. add them to a wsf-dtf-v3 tuning
spec doc"*.

`docs/wsf_dtf_v3_spec.md` is the machine's spec. **This doc is the tuning record**: the bars Joe
has named as targets, his own walk-through of what the machine should do at each, and the rules he
has set while reading them. Nothing here is built unless a section says so.

---

## 0. WHERE THE TWO TARGETS CAME FROM

Walk 5 of the test-point walk (`walk_mom_models.py`, table `wsf_dtf_mom_models`, `wdm_walk=5`) ran
900 minutes and produced 90 test-points over 08-25 01:51 to 08-28 22:26.

| what happened at the test-point | test-points |
|---|---|
| ws2's r line already showed momentum under the settings in force | 40 |
| ws2's r line already past the dr-side edge of the 17/83 fence | 19 |
| ws3's r line used instead of ws2, already showed momentum | 7 |
| dropped by the sweep, later covered by a divergence on gcws30r | 12 |
| pooled, later covered by a divergence on gcws30r | 1 |
| ws2's r line never reached the 20/80 edge inside 35 minutes | 9 |
| **dropped by the sweep, and no divergence either** | **2** |

The 2 are the targets. Every other test-point already has a route.

14 full sweeps of all 2,580,480 knob combinations ran during walk 5. **Not one found a combination
that satisfies the whole accumulated set.** Joe 0913 closed the sweep on that basis: *"I don't
think we need to sweep"*.

**NOTHING IN WALK 5 HAS BEEN SCORED AGAINST PRICE.** No entry, no exit, no return was computed at
any test-point, in any of the five walks. Joe 0913, on his own reading of the result: *"fair call -
that's a view I'm holding with an internal (and biased) lookahead"*.

---

## 1. TARGET — 08-26 04:51:40, dr -1

Cycle 26 of walk 5. ws2's r line reads 46.10 at the test-point and reaches the 20/80 edge at
04:56:15. No combination of the 2,580,480 calls it momentum. gcws30r carries no divergence in any
of the 24 anchor bars after the test-point.

**Joe 0913, verbatim:**

> -option1, walk to ws1mage-rev, test for dr-flip, find flip so use ws1mage-rev to trade at 04:59:50
> -option2, walk to ws1mage-rev, test for dr-flip, find that dr has flipped, walked the wsf-dtf-v3
>  stall times, find no acceptable signal before the stalls, force exit on 06:20, find that ws1Mage
>  has just gone low oob, wait for next ws1mage-rev
> -if option 1 is taken, stop needs 0.7. exit at dr 1 ~05:35: weak-mage TF2 makes it a simple decision

**What the `ws1mage-rev` producer returns from that bar**, measured 0913 at its default knobs —
dwell 3 bars = 15 s, reversal wob 2 steps = 3 bars = 15 s, hold 4 bars = 20 s, boundaries 75/25:

| dr | leg | bar | ws1Mage |
|---|---|---|---|
| -1 | ws1Mage's oob run reaches dwell | 08-26 04:51:40 | 13.93 |
| -1 | ws1Mage reverses | 08-26 04:52:10 | 6.78 |
| -1 | gcws30Mage crosses back in bounds | 08-26 04:59:35 | — |
| -1 | that cross becomes knowable | **08-26 04:59:50** | — |
| +1 | ws1Mage's oob run reaches dwell | 08-26 05:26:45 | 75.87 |
| +1 | ws1Mage reverses | 08-26 05:27:00 | 85.50 |
| +1 | gcws30Mage crosses back in bounds | 08-26 05:28:35 | — |
| +1 | that cross becomes knowable | 08-26 05:28:50 | — |

Joe's 04:59:50 is the dr -1 knowable bar. The two agree.

---

## 2. TARGET — 08-27 20:53:10, dr -1

Cycle 59 of walk 5. ws2's r line reads 44.16 at the test-point and reaches the 20/80 edge at
21:22:00. No combination of the 2,580,480 calls it momentum. gcws30r carries no divergence in any
of the 24 anchor bars after the test-point. ws4 was rescued here by the digression, on the loosest
combination in the grid.

**Joe 0913, verbatim:**

> -option1, walk to ws1mage-rev, test for dr-flip, find no flip. without the flip = pxs is far from
>  a pivot, and that makes option1 a non-option
> -option2, hand over to dtf, walk the stall events until acceptable mask at 21:45 (only just: the
>  middle values are pushing the limits """14.6 (9)    30.1 (10)    27.1 (11)    33.4 (12)"""),
>  ws1mage-rev fired inside of the last 2 minutes, so we know we're entering the trade on the mfe
>  side

---

## 3. THE TWO OPTIONS, AS A SHAPE

Joe described the same two-option shape at both targets. Written out as he used it, not as a built
mechanic:

- **option 1** — walk to `ws1mage-rev`, test for a dr flip. A flip present means option 1 is live
  and the trade is taken at the `ws1mage-rev` knowable bar. No flip means pxs is far from a pivot,
  and option 1 is not available.
- **option 2** — hand over to dtf, walk the stall events, and wait for an acceptable mask. If no
  acceptable signal arrives before the stalls, force exit, then wait for the next `ws1mage-rev`.

**NOT BUILT.** No producer runs this shape today. The terms it rests on all exist as separate
mechanics — `ws1mage_rev` in the jig, `jig.stall_mask`, the mask sequence (gcws30 then ws1..ws18,
19 tags and 18 pairs), the weak-mage-tf scan over TF2 to TF12 — and none of them is wired into this
shape.

**OPEN, AND JOE'S TO SET.** Each of these is named in his walk-throughs and has no rule behind it
yet:

| # | open term | what is missing |
|---|---|---|
| T-1 | "test for dr-flip" | which flip, over what span from the `ws1mage-rev` bar |
| T-2 | "acceptable mask" | what makes a mask acceptable. His 21:45 reading calls it *"only just"* |
| T-3 | "no acceptable signal before the stalls" | which stall bar closes the window |
| T-4 | "force exit" | the rule that picks the exit bar. His 06:20 is a reading, not a derived bar |
| T-5 | "stop needs 0.7" | the units, and whether 0.7 is a knob or a one-off reading |
| T-6 | "entering the trade on the mfe side" | the test that establishes the mfe side at entry time |

---

## 4. DIVERGENCE'S PLACE IN THE MACHINE — Joe 0913

**Verbatim:**

> -if a test-point finds momentum on its own, divergence is not needed so the 2 minute delay is moot
> -if there is no momentum at the test-point, then the 2 minutes grace is accepted

**What this sets, in order:**

1. at the test-point, run the momentum verdict on the line under test.
2. momentum true -> the event is knowable at the test-point bar. The divergence never runs.
3. momentum false -> the divergence runs on gcws30r against pxs, anchored at each of the 24 bars
   after the test-point (120 s), and the line is momentum-true if any of them fires.
4. in that case the event is knowable at the divergence's firing bar, which is up to 120 s later
   than the test-point.

**The settled parts, from Joe 0913:**

| what | answer |
|---|---|
| price series | `__pxs__` from the tape cache — source `close`, DEMA length 2 |
| line the divergence reads | `gcws30r` — registered at 30 seconds, cached, 0..100 scale |
| does the divergence move or gate the test-point | neither |
| what a firing divergence does | marks the line momentum-true |
| the alignment test | redundant. The machine returns bearish only at dr +1 and bullish only at dr -1, so any verdict that fires already aligns. The rule is simply: divergence fires -> momentum-true |
| the anchor bar | each of the 24 bars AFTER the test-point; fires if any of them fires |

**NOT BUILT.** `walk_mom_models.py` passed the divergence a price series of all zeros, so it could
never fire; and it read the flat-run bar and never read the reversal bar. Both faults are recorded
in `docs/wsf_dtf_v3_spec.md` §13. The ordering above has not been written into any producer.

**MEASURED 0913 — the divergence on the 14 dropped test-points**, at AF_BLOCK 60 bars = 300 s look-back,
24 anchors = 120 s, machine boundary 50:

| cycle | test-point bar | dr | gcws30r at the test-point | divergence |
|---|---|---|---|---|
| 7 | 08-25 09:36:25 | +1 | 84.02 | bearish, 15 s later |
| 10 | 08-25 11:36:25 | +1 | 81.39 | bearish, 5 s later |
| 24 | 08-26 03:48:10 | -1 | 31.72 | bullish, 5 s later |
| 26 | 08-26 04:51:40 | -1 | 9.94 | **none** |
| 28 | 08-26 06:25:10 | -1 | 1.20 | bullish, 20 s later |
| 33 | 08-26 12:07:10 | +1 | 53.48 | bearish, 5 s later |
| 35 | 08-26 15:26:10 | +1 | 59.50 | bearish, 5 s later |
| 57 | 08-27 20:01:25 | -1 | 60.38 | bullish, 40 s later |
| 59 | 08-27 20:53:10 | -1 | 15.86 | **none** |
| 66 | 08-28 02:59:50 | +1 | 82.26 | bearish, 70 s later |
| 71 | 08-28 05:31:10 | +1 | 92.10 | bearish, 110 s later |
| 75 | 08-28 08:14:00 | -1 | 1.82 | bullish, 60 s later |
| 79 | 08-28 10:55:40 | +1 | 98.43 | bearish, 20 s later |
| 83 | 08-28 14:36:10 | +1 | 66.37 | bearish, 5 s later |

Plus the pooled test-point, cycle 90, 08-28 22:26:10, dr +1, gcws30r 67.97: bearish, 5 s later.

**Caveats, each stated once:**

- 3 of the 13 fired on a price move under 0.0001 — cycles 33, 79 and 7. The machine has no minimum
  price move; any non-zero move in the right direction counts.
- 5 of the 13 fired more than 15 s after the test-point. The furthest, cycle 71, fired at 110 s of
  the 120 s window.
- none of the 13 has been on Joe's pine.

---

## 5. OPEN

| # | item |
|---|---|
| O-1 | the two options at §3 are not built, and T-1 to T-6 have no rules |
| O-2 | the divergence ordering at §4 is not written into any producer |
| O-3 | no test-point in any of the five walks has been scored against price |
| O-4 | the 9 test-points where ws2's r line never reached the edge have no route at all |
