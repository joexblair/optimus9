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
| 1 | 2026-08-30 00:00:00 | LONG | 2026-08-30 01:27:55 | t2 | 87.9 | ws5 | 1.8737 | +0.5906 | -1.2780 | 0.1975 | -1.4755 |
| 2 | 2026-08-30 01:28:00 | SHORT | 2026-08-30 05:40:55 | t2 | 252.9 | ws12 | 0.5261 | +2.1507 | +1.1501 | 0.1975 | +0.9526 |
| 3 | 2026-08-30 05:41:00 | LONG | 2026-08-30 07:01:00 | t1 | 80.0 | ws12 | 0.2348 | +1.2000 | +0.9444 | 0.1975 | +0.7469 |
| 4 | 2026-08-30 07:01:05 | SHORT | 2026-08-30 07:44:00 | t1 | 42.9 | ws4 | 0.0103 | +1.5196 | +1.2922 | 0.1975 | +1.0947 |
| 5 | 2026-08-30 07:44:05 | LONG | 2026-08-30 08:28:00 | cws1b counter-oob | 43.9 | ws12 | 0.1414 | +0.4399 | +0.0052 | 0.1975 | -0.1923 |
| 6 | 2026-08-30 08:28:05 | SHORT | 2026-08-30 08:33:00 | t1 | 4.9 | ws12 | 0.1571 | +0.1937 | -0.1571 | 0.1975 | -0.3546 |
| TOTAL 6 legs | | | | | 512.6 | | 2.9434 | +6.0946 | +1.9569 | 1.1850 | +0.7719 |

### the DELTA against 1027_pseudo_closed/legs_blocks.md

| leg | field | banked | this run | match |
|---|---|---|---|---|
| 1 | the open | 2026-08-30 00:00:00 | 2026-08-30 00:00:00 | yes |
| 1 | dir | LONG | LONG | yes |
| 1 | the exit | 2026-08-30 00:20:55 | 2026-08-30 01:27:55 | ** NO ** |
| 1 | ended by | retest | t2 | ** NO ** |
| 1 | MAE % | 0.5193 | 1.8737 | ** NO ** |
| 1 | MFE % | 0.5906 | 0.5906 | yes |
| 1 | realised % | -0.0458 | -1.2780 | ** NO ** |
| 2 | the open | 2026-08-30 00:21:00 | 2026-08-30 01:28:00 | ** NO ** |
| 2 | dir | SHORT | SHORT | yes |
| 2 | the exit | 2026-08-30 02:35:20 | 2026-08-30 05:40:55 | ** NO ** |
| 2 | ended by | barrage | t2 | ** NO ** |
| 2 | MAE % | 0.1172 | 0.5261 | ** NO ** |
| 2 | MFE % | 1.8287 | 2.1507 | ** NO ** |
| 2 | realised % | +1.3703 | +1.1501 | ** NO ** |
| 3 | the open | 2026-08-30 02:35:25 | 2026-08-30 05:41:00 | ** NO ** |
| 3 | dir | LONG | LONG | yes |
| 3 | the exit | 2026-08-30 02:46:55 | 2026-08-30 07:01:00 | ** NO ** |
| 3 | ended by | retest | t1 | ** NO ** |
| 3 | MAE % | 0.1653 | 0.2348 | ** NO ** |
| 3 | MFE % | 0.5061 | 1.2000 | ** NO ** |
| 3 | realised % | +0.1963 | +0.9444 | ** NO ** |
| 4 | the open | 2026-08-30 02:47:00 | 2026-08-30 07:01:05 | ** NO ** |
| 4 | dir | SHORT | SHORT | yes |
| 4 | the exit | 2026-08-30 05:02:00 | 2026-08-30 07:44:00 | ** NO ** |
| 4 | ended by | cws1b counter-oob | t1 | ** NO ** |
| 4 | MAE % | 0.3144 | 0.0103 | ** NO ** |
| 4 | MFE % | 2.2062 | 1.5196 | ** NO ** |
| 4 | realised % | +1.3041 | +1.2922 | ** NO ** |
| 5 | the open | 2026-08-30 05:02:05 | 2026-08-30 07:44:05 | ** NO ** |
| 5 | dir | LONG | LONG | yes |
| 5 | the exit | 2026-08-30 05:11:00 | 2026-08-30 08:28:00 | ** NO ** |
| 5 | ended by | t1 | cws1b counter-oob | ** NO ** |
| 5 | MAE % | 0.0313 | 0.1414 | ** NO ** |
| 5 | MFE % | 0.5066 | 0.4399 | ** NO ** |
| 5 | realised % | +0.1828 | +0.0052 | ** NO ** |
| 6 | the open | 2026-08-30 05:11:05 | 2026-08-30 08:28:05 | ** NO ** |
| 6 | dir | SHORT | SHORT | yes |
| 6 | the exit | 2026-08-30 07:44:00 | 2026-08-30 08:33:00 | ** NO ** |
| 6 | ended by | t1 | t1 | yes |
| 6 | MAE % | 1.1156 | 0.1571 | ** NO ** |
| 6 | MFE % | 0.6725 | 0.1937 | ** NO ** |
| 6 | realised % | +0.4431 | -0.1571 | ** NO ** |

| the read | value |
|---|---|
| fields compared | 42 |
| fields that differ | 33 |
| the verdict | the latch arm is a DIFFERENT mech - a difference here is its effect, not a fault |

## the latch state on 2026-08-30, LOW side

| the line | ex-fence latch-ons | oob latch-ons | ex-fence releases | bars latched ex-fence | bars ex-fence by VALUE | bars latched oob | bars oob by VALUE |
|---|---|---|---|---|---|---|---|
| ws1 | 33 | 31 | 33 | 8533 | 2316 | 7852 | 1788 |
| ws2 | 14 | 10 | 15 | 8983 | 2016 | 6895 | 1104 |
| ws3 | 14 | 13 | 14 | 8439 | 2016 | 6459 | 1404 |
| ws4 | 12 | 11 | 11 | 7736 | 1839 | 6966 | 1171 |
| ws5 | 11 | 10 | 10 | 7890 | 1886 | 6919 | 1145 |
| ws6 | 10 | 9 | 9 | 7929 | 2004 | 6864 | 1205 |
| ws7 | 10 | 8 | 9 | 8628 | 2097 | 7132 | 1338 |
| ws8 | 9 | 8 | 8 | 8602 | 1991 | 6577 | 1122 |
| ws9 | 8 | 8 | 7 | 6684 | 2060 | 6416 | 1235 |
| ws10 | 6 | 5 | 6 | 7359 | 1889 | 6015 | 1033 |
| ws11 | 7 | 7 | 6 | 6404 | 2225 | 6014 | 1168 |
| ws12 | 7 | 6 | 6 | 7717 | 2054 | 5618 | 1200 |

## the latch state on 2026-08-30, HIGH side

| the line | ex-fence latch-ons | oob latch-ons | ex-fence releases | bars latched ex-fence | bars ex-fence by VALUE | bars latched oob | bars oob by VALUE |
|---|---|---|---|---|---|---|---|
| ws1 | 32 | 27 | 32 | 8088 | 1872 | 6732 | 1248 |
| ws2 | 13 | 11 | 13 | 8031 | 1488 | 6399 | 720 |
| ws3 | 13 | 10 | 14 | 8478 | 1836 | 7491 | 1080 |
| ws4 | 11 | 9 | 11 | 9214 | 1435 | 7454 | 777 |
| ws5 | 10 | 9 | 10 | 9359 | 1309 | 7282 | 666 |
| ws6 | 8 | 5 | 8 | 7919 | 1114 | 4006 | 481 |
| ws7 | 7 | 5 | 7 | 6514 | 1077 | 4133 | 500 |
| ws8 | 6 | 5 | 6 | 6278 | 1017 | 4401 | 401 |
| ws9 | 5 | 4 | 5 | 8141 | 955 | 6877 | 357 |
| ws10 | 4 | 3 | 4 | 7384 | 941 | 5551 | 350 |
| ws11 | 3 | 3 | 3 | 8339 | 1259 | 7610 | 574 |
| ws12 | 4 | 4 | 4 | 7567 | 1284 | 7044 | 716 |

