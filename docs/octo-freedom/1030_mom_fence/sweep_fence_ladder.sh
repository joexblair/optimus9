#!/bin/bash
#   THE COUNTERFACTUAL HE ASKED FOR. His 1030: *"fence 75/25, ladder ws1..ws20 - did we prove that
#   this was better than 80/20, ladder ws1..ws12?"*. It was never run: fence_pop.md and
#   latch_release_ab.md counted lines and latch holds, not legs, and every chain walk in this
#   directory is at 75/25 with ws20.
#   FOUR CELLS, the takeover OFF on all of them so the fence and the ladder are the only things
#   moving. The 75/25 + ws20 cell is wk_tf_off.md, already running in the floor sweep.
cd /home/joe/thecodes/docs/octo-freedom/1030_mom_fence
export W_WIN_END='2026-09-06 23:59:55'
BASE="LG_TAPE_END=2026-10-05 W_V4_LIN2_EXFNC_LATCH_REL=lift W_V4_LIN2_COUNTER_OOB_ON=0 W_V4_LIN2_MATRY_WSF_TAKEOVER_ON=0 W_V4_EXPERIMENT=1 W_WALKS=none"
#   the BANK's fence and ladder - the only cell with no RMOM_FNC or L2_MOM_MAXTF override at all
env $BASE nice -n 10 python3 -u chain_lift_2d.py > wk_fl_80_12.md 2> wk_fl_80_12.err &
#   the fence alone
env $BASE W_V4_RMOM_FNC=75 nice -n 10 python3 -u chain_lift_2d.py > wk_fl_75_12.md 2> wk_fl_75_12.err &
#   the ladder alone
env $BASE W_V4_L2_MOM_MAXTF=20 nice -n 10 python3 -u chain_lift_2d.py > wk_fl_80_20.md 2> wk_fl_80_20.err &
wait
echo "the three counterfactual cells are done"
