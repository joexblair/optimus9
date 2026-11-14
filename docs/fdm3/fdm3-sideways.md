# fdm3-sideways

GOAL: tell a trade, at the moment it opens, whether the market is consolidating — so the walk can
take a different shape in a market that is going sideways than in one that is running.

Joe's words for why it exists: *"sideways mode (needed to handle market consolidation)"*.

---

## the spec, in simple words

- a trade is either in **sideways mode** or not. The flag is called `sideways`.
- `sideways` is set **once, at the open bar of the outgoing trade** — the trade being opened.
  - it is set on the OUTGOING trade on purpose. Joe 1114: *"if we applied a sideways verdict to the
    incoming trade, that information would be lost when the incoming trade ends"*.
- the resting state is **`sideways == true`**.
- **the trigger** — what turns it off:
  - find a `pxs` pivot: the bar where `pxs` is at its most extreme inside a `ws1b` oob excursion,
    on the same side as that excursion.
    - if `pxs` sits flat at that extreme over several bars, take the LAST of them.
  - at that pivot bar, read `ws{fdm3-sideways-trigger}b` and `ws{fdm3-sideways-trigger}r`,
    both closed-prev.
  - if EITHER of those two lines is oob, `sideways == false` for the whole trade.
  - if neither is oob, `sideways` stays true.
- **the flip** — the only one allowed:
  - `sideways == true` may become `false` later in the walk.
  - `false` can NEVER go back to `true`. Joe 1114: *"the in-walk sideways flip to non-sideways is
    the only allowed flip in the trade"*.
  - the flip is tested at **every ws1 seam**, until the walk ends.
  - the test at a seam is the plain trigger above, not the retest below.
- **the retest** — a second way to reach `sideways == false`, run when the plain trigger has not
  fired:
  - if `ws1b` is oob at the bar being read, walk FORWARD until `ws1b` is ib. That ib cross is the
    `pxs-retest-anchor`.
    - this is a forward walk, not a lookahead: the decision is made AT the ib bar.
  - from the anchor, walk BACK to the last same-side `ws1b` oob→ib cross. That is the
    `pxs-retest-floater`.
    - the floater and the anchor must have at least one `ws1r` crossing UNDER 50 between them.
      Joe 1114: this describes a full `ws1r` cycle, which starts and finishes on the same side of 50.
    - if the nearest candidate fails that test, keep walking back. There is no bound.
  - IF `ws{fdm3-sideways-trigger}b` or `ws{fdm3-sideways-trigger}r` is closed-prev oob at the
    floater bar:
    - build a window of `fdm3-sideways-retest-scan-window` minutes each side of the floater, and
      take the same-side `ws{fdm3-sideways-trigger}` OHLC **open** extremum inside it.
    - build the same window around the anchor, and take its same-side open extremum.
    - IF the gap between those two opens, as a percent of the EARLIER of the two, is at or under
      `fdm3-sideways-retest-diff-pct`:
      - feed the two EXTREMUM bars to the divergence read, and test `ws3r`, `ws4r` and `ws5r`.
        - Joe 1114: *"the anchor and floater should be found at the same-side ws5 OHLC open
          extremum inside that 25min window, so the timestamps should be multiples of 5 minutes"*.
          The two `ws1b` cross bars only CENTRE the windows; they are not what the divergence reads.
        - the verdict is read on the same side as the `ws1b` excursion.
      - IF ANY of the three prints a divergence on that side, `sideways == false`.
  - ELSE IF neither of those two lines is oob at the floater bar:
    - do nothing.

---

## the knobs

| the knob | his name for it | its value | what it is |
|---|---|---|---|
| `SIDEWAYS_TRIGGER` | `fdm3-sideways-trigger` | 5 | the ONE timeframe whose b and r lines the trigger reads, closed-prev at 300 s |
| `SIDEWAYS_RETEST_SCAN_WINDOW` | `fdm3-sideways-retest-scan-window` | 12.5 | minutes each side of a retest bar, so a 25 minute span |
| `SIDEWAYS_RETEST_DIFF_PCT` | `fdm3-sideways-retest-diff-pct` | 0.88 | the open-extremum gap ceiling, as a percent of the EARLIER open |

They live in `docs/fdm3/fdm3_knobs.py`, NOT in `v4_knobs`, so a v4 ruling and an fdm3 ruling cannot
move each other. An off-ruled run raises at import unless `W_FDM3_EXPERIMENT=1`.

---

## the readings that are MINE and are NOT ruled

| the reading | what I chose | why it was open |
|---|---|---|
| the anchor bar | the excursion's own `ws1b` oob→ib cross | read off his *"walk forward until ws1b is ib"*. He has not said what the anchor is at a seam where `ws1b` is already ib |
| `ws1r`'s read for the under-50 cross | closed-prev at 60 s | he named the cross but not the read |
| the r lines fed to the divergence | `ws3r`, `ws4r`, `ws5r` closed-prev | he named the lines but not the read |

The price the divergence reads is NOT mine: it is the RAW close, which the Jig already rules —
*"DEMA-smoothing the price slope DESTROYS it. The raw price slope is correct."*

---

## what was learned building it

- **the two triggers he first wrote were not complements.** `(b is not oob OR r is not oob)` against
  `(b is oob OR r is oob)` both fire whenever one line is oob and the other is not, and that is
  14.3% of all bars — 233,340 of 1,630,020 on the LOW side. His own 2026-09-23 0405 example sat in
  that overlap. It was resolved by making `sideways == true` the resting state and `false` the only
  thing a trigger can do, which needs no order between two tests because there is only one test.
- **the trade's DIRECTION and its TARGET side are different things, and only one of them is locked
  to the excursion side.** A SHORT is born only of a HIGH-side excursion and a LONG only of a
  LOW-side one; but a SHORT hunts the LOW oob and a LONG the HIGH oob, so the target side is the
  opposite of the excursion side. Reading the divergence sign through the target side instead of the
  direction gives the wrong answer silently. The only safe form is one row per case:

  | the `ws1b` excursion side | the trade born of it | the oob it hunts | the divergence state that fires |
  |---|---|---|---|
  | LOW | LONG | high oob | `−1` |
  | HIGH | SHORT | low oob | `+1` |

- **a price match is not a divergence.** `jig.anchor_floater`'s `state` has five values, not two:
  `±1` divergence, `±2` price match, `0` the noise band, and `None` when it cannot pick a pair.
  Joe 1114: *"Price Match (state +/-2) will be ignored by sideways mode"*, so a caller tests
  `abs(state) == 1` and nothing else.
- **the divergence producer could not take two supplied bars.** `jig.anchor_floater` DERIVES its own
  anchor and floater through its steps 1 to 3. `jig.divergence` takes two indices but is
  pseudo-disabled. Joe ruled a new entry point, and `jig.anchor_floater_given` is it: step 4 and
  nothing else, sharing the same `d_osc` / `d_px` / `AF_SLOPE_FLOOR` / `state` arithmetic so the
  two cannot drift.
- **his `pxs-retest-floater` is NOT `anchor_floater`'s floater.** His is a `ws1b` oob→ib cross; the
  producer's own is an r extremum from its step 3. His name stays; the new entry point is forbidden
  from deriving a pair of its own and says so in its docstring.
- **feeding the cross bars instead of the extremum bars changed the answer.** On 2026-09-21 the
  13:32 and 13:34 excursions read price match on all three r lines off the cross bars, and
  `sideways == false` off the extremum bars. Two of nine excursions flipped.
- **a bar's OPEN is not on disk.** The cached arrays hold t/h/l/c only. The real 5 s opens come from
  `kline_collection`; using the previous close as a proxy would have been my number, not the
  exchange's.
- **grazes are expected and are not a fault.** Joe 1114: *"this shows that there are grazes, which
  is fine. each graze is not directly impacting a trading decision's profit - if the next excursion
  detects sideways-false then the walk will dynamically change its shape"*.

---

## his examples, matched

Run by `docs/octo-freedom/1114_sideways/sideways_probe.py`, which is a PROBE and not the mech.

| the `ws1b` excursion | side | the pxs pivot | ws5b | oob | ws5r | oob | the RAW verdict | the FINAL verdict |
|---|---|---|---|---|---|---|---|---|
| 2026-09-21 12:58:00 .. 13:00:55 | HIGH | 2026-09-21 12:59:50 | 61.92 | no | 77.83 | no | true | do nothing — his ELSE IF |
| 2026-09-21 13:02:00 .. 13:10:55 | HIGH | 2026-09-21 13:02:00 | 68.42 | no | 80.38 | no | true | do nothing — his ELSE IF |
| 2026-09-21 13:32:00 .. 13:32:55 | LOW | 2026-09-21 13:32:15 | 40.21 | no | 62.51 | no | true | sideways == FALSE — divergence |
| 2026-09-21 13:34:00 .. 13:34:55 | LOW | 2026-09-21 13:34:15 | 40.21 | no | 62.51 | no | true | sideways == FALSE — divergence |
| 2026-09-21 13:37:00 .. 13:42:55 | LOW | 2026-09-21 13:39:50 | 37.70 | no | 48.43 | no | true | sideways == FALSE — divergence |
| 2026-09-21 14:06:00 .. 14:08:55 | LOW | 2026-09-21 14:08:00 | 34.52 | no | 39.82 | no | true | do nothing — his ELSE IF |
| 2026-09-23 04:00:00 .. 04:01:55 | LOW | 2026-09-23 04:00:05 | 53.36 | no | 18.13 | no | true | sideways == true — the diff is 1.8033%, too wide |
| 2026-09-23 04:03:00 .. 04:06:55 | LOW | 2026-09-23 04:06:40 | 46.47 | no | 9.92 | OOB | FALSE | sideways == FALSE on the raw trigger |
| 2026-09-23 04:24:00 .. 04:30:55 | HIGH | 2026-09-23 04:25:55 | 69.51 | no | 35.61 | no | true | sideways == FALSE — divergence, all three r lines `+1` |

- his `sideways == true` example, 09-21 1340: the 13:37:00 .. 13:42:55 excursion, pxs low at
  13:39:50, neither ws5 line oob. The raw trigger matches. The retest then flips it, which is the
  mech working, not a mismatch with his read.
- his `sideways == false` example, 09-23 0405: the 04:03:00 .. 04:06:55 excursion, pxs low at
  04:06:40, ws5r oob at 9.92. Matches on the raw trigger alone.
- his retest example, 09-23: the anchor cross lands 04:31:00 against his *"~0431"*, the floater
  cross 03:27:00 against his *"~0326"*, and the two extremum bars are the 03:25:00 and 04:30:00
  ws5 opens — the two bars he named.

---

## what is NOT built, and what is still unruled

| | |
|---|---|
| what `sideways == true` DOES to the walk | NOT SPECIFIED. The spec is trigger-only; Joe is handing it over in chunks |
| `6x-AWflip` | the rev-trade event that opens his 2026-09-24 1501 example. Parked for a different chunk |
| `ws1b` for sideways-false against `gcws30b` for sideways-true | Joe 1114: *"don't dive into this yet"* |
| the mech itself | only the probe exists. `sideways` is not attached to any trade yet, because it belongs to the outgoing trade and the opener above is not built |
