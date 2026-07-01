# Sweep harness — the mainstay optimiser (0701)

A reusable, parallel, checkpointed parameter sweep over the strategy stack. Scores each config on N windows by
**worst-window net** (minimax — the best worst-case, robust to regime). Built to be extended as new filters land
(post-o9-live). Three files, one responsibility each:

| file | responsibility |
|---|---|
| `bias_machine.py` | two **injection hooks** on `BiasWindow`: `line_overrides` (in-memory line configs, zero DB races) · `base_cache` (reuse a pre-loaded base tape) |
| `sweep_eval.py` | the **atomic unit**: `evaluate(db, end_ms, config, base_cache=…) → (net_of_cost%, n, win%)`. Config = a dict of overrides; SRP build→walk→(bias filter)→exit→score |
| `sweep_run.py` | the **orchestrator**: derive param space → covering-block generator → 16-core parallel → checkpoint to `sweep_results` → rank worst-window |

## Run
```
python3 sweep_run.py smoke   # ~40 configs, verify mechanics
python3 sweep_run.py full    # ~5000 configs, ~5h; RESUMABLE — re-run to continue after any stop
```
Results land in `sweep_results (idx, worst, nets[json], pv[json], err, ts)`. Rank: `ORDER BY worst DESC`.

## The config dict (what `evaluate` accepts)
```
{ line_overrides: {ind_name: (tf_sec, cfg_tuple, value_mode)},   # per-line, in-memory
  bias:   {BiasConfig knob overrides},
  lrcfg:  {sl, exit_rlb, curl_n, …},
  exit:   {predict, gate_fam, slip},
  bias_filter: {tf,lenM,lenm,multM,multm,srcM,srcm,N,oob} | None }   # hb33 entry filter
```
Nothing is written to the DB per config → workers are race-free.

## Param space (auto-derived — DON'T hardcode)
`init_space()` reads the **actual fetched line cache** (24 s-lines) and builds each line's len/mult/src ranges from
its live base ±deltas. Knobs + hb33 bias params live in `KNOB_SPACE`/`KNOB_DEFAULT`. `DEFAULT` = the current
shipping config, so any un-swept param stays at ship value.

## Covering-block generation (Joe's "overlapping subsets")
`gen_configs(target)` draws random `block`-param subsets (others at DEFAULT), each contributing ≤`per_block` of its
factorial, **bounded by target**. Blocks accumulate pair-coverage → every setting interacts with every other.
Deterministic (`SEED`) so resume aligns idx.

## Extending it (the post-o9-live path)
- **New filter/knob:** add its values to `KNOB_SPACE` + default to `KNOB_DEFAULT`, map it in `param_to_config`,
  consume it in `evaluate`. It auto-enters the covering blocks.
- **New line into the sweep:** it's automatic once the stack fetches it (derived from the cache).
- **New metric:** change the score in `_work` (currently `min(nets)`); the equity map (dynamic 5× sizing) is a
  top-N projection via `build_v2_walk.py`, kept out of the per-config loop for speed.
- **Real Bybit cost:** set `sweep_eval.RT_COST` once o9-live reports the true round-trip (fees + order-book slip).

## Windows
7 windows, 7-day each, 2-day overlaps, tiling **05-18→06-24** (the TV-sanitised span). Change `WINDOW_ENDS`.

## Notes
- Base-tape reload was the parallel bottleneck (DB contention); `base_cache` fixes it (~load once/window/worker).
- Metric per window = net-of-cost total % (comparable/additive across equal-length windows).
- See [[project_o9_live]] — real fills replace the 0.20% cost estimate; this stays the backtest optimiser.
