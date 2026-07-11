# Finisher — the two-stage nof9

> [o9-live arm-delay spec](./README.md) · **causal / emerging-only**, every read via the jig.
> `jig.causal.fin_unlatch_6of9` · `lr_v2.fin_box_qualified` / `fin_unlatch_nof9`. Canonical detail:
> `../finisher_lookback_spec.md`.

Two responsibilities, two functions (SRP). Fixes the misunderstanding where the finisher was pinned to the
s3s4 gate instead of the arm unlatch.

## QUALIFIER — `fin_box_qualified`
Did BOTH `s15a` AND `s30a` qualify in the box `[arm-box_lb, arm+tol]`? Owns `box_lb = fin_lb = 42` (7×30s,
backward) / `tol = fin_fwd = 12` (2×30s, forward), DB-sourced (`lp_config`, `lr.py:53`). Validates a
(near-)immediate trade. **`gcs5a` is NOT in the qualifier** (Joe: gcs5a only preens the delay when fin_unlatch
qualifies — it is a component of the TRIGGER). The **back-lookback is load-bearing**: a finisher co-firing in
the moments *before* the arm still counts (19:42: the 20:20:05 co-fire is arm−2:25, inside the 7×30s window).
*(A harness bug counted `fin_lb` in 5s bars = 35s; fixed to pull `cfg.fin_lb`/`cfg.fin_fwd`.)*

## TRIGGER — `fin_unlatch_nof9`
Once qualified, the first bar at/after the arm where a **≥N-of-9** confluence binds within `bind_tol`. `N=6`
default. `bind_tol = 6` (1×30s) binds sets that don't breach on the same bar (Joe: needed because on 07-09 the
last gcs5a bar is 23:08:25 but `s30Mage` doesn't reverse until the bar after). Scans the arm's whole life to
the cancel — **no forward cap** (Joe: "wasn't I clear about caps?" — a `+tol+bind_tol=90s` disguised cap was
removed; removing it took the book from 2 trades to 5).

## The 9 = 3 sets {gcs5, s15, s30} × {mini-OOB, Mage-OOB, r-in-lookback}
`s2a` was replaced by `gcs5a` (the 5s clone of s15a). Two anchor modes:
- **`anchor='breach'` (DEFAULT):** conditions counted **INDEPENDENTLY, no Mage-reversed gate** — the 6of9 only
  needs the lines OOB, not the optimal price. The **r-in-lookback vote is gated on a line (r OR m OR Mage)
  actually breaching this bar** (Joe's exact wording), so r counts only when it genuinely breaches. Code:
  `line = roob | m | Moob; v = m + Moob + (rlb & line)`.
- **`anchor='oob'`** = the `a` definition (Mage-OOB AND Mage-reversed = 2, +1 if r in lookback). The
  Mage-reversed gate is the r-lookback anchor AND the optimal-entry price; it belongs to `s_qualify` (the entry
  finisher), not the trigger. Joe: "the 'a' logic requires Mage to reverse so we have 1) a common anchor for
  the r lookback and 2) the most optimal price."

**`gcs5` r_lb = 29** (5s bars = 145s; Joe: "I have gcs5r breaching at 23:08:25, so the long lookback isn't
necessary"). gcs5/s15 lines **READ from the DB** — a hand-built k-tuple silently malforms
(`../reference_line_cfg_tuple` equivalent). `gcs5M`/`s15M` overridden to `37|0.6|ohlc4` under eval; okayed for
`indicator_configs` but held (s15M 0.83→0.6 changes s15a for the gate path AND o9-live — blast radius) until
nof9 is proven.

## Worked example (0710)
Arm 13:55 SHORT. Breach-mode 6of9 hits exactly 6 at **14:01:35** (gcs5 3 + s15 2 + s30 1). Matches Joe's chart
read (`s30m:106, s15m:140, s15r:96, gcs5m:102, gcs5Mage:109, gcs5r:99`).

## The s15a requirement (ENTRY, load-bearing invariant)
The trade is ALWAYS placed on the NEXT same-side `s15a` at/after `max(arm, authorising-s30a)`, never on the
pre-arm co-fire. `lr_v2.py:495`: `next((k for k in range(max(i, j30), cap) if q15[k]), None)`.

## s15a definition — OPEN
`s_qualify = Mrev & m_OOB & (M_OOB | ¬fin_s30M_oob) & r_in_lb`. Live `fin_s30M_oob=1` REQUIRES the s15 Major
OOB; `=0` is mini-only. Which is intended is Joe's call.
