#!/bin/bash
#   THE THREE CELLS RE-RUN, ONE AT A TIME. The first attempt put them alongside 21 other arms and
#   all three wrote a 0-byte .md with a 0-byte .err - no traceback, which is what a SIGKILL leaves.
#   23 GB of memory against 21 arms at about 1 GB each is the candidate cause; dmesg is not
#   readable here so it stays a candidate. Sequential keeps the extra peak at one process.
cd /home/joe/thecodes/docs/octo-freedom/1030_mom_fence
export W_WIN_START='2026-08-30 00:00:00'
export W_WIN_END='2026-09-06 23:59:55'
export LG_TAPE_END=2026-10-05 W_WALKS=none W_V4_EXPERIMENT=1
export W_V4_LIN2_EXFNC_LATCH_REL=lift W_V4_LIN2_COUNTER_OOB_ON=0 W_V4_LIN2_MATRY_WSF_TAKEOVER_ON=0
run () {  # $1 out  $2.. the overrides
  local out=$1; shift
  env "$@" nice -n 10 python3 -u chain_lift_2d.py > "$out.md" 2> "$out.err"
  echo "$out exit $? : $(grep -c '^| TOTAL' $out.md) TOTAL row(s)"
}
run wk_fl_80_12 W_V4_RMOM_FNC=80 W_V4_L2_MOM_MAXTF=12
run wk_fl_75_12 W_V4_RMOM_FNC=75 W_V4_L2_MOM_MAXTF=12
run wk_fl_80_20 W_V4_RMOM_FNC=80 W_V4_L2_MOM_MAXTF=20
echo "the three cells are done"
