# Handover — manual board predictions + rsd

**Written** 0802 18:45 UTC · **For** a new session with singular focus
**Scope** manual trading predictions from the board reads, and applying what they teach to **rsd**.
**Primary method** §3.2 — **learn in REALTIME**. The tape lookback is a *comparison aid at decision time*, not the dataset.
**Success is defined** — §3.3. `work = price moves positively >= 0.9%`.

> Joe 0803: *"we're not moving the causal jig to a new session, just your manual trading predicitions"*

**NOT in scope.** The causal jig (`build_rpl_jig.py`), exhv2 internals, the slip/gate work,
task #44, task #46, the jig-vs-batch backtests. All of that **stays in the current session**.
The jig keeps running there; this session **reads** its output and **writes** predictions.

---

## 1 — What this session does

| | |
|---|---|
| **reads** | `rpl_jig` heartbeat rows — the full board, every 5 s |
| **writes** | `rpl_jig_pred` — falsifiable claims, committed before the outcome is knowable |
| **writes** | `rpl_learn` — what held, what failed, with evidence counts |
| **reads** | `rpl_seed` — Joe's verbatim words. Never edited |
| **never touches** | the jig process, `build_rpl_jig.py`, exhv2, the gates |

- the jig writes a heartbeat every 5 s with 37 lines. That is the board
- predictions are made **from** the board, not from the mechanic
- **do not restart or modify the jig from this session.** If it dies, say so — it belongs to the other session

---

## 2 — Joe's seed notes — VERBATIM

All 23 rows live in **`rpl_seed`**, keyed by `sd_topic`. The four that define the reads:

### GRAVITY + WEAKNESS — `sd_topic='gravity'`
> *"I see the pegged Mages as gravity attracting the "weaker" s15r/m/x - the Mage will pull the other
> lines up to them if r and m are on the other side of the board. the nuances that might push back are:
> -s15x made a huge up move @ ~07:15, while s15m stayed mid board - this is a sign of weakness in the
> other direction: m is not strong enough to push up -s1r @ 07:45 failed to breach hi, another sign of
> weakness. how this plays out is yet to be seen, but if you woke up every minute and spend time looking
> at weakness and gravity between lines, I think you could build a model"*

- **two** weakness forms: x excursion with m mid-board, **and** a line touching a boundary and failing to hold

### BOBBING — `sd_topic='bobbing'`
> *"use all of the lines in exhv2 + the LTFs that we've spun up. tip: if a Mage is bobbing on a boundary
> line, a higher TF Mage is making it's way to the same boundary <-this is gold: now you know which HTF
> Mage to track to its oob"*

- it **names which** HTF Mage to watch. It is a pointer, not a timing signal

### GATHER — `sd_topic='gather'`
> *"one last thing before I bail: if you want to know if a line is going to reverse, take guidance from
> the smaller TFs (gcs5, gcs15, s30, possibly s1). their lines will gather to a boundary before they push
> away from it, and this momentum feeds into the TFs above it. obviously nothing is pefect (ultimately,
> trading is trying to predict human behaviour), but you'll get to understand when they're committed
> (tredning) and when they're unsure (sideways)"*

- gather is a property of the **set** at a small TF, not of one line
- the read is **committed vs unsure**, not up vs down

### HTF DIAGNOSTIC — `sd_topic='htf'`
> *"last tip: if your predictions don't pan out, start by looking at the HTFs (>22) - you might find
> something bigger cutting an opposing path. night"*

- run this on a **failed** call, before re-reading the LTFs

### METHOD — `sd_topic='method'`
> *"stay loose - this is as much fuzzy logic as it is science"*

> *"that was my driver: if you predict without lookahead, you'll evolve under internal friction - a good
> way to grow"*

- the friction **is** the point. The hit rate is secondary

---

## 3 — The prediction record, and the uncomfortable part

**58 scored calls, 30 right / 28 wrong / 1 void = 51.7%.**

| category | n | right | rate |
|---|---|---|---|
| **MECHANIC behaviour** | 8 | 8 | **100.0%** |
| GATE arithmetic (r pair vs thresholds) | 13 | 7 | 53.8% |
| GRAVITY / WEAKNESS | 4 | 2 | 50.0% |
| GATHER | 6 | 2 | 33.3% |
| **INVENTED tells (mine)** | 6 | 2 | 33.3% |
| **BOBBING** | 4 | 1 | **25.0%** |

- **caveat**: the bucketing is mine and 17 of 58 span categories. Indicative, not exact
- **I initially wrote up this record as "Joe's reads net positive, my invented tells 0 for 3". That is false.** The split above is the corrected version, and it is in `rpl_learn`

**The finding that matters for the new session:**

- the **shapes are real** — gravity, weakness, bobbing and gather all appear on the board exactly as described
- **my conversion of a shape into a falsifiable race was not better than chance**
- the only category above chance is the one where I predicted **what the code would do**, not what the board would do

---

## 3.1 — Joe's correction to my diagnosis. READ THIS BEFORE ACTING ON §3

I concluded from the above that the fault was my threshold-picking. **Joe says that is wrong:**

> *"- my conversion of a shape into a threshold and a horizon was not better than chance"
> -this just means the shape needed to add more HTF or LTF line postitioning <- ie gather more data and
> find the patterns*

- the shape was **under-specified**, not badly thresholded
- a read stated as **two lines** (x vs m, LTF vs HTF) cannot carry a threshold until the **positions of the other lines** are folded into it
- **the fix is more data per shape, not better guessing**

**So the work is not "learn to pick levels". It is "state the shape with enough lines in it that a level follows."**

- practical form: a call should not be *"x15 falls below m15 before m15 reaches 70"*. It should be
  *"x15 falls below m15 **given** h30/h45/h60/h90 at these positions and mg5/mg15/mg30/mg1/mg2 at these"* —
  and the level comes from what that **configuration** has done before
- which is exactly what §3.2 is for

---

## 3.2 — THE METHOD: realtime learning, with the tape as a comparison aid

> **CORRECTION 0803.** An earlier draft of this section called the tape "the dataset" and realtime "the
> trigger". That is backwards. Joe: *"you'll be learning only in realtime in the new session"*. The call is
> made live and committed live; the lookback informs that call, it does not replace it.

**Why that also settles the lookahead worry**

- the call is committed at bar **T**; the analogues are all strictly **before T**; the outcome resolves **after T**
- there is **no fitting loop over the future** — the standard contamination cannot occur
- **the residual risk is different and smaller: overfitting, not lookahead.** Running several lookups and then
  picking whichever shape gives the nicest answer is still causal but it is curve-fitting to the tape
- **guard: commit the shape BEFORE running the lookup.** Same discipline as the insert guard in §5.1


> *you don't have to do this learning exclusively in realtime - there's 2.5 months of tape that you can
> scan: when you have a live scenario in front of you, look back to find a group of similar situations in
> the tape - see what happened to the historical scenarios. if you don't get the same outcome as the
> historical scenarios then find the differences between the lines and their positions on the boards.
> when you review the history, look everywhere for crosses - they are the moments when things really
> happen, and what you should be looking for in your realtime predictions*

**The loop, in order:**

1. **live scenario in front of you** — the current board
2. **find a GROUP of similar situations in the tape** — not one analogue, a group
3. **read what happened to them** — that is the prediction, and it comes with an n
4. **if the live outcome differs**, diff the **line positions** between the live board and the historical ones. The difference IS the missing conditioning line from §3.1
5. **look everywhere for CROSSES** in the history — *"they are the moments when things really happen"*
6. **crosses are what to predict live**

**Why this matters for the numbers in §3:** 58 realtime calls took 10 hours. One tape scan yields
**thousands** of analogues per shape. The reads sit at chance because **n was far too small to have
found the missing lines** — not because the reads are wrong.

**The tape**

| | |
|---|---|
| span | **05-07 00:00 → 07-31 23:59:55** |
| bars | **1,486,080** at the 5 s grid |
| duration | ~2.8 months |
| pre-05-07 | synthetic, deleted 0802. Do not go back further |

**How to get a historical board** — the jig's 37 lines rebuild over **any** window:

```python
import build_rpl_jig as J
from optimus9.analysis.jig import Jig
with Jig(end_ms, hours=J.WIN_HOURS, warmup=J.WIN_WARMUP, overrides=J.LINES) as j:
    ts  = np.asarray(j.W.ts, np.int64)
    m4  = np.asarray(j.W.line('jM4'),  float)     # s4Mage
    r15 = np.asarray(j.W.line('jr15'), float)     # etc, all 37 names in J.LINES
```
- `WIN_HOURS` = 24, `WIN_WARMUP` = 24 → a **72 h** window. Widen for a longer scan
- this is the **same call the backtest harness uses**, so a historical board is identical to a live one
- a full build takes **~2 min** — run it in the background, never in the foreground

**Crosses — where to hunt**

- the jig only computes **two** cross pairs today: `jx15 × jm15` (the anchor) and `jg15x × jg15m` (the confirm)
- Joe says **everywhere**. The 37-line set gives far more pairs than that
- use `cau.cross_wob(A - B, 0.0, dir, R.WOBN)` then take rising edges — `wob_n` = 9 bars = 45 s of wobble tolerance
- **caveat**: a `cross_wob` cross is confirmed 45 s **after** it happens. In history that is free; live it is a lag

---

## 3.3 — WHAT "WORKS" MEANS — Joe's definition, and the gap in it

> *you'll be learning only in realtime in the new session. the goal is to find the realtime patterns that work
> (work = price moves positively >=0.9%) through a mix of look back comparision and your own learnings*

**`work = price moves positively >= 0.9%`**

### The miss this exposes

| | |
|---|---|
| predictions written 0802 | **63** |
| mentioning `pxs` or price | **0** |

- every call was **line vs line** — x15 vs m15, max r vs 83.0, h30 vs h60
- **the entire 63-call record cannot be scored against the thing that matters**
- **the new session must predict PRICE, conditioned on the line configuration.** Not lines

### What 0.9% looks like — 0802 tape

| | |
|---|---|
| heartbeat bars | 9,318 · 05:52:50 → 19:09:15 |
| pxs range | 0.12806323 … 0.13094233 = **2.25%** peak-to-trough |
| bars with a forward **up** move ≥ 0.9% | **4,805 / 9,318 = 51.6%** |
| bars with a forward **down** move ≥ 0.9% | **5,298 / 9,318 = 56.9%** |

- no horizon applied — "forward" means to the end of the run, per Joe's no-caps rule
- one day, one regime

### RESOLVED 0803 — Joe's full definition

> *not before - after. after your prediction, does price move (in the direction of your prediction) more than 0.9%*
> *-to keep it sane, you need to know where to predict from: the answer is, predict when s4Mage is oob*
> *-the prediction's direction doesn't rely on the OOB side. sometimes low s4M oob will be a LONG prediction, but if
> s15 and s22 have momo then s4M will stay oob for an extended period - that's an opprtuinity to pick up a short
> trade (while you follow the momo)*

**Three rules, all binding.**

| # | rule |
|---|---|
| **1. MEASURE** | 0.9% is measured **AFTER** the prediction, in the **prediction's own direction**. One-sided. **No opposing leg. No horizon.** My "before −0.9%" framing was wrong |
| **2. TRIGGER** | **only predict when s1M OR s2M is OOB.** In-bounds = no prediction. Do not fabricate a trigger to fill a watch cycle. **SCOPE: this is MY PREDICTION trigger only — `exhv2` is untouched** (see box below) |
| **3. DIRECTION** | **does NOT follow the OOB side.** An OOB-lo can be a LONG. But if the r lines have **momo**, the Mage stays OOB for an extended period — trade **WITH** the move (SHORT on an OOB-lo). No momo = exhaustion = reversal. **Read THREE r lines: s4r, s15r, s22r** (Joe 0803) |

- rule 3 is the same distinction as `momo` vs r-pred in exhv2, and it matches the standing note: *x crossing a
  NON-established r is exhaustion; established r means continuation*
### ⚠ SCOPE — the trigger change is for PREDICTIONS, not for exhv2

> Joe 0803: *"we've conflated - I was suggesting s2M or s1M for your realtime trading, not for exhv2"*

| | trigger |
|---|---|
| **my realtime predictions** | **s1M OR s2M OOB** |
| **`exhv2` walk** | **s4Mage OOB for 240 s — UNCHANGED** |

- **verified 0803, no code contamination**: `build_exhv2.py:300` and `build_rpl_jig.py:263` both still call
  `oob_qualified(M4, HI, LO)`. `jg_oob_side` / `jg_qualified` are still derived from `M4`
- `jMg1` / `jMg2` appear in `build_rpl_jig.py` only at `:301-302` (banking) and `:272` (the GATHER spread
  measure). **They drive nothing in the mechanic**
- the conflation was in this document and one `rpl_learn` row. Both corrected

### The trigger change — 2.38x the moments, not 1.10x

> *make it s2M oob or s1M oob - it will give you more opportunities to learn. for LTF predictions to work
> effectively, you'll need to consider s4r's momentum as well as 15 and 22*

0802 tape, 9,502 heartbeat bars, HI 85.0 / LO 15.0:

| trigger | bars | % | **rising edges** |
|---|---|---|---|
| s4M OOB *(old)* | 4,158 | 43.8% | **79** |
| s1M OOB | 3,423 | 36.0% | 153 |
| s2M OOB | 3,809 | 40.1% | 158 |
| **s1M OR s2M OOB (NEW)** | **4,582** | **48.2%** | **188** |

- **the gain is in EDGES, not bars** — bars only 1.10x, edges **2.38x**. An edge is what a prediction moment
  actually is; the faster Mages cross their boundaries far more often
- **NO CODE CHANGE NEEDED.** `jg_mg1` and `jg_mg2` (bb 37|0.7 @ TF 1.0 / 2.0 min) are banked on every heartbeat

**Computing momo for rule 3** — `s4r` / `s15r` / `s22r`, from the banked series:

| knob | value |
|---|---|
| `MOMO_SAMPLES` | 12 |
| `MOMO_STEP_BARS` | 60 bars = 5 min |
| history required | **660 bars = 55 min** |
| `MOMO_SLOPE_MIN` | 1.0 r-units per 5-min sample |
| `MOMO_R2_MIN` | 0.50 |
| `LEVEL_SLACK` | 13.9 |
| `CURL_ARC_MIN` | 4.0 |

- **do NOT `import build_exhv2` to get `momo()`** — it pulls the whole RPL chain and takes over 2 minutes.
  Reimplement the formula against `jg_r4` / `jg_r15` / `jg_r22`

### Can the mechanic even reach 0.9%? — YES, on 36.7%

`rpl_dominoes`, n = 147:

| | |
|---|---|
| MFE median | **0.568%** |
| MFE mean | 0.848% |
| MFE p90 | 1.868% |
| MFE max | 5.266% |

| threshold | rows | rate |
|---|---|---|
| **MFE ≥ 0.9%** | **54 / 147** | **36.7%** |
| MFE ≥ 0.5% | 80 / 147 | 54.4% |
| MFE ≥ 0.3% | 101 / 147 | 68.7% |
| MFE ≥ 0.163% *(the 0802 live trade)* | 120 / 147 | 81.6% |

- **the 0802 live exit at 0.163% MFE sits at the 19th percentile.** It was a poor instance, not a typical one
- **this corrects what I wrote one cycle earlier**, when I said that excursion size might be typical and no exit rule could fix it

**And it inverts the #45 hop finding:**

| split | MFE ≥ 0.9% | MFE-side rate |
|---|---|---|
| hopped (`dm_hops` ≥ 1) | **25.0%** (11/44) | **61.4%** |
| direct (`dm_hops` = 0) | **41.7%** (43/103) | 25.2% |

- **the hop selects for the correct SIDE and for a SMALLER excursion.** Side and size are different objectives
- if the target is 0.9%, the hop is the **wrong** filter despite being the better side detector

### The prediction form the new session should use

```
PRECONDITION: s4Mage is OOB at this bar.  If not, DO NOT PREDICT.

DIRECTION:  s15/s22 momo present -> trade WITH the move that put s4M OOB (continuation)
            s15/s22 momo absent  -> trade AGAINST it (exhaustion)

CLAIM:      from THIS bar, pxs moves >= 0.9% in the predicted direction.
            No opposing leg. No horizon. It either gets there or it has not yet.

BASIS:      the full configuration - x/m/M/r at s4/s15/s22 + mg5/mg15/mg30/mg1/mg2
                                    + s1r/s30r + h30/h45/h60/h90
```
- the **claim** is about price, one-sided
- the **basis** carries the full configuration, per §3.1
- the **lookback** supplies the rate at which that configuration has produced 0.9% before
- **scoring**: `right` when it reaches 0.9%. It cannot be scored `wrong` by a threshold — only by
  a later ruling from Joe on when to give up on an open call

---

## 4 — What held, what failed

Full detail in **`rpl_learn`** — filter `ln_scope IN ('predict','both')`.

| read | status | conf | the actual result |
|---|---|---|---|
| BOBBING | held | 70 | **six** LTF pushes at HI failed to propagate before the seventh carried the whole ladder. #28 right, #31 wrong, #57 wrong |
| GATHER | held | 65 | works **both** directions. #23 right in 21.4 min, #43 right taking h60 to a new session low |
| WEAKNESS | held | 60 | reliable as a **shape** (#29 right 7.6 min, #36 right 1.8 min), useless as a **push predictor** (#47 wrong) |
| GRAVITY | **open** | 40 | h90 held a 7-pt band across ~3000 bars, then broke below it and led **down**. A pegged line attracts only while pegged |
| HTF-follow *(mine)* | **falsified** | 85 | #49. The ladder rose with push 12 and the push failed. Marks participation, not a carrier |
| x-over-m gap as carrier tell *(mine)* | **falsified** | 90 | #47. Push 11 carried at gap **+78.8**; push 7 carried **converged**. Both extremes carried |
| trajectory extrapolation *(mine)* | **falsified** | 90 | #51. s15r fell 12 pts in 20 min then stopped dead at 35.5 |

**I have no validated tell for which push carries.** 2 of 14 carried; nothing separates them.

---

## 5 — Method rules, earned the hard way

`ln_scope='both'` in `rpl_learn`.

**5.1 Guard the insert.** Compose the claim and write it **from the same bar**.
- #21 was malformed: I chose "before m15 reaches 85" from a read where m15 was 59.5; by the insert bar it was **112.92**. It ran 59.5 → 112.9 in 130 s
- **fix, used on every call from #22 on**: the `INSERT ... SELECT` carries a `WHERE` that refuses the row if either leg is already satisfied. It has refused rows

```sql
INSERT INTO rpl_jig_pred (jp_at_ms, jp_at_utc, jp_claim, jp_basis, jp_state, jp_outcome)
SELECT jg_ms, jg_utc, %s, CONCAT(...), CONCAT(...), 'open'
FROM rpl_jig WHERE jg_kind='heartbeat'
  AND <leg A not yet satisfied>
  AND <leg B not yet satisfied>
ORDER BY jg_ms DESC LIMIT 1
```
- if it writes no row, **say so**. Do not retry with looser legs

**5.2 Never rewrite `jp_claim` or `jp_basis`.** The call stands as made. Corrections go in `jp_note`.

**5.3 State the margin.** 6 of 34 resolved in under 2 min and test nothing.
- median resolution **12.9 min**; 19 of 34 over 10 min
- **set the opposing leg SHORTER than yours** when the read is the point, and say that you did

**5.4 Race form, no time cap.** `A before B`, both observable, neither pre-satisfied. Joe's standing rule: no cap/horizon/window unless he specifies one.

**5.5 `jp_claim` is `varchar(255)`.** It fails loudly at 256+. Keep claims sharp rather than widening the column.

**5.6 Every harness mismatch this session was mine, not the code's.** Three false MISMATCH reports:
- hardcoded state strings copied from a different row
- passed the wrong direction (`ed`) into a comparison
- moved a target bar without moving the window containing it

---

## 6 — The one board fact the new session must carry

**`ln_scope='both'`, confidence 90.**

**The r pair is LAGGED, not inert.** `s15r` / `s22r` do nothing for 15–30 minutes, then **step hard at a TF close**.

| close | s15r | step |
|---|---|---|
| 18:01 | 61.5 | +10.0 |
| 18:16 | 70.7 | +9.2 |
| 18:30 | 78.8 | +7.3 |
| 18:32 | 79.5 | +0.7 |

- I called it inert at 17:44 after it moved **0.5 points** through a 120-point s4M excursion
- the response arrived **20 minutes later** in one step
- **I was wrong about this line three times in a row, each correction in the same direction**
- **do not read a flat r line as a dead one.** Read it as pending

---

## 7 — rsd, and how the reads apply

**Joe named it rsd.** Task **#43**. `build_rsd.py` exists and banks `rpl_rsd`.

### Joe's rsd notes — VERBATIM

> *"do you think you could use a variation of MFE side detection to find swings, using s2,s1,s30,gcs15,gcs5?"*

> *"1) we need to sweep combos to find the most reliable / 2) the last reading before the walk started /
> 3) I don't know without seeing a pine emit. my guess: rsd is more multidimensional than it seems /
> 4) that's also a data driven (pine) decision"*

### What is built

| | |
|---|---|
| lines | 5 Mages, **bb 37 \| 0.7 \| close** at TF **5/60, 0.25, 0.5, 1.0, 2.0** min |
| signal | s4M cross OOB **+ 48 bars** (`WALK_DWELL_BARS` = 48 bars = 240 s at the 5 s grid) |
| side readings | both banked — `lastoob` and `mid` |
| scored by | `swing_detect` at 1% |
| table | `rpl_rsd` |

### The MFE-side mechanic it varies

- `mf = int(sd != wt)` ; `ed = -dr if mf else dr`
- proven: `ed` resolves to the s4Mage breach side in **all four** bias/side combinations
- so **bias changes no decision** — only the `mf` flag
- Joe: *"the side s4M breaches on is the gauranteed bias direction"*

### The four rulings still open

1. **sweep combos** across the 5 Mages to find the most reliable — not done
2. **read the LAST value before the walk started** — Joe's explicit choice
3. + 4. the rest is a **pine emit** decision. Joe will not rule without seeing one

### How this session's reads should feed rsd

- rsd is **exactly** the small-TF set Joe's GATHER note names: gcs5, gcs15, s30, s1
- GATHER held at 65 confidence — the strongest of the four reads as measured
- so the first thing to test on rsd is whether **gather state at the last pre-walk bar** predicts the swing better than the side flag alone
- **BOBBING at 25%** is the weakest measured read but it has the clearest mechanism. On rsd it becomes: does the bobbing Mage name which of the 5 turns first
- **do not** import my three falsified tells into rsd. They are recorded as falsified for that reason

---

## 8 — Tables

| table | concern | who writes |
|---|---|---|
| `rpl_seed` | Joe's verbatim words. **Immutable** | append only, when Joe says something new |
| `rpl_learn` | what was learned, with evidence and rating | this session |
| `rpl_jig_pred` | the calls | this session |
| `rpl_jig` | the board (heartbeats) + jig events | **the other session's jig.** Read only from here |
| `rpl_rsd` | rsd output | `build_rsd.py` |

### `rpl_learn` columns

| column | meaning |
|---|---|
| `ln_scope` | **`predict`** (this session) · `jig` (the other) · `both` |
| `ln_kind` | `read` \| `mechanic` \| `defect` \| `measurement` \| `method` |
| `ln_statement` | one claim |
| `ln_evidence` | the numbers behind it |
| `ln_evidence_n` | instances. **1 = anecdote** |
| `ln_status` | `held` \| `falsified` \| `open` \| `fixed` \| `blocked` |
| `ln_confidence` | **mine**, 0-100, from evidence count and directness |
| `ln_weight` | **Joe's rating. NULL until he sets it.** Not mine to fill |
| `ln_refs` | pred #, task #, file:line |

**Start every session with:**
```sql
SELECT ln_kind, ln_status, ln_confidence, ln_weight, ln_subject, ln_statement
FROM rpl_learn WHERE ln_scope IN ('predict','both')
ORDER BY COALESCE(ln_weight, ln_confidence) DESC;

SELECT sd_topic, sd_verbatim FROM rpl_seed ORDER BY sd_pk;
```

---

## 9 — Ideas to try

**Not tasks — candidates.** Reordered 0803 after Joe's §3.1/§3.2 notes: the tape work comes first.

1. **BUILD THE ANALOGUE SCAN.** §3.2 is the whole method and nothing exists for it yet. Take a live board vector (the 37 line values), find its nearest neighbours across the 2.8-month tape, and report what happened next to each. Output is a distribution with an **n**, not a guess.
2. **BUILD THE CROSS INDEX.** Joe: *"look everywhere for crosses - they are the moments when things really happen"*. Enumerate `cross_wob` rising edges for **every** line pair in `J.LINES` across the tape, bank them with the full board state at each. That table is the substrate for everything else.
3. **State shapes with more lines in them** (§3.1). Re-specify gravity / weakness / bobbing / gather as configurations over the HTF **and** LTF sets, not as two-line relations. Then let the level come from the analogue distribution rather than from a round number.
4. **Predict the r-line STEP, not the level.** The step is the event; the flat stretch is not. A call of the form *"s15r steps ≥ 5 points at its next close"* is testable and I never made one. Ties directly to the `ln_scope='both'` r-lag learning.
5. **Score by category automatically.** Add `jp_read` to `rpl_jig_pred` so the by-category rate is queryable rather than hand-bucketed. 17 of 58 were unbucketable.
6. **Bobbing → which Mage, not whether.** The read names a target. Test the naming, not the arrival: *"the next HTF Mage to make a new session extreme is h30, not h45/h60/h90."*
7. **Gather commitment vs sideways.** Joe's own framing and I never tested it directly — only the directional consequence. Build a commitment measure from the small-TF **spread** (already banked as `jg_gsp_*`) and the signed boundary distance (`jg_gbd_*`).
8. **rsd sweep** — the 5-Mage combo sweep Joe asked for, task #43 item 1. Run it **against the tape**, not live.
9. **rsd pine emit** — Joe will not rule items 3 and 4 without it.

---

## 10 — State at handover

| | |
|---|---|
| jig run | `0802_182429`, pid **1551853**, `--hours 24` — **belongs to the other session** |
| jig health | 204 heartbeats, all gaps 5 s |
| live walk | 18:31:20, side **hi**, dir **SHORT**, in ANCHOR state |
| board 18:41:10 | s4M 100.6 · `run_bars` 166 · qualified · **max r 79.5** · min r 60.3 · s15M 109.4 · s22M 78.4 · h30 68.6 · h90 76.8 |
| open prediction | **#60** — max r ≥ 83.0 before s4M < 85.0. Closest the HI gate has been all session (3.5 away) |
| `rpl_seed` | 23 rows |
| `rpl_learn` | 20 rows — 7 `predict`, 4 `both`, 9 `jig` |
| `rpl_jig_pred` | 60 rows — 30 right, 28 wrong, 1 void, 1 open |
