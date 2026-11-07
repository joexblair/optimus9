# the momentum petri dish — the first result. 2026-11-05

HIS FRAMING: *"all we need the mech to do is to decide if it has enough momentum to walk to an
ex-20/80 r-line, who will carry using our established mech"* / *"I think we can work with the lower
mages"* / *"forge ahead - let's get that monies"*.

Jig: `docs/octo-freedom/1022_v4/out/momo_dish.py`. Output: `dish_full.out`, 416 rows, 246 s.
Population: the four lower Mage rungs' sweep-pivot legs over the whole 94.5-day tape, de-overlapped.
Label: HOW MANY of ws4r..ws30r - step 1's own carrier set - reach the fence inside the leg, 0 to 27.
Score: each feature split at ITS OWN median; the separation is the drop in zero-carrier legs.

## THE RANKING, ON THE ROW WITH THE MOST HEADROOM

ws1Mage, closed-prev, 15/85, LOW. 2,251 de-overlapped legs. The label's own numbers: 31.1%
zero-carrier legs, median 2 carriers, p90 12.

| the feature | its median | legs below | zero-carrier below | median carriers below | legs at or above | zero-carrier above | median carriers above | separation |
|---|---|---|---|---|---|---|---|---|
| n_rpred | 1 | 1071 | 49.8% | 1 | 1180 | 14.2% | 4 | **+35.6** |
| n_mage_above_x | 13 | 1056 | 13.3% | 4 | 1195 | 46.9% | 1 | **-33.6** |
| n_pinned | 10 | 1115 | 45.2% | 1 | 1136 | 17.3% | 4 | **+27.9** |
| n_momo | 5 | 1064 | 37.0% | 1 | 1187 | 25.8% | 3 | +11.3 |
| n_mage_above_r | 14 | 1084 | 25.8% | 3 | 1167 | 36.0% | 1 | -10.2 |
| sum_mage_minus_r | 35.194 | 1125 | 26.5% | 2 | 1126 | 35.7% | 1 | -9.2 |
| mean_d1 | 0 | 63 | 36.5% | 1 | 2188 | 30.9% | 2 | +5.6 |
| n_mdiff_grew | 0 | 0 | - | - | 2251 | - | - | no split |
| max_d1 | 0 | 0 | - | - | 2251 | - | - | no split |
| n_hinge | 0 | 0 | - | - | 2251 | - | - | no split |

The same row on EMERGING: n_pinned +29.4 (39.1% -> 9.7%, median 1 -> 6), n_momo +16.3,
n_mage_above_x -27.9, n_mage_above_r -11.5, n_mdiff_grew +1.9, n_rpred no split.

## FOUR FINDINGS

### 1  r-pred wins on its own read and its own fence

+35.6 at ws1Mage closed-prev 15/85, both sides. 15/85 is `predict_breach`'s native boundary
(BOUNDARY_HI 85 / BOUNDARY_LO 15), so this is r-pred answering the question it was built for. On
EMERGING it does not split at all - its median flag count is 0 there.

### 2  HIS CRUDE RULE IS INVERTED, AND THE Mage-vs-x FORM IS 3x STRONGER

n_mage_above_x separates -33.6: FEWER carriers with the slow %B beyond the fast %B toward the fence
predicts MORE carriers reaching it. 13.3% zero-carrier below the median against 46.9% above, median
4 carriers against 1.

n_mage_above_r is the same sign at -10.2, and sum_mage_minus_r at -9.2.

THE MECHANISM IS HIS OWN TAIL LOGIC. `Mage` is %B over 38 bars and `x` is %B over 5. When the slow
line is already far beyond the fast one toward the fence the move is MATURE - the slow has arrived
and the fast has pulled back. When the fast leads, the move is YOUNG and the slow has yet to follow.
A fast line ahead of a slow one means the move is still coming, which is the matryoshka read applied
to one timeframe's own pair.

So his *"if Mage is higher than r, then momentum is expected"* has the right pair and the wrong
sign for THIS label. HIS CALL on what that means for the rule.

### 3  n_pinned - his flattening idea - is second, and it wins on emerging

+27.9 on closed-prev and +29.4 on emerging, and on emerging it sorts the LIVE legs best of any
feature: median 1 carrier below the split against 6 above. A line pinned at its sampled extreme has
its move unspent.

### 4  THE HINGE CANNOT BE MEASURED AT A 5-SECOND BAR

n_hinge's median is 0 of 27 on both reads: at the typical decision bar, NO carrier shows a one-bar
velocity reduction. On closed-prev the staircase is flat between seams, so `abs(r0-r1) <
abs(r1-r2)` compares two zeros. max_d1 and n_mdiff_grew degenerate the same way on closed-prev.

Lane's hinge needs the line's OWN bar, not the 5 s grid. That is the same staircase fault that
makes the live momentum verdict sample 2.40 times per closed-prev step at ws12r.

## WHAT THIS DOES NOT SAY

- no feature was COMBINED with another. Every number above is one feature alone.
- the separation is measured on the de-overlapped legs only, which is the honest episode set.
- nothing is wired into any machine. The dish reads; it decides nothing.

## THE VOTE — the three signals added up. 1105, step 3

Each of the three that separated votes "carry" when it sits on the carry side of ITS OWN median -
the side the dish measured, so the fast-versus-slow pair votes on the LOW side because its
separation was negative. NO NEW VALUE: the medians are the data's and the vote is a count.

ws1Mage, closed-prev, 2,251 de-overlapped legs:

| the fence | side | votes | legs | zero-carrier legs | median carriers | p90 |
|---|---|---|---|---|---|---|
| 15/85 | LOW | 0 | 660 | 57.3% | 0 | 3 |
| 15/85 | LOW | 1 | 486 | 39.3% | 1 | 7 |
| 15/85 | LOW | 2 | 429 | 18.9% | 3 | 12 |
| 15/85 | LOW | 3 | 676 | **7.4%** | **6** | 16 |
| 15/85 | HIGH | 0 | 610 | 59.2% | 0 | 3 |
| 15/85 | HIGH | 1 | 518 | 37.5% | 1 | 7 |
| 15/85 | HIGH | 2 | 449 | 25.2% | 2 | 10 |
| 15/85 | HIGH | 3 | 674 | **8.8%** | **6** | 16 |
| 20/80 | LOW | 0 | 660 | 40.6% | 1 | 5 |
| 20/80 | LOW | 1 | 486 | 18.3% | 3 | 11 |
| 20/80 | LOW | 2 | 429 | 8.4% | 5 | 15 |
| 20/80 | LOW | 3 | 676 | **2.2%** | **9** | 20 |

The 3-vote row across all four lower rungs, closed-prev, 15/85, LOW:

| the Mage line | legs at 3 votes | zero-carrier | median carriers | the row's base rate |
|---|---|---|---|---|
| ws1Mage | 676 | 7.4% | 6 | 31.1% |
| ws2Mage | 448 | 4.9% | 8 | 16.6% |
| ws3Mage | 353 | 4.2% | 12 | 10.8% |
| ws5Mage | 216 | 0.9% | 15 | 4.9% |

MONOTONE EVERYWHERE AT 0 -> 3 EXCEPT ONE STEP: ws3Mage reads 18.0% at 2 votes against 13.9% at 1,
and 9.0% against 7.2% at 20/80. So the 1-to-2 step is not monotone on that rung. The 3-vote row is
clean on every rung.

## WHAT THE VOTE SAID AT 2026-08-07 08:58:00 — HIS TARGET BAR

| the signal | its value | the median it is scored against | its vote |
|---|---|---|---|
| r-pred flags | 3 of 27 | 1 | CARRY |
| the fast-versus-slow pair | 6 of 27 | 13 | CARRY |
| pinned at their extreme | 3 of 27 | 10 | no |

TWO OF THREE. So a gate at 3 votes does NOT hold that leg, and a gate at 2 does. The clean
threshold is the one that fails his bar, and the one that saves his bar is the muddy one.

WHAT ACTUALLY HAPPENED THERE: 8 of 26 eligible carriers reached 15/85 by the ws1Mage leg's own
close, 65 minutes later, climbing ws5 -> ws12 in order. The 2-vote row's median is 2 carriers, so
the vote pointed the right way and UNDER-called the size.

## THE LIMIT THIS RESULT HAS, AND IT IS LOAD-BEARING

The dish scores the LEG'S OPEN bar. The gate would sit at the fdm2-wsxcad-director's truncation
bar, mid-walk. THOSE ARE DIFFERENT BAR POPULATIONS, so the medians measured here may not transfer.
Settling it needs the dish re-pointed at director truncation bars, which is a measurement and not a
conclusion.

## HANDOVER — 1106, where this stands

### HIS RULINGS SO FAR ON THE MOMENTUM GATE

| what he settled | his words |
|---|---|
| the gate's bar | the fdm2-wsxcad-director's truncation bar - *"is this the bar where the new momentum mech tests for votes"* / yes |
| what the vote winning produces | **NOTHING**. *"no new trade is opened if the momentum votes win: the incoming trade simply continues walking forward"* - no close, no open, no router signal |
| where the trade goes then | *"continues the trade's walk forward to an ex-20/80-fence bar"*. That is the PURPOSE, not a new end condition: once a carrier is ex-20/80, step 1 counts it at the next cadence event and the established mech takes over |
| the lower Mage rungs | *"I think we can work with the lower mages"* |
| the label | *"decide if it has enough momentum to walk to an ex-20/80 r-line, who will carry using our established mech"* - board level, over step 1's own carrier set |
| the MAE 1.10% stop | NOT a consequence of this change. *"isn't that just the normal state for any trade?"* - it is standing state, and my calling it a consequence put a sign on a neutral fact |

### STILL HIS, TWO QUESTIONS

| # | the question | my reading, which he has not confirmed |
|---|---|---|
| 1 | if the director's test passes AGAIN later in the same walk, does it truncate then | it can truncate at a later pass. One-shot veto |
| 3 | is the vote read only where the director wants to truncate, or at every bar of its walk | only where it wants to truncate |

Question 1 matters on 2026-08-07: ws5r reached 15/85 at 09:05:00 and the director's walk ends at
09:05:10, so a later pass that still truncates kills the leg short of the carrier.

### IN FLIGHT

`docs/octo-freedom/1022_v4/out/trunc_dish.py` - ONE continuous chain over the whole 94.5-day tape
through v4_fdm2.legs, harvesting every director truncation bar with its own leg's side, then reading
the three signals there. It prints the truncation medians BESIDE the leg-open medians so the shift
is a number. Started 2026-11-06 00:54. Output: `/home/joe/.claude/jobs/7c82535c/tmp/trunc.out`.

WHY IT IS NEEDED: momo_dish scored the LEG'S OPEN bar and the gate reads a truncation bar. Those are
different bar populations, so the vote floor cannot be chosen off the first dish.

### WHAT THE REPORT OWES HIM WHEN IT LANDS

| the column | what it holds |
|---|---|
| the truncation bars where the vote holds | the count |
| where each of those legs ends instead | which of the five endings - a later director truncation, the next cadence event, the ws10x fallback, the day's end, the stop |
| the realised figure per ending | the number, no adjective |
| the carriers reached from the overruled bar | against the leg's own exit and the ws1Mage leg open there |

### UNCOMMITTED ON DISK

- `docs/octo-freedom/1022_v4/out/momo_dish.py`
- `docs/octo-freedom/1022_v4/out/trunc_dish.py`
- `docs/octo-freedom/1105_momo_dish.md`

He banked the 08:26 work explicitly and has not asked for this to be committed, so it sits.

## fdm2-momo — HIS NAME, 1106. His wiring, and the measurement that backs it

HIS WORDS: *"my idea for wiring: we need to see fdm2-momo (the new mech's name) fire only once when
we're cad walking, then we know we're safe to walk to a ex-20/80-fence bar without being
rev-traded"*.

### IT WORKS ON EMERGING, AT THE CAD WALK'S FIRST BAR

The cad walk on the 2026-08-07 08:26:10 LONG runs 08:55:10 to 09:05:10. The director truncated at
08:57:55. Every bar of that walk, the three signals and the vote on the 417-truncation-bar medians:

| the bar | the read | r-pred | fast-vs-slow | pinned | votes |
|---|---|---|---|---|---|
| 08:55:10 | closed-prev | 4 | 6 | 21 | 2 of 3 |
| 08:55:10 | emerging | 3 | 0 | 21 | **3 of 3** |
| 08:56:10 | closed-prev | 3 | 6 | 23 | 2 of 3 |
| 08:56:10 | emerging | 3 | 0 | 23 | 3 of 3 |
| 08:57:10 | closed-prev | 3 | 6 | 15 | 2 of 3 |
| 08:57:10 | emerging | 0 | 1 | 15 | 3 of 3 |
| 08:58:10 | closed-prev | 3 | 6 | 2 | 1 of 3 |
| 08:58:10 | emerging | 0 | 2 | 2 | 2 of 3 |
| 08:59:10 | closed-prev | 3 | 6 | 7 | 2 of 3 |
| 08:59:10 | emerging | 0 | 3 | 7 | 3 of 3 |
| 09:00:10 | closed-prev | 2 | 3 | 11 | 3 of 3 |
| 09:00:10 | emerging | 0 | 4 | 11 | 3 of 3 |
| 09:01:10 | closed-prev | 2 | 3 | 10 | 3 of 3 |
| 09:02:10 | closed-prev | 2 | 3 | 20 | 3 of 3 |
| 09:03:10 | emerging | 6 | 0 | 26 | 3 of 3 |
| 09:05:10 | emerging | 4 | 1 | 26 | 3 of 3 |

| the read | first bar in the cad walk scoring 3 of 3 | first scoring 2 or more |
|---|---|---|
| closed-prev | 2026-08-07 09:00:00 | 2026-08-07 08:55:10 |
| emerging | **2026-08-07 08:55:10** | 2026-08-07 08:55:10 |

SO HIS PLACEMENT HOLDS. On emerging, fdm2-momo fires 3 of 3 on the cad walk's FIRST bar, 2 min 45 s
before the director truncated. A one-shot latch set there overrules the 08:57:55 truncation.

### CORRECTION TO MY OWN READING

I said the board *"spends its pinned state during the director's own race and walk - 21 of 27 down
to 6"*. That was two points. The full series is 21, 23, 15, 6, 2, 7, 11, 10, 20, 26, 26, 26 - a DIP
four bars wide, not a decay. The pinned count recovers to 26 of 27 by 09:03.

THE DIRECTOR TRUNCATED INSIDE THE DIP. 08:57:55 sits between the 15 at 08:57:10 and the 2 at
08:58:10. Both reads are of the same momentary let-go, which is why the truncation test and the
pinned trough coincide - and why a latch set BEFORE the dip survives it.

### STILL HIS, TWO QUESTIONS

| # | the question | the candidates |
|---|---|---|
| 1 | what ends the latch when no carrier arrives - 53.5% of the 417 truncation bars have none by the ws1Mage leg's close | the cad walk's own end, the next cadence event, the carrier arriving, the stop |
| 2 | "once" per cad walk, per cadence event, or per leg | the 06:48:10 SHORT had two cadence events 3h24m apart, so these are different machines |

### WHAT HAS NOT BEEN MEASURED

08:51 was HIS pick because it was the highest bar before price fell into 08:58, so it is the best
case and not a sample. The run that settles fdm2-momo is the same vote read at the FIRST BAR of
every one of the 417 cad walks, carried to each one's own truncation, with the carrier outcome
beside it. That tells us how often fdm2-momo fires on a leg that goes nowhere.

## fdm2-momo MEASURED OVER THE TAPE — 1106. The split that changed the reading

`docs/octo-freedom/1022_v4/out/momo_latch.py`, one continuous chain through v4_fdm2.legs, 2,199 s.
The harvest is cached to `latch_cache.json` so the next question costs seconds.

| the population | value |
|---|---|
| legs on the tape | 1,286 |
| director truncations | 417 |
| of those WITH a cad walk - the population his wiring covers | **220** |
| of those firing on the ws1 seam+15s bar with NO walk | **197, 47.2%** |
| the truncation IS the leg's exit | **100.0% of all 417**, median 5 s later |

### THE WITH-WALK POPULATION, WHICH IS THE ONE THAT COUNTS

| the read | votes | cases | fires | carriers reaching 15/85 after the truncation, median | zero-carrier | p90 | median lead, s |
|---|---|---|---|---|---|---|---|
| emerging | 1 | 59 | no | 1.0 | 39.0% | 4 | 125 |
| emerging | 2 | 43 | no | 1.0 | 34.9% | 9 | 260 |
| emerging | 3 | 118 | **yes** | 2.0 | **22.9%** | 11 | **272** |
| closed-prev | 0 | 7 | no | 1.0 | 42.9% | 1 | 50 |
| closed-prev | 1 | 65 | no | 0.0 | 63.1% | 4 | 200 |
| closed-prev | 2 | 84 | no | 0.0 | 51.2% | 9 | 270 |
| closed-prev | 3 | 64 | **yes** | 1.0 | 39.1% | 7 | 282 |

EMERGING IS CLEAN AND MONOTONE: 39.0 -> 34.9 -> 22.9. CLOSED-PREV IS NOT - its 0-vote row reads
42.9% against 63.1% at one vote, and the 0-vote row is 7 cases. So emerging is the read.

fdm2-momo fires on 118 of the 220 with-walk cases, a median 272 s = 4 min 32 s before the
truncation it would overrule.

### CORRECTION TO MY OWN READING

I reported that *"the legs fdm2-momo would overrule are already the best-realising legs"*, median
+0.709. THAT CAME FROM THE MIXED TABLE. Split, the pattern lives in the NO-WALK cases and not in the
population his wiring covers:

| had a cad walk | the read | votes | cases | realised %, median | MAE %, median | MFE %, median |
|---|---|---|---|---|---|---|
| yes | emerging | 1 | 59 | +0.436 | 0.380 | +1.167 |
| yes | emerging | 2 | 43 | +0.682 | 0.506 | +1.729 |
| yes | emerging | 3 | 118 | +0.548 | 0.448 | +1.175 |
| yes | closed-prev | 1 | 65 | +0.625 | 0.335 | +1.234 |
| yes | closed-prev | 2 | 84 | +0.585 | 0.474 | +1.328 |
| yes | closed-prev | 3 | 64 | +0.562 | 0.458 | +1.257 |
| no | closed-prev | 2 | 58 | +0.711 | 0.374 | +1.299 |
| no | closed-prev | 3 | 18 | **+1.298** | 0.424 | +1.754 |
| no | emerging | 3 | 43 | +0.726 | 0.446 | +1.300 |

On the with-walk rows the realised figure is FLAT across the vote: +0.436, +0.682, +0.548. So
fdm2-momo is not selecting the already-best legs there.

### THE ROOM THE LATCH IS AIMING AT

At 3 votes, with a cad walk, emerging: MFE +1.175 against realised +0.548 - **0.627 of MFE left on
the table at the truncation**, with a median 2 carriers still reaching 15/85 afterwards.

### WHAT IS STILL UNBUILT

Where an overruled leg ENDS instead. Every one of the 417 truncations is its leg's exit, so there is
no held-on outcome anywhere on the tape to read. It needs the latch wired into v4_fdm2.walk and the
fdm2 chain re-run as an A/B. That is a change to the live machine and it is proposed, not applied.

## THE fdm2-momo A/B — 1106. POSITIVE NET, AND NOT FOR THE REASON IT WAS BUILT

`docs/octo-freedom/1022_v4/out/momo_ab.py`. One process, one tape load, a continuous chain per arm
over the whole 94.5 days. Arm A is the banked machine, FDM2_MOMO_ON 0. Arm B is FDM2_MOMO_ON 1,
FDM2_MOMO_VOTES 3, FDM2_MOMO_READ emerging, medians 0 / 7 / 9.

| the total | arm A, the banked machine | arm B, fdm2-momo on | the move |
|---|---|---|---|
| legs | 1286 | 1251 | -35 |
| stopped | 612 | 602 | -10 |
| gross % | -40.179 | -17.822 | **+22.357** |
| drag % | -253.985 | -247.073 | +6.912 |
| net % | **-294.164** | **-264.894** | **+29.270** |
| MAE % total | 984.989 | 954.102 | -30.887 |
| MFE % total | +1500.744 | +1498.090 | -2.654 |
| MFE captured | -2.7% | -1.2% | +1.5 |

BOTH ARMS LOSE. Gross is negative in both, -40.179 and -17.822, and the drag is -253.985 and
-247.073. The drag is the dominant term by a factor of six over gross.

### WHERE THE +29.270 ACTUALLY COMES FROM

| the differing legs | count | realised in A, total | realised in B, total |
|---|---|---|---|
| in both arms, B held LONGER | 28 | +32.523 | **+25.974** |
| in both arms, B held SHORTER | 114 | +91.399 | **+106.391** |
| only in arm A | 226 | -11.824 | - |
| only in arm B | 191 | - | +2.072 |

| arm A-only legs by exit kind | count | realised total |
|---|---|---|
| rev-trade | 125 | +99.276 |
| STOP at 1.10% | 101 | **-111.100** |

| arm B-only legs by exit kind | count | realised total |
|---|---|---|
| rev-trade | 109 | +92.272 |
| STOP at 1.10% | 82 | **-90.200** |

THE DESIGNED EFFECT LOST MONEY. The 28 legs that B held LONGER - the thing the latch is for - went
from +32.523 to +25.974, a loss of 6.549.

THE GAIN IS CHAIN RE-ROUTING. 114 legs ended EARLIER in B and gained 14.992; dropping arm A's
226 unique legs recovered 11.824; arm B's 191 unique legs added 2.072. The sum is +22.339, which is
the gross move. 19 net fewer stops - 101 against 82 among the unique legs - is where most of it sits.

SO THE A/B IS POSITIVE AND IT IS NOT EVIDENCE THAT THE MOMENTUM READ WORKS. Refusing one rev-trade
re-sequences every leg after it, and the re-sequenced chain happens to meet fewer stops. 1,060 of
the leg opens are shared; 417 are not.

### WHAT THAT MEANS FOR THE NEXT STEP

The designed effect and the measured gain point in opposite directions. Testing the mech rather than
the reshuffle needs the 28-leg group isolated - hold the leg longer and change NOTHING else about
the chain's sequence - which is a different experiment from this one.
