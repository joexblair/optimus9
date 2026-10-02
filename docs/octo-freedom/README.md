# docs/octo-freedom — where this machine's reports live

`octo-freedom` is Joe's name for the validated machine: the arm / turn / qualify / race /
ws1mage-rev walk that emits **`WALK FIRES FROM`**. Named 1001: *"octo-freedom / it's now, it's the
goal, and it's got a little bit of chinese numerology sneaked in the back pocket"*.

## REPORTS GO HERE, AS FILES IN THIS REPO

Joe 1001: *"guide it to store reports locally. create a docs/octo-freedom/"*.

A report written anywhere else is not a report. **Not** in a Claude Docs page, not in a chat message,
not in a scratch directory. The reason is the one this machine was built to answer: a number that
cannot be re-derived from the repo is a written record, not a checkable result. Three things have
already been lost or nearly lost to that this session:

| what | how |
|---|---|
| the `all_wsf_flatrun_grid` `_bars` columns | 20 columns held values; NOTHING in the repo populated them. An authorised overwrite deleted the only copy |
| `wsf_trade_config` v4's `walk_dr_*` rows | written by an ad-hoc insert, not by `seed()`. A clean DB would not have had them |
| the 09-01 MAE/MFE figures | produced by a scratch `mae.py` that no longer exists. The numbers survive only as prose in `NOTES_momtf_mechdev.md` |

## NAMING

    docs/octo-freedom/MMDD_<what-it-is>.md

`MMDD` is the day the work was done, so the directory sorts chronologically. One file per report.
Append to an existing file when the work continues the same thread; start a new one when the subject
changes.

## WHAT A REPORT MUST CARRY

| element | why |
|---|---|
| the command that produced every number, verbatim | so the next reader re-runs it rather than trusting it |
| the knobs in force, with their source | a config version, a file:line, or "hardcoded at X" — never just the value |
| the tape it ran on | `TAPE_END` and the bar range. The tape is a FIXED 94.5-day width anchored on its END, so the end implies the start |
| what was NOT measured | the absence is the finding more often than the presence |
| file:line for every claim about code | a claim about code that cites no line is an opinion |

**No evaluative adjectives on results.** Flat numbers. A bug fix is not a win.

## THE REPORTS, INDEXED

One job per report. Where two reports touch the same question, the later one says which it builds on;
the rulings themselves live in `docs/o9-live-recon/OPEN.md`, not here.

| report | its one job | builds on / builds into |
|---|---|---|
| `1001_handover_to_next_session.md` | the strategy-side handover prompt and its open list | → `1001_open_items.md` |
| `1001_recon_validation.md` + `1001_recon_validation/` | the o9-live recon session's validation of the port: 12 checks, 37 mutations, the causality verdict, the stale-doc list | `docs/o9-live-recon/CAUSALITY.md`'s 1001 audit (same verdict, re-derived) |
| `1001_open_items.md` | what was open on 1001, read from the handover; a dated snapshot | ← the handover; its items are now ruled in `OPEN.md` |
| `1001_dr_convergence.md` | how long each state-carrier (`rig.DR`, `rig.DRW`, `ArmState`) runs before it resets | → `1001_warmup.md` |
| `1001_warmup.md` | the minimum live window: 72.47 h = 63.04 h line convergence + 9.43 h arm reach-back | ← `1001_dr_convergence.md`; → `1001_rebuild_timing.md` |
| `1001_rebuild_timing.md` + `1001_rebuild_timing/` | what a 104 h rebuild costs per bar: lines 1.27-1.45 s, walk + rule#1 79 s; shapes A/B/C | ← `1001_warmup.md`; → shape B, `1002_live_producer.md` |
| `1001_rewalk_on_ruled_dr.md` | 09-01 re-walked on the ruled dr series; the `octo-sig` label | ← `NOTES_momtf_mechdev.md:447` |
| `1002_live_producer.md` + `1002_live_producer/` | the live producer: what was built, the regression, the 09-01 replay, the start | ← every report above |
| `1002_bybit_api_check.md` | o9-live, fakeAPI and the data feeds against Bybit's current V5 docs: inventory, improvements, what could not be verified | → `MVP2.md` item 2 (L1); `docs/second_ws_spec.md` (M1) |
| `chat/` | the inter-session chat log and its tool | - |

## WHAT LIVES WHERE

| file | holds |
|---|---|
| `docs/octo-freedom/` | reports on this machine, newest work appended or added as a new dated file |
| `docs/o9-live-recon/` | the o9-live + fakeAPI handover package, including the startup prompt a new session reads |
| `docs/22_go_20260921/NOTES_momtf_mechdev.md` | the day-by-day record of how the machine was built, Joe's rulings quoted verbatim |
| `report_leash_walk.py` | the acceptance test. 9 validated bars plus the day's shape, exits 1 on either moving |
| `tests/test_arm_state.py`, `tests/test_leash_walk.py` | 12 property checks (14 since Q5 landed) |
| `tests/test_trade_walk.py`, `tests/test_octo_loop.py` | the trade book's stepper (T1-T5) and the live decide layer (L1-L6), 1002 |
| `optimus9/live/octo_inputs.py`, `octo_freedom.py`, `octo_loop.py` | the live producer, shape B, 1002 |
| `optimus9/live/trade_signal_dump.py`, `feed_errors.py` | the trade-signal dump and the errors log, 1002 |
| `o9live_trade_signal_dump.log`, `o9live_errors.log`, `o9live_octo.log` | o9-live's dump, errors log and run log, repo root (gitignored as `*.log`) |

## THE MACHINE, IN ONE TABLE

| mech | how it contributes |
|---|---|
| dr latch | sets the direction. ws1Mage + ws13m both past 85 or both past 15 — **oob**, no wob. Joe 1001: *"my view of dr is ws1Mage + ws13m oob"* |
| arm | opens the window. ws5Mage holds past 75 or 25 on the dr side for 6 bars = 30 s. Cancels on a 50-cross. Its dr must match the signal's |
| coil | says the coil let go. The combined coil ticks down, first time after the arm |
| momTF bucket | says the lines stopped pushing. 3 timeframes at ws7 or above drop out |
| mom-xfer flat-runs | confirms it. 1 flat-run start from ws4 or above, inside a trailing 4 min |
| ws1mage-rev | the last gate. A rev cross in the last 240 s whose confirmation bar has passed |
| rule#1 | decides whether it is tradeable. ws1r and (ws2r or ws3r) outside 27/73 on the dr side, inside the last 5 min, backward only |
| WALK FIRES FROM | the signal. The first bar all of the above hold at once |
| trade_walk | closes it. Three exits racing — an opposing signal, the dr flip, or the stop |
| the stop | caps the loss. 0.70% from entry, live inside the walk, wins any tie |

**The evidence is ONE DAY** — 9 signal bars on 09-01, 16 armed episodes. Joe 1001: *"we are well
aware that this is not a proven strategy"*.
