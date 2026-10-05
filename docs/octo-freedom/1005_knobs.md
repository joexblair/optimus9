# 1005 — the knob register for the lazy-g routing + scoring chain

Every number the 1005 chain depends on, with where it came from and who owns it. Results and the
measurements behind each choice: `1005_scored_outcomes.md`. Runnable chain: `1005_scoring/`.

Read the OWNER column before changing anything. **JOE** = his ruling, do not move it. **MINE** = a
decision I made and named; it is a proposal, not a fact. **BANKED** = already in the machine.

## 1. ROUTING — mtd, then branch D

| knob | value | owner | source |
|---|---|---|---|
| mtd lines | g5 / g15 / g30 / ws1 Mage | JOE | 1004 mtd spec |
| mtd step-1 lookback | **48 bars = 4 min** | MINE | measured knee, 09-25: 4 min captures 39 of 39 signals, nothing past it adds one; 2 min caught 29 of 39. `1003_lazy_g_spec.md` |
| mtd extrema test | **same-dr**, both the lookback and the forward walk | JOE | 1004, *"that's my mistake - the extrema test is same-dr"* + *"yes same-dr for the forward walk too"* |
| mtd step-2 read bar | the step-1 extrema | JOE | 1004 rollback, *"you're absolutely right. rollback"* |
| mtd per-line tolerance | g5 0 · g15 **3** · g30 **6** · ws1 0 bars (= 0 s / 15 s / 30 s / 0 s) | MINE | Joe 1004 *"your call on the #2 window size"*. Anchored to CONSTRUCTION — each line's own bar width, the most its close can lag a 5 s close. A 5-120 s sweep showed no stability knee |
| mtd forward-walk reversal | `lr_v2._mage_rev`, rev_wob **2** | BANKED | v3_config |
| `LAZY_G_D_GAP_MAX` | **4** skipped TFs in the ex-fence block | JOE | 1004, explicitly arbitrary, *"I'm choosing 4 as an arbitrary knob (add to spec for sweeping)"* — NOT YET SWEPT |
| branch D ladder | ws1..ws12 r, ws1 claims its floater value when the divergence test fires | JOE | 1004, *"the floater, ie the moment when ws1r completed its purpose"* |
| branch D band test | higher TFs have no claim unless they print between ws1r and the weakest ex-fence r | JOE | 1004 answer 3 |
| branch D grade | Mage net ws1->ws12. AWAY from dr = with-trend · TOWARDS = against-trend | JOE | 1004 |
| warm-up | **2160 bars = 3 h** before any printed span | JOE | 1004 ruling |
| `rig.DR` | per bar, rebuilt from `sweep_v3_signal.Rig.__init__:99-106` | JOE | 1004, *"the report's rows must honour rig.DR"* |
| `STALL_N` | 6 | BANKED | Joe 0814 |
| traj | `rule2_trajectory.trajectory`, block 60 bars, min_bars 24, min_travel 0.0 | BANKED | wsf_dtf_v3_spec s22, Joe 0924 |
| fences | oob **15/85** · Mage 25/75 · rule#1 27/73 · r-momo 17/83 | BANKED | four separate fences, not one |

## 2. SCORING

| knob | value | owner | source |
|---|---|---|---|
| side rule | **dr-bias** (dr +1 = SHORT, dr -1 = LONG). The stage-2 flip is OFF | MEASURED | the flip costs **-2.508 pp over 9 days** / -0.021 per trade. Wins 4 days, loses 5. `1005_scored_outcomes.md` s5 |
| swing_detect | **0.70 %** | MINE | the separation knee: CONF vs NOT-CONF MAE median 0.258 / 1.622 = 6.3x, widest of ten points. **DEPARTS from the banked 1 %** (`docs/linelab_spec.md` s0, "Locked by Joe") |
| exit | the next favourable swing pivot, swing-to-pivot | BANKED | `docs/linelab_spec.md` s0 |
| MAE / MFE | `max(0, adverse)` over entry -> that pivot. Pre-entry adverse belongs to a different leg | BANKED | same |
| stop | **0.80 %** of entry | JOE | 1005, *"apply a 0.7% and 0.8% stop"*. 0.80 beats 0.70 by **+9.186 pp** on the dr-bias set. **The LIVE machine still runs `mae_cap` 0.70** (`wsf_trade_config` v3) — the two differ |
| drag | **0.1975 %** per trade = 2 x 5.50 bps taker + 8.75 bps slippage at 22,000 coins | BANKED | `docs/strat-3-r-oob/spec.md:77`. ONE orderbook measurement applied flat |

## 3. SIZING

| knob | value | owner | source |
|---|---|---|---|
| pyramid | **NO CAP** | JOE | 1005, *"drop the pyramid max"*. Measured max **4** concurrent legs over 9 days |
| start balance | **888.00 USD** | JOE | 1005 |
| risk budget | **2.0 % of equity per entry** | MINE | the classic 2 %-risk convention. Return and drawdown are both near-linear in it — **no knee**, so it is a convention, not an optimum. Swept 0.5 to 10.0 in s7 |
| worst case per trade | **0.9975 % of notional** = stop 0.80 + drag 0.1975. Known BEFORE entry | DERIVED | it is the stop, not an estimate |
| leverage | `risk_i = 2.0 / (n_live + 1)` · `lev_i = risk_i / 0.9975` | MINE | alone 2.00x · 1 live 1.00x · 2 live 0.67x · 3 live 0.50x. Holds total open risk at 2 % with concurrency unbounded |
| alternative sizing | constant 2 % per leg, the sneaky-1 precedent (`sneaky_trade_1_handover.md:174`) | BANKED | banked in `lazyg_compound` as `lc_size_mode='constant'` |
| position size in coins | **NOT SET** | JOE | MVP2 item 4. Every figure is a percentage or a dollar derived from the $888 start |

## 4. WHERE IT IS BANKED

| what | where |
|---|---|
| per-trade compound P&L, both sizing modes | MySQL **`lazyg_compound`**, 151 rows x 2 modes. Unique key `uq_lc` carries side_rule, stop, swing, cost, pyr_max, risk_pct, size_mode, start_usd, open_ms — every knob that changes a row |
| the runnable chain | `1005_scoring/` — `score39.py` (mtd + D + scoring), `flip39.py`, `ninedays.py`, `fc7.py` (bootstrap), `stops_pyr.py`, `compound_db.py` (the DB bank), `lineage.py` (the baton defect) |
| the 298 octo-sig inputs | `1005_scoring/octosig/2026-09-{25..30}.out`, `2026-10-0{1,2,3}.out` + `run.sh` |
| results and every measurement | `1005_scored_outcomes.md` |

## 5. OPEN — NOT RULED

| item | state |
|---|---|
| `neither` = BLOCK | +3 on 09-25, **-1** on 09-26. Does not hold |
| `no fire` = BLOCK | 0 on both days |
| D empty ex-fence block = BLOCK | +1 on 09-25, **-5** on 09-26. Inverts hardest |
| the stall-contiguity gate | Joe's own 07:57 verdict mechanism. He has not been able to name the knob: *"3 TFs stalled inside of a 4 TF window to be contiguous ... this needs a sweep - I can't think how to describe the knob(s)"*. UNBUILT |
| the baton lineage rule | `baton.py:125` is `rider = max(c)` — NO lineage. 61 of 139 passes are illegal at +-3 TF, 41 have no legal successor at all. Three values open: the hop window, what happens with no legal successor, whether a downward pass is a pass. `1005_scored_outcomes.md` s5 |
| `LAZY_G_D_GAP_MAX` 4 | Joe's, explicitly arbitrary, flagged for sweeping |
| the stop sweep | 0.70 vs 0.80 is **two points, not a sweep**. The direction says the live 0.70 may bind early; it does not locate a knee |
| branch B and C agree/disagree direction | unruled |
| mtd population B | the ws1mage-rev + ws1r oob events walked bar by bar. NEVER RUN |
| held-out days | **NONE.** All 9 days are in-sample for every knob above |

---

## 6. 1005 OOS — 10-04, THE FIRST HELD-OUT DAY. IT MOVES TWO CONCLUSIONS.

Added 2026-10-05 after Joe reassigned the OOS run to this session. Built: `build_tape.py 2026-10-05`
(98 override lines, 63.4 s, the tape reused from the recon session's build) ->
`report_leash_walk.py --day 2026-10-04 --tape-end 2026-10-05` -> 30 `R|` rows, 27 in the day window.

Every knob in sections 1-3 UNCHANGED. The chain is now parameterised so the OOS runs the identical
code path: `LG_DAYS`, `LG_TAPE_END`, `LG_TABLE`.

| basis | trades | total net % | mean net % | winners | stopped |
|---|---|---|---|---|---|
| 10-04 confluences, FLIPPED (ninedays `net`) | 11 | **+10.398** | **+0.945** | 10 of 11 | 1 |
| 10-04, every octo-sig ungated | 27 | — | +0.465 | — | — |

- +0.945 mean is the **best of any day in the set**. n = 11. One day.
- banked to **`lazyg_compound_oos`** (11 rows x 2 sizing modes). `lazyg_compound` stays in-sample
  only and was verified unchanged at 302 rows before and after.

### ON THE RECOMMENDED dr-bias BASIS THE HELD-OUT DAY LOSES MONEY

| sizing | trades | start $ | final $ | return % | max DD % |
|---|---|---|---|---|---|
| shared budget | 11 | 888.00 | **885.27** | **-0.31** | 4.03 |
| constant per leg | 11 | 888.00 | 911.85 | +2.69 | 6.27 |

| 10-04 | notional traded $ | gross P&L $ | drag paid $ | net P&L $ | drag as % of gross |
|---|---|---|---|---|---|
| 11 trades | 12,667.36 | +22.29 | **-25.02** | **-2.73** | **112.2 %** |

**The day's gross edge did not clear its own drag.** $25.02 paid against $22.29 of gross.

### THE FLIP IS NOT DECIDED — section 5's correction was itself an over-read

| day | wt rows | dr-bias total net % | flipped total net % | delta |
|---|---|---|---|---|
| 09-25 | 12 | +0.800 | +10.378 | **+9.578** |
| 09-26 | 11 | -0.787 | +5.756 | **+6.543** |
| 09-27 | 15 | +0.816 | +4.690 | **+3.873** |
| 09-28 | 5 | +3.702 | -0.895 | **-4.597** |
| 09-29 | 20 | +4.055 | +7.945 | **+3.891** |
| 09-30 | 10 | +2.629 | -0.623 | **-3.252** |
| 10-01 | 13 | +7.066 | -1.232 | **-8.298** |
| 10-02 | 17 | +8.748 | +4.242 | **-4.506** |
| 10-03 | 14 | +5.353 | -0.387 | **-5.740** |
| **10-04 HELD OUT** | 7 | **-1.066** | **+7.146** | **+8.212** |
| **10 days** | 124 | +31.316 | **+37.020** | **+5.704** (+0.046/trade) |

- **the flip wins 5 days and loses 5.** Over 9 days it totalled **-2.508**; adding one held-out day
  flips the total to **+5.704**.
- single-day deltas run **-8.298 to +9.578**. The 10-day total is inside one day's swing of zero.
- so: NOT "the flip holds" (my 2-day read) and NOT "the flip costs 2.5 pp" (my 9-day read). The
  quantity's day-to-day spread exceeds its own total. **Undecided, and it needs more days, not a
  verdict.** See [[day-is-the-block-unit]].

### THE TEN DAYS TOGETHER — 9 in-sample + 1 held out, labelled as such

| | octo-sig | CONF | BLOCKED | OPEN | CONF total net % | CONF mean | winners | stopped | ungated mean |
|---|---|---|---|---|---|---|---|---|---|
| 9 in-sample | 298 | 151 | 31 | 116 | +37.148 | +0.246 | 97 of 151 | 44 | +0.206 |
| **10 days** | **325** | **162** | 36 | 127 | **+47.546** | **+0.293** | 107 of 162 | 45 | **+0.227** |

The 9 in-sample days reproduce BYTE-IDENTICALLY on the 10-05 tape (checked row by row), so the
tape-end shift does not move the lines and the 10-day aggregate is legitimate.

### TWO CORRECTIONS TO SECTION 5

1. **the longest consecutive losing run is 6, not 3.** The 3 was the FLIPPED basis over 9 days. On
   the dr-bias basis over 10 days it is **6**. At 2.228x that is 11.42 % of equity; at the live
   13.595x it is **54.19 %**.
2. a new boundary case now handled: **UNRESOLVED** rows, where no favourable swing pivot exists after
   the entry inside the tape. 3 of them on 10-04 (23:04:15, 23:15:00, 23:16:30) because the tape ends
   10-04 23:59:55. They are EXCLUDED and COUNTED, never scored 0 — inventing an exit at the tape end
   would be a truncation. The 9 in-sample days have 0, because that tape ran a day past 10-03.
