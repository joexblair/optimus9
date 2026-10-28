# THE PSEUDO-CLOSED LINE vs THE PRODUCT'S CLOSED READ, 2026-08-30 00:00:00 .. 2026-09-06 23:59:55
# pseudo-closed: ws{T}r computed on the bar sequence ENDING AT t - t, t-T, t-2T, ...
#   so the value at t is the closed value of a ws{T} grid phased to close at t.
# the chain is the product's own: SMA(Stoch(RSI(close,5),8),7), BARS 120 of history.
# RULED_OK True

## TEST 1 - on the bars where the midnight grid closes, it must EQUAL the closed read

| the line | grid-close bars in range | max abs diff | median abs diff | bars over 0.01 |
|---|---|---|---|---|
| ws13r | 887 | 18.356132 | 0.000032 | 254 |
| ws14r | 823 | 13.454018 | 0.000044 | 237 |
| ws15r | 767 | 0.000000 | 0.000000 | 0 |
| ws16r | 719 | 0.000000 | 0.000000 | 0 |

## TEST 2 - the EX-FENCE state, which is what he said the mech needs

| the line | side | bars ex-fence CLOSED | bars ex-fence PSEUDO | bars ex-fence EMERGING | pseudo agrees with closed | emerging agrees with closed |
|---|---|---|---|---|---|---|
| ws13r | LOW | 16152 | 15662 | 16012 | 91.3% | 92.2% |
| ws13r | HIGH | 13848 | 13078 | 13722 | 93.6% | 94.8% |
| ws14r | LOW | 18408 | 16490 | 19067 | 91.0% | 93.3% |
| ws14r | HIGH | 13752 | 12493 | 14850 | 94.7% | 94.0% |
| ws15r | LOW | 16020 | 16616 | 16189 | 91.1% | 92.8% |
| ws15r | HIGH | 10440 | 12315 | 11347 | 95.0% | 95.7% |
| ws16r | LOW | 15744 | 17504 | 16645 | 92.2% | 94.0% |
| ws16r | HIGH | 10944 | 12205 | 12694 | 95.0% | 95.0% |

## TEST 3 - the bar warmup doubled, 120 -> 240

| the line | max abs change | share of bars that move |
|---|---|---|
| ws13r | 9.69e-09 | 8.8057% |
| ws14r | 1.04e-08 | 9.2672% |
| ws15r | 8.94e-09 | 9.7620% |
| ws16r | 1.15e-08 | 9.5153% |
