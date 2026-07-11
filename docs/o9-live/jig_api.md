# Jig API — the one legal source

> [o9-live arm-delay spec](./README.md) · **causal / emerging-only**.
> `optimus9/analysis/jig.py`. Every mechanism reads here — no hand-rolled prediction/curl, no hand-built
> line tuples.

## `causal.*` — live-legal
- `line(name)` = `W.line` value-mode-honoured emerging read (validated 99.89% vs TV/24h).
- `predict_set(prefix, tol=0.0, maj='M'|'Mage')` — predicted-breach sign for a set; `tol` sweepable,
  `0.0` = spec. Ungated (mini-OOB gate is the consumer's). `mini_oob(prefix)` — ±1/0 OOB sign of the set's
  mini. `predict(k, m, M, tol)` — the primitive. See [prediction](./prediction_and_curl.md).
- `finishers(tf, r_lb)` → `s_qualify` (qhi short-side, qlo long-side). `finisher_parts(tf, r_lb)` — per-bar
  components for N-of-9 (m/Moob/Mrev/rlb per side). `finisher_pair(...)` = the causal co-occurrence EVENT
  (feed a consumer; don't re-bake the conjunction inline).
- `fin_unlatch_6of9(arm, cap, side, q15, q30, sets=(('gcs5',29),('s15',None),('s30',None)), N=6, box_lb=None,
  tol=None, bind_tol=6, anchor='breach')` — gates on `fin_box_qualified` internally (jig.py:84), then
  `fin_unlatch_nof9`. Returns the trade bar or None. See [finisher](./finisher_6of9.md).
- `reversal(line, wob)` — boundary-agnostic `_mage_rev` (causal). `coarse(name, seam_ms)` +
  `curl(ts_c, c, direction, with_val)` — the single curl-detect impl (`_curl_detect`, also lr_exit_v2). See
  [curl](./prediction_and_curl.md).

## `score.*` — HARNESS / non-causal (NEVER inside a strategy)
- `emit_bgcolor(streams, path, title, opacity)` — array-bgcolor Pine emitter (chunked-400 + binary_search;
  identifiers prefixed `s_` to dodge Pine keywords). Plus swings, entry-quality, `emit_labels`.
