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

### M4 — a finisher line's momentum is CANCELLED by its own x/m/b crossing it

-Joe 0812: "10:57 - ws3r crossed under by ws3x/m/b. this cancels ws3r's momentum and generates a
 trade signal"
-so the cancel is a per-line event: the line's own faster bands crossing its r
-this is the finisher-side analogue of the domTF stall
-UNSPECIFIED: whether all three of x/m/b must cross, or any one

### M5 — every finisher decision is gated to a gcws30 signal

-Joe 0812: "finisher events and decisions can only take place on a gcws30 signal"
-so the finisher clock is the gcws30 signal series, not the 5 s bar
-a condition that becomes true between signals waits for the next signal
-this is why Joe's timestamps land on signals and his action timestamps land 5 s later

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
