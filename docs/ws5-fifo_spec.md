# ws5-fifo

Joe's name, 0906: artefact `FIFO + concentrated BB`, mechanic `ws5-fifo`, line `ws5`. Banked in
`eyes_on_pine` seq 12.

**The spec is Joe's. The build is mine. Where they disagree, his words win and the code is rewritten.**
Build: `emit_ws5_fifo.py`. Artefact: `ws5_fifo_0805_0819.pine`.

---

## The mechanic

A **span** has an open and a close. The close is the trade time — Joe 0906: *"the `ends` column is the
time the trade would be placed."*

### The span OPENS

On the bar all four hold at once, and did not on the previous bar:

- `dr` is set, +1 or −1. Never 0.
- **ws5m** holds the away-from-50 state.
- **ws5Mage** holds the away-from-50 state.
- **the dr-side boundary** holds the away-from-50 state — 85 at dr +1, 15 at dr −1.
- **ws5Mage is oob** at that bar — ≥ 85 at dr +1, ≤ 15 at dr −1.

`ws5b` is optional (Joe 0907: *"make b optional"*). It is not tested.

### The span CLOSES

On the **first** bar after the open, inside the same dr run, where all three **ws2** lines hold the
towards-50 state — the dr-side boundary, ws2Mage and ws2m.

- Joe 0907: *"when all of the ws3 (or ws2) lines have crossed towards 50, that is when the span is
  terminated. ie `T3` is the terminator."*
- Joe 0907: *"there can only be the first ws3 close per ws5 open."* One close per open; later closes
  inside the same span are discarded.
- An open whose dr flips before any close arrives is dropped.

---

## The rules that decide the population

### The open population is set by ws5 alone

Joe 0907: *"I never asked to open the ws3 set. the ask was to simply cross the lines that were already
in play at the time of ws5 opening the span."*

- Every bar the open condition newly becomes true is a span. **An open is never consumed, replaced or
  ignored by a live span.**
- **Spans may overlap.** Two or more can be live at once.
- The open count does not move when the closing timeframe changes. Measured 08-05 → 08-12 at tolerance
  0: 311 opens, and 311 spans whether ws5, ws3 or ws2 closes them.

**THE BUG THIS REPLACES.** The first build let a live span swallow later opens. It dropped 174 of 311
opens over 08-05 → 08-12, and *which* it dropped depended on the close timeframe — so the row count
moved 379 / 429 / 483 for ws5 / ws3 / ws2 closing over 08-05 → 08-19. Joe: *"the latest pine (ws2 based)
added a lot more signals, which should not have happened."* Every count produced before 0907 came from
that build and is superseded: 137, 150, 112, 361, 379, 429, 483, 533, 853.

### away-from-50 and towards-50 are HELD STATES

Not events. A line stays in its state until a confirmed cross puts it in the other one.

- At dr +1: **over** = away from 50, **under** = towards 50.
- At dr −1: **under** = away from 50, **over** = towards 50.
- Joe 0906: *"dr needs to provide to 2 different types of crosses: the type that opens the span by
  crossing away from 50, and the type that closes the span when it crosses towards 50."*
- The closing cross is the one the repo already builds — `far_side()` at `build_wsf_x_cross.py:88-93`.
  The opening cross is the other half and exists only here.

### A dr flip clears everything

All line states go unknown and any open span is cancelled. dr flips 7 times on 08-05 alone, so this
fires often.

---

## The knobs

| knob | value | units | source |
|---|---|---|---|
| `TF_OPEN` | 5 | timeframe minutes | the mechanic's name |
| `TF_CLOSE` | 2 | timeframe minutes | Joe 0907 *"lock ws2 in to the mech"* |
| `XWOB` | 6 | bars = 30 s at the 5 s grid | Joe 0907 *"apply a xwob of 6"* |
| `MAGE_TOL` | 10.0 | line points | Joe 0907 *"add a tolerance of 10"* |
| boundary hi / lo | 85 / 15 | line points | `optimus9_system` |
| dr source | ws5Mage oob 85/15, latched | — | Joe 0906 *"for this experiment, dr can be set using ws5Mage oob"* + *"confirmed"* on latching |

- **`XWOB` is not the repo's value.** `build_wsf_x_cross.py:46` sets `XCROSS_XWOB = 5`. ws5-fifo uses 6.
- **`MAGE_TOL`**: the ws5Mage cross only puts ws5Mage into the away state if ws5Mage was within 10 points
  of its dr-side boundary at the cross bar — ≥ 75 at dr +1, ≤ 25 at dr −1. ws5Mage must still be fully
  oob at the open bar. The tolerance loosens the cross test, not the open gate.
  - Joe 0907: *"what is the impact if I require the Mage to be crossed while it's oob?"* then, on being
    shown the cost, *"add a tolerance of 10"*.
  - Measured over 08-05 → 08-19: tolerance 0 gives 411 opens, 10 gives 655, and switching the
    requirement off entirely gives 853.
- **`dr` is global.** One series serves every timeframe.

---

## The pine

`Jig._Score.emit_bgcolor()` at `optimus9/analysis/jig.py:850`. The emitted shape is locked — Joe 0731,
do not change it.

- **red = SHORT (dr +1), green = LONG (dr −1).** The codebase's own mapping; the locked block at
  `jig.py:789-792` pairs `s_sig_short` with red and `s_sig_long` with green.
- **Only the span END is painted, DOUBLED** — the TF1 bar it ends on plus the one after it. Joe 0907:
  *"I need the bgcolors to be doubled for easy view - eg for 13:48, there should be a bgcolor at 13:48
  and 13:49."* An earlier build painted the whole span and produced leadup bars Joe did not want.
- Red carries `RED_BG_TRANSP` 47 so bearish candle bodies read through; green carries 0. Format's values.
- Known property of the locked format: one `bg` variable means the last matching `if` wins, so green
  paints over red on a shared bar.

Current output, 08-05 00:00:00 → 08-19 11:59:55:

| field | value |
|---|---|
| ws5 opens with their open in range | 655 |
| opens that never closed before the dr flipped | 0 |
| spans with their close in range | 657 |
| red — SHORT | 347 |
| green — LONG | 310 |
| TF1 stamps painted | 769 |

A span may open before the range and close inside it, which is why 657 exceeds 655. The two counts are
on different bases and are never subtracted.

---

## What has been measured, and what has not

### Measured

- **Joe's eyes, 08-05, 17 span ends.** *"except for 13:21:50 and 17:05:55, all of those timestamps are
  profitable."* 15 of 17. On the two misses: *"I wouldn't label the 2 misses as failures - it indicates
  a fault in the mech. the misses are seen as accepted cost of business."* Banked, `eyes_on_pine` seq 12.
  **Those 17 came from the consuming build, so the span set behind them is not this mech's.**
- **MFE / MAE, 08-06 → 08-19, 361 rows, consuming build, ws5 terminating.** MFE mean 1.20% median 0.51%;
  MAE mean 0.28% median 0.16%; MFE > MAE on 271 of 361. Per-day: MFE mean beat MAE mean on 15 of 15 days.
  **Superseded by the open-population fix.**
- **ws5 / ws3 / ws2 as the exit inside a ws5-bounded span, 112 paired rows, 08-05 → 08-10.** ws2 best on
  7 of 8 measures. That comparison is internally fair but describes an exit, not a terminator.

### Not measured

- **No MFE or MAE exists for this mech as specified.** Every scored table used the consuming build,
  ws5-terminated spans, or both.
- **No eyes on any span from the corrected build.**
- **ws2 versus ws3 as the actual terminator, under the corrected open population.** The lock-in rests on
  the 112-row exit comparison.
- **Overlapping spans.** Spans may now run concurrently — six opens inside 2.75 minutes on 08-06
  09:01–09:03 all close together. Position sizing and concurrency have no rule.

---

## Open questions

1. **A span that opens into an already-satisfied close condition.** 08-09 01:54:40 opened at a bar where
   the ws2 lines had finished crossing towards 50 one minute earlier. The build waits for a fresh
   crossing. Closing on the open bar instead produces 104 zero-length spans over 08-05 → 08-19.
2. **Whether a span may straddle a dr flip.** Joe 0907: *"unsure, but also unlikely given the tight
   spans. let's address it if it materialises."* It materialises — dr flips 7 times on 08-05.
3. **The span-length cut.** Joe's ws20 100 / ws10 50 / ws5 25 minutes were set against a different
   construction and no cut is applied in the build.
4. **The confluence mech for a long one-directional leg.** Joe 0907: *"this large leg needs a confluence
   mech - those small MFE rows will quickly diminish the account without a control."* The reference case
   is 08-07 22:00:10 → 08-08 21:11:15 — 23.2 hours, price +6.12%, no 2.2% reversal, 33 entries at MFE
   mean 0.40%. Nothing built.

---

## Lines the mech needs

All at the wsf role specs, in the close line cache at END 2026-08-19 12:00, HOURS 40, WARMUP 1114.

| role | spec | value mode |
|---|---|---|
| `x` | `('bb', 5, 0.35, 'close')` | emerging |
| `m` | `('bb', 6, 0.4, 'close')` | emerging |
| `Mage` | resolved from `mech_lines(db, 'wsf')` | emerging |
| `r` | `('k', 5, 8, 7, 'close')` | emerging |

Built at ws2, ws3, ws5 for the mech. Also cached at ws30, ws45, ws60, ws90, ws120 for r/x/m — Joe 0907,
not yet used by anything.
