# 1030 — THE MOM FENCE AT 25/75, THE LADDER AT ws20

Joe 1030: *"the next thing I need is an understanding of the 20/80 mom fence. make the fence
75/25, and increase the TF from 12 to 20"*.

## the two knobs his words name

| the knob | at the bank | his 1030 value | where it is declared | his words that set the bank |
|---|---|---|---|---|
| `RMOM_FNC` | 80.0 → the pair (20.0, 80.0) | 75.0 → (25.0, 75.0) | `v4_knobs.py:50` | *"v4_rmom_fnc, default 80"*; and 1025, asked whether v4mom_fnc is the same knob: *"yes"* |
| `L2_MOM_MAXTF` | 12 | 20 | `v4_knobs.py:317` | *"v4mom_maxTF = 12"* — 1025, the lineage2 fork |

- both are in `RULED`, so a run at his values refuses unless `W_V4_EXPERIMENT=1`
- the r lines are already on disk to ws30r, so the ladder top has lines to read
- `fence_pop.py` / `fence_pop.md` measure the fence at both settings. Neither knob is moved by it.

## NOTHING IS BUILT YET — the concretions his two values do not settle

| # | the concretion | whose |
|---|---|---|
| 1 | `L2_MOM_MAXTF` is the ceiling in EIGHT consumers, not one: the whole-board candidate range, the rider scan cap, the cascade ladder (`v4_lineage2.py:254` and `:281`), `v4_reentry`'s top rung, lin2-reentry's `>ws5` band, the t3 rider range, `v4_l2_cadence.py:741`'s HTF range, and the barrage's `off` fit pool. `v4_knobs.py:378-380` records that the barrage was given its OWN ceiling (`LIN2_BARRAGE_MAX_TF` 15) specifically so `L2_MOM_MAXTF` could stay 12. Does 20 move all eight, or only the fence test? | HIS |
| 2 | the absolute line-count knobs were all measured on a 12-line ladder — `MC_MIN` 4 (the cascade floor), `LIN2_CHAIN_OPEN_LINES` 2, `LIN2_BARRAGE_LINES` 6. At a 20-line ladder "at least 4 beyond the fence" on the LOW side goes from 14.79% of bars to 36.09%. Do they stay absolute, or move with the ladder? | HIS |
| 3 | `MC_TF_HI` 12 is the mage cascade's OWN ceiling and sits in `CASCADE_RULED`, a separate refusal. Does it follow to 20? | HIS |
| 4 | the Mage ladder is hard-coded `range(1, 13)` in roughly twenty drivers and does NOT read the knob, so raising `L2_MOM_MAXTF` alone leaves the board without ws13Mage..ws20Mage. Driving the loaders off the knob is one source for one fact — MINE, and behaviour-preserving while the knob is 12. | MINE |
| 5 | context, not a question: his 1017 band names make ws13..ws20 **dtf**, and `v4_l2_cadence.py:325` states dtf lines are not on the lineage2 board. At 20 they are. | — |
