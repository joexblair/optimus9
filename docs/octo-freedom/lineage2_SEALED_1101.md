# LINEAGE2, SEALED 2026-11-01

His word: *"bank everything we have done in lineage2, and seal it for later use"* / *"the next job
is a greenfields build so make sure everything is durable before you release lineage2 from memory"*.

THIS FILE IS THE HANDOVER. Everything needed to pick lineage2 up again is here: every knob with the
ruling that set it, the numbers the machine produced, and the two things still measured as wrong.
A later session needs no transcript.

## THE RULED BANK - a plain run needs no overrides and RULED_OK is True

| the knob | value | what it is |
|---|---|---|
| LIN2_CP_EXFNC | 'closed_prev' | the ex-fence read's source. His *"we will use closed_prev only for exiting fences"* |
| LIN2_CP_OOB | 'emerging' | the oob 15/85 read. He put oob in neither category and said *"build for both options"* |
| LIN2_CP_IB | 'emerging' | the oob->ib cross. His *"my gut says emerging: create a knob that tests both options"* |
| LIN2_CP_MIN_TF | 1 | the TF floor for the chart-matched read. Was 2 until *"change ws1r to closed-p"* |
| LIN2_CP_GCWS30B | 'closed_prev' | gcws30b for EVERY consumer - the t1 b line and the arm race. His *"yes"* |
| LIN2_CP_WS1R | 'closed_prev' | ws1r's VALUE in the t1 r gate |
| LIN2_CP_LIFT | 'closed_prev' | ws1r's reversal BARS. His *"lift-off needs a close-p mode for ws1r - it only reacts to full 1 minute bars"* |
| LIN2_T1_B_LINE | 'gcws30b' | t1's b line |
| LIN2_T1_B_FNC | 95.0 -> (5.0, 95.0) | the way OUT. His *"I omitted the 5/95 requirement for gcws30b"* |
| LIN2_T1_B_WOB | 6 bars = 30 s | the ib cross hold. His *"xwob for ib cross is 6 bars"* |
| LIN2_T1_B_IB_DWELL | 12 bars = 60 s | the HELD ib dwell. His *"add a 1 minute minimum dwell on gcws30b ib"* |
| LIN2_T1_R_FNC | 56.0 -> (44.0, 56.0) | the r gate on ws1r at its stamp |
| LIN2_T1_GRACE_AT | 'cross' | where the 120 s grace starts |
| LIN2_LATCH_EXFNC_ON | 0 | BANKED OFF. His *"disable the latch.  I introduced it get around emerging"* |
| LIN2_BOARD_HOLD | 'linhop_exfnc' | the board test. Arms: off, board_oob, board_oob_rev, linhop_exfnc |
| L2_LIN_HOP | 2 | the hop reach, rider+1 .. rider+2 |
| LIN2_RIDER_JUMP | 8 | the jump bound at a cadence |
| L2_MOM_MAXTF | 30 | the ladder top |
| RMOM_FNC | 75.0 -> (25.0, 75.0) | the r fence |
| OOB_LO / OOB_HI | 15.0 / 85.0 | oob, always |
| LIN2_PASS | 'ib' | the baton pass mode |
| LIN2_TOP_RESET_ON | 1 | the ladder-top rider reset, no limit on repeats |
| LIN2_CASCADE_NO_ACTION | 0 | the mage cascade DISABLED. His 1031 *"completely disable the mage cascade"* |
| LIN2_DIV_ON | 0 | the divergence OFF. His *"divergence can be completely disabled"* |
| LIN2_B1_HOLD | 0 | the b line's return hold, UNUSED by t1 - t1 passes the ib dwell 12 explicitly |
| LIN2_B1_OOB_DWELL | 0 | the b line's entry dwell |
| L2_T1_GRACE_S | 120 s = 24 bars | the forward window for a late ws1r reversal |
| LIN2_REV_WOB | 12 bars = 60 s | a rung's reversal hold, raw -> stamp |
| L2_CWS1R_WOB | 1 bar | ws1r's own reversal hold, so its stamp equals its raw bar |
| LIFT_PTS | 6 samples | the lift-off lattice's sample count |
| GAP_PER_TF | 2.8 bars per TF-minute | the lattice width |
| LIFT_TOL | 2.0 r-points | the at-extreme tolerance |
| LIFT_WOB | 8 bars = 40 s | jig.lift_stamp's own hold. NOT the lineage2 ws1r stamp |
| LIN2_MAE_CAP | 1.10% | the stop |

## THE t1 CADENCE, AS SEALED - one excursion, two fences

    the way out      gcws30b beyond (5.0, 95.0) on at least one bar of the journey
    the journey      the single excursion beyond (15.0, 85.0), which CONTAINS the 5/95 run
    a blip           an ib excursion shorter than LIN2_T1_B_IB_DWELL 12 bars does NOT break it
    the return       the 15.0/85.0 ib cross, hold LIN2_T1_B_WOB 6 bars, then the 12-bar HELD dwell
    the run match    CONTAINMENT - which held run contains the bar before the cross
    the r gate       ws1r at its stamp past (44.0, 56.0), on the chart-matched VALUE
    the reversal     ws1r's lift-off on the chart-matched series, so it lands on a 60 s close
    the fire bar     the LATEST of the cross confirm bar, the dwell's last bar, the reversal stamp

## THE CADENCE TASK ORDER, as he left it

    1  the lin-hop reach test      HIS "(almost) first task". A rung in rider+1..rider+2 that is
                                   ex-fence AND printing towards holds the walk to the next cadence.
                                   A rider of 0 reaches ws1..ws2 - MY reading, stated.
    2  the divergence test         OFF
    3  the barrage exhaust
    4  the mage-cascade verdict    DISABLED
    5  the rider pickup
    6  the matryoshka takeover
    7  the candidate scan (BATON)
    8  HOLD
    9  the ladder-top reset
    10 the EXHAUST

HIS "almost" IS UNRESOLVED. He said *"I say "almost" because I'm not sure of the cadence's task
order"*. The list above is what he moves it against. The one worth his eye is the barrage exhaust,
which ends the walk outright and now sits behind the reach test.

## WHAT THE SEALED MACHINE PRODUCES

2026-09-03, his 00:37 LONG open, stop ON at 1.10%, no way back in after a stop - chain_0903_lift.md

| leg | the open | dir | the exit | ended by | held min | net % |
|---|---|---|---|---|---|---|
| 1 | 2026-09-03 00:37:00 | LONG | 2026-09-03 02:37:25 | t1 | 120.4 | +1.9745 |
| 2 | 2026-09-03 02:37:30 | SHORT | 2026-09-03 04:39:00 | t1 | 121.5 | +0.6390 |
| 3 | 2026-09-03 04:39:05 | LONG | 2026-09-03 05:55:00 | t1 | 75.9 | +1.4008 |
| 4 | 2026-09-03 05:55:05 | SHORT | 2026-09-03 08:07:35 | STOP at 1.10% | 132.5 | -1.2975 |
| TOTAL | | | | 4 scored legs | 450.3 | **+2.7167** |

MAE 2.0366, MFE +6.0359, realised +3.5067, drag 0.7900 - 22.5% of gross.

## THE TWO THINGS STILL MEASURED AS WRONG

| # | what |
|---|---|
| 1 | THE 08-14 1407 IS GONE. The 06:59:00 arm now exhausts at 21:00:55 on the banked 'ib' mode, 841.9 min in with 30 baton passes. 'reversal' lands 12:16:55. His 1407 is in no mode. It was 14:07:20 before the chart-matched reads went in |
| 2 | THE 17:01 ARM IS 62.0 MIN LATE. His validated list is 17:16, 22:01, 23:39, 00:07, 00:36; the race now fires 18:18:00 for the 17:01 LONG. 3 of 5 are within 1.5 min. The cause is the ws1r and gcws30b routing, which the arm race reads |

## HIS FOUR OPEN DECISIONS

| # | the question |
|---|---|
| 1 | the task order - where the reach test really belongs, his "almost" |
| 2 | whether the board test stays at the hop-reach arm or moves to one of the oob arms. On 09-03 the arms give: off +2.6805, board_oob +0.6770, board_oob_rev +2.6846, linhop_exfnc +2.7167 |
| 3 | whether "printing towards" means the banked `towards` read with its age and travel floors, or the direction alone. On 2026-09-03 05:02:55 that is the whole difference |
| 4 | a pxs reversal detector. There is none in the tree, so every "does pxs reverse" answer in this work is the sign of a price move, not a measured reversal |

## THE MATRYOSHKA PROBE - measured, unbuilt, no knob

His 1101 idea, tested at 14 cadences on 2026-09-03 with a 180 s window on the chart-matched values:

| the arm | fires | turns among the fires | the base rate |
|---|---|---|---|
| ws1..ws3 | 8 of 14 | 5 of 8 | 7 of 11 turn on the 11-cadence set |
| ws1..ws4, ws4r oob invalidating | 7 of 14 | 5 of 7 | the same |

Neither beats the base rate. His *"ws2r (or any line) printing away infers a reversal has already
happened"* is the reading that makes the away state the count rather than the reversal detector.
Files: matry_away.md, matry_cp_123.md, matry_cp_1234.md, matry180_*.md, matry11_*.md.

## THE DRIVERS

| the file | what it owns |
|---|---|
| 1030_mom_fence/chain_lift_2d.py | THE chain driver. W_WIN_START, W_WIN_END, W_OPEN, W_SIDE, W_MAE_CAP, W_WALKS (a DATE:leg key), W_RESIG |
| 1030_mom_fence/baton_l2_0814.py | the handed-in-arm walk, all three pass modes. Also W_RESET_SCAN, W_HOLD_*, W_REVSCAN_*, W_REVWIN_*, W_LIFT_ARMS, W_BOARD_AT, W_MATRY* |
| 1030_mom_fence/t1_grace_diff.py | the t1 cadence list, the per-cross trace, the gcws30b value trace, the open-to-arm gap read |
| 1030_mom_fence/arm_from_open.py | his arm list against the race |
| 1022_v4/v4_truncation_test.py | the standing causality check. Bound a walk at its own verdict bar; identical rows prove no forward read |

## THE CAUSALITY POSITION

| the read | state |
|---|---|
| every line in play | emerging mode in the DB - b, r, m, x, Mage, and gcws30b |
| the lookahead register entry A4 | SEAM BUILT, OFF - 92d0fe5 |
| the chart-matched series | v4_closed_prev.series, which asserts its own causality: the bar it reads is strictly before the bar it serves, inside a coarse bar that has already closed |
| a NaN before a line's first completed coarse bar | fails every fence comparison, so an unwarmed bar reads as not-ex-fence and not-oob. A direction, chosen and stated |
