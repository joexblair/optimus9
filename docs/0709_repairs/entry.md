# 0709 repairs — ENTRY (arm · big leg · finisher)

Milestones the bot must pass to be profitable. Source: the 0709 live arm probe (`O9_PRODUCER=arm`, 10:19→17:59,
7h40m, 38 arms) plus 42d backtest. Parent: `docs/arm_delay_research.md` (CLOSED) · `docs/causal_lookahead_register.md`.

| mechanic | learnt | needs attention |
|---|---|---|
| **arm** | Spec's base clause was never built. Fixed, causal, window-invariant. 38 live arms, every one at an `s5m` reversal, none at a breach. | Nothing. |
| **big leg / hold** | Latches on an **emerging wick** — `s7M` touched `85.24`, closed `78.40`. | **Hold path never executed.** 0 of 38 arms held. Untested branch. |
| **arm→trade** | 38 arms → 38 trades, 1:1. | 20 `close_leg` errors (see misc.md). |

---

## 1. The arm — FIXED (`e10b856`)

**[read]** `docs/arm_delay_research.md`: *"base (unconditional): the arm waits for the **s5m reversal** instead
of the s5m breach."* The build never implemented it — `arm_delay`'s own docstring said so. It armed at the
breach whenever a forward scan found no big leg ahead, and the scan started at `i+1` so it never read the arm's
own bar. Live's window ends at the arm bar (`cap == i+1`, empty range), so **live armed at every breach**:
blindness to the present, not foresight. The full-history backtest scanned into bars that did not exist when
live had to commit. Same defect, two ends.

**The rule now:** a breach is never an arm — it creates a *candidate*. The candidate's trigger is the **s5m
reversal**. At that bar: big leg visible → **hold**, trigger becomes the **s5Mage reversal**; no big leg → the
arm **fires there**. Further breaches on a live candidate are swallowed (same excursion). Opposite-side s5m
breach cancels. No `cap`, no scan.

### Example A — 07-06, six breaches → three arms **[measured]**
```
breaches (es=+1) : 20:40:40  20:51:10  21:22:45  21:23:00  21:23:45  21:28:40
price            : 0.16381 -> 0.16753   (+2.3% over 49 min: live shorted every ripple)
OLD backtest arm : 21:29:40 (single)  <- reached by scanning 48 min ahead for a leg
OLD live arms    : all six            <- reached by never checking the present
NEW arms         : 20:59:55 · 21:24:25 · 21:29:40   (all at s5m reversals)
```

### Example B — 07-09, live, the state machine walking **[measured]**
```
10:10:30 breach -> candidate      10:14:05 rev, no candidate -> nothing
10:11:20 rev    -> ARM, popped    10:16:40 rev, no candidate -> nothing
10:17:10 breach -> candidate      10:19:25 breach -> candidate
10:19:00 rev    -> ARM, popped    10:19:35 breach -> SWALLOWED (same excursion)
                                  10:20:15 rev    -> ARM, popped
```
Both halves of the gate are live: a breach alone is not an arm, and **a reversal alone is not an arm either**.

**[measured]** Window-invariance: 12 truncation points, 0 mismatches. Full-window arms 1150 → 464.

**Proposed fix:** none. Verify the `s5r` divergence arm follows the same rule under a longer sample.

---

## 2. The big leg / hold — UNPROVEN

**[measured]** The big-leg gate is `d5h & d7h & ((s7r >= 85) | (p7 == 1))` — s5Mage AND s7Mage each *travelled
directly* to the `es` side (a **latch**, held until the line re-touches the opposite band), AND s7r breached or
is predicted. Joe's prior was that "sees big leg" = `s7r` predicted; it is one of three ANDed conditions.
Frequency: **9 bars out of 637** in the studied hour (1.4%).

### Example — 07-06 21:28:50, the wick that latched **[measured]**
```
             emerging s7M   closed s7M (epoch / midnight)
21:28:50        85.24          79.61 / 78.20     <- gate reads emerging; latches d7h here
21:29:00        84.59          78.40 / 78.20
22:17:00        92.97          87.97 / 106.42    <- decisively OOB (Joe's chart reading)
```
The forming 7-minute bar cleared the 85 boundary by **0.24** and closed back at **78.40**. `oob_2_oob` latched
on that touch and holds until `s7M` returns ≤15. **Causal — live genuinely saw 85.24 — but possibly wrong.**
Not an anchor artifact (epoch vs midnight differ by −1.41 there; though **+18.45** at 22:17 — the non-divisor 7m
anchor is wild elsewhere, its own problem).

**Consequence:** the leg lapsed *before* the s5m reversal at 21:29:40, so all three arms fired on the base
clause. **0 of 38 live arms held.** The tide screen we rebuilt has never executed the branch it is named for.

**Proposed fixes (A/B, none chosen):**
- **(a)** latch only on a **closed** OOB — stale by ≤1 HTF bar, not future, so still live-legal.
- **(b)** require the emerging touch to persist **N bars** before latching.
- **(c)** leave as-is; the latch is causal and the wick is real information.
- **(d)** relax the conjunction (`s7r`-predict alone · `d7h` only · full three-way) — this is the knob that
  decides how often the tide screen intervenes at all. Nobody has measured the middle ground.

**First requirement:** find a window where the big leg is visible **at** an s5m reversal, so the hold branch
executes at least once before any of the above is swept.

---

## 3. `fin_unlatch` — FIXED (`042f486`), not re-measured post-arm-fix

**[measured]** The entry waited on an unordered `.any()` over a box reaching `fin_fwd` bars **past** the
unlatch, then entered at the *first* `s15a`. 217/1897 M1 trades (11.4%) were authorised by an `s30a` that fired
**after** the entry bar (p50 = 4 bars = **20s**). Live's `cap<=T+1` made `tk != T` for exactly those, so
o9-live never fired them while the backtest booked all 217.

Repaired to spec §4 (*"walk forward with 2×30s tolerance for a late line"*): enter at the first `s15a` at/after
the authorising `s30a` — what `fin_gate` already did with `max(j15, j30)`.

**[measured]** The look-ahead was **costing** money: early entries mean **−0.0203%/trade**; the same setups
entered 20s later pay **+0.1292%** at 57.4% win. Arm A `+122.71%` → Arm B `+134.17%` over 42d.

**Needs attention:** all of that was measured on the **old arm**. The book must be re-derived on the new one.

---

---

## 4. RE-BASELINE, 2026-07-09 19:05 UTC — the fixed arm's 42d book is net negative

`rebaseline_fixed_arm.py`, same window, same exit, same knobs, `strand_rescue` excluded. **[measured]**

```
                 OLD (breach arm)      NEW (fixed arm)
entries              2628                  1540
net                +133.97%              -266.55%
mean/trade         +0.0473%              -0.1731%
win rate              51.5%                 43.7%
avg winner          +1.060%               +0.921%
avg loser           -1.022%               -1.023%
stopped          1050 (40.0%)           717 (46.6%)
MAE p50 / p90    0.639% / 0.999%      0.803% / 1.008%

M1 -157.74%  ·  M2 -108.81%       (win 43.7% on both halves)
reason=exit  n=818  +573.89%  81.8% win
reason=SL    n=717  -845.68%  avg -1.179%
stack-close cost  -35.0% -> -5.7%    depth_max 14 -> 7
```

**The old +133.97% was the look-ahead.** Removing it removes the edge.

**Entry quality got worse, not better.** MAE p50 `0.639% -> 0.803%`. The arm that waits for the reversal enters
*deeper into adverse excursion* than the arm that fired at the breach. The original arm-delay claim
(`MAE 0.52 -> 0.32`) came from the forward scan.

Three facts bound the interpretation:
- `arm_wob = 7` — the reversal needs 7 consecutive same-direction bars. **[inferred]** the arm may now fire well
  after the turn. Not measured.
- Every knob in this run (`sl=0.90%`, the curl exit seams, `fin_lb`/`fin_fwd`) was swept against the breach-arm
  book.
- The hold path still never fires (big leg is 1.4% of bars).

---

---

## 5. hb33 bias entry-filter — DISPROVEN AND REMOVED, 2026-07-09

Tested as the candidate to close the 8.3-point win-rate gap (`42.1%` actual vs `50.4%` breakeven). It rejected
entries whose side opposed a 33-minute bias direction, built from three band pairs (`hbhl33`/`hblo33`/`hbhi33`)
crossed and clustered.

**[measured]** 42d, breach arm, both alignment stamps:
```
baseline (no filter)      n=3311  mean=-0.1737%  win=42.1%  breakeven=50.4%  stopped=49.8%
bias filter, leaky stamp  n=1689  mean=-0.2264%  win=41.6%  breakeven=52.9%  stopped=50.1%
bias filter, causal stamp n=1640  mean=-0.2097%  win=42.1%  breakeven=52.5%  stopped=49.6%
```
- Rejects ~50% of the book (49.0% / 50.5%).
- **Both stamps are worse than baseline.** Not a look-ahead edge — no edge.
- Win rate after filtering equals the unfiltered book. The rejections are uncorrelated with outcome.
- Average winner shrinks enough to raise breakeven from `50.4%` to `52.5%`.

The prior claim (`docs/exit_v2_design.md` §4: *"avg +0.389% / win 77%"*, 84,700-combo sweep, 98% of configs beat
baseline) was measured on one 5-day window with the look-ahead arm. It does not reproduce.

**Removed as a candidate mechanic (Joe, 0709):** `sweep_eval._bias_filter`, the `bias_filter` config key,
`sweep_run`'s `bias_on` / `hb_*` / `bro_N` knobs, and `exit_v2_design.md` §4. `bias_state.bro_stream` /
`bro_verdict` remain — other consumers read them.

---

## Open, ranked

1. **Sweep `arm_wob`.** A 7-bar confirmation on a 5-minute line may be the whole deficit. It has never been
   swept against a causal arm.
2. **Make the hold branch execute once.** It is the only untested path in the arm.
3. **Re-sweep every knob** on the new book: `sl`, curl seams, `fin_lb`/`fin_fwd`, exit family. All were fitted
   to the breach arm.
3. **`s5r` coarse-curl as the base trigger** (Joe): A/B against the `s5m` reversal *after* the signals are
   known true.
4. Confirm the `s5r` divergence arm obeys the same candidate rule.
