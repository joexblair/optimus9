# the main chain — handover

**Status, Joe 1016:** *"still benched for now"*. This doc exists so it can be picked up where it
was left, per his earlier instruction: *"main-chain needs the same attention as octo2. we'll need
to be able to pick it up where we left off. same verbatim spec notes"*.

**It is a DIFFERENT machine from `octo2`.** `octo2` does not import it and does not reproduce it.
Joe 1016: *"when it's further developed, we'll need to integrate the main-chain machine"* — that
integration has not happened and is benched.

**Joe's name for it is `octo-freedom`** — the arm / race / ws1mage-rev walk that emits
`WALK FIRES FROM`. It has been running on o9-live + fakeAPI since 1002, shape B.

---

## 1. THE CHAIN, as the README states it

| stage | what it says |
|---|---|
| coil | says the coil let go. The combined coil ticks down, first time after the arm |
| momTF bucket | says the lines stopped pushing. 3 timeframes at ws7 or above drop out |
| mom-xfer flat-runs | confirms it. 1 flat-run start from ws4 or above, inside a trailing 4 min |
| ws1mage-rev | the last gate. A rev cross in the last 240 s whose confirmation bar has passed |
| rule#1 | decides whether it is tradeable. ws1r and (ws2r or ws3r) outside 27/73 on the dr side, inside the last 5 min, backward only |
| **WALK FIRES FROM** | the signal. The first bar all of the above hold at once |
| trade_walk | closes it. Three exits racing — an opposing signal, the dr flip, or the stop |

---

## 2. THE FILES

| file | owns |
|---|---|
| `1005_scoring/machine.py` | `build()`, `chain()`, the six declared legs, the frozen reference |
| `1005_scoring/_chain10.py` | the walk — the arm, the loop, the baton, the lineage, last-mile, the mom-true masks |
| `1005_scoring/_restart.py` | the chain restart, Joe 1013 |
| `1005_scoring/_htfgate.py` | the HTF gate — what a higher-timeframe oob line permits to open |
| `1005_scoring/_ibmech.py` | the ws1cp-ib mech — `cps`, `ib_bar`, `_mode1` |
| `1005_scoring/_momtrue.py` | the cached mom-true masks, `momo_g` (strip OFF), Joe 1009 |
| `1005_scoring/1013_report.py` | **THE ONE REPORT.** One build, every table |

**To run it:** `python3 1013_report.py` from `docs/octo-freedom/1005_scoring`. The tape is
cwd-sensitive — score39 resolves a shorter tape from elsewhere, so run it from that directory and
check the printed bar count.

---

## 3. THE LIVE KNOB VALUES, read off the files 1016

| knob | value | where |
|---|---|---|
| `LOOP_TF` / `W_LOOP_END` | ws10 / `oob` | `_chain10.py:308` |
| `W_LOOP_LB` | 48 bars = 4 min | `_chain10.py:310` |
| `W_ARM` | `cp` | `_chain10.py:431` |
| `W_KICK` | `off` | `_chain10.py:105` |
| `LIN_HOP` | from `SC.LG['lin_hop']` | `_chain10.py:64` |
| `LIN_LASTMILE_KCKSTRT_TFCAP` | ws7 | `_chain10.py:451`. Joe: *"let's fix the cap at 7"* |
| `LIN_LASTMILE_MAX_GAP` | 24 bars | `_chain10.py:496` |
| `LINFIN_WALK_DELAy` | 12 bars | `_chain10.py:497` |
| `LINFIN_WALK_AWAY_MIN` | 2 | `_chain10.py:498` |
| `W_MAE_STOP` | 1.1 | `_chain10.py:548` |
| `W_BATON` | `oob` | `_chain10.py:568` |
| `W_PASS` | `oob` | `_chain10.py:589`. Joe's tag ruling |
| `W_CP_DWELL` / `W_CP_XWOB` / `W_CP_MODE` | 4 / 2 / `both` | `_chain10.py:323, 358, 333` |
| `W_GC` / `W_GC_HOLD` | on / `wait` | `_chain10.py:278, 279` |
| `W_STALL_N` | from `SC.LG['stall_n']` | `_chain10.py:396` |
| `W_RESTART` | on | `_restart.py:35` |
| `W_RESTART_MAGE_DWELL` | 24 bars, STRICTLY greater | `_restart.py:33` |
| `W_RESTART_AWAY_TFS` | ws1, ws2, ws3 | `_restart.py:34` |
| `W_HTF_GATE` | on | `_htfgate.py:41` |
| `W_HTF_TFS` | ws30, ws45, ws60, ws90 | `_htfgate.py:36` |
| `W_HTF_X_TF` / `W_HTF_IB_TF` | ws60 / ws30 | `_htfgate.py:37, 38` |
| `W_HTF_X_WOB` | 48 bars = 4.0 min | `_htfgate.py:39`. Joe: *"a 48 wob"* |
| `W_HTF_REN_WOB` | 0 bars = no hold | `_htfgate.py:40` |

---

## 4. THE FROZEN REFERENCE — the gate that stops the number drifting

Six declared legs in `machine.TRADES`, checked against `machine.FROZEN` every run.
`FROZEN_TOTAL = (9.5071, 10.6667)`, `TOL = 0.0002` — the 4-decimal printing precision, not a
tolerance on the mech.

| leg | opens | closes | dr | frozen (close, end) |
|---|---|---|---|---|
| 07-17 21:58 LONG | 2026-07-17 21:58:00 | 2026-07-18 01:15:20 | −1 | 1.1199, 1.3945 |
| 07-18 02:31 SHORT | 2026-07-18 02:31:00 | 2026-07-18 06:34:30 | +1 | 5.2666, 4.9508 |
| 07-18 08:46 LONG | 2026-07-18 08:46:55 | 2026-07-18 10:07:10 | −1 | 0.3929, 0.4014 |
| 07-18 16:07 LONG | 2026-07-18 16:11:10 | 2026-07-18 16:38:00 | −1 | 0.7967, 1.9325 |
| 07-18 18:12 SHORT | 2026-07-18 18:12:00 | 2026-07-18 18:44:35 | +1 | 0.4362, 0.4083 |
| 07-18 18:45 LONG | 2026-07-18 18:45:15 | 2026-07-18 20:05:40 | −1 | 1.4948, 1.5793 |

**The re-freezes are Joe's calls, each taken with the cost on the table:**
- 1013 *"re-freeze the reference and add both trades, for 10.2784%"* — added legs 5 and 6, the
  07-18 chain's own links
- 1013 *"bank, commit and push, make this machine live"* — `W_IB_DWELL` 2 moved four of the six
  close events
- 1013 *"bank, commit and push. update docs. make this machine live"* — the loop work moved two,
  both gained
- 1013 *"let's fix the cap at 7"* — two trades moved and **both got worse**, total +10.2783 →
  +10.2069. His call, with the cost stated

---

## 5. WHAT WAS OPEN WHEN IT WAS BENCHED

| # | item | state |
|---|---|---|
| 1 | **the 18:12 join is broken** | the 16:07 leg's walk now ends 18:10:05, so leg 5 opens 18:12:00 — 1.9 min after leg 4 ends. FLAGGED in `machine.py`, Joe's to rule |
| 1b | **`machine.py`'s own re-freeze comments are stale** | found 1016. The six `FROZEN` end values sum to **10.6668** and `FROZEN_TOTAL` says **10.6667**, so the dict is self-consistent. But the comment above it records the cap-at-7 re-freeze as ending at **+10.2069**, and an earlier one at **+10.2783**. The numbers in the comments no longer describe the numbers in the dict. NOT FIXED — it is a record of Joe's calls and the correction is his. The gate itself is sound; only its narrative has drifted |
| 2 | the ws1cp rebuild | which under-cross to take so `cp2` can be called. Joe's |
| 3 | the 10-hour GPU sweep | HELD by Joe |
| 4 | `W_EXPERIMENT` discipline | an off-ruled run is not the machine. `_ruled.check` prints the verdict as `_chain10`'s first lines; report the ruled run beside it or not at all |
| 5 | the `POI` items | mom-xfer on Mage excursions; octo-sigs back into the walk. Joe: *"not just yet"* |

---

## 6. HOW IT RELATES TO `octo2`

`octo2` reuses `machine.SC` (the tape and the lines) and `_chain10.RL` / `_chain10.BANK` (the r
lines and the momo banks) and **nothing else**. It does not call `machine.chain`, `_restart`,
`_htfgate` or `_ibmech`. The two machines share data and no logic.

Integrating them is Joe's call and is benched: *"still benched for now"*.
