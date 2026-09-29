# What Joe has ruled, what he has not, and the traps

## Ruled — do not re-ask

| | |
|---|---|
| instance | v7 |
| gate | the banked `rule1_gate.gate()['open']` — his sheet col L `code #1 gate`, 72 open / 49 closed |
| same-bar priority, dr-flip vs sig_utc | **the dr-flip wins** |
| **same-bar priority, stop vs opposing sig_utc** | **the STOP wins.** Joe 0929-late, asked directly: *"use stop"*. Flagged to him before the first recon job, and now closed |
| **order type** | **market**, both legs. Joe 0929-late: *"order type: market. MVP2 will develop the placement of limit orders"* |
| **the stop is client-side for MVP1** | Joe 0929-late, on a disconnect leaving the position naked: *"yes. that's MVP2 - we'll apply a larger stop with the exchange as a backstop"*. See `MVP2.md` |
| price recon | out of scope, MVP2 |
| lookahead test | re-run from the tape, not a diff against stored verdicts |
| tape vs line at recon | the line-cache, deliberately, as a second test-point |
| dr producer | `latch_wob` at `LATCH_W` 8. He reversed his own "no wob" instinct on the numbers |
| the backstop | the flip **back to** the trade's own dr, two flips forward |
| scratchpad | moved into the codebase, knobs in the DB. Done |
| P&L | closed since 0917. MAE/MFE only |
| **a sig_utc closes ONLY on an opposing dr** | Joe 0929-late, after spotting 09-01 03:40:05 (a SHORT) being closed by the 04:26:00 sig_utc (also a SHORT): *"trades must be first closed by an opposing dr signal, and secondly by a dr-flip if there is not opposing dr signal"*. A same-dr sig_utc is INERT - *"for now, it's inert"* |
| **the dr-flip backstop CLOSES but never OPENS** | Joe 0929-late: *"now we have the data I can see that dr-flip as an open is not helpful. the cost is accceptable - it gives us space to apply other mechs (lazy-g for example)"*. It still closes, or a trade would run to the next opposing signal whatever happened |
| **the MAE cap is 0.70%, and the stop is IN THE WALK** | Joe specified 0.9 on 0929, ruled 0.70 on the first ladder, then re-ruled it on the ladder re-walked with the stop live: *"retain 0.7% as the stop"*. `MFE-MAE` prints `-0.70` on a stopped trade |
| **the stop RACES the other exits** | Joe 0929-late: *"research how a stop is applied in trading - you'll learn that it's both: (at its signal or flip bar) OR (at the stop bar)"*. Three live exits, first to fire wins |
| **the cap goes in the KEY, not in `wsf_trade_config`** | Joe 0929-late chose this over a config row and a version bump. `wtc_v2_v7_rule1_gateopen_mae0.70` |
| **only the MAE-capped mech is handed over** | Joe 0929-late: *"you should be handing over only the mech that the MAE cap was applied to"*. Anything measured without the cap - `docs/sweeps/`, every row in `wsf_trades`, every variant - is a **different mech**. It is not a baseline and not a comparison |
| **the 0929 knob sweep is out** | Joe 0929-late: *"ok, the sweep is definitely poisoned. let's go back to baseline"*. It ran before the cap and before the flip-open ruling. Do not use `docs/sweeps/` |
| the gate window | **backward-only, 7 min**. Joe 0929: *"the -3.5 and + 3.5 logic is what's making it non-causal, so let's drop the forward"* |
| the config | **v2 only**. Joe 0929 dropped v1 and its 166 rows after the A/B |
| a forward WAIT on a rejected sig bar | **rejected**. Joe 0929: *"no V3, just v2"*. It was causal and recovered all 7 lost opens, but 5 of 7 additions lose |
| the §20.2 latency | **accepted for now**. Joe 0929: *"latency is ok for now. eventually we'll cherry-pick what we need from the classes and optimise"* |

## Not ruled — will need him

**Find an item by its name, not its number.** The numbers are stable but they are hard to search.

| # | the question, in one line | blocks |
|---|---|---|
| 1 | ~~can the signal chain run forward~~ | ANSWERED — it runs in realtime |
| 2 | what fields go in the trade-signal dump | the dump, the monitor |
| 3 | position size for this strategy | MVP2 only |
| 4 | what happens to the 988 old ledger rows | nothing — housekeeping |
| 5 | ~~should wsl_sig_utc carry sig_conf~~ | RULED — it must |
| 6 | ~~may the book go flat~~ | SETTLED by the flip-open ruling — it does |
| 7 | re-bank the 121 leash rows at sig_conf | the leash bank |
| 8 | ~~build a banker for this mech~~ | CLOSED - `build_wsf_trades.py`, key `..._mae0.70` |
| 9 | ~~stop vs opposing sig_utc on the same bar~~ | RULED — the stop wins. Measured: never occurs |
| 10 | ~~does a stop END the trade~~ | CLOSED - it does, and it RACES the other two exits |
| 11 | ~~entry bar~~ | CLOSED - the mech enters on the sig bar. See the note under item 1 |

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

   Bimodal: **41 of 121 emit at exactly 0 s** (the sig bar is the last event — all 11 `forward` and
   30 of 62 `confirmed`); the other 80 bind on the moment's end row at a median 340 s.

   **CAVEAT on the 41.** A cold re-run of `report_realtime_replay.py` on 0929-late returned **42 of
   121 (34.7%)** for eager and 38 of 121 for settled. The 41 is what the run that produced the
   latency table printed. The two have not been reconciled. Re-run it and take the number your own
   run prints; do not quote 41 without re-running.

   o9-live will know each timestamp correctly, that far after the bar it points at. **A recon that
   does not carry this number will read the delay as a fault.** Re-run the replay whenever a
   producer in the chain changes.

2. **The dump's exact fields.** `RECON.md` suggests a set. It is a suggestion.

3. **Position size.** 22,000 coins is banked for sneaky-1. Nothing is set for this strategy. Not
   needed for MVP1 selection recon, needed the moment price enters. See `MVP2.md`.

4. **What happens to the 988 old `o9_ledger` rows.** Filter by time, by symbol, or start a fresh
   ledger.

5. ~~**Whether `wsl_sig_utc` should carry `sig_conf`.**~~ **RULED 0929 — Joe: *"sig_conf is
   unconditional - it has to happen"*.** `coil_exit.py` now emits the conf bar on every branch that
   was handing back a cross bar. The SELECTION is still made on the cross; only the bar returned
   moves, and `boundary_xwob` 4 makes every move exactly 3 bars = 15 s.

   | branch | rows | `rev` moves | `actionable` moves |
   |---|---|---|---|
   | CONFIRMED | 62 | +3 bars | no — it is release bar + confirm_lag_s, not a mage-rev |
   | GAP | 23 | +3 bars | **+3 bars** — the cross was knowable by `base`, but acting ON it is still 15 s early |
   | FORWARD | 11 | +3 bars | no — it is `base` |
   | LOOKBACK | 25 | no | no — `_knowable` already required `sig_conf <= named` |

   96 of 121 `rev` values move; 23 of 121 `wsl_act_utc` values move, all on the GAP branch.

   **UNRECONCILED, and measure it before you quote it.** The branch table above gives LOOKBACK 25,
   while the trap at the bottom of this file says 23 rows are the moment's END ROW. The DB settles
   only the coarse split — `wsl_source` on the 121 v7 rows is **CONFIRM 62 / END 59**, and
   23 + 11 + 25 = 59, so the branch table is internally consistent with the bank. The 98/23 pair in
   the trap is not. Re-derive the per-branch `via` counts from `coil_exit.resolve` before acting.

6. **~~Whether the book may ever go flat.~~ IT NOW DOES.** This item used to say the book cannot go
   flat after the first trade, because every event is a reversal. **That was true before the
   dr-flip-never-opens ruling and is false now.** Under the ruling the book sits FLAT for 43.8 h of
   the 119.5 h 09-01..09-06 window — **36.6%**. Nothing is open for Joe here; the entry is kept so
   the old statement is not read as current.

7. **Re-banking the 121 `wsf_leash` rows at `sig_conf`.** `coil_exit.py` now emits the conf bar, but
   the 121 banked v7 rows still hold the **old cross bars**. `wsl_knobs` does not encode the change,
   so the unique key cannot tell the two shapes apart and a re-run would either collide or silently
   mix them. Joe's call: re-bank in place, bank alongside under a new knob-string, or leave the bank
   as the historical record and note the offset.

8. ~~**This mech has no banked trade table.**~~ **CLOSED 0929-late.** `trade_walk.walk` carries the
   stop, so `build_wsf_trades.py` produces and banks this mech.

   Joe chose the key over a config row: **`wtc_v2_v7_rule1_gateopen_mae0.70`**. A capped run can
   never land on the 332 uncapped rows. On those rows: *"they exist in a historical key so it
   shouldn't matter"* — they are left exactly as they are.

   **ONE THING IS STILL OPEN AND IT IS SMALL.** Putting the cap in the key rather than in
   `wsf_trade_config` leaves `MAE_CAP = 0.70` as a literal in `optimus9/compute/trade_walk.py`. It
   is the only value in the mech that does not live in the DB, against Joe's standing rule. His
   choice put it there; he has not been asked whether he also wants it as a config row.

9. ~~**Same-bar priority between the stop and an opposing sig_utc.**~~ **RULED 0929-late — Joe:
   *"use stop"*.** The stop wins, and it is in `trade_walk.walk`.

   **Measured over the 90-day window the tie never occurs:** 0 stop-and-flip and 0 stop-and-sig_utc
   collisions across all 381 stops. Both variants of the walk — stop bar closed to opens, and open
   allowed on the stop bar — produce identical output. The rule exists for a window that does
   collide, not for this one.

10. ~~**Does a stop END the trade?**~~ **RULED 0929-late. IT DOES, AND IT RACES THE OTHER TWO.**

    Joe corrected the framing first: *"research how a stop is applied in trading - you'll learn that
    it's both: (at its signal or flip bar) OR (at the stop bar)"*. A stop does not replace the other
    exits — an open trade carries three live exits and ends at whichever fires first.

    The cap used to be applied in scoring, so a stopped trade still ran to its signal/flip bar and
    the book stayed occupied. **No trade re-scores now** — a stopped trade is −0.70 either way — but
    its close bar moves earlier and the book frees up.

    | | measured over the 90 days |
    |---|---|
    | the book was held past the stop bar | median 1,177 bars = 98 min, max 4,421 bars = 6.1 h |
    | ungated sig_utc bars inside those windows | 216, across 158 of 311 |
    | trades | 753 → **894** |
    | net per trade | +0.3776 → **+0.3911** |

    The cap was then re-swept against the re-walked ladder and Joe re-ruled it: *"retain 0.7% as the
    stop"*. `SPEC.md` carries all 81 rungs.

11. ~~**The entry bar.**~~ **CLOSED 0929-late. The mech enters on the sig bar and its number stands.**

    An earlier version of this file called that number a "ceiling" and said it was not achievable.
    **That claim was imported from a measurement of a DIFFERENT mech** — `bank_emit_entry.py`, which
    has no cap. The capped mech has never been measured at any entry bar other than the sig bar, so
    there was no basis for the word. Removed.

    The 165 s emission latency is real, is measured, and is a **recon** number — see item 1 and
    `RECON.md`. Joe ruled it: *"latency is ok for now"*. It does not discount the mech's number.

## Traps

**The gate trap is CLOSED too.** `rule1_gate` used to read `[k - tol, k + tol]` - 210 s of future -
and extend a run forward unbounded. Joe 0929 dropped the forward half: the window is now
`[k - 84 bars, k]`, 7 minutes back, and a run stops at the window edge. **Config v1 and its 166 rows are GONE** — Joe 0929
dropped them after the A/B, so v2 is the only shape that runs. Do not reintroduce a forward read.

**The backstop trap is CLOSED.** It used to be real: `trade_walk.backstop()` computed the closing bar
at open time from the stretch list, which is a future bar. Joe 0929: *"make this causal before we
handover to a new session. ie, IF this bar has dr-flip THEN"*. `walk()` is now a bar-by-bar loop
carrying `dr` and a `left` flag and reading only `dr[k]` and `dr[k-1]`. `backstop()` is deleted.
Do not reintroduce the old shape.

**`wsl_sig_utc` is the `sig` CROSS bar, not the `sig_conf`.** `sig_conf = sig + boundary_xwob − 1 =
sig + 3 bars = 15 s`. Comparing the banked column against `sig_conf` matches **0 of 121**, so when
you are checking what production banked, check against `sig`. **This is a description of the bank,
not an endorsement — see item 7.** Joe 0929 read the same fact as a defect and ruled on it.
The per-branch split of which rows are the moment's END ROW is **unreconciled — see item 5.**

**`wsf_leash` holds several rows on one sig bar.** 121 rows are 109 distinct bars over the window; on
09-01, 32 rows are 28 bars. Any count keyed on the bar collapses them. Say which you mean.

**`wsl_dr` is not the walk's dr.** `wsl_dr` is `latch` (no wob) read at the moment's **first** bar —
242 of 242. The walk's dr is `latch_wob` read live at the bar it starts from. They differ on 7 of 242
rows. §22.21 and §22.22. This is intended, not a bug to fix.

**EVERY ROW IN `wsf_trades` IS A MECH WITHOUT THE CAP.** 332 rows, 4 key/window groups, none of
them carrying the stop. Do not compare o9-live against any of them and do not quote their numbers.
See item 8.

**The cap and the close rules are not knobs and they are not in the key.** `wsf_trade_config` v2 is
16 rows; `mae_cap` is not one of them. `trade_config.key()` is
`wtc_v%d_%s_%s % (version, leash_instance, gate)`, so a capped and an uncapped run land on the
**same key**. See item 8.

**o9-live's `StrategyLoop` runs `v2_walk_ad` today.** Not this strategy, and `ops/run_o9live.py:28`
labels that producer *"'ad'=v2_walk_ad (look-ahead arm-delay)"*. See `CODE_MAP.md`.

**The sign conventions are inverted between the two codebases.** `optimus9/live/strategy.py:5-6`:
*"bd +1 = Buy/long, bd −1 = Sell/short"*. This strategy: **`dr +1 = SHORT, dr −1 = LONG`**. A
producer written for `StrategyLoop` must flip the sign. Nothing in the live code says so.

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
