# Epoch vs Midnight Anchor — Spec & Gremlin Register

**Purpose:** one place that nails *how HTF bars are anchored*, every call-site that decides it (the hooks),
and every way it has bitten us (the gremlins) — so we converge on a reliable, TV-matching foundation.

## The problem, in one line
Resampling the 5s tape into higher-TF bars can anchor the grid two ways: **epoch** (floor to the tf grid from
1970) or **UTC-midnight** (re-anchored each day). **TradingView uses midnight.** For TFs that don't divide a day
evenly, the two grids differ — so an epoch-anchored line sits ~minutes off the chart and never matches.

## Mechanism (`IndicatorComputer`)
- `_bar_open(ts, tf, anchor)`: `'epoch'` = `(ts // tf) * tf`; `'midnight'` = `day + ((ts-day)//tf)*tf`.
- **Identical when `86400 % tf_seconds == 0`** (day-divisor TFs: 30/120/180/240/360/960s …). **They differ only for
  non-divisor TFs** (420s/7m, 1320s/22m, 1980s/33m …). → the bug is invisible on divisor TFs and only bites when a
  non-divisor line is read.
- TV anchors intraday bars to the session = UTC-midnight for 24/7 perps. **midnight = TV-matching; epoch = off-grid.**

## Affected lines (live, non-day-divisor TFs — the only ones that ever move)
| TF | seconds | lines |
|----|---------|-------|
| 7m | 420 | `blp14M/m/r` · `s14M/m/r` · `s7r` |
| 22m | 1320 | `s22M/m/r` |
| 33m | 1980 | `hbhi33` · `hblo33` · `hbhl33` (bro-cross sets) |

Everything else (s30, s2/3/4/6, hb16 …) is **byte-identical** under either anchor.

## The hooks (every place an anchor is decided)
| call-site | anchor | path | status |
|-----------|--------|------|--------|
| `IC.resample` / `_bar_open` / `lookahead_resample` | default `'epoch'` | the root resamplers | default is the trap |
| `IC.f_bb_lookahead` / `f_k_lookahead` (438/508) | default `'epoch'` | line compute (closed+developing) | default is the trap |
| `bias_machine._raw` (164) | **`'midnight'`** | bias closed `_line` | **FIXED 2026-06-30** (was epoch) |
| `bias_machine._line_emerging` (179) | `'midnight'` | bias emerging | OK (blp fix 0620) |
| `bl_detect` (408) | `'midnight'` | bl **closed** | OK |
| `bl_detect` (415-416) | default `'epoch'` | bl emerging/default | ⚠ non-divisor bl lines drift |
| `indicator_monitor` (74/88) | default `'epoch'` | live line monitor | ⚠ (see live-BL note) |
| `optimizer_runner` (418) | default `'epoch'` | optimizer p-rev line | ⚠ if non-divisor |
| `report_manager` (119/153), `gate_sweep_runner` (66), `goal_alignment` (171), `pk5s_gate_computer` (274) | default `'epoch'` | various | ⚠ if non-divisor |
| `gate_signal_sweep` (101/119) | default (30s) | gate | safe (divisor) |

## The gremlins
1. **Epoch is the DEFAULT.** Every caller that forgets the arg drifts off-grid. This is the root gremlin — the safe
   default should be midnight; epoch should be the *explicit* exception.
2. **Divisor-TF masking.** Divisor TFs hide the bug; it only surfaces when a 7/22/33m line is used — so it lands late,
   in a specific line, looking like a line-value bug rather than an anchor bug.
3. **closed-vs-emerging split.** The *same* line's closed and emerging values anchored differently
   (`_line` epoch vs `_line_emerging` midnight) → its closed and emerging crosses sat on different grids. Fixed for
   the bias machine 2026-06-30; `bl_detect` still mirrors the split (408 midnight vs 415-416 epoch).
4. **Lineage.** `constants.py:15` records an earlier `f_bb_lookahead` default bug (a rescale-slot default) — same
   family of "the default bit us."
5. **The one legit epoch consumer:** the **live BL path** (realtime 5s grid). Any global flip must leave it on epoch
   *explicitly*.

## Immediate fix (2026-06-30)
`bias_machine._raw` (164): `IC.resample(self.base, tf_sec)` → `IC.resample(self.base, tf_sec, 'midnight')`.
Closed bias lines now on the TV grid (verified: hb33 closes at 00:33/01:06/01:39/02:12). Emerging was already
midnight. Divisor-TF lines unchanged.

## The reliable foundation (the eventual nail — staged, each its own task)
1. **Invert the default** to `'midnight'` across `resample` / `_bar_open` / `lookahead_resample` /
   `f_bb_lookahead` / `f_k_lookahead`. TV-grid becomes the safe default; you can't drift by forgetting.
2. **Make the live-BL path pass `'epoch'` explicitly** (the one consumer that needs it) before #1 lands.
3. **Source the anchor per-line from the DB** (the `_line_emerging` TODO) — a line's grid becomes config, not a
   hardcoded literal (no-hardcode rule).
4. **Audit every hook** in the table above; set each explicitly per its path (indicator → midnight, live-BL → epoch).
5. **Re-validate** any grind/tuning produced on the previously-epoch non-divisor lines (s14/s22/blp/hb33).
