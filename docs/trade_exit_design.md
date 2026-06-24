# Trade-exit: exit-line TF scales with the pk source (SnF)

**Status:** sketch (Joe 0624, born from `snf_compare`). Interrogate before building — this is a
design seed, not a settled mechanic.

## The idea
The TF of the line used in a trade's **exit** calculation scales with the TF/size of the **pk
source** that opened the trade. Larger / slower pk source → higher-TF exit line; smaller / faster
source → lower-TF exit line.

## Why (the snf_compare seed)
`snf_compare` (0624) showed the slow Major line **s12M** (TF12) fires rare, high-conviction pks —
Joe: *"the slow mover breaches in line with the big swings."* A trade opened off a slow/big pk
should be held against a **slow** exit line (ride the swing); a trade off a fast pk (s3m, TF3) should
exit on a **fast** line (take it and go). Today's exit uses a fixed line (s30 / TF30, the "next
opposite s30 wob with gate lines OOB") — which mismatches both ends of the spectrum.

## Open questions (resolve with Joe before building)
- **Mapping** — pk-source TF → exit-line TF. Linear, tiered, or a DB lookup (no-hardcode)?
- **Which line** — the same `s{tf}{M/m/r}` family at the scaled TF? Which variant carries the exit?
- **Exit condition** — does the scaled line replace the **wob line** (s30), the **gate lines**, or
  both, in `BiasWindow.run()`'s "opposite wob + gate OOB" exit?
- **Integration** — relationship to the BL machine's exit3 (BB×K cross + anchored wobble). Separate
  exit, or one unified mechanic?
- **pk "size"** — measured by the trigger TF, the osc TF, or the realised swing magnitude?

## Validation
Grind the exit-line TF (a sweep) against the first-trade metric (pnl · mae · hit) **per pk-source
TF**, across the 9 bias_eval windows — confirm the TF-scaling actually lifts the outcome before
baking it. SRP: the exit is its own responsibility — feed it the trade + the pk-source TF, let it
choose the line; do not fuse it into entry/placement.

Related: `snf_compare.py`, the bias cascade (`bias_machine.placements`/`run`), the BL exit3 design.
