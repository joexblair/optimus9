# ws1mage-rev <-> octo-freedom: the coupling, measured

Joe 1005: *"we need to unpack octo-sig. it seems that ws1mage-rev is too tightly coupled with
octo-freedom - am I wrong?"*

**Not wrong.** The coupling is at the ENTRY BAR, which is tighter than a gate. And it runs through
ONE of the producer's four knobs; the other three are severed.

## WHERE IT SITS IN THE WALK

`optimus9/compute/leash_walk.py` `LeashWalk.step`, the last five lines:

    if self._turn is None or self._qual is None:      return False     # the turn + the qualify
    if k < max(self._turn, self._qual):               return False     # the scan bound
    if sum(1 for x in self._fr_starts if lo <= x <= k) < self.race:    # the race
                                                      return False
    return bool(rev_ok)                                                # <- THE WS1MAGE-REV LOOKBACK

- arm / turn / qualify / race are PRECONDITIONS. `rev_ok` is the deciding line.
- `rev_ok` comes from `rev_lookback_mask(legs['sig'], legs['sig_conf'], n, rev_lookback)` —
  `report_leash_walk.py:201`.

## BAR LEVEL — rev cuts two thirds of the candidate bars

ALL-TRUE arm = the rev mask replaced with ones, so every bar reaching the last line fires.

| day | bars reaching the last line | rev passes | rev selectivity |
|---|---|---|---|
| 09-25 | 8,317 | 2,801 | 33.7% |
| 10-02 | 9,464 | 3,278 | 34.6% |
| 10-03 | 8,992 | 3,046 | 33.9% |
| 10-04 | 10,282 | 3,719 | 36.2% |
| 07-23 | 5,488 | 1,558 | 28.4% |
| 08-30 | 10,225 | 3,774 | 36.9% |
| **total** | **52,768** | **18,176** | **34.4%** |

## SIGNAL LEVEL — it is not a veto, it MOVES THE FIRE BAR

`walk_fires_from` takes the FIRST bar of each consecutive emitted run. When rev is false across the
front of an otherwise-satisfied run, the fire bar becomes the first bar where rev goes true. So the
rev leg does not only delete signals — it decides WHICH BAR of the run is `WALK FIRES FROM`.

| day | with rev | without rev | identical timestamps | only WITH rev | only WITHOUT rev |
|---|---|---|---|---|---|
| 09-25 | 39 | 45 | 22 | 17 | 23 |
| 10-02 | 43 | 44 | 24 | 19 | 20 |
| 10-03 | 32 | 37 | 20 | 12 | 17 |
| 10-04 | 30 | 43 | 18 | 12 | 25 |
| 07-23 | 16 | 20 | 11 | 5 | 9 |
| 08-30 | 35 | 43 | 19 | 16 | 24 |
| **total** | **195** | **232** | **114** | **81** | **118** |

| reading | value |
|---|---|
| octo-sigs the rev leg leaves on the same bar | **114 of 195 = 58%** |
| octo-sigs whose BAR exists only because rev gates | **81 = 42%** |
| octo-sigs the rev leg deletes | 118 |

**42% of octo-sig entry bars are placed by the ws1mage-rev lookback.**

## ONE WIRE OF FOUR IS CONNECTED

| the producer's knob | what it feeds | reaches the walk |
|---|---|---|
| `dwell` | `dwell_ok` | **NO — inert** (12 sweep cells, 1 result) |
| `rev_wob` | `rev` | **NO — inert** (8 sweep cells, 1 result) |
| `gate='rev'/'off'` | `rev` | **NO — inert** (356,818 -> 0 changes nothing) |
| `lookback_s` -> `rev_lookback` | the mask width | **YES** |

And the one live wire is the strongest knob in the whole 630-cell upstream sweep:

| lookback_s | FIT n | FIT mean | TEST n | TEST mean | growth |
|---|---|---|---|---|---|
| **60** | **201** | +0.2891 | **119** | **+0.3817** | **1.056893** |
| 90 | 191 | +0.2966 | 111 | +0.3665 | 1.052972 |
| 150 | 170 | +0.2866 | 120 | +0.3735 | 1.054365 |
| **240 (live)** | **166** | +0.3213 | **110** | **+0.2849** | **1.042213** |
| 360 | 148 | +0.2914 | 102 | +0.2396 | 1.038068 |
| 600 | 146 | +0.2890 | 103 | +0.2370 | 1.032943 |

- it is not a filter width. It is **entry timing**, and shortening it to 60 s adds 35 FIT trades and
  9 held-out TEST trades while raising held-out mean from +0.2849 to +0.3817.

## IT REACHES THE RULINGS ON THE TABLE

09-25, the 39 scored rows: **17 of 39 fire bars exist only because the rev leg gates**, including
rows awaiting a ruling —

| octo-sig | status | route | placed by rev |
|---|---|---|---|
| 02:42:35 | BLOCKED | mtd.r2 | YES |
| 18:14:15 | OPEN · band claimed | mtd.r1 | YES |
| 19:49:55 | OPEN · no r block | mtd.r1 | YES |
| 19:54:00 | BLOCKED | mtd.r2 | YES |
| 20:04:45 | OPEN · band claimed | mtd.r1 | YES |

## WHAT THIS IS, PLAINLY

- **structurally** the walk is clean: one producer, one consumer, `step_bar` shared by backtest and
  live, no copied routing.
- **mechanically** it is one wire. Three of the producer's four knobs are computed, applied, and
  discarded before the walk sees them, so `ws1mage-rev` as a MECHANIC is not in octo-freedom —
  only its `sig` cross and a lookback width are.
- the tight part is that the one surviving wire sets **42% of entry bars**, and it is the knob with
  the most held-out effect in the sweep.

**FOR JOE TO RULE:** whether octo-sig's entry bar should be placed by the rev lookback at all, or
whether the walk should emit on the race and let `ws1mage-rev` (3 legs, via `jig.mage_rev_walk`
which has zero callers) be a separate confirmer. Both are builds, neither is mine to choose.
