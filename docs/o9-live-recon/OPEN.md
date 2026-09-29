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

1. **Whether the sig_utc producer chain can run forward.** Joe 0929 corrected an earlier framing of
   this — they are not a banked-moments mystery: *"they may seem to be banked confluence, but their
   source is ultimately the wsf_dtf_v3 report being consumed by the wsf_leash `coil` report"*.

   The chain, top to bottom:

   | step | producer | what it emits |
   |---|---|---|
   | 1 | `build_wsf_dtf_v3.py` | `wsf_dtf_v3` — one row per (line, dr run): the first bar in that run where the line's r is sideways AND outside the 25/75 fence, ws1..ws23 |
   | 2 | `report_coil_exit.py` | reads `wdv_ms, wdv_dr` from `wsf_dtf_v3`, builds the coil, the confluence moments and the confirmed release |
   | 3 | `optimus9/compute/coil_exit.py` `resolve` | the ACTIONABLE bar and the validating `rev` |
   | 4 | `leash_bank.py` | banks it — `wsl_sig_utc` is `resolve`'s `rev` field |

   So the live question is concrete: **can steps 1 and 2 run forward on a bounded window ending at
   now**, the way `StrategyLoop` already does for `v2_walk_ad`. Step 1 is per dr run and step 2 walks
   rows, so neither is obviously blocked — but §20.2's latency is real and sits in step 2: a
   moment's end is only knowable when the next row prints, median 300 s, p75 492 s, max 5000 s.
   That latency is in the mech, not the implementation, and it sets the floor on how late a live
   `sig_utc` can be.

2. **The dump's exact fields.** `RECON.md` suggests a set. It is a suggestion.
3. **Position size.** 22,000 coins is banked for sneaky-1. Nothing is set for this strategy. Not
   needed for MVP1 selection recon, needed the moment price enters.
4. **What happens to the 988 old `o9_ledger` rows.** Filter by time, by symbol, or start a fresh
   ledger.
6. **Whether `wsl_sig_utc` should carry `sig_conf` instead of the `sig` cross bar.** THE ONE OPEN
   DECISION THAT BLOCKS CLEAN RECON.

   `oob_ib_cross` (`jig.py:117`) emits a cross only after IB has held `boundary_xwob` = 4 bars = 20 s,
   and returns `(cross_idx, conf_idx, side)` where `conf_idx = cross + xwob − 1` is *"the first bar
   the cross is KNOWABLE"*. Two consumers take `cross_idx` and drop `conf_idx`:

   | file:line | code | path |
   |---|---|---|
   | `coil_exit.py:49` | `return int(sg[k])` | CONFIRM + FORWARD |
   | `coil_exit.py:75` | `first = inside[0]` — `_knowable` filters on `sig_conf` then returns the cross bar | GAP |
   | `coil_exit.py` LOOKBACK | the moment's END ROW, already at or after a `sig_conf` | clean |

   Joe 0929: *"sig has already qualified the wob in code, but the wrong field was presented. every
   change will be exactly 15sec"*. He has **not** said to change it.

   Measured over the window, 50 of the 68 gated-open bars are exposed:

   | variant | trades | MFE > MAE | MAE mean | MFE mean |
   |---|---|---|---|---|
   | open at the `sig` cross bar (banked) | 119 | 68 (57.1%) | 0.698 | 0.991 |
   | open at `sig_conf`, +3 bars = 15 s | 119 | 68 (57.1%) | 0.720 | 0.969 |

   **Why it blocks recon.** o9-live cannot act at the cross bar — the hold is not complete yet. If
   the reference keeps opening there, every recon shows a 15 s divergence on 50 of 68 opens and that
   drift is indistinguishable from a genuine causality fault. Put it to Joe before the first recon
   job, not after.

   Related and already ruled out as the cheap fix: dropping `boundary_xwob` to 1 collapses `sig_conf`
   onto `sig` and costs MFE > MAE 57.1% → 53.7%. Joe 0929 ruled the sweep: *"no changes are needed in
   the g30 (ergo mage-rev) mech"*.

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
