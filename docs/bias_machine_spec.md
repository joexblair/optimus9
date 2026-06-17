# Bias Machine — Spec

status: **building** — walking Joe's OG timeline entry-by-entry to derive the rules.
started 0615. Joe's words are canonical; Claude's discovery is supporting context, kept
separate. Companion: `bias_machine_overnight_0615.md` (Claude's scan findings).

---

## Preamble (Joe's words, verbatim — 0615)

```
BIAS MACHINE
bias is set by 22a
- we place pyramid trades along the bias line

every TF except 7 has the same s30 config
- m:10|0.4|hlc3
- M:37|0.72|ohlc4
- r:5|6|6|hl2
TF7 has a doubled config, and is referred to as s14
- s14 config (TF7)
-- m:20|0.77|hlc3
-- M:74|0.72|ohlc3
-- r:10|12|12|hl2
- s14 might not be used in this machine. TBC

s18
- m:18|0.65|hlc3
- M:111|0.74|ohlc4
- r:5|6|6|hl2

the use of 'a' (eg s30a, s2a)
- a is 'all'. all 3 lines: m, M, and r
-- there are no b's in this machine

trades are initiated by (s2m+M or s2m+r) +s30a +pk signal
- note I don't have pk signals. for now, we will treat s30m wobble slayer as c_bls3,
  and build a pk detection window around it

important concept to understand. if an M line stays near one boundary (eg high), and the
m+r are breaching at the other boundary (ie low), the trend is LONG.
- M in solidarity near a boundary creates gravity

all calculations are based on the closed bar value, not the emerging value
```

---

## Corrections to Claude's prior interpretation (0615)

- **bias is set by `s22a`** — NOT "s22a + s18a" as I'd written. s18 has its own config but
  is not stated as a bias-setter here.
- **s22 REVERSALS are the primary mover.** M-gravity is a *concept to learn*, NOT the
  lynchpin — I over-weighted it overnight. Re-centering on s22 reversals.
- **s18 config = m:18|0.65|hlc3, M:111|0.74|ohlc4, r:5|6|6|hl2** (on TF6) — supersedes both
  my "TF6 ×3 of the centroid" guess AND the existing-s18 (k 12/66/147) config.
- **PK signal is not built yet** — stand-in = the s30m wobble_slayer treated as c_bls3,
  with a pk detection window around it.

## Resolved (0615)

- **s30 = EMERGING in prod; all other TFs = CLOSED bars.** (Pen tests may use closed s30
  for convenience.) Resolves the closed-vs-emerging fork.
- **s30r and s6r source = `close`** (were hl2). [scope TBC: all r lines, or just these two?]

## Open forks (resolve before/while walking)

1. **What IS an "s22 reversal"** (the primary mover)? Which line reverses — s22r (the K
   turn-detector), s22m, or s22a — and from what state (OOB? a boundary)?

## ⚠️ PARKED — bar timestamp convention (close vs open)  [0616]

**Our tooling labels bars by CLOSE time; TV labels by OPEN time** → a constant offset
(e.g. our `22:29:00` closed bar = Joe's `22:28:30` on TV). We are **keeping close-time**
(switching to open-time risks wrong realtime behaviour — the bar isn't closed at its
open). So when comparing our scripts to a TV eyeball, **expect ~one-bar timestamp
disagreement** even when the values agree. **If we hit bias-machine problems that look
like a mismatch, RE-OPEN this.** Separately: at 30s in volatile chop, our 5s→30s resample
diverges from TV's native-30s OHLC by ~6–9 pts (the known tape-vs-TV issue) — tape is the
arbiter, not bar-by-bar TV parity.

## Dynamic-p_c s6 PK (rule, locked 0615)

A "reliable s6 PK" via an event-anchored s6r divergence. All on the SAME side S.
- **Gate:** s14M OOB (side S) — gates the ANCHOR sample only (latched, not retested
  elsewhere). s14M = TF7 BB 74|0.72|ohlc3 (≡ohlc4).
- **Anchor:** while s14M OOB(S), at an s6m breach(S), the first time **s30a prints an
  **s30M** wobble_slayer(S)** (Major, *not* m — kills solo-min twitches) → capture **s6r**.
- **Floater:** the **previous same-side s6m breach** (s14M disregarded there). Work
  BACKWARDS from the anchor → the **LAST** s30a-s30M wobslay(S) before that breach ends
  (not the first) → capture s6r.
- **s30a requirement (0616):** a qualifying wobslay needs **all three s30 lines (m, M, r)
  OOB on side S at the s30M EXTREME** (the trough/peak, i.e. 2 bars before the 2-bar
  confirmation). Without it, near-boundary s30M twitches fire spurious wobs. Applies to
  BOTH anchor and floater. wobslay fires/samples at the confirmation bar (realtime-honest).
- **Signal:** anchor > floater → **bullish**; floater > anchor → **bearish** (absolute,
  side-independent — s14M only chooses where the *anchor* is sampled).
- "dynamic p_c": the floater lookback is the *previous breach event*, not a fixed N bars.
- wobble_slayer(S) = 2 bars off the OOB extreme (hi: peak≥85 then c<b<a; lo: ≤15 then c>b>a).
- PK stand-in note (preamble): no real pk yet — s30M wobslay treated as c_bls3.
- **Tooling:** `bias_pk_pentest.py` (numeric trace) + `bias_pk_pentest.pine` (15s viz).
  First pen test window 0610 2012→0230: 4 anchors (BEAR/BULL/BEAR/BULL).

## Validated foundation (Claude's discovery — detail in overnight doc)

- **native value = the closed bar read at its close boundary (HH:MM:00)** — matches your TV
  prints; m & r to the decimal.
- HTF lines need **~160h warmup** to converge (RSI/STC).
- M mult per-TF (0614): s2M/s22M = 0.83, s6M = 0.72. **s22M still reads ~+10 high vs TV —
  parked** (config mismatch, not warmup).
- data source = **`kline_collection`** (5s base tape; via KlineLoader.load_window).

---

## Reporting / tooling

- **`bias_pk_validate.py`** — 96/168h validation. Per gated bias print: *run-up to the
  adversarial swing* (favourable excursion to the first counter-bias ZigZag pivot) +
  *profit to the next s14M OOB reversal*.
- **`bias_pk_backtest.py`** — trades the bias prints over the last 7d. ENTRY = the next
  aligned s30a+s30M wobslay after the print (BEAR→hi reversal, BULL→lo); EXIT = the
  opposite s6m+s30a+s30M confluence. 33K lots · 50x · Bybit taker 0.11% rt · 1000 USDT
  start. Runs two gate modes: **s14M OOB** and debug **s14M vs 50**.
- **`bias_pk_trades`** (db table) — per-trade ledger, one row per (gate_mode, trade):
  `gate_mode, print_time, entry_time, exit_time, direction, exit_reason, entry_px,
  exit_px, lot_coins, notional_usd, leverage, margin_usd, fee_usd, pnl_usd,
  pnl_margin_pct, balance_usd`. `balance_usd` runs per gate_mode; filter on `gate_mode`.

## Rules from the timeline
*(built as we walk each entry — to follow)*
