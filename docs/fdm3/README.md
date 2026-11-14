# fdm3 — the index

GOAL: hold every fdm3 mech in one place, so a reader can find what each one decides without
reading the code.

---

## what fdm3 does

fdm3 reads the state of the market at the moment a trade opens and shapes that trade's walk to suit
it, rather than running one fixed walk shape in every condition. Its first mech, `fdm3-sideways`,
asks a single question at the open bar — is the market consolidating or running — by taking the
`pxs` pivot inside a `ws1b` oob excursion and reading whether the `ws{fdm3-sideways-trigger}` b and
r lines are out of bounds there; a consolidating market leaves `sideways == true`, the resting
state, and a running one turns it off for the life of the trade. The flag can only ever turn off,
never back on, and it is re-tested at every ws1 seam so a market that starts flat and then runs is
caught mid-walk. A second, slower path can also turn it off: a `pxs` retest that compares two
`ws{fdm3-sideways-trigger}` OHLC open extrema twenty-five minutes apart and, when they sit within
`fdm3-sideways-retest-diff-pct` of each other, asks the divergence read whether `ws3r`, `ws4r` or
`ws5r` disagrees with price across that span.

---

## the mechs

| the mech | its doc | what it decides | state |
|---|---|---|---|
| `fdm3-sideways` | [fdm3-sideways.md](fdm3-sideways.md) | whether a trade opens in sideways mode | the trigger and the retest are specified and matched against Joe's examples. What sideways mode DOES is not yet specified. Only a probe exists |
| `fdm3-oracle` | [docs/octo-freedom/1022_v4/out/fdm3_oracle.py](../octo-freedom/1022_v4/out/fdm3_oracle.py) | it SHOWS, it does not decide: one row per closed-prev ws1 bar, one cell per wsf line, carrying `breaching_line.predict_breach`'s -1/+1 on the emerging r, m and Mage, with the word towards or away under each cell | LIVE on port 8788 as the `o9-fdm3-oracle` unit. Renamed from `fdm2-oracle` at his 1114 *"rename it to fdm3-oracle in all places... you can take ownership of it now"*, and owned by this session from that bar. The installed systemd unit still carries the OLD name and needs his password to change - see the commands in the handover |

---

## obscure or unexpected uses of a mech

| the mech | the ordinary use | how fdm3 uses it |
|---|---|---|
| the divergence read, `jig.anchor_floater` | timing an EXIT. A divergence between price and an oscillator is traditionally read as a warning that the move in progress is tiring, so it is used to leave a trade | fdm3-sideways reads it on the trade about to BEGIN. Joe 1114: *"divergences are traditionally used to time an exit. in sideways mode, we want divergence to tell us how to handle the trade that is about to begin"*. The sign is therefore compared against the OUTGOING trade's side, not the incoming one |
| `jig.anchor_floater`'s own anchor and floater selection | the producer picks both bars itself, through its four-step look-back from one bar `k` | fdm3-sideways already knows which two bars to compare, so steps 1 to 3 must not run. `jig.anchor_floater_given` is Joe's ruled entry point: step 4 alone, on two bars handed in |
| a price match from the divergence read | `state ±2` is real evidence — price and the oscillator AGREE, the trend continuing | fdm3-sideways IGNORES it. Joe 1114: *"Price Match (state +/-2) will be ignored by sideways mode"*. Only `abs(state) == 1` counts |
| the `sideways` verdict's owner | a verdict read at a decision bar normally belongs to the trade being CLOSED, because the exit is the lever | `sideways` belongs to the trade being OPENED. Joe 1114: *"if we applied a sideways verdict to the incoming trade, that information would be lost when the incoming trade ends"* |
| a `ws1b` oob excursion | fdm2's cadence event is a `ws1b` oob→ib cross with its own nestle and gate tests | fdm3-sideways uses the same excursion as a CONTAINER — it looks inside it for the most extreme `pxs` bar, and the excursion's side sets every read's side |
| a bar's OHLC open | the lines and the backtest run off closes, highs and lows | the retest's two comparison points are OPENS of `ws{fdm3-sideways-trigger}` bars, which are not on disk and come from `kline_collection` directly |

---

## the knobs

All fdm3 knobs live in [fdm3_knobs.py](fdm3_knobs.py), not in `v4_knobs`, so a v4 ruling and an
fdm3 ruling cannot move each other. Banked means the default has moved and an off-ruled run raises
at import unless `W_FDM3_EXPERIMENT=1`. The env override is `W_FDM3_<NAME>`.

| the knob | his name | value |
|---|---|---|
| `SIDEWAYS_TRIGGER` | `fdm3-sideways-trigger` | 5 |
| `SIDEWAYS_RETEST_SCAN_WINDOW` | `fdm3-sideways-retest-scan-window` | 12.5 |
| `SIDEWAYS_RETEST_DIFF_PCT` | `fdm3-sideways-retest-diff-pct` | 0.88 |

---

## how the spec arrives

Joe 1114: *"the full spec is huge so I'm teaching you and validating us in chunks"*. Each chunk is
read for holes before anything is built, the holes go back to him as a numbered list, and only his
answers go into these docs. A reading that is mine and not his is labelled MINE wherever it appears.
