# Handover — 2026-08-02

Branch `causal/lookahead`. Last commit `ff67d7d` *bp50: dominoes filter + the 0802 handover*.

**If you read nothing else: go to §0 step 4. It is your first job, Joe has already approved it, and it is
written out in full — the broken state, the fix, and the code. Nothing about it needs asking.**

---

## §0 — START HERE, FOUR STEPS

**Step 1.** Read the §1 REQUIRED list. Nothing else first.

**Step 2.** Recreate the task list from §7, using Joe's numbering in the subject line.

> The §7 rows are **subjects only**. They are not the instructions. Every task's body lives elsewhere in
> this doc — for **#31, the first job, the body is §0 step 4 below and it is complete**: what is broken,
> what the fix is, and the code to write. Do not open #31 expecting a spec somewhere else.

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

**Read when touched** — all verified to exist 0802

`docs/rpl_flow_spec.md` · `docs/linelab_spec.md` · `docs/bp50.md` · `docs/causal_lookahead_register.md` · `docs/rpl_sweep_spec.md` · `docs/rpl_event_store_spec.md` · `docs/o9_live_design.md` · `docs/quirks_to_remember.md` · `docs/task_register.md` · `docs/measure_before_verdict.md`

- there is **no** `divergence_research.md` in the repo. The divergence contract lives in the code:
  `jig.py:266` `pk_state()` docstring and `pk5s_gate_computer.py:285` `_pk_state_from_slopes`.
  The "price source is raw" convention is stated in the `pk_state` docstring
- there is **no** `bl_detect.md`, `pine_format.md`, `kline_sanitise.md` or `o9_live.md`. The pine
  format lock lives in the `jig._bgcolor_frag` docstring; the sanitiser contract in
  `optimus9/data/kline_sanitiser.py`

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

**IT BITES AD-HOC SCRIPTS TOO.** Measured 0802:

| import order | tape L0 carries |
|---|---|
| `import optimus9.orchestration.rpl_walk` alone | 05-22 08:00:00 → 07-12 23:59:55, 892,800 bars |
| `import build_exhv2` first, then `rpl_walk` | **04-28 06:34:00 → 06-13 23:59:55, 807,432 bars** |

- any script querying `rpl_dominoes` / `rpl_exhv2` and indexing into `R.L0['ts']` **must import `build_exhv2`
  first**, or every row before 05-22 08:00 silently maps to bar index 0
- that is 29 of the 142 `rpl_dominoes` rows. `np.searchsorted` returns 0 without error, so the failure is
  silent and looks like real data
- `build_dominoes_db.py`, `emit_dominoes_pine.py` and `report_dominoes.py` are all safe — the first two import
  `build_exhv2` at module level, the third never touches `L0`

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
| **31** | **COMPLETED 0802.** 142 anchors → 142 confirmed signals, 0 dropped; confirm lag med 2.38 min. `rpl_dominoes` 142 rows, `rpl_walkcand` 3,029, one mode. §9 re-derived by `report_dominoes.py` — the strict-dominoes lift falls 1.41× → **1.21×** ALL and **0.93×** FRESH. Original body: **rebuild dominoes on REWALK 2 + gcs15 confirm.** Three artefacts are on the wrong signal (`A ungated`, the raw s15x × s15m cross) and two are banked for both REWALK modes. (a) `build_dominoes_db.py` — `:137` `for mode in (0, 2)` → `(2,)`; `:147` `ro[I['sig']]` is the ANCHOR, advance to the first gcs15x × gcs15m cross at/after it; add `dm_s15x_ms`/`dm_s15x_utc`; count and print rows with no gcs15 cross. (b) re-run it — it DROPs and recreates `rpl_dominoes` / `rpl_walkcand`. (c) same change in `emit_dominoes_pine.py`, re-emit. (d) re-derive every §9 number. **Full body + the code: §0 step 4.** Joe has approved this; no discussion needed | **COMPLETED** |
| **32** | **the exit lookahead** — `held` needs 240 s of future; see §9(4) | **NEW** |
| **33** | `build_exh_stat.py:130` DELETEs unconditionally, not only under `--fresh` | **NEW** |
| **34** | `end_ms` single source of truth — 3 hardcoded values, no override | **NEW** |

---

## §8 — FILES

**Created 0801-0802, uncommitted**

| file | state |
|---|---|
| `build_dominoes_db.py` | **DONE 0802.** One mode (2); anchor→gcs15-confirm advance; `dm_s15x_ms`/`dm_s15x_utc`; drop count printed |
| `emit_dominoes_pine.py` | **DONE 0802.** Same confirm advance, same drop count, legend rewritten |
| `report_dominoes.py` | **NEW 0802.** DB-only. Re-derives §9: confirm lag, detector lift on 3 slices, the exit-lookahead table, the reframe |
| `build_s33curl.py` | complete; task #30 closed, method kept |
| `dominoes.pine` | re-emitted 0802 on the confirmed signal |

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
| `rpl_dominoes` | **142** | rebuilt 0802 — REWALK 2 + gcs15 confirm, one mode. `dm_rewalk` is 2 on every row |
| `rpl_walkcand` | **3,029** | rebuilt 0802 — same config |

- the prior 284 / 5,212 `A ungated` rows were **not** snapshotted before the DROP. Their headline figures survive in §9 as struck-through values

---

## §9 — OPEN FLAGS

**(1) RESOLVED 0802 — every number below is now on REWALK 2 + gcs15 confirm.** Re-derived by `report_dominoes.py` off the rebuilt `rpl_dominoes` (142 rows, one mode). The `A ungated` figures are struck through where they moved.

**(1a) The confirm costs 0 signals.** 142 anchors → 142 confirmed signals, **0 rows dropped** for want of a gcs15 cross. §9(8) is answered.

- confirm lag `dm_sig_ms − dm_s15x_ms`: **med 2.38 min, mean 2.76 min, min 0.00, max 10.92**
- **10 of 142 rows have zero lag** — the gcs15 cross lands on the same bar as the s15 anchor

**(2) The falling-dominoes finding — it does NOT hold up under the confirm.** Strict ordering `gcs15M < s30M < s1M` by OOB→IB crossing bar, read at the signal, all crossings at/before it (causal). REWALK 2 + gcs15 confirm:

| slice | n | base | strict n | precision | lift | ~~was (A ungated)~~ |
|---|---|---|---|---|---|---|
| ALL 05-18..06-14 | 142 | 43.7% | 34 | 52.9% | **1.21×** | ~~1.41×~~ |
| OLD 05-18..06-04 | 101 | 39.6% | 24 | 54.2% | **1.37×** | ~~1.44×~~ |
| FRESH 06-04..06-14 | 41 | 53.7% | 10 | 50.0% | **0.93×** | ~~1.55×~~ |

- **FRESH is now BELOW base rate** (0.93×). The `A ungated` reading had FRESH as the strongest slice at 1.55×. That inversion is the headline
- loose (`<=`) is now indistinguishable from strict: 1.22× / 1.33× / **1.00×** on n = 49 / 36 / 13. The "ties are noise, require strict" rule no longer separates anything
- **reverse order is still a clean anti-signal**: **0.00× on all three slices**, n = 4 / 2 / 2. Precision 0.0% every time
- base rate is unchanged at 43.7% by construction — `dm_mfe_side` is set at the walk bar, which the confirm does not move. That is the consistency check that the rebuild landed
- **the divergence half is dead** — 0.58× to 1.67× on `A ungated`, no stable edge. Not re-derived; the reason still stands (dominoes rows are overwhelmingly **PM**, signs agreeing, so the intersection fires on 1-3 rows)
- **the reframe is REVERSED.** On `A ungated` the non-MFE-side fires traded better (win 76.9% vs 57.1%). Under gcs15 confirm the MFE-side fires are the better ones:

| strict fires | n | win% | ret med | MAE med | live-exit win% | live ret med | live MAE med |
|---|---|---|---|---|---|---|---|
| MFE-side | 18 | 66.7 | +0.129 | 0.193 | **55.6** | +0.010 | 0.291 |
| non-MFE-side | 16 | 62.5 | +0.102 | 0.074 | **43.8** | −0.080 | 0.242 |

- on the live-confirmable exit the non-MFE-side fires **lose** (43.8% win, ret med −0.080). The entry-quality reading does not survive the confirm
- non-MFE-side still carries the lower MAE median (0.074 vs 0.193) — lower excursion, worse return

**(3) `v2_mfe_side` is a misleading name.** It means *"s4Mage crossed OOB on the opposite boundary to the side the r-pred predicted"* — `mfe = int(sd != wt)`. It does **not** mean "price has already moved favourably". Joe read 05-25 18:31:25 as obviously MFE-side; the column says 0, and both are right about different things. Worth renaming.

**(4) THE EXIT LOOKAHEAD — real, live, and it inflates every trade number I produced.**

`held[z]` requires the OOB run starting at `z` to last `WALK_DWELL_BARS` = 48 bars = 240 s. That verdict is only knowable at `z + 48`. Taking the exit price at `z` uses 240 s of future.

Re-derived 0802 under REWALK 2 + gcs15 confirm:

| exit rule | n | ret med | ret mean | ret sum | win% | MAE med |
|---|---|---|---|---|---|---|
| at the crossing bar (**lookahead**) | 142 | +0.149 | +0.268 | +37.99 | 62.7 | 0.235 |
| at crossing + 48 bars (**confirmable live**) | 142 | **−0.026** | +0.223 | +31.60 | **49.3** | 0.332 |

- ret sum −17%, win rate **below** a coin flip, MAE median +41%, **ret median goes negative**
- the confirm improved both columns against `A ungated` (lookahead ret sum +33.97 → +37.99, live +25.80 → +31.60; MAE med 0.265 → 0.235 and 0.372 → 0.332) but did **not** close the gap between them
- ~~on `A ungated`: 54.2% / 50.7% win, ret sum +33.97 / +25.80, MAE med 0.265 / 0.372~~
- the same gate sets the walk bar, where it costs nothing (the signal comes later anyway). At the exit it is a genuine forward peek
- `build_dominoes_db.py` already banks **both** (`dm_ret`/`dm_mae` vs `dm_cret`/`dm_cmae`). Keep that

**(5) REWALK 2 may be changing the branch more than the entry. STILL OPEN, and now harder.** On 05-25 r-pred 15:34:45: REWALK 0 walks to 17:06:20 (branch momo/tf22), REWALK 2 hops twice to 18:00:35 (branch s4/tf4) — **identical signal bar 18:31:25 and identical exit**. If that is common, part of REWALK 2's measured gain is branch reassignment, not entry improvement.

- the rebuild banks **one mode only**, so `rpl_dominoes` can no longer answer this with a query. It needs its own REWALK 0 run into a separate table, or it stays on the 05-25 hand-trace

**(6) The mechanic degrades out of sample.** Best config: median MAE 0.31 → 0.56, median ratio 4.10 → 1.81, development stretch vs the 11 days after it. FRESH is only 11 days because `rpl_exh_applied` stops 06-13; the OOS cache runs to 07-31, so extending means running RPL forward on the new tape.

**(7) `over/under Moob` is still open.** `build_exhv2.py:356-362` — the strict reading (s4Mage must STILL be OOB at the cross bar) killed three days of signals, so it was reverted to a value test pending Joe's ruling. Known weakness: when s4Mage has crossed to the far side by the cross bar the test is vacuous.

**(8) CLOSED 0802 — gcs15 confirm costs no signals.** 142 anchors → 142 confirmed signals, 0 dropped. `build_dominoes_db.py` and `emit_dominoes_pine.py` both count and print the drop figure; it is currently 0. See §9(1a) for the lag it does cost.

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
