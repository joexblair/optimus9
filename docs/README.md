# optimus9 documentation

## Structure

```
docs/
├── README.md         # this file — folder structure + round pattern
├── specs/            # active round specs
├── archive/          # implementation artifacts from past rounds (verbatim, audit trail)
└── sql/              # schema diffs and data ops, dated by round
```

## Active spec

The current round's spec lives in `docs/specs/`:

- **r02_260514_pk5s.md** — 5s PK gate, p-rev (Pine `barmerge.lookahead_on` equivalent), optimus9 package restructure, compare workflow

## Round pattern

Each round produces one spec file in `docs/specs/`, named `rNN_YYMMDD_topic.md` — round number (zero-padded), ISO-style date of round inception, short topic slug.

Spec template:

```markdown
# Title
**Spec, YYMMDD**

---

## Changes log
*Most recent first. Each entry is a refinement made during the round.*

### YYMMDD — <subject>
<body — what changed, why>
→ updates: <which spec section / artifact was changed>

---

## Scope
<what this round delivers; what it does NOT>

## Decisions log
<every committed decision, with rationale>

## <round-specific sections>

## Open questions
<resolved questions migrate down into Decisions log; unresolved stay here>
```

The changes log at the top captures refinements **during** the round — bug fixes surfaced by smoke runs, design pivots from review feedback, follow-on tasks added mid-stream. When the round closes, the changes log is the journey; the body of the spec is the final state. Both are preserved.

## Archive policy

`docs/archive/` holds implementation artifacts from completed rounds — patches docs, migration scripts, additions files. Kept verbatim for audit trail and reproducibility. Naming: `rNN_YYMMDD_<artifact-name>.{md,py,sql}`. Once archived, files are not edited; if revisiting an old round's work is needed, branch the artifact rather than mutating it.

## SQL artifacts

`docs/sql/` holds:
- `*_schema_diff.sql` — schema migrations (ALTERs, new tables, seeds). Idempotent within each round's diff; cumulative across rounds.
- `*_data_cleanup.sql` — one-off data ops (corrections, retroactive labeling). Read the inspection SELECT at the top before running.

If rebuilding the DB from scratch: apply `schema.sql` (canonical baseline), then each round's `_schema_diff.sql` in order. Data cleanup scripts are run-once and skipped on rebuilds.

## Starting a new round

1. Pick the next sequential round number.
2. Create `docs/specs/rNN_YYMMDD_topic.md` from the template above. The date is the round's inception (not its completion).
3. Work the round. Changes log accumulates at the top; body grows organically.
4. When deliverables ship and are verified:
   - Archive patches docs and migration scripts to `docs/archive/` with `rNN_` prefix.
   - Move SQL artifacts to `docs/sql/` with `rNN_` prefix.
   - Update this README's "Active spec" pointer and "Round history" table.
5. The spec file itself stays in `docs/specs/` permanently — it's the canonical record.

## Round history

| Round | Date    | Topic                                                     | Status |
|-------|---------|-----------------------------------------------------------|--------|
| r02   | 260514  | 5s PK gate + p-rev + optimus9 restructure + compare       | active |
| r01   | —       | Initial codebase, 30-day grind on b6M (or_pk=1)           | pre-docs (not formally specced) |
