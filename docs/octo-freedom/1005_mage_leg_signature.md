# The Mage-diff leg signature — six legs tested, 1005

Joe: *"let's test these. if we can't pick a common thread then I'll let the hypothesis go"* —
four new legs, plus the two already seen, one Rig load, one producer (`1005_scoring/mage_leg_test.py`,
output `legtest.out`). No pxs. Raw Mage data and ws1Mage oob/ib crosses only.

## The two terms under test

| term | definition | provenance |
|---|---|---|
| MAGNITUDE | mean \|Mage diff\| on ws8..ws12 between the ws1Mage extrema and the first ib cross | Joe's observation on the 10-04 pm diff table |
| ENGAGEMENT | `tail / ws5` — does the tail move as much as ws5, or decay above it | **MINE**, threshold 0.8 fitted to one event (12:16) |

Event definition unchanged from the 10-04 pm run: one row per ws1Mage oob->ib cross inside the
window, anchored to the most extreme ws1Mage of the run since the previous cross. `rev_wob` = 2
fires on any 2-bar run (171 revs in 75 min on 10-04 pm), so the cross is the dedup key.

## Result — the magnitude term never separates

| leg | events | top by tail | tail | 2nd | sep | ws1 rank-1 | whole rank-1 | 3 agree |
|---|---|---|---|---|---|---|---|---|
| 10-04 am (12:16 = Joe's pivot) | 19 | 12:16 | 8.42 | 8.40 | **1.00x** | 12:16 | 12:16 | YES |
| 10-04 pm (Joe flagged 15:04, 15:18) | 9 | 15:04 | 14.69 | 8.71 | **1.69x** | 15:04 | 15:04 | YES |
| 10-04 05:16 -> 08:30 | 25 | 06:11 | 5.07 | 4.50 | **1.13x** | 07:56 | 07:56 | NO |
| 10-04 00:35 -> 04:00 | 28 | 03:35 | 9.86 | 7.97 | **1.24x** | 03:35 | 03:35 | YES |
| 10-03 09:35 -> 11:30 | 17 | 10:47 | 6.26 | 5.27 | **1.19x** | 09:51 | 10:05 | NO |
| 10-03 05:33 -> 09:00 | 45 | 08:19 | 9.51 | 6.39 | **1.49x** | 08:19 | 08:19 | YES |

- 4 of 6 legs: the three absolute measures agree on one event. 2 of 6 they name different events.
- **0 of 6 legs reach 2x separation** over the 2nd-ranked event.
- 12:16 beats 10:54 by **8.42 vs 8.40 = 0.24%**. "Rank 1 of 19" is true and carries no margin.
- where the three agree, the tail adds nothing over `max |ws1Mage diff|` — same event.

## Result — the engagement term is not a selector

| leg | events | ENGAGED (tail/ws5 > 0.8) | share | ENGAGED with tail < 2.0 | top-tail event's rank on tail/ws5 |
|---|---|---|---|---|---|
| 10-04 am | 19 | 10 | 53% | 4 | **4 of 19** |
| 10-04 pm | 9 | 0 | 0% | 0 | 3 of 9 |
| 10-04 05:16 | 25 | 9 | 36% | 4 | 1 of 24 |
| 10-04 00:35 | 28 | 15 | 54% | 8 | **23 of 28** |
| 10-03 09:35 | 17 | 11 | 65% | 7 | 3 of 17 |
| 10-03 05:33 | 45 | 6 | 13% | 2 | **19 of 45** |

| pooled, 6 legs | value |
|---|---|
| events | 143 |
| ENGAGED | **51 = 36%** |
| correlation(tail magnitude, tail/ws5) | **-0.036** |

- the ratio is a **denominator artefact**. 10-03 11:11: ws5 diff **+0.32**, tail 1.39, ratio **4.38**,
  flagged ENGAGED. ws1 moved +15.51 and ws3/ws4 moved -0.08 / -0.17. Nothing engaged.
- 12 of the 51 ENGAGED events have tail < 1.0.

## Correction to what was reported earlier

The 10-04 am report showed **4 rows** (12:16, 10:54, 10:36, 10:01 — the top 4 by tail magnitude)
and presented `tail/ws5 = 0.94` at 12:16 as the standout. Across all 19 events in that leg
12:16 is **rank 4 on tail/ws5** (12:26 1.22, 12:09 1.13, 11:40 1.08) and **10 of 19 events are
ENGAGED**. The engagement term never isolated 12:16; the 4-row view made it look as if it did.

## Still Joe's to rule

The 4 new legs have no named pivot. The magnitude term's picks are **06:11, 03:35, 10:47, 08:19**.
Whether those are turns is his read, not a measurement in this file.

---

# Joe's eyes on the four picks, and the ws13-23 band he asked for — 1005

| leg | pick | Joe's read |
|---|---|---|
| 10-03 09:35 -> 11:30 | 10:47 | **"is on pivot"** |
| 10-03 05:33 -> 09:00 | 08:19 | **"only 10 minutes late"** |
| 10-04 00:35 -> 04:00 | 03:35 | **"also 10 minutes late"** |
| 10-04 05:16 -> 08:30 | 06:11 | **"not close"** — 10 min earlier would have read as a reversal (sideways for the previous 20 min). *"06:11 might have been overruled if the 13-23 Mages were employed"* |

So 3 of 4 picks land on or within 10 min of the turn. The earlier verdict of "no common thread"
was written against a truncated ladder and without this ground truth.

## THE LADDER WAS MINE AND IT WAS TRUNCATED

| fact | value |
|---|---|
| `rig.tfs` | **1 .. 23** |
| ws13 Mage finite bars | 1,627,248 (07-02 19:56 -> 10-04 23:59) |
| ws23 Mage finite bars | 1,622,940 (07-03 01:55 -> 10-04 23:59) |
| ladder the first run read | **ws1 .. ws12** |
| source of the cut | `range(1, 13)` in `mage_leg_test.py` — mine, not a Joe ruling |

ws13..ws23 were in the Rig the whole time. Nothing had to be built to employ them.

## THE UPPER BAND ws13-23 — it does overrule 06:11

| leg | tail pick | upper ws13-23 at the pick | upper/tail | pick's rank on upper | upper rank-1 | upper max |
|---|---|---|---|---|---|---|
| 10-04 am | 12:16 | 6.02 | 0.72 | **2 of 19** | **10:54** | 6.22 |
| 10-04 pm | 15:04 | 10.19 | 0.69 | 1 of 9 | 15:04 | 10.19 |
| 10-04 05:16 | 06:11 | 4.44 | 0.88 | **2 of 25** | **07:56** | 5.22 |
| 10-04 00:35 | 03:35 | 8.07 | 0.82 | 1 of 28 | 03:35 | 8.07 |
| 10-03 09:35 | 10:47 | 3.86 | 0.62 | 1 of 17 | 10:47 | 3.86 |
| 10-03 05:33 | 08:19 | 7.87 | 0.83 | 1 of 45 | 08:19 | 7.87 |

- **4 of 6 legs**: the upper band confirms the tail pick at rank 1 — including both "10 min late"
  picks and the one "on pivot" pick.
- **06:11 is overruled.** 07:56 takes rank 1 at 5.22 vs 06:11's 4.44 — 07:56 is **17.6% above**.
  07:56 was already ws1's rank-1 event on that leg, so two measures name it and only ws8-12 named 06:11.
- **12:16 is also overruled**, by 10:54 at 6.22 vs 6.02 — **3.3%**. That contradicts Joe's named pivot.

| the overrule margins | value |
|---|---|
| 06:11 loses to 07:56 by | **17.6%** |
| 12:16 loses to 10:54 by | **3.3%** |

A margin between those two keeps 12:16 and overrules 06:11. n = 2. Not anchored to anything.
**OPEN FOR JOE:** does the upper band overrule outright, or only veto past a margin.

## THE "10 MINUTES LATE" IS THE oob FENCE'S ARRIVAL, NOT A RANKING ERROR

There is no event 10 minutes earlier to pick. ws1Mage had not crossed the 85 / 15 fence.

| 10-03, events either side of 08:19 | side | ws1Mage extrema |
|---|---|---|
| 08:02:00 | lo | 14.89 |
| 08:03:25 | lo | -5.20 |
| **08:19:30** | **hi** | **128.17** |
| 08:20:25 | hi | 85.54 |

- 08:19:30 is the **first `hi` event** of the run. The 15.9 min before it carry no event at all.

| 10-04, events either side of 03:35 | side | ws1Mage extrema |
|---|---|---|
| 03:20:00 | lo | 8.85 |
| 03:31:25 | hi | 85.14 |
| **03:35:10** | **hi** | **139.05** |
| 03:39:40 | hi | 86.07 |

- 11.4 min with no event between 03:20:00 and 03:31:25. Nothing exists at ~03:25.

## OVERSHOOT PAST THE FENCE AT THE SIX PICKS — does not separate

| pick | ws1Mage extrema | side | extrema -> ib cross | Joe's read |
|---|---|---|---|---|
| 10-03 10:47:35 | 104.44 | hi | 0.5 min | on pivot |
| 10-04 12:16:40 | -29.03 | lo | 1.3 min | on pivot |
| 10-04 06:11:00 | 101.36 | hi | 2.0 min | not close |
| 10-03 08:19:30 | 128.17 | hi | 0.6 min | 10 min late |
| 10-04 03:35:10 | 139.05 | hi | 3.8 min | 10 min late |
| 10-04 15:04:30 | 134.61 | hi | 3.7 min | flagged, unjudged |

- the two "10 min late" picks carry the two largest overshoots (128.17, 139.05) against 104.44 on pivot
- but 101.36 at 06:11 is "not close", so overshoot alone does not separate. n = 4 judged picks.
- extrema -> ib cross does not separate either: 0.5 min on pivot, 0.6 min 10 min late.

---

# Joe 1005: "the ws1mage-rev at 07:56 isn't dr aligned ... maybe all of your calcs are using a flipped dr?"

## 1. No flip to find — the script reads no dr at all

`mage_leg_test.py` takes every `oob_ib_cross(ws1Mage, 85, 15, boundary_xwob=4)` with no dr test
of any kind. There is no dr term in it to be flipped.

## 2. The dr the WALK receives says -1 at 07:56

| fact | value |
|---|---|
| producer | `report_leash_walk.py:204` -> `walk(lad, mage, **rig.DR**, rig.CC, ...)` |
| rule | `sweep_v3_signal.py:100-106` |
| dr +1 | ws1Mage >= 85 **AND** ws13m >= 85 |
| dr -1 | ws1Mage <= 15 **AND** ws13m <= 15 |
| anything else | **keeps the previous value — it LATCHES** |
| `rig.DR` at 10-04 07:56 | **-1** |

Joe reads +1. The code reads -1. The disagreement is on the dr the live machine consumes.

## 3. THE MECHANISM — a 2.5 minute dip latched dr -1 for 89 minutes

| bar | ws1Mage | ws13m | dr |
|---|---|---|---|
| 07:54:00 | 17.80 | 22.58 | +1 |
| 07:54:30 | 13.90 | 16.66 | +1 |
| **07:55:00** | **14.53** | **15.22** | **-1** |
| 07:56:00 | 1.70 | -3.92 | -1 |
| 07:57:30 | 40.98 | 56.64 | -1 |
| 07:59:00 | 61.80 | 86.20 | -1 |
| **07:59:30** | **78.74** | **107.18** | **-1** |
| 08:02:00 | 74.58 | 96.72 | -1 |

| the -1 latch | value |
|---|---|
| flips to -1 at | **10-04 07:54:55** (ws1Mage 11.99, ws13m 13.80) |
| next change | **10-04 09:24:00** |
| held -1 for | **89.1 min** |
| ws13m peak inside the latch | **111.24** at 07:59:35 — 4.7 min after the flip |
| ws1Mage peak inside the latch | 90.97 at 09:23:55 — 5 s before the latch broke |
| bars inside the latch with ws13m >= 85 | 54 of 1069 |
| bars inside the latch with ws1Mage >= 85 | **3** |

- the flip back to +1 needs BOTH lines >= 85 **on the same bar**. ws1Mage had 3 such bars in 1069.
- ws13m was at 107.18 four minutes after dr went -1. Joe's +1 is what ws13m says.
- **OPEN FOR JOE:** should a 25 s double-dip below 15 latch dr for 89 min. The code does exactly
  what `sweep_v3_signal.py:100-106` says; whether that is the intended dr is his ruling, not mine.

| dr runs, 10-03 + 10-04 | value |
|---|---|
| runs | 62 |
| median run length | 33.5 min |
| longest run | 159.6 min |
| mean share of a run where ws13m sits past the OPPOSITE fence | 8.1% |
| runs where that exceeds 25% of the run | 5 of 62 |

## 4. The alignment census is CIRCULAR — its 94% is not evidence

| pooled, 6 legs | count |
|---|---|
| events | 143 |
| dr-ALIGNED under `rig.DR` | 135 = **94%** |
| ANTI-aligned | 8 = 6% |
| dr == 0 at the extrema | 0 |

- a lo-side ws1mage-rev means ws1Mage <= 15, which is **one of the two conditions for dr -1**.
  The event and the dr are built on the same 85/15 fence on the same line, so alignment is close to
  automatic. 94% measures the shared fence, not a property of the events.
- ws1Mage is the last-arriving input on **32 of 63** dr flips across 10-03 + 10-04, ws13m on 15,
  both on one bar on 16. dr's timing is predominantly set by ws1Mage.
- none of the 8 anti-aligned events is a leg's top pick. Highest is 10-04 02:42, tail 5.10, rank 6
  of 28. **No happy accident there.**

## 5. THE CONSEQUENCE — the 06:11 overrule I reported last turn does not survive

| 10-04 05:16 leg, ranked by upper ws13-23 | upper | side | `rig.DR` |
|---|---|---|---|
| 1 | **07:56** | 5.22 | **lo** | -1 |
| 2 | 06:11 | 4.44 | hi | +1 |
| 3 | 07:21 | 4.11 | hi | +1 |

- 07:56 is the **only** event outranking 06:11 on the upper band.
- under Joe's reading (dr +1 at 07:56, so a hi-side rev is required) 07:56 is anti-aligned and
  disqualified — and the upper band hands the leg straight back to **06:11**, which he called
  "not close". **The ws13-23 overrule evaporates.**
- under `rig.DR` (-1 at 07:56) it is aligned and the overrule stands.
- the overrule therefore rests entirely on which dr is correct at 07:56.
