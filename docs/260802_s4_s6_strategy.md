# 0802 s4 s6 strategy

**Status: SPEC OF RECORD.** Created 0803 at Joe's instruction.

> Joe 0803, verbatim, on the name:
> "it'll need to have a differentiating name.  call it 0802 s4 s6 strategy"

Named for its two producers: **s4Mage sets the entry, s6 sets the exit.**

> Joe 0803, verbatim:
> "copy my response verbatim into our spec doc. if we don't have a spec doc yet, then create a '0802
> strategy' and drop everything we are _currently_ using into it (also with my verbatim responses, so
> that nothing is lost in translation)
>
> anything that we've tried and are not currently employing needs to go in its own section at the
> bottom of the spec, along with the reason why it's need benched"

**This is NOT the exhv2 chain.** `docs/260803_draft_strategy.md` specs r-pred → exhv2 walk → anchor →
signal. This document specs a different mechanic: s4Mage OOB excursions with an s6 exit. They share
lines and a tape; they do not share a flow.

**EVERY P&L NUMBER MEASURED SO FAR IS INVALID.** Two defects found 0803 after the measurements were
taken — the exit used the wrong line (§3) and the entry set counted bobs as trades (§2). Nothing in
§9 has been re-scored. Mechanics in §1–§6 are current; numbers are not.

---

## 1. Boundaries and lines

| name | spec | source |
|---|---|---|
| HI / LO | 85.0 / 15.0 | `optimus9_system` |
| grid | 5 s bars | |
| s4Mage | `bb 37\|0.70\|close` @ TF4 | the walk producer, unchanged |
| s6Mage | `bb 37\|0.90\|close` @ TF6 | Joe 0803: 0.70 -> 0.90 |
| s6m | `bb 6\|0.40\|close` @ TF6 | the mini. Joe 0803: 0.45 -> 0.40 |
| s6x | `bb 5\|0.35\|close` @ TF6 | Joe 0803, new. **The exit's crossing line** — §3 |
| s1Mage | `bb 37\|0.83\|close` @ TF1 | item 14's line |
| s4m | `bb 6\|0.45\|close` @ TF4 | the mini. The reverse event's trigger — §5 |
| HTF Mage | `bb 37\|0.83\|close` at every TF | |
| r | kline `k_len 7, rsi 5, stc 11, close` | `R.LN['r']` |
| x | `bb 5\|0.37\|close` | |
| mini m | `bb 6\|0.45\|close` | |

> Joe 0803, verbatim:
> "note s5Mage and s6Mage, gcs15 and s30 are all using 37|0.83|close"

> Joe 0803, verbatim:
> "duplicated indicator sets noted. relabel the 30sec `s30` to `gcs30`"

`s30` means **30 minutes** everywhere in this document. The 30-second line is `gcs30`.

`retest_min_ib_sec` = **120** in `rpl_config` baseline = 24 bars at the 5 s grid. Read by
`rpl_walk.py:42` as `RETEST_MIN_IB_MS`, applied at `rpl_walk.py:275` with the comment *"new excursion
only after a GENUINE IB dwell (merge micro-wiggles)"*.

---

## 2. ENTRY

> Joe 0803, verbatim — **the current rule**:
> "you've overcomplicated this, so here is the simple version that I am asking for: add 1 trade for each
> s4M excursion that is separated by IB > IB dwell, and report only on that. all other OOB excursions
> belong only to bobbing. bobbing is not trading, bobbing is an indicator"

> Joe 0802, verbatim — the original excursion definition:
> "can you run a fun idea for me? between 07-21 and 07-31, when every s4Mage crosses into oob and dwells
> >30 seconds, find the number of excursions that are > 0.75 MFE to the swing detect 1% pivot"

**The rule**

1. an **excursion** = any s4Mage OOB run. The entry is its **first** bar — entry wob 1, no dwell filter.
   Causal by construction: nothing about the run's future length is read.
2. **GATE 5** — the in-bounds stretch before the excursion must exceed **24 bars = 120 s**
   (`retest_min_ib_sec` = 120, `rpl_config` baseline)
3. **GATE 14** — s1Mage must have held within **15 board points** of that same boundary for
   **> 24 bars = 120 s** before entry
   > Joe 0802: "require s1Mage to have been loosely/fuzzy lo oob for > 2 minutes"
4. every other excursion is **bobbing**. Bobbing is an indicator, not a trade — see §6
5. direction = the s4Mage OOB side. **hi breach → LONG**, lo breach → SHORT
6. **item 13 (ALT) is NOT applied** — measured vacuous at 13,622 of 13,622 runs, because with every run
   entry-eligible the previous run is nearly always the other side or has s4Mage crossing 50 between
7. **NOTHING BLOCKS A SECOND ENTRY WHILE A POSITION IS OPEN** — item 15, still open

**On direction.** Joe 0802 corrected the opposite reading:

> "this rule is incorrect - oob-hi does not prove that the trade signal will be SHORT"

> "got it - so you can see that a hi OOB Mage doesn't always have to produce a short trade / --if you
> agree that this should be a long trade based on the mechanism's proven code, then re-build the full
> walk and find the correct moment for the LONG entry that capitalises on momo"

Verified 0803 against price on the A+D∧ALT set: green (hi breach, `tr_dr` +1) spans average **+0.818%**
raw price movement, red (lo breach) **−1.256%**; `tr_ret` = `tr_dr` × price change on all 135 rows,
0 mismatches; direction agrees with realised price move on 80% (hi) and 85% (lo) of rows.

**`emit_dominoes_pine.py:100` uses the OPPOSITE convention** (`'hi' -> SHORT`). That is a different
mechanic's file. Do not carry its sign into this strategy.

---

## 3. EXIT — `s6_EXIT`

> Joe 0803, verbatim:
> "so the answer is this: s6_EXIT on  (OOB s6m) crossing s6Mage.  don't require s6Mage to be OOB"

> Joe 0803, verbatim:
> "s6_EXIT has priority over (s4m crossing boundary while s4Mage stays OOB and s6Mage is IB)"

**The rule, as built 0804**

| trade | breach side | gate — evaluated at the cross bar | cross |
|---|---|---|---|
| LONG | hi | s6x was `>= HI` (85.0) within the last **72 bars = 6 min** | s6x crosses **down** through s6Mage |
| SHORT | lo | s6x was `<= LO` (15.0) within the last **72 bars = 6 min** | s6x crosses **up** through s6Mage |

- **crossing line is s6x** (`bb 5\|0.35\|close` @ TF6), which beat s6m on the tape
- **s6Mage's own level is NOT tested.** Requiring it was the original defect
- **the OOB test is a LOOKBACK, not a test at the cross bar.** Testing it AT the cross cannot fire while
  s6Mage is in bounds: to cross down through an s6Mage at 65, s6x must fall to 65, which is under HI.
  > Joe 0803: "could the answer be to look back 6 minutes for the OOB s6m ?"
- **EXIT WOB = 3 bars = 15 s.** The cross must hold 3 consecutive bars; the exit is the 3rd.
  > Joe 0803, from the wob sweep against his 07-29 02:16 target: "3 is good"
  - undebounced (wob 1) fired on a single 5 s bar. On 07-29 trade #1 that exited 02:12:05 on a cross
    whose sign-run was 1 bar long. wob 3 moves it to 02:19:00.
- **derivable, not fixed**: `s46_exit` stores `sx_run_bars`, so the exit at any wob n is
  `sx_ms + (n-1)` bars for runs with `sx_run_bars >= n`.

**TWO SIGN INVERSIONS, FOUND AND FIXED 0804.** `s46_exit` was storing `sx_dir` as the direction the
LINE moved and gating each cross on the crossed side's boundary. The consumer reads `sx_dir` as a TRADE
side, so a long was being closed by an up-cross and gated on the wrong boundary. Restored to
`build_exit2.py`'s correct form: **`sx_dir` is the trade the cross closes**, and `sx_lb_min` is bars
since the line was OOB on **that trade's breach side**. Symptom that exposed it: the wob sweep and the
window builder disagreed on trade #1 (02:19:00 vs 02:12:20), and `sx_lb_min` read 507 where it should
have read 2.

**The earlier exit (now dead).** Joe 0802:

> "exit: use s6x crossing s6Mage (crossunder for hi breach)"

> "require both x and Mage to be OOB before the cross. set s6Mage multi to 0.7"

> "find the best wob for the best pnl"

That produced `wob` 72 = 360 s. **Both the line and the gate were wrong**: the crossing line is s6m
(`bb 6\|0.45`), not s6x (`bb 5\|0.37`), and requiring s6Mage OOB coupled the exit to the §5 reverse
event from the opposite side — the event selects s6Mage IB, the exit demanded s6Mage OOB, so on exactly
the population under study the exit was dormant. Holds ran 518 min against 400. Every exit-derived
figure taken before 0803 20:30 was measured through that dormancy.

Carried over to the corrected rule, `wob` 72 produces mean 0.002% — the 72 was fitted to the old line
and does not transfer.

---

## 4. ALT — the same-side filter

> Joe 0802, verbatim — strict:
> "filter out any s4Mage OOBs that were last OOB on the same side - eg the s4Mage must travel from hi
> OOB to low OOB"

> Joe 0802, verbatim — loose:
> "loosen the ALT requirement - now allow same-side OOB double dipping if Mage as traversed past 50
> before returning to the egress OOB"

| column | rule |
|---|---|
| `tr_alt_strict` | the previous excursion was the **other** side |
| `tr_alt_loose` | other side, **OR** same side with s4Mage traversing past 50 in between |

**Measured 0803 (on the pre-correction entry set — indicative only).** ALT cut entries-per-exit from
15.0 to 4.0 (loose) and 2.7 (strict), raised the mean, and simultaneously removed the worst trade and
the deepest MAE. It behaves as a redundancy filter, not a return filter. Its role may be superseded by
the §2 IB-dwell rule, which addresses the same duplication directly — **not yet tested**.

---

## 5. The s6Mage exhaustion reverse

> Joe 0803, verbatim:
> "you might be able to do this instead:
> --when s4m spikes up and crosses the low boundary, measure s6Mages value. if s6Mage is IB while
> s4Mage is OOB, then s6Mage is exhausted: exit the trade AND start a new trade in the direction of s4M"

> Joe 0803, verbatim — the clarification:
> "no, I'm referring to s4m crossing up while s4Mage is slowly reversing (still OOB)"

> Joe 0803, verbatim — on the reversing clause:
> "reversing was my assumption (I can't see emerging bars on TV s4). if s4Mage slowly reversing breaks
> the logic, it can be dropped"

**The event**

- `s4m` (`bb 6\|0.45` @ TF4) **leaves OOB** on the cage side
- **and** `s4Mage` (`bb 37\|0.70` @ TF4) is **still OOB on that same side**
- **and** `s6Mage` is **IB** at that bar → s6Mage is exhausted
- → exit the held trade **and** open a new one in the direction of s4M

**Priority: `s6_EXIT` fires first.** A reverse event is only live if `s6_EXIT` has not already closed
the position (Joe 0803, §3).

**No reversal test is coded.** The guard is "s4Mage still OOB", which is Joe's written clause.
`sx_s4m_oob_bars` and `sx_s4mage_oob_bars` are banked so a reversal condition can be added as a filter
rather than a rebuild.

**Open**: "direction of s4M" is ambiguous between the OOB side and the direction s4m is spiking. Both
outcomes are banked (`sx_rev_*` / `sx_con_*`); the choice is Joe's.

---

## 6. Bobbing — an indicator, not a trade

> Joe 0803, verbatim:
> "the scenarios you see here are the defintion of bobbing - mage is pegged while it waits for whichever
> higher TF Mage is tracking towards OOB
> --hypothesis: if we know which HTF Mage(s) break the bobbers out of their bearish cage, then we can
> find the HTF mage's value at the time when we opened the trade (ie s4M crossing to OOB). if we have
> that HTF Mage value, and the 9 momo-test samples before it, we can build a model that detects which
> HTF Mage will end the bobbing, and we get 1) a more targetted exit and 2) we stay away from entring
> trades like 07-28 11:00"

> Joe 0803, verbatim:
> "bobbing is a function for all TFs - you'll find lots of bobing in the <=1 TFs"
>
> "bob ending is related to the same TF"
>
> "'which HTF Mage breaks them out' does it cross OOB on the cage side? - yes"
>
> "9/12/whatever works"

> Joe 0803, verbatim:
> "the episode is inconsistent per s4Mage excursion (the bob). measuring them individually and manually
> will give a better feel of the data"

> Joe 0803, verbatim — correcting an inverted definition:
> "this is inverted. consolidation will create small OOB grazes"

**The definition**

- a **bobbing sequence** on TF X = a maximal run of consecutive same-side OOB excursions on TF X's Mage
  with no 50-traverse between them
- the bob **ends** when TF X's **own** Mage traverses 50 away from the cage side
- the **breaker** = a rung **above** TF X crossing OOB **on the cage side**, nearest at or before the break
- the model's features are read at the **bob start** (= the trade-open bar), so they are causal. The
  breaker's identity is the **label** and is not causal

**Measured 0803**: 24,645 sequences across TF 1..120. s1 has 3,547; s4 1,096; s120 45. 1-only sequences
fall 35% → 7% as TF rises. Median duration 8 min at s1, 803 min at s120.

**Momo samples**: `MOMO_SAMPLES` = 12 (`build_exhv2.py:42` = `MOMO_WINDOW_MIN` 60 ÷ `MOMO_STEP_MIN` 5).
Nine was the value when the window was 45 min. Twelve are stored (`bk_s0..bk_s11`) at 60 bars = 5 min
apart; nine is the slice `bk_s3..bk_s11`.

---

## 7. Knobs — set, unset, and Joe's

| knob | value | status |
|---|---|---|
| entry dwell | 6 bars = 30 s | **SET** — Joe 0802 "dwells >30 seconds" |
| IB dwell | 24 bars = 120 s | **SET** — `retest_min_ib_sec`, `rpl_config` baseline |
| s6_EXIT `wob` | — | **UNSET.** The old 72 was fitted to the old line. Must be re-swept |
| stop | none | **SET by measurement, needs re-testing.** Every stop reduced the mean on the old rule |
| momo level gate for a Mage | — | **UNSET.** Joe 0803: "maybe 50 is too low of a bar for MAge momo" — `LEVEL_SLACK` 13.9 around 50 is far below where a Mage separates |
| TP | — | **UNSET.** Never re-run since the grid-cap error |

> Joe 0803, verbatim, on the momo level:
> "maybe 50 is too low of a bar for MAge momo"

---

## 8. Joe's standing rules for this work

> "there's a semi-generic rule I have anout BB lines and Klines - BB lines will lead a K line around the
> board. if BB is higher than K, K is likely to be bullish. inverse for bear"

> "RPL init scan: RPL starts at the ceiling TF, and looks down to find the highest TF that has a oob r,
> or a r-prediction. you'll need to scan bear and bull"

> "it's simply this: green for long, red for short"

> "-this one is stright forward: can you see the s22momo ?"

> "I used the MAE to weed out the unwanted signals"

> "got it - can't use history to predict if a trade is more likley to fail (ie build a gate based on
> historical data)"

> "'everything measured is a still frame at one bar.' -this feels important to dive in to. every trade
> has a setup. granted it's slower to unpack in code, but I'm in no hurry"

---

## 9. Tables

| table | rows | scope | valid? |
|---|---|---|---|
| `rpl_trades` | 5,952 | excursions + HTF/init/momo features, full tape | **entries over-counted, exits on the wrong line** |
| `rpl_exit2` | 65,472 | 5,952 excursions × 11 `wob`, corrected s6_EXIT | **entries over-counted** |
| `rpl_bob2` | 24,645 | bobbing sequences, all TFs, + breaker + 12 momo samples | valid as an indicator table |
| `rpl_bob_seq` / `rpl_bob_htf` | 1,257 / 150,840 | TF4 sequences, full 120-rung cross-product | valid |
| `rpl_s6exh2` | 11,531 | §5 reverse events, both outcomes banked | **exits on the wrong line** |
| `rpl_bob2_w` / `rpl_s6exh2_w` | — | 07-25 → 07-30 slice | same faults, 2.5 blocks |
| `rpl_learn` | 68 | banked findings, 0803 session = rows 62–68 | see §10 |

**Producers**: `build_trades.py` (superseded), `build_trades2.py`, `build_exit2.py`, `build_bob.py`,
`build_bob2.py`. **None of them apply the §2 IB-dwell rule.**

---

## 10. BENCHED — tried, not currently employed

### 10a. FALSIFIED by measurement

**HTF-opposed rung count.** Counting the HTF rungs where the Mage sits on the far side of its own r
(Joe's BB-leads-K rule applied across 7 rungs).
*Why benched*: produced a monotone 0→7 gradient on 10 days (5 blocks) and does not exist on 75 days or
in either half. `nopp`=7 −0.195% with a 40% loss rate, the worst cell; `nopp`=0 +0.532%. Non-monotone
throughout. Banked `rpl_learn` 66.

**LTF x-crossing-Mage as an entry timer.** Joe 0803: *"require oob gcs5x crossing gcs5Mage (or any
other ltf) to optimise the trade entry"*.
*Why benched*: the cross fires on 95–99% of trades so it filters almost nothing, and the wait costs
more than it saves. Worse at every LTF, monotone in the wait: gcs5 delayed 0.047 vs 0.079 on the same
rows entered at the OOB; s2 at 55 min wait, 0.017 vs 0.058. Banked `rpl_learn` 65.

**RPL init scan, standalone.** Joe 0803: ceiling-down, highest TF with an OOB r or an r-pred.
*Why benched as a standalone*: against-trend beats with-trend 0.344% vs 0.086% at ceiling 90, but
halves out of sample (IS 0.558/blk-t +1.97 → OOS 0.149/+0.41) and Q4 is +0.04. **Retained as the
second condition in the A+D conjunction** (§10c) and as a diagnostic. The effect concentrates in the
s31–s60 band (0.773%, blk-t +2.21) rather than spreading up the ladder.

**`tr_s1hold` as a return filter.** Joe 0802: *"filter on s1Mage bobbing on the bias side. ie for a lo
breach s4Mage, require s1Mage to have been loosely/fuzzy lo oob for > 2 minutes"*.
*Why benched as a return filter*: 0.167% at the 2-minute threshold against a 0.148% baseline, and
blk-t **falls** (+1.69 → +1.37). Higher thresholds get worse. **Retained as a redundancy filter** —
it cuts entries-per-exit from 14.7 to 5.0. The §2 IB-dwell rule may supersede it.

### 10b. PROVISIONAL — measured on the wrong exit, needs re-scoring

**s15/s22 Mage momo at the exit bar.** Joe 0803: *"add s15 and s22 momo to the mix - test them when the
s6 exit is signalling, see if you get more length from the trade"*. Rule: at the exit bar read s15 Mage
momo; `curl` → take this exit; `momo` with the Mage level ≥ 175 → hold to the 3rd exit signal.
*Why benched*: measured 0.447% vs 0.148% baseline, blk-t +2.61, IS +1.90 / OOS +1.89 — but on the old
exit line. Must be re-derived. Confirms Joe's "50 is too low for a Mage": the OOS ranking **rises**
monotonically as the gate goes 100 → 175 while the IS ranking falls. Banked `rpl_learn` 64.

**A(s120) ∧ D ∧ ALT — the "135 trades".** s120 r on the bias side of 50 at entry, the init scan against
the trade, ALT-loose.
*Why benched*: 1.048% mean, blk-t +3.90, held both halves and all four quarters, tail improved
(worst −3.446% vs −23.284%) — but every one of those figures is exit-derived and the entry set
over-counts. Banked `rpl_learn` 62–63. **Re-score before quoting.**

### 10c. NEVER BUILT

**s6Mage as the entry producer.** Joe 0802: *"replace s4MAge with s6Mage (same config)"*.
*Why benched*: needs a rebuild — every table walks `M4` only.

**MFE to the swing_detect 1% pivot.** Joe 0802: *"find the number of excursions that are > 0.75 MFE to
the swing detect 1% pivot"*.
*Why benched*: `tr_mfe` measures to the exit bar, not to the pivot. `find_pivots` appears nowhere in
the current builds. Note `find_pivots` is **NOT causal** — it confirms only after a pct% retrace.

**TP grid.** Joe 0802: *"which TP would produce the most return if we had a 0.3 or 0.4 stop"*.
*Why benched*: needs MAE/MFE path ordering, which no table stores. A stop-only sweep IS derivable and
was run; a TP sweep is not.

**Splitting the init scan's two conditions.** The scan ORs `r` OOB with `predict_breach` == direction.
*Why benched*: the stored column holds only the winning TF, not which condition won it. Traced at
07-28 11:00 the bull rungs fired on `r` OOB while the bear rungs fired on `P` — two different
mechanisms collapsed into one number. Needs a rebuild storing them apart.

### 10d. BLOCKED

**Double-printed bgcolor.** Joe 0803: *"show me the 135 entries as red/green double-printed bgcolors"*.
*Why blocked*: needs one `bgcolor()` call per stream. `jig.py:547` marks `_bgcolor_frag` **FORMAT IS
LOCKED — DO NOT CHANGE WITHOUT JOE'S AUTHORISATION (Joe 0731)**, with a standing note that per-stream
`bgcolor()` calls were tried and reverted twice. A single `bg` variable can hold only one colour
regardless of stream count. `emit_ad_pine.py` emits two honest streams instead.

---

## 11. Findings that are NOT strategy but must not be lost

**`.rpl_cache` is not stale.** Task #42 flagged it as contaminated by synthetic klines. Measured 0803:
a fresh 60 h-warmup jig reproduces `L0`'s r lines to **0.0000** max abs diff at s4/s15/s22/s60/s120 when
scored on the analysis window, and every Bollinger line is bit-identical at every warmup tested
(60/180/360/720/1012 h). Scoring the whole jig array including its own warmup region produces an
apparent 29.79% mismatch at s120 — that is the artefact. Banked `rpl_learn` 68.

**The 10-day window understated the tail by 3x.** 07-21..07-31: worst trade −7.377%, max MAE 9.292%.
Full tape: **−23.284% / 28.781%**. Every exit conclusion taken before 0803 was measured on a window
containing no large adverse excursion. Banked `rpl_learn` 67.

**Pre-05-18 is synthetic warmup, never analysis** (`rpl_walk.py:121`, Joe 0729). A build that omits the
filter banks 941 synthetic rows and inverts results.

**Effective n.** Excursions collapse hard onto shared exits: 15.0 entries per exit unfiltered, 4.0 with
ALT-loose, 2.7 with ALT-strict, 1.3 with A+D+ALT. Any t computed on the row count is overstated by
roughly the square root of that factor. The §2 IB-dwell rule attacks this at the source.

---
---

# 0804 — LOOKAHEAD IN THE EXIT. Every leg measurement from 0804 is void.

Joe 0804: "4 - this isn't causal". Correct.

## THE DEFECT — sweep_s46_exit.py:266

```python
if s6 is not None and not (s6_mode == 'fallback' and cand):
```

`cand` holds the leg's next fire bar ANYWHERE in the future (unbounded searchsorted). Under
`s6_mode='fallback'` the s6 exit is suppressed whenever the leg fires AT ALL. Standing at the s6
exit bar you cannot know whether the leg will fire 5,000 bars later.

`s6_mode='race'` — `b = min(cand)`, whichever fires first — IS causal.

## PROOF OF WHERE IT ENTERS

| config | s6_mode | n | mean ret | mean hold |
|---|---|---|---|---|
| no leg, no gate | fallback | 854 | +0.005774 | — |
| no leg, no gate | race | 854 | **+0.005774** | — |
| x15M30 H2 + G30 | fallback | 854 | **+0.410773** | 3,974 bars |
| x15M30 H2 + G30 | race | 854 | **+0.010545** | **295 bars** |

Baseline rows are BIT-IDENTICAL across modes (`firemap=None` -> `cand` always empty -> the
suppression branch never fires). Any config WITH a leg diverges 39x on mean and 13x on hold.
**The lookahead was buying 3,679 extra bars of hold per trade.**

## THE DAMAGE — walk-forward, x1 p70 refit weekly, item 15 on, net 0.110% taker

| exit | s6_mode | n | net mean | t | weeks>0 |
|---|---|---|---|---|---|
| x15M30 H2 filtered | fallback | 83 | +0.6085 | 2.26 | 7/8 |
| **x15M30 H2 filtered** | **RACE** | 110 | **−0.0187** | **−0.23** | **2/8** |
| x22M H0 filtered | fallback | 85 | +0.5088 | 2.16 | 6/8 |
| **x22M H0 filtered** | **RACE** | 110 | **−0.0165** | −0.21 | 2/8 |
| x15M H13 filtered | fallback | 89 | +0.3804 | 2.00 | 7/8 |
| **x15M H13 filtered** | **RACE** | 110 | **−0.0269** | −0.33 | 2/8 |
| x15M30 H2 UNFILTERED | RACE | 325 | −0.0976 | −2.37 | 1/8 |

## SCOPE OF THE VOID
Every leg measurement from 0804 ckpt 17 onward: STALL/TRAIL, fee pricing, power analysis, stop
sweep, MAE prediction, regime/beta, the 208-config leg family, the gate paired test (104/104), the
gate 84-config sweep, the entry threshold sweeps, ib>48 interior optimum, the 58-column screen, the
time-split, the full stack (t 3.14), the dose-response, the walk-forward (t 2.26), the long-side
screen, the symmetry test.

## WHAT SURVIVES
- all baseline-only rows (s6 exit, no leg) — identical under both modes, verified
- the G30 gate DEFINITION (source read): `gate_open(L, dr, tfs=(30,), states=(1,), gwob=1)`
- LOOKAHEAD FOUND IN s46_run (source read): `sr_dwell_bars` = `b-a+1`, `sr_m4_min`/`sr_m4_max` =
  `M4[a:b+1]` — all three span forward to the run END. `sr_ib_bars` (`ibrun[a-1]`) is causal.
  The names `sr_ib_bars` and `sr_dwell_bars` differ by one character of code.
- the causality audit: knobs 1,2,3,5,6,7 are clean AS MECHANICS. `momo(r,dr,w)` samples
  `w - k*MOMO_STEP_BARS`, every index <= w.
- the arithmetic: subtracting a constant cost from a tight distribution inverts t; n* scales with sd^2

## JOE'S DECISIONS 0804
- item 15 (no-pyramiding) stays ON — "pyramiding needs to be disabled". Supersedes item 16 of the
  0803 16-line chain.
- `s6_mode='race'` only. 'fallback' retired.
- curl stays in the gate — "leave it on for now - I think there are other unbuilt mechanics that
  need to confluence curl". States become (1,2). Re-measure under 'race'.

## CLEAN BASELINE, FOR REFERENCE
854 trades, s6 exit alone: **+0.005774/trade gross** against a 0.110% round-trip taker cost line.

---
---

# 0805 — THE KNOB REGISTER. Every sweepable value from the 0804/0805 session.

Naming: `sr_s4hold` parallels `sr_s1hold` and keeps the `sr_` prefix (Joe 0805: "use your own code
notations"). Knob `S4HOLD_MIN`, default 0 = OFF.

## A. ITEM 10 — the entry gate

    current   sr_ib_bars > 24  AND  sr_s1hold > 24
    with the new knob ON:
              sr_ib_bars > 24  AND  sr_s1hold > 24  AND  sr_s4hold >= S4HOLD_MIN

| knob | what it counts | default | sweep | file |
|---|---|---|---|---|
| `sr_ib_bars` floor | 5 s bars s4Mage sat BETWEEN the levels immediately before the stretch | **> 24** = 120 s | 0, 6, 12, 24, 48, 96, 192 | `build_s46_window.py:81`, `sweep_s46_exit.py:90` |
| `sr_s1hold` floor | 5 s bars s1Mage sat within `FUZZ` 15 board points of that boundary before the stretch | **> 24** = 120 s | 0, 6, 12, 24, 48, 96, 192 | same |
| **`S4HOLD_MIN`** | **5 s bars s4Mage has held OOB AT the entry bar** | **0 = OFF** | 0 (off), 6, 12, 24 | new |
| `FUZZ` | s1Mage proximity band to the boundary | 15 board points | not swept | `build_s46.py:218` |

**WHY `S4HOLD_MIN` EXISTS (Joe 0805).** 07-29 09:40:20 opened on a stretch of ONE 5 s bar: s4Mage
reached 85.17, i.e. 0.17 points past the 85 level, and fell back on the next bar. Both existing
counts passed comfortably (`sr_ib_bars` 475 = 39.6 min, `sr_s1hold` 109 = 9.1 min) because they
measure the RUN-UP, not the breach. Joe: "s4M cannot be considered trade worthy if it only dwells
for 5 seconds."

Population, `s46_run`, stretch length in 5 s bars:

| stretch <= | all 13,633 stretches | after `>24 AND >24` (854 rows) |
|---|---|---|
| 1 bar (5 s) | 22.0% | **24.1% = 206 trades** |
| 2 bars | 34.3% | 35.9% |
| 6 bars (30 s) | 56.3% | 57.1% |
| 24 bars (120 s) | 78.0% | 76.1% |
| median | 5 bars = 25 s | 5 bars = 25 s |

The gate moves the one-bar share 22.0% -> 24.1%, i.e. it does not select on breach quality at all.

**⚠ TURNING `S4HOLD_MIN` ON MODIFIES ITEM 11.** At the entry bar s4Mage has been OOB for exactly 1
bar, because item 11 opens on the stretch's FIRST bar. So any floor > 1 can only be met by DELAYING
entry to bar `S4HOLD_MIN` of the stretch. That is causal (it waits, it does not peek) but it
contradicts item 11's "no waiting, no confirmation". Off by default; Joe 0805 has other mechanics
planned for these edge cases.

**DO NOT USE `sr_dwell_bars` FOR THIS.** It is `int(b - a + 1)` — the run's TOTAL length, measured
forward to its end. Lookahead. `sr_s4hold` must count only bars at or before the test bar.

## B. ITEM 13 — momo

| knob | role | default | sweep | file |
|---|---|---|---|---|
| momo states counted as detected | which indicator states arm the gate | **momo(1) + curl(2)** | — | `s46_momo.walk` |
| fence width `s` | `fence_lo = LO + s`, `fence_hi = 100 - LO - s`. At s=3 that is 18/82 | **3** | 2, 3, 4, 5, 6, 7, 8 | `s46_momo.FENCE_SWEEP` |
| xwob while momo-held | REPLACES `EXIT_WOB` 3 once armed; unarmed trades keep 3 | **6** | 3, 4, 5, 6, 7, 8, 9 | `s46_momo.XWOB_SWEEP` |
| line config | which r spec feeds momo and the oob hunt | **CUR** | CUR / A / B | `build_s46_event.NPZ` |

Line configs: **CUR** = `10\|4\|11` on both duties · **A** = momo on `10\|4\|11`, oob hunt on `7\|5\|12`
· **B** = `7\|5\|12` on both. A/B measured +4 boundary reaches (14 -> 18 of 36) with A leaving the
momo column bit-identical to CUR.

**DEFERRED (Joe 0805): r spec `7|7|12`** — a third spec, `k_len 7 | rsi 7 | stc 12`. Joe: "a sweep.
I don't think we do the sweep now, we need more OOS before we make decisions."

## C. THE CURL GATES — corrections to `build_exhv2.momo()`, applied in `optimus9/compute/momo_gated.py`

`momo()` tests direction alignment and a fit floor ONLY on its `momo` branch. Its `curl` branch had
neither, which armed 07-27 09:07:00 on a SHORT while s15r rose at slope +0.975 with `qa` +22.635 (a
minimum: the down curl had already ENDED, vertex 0.259).

| gate | test | default | file |
|---|---|---|---|
| 1 alignment | curl needs slope aligned with `dr`, same test `momo` uses | ON | `momo_gated.momo_g` |
| 2 arc direction | curl BEGINNING only — `dr -1` needs `qa < 0`, `dr +1` needs `qa > 0` | ON | same |
| 3 `CURL_R2_MIN` | QUADRATIC r2 floor | **0.40** | same |

`CURL_R2_MIN` 0.40 was chosen from the data: the errant 07-27 09:19:00 s22 bar scores 0.3238, and
0.40 is the lowest 0.05 step above it. Across the 2,289 bars already passing gates 1+2 the
distribution is min 0.1553 / p10 0.4157 / median 0.6735 / max 0.8719, so 0.40 sits below the 10th
percentile and keeps 90.8%. It rests on ONE event — sweep it once the mechanic is bedded.

Inherited from `build_exhv2`, not swept this session: `MOMO_R2_MIN` 0.50 (LINEAR fit floor on the
momo branch) · `MOMO_SLOPE_MIN` 1.0 · `MOMO_WINDOW_MIN` 60 min · `MOMO_STEP_MIN` 5 min ->
`MOMO_STEP_BARS` 60 · `MOMO_SAMPLES` 12 · `CURL_ARC_MIN` 4.0 · `CURL_VTX_LO/HI` 0.05/0.95 ·
`LEVEL_SLACK` 13.9.

## D. THE OPPOSING CURL

| knob | role | default | file |
|---|---|---|---|
| lines required | both s15r AND s22r in opposing curl, same bar | **both** | `build_s46_event.oppc` |
| detection | the same `curl` state read against the INVERTED `dr` | — | same |
| exit line | s6x (Joe 0805 corrected point 3 from s6m) | s6x | `s46_momo.walk` |

Joe 0805 on the both-lines rule: "the nature of K lines says the smaller TF will curl before the
higher TF does. when s22r matches s15r curl, then market has reversed enough to impact s22r's
direction." I read "matches" as SAME BAR, not a sequence — stated, not assumed.

Fired on 3 of 27 armed trades, cutting each ~85%: n=19 999.8 -> 149.6 min, n=21 803.8 -> 135.5,
n=30 1300.0 -> 178.8.

## E. ITEMS 14/15 — the exit cross

| knob | role | current | file |
|---|---|---|---|
| `EXIT_LINE` | which line crosses | `s6x` | `sweep_s46_exit.py:62` |
| `EXIT_LB` | s6x must have been past 85/15 on the trade's side within this many bars | 72 = 6 min | same |
| `EXIT_WOB` | the cross only counts if s6x HOLDS the new side this many bars | 3 = 15 s | same |

**PARKED (Joe 0805):** `sx_run_bars` is counted on the 5 s grid, so `EXIT_WOB` 3 debounces a
6-minute line over 15 s — a fifth of one of its own bars. Joe: "this can be swept after the mechanic
is bedded."

**DEFECT IN MY RUNS, not in your code:** `build_s46_event.py` filtered `s46_exit` on `sx_lb_min<=72`
only and applied the `(wob-1)` shift, but omitted `sx_run_bars >= wob`. `build_s46_window.py:74-79`
applies both. Mine therefore accepted crosses whose run ended before the wob was met — looser, not
lookahead. Every exit bar in the 91-row `s46_event` run is affected and needs re-running.

## F. VOIDED — do not sweep these without re-reading ckpt 40

`s6_mode` in `sweep_s46_exit.py` had `'fallback'`, which suppresses the s6 exit whenever the leg
fires anywhere in the future. NOT CAUSAL. Every leg result from 0804 ckpt 17 onward used it. Use
`'race'` only. The entry-side knobs measured under it — `sr_x1` p70, the leg/H/gate grid — are all
unproven until re-run.

---

## 0805 — ITEM 13 AS BUILT, and where the code lives

    ARM        per bar of the walk: indicator returns momo(1) or curl(2), same bias, s15r OR s22r
    HOLD       once armed the trade ignores its normal exit
    momo_exit  1) BOTH r beyond the fence  |  2) EITHER r beyond the fence   — both LATCHED
               closes at the NEXT qualifying s6x cross
    OPPOSING   the same curl state read against the INVERTED dr, on s15r AND s22r, same bar
    CURL       cancels the fence latch; closes at the next qualifying s6x cross
    UNARMED    item 15 unchanged — next bias-side gated s6x cross at EXIT_WOB 3

| file | role |
|---|---|
| `optimus9/compute/momo_gated.py` | the momo INDICATOR + 3 curl gates |
| `optimus9/analysis/s46_momo.py` | the MECHANIC, pure logic. `walk()` |
| `optimus9/analysis/build_s46_event.py` | writes `s46_event`; re-scores `s46_window` |
| `optimus9/analysis/sweep_s46_momo.py` | the 49-config sweep |

`build_exhv2.py`, `build_s46.py`, `build_s46_window.py` are UNMODIFIED.

RESULT, 36 trades 07-27->07-29, cfg CUR fence 7 xwob 3, net of 0.110% taker:
**+0.5740/trade, win 75.0%, ret sum +24.62** — but 46% of that comes from 3 trades, and item 15
(no-pyramiding) cuts it to 24 trades and +0.3263/trade.

SWEEP: fence is monotone 2->7 then flat (13.7x spread); **xwob is INERT** across 3-9.

FULL HANDOVER: `docs/260805_handover.md` — includes 11 loose ends, the voided 0804 work, and the
divergence read-up Joe parked.
