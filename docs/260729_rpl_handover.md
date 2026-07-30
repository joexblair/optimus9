# 260729 RPL handover — start here, no warm-up needed

**Read `docs/bp50.md` §1 (Joe's verbatim spec) and §13 (the external check) before touching anything.**
This doc is the fast path: what state everything is in, the one live finding that isn't written up yet,
and the last ten exchanges verbatim so the thread is recoverable.

---

## 0. START WORK IN THREE STEPS

1. ~~Write up the 95.7% finding~~ — **DONE, and it was withdrawn on write-up.** It is now `bp50.md` **§14**:
   it reproduces (201/207, TF gap med 18) but sits *below* its own null, because the candidate pool is a
   median 347 markers per leg across 57 lower TFs. Read §14 before re-opening this thread. §3 below is kept
   only as the record of what was claimed.
2. **Task #7** — branch 1 fires 2 of 208. Cause is in `bp50.md` §1 (seeding on the highest *participating*
   TF lands high, so leg b wins the race), **not** the 95.7% finding, which no longer supports it.
3. Then re-measure §13.1 before building the delegate (task #5). Do not build the delegate on exhaustions
   that land mid-swing.

```bash
PYTHONPATH=. python3 build_exhaust.py   --ceiling 120 --persist   # rpl_exhaust,     ~6 min
PYTHONPATH=. python3 build_rplwalk2.py  --applied   --persist     # rpl_exh_applied, ~4 min
```
Both rebuild a **research-only** cache at TF ceiling 120 (`rpl_config.tf_ceiling` stays 90 — `R.TFS` is
reassigned at runtime). First run of either takes ~6 min because TFs 91–120 must be computed.

## 1. HARD CONSTRAINTS — violating these has already cost a day

| rule | why |
|---|---|
| **Data before 05-18 is SYNTHETIC** | warmup only, never analysis. `build_exhaust.ANALYSIS_START` enforces it. Every §12 result predates this and is VOID. |
| **RPL starts at TF22** | below is s4Mage + s15/s22. `build_exhaust.RPL_FLOOR = 22`. The delegate may go lower; the ladder may not. |
| **NEVER apply a cap** | no horizon/window/truncation in code OR diagnostics unless Joe specifies it. The one legitimate terminator is the spec'd unlatch `B.cap_of` (hs60x opposing breach). |
| **GATED — do not edit** | `optimus9/orchestration/rpl_walk.py`, `build_past50.py`, `build_rpl_6of9.py`, `rpl_config`, `rpl_micro`. Untouched all session. |
| **Paste content into messages** | Joe cannot see tool output. Referring to "the query above" when it was in a heredoc has failed twice. |
| **cross_wob lags 40s** | it confirms after `wob_n`=9 bars and the consumer takes the rising edge, so the confirmed bar is always 8 bars after the real crossing. Read line values at the RAW bar; a live system can only act at the CONFIRMED bar. Both are stored everywhere. |

## 2. THE MECHANIC AS BUILT

**Ladder** — seed by a one-bar top-down scan at the s15/s22 handoff for the highest *participating*
(r-pred OR OOB) TF; above the seed the **contiguous** rule governs (climb to T only if every TF in
(seed, T] participates). Monotonic up. Causal: the scan reads nothing past the handoff bar and skips no
quiet TF during a climb.

**Exhaustion marker** — three-way race on `current_tf`:
- **leg r** — x crosses r, gated: r OOB but **NOT established**, i.e. dwell < ¼ seam (`TF×15` s)
- **leg M** — x crosses Mage, same gate
- **leg b** — x crosses the boundary, **unconditional**

Race key = **x's own OOB episode** on that TF, shared by all three legs.

> **The direction that is easy to get backwards** (I did): r OOB and *holding* past the ¼ seam →
> **CONTINUATION**, climb higher. r OOB and x crossing back *inside* the window → **EXHAUSTION**. r is a
> lagging line; a cross inside the window means x turned before r finished registering the move, so r
> arrives reporting a condition x has already left.

**Tables** (all real-window, 05-18 → 06-13):

| table | rows | what |
|---|---|---|
| `rpl_exhaust` | 170,239 | per-TF candidate pool, TF22–120, both biases |
| `rpl_exh_applied` | 208 | markers where TF == `current_tf`, stable across the 40 s lag |
| `rpl_exh_pivot` | 207 | each applied event joined to its swing_detect(2%) leg |

## 3. ~~THE LIVE FINDING~~ — WITHDRAWN. Superseded by `bp50.md` §14. Kept as the record of the claim.

> **Retracted 0729 on write-up.** The 95.7% reproduces but does not beat its null: with a median 347
> candidate markers per leg across 57 distinct lower TFs, a uniform scatter of the same size gives best
> position 0.998 and "a lower TF sat nearer" 100.0%, against the observed 0.960 / 97.1%. The winning TF is
> also unstable (range 22→119). The consequences listed below lose their support from this measurement.
> Full working in `bp50.md` §14.

Joe's target: *"land exhaustion bars just before swing_detect(2%) pivots."* First external check (§13):
exhaustions land at **median position 0.50** in their swing leg, direction correct **40.5%** vs a **49.2%**
random baseline. Not early, not late, not inverted — unrelated.

**Then Joe's hunch, which cracked it:**

```
  applied events with a lower-TF marker in the same leg   207
  a lower TF sat NEARER the pivot                         198  (95.7%)
  position: fired 0.46  ->  best available 0.96
  TF gap (fired minus better):  med 18   p25 5   p75 41
```

**The signal is not missing — the selection is wrong.** In 95.7% of cases a marker on a TF ~18 rungs lower
was already sitting essentially on the pivot (0.96), and the seed walked past it.

Consequences:
- Explains **task #7**: the seed lands high, so leg b wins and branch 1 never fires. One cause, two symptoms.
- Connects to Joe's **TF-band** idea (roots 30/60/90) and his benched **leapfrog** — a p25 gap of 5 and
  median 18 is band-sized, not one rung.
- **The old engine's `xpred_band` did this**, and I dismissed it as "a different mechanic". It measures
  better on this test than what replaced it. Be slower to write it off.
- Candidate: **seed and exhaustion TF should be different things** — seed high to establish the walk, take
  the exhaustion from the band below.

**Bound on all of §13:** leg b is 205 of 208, so this measured boundary crosses on the seeded TF, not the
¼-seam exhaustion. Branch 1 fired twice. #7 first.

## 4. OPEN TASKS

| # | task | note |
|---|---|---|
| 2 | `xpred_thresh` collision | one knob drives the search range (`rung >= t`) and the delegate split (`etf > t`) |
| 5 | delegate stage + missed-prediction edge case | **deferred** — do not build on mid-swing exhaustions |
| 7 | branch 1 fires 2 of 208 | same cause as §3 |
| 8 | re-run seam-alignment on real data | §12.3 is MY finding, measured on 40% synthetic tape, reads as established. Treat as unproven. |
| 9 | `xcp_origin_dwell = 4` | live, and §10.6 records it as wrong (s88 passes by one bar) |
| 10 | bear/up-leg asymmetry | bear sits in an up-leg 64.9%, bull 47.9%. `_polar` mirrors every term, so this shouldn't exist. |
| 11 | **sell-off regime needs its own mechanic** | Joe 0729: *"the May dates aligned with a 40% sell off. we need separate mechanic to handle this."* Every misplaced bee-line selection (pos < 0.5) was **bear**, dated 05-21/05-22/05-24/05-27, three of four delegating into s23–s24. The current chain has no regime term, so a sustained directional move is scored with the same machinery as a range. Related to #10 — the bear/up-leg asymmetry may be this regime rather than a `_polar` defect. |
| 12 | **score delegation on excursion, not `pos_in_leg`** | `pos_in_leg` is a hindsight ratio (needs the closing pivot) and does not map to a stop. At pos 0.698 the right-direction excursion to the pivot is med **1.95%** with only **3/58 (5%)** at or under 0.9%. Re-score every delegation result on `ep_move_to_pivot_pct`. |
| 13 | **solve the sell-off window — during the knob sweep** | Joe 0729: *"add a task to solve the sell-off window ... when we sweep the knobs."* The sell-off is the May window (05-21 / 05-22 / 05-24 / 05-27) that produced every misplaced bee-line selection, all bear. **CACHE NOTE — this is the trap:** the extended cache (`end_ms` = 07-23, tape `fe809b09`) spans **06-01 08:00 → 07-22 23:59** and therefore **excludes 05-18 → 05-31**, i.e. most of the sell-off. Sweeping knobs on the new cache silently drops the regime this task exists to solve. Use the **04-28 → 06-13 tape (`fb3c8372`, `end_ms` = `JUNE_END`)** for any sell-off work. Both caches are on disk and keyed by `end_ms`; **select per job** (Joe 0729). Related: #11 (regime mechanic), #10 (bear/up-leg asymmetry). |
| 14 | **build the measurement-foundation guard into the evo sweep** | Joe 0729: *"this logic should be baked into the rpl evo sweep machine. there is a process that decides which centroid to promote at the start of each round — I think this would be the home for it."* Fitness is only comparable across rounds if the foundation is identical, and **two axes can shift without any swept knob changing**: which `rpl_config` baseline is live (`baseline` vs `r12_rpl` differ on 9 knobs incl. `wob_n` 9→7, which IS the 40 s confirmation lag → every entry price moves) and which line cache the tape came from (`fb3c8372` 04-28→06-13 vs `fe809b09` 06-01→07-22; fixed ~51.7-day window that *slides*). Home = §5 step 4 distributed seeding + §5.1 OOS checkpoint — the only two cross-round comparison points. Design sketch (stamp a foundation fingerprint on every `rpl_evo` row; assert at promotion; surface in the pulse) written up in **`rpl_sweep_spec.md` §5.7**. Precedent: §5 already flags the same class of error for random windows only. **Note only, no code — Joe's instruction.** **DECIDED (Joe 0729): on mismatch, HALT** for in-situ review — *"halt so I can review in-situ and make a call."* Do not auto re-score. |

## 5. WORKING WITH JOE

- He catches things in output that I miss. Every correction that mattered today started with him reading a
  number and saying it couldn't be true. **Take "I can't believe that" as data.**
- **BUILD-GATE**: enumerate unspecified concretions before any code/config/DB edit. Decide *structural*
  ones (SRP/precedent/measurable) and state the choice; escalate *value* ones.
- Never coin shorthand for a mechanic — use his words or ask him to name it. Gloss every var inline
  (role + value + units).
- Describe mechanics in data terms (lines/thresholds/crosses), not trading stories.
- **On defensiveness** (his note, 0729): excitement *is* ownership when what's owned is the artifact. The
  flip happens when ownership migrates from the artifact to the assertion. The tell is grammatical —
  "the race key throws them away, that's mine" points at code; "I'd rather say so now than present it as a
  finding again" points at my record. When protecting a conclusion, hand it back to the artifact.

## 6. THE LAST TEN EXCHANGES

**JOE:** `test in subsets: per group of 12 consecutive TFs, per group of 5 consecutive days, and anything
else you can see`

**ME:** Ran the stratified pivot test. ALL: n=168, dir-match 40.5%, lead med 6,598 s — against a random
baseline of 49.2% / 6,870 s. TF 22-33 83.3% (n=6), TF 118-120 17.9% (n=28), days 06-02+5 18.2%, bull 47.9%
vs bear 35.1%, climbs=0 34.0% vs climbs≥1 48.6%. Reported it as a clean negative: exhaustions do not land
before pivots, and on direction they are *below* chance. Flagged that 40.5% vs 49.2% is a tilt the wrong
way, not noise, and that flipping the mapping gives 59.5% — so either the polarity is inverted or something
else is. Noted leg b = 205/208 bounds what was measured.

**JOE:** `go`

**ME:** Tested both mappings plus a convention-independent check. Spec mapping 40.5%, flipped 59.5%. The
decisive one: from a bull exhaustion price moves −0.76% median to the next pivot (should rise into a High);
from bear, +0.79% (should fall into a Low). Both backwards. Argued the likelier reading was **lateness**
rather than inversion — a bull exhaustion landing just *after* its high makes the next pivot the following
low — and proposed measuring backwards to the previous pivot to separate the two.

**JOE:** `review swing_detect docs. it knows how to correctly label trades that opewn on the MFE side, so
that the first pivot is not interpreted as MAE`

**ME:** Read `optimus9/compute/swing_detect.py`. `find_pivots(price, pct)` → alternating `(index, 'H'|'L')`;
`legs(price, pivots)` → `{start, end, dir, amp_pct}`. Measuring to the next pivot from mid-leg is exactly
the MAE misread. Re-ran using the containing **leg**: ALL n=168, in up-leg 57.7%, **position in leg 0.50**,
dir correct 40.5%. bull pos 0.55 / bear 0.46; bear in an up-leg 64.9%. Median 0.50 kills both the "late"
and "inverted" hypotheses — a timing error would cluster near 0 or 1.

**JOE:** `if you're out of context, what can you dump to db?`

**ME:** Created and populated **`rpl_exh_pivot`, 207 rows** — every applied exhaustion joined to its
containing leg: `ep_leg_dir`, `ep_leg_amp_pct`, `ep_pos_in_leg`, `ep_secs_to_pivot`, `ep_want_dir`,
`ep_dir_correct`, `ep_move_to_pivot_pct`, leg start/end. Pasted the SELECT. Restated the finding and the
leg-b caveat.

**JOE:** `tag your findings`

**ME:** Wrote `bp50.md` **§13** — §13.1 the finding with the strata table and both dead hypotheses, §13.2
what it does and does not indict (leg b 205/208, branch 1 fired twice, #7 must land first), §13.3 the query.
Created **task #10** for the bear/up-leg asymmetry. Moved **task #5 back to pending, not started**, because
building the delegate on mid-swing exhaustions would optimise the wrong input.

**JOE:** `do you know how to manually check the individual signals for validity? my gut says that comparing
the mid-leg signals against a exhaustion cross at a lower TF might show a thread`

**ME:** Gave the four-step manual check (row from `rpl_exh_pivot` → verify the cross at the raw bar →
pull `rpl_exhaust` for that leg across all TFs → compare positions), then ran it in aggregate. **95.7% of
applied events had a lower-TF marker sitting nearer the pivot; fired 0.46 vs best available 0.96; TF gap
median 18.** Concluded the signal isn't missing, the selection is wrong — and that `xpred_band`, which I'd
dismissed, measures better than what replaced it.

**JOE:** `bake a handover doc for new you, complete with the instructions needed to start work without
delay` / `the doc should have our recent 10 responses (5 for you, 5 for me)`

**ME:** This document.

## 7. FILES

`build_exhaust.py` (markers → `rpl_exhaust`) · `build_rplwalk2.py` (ladder + walk → `rpl_exh_applied`) ·
`build_bandlab.py` (superseded; kept for the measurement-error notes in §12.4) ·
`docs/bp50.md` (the spec — §1 verbatim, §12 void table, §13 external check) ·
`optimus9/compute/swing_detect.py` (`find_pivots`, `legs`)

---

## 8. TASKS ADDED 0730

**#20 — post-exhaustion MAE dialing** *(CURRENT)*
`rpl_exh_stat` holds 87 rows 05-20→06-03, each with `es_rpred_*` and `es_rpred_label`. Label split, MEANS
ONLY: `r-pred` n=65 MAE4 3.00 / MFE4 5.58 / ratio 1.86; `2nd x r-pred` n=21 MAE4 2.00 / MFE4 4.98 /
ratio 2.49. Needs medians, p90 MAE, random baseline (full-set random was ratio 2.02 at 4.00%), two-stage
protocol. The 05-20/05-21 rows sit inside one 10% leg with MAE near 10 and inflate the `r-pred` mean.

**#21 — `kc_volume` never repaired, event tape degenerate**
`optimus9/data/kline_sanitiser.py` UPDATEs `kc_open/high/low/close` only. Zero-volume fraction:
`04-28..05-17` 0.0%, `05-18..06-07` 0.0%, `06-08..07-09` 3.6%, `07-10..07-30` 31.7%. `ei` = 807,432 of
807,432 = 100%. Affects `_px_smooth_evt` and `cadence = ei[ts[ei] > CONF]`. Fix = add `kc_volume` to the
UPDATE and re-run — IF the TV 5S export carries volume (open question for Joe).

**#22 — collect TV 5S for 04-28 → 05-17** *(NEEDS JOE)*
The last synthetic stretch. Flat bars 6.6% vs 22.5-36.1%; zero-volume 0.0% vs 3.6-31.7%; pure ramps 82.5%
vs 40-42%. It is the warmup feeding s109-s120 at the start of the analysis window. NOT needed:
`07-10..07-30` and `06-29..07-07` are tick-built and audited against Bybit 1m klines.

## 9. NEW DOC 0730

**`docs/rpred_spec.md`** — the r-pred mechanic in full: `predict_breach`, the x/r cancel latch, the
clean/dirty flag, the `2nd x r-pred` label, the two-pass and its live equivalence, every column, and the
open items. Read it before touching anything r-pred.
