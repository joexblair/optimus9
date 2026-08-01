# 260731 handover — read this first, then §1's reading list

Written 2026-07-31 for the next session. Joe's instruction: *"add anything else that you will find useful
so that I don't have to explain anything that we're currently using."* Assume he explains nothing.

---

## 0. START WORK IN FOUR STEPS

1. Read **§1 reading list** — the four docs marked REQUIRED. Nothing else in `docs/` is needed to start.
2. **Recreate the task list** — §7. One `TaskCreate` per row, in order. Joe's numbering (#2..#26) lives in
   the *subject*; the tool's own IDs are 1..22 and are meaningless to him. Always speak in Joe's numbers.
3. **Verify the tree runs** — `python3 report_exhv2.py` should print 87 rows in ~1 s with no rebuild.
4. **First job is task #26** — the Mage-develop hold. Spec is `docs/exhv2_spec.md` **§10a**, verbatim.
   Job one inside it is *measuring* `recently`. Do not pick a value for it.

---

## 1. READING LIST

**REQUIRED — read in full before touching code**

| doc | why |
|---|---|
| `docs/exhv2_spec.md` | 410 lines. The mechanic you are working on. §10a is your first job. |
| `docs/rpred_spec.md` | the r-pred mechanic in full. exhv2's walk STARTS at `es_rpred_ms`. |
| `docs/jig.md` | the jig is the producer library. Every causal signal must come from it, not a fork. |
| `docs/staying_light.md` | how to not blow the context / the runtime budget. Joe notices when you do. |

**REQUIRED — the working relationship**

| doc | why |
|---|---|
| `docs/korero_working_relationship.md` | how Joe works. 21 KB. Read it. |
| `docs/260729_rpl_handover.md` §1, §5 | hard constraints + "working with Joe". §5 is short and it matters. |

**READ WHEN THE TASK TOUCHES IT**

| doc | trigger |
|---|---|
| `docs/bp50.md` | RPL itself — 92 KB, the master spec. §18 is the 0730 addition. |
| `docs/rpl_sweep_spec.md` | any knob sweep. §5.7 is the measurement-foundation guard (task #14). |
| `docs/rpl_flow_spec.md` | the flow/chain structure |
| `docs/causal_lookahead_register.md` | before claiming anything is causal |
| `docs/quirks_to_remember.md` | short, saves repeat mistakes |
| `docs/linelab_spec.md` | `swing_detect` 1% pivots — the scoring tape for every A/B |
| `docs/rpl_event_store_spec.md` | writing to `rpl_*` tables |

---

## 2. HARD CONSTRAINTS — violating these has cost real time

- **Data before 05-18 is SYNTHETIC.** Warmup only, never analysis. Flat bars 6.6% vs 22.5-36.1% on real
  stretches; zero-volume 0.0% vs 3.6-31.7%; pure ramps 82.5% vs 40-42%.
- **NEVER apply a cap** — no horizon, window, or truncation, in code OR in a diagnostic, unless Joe
  specified it. This includes "top 10 rows" in a report.
- **NEVER `DROP` or overwrite a table Joe is using.** Build alongside under a new name. Scope changes go to
  Joe *before* the run.
- **NEVER `pkill -f <pattern>`** where the pattern matches your own shell — it does, and it kills you.
  Launch to a fresh output file instead.
- **Two-stage A/B, always.** Stage 1 banks causal timestamps to disk. Stage 2 loads `swing_detect` and
  scores. Never feed scoring back into generation.
- **BUILD-GATE.** Before any code/config/DB edit, enumerate every unspecified concretion. Decide the
  *structural* ones (SRP / precedent / measurable) and **state the choice**. Escalate *value* ones.
- **Joe cannot see tool output.** Paste the actual content into the message. Every table, every number.
- **RPL starts at TF22** — `build_exhaust.RPL_FLOOR = 22`.
- **No lookahead.** If a producer needs a value it cannot causally reach, that is a design fault, not a
  detail to work around.

---

## 3. WHAT IS LIVE RIGHT NOW

### exhv2 — the thing being built

- **producer**: `build_exhv2.py`. `--persist` writes `rpl_exhv2` (87 rows). Full run ~4 min.
- **report**: `report_exhv2.py`. DB-only, no build imports, ~1 s. `--race` adds the diagnostic column.
- **pine**: `emit_exhv2_pine.py` → `exhv2_tf4.pine`. **FORMAT IS LOCKED — see §4.** File is gitignored.
- **table**: `rpl_exhv2`, 87 rows, `05-20 07:48 .. 06-03 20:36`.
- **targets**: 14 hand-marked `corrected_conf` values in `transfer/260730_exhv2_notes.csv`.
  Current: mean `+38.7`, median `+25.5`, mean |err| `55.2`, median |err| `38.4` minutes.

**The flow, in one line:** an RPL exhaustion fires → take its `es_rpred_ms` → **walk forward** to the first
bar `s4Mage` *crosses* to OOB and holds contiguously for `WALK_DWELL_BARS` → classify `s15r` and `s22r` as
`momo` / `sideways` / `curl` / `none` → that picks the **branch** (momo vs s4) and the **act** (`rev` vs
`EXIT`) → the **signal** fires on **A ungated**.

- **`signal`** (`v2_sig_ms`) = **A ungated** = the first `s15x × s15m` cross at or after the **walk** bar,
  in the trade direction, **no qualify, no gate**. On **all 87 rows**.
- **`act`** = `rev` (67) / `EXIT` (20). It classifies; it no longer changes which cross emits.
- **`race`** (`v2_race_ms`) = the branch race bar A replaced. Kept in the table, **off the report**
  (Joe 0731: *"race column is not as valuable"*). `--race` puts it back.
- Joe 0731: *"I was using exit generically for exit and rev."* When he says "exit", he means the signal.

**Joe's LOCKED report format.** Do not vary it without being asked:

```
r-pred | walk | bias | TF | s15 s22 act | branch cross | signal
```

### RPL — the parent mechanic

- `build_exhaust.py` → `rpl_exhaust` (markers)
- `build_rplwalk2.py` → `rpl_exh_applied` (ladder + walk). `applied_2pass()` resolves the r-pred
  circularity by iterating; converges `144 → 147 → 147`.
- `build_rpred.py` → `rpl_rpred` (377 rows). Pass 1 flips `RPRED_PERSIST` and rebuilds; pass 2 fills
  `es_rpred_*`.
- `build_exh_stat.py` → `rpl_exh_stat` (87 rows, MFE/MAE at 2.22% and 4.00%)

### The jig — `optimus9/analysis/jig.py`

The producer library. **Every causal signal comes from here**; a fork is a defect. Session additions:

- `_Causal.clean_dirty(r, x, side, hi, lo, fh, fl, wob, mode, spend_bars)` — the single clean/dirty
  producer. `mode='rpl'` takes applied-exhaustion bars as the spend; `mode='exhv2'` derives the spend from
  x crossing r or the boundary. Lines start **dirty**. Two clean scenarios, both first-class: x crosses
  back through r, **or** r returns to the FH/FL fence.
- `RED_BG_TRANSP = 47` — literal bgcolor transparency for `color.red` only, applied inside
  `_bgcolor_frag` so every modular pine caller inherits it (Joe 0731: solid red masked the bearish candle bodies).
- **`_bgcolor_frag`'s docstring carries a FORMAT LOCK.** Read it before touching any pine emit.

**GOTCHA:** the cached path uses `rpl_cache._Cau`, **not** `jig._Causal`. Any new array-only producer in
`_Causal` needs a delegating line in `_Cau` or the cached path raises `AttributeError`.

---

## 4. EVERY KNOB TOUCHED THIS SESSION

### exhv2 — `build_exhv2.py`

| knob | value | units / role |
|---|---|---|
| `MOMO_WINDOW_MIN` | 60 | minutes. Momentum sample window. Joe 0731 raised it from 45. **SWEEP** |
| `MOMO_STEP_MIN` | 5 | minutes between samples |
| `MOMO_STEP_BARS` | 60 | derived: `5 × 12` bars at the 5 s grid |
| `MOMO_SAMPLES` | 12 | derived: `60 / 5`. Was 9 at the 45-min window |
| `MOMO_SLOPE_MIN` | 1.0 | r-units per 5-min sample. Slope floor. Joe's refs: 2.858 / 0.217. **SWEEP** |
| `MOMO_R2_MIN` | 0.50 | dimensionless. Straightness floor. **SWEEP** |
| `CURL_ARC_MIN` | 4.0 | r-units. Arc height above which a "sideways" verdict is re-read as a curl. **SWEEP** |
| `CURL_VTX_LO` / `CURL_VTX_HI` | 0.05 / 0.95 | fraction of window. Vertex must sit inside, not on the edge |
| `WALK_DWELL_BARS` | 48 | bars = **240 s** at the 5 s grid. The OOB run must hold **CONTIGUOUSLY** |
| `LEVEL_SLACK` | 13.9 | r-units. Gate slackens by `LEVEL_SLACK × T`, `T = R² × min(1, \|slope\|/slope_min)`, clipped [0,1]. **SWEEP** |
| `TFS` | `(4, 15, 22)` | exhv2 is contained to TF ≤ 22 |
| `HI` / `LO` | 85 / 15 | OOB boundaries |
| `tgt_order` | `('r','Mage','boundary')` | same-bar tie-break, explicit. Matches `build_exhaust.py:134`'s implicit append order |

**`LEVEL_SLACK` provenance:** drawn uniform 0-15 on `os.urandom` entropy at Joe's instruction — *"coin-toss
it… your random choice might uncover other quirks that we would otherwise miss"*. It did: at 13.9 the
mechanic **over-fires** momentum on `0520 07:03` and `0521 02:05`. A tighter value trades those back.

**Curl detection runs at FULL 5 s resolution** (720 bars at a 60-min window), not at the 12 point-samples.
At 12 samples the quadratic fit hallucinates turns. Curl = vertex inside `[0.05, 0.95]` **AND**
`|a|/4 ≥ CURL_ARC_MIN`.

### exhv2 line set — Joe 0731, exhv2 builds its OWN lines

Four of five differ from the live `rpl_config` baseline. **Do not "fix" these back.**

| line | exhv2 | live baseline |
|---|---|---|
| `x` s4/s15/s22 | bb **4**\|0.37\|close | bb 5\|0.37\|close |
| `m` s4/s15/s22 | bb 6\|0.45\|close | same |
| `M` s4/s15/s22 | bb 37\|**0.7**\|close | bb 37\|0.83\|close |
| `r` **s4** | kline 7\|**6**\|11\|close | kline 7\|5\|11\|close |
| `r` **s15 / s22** | kline **10\|4**\|11\|close | kline 7\|5\|11\|close |

### r-pred — `optimus9/orchestration/rpl_walk.py`

| knob | value | role |
|---|---|---|
| `RPRED_PERSIST` | `False` | **default OFF.** `build_lines` runs at import and ~20 scripts import this module |
| `RPRED_START` | `2026-05-18` | write floor. r-pred still *looks back* freely |
| `RPRED_END` | `None` | write ceiling |
| `RPL_TF_CEILING` | env override | **⚠ CHANGES THE TAPE, not just the ceiling** — `_ovr` is part of the cache key. At 120 the tape is 05-22→07-12 (892,800 bars); the research tape is 04-28→06-13 (807,432 bars) |
| `RPRED_VETO` | `True` | **DEAD NO-OP**, cannot fire. Marked for removal (Joe 0725) |
| `predict_breach` | `HI` 85 / `LO` 15 / `FH` 70 / `FL` 30 / `tol` 0.0 | `optimus9/compute/breaching_line.py:26`. Emits a per-bar STATE `{+1, −1, 0}`, no timestamp |

### jig / pine

| knob | value | role |
|---|---|---|
| `RED_BG_TRANSP` | 47 | `jig.py`. bgcolor red transparency, 0 solid .. 100 invisible. Red only — blue/yellow/green still at 0 |
| `wob_n` | 9 bars = **45 s** at the 5 s grid | `cross_wob` debounce. The sanctioned cross producer |
| `_labels_frag` `transp` | 75 | label colour transparency, unrelated to bgcolor |

`RED_BG_TRANSP` is honoured by every caller of `jig._bgcolor_frag` (i.e. `emit_bgcolor`, `emit_overlay`).
A stream can opt out with an explicit per-stream `'opacity'` key. Hand-rolled emitters were set to 47
individually: `arm_gate_emit.py:89`, `build_flip_finisher_pine.py:68`, `lp_cascade_emit.py:130`,
`cf15_pine_emit.py:53`, `emit_combo_recon.py:106`, `emit_bl_viz.py:133`, `build_past50_pine.py:55`,
`kernel_full_pine.py:41`, `optimus9/emit/pine_strategy_emitter.py:579,581,583`.

### ⚠ THE PINE EMIT FORMAT IS LOCKED

**Joe 0731: *"add a note to the jig pine emit: don't change the format without auth."*** The lock is
written into the `jig._bgcolor_frag` docstring. Read it before touching anything pine.

The emitted shape, exactly: header note → `indicator()` → one `input.bool` per stream → one `f_<name>()`
array function per stream → the array calls → `bg = color(na)` → one `if` per stream assigning `bg :=`
**with a literal transparency** → a **single** `bgcolor(bg)`.

```
bg = color(na)
if show_s_walk_hi and array.binary_search(s_walk_hi, time) >= 0
    bg := color.new(color.blue, 0)
if show_s_walk_lo and array.binary_search(s_walk_lo, time) >= 0
    bg := color.new(color.yellow, 0)
if show_s_sig_short and array.binary_search(s_sig_short, time) >= 0
    bg := color.new(color.red, 47)
if show_s_sig_long and array.binary_search(s_sig_long, time) >= 0
    bg := color.new(color.green, 0)
bgcolor(bg)
```

- **I broke this TWICE in one session.** Once by "improving" it to per-stream `bgcolor()` calls; once by
  replacing the literals with an `opac = input.int(...)` slider. Joe rejected both and pasted the target
  block back verbatim. **There is no `opac` input.** Do not add one.
- transparency is a **literal per stream**: blue `0`, yellow `0`, **red `47`**, green `0`.
  `RED_BG_TRANSP = 47` applies to `color.red` only; every other stream takes the caller's `opacity`.
- **KNOWN AND ACCEPTED**: a single `bg` var means the **last matching `if` wins**, so on a shared bar the
  later stream hides the earlier one. Stream order **is** priority. That is a property of the format.
- **currently 12 of 72 walk bars are hidden by a signal** (was 6 under the race signal) — A ungated fires
  a median 10 min after the walk, so it lands in the same TF4 bucket far more often. 11 blue, 3 yellow.
  Joe has seen the list. **He has not asked for it to change. Do not change it.**

---

## 5. RUNTIMES — so you can predict, and so you don't over-poll

| step | measured |
|---|---|
| `import rpl_walk` | 16.0 s |
| `import build_exhaust` | 37.7 s |
| `rebuild_cache(120)` | 9.9 s |
| all three, cold | ~64 s |
| `build_exhv2.py --persist` | ~4 min |
| `report_exhv2.py` | ~1 s (DB only) |

- **Predict before you run**, and when you overshoot the prediction, say so unprompted.
- The line cache is per-line and keyed on each line's own resolved spec, so a partial config change only
  rebuilds the changed lines. `CACHE_DIR` = `optimus9/orchestration/.rpl_cache`, gitignored.
- **Two caches exist and are keyed by `end_ms`** — `fb3c8372` (04-28→06-13, `end_ms = JUNE_END`) and
  `fe809b09` (06-01→07-22). **Select per job.** The second one *excludes* 05-18→05-31, i.e. most of the
  sell-off window — see task #13, that is the trap.

---

## 6. DATA FOUNDATION — known defects

- **`kc_volume` was never repaired.** `optimus9/data/kline_sanitiser.py` UPDATEs `kc_open/high/low/close`
  only. So `evt = volume > 0` is true everywhere and `ei` = 807,432 of 807,432 bars = **100%**. The event
  tape is degenerate. Affects `_px_smooth_evt` and `cadence`. Task #21.
- Zero-volume fraction by stretch: `04-28..05-17` 0.0% · `05-18..06-07` 0.0% · `06-08..07-09` 3.6% ·
  `07-10..07-30` 31.7%.
- `kline_audit` covers **07-23 → 07-30 only**.
- **PRTG `faults_5s` fires on no-trade bars** — 347 of 413 `frozen` faults have `kc_volume = 0`. Task #23,
  needs Joe's OK before changing the gate.
- `07-10..07-30` and `06-29..07-07` are tick-built and audited against Bybit 1m klines — those are clean.

---

## 7. RECREATE THE TASK LIST

One `TaskCreate` per row, in this order. **Put Joe's number in the subject** — he refers to tasks by
these numbers, and the tool's own IDs (1..22) will not match. Set #20 to `in_progress`, the rest `pending`.

| Joe's # | subject | detail source |
|---|---|---|
| 2 | `xpred_thresh` collision: one knob, two mechanics | one knob drives both the search range (`rung >= t`) and the delegate split (`etf > t`) |
| 5 | delegate stage + missed-prediction edge case (DEFERRED) | do not build on mid-swing exhaustions |
| 7 | branch 1 fires only 2 of 208 | same cause as `260729_rpl_handover.md` §3 |
| 8 | re-run seam-alignment on real data (currently VOID) | measured on 40% synthetic tape, reads as established. Treat as unproven. |
| 9 | `xcp_origin_dwell = 4` is live and recorded as WRONG | s88 passes by one bar |
| 10 | bear/up-leg asymmetry that should not exist | bear sits in an up-leg 64.9%, bull 47.9%. `_polar` mirrors every term. |
| 11 | sell-off regime needs its own mechanic | every misplaced bee-line selection was bear, 05-21/22/24/27. No regime term in the chain. |
| 12 | score delegation on excursion, not `pos_in_leg` | `pos_in_leg` needs the closing pivot = hindsight. Re-score on `ep_move_to_pivot_pct`. |
| 13 | solve the sell-off window during the knob sweep (**CACHE TRAP**) | use the 04-28→06-13 tape `fb3c8372`. The extended cache excludes most of the sell-off. |
| 14 | measurement-foundation guard at centroid promotion | `rpl_sweep_spec.md` §5.7. **On mismatch, HALT** for in-situ review — Joe's call, do not auto re-score. |
| 15 | s3a x-cross: fall back to s4r when s3r is missing inside the r-lookback | |
| 16 | parallel {TF+[1,2,3]} `wob_cross` as a cross-decision assist (FLAGGED IDEA) | |
| 17 | band map defect: TF3 and TF 9-30 run the wrong r oscillator | |
| 18 | A/B: adding the s3a+x-cross finisher stage to the chain | two-stage protocol |
| 19 | Jig's `line()` path bypasses the line cache and recomputes every call | |
| 20 | **post-exhaustion MAE dialing** — set `in_progress` | `rpl_exh_stat`, 87 rows. Label split MEANS ONLY: `r-pred` n=65 MAE4 3.00 / MFE4 5.58 / ratio 1.86; `2nd x r-pred` n=21 MAE4 2.00 / MFE4 4.98 / ratio 2.49. Needs medians, p90 MAE, random baseline (full-set random = 2.02 at 4.00%). |
| 21 | `kc_volume` never repaired — event tape degenerate | §6 above. **Open question for Joe: does the TV 5S export carry volume?** |
| 22 | collect TV 5S for 04-28 → 05-17 (**NEEDS JOE**) | the last synthetic stretch |
| 23 | PRTG `faults_5s` gate on `kc_volume > 0` (**NEEDS JOE'S OK**) | §6 above |
| 24 | build exhv2 | largely done — `build_exhv2.py`, `rpl_exhv2`, `exhv2_spec.md`. Close it or narrow it. |
| 25 | jig producer consolidation + fork-2 divergences on the sweep list | Pine split out of `_Score`. Forks 1, 3, 4, 6, 7, 8 still to pull in. Fork 2 = follow `rpl_walk`; add its divergences to the sweep list. |
| 26 | **the Mage-develop hold: measure `recently`, then drop the trigger** | `exhv2_spec.md` §10a, verbatim. **THIS IS THE FIRST JOB.** |

---

## 8. FILES THIS SESSION CREATED OR CHANGED

**New, in the repo:**

- `build_exhv2.py` — the exhv2 producer
- `report_exhv2.py` — the locked-format report, DB-only
- `emit_exhv2_pine.py` — the pine emit (format LOCKED, see §4)
- `build_rpred.py`, `build_exh_stat.py` — the two-pass r-pred fill and the stat rebuild
- `docs/exhv2_spec.md` (410 lines), `docs/rpred_spec.md` (~290 lines)
- `docs/260731_handover.md` — this file

**Changed:**

- `optimus9/analysis/jig.py` — `_Causal.clean_dirty`, `RED_BG_TRANSP = 47` in `_bgcolor_frag`
- `optimus9/orchestration/rpl_cache.py` — `_Cau.clean_dirty` delegation
- `optimus9/orchestration/rpl_walk.py` — `persist_rpred`, the x/r cancel in `_climb_to_prov`,
  `RPL_TF_CEILING`
- `build_rplwalk2.py` — `applied_2pass`, `rpred_episodes`, `line_state` now calls the jig producer
- 11 pine emitters — red bgcolor to 47

**`emit_exhv2_pine.py`** — the pine emit, now a repo file (it used to live in the session tmp dir and die
with the session). Reads `v2_sig_ms`, `v2_walk_ms`, `v2_eff_bias`, `v2_walk_side` from `rpl_exhv2`; buckets
every timestamp to its TF4 bar (`ms // 240000 * 240000`); four streams **in this order** —
`walk_hi` blue (`v2_walk_side == 'hi'`), `walk_lo` yellow, `sig_short` red (`v2_eff_bias == 'bull'` → hi
breach → SHORT), `sig_long` green (`bear`). Output `exhv2_tf4.pine`, **gitignored** (`.gitignore:9 *.pine`).
Last run: 143 painted bars, 35/36/35/37 distinct TF4 bars, span `05-20 07:48 .. 06-03 20:36`.

---

## 9. OPEN FLAGS — raised, not ruled on

- **EXIT colouring.** 20 of the 87 rows are `act = EXIT` and paint red/green by direction exactly like a
  reversal, so an exit is indistinguishable from an entry on the chart. Raised three times. Two colours
  are free if Joe wants them split.
- **`over/under Moob` known weakness.** The test is positional (`x > Mage` for a hi walk). When s4Mage has
  crossed to the far side by the cross bar it is vacuous: `0520 07:42` fires SHORT at 07:58 where s4Mage is
  −3.71 (lo-OOB) and `x > −3.71` passes for almost any x. The strict alternative — require s4Mage still OOB
  on the walk side at the cross — pushed two signals **three days** out and was rejected.
- **MFE/MAE has NOT been re-scored on `v2_sig_ms`.** The whole case for A ungated rests on pivot distance,
  not measured excursion. Both timestamps are in `rpl_exhv2` side by side, so one pass settles it.
  Joe's read of the worst row (`0521 21:04`, A at 23:02, 118 min lag) from the chart: **~2.0 MFE / ~0.4
  MAE** — *"the mechanic is doing a great job."* Wall-clock lag alone is the wrong measure.

---

## 10. HOW JOE WORKS

Full detail in `docs/korero_working_relationship.md`. The parts that bite in the first hour:

- **He catches things in output that you miss.** Take *"I can't believe that"* as data, every time. Every
  correction that mattered started with him reading a number and saying it couldn't be true.
- **Response format is specified** and he will call out drift by name (*"Joe's convo style"*): short
  raw-data bullets, numbers first, no connecting prose; gloss every var inline with role + value + units;
  then two mandatory closers — a one-paragraph **Summary**, then **PnL impact** opening with a `TL;DR:`
  line. Say "no effect" or "unknown" when that is honest. Never pad it.
- **Never coin shorthand for a mechanic.** Use his words, or ask him to name it. When he asks *you* to
  name something, check whether an existing word already covers it before inventing one.
- **Describe mechanics in data terms** — lines, thresholds, crosses. Not trading stories.
- **On defensiveness** (his note): excitement *is* ownership when what's owned is the artifact. The flip
  happens when ownership migrates from the artifact to the assertion. The tell is grammatical — *"the race
  key throws them away, that's mine"* points at code; *"I'd rather say so now than present it as a finding
  again"* points at your record. When protecting a conclusion, hand it back to the artifact.
- **Don't treat him like a fool.** He told you this once. When his chart read disagrees with your output,
  the default assumption is that your output is wrong.
- **He answers precisely when asked precisely.** A vague question gets a vague answer and costs a round
  trip. Ask for the one value you need.
- When he says *"pick one fault only and we'll work on it together"*, he means it — a wall of findings is
  worse than one.
