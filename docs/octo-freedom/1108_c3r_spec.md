# fdm2-3r-cadence — the spec, as he ruled it

HIS NAME, 1107: *"the mech has no name. Yours to give --fdm2-3r-cadence"*.
Prefix `c3r_`. Where it sits, 1107: *"it fires on each bar, while the walk is walking"*.

Every line below is quoted from him or marked MINE.

## the read

| what | the read | his words |
|---|---|---|
| ws3r | **emerging** | 1107: *"it's closed-prev causing the problem. if we make ws3r emerging for this c3r mech, does it satisfy all of examples?"* — it did, 6 of 7 markers, and he dropped the seventh |
| every other line | closed-prev | the standing default |

## the five clauses, his indentation

His pasted spec, 1107, verbatim:

```
1) IF a ws3r line's trajectory is matching ws1r's trajectory until ws1r crosses to ib
2) -IF the ws3r line continues its trajectory and reaches oob without returning past counter-side 50
3) --IF ws3Mage or ws3b is past counter-side 50
4) ---IF ws3r crosses to in-20/80-fence
5) ----IF ws1b has not been same-side oob between 'ws1r reversal' and 'ws3r crossing to in-20/80-fence'
6) -----rev-trade ELSE stop
```

## his rulings on each clause

| the clause | what he ruled |
|---|---|
| 1, what "trajectory matching" means | *"both lines read towards the same side"* |
| 1, where the match must start | *"ws1r's oob entry. note that ws1r will not be oob shortly after and ws3r will not.. this makes the 'ws1r's oob entry.' test a one-time-only test"* |
| 2, what it is for | *"clause 2 was designed to reject an unstable ws3r, a line that bends back and forth before it reaches the target side. an example of this is seen between 08-24 0836 and 0915"* |
| 2, where the window opens | *"ws3r's first print on the target side of 50 after ws1r's target-side oob entry"* |
| 2, how many returns make it unstable | *"one return is enough to trigger unstable"* |
| 3, at which bar | *"the full TF bar before the cross to infence"* |
| 4, the second branch | *"4) ---IF ws3r crosses to in-20/80-fence OR (ws1Mage is same-side oob and reversing while ws3r is oob, and ws4r is infence)"* / *"ws1Mge reversal is lift-off driven"* |
| 4, branch B vs the cross | *"my reading for both is 'the branch-B bar replaces the cross'"* |
| 5, which event | *"same event: ws1r to ib"* |
| 6, what "ELSE stop" means | *"I wrote this only so the mech would have closure. I'm saying the outcomes are either rev-trade, or kill (stop) the 3r-cadence mech"* |

## HIS 1108 ADDITION — the rev-trade waits for ws1Mage

His words: *"one addition to c3r's rev-trade sepc line: walk to ws1MAge same-side reversal
(where ever it is on the board) before placing the rev-trade"*.

So clause 6 is no longer the placement bar. Clause 6 arms a walk; the walk places the rev-trade.

| what | the ruling | source |
|---|---|---|
| what the walk waits for | the first ws1Mage **same-side** reversal | his words |
| any level requirement on it | NONE — *"where ever it is on the board"*. "board" is the full range, never a region | his words, and his 1016 ruling on the word board |
| which producer reads it | `jig.lift_off(ws1Mage emerging, side, LIFT_PTS, gap_for(1), LIFT_TOL, LIFT_WOB)` | his 1108 pick between two candidates. It takes the side as an input, so same-side is direct, and c3r branch B already reads this exact stamp |
| what ends the wait with no rev-trade | **a race: the MAE 1.1 stop, or the next cadence event — first of** | his 1108 words: *"race mae stop and next cadence event (first of)"* |
| the LEVEL ws1Mage must hold at its reversal | **oob**, 85 high / 15 low | his 1108 *"apply the ws1Mage oob to the mech so that we are net positive"*, after the five-gate sweep |
| the knobs | `FDM2_C3R_MAGE_ON` 1, `FDM2_C3R_MAGE_GATE` 'oob' | banked 1108 |

### decided and stated, not his

| the concretion | MY choice | why |
|---|---|---|
| which bar the walk starts from | the clause-4 bar — branch A's cross bar or branch B's bar, whichever fired | it is the bar clause 6 reaches today |
| which bar the rev-trade is placed on | the lift-off **stamp**, `K.lift_stamp(b)` = b + LIFT_WOB - 1 = b + 35 s at LIFT_WOB 8 | his standing rule: a lift-off is not knowable until its hold completes, and every consumer adds the wob in one place |
| the ws1Mage read for the lift-off | emerging | his standing rule: lift-off reads emerging, every other line read is chart-matched. Branch B already reads `LN['MGE'][1]` |
| the cadence-event producer for the race | `v4_fdm2.cadence_events(LN, side, A, B)` | it is the one that enumerates them |

### OPEN — needs his ruling before the race is wired

| the gap | the question |
|---|---|
| a tie | the lift-off stamp and a cadence event land on the SAME bar. Which wins? His banked tie convention is *"A TIE GOES TO THE STOP"*, but that was the price stop against a signal, not two signals |
| the cadence event's side | does ANY cadence event end the wait, or only one on the same side as the c3r arm? |

## HIS 1108 LATER RULINGS — the stop, the exit, the row unit

| what | the ruling | his words |
|---|---|---|
| ws3r minimum dwell | 36 bars = 180 s, as `FDM2_C3R_DWELL` | *"ws3r minimum dwell should be 3 minutes"* |
| the exit | the first TARGET-SIDE cadence event after the open, or the stop, first of | *"the next opposite-side cadence event. it's the best option we have because the c3r trade events are not continuous - they exist to fill the main chain when the walk has no other way to reverse a trade"* |
| which cadence side closes it | the target side only | *"the cadence must be target-side (example c3r opens a high SHORT, the only thing that can close it is a target (low) side cadence or a stop)"* |
| the stop LEVEL | a RAW kline high or low, found by `jig.mage_cascade_bar` walking back to look forward | *"we set the stop level using raw high/low"* |
| the stop TRIGGER | pxs reaching that absolute price, via `F2.stop_bar_at` | *"we use pxs to match the stop level ... pxs smoothes out the bumps, so small spikes near the stop won't appear to pxs, therefore the stop is avoided - only a real price push can trigger the stop"* |
| the row unit | one row per trade event | *"consolidate and count the trade as a single evemt"* |
| the 94-day baseline | not run | *"no 94 day baselines yet - there's a lot of things to make right before we spend cost on it"* |
| the firing population | his, by eyeball | *"the firing population is harder to gauge, for the reasons I called out - I'll have to do it by eyeball"* |

### the five-gate sweep that set `FDM2_C3R_MAGE_GATE`

Same 25 trades, 2026-08-25 .. 2026-08-31, raw-level stop and the target-side cadence exit.

| the ws1Mage gate | the wait, median | MAE %, median | realised %, total | net % | net % per trade |
|---|---|---|---|---|---|
| none | 0.8 min | 0.221 | -4.569 | -9.507 | -0.3803 |
| oob | 24.0 min | 0.140 | +7.610 | **+2.673** | +0.1069 |
| ib | 2.0 min | 0.321 | -2.382 | -7.319 | -0.2928 |
| ex-fence | 23.2 min | 0.131 | +7.708 | +2.771 | +0.1108 |
| in-fence | 2.4 min | 0.375 | -3.430 | -8.368 | -0.3347 |

`ex-fence` nets 0.098 points higher. HE PICKED `oob`. 25 trades cannot separate them.

### OPEN after the ws1Mage wait landed

| the gap | the detail |
|---|---|
| two c3r firings can land on ONE ws1Mage reversal | 2026-08-30 20:27:05 and 2026-08-30 21:39:05 both wait into 2026-08-30 22:02:35 and open the same trade. His consolidation was on the c3r firing bar; the collision is now at the landing bar. Counting it once: 24 trades, net +0.831%, +0.0346% per trade |
| the walk back can place the level AT the open bar | 3 of 20 stopped trades, and 12 of 20 within 12 bars = 60 s. The tightest stop is 0.005%. His buffer ruling is still open and this is where it bites |

## `fdm2-dynastop` — HIS NAME, 1108, HIS GO

His words: *"noted. bank this `fdm2-dynastop` mech as-is."*

| what | the detail |
|---|---|
| what the mech is | a per-day stop percent that HE rules, with the measured leg travel beside it |
| `FDM2_C3R_STOP_SRC` | `day` — the stop is his ruling for the UTC day the trade OPENS on |
| `FDM2_C3R_STOP_BASE` | 1.10 — the percent on a day he has not ruled. His *"I think our baseline is 1.1, but that could be wrong"* |
| the day a trade belongs to | the day its trade OPENS on, UTC. MINE, stated |
| the trigger | pxs reaching that absolute price — his 1108 two-series rule still holds |
| `c3r_stop_day` | HIS rulings. One row per UTC day: percent, his words, when set. Only he writes it |
| `c3r_leg_mfe` | the measurement. One row per (day, timeframe): legs and the leg travel's min / p25 / median / p75 / max, plus the median leg length. Carries a knob hash |
| the ruling banked so far | 2026-08-25 at 2.000%, his *"0825 needs a 2% stop"* |
| `FDM2_C3R_STOP_SRC` = `walkback` | the raw-extreme level from `jig.mage_cascade_bar`. Kept because it is measured |

### what it measured, 2026-08-25 .. 2026-08-31, 22 trades

| the stop rule | trades | stopped | closed at a target-side cadence | gross % | net % |
|---|---|---|---|---|---|
| the raw-extreme walk back | 22 | 18 | 4 | +5.467 | +1.122 |
| `fdm2-dynastop`, every day at 1.10 | 22 | 10 | 11 | +2.960 | -1.385 |
| `fdm2-dynastop`, 08-25 ruled at 2.00 | 22 | 10 | 11 | +2.060 | -2.285 |

Banked with those numbers on the record. It is the instrument for his rulings, not yet a better stop.
