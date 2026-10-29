# THE LATCH ARM: THE oob/EX-FENCE CONSISTENCY AND THE RIDER IT PICKS
# 2026-08-30, 17280 bars. LIN2_LATCH_EXFNC_ON 1 | LIN2_EXFNC_LATCH_WOB 4 bars | RULED_OK False

## 1 - REMOVED. There is no oob latch - his 1029 correction. Every oob
      read in the walk is the line value.

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

