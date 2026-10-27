# W_V4_EXPERIMENT=1 - THIS IS NOT THE MACHINE. 1 knob(s) off the bank: LIN2_CAND_NOT_REVERSED is 1, ruled 0 (OFF is the bank. 1 = no reversal since the rider took the baton, 2 = none since the arm. His 1027 "can we test it on the day?" - the test arms, not a banked change. The wob is LIN2_REV_WOB 12, which is MINE)
# lineage2 chained, 2026-08-30 00:00:00 .. 2026-08-30 23:59:55
# t3 needs max(2, round(0.75 x the ex-fence population)) reversals, matryoshka ws7..rider-1
# gate closed | lin_hop 2 lifted only at t1/t2 | RULED_OK False

## first side HIGH  (780.3s)

| the read | value |
|---|---|
| walks | 17 |
| verdicts EXHAUST | 15 |
| verdicts NO ARM | 1 |
| verdicts NO VERDICT | 0 |
| verdicts DIV REV-TRADE | 1 |
| t1 cadence events | 4 |
| t2 cadence events | 5 |
| t3 cadence events | 0 |
| walks that reached a RETEST row | 15 |
|   the gate shut, cws1r not oob at the arm | 4 |
|   the gate shut, cws2r/cws3r not both in the fence | 2 |
|   the gate opened | 9 |
|   the gate opened, no oob->ib cross to the data end | 0 |
| the gate cadence ENDED the walk | 5 |
| the gate cadence RE-SCANNED a rider | 4 |
| BATON passes | 8 |
| LATCH1 armed | 16 |
| cadences taking NO ACTION on the mage-cascade | 16 |
| latch cadence events | 1 |
| cws1b counter-oob cadence events | 10 |

| the DIV branch read | arms |
|---|---|
| a divergence, LONG | 1 |
| PM, trend SHORT | 1 |
| all DIV arms | 2 |
|   of those, a REV-TRADE verdict | 1 |

| the gate cadence | side | what it did | why |
|---|---|---|---|
| 2026-08-30 00:20:55 | HIGH | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-08-30 01:04:55 | LOW | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 18.31, the highest ex-fence |
| 2026-08-30 02:46:55 | HIGH | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-08-30 03:06:55 | LOW | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 12.28, the highest ex-fence |
| 2026-08-30 05:07:55 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 83.86, the highest ex-fence |
| 2026-08-30 10:13:55 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws4 81.84, the highest ex-fence |
| 2026-08-30 19:31:55 | LOW | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-08-30 21:04:55 | LOW | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-08-30 22:03:55 | HIGH | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |

## THE REV-TRADES, and the bars that created each one

| # | the open | dir | the arm | the cadence that ended it | the exhaust = the rev-trade bar | the verdict | latch 1 fires | MAE % | MFE % | SP TF | the pivot | given % | leg MFE % | share |
#   THE EXHAUST BAR *IS* THE REV-TRADE BAR. An exhaust is only ever declared at a
#   cadence event bar, so every bar in that column is a cadence bar. The trade closes
#   there and the opposite side opens at that bar + 1, which is the NEXT row's open.
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-08-30 00:00:05 | LONG | 2026-08-30 00:18:00 | retest | 2026-08-30 00:20:55 | EXHAUST | 0 | -0.529 | +0.580 | ws1Mage | 2026-08-30 00:10:30 | +0.430 | 1.002 | 0.429 |
| 2 | 2026-08-30 00:21:00 | SHORT | 2026-08-30 01:02:00 | cws1b counter-oob | 2026-08-30 02:41:00 | EXHAUST | 5 | -0.117 | +1.829 | ws2Mage | 2026-08-30 02:53:00 | +0.093 | 1.794 | 0.052 |
| 3 | 2026-08-30 02:41:05 | LONG | 2026-08-30 02:43:00 | retest | 2026-08-30 02:46:55 | EXHAUST | 0 | -0.288 | +0.077 | ws2Mage | 2026-08-30 02:38:25 | +0.129 | 0.480 | 0.269 |
| 4 | 2026-08-30 02:47:00 | SHORT | 2026-08-30 03:01:00 | cws1b counter-oob | 2026-08-30 05:02:00 | EXHAUST | 5 | -0.314 | +2.206 | ws1Mage | 2026-08-30 05:29:45 | +0.380 | 0.578 | 0.658 |
| 5 | 2026-08-30 05:02:05 | LONG | 2026-08-30 05:04:00 | t2 | 2026-08-30 05:52:55 | EXHAUST | 0 | -0.324 | +0.507 | ws1Mage | 2026-08-30 05:51:20 | +0.016 | 0.392 | 0.040 |
| 6 | 2026-08-30 05:53:00 | SHORT | 2026-08-30 07:26:00 | t1 | 2026-08-30 08:31:00 | EXHAUST | 1 | -1.279 | +0.512 | ws1Mage | 2026-08-30 09:17:05 | -0.084 | 0.614 | -0.137 |
| 7 | 2026-08-30 08:31:05 | LONG | 2026-08-30 10:11:00 | cws1b counter-oob | 2026-08-30 11:33:00 | EXHAUST | 1 | -1.017 | +0.320 | ws15Mage | 2026-08-30 11:52:25 | +0.306 | 1.840 | 0.166 |
| 8 | 2026-08-30 11:33:05 | SHORT | 2026-08-30 11:48:00 | cws1b counter-oob | 2026-08-30 12:04:00 | EXHAUST | 0 | -0.363 | +0.347 | ws2Mage | 2026-08-30 12:33:15 | +1.191 | 1.113 | 1.070 |
| 9 | 2026-08-30 12:04:05 | LONG | 2026-08-30 12:04:05 | t2 | 2026-08-30 12:35:55 | EXHAUST | 2 | -0.031 | +1.321 | ws1Mage | 2026-08-30 13:36:00 | +0.493 | 0.707 | 0.696 |
| 10 | 2026-08-30 12:36:00 | SHORT | 2026-08-30 14:40:00 | t2 | 2026-08-30 15:05:55 | EXHAUST | 1 | -1.955 | +0.516 | ws1Mage | 2026-08-30 15:11:00 | +0.514 | 0.893 | 0.576 |
| 11 | 2026-08-30 15:06:00 | LONG | 2026-08-30 18:34:00 | cws1b counter-oob | 2026-08-30 19:22:00 | EXHAUST | 1 | -3.827 | +1.257 | ws3Mage | 2026-08-30 21:01:40 | +5.016 | 2.640 | 1.900 |
| 12 | 2026-08-30 19:22:05 | SHORT | 2026-08-30 19:26:00 | retest | 2026-08-30 19:31:55 | EXHAUST | 0 | -0.059 | +0.704 | ws2Mage | 2026-08-30 19:01:15 | +1.014 | 5.400 | 0.188 |
| 13 | 2026-08-30 19:32:00 | LONG | 2026-08-30 20:12:00 | t2 | 2026-08-30 20:54:55 | EXHAUST | 0 | -4.635 | +0.005 | ws3Mage | 2026-08-30 21:48:05 | +1.249 | 1.885 | 0.663 |
| 14 | 2026-08-30 20:55:00 | SHORT | 2026-08-30 21:02:00 | retest | 2026-08-30 21:04:55 | EXHAUST | 0 | -0.132 | +1.955 | ws1Mage | 2026-08-30 21:38:05 | +0.403 | 1.032 | 0.390 |
| 15 | 2026-08-30 21:05:00 | LONG | 2026-08-30 22:00:00 | retest | 2026-08-30 22:03:55 | EXHAUST | 0 | -0.549 | +1.525 | ws3Mage | 2026-08-30 21:56:40 | +0.782 | 1.331 | 0.588 |
| 16 | 2026-08-30 22:04:00 | SHORT | 2026-08-30 22:24:00 | - | 2026-08-30 22:24:00 | DIV REV-TRADE | 0 | -0.006 | +1.684 | ws5Mage | 2026-08-31 08:42:25 | -1.017 | 2.107 | -0.483 |

| the read | value |
|---|---|
| rev-trades | 16 |
| sum MAE % | -15.425 |
| sum MFE % | +15.345 |
| median MAE % | -0.324 |
| median MFE % | +0.704 |
| worst MAE % | -4.635 |
| best MFE % | +2.206 |
| MFE > abs(MAE) | 9 of 16 |
| median share | 0.429 |
| sweep-pivot knobs | SP_PICK lowest_pct, SP_BAND 0.0, SP_CONTAIN 0, SP_XWOB 18, SP_ALIGN_S 300, SP_TFS wide |

| the latch 1 bar | trade | dir | rider | the cadence it armed on | the state |
|---|---|---|---|---|---|
| 2026-08-30 01:04:55 | 2 | SHORT | cws2 | t2 | -1 |
| 2026-08-30 01:21:00 | 2 | SHORT | cws3 | t1 | -1 |
| 2026-08-30 02:00:55 | 2 | SHORT | cws5 | t2 | -1 |
| 2026-08-30 02:30:00 | 2 | SHORT | cws5 | t1 | -1 |
| 2026-08-30 02:30:55 | 2 | SHORT | cws5 | t2 | -1 |
| 2026-08-30 03:19:00 | 4 | SHORT | cws3 | t1 | -1 |
| 2026-08-30 03:43:55 | 4 | SHORT | cws3 | t2 | -1 |
| 2026-08-30 03:54:00 | 4 | SHORT | cws3 | t1 | -1 |
| 2026-08-30 03:54:55 | 4 | SHORT | cws3 | t2 | -1 |
| 2026-08-30 04:13:00 | 4 | SHORT | cws3 | t1 | -1 |
| 2026-08-30 07:44:00 | 6 | SHORT | cws5 | t1 | -1 |
| 2026-08-30 10:29:00 | 7 | LONG | cws4 | t1 | +1 |
| 2026-08-30 12:16:00 | 9 | LONG | cws2 | t1 | +1 |
| 2026-08-30 12:35:55 | 9 | LONG | cws4 | t2 | +1 |
| 2026-08-30 15:05:55 | 10 | SHORT | cws5 | t2 | -1 |
| 2026-08-30 18:38:00 | 11 | LONG | cws5 | t1 | +1 |

### trade 1 - 2026-08-30 00:00:05 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 00:18:00 | ARM | - | cws1b+cws1r: cws1b 109.73 + cws1r 97.62 oob |
| 2026-08-30 00:18:00 | RIDER | cws1 | cws1 r 97.62, the highest ex-fence |
| 2026-08-30 00:18:00 | RETEST | - | cws1r 97.62 oob + cws2r 57.93 / cws3r 36.62 in - the gate opens; cws1r oob->ib cross 2026-08-30 00:20:00, wob 12, cadence at 2026-08-30 00:20:55 |
| 2026-08-30 00:20:55 | EXHAUST | cws1 | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |

### trade 2 - 2026-08-30 00:21:00 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 01:02:00 | ARM | - | cws1b+cws1r: cws1b -6.74 + cws1r 10.24 oob |
| 2026-08-30 01:02:00 | RIDER | cws1 | cws1 r 10.24, the highest ex-fence |
| 2026-08-30 01:02:00 | RETEST | - | cws1r 10.24 oob + cws2r 23.07 / cws3r 51.20 in - the gate opens; cws1r oob->ib cross 2026-08-30 01:04:00, wob 12, cadence at 2026-08-30 01:04:55 |
| 2026-08-30 01:04:55 | RIDER | cws2 | v4-arm-lineage-retest: the re-scan rides cws2 18.31, the highest ex-fence |
| 2026-08-30 01:04:55 | LATCH1 | cws2 | latch 1 at the t2 cadence 2026-08-30 01:04:55, divergence state -1 |
| 2026-08-30 01:04:55 | NO ACTION | cws2 | t2 cws1r ib cross 01:04:00 confirmed 01:04:55 at wob 12, cws1b 16.84 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 01:12:55 | BATON | cws2 | ws2 -> ws3, between cadences, lin_hop 2 |
| 2026-08-30 01:21:00 | LATCH1 | cws3 | latch 1 at the t1 cadence 2026-08-30 01:21:00, divergence state -1 |
| 2026-08-30 01:21:00 | NO ACTION | cws3 | t1 cws1b oob 01:06:00..01:20:55, cws1r reversed 01:20:00 during, stamp 01:20:00 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 01:21:55 | BATON | cws3 | ws3 -> ws5, between cadences, lin_hop 2 |
| 2026-08-30 01:35:55 | NO PASS | cws5 | cws5 27.32 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 01:46:55 | NO ACTION | cws5 | t2 cws1r ib cross 01:46:00 confirmed 01:46:55 at wob 12, cws1b 60.31 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:00:55 | LATCH1 | cws5 | latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 |
| 2026-08-30 02:00:55 | NO ACTION | cws5 | t2 cws1r ib cross 02:00:00 confirmed 02:00:55 at wob 12, cws1b 39.39 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:04:05 | NO ACTION | cws5 | latch latch 2: rider cws5 reversed raw 2026-08-30 01:22:15 stamp 2026-08-30 01:23:10, no candidate inside lin_hop, support ws2 raw 2026-08-30 02:02:45 stamp 2026-08-30 02:03:40, ws3 raw 2026-08-30 02:03:10 stamp 2026-08-30 02:04:05, ws4 raw 2026-08-30 02:02:50 stamp 2026-08-30 02:03:45 \| latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:30:00 | LATCH1 | cws5 | latch 1 at the t1 cadence 2026-08-30 02:30:00, divergence state -1 |
| 2026-08-30 02:30:00 | NO ACTION | cws5 | t1 cws1b ib 02:28:00, cws1r reversed 02:30:00 inside the 120s grace, stamp 02:30:00 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:30:55 | LATCH1 | cws5 | latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1 |
| 2026-08-30 02:30:55 | NO ACTION | cws5 | t2 cws1r ib cross 02:30:00 confirmed 02:30:55 at wob 12, cws1b 33.31 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:38:15 | NO ACTION | cws5 | latch latch 2: rider cws5 reversed raw 2026-08-30 01:22:15 stamp 2026-08-30 01:23:10, no candidate inside lin_hop, support ws2 raw 2026-08-30 02:37:05 stamp 2026-08-30 02:38:00, ws3 raw 2026-08-30 02:37:20 stamp 2026-08-30 02:38:15, ws4 raw 2026-08-30 02:37:05 stamp 2026-08-30 02:38:00 \| latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:41:00 | CADENCE | cws5 | cws1b counter-oob cws1b 88.94 entered the HIGH oob 02:41:00 \| rider cws5 25.57, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 02:41:00 | EXHAUST | cws5 | t4 at a cws1b counter-oob cadence - rider cws5 25.57, no candidate inside lin_hop 2 |

### trade 3 - 2026-08-30 02:41:05 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 02:43:00 | ARM | - | cws1b+cws1r: cws1b 108.98 + cws1r 89.24 oob |
| 2026-08-30 02:43:00 | RIDER | cws1 | cws1 r 89.24, the highest ex-fence |
| 2026-08-30 02:43:00 | RETEST | - | cws1r 89.24 oob + cws2r 52.29 / cws3r 44.78 in - the gate opens; cws1r oob->ib cross 2026-08-30 02:46:00, wob 12, cadence at 2026-08-30 02:46:55 |
| 2026-08-30 02:46:55 | EXHAUST | cws1 | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |

### trade 4 - 2026-08-30 02:47:00 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 03:01:00 | ARM | - | cws1b+cws1r: cws1b 3.75 + cws1r 7.68 oob |
| 2026-08-30 03:01:00 | RIDER | cws1 | cws1 r 7.68, the highest ex-fence |
| 2026-08-30 03:01:00 | RETEST | - | cws1r 7.68 oob + cws2r 22.13 / cws3r 55.36 in - the gate opens; cws1r oob->ib cross 2026-08-30 03:06:00, wob 12, cadence at 2026-08-30 03:06:55 |
| 2026-08-30 03:06:55 | RIDER | cws2 | v4-arm-lineage-retest: the re-scan rides cws2 12.28, the highest ex-fence |
| 2026-08-30 03:12:55 | BATON | cws2 | ws2 -> ws3, between cadences, lin_hop 2 |
| 2026-08-30 03:19:00 | LATCH1 | cws3 | latch 1 at the t1 cadence 2026-08-30 03:19:00, divergence state -1 |
| 2026-08-30 03:19:00 | NO ACTION | cws3 | t1 cws1b oob 03:01:00..03:18:55, cws1r reversed 03:09:00 during, stamp 03:09:00 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 03:21:55 | NO PASS | cws3 | cws3 26.79 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 03:43:55 | LATCH1 | cws3 | latch 1 at the t2 cadence 2026-08-30 03:43:55, divergence state -1 |
| 2026-08-30 03:43:55 | NO ACTION | cws3 | t2 cws1r ib cross 03:43:00 confirmed 03:43:55 at wob 12, cws1b 43.12 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 03:54:00 | LATCH1 | cws3 | latch 1 at the t1 cadence 2026-08-30 03:54:00, divergence state -1 |
| 2026-08-30 03:54:00 | NO ACTION | cws3 | t1 cws1b oob 03:50:00..03:53:55, cws1r reversed 03:53:00 during, stamp 03:53:00 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 03:54:55 | LATCH1 | cws3 | latch 1 at the t2 cadence 2026-08-30 03:54:55, divergence state -1 |
| 2026-08-30 03:54:55 | NO ACTION | cws3 | t2 cws1r ib cross 03:54:00 confirmed 03:54:55 at wob 12, cws1b 17.82 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 04:13:00 | LATCH1 | cws3 | latch 1 at the t1 cadence 2026-08-30 04:13:00, divergence state -1 |
| 2026-08-30 04:13:00 | NO ACTION | cws3 | t1 cws1b oob 04:06:00..04:12:55, cws1r reversed 04:08:00 during, stamp 04:08:00 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 04:15:55 | NO PASS | cws3 | cws3 21.39 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 05:02:00 | CADENCE | cws3 | cws1b counter-oob cws1b 99.93 entered the HIGH oob 05:02:00 \| rider cws3 41.69, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 05:02:00 | EXHAUST | cws3 | t4 at a cws1b counter-oob cadence - rider cws3 41.69, no candidate inside lin_hop 2 |

### trade 5 - 2026-08-30 05:02:05 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 05:04:00 | ARM | - | cws1b+cws1r: cws1b 115.76 + cws1r 85.53 oob |
| 2026-08-30 05:04:00 | RIDER | cws1 | cws1 r 85.53, the highest ex-fence |
| 2026-08-30 05:04:00 | RETEST | - | cws1r 85.53 oob + cws2r 75.45 / cws3r 52.02 in - the gate opens; cws1r oob->ib cross 2026-08-30 05:07:00, wob 12, cadence at 2026-08-30 05:07:55 |
| 2026-08-30 05:07:55 | RIDER | cws2 | v4-arm-lineage-retest: the re-scan rides cws2 83.86, the highest ex-fence |
| 2026-08-30 05:11:00 | CADENCE | cws2 | t1 cws1b oob 05:02:00..05:10:55, cws1r reversed 05:07:00 during, stamp 05:07:00 \| rider cws2 90.23, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-30 05:11:00 | HOLD | cws2 | rider cws2 90.23 oob - no action |
| 2026-08-30 05:12:55 | NO PASS | cws2 | cws2 81.72 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 05:52:55 | CADENCE | cws2 | t2 cws1r ib cross 05:52:00 confirmed 05:52:55 at wob 12, cws1b 35.84 not oob \| rider cws2 66.84, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 05:52:55 | EXHAUST | cws2 | t4 at a t2 cadence - rider cws2 66.84, no candidate on the whole board |

### trade 6 - 2026-08-30 05:53:00 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 07:26:00 | ARM | - | cws1b+cws1r: cws1b -3.43 + cws1r 12.64 oob |
| 2026-08-30 07:26:00 | RIDER | cws3 | cws3 r 12.22, the highest ex-fence |
| 2026-08-30 07:26:00 | RETEST | - | cws2r 18.89 / cws3r 12.22 - not both inside the fence at the arm |
| 2026-08-30 07:30:55 | BATON | cws3 | ws3 -> ws5, between cadences, lin_hop 2 |
| 2026-08-30 07:44:00 | LATCH1 | cws5 | latch 1 at the t1 cadence 2026-08-30 07:44:00, divergence state -1 |
| 2026-08-30 07:44:00 | CADENCE | cws5 | t1 cws1b oob 07:26:00..07:43:55, cws1r reversed 07:40:00 during, stamp 07:40:00 \| rider cws5 0.59, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-30 07:44:00 | BATON | cws5 | ws5 -> ws7, at a t1 cadence, whole board |
| 2026-08-30 08:03:55 | NO PASS | cws7 | cws7 24.05 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 08:31:00 | CADENCE | cws7 | t1 cws1b ib 08:29:00, cws1r reversed 08:31:00 inside the 120s grace, stamp 08:31:00 \| rider cws7 56.66, no-longer-exfence yes, reversed yes \| mage-cascade neither |
| 2026-08-30 08:31:00 | EXHAUST | cws7 | t4 at a t1 cadence - rider cws7 56.66, no candidate on the whole board |

### trade 7 - 2026-08-30 08:31:05 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 10:11:00 | ARM | - | cws1b+cws1r: cws1b 114.29 + cws1r 86.09 oob |
| 2026-08-30 10:11:00 | RIDER | cws1 | cws1 r 86.09, the highest ex-fence |
| 2026-08-30 10:11:00 | RETEST | - | cws1r 86.09 oob + cws2r 63.89 / cws3r 64.12 in - the gate opens; cws1r oob->ib cross 2026-08-30 10:13:00, wob 12, cadence at 2026-08-30 10:13:55 |
| 2026-08-30 10:13:55 | RIDER | cws4 | v4-arm-lineage-retest: the re-scan rides cws4 81.84, the highest ex-fence |
| 2026-08-30 10:13:55 | CADENCE | cws4 | t2 cws1r ib cross 10:13:00 confirmed 10:13:55 at wob 12, cws1b 77.01 not oob \| rider cws4 81.84, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-30 10:13:55 | HOLD | cws4 | rider cws4 81.84 ex-fence and not reversed - no action |
| 2026-08-30 10:16:55 | NO PASS | cws4 | cws4 77.93 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 10:29:00 | LATCH1 | cws4 | latch 1 at the t1 cadence 2026-08-30 10:29:00, divergence state +1 |
| 2026-08-30 10:29:00 | NO ACTION | cws4 | t1 cws1b oob 10:23:00..10:28:55, cws1r reversed 10:27:00 during, stamp 10:27:00 \| mage-cascade up matches the LONG - no action, keep walking |
| 2026-08-30 10:36:55 | NO PASS | cws4 | cws4 77.93 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 11:12:55 | NO ACTION | cws4 | t2 cws1r ib cross 11:12:00 confirmed 11:12:55 at wob 12, cws1b 64.97 not oob \| mage-cascade up matches the LONG - no action, keep walking |
| 2026-08-30 11:33:00 | CADENCE | cws4 | cws1b counter-oob cws1b 12.90 entered the LOW oob 11:33:00 \| rider cws4 58.41, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-30 11:33:00 | EXHAUST | cws4 | t4 at a cws1b counter-oob cadence - rider cws4 58.41, no candidate inside lin_hop 2 |

### trade 8 - 2026-08-30 11:33:05 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 11:48:00 | ARM | - | cws4r: cws4r 12.52 oob |
| 2026-08-30 11:48:00 | RIDER | cws4 | cws4 r 12.52, the highest ex-fence |
| 2026-08-30 11:48:00 | RETEST | - | cws1r 49.22 is not oob at the arm - the gate stays shut |
| 2026-08-30 11:56:55 | NO PASS | cws4 | cws4 19.77 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 12:04:00 | CADENCE | cws4 | cws1b counter-oob cws1b 96.64 entered the HIGH oob 12:04:00 \| rider cws4 43.98, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 12:04:00 | EXHAUST | cws4 | t4 at a cws1b counter-oob cadence - rider cws4 43.98, no candidate inside lin_hop 2 |

### trade 9 - 2026-08-30 12:04:05 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 12:04:05 | ARM | - | cws2Mage+cws2r: cws2Mage 90.48 + cws2r 92.13 oob |
| 2026-08-30 12:04:05 | DIV | - | cws1r divergence none \| anchor_floater state +2 PM, trend SHORT |
| 2026-08-30 12:04:05 | RIDER | cws2 | cws2 r 92.13, the highest ex-fence |
| 2026-08-30 12:04:05 | RETEST | - | cws1r 79.80 is not oob at the arm - the gate stays shut |
| 2026-08-30 12:16:00 | LATCH1 | cws2 | latch 1 at the t1 cadence 2026-08-30 12:16:00, divergence state +1 |
| 2026-08-30 12:16:00 | NO ACTION | cws2 | t1 cws1b oob 12:04:00..12:15:55, cws1r reversed 12:12:00 during, stamp 12:12:00 \| mage-cascade up matches the LONG - no action, keep walking |
| 2026-08-30 12:16:55 | BATON | cws2 | ws2 -> ws4, between cadences, lin_hop 2 |
| 2026-08-30 12:24:55 | NO PASS | cws4 | cws4 83.00 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 12:35:55 | LATCH1 | cws4 | latch 1 at the t2 cadence 2026-08-30 12:35:55, divergence state +1 |
| 2026-08-30 12:35:55 | CADENCE | cws4 | t2 cws1r ib cross 12:35:00 confirmed 12:35:55 at wob 12, cws1b 66.45 not oob \| rider cws4 60.47, no-longer-exfence yes, reversed yes \| mage-cascade neither |
| 2026-08-30 12:35:55 | EXHAUST | cws4 | t4 at a t2 cadence - rider cws4 60.47, no candidate on the whole board |

### trade 10 - 2026-08-30 12:36:00 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 14:40:00 | ARM | - | cws4r: cws4r 12.14 oob |
| 2026-08-30 14:40:00 | RIDER | cws5 | cws5 r 15.81, the highest ex-fence |
| 2026-08-30 14:40:00 | RETEST | - | cws1r 28.69 is not oob at the arm - the gate stays shut |
| 2026-08-30 14:55:55 | NO PASS | cws5 | cws5 20.65 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 15:05:55 | LATCH1 | cws5 | latch 1 at the t2 cadence 2026-08-30 15:05:55, divergence state -1 |
| 2026-08-30 15:05:55 | CADENCE | cws5 | t2 cws1r ib cross 15:05:00 confirmed 15:05:55 at wob 12, cws1b 40.26 not oob \| rider cws5 40.40, no-longer-exfence yes, reversed yes \| mage-cascade neither |
| 2026-08-30 15:05:55 | EXHAUST | cws5 | t4 at a t2 cadence - rider cws5 40.40, no candidate on the whole board |

### trade 11 - 2026-08-30 15:06:00 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 18:34:00 | ARM | - | cws1b+cws1r: cws1b 96.35 + cws1r 88.13 oob |
| 2026-08-30 18:34:00 | RIDER | cws5 | cws5 r 80.58, the highest ex-fence |
| 2026-08-30 18:34:00 | RETEST | - | cws2r 82.90 / cws3r 50.95 - not both inside the fence at the arm |
| 2026-08-30 18:38:00 | LATCH1 | cws5 | latch 1 at the t1 cadence 2026-08-30 18:38:00, divergence state +1 |
| 2026-08-30 18:38:00 | CADENCE | cws5 | t1 cws1b oob 18:32:00..18:37:55, cws1r reversed 18:37:00 during, stamp 18:37:00 \| rider cws5 80.58, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-30 18:38:00 | BATON | cws5 | ws5 -> ws6, at a t1 cadence, whole board |
| 2026-08-30 18:44:20 | CADENCE | cws6 | latch latch 2: rider cws6 reversed raw 2026-08-30 18:42:40 stamp 2026-08-30 18:43:35, no candidate inside lin_hop, support ws3 raw 2026-08-30 18:42:40 stamp 2026-08-30 18:43:35, ws4 raw 2026-08-30 18:43:25 stamp 2026-08-30 18:44:20, ws5 raw 2026-08-30 18:39:15 stamp 2026-08-30 18:40:10 \| latch 1 at the t1 cadence 2026-08-30 18:38:00, divergence state +1 \| rider cws6 89.23, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-30 18:44:20 | HOLD | cws6 | rider cws6 89.23 oob - no action |
| 2026-08-30 18:48:55 | BATON | cws6 | ws6 -> ws8, between cadences, lin_hop 2 |
| 2026-08-30 19:22:00 | CADENCE | cws8 | cws1b counter-oob cws1b 14.16 entered the LOW oob 19:22:00 \| rider cws8 81.01, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-30 19:22:00 | EXHAUST | cws8 | t4 at a cws1b counter-oob cadence - rider cws8 81.01, no candidate inside lin_hop 2 |

### trade 12 - 2026-08-30 19:22:05 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 19:26:00 | ARM | - | cws1b+cws1r: cws1b -7.44 + cws1r 12.71 oob |
| 2026-08-30 19:26:00 | RIDER | cws1 | cws1 r 12.71, the highest ex-fence |
| 2026-08-30 19:26:00 | RETEST | - | cws1r 12.71 oob + cws2r 36.76 / cws3r 45.91 in - the gate opens; cws1r oob->ib cross 2026-08-30 19:31:00, wob 12, cadence at 2026-08-30 19:31:55 |
| 2026-08-30 19:31:55 | EXHAUST | cws1 | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |

### trade 13 - 2026-08-30 19:32:00 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 20:12:00 | ARM | - | cws4r: cws4r 88.22 oob |
| 2026-08-30 20:12:00 | RIDER | cws4 | cws4 r 88.22, the highest ex-fence |
| 2026-08-30 20:12:00 | RETEST | - | cws1r 52.38 is not oob at the arm - the gate stays shut |
| 2026-08-30 20:32:55 | NO PASS | cws4 | cws4 80.72 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 20:54:55 | CADENCE | cws4 | t2 cws1r ib cross 20:54:00 confirmed 20:54:55 at wob 12, cws1b 59.76 not oob \| rider cws4 35.15, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 20:54:55 | EXHAUST | cws4 | t4 at a t2 cadence - rider cws4 35.15, no candidate on the whole board |

### trade 14 - 2026-08-30 20:55:00 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 21:02:00 | ARM | - | cws1b+cws1r: cws1b -21.58 + cws1r 8.90 oob |
| 2026-08-30 21:02:00 | RIDER | cws1 | cws1 r 8.90, the highest ex-fence |
| 2026-08-30 21:02:00 | RETEST | - | cws1r 8.90 oob + cws2r 43.68 / cws3r 61.43 in - the gate opens; cws1r oob->ib cross 2026-08-30 21:04:00, wob 12, cadence at 2026-08-30 21:04:55 |
| 2026-08-30 21:04:55 | EXHAUST | cws1 | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |

### trade 15 - 2026-08-30 21:05:00 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 22:00:00 | ARM | - | cws1b+cws1r: cws1b 102.90 + cws1r 97.10 oob |
| 2026-08-30 22:00:00 | RIDER | cws1 | cws1 r 97.10, the highest ex-fence |
| 2026-08-30 22:00:00 | RETEST | - | cws1r 97.10 oob + cws2r 60.57 / cws3r 40.02 in - the gate opens; cws1r oob->ib cross 2026-08-30 22:03:00, wob 12, cadence at 2026-08-30 22:03:55 |
| 2026-08-30 22:03:55 | EXHAUST | cws1 | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |

### trade 16 - 2026-08-30 22:04:00 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 22:24:00 | ARM | - | cws2Mage+cws2r: cws2Mage 5.22 + cws2r 10.29 oob |
| 2026-08-30 22:24:00 | DIV | - | cws1r divergence -1 bullish \| anchor_floater state -1 divergence, LONG |

| LATCH 1 armed | side | rider | stage | why |
|---|---|---|---|---|
| 2026-08-30 01:04:55 | LOW | cws2 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 01:04:55, divergence state -1 |
| 2026-08-30 01:21:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 01:21:00, divergence state -1 |
| 2026-08-30 02:00:55 | LOW | cws5 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 |
| 2026-08-30 02:30:00 | LOW | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 02:30:00, divergence state -1 |
| 2026-08-30 02:30:55 | LOW | cws5 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1 |
| 2026-08-30 03:19:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 03:19:00, divergence state -1 |
| 2026-08-30 03:43:55 | LOW | cws3 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 03:43:55, divergence state -1 |
| 2026-08-30 03:54:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 03:54:00, divergence state -1 |
| 2026-08-30 03:54:55 | LOW | cws3 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 03:54:55, divergence state -1 |
| 2026-08-30 04:13:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 04:13:00, divergence state -1 |
| 2026-08-30 07:44:00 | LOW | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 07:44:00, divergence state -1 |
| 2026-08-30 10:29:00 | HIGH | cws4 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 10:29:00, divergence state +1 |
| 2026-08-30 12:16:00 | HIGH | cws2 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 12:16:00, divergence state +1 |
| 2026-08-30 12:35:55 | HIGH | cws4 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 12:35:55, divergence state +1 |
| 2026-08-30 15:05:55 | LOW | cws5 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 15:05:55, divergence state -1 |
| 2026-08-30 18:38:00 | HIGH | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 18:38:00, divergence state +1 |

| the LATCH cadence | side | rider | stage | why |
|---|---|---|---|---|
| 2026-08-30 01:04:55 | LOW | cws2 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 01:04:55, divergence state -1 |
| 2026-08-30 01:21:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 01:21:00, divergence state -1 |
| 2026-08-30 02:00:55 | LOW | cws5 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 |
| 2026-08-30 02:04:05 | LOW | cws5 | NO ACTION | latch latch 2: rider cws5 reversed raw 2026-08-30 01:22:15 stamp 2026-08-30 01:23:10, no candidate inside lin_hop, support ws2 raw 2026-08-30 02:02:45 stamp 2026-08-30 02:03:40, ws3 raw 2026-08-30 02:03:10 stamp 2026-08-30 02:04:05, ws4 raw 2026-08-30 02:02:50 stamp 2026-08-30 02:03:45 \| latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:30:00 | LOW | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 02:30:00, divergence state -1 |
| 2026-08-30 02:30:55 | LOW | cws5 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1 |
| 2026-08-30 02:38:15 | LOW | cws5 | NO ACTION | latch latch 2: rider cws5 reversed raw 2026-08-30 01:22:15 stamp 2026-08-30 01:23:10, no candidate inside lin_hop, support ws2 raw 2026-08-30 02:37:05 stamp 2026-08-30 02:38:00, ws3 raw 2026-08-30 02:37:20 stamp 2026-08-30 02:38:15, ws4 raw 2026-08-30 02:37:05 stamp 2026-08-30 02:38:00 \| latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 03:19:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 03:19:00, divergence state -1 |
| 2026-08-30 03:43:55 | LOW | cws3 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 03:43:55, divergence state -1 |
| 2026-08-30 03:54:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 03:54:00, divergence state -1 |
| 2026-08-30 03:54:55 | LOW | cws3 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 03:54:55, divergence state -1 |
| 2026-08-30 04:13:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 04:13:00, divergence state -1 |
| 2026-08-30 07:44:00 | LOW | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 07:44:00, divergence state -1 |
| 2026-08-30 10:29:00 | HIGH | cws4 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 10:29:00, divergence state +1 |
| 2026-08-30 12:16:00 | HIGH | cws2 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 12:16:00, divergence state +1 |
| 2026-08-30 12:35:55 | HIGH | cws4 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 12:35:55, divergence state +1 |
| 2026-08-30 15:05:55 | LOW | cws5 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 15:05:55, divergence state -1 |
| 2026-08-30 18:38:00 | HIGH | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 18:38:00, divergence state +1 |
| 2026-08-30 18:44:20 | HIGH | cws6 | CADENCE | latch latch 2: rider cws6 reversed raw 2026-08-30 18:42:40 stamp 2026-08-30 18:43:35, no candidate inside lin_hop, support ws3 raw 2026-08-30 18:42:40 stamp 2026-08-30 18:43:35, ws4 raw 2026-08-30 18:43:25 stamp 2026-08-30 18:44:20, ws5 raw 2026-08-30 18:39:15 stamp 2026-08-30 18:40:10 \| latch 1 at the t1 cadence 2026-08-30 18:38:00, divergence state +1 \| rider cws6 89.23, no-longer-exfence no, reversed yes \| mage-cascade down |

| the cws1b counter-oob cadence | side | rider | stage | why |
|---|---|---|---|---|
| 2026-08-30 02:41:00 | LOW | cws5 | CADENCE | cws1b counter-oob cws1b 88.94 entered the HIGH oob 02:41:00 \| rider cws5 25.57, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 02:41:00 | LOW | cws5 | EXHAUST | t4 at a cws1b counter-oob cadence - rider cws5 25.57, no candidate inside lin_hop 2 |
| 2026-08-30 05:02:00 | LOW | cws3 | CADENCE | cws1b counter-oob cws1b 99.93 entered the HIGH oob 05:02:00 \| rider cws3 41.69, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 05:02:00 | LOW | cws3 | EXHAUST | t4 at a cws1b counter-oob cadence - rider cws3 41.69, no candidate inside lin_hop 2 |
| 2026-08-30 11:33:00 | HIGH | cws4 | CADENCE | cws1b counter-oob cws1b 12.90 entered the LOW oob 11:33:00 \| rider cws4 58.41, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-30 11:33:00 | HIGH | cws4 | EXHAUST | t4 at a cws1b counter-oob cadence - rider cws4 58.41, no candidate inside lin_hop 2 |
| 2026-08-30 12:04:00 | LOW | cws4 | CADENCE | cws1b counter-oob cws1b 96.64 entered the HIGH oob 12:04:00 \| rider cws4 43.98, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 12:04:00 | LOW | cws4 | EXHAUST | t4 at a cws1b counter-oob cadence - rider cws4 43.98, no candidate inside lin_hop 2 |
| 2026-08-30 19:22:00 | HIGH | cws8 | CADENCE | cws1b counter-oob cws1b 14.16 entered the LOW oob 19:22:00 \| rider cws8 81.01, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-30 19:22:00 | HIGH | cws8 | EXHAUST | t4 at a cws1b counter-oob cadence - rider cws8 81.01, no candidate inside lin_hop 2 |

NO t3 EVENT in the window.

## first side LOW  (783.8s)

| the read | value |
|---|---|
| walks | 16 |
| verdicts EXHAUST | 14 |
| verdicts NO ARM | 1 |
| verdicts NO VERDICT | 0 |
| verdicts DIV REV-TRADE | 1 |
| t1 cadence events | 4 |
| t2 cadence events | 5 |
| t3 cadence events | 0 |
| walks that reached a RETEST row | 14 |
|   the gate shut, cws1r not oob at the arm | 4 |
|   the gate shut, cws2r/cws3r not both in the fence | 2 |
|   the gate opened | 8 |
|   the gate opened, no oob->ib cross to the data end | 0 |
| the gate cadence ENDED the walk | 4 |
| the gate cadence RE-SCANNED a rider | 4 |
| BATON passes | 8 |
| LATCH1 armed | 16 |
| cadences taking NO ACTION on the mage-cascade | 16 |
| latch cadence events | 1 |
| cws1b counter-oob cadence events | 10 |

| the DIV branch read | arms |
|---|---|
| a divergence, LONG | 1 |
| PM, trend SHORT | 1 |
| all DIV arms | 2 |
|   of those, a REV-TRADE verdict | 1 |

| the gate cadence | side | what it did | why |
|---|---|---|---|
| 2026-08-30 01:04:55 | LOW | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 18.31, the highest ex-fence |
| 2026-08-30 02:46:55 | HIGH | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-08-30 03:06:55 | LOW | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 12.28, the highest ex-fence |
| 2026-08-30 05:07:55 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 83.86, the highest ex-fence |
| 2026-08-30 10:13:55 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws4 81.84, the highest ex-fence |
| 2026-08-30 19:31:55 | LOW | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-08-30 21:04:55 | LOW | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-08-30 22:03:55 | HIGH | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |

## THE REV-TRADES, and the bars that created each one

| # | the open | dir | the arm | the cadence that ended it | the exhaust = the rev-trade bar | the verdict | latch 1 fires | MAE % | MFE % | SP TF | the pivot | given % | leg MFE % | share |
#   THE EXHAUST BAR *IS* THE REV-TRADE BAR. An exhaust is only ever declared at a
#   cadence event bar, so every bar in that column is a cadence bar. The trade closes
#   there and the opposite side opens at that bar + 1, which is the NEXT row's open.
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-08-30 00:00:05 | SHORT | 2026-08-30 01:02:00 | cws1b counter-oob | 2026-08-30 02:41:00 | EXHAUST | 5 | -0.580 | +1.884 | ws2Mage | 2026-08-30 02:53:00 | +0.093 | 1.794 | 0.052 |
| 2 | 2026-08-30 02:41:05 | LONG | 2026-08-30 02:43:00 | retest | 2026-08-30 02:46:55 | EXHAUST | 0 | -0.288 | +0.077 | ws2Mage | 2026-08-30 02:38:25 | +0.129 | 0.480 | 0.269 |
| 3 | 2026-08-30 02:47:00 | SHORT | 2026-08-30 03:01:00 | cws1b counter-oob | 2026-08-30 05:02:00 | EXHAUST | 5 | -0.314 | +2.206 | ws1Mage | 2026-08-30 05:29:45 | +0.380 | 0.578 | 0.658 |
| 4 | 2026-08-30 05:02:05 | LONG | 2026-08-30 05:04:00 | t2 | 2026-08-30 05:52:55 | EXHAUST | 0 | -0.324 | +0.507 | ws1Mage | 2026-08-30 05:51:20 | +0.016 | 0.392 | 0.040 |
| 5 | 2026-08-30 05:53:00 | SHORT | 2026-08-30 07:26:00 | t1 | 2026-08-30 08:31:00 | EXHAUST | 1 | -1.279 | +0.512 | ws1Mage | 2026-08-30 09:17:05 | -0.084 | 0.614 | -0.137 |
| 6 | 2026-08-30 08:31:05 | LONG | 2026-08-30 10:11:00 | cws1b counter-oob | 2026-08-30 11:33:00 | EXHAUST | 1 | -1.017 | +0.320 | ws15Mage | 2026-08-30 11:52:25 | +0.306 | 1.840 | 0.166 |
| 7 | 2026-08-30 11:33:05 | SHORT | 2026-08-30 11:48:00 | cws1b counter-oob | 2026-08-30 12:04:00 | EXHAUST | 0 | -0.363 | +0.347 | ws2Mage | 2026-08-30 12:33:15 | +1.191 | 1.113 | 1.070 |
| 8 | 2026-08-30 12:04:05 | LONG | 2026-08-30 12:04:05 | t2 | 2026-08-30 12:35:55 | EXHAUST | 2 | -0.031 | +1.321 | ws1Mage | 2026-08-30 13:36:00 | +0.493 | 0.707 | 0.696 |
| 9 | 2026-08-30 12:36:00 | SHORT | 2026-08-30 14:40:00 | t2 | 2026-08-30 15:05:55 | EXHAUST | 1 | -1.955 | +0.516 | ws1Mage | 2026-08-30 15:11:00 | +0.514 | 0.893 | 0.576 |
| 10 | 2026-08-30 15:06:00 | LONG | 2026-08-30 18:34:00 | cws1b counter-oob | 2026-08-30 19:22:00 | EXHAUST | 1 | -3.827 | +1.257 | ws3Mage | 2026-08-30 21:01:40 | +5.016 | 2.640 | 1.900 |
| 11 | 2026-08-30 19:22:05 | SHORT | 2026-08-30 19:26:00 | retest | 2026-08-30 19:31:55 | EXHAUST | 0 | -0.059 | +0.704 | ws2Mage | 2026-08-30 19:01:15 | +1.014 | 5.400 | 0.188 |
| 12 | 2026-08-30 19:32:00 | LONG | 2026-08-30 20:12:00 | t2 | 2026-08-30 20:54:55 | EXHAUST | 0 | -4.635 | +0.005 | ws3Mage | 2026-08-30 21:48:05 | +1.249 | 1.885 | 0.663 |
| 13 | 2026-08-30 20:55:00 | SHORT | 2026-08-30 21:02:00 | retest | 2026-08-30 21:04:55 | EXHAUST | 0 | -0.132 | +1.955 | ws1Mage | 2026-08-30 21:38:05 | +0.403 | 1.032 | 0.390 |
| 14 | 2026-08-30 21:05:00 | LONG | 2026-08-30 22:00:00 | retest | 2026-08-30 22:03:55 | EXHAUST | 0 | -0.549 | +1.525 | ws3Mage | 2026-08-30 21:56:40 | +0.782 | 1.331 | 0.588 |
| 15 | 2026-08-30 22:04:00 | SHORT | 2026-08-30 22:24:00 | - | 2026-08-30 22:24:00 | DIV REV-TRADE | 0 | -0.006 | +1.684 | ws5Mage | 2026-08-31 08:42:25 | -1.017 | 2.107 | -0.483 |

| the read | value |
|---|---|
| rev-trades | 15 |
| sum MAE % | -15.359 |
| sum MFE % | +14.820 |
| median MAE % | -0.363 |
| median MFE % | +0.704 |
| worst MAE % | -4.635 |
| best MFE % | +2.206 |
| MFE > abs(MAE) | 8 of 15 |
| median share | 0.390 |
| sweep-pivot knobs | SP_PICK lowest_pct, SP_BAND 0.0, SP_CONTAIN 0, SP_XWOB 18, SP_ALIGN_S 300, SP_TFS wide |

| the latch 1 bar | trade | dir | rider | the cadence it armed on | the state |
|---|---|---|---|---|---|
| 2026-08-30 01:04:55 | 1 | SHORT | cws2 | t2 | -1 |
| 2026-08-30 01:21:00 | 1 | SHORT | cws3 | t1 | -1 |
| 2026-08-30 02:00:55 | 1 | SHORT | cws5 | t2 | -1 |
| 2026-08-30 02:30:00 | 1 | SHORT | cws5 | t1 | -1 |
| 2026-08-30 02:30:55 | 1 | SHORT | cws5 | t2 | -1 |
| 2026-08-30 03:19:00 | 3 | SHORT | cws3 | t1 | -1 |
| 2026-08-30 03:43:55 | 3 | SHORT | cws3 | t2 | -1 |
| 2026-08-30 03:54:00 | 3 | SHORT | cws3 | t1 | -1 |
| 2026-08-30 03:54:55 | 3 | SHORT | cws3 | t2 | -1 |
| 2026-08-30 04:13:00 | 3 | SHORT | cws3 | t1 | -1 |
| 2026-08-30 07:44:00 | 5 | SHORT | cws5 | t1 | -1 |
| 2026-08-30 10:29:00 | 6 | LONG | cws4 | t1 | +1 |
| 2026-08-30 12:16:00 | 8 | LONG | cws2 | t1 | +1 |
| 2026-08-30 12:35:55 | 8 | LONG | cws4 | t2 | +1 |
| 2026-08-30 15:05:55 | 9 | SHORT | cws5 | t2 | -1 |
| 2026-08-30 18:38:00 | 10 | LONG | cws5 | t1 | +1 |

### trade 1 - 2026-08-30 00:00:05 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 01:02:00 | ARM | - | cws1b+cws1r: cws1b -6.74 + cws1r 10.24 oob |
| 2026-08-30 01:02:00 | RIDER | cws1 | cws1 r 10.24, the highest ex-fence |
| 2026-08-30 01:02:00 | RETEST | - | cws1r 10.24 oob + cws2r 23.07 / cws3r 51.20 in - the gate opens; cws1r oob->ib cross 2026-08-30 01:04:00, wob 12, cadence at 2026-08-30 01:04:55 |
| 2026-08-30 01:04:55 | RIDER | cws2 | v4-arm-lineage-retest: the re-scan rides cws2 18.31, the highest ex-fence |
| 2026-08-30 01:04:55 | LATCH1 | cws2 | latch 1 at the t2 cadence 2026-08-30 01:04:55, divergence state -1 |
| 2026-08-30 01:04:55 | NO ACTION | cws2 | t2 cws1r ib cross 01:04:00 confirmed 01:04:55 at wob 12, cws1b 16.84 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 01:12:55 | BATON | cws2 | ws2 -> ws3, between cadences, lin_hop 2 |
| 2026-08-30 01:21:00 | LATCH1 | cws3 | latch 1 at the t1 cadence 2026-08-30 01:21:00, divergence state -1 |
| 2026-08-30 01:21:00 | NO ACTION | cws3 | t1 cws1b oob 01:06:00..01:20:55, cws1r reversed 01:20:00 during, stamp 01:20:00 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 01:21:55 | BATON | cws3 | ws3 -> ws5, between cadences, lin_hop 2 |
| 2026-08-30 01:35:55 | NO PASS | cws5 | cws5 27.32 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 01:46:55 | NO ACTION | cws5 | t2 cws1r ib cross 01:46:00 confirmed 01:46:55 at wob 12, cws1b 60.31 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:00:55 | LATCH1 | cws5 | latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 |
| 2026-08-30 02:00:55 | NO ACTION | cws5 | t2 cws1r ib cross 02:00:00 confirmed 02:00:55 at wob 12, cws1b 39.39 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:04:05 | NO ACTION | cws5 | latch latch 2: rider cws5 reversed raw 2026-08-30 01:22:15 stamp 2026-08-30 01:23:10, no candidate inside lin_hop, support ws2 raw 2026-08-30 02:02:45 stamp 2026-08-30 02:03:40, ws3 raw 2026-08-30 02:03:10 stamp 2026-08-30 02:04:05, ws4 raw 2026-08-30 02:02:50 stamp 2026-08-30 02:03:45 \| latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:30:00 | LATCH1 | cws5 | latch 1 at the t1 cadence 2026-08-30 02:30:00, divergence state -1 |
| 2026-08-30 02:30:00 | NO ACTION | cws5 | t1 cws1b ib 02:28:00, cws1r reversed 02:30:00 inside the 120s grace, stamp 02:30:00 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:30:55 | LATCH1 | cws5 | latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1 |
| 2026-08-30 02:30:55 | NO ACTION | cws5 | t2 cws1r ib cross 02:30:00 confirmed 02:30:55 at wob 12, cws1b 33.31 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:38:15 | NO ACTION | cws5 | latch latch 2: rider cws5 reversed raw 2026-08-30 01:22:15 stamp 2026-08-30 01:23:10, no candidate inside lin_hop, support ws2 raw 2026-08-30 02:37:05 stamp 2026-08-30 02:38:00, ws3 raw 2026-08-30 02:37:20 stamp 2026-08-30 02:38:15, ws4 raw 2026-08-30 02:37:05 stamp 2026-08-30 02:38:00 \| latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:41:00 | CADENCE | cws5 | cws1b counter-oob cws1b 88.94 entered the HIGH oob 02:41:00 \| rider cws5 25.57, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 02:41:00 | EXHAUST | cws5 | t4 at a cws1b counter-oob cadence - rider cws5 25.57, no candidate inside lin_hop 2 |

### trade 2 - 2026-08-30 02:41:05 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 02:43:00 | ARM | - | cws1b+cws1r: cws1b 108.98 + cws1r 89.24 oob |
| 2026-08-30 02:43:00 | RIDER | cws1 | cws1 r 89.24, the highest ex-fence |
| 2026-08-30 02:43:00 | RETEST | - | cws1r 89.24 oob + cws2r 52.29 / cws3r 44.78 in - the gate opens; cws1r oob->ib cross 2026-08-30 02:46:00, wob 12, cadence at 2026-08-30 02:46:55 |
| 2026-08-30 02:46:55 | EXHAUST | cws1 | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |

### trade 3 - 2026-08-30 02:47:00 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 03:01:00 | ARM | - | cws1b+cws1r: cws1b 3.75 + cws1r 7.68 oob |
| 2026-08-30 03:01:00 | RIDER | cws1 | cws1 r 7.68, the highest ex-fence |
| 2026-08-30 03:01:00 | RETEST | - | cws1r 7.68 oob + cws2r 22.13 / cws3r 55.36 in - the gate opens; cws1r oob->ib cross 2026-08-30 03:06:00, wob 12, cadence at 2026-08-30 03:06:55 |
| 2026-08-30 03:06:55 | RIDER | cws2 | v4-arm-lineage-retest: the re-scan rides cws2 12.28, the highest ex-fence |
| 2026-08-30 03:12:55 | BATON | cws2 | ws2 -> ws3, between cadences, lin_hop 2 |
| 2026-08-30 03:19:00 | LATCH1 | cws3 | latch 1 at the t1 cadence 2026-08-30 03:19:00, divergence state -1 |
| 2026-08-30 03:19:00 | NO ACTION | cws3 | t1 cws1b oob 03:01:00..03:18:55, cws1r reversed 03:09:00 during, stamp 03:09:00 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 03:21:55 | NO PASS | cws3 | cws3 26.79 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 03:43:55 | LATCH1 | cws3 | latch 1 at the t2 cadence 2026-08-30 03:43:55, divergence state -1 |
| 2026-08-30 03:43:55 | NO ACTION | cws3 | t2 cws1r ib cross 03:43:00 confirmed 03:43:55 at wob 12, cws1b 43.12 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 03:54:00 | LATCH1 | cws3 | latch 1 at the t1 cadence 2026-08-30 03:54:00, divergence state -1 |
| 2026-08-30 03:54:00 | NO ACTION | cws3 | t1 cws1b oob 03:50:00..03:53:55, cws1r reversed 03:53:00 during, stamp 03:53:00 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 03:54:55 | LATCH1 | cws3 | latch 1 at the t2 cadence 2026-08-30 03:54:55, divergence state -1 |
| 2026-08-30 03:54:55 | NO ACTION | cws3 | t2 cws1r ib cross 03:54:00 confirmed 03:54:55 at wob 12, cws1b 17.82 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 04:13:00 | LATCH1 | cws3 | latch 1 at the t1 cadence 2026-08-30 04:13:00, divergence state -1 |
| 2026-08-30 04:13:00 | NO ACTION | cws3 | t1 cws1b oob 04:06:00..04:12:55, cws1r reversed 04:08:00 during, stamp 04:08:00 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 04:15:55 | NO PASS | cws3 | cws3 21.39 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 05:02:00 | CADENCE | cws3 | cws1b counter-oob cws1b 99.93 entered the HIGH oob 05:02:00 \| rider cws3 41.69, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 05:02:00 | EXHAUST | cws3 | t4 at a cws1b counter-oob cadence - rider cws3 41.69, no candidate inside lin_hop 2 |

### trade 4 - 2026-08-30 05:02:05 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 05:04:00 | ARM | - | cws1b+cws1r: cws1b 115.76 + cws1r 85.53 oob |
| 2026-08-30 05:04:00 | RIDER | cws1 | cws1 r 85.53, the highest ex-fence |
| 2026-08-30 05:04:00 | RETEST | - | cws1r 85.53 oob + cws2r 75.45 / cws3r 52.02 in - the gate opens; cws1r oob->ib cross 2026-08-30 05:07:00, wob 12, cadence at 2026-08-30 05:07:55 |
| 2026-08-30 05:07:55 | RIDER | cws2 | v4-arm-lineage-retest: the re-scan rides cws2 83.86, the highest ex-fence |
| 2026-08-30 05:11:00 | CADENCE | cws2 | t1 cws1b oob 05:02:00..05:10:55, cws1r reversed 05:07:00 during, stamp 05:07:00 \| rider cws2 90.23, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-30 05:11:00 | HOLD | cws2 | rider cws2 90.23 oob - no action |
| 2026-08-30 05:12:55 | NO PASS | cws2 | cws2 81.72 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 05:52:55 | CADENCE | cws2 | t2 cws1r ib cross 05:52:00 confirmed 05:52:55 at wob 12, cws1b 35.84 not oob \| rider cws2 66.84, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 05:52:55 | EXHAUST | cws2 | t4 at a t2 cadence - rider cws2 66.84, no candidate on the whole board |

### trade 5 - 2026-08-30 05:53:00 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 07:26:00 | ARM | - | cws1b+cws1r: cws1b -3.43 + cws1r 12.64 oob |
| 2026-08-30 07:26:00 | RIDER | cws3 | cws3 r 12.22, the highest ex-fence |
| 2026-08-30 07:26:00 | RETEST | - | cws2r 18.89 / cws3r 12.22 - not both inside the fence at the arm |
| 2026-08-30 07:30:55 | BATON | cws3 | ws3 -> ws5, between cadences, lin_hop 2 |
| 2026-08-30 07:44:00 | LATCH1 | cws5 | latch 1 at the t1 cadence 2026-08-30 07:44:00, divergence state -1 |
| 2026-08-30 07:44:00 | CADENCE | cws5 | t1 cws1b oob 07:26:00..07:43:55, cws1r reversed 07:40:00 during, stamp 07:40:00 \| rider cws5 0.59, no-longer-exfence no, reversed no \| mage-cascade up |
| 2026-08-30 07:44:00 | BATON | cws5 | ws5 -> ws7, at a t1 cadence, whole board |
| 2026-08-30 08:03:55 | NO PASS | cws7 | cws7 24.05 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 08:31:00 | CADENCE | cws7 | t1 cws1b ib 08:29:00, cws1r reversed 08:31:00 inside the 120s grace, stamp 08:31:00 \| rider cws7 56.66, no-longer-exfence yes, reversed yes \| mage-cascade neither |
| 2026-08-30 08:31:00 | EXHAUST | cws7 | t4 at a t1 cadence - rider cws7 56.66, no candidate on the whole board |

### trade 6 - 2026-08-30 08:31:05 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 10:11:00 | ARM | - | cws1b+cws1r: cws1b 114.29 + cws1r 86.09 oob |
| 2026-08-30 10:11:00 | RIDER | cws1 | cws1 r 86.09, the highest ex-fence |
| 2026-08-30 10:11:00 | RETEST | - | cws1r 86.09 oob + cws2r 63.89 / cws3r 64.12 in - the gate opens; cws1r oob->ib cross 2026-08-30 10:13:00, wob 12, cadence at 2026-08-30 10:13:55 |
| 2026-08-30 10:13:55 | RIDER | cws4 | v4-arm-lineage-retest: the re-scan rides cws4 81.84, the highest ex-fence |
| 2026-08-30 10:13:55 | CADENCE | cws4 | t2 cws1r ib cross 10:13:00 confirmed 10:13:55 at wob 12, cws1b 77.01 not oob \| rider cws4 81.84, no-longer-exfence no, reversed no \| mage-cascade down |
| 2026-08-30 10:13:55 | HOLD | cws4 | rider cws4 81.84 ex-fence and not reversed - no action |
| 2026-08-30 10:16:55 | NO PASS | cws4 | cws4 77.93 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 10:29:00 | LATCH1 | cws4 | latch 1 at the t1 cadence 2026-08-30 10:29:00, divergence state +1 |
| 2026-08-30 10:29:00 | NO ACTION | cws4 | t1 cws1b oob 10:23:00..10:28:55, cws1r reversed 10:27:00 during, stamp 10:27:00 \| mage-cascade up matches the LONG - no action, keep walking |
| 2026-08-30 10:36:55 | NO PASS | cws4 | cws4 77.93 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 11:12:55 | NO ACTION | cws4 | t2 cws1r ib cross 11:12:00 confirmed 11:12:55 at wob 12, cws1b 64.97 not oob \| mage-cascade up matches the LONG - no action, keep walking |
| 2026-08-30 11:33:00 | CADENCE | cws4 | cws1b counter-oob cws1b 12.90 entered the LOW oob 11:33:00 \| rider cws4 58.41, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-30 11:33:00 | EXHAUST | cws4 | t4 at a cws1b counter-oob cadence - rider cws4 58.41, no candidate inside lin_hop 2 |

### trade 7 - 2026-08-30 11:33:05 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 11:48:00 | ARM | - | cws4r: cws4r 12.52 oob |
| 2026-08-30 11:48:00 | RIDER | cws4 | cws4 r 12.52, the highest ex-fence |
| 2026-08-30 11:48:00 | RETEST | - | cws1r 49.22 is not oob at the arm - the gate stays shut |
| 2026-08-30 11:56:55 | NO PASS | cws4 | cws4 19.77 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 12:04:00 | CADENCE | cws4 | cws1b counter-oob cws1b 96.64 entered the HIGH oob 12:04:00 \| rider cws4 43.98, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 12:04:00 | EXHAUST | cws4 | t4 at a cws1b counter-oob cadence - rider cws4 43.98, no candidate inside lin_hop 2 |

### trade 8 - 2026-08-30 12:04:05 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 12:04:05 | ARM | - | cws2Mage+cws2r: cws2Mage 90.48 + cws2r 92.13 oob |
| 2026-08-30 12:04:05 | DIV | - | cws1r divergence none \| anchor_floater state +2 PM, trend SHORT |
| 2026-08-30 12:04:05 | RIDER | cws2 | cws2 r 92.13, the highest ex-fence |
| 2026-08-30 12:04:05 | RETEST | - | cws1r 79.80 is not oob at the arm - the gate stays shut |
| 2026-08-30 12:16:00 | LATCH1 | cws2 | latch 1 at the t1 cadence 2026-08-30 12:16:00, divergence state +1 |
| 2026-08-30 12:16:00 | NO ACTION | cws2 | t1 cws1b oob 12:04:00..12:15:55, cws1r reversed 12:12:00 during, stamp 12:12:00 \| mage-cascade up matches the LONG - no action, keep walking |
| 2026-08-30 12:16:55 | BATON | cws2 | ws2 -> ws4, between cadences, lin_hop 2 |
| 2026-08-30 12:24:55 | NO PASS | cws4 | cws4 83.00 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 12:35:55 | LATCH1 | cws4 | latch 1 at the t2 cadence 2026-08-30 12:35:55, divergence state +1 |
| 2026-08-30 12:35:55 | CADENCE | cws4 | t2 cws1r ib cross 12:35:00 confirmed 12:35:55 at wob 12, cws1b 66.45 not oob \| rider cws4 60.47, no-longer-exfence yes, reversed yes \| mage-cascade neither |
| 2026-08-30 12:35:55 | EXHAUST | cws4 | t4 at a t2 cadence - rider cws4 60.47, no candidate on the whole board |

### trade 9 - 2026-08-30 12:36:00 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 14:40:00 | ARM | - | cws4r: cws4r 12.14 oob |
| 2026-08-30 14:40:00 | RIDER | cws5 | cws5 r 15.81, the highest ex-fence |
| 2026-08-30 14:40:00 | RETEST | - | cws1r 28.69 is not oob at the arm - the gate stays shut |
| 2026-08-30 14:55:55 | NO PASS | cws5 | cws5 20.65 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 15:05:55 | LATCH1 | cws5 | latch 1 at the t2 cadence 2026-08-30 15:05:55, divergence state -1 |
| 2026-08-30 15:05:55 | CADENCE | cws5 | t2 cws1r ib cross 15:05:00 confirmed 15:05:55 at wob 12, cws1b 40.26 not oob \| rider cws5 40.40, no-longer-exfence yes, reversed yes \| mage-cascade neither |
| 2026-08-30 15:05:55 | EXHAUST | cws5 | t4 at a t2 cadence - rider cws5 40.40, no candidate on the whole board |

### trade 10 - 2026-08-30 15:06:00 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 18:34:00 | ARM | - | cws1b+cws1r: cws1b 96.35 + cws1r 88.13 oob |
| 2026-08-30 18:34:00 | RIDER | cws5 | cws5 r 80.58, the highest ex-fence |
| 2026-08-30 18:34:00 | RETEST | - | cws2r 82.90 / cws3r 50.95 - not both inside the fence at the arm |
| 2026-08-30 18:38:00 | LATCH1 | cws5 | latch 1 at the t1 cadence 2026-08-30 18:38:00, divergence state +1 |
| 2026-08-30 18:38:00 | CADENCE | cws5 | t1 cws1b oob 18:32:00..18:37:55, cws1r reversed 18:37:00 during, stamp 18:37:00 \| rider cws5 80.58, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-30 18:38:00 | BATON | cws5 | ws5 -> ws6, at a t1 cadence, whole board |
| 2026-08-30 18:44:20 | CADENCE | cws6 | latch latch 2: rider cws6 reversed raw 2026-08-30 18:42:40 stamp 2026-08-30 18:43:35, no candidate inside lin_hop, support ws3 raw 2026-08-30 18:42:40 stamp 2026-08-30 18:43:35, ws4 raw 2026-08-30 18:43:25 stamp 2026-08-30 18:44:20, ws5 raw 2026-08-30 18:39:15 stamp 2026-08-30 18:40:10 \| latch 1 at the t1 cadence 2026-08-30 18:38:00, divergence state +1 \| rider cws6 89.23, no-longer-exfence no, reversed yes \| mage-cascade down |
| 2026-08-30 18:44:20 | HOLD | cws6 | rider cws6 89.23 oob - no action |
| 2026-08-30 18:48:55 | BATON | cws6 | ws6 -> ws8, between cadences, lin_hop 2 |
| 2026-08-30 19:22:00 | CADENCE | cws8 | cws1b counter-oob cws1b 14.16 entered the LOW oob 19:22:00 \| rider cws8 81.01, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-30 19:22:00 | EXHAUST | cws8 | t4 at a cws1b counter-oob cadence - rider cws8 81.01, no candidate inside lin_hop 2 |

### trade 11 - 2026-08-30 19:22:05 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 19:26:00 | ARM | - | cws1b+cws1r: cws1b -7.44 + cws1r 12.71 oob |
| 2026-08-30 19:26:00 | RIDER | cws1 | cws1 r 12.71, the highest ex-fence |
| 2026-08-30 19:26:00 | RETEST | - | cws1r 12.71 oob + cws2r 36.76 / cws3r 45.91 in - the gate opens; cws1r oob->ib cross 2026-08-30 19:31:00, wob 12, cadence at 2026-08-30 19:31:55 |
| 2026-08-30 19:31:55 | EXHAUST | cws1 | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |

### trade 12 - 2026-08-30 19:32:00 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 20:12:00 | ARM | - | cws4r: cws4r 88.22 oob |
| 2026-08-30 20:12:00 | RIDER | cws4 | cws4 r 88.22, the highest ex-fence |
| 2026-08-30 20:12:00 | RETEST | - | cws1r 52.38 is not oob at the arm - the gate stays shut |
| 2026-08-30 20:32:55 | NO PASS | cws4 | cws4 80.72 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 20:54:55 | CADENCE | cws4 | t2 cws1r ib cross 20:54:00 confirmed 20:54:55 at wob 12, cws1b 59.76 not oob \| rider cws4 35.15, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 20:54:55 | EXHAUST | cws4 | t4 at a t2 cadence - rider cws4 35.15, no candidate on the whole board |

### trade 13 - 2026-08-30 20:55:00 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 21:02:00 | ARM | - | cws1b+cws1r: cws1b -21.58 + cws1r 8.90 oob |
| 2026-08-30 21:02:00 | RIDER | cws1 | cws1 r 8.90, the highest ex-fence |
| 2026-08-30 21:02:00 | RETEST | - | cws1r 8.90 oob + cws2r 43.68 / cws3r 61.43 in - the gate opens; cws1r oob->ib cross 2026-08-30 21:04:00, wob 12, cadence at 2026-08-30 21:04:55 |
| 2026-08-30 21:04:55 | EXHAUST | cws1 | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |

### trade 14 - 2026-08-30 21:05:00 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 22:00:00 | ARM | - | cws1b+cws1r: cws1b 102.90 + cws1r 97.10 oob |
| 2026-08-30 22:00:00 | RIDER | cws1 | cws1 r 97.10, the highest ex-fence |
| 2026-08-30 22:00:00 | RETEST | - | cws1r 97.10 oob + cws2r 60.57 / cws3r 40.02 in - the gate opens; cws1r oob->ib cross 2026-08-30 22:03:00, wob 12, cadence at 2026-08-30 22:03:55 |
| 2026-08-30 22:03:55 | EXHAUST | cws1 | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |

### trade 15 - 2026-08-30 22:04:00 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 22:24:00 | ARM | - | cws2Mage+cws2r: cws2Mage 5.22 + cws2r 10.29 oob |
| 2026-08-30 22:24:00 | DIV | - | cws1r divergence -1 bullish \| anchor_floater state -1 divergence, LONG |

| LATCH 1 armed | side | rider | stage | why |
|---|---|---|---|---|
| 2026-08-30 01:04:55 | LOW | cws2 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 01:04:55, divergence state -1 |
| 2026-08-30 01:21:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 01:21:00, divergence state -1 |
| 2026-08-30 02:00:55 | LOW | cws5 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 |
| 2026-08-30 02:30:00 | LOW | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 02:30:00, divergence state -1 |
| 2026-08-30 02:30:55 | LOW | cws5 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1 |
| 2026-08-30 03:19:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 03:19:00, divergence state -1 |
| 2026-08-30 03:43:55 | LOW | cws3 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 03:43:55, divergence state -1 |
| 2026-08-30 03:54:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 03:54:00, divergence state -1 |
| 2026-08-30 03:54:55 | LOW | cws3 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 03:54:55, divergence state -1 |
| 2026-08-30 04:13:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 04:13:00, divergence state -1 |
| 2026-08-30 07:44:00 | LOW | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 07:44:00, divergence state -1 |
| 2026-08-30 10:29:00 | HIGH | cws4 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 10:29:00, divergence state +1 |
| 2026-08-30 12:16:00 | HIGH | cws2 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 12:16:00, divergence state +1 |
| 2026-08-30 12:35:55 | HIGH | cws4 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 12:35:55, divergence state +1 |
| 2026-08-30 15:05:55 | LOW | cws5 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 15:05:55, divergence state -1 |
| 2026-08-30 18:38:00 | HIGH | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 18:38:00, divergence state +1 |

| the LATCH cadence | side | rider | stage | why |
|---|---|---|---|---|
| 2026-08-30 01:04:55 | LOW | cws2 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 01:04:55, divergence state -1 |
| 2026-08-30 01:21:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 01:21:00, divergence state -1 |
| 2026-08-30 02:00:55 | LOW | cws5 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 |
| 2026-08-30 02:04:05 | LOW | cws5 | NO ACTION | latch latch 2: rider cws5 reversed raw 2026-08-30 01:22:15 stamp 2026-08-30 01:23:10, no candidate inside lin_hop, support ws2 raw 2026-08-30 02:02:45 stamp 2026-08-30 02:03:40, ws3 raw 2026-08-30 02:03:10 stamp 2026-08-30 02:04:05, ws4 raw 2026-08-30 02:02:50 stamp 2026-08-30 02:03:45 \| latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:30:00 | LOW | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 02:30:00, divergence state -1 |
| 2026-08-30 02:30:55 | LOW | cws5 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1 |
| 2026-08-30 02:38:15 | LOW | cws5 | NO ACTION | latch latch 2: rider cws5 reversed raw 2026-08-30 01:22:15 stamp 2026-08-30 01:23:10, no candidate inside lin_hop, support ws2 raw 2026-08-30 02:37:05 stamp 2026-08-30 02:38:00, ws3 raw 2026-08-30 02:37:20 stamp 2026-08-30 02:38:15, ws4 raw 2026-08-30 02:37:05 stamp 2026-08-30 02:38:00 \| latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 03:19:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 03:19:00, divergence state -1 |
| 2026-08-30 03:43:55 | LOW | cws3 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 03:43:55, divergence state -1 |
| 2026-08-30 03:54:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 03:54:00, divergence state -1 |
| 2026-08-30 03:54:55 | LOW | cws3 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 03:54:55, divergence state -1 |
| 2026-08-30 04:13:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 04:13:00, divergence state -1 |
| 2026-08-30 07:44:00 | LOW | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 07:44:00, divergence state -1 |
| 2026-08-30 10:29:00 | HIGH | cws4 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 10:29:00, divergence state +1 |
| 2026-08-30 12:16:00 | HIGH | cws2 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 12:16:00, divergence state +1 |
| 2026-08-30 12:35:55 | HIGH | cws4 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 12:35:55, divergence state +1 |
| 2026-08-30 15:05:55 | LOW | cws5 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 15:05:55, divergence state -1 |
| 2026-08-30 18:38:00 | HIGH | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 18:38:00, divergence state +1 |
| 2026-08-30 18:44:20 | HIGH | cws6 | CADENCE | latch latch 2: rider cws6 reversed raw 2026-08-30 18:42:40 stamp 2026-08-30 18:43:35, no candidate inside lin_hop, support ws3 raw 2026-08-30 18:42:40 stamp 2026-08-30 18:43:35, ws4 raw 2026-08-30 18:43:25 stamp 2026-08-30 18:44:20, ws5 raw 2026-08-30 18:39:15 stamp 2026-08-30 18:40:10 \| latch 1 at the t1 cadence 2026-08-30 18:38:00, divergence state +1 \| rider cws6 89.23, no-longer-exfence no, reversed yes \| mage-cascade down |

| the cws1b counter-oob cadence | side | rider | stage | why |
|---|---|---|---|---|
| 2026-08-30 02:41:00 | LOW | cws5 | CADENCE | cws1b counter-oob cws1b 88.94 entered the HIGH oob 02:41:00 \| rider cws5 25.57, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 02:41:00 | LOW | cws5 | EXHAUST | t4 at a cws1b counter-oob cadence - rider cws5 25.57, no candidate inside lin_hop 2 |
| 2026-08-30 05:02:00 | LOW | cws3 | CADENCE | cws1b counter-oob cws1b 99.93 entered the HIGH oob 05:02:00 \| rider cws3 41.69, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 05:02:00 | LOW | cws3 | EXHAUST | t4 at a cws1b counter-oob cadence - rider cws3 41.69, no candidate inside lin_hop 2 |
| 2026-08-30 11:33:00 | HIGH | cws4 | CADENCE | cws1b counter-oob cws1b 12.90 entered the LOW oob 11:33:00 \| rider cws4 58.41, no-longer-exfence yes, reversed yes \| mage-cascade up |
| 2026-08-30 11:33:00 | HIGH | cws4 | EXHAUST | t4 at a cws1b counter-oob cadence - rider cws4 58.41, no candidate inside lin_hop 2 |
| 2026-08-30 12:04:00 | LOW | cws4 | CADENCE | cws1b counter-oob cws1b 96.64 entered the HIGH oob 12:04:00 \| rider cws4 43.98, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 12:04:00 | LOW | cws4 | EXHAUST | t4 at a cws1b counter-oob cadence - rider cws4 43.98, no candidate inside lin_hop 2 |
| 2026-08-30 19:22:00 | HIGH | cws8 | CADENCE | cws1b counter-oob cws1b 14.16 entered the LOW oob 19:22:00 \| rider cws8 81.01, no-longer-exfence no, reversed yes \| mage-cascade up |
| 2026-08-30 19:22:00 | HIGH | cws8 | EXHAUST | t4 at a cws1b counter-oob cadence - rider cws8 81.01, no candidate inside lin_hop 2 |

NO t3 EVENT in the window.
