# fdm2 - the machine as he ruled it on 1103

HIS NAMING. *"yes, but don't delete the fdm work. let's call this sandbox `fdm2`"*. The old
`fdm-cadence` body stays untouched in `1103_fdm/`. This file carries ONLY the machine that replaced
it. Nothing from the old body is folded in.

HIS OFFLINE SPEC NOTES ARE OUT OF THE SANDBOX. *"we're building in a sandbox presently - so theses
fdm_spec notes have no place"*. Every line below is cited to HIM, from chat, not to a notes file.

WHAT THE OLD BODY GAVE UP ITS PLACE TO. His six answers, verbatim:

| # | the question I raised | his ruling |
|---|---|---|
| A | does today's bimodal logic replace the old `fdm-cadence` body | *"yes, but don't delete the fdm work. let's call this sandbox `fdm2`"* |
| B | there is no exit except a rev-trade | *"add the typical mae1.1 stop, and let the router decide if a rev-trade signal means CLOSE then OPEN, or just OPEN. if it's close then open, consume 2 bars. if it's only open, consume 1 bar"* |
| C | is `fdm-10x-fallback` still its own mech | *"not in use. the new 'ws10x-cross triggering a reversal check' is the next evolution of ws10x-cross"* |
| D | which fence does step 1 use | *"ex 20/80"* |
| E | no stop | *"covered in B"* |
| F | the rev-trade's own open bar | *"covered in B"* |

## THE TRADE LIFECYCLE

A trade exists or it does not. There are exactly three transitions.

| from | the event | to |
|---|---|---|
| FLAT | the fdm re-entry fires | a trade, side from the gcws30b window's oob side |
| a trade | a rev-trade signal | the opposite trade. CLOSE then OPEN, 2 bars |
| a trade | the mae1.1 stop | FLAT. The re-entry is the only way back |

- the first trade of a chain comes from the re-entry. Verified at 2026-08-03 00:41:30, side +1 high -> SHORT.
- no cadence event is evaluated while FLAT. The cadence is tested on the live trade's target side, and FLAT has no target side.
- a rev-trade from FLAT cannot occur, so the router's "just OPEN, 1 bar" arm is unreachable in fdm2 today. It is built because he ruled it.

## THE BAR ACCOUNTING

Joe B: *"if it's close then open, consume 2 bars. if it's only open, consume 1 bar"*.

| the router's case | the signal bar | the CLOSE price bar | the OPEN price bar | bars consumed |
|---|---|---|---|---|
| CLOSE then OPEN | s | s + 1 | s + 2 | 2 |
| just OPEN | s | - | s + 1 | 1 |

- MY READING OF "consume 2 bars", stated as mine: the two bars are s+1 and s+2, one each for the close and the open. The alternative is both at s+2.
- the old chain closed at s+1 and opened at s+1 - ONE bar for both. That is the number this ruling moves.
- `v4_signal.fire_bar` is s+1 and stays the only-OPEN arm's bar, unchanged.

## THE DECISION AT A CADENCE EVENT

```
at a same-side cadence event
-are there same-side ex-20/80 `towards` lines in the timeframes above ws3?
--NO  -> rev-trade
--YES -> walk to the next same-side cadence OR the same-side ws10x-cadence, whichever is first

if the ws10x-cadence fires first
-count the lines reversed since the cadence event, over the trade's ex-20/80 population, ws3..ws30
--pct >= 40% (fdm-ws10x-cad-grace) -> the ws10x-grace-walk starts, 5 minutes from the ws10x-cadence
---re-count every 5 s bar, the same running count, carried on from its value at the ws10x-cadence
----pct >= 50% -> rev-trade at that bar
----the 5 minutes expire -> no action, wait for the next cadence or ws10x-cadence
--pct < 40% -> no action, wait for the next cadence or ws10x-cadence
-only ONE ws10x-cadence per walk. No second one after a grace expiry
```

| the piece | the ruling |
|---|---|
| step 1's range | above ws3 IN TIMEFRAME - ws4..ws30 |
| step 1's fence | ex-20/80, his D |
| step 1's two tests | ex-20/80 AND `towards`, both, on the trade's target side |
| the count's population | ws3..ws30, the lines ex-20/80 at least once during the trade. 28 lines |
| the count's origin | the cadence event, not the ws10x-cadence |
| the grace clock's origin | the ws10x-cadence |
| the grace re-count cadence | every 5 s bar. His own correction: *"the lift-off reversals are emerging, so we should be testing per 5s bar"* |
| why the count does not reset | *"why would it reset? the grace fires on a low pct, and the low pct can't be derived until the ws10x cadence"* |
| under 40% | no branch. No action, wait |

## THE TWO VERIFIED CASES

| the ws10x-cadence | the pct at it | the rev-trade bar | the pct there |
|---|---|---|---|
| 2026-08-03 10:12 | 10 of 21 = 47.6% | 2026-08-03 10:13:00, ws24 | 11 of 21 = 52.4% |
| 2026-08-03 18:52:55 | 17 of 22 = 77.3% | 2026-08-03 18:52:55, the first bar | the same bar |

- both are on 08-03, a day he has surveyed. By his own rule that is where the holes are least likely to be.

## WHAT IS BUILT

| the piece | where | state |
|---|---|---|
| the cadence event, his revised preamble | `1103_fdm/fdm_cadence_census.py:cadence_events` | runs. Lands on his own 6 trade times + 1.0 min |
| the ws10x race, 3 candidates | `1103_fdm/fdm_cadence_census.py:x10_race` | runs at wob 24 and 36, both |
| the towards / reversal census | `1103_fdm/fdm_cadence_census.py:census` | runs |
| the fdm re-entry | `1022_v4/v4_fdm_reentry.py` | banked. Verified 2026-08-03 00:41:30. HIS 1104 x-cross mod is IN and live - see `fdm2_reentry_machine.md` |
| the mae1.1 stop | `1022_v4/v4_fdm2.py:stop_bar` | carried by value from `v4_chain`. ON by default |
| the bimodal decision | `1022_v4/v4_fdm2.py:step1` + `walk` | built, runs |
| the grace walk | `1022_v4/v4_fdm2.py:walk` | built, runs. Per 5 s bar, population frozen |
| the rev-trade emitter | `1022_v4/v4_fdm2.py:walk` -> `v4_signal` mech `fdm2-rev-trade` | built |
| the cadence-to-cadence chain | `1022_v4/v4_fdm2.py:legs` + `1103_fdm2/fdm2_chain.py` | built, runs |

## HIS 1103 ANSWERS TO THOSE THREE - all closed

| # | the line | his ruling |
|---|---|---|
| 1 | the ws10x race's wob | *"now that we have the grade period, we can leverage a smaller wob: use 24"*. `FDM_X10_WOB` 24 bars = 120 s. 36 is the other arm |
| 2 | the mae1.1 stop's default | *"yes, move it to defualt"*. `FDM_MAE_CAP` 1.1, always applied. No `W_MAE_CAP=on` gate, unlike lineage2's `LIN2_MAE_CAP` |
| 3 | does the population grow during the grace walk | *"no"*. Frozen at the ws10x-cadence over [the trade's open, the ws10x-cadence]. Both his verified cases carry a constant denominator, 21 at 1012 and 22 at 1841 |

## THE CADENCE PREAMBLE, AS IT NOW STANDS

HIS 1103 CORRECTION: *"ws1r, ws2r, ws3r are all qualifying lines"*, with the fdm line he handed
over beside it - *"add this (from fdm) to our sandbox"*:

    cadence windows open when ws1r or ws2r or ws3r oob AND are nestled inside of ws1Mage or
    ws2Mage at any time during ws1Mage/ws2Mage's oob excursion
    -#nestled: ws1Mage or ws2Mage is deeper oob when ws1-3r is less deeper oob

| the test | whose words | state |
|---|---|---|
| the **nestle** - a ws1,2Mage deeper oob than an oob ws1,2,3r, any pair, no TF match, latching for the window | his, and `nestle` is HIS NAME | built |
| ws3Mage ex-25/75 while ws1b is oob | his 1103 preamble. HE HAS NOT NAMED IT | built, at `FDM_M3_FNC` 25.0 |
| "ws1Mage, ws1b, ws1r are all oob at some time during ws1b's oob excursion" | his 1103 preamble | **DROPPED AS IMPLIED.** Read with his correction the nestle proves every clause of it: an oob r among ws1,2,3r, a ws1,2Mage deeper than it (so itself oob), inside a ws1b oob run |
| `t1` / `t2` / `t3` | MINE, and they collided with lineage2's cadence TYPES | dropped on his *"what is t1 and t2?  if they are the cadences from the earlier specs, then drop them"* |

WHAT THE DROPPED LINE COST. As written it required ws1r specifically, and it rejected
2026-08-03 16:45:00 - ws1r's deepest reading in that 2m55s excursion was 20.24 against the 15.0
oob fence, while ws2r reached 7.14 and carries the nestle on its own.

| the 1644 LOW reading | before his correction | after |
|---|---|---|
| cadence events in 16:44:00 .. 18:41:00 | 0 | 1, at 2026-08-03 16:45:00 |
| the verdict | NO CADENCE EVENT | rev-trade 2026-08-03 16:47:40, ws10r, 9 of 10 = 90.0% |
| step 1 at the cadence event | - | 7 of 27 |

It is the only one of the seven decision paths that moved. It also closes gap C from his own
answers - 1644 LOW had 1.95 h with no decision point, and the fallback is ruled out of use.

## THE EXCURSION ANCHOR IS ws1b - SETTLED 1103

| his ruling | what it closes |
|---|---|
| *"ws1Mage and ws2Mage oob's job is to nestle ws1,2,3r"* | the Mage lines do not anchor the window. The excursion is ws1b's, his 1103 revised preamble, and that is what the code reads |
| *"we're on closed-prev bars so they always return to ib on the same 1min bar"* | the window's close and the preamble's *"ws1b to ib"* are the SAME bar. Nothing to choose |
| *"the real reason why I use ws1b is this: gcws30b swings with more force than gcws30Mage, so it prints ex-5/95-fence excursions that are meaningful. this was useful to us in a previous build, so I'm holding on to it in case I need it again"* | why the b line, not the Mage. His reason, kept here so it is not re-litigated |
| *"ws3Mage is settled on 25/75"* | `FDM_M3_FNC` 25.0. The 20/80 reading of ws3Mage belonged to the old body and is not in the sandbox |

HIS VERBATIM ws1b LINES, all of them:

| the source | his line |
|---|---|
| his 1103 chat, transcribed in `1103_fdm/fdm_cadence_census.py` | *"a cadence event prints on ws1b to ib, IF ws1,2Mage was more deeply oob (further away from 50) than ws1,2,3r during ws1b's oob excursion"* |
| same | *"-ws1Mage, ws1b, ws1r are all oob at some time during ws1b's oob excursion"* |
| same | *"-ws3Mage must be ex 25/75 fence while ws1b is oob"* |
| same | *"--this cadence event can only be tested on target-side"* |

Those four lines are his whole ws1b spec for the sandbox. The two further ws1b lines in his offline
notes belong to the old body's walk-until and are not read here.

## HIS INCOMING-ONLY RULE IS CONVERSATIONAL, NOT A SPEC CHANGE

*"from now on, I'll only refer to the 'incoming' trade, which matches your banked 'SHORT hunts the
low oob'"* / *"completely delete my 'low side long' statement"* / **and then**: *"that was a rule
for me to adhere to - not for the code or the spec"*.

NOTHING IN THE MECH MOVES. The side at a cadence event stays the OUTGOING trade's target - the
trade being closed - which is what the verification table has always used and what reproduced his
own six trade times at +1.0 min each.

THE "low side LONG" STATEMENT IS DELETED, and with it the only thing that set 0702's side. The
day's first trade has no prior trade to take a side from, so it runs BOTH sides again.

## OPEN - WHAT THE BUILD SURFACED

| # | the line | why it matters |
|---|---|---|
| 4 | the reversal's STAMP vs its lift bar | `1103_fdm`'s census counted the RAW lift-off bar. `jig.lift_off`'s own contract puts the event 7 bars = 35 s later - *"the consumer adds the wob"* - so the census carried 35 s of lookahead. `v4_fdm2` counts the stamp. Any census number where a lift landed inside a window's last 7 bars will differ |
| 5 | `FDM_X10_FRM` - must the race's CROSS follow the cadence event, or only its CONFIRM | at `cross` (the default, on precedent - the census used it and his 1841 18:52:55 came from it) a race already in flight at the cadence event is not that walk's ws10x. At `confirm` it is. On the first leg this moved the 01:42:00 walk's ws10x from 01:44:05 (to ib) to 01:43:45 (to ws10Mage) |
| 6 | a cadence event landing INSIDE the 5-minute grace walk | he ruled the expiry and the <40% branch, not this. MY BOUND: the grace walk stops at the bar before the next cadence event, because *"the mech will be walking from cadence event to cadence event"* makes the cadence the spine and skipping one contradicts it |

## STRUCTURAL, DECIDED BY ME AND STATED

- fdm2 gets its own chain driver. `1022_v4/v4_chain.py` imports `v4_lineage2` at module level, and importing it would drag the whole lineage2 stack into a greenfield build. The leg scoring, `stop_bar` and the flat-after-stop handling are the chain's, not lineage2's, so they are carried by value into fdm2's driver.
- `stop_bar`'s intra-bar tie convention carries unchanged: inside one 5 s bar the high and the low are both there and their order is unknown, so a bar that breaches the cap is the stop even if it also moved favourably. That convention is MINE and it is the conservative one.
- `1030_mom_fence/chain_lift_2d.py` keeps its `v4_fdm_reentry` import for now - that is lineage2's sealed driver and fdm2 does not read it. The contamination is one-way and it stops being a question once fdm2's driver exists.
