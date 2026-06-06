# <milestone> — design

**Status:** <define | explore | scope | building | done> · <date>
**Cycle shape:** Define → Explore → Scope → Decompose → Recycle (see
korero_working_relationship.md "Cycle process").

---

## 1. Objective (Define)

One paragraph: what this milestone is *for*, in the project's own terms. Why now,
where it sits in the pipeline, what it's downstream/upstream of.

## 2. What good looks like (Define — the DoD)

The bar this must clear to be "done". Phrase as outcomes, not tasks. The
**behaviour-by-example** section (§8) makes this executable.

## 3. Explore — tangents drilled

What we investigated before committing scope. Each tangent: the question, what we
found, and the call (in-scope / parked / dropped). Subagent findings land here.

## 4. Scope

**In scope (this cycle):**
- …

**Out of scope → next spec for review:**
- … (parked, not done — carry to the next milestone's Define)

## 5. Logical flow

The end-to-end mechanism at medium-low detail. Stages, the data at each, the exact
conditions/maths. Lock this *before* code.

## 6. Reuse map (SRP pass)

| need | existing (reuse / extend >80% / new) |
|---|---|
| … | … |

Run the post-doc SRP survey here — prefer extend over new.

## 7. Open decisions

The forks still needing Joe. Each: the choice, the options, the lean.

## 8. Behaviour by example (tests = DoD)

The behavioural cases that pin the spec. Mark ✅ implemented (→ test file) /
⬜ pending (the spec for the next build). Write these *first* — they map the code.

- **<unit>** — `tests/test_<x>.py` ✅ / ⬜
  - case → expected
  - edge → expected

## 9. Build status / task list (Decompose)

Numbered, ✅/⬜. Mirrors the queue. Gated items carry their blocker.

1. ⬜ …

---

## Recycle notes (fill at close)

- **Wins kept:** …
- **Failures (CI ledger):** … → fold into korero / memory
- **Disciplines that emerged:** …
- **Pruned / superseded:** …
