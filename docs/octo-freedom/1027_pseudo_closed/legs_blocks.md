# THE CHAIN'S LEGS AS BLOCKS, 2026-08-30
# TAPE 1632960 bars | LG_TAPE_END 2026-10-05 | RULED_OK True
# BLOCKS printed: legs 4..6. SUMMARY: every leg walked, 6 of them.
# BOARD: ws1..ws3 keep their reads (cws); ws4.. read PSEUDO (ws) for ex-fence and for the quoted value. LIN2_PSEUDO_MIN_TF 4.
# BARRAGE: LIN2_BARRAGE_MIN_TF 9, LINES 6, TOL 70s, MIN_TF_MODE 'membership' - the pine-emit settings.
# EACH LEG STARTS AT ITS OWN OPEN. The previous leg's rows are not repeated - his 1028
#   ruling. The open is 1 bar after the previous exhaust, which is the rev-trade bar.
# baton candidates: every candidate TF offered at that bar with its r value on the board
#   that answered it. "none offered" is a NO PASS with no candidate inside lin_hop 2.
# realised is priced at the fill bar = exhaust + 1, one bar after the block's last row.
# ex-fence is the 20/80 fence from RMOM_FNC; oob is 15/85.

## leg 4 of 6 - 2026-08-30 SHORT   opens 2026-08-30 02:47:00   exits 2026-08-30 05:02:00 on cws1b counter-oob   MAE 0.3144   MFE 2.2062   realised +1.3041   held 135.0 min   CONTINUITY: UNBROKEN - 1 bar after leg 3 exhaust 2026-08-30 02:46:55

| ts | event | baton candidates | pxs | pct for THIS leg |
|---|---|---|---|---|
| 2026-08-30 02:47:00 | >>> THIS LEG OPENS SHORT | - | 0.194000 | -0.0000 |
| 2026-08-30 02:53:00 | the ADVERSE extreme - MAE 0.3144 | - | 0.194610 | -0.3144 |
| 2026-08-30 03:01:00 | ARM - cws1b+cws1r: cws1b 3.75 + cws1r 7.68 oob | - | 0.192920 | +0.5567 |
| 2026-08-30 03:01:00 | RIDER rider cws1 - cws1 r 7.68, the highest ex-fence; rev lift-off 2026-08-30 02:50:55 / pseudo 2026-08-30 02:52:35 | - | 0.192920 | +0.5567 |
| 2026-08-30 03:01:00 | RETEST - cws1r 7.68 oob + cws2r 22.13 / cws3r 55.36 in - the gate opens; cws1r oob->ib cross 2026-08-30 03:06:00, wob 12, cadence at 2026-08-30 03:06:55 | - | 0.192920 | +0.5567 |
| 2026-08-30 03:06:55 | RIDER rider cws2 - v4-arm-lineage-retest: the re-scan rides cws2 12.28, the highest ex-fence; rev lift-off 2026-08-30 02:51:35 / pseudo 2026-08-30 02:38:35 | - | 0.192420 | +0.8144 |
| 2026-08-30 03:12:55 | BATON rider cws2 - ws2 -> ws3, between cadences, lin_hop 2; rev lift-off 2026-08-30 03:10:15 / pseudo 2026-08-30 03:10:35 | cws3: 11.67 | 0.192330 | +0.8608 |
| 2026-08-30 03:19:00 | LATCH1 rider cws3 - latch 1 at the t1 cadence 2026-08-30 03:19:00, divergence state -1; rev lift-off 2026-08-30 03:15:35 / pseudo 2026-08-30 03:18:35 | - | 0.192290 | +0.8814 |
| 2026-08-30 03:19:00 | NO ACTION rider cws3 - t1 cws1b oob 03:01:00..03:18:55, cws1r reversed 03:09:00 during, stamp 03:09:00 \| mage-cascade down matches the SHORT - no action, keep walking | - | 0.192290 | +0.8814 |
| 2026-08-30 03:21:55 | BATON rider cws3 - ws3 -> ws4, between cadences, lin_hop 2; rev lift-off 2026-08-30 03:15:35 / pseudo 2026-08-30 03:18:35 | ws4: 4.25 | 0.192060 | +1.0000 |
| 2026-08-30 03:27:10 | BATON rider ws4 - ws4 -> ws5, between cadences, lin_hop 2; rev lift-off 2026-08-30 03:24:35 / pseudo 2026-08-30 03:22:50 | ws5: 13.71 | 0.192320 | +0.8660 |
| 2026-08-30 03:30:05 | NO PASS rider ws5 - cws5 27.94 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 0.192550 | +0.7474 |
| 2026-08-30 03:43:55 | LATCH1 rider ws5 - latch 1 at the t2 cadence 2026-08-30 03:43:55, divergence state -1; rev lift-off 2026-08-30 03:30:35 / pseudo 2026-08-30 03:29:45 | - | 0.192460 | +0.7938 |
| 2026-08-30 03:43:55 | NO ACTION rider ws5 - t2 cws1r ib cross 03:43:00 confirmed 03:43:55 at wob 12, cws1b 43.12 not oob \| mage-cascade down matches the SHORT - no action, keep walking | - | 0.192460 | +0.7938 |
| 2026-08-30 03:54:00 | LATCH1 rider ws5 - latch 1 at the t1 cadence 2026-08-30 03:54:00, divergence state -1; rev lift-off 2026-08-30 03:30:35 / pseudo 2026-08-30 03:51:40 | - | 0.191610 | +1.2320 |
| 2026-08-30 03:54:00 | NO ACTION rider ws5 - t1 cws1b oob 03:50:00..03:53:55, cws1r reversed 03:53:00 during, stamp 03:53:00 \| mage-cascade down matches the SHORT - no action, keep walking | - | 0.191610 | +1.2320 |
| 2026-08-30 03:54:55 | LATCH1 rider ws5 - latch 1 at the t2 cadence 2026-08-30 03:54:55, divergence state -1; rev lift-off 2026-08-30 03:30:35 / pseudo 2026-08-30 03:54:45 | - | 0.191480 | +1.2990 |
| 2026-08-30 03:54:55 | NO ACTION rider ws5 - t2 cws1r ib cross 03:54:00 confirmed 03:54:55 at wob 12, cws1b 17.82 not oob \| mage-cascade down matches the SHORT - no action, keep walking | - | 0.191480 | +1.2990 |
| 2026-08-30 04:10:05 | NO PASS rider ws5 - cws5 24.50 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 0.190680 | +1.7113 |
| 2026-08-30 04:13:00 | LATCH1 rider ws5 - latch 1 at the t1 cadence 2026-08-30 04:13:00, divergence state -1; rev lift-off 2026-08-30 03:30:35 / pseudo 2026-08-30 04:11:55 | - | 0.190820 | +1.6392 |
| 2026-08-30 04:13:00 | NO ACTION rider ws5 - t1 cws1b oob 04:06:00..04:12:55, cws1r reversed 04:08:00 during, stamp 04:08:00 \| mage-cascade down matches the SHORT - no action, keep walking | - | 0.190820 | +1.6392 |
| 2026-08-30 04:15:10 | NO PASS rider ws5 - cws5 26.17 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 0.191070 | +1.5103 |
| 2026-08-30 04:15:20 | NO ACTION rider ws5 - latch latch 2: rider cws5 reversed raw 2026-08-30 03:19:30 stamp 2026-08-30 03:20:25, no candidate inside lin_hop, support ws2 raw 2026-08-30 04:14:25 stamp 2026-08-30 04:15:20, ws3 raw 2026-08-30 04:14:00 stamp 2026-08-30 04:14:55, ws4 raw 2026-08-30 04:14:20 stamp 2026-08-30 04:15:15 \| latch 1 at the t1 cadence 2026-08-30 04:13:00, divergence state -1 \| mage-cascade down matches the SHORT - no action, keep walking | - | 0.190970 | +1.5619 |
| 2026-08-30 04:15:40 | BATON rider ws5 - ws5 -> ws7, between cadences, lin_hop 2; rev lift-off 2026-08-30 04:15:00 / pseudo 2026-08-30 04:15:25 | ws7: 16.66 | 0.191000 | +1.5464 |
| 2026-08-30 04:15:55 | NO PASS rider ws7 - cws7 21.20 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 0.191070 | +1.5103 |
| 2026-08-30 04:16:20 | NO ACTION rider ws7 - latch latch 2: rider cws7 reversed raw 2026-08-30 03:18:20 stamp 2026-08-30 03:19:15, no candidate inside lin_hop, support ws4 raw 2026-08-30 04:14:20 stamp 2026-08-30 04:15:15, ws5 raw 2026-08-30 04:15:25 stamp 2026-08-30 04:16:20, ws6 raw 2026-08-30 04:14:45 stamp 2026-08-30 04:15:40 \| latch 1 at the t1 cadence 2026-08-30 04:13:00, divergence state -1 \| mage-cascade down matches the SHORT - no action, keep walking | - | 0.191200 | +1.4433 |
| 2026-08-30 04:17:00 | NO PASS rider ws7 - cws7 26.49 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 0.191280 | +1.4021 |
| 2026-08-30 04:47:20 | the favourable extreme - MFE 2.2062 | - | 0.189720 | +2.2062 |
| 2026-08-30 05:02:00 | CADENCE rider ws7 - cws1b counter-oob cws1b 99.93 entered the HIGH oob 05:02:00 \| rider cws7 69.22, no-longer-exfence yes, reversed yes \| mage-cascade down | none offered | 0.191420 | +1.3299 |
| 2026-08-30 05:02:00 | EXHAUST rider ws7 - t4 at a cws1b counter-oob cadence - rider cws7 69.22, no candidate inside lin_hop 2; rev lift-off 2026-08-30 04:53:50 / pseudo 2026-08-30 04:54:35 | - | 0.191420 | +1.3299 |
| 2026-08-30 05:02:00 | THIS LEG CLOSES on cws1b counter-oob, realised +1.3041 | - | 0.191420 | +1.3299 |

## leg 5 of 6 - 2026-08-30 LONG   opens 2026-08-30 05:02:05   exits 2026-08-30 05:11:00 on t1   MAE 0.0313   MFE 0.5066   realised +0.1828   held 8.9 min   CONTINUITY: UNBROKEN - 1 bar after leg 4 exhaust 2026-08-30 05:02:00

| ts | event | baton candidates | pxs | pct for THIS leg |
|---|---|---|---|---|
| 2026-08-30 05:02:05 | >>> THIS LEG OPENS LONG | - | 0.191470 | +0.0000 |
| 2026-08-30 05:02:05 | the ADVERSE extreme - MAE 0.0313 | - | 0.191410 | -0.0313 |
| 2026-08-30 05:04:00 | ARM - cws1b+cws1r: cws1b 115.76 + cws1r 85.53 oob | - | 0.191960 | +0.2559 |
| 2026-08-30 05:04:00 | RIDER rider cws1 - cws1 r 85.53, the highest ex-fence; rev lift-off 2026-08-30 04:58:35 / pseudo 2026-08-30 04:59:35 | - | 0.191960 | +0.2559 |
| 2026-08-30 05:04:00 | RETEST - cws1r 85.53 oob + cws2r 75.45 / cws3r 52.02 in - the gate opens; cws1r oob->ib cross 2026-08-30 05:07:00, wob 12, cadence at 2026-08-30 05:07:55 | - | 0.191960 | +0.2559 |
| 2026-08-30 05:07:35 | the favourable extreme - MFE 0.5066 | - | 0.192440 | +0.5066 |
| 2026-08-30 05:07:55 | RIDER rider ws8 - v4-arm-lineage-retest: the re-scan rides cws8 82.30, the highest ex-fence; rev lift-off 2026-08-30 04:47:45 / pseudo 2026-08-30 05:01:25 | - | 0.192230 | +0.3969 |
| 2026-08-30 05:08:50 | NO PASS rider ws8 - cws8 69.47 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 0.192130 | +0.3447 |
| 2026-08-30 05:11:00 | EXHAUST rider ws8 - t1 cws1b oob 05:02:00..05:10:55, cws1r reversed 05:07:00 during, stamp 05:07:00 \| mage-cascade down OPPOSES the LONG - rev-trade; rev lift-off 2026-08-30 04:47:45 / pseudo 2026-08-30 05:09:25 | - | 0.191770 | +0.1567 |
| 2026-08-30 05:11:00 | THIS LEG CLOSES on t1, realised +0.1828 | - | 0.191770 | +0.1567 |

## leg 6 of 6 - 2026-08-30 SHORT   opens 2026-08-30 05:11:05   exits 2026-08-30 07:44:00 on t1   MAE 1.1156   MFE 0.6725   realised +0.4431   held 152.9 min   CONTINUITY: UNBROKEN - 1 bar after leg 5 exhaust 2026-08-30 05:11:00

| ts | event | baton candidates | pxs | pct for THIS leg |
|---|---|---|---|---|
| 2026-08-30 05:11:05 | >>> THIS LEG OPENS SHORT | - | 0.191820 | -0.0000 |
| 2026-08-30 06:59:15 | the ADVERSE extreme - MAE 1.1156 | - | 0.193960 | -1.1156 |
| 2026-08-30 07:22:15 | ARM - cws4r: cws4r 14.45 oob | - | 0.192250 | -0.2242 |
| 2026-08-30 07:22:15 | RIDER rider ws4 - cws4 r 14.45, the highest ex-fence; rev lift-off 2026-08-30 07:10:35 / pseudo 2026-08-30 07:15:10 | - | 0.192250 | -0.2242 |
| 2026-08-30 07:22:15 | RETEST - cws2r 28.00 / cws3r 12.22 - not both inside the fence at the arm | - | 0.192250 | -0.2242 |
| 2026-08-30 07:24:15 | NO PASS rider ws4 - cws4 22.90 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 | none offered | 0.192280 | -0.2398 |
| 2026-08-30 07:43:20 | the favourable extreme - MFE 0.6725 | - | 0.190530 | +0.6725 |
| 2026-08-30 07:44:00 | LATCH1 rider ws4 - latch 1 at the t1 cadence 2026-08-30 07:44:00, divergence state -1; rev lift-off 2026-08-30 07:10:35 / pseudo 2026-08-30 07:40:40 | - | 0.190990 | +0.4327 |
| 2026-08-30 07:44:00 | EXHAUST rider ws4 - t1 cws1b oob 07:26:00..07:43:55, cws1r reversed 07:40:00 during, stamp 07:40:00 \| mage-cascade up OPPOSES the SHORT - rev-trade; rev lift-off 2026-08-30 07:10:35 / pseudo 2026-08-30 07:40:40 | - | 0.190990 | +0.4327 |
| 2026-08-30 07:44:00 | THIS LEG CLOSES on t1, realised +0.4431 | - | 0.190990 | +0.4327 |

## the summary - one row per leg, every leg walked

| leg | the open | dir | the exit | ended by | held min | the rider chain | MAE % | MFE % | realised % | drag % | net % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-08-30 00:00:00 | LONG | 2026-08-30 00:20:55 | retest | 20.9 | cws1 | 0.5193 | +0.5906 | -0.0458 | 0.1975 | -0.2433 |
| 2 | 2026-08-30 00:21:00 | SHORT | 2026-08-30 02:35:20 | barrage | 134.3 | cws1 > cws2 > cws3 > ws5 > ws6 > ws8 > ws9 > ws11 | 0.1172 | +1.8287 | +1.3703 | 0.1975 | +1.1728 |
| 3 | 2026-08-30 02:35:25 | LONG | 2026-08-30 02:46:55 | retest | 11.5 | cws1 | 0.1653 | +0.5061 | +0.1963 | 0.1975 | -0.0012 |
| 4 | 2026-08-30 02:47:00 | SHORT | 2026-08-30 05:02:00 | cws1b counter-oob | 135.0 | cws1 > cws2 > cws3 > ws4 > ws5 > ws7 | 0.3144 | +2.2062 | +1.3041 | 0.1975 | +1.1066 |
| 5 | 2026-08-30 05:02:05 | LONG | 2026-08-30 05:11:00 | t1 | 8.9 | cws1 > ws8 | 0.0313 | +0.5066 | +0.1828 | 0.1975 | -0.0147 |
| 6 | 2026-08-30 05:11:05 | SHORT | 2026-08-30 07:44:00 | t1 | 152.9 | ws4 | 1.1156 | +0.6725 | +0.4431 | 0.1975 | +0.2456 |
| TOTAL 6 legs | | | | | 463.6 | | 2.2632 | +6.3108 | +3.4508 | 1.1850 | +2.2658 |
| MEAN per leg | | | | | 77.3 | | 0.3772 | +1.0518 | +0.5751 | 0.1975 | +0.3776 |

| the read | value |
|---|---|
| legs with an exhaust | 6 of 6 |
| legs net-positive after drag | 3 of 6 |
| MFE collected | 54.7% |
| drag as a share of summed MFE | 18.8% |
| summed drag in its own right | 1.1850% over 6 round trips |

| ended by | legs | summed realised % | summed net % |
|---|---|---|---|
| barrage | 1 | +1.3703 | +1.1728 |
| cws1b counter-oob | 1 | +1.3041 | +1.1066 |
| retest | 2 | +0.1504 | -0.2446 |
| t1 | 2 | +0.6259 | +0.2309 |
