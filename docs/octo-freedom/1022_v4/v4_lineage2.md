# lineage2 — spec

Named by Joe 1025: *"I need a lineage2 fork of lineage - we're going to play with a new idea"*.
A FORK. v4lineage is untouched; nothing here is in the machine.

His words are quoted verbatim. Everything outside a quote is the build.

## 1. The one difference

> the key difference for lineage2: v4lineage tests `r` mom states on every bar, lineage2 tests them
> on a determined cadence

> lineage2 will default baton-pass on ib

And why it matters, his own framing:

> the point of lineage2's extremum-testing cadences (either ws1r or ws1b) is to give the walk the
> best chance of reaching the pivot. in v4lineage, ws6r reversing without oob would have been the
> end of the walk. with cadences, we get to see the true state of the overall momentum - ws7
> "showing up" is the proof of concept

> the point of cadences: they are where decisions are made. testing at set points (like 0723)
> provides the opportunity to override a poor signal (ws6r exhaust) if a better signal (ws7
> ex-fence) has presented itself

## 2. The board

> all calcs and decisions are target-side
> --(ie SHORT's target-side is low, LONG's target-side is high)

## 3. The knobs

His four from the 1025 handover:

| the knob | value | his words |
|---|---|---|
| `v4mom_maxTF` | 12 | *"v4mom_maxTF = 12"* |
| `v4mom_fnc` | 100 − 20 = 80 → (20, 80) | *"identical to the banked RMOM_FNC 80. Same knob - yes"*. So it IS `RMOM_FNC`, and moving one moves both |
| `lin_hop` | 2 | *"lin_hop = 2"* |
| the t1cadence grace | 120 s | *"the 2-minute grace in t1cadence -knob"* |
| the t3cadence fraction | 0.75 | *"int(round(75%))"* |
| `v4cadence_fnc` | DROPPED | *"v4cadence_fnc -drop"* |

And the full set as built, every one in `v4_knobs.py` with his quote beside it. The NAME column
says whose the name is; the VALUE column says whose the value is. Twenty-four knobs.

| the knob | value | the name is | the value is | what it governs |
|---|---|---|---|---|
| `L2_MOM_MAXTF` | 12 | his | his | the ladder's top rung |
| `L2_LIN_HOP` | 2 | his | his | max hops rider → candidate between cadences |
| `L2_T1_GRACE_S` | 120 s | mine | his | t1's late-cws1r-reversal window |
| `L2_T3_ON` | **0** | mine | his | the old t3cadence. BANKED OFF — *"the old t3 is defunct"* |
| `L2_T3_FRAC` | 0.75 | his | his | t3's fraction of the ex-oob HTF population |
| `L2_T3_MIN_MATRY` | 2 | mine | his | t3's floor on reversed matryoshka lines |
| `L2_GATE_MODE` | `closed` | mine | his | which ladder t3's oob population reads |
| `L2_CWS1R_WOB` | 1 bar = 5 s | mine | his | the lift-off wob on cws1r for t1's reversal |
| `L2_ARM_RETEST` | 1 | his (the mech) | his | v4-arm-lineage-retest on/off |
| `L2_RE_IB_MIN` | 2 rungs | mine | his | v4_reentry's count of Mage rungs that stayed ib |
| `LIN2_LATCH_ON` | 1 | mine | his | the 2-staged latch on/off |
| `LIN2_T3_MIN_TF` | 5 | **his** | his | the rider range latch 2 accepts, ws5..ws12 |
| `LIN2_LATCH_LIFE_S` | 600 s | mine | his | how long latch 1 stays latched |
| `LIN2_SUPPORT_LINES` | 3 | mine | his | the lines below the rider that must ALL have reversed |
| `LIN2_REV_WOB` | 12 bars = 60 s | mine | his | the reversal wob, THIS mech only |
| `LIN2_CROSS_WOB` | 12 bars = 60 s | mine | his | every cross to ib and to in-mom-fnc |
| `LIN2_COUNTER_OOB_ON` | 1 | mine | his | the cws1b counter-oob cadence on/off |
| `LIN2_CASCADE_NO_ACTION` | 1 | mine | his | the mage-cascade truth table on/off |
| `LIN2_MISMATCH_ACTION` | `rev-trade` | mine | his | what a mismatch does at the counter-oob cadence |
| `LIN2_MAE_CAP` | 1.1 % | mine | his | the report-only stop-loss model |
| `LIN2_CAND_NOT_REVERSED` | **0** | mine | mine (OFF so the bank does not move) | the third term on the baton candidate test |
| `LIN2_BARRAGE_TOL_S` | 70 s | mine | MEASURED off his 02:29 | cross → ws1r reversal tolerance |
| `LIN2_BARRAGE_LINES` | 6 | mine | MEASURED off his 02:29 | the reversal count that makes a barrage |
| `LIN2_BARRAGE_MIN_TF` | **0 = OFF** | mine | UNRULED | the lowest TF the barrage must reach |

## 4. Which lines, closed or emerging

Joe 1025 settled it line by line. His reason:

> the cws lines were introduced for accuracy and specificity in the lower TFs
> -the rider-scan has all lines emerging for intra-mech continuity
> -I don't want slower TF's running on closed bars because it spoils the line reversal times

| the clause | the line | mode |
|---|---|---|
| t1cadence trigger and its ib cross | cws1b | CLOSED |
| t1cadence qualifier | cws1r | CLOSED — *"this is my wrong: both should be cws1r"* |
| t2cadence | cws1r, cws1b | CLOSED |
| t3cadence HTF set | ws7r..ws12r | EMERGING |
| the arm race | ws4r | EMERGING |
| the arm race | cws1b, cws1r, cws2Mage, cws2r | CLOSED |
| the rider scan | ws1r..ws12r | EMERGING |
| v4_reentry | ws5Mage, ws{>5}Mage | EMERGING |

**NO DWELL ON ANY ib CROSS HERE.** Joe 1025:

> no dwell. the way I see it: because we're on closed bars, we have an automatic wob. it also means
> I have TV values that are precisely aligned with what the code sees

## 5. lin_hop applies BETWEEN cadences, not AT one

Joe 1025, resolving the ws8 → ws11 pass in his own 08-30 example:

> here's the distinction: when baton is being passed between cadence markers, linhop applies. at a
> cadence event, linhop doesn't apply
> --the same is true for "review the board from ws{riderTF} to ws{v4mom-maxTF}"

| when | the candidate range |
|---|---|
| between cadences, invisible to the walk | riderTF + 1 .. riderTF + `lin_hop` |
| at a cadence event | riderTF + 1 .. `v4mom_maxTF` |

## 6. Baton passing

> -baton passing will mostly happen between the cadence events, therefore be invisible to the walk
> -baton passing is initiated by 2 conditions
> --1) rider was oob and has crossed to ib
> --2) rider was between ex-v4mom-fnc and oob, and crossed to in-v4mom-fnc
> -baton can only be received by a higher TF. the max hops between a rider and a candidate baton
>  receiver is {lin_hop, default 2}
> -baton can only be received by an r line that is 1) ex v4mom-fnc and 2) tagged as `towards`
> --without "tagged as `towards`", there is a risk of riding a line that has already spent it's
>  momentum

**THE `towards` PERSPECTIVE IS TARGET-SIDE**, Joe 1025: *"the perspective is target-side for the
whole ladder"*. The DIRECTION is still each TF's own Mage trajectory.

Joe 1027 settled the same perspective for the shared producer `jig.away_toward`, correcting an
earlier reading of mine for the third time: *"the actual toward/away perspective comes from the
open (or invisible-incoming, if no trade is open) trade: use the target-side"*. So the two now
agree, and `jig.away_toward`'s header carries his ruling. lineage2 still computes its own tag,
because `towards` reads `rule2_trajectory.opposed_extrema` over `K.traj_block(tf)` and the producer
reads a Mage direction - two different inputs to the same perspective.

## 7. The four cadences

### t1cadence — cws1b is oob

> --if cws1b is oob
> ---walk to "%cws1b crossing from oob to ib%"
> ---IF (cws1r had "reversed on target-side of 50" while cws1b was oob) OR (cws1r reverses on
>  target-side of 50 in the 2 minutes (CAUSALLY) following the cws1b oob to ib cross)
> ----fire a cadence event on the "%cws1b crossing from oob to ib%" bar or the "late cws1r
>  reversing" bar, whichever is last

His examples:

| the bar | what it is |
|---|---|
| 2026-08-29 04:30 low | cws1b crossed oob→ib, cws1r has NOT reversed — NOT a cadence |
| 2026-08-29 04:36 low | cws1b crosses to ib again AND cws1r reversed while it was oob — a cadence |
| 2026-08-29 07:47 high | cws1b crosses to ib, cws1r not yet reversed |
| 2026-08-29 07:48 | cws1r confirmed reversed inside the grace — the cadence fires |

### t2cadence — cws1r is oob, cws1b is not

> --IF cws1r is oob and cws1b is NOT oob
> ---fire a cadence event when cws1r crosses to ib

His examples: 2026-08-28 14:58 high, 17:48 high, 2026-08-29 05:42, 10:13.

### t3cadence — the HTF reversal

> TYPE 3 v4cadence (the HTF reversal - when any of ws7r to ws12r (HTF lines) have been oob already
> in this trade, and now int(round(75%)) of the HTF lines are printing a reversal)

| the concretion | his answer |
|---|---|
| 75% of what population | the HTF lines that HAVE BEEN oob — *"confirmed"*. His 07:49 example has one such line and 75% qualifies on it |
| "printing a reversal" | *"lift-off. for t3cadence, precisely timed reversal(s) help us improve profit"* |
| "already in this trade" | *"use the arm bar"* |
| the extra gate | *"the 75% qualification can only fire if there are no higher TFs exfence, ie there are no baton-pass candidates"* |

### t4cadence — a non-oob rider reverses with nowhere to pass

> TYPE 4 v4cadence (a new rider receives the baton when not oob, and reverses away from target-side
> without reaching oob)
> ---1902, ws8 reverses. reversing when ex-fence-not-oob creates the same result as oob-to-ib - it
>  needs to pass the baton or declare exhaust
> ----this is where t4cadence fires - a non-oob rider TF without an in-lin-hop TF to pass the baton to

## 8. v4_reentry

> -ws5Mage oob to IB AND ws{any TF >5}Mage failed to reach oob while ws5Mage was oob

Joe 1025: *"build it now. the described reentry will be the only reentry mech in lineage2"*. It is a
SIGNAL PRODUCER — the router opens the trade lineage2's walk then runs on. His examples:
2026-08-28 11:25, 15:00, 2026-08-29 00:10, 02:35.

## 9. The walk

> race the arm:
> -armed needs one of these 3 to qualify:
> --ws4r oob, or (cws1b + cws1r oob), or (cws2Mage + cws2r oob)
> -if cws2Mage + cws2r wins the race, check for a cws1r div and follow its verdict

**THE DIVERGENCE BRANCH**, Joe 1025:

> for "hi/lo", use the target-side
> follows its verdict: if the open trade (or invisible trade if there is no open trade) is SHORT and
> the verdict is +1, the verdict is AGAINST the SHORT and router will create a rev-trade. the same
> is true for the inverse: LONG trade and -1 verdict is a rev-trade. if the trade direction and the
> verdict align, take no action

Then:

> -if armed is true (causal)
> --scan ws{1 to v4_mom_maxTF} for the highest ws{TF}r ex-fence, and make that TF the rider
> --IF no rider is assigned at the armed bar +5s
> ---the walk ends. pass to router for a rev-trade
> --if a cadence event fires
> ---gather the rider's two states:
> ----1) no-longer-exfence: yes/no
> ----2) has reversed: yes/no since the last ("initial rider detection" or "last cadence event")
> ---review the board from ws{riderTF} to ws{v4mom-maxTF} for target-side lines that are ex-fence
>  and tagged as `towards` - these are baton-pass candidates
> ----remember that the riderTF can change between cadence events
> ---if baton-pass candidate(s) are discovered, the rider becomes the candidate with the highest TF
> ---else if there are zero baton-pass candidates
> ----if (rider TF is oob) OR (rider TF is between ex-fence and oob AND has not reversed)
> -----no action needed. walk to the next cadence event
> ----else declare exhaustion and defer to the router for rev-trade

## 10. The CLOSED ladder is computed, not loaded — `v4_closed_prev`

Section 4 says which lines read CLOSED. This is HOW, and it is a mech of its own because the
closed `.npy` lines on disk cannot be used.

Joe 1026 asked for the fix and named it himself:

> from memory, I think the best fix was to take the last 5s bar's close value (eg the xx:xx:55
> timestamp). does that help? we absolutely need to be aligned with the live tape

> I've assumed the "seam - 5s" is our only option. push back if I've missed the point

**WHAT WAS WRONG WITH THE FILES.** Register A4 in `docs/causal_lookahead_register.md`: `resample`
stamps each bar at window-open while aggregating the whole window, and `align_to_base` maps a
mid-window base bar onto that still-forming bar. Up to one full TF of future on every read.

**THE READ AS BUILT.** `v4_closed_prev.series(emerging, tf_seconds)` returns, for every 5 s bar,
the EMERGING value at the last 5 s bar of the most recently COMPLETED bucket, held forward. Two
asserts carry the causality claim, not comments:

| the assert | what it refuses |
|---|---|
| `first < idx` | a closed-prev read at or after the bar it serves |
| `T[first] < bucket_open` | a closed-prev read taken from inside the forming bucket |

**THE GRID IS MIDNIGHT-ANCHORED FOR EVERY TF**, matching `line_reader`'s own rule. The first build
used the epoch grid: cws7r mismatched the reference on 49,800 of 86,400 bars and cws11r on 64,224.
On the midnight grid the mismatch count is 0 over 1,036,800 bars.

**VALIDATED AGAINST THE LIVE TAPE**, the 4-hour run of 2026-10-26 21:27:40 to 2026-10-27 01:27:00:

| the read | value |
|---|---|
| r lines, seam\-5s against the live tape | match to 2.8e-14 |
| missing bars | 0 |
| OHLCV rewrites | 0 |
| bars captured | 2880 |
| firings captured | 408 |

**THE STALENESS IS THE COST, and it is not hidden.** Over the same 4 hours the emerging read fired
320 times against the seam\-5s read's 88, and the seam read saw 32 of 134 baton passes. That is why
only the reversal detection stayed emerging - his 1025 reason: *"I don't want slower TF's running on
closed bars because it spoils the line reversal times"*.

## 11. Every cross INTO the gentler state carries wob 12 — `LIN2_CROSS_WOB`

Joe 1027: *"add the wob12 to all crosses to ib and crosses to in-mom-fnc"*, then narrowing his own
first wording: *"from your response, I can see this request was flawed. I need wob12 only for r
lines crossing back to ib, or to in-mom-fnc"*.

The actionable bar is the LAST bar of the hold, never the cross bar.

| the site | the cross |
|---|---|
| t1cadence | cws1b oob → ib |
| t2cadence | cws1r oob → ib |
| v4-arm-lineage-retest | cws1r oob → ib |
| the walk's pass rule 1 | rider oob → ib |
| the walk's pass rule 2 | rider ex-mom-fnc → in-mom-fnc |

**IT DOES NOT GOVERN CROSSES THE OTHER WAY.** Entering oob and entering ex-fence still carry no
dwell: a single bar past the fence makes a line ex-fence and a rider candidate.

**IT SUPERSEDES TWO OF HIS OWN EARLIER RULINGS**, both recorded rather than quietly dropped:

| the superseded ruling | his words then |
|---|---|
| the retest's gap 5 | *"5, your read"*, accepting L2_CWS1R_WOB 1 for its oob→ib cross |
| `v4_l2_cadence`'s header rule | *"every `oob_ib_cross` call takes xwob 1 and the cross bar IS the actionable bar"* |

The knob's NAME is mine. The value and the rule are his.

## 12. `v4-arm-lineage-retest` — the arm is a cadence

HIS SPEC, 1026, verbatim:

> your own spec line says the verdict would be HOLD... -good point. let's add a
> `v4-arm-lineage-retest` mech that will fire at arm:
> if ws1r is oob at arm
> -if ws2r and ws3r are in mom-fnc
> --walk ws1r to handover (ib) and follow the lineage process
> --if an exhaust is found, route to rev-trade

> earlier I stated that cadence events are where you make decisions. I'm adding arm as a cadence

Then, narrowing it himself: *"8, the gate's cadence is the cws1r oob→ib cross bar"*. So the arm
OPENS the gate and decides nothing itself.

HIS NINE RULINGS, each one his:

| # | the gap | his answer |
|---|---|---|
| 1 | the ladder | CLOSED cws — *"my error: I meant to use cws, not ws"* |
| 2 | "in mom-fnc" | not ex-fence on the TARGET side |
| 3 | when cws2r / cws3r are read | the arm bar only |
| 4 | "handover (ib)" | the oob→ib cross only, not the second pass rule |
| 5 | the wob | L2_CWS1R_WOB 1 bar = 5 s — SUPERSEDED 1027 by LIN2_CROSS_WOB 12 |
| 6 | the rider there | *"re-scan and ride the highest"* |
| 7 | what this is | a gate in the walk; core arm1, core arm2 and ws5rbackstop are off for lineage2 work |
| 8 | the cadence bar | the cws1r oob→ib cross bar |
| 9 | a cap on the walk | *"no need for a cap. if cws1r is oob, it has no choice but to cross to ib"* |

**HIS OWN 00:17 INSTANCE**, which is why the mech exists: the 2026-08-30 00:17:00 HIGH arm had no
baton candidates for ws1, and he said *"that high 00:17 arm should have immediately fired exhaust"*.
The gate's flow through his instance gave 00:19, and his ruling was *"the 0019 matches my view"*.

## 13. The `cws1b` counter-oob cadence

HIS SPEC, 1026, marked IMPORTANT and confirmed 1027 with *"go"*:

> create a cadence when cws1b crosses to counter target-side oob (eg 08-30 1921)

And on what it does, 1027:

> cws1b counter-oob needs to fire immediately. the logic: if b is printing on the non target oob,
> the trade has failed and we need to recover lost profit asap

| the concretion | as built |
|---|---|
| the side | the COUNTER oob: a HIGH-target walk watches cws1b ≤ 15, a LOW-target walk cws1b ≥ 85 |
| the fence | `K.oob_mask(v, -side)` — the one home, so it cannot drift from any other oob read |
| the dwell | NONE. He named none, so the bar is the RAW cross bar |
| the bar | the rising edge into the band |
| what it does | it is a cadence — the walk's own board review runs there, as at a t1 or a t2 |
| its name | NOT NUMBERED BY HIM. The rows carry the description `cws1b counter-oob` until he names it |

**HIS EXAMPLE LANDS EXACTLY.** From 2026-08-30 19:19 cws1b reads 41.20, then 26.38, then 14.16 at
19:21:00 — the first bar at or past the LOW oob fence 15, inside a HIGH-target walk.

**cws1b IS NOT BOUNDED 0..100.** Measured over 08-30..09-03 its firings include 105.07 and −18.11.
The fence reads them the same way and nothing clips.

**WHAT IT DID TO THE DAY.** It is also the one cadence type exempt from the no-action half of
section 15, and that exemption restored 2026-08-30 from 6 walks to 17.

## 14. The 2-staged latch — the t3 replacement

t3cadence is defunct. Joe 1026, after the 24 t3 events were scored: *"I see what you see - it
doesn't hold up ... disable t3 and walk forward from the arm"*, then *"10, yes - the old t3 is
defunct"*. `L2_T3_ON` is banked 0 and kept only as the A/B arm.

HIS REPLACEMENT, verbatim:

> I see a potential replacement for t3, and it's 2-staged latch
> 1st latch, the bearish divergence that fires on the 2151 t1 cadence
> 2nd latch, ws7r reversing (with wob12) and no baton candidate options PLUS the supporting
> ws4,5,6r matryoshka reversals

and the correction he made one message later: *"latch#1 could be a misconstrued target-side. use
the ws1b cross as the target side"*.

HIS RULINGS ON ITS GAPS, 1026, each one his:

| the gap | his answer |
|---|---|
| the divergence read | `jig.anchor_floater`'s `state` — *"I instructed to not use jig.divergence"* |
| latch 1's bar | *"2, at the cadence bar"* |
| latch 1's life | *"3, 10 minutes (knob)"* → `LIN2_LATCH_LIFE_S` 600 s |
| the rider range | *"4, the rider between ws{knob:5,'lin2_t3_min_tf'} and ws12"* |
| the reversal wob | *"static wob12. noted, we'll keep the static"* → `LIN2_REV_WOB` 12, THIS mech only |
| no baton candidate | *"6, inside linhop"* |
| the support | *"7, 3 lines below the rider"* → `LIN2_SUPPORT_LINES` 3, ALL of them |
| the support window | *"8, since the cadence"* |
| the read | *"9, whatever we're consuming in the live test"* → emerging |

FIVE READINGS ARE MINE, each on precedent in this codebase, none of them a number I invented:

| my reading | the precedent it rests on |
|---|---|
| latch 1 fires when `state == side` | the banked DIV branch in the walk makes the same comparison — a +1 verdict against a +1 side is the rev-trade |
| latch 1 reads at EVERY cadence | with t3 defunct, t1, t2 and the counter-oob are the only producers left, so *"at the cadence bar"* has no second reading |
| latch 2 completing EXHAUSTS the walk | latch 2 already requires no baton candidate, which IS the walk's exhaust branch |
| the support lines read the TARGET side | the side t3's own reversal read used |
| a reversal is acted on at its STAMP | banked in `v4_fast`: *"the raw bar is the anchor and the identity of the reversal"*; here stamp = raw + `LIN2_REV_WOB` − 1 = raw + 11 = 55 s |

**A BUG THE STAMP RULE CAUGHT.** Latch 1's support window first tested the STAMP against the
cadence instead of the RAW bar, which admitted reversals that predated the cadence. Fixed, and the
2026-08-30 06:31:10 latch moved to 06:34:40.

**WHY THE WOB IS STATIC 12.** Measured 1026 across ws5/7/9/12r over 08-30..09-03: a seam-aligned
dynamic wob kept ~25% fewer reversals and was slower on every one, median 75–80 s against the
static 55 s. Joe: *"static wob12"*.

**HIS OWN 2026-10-26 WALK, the one the latch was built from:**

| the bar | what he read |
|---|---|
| 2026-10-26 21:51:00 | the t1 cadence, the first group with the ratio inverted — latch 1 |
| 2026-10-26 21:53:00 | the live OPEN |
| 2026-10-26 22:32:00 | ws6r at low ex-fence — *"great: ws6r is what I was hoping for"* |
| 2026-10-26 23:06:00 | the next cadence, ws1r to ib with no baton candidates — the exhaust |

His own measure of it: *"our live 2153 OPEN to the 2306 cadence ws1r exhaust returns us ~0.8%"*.

## 15. The mage cascade is read at EVERY cadence

Joe 1027, after the 18.96 hand-picked value was ruled out:

> I'm more inclined to either a) use the last closed bar value (18.2 at 0136), or b) get a
> mage-verdict, and if its verdict matches the trade direction then take no action (ie keep
> walking) --in fact, let's get the mage-cascade verdict at every cadence event

Then, correcting a build that only had the no-action half:

> the issue isn't in mage cascade, it's how the mage-cascade is applied.
> --if the trade is long and the verdict is up, take no action. if the trade is long and the verdict
> is down, rev-trade
> --if the trade is short and the verdict is up, rev-trade. if the trade is short and the verdict is
> down, take no action

**HIS TRUTH TABLE, as built:**

| the trade | the verdict | the action |
|---|---|---|
| LONG (target HIGH) | `up` | take no action — keep walking |
| LONG (target HIGH) | `down` | rev-trade |
| SHORT (target LOW) | `down` | take no action — keep walking |
| SHORT (target LOW) | `up` | rev-trade |
| either | `neither` | *"2, let the cadence decide"* — the board review runs |

**A MISMATCH IS AN EXIT**, not a fall-through to the board review. The row stage is `EXHAUST` and
the `why` carries `OPPOSES`.

**THE PRODUCER REFUSES TO MAP THE SIDE ITSELF.** `jig.mage_cascade`'s header: *"NO dr IN OR OUT. A
consumer maps `verdict` onto its own trade side."* I asserted up→LONG as the producer's semantics
on 1027 and he answered *"that's not the mech"*; the mapping above is his, given in full, and it
lives in the consumer.

**THE COUNTER-OOB CADENCE IS EXEMPT FROM THE NO-ACTION HALF ONLY.** Joe 1027: *"narrow it - applies
only to cws1b counter oob"*. Its mismatch action is the knob:

| `LIN2_MISMATCH_ACTION` | what happens |
|---|---|
| `rev-trade` (THE BANK) | the walk ends and the opposite side opens at the exhaust bar + 1 |
| `close-only` | the walk ends and NO opposite side opens — reentry is left to open the next one |

`close-only` CURRENTLY LEAVES A GAP: `v4_reentry` is not wired into the chain, so nothing opens the
next trade and the chain stops at that exhaust. He was told and answered *"noted"*.

**THE MECHANIC HAS NO NAME BUT HIS.** I called it "suppression" in a report on 1027; that was my
coinage and it is gone. The cadence TAKES NO ACTION and the walk KEEPS WALKING — his words. The row
stage is `NO ACTION`.

**WHAT IT DID TO 2026-08-30**, the HIGH-first chain under the full table:

| the read | value |
|---|---|
| rev-trades | 16 |
| ended by the cascade mismatch | 6 |
| ended by the board review | 10 |
| capped at MAE 1.1 | 5 of 16 |
| capped AND ended by the mismatch | 5 of 5 |

That last row is what task 35 exists to explain, in his framing: *"the cadence that says 'the
cascade disagrees with you, get out' is firing on the trades that were going badly"*.

## 16. The barrage

HIS QUESTION, 1027, then his ruling:

> if there was a tolerance that allowed for low-side ws1r reversing to pseudo fit "inside the
> ws1Mage oob to ib" at 02:29, would it have detected a barrage of low-side reversals and declared
> exhaust? is there anywhere else in the day where ws1r reverses after the ws1Mage crosses to ib?

> so the tolerance alone will not select 02:29. It needs a second condition — the barrage itself is
> the obvious candidate, agreed — let's see the outcome as a standalone list with maemfe data

> bank the barrage results and wire the mech into the chain

**THE THREE CONDITIONS:**

| # | the condition |
|---|---|
| 1 | ws1Mage crosses from oob to ib on a side |
| 2 | ws1r reverses on the SAME side within `LIN2_BARRAGE_TOL_S` of that cross |
| 3 | at least `LIN2_BARRAGE_LINES` r lines reverse on that side between the cross and the ws1r reversal |

**BOTH THRESHOLDS ARE MEASURED OFF HIS 02:29 INSTANCE, not chosen and not swept:**

| the knob | value | what it is a measurement of |
|---|---|---|
| `LIN2_BARRAGE_TOL_S` | 70 s | the gap from the 2026-08-30 02:27:50 ws1Mage cross to the 02:29:00 ws1r reversal |
| `LIN2_BARRAGE_LINES` | 6 | the lines reversing LOW inside those 70 s — ws1, ws3, ws4, ws6, ws7, ws8 |

**WHY CONDITION 3 EXISTS.** Of 204 LOW-side ws1Mage ib-crosses on 2026-08-30, 94 have a ws1r
reversal inside 120 s and the median gap is 140 s. The tolerance ALONE selects nothing.

**THE BANKED LIST**, 2026-08-30, from `out/l2_barrage.md`. 8 instances, all LOW side, in 3 clusters.
No trade side is derived — the rise and the fall from the signal bar are both reported, and the
scale is sweep-pivots because this mech has no exit rule of its own:

| the ws1Mage cross | the ws1r reversal | gap s | lines | which | rise % | fall % | SP TF | the pivot | leg MFE % |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-30 02:27:50 | 2026-08-30 02:29:00 | 70 | 6 | ws1,ws3,ws4,ws6,ws7,ws8 | +0.877 | −12.842 | ws2Mage | 2026-08-30 02:36:10 | 0.667 |
| 2026-08-30 02:34:20 | 2026-08-30 02:34:45 | 25 | 7 | ws1,ws2,ws3,ws4,ws8,ws11,ws12 | +1.059 | −12.684 | ws2Mage | 2026-08-30 02:38:25 | 0.480 |
| 2026-08-30 02:34:45 | 2026-08-30 02:34:45 | 0 | 7 | ws1,ws2,ws3,ws4,ws8,ws11,ws12 | +1.059 | −12.684 | ws2Mage | 2026-08-30 02:38:25 | 0.480 |
| 2026-08-30 09:43:45 | 2026-08-30 09:44:45 | 60 | 8 | ws1,ws4,ws5,ws6,ws7,ws9,ws11,ws12 | +3.175 | −10.856 | ws20Mage | 2026-08-30 10:04:00 | 2.592 |
| 2026-08-30 10:04:45 | 2026-08-30 10:05:25 | 40 | 11 | ws1,ws2,ws3,ws4,ws5,ws6,ws8,ws9,ws10,ws11,ws12 | +3.110 | −10.912 | ws15Mage | 2026-08-30 11:52:25 | 1.840 |
| 2026-08-30 10:05:25 | 2026-08-30 10:05:25 | 0 | 9 | ws1,ws2,ws3,ws4,ws5,ws6,ws8,ws9,ws12 | +3.110 | −10.912 | ws15Mage | 2026-08-30 11:52:25 | 1.840 |
| 2026-08-30 19:06:20 | 2026-08-30 19:07:20 | 60 | 8 | ws1,ws4,ws5,ws7,ws8,ws9,ws10,ws11 | +0.170 | −10.035 | ws3Mage | 2026-08-30 21:01:40 | 2.640 |
| 2026-08-30 19:07:20 | 2026-08-30 19:07:20 | 0 | 8 | ws1,ws4,ws5,ws7,ws8,ws9,ws10,ws11 | +0.170 | −10.035 | ws3Mage | 2026-08-30 21:01:40 | 2.640 |

**THE RISE AND FALL CARRY NO HORIZON.** They are measured from the signal bar to the window end
2026-08-30 23:59:55, because no cap exists unless he sets one.

**HIS OBSERVATION ON THE FIRST ROW**, 1027: *"0234 is better than 0229, and 0229 did not have the
higher lines"*, and his correction of my reading of it: *"look at it this way: 0234 is lower than
0229, therefore the incoming SHORT collects more pnl. following that, the climb from 0234 to the
0244 high-side exhaust is more lucrative than 0229 to 0244"*.

| the read | value |
|---|---|
| instances with no ws9..ws12 line | 1 — his 02:29, which tops out at ws8 |
| instances remaining if `LIN2_BARRAGE_MIN_TF` = 9 | 7 |

`LIN2_BARRAGE_MIN_TF` IS 0 = OFF, because he has not ruled the value.

**THE 19:07 PAIR IS THE CASE HE FLAGGED AS UNRESOLVED.** Joe 1027: *"19:07 failing was expected: we
spent a lot of time trying to fit t3 to it and it's still unresolved"*. The barrage selects it
without being fitted to it.

**TWO GAPS ARE HIS, AND THE WIRING WAITS ON THEM:**

| # | the gap |
|---|---|
| 1 | what the barrage DOES when it fires — declare exhaust (his original *"declared exhaust"*), or fire as a cadence and let the board review decide |
| 2 | `LIN2_BARRAGE_MIN_TF` — 0 as banked, or 9, which drops his own 02:29 instance |

## 17. The MAE 1.1 cap — a report-only stop model

Joe 1027: *"the truth table: if MAE > 1.1, cap mae at 1.1 and print 0 in mfe"*.

| what it is | what it is NOT |
|---|---|
| a stop-loss model in the REPORT | a decision in the walk |
| MAE reported at the cap, MFE printed 0 | a cap on any measurement the walk reads |

The reasoning is his own: a trade whose adverse excursion passes the cap would have been closed
before it reached its favourable excursion, so the favourable number is not collectable and prints
0.

**IT IS THE ONLY CAP IN THE FORK**, and it exists because he set it. The standing rule is that no
cap, horizon, window or truncation exists in code OR in a diagnostic unless he specifies one.

**IT BREAKS THE CHAIN**, and he said so first: *"the mae1.1 pseudo-stop will break the chain, so we
need a way back in"*. Turning it into a real stop and wiring the way back in is task 39; `v4_reentry`
is the candidate and is not wired.

## 18. Open — and NOT decided by me

| # | what is open | whose |
|---|---|---|
| 1 | what the barrage does when it fires | his |
| 2 | `LIN2_BARRAGE_MIN_TF` — 0 or 9 | his |
| 3 | the rider's own reversal window in latch 2 | his |
| 4 | `LIN2_CAND_NOT_REVERSED` — 0, 1 or 2, and which wob the term reads | his |
| 5 | the ex-fence half of the live-tape validation — reconstruct from bars.jsonl, or capture a second run | his |
| 6 | whether the MAE cap becomes a real stop, and what reopens | his |
| 7 | `v4_reentry` wired into the chain, or ruled out | his |
| 8 | walking the cadence forward when gcws30Mage and gcws15Mage are both counter-oob and reversing | his, and he has named the knob `l2_walk_cadence_fwd` 2 |
