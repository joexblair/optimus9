# The causality audit

Joe 0929: *"make sure everything is causal. meticulously review the code for non-causal behaviour,
and walk the code by hand to confirm"*, then *"have you walked the producers for causality?"* — the
honest answer at that moment was no, only the trade chain. Both halves are walked now.

## The distinction that decides every verdict below

| | |
|---|---|
| **a forward read** | produces a verdict AT bar `k` using bars after `k`. This is lookahead. o9-live cannot reproduce it |
| **a deferred decision** | produces its verdict AT the later bar. o9-live reproduces it by waiting |

Three mechs in this chain are deferred and none of them is a defect: `coil_moment.release`'s confirm
window, `coil_exit.first_forward`, and the dr-flip backstop. One mech was a genuine forward read —
`rule1_gate` — and Joe closed it on 0929.

## The trade chain

| module | verdict | evidence |
|---|---|---|
| `optimus9/compute/dr_latch.py` | **causal** | both `latch` and `latch_wob` are forward loops; each bar reads only itself. 0 forward-read shapes |
| `optimus9/analysis/jig.py` `anchor_floater` | **causal** | all four steps walk backward. 0 reads above `k`, and its own docstring says so |
| `optimus9/compute/test_points.py` | **causal** | `flat_run_at` window is `r[k - samples + 1 : k + 1]`, ending at `k`. `stretches` builds a list but nothing in the walk consumes it any more |
| `optimus9/compute/trade_walk.py` `walk` | **causal since 0929** | bar-by-bar, reads `dr[k]` and `dr[k-1]` only |
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
| `optimus9/compute/coil_exit.py` `first_forward` | **deferred** | searches ahead for dwell_ok → rev → sig, but the ACTIONABLE bar it returns IS that future bar. The decision lands there |

## The one forward-looking column, and it has no consumer

`wsf_dtf_v3.wdv_run_bars` — *"length of the sideways run this row opens"*. At the row's bar you cannot
know how long the run will be, so the column **is** forward-looking.

- grep for `wdv_run_bars` outside `build_wsf_dtf_v3.py`: **nothing**.
- the leash chain reads only `wdv_ms` and `wdv_dr` from that table — `report_coil_exit.py:92`.

**It is a live trap.** Anything that starts reading that column inherits lookahead silently.

## The trap that was closed on 0929

`trade_walk.backstop()` computed a trade's closing bar AT OPEN TIME from the dr stretch list — a
future bar. The walk never acted on it early, so the banked trades were correct, but the SHAPE was
lookahead and any live implementation copying it would hold knowledge it cannot have. Worse, that
lookahead would be **invisible to the recon**, because both sides would agree.

`walk()` is now a bar-by-bar loop carrying the trade's dr `D` and a `left` flag:

| step | test | action |
|---|---|---|
| 1 | `dr[k] == -D` | `left = True` — the trade has reached its target side |
| 2 | `left and dr[k] == D and dr[k] != dr[k-1]` | **this bar is the backstop** — **CLOSE ONLY.** The flip has never opened since Joe's 0929-late ruling; the book goes flat |
| 3 | else, this bar is an ungated sig_utc | reversal |

Step 2 before step 3 is Joe's same-bar priority. `backstop()` is deleted. **Do not reintroduce it.**

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
python3 sweep_mae_cap.py            # 753 trades over 90 days, peak cap 0.70 at +0.3776/trade
python3 report_realtime_replay.py   # 121 of 121 moments, zero revisions
```

**Do NOT run `build_wsf_trades.py` to check this.** It has no stop in it, so it produces a mech
without the cap, and it banks. See `SPEC.md`, *this mech has no banked trade table*.

Both must reproduce from the tape and the DB alone. If they do not, something in the cache moved and
that is itself a finding — see `RECON.md`'s three mismatch classes.
