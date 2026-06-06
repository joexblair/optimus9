# cluster_scoring — design (r08 KPI)

**Status:** logical flow locked 2026-06-01. Awaiting first real grind (or_pk 58,
gcs5M geometry sweep) to validate against. Mechanism built
(`optimus9/analysis/cluster_scoring.py`); future-use tables + MAE auto-centre +
`run.py` subcommand still to wire.

---

## 1. Objective

Rank a grind's **centroids** by how much profit they bank **from genuine
swing-catches** — the combos that "often fire near the swing", where *near the
swing* means: a pk whose **entry value lets the trade pass through the swing's
peak to a profitable result without being stopped first.**

This is the **keeper-library selector**. It sits **downstream of the bny30 gate**
— it scores *gated* per-line signals (the gate has already removed the obvious
noise). Output feeds the per-line keeper libraries, which SnF later composes.

> Pipeline position: `gate (bnyM+bnyp) → conditions → per-line signals →
> [cluster_scoring picks keepers] → per-line libraries → SnF coalition`

`cluster_quality_score`'s earlier "more concentrated" framing is **dropped** —
what matters is firing near the swing, measured as banked profit.

---

## 2. Data artifacts (peeled from the firehose)

AM's canonical `pk_combo_summary` is the *aggregate* per combo (total / won /
stopped / avg_win%) and carries **no timestamps** — that's why it's O(combos).
The timestamps only live in the raw `pk_signals` firehose (~19M rows for a
13,440-combo grind). We do **not** want cluster_scoring (or SnF) re-querying that.

So when AM runs, it materialises just the **top-N centroids + their
`(ts, dir)`** into two small reusable tables:

| table | columns |
|---|---|
| `am_centroids` | `amc_pk, amc_or_pk, amc_rank, amc_n_signals, amc_<param>…` (full combo) |
| `am_centroid_signals` | `acs_amc_pk, acs_ts, acs_dir` |

`amc_rank` = AM's gross_banked rank (DD filter **off** — drawdown is a
portfolio-level concern, not a signal-grind gate, per r07; at 5s it would cull
every combo). This is the canonical "AM gives us the centroids" artifact —
persisted once, reused everywhere.

---

## 3. Logical flow

### S1 — Centroids + timestamps
Read top-N centroids and their signal timestamps from `am_centroids` /
`am_centroid_signals`. Load klines over `[min ts, max ts + horizon]`; map every
signal `ts` → bar index. `horizon` caps each outcome walk (default 3h of 5s bars
— both for speed and because a 5s entry unresolved after hours isn't the trade
we're crediting).

### S2 — Swing zones  *(reuse: `swing_detect` percentage ZigZag)*
Per `win`: `legs(find_pivots(close, win))`, keep `|amp_pct| ≥ win` → the
**significant swings**. Each carries `start`, `end` (the extreme), `dir`.
*Significance tracks `win`* — a swing must be ≥ win% to be bankable at win%.

### S3 — Score, per centroid × (win, stop) cell  *(reuse: `walk_to_first_cross`)*
Outcome of each signal: `walk_to_first_cross(win, stop)` → **win / stop /
undecided**.

A signal is **near a swing** when either:
- **PRE** — bar ∈ `[leg.start, leg.end]`, `dir == leg.dir` (fires during the
  swing, in its direction). **Uncapped** — a combo banking 3 entries on one swing
  scores 3× (consistent with the total-profit objective; twitchiness then exposes
  itself, see §6).
- **POST** — bar > `leg.end`, `dir == leg.dir`, entry within `stop` of the
  extreme, **first 2 only** (continuation right off the peak).

Two metrics:

- **`swing_capture`** = Σ realised win% over signals that are **near a swing AND
  walk-win**. Winners-only, always ≥ 0. This is "what it caught."
- **`total_net`** = net over **all** the centroid's signals (`+win / −stop / 0`).
  Off-swing and misfired losers drag it down (net, so volume can't game it). This
  is "what it cost overall" — the honesty check.

### S4 — Aggregate + rank
**Mean** each metric across the grid cells (a knife-edge `(win,stop)` winner
can't top the board — the gate-overfit lesson). Sort **`swing_capture` desc, then
`total_net` desc**. Persist `cluster_scores`.

---

## 4. Why `swing_capture` is winners-only (the reasoning)

- The spec's *"a value that allows the trade to pass through the peak without
  being stopped"* is, on real price, **identical** to *"the walk reaches +win
  before −stop."* There is no separate geometric test — the realised path **is**
  the test.
- So a near-swing fire either **passed through (win)** or **didn't (stop)**. The
  ones that didn't aren't swing-*catches* — they're misfires. Counting their
  −stop in `swing_capture` would blur *aimed near a swing* with *caught a swing*.
- The misfires aren't hidden — they're **drag in `total_net`**. The two columns
  cleanly split *what it caught* (`swing_capture` ≥ 0) from *what it cost*
  (`total_net`, signed).
- `swing_capture` therefore only ticks up when real swing profit is banked → trivial
  to read as "the profitable swingers." Undecided-within-horizon entries score 0
  in both (not a catch, not a realised loss).

`coverage` (fraction of swings caught) was considered and **dropped** — it
doesn't drive the sort, and the scalar % is the wrong shape for SnF, which will
want the per-swing *catch set* (a richer artifact), not a count.

---

## 5. The (win, stop) sweep

- `win` — a small grid (5s trades; full-size 0.9% rules may not apply).
- `stop` — **auto-centred** on the winners' MAE from the GoalAlignment report:
  the adverse-excursion distribution of eventual winners → `mean + k·σ` (with
  outlier trimming) = "how far underwater do winners actually go." The stop must
  sit just beyond that or it kills eventual winners. The grid brackets the centre.

Auto-pulling the centre keeps the stop *data-derived*, not guessed.

---

## 6. Output

`cluster_scores`, one row per centroid:

| col | meaning |
|---|---|
| `rank_n` | cluster rank (swing_capture primary, total_net secondary) |
| `am_rank` | AM's gross_banked rank (provenance) |
| `combo` | **full** centroid fingerprint, e.g. `8\|0.74\|hlcc4\|c5\|w33\|r6\|sf17\|m1` |
| `n_signals` | the centroid's signal count |
| `swing_capture` | banked swing-catch profit (≥ 0) |
| `total_net` | net P&L over all signals (signed) |

The `combo` fingerprint is the **deliverable** — the exact config to lock as a
keeper. Params are identity, never scoring inputs (the score is a pure function
of timestamps + price).

**Twitch detection (future):** a twitchy combo posts a wide `swing_capture` ↔
`total_net` gap — many in-zone wins inflate swing_capture while the misfires from the
same twitchiness sink total_net. A `fires_per_catch` flag can name it outright
later; uncapped PRE is what makes the fault visible.

---

## 7. Reuse map (SRP)

| need | existing |
|---|---|
| top-N centroids + signals | `AnalyzeManager.top_combo_signals` → materialised tables |
| swing detection | `swing_detect.find_pivots` / `legs` |
| win/stop outcome | `outcome_walker.walk_to_first_cross` |
| price window | `KlineLoader.load_window` |
| stop centre | new GoalAlignment winners-MAE method |

No new swing or outcome code; cluster_scoring is the overlay that composes them.

---

## 8. Build status

1. ✅ AM materialises `am_centroids` / `am_centroid_signals` (`materialize_centroids`).
2. ✅ GoalAlignment winners-MAE stop centre (`winner_mae_stop`, `mean+kσ`, trimmed,
   window-aligned). **Dispatched** — the stop grid *ceiling*, not gospel.
3. ✅ cluster_scoring reads the tables; full `combo` fingerprint; stop sweep spans
   **0.33 (manual floor) → winners-MAE centre**.
4. ✅ First 58 run (2026-06-01): KPI reorders AM's gross_banked rank — geometry
   matters. Keeper neighbourhood `len 32–34 / close / sf 15–18`; `total_net`
   uniformly negative (off-swing bleed ≈ 480 below `swing_capture`).
5. ✅ `run.py cluster_score --or_pk N` subcommand.
6. ✅ Renamed `swing_capture` → **`swing_capture`**; added **`capture_per_1k`**
   (efficiency, volume stripped) + **`win_pct`** (AM-comparable decided win rate) +
   `report()` (multi-lens table, best-by-lens, lens correlations).
7. ⬜ `run()` auto-materialises centroids on analyze (so they're pre-baked).
8. ⬜ **Conviction weight** (Joe's MAE idea) — see §9.

**Key finding (58, 2026-06-01) — there are only TWO axes.** `swing_capture`,
`win_pct`, `total_net`, `n_signals` all correlate 0.74–0.94 — they ride one
**volume/gross** axis (so `swing_capture`'s rank just echoes AM's gross_banked).
The ONLY orthogonal lens is **`capture_per_1k`** (efficiency), which correlates
**−0.4 to −0.8** with the rest — it's contrarian, and it favours the *selective*
combos (len 36/42/43, fewer signals) that the volume axis buries. This matches AM:
its **expectancy** (per-trade edge) likewise picks the low-volume combos, while its
gross_banked picks the high-volume ones. Win rate is ~uniform (~38%) → not a
differentiator. **Takeaway: efficiency is the real signal; the conviction weight
(§9) is what turns `swing_capture` from a volume echo into a quality metric.**

---

## 9. Behaviour by example (tests)

Test cases pin the metric definitions — prose is ambiguous, an example isn't.
Implemented cases live in `tests/`; the pending ones are the *spec* for the next
build. (Writing the cases first is what mapped the code — the in-zone-loser case
is what forced `swing_capture` to be winners-only.)

### `swing_capture` / `total_net` — `tests/test_cluster_scoring.py` ✅
- in-zone PRE winner + POST winner → both in `swing_capture` (Σ win%).
- in-zone entry that **lost** → excluded from `swing_capture`, still drags `total_net`.
- POST entry **outside** the stop band → excluded from near; counts in `total_net`.
- only the **first 2** POST continuation pks counted.
- no significant legs → no catches (near 0), `total_net` still nets all.

### `winner_mae` — `tests/test_winner_mae.py` ✅
- winner that dips then wins → records the dip %.
- never reaches +profit within horizon → `None` (not a winner).
- clean winner (never dips) → `0.0`. horizon caps detection.

### stop grid ✅
- spans manual floor (0.33) → winners-MAE centre, window-aligned.

### Conviction weight — ⬜ PENDING (next build; both options as spec)
**Anchor = swing-relative excursion**: how far past `leg.end` (the extreme) price
went before the trade won — NOT entry-relative MAE (Joe's manual stop is set
relative to the *swing*, not the entry). `R = 0.33 + x`.
- excursion 0 (won without breaching the extreme) → max weight.
- excursion < R → full weight (tiered) / headroom ≈ 1 (continuous).
- excursion = R → half (continuous `R/(R+exc)`) / boundary (tiered).
- excursion ≫ R (only survived on the loose stop) → low weight.

Two columns to score side-by-side, decide fold-vs-separate from 58 output:
- **(a) `swing_capture_w`** = Σ `win% · weight` — conviction-weighted profit (would
  replace `swing_capture` as primary).
- **(b) `conviction`** = mean weight over the combo's winners — `swing_capture` stays
  literal banked-$, conviction rides as its own column / secondary.
