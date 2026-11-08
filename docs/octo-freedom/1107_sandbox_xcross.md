# `fdm2-xcv`, and the reads built beside it, 2026-11-07

HIS 1108 NAME AND GO: *"take ownership of the files. bank them as the fdm2-xcv mech. commit and
push all files, yours or not"*. The mech was built in another session and handed over at log entry
#46; it is mine from 1108 and `fdm2-xcv` is its name. Earlier text in this file saying "the sandbox
x-cross mech" means `fdm2-xcv`.

HIS 1108: *"bank, update specs and make knobs durable"*.

PLAINLY: the sandbox x-cross mech prints one **xcross validator report** per cadence event. Each report lists
the r values ws30r..ws10r at a ws{TF}x extremum and at its cross, then again on ws5x. Beside the mech sit a fake cadence (experimental), two
lines he named (ws{TF}e and ws{TF}r2), and the RSI divergence read `bullish-rsi` / `bearish-rsi`. Every knob is
banked: the default is his value, and a run with a knob off the bank refuses unless it declares itself an
experiment.

The code is `1107_sandbox_xcross/`. The knobs are `1107_sandbox_xcross/sandbox_knobs.py` and the Jig's `RSIDIV_*`.

---

## 0. `fdm2-xcv` - HIS SPEC, 1108, VERBATIM

HIS 1108, after reading what I had built: *"it feels like you're over-complicating a simple mech /
this is all you need for now"*. His spec, as he wrote it:

```
diff-function()
    --use "walkback to look forward' to find the pre-cross extremum of ws{knob:5}x, and collect the line values for ws10-ws30
    --collect the line values for ws10-ws30 at the x-cross
    --report the diff(extremum,xcross) for each line

:START
IF a cadence event fires
-IF a ws{knob:5}x cross race:{Mage,boundary,r} event printed inside that cadence's window  #standard cross under for lowside / cross over for highside
--call diff-function
--make a verdict based on the ws30-ws10 diff pattern  (to be built)
-ELSE IF NOT ws{knob:5}x cross race:{Mage,boundary,r} event printed inside that cadence's window
--walk to race:{next cadence, x-cross}
--IF x-cross wins the race
---call diff-function
--ELSE IF next cadence wins the race
---goto START
```

### his 1108 rulings that fill the gaps in it

| the gap I raised | his ruling |
|---|---|
| one x line or two | ONE. *"this is on me - the top rows (the dynamic xcross and the ws4 xcross) were' just for my ref. ws5x is the one all of my timestamps were based on"*. `WS5X_TF` 5 is the `ws{knob:5}x` knob; my `XCV_TFS '4,5'` is removed |
| the verdict when it reads `none` | *"we haven't got that far yet"*. PARKED |
| the hold | **`FDM_X10_WOB` 24 bars = 120 s, counting the cross bar. `F2.x_race` owns the cross.** He ruled it out first - *"there is no hold - the cross is read raw"*, with his reason *"if the diff pattern doesn't give a usable result, then the cad walk will automatically consume the wob. if the diff pattern has a verdict, we've saved 2 minutes and gained profit"* - then reversed on the evidence below: *"ok - that makes the wob necessary"* |
| the ws10-ws30 read | *"emerging"* |
| which line ws10-ws30 is | *"ws10r to ws30r, on banked config"* - StochRSI 7\|5\|8\|close |
| what a skipped cadence prints | *"no note. if there's a fault to diagnose, I'll be looking at the charts and it will be obvious to me if the 'skipped' cadence has any impact on the debugging"*. NOTHING is printed |
| the no-duplicate-at-one-bar rule | *"stands"* |
| the rev-trade | *"not yet. I want to see the fundamentals aligned with me before we do anything more"* |

### HIS 1108 CAD WALK COLUMNS

His words: *"add 2 columns to this report, on the far righthand side: 1) the cad-walked timestamp
when 3 ups or 3 downs print after a 'none' `3of4 read`, 2) the up/down verdict / if `the 3-of-4
read` is not none for a row, the fields in the new columns will read '-'"*.

| what | the detail |
|---|---|
| when the walk runs | ONLY on a row whose 3-of-4 read is `none`. Every other row prints `-` in both columns |
| what is re-read | the extremum is FIXED - it is the pre-cross extremum. The SECOND row of the diff moves to the bar being read. That is the only reading under which the diff changes at all, and it is MINE |
| the bound | NONE APPLIED. He has not ruled one here, so the walk runs to the tape end and the delay is reported beside it. A bound can only cut rows, never add them |
| where it lives | the `xcv` request kind on the live process, so the table is repeatable on any day and any x line |

### WHY THE WOB IS NECESSARY - the measurement that reversed his own ruling

He asked why the report showed 2026-08-25 02:31:55 for the 02:22:00 HIGH event while the
no-hold build printed 02:22:40. The bars:

| the bar | ws5x emerging | oob at 85? |
|---|---|---|
| 2026-08-25 02:22:35 | 85.38 | OOB |
| **2026-08-25 02:22:40** | **83.76** | **crossed inside - the raw cross** |
| 2026-08-25 02:22:45 | 91.62 | OOB again, ONE BAR later |

ws5x crossed the 85 boundary downward and bounced straight back on the next bar. The held race
discarded that cross and six more between 02:30:15 and 02:31:30, all of which broke inside their
own 120 s, and took the seventh at 02:31:55 on ws5r.

His reading: *"ok - that makes the wob necessary"*. So the hold stands, `F2.x_race` owns the cross,
and `F2.x_cross_raw` - the no-hold reader I had added - is REMOVED. Two cross readers for one mech
is a drift trap, and nothing reads it now.

## 1. `fdm2-xcv` - HIS FOUR ITEMS

HIS 1107: *"the next data collection will be built by these 4 items: the cadence, the highest TF selected, the
ws{TF}x cross after the cadence, and the report"*.

| # | item | what it is | his words |
|---|---|---|---|
| 1 | the cadence | `v4_fdm2.cadence_events`, the BUILT version: ws1b's oob excursion, the cross back to ib, the nestle, the ws3Mage ex-25/75 gate with its rescue | *"we'll be using the built version"* |
| 2 | the TF | the highest line ws1..ws30 that is ex-20/80 AND towards at the cadence event | *"at the cadence event, find the highest es-20/80-fence towards line and make that the TF for the ws{TF}x cross"* |
| 3 | the x-cross | `v4_fdm2.x_race` on that TF, from the cadence event: the first of ws{TF}x to ib, to ws{TF}r, to ws{TF}Mage that holds 24 bars = 120 s, counting the cross bar | *"the trade won't be considered. this means you can use the side of the cadence to dictate the side of the ws{}x cross"* |
| 4 | the report | the xcross validator report below, one per cadence event, printed one after another | *"the reports will be printed consecutively, in a text file"* |

- HIGH and LOW cadence events go to separate files, his *"repeat the mech's run for the lowside cadence events,
  and dump their consecutive reports into a separate text file"*.
- ws{TF}x is read emerging. Its r and Mage racers are read closed-prev, as `x_race` was built.
- ex-20/80 is `v4_fdm2.ex2080_line`, reading either: the closed-prev value, or the emerging extreme over 12 bars =
  60 s (`FDM_EXF_READ` 'either', `FDM_EXF_EM_BARS` 12, both in v4_knobs).

## 2. THE xcross validator report

HIS 1108 NAME: *"let's name that report "xcross validator report" - it matches what it does"*. HIS 1108 BANK:
*"bank the latest version, the one that has ws5x as a static line for each table"* - the version below, with the
selected ws{TF}x block and the fixed ws5x block in every report. `WS5X_TF` is banked 5.

HIS 1107: *"report the ws30r to ws10r emerging values in a 22 column table"*, then *"delete these sections from
both files"* (the per-event item table) and *"drop the r2 rows, and replace them with r rows that were calculated
on ws5x"*.

| row | what it holds |
|---|---|
| banner | `xcross validator report · `, the cadence side, the cadence event's time, and "n of N" |
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
- Each kept event runs through the same xcross validator report, banner `xcross validator report · HIGH FAKE
  cadence event`. He named the report 1108, asked about this banner: *"what did we name this report"*, then
  *"let's name that report "xcross validator report" - it matches what it does"*. "FAKE" in the banner is my label.
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
| `WS5X_TF` | 5 | TF | YES | "replace them with r rows that were calculated on ws5x", then 1108 "bank the latest version, the one that has ws5x as a static line for each table" |
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
| the 1108 rename rerun, against commit f8224e6 | HIGH, LOW and fake identical apart from the name in each file title and banner; the ws5x block in 15 of 15 HIGH, 13 of 13 LOW, 7 of 7 fake reports |
| the 1108 rerun on the banked knobs, against the files from before | HIGH, LOW, fake and the ws2b pine byte-identical; the ws2b events file identical but for one legend row |
| that legend row, corrected 1108 | the RSI-level-gate row read "off - gcws30b oob only" on the ws2b run; it now names the gate it ran on, ws2b |
| ws1r rebuilt from the read's RSI, 1,440 bars of the day | max difference 7.1e-14 |
| gcws30r rebuilt from the read's RSI, 2,880 bars of the day | max difference 1.1e-13 |
| ws12e from `e_line(12)`, against the 1107 in-memory build | 0 difference, 0 NaN mismatches; its ws12Mage control row exact |
| `rsi_divergence` called with its defaults | no events |
| `W_SBX_WS5X_TF=6` | REFUSED |
| `W_RSIDIV_LINES=ws1r` | REFUSED |

---

## 10. THE xcv VERDICT - HIS 1108 VIEW, NOT YET BUILT

HIS WORDS: *"the next task: reading the xcv report's 'direction of the diff' line / we will learn
this in small batches / my current view is that a xcv verdict can be build only when 3 'down's or
3 'up's are printing in the 4 lefthand side TFs (ws30 to ws27) / examples where a xcv verdict
cannot be created: 0702, 0754, 0808, 1004 / because they are not printing 3 ups or downs, the cad
walk (10 min) will carry the report forward until a xcv verdict prints"*, and *"when a verdict of
`up` or `down` is created, a rev-trade is created"*.

NOTHING IS BUILT. The measurement below is what his rule gives on the report as it stands.

### his four examples, under his own rule

| the cadence event | side | the direction row | ws30 | ws29 | ws28 | ws27 | ups | downs | flats | his verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-25 07:02:00 | LOW | ws4x | down | flat | down | flat | 0 | 2 | 2 | none |
| 2026-08-25 07:02:00 | LOW | ws5x | down | flat | down | flat | 0 | 2 | 2 | none |
| 2026-08-25 07:54:00 | LOW | ws4x | up | flat | down | flat | 1 | 1 | 2 | none |
| 2026-08-25 07:54:00 | LOW | ws5x | - | - | - | - | - | - | - | no cross |
| 2026-08-25 08:08:00 | LOW | ws4x | flat | flat | flat | flat | 0 | 0 | 4 | none |
| 2026-08-25 08:08:00 | LOW | ws5x | up | down | flat | up | 2 | 1 | 1 | none |
| 2026-08-25 10:04:00 | LOW | ws4x | flat | flat | flat | up | 1 | 0 | 3 | none |
| 2026-08-25 10:04:00 | LOW | ws5x | up | flat | flat | up | 2 | 0 | 2 | none |

All four fail on BOTH direction rows, so his examples do not say WHICH row drives the verdict.

### the census over 2026-08-25, 28 cadence events

| the reading | verdicts |
|---|---|
| the ws4x direction row alone | 10 of 28 |
| the ws5x direction row alone | 12 of 28 |
| BOTH rows, agreeing on the same verdict | 9 of 28 |
| EITHER row | 13 of 28 |

### OPEN - needed before it can be built

| the gap | the question |
|---|---|
| which direction row | the ws4x row, the ws5x row, both agreeing, or either. His four examples fail on every reading so they do not settle it |
| what the cad walk carries forward | re-run the race from each later bar, or hold the cross bar and re-read the direction at the current bar, or wait for the NEXT ws{TF}x cross inside the 10 min |
| where the 10 min starts | the cadence event bar, or the ws{TF}x cross bar |
| the 4 events with no cross at all | 17:10:00 LOW, 17:51:00 HIGH, 19:35:00 LOW, 20:52:00 LOW print no rows under his new race bound. Does the cad walk carry those too |
| the rev-trade's side | an `up` verdict and a `down` verdict map to which trade direction |
