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

## THE RESULT, FROZEN AND ASSERTED — RE-FROZEN 1013

Joe 1013: *"re-freeze the reference and add both trades, for 10.2784%"*.

| trade | close event | n of 7 | held? | extension fires | last mile ends | why | gross at the close | gross at the end |
|---|---|---|---|---|---|---|---|---|
| 07-17 21:58 LONG | 2026-07-18 01:15:20 | 0 | no | 2026-07-18 03:41:10 | 2026-07-18 03:42:05 | exhaustion | +1.3061% | +1.3666% |
| 07-18 02:31 SHORT | 2026-07-18 10:40:40 | 6 | YES | 2026-07-18 11:11:15 | 2026-07-18 11:13:35 | exhaustion | +4.8615% | +4.8337% |
| 07-18 08:46 LONG | 2026-07-18 10:07:10 | 0 | no | 2026-07-18 10:07:10 | 2026-07-18 10:07:20 | exhaustion | +0.3929% | +0.4014% |
| 07-18 16:07 LONG | 2026-07-18 16:38:15 | 5 | YES | 2026-07-18 17:39:10 | 2026-07-18 18:12:00 | exhaustion | +0.7967% | +1.7205% |
| 07-18 18:12 SHORT | 2026-07-18 18:44:15 | 3 | no | 2026-07-18 18:44:15 | 2026-07-18 18:45:15 | blast radius | +0.4441% | +0.3769% |
| 07-18 18:45 LONG | 2026-07-18 20:04:00 | 2 | no | 2026-07-18 21:17:45 | 2026-07-18 21:17:55 | exhaustion | +1.4948% | +1.5793% |
| **TOTAL** | — | — | — | — | — | — | **+9.2961%** | **+10.2783%** |

All 14 figures asserted on every run. `machine.py` exits non-zero on any mismatch.

### THE ws30 MODE, link 3

Joe 1013: *"let ws30 fire the hold and ride it"* / *"I think the `ws30 -> oob -> ws1cp-ib` flow is
the best option for a surgical way to use a line as wide as ws30"*. When ws30 is mom-true toward the
TRADE'S OWN board at the close event - *"we can only use the trades side for link 3"* - ws30 becomes
the hold-and-ride line for that trade alone and the close fires at the first target-side ws1cp-ib
after ws30r goes oob, not at the dws10r stall. `W_EXT_WS30`, default on.

IT FIRES ON TWO TRADES, NOT ONE. My estimate of +9.9939% assumed it touched only 18:45; it also
fires on 21:58 LONG, whose 01:15:20 close now holds to 03:41:10. That is why the total is +10.2783%.

| trade | ws30r goes oob | the held close fires | gross at the end, before -> after |
|---|---|---|---|
| 07-17 21:58 LONG | 2026-07-18 02:30:00 | 2026-07-18 03:41:10 | +1.0821% -> +1.3666% |
| 07-18 18:45 LONG | 2026-07-18 20:30:05 | 2026-07-18 21:17:45 | +0.3956% -> +1.5793% |

THE LARGE-LEG TESTS ARE NOT IN THIS PATH. The ws30 mode reaches 2026-07-18 21:17:45 on the 18:45
LONG without them; the large-leg walk reached the same bar by another route and is shipped nowhere.
See `1013_large_leg_findings.md`.

### THE CHAIN IS ASSERTED END TO END

The last three trades are the 07-18 chain's own links, each opening on the bar the one before it
ended:

| link | ends | the next link opens | same bar? |
|---|---|---|---|
| 07-18 16:07 LONG | 2026-07-18 18:12:00 | 2026-07-18 18:12:00 | yes |
| 07-18 18:12 SHORT | 2026-07-18 18:45:15 | 2026-07-18 18:45:15 | yes |

## THE PREVIOUS FREEZE, FOR THE RECORD

| trade | close event | n of 7 | held? | extension fires | last mile ends | why | gross at the close | gross at the end | moved |
|---|---|---|---|---|---|---|---|---|---|
| 07-17 21:58 LONG | 2026-07-18 01:15:20 | 0 | no | 2026-07-18 01:15:20 | 2026-07-18 01:16:20 | exhaustion | +1.0517% | +1.0821% | +0.0304% |
| 07-18 02:31 SHORT | 2026-07-18 10:40:40 | 6 | YES | 2026-07-18 11:11:15 | 2026-07-18 11:13:35 | exhaustion | +4.8615% | +4.8337% | -0.0277% |
| 07-18 08:46 LONG | 2026-07-18 10:07:10 | 0 | no | 2026-07-18 10:07:10 | 2026-07-18 10:07:20 | exhaustion | +0.3929% | +0.4014% | +0.0084% |
| 07-18 16:07 LONG | 2026-07-18 16:38:15 | 5 | YES | 2026-07-18 17:39:10 | 2026-07-18 18:12:00 | exhaustion | +0.7967% | +1.7205% | +0.9238% |
| **TOTAL** | — | — | — | — | — | — | **+7.1028%** | **+8.0377%** | **+0.9349%** |

That was the freeze before the ws30 mode, four trades at +8.0377%. The hold adds no leg boundary, so
drag is unchanged — every figure in this file is gross.

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

## THE HTF oob GATE — BANKED 1013

`_htfgate.py`. Joe 1013: *"I'm going to use a hack to get us past the 21:17 short ... -if a trade
closes when ws{>=30}r is oob, only open trades that are towards the oob HTF line / -the restriction
ends when ws30r is IB after ws60x-crosses r with a 48 wob"*, and the form built is his
clarification: *"if the HTF line is high OOB, then only long trades sourced from low oob ws1cp's
are allowed. the inverse is true for an HTF low oob: only high oob ws1cp's are allowed to place a
SHORT trade"*.

| the HTF | the cp permitted | the trade it places |
|---|---|---|
| ws{30,45,60,90}r HIGH oob | a **LOW**-oob ws1cp | a LONG |
| ws{30,45,60,90}r LOW oob | a **HIGH**-oob ws1cp | a SHORT |
| none oob | any cp | either |

THE RELEASE: ws60x crosses **UNDER** ws60r — Joe: *"it's always x-crossing under on a high oob"* —
holds `W_HTF_X_WOB` 48 bars = 4.0 min, then the first bar ws30r is inside the oob fence 15/85.
MEASURED from the 2026-07-18 21:17:55 exit: 57 ws60x/ws60r crosses before 03:09 and only 8 hold the
wob, the rest being 5-to-45-second flickers. UNDER-only makes the first qualifying cross
2026-07-19 01:00:00, its wob completes 01:03:55, and the release lands **2026-07-19 01:05:45** —
the row Joe banked.

SRP: the gate opens no trade and closes none. `_ibmech` stamps the cps, `_extmom` holds the close,
`_chain10` walks, and none of them knows the gate exists — the caller asks it before it opens.

### THE WALK FROM 2026-07-18 21:17:55, THE GATE LIVE

Stop 2026-07-19 11:22 unless carrying a trade; if carrying, walk it to the end then stop.

| step | exit bar | the oob HTF line | the cp permitted | the release | the cp taken |
|---|---|---|---|---|---|
| 1 | 2026-07-18 21:17:55 | ws30r 86.58 HIGH | LOW-oob, a LONG | 2026-07-19 01:05:45 | LOW cp 03:58:05, ib 04:11:55 |
| 2 | 2026-07-19 05:22:55 | ws30r 7.05 LOW | HIGH-oob, a SHORT | 2026-07-19 06:33:20 | HIGH cp 05:51:45, ib 05:53:30 |
| 3 | 2026-07-19 08:03:10 | ws45r 3.78 LOW | HIGH-oob, a SHORT | 2026-07-19 08:22:15 | LOW cp 09:15:10, ib 09:16:15 |

| open | side | close event | ws30 mode | the walk ends | why | gross |
|---|---|---|---|---|---|---|
| 2026-07-19 04:11:55 | LONG | 2026-07-19 05:05:25 | no | 2026-07-19 05:22:55 | exhaustion | +0.3741% |
| 2026-07-19 05:53:30 | SHORT | 2026-07-19 07:53:25 | no | 2026-07-19 08:03:10 | exhaustion | +0.5390% |
| 2026-07-19 09:16:15 | LONG | 2026-07-19 09:54:25 | YES | 2026-07-19 22:04:35 | exhaustion | -0.7911% |
| **TOTAL** | — | — | — | — | — | **+0.1220%** |

- step 1 carries NOTHING for 6 h 54 m: every HIGH cp between 21:17:55 and the release is blocked,
  and the walk waits for the LOW cp at 03:58:05 - the cp the `W_IB_DWELL` 2 ruling unlocked.
- step 3 opens a LONG off a LOW cp although the restriction wanted a SHORT: its ib bar 09:16:15 is
  past the release at 08:22:15, so the restriction had already lapsed. It is the only losing leg.
- THE UNRESTRICTED WALK FROM THE SAME BAR LOST 3.3111% over three alternating-side links. The gate
  is +3.4331% against it on this stretch.

### WHAT IS STILL OPEN

- leg 3 ran **12 h 10 m** on the ws30 mode, 09:16:15 to 22:04:35, and that single hold is the whole
  negative. The ws30 mode has no time bound. Same shape seen on the 07:59 LONG.
- `oob_side` takes the FIRST oob line in TF order. Joe named no tie-break and the lines have not
  been seen oob on opposite ends at the same bar. Stated in the module.
- the knob NAMES `W_HTF_GATE`, `W_HTF_TFS`, `W_HTF_X_TF`, `W_HTF_IB_TF`, `W_HTF_X_WOB` are mine;
  every value is his.
