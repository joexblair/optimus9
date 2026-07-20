# rpl flow — spec

*Causal/emerging only. A **walk** = one flip cycle, labelled `DD_NN`. Storage: `docs/rpl_event_store_spec.md`.
Research impl: `rpl_flow.py` (pre-confirm) + `rpl_s8cycle.py` (post-confirm climb).*

## Cycle (per walk)
1. **Flip** (`flip_finisher`) fires → post-flip transitional state.
2. **s2-cycle (s1/s2 direction cycle)** — runs from the flip with **NO timeout**. Joe's rule, verbatim:
   > s2-cycle needs to run until 1) any s8-cycle TF is r-pred'd, or 2) s1 or s2 create an exhaustion event. one of these 2 scenarios is 100% gauranteed to happend, so there's no need for a timeout

   Reversal trigger = an **s1/s2 exhaustion** (LTF x-cross-pred against the current dir — r at the boundary +
   an x-cross, so it can't fire at the flip seam where r sits at the opposite extreme) = **step 1**. The
   reversal then fires at the **delegate x×r wob cross** (`dTF = max(delegate_tf_floor, etf − delegate_offset)`
   → TF2 delegates to **TF1**), exactly as the main flip's provisional — **close the current trade AND open the
   opposite (reverse)**, re-watch from the reversal (`dir_reverse`). On an **s8-cycle TF (s3–s8) r-pred'd in the
   current dir** → **s8 climb takes over** (`dir_confirm`). Whichever fires first. `s1s2_confirm_tol_ms` retired.
   **gcs5 finisher (wired):** after the delegate cross, on **event bars only** (volume>0 — the index-vs-event
   gotcha, `quirks_to_remember.md`), the reversal fires at the **FIRST** flip-direction gcs5x×gcs5m cross where
   **gcs5r was OOB on the exhausted-leg side within the last `gcs5_r_tol` (4) event bars** (r drops out of OOB
   as the top/bottom rolls over, so it's a tolerance not a same-bar gate). gcs5 = generic r/m/x at 5s. First,
   because realtime can't wait for a better one. (12_04: reversals 05:09:35 / 05:25:00 / 05:50:45 / 06:07:35.)
3. Confirmed → **s8 cycle** takes over rpl: the r-pred baton passes s1/s2 → **s3** and climbs. The confirm
   **gates** the same walk's climb — it does not terminate the walk.

## Climb — current_tf (r-pred frontier)
- **r-pred = `predict_breach`==+1 OR r has actually breached** (r ≥ HI, bias side). A breached TF stays
  r-pred; it does NOT drop out when predict_breach switches off. (Predict-only collapses the frontier to
  0 during a breach run — the ladder must stay alive through it.)
- **current_tf = the highest r-pred TF, monotonic up** — never looks back. s3–s8 is the transitional
  space; if r-pred picks a TF > s8, current_tf jumps straight there, no transition. (Subsumes the old
  "HTF handoff" — it's just the frontier climbing.)
- **Cadence = every EVENT bar** (0720 look-ahead fix). The old s1x×s1m marker cadence had multi-minute gaps
  (e.g. 12_04 08:47:15→08:55:45); the exhaustion look-back window `(prev, now]` then swallowed a cross that
  crossed early (08:47:40) but wasn't *detected* until the late marker (08:55:45) — and the flip was stamped
  from the early cross = **back-dated ~16 min (look-ahead)**. Per-event-bar detection catches each cross at its
  true time = causal. [measured vs detect/capwin fixes: perbar keeps the true cross times, the others delay
  every exhaustion.] (index-vs-event, `quirks_to_remember.md`: iterate event bars, not the 5s grid.)
- **Emerging lines only — seam-carry REMOVED.** It protected the (dropped) velocity calc and lagged
  every line ~2min at each bar seam, hiding real crosses AND breaches. Emerging = what TV / o9-live see.

## x-cross-pred → EXHAUSTION
- **Terminology: "exhaustion" is used EXCLUSIVELY for x-cross-pred = true** — NOT for the climbing
  current_tf (which was loosely called exhaustion until 0719).
- x-cross-pred is **NOT bound to current_tf**. It is tested across the **look-back range**
  [current_tf down to `xcp_tf_floor` (19)].
- **No TF selection.** The range is a set of candidates; exhaustion is simply the **first lower TF to
  cross** (chronologically). We wait for one of them to cross. The exhaustion may fire EARLY (mid-climb,
  e.g. 12_02 s19@02:54) — that's fine, because the **s1 finishing step** (below) refines the flip forward
  to the true reversal. (Override/latch attempts to suppress early exhaustions were retired — the
  finishing step does the job instead.)
- A TF's x-cross-pred fires when: x **down-crosses** r (bias-side down-cross of x−r / x−M / x−HI) AND
  **r within `xcp_bnd_offset` (4) of the boundary** (r > HI−4) AND s2r on the flip (es) side of 50.
  The 4-point rule fixes the conundrum that a mid-board x-cross could just be "r predicted, not yet
  OOB"; requiring r at the boundary makes it a genuine reversal — and it subsumes the old
  higher-TF-overrides-lower rule (a lower TF only qualifies once its own r is at the boundary).

## Flip (provisional → s30 finishing)
- Exhaustion → **provisional flip**: delegate `max(2, exhaustion_tf − delegate_offset)` (floor=2),
  x-cross-r wob cross on the flip side → `flip_provisional`.
- **s30 finishing step** — the provisional is refined forward: wait for **s30r to r-pred the flip side**
  (`predict_breach` on the flip direction = the trigger the new leg is starting), then the FINAL
  **`flip_finisher`** fires at the next **flip-direction s30x×s30m cross while s30m is OOB (instant) and
  s30Mage is LATCHED-OOB** on the profitable (exhausted-leg) side (see principle below). This lands the
  flip at the true reversal, not the early exhaustion.
- **s30Mage latch:** the slow Mage sits OOB only intermittently at a reversal (e.g. 12_02 top: s30Mage>85
  at 03:23 and 03:32, not continuously) — so it **latches**: once it goes OOB on the profitable side (from
  the provisional onward) it stays set, and the s30m-OOB cross after the r-pred fires the flip. s30m stays
  instantaneous (fast supporting line at the cross); only s30Mage latches. SRP: m = instant position, Mage
  = latched confirmation.
- **Profitable-side positioning (0719, Joe's rule):** any line whose OOB position *supports* a flip must
  sit on the side that makes the flip most profitable = the **exhausted-leg side, NOT the flip direction.**
  A bullish flip is a bottom → the best long entry is at the low → the supporting momentum lines (s30m,
  s30Mage) sit **OOB-low (<LO)**, stretched into the down-leg they're reversing. (Bear flip = top →
  supporting lines OOB-high >HI.) The slow Mage lags the turn, so at the optimal flip it's maximally
  stretched into the exhausted leg. [measured 12_01: s30Mage is OOB-low through ~00:31, only reaches >HI
  at 01:02 = rally already run.] The r-pred trigger stays on the *flip direction* (it forecasts the new
  leg); only the OOB *position* gates flip to the exhausted-leg side. Earlier code gated the finishing on
  the flip-direction side (Mage>HI for a bull flip) → landed the flip at 01:02, ~31 min past the 00:31
  target.
- Flip = opposite of the confirmed bias.

## Knobs (all DB-sourced, `rpl_config` baseline)
boundary 85/15 · fence 65/35 · anti 50 · s2_tf 120 · delegate_offset 5 · wob_n 9 · div_net_min 3 ·
s1s2_confirm_tol_ms 240000 · **xcp_bnd_offset 4** (4-point rule) · **xcp_tf_floor 19** (look-back floor).
**latch_depth 5** · **latch_dwell 2** — s30Mage finishing latch filter (0719 sweep). depth = points beyond
the OOB boundary Mage must reach; dwell = consecutive 5s bars held past-depth (via `cross_wob`). Filters
lesser Mage excursions (the shallow 12_01 00:04:30 poke, s30M=12.6 = 2.4 below LO). Locked vs both flips:
12_01 → 07:55 (bottom), 12_02 → 03:30 (dwell=1 → 03:22); both = Joe's accepted reads. s30m stays instant.
Seam-carry (`carry_ms`) and velocity/smoothing (`vmin`) retired.
