# 1001 — 09-01 re-walked on the ruled dr series, and two rulings recorded

Joe 1001 ruled the live trade book's dr is the 28-signal report's dr — `rig.DR`, oob 85/15, no wob
(`report_leash_walk.py:180`). The banked 09-01 MAE/MFE (`NOTES_momtf_mechdev.md:447-455`) was walked
on `rig.DRW` (Mage 75/25, wob 8). Joe, asked whether re-walking was worth it: *"is it valuable? if so
then do it"*.

**IT WAS VALUABLE, AND THE NUMBER MOVES.** `-0.662` on set A and on the UNION, `0.000` on set B. All
of it is ONE trade.

**WHY IT WAS WORTH RUNNING, decided before running it:** 10 of the banked 13 trades did NOT stop, so
their closes read the dr series bar by bar, and 717 of 09-01's 17,280 bars (4.15%) disagree between
the two series. The stop was known to be immune — it reads `pos['dr']`, fixed at the open bar
(`trade_walk.py:157`) — so the exposure was 10 of 13 closes, not 3.

## THE DISCIPLINE: THE BANKED NUMBERS WERE REPRODUCED FIRST

`trade_walk.walk(opens, series, rig.px, min(opens), k1, 0.70)` then `measure_live_stop.score`
(`-cap` if stopped, else `MFE - MAE`), tape pinned to `END_MS` 2026-09-08, day end bar 23:59:55.

| set | opens | closed | stopped | MFE>MAE | MAE sum | MFE sum | score | vs banked |
|---|---|---|---|---|---|---|---|---|
| A, on `DRW` | 9 | 8 | 2 | 6 | 2.813 | 10.986 | +8.153 | **REPRODUCED** |
| B, on `DRW` | 5 | 5 | 1 | 4 | 1.649 | 13.068 | +11.341 | **REPRODUCED** |
| UNION, on `DRW` | 14 | 13 | 3 | 10 | 4.462 | 20.202 | +15.642 | **REPRODUCED** |

Set A = the 9 FINAL YES fire bars. Set B = Joe's 5 (05:01:30, 07:27:15, 12:41:45, 13:05:25,
17:27:50). 23:18:50 is unclosed at the day end and excluded from every total, as banked.

## THE RESULT ON THE RULED SERIES

| set | series | opens | closed | stopped | MFE>MAE | MAE sum | MFE sum | score | per trade |
|---|---|---|---|---|---|---|---|---|---|
| A | `DRW` banked | 9 | 8 | 2 | 6 | 2.813 | 10.986 | +8.153 | +1.0191 |
| A | **`DR` ruled** | 9 | 8 | 2 | 6 | 2.813 | **10.324** | **+7.491** | **+0.9363** |
| B | `DRW` banked | 5 | 5 | 1 | 4 | 1.649 | 13.068 | +11.341 | +2.2682 |
| B | **`DR` ruled** | 5 | 5 | 1 | 4 | 1.649 | 13.068 | +11.341 | +2.2682 |
| UNION | `DRW` banked | 14 | 13 | 3 | 10 | 4.462 | 20.202 | +15.642 | +1.2032 |
| UNION | **`DR` ruled** | 14 | 13 | 3 | 10 | 4.462 | **19.540** | **+14.980** | **+1.1523** |

- the trade COUNT, the STOP count and the MFE>MAE count are unchanged in every set.
- the MAE sum is unchanged in every set.
- only the MFE sum moves, and only on A and the UNION.

## PER TRADE, UNION — THE WHOLE DELTA IS 02:40:35

| open | `DRW` close | `DR` close | `DRW` by | `DR` by | dMAE | dMFE |
|---|---|---|---|---|---|---|
| 00:27:35 | 02:40:35 | 02:40:35 | sig_utc | sig_utc | +0.000 | +0.000 |
| **02:40:35** | **03:38:00** | **03:25:20** | **sig_utc** | **dr-flip** | **+0.000** | **−0.662** |
| 03:38:00 | 05:01:30 | 05:01:30 | sig_utc | sig_utc | +0.000 | +0.000 |
| 05:01:30 | 06:24:40 | 06:24:05 | dr-flip | dr-flip | +0.000 | +0.000 |
| 07:27:15 | 09:02:15 | 09:02:15 | sig_utc | sig_utc | +0.000 | +0.000 |
| 09:02:15 | 12:13:30 | 12:13:00 | dr-flip | dr-flip | +0.000 | +0.000 |
| 12:41:45 | 13:01:30 | 13:01:30 | stop | stop | +0.000 | +0.000 |
| 13:05:25 | 14:50:00 | 14:50:00 | sig_utc | sig_utc | +0.000 | +0.000 |
| 14:50:00 | 15:49:40 | 15:51:40 | dr-flip | dr-flip | +0.000 | +0.000 |
| 17:27:50 | 17:59:25 | 17:59:25 | sig_utc | sig_utc | +0.000 | +0.000 |
| 17:59:25 | 18:15:55 | 18:15:55 | stop | stop | +0.000 | +0.000 |
| 18:20:00 | 18:28:00 | 18:28:00 | stop | stop | +0.000 | +0.000 |
| 22:24:10 | 23:18:35 | 23:18:00 | dr-flip | dr-flip | +0.000 | +0.000 |
| SUM | | | | | **+0.000** | **−0.662** |

**THE RULE THE DAY SHOWS: a close only moves a number when its EXIT MECHANISM changes.** 5 of the 13
UNION closes land on a different bar, but 4 of those 5 move by 30 s to 2 min and reach the same
extremes, so they cost 0.000. The one that costs is 02:40:35, where the exit changed class — on
`DRW` the 03:38:00 opposing signal closed it (`sig_utc`), on `DR` a dr-flip got there first at
03:25:20, 12.7 min earlier, cutting MFE 1.242 -> 0.580. Its MAE is 0.126 either way.

- set B's sums are bit-identical across 4 moved closes. **Checked per trade rather than reported from
  the aggregate**: every one is +0.000/+0.000. The largest move in set B is 17:27:50 extending
  19:11:20 -> 19:27:00, 15.7 min, into ground already covered.
- the 3 stops are identical on both series, as predicted from `trade_walk.py:157`.

## WHAT THIS RE-WALK DID NOT DO

**It did not implement Joe's `arm_dr` ruling** (below). It used `trade_walk`'s current behaviour,
`d = int(dr[k])` at the open bar. It did not need to: 0 of 23 run-first bars on 09-01 have
`rig.DR[fire] != arm_dr` (`1001_warmup.md`), and all 14 opens here carry the same dr on both series.
On a day where they differ, this re-walk's method and Joe's ruling would give different trades.

## TWO RULINGS FROM JOE, 1001

### 1. which dr opens the trade when the arm's and the bar's differ

Joe: *"we had a similar scenario yesterday, when 12:41 self-walked to `WALK FIRES FROM`: 13:05. 12:41
was non-arm, 13:05 was arm (your 'the arm dr MUST equal the signal dr') -- I think we do the same for
dr"*.

**The arm's dr governs, tested at the signal bar.** Same precedent as the arm itself — Joe 1001:
*"`arm` is tested at the signal (WALK FIRES FROM)"*.

- this is CONSISTENT with his earlier *"it's the dr in this report"*, and the two rulings compose:
  the SERIES is `rig.DR`, and the BAR it is read at is the arm bar, carried forward. `arm_dr` is
  literally `rig.DR[arm_bar]` — `ArmState.step` receives `dr_k` from `rig.DR` and stores `arm_dr = d`
  (`arm_state.py:88-91`).
- **so `trade_walk` must take the trade's dr from the arm, not from `dr[k]`.** It currently reads
  `d = int(dr[k])` at `trade_walk.py:151, 157`. Unbuilt; the producer does not exist.
- where no arm exists (the 4 non-armed opens in Joe's 5), `rig.DR[k]` is the only dr there is.

### 2. the label for an open in the trade log

Joe: **`octo-sig`**.

| where it goes | current | note |
|---|---|---|
| `o9_ledger.reason` `varchar(40)` | `entry` 268 rows, `pyramid` 720 rows — v2's, `strategy.py:108` | `octo-sig` is 8 chars, fits |
| `trade_walk`'s `opened_by` | `'sig_utc'` hard-coded at 4 sites | see below |

**THE ONE STRUCTURAL CONSEQUENCE, and it is not a value call.** `opened_by='sig_utc'` is hard-coded
at `trade_walk.py:155`, `bank_emit_entry.py:62`, `sweep_mae_cap.py:43` and `measure_live_stop.py:77`.
`trade_walk.py` is SHARED with the v7 chain, so editing its literal would relabel the v7 chain's
opens too. `trade_walk.walk` takes no `opened_by` parameter. So the label has to arrive as an
argument rather than as an edit to the shared literal — otherwise one mech's rename silently rewrites
another's trade log.

---

## 1001 — DOES `DRW` GIVE AN EARLIER BACKSTOP? NO. IT IS LATER IN 69% OF CASES

Joe: *"in practice, does DRW provide a earlier backstop-dr-flip? if so then I have 2 reasons to
approve it and lock it in"*.

Measured for EVERY bar of the tape, no sampling. Both series alternate strictly and never return to
0, so a trade opened in stretch `i` closes by dr-flip at the first bar of stretch `i+2`; that bar was
computed under each series and compared.

| `DRW` vs `DR` dr-flip close | bars | share |
|---|---|---|
| **`DRW` closes LATER** | **1,079,436** | **69.0%** |
| `DRW` closes EARLIER | 443,113 | 28.3% |
| same bar | 40,764 | 2.6% |
| median signed difference | **+0.33 min** (`DRW` later by 20 s) | |
| mean signed difference | **−1.82 min** (`DRW` earlier) | |

Subset: the 1,563,313 bars (95.7% of tape) where `DR == DRW` at the open, so the trade side is the
same and the comparison is like for like. The all-bars figures are 68.3% / 29.2% / 2.5%, median
+0.33, mean −1.78.

**THE MEDIAN AND THE MEAN DISAGREE IN SIGN, AND BOTH ARE REPORTED BECAUSE THE SHAPE IS THE ANSWER.**
`DRW` is later most of the time by a small amount (median 20 s), and earlier occasionally by a large
amount — a tail big enough to pull the mean to −1.82 min. So "earlier backstop" is true rarely and
largely, false usually and narrowly.

**Why it goes this way:** the two knobs oppose. `DRW`'s looser 25/75 fence is reached EARLIER than
`DR`'s 15/85, but its `wob` 8 (8 consecutive bars = 40 s) delays every latch move and drops short
stretches entirely. The wob wins 69% of the time.

**The 09-01 trades agree with the tape.** Of the 9 re-walked trades where either series closed by
dr-flip, `DRW` was later on 6 and earlier on 3 — 67%, against the tape's 69.0%.

| open | `DRW` close | `DR` close | `DRW` is |
|---|---|---|---|
| 02:40:35 | 03:38:00 | 03:25:20 | later (and its close was `sig_utc`, not a flip) |
| 03:38:00 | 05:04:30 | 05:04:00 | later by 30 s |
| 05:01:30 | 06:24:40 | 06:24:05 | later by 35 s |
| 07:27:15 | 09:24:50 | 09:24:40 | later by 10 s |
| 09:02:15 | 12:13:30 | 12:13:00 | later by 30 s |
| 22:24:10 | 23:18:35 | 23:18:00 | later by 35 s |
| 13:05:25 | 14:59:35 | 14:59:50 | **earlier by 15 s** |
| 14:50:00 | 15:49:40 | 15:51:40 | **earlier by 2 min** |
| 17:27:50 | 19:11:20 | 19:27:00 | **earlier by 15.7 min** |

So the second reason does not hold. Separating the fence from the wob is MVP2 item 5, unrun.

## 1001 — THE TWO GAPS, ANSWERED

### gap 1: `walk_open_label` in `trade_config.key()`? NO. Risk either way is LOW.

| fact | source |
|---|---|
| `wsf_trades` is `UNIQUE (wt_key, wt_win, wt_open_ms)` | `SHOW INDEX FROM wsf_trades` |
| `key()` already carries `_version` | `trade_config.py:136` |
| octo-freedom loads **v4**, the v7 chain loads **v3** | `wtc_v4_...` vs `wtc_v3_...` — already distinct |
| every banked row is **v2** | `wtc_v2_v7_rule1_gateopen` 146, `_entry_emit` 119, `_entry_emit_noflipopen` 67 = **332 rows**. Nothing banked under v3 or v4, so nothing to orphan |

**The decisive structural reason:** `key()` identifies a KNOB SET. `walk_open_label` changes no trade
and no number — only a label — so it creates no A/B for an overwrite to destroy, which is what
`knobs-belong-in-the-unique-key` exists to prevent. The version already separates the two mechs.

### gap 2: consolidate the copies? THE RISK IS NOT IN CONSOLIDATING. IT IS IN WHAT ALREADY DIVERGED.

AST-extracted, docstrings stripped, bodies compared:

| copy | md5 of the normalised body | verdict |
|---|---|---|
| `sweep_v3_signal.walk_no_flip_open:45` | `ff31767c8a92` | the reference |
| `sweep_mae_cap.walk_no_flip_open:25` | `ff31767c8a92` | **functionally identical** |
| `bank_emit_entry.walk_no_flip_open:44` | `b763a39dce5c` | **DIVERGENT** |

`bank_emit_entry`'s copy is missing Joe's 0929 same-dr-inert clause:

    d = int(dr[k])
    if pos is not None and not (d == -pos['dr'] and d != 0):
        continue

Without it a same-dr `sig_utc` CLOSES the open trade and opens a new one instead of being inert. Its
own docstring says *"the walk is otherwise his 0929 rule"* — "otherwise" referring only to the
dr-flip open being removed. So the docstring overclaims by one clause.

**AND THAT SCRIPT BANKED ROWS.** `bank_emit_entry.py`'s `NEW_KEY = SRC_KEY + '_entry_emit' +
('_noflipopen' if ...)` matches two of the three banked keys: 119 + 67 = **186 of the 332 rows in
`wsf_trades`**.

- **whether the missing clause actually changed any of those 186 rows is NOT measured.** It needs the
  two copies run over the same opens and the rows compared.
- the consolidation itself is low urgency and carries real regression risk — `measure_live_stop.walk`
  is a fourth variant with `cap` and `open_on_stop_bar`, so merging means one function with flags.

---

## 1001 — THE wob THAT HOLDS +1.2032 AND MOVES THE BACKSTOP EARLIER: wob 7

Joe's target: *"what wob would satisfy our 'DRW banked', +1.2032 AND move the backstop-dr-flip to
median signed diff that's better than 0.33?"*

**HIT, with wob 7 = 35 s.** Both metrics per wob, on the acceptance test's tape (END_MS 2026-09-08),
`latch_wob` fence 75/25 unchanged, UNION trade set, `mae_cap` 0.70.

**The sweep's latch was verified before anything was read off it:** the vectorised `latch_wob` is
bit-identical to `dr_latch.latch_wob` at wob 8 and to `rig.DRW` — 0 of 1,632,960 bars differ.

| wob | seconds | stretches | closed | stop | MFE>MAE | score | **per trade** | **median min** | mean min |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 3,231 | 13 | 3 | 10 | +14.598 | +1.1229 | **−1.25** | −19.95 |
| 2 | 10 | 3,037 | 13 | 3 | 10 | +14.598 | +1.1229 | −0.67 | −15.73 |
| 3 | 15 | 2,889 | 13 | 3 | 10 | +14.598 | +1.1229 | −0.33 | −12.73 |
| 4 | 20 | 2,803 | 13 | 3 | 10 | +14.598 | +1.1229 | −0.08 | −10.30 |
| 5 | 25 | 2,699 | 13 | 3 | 10 | +14.598 | +1.1229 | +0.08 | −7.35 |
| 6 | 30 | 2,613 | 13 | 3 | 10 | +14.980 | +1.1523 | +0.17 | −5.37 |
| **7** | **35** | **2,555** | **13** | **3** | **10** | **+15.642** | **+1.2032** | **+0.25** | **−3.36** |
| 8 | 40 | 2,507 | 13 | 3 | 10 | +15.642 | +1.2032 | +0.42 | −1.85 |
| 9 | 45 | 2,439 | 13 | 3 | 10 | +15.642 | +1.2032 | +0.50 | +0.86 |
| 10 | 50 | 2,381 | 13 | 3 | 10 | +15.642 | +1.2032 | +0.58 | +2.92 |
| 12 | 60 | 2,279 | 14 | 3 | 10 | +15.455 | +1.1039 | +0.83 | +7.74 |
| 16 | 80 | 2,163 | 14 | 3 | 10 | +16.765 | +1.1975 | +1.17 | +13.99 |
| 20 | 100 | 2,045 | 14 | 3 | 10 | +16.680 | +1.1914 | +1.58 | +20.07 |
| 24 | 120 | 1,949 | 14 | 3 | 10 | +16.631 | +1.1880 | +2.33 | +26.92 |
| 30 | 150 | 1,799 | 14 | 4 | 10 | +16.255 | +1.1611 | +4.33 | +36.54 |
| 48 | 240 | 1,451 | 12 | 3 | 9 | +16.653 | +1.3878 | +23.33 | +70.98 |

- swept 1..48 bars (5 s..240 s). Both columns are monotone in wob across the whole range, so there is no interior optimum hidden between the rows.
- **wob 7 is the lowest wob in the score-preserving band.** wob 7, 8, 9, 10 all give +1.2032; of those 7 has the earliest backstop. That is a measured band edge, not a preference.
- wob 7 improves the mean as well: −3.36 min against wob 8's −1.85.
- trade count 13, stops 3, MFE>MAE 10 are unchanged across wob 1..10.

### THE +0.33 vs +0.42 DISCREPANCY, STATED

The earlier full-tape measurement put wob 8's median at **+0.33**; this sweep puts it at **+0.42**.
Different tape: the earlier run used `TAPE_END` 2026-09-30, this one uses the acceptance test's
2026-09-08, because the +1.2032 only exists on that tape. Neither number is wrong; they are different
windows. wob 7 beats wob 8 on the SAME tape, which is the comparison the target asks for.

### WHAT THE TARGET CANNOT DO: A NEGATIVE MEDIAN AT +1.2032

| want | wob | per trade | median |
|---|---|---|---|
| hold +1.2032, earliest backstop | **7** | +1.2032 | +0.25 |
| median at or below 0 (DRW no later than DR) | **<= 4** | +1.1229 | −0.08 |
| cost of the negative median | | **−0.0803 per trade** | |

The score-preserving band is wob 7..10 and the median is positive throughout it. A median at or below
zero needs wob <= 4, which drops the score to +1.1229.

### THE CAVEAT THAT MATTERS MORE THAN THE ANSWER

**The entire step from wob 6 to wob 7 is ONE trade.** +15.642 − +14.980 = **+0.662**, which is
exactly the 02:40:35 trade's MFE delta measured earlier in this report. At wob <= 6 the DRW latch is
fast enough that a dr-flip closes 02:40:35 at ~03:25; at wob >= 7 it is slow enough that the opposing
03:38:00 signal closes it instead, and MFE goes 0.580 -> 1.242.

- so the band edge Joe's target lands on is produced by **one trade on one day**. Effective-n: 13 trades, 1 day, 16 armed episodes. No rate is claimed.
- the backstop median, by contrast, is a whole-tape figure over ~1.56M bars and is monotone — that half of the answer is robust.
- **Joe's 0926 "we have to stick on 8" was measured on `t` tags across 154 sig_utc rows**, not on this. Moving 8 -> 7 has not been checked against that measurement, and it is the one that produced the current value.

---

## RULED 1001 — `DRW` BANKED AS IS. fence 25/75 AND wob -> octo-freedom MVP2 SWEEP

Joe: *"no changes then - we bank DRW and move on. fence25 and the wob are destined for a sweep at the
end of octo-freedom's MVP2"*.

| knob | value, banked | where it goes |
|---|---|---|
| `latch_wob` | **8 bars = 40 s** | the sweep at the end of octo-freedom's MVP2 |
| `mage_fence_lo/hi` | **25.0 / 75.0** | the same sweep |

- wob 7 is NOT applied. The sweep above supersedes the single-target answer, and the reason it should
  is in this report: the wob 6 -> 7 step is one trade on one day.
- this is a SECOND dr sweep, distinct from `MVP2.md` item 5 (`docs/o9-live-recon/`), which is the
  o9-live recon MVP2. Joe's words place this one at the end of **octo-freedom's** MVP2.

## 1001 — THE GAP 2 DIVERGENCE CHECK: IT FIRED ON 18 OF 67 BANKED ROWS

Joe: *"I agree with your priority splits - run the divergence checks now"*.

**THE TEST, and it needs no re-run.** The reference `walk_no_flip_open`
(`sweep_v3_signal.py:45` = `sweep_mae_cap.py:25`, md5 `ff31767c8a92`) closes on a `sig_utc` only when
`d == -pos['dr'] and d != 0`, and the new trade takes `pos['dr'] = d`. **So under the reference, two
consecutive trades across a `sig_utc` close must carry OPPOSITE dr.** A same-dr pair is impossible.
`bank_emit_entry.py:44`'s copy is missing that clause, so for it any `sig_utc` bar closes and
reopens — including a same-dr one.

Run against the banked rows of `wtc_v2_v7_rule1_gateopen_entry_emit_noflipopen`, the key
`bank_emit_entry.py` writes with its own copy:

| | |
|---|---|
| rows | 67 |
| `opened_by` | `sig_utc` 67 |
| **same-dr rows across a `sig_utc` close** | **18** |
| of those, `close_ms` == next `open_ms` **exactly** | **5** |
| rows skipped as UNREACHABLE (could explain a false pair) | 2, per the script's own docstring |
| **so genuine divergences** | **at least 16 of 67 = 23.9%** |

The 5 exact-millisecond pairs are the unambiguous signature — a close and a same-dr open on the
identical bar, which the reference makes inert:

| row | next | dr | close of row == open of next |
|---|---|---|---|
| n14 | n15 | −1 | 09-01 18:20:00 |
| n17 | n18 | −1 | 09-01 22:24:10 |
| n23 | n24 | −1 | 09-02 05:06:30 |
| n26 | n27 | −1 | 09-02 08:35:00 |
| n57 | n58 | −1 | 09-05 02:13:10 |

The other 13 pairs show the next `open_ms` LATER than the close, which is expected and not
exculpatory: `bank_emit_entry.py:95` banks `U(o)` where `o = EMIT.get(t['open'], t['open'])` — the
EMIT bar, not the walk's open bar — so a same-bar reopen is recorded at its later emit bar.

**WHAT IT MEANS FOR THE ROWS.** Each of the 18 is a trade the reference rule would have left running
to its real exit, and a second trade that would never have existed. So the banked 67 carry MORE
trades, each SHORTER, than Joe's 0929 rule produces. The corrected count is **not** 67 − 18: collapsing
one pair can expose the next bar to the same test, so it cascades. The exact number needs the chain
re-run and is not claimed here.

**A SECOND FINDING, FROM THE SAME QUERY.** The sibling key
`wtc_v2_v7_rule1_gateopen_entry_emit` (119 rows) has `opened_by`: `sig_utc` 67, **`dr-flip` 52**.

- **no code in the repo can produce `opened_by='dr-flip'`.** All five `opened_by` literals are
  `'sig_utc'`. Those 52 rows came from the superseded closes-AND-opens rule, before Joe's 0929
  *"dr-flip as an open is not helpful"*.
- that is expected and the script's docstring says so — it is not a second defect. It IS another
  instance of the handover's *"numbers that live outside the repo"* trap: **119 of the 332 rows in
  `wsf_trades` are not reproducible from the repo as it stands.**
- the same-dr test does not apply to those 119, because the rule that wrote them is not the rule the
  test assumes.

**NOT DONE, and it is Joe's call:** re-banking. Under `never-drop-joes-tables` a correction goes
BESIDE the existing rows under a new key, never over them, and the scope comes to Joe before the run.

### CORRECTED 1001 — THE DIVERGENCE FIGURE'S DENOMINATOR WAS WRONG, AND THE FLOOR WAS UNSUPPORTED

Joe asked how `sig_utc` is built and whether I was carrying biases. Both corrections came out of that.

| what I published | what it should have been |
|---|---|
| "18 of 67 = 23.9%" | **18 of 36 = 50%.** The `_noflipopen` key's 67 ROWS contain only **36** `sig_utc` closes (`closed_by`: `sig_utc` 36, `dr-flip` 30, NULL 1). The test only applies to `sig_utc` closes, so 67 was the wrong denominator and the figure UNDERSTATED the divergence |
| "at least 16 genuine, 2 skipped per the script's docstring" | **unsupported.** The *"TWO TRADES DO NOT APPEAR"* line is about the `_entry_emit` set; I never ran the `_noflipopen` variant to get its own UNREACHABLE count. The floor is the **5** exact-millisecond pairs, which no skip can manufacture, plus 13 more that a skip could in principle explain |

**The 5 exact-ms pairs remain immune to the skip confound.** `wt_open_ms` is the EMIT bar, which is at
or after the walk's open bar; trades are sequential, so the next trade's open bar is at or after this
one's close bar. If the next row's emit bar EQUALS this row's close bar, the next walk open bar is
that same bar exactly, and nothing can sit between.

**A number already in the repo that I should have read before measuring.** `trade_walk.py:17-19`
records the same phenomenon: *"This walk used to close on any bar in `opens` with no dr comparison at
all, and on the banked window that was 43 of 67 sig_utc closes - 64% of them - closing a trade into a
signal of its own direction."*

- **it is NOT the same row set as mine.** That 67 is a count of `sig_utc` CLOSES in a pre-inert
  `trade_walk` run on the banked window; the `_noflipopen` key has 36. No banked key has 67 `sig_utc`
  closes (`wtc_v2_v7_rule1_gateopen` has 85, `_entry_emit` 66, `_noflipopen` 36), so the 43/67 lives
  outside the banked rows.
- so it corroborates the phenomenon and does not replace the measurement. The point stands that I
  audited `trade_walk`'s copies without first reading `trade_walk`'s own docstring, which states both
  the ruling and a measurement of it.

**AND THE RULING IS REAL, which my framing had only assumed.** `trade_walk.py:12-22` carries it with
Joe's verbatim words and the case that produced it — 09-01 03:40:05, a SHORT, closed by the 04:26:00
`sig_utc` which was also a SHORT:

  *"trades must be first closed by an opposing dr signal, and secondly by a dr-flip if there is not
  opposing dr signal"* ... and asked whether a same-dr `sig_utc` should touch the trade at all:
  *"for now, it's inert"*.

So `bank_emit_entry.py:44`'s copy is genuinely missing a ruled clause, and the two matching copies are
right. **But I had reached that conclusion by taking the 2-of-3 majority as the reference, not by
reading the ruling** — and `build_wsf_trades.py:22` states the same 0929 rule as *"every UNGATED
sig_utc is a reversal: closes the open trade and opens a new one"*, with no dr condition, which is the
wording `bank_emit_entry`'s copy implements. Had that been the whole record I would have labelled the
correct copy as broken.

## 1001 — HOW `sig_utc` IS BUILT

| | |
|---|---|
| what it is | the `sig` CROSS bar of a `ws1mage_rev` leg — `legs['sig']` at `coil_exit.py:104`, from `jig.ws1mage_rev` |
| how often | the cross bar on **98 of 121** v7 rows (`build_wsf_trades.py:16-17`) |
| **it is NOT knowable at its own bar** | the cross is confirmed `boundary_xwob - 1` = **3 bars = 15 s** later, at `sig_conf`. `coil_exit.first_forward` and `resolve`'s GAP branch both return the CROSS bar, not the confirmation |
| Joe's read, 0929 | *"sig has already qualified the wob in code, but the wrong field was presented"* — **not yet ruled** |
| measured cost of moving to `sig_conf` | 119 trades either way, MFE>MAE 68 either way, MAE mean 0.698 -> 0.720, MFE mean 0.991 -> 0.969 |

- in `bank_emit_entry.py:93-96` the walk's `opens` are the `rev` bars from `coil_exit.resolve` that pass the rule#1 gate; the banked open TIMESTAMP is the EMIT bar `max(brk, rev, actionable)`, not the open bar.
- in `trade_walk`, **`'sig_utc'` is a LABEL applied to every open, not a test.** The walk receives `opens` as bar indices and never asks what produced them. That is why the `octo-sig` label is a parameter question and not a mech question.

## 1001 — Q2, THE `sig_conf` FIELD ON THE RECON'S REFERENCE PATH

### CORRECTION FIRST: I REINSERTED `brk`, AND IT IS THE SECOND TIME TODAY

I wrote *"`max(brk, rev, actionable)` does not rescue it"* about the recon's reference.

| | |
|---|---|
| `brk` in `measure_live_stop.py` | **0 hits.** It is not on the recon's reference path at all |
| `brk`'s status | **OUT**, by Joe 1001 (`OPEN.md:43`): *"there is no need to hold on to `brk` as backstop"*. `release`, `moments`, `coil_exit`, `i1`, the four `actionable_*` and the four `via` branches are all out of the mech |
| where I took it from | `bank_emit_entry.py:86-87`, which I had read minutes earlier for the divergence check — a BANKER for the v7 chain |
| first occurrence, same session | `OPEN.md:148-152`, Joe: *"I think you've reinserted a mech that I called out as lookahead... have you let a bias find its way into the handover docs?"* Withdrawn then, back now |

**The mechanism of the slip, so it is findable next time:** I reached for the emit-bar formula to
pre-empt an objection to my own claim — "and `max(...)` does not rescue it" — instead of checking
whether that formula was on the path I was describing. **Raising a mechanism in order to dismiss it is
the tell**, because it buys the argument a rebuttal it did not earn.

### THE CORRECTED STATEMENT

**There is no emit bar on the recon's reference path.** `measure_live_stop.build:132-134` returns the
gated `rev` bars, and `trade_walk.walk` opens AT those bars. Nothing stands between the signal bar and
the open.

    ex = coil_exit.resolve(m, p, conf, LEGS[d], lag, look, bool(cfg['gap_fill']))
    if ex['rev'] is not None and A <= int(ex['rev']) <= B:
        sig.add(int(ex['rev']))
    return sig, sorted(k for k in sig if rig.gate_open(k))

| | |
|---|---|
| the reference's open bar | `ex['rev']` from `coil_exit.resolve`, gated by `Rig.gate_open` |
| what that is | the **cross** bar — `first_forward` and the GAP branch both return it (`build_wsf_trades.py:17-18`) |
| confirmed at | `sig_conf` = cross + `boundary_xwob - 1` = **3 bars = 15 s** later |
| how often | the cross bar on **98 of 121** v7 rows = **81%** |
| measured cost of moving to `sig_conf` | 119 trades either way, MFE>MAE 68 either way, MAE mean 0.698 -> 0.720, MFE mean 0.991 -> 0.969 |

**octo-freedom is NOT affected.** `leash_walk.rev_lookback_mask:200` sets `a = max(sig_conf, sig)`, so
a bar is only eligible once the confirmation has passed. The 15 s is already closed inside the machine.

**UNRULED, and it is Joe's.** His 0929 words: *"sig has already qualified the wob in code, but the
wrong field was presented"*. The proposal is one line — the reference's signal bar becomes
`max(rev, sig_conf)` — and the cost is already measured. Nothing is applied.

### CORRECTED 1001 — THE `sig_conf` "NOW JOB" DID NOT EXIST

The section above said the recon's reference enters at the CROSS bar, 15 s early on 98 of 121 rows,
and called it a now job. **Wrong, and the root was a stale docstring I quoted instead of reading the
code behind it.**

| what I claimed | what the code does |
|---|---|
| `coil_exit.first_forward` returns the cross bar | `:112` returns `sc[k]`, the **`sig_conf`**. Its own docstring: *"The SELECTION is on the cross bar ... and the bar RETURNED is that cross's `sig_conf`"*, Joe 0929: *"sig_conf is unconditional - it has to happen"* |
| `resolve`'s GAP branch returns the cross bar | `:142` takes `inside[0][1]`, commented *"the FIRST cross after `named`, at ITS conf bar"* |
| so the rebuilt chain is 15 s early | it is not. CONFIRMED `:127`, GAP `:142`, FORWARD `:145` all give a conf bar |
| source of my error | `build_wsf_trades.py:18`, now struck as false. I cited a docstring as authority for a defect and never opened `coil_exit.py` |

**WHAT IS ACTUALLY 15 s EARLY:** the 121 **banked** `wsl_sig_utc` rows. `measure_live_stop.build`
never reads them. Joe's 0929 *"the wrong field was presented"* is about the BANK, not the chain.

**AND THE v7 CHAIN'S REAL LOOKAHEAD, which my wrong claim obscured:** the LOOKBACK branch sets
`rev = named = moment['i1']` (`coil_exit.py:135`), the moment's END, which is only knowable when the
next row prints. That is `i1`, and it is why `octo-freedom` carries no `i1` and no `brk`
(`leash_walk.py:34-36`). Caught by the o9-live recon session, chat #30.
