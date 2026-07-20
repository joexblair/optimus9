# Quirks to remember

A lean, high-RoI glossary of Optimus9 concepts that recur — the things Joe has had
to explain more than once. Keep it short and cheap to reference. Append a new
concept only when it's genuinely a repeat-explained convention; detailed/reference
material (e.g. settings cheat sheets) lives in its own doc.

---

## Blown-up lines — `itf_seconds` vs `itf_label`

A line can run on a **real** timeframe but **behave** like a higher one, by
multiplying its length settings. This is why `indicator_timeframes` carries BOTH:

- **`itf_seconds`** — the actual TF the line is computed on (its base cadence).
- **`itf_label`** — the TF it *emulates* (what it behaves like).

**Example — s18:** a standard `s`-series config with its lengths **×3**. It runs
on **TF6 (360s)** but **behaves like a TF18 line**. So in `indicator_timeframes`
it maps to `itf_pk 10` = `itf_label '18'`, `itf_seconds 360` — *not* the plain
`'6'`/360s entry (`itf_pk 6`). Two 360s rows exist for exactly this reason.

Naming: a line's name is `{is_prefix}{itf_label}{il_suffix}` — e.g. `s18m` =
`s` + `18` + `m`; `hb9b` = `hb` + `9` + `b`.

---

## SnF — Support and Friction

`SnF` is how the machine **compares PK signals from multiple sources** — the
interplay of *support* (signals agreeing/reinforcing) and *friction* (signals
opposing). It's the lens for multi-source PK arbitration / line composition, NOT
"snap and freeze" (an early wrong guess). The full SnF is an r08 coalition engine
(see `gate_sweep_design.md` / `cluster_scoring_design.md`).

For the BL HTF PK (exit4), the 5s-native trigger is run "through a SnF class stub"
— for now a straight passthrough to the gca5m 5s PK.

**Terminology + properties:**
- **raw pk** = a 5s-native PK. Two things we rely on: they *cluster around swings*,
  and their *shape is regime-invariant* — the macro energy/shape of a messy day vs a
  smooth day does not filter down to or change the shape of a 5s pk.
- **SnF pk** = the result of **bonded** raw pks (the coalition output). PK *strength*
  (e.g. vote-bucket lopsidedness — 7L/1S is stronger than 7L/3S) is measured at the
  **SnF-pk** level, not the raw-pk level.

---

## BL line layering — a line owns only the swing it sees

The BL lines stack across timeframes (LTF → HTF). A **30s line cannot know what the
HTF lines do above it** — by design. Its only job is to reliably **own the swing it
sees**: clock a modicum of profit on the local swing it can resolve. That mid-level
reliability is what the heavy-lifting HTF BL lines lean on; the LTF line is not asked
to predict the macro, only to be a dependable component.

Consequence for grinding/scoring LTF lines: **rank by reliability, not peak PnL.** A
combo that is net-positive in *every* window with steady placement win% beats one that
spikes in a single window and bleeds the rest. (s30r/s30M dial-in, 2026-06-12.)

The cascade reads LTF→HTF: shorter TF-relative indicator lengths react sooner, so LTF
lines breach *first* and bob in/out of OOB while the slower lines catch up; the gate
(combined state) only resolves when every line is at 3/0. (See `bl_machine_design.md`.)

---

## Index bars vs event bars — the reporting/analysis gotcha (0720)

Lines compute on the **event tape** (real-trade bars, `volume>0`) and forward-fill onto
the full 5s **index grid** (`filler_invisible`, default ON). So a value at a 5s index
slot with no trade is a **carry-forward** of the last real bar, not a fresh observation.

- **Symptom:** a table/probe walking the full 5s grid shows timestamps that don't exist
  as trades (e.g. no 05:42:00 event bar — the tape jumps 05:41:55 → 05:42:10), with
  repeated values across filler slots.
- **When it bites:** any *ad-hoc probe or table* that indexes `ts` on a fixed 5s stride.
  Cross detection in the flow is mostly safe (a forward-fill repeats the value, so
  `sign()` doesn't change → no phantom cross at fillers; the cross fires at the next real
  bar). Reporting is where it misleads.
- **Fix:** pull the event-bar mask from the base tape volume — `evt = jig.W.base['volume']
  > 0` — and index/pad/lead-in on `np.flatnonzero(evt)`, not the raw 5s stride. The
  cadence between event bars is irregular (~5–20s by trade activity), not a clean 5s.
- Related: `project_filler_invisible` (the fix), `frozen_tape_failure` (V=0 dojis).
