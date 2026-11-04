# the 1104 arm tables, one block per finished grid
# his ask: "re-print the [each arm] table at the end of the sweep for comparison"

## sweep_1104_knobs.md | 48 configs x 8 days
# the control row, config 0 against the banked machine: HOLDS on 4 of 4 banked days
# every number is a sum of that cut's per-day nets over every config holding the arm

| the arm | your 4 days net % | the 4 random days net % | all 8 net % | configs | legs |
|---|---|---|---|---|---|
| the ws6r gate oob | +193.229 | +18.859 | +212.088 | 24 | 2394 |
| the ws6r gate at 20/80 | +188.005 | -34.291 | +153.714 | 24 | 2430 |
| the reversal read live | +278.118 | +73.220 | +351.338 | 24 | 2576 |
| the reversal read chart-matched | +103.116 | -88.652 | +14.464 | 24 | 2248 |
| ws5r's fence 15/85 | +74.024 | -19.090 | +54.934 | 16 | 1388 |
| ws5r's fence 20/80 | +133.674 | +12.937 | +146.611 | 16 | 1636 |
| ws5r's fence 25/75 | +173.536 | -9.279 | +164.257 | 16 | 1800 |
| the scan ceiling 12 | +193.074 | +7.228 | +200.302 | 24 | 2366 |
| the scan ceiling 30 | +188.160 | -22.660 | +165.500 | 24 | 2458 |
| the ib close out of the set | +191.761 | -7.403 | +184.358 | 24 | 2412 |
| the ib close in the set | +189.473 | -8.029 | +181.444 | 24 | 2412 |

## sweep_1104_knobs_94d.md | 48 configs x 94 days
# the control row, config 0 against the banked machine: HOLDS on 4 of 4 banked days
# every number is a sum of that cut's per-day nets over every config holding the arm

| the arm | your 4 days net % | the 4 random days net % | the other 86 days net % | all 94 net % | configs | legs |
|---|---|---|---|---|---|---|
| the ws6r gate oob | +193.229 | +18.859 | -4264.573 | -4052.485 | 24 | 23806 |
| the ws6r gate at 20/80 | +188.005 | -34.291 | -4169.873 | -4016.159 | 24 | 23838 |
| the reversal read live | +278.118 | +73.220 | -3933.917 | -3582.579 | 24 | 26122 |
| the reversal read chart-matched | +103.116 | -88.652 | -4500.529 | -4486.065 | 24 | 21522 |
| ws5r's fence 15/85 | +74.024 | -19.090 | -2352.234 | -2297.300 | 16 | 12812 |
| ws5r's fence 20/80 | +133.674 | +12.937 | -2942.869 | -2796.258 | 16 | 16178 |
| ws5r's fence 25/75 | +173.536 | -9.279 | -3139.343 | -2975.086 | 16 | 18654 |
| the scan ceiling 12 | +193.074 | +7.228 | -4062.839 | -3862.537 | 24 | 23282 |
| the scan ceiling 30 | +188.160 | -22.660 | -4371.607 | -4206.107 | 24 | 24362 |
| the ib close out of the set | +191.761 | -7.403 | -4367.741 | -4183.383 | 24 | 23844 |
| the ib close in the set | +189.473 | -8.029 | -4066.705 | -3885.261 | 24 | 23800 |
