# Bias Machine — Spec

status: **building** — walking Joe's OG timeline entry-by-entry to derive the rules.
started 0615. Joe's words are canonical; Claude's discovery is supporting context, kept
separate. Companion: `bias_machine_overnight_0615.md` (Claude's scan findings).

---

## Preamble (Joe's words, verbatim — 0615)

```
BIAS MACHINE
bias is set by 22a
- we place pyramid trades along the bias line

every TF except 7 has the same s30 config
- m:10|0.4|hlc3
- M:37|0.72|ohlc4
- r:5|6|6|hl2
TF7 has a doubled config, and is referred to as s14
- s14 config (TF7)
-- m:20|0.77|hlc3
-- M:74|0.72|ohlc3
-- r:10|12|12|hl2
- s14 might not be used in this machine. TBC

s18
- m:18|0.65|hlc3
- M:111|0.74|ohlc4
- r:5|6|6|hl2

the use of 'a' (eg s30a, s2a)
- a is 'all'. all 3 lines: m, M, and r
-- there are no b's in this machine

trades are initiated by (s2m+M or s2m+r) +s30a +pk signal
- note I don't have pk signals. for now, we will treat s30m wobble slayer as c_bls3,
  and build a pk detection window around it

important concept to understand. if an M line stays near one boundary (eg high), and the
m+r are breaching at the other boundary (ie low), the trend is LONG.
- M in solidarity near a boundary creates gravity

all calculations are based on the closed bar value, not the emerging value
```

---

## Corrections to Claude's prior interpretation (0615)

- **bias is set by `s22a`** — NOT "s22a + s18a" as I'd written. s18 has its own config but
  is not stated as a bias-setter here.
- **s22 REVERSALS are the primary mover.** M-gravity is a *concept to learn*, NOT the
  lynchpin — I over-weighted it overnight. Re-centering on s22 reversals.
- **s18 config = m:18|0.65|hlc3, M:111|0.74|ohlc4, r:5|6|6|hl2** (on TF6) — supersedes both
  my "TF6 ×3 of the centroid" guess AND the existing-s18 (k 12/66/147) config.
- **PK signal is not built yet** — stand-in = the s30m wobble_slayer treated as c_bls3,
  with a pk detection window around it.

## Resolved (0615)

- **s30 = EMERGING in prod; all other TFs = CLOSED bars.** (Pen tests may use closed s30
  for convenience.) Resolves the closed-vs-emerging fork.
- **s30r and s6r source = `close`** (were hl2). [scope TBC: all r lines, or just these two?]

## Open forks (resolve before/while walking)

1. **What IS an "s22 reversal"** (the primary mover)? Which line reverses — s22r (the K
   turn-detector), s22m, or s22a — and from what state (OOB? a boundary)?

## ⚠️ PARKED — bar timestamp convention (close vs open)  [0616]

**Our tooling labels bars by CLOSE time; TV labels by OPEN time** → a constant offset
(e.g. our `22:29:00` closed bar = Joe's `22:28:30` on TV). We are **keeping close-time**
(switching to open-time risks wrong realtime behaviour — the bar isn't closed at its
open). So when comparing our scripts to a TV eyeball, **expect ~one-bar timestamp
disagreement** even when the values agree. **If we hit bias-machine problems that look
like a mismatch, RE-OPEN this.** Separately: at 30s in volatile chop, our 5s→30s resample
diverges from TV's native-30s OHLC by ~6–9 pts (the known tape-vs-TV issue) — tape is the
arbiter, not bar-by-bar TV parity.

## Dynamic-p_c s6 PK (rule, locked 0615)

A "reliable s6 PK" via an event-anchored s6r divergence. All on the SAME side S.
- **Gate:** s14M OOB (side S) — gates the ANCHOR sample only (latched, not retested
  elsewhere). s14M = TF7 BB 74|0.72|ohlc3 (≡ohlc4).
- **Anchor:** while s14M OOB(S), at an s6m breach(S), the first time **s30a prints an
  **s30M** wobble_slayer(S)** (Major, *not* m — kills solo-min twitches) → capture **s6r**.
- **Floater:** the **previous same-side s6m breach** (s14M disregarded there). Work
  BACKWARDS from the anchor → the **LAST** s30a-s30M wobslay(S) before that breach ends
  (not the first) → capture s6r.
- **s30a requirement (0616):** a qualifying wobslay needs **all three s30 lines (m, M, r)
  OOB on side S at the s30M EXTREME** (the trough/peak, i.e. 2 bars before the 2-bar
  confirmation). Without it, near-boundary s30M twitches fire spurious wobs. Applies to
  BOTH anchor and floater. wobslay fires/samples at the confirmation bar (realtime-honest).
- **Signal:** anchor > floater → **bullish**; floater > anchor → **bearish** (absolute,
  side-independent — s14M only chooses where the *anchor* is sampled).
- "dynamic p_c": the floater lookback is the *previous breach event*, not a fixed N bars.
- wobble_slayer(S) = 2 bars off the OOB extreme (hi: peak≥85 then c<b<a; lo: ≤15 then c>b>a).
- PK stand-in note (preamble): no real pk yet — s30M wobslay treated as c_bls3.
- **Tooling:** `bias_pk_pentest.py` (numeric trace) + `bias_pk_pentest.pine` (15s viz).
  First pen test window 0610 2012→0230: 4 anchors (BEAR/BULL/BEAR/BULL).

## Validated foundation (Claude's discovery — detail in overnight doc)

- **native value = the closed bar read at its close boundary (HH:MM:00)** — matches your TV
  prints; m & r to the decimal.
- HTF lines need **~160h warmup** to converge (RSI/STC).
- M mult per-TF (0614): s2M/s22M = 0.83, s6M = 0.72. **s22M still reads ~+10 high vs TV —
  parked** (config mismatch, not warmup).
- data source = **`kline_collection`** (5s base tape; via KlineLoader.load_window).

---

## Reporting / tooling

- **`bias_pk_validate.py`** — 96/168h validation. Per gated bias print: *run-up to the
  adversarial swing* (favourable excursion to the first counter-bias ZigZag pivot) +
  *profit to the next s14M OOB reversal*.
- **`bias_pk_backtest.py`** — trades the bias prints over the last 7d. ENTRY = the next
  aligned s30a+s30M wobslay after the print (BEAR→hi reversal, BULL→lo); EXIT = the
  opposite s6m+s30a+s30M confluence. 33K lots · 50x · Bybit taker 0.11% rt · 1000 USDT
  start. Runs two gate modes: **s14M OOB** and debug **s14M vs 50**.
- **`bias_pk_trades`** (db table) — per-trade ledger, one row per (gate_mode, trade):
  `gate_mode, print_time, entry_time, exit_time, direction, exit_reason, entry_px,
  exit_px, lot_coins, notional_usd, leverage, margin_usd, fee_usd, pnl_usd,
  pnl_margin_pct, balance_usd`. `balance_usd` runs per gate_mode; filter on `gate_mode`.

## Rules from the timeline
*(built as we walk each entry — to follow)*

---

## Engine architecture & DB integration (0619–0620)

Engineering layer for the beta engine `bias_machine.py` (first consumer: the pk grinds + `bias_pk_emit.py`).

### SRP split of the pk path (done, parity-gated)
`ups()` conflated event-construction with verdict. Split into single-responsibility methods:
- **`pk_events(trigs, gate, flt_half=2, floater_src='same')`** — the anchor/floater EVENT stream only,
  no call. Owns wrong-side drop, s14M/s14r gate, floater sourcing + location. Knobs:
  `flt_half` (2 = ±2-bar min/max scan · 0 = no scan, raw osc at the source bar · None = legacy
  rolling-avg) and `floater_src` (`same` = last same-side anchor `g[S]` · `last` = last anchor of
  ANY side, single `g` slot — the 0612 PM-suppression rule).
- **`verdict_magnitude(events)`** — call by `|anchor − floater|` band (the current pk-update call).
- **`verdict_pk(events, slope_floor, delay, …)`** — call by the pk machine over the FULL event stream
  (`_pk_state_from_slopes`: same-sign slopes → PM ±2 → single-line `pk_raw=0` suppress; opposite → DIV
  ±1 fires). No pre-filter coupling.
- **`ups()`** kept as `verdict_magnitude(pk_events(...))` — behaviour-identical, and the future **SnF**
  (Support & Friction) meld seam. `pk_feed()` kept as a back-compat wrapper (pre-filter → `verdict_pk`).
- Coverage: `tests/test_bias_machine.py` — golden-master (frozen window 1781753040000, DB-free fixture
  in `tests/fixtures/`, regen via `tests/_gen_bias_golden.py`) + synthetic units.

### Lines are DB-sourced — no hardcoding (0620)
All bias lines live in `indicator_configs`, resolved through the live view (no tuples).
- **`vw_indicator_configs_live`** (renamed from `indicator_configs_live`, 0620): current line per
  `(series, line, timeframe)` via `MAX(ic_live_after_dt) ≤ now()`. **`ind_name` fixed** to
  `CONCAT(is_prefix, itf_label, il_suffix)` (was `prefix+suffix`, which collided every TF of a series).
  Durable source: `optimus9/sql/views/vw_indicator_configs_live.sql`.
- **Seeder** `seed_bias_lines.py` (idempotent): added series `mo`/`xm`, the 45s timeframe, and 12
  configs — `s12m`(720), `s14M/m/r`(420), `s3m`(180), `s30M/m/r`(30), `mo12m`(720), `xm45m/M/r`(45).
  `s30M`(0.72) and `s30r`(6\|6\|5) are **new versions** (`live_after_dt` 2026-06-20) that supersede the
  epoch prod rows — these were an earlier BL-grind suggestion; supersede is global-by-design.
- **Caller rule:** resolution-by-name → the view (`bl_detect` predictor lookup, `goal_alignment` gate);
  provenance joins by stored `ic_pk` and writes stay on the base table (the view hides superseded rows).
  `goal_alignment.DEFAULT_GATE` updated to the corrected names (`bny30M`/`bny30p`).

### Config-driven engine (built 0620)
- **`LineStore(db)`** — SRP DB resolution: `ind_name → (tf_seconds, cfg-tuple)` from
  `vw_indicator_configs_live`. Building (resample/align) stays with the window.
- **`BiasConfig`** dataclass = single source of truth for one run: line refs (by `ind_name`) +
  mechanism knobs (`osc`, `gate`, `floater_anchor`, `flt_half`, `verdict`, `entry_order`, `s3_variant`,
  `xm45`, `mae`, `target`, `xm45r_lookback`, `trigger_tf`). Defaults reproduce the pre-config engine.
- **`BiasWindow(db, end, cfg=BiasConfig())`** builds every named line live from the DB via `LineStore`
  (`_line(ind_name)`) — **no tuples**. All 15 bias lines seeded (`seed_bias_lines.py`) + line-parity
  byte-identical to the old tuples; the config-driven path reproduces the golden master and the
  cascade emit (weakest window 35 trades / 11 correct) exactly.
- **Consumer entry-point `BiasWindow.signals()`** = `trigs(cfg.trigger_tf) → pk_events(cfg knobs) →
  verdict(cfg)`. `verdict(events)` dispatches on `cfg.verdict` (magnitude | pk) — the consumer feeds
  the event stream and the CONFIG picks the verdict, never a baked-in call. `cfg.floater_anchor` and
  `cfg.verdict` are live through this path (the `ups()` wrapper is magnitude/same only — back-compat).
- `bias_pk_emit.py` consumes `BiasConfig` via `W.signals()` (no `set_osc`/`set_entry`, no hardwired
  `ups()`). Those mutators remain as deprecated shims for the not-yet-ported grinds.
- **Flagged remaining tuple:** the generic `tf()` arbitrary-TF sweep (GEN_M/GEN_R at any TF) — the old
  exploratory path, not DB-driven (would need every TF seeded). Trigger uses it but is parity-identical
  (GEN_M@720 ≡ seeded `s12m`).

### Results infra (built 0620)
- **`bias_results.BiasResults`** (SRP persistence): `bias_config` ← `bias_eval` ← `bias_pk_results`.
  `bias_config` columns are **introspected from `BiasConfig`** (auto-migrated when a field is added);
  code (str) columns are case-sensitive (`utf8mb4_0900_as_cs`). MySQL column names are case-insensitive,
  so the `_M`/`_m` line refs map to `_maj`/`_min` columns (`_col()`); the `BiasConfig` field keeps `_M`/`_m`.
- `bias_eval` = one row per (config × window) with `cfg` FK, window bounds, `run_ts`, `engine_rev`
  (md5 of `bias_machine.py`). `bias_pk_results` = the pk mechanic's `correct`/`total`, FK eval.
- **Future mechanics (line positioning, line cross) land as SIBLING tables** under the same `bias_eval`.
- **Stored snapshot (Joe 0620):** the floater×verdict×g_gated sweep (8 configs × 9 windows) is in the
  tables, all `live_after=now` — current/live, **no single winner promoted** (bias-pk holding pattern;
  pk's sparser stream is the bet, pending line positioning filling the gaps).

### blp line-positioning mechanic + the resample-anchor bug (0620)
New mechanic (sibling to pk): emerging blp14 line crossovers under a confluence cascade.
- **blp14** = clone of s14 (TF7) seeded under series `blp`, built **emerging** (`_line_emerging` →
  `f_*_lookahead`, the developing bar per 5s, sampled every 60s via `blp14()`). `s22` (TF22, the real
  bias decider) also seeded.
- **`blp_crosses()`** — any-pair (m×M, m×r, M×r) crossover on the 1-min samples → (pair, before/after).
- **`blp_signals(wob_tol_min=2)`** — cascade v2 (Joe 0620): at each s30M wob (side S), require ANY s22
  line OOB · xm45a · a blp14 **m×M** cross (both OOB) within ±2min; s14M = annotation not gate ('GATED'
  if IB); colour per s14M side; gravity if blp14M/s22M on the other side of 50. Pine emit = TODO.
- **RESAMPLE-ANCHOR BUG (found + fixed):** `IC.resample`/`lookahead_resample` were **epoch-anchored**
  (420s bars open at min-of-day ≡3 mod 7); TV anchors to **UTC midnight** (≡0 mod 7). 3–4 min phase
  drift scrambled the developing bar → big errors on fast moves. Fix: `IC._bar_open(ts, tf, anchor)`
  flow function + `anchor='epoch'|'midnight'` threaded through resample/lookahead_resample/
  f_bb_lookahead/f_k_lookahead (default epoch → **live BL path untouched, suite green**). `_line_emerging`
  uses `anchor='midnight'`. TODO: source the anchor from a DB column, not a hardcoded default.
- **Result vs Joe's TV (4 points):** the anchor fix lands **blp14r** (was +12 off, now <1). **blp14m/M
  (BB) still off ~5–17** — isolated to the **parked "s22M reads ~+10 high vs TV (config mismatch)"**
  (blp14M = s22M-doubled, inherits it). NOT a new bug. Cross-check (Joe's 5): r-driven crosses land,
  m/M-driven ones (04:12, 06-13 01:03 "all 3") miss — downstream of the parked s-M gap.
- **Next:** resolve the parked s-M BB-vs-TV config gap (needs TV's exact BB config/rescale for the M
  line) — the one thing between here and clean blp14 crosses. Joe's blown-up TF1 ×7 alt was tried
  (closed f_bb on 60s); r worse, m/M no better — not the fix.

### pk-mechanic findings (0620)
- `g_gated=True` (gate the floater `g`-update by s14M) is a small net win on the baseline
  (same/magnitude 42→43%, 6/9→7/9 windows, fewer/cleaner trades). The 0617 "g ungated" rule is the A/B off-switch.
- `last`+`pk` fixes the eyeballed bad signals (0612 08:24 / 11:12) and holds the rate (~42%) but on ~1/3
  the volume — pk only fires on osc-vs-price divergence (PM = osc & price agree → suppressed). Held as A/B.
