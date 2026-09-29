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
| the gate window | **backward-only, 7 min**. Joe 0929: *"the -3.5 and + 3.5 logic is what's making it non-causal, so let's drop the forward"*. Config **v2** is the live one |

## Not ruled — will need him

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

**The gate trap is CLOSED too.** `rule1_gate` used to read `[k - tol, k + tol]` - 210 s of future -
and extend a run forward unbounded. Joe 0929 dropped the forward half: the window is now
`[k - 84 bars, k]`, 7 minutes back, and a run stops at the window edge. Config v1 keeps the old shape
so its banked trades stay reproducible; **v2 is the live one**. Do not reintroduce a forward read.

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
