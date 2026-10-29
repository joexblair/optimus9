# THE FIRST 3 LEGS ON THE PSEUDO BOARD, 2026-08-30
# ws1..ws3 keep their reads; ws4.. read PSEUDO for ex-fence and for the value shown.
# the walk is unchanged - every banked mech, decisions at cadences. only the board moved.
# the WALK acts on lift-off; both reversal times are reported. his ruling.
# the rider prefix says which board answered: cws = closed, ws = pseudo.
# RULED_OK True | LIN2_PSEUDO_MIN_TF 4 | LIFT_WOB 8

## leg 1 - target side HIGH, walking from 2026-08-30 00:00:00

| the bar | stage | rider | its value | board | lift-off rev | pseudo rev | candidates | why |
|---|---|---|---|---|---|---|---|---|
| 2026-08-30 00:18:00 | ARM | - | - | - | - | - | - | cws1b+cws1r: cws1b 109.73 + cws1r 97.62 oob |
| 2026-08-30 00:18:00 | RIDER | cws1 | 97.62 | closed | 2026-08-30 00:08:10 | 2026-08-30 00:08:35 | - | cws1 r 97.62, the highest ex-fence |
| 2026-08-30 00:18:00 | RETEST | - | - | - | - | - | - | cws1r 97.62 oob + cws2r 57.93 / cws3r 36.62 in - the gate opens; cws1r oob->ib cross 2026-08-30 00:20:00, wob 12, cadence at 2026-08-30 00:20:55 |
| 2026-08-30 00:20:55 | EXHAUST | cws1 | 78.56 | closed | 2026-08-30 00:19:10 | 2026-08-30 00:19:35 | - | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |

| leg 1 | value |
|---|---|
| the verdict | EXHAUST |
| the bar | 2026-08-30 00:20:55 |
| the arm | 2026-08-30 00:18:00 |
| rows | 4 |

## leg 2 - target side LOW, walking from 2026-08-30 00:20:55

| the bar | stage | rider | its value | board | lift-off rev | pseudo rev | candidates | why |
|---|---|---|---|---|---|---|---|---|
| 2026-08-30 01:02:00 | ARM | - | - | - | - | - | - | cws1b+cws1r: cws1b -6.74 + cws1r 10.24 oob |
| 2026-08-30 01:02:00 | RIDER | cws1 | 10.24 | closed | 2026-08-30 00:58:35 | 2026-08-30 00:50:35 | - | cws1 r 10.24, the highest ex-fence |
| 2026-08-30 01:02:00 | RETEST | - | - | - | - | - | - | cws1r 10.24 oob + cws2r 23.07 / cws3r 51.20 in - the gate opens; cws1r oob->ib cross 2026-08-30 01:04:00, wob 12, cadence at 2026-08-30 01:04:55 |
| 2026-08-30 01:04:55 | RIDER | cws2 | 18.31 | closed | 2026-08-30 01:04:00 | 2026-08-30 00:36:35 | - | v4-arm-lineage-retest: the re-scan rides cws2 18.31, the highest ex-fence |
| 2026-08-30 01:04:55 | LATCH1 | cws2 | 18.31 | closed | 2026-08-30 01:04:00 | 2026-08-30 00:36:35 | - | latch 1 at the t2 cadence 2026-08-30 01:04:55, divergence state -1 |
| 2026-08-30 01:04:55 | NO ACTION | cws2 | 18.31 | closed | 2026-08-30 01:04:00 | 2026-08-30 00:36:35 | - | t2 cws1r ib cross 01:04:00 confirmed 01:04:55 at wob 12, cws1b 16.84 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 01:12:55 | BATON | cws2 | 24.16 | closed | 2026-08-30 01:08:35 | 2026-08-30 01:10:35 | ws3 | ws2 -> ws3, between cadences, lin_hop 2 |
| 2026-08-30 01:21:00 | LATCH1 | cws3 | 20.97 | closed | 2026-08-30 01:19:55 | 2026-08-30 00:42:35 | - | latch 1 at the t1 cadence 2026-08-30 01:21:00, divergence state -1 |
| 2026-08-30 01:21:00 | NO ACTION | cws3 | 20.97 | closed | 2026-08-30 01:19:55 | 2026-08-30 00:42:35 | - | t1 cws1b oob 01:06:00..01:20:55, cws1r reversed 01:20:00 during, stamp 01:20:00 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 01:21:55 | BATON | cws3 | 20.97 | closed | 2026-08-30 01:19:55 | 2026-08-30 01:21:35 | ws4,ws5 | ws3 -> ws5, between cadences, lin_hop 2 |
| 2026-08-30 01:23:55 | BATON | ws5 | 20.48 | pseudo | 2026-08-30 01:22:50 | 2026-08-30 01:23:25 | ws6 | ws5 -> ws6, between cadences, lin_hop 2 |
| 2026-08-30 01:29:45 | BATON | ws6 | 22.05 | pseudo | 2026-08-30 01:20:15 | 2026-08-30 01:29:25 | ws8 | ws6 -> ws8, between cadences, lin_hop 2 |
| 2026-08-30 01:30:15 | BATON | ws8 | 19.61 | pseudo | 2026-08-30 01:26:05 | 2026-08-30 01:25:25 | ws9 | ws8 -> ws9, between cadences, lin_hop 2 |
| 2026-08-30 01:31:30 | BATON | ws9 | 17.42 | pseudo | 2026-08-30 01:23:35 | 2026-08-30 01:29:25 | ws11 | ws9 -> ws11, between cadences, lin_hop 2 |
| 2026-08-30 01:33:10 | NO PASS | ws11 | 19.62 | pseudo | 2026-08-30 01:20:45 | 2026-08-30 01:22:10 | none | cws11 19.62 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 01:46:55 | NO ACTION | ws11 | 22.96 | pseudo | 2026-08-30 01:37:15 | 2026-08-30 01:45:50 | - | t2 cws1r ib cross 01:46:00 confirmed 01:46:55 at wob 12, cws1b 60.31 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 01:48:55 | NO PASS | ws11 | 25.64 | pseudo | 2026-08-30 01:37:15 | 2026-08-30 01:48:40 | none | cws11 25.64 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 02:00:55 | LATCH1 | ws11 | 33.49 | pseudo | 2026-08-30 01:37:15 | 2026-08-30 02:00:00 | - | latch 1 at the t2 cadence 2026-08-30 02:00:55, divergence state -1 |
| 2026-08-30 02:00:55 | NO ACTION | ws11 | 33.49 | pseudo | 2026-08-30 01:37:15 | 2026-08-30 02:00:00 | - | t2 cws1r ib cross 02:00:00 confirmed 02:00:55 at wob 12, cws1b 39.39 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:01:45 | NO PASS | ws11 | 37.23 | pseudo | 2026-08-30 01:37:15 | 2026-08-30 02:00:00 | none | cws11 37.23 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 02:30:00 | LATCH1 | ws11 | 19.33 | pseudo | 2026-08-30 02:12:45 | 2026-08-30 02:28:55 | - | latch 1 at the t1 cadence 2026-08-30 02:30:00, divergence state -1 |
| 2026-08-30 02:30:00 | NO ACTION | ws11 | 19.33 | pseudo | 2026-08-30 02:12:45 | 2026-08-30 02:28:55 | - | t1 cws1b ib 02:28:00, cws1r reversed 02:30:00 inside the 120s grace, stamp 02:30:00 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:30:55 | LATCH1 | ws11 | 22.80 | pseudo | 2026-08-30 02:12:45 | 2026-08-30 02:28:55 | - | latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1 |
| 2026-08-30 02:30:55 | NO ACTION | ws11 | 22.80 | pseudo | 2026-08-30 02:12:45 | 2026-08-30 02:28:55 | - | t2 cws1r ib cross 02:30:00 confirmed 02:30:55 at wob 12, cws1b 33.31 not oob \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:31:35 | NO PASS | ws11 | 21.30 | pseudo | 2026-08-30 02:12:45 | 2026-08-30 02:28:55 | none | cws11 21.30 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 02:39:55 | NO ACTION | ws11 | 38.88 | pseudo | 2026-08-30 02:38:10 | 2026-08-30 02:39:55 | - | latch latch 2: rider cws11 reversed raw 2026-08-30 01:20:10 stamp 2026-08-30 01:21:05, no candidate inside lin_hop, support ws8 raw 2026-08-30 02:37:15 stamp 2026-08-30 02:38:10, ws9 raw 2026-08-30 02:37:20 stamp 2026-08-30 02:38:15, ws10 raw 2026-08-30 02:39:00 stamp 2026-08-30 02:39:55 \| latch 1 at the t2 cadence 2026-08-30 02:30:55, divergence state -1 \| mage-cascade down matches the SHORT - no action, keep walking |
| 2026-08-30 02:40:10 | NO PASS | ws11 | 39.08 | pseudo | 2026-08-30 02:38:10 | 2026-08-30 02:39:55 | none | cws11 39.08 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-30 02:41:00 | CADENCE | ws11 | 33.62 | pseudo | 2026-08-30 02:38:10 | 2026-08-30 02:39:55 | none | cws1b counter-oob cws1b 88.94 entered the HIGH oob 02:41:00 \| rider cws11 33.62, no-longer-exfence yes, reversed no \| mage-cascade down |
| 2026-08-30 02:41:00 | EXHAUST | ws11 | 33.62 | pseudo | 2026-08-30 02:38:10 | 2026-08-30 02:39:55 | - | exhaust at a cws1b counter-oob cadence - rider cws11 33.62, no candidate inside lin_hop 2 |

| leg 2 | value |
|---|---|
| the verdict | EXHAUST |
| the bar | 2026-08-30 02:41:00 |
| the arm | 2026-08-30 01:02:00 |
| rows | 29 |

## leg 3 - target side HIGH, walking from 2026-08-30 02:41:00

| the bar | stage | rider | its value | board | lift-off rev | pseudo rev | candidates | why |
|---|---|---|---|---|---|---|---|---|
| 2026-08-30 02:43:00 | ARM | - | - | - | - | - | - | cws1b+cws1r: cws1b 108.98 + cws1r 89.24 oob |
| 2026-08-30 02:43:00 | RIDER | cws1 | 89.24 | closed | 2026-08-30 02:36:10 | 2026-08-30 02:37:35 | - | cws1 r 89.24, the highest ex-fence |
| 2026-08-30 02:43:00 | RETEST | - | - | - | - | - | - | cws1r 89.24 oob + cws2r 52.29 / cws3r 44.78 in - the gate opens; cws1r oob->ib cross 2026-08-30 02:46:00, wob 12, cadence at 2026-08-30 02:46:55 |
| 2026-08-30 02:46:55 | EXHAUST | cws1 | 74.76 | closed | 2026-08-30 02:44:40 | 2026-08-30 02:45:35 | - | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |

| leg 3 | value |
|---|---|
| the verdict | EXHAUST |
| the bar | 2026-08-30 02:46:55 |
| the arm | 2026-08-30 02:43:00 |
| rows | 4 |

