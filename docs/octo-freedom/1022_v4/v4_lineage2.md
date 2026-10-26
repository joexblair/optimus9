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

| the knob | value | his words |
|---|---|---|
| `v4mom_maxTF` | 12 | *"v4mom_maxTF = 12"* |
| `v4mom_fnc` | 100 − 20 = 80 → (20, 80) | *"identical to the banked RMOM_FNC 80. Same knob - yes"*. So it IS `RMOM_FNC`, and moving one moves both |
| `lin_hop` | 2 | *"lin_hop = 2"* |
| the t1cadence grace | 120 s | *"the 2-minute grace in t1cadence -knob"* |
| the t3cadence fraction | 0.75 | *"int(round(75%))"* |
| `v4cadence_fnc` | DROPPED | *"v4cadence_fnc -drop"* |

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
| the arm race | ws4r EMERGING; cws1b, cws1r, cws2Mage, cws2r CLOSED |
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
whole ladder"*. That is NOT `jig.away_toward`, whose perspective is ws1Mage's by his own 1019
ruling for a different mech, so lineage2 computes its own tag and the shared producer is untouched.
The DIRECTION is still each TF's own Mage trajectory.

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
