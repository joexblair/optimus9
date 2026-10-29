# THE PER-LINE EX-FENCE LATCH - the regression, the ceiling, and the latch delta
# TAPE 1632960 bars | LG_TAPE_END 2026-10-05 | RULED_OK False
# KNOBS: LIN2_LATCH_EXFNC_ON 1 | LIN2_EXFNC_LATCH_WOB 4 bars = 20 s | LIN2_BARRAGE_MAX_TF 15 | L2_MOM_MAXTF 12
# PSEUDO BAND ws4..ws15. ws13 and ws14 pseudo are NOT bit-exact to the closed read (1440/13 = 110.77, 1440/14 = 102.86).
# BARRAGE: MIN_TF 9, LINES 6, TOL 70s, MODE 'membership', FIT 'off'

## the barrage ceiling, 2026-08-30 00:00:00 .. 2026-09-06 23:59:55

| max_tf | side | cadences | first | last |
|---|---|---|---|---|
| 12 | HIGH | 11 | 2026-08-31 14:32:40 | 2026-09-06 18:14:10 |
| 12 | LOW | 13 | 2026-08-30 02:35:20 | 2026-09-05 23:40:10 |
| 15 | HIGH | 17 | 2026-08-30 16:19:30 | 2026-09-06 18:14:10 |
| 15 | LOW | 19 | 2026-08-30 02:35:20 | 2026-09-05 23:40:10 |
| 12 | BOTH | 24 | | |
| 15 | BOTH | 36 | | |

| the read | value |
|---|---|
| cadences at max_tf 12 | 24 |
| cadences at max_tf 15 | 36 |
| kept by both | 24 |
| added by 15 | 12 |
| dropped by 15 | 0 |

| the bars max_tf 15 adds | |
|---|---|
| 2026-08-30 16:19:30 | |
| 2026-08-30 23:49:30 | |
| 2026-08-31 07:29:25 | |
| 2026-08-31 13:44:00 | |
| 2026-09-01 03:18:35 | |
| 2026-09-01 23:26:10 | |
| 2026-09-02 15:45:35 | |
| 2026-09-03 23:25:00 | |
| 2026-09-05 00:27:50 | |
| 2026-09-05 10:17:45 | |
| 2026-09-05 11:20:35 | |
| 2026-09-05 13:54:50 | |

## the 6 legs on 2026-08-30

### LIN2_LATCH_EXFNC_ON 1 - the latch arm

| leg | the open | dir | the exit | ended by | held min | the rider chain | MAE % | MFE % | realised % | drag % | net % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026-08-30 00:00:00 | LONG | 2026-08-30 01:00:00 | cws1b counter-oob | 60.0 | ws5 | 0.7026 | +0.5906 | -0.5754 | 0.1975 | -0.7729 |
| 2 | 2026-08-30 01:00:05 | SHORT | 2026-08-30 02:35:20 | barrage | 95.2 | ws2 | 0.0717 | +1.3059 | +0.8450 | 0.1975 | +0.6475 |
| 3 | 2026-08-30 02:35:25 | LONG | 2026-08-30 02:46:55 | t2 | 11.5 | ws6 | 0.1653 | +0.5061 | +0.1963 | 0.1975 | -0.0012 |
| 4 | 2026-08-30 02:47:00 | SHORT | 2026-08-30 05:02:00 | cws1b counter-oob | 135.0 | ws12 | 0.3144 | +2.2062 | +1.3041 | 0.1975 | +1.1066 |
| 5 | 2026-08-30 05:02:05 | LONG | 2026-08-30 05:11:00 | t1 | 8.9 | ws7 > ws8 | 0.0313 | +0.5066 | +0.1828 | 0.1975 | -0.0147 |
| 6 | 2026-08-30 05:11:05 | SHORT | 2026-08-30 07:44:00 | t1 | 152.9 | ws4 | 1.1156 | +0.6725 | +0.4431 | 0.1975 | +0.2456 |
| TOTAL 6 legs | | | | | 463.6 | | 2.4010 | +5.7880 | +2.3959 | 1.1850 | +1.2109 |

### the DELTA against 1027_pseudo_closed/legs_blocks.md

| leg | field | banked | this run | match |
|---|---|---|---|---|
| 1 | the open | 2026-08-30 00:00:00 | 2026-08-30 00:00:00 | yes |
| 1 | dir | LONG | LONG | yes |
| 1 | the exit | 2026-08-30 00:20:55 | 2026-08-30 01:00:00 | ** NO ** |
| 1 | ended by | retest | cws1b counter-oob | ** NO ** |
| 1 | MAE % | 0.5193 | 0.7026 | ** NO ** |
| 1 | MFE % | 0.5906 | 0.5906 | yes |
| 1 | realised % | -0.0458 | -0.5754 | ** NO ** |
| 2 | the open | 2026-08-30 00:21:00 | 2026-08-30 01:00:05 | ** NO ** |
| 2 | dir | SHORT | SHORT | yes |
| 2 | the exit | 2026-08-30 02:35:20 | 2026-08-30 02:35:20 | yes |
| 2 | ended by | barrage | barrage | yes |
| 2 | MAE % | 0.1172 | 0.0717 | ** NO ** |
| 2 | MFE % | 1.8287 | 1.3059 | ** NO ** |
| 2 | realised % | +1.3703 | +0.8450 | ** NO ** |
| 3 | the open | 2026-08-30 02:35:25 | 2026-08-30 02:35:25 | yes |
| 3 | dir | LONG | LONG | yes |
| 3 | the exit | 2026-08-30 02:46:55 | 2026-08-30 02:46:55 | yes |
| 3 | ended by | retest | t2 | ** NO ** |
| 3 | MAE % | 0.1653 | 0.1653 | yes |
| 3 | MFE % | 0.5061 | 0.5061 | yes |
| 3 | realised % | +0.1963 | +0.1963 | yes |
| 4 | the open | 2026-08-30 02:47:00 | 2026-08-30 02:47:00 | yes |
| 4 | dir | SHORT | SHORT | yes |
| 4 | the exit | 2026-08-30 05:02:00 | 2026-08-30 05:02:00 | yes |
| 4 | ended by | cws1b counter-oob | cws1b counter-oob | yes |
| 4 | MAE % | 0.3144 | 0.3144 | yes |
| 4 | MFE % | 2.2062 | 2.2062 | yes |
| 4 | realised % | +1.3041 | +1.3041 | yes |
| 5 | the open | 2026-08-30 05:02:05 | 2026-08-30 05:02:05 | yes |
| 5 | dir | LONG | LONG | yes |
| 5 | the exit | 2026-08-30 05:11:00 | 2026-08-30 05:11:00 | yes |
| 5 | ended by | t1 | t1 | yes |
| 5 | MAE % | 0.0313 | 0.0313 | yes |
| 5 | MFE % | 0.5066 | 0.5066 | yes |
| 5 | realised % | +0.1828 | +0.1828 | yes |
| 6 | the open | 2026-08-30 05:11:05 | 2026-08-30 05:11:05 | yes |
| 6 | dir | SHORT | SHORT | yes |
| 6 | the exit | 2026-08-30 07:44:00 | 2026-08-30 07:44:00 | yes |
| 6 | ended by | t1 | t1 | yes |
| 6 | MAE % | 1.1156 | 1.1156 | yes |
| 6 | MFE % | 0.6725 | 0.6725 | yes |
| 6 | realised % | +0.4431 | +0.4431 | yes |

| the read | value |
|---|---|
| fields compared | 42 |
| fields that differ | 9 |
| the verdict | the latch arm is a DIFFERENT mech - a difference here is its effect, not a fault |

## the latch state on 2026-08-30, LOW side

| the line | ex-fence latch-ons | oob latch-ons | ex-fence releases | bars latched ex-fence | bars ex-fence by VALUE | bars latched oob | bars oob by VALUE |
|---|---|---|---|---|---|---|---|
