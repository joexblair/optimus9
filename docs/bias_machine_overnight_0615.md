# Bias machine — overnight findings (night of 0614→0615)

Built the gravity-scan foundation (#4) and 3D'd outward while you slept. Headline
synthesis first, then the data, then the open threads.

## THE synthesis (the one that ties it together)

**M's alignment vs the m+r breach decides trend-vs-reversal.** Two mutually-
exclusive setups, opposite trades, both with an edge in the tape:

| setup | M vs the m+r breach | behaviour | direction | hit |
|-------|---------------------|-----------|-----------|-----|
| **GRAVITY** (your rule) | M on the OPPOSITE side of 50 (divergent) | price reverts toward M | counter-breach | ~67% w/ shallow-M filter |
| **EXHAUSTION** (my probe) | all lines incl. M same side (aligned) | trend continues | with-breach | ~65% short-lived |

So gravity and exhaustion never fire on the same bar — the M line's position **is**
the discriminator. Divergence = reversal. Alignment = trend. This is why "all lines
OOB" is NOT a PK (see below).

## 1. Foundation — VALIDATED against your TV prints

Spot-checked s2/s6/s22 (m/M/r) vs your three readings. Two things locked:
- **Native value = the just-closed bar, read at its close boundary (HH:MM:00).** Not
  `:55`. The value steps exactly at the bar close; reading mid-bar gives the still-
  forming bar. (s6 @ 12:24 matches TV to the decimal on all three lines.)
- **HTF lines need DEEP warmup (160h+)** or the RSI/STC under-converge. s2 had
  thousands of warmup bars and matched; s22 with only ~105 bars read 7–22 off until
  warmup deepened. First-class config for any backtest window (live = non-issue).
- **m (bb10/0.40/hlc3) and r (k5/6/6/hl2) match TV to the decimal.**

## 2. PARKED for you — the M line

M (bb37/0.72/ohlc4) reads **+8 to +12 high on s2 and s22, but PERFECT on s6**. Not
warmup (s2 has 4800 bars), not a uniform mult error (that would break s6). Something
TF-specific about the BB37 config. Needs your eye — config? source? a TV-side quirk
on the 37-period band? All scans below use M as-is, so the M-depth numbers may shift
once this is resolved.

## 3. CORRECTION absorbed — s18 = TF6

s18 is **TF6 (360s/6-min) blown up ×3 lengths**, not 18-min native — same
itf-seconds-vs-label quirk as the existing s18 (s18b = K 12/66/147/close, s18m =
BB 51/0.83/hl2). TF map now: **s2/s6/s9/s22 native; s18 (TF6×3) and s14 (TF7×2) are
blown-up emulations; s30 the only emerging line.**

## 4. GRAVITY scan — the shallow-M edge (robust)

Rule as given (M opposite 50, grabbed at the s6m wobble_slayer), episode-gated, over
96h then 168h. The bare rule is coin-flip (~55%). The edge is entirely in **M-depth**:

| |M−50| bucket | hit (h30) | median | fav/adv |
|--------------|-----------|--------|---------|
| **< 10 (shallow, just past 50)** | **67–78%** | +0.4 to +0.8% | 1.1 / 0.4 |
| 10–20 | ~50% | −0.2% | 0.9 / 0.5 |
| ≥ 20 (deep, near OOB boundary) | **0%** (0/3) | −0.8% | — |

**This challenges your "M near the boundary" phrasing.** If "boundary" = the 85/15
OOB edge, those are the depth≥20 cases that LOST every time. The live signal is **M
just across 50** (within ~10), not M pinned near the OOB edge. Monotonic and stable
across both windows. LO-longs also ran cleaner than HI-shorts (adv 0.16 vs 0.86) but
n is small — likely regime.

## 5. EXHAUSTION probe — "all lines OOB" is a TREND, not a PK

Tested "all 4 TF m-lines OOB same side → reversal" (359 events). **Reversal bet loses:
hit 32/36/44%, adverse double favorable.** So multi-TF alignment *continues* the trend
(~65%, 2:1) — it does NOT mark a top/bottom. The naive "everything's oversold, fade
it" is a trap here.

→ **Therefore the PK is NOT "all lines OOB."** Both your test PKs (bearish 0448,
bullish 1652) sit at full multi-TF exhaustion — but so do 359 non-reversals. The PK is
the *rare* reversal inside a persistent trend, and the discriminator must be the
**divergence** (s22r line-slope vs price-slope — exactly the `_states_standard`
p_c:9/p_r:4 you want wired), not the alignment. s22r is the lagging IB line at both
PKs (77.4 / 47.6) while everything else is OOB — it's the right line to watch.

## 6. Your requested test cases — logged

- **42 s22r lift cases** (OOB→IB transitions) over the window — in the probe output.
- PK #1 bearish 0448: every m-line HI-OOB across s2/s6/s9/s22; M HI on s6/s9/s22.
- PK #2 bullish 1652: mirror — every m-line LO-OOB; M LO.

## Open threads for the morning (pick any)

1. **M line** — resolve the +8/+12 on s2/s22 (§2). Gates clean M-depth numbers.
2. **Wire the divergence** — `_states_standard(s22r, dema, p_c:9, p_r:4)` needs the
   DEMA price proxy you flagged as "test it." That's the PK trigger, and §5 says it's
   the missing discriminator. Need to pick the proxy + spot-check vs your 0448/1652 PKs.
3. **Gravity: lock M-depth<10 as a filter?** Re-run once M is fixed; check it survives.
4. **Continuation edge** (§5) — a bonus, opposite trade. Worth its own scan? It maps to
   your "pyramid along the bias line + take-money-and-run" better than the reversal does.
5. **s18/s2 as 3D context** on the gravity setups (deferred — centered on validated s6).

## 7. 3D table — what separates reversals from the field (0615, post-clarification)

Mapped every HTF line (s6/s9/s22 × m/M/r, side-normalised breach-dev, @prev + pool
floater) for the exhaustion field, then re-cut the universe to **p-rev moments**
(s30m reversing inside an s22m breach) per Joe's steer.

- **M fix:** s2M/s22M → mult 0.83 (s2M now exact vs TV); s6M stays 0.72. **s22M still
  +10 high at every warmup depth → genuine config mismatch, not warmup. Parked.**
- **Exhaustion universe (all-m-OOB):** static config barely separates reversals from
  continuations (all Δ ≤7 breach-dev). Best lever = s22m depth: shallow/just-OOB →
  45% reverse, deep → 29%. Both controls look like ordinary exhaustion configs.
- **p-rev universe (s30m turn inside s22m breach):** base reversal rate 36%→**40%**.
  Discriminator **flipped to M-ALIGNMENT** — reversals have M-lines deeper on the
  breach side (s9M +7.1, s6M +4.1 clean-line corroborated; s22M aligned → 47%, +8).
  The controls' "gravitating r" does NOT generalise (r-grav lift −3) — n=2 fluke.
- **Open contradiction:** gravity wants M *divergent* (shallow/opposite 50); p-rev
  wants M *aligned* (deep/same side). Two opposite M conditions — real two-setup
  split, or one's an artifact? TBD.
- **Caveat:** p-rev universe is too granular (4968 events; 19 within ±10min of each
  control — s30m micro-wiggles around the boundary). Needs a turn-magnitude filter
  (deep peak + minimum roll-over) to isolate real p-revs. Next step.
- Files: `bias_3d_table.py` + `bias_3d_table.csv` (358 exhaustion / 4968 p-rev rows).

## Where it lives
- `/home/joe/thecodes/bias_gravity_scan.py` — foundation (config TABLES) + gravity scan.
- `/home/joe/thecodes/bias_moment_probe.py` — PK-moment dump + s22r-lift scan.
- Nothing committed; no production code touched. All exploratory, in `thecodes/`.
