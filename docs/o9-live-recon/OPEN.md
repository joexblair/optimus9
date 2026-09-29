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
| the gate window | **backward-only, 7 min**. Joe 0929: *"the -3.5 and + 3.5 logic is what's making it non-causal, so let's drop the forward"* |
| the config | **v2 only**. Joe 0929 dropped v1 and its 166 rows after the A/B |
| a forward WAIT on a rejected sig bar | **rejected**. Joe 0929: *"no V3, just v2"*. It was causal and recovered all 7 lost opens, but 5 of 7 additions lose |
| the §20.2 latency | **accepted for now**. Joe 0929: *"latency is ok for now. eventually we'll cherry-pick what we need from the classes and optimise"* |

## Not ruled — will need him

1. ~~**Whether the sig_utc producer chain can run forward.**~~ **ANSWERED 0929 — IT RUNS IN
   REALTIME.** Joe corrected the framing first: *"your 'run forward on a bounded window' sounds like
   lookahead, but you could just be saying 'run in realtime'"*. The second one.

   `report_realtime_replay.py` hands the producer only bars 0..k at every cutoff `k` — the v3 rows
   that have printed, the ws1mage-rev legs whose own `sig_conf` is at or before `k`, and
   `release(last_bar=k)` — and records what it would emit. The ladder is every v3 row bar in the
   window, 1179 of them, because that is when information arrives.

   | emission rule | moments emitted | of 121 historical | revisions | match history | differ |
   |---|---|---|---|---|---|
   | eager — emit as soon as the run breaks | 121 | 121 | **0** | 121 | 0 |
   | settled — wait for `k >= i1 + lag_bars` so `release`'s confirm window is never clipped | 121 | 121 | **0** | 121 | 0 |

   Zero revisions is the finding. An answer that changes after it was given is the only signature
   lookahead leaves, and there are none. `coil_moment.release`'s clipped-window hazard — *"A clipped
   window can only fail to disconfirm"* — does not fire on this window either: eager and settled
   agree on all 121.

   **The cost is latency, and it is in the mech.** Measured as (first emittable bar) − (the sig bar
   it names):

   | rule | n | p25 | median | p75 | p90 | max | mean |
   |---|---|---|---|---|---|---|---|
   | eager | 121 | 0 s | 165 s | 440 s | 860 s | 4955 s | 405 s |
   | settled | 121 | 0 s | 180 s | 440 s | 890 s | 4955 s | 416 s |

   Bimodal: 41 of 121 emit at **exactly 0 s** (the sig bar is the last event — all 11 `forward` and
   30 of 62 `confirmed`); the other 80 bind on the moment's end row at a median 340 s.

   o9-live will know each timestamp correctly, that far after the bar it points at. **A recon that
   does not carry this number will read the delay as a fault.** Re-run the replay whenever a
   producer in the chain changes.

2. **The dump's exact fields.** `RECON.md` suggests a set. It is a suggestion.
3. **Position size.** 22,000 coins is banked for sneaky-1. Nothing is set for this strategy. Not
   needed for MVP1 selection recon, needed the moment price enters.
4. **What happens to the 988 old `o9_ledger` rows.** Filter by time, by symbol, or start a fresh
   ledger.
6. ~~**Whether `wsl_sig_utc` should carry `sig_conf`.**~~ **RULED 0929 — Joe: *"sig_conf is
   unconditional - it has to happen"*.** `coil_exit.py` now emits the conf bar on every branch that
   was handing back a cross bar. The SELECTION is still made on the cross; only the bar returned
   moves, and `boundary_xwob` 4 makes every move exactly 3 bars = 15 s.

   | branch | rows | `rev` moves | `actionable` moves |
   |---|---|---|---|
   | CONFIRMED | 62 | +3 bars | no — it is release bar + confirm_lag_s, not a mage-rev |
   | GAP | 23 | +3 bars | **+3 bars** — the cross was knowable by `base`, but acting ON it is still 15 s early |
   | FORWARD | 11 | +3 bars | no — it is `base` |
   | LOOKBACK | 25 | no | no — `_knowable` already required `sig_conf <= named` |

   96 of 121 `wsl_sig_utc` values move; 23 of 121 `wsl_act_utc` values move, all on the GAP branch.

   **THE 121 BANKED ROWS STILL HOLD THE OLD CROSS BARS — see open item 8.**

7. **Whether the book may ever go flat.** As the rules stand it cannot after the first trade — every
   event is a reversal. Joe was shown this on 0929 and parked it: *"I'll keep improving the strategy
   in the background"*. Do not redesign it.

## Traps

**The gate trap is CLOSED too.** `rule1_gate` used to read `[k - tol, k + tol]` - 210 s of future -
and extend a run forward unbounded. Joe 0929 dropped the forward half: the window is now
`[k - 84 bars, k]`, 7 minutes back, and a run stops at the window edge. **Config v1 and its 166 rows are GONE** — Joe 0929
dropped them after the A/B, so v2 is the only shape that runs. Do not reintroduce a forward read.

**The backstop trap is CLOSED.** It used to be real: `trade_walk.backstop()` computed the closing bar
at open time from the stretch list, which is a future bar. Joe 0929: *"make this causal before we
handover to a new session. ie, IF this bar has dr-flip THEN"*. `walk()` is now a bar-by-bar loop
carrying `dr` and a `left` flag and reading only `dr[k]` and `dr[k-1]`. `backstop()` is deleted.
Same trades, and provably so — the latch alternates strictly, so the first bar back at D after
being −D IS the end of the −D stretch. Do not reintroduce the old shape.

**`wsl_sig_utc` is the `sig` CROSS bar, not the `sig_conf`** — on 98 of 121 v7 rows; the other 23
are the moment's END ROW (the LOOKBACK path in §20.4). `sig_conf = sig + boundary_xwob − 1 = sig + 3
bars = 15 s`. Comparing the banked column against `sig_conf` matches **0 of 121**, so when you are
checking what production banked, check against `sig`. **This is a description of the bank, not an
endorsement — see open item 6.** Joe 0929 read the same fact as a defect.

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
