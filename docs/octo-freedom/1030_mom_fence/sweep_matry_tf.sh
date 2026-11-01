#!/bin/bash
#   LIN2_MATRY_WSF_TAKEOVER_TF SWEPT 7..13, his 1030: "this indicates that the
#   LIN2_MATRY_WSF_TAKEOVER_TF is too low. sweep upwards from 7 to 13".
#   ONE PROCESS PER VALUE, so the refusal gate sees each value in its own environment and prints
#   its own deltas - a value mutated after import would walk off-ruled while the gate's printout
#   still named 7.
#   THE CONTROL ROW is the takeover OFF, run from the same code state as the seven arms.
cd /home/joe/thecodes/docs/octo-freedom/1030_mom_fence
BASE="LG_TAPE_END=2026-10-05 W_V4_RMOM_FNC=75 W_V4_L2_MOM_MAXTF=20 W_V4_LIN2_EXFNC_LATCH_REL=lift W_V4_LIN2_COUNTER_OOB_ON=0 W_V4_EXPERIMENT=1"
env $BASE W_V4_LIN2_MATRY_WSF_TAKEOVER_ON=0 nice -n 5 python3 -u chain_lift_2d.py > sweep_tf_off.md 2> sweep_tf_off.err &
for N in 7 8 9 10 11 12 13; do
  env $BASE W_V4_LIN2_MATRY_WSF_TAKEOVER_ON=1 W_V4_LIN2_MATRY_WSF_TAKEOVER_AT=event \
      W_V4_LIN2_MATRY_WSF_TAKEOVER_TF=$N nice -n 5 python3 -u chain_lift_2d.py \
      > sweep_tf_$N.md 2> sweep_tf_$N.err &
done
wait
echo "all eight arms done"
for f in sweep_tf_off sweep_tf_7 sweep_tf_8 sweep_tf_9 sweep_tf_10 sweep_tf_11 sweep_tf_12 sweep_tf_13; do
  echo "$f : $(grep '^| TOTAL' $f.md 2>/dev/null || echo 'NO TOTAL ROW')"
done
