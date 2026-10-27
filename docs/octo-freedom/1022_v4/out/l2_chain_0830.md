# lineage2 chained, 2026-08-30 00:00:00 .. 2026-08-30 23:59:55
# t3 needs max(2, round(0.75 x the ex-fence population)) reversals, matryoshka ws7..rider-1
# gate closed | lin_hop 2 lifted only at t1/t2 | RULED_OK True

## first side HIGH  (403.0s)

| the read | value |
|---|---|
| walks | 17 |
| verdicts EXHAUST | 15 |
| verdicts NO ARM | 1 |
| verdicts NO VERDICT | 0 |
| verdicts DIV REV-TRADE | 1 |
| t1 cadence events | 0 |
| t2 cadence events | 2 |
| t3 cadence events | 0 |
| walks that reached a RETEST row | 15 |
|   the gate shut, cws1r not oob at the arm | 4 |
|   the gate shut, cws2r/cws3r not both in the fence | 2 |
|   the gate opened | 9 |
|   the gate opened, no oob->ib cross to the data end | 0 |
| the gate cadence ENDED the walk | 5 |
| the gate cadence RE-SCANNED a rider | 4 |
| BATON passes | 10 |
| LATCH1 armed | 17 |
| cadences taking NO ACTION on the mage-cascade | 13 |
| latch cadence events | 0 |
| cws1b counter-oob cadence events | 4 |

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

| # | the open | dir | the arm | the cadence that ended it | the exhaust = the rev-trade bar | the verdict | MAE % | MFE % | capped | SP TF | the pivot | leg MFE % | ended by |
#   THE EXHAUST BAR *IS* THE REV-TRADE BAR. An exhaust is only ever declared at a
#   cadence event bar, so every bar in that column is a cadence bar. The trade closes
#   there and the opposite side opens at that bar + 1, which is the NEXT row's open.
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-08-30 00:00:05 | LONG | 2026-08-30 00:18:00 | retest | 2026-08-30 00:20:55 | EXHAUST | -0.529 | +0.580 | - | ws1Mage | 2026-08-30 00:10:30 | 1.002 | the board review |
| 2 | 2026-08-30 00:21:00 | SHORT | 2026-08-30 01:02:00 | barrage | 2026-08-30 02:35:20 | EXHAUST | -0.117 | +1.829 | - | ws2Mage | 2026-08-30 02:53:00 | 1.794 | the barrage |
| 3 | 2026-08-30 02:35:25 | LONG | 2026-08-30 02:43:00 | retest | 2026-08-30 02:46:55 | EXHAUST | -0.165 | +0.506 | - | ws2Mage | 2026-08-30 02:38:25 | 0.480 | the board review |
| 4 | 2026-08-30 02:47:00 | SHORT | 2026-08-30 03:01:00 | cws1b counter-oob | 2026-08-30 05:02:00 | EXHAUST | -0.314 | +2.206 | - | ws1Mage | 2026-08-30 05:29:45 | 0.578 | the board review |
| 5 | 2026-08-30 05:02:05 | LONG | 2026-08-30 05:04:00 | t1 | 2026-08-30 05:11:00 | EXHAUST | -0.031 | +0.507 | - | ws1Mage | 2026-08-30 04:56:30 | 0.971 | the mage-cascade mismatch |
| 6 | 2026-08-30 05:11:05 | SHORT | 2026-08-30 07:26:00 | t1 | 2026-08-30 07:44:00 | EXHAUST | -1.100 | +0.000 | YES | ws5Mage | 2026-08-30 07:12:20 | 1.228 | the mage-cascade mismatch |
| 7 | 2026-08-30 07:44:05 | LONG | 2026-08-30 10:11:00 | t2 | 2026-08-30 10:13:55 | EXHAUST | -1.100 | +0.000 | YES | ws15Mage | 2026-08-30 11:52:25 | 1.840 | the mage-cascade mismatch |
| 8 | 2026-08-30 10:14:00 | SHORT | 2026-08-30 11:48:00 | cws1b counter-oob | 2026-08-30 12:04:00 | EXHAUST | -0.817 | +0.058 | - | ws2Mage | 2026-08-30 12:33:15 | 1.113 | the board review |
| 9 | 2026-08-30 12:04:05 | LONG | 2026-08-30 12:04:05 | t2 | 2026-08-30 12:35:55 | EXHAUST | -0.031 | +1.321 | - | ws1Mage | 2026-08-30 13:36:00 | 0.707 | the board review |
| 10 | 2026-08-30 12:36:00 | SHORT | 2026-08-30 14:40:00 | t2 | 2026-08-30 15:45:55 | EXHAUST | -1.100 | +0.000 | YES | ws20Mage | 2026-08-30 16:25:10 | 3.965 | the mage-cascade mismatch |
| 11 | 2026-08-30 15:46:00 | LONG | 2026-08-30 18:34:00 | t1 | 2026-08-30 18:38:00 | EXHAUST | -1.100 | +0.000 | YES | ws2Mage | 2026-08-30 17:57:25 | 1.143 | the mage-cascade mismatch |
| 12 | 2026-08-30 18:38:05 | SHORT | 2026-08-30 19:26:00 | retest | 2026-08-30 19:31:55 | EXHAUST | -0.265 | +1.247 | - | ws2Mage | 2026-08-30 19:01:15 | 5.400 | the board review |
| 13 | 2026-08-30 19:32:00 | LONG | 2026-08-30 20:12:00 | t2 | 2026-08-30 20:54:55 | EXHAUST | -1.100 | +0.000 | YES | ws3Mage | 2026-08-30 21:48:05 | 1.885 | the mage-cascade mismatch |
| 14 | 2026-08-30 20:55:00 | SHORT | 2026-08-30 21:02:00 | retest | 2026-08-30 21:04:55 | EXHAUST | -0.132 | +1.955 | - | ws1Mage | 2026-08-30 21:38:05 | 1.032 | the board review |
| 15 | 2026-08-30 21:05:00 | LONG | 2026-08-30 22:00:00 | retest | 2026-08-30 22:03:55 | EXHAUST | -0.549 | +1.525 | - | ws3Mage | 2026-08-30 21:56:40 | 1.331 | the board review |
| 16 | 2026-08-30 22:04:00 | SHORT | 2026-08-30 22:24:00 | - | 2026-08-30 22:24:00 | DIV REV-TRADE | -0.006 | +1.684 | - | ws5Mage | 2026-08-31 08:42:25 | 2.107 | the board review |

| the read | value |
|---|---|
| trades capped at MAE 1.10% | 5 of 16 |
| ended by a mage-cascade mismatch | 6 |
| ended by the barrage | 1 |
| ended by the cadence board review | 9 |
| the mismatch action | rev-trade |

| the read | value |
|---|---|
| rev-trades | 16 |
| sum MAE % | -8.458 |
| sum MFE % | +13.418 |
| median MAE % | -0.314 |
| median MFE % | +0.580 |
| worst MAE % | -1.100 |
| best MFE % | +2.206 |
| MFE > abs(MAE) | 10 of 16 |
| sweep-pivot knobs | SP_PICK lowest_pct, SP_BAND 0.0, SP_CONTAIN 0, SP_XWOB 18, SP_ALIGN_S 300, SP_TFS wide |

| the latch 1 bar | trade | dir | rider | the cadence it armed on | the state |
|---|---|---|---|---|---|
| 2026-08-30 01:04:55 | 2 | SHORT | cws2 | t2 | -1 |
| 2026-08-30 01:21:00 | 2 | SHORT | cws3 | t1 | -1 |
| 2026-08-30 02:00:55 | 2 | SHORT | cws6 | t2 | -1 |
| 2026-08-30 02:30:00 | 2 | SHORT | cws6 | t1 | -1 |
| 2026-08-30 02:30:55 | 2 | SHORT | cws6 | t2 | -1 |
| 2026-08-30 02:35:20 | 2 | SHORT | cws6 | barrage | -1 |
| 2026-08-30 03:19:00 | 4 | SHORT | cws3 | t1 | -1 |
| 2026-08-30 03:43:55 | 4 | SHORT | cws4 | t2 | -1 |
| 2026-08-30 03:54:00 | 4 | SHORT | cws4 | t1 | -1 |
| 2026-08-30 03:54:55 | 4 | SHORT | cws4 | t2 | -1 |
| 2026-08-30 04:13:00 | 4 | SHORT | cws4 | t1 | -1 |
| 2026-08-30 07:44:00 | 6 | SHORT | cws5 | t1 | -1 |
| 2026-08-30 12:16:00 | 9 | LONG | cws2 | t1 | +1 |
| 2026-08-30 12:35:55 | 9 | LONG | cws4 | t2 | +1 |
| 2026-08-30 15:05:55 | 10 | SHORT | cws5 | t2 | -1 |
| 2026-08-30 15:45:55 | 10 | SHORT | cws7 | t2 | -1 |
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
| 2026-08-30 01:35:55 | BATON | cws5 | ws5 -> ws6, between cadences, lin_hop 2 |
| 2026-08-30 01:36:55 | NO PASS | cws6 | cws6 25.78 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 01:46:55 | NO ACTION | cws6 | t2 cws1r ib cross 01:46:00 confirmed 01:46:55 at wob 12, cws1b 60.31 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:00:55 | LATCH1 | cws6 | latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 |
| 2026-08-30 02:00:55 | NO ACTION | cws6 | t2 cws1r ib cross 02:00:00 confirmed 02:00:55 at wob 12, cws1b 39.39 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:04:05 | NO ACTION | cws6 | latch latch 2: rider cws6 reversed raw 2026-08-30 01:19:40 stamp 2026-08-30 01:20:35, no candidate inside lin_hop, support ws3 raw 2026-08-30 02:03:10 stamp 2026-08-30 02:04:05, ws4 raw 2026-08-30 02:02:50 stamp 2026-08-30 02:03:45, ws5 raw 2026-08-30 02:02:45 stamp 2026-08-30 02:03:40 \| latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:30:00 | LATCH1 | cws6 | latch 1 at the t1 cadence 2026-08-30 02:30:00, divergence state -1 |
| 2026-08-30 02:30:00 | NO ACTION | cws6 | t1 cws1b ib 02:28:00, cws1r reversed 02:30:00 inside the 120s grace, stamp 02:30:00 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:30:55 | LATCH1 | cws6 | latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1 |
| 2026-08-30 02:30:55 | NO ACTION | cws6 | t2 cws1r ib cross 02:30:00 confirmed 02:30:55 at wob 12, cws1b 33.31 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:35:20 | LATCH1 | cws6 | latch 1 at the barrage cadence 2026-08-30 02:35:20, divergence state -1 |
| 2026-08-30 02:35:20 | EXHAUST | cws6 | barrage ws1Mage 19.79 LOW oob->ib 02:34:20, ws1r reverses 02:34:45 (25 s), 7 lines reverse with it (ws1,ws2,ws3,ws4,ws8,ws11,ws12), top ws12 - confirmed 02:35:20 \| mage-cascade down \| the walk ends |

### trade 3 - 2026-08-30 02:35:25 LONG, every bar that made it

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
| 2026-08-30 03:21:55 | BATON | cws3 | ws3 -> ws4, between cadences, lin_hop 2 |
| 2026-08-30 03:28:55 | NO PASS | cws4 | cws4 28.50 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 03:43:55 | LATCH1 | cws4 | latch 1 at the t2 cadence 2026-08-30 03:43:55, divergence state -1 |
| 2026-08-30 03:43:55 | NO ACTION | cws4 | t2 cws1r ib cross 03:43:00 confirmed 03:43:55 at wob 12, cws1b 43.12 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 03:54:00 | LATCH1 | cws4 | latch 1 at the t1 cadence 2026-08-30 03:54:00, divergence state -1 |
| 2026-08-30 03:54:00 | NO ACTION | cws4 | t1 cws1b oob 03:50:00..03:53:55, cws1r reversed 03:53:00 during, stamp 03:53:00 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 03:54:55 | LATCH1 | cws4 | latch 1 at the t2 cadence 2026-08-30 03:54:55, divergence state -1 |
| 2026-08-30 03:54:55 | NO ACTION | cws4 | t2 cws1r ib cross 03:54:00 confirmed 03:54:55 at wob 12, cws1b 17.82 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 04:13:00 | LATCH1 | cws4 | latch 1 at the t1 cadence 2026-08-30 04:13:00, divergence state -1 |
| 2026-08-30 04:13:00 | NO ACTION | cws4 | t1 cws1b oob 04:06:00..04:12:55, cws1r reversed 04:08:00 during, stamp 04:08:00 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 04:16:55 | NO PASS | cws4 | cws4 26.85 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 05:02:00 | CADENCE | cws4 | cws1b counter-oob cws1b 99.93 entered the HIGH oob 05:02:00 \| rider cws4 66.06, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 05:02:00 | EXHAUST | cws4 | t4 at a cws1b counter-oob cadence - rider cws4 66.06, no candidate inside lin_hop 2 |

### trade 5 - 2026-08-30 05:02:05 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 05:04:00 | ARM | - | cws1b+cws1r: cws1b 115.76 + cws1r 85.53 oob |
| 2026-08-30 05:04:00 | RIDER | cws1 | cws1 r 85.53, the highest ex-fence |
| 2026-08-30 05:04:00 | RETEST | - | cws1r 85.53 oob + cws2r 75.45 / cws3r 52.02 in - the gate opens; cws1r oob->ib cross 2026-08-30 05:07:00, wob 12, cadence at 2026-08-30 05:07:55 |
| 2026-08-30 05:07:55 | RIDER | cws2 | v4-arm-lineage-retest: the re-scan rides cws2 83.86, the highest ex-fence |
| 2026-08-30 05:11:00 | EXHAUST | cws2 | t1 cws1b oob 05:02:00..05:10:55, cws1r reversed 05:07:00 during, stamp 05:07:00 \| mage-cascade down OPPOSES the LONG - rev-trade |

### trade 6 - 2026-08-30 05:11:05 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 07:26:00 | ARM | - | cws1b+cws1r: cws1b -3.43 + cws1r 12.64 oob |
| 2026-08-30 07:26:00 | RIDER | cws3 | cws3 r 12.22, the highest ex-fence |
| 2026-08-30 07:26:00 | RETEST | - | cws2r 18.89 / cws3r 12.22 - not both inside the fence at the arm |
| 2026-08-30 07:30:55 | BATON | cws3 | ws3 -> ws5, between cadences, lin_hop 2 |
| 2026-08-30 07:44:00 | LATCH1 | cws5 | latch 1 at the t1 cadence 2026-08-30 07:44:00, divergence state -1 |
| 2026-08-30 07:44:00 | EXHAUST | cws5 | t1 cws1b oob 07:26:00..07:43:55, cws1r reversed 07:40:00 during, stamp 07:40:00 \| mage-cascade up OPPOSES the SHORT - rev-trade |

### trade 7 - 2026-08-30 07:44:05 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 10:11:00 | ARM | - | cws1b+cws1r: cws1b 114.29 + cws1r 86.09 oob |
| 2026-08-30 10:11:00 | RIDER | cws1 | cws1 r 86.09, the highest ex-fence |
| 2026-08-30 10:11:00 | RETEST | - | cws1r 86.09 oob + cws2r 63.89 / cws3r 64.12 in - the gate opens; cws1r oob->ib cross 2026-08-30 10:13:00, wob 12, cadence at 2026-08-30 10:13:55 |
| 2026-08-30 10:13:55 | RIDER | cws4 | v4-arm-lineage-retest: the re-scan rides cws4 81.84, the highest ex-fence |
| 2026-08-30 10:13:55 | EXHAUST | cws4 | t2 cws1r ib cross 10:13:00 confirmed 10:13:55 at wob 12, cws1b 77.01 not oob \| mage-cascade down OPPOSES the LONG - rev-trade |

### trade 8 - 2026-08-30 10:14:00 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 11:48:00 | ARM | - | cws4r: cws4r 12.52 oob |
| 2026-08-30 11:48:00 | RIDER | cws4 | cws4 r 12.52, the highest ex-fence |
| 2026-08-30 11:48:00 | RETEST | - | cws1r 49.22 is not oob at the arm - the gate stays shut |
| 2026-08-30 11:56:55 | BATON | cws4 | ws4 -> ws5, between cadences, lin_hop 2 |
| 2026-08-30 12:00:55 | NO PASS | cws5 | cws5 21.20 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 12:04:00 | CADENCE | cws5 | cws1b counter-oob cws1b 96.64 entered the HIGH oob 12:04:00 \| rider cws5 21.20, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-30 12:04:00 | EXHAUST | cws5 | exhaust at a cws1b counter-oob cadence - rider cws5 21.20, no candidate inside lin_hop 2 |

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
| 2026-08-30 15:05:55 | BATON | cws5 | ws5 -> ws7, at a t2 cadence, whole board |
| 2026-08-30 15:10:55 | NO PASS | cws7 | cws7 23.84 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 15:45:55 | LATCH1 | cws7 | latch 1 at the t2 cadence 2026-08-30 15:45:55, divergence state -1 |
| 2026-08-30 15:45:55 | EXHAUST | cws7 | t2 cws1r ib cross 15:45:00 confirmed 15:45:55 at wob 12, cws1b 27.83 not oob \| mage-cascade up OPPOSES the SHORT - rev-trade |

### trade 11 - 2026-08-30 15:46:00 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 18:34:00 | ARM | - | cws1b+cws1r: cws1b 96.35 + cws1r 88.13 oob |
| 2026-08-30 18:34:00 | RIDER | cws5 | cws5 r 80.58, the highest ex-fence |
| 2026-08-30 18:34:00 | RETEST | - | cws2r 82.90 / cws3r 50.95 - not both inside the fence at the arm |
| 2026-08-30 18:38:00 | LATCH1 | cws5 | latch 1 at the t1 cadence 2026-08-30 18:38:00, divergence state +1 |
| 2026-08-30 18:38:00 | EXHAUST | cws5 | t1 cws1b oob 18:32:00..18:37:55, cws1r reversed 18:37:00 during, stamp 18:37:00 \| mage-cascade down OPPOSES the LONG - rev-trade |

### trade 12 - 2026-08-30 18:38:05 SHORT, every bar that made it

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
| 2026-08-30 20:32:55 | BATON | cws4 | ws4 -> ws5, between cadences, lin_hop 2 |
| 2026-08-30 20:35:55 | NO PASS | cws5 | cws5 79.31 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 20:54:55 | EXHAUST | cws5 | t2 cws1r ib cross 20:54:00 confirmed 20:54:55 at wob 12, cws1b 59.76 not oob \| mage-cascade down OPPOSES the LONG - rev-trade |

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
| 2026-08-30 02:00:55 | LOW | cws6 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 |
| 2026-08-30 02:30:00 | LOW | cws6 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 02:30:00, divergence state -1 |
| 2026-08-30 02:30:55 | LOW | cws6 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1 |
| 2026-08-30 02:35:20 | LOW | cws6 | LATCH1 | latch 1 at the barrage cadence 2026-08-30 02:35:20, divergence state -1 |
| 2026-08-30 03:19:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 03:19:00, divergence state -1 |
| 2026-08-30 03:43:55 | LOW | cws4 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 03:43:55, divergence state -1 |
| 2026-08-30 03:54:00 | LOW | cws4 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 03:54:00, divergence state -1 |
| 2026-08-30 03:54:55 | LOW | cws4 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 03:54:55, divergence state -1 |
| 2026-08-30 04:13:00 | LOW | cws4 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 04:13:00, divergence state -1 |
| 2026-08-30 07:44:00 | LOW | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 07:44:00, divergence state -1 |
| 2026-08-30 12:16:00 | HIGH | cws2 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 12:16:00, divergence state +1 |
| 2026-08-30 12:35:55 | HIGH | cws4 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 12:35:55, divergence state +1 |
| 2026-08-30 15:05:55 | LOW | cws5 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 15:05:55, divergence state -1 |
| 2026-08-30 15:45:55 | LOW | cws7 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 15:45:55, divergence state -1 |
| 2026-08-30 18:38:00 | HIGH | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 18:38:00, divergence state +1 |

| the LATCH cadence | side | rider | stage | why |
|---|---|---|---|---|
| 2026-08-30 01:04:55 | LOW | cws2 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 01:04:55, divergence state -1 |
| 2026-08-30 01:21:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 01:21:00, divergence state -1 |
| 2026-08-30 02:00:55 | LOW | cws6 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 |
| 2026-08-30 02:04:05 | LOW | cws6 | NO ACTION | latch latch 2: rider cws6 reversed raw 2026-08-30 01:19:40 stamp 2026-08-30 01:20:35, no candidate inside lin_hop, support ws3 raw 2026-08-30 02:03:10 stamp 2026-08-30 02:04:05, ws4 raw 2026-08-30 02:02:50 stamp 2026-08-30 02:03:45, ws5 raw 2026-08-30 02:02:45 stamp 2026-08-30 02:03:40 \| latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:30:00 | LOW | cws6 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 02:30:00, divergence state -1 |
| 2026-08-30 02:30:55 | LOW | cws6 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1 |
| 2026-08-30 02:35:20 | LOW | cws6 | LATCH1 | latch 1 at the barrage cadence 2026-08-30 02:35:20, divergence state -1 |
| 2026-08-30 03:19:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 03:19:00, divergence state -1 |
| 2026-08-30 03:43:55 | LOW | cws4 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 03:43:55, divergence state -1 |
| 2026-08-30 03:54:00 | LOW | cws4 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 03:54:00, divergence state -1 |
| 2026-08-30 03:54:55 | LOW | cws4 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 03:54:55, divergence state -1 |
| 2026-08-30 04:13:00 | LOW | cws4 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 04:13:00, divergence state -1 |
| 2026-08-30 07:44:00 | LOW | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 07:44:00, divergence state -1 |
| 2026-08-30 12:16:00 | HIGH | cws2 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 12:16:00, divergence state +1 |
| 2026-08-30 12:35:55 | HIGH | cws4 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 12:35:55, divergence state +1 |
| 2026-08-30 15:05:55 | LOW | cws5 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 15:05:55, divergence state -1 |
| 2026-08-30 15:45:55 | LOW | cws7 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 15:45:55, divergence state -1 |
| 2026-08-30 18:38:00 | HIGH | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 18:38:00, divergence state +1 |

| the cws1b counter-oob cadence | side | rider | stage | why |
|---|---|---|---|---|
| 2026-08-30 05:02:00 | LOW | cws4 | CADENCE | cws1b counter-oob cws1b 99.93 entered the HIGH oob 05:02:00 \| rider cws4 66.06, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 05:02:00 | LOW | cws4 | EXHAUST | t4 at a cws1b counter-oob cadence - rider cws4 66.06, no candidate inside lin_hop 2 |
| 2026-08-30 12:04:00 | LOW | cws5 | CADENCE | cws1b counter-oob cws1b 96.64 entered the HIGH oob 12:04:00 \| rider cws5 21.20, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-30 12:04:00 | LOW | cws5 | EXHAUST | exhaust at a cws1b counter-oob cadence - rider cws5 21.20, no candidate inside lin_hop 2 |

NO t3 EVENT in the window.

## first side LOW  (376.9s)

| the read | value |
|---|---|
| walks | 16 |
| verdicts EXHAUST | 14 |
| verdicts NO ARM | 1 |
| verdicts NO VERDICT | 0 |
| verdicts DIV REV-TRADE | 1 |
| t1 cadence events | 0 |
| t2 cadence events | 2 |
| t3 cadence events | 0 |
| walks that reached a RETEST row | 14 |
|   the gate shut, cws1r not oob at the arm | 4 |
|   the gate shut, cws2r/cws3r not both in the fence | 2 |
|   the gate opened | 8 |
|   the gate opened, no oob->ib cross to the data end | 0 |
| the gate cadence ENDED the walk | 4 |
| the gate cadence RE-SCANNED a rider | 4 |
| BATON passes | 10 |
| LATCH1 armed | 17 |
| cadences taking NO ACTION on the mage-cascade | 13 |
| latch cadence events | 0 |
| cws1b counter-oob cadence events | 4 |

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

| # | the open | dir | the arm | the cadence that ended it | the exhaust = the rev-trade bar | the verdict | MAE % | MFE % | capped | SP TF | the pivot | leg MFE % | ended by |
#   THE EXHAUST BAR *IS* THE REV-TRADE BAR. An exhaust is only ever declared at a
#   cadence event bar, so every bar in that column is a cadence bar. The trade closes
#   there and the opposite side opens at that bar + 1, which is the NEXT row's open.
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-08-30 00:00:05 | SHORT | 2026-08-30 01:02:00 | barrage | 2026-08-30 02:35:20 | EXHAUST | -0.580 | +1.884 | - | ws2Mage | 2026-08-30 02:53:00 | 1.794 | the barrage |
| 2 | 2026-08-30 02:35:25 | LONG | 2026-08-30 02:43:00 | retest | 2026-08-30 02:46:55 | EXHAUST | -0.165 | +0.506 | - | ws2Mage | 2026-08-30 02:38:25 | 0.480 | the board review |
| 3 | 2026-08-30 02:47:00 | SHORT | 2026-08-30 03:01:00 | cws1b counter-oob | 2026-08-30 05:02:00 | EXHAUST | -0.314 | +2.206 | - | ws1Mage | 2026-08-30 05:29:45 | 0.578 | the board review |
| 4 | 2026-08-30 05:02:05 | LONG | 2026-08-30 05:04:00 | t1 | 2026-08-30 05:11:00 | EXHAUST | -0.031 | +0.507 | - | ws1Mage | 2026-08-30 04:56:30 | 0.971 | the mage-cascade mismatch |
| 5 | 2026-08-30 05:11:05 | SHORT | 2026-08-30 07:26:00 | t1 | 2026-08-30 07:44:00 | EXHAUST | -1.100 | +0.000 | YES | ws5Mage | 2026-08-30 07:12:20 | 1.228 | the mage-cascade mismatch |
| 6 | 2026-08-30 07:44:05 | LONG | 2026-08-30 10:11:00 | t2 | 2026-08-30 10:13:55 | EXHAUST | -1.100 | +0.000 | YES | ws15Mage | 2026-08-30 11:52:25 | 1.840 | the mage-cascade mismatch |
| 7 | 2026-08-30 10:14:00 | SHORT | 2026-08-30 11:48:00 | cws1b counter-oob | 2026-08-30 12:04:00 | EXHAUST | -0.817 | +0.058 | - | ws2Mage | 2026-08-30 12:33:15 | 1.113 | the board review |
| 8 | 2026-08-30 12:04:05 | LONG | 2026-08-30 12:04:05 | t2 | 2026-08-30 12:35:55 | EXHAUST | -0.031 | +1.321 | - | ws1Mage | 2026-08-30 13:36:00 | 0.707 | the board review |
| 9 | 2026-08-30 12:36:00 | SHORT | 2026-08-30 14:40:00 | t2 | 2026-08-30 15:45:55 | EXHAUST | -1.100 | +0.000 | YES | ws20Mage | 2026-08-30 16:25:10 | 3.965 | the mage-cascade mismatch |
| 10 | 2026-08-30 15:46:00 | LONG | 2026-08-30 18:34:00 | t1 | 2026-08-30 18:38:00 | EXHAUST | -1.100 | +0.000 | YES | ws2Mage | 2026-08-30 17:57:25 | 1.143 | the mage-cascade mismatch |
| 11 | 2026-08-30 18:38:05 | SHORT | 2026-08-30 19:26:00 | retest | 2026-08-30 19:31:55 | EXHAUST | -0.265 | +1.247 | - | ws2Mage | 2026-08-30 19:01:15 | 5.400 | the board review |
| 12 | 2026-08-30 19:32:00 | LONG | 2026-08-30 20:12:00 | t2 | 2026-08-30 20:54:55 | EXHAUST | -1.100 | +0.000 | YES | ws3Mage | 2026-08-30 21:48:05 | 1.885 | the mage-cascade mismatch |
| 13 | 2026-08-30 20:55:00 | SHORT | 2026-08-30 21:02:00 | retest | 2026-08-30 21:04:55 | EXHAUST | -0.132 | +1.955 | - | ws1Mage | 2026-08-30 21:38:05 | 1.032 | the board review |
| 14 | 2026-08-30 21:05:00 | LONG | 2026-08-30 22:00:00 | retest | 2026-08-30 22:03:55 | EXHAUST | -0.549 | +1.525 | - | ws3Mage | 2026-08-30 21:56:40 | 1.331 | the board review |
| 15 | 2026-08-30 22:04:00 | SHORT | 2026-08-30 22:24:00 | - | 2026-08-30 22:24:00 | DIV REV-TRADE | -0.006 | +1.684 | - | ws5Mage | 2026-08-31 08:42:25 | 2.107 | the board review |

| the read | value |
|---|---|
| trades capped at MAE 1.10% | 5 of 15 |
| ended by a mage-cascade mismatch | 6 |
| ended by the barrage | 1 |
| ended by the cadence board review | 8 |
| the mismatch action | rev-trade |

| the read | value |
|---|---|
| rev-trades | 15 |
| sum MAE % | -8.392 |
| sum MFE % | +12.893 |
| median MAE % | -0.549 |
| median MFE % | +0.507 |
| worst MAE % | -1.100 |
| best MFE % | +2.206 |
| MFE > abs(MAE) | 9 of 15 |
| sweep-pivot knobs | SP_PICK lowest_pct, SP_BAND 0.0, SP_CONTAIN 0, SP_XWOB 18, SP_ALIGN_S 300, SP_TFS wide |

| the latch 1 bar | trade | dir | rider | the cadence it armed on | the state |
|---|---|---|---|---|---|
| 2026-08-30 01:04:55 | 1 | SHORT | cws2 | t2 | -1 |
| 2026-08-30 01:21:00 | 1 | SHORT | cws3 | t1 | -1 |
| 2026-08-30 02:00:55 | 1 | SHORT | cws6 | t2 | -1 |
| 2026-08-30 02:30:00 | 1 | SHORT | cws6 | t1 | -1 |
| 2026-08-30 02:30:55 | 1 | SHORT | cws6 | t2 | -1 |
| 2026-08-30 02:35:20 | 1 | SHORT | cws6 | barrage | -1 |
| 2026-08-30 03:19:00 | 3 | SHORT | cws3 | t1 | -1 |
| 2026-08-30 03:43:55 | 3 | SHORT | cws4 | t2 | -1 |
| 2026-08-30 03:54:00 | 3 | SHORT | cws4 | t1 | -1 |
| 2026-08-30 03:54:55 | 3 | SHORT | cws4 | t2 | -1 |
| 2026-08-30 04:13:00 | 3 | SHORT | cws4 | t1 | -1 |
| 2026-08-30 07:44:00 | 5 | SHORT | cws5 | t1 | -1 |
| 2026-08-30 12:16:00 | 8 | LONG | cws2 | t1 | +1 |
| 2026-08-30 12:35:55 | 8 | LONG | cws4 | t2 | +1 |
| 2026-08-30 15:05:55 | 9 | SHORT | cws5 | t2 | -1 |
| 2026-08-30 15:45:55 | 9 | SHORT | cws7 | t2 | -1 |
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
| 2026-08-30 01:35:55 | BATON | cws5 | ws5 -> ws6, between cadences, lin_hop 2 |
| 2026-08-30 01:36:55 | NO PASS | cws6 | cws6 25.78 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 01:46:55 | NO ACTION | cws6 | t2 cws1r ib cross 01:46:00 confirmed 01:46:55 at wob 12, cws1b 60.31 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:00:55 | LATCH1 | cws6 | latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 |
| 2026-08-30 02:00:55 | NO ACTION | cws6 | t2 cws1r ib cross 02:00:00 confirmed 02:00:55 at wob 12, cws1b 39.39 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:04:05 | NO ACTION | cws6 | latch latch 2: rider cws6 reversed raw 2026-08-30 01:19:40 stamp 2026-08-30 01:20:35, no candidate inside lin_hop, support ws3 raw 2026-08-30 02:03:10 stamp 2026-08-30 02:04:05, ws4 raw 2026-08-30 02:02:50 stamp 2026-08-30 02:03:45, ws5 raw 2026-08-30 02:02:45 stamp 2026-08-30 02:03:40 \| latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:30:00 | LATCH1 | cws6 | latch 1 at the t1 cadence 2026-08-30 02:30:00, divergence state -1 |
| 2026-08-30 02:30:00 | NO ACTION | cws6 | t1 cws1b ib 02:28:00, cws1r reversed 02:30:00 inside the 120s grace, stamp 02:30:00 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:30:55 | LATCH1 | cws6 | latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1 |
| 2026-08-30 02:30:55 | NO ACTION | cws6 | t2 cws1r ib cross 02:30:00 confirmed 02:30:55 at wob 12, cws1b 33.31 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:35:20 | LATCH1 | cws6 | latch 1 at the barrage cadence 2026-08-30 02:35:20, divergence state -1 |
| 2026-08-30 02:35:20 | EXHAUST | cws6 | barrage ws1Mage 19.79 LOW oob->ib 02:34:20, ws1r reverses 02:34:45 (25 s), 7 lines reverse with it (ws1,ws2,ws3,ws4,ws8,ws11,ws12), top ws12 - confirmed 02:35:20 \| mage-cascade down \| the walk ends |

### trade 2 - 2026-08-30 02:35:25 LONG, every bar that made it

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
| 2026-08-30 03:21:55 | BATON | cws3 | ws3 -> ws4, between cadences, lin_hop 2 |
| 2026-08-30 03:28:55 | NO PASS | cws4 | cws4 28.50 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 03:43:55 | LATCH1 | cws4 | latch 1 at the t2 cadence 2026-08-30 03:43:55, divergence state -1 |
| 2026-08-30 03:43:55 | NO ACTION | cws4 | t2 cws1r ib cross 03:43:00 confirmed 03:43:55 at wob 12, cws1b 43.12 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 03:54:00 | LATCH1 | cws4 | latch 1 at the t1 cadence 2026-08-30 03:54:00, divergence state -1 |
| 2026-08-30 03:54:00 | NO ACTION | cws4 | t1 cws1b oob 03:50:00..03:53:55, cws1r reversed 03:53:00 during, stamp 03:53:00 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 03:54:55 | LATCH1 | cws4 | latch 1 at the t2 cadence 2026-08-30 03:54:55, divergence state -1 |
| 2026-08-30 03:54:55 | NO ACTION | cws4 | t2 cws1r ib cross 03:54:00 confirmed 03:54:55 at wob 12, cws1b 17.82 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 04:13:00 | LATCH1 | cws4 | latch 1 at the t1 cadence 2026-08-30 04:13:00, divergence state -1 |
| 2026-08-30 04:13:00 | NO ACTION | cws4 | t1 cws1b oob 04:06:00..04:12:55, cws1r reversed 04:08:00 during, stamp 04:08:00 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 04:16:55 | NO PASS | cws4 | cws4 26.85 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 05:02:00 | CADENCE | cws4 | cws1b counter-oob cws1b 99.93 entered the HIGH oob 05:02:00 \| rider cws4 66.06, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 05:02:00 | EXHAUST | cws4 | t4 at a cws1b counter-oob cadence - rider cws4 66.06, no candidate inside lin_hop 2 |

### trade 4 - 2026-08-30 05:02:05 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 05:04:00 | ARM | - | cws1b+cws1r: cws1b 115.76 + cws1r 85.53 oob |
| 2026-08-30 05:04:00 | RIDER | cws1 | cws1 r 85.53, the highest ex-fence |
| 2026-08-30 05:04:00 | RETEST | - | cws1r 85.53 oob + cws2r 75.45 / cws3r 52.02 in - the gate opens; cws1r oob->ib cross 2026-08-30 05:07:00, wob 12, cadence at 2026-08-30 05:07:55 |
| 2026-08-30 05:07:55 | RIDER | cws2 | v4-arm-lineage-retest: the re-scan rides cws2 83.86, the highest ex-fence |
| 2026-08-30 05:11:00 | EXHAUST | cws2 | t1 cws1b oob 05:02:00..05:10:55, cws1r reversed 05:07:00 during, stamp 05:07:00 \| mage-cascade down OPPOSES the LONG - rev-trade |

### trade 5 - 2026-08-30 05:11:05 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 07:26:00 | ARM | - | cws1b+cws1r: cws1b -3.43 + cws1r 12.64 oob |
| 2026-08-30 07:26:00 | RIDER | cws3 | cws3 r 12.22, the highest ex-fence |
| 2026-08-30 07:26:00 | RETEST | - | cws2r 18.89 / cws3r 12.22 - not both inside the fence at the arm |
| 2026-08-30 07:30:55 | BATON | cws3 | ws3 -> ws5, between cadences, lin_hop 2 |
| 2026-08-30 07:44:00 | LATCH1 | cws5 | latch 1 at the t1 cadence 2026-08-30 07:44:00, divergence state -1 |
| 2026-08-30 07:44:00 | EXHAUST | cws5 | t1 cws1b oob 07:26:00..07:43:55, cws1r reversed 07:40:00 during, stamp 07:40:00 \| mage-cascade up OPPOSES the SHORT - rev-trade |

### trade 6 - 2026-08-30 07:44:05 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 10:11:00 | ARM | - | cws1b+cws1r: cws1b 114.29 + cws1r 86.09 oob |
| 2026-08-30 10:11:00 | RIDER | cws1 | cws1 r 86.09, the highest ex-fence |
| 2026-08-30 10:11:00 | RETEST | - | cws1r 86.09 oob + cws2r 63.89 / cws3r 64.12 in - the gate opens; cws1r oob->ib cross 2026-08-30 10:13:00, wob 12, cadence at 2026-08-30 10:13:55 |
| 2026-08-30 10:13:55 | RIDER | cws4 | v4-arm-lineage-retest: the re-scan rides cws4 81.84, the highest ex-fence |
| 2026-08-30 10:13:55 | EXHAUST | cws4 | t2 cws1r ib cross 10:13:00 confirmed 10:13:55 at wob 12, cws1b 77.01 not oob \| mage-cascade down OPPOSES the LONG - rev-trade |

### trade 7 - 2026-08-30 10:14:00 SHORT, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 11:48:00 | ARM | - | cws4r: cws4r 12.52 oob |
| 2026-08-30 11:48:00 | RIDER | cws4 | cws4 r 12.52, the highest ex-fence |
| 2026-08-30 11:48:00 | RETEST | - | cws1r 49.22 is not oob at the arm - the gate stays shut |
| 2026-08-30 11:56:55 | BATON | cws4 | ws4 -> ws5, between cadences, lin_hop 2 |
| 2026-08-30 12:00:55 | NO PASS | cws5 | cws5 21.20 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 12:04:00 | CADENCE | cws5 | cws1b counter-oob cws1b 96.64 entered the HIGH oob 12:04:00 \| rider cws5 21.20, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-30 12:04:00 | EXHAUST | cws5 | exhaust at a cws1b counter-oob cadence - rider cws5 21.20, no candidate inside lin_hop 2 |

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
| 2026-08-30 15:05:55 | BATON | cws5 | ws5 -> ws7, at a t2 cadence, whole board |
| 2026-08-30 15:10:55 | NO PASS | cws7 | cws7 23.84 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 15:45:55 | LATCH1 | cws7 | latch 1 at the t2 cadence 2026-08-30 15:45:55, divergence state -1 |
| 2026-08-30 15:45:55 | EXHAUST | cws7 | t2 cws1r ib cross 15:45:00 confirmed 15:45:55 at wob 12, cws1b 27.83 not oob \| mage-cascade up OPPOSES the SHORT - rev-trade |

### trade 10 - 2026-08-30 15:46:00 LONG, every bar that made it

| the bar | stage | rider | why |
|---|---|---|---|
| 2026-08-30 18:34:00 | ARM | - | cws1b+cws1r: cws1b 96.35 + cws1r 88.13 oob |
| 2026-08-30 18:34:00 | RIDER | cws5 | cws5 r 80.58, the highest ex-fence |
| 2026-08-30 18:34:00 | RETEST | - | cws2r 82.90 / cws3r 50.95 - not both inside the fence at the arm |
| 2026-08-30 18:38:00 | LATCH1 | cws5 | latch 1 at the t1 cadence 2026-08-30 18:38:00, divergence state +1 |
| 2026-08-30 18:38:00 | EXHAUST | cws5 | t1 cws1b oob 18:32:00..18:37:55, cws1r reversed 18:37:00 during, stamp 18:37:00 \| mage-cascade down OPPOSES the LONG - rev-trade |

### trade 11 - 2026-08-30 18:38:05 SHORT, every bar that made it

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
| 2026-08-30 20:32:55 | BATON | cws4 | ws4 -> ws5, between cadences, lin_hop 2 |
| 2026-08-30 20:35:55 | NO PASS | cws5 | cws5 79.31 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 20:54:55 | EXHAUST | cws5 | t2 cws1r ib cross 20:54:00 confirmed 20:54:55 at wob 12, cws1b 59.76 not oob \| mage-cascade down OPPOSES the LONG - rev-trade |

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
| 2026-08-30 02:00:55 | LOW | cws6 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 |
| 2026-08-30 02:30:00 | LOW | cws6 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 02:30:00, divergence state -1 |
| 2026-08-30 02:30:55 | LOW | cws6 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1 |
| 2026-08-30 02:35:20 | LOW | cws6 | LATCH1 | latch 1 at the barrage cadence 2026-08-30 02:35:20, divergence state -1 |
| 2026-08-30 03:19:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 03:19:00, divergence state -1 |
| 2026-08-30 03:43:55 | LOW | cws4 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 03:43:55, divergence state -1 |
| 2026-08-30 03:54:00 | LOW | cws4 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 03:54:00, divergence state -1 |
| 2026-08-30 03:54:55 | LOW | cws4 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 03:54:55, divergence state -1 |
| 2026-08-30 04:13:00 | LOW | cws4 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 04:13:00, divergence state -1 |
| 2026-08-30 07:44:00 | LOW | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 07:44:00, divergence state -1 |
| 2026-08-30 12:16:00 | HIGH | cws2 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 12:16:00, divergence state +1 |
| 2026-08-30 12:35:55 | HIGH | cws4 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 12:35:55, divergence state +1 |
| 2026-08-30 15:05:55 | LOW | cws5 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 15:05:55, divergence state -1 |
| 2026-08-30 15:45:55 | LOW | cws7 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 15:45:55, divergence state -1 |
| 2026-08-30 18:38:00 | HIGH | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 18:38:00, divergence state +1 |

| the LATCH cadence | side | rider | stage | why |
|---|---|---|---|---|
| 2026-08-30 01:04:55 | LOW | cws2 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 01:04:55, divergence state -1 |
| 2026-08-30 01:21:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 01:21:00, divergence state -1 |
| 2026-08-30 02:00:55 | LOW | cws6 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 |
| 2026-08-30 02:04:05 | LOW | cws6 | NO ACTION | latch latch 2: rider cws6 reversed raw 2026-08-30 01:19:40 stamp 2026-08-30 01:20:35, no candidate inside lin_hop, support ws3 raw 2026-08-30 02:03:10 stamp 2026-08-30 02:04:05, ws4 raw 2026-08-30 02:02:50 stamp 2026-08-30 02:03:45, ws5 raw 2026-08-30 02:02:45 stamp 2026-08-30 02:03:40 \| latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:30:00 | LOW | cws6 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 02:30:00, divergence state -1 |
| 2026-08-30 02:30:55 | LOW | cws6 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1 |
| 2026-08-30 02:35:20 | LOW | cws6 | LATCH1 | latch 1 at the barrage cadence 2026-08-30 02:35:20, divergence state -1 |
| 2026-08-30 03:19:00 | LOW | cws3 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 03:19:00, divergence state -1 |
| 2026-08-30 03:43:55 | LOW | cws4 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 03:43:55, divergence state -1 |
| 2026-08-30 03:54:00 | LOW | cws4 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 03:54:00, divergence state -1 |
| 2026-08-30 03:54:55 | LOW | cws4 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 03:54:55, divergence state -1 |
| 2026-08-30 04:13:00 | LOW | cws4 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 04:13:00, divergence state -1 |
| 2026-08-30 07:44:00 | LOW | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 07:44:00, divergence state -1 |
| 2026-08-30 12:16:00 | HIGH | cws2 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 12:16:00, divergence state +1 |
| 2026-08-30 12:35:55 | HIGH | cws4 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 12:35:55, divergence state +1 |
| 2026-08-30 15:05:55 | LOW | cws5 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 15:05:55, divergence state -1 |
| 2026-08-30 15:45:55 | LOW | cws7 | LATCH1 | latch 1 at the t2 cadence 2026-08-30 15:45:55, divergence state -1 |
| 2026-08-30 18:38:00 | HIGH | cws5 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 18:38:00, divergence state +1 |

| the cws1b counter-oob cadence | side | rider | stage | why |
|---|---|---|---|---|
| 2026-08-30 05:02:00 | LOW | cws4 | CADENCE | cws1b counter-oob cws1b 99.93 entered the HIGH oob 05:02:00 \| rider cws4 66.06, no-longer-exfence yes, reversed yes \| mage-cascade down |
| 2026-08-30 05:02:00 | LOW | cws4 | EXHAUST | t4 at a cws1b counter-oob cadence - rider cws4 66.06, no candidate inside lin_hop 2 |
| 2026-08-30 12:04:00 | LOW | cws5 | CADENCE | cws1b counter-oob cws1b 96.64 entered the HIGH oob 12:04:00 \| rider cws5 21.20, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-30 12:04:00 | LOW | cws5 | EXHAUST | exhaust at a cws1b counter-oob cadence - rider cws5 21.20, no candidate inside lin_hop 2 |

NO t3 EVENT in the window.
