# THE ws5rbackstop NET, RE-SCORED. Joe 1024, his option 3.
# the trades, the entries and the exit rule are IDENTICAL. Only the MFE window differs.
#   banked        -> the next favourable 2.0% pivot after the entry (825 pivots)
#   sweep-pivots  -> the end of the sweep-pivots leg. PICK 'lowest_pct', BAND 0.000, CONTAIN off,
#                    XWOB 18, TFs = his six plus ws1Mage and ws2Mage
# THE EXIT IS JOE 1022: a stopped trade at -1.100%, a positive at 90% of its MFE, read
#   in BAR ORDER. The 90%% leg is NOT causal - a SCORED net, not a tradeable one.
# the oob filter is OFF - Joe 1023, *"the oob filter can't be applied to a reversal test"*.
# the triple is (rsi, stc, k_len). RULED_OK True. DRAG IS ITS OWN COLUMN.

| the read | value |
|---|---|
| configs in the sweep | 27 |
| run here | 12 |
| SKIPPED, the line cache is gone from .rpl_cache/lines | 15 |
| skipped | (5, 7, 5) |
| skipped | (5, 8, 5) |
| skipped | (5, 9, 5) |
| skipped | (6, 7, 5) |
| skipped | (6, 8, 5) |
| skipped | (6, 9, 5) |
| skipped | (7, 7, 5) |
| skipped | (7, 7, 6) |
| skipped | (7, 7, 7) |
| skipped | (7, 8, 5) |
| skipped | (7, 8, 6) |
| skipped | (7, 8, 7) |
| skipped | (7, 9, 5) |
| skipped | (7, 9, 6) |
| skipped | (7, 9, 7) |

| rsi | stc | k_len | the MFE window | trades | stopped | stop rate | gross %% | gross per trade %% | median MFE %% | drag at 0.1975 %% | NET at 0.1975 %% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 7 | 6 | banked 2% pivot | 622 | 178 | 28.6% | +697.98 | +1.1221 | +1.733 | 122.84 | +575.13 |
| 5 | 7 | 6 | sweep-pivots | 621 | 107 | 17.2% | +497.01 | +0.8003 | +0.922 | 122.65 | +374.36 |
| 5 | 7 | 7 | banked 2% pivot | 365 | 113 | 31.0% | +359.81 | +0.9858 | +1.688 | 72.09 | +287.72 |
| 5 | 7 | 7 | sweep-pivots | 365 | 66 | 18.1% | +258.18 | +0.7073 | +0.941 | 72.09 | +186.09 |
| 5 | 8 | 6 | banked 2% pivot | 606 | 176 | 29.0% | +666.23 | +1.0994 | +1.698 | 119.69 | +546.55 |
| 5 | 8 | 6 | sweep-pivots | 606 | 113 | 18.6% | +491.47 | +0.8110 | +0.940 | 119.69 | +371.78 |
| 5 | 8 | 7 <- DB row | banked 2% pivot | 387 | 112 | 28.9% | +397.56 | +1.0273 | +1.573 | 76.43 | +321.13 |
| 5 | 8 | 7 <- DB row | sweep-pivots | 387 | 69 | 17.8% | +317.17 | +0.8196 | +0.913 | 76.43 | +240.74 |
| 5 | 9 | 6 | banked 2% pivot | 568 | 159 | 28.0% | +660.98 | +1.1637 | +1.689 | 112.18 | +548.80 |
| 5 | 9 | 6 | sweep-pivots | 568 | 113 | 19.9% | +479.68 | +0.8445 | +0.996 | 112.18 | +367.50 |
| 5 | 9 | 7 | banked 2% pivot | 387 | 108 | 27.9% | +420.49 | +1.0865 | +1.550 | 76.43 | +344.06 |
| 5 | 9 | 7 | sweep-pivots | 387 | 73 | 18.9% | +302.84 | +0.7825 | +0.868 | 76.43 | +226.41 |
| 6 | 7 | 6 | banked 2% pivot | 669 | 189 | 28.3% | +738.08 | +1.1033 | +1.688 | 132.13 | +605.95 |
| 6 | 7 | 6 | sweep-pivots | 669 | 123 | 18.4% | +534.10 | +0.7984 | +0.919 | 132.13 | +401.98 |
| 6 | 7 | 7 | banked 2% pivot | 401 | 119 | 29.7% | +403.03 | +1.0051 | +1.578 | 79.20 | +323.83 |
| 6 | 7 | 7 | sweep-pivots | 401 | 74 | 18.5% | +301.22 | +0.7512 | +0.894 | 79.20 | +222.02 |
| 6 | 8 | 6 <- BANK | banked 2% pivot | 628 | 175 | 27.9% | +726.32 | +1.1566 | +1.691 | 124.03 | +602.29 |
| 6 | 8 | 6 <- BANK | sweep-pivots | 628 | 124 | 19.7% | +532.20 | +0.8475 | +1.009 | 124.03 | +408.17 |
| 6 | 8 | 7 | banked 2% pivot | 401 | 109 | 27.2% | +457.20 | +1.1401 | +1.679 | 79.20 | +378.00 |
| 6 | 8 | 7 | sweep-pivots | 401 | 70 | 17.5% | +337.81 | +0.8424 | +0.875 | 79.20 | +258.61 |
| 6 | 9 | 6 | banked 2% pivot | 594 | 173 | 29.1% | +646.41 | +1.0882 | +1.686 | 117.32 | +529.09 |
| 6 | 9 | 6 | sweep-pivots | 594 | 115 | 19.4% | +501.43 | +0.8442 | +1.010 | 117.32 | +384.12 |
| 6 | 9 | 7 | banked 2% pivot | 409 | 120 | 29.3% | +429.24 | +1.0495 | +1.676 | 80.78 | +348.46 |
| 6 | 9 | 7 | sweep-pivots | 409 | 87 | 21.3% | +308.95 | +0.7554 | +0.956 | 80.78 | +228.18 |
# took 111 s
