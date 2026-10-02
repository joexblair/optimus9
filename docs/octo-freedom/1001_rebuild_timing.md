# 1001 — what one 104 h rebuild costs, per 5 s bar

**RULED 1002: shape B** (Joe: *"B"*), from these numbers. Built: `1002_live_producer.md`.

Joe 1001: *"go for it"* — time one 104 h rebuild before choosing between `OPEN.md`'s bounded re-walk
(rebuild everything every bar) and an evolving cache. He added: *"I'm more thinking we should have an
evolving cache, updated per 5s"*.

Script: `docs/octo-freedom/1001_rebuild_timing/time_rebuild.py`. Reads only; writes nothing to the DB.

## The answer

| part of one rebuild | seconds per 5 s bar | what it is |
|---|---|---|
| load 104 h of 5 s bars + `px` | 0.893 – 0.995 | `BiasWindow` construction (`bl_detect._setup`) |
| build the 31 lines the walk and rule#1 read | 0.375 – 0.456 | `W.line(n)` for all 31 |
| **lines subtotal** | **1.268 – 1.451** | 3 fresh windows at consecutive bars |
| ws1mage-rev legs + rev mask | 0.157 | vectorised over 104 h |
| `leash_walk.walk` over 104 h, memo cold | 44.277 | 74,880 bars stepped; 192,329 `momentum_true` + 964,180 `flat_run_at` calls |
| rule#1 `gate_open(k, 60)` on the walk's bars | 34.615 | 11,816 MECH bars gated, 4,791 emitted |
| **walk + rule#1 subtotal** | **79.05** | one cold pass |
| **full stateless rebuild** | **≈ 80.3 – 80.5** | the two subtotals added; not run as one call |

- The budget is one 5 s bar. A full stateless rebuild costs about 16× that.
- The lines are NOT the cost. They take 1.27–1.45 s, about 2% of a full rebuild. Re-running the walk and rule#1 over 104 h is the rest.
- **CORRECTION** to my chat #28 and my 1001 report to Joe: *"the lines are where the 104 h cost sits ... carrying only the arm/walk/book state saves almost nothing"*. Measured, it is the other way round.
- The workmate's ~26 s (chat #27) was a proportion from v2's timing, labelled as such. This replaces it.

## What the numbers say about the three shapes

| shape | per-bar work | measured cost per bar | new code needed |
|---|---|---|---|
| A — stateless: rebuild lines AND re-walk 104 h every bar (`OPEN.md`'s ruling) | everything | ≈ 80 s | none |
| B — carry the walk/arm/book state, rebuild the lines every bar | 104 h line build + ONE walk step + rule#1 on that bar if it passes the walk | 1.27–1.45 s lines + 0.59 ms average walk step + 2.93 ms per gated bar | a decide layer that carries `ArmState`/`LeashWalk`/the trade book across calls; the line layer is unchanged |
| C — carry everything, lines included | one step of every line + one walk step | not measured; no incremental line code exists | incremental `f_k_lookahead`/`f_bb_lookahead` with carried per-timeframe state, proven equal to the batch path |

- The walk-step and gate figures in row B are AVERAGES from the cold 104 h pass: 44.277 s / 74,880 bars = 0.59 ms per bar, and 34.615 s / 11,816 = 2.93 ms per gated bar. Not timed as a live loop.
- In B the lines still self-heal every bar, because they are rebuilt from the tape each time. Only the walk state is carried, and it is what `OPEN.md`'s self-healing argument applies to. A periodic cold re-walk (79 s per pass) compared against the carried state would check it. How often is Joe's.
- `ArmState.step` and `LeashWalk.step` already refuse a skipped bar (`arm_state.py:66-68`, `leash_walk.py:129-131`), so they were built for shape B or C.

## The timed lines are the backtest's lines

The timing builds the ws lines from the backtest cache's own role recipe,
`override(tf * 60, *spec[role])` with `spec` from `mech_lines(db, 'wsf')`, the same as
`report_coil_exit.py:39-50` and `build_wsf_trades.py:96-103`. 12 of the 31 are NOT in
`vw_indicator_configs_live` (`ws11r`–`ws21r` except `ws15r`, plus `ws23r` and `ws13m`), so the live
path cannot build them by name. It has to pass the same overrides. The gcws30 lines are read by name,
as the backtest does through the Jig.

Checked against the backtest's arrays (`Rig`, tape `END_MS` 2026-09-08) over the window's last hour,
720 bars ending 2026-09-01 12:00:00:

| lines | max abs diff | NaN mismatches |
|---|---|---|
| `ws1r`..`ws23r`, `gcws30r` (k role) | 0.0 to 8.5e-14 | 0 |
| `ws13m` | 0.0 | 0 |
| `ws5Mage` | 3.0e-10 | 0 |
| `ws1Mage` | 7.7e-09 | 0 |
| `gcws30Mage` | 6.6e-09 | 0 |
| `ws1m` | 1.7e-07 | 0 |
| `gcws30m` | 1.8e-07 | 0 |
| `ws2x` (rule#1's divergence line) | 2.0e-07 | 0 |

- The bb-role lines differ at the 1e-7 level, not 0. Whether any 1e-7 difference flips a fence or a
  cross test on any bar is not measured.

## Where it ran

| thing | value |
|---|---|
| repo | `causal/lookahead`, working tree at 2026-10-01 ~23:50 UTC (uncommitted changes from both sessions present) |
| line timing | `BiasWindow(db, end, lookback=24, warmup=80, cfg=BiasConfig(**BASE_BIAS), line_overrides=..., lean=True)` at end = 2026-09-01 12:00:00, 12:00:05, 12:00:10 UTC; 74,880 bars each |
| walk timing | backtest arrays, `TAPE_END` pinned 2026-09-08 (as `report_leash_walk.py` does), span 2026-08-28 16:00:00 → 2026-09-01 23:59:55 = 74,880 bars; knobs from `wsf_trade_config` v4; rule#1 at 60 bars |
| machine | 16 cores, 23 GB; another session was running its own jobs at the same time |

```
cd /home/joe/thecodes/docs/octo-freedom/1001_rebuild_timing
python3 time_rebuild.py lines     # 4.6 s wall for 3 builds
python3 time_rebuild.py walk      # 2 min 21 s wall: Rig load + walk + gate + the line check
```

## Not measured

| not measured | why it matters |
|---|---|
| shape B as a running loop | row B's walk and gate costs are averages of a cold pass, not a timed live step |
| shape C | no incremental line code exists to time |
| timing spread beyond 3 consecutive bars at 12:00 | DB load is 62–69% of the line cost and depends on the DB under live writes |
| verdict equality at the 1e-7 bb-line differences | the check compares values, not whether a test flips |
| the walk timing on `BiasWindow` lines | it ran on the backtest arrays: same code, same sizes, different source |
