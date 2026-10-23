# `v4core` — Joe's handover, and what is settled

Joe 1023 handed this over as one message after the 1023 causality repair. His spec is reproduced
VERBATIM below and is never retyped in my own words; the rulings and the open items sit under it.

NOT BUILT YET. This doc records the spec and the decisions so the build can start from a settled
brief. The walkthrough he supplied is one day of estimated times — his words: *"all numbers
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

Note the difference between STEP0 and STEP2, which is his and is not a typo: STEP0 requires
`ws2r oob AND ws3r oob`, STEP2 requires `ws2r or ws3r are oob`.

## 2. The lines it reads, SETTLED 1023

| the line | the spec | value mode |
|---|---|---|
| `ws1b` | `bb` 49 / 0.95 / close — the Bollinger-position line | emerging, the DB `wsf` row |
| `cws1r`, `cws2r`, `cws3r` | the DB `mech_lines('wsf')` r row, `7\|5\|8` in Joe's notation | **closed** |
| `cws1Mage`, `cws2Mage` | the DB `mech_lines('wsf')` Mage row, `bb` 38 / 0.93 | **closed** |

- `ws1b` CONFIRMED. Joe 1023: *"yes to ws1b"*. No v4 mech had read the `b` role before.
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

## 6. Open, and NOT decided by me

| item | what is missing |
|---|---|
| `target-side` at STEP0 | with no open trade there is no trade to take the side from. STEP0 walks "until ws1b is oob on target-side" — which side, before a trade exists, is unruled |
| the `v4core` arm's own measurement | the `v4core`-lines-closed arm has never been measured. Joe 1023: *"noted - that's next"* |
| the 6-day walk | the fence and the source are both held until it runs |

## 7. Related

`v4_bank.md` (the board, `rev-trade`, the knobs) · `v4_lineage.md` (the baton chain) ·
`v4_saviour.md` (the open-trade verdict) · `v4_knobs.py` (the in-force copy, 29 knobs)
