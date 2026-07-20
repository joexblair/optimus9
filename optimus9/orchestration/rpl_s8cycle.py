"""Thin CLI over rpl_walk.run_chain: auto-walk the day's flip chain from one seed, tee the flips, persist.
Every flip (rollercoaster reversal or climb) becomes its own DD_NN rpl_run row (rr_rollercoaster tagged).
Usage: python3 -m optimus9.orchestration.rpl_s8cycle [seed_bias] [seed_start_hhmm_day]
  e.g. python3 -m optimus9.orchestration.rpl_s8cycle          (default: bear @ 21:32 day 11)."""
import sys
import optimus9.orchestration.rpl_walk as R

seed_bias = sys.argv[1] if len(sys.argv) > 1 else 'bear'
seed_start = None
if len(sys.argv) > 2:  # "HH:MM" or "HH:MM:DD" (day defaults to 12)
    parts = sys.argv[2].split(':'); h, m = int(parts[0]), int(parts[1]); day = int(parts[2]) if len(parts) > 2 else 12
    seed_start = R._ms(h, m, 0, day=day)
R.run_chain(seed_bias, seed_start, tee=True)
