# Finisher lookback on arm unlatch — spec (#53, Joe 0704)

**CANONICAL. This is the ONE spec for `fin_unlatch`.** Any other doc that describes its behaviour is a
pointer here, not a second source of truth.

## The s15a requirement (the load-bearing invariant, Joe 0710)
**The trade is ALWAYS placed on the NEXT same-side s15a — never on the pre-arm co-fire.** The proximal
box only *authorises*; the entry bar is `next q15 at/after max(arm, authorising-s30a)`. This is not
optional and not a tolerance: the pre-arm s15a that completed the setup is evidence the setup is live,
but the entry waits for a fresh same-side s15a.
- Confirmed in prod: `lr_v2.py:495` — `return next((k for k in range(max(i, j30), cap) if q15[k]), None)`.
- Worked example (0710): arm `07-09 23:07:30` SHORT. Setup complete at `23:04:25` (s15a+s30a co-fire, 3 min
  before the arm). Entry is NOT there — it is the next same-side s15a at/after the arm.

## Box units — 30s bars, not 5s
`fin_lb = 42` five-second bars = **7×30s**; `fin_fwd = 12` = **2×30s**. Engine default `lr.py:53`,
DB-sourced `lp_config`. A tool that passes `7`/`2` raw is reading 5s bars (35s/10s) and is WRONG — pull
from `cfg.fin_lb`/`cfg.fin_fwd`, never hardcode.

## fin_unlatch_6of9 — the two-stage nof9 variant (Joe 0710)
The s15a-trigger is replaced by a two-stage entry for the arm-delay build. Two responsibilities, two
functions (SRP):

- **QUALIFIER `fin_box_qualified`** — did BOTH s15a AND s30a qualify in the box `[arm-box_lb, arm+tol]`?
  Owns `box_lb` (7×30s) / `tol` (2×30s). gcs5a is NOT part of the qualifier. Validates a (near-)immediate
  trade.
- **TRIGGER `fin_unlatch_nof9` (anchor='breach', DEFAULT)** — once qualified, the entry is the first bar
  at/after the arm where a `>=N-of-9` confluence binds. The 9 = **3 sets {gcs5, s15, s30} × {mini-OOB,
  Mage-OOB, r-in-lookback}, counted INDEPENDENTLY**. NO Mage-reversed gate — the 6of9 only needs the lines
  OOB, not the optimal price (that is the 'a' finisher's job). The r-in-lookback vote is **gated on a line
  (r OR m OR Mage) actually breaching this bar**, so r counts only when it genuinely breaches. `bind_tol`
  (1×30s) binds the sets when they don't breach on the same bar. The trigger scans the arm's WHOLE life to
  the cancel — **no forward cap**.
- **anchor='oob'** = the 'a' definition (Mage-OOB AND Mage-reversed = 2, +1 if r in lookback). The
  Mage-reversed gate is the r-lookback anchor AND the optimal entry price; it belongs to `s_qualify` (the
  entry finisher), not the 6of9 trigger.
- gcs5 r_lb = **29** (5s bars). gcs5/s15 lines READ from the DB — never hand-build a k-tuple.
- Worked example (0710): arm `07-10 13:55` SHORT. Breach-mode 6of9 hits exactly 6 at `14:01:35`
  (gcs5 3 + s15 2 + s30 1). Matches Joe's chart read.

## OPEN
- **The s15a *definition* for `fin_unlatch`.** `s_qualify` = `Mrev & m_OOB & (M_OOB | ¬fin_s30M_oob) &
  r_in_lb`. Live `fin_s30M_oob = 1` REQUIRES the s15 Major OOB. Which is intended is Joe's call.
- **The arm cancel.** A single opposite-side s5m breach cancels the arm. On `07-10 13:55` that fires at
  `14:00:00`, 95 s before the 6of9 confluence at `14:01:35`, so the arm dies before its setup completes.
  Whether one opposite breach is a real cancel or a twitch the arm should survive — Joe's call.

---

Fixes the misunderstanding where the finisher check was pinned to the **s3s4 gate** instead of the
**arm unlatch**, so late-qualifying finishers were missed (the 09:34 LONG episode never traded).

## Label glossary (0704)
- **finisher lookback on arm unlatch** — the check that hunts for qualified finishers (s15a + s30a). *(was "finisher window")*
- **arm-delay-s7r** — the arm-delay mechanism; the big-leg condition is gated on s7r. *(was "arm-delay")*
- **s3s4 gate** — the arm→gate lifecycle gate (opens via path a/b/c off s3/s4). *(was "gate")*
- **arm unlatch** — the s5Mage reversal that releases the delayed arm (the arm-delay-s7r re-time bar).

## BRD (Joe, verbatim)
> Because the qualifiers that create a trade (the "finishers") might qualify in the moments before the arm
> is unlatched, we look back 7 bars to hunt for that qualification. If we find the qualifiers in a qualified
> state, inside the 7×30s bars prior to arm unlatch, then we place a trade on the **next same-side s15a**.

## Flow (the fix — replaces the single gate-pinned box)
1. **Arm unlatch** fires (the s5Mage reversal / arm-delay-s7r re-time bar).
2. **Proximal check** — look **back 7×30s** from the unlatch: are **s15a AND s30a** both in a qualified state?
3. **If yes → place the trade on the NEXT same-side s15a.** *(the s15a is the trade-placement mechanism, not optional.)*
4. **If no → proceed to s3s4 gate testing** → if the s3s4 gate opens, the finishers get **a chance** (NO time
   limit) to qualify → **place the trade on the NEXT same-side s15a** when they do. The chance runs until the
   **arm cancels**.

The trade is **always** placed on the next same-side s15a (both the proximal path and the gate path).

## Arm cancel (resolved: option a, Joe 0704)
- The arm cancels on an **opposite-side s5m breach** — a hi-breach cancels a long arm (from a lo-breach), and vice-versa.
- This is the sole time-limit on the gate-path chance (step 4): the finishers can qualify any time until the opposite breach.
- Build: `v2_arm` cap = `min(opposite-side-s5m-breach, i + horizon)` — the opposite breach cancels; the 1.5h
  **horizon stays as a backstop** for now (full horizon removal per the spec is a *separate* change, not this build).

## Knobs (DB-sourced, lp_config)
- **arm_wob** (=2) — s5Mage reversal wobslay for the arm unlatch. Higher → unlatch lands later / on the truer swing.
- **fin_lb** (=7×30s) / **fin_fwd** (=2×30s) — **belong ONLY to the finisher lookback on arm unlatch** (step 2):
  the proximal box is `[unlatch − fin_lb, unlatch + fin_fwd]`. `fin_fwd` is that check's late-line tolerance —
  it does NOT bound the step-4 gate-path chance (which has no time limit; see Arm cancel).

## Sweep
- **2-D combo: `arm_wob` × `fin_fwd`**, across the **full set of windows** (worst-window minimax). They overlap
  (both bridge the unlatch→swing gap) → sweep together, not two 1-D sweeps.

## Current-code divergence (finisher_v2 today)
- Anchor: **s3s4 gate**, not the **arm unlatch**.
- Shape: a box `[gate−fin_lb, gate+fin_fwd]` requiring both finishers inside — vs the BRD's **back-lookback at
  the unlatch** + **forward chance after the gate**, firing on the next same-side s15a.
- Trigger: a **gcs5M reversal** after Q1 — vs the BRD's **next same-side s15a**.

**RESOLVED for the trigger (0710):** `fin_unlatch` (`lr_v2.py:477`) now fires on the **next same-side s15a**
at/after `max(arm, authorising-s30a)` — the BRD trigger, the gcs5M reversal is gone. The remaining
divergence is the ANCHOR: `fin_gate` uses the s3s4 gate (forward-only), `fin_unlatch` uses the arm bar with
the proximal back-lookback. Both are exposed as `--producer` in `arm_trade.py`; the arm-delay book
currently runs `gate`.

Related: [[project_o9live_forward_live]] · the r_lb TF-bar fix (commit 81293a6) already lets the finishers
qualify properly, so this episode now trades via the proximal path — re-scope during the build.
