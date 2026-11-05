# the fdm2 re-entry machine | banked 2026-11-04

The mech lives in `docs/octo-freedom/1022_v4/v4_fdm_reentry.py`, function `signals`. It is the
only way into a trade from flat, so every chain's first leg comes from it.

## the window, after his 1105 purge

```
-a window opens when ws1b is oob on the side
-the window closes when ws1b crosses back inside on the same side
--the close bar is the bar that cross confirms on
--a window with no close after it never fires
--one window per close, so two opens before one close collapse onto it
```

His 1105: *"purge '--gcws30b is past the 5/95 fence, on either side' from the reentry spec"*.
`FDM_RE_WIN_OPEN` moves from 'both' to 'ws1b'. gcws30b is still read by the cadence-event mech;
this purge is the OPENING test only.

## his 1104 walk, the banked base

```
-if a cadence window opens
--walk until ws5 reverses
---if ws5r reverses while ex-20/80-fence
----if ws6r is ex-20/80-fence
-----walk forward until ws6r reverses
----else if ws6r is not ex-20/80-fence
-----scan the wsf TFs above ws6 for a wsf ws{higher TF}r that is infence
-----if a higher wsf TF r is infence
------open a trade on the last to fire, out of ws5r reversing or ws6r reversal or ws1b
       crossing to ib
#all signals are sameside of the cadence
```

## his 1104 mod, banked the same day

```
-IF a ws{a TF}r line is ex-20/80-fence and waiting to reverse before handing over to the next
 highest TF
--IF a ws{a TF}x crosses the ws{a TF}r line using emerging values and wob 12
   (crosses over for lowside, crosses UNDER for highside)
---IF ws{a TF +1}r is infence
----rev-trade
```

His example: ws5r low side, 2026-08-07 06:50 to 07:05, ws5x crossing over ws5r, ws6r at 43.

**"rev-trade" is his generic word for sending the signal to the router.** From flat the router's
action is an OPEN only, 1 bar - his *"the router knows there isn't an incoming trade"*.

### his 1105 corrections to it, all banked

| what he corrected | what changed |
|---|---|
| *"there was no such 'ws4r is not past the 20 fence' gate on the ws{a TF}x cross"* | the fence is the STATE the line is in while waiting - past it at some bar from the window's open to the cross - not a test at the cross bar. `FDM_RE_XCROSS_FNC_AT` 'stretch' |
| *"are you saying that ws4x didn't cross ws4r?"* | it had. `_xcross` returned only the FIRST cross and the caller tested it once. It now returns every confirming cross and the first that passes all three gates fires |
| *"I intentionally referd to `a TF`, so that you would see the dynamic nature of the mod"* | it watches every line from `FDM_RE_XCROSS_LO` to `FDM_RE_SCAN_HI`, not two fixed points. `FDM_RE_XCROSS_TFS` 'band' |
| *"make ws4 the lowest TF"* | `FDM_RE_XCROSS_LO` 4. It is NOT tied to the trigger line - that floor was mine and it hid the only qualifying cross |

Three defects of mine were found in the same stretch and are fixed:

| the defect | what it did |
|---|---|
| a base-walk stop ran before the mod's bar was used and `continue`d out of the window | the 2026-08-07 05:33:00 window lost its 05:45:15 signal |
| both mod appends carried none of the 9 fields the trace report reads past `SG.signal` | `KeyError: 'close'` |
| two of those fields are `None` for a mod-fired window and the report called `int()` on them | `TypeError` on `int(None)`; the report now prints `-`, as it already did for `b6` |

### his 1105 acceptance test, met

| the 2026-08-07 05:33:00 LOW window | value |
|---|---|
| the window opened, ws1b oob LOW | 2026-08-07 05:33:00 |
| its ws1b ib close | 2026-08-07 05:36:00 |
| the base walk's ws5 reversal | 2026-08-07 05:50:35, ws5r 29.13, not past 20 - the base walk stops |
| what carried it | HIS MOD |
| the signal bar | **2026-08-07 05:45:15** |
| the cross behind it | ws4x crossed ws4r 05:44:20 on emerging, held 12 bars = 60 s |
| ws4r past the fence while waiting | 12.1980 at 05:44:00 |
| ws5r in-fence at the cross | 30.4863 |
| the trade | LONG, open 2026-08-07 05:45:20 |

The whole 2026-08-07 signal list is `fdm2_reentry_0807.md` in this directory. The day's first
signal moves from 06:57:40 to **00:13:10**: the ws4 floor, the stretch-read fence and testing
every cross widen the mech a long way, and the day's net is measured by the leg chain, not here.

### the two waiting points it watches

| the waiting point | the line | the line above it | where the search starts |
|---|---|---|---|
| the walk is waiting for the reversal that starts it | `FDM_RE_REV_TF` 5 | ws6 | the cadence window's open |
| the walk is waiting for the gate line's reversal | `FDM_RE_GATE_TF` 6 | ws7 | the ws5 reversal bar |

His answer on which lines: *"any lines that fdm2-reentry needs"*.

### its knobs

| the knob | value | what it is |
|---|---|---|
| FDM_RE_XCROSS_ON | 1 | ON. At 0 the walk is the 1104 base and every earlier number is reproduced |
| FDM_RE_XWOB | 12 | his hold, 12 bars = 60 s. Held apart from LIN2_CROSS_WOB 12, a different mechanic |
| FDM_RE_XCROSS_TFS | band | every line from FDM_RE_XCROSS_LO to FDM_RE_SCAN_HI. 'both', 'rev' and 'gate' are the fixed-point settings it replaced. THE KNOB NAME IS MINE |
| FDM_RE_XCROSS_LO | 4 | the lowest line it watches, his *"make ws4 the lowest TF"* |
| FDM_RE_XCROSS_FNC_AT | stretch | the fence is read across the waiting stretch, his 1105 correction. 'cross' reads it at the cross bar |
| FDM_RE_XCROSS_UP_READ | closed_prev | the ws{TF+1}r in-fence read. His own 43 is the closed-prev value; emerging reads 40.79 there. THE READ IS MY CALL |

### what is mine in it, stated

| the reading | why it is mine |
|---|---|
| the ws{TF}r ex-20/80 test reads EMERGING, the same series as the cross | they describe the same line at the same bar, so they take the same series |
| when two crosses qualify, the EARLIEST fires | matches the walk's own "first" rule everywhere else |
| the earlier of the mod's bar and the base walk's bar wins | a walk forward meets whichever comes first; no priority knob is needed |
| the ws1b ib close stays in the last-to-fire set for the mod | `FDM_RE_FIRE_IB` 1 is his spec, and it keeps the signal from preceding ws1b's return |
| the window-open invariant was split, not deleted | see below |

### the invariant that moved

The base walk fires on the LAST of three events, so its signal could never precede the ws5
reversal, and one assert carried both that claim and the window-open claim. The mod fires BEFORE
the reversal on purpose. The assert is now two:

| the assert | holds for |
|---|---|
| the fire bar is at or after the window's open | every path |
| the fire bar is at or after the ws5 reversal, unless the mod fired | the base walk only, with the exception carried by a flag, not a label string |

## what the mod did on 2026-08-07

| the reading | value |
|---|---|
| re-entry windows | 19 |
| windows whose signal moved earlier | 13 |
| windows unchanged | 6 |
| the largest move earlier | 34 min 10 s - the 08:43:00 HIGH window, 09:30:35 to 08:56:25 |
| his own example window, 06:53:00 LOW | 07:10:35 to 06:57:40, 12 min 55 s earlier |

**His 1104 ruling on how it gets tested:** *"the mod only fires for reentry (ie when we don't have
an open trade), so recreating the walk is not needed - I'll be investigating every stop by hand,
so if there's issues in the mod I'll see them in the wild - that's a better way to evolve"*. So
there is no sweep of it, by his instruction.
