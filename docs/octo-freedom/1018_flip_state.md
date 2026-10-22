# 1018 — where the trade-flip stands, and what is uncommitted

Written at the sign-off before octo-v3 dev starts. Numbers only; no ruling is made here.

Joe 1018: *"take the night off. tomorrow we'll start dev on a octo-v3"*

Joe 1018: *"octo-v3 is greenfield - we're going back to basics"*

**THIS DOC IS A RECORD, NOT AN INHERITANCE.** octo-v3 carries nothing over from octo2 - no mech,
no knob, no default, no `_ruled.py` entry - unless Joe names it.

## 1. The arm every number below was measured on

| knob | value | what it is |
|---|---|---|
| `W_OCTO2_FLIP` | 1 for the measurement, **0 in the code** | the trade-flip mech. NOT banked |
| `W_OCTO2_FIRE` | `verdict` | the fill bar = the OPEN bar itself, so every wait is 0 s |
| `W_OCTO2_MAE_CAP` | 1.60 | the stop, % adverse. Banked 1017 |
| `W_VOTE_MIN` | 2 | objections that KILL a flip. Raising it makes MORE flips |
| drag | 0.1975 | % per trade. Banked |
| tape | 1,632,960 bars | 94 days, 2026-07-03 to 2026-10-04 |

## 2. The flip's own net, whole tape

| the group | trades | stopped at the cap | total net | net per trade | positive rows |
|---|---|---|---|---|---|
| FLIPPED | 1078 | 223 | -257.7610% | -0.2391% | 379 (35.2%) |
| not flipped | 1090 | 305 | -32.4519% | -0.0298% | 598 (54.9%) |
| all | 2168 | 528 | -290.2129% | -0.1339% | 977 (45.1%) |

| the direction | count | net | net per trade |
|---|---|---|---|
| a printed SHORT became a LONG | 502 | -122.2105% | -0.2434% |
| a printed LONG became a SHORT | 576 | -135.5505% | -0.2353% |

Both directions lose at the same rate, so the loss is not a side-polarity error.

## 3. `W_VOTE_MIN` is the flip count's control

| `W_VOTE_MIN` | flips | NET (cap-loss) |
|---|---|---|
| 1 | 163 | -80.7044% |
| 2 | 1076 | -295.3221% |
| 3 | 2343 | -610.3076% |
| 4 | 2494 | -663.2986% |

## 4. The sweep, 13 arms, `oobdiv` unless named

| the arm | trades | stopped | flipped | NET cap-loss |
|---|---|---|---|---|
| flip OFF — the 1017 bank | 1624 | 464 | 0 | -81.3214% |
| flip OFF, cap off | 1301 | 0 | 0 | +12.9491% |
| flip ON | 2100 | 556 | 1076 | -295.3221% |
| flip ON, min_obj=1 | 1690 | 468 | 163 | -80.7044% |
| flip ON, min_obj=3 | 2449 | 600 | 2343 | -610.3076% |
| flip ON, min_obj=4 | 2494 | 615 | 2494 | -663.2986% |
| flip ON, cap off | 1843 | 0 | 1079 | -189.8205% |
| flip ON, cap 2.50 | 1995 | 300 | 1078 | -193.8624% |
| flip ON, min_obj=3, cap off | 2437 | 0 | 2340 | -511.8425% |
| flip ON, min_obj=3, cap 2.50 | 2444 | 339 | 2342 | -517.1239% |
| flip ON, fire=verdict | 2168 | 528 | 1078 | -290.2129% |
| flip ON, div weight 2 | 2100 | 556 | 1076 | -295.3221% |
| flip ON, slope_floor 2.0 | 2100 | 556 | 1075 | -296.7669% |

No capped arm is positive. The AF knobs span 56 pp; the cap spans 207 pp.

## 5. Open, nothing decided

| the item | state |
|---|---|
| `W_OCTO2_FLIP` | defaults to 0. Joe said wire it in, not bank it. No ruling |
| the 3 unrun sweep arms | div weight 2 x cap off, slope floor 2.0 x cap off, flip off x cap off re-run |
| `W_AF_BLOCK` 60 | no ruling, not in `_ruled.py` |
| `W_AF_SLOPE_FLOOR` 0.0 | no ruling, not in `_ruled.py` |
| `W_VOTE_DIV_WEIGHT` 1 | no ruling. Joe: *"leaning to giving 2 votes when all 3 lines are in agreeance"* |
| the open-vote mech | has NO name. `_openvote.py` is a placeholder filename |
| the lin-exh `bnd` fence read | one-sided vs both-sided 17/83, unruled |
| the low-cluster anchor tolerance | Joe's ws2->ws8 read vs his own "start at 1" rule |
| the +408.8044% at `bfa3b8f` vs +12.9491% cap-off now | a ~176 pp gap, unexplained |
| `1017_bank_a.md` S2-S4 | carries the superseded 40-trade numbers |

## 6. Uncommitted at sign-off, branch `causal/lookahead`

| file | state |
|---|---|
| `docs/octo-freedom/1005_scoring/_chain10.py` | modified |
| `docs/octo-freedom/1005_scoring/_ruled.py` | modified |
| `docs/octo-freedom/1005_scoring/_vetomom.py` | modified |
| `docs/octo-freedom/1005_scoring/_win3.py` | modified |
| `docs/octo-freedom/1005_scoring/octo2.py` | modified |
| `optimus9/analysis/jig.py` | modified |
| `docs/octo-freedom/1005_scoring/_openvote.py` | untracked |
| `docs/octo-freedom/1017_bank_a.md` | untracked |

Nothing is staged. The 1017 bank-A commit Joe asked for was not made.

## 7. The two dev-caches, both warm

| the window | key | bars | events | closed trades | cap stops | control |
|---|---|---|---|---|---|---|
| 2026-08-25..27 | `4d2edb1538134965e89c` | 51,840 | 73 | 53 | 27 | OK |
| 2026-09-10..12 | `92e922869b958284a248` | 51,840 | 103 | 44 | 9 | OK |
