# Breaching-Line machine — Business Requirements (reverse-engineered)

**Status:** Draft for review · 2026-06-09 · reverse-engineered from
`breaching_line.py` + `bl_detect.py` against `bl_machine_design.md` and the xlsx
(`260511 trend machine.xlsx`, Sheet1 "BL exit options"). Purpose: state what the
machine *requires* of its lines/supports so the 8-line group's support model is a
deliberate design, not an artifact of the hb9 single-line slice.

This is a BRD (what + why), not an implementation plan. Where today's code and the
intended vision diverge, that's called out in §6 for the review chat — not silently
encoded.

> **ACTIONED (2026-06-13).** The support model (BR-A…D) is implemented (commit `9b066ce`):
> prediction sources from the set, exits bind to the breach via `bl_lines.bl_support_ic_pk`
> (+ `bl_exit3_support_ic_pk`). §5/§6/§8 are now the historical rationale. The **machine
> mechanism** is in `bl_machine_design.md`; the **live** support config is `bl_lines` (this
> doc's §7 table is a dated snapshot — verify against the DB). ⚠ `prediction_anchor` rename
> (BR-D) did NOT land — the code uses `predictor_min`/`predictor_maj`.

---

## 1. Purpose

- The BL machine watches one HTF "breaching line" (a K line) leave and return to
  the 85/15 boundary, emitting a 4-state journey (idle→breached→curled→complete).
- The collective of these journeys is the entry gate: closed while **any** line is
  mid-journey, open only when **all** are idle/complete. It is `bny30` inverted —
  the entry-quality lever meant to pull the data stop (~0.68) toward 0.33.
- A breach line cannot run alone: it needs **support line(s)** that drive its
  prediction and its exits. The support model is the subject of this BRD.

## 2. Actors / inputs (per breach line)

- **K line** (`k`) — the breaching line itself; per-5s, emerging/lookahead values.
- **Predictor BBs** — the set's mini + Major BB (`predictor_min_bb` /
  `predictor_maj_bb`), driving the `prediction_anchor` (§5, BR-B).
- **Exit support BB(s)** — the BB(s) bound to this breach in bl_lines, driving the
  exits (§5, BR-A/C). Distinct concern from prediction.
- **Cycle seams** — TF-boundary markers for the exit2 anchor.
- **Tuning** (one active `bl_config` row): curl floor/lookback, exit lookback,
  pseudo-cross proximity, grace, exit2 ref, **exit_mask** (which exits are live),
  bb_pad, the 85/15 boundary + 70/30 fence.

## 3. Functional requirements — the state machine

- **FR-1 Engage band.** A line inside the 70:30 fence is dormant (state 0). Engage
  only outside it: `[15–30]/[70–85]` predict, beyond `15/85` breached.
- **FR-2 Breach (0→1).** K crosses 85/15, **or** is predicted to (FR-6), and a
  *fresh* engagement (an IB→OOB crossing or a fresh prediction), not a pegged line.
- **FR-3 Curl (1→2), mandatory.** K's ROC reverses past the curl floor while OOB.
  No skipping 2; exit1 is the sole bypass (FR-5a).
- **FR-4 Complete (2→3).** Any enabled exit method fires (§5).
- **FR-5 Re-arm / reset.** 2→1 re-breach (bobbing); 3→1 re-pull while completing;
  3→0 reset (single-line: next bar; multi-line gate-hold parked).
- **FR-6 Prediction.** K is predicted to breach when the BB anchor overshoots the
  boundary by more than K falls short: `anchor=max(m,M)` (hi) / `min(m,M)` (lo),
  anchor OOB, `(anchor−HI) > (HI−k)`. Uses **both** support lines.

## 4. Functional requirements — exit methods

From state 2 (or same-bar via FR-5a), complete on any **enabled** exit:

- **FR-5a exit1 — OOB→IB.** The exit BB was OOB within `exit_lookback` and is now
  IB. *Bypasses the curl* (can fire same bar as the breach).
- **FR-5b exit2 — K reverses past its pre-breach anchor.** K crosses back past the
  K-line value one seam before the breach extreme. A clean line-turn, BB-independent.
  Requires the curl.
- **FR-5c exit3 — BB×K toward IB.** The exit BB cuts through K heading in-boundary
  (real cross, or pseudo-cross when within `pseudo_cross` and converging). Requires
  the curl (or the grace window after an early exit3).

Per-line `exit_mask` selects which of 1/2/3 are live (exit4/p-rev parked).

## 5. The real root — prediction-BBs and exit-BBs are conflated

`m`/`M` are BB suffixes (mini / Major), **intrinsic to every indicator set** — not
bl_lines concepts. Two genuinely separate concerns got tangled into one BB pair:

| concern | should source from | today sources from |
|---|---|---|
| **prediction** (the min/max-OOB formula) | the set's mini+Major BBs | bl_lines support rows |
| **exits** (exit1 OOB→IB, exit3 BB×K) | the BB named in the xlsx exit def | the same bl_lines rows |

**Two separate bugs, both confirmed against the live DB:**
1. **Over-seeding.** `seed_bl_lines.py:99-100` roles *every* BB line `support`, so
   bl_lines carries 16 active support BBs when only **8** are named in the xls. The
   support BBs are meant to be *hand-picked* per the xls exit defs, not dumped. →
   remove any bl_lines row not specifically called out in the xls.
2. **Prediction reads bl_lines.** `_load_families` sources `bb_m`/`bb_M` from those
   bl_lines support rows (by suffix) and `run()` feeds them to prediction. Prediction
   should source its mini+Major from the *set*; reading bl_lines is the bug that let
   the C-1 collision corrupt prediction.

Consequences, re-read through the split:

- **C-1 (collision).** `_load_families` resolves supports by **series (`ic_is_pk`) +
  suffix**. With >1 breach per series every breach pulls the same set. It corrupted
  *both* prediction and exits *only because prediction lived in bl_lines*. Source
  prediction from the set and bind exit-supports to the breach → collision gone.
- **C-3 (exit3 ≠ exit1 BB).** Survives, but now purely in the exit-support layer:
  hb15b's exit3 reads `hb9M` while exit1/2 read `hb15M`.
- ~~C-2 (single-BB family)~~ **dropped** — my Sheet2 misread. Every set has both BBs;
  the missing ones are now seeded in `ic`.

## 6. Requirements for the 8-line group

- **BR-A — exit supports bind to the breach.** A bl_lines `support` row links to its
  breach explicitly (`bl_support_of` → the breach's `bl_pk`), replacing series+suffix
  resolution. A BB in bl_lines as `support` ⇒ it supports the **exits**, nothing else.
  Fixes C-1.
- **BR-B — prediction sources from the set, not bl_lines.** `_load_families` resolves
  `predictor_min_bb` / `predictor_maj_bb` from the breach's own indicator set (same
  series prefix + label, suffix m / M, type bb). The m/M BBs need **not** be seeded as
  bl_lines rows at all. The derived value is renamed **`prediction_anchor`** (PK-
  aligned, for the coming PK↔BL link).
- **BR-C — exit3 may name a different support.** A breach's exit3 can read a support
  distinct from exit1 (hb15b). The `run()` exit input becomes
  `{exit_support, exit3_support?}` rather than the single `bb_M`. *The one true
  machine change* — everything else is wiring + rename.
- **BR-D — rename for clarity + the PK future.** `bb_m`/`bb_M` → `predictor_min_bb`/
  `predictor_maj_bb` (prediction inputs); a separate `exit_support` (+ optional
  `exit3_support`) input for the exits; derived `prediction_anchor`.

## 7. The 8 active breaches — sourced two ways (post-corrections)

All K-type. Prediction = the set's mini+Major (BR-B). Exit support = the xlsx-named
BB bound in bl_lines (BR-A). b6p dropped; b6b/s30r per Joe's 2026-06-09 corrections.

| breach | predictor (set m / M) | exit support | exit3 override |
|---|---|---|---|
| s90b | s90m / s90M | **s90m** (mini!) | — |
| hb9b | hb9m / hb9M | hb9M | — |
| hs9r | hs9m / hs9M | hs9m | — |
| hs15r | hs15m / hs15M | hs15m | — |
| s18b | s18m / s18M | s18m | — |
| b6b | b6m / b6M | b6M | — |
| s30r | s30m / s30M | **s30m** (mini) | — |
| hb15b | hb15m / hb15M | hb15M | **hb9M** |

*Verified against live `bl_lines` 2026-06-13.* Note the exit support is **independent of the
M/m letter** and of prediction — **most are minis** now (s30r, s90b, hs9r, hs15r, s18b);
only hb9b/b6b/hb15b use the Major. It must be named explicitly per breach.

## 8. Open questions for review

1. **BR-C staging.** Build the exit3-override *data model* now (record hb9M as
   hb15b's exit3 support, truthfully), and land the `run()` exit3-input change as its
   own small, tested step? Or approximate hb15b (hb15M for all 3 / exit3 masked) to
   move the baseline grind now?
2. **hb15M vs hb15m.** Sheet2 lists only `hb15m` (len13, 0.68); the exit text writes
   `hb15M`. Same line, or a distinct Major you've now seeded?
3. **Type-agnostic exits (Joe principle).** BL must not see a line's type. Each exit
   reads a line *value*; the type-specific calc happens upstream in the computer.
   - exit2 reads the **breach line's own** value reversing past its pre-breach anchor.
   - exit1/exit3 read a **support** value (OOB→IB / cross). In practice supports are
     BBs so far, but `run()` must accept any value array — no K/BB branching inside.
   *Resolved by the model; recorded so the refactor enforces it.*
4. **prediction pairs.** Joe seeded the missing m/M in `ic` (incl. hb15M) — all sets
   now covered. BR-B can assume a complete mini+Major pair per active breach. ✓
