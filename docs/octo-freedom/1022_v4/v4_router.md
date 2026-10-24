# THE ROUTER — spec

Banked 2026-10-24. Joe's words are quoted verbatim; everything outside a quote is the build.

## 1. Why it exists

> the code should be asking "where is my rev-trade event?", but we haven't (SRP) built a routing
> mech. without a single point producing rev-trade, mechs conflate internally

Before it, two things were computed in several places by several rules:

| the thing | where it was computed | the rules |
|---|---|---|
| the rev-trade bar | v4core, v4core's immediate case, the backstop, three v4saviour returns, v4_equity.ledger | `exh + 1`, `a + 1`, `max(exh, fire) + 1`, `fill + 1` |
| the direction | the chain, the scan | `flip(the previous trade)`, `'SHORT' if side > 0` |

The two direction rules disagreed on 2026-09-01 19:43: a HIGH-oob backstop fire printed a LONG,
because the chain alternated from the previous SHORT. Joe found the contradiction inside the row.

## 2. A signal, and a fire

> a signal, or a fire (do you see these as the same thing? I see "signal" as "here, I have
> actionable data for you", and fire as "I'm actioining based on that signal". the distinction
> allows for holding signals if other mechs need to qualify

A signal carries a BAR and a SIDE, and nothing else that a router would need:

| field | what it is |
|---|---|
| `bar` | the bar the mech's last condition landed — an exhaust, a fill, an arm |
| `side` | +1 the HIGH oob side, -1 the LOW. An input, never derived |
| `mech` | `core`, `backstop` or `saviour` |
| `src` | the bar the mech's own walk started. For the trace only; the router never reads it |
| `why` | one line for the report |

There is NO `open` field and NO `dir` field, on purpose. `v4_signal` owns this and produces no
signal itself.

## 3. What a mech may produce

> Does a mech's condition being met create a candidate regardless of what is open
> -yes. then the pyramid checks are downstream of that

So every producer is a TAPE SCAN, both sides, regardless of what is open:

| producer | the signal bar | the side |
|---|---|---|
| `v4_sig_core` | the lineage exhaust, or the arm itself in the immediate case | both, scanned separately |
| `v4_sig_bstop` | `max(the lineage exhaust, the fire)` | both, no filter |
| `v4_sig_saviour` | the `SAVIOUR REV` fill | the counter of the arming signal's side |

`v4core` used to be asked *"what will close the trade that is open?"*, which made a signal's
existence depend on the open position — a counter-side arm was invisible rather than a candidate.

## 4. The saviour arms on a SIGNAL

> the saviour's hunt starts at the gated signal's bar
> -yes, exactly the same behaviour as a non-gated signal

> here's what makes this simple and easy - the 0429 signal doesn't know it's gated, that's routers
> decision. router doesn't feedback, therefore ZERO action is needed to allow the 0459 saviour
> qualification to fire

The router does not call v4saviour. One hunt per signal, from that signal's own bar, and the
hunt's target-side is the counter of the signal's side — a HIGH signal would open a SHORT, and a
SHORT's target-side is LOW. The signal it emits carries that same side, so it closes the SHORT and
opens a LONG:

> saviour should pass timestamp/LOW/saviour to router

**What the old wiring suppressed.** `route` called v4saviour once per BLOCK, at the block's
earliest open bar, through a `saviour=` callback. On 2026-09-01 the 04:28:55 HIGH core signal is
refused against the 03:34:30 SHORT, and the only hunt on that block ran from 03:34:30:

| the hunt's start | the arm walkback read | the verdict |
|---|---|---|
| 2026-09-01 03:34:30, the block open | ws5r 90.66 at 2026-09-01 03:15:00, HIGH oob | NOT ARMED |
| 2026-09-01 04:28:55, the signal's own bar | ws5r 41.91 at 2026-09-01 04:25:10, not oob | SAVIOUR REV, fill 2026-09-01 04:41:45 |

## 5. A saviour arms on a saviour

> I know of at least one scenario where saviour signalled `saviour-rev`, then the next trade
> followed the same `saviour-rev` path. I can't find it now, but we do need to allow for it. why do
> you think it would chain without end?

It does not chain without end. A hunt looks FORWARD from its start bar, so its fill is strictly
after the bar that armed it; a chain's bars strictly increase and the window ends it. That is an
assert in `v4_sig_saviour._hunt`, not a comment:

    assert int(res['fill']) > int(g['bar'])

`produce` runs to a fixed point — each generation arms the next, and it stops when a generation
produces nothing new. There is NO generation cap. The generation counts print on every run.

## 6. The fire bar

One rule, in one place — `v4_signal.fire_bar` — replacing the five computations in §1:

    the fire bar = the signal bar + 1

The signal bar is already the bar its last condition became knowable, so the fire is the next bar
and nothing earlier. The report asserts `the open == the signal bar + 1` on every row.

## 7. The pyramid

> router only holds the LONG signal for milliseconds: it's job is to accept the signal, check
> count(exisitng open same-side trade) <= max_pyramid, and drop the signal if false

`v4_pyramid.Pyramid` owns the open trades, the count, the boundary and the close-all:

> SRP the max_pyramid routing. my gut says it should be a class

**The boundary is `count < cap`**, ruled by Joe 1024: *"count < cap is right"*. So cap 2 means at
most two open in a direction. His earlier restatement of the test is the same thing:

> it is simply: I'm about to open a SHORT (or a long), is there a SHORT (or long) already open

**THE ORDER IS HIS AND IT MATTERS.**

> rev-trade is 2 opposing mechanisms: CLOSE the trade, then OPEN a **NEW** trade in the opposite
> direction

The close runs first, then the open is tested. Because a signal closes the OPPOSITE direction and
is tested on its OWN, closing never frees the slot it is then tested against.

**A refused signal is DROPPED.** No queue, no retry. A signal is acted on once, at its own bar + 1,
or not at all.

## 8. The close

> [which open position does a signal close, when two or more are open on that side]
> -close all of them together

> [does each open position get its own saviour] -no. a single saviour will open on qualification
> and defer to the router if `saviour-rev` prints. the router will close them all together

## 9. UNRULED, and it decides trades

Signals are acted on in fire order, which is signal-bar order. Within one bar the order is the
mech's NAME — alphabetical, so `backstop` before `core` before `saviour`. That order decides which
of several signals sharing a bar becomes the trade and which are dropped.

On 2026-09-01 at 01:37:10 three LOW signals share the bar — a v4core arm2 arm at 01:14:25 and two
backstop fires at 01:16:55 and 01:18:40. All three start at ws4, all three hand the baton ws5 to
ws6 at 01:35:25, and all three second-walk to 01:37:10; two of them are the same walk from 01:20:45
on. At cap 2 the first two open and the third is dropped.

## 10. The report

> besides the timestamp 1) the data that was passed into router and 2) what the router did with it
> and 3) why it did what it did

> why is `open before` important? the router doesn't need that data

`route(..., journal=[])` records one row per decision: what it was handed, what it did, and the
count it compared to the cap. It does NOT record the open set — the decision reads one number.

The detail column is reduced on his word: *"the detail column can be reduced to ` step2 arm
00:26:00, ws2`"*. Its stamps are bare `HH:MM:SS`, which loses the day on a window that spans dates.

## 11. What runs

    python3 v4_route_run.py <out|-> <start> <end> [max_pyramid]

`max_pyramid` defaults to `K.MAX_PYRAMID` 2 and REFUSES any other value unless `W_V4_EXPERIMENT=1`.
Before that check, a run at 1 printed `RULED_OK True` beside a machine that was not the bank.
