# The causality audit

Joe 0929: *"make sure everything is causal. meticulously review the code for non-causal behaviour,
and walk the code by hand to confirm"*, then *"have you walked the producers for causality?"* — the
honest answer at that moment was no, only the trade chain. Both halves are walked now.

## The distinction that decides every verdict below

| | |
|---|---|
| **a forward read** | produces a verdict AT bar `k` using bars after `k`. This is lookahead. o9-live cannot reproduce it |
| **a deferred decision** | produces its verdict AT the later bar. o9-live reproduces it by waiting |

FOUR mechs in this chain are deferred (corrected 1001 - `oob_ib_cross`'s `sig` is the fourth, see
the 1001 audit below) and none of them is a defect: `coil_moment.release`'s confirm
window, `coil_exit.first_forward`, and the dr-flip backstop. One mech was a genuine forward read —
`rule1_gate` — and Joe closed it on 0929.

## The trade chain

| module | verdict | evidence |
|---|---|---|
| `optimus9/compute/dr_latch.py` | **causal** | both `latch` and `latch_wob` are forward loops; each bar reads only itself. 0 forward-read shapes |
| `optimus9/analysis/jig.py` `anchor_floater` | **causal** | all four steps walk backward. 0 reads above `k`, and its own docstring says so |
| `optimus9/compute/test_points.py` | **causal** | `flat_run_at` window is `r[k - samples + 1 : k + 1]`, ending at `k`. `stretches` builds a list but nothing in the walk consumes it any more |
| `optimus9/compute/trade_walk.py` `walk` | **causal** | bar-by-bar. Reads `dr[k]`, `dr[k-1]`, and - for the stop - `px[k]` against the entry bar's own price. Nothing above `k` |
| `optimus9/compute/trade_walk.py` `mae_mfe` | causal **at the close bar** | the span `[o, c]` is entirely past once `c` has printed |
| `optimus9/compute/rule1_gate.py` | **causal at config v2** | the window was `[k - tol, k + tol]`. Joe dropped the forward half |

## The upstream producers

| producer | verdict | evidence |
|---|---|---|
| `build_wsf_dtf_v3.py` — `flat_run_at` | **causal** | the window ends at `k`; the bar the run reaches `samples` is the bar it is knowable on |
| `build_wsf_dtf_v3.py` — `race_bars` | **causal** | `run` is a backward consecutive count via `maximum.accumulate`; `cand` fires on the bar the run REACHES `xwob`; `last_near` also accumulates backward |
| `optimus9/compute/stretchy_leash.py` | **causal** | `coil = dr*((m+Mage)/2 - r)` reads bar `i` of three lines at bar `i`. 0 forward-read shapes in 52 lines |
| `optimus9/compute/coil_moment.py` `release` | **deferred** | reads `v[t+1 : t+1+lag_bars]`, the confirm window. The verdict is known at `t + confirm_lag_s` 180 s; the peak `t` sits inside the moment |
| `optimus9/compute/coil_exit.py` `_knowable` | **causal** | requires `sig_conf <= by` explicitly. Joe 0917: *"keep it causal"* |
| `optimus9/compute/coil_exit.py` `first_forward` | **deferred, and UNBOUNDED** | CORRECTED 1001. It searches ahead dwell_ok → rev → sig and returns that cross's `sig_conf`, which is assigned to **`rev`** — `coil_exit.py:127` (CONFIRMED) and `:145` (FORWARD) — **never** to an `actionable_*` field. CONFIRMED's actionable is `pick + lag_bars` (`:125-126`); FORWARD's is `base = moment['brk']` (`:130, 144`). The search has **no bound**: three bare `np.searchsorted` calls, no `by`, no `last_bar` (`:104-112`). `rev` IS the banked `wsl_sig_utc` (`report_coil_exit.py:145-146`) and IS the walk's open bar (`measure_live_stop.py:131-133`), so the entry bar is set by an unbounded forward search. Measured on 09-01, `rev` − `actionable_confirmed`: 10 bars min, 58 median, **451 max** = 2,255 s (`docs/22_go_20260921/NOTES_momtf_mechdev.md:180-186`). It is deferred, not lookahead — every bar it reads is at or before the bar it returns — but a live producer must expect the entry to land that far past `pick + 180 s` |

## The one forward-looking column, and it has no consumer

`wsf_dtf_v3.wdv_run_bars` — *"length of the sideways run this row opens"*. At the row's bar you cannot
know how long the run will be, so the column **is** forward-looking.

- grep for `wdv_run_bars` outside `build_wsf_dtf_v3.py`: **nothing**.
- the leash chain reads only `wdv_ms` and `wdv_dr` from that table — `report_coil_exit.py:92`.

**It is a live trap.** Anything that starts reading that column inherits lookahead silently.

## 1001 — THE ENTRY BAR IS THE ONE LOOKAHEAD IN THE HEADLINE NUMBER

This row was missing from every table in this file, and it is the only non-causal read that sets
`+0.3911`.

| step | file:line | expression |
|---|---|---|
| the trade's open bar | `measure_live_stop.py:131-133` | `if ex['rev'] is not None and A <= int(ex['rev']) <= B: sig.add(int(ex['rev']))` -> `opens` |
| what it is scored from | `measure_live_stop.main()` | `walk(opens, ...)` then `score(px, T, CAP)`, which reads `t['open']` — **no emit-bar adjustment** |
| the bar the decision is KNOWABLE at | `sweep_v3_signal.py:234`, `measure_emit_entry.py:54-56` | `e = max(brk, int(ex['rev']), int(coil_exit.fired(ex)[1]))` |

**CORRECTED 1001, AFTER AN OVERSTATEMENT.** This section first labelled the entry bar LOOKAHEAD
outright, on the strength of "80 of 121 moments where `e > rev`". That figure is the count where the
CONSERVATIVE emit bar is later than `rev` — and `e = max(brk, rev, actionable)` waits for `brk` on
EVERY branch, including the two that do not need it. It is not the lookahead count. **It must be
asked per branch: is `rev` at or after the last bar that branch actually had to read?**

| via | the last bar the branch needs | moments on 09-01 | `rev` >= it | entry causal at `rev` |
|---|---|---|---|---|
| CONFIRMED | `actionable` = `pick + lag_bars`. The branch reads nothing from the moment | 15 | **15** | **YES, all of them** |
| FORWARD | `base` = `brk`, and `rev = first_forward(legs, brk) >= brk` | 1 | **1** | **YES** |
| GAP | reached only after the NEGATIVE verdict, which needs `i1` hence `brk`; `rev` is a `sig_conf` with conf `<= base = brk` | 9 | 1 | **no, 8 of 9** |
| LOOKBACK | same negative verdict; `rev = named = i1`, and `brk > i1` by construction | 7 | 0 | **no, 7 of 7** |
| **total** | | **32** | **17** | **17 causal, 15 not** |

**LABEL: CAUSAL on CONFIRMED and FORWARD. LOOKAHEAD on LOOKBACK and most of GAP.** The non-causal
15 are the branches reached only by deciding the moment did NOT confirm — a verdict that needs the
breaking row — while their `rev` sits at or before it.

| what it costs to enter at the first bar o9-live can act on, 90 days | value |
|---|---|
| eager emit | +0.3911 -> +0.3352 |
| settled emit | +0.3911 -> +0.3495 |
| gated opens, named bar -> emit bar | 1,045 -> 901 / 900 |

Joe has not ruled the entry bar changed, so the number stands. The recon should match the GAP and
LOOKBACK rows on the emit bar; CONFIRMED and FORWARD can be matched at `rev`.

## 1001 — ONE DORMANT LOOKAHEAD SEAM, a DB field away

`indicator_computer.py:46` `ALIGN_CLOSE_STAMP = False`, named in its own docstring at `:97-103` as
*"the closed-mode look-ahead seam"*: a base bar inside window `w` maps to `w` ITSELF, whose
high/low/close aggregate `w`'s whole span including its future. Backtest-only — live reads index
`-1`, where the aggregate covers `<= T`.

| fact | evidence |
|---|---|
| the flag is at its leaky setting | `indicator_computer.py:46` |
| the only switch that would flip it is never called | `compute_flags.py:38` reads `lp_align_close_stamp`; the table `lab_params` does not exist in this DB |
| dormant only because of DATA | all 70 `ws*`/`gcws*` lines are `value_mode = 'emerging'`, so `align_to_base` is unreachable via `LineReader.closed()` |
| blast radius if ONE line is set to `closed` | up to (tf - 5 s) of future per bar; the chain reaches `itf_seconds` 1380 => up to **1,375 s** |
| why it is the worst class for THIS recon | o9-live builds lines through the SAME `LineReader` and the same `value_mode` view, but physically cannot read an unclosed window — so the leak would be **backtest-only** and the recon would report `selection` while the cause is lookahead in the BACKTEST |

The emerging path itself is CLEAN: `lookahead_resample` uses `cummax`/`cummin` (not
`transform('max')`), and `f_k_lookahead`/`f_bb_lookahead` read every closed value at
`lb_idx = idx - 1`, the last COMPLETED window. The function NAMES are the hazard: everything is
called `*_lookahead` after Pine's `barmerge.lookahead_on`, and they implement the opposite.

## 1001 lookahead audit — the six producers the package had never walked

Joe 1001: *"the agent will double check for errant lookahead. you should double check from your
side as well"*. This is the second pass, on the modules the earlier audit had not read from source.

| module | what it reads | verdict |
|---|---|---|
| `dr_latch.latch` / `latch_wob` | `for k in range(i0, i1+1)`, reading `m1[k]`, `mx[k]` and carried state (`cur`, `up`, `dn`) only | **CLEAN** |
| `px` = DEMA(close, 2) | `_ema` is a forward recursion at `alpha = 2/(n+1)`; `_sma`/`_stdev` use `pd.Series.rolling(n)` with no `center=` | **CLEAN** |
| `oob_ib_cross` -> `sig` / `sig_conf` | `run` and `conf` are `np.maximum.accumulate` prefix ops; the cross bar is `k = c - (xwob-1)`, derived BACKWARD from the conf bar | **DEFERRED, and disciplined** |
| `lr_v2._mage_rev` -> `rev` | `out[1:]` is set from `cur`, which uses `np.diff` and prefix accumulates; `out[k]` depends on `dd[k-1]` = bars <= k | **CLEAN** |
| `stretchy_leash.combined_coil` -> `rig.CC` | per-bar algebra summed across `coil_lines`. No window, no normalisation across the series | **CLEAN** |
| `Rig.segs_for` and the v3-row `a_ + np.argmax(seg)` | the segment bound `b_` is a future bar, but `argmax` takes the FIRST True, which a forward walk finds at the same bar. The bound assigns bars to segments; segment membership at `k` is knowable at `k` because the dr has not flipped yet | **CLEAN — the bound does not choose the row** |

`sig` vs `sig_conf`, stated plainly because it is the one place discipline is doing the work:
`oob_ib_cross` names the cross bar `k` but can only do so at `c = k + xwob - 1` — the bar IB has
held `xwob` 4 bars. So `sig` is a LABEL computed at `c`; `sig_conf` is `c`. Acting on `sig` would
act 15 s before the evidence exists. `coil_exit._knowable` requires `sig_conf <= by` and
`first_forward` returns `sc[k]`, so no consumer on this path acts on the cross bar.

### ONE CONDITIONAL LOOKAHEAD — it does not fire on this tape, and it is not guarded

`build_wsf_trades.py:126-129`:

    good = np.isfinite(px)
    if not good.all():
        px = np.interp(np.arange(len(px)), np.flatnonzero(good), px[good])

`np.interp` is TWO-SIDED. An INTERIOR non-finite bar is filled from the next finite bar as well as
the previous one, so its value would carry information from the future. Leading non-finite bars are
clamped to the first finite value, which leaks nothing.

Measured on the 09-08 tape, 1,632,960 bars:

| non-finite `px` | count | effect |
|---|---|---|
| total | 2 | — |
| LEADING (bars 0 and 1, the DEMA(close, 2) warmup) | 2 | clamped, no leak |
| INTERIOR | **0** | none |

So it is clean today. **It is clean by luck, not by construction** — a tape with an interior kline
gap would fill those bars from later bars, and the stop and every MAE/MFE read that series. A
forward-fill (`np.maximum.accumulate` of the last finite value, or `pandas.ffill`) would make it
clean by construction. Not changed here: it is a code change to a module on the banked path, and
nothing has asked for it.

## The defect that was closed on 0930 — not a lookahead, a wrong-tape read

It is in this file because it was invisible to every causality argument above: nothing about the
SHAPE of the loop was wrong, the chain simply read the right function on the wrong bars.

`sweep_v3_signal.Rig` loads the tape **twice**:

| loader | what it supplies |
|---|---|
| `report_coil_exit.load()` | `ts` — the bar grid everything else is indexed by |
| `build_wsf_trades.load()` | `r1`, `r2`, `r3`, `g30r`, `px` — the lines **rule#1** reads |

`build_wsf_trades.py:61` does `from optimus9.orchestration.build_ws_lines import END_MS, HOURS,
WARMUP` — **by value, at import time**. A process that walks more than one window changes `END_MS`
and reloads `report_coil_exit`, but unless it also deletes `build_wsf_trades` from `sys.modules` the
second loader keeps the FIRST tape. `ts` moves; the `r` lines do not. `gate_open()` then indexes
`r1/r2/r3/g30r` with bar numbers from a different tape.

`oos_confirm_lag.py` and `score_5day_windows.py` both did this.

| measurement | before the fix | after |
|---|---|---|
| IS rule#1 open | — | **unchanged** |
| OOS-A rule#1 open | — | **roughly doubled** |
| OOS-B rule#1 open | — | **roughly doubled** |
| IS net per trade | +0.3911 | **+0.3911 — reproduces exactly** |

**THE RATES ARE DELIBERATELY ABSENT.** `oos_confirm_lag.py:126-146` prints `sig bars` and
`rule#1 open` as integers and never a percentage, so any rate here would be derived with neither
numerator nor denominator published. Re-running it needs `TAPE_END` back at 2026-09-08 — see the
precondition row in `README.md`. The direction is the finding; the rates are not yet evidence.

The fix is a hard guard in `Rig.__init__`, not a convention:

```python
_t = np.asarray(_t, np.int64)
if len(_t) != n or not np.array_equal(_t, np.asarray(ts, np.int64)):
    raise RuntimeError('Rig tape mismatch: ...  Reload build_wsf_trades after changing END_MS.')
```

**Any new script that walks more than one window must add `build_wsf_trades` to its
`sys.modules` reload list.** The guard will stop it if it does not, which is the point.

Two downstream results came out of the corrected path:

| result | where it is recorded | how to re-derive it |
|---|---|---|
| `confirm_lag_s` 165 loses both OOS windows, −0.0058 and −0.0239 per trade, so 180 stands | `OPEN.md`'s Ruled table | `oos_confirm_lag.py` |
| of 29 five-day windows, **none** sits below median − 3×MAD, so no window is excluded | **nowhere else — this sentence is its only record** | `score_5day_windows.py:150-154`, which no reproduce block names |

## The trap that was closed on 0929

`trade_walk.backstop()` computed a trade's closing bar AT OPEN TIME from the dr stretch list — a
future bar. The walk never acted on it early, so the banked trades were correct, but the SHAPE was
lookahead and any live implementation copying it would hold knowledge it cannot have. Worse, that
lookahead would be **invisible to the recon**, because both sides would agree.

`walk()` is now a bar-by-bar loop carrying the trade's dr `D` and a `left` flag:

| step | test | action |
|---|---|---|
| 0 | `-((px[k] - px[open]) / px[open] * 100) * D <= -0.70` | **the STOP** — close, book flat. Joe: *"use stop"* |
| 1 | `dr[k] == -D` | `left = True` — the trade has reached its target side |
| 2 | `left and dr[k] == D and dr[k] != dr[k-1]` | **the backstop** — **CLOSE ONLY.** The flip has never opened since Joe's 0929-late ruling; the book goes flat |
| 3 | else, this bar is an ungated sig_utc | reversal |

Step 0 reads `px[k]` and the entry bar's price. Both are at or before `k`, so the stop is causal.
Step 0 before 2 before 3 is Joe's same-bar priority. Measured over the 90-day window the ties never
fire: **0 stop-and-flip and 0 stop-and-sig_utc collisions across 381 stops.** `backstop()` is deleted. **Do not reintroduce it.**

It is provably the same output, not luckily: the latch alternates strictly — a change needs
`d[k] != d[k-1]` and `d[k] != 0`, and it never returns to 0 once set — so the first bar back at `D`
after being `-D` IS the end of the `-D` stretch. Verified against the walk at the time: identical output, every MAE/MFE unchanged. The causality
argument stands on its own — it is about the SHAPE of the loop, not about a trade count.

## The hand-walk — it proves the SHAPE, not a trade count

**This walk is not checked against `wsf_trades`.** Every row there is a mech without the cap, so a
match would prove nothing about this mech. What the walk proves is that the decision at each bar
reads only `dr[k]` and `dr[k-1]` plus a carried flag — which is what makes it reproducible live.

A SHORT opened at dr +1 on 09-01 at 04:26:00:

| bar | dr[k−1] | dr[k] | change | == −D | left after | == D and change | decision |
|---|---|---|---|---|---|---|---|
| 04:57:40 | +1 | −1 | yes | yes | True | . | carry on |
| 05:04:30 | −1 | +1 | yes | . | True | yes | **backstop — CLOSE ONLY, book goes flat** |

Two bars decide it. Neither reads a bar above `k`. **No stop is applied here** — the cap lives in
`sweep_mae_cap.py`'s scoring, so in this mech the trade would end earlier if its adverse excursion
reached 0.70% before 05:04:30. That is `OPEN.md`, *does a stop end the trade*.

**A correction to an earlier version of this section:** it walked these bars and labelled them
"09-01 trade 3". They are the bars that decide the trade opened at 04:26:00.

## What a new session should re-run before trusting any of this

```
python3 sweep_live_stop.py          # the cap ladder, 81 rungs. The 0.70 rung is 894 / +0.3911
python3 report_realtime_replay.py   # 121 of 121 moments, zero revisions
```

**Not `build_wsf_trades.py`.** It reads signal bars from `wsf_leash`, which still holds the
pre-`sig_conf` cross bars, so it does not reproduce these numbers until the re-bank lands.

Both must reproduce from the tape and the DB alone. If they do not, something in the cache moved and
that is itself a finding — see `RECON.md`'s three mismatch classes.
