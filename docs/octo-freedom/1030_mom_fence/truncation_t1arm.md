# THE TRUNCATION TEST
# driver docs/octo-freedom/1030_mom_fence/baton_l2_0814.py | arm 2026-08-14 06:59:00 | side low | the bound auto
# every W_V4_* knob comes from this environment, untouched

# the bound was taken from the unbounded run: 2026-08-14 14:07:20

| the read | no end bound | bounded at 2026-08-14 14:07:20 | same? |
|---|---|---|---|
| the verdict, block 1 | EXHAUST 2026-08-14 14:07:20 | EXHAUST 2026-08-14 14:07:20 | YES |
| the verdict, block 2 | EXHAUST 2026-08-14 14:07:20 | EXHAUST 2026-08-14 14:07:20 | YES |
| the verdict, block 3 | EXHAUST 2026-08-14 14:07:20 | EXHAUST 2026-08-14 14:07:20 | YES |
| every row of mode 'ib' | 58 rows | 58 rows | IDENTICAL |
| every row of mode 'reversal' | 58 rows | 58 rows | IDENTICAL |
| every row of mode 'reversal+quarter' | 58 rows | 58 rows | IDENTICAL |

| the read | value |
|---|---|
| THE TEST | PASSES - no decision read past the bound |
