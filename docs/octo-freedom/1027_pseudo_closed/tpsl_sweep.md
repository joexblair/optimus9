# TP x SL x SIGNALLING LINE, TARGETED ON NET, 2026-08-31 00:00:00 .. 2026-09-03 23:59:55
# NET = sum realised - trades x 0.1975%. DRAG is o9-live's figure: 11.0 bps fee +
#   8.75 bps slippage round trip (docs/o9-live-recon/OPEN.md, drag_pct in o9_control).
#   NOT 0.55 (stale, pre-slippage) and NOT 0.29 (not in the repo).
# the slippage half is measured ONCE at 22,000 coins and applied FLAT - the doc says so.
# BREAK-EVEN per trade is 0.1975%, so a TP below that cannot pay at any hit rate.
# first touch is exact; ties go to the SL. both side-map arms. RULED_OK True

## ws15r - 112 reversals in range, 111 legs. TP grid 0.1..5.4, SL grid 0.1..5.4

### arm A: HIGH->SHORT - the 8 best by NET

| TP %% | SL %% | trades | TP hits | SL hits | held to reversal | gross %% | drag %% | NET %% |
|---|---|---|---|---|---|---|---|---|
| 1.5 | 0.1 | 111 | 9 | 95 | 7 | +6.571 | 21.922 | -15.351 |
| 1.4 | 0.1 | 111 | 10 | 95 | 6 | +6.474 | 21.922 | -15.448 |
| 1.6 | 0.1 | 111 | 7 | 95 | 9 | +5.796 | 21.922 | -16.126 |
| 1.3 | 0.1 | 111 | 10 | 95 | 6 | +5.474 | 21.922 | -16.448 |
| 2.1 | 0.1 | 111 | 4 | 96 | 11 | +5.324 | 21.922 | -16.599 |
| 0.7 | 0.1 | 111 | 20 | 89 | 2 | +5.251 | 21.922 | -16.671 |
| 1.1 | 0.1 | 111 | 12 | 95 | 4 | +4.969 | 21.922 | -16.953 |
| 2.0 | 0.1 | 111 | 4 | 96 | 11 | +4.924 | 21.922 | -16.999 |

| ws15r arm A: HIGH->SHORT | value |
|---|---|
| combos | 2916 |
| combos with a POSITIVE net | 0 |
| the best net % | -15.351 at TP 1.5 / SL 0.1 |
| its gross % | +6.571 |
| its drag % | 21.922 |

### arm B: HIGH->LONG - the 8 best by NET

| TP %% | SL %% | trades | TP hits | SL hits | held to reversal | gross %% | drag %% | NET %% |
|---|---|---|---|---|---|---|---|---|
| 1.3 | 5.4 | 111 | 20 | 0 | 91 | +18.116 | 21.922 | -3.807 |
| 1.3 | 5.3 | 111 | 20 | 0 | 91 | +18.116 | 21.922 | -3.807 |
| 1.3 | 5.2 | 111 | 20 | 0 | 91 | +18.116 | 21.922 | -3.807 |
| 1.3 | 5.1 | 111 | 20 | 0 | 91 | +18.116 | 21.922 | -3.807 |
| 1.3 | 5.0 | 111 | 20 | 0 | 91 | +18.116 | 21.922 | -3.807 |
| 1.3 | 4.9 | 111 | 20 | 0 | 91 | +18.116 | 21.922 | -3.807 |
| 1.3 | 4.8 | 111 | 20 | 0 | 91 | +18.116 | 21.922 | -3.807 |
| 1.3 | 4.7 | 111 | 20 | 0 | 91 | +18.116 | 21.922 | -3.807 |

| ws15r arm B: HIGH->LONG | value |
|---|---|
| combos | 2916 |
| combos with a POSITIVE net | 0 |
| the best net % | -3.807 at TP 1.3 / SL 5.4 |
| its gross % | +18.116 |
| its drag % | 21.922 |

## ws10r - 148 reversals in range, 147 legs. TP grid 0.1..4.3, SL grid 0.1..4.3

### arm A: HIGH->SHORT - the 8 best by NET

| TP %% | SL %% | trades | TP hits | SL hits | held to reversal | gross %% | drag %% | NET %% |
|---|---|---|---|---|---|---|---|---|
| 0.8 | 4.3 | 147 | 61 | 0 | 86 | +22.309 | 29.033 | -6.723 |
| 0.8 | 4.2 | 147 | 61 | 0 | 86 | +22.309 | 29.033 | -6.723 |
| 0.8 | 4.1 | 147 | 61 | 0 | 86 | +22.309 | 29.033 | -6.723 |
| 0.8 | 4.0 | 147 | 61 | 0 | 86 | +22.309 | 29.033 | -6.723 |
| 0.8 | 3.9 | 147 | 61 | 0 | 86 | +22.309 | 29.033 | -6.723 |
| 0.8 | 3.8 | 147 | 61 | 0 | 86 | +22.309 | 29.033 | -6.723 |
| 0.8 | 3.7 | 147 | 61 | 0 | 86 | +22.309 | 29.033 | -6.723 |
| 0.8 | 3.6 | 147 | 61 | 0 | 86 | +22.309 | 29.033 | -6.723 |

| ws10r arm A: HIGH->SHORT | value |
|---|---|
| combos | 1849 |
| combos with a POSITIVE net | 0 |
| the best net % | -6.723 at TP 0.8 / SL 4.3 |
| its gross % | +22.309 |
| its drag % | 29.033 |

### arm B: HIGH->LONG - the 8 best by NET

| TP %% | SL %% | trades | TP hits | SL hits | held to reversal | gross %% | drag %% | NET %% |
|---|---|---|---|---|---|---|---|---|
| 0.2 | 4.3 | 147 | 113 | 0 | 34 | +3.598 | 29.033 | -25.435 |
| 0.7 | 0.1 | 147 | 19 | 122 | 6 | +2.352 | 29.033 | -26.680 |
| 0.3 | 4.3 | 147 | 96 | 0 | 51 | +2.315 | 29.033 | -26.717 |
| 0.1 | 4.3 | 147 | 129 | 0 | 18 | +2.103 | 29.033 | -26.930 |
| 0.1 | 4.2 | 147 | 129 | 0 | 18 | +2.103 | 29.033 | -26.930 |
| 0.1 | 4.1 | 147 | 129 | 0 | 18 | +2.103 | 29.033 | -26.930 |
| 0.1 | 4.0 | 147 | 129 | 0 | 18 | +2.103 | 29.033 | -26.930 |
| 0.1 | 3.9 | 147 | 129 | 0 | 18 | +2.103 | 29.033 | -26.930 |

| ws10r arm B: HIGH->LONG | value |
|---|---|
| combos | 1849 |
| combos with a POSITIVE net | 0 |
| the best net % | -25.435 at TP 0.2 / SL 4.3 |
| its gross % | +3.598 |
| its drag % | 29.033 |

## ws30r - 59 reversals in range, 58 legs. TP grid 0.1..5.4, SL grid 0.1..5.4

### arm A: HIGH->SHORT - the 8 best by NET

| TP %% | SL %% | trades | TP hits | SL hits | held to reversal | gross %% | drag %% | NET %% |
|---|---|---|---|---|---|---|---|---|
| 2.0 | 0.1 | 58 | 5 | 51 | 2 | +6.286 | 11.455 | -5.169 |
| 1.6 | 0.1 | 58 | 7 | 50 | 1 | +6.121 | 11.455 | -5.334 |
| 5.3 | 0.1 | 58 | 1 | 53 | 4 | +5.929 | 11.455 | -5.526 |
| 5.2 | 0.1 | 58 | 1 | 53 | 4 | +5.829 | 11.455 | -5.626 |
| 1.9 | 0.1 | 58 | 5 | 51 | 2 | +5.786 | 11.455 | -5.669 |
| 5.1 | 0.1 | 58 | 1 | 53 | 4 | +5.729 | 11.455 | -5.726 |
| 5.0 | 0.1 | 58 | 1 | 53 | 4 | +5.629 | 11.455 | -5.826 |
| 1.8 | 0.1 | 58 | 6 | 51 | 1 | +5.621 | 11.455 | -5.834 |

| ws30r arm A: HIGH->SHORT | value |
|---|---|
| combos | 2916 |
| combos with a POSITIVE net | 0 |
| the best net % | -5.169 at TP 2.0 / SL 0.1 |
| its gross % | +6.286 |
| its drag % | 11.455 |

### arm B: HIGH->LONG - the 8 best by NET

| TP %% | SL %% | trades | TP hits | SL hits | held to reversal | gross %% | drag %% | NET %% |
|---|---|---|---|---|---|---|---|---|
| 1.5 | 0.5 | 58 | 11 | 31 | 16 | +8.529 | 11.455 | -2.926 |
| 1.3 | 0.5 | 58 | 13 | 30 | 15 | +8.438 | 11.455 | -3.017 |
| 4.2 | 0.5 | 58 | 1 | 32 | 25 | +8.336 | 11.455 | -3.119 |
| 1.8 | 0.5 | 58 | 8 | 32 | 18 | +8.292 | 11.455 | -3.163 |
| 4.1 | 0.5 | 58 | 1 | 32 | 25 | +8.236 | 11.455 | -3.219 |
| 3.1 | 0.5 | 58 | 2 | 32 | 24 | +8.205 | 11.455 | -3.250 |
| 5.4 | 0.5 | 58 | 0 | 32 | 26 | +8.145 | 11.455 | -3.310 |
| 5.3 | 0.5 | 58 | 0 | 32 | 26 | +8.145 | 11.455 | -3.310 |

| ws30r arm B: HIGH->LONG | value |
|---|---|
| combos | 2916 |
| combos with a POSITIVE net | 0 |
| the best net % | -2.926 at TP 1.5 / SL 0.5 |
| its gross % | +8.529 |
| its drag % | 11.455 |

## every line and arm, by net

| the line | arm | trades | TP %% | SL %% | gross %% | drag %% | NET %% | positive combos |
|---|---|---|---|---|---|---|---|---|
| ws30r | B: HIGH->LONG | 58 | 1.5 | 0.5 | +8.529 | 11.455 | -2.926 | 0 of 2916 |
| ws15r | B: HIGH->LONG | 111 | 1.3 | 5.4 | +18.116 | 21.922 | -3.807 | 0 of 2916 |
| ws30r | A: HIGH->SHORT | 58 | 2.0 | 0.1 | +6.286 | 11.455 | -5.169 | 0 of 2916 |
| ws10r | A: HIGH->SHORT | 147 | 0.8 | 4.3 | +22.309 | 29.033 | -6.723 | 0 of 1849 |
| ws15r | A: HIGH->SHORT | 111 | 1.5 | 0.1 | +6.571 | 21.922 | -15.351 | 0 of 2916 |
| ws10r | B: HIGH->LONG | 147 | 0.2 | 4.3 | +3.598 | 29.033 | -25.435 | 0 of 1849 |
