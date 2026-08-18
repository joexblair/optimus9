# ws-finisher spec

Opened 2026-08-17. Joe: *"we can begin the ws-finisher spec now. bank domTF, then purge it from
your memory - it's important that you don't conflate domTF with ws-finisher, and more important
that you don't bring any other logic into the is spec dev (besides what I directly ask of you)."*

**NOTHING FROM domTF IS IN THIS SPEC.** No stall, no handover race, no median line, no momentum
check, no tagged group, no HTF-curl. domTF's own spec is `domTF-finisher_spec.md` and it stays
there. The only thing this spec takes from that side of the house is the `domTF` state column,
read as given from `v_ws_fin_walk` — Joe 0817: *"don't spend time validating my domTF claims: I'm
manually validating against the raw data from the v_ws_fin_walk view."*

---

## the preamble, Joe 0817 verbatim

> Mage's purpose is to travel from source oob to target oob, in an endless loop, matching the ebb
> and flow of pxs.
>
> a smaller TF's Mage forms the tail of a higher TF's Mage
>
> when Mage is oob, it's strength will wane. this waning is the moment of weakness

## the weak-mage-tf mechanism, Joe 0817 verbatim

> when the market loses momentum and becomes weak, all of the finisher Mages will reverse (to
> continue matching pxs'a ebb and flow)
>
> wsf9of12 events are positioned to capture these reversal patterns. all weak-mage-tf data
> collection will take place when wsf9of12 fires
>
> when this reverse happens, the individual TFs will each have their own value for Mage. because a
> higher TF is slower moving than a LTF, a higher TF may not have reached target oob before the pxs
> reversal
>
> this disparity between a lower and higher TF Mage forms a load bearing decision: if a higher TF
> (eg 4) Mage's value is IB, and the lower TFs (1,2,3) are in the target oob, it proves that the
> higher TF Mages line is exhausted and a trade signal is created
>
> to find weakness, the code will scan the Mage values, upwards from TF1 to TF8, to find the first
> mage that is not OOB
>
> the first Mage that prints an IB value, is the weak-mage-tf

---

## THE RULE, as built

Producer: `jig.weak_mage_tf`. Runs at every `ws_fin_9of12` signal bar, and only there.

1. Scan ws1Mage, ws2Mage, ... up to ws8Mage, in that order.
2. A line counts as out of bounds if it was out of bounds at **any** bar inside the lookback
   window, not only at the signal bar.
3. The **weak-mage-tf** is the first line in the scan that was not out of bounds at any point in
   that window.
4. If every line from TF1 to TF8 was out of bounds inside the window, the weak-mage-tf is
   **None**. That is a result, not a failure. Joe 0817: *"no signals are created, but a stub needs
   to capture and report this when it happens."* Every such bar is kept in `ws_fin_weak_mage`
   with each line's seconds-since-last-out, so the reason is on the row.

### rule C

Joe 0817: *"if weak-mage-tf == None and domTF state is FREE, fire a trade signal"*.

### direction

Joe 0817: *"confirm you are using dr to identify the direction. adding new LONG/SHORT logic isn't
SRP - dr gives us all that we need for postitioning and trade direction."*

The producer reads `dr` and tests its sign. It holds no LONG/SHORT logic and never converts the
bias to a word.

### settled against Joe's own reads, 08-04

| signal bar | dr | weak-mage-tf | domTF | rule C |
|---|---|---|---|---|
| 10:53:35 | +1 | TF8 | FREE | — |
| 11:34:00 | −1 | TF2 | FREE | — |
| 08:02:50 | +1 | TF4 | BLOCKED | — |
| 04:49:15 | +1 | None | FREE | fires |

Joe read all four. On 04:49:15 he first said TF2, then: *"I agree with your 04:49 view -
weak-mage-tf = None"*.

---

## what is banked

| | |
|---|---|
| `jig.weak_mage_tf` | the producer |
| `build_ws_finisher.py` | runs it over every signal in `v_ws_fin_walk`, applies rule C, writes the table |
| `ws_fin_weak_mage` | one row per signal, including every bar with no weak-mage-tf. The knobs are in the unique key |

---

---

## the next layer, Joe 0817 verbatim — wsf-momoc and wsf-exhaust

> now we'll integrate wsf-momoc (ws strategy->finisher mech->momo or curl) and wsf-exhaust (stall
> OR reverse OR (cross into oob))
>
> -both events apply only to ws{tf}r
>
> -when wsf-momoc is true for the lines (at wsf9of12), no trade activity can happen
>
> -when wsf-exhaust is true for the lines (at wsf9of12), the weak-mage-tf will create a trade
> signal when ws{weak-mage-tf}x crosses r
>
> -wsf-momoc and esf-exhaust are exclusive - only one is active at any given time
>
> -"wsf-momoc is true for the lines" and "wsf-exhaust is true for the lines" are the 2 lessons that
> we need to learn. these 2 states are the output of the modelling

**NOT BUILT.** Nothing in the code produces either state. What is settled:

| | |
|---|---|
| the lines | `ws{tf}r` only. Not Mage, not x, not b |
| coverage | TF1 to TF8. Joe 0817 asked for the per-TF report to be repeated on TF1-8 after seeing TF2-10 |
| the two are exclusive | only one is active at a time |
| what wsf-momoc does | blocks all trade activity |
| what wsf-exhaust does | arms the weak-mage-tf. The trade signal then fires when ws{weak-mage-tf}x crosses ws{weak-mage-tf}r |
| **what is unknown** | how the per-line states combine into "true for the lines" — per line, or one verdict over all eight. Joe 0817: *"these 2 states are the output of the modelling"* |

### carry-forward

Joe 0817, the 11:34:00 case: *"11:34 is dr -1. at ~11:32, ws1r stalled and reversed. this state
should be carried forward to the 11:34."*

Joe on the window: *"there is no window for this mechanic - 'carried forward' = hold on to the last
momoc/exhaust state (which would be produced at 11:32, if the code was already built to handle
reversals)."* So the state is held indefinitely until the next one replaces it. There is no decay
and no expiry.

### Joe's answers to the six open questions, 0817

| # | question | Joe |
|---|---|---|
| 1 | is the reverse in wsf-exhaust the stall's reverse, or its own thing | *"we can't derive this yet. building a reversal producer is the next step"* |
| 2 | what separates stall from sideways | *"we need to know 1) the difference between the stall mech and the sideways mech, 2) why did 11:33:30 report 'none', while the prior bar was 'sideways' - ie why did it flip at that moment?"* — both measured below |
| 3 | is the wsf stall the same code as the domTF stall | *"domTF and wsf stall logic are the same. the only difference would be in the sampling interval - less width for smaller TFs"* |
| 4 | what sampling width for TF1-8 | *"we'll need to tune it based on the results. I don't know what results I'm looking for yet"* — OPEN |
| 5 | the carry-forward window | no window, hold the last state |
| 6 | which side does "cross into oob" mean | *"yes, same-side dr. eg dr +1 = crossing over 85"* |

### the answer to question 2, measured on ws1r 08-04

**stall and sideways measure different things.** Sideways is about the SHAPE of the fitted window:
a near-straight line whose slope is under the floor, with too little bend to be a curl. Stall is
about EXTREMES: N samples in a row with no new extreme. They can be true at the same time and
neither implies the other.

Proof on the same line and window — ws1r holds 17.11 from 11:31:40 to 11:32:10, which is a stall,
while the verdict reads `sideways` throughout at slope about -0.8. At 11:32:25 it prints 15.77, a
new low, and the stall breaks. `sideways` carries on to 11:33:30 regardless.

**why 11:33:30 flipped.** Read downward, one bar apart:

| bar | ws1r | slope | fit | bend | turning point | verdict |
|---|---|---|---|---|---|---|
| 11:33:25 | 16.86 | -0.563 | 0.494 | 14.05 | 0.985 | sideways |
| 11:33:30 | 16.86 | -0.615 | 0.520 | 17.65 | 0.883 | curl |

Two gates flip on the same bar. The bend measure (bend x 0.25) goes 3.51 to 4.41, crossing the 4.0
floor; the turning point moves from 0.985, outside the 0.05-0.95 band, to 0.883, inside it. So the
raw verdict is `curl`. The gated verdict then prints `none`, because for a downward read the gate
requires the bend to be negative and it is +17.65 — the line is bending UP under a downward read.
That is the reversal Joe saw at 11:32, and the gate throws away the number that proves it.

**This is why the reversal producer is the next step, and why the momo refactor comes first.** See
`docs/handover_momo_refactor.md`.

---

## KNOBS

| knob | value | what it does |
|---|---|---|
| `WMT_LOOKBACK_S` | **120 seconds** | the lookback tolerance. A Mage that was out of bounds at any bar inside this window still counts as out. Joe 0817: *"add a lookback tolerance to capture Mage values that were recently oob. knob:120sec"*. At the 5-second grid that is 25 bars, the signal bar included |
| `WMT_TFS` | **1 to 8** | the timeframes the scan walks, in order. Joe 0817: *"confirmed: TF1 to TF8"* |
| `WMT_SAME_SIDE` | **True** | with it on, a line's out-of-bounds readings only count on the side `dr` points at. With it off either side counts. Joe 0817: *"unsure. create a knob for it. default to same-side"*. The definition of what same-side means is mine and is untested |
| the boundaries | **85 / 15** | read from `optimus9_system`. Joe 0817: *"85/15 is good for now, BUT the final spec will have fuzzy logic applied to boundaries. the final spec will be model based"* |

### knobs this spec does not own

| value | where it is set | note |
|---|---|---|
| everything that makes a wsf9of12 bar | `build_ws_fin.py`, `jig.py` — listed in `docs/domTF-finisher_spec.md` → KNOBS | the signal bars are an INPUT here. Changing any of them changes which bars this spec runs on, but they are not knobs of this spec |
| the `domTF` state column | `v_ws_fin_walk` | read as given. Joe 0817: *"don't spend time validating my domTF claims"* |
| `MOMO_CHECK_TFS` **2 to 10** | `optimus9/analysis/jig.py` | coverage for the ad-hoc momentum reports Joe asks for by timestamp. Joe 0816: *"permanently include ws[2,3,4,5]r in the momo check"*, then *"reduce coverage: ws2 to w10"*. The wsf per-TF reads use TF1 to TF8 instead |

### knobs this spec needs and does not have

| knob | state |
|---|---|
| the wsf stall's sampling width for TF1-8 | UNSET. Joe 0817: *"less width for smaller TFs"* and *"we'll need to tune it based on the results. I don't know what results I'm looking for yet"* |
| whatever the reversal producer needs | UNSET. Not built |
| how per-line states become "true for the lines" | UNSET. Joe 0817: *"these 2 states are the output of the modelling"* |
