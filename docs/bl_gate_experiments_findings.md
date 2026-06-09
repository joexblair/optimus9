# BL gate experiments — overnight findings (2026-06-09)

Autonomous run while Joe slept. Objective (Joe): **trades closest to the swings, with
the smallest qty** (⇒ least fees/slippage). "Won't get both — find the workable
balance." Plus: "pick and mix" the lines, and drop lines that overlap the bny gates.

All on the single 9-day window, gate fixed to **bny30M-only / -p-only / both / off**.
Line-states are gate-independent → precomputed once, re-evaluated per gate.

## 1. The four gate datasets

| mode | gate | n/day | stop med | best stop | cluster net (top) |
|---|---|---|---|---|---|
| **off**  | none | 144.7 | 1.770 | 1.622 | **−14.9** (bleeds) |
| **M**    | bny30M (BB) | **15.3** | 1.439 | 1.050 | +9.2 |
| **p**    | bny30p (K)  | 25.6 | 1.355 | 1.054 | +31.1 |
| **both** | M OR p | 33.8 | 1.417 | 1.151 | +17.5 |

**Findings:**
- **The gate is the lever, decisively.** Off fires 145/day and is **net-negative** —
  the ungated PK firehose catches swings but bleeds on off-swing entries. Any gate
  flips net positive and roughly halves-to-tenths the qty.
- **Counterintuitive but real: `both` admits MORE than either alone** (33.8 vs M 15.3
  / p 25.6). The mean-reversion gate keeps a fire where it *opposes* an OOB side;
  OR-folding M+p is OOB more often → more fires pass. So **M-only is the *most*
  selective**, landing nearest your ~10/day.
- bny30M-only (M) owns the ~10/day target zone; bny30p-only (p) wins on net/win-rate
  at higher qty.

## 2. Balance picks (top-42 candidates/mode, normalized low-qty + low-stop + high-efficiency)

| mode | combo | /day | stop | cap/1k | win% | net |
|---|---|---|---|---|---|---|
| p | 5,4,7,2,2,17,4,8 | 22.6 | 1.094 | 323.6 | 58.5 | 28.1 |
| **M** | 4,3,5,2,2,12,4,17 | **12.9** | 1.076 | 312.8 | 54.5 | 9.5 |
| M | 5,3,5,2,3,12,4,17 | 12.3 | 1.050 | 309.9 | 50.4 | 3.0 |

M = fewest trades nearest target; p = best win-rate/net if you'll take ~2× the qty.

## 3. Leave-N-out (gate-M, ref combo) — line roles

- **s30r is the qty ENGINE**: drop it → 12.8→**4.7**/day (and stop worsens). Highest
  gate overlap (30s line vs 30s gate).
- **s90b is the qty SUPPRESSOR**: drop it → 12.8→**19.1**/day. The two 30s lines do
  *opposite* jobs, so "drop the 30s pair" is not a clean win (→6.2/day, stop 1.43).
- **hs15r & s18b are proximity contributors** (dropping them worsens stop most).
- The full-8 consensus has the best proximity *at its own combo* — but a subset
  deserves its own combo (next section).

## 4. Pick-and-mix — per-subset frontier (gate-M, each re-ground on its own brackets)

| subset | best-stop combo | /day | **stop** | prof |
|---|---|---|---|---|
| full8 | 7,3,5,2,2,12,4,17 | 12.7 | 1.045 | 2.445 |
| drop_b6b | … | 14.0 | 1.034 | 2.462 |
| **slow4** (hb15b,hb9b,hs15r,hs9r) | **4,4,3,2** | **6.9** | **0.858** | 1.996 |
| slow4+s30r | … | 25.7 | 1.228 | 2.421 |
| prox_core | … | 38.9 | 1.149 | 2.354 |

### slow-4 looked like the winner — cluster scoring says it's a TRAP
- By `avg_stop` alone, gate-M + slow-4 is gorgeous: **0.858 stop @ 6.9/day**, the only
  sub-1.0 of the night, below the ~10/day target. Seductive.
- **But cluster validation kills it:** every slow-4 candidate is **win% 37–47% and
  net-NEGATIVE** (best: `2,7,3,2` cap/1k 267, **win 46.6%, net −3.1**). The tight
  adverse-excursion-to-swing does **not** translate to winning trades.
- **Lesson (and exactly why you wanted cluster on these): `avg_stop` ≠ profitability.**
  Geometric proximity to a swing and *catching* the swing over the 0.33–1.14 stop grid
  are different things, and slow-4 is where they diverge. The fast lines weren't just
  qty — their **consensus was selecting trades that actually win**. Dropping them
  tightened the geometry but gutted the win-rate.

### ★ The real objective-winners (validated positive-net)
| pick | /day | stop | **win%** | **net** | note |
|---|---|---|---|---|---|
| **gate-M full-8** `4,3,5,2,2,12,4,17` | **12.9** | 1.076 | **54.5** | **+9.5** | smallest qty at positive net — nearest ~10/day |
| **gate-p full-8** `5,4,7,2,2,17,4,8` | 22.6 | 1.094 | **58.5** | **+28.1** | best win/net, at ~2× the qty |

The honest pick-and-mix answer: the **gate** does the heavy lifting; the **full line
set** (consensus) is what makes entries *win*, not just sit near swings. Trimming
lines trades win-rate for tighter geometry — a bad trade once cluster-scored.

## 5. Caveats (holding the line on the stake)

- **Single 9-day window.** This is candidate selection, not robustness. The 0.858 must
  hold on the **26× 9-day leave-out windows** before we trust it. That's the next run.
- **Not tradeable P&L.** cluster net/win% use the swept 0.33–1.13 stop grid on swing
  geometry; no exit4/p-rev, no live fills. It says the structure leans right, not £.
- **stop 0.858 is avg adverse-excursion to the next swing**, not a live stop-loss.

## 6. Artifacts
- Code: `bl_gate_experiments.py` (4-mode driver), `leave_n_out.py`, `subset_regrind.py`,
  `slow4_validate.py`; gate parametrized in `gate_signal_sweep.py` (gate_bb/gate_k).
- Tables: `bl_group_results_{off,M,p,both}`, `gate_experiment_summary`, `cluster_scores`
  (last = slow4), centroids `am_centroids` or_pk 9001–9005.
- Fixed a latent bug: `run.py cmd_cluster_score` referenced `near_swing` (renamed to
  `swing_capture`) → KeyError on the success log line. Patched.

## 7. Recommended next steps
1. **Validate gate-M & gate-p full-8 across the 26 windows** (robustness — do win 54/58%
   + net hold out-of-sample?). This is the real candidate; slow-4 is discarded.
2. **Re-rank the pick-and-mix subsets by cluster win/net, not `avg_stop`.** The §4
   frontier used proximity, which we now know misleads (slow-4). Cluster-score
   drop_b6b / drop_s90b / etc. before trusting any subset. The likely truth: the full
   consensus wins; trimming costs win-rate.
3. **Decide the objective weighting.** "Closest to swings" must mean *profit-aware*
   (swing_capture/win%), not geometric `avg_stop` — slow-4 proves the difference.
   Confirm: minimise qty subject to net>0 & win>50%? Then M full-8 is today's pick.
4. **Sweep `bl_config`** (curl_floor, pseudo_cross, bb_pad, exit2_ref) — your hint; the
   machine-tuning axis is untested and may lift win-rate at low qty (where M sits).
5. Then targeting/K-of-N + p-rev/exit4 once the gate × line-set is locked.

## 8. The meta-lesson
The brightest single-metric result (slow-4's 0.858 stop) was the wrong answer. Only the
second metric (cluster win/net) revealed it. Same shape as the phantom-0.59 catch:
**a seductive number is a hypothesis, not a finding, until a second independent lens
confirms it.** The gate-M/p picks are reported *because* two lenses agree on them.
