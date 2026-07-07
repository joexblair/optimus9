# The test-jig — `optimus9/analysis/jig.py`

**One object over a pinned window that exposes the standard test requirements, so analysis scripts stop hand-rolling
what the engine already packages.** Born 0707 after the same drift-tax was paid four times in a session (re-rolling
`fin_unlatch`, nearly re-rolling `s_qualify`, hand-rolling `lr_walk`'s `mfe_side`, computing MAE-to-exit instead of
MAE-to-swing).

**The one rule — delegation is absolute.** The jig only *calls* existing producers; it never re-implements their
logic. If a verdict isn't packaged yet, split the producer first, then expose the split here. A facade that copies
logic forks the truth and drifts.

**The two namespaces — the split IS the guardrail.** `jig.causal.*` is live-legal (a strategy may use it);
`jig.score.*` is harness/scoring and **non-causal** (uses future data — never inside a strategy). Reaching for
`jig.score.*` in a decision path is the tell you've crossed into look-ahead.

---

## Index

### Construction
- **`Jig(end_ms, hours, warmup, overrides, dev, bias)`** — builds the pinned bench once; `.causal`/`.score` hang off it.
- **`.ts .px .n .cfg .hi .lo .W`** — the window's 5s timestamp/price arrays, bar count, `lr_config`, boundaries, and raw `BiasWindow` (read-only).

### `jig.causal.*` — LIVE-LEGAL (delegates to the real producers)
- **`line(name)`** — the value_mode-honoured 5s array for one line (emerging = causal).
- **`sign(name)`** — per-bar OOB sign of a line: `+1` hi / `−1` lo / `0` in-band.
- **`finishers(tf, r_lb=None)`** — the packaged `s{tf}a` qualify (Mage-reversal → r-lookback) as `(qhi, qlo)`.
- **`finisher_parts(tf, r_lb=None)`** — the per-bar COMPONENTS of `s{tf}a` (Mage-OOB · Mage-reversed · r-in-lookback) for N-of-9 gates.
- **`arms()`** — the v2 arm events `[(i, es, bd, cap, src)]`.
- **`gates(arms=None)`** — the s3s4 gate opens for a set of arms.
- **`predict(k, m, M)`** — per-bar predicted-breach direction of line `k` from anchor BBs `m`/`M`.
- **`reversal(line, wob)`** — boundary-agnostic reversal of a line: `+1` up-turn / `−1` down-turn after `wob` confirming steps.
- **`coarse(name, seam_ms)`** — sample an emerging line at seam boundaries (e.g. every 5 min).
- **`curl(ts_c, c, direction)`** — causal trough(`+1`)/peak(`−1`) detector on a coarse series; fires one seam late.

### `jig.score.*` — HARNESS / SCORING, NON-CAUSAL (never in a strategy)
- **`swings(price=None, pct=None)`** — 0.9%-ZigZag pivots `[(idx, 'H'/'L')]` (price ffill'd first).
- **`legs(pivots=None, price=None)`** — consecutive pivots → `[{start, end, dir, amp_pct}]`.
- **`entry_quality(entries)`** — per-trade MAE/MFE to the next favourable swing (exit-INDEPENDENT) + `mfe_side`.
- **`table(rows, headers, row_fmt)`** — print a fixed-width table.
- **`emit_labels(labels, path, title)`** — pine label emit (entry/exit, green/red, up/down; TV op-limit safe).

---

## Construction

### `Jig(end_ms, hours=48, warmup=24, overrides=None, dev=None, bias=None)`
Builds the pinned `BiasWindow` + `lr_config` once and holds them. Everything else hangs off `jig.causal` / `jig.score`.
- **`end_ms`** — window END, unix ms. **Pin it to a fixed timestamp** (not `now`) so runs reproduce — the now-based
  window confounded a real A/B this session.
- **`hours`** — trade span before `end_ms` (default 48). **`warmup`** — extra hours before that for line warmup (24).
  Total `BiasWindow` lookback = `hours + warmup`.
- **`overrides`** — `BiasWindow` `line_overrides` for non-DB lines, `{ind_name: (tf_sec, cfg_tuple, value_mode)}`,
  e.g. `{'s10r': (600, ('k',6,6,5,'hl2'), 'emerging')}`.
- **`dev`** — an open `DatabaseManager`; if omitted the jig opens (and on `close()` disposes) its own.
- **`bias`** — a `BiasConfig`; defaults to `BiasConfig(**BASE_BIAS)`.
- **Attributes:** `.ts` (int-ms array), `.px` (float), `.n`, `.cfg`, `.hi/.lo`, `.W`, `.hours`.
- Use as a context manager to auto-close the DB: `with Jig(end) as J: ...`.

```python
from optimus9.analysis.jig import Jig
import datetime as dtm; from datetime import timezone
end = int(dtm.datetime(2026, 7, 7, 20, 0, tzinfo=timezone.utc).timestamp() * 1000)
with Jig(end, hours=48, warmup=24, overrides={'s10r': (600, ('k',6,6,5,'hl2'), 'emerging')}) as J:
    ...
```

---

## `jig.causal.*` — live-legal

### `causal.line(name) -> np.ndarray`
Delegates to `W.line` — THE value_mode-honoured read (emerging → causal developing value; closed → base-aligned).
Returns a float array over the full 5s grid. **Always use this, never a raw resample.**
```python
s5m = J.causal.line('s5m')
```

### `causal.sign(name) -> np.ndarray[int]`
Per-bar OOB sign of a line vs `cfg.hi`/`cfg.lo`: `+1` (≥hi), `−1` (≤lo), `0` (in-band). Computed here (trivial), not a
producer. Used for breach detection: a fresh breach = `sign[i]!=0 and sign[i]!=sign[i-1]`.

### `causal.finishers(tf, r_lb=None) -> (qhi, qlo)`
Delegates to **`s_qualify`** — the packaged finisher: `s{tf}a` qualifies at the `s{tf}Mage` reversal
(`wob=cfg.fin_mage_wob`) with m OOB (+M OOB unless `cfg.fin_s30M_oob=0`) and a same-side r within `r_lb` bars back.
- `tf` — `'s2'`/`'s15'`/`'s30'` (the line prefix).
- `r_lb` — the r-lookback in the r-line's own TF bars. Defaults to `cfg.{tf}r_lb` (exists for s15/s30). **For a tf
  without a DB lookback (e.g. `s2`), pass `r_lb=`** (raises otherwise).
- Returns **`(qhi, qlo)`** bool arrays: `qhi` = **short-side** qualify (es=+1), `qlo` = **long-side** (es=−1).
```python
q15h, q15l = J.causal.finishers('s15')
q2h,  q2l  = J.causal.finishers('s2', r_lb=J.cfg.s15r_lb)
```
Do NOT hand-roll the finisher latch either — for the entry latch (both in a box → trade on the next same-side s15a)
use `lr_v2.fin_unlatch`.

### `causal.finisher_parts(tf, r_lb=None) -> dict`
Delegates to **`s_qualify_parts`** (the SRP-split components of `s_qualify`). Returns per-side bool arrays:
`m_hi/m_lo` (m OOB), `Moob_hi/Moob_lo` (Mage OOB), `Mrev_hi/Mrev_lo` (Mage reversed toward the side, wob
`cfg.fin_mage_wob`), `rlb_hi/rlb_lo` (same-side r OOB within `r_lb` back). `s_qualify = Mrev & m & (Moob | ¬strict) &
rlb`. For **N-of-9** finisher gates: count the components across `s2/s15/s30` in the box instead of AND-ing them.

### `causal.arms() -> list`
Delegates to **`v2_arm`**. Returns `[(i, es, bd, cap, src)]` — bar index, side (es=+1 short / −1 long), bd=−es, the
arm's cancel/deadline bar `cap`, and the source (`'s5m'`/`'s5r'`).

### `causal.gates(arms=None) -> list`
Delegates to **`gate_open`**. Pass an arm list (defaults to `self.arms()`). Returns the s3s4 gate-open events.

### `causal.predict(k, m, M) -> np.ndarray[int]`
Delegates to **`predict_breach`** (with `cfg.hi/lo` + module `FENCE_HI/LO`). Per bar: does anchor `min/max(m,M)`
overshoot the boundary by more than `k` undershoots, while `k` is in the engage band and unbreached? Returns
`+1`/`−1`/`0`. All three args are line arrays (from `causal.line`).
```python
p10 = J.causal.predict(J.causal.line('s10r'), J.causal.line('s5m'), J.causal.line('s5M'))
```

### `causal.reversal(line, wob) -> np.ndarray[int]`
Delegates to **`lr_v2._mage_rev`**. Boundary-agnostic reversal of a line array: `+1` = up-turn / `−1` = down-turn,
confirmed after `wob` consecutive same-direction steps (`wob<=0` = first slope-flip). Causal (fires from steps ≤ the
bar; the turn is confirmed `wob` bars after it starts). Used for the arm-delay's s5Mage reversal and the s2Mage gate.
```python
rev5 = J.causal.reversal(J.causal.line('s5M'), J.cfg.arm_wob)
```

### `causal.coarse(name, seam_ms) -> (ts_c, vals)`
Samples an EMERGING line at every `seam_ms` boundary (`ts % seam_ms == 0`). `seam_ms=300000` = 5-min seams. Returns
the sampled timestamps + values. Used to detect shifts without 5s wiggle.

### `causal.curl(ts_c, c, direction) -> set[int]`
Causal trough/peak on a coarse series: `direction=+1` a trough (curl up), `−1` a peak (curl down). Fires **one seam
after** the turn (`c[k-1]` was the extreme), using only samples ≤ k — so it's causal, with ≤ one-seam lag. Returns the
set of 5s-timestamps at which a curl confirms.
```python
tc, vc = J.causal.coarse('s10r', 300000)
up_seams = J.causal.curl(tc, vc, +1)
```

---

## `jig.score.*` — harness / scoring (NON-CAUSAL)

### `score.swings(price=None, pct=None) -> list[(idx, 'H'/'L')]`
Delegates to **`find_pivots`** (0.9% ZigZag). `price` defaults to `J.px`, `pct` to `cfg.swing_pct`. The price is
**ffill'd** first (find_pivots stalls on the DEMA-warmup NaN). Non-causal: a pivot is only known once price reverses
`pct%` from it, and the final pivot is provisional.

### `score.legs(pivots=None, price=None) -> list[dict]`
Delegates to `swing_detect.legs`. Consecutive pivots → `[{start, end, dir(+1 up/−1 down), amp_pct}]`. `pivots`
defaults to the 0.9% swings of `price` (ffill'd).

### `score.entry_quality(entries) -> list[tuple]`
Delegates to **`lr_walk`** — the packaged entry-quality verdict.
- `entries` = `[(trade_ms, es, bd, bar_idx)]` (e.g. `[(int(J.ts[i]), es, bd, i) for (i,es,bd,cap,src) in arms]`).
- Returns per trade `(trade_ms, dt, es, bd, mae, mfe, mfe_ok, mfe_side, price)`:
  - **`mae`/`mfe`** — measured from entry to the next **FAVOURABLE** swing pivot → **exit-INDEPENDENT** (does not move
    when the exit changes; this is the true entry-quality number, unlike MAE-to-exit).
  - **`mfe_side`** — `1` if the next swing pivot after entry is the favourable kind (long→High, short→Low), i.e. the
    trade **opened on the MFE side of the swing** (favourable leg ahead); `0` = adverse leg first.
  - **`mfe_ok`** = `mfe >= cfg.target`.
```python
ent  = [(int(J.ts[i]), es, bd, i) for (i, es, bd, cap, src) in J.causal.arms()]
for tms, dt, es, bd, mae, mfe, ok, side, px in J.score.entry_quality(ent):
    ...
```

### `score.table(rows, headers, row_fmt)`
Prints `headers` (joined) then each row via `row_fmt % tuple(row)`. A convenience printer, no logic.

### `score.emit_labels(labels, path, title) -> int`
Writes a Pine v5 file of labels. `labels = [{ts:int-ms, y:float, text:str, green:bool, up:bool}]` — `green`→green/red
bg-tone, `up`→`style_label_up`/`down`. Function-wrapped arrays + a `barstate.islast` loop (TV op-limit safe),
`size.normal`, `xloc.bar_time`. Returns the label count. Newlines in `text` = `\\n`.
```python
J.score.emit_labels([{'ts': int(J.ts[e]), 'y': float(J.px[e]), 'text': 'LONG IN', 'green': True, 'up': True}],
                    '/home/joe/thecodes/x.pine', 'my emit')
```

---

## Gotchas
- **Pin `end_ms`.** A now-based window makes A/Bs irreproducible.
- **`entry_quality` MAE is entry-side; the wireframe's old MAE-to-exit was not** — a later exit deepened it. Use
  `entry_quality` for entry judgement and realized-at-exit for the exit.
- **`causal.*` vs `score.*` is a hard line.** If you find yourself wanting `score.swings`/`entry_quality` inside a
  strategy's decision, stop — that's look-ahead.
- **New verdict not packaged?** Split the producer in `lr_v2`/`s_qualify` first, then expose it here. Never fork logic
  into the jig (that's the drift the jig exists to kill).
