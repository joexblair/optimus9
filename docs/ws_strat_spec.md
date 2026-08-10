# ws_strat spec

reflects the code at 0810. mechanic: `optimus9/analysis/ws_strat.py`. io: `optimus9/analysis/build_ws_strat_walk.py`.

---

## lines

    ws{TF}Mage: 38|0.93|close        TF   = [1,2,3,4,5,6,8,15,22] minutes
    ws{TF}m:     6|0.4|close
    ws{TF}x:     5|0.35|close
    ws{TF}b:    49|0.95|close
    ws{TF}r:     7|5|8|close

    gcws{gcTF}Mage: 38|0.93|close    gcTF = [15,30] seconds
    gcws{gcTF}m:     6|0.4|close
    gcws{gcTF}x:     5|0.35|close
    gcws{gcTF}b:    49|0.95|close
    gcws{gcTF}r:     7|5|8|close

-all emerging, boundaries 85 / 15 from `optimus9_system`
-the walk uses gcws30b. the gate uses ws1Mage and ws1b. every other line is stored, not read

---

## signal logic

-walk forward on pxs, 5s bars, from 08-04 12:00 to cache end
-open the dwell on a gcws30b oob breach
--gcws30b oob = >= 85 (hi) or <= 15 (lo)
--the dwell counts consecutive 5s bars on ONE side
--the dwell resets on a side flip, on a confirmed cross, and on NaN
--if an ib cross wob is incomplete, the dwell is not affected
---incomplete = fewer than {XWOB:2} consecutive ib bars
---the dwell is carried across the poke and keeps counting when gcws30b returns oob
--example:
---gcws30b goes oob-lo @ 08-04 16:07:45, dwell = 1
---gcws30b prints 15.35 @ 08-04 16:10:10, ib for 1 bar only, dwell holds at 29
---gcws30b prints 14.87 @ 08-04 16:10:15, back oob-lo, dwell = 30

-create a gcws30 signal on the ib cross
--the cross is the first ib bar. ib = 15 < v < 85, strictly
--the cross is confirmed when {XWOB:2} consecutive 5s bars have printed ib
--the confirmation bar = cross + XWOB - 1. every line value is read at the confirmation bar
--discard the signal unless the dwell was > {OOBW:16} 5s bars at the last oob bar
--example:
---cross @ 08-04 16:10:20, gcws30b = 15.35, dwell = 30
---confirmed @ 08-04 16:10:25, ib_run = 2
---30 > 16, so the signal stands

---

## gate logic

    now we need to gate ws30 signals
    -unless ws1Mage is OOB
    --unless ws1b is outside of a 100-{knob:22} fence
    ---a gcws30 signal is gated

-gated is the resting state. the lines cannot block, only release
-released = ws1Mage oob AND ws1b outside the fence, both read at the confirmation bar
--ws1Mage oob = >= 85 or <= 15
--ws1b outside the fence = > 78 or < 22
--not side-matched. oob means oob, either side
-example, released:
---cross @ 08-04 12:38:50, confirmed @ 12:38:55, side +1
---ws1Mage = 93.93, oob
---ws1b = 94.23, outside the fence
---released
-example, gated:
---cross @ 08-04 16:31:25, side -1
---ws1Mage = 23.85, not oob
---ws1b = 21.83, outside the fence
---the unless is not qualified, so it stays gated

---

## ws1b weaker flag

-if ws1b is outside of the fence and has not reached oob when gcws30 signals, then a flag is set to show that ws1b was weaker than s1Mage
--set when ws1Mage is oob AND ws1b is outside the fence AND ws1b is not oob
--so ws1b sits in 78..85 or 15..22
--both sides of the comparison must hold. without the ws1Mage term the flag fires where ws1b cleared the fence and ws1Mage cleared nothing, and the words are then false
-column `wsw_ws1b_weaker_than_ws1Mage`
-example:
---cross @ 08-04 13:02:15, side -1
---ws1Mage = 14.32, oob
---ws1b = 16.19, outside the fence, not oob
---flag set

---

## ws1b lookback — SEPARATE MECHANIC, held still

-IF gcws30 has created a signal and ws1b is not oob THEN a {LB:19}-bar lookback is employed to capture a ws1b oob. IF the lookback captures ws1b oob THEN 1) mark the gcws30 signal as `ws1-exhausted`, 2) leave the gcws30 signal ungated
--reads ws1b only
--the window ends AT the confirmation bar. causal
--it sits OUTSIDE the gate's AND — it releases on its own
-Joe 0810: until I feel some stability, we'll be working on one mechanism at a time. leave the lookback code as it is

---

## knobs

| knob | value | unit |
|---|---|---|
| OOBW | 16 | 5s bars, tested `>`, so >= 17 = 85s |
| XWOB | 2 | 5s bars = 10s ib hold |
| fence | 22 | ws1b outside [22,78] |
| LB | 19 | 5s bars = 95s |
| BUCKET_MS | 60,000 | pine grid, TF1 pane |

---

## counts — 08-04 12:00 to 08-09 12:00, 86,400 bars

| | n |
|---|---|
| ib crossings found | 1,310 |
| dwell > 16, so a signal | 361 |
| released by ws1Mage + ws1b | 160 |
| released by the lookback alone | 96 |
| nothing released | 105 |
| ws1b_weaker_than_ws1Mage | 28 |
| ws1-exhausted | 123 |

---

## outputs

| artefact | holds |
|---|---|
| `ws_strat_walk` | one row per signal, 48 cols. every knob and line spec stamped on the row |
| `ws_strat_bar` | one row per 5s bar, 86,400 rows. pxs, close, dwell state, all 21 line values, gate verdict on signal bars |
| `ws_strat_gated.pine` | the signals the gate releases. red = hi side, green = lo side. TF1 |
| `ws_strat_blocked.pine` | the signals nothing releases. `emit_ws_gated.py` |

-a filename's meaning does not move. contents refresh, meaning stays
-`*.pine` is gitignored. the emitters are tracked, the outputs are not

---

## benched

**ws1x reversing.** was in the gate as `---unless s1x has wob {knob:4} reversed`.
*why benched*: Joe 0810 — I can also see how ws1x reversing is not aligned with the ws30 markers, and creating friction. measured before removal: as a condition on the openers it withheld 235 of 247. `jig._mage_rev` fires on the ONE bar the run-length hits ±wob, so as a same-bar test it almost never coincided with a confirmation bar. out of the gate, out of the stored lines, out of the tables.

**fence at 10.** the 0806 sweep took the fence from 22 to 10 on event count.
*why benched*: at 10 the fence [10,90] sits OUTSIDE the 15/85 boundary and inverts the clause — a ws1b that IS oob then sits inside the fence and the clause goes silent. 12 of 87 signals were in that band, 3 gated with ws1b oob. back to 22, which sits inside the boundary.

---

## parked

-**bb multi sweep on Mage and b** to pull the signals back 30sec, A/B on MAE and MFE. blocked: needs new indicator_configs rows per mult, a cache build per mult, and an exit rule or horizon. no exit rule exists

---

## notes

-the indentation in a spec is logical. a deeper level nests inside the one above. `--` under `-` reads as AND
-the 08-08 collector outage 09:29:25 -> 19:24:15, 7,137 bars, was repaired 0809 from TV csv via `kline_sanitiser`. tape is 1,632,961 bars over 05-07 -> 08-09 12:00, 0 gaps
