# What Joe has ruled, what he has not, and the traps

## Ruled — do not re-ask

| | |
|---|---|
| instance | v7 |
| gate | the banked `rule1_gate.gate()['open']` — his sheet col L `code #1 gate`, 72 open / 49 closed |
| same-bar priority | the dr-flip wins |
| price recon | out of scope, MVP2 |
| lookahead test | re-run from the tape, not a diff against stored verdicts |
| tape vs line at recon | the line-cache, deliberately, as a second test-point |
| dr producer | `latch_wob` at `LATCH_W` 8. He reversed his own "no wob" instinct on the numbers |
| the backstop | the flip **back to** the trade's own dr, two flips forward |
| scratchpad | moved into the codebase, knobs in the DB. Done |
| P&L | closed since 0917. MAE/MFE only |

## Not ruled — will need him

0. **`rule1_gate` IS NOT CAUSAL, and it is the blocker.** Its window is `[k - tol, k + tol]`, so at
   `rule1_tol` 7 min total it reads **42 bars = 210 s after the signal bar**, and `longest_outside`
   extends a run forward with **no bound**. A verdict at bar `k` is not knowable at bar `k`.
   Measured over the 109 distinct v7 sig bars:

   | window | gate open | closed | verdict changes vs banked |
   |---|---|---|---|
   | `[k-42, k+42]` — banked, NOT causal | 64 | 45 | — |
   | `[k-84, k]` — same 7 min, all behind | 68 | 41 | **18** — 7 open→closed, 11 closed→open |
   | `[k-42, k]` — 3.5 min behind | 56 | 53 | **8** — 8 open→closed, 0 closed→open |

   Every changed verdict adds or removes a trade, so this is a strategy change, not a refactor.
   A fourth option changes nothing: keep the window and treat the verdict as knowable at `k + 42`,
   the `sig_conf` pattern this codebase already uses — same trades, each opening 3.5 min later.
   `rule1_gate.py`'s docstring carries all of it. **Nothing has been changed.**

1. **Where realtime `sig_utc` comes from.** `wsf_leash.wsl_sig_utc` is produced by
   `report_coil_exit.py` from banked confluence moments, and a moment's end is *"only knowable when
   the next row prints"* (§20.2, median 300 s, max 5000 s). That latency is inherent to the mech, not
   an implementation detail. Whether o9-live recomputes the leash live, reads the table as it fills,
   or something else, is **the biggest open question in the job**.
2. **The dump's exact fields.** `RECON.md` suggests a set. It is a suggestion.
3. **Position size.** 22,000 coins is banked for sneaky-1. Nothing is set for this strategy. Not
   needed for MVP1 selection recon, needed the moment price enters.
4. **What happens to the 988 old `o9_ledger` rows.** Filter by time, by symbol, or start a fresh
   ledger.
5. **Whether the book may ever go flat.** As the rules stand it cannot after the first trade — every
   event is a reversal. Joe was shown this on 0929 and parked it: *"I'll keep improving the strategy
   in the background"*. Do not redesign it.

## Traps

**The backstop trap is CLOSED.** It used to be real: `trade_walk.backstop()` computed the closing bar
at open time from the stretch list, which is a future bar. Joe 0929: *"make this causal before we
handover to a new session. ie, IF this bar has dr-flip THEN"*. `walk()` is now a bar-by-bar loop
carrying `dr` and a `left` flag and reading only `dr[k]` and `dr[k-1]`. `backstop()` is deleted.
Same 142 trades, and provably so — the latch alternates strictly, so the first bar back at D after
being −D IS the end of the −D stretch. Do not reintroduce the old shape.

**`wsl_sig_utc` is not a `sig_conf`.** It is the `sig` CROSS bar on 98 of 121 v7 rows, and the
moment's END ROW on the other 23 (the LOOKBACK path in §20.4). `sig_conf = sig + boundary_xwob − 1 =
sig + 3 bars`. Comparing against `sig_conf` matches **0 of 121** — that mistake cost a session turn.

**`wsf_leash` holds several rows on one sig bar.** 121 rows are 109 distinct bars over the window; on
09-01, 32 rows are 28 bars. Any count keyed on the bar collapses them. Say which you mean.

**`wsl_dr` is not the walk's dr.** `wsl_dr` is `latch` (no wob) read at the moment's **first** bar —
242 of 242. The walk's dr is `latch_wob` read live at the bar it starts from. They differ on 7 of 242
rows. §22.21 and §22.22. This is intended, not a bug to fix.

**o9-live's `StrategyLoop` runs `v2_walk_ad` today.** Not this strategy. See `CODE_MAP.md`.

## Joe's standing rules for whoever picks this up

> "always be raw with me, and never infer. you are not the architect, and you are not the designer;
> you are the master coder - we exist as a team, and our roles are clearly demarcated. any time you
> need to make an unplanned decision while you code, stop and tell me what you see"

> "you're not here to make data look good. the data you see as not good, is exactly the data I need to
> make decisions: you will not hide it from me"

> "my requirement is that you use only the mecahnisms I've given you to try and hit a target. if you
> can't hit a full target, tell me why. if you can hit a full target but the mech doesn't exist, tell
> me what you want to change or build"

Also: no caps, windows or truncations he did not ask for; every hard-coded value belongs in the DB;
every figure goes in a table, never inline in a bullet; no percentage without its episode count; and
three closers on every substantive response — Summary as bullets, Reads, PnL impact.

`.claude/joes-convo-style.md` is the full format contract. `docs/staying_light.md` is the other half.
