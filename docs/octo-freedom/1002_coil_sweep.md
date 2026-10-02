# 1002 — the coil's timeframe set does not select entries, and the 7-day baseline stops 54.7%

Joe asked: *"sweep the TFs that create the coil to see if there is potential improvement in the list
of trades showing in o9-live. use gcws30 to ws8"*, with the hypothesis: *"a different coil would have
a benefit at entry by dropping the trades that were triggered on a smaller TF"*, and
*"I'm fine to move our working window to 09-25 to 10-01 (full days)"*.

**THE HYPOTHESIS CANNOT BE TESTED THROUGH `coil_lines`. THE KNOB IS INERT FOR ENTRY SELECTION.**

## WHAT WAS SWEPT

| | |
|---|---|
| candidates | every **contiguous** range of the ordered ladder `[gcws30, ws1..ws8]` = **45 sets**. Contiguous, not all 511 subsets, because the hypothesis is about shifting the coil UP the ladder |
| window | **09-25 .. 10-01**, 7 full days, 120,960 bars, **0 missing klines** |
| tape | rebuilt at `TAPE_END` **2026-10-02 00:00** — the previous end was 09-30, so 09-30 and 10-01 sat outside it. 92 lines (ws1..ws23 x m/Mage/r/x) built in 148 s, 0 missing. Old cache keys untouched |
| CC per set | `sum over keys of ((m + Mage)/2 - r)` at dr=1 — exactly as `Rig.__init__` builds it (`sweep_v3_signal.py:134-136`). The walk applies the arm's dr |
| scoring | run-first bars -> `trade_walk.walk(opens, rig.DR, rig.px, ..., mae_cap 0.70)` -> `measure_live_stop.score` |

## THE RESULT: 45 SETS, ONE ANSWER

| metric | distinct values across all 45 sets |
|---|---|
| mech bars | **1** -> 20,496 |
| `WALK FIRES FROM` | **1** -> 228 |
| trades | **1** -> 139 |
| stopped | **1** -> 76 |
| MFE>MAE | **1** -> 62 |
| score | **1** -> +31.148 |

## IT IS NOT A BUG. THE COIL MOVES THE TURN AND THE GATE DOES NOT NOTICE

`gcws30` alone against `ws8` alone, on 09-25:

| check | result |
|---|---|
| CC arrays identical? | **False** |
| max \|CC diff\| over the day | **129.01** |
| run-first bars where the **TURN BAR differs** | **27 of 39** |
| emitted-bar sets identical? | **True** |

**The timing is the whole explanation:**

| coil set | `turn − arm` (bars) | `qualify − arm` (bars) |
|---|---|---|
| `gcws30` | min 1, **med 1**, max 3 | min 7, **med 14**, max 64 |
| `ws8` | min 1, **med 4**, max 8 | min 7, med 14, max 64 |
| `gcws30+ws1` | min 1, med 1, max 3 | min 7, med 14, max 64 |

- the gate needs the turn AND the qualify (`leash_walk.py:170-171`). The turn lands at arm+1..arm+8; the qualify never before arm+7, median arm+14.
- **so the qualify alone decides when the gate opens.** Moving the turn by up to 7 bars changes nothing.
- `qualify − arm` is identical across sets, as it must be: the momTF bucket reads no coil.
- the turn's max (8) does exceed the qualify's min (7), so they CAN cross in principle. Over 39 episodes on 09-25 no crossing changed an emitted bar.

**WHAT WOULD MAKE THE COIL SELECT.** The turn would have to become a CONSTRAINT rather than a gate
that is already open — the turn required AFTER the qualify, or within N bars of it. That is a mech
change and it is Joe's. Nothing here proposes one.

## THE 7-DAY BASELINE, WHICH IS THE BIGGER NEWS

`coil_lines` `['gcws30','ws1']`, 09-25..10-01:

| | 7 days, 09-25..10-01 | the banked 09-01 UNION |
|---|---|---|
| trades | **139** | 13 |
| stopped | **76 = 54.7%** | 3 = 23.1% |
| MFE>MAE | 62 = 44.6% | 10 = 76.9% |
| score | +31.148 | +15.642 |
| **per trade** | **+0.2241** | **+1.2032** |

- **effective-n: 139 trades over 7 days.** The 13-trade day was not representative.
- the live run agrees with the 7-day figure, not the one-day one: 14 of 20 o9-live trades went past the 0.70% stop.
- **NOT a like-for-like comparison of the scores:** the 09-01 UNION included Joe's 5 lazy-g timestamps, which are not in the run-first population swept here. The per-trade and stop-rate columns are the comparable ones.

## WHAT THIS DOES NOT MEASURE

- the live bars themselves. o9-live traded 10-02 01:45..18:44, which is still outside the rebuilt tape (ends 10-02 00:00). A further `TAPE_END` move would cover them.
- **why 54.7% stop.** The stop rate is the finding; its cause is not in this sweep. The 0.70% cap is `mae_cap` from `wsf_trade_config`, and whether the signal is early, the stop is tight, or the regime changed is unmeasured.
- any coil set OUTSIDE the contiguous ranges. 466 of the 511 subsets were not run — but since all 45 contiguous sets, including every single line alone, give one identical answer, a non-contiguous set changing it would need the turn to start binding, which the timing above rules out.
