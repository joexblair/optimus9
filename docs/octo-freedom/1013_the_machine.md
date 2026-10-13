# THE MACHINE — 1013

Joe 1013: *"make it the machine"*, after *"what word do you need from me that I can give you when
I'm ready for our current 'banked chain' to be the live machine? that live machine is what we will
be continue our work on"*.

```
cd docs/octo-freedom/1005_scoring && python3 machine.py
```

No arguments. No env vars. Joe 1013: *"I need full state in the live machine without needing
multiple versions of the same arg"*.

## THE CHAIN

| # | link | mech | computed here? |
|---|---|---|---|
| 1 | the trade opens | Joe's open mech | **not shared yet** — the four opens are declared |
| 2 | the close event fires | `_ibmech`, the ws1Mage IB-cross mech | **yes** — `IBMech.walk(open_bar, dr)`, closed 1013 |
| 3 | the close is held and extended | `_extmom`, the momentum extension | **yes** — `exit_bar` is called, the extension bar is no longer a literal |
| 4 | the last mile walks | `_chain10` under `W_ARM=lastmile` | **yes** |

LINK 2 CLOSED, 1013. Joe: *"close link 2"*. `IBMech.walk` scans forward from the open on the target
board's side only, takes the decision bar at each target-side ws1-cp (the g30 delegation when it
fires, else the ws1Mage IB bar) and reads the 5-minute grace window; the first REVERSE is the close.
All four close bars are now COMPUTED and each is asserted against the bar banked in `2fa091e` /
`ba38629` — all four match. Its class docstring promised `entries()` and `walk()` and neither
existed; the walk lived in throwaway drivers, which is how a lineage walk got substituted for it at
the 2026-07-18 18:12:00 bar.

`machine.chain(open_bar, dr)` runs all three live links as ONE function, so a caller cannot stitch a
different mech into the middle of it.

THE ONLY DECLARED INPUT LEFT IS LINK 1: the trade's open bar and side. Joe has not shared the open
mech.

## THE RESULT, FROZEN AND ASSERTED

| trade | close event | n of 7 | held? | extension fires | last mile ends | why | gross at the close | gross at the end | moved |
|---|---|---|---|---|---|---|---|---|---|
| 07-17 21:58 LONG | 2026-07-18 01:15:20 | 0 | no | 2026-07-18 01:15:20 | 2026-07-18 01:16:20 | exhaustion | +1.0517% | +1.0821% | +0.0304% |
| 07-18 02:31 SHORT | 2026-07-18 10:40:40 | 6 | YES | 2026-07-18 11:11:15 | 2026-07-18 11:13:35 | exhaustion | +4.8615% | +4.8337% | -0.0277% |
| 07-18 08:46 LONG | 2026-07-18 10:07:10 | 0 | no | 2026-07-18 10:07:10 | 2026-07-18 10:07:20 | exhaustion | +0.3929% | +0.4014% | +0.0084% |
| 07-18 16:07 LONG | 2026-07-18 16:38:15 | 5 | YES | 2026-07-18 17:39:10 | 2026-07-18 18:12:00 | exhaustion | +0.7967% | +1.7205% | +0.9238% |
| **TOTAL** | — | — | — | — | — | — | **+7.1028%** | **+8.0377%** | **+0.9349%** |

`machine.py` asserts all 10 of those figures and exits non-zero on a mismatch, so a regression fails
the script instead of waiting to be noticed in a table. The hold adds no leg boundary, so drag is
unchanged — these are gross figures.

## THE FOUR DEFAULTS THAT MOVED

Joe 1013, on what the word had to fix: *"does this mean that when I say 'bank', you're not fixing
the config as 'confirmed and in-use'?"* — it did not. Every ruling of his lived as a knob while the
default kept the superseded value, so an unset run was the OLD mech.

| knob | was | now | his words |
|---|---|---|---|
| `W_ARM` | mage | **cp** | 1011: *"replace the current ws2Mage lineage walk qualifier with ws1-cp"* |
| `W_ARM_TF` | 2 | **1** | 1009: *"let's swap ws2Mage with ws1Mage"* |
| `W_LOOP_TF` | off | **10** | 1013: *"ws10 is the loop tf"* |
| `W_CEIL` | unset | **30** | 1013: *"ws30 is the ceiling"* |
| `LG_TAPE_END` | 2026-10-04 | **2026-10-05** | 1013: *"full state in the live machine"* |

THE HISTORY MOVES WITH THEM, on his ruling: *"the history is in the past for us now. the machine
we're building now is the only one - if we choose to bring a historical machine into our working
machine, then we can modify it to work with the live machine"*. Every lineage-walk figure banked
before 1013 was produced on the ws2Mage arm with no loop TF and no flat ceiling.

NOT AFFECTED: the +8.0377% chain. `_ibmech` and `_extmom` contain no arm reference, and in last-mile
mode `armed` is True at the first bar so neither arming block runs — proven by reading every `MARM`
and `ARM ==` read in `_chain10`. Measured both ways over the four trades' lineage walks before the
move: ws2Mage +1.2806%, ws1-cp +2.2533%, and that is the lineage walk, not the chain.

## THE RULED GATE

`_ruled.py` holds every knob Joe has ruled, its ruled value, and the words that ruled it.
`_chain10` checks the values a run is REALLY using against that table and prints the result as its
first lines. An off-ruled run **refuses** unless `W_EXPERIMENT=1`, and that flag prints too.

```
RULED CHECK — 18 of 65 knob reads are covered by the ruled set, 12 of them read here; every one MATCHES its ruling
```

- the coverage count is printed on purpose. A table that silently claimed all 65 would be the same
  failure in a new coat.
- no entry goes in from memory. If the words are not in the repo or the conversation, the knob stays
  uncovered and the count says so.
- the remaining 47 are their own bucket. Joe 1013: *"I'm fine with these in their own bucket.
  whenever we sweep, we will validate the knobs before we sweep"*.

## WHAT THIS REPLACED

The 2026-07-18 18:12:00 chain walk. It ran `run_leg` from a new open with no last-mile mode, so the
arm applied and took the `mage` default — the SHORT armed on ws2Mage, never armed at all, and ran to
the MAE stop at -2.5571%. With the gate in place that run refuses before it reports a figure.
