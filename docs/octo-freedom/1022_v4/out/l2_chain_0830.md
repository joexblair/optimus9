# lineage2 chained, 2026-08-30 00:00:00 .. 2026-08-30 23:59:55
# t3 needs max(2, round(0.75 x the ex-fence population)) reversals, matryoshka ws7..rider-1
# gate closed | lin_hop 2 lifted only at t1/t2 | RULED_OK True

## first side HIGH  (91.3s)

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
| LATCH1 armed | 16 |
| cadences taking NO ACTION on the mage-cascade | 14 |
| latch cadence events | 0 |
| cws1b counter-oob cadence events | 6 |

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
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-08-30 00:00:05 | LONG | 2026-08-30 00:18:00 | retest | 2026-08-30 00:20:55 | EXHAUST | -0.529 | +0.580 | - | ws1Mage | 2026-08-30 00:10:30 | 1.002 | the board review |
| 2 | 2026-08-30 00:21:00 | SHORT | 2026-08-30 01:02:00 | cws1b counter-oob | 2026-08-30 02:41:00 | EXHAUST | -0.117 | +1.829 | - | ws2Mage | 2026-08-30 02:53:00 | 1.794 | the board review |
| 3 | 2026-08-30 02:41:05 | LONG | 2026-08-30 02:43:00 | retest | 2026-08-30 02:46:55 | EXHAUST | -0.288 | +0.077 | - | ws2Mage | 2026-08-30 02:38:25 | 0.480 | the board review |
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
| ended by the cadence board review | 10 |
| the mismatch action | rev-trade |

| the read | value |
|---|---|
| rev-trades | 16 |
| sum MAE % | -8.581 |
| sum MFE % | +12.989 |
| median MAE % | -0.314 |
| median MFE % | +0.580 |
| worst MAE % | -1.100 |
| best MFE % | +2.206 |
