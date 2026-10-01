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

## WHAT LIVES WHERE

| file | holds |
|---|---|
| `docs/octo-freedom/` | reports on this machine, newest work appended or added as a new dated file |
| `docs/o9-live-recon/` | the o9-live + fakeAPI handover package, including the startup prompt a new session reads |
| `docs/22_go_20260921/NOTES_momtf_mechdev.md` | the day-by-day record of how the machine was built, Joe's rulings quoted verbatim |
| `report_leash_walk.py` | the acceptance test. 9 validated bars plus the day's shape, exits 1 on either moving |
| `tests/test_arm_state.py`, `tests/test_leash_walk.py` | 12 property checks |

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
