#!/bin/bash
# octo-sig (WALK FIRES FROM) for 09-25 .. 10-03, on the extended tape.
# --tape-end 2026-10-04 => the tape ends 2026-10-03 23:59:55, the furthest FULL day in
# kline_collection (which runs to 2026-10-04 17:35:55). Sequential: each Rig loads the full line
# set and parallel runs OOM.
cd /home/joe/thecodes
for d in 2026-09-25 2026-09-26 2026-09-27 2026-09-28 2026-09-29 2026-09-30 2026-10-01 2026-10-02 2026-10-03; do
  s=$(date +%s)
  timeout 3600 python3 report_leash_walk.py --day "$d" --tape-end 2026-10-04 \
    > /home/joe/.claude/jobs/6eb9931e/tmp/octosig/$d.out 2>&1
  rc=$?
  echo "$d exit=$rc secs=$(( $(date +%s) - s )) rows=$(grep -c '^R|[0-9]' /home/joe/.claude/jobs/6eb9931e/tmp/octosig/$d.out) $(grep -m1 '^W|' /home/joe/.claude/jobs/6eb9931e/tmp/octosig/$d.out)"
done
echo ALLDONE
