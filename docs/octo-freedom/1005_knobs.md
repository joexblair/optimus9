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
