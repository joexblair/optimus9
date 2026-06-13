# Breaching Lines (BL) machine — design

**Status:** Scope — **foundation verified, ready to build** · 2026-06-03. First
slice = hb9 4-state detection, intrabar. References: `260511 trend machine.xlsx`,
`260604 BL machine.txt` (Pine — harvest, don't port), Joe's red-pen 2026-06-01/02.

> **BL doc map (the source of truth).** This doc = the **machine mechanism** (states,
> gate / `c_bls`, fence, prediction, exits). Companions: `bl_line_brd.md` (the line/support
> *wiring* — which BB supports which breach; the **live** config is `bl_lines`) ·
> `bl_dialin_process.md` (the dial-in / grind process) · `bl_settings_cheatsheet.md` (the
> dialable knobs). Historical (kept, not authoritative): `bl_grind_design.md` (superseded —
> old expectancy objective) · `bl_gate_experiments_findings.md` (a dated findings log).

## 0. Foundation — verified, and the intrabar pivot (2026-06-03)

The data + line foundation BL stands on is now **proven true vs TradingView**, so
state mismatches will be machine logic, not bad inputs:
- **Tape**: gapless, exchange-faithful (kline-tape milestone). 9-min OHLC = TV to
  the digit; no gaps, no dropped windows, no dojis (verified).
- **Lines**: DEMA, BB, **K all reproduce TV** (K @21:18 = 81.1 = TV, stable across
  warmups). The BB de-conflation (rsi_ob/rsi_os 70/30 rescale vs boundary 85/15) is
  in `constants.py`; `bl_detect` bm = TV (76.0/73.3/86.4). [[project_thresholds_constants]]
- **Two HTF views per 5s bar** exist in `bl_states`: `c9` (last *closed* 9-min bar)
  and `e9` (the **emerging** bar — O anchored at cycle-open, H/L the running
  min/max of the current emergence, C = current 5s close). `e9` is the realtime
  object. Tidy still owed: drop `bl_detect._htf_views`, reuse `IC.lookahead_resample`.

**The pivot (Joe, 2026-06-03):** `bny30` fires *intrabar* — almost never on a clean
TF9 boundary. So the BL machine must evaluate **breach / curl / exit on the emerging
bar (`e9`), per-5s, intrabar** — not only on closed HTF bars. The DoD becomes: are
the **intrabar** BL states good enough to gate **p-rev**? (See §11.)

## 1. Objective

BL detects HTF "breaching lines" leaving and returning to boundary, producing —
**organically, with no verdict combiner** — the trend reversal that gates trades.
It's bny30 inverted: a breach **latches the gate shut**; the gate only opens once
the breaching lines have completed their journey. The entry-quality lever that
should pull the data-derived stop (~0.68) toward Joe's trusted 0.33 and unblock the
cluster_scoring conviction weight (task #10).

## 2. The gate is a collective hold (key mechanic)

- Each breaching line runs its own 4-state machine.
- The gate stays **closed** while ANY line is mid-journey (state 1 or 2).
- **Cascade**: a fast line (30s) breaching can *pull* a slower line (TF4) out, which
  pulls a 9-line out. The fast line **bobs in and out of OOB** (cycling its states)
  as it gravitates toward the slower line.
- The gate **opens** only when ALL lines are state 3 or 0.
- At gate-open, a trade can fire if a **5s PK printed within the last x bars**
  (lookback) — OR'd with the proxy-PK path (§9). *[downstream — parked.]*

## 2b. c_bls — the combined breaching line state (the gate, formally)

- **bls** = a single line's breaching-line state (0/1/2/3, §3).
- **c_bls** = the **combined MINIMUM of the non-zero line states**; lines at `bls:0` are
  **excluded** from the fold (c_bls:0 only when every line is idle).
  - 2-line examples: `{1, 3}` → **1** · `{2, 1}` → **1** · `{2, 0}` → **2** (the 0 is dropped).
- **`c_bls:3` ⟺ every non-zero line is at 3.** And `2→3` only fires when an **exit method
  completes** (§5) — so `c_bls:3` means *every active line has had an exit trigger*. (State 3
  can only happen on an exit — obvious but crucial.)
- **`c_bls:3` is the gate opener**, and the **centre of the PK-signal tolerance range**: a
  bias-aligned 5s PK admitted within **±lookback of a `c_bls:3`** capitalises on the open gate
  (lookback lets a non-time-synced PK still take it). See `bl_dialin_process.md`.
- Implementation: `bl_detect` folds it as `min` over non-zero states (0 masked), 0 iff all
  idle — single-sourced into `combined_state` / `c_bls`.

## 3. The 4-state machine (per line)

`0` idle · `1` breached · `2` curled · `3` complete.

| from | to | on |
|---|---|---|
| 0 | 1 | K breaches, or is **predicted** to (prediction calc), while outside the 30:70 fence |
| 1 | 2 | the K line **curls** (ROC reducing past floor) — **mandatory** intermediate |
| 2 | 3 | any **exit method** completes (§5) |
| 2 | 1 | re-breach (bobbing) |
| 3 | 1 | while IB, K predicted again or breaches again (re-pulled) |
| 3 | 0 | reset when the gate opens (all lines done) |

**Keep from Pine:** the states, the ROC/curl calc, the prediction calc.
**Drop:** the Pine's exit logic (counter-candle / PK) → replaced by §5; and the
**7-bar fresh-breach** hack (a TV "wait for a full 30s bar" device — Python reads
real bars, so fresh-breach = breaching now, clear last bar).

## 4. No-engagement fence (30:70)

We do **not** predict/engage a K breach while K sits inside the 30:70 band. Zones:
**[30–70] ignore** · **[15–30]/[70–85] engage + predict** · **beyond 15/85
breached**. (A separate IB-fence near 15/85 for auto-complete exists in the Pine —
parked, §9.)

## 4b. Breach prediction (kept from Pine, re-derived)

A K line is **predicted to breach** when the BB anchor overshoots the boundary by
more than the K falls short of it — the BB's pull will carry K through.

**Hi breach (short):**
- `bb_anchor = max(m, M)` (the higher BB);
- predicted = `bb_anchor` is OOB-hi **AND** `(bb_anchor − HI) > (HI − k)`.

**Lo breach (long)** mirrors it: `bb_anchor = min(m, M)`, OOB-lo,
`(LO − bb_anchor) > (k − LO)`.

Examples (HI=85, K=75): `m=56/M=120` → anchor 120, `35 > 10` → **true**;
`m=56/M=90` → anchor 90, `5 > 10` → **false**.

> **Resolved:** `breaching_line.predict_breach` uses `>` (matches both of Joe's
> worked examples); 11 tests green. The written `<` was a slip.

Prediction is suppressed inside the 30:70 fence (§4). The prediction uses **both**
BB lines via `max/min(m, M)` — so hb9m IS needed here (its *exit* role is parked).
**Constraint:** the BB lines (M/m) are hand-curated to serve prediction — the AM
grind must NOT sweep/auto-update their multiplier (future-state).

## 5. Exit methods (the new logic — per-line; hb9 example)

From state 2, complete (→3) via ANY of:
1. **immediate** if hb9M (BB) was OB and is now IB {default lookback 2 bars};
2. hb9M has a **non-subtle ROC** (after hb9b curled) — flatten or reverse;
3. **hb9M ✕ hb9b toward IB** — the BB falls through the K heading to in-boundary
   (pseudo-cross when within x and converging).

Exit set varies per line; side-agnostic is a per-line toggle (parked).

## 6. First slice — hb9 4-state detection over 12h

Lines all on **TF9** (same family stem → same pane/TF):
- **hb9b** — K, `5|74|29|hlc3` — the breaching line (drives the state machine).
- **hb9M** — BB, `19|0.78|hl2` — drives the exits + the prediction anchor.
- **hb9m** — BB, `13|0.78|ohlc4` — feeds the prediction anchor `max/min(m,M)`; its
  exit role is parked ("later jic").

Deliverable: run the 4-state machine on hb9b over the last 12h and emit, for Joe's
eye vs TV:
- a **persistence table** updated **every 5s close** (one row/bar): `UTC`, `dema` +
  line values, `predicted` (bool), one **bool per exit type** (1/2/3/…), `state`,
  + any debug fields the next steps need;
- a **Pine overlay** with state labels.

## 7. Reuse map (SRP)

| need | existing |
|---|---|
| line values + breach (OOB) | `indicator_computer.compute_oob_side` / `f_bb` / `f_k` |
| curl (ROC reducing) | slope `line - line[mult]` + `_states_roc_curl` |
| prediction calc | port from Pine (anchors) + add 30:70 fence, drop 7-bar |
| data + config | `KlineLoader`, `indicator_configs_live` |
| Pine emit | the `gate_validation` emit_pine pattern |

New: the 4-state machine, the three exit methods, the BB✕K crossover primitive,
seeding the hb9 lines.

## 8. Behaviour by example (tests = DoD)

- 0→1 on breach / predicted **outside** 30:70; no engage **inside** 30:70.
- 1→2 only on curl (mandatory — no skipping to 3).
- 2→3 on each exit method (three cases).
- 2→1 re-breach; 3→1 re-pull (predicted/breach while IB); 3→0 reset on gate-open.
- the 12h hb9 run yields the table + Pine; states match TV by eye.

## 9. Parked → next spec for review

- Multi-line **cascade + collective gate-hold** (only emerges with >1 line).
- **Gate-open trade trigger** (5s-PK-lookback OR proxy-BB-PK).
- **PK-exit coupling** — BL closed by its related BB PK, p-rev'd from 5s PK (hb9's
  exits don't use it).
- TOB (Trade-On-Breach), IB-fence auto-complete, hb9m, side-agnostic toggle,
  full HTF line seeding.

## 11. Intrabar evaluation (the spine)

The machine ticks per-5s on the **emerging** view, not on closed HTF bars:
- **breach (0→1):** `e9`-driven K (`f_k_lookahead`) crosses 85/15, or is predicted
  (§4b), outside the 30:70 fence — evaluated every 5s as the bar emerges.
- **curl (1→2):** ROC `line − line[mult]` (mult = TF9/5 = 108) on the developing
  line. *Design watch:* the developing line **resets/jumps at each cycle boundary**
  (H/L re-anchor) — the curl lookback must not read a boundary jump as a curl.
  First slice will surface whether curl is stable intrabar or wants a guard.
- **exit (2→3):** the three §5 methods read `e9` (BB now IB / non-subtle ROC /
  BB✕K toward IB) intrabar — so a gate firing mid-cycle still gets a live exit read.

Closed-bar (`c9`) values remain available for confirmation / debug columns.

## 10. Definition of done + remaining open

**What good looks like:**
- **Target 1 — states placed right (intrabar):** Python BL states match the manual
  application on TV, read **at the 5s the gate would fire** (not just at TF9 close).
  Joe's eye on `bl_states` vs the chart. The foundation (§0) means a mismatch is
  machine logic, not inputs.
- **Target 2 — good enough for p-rev:** the payoff. Does intrabar BL gating measurably
  clean the 5s-PK noise / improve entry quality enough to drive p-rev? This is the
  reframed DoD — BL earns its place by helping p-rev, evaluated where bny30 actually
  fires (intrabar), not on idealised closed-bar timing.

**Resolved:** foundation true vs TV (§0); TF (hb9 on TF9); prediction calc + `>`
direction (§4b); state map (§3); hb9m role (prediction anchor); intrabar spine (§11).

**Open to interrogate before build:**
1. **Curl intrabar stability** (§11) — does the boundary jump fake a curl? guard?
2. **"Good enough for p-rev"** — the measurable bar for Target 2 (what we compare:
   p-rev entries with vs without BL gating, on which window/metric).
3. **Scope of slice 1** — single line (hb9) only, no cascade/gate-hold (§9 parked) —
   confirm.
4. **`lookahead_resample` reuse** — fold the `bl_detect` Footwork tidy into slice 1
   or keep separate.

## 12. bl_review — the materialised report (over bl_states + swings)

`run.py bl_review` projects the meaningful `bl_states` rows for eyeballing (Excel/SQL):

- **`event`** per row: `state` (a state change), `exit` (a raw exit *condition* fired
  but did NOT complete — e.g. exit3 pseudo-cross while still bls1), `gate_open` (a line
  reached 0/3 from 1/2), `context` (a run-up bar, below).
- **11-bar run-up** (req-1 context): for every state change / `gate_open`, the **11
  `bl_states` bars immediately before it** are also emitted, tagged `event='context'`
  — so you see the lead-in *into* each transition, not just the transition bar.
- **gate-open risk/reward** (px_smooth, 0.9 % ZigZag swings): per `gate_open`,
  `stop_pct` = abs % from the gate-open px to the next swing in the breach direction
  (the adverse excursion if the gate opened early); `profit_pct` = the following leg
  (the move the trade is opening for). Direction is read from the *in-breach* bar (a
  reset gate-open carries `breach_dir=0`). At the data edge (no future swing) both NULL.
- columns: `bl_line` (e.g. hb9b), `predicted`, `state`, `breach_dir`, `breach_line`,
  `bb_main`, `exit_bits`, `px_smooth`, `stop_pct/at`, `profit_pct/at`.
