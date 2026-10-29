# THE FIRST 3 LEGS, 2026-08-30 - the 1008 block format
# TAPE 1632960 bars | LG_TAPE_END 2026-10-05 | RULED_OK True
# BOARD: ws1..ws3 keep their reads; ws4.. read PSEUDO for ex-fence and for the quoted value. LIN2_PSEUDO_MIN_TF 4.
# BARRAGE: LIN2_BARRAGE_MIN_TF 9, LINES 6, TOL 70s, MIN_TF_MODE 'membership' - the pine-emit settings.
# THE EXHAUST BAR IS THE REV-TRADE BAR: the leg closes there, the opposite side opens at
#   that bar + 1. So INCOMING LEG CLOSES and THIS LEG OPENS are 5 s apart, not the same bar.
# pct for THIS leg is measured from THIS leg open on THIS leg side. Incoming rows read
#   NEGATIVE where price was already beyond this open.
# ex-fence is the 20/80 fence from RMOM_FNC; oob is 15/85. ws1..ws3 are cws (closed), ws4+ are ws (pseudo).

## leg 1 of 3 - 2026-08-30 LONG   opens 2026-08-30 00:00:00   exits 2026-08-30 00:20:55 on EXHAUST   MAE 0.5193 at +8.4 min   MFE 0.5906 at +18.2 min   realised -0.0458   CONTINUITY: the first leg - opens at the window start

| ts | min from THIS open | event | pxs | pct for THIS leg |
|---|---|---|---|---|
| 2026-08-29 23:59:55 | -0.1 | no incoming leg - the chain has no trade open before leg 1 | 0.196380 | -0.0102 |
| 2026-08-30 00:00:00 | +0.0 | >>> THIS LEG OPENS LONG | 0.196400 | +0.0000 |
| 2026-08-30 00:08:25 | +8.4 | the ADVERSE extreme - MAE 0.5193 | 0.195380 | -0.5193 |
| 2026-08-30 00:18:00 | +18.0 | ARM - cws1b+cws1r: cws1b 109.73 + cws1r 97.62 oob | 0.197310 | +0.4633 |
| 2026-08-30 00:18:00 | +18.0 | RIDER rider cws1 - cws1 r 97.62, the highest ex-fence; rev lift-off 2026-08-30 00:08:10 / pseudo 2026-08-30 00:08:35 | 0.197310 | +0.4633 |
| 2026-08-30 00:18:00 | +18.0 | RETEST - cws1r 97.62 oob + cws2r 57.93 / cws3r 36.62 in - the gate opens; cws1r oob->ib cross 2026-08-30 00:20:00, wob 12, cadence at 2026-08-30 00:20:55 | 0.197310 | +0.4633 |
| 2026-08-30 00:18:15 | +18.2 | the favourable extreme - MFE 0.5906 | 0.197560 | +0.5906 |
| 2026-08-30 00:20:55 | +20.9 | EXHAUST rider cws1 - v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends; rev lift-off 2026-08-30 00:19:10 / pseudo 2026-08-30 00:19:35 | 0.196380 | -0.0102 |
| 2026-08-30 00:20:55 | +20.9 | THIS LEG CLOSES on EXHAUST, realised -0.0458 | 0.196380 | -0.0102 |

## leg 2 of 3 - 2026-08-30 SHORT   opens 2026-08-30 00:21:00   exits 2026-08-30 02:35:20 on EXHAUST   MAE 0.1172 at +16.4 min   MFE 1.8287 at +55.8 min   realised +1.3703   CONTINUITY: UNBROKEN - 1 bar after leg 1 exhaust 2026-08-30 00:20:55

| ts | min from THIS open | event | pxs | pct for THIS leg |
|---|---|---|---|---|
| 2026-08-30 00:00:00 | -21.0 | INCOMING LEG OPENS LONG | 0.196400 | -0.0458 |
| 2026-08-30 00:18:00 | -3.0 | incoming: ARM - cws1b+cws1r: cws1b 109.73 + cws1r 97.62 oob | 0.197310 | -0.5094 |
| 2026-08-30 00:18:00 | -3.0 | incoming: RIDER rider cws1 - cws1 r 97.62, the highest ex-fence; rev lift-off 2026-08-30 00:08:10 / pseudo 2026-08-30 00:08:35 | 0.197310 | -0.5094 |
| 2026-08-30 00:18:00 | -3.0 | incoming: RETEST - cws1r 97.62 oob + cws2r 57.93 / cws3r 36.62 in - the gate opens; cws1r oob->ib cross 2026-08-30 00:20:00, wob 12, cadence at 2026-08-30 00:20:55 | 0.197310 | -0.5094 |
| 2026-08-30 00:20:55 | -0.1 | incoming: EXHAUST rider cws1 - v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends; rev lift-off 2026-08-30 00:19:10 / pseudo 2026-08-30 00:19:35 | 0.196380 | -0.0357 |
| 2026-08-30 00:20:55 | -0.1 | INCOMING LEG CLOSES on EXHAUST, realised -0.0458 | 0.196380 | -0.0357 |
| 2026-08-30 00:21:00 | +0.0 | >>> THIS LEG OPENS SHORT | 0.196310 | -0.0000 |
| 2026-08-30 00:37:25 | +16.4 | the ADVERSE extreme - MAE 0.1172 | 0.196540 | -0.1172 |
| 2026-08-30 01:02:00 | +41.0 | ARM - cws1b+cws1r: cws1b -6.74 + cws1r 10.24 oob | 0.195000 | +0.6673 |
| 2026-08-30 01:02:00 | +41.0 | RIDER rider cws1 - cws1 r 10.24, the highest ex-fence; rev lift-off 2026-08-30 00:58:35 / pseudo 2026-08-30 00:50:35 | 0.195000 | +0.6673 |
| 2026-08-30 01:02:00 | +41.0 | RETEST - cws1r 10.24 oob + cws2r 23.07 / cws3r 51.20 in - the gate opens; cws1r oob->ib cross 2026-08-30 01:04:00, wob 12, cadence at 2026-08-30 01:04:55 | 0.195000 | +0.6673 |
| 2026-08-30 01:04:55 | +43.9 | RIDER rider cws2 - v4-arm-lineage-retest: the re-scan rides cws2 18.31, the highest ex-fence; rev lift-off 2026-08-30 01:04:00 / pseudo 2026-08-30 00:36:35 | 0.195270 | +0.5298 |
| 2026-08-30 01:04:55 | +43.9 | LATCH1 rider cws2 - latch 1 at the t2 cadence 2026-08-30 01:04:55, divergence state -1; rev lift-off 2026-08-30 01:04:00 / pseudo 2026-08-30 00:36:35 | 0.195270 | +0.5298 |
| 2026-08-30 01:04:55 | +43.9 | NO ACTION rider cws2 - t2 cws1r ib cross 01:04:00 confirmed 01:04:55 at wob 12, cws1b 16.84 not oob \| mage-cascade down matches the SHORT - no action, keep walking | 0.195270 | +0.5298 |
| 2026-08-30 01:12:55 | +51.9 | BATON rider cws2 candidates cws3 - ws2 -> ws3, between cadences, lin_hop 2; rev lift-off 2026-08-30 01:08:35 / pseudo 2026-08-30 01:10:35 | 0.194380 | +0.9831 |
| 2026-08-30 01:16:50 | +55.8 | the favourable extreme - MFE 1.8287 | 0.192720 | +1.8287 |
| 2026-08-30 01:21:00 | +60.0 | LATCH1 rider cws3 - latch 1 at the t1 cadence 2026-08-30 01:21:00, divergence state -1; rev lift-off 2026-08-30 01:19:55 / pseudo 2026-08-30 00:42:35 | 0.193970 | +1.1920 |
| 2026-08-30 01:21:00 | +60.0 | NO ACTION rider cws3 - t1 cws1b oob 01:06:00..01:20:55, cws1r reversed 01:20:00 during, stamp 01:20:00 \| mage-cascade down matches the SHORT - no action, keep walking | 0.193970 | +1.1920 |
| 2026-08-30 01:21:55 | +60.9 | BATON rider cws3 candidates ws4,ws5 - ws3 -> ws5, between cadences, lin_hop 2; rev lift-off 2026-08-30 01:19:55 / pseudo 2026-08-30 01:21:35 | 0.194210 | +1.0697 |
| 2026-08-30 01:23:55 | +62.9 | BATON rider ws5 candidates ws6 - ws5 -> ws6, between cadences, lin_hop 2; rev lift-off 2026-08-30 01:22:50 / pseudo 2026-08-30 01:23:25 | 0.194290 | +1.0290 |
| 2026-08-30 01:29:45 | +68.8 | BATON rider ws6 candidates ws8 - ws6 -> ws8, between cadences, lin_hop 2; rev lift-off 2026-08-30 01:20:15 / pseudo 2026-08-30 01:29:25 | 0.193870 | +1.2429 |
| 2026-08-30 01:30:15 | +69.2 | BATON rider ws8 candidates ws9 - ws8 -> ws9, between cadences, lin_hop 2; rev lift-off 2026-08-30 01:26:05 / pseudo 2026-08-30 01:25:25 | 0.194050 | +1.1512 |
| 2026-08-30 01:31:30 | +70.5 | BATON rider ws9 candidates ws11 - ws9 -> ws11, between cadences, lin_hop 2; rev lift-off 2026-08-30 01:23:35 / pseudo 2026-08-30 01:29:25 | 0.193910 | +1.2226 |
| 2026-08-30 01:33:10 | +72.2 | NO PASS rider ws11 candidates none - cws11 19.62 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | 0.194130 | +1.1105 |
| 2026-08-30 01:46:55 | +85.9 | NO ACTION rider ws11 - t2 cws1r ib cross 01:46:00 confirmed 01:46:55 at wob 12, cws1b 60.31 not oob \| mage-cascade down matches the SHORT - no action, keep walking | 0.194590 | +0.8762 |
| 2026-08-30 01:48:55 | +87.9 | NO PASS rider ws11 candidates none - cws11 25.64 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | 0.194250 | +1.0494 |
| 2026-08-30 02:00:55 | +99.9 | LATCH1 rider ws11 - latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1; rev lift-off 2026-08-30 01:37:15 / pseudo 2026-08-30 02:00:00 | 0.193640 | +1.3601 |
| 2026-08-30 02:00:55 | +99.9 | NO ACTION rider ws11 - t2 cws1r ib cross 02:00:00 confirmed 02:00:55 at wob 12, cws1b 39.39 not oob \| mage-cascade down matches the SHORT - no action, keep walking | 0.193640 | +1.3601 |
| 2026-08-30 02:01:45 | +100.8 | NO PASS rider ws11 candidates none - cws11 37.23 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | 0.193800 | +1.2786 |
| 2026-08-30 02:30:00 | +129.0 | LATCH1 rider ws11 - latch 1 at the t1 cadence 2026-08-30 02:30:00, divergence state -1; rev lift-off 2026-08-30 02:12:45 / pseudo 2026-08-30 02:28:55 | 0.193740 | +1.3092 |
| 2026-08-30 02:30:00 | +129.0 | NO ACTION rider ws11 - t1 cws1b ib 02:28:00, cws1r reversed 02:30:00 inside the 120s grace, stamp 02:30:00 \| mage-cascade down matches the SHORT - no action, keep walking | 0.193740 | +1.3092 |
| 2026-08-30 02:30:55 | +129.9 | LATCH1 rider ws11 - latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1; rev lift-off 2026-08-30 02:12:45 / pseudo 2026-08-30 02:28:55 | 0.193610 | +1.3754 |
| 2026-08-30 02:30:55 | +129.9 | NO ACTION rider ws11 - t2 cws1r ib cross 02:30:00 confirmed 02:30:55 at wob 12, cws1b 33.31 not oob \| mage-cascade down matches the SHORT - no action, keep walking | 0.193610 | +1.3754 |
| 2026-08-30 02:31:35 | +130.6 | NO PASS rider ws11 candidates none - cws11 21.30 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | 0.193640 | +1.3601 |
| 2026-08-30 02:35:20 | +134.3 | LATCH1 rider ws11 - latch 1 at the barrage cadence 2026-08-30 02:35:20, divergence state -1; rev lift-off 2026-08-30 02:35:20 / pseudo 2026-08-30 02:32:35 | 0.193600 | +1.3805 |
| 2026-08-30 02:35:20 | +134.3 | EXHAUST rider ws11 - barrage ws1Mage 19.79 LOW oob->ib 02:34:20, ws1r reverses 02:34:45 (25 s), 7 lines reverse with it (ws1,ws2,ws3,ws4,ws8,ws11,ws12), top ws12 - confirmed 02:35:20 \| mage-cascade down \| the walk ends; rev lift-off 2026-08-30 02:35:20 / pseudo 2026-08-30 02:32:35 | 0.193600 | +1.3805 |
| 2026-08-30 02:35:20 | +134.3 | THIS LEG CLOSES on EXHAUST, realised +1.3703 | 0.193600 | +1.3805 |

## leg 3 of 3 - 2026-08-30 LONG   opens 2026-08-30 02:35:25   exits 2026-08-30 02:46:55 on EXHAUST   MAE 0.1653 at +0.6 min   MFE 0.5061 at +7.6 min   realised +0.1963   CONTINUITY: UNBROKEN - 1 bar after leg 2 exhaust 2026-08-30 02:35:20

| ts | min from THIS open | event | pxs | pct for THIS leg |
|---|---|---|---|---|
| 2026-08-30 00:21:00 | -134.4 | INCOMING LEG OPENS SHORT | 0.196310 | +1.3893 |
| 2026-08-30 01:02:00 | -93.4 | incoming: ARM - cws1b+cws1r: cws1b -6.74 + cws1r 10.24 oob | 0.195000 | +0.7127 |
| 2026-08-30 01:02:00 | -93.4 | incoming: RIDER rider cws1 - cws1 r 10.24, the highest ex-fence; rev lift-off 2026-08-30 00:58:35 / pseudo 2026-08-30 00:50:35 | 0.195000 | +0.7127 |
| 2026-08-30 01:02:00 | -93.4 | incoming: RETEST - cws1r 10.24 oob + cws2r 23.07 / cws3r 51.20 in - the gate opens; cws1r oob->ib cross 2026-08-30 01:04:00, wob 12, cadence at 2026-08-30 01:04:55 | 0.195000 | +0.7127 |
| 2026-08-30 01:04:55 | -90.5 | incoming: RIDER rider cws2 - v4-arm-lineage-retest: the re-scan rides cws2 18.31, the highest ex-fence; rev lift-off 2026-08-30 01:04:00 / pseudo 2026-08-30 00:36:35 | 0.195270 | +0.8522 |
| 2026-08-30 01:04:55 | -90.5 | incoming: LATCH1 rider cws2 - latch 1 at the t2 cadence 2026-08-30 01:04:55, divergence state -1; rev lift-off 2026-08-30 01:04:00 / pseudo 2026-08-30 00:36:35 | 0.195270 | +0.8522 |
| 2026-08-30 01:04:55 | -90.5 | incoming: NO ACTION rider cws2 - t2 cws1r ib cross 01:04:00 confirmed 01:04:55 at wob 12, cws1b 16.84 not oob \| mage-cascade down matches the SHORT - no action, keep walking | 0.195270 | +0.8522 |
| 2026-08-30 01:12:55 | -82.5 | incoming: BATON rider cws2 candidates cws3 - ws2 -> ws3, between cadences, lin_hop 2; rev lift-off 2026-08-30 01:08:35 / pseudo 2026-08-30 01:10:35 | 0.194380 | +0.3925 |
| 2026-08-30 01:21:00 | -74.4 | incoming: LATCH1 rider cws3 - latch 1 at the t1 cadence 2026-08-30 01:21:00, divergence state -1; rev lift-off 2026-08-30 01:19:55 / pseudo 2026-08-30 00:42:35 | 0.193970 | +0.1808 |
| 2026-08-30 01:21:00 | -74.4 | incoming: NO ACTION rider cws3 - t1 cws1b oob 01:06:00..01:20:55, cws1r reversed 01:20:00 during, stamp 01:20:00 \| mage-cascade down matches the SHORT - no action, keep walking | 0.193970 | +0.1808 |
| 2026-08-30 01:21:55 | -73.5 | incoming: BATON rider cws3 candidates ws4,ws5 - ws3 -> ws5, between cadences, lin_hop 2; rev lift-off 2026-08-30 01:19:55 / pseudo 2026-08-30 01:21:35 | 0.194210 | +0.3047 |
| 2026-08-30 01:23:55 | -71.5 | incoming: BATON rider ws5 candidates ws6 - ws5 -> ws6, between cadences, lin_hop 2; rev lift-off 2026-08-30 01:22:50 / pseudo 2026-08-30 01:23:25 | 0.194290 | +0.3460 |
| 2026-08-30 01:29:45 | -65.7 | incoming: BATON rider ws6 candidates ws8 - ws6 -> ws8, between cadences, lin_hop 2; rev lift-off 2026-08-30 01:20:15 / pseudo 2026-08-30 01:29:25 | 0.193870 | +0.1291 |
| 2026-08-30 01:30:15 | -65.2 | incoming: BATON rider ws8 candidates ws9 - ws8 -> ws9, between cadences, lin_hop 2; rev lift-off 2026-08-30 01:26:05 / pseudo 2026-08-30 01:25:25 | 0.194050 | +0.2221 |
| 2026-08-30 01:31:30 | -63.9 | incoming: BATON rider ws9 candidates ws11 - ws9 -> ws11, between cadences, lin_hop 2; rev lift-off 2026-08-30 01:23:35 / pseudo 2026-08-30 01:29:25 | 0.193910 | +0.1498 |
| 2026-08-30 01:33:10 | -62.2 | incoming: NO PASS rider ws11 candidates none - cws11 19.62 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | 0.194130 | +0.2634 |
| 2026-08-30 01:46:55 | -48.5 | incoming: NO ACTION rider ws11 - t2 cws1r ib cross 01:46:00 confirmed 01:46:55 at wob 12, cws1b 60.31 not oob \| mage-cascade down matches the SHORT - no action, keep walking | 0.194590 | +0.5010 |
| 2026-08-30 01:48:55 | -46.5 | incoming: NO PASS rider ws11 candidates none - cws11 25.64 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | 0.194250 | +0.3254 |
| 2026-08-30 02:00:55 | -34.5 | incoming: LATCH1 rider ws11 - latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1; rev lift-off 2026-08-30 01:37:15 / pseudo 2026-08-30 02:00:00 | 0.193640 | +0.0103 |
| 2026-08-30 02:00:55 | -34.5 | incoming: NO ACTION rider ws11 - t2 cws1r ib cross 02:00:00 confirmed 02:00:55 at wob 12, cws1b 39.39 not oob \| mage-cascade down matches the SHORT - no action, keep walking | 0.193640 | +0.0103 |
| 2026-08-30 02:01:45 | -33.7 | incoming: NO PASS rider ws11 candidates none - cws11 37.23 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | 0.193800 | +0.0930 |
| 2026-08-30 02:30:00 | -5.4 | incoming: LATCH1 rider ws11 - latch 1 at the t1 cadence 2026-08-30 02:30:00, divergence state -1; rev lift-off 2026-08-30 02:12:45 / pseudo 2026-08-30 02:28:55 | 0.193740 | +0.0620 |
| 2026-08-30 02:30:00 | -5.4 | incoming: NO ACTION rider ws11 - t1 cws1b ib 02:28:00, cws1r reversed 02:30:00 inside the 120s grace, stamp 02:30:00 \| mage-cascade down matches the SHORT - no action, keep walking | 0.193740 | +0.0620 |
| 2026-08-30 02:30:55 | -4.5 | incoming: LATCH1 rider ws11 - latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1; rev lift-off 2026-08-30 02:12:45 / pseudo 2026-08-30 02:28:55 | 0.193610 | -0.0052 |
| 2026-08-30 02:30:55 | -4.5 | incoming: NO ACTION rider ws11 - t2 cws1r ib cross 02:30:00 confirmed 02:30:55 at wob 12, cws1b 33.31 not oob \| mage-cascade down matches the SHORT - no action, keep walking | 0.193610 | -0.0052 |
| 2026-08-30 02:31:35 | -3.8 | incoming: NO PASS rider ws11 candidates none - cws11 21.30 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | 0.193640 | +0.0103 |
| 2026-08-30 02:35:20 | -0.1 | incoming: LATCH1 rider ws11 - latch 1 at the barrage cadence 2026-08-30 02:35:20, divergence state -1; rev lift-off 2026-08-30 02:35:20 / pseudo 2026-08-30 02:32:35 | 0.193600 | -0.0103 |
| 2026-08-30 02:35:20 | -0.1 | incoming: EXHAUST rider ws11 - barrage ws1Mage 19.79 LOW oob->ib 02:34:20, ws1r reverses 02:34:45 (25 s), 7 lines reverse with it (ws1,ws2,ws3,ws4,ws8,ws11,ws12), top ws12 - confirmed 02:35:20 \| mage-cascade down \| the walk ends; rev lift-off 2026-08-30 02:35:20 / pseudo 2026-08-30 02:32:35 | 0.193600 | -0.0103 |
| 2026-08-30 02:35:20 | -0.1 | INCOMING LEG CLOSES on EXHAUST, realised +1.3703 | 0.193600 | -0.0103 |
| 2026-08-30 02:35:25 | +0.0 | >>> THIS LEG OPENS LONG | 0.193620 | +0.0000 |
| 2026-08-30 02:36:00 | +0.6 | the ADVERSE extreme - MAE 0.1653 | 0.193300 | -0.1653 |
| 2026-08-30 02:43:00 | +7.6 | ARM - cws1b+cws1r: cws1b 108.98 + cws1r 89.24 oob | 0.194600 | +0.5061 |
| 2026-08-30 02:43:00 | +7.6 | RIDER rider cws1 - cws1 r 89.24, the highest ex-fence; rev lift-off 2026-08-30 02:36:10 / pseudo 2026-08-30 02:37:35 | 0.194600 | +0.5061 |
| 2026-08-30 02:43:00 | +7.6 | RETEST - cws1r 89.24 oob + cws2r 52.29 / cws3r 44.78 in - the gate opens; cws1r oob->ib cross 2026-08-30 02:46:00, wob 12, cadence at 2026-08-30 02:46:55 | 0.194600 | +0.5061 |
| 2026-08-30 02:43:00 | +7.6 | the favourable extreme - MFE 0.5061 | 0.194600 | +0.5061 |
| 2026-08-30 02:46:55 | +11.5 | EXHAUST rider cws1 - v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends; rev lift-off 2026-08-30 02:44:40 / pseudo 2026-08-30 02:45:35 | 0.193920 | +0.1549 |
| 2026-08-30 02:46:55 | +11.5 | THIS LEG CLOSES on EXHAUST, realised +0.1963 | 0.193920 | +0.1549 |

## the MAE / MFE aggregate over the 3 legs

| leg | the open | dir | the exit | MAE % | MFE % | realised % | drag % | net % |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-08-30 00:00:00 | LONG | 2026-08-30 00:20:55 | 0.5193 | +0.5906 | -0.0458 | 0.1975 | -0.2433 |
| 2 | 2026-08-30 00:21:00 | SHORT | 2026-08-30 02:35:20 | 0.1172 | +1.8287 | +1.3703 | 0.1975 | +1.1728 |
| 3 | 2026-08-30 02:35:25 | LONG | 2026-08-30 02:46:55 | 0.1653 | +0.5061 | +0.1963 | 0.1975 | -0.0012 |
| TOTAL 3 legs | | | | 0.8018 | +2.9255 | +1.5207 | 0.5925 | +0.9282 |
| MEAN per leg | | | | 0.2673 | +0.9752 | +0.5069 | 0.1975 | +0.3094 |

| the read | value |
|---|---|
| legs with an exhaust | 3 of 3 |
| MFE collected | 52.0% |
| drag as a share of summed MFE | 20.3% |
