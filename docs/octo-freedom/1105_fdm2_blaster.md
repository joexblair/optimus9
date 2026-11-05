# fdm2-blaster — HIS NAME, 1105. The rulings, and why it is on hold

He named it on 1105: *"9: fdm2-blaster"*. It is the matryoshka + blast-radius reading of the board
at a cadence event. **NOTHING IS BUILT.** His closing line on 1105: *"how to model: this is on hold
- I need to improve the cadence event before we can accurately model"*.

## HIS RULINGS, 1105

| # | the question I asked | his ruling |
|---|---|---|
| 1 | which lines form the actionable cluster | *"this needs modelling, but for now: ws1-ws4"* |
| 2 | how many of that cluster must print | *"this depends on ws1 and ws2 ... it's not a simple n of 4"* |
| 3 | does "recently flipped" mean inside the flattening width | *"I don't know yet. let's contain it to the flattening width for now"* |
| 4 | what the high-TF cluster that resists does | *"nothing yet - modelling will answer the question"* |
| 5 | does the 4-of-5 blast-radius gate survive | **"no"** |
| 6 | does it fire at the cadence event only | *"no, it fires contiuously during the autocalled cad walk, using FDM_XCAD_WALK_MIN 10.0 min"* |
| 7 | which walk gets auto-called | answered by 6 - `FDM_XCAD_WALK_MIN` 10.0 min, not `FDM_X10_GRACE_MIN` 5.0 min |
| 8 | every cadence event, or only a no-candidate one | **"yes"** - every cadence event |
| 9 | the name | **fdm2-blaster** |

Earlier in the same message, two more:

| the ruling | his words |
|---|---|
| the trade-open marker is general | *"remove the ws{>25}r restriction. I see 'the use trade open as a marker mech' being available to any mech that needs to test between cadences"* |
| only ws1r..ws10r are sampled for flattening | `FDM2_MATR_LFTOF_CONF` 10, his knob name and his value |

## THE BLAST RADIUS, RESTATED AFTER HIS CORRECTION OF MY WORDING

My "downward pressure / upward pressure" read as a statement about who sends the pressure. It is
not. The tail always pushes UP the ladder; what changes is **how many rungs up the target sits**.

| the target | the cost |
|---|---|
| the rung directly above the tail | cheap. It follows - *"the line is the same line zoomed across all of the timeframes"* |
| a rung far above the tail | expensive. *"a lower TF tail can attempt to pull a much higher TF to it's will, but there is no gaurantee that the HTF line will follow"* |
| a cluster of high TFs printing one direction | *"will not bend, or very slowly bend, to the lower TF tail"* |

## WHY IT IS NOT n OF 4 — THE TAIL LOGIC

Every ws{n}r is the SAME line, binned at a different bar width, one config 7|5|8|close. So:

| the consequence | what it means for the count |
|---|---|
| ws4r's value contains ws1r's recent history, binned coarser | ws4r cannot turn unless the move that turned ws1r survived long enough to land in 4-minute bins |
| ws1r away with ws2r still towards says only that the finest bin has turned | ws1r away alone is a candidate, not a carry |
| so the cluster size is a DURATION reading in disguise | "4 of 4 away" says the turn survived into the 4-minute bins, which takes about 4x as long as surviving into the 1-minute bins |
| and that is why it depends on ws1 and ws2 | ws1r + ws2r away = the turn is alive NOW at the finest resolution. ws3r/ws4r away while ws1r/ws2r are towards = the coarse bins still hold an OLD turn and will unwind upward |

So the question becomes two readings, not one count:

    a) are ws1r and ws2r away at this bar
    b) the highest TF in an unbroken run from ws2 upward that is away, with each rung's
       turn stamped AFTER the rung below it

TWO PHRASES OF MINE, NOT HIS - "the live head" for (a) and "the carry" for (b) were my shorthand in
chat. They need his words before they go into any spec text.

## THE OUT-OF-ORDER STAMP IS NOT A PROBLEM — HIS 1105 RULING

At 2026-08-07 08:26:00, LOW side, the last stamp per line:

| the line | its last LOW lift-off stamp in [06:48:10, 08:26:00] |
|---|---|
| ws1r | 2026-08-07 08:24:30 |
| ws2r | 2026-08-07 08:12:30 |
| ws3r | 2026-08-07 08:25:55 |
| ws4r | 2026-08-07 08:24:35 |

I raised ws2r's stamp landing 12 minutes before ws1r's as a blocker and asked for every stamp per
line. HE RULED IT OUT: *"the 0812 print was a skinny blip that can be ignored.  it has no
consequence: ws2r will reprint `away` after it cycles through low exfence at ~0828, which is the
point of the cad walk"*.

- so NO blip test is built, and the all-stamps reading is not needed
- an out-of-order rung holds the carry short until that rung reprints
- fdm2-blaster re-reads at EVERY bar of the auto-called cad walk, `FDM_XCAD_WALK_MIN` 10.0 min, so
  the reprint is picked up where it happens

## THE PRODUCER — BUILT 1105

`optimus9/analysis/jig.fdm2_blaster(rows, bar, head_tfs=(1, 2), lo=2, hi=None)`.

| the field it returns | what it holds |
|---|---|
| `head` | {tf: 'away'\|'towards'} for ws1r and ws2r. No verdict - whether ws1r alone opens it is unsettled |
| `head_away` | how many of the two read away. A count, not a gate |
| `head_age` | {tf: bars from that tf's stamp to the bar} - the staleness reading his open value needs |
| `away_run` | the highest TF in an unbroken `away` run from ws2, ORDER IGNORED |
| `carry` | the same run with the order rule applied - each rung stamped at or after the rung below |
| `carry_tfs` | the rungs in that run |
| `broke_at` / `why` | the rung that ended the carry, and which rule ended it |
| `lags` | {tf: bars from the rung below's stamp} over the carry - the per-rung spacing a model fits |

- IT HOLDS NO THRESHOLD AND RETURNS NO VERDICT, which is what *"modelling will answer the
  question"* requires
- it touches no array. The caller hands in the `fdm2_cad_mom_detector` rows it already builds, so
  the cost in a per-bar walk is nil and the causality stays with the caller
- EQUAL STAMPS COUNT AS ORDERED. Two lines stamping on one 5 s bar is not evidence against the
  order, and `jig.r_matryoshka` already reads the coarse bend as following when it lands AT the
  fine bend's bar. That precedent is the reason, not a preference
- THE SCAN HAS NO TOP. `hi=None` scans the whole ladder handed in. He has named no top for the
  run and `FDM2_MATR_LFTOF_CONF` 10 caps the flattening sample capture, a different reading

## WHAT IS DROPPED

- the 4-of-5 blast-radius gate, his "no". No code, no knob, no spec text
- `fdm-blst-rad-conf-tfs` was never built, so nothing is removed from the tree
- my "chain's reach" - it measured ws1..ws28 at 08:26:00 and separated nothing

## OPEN — EVERYTHING ELSE IS SETTLED

| # | what is unbuilt |
|---|---|
| 1 | the flattening read itself. The four knobs hold his values; no code reads them yet |
| 2 | the auto-call of fdm2-blaster at every cadence event, inside the `FDM_XCAD_WALK_MIN` 10.0 min cad walk |
| 3 | modelling - ON HOLD, his *"I need to improve the cadence event before we can accurately model"* |

## THE FIRST RUN — 2026-08-07 08:26:00, AND THE CLIMB INSIDE THE CAD WALK

`/home/joe/.claude/jobs/7c82535c/tmp/blaster0826.py` -> `blaster0826.out`. One cadence event, n = 1.
The leg is the 06:48:10 SHORT, target side LOW, stopped 12:11:35 at -1.100 with the MAE 1.1 stop ON.

| at the cadence event 08:26:00 | value |
|---|---|
| ws1r | away, stamped 90 s before the bar |
| ws2r | away, stamped 810 s before the bar - the 08:12:30 blip he ruled ignorable |
| of ws1r and ws2r, away | 2 of 2 |
| the away run from ws2, order ignored | ws6 |
| the carry, order applied | ws3 |
| what ended the carry | ws4r stamped 16 bars = 80 s BEFORE ws3r |

**HIS PREDICTION IS ON THE TAPE.** His 1105 words: *"the lower lines are matryoshka, so ws7,8,9 are
(literally) bound to their lead"*. Inside the auto-called cad walk the away run climbs:

| the bar | the away run from ws2 |
|---|---|
| 2026-08-07 08:26:00 | ws6 |
| 2026-08-07 08:31:00 | ws7 |
| 2026-08-07 08:32:00 | ws8 |

- ws7r and ws8r read `towards` at the cadence event and were ex-20/80 LOW. The tail dragged them
  away 5 min and 6 min later, inside the 10.0 min walk
- so the auto-call is doing the job he gave it. The verdict the leg needed was available at
  08:31:00 or 08:32:00, not at 12:11:35

## THE ORDER RULE, STRUCK 1105 — the numbers that killed it

The carry never passes ws3 and it drops to ws2 for 2 min 35 s:

| the bar | the carry | what ended it |
|---|---|---|
| 2026-08-07 08:26:00 | ws3 | ws4r stamped 16 bars BEFORE ws3r |
| 2026-08-07 08:30:00 | ws2 | ws3r stamped 49 bars BEFORE ws2r |
| 2026-08-07 08:32:35 | ws3 | ws4r stamped 26 bars BEFORE ws3r |
| 2026-08-07 08:34:35 | ws3 | ws4r stamped 50 bars BEFORE ws3r |

- the cause: `fdm2_cad_mom_detector` returns the LAST stamp in the span, and a fine line re-stamps
  often. Each ws2r re-turn pushes ws2r's stamp past ws3r's, and the order rule then rejects ws3r
- **his own blip ruling says a fine line re-turning is normal and has no consequence.** The order
  rule as I built it turns every fine re-turn into a carry break, which is the opposite
- the away run, order ignored, tracks the climb correctly over the same 10 minutes
- HE STRUCK IT, 1105: *"if the towards and aways are telling us the truth, why is the aging
  important?"*. The away run alone is the reading, and it gave ws6 -> ws7 -> ws8 on this event.
  The three repair options I put up are void with it.

## HIS ~0828 CALL, MEASURED

| his words | what the tape says |
|---|---|
| *"ws2r will reprint `away` after it cycles through low exfence at ~0828"* | ws2r reads `away` at EVERY bar from 08:26:00 to 08:36:00. It never left away inside the walk, so there was no reprint to wait for |

## HIS 1105 SECOND ROUND OF RULINGS — APPLIED

| # | his words | what moved |
|---|---|---|
| the age test | *"if the towards and aways are telling us the truth, why is the aging important?"* / *"it shouldn't matter ... keep the data for reporting only"* | the order gate is GONE from `jig.fdm2_blaster`. `head_age` and `lags` are reported and gate nothing |
| the head | *"ws2 and ws1"* | `head_both` - BOTH must read away |
| the run's top | *"ws12"* | `FDM2_BLAST_SCAN_HI` 12. The knob name is mine, the value is his |
| the flattening sample set | `FDM2_MATR_LFTOF_CONF` 10, his knob name and value | ws1r..ws10r contribute samples |
| the flattening span | *"they should be in sync. let's use ws{knob:3,'FDM2_CAD_FLATIN_WIDTH}"* | `FDM2_CAD_FLATIN_WIDTH` 3. EVERY line reads ws3's lattice: gap 8 bars, span 40 bars = 200 s |
| the 4-of-5 gate in his spec | *"yes"* to striking it | the 4-of-5 block, its `fdm-blst-rad-conf-tfs` row and its reversal-origin row are deleted from `fdm_spec_VERBATIM.md` |
| the lazy-g spec | *"sunset this spec and drop the words"* | SUNSET banner on `1003_lazy_g_spec.md`, an entry in `docs/sunset_register.md`, and the "order is guaranteed by construction" sentence - MINE, not his - deleted from that doc AND from `docs/wsf_setup_model.md` 3.12 |
| the gap reading | *"agreed, but I'm not 100% sure how to make use of it. I know we can't apply a gap test to ws1"* | PARKED. `gap` stays reported. No gap test anywhere, and none on ws1r in particular |
| the three order anchors | *"I'm not sure what this means"* | the question is void - it only existed to repair the order gate, which is dropped |

## STILL HIS, 1105

| # | the value |
|---|---|
| 1 | SETTLED - the flattening tolerance is 40 s. `FDM2_CAD_FLATIN_TOL` 8 bars, label mine on his *"your call on the label"* |
| 2 | SETTLED - "the carry" is retired. The field is `away_run` / `away_tfs`. "the live head" stays his word |

## WHEN THE AWAY/TOWARDS MECH STOPS PRINTING `away` — HIS QUESTION 2, ANSWERED FROM THE CODE

`jig.fdm2_cad_mom_detector` reaches `towards` by exactly two routes:

| the route | the condition |
|---|---|
| no reversal | no lift-off stamp inside the span -> `towards`, and `rev` is None |
| gap 0 | the line's closed-prev value IS the span's own extremum on the side -> `gap` 0.0 -> `towards` |

- `gap` = `cp[bar]` minus `min(cp over the span)` on a LOW side, and the span INCLUDES the bar, so
  gap is never negative. There is no third route
- **so `towards` is not a drift reading. It is binary**: the line is sitting on a new span extreme,
  or it is not
- for the 06:48:10 SHORT the span starts at the trade's open, so ws1r prints `towards` only by
  taking out its lowest closed-prev value since 06:48:10

MEASURED, `/home/joe/.claude/jobs/7c82535c/tmp/ws1_towards.out` - ws1r's closed-prev staircase from
the cadence event to 09:00:00, all 33 steps:

| the reading | value |
|---|---|
| ws1r's state at all 33 steps | `away` |
| the span LOW extremum, unchanged the whole way | 1.2705, set before the cadence event |
| the lowest ws1r closed-prev in the range | 14.0152 at 2026-08-07 08:59:00 |
| its deepest fall inside the range | 78.4183 at 08:35:00 to 17.8829 at 08:42:00 |

- so a fast line that has left the leg's extremum reads `away` for the rest of the leg unless it
  takes that extremum out. HE ACCEPTED THAT AS CORRECT, 1105: *"good. I forgot the away was based
  on the target-side extremum"*

## CANCELLED 1105 — the ws1r exception and its rulings 1, 2 and 4

HIS WORDS: *"I forgot the away was based on the target-side extremum. that nulls my concerns about
ws1r, and cancels #1,#2,#4 rulings"* and, on the pending-verdict question, *"this is redundant now"*.
The exception, its three rulings and the options I put up for its trigger are GONE - no code, no
spec text, no explanation. What stays is the fact that caused the cancellation, above: `towards`
means the line is sitting ON the span's extremum.
