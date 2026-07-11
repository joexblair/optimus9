# Arm ladder — the hunt, the climb, the latch

> [o9-live arm-delay spec](./README.md) · **causal / emerging-only**, every read via the jig.
> Engine: `arm_walk.py` — `Board`, `walk`.

The delayed arm: an `s5m` breach opens permission to hunt; the ladder climbs through timeframes on each apex
`r` curl and arms when momentum stops climbing. Reward scales with how high the ladder climbs — **bigger TF,
bigger leg, bigger reward** — but the apex TF is deliberately **not stable**: it is whichever TF's momentum
carries the turn (TF6 on one top, TF19 on another, sometimes none). A turn is marked by *one* TF's `r`
crossing, and which one is unpredictable.

## Board — `arm_walk.Board`
Cached on the jig per `(tfs, es, tol, bands, wob)` — a per-hunt rebuild was the whole cost of a day's run.
Computes the emerging lines once: `s{tf}r/m/Mage`, `predict_set`, `mini_oob`, OOB masks, the `1/3-TF`
prediction seams (`pseam`), and the coarse curl sets (`curl`, seam = `TF·60 // curl_div`).

**Line configs the walk uses:** `s{tf}m = bb 7|0.50|ohlc4` emerging for every TF **except 5**; `s5m` = the DB
override `bb 8|0.65|ohlc4` (below); `s{tf}r = k 5|5|6|close`; `s{tf}Mage = bb 37|0.70|ohlc4`.

## Walk state machine — per 5s bar `k`, from the hunt bar `kh`
1. **Permission** — `permission=True`: an `s5m` 300s-seam reading on the wrong side kills the hunt (`s5m
   permission dropped`). Entry uses it; the TP disables it (`permission=False`).
2. **No-op until the apex `r` predicts** — tested ONLY at the apex's `1/3-TF` prediction seam (`pseam[apex]`;
   `s5r` = 300s → 100s seam). The walk-forward finds `s5r` predicted, then waits for its curl.
3. **Climb on the apex `r` curl** — at each apex-`r` coarse curl, test the TF above:
   `live = HTF r predicted(==es) OR HTF r OOB(es)` → climb (`sub=apex; apex=HTF`); else see `arm_mode`.
4. **Arm** — the two-stage latch (below), or top-of-ladder (apex is the last TF → arm there).

## `arm_mode` — the entry/TP asymmetry (deliberate)
- **`'latch'` (ENTRY, Joe 0710)** — ONLY the two-stage latch arms. An **htf-quiet curl is a no-op**: "no op,
  keep walking until you find a same-TF r, or cancel when all lines are IB" (Joe). The three htf-quiet losers
  all had NO `s5r` prediction and should have kept walking. `--allib` knobs the "cancel when all ladder r lines
  return IB after one breached" behaviour.
- **`'both'` (TP)** — latch OR **htf-quiet** arms, so a **fast single-TF reversal (s6 quiet) arms at the base
  TF5**. `'latch'` would never fire a TF5-only arm — that was the 19:42 exit miss. ⚠ The TP accepts an
  htf-quiet base curl that the entry rejects; intentional (fast reversals are s5-only) but the one place entry
  and TP diverge — flag if re-touched. See [take_profit](./take_profit.md).

## Two-stage latch (Joe 0710) — the arm trigger
Joe's definition: "a 2-stage latch, driven by separate `r` lines (TF and TF+1). When one reverses, stage 1 is
unlatched; when the other reverses, `armed=true`." A curl is an edge, so it can never coincide with another
TF's edge except by luck of the seam grid — **latch it**: once `s{n}r` curls against `es`, the TF is *held
reversed*; "in sync" becomes "held at the same bar."
- **Stage 1** — the first of the two coarse curls latches.
- **Stage 2** — the second one **arms**. **No expiry, no cancel** (Joe): "if they're both out, they MUST
  eventually reverse. If the second one takes longer (likely the higher of the two), then we've bought a trip
  over MAE and straight into MFE." (Proof: 20:25→21:12 armed MAE 0.00 / MFE 0.94, +0.217% in 5 min.)

Code (`walk`, `latch=True`): arm when `brc[apex]` and `brc[htf]` are both set AND each has a coarse curl in
`[breach, k]`. Emitted `latch TF{apex}+TF{htf}`. The `latch=False` `backstop TF{sub}+TF{apex}` branch is the
synced-curl variant (sub-apex and apex breach within 1 apex-TF-bar and curl together; `brc_tol`, `curl_tol`).

## Prediction-then-not-yet trap (why the latch exists)
A plain "arm when the TF above has no prediction" rule can't tell *"the TF above has nothing"* from *"the TF
above hasn't spoken yet."* On 06:01 it armed at TF8/05:48 when `s9r`'s first prediction was 05:51:40 — 3.5 min
into the not-yet window. The latch requires the HTF to have actually **breached and curled**, not merely be
silent.

## Stale-hunt hazard (open)
With the no-prediction cancel removed, the htf-quiet no-op is correct *within* a live move but wrong once the
move is over — a 2h15m-old hunt (07-08 21:00; 07-09 23:20→01:47:30) arms on a fresh unrelated TF6/TF7 pair.
Proposed bound: `s5m` returning IB for **N consecutive seams** (not one) — one knob, not yet adopted.

## No caps
The hunt/arm run to the arm or the cancel; no fixed horizon (Joe, verbatim). Window sizing is a fixed harness
margin (`TAPE_MARGIN_MIN=300`), not a knob; the forward bound is the tape end.

## s5m override — the ONE sanctioned hardcode
`arm_walk.py:42` — `S5M_OVERRIDE = ('bb', 8, 0.65, 'ohlc4')`, emerging, itf 300. Joe 0710: "I'm going to make
an exception to the hardcode rule. set your s5m to 8|0.65|ohlc4 in code and we'll firm it up in ic after a
full sweep." At 0.65 `s5m` is OOB at 46.4% of 300s seams (vs 69.9% at 0.40); the median OOB episode is 2 seams
(10 min) and 64.4% of consecutive episodes flip side — so with the permission-cancel the hunt dies at seam 2
before `s5r` predicts. **This is why the book runs cancel-on-opposite-breach, not the permission drop** — see
[arm_cancel](./arm_cancel.md).
