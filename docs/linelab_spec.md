# linelab — bi-directional trade-signal spec (Joe 0724-25)

Warm-cache line laboratory (`linelab.py`) for building ONE mirror-symmetric short/long trade signal. All numbers
are measured on the sweep's exact basis (px_smooth EVENT bars, `find_pivots`) so they are bit-comparable to the
RPL evo / failscan.

## 0. The core yardstick — `swing_detect @ 1%` (Joe's gut, 0725)

**This is the load-bearing mechanic, not the confluence lines.** Every MFE/MAE is measured **swing-to-pivot**:
`find_pivots(px_smooth_event, 1.0)` defines what counts as a move; the entry is anchored and measured **forward to
the next favourable pivot only** (a pre-entry adverse move belongs to a different leg → a clean favourable-side entry
scores **MAE = 0**, never tagged as an adverse leg). **No stops** — pure MFE/MAE. Flip-to-flip holding was tried and
**rejected** (not the right mechanic). The 1% swing is the definition of a tradeable move; the signal's whole job is
to enter one early and clean.

## 1. Mechanics stack (siglab, mirror-symmetric)

`d = -1 SHORT / +1 LONG`. Everything mirrors (`siglab.py`).
- **Cadence = s5** (dialed from an exhaustive cadence sweep 4-8: s5 gives the earliest entry AND best MFE/MAE;
  s4 overshoots into noise, s8 enters ~0.26% later and captures ~50% less MFE). `xm_cross(base='s5', wob=6)` — the
  s8x×s8m stack minus the align gate: wob-6 debounce → sustained-OOB dwell (180s) → opposite-side guard.
- **s4 episode** (the twitchy line, EXCLUDED from TF sweeps): `T*` = the s4x episode extreme (argmax on a HI run for
  SHORT / argmin on a LO run for LONG) within an **18-min lookback** of the cadence marker (18 not 30 so a stale prior
  twitch can't mask s4x genuinely failing to breach). HTFs are sampled **at T\*** (not their own wide episodes).
- **roll gate**: the fast s4 must have exhausted — `d * gap_s4 >= 0` (SHORT: x peaked ≤ its mid m; LONG: x troughed ≥ m).
- **confluence (AND)**: `strength_slow >= thr_slow AND strength_fast >= thr_fast`, where `strength` = how far an HTF is
  stretched the favourable way vs s4 (SHORT `gap_htf-gap_s4`, LONG `gap_s4-gap_htf`). ONE config, mirror-applied to
  both directions — **separate short/long tunings are overfitting** (Joe).

## 2. The honest robust result (14-day OOS split, 0725)

Sweeps are **exhaustive step=1** (every integer TF 6-30, every integer threshold — 🪖 no number left behind). The
naive "rank by median net" is **gamed by the threshold knob** (crank it → 8-9 lucky fires → fake +2.0 net) and by
window luck. The 7-day peak `s26≥12 & s10≥6` (+2.05) was exactly that — **gone at 14 days**. Correct objective =
**ROBUST = min(fitNet, testNet, each direction, each half)** on a fit-first-7d / test-last-7d split — nothing hides.

**What survives every filter:**
- **`s10` is the one universal confirmer** — in every top-robust config across 7d→14d, threshold-gaming, and
  fit/test. The genuine discovery of the sweep.
- **Honest edge ≈ +1.13 net/trade, ~88% bank, balanced** short≈long. NOT the gaudy +2.0 (those were single slices
  hiding a weak slice).
- Your original **`s26 & s10` *structure* was real; the *thresholds* were the overfit** — `s26≥19 & s10≥5` survives
  robustly; `s26≥12 & s10≥6` was the window spike.
- ⚠ **Open — the confluence may be near-single-line:** several top-robust configs have a near-inert slow anchor
  (`s20≥3` ≈ always-true) → the robust core may be **`s10 strength ≥ ~16` alone**. Test single-s10 vs the pair under
  the ROBUST objective before trusting the second line.

## 3. Knob census + what's still unturned

Swept step=1: slow TF, fast TF, thr_slow, thr_fast. **Locked by Joe:** swing_detect 1%, swing-to-pivot, no stops,
cadence s5. **Not yet swept (all regenerate the marker set → siglab params + outer loop, ROBUST-scored):**
roll-margin (exhaustion depth), lookback (18min), s4 OOB level (85/15), cadence wob (6), cadence dwell/guard.
Rebuild-required (deferred): x len5/mult0.37, m len6/mult0.45.

## 4. Files
- `siglab.py` — mirror-symmetric core (`Lab.extreme/gap_s4/score/leg`, `markers`, `strength`).
- `build_gap_report.py` → `gap_report` (per-cadence multi-TF gap table). `build_cadence_markers.py` → `cadence_markers`.
- `build_confluence_sweep.py` (exhaustive unified) · `build_oos_split.py` (ROBUST fit/test) · `cadence_sweep.py`.
- `build_trade_report_hs60.py` → `trade_report_hs60`; `score_shorts.py`, `build_flips.py` (flip-to-flip, rejected).
