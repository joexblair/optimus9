# handover — the ws-finisher

Written 0818. Spec: `docs/ws-finisher_spec.md`. That doc is the authority; this one says where the
code and data are and what is not built yet.

## the scope wall

Joe 0817, opening the spec: *"bank domTF, then purge it from your memory - it's important that you
don't conflate domTF with ws-finisher, and more important that you don't bring any other logic into
the is spec dev (besides what I directly ask of you)."*

Nothing from domTF is in this spec. The ONLY thing crossing the wall is the `domTF` state column,
read as given from `v_ws_fin_walk`. Joe 0817: *"don't spend time validating my domTF claims: I'm
manually validating against the raw data from the v_ws_fin_walk view."*

## what is built

| | |
|---|---|
| `jig.weak_mage_tf(mage, hi, lo, bar, lookback_bars, dr, tfs, same_side)` | the producer. Returns `(weak_tf, detail)` |
| `build_ws_finisher.py` | runs it at every signal in `v_ws_fin_walk`, applies rule C, writes the table |
| `ws_fin_weak_mage` | **121 rows**, one per signal. The knobs are in the unique key |

The producer reads `dr` and tests its sign. It holds no LONG/SHORT logic, per Joe 0817: *"adding
new LONG/SHORT logic isn't SRP - dr gives us all that we need."*

## the numbers as they stand, 08-04

| weak-mage-tf | signals |
|---|---|
| none found | 30 |
| TF1 | 10 |
| TF2 | 42 |
| TF3 | 20 |
| TF4 | 12 |
| TF5 | 1 |
| TF6 | 2 |
| TF8 | 4 |
| **total** | **121** |

| rule C | signals |
|---|---|
| fires (no weak-mage-tf AND domTF FREE) | **12** |
| does not fire | 109 |

| domTF at the signal | with a weak-mage-tf | without |
|---|---|---|
| FREE | 47 | 12 |
| BLOCKED | 44 | 18 |

The 30 rows with no weak-mage-tf are kept, not dropped. Joe 0817: *"no signals are created, but a
stub needs to capture and report this when it happens."* Each carries every line's seconds-since-
last-out, so the reason is on the row.

## settled against Joe's own chart reads

| signal bar | dr | weak-mage-tf | domTF |
|---|---|---|---|
| 10:53:35 | +1 | TF8 | FREE |
| 11:34:00 | −1 | TF2 | FREE |
| 08:02:50 | +1 | TF4 | BLOCKED |
| 04:49:15 | +1 | None | FREE |

Joe read all four on the chart. His read IS the measurement; do not re-derive them to check him.

## what is NOT built

**wsf-momoc and wsf-exhaust.** Joe 0817 gave the definitions and they are in the spec verbatim.
No code produces either state. Settled: both apply to `ws{tf}r` only, TF1 to TF8; they are mutually
exclusive; momoc blocks all trade activity; exhaust arms the weak-mage-tf so the trade fires when
ws{weak-mage-tf}x crosses ws{weak-mage-tf}r. Unknown: how the eight per-line states become one
verdict — Joe 0817: *"these 2 states are the output of the modelling."*

**The reversal producer. This is the next step.** Joe 0817, asked whether the `reverse` inside
wsf-exhaust is the stall's reverse: *"we can't derive this yet. building a reversal producer is the
next step."*

The 11:34:00 case is what it has to satisfy. Joe: *"11:34 is dr -1. at ~11:32, ws1r stalled and
reversed. this state should be carried forward to the 11:34."* Carry-forward has no window — hold
the last state until the next one replaces it.

The number that proves that reversal already exists and is already thrown away: at 11:33:30 ws1r's
quadratic bends +17.65 under a downward read. `momo()` calls that bar `curl`; `momo_g` gate 2
rejects it and returns `none`, discarding the +17.65. Getting that number OUT of the function is
what `docs/handover_momo_refactor.md` is for, and it is why the refactor comes before the reversal
producer.

**The wsf stall.** Joe 0817: *"domTF and wsf stall logic are the same. the only difference would be
in the sampling interval - less width for smaller TFs."* The producer `jig.stall_mask` already
exists and is the same code. The sampling width for TF1-8 is UNSET; Joe: *"we'll need to tune it
based on the results. I don't know what results I'm looking for yet."*

## where to start

1. Read `docs/ws-finisher_spec.md` top to bottom. It carries Joe's words verbatim.
2. Do the momo refactor first — `docs/handover_momo_refactor.md`.
3. Then the reversal producer, tested against 11:32 on ws1r.
4. Then ask Joe for the sampling width, or propose one anchored to a measurement — never to a
   preference.

## house rules that apply here

- Report one column, top to bottom. Joe: *"I need a report that I scan from the top to the bottom,
  without having to look at a 2nd page that is bolted onto the table."* Every figure goes in a
  table, never inline in a bullet.
- Never dress up a result. State the before number and the after number.
- Never coin a name for a mechanic. Use Joe's word or ask him for one.
- Stop BEFORE an unplanned decision, not while running it.
- No cap, horizon, window or truncation anywhere unless Joe specified it.
- Hit a target with Joe's mechanisms only. If it cannot be hit, say why. If it can, say what you
  want to change — never apply it, never dump the sweep.
