# THE LATCH ARM: THE oob/EX-FENCE CONSISTENCY AND THE RIDER IT PICKS
# 2026-08-30, 17280 bars. LIN2_LATCH_EXFNC_ON 1 | LIN2_EXFNC_LATCH_WOB 4 bars | RULED_OK False

## 1 - bars where the oob latch is ON and the ex-fence latch is OFF

| the line | side | oob-latched and NOT ex-fence-latched | as % of the 17280 bars |
|---|---|---|---|
| ws1 | LOW | 1332 | 7.7% |
| ws2 | LOW | 1128 | 6.5% |
| ws3 | LOW | 848 | 4.9% |
| ws4 | LOW | 889 | 5.1% |
| ws5 | LOW | 1039 | 6.0% |
| ws6 | LOW | 3090 | 17.9% |
| ws7 | LOW | 2212 | 12.8% |
| ws8 | LOW | 1780 | 10.3% |
| ws9 | LOW | 1072 | 6.2% |
| ws10 | LOW | 641 | 3.7% |
| ws11 | LOW | 711 | 4.1% |
| ws12 | LOW | 356 | 2.1% |
| ws1 | HIGH | 624 | 3.6% |
| ws2 | HIGH | 2040 | 11.8% |
| ws3 | HIGH | 1944 | 11.2% |
| ws4 | HIGH | 702 | 4.1% |
| ws5 | HIGH | 929 | 5.4% |
| ws6 | HIGH | 785 | 4.5% |
| ws7 | HIGH | 1370 | 7.9% |
| ws8 | HIGH | 1860 | 10.8% |
| ws9 | HIGH | 206 | 1.2% |
| ws10 | HIGH | 991 | 5.7% |
| ws11 | HIGH | 155 | 0.9% |
| ws12 | HIGH | 756 | 4.4% |

| the read | value |
|---|---|
| summed inconsistent bars over 24 line-sides | 27460 |
| the same state read off the VALUES | 0 - oob is a subset of ex-fence by construction |

## 2 - the rider the scan returns at every bar, by read

### LIN2_LATCH_EXFNC_ON 0 - the banked read, LOW side

| the rider the scan returns | bars | % of the 17280 bars |
|---|---|---|
| none - no ex-fence line | 7101 | 41.1% |
| ws1 | 1349 | 7.8% |
| ws2 | 1003 | 5.8% |
| ws3 | 502 | 2.9% |
| ws4 | 468 | 2.7% |
| ws5 | 565 | 3.3% |
| ws6 | 580 | 3.4% |
| ws7 | 661 | 3.8% |
| ws8 | 676 | 3.9% |
| ws9 | 736 | 4.3% |
| ws10 | 639 | 3.7% |
| ws11 | 946 | 5.5% |
| ws12 | 2054 | 11.9% |

### LIN2_LATCH_EXFNC_ON 1 - the latch read, LOW side

| the rider the scan returns | bars | % of the 17280 bars |
|---|---|---|
| none - no ex-fence line | 763 | 4.4% |
| ws1 | 116 | 0.7% |
| ws2 | 2117 | 12.3% |
| ws3 | 1276 | 7.4% |
| ws4 | 350 | 2.0% |
| ws5 | 324 | 1.9% |
| ws6 | 308 | 1.8% |
| ws7 | 591 | 3.4% |
| ws8 | 2057 | 11.9% |
| ws9 | 520 | 3.0% |
| ws10 | 510 | 3.0% |
| ws11 | 631 | 3.7% |
| ws12 | 7717 | 44.7% |

