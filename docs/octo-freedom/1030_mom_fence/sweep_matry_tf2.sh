#!/bin/bash
#   THE SWEEP EXTENDED PAST 13. His gate: *"when your sweep gets to a state where the
#   LIN2_MATRY_WSF_TAKEOVER_TF is printing the same timestmaps (0441 and the other one), then you
#   can run a full sweep of all the knobs"*. 7..13 is flat - both firings rode ws18 and ws13, so
#   every value in that range admits both. Raising the floor can only ever REMOVE firings, since
#   the gate is `rider >= TF`.
cd /home/joe/thecodes/docs/octo-freedom/1030_mom_fence
BASE="LG_TAPE_END=2026-10-05 W_V4_RMOM_FNC=75 W_V4_L2_MOM_MAXTF=20 W_V4_LIN2_EXFNC_LATCH_REL=lift W_V4_LIN2_COUNTER_OOB_ON=0 W_V4_EXPERIMENT=1"
for N in 14 15 16 17 18 19 20; do
  env $BASE W_V4_LIN2_MATRY_WSF_TAKEOVER_ON=1 W_V4_LIN2_MATRY_WSF_TAKEOVER_AT=event \
      W_V4_LIN2_MATRY_WSF_TAKEOVER_TF=$N nice -n 5 python3 -u chain_lift_2d.py \
      > sweep_tf_$N.md 2> sweep_tf_$N.err &
done
wait
echo "14 to 20 done"
