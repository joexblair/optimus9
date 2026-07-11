# Constraints & open items

> [o9-live arm-delay spec](./README.md) · **causal / emerging-only**.

## Constraints (Joe, verbatim / standing)
- **Causal / emerging ONLY.** Never "use closed to match TV". **TV is the source of truth**, synced on the
  emerging value.
- **Never hardcode** — values belong in the DB (`lp_config`, `indicator_configs`). The `s5m = 8|0.65|ohlc4`
  and `gcs5M/s15M = 37|0.6|ohlc4` overrides are named-in-code ONLY until swept and written.
- **No caps.** The hunt/arm run to the arm or the cancel; no fixed horizon.
- **No hand-roll.** Data and events come only from the jig; a re-implemented producer or hand-built k-tuple is
  silent corruption.
- **Signals belong to Joe** — never mute/filter/narrow a monitor or alert.
- **SRP** — split conflated jobs before extending; feed the event stream, don't bake in a verdict.
- Commit authority: granular, to main, specific files, pytest-green. NOT push, NOT destructive. ALTER on the
  live DB needs an exact named instruction. Never touch/change o9-live without explicit authorization.

## Open items
- **Mid-band curl divisor** (8–14): optimal `TF/div` is an open sweep (task #6). This is the give-back lever —
  the base arm fires at the 150s curl seam and the exit lands past the turn. See [take_profit](./take_profit.md).
- **Arm cancel:** one opposite `s5m` breach vs the s2Mage cancel-stay — A/B run (2 recovered, 0 lost), Joe's
  verdict pending. See [arm_cancel](./arm_cancel.md).
- **Stale-hunt bound:** `s5m` IB for N consecutive seams — proposed, not adopted. See [arm_ladder](./arm_ladder.md#stale-hunt-hazard-open).
- **s15a definition (`fin_s30M_oob`):** Major-OOB-required vs mini-only — Joe's call. See [finisher](./finisher_6of9.md#s15a-definition--open).
- **Backstop tightening:** the IB-return exit is looser than an arm exit (14:01 held to 16:45).
- **Test the next 2 HTFs** (not 1) for pred/breach — Joe's read on 05:15/05:24/11:02 (a TF6 that already
  breached but armed at TF5); changes the apex, not the arm rule.
- **No trading for 4 hours** after a ~2% fast move (the 08:54 case wrecks the calcs).
- **Roll the HTF window** to kill the sawtooth — changes every line; Joe's authorisation. See [tape_hazards](./tape_hazards.md).
- **Write s15M/gcs5M = 37|0.6|ohlc4 to `indicator_configs`** — okayed, held until nof9 proven (blast radius).
- **Maker fills** — the cost lever; needs a fill-probability model. See [cost_and_edge](./cost_and_edge.md).
- **Exit finisher `s15a → gcs1a`** when 1s klines exist (task #5).
- **18:54 long-arm** — why the long ladder didn't latch (peel back after the AD-TP pipeline).
