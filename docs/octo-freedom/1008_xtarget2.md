# 1008 — #61's COMBINED [Mage, b, boundary] TARGET, 48 ARMS, AND THE ENTRY WALK RE-RUN

Joe 1008: *"run #61. I see you were exapanding to multi TFs - thats a good call and should be
included in the sweep"* / *"queue it"*.

Drivers: `_xtarget2.py` (48 arms + control), `_fullwindow.py` (the entry walk, 4 arms).
Both on the banked knob key ws12_baton_config.v1, 95 days, LG_TAPE_END=2026-10-05.

# #61 — THE COMBINED [Mage, b, boundary] TARGET. 48 arms of 48 returned, control YES

## THE CONTROL — the banked B build, re-run inside this sweep

| block | expected NET | measured NET | legs expected | legs measured | verdict |
|---|---|---|---|---|---|
| fit | +0.7511 | +0.7511 | 779 | 779 | MATCH |
| hold | +4.0801 | +4.0801 | 844 | 844 | MATCH |
| all | +4.8312 | +4.8312 | 1623 | 1623 | MATCH |

## EVERY ARM, RANKED ON THE FIT HALF ALONE — the hold block chooses nothing

| rank on fit | combine | target TFs | in-fence | what `boundary` is | legs | stops | **fit NET** | hold NET | all-95 NET | MFE/MAE | x-cross exits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **ALL** | the SAME TF — #61's own | on | the counter-side ex-fence (17 / 83) | 1535 | 185 | **+3.4312** | -12.2813 | -8.8501 | 1.0330 | 599 |
| 2 | **ALL** | h+1 AND h+2 | on | the counter-side ex-fence (17 / 83) | 1531 | 184 | **+2.9548** | -5.8822 | -2.9274 | 1.0347 | 586 |
| 3 | **ALL** | h+1 only | on | the counter-side ex-fence (17 / 83) | 1533 | 185 | **+0.0800** | -8.2936 | -8.2136 | 1.0335 | 595 |
| 4 | **ALL** | the SAME TF — #61's own | OFF | the counter-side ex-fence (17 / 83) | 1542 | 188 | **-0.0517** | -0.5535 | -0.6052 | 1.0398 | 638 |
| 5 | **ALL** | h+1 only | OFF | the counter-side ex-fence (17 / 83) | 1542 | 188 | **-0.1442** | -0.5535 | -0.6977 | 1.0397 | 638 |
| 6 | **ALL** | h+1 AND h+2 | OFF | the counter-side ex-fence (17 / 83) | 1542 | 188 | **-0.4570** | -0.6817 | -1.1387 | 1.0392 | 636 |
| 7 | **ALL** | the SAME TF — #61's own | on | the counter-side oob (15 / 85) | 1529 | 184 | **-2.0838** | -5.1673 | -7.2511 | 1.0343 | 591 |
| 8 | **ALL** | h+1 AND h+2 | on | the counter-side oob (15 / 85) | 1525 | 183 | **-2.3903** | +1.2614 | -1.1289 | 1.0363 | 578 |
| 9 | **ALL** | h+1 only | on | the counter-side oob (15 / 85) | 1527 | 184 | **-5.3427** | -1.1773 | -6.5200 | 1.0350 | 587 |
| 10 | **ALL** | h+1 only | OFF | the counter-side oob (15 / 85) | 1536 | 187 | **-5.6877** | +5.5788 | -0.1089 | 1.0405 | 630 |
| 11 | **ALL** | the SAME TF — #61's own | OFF | the counter-side oob (15 / 85) | 1536 | 187 | **-5.6877** | +5.5788 | -0.1089 | 1.0405 | 630 |
| 12 | **ALL** | h+1 AND h+2 | OFF | the counter-side oob (15 / 85) | 1536 | 187 | **-5.9229** | +5.4507 | -0.4722 | 1.0401 | 628 |
| 13 | **ALL** | h+1 only | on | the dr-side ex-fence (83 / 17) | 1594 | 203 | **-6.3817** | -47.9388 | -54.3205 | 0.9531 | 806 |
| 14 | **ALL** | h+1 only | on | the dr-side oob (85 / 15) | 1594 | 203 | **-6.3817** | -47.9388 | -54.3205 | 0.9531 | 806 |
| 15 | **ANY** | h+1 only | on | the counter-side ex-fence (17 / 83) | 1610 | 202 | **-8.1605** | -35.9061 | -44.0666 | 0.9523 | 844 |
| 16 | **ANY** | h+1 only | on | the counter-side oob (15 / 85) | 1610 | 202 | **-8.1605** | -35.9362 | -44.0967 | 0.9523 | 844 |
| 17 | **ALL** | h+1 AND h+2 | on | the dr-side ex-fence (83 / 17) | 1584 | 203 | **-8.2878** | -49.1266 | -57.4144 | 0.9558 | 773 |
| 18 | **ALL** | h+1 AND h+2 | on | the dr-side oob (85 / 15) | 1584 | 203 | **-8.2878** | -49.1266 | -57.4144 | 0.9558 | 773 |
| 19 | **ALL** | h+1 only | OFF | the dr-side oob (85 / 15) | 1612 | 199 | **-8.5516** | -0.1672 | -8.7188 | 0.9633 | 942 |
| 20 | **ANY** | h+1 only | OFF | the counter-side ex-fence (17 / 83) | 1631 | 203 | **-8.8863** | +9.3217 | +0.4354 | 0.9334 | 1014 |
| 21 | **ANY** | h+1 only | OFF | the counter-side oob (15 / 85) | 1631 | 203 | **-8.8863** | +9.2916 | +0.4053 | 0.9334 | 1014 |
| 22 | **ANY** | h+1 AND h+2 | OFF | the counter-side ex-fence (17 / 83) | 1637 | 202 | **-9.0709** | +16.3017 | +7.2308 | 0.9352 | 1025 |
| 23 | **ANY** | h+1 AND h+2 | OFF | the counter-side oob (15 / 85) | 1637 | 202 | **-9.0709** | +16.2716 | +7.2007 | 0.9351 | 1025 |
| 24 | **ALL** | h+1 only | OFF | the dr-side ex-fence (83 / 17) | 1610 | 199 | **-9.6207** | -10.3564 | -19.9771 | 0.9562 | 939 |
| 25 | **ANY** | h+1 AND h+2 | on | the counter-side ex-fence (17 / 83) | 1607 | 201 | **-11.3992** | -35.0525 | -46.4517 | 0.9485 | 836 |
| 26 | **ANY** | h+1 AND h+2 | on | the counter-side oob (15 / 85) | 1607 | 201 | **-11.3992** | -35.0826 | -46.4818 | 0.9485 | 836 |
| 27 | **ALL** | the SAME TF — #61's own | on | the dr-side ex-fence (83 / 17) | 1602 | 205 | **-13.1736** | -49.6067 | -62.7803 | 0.9463 | 821 |
| 28 | **ALL** | the SAME TF — #61's own | on | the dr-side oob (85 / 15) | 1602 | 205 | **-13.1736** | -49.6067 | -62.7803 | 0.9463 | 821 |
| 29 | **ALL** | the SAME TF — #61's own | OFF | the dr-side oob (85 / 15) | 1620 | 200 | **-13.7843** | +6.7228 | -7.0615 | 0.9603 | 968 |
| 30 | **ALL** | h+1 AND h+2 | OFF | the dr-side oob (85 / 15) | 1602 | 202 | **-14.0566** | -4.3979 | -18.4545 | 0.9647 | 910 |
| 31 | **ALL** | the SAME TF — #61's own | OFF | the dr-side ex-fence (83 / 17) | 1618 | 200 | **-14.6007** | -3.2301 | -17.8308 | 0.9537 | 962 |
| 32 | **ANY** | the SAME TF — #61's own | on | the counter-side ex-fence (17 / 83) | 1605 | 204 | **-14.7705** | -39.7073 | -54.4778 | 0.9435 | 847 |
| 33 | **ANY** | the SAME TF — #61's own | on | the counter-side oob (15 / 85) | 1605 | 204 | **-14.7705** | -39.8701 | -54.6406 | 0.9434 | 847 |
| 34 | **ALL** | h+1 AND h+2 | OFF | the dr-side ex-fence (83 / 17) | 1600 | 202 | **-14.9624** | -13.9123 | -28.8747 | 0.9582 | 908 |
| 35 | **ANY** | the SAME TF — #61's own | OFF | the counter-side ex-fence (17 / 83) | 1629 | 204 | **-17.8668** | +10.5111 | -7.3557 | 0.9240 | 1039 |
| 36 | **ANY** | the SAME TF — #61's own | OFF | the counter-side oob (15 / 85) | 1629 | 204 | **-17.8668** | +10.3483 | -7.5185 | 0.9239 | 1039 |
| 37 | **ANY** | h+1 only | on | the dr-side ex-fence (83 / 17) | 1659 | 211 | **-48.0388** | -1.7211 | -49.7599 | 0.8998 | 985 |
| 38 | **ANY** | h+1 AND h+2 | OFF | the dr-side ex-fence (83 / 17) | 1675 | 212 | **-49.2348** | +41.3190 | -7.9158 | 0.8813 | 1148 |
| 39 | **ANY** | h+1 only | OFF | the dr-side ex-fence (83 / 17) | 1675 | 212 | **-49.5014** | +39.6253 | -9.8761 | 0.8810 | 1147 |
| 40 | **ANY** | h+1 only | on | the dr-side oob (85 / 15) | 1661 | 213 | **-50.6431** | -1.3019 | -51.9450 | 0.8949 | 993 |
| 41 | **ANY** | h+1 only | OFF | the dr-side oob (85 / 15) | 1677 | 214 | **-51.1392** | +37.2940 | -13.8452 | 0.8757 | 1154 |
| 42 | **ANY** | h+1 AND h+2 | on | the dr-side ex-fence (83 / 17) | 1650 | 211 | **-51.5848** | -5.8194 | -57.4042 | 0.8941 | 965 |
| 43 | **ANY** | h+1 AND h+2 | OFF | the dr-side oob (85 / 15) | 1677 | 214 | **-51.7398** | +38.9877 | -12.7521 | 0.8756 | 1155 |
| 44 | **ANY** | the SAME TF — #61's own | on | the dr-side ex-fence (83 / 17) | 1654 | 213 | **-51.8383** | -11.1615 | -62.9998 | 0.8948 | 971 |
| 45 | **ANY** | the SAME TF — #61's own | on | the dr-side oob (85 / 15) | 1656 | 214 | **-52.8294** | -8.1728 | -61.0022 | 0.8932 | 976 |
| 46 | **ANY** | the SAME TF — #61's own | OFF | the dr-side ex-fence (83 / 17) | 1675 | 212 | **-52.9987** | +35.5810 | -17.4177 | 0.8756 | 1162 |
| 47 | **ANY** | the SAME TF — #61's own | OFF | the dr-side oob (85 / 15) | 1677 | 214 | **-54.5386** | +35.7841 | -18.7545 | 0.8724 | 1165 |
| 48 | **ANY** | h+1 AND h+2 | on | the dr-side oob (85 / 15) | 1652 | 213 | **-54.7222** | -5.5367 | -60.2589 | 0.8889 | 973 |

## #61's OWN OPEN QUESTION — ALL of the set, or ANY one of it

| the combine rule | arms | mean fit NET | mean hold NET | best fit NET | best hold NET |
|---|---|---|---|---|---|
| all | 24 | -6.3569 | -13.9752 | +3.4312 | +6.7228 |
| any | 24 | -31.6299 | +1.8904 | -8.1605 | +41.3190 |

## THE TF OFFSET — Joe 1008 ratified the multi-TF expansion

| the target TFs | arms | mean fit NET | mean hold NET | best fit NET | best hold NET |
|---|---|---|---|---|---|
| both | 16 | -18.7270 | -5.3141 | +2.9548 | +41.3190 |
| next | 16 | -17.2154 | -5.6362 | +0.0800 | +39.6253 |
| self | 16 | -21.0377 | -7.1770 | +3.4312 | +35.7841 |

## WHAT `boundary` IS — four readings, none picked

| the reading | arms | mean fit NET | mean hold NET | best fit NET | best hold NET |
|---|---|---|---|---|---|
| exf_ctr | 12 | -5.3618 | -8.5648 | +3.4312 | +16.3017 |
| exf_dr | 12 | -30.8520 | -6.3623 | -6.3817 | +41.3190 |
| oob_ctr | 12 | -8.1058 | -5.2877 | -2.0838 | +16.2716 |
| oob_dr | 12 | -31.6540 | -3.9550 | -6.3817 | +38.9877 |

## THE IN-FENCE TEST ON THE LINE TARGETS

| in-fence | arms | mean fit NET | mean hold NET | best fit NET | best hold NET |
|---|---|---|---|---|---|
| 0 | 24 | -19.7637 | +12.0882 | -0.0517 | +41.3190 |
| 1 | 24 | -18.2231 | -24.1730 | +3.4312 | +1.2614 |

## WHAT THIS SWEEP SAYS

| the question | the answer |
|---|---|
| the fit-half winner | **ALL / the SAME TF — #61's own / in-fence on / the counter-side ex-fence (17 / 83)** at fit +3.4312, hold -12.2813, all -8.8501 |
| it ranks this on hold | **35 of 48** |
| does the fit ranking transfer | Spearman fit vs hold **-0.232** across 48 arms |
| arms positive on BOTH halves | **none** |
| the banked B build, for reference | fit +0.7511, hold +4.0801, all +4.8312, MFE/MAE 0.9527 |
| arms beating banked B on all-95 NET | **2 of 48** |
| arms beating banked B on BOTH halves | **0 of 48** |
