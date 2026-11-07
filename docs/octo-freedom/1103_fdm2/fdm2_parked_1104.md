# PARKED, to resume when the sweep is closed - his 1104 words

*"before I worked on the reentry, we were looking at a table that produced the groups of towards
lines and reversed lines, that we were using to confluence or stay the ws10x-cadence verdicts.
we'll return to this work after the sweep is closed"*

## what that work was

The `fdm2-conf` table - his name, 1104 - reads the board at each trade-setup's signal bar and
groups the lines two ways:

- `towards` / `away` from the Jig's `towards_away`, the rolling-extremum producer on EMERGING values with an
  exact gap: one anchor per trade side, so a line cannot be both
- the reversal groups from the lift-off stamps, which is what the ws10x-cadence's own reversal
  count already uses

The purpose, in his words, was to **confluence or stay** a ws10x-cadence verdict: the cadence says
rev-trade, and the groups of towards lines and reversed lines either back that or hold it.

## where it stands

| what exists | where |
|---|---|
| the fdm2-conf table | `W_FDM2_CONF=on` in fdm2_chain.py, 11 columns, every re-entry leg plus incoming setups at or under zero |
| towards / away | `jig.towards_away`, banked on the Jig as the single source |
| the reversal count | `v4_fdm2.reversed_tfs` and `reversed_since`, the ws10x-cadence's own |
| what was NOT built | the confluence or stay rule itself. He never ruled it |

## why it matters more now than it did

The 1104 sweep found the exit is the stage that loses: the walk and the stop keep -2.1% of the
move the openings find, against a hindsight ceiling of +0.6059% per open. The ws10x-cadence IS the
exit's decision, and staying a bad verdict is exactly the lever the baseline says is missing.

See `fdm2_baseline_1104.md` for the numbers this resumes against.

## HIS CANDIDATE RULE, verbatim, and it was never recorded on disk until now

The rule itself exists in his own words from the chat and nowhere else. Writing it down so it is
not lost a second time:

*"if I base a decision on the 'travelling the incoming way' data, each one of the >=20 of 30
incomings would not print a rev-trade - ie the `trade-setup` would be extended and reviewed at the
next cadence"*

And in the same message, the discrepancy that stopped the work:

*"there's a potential discrepancy: the sum of travelling incoming and travelling outgoing is
greater than the set size"*

IT IS A CANDIDATE, NOT A RULING. He wrote it as "if I base a decision on", and the threshold -
20 of 30 - is his number from reading the table, not a swept one.

## the thread, in order, from the files

| # | what happened | where it is |
|---|---|---|
| 1 | the non-profitable setups table, 4 group columns with their longest runs, 09-15..09-17 | `nonprofit.md`, 201 rows |
| 2 | he read it and proposed the rule above | chat only, now recorded here |
| 3 | he spotted the sum exceeding the set size | the two-sided `towards` let a line be both |
| 4 | he asked for the producer on the Jig - *"bank this so that its not lost ... this should be on the jig so that it has a single source of truth"* - and it was BUILT THERE, not wired into any machine path | the Jig's `towards_away` |
| 5 | the table was rebuilt on the banked mech, and he named it | the fdm2-conf table, `W_FDM2_CONF=on` |
| 6 | he deleted the two longest-run columns and widened the rows to every re-entry leg | the 11 columns it has now |
| 7 | the re-entry work took over | 1104 |

## what is still missing to build it

| the piece | state |
|---|---|
| the groups | built, on the banked mech |
| the table | built, 11 columns |
| his threshold, 20 of 30 | written down, never swept, never ruled |
| which group the threshold reads | `towards the incoming way, ws1-ws30` is the column his sentence names |
| what "extended and reviewed at the next cadence" does to the walk | NOT specified. The walk currently has no "stay" state - a cadence event either rev-trades or walks on |
| whether a stay can repeat | not specified |

THE ONE THING THAT NEEDS HIM: the stay is a THIRD outcome at a cadence event, where the mech has
two. What a stayed verdict does to the next cadence event, and whether it can stay again, is his.

## A CORRECTION HE MADE, 1104

*"that conversation was never converted to a banked mech as far as I'm concerned"*.

He is right, and the word "banked" was mine. What is true:

| the claim | the state |
|---|---|
| the producer exists on the Jig | yes - `towards_away`, marked [PRODUCER - Joe 1103] |
| he asked for it there | yes - *"bank this so that its not lost ... a single source of truth"* |
| any machine path reads it | NO. Only the fdm2-conf table, which is a report |
| a code default moved for it | NO |
| an off-ruled run refuses without it | NO |
| step 1 was ever ruled onto it | NO. Step 1 still reads v4_fdm2.towards, untouched |

So by his own standard - a bank moves the default and an off-ruled run refuses - it was never banked.
It was recorded so it would not be lost, which is exactly what he asked for and all he asked for.
MY FRAMING OF IT AS A "MECH MISMATCH" ASSERTED A RULING HE NEVER MADE.

## PARKED 1106 — bolt the cad walk onto the cadence event, regardless of the ws10x-cadence

HIS WORDS, 1106: *"I recall suggesting that we bolt the cad walk on to the cadence event by default,
regardless of the ws10x-cadence. I didn't follow up on it so that's on me. stash the idea for me,
we'll come back to it after momo is baked"*.

WHAT RAISED IT. He asked why the cad walk started 4 min 10 s after its cadence event on the
2026-08-07 08:26:10 LONG, and the answer was three stacked waits:

| the wait | seconds | what it waits for |
|---|---|---|
| 08:51:00 -> 08:52:20 | 80 | ws1x to cross ws1Mage. Price, not a rule |
| 08:52:20 -> 08:54:15 | 115 | FDM_X10_WOB 24 bars of hold before the cross counts |
| 08:54:15 -> 08:54:55 | 40 | the next ws1 closed-prev seam, which lands at :55 |
| 08:54:55 -> 08:55:10 | 15 | FDM_XCAD_SEAM_S 15.0, his own number |
| total | 250 | |

HIS POINT: *"that's what happens if the x-cross fires"*. When no x-cross fires there is no cad walk
at all, so anything that reads inside a cad walk - fdm2-momo included - never gets a bar to read.

NO CODE, NO SPEC TEXT, NO KNOB. Parked until he says momo is baked.

THE MEASUREMENT THAT WOULD SIZE IT is already in the fdm2-momo run: it counts the truncations that
had a cad walk against those that fired on the ws1 seam+15s bar with no walk at all. That number is
the floor on how much the bolt-on would add.
