# THE CHAIN - FENCE 75/25, LADDER ws1..ws30, THE LATCH RELEASED ON LIFT
# WINDOW 2026-09-03 00:00:00 .. 2026-09-03 23:59:55 | TAPE 1632960 bars | RULED_OK True
# RMOM_FNC 75.0 -> (25.0, 75.0) | L2_MOM_MAXTF 30 | LIN2_EXFNC_LATCH_REL 'lift'
# the latch turns ON at an ex-fence cross held 4 bars = 20 s, and is released ONLY by that
#   line's own lift-off on the same side, stamped at lift + LIFT_WOB - 1 = lift + 7 bars = 35 s.
#   and its sampling RESTARTS at the latch-on bar - his 1030 ruling - so the lattice must refill before any release can print.
# the barrage no longer releases the latch on this arm. It is still a cadence, so the column stays.
# LIN2_COUNTER_OOB_ON 0 - his 1030 *"drop the opposing oob side forced exit"*. At 0 the ws1b counter-target-side
#   oob cadence is not produced at all, so no leg can exit on it. Its replacement is UNRULED - his own words.
# the open is 2026-09-03 00:37:00 LONG, handed in - W_OPEN, his own bar and side
# the way back in after a stop: NONE - the chain ends at its first stop
# the baton fence test reads: latch, released on lift. the stop is ON at LIN2_MAE_CAP 1.10%, with 0 lin2-reentry signals as the way back in. drag 0.1975% per round trip, its own column and its own total.
# ts is the bar. pxs is that bar's close unless the row names an extreme. pct is signed to THIS leg.
# baton candidates: every candidate timeframe offered at that bar with its value. "none offered" = a hand-over attempt with no candidate inside lin_hop 2.
# exfnc ltchd: every ws1..ws30 line whose ex-fence latch is ON at that bar, on this leg's side.
# a row whose bar carried a cadence starts **CADENCE:**.

## THE CHAIN SUMMARY - one row per leg, chronological

| day | leg of that day | leg of the chain | the open | dir | the exit | ended by | held min | the rider chain | MAE % | MFE % | realised % | drag % | net % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-03 | 1 | 1 | 2026-09-03 00:37:00 | LONG | 2026-09-03 01:36:00 | t1 | 59.0 | ws10 > ws15 | 0.1735 | +2.3198 | +1.8121 | 0.1975 | +1.6146 |
| 2026-09-03 | 2 | 2 | 2026-09-03 01:36:05 | SHORT | 2026-09-03 04:56:55 | STOP at 1.10% | 200.8 | ws5 > ws6 > ws8 > ws9 > ws10 > ws12 > ws17 > ws18 | 1.1000 | +0.9278 | -1.1000 | 0.1975 | -1.2975 |
| TOTAL | | 2 scored legs | | | | | 259.8 | | 1.2735 | +3.2475 | +0.7121 | 0.3950 | +0.3171 |

| the read | value |
|---|---|
| legs in the chain over the window | 2 |
| legs opening on 2026-09-03 | 2 |
| seconds to compute | 65.1 |
