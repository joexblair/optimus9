# 1005 — the 39 octo-sig of 09-25 scored, and the baton lineage defect

Two things, both from Joe 1005.

## 1. SCORING THE ROUTING OUTCOMES

Joe: *"you can decide if the status is correct based on swing_detect + MAE/MFE. your choice on the
swing size - measure for effect. let's say that any signal which creates >0.7 MAE% (or maybe 0.8%
- your call) should be blocked"*.

Scorer: `$CLAUDE_JOB_DIR/tmp/score39.py` (sweep + per-row) and `final39.py` (the table). Output
`score39.out`, `final39.out`.

### my two delegated choices

| knob | chosen | why, measured |
|---|---|---|
| swing pct | **0.70** | the separation knee. CONF MAE median vs NOT-CONF MAE median: 0.077/0.160 at 0.40, 0.215/0.244 at 0.50, 0.258/0.628 at 0.60, **0.258/1.622 at 0.70 (6.3x, the widest of ten)**, 0.366/1.622 at 0.80, 0.495/1.681 at 1.00, 1.192/1.681 at 1.25. Median hold 24.0 min at 0.70 vs 62.1 min at 1.00 — a 0.70 % stop cannot live inside a 62-min unstopped window |
| MAE% threshold | **0.70** | not a new knob: `mae_cap` 0.70 % of entry is already live inside `trade_walk`. Measured: the >0.70 MAE set and the "adverse 0.70 touched BEFORE the favourable pivot" set are the SAME 18 of 39 rows |

DEPARTURE FLAGGED: `docs/linelab_spec.md` s0 records swing_detect **1 %** as locked by Joe. 0.70 is
my call under his explicit delegation this turn; MAE@1.0 is carried in `score39.out` for every row.

### the outcome, 39 rows

| mech says | n | MAE <= 0.70 | MAE > 0.70 | reading |
|---|---|---|---|---|
| CONFLUENCE · with-trend | 12 | 6 | 6 | 6 of 12 correct |
| CONFLUENCE · against-trend | 8 | 7 | 1 | 7 of 8 correct |
| BLOCKED (mtd.r2) | 5 | 3 | 2 | 2 of 5 correct |
| OPEN · neither | 7 | 2 | 5 | 5 would block, 2 would fire |
| OPEN · D no fire | 6 | 3 | 3 | 3 would block, 3 would fire |
| OPEN · no r block | 1 | 0 | 1 | 1 would block |

- agreement on the 25 rows the mech has a verdict on: **15 of 25**.
- **against-trend is the CLEAN path (7 of 8), with-trend is the dirty one (6 of 12).** MVP2 plans the
  smaller size for against-trend. On this one day the heat is on the other side of that split.
- the 7 heat confluences: 07:59:20, 08:06:10, 08:26:10, 10:45:15, 18:04:35, 18:06:15, 20:10:50.
  All 7 have `claim = none` — no TF objected. 3 of the 7 (10:45 ws4, 18:04 ws12, 18:06 ws1) have a
  ONE-MEMBER ex-fence block, where the band collapses to [ws1r, its floater] so no higher TF CAN
  object: 1-member 3 of 6 heat, median MAE 0.793 · 2+ members 4 of 14 heat, median MAE 0.258.
- the 3 over-blocked mtd.r2 rows (09:02, 11:14, 16:46) took 0.096/0.185/0.000 MAE. Their nets
  +14.41/+27.20/+9.49 do not separate from the 2 correct blocks (-26.92/+10.54) — no magnitude floor
  sorts them.

### what each pending ruling buys

| ruling | rows | right | wrong | net |
|---|---|---|---|---|
| `neither` = BLOCK | 7 | 5 | 2 | +3 |
| `no fire` = BLOCK | 6 | 3 | 3 | 0 |
| D empty block = BLOCK | 1 | 1 | 0 | +1 |

- all three ruled: agreement 24 of 39.
- the BAND-DEPTH knob (a claim counts only if >= X inside the band) reaches 5 of 6 at X in
  (19.78, 21.14] — a 1.36-wide window on 6 rows, one day. Not a knob; a coincidence.

## 2. THE BATON LINEAGE DEFECT — mine

Joe 1005: *"the rider tag must be earnt though the lineage of baton passes. they don't have to be
strictly sequential, hopping one or two TFs is accepted"*.

`baton.py:120-131` has NO lineage rule:
```python
avail = lambda j: [t for t in TFS if MT[t][j] and not ST[t][j]]
if rider is None:
    c = avail(j); rider = max(c)
```
The successor is the HIGHEST available mom-true-and-not-stalled TF in ws3..ws23. The outgoing
rider's TF is never consulted, so a pass can jump any distance in either direction and the chain
can never break. Measured on 09-25, 139 passes (warm bar 21:00 on 09-24 -> 23:59:55):

| hop window | the taken pass was legal | a legal successor existed | chain should have ENDED |
|---|---|---|---|
| +-1 TF | 51 of 139 | 73 | 66 |
| +-2 TF | 72 of 139 | 93 | 46 |
| +-3 TF | 78 of 139 | 98 | 41 |

The two riders Joe asked about:
- **ws23 at 02:12:10 / 02:13:10** — seated 02:03:50 on a **+14** from ws9. At that seat bar only
  ws3, ws4, ws23 were available: nothing within +-3, so the chain should have ended. The last legal
  pass anywhere in its lineage is ws7 -> ws9 (+2) at 23:26:00. **It appeared; it did not climb.**
- **ws15 at 02:42:35** — seated 02:41:30 on a **-4** from ws19, again with no +-3 option. Its
  lineage DOES hold two earned passes: ws15 -> ws18 (+3) at 02:40:40 and ws18 -> ws19 (+1) at
  02:41:05. That run was itself seeded by ws23 -> ws15 (-8) at 02:36:30, off the same cold ws23.

SCOPE: this invalidates the `riding` and `traj` columns in
`transfer/2026-09-25_baton_stall_octosig_fullday.txt` and
`transfer/2026-09-25_baton_stall_octosig_0000-1200.txt`. It does NOT touch section 1 — the mtd /
branch D table never reads `riding`.

UNSPECIFIED, Joe's to rule:
1. the hop window — "hopping one or two TFs" = `|dTF| <= 2` (ws9 -> ws11) or `<= 3` (ws9 -> ws12)?
2. no legal successor — does the chain END with `riding` blank until a fresh seed, or does the baton
   hold on the stalled rider?
3. is a DOWNWARD pass a pass at all? 43 of 127 printed passes go down, and the walk language is
   "continue consuming the HIGHER mom-true TFs as they print".

Scripts: `$CLAUDE_JOB_DIR/tmp/lineage.py`.

## 3. STAGE 2 — with-trend FLIPPED, and 09-26 added

Joe 1005: *"CONF with-trend is reading upside down - this is the stage 2 we talked of earlier. do you
want to apply your suggestion to walk to the extrema for a better position? flip the LONG with SHORT
and recreate"*.

So for every branch-D confluence graded **with-trend** (Mage net AWAY from dr) the trade side is the
OPPOSITE of the dr-bias side. `against-trend` is untouched. Script `$CLAUDE_JOB_DIR/tmp/flip39.py`,
day via `LG_DAY`; output `flip_2026-09-25.out`, `flip_2026-09-26.out`.

| day | with-trend rows | clean as published | clean flipped | gain |
|---|---|---|---|---|
| 09-25 | 12 | 6 | **10** | +4 |
| 09-26 | 11 | 6 | **9** | +3 |

| mech says | 09-25 | 09-26 | both |
|---|---|---|---|
| CONFLUENCE · with-trend · STAGE 2 FLIP | 10 of 12 | 9 of 11 | **19 of 23** |
| CONFLUENCE · against-trend | 7 of 8 | 2 of 2 | **9 of 10** |
| BLOCKED (mtd.r2) | 2 of 5 | 0 of 3 | **2 of 8** |

- 09-26 DOES produce confluences: **13 of 26** octo-sig (11 with-trend stage-2 flip, 2 against-trend).
- mtd.r2 over-blocks on both days: 3 of 5 on 09-25, 3 of 3 on 09-26 = **6 of 8**.

### THE THREE OPEN RULINGS DO NOT SURVIVE 09-26

| ruling | 09-25 net | 09-26 net | both |
|---|---|---|---|
| `neither` = BLOCK | +3 | **-1** | +2 |
| `no fire` = BLOCK | 0 | 0 | 0 |
| D empty block = BLOCK | +1 | **-5** | **-4** |

CORRECTION to section 1: `neither` = BLOCK was reported there as the one ruling that pays (+3). On
09-26 it is -1. `D empty block` = BLOCK inverts hardest: 1 row on 09-25 (heat, block correct) vs
5 rows on 09-26, all 5 clean. None of the three is a one-day call.

### "WALK TO THE EXTREMA FOR A BETTER POSITION" — NOT CAUSAL FOR THIS POPULATION

- 23 of 23 with-trend rows across both days reach step 1 by the **lookback**, so the extrema bar is
  already in the PAST at the signal: lag -0.3 m to -4.0 m. That bar is gone; the entry cannot be taken.
- My original suggestion was made about **mtd.r2**, whose extrema came from the FORWARD walk. It was
  causal where I made it. It is not causal applied here.
- measured anyway as a REFERENCE, per [[causal-options-only]] (dataset reads are fine for spec work):

| population | n | clean | heat | MAE med | MFE med |
|---|---|---|---|---|---|
| 09-25 B flipped, signal-bar entry | 12 | 10 | 2 | 0.144 | 1.202 |
| 09-25 C flipped, extrema entry (NOT takeable) | 12 | 12 | 0 | 0.275 | 0.620 |
| 09-26 B flipped, signal-bar entry | 11 | 9 | 2 | 0.241 | 0.724 |
| 09-26 C flipped, extrema entry (NOT takeable) | 11 | 11 | 0 | 0.149 | 0.276 |

The extrema entry removes all the heat and roughly halves the MFE (1.202 -> 0.620, 0.724 -> 0.276).
It buys cleanliness with move.

THE CAUSAL VERSION OF THE SAME IDEA, unbuilt and Joe's to rule: from the signal bar walk FORWARD to
the next same-dr g5Mage oob then its reversal at wob 2 — the `step 1f` machinery already in
`mtd_lens.py`. Not measured.

## 4. PnL SUMMARY

Joe 1005: *"what's the pnl summary?"*. Script `$CLAUDE_JOB_DIR/tmp/pnl.py` (per day) and
`pnl_both.py` (combined). Output `pnl_2026-09-25.out`, `pnl_2026-09-26.out`.

### the round trip I assembled — both legs banked, the pairing is mine

| leg | value | source |
|---|---|---|
| entry | the octo-sig bar, `__pxs__` | the signal |
| side | against-trend = dr-bias · with-trend = OPPOSITE (stage 2 flip) | Joe 1005 |
| stop | **`mae_cap` 0.70 %** of entry, fires when adverse 0.70 is touched before the exit | `wsf_trade_config` v3; a REQUIRED arg at `trade_walk.py:74`, live in the machine today |
| exit | the next favourable swing pivot, `find_pivots(__pxs__, 0.70)` | the banked swing-to-pivot yardstick |
| cost | **0.1975 %** per trade = 2 x 5.50 bps taker + 8.75 bps slippage at 22,000 coins | `docs/strat-3-r-oob/spec.md:77`, `docs/mage_cascade_findings.md:307` |

MY DECISION, STATED: the exit was unspecified for this population. I paired the live stop with the
banked swing-to-pivot exit rather than running `trade_walk`'s three racing exits, which have not
been run on these signals.

NOT MEASURED, assumed: a stopped trade fills at exactly -0.70 (no stop slippage); the 0.1975 drag is
ONE orderbook measurement at 22,000 coins applied flat; **position size is NOT SET** (MVP2 item 4)
so every figure is a percentage; signals 1 s to 95 s apart count as separate trades (task #7,
"review pyramids", is open on exactly that); there is NO concurrency or capital model, so the
totals only add up if every trade gets full size.

### 09-25 + 09-26 combined

| population | n | total net % | mean net % | median net % | winners | stopped |
|---|---|---|---|---|---|---|
| CONFLUENCE — the trades taken | 33 | **+20.204** | +0.612 | +0.526 | 24 of 33 | 5 |
| · with-trend, stage 2 flip | 23 | **+16.134** | +0.701 | +0.538 | 16 of 23 | 4 |
| · against-trend | 10 | **+4.070** | +0.407 | +0.436 | 8 of 10 | 1 |
| BLOCKED by mtd.r2 — rejected | 8 | **+5.047** | +0.631 | +0.430 | 6 of 8 | 2 |
| OPEN — no rule yet | 24 | **+3.226** | +0.134 | -0.002 | 12 of 24 | 11 |
| EVERY octo-sig, ungated | 65 | **+28.477** | +0.438 | +0.448 | 42 of 65 | 18 |

### what the stage 2 flip is worth — with-trend rows only, same stop, same cost

| day | rows | total net % as published | total net % flipped | delta | per trade |
|---|---|---|---|---|---|
| 09-25 | 12 | +0.800 | **+10.378** | **+9.578** | +0.798 |
| 09-26 | 11 | -0.787 | **+5.756** | **+6.543** | +0.595 |
| both | 23 | +0.013 | **+16.134** | **+16.121** | +0.701 |

Unflipped, the with-trend set is **+0.013 total over 23 trades** — flat. The flip is the whole result.

### does the gate pay? NOT on 09-26

| day | confluences | their total net % | their mean | ungated n | ungated total | ungated mean | gate pays? |
|---|---|---|---|---|---|---|---|
| 09-25 | 20 | +13.363 | +0.668 | 39 | +9.704 | +0.249 | YES |
| 09-26 | 13 | +6.841 | +0.526 | 26 | +18.774 | +0.722 | **NO** |
| both | 33 | +20.204 | +0.612 | 65 | +28.477 | +0.438 | mean yes, total no |

- the gate raises mean net per trade (+0.438 -> +0.612) and gives up total (+28.477 -> +20.204),
  because it takes 33 of 65.
- **mtd.r2 is the weak link on both tests.** It rejected 8 rows that earned +5.047 (+0.631 mean),
  which beats the mean of the trades it let through. It was already 2 of 8 correct on the MAE test.

## 5. NINE DAYS — THE FLIP DOES NOT SURVIVE. SECTIONS 3 AND 4 ARE A 2-DAY RESULT.

Joe 1005 asked for a "7 day forecast". 7 more days of octo-sig were already built (09-25 .. 10-03,
298 signals), so they were MEASURED, not forecast. Scripts `ninedays.py`, `fc7.py`.

| day | octo-sig | CONF | wt flip | at | BLOCKED | OPEN | CONF total net % | CONF mean | winners | stopped | ungated mean |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 09-25 | 39 | 20 | 12 | 8 | 5 | 14 | +13.363 | +0.668 | 14 of 20 | 3 | +0.249 |
| 09-26 | 26 | 13 | 11 | 2 | 3 | 10 | +6.841 | +0.526 | 10 of 13 | 2 | +0.722 |
| 09-27 | 34 | 18 | 15 | 3 | 3 | 13 | +4.195 | +0.233 | 11 of 18 | 6 | +0.320 |
| 09-28 | 29 | 11 | 5 | 6 | 3 | 15 | +0.008 | +0.001 | 6 of 11 | 5 | +0.068 |
| 09-29 | 47 | 22 | 20 | 2 | 7 | 18 | +10.072 | +0.458 | 16 of 22 | 6 | +0.219 |
| 09-30 | 29 | 11 | 10 | 1 | 2 | 16 | -0.090 | -0.008 | 7 of 11 | 4 | +0.358 |
| 10-01 | 24 | 17 | 13 | 4 | 0 | 7 | -0.437 | -0.026 | 10 of 17 | 5 | -0.019 |
| 10-02 | 43 | 25 | 17 | 8 | 6 | 12 | +3.581 | +0.143 | 15 of 25 | 9 | +0.057 |
| 10-03 | 27 | 14 | 14 | 0 | 2 | 11 | -0.387 | -0.028 | 8 of 14 | 4 | -0.102 |
| **9 days** | **298** | **151** | 117 | 34 | 31 | 116 | **+37.148** | **+0.246** | 97 of 151 | 44 | **+0.206** |

### THE CORRECTION

| day | wt rows | total net % as published | total net % flipped | delta |
|---|---|---|---|---|
| 09-25 | 12 | +0.800 | +10.378 | **+9.578** |
| 09-26 | 11 | -0.787 | +5.756 | **+6.543** |
| 09-27 | 15 | +0.816 | +4.690 | **+3.873** |
| 09-28 | 5 | +3.702 | -0.895 | **-4.597** |
| 09-29 | 20 | +4.055 | +7.945 | **+3.891** |
| 09-30 | 10 | +2.629 | -0.623 | **-3.252** |
| 10-01 | 13 | +7.066 | -1.232 | **-8.298** |
| 10-02 | 17 | +8.748 | +4.242 | **-4.506** |
| 10-03 | 14 | +5.353 | -0.387 | **-5.740** |
| **9 days** | **117** | **+32.382** | **+29.874** | **-2.508 (-0.021 per trade)** |

- the stage 2 flip wins on 4 days and loses on 5. Over 9 days it **costs 2.508 pp**.
- the whole confluence set: flipped **+37.148** vs unflipped **+39.656**.
- section 3's "the flip holds across both days, 19 of 23" was a 2-day result. It does not generalise.
- the confluence gate is marginal over 9 days: +0.246 mean vs +0.206 ungated. 4 of 9 days flat or negative.

### LEVERAGE — the one number with no free parameter, then the ladder that needs Joe's tolerance

| measure | 9 days |
|---|---|
| worst single trade | **-0.8975 %** (mae_cap 0.70 + 0.1975 cost) |
| L at which ONE worst trade wipes the account | **111.4x** = 100 / 0.8975 |
| longest consecutive losing run | **3 trades** |

Drawdown binds far earlier than 111.4x. Compounding the 151 confluences chronologically:

| L | final equity x | total return % | max DD % |
|---|---|---|---|
| 1x | 1.4397 | +43.97 | 5.46 |
| 2x | 2.0442 | +104.42 | 10.78 |
| 3x | 2.8634 | +186.34 | 15.95 |
| 5x | 5.3991 | +439.91 | 25.81 |
| 10x | 21.1105 | +2011.05 | 47.44 |
| 20x | 132.5129 | +13151.29 | 77.32 |
| 30x | 268.0455 | +26704.55 | 92.22 |
| 50x | 30.7358 | +2973.58 | 99.68 |
| 75x | 0.0002 | -99.98 | 100.00 |

| max DD target | max L | final | total |
|---|---|---|---|
| <= 10 % | **1.9x** | 1.94x | +94.3 % |
| <= 20 % | **3.8x** | 3.72x | +272.1 % |
| <= 25 % | **4.8x** | 5.13x | +412.8 % |
| <= 33 % | **6.6x** | 8.52x | +752.5 % |
| <= 50 % | **10.7x** | 24.77x | +2376.7 % |

HALTED, Joe's to set: (1) the max-drawdown tolerance that defines "contains loss" — every L above
is a function of it; (2) the ramp rule for "increase over time" — the non-arbitrary form is to
re-derive L each day from running equity so the worst historical losing run (3 trades = -2.69 %
ungeared) costs a fixed FRACTION of current equity, and that fraction is a value, not a measurement.

### THE 7-DAY PROJECTION — day-block bootstrap, 20,000 paths over the 9 measured days

| variant | L | p5 | median | p95 | P(final < 1.0) | P(max DD > 50 %) |
|---|---|---|---|---|---|---|
| with the flip | 1x | 1.0938 | **1.3187** | 1.6441 | 0.2 % | 0.0 % |
| with the flip | 5x | 1.4681 | **3.5640** | 10.5793 | 0.4 % | 0.0 % |
| with the flip | 10x | 1.7764 | **9.9095** | 78.9996 | 1.2 % | 1.0 % |
| NO flip | 1x | 1.2022 | **1.3561** | 1.5186 | 0.0 % | 0.0 % |
| NO flip | 5x | 2.3121 | **4.1588** | 7.2642 | 0.0 % | 0.0 % |
| NO flip | 10x | 4.2936 | **13.5106** | 39.4447 | 0.0 % | 15.6 % |

- the unflipped set is better at every percentile below p75 AND tighter: p5 1.2022 vs 1.0938 at L=1.
- blocks are whole days drawn with replacement, so within-day clustering and day-to-day spread are
  preserved. It is a resample of 9 days; it cannot know a regime those 9 days do not contain.
- the 9 days are all in-sample for the mech's knobs. Nothing here is held out.

## 6. STOP 0.70 vs 0.80, WITH PYRAMID MAX 2

Joe 1005: *"apply a 0.7% and 0.8% stop / and pyramid max 2 trades"*. Script `stops_pyr.py`,
output `stops_pyr.out`. 9 days, 151 confluences before the cap.

PYRAMID 2 taken from the banked precedent, not invented:
- `docs/sneaky_trade_1_handover.md:176` — *"pyramid | **max 2** concurrent | Joe 0916, verified
  held-out 0917"*. A confluence arriving while 2 are still open is SKIPPED; queueing would need a
  rule that does not exist.
- same file line 174 — *"22,000 coins, fixed. On a staggered pair that is 22,000 EACH"*. So size is
  **full on each leg**, not split. The cap is flat across the book, not per side.

| stop | side rule | confluences | taken | skipped by pyramid 2 | stopped out of taken |
|---|---|---|---|---|---|
| 0.70 % | stage 2 flip | 151 | 144 | 7 | 42 = 29 % |
| 0.70 % | dr-bias, no flip | 151 | 144 | 7 | 43 = 30 % |
| 0.80 % | stage 2 flip | 151 | 143 | 8 | 39 = 27 % |
| 0.80 % | dr-bias, no flip | 151 | 144 | 7 | 35 = 24 % |

| stop | side rule | taken | total net % | mean net % | median net % | winners | worst trade % |
|---|---|---|---|---|---|---|---|
| 0.70 % | stage 2 flip | 144 | +35.999 | +0.250 | +0.265 | 93 of 144 | -0.897 |
| 0.70 % | dr-bias, no flip | 144 | +37.938 | +0.263 | +0.385 | 97 of 144 | -0.897 |
| 0.80 % | stage 2 flip | 143 | +35.750 | +0.250 | +0.277 | 94 of 143 | -0.998 |
| **0.80 %** | **dr-bias, no flip** | 144 | **+47.124** | **+0.327** | **+0.406** | **103 of 144** | -0.998 |

- **0.80 beats 0.70 by +9.186 pp on the no-flip set** (+47.124 vs +37.938) and does nothing on the
  flipped set (+35.750 vs +35.999). Stop rate 30 % -> 24 %.
- the flip loses at BOTH stop levels. Section 5's correction holds.
- 0.80 / no flip is positive on **9 of 9 days**: +2.264, +1.694, +6.223, +4.305, +5.786, +3.860,
  +10.505, +6.037, +6.452.

### what the pyramid-2 cap costs

| stop | side rule | ungated total % | pyramid-2 total % | delta | mean before | mean after |
|---|---|---|---|---|---|---|
| 0.70 % | stage 2 flip | +37.148 | +35.999 | -1.149 | +0.246 | +0.250 |
| 0.70 % | dr-bias, no flip | +39.656 | +37.938 | -1.717 | +0.263 | +0.263 |
| 0.80 % | stage 2 flip | +37.979 | +35.750 | -2.229 | +0.252 | +0.250 |
| 0.80 % | dr-bias, no flip | +49.483 | +47.124 | -2.359 | +0.328 | +0.327 |

The cap drops 7 or 8 of 151 and moves the mean by 0.000 to +0.004. At this signal density it is
almost free and almost inert — 3-deep overlaps are rare.

| stop | side rule | L=1 | L=2 | L=3 | L=5 | L=10 | DD at L=5 | DD at L=10 |
|---|---|---|---|---|---|---|---|---|
| 0.70 % | stage 2 flip | 1.4235 | 1.9993 | 2.7712 | 5.1224 | 19.1879 | 27.99 % | 50.45 % |
| 0.70 % | dr-bias, no flip | 1.4521 | 2.0824 | 2.9496 | 5.7076 | 24.2492 | 24.14 % | 46.30 % |
| 0.80 % | stage 2 flip | 1.4194 | 1.9860 | 2.7401 | 5.0056 | 17.9295 | 33.79 % | 58.47 % |
| **0.80 %** | **dr-bias, no flip** | **1.5911** | **2.4980** | **3.8703** | **8.9383** | **58.2771** | **26.54 %** | **47.13 %** |

Exposure census under the cap: both legs open for 16.5 % to 18.2 % of total open time.

CAVEATS, all flagged:
- the 0.80 stop is WIDER than the 0.70 swing used to place the exit pivot, so a trade can lose more
  than the move that defines the exit. Joe named both levels; this is stated, not corrected.
- **two points is not a sweep.** 0.80 > 0.70 on the no-flip set over 9 IN-SAMPLE days. The direction
  says the live `mae_cap` 0.70 may be binding early; it does not say where the knee is.
- with full size on each leg, a realised close-order chain cannot see the simultaneous unrealised dip
  of two open legs, so the drawdown understates the overlap.

## 7. THE COMPOUND PnL TABLE, BANKED — `lazyg_compound`

Joe 1005: *"now let's see the complete table showing the compound pnl, in a db table. for each trade
decide the leverage that will be applied in accordance with safe practices. account starts at 888
dollars"* then *"drop the pyramid max"*.

Script `$CLAUDE_JOB_DIR/tmp/compound_db.py`. NEW table, nothing dropped. 151 rows per sizing mode.

| knob | value | where it came from |
|---|---|---|
| side rule | dr-bias, NO flip | section 5 — the flip costs 2.5 pp over 9 days |
| stop | 0.80 % | Joe 1005, the better of the two he named |
| swing | 0.70 % | places the exit pivot |
| cost | 0.1975 % | banked drag at 22,000 coins |
| pyramid | **NO CAP** | Joe 1005, "drop the pyramid max" |
| start | 888.00 USD | Joe 1005 |
| risk budget | **2.0 % of equity per entry** | MY CHOICE — the classic 2 %-risk convention, swept below |

Every one of those is in `uq_lc`, the unique key, so an A/B cannot overwrite itself.

### THE LEVERAGE RULE — my decision, named because it is a value

- the worst case per trade is **known before entry and is not an estimate**: stop 0.80 % + cost
  0.1975 % = **0.9975 % of notional**. A risk budget therefore converts straight to leverage.
- with the pyramid cap dropped, concurrency is unbounded — **measured max 4 concurrent legs**. A
  constant 2 % per leg would let 4 live legs stack to 8 % of equity at risk.
- so the budget is **divided at the moment of entry**, which is causal (`n_live` is known then):
  `risk_i = 2.0 / (n_live + 1)` · `lev_i = risk_i / 0.9975`
- alone **2.00x** · one leg live **1.00x** · two live **0.67x** · three live **0.50x**. It never
  reaches zero, so no trade is silently dropped — Joe dropped the cap.
- dollar size grows as equity compounds while leverage stays bounded. That is the ramp.

### RESULT

| sizing mode | trades | start $ | final $ | return % | max DD % | peak lev | min lev | mean lev | worst trade $ | best trade $ |
|---|---|---|---|---|---|---|---|---|---|---|
| **shared budget** (divided) | 151 | 888.00 | **2,022.18** | **+127.72** | **10.54** | 2.01x | 0.50x | 1.74x | -40.38 | +98.40 |
| constant per leg (sneaky-1 precedent) | 151 | 888.00 | 2,303.47 | +159.40 | 11.46 | 2.01x | 2.01x | 2.01x | -44.97 | +106.90 |

| day | trades | equity close $ | day P&L $ | day % |
|---|---|---|---|---|
| 09-25 | 20 | 917.95 | +29.95 | +3.37 % |
| 09-26 | 13 | 941.72 | +23.77 | +2.59 % |
| 09-27 | 18 | 1,035.31 | +93.59 | +9.94 % |
| 09-28 | 11 | 1,123.24 | +87.92 | +8.49 % |
| 09-29 | 22 | 1,228.08 | +104.85 | +9.33 % |
| 09-30 | 11 | 1,330.26 | +102.18 | +8.32 % |
| 10-01 | 17 | 1,620.90 | +290.64 | +21.85 % |
| 10-02 | 25 | 1,818.72 | +197.82 | +12.20 % |
| 10-03 | 14 | 2,022.18 | +203.47 | +11.19 % |

### THE SWEEP AROUND MY ONE CHOICE

| risk per entry % | lev when alone | final $ shared | DD % shared | final $ constant | DD % constant |
|---|---|---|---|---|---|
| 0.5 | 0.50x | 1,096.62 | 2.72 | 1,135.17 | 2.96 |
| 1.0 | 1.00x | 1,349.46 | 5.38 | 1,444.05 | 5.86 |
| 1.5 | 1.50x | 1,654.79 | 7.99 | 1,828.16 | 8.69 |
| **2.0** | **2.01x** | **2,022.18** | **10.54** | 2,303.47 | 11.46 |
| 3.0 | 3.01x | 2,988.98 | 15.49 | 3,606.24 | 16.82 |
| 5.0 | 5.01x | 6,273.17 | 24.77 | 8,371.75 | 26.80 |
| 8.0 | 8.02x | 17,306.05 | 37.22 | 25,992.19 | 40.08 |
| 10.0 | 10.03x | 31,966.54 | 44.62 | 50,865.94 | 47.88 |

Return is near-linear in the budget and so is drawdown — there is no knee, so 2.0 is a convention,
not a measured optimum. Joe's to move.

CAVEATS:
- **all 9 days are in-sample** for every knob in the mech. Nothing is held out.
- the `lc_eq_close` column is the equity after THAT trade's close, and closes do not follow the open
  order, so read top-to-bottom it is not monotonic (rows 108-110, 89-90). That is correct
  bookkeeping, not an error.
- a trade is sized off equity at its OPEN; with up to 4 legs live, the realised close-order chain
  cannot see the simultaneous unrealised dip, so `lc_dd_pct` understates intraday heat.
- no funding, no stop slippage, no exchange margin-tier or liquidation mechanics are modelled.

### DRAG, reported separately — Joe 1005: "I don't see drag reported"

GAP, FIXED: the drag was folded inside `lc_net_pct` with no column of its own and no dollar total.
`lazyg_compound` now carries **`lc_drag_pct`** (0.1975, % of notional, per trade), **`lc_gross_usd`**
(notional x gross %) and **`lc_drag_usd`** (notional x 0.1975 %). 151 rows per mode re-banked.

| day | trades | notional traded $ | gross P&L $ | drag paid $ | net P&L $ | drag as % of gross |
|---|---|---|---|---|---|---|
| 09-25 | 20 | 30,103.97 | +89.40 | **-59.46** | +29.95 | 66.5 % |
| 09-26 | 13 | 22,988.46 | +69.17 | **-45.40** | +23.77 | 65.6 % |
| 09-27 | 18 | 32,268.60 | +157.32 | **-63.73** | +93.59 | 40.5 % |
| 09-28 | 11 | 20,812.06 | +129.03 | **-41.10** | +87.92 | 31.9 % |
| 09-29 | 22 | 46,835.16 | +211.36 | **-92.50** | +118.86 | 43.8 % |
| 09-30 | 11 | 25,236.27 | +138.00 | **-49.84** | +88.16 | 36.1 % |
| 10-01 | 17 | 39,544.98 | +368.74 | **-78.10** | +290.64 | 21.2 % |
| 10-02 | 25 | 82,594.12 | +360.94 | **-163.12** | +197.82 | 45.2 % |
| 10-03 | 14 | 42,705.18 | +287.81 | **-84.34** | +203.47 | 29.3 % |
| **9 days** | **151** | **343,088.80** | **+1,811.79** | **-677.60** | **+1,134.18** | **37.4 %** |

- drag per trade: **$4.49 mean**, $0.88 min, $8.00 max. It is 0.1975 % of notional, so it grows as
  equity compounds.
- **$677.60 paid to make $1,134.18** — drag is 59.7 % of the account's growth.

| variant | final $ | return % | delta $ | delta pp |
|---|---|---|---|---|
| as traded, drag 0.1975 % | 2,022.18 | +127.72 | — | — |
| drag 0.0000 %, no fees no slippage | **3,382.13** | **+280.87** | **+1,359.95** | **+153.15** |

Compounded, drag costs **$1,359.95**, not the $677.60 simple sum — every dollar of drag is a dollar
that never compounds again.

SLICING NOTE: the drag table groups by the trade's OPEN day (`lc_day`). The equity table in the
section above is sliced at the LAST CLOSE on each day. The two differ at the midnight boundary
(09-29 / 09-30) because a trade opened 09-29 23:44 closes on 09-30. The 9-day totals agree:
+1,134.18 = 2,022.18 - 888.00.
