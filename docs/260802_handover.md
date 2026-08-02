# Handover — 2026-08-02

Branch `causal/lookahead`. Last commit `554156f` *bp50: exhv2 + the s4M-cycle re-walk, driven by the r-pred alone*.

---

## §0 — START HERE, FOUR STEPS

**Step 1.** Read the §1 REQUIRED list. Nothing else first.

**Step 2.** Recreate the task list from §7, using Joe's numbering in the subject line.

**Step 3.** Verify the tree runs: `python3 build_exhv2.py` → expect `exhv2: 142 of 142 rows produced a walk`, ~45 s.

**Step 4 — YOUR FIRST JOB, no discussion needed, Joe has already approved it.**

> **Rebuild everything on ONE configuration: REWALK 2 + gcs15 confirm.**

Joe, verbatim, 0802: *"we can't be using both"* … *"here's the history and the approved decision"* … *"agreed on gcs15"*.

Three artefacts are currently built on the **wrong** signal definition (`A ungated`, the raw s15x × s15m cross) and two of them are banked for **both** REWALK 0 and 2. Fix all three:

| # | artefact | current state | required state |
|---|---|---|---|
| 1 | `build_dominoes_db.py` | **HALF-EDITED.** Docstring says REWALK 2 + gcs15 confirm. Code at `:137` still says `for mode in (0, 2)` and `:147` still takes `ro[I['sig']]` raw | one mode (2); signal = first gcs15 cross at/after `ro[I['sig']]` |
| 2 | `rpl_dominoes` / `rpl_walkcand` | 284 / 5,212 rows, built on the wrong config | rebuild — the script DROPs and recreates both |
| 3 | `emit_dominoes_pine.py` → `dominoes.pine` | `--rewalk 2` default but signal is `A ungated` | same gcs15 confirm change |

**The gcs15 confirm rule, exactly:**

```python
# gcs15 = the gcs/RPL flavour (what gcs5 and s30 already are; gcs15 was cloned from s30).
# NOT exhv2's x bb 4|0.37.
ovr = {**bbline('gcs15x', 15.0/60.0, length=5, mult=0.37, src='close'),
       **bbline('gcs15m', 15.0/60.0, length=6, mult=0.45, src='close')}
J  = cache_jig_perline(R.end_ms, 40, 600, ovr, pxs_cfg=R.PXS_CFG)
GX = np.asarray(J.W.line('gcs15x'), float); GM = np.asarray(J.W.line('gcs15m'), float)

xdr = -1 if side == 'hi' else 1                       # hi walk -> SHORT
c   = R.L0['src'].causal.cross_wob(GX - GM, 0.0, xdr, R.WOBN)   # wob_n = 9 bars = 45 s
XC  = np.flatnonzero(c & ~np.r_[False, c[:-1]])       # rising edges

anchor = int(np.searchsorted(ts, ro[I['sig']]))       # the s15x X s15m cross — ANCHOR, not signal
nx = XC[XC >= anchor]
if not len(nx):
    lost += 1                                         # COUNT AND REPORT. Do not silently drop.
    continue
sb = int(nx[0])                                       # THE SIGNAL
```

- keep the anchor as its own column `dm_s15x_ms` / `dm_s15x_utc` — Joe needs to see the lag the confirm adds
- read the LTF-Mage dominoes state at `sb` (the confirmed signal), **not** at the anchor
- report how many rows have no gcs15 cross after the anchor. **No silent truncation** — that is a standing rule

**Then re-run every headline number in §9.** They are all on `A ungated` and are therefore not the approved mechanic's numbers.

---

## §1 — READING LIST

**REQUIRED, before touching code**

| doc | why |
|---|---|
| `docs/exhv2_spec.md` | the mechanic you are working on |
| `docs/rpred_spec.md` | what RPL hands over |
| `docs/jig.md` | line construction, `bbline` tf is **MINUTES** |
| `docs/staying_light.md` | runtime discipline |

**REQUIRED, relationship**

| doc | why |
|---|---|
| `docs/korero_working_relationship.md` | how Joe wants this to go |
| `docs/260729_rpl_handover.md` §1 + §5 | RPL's shape and its knobs |
| `docs/260731_handover.md` | the previous handover; §4 knob table is still current for RPL |

**Read when touched**

`docs/rpl_flow_spec.md` · `docs/linelab_spec.md` · `docs/divergence_research.md` (§12: price source is raw) · `docs/bl_detect.md` · `docs/pine_format.md` · `docs/kline_sanitise.md` · `docs/o9_live.md`

---

## §2 — HARD CONSTRAINTS

- **BUILD-GATE.** Before any code/config/DB edit, enumerate every unspecified concretion. Decide *structural* ones (SRP / precedent / measurable) and **state the choice**. Escalate *value* ones to Joe. Never decide a value gap unilaterally.
- **No caps.** No cap, horizon, window, truncation or top-N — in code **or** in diagnostics — unless Joe specified it. If something is bounded, `log()`/print what was dropped.
- **No `DROP` of Joe's tables.** Build alongside under a new name. `rpl_dominoes` / `rpl_walkcand` are mine and may be dropped by their own builder; nothing else may.
- **Never `pkill -f <pattern>`** where the pattern matches the shell running it. Launch to a fresh output file instead.
- **Two-stage A/B.** Bank causal timestamps first, score with `swing_detect` second. Never feed scoring back into generation.
- **Pre-05-18 is synthetic warmup**, never analysis. `RPRED_START` = 05-18.
- **No lookahead** — and see §9(4), there is one live right now.
- **Never coin shorthand for a mechanic.** Use Joe's words ("falling dominoes", "last mile", "the walk", "slip zone") or ask him to name it.

---

## §3 — WHAT'S LIVE

**exhv2 flow, one line:**

> RPL prints an **r-pred** → bp50 walks forward on s4 to the first **held s4Mage crossing into OOB** → while s22 reads `momo`, re-walk to the next one (**REWALK 2**) → classify s15r/s22r → branch (momo / sideways / s4) → **s15x × s15m cross = ANCHOR** → **next gcs15x × gcs15m cross = SIGNAL**.

- direction is set **at the walk bar**, from the s4Mage OOB side: `sd = 'hi' if M4[b] >= HI else 'lo'` (`build_exhv2.py:294`). **hi → SHORT, lo → LONG.** Not the bias. No cycle, no lookahead.
- the walk bar precedes the signal on **142 of 142** rows. Signal minus walk: min +0.2 min, median +10.3 min, max +117.8 min.
- RPL passes **nothing but the fact of an r-pred**. bp50 must already be warm. No timestamp handoff.

**Producers**

| file | role |
|---|---|
| `build_exhv2.py` | the exhv2 producer. `REWALK` default **2**. `momo()` is module-level. `LINE_SPEC` / `R_SPEC` are its own line set |
| `build_exh_stat.py` | fills `rpl_exh_stat` from `rpl_exh_applied`. **`:130` runs `DELETE FROM rpl_exh_stat` unconditionally**, not only under `--fresh` |
| `build_dominoes_db.py` | the dominoes dataset. **Half-edited — see §0** |
| `emit_dominoes_pine.py` | the pine overlay. **Wrong signal — see §0** |
| `report_exhv2.py` | locked-format report, DB-only, ~1 s |
| `optimus9/orchestration/rpl_walk.py` | RPL. `end_ms` hardcoded 07-13 at `:49`. `_ovr` = 489 names / 487 specs at ceiling 120 |

**jig**

- `emit_bgcolor(streams, path, title, opacity=None, notes=None)` — **FORMAT IS LOCKED**, see §4
- `emit_overlay(labels, streams, path, title, opacity=60, scheme='redgreen', notes=None)` — labels **over** bgcolor, one indicator. This is what `dominoes.pine` uses
- `_labels_frag` label dict = `{ts, y, text, green:bool, up:bool}`; `green` → green/red, `up` → `label_up`/`label_down`; `max_labels_count = 500`
- **`notes` accepts multi-line** — `jig.py:611` splits on `\n` and prefixes each with `// `. Put the colour legend FIRST
- **`\n` inside label text must be the two characters `\` `n`** (Python `'\\n'`). A real newline is a raw newline inside a Pine string literal and will not parse
- `pk_state(line_slope, price_slope, slope_floor)` → `Pk5sGateComputer._pk_state_from_slopes`. ±1 divergence, ±2 PM, 0 noise

**The `_Cau` gotcha:** `Jig.line()` bypasses the line cache and recomputes on every call (task #19). Use `cache_jig_perline` and hold the array.

---

## §4 — EVERY KNOB

**exhv2 — the approved configuration**

| knob | value | units / role |
|---|---|---|
| `REWALK` | **2** | hop to the next held s4Mage OOB crossing while s22 reads `momo`; repeat until it doesn't |
| `WALK_DWELL_BARS` | **48** | bars = **240 s**. An OOB run must last this long before the crossing counts as a walk candidate |
| last mile | **gcs15 confirm** | the s15 cross is the anchor; the next gcs15 cross is the signal |
| `MOMO_R2_MIN` | 0.50 | r² floor for `momo()` |
| `MOMO_SLOPE_MIN` | 1.00 | slope floor, r-units per sample |
| `momo_ride_oob_slip` | **2.0** | r-units of gap to the 15/85 boundary permitted at the cross bar. Last value before MAE max jumps 2.25 → 4.38 |
| `HI` / `LO` | 85 / 15 | boundary. Home is `optimus9_system`, not rpl_config |
| `wob_n` (`WOBN`) | 9 | bars = **45 s**. Cross confirmation dwell |

**Lines — exhv2's own set (`build_exhv2.LINE_SPEC` / `R_SPEC`), NOT the rpl_config baseline**

| line | spec | TF |
|---|---|---|
| x | bb 4\|0.37\|close | per-TF |
| m | bb 6\|0.45\|close | per-TF |
| **M (s4Mage)** | **bb 37\|0.7\|close** | TF4 |
| r (s4) | kline 7\|6\|11\|close | TF4 |
| r (s15, s22) | kline 10\|4\|11\|close | TF15, TF22 |

**Lines added for the dominoes work — rpl_config baseline flavour, mult 0.83 not 0.7**

| line | spec | TF |
|---|---|---|
| `gcs15M` | bb 37\|0.83\|close | 0.25 min = **15 s** |
| `s30M` | bb 37\|0.83\|close | 0.5 min = **30 s** |
| `s1M` | bb 37\|0.83\|close | 1.0 min = **60 s** — identical spec to `M1`, same TF |
| `gcs15x` | bb 5\|0.37\|close | 15 s — **the confirm line** |
| `gcs15m` | bb 6\|0.45\|close | 15 s — **the confirm line** |

**Divergence — the existing machine, `trade_book.py:39` config**

| knob | value |
|---|---|
| `L_DIV` | 24 bars = **120 s** — anchor/floater gap |
| `FLOOR` (`slope_floor`) | 0.5 |
| price source | raw, per `divergence_research.md` §12 |

**PINE FORMAT LOCK** — `jig._bgcolor_frag` docstring carries it. Header note → `indicator()` → one `input.bool` per stream → one `f_<name>()` per stream → array calls → `bg = color(na)` → one `if` per stream with a **LITERAL** transparency → a **single** `bgcolor(bg)`. blue 0 / yellow 0 / red 47 / green 0. **No `opac` slider.** Order is priority: later streams paint over earlier. This has been broken twice and reverted twice. Do not change it on your judgement.

---

## §5 — RUNTIMES, AND THE TWO-CACHE TRAP

| command | time |
|---|---|
| `python3 build_exhv2.py` | ~45 s |
| `python3 build_dominoes_db.py` | **1 m 47 s** (two REWALK modes; ~60 s once it is one mode) |
| `python3 emit_dominoes_pine.py` | ~50 s |
| `python3 build_exh_stat.py` | 1 m 24 s |
| `python3 report_exhv2.py` | ~1 s, DB-only |
| OOS cache build, 509 specs | 18.2 min, 2.14 s/spec |

**THE TWO-CACHE TRAP (task #13).** `build_rpl_6of9.py:41` does `R.end_ms = JUNE_END` (06-14). Anything importing it — exhv2, build_exhaust — runs on the **06-14** tape, while `rpl_walk.py:49` says **07-13**. Three hardcoded `end_ms` values exist (`rpl_walk.py:49`, `build_rpl_6of9.py:31`, `linelab.py:24`) and there is no `RPL_END_MS` override. Always print which tape you are on before trusting a number.

`RPL_TF_CEILING` env var lets a caller build L0 **once** at the ceiling it needs. Set it to `120` before importing `rpl_walk` or you pay for a ceiling-90 build then a rebuild.

---

## §6 — DATA FOUNDATION

| stretch | state |
|---|---|
| before 05-18 | **synthetic warmup.** Never analysis |
| 05-07 → 05-17 | TV 5 s replaced 0801. 193,524 rows, 100% `was_synth`, 0 inserts |
| 04-28 → 05-06 | **still missing** TV 5 s (task #22) |
| before 06-08 | `kc_volume` holds **1-minute volume replicated across 12 bars**. 100% of minutes share one value, so `evt` is blind |
| from 07-10 | true 5 s volume, 31.7% zeros |

- `kline_sanitiser.py:116` — the `UPDATE` sets `kc_open/high/low/close` and **not `kc_volume`**. The `INSERT` at `:113` does include it, but every May bar already existed so all took the UPDATE path. That is the defect behind task #21
- `evt = kline_collection.kc_volume > 0` is the **only** place volume enters the signal path (`rpl_cache.py:50`/`:100`, `rpl_walk.py:163`). It feeds `_px_smooth_evt` → `pxs` and the gcs5 finisher's event-bar tolerance
- OOS cache tape: **04-28 06:34 → 07-31 23:59**, 1,636,872 bars, evt 91.40%. The spec's `ei` = 100% figure is stale
- r120 converges by day 5-6, so **7 days of warmup is sufficient** — not the 52 days the spec asks for

---

## §7 — TASK LIST (recreate with Joe's numbering in the subject)

| # | subject | state |
|---|---|---|
| 2 | `xpred_thresh` collision: one knob, two mechanics | pending |
| 5 | delegate stage + missed-prediction edge case (DEFERRED) | pending |
| 7 | branch 1 fires only 2 of 208 | pending |
| 8 | re-run seam-alignment on real data (currently VOID) | pending |
| 9 | `xcp_origin_dwell` = 4 is live and recorded as WRONG | pending |
| 10 | bear/up-leg asymmetry that should not exist | pending |
| 11 | sell-off regime needs its own mechanic | pending |
| 12 | score delegation on excursion, not `pos_in_leg` | pending |
| 13 | solve the sell-off window during the knob sweep (**CACHE TRAP**) | pending |
| 14 | measurement-foundation guard at centroid promotion | pending |
| 15 | s3a x-cross: fall back to s4r when s3r is missing inside the r-lookback | pending |
| 16 | parallel {TF+[1,2,3]} `wob_cross` as a cross-decision assist (FLAGGED IDEA) | pending |
| 17 | band map defect: TF3 and TF 9-30 run the wrong r oscillator | pending |
| 18 | A/B: adding the s3a+x-cross finisher stage to the chain | pending |
| 19 | Jig's `line()` path bypasses the line cache and recomputes every call | pending |
| 20 | post-exhaustion MAE dialing | **in_progress** |
| 21 | `kc_volume` never repaired — event tape degenerate | pending |
| 22 | collect TV 5S for 04-28 → 05-06 (NEEDS JOE) | pending |
| 23 | PRTG `faults_5s` gate on `kc_volume > 0` (NEEDS JOE'S OK) | pending |
| 24 | close/narrow exhv2 | pending |
| 25 | jig producer consolidation + fork-2 divergences on the sweep list | pending |
| 26 | the Mage-develop hold — **PARKED** by Joe: *"we won't pull the thread any further"* | pending |
| 27 | remove the race column from the exhv2 report default | **completed** |
| 28 | s4M-cycle re-walk while s22 has momentum — **REWALK 2 is the approved default** | pending |
| 29 | map and package RPL + bp50 as-is for o9-live to prove the causal flow | pending |
| 30 | s33r curl detection — **CLOSED, not tenable live** (confirmation lag ~7 min per r-unit) | pending |
| **31** | **rebuild dominoes on REWALK 2 + gcs15 confirm** — §0 step 4 | **NEW, do first** |
| **32** | **the exit lookahead** — `held` needs 240 s of future; see §9(4) | **NEW** |
| **33** | `build_exh_stat.py:130` DELETEs unconditionally, not only under `--fresh` | **NEW** |
| **34** | `end_ms` single source of truth — 3 hardcoded values, no override | **NEW** |

---

## §8 — FILES

**Created 0801-0802, uncommitted**

| file | state |
|---|---|
| `build_dominoes_db.py` | **HALF-EDITED — finish it first** |
| `emit_dominoes_pine.py` | works; wrong signal definition |
| `build_s33curl.py` | complete; task #30 closed, method kept |
| `dominoes.pine` | emitted on the wrong signal |

**Modified, uncommitted**

| file | change |
|---|---|
| `build_exhv2.py` | `REWALK` default 2; REWALK 3/4 modes; `_derive()` helper; `momo()` lifted to module level |

**DB tables**

| table | rows | note |
|---|---|---|
| `rpl_exh_stat` | **142** | rebuilt 0801 with no `--window`, 05-18 01:35 → 06-13 06:32 |
| `rpl_exh_stat_bak0801` | 87 | the prior windowed set. **Do not drop** |
| `rpl_exhv2` | 87 | **STALE** — still the old 87-row population |
| `rpl_dominoes` | 284 | **WRONG CONFIG** — both REWALK modes, `A ungated` |
| `rpl_walkcand` | 5,212 | **WRONG CONFIG** — same |

19 files were uncommitted at `554156f`; 4 are now. Joe has not asked for a commit since.

---

## §9 — OPEN FLAGS

**(1) Every dominoes number is on the wrong signal.** The reframe below was measured on `A ungated`. Re-derive it under gcs15 confirm before repeating any of it to Joe.

**(2) The falling-dominoes finding — Joe's idea, and it held.** Strict ordering `gcs15M < s30M < s1M` by OOB→IB crossing bar, read at the signal, all crossings at/before it (causal):

| rewalk | slice | precision | base | lift |
|---|---|---|---|---|
| 2 | ALL 05-18..06-14 | 61.8% | 43.7% | 1.41× |
| 2 | OLD 05-18..06-04 | 57.1% | 39.6% | 1.44× |
| 2 | FRESH 06-04..06-14 | 83.3% | 53.7% | 1.55× |
| 0 | ALL / OLD / FRESH | — | — | 1.56× / 1.59× / 1.46× |

- beats base rate in **6 of 6** slices. Non-strict fails once (0.80×) — ties are noise, require strict
- **reverse order is an anti-signal**: 0.38× / 0.00× / 0.93×
- **the divergence half is dead** — 0.58× to 1.67×, no stable edge. Reason: dominoes rows are overwhelmingly **PM** (signs agreeing), so divergence and dominoes are near mutually exclusive; their intersection fires on 1-3 rows
- **the reframe**: on `A ungated` the non-MFE-side fires traded *better* than the MFE-side ones (win 76.9% vs 57.1%, MAE med 0.04 vs 0.21), so it looks like an **entry-quality** filter that correlates with MFE-side rather than an MFE-side detector. **Unverified under gcs15 confirm.**

**(3) `v2_mfe_side` is a misleading name.** It means *"s4Mage crossed OOB on the opposite boundary to the side the r-pred predicted"* — `mfe = int(sd != wt)`. It does **not** mean "price has already moved favourably". Joe read 05-25 18:31:25 as obviously MFE-side; the column says 0, and both are right about different things. Worth renaming.

**(4) THE EXIT LOOKAHEAD — real, live, and it inflates every trade number I produced.**

`held[z]` requires the OOB run starting at `z` to last `WALK_DWELL_BARS` = 48 bars = 240 s. That verdict is only knowable at `z + 48`. Taking the exit price at `z` uses 240 s of future.

| exit rule | n | ret med | ret mean | ret sum | win% | MAE med |
|---|---|---|---|---|---|---|
| at the crossing bar (**what I reported**) | 142 | +0.079 | +0.239 | +33.97 | 54.2 | 0.265 |
| at crossing + 48 bars (**confirmable live**) | 142 | +0.016 | +0.182 | +25.80 | **50.7** | 0.372 |

- ret sum −24%, win rate to a coin flip, MAE median +40%
- the same gate sets the walk bar, where it costs nothing (the signal comes later anyway). At the exit it is a genuine forward peek
- `build_dominoes_db.py` already banks **both** (`dm_ret`/`dm_mae` vs `dm_cret`/`dm_cmae`). Keep that

**(5) REWALK 2 may be changing the branch more than the entry.** On 05-25 r-pred 15:34:45: REWALK 0 walks to 17:06:20 (branch momo/tf22), REWALK 2 hops twice to 18:00:35 (branch s4/tf4) — **identical signal bar 18:31:25 and identical exit**. If that is common, part of REWALK 2's measured gain is branch reassignment, not entry improvement. One query against `rpl_dominoes` once it is rebuilt.

**(6) The mechanic degrades out of sample.** Best config: median MAE 0.31 → 0.56, median ratio 4.10 → 1.81, development stretch vs the 11 days after it. FRESH is only 11 days because `rpl_exh_applied` stops 06-13; the OOS cache runs to 07-31, so extending means running RPL forward on the new tape.

**(7) `over/under Moob` is still open.** `build_exhv2.py:356-362` — the strict reading (s4Mage must STILL be OOB at the cross bar) killed three days of signals, so it was reverted to a value test pending Joe's ruling. Known weakness: when s4Mage has crossed to the far side by the cross bar the test is vacuous.

**(8) `A ungated` costs signals.** 0 of 142 rows fail to produce one, but gcs15 confirm may drop rows where no gcs15 cross follows the anchor. **Count and report them.**

---

## §10 — HOW JOE WORKS

**Convo style** — the hook injects it every turn. Follow it exactly.

- short, detailed **raw-data bullets**. One fact per bullet. **Numbers first.** No connecting prose between bullets
- **tables** when comparing more than 2 dimensions. Joe has autism and reads tables far better than inline results
- **gloss every var/constant/column inline**: role + current value + units — `wob_n` = 9 bars = 45 s at the 5 s grid
- caveats get their **own bullet**. Never hedge inside a sentence
- corrections: **one bullet** stating the correction. No apology, no account of the slip, no tallying past errors
- **never coin shorthand for a mechanic.** Use Joe's words or ask him to name it
- describe mechanics in **data terms** (lines, thresholds, crosses), not trading stories

**The two mandatory closers, in this order, on every substantive reply**

1. **Summary** — ONE paragraph of prose tying the bullets together. Carries the *meaning*, not a re-list
2. **PnL impact** — opens with a `TL;DR:` one-liner giving the verdict alone, then direction, rough size, and what would have to be true for it to hold. Say "no effect" or "unknown" when that is honest. Never pad

**Behaviour**

- **"I can't believe that" is data.** Joe catches real errors. Go and check rather than defending
- **Joe cannot see tool output.** Paste the actual content into the message
- **hand the conclusion back to the artefact.** When Joe challenges a claim, the defensive move is to migrate ownership from the artefact to your own assertion. Don't. Go and re-read the artefact
- **a stored memory is a claim you have not yet earned.** When you read one, go find the current instance of that failure in your own output
- Joe answers concretion lists tersely — `1 a) / 2 all 4 lines / 3 exhv2 / 4 clone s30r`. Number your questions so he can

**Things I got wrong this session, so you don't repeat them**

- built the whole dominoes dataset on `A ungated` when `gcs15 confirm` was already approved, and banked both REWALK modes — Joe: *"we can't be using both"*
- wrote *"that's the ambiguity that just cost you"* about a defect in **my** emit. It read as blame
- emitted a 700-character single-line pine header with the colour legend buried 230 chars in, when the emitter has supported multi-line notes all along
- quoted REWALK 2's walk bar without naming the mode, when Joe was reading REWALK 0's
- printed `v2_race_ms` (tuple index 33) and called it the r-pred
