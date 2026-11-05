# the fdm2-conf machine | banked 2026-11-04

His 1104: *"make this the fdm2-conf machine"*. The arm is `W_FDM2_CONF=on` in
`docs/octo-freedom/1103_fdm2/fdm2_chain.py`; the producer is `jig.reversal_extremum` in
`optimus9/analysis/jig.py`.

## the definition this machine is built on

| at a trade's | his term | his words |
|---|---|---|
| OPEN bar | outgoing | *"being sent out rather than received"* |
| CLOSE bar | incoming | *"arriving at a destination, taking up a new position or role"* |

*"a single trade is both outgoing and incoming - it all depends on which end of the trade you're
looking at. at 1710, the SHORT is outgoing, and at 1923 the same SHORT is incoming"* /
*"at 1923 a rev-trade happens, so the incoming SHORT is closed, and the outgoing LONG is opened"*.

The lever: *"we curate the EXIT to improve the ensuing OPEN - this means that the incoming trade
AND ITS SIDE is where we make a `walk` or `rev-trade` decision"*.

So at a data bar the open trade is the one a rev-trade would close. It is the incoming trade, and
every board column reads ITS own target side - HIGH for a LONG, LOW for a SHORT.

## the row is a data bar

His 1104: *"we haven't proved that the LONG has exited at 1617. 1617 is where we collect data and
decide on 1) rev-trade, or 2) the cad walk"*.

| the column | what it holds at a data bar |
|---|---|
| the setup opens | `pending` - the outgoing trade's open, 2 bars past a rev-trade not yet decided |
| the incoming trade | the open trade, named by its own open bar, still open |
| its own side | HIGH for a LONG, LOW for a SHORT |
| the setup | `incoming trade based` or `re-entry based` |
| what opened it | what put the data bar on the board |
| realised % | `pending` - needs the outgoing trade to exist and then close |
| ex-20/80 its own way | ws1..ws30 past the fence on the incoming side, closed-prev |
| travelling its own way | `jig.reversal_extremum` state `towards`, incoming side |
| travelling the counter way | the same producer, the other side |
| its unrealised % at the data bar | the open trade's mark at that bar |

Filling `the setup opens` or `realised %` is a read of bars after the decision. Both stay in the
table because they are his columns and the gap is the point.

**NO PROFITABILITY FILTER ON THE ROWS.** The old population - every re-entry leg plus an incoming
setup only when it realised at or under zero - cannot be applied at a data bar without reading
past it. The filter is gone by causality, and that reading is MINE.

## the knobs

| the knob | value | what it is |
|---|---|---|
| FDM_CONF_READ | closed_prev | the VALUE source. His 1104 *"closed-prev is the standard for everything except lift-off"*, the later of his two rulings here. `emerging` is the arm it replaced |
| FDM_CONF_BARS | event+x10 | the data bars: each cadence event plus that event's ws10x race confirm. `event` is the narrower arm. THE KNOB NAME IS MINE |
| LIFT_PTS | 6 | samples in the lift-off window |
| LIFT_TOL | 2.0 | r-points off the window extreme |
| LIFT_WOB | 8 | bars the lift-off state must stay failed = 40 s |
| GAP_PER_TF | 2.8 | bars per TF-minute, the lift-off gap |
| FDM_FNC_2080 | 20 | the fence, 20/80. "ex" includes oob |
| FDM_MAE_CAP | 1.1 | the stop, % adverse from the open. ON |

## what `towards` can mean

`jig.reversal_extremum` takes the side's extreme over a span that INCLUDES the read bar, so its
gap is never negative. `towards` therefore means exactly "sitting at its own running extreme since
the anchor", and `away` means anything else.

Measured at 2026-08-07 16:17:30, the 18 `towards` lines on the HIGH side split:

| the breakdown | count |
|---|---|
| at a gap of exactly +0.0000 | 17 |
| no lift-off reversal inside the span | 1 - ws30r |
| a gap above 0 and still `towards` | 0 |

## what is NOT in it

- the ws8x row from his 1104 experiment. The race has no producer for a line other than ws10, and
  which line it would run on is unruled.
- his 1104 mech update *"because there are towards lines that are ex-20/80-fence, the cadence
  cannot print a rev-trade"*. `jig.confluence_above` holds his 3-step confluence rule; that gate
  is not in it yet.
- the >=20-of-30 extend rule from his *"if I base a decision on the 'travelling the incoming way'
  data, each one of the >=20 of 30 incomings would not print a rev-trade"*. Never ruled into code.

## the proof run

`W_FDM2_DAY=2026-08-07 W_FDM2_CONF=on W_FDM2_LEGS=all` - the whole file is
`fdm2_conf_0807.md` in this directory.

| the reading | value |
|---|---|
| legs walked | 13 |
| data bars | 23 |
| tape | 1,632,960 bars, ends 2026-10-04 23:59:55 |

The two rows that were built by hand first, and which the driver reproduces exactly:

| the data bar | the incoming trade | its own side | what opened it | ex-20/80 its own way | travelling its own way | travelling the counter way | its unrealised % |
|---|---|---|---|---|---|---|---|
| 2026-08-07 16:11:00 | 2026-08-07 14:41:10 LONG | HIGH, upwards | the ws1b oob-to-ib cadence event | 4 of 30 | 16 of 30 | 1 of 30 | +0.439 |
| 2026-08-07 16:18:50 | 2026-08-07 14:41:10 LONG | HIGH, upwards | the ws10x race, to ws10r | 3 of 30 | 18 of 30 | 1 of 30 | +0.157 |

The 2026-08-07 16:17:30 row from his ws8x experiment is absent for the reason under
**what is NOT in it**.

## the definition, in his indented style

```
-every trade has two ends: the bar it opens on, and the bar it closes on
-at the bar a trade opens, that trade is the OUTGOING trade
--outgoing means it is being sent out
-at the bar a trade closes, that same trade is the INCOMING trade
--incoming means it is arriving
-so one trade is both, and the bar you are standing on tells you which one it is

-a rev-trade bar closes one trade and opens another on the opposite side
--the trade being closed on that bar is the incoming trade
--the trade being opened on that bar is the outgoing trade

-we curate the exit to improve the open that follows it
--so the walk-or-rev-trade decision is made on the incoming trade
--and it is read on the incoming trade's own side
---an incoming LONG reads the high side
---an incoming SHORT reads the low side

-at a bar where nothing has been decided yet, the open trade is the incoming trade
--because a rev-trade on that bar would be the bar that closes it
--its own side is the side every line is read on
--the trade that would be opened does not exist yet
---so nothing about that trade can be read at this bar
---its open bar is unknown
---what it realises is unknown
```

## no overlap with the mech that creates cadence events

The two read disjoint inputs. The cadence-event mech decides WHICH BARS exist to decide on; this
producer decides WHAT ONE LINE READS at a bar it is handed.

| the mech | what it reads |
|---|---|
| cadence events | ws1b, the r ladder, the Mage ladder, gcws30b for the rescue, the oob fence 15/85, FDM_M3_FNC 25 |
| this producer | ONE line's values, that same line's emerging copy for the lift-off, LIFT_PTS 6, the per-TF gap, LIFT_TOL 2.0, LIFT_WOB 8 |

This producer cannot declare a bar - it takes `bar` as an argument. So it has not overtaken the
cadence-event mech and cannot.
