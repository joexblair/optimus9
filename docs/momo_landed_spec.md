# momo_landed spec

reflects the code at 0810, before the clear-mechanism change. producer: `optimus9/analysis/jig.py::momo_landed`.
verdict: `optimus9/compute/momo_gated.py::momo_g` under `momo_window`. io: `build_momo_landed.py`.
report + pine: `report_momo_landed.py`. reads: `build_eyes_on_pine.py`.

---

## lines

    ws{TF}r: 7|5|8|close        TF = 8..33 minutes, 26 lines, emerging
    ws1Mage: 38|0.93|close      read for the per-bar table only
    ws1b:    49|0.95|close      read for the per-bar table only

-pxs grid 5s. window 08-04 12:00 -> 08-09 12:00, 86,400 bars

---

## ws1 markers

-a ws1 marker = a gcws30b oob->ib crossing RELEASED by the ws1 gate
--read from `ws_strat_walk` where `wsw_gate_by = 'ws1Mage+ws1b'`, not recomputed here
--stamped at `wsw_conf_ms`, the confirmation bar. causal
--`dr` = `wsw_side`, the signal's own side
-160 markers over the window. 81 at dr +1, 79 at dr -1
-median gap between markers 45 min

---

## tagging

-at each marker, tag the ws{8..33}r lines that qualify for momentum (momo or curl)
--the verdict is `momo_g(R[tf], dr, marker_bar)`
--the momo window is DYNAMIC: `{K_WINDOW:4} x TF` minutes. TF8 -> 32 min, TF33 -> 132 min
--`momo_window()` rebinds `MOMO_WINDOW_MIN` and `MOMO_SAMPLES` per TF, then restores
-1,684 (marker x TF) tags on 154 of 160 markers
-2 markers tag nothing: 08-04 20:41:55 and 20:54:55, both dr +1

---

## fence_momo_landed

    fence_momo_landed = 100 - {knob:20}   ->  fence [20, 80]

-outside = `v > 80` for dr +1, `v < 20` for dr -1
-a tagged line must be INSIDE the fence at or after the tag before it can cross out
--the outside-run must START at or after the tag. standing outside since the tag is not a crossing
--MY READING, not stated by Joe. still open

---

## momo_landed

-IF a momentum tagged line has {XWOB:4} crossed out of the fence
--create a timestamped `momo_landed` event
-the event bar = the bar the hold completes = cross + XWOB - 1. first knowable bar
-117 events

## the clear — BEING REPLACED 0810

-CURRENT: all tags are cleared when a momo_landed event is printed
--Joe's words: "all tags are cleared when a momo_landed event is printed"
--consequence: one landing per marker. 117 events from 117 distinct markers
--consequence: tags are live on only 26.1% of bars in 08-04 12:00 -> 22:00
--worked case: marker 08-04 18:08:05 tagged 22 TFs; ws12r landed 18:09:35; the other 21 tags were
  discarded unfired after 90 s. next marker 19:12:35, so 63.0 min with an empty set
-REPLACEMENT, Joe 0810: "instead of clearing on 'first momentum line exiting fence', now it will
 be 'highest TF momentum line curling against bias'"

---

## knobs

| knob | value | unit |
|---|---|---|
| fence_momo_landed | 20 | fence [20, 80] |
| XWOB | 4 | 5s bars = 20s held outside the fence |
| K_WINDOW | 4 | momo window = 4 x TF minutes |
| TFS | 8..33 | minutes, 26 lines |

-`MOMO_WINDOW_MIN` now dynamic at 4 x TF. `LEVEL_SLACK` 13.9, `MOMO_STEP_MIN` 5, `MOMO_SLOPE_MIN` 1.0,
 `MOMO_R2_MIN` 0.50 — all in the queued URGENT tuning task, untuned

---

## counts — 117 events

| | n |
|---|---|
| markers | 160 |
| (marker x TF) tags | 1,684 on 154 markers |
| momo_landed events | 117 |
| dr +1 / -1 | 60 / 57 |
| momo / curl at the tag | 106 / 11 |
| distinct ws{TF}r lines that landed | 25 of 26 |
| distinct markers that produced a landing | 117 |

| lag, marker -> landed | min 0.3 | mean 7.7 | max 36.2 min |
| lag, momentum_true -> landed | min 0.5 | median 12.8 | mean 28.6 | max 150.8 min |

-events by line, top: ws8r 28, ws9r 11, ws10r 6, ws12r 6, ws13r 6, ws15r 6
-tagging is near-uniform TF8 (98 markers) to TF33 (48), so the ws8r concentration is a RACE, not a
 tagging bias — under the current clear the first line to the fence takes the marker

---

## momentum_true

-`momentum_true` = the FIRST marker of the unbroken same-side run in which that TF stayed qualified
-`momentum_set_by_tf` = `min-max` of every TF tagged at that marker. unfiltered
-marker-grained, NOT 5s. momentum is evaluated only at markers. Joe 0810: "this is exactly how I
 want it to behave"
-a run breaks on a side flip. `dr` is an input to the momentum test
-a run does NOT break on an intervening momo_landed. clearing tags is bookkeeping

| | n |
|---|---|
| momentum_true == the tagging marker | 62 |
| momentum_true earlier | 55 |
| interval A markers (momentum_true, tag] with the TF NOT tagged | **0** — the run is unbroken by construction |
| interval B markers (tag, landed) | 1 of 117 — 08-07 02:21:10 ws11r, a side-flipped marker that did not re-tag it |

-`momentum_true` is NOT the bias flip: 71 of 117 sit on a flip, 45 do not, 1 is the first marker
-38 of the 84 distinct momentum_true stamps have no flip behind them
-13 of the 59 bias flips produce no landing at all
-the gap from the previous marker does not separate the two causes: flip median 44.3 min,
 no-flip median 54.3 min

---

## outputs

| artefact | holds |
|---|---|
| `momo_landed` | 117 rows, 19 cols. one row per event, every knob stamped |
| `momo_landed_bar` | 86,400 rows, 43 cols. per 5s bar: pxs, marker, tag set, landing, 26 r columns |
| `momo_landed_report` | 117 rows, 18 cols. the onscreen table + momentum_true + set_by_tf |
| `ws_strat_momo_landed.pine` | 117 events -> 117 TF1 bars. BLUE dr +1 (60), YELLOW dr -1 (57) |
| `eyes_on_pine` | 175 rows, 12 cols. Joe's chart reads, one row per event, appended never overwritten |
| `big_bar_detection` | 0 rows at MOVE_PCT 1.0 / MOVE_SEC 180 / EDGE_SLACK 2 |

---

## big bar detection — EXPERIMENTAL, 0 signals

-both conditions ANDed. bias = the momentum tag's `dr` (MY READING)
-run 08-04 12:00 -> 22:00, 7,200 bars

| condition | bars |
|---|---|
| C1a 1% move inside 180s | 52 (0.72%) |
| C1b ws1x crosses ws1b | 432 |
| C1a AND C1b | 1 |
| any live tag | 1,881 (26.1%) |
| C2 a live tag in [78,80)/(20,22] | 491 |
| ALL | **0** |

-the one condition-1 bar is 08-04 19:45:00, up 1.001%, ws1x under ws1b. **live tags: NONE** —
 ws18r landed 19:22:05 and cleared the set; next marker 20:20:05
-1% is ~the 99.85th percentile of the window. max 180s move: up 1.353% @ 20:53:25, dn 1.260% @ 20:17:15
-EDGE_SLACK 2 -> 30 changes nothing. MOVE_PCT must fall to 0.2% before 2 signals appear
-`ws1x` (5|0.35|close) is still a live config; it was deleted from the ws_strat gate, not the DB

---

## ws33r 08-04, the fence-resolution case

-ws33r sits at 80.2200 from 19:32:35 to 19:47:55, then prints 89.2951 at 19:48:00 — +9.0751 in one 5s bar
-hi edge 80.0 (fence 20) -> exits 19:15:00, lands 19:15:15
-hi edge 80.5 through 85.0 -> ALL exit 19:48:00, land 19:48:15. the step jumps the whole band
-hi edge 90.0 -> never before 21:30
-max ws33r 19:00 -> 21:30 is 89.2951, first at 19:48:00, re-touched 20:09 -> 20:15
-the fence has two usable settings on this line and nothing between them

---

## notes

-a filename's meaning does not move. contents refresh, meaning stays
-Joe's eyes on the pine are a measurement. reads go in `eyes_on_pine`, one row per event, verbatim
-momo's window is dynamic at 4 x TF; the other momo constants are not, and are untuned
