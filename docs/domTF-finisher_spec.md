# domTF-finisher spec

Joe's finisher notes, verbatim, plus my notes on the mechanisms they describe.
Companion to the domTF-climb state machine. Joe 0811-0812.

---

## the two mechanics

    domTF-climb   the momentum layer. TF8..33 r lines. Holds the finishers off while a
                  higher timeframe is still carrying the move.
    finishers     the trade layer. gcws30 is the lynchpin; ws1..ws6 confluence it.
                  Places and closes positions.

-they are mutually exclusive. exactly one is active
-**finisher events and decisions can only take place on a gcws30 signal** (Joe 0812)

---

## Joe's note 1 — the 06:40 -> 08:02 walk, verbatim

    -when FREE is signalled, the domTF-climb mechanic will stop and the finisher mechanic will start

    -domTF-climb will start when finisher has entered the handoff-trade, followed by the first
     finisher trade signal. eg 08:02

    -the walk from 06:40 to 08:02
    06:40 ws6r has -1 momo
    07:00 ws6r has crossed low boundary
    07:00 ws1r is high and s1Mage/s1b are IB
    07:09 gcws30r is ~holding the same value as gcws30r @07:03. this indicates that -1 momentum
          is still present
    07:19 ws1b and ws1Mage are low oob, ws1r is almost low OOB. gcws30r, ws2r and ws3r are all
          printing "higher than their last excursion", which indicates market weakness. r lines
          representing market weakness is the foundation that the finisher mechanic is built on
    07:19 a trade is placed based on the positioning of the finishers r lines, when compared
          between the ws1 markers.
    07:19 to ~08:01: the same logic is applied across the finisher TFs. at ~08:02, gcws30
          creates a signal
    --if domTF-climb has a line in momo or curl state, then domtf-climb is active again, and the
      finishers handover to domTF-climb
    --if domTF-climb does not have a candidate to handoff too, then a reversing trade is placed
      by the finishers

## Joe's note 2 — the 09:00:05 -> ~10:57 walk, verbatim

    at 09:00:05, the finishers are indicating a bearish move, so the trade that began at 07:19 is
    closed and new short postion is created

    (estimations only)
    09:36 - ws6r is curling and gcws30b is signalling. the r lines have lifted, indicating weakness
    09:36:05 - a long trade is placed
    10:18 - ws6r has stalled. there are no dr-aligned domTF states, so no handoff
    10:18:05 the LONG position is closed, the SHORT trade is created
    10:39 - the SHORT position is closed, the LONG is created
    10:53 - gcws30 signals. we find that gcws30r and ws1r are weak. ws3r has momentum so we walk
            forward
    10:57 - ws3r crossed under by ws3x/m/b. this cancels ws3r's momentum and generates a trade signal
    10:57 domTF-climb takes over

---

## my notes on the mechanisms Joe describes

### M1 — weakness is a RELATIVE r-line read, not a level

-Joe 0811: "gcws30r, ws2r and ws3r are all printing 'higher than their last excursion', which
 indicates market weakness. r lines representing market weakness is the foundation that the
 finisher mechanic is built on"
-so weakness is measured against the line's OWN prior excursion, not against a fixed boundary
-verified 0812 at 07:19: gcws30r 50.18 vs a 0.00 low at 06:29:30; ws2r 35.34 vs 7.66 at 06:37:40;
 ws3r 47.63 vs 2.91 at 06:42:20. all three well above. MATCH
-UNSPECIFIED: the lookback that defines "last excursion". I measured from 06:00 because that is
 where I started the trace, which is a window I chose

### M2 — the finishers read POSITION BETWEEN ws1 MARKERS

-Joe 0811: "a trade is placed based on the positioning of the finishers r lines, when compared
 between the ws1 markers"
-so the comparison frame is marker-to-marker, not bar-to-bar
-ws1 markers are markers only. Joe 0811: "ws1 markers don't exist to gate trades"

### M3 — the finisher TFs cascade

-Joe 0811: "the gcws30r to ws6r lines are using momentum as a cascade to complete the trade"
-Joe 0811: "07:19 to ~08:01: the same logic is applied across the finisher TFs"
-the finisher lines are gcws30, ws1, ws2, ws3, ws4, ws5, ws6 — ascending TF
-the same weakness/momentum read is applied at each, in TF order

### M4 — a finisher line's momentum is CANCELLED by its own x/m/b crossing BACK TOWARDS 50

-Joe 0812: "10:57 - ws3r crossed under by ws3x/m/b. this cancels ws3r's momentum and generates a
 trade signal"
-Joe 0812, the final blow: "**ws3x/m/b crossing back towards 50**"
-so the cancel is NOT merely x/m/b sitting below r. It is the bands REVERSING toward the midline.
 Direction is the test; relative position to r is not sufficient on its own
-this is the finisher-side analogue of the domTF stall
-the 10:58:00 bar is consistent on all three lines, one 1-min step:

    ws3x  102.79 -> 79.80    -22.99
    ws3m   96.42 -> 84.08    -12.34
    ws3b   86.31 -> 82.99     -3.32
    ws3r   76.27 -> 88.77    +12.50   (r rising while all three bands fall towards 50)

-ONE BAR OF EVIDENCE. Not measured as a rule. The "towards 50" test needs a lookback and a
 threshold, neither of which is specified
-UNSPECIFIED: whether all three of x/m/b must turn, or any one

### M5 — every finisher decision is gated to a gcws30 signal

-Joe 0812: "finisher events and decisions can only take place on a gcws30 signal"
-so the finisher clock is the gcws30 signal series, not the 5 s bar
-a condition that becomes true between signals waits for the next signal
-this is why Joe's timestamps land on signals and his action timestamps land 5 s later

**LOCKED 0813 — the g30_marker.**

-Joe 0813, the definition, verbatim: "g30 marker signal - confirmed b crossing from oob to ib,
 with an xwob"
-Joe 0813 named it: **`g30_marker`**
-so: a gcws30b OOB->IB crossing held IB for XWOB 2 bars. **NO OOBW dwell filter. NO ws1 gate.**
-Joe 0813 on what it is for: "for right now, it provides a clock for g15 and g30 activities. it is
 not a replacement for ws1 or any other mech"
-Joe 0813: "unless there is a g30 marker signal, ws_fin_9of12 cannot fire"
-Joe 0813 on why no expiry knob is needed: "this is the reason for the mandatory g30b vote. it
 organically gaurantees a g30 marker signal". gcws30b votes ONLY while OOB and unlatch#2 is its
 return to IB, so the latch waits on the mandatory voter's own return and cannot hang. The side
 matches for free: candidates() stamps the side from the last OOB bar, which is the side g30b
 voted on. A gcws15b requirement would guarantee a g15b return, NOT a g30_marker.
-Joe 0813, a second qualification before the crossing: option a — the NEWEST replaces the armed
 one; `wsf_absorbed` counts how many folded in.
-in ws_strat terms this is `candidates()` output, before `walk()`'s oobw gate and before `gate()`.
 08-04 00:00 -> 12:22: 166 of these, against 68 that clear OOBW 16 and 41 the ws1 gate releases.

**THE DUAL LATCH — Joe 0813, verbatim**

    treat the 2 signals as a dual latch.
    unlatch#1: 9 of 12 lines
    unlatch#2: same-side g30b crossing to ib

-**9of12 must always carry a g30b vote** (Joe 0813: "for this to work reliably, 9of12 must always
 carry a g30b vote"). A bar with 9 voters that does NOT include gcws30b is not a qualification.
-**same-side**: the crossing's side must equal the qualification's side.
-THE ORDER IS SELF-ENFORCING. gcws30b can only vote while it is OOB, and the crossing is the move
 to IB, so the two can never share a bar and unlatch#1 always precedes unlatch#2. This is why the
 g30b vote requirement is what makes the mechanic reliable.
-the event's timestamp is the crossing's confirmation bar — the first bar both latches are open.

### M6b — handoff tolerance after a finisher trade signal

-Joe 0812: "a {knob:17 x 1min bars} tolerance must be given to a handoff which lands just after a
 finisher trade signal"
-`handoff_tolerance` = 17 x 1 min = **17 min** = 204 bars at the 5 s grid
-worked case, Joe 0812: "11:05:30 is an immediate fire - the finishers created a signal at ~10:53,
 when ws1 and gcws30 both signalled with a weak r while ws2r was stalled"
--gcws30 signal conf 10:53:35 -> handoff 11:05:30 = 11.9 min. Inside 17, so the handoff is
  attributed to that signal rather than treated as a separate event
-MY READING, not stated: the tolerance is ONE-SIDED — the handoff must land AFTER the signal.
-UNSPECIFIED: what the attribution changes downstream. Joe called it "an immediate fire", which I
 read as: the handoff belongs to that signal's trade, not as a new decision point.

### M7 — direction comes from the OOB side, and lives in `dr`

-Joe 0812: "its 100% obvious that a LONG trade will launch from a lo oob, and inverse for SHORT.
 if you want to rely on +1 and -1, you'll find it in `dr`."

    9+ of 12 lines OOB-LOW   -> LONG
    9+ of 12 lines OOB-HIGH  -> SHORT

-ws_fin_9of12 emits hi_fire / lo_fire, which are boundary counts. It carries no direction.
-`dr` is the signed field already on the markers (wsw_side) and the momentum tags (ml_dr).
-I had labelled hi_fire as +1 and treated +1 as LONG in the 08-04 ledger. That is inverted against
 this rule: every ledger figure produced before 0812 under "+1 = LONG" has the wrong sign.


### M8 — the bar counters count GRID bars, not trade bars. SETTLED, leave as is

-Joe 0813: "it tells me that we might not be using event bars" -> measured, then Joe 0813:
 "the honest answer: we leave it as is. if we count only the event bars, then we extend the delay -
 the cost is high"

-THE LINES ARE ALREADY EVENT-DRIVEN. 08-04, 17,281 bars on the 5 s grid, 11,150 with a trade and
 6,131 without. ws14r, ws14x and ws27r each changed value on a no-trade bar ZERO times all day.
-THE COUNTERS ARE NOT. Every one counts positions on the 5 s grid:
     4 bars   the fast-partner hold in the domTF handover
     4 bars   WSF_WS1_XWOB, on ws1Mage and ws1b
     2 bars   XWOB, marking the gcws30b crossing back inside
    12 bars   MIN_IB_DWELL, the IB run that resets the oob dwell
    16 bars   OOBW, the oob dwell a gcws30 crossing must clear
-CONSEQUENCE, accepted: a hold can be satisfied by one reading plus copies of itself. One ws14r
 value survives 4 bars or longer 710 times in the day, and once for 288 bars (24 minutes). At the
 17:58:15 handover the 4-bar hold contained 2 readings, at 17:58:00 and 17:58:15.
-WHY IT STANDS: counting trade bars only would push every confirmation later. Joe's call, on cost.


### M9 — the handoff is often NOT the seam for a trade signal

-Joe 0814, verbatim: "the handoffs between domTF and finisher are often not the seam for a trade
 signal. ie, if domTF hands off to the finisher, and the finisher can see same-side momentum inside
 of its own universe, then the trade signal will be delayed until that finisher momentum has played
 out"

-so a handoff time is NOT a trade time. The finisher takes over and then runs its own momentum test
 across its own lines before it will signal.
-CONSEQUENCE for measurement: scoring a handoff against price from the handoff bar measures the
 wrong instant. Joe 0814 gave this as the reason not to run the 0.9% leg measure over the 105
 signals yet.
-the finisher's own momentum test is not built. Its window, step and slope floor are unset — see
 task #6, second half.


### M10 — the momentum fit uses a FIXED SAMPLE COUNT, not a fixed gap. Banked 0814

-Joe 0810 made the momentum window dynamic: "it should be dynamic. use this value: {knob:4} x
 {TF width}". The gap between sample points stayed at RPL's 5 minutes, so the SAMPLE COUNT grew with
 the timeframe: 10 points on ws13r, 21 on ws27r.
-Joe 0814: "why are the samples increasing with the TF? this skews the sampling results between the
 lines" -> then "should it be 21 samples per line?" -> then "bank the spec and code".

**WHY IT WAS A BIAS, measured 08-04, domTF range 13..27**

how fast each line actually moves, r units per minute, median over 5-minute steps:

    ws13r 0.430  ws14r 0.421  ws15r 0.380  ws16r 0.366  ws17r 0.363
    ws18r 0.288  ws19r 0.280  ws20r 0.253  ws21r 0.241  ws22r 0.261
    ws23r 0.255  ws24r 0.230  ws25r 0.221  ws26r 0.161  ws27r 0.159

-the shortest line runs 2.71x the longest, and the decline is smooth apart from two steps:
 ws17r -> ws18r drops 21%, ws25r -> ws26r drops 27%. See task #10.
-MOMO_SLOPE_MIN 1.0 is denominated PER SAMPLE. With one fixed 5-minute gap it demands the same
 0.200 r per minute of every line — 2.15x what ws13r normally does, 0.80x what ws27r does.
-fixing the count instead makes the gap scale with the window, so the demand tracks the line. The
 spread of demand-over-normal-speed falls from 0.80-2.15 to 0.84-1.23.
-redundancy does not rise on the short lines: at 21 samples repeats run 17% to 28% with no trend by
 timeframe, and the LONGEST lines carry the most.

**WHAT IT COSTS, all 105 domTF signals on 08-04**

    domTF frees the finishers   52 -> 54
    domTF holds them            53 -> 51
    verdicts changed             4 of 105
    median hold               21.8 -> 19.2 minutes

-the 4 that change are 09:19:05, 13:02:20 and 14:44:30 held -> free, and 21:49:25 free -> held. In
 each, exactly ONE line crosses or falls below the momentum floor.
-11 more rows keep their verdict but change which line is the longest one carrying the move.
-IT DOES NOT MOVE JOE'S THREE LABELLED BARS. 07:21:50, 11:53:00 and 17:14:35 are all still free.

**WHERE IT LIVES**

    momo_gated.MOMO_FIXED_SAMPLES = 0     DEFAULT OFF. 0 keeps the old behaviour everywhere.
    build_ws_fin sets it to 21            the domTF walk only.

-DEFAULT IS OFF BY MY DECISION, not Joe's: momo_window is shared with build_momo_landed,
 build_handoff, build_ws_momo, s46_momo, build_s46_event, sweep_s46_momo and jig. Only the domTF
 walk has been measured. Say the word to make it global.
-STILL UNTUNED: the straight-line fit floor 0.50 and the curved fit floor 0.40 were set against a
 12-point fit and are now applied to a 21-point one. Task #1.

### M11 — the HTF-curl restriction is a BOLT-ON to the domTF handover. Banked 0814

Joe 0814: *"IF a domTF HTF has recently {knob:2 TF bars} curled towards dr, then the handoff
(cross OR stall) needs to be created by the HTFs[22:27] -- if we let the smaller domTFs create the
exit, it will be premature - the HTF curl says renewed high-level momentum."*

Joe 0814: *"this mech isn't a replacement to the existing (and mostly functional) domTF mechanic -
it's a bolt on."*

THE HANDOVER RACE. The candidates are the BLOCKING lines — the lines whose momentum verdict at the
signal bar is `momo` or `curl` in the signal's direction. A line that is not blocking has nothing
to hand over. First past the post wins, on either test:

- **cross** — the fast partner has crossed to the far side of the r line and held `HANDOVER_XWOB`
  4 grid bars = 20 s, AND the r line is back between the boundaries (15 and 85).
- **stall** — `STALL_N` 6 consecutive lattice samples with no new extreme in the signal's
  direction. No boundary condition; a stalled line has stopped moving wherever it sits.

THE STALL EXISTS TO CATCH WHAT THE CROSS MISSES. Joe 0814: *"your logic is sound, and for the most
part the two will ~coincide. the reason for having stall, is to catch the moments that a x cross
misses, eg TF25, 08-01 ~12:55."* The two tests are not redundant and the stall is not a backup —
it covers the turns where the fast partner never crosses.

WHEN THE RESTRICTION ENGAGES. A line between 22 and 27 must have bent into the signal's direction
within `CURL_RECENCY_TF_BARS` 2 bars of that line's own timeframe (44 min on ws22r, 54 on ws27r),
AND at least one BLOCKING line must sit between 22 and 27. Then the race is cut to the blocking
lines in 22-27 only.

WHEN IT DOES NOT ENGAGE. No blocking line between 22 and 27 means the restriction has no runners
and DOES NOT QUALIFY. The plain race runs on all the blocking lines. Joe 0814: *"you weren't
'falling back'; you were simply not engaging the new spec because it didn't qualify (ie no HTF
lines)."* This is not a fallback, a default, or a degraded path — the bolt-on is simply absent.

MEASURED 08-04, full day, 105 signals, 51 blocked. The HTF-curl restriction, at `STALL_N` 3:

| | |
|---|---|
| restriction offered (a 22-27 line bent in) | 31 of 51 |
| restriction engaged and moved the handover later | 14 of 31 |
| offered but did not qualify — no blocking line in 22-27 | rows 75, 76, 77 |

THE `STALL_N` 3 -> 6 A/B. Both walks are banked in `ws_fin_9of12`, told apart by `wsf_stall_n`:

| `STALL_N` | signals | blocked | handover | won by cross | won by stall | median wait | mean | max | inside 3 grid bars |
|---|---|---|---|---|---|---|---|---|---|
| 3 | 105 | 51 | 51 | 3 | 48 | 0.33 min | 2.72 | 18.7 | 25 |
| 6 | 105 | 51 | 51 | 40 | 11 | 19.25 min | 23.61 | 77.9 | 4 |

The two tests swapped places. At 6 the stall is the minority test, which is what Joe's reason for
having it requires.

JOE'S READ ON THE FOUR REMAINING NEXT-BAR STALLS. At `STALL_N` 6, four rows still hand over on the
next bar: 06:48:00, 06:50:25, 06:52:10 (all ws14r) and 18:57:35 (ws15r). Joe 0814 read all four on
the chart — *"these are exactly correct - price went semi sideways for a few minutes after a solid
sell-off"*, and on 18:57:35 *"also correct, for a similar reason"*. Verdict `pass`, banked in
`eyes_on_pine` sequence 8, rows 361-364. These were the only evidence that `STALL_N` 6 is still
loose; the read removes it.

THE FOUR LONGEST HOLDS, all won by cross, all unread on the chart:

| row | g30_marker | handover | wait |
|---|---|---|---|
| 17 | 05:01:50 | 06:19:45 ws23r cross | 77.9 min |
| 18 | 05:04:35 | 06:18:35 ws22r cross | 74.0 min |
| 98 | 22:10:10 | 23:13:30 ws25r cross | 63.3 min |
| 97 | 22:06:10 | 23:06:15 ws18r cross | 60.1 min |

THE TABLE'S IDENTITY. `ws_fin_9of12`'s unique key gained `wsf_stall_n`, `wsf_ho_xwob`,
`wsf_curl_tfbars` and `wsf_htf_band` on 0814, so two walks at different handover knobs sit side by
side instead of overwriting each other. Any query that counts rows MUST filter on them — without
that filter the counts sum every walk in the table.

`STALL_N` 3 -> 6, Joe 0814. At 3 the stall was looser than the cross on every one of the 15
lines and won 48 of 51 handovers:

| test | base rate, 08-04 full day |
|---|---|
| stall, `STALL_N` 3 | 49.4% - 57.5% of bars |
| stall, `STALL_N` 6 | 33.7% - 46.5% of bars |
| cross, `HANDOVER_XWOB` 4 grid bars = 20 s | 33.6% - 47.8% of bars |

At 6 the two are level, so the race turns on which fires first rather than on which is looser.
The wait grows from 7.8-16.2 min to 15.5-32.5 min, depending on the line.

THE BASE RATE CURVE HAS NO KNEE. Measured n = 1 to 19 on all 15 lines in both directions: a smooth
slide from ~65% to ~6%. No value of n is picked out by the shape of the data, which is why the
cross's availability was used as the anchor. n = 20 is unreachable by construction — it would need
the oldest of the 21 samples to be the extreme of the whole window.

### M6 — position flow

-observed in Joe's two notes: the finishers are always in a position while active. A decision
 closes the current one and opens the opposite
-09:00:05 close long / open short; 09:36:05 open long; 10:18:05 close long / open short;
 10:39 close short / open long
-the reversing trade Joe named earlier is this same flip, taken when domTF-climb has no candidate

---

## open concretions

| # | unspecified | who decides |
|---|---|---|
| 1 | the lookback that defines "last excursion" for M1 | Joe |
| 2 | whether M4 needs all of x/m/b or any one | Joe |
| 3 | how the finishers reach a decision from the r-line positions — the confluence rule itself | Joe, "currently in architecture phase" |
| 4 | what "weak" means numerically for gcws30r / ws1r at 10:53 | Joe |
| 5 | what the M6b attribution changes downstream — Joe called 11:05:30 "an immediate fire" | Joe |
| 6 | whether the near-band dominance walk or the domTF-climb state machine is authoritative for FREE. They disagree at 10:57 | Joe |

---

## settled domTF-climb configuration, for reference

| | |
|---|---|
| activation | MANUAL while the spec is built |
| seed | all dr-aligned momo\|curl lines; **D = the highest** |
| turn ends | **stall** (`STALL_N` 3) **or D in `curl` on its own dr** |
| ratchet | on a signal, search the FULL TF range above D for momo\|curl; **take the highest**; loop |
| FREE | no higher TF in momo\|curl -> all domTF activity stops, set NULLed |
| fence exit | **disabled** as a turn-ender (Joe 0812) |
| ws1 markers | refresh tags only while the climb is running |

-worked case: activate 08:02:50 dr +1, D=ws20r -> ws22r 08:15:00 -> ws25r 08:25:00 -> ws31r
 09:00:00 -> FREE 09:00:05. 57.2 min, 3 ratchet steps, every step triggered by the stall

---

## what is banked

| | |
|---|---|
| `build_ws_fin.py` | the walk. Writes all three tables and creates the view |
| `ws_fin_9of12` | one row per signal, 63 stamped columns. Every line's value and its vote |
| `ws_fin_walk` | one row per event. Multiple walks stack here, separated by the 15-column unique key |
| `ws_fin_tagshrink` | one row per line that left a tagged group |
| `v_ws_fin_walk` | **the report.** The latest walk only, picked by `wfw_pk`, one row per event, rendered — wait in minutes, `max_TF` as `ws{TF}r`, `-` on the FREE rows. This is what Joe reads |
| `build_ws_fin_pine.py` → `ws_fin_walk.pine` | the chart. 121 bars, 62 labels, three lines each: the signal bar with its bias, what it held until, and the cross that ended it |
| `eyes_on_pine` | Joe's chart reads. Appended, never overwritten |

The 08-04 window as it stands: **121 signals**, 57 high side and 64 low, **BLOCKED 62 / FREE 59**.

Every knob that changes a row is BOTH a column and part of the unique key, and `_wsf_key()` is the
single definition of that key — the DELETE before a rebuild and every summary read the same one.
Two copies is how a summary came to report 542 rows from 121 signals.

---

## KNOBS — every value the domTF walk reads

Banked 0818 on Joe's ask: *"depply scan the transcript for knobs. ensure all knobs are in the spec
docs"*. Grouped by the file the value lives in. A knob listed here is one that changes the rows the
walk writes.

### the wsf9of12 gate — `optimus9/analysis/jig.py`

| knob | value | what it does |
|---|---|---|
| `WSF_N` | **9** | votes needed, of the 12 lines |
| `WSF_HANDICAP` | **0** | points the six gcws b/m/Mage lines get off the boundary. 0 = they vote at 85 / 15 like everything else. Was 7, then 9 for one run — that run was a shotgun and was reverted |
| `WSF_LINE_HANDICAP` | **{'ws1b': 1}** | per-line override of the above. ws1b votes at 84 / 16. It is the one line `WSF_HANDICAP` cannot reach |
| `WSF_WS1_XWOB` | **1** | consecutive bars ws1Mage / ws1b must hold past their boundary before voting. 1 = a single bar votes. Was 4 (20 s) |
| `WSF_LINE_XWOB` | **{'ws1Mage': 1, 'ws1b': 1}** | the two lines the hold above applies to. The other ten have no hold |
| `WSF_VOTE_HOLD` | **0 (off)** | would hold every line's vote for N bars |
| `WSF_VOTE_STICKY` | **0 (off)** | would carry a vote across a gap shorter than N bars |
| `WSF_REQUIRE` | **('gcws30b',)** | a bar that reaches 9 votes without gcws30b among them is not a qualification |

### the domTF walk — `build_ws_fin.py`

| knob | value | what it does |
|---|---|---|
| `START` / `END` | **08-04 00:00 → 08-05 00:00 UTC** | the window. It is the first column of both unique keys, so two windows never overwrite each other |
| `G30_LEVEL` | **'g30_marker'** | which gcws30 event list arms the walk. XWOB only — no dwell gate, no ws1 gate |
| `XWOB` | **2** | consecutive bars gcws30b must hold past the boundary for a marker to count |
| `FENCE_OVERRIDE` | **None** | None = use `optimus9_system`'s 85 / 15. A number here replaces both sides. 80 / 20 was measured once: 279 → 300 markers, 133 signals |
| `DOMTF_MIN` / `DOMTF_MAX` | **13 / 27** | the timeframe ladder the walk may climb. Was 8 at the low end |
| `HANDOVER_RULE` | **'median'** | 'median' = the tagged group's middle line takes the handover. 'first' = first past the post, the older race |
| `STALL_N` | **6** | samples with no new extreme before a stall fires. Anchored to the cross test's base rate, not to a knee |
| `HANDOVER_XWOB` | **4** | bars the fast partner must hold on the far side of its r line for the cross to count |
| `DOMTF_HTF_BAND` | **(22, 27)** | the high band that may take a handover when the high timeframe is curled |
| `CURL_RECENCY_TF_BARS` | **2** | how recent that curl must be, counted in bars of the line's own timeframe |
| `RESCUE_REJECTED_CURL` | **True** | a curl the gate rejected is still allowed back into the pool |
| `NESTED_OPPOSITION` | **True** | on |
| `NESTED_OPPOSITION_MIN` | **3** | how many nested lines must oppose before the opposition counts |
| `K_WINDOW` | **4** | each line's momentum window = 4 × its own timeframe, in minutes. From `build_momo_landed.py` |
| `TFS` | **8 to 33** | the full ladder the r lines are built on. `DOMTF_TFS` is the 13-27 slice of it |
| `R_SPEC` | **k_len 7, rsi 5, stc 8, close** | how every ws{tf}r line is built |

### the momentum verdict — `optimus9/compute/momo_core.py` and `momo_gated.py`

| knob | value | what it does |
|---|---|---|
| `MOMO_FIXED_SAMPLES` | **21** | set by `build_ws_fin.py` at import; the module default is 0. Every line's fit uses 21 points across its own window, so the gap between points scales with the timeframe |
| `MOMO_WINDOW_MIN` | **60** | the window, minutes. Was 45 |
| `MOMO_STEP_MIN` | **5** | gap between points when `MOMO_FIXED_SAMPLES` is 0 |
| `MOMO_SAMPLES` | **12** | 60 / 5, the point count that follows from the two above |
| `MOMO_R2_MIN` | **0.50** | how straight the line must be to read as a straight line |
| `MOMO_SLOPE_MIN` | **1.0** | slope floor, r-units per 5-minute point |
| `LEVEL_SLACK` | **13.9** | how far past the boundary the level gate slackens, scaled by the fit |
| `CURL_ARC_MIN` | **4.0** | how much bend a curl needs |
| `CURL_VTX_LO` / `CURL_VTX_HI` | **0.05 / 0.95** | where the bend's turning point must sit inside the window |
| `CURL_R2_MIN` | **0.40** | the bend's own fit floor |

**Open, and it is task #1:** `MOMO_R2_MIN`, `MOMO_SLOPE_MIN` and `LEVEL_SLACK` were set against a
12-point fit. The domTF walk now runs them against a 21-point fit. They have not been re-derived.
Joe delayed this once already.

`CURL_ARC_MIN` and `CURL_R2_MIN` are NOT part of that task. The bend they gate is fitted on every
5-second bar in the window against an x-axis stretched 0 to 1, so the point count does not reach
it. Measured on ws1r at 08-04 11:33:30, 4-minute window, read downward: at 2, 12 and 21 points the
bend is 17.6460, the arc 4.4115 and the bend's own fit 0.6216 — identical — while the slope moves
-15.6117 to -1.1627 to -0.6146. The axis those two move on is WINDOW LENGTH, `K_WINDOW` (4) times
the timeframe.

### read but not set by this walk

| value | where | note |
|---|---|---|
| boundaries **85 / 15** | `optimus9_system` | every line's out-of-bounds test |
| `MIN_IB_DWELL` **12** | `ws_strat.py` | the in-bounds run that resets the dwell. NOT read at `G30_LEVEL='g30_marker'` |
| `OOBW` **16** | `build_ws_strat_walk.py` | the ws_strat walk's dwell gate. NOT read at `G30_LEVEL='g30_marker'` |
