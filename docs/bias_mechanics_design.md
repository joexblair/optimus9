# Bias machine additional mechanics (#37)

**Why:** the confluence dataset proved the bias signal isn't strong enough to confluence lines against
(s12m → 12 trades, prox/mfe rarely align). Strengthen the bias STATES first. Six mechanics; **bro-cross
is specced below**, the other five are stubs (interrogate each before building).

## Architecture (locked)
- The five new mechanics sit at the **`bias_pk` layer** — peer producers, NOT inside bias_pk. `bias_state`
  consumes their signal streams (it depends on bias_pk + consumes its signals today; same seam).
- **SRP: over-engineer it.** While the hood's up, review + refactor the bias_machine classes freely.
  Each mechanic = its own producer; never bake a verdict into the event stream — emit events, let
  bias_state apply the verdict.
- **All config in the DB.** Tolerances → `lp_config`. Indicator sets → `indicator_configs` (versioned via
  `ic_live_after_dt`). No hardcodes.

## Mechanic: bro-cross (the "b series" = bronto 🦕)
**Producer of a bias direction**, consumed by bias_state. Trigger = the first OOB **M×m** (mage×minion BB)
crossover across four hb16 sets:
- **lo-breach → BULL**: hb{set}16m crosses OVER hb{set}16M (minion over mage), both OOB-low.
- **hi-breach → BEAR**: hb{set}16M crosses OVER hb{set}16m (mage over minion), both OOB-high.
- Whichever set crosses **first** creates the new bias direction.
- **Wobslay**: TF16 ⇒ chop expected at the crossover; both M and m use a wobslay tol = `lp_bro_wob` (12 × 5s
  bars) per set.
- **`hb16` triggers the mechanic** (the canonical set; the other three are src-variant lenses).

### The 4 hb16 sets (all itf_pk=20 "16"/960s; configs Joe-supplied, authoritative — overwrite DB)
| set     | is_prefix | M (bb, 19│0.64) | m (bb, 13│0.68) | b (k 7│74│29 hlc3) | p (k 7│77│73 close) |
|---------|-----------|-----------------|-----------------|--------------------|---------------------|
| hb16    | hb (8)    | **close**       | ohlc4           | yes                | yes                 |
| hbhl16  | hbhl (new)| hl2             | ohlc4           | — BB only          | —                   |
| hblo16  | hblo (new)| low             | low             | — BB only          | —                   |
| hbhi16  | hbhi (new)| high            | high            | — BB only          | —                   |

- `hb16` reconfigure vs today's DB: M src `hl2→close`, b k_len `5→7` (m, p already match).
- Only `hb16` keeps b+p; hbhl/hblo/hbhi are **M+m BB-only**.

## Cascade change (the first-trade metric — TEST scaffolding, not the live trade machine)
`s6m gate → xm45a → gcs15a → xm45min wob`  (was: `s3m → s30a → s30M wob`)
- gate: **s3m → s6m** (A/B later: s6m vs 4-of-6 s3+s6 OOB; start by just moving to s6m).
- `s30a → xm45a`; **gcs15a inserted as a 3rd stage**; wob `s30M → xm45min`.
- `xm45a` / `gcs15a` = all lines of that set OOB together ('a' = all).

## gcs15 (new set, TF=15s, itf_pk=2)
Copied from s30 (M ohlc4 / m hlc3 / r k5│6│6 close), is_prefix `gcs` (6). **`gcs15r` uses the
`lp_s30r_lb` lookback logic.** Wire in now to see impact on bl_review. May land in the trade-gate config.

## Value-construction mode (structural — DONE 0625)
Per-line **closed vs emerging** toggle, a 4th indicator-config dimension (not `lp_`): `indicator_value_modes`
(1=closed TV-verbatim/stable, 2=emerging intrabar/realtime) + `ic_ivm_pk` on indicator_configs →
`value_mode` in the view. Default `closed`. **Declarative only until each consumer is wired to read it**
(behaviour-preserving). Subsumes #33 (now the BL-consumer-wiring instance). Use: flip a line to `closed`
for TV-verbatim review or specific realtime lines; rest stay as chosen. New hb16/gcs15 sets pick a mode at
creation. [[project_blp_line_positioning]] blp14 = a known emerging line to flag when wiring.

## DB rows to create
- `indicator_series`: +`hbhl`, +`hblo`, +`hbhi` (next free is_pk). ⚠ **gcs15 reuses existing `gcs` (is_pk 6)**
  — so 3 new is_pk, not 4 (Joe said "4 new is_pk incl gcs15" — flag: did you mean 4 new line-SETS?).
- `indicator_configs` (versioned, new `ic_live_after_dt`): reconfigure hb16 M+b; hbhl16/hblo16/hbhi16
  M+m; gcs15 M/m/r. Each picks `ic_ivm_pk` (closed vs emerging) at creation.
- `lp_config`: +`lp_bro_wob`=12. (`lp_s30r_lb`=19, `lp_pin_prox`=0.4 already present.)

## Grind plan (after wiring, only if bias updates don't match the chart's story)
Sweep **hb16 src only** {close, hlc3, hlcc4}; grind M (mage) + m (minion) together, small steps. Other 3
sets' srcs fixed. Number fields stay put unless the chart disagrees.

## Open micro-forks (before config creation)
1. **hb16 reconfigure** = version-insert (new dated row, keeps hl2 in history) vs in-place UPDATE? Lean
   **version** (table is built for it; reversible). Joe said "overwrite" — confirm which.
2. **line_type for the BBs** = `bb` (matches existing hb16M/m). ✓ assumed.
3. **is_pk values** for the 3 new prefixes = MAX(is_pk)+1 onward. ✓ assumed.

## The other five mechanics (stubs — spec each before building)
gravity · FIFO · weakness · bl state change · bias neutral.

See [[bias_machine_eval_constraints]], [[project_bias_meld]], [[project_bias_results_holding]].
