# 1017 — the bank: Joe's "A" entry timing and the 1.60 MAE cap

Joe 1017, the instruction this doc records:

> *"bank A. update spec, store knobs, commit and push all files, make the machine live / I'll
> review the trade list after that's done and keep honing"*

"A" is his own label, from a two-row options table he was given:

> **A — wait for option 2, no fallback.** At the verdict you commit to waiting. If it fires you
> enter late; if it never fires you get no trade.

He had already ruled out the alternative himself. Asked whether a fallback to the verdict bar on
the signals option 2 misses was causal, he said *"no"* — picking which signals not to wait for
needs the exit bar, which is in the future at the verdict.

---

## 1. What changed in the machine

| the file | the change |
|---|---|
| `docs/octo-freedom/1005_scoring/octo2.py` | a verdict no longer opens at its own bar. It **arms** there and the trade fills at the oob-divergence fire bar. A verdict whose fire bar never arrives produces no trade. The 1.60 MAE cap is a new exit path. |
| `optimus9/analysis/jig.py` | `next_oob_divergence` — the fire-bar producer. Also `mage_cascade`, `mage_cascade_bar`, `r_matryoshka` from earlier in the same session. |
| `docs/octo-freedom/1005_scoring/_chain10.py` | `ib_return` and `W_LIN_IB_XWOB` = 5. |
| `docs/octo-freedom/1005_scoring/_openvote.py` | the three-voter open vote plus test 2, all reading one bar. |
| `docs/octo-freedom/1005_scoring/_ruled.py` | 20 new ruled knobs, each with his words. |

### the trade record

`armed` is the verdict bar — his OPEN, and the trade's identity. `entry` is the physical fill bar —
his `trade-fires` column. Joe 1017: *"we could keep OPEN as 02:07, then have a `trade-fires` column
that prints the bar of the physical open"*. `octo2.gross` prices off `entry`, which is why the fill
bar keeps that field name.

---

## 2. The entry timing, his spec

> *"2) wait for the next high-side g30Mage oob, and use that bar as the anchor for a divergence
> test / --if the divergence test is bearish, then open the SHORT at 19:26"*

The side is the **trade's**, from *"because this a SHORT ... wait for the next high-side g30Mage
oob"*. The event-side variant was measured beside it and is not banked; it is not offered as a knob
either, because it keys off the ws1cp's oob side and `octo2` does not track that.

`W_OCTO2_FIRE` = `oobdiv`, `W_OCTO2_FIRE_TF` = 30 seconds (g30Mage). `verdict` restores the old
behaviour for an A/B.

### why not the other two options he offered

All three were tested on all 40 trades of 2026-08-22 to 2026-08-24, at the 1.60 cap:

| the option | net | trades |
|---|---|---|
| 1 — fire at the verdict when the matryoshka test says `follows` | −3.1004% | 15 |
| **2 — the next g30Mage oob + anchored divergence, trade side** | **+14.5689%** | **34** |
| 3 — ws1r reverse high of 50, ws1x crossing [boundary, r, Mage] xwob 5 | −6.9125% | 40 |
| octo2 as it stood, firing at the verdict every time | +1.4405% | 40 |

Option 1 was exactly a **no-op** on the trades it kept — +0.0000 pp against octo2 — because it
fires where octo2 already fires. Its only effect was to drop 25 of 40 trades. Option 3 lost at
every cap value swept.

### what the bank costs, reported and not hidden

- **6 of the 40 signals never fire before their own exit** and are given up. They were worth
  +8.2009% at the cap.
- the wait reaches **4,390 s** on 2026-08-22 05:15:00 — longer than the 4,065 s ib-return delay
  Joe rejected as *"unacceptable"*. Median 972 s, 8 of 34 over 2,500 s.
- the 34-trade measurement used **octo2's own exit bars**. The exit is event-driven, not
  entry-driven, so a later entry keeps the same exit in most cases — but a pending trade misses any
  closing event inside its own wait, so the trade set changes. The 94-day run below is the first
  measurement with that effect included.

---

## 3. The MAE cap

> *"apply a 1.6 MAE cap. if the cap is hit, the MFE for that row is set to zero"*

and, asked whether the row then realises the cap loss rather than zero:

> *"-yes"*

and on the value:

> *"MAE is intentionally higher (1.6) because our window is a high MFE zzone"*

`W_OCTO2_MAE_CAP` = 1.60, `W_OCTO2_MAE_CAP_ON` = 1. A stopped row realises **exactly −1.60%**, and
drag is added on top of that by the report, never inside the machine.

**The stop wins a tie.** Inherited, not mine: `trade_config`'s `stop_same_bar_priority` is `stop`,
Joe 0929 *"use stop"*.

### the cap sweep that sits behind 1.60

40 trades, 2026-08-22 to 2026-08-24, cap-loss reading, octo2's original entry timing:

| the cap | octo2's net |
|---|---|
| 0.70 — `trade_config`'s own `mae_cap` | −7.8206% |
| 1.10 — lineage's `stop` | −9.6237% |
| **1.60 — his** | **+1.4405%** |
| 2.00 | +0.0315% |
| 2.50 | −0.7182% |
| 3.00 | −7.7182% |
| none | +42.6097% |

1.60 is the peak of the swept range for every arm. On 40 trades that is a coincidence worth naming
rather than a validated choice — and it is his number, not one fitted for him.

The uncapped +42.6097% was carried almost entirely by trades that first went 1.6%+ against before
resolving. The MAE median across the 40 is **1.3186%**.

---

## 4. The one rule of this bank Joe has NOT set

**Does a pending trade occupy a pyramid slot?**

As built it does **not** — `octo2`'s CAP test has always counted `live`, and a trade armed at a
verdict but still waiting for its fire bar is not live. That is the literal reading of the existing
code and it is stated at the line in `octo2.walk`.

He has ruled on the pyramid before — 1017: *"3 LONG trades would break the pyramid rule"* — so if a
pending trade should hold a slot, that is the line to change and this run to repeat.

Two smaller rules are stated at their own lines in the code rather than guessed:

- **the stand-down is stamped at the verdict, not at the fill.** `last_print` has always marked
  where the decision was taken, and the stand-down spaces decisions.
- **a closing event inside a pending wait does nothing to the pending trade.** The close loop has
  always iterated `live` only.

---

## 5. The 1018 session — the divergence machine and the 4th voter

### the machine is `jig.anchor_floater`, not `jig.divergence`

Joe 1018 settled which of the two producers is the divergence machine:

> *"you're right - anchor_floater is the correct divergence machine"*

and why the other one cannot be:

> *"fix jig.divergence. it's completely illogical for them both to be oob - most r divergences
> print an ib anchor"*

`jig.divergence` builds both the anchor and the floater from oob **episodes**, so an in-bounds
anchor cannot exist in it. It has **zero production callers** in the repo. A rename of both
producers was attempted and **rolled back** on his word — *"this is fast turning into a mess /
rollback and we'll use anchor_floater as our divergence machine"* — so the names are unchanged.

### three faults found in `anchor_floater`, all his diagnoses

| # | the fault | his words | the fix |
|---|---|---|---|
| 1 | step 1 **rejected** any anchor on the pivot's side of 50, so a genuine bullish divergence with an ib anchor could never fire | *"the 'side of 50' has accidently bled into the current state where the genuine bullish divergence is unable to fire / the past 50 mech can't block an anchor if it's already past 50"* | `AF_ANCHOR_MID` False. Step 2 already walks back from `k-1`, so the anchor's own run becomes the pivot by itself — his shape **A** |
| 2 | the pivot could be a **pinhole**. At 2026-08-26 03:58:40 it was 4 bars, 20 s, 0.52 points above 50 — five 50-crossings inside ten minutes | *"was there a pinhole through 50 that I don't see?"* | `AF_PIVOT_WIDTH` 12 bars = 60 s, `AF_PIVOT_DEPTH` 2.0 r points. A run failing either is stepped over |
| 3 | the step-3 walk stopped on **one** non-improving block, landing on a 43.82 knife-edge mid-descent while the real low sat 5.9 blocks further back | *"B - no lookback cap"* | `AF_STOP_N` 2 consecutive non-improving blocks. No distance cap — his words. An empty block still does not count, his 0921 rule |

The three values were delegated: *"your call on the value - whatever allows ws3r to genuinely cross
past 50 before finding the 03:29 low extrema"* / *"I think seperate knobs are good"*. 12 is one
full ws1 bar of persistence; 2.0 is this file's own `SR_TOL` from his 0912 *"tolerance ~2%"*; 2 is
the minimum that reaches his named 03:29 low of 16.52.

### the divergence table at the 2026-08-26 04:00:45 anchor, dr −1

| the line | the anchor r | the pivot | the floater | d_osc | d_px | fired |
|---|---|---|---|---|---|---|
| ws1r | 68.83 | 04:00:05 r 75.90 | 03:52:50 r 13.58 | +55.25 | −0.00060 | **BULLISH −1** |
| ws2r | 33.23 | 03:42:10 r 70.03 | 03:14:00 r 21.31 | +11.92 | −0.00095 | **BULLISH −1** |
| ws3r | 36.56 | 03:56:15 r 54.21 | 03:32:30 r 16.52 | +20.04 | −0.00070 | **BULLISH −1** |

Before the fixes, ws1r returned `None` on the first line of the body and ws3r took a non-extreme
floater. All three now fire.

### the Mage lines are dropped

> *"I think the Mages are too fickle for divergence - we'll drop them and use the 3 aaaarrr`s"*

So the test is **3 lines**, not the 6 of his 1017 spec. Measured at the same anchor: ws1Mage
d_osc −7.17, ws2Mage −29.41 — both made a **lower** low with price, which is confirmation, not
divergence. And `mid` 50 with `AF_PIVOT_DEPTH` 2.0 are **r-scale** numbers: under them ws3Mage's
walk reached a pivot of 141.88 and a floater of −5.87 nearly four hours back, because Mage is
unbounded. The Mage lines are still read for **one** purpose — selecting the bound side.

### voter 4, and 2 of 4

> *"add divergence as the 4th voter for `4-voters-against`. minimum 2 of 4"*

`W_VOTE_MIN` stays 2; the voter count moved from 3 to 4. The bound side is his 1017 rule — *"the
divergence test is bound to the side that printed the last oob Mage"* — and the polarity matches
the other three voters: **it objects when the divergence does not support the trade**, because a
bullish divergence supports a LONG and that is silence, not an objection.

### the scan: 13 MAE-1.6 stops exiting 2026-08-26

| the measure | value |
|---|---|
| ALLOWED against the trade at the event bar | 3 of 13 — 23.1% |
| ALLOWED at the next same-side ws1Mage oob-X-ib, inside his 10-min cap | 2 of 13 |
| ALLOWED at either | 3 of 13 |
| lin-exh objects on | 10 of 13 |
| the divergence voter objects on | 10 of 13 |
| the mage-cascade objects on | **0 of 13** |

At 2-of-4 the cascade contributes nothing to a kill on this day.

### THE COUPLING NOBODY HAD SEEN

Tuning the divergence machine **moves octo2's trades**. `next_oob_divergence` — the banked entry
timing — calls `anchor_floater`, so the three new knobs changed which trades exist: the 2026-08-26
MAE-cap stops went from **11 to 13**, with 04:46:40 and 11:38:30 appearing. The divergence producer
can no longer be tuned in isolation from the machine's P&L.

---

## 6. Still open, carried forward

| # | the item |
|---|---|
| 1 | **lin-exh's polarity.** Confirmed by Joe but not yet built: when the trade runs AWAY from the side being measured, lin-exh qualifying is a confluence, not an objection. Inverting it on the 41 signals moves 27 verdicts. |
| 2 | **lin-exh's bar.** His spec walks forward to `ib_return`'s stamp; voter 2 still reads the cascade bar. |
| 3 | **the `bnd` fence reading.** `_chain10.bnd` is one-sided, so at d −1 a `.` means only `v > 17` with no ceiling. Unruled. |
| 4 | **the open vote has no name.** `_openvote.py` is a placeholder filename. |
| 5 | **the matryoshka test's unsettled knobs** — the minimum lag, the walk's own direction, and what `not yet` does. Joe 1017: *"I'm expecting the voters to handle this organically. if it doesn't, I'll find a better negative branch"*. |
| 6 | **re-walking the exit from each candidate entry**, which is the only way to separate "better entry" from "shorter trade". |
| 7 | **the timeout variant** of the entry timing — wait up to T for the fire bar, else enter at T. Causal, unmeasured, would recover some of the 6 given-up signals. |
| 8 | the two seam grids on the register: `momo_seam` midnight against `jig`'s epoch default. |
