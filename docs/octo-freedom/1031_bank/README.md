# 1031 - THE MACHINE, BANKED

BANKED 2026-11-01. Joe: *"bank everything we've walked on and make this config the machine"*.

The ruled check passes with no environment overrides. Every figure below was measured on this
config, and the walk it is validated on carries a passing truncation test.

## the validated walk

| the read | value |
|---|---|
| the arm | 2026-08-14 06:59:00, handed in, side low |
| the verdict, all three pass modes | EXHAUST |
| the verdict bar | 2026-08-14 14:07:20 |
| minutes from the arm | 428.3 |
| rows in the trace, each mode | 58 |
| the truncation test, bound taken from the run | PASSES - every verdict and every row identical |
| t1 cadences acting before their own cross confirm | 0 |

His word on the bar: *"1407 is as good as 1418, and it adds validation of the 2 updates"*.

## what moved into the bank

| the knob | was | now | whose |
|---|---|---|---|
| RMOM_FNC | 80.0 | 75.0 -> (25.0, 75.0) | his 1030 |
| L2_MOM_MAXTF | 12 | 30 | his 1031 |
| LIN2_CAD_TYPES | 'all' | 't1' | his 1031 |
| LIN2_EXFNC_LATCH_REL | 'bank' | 'lift' | his 1031 spec revision |
| LIN2_RELATCH_ON | 0 | 1 | his 1031 |
| LIN2_RIDER_JUMP | 0 | 8 | his 1031 |
| LIN2_TOP_RESET_ON | 0 | 1 | his 1031 |
| LIN2_CASCADE_NO_ACTION | 1 | 0 | his 1031 |
| LIN2_COUNTER_OOB_ON | 1 | 0 | his 1030 |
| LIN2_T1_B_LINE | ws1b | gcws30b | his 1031 |
| LIN2_T1_B_WOB | - | 6 bars = 30 s | his 1031 |
| LIN2_T1_R_FNC | side-of-50 | 56.0 -> (44.0, 56.0) | his 1031 |
| LIN2_T1_GRACE_AT | - | 'cross' | his 1031 choice |
| LIN2_ARM_B_LINE | ws1b | gcws30b | his 1031 |
| LIN2_ARM_B_FNC | - | 95.0 -> (5.0, 95.0) | his 1031 |
| LIN2_ARM_B_WOB | - | 6 bars = 30 s | his 1031 |
| LIN2_ARM_WS3R_ON | - | 0 | his uncertainty |
| the arm's r group | ws1b AND ws1r | gcws30b AND (ws1r OR ws2r) | his 1031 revision |
| the t1 fire bar | max(cross bar, reversal stamp) | max(cross CONFIRM, reversal stamp) | his 1031 |

## two defects fixed in banked code

| the defect | what it was | how it was found |
|---|---|---|
| `v4_l2_proxy._releases` | passed its own cache key tuple where the SIDE belongs, so the banked latch-release arm raised TypeError on every call and had never been run | running the banked arm for the first time |
| `v4_l2_cadence.t1` | fired on the ws1b ib CROSS bar while its own filter and its own comment both used the wob-12 CONFIRM bar. 16 of 17 t1 cadences on the 0659 walk acted 25 to 55 s before their qualifying hold completed | the truncation test |

His ruling on the second: *"option 1 - the wob has earnt a place in the mech.  its true value will
be swept in the future"*.

## the arm update, validated against his own five rows

| his open | side | HIS arm | the arm fires, ws1r carrying it | the gap |
|---|---|---|---|---|
| 2026-09-03 17:01:00 | LONG | 2026-09-03 17:16:00 | 2026-09-03 17:17:25 | +1.4 min |
| 2026-09-03 19:30:00 | SHORT | 2026-09-03 22:01:00 | 2026-09-03 22:01:15 | +0.2 min |
| 2026-09-03 23:24:00 | LONG | 2026-09-03 23:39:00 | 2026-09-03 23:30:00 | -9.0 min |
| 2026-09-03 23:43:00 | SHORT | 2026-09-04 00:07:00 | 2026-09-04 00:07:30 | +0.5 min |
| 2026-09-04 00:09:00 | LONG | 2026-09-04 00:36:00 | 2026-09-04 00:36:40 | +0.7 min |

| the read | value |
|---|---|
| inside his +-5 min estimate | 4 of 5 |
| ws2r oob at any of the five firing bars | none. His word: *"the ws2r only fired onced inside of 09-03 and 09-04, so its absence here is understood"* |
| the 23:39 row | his own note: *"I missed that ws1r oob at 2330"* |
| nothing fitted to his times | the terms are his words only |

## the t1 update, validated against his own two examples

| his example | the bar | ws1r there | the fence | qualifies? | he said |
|---|---|---|---|---|---|
| r 50.3 | 2026-09-03 11:52:00 | 50.34 | >= 56.0 high, <= 44.0 low | no | no |
| r 59 | 2026-09-03 12:33:00 | 57.71 | >= 56.0 high, <= 44.0 low | YES high side | YES |

## what the new t1 costs in cadence count, 2026-09-03 and 09-04

| the arm | low side | high side |
|---|---|---|
| pre-1031 - ws1b wob 12, r past 50 | 43 | 49 |
| banked - gcws30b wob 6, r past 56, grace on the cross bar | 102 | 95 |

His reading: *"the additional cadences (and also the additional arms) will help us improve the
chain's net% purely by picking up opportunities that were overlooked by having ws1b in the arm
mech"*.

## the mage cascade, disabled

| who owned the exit, over 143 legs | legs | legs negative | summed net % |
|---|---|---|---|
| mage-cascade OPPOSES | 123 | 61 | -17.8102 |
| DIV REV-TRADE | 13 | 1 | +7.6393 |
| EXHAUST | 2 | 0 | +7.8977 |
| the board review | 3 | 2 | -0.4565 |

It ended all 5 of the 0659 variants at their first cadence. His word: *"completely disable the mage
cascade"*. Its verdict is still PRINTED in every cadence row, as data.

## two tools deployed, his instruction

| the tool | what it catches |
|---|---|
| `docs/octo-freedom/his_words.md` + `.claude/hooks/his-words.py` | a *"..."* quote attributed to him that is not in the registry. An unregistered quote is MINE until he confirms it |
| `docs/octo-freedom/1022_v4/v4_truncation_test.py` | a decision that reads past the bar it is taken on. It found the t1 defect above. Pass `auto` for the bound and it takes the verdict bar from the run, so a stale bar cannot produce a vacuous pass |

## still his, carried forward

| # | the item |
|---|---|
| 1 | names for the ladder-top reset trick and for the seven knobs that carry my names |
| 2 | no limit on ladder-top resets - his *"yes"*, recorded as his |
| 3 | the opposite-side ex-fence clear - HELD, *"I haven't given up on barrage yet"*. Mine, unattributed, alive only in the 'barrage' release arm |
| 4 | the three pass modes stay as arms. LIN2_PASS is banked at 'ib' and none of the three is ruled |
| 5 | every t1 figure measured before 1031 carries the cross-bar lookahead. He relies on them all - *"that's the only causal option"* - so they need re-running |
