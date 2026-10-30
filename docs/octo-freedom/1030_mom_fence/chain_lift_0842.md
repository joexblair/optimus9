# THE 2-DAY CHAIN - FENCE 75/25, LADDER ws1..ws20, THE LATCH RELEASED ON LIFT-OFF
# WINDOW 2026-08-30 00:00:00 .. 2026-08-31 23:59:55 | TAPE 1632960 bars | RULED_OK False
# RMOM_FNC 75.0 -> (25.0, 75.0) | L2_MOM_MAXTF 20 | LIN2_EXFNC_LATCH_REL 'lift'
# the latch turns ON at an ex-fence cross held 4 bars = 20 s, and is released ONLY by that
#   line's own lift-off on the same side, stamped at lift + LIFT_WOB - 1 = lift + 7 bars = 35 s.
#   and its sampling RESTARTS at the latch-on bar - his 1030 ruling - so the lattice must refill before any release can print.
# the barrage no longer releases the latch on this arm. It is still a cadence, so the column stays.
# LIN2_COUNTER_OOB_ON 0 - his 1030 *"drop the opposing oob side forced exit"*. At 0 the cws1b counter-target-side
#   oob cadence is not produced at all, so no leg can exit on it. Its replacement is UNRULED - his own words.
# the open is 2026-08-29 23:53:55 SHORT, handed in - the router's fire bar off the lin2-reentry signal 2026-08-29 23:53:50.
# the baton fence test reads: latch, released on lift. the 1.1% stop is OFF. drag 0.1975% per round trip, its own column and its own total.
# ts is the bar. pxs is that bar's close unless the row names an extreme. pct is signed to THIS leg.
# baton candidates: every candidate timeframe offered at that bar with its value. "none offered" = a hand-over attempt with no candidate inside lin_hop 2.
# exfnc ltchd: every ws1..ws20 line whose ex-fence latch is ON at that bar, on this leg's side.
# a row whose bar carried a cadence starts **CADENCE:**.

## THE CHAIN SUMMARY - one row per leg, chronological

| day | leg of that day | leg of the chain | the open | dir | the exit | ended by | held min | the rider chain | MAE % | MFE % | realised % | drag % | net % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-29 | 1 | 1 | 2026-08-29 23:53:55 | SHORT | 2026-08-30 01:59:55 | t2 | 126.0 | ws2 | 0.5088 | +1.9536 | +1.3940 | 0.1975 | +1.1965 |
| 2026-08-30 | 1 | 2 | 2026-08-30 02:00:00 | LONG | 2026-08-30 02:45:55 | t2 | 45.9 | ws6 | 0.3560 | +0.4024 | +0.0877 | 0.1975 | -0.1098 |
| 2026-08-30 | 2 | 3 | 2026-08-30 02:46:00 | SHORT | 2026-08-30 04:41:00 | t1 | 115.0 | ws18 > ws20 | 0.3196 | +2.0568 | +1.6393 | 0.1975 | +1.4418 |
| 2026-08-30 | 3 | 4 | 2026-08-30 04:41:05 | LONG | 2026-08-30 05:10:10 | t1 | 29.1 | ws6 | 0.5712 | +0.8543 | +0.5660 | 0.1975 | +0.3685 |
| 2026-08-30 | 4 | 5 | 2026-08-30 05:10:15 | SHORT | 2026-08-30 09:41:35 | t1 | 271.3 | ws4 > ws6 > ws8 > ws10 > ws12 > ws13 | 1.0787 | +1.4540 | +1.1725 | 0.1975 | +0.9750 |
| 2026-08-30 | 5 | 6 | 2026-08-30 09:41:40 | LONG | 2026-08-30 10:12:55 | t2 | 31.2 | ws4 > ws5 | 0.4113 | +0.4008 | +0.1740 | 0.1975 | -0.0235 |
| 2026-08-30 | 6 | 7 | 2026-08-30 10:13:00 | SHORT | 2026-08-30 11:52:55 | t1 | 99.9 | ws20 | 0.6580 | +0.2158 | -0.0158 | 0.1975 | -0.2133 |
| 2026-08-30 | 7 | 8 | 2026-08-30 11:53:00 | LONG | 2026-08-30 12:03:55 | DIV REV-TRADE | 10.9 | - | 0.1263 | +0.4579 | +0.4421 | 0.1975 | +0.2446 |
| 2026-08-30 | 8 | 9 | 2026-08-30 12:04:00 | SHORT | 2026-08-30 13:16:10 | t2 | 72.2 | ws5 | 1.2786 | +0.0734 | -0.2568 | 0.1975 | -0.4543 |
| 2026-08-30 | 9 | 10 | 2026-08-30 13:16:15 | LONG | 2026-08-30 14:56:55 | t2 | 100.7 | ws20 | 0.2456 | +2.2317 | +0.6533 | 0.1975 | +0.4558 |
| 2026-08-30 | 10 | 11 | 2026-08-30 14:57:00 | SHORT | 2026-08-30 16:41:35 | t2 | 104.6 | ws20 | 0.8360 | +1.5059 | +0.3894 | 0.1975 | +0.1919 |
| 2026-08-30 | 11 | 12 | 2026-08-30 16:41:40 | LONG | 2026-08-30 18:06:25 | t2 | 84.8 | ws9 | 3.8524 | +0.3805 | -2.3145 | 0.1975 | -2.5120 |
| 2026-08-30 | 12 | 13 | 2026-08-30 18:06:30 | SHORT | 2026-08-30 21:04:00 | t2 | 177.5 | ws16 | 0.8058 | +5.1283 | +3.7462 | 0.1975 | +3.5487 |
| 2026-08-30 | 13 | 14 | 2026-08-30 21:04:05 | LONG | 2026-08-30 22:59:55 | t2 | 115.8 | ws17 | 2.1290 | +1.4858 | -1.6743 | 0.1975 | -1.8718 |
| 2026-08-30 | 14 | 15 | 2026-08-30 23:00:00 | SHORT | 2026-08-30 23:49:00 | t1 | 49.0 | ws19 | 0.4003 | +4.7082 | +3.4903 | 0.1975 | +3.2928 |
| 2026-08-30 | 15 | 16 | 2026-08-30 23:49:05 | LONG | 2026-08-31 00:19:55 | t2 | 30.8 | ws4 | 0.0643 | +2.9563 | +1.8404 | 0.1975 | +1.6429 |
| 2026-08-31 | 1 | 17 | 2026-08-31 00:20:00 | SHORT | 2026-08-31 01:09:15 | t1 | 49.2 | ws18 | 0.8319 | +0.2467 | -0.0287 | 0.1975 | -0.2262 |
| 2026-08-31 | 2 | 18 | 2026-08-31 01:09:20 | LONG | 2026-08-31 03:24:25 | t1 | 135.1 | ws4 | 2.1335 | +0.5965 | -0.8029 | 0.1975 | -1.0004 |
| 2026-08-31 | 3 | 19 | 2026-08-31 03:24:30 | SHORT | 2026-08-31 04:23:25 | t1 | 58.9 | ws16 | 0.7747 | +1.8444 | +1.2142 | 0.1975 | +1.0167 |
| 2026-08-31 | 4 | 20 | 2026-08-31 04:23:30 | LONG | 2026-08-31 04:57:20 | t2 | 33.8 | ws10 | 0.2926 | +0.6321 | +0.2692 | 0.1975 | +0.0717 |
| 2026-08-31 | 5 | 21 | 2026-08-31 04:57:25 | SHORT | 2026-08-31 08:52:20 | t2 | 234.9 | ws5 > ws7 | 3.3738 | +0.1868 | -2.4107 | 0.1975 | -2.6082 |
| 2026-08-31 | 6 | 22 | 2026-08-31 08:52:25 | LONG | 2026-08-31 10:43:30 | t1 | 111.1 | ws3 > ws5 | 1.1057 | +0.4959 | -0.1653 | 0.1975 | -0.3628 |
| 2026-08-31 | 7 | 23 | 2026-08-31 10:43:35 | SHORT | 2026-08-31 11:54:30 | t1 | 70.9 | ws20 | 0.7593 | +1.0904 | +0.7821 | 0.1975 | +0.5846 |
| 2026-08-31 | 8 | 24 | 2026-08-31 11:54:35 | LONG | 2026-08-31 13:04:55 | t2 | 70.3 | ws4 | 1.0300 | +1.1105 | -0.4316 | 0.1975 | -0.6291 |
| 2026-08-31 | 9 | 25 | 2026-08-31 13:05:00 | SHORT | 2026-08-31 15:21:35 | t1 | 136.6 | ws17 | 1.7799 | +0.8322 | +0.0809 | 0.1975 | -0.1166 |
| 2026-08-31 | 10 | 26 | 2026-08-31 15:21:40 | LONG | 2026-08-31 18:33:35 | barrage | 191.9 | ws2 > ws3 > ws13 > ws15 | 0.5784 | +3.4702 | +2.8571 | 0.1975 | +2.6596 |
| 2026-08-31 | 11 | 27 | 2026-08-31 18:33:40 | SHORT | 2026-08-31 19:23:15 | t1 | 49.6 | ws5 | 1.9906 | +1.0121 | +0.4274 | 0.1975 | +0.2299 |
| 2026-08-31 | 12 | 28 | 2026-08-31 19:23:20 | LONG | 2026-08-31 21:37:00 | t1 | 133.7 | ws12 | 0.9092 | +0.9939 | +0.6664 | 0.1975 | +0.4689 |
| 2026-08-31 | 13 | 29 | 2026-08-31 21:37:05 | SHORT | 2026-08-31 22:21:50 | t1 | 44.8 | ws20 | 0.1683 | +1.0154 | +0.8471 | 0.1975 | +0.6496 |
| 2026-08-31 | 14 | 30 | 2026-08-31 22:21:55 | LONG | - | no exhaust | - | - | - | - | - | - | - |
| TOTAL | | 29 scored legs | | | | | 2785.6 | | 29.3698 | +39.7928 | +14.6390 | 5.7275 | +8.9115 |

## 2026-08-31 leg 5 - SHORT   opens 2026-08-31 04:57:25   exits 2026-08-31 08:52:20 on t2   held 234.9 min   MAE 3.3738   MFE 0.1868   realised -2.4107   net -2.6082

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-31 04:57:25 | >>> THIS LEG OPENS SHORT | - | 5: ws2,ws6,ws7,ws8,ws9 | last 23:49:30, 307.9 min ago | 0.171320 | -0.0000 |
| 2026-08-31 05:00:00 | the favourable extreme - MFE 0.1868 | - | 4: ws6,ws7,ws8,ws9 | last 23:49:30, 310.5 min ago | 0.171000 | +0.1868 |
| 2026-08-31 08:21:00 | ARM - cws1b+cws1r: cws1b 13.50 + cws1r 7.21 oob | - | 3: ws1,ws4,ws5 | last 23:49:30, 511.5 min ago / counter-side 2026-08-31 07:29:25 | 0.174980 | -2.1364 |
| 2026-08-31 08:21:00 | RIDER rider cws5 - cws5 r 22.92, the highest ex-fence | - | 3: ws1,ws4,ws5 | last 23:49:30, 511.5 min ago / counter-side 2026-08-31 07:29:25 | 0.174980 | -2.1364 |
| 2026-08-31 08:21:00 | RETEST - cws1r 7.21 oob + cws2r 48.26 / cws3r 27.65 in - the gate opens; cws1r oob->ib cross 2026-08-31 08:23:00, wob 12, cadence at 2026-08-31 08:23:55 | - | 3: ws1,ws4,ws5 | last 23:49:30, 511.5 min ago / counter-side 2026-08-31 07:29:25 | 0.174980 | -2.1364 |
| 2026-08-31 08:23:55 | **CADENCE:** RIDER rider cws5 - v4-arm-lineage-retest: the re-scan rides cws5 22.92, the highest ex-fence | - | 3: ws1,ws4,ws5 | last 23:49:30, 514.4 min ago / counter-side 2026-08-31 07:29:25 | 0.175040 | -2.1714 |
| 2026-08-31 08:28:15 | BATON rider cws5 - ws5 -> ws7, between cadences, lin_hop 2 | cws7: 27.05 | 3: ws1,ws2,ws7 | last 23:49:30, 518.8 min ago / counter-side 2026-08-31 07:29:25 | 0.175420 | -2.3932 |
| 2026-08-31 08:35:40 | NO PASS rider cws7 - cws7 25.57 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 2: ws2,ws5 | last 23:49:30, 526.2 min ago / counter-side 2026-08-31 07:29:25 | 0.175860 | -2.6500 |
| 2026-08-31 08:42:30 | the ADVERSE extreme - MAE 3.3738 | - | 3: ws5,ws6,ws7 | last 23:49:30, 533.0 min ago / counter-side 2026-08-31 07:29:25 | 0.177100 | -3.3738 |
| 2026-08-31 08:52:20 | **CADENCE:** EXHAUST rider cws7 - t2 cws1r ib cross 08:51:25 confirmed 08:52:20 at wob 12, cws1b 38.69 not oob, ws1b hold 0 \| mage-cascade up OPPOSES the SHORT - rev-trade | - | 5: ws6,ws7,ws8,ws9,ws10 | last 23:49:30, 542.8 min ago / counter-side 2026-08-31 07:29:25 | 0.175450 | -2.4107 |
| 2026-08-31 08:52:20 | THIS LEG CLOSES on t2, realised -2.4107, drag 0.1975, net -2.6082 | - | 5: ws6,ws7,ws8,ws9,ws10 | last 23:49:30, 542.8 min ago / counter-side 2026-08-31 07:29:25 | 0.175450 | -2.4107 |

## 2026-08-30 leg 13 - LONG   opens 2026-08-30 21:04:05   exits 2026-08-30 22:59:55 on t2   held 115.8 min   MAE 2.1290   MFE 1.4858   realised -1.6743   net -1.8718

| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |
|---|---|---|---|---|---|---|
| 2026-08-30 21:04:05 | >>> THIS LEG OPENS LONG | - | 2: ws6,ws9 | last 16:19:30, 284.6 min ago / counter-side 2026-08-30 19:07:55 | 0.180370 | +0.0000 |
| 2026-08-30 21:59:15 | ARM - cws1b+cws1r: cws1b 103.18 + cws1r 97.10 oob | - | 9: ws1,ws3,ws9,ws10,ws11,ws13,ws15,ws16,ws17 | last 16:19:30, 339.8 min ago / counter-side 2026-08-30 19:07:55 | 0.182160 | +0.9924 |
| 2026-08-30 21:59:15 | RIDER rider cws17 - cws17 r 79.42, the highest ex-fence | - | 9: ws1,ws3,ws9,ws10,ws11,ws13,ws15,ws16,ws17 | last 16:19:30, 339.8 min ago / counter-side 2026-08-30 19:07:55 | 0.182160 | +0.9924 |
| 2026-08-30 21:59:15 | RETEST - cws1r 97.10 oob + cws2r 60.57 / cws3r 40.02 in - the gate opens; cws1r oob->ib cross 2026-08-30 22:02:00, wob 12, cadence at 2026-08-30 22:02:55 | - | 9: ws1,ws3,ws9,ws10,ws11,ws13,ws15,ws16,ws17 | last 16:19:30, 339.8 min ago / counter-side 2026-08-30 19:07:55 | 0.182160 | +0.9924 |
| 2026-08-30 22:01:40 | the favourable extreme - MFE 1.4858 | - | 8: ws3,ws9,ws10,ws12,ws13,ws15,ws16,ws17 | last 16:19:30, 342.2 min ago / counter-side 2026-08-30 19:07:55 | 0.183050 | +1.4858 |
| 2026-08-30 22:02:55 | **CADENCE:** RIDER rider cws17 - v4-arm-lineage-retest: the re-scan rides cws17 79.42, the highest ex-fence | - | 9: ws2,ws3,ws9,ws10,ws12,ws13,ws15,ws16,ws17 | last 16:19:30, 343.4 min ago / counter-side 2026-08-30 19:07:55 | 0.182100 | +0.9591 |
| 2026-08-30 22:30:20 | the ADVERSE extreme - MAE 2.1290 | - | 4: ws12,ws15,ws16,ws17 | last 16:19:30, 370.8 min ago / counter-side 2026-08-30 19:07:55 | 0.176530 | -2.1290 |
| 2026-08-30 22:59:55 | **CADENCE:** EXHAUST rider cws17 - t2 cws1r ib cross 22:59:00 confirmed 22:59:55 at wob 12, cws1b 26.94 not oob, ws1b hold 0 \| mage-cascade down OPPOSES the LONG - rev-trade | - | 4: ws1,ws15,ws16,ws17 | last 16:19:30, 400.4 min ago / counter-side 2026-08-30 19:07:55 | 0.177530 | -1.5745 |
| 2026-08-30 22:59:55 | THIS LEG CLOSES on t2, realised -1.6743, drag 0.1975, net -1.8718 | - | 4: ws1,ws15,ws16,ws17 | last 16:19:30, 400.4 min ago / counter-side 2026-08-30 19:07:55 | 0.177530 | -1.5745 |

| the read | value |
|---|---|
| legs in the chain over the two days | 30 |
| legs opening on 2026-08-30 | 15 |
| legs opening on 2026-08-31 | 14 |
| legs opening on 2026-08-29 | 1 |
| seconds to compute | 338.6 |
