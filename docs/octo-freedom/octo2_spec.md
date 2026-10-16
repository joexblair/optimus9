# `octo2` — the spec

**Joe named it, 1016:** *"this is a new machine that we're building now, named `octo2`"*.

**Its status, Joe 1016:** *"bank this as our state and make the machine live"* — and, asked what
live meant: *"when I saidd make the machine live, I'm saying this is the machine we're going to
continue developing. for actual realtime testing, I'll refer to o9-live"*. So `octo2` is the
machine we develop on. It is not deployed anywhere.

**No P&L lives in it.** Joe 1016: *"I'm against brining pnl into a machine - you'll recall that it
somehow trips you up when we're improving mechs"*. `Octo2.gross()` returns a price percentage.
Cost, size, drag and net are computed in sweep and report scripts, never here. Position size and a
stop are o9-live's questions and Joe ruled them out of the machine: *"1: that's fine... 2; same
as 1"*.

---

## 1. WHAT IT IS — a side-event machine

**Joe's ruling, 1016:** *"the exits are the same as the entries in my eyes"* / *"I'm calling it"*.

    a LOW-side event   closes every open SHORT and opens a LONG
    a HIGH-side event  closes every open LONG  and opens a SHORT

**The side rule that forced the structure, Joe 1016:** *"because there was already an OPEN LONG
printing at 19:12, and 19:12 is low side, there is no action to take on the already opened LONG
trade. the only thing that interacts with a LONG is a high oob EXIT -this means your correction is
poisoned, because you weren't aware that the OPEN long can't be touched by a low-side signal. the
only thing the low-side signal can do is open a LONG trade"*.

**The side mapping, settled 1016.** Joe raised *"the turn-predictor might be inverted"*; asked
directly about the 2026-07-22 00:23 event he ruled *"it's a short trade, all calculations are on
the target side, which is low side for a SHORT trade"*. A HIGH-side event opens a SHORT. The frame
is the banked one: **dr +1 SHORT, dr −1 LONG**.

**The exit reason, Joe 1016:** *"I just saw that the colum is `the source`. that's counter intuitive
when you place it next to the exit. instead of `the source` coumn, create a `exit reason` column"*.
A trade carries `source` (the event that opened it) and `exit_reason` (the event that closed it,
stamped at the close). A report prints `exit reason` beside the exit, never `source`.

---

## 2. THE FILES AND WHAT EACH OWNS

| file | owns |
|---|---|
| `1005_scoring/octo2.py` | the walk — the trigger order, the standdown, the cap, the side rule, the dedupe |
| `1005_scoring/_conj.py` | the conjunction — its role map, span, the ws2/ws3 patch, the ws1Mage gate and its slack, and the x-cross lookback that consumes it |
| `1005_scoring/_bouncepred.py` | the `continuance` / `reverse` verdict on the FIXED two-offset grid (superseded as the default, kept for A/B) |
| `1005_scoring/_bp_g15.py` | the same verdict on the **g15Mage ib-cross grid — BANKED** |
| `1005_scoring/_lineage_conf.py` | lineage as a confluence verdict. It cannot return a bar |
| `1005_scoring/_momxfer.py` | the mom-xfer racer gate. **OFF by Joe's ruling** |
| `1005_scoring/_fill.py` | the maker-first fill model with a taker backup. A REPORTING module; the machine does not import it |
| `optimus9/analysis/jig.py` | every producer. Joe 1016: *"any producers need to be in the jig"* |

---

## 3. THE TRIGGERS, in the order they were built

**1. ws5Mage ENTERING oob, either side.** An entry, not a state — being in oob cannot re-trigger.
That mattered: a 40-second flicker became a second SHORT on 2026-07-22 before Joe accepted it
explicitly. On 2026-07-22 this trigger beat every gated turn-predictor by 6.24 hours and its signal
bar sat 0.75 min before the 19:13:15 L price pivot.

**2. the GATED TURN-PREDICTOR** — the conjunction with Joe's 1015 gate: *"the turn signal can only
fire if ws1Mage is same-side oob"*.

**The gate reads ws1Mage, not ws1r. Settled 1016.** Joe raised the inversion from *"the reversal
firing on a high ws1r signal"*; at the 00:22:00 fire the two lines disagree by 51.58 points —
ws1Mage 83.51, ws1r 31.93. Asked which line, he ruled: *"which line": ws1Mage, not ws1r"*.

---

## 4. `bounce-pred` — JOE'S NAME, JOE'S MECH

**His spec, 1016:** *"bake the `bounce-pred` mech - it's a last mile improvment that needs to slot
in directly after ws5Mage oob. -it will only fire when ws5Mage is oob, and will fire on each ws5Mage
reversing until `continuance` is no longer printed, ie `continuance` will flip to `reverse` --in our
07-22 00:23 to 01:08 EXAMPLE, the `continuance` events are 00:35, 00:55, and the `reverse` event
prints at ~01:08:45"*.

**The two verdicts, from his own description of the two reference bars:** *"T23 is when ws5Mage is
oob and starts bouncing on high oob while it has to wait for a higher TF to complete its journey to
ws5Mage oob side / T50 is when that bouncing stops - it's the pivot"*.

    continuance   the bouncing is still running. A higher TF has not finished its journey. WAIT
    reverse       the bouncing has stopped. This is the pivot. The entry is good

I had these the wrong way round once and it inverted the whole result.

**The signal is HELD until the reverse confirms, Joe 1016:** *"when 00:23 prints `continuance`, the
00:23 signal is held until `reverse` prints at ~01:08 (+ the additional 10 minutes need to confirm
the `reverse` signal). in this example, the SHORT opens at ~01:18"*. So the event bar is the
verdict's `known_at`, not the trigger bar.

**The measure, Joe 1016:** *"can you see that T23's 10 diff is noticably higher the its 7.5 diff,
while the T50's 10 diff is near or slightly lower than its 7.5 diff?"* — the SECOND DIFFERENCE
across the ws30→ws1 Mage ladder, in points. **A ratio was mine and is rejected:** Joe asked *"could
ratio be the wrong way to measure this?"* — it divides by a near-zero denominator, spanned −6.12 to
+10.37 at the reversals, and separated nothing.

**`bounce-pred` HAS PRIORITY OVER THE TURN-PREDICTOR. Joe 1016:** *"bounce-pred has prioirty over
turn-predictor"*. A turn-predictor event is held whenever ws5Mage is oob at the event bar.
His earlier wording — *"`bounce-pred` is not applied to a `turn-detection` event"* — is SUPERSEDED
and kept here so the change is legible. It let 2026-07-22 00:23:55 through unheld with ws5Mage at
102.92, HIGH oob, which is the event he then called out.

**The hold starts at the EVENT bar, not the conjunction's fire bar.** Joe named *"00:23"*, which is
the event bar 00:23:55; the fire was 00:22:00. Structural and stated: the event bar is the only bar
the hold can causally start from.

---

## 5. THE BANKED GRID — `g15ib`

**Joe's idea, 1016:** *"I have a further idea - instead of a fixed width, collect samples on each
g15Mage crossing back to ib (on the target side). the logic: we're sampling at locations that are
consistent within the market's cycles -this needs an arm - it can come from ws5Mage crossing to
target-side oob"*.

**Why it was worth building, measured before a line of it was written:** armed at the ws5Mage
HIGH-oob entry 2026-07-22 00:02:10, at the oob fence 85/15 with xwob 4 bars, **his two named
continuance bars ARE g15Mage HIGH→ib crosses, exact to the second** — cross 8 is 00:35:00 and
cross 9 is 00:55:00.

**The producer is the Jig's, Joe 0806:** `jig.oob_ib_cross(line, hi, lo, xwob)` at
`optimus9/analysis/jig.py:176`, which returns `(cross, conf, side)` with `conf` the bar the cross
becomes knowable. No new producer was needed.

**THE BANK, Joe 1016:** *"g15 ws5/fwd/ex/xwob1/step1 +173.9969% / bank this as our state and make
the machine live. no mom-xfer"*.

| knob | banked | what it means |
|---|---|---|
| `W_OCTO2_GRID` | `g15ib` | the hold is measured on the g15Mage ib-cross grid |
| `W_G15_SIDE` | `ws5` | the cross is on the side ws5Mage crossed to |
| `W_G15_PAIR` | `fwd` | the pair is THIS cross and the NEXT |
| `W_G15_FENCE` | `ex` | the ex-fence 83/17 |
| `W_G15_XWOB` | `1` | 1 bar = 5 s of IB hold for the cross to confirm |
| `W_G15_STEP` | `1` | one cross forward |

**Verified from the defaults alone, no env vars, 94 built days 2026-07-03 to 2026-10-04:**

| measure | value |
|---|---|
| gross | +399.7394% |
| trades | 1143 |
| drag at the banked 0.1975% per trade | 225.7425% = 56.5% of gross |
| **net** | **+173.9969%** |
| win rate | 72.1% |
| days positive | 63 of 94 |

**WHAT THE BANK RETIRES.** Under `g15ib` the two fixed offsets `W_BP_OFF_A` and `W_BP_OFF_B` are
NOT READ. The +7.5/+9.5 pair proposed on 94-day named-bar fidelity is **moot** and that decision is
closed. The offsets stay ruled because the `fixed` A/B path still reads them.

**THE OPPOSING-SIDE VARIANT IS RULED OUT BY MEASUREMENT.** Joe 1016: *"the other option I want to
share: sample on the opposing-side g15MAge crossing to ib - ie for a high target-side (like our
example 00:23), test on low oob g15Mage's crossing to ib"*. It put his ~01:18 bar on the grid to 15
seconds — g15Mage LOW→ib cross 7 at 01:17:55, knowable 01:18:10, reading reverse 0 of 30 — but over
94 days all 16 of its arms land between **−105.93% and −125.87% net**, at a 55.3–60.8% win rate
against the same side's 70.6–72.3%.

**THE WAIT IS UNBOUNDED, AND THAT IS NOT A DEFECT TO CAP.** Joe has specified no cap. On his own
window 00:56:30 to 01:09:40 is 13.2 min and 01:09:40 to 01:29:15 is 19.6 min, against the
superseded fixed grid's constant +10 min. `known_at` is the later of the two crosses' confirmation
bars, so the mech stays causal however long the wait runs.

---

## 6. THE CONJUNCTION — `_conj.py`

**Joe's five lines, 1015/1016:** g15Mage, g30Mage, ws1Mage, ws2Mage, ws3Mage, each confirming an
oob→ib cross inside a span, gated on ws1Mage being same-side oob.

**The role map, his 1016 instruction:** *"create knobs that are more than just a simple number.
think, how can I swap Mage line's participation in a mech"*.

    W_CONJ_ROLES  g15Mage:latch,g30Mage:latch,ws1Mage:member+gate,ws2Mage:patch,ws3Mage:patch+anchor

**`latch` is his ruling, 1016:** *"g15Mage is constantly on the move, the result of mimicing 15second
candle behaviour. allowing it to fall back to a `missing` state poisons the output -let's make the
flip from `missing` to `in` a one-way trip for g15. add also g30 to the same regime"*.

**K = 5, his preference with his reason, 1016:** *"K=5 is preffered so that when ws3 does not print
a divergence, we are still exhibiting safe behaviour"*. He held it until the data was in: *"Two
things I have not measured and will not assume: -I'm glad you called this out - I want to know as
well. gather the data then I can confirm K=5"*.

**`patch` is his mech, 1016:** *"create a mech that needs 1) and 2) to qualify, then patches
conjuncture so that ws3Mage's input is made true"* — where 1) is ws3Mage blocking the conjunction
verdict and 2) a ws3r divergence anchored on ws3Mage's reversal. And: *"include ws2Mage. the logic:
if ws3 is printing a divergence, ws2 is naturally going to follow it"*.

**The patch's trajectory test is his read, 1016:** *"but that is arithmetic, not signal... -my read:
the strengh has increased from 11135 to 18387 in 1.5 minutes - that's a strong trajectory. we don't
need to know if pxs has bottomed - the indicators are giving us the data"*. `W_CONJ_TRAJ_MIN` 25.0
is MINE — his 30.6% plus slack, per his *"you'll need a minimum angle, whic I won't be able to
supply. use the value that created the mech, + slack, we can tweak it later"*.

**The gate slack, BANKED 4 bars = 20 s.** Strict gives the LOW side 0 of 40 fires on a price pivot;
slack 4 gives 25 of 190 = 13.2% and costs the HIGH side 25.6% → 24.7%. The chain goes +5.9609% →
+7.9887%. Joe 1016: *"I agree. bake it along with all of the mechs that create the 7.9887. add the
lineage confluence-only mech also"*.

**The x-cross lookback is his knob, 1016:** *"when this is built and applied, the ws5x-cross might
still be out of sequence. fix this with a {knob:2, 'CONJ_XCRS_LB'} minute lookback"*, then *"from
your numbers, I think 3 is better than 2. xwob needs to be confirmed"*. `CONJ_XCRS_LB` 36 bars =
3 min, `W_CONJ_XCRS_XWOB` 8.

---

## 7. THE REST OF THE WALK

**THE STANDDOWN, Joe 1016:** *"until we have a reason to change: require a 4 minute standdown after
a trade is printed. the logic (untested, possibly unsound): if the pivot is still pivoting after 4
minutes then there's a lot of trading activity happening, which might indicate the end of a larger
cycles momentum"*. 48 bars. Measured: on the 2026-07-22 22:10:35 leg it suppressed three ws5Mage
flicker triggers at 22:12:35, 22:13:30 and 22:13:55.

**THE CAP, Joe 1015:** *"for the second LONG, pyramid it. max 2 same-target trades at any given
time"*. `W_CONJ_CAP` 2.

**LINEAGE IS CONFLUENCE ONLY, Joe 1015:** *"lineage is confluence only"*. `_lineage_conf.read()`
returns one of `carrying` / `exhausted` / `blocked` plus a sentence, and **never a bar**, so lineage
cannot become an entry or an exit by accident. `CARRY_MIN` 12 bars is MINE and stated.

**THE NON-OOB BAND IS DISABLED, Joe 1016:** *"disable it"*. It was a joint mech — Joe: *"no - it's
ours. you brought it to the table, and I offered mode for it"*. The producer stays in the Jig as
`mage_band_split` with its in-use costs recorded there.

**THE DEDUPE IS ON (bar, side).** A bar is one side-event however many triggers landed on it.
Found twice in my own runs: several ws5Mage oob entries resolving to one knowable bar printed
2026-07-22 01:04:05 four times; then the priority ruling made the oob path and the turn path resolve
to the same bar and 00:47:30 printed twice. The key drops the source on purpose — with the source in
it, one reverse at one bar on one side counts twice because two paths found it.

**`mom-xfer` IS OFF BY HIS RULING, not by omission. Joe 1016:** *"no mom-xfer"*. It was measured
first: the per-TF race version is `XFER_TFS = (9, 8, 7)` at
`docs/22_go_20260921/report_leash_momtf.py:72` — his recall was ws8/ws9/ws10 and the banked set is
ws7/ws8/ws9. Its best arm over 94 days was ws11/ws12/ws13 at count 1, netting +157.3814% against
the banked g15 grid's +173.9969%. A second finding, recorded because it inverts the mech's own
name: the gate helps on `true` (the racers STILL momentum-true) and does nothing or costs on `left`
(the racers having LEFT momentum).

---

## 8. CAUSALITY

Every trigger bar is the bar its own event becomes knowable — a conjunction fires at the k-th
confirmation, an x-cross at its xwob completion, a bounce-pred verdict at its `known_at`. The
x-cross lookback only ever reaches BACKWARD from a bar that has arrived. `_bp_g15.verdict_at`
asserts `known_at >= the later sample bar`; `_bouncepred.read_bars` asserts no read bar exceeds
`j + OFF_B`.

---

## 9. WHAT IS STILL OPEN

| # | the decision | state |
|---|---|---|
| 1 | **what ends the hold** | `walk` stops at the FIRST reverse. On the 00:02:10 to 01:10:30 episode the verdict flips 25 times and the first reverse is a 1-of-30 flicker at 00:06:00. Every causal rule I can state lands before Joe's named bar. **The single highest-value open ruling** — it blocks both of his grid readings |
| 2 | the maker-first fill config | `_fill.py` is built; the sweep of offset × backup wait × maker-exit has not run. Joe 1016: *"the three things all live in the data - the goal is the config that produces the best overal pnl"* |
| 3 | `W_BP_MIN_LINES` 15 of 30 | MINE. The only number in bounce-pred Joe did not give. Not load-bearing at any of his named bars — every reading there is 0–1 of 30 or 30 of 30 |
| 4 | `W_CONJ_TRAJ_MIN` 25.0 | MINE, his value plus slack, per his own instruction |
| 5 | `_lineage_conf.CARRY_MIN` 12 bars | MINE and stated |
| 6 | the main-chain integration | Joe 1016: *"still benched for now"*. See `main_chain_handover.md` |
