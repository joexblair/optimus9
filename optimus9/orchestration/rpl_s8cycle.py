"""Thin CLI over rpl_walk.run_walk: run one flip walk, tee the events, persist to DB.
Usage: python3 -m optimus9.orchestration.rpl_s8cycle <walk> [depth] [dwell]   (defaults from DB baseline).
Persistence is intrinsic to run_walk (tee=True => refresh rpl_event); this is just the CLI entry."""
import sys
import optimus9.orchestration.rpl_walk as R

WALK = sys.argv[1] if len(sys.argv) > 1 else '12_02'
depth = int(sys.argv[2]) if len(sys.argv) > 2 else None
dwell = int(sys.argv[3]) if len(sys.argv) > 3 else None
R.run_walk(WALK, depth, dwell, tee=True)
