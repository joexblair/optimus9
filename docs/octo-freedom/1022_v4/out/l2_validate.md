# lineage2 VALIDATION against his 1025 examples. RULED_OK True
# L2_MOM_MAXTF 12 | L2_LIN_HOP 2 | L2_T1_GRACE_S 120 | L2_T3_FRAC 0.75 | RMOM_FNC 80.0
# L2_CWS1R_WOB 1 | L2_GATE_MODE emerging | STATE closed, reversal TIMING emerging,
#   t3 GATES on emerging - routed by v4_l2_proxy.Board

## t1cadence - his examples

| his example | side | my nearest t1 | gap | why | his verdict |
|---|---|---|---|---|---|
| 2026-08-29 04:30:00 | LOW | 2026-08-29 04:36:00 | +360 s | t1 cws1b oob 04:31:00..04:35:55, cws1r reversed 04:35:00 during, stamp 04:35:00 | NOT a cadence |
| 2026-08-29 04:36:00 | LOW | 2026-08-29 04:36:00 | +0 s | t1 cws1b oob 04:31:00..04:35:55, cws1r reversed 04:35:00 during, stamp 04:35:00 | a cadence |
| 2026-08-29 07:47:00 | HIGH | 2026-08-29 07:49:00 | +120 s | t1 cws1b ib 07:47:00, cws1r reversed 07:49:00 inside the 120s grace, stamp 07:49:00 | cws1r not yet qualified |
| 2026-08-29 07:48:00 | HIGH | 2026-08-29 07:49:00 | +60 s | t1 cws1b ib 07:47:00, cws1r reversed 07:49:00 inside the 120s grace, stamp 07:49:00 | the cadence fires |

## t2cadence - his examples

| his example | side | my nearest t2 | gap | why |
|---|---|---|---|---|
| 2026-08-28 14:58:00 | HIGH | 2026-08-28 14:58:00 | +0 s | t2 cws1r ib 14:58:00, cws1b 75.59 not oob |
| 2026-08-28 17:48:00 | HIGH | 2026-08-28 17:48:00 | +0 s | t2 cws1r ib 17:48:00, cws1b 79.23 not oob |
| 2026-08-29 05:42:00 | LOW | 2026-08-29 05:29:20 | -760 s | t2 cws1r ib 05:29:20, cws1b 57.59 not oob |
| 2026-08-29 05:42:00 | HIGH | 2026-08-29 05:42:00 | +0 s | t2 cws1r ib 05:42:00, cws1b 64.36 not oob |
| 2026-08-29 10:13:00 | LOW | 2026-08-29 10:06:00 | -420 s | t2 cws1r ib 10:06:00, cws1b 40.91 not oob |
| 2026-08-29 10:13:00 | HIGH | 2026-08-29 10:13:00 | +0 s | t2 cws1r ib 10:13:00, cws1b 35.39 not oob |

## his 2026-08-29 07:04 HIGH walk - every row

| the bar | stage | why |
|---|---|---|
| 2026-08-29 07:00:05 | ARM | ws4r: ws4r 85.48 oob |
| 2026-08-29 07:00:05 | RIDER | cws5 r 91.61, the highest ex-fence |
| 2026-08-29 07:23:00 | CADENCE | t1 cws1b ib 07:22:00, cws1r reversed 07:23:00 inside the 120s grace, stamp 07:23:00 | rider cws5 57.50, no-longer-exfence yes, reversed yes |
| 2026-08-29 07:23:00 | BATON | ws5 -> ws7, at a cadence, whole board |
| 2026-08-29 07:23:00 | CADENCE | t2 cws1r ib 07:23:00, cws1b 66.86 not oob | rider cws7 80.86, no-longer-exfence no, reversed no |
| 2026-08-29 07:23:00 | HOLD | rider cws7 80.86 ex-fence and not reversed - no action |
| 2026-08-29 07:34:05 | CADENCE | t3 1 of 1 oob HTF lines reversed (ws7), none above ws7 ex-fence [gate on emerging] | rider cws7 80.36, no-longer-exfence no, reversed yes |
| 2026-08-29 07:34:05 | BATON | ws7 -> ws9, at a cadence, whole board |
| 2026-08-29 07:49:00 | CADENCE | t1 cws1b ib 07:47:00, cws1r reversed 07:49:00 inside the 120s grace, stamp 07:49:00 | rider cws9 78.32, no-longer-exfence yes, reversed yes |
| 2026-08-29 07:49:00 | EXHAUST | t4 - rider cws9 78.32, no candidate on the whole board |

verdict EXHAUST at 2026-08-29 07:49:00. his: t1 0704, t2 0723, t1 0734, t1 0747, t3 0749 end-of-walk

## his 2026-08-30 18:37 walk - every row

### target-side LOW

| the bar | stage | why |
|---|---|---|
| 2026-08-30 19:16:00 | ARM | ws4r: ws4r 14.46 oob |
| 2026-08-30 19:16:05 | NO RIDER | no cws1..cws12 r is ex-fence at the arm bar + 5s - the walk continues, t3 and t4 stay reachable |
| 2026-08-30 19:50:00 | RIDER | t3 1 of 1 oob HTF lines reversed (ws7), none above ws7 ex-fence [gate on emerging] | cws7 r 15.15 picked up at a cadence, no prior rider |
| 2026-08-30 19:51:00 | CADENCE | t1 cws1b oob 19:21:00..19:50:55, cws1r reversed 19:45:00 during, stamp 19:45:00 | rider cws7 15.15, no-longer-exfence no, reversed no |
| 2026-08-30 19:51:00 | HOLD | rider cws7 15.15 ex-fence and not reversed - no action |
| 2026-08-30 20:11:00 | BATON | ws7 -> ws9, between cadences, lin_hop 2 |
| 2026-08-30 20:35:00 | CADENCE | t2 cws1r ib 20:35:00, cws1b 35.26 not oob | rider cws9 44.88, no-longer-exfence yes, reversed yes |
| 2026-08-30 20:35:00 | EXHAUST | t4 - rider cws9 44.88, no candidate on the whole board |

verdict EXHAUST at 2026-08-30 20:35:00

### target-side HIGH

| the bar | stage | why |
|---|---|---|
| 2026-08-30 18:35:00 | ARM | cws1b+cws1r: cws1b 90.25 + cws1r 94.66 oob |
| 2026-08-30 18:35:00 | RIDER | cws6 r 89.70, the highest ex-fence |
| 2026-08-30 18:37:00 | CADENCE | t1 cws1b oob 18:31:00..18:36:55, cws1r reversed 18:36:00 during, stamp 18:36:00 | rider cws6 89.23, no-longer-exfence no, reversed no |
| 2026-08-30 18:37:00 | HOLD | rider cws6 89.23 oob - no action |
| 2026-08-30 18:42:00 | BATON | ws6 -> ws8, between cadences, lin_hop 2 |
| 2026-08-30 18:56:10 | CADENCE | t3 3 of 3 oob HTF lines reversed (ws7,8,11), none above ws11 ex-fence [gate on emerging] | rider cws8 80.58, no-longer-exfence no, reversed yes |
| 2026-08-30 18:56:10 | BATON | ws8 -> ws11, at a cadence, whole board |
| 2026-08-30 19:54:00 | CADENCE | t2 cws1r ib 19:54:00, cws1b 20.67 not oob | rider cws11 35.11, no-longer-exfence yes, reversed yes |
| 2026-08-30 19:54:00 | EXHAUST | t4 - rider cws11 35.11, no candidate on the whole board |

verdict EXHAUST at 2026-08-30 19:54:00

his: t1 1837, baton 1842 ws6->ws7, 1844 ws7->ws8, t4 1902 ws8 reverses, ws11 exfence,
     1915 ws11 oob->ib, t3 end-of-walk

## his 2026-08-29 02:35 basic walk - LONG, target-side HIGH

| the bar | stage | why |
|---|---|---|
| 2026-08-29 03:00:00 | ARM | ws4r: ws4r 93.08 oob |
| 2026-08-29 03:00:00 | RIDER | cws4 r 91.34, the highest ex-fence |
| 2026-08-29 03:28:20 | CADENCE | t3 1 of 1 oob HTF lines reversed (ws8), none above ws8 ex-fence [gate on emerging] | rider cws4 51.58, no-longer-exfence yes, reversed yes |
| 2026-08-29 03:28:20 | BATON | ws4 -> ws8, at a cadence, whole board |
| 2026-08-29 04:45:05 | CADENCE | t1 cws1b oob 04:41:00..04:45:00, cws1r reversed 04:44:00 during, stamp 04:44:00 | rider cws8 43.69, no-longer-exfence yes, reversed yes |
| 2026-08-29 04:45:05 | EXHAUST | t4 - rider cws8 43.69, no candidate on the whole board |

verdict EXHAUST at 2026-08-29 04:45:05. his: arm 0300 on ws4r oob, t1 0303, exhaust -> SHORT, then arm 0356 low
