# strat-3-r-oob — handover

Joe 0925 named it and separated it: *"given that '3 `r`s oob' mostly fails to align with
wsf_leash, I'm declaring it as a second strategy to be developed separately"*.

**NOTHING IS BUILT. NO DEV OR SCIENCE UNTIL JOE SAYS SO.**

## The startup prompt — paste this to open the next session

> You are picking up `strat-3-r-oob`, a second trading strategy Joe separated from the wsf_leash
> work on 0925. It is a **handover review only**.
>
> **Do not develop, do not run science, do not propose knob values.** Joe will say when.
>
> Your one job this session: **read every file in `docs/strat-3-r-oob/`, re-run `scan.py`, and
> validate that the handover is complete.** Specifically:
>
> 1. Does `scan.py` reproduce `scan_20260925.txt` exactly? Report any drift.
> 2. Does `measured.md` match what `scan.py` produces? Check every figure.
> 3. Does `spec.md` describe the mechanic that `scan.py` actually implements? Name any gap.
> 4. Is anything in `open_questions.md` already answered somewhere in the repo? If so, say where.
> 5. Is anything MISSING that you would need before building? List it.
>
> Report what you find. Change nothing. If you think a decision is needed, stop and tell Joe —
> he is the architect and designer, you are the master coder.
>
> Standing rules that apply from bar one: use only the mechanisms Joe has given you; if you cannot
> hit a target, say why; never present data as better than it is; every unplanned decision stops
> and goes to Joe.

## The files

| file | what it holds |
|---|---|
| `spec.md` | the mechanic, every knob, every producer it reads, and what is MINE vs Joe's |
| `history.md` | how it was found on 0925, and every correction made along the way |
| `measured.md` | the 28 episodes, the returns, the tag split, and the cost check |
| `open_questions.md` | every decision that is not made |
| `scan.py` | the producer that generated the numbers. Reproducible |
| `scan_20260925.txt` | its output on 09-01 → 09-06 |

## The one-line version

At any bar in a dr stretch where **ws1r, ws2r and ws3r are all out of bounds on the dr side inside
a rolling 60 s window**, walk `ws{tf}Mage`-rev from that bar and take the earliest print. Measured
over 5 days: 28 episodes, 18 of 28 in profit at +33 min, and on Joe's `t`-tagged subset 13 of 20
clear the 22,000-coin drag with a +0.339% mean.

## Reproducibility

`scan.py` execs `docs/22_go_20260921/_prelude.py` for the tape, the ws1..ws23 role lines, the momo
banks, the v3 config and the dr latch. It has no scratchpad dependency.

Verified 0925: `python3 docs/strat-3-r-oob/scan.py` reproduces `scan_20260925.txt` **byte for byte**.
