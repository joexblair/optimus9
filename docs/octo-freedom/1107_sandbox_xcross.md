# The sandbox x-cross mech, and the reads built beside it, 2026-11-07

HIS 1108: *"bank, update specs and make knobs durable"*.

PLAINLY: the sandbox x-cross mech prints one report per cadence event. Each report lists the r values
ws30r..ws10r at a ws{TF}x extremum and at its cross. Beside the mech sit a fake cadence (experimental), two
lines he named (ws{TF}e and ws{TF}r2), and the RSI divergence read `bullish-rsi` / `bearish-rsi`. Every knob is
banked: the default is his value, and a run with a knob off the bank refuses unless it declares itself an
experiment.

The code is `1107_sandbox_xcross/`. The knobs are `1107_sandbox_xcross/sandbox_knobs.py` and the Jig's `RSIDIV_*`.

---

## 1. THE SANDBOX x-CROSS MECH - HIS FOUR ITEMS

HIS 1107: *"the next data collection will be built by these 4 items: the cadence, the highest TF selected, the
ws{TF}x cross after the cadence, and the report"*.

| # | item | what it is | his words |
|---|---|---|---|
| 1 | the cadence | `v4_fdm2.cadence_events`, the BUILT version: ws1b's oob excursion, the cross back to ib, the nestle, the ws3Mage ex-25/75 gate with its rescue | *"we'll be using the built version"* |
| 2 | the TF | the highest line ws1..ws30 that is ex-20/80 AND towards at the cadence event | *"at the cadence event, find the highest es-20/80-fence towards line and make that the TF for the ws{TF}x cross"* |
| 3 | the x-cross | `v4_fdm2.x_race` on that TF, from the cadence event: the first of ws{TF}x to ib, to ws{TF}r, to ws{TF}Mage that holds 24 bars = 120 s, counting the cross bar | *"the trade won't be considered. this means you can use the side of the cadence to dictate the side of the ws{}x cross"* |
| 4 | the report | the r table below, one per cadence event, printed one after another | *"the reports will be printed consecutively, in a text file"* |

- HIGH and LOW cadence events go to separate files, his *"repeat the mech's run for the lowside cadence events,
  and dump their consecutive reports into a separate text file"*.
- ws{TF}x is read emerging. Its r and Mage racers are read closed-prev, as `x_race` was built.
- ex-20/80 is `v4_fdm2.ex2080_line`, reading either: the closed-prev value, or the emerging extreme over 12 bars =
  60 s (`FDM_EXF_READ` 'either', `FDM_EXF_EM_BARS` 12, both in v4_knobs).

## 2. THE REPORT

HIS 1107: *"report the ws30r to ws10r emerging values in a 22 column table"*, then *"delete these sections from
both files"* (the per-event item table) and *"drop the r2 rows, and replace them with r rows that were calculated
on ws5x"*.

| row | what it holds |
|---|---|
| banner | the cadence side, the cadence event's time, and "n of N" |
| r · extremum | ws30r..ws10r, EMERGING, at the ws{TF}x extremum: `jig.mage_cascade_bar`'s walk back to look forward, in 48-bar = 240 s steps from the cross bar |
| r · cross | ws30r..ws10r, EMERGING, at the ws{TF}x cross bar |
| r · diff | cross minus extremum, per column |
| r · direction | up, down, or flat (exactly 0) |
| the ws5x block | the same four rows on ws5x, whatever TF the cadence selected - no dynamic selection. When the selected TF is ws5, the two blocks are the same rows |

- The r line is the stored ws{TF}r: StochRSI 7|5|8|close in his notation (k_len|rsi|stc|src).
- Each file opens with a legend table: the day, the side, the tape's bar count, v4's knob hash with its
  off-the-bank list, and every read in this section.
- `--fake` prints the same report for the fake cadence events, on screen.

## 3. MINE - READS HE HAS NOT RULED

Each one is printed in the files' legend as `MINE:`.

| read | what the code does | the other reading |
|---|---|---|
| towards | step 1's trajectory reader, no anchor | the director's reader, which needs the trade open as its anchor - the dependency his sandbox rule exists to remove |
| the TF scan | ws1..ws30, the director's range | step 1 scans ws4..ws30 |
| the race bound | the tape end | the built fdm2 leg walk stops at the next cadence event |
| the first report row | the ws{TF}x extremum | the cadence event bar |
| the walk back | not bounded, so the extremum may sit before the cadence event | bounded at the cadence event |
| `FAKE_DAY` | 2026-08-25, the day every 1107 sandbox read was on | his fake window named no day |

## 4. THE FAKE CADENCE - EXPERIMENTAL

HIS 1107: *"experimental:  I need you to fake a cadence event whenever ws1b crosses to ib, while ws1Mage was oob
during ws1b's oob excursion, from 1745 to 1920. these will all be high side events"*, *"show the list of reports
onscreen - no summaries"*.

- A fake event is a closed-prev ws1b cross from the high oob (85) back to ib, inside 17:45:00..19:20:00.
- It is kept when closed-prev ws1Mage is at or over 85 on at least one bar of the oob excursion before the cross.
- Each kept event runs through the sandbox mech's own report, banner `HIGH FAKE cadence event`. That banner is MY
  label: he has not named this report (asked 1108, *"what did we name this report"*).
- One comment line prints per ws1b cross in the window, kept or not, with the excursion and its ws1Mage maximum.
- It lives in `sandbox_xcross.py` (`fake_events`, `fake_main`), so it reads the same driver as the real cadence.

## 5. THE LINES HE NAMED

| line | his words | spec | built by | read by |
|---|---|---|---|---|
| ws{TF}e | *"a BB%B line with len 4 and multi 0.5, src: close"*, *"going forward I'll refer to this line as ws{TF}e"* | BB%B 4\|0.5\|close at the TF | `sandbox_xcross.e_line(tf)`, in memory | no report |
| ws{TF}r2 | *"create a new `ws{TF}r2` stochrsi line: klen:6, rsilen:6, stochrange:10, src close"* | StochRSI 6\|6\|10\|close (k_len\|rsi\|stc\|src) | `sandbox_xcross.r2_lines()`, ws10r2..ws30r2 in memory | no report since he dropped its rows |

- Neither line is written to the line cache.
- Each build carries a control row built in the same Jig, which must equal the cached line exactly or the build
  refuses: ws{TF}Mage for ws{TF}e, ws30r for ws{TF}r2.
- ws{TF}r2 goes through the named `KLine`, so the legacy tuple order ('k', rsi, stc, k_len, src) cannot transpose.

## 6. `bullish-rsi` / `bearish-rsi` - THE RSI DIVERGENCE

HIS 1107, after price made a lower low and RSI(5) a higher low from 2026-08-25 07:49 to 07:51: *"can you code it?
it would have its own label for any events that it claims: `{bearish,bullish}-rsi`"*. His purpose: *"I'm planning
to use divergence to enhance lift-offs timing, so that we get reversal events sooner"*.

- THE PRODUCER: `jig.rsi_divergence(close, rsi, gate, oob)`, on one line's own completed bars.
- THE DRIVER: `rsi_div.py <day>` writes `rsi_div_<day>_ws2b.txt`. THE PINE: `rsi_div_emit.py <day>` writes the
  matching `.pine` (gitignored; the emitter is the durable artefact).

| ruling | his words |
|---|---|
| the lines: the RSI under ws1r (60 s bars) and under gcws30r (30 s bars) | *"ws1r and gcws30r"* |
| the gate: same-side oob at the anchor bar only | *"while gcws30b is same-side oob"*, and he chose the anchor-only option |
| the gate line, BANKED ws2b, read closed-prev at 120 s | *"it's two noisy - lets try it with ws2b"*, then *"that's better.  bank it and update the jig producer"* |
| both sides | *"the mech needs to allow for both sides"* |
| one event per earlier point, its first anchor bar | he chose the first-bar-only option |
| an RSI-level gate, as a knob | *"your preference.  these 2 options should be chosen by a knob"* |
| THE WHOLE READ IS OFF BY DEFAULT | *"make this mode's default: off"* |

| read | what the code does | whose |
|---|---|---|
| the earlier point | the most recent low (high): a bar with a strictly higher (lower) close on both sides | MINE |
| fires, bullish-rsi | the anchor close is below that low's close AND the anchor RSI is above the low's RSI | MINE (strict) |
| fires, bearish-rsi | the mirror | MINE (strict) |
| distance to the earlier point | no limit | MINE |
| the RSI-level gate | `RSIDIV_LVL_GATE` 0 = off, my preference: the oob gate already restricts the read to a stretched move | MINE |
| price | the raw close, his 0711 finding that a smoothed price slope ruins the read | his |
| the stamp | the line's print bar, where closed-prev shows the completed bar | the closed-prev rule |

- THE CONTROL: the read's RSI, then stoch(stc), then the k_len average, rebuilds the stored ws1r and gcws30r on
  every print bar of the day. The driver prints the maximum difference in its legend.
- `rsi_divergence` called with its defaults returns no events. `rsi_div.py` passes `on=True` for its own run, and
  its legend says so.
- NOT CONSUMED by any mech yet. Measuring it against lift-off timing is the next step he described.

## 7. THE KNOBS, BANKED 1108

Generated from `sandbox_knobs.table()` and `jig.rsidiv_check()`, the live checks, not a claim. A knob off its
banked value refuses the run unless `W_SBX_EXPERIMENT=1` (the sandbox knobs) or `W_RSIDIV_EXPERIMENT=1` (the
RSI divergence) is set. The labels are mine; the values are his unless the row says MINE.

The sandbox knobs, `sandbox_knobs.py`, env `W_SBX_<NAME>`:

| the knob | value | units | ruled | Joe's words |
|---|---|---|---|---|
| `REPORT_TF_HI` | 30 | TF | YES | "report the ws30r to ws10r emerging values in a 22 column table" |
| `REPORT_TF_LO` | 10 | TF | YES | "report the ws30r to ws10r emerging values in a 22 column table" |
| `WS5X_TF` | 5 | TF | YES | "replace them with r rows that were calculated on ws5x" |
| `R2_KLEN` | 6 | bars | YES | "klen:6" |
| `R2_RSI` | 6 | bars | YES | "rsilen:6" |
| `R2_STC` | 10 | bars | YES | "stochrange:10" |
| `R2_SRC` | close | source | YES | "src close" |
| `E_LEN` | 4 | bars | YES | "a BB%B line with len 4" |
| `E_MULT` | 0.5 | std devs | YES | "multi 0.5" |
| `E_SRC` | close | source | YES | "src: close" |
| `FAKE_DAY` | 2026-08-25 | day | YES | MINE - his window named no day; every 1107 sandbox read was on 2026-08-25 |
| `FAKE_FROM` | 17:45:00 | UTC time | YES | "from 1745 to 1920" |
| `FAKE_TO` | 19:20:00 | UTC time | YES | "from 1745 to 1920" |

The RSI divergence knobs, in the Jig beside its producer, env `W_<NAME>`:

| the knob | value | ruled | Joe's words |
|---|---|---|---|
| `RSIDIV_ON` | 0 | YES | "make this mode's default: off" - the whole read, his choice |
| `RSIDIV_LINES` | ws1r, gcws30r | YES | "ws1r and gcws30r" |
| `RSIDIV_GATE` | ws2b | YES | "that's better.  bank it and update the jig producer" - on the ws2b pine |
| `RSIDIV_LVL_GATE` | 0 | YES | "your preference.  these 2 options should be chosen by a knob" - mine is 0 |
| `RSIDIV_LVL` | 30.0 | YES | MINE - only read when RSIDIV_LVL_GATE is 1 |
| `RSIDIV_GATE_TF` | ws2b 120 s, gcws30b 30 s | fixed | each gate line's own timeframe, not a knob |

NOT RE-DECLARED, each banked in its own home: the cadence, the ex-20/80 fence, the race's 24-bar wob and the
director range are v4_fdm2's, in `1022_v4/v4_knobs.py`; the walk back's 48-bar step (`MC_GAP`) is the Jig's.

## 8. HOW TO RUN

| command, from anywhere | writes |
|---|---|
| `python3 sandbox_xcross.py 2026-08-25` | `sandbox_xcross_2026-08-25_HIGH.txt`, `sandbox_xcross_2026-08-25_LOW.txt` |
| `python3 sandbox_xcross.py --fake` | the fake cadence reports, on screen |
| `python3 rsi_div.py 2026-08-25` | `rsi_div_2026-08-25_ws2b.txt` |
| `python3 rsi_div_emit.py 2026-08-25` | `rsi_div_2026-08-25_ws2b.pine` |
| `python3 sandbox_knobs.py` | the sandbox knob table, on screen |

- Every run prints its knobs first and stops before any output when one is off the bank.
- The gcws30b gate still runs as an experiment (`W_RSIDIV_GATE=gcws30b W_RSIDIV_EXPERIMENT=1`) and writes its own
  `rsi_div_<day>.txt` / `.pine`, so the banked ws2b files are never overwritten.

## 9. COUNTS AT THE BANK, 2026-08-25

| the run | knobs | count |
|---|---|---|
| HIGH cadence events, `sandbox_xcross_2026-08-25_HIGH.txt` | on the bank | 15 reports |
| LOW cadence events, `sandbox_xcross_2026-08-25_LOW.txt` | on the bank | 13 reports |
| fake HIGH cadence events, 17:45:00..19:20:00, `--fake` | on the bank | 7 reports (8 ws1b crosses; 2026-08-25 19:17:00 dropped, ws1Mage max 84.31) |
| `bullish-rsi` / `bearish-rsi`, ws2b gate, `rsi_div_2026-08-25_ws2b.txt` | on the bank | 55 events |
| ... ws1r bullish-rsi / bearish-rsi | on the bank | 11 / 12 |
| ... gcws30r bullish-rsi / bearish-rsi | on the bank | 13 / 19 |
| `bullish-rsi` / `bearish-rsi`, gcws30b gate, `rsi_div_2026-08-25.txt` | EXPERIMENT, off the bank | 130 events |
| ... ws1r bullish-rsi / bearish-rsi | EXPERIMENT, off the bank | 17 / 23 |
| ... gcws30r bullish-rsi / bearish-rsi | EXPERIMENT, off the bank | 43 / 47 |

| control | result |
|---|---|
| the tape | 1,632,960 bars, 2026-07-02 12:00:00 .. 2026-10-04 23:59:55 |
| the 1108 rerun on the banked knobs, against the files from before | HIGH, LOW, fake and the ws2b pine byte-identical; the ws2b events file identical but for one legend row |
| that legend row, corrected 1108 | the RSI-level-gate row read "off - gcws30b oob only" on the ws2b run; it now names the gate it ran on, ws2b |
| ws1r rebuilt from the read's RSI, 1,440 bars of the day | max difference 7.1e-14 |
| gcws30r rebuilt from the read's RSI, 2,880 bars of the day | max difference 1.1e-13 |
| ws12e from `e_line(12)`, against the 1107 in-memory build | 0 difference, 0 NaN mismatches; its ws12Mage control row exact |
| `rsi_divergence` called with its defaults | no events |
| `W_SBX_WS5X_TF=6` | REFUSED |
| `W_RSIDIV_LINES=ws1r` | REFUSED |
