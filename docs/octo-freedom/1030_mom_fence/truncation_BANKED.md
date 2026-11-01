# THE TRUNCATION TEST
# driver docs/octo-freedom/1030_mom_fence/baton_l2_0814.py | arm 2026-08-14 06:59:00 | side low | the bound 2026-08-14 14:18:00
# every W_V4_* knob comes from this environment, untouched

| the read | no end bound | bounded at 2026-08-14 14:18:00 | same? |
|---|---|---|---|
| the verdict, block 1 | EXHAUST 2026-08-14 14:18:00 | EXHAUST 2026-08-14 14:18:00 | YES |
| the verdict, block 2 | EXHAUST 2026-08-14 14:18:00 | EXHAUST 2026-08-14 14:18:00 | YES |
| the verdict, block 3 | EXHAUST 2026-08-14 14:18:00 | EXHAUST 2026-08-14 14:18:00 | YES |
| every row of mode 'ib' | 42 rows | 42 rows | IDENTICAL |
| every row of mode 'reversal' | 44 rows | 44 rows | IDENTICAL |
| every row of mode 'reversal+quarter' | 44 rows | 44 rows | IDENTICAL |

| the read | value |
|---|---|
| THE TEST | PASSES - no decision read past the bound |
