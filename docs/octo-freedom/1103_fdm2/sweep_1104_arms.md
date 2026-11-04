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

## sweep_1104_rtrip_94d.md | 27 configs x 94 days
# the control row, config 0 against the banked machine: HOLDS on 4 of 4 banked days
# every number is a sum of that cut's per-day nets over every config holding the arm

| the arm | your 4 days net % | the 4 random days net % | the other 86 days net % | all 94 net % | configs | legs |
|---|---|---|---|---|---|---|
| the r trip (rsi, stoch range, stoch len) (4, 7, 6) | +7.656 | -17.062 | -124.772 | -134.178 | 1 | 893 |
| the r trip (rsi, stoch range, stoch len) (4, 7, 7) | +20.501 | -14.889 | -126.896 | -121.284 | 1 | 755 |
| the r trip (rsi, stoch range, stoch len) (4, 7, 8) | +9.419 | -8.725 | -146.165 | -145.471 | 1 | 647 |
| the r trip (rsi, stoch range, stoch len) (4, 8, 6) | -0.878 | -18.978 | -142.002 | -161.858 | 1 | 963 |
| the r trip (rsi, stoch range, stoch len) (4, 8, 7) | +8.082 | -8.203 | -155.155 | -155.276 | 1 | 816 |
| the r trip (rsi, stoch range, stoch len) (4, 8, 8) | +4.356 | -6.850 | -164.795 | -167.289 | 1 | 694 |
| the r trip (rsi, stoch range, stoch len) (4, 9, 6) | -8.722 | -7.853 | -163.805 | -180.380 | 1 | 1016 |
| the r trip (rsi, stoch range, stoch len) (4, 9, 7) | +18.843 | -2.422 | -200.542 | -184.121 | 1 | 864 |
| the r trip (rsi, stoch range, stoch len) (4, 9, 8) | +14.897 | -11.678 | -191.463 | -188.244 | 1 | 726 |
| the r trip (rsi, stoch range, stoch len) (5, 7, 6) | +3.318 | -19.370 | -165.300 | -181.352 | 1 | 983 |
| the r trip (rsi, stoch range, stoch len) (5, 7, 7) | +6.735 | -5.742 | -173.126 | -172.133 | 1 | 851 |
| the r trip (rsi, stoch range, stoch len) (5, 7, 8) | +1.002 | -6.300 | -160.783 | -166.081 | 1 | 701 |
| the r trip (rsi, stoch range, stoch len) (5, 8, 6) | -4.438 | -5.158 | -190.937 | -200.533 | 1 | 1044 |
| the r trip (rsi, stoch range, stoch len) (5, 8, 7) | +1.664 | -2.009 | -195.376 | -195.721 | 1 | 898 |
| the r trip (rsi, stoch range, stoch len) (5, 8, 8) | +3.023 | +3.384 | -147.610 | -141.203 | 1 | 775 |
| the r trip (rsi, stoch range, stoch len) (5, 9, 6) | -7.898 | +2.414 | -179.214 | -184.698 | 1 | 1071 |
| the r trip (rsi, stoch range, stoch len) (5, 9, 7) | +16.915 | -0.842 | -220.867 | -204.794 | 1 | 928 |
| the r trip (rsi, stoch range, stoch len) (5, 9, 8) | -0.952 | +3.119 | -183.563 | -181.396 | 1 | 817 |
| the r trip (rsi, stoch range, stoch len) (6, 7, 6) | -1.253 | -8.885 | -175.715 | -185.853 | 1 | 991 |
| the r trip (rsi, stoch range, stoch len) (6, 7, 7) | +7.860 | -0.956 | -165.434 | -158.530 | 1 | 903 |
| the r trip (rsi, stoch range, stoch len) (6, 7, 8) | +0.790 | +2.112 | -190.159 | -187.257 | 1 | 776 |
| the r trip (rsi, stoch range, stoch len) (6, 8, 6) | -4.529 | -11.707 | -159.962 | -176.198 | 1 | 1057 |
| the r trip (rsi, stoch range, stoch len) (6, 8, 7) | +17.072 | +6.544 | -177.185 | -153.569 | 1 | 941 |
| the r trip (rsi, stoch range, stoch len) (6, 8, 8) | +1.366 | +7.737 | -196.086 | -186.983 | 1 | 841 |
| the r trip (rsi, stoch range, stoch len) (6, 9, 6) | -0.266 | -4.052 | -175.049 | -179.367 | 1 | 1065 |
| the r trip (rsi, stoch range, stoch len) (6, 9, 7) | +16.850 | +4.944 | -202.924 | -181.130 | 1 | 987 |
| the r trip (rsi, stoch range, stoch len) (6, 9, 8) | -2.694 | -1.539 | -176.766 | -180.999 | 1 | 879 |

## sweep_1104_bmult_94d.md | 5 configs x 94 days
# the control row, config 0 against the banked machine: HOLDS on 4 of 4 banked days
# every number is a sum of that cut's per-day nets over every config holding the arm

| the arm | your 4 days net % | the 4 random days net % | the other 86 days net % | all 94 net % | configs | legs |
|---|---|---|---|---|---|---|
| ws1b's multiplier 0.9 | +6.060 | -2.632 | -168.377 | -164.949 | 1 | 905 |
| ws1b's multiplier 1.0 | +3.930 | -0.820 | -190.939 | -187.829 | 1 | 866 |
| ws1b's multiplier 0.85 | +3.712 | -2.973 | -185.781 | -185.042 | 1 | 905 |
| ws1b's multiplier 0.95 | +1.664 | -2.009 | -195.376 | -195.721 | 1 | 898 |
| ws1b's multiplier 1.05 | +7.907 | -5.639 | -179.559 | -177.291 | 1 | 860 |

## sweep_1104_tfpair_94d.md | 88 configs x 94 days
# the control row, config 0 against the banked machine: HOLDS on 4 of 4 banked days
# every number is a sum of that cut's per-day nets over every config holding the arm

| the arm | your 4 days net % | the 4 random days net % | the other 86 days net % | all 94 net % | configs | legs |
|---|---|---|---|---|---|---|
| TF_PAIR (5, 6) | +117.887 | -13.677 | -2539.381 | -2435.171 | 14 | 14293 |
| TF_PAIR (7, 8) | +52.595 | +195.753 | -1914.260 | -1665.912 | 14 | 12629 |
| TF_PAIR (8, 9) | +124.110 | +84.825 | -1847.922 | -1638.987 | 14 | 12312 |
| TF_PAIR (10, 11) | -6.776 | +83.717 | -2479.753 | -2402.812 | 14 | 10696 |
| TF_PAIR (12, 13) | +90.392 | +24.234 | -1581.752 | -1467.126 | 12 | 8942 |
| TF_PAIR (15, 16) | +2.890 | -41.172 | -994.526 | -1032.808 | 12 | 6932 |
| TF_PAIR (20, 21) | +20.378 | -31.632 | -666.134 | -677.388 | 8 | 3738 |
| FDM_RE_SCAN_FLOOR gate | +221.155 | +188.679 | -6487.366 | -6077.532 | 48 | 37848 |
| FDM_RE_SCAN_FLOOR ws13 | +180.321 | +113.369 | -5536.362 | -5242.672 | 40 | 31694 |
| the scan ceiling 12 | +36.039 | +54.742 | -1010.322 | -919.541 | 8 | 5945 |
| the scan ceiling 18 | +101.561 | +79.816 | -3186.903 | -3005.526 | 24 | 18673 |
| the scan ceiling 24 | +130.910 | +86.072 | -3822.625 | -3605.643 | 28 | 21900 |
| the scan ceiling 30 | +132.966 | +81.418 | -4003.878 | -3789.494 | 28 | 23024 |
| the reversal read live | +271.260 | +205.367 | -6185.761 | -5709.134 | 44 | 39039 |
| the reversal read chart-matched | +130.216 | +96.681 | -5837.967 | -5611.070 | 44 | 30503 |

## sweep_1104_curve_94d.md | 97 configs x 94 days
# the control row, config 0 against the banked machine: HOLDS on 4 of 4 banked days
# every number is a sum of that cut's per-day nets over every config holding the arm

| the arm | your 4 days net % | the 4 random days net % | the other 86 days net % | all 94 net % | configs | legs |
|---|---|---|---|---|---|---|
| KNOB LIFT_PTS | +5.380 | -9.591 | -764.430 | -768.641 | 4 | 3557 |
| KNOB LIFT_TOL | +8.716 | +2.018 | -751.942 | -741.208 | 4 | 3489 |
| KNOB LIFT_WOB | -2.509 | -16.114 | -890.401 | -909.024 | 5 | 4518 |
| KNOB FDM_M3_FNC | +21.981 | -10.374 | -996.679 | -985.072 | 5 | 4452 |
| KNOB FDM_POP_LO | +28.490 | -18.037 | -941.457 | -931.004 | 5 | 4260 |
| KNOB FDM_SAV_ON | -1.612 | -7.633 | -451.669 | -460.914 | 2 | 2167 |
| KNOB FDM_MAE_CAP | +36.659 | -15.893 | -870.123 | -849.357 | 5 | 4452 |
| KNOB FDM_X10_FRM | +10.009 | -4.018 | -387.130 | -381.139 | 2 | 1785 |
| KNOB FDM_X10_WOB | +31.714 | -10.758 | -964.173 | -943.217 | 5 | 4458 |
| KNOB FDM_FNC_2080 | +21.001 | -5.904 | -688.071 | -672.974 | 4 | 3464 |
| KNOB FDM_REV_FROM | -1.015 | -7.261 | -405.394 | -413.670 | 2 | 1863 |
| KNOB FDM_RE_B_FNC | -0.155 | -16.969 | -751.337 | -768.461 | 4 | 3624 |
| KNOB L2_MOM_MAXTF | +9.838 | -14.051 | -590.091 | -594.304 | 3 | 2722 |
| KNOB FDM_RE_IB_XWOB | +6.656 | -8.036 | -781.504 | -782.884 | 4 | 3592 |
| KNOB FDM_RE_WS5_FNC | +29.728 | -21.310 | -1015.996 | -1007.578 | 5 | 5192 |
| KNOB FDM_RE_WIN_OPEN | +5.313 | -22.559 | -892.391 | -909.637 | 5 | 4415 |
| KNOB TRAJ_MIN_TRAVEL | -2.664 | -6.776 | -749.500 | -758.940 | 4 | 3668 |
| KNOB FDM_M3_RESCUE_ON | +0.181 | -2.278 | -364.538 | -366.635 | 2 | 1687 |
| KNOB FDM_RE_WIN_CLOSE | +3.328 | -4.018 | -390.752 | -391.442 | 2 | 1796 |
| KNOB FDM_M3_RESCUE_FNC | +3.967 | +0.433 | -917.001 | -912.601 | 5 | 4468 |
| KNOB FDM_X10_GRACE_MIN | +8.320 | -9.747 | -976.903 | -978.330 | 5 | 4513 |
| KNOB FDM_X10_GRACE_PCT | +22.432 | -6.659 | -988.105 | -972.332 | 5 | 4499 |
| KNOB FDM_X10_TRADE_PCT | +32.865 | -17.263 | -991.184 | -975.582 | 5 | 4286 |
| KNOB FDM_STEP1_ABOVE_TF | -0.393 | -16.683 | -898.143 | -915.219 | 5 | 4640 |
| RUNG 0 | +0.181 | -2.278 | -364.538 | -366.635 | 2 | 1687 |
| RUNG 1 | +11.397 | -18.829 | -1024.375 | -1031.807 | 5 | 4844 |
| RUNG 3 | +4.992 | -6.027 | -586.128 | -587.163 | 3 | 2694 |
| RUNG 4 | -4.099 | -6.881 | -356.375 | -367.355 | 2 | 1800 |
| RUNG 5 | +5.096 | -12.805 | -366.538 | -374.247 | 2 | 1842 |
| RUNG 6 | +1.232 | -11.427 | -577.809 | -588.004 | 3 | 2692 |
| RUNG 8 | +6.762 | -8.409 | -760.519 | -762.166 | 4 | 3580 |
| RUNG 10 | +3.836 | -4.473 | -195.235 | -195.872 | 1 | 865 |
| RUNG 12 | +19.011 | -4.508 | -895.765 | -881.262 | 5 | 4368 |
| RUNG 16 | +1.241 | -3.059 | -159.310 | -161.128 | 1 | 921 |
| RUNG 18 | +4.479 | -2.215 | -204.647 | -202.383 | 1 | 887 |
| RUNG 20 | +6.510 | -6.529 | -204.392 | -204.411 | 1 | 916 |
| RUNG 24 | +1.664 | -2.009 | -195.376 | -195.721 | 1 | 898 |
| RUNG 25 | +1.664 | -5.513 | -190.323 | -194.172 | 1 | 908 |
| RUNG 30 | +1.664 | -2.009 | -195.376 | -195.721 | 1 | 898 |
| RUNG 36 | +0.774 | -2.583 | -189.506 | -191.315 | 1 | 901 |
| RUNG 48 | +11.341 | -3.627 | -180.194 | -172.480 | 1 | 900 |
| RUNG 0.0 | -0.666 | -1.694 | -187.375 | -189.735 | 1 | 917 |
| RUNG 0.5 | -0.666 | -1.694 | -187.375 | -189.735 | 1 | 917 |
| RUNG 0.8 | -3.035 | -13.361 | -180.243 | -196.639 | 1 | 862 |
| RUNG 1.0 | -3.320 | -6.265 | -365.253 | -374.838 | 2 | 1839 |
| RUNG 1.1 | +1.664 | -2.009 | -195.376 | -195.721 | 1 | 898 |
| RUNG 1.5 | +11.497 | -0.441 | -177.760 | -166.704 | 1 | 892 |
| RUNG 2.0 | +13.525 | -2.096 | -547.441 | -536.012 | 3 | 2721 |
| RUNG 2.5 | +1.664 | -1.711 | -197.565 | -197.612 | 1 | 897 |
| RUNG 3.0 | +14.856 | -0.743 | -354.855 | -340.742 | 2 | 1750 |
| RUNG 4.0 | +8.856 | +7.652 | -175.887 | -159.379 | 1 | 813 |
| RUNG 5.0 | +3.328 | -4.018 | -390.752 | -391.442 | 2 | 1796 |
| RUNG 10.0 | +2.997 | -2.775 | -380.338 | -380.116 | 2 | 1814 |
| RUNG 15.0 | +21.755 | -20.746 | -885.399 | -884.390 | 5 | 4239 |
| RUNG 20.0 | +14.173 | -13.700 | -999.304 | -998.831 | 5 | 4488 |
| RUNG 25.0 | +18.980 | -7.610 | -565.509 | -554.139 | 3 | 2843 |
| RUNG 30.0 | +14.210 | -5.094 | -1151.952 | -1142.836 | 6 | 5590 |
| RUNG 35.0 | +9.894 | -3.418 | -608.302 | -601.826 | 3 | 3132 |
| RUNG 40.0 | +5.305 | -5.476 | -583.172 | -583.343 | 3 | 2705 |
| RUNG 45.0 | -0.248 | -2.009 | -187.503 | -189.760 | 1 | 916 |
| RUNG 50.0 | +10.137 | -5.729 | -577.519 | -573.111 | 3 | 2712 |
| RUNG 60.0 | +16.754 | -6.504 | -403.652 | -393.402 | 2 | 1762 |
| RUNG 70.0 | +8.757 | -8.792 | -209.723 | -209.758 | 1 | 829 |
| RUNG 80.0 | +12.433 | -0.211 | -184.586 | -172.364 | 1 | 775 |
| RUNG both | +1.664 | -2.009 | -195.376 | -195.721 | 1 | 898 |
| RUNG ws1b | +0.252 | -9.106 | -384.313 | -393.167 | 2 | 1810 |
| RUNG cross | +1.664 | -2.009 | -195.376 | -195.721 | 1 | 898 |
| RUNG event | +1.664 | -2.009 | -195.376 | -195.721 | 1 | 898 |
| RUNG first | +1.469 | -7.454 | -154.196 | -160.181 | 1 | 833 |
| RUNG window | -2.679 | -5.252 | -210.018 | -217.949 | 1 | 965 |
| RUNG confirm | +8.345 | -2.009 | -191.754 | -185.418 | 1 | 887 |
| RUNG gcws30b | +3.592 | -5.999 | -353.882 | -356.289 | 2 | 1772 |
| RUNG sameside | +1.664 | -2.009 | -195.376 | -195.721 | 1 | 898 |
