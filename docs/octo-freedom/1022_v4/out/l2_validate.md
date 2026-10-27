# lineage2 VALIDATION against his 1025 examples. RULED_OK True
# L2_MOM_MAXTF 12 | L2_LIN_HOP 2 | L2_T1_GRACE_S 120 | L2_T3_FRAC 0.75 | RMOM_FNC 80.0
# L2_CWS1R_WOB 1 | L2_GATE_MODE closed | STATE closed, reversal TIMING emerging,
#   t3 GATES on closed - routed by v4_l2_proxy.Board

## t1cadence - his examples

| his example | side | my nearest t1 | gap | why | his verdict |
|---|---|---|---|---|---|
| 2026-08-29 04:30:00 | LOW | 2026-08-29 04:37:00 | +420 s | t1 | NOT a cadence |
| 2026-08-29 04:36:00 | LOW | 2026-08-29 04:37:00 | +60 s | t1 | a cadence |
| 2026-08-29 07:47:00 | HIGH | 2026-08-29 07:50:00 | +180 s | t1 | cws1r not yet qualified |
| 2026-08-29 07:48:00 | HIGH | 2026-08-29 07:50:00 | +120 s | t1 | the cadence fires |

## t2cadence - his examples

| his example | side | my nearest t2 | gap | why |
|---|---|---|---|---|
| 2026-08-28 14:58:00 | HIGH | 2026-08-28 14:59:55 | +115 s | t2 |
| 2026-08-28 17:48:00 | HIGH | 2026-08-28 17:49:55 | +115 s | t2 |
| 2026-08-29 05:42:00 | LOW | 2026-08-29 05:30:55 | -665 s | t2 |
| 2026-08-29 05:42:00 | HIGH | 2026-08-29 05:43:55 | +115 s | t2 |
| 2026-08-29 10:13:00 | LOW | 2026-08-29 10:07:55 | -305 s | t2 |
| 2026-08-29 10:13:00 | HIGH | 2026-08-29 10:14:55 | +115 s | t2 |

## his 2026-08-29 07:04 HIGH walk - every row

| the bar | stage | why |
|---|---|---|
| 2026-08-29 07:00:00 | ARM | cws4r: cws4r 90.21 oob |
| 2026-08-29 07:00:00 | RIDER | cws4 r 90.21, the highest ex-fence |
| 2026-08-29 07:00:00 | RETEST | cws1r 12.10 is not oob at the arm - the gate stays shut |
| 2026-08-29 07:08:55 | BATON | ws4 -> ws5, between cadences, lin_hop 2 |
| 2026-08-29 07:10:55 | NO PASS | cws5 81.54 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-29 07:24:00 | LATCH1 | latch 1 at the t1 cadence 2026-08-29 07:24:00, divergence state +1 |
| 2026-08-29 07:24:00 | EXHAUST | t1 cws1b ib 07:23:00, cws1r reversed 07:24:00 inside the 120s grace, stamp 07:24:00 | mage-cascade down OPPOSES the LONG - rev-trade |

verdict EXHAUST at 2026-08-29 07:24:00. his: t1 0704, t2 0723, t1 0734, t1 0747, t3 0749 end-of-walk

## his 2026-08-30 18:37 walk - every row

### target-side LOW

| the bar | stage | why |
|---|---|---|
| 2026-08-30 19:26:00 | ARM | cws1b+cws1r: cws1b -7.44 + cws1r 12.71 oob |
| 2026-08-30 19:26:00 | RIDER | cws1 r 12.71, the highest ex-fence |
| 2026-08-30 19:26:00 | RETEST | cws1r 12.71 oob + cws2r 36.76 / cws3r 45.91 in - the gate opens; cws1r oob->ib cross 2026-08-30 19:31:00, wob 12, cadence at 2026-08-30 19:31:55 |
| 2026-08-30 19:31:55 | EXHAUST | v4-arm-lineage-retest: no cws1..cws12 r is ex-fence at the gate cadence - the walk ends |

verdict EXHAUST at 2026-08-30 19:31:55

### target-side HIGH

| the bar | stage | why |
|---|---|---|
| 2026-08-30 18:35:00 | ARM | cws1b+cws1r: cws1b 95.76 + cws1r 91.98 oob |
| 2026-08-30 18:35:00 | RIDER | cws5 r 80.58, the highest ex-fence |
| 2026-08-30 18:35:00 | RETEST | cws2r 82.90 / cws3r 50.95 - not both inside the fence at the arm |
| 2026-08-30 18:38:00 | LATCH1 | latch 1 at the t1 cadence 2026-08-30 18:38:00, divergence state +1 |
| 2026-08-30 18:38:00 | EXHAUST | t1 cws1b oob 18:32:00..18:37:55, cws1r reversed 18:37:00 during, stamp 18:37:00 | mage-cascade down OPPOSES the LONG - rev-trade |

verdict EXHAUST at 2026-08-30 18:38:00

his: t1 1837, baton 1842 ws6->ws7, 1844 ws7->ws8, t4 1902 ws8 reverses, ws11 exfence,
     1915 ws11 oob->ib, t3 end-of-walk

## his 2026-08-29 02:35 basic walk - LONG, target-side HIGH

| the bar | stage | why |
|---|---|---|
| 2026-08-29 03:04:00 | ARM | cws4r: cws4r 91.34 oob |
| 2026-08-29 03:04:00 | RIDER | cws4 r 91.34, the highest ex-fence |
| 2026-08-29 03:04:00 | RETEST | cws1r 27.64 is not oob at the arm - the gate stays shut |
| 2026-08-29 03:08:55 | NO PASS | cws4 81.11 ATTEMPTS to hand over, between cadences - no candidate inside lin_hop 2 |
| 2026-08-29 03:38:00 | CADENCE | cws1b counter-oob cws1b 14.13 entered the LOW oob 03:38:00 | rider cws4 50.54, no-longer-exfence yes, reversed yes | mage-cascade up |
| 2026-08-29 03:38:00 | EXHAUST | t4 at a cws1b counter-oob cadence - rider cws4 50.54, no candidate inside lin_hop 2 |

verdict EXHAUST at 2026-08-29 03:38:00. his: arm 0300 on ws4r oob, t1 0303, exhaust -> SHORT, then arm 0356 low

## the barrage producer, 2026-08-30, against out/l2_barrage.md

# LIN2_BARRAGE_TOL_S 70 s | LIN2_BARRAGE_LINES 6 | LIN2_BARRAGE_MIN_TF 9 | ON 1
# the cadence bar is the LAST CONTRIBUTING REVERSAL'S STAMP - the raw ws1r reversal bar is
#   in the why, so the banked list and this table can be lined up.

| the target side | the cadence bar | why |
|---|---|---|
| LOW | 2026-08-30 02:35:20 | ws1Mage 19.79 LOW oob->ib 02:34:20, ws1r reverses 02:34:45 (25 s), 7 lines reverse with it (ws1,ws2,ws3,ws4,ws8,ws11,ws12), top ws12 - confirmed 02:35:20 |
| LOW | 2026-08-30 09:45:20 | ws1Mage 18.23 LOW oob->ib 09:43:45, ws1r reverses 09:44:45 (60 s), 8 lines reverse with it (ws1,ws4,ws5,ws6,ws7,ws9,ws11,ws12), top ws12 - confirmed 09:45:20 |
| LOW | 2026-08-30 10:06:00 | ws1Mage 18.80 LOW oob->ib 10:04:45, ws1r reverses 10:05:25 (40 s), 11 lines reverse with it (ws1,ws2,ws3,ws4,ws5,ws6,ws8,ws9,ws10,ws11,ws12), top ws12 - confirmed 10:06:00 |
| LOW | 2026-08-30 19:07:55 | ws1Mage 22.05 LOW oob->ib 19:06:20, ws1r reverses 19:07:20 (60 s), 8 lines reverse with it (ws1,ws4,ws5,ws7,ws8,ws9,ws10,ws11), top ws11 - confirmed 19:07:55 |

| the read | value |
|---|---|
| cadences produced | 4 |
| on the LOW target side | 4 |
| on the HIGH target side | 0 |
| his 02:29 instance | DROPPED by LIN2_BARRAGE_MIN_TF 9, his ruling |
| the 02:34 instance that replaces it | present |
