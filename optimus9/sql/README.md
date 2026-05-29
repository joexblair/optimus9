# optimus9/sql/

SQL artifacts for the optimus9 project — stored procedures, views,
schema migrations. The MySQL database `pk_optimizer` holds the live
versions; this directory is the source-of-truth for re-creating them
from scratch and for code review.

## Layout

```
optimus9/sql/
├── README.md          — this file
├── procs/             — stored procedures (callable utilities)
│   ├── clone_test_config.sql
│   ├── delete_test_config.sql
│   └── inspect_test_config.sql
├── views/             — read-only abstractions (empty for now)
└── migrations/        — schema DDL changes (empty for now)
```

## File conventions

**Header block**: every `.sql` file starts with a comment block stating:
- Filed (milestone or date)
- Intent (one-paragraph purpose)
- Usage example
- Dependencies (other procs, tables it touches)

**DROP-then-CREATE**: every proc file begins with `DROP PROCEDURE IF
EXISTS <name>;`. Re-running a file is always safe; never partial state.

**No business logic inline**: procs are utilities (clone, delete,
inspect) — orchestration. They do NOT encode grind logic, signal
detection rules, or anything domain-specific. That stays in Python.

**Hard refuse over force flags**: when a proc has a safety condition,
it errors rather than offering a `force=true` bypass. Force flags
encourage accidents. If the caller needs to bypass, they handle the
upstream condition explicitly.

## Installation order (fresh DB)

For a fresh `pk_optimizer` database, install procs in this order:

```bash
mysql -u <user> pk_optimizer < procs/inspect_test_config.sql
mysql -u <user> pk_optimizer < procs/clone_test_config.sql
mysql -u <user> pk_optimizer < procs/delete_test_config.sql
```

Order matters only if procs call each other — currently they don't,
but the install order shown is alphabetical-by-dependency-direction
(inspect is the read-only base, clone creates, delete destroys).

## Current procs

### inspect_test_config(tc_pk)

Returns 4 result sets showing the complete picture of a tc_pk:
header, params, extensions, votes. Use to audit before grinding or
verify a clone landed correctly. Errors if tc_pk does not exist.

### clone_test_config(src_tc_pk, OUT new_tc_pk)

Faithful clone of a tc_pk plus all dependent rows. Auto-suffixes the
new label with `_clone` or `_cloneN` so source attribution survives a
chain of clones. Returns new tc_pk via OUT param. Errors if source
does not exist.

### delete_test_config(tc_pk, confirmation_token)

Safe delete of a tc_pk with FK-correct deletion order (cascade is NOT
enabled on the relevant parent FKs, so dependents are dropped explicitly
in bottom-up order). The confirmation_token is a required second
parameter that keeps the safety surface visible at every callsite:

- `''` (empty string) — safe path. Hard refuses if any optimizer_runs
  reference the tc_pk. Caller must clean up runs first.
- `'force'` — override path. Cascade-deletes the optimizer_runs and
  their pk_signals + pk_outcomes before removing the tc_pk. Case-
  sensitive, lowercase only.
- Anything else — error (catches typos like `'Force'`, `'yes'`, etc.).

Returns a confirmation row showing what was actually deleted
(deleted_tc_pk, deleted_label, force_used, runs_deleted,
signals_deleted, outcomes_deleted, status).

Examples:
```sql
CALL delete_test_config(101, '');         -- safe delete (no attached runs)
CALL delete_test_config(101, 'force');    -- override (also drops runs)
```

## Version notes

Procs land in the codebase as part of the milestone where they're
written. The header block's "Filed" line gives the milestone.

When a proc's signature changes (new params, different return shape),
bump the version in the header and document the change at the top of
the file. Backwards-incompatible changes need a deprecation note.

The DB has the live copy; this directory has the recipe. If they
drift, the directory is authoritative — re-run the file against the
DB to resync.

## Future additions (filed)

- **views/active_grinds** — view showing tc_pks currently configured
  for active grinding (no orphans, valid gates, sane param ranges).
  Useful for the eventual UI's tc-picker.

- **procs/archive_grind_run** — companion to the r07-filed archive util.
  Dumps pk_signals + pk_outcomes for an or_pk to compressed CSV, then
  DELETEs from MySQL. Currently planned as Python; reassess if SQL is
  the cleaner home.

- **migrations/** — populates when we change schema. Currently the
  schema is hand-maintained via DbForge; migrations land here when
  we adopt versioned schema management (likely r08 production engine
  work, where the live trading DB needs reproducible deploys).
