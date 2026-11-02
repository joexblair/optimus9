# 2026-09-03 04:37:55 | leg 2 SHORT, low side | rider ws12 | the banked wob 4 bars = 20 s
# the fence is (25.0, 75.0) | oob is 15.0/85.0 | the jump cap at a ws12 rider is ws20

| the wob | bars = s | the candidates in ws13..ws20 | ws12 latched? | ws12 no-longer-exfence? | ws12 reversed? | ws12 oob by value? | HOLD declines? | THE BRANCH |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 bars = 5 s | ws13, ws14, ws15, ws16, ws17 | YES | no | no | YES | no | BATON -> ws17 |
| 2 | 2 bars = 10 s | ws13, ws14, ws15, ws16, ws17 | YES | no | no | YES | no | BATON -> ws17 |
| 4 | 4 bars = 20 s | ws13, ws14, ws15, ws16, ws17 | YES | no | no | YES | no | BATON -> ws17 |
| 6 | 6 bars = 30 s | ws13, ws14, ws15, ws16, ws17 | YES | no | no | YES | no | BATON -> ws17 |
| 8 | 8 bars = 40 s | ws13, ws14, ws15, ws16, ws17 | YES | no | no | YES | no | BATON -> ws17 |
| 12 | 12 bars = 60 s | ws13, ws14, ws15, ws16, ws17 | YES | no | no | YES | no | BATON -> ws17 |
| 18 | 18 bars = 90 s | ws13, ws14, ws15, ws16, ws17 | YES | no | no | YES | no | BATON -> ws17 |
| 24 | 24 bars = 120 s | ws13, ws14, ws15, ws16, ws17 | YES | no | no | YES | no | BATON -> ws17 |
| 36 | 36 bars = 180 s | ws13, ws14, ws15, ws16, ws17 | YES | no | no | YES | no | BATON -> ws17 |
| 48 | 48 bars = 240 s | ws13, ws14, ws15, ws16, ws17 | YES | no | no | YES | no | BATON -> ws17 |
| 60 | 60 bars = 300 s | ws14, ws15, ws16, ws17 | YES | no | no | YES | no | BATON -> ws17 |
| 90 | 90 bars = 450 s | ws15 | YES | no | no | YES | no | BATON -> ws15 |
| 120 | 120 bars = 600 s | NONE | YES | no | no | YES | no | HOLD |
| 180 | 180 bars = 900 s | NONE | YES | no | no | YES | no | HOLD |
| 240 | 240 bars = 1200 s | NONE | YES | no | no | YES | no | HOLD |
| 360 | 360 bars = 1800 s | NONE | no | YES | no | YES | no | HOLD |
| 480 | 480 bars = 2400 s | NONE | no | YES | no | YES | no | HOLD |

| the read | value |
|---|---|
| ws12 r value at the bar | 13.56 |
| the low oob fence | 15.0 |
| so ws12 is oob by value | YES, by 1.44 points |
| LIN2_LATCH_OOB_ON | 0 - at 0 the baton oob read IS the line value, not the latch |
| the wob the knob is restored to | 4 |
