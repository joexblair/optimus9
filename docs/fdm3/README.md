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
| `fdm3-ltf-5aw-6x` | [oracle_rows.py](oracle_rows.py), `ltf_5aw_6x` | an aw-exhaust event — five gates over a 3-row window of the oracle's rows: >=6 of ws1..ws8 carrying an x-cross inside 1 row, >=10 of ws1..ws15 crossing collectively, <=1 of ws8..ws15 printing exf, >=10 timeframes reading AW(\*), and >=5 new AW prints | **CONFIRMED by Joe 1116.** The evidence is [out/ltf_5aw_6x_0920_0923_A_ws1_ws6.txt](out/ltf_5aw_6x_0920_0923_A_ws1_ws6.txt) — 40 instances over 09-20..09-23, read with A ws1-ws6 on. What an aw-exhaust event DOES is still unspecified |
| `fdm3-4-ltf-aws` | [oracle_rows.py](oracle_rows.py), the `find` and rate modes | an aw-exhaust event — >=4 AW flips on one row within ws1..ws6, with >=13 of ws1..ws15 crossing collectively, both inside a 4-row window | built and measured: 816 rows over the tape, 8.6 a day. His 09-23 0157 example matches exactly. Not confirmed |
| `fdm3-ltf-xcross` | [oracle_rows.py](oracle_rows.py), `ltf_xcross` | >=6 of ws1..ws8 carrying an x-cross inside 2 rows, inside 3 rows carrying 13of15, with >=4 timeframes reading AW(\*) and >=2 new AW prints | built and measured: 19,687 rows over the tape, 208.3 a day. Four of his five examples fire on the row he named and 09-24 2230 one row later. Not confirmed |
| `fdm3` xe-all-in | [oracle_rows.py](oracle_rows.py), the rate mode | an xe-exhaust event — 15of15 in a 2-row window | built and measured: 6,397 rows over the tape, 67.7 a day. **His 09-25 0547 example does not reproduce** — 0546 prints ws2 alone and 0547 prints six timeframes. Not confirmed |
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
| an x-cross and an e-cross | each print is its own event, and a timeframe can print several inside one window | every fdm3 scenario counts a cross ONCE per timeframe per window, so either count tops out at 15. Joe 1115: *"the x and e crosses are 1 type per TF per scenario (ie the max for any scenario is 15 of e and 15 of x)"*. The per-timeframe double prints stay unread until he rules on them |
| the oracle's A buttons | a viewing option on the page, for looking at the lift-off reads a different way | `fdm3-ltf-5aw-6x` is BANKED with A ws1-ws6 on, so a page option is part of a mech's definition. It moves the AW columns only — the x and e cross bits are built outside the oracle's state loop and no A button can touch them |

---

## operating the oracle

| | |
|---|---|
| the unit | `o9-fdm3-oracle.service`, enabled, running as `joe` from `docs/octo-freedom/1022_v4/out` |
| the page | 127.0.0.1:8788 |
| the log | `/home/joe/thecodes/fdm3_oracle.log` |
| **a restart costs ~18 minutes** | Joe 1114: *"it takes ~18 minutes to restart"*. The 7 towards/away runs go one after another at 97.9 s to 109.4 s each, and the matrix is in memory with no disk cache |
| so | a restart is EXPENSIVE. Batch code changes to that file, and read the running page rather than restarting to check something |
| the standing idea for cutting it | Joe 1113: build the 8 combinations in parallel. cupy 14.1.1 and one RTX 3060 Ti are available, and every state must stay byte-identical to the serial page |

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
| `MOM_FNC` | `fdm3-23-77-fnc` (MY name, off his `fdm-20-80-fnc`) | 23.0 |
| `LTF_XCROSS_HITS` | `fdm3-ltf-xcross-hits` | 6 |
| `LTF_XCROSS_ROWS` | `fdm3-ltf-xcross-rows` | 2 |
| `LTF_XCROSS_MAXTF` | `fdm3-ltf-xcross-maxTF` | 8 |
| `LTF_XCROSS_NOF15_ROWS` | `fdm3-ltf-xcross-nof15-rows` | 3 |
| `MIN_AW_PRINTS` | `fdm3-min-aw-prints` | 4 |
| `MIN_AW_FLIPS` | `fdm3-min-aw-flips` | 2 |
| `LTF_5AW_6X_XCROSS_ROWS` | `fdm3-ltf-5aw-6x-xcross-rows` | 1 |
| `LTF_5AW_6X_MIN_AW_PRINTS` | `fdm3-ltf-5aw-6x-min-aw-prints` | 10 |
| `LTF_5AW_6X_MIN_AW_FLIPS` | `fdm3-ltf-5aw-6x-min-aw-flips` | 5 |
| `LTF_5AW_6X_A_WS1_WS6` | the oracle's A ws1-ws6 button (MY name) | 1 |
| `LTF_5AW_6X_A_WS7_WS15` | the oracle's A ws7-ws15 button (MY name) | 0 |

`fdm-20-80-fnc` in `v4_knobs` stays at 20.0. Joe 1115: *"keep it as a fdm3 fence"* — so fdm2 step
1, the reversal population, the handoff walk's candidate test and the re-entry's inside test are
untouched by the 23/77 move.

---

## how the spec arrives

Joe 1114: *"the full spec is huge so I'm teaching you and validating us in chunks"*. Each chunk is
read for holes before anything is built, the holes go back to him as a numbered list, and only his
answers go into these docs. A reading that is mine and not his is labelled MINE wherever it appears.
