#!/bin/bash
# docs_reorg.sh — set up docs/ structure and migrate existing files into it
#
# Run once from project root after the migrate.py work is verified. Idempotent
# w.r.t. directory creation; will fail loudly if source files are already
# missing (which means they've already been moved). Adjust as needed.
#
# r02 = 5s PK gate + p-rev + optimus9 restructure (the work covered by
# 260514_pk5s_spec.md and downstream artifacts). r01 implicit = pre-this-
# codebase 30-day grind work.

set -e

echo "Creating docs/ structure..."
mkdir -p docs/specs docs/archive docs/sql

echo ""
echo "Moving r02 artifacts..."

# Active spec — renamed to round-numbered convention
mv 260514_pk5s_spec.md                     docs/specs/r02_260514_pk5s.md

# Archived implementation artifacts from r02 (patches applied, migrations run;
# kept verbatim for audit trail per docs/README.md policy)
mv 260514_managers_patches.md              docs/archive/r02_260514_managers_patches.md
mv 260514_managers_additions.py            docs/archive/r02_260514_managers_additions.py
mv optimus9_post_migration_patches.md      docs/archive/r02_260515_post_migration_patches.md
mv migrate.py                              docs/archive/r02_260515_migrate.py

# SQL artifacts — schema and data ops
mv 260514_schema_diff.sql                  docs/sql/r02_260514_schema_diff.sql
mv optimus9_data_cleanup.sql               docs/sql/r02_260515_data_cleanup.sql

echo ""
echo "Done. Verify with:"
echo "  tree docs/"
echo "  ls -la"
echo ""
echo "Project root should now have:"
echo "  optimus9/   tests/   docs/   run.py   logger.py   schema.sql   README.md"
echo "  (plus pytest.ini, possibly managers.py.bak if you haven't deleted it yet)"
