# rpl event storage — spec

*0719. Persistence seam for the rpl flow (`r-pred → x-cross-pred → bias_trend_flip → flip_div`).
Event-grain, so a sibling to `GrindStore` (which is KPI/cell-grain — see `grind_storage_spec.md`),
NOT a bespoke per-script table. Code: `optimus9/db/rpl_event_store.py` (`RplEventStore`).*

## Why a sibling, not GrindStore
- GrindStore stores **one KPI row per config cell** — a sweep leaderboard.
- rpl produces a **timestamped event stream per run** (r-pred onsets, x-cross-preds, the flip, div
  votes). Different grain. Forcing it into KPI shape fights the data. Precedent: `trade_book`.

## Three tables

**`rpl_config`** — named knob baseline. The flow READS these; nothing is hardcoded in-script.

| col | type | meaning |
|---|---|---|
| `rc_pk` | BIGINT PK | |
| `rc_name` | VARCHAR(40) UNIQUE | `baseline`, `anti40`, … |
| `rc_knobs` | JSON | every flow knob (see below) |
| `rc_notes` | VARCHAR(255) | |

`rc_knobs` holds: `lines` (per-line kline/bb cfg for r/x/m/M + s1/s30/s2 fixed lines), `tfs.lo/hi`
(exhaustion-ladder sweep range), `boundary.hi/lo` (85/15), `fence.fh/fl` (predict_breach engage band
65/35), `anti` (anti-fence + s2r gate midline, 50 = side-of-50), `vmin` (x-cross-pred velocity floor),
`carry_ms` (seam-carry, 120000), `s2_tf_sec` (fast current-bias filter TF, 120), `delegate_offset`
(bias_trend_flip delegates exh−5), `wob_n` (cross_wob debounce, 9), `div_net_min` (entry ≥N votes, 3),
`div_horizon_ms` (div search after flip, 1800000).

**`rpl_run`** — one row per flow execution. `rr_config_pk` → the knobs it read; `rr_engine_rev` =
flow-script md5; `rr_entry_ms` = resolved flip_div entry (NULL = none); `rr_side` bull/bear;
`rr_window_start/end` ms.

**`rpl_event`** — the teed stream. `re_run_pk` → run; `re_ts` ms; `re_stage`
(r-pred/x-cross-pred/bias_trend_flip/flip_div); `re_tf`; `re_r`,`re_x`; `re_net`; `re_votes` JSON
(s1r/s1M/s30r/s30M); `re_mode` (predict/backstop + s2r); `re_note`; `re_is_entry`.

**`vw_rpl_entries`** — `re_is_entry=1` rows joined to run + config knobs = the discovery surface:
"every entry and the knobs that produced it", one query.

## API (mirrors GrindStore)
```
st  = RplEventStore(db)
pk  = st.upsert_config('baseline', KNOBS)      # seed/replace a knob baseline
C   = st.load_config('baseline')               # {'rc_pk',..., **knobs} — the flow reads THESE
run = st.register_run('bull', w0, w1, C['rc_pk'], engine_rev=rev)
st.log_events(run, events)                      # bulk executemany (one txn)
st.set_entry(run, entry_ms)
```

## Discipline
- No hardcoded knobs in the flow — change a value = `upsert_config` a new named baseline, re-run.
- Events sourced from the jig only (`W.line`), teed inline via `tee(t,stage,**f)`, flushed once.
- A pivot is reproducible from `rr_config_pk` + `rr_engine_rev`.
