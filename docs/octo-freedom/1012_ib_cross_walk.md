# 1012 — THE ws1Mage IB-CROSS WALK

Joe's sampling logic, 1012, measured and then corrected by him twice. The second correction is the
one that made it work.

## THE ENTRY — Joe 1012, verbatim

> the 03:45 signal was created by a high oob ws1Mage to IB cross. it is absolutely a SHORT position

| the cp side | ws1Mage walks | the IB cross is | the trade's TARGET board |
|---|---|---|---|
| HIGH | high oob -> in-fence | a SHORT | **LOW** |
| LOW | low oob -> in-fence | a LONG | **HIGH** |

The trade direction is the OPPOSITE of the cp side. The target board is the opposite of the cp side.
This is [[trade-side-sets-the-target-board]] applied to the cp: the trade heads away from the board
its cp fired on.

## THE DECISION — only at a TARGET-SIDE cp

Joe 1012, on the leg I closed at a same-side cp:

> the 02:17 SHORT trade is targetting a low side OOB (this is in spec, review if needed). 03:45 is
> same-side as 02:17, so it can't be the exit because it is not on the target side

A same-side cp is ignored. At a TARGET-side cp, walk forward to the bar ws1Mage reaches in-fence
held `wob` bars - that bar is the decision bar - and read the FIRST in-fence ws{T}Mage above ws1
over the cp -> decision-bar walk:

| the first in-fence TF above ws1 | the verdict |
|---|---|
| moving TOWARD the cp side, i.e. toward the TARGET board | **RIDE** - the trade continues |
| moving AWAY from it, like ws1Mage | **REVERSE** - the trade closes and the opposite one opens |

CAUSAL: every value is read at or before the decision bar.

## THE BANKED WALK — 07-18, the 02:31:00 SHORT

| bar | event | pxs | the SHORT |
|---|---|---|---|
| 2026-07-18 02:17:15 | the HIGH-side ws1-cp, ws1r 89.68 ws1Mage 99.39 | 0.134828 | — |
| 2026-07-18 02:31:00 | high-oob ws1Mage -> IB, held 24 bars = **ENTRY** | 0.134920 | 0.0000% |
| 2026-07-18 03:45:20 | a HIGH-side cp - SAME side, not the target board, **IGNORED** | 0.135061 | -0.1044% |
| 2026-07-18 04:11:40 | the first TARGET-side LOW cp, ws1r 11.59 ws1Mage 8.95 | 0.134573 | +0.2574% |
| 2026-07-18 04:16:50 | its IB cross, ws1Mage 8.95 -> 18.44 (+9.48 away from LOW) | 0.134431 | +0.3626% |
| 2026-07-18 04:16:50 | ws2Mage 34.66 -> 33.11, **-1.54 TOWARD LOW** -> **RIDE** | — | — |
| 2026-07-18 08:42:55 | the pxs low | 0.127390 | **+5.5809%** |

THE BOARD AT THE 04:11:40 DECISION, cp -> 04:16:50:

| line | at the cp | at the decision bar | move | toward LOW? |
|---|---|---|---|---|
| ws1Mage | 8.95 | 18.44 | +9.48 | no - it is retreating |
| ws2Mage | 34.66 | 33.11 | **-1.54** | **YES - the first in-fence line** |
| ws3Mage | 35.17 | 37.10 | +1.94 | no |
| ws4Mage | 37.65 | 38.56 | +0.91 | no |
| ws5Mage | 41.68 | 42.28 | +0.60 | no |
| ws6Mage | 56.35 | 55.81 | -0.54 | YES |
| ws7Mage | 60.24 | 59.66 | -0.58 | YES |
| ws8Mage | 63.77 | 63.14 | -0.63 | YES |
| ws9Mage | 66.39 | 65.73 | -0.65 | YES |
| ws10Mage | 67.06 | 67.33 | +0.26 | no |

6 of the 9 lines above ws1 point at LOW. ws1Mage's own IB cross looks like a LONG trigger; the
ws2Mage reading is what stopped the reversal.

WHAT EACH CHOICE WAS WORTH, validation only, not an input:

| bar | pxs | RIDE the SHORT from 02:31:00 | REVERSE to a LONG at 04:16:50 |
|---|---|---|---|
| 2026-07-18 04:30:00 | 0.134321 | +0.4439% | -0.2004% |
| 2026-07-18 05:00:00 | 0.133513 | +1.0429% | -0.8009% |
| 2026-07-18 05:42:15 | 0.132542 | +1.7624% | -1.5221% |
| 2026-07-18 06:59:40 | 0.132063 | +2.1171% | -1.8776% |
| 2026-07-18 08:42:55 | 0.127390 | **+5.5809%** | **-5.3499%** |
| 2026-07-18 09:09:00 | 0.127973 | +5.1492% | -4.9172% |

## WHAT THE WRONG SIDE COST, recorded so it is not repeated

My first build used the cp's OWN side for the retest, so the 02:31:00 SHORT closed at the HIGH-side
cp 03:45:20 on a ws5Mage move of -1.93. At that cp **every line ws2-ws10 was falling** - the whole
board heading to the SHORT's target - and the verdict read it as a reason to close.

| the measurement | with the wrong side | with the target side |
|---|---|---|
| the 02:31:00 SHORT | closed 03:45:20, -0.1044% | rides to +5.5809% at the pxs low |
| the whole-tape option-A sweep | net -81% to -143% at every wob | void - built on the wrong side |
| the 3,377-row "95.0% accurate" classification | scored cp -> decision bar, a move already complete | void as an entry signal |

Three readings in a row were void for the same reason: the side. The relationship Joe spotted was
real in all of them; only the direction convention was wrong.

## STILL OPEN

| open point | detail |
|---|---|
| the IB-cross wob | 24 bars = 120 s here. Swept 1..24 under the WRONG side, so the sweep says nothing. Needs re-running on the target side |
| a minimum on the TF's move | the -1.54 that produced RIDE is small. No level set, and one leg cannot anchor one |
| two cps resolving to one decision bar | a known defect in my sweep code - the later cp's verdict won by loop order. Not yet fixed |
| a verdict of none | when no ws2-ws10 Mage is in-fence at the cp there is no verdict. 7 of 3,377 cps. Unhandled |

## THE CONFIGURATION, BANKED 1012

| setting | value | Joe's words |
|---|---|---|
| the entry | a ws1-cp's ws1Mage oob -> IB cross. HIGH cp = SHORT, LOW cp = LONG | *"a high oob ws1Mage to IB cross ... is absolutely a SHORT position"* |
| the target board | the opposite side from the entry cp | *"the 02:17 SHORT trade is targetting a low side OOB"* |
| which cps decide | TARGET-side only. Same-side cps are ignored | *"03:45 is same-side as 02:17, so it can't be the exit"* |
| the line | the FIRST in-fence ws{T}Mage above ws1, read AT THE cp BAR | — |
| the reading | its move from the cp bar to the IB bar. Toward the target = RIDE, away = REVERSE | — |
| the reference | **the cp**, not the line's window peak | *"the reference is the cp"* |
| the ceiling | **ws30**. Ladder above ws1 is ws2..ws24, ws30 | *"lets make 30 the ceiling"* |
| silence | **RIDES** | *"silence rides ... that weakness shows up on the Mage scan at at least one ws1-cp-ib event per leg"* |
| cp dwell | 4 bars = 20 s | 1012, W_CP_DWELL |
| IB-cross wob | 24 bars = 120 s | — |
| two cps on one IB bar | the earlier cp's verdict stands | mine, stated |
| a retest past the IB bar | 5 min is acceptable, 10 min is not | *"I was ok with 5min past ws1cp, but I feel that 10min is pushing it too far"* |

THE LADDER. Joe 1012: *"the lines run from g5 to ws24, then 30,45,60,90"*. The cache also holds
ws25-ws29 and ws120, which are NOT in the design and are excluded. g5, g15 and g30 exist
sub-minute; they sit below ws1 so they are never scan candidates.

## THE THREE LEGS UNDER THAT CONFIGURATION

| leg | entry | close | made | net after 0.22% drag | ran min | rides | silences |
|---|---|---|---|---|---|---|---|
| 07-17 21:58:00 LONG | 2026-07-17 21:58:00 | 2026-07-18 01:19:05 | +0.8453% | +0.6253% | 201.1 | 0 | 0 |
| 07-18 02:31:00 SHORT | 2026-07-18 02:31:00 | 2026-07-18 11:07:00 | +4.7330% | +4.5130% | 516.0 | 2 | 3 |
| 07-18 08:46:55 LONG | 2026-07-18 08:46:55 | 2026-07-18 16:41:00 | +0.2278% | +0.0078% | 474.1 | 2 | 0 |
| TOTAL | — | — | **+5.8061%** | **+5.1461%** | 1191.2 | 4 | 3 |

## THE GIVE-BACK, AND ITS NAMED CAUSE ON ONE LEG

| leg | peak | close | given back |
|---|---|---|---|
| 07-17 21:58:00 LONG | +1.1435% at 2026-07-18 01:14:00 | +0.8453% | 0.2982% |
| 07-18 02:31:00 SHORT | +5.5809% at 2026-07-18 08:42:55 | +4.7330% | 0.8479% |
| 07-18 08:46:55 LONG | +1.1811% at 2026-07-18 14:53:10 | +0.2278% | 0.9532% |

The 08:46:55 LONG's peak at 2026-07-18 14:53:10 HAS NO ws1-cp. Joe called it before it was measured.
ws1r reaches 89.74 at 14:53:00, clear of the 85 line; ws1Mage tops at 80.82, **4.18 short of it**. The
pair never both reach high oob between 14:45 and 15:05, so no mode-1 cp can form and the peak cannot
be read. The next three cps - 15:15:15, 15:16:55, 15:58:50 - are all LOW side, same-side for this
LONG, so all three are ignored. The trade ran 107.8 min past its high.

## THE PATH THE cp REFERENCE CANNOT SEE — recorded, ruled against

At the 2026-07-18 12:02:15 cp, the cp->IB diff read **+35.95 on ws6**, the strongest line on the
board, and **24 of 24 lines positive**. Measured from each line's own peak inside that window,
**24 of 24 were negative**: ws6 topped at 103.34 at 12:12:50 and was 86.94 at the 12:15:45 IB bar.
23 of the 24 lines share a peak bar of 12:06:45, nine minutes before the IB bar, and pxs peaked
there too at +1.0899% against +0.5135% at the IB bar.

Joe ruled the reference stays the cp. Recorded because the diff and the path disagree completely on
that bar, and a peak->IB reference would have REVERSED that decision.
