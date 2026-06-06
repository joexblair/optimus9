# r07 — Vote Machine Architecture (design sketch)

**Status**: pre-code design. Update with corrections before writing the apply script.

---

## Terminology

Before sketching, lock in the words. Sloppy usage of "pool" caused
confusion in the v1 draft of this doc.

- **Pool** — full settings group for ONE line: p_c, p_w, p_r,
  suppression, slope, multiplier, weight_close, weight_wide. One pool
  per line. NOT split into close vs wide.
- **Probe** — a close or wide measurement WITHIN a pool. Two probes per
  pool, distinct distances (pool_c vs pool_w bars back) and weights
  (weight_close vs weight_wide). The vote machine aggregates per-probe
  contributions.
- **Voter** — synonym for pool in vote-machine context. Multi-line SnF
  has multiple voters, each a pool. Single-line gca5m has one voter
  with two probes.

When the vote machine "aggregates," the signal is per-bar but compiled
from probe-level contributions across one or more pools/voters. The
chain (probe state → pool weight → vote bucket → ratio → pk_raw) should
remain conceptually traceable. Whether it remains **persistently**
traceable is an open schema question (see below).

---

## Why now

Surfaced by the PM additive discussion:
1. Python has TWO incompatible signal-generation paths:
   - **Self-gated**: vote machine, no external gate (Pk5sGateComputer)
   - **Gated**: external gate, no vote machine (PKSignalDetector)
2. Pine has both: vote machine + external gate as final filter.
3. Production target is "gated always on" (per user). Multi-line SnF needs voting.
4. PM additive doesn't have a home in the current gated path because there's
   no vote machine to additively contribute to.

Adding PM additive to Pk5sGateComputer as-is would cement a do-everything
class and tangle PM math with line computation, decision delay, persistence.
Better to extract vote machine first, then PM additive lands in a clean class.

## Pine deprecation (decided 2026-05-26)

The hybrid pilot path (Pine alerts → webhook → Python orders) is dropped.
Python becomes the production engine. Pine remains as a **visualization and
validation tool only**.

What this changes:
- Python's vote machine is **canonical**, not a port of Pine's. We're free
  to deviate where it improves the production implementation.
- Pine-Python parity is no longer a constraint. Snapshot validation
  remains useful for catching unintended drift, but Pine and Python can
  diverge intentionally.
- Decision delay state machine survives the r07 refactor for parity-with-
  current-Python (pure refactor discipline) but is questionable post-extract.
  Filed as a separate r07/r08 decision: keep or drop based on whether it
  serves production. User has flagged it as hostile to HTF anchors.
- pm_option_a vs pm_option_b: production probably keeps pm_option_b (the
  one that lets the control voter have effect). Resolve before Step 5.
- Control voter: works in Pine's vote arithmetic. Question whether it
  serves Python production separately from Pine. Filed.

---

## Current state

**Pk5sGateComputer.compute()** — does everything for the self-gated path:
- Per-line line computation (calls `_compute_line`)
- Per-pool state classification (`_states_standard`, `_states_roc_curl`)
- Vote folding (long_pts, short_pts, neutral_pts accumulation)
- PM suppression (`adj_long = max(0, long_pts - pm_short_wt * pm_supp)`)
- Ratio computation and threshold check (`pk_raw`)
- Decision delay state machine (`_apply_decision_delay`)
- Returns: `s5_pk_final` array (sign-inverted for fold_gates)

**PKSignalDetector.detect()** — does the gated path:
- Per-pool state classification (delegates to PKStateComputer)
- Per-pool transition detection
- Per-pool gate filter (delegates to PKGateFilter)
- Returns: list of signal dicts (per pool)

**Mismatch**: SignalDetector doesn't aggregate. GateComputer aggregates but
has no external gate. Production needs both.

---

## Proposed classes

### `PKStateComputer` (existing — unchanged)
Pure per-pool state math. Vectorized. No changes needed.

### `PKGateFilter` (existing — minor extension)
Currently a per-bar boolean predicate. May need a vectorized form for
operating on full arrays in the vote pipeline, but interface stays clean.

### `PKVoteMachine` (NEW)
Pure vote-folding math. Single responsibility: take per-probe state arrays
from one or more pools, return long_pts/short_pts/neutral_pts plus derived
ratios and pk_raw.

**Step-2 signature** (initial extract, NO pm_additive yet):

```python
class PKVoteMachine:
    def __init__(self,
                 pm_suppress_str: float = 0.5,
                 control_voter_weight: int = 0,
                 pm_option_a: bool = False):
        ...

    def aggregate(self,
                  probe_states: dict,    # {(pool_id, 'close'): arr, (pool_id, 'wide'): arr, ...}
                  probe_weights: dict,   # {(pool_id, 'close'): w_close, (pool_id, 'wide'): w_wide, ...}
                  threshold_long: float,
                  threshold_short: float) -> dict:
        """
        Vectorized vote aggregation. Returns:
          {
            'long_pts':     array,
            'short_pts':    array,
            'neutral_pts':  array,
            'long_ratio':   array (0-10 scaled),
            'short_ratio':  array (0-10 scaled),
            'pk_raw':       array (-1, 0, +1),
            'contributors': optional per-bar metadata for traceability
          }
        """
```

**Step-4 signature** (after pm_additive lands — additive args appear here):

```python
class PKVoteMachine:
    def __init__(self,
                 pm_suppress_str: float = 0.5,
                 pm_additive_close_str: float = 0.0,   # NEW in Step 4
                 pm_additive_wide_str: float = 0.0,    # NEW in Step 4
                 control_voter_weight: int = 0,
                 pm_option_a: bool = False):
        ...
    # aggregate() signature unchanged; new args feed internal logic only
```

**Implementing Step 2: use the Step-2 signature exactly.** Don't pre-add
the pm_additive args; they land in Step 4 with their own validation pass.

Single-line gca5m: one pool_id, two probes (close + wide).
Multi-line SnF (r08): N pool_ids, two probes per pool.

Notes on PM mechanics inside `aggregate`:
- PM_LONG / PM_SHORT route to neutral_pts at full weight (current behavior)
- **Step 4 only**: PM_LONG / PM_SHORT ADDITIONALLY add
  (probe_weight * pm_additive_X_str) to
  the matching directional bucket. pm_additive is per-probe-type (close
  vs wide), NOT per-pool — the same additive strength applies across all
  pools' close-probes (and similarly for wide-probes).
- adj_long = max(0, long_pts - pm_short_wt * pm_suppress_str) (existing)
- adj_short = symmetric
- active_w = adj_long + adj_short + neutral_pts (under pm_option_a=false)
- ratios = adj_X / active_w × 10
- pk_raw fires when ratio exceeds threshold

### `PKDecisionMachine` (DROPPED)

**Original plan**: extract decision delay (countdown + opposing-PK
cancellation) into its own class.

**Updated decision (2026-05-26)**: decision delay is **deleted from
Python's production path entirely**. Reason: user has flagged it as
hostile to HTF anchor signals — valid 5s pks get cancelled by noisy
opposing-direction PKs during the countdown window. Cost > benefit.

Implementation impact: `Pk5sGateComputer._apply_decision_delay` gets
deleted (not extracted). `pk_raw` becomes `s5_pk_final` directly. No
new class.

Pine retains decision delay because it's a validation tool — visual
comparison may still want to mirror the original behavior in some
contexts. But it's not load-bearing for production.

### `PKSignalDetector` (existing — promoted to flow manager)
Becomes the workflow orchestrator. Composes state → (vote) → gate → emit.
Different configurations for different use cases:

```python
class PKSignalDetector:
    def __init__(self,
                 state_computer: PKStateComputer,
                 gate_filter: PKGateFilter,
                 vote_machine: Optional[PKVoteMachine] = None):
        ...

    def detect(self, line, dema, pool_c, pool_w, pool_range, multiplier,
               slope_floor, oob_side, params, line_type='bb') -> list:
        """
        Flow:
          1. Compute per-pool states (PKStateComputer)
          2. If vote_machine: aggregate probe states into pk_raw,
             then apply gate filter to aggregate result
             Else: per-pool gate filter on each probe state (current behavior)
          3. Detect transitions and emit signals
        """
```

When `vote_machine=None`: current per-pool transition behavior. Validates
against or_pk=44/47.

When supplied: vote-machine path. New production-target flow.

Note: no `decision_machine` arg. Decision delay deleted (see PKDecisionMachine
section above).

### `Pk5sGateComputer` (existing — becomes a thin composer)
Refactored to use PKVoteMachine. Its `compute()` becomes the wiring:
load votes, compute per-probe states, hand to vote machine, return
s5_pk_final (no decision delay).

---

## Migration path

**Step 1** ✅ **DONE 2026-05-26**: Delete decision delay from Pk5sGateComputer.
- Removed `_apply_decision_delay` method, `decision_dly` param lookup
- `s5_pk_final = pk_raw` direct assignment in place
- Apply script `apply_r07_remove_decision_delay.py` shipped with WARNING
  block documenting the skip-logic bug (do not model on this script)

**Step 2** ✅ **DONE 2026-05-29**: Extract PKVoteMachine WITHOUT pm_additive.
- `optimus9/compute/pk_vote_machine.py` — pure vote-folding math
- `Pk5sGateComputer.compute()` rewritten as thin composer; optional
  `vote_machine` constructor injection point added
- 14 unit tests in `tests/test_pk_vote_machine.py` cover the math
  including a regression test against hand-calculated inline values
- Stale `tests/test_pk5s_gate_computer.py` deleted (only tested the
  removed `_apply_decision_delay`)
- Validation: or48 grind on tc_pk=99 (1-day, gated path) produced
  structural shape matching or47 (80 combos, all grid points,
  tight signal-count distribution, monotonic patterns preserved).
  Signal counts +50% vs or47 due to different 24h market window;
  TV's independent backtest showed +40% over the same windows,
  confirming regime variance not code drift. PKVoteMachine integration
  for non-empty pk_5s extensions remains unvalidated end-to-end (no
  active config exists); unit tests cover the math, integration
  coverage waits for SnF or a self-gated test config.

**Step 3** (CC's lane): Promote PKSignalDetector to flow manager.
- Optional vote_machine constructor arg (no decision_machine — dropped)
- When None, behaves exactly as today (validates against or_pk=44/47/48)
- When supplied, new vote-machine flow available
- Validate: or_pk=48 re-run with vote_machine=None still produces
  identical signals (vote machine NOT engaged for single-line gca5m
  without vote_machine arg)

**Step 4** (CC's lane): Add pm_additive to PKVoteMachine.
- Two new constructor args: `pm_additive_close_str`, `pm_additive_wide_str`
- Default 0.0 (no behavioral change)
- New behavior: PM sentinels add to matching directional bucket too
- Validate: 0.0 settings produce same output as Step 3

**Step 5 (r08+)**: Production engine.
- Live tick consumer (extends/replaces TickCollector)
- Live signal engine using vote machine + gate filter
- Position management
- Order placement via Bybit API
- Monitoring/observability
- Bigger than this milestone — its own backlog when we get there

---

## Validation strategy

At each step, the test is: **re-run a known reference grind, signal counts
and timestamps match**. The snapshot CSV approach we used for Phase A
validation works directly.

Step 1-3 validations use or_pk=44/47 (gated path, no vote machine).
Step 4 validation needs a self-gated reference grind (or_pk TBD).
Step 5 validation is the new production-target grind — no comparison
reference, just sanity checks (signal count plausible, win rate sensible).

---

## Observations to verify in Python

### Pine PM additive behavior — non-linear and polarising (verify post-Python implementation)

User tested PM additive in Pine. Observation: behavior appears non-linear
and polarising — small input changes produce disproportionate output
changes; trades concentrate at threshold-crossing boundary conditions.

**Likely cause (theory)**: PM additive contributes `weight * additive_str`
to the matching directional bucket. The vote ratio then divides into a
threshold check, which creates step-function behavior. A small additive
increase pushes barely-below-threshold bars above threshold, fires them.
This is mathematically expected from any threshold-based vote machine.

**Plan**: implement PM additive in Python's vote machine. Run grind
across the additive parameter range. If Python shows the same non-linear
response surface, it's the math (not a Pine quirk). If Python shows
smoother behavior, Pine has an implementation issue worth diagnosing.

Filed so future-us doesn't try to "fix" the non-linearity if it turns
out to be the correct behavior.

---

## Open design questions

1. **Signal traceability**: a vote-machine signal at bar i was compiled
   from probe-level contributions across one or more pools. The chain is
   real even if compact. Options for persisting it:
   - JSON column on pk_signals carrying `{contributing_probes: [...]}`
   - A new pk_signal_contributions table joined back at query time
   - Most-significant-contributor stored as `pks_pool` (lose detail
     but keep the existing schema unchanged)
   - Aggregate-only persistence (pks_pool='aggregate', detail discarded)
   Real tradeoff — detail vs schema simplicity vs storage size. Worth a
   focused conversation when we hit Step 5.

2. **Multi-line voting**: PKVoteMachine.aggregate() takes `pool_states`
   as a dict. For multi-line SnF, it'd be `{line_name: {pool: state}}` or
   `{(line_name, pool): state}`. Need to decide the shape now or accept
   refactor later. Lean: single-line for r07, multi-line for r08.

3. **PKStateComputer's responsibility**: currently the state computer is
   per-pool. For multi-line, each line has its own state computer (or
   the state computer takes line config as an arg). Probably needs a
   factory or per-line instances.

4. **Persistence schema**: pk_signals carries per-pool columns (pks_pool,
   pks_pool_c, pks_pool_w). Vote-machine signals don't fit cleanly.
   Schema migration question for the production grind.

These don't need to be solved before code starts — they surface during
implementation. But filing here so we don't forget to think about them
when we get to Step 5.

---

## Plan progress and next-session framing

**Step 1 (delete decision delay): DONE 2026-05-26.** Behavior change —
subsequent self-gated grinds will produce more signals than r06-era
output (decision delay was filtering pk_raw fires that opposed pending
state). This drift is INTENDED.

**Next session targets Step 2** (extract PKVoteMachine). Step 3
(promote PKSignalDetector to flow manager) is the natural follow-on
once Step 2 validates. Step 4 (pm_additive) is small and lands after
the extract is clean.

**If Steps 2-3 take longer than expected**: stop after Step 2, ship
the extract without flow-manager promotion. Step 3 isn't load-bearing
on its own — its job is to make the vote machine reachable from the
gated path, which we can wire later.

**Step 5 (production engine)**: own milestone (r08+). The vote machine
extract and flow-manager promotion give us the building blocks; Step 5
wires the production pipeline around them.
