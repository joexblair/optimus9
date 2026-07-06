# o9-live ⇄ backtest reconcile — hypothesis ledger (living, Joe 0707)

Backtest = source of truth (`v2_cascade`, the `v2_walk_ad` chain). o9-live is audited against it. Tooling:
`recon_suite.py` (per-event battery + scoreboard), `stream_tail.py` (arm+gate wake-feed → harness Monitor),
`arm_alert.py` (operator terminal tail). Working cadence: monitor wakes → run the suite on the event → diagnose →
extend hypotheses/scripts → rest.

## THE load-bearing finding (0707) — offline repro look-ahead
- The live decision's logged `o9_state_log.kline_ms = now_ms = bar_open + BAR(5000) + DELAY(301)`.
- At live time the tape's newest row is the **just-closed** bar (the forming bar isn't stored yet — see
  `driver.py`). Offline the tape has **advanced**, so `window(kline_ms)` lands **one bar too far forward** = a
  one-bar look-ahead. Symptom: slow lines (s15/s30) degenerate (s30m → 50.0), fast lines nearly right.
- **Fix:** reproduce at `now_ms = K − BAR` → `W.ts[-1] == K − 5301` = the bar o9-live actually decided on.
  Validated: **0.00000** line diff across all 19 lines, arm reproduced. Baked into `recon_suite.Repro.at()`.
- Family note: this is a reconcile-specific look-ahead (offline tape ahead of the live decision point), cousin to
  `project_v2_lookahead` (closed-vs-emerging). Any offline "reproduce what o9-live saw" MUST shift one bar back.

## Hypotheses — built as PASS/FAIL checks in recon_suite.py
- **bar_align** — `W.ts[T] == kline_ms − 5301`. Guards the look-ahead fix.
- **line_fidelity** — max |o9 snapshot (`o9_state_log_line`) − repro `W.line[T]`| < 0.05. Bit-exact when faithful.
- **event_reproduced** — backtest `mech_events@T` contains the o9-logged (state, es, meta). The core audit.
- **bt_extra_events** — producer events co-emitted at T that the o9 row didn't carry (e.g. `stale_exit` beside `arm`).
- **double_log** — exactly 1 row per (state, kline_ms). >1 ⇒ orphan-process double-write (see below).
- **emit_lag** — `created_ms − kline_ms` ∈ [0,15)s. Feed/processing health.
- **loop_singleton** — ≤1 `run_o9live.py` process alive. >1 is the double-log root cause.

## Findings / status
- **Clean post-reset stream: 4/4 events matched, 0 spurious** (2 arm + 2 gate). o9-live faithfully reproduces the
  backtest when a single loop runs.
- **Double-log root = orphan loop processes** (restarts with no single-instance guard → N concurrent writers → same
  arm 2–10× with different `created_ms`). A lone correct loop cannot double-write (driver fires `on_bar` once/bar;
  `v2_arm` dedups setups by bar-index). It is a **write-layer artifact, not a spurious cascade event**.
- **`recon_arm_gate.py` alignment bug (suspected, unverified):** keys backtest events by bar-open `ts[i]` but o9
  events by `kline_ms = ts+5301`, so they never align by ms → the `arm_gate_recon` table would read all-one-sided.
  Superseded for per-event work by `recon_suite.py`; fix or retire before trusting `arm_gate_recon`.

## Troubleshooting log

### 0707 — kline_ms mislabel (Joe's catch) + trade reconcile
- **Steps:** read `driver.py` (`_latest_bar` returns `kc_timestamp`=bar OPEN; `now_ms=ts+bar+delay=ts+5301`), `app.py:39`
  (`record(..., now_ms, ...)` stores `now_ms` in the `kline_ms` column), grepped kline_ms consumers.
- **Result — it's a MISLABEL, not a timing fault.** The kline prints correctly at seam+301 per spec (ticks
  00.000–04.999 → printed at +301). But o9-live stores the **decision instant** (`ts+5301`) in the `kline_ms`
  column, when that column should hold the **actual bar open** (`ts` = `W.ts[-1]`, the just-closed bar). My earlier
  `K−5000` offline hack was compensating for this instead of naming it. `created_ms` already holds the write instant.
- **Blast radius of relabeling:** `ui_server.py:96` joins `o9_state_log.kline_ms` against **ledger trade-times** (which
  use `now_ms`) to attribute cascade events to a trade. Switching state_log to bar-open skews that join by 5301ms
  unless the ledger side is shifted too. So the relabel is NOT free.
- **DECISION FORK (open — Joe's reason needed):**
  - *Opt-1 relabel at source* — store `W.ts[-1]` as kline_ms. Honest bar stamp; must also shift the UI attribution
    bounds −5301 (or move the ledger to bar-open). Bigger ripple.
  - *Opt-2 keep now_ms, document only* — kline_ms stays = decision instant (self-consistent with ledger/created_ms
    clock). recon_suite already maps K→bar via `−5301`. Smallest change; "mislabel" is then just a naming note.
  - *Opt-3 (Claude's rec) add `bar_ms` column* = `W.ts[-1]` — additive, zero ripple; gives reconciliation a true bar
    key while leaving the ledger-join clock intact. One column = one meaning (the bar it describes vs when decided).
- **Trade reconcile (Joe flagged 20:42:15):** both trade events (20:42:15, 20:52:25 — M2, LONG, halted so no order)
  reconcile **bit-exact** (0.00000 line diff; backtest emits `('trade',1,'M2')`). `trade` added to recon_suite STATES.
- **Net:** clean post-reset stream = **6/6 matched (arm+gate+trade), 0 spurious.** Event-level reconcile is CLEAN;
  #54's gap is downstream (exit/sizing/hedge), not the cascade signals.

### 0707b — live-trading anomaly, #54 exit bug caught, side-label inversion, purity + PnL
- **o9-live is NOT halted** (`o9_control.halted=0`, cleared ~20:50 — a resume). Live paper-trading since: 2 closed
  trades, net **−$43.10**, equity $500→$456.90. Contradicts the handover's "do not resume" — surfaced to Joe.
- **Live #54 exit-bug instance:** led2 SHORT entry 0.16494 → exit **0.16798 = −1.84%** — blew clean past the 0.9%
  SL (the flip-past-SL downstream gap). led1 was a clean short (+0.37%, exit worked). 1 of 2 exits failed = the exact
  reconcile target, caught live.
- **SIDE-LABEL INVERSION (my bug, ledger caught it):** `es` = the OOB *breach* side; the trade goes AGAINST it
  (`bd=-es`, side=`_SIDE[bd]`). GROUND TRUTH: o9_ledger opened a **Sell at the es=+1 trade event**. So **es=+1 →
  SHORT, es=-1 → LONG**. `arm_alert`/`stream_tail` `_side` corrected + feeders restarted; earlier "_SIDE fix" (which
  fed `es` into a `bd` map) was the error. Recon MATCH verdicts unaffected (es↔es); only the human label was wrong.
- **PURITY (Joe Q1): NO 5301 in the backtest.** `lr_exit_v2` enters at `px[tj]`, walks forward `tj+1..n`, takes
  SL/exit at `px[k]`/`px[ek]` — each price known at that bar's close; no look-ahead. The 5301 is only o9-live's
  state_log label. (`W.px` is a resampled close, ~1e-6 off raw kc_close — immaterial, not look-ahead.)
- **PnL SUMMARY (Joe Q2): close match, same data confirmed.** `backtest_pnl.py` v2_walk_ad 10.3d:
  FULL n=681 $500→$22,944 (45.9×) win 71% avgNet +0.353% — vs Joe's 656 / $22,659 / 45.3× / 71% / +0.364%.
  Deltas: my window resolved to 10.8d actual (warmup +12h) vs 10.3d (→~25 more trades); SINGLE-POSITION 241/7.5×
  vs Joe's 224/10.0× (definition/window differs — his accounting lives in `ker_*.py`). Same producer/config/data.

## OPEN hypotheses (next wakes)
- ~~**stale_exit honoring**~~ **RESOLVED 0707:** `stale_exit` is **emit-only** in the AD path. `_stale()` is called
  only by `v2_walk(stale_exit=True)`; `v2_cascade` (consumed by BOTH `v2_walk_ad` and `v2_mech_events`) never gates
  on it. So o9-live and backtest AGREE (both trade through it) — **not a reconcile divergence.** BUT the spec says
  `stale_exit` → "exit flow, no trade" (flow-2 AB toggle) and the shipping AD producer doesn't enforce it → a
  **spec-vs-build gap, parked for Joe's call** (whether the AD path should honor stale_exit). `bt_extra_events`
  detail is currently hidden in the suite's per-event line (verdict=None → shows `--`); surface the detail if chasing.
- **over-fire on the OLD (pre-reset) stream** — the handover's ~9% over-fire was measured on the multi-process,
  look-ahead-confounded data; re-measure on the clean stream as it accumulates (may evaporate).
- **batch-window efficiency** — a single window read at each event's bar-index should equal the per-event K−BAR
  window IF lines are strictly causal; verify, then use it to audit a whole session cheaply.
- **gate reason (a/b/c) agreement** across a larger sample; **trade-event** reproduction once trades resume.
- **emit_lag distribution** under feed hiccups; correlate with any fidelity slips.
