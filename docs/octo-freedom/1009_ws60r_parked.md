# PARKED: THE ws60r / ws12r-oob ROUTING MECH. 1009

Joe 1009: *"let's park the ws60r/ws12 oob routing mech"*. Everything below is banked so it can be
picked up cold. NOTHING IS APPLIED - every knob defaults to the banked build.

## HOW TO PICK IT UP

All knobs live in `docs/octo-freedom/1005_scoring/_chain10.py`, all default to the banked value.

| knob | default | what it does |
|---|---|---|
| `W_DGATE` | `off` | `off` the handover fires on the oob run alone / `traj` travel decides / `vote` the 40-min count-vote decides |
| `W_VOTE_TIE` | `c3` | with `W_DGATE=vote`: `c3` = the ws5-ws11 traj majority breaks a tie, `travel` = the old reading breaks it (the ISOLATION ARM) |
| `W_VOTE_MIN` | 40 | the vote window in minutes. 40.0 / the 5.0-min block = 8 diffs |
| `W_C3_LO` / `W_C3_HI` | 5 / 11 | C3's TF band |
| `W_SQX` | 0 | Joe's rule: an oob run that ends SHORT of the dwell with a squashed walk x-cross in it closes A at the bar ws12r returns IN-BOUNDS and opens B |
| `W_ARM_TF` | 2 | the `exit-armed` line. 2 = ws2Mage banked, 1 = Joe's swap |
| `W_TRACE_DGATE` | 0 | adds ws60r's own reading to the trace at every bar it is or would be consulted |
| `W_TRACE_NOX` | 0 | records the walk x-crosses that `W_NOX=1` suppresses |
| `W_TRAJ_LOOK` | 24 | the traj lookback in samples. `3 * TF` = 36 is Joe's 1009 value |

THE REGRESSION THAT MUST HOLD: `LG_TAPE_END=2026-10-05 W_DGATE=off` -> **1623 legs, NET +4.8307**.
Verified after every patch on 1009.

## THE LEDGER — every arm measured, net after 0.11% per leg boundary

Run with `W_NOX=1 W_SQX=1 W_TRAJ_LOOK=36` unless stated.

| the arm | legs | NET | note |
|---|---|---|---|
| no ws60r gate, `W_DGATE=off` | 1423 | **+12.0857** | ALSO removes the exhaustion override and every B path. THREE CHANGES BUNDLED - not isolated |
| the 40-min count-vote + travel tie-break | 1586 | **+9.5361** | the vote replacing travel-weight is worth **+7.5188** |
| travel only, `W_DGATE=traj` | 1596 | +2.0173 | |
| the 40-min count-vote + C3 tie-break | 1593 | **-15.3215** | |
| the banked build, `W_DGATE=off` with no NOX/SQX | 1623 | **+4.8307** | the regression |

## WHAT WAS LEARNED, WITH NUMBERS

- **C3** - the traj majority across ws5r..ws11r - scored **7 of 8** on DIRECTION against Joe's own
  chart read of 8 measured ties. Its NET is **-4.9174** per-episode over 14 effective episodes
  (7 worse -15.7440, 7 better +10.8265, 22 of 36 unchanged). Direction accuracy and net are
  different targets. On a fair coin 7 of 8 happens 7.0% of the time, so n=8 cannot separate it
  from the always-UP constant, which scored 5 of 8.
- **C3 is dr-BLIND.** `TRAJ_KIND='close'` ignores the `side` argument, so C3 and the 36-sample
  tie-breaker are byte-identical at side +1 and -1 on all 8 ties. The flip-the-dr refutation test
  is a no-op on C3, C1, C4, C2 and the ladders; only the divergence anchor reads dr.
- **ws12r's own reversal is 79.9%** - 3031 of 3795 oob runs return in-bounds before the 6.1-min
  dwell completes. That is the ~80% Joe sees on the charts. pxs reverses 48-57% across all runs,
  but only **26.5-36.7% on the runs that COMPLETE the dwell**, so `oob_gate_bars` 72 already
  selects continuation.
- **ws60x leads ws60r perfectly and uselessly often.** 100% of crosses held 24 or 48 bars see
  ws60r's traj match, 0 exceptions, on both the `r` and `m` targets - but 62-77% are ALREADY
  matched when the wob completes. The lead population is ~1/3. p90 lag 17.2 min (r) / 25.6 min (m)
  at wob 24. See `1009_arming.md` for the full table.
- **The arming line swap** (ws2Mage -> ws1Mage) arms 37% sooner and costs ~930 extra legs and
  ~102 of drag, taking every gate form to about -200. See `1009_arming.md`.

## THE OPEN QUESTIONS, RANKED BY THE SIZE OF THE NUMBER

1. **the never-armed legs** - ~205 legs, **-404.52**, 161 of them hitting `mae_stop_pct`. Their
   arming line never crosses into oob at any bar of the leg, so no walk exit exists for them by
   construction. A mech that doesn't depend on the arming crossing DOES NOT EXIST. The largest
   number in the build.
2. **the gate/exhaustion isolation** - `W_DGATE=off` bundles three changes. An always-HANDOVER
   mode would isolate the gate from the exhaustion override and the B paths, and decide whether
   the gate or the B-trades cost the 2.5 to 22.
3. **the ws60x-inserts-the-verdict mech** - Joe 1009's design, unbuilt. Knobs unset: which line
   (r or m), which wob (24 or 48), and how recent "recent" is.
4. **C3's tie-break band and the EDGE question** - Joe ruled ANY squashed cross counts
   (*"more hits are better than less"*); the EDGE-only variant was 10 A-trades against 23.
5. **`W_EXH_FRAC`** - the 1/4-seam fraction, never swept. Joe: *"I don't think it will be far
   from 0.25"*.
6. **x-cross** - disabled by `W_NOX=1` throughout. Joe: *"x-cross is troublesome at the moment,
   it's on my list for us after the sweep"*.

## THE SCRIPTS

| file | what it does |
|---|---|
| `_abrep.py` | **the permanent 9-column A/B walk renderer**. `X_DAY`, `X_FROM`, `X_NTRADE`, `X_CEIL` |
| `_c3cost.py` | C3's per-episode cost, both arms from the same leg open |
| `_c3walk.py` | the 5 worst C3 ties as timestamp walks, shared prefix then the two branches |
| `_bprof.py` | the reversal premise + the worst 5-day span + every B trade's MAE/MFE profile |
| `_mlead.py` / `_x60lag.py` | the ws60x lead-lag against ws60m and ws60r |
| `_barm.py` | the arming delay and the never-armed population |
| `_votecmp.py` | the vote gate against the travel gate, tape-wide |
| `_noxsq.py` / `_noxpop.py` | the squashed-x-cross population, 23 A-trades |
| `_stale.py` .. `_stale9.py` | Joe's chart clauses turned into measurables, the 8-tie scan, the truth scoring |
| `_squash.py` | the three readings of "a squashed cross" (SUPERSEDED - wrong mech, kept for the record) |
| `_flip.py` | the dr-flip refutation test |

## CORRECTIONS MADE TO MY OWN CLAIMS ON 1009 — on the record

- the C3 cost is **-4.9174** per-episode, not the -24.8576 I first gave. That figure was the
  whole-chain difference and carried every downstream leg shifting off a changed exit bar.
- there is **no mech fault** in the multi-decision leg. The arms diverge exactly at the first gate
  decision on all 5 ties checked; my "diverges before the routing bar" came from an assert over
  rows that included my own inserted MAE/MFE bar rows, which move with the exit bar.
- Joe's ~80% is **ws12r's own reversal**, not pxs. pxs does not reach 80% on any measure tried.
- the MAE/MFE BAR rows were mislabelled with the stop-rule values on a stopped leg. Fixed: bar
  rows carry the measurement, the closing line carries the stop rule and names the tape's reading.
