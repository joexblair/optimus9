# STEP 1 OF THE NET%% SWEEP: LIN2_BARRAGE_MIN_TF, both MIN_TF_MODE arms
# WINDOW 2026-08-30 00:00:00 .. 2026-09-06 23:59:55 | TAPE 1632960 bars | RULED_OK True
# HELD AT BANK: LIN2_BARRAGE_MAX_TF 15, LINES 6, TOL 70s, FIT 'off', LIN2_PSEUDO_MIN_TF 4, LIN2_LATCH_EXFNC_ON 0
# DRAG 0.1975% per round trip, its own column and its own total.
# net %% = summed realised %% minus summed drag. Every leg scored, no cap, no horizon.

## the control row - the banked config over 2026-08-30 alone

| the read | expected | this run | match |
|---|---|---|---|
| legs | 6 | 21 | ** NO ** |
| net % | +2.2658 | -0.7203 | ** NO ** |

** THE CONTROL FAILED. Every row below is suspect. **

## the grid, ordered by MIN_TF then mode

| min_tf | mode | legs | barrage exits | MAE %% | MFE %% | realised %% | drag %% | net %% | net %% per leg | legs net-positive |
|---|---|---|---|---|---|---|---|---|---|---|
