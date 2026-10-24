# `v4core` — Joe's handover, and what is settled

Joe 1023 handed this over as one message after the 1023 causality repair. His spec is reproduced
VERBATIM below and is never retyped in my own words; the rulings and the open items sit under it.

BUILT AND BANKED. `v4_core_arm.py` holds the arm, `v4_machine.py` the chain. The walkthrough he
supplied is one day of estimated times — his words: *"all numbers
estimated. time estimates are +/-5 minutes"* and *"my times are always estaimate"* — so the
MECHANIC comes from his words and no knob is ever fitted to a timestamp he quoted.

## 1. The spec, verbatim

```
`v4core` mech:
STEP0 IF there is "no open trade": walk until ws1b is oob on target-side, then walk to (ws2r oob AND ws3r oob) AND (ws1Mage or ws2Mage are same-side past 5/95)
-"same-side past 5/95" means <5 if target-side is low, >95 if target-side high
-"no open trade" will fire after a stop, and at the start of the machine

STEP1 on trade open, walk until ws1b is oob on target-side

STEP2 IF (ws2r or ws3r are oob) AND (ws1Mage or ws2Mage are same-side past 5/95), the rev-trade is armed

STEP3: # disabled: pre-lineage test. ws1-3
STEP4 walk `v4-lineage` to exhaustion
STEP5 rev-trade and disable the arm
```

## 1a. STEP0's `AND` is deliberate, and he gave the mechanism

The difference between STEP0 and STEP2 is his and is not a typo: STEP0 requires `ws2r oob AND ws3r
oob`, STEP2 requires `ws2r or ws3r are oob`. Joe 1023, verbatim:

> STEP0 is specifically `AND` to avoid re-entering mid cycle and creating a second stop

> context: ws3r and ws2r represent the humans' momentum cycles - when they are oob, a cycle is
> cycling. if one of these moments creates a stop, I suspect an unstable market. waiting for
> (ws2r AND ws3r) feels like the safest option we have for a profitable reentry.

> AND vs OR for step 0 needs to be a knob

`V4CORE_STEP0_JOIN` 'and' is that knob. STEP2's join stays `or` and is NOT knobbed - he asked for
step 0.

### A measurement I got wrong, and the correction

I tested his twelve walkthrough arms against STEP0's `AND` and reported that only 5 of 12
reproduced, against 11 of 12 under `OR` - and put that to him as a spec question. That was a
CATEGORY ERROR. STEP0 fires only when there is no open trade, which in his walkthrough is the
chain start and nothing else; every later arm is STEP2's rev-trade arm, where `or` is already the
rule. Read per step, his spec reproduces his whole day:

| the arm | which step | the rule | result |
|---|---|---|---|
| 2026-09-01 17:30 | STEP0, the chain start | `AND` | ws2r 96.23 high AND ws3r 86.18 high - passes |
| the other 11 | STEP2 | `or` | 11 of 11 on the side his direction implies |
| 2026-09-02 10:26 | STEP2 | `or` | correctly NO arm - both Mages fail `> 95` |

The seven `AND` failures I reported were all the same shape - one of ws2r/ws3r oob, the other in
bounds - and are exactly the mid-cycle re-entries his reasoning excludes.

## 2. The lines it reads, SETTLED 1023

| the line | the spec | value mode |
|---|---|---|
| `cws1b` | `bb` 49 / 0.95 / close — the Bollinger-position line | **closed** |
| `cws1r`, `cws2r`, `cws3r` | the DB `mech_lines('wsf')` r row, `7\|5\|8` in Joe's notation | **closed** |
| `cws1Mage`, `cws2Mage` | the DB `mech_lines('wsf')` Mage row, `bb` 38 / 0.93 | **closed** |

- `ws1b` CONFIRMED. Joe 1023: *"yes to ws1b"*. No v4 mech had read the `b` role before.
- IT IS CLOSED TOO, Joe 1023: *"ws1b should be mode:closed"*. It was banked as emerging on 1023
  and that was wrong by one turn: at four of the twelve arms in his walkthrough emerging reads
  `ws1b` IN BOUNDS, and closed puts three of those four on an oob side - 01:29 goes 22.04 ib to
  5.24 low, 07:13 goes 84.99 ib to 89.44 high, 16:17 goes 64.88 ib to 108.44 high. STEP0's and
  STEP1's first gate would have failed at those bars. The `c` prefix on the name follows his own
  naming for the closed set; he named five lines and this is the sixth.
- THE `c` PREFIX IS HIS: *"we create 5 new lines (cws1-3r and cws1-2Mage) as closed and assign
  them to v4core"*.
- THE SPEC IS THE DB ROW, NOT THE BANK. Joe 1023, asked which of the two: *"db row"*. The bank is
  `6|6|8` and the DB row is `7|5|8`; the DB row is the one that reproduced his TV walkthrough to a
  mean gap of 0.35 against emerging's 4.21, so `v4core` reads the lines he actually looks at.
- THE REST OF THE MACHINE STAYS ON EMERGING. Joe 1023: *"I'm a small and many kind of guy - it's a
  business model that always wins for me"*. The blanket shift to closed took 210 trades against
  emerging's 543, so emerging stays and the closed lines are `v4core`'s alone.
- all five arrays are already cached; nothing needs building.

## 3. The 5/95 fence

`V4CORE_MAGE_FNC` 5.0, mirrored to (5.0, 95.0), tested by `K.past_v4core_mage(v, side)`. One knob
and `100 - knob`, the same form as `OOB_FNC` 15 and `MID_FNC` 50, because two separate knobs could
drift apart and one cannot.

- Joe 1023: *"fence knob: yes"*.
- THE NAME IS MINE and deliberately not "oob". `oob` is ALWAYS 15/85; this is a tighter fence on
  the Mage lines for one mech. Joe has not named it.
- STRICTLY past, which is his wording: exactly 5.0 or 95.0 does not pass.
- HELD AT 5, NOT DEFENDED. Joe 1023: *"5/95 was my eyeballing. I wouldn't change it before walking
  the full 6 day window, but it's an option"*. It is a sweep candidate.
- the second sweep candidate is the SOURCE, same hold: *"the other sweep option is the source: hl2
  beats close at 10:26. the same wait applies - no changes until the full walk"*.

## 4. STEP3 is not built

His line is `STEP3: # disabled: pre-lineage test. ws1-3`. It is left OUT of the code entirely
rather than built dormant — a parked mech gets no code and no spec text beyond this note.

## 5. The walkthrough, measured against his TV values

His quoted values are CLOSED-bar values. Measured 1023 at the five points he named, against the DB
`wsf` specs:

| the arm | the line | Joe TV | emerging | gap | closed | gap |
|---|---|---|---|---|---|---|
| 2026-09-01 17:30 | ws3r | 86.00 | 89.31 | +3.31 | 86.18 | +0.18 |
| 2026-09-01 17:30 | ws2r | 96.00 | 95.55 | -0.45 | 96.23 | +0.23 |
| 2026-09-01 17:30 | ws1Mage | 100.00 | 96.02 | -3.98 | 100.16 | +0.16 |
| 2026-09-01 18:21 | ws3r | 13.00 | 13.69 | +0.69 | 13.69 | +0.69 |
| 2026-09-01 18:21 | ws2r | 10.00 | 10.44 | +0.44 | 10.24 | +0.24 |
| 2026-09-01 18:21 | ws1Mage | 9.00 | 12.93 | +3.93 | 9.01 | +0.01 |
| 2026-09-01 19:53 | ws3r | 12.00 | 12.85 | +0.85 | 12.79 | +0.79 |
| 2026-09-01 19:53 | ws2r | 10.00 | 13.89 | +3.89 | 10.29 | +0.29 |
| 2026-09-01 19:53 | ws1Mage | 4.00 | 13.60 | +9.60 | 4.44 | +0.44 |
| 2026-09-02 01:29 | ws2r | 10.00 | 10.35 | +0.35 | 10.35 | +0.35 |
| 2026-09-02 01:29 | ws1Mage | 3.80 | 19.72 | +15.92 | 3.84 | +0.04 |
| 2026-09-02 10:26 | ws1Mage | 93.00 | 85.87 | -7.13 | 92.21 | -0.79 |

| the summary | emerging | closed |
|---|---|---|
| mean absolute gap, all 12 | 4.21 | 0.35 |
| mean absolute gap, ws1Mage alone | 8.11 | 0.29 |
| largest single gap | 15.92 | 0.79 |

Two of his five arms pass the 5/95 gate on closed and fail it on emerging — 19:53 and 01:29, both
on `ws1Mage`. That is the whole reason the `c` lines exist.

### The two arms he ruled on directly

- **18:21** — his quoted `ws1Mage:9` does NOT pass a strict `< 5`, and 9.01 closed confirms the
  reading. Joe 1023: *"use ws2Mage at 18:22 - ws2Mage is in the spec"*. `ws2Mage` closed is -1.52
  there, so the arm stands on `ws2Mage`. His own note covers it: *"ws2Mage also qualifies, but we
  only need 1 mage to carry the decision"*.
- **10:26** — he flagged it himself as *"contentious - ws1Mage is 93 on TV"*. Closed reads 92.21,
  which fails `> 95`, and `ws2Mage` closed is 73.76, which also fails. Joe 1023: *"if a sweep
  can't improve it then it's stopped"*. So no arm there, and no fence change to make one.

## 5a. THE SECOND ARM — BANKED 1024

Joe 1024, verbatim:

```
add a second v4core arm: if ws1r is oob on target side, min dwell 18 bars, and ws1Mage is same-side
oob, and any TWO of ws4-8r are same-side oob, arm.
```

His example fires, from his own charts: *"0334, lineage carries to 0337 exhaust / 0624, lineage
exhaust at the same bar / 1349, lineage exhaust at the same bar / 1549, lineage exhaust at the same
bar"*, with *"I've excluded the ws2r or ws3r armings that fire on the same (ws1 + 2more) bars"*.
He then dropped two of them: *"drop '06:24 and 15:49'"*.

### The same mech as built

```
STEP1's cws1b oob gate must be AT OR BEFORE the arm bar
-"yes. apply this to the existing mech as well"                                  [MOD 1024]
--it used to `continue` past the gate bar without testing an arm there, so the gate
  bar could never also be the arm bar and EVERY arm was at least one bar late
--on 09-01 all five second-arm candidates have cws1b oob ON their arm bar
--it also moved three STEP2 arms earlier: 07:23:00, 17:59:00, 19:57:00
the SECOND ARM, STEP2's sibling - "is it STEP2's sibling - yes"
-cws1r oob on the target side
--the oob run must REACH ARM2_DWELL 18 bars, so the earliest arm is bar 18 of the run
---his 03:34:25 and 13:50:25 both land on bar 18 of their run
-AND cws1Mage same-side oob
-AND at least ARM2_POOL_MIN 2 of cws4r..cws8r same-side oob
-EVERY LINE IS A CLOSED c-LINE - "everything is measured on closed bars"
--cws1Mage is the clause that moves: at 06:24 it reads -5.60 and LOW oob while the
  EMERGING ws1Mage reads 23.33 and is not
-either sibling may fire; `arm` takes whichever lands first, and reports `which`
lineage is entered at CORE_LIN_ENTRY_TF 4 - HIS KNOB AND HIS NAME
-"maybe setting the entry TF to {knob:4,'V4_CORE_LIN_ENTRY_TF'} will settle it"    [MOD 1024]
--it REPLACED his own earlier "start from ws1. most of them are on the pivot, so
  near-instant exhaust is typical behaviour", which he then caught: "there's a
  miswiring somewhere. the A trade mech picked 0116 as the arm and walked it to 0137.
  this B trade has exhausted immediate"
--at the 01:14:25 arm the emerging ws2r is 21.11 against the 20 fence, so a ws1 start
  died at its first hand-off with EXHAUST at 01:16:20. The oob at that bar is ws1r
  10.14, a HOLE at ws2r 21.11 and ws3r 15.74, then ws4r 7.94 and ws5r 9.02
--with the entry at ws4 that arm walks to 01:37:10, which matches the A-path backstop
  trade EXACTLY
-IF cws{CORE_LIN_ENTRY_TF}r is NOT oob at the arm bar, it is an immediate exhaust    [MOD 1024]
--"if ws{V4_CORE_LIN_ENTRY_TF}r is not oob, then it is an immediate exhaust"
--read at the ARM BAR, which is the bar the hand-off happens on
--WHY ws4 AND NOT THE LOWEST OOB RUNG, his reason: "I've chosen ws4 specifically to
  align with the new 'ws4r to ws1Mage ib mech', which we'll insert immediately before
  exhaust (not yet, but soon). what you're seeing in ws5 and ws6 are the unwinding of
  the higher TFs momentum, and I've got a plan brewing to teach the new mech how do
  ride it without the signal delays we typically inherit by passing the baton higher"
```

### What it did to 2026-09-01

| the read | ARM2 off | ARM2 on |
|---|---|---|
| trades | 16 | 14 |
| by core | 9 | 11 |
| by backstop | 4 | 2 |
| by saviour | 2 | 0 |
| shared with the other arm | - | 11 |
| trades the second arm dropped | - | 5 |
| trades only the second arm has | - | 3 |

| the arm | the entry TF read | the outcome |
|---|---|---|
| 2026-09-01 01:14:25 | ws4r oob | walks to EXHAUST 01:37:10 - matches the A-path trade |
| 2026-09-01 03:34:25 | ws4r 76.13, NOT oob | immediate exhaust, opens 03:34:30 |
| 2026-09-01 06:57:25 | ws4r 28.58, NOT oob | immediate exhaust, opens 06:57:30 |
| 2026-09-01 13:50:25 | ws4r 78.50, NOT oob, but ws5r 91.71 IS | immediate exhaust, opens 13:50:30 |

ws4r never reaches oob within 5 minutes of any of the three immediate cases, so the exhaust is the
honest read rather than a near-miss. At 13:50:25 the oob sits one rung up at ws5r 91.71 and the
entry at 4 declares exhaust anyway - which is his deliberate choice, quoted above.

### Scored by `sweep-pivots`, the machine's own trades

The three immediate-exhaust opens, scored against their own swing - the first time `sweep-pivots`
has been run on machine events rather than on the in-test chain's:

| the open | % off the pivot | the share of the leg behind |
|---|---|---|
| 2026-09-01 03:34:30 | -0.006% | 0.007 |
| 2026-09-01 06:57:30 | +0.359% | 0.205 |
| 2026-09-01 13:50:30 | -0.185% | 0.065 |

Two of the three sit inside 0.2% of their pivot with almost nothing of the swing given away, which
is what he predicted when he ruled the near-instant exhaust acceptable.

## 6. Open, and NOT decided by me

| item | what is missing |
|---|---|
| the `v4core` arm's own measurement | the `v4core`-lines-closed arm has never been measured. Joe 1023: *"noted - that's next"* |
| the 6-day walk | the fence and the source are both held until it runs |

Nothing else is open. The side question is settled - see below.

## 6a. STEP0 IS NOT A SEPARATE MECH — SETTLED 1023

It is STEP1 and STEP2 run against an **invisible LONG or SHORT**. Joe 1023, verbatim:

> as the first trade, the arm comes from a non-existent/invisible LONG trade, so the arm happens at
> 17:20 when cws1b prints 101.9

> the invisible walk continues to the v4core event. both cws2r and cws3r are oob, so lineage is
> passed TF3

> lineage has no baton receiver, so exhaust is printed immediately

and, on writing it down:

> be sure to swap "LONG" with "LONG or SHORT" when you write it to the spec

So BOTH invisible trades run, one per side, which is the same thing as his earlier *"scan both
sides as you walk"*. There is no separate STEP0 code path:

| the invisible trade | its target-side | STEP1 waits for | the real trade it rev-trades into |
|---|---|---|---|
| an invisible LONG | high | cws1b high oob | a SHORT |
| an invisible SHORT | low | cws1b low oob | a LONG |

Whichever side's setup completes first sets the real trade, and the real trade is that invisible
one's rev-trade - which is exactly `low oob -> LONG, high oob -> SHORT`.

### Measured on his own leg, 2026-09-01

| his statement | measured | match |
|---|---|---|
| the arm at 17:20, cws1b prints 101.9 | 2026-09-01 17:20:00, cws1b 101.95 | YES |
| the invisible walk reaches the v4core event | 2026-09-01 17:30:00 | YES |
| both cws2r and cws3r are oob | cws2r 96.23, cws3r 86.18 | YES |
| so lineage is passed TF3 | both oob -> his tie-break to cws3r -> ws3 | YES |
| lineage has no baton receiver, exhaust immediately | NO - ws4 and ws5 both receive. 7 or 8 steps | **no** |

cws1b is high oob for exactly TWO bars there: 69.68 at 17:19:55, 101.95 at 17:20:00, 81.34 by
17:21:00. One closed-bar print.

THE WALK, AND HIS RULING ON IT. Under the banked `LIN_PASS` 'ib' the exhaust is 17:40:25 and the
SHORT opens 17:40:30; under his 1022 reversal-pass rule the exhaust is 17:40:55 and it opens
17:41:00. Shown both, Joe 1023: *"1741 is fine"*. So his walkthrough's 17:33 for this leg is
superseded by his own reading of the walk.

## 6b. The side at STEP0, SETTLED 1023

With no open trade there is no trade to take `target-side` from. Joe 1023, verbatim:

> scan both sides as you walk. when the setup prints, the lines will all be on either high oob or
> low oob. if low oob, open a LONG, if high oob, open a short

So STEP0 runs TWO hypotheses, one per side, and whichever completes first sets the side. `low oob
-> LONG`, `high oob -> SHORT` - the same polarity `v4-ws5rbackstop` already uses, where a HIGH oob
reversal spawns a SHORT and a LOW oob reversal spawns a LONG.

MEASURED ON ALL TWELVE ARMS, closed lines: every arm that fires lands on EXACTLY ONE side, that
side gives the direction he wrote, and zero arms qualify on both sides at once. The rule is not
contradicted anywhere in his day.

`target-side` therefore means two different things in his spec and both are correct in place:
- **STEP0** - the side being SCANNED. There is no trade yet, so it is the setup's own oob side.
- **STEP1 and STEP2** - the OPEN TRADE's target-side, high for a LONG and low for a SHORT.

That makes STEP1/STEP2 the MIRROR of STEP0: the setup shape that opened a LONG off low oob is the
same shape that, printing later on high oob, arms its reversal. One shape, either side.

## 7. Related

`v4_bank.md` (the board, `rev-trade`, the knobs) · `v4_lineage.md` (the baton chain) ·
`v4_saviour.md` (the open-trade verdict) · `v4_knobs.py` (the in-force copy, 29 knobs)
