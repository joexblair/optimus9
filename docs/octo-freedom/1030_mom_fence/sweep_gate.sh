#!/bin/bash
#   HIS 1030 CASCADE REVERSAL GATE, measured. Two arms on the 2-day window FIRST as the integrity
#   check - the gate-OFF arm must reproduce +7.2259 net exactly, because the knob is the only thing
#   that changed in v4_lineage2 and an off arm must be the arm that already ran. Then the week.
cd /home/joe/thecodes/docs/octo-freedom/1030_mom_fence
BASE="LG_TAPE_END=2026-10-05 W_V4_RMOM_FNC=75 W_V4_L2_MOM_MAXTF=20 W_V4_LIN2_EXFNC_LATCH_REL=lift W_V4_LIN2_COUNTER_OOB_ON=0 W_V4_LIN2_MATRY_WSF_TAKEOVER_ON=0 W_V4_EXPERIMENT=1 W_WALKS=none"
#   the 2-day control, gate OFF - this must print +7.2259
env $BASE W_V4_LIN2_CASC_REV_GATE_ON=0 nice -n 12 python3 -u chain_lift_2d.py > gate_2d_off.md 2> gate_2d_off.err &
env $BASE W_V4_LIN2_CASC_REV_GATE_ON=1 nice -n 12 python3 -u chain_lift_2d.py > gate_2d_on.md 2> gate_2d_on.err &
wait
echo "2-day pair done"
export W_WIN_END='2026-09-06 23:59:55'
env $BASE W_WIN_END="$W_WIN_END" W_V4_LIN2_CASC_REV_GATE_ON=1 nice -n 12 python3 -u chain_lift_2d.py > gate_wk_on.md 2> gate_wk_on.err &
wait
echo "the week gate-on arm is done"
