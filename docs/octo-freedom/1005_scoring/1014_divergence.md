# THE DIVERGENCE CHAIN. 1014. BANKED AND PARKED.

Joe 1014: *"bank the divergence chain and make everything. we'll come back to it in time - right
now it's not printing enough value to compete with main-chain"*.

The main chain reads +13.6487% over 14 legs, 2026-07-17 21:58:00 to 2026-07-20 01:02:15. The best
divergence configuration reads +3.4989% over 10 trades across twelve days. That is the comparison
that parked it.

## THE DIVERGENCE IS THE JIG'S, NOT A REBUILD

`optimus9.analysis.jig.anchor_floater` - Joe's own 0912 four-step spec, already built, with his
words in its docstring. 1014: *"which is my own invention - please don't do that. always check the
Jig before inventing"*, after I answered a divergence question with a peak-finder I had written on
the spot. The peak-finder put the ws2 floater at 2026-07-19 16:45:45; the Jig puts it at 16:23:30,
and Joe's own read was ~16:22.

## THE FOUR ANCHORS TESTED, 2026-07-11 to 2026-07-22, twelve days

| the anchor | lines voting | 2-of-N trades | 2-of-N gross | win rate |
|---|---|---|---|---|
| the ws1cp, tolerance 0 | ws1r, ws1Mage, ws2r, ws2Mage, 3 of 4 | 17 | -1.3332% | — |
| the ws1cp, tolerance 66 bars | the same | 24 | -15.1381% | — |
| ws4Mage oob -> ib, 90 s hold | ws4r, ws4Mage, 2 of 2 | 10 | **+3.4989%** | 70% |
| ws3Mage oob -> ib, 90 s hold | ws3r, ws3Mage | 17 | -2.1473% | 41% |
| ws2Mage oob -> ib, 90 s hold | ws2r, ws2Mage | 26 | -17.0144% | 42% |
| old-school, ws4r target-side extreme holding 240 s | ws4r, ws4Mage | 41 | -11.5515% | 46% |
| old-school, ws3r extreme holding 180 s | ws3r, ws3Mage | 42 | -9.6526% | 52% |
| old-school, ws2r extreme holding 120 s | ws2r, ws2Mage | 63 | -15.3127% | 51% |

Dropping a vote to 1 of 2 loses in every case: -13.5976%, -20.2796%, -18.8787%, -22.9829%,
-20.2796%, -18.8787%.

## THE ONE CONFIGURATION THAT PASSES A HOLD-OUT

The ws4Mage trigger, 2 of 2, is the only mech all session with BOTH halves positive.

| the momentum report | fit, 07-11 to 07-16 | hold-out, 07-17 to 07-22 | both |
|---|---|---|---|
| the banked 7 lines | +1.2899%, 4 trades, 3 / 1 | +2.2089%, 6 trades, 4 / 2 | +3.4988% |
| the halved 4 lines | +1.3637%, 4 trades, 3 / 1 | +1.8972%, 6 trades, 4 / 2 | +3.2609% |

10 trades over 12 days. The fit half's 4 trades cannot carry much, and this is the caveat on the
whole finding.

## THE CONTINUATION AND REVERSAL VOTES

Joe's names, 1014: *"own board is the continuation vote, toward the other is the reversal vote"*.
My "with / against the momentum" was my own coinage and is gone from the code.

| the config | continuation leads | reversal leads | level |
|---|---|---|---|
| ws4Mage trigger, banked 7 | 0 / 1, -0.6893% | 7 / 2, **+4.1881%** | 0 / 0 |
| ws4Mage trigger, halved 4 | 0 / 0, +0.0000% | 6 / 2, **+3.4741%** | 1 / 1, -0.2131% |
| old-school ws4, halved 4 | 7 / 5, -1.1880% | 12 / 14, -10.1878% | 4 / 3, +1.3925% |
| old-school ws3, halved 4 | 6 / 4, +3.7312% | 22 / 16, -8.9214% | 4 / 4, -2.0962% |
| old-school ws2, halved 4 | 4 / 2, -1.1902% | 32 / 27, -11.9896% | 7 / 7, -3.4833% |

THE BUCKET LABEL DOES NOT PREDICT THE OUTCOME, THE ANCHOR DOES. The reversal bucket earns on the
ws4Mage anchor and loses -31.0988% over 123 trades on the three old-school anchors.

## THE DIRECTION GATE IS STRUCTURALLY DEAD UNDER GLOBAL dr

Joe 1014 turned the gate off - *"disable the trade direction gate. eg, if it prints BULLISH, open a
long trade"*. It changed nothing, and the old-school run says why: with global dr setting the
perspective, `anchor_floater` refuses the wrong side of 50, so the verdict and dr carry the same
sign BY CONSTRUCTION. 0 disagreements in 9,656 line-readings across ws4, ws3 and ws2.

On the ws4Mage anchor, where the end the line LEFT sets the perspective instead, there were 8
disagreements in 966 readings. Still near-inert.

## THE MOMENTUM REPORT IS NOW A KNOB

`W_MOM_LINES`, a comma list. Default is the banked seven: ws12, ws15, ws20, ws30, dws8r, dws10r,
dws15r. Joe 1014: *"create a mode in the momentum report that allows for different TFs"*, then
*"reduce each TF by half (eg tf20 becomes tf10)"* and *"int() all of them"*.

The halved set under int() is ws6, ws7, ws10, ws15, dws4r, dws5r, dws7r - and the three dws halves
ARE NOT IN THE CACHE. Only dws8r, dws10r and dws15r exist. A name that cannot be loaded is reported
on the run's own header and skipped, never silently dropped. So the halved report is 4 lines.

## THE ws1cp TOLERANCE, RULED 0

`W_IB_SYNC`, Joe 1014: *"set the sync tolerance to 0 and keep it as a knob"*. 66 bars = 5.5 min was
built on his *"bake the 5.5minute sync tolerance"*; it costs the main chain -11.1082%, +13.6487% to
+2.5405%, because it creates far more cross-backs and fires every close event earlier.

## THE MASK CACHE KEY - A LIVE CACHE-DRIFT FAULT, FIXED

`momo_config` holds thirteen knobs. The mom-true mask's cache key carried ONE of them, `k_window`.
A sweep that moved any of the other twelve would have written a new bank, recomputed nothing, and
loaded the old mask off disk - every combination returning the banked numbers, the sweep reading
flat. The 1008 cache-drift failure in a second place.

FIXED 1014 on Joe's *"go for 1 and 2"*: the key now carries the twelve as a DELTA against the live
bank, so an unchanged bank keys exactly as before and no mask on disk was invalidated.
`python3 machine.py` matches all 14 frozen figures after the change.

## WHAT A SWEEP COSTS, MEASURED

| unit | seconds |
|---|---|
| import machine, including score39's line load | 53.6 |
| machine.build | 1.0 |
| one full chain run after one import | 0.3 |
| one mask, unchanged bank, cache hit | 0.01 |
| one mask, CHANGED bank, recompute | **311.53** |
| a full 33-line mask set at a changed bank | 10,281 s = 2.86 h |

| a 10-hour budget buys | combinations |
|---|---|
| chain knobs only, one import | ~119,800 |
| momo knobs, full 33-line rebuild each | **3** |

THREE LEVERS on that wall, none taken yet: sweep momo on one line only (~115 combos); build the
masks over the 12-day window instead of the whole 1.6M-bar tape (~110, and they multiply with the
first to ~900); or put `momtrue_mask` on the GPU - an RTX 3060 Ti with cupy is on the box and the
speed-up is unmeasured.

## THE SCRIPTS

| file | what it runs |
|---|---|
| `1014_acid.py` | the ws1cp-anchored divergence chain, his acid test |
| `1014_ws4div.py` | the ws{tf}Mage oob -> ib trigger, tf a knob, both vote thresholds |
| `1014_oldschool.py` | the target-side r extreme anchor under global dr |
| `1014_divsweep.py` | the twelve days with the tolerance swept and a hold-out split |
| `1014_strains.py` | one chain versus two |

## THE OPEN THREAD THAT PARKED IT

Joe 1014 on the main chain's own critical path: *"07-22 ~13:37 builds a ws1cp there, but it's only
half way up the hill. the true ws1cp is when ws1x crosses under ws1Mage at 14:06, at the top of the
hill"*.

MEASURED. The cp scan calls `_mode1` only - ws1r and ws1Mage both oob, held 2 bars. `cp2`, the
ws1x/ws1Mage cross mode, EXISTS in `_ibmech` and is called by none of the three scan sites, and
`W_CP_MODE` 'both' never reaches them.

| what | bar | value |
|---|---|---|
| the mode-1 cp the scan stamps | 2026-07-22 13:36:05 | ws1r 93.22, ws1Mage 91.00 |
| the ws1r peak | 2026-07-22 13:37:10 | 98.08 |
| the ws1Mage peak | 2026-07-22 13:39:50 | 111.97 |
| the x-crosses-under nearest his 14:06 | 2026-07-22 14:07:05 | ws1x 92.32, ws1Mage 93.96 |
| ws1r at that bar | — | 71.17, NOT oob, so mode 1 can never stamp there |

AND THE REASON IT IS A BUILD JOB, not a switch: ws1x crosses ws1Mage **57 times** in the 50 minutes
from 13:30 to 14:20, 29 of them under-crosses, the shortest gap 5 s and 8 of them inside one minute
at 13:41. Joe 1014: *"we can't call cp2 until we know which x-cross to take - that's the job we need
to build and test"*.
