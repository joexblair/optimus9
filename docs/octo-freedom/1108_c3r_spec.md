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

## HIS 1108 QUESTION — why no LOW c3r near 0259 on 2026-08-25

His words: *"what would prevent a low c3r from firing near the ws3x-cross over
race{boundary,r,MAge} wob 12 at 0259?"*.

NOTHING IN CLAUSES 2 TO 6. c3r never got a LOW arm there, so clause 1 never started. An arm is a
ws1r same-side **oob** entry, his *"ws1r's oob entry... this makes the test a one-time-only test"*.

| ws1r LOW oob runs on 2026-08-25, closed-prev | opens | closes | the LOW extreme in it |
|---|---|---|---|
| 1 | 2026-08-25 00:07:00 | 2026-08-25 00:07:55 | 10.38 |
| 2 | 2026-08-25 00:20:00 | 2026-08-25 00:22:55 | 9.16 |
| 3 | 2026-08-25 00:33:00 | 2026-08-25 00:33:55 | 14.78 |
| 4 | 2026-08-25 01:36:00 | 2026-08-25 01:37:55 | 8.61 |
| 5 | 2026-08-25 04:22:00 | 2026-08-25 04:22:55 | 8.53 |
| 6 | 2026-08-25 05:43:00 | 2026-08-25 05:46:55 | 2.48 |

The gap from 2026-08-25 01:37:55 to 2026-08-25 04:22:00 is 2 h 44 min with NO LOW oob entry, and
0259 sits inside it.

WHAT ws1r DID DO THERE: a LOW ex-20/80 run from 2026-08-25 02:57:00 to 2026-08-25 03:01:55, 60
bars = 5.0 min, whose lowest value is **18.10** at 2026-08-25 03:01:00. The oob line is 15, so it
came 3.10 short and never crossed.

| the window read | value |
|---|---|
| ws1r LOW ex-20/80 run | 2026-08-25 02:57:00 .. 2026-08-25 03:01:55 |
| its lowest value | 18.10 at 2026-08-25 03:01:00 |
| the oob threshold | 15 |
| how far short | 3.10 |
| c3r arms in 2026-08-25 02:00:00 .. 04:00:00 | 2, BOTH HIGH - 02:00:00 killed by the dwell, 03:29:00 killed by clause 2 |
| c3r firings in that window | none |

HIS ws3x LANDMARK, located. The `xdiag` reader runs the banked `FDM_X10_WOB` 24, so the wob-12
outcome is read off each candidate's own break bar rather than by running a knob off the bank:

| the arm | the cross | ws3x there | the racer there | bars before the hold broke | does it survive a 12-bar hold | its confirm bar at wob 12 |
|---|---|---|---|---|---|---|
| ws3r | 2026-08-25 02:46:30 | 68.48 | 61.18 | never broke in 24 | YES | 2026-08-25 02:47:25 |
| ws3r | 2026-08-25 02:53:25 | 44.71 | 43.43 | 17 | YES | 2026-08-25 02:54:20 |
| ws3r | 2026-08-25 03:00:15 | 33.19 | 26.22 | 4 | no | - |
| ws3r | 2026-08-25 03:00:40 | 27.99 | 26.22 | 1 | no | - |
| ws3r | 2026-08-25 03:01:45 | 33.19 | 26.22 | never broke in 24 | YES | 2026-08-25 03:02:40 |

So his landmark is real - two LOW ws3x crosses survive a 12-bar hold within 6 minutes of 0259 - and
c3r does not read ws3x at all. ITS TRIGGER IS ws1r REACHING oob, and ws1r stopped at 18.10.

## HIS 1109 HYPOTHESIS — a higher Mage reversal leading ws3r's

HIS WORDS: *"we can predict a reversal of ws{TF}r if ws{TF+2}Mage and the lower TF Mages are
printing a semi-cascade pattern that printings timestamps in a close range (I don't know what
close range is yet, let the data guide you). IF the conditions are true, then the reversal of
ws{TF}r can be printed when ws{TF+2 (or +3,+4 - sweep)}Mage reverses"*, and his test: *"test it on
every 08-25 to 08- setup when ws1r,ws2r,ws3r are exfence on the same side. the test passes if
ws3r does actually reverse within 2 minutes of the higher Mages signal"*.

| what | the detail |
|---|---|
| the span run | 2026-08-25 00:00:00 .. 2026-08-31 23:59:55 — HIS END DATE IS TRUNCATED in his message, *"08-25 to 08- "*. 08-31 is MY reading of it and it is stated, not ruled |
| the setup | ws1r, ws2r AND ws3r all ex-20/80 on the same side, through `F2.ex2080_line` |
| the row unit | one row per EPISODE at the run's open. MINE and stated — counting every bar of a run would manufacture the population |
| the pass | the Mage stamp FIRST, then ws3r within 2.0 min = 24 bars. A negative gap FAILS: a ws3r reversal that printed first is not a prediction |
| `semi-cascade` | NOT a term in the tree. NO pattern rule is applied — the ladder stamps and their spread are printed so he names the rule |
| the reader | the `magelead` request kind |

### THE UNGATED RESULT — 94 episodes, 41 HIGH and 53 LOW

| the offset | setups | PASS | FAIL, ws3r led | FAIL, too late | the pass rate |
|---|---|---|---|---|---|
| ws5Mage, +2 | 94 | 52 | 19 | 23 | 55% |
| ws6Mage, +3 | 94 | 51 | 22 | 21 | 54% |
| ws7Mage, +4 | 94 | 46 | 34 | 14 | 49% |

61 of the 94 pass on at least one offset, 33 on none. UNGATED THIS IS NEAR A COIN FLIP, and his
hypothesis is not the ungated claim — the gate is his undefined *"close range"*.

### THE DATA NAMES HIS CLOSE RANGE

The spread between the first and the last of the ws1Mage..ws7Mage stamps, bucketed:

| the ladder spread, ws1Mage to ws7Mage | setups | ws5Mage +2 PASS | its rate | ws6Mage +3 PASS | its rate | ws7Mage +4 PASS | its rate |
|---|---|---|---|---|---|---|---|
| 0 to 30 s | 12 | 10 | 83% | 9 | 75% | 10 | 83% |
| 31 to 60 s | 15 | 10 | 67% | 11 | 73% | 8 | 53% |
| 61 to 120 s | 11 | 5 | 45% | 4 | 36% | 3 | 27% |
| 121 to 300 s | 27 | 15 | 56% | 15 | 56% | 13 | 48% |
| 301 to 600 s | 18 | 9 | 50% | 8 | 44% | 8 | 44% |
| over 600 s | 11 | 3 | 27% | 4 | 36% | 4 | 36% |

| the spread across all 94 | value |
|---|---|
| the smallest | 0 min 05 s |
| the median | 2 min 32 s |
| the largest | 26 min 50 s |

HIS READ HOLDS WHERE THE SPREAD IS TIGHT. At 60 s or under the ladder gives 20 of 27 on the +2
offset = 74%, against 55% ungated. Past 60 s the rate collapses to 45% and never recovers. The
monotone part is only the first two buckets, so a THRESHOLD AT 60 s is what the data supports; it
is HIS to rule, and nothing is applied.

| the gate | setups | ws5Mage +2 PASS | its rate |
|---|---|---|---|
| spread 60 s or under | 27 | 20 | 74% |
| spread over 60 s | 67 | 32 | 48% |

### THE LEAD IS SMALL WHERE IT PASSES

| the ws5Mage +2 lead on ws3r, over the 52 passing rows | value |
|---|---|
| the smallest | 0 min 00 s — the same bar |
| the median | 0 min 10 s |
| the largest | 1 min 50 s |

A MEDIAN LEAD OF 10 s IS THE WEAKNESS. The hypothesis is that the Mage prints EARLY enough to be
used, and on half the passing rows it buys 2 bars. The 0659 case he started from is not typical:
ws5Mage led ws3r by 70 s there, which is at the 90th percentile of this population.

### HIS 0808 LOW EXAMPLE — a counter-example, and he found it by eye

He said *"there's another example near 0808 low"*. It is NOT one of the 94 episodes, because the
setup never holds there: **ws2r is never ex-fence**, sitting at 43.65 to 48.13 against the LOW 20
line, and ws1r only crosses it for 4 bars.

| the bar | ws1r emerging | ex-fence | ws2r emerging | ex-fence | ws3r emerging | ex-fence |
|---|---|---|---|---|---|---|
| 2026-08-25 08:08:00 | 30.71 | . | 43.65 | . | 12.69 | EXF |
| 2026-08-25 08:09:00 | 16.42 | EXF | 43.65 | . | 14.55 | EXF |
| 2026-08-25 08:09:15 | 19.36 | EXF | 43.65 | . | 18.82 | EXF |
| 2026-08-25 08:09:20 | 20.61 | . | 43.88 | . | 20.77 | . |

WHAT THE LINES DID THERE — the Mage cluster lands ON the ws3r reversal bar, not before it:

| the line | its LOW stamps, 2026-08-25 08:05:00 .. 08:25:00 |
|---|---|
| ws3r | 2026-08-25 08:09:35, 2026-08-25 08:12:35 |
| ws1Mage | 2026-08-25 08:09:35, 08:12:35, 08:15:10, 08:19:35, 08:21:25, 08:22:15, 08:24:55 |
| ws2Mage | 2026-08-25 08:09:35, 08:11:00, 08:12:35, 08:22:35, 08:24:50 |
| ws3Mage | 2026-08-25 08:09:35, 08:12:15, 08:22:25, 08:24:50 |
| ws4Mage | 2026-08-25 08:12:35, 08:22:45, 08:23:35, 08:24:50 |
| ws5Mage | 2026-08-25 08:12:35, 08:24:50 |
| ws6Mage | 2026-08-25 08:12:35 |
| ws7Mage | 2026-08-25 08:12:20 |

| the read at 0808 LOW | value |
|---|---|
| ws1Mage, ws2Mage, ws3Mage | all three stamp 2026-08-25 08:09:35 - a spread of 0 s, the tightest in the data |
| ws3r's first reversal | 2026-08-25 08:09:35 - THE SAME BAR |
| ws4Mage, ws5Mage, ws6Mage | all three stamp 2026-08-25 08:12:35, with ws7Mage 15 s earlier |
| ws3r's second reversal | 2026-08-25 08:12:35 - again THE SAME BAR |
| the ws5Mage +2 lead on ws3r's first | -3 min 00 s - ws3r led by three minutes |
| the ws5Mage +2 lead on ws3r's second | 0 min 00 s |

THE TIGHTEST CLUSTER BUYS NO TIME. It matches the ws3r reversal bar exactly, twice, and leads it
by nothing. That sharpens the weakness already measured over the 94: a tight ladder predicts the
BAR well and gives no warning before it. HIS GATE WOULD SELECT THIS SETUP AND IT WOULD BE USELESS
AS A PREDICTOR - it is a coincidence detector at a 0 s spread.

### HIS 1109 READ ON THE FAILURES — TESTED, AND IT DOES NOT SEPARATE THEM

HIS WORDS: *"I think the 'failures' are caused by each of them having a higher r line that is
ex-fence at the time of ws{TF+2}Mage reversing, so the walk follows the higher r line"*.

The read is at the +2 Mage's own stamp bar: every ws{TF}r above ws3 tested for ex-20/80 on the
same side, through `F2.ex2080_line`.

| at the +2 Mage bar | setups | a higher ex-fence r line above ws3 | none above | the share with one |
|---|---|---|---|---|
| PASS on +2 | 52 | 42 | 10 | 81% |
| FAIL on +2 | 42 | 30 | 12 | 71% |
| every setup | 94 | 72 | 22 | 77% |

PRESENCE DOES NOT DISCRIMINATE. A higher ex-fence line is present on 81% of the PASSES and 71% of
the failures - slightly MORE common where ws3r did follow. HIS READ IS NOT SUPPORTED AS A PRESENCE
TEST.

NOR DOES ITS HEIGHT:

| the group | setups | the highest ex-fence r above ws3, median | its min | its max | lines above ws3 ex-fence, median |
|---|---|---|---|---|---|
| PASS on +2 | 52 | ws12 | ws4 | ws30 | 2 |
| FAIL on +2 | 42 | ws10 | ws4 | ws30 | 2 |

THE COUNT IS WHERE A SIGNAL SITS, and it points the OTHER WAY from his read:

| lines above ws3 ex-fence at the +2 Mage bar | PASS | FAIL | the pass rate |
|---|---|---|---|
| none | 10 | 12 | 45% of 22 |
| 1 to 3 | 19 | 16 | 54% of 35 |
| 4 to 8 | 19 | 7 | 73% of 26 |
| 9 to 15 | 4 | 6 | 40% of 10 |
| 16 to 27 | 0 | 1 | 0% of 1 |

4 TO 8 LINES ABOVE ws3 BEING EX-FENCE IS THE BEST BAND IN THE DATA, 73% of 26 - and it is MORE
higher ex-fence lines, not fewer. Past 8 the rate collapses to 40%. The band is not monotone
either side, so it is a shape to look at rather than a rule to bank. NOTHING IS APPLIED.

HIS 4 REVIEW CASES, under his own read:

| the case | side | the gap | the highest ex-fence r above ws3 at the +2 Mage bar | lines above ex-fence |
|---|---|---|---|---|
| 2026-08-29 11:45:00 | LOW | 6 min 05 s | none | 0 of 27 |
| 2026-08-28 15:45:00 | LOW | 8 min 00 s | ws6r 16.75 | 1 of 27 |
| 2026-08-26 21:10:00 | HIGH | 9 min 05 s | ws30r 92.88 | 9 of 27 |
| 2026-08-29 14:48:00 | HIGH | 11 min 05 s | ws28r 87.29 | 11 of 27 |

TWO OF HIS FOUR HAVE NO HIGHER LINE TO FOLLOW. 2026-08-29 11:45:00 has ZERO ex-fence lines above
ws3 at the Mage bar and still took 6 min 05 s, and 2026-08-28 15:45:00 has one. The two HIGH cases
do carry 9 and 11, which is the pattern he describes - so his read fits the two long-gap HIGH
cases and not the two LOW ones.

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
