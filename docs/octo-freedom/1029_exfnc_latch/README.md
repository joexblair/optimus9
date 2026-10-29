# 1029 — the ex-fence latch, the lin2-reentry open, and prev-close dropped

BANKED 2026-10-29. Joe: *"bank this as the machine"*.

## what the machine is now

| the item | the value | whose |
|---|---|---|
| the previous completed bar's close | **OUT of the walk entirely** | his — *"completely drop prev-close"* |
| ws1b, ws1r, ws1Mage, ws2Mage | the live read, via `v4_live_lines.arm_lines` | his |
| every fence test's fallback source | the live value — no knob, there is no second arm | his |
| the per-line ex-fence latch | `LIN2_LATCH_EXFNC_ON` 1 | his mech, his label, his bank |
| the latch's hold | `LIN2_EXFNC_LATCH_WOB` 4 bars = 20 s | his value |
| the pseudo-closed line | `LIN2_PSEUDO_MIN_TF` 99 = off | his bank. 4 is the other arm |
| the chain's open | `LIN2_CHAIN_OPEN_ON` 1 — the lin2-reentry signal | his mech, his label |
| the ws1b crossing hold on the open | `LIN2_CHAIN_OPEN_XWOB` 1 | mine, and he kept it: *"having xwob at 1 while we're testing will highlight any issues that I've papered over"* |
| ws1b's held state in the two cadences | `LIN2_B1_HOLD` 0 | his — *"let's use wob 0 until we sweep"* |
| the barrage's ceiling | `LIN2_BARRAGE_MAX_TF` 15 | his value |
| the mage cascade's anchor | a ws1Mage extremum, 48-bar = 4-min look-back | his ruling and his 1017 number |

## the mage-cascade anchor, which is the last thing banked

Joe 1029: *"were the mage cascades anchored on a ws1Mage's extremum? if not, they should be"*. They
were not. The lineage2 walk passed the cadence bar straight into `mage_cascade`, while all six
other consumers of that producer in the tree call `mage_cascade_bar` first.

Measured on 2026-08-30, the two bars he asked about:

| the cadence bar | read at the bar | anchored on the extremum | ws1Mage at the bar | ws1Mage at the anchor |
|---|---|---|---|---|
| 04:41:00 | down | **up** | 48.56 | -14.39 at 04:40:00 |
| 04:48:30 | down | **up** | 18.17 | -19.38 at 04:47:20 |

At the cadence bar ws1Mage has already climbed off its low, so the first rung reads as falling and
the low cluster is called falling. At the extremum the low cluster rises away from it.

## what the anchor was worth on 2026-08-30

| the read | read at the cadence bar | anchored |
|---|---|---|
| legs | 14 | 15 |
| legs with an exit | 13 | 14 |
| legs net-positive after drag | 5 of 13 | 7 of 14 |
| summed MAE % | 11.7308 | 12.1509 |
| summed MFE % | +17.7660 | +18.4593 |
| summed realised % | +2.9602 | +4.9598 |
| summed drag % | 2.5675 | 2.7650 |
| summed net % | +0.3927 | **+2.1948** |
| MFE collected | 16.7% | 26.9% |

One day. Not a sample.

## the lin2-reentry open

His flow, 1029 verbatim:

    -there is no trade open  (either because of a STOP, or because the machine is cold-starting)
    -walk
    -if ws1b crosses from oob to ib (candidate-side)
    --if ws5Mage is oob or has been oob in the last 5 minutes on the candidate-side
    ---anchor on the ws5Mage extremum.  the anchor is for the next step to align with
    ---if at least 2 ws{>5}Mage wsf lines are printing a value that is away from the candidate
       side, at the anchor bar
    ----open the trade, direction: away from candidate-side

His first line is the ROUTER's, not the mech's — a signal source reads no open position. So
`v4_sig_lin2_reentry` states every firing on the tape (7,787 of them) and the router drops the ones
it cannot take. On 2026-08-29 both 23:53:50 and 23:56:00 are stated; the router opens on the first.

| the read | value |
|---|---|
| the signal | 2026-08-29 23:53:50, ws1b came in from the HIGH side |
| the router's fire bar | 2026-08-29 23:53:55 |
| the direction | SHORT |
| the anchor | 2026-08-29 23:52:10, ws5Mage 89.64 |
| lines beyond it | 7 of 7 |
| his own call | *"the ws1b firing should move 2350 forward to 2353"* |

## prev-close, and why it is gone

He asked whether a ws1r crossing at 2026-08-30 00:19 would be reading a ws12r value set at 00:12.
Measured at that bar:

| the line | the value at 00:19:00 | the bar it was set | the lag, min |
|---|---|---|---|
| cws1r | 85.2820 | 00:18:55 | 0.08 |
| cws5r | 57.1214 | 00:14:55 | 4.08 |
| cws7r | 73.4420 | 00:13:55 | 5.08 |
| cws10r | 42.2138 | 00:09:55 | 9.08 |
| cws11r | 42.6505 | 00:10:55 | 8.08 |
| cws12r | 51.6558 | 00:11:55 | 7.08 |

It was never lookahead - it is the previous completed bucket's close, causal by construction. He
dropped it on the staleness.

WHAT IT COST WHILE IT WAS IN THE WALK'S PATH: his ws1b hold is meant to hold the
00:59:25..01:20:45 low excursion together as one event. On prev-close that moment is one clean
crossing at 01:04:00 holding 24 bars, so a 12-bar hold qualifies and the exit fires at 01:04:55. On
the live read it is four crossings of 9, 4, 2 and 9 bars, none of which qualifies. Dropping
prev-close took that SHORT from 71.0 min and +0.6766 to 153.9 min and +1.5415.

## every figure measured before 2026-10-29 is void

The arm bar, the retest gate, the two cadences and every exit moved when prev-close left. Nothing
from the earlier runs in this session carries forward.

## the files

| the file | what it owns |
|---|---|
| `v4_live_lines.py` | the four lines the walk is handed, all live |
| `v4_sig_lin2_reentry.py` | every lin2-reentry signal on the tape. Reads no open position |
| `v4_chain.py` | the chain's open, its legs, and their scoring. One copy of the loop |
| `v4_l2_proxy.py` | the board, and the ex-fence latch |
| `legs_live.py` | the leg report in his format |
| `arms_three.py` | the three reads, with and without the 1.1% stop |
| `latch_xwob.py` | the ws1b crossing hold at 1 and at 12 |
| `span_trace.py` | every 5 s bar of ws5Mage and ws1b with the mech marked per row |

## unruled, carried forward

| the item | whose |
|---|---|
| whether a leg whose exit lands before its own open pays the 0.1975% drag | his |
| the cascade's line floor — at 3 the 04:48:30 verdict flips to up | his |
| whether a cascade cluster needs a minimum size in points, not just a line count | his |
| the barrage's 70-second tolerance, and whether the ws1r reversal may precede the ws1Mage crossing | his |
| the sweep ranges for every knob above | his |
