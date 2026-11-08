# the live process's SRP repair, 2026-11-08

GOAL: give `out/momo_live.py` ONE job - receive a request, route it, return lines - so that a local
name can never again shadow a module import across 23 unrelated readings. HIS 1108 GO: *"re the
SRP - I'm sure you want to make that clean - set up a SRP plan to make your house pretty, then
apply it"*.

PLAINLY: the live process answers 23 kinds of request. Twelve of them are one line that calls a
named table builder. Eleven hold their whole body inside the routing function, 463 lines of it,
and I added ten of those eleven in three days. That one function is 577 lines long, and it is why a
local variable named `R` silently replaced the render module for every other kind until one of them
was called.

---

## 0. WHAT IS WRONG, MEASURED

| the measure | value |
|---|---|
| `out/momo_live.py`, total lines | 746 |
| the one routing function | 577 lines |
| request kinds inside it | 23 |
| kinds that are already one line to a builder | 12, holding 110 lines |
| kinds holding their body inline | 11, holding 463 lines |
| kinds I added in 3 days | 10 |
| what it already cost | commit `08f89c1` - `Rr, Mm` renamed because `R, M = LN['CPR'][tf], LN['CPM'][tf]` shadowed the module-level render import for the WHOLE function. Python binds that at compile time, so every other kind broke silently until called |

| the kind | lines inline | calls a builder | where it belongs |
|---|---|---|---|
| knobs | 9 | head, row | stays - already routed |
| stages | 35 | head, row | stage 2 |
| c3rmage | 10 | c3rmage_table | stays |
| tawaway | 63 | row | stage 1 |
| xcvdiff | 45 | row | stage 1 |
| xcv | 84 | none | stage 1 |
| xdiag | 70 | row, stamp | stage 1 |
| xcross | 29 | none | stage 1 |
| legmfe | 11 | legmfe_table | stays |
| cadlist | 26 | none | stage 1 |
| pivstop | 10 | pivstop_table | stays |
| c3rscan | 9 | cad3r_scan | stays |
| vals | 11 | vals_table | stays |
| runs | 8 | runs_table | stays |
| board | 42 | row | stage 2 |
| legfrom | 25 | row | stage 2 |
| cad3r | 7 | cad3r_table | stays |
| trail | 7 | trail_table | stays |
| window | 9 | window_table | stays |
| pct50 | 26 | pct50_table | stage 2 |
| day | 8 | cadwalk_summary, legs_table | stays |
| leg | 18 | cadwalk_table, leg_table | stage 2 |
| cadwalk | 11 | cadwalk_table | stays |

## 1. WHY NOT JUST MOVE IT ALL TO THE RENDER MODULE

`out/momo_render.py` is ALREADY 1933 lines with 24 builders. Moving 463 lines into it makes a worse
single-responsibility problem than the one being fixed. The destination is chosen by WHICH MECH the
reading serves:

| the destination | what goes there | why |
|---|---|---|
| `out/xcv_report.py` - NEW | the 6 `fdm2-xcv` readings: xcv, xcvdiff, xdiag, xcross, cadlist, tawaway - 317 lines | one mech, one reporting module. It is also the mech under active work, so it is the one that keeps growing |
| `out/momo_render.py` | the 5 remaining: stages, board, legfrom, pct50, leg - 146 lines | their neighbours are already there - `pct50_table`, `leg_table`, `legs_table`, `cadwalk_table` |
| `out/momo_live.py` | the request parse, the route, the return | nothing else |

## 2. THE RULE THAT REPLACES THE BUG

A builder takes `LN` and PLAIN VALUES - bars, sides, names, numbers. It never takes `q`, and it
never reaches for a module-level import by a one-letter name. The routing function unpacks `q` and
calls the builder, so it holds no local that can shadow anything. The 1-line kinds already obey
this; the move makes it true for all 23.

## 3. WHAT COUNTS AS DONE - THE PROOF, NOT MY WORD

Every one of the 23 kinds must return BYTE-IDENTICAL output before and after. The capture script is
`capture_kinds.py` in the job tmp: one representative request per kind, all on 2026-08-25, with the
`_answered in` timing line dropped from both sides because it is the run's wall clock and not part
of the answer.

| the gate | state |
|---|---|
| before-capture, all 23 kinds, on the bank | DONE - 1440 lines, `RULED_OK True`, no kind errors |
| stage 1 moved | DONE - `out/xcv_report.py`, 7 builders, 380 lines |
| after-capture, stage 1, byte-identical on all 23 | DONE - 23 of 23 identical by sha1, 0 differing |
| stage 2 moved | DONE - 5 builders into `out/momo_render.py`, which goes 1933 to 2097 lines |
| after-capture, stage 2, byte-identical on all 23 | DONE - 23 of 23 identical by sha1, 0 differing |

## 6. WHAT IT MEASURES AT, AFTER

| the measure | before | after |
|---|---|---|
| `out/momo_live.py`, total lines | 746 | 331 |
| its one routing function | 577 | 159 |
| request kinds | 23 | 23 |
| the longest kind inside the routing function | 84 lines | 11 lines |
| `out/momo_render.py` | 1933 | 2097 |
| `out/xcv_report.py` | did not exist | 380 |

THE CHAIN STAYED PUT. The five stage-2 readings consume the live process's memoised day chain, so
`chain(day)` is still called in the routing function and `LG`, `TR` and `SIGS` are handed to the
builder as plain values. Memoisation belongs to the process that holds the arrays; rendering does
not.

## 4. SEQUENCING, AND WHY IT IS TWO STAGES

Stage 1 is 6 kinds with no existing builder - a pure move, the biggest win, and on the mech under
active work. Stage 2 is 5 kinds that already call a builder and carry argument preparation around
it; they touch the trade reporting he reads every day, so they get their own step and their own
proof rather than riding along with stage 1.

## 5. WHAT IS NOT IN SCOPE

No reading changes. No knob moves. No column changes. If a byte differs, the move is wrong and the
move gets fixed - the output does not.
