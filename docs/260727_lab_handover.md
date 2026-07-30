# Lab handover — 2026-07-27

For a fresh Claude picking up the **lab build track**. Scope = `build_rpl_6of9.py` + `build_past50.py` (bp50) + the live 05:52-long investigation. This is NOT the evo-sweep track (that is the separate `rpl_evo_sweep` pulse-monitoring job — mentioned here only for orientation, §7).

---

## 0. READ FIRST — standing rules Joe enforces (violating these is the #1 recurring failure)

1. **BUILD-GATE** (saved to memory `build-gate.md`; Joe pastes it verbatim on build turns). Before ANY edit to code/config/DB/files:
   (1) quote the literal words that authorize the change;
   (2) BEFORE writing a line, enumerate every concretion the change contains that the words did NOT specify — at the **value/mechanism** level: each hardcoded number/threshold · each constant-vs-live-query (static-vs-dynamic) choice · each default · when-it-runs/refreshes (once vs every run) · any added scope/file/table/behavior — each with its 2+ literal options and which you'd pick;
   (3) non-empty list → **WRITE NOTHING**, show it, halt for his pick per item;
   (4) truly empty → say "no unspecified concretions" and proceed.
   Banned: reasonable defaults · generalizing · robustness/DRY/elegance · "while I'm at it." A "go" on VALUES is not a "go" on BEHAVIOR (live-vs-pinned, when-it-runs). Describing scope as a GOAL ("rebuild under the centroid config") is itself a violation — enumerate concretions, not intent. **Every unspecified concretion is his decision; surfacing it is your burden, never his catch.**
2. **NEVER hand-roll** what the engine/jig/orchestration already packages. Build on real seams only. (Root of the worst past blow-up: a hand-rolled `rpl_fin_6of9` with invented `FIN6_RLB_MS` / `_rolling_any_ms` instead of the jig's `finisher_parts` + `fin_unlatch_nof9`.)
3. **Describe mechanics in DATA terms** — lines/thresholds/crosses — never a trading narrative. (memory `spec-no-trading-narrative.md`)
4. **Report MEAN, not median.**

---

## 1. What the lab is for

Optimus9, Bybit perpetuals, a **causal** trade-signal system. The lab track integrates the **bp50** setup/trigger chain with the **RPL** interception + **6-of-9 confluence finisher**, and **persists every per-trade micro-decision** to a DB table (`rpl_micro`) so micro-decision reports are instant (no re-walk). Harness for bp50 = the **linelab event tape** (June, 5 s grid).

---

## 2. The chain (end to end)

```
bp50.qualify()  ─ s4Mage OOB same-side sustained >240s  AND  hs60x OOB same-side
      │
bp50.trigger()  ─ Branch A / B routing (see §3) + RGATE on gtr2   → A/B FIRE
      │
  RPL interception (build_rpl_6of9)  ─ A/B fires → BLOCK →
      _climb_to_prov from the fire bar → first r-pred rung >= TF5_FLOOR(5)?
          yes → TAKEOVER (provisional)      no → release A/B
      │
bp50.s3s4_gate()  ─ paths a/b/c → gate_open
      │
jig.rpl_fin_6of9()  ─ >=6-of-9 confluence LATCH finisher   → FLIP FINISHER (the trade)
```

- **cap** for the finisher = **hs60x opposing-breach, NO horizon** (runs until the opposing hs60x breach; not a bar count).
- `_climb_to_prov` was an **extract-method** lift of `_climb_flip`'s climb→provisional loop out of `run_chain` to module level in `rpl_walk.py`. Regression-PROVEN byte-for-byte (15 flips identical) — sweep-safe. `_climb_flip` is now a thin caller of it.

---

## 3. bp50 Branch routing + the A-LATCH (recently changed — know this)

- `_r_same_side(r, de) = (r >= 50) if de > 0 else (r <= 50)` — r on the same side of 50 as the **breach** de (lo-breach de<0 → r ≤ 50).
- **r same-side of the breach → Branch A** (x/m × Mage). **PREFERRED**, and **LATCHES one-way**: once any HTF SS is true, the walk stays A for the rest of the walk — it never demotes back to B.
- **not-same-side → Branch B** (x OOB & x×m). Eligible only **pre-latch**.
- Code: `trigger()` (`build_past50.py:194`) has `latched_A=False`, armed by `if any(SS[tf][i] for tf in HTFS): latched_A=True`, and the branch decision is `if latched_A:` (line ~220) — NOT a per-bar `if any(SS...)` (that per-bar re-check was the bug; fixed).
- **`s5m` loose thread in s3s4_gate** — Joe asked how bp50 mitigates it; that thread is noted, not closed.

---

## 4. `jig.rpl_fin_6of9` (the finisher — lives in the JIG, on real seams)

`optimus9/analysis/jig.py:114`
```python
def rpl_fin_6of9(self, arm, cap, side, sets=(('s1',19),('s2',19),('s15',19)),
                 N=6, bind_tol=6, anchor='breach'):
    parts = {s: self.finisher_parts(s, r_lb=rlb) for (s,rlb) in sets}
    return fin_unlatch_nof9(parts, arm, cap, side, N=N, bind_tol=bind_tol, anchor=anchor)
```
- Sets **s1a / s2a / s15a**, each `a` = an {m, M, r} bundle + r-lookback. **r_lb = 19 own-TF bars** for all three. **N=6, bind_tol=6, anchor='breach'.**
- SRP: the finisher **mechanic** is in the jig; the **orchestration** (who calls it, when) is in the script. Do not move orchestration into the jig (an earlier `s3s4gate_rpl_fin_6of9` chain method was added then REMOVED per SRP).

---

## 5. `build_rpl_6of9.py` — the integration + persister

**Pinned engine config** (NOT a live query — frozen snapshot; do not turn it dynamic):
```python
JUNE_END = ms(6,14); TF5_FLOOR = 5; XPRED_THRESH, XPRED_BAND = 30, 5
MINI = {'s2.r.stc':8, 's8.r.rsi':6, 'htf.r.k_len':10, 'htf.r.stc':12, 'fence_lo':30}
S2T, S8T = 2, 8
# engine wiring:
R.end_ms = JUNE_END; SW._apply_knobs(MINI)
R.FL = MINI['fence_lo']; R.FH = 100 - MINI['fence_lo']     # fence 70/30 → FL=30, FH=70
R.L0 = SW._build_line_L0(MINI)                              # per-band r on June
lr_v2.FENCE_HI, lr_v2.FENCE_LO = R.FH, R.FL
```
- **Current fence = 70/30** (`fence_lo=30` → FL=30, FH=70). Higher FH = ANTI-fence (r-pred picks only r near OOB = more selective). NOTE: the inline comment at `:43` still reads "FL=37/FH=63" — that is STALE; the runtime value is FL=30/FH=70.
- `J3 = Jig(JUNE_END, hours=40, warmup=600, overrides=ov)` — live jig with s1a/s2a/s15a bundles + gate lines (s2r/s3/s4/s1M) + hs60x. `glines(k)` = the full gate line set. `r1 = lambda v: round(float(v),1)` — **all recorded line values are 1 dp.**
- **`trace_fire(oi, de, ti)`** records ALL lines each mechanism reads: r-pred→r,m,M · x-cross-pred→x,r,s2r · flip_provisional→x,r · gate→8 lines · fin6of9→9 lines. (Reporting requirement from Joe: show every line a mechanism relied on to create its event.)
- **`persist_day(day)`** — two-phase: collect chains → sort FIRED chains by finisher time → stamp id → write.
- **`report_day(day, tid=None)`** — groups by (m_fire, m_tf); reads `rpl_micro` (instant, no re-walk).
- **CLI:** `python3 build_rpl_6of9.py --persist YYYY-MM-DD` · `--report YYYY-MM-DD [mmdd_NN]`. Run with `PYTHONPATH=/home/joe/thecodes`.

### `rpl_micro` table (schema verified 2026-07-27)
`m_id · m_tid varchar(9) · m_tf int · m_day varchar(10) · m_fire varchar(14) · m_branch varchar(2) · m_de int · m_mode varchar(12) · m_seq int · m_mechanic varchar(24) · m_time varchar(14) · m_decision varchar(400) · m_lines text · m_built ts`
- **`m_tid`** = `mmdd_NN` (e.g. `0613_01`); **finisher-ordered, FIRED-only** — the first flip-finisher after 00:00 UTC earns `_01`. Non-firing chains get NULL tid.
- **`m_fire` / `m_time`** = UTC strings, format `"mmdd hh:mm:ss"`.
- All duplicates are shown (not collapsed).

### Last persisted state — 06-13 (latched trigger, fence 70/30)
`python3 build_rpl_6of9.py --persist 2026-06-13` → **8 chains / 6 trades**, ids `0613_01`..`0613_06`, all **Branch A takeover**. Finishers: 02:09:00, 09:05:35 (×2), 19:42:05 (×3). One `06-14 01:06:30` chain is **out-of-grid** (past JUNE_END) → correctly skipped (guard: `if fts < gts[0] or fts > gts[-1]: skip`). The latch's only 06-13 effect vs pre-latch: it removed a stray **20:52:25 Branch-B** non-trade fire (SS had already latched A there). The 6 trades were unchanged.

---

## 6. OPEN THREAD (live, unresolved) — create the 05:52 long

Joe is tracing a **missing long trade at the ~05:52 low on 06-13** (hs60x bottoms −37 there). **This is the current goal.** Latest diagnosis (verified 2026-07-27):

- Onset 05:34:50, de=−1. `trigger()` (latched) returns **NO FIRE in 5h**.
- Through 05:45–06:00 the line geometry is: **x pinned deep-OOB below m, both ~30 pts below Mage.** At the 05:52 low: x=−25.9, m=−21.6, Mage=+7.6.
- **Branch A can't fire it** — needs x/m to cross UP through Mage; they're far below. First x/m×Mage up-cross is **06:05:05** (13 min after the low, past the window) and even that is rejected by the full trigger.
- **Branch B can't fire it either** — B's OOB leg IS satisfied (x below LO throughout), but the **x×m up-cross never happens** because **x stays below m the entire window** (x never overtakes m to the upside). So un-latching would NOT create the trade.
- **Conclusion:** neither existing trigger has a *cross* to fire on at the low. The latch is NOT the blocker. Creating the 05:52 entry requires a **NEW trigger** keyed off what IS present at the low — x at an OOB extreme + turning — not an x×m or x/m×Mage cross.

**AWAITING JOE'S DECISION** (do NOT pick one — build-gate): which signal defines the 05:52 entry? Candidates surfaced (present at the low): (1) x OOB-extreme + x turning up (x<LO and x[i]>x[i−k]); (2) r-based (r15 bottoms 34 / r22 bottoms 7); (3) something else he reads there. **Do not build any of these until he chooses.**

Diagnostic script used: `$CLAUDE_JOB_DIR/tmp/make0552.py` (rebuild if the job dir is gone; imports `build_past50`, walks the 05:34 onset).

---

## 7. Orientation only — the OTHER track (evo sweep)

Separate background job: `python3 -u -m optimus9.orchestration.rpl_evo_sweep` (rotating-driver elitist evo, 24 GB box), monitored via a recurring **pulse** cron (~15 min) with a strict format (MILESTONE lead · MANDATORY MAE/MFE table · proc/RAM/OOM · progress · OOS · cycle · centroids · knobs · failscan appendix · "Net:" riff). As of this handover: **cycle 3 (SPLIT), round 20**; RC adopted-net +0.145 (real o7 +0.054), RPL +0.161. Pulse format details in memory `pulse-format.md`. **Not part of the lab track — don't touch unless asked.**

Known unbuilt (do NOT build without Joe's go): `build_kpi.py` ghost guard — at cycle boundaries the latest-write `rpl_oos32` can grab a prior run's same-cycle-number row → RC oos7/maximin overstated (shows +0.145, real ~+0.054). Guard owed: reject `o32_round > current_round`. Unrequested.

---

## 8. Key files
- `build_rpl_6of9.py` — integration + persister (§5)
- `build_past50.py` — bp50 setup/trigger chain + branch latch (§3)
- `optimus9/analysis/jig.py:114` — `rpl_fin_6of9` (§4)
- `optimus9/orchestration/rpl_walk.py:144` — `_climb_to_prov`
- `docs/linelab_spec.md`, `docs/rpl_sweep_spec.md` — specs
- Memory index: `~/.claude/projects/-home-joe-thecodes/memory/MEMORY.md` (build-gate, spec-no-trading-narrative, pulse-format, linelab-signal-spec, rc-window-realtime)

## 9. DB access pattern
```python
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
d = DatabaseManager(**get_db_config()); d.connect()
# d.execute(sql, params, fetch=True) → list[dict]
d.disconnect()
```
