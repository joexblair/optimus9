# THE ws1-ANCHORED LINEAGE — BUILT 1006, HALTED ON ONE DEFINITION

Joe's spec, 1006, verbatim:

> *"for the lineage to qualify legal, it needs to be measured from ws1 and jump no more than 2 higher
> TFs to find the next TF with momentum"*
> *"TF numbers. eg, ws1 can only look to ws2 and ws3 for a baton pass"*
> *"os_legal_succ should be a confirmation of the lineage - if its 1, we can act on os_stalled_now and
> os_new_stalls"*
> *"I know the spec doesn't include ws1r at the moment, but this example shows me that we need it as
> an anchor"*

## WHAT IS BUILT

| piece | where | state |
|---|---|---|
| `LIN_HOP` = 2, `LIN_ANCHOR` = ws1, `LIN_TF` = ws1..ws12 | `octosig_db.py` | built |
| `lineage(mt_at)` — walk up from ws1, hop <= 2, repeat | `octosig_db.py` | built |
| `r_band(v, d)` — 'O' oob / 'x' between fences / '.' in-fence, dr-sided | `octosig_db.py` | built |
| `baton.MT12` — mom-true over ws1..ws12, `TFS` untouched | `baton.py` | built |
| 18 new columns | `octosig_rulings` | ALTERed in, populated |
| 09-25 smoke build, 39 rows | knob key `...\|lineage-ws1` | done |
| 12-day rebuild | — | **NOT RUN — held on the question below** |

`baton.py`'s own report is **byte-identical** before and after the MT12 addition (225 lines, diff
rc=0). `TFS` stays `range(3, 24)`, so `os_stalled_n`, `os_momtrue_n`, the "of 21" denominator and the
baton chain did not move.

## THE NEW COLUMNS

| column | what it holds |
|---|---|
| `os_lin_chain` | the realised walk, e.g. `ws1 > ws3` |
| `os_lin_top` / `os_lin_len` / `os_lin_broke_at` | where it reached, how many TFs, the TF it could not hop past |
| `os_lin_mt` / `os_lin_mt_hi` | every mom-true TF in ws1..ws12, and the highest |
| `os_legal_succ` | REDEFINED — 1 = the chain reached `os_lin_mt_hi`, 0 = momentum stranded above a gap > 2, NULL = no mom-true TF at all |
| `os_r_ladder` | 12 characters, ws1..ws12: `O` oob, `x` between 83 and 85, `.` in-fence |
| `os_r_ws1` / `os_r_oob_top` / `os_r_between_n` | the anchor's r, the highest oob TF, the count in the band |
| `os_casc_str` | the Mage cascade ws1..ws12 as text, 1 dp, comma separated |
| `os_casc_mid_end` | mean(ws3,ws4) minus mean(ws1,ws12). NEGATIVE = the matryoshka V |
| `os_casc_fast` / `os_casc_slow` | ws3-ws1 and ws11-ws6 |
| `os_casc_spread` / `os_casc_argmin` / `os_casc_argmax` / `os_casc_monotone` | the ladder's shape |

Anchor for all of them: the **routing anchor** — the lookback-g5extrema bar, or the fwd-g5extrema
bar when the lookback found none. The same bar mtd and branch D read.

## THE TWO BARS JOE READ

### 11:28:15, anchor 11:27:10, dr +1

| TF | r | band | mom-true | Mage |
|---|---|---|---|---|
| ws1 | 79.89 | . | Y | 102.42 |
| ws2 | 56.57 | . | - | 111.68 |
| ws3 | 80.64 | . | Y | 112.80 |
| ws4 | 76.89 | . | - | 125.44 |
| ws5 | 68.07 | . | - | 125.36 |
| ws6 | 81.99 | . | - | 113.85 |
| ws7 | 86.94 | O | - | 108.65 |
| ws8 | 94.40 | O | Y | 113.13 |
| ws9 | 97.14 | O | Y | 109.80 |
| ws10 | 83.27 | x | Y | 114.78 |
| ws11 | 74.54 | . | Y | 117.74 |
| ws12 | 73.01 | . | Y | 113.16 |

Joe's read: *"ws9 oob, ws10 is between ex-fence and oob, and ws11 and ws12 are infence"* — **exact
match on all four lines**, at the anchor AND at os_ts.

Joe's read of the lineage: *"my view sees 11:28's lineage incrementing in steps of 1 and 2 (legal)"*.
The built chain is `ws1 > ws3`, `os_legal_succ` 0 — ws3 to ws8 is a 5-TF gap in mom-true.

### 09:32:00, anchor 09:28:05, dr +1

| TF | r | band | mom-true | Mage |
|---|---|---|---|---|
| ws1 | 93.72 | O | Y | 106.90 |
| ws2 | 54.88 | . | Y | 94.86 |
| ws3 | 45.57 | . | - | 87.82 |
| ws4 | 50.80 | . | - | 89.92 |
| ws5 | 48.65 | . | - | 95.95 |
| ws6 | 48.55 | . | - | 101.01 |
| ws7 | 48.03 | . | - | 101.33 |
| ws8 | 38.80 | . | - | 102.29 |
| ws9 | 52.68 | . | - | 108.04 |
| ws10 | 61.80 | . | - | 113.99 |
| ws11 | 74.82 | . | - | 115.60 |
| ws12 | 79.77 | . | - | 110.51 |

Joe's read: *"ws1 is the strongest line, so market reverses because ws2 and ws3 are infence"* — the
band column agrees, ws1 is the only `O` and ws2/ws3 are `.`.
The built chain is `ws1 > ws2`, `os_legal_succ` 1 — because **momo_g_why calls ws2 mom-true at r
54.88**.

## THE HALT

Two readings of *"the next TF with momentum"* are both defensible and they disagree:

| reading | what it is | 09:32 chain | 11:28 chain |
|---|---|---|---|
| **A — mom-true** | `momo_g_why` state in (`momo`, `curl`); the project's existing definition everywhere | `ws1 > ws2` | `ws1 > ws3` |
| **B — the r band** | r at or beyond the ex-fence (83 / 17); the words Joe used in both reads | `ws1` | `ws1` |

Measured over 09-25, 39 octo-sigs: **the two chains are identical on 14 rows and differ on 25.**

Neither reproduces *"11:28's lineage incrementing in steps of 1 and 2"*. Under A the ws1 walk stops
at ws3; under B it never leaves ws1. The contiguous run Joe is describing at 11:28 is **ws8-ws9-ws10-
ws11-ws12** — the top of the ladder, not a walk from ws1.

**Open for Joe's ruling:**
1. Is "momentum" in the lineage mom-true (A), or the r band (B), or a third thing?
2. At 11:28 the picture he is reading sits at the oob line and its peers, not at ws1. Is the lineage
   anchored at ws1 ALWAYS, or anchored at ws1 only when ws1 is the oob line?

Both readings are banked as columns (`os_lin_mt` for A, `os_r_ladder` for B) so either answer is a
query, not a rebuild.

## ALSO HELD

Joe 1006: *"a logic update is needed for the mech (09:32)"*, referring to the matryoshka read. The
rule itself has not been named. `os_mage_net` is **unchanged**; the shape is banked as data
(`os_casc_*`) and nothing reads it yet.

`os_casc_mid_end` on the two bars: 09:32 **-19.83** (the V, middle below the ends), 11:28 **+11.33**
(the inverse). Banked, not acted on.

## LAST, AT JOE'S WORD

The forward-walk mech — walk until the oob line stalls, retest its peers, and if the picture is
unchanged place a signal on the next g5Mage and g15Mage same-side oob reversing. Joe 1006: *"leave
this mech-build to last. build everything else, then we'll carefully craft it so that it matches my
vision"*.

---

# JOE'S ANSWER, 1006 — MOMENTUM IS A STATE, THE LINEAGE IS A TIME WALK

> *"momentum is a state"*
> *"per line: an `r` line either has it or it doesn't, based on the established momentum machine's mechs"*
> *"per collective: momentum is held by an `r` line as the rider of momentum, and collective momentum
> is lost when the {riderTF +2} TFs have not proven strong enough to exit the the fence at the moment
> when riderTF has stalled"*

| question | settled |
|---|---|
| per-line momentum | **mom-true** — `momo_g_why` state in (`momo`, `curl`) |
| the r band | **not momentum** — it is the fence-exit proof. oob = exited, 83-85 = might exit, in-fence = too weak |
| the lineage's shape | **a time walk**, not a one-bar ladder read |
| the loss test | riderTF **stalls** AND {riderTF, +1, +2} have not exited the fence |

The snapshot lineage built earlier in this file answers "what does the ladder look like now". It does
not answer "who holds momentum and did it get passed". **`os_legal_succ` as built measures nothing
Joe has described.**

The lineage and the mech Joe held to last are the SAME machine. *"walk the signal forward until ws9
(the oob line) is stalled, then retest its peers"* IS the collective-loss test.

## JOE'S THREE STEPS vs THE TAPE — 09-25

| Joe's step | the event on the tape | tape ts | Joe's ts | Joe's offset |
|---|---|---|---|---|
| ws1 printing mom-true | ws1 mom-true ON at dr +1, r 81.05 | **10:27:05** | 10:24 | 3.1 min early |
| ws2 is oob | ws2 first `. -> O`, r 85.46 | **10:28:00** | 10:32 | 4.0 min late |
| ws4 is mom-true | ws4 mom-true ON, r 50.00 | **10:27:05** | 10:32 | 4.9 min late |
| ws4 is oob | ws4 first `. -> O`, r 86.92 | **10:40:00** | 10:44 | 4.0 min late |
| ws6 is mom-true | ws6 mom-true ON, r 46.38 | **10:40:40** | 10:44 | 3.3 min late |

Every step confirmed. dr flipped from -1 to +1 between 10:26:10 and 10:27:05, and ws1, ws2, ws3, ws4
all printed mom-true on that same bar — the leg starts at the dr flip, not at ws1 alone.

At 10:32:00 exactly ws2 reads 83.91, the 83-85 band. It chatters in and out of oob from 10:28:00 to
10:34:45. First crossing is the event; the exact second is not.

## THE WHOLE dr +1 LEG, 10:27:05 -> 11:30:00

| ts | event | r |
|---|---|---|
| 10:27:05 | ws1, ws2, ws3, ws4 mom-true ON | 81.05 / 80.59 / 79.26 / 50.00 |
| 10:28:00 | ws1 oob, ws2 oob | 91.25 / 85.46 |
| 10:30:25 | ws3 oob | 85.25 |
| 10:30:45 | ws5 mom-true ON | 51.31 |
| 10:40:00 | ws4 oob, ws8 mom-true ON | 86.92 / 50.04 |
| 10:40:40 | ws6 mom-true ON | 46.38 |
| 10:48:00 | ws7 mom-true ON | 53.19 |
| 10:50:00 | ws5 oob | 92.60 |
| 10:51:05 | ws9 mom-true ON | 58.02 |
| 10:54:00 | ws6 oob, ws10 mom-true ON | 88.99 / 47.21 |
| 11:01:40 | ws11 mom-true ON | 49.60 |
| 11:04:00 | ws8 oob | 87.91 |
| 11:05:00 | ws7 oob | 90.91 |
| 11:12:00 | ws12 mom-true ON | 57.86 |
| 11:15:00 | ws9 oob | 93.90 |

## THE PASS, TESTED ON EVERY oob CROSSING IN THE LEG

| TF exits the fence | ts | TF+1 mom-true | TF+2 mom-true | pass within +2 |
|---|---|---|---|---|
| ws1 | 10:28:00 | ws2 Y | ws3 Y | yes |
| ws2 | 10:28:00 | ws3 Y | ws4 Y | yes |
| ws3 | 10:30:25 | ws4 Y | ws5 Y (+20 s) | yes |
| ws4 | 10:40:00 | ws5 Y | ws6 Y (+40 s) | yes |
| ws5 | 10:50:00 | ws6 Y | ws7 Y | yes |
| ws6 | 10:54:00 | ws7 Y | ws8 Y | yes |
| ws8 | 11:04:00 | ws9 Y | ws10 Y | yes |
| ws7 | 11:05:00 | ws8 Y | ws9 Y | yes |
| ws9 | 11:15:00 | ws10 Y | ws11 Y | yes |

**Nine of nine.** The cascade never broke in this leg. The successor is sometimes ahead of the oob
crossing (ws4 by 55 s, ws7 by 2.0 min) and sometimes behind it (ws5 by 20 s, ws6 by 40 s) — the two
are near-simultaneous, not strictly ordered.

## WHAT THIS TRACE DOES NOT COVER

- the window is 10:00:00 to 11:30:00, which I chose. The octo-sig is at 11:28:15, so the **forward
  walk to ws9's stall runs past the end of it.** The loss test cannot be read from this file.
- ws10/ws11/ws12 fence state after 11:30 is not in it either.

Full event trace, 514 events, every mom-true on/off, every band crossing, every stall onset:
`1006_lineage_trace_0925.txt`. Producer: `1005_scoring/lineage_trace.py`.

---

# THE WALK COMPLETED — 09-25, 10:27:05 TO A TRADE SIGNAL

Joe 1006: *"it's important that the lineage walks TFs upward, never backwards"* — banked in
`octosig_db.py:LIN_HOP`. The candidate set for a rider on ws{t} is exactly {ws{t+1}, ws{t+2}};
every lower TF is out of the walk for good, including ones still sitting oob.

Producers: `1005_scoring/walk_after_1115.py` (env `W_FROM`, `W_RIDER`),
`1005_scoring/signal_after_loss.py` (env `W_LOSS`).

## THE LADDER CLIMB

| ts | event | r |
|---|---|---|
| 10:26:10 -> 10:27:05 | dr flips -1 -> +1; ws1, ws2, ws3, ws4 all print mom-true | 81.05 / 80.59 / 79.26 / 50.00 |
| 10:28:00 | ws1 oob, ws2 oob | 91.25 / 85.46 |
| 10:30:25 | ws3 oob | 85.25 |
| 10:40:00 | ws4 oob | 86.92 |
| 10:50:00 | ws5 oob | 92.60 |
| 10:54:00 | ws6 oob | 88.99 |
| 11:04:00 | ws8 oob | 87.91 |
| 11:05:00 | ws7 oob | 90.91 |
| 11:15:00 | ws9 oob | 93.90 |
| **11:28:15** | **the octo-sig fires** — ws9 oob, ws10 in the 83-85 band, ws11/ws12 in-fence | — |
| 11:30:00 | ws10 oob — the last successful pass | 88.17 |
| **11:48:00** | **ws10 stalls, ws11 69.31 and ws12 74.36 both in-fence -> COLLECTIVE MOMENTUM LOST** | 78.97 |

## THE LOSS CALL — BOTH READINGS AGREE, 2.1 min APART

Joe's rule: *"collective momentum is lost when the {riderTF +2} TFs have not proven strong enough to
exit the fence at the moment when riderTF has stalled"*. Two readings of *"have not proven ... at the
moment"*:

| reading | rider | stalls at | ws+1 / ws+2 at that bar | verdict |
|---|---|---|---|---|
| snapshot at the stall bar | ws9 | 11:50:05 | ws10 60.90 `.` / ws11 66.84 `.` | LOST |
| "have proven" = during the rider's reign, so ws10 took the baton at 11:30:00 | ws10 | **11:48:00** | ws11 69.31 `.` / ws12 74.36 `.` | LOST |

ws11 and ws12 never reach oob in this dr +1 leg. Their first oob crossings are 13:00:00 (ws12) and
13:46:05 (ws11), both at dr -1. **This example does not force the ruling** - it only says the
continuation reading is the earlier call.

ws10 at its stall is still mom-true and already back in-fence at 78.97 after peaking at 88.17. ws11
and ws12 are mom-true with neither out of the fence - Joe's "waning momentum" picture, one rung above
where he read it at 11:28.

## THE TRADE SIGNAL

Joe's rule: *"a signal is placed on the next g5Mage and g15Mage same-side oob reversing"*. The
"reversing" test is `_mage_rev(line, wob_n)` with `REV_WOB` = 2 bars = 10 s at the 5 s grid - the
turn is confirmed only after 2 consecutive same-direction steps, NaN counting as flat and extending
the run. It returns a SIGNED flag, so the turn has a direction.

| reading of "same-side" | ts | dr | g5Mage | g15Mage | REV signed | after the loss |
|---|---|---|---|---|---|---|
| **A** - both Mages on the same side as each other, read at the current dr | **12:14:10** | -1 | 8.94 | -18.20 | **+1** (turned UP) | 26.2 min |
| **B** - the same side as the leg that just died (high, >= 85) | **12:30:20** | -1 | 92.17 | 89.88 | **-1** (turned DOWN) | 42.3 min |

BOTH readings are directionally coherent, each out of its own fence:

| reading | ts | the fence both Mages are outside | g5Mage turns | out of that fence |
|---|---|---|---|---|
| A | 12:14:10 | low, <= 15 (g5 8.94, g15 -18.20) | **UP**, REV +1 | yes |
| B | 12:30:20 | high, >= 85 (g5 92.17, g15 89.88) | **DOWN**, REV -1 | yes |

So the choice between them is not settled by direction - both are a genuine reversal out of the fence
they sit outside. They differ in WHICH fence, 16.2 min apart, and reading B is on the side the dead
leg was climbing.

**dr flipped +1 -> -1 at 12:13:55**, between the loss call and both signal bars. The loss was declared
on the dr +1 leg and both candidate signals land after the flip. Whether the walk survives a dr flip
is not ruled.

## NEITHER SIGNAL EXISTS IN octo-freedom TODAY

09-25 has **39** `WALK FIRES FROM` rows. Between 11:28:15 and 13:40 there are only:

| octo-sig |
|---|
| 11:28:15 |
| 13:33:40 |
| 13:37:05 |

| gap | minutes |
|---|---|
| loss 11:48:00 -> next existing octo-sig 13:33:40 | **105.7** |
| reading A 12:14:10 -> 13:33:40 | 79.5 |
| reading B 12:30:20 -> 13:33:40 | 63.3 |

**The walk fires in a 105.7-minute window where octo-freedom is silent.** That is the whole point of
the mech, and it is the first measured evidence of it.

## NOT SCORED, AND WHY

No MAE/MFE on 12:14:10 or 12:30:20. The signal's SIDE is not ruled. dr is -1 at both bars, so the
dr-bias frame would read LONG, but this is a new signal type and Joe has not said whether it inherits
that frame, the `sneaky-trade-1` frame, or something else. Scoring it under a guessed side would
manufacture the result.

## OPEN FOR JOE

1. the loss reading - snapshot at the rider's stall, or "has proven during the reign" (the baton
   moves to ws10 at 11:30:00 and the call comes 2.1 min earlier)
2. "same-side" - both Mages agreeing with each other at the current dr (12:14:10), or the side of the
   leg that just died (12:30:20)
3. does the walk survive a dr flip? The flip at 12:13:55 sits between the loss and both signals
4. what side does this signal take?
