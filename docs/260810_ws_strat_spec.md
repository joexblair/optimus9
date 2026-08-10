# ws_strat — the gcws30b walk and the ws1 gate

Joe's spec, 0805–0810. The live copy is the `optimus9/analysis/ws_strat.py` docstring; this doc is
the same thing in Joe's own layout, with the knob register and the history of what changed.

Code: `optimus9/analysis/ws_strat.py` (mechanic, no IO) · `optimus9/analysis/build_ws_strat_walk.py`
(tables + pine). Window 08-04 12:00 → 08-09 12:00 UTC, 86,400 bars of 5 s.

**THE INDENTATION IS LOGICAL.** Joe 0810: *"the layout is typically logical when I spec — I just had
an error in my writing this time."* A deeper level is nested inside the one above it. Read the
levels; where they disagree with the prose, ask which is the error.

---

## 1. The walk

    starting at 08-04 12:00
    -walk forward on pxs
    -IF gcws30b has been oob for > {knob:16} * 5s bars
    --IF gcws30b has crossed from OOB to IB, using XWOB={knob:2}
    ---store the crossover timestamp and the line values for:
        gcws30[b,Mage,r]
        ws[1,2,3,4,5,6][b,Mage,r]
    -loop the walk until cache end

    if a IB cross wob is incomplete, the OOB dwell is not affected      (Joe 0805)

- OOB = `v >= 85` or `v <= 15`; IB = `15 < v < 85` strictly. NaN is neither and breaks both runs.
- the dwell counts OOB bars on ONE side. It resets on a CONFIRMED cross, a side flip, or NaN — an IB
  excursion shorter than XWOB does not touch it.
- **cross** = the first IB bar. **confirmation bar** = `cross + XWOB - 1`, the first bar the crossing
  is knowable. Every gate clause and every banked line value is read at the CONFIRMATION bar.
- the dwell a signal is gated on is the value at the LAST OOB BAR before the cross.

## 2. The gate

    now we need to gate ws30 signals
    -unless ws1Mage is OOB
    --unless ws1b is outside of a 100-{knob:22} fence
    ---a gcws30 signal is gated

    released = ws1Mage OOB  AND  ws1b outside the fence

- **gated is the resting state.** The lines cannot block, only RELEASE. A signal that nothing
  releases simply stays blocked; there is no actor to name, and `wsw_gate_by` is `''`.
- Joe 0810 in plain terms: *"block (gate) a gcws30 signal unless s1Mage is oob and s1b is outside of
  its fence."*
- NOT side-matched. "is OOB" means OOB, either side.

## 3. The flag

    if ws1b is outside of the fence and has not reached oob when gcws30 signals, then a flag is set
    to show that ws1b was weaker than s1Mage                                        (Joe 0810)

- column `wsw_ws1b_weaker_than_ws1Mage`. Both sides of the comparison must hold:
  `ws1Mage OOB AND ws1b outside the fence AND ws1b not OOB`.
- with only the ws1b half it fires on 87 signals and its own words are false on 59 of them, because
  ws1b cleared the fence while ws1Mage cleared nothing.

## 4. The 19-bar lookback — a SEPARATE mechanic

    IF gcws30 has created a signal and ws1b is not oob THEN a 19-bar lookback is employed to capture
    a ws1b oob. IF the lookback captures ws1b oob THEN 1) mark the gcws30 signal as `ws1-exhausted`,
    2) leave the gcws30 signal ungated                                              (Joe 0805)

- reads **ws1b only**. The window ENDS at the confirmation bar — causal.
- it sits OUTSIDE the section-2 AND: Joe's wording is a flat "leave the gcws30 signal ungated", so it
  releases on its own.
- Joe 0810: *"until I feel some stability, we'll be working on one mechanism at a time. leave the
  lookback code as it is."* Held still, not endorsed — it currently releases 96 of the 256.

## 5. The knob register

| knob | value | unit |
|---|---|---|
| `OOBW` | 16 | 5 s bars, tested `>` — so >= 17 bars = 85 s |
| `XWOB` | 2 | 5 s bars = 10 s IB hold |
| `GATE_FENCE` | 22 | ws1b outside [22, 78] |
| `GATE_LB` | 19 | 5 s bars = 95 s |
| `BUCKET_MS` | 60,000 | the pine grid. TF1 pane |
| boundaries | 85 / 15 | `optimus9_system`, the single home |
| `gcws30b`, `ws1b` | bb 49\|0.95\|close | @30 s and @60 s |
| `ws1Mage` | bb 38\|0.93\|close | @60 s |

Counts at these values, 361 signals from 1,310 candidates:

| | n |
|---|---|
| released by ws1Mage AND ws1b | **160** |
| released by the lookback alone | 96 |
| nothing released | 105 |
| `ws1b_weaker_than_ws1Mage` | 28 |
| `ws1-exhausted` | 123 |

## 6. Deleted, with the reason

- **ws1x reversing** — Joe 0810: *"I can also see how ws1x reversing is not aligned with the ws30
  markers, and creating friction - delete ws1x reversing from the spec."* Measured before removal:
  as an AND on the openers it withheld 235 of 247, leaving the lookback to do 119 of 131 opens.
  `jig._mage_rev` pulses on the ONE bar the signed run-length hits ±wob, so as a same-bar condition
  it almost never coincides with a confirmation bar. Out of the gate, out of LINES, out of the
  tables.

## 7. Tables and outputs

| artefact | contents | meaning is FIXED |
|---|---|---|
| `ws_strat_walk` | one row per signal, 48 cols — every knob and line spec stamped | |
| `ws_strat_bar` | one row per 5 s bar of the window, 86,400 rows — pxs, raw close, dwell state, all 21 line values, and the gate verdict on signal bars. This is the analysis surface | |
| `ws_strat_gated.pine` | the signals the current gate RELEASES. Joe cats this file | **yes — do not repoint it** |
| `ws_strat_blocked.pine` | the signals nothing releases (`emit_ws_gated.py`) | yes |

- `*.pine` is gitignored; the emitters are tracked, the outputs are not.
- a filename's MEANING never moves. Contents refresh; if a new view is wanted it gets a new file.

## 8. Parked

- **BB multi sweep on Mage and b** to pull the signals back 30 s, A/B on MAE and MFE (Joe 0805).
  Blocked: needs new `indicator_configs` rows per mult, a cache build per mult, and an exit rule or
  horizon — no exit rule exists yet, so MAE/MFE cannot be scored.
- **the 08-08 collector outage**, 09:29:25 → 19:24:15, 7,137 bars. Repaired 0809 from TV CSV via
  `kline_sanitiser`. Tape is 1,632,961 bars over 05-07 → 08-09 12:00 with 0 gaps.

## 9. What was wrong before 0810, all caught by Joe

| fault | corrected to |
|---|---|
| ws1x built as a third OR'd opener | deleted — it was never an opener |
| the gate was an if/elif chain, i.e. OR | AND |
| the 0806 sweep put the fence at 10 | back to Joe's 22. At 10 the fence [10,90] sits OUTSIDE the 15/85 boundary and INVERTS the clause: a ws1b that IS oob then sits inside the fence and the clause goes silent. 12 of 87 signals were in that zone, 3 gated with ws1b oob |
| the flag carried only the ws1b half | both sides of the comparison |
| `BUCKET_MS` 15 s against a TF1 pane | 60 s. `array.binary_search` matches the BAR OPEN exactly, so 118 of 160 marks addressed bars that do not exist and never painted |
| the 160 verified | re-tested from scratch against the spec: 160 expected, 160 painted, 0 disagreements |
