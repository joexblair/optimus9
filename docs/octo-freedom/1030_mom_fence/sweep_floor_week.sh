#!/bin/bash
#   THE FLOOR SETTLED ON THE WEEK. His 1030: *"settle (sweep) the floor (the control's net%) on a
#   wider window"*, net% the target.
#   THE WINDOW IS 2026-08-30 00:00:00 .. 2026-09-06 23:59:55 - 8 days, MY choice and stated: it is
#   the window every other A/B in this work used, so the rows are comparable to them. The whole
#   tape is reachable the same way and costs about 7 h of wall clock.
#   15 ARMS: the takeover OFF as the control, then the floor at 7..20. 21 or more cannot fire at
#   all with the ladder top at L2_MOM_MAXTF 20.
cd /home/joe/thecodes/docs/octo-freedom/1030_mom_fence
BASE="LG_TAPE_END=2026-10-05 W_V4_RMOM_FNC=75 W_V4_L2_MOM_MAXTF=20 W_V4_LIN2_EXFNC_LATCH_REL=lift W_V4_LIN2_COUNTER_OOB_ON=0 W_V4_EXPERIMENT=1 W_WIN_END=2026-09-06T23:59:55 W_WALKS=none"
BASE="${BASE/W_WIN_END=2026-09-06T23:59:55/}"
export W_WIN_END='2026-09-06 23:59:55'
env $BASE W_WALKS=none W_V4_LIN2_MATRY_WSF_TAKEOVER_ON=0 nice -n 5 python3 -u chain_lift_2d.py > wk_tf_off.md 2> wk_tf_off.err &
for N in 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  env $BASE W_WALKS=none W_V4_LIN2_MATRY_WSF_TAKEOVER_ON=1 W_V4_LIN2_MATRY_WSF_TAKEOVER_AT=event \
      W_V4_LIN2_MATRY_WSF_TAKEOVER_TF=$N nice -n 5 python3 -u chain_lift_2d.py \
      > wk_tf_$N.md 2> wk_tf_$N.err &
done
wait
echo "all 15 week arms done"
head -3 wk_tf_off.md
