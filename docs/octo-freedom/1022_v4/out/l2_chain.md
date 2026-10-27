# lineage2 chained, 2026-08-30 00:00:00 .. 2026-09-03 23:59:55
# t3 needs max(2, round(0.75 x the ex-fence population)) reversals, matryoshka ws7..rider-1
# gate closed | lin_hop 2 lifted only at t1/t2 | RULED_OK True

## first side HIGH  (638.9s)

| the read | value |
|---|---|
| walks | 81 |
| verdicts EXHAUST | 71 |
| verdicts NO ARM | 0 |
| verdicts NO VERDICT | 1 |
| verdicts DIV REV-TRADE | 9 |
| t1 cadence events | 81 |
| t2 cadence events | 53 |
| t3 cadence events | 0 |
| walks that reached a RETEST row | 72 |
|   the gate shut, cws1r not oob at the arm | 34 |
|   the gate shut, cws2r/cws3r not both in the fence | 9 |
|   the gate opened | 29 |
|   the gate opened, no oob->ib cross to the data end | 0 |
| the gate cadence ENDED the walk | 10 |
| the gate cadence RE-SCANNED a rider | 19 |
| BATON passes | 110 |
| LATCH1 armed | 83 |
| latch cadence events | 19 |
| cws1b counter-oob cadence events | 86 |

| the DIV branch read | arms |
|---|---|
| a divergence, SHORT | 3 |
| a divergence, LONG | 6 |
| PM, trend SHORT | 3 |
| all DIV arms | 12 |
|   of those, a REV-TRADE verdict | 9 |

| the gate cadence | side | what it did | why |
|---|---|---|---|
| 2026-08-30 00:20:00 | HIGH | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-08-30 01:04:00 | LOW | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 18.31, the highest ex-fence |
| 2026-08-30 02:46:00 | HIGH | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-08-30 03:06:00 | LOW | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 12.28, the highest ex-fence |
| 2026-08-30 05:07:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 83.86, the highest ex-fence |
| 2026-08-30 10:13:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws4 81.84, the highest ex-fence |
| 2026-08-30 19:31:00 | LOW | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-08-30 21:04:00 | LOW | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-08-30 22:03:00 | HIGH | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-08-31 02:58:00 | LOW | RIDER | v4-arm-lineage-retest: the re-scan rides cws4 13.95, the highest ex-fence |
| 2026-08-31 04:57:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws4 85.45, the highest ex-fence |
| 2026-08-31 16:49:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws3 80.87, the highest ex-fence |
| 2026-08-31 21:34:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 89.36, the highest ex-fence |
| 2026-09-01 00:23:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws9 82.59, the highest ex-fence |
| 2026-09-01 03:39:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws8 82.96, the highest ex-fence |
| 2026-09-01 05:08:00 | HIGH | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-09-01 13:52:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws6 86.94, the highest ex-fence |
| 2026-09-01 17:26:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws5 81.31, the highest ex-fence |
| 2026-09-02 00:32:00 | LOW | RIDER | v4-arm-lineage-retest: the re-scan rides cws5 12.94, the highest ex-fence |
| 2026-09-02 06:46:00 | HIGH | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-09-02 10:22:00 | HIGH | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-09-02 12:03:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws4 86.22, the highest ex-fence |
| 2026-09-02 12:41:00 | LOW | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-09-02 22:11:00 | LOW | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 0.96, the highest ex-fence |
| 2026-09-02 23:12:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 85.91, the highest ex-fence |
| 2026-09-03 04:57:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws3 81.88, the highest ex-fence |
| 2026-09-03 07:53:00 | LOW | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-09-03 08:10:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 86.97, the highest ex-fence |
| 2026-09-03 10:59:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws4 81.30, the highest ex-fence |

NO t3 EVENT in the window.

## first side LOW  (607.4s)

| the read | value |
|---|---|
| walks | 80 |
| verdicts EXHAUST | 70 |
| verdicts NO ARM | 0 |
| verdicts NO VERDICT | 1 |
| verdicts DIV REV-TRADE | 9 |
| t1 cadence events | 81 |
| t2 cadence events | 53 |
| t3 cadence events | 0 |
| walks that reached a RETEST row | 71 |
|   the gate shut, cws1r not oob at the arm | 34 |
|   the gate shut, cws2r/cws3r not both in the fence | 9 |
|   the gate opened | 28 |
|   the gate opened, no oob->ib cross to the data end | 0 |
| the gate cadence ENDED the walk | 9 |
| the gate cadence RE-SCANNED a rider | 19 |
| BATON passes | 110 |
| LATCH1 armed | 83 |
| latch cadence events | 19 |
| cws1b counter-oob cadence events | 86 |

| the DIV branch read | arms |
|---|---|
| a divergence, SHORT | 3 |
| a divergence, LONG | 6 |
| PM, trend SHORT | 3 |
| all DIV arms | 12 |
|   of those, a REV-TRADE verdict | 9 |

| the gate cadence | side | what it did | why |
|---|---|---|---|
| 2026-08-30 01:04:00 | LOW | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 18.31, the highest ex-fence |
| 2026-08-30 02:46:00 | HIGH | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-08-30 03:06:00 | LOW | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 12.28, the highest ex-fence |
| 2026-08-30 05:07:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 83.86, the highest ex-fence |
| 2026-08-30 10:13:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws4 81.84, the highest ex-fence |
| 2026-08-30 19:31:00 | LOW | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-08-30 21:04:00 | LOW | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-08-30 22:03:00 | HIGH | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-08-31 02:58:00 | LOW | RIDER | v4-arm-lineage-retest: the re-scan rides cws4 13.95, the highest ex-fence |
| 2026-08-31 04:57:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws4 85.45, the highest ex-fence |
| 2026-08-31 16:49:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws3 80.87, the highest ex-fence |
| 2026-08-31 21:34:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 89.36, the highest ex-fence |
| 2026-09-01 00:23:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws9 82.59, the highest ex-fence |
| 2026-09-01 03:39:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws8 82.96, the highest ex-fence |
| 2026-09-01 05:08:00 | HIGH | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-09-01 13:52:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws6 86.94, the highest ex-fence |
| 2026-09-01 17:26:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws5 81.31, the highest ex-fence |
| 2026-09-02 00:32:00 | LOW | RIDER | v4-arm-lineage-retest: the re-scan rides cws5 12.94, the highest ex-fence |
| 2026-09-02 06:46:00 | HIGH | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-09-02 10:22:00 | HIGH | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-09-02 12:03:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws4 86.22, the highest ex-fence |
| 2026-09-02 12:41:00 | LOW | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-09-02 22:11:00 | LOW | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 0.96, the highest ex-fence |
| 2026-09-02 23:12:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 85.91, the highest ex-fence |
| 2026-09-03 04:57:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws3 81.88, the highest ex-fence |
| 2026-09-03 07:53:00 | LOW | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |
| 2026-09-03 08:10:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws2 86.97, the highest ex-fence |
| 2026-09-03 10:59:00 | HIGH | RIDER | v4-arm-lineage-retest: the re-scan rides cws4 81.30, the highest ex-fence |

NO t3 EVENT in the window.
