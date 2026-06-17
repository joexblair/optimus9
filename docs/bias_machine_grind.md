# Bias Machine — grind & todos

Living doc for the bias-machine PK grind: params to sweep, the metric, and the open
mechanism questions we're working through. Companion: `bias_machine_spec.md` (rules),
`bias_pk_pentest.py` / `.pine` (the pen-test harness).

## The root issue we're chasing (Joe 0616)
**The s30a wobs we pick don't align with the s6r oscillator's peak/trough** → the s6r
value sampled is off the turn → calcs skewed, labels inverted. No committed plan yet;
the debug knobs below are steps toward isolating/fixing it.

## Grind params (to sweep)
| param | current | sweep | notes |
|-------|---------|-------|-------|
| **anchor/floater variance** (`NEUTRAL_BAND`) | 2.2 | small steps, ~0.3 | \|anchor−floater\| ≤ band → NEUTRAL |
| _(more as they surface)_ | | | s30a definition, wobslay bars, side-of-50 cutoff, … |

## Metric (TBD — define before grinding)
- Candidate: directional-call accuracy vs forward px at +Nm (and/or PnL with a stop).
- Must handle NEUTRAL (exclude from accuracy, or count as "no trade").
- Current window (0610 11:00→0611 12:30): 15 pks, ~6/7 directional hit = coinflip → the
  root alignment issue dominates; param tuning won't rescue it alone.

## Open mechanism questions / todos
- [ ] **Root:** make the s30a wob align with the s6r peak/trough (the inversion fix).
- [ ] **s6m breach+reverse precursor** — applied to the **ANCHOR only, for now** (Joe 0616).
      Tested on closed bars. TODO: later apply wobs to a **modified emerging s6m line**.
- [ ] **Floater precursor symmetry** — should breach+reverse also gate the floater? (open).
- [ ] **side-of-50 s6r + lookback** — when no correct-side wob sits between anchor & floater,
      both inherit the same prior value → ties. NEUTRAL band masks the label; root is the
      alignment issue above.
- [ ] **Prod vs debug** — pen test uses s14M-vs-50 alignment + no OOB gate (DEBUG). Prod =
      s14M-OOB gate. Keep the debug/prod paths separable when we lock the grind.
- [ ] **s30 emerging in prod** — pen test uses closed s30; prod s30 emerging.

## Parked
- **Bar timestamp convention** (close vs open) — see spec's ⚠️ note. Re-open only if a
  mismatch shows up.

## Current debug state (0616)
- `bias_pk_pentest.py` is in **DEBUG mode**: s14M-vs-50 alignment, no OOB gate, side-of-50
  s6r with lookback, s6m breach+reverse precursor (anchor only), NEUTRAL band 2.2.
- Window 0610 11:00 → 0611 12:30. Emits 15 pks → `bias_pk_pentest.pine` (array-based).
