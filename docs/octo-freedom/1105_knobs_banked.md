# every v4 knob at its banked value — 2026-11-05

HIS 1105: *"update specs and store all knobs, and make that config the machine"*.

Generated from `v4_knobs.table()`, which reads the RULED registry and the live values in one
pass, so the "ruled" column is a live check rather than a claim. A knob off its banked value
refuses the run unless `W_V4_EXPERIMENT=1` is set - THIS TABLE IS THE MACHINE.

| the count | value |
|---|---|
| knobs in the registry | 193 |
| off the bank | 0 |
| added at 1105 | 4 |

| the knob | value | units | ruled | Joe's words |
|---|---|---|---|---|
| `RMOM_FNC` | 75.0 | r-points | YES | "v4_rmom_fnc, default 80 - fence used when testing if a r is close enough to oob to be predicted" |
| `LIN_HOP` | 2 | TFs | YES | "1, 2" |
| `IB_WOB` | 3 | bars | YES | "10, 3" - SUPERSEDED by LIN_IB_DWELL |
| `LIN_IB_DWELL` | 2.5 | bars per TF | YES | "it needs to be dynamic: let's start with int(TF * {knob:2.5, `V4_LIN_IB_DWELL`})" |
| `TF_CEILING` | 10 | TF | YES | "18, unsure.  use 10" - PROVISIONAL |
| `LIN_PASS` | ib | mode | YES | the code's original. His 1022 spec says "reversal" - 1023 |
| `LIN_LOOKBACK_FLOORED` | 1 | yes/no | YES | "yes" to rungs below ws6 never looking back - 1023 |
| `LIN_LOOKBACK_FLOOR_TF` | 6 | TF | YES | "ws6 needs to be the complimentary knob" - 1023 |
| `R_RSI` | 5 | bars | YES | DEBANKED to the DB row 1024 - see the R_* block above |
| `R_STC` | 8 | bars | YES | DEBANKED to the DB row 1024 - unchanged, the DB and the sweep centroid agree on stc |
| `R_KLEN` | 7 | bars | YES | DEBANKED to the DB row 1024 - see the R_* block above |
| `MAX_PYRAMID` | 1 | positions | YES | "set pyramid to 1" - 1024 |
| `BSTOP_OOB_WHEN` | window | mode | YES | "I think the answer is 'just recent'" - 1022, defaulted 1023 |
| `BSTOP_CASCADE_AT` | lift | mode | YES | "not extrema - measure where the r reversals print" - #25, defaulted 1023 |
| `V4CORE_MAGE_FNC` | 5.0 | r-points | YES | "same-side past 5/95" - 1023, his eyeballing, held |
| `V4CORE_STEP0_JOIN` | and | mode | YES | "STEP0 is specifically AND to avoid re-entering mid cycle and creating a second stop" - 1023 |
| `SAV_WS2_OOB_TEST` | 16.0 | minutes | YES | "increase CAP to {knob:16} minutes, and start the timer when the trade opens" |
| `SAV_IB_XWOB` | 2 | bars | YES | "23, 2" |
| `SAV_MAGE_GATE_WOB` | 8 | bars | YES | "IF any ws1Mage bar lands outside of the past-50-gate (wob 8), route to the ws1r mage-cascade test" |
| `SAV_CASCADE_GAP` | 12 | bars | YES | "create a v4-saviour specific knob that looks back in 1 minute jumps" |
| `SAV_CASCADE_ZOOM` | 2 | rungs | YES | "26, 2 knob" - the Jig's MC_ZOOM, captured at v4 level |
| `SAV_CASCADE_MIN` | 4 | lines | YES | his 1017 "4 or more consecutive TFs" - the Jig's MC_MIN, captured at v4 level |
| `SAV_CASCADE_TF_HI` | 12 | TF | YES | THE BANKED LADDER TOP, what v4_machine gets. HIS 1103 "reduce the mage cascade to ws1-ws6" is fdm2's own value, passed by its driver so the live machine is untouched |
| `SAV_CASCADE_ANCHOR` | liftoff | ? | YES | HIS #25 "not extrema - measure where the r reversals print" is the bank. "ws1mage" is his 1103 "test at the ws1Mage extremum", passed by fdm2's driver |
| `SAV_CASCADE_MODE` | extrema | mode | YES | "25, not extrema - measure where the r reversals print" for the r-driven reads; the ROUTED read is anchored on the ws1Mage extrema, so this mode is 'extrema' |
| `TRAJ_WIDTH` | 21.0 | bars per TF-minute | YES | "lock it in" - 1.75 of the line's own bar, the measured peak on BOTH ws21r and ws13r |
| `TRAJ_MIN_FRAC` | 0.5 | fraction of the block | YES | HELD at 0.5 through the width sweep, NOT swept itself |
| `TRAJ_MIN_TRAVEL` | 0.0 | r-points | YES | Joe 0924: *"I would say the true threshold is in the OOS data"* - UNSET, and it passes dust |
| `BSTOP_SYNC_MIN` | 8.8 | minutes | YES | "the ws1r,ws2r,ws3r oob condition has a +/-8.8 minute window to sync with ws5r reversing.  this needs to be causal" |
| `BSTOP_POOL_HI` | 3 | TF | YES | "(ws1r or ws2r or ws3r are same side oob)" |
| `OOB_FNC` | 15.0 | r-points | YES | standing - oob is ALWAYS 15/85. ONE knob: *"oob_hi and oob_lo are expressed as one knob, to avoid imbalnace.  the formula is (100 -{knob:15})"* |
| `MID_FNC` | 50.0 | r-points | YES | "change `mid` to a fence, same logic as above. 100-{knob:50}" |
| `LIFT_PTS` | 6 | samples | YES | "34, 6 knob" |
| `LIFT_TOL` | 2.0 | r-points | YES | "35, 2.0 knob" |
| `LIFT_WOB` | 8 | bars | YES | "37, 8 knob" and "add a wob 8 to reduce the early reversals" |
| `GAP_PER_TF` | 2.8 | bars per TF-minute | YES | "let's choose 2.8 until we get to the sweep" - PROVISIONAL |
| `SP_PICK` | lowest_pct | ? | YES | "start at the lowest TF and scan upwards ... the TF swing/pivot to pick should be the highest TF printing the lowest pct (between pivot and event)" - 1024 |
| `SP_BAND` | 0.0 | ? | YES | his near-same band. MEASURED: 53.6% of the 37,178 consecutive-pct gaps are EXACTLY 0 - TFs sharing a leg extremum - and p10 to p50 are all 0.0000 while p75 is 0.3705. So 0.0 already captures the clustering; widening to 0.5 cost 43.6% -> 28.8% within 0.25% of the pivot and bought only +1.397% -> +1.802% of leg. No knee - 1024 |
| `SP_CONTAIN` | 0 | ? | YES | OFF. Right on the 3 events it was proposed against, wrong on 5,323: 2,198 events lose EVERY candidate, the median candidate count falls 8.0 -> 1.0, and the median distance off the pivot goes 0.327% -> 1.157% with the worst 8.953% -> 26.146% - 1024 |
| `SP_XWOB` | 18 | ? | YES | "introduce a wob 18 and retest" - 1024. The only wob he named for this mech. It lifted the MFE-side rate on every TF |
| `SP_ALIGN_S` | 300 | ? | YES | "agreed on 300s" - 1024. UNREAD by the banked SP_PICK; it gates only the 'window' arm, kept as the comparison |
| `ARM2` | 1 | ? | YES | v4core's second arm, live. "add a second v4core arm" - 1024 |
| `ARM2_DWELL` | 18 | ? | YES | "min dwell 18 bars" - 1024. The ws1r oob run's own length, so the earliest arm is bar 18 of the run |
| `ARM2_POOL_MIN` | 2 | ? | YES | "any TWO of ws4-8r are same-side oob" - 1024 |
| `CORE_LIN_ENTRY_TF` | 4 | ? | YES | "maybe setting the entry TF to {knob:4,'V4_CORE_LIN_ENTRY_TF'} will settle it" - 1024, replacing his earlier "start from ws1" |
| `SAV_ARM_WALKBACK` | 30 | ? | YES | "at trade open, walkback in 5 minute jumps (cap: 30 minutes) to find the ws5r extrema. if the extrema is oob, the gate is closed and saviour may not fire" - 1024, with "full range" on the sampling |
| `LIN_W4` | 0 | ? | YES | arm A is the bank. The handover is arm B of the 1024 A/B and is NOT the machine until he rules it |
| `LIN_W4_GRACE_S` | 180 | ? | YES | "I propose we give 3 minutes grace to overcome the scenario" - 1024. UNANCHORED: the jump-back distribution has no knee, p75 is 0.3705 |
| `LIN_W4_G1_XWOB` | 4 | ? | YES | Joe 0911 "reversal:2, boundary:4. both are knobs" - the boundary one |
| `SP_TFS` | wide | ? | YES | THE ONE ITEM AWAITING HIS WORD. His 1024 list was SIX - ws3Mage, ws5Mage, ws10Mage, ws15Mage, ws20Mage, ws30Mage. ws1Mage and ws2Mage are MINE, and every measurement that justified banking used all eight, so the banked value is the one that was RUN. On his six alone the 18-row check scores 8 of 18 against 17 of 18. At ALIGN_S 300 ws1Mage and ws2Mage are the scale TF on 41.0% of events |
| `L2_MOM_MAXTF` | 30 | timeframe | YES | "v4mom_maxTF = 12" - 1025, the lineage2 fork |
| `L2_LIN_HOP` | 2 | timeframe hops | YES | "lin_hop = 2" - 1025. Applies BETWEEN cadences only, his ruling |
| `L2_T1_GRACE_S` | 120 | seconds | YES | "the 2 minutes (CAUSALLY) following" - 1025, confirmed a knob |
| `L2_T3_FRAC` | 0.75 | fraction of the oob HTF lines | YES | "L2_T3_FRAC 0.75 survives" - 1026. Of the rider's matryoshka lines that reached EX-FENCE since the arm, not oob: "requiring lines to be oob excludes the lines that reached only ex-fence before reversing" |
| `L2_T3_MIN_MATRY` | 2 | matryoshka lines that reversed | YES | "use the >=2 applied to the lines that actually reversed" - 1026. t3 needs max(2, round(L2_T3_FRAC x the ex-fence population)) |
| `L2_ARM_RETEST` | 1 | ? | YES | BANKED ON. v4-arm-lineage-retest, Joe 1026: "let's add a `v4-arm-lineage-retest` mech that will fire at arm". His nine rulings are in v4_lineage2.md; 0 is the A/B arm |
| `LIN2_BARRAGE_TOL_S` | 70 | ? | YES | MEASURED off his 2026-08-30 02:29 instance - the 02:27:50 cross to the 02:29:00 ws1r reversal. Not chosen, not swept |
| `LIN2_BARRAGE_LINES` | 6 | ? | YES | MEASURED off the same instance - ws3,4,8,6,7,1 inside those 70 s. With the tolerance it cuts 204 LOW crosses to 8 instances |
| `LIN2_BARRAGE_MIN_TF` | 9 | ? | YES | *** UNRULED AND EMPTY AT 9. *** His 1027 definition is "the minimum TF allowed to contribute", a floor applied BEFORE the line count. At 9 the pool is ws9..ws12 (four lines) and LIN2_BARRAGE_LINES 6 cannot be met, so the mech fires NOTHING. His 9 was ruled against a membership reading - a different mechanic. (min_tf, lines) must be ruled together |
| `LIN2_BARRAGE_MIN_TF_MODE` | membership | ? | YES | the arm the pine emit and the banked 24-cadence list were built on - one contributing line at or above MIN_TF, count over ws1..12. HIS choice 1028 ("B"). The "floor" arm is HIS definition but is EMPTY at MIN_TF 9 / LINES 6, so the pair must be ruled before it can be the default |
| `LIN2_PSEUDO_MIN_TF` | 99 | ? | YES | 99 = OFF. "bank this as the machine" - 1029 names the arm with the ex-fence latch ON and pseudo OUT. 4 is the other arm |
| `LIN2_REV_FENCE` | 40 | ? | YES | HIS value and HIS words 1028: a LOW reversal counts only below 40, a HIGH only above 60. "lock it in". A THIRD fence - not oob (15/85) and not ex-fence (20/80). THE SCOPE IS UNRULED: no consumer reads it yet |
| `LIN2_REV_FENCE_AT` | confirm | ? | YES | the value at the bar the turn becomes KNOWABLE on - the causal one. HIS ruling 1028 after both were measured. "turn" is the hindsight reading |
| `LIN2_BARRAGE_WIN_S` | 0 | ? | YES | the counting window is the ws1r reversal bar - the as-built behaviour, so nothing measured so far moves. His 1027 option A split it from the tolerance, which only ever meant to let ws1Mage and ws1r sync. THE VALUE IS UNRULED and comes off the sweep |
| `LIN2_BARRAGE_FIT` | off | ? | YES | neither of his two fits - a short pool fires nothing. THE BANKED ARM. lines = his "reduce the minimum required lines to fit them all inside the ws12cap"; cap = his "increase the ws12 cap to include the minimum required lines". The arm names are MINE |
| `LIN2_BARRAGE_FENCE` | any | ? | YES | no fence test on a contributing reversal - the banked behaviour and what every measurement so far used. in/ex are the sweep arms for his 1027 "sweep reversing infence vs reversing exfence". The knob name and the arm names are MINE |
| `LIN2_BARRAGE_ON` | 1 | ? | YES | BANKED ON, Joe 1027: "bank the barrage results and wire the mech into the chain". It fires as a CADENCE and that cadence EXHAUSTS - his "both - a cadence keeps the walk's transactions uniform, and exhaust will fire". 0 is the A/B arm |
| `LIN2_MISMATCH_ACTION` | rev-trade | ? | YES | "make this a knob: rev-trade, or, close only (so that reentry creates the next open)" - 1027, narrowed the same day to the cws1b counter-oob cadence ONLY. close-only stops the chain until v4_reentry is wired, task 31 |
| `LIN2_MAE_CAP` | 1.1 | ? | YES | "if MAE > 1.1, cap mae at 1.1 and print 0 in mfe" - 1027. A stop-loss model in the REPORT only; it moves no decision |
| `LIN2_CAND_NOT_REVERSED` | 0 | ? | YES | OFF is the bank. 1 = no reversal since the rider took the baton, 2 = none since the arm. His 1027 "can we test it on the day?" - the test arms, not a banked change. The wob is LIN2_REV_WOB 12, which is MINE |
| `LIN2_CASCADE_NO_ACTION` | 0 | ? | YES | BANKED OFF 1031 - "completely disable the mage cascade", after it was shown owning 123 of 143 leg exits at -17.8102 summed and ending all 5 of the 0659 variants at their first cadence. The verdict is still PRINTED as data. WAS (1, his word 1027 - "bank it, and make the current machine default". "if its verdict matches the trade direction then take no action (ie keep walking)" - 1027. up = LONG, down = SHORT, his "1, confirmed". neither is NOT suppressed - "let the cadence decide" |
| `LIN2_CROSS_WOB` | 12 | ? | YES | "add the wob12 to all crosses to ib and crosses to in-mom-fnc" - 1027. Five sites: t1, t2, the retest gate, and both pass-bar rules. Supersedes L2_CWS1R_WOB 1 on the retest cross and the "xwob 1" header ruling. Crosses INTO oob or ex-fence still carry no dwell |
| `LIN2_COUNTER_OOB_ON` | 0 | ? | YES | BANKED OFF 1030 - "drop the opposing oob side forced exit". Its replacement is UNRULED, his own words. WAS (1, "create a cadence when cws1b crosses to counter target-side oob (eg 08-30 1921)" - 1026, "go" - 1027. Raw cross bar, no wob. 69 firings arm..exhaust over 08-30..09-03 |
| `LIN2_CAD_LATCH_ON` | 1 | ? | YES | BANKED ON. the 2-staged latch, Joe 1026: "I see a potential replacement for t3, and it's 2-staged latch" |
| `LIN2_CHAIN_OPEN_ON` | 1 | on/off | YES | HIS MECH - "the chain open should be on the ws5Mage oob" - 1029. ON: "should be" is a ruling. OFF keeps the handed-in first side |
| `LIN2_CHAIN_OPEN_TF` | 5 | TF | YES | HIS LINE - ws5Mage - 1029 |
| `LIN2_CHAIN_OPEN_LOOKBACK_S` | 300 | seconds | YES | HIS VALUE - "has been oob in the last 5 minutes" - 1029 |
| `LIN2_CHAIN_OPEN_XWOB` | 1 | bars | YES | MINE. The RAW ws1b cross. His "wob12 to all crosses" (1027) points at 12; raw is 0.8 min from his "2353" against 1.8 |
| `LIN2_CHAIN_OPEN_LINES` | 2 | lines | YES | HIS VALUE - "at least 2 higher TFs must be printing LOWER values" - 1029. The band ws6..ws12 is mine |
| `LIN2_BARRAGE_MAX_TF` | 15 | TF | YES | HIS VALUE - "barrage maxTF needs to increase, knob:15" - 1029. Barrage-only; L2_MOM_MAXTF stays 12. Sweep range [12-22] is his |
| `LIN2_B1_HOLD` | 0 | bars | YES | HIS MECH - "if ws1b to ib has not qualified its wob 12, then its value is not passed in" - 1029. OFF until measured. At 12 it holds his 2026-08-30 00:59:25..01:20:45 low excursion together as one event |
| `LIN2_LATCH_EXFNC_ON` | 0 | on/off | YES | BANKED OFF 1101: "disable the latch.  I introduced it get around emerging". The chart-matched ex-fence read replaces it. WAS (1, HIS MECH, HIS KNOB NAME AND HIS BANK - "ADD LIN2_LATCH_EXFNC_ON" then "bank this as the machine", 1029) |
| `LIN2_CP_EXFNC` | closed_prev | ? | YES | BANKED 1101: "we will use closed_prev only for exiting fences". "emerging" is the pre-1101 arm |
| `LIN2_CP_OOB` | emerging | ? | YES | BANKED at today's read 1101. He put oob in neither category and said "build for both options", so the bank moves no verdict and "closed_prev" is the arm |
| `LIN2_CP_IB` | emerging | ? | YES | BANKED 1101 on his gut - "my gut says emerging: create a knob that tests both options". "closed_prev" is the arm |
| `FDM_RE_IB_XWOB` | 1 | ? | YES | the ib cross hold that closes the re-entry window. 1 is the cross bar itself, the same hold the cadence event uses on ws1b |
| `FDM_RE_B_FNC` | 5.0 | ? | YES | gcws30b's own fence, 5 -> (5, 95), the smaller end per his 1103 convention. WAS 95.0 |
| `FDM_RE_WIN_OPEN` | ws1b | ? | YES | HIS 1105 PURGE of the gcws30b clause: "purge '--gcws30b is past the 5/95 fence, on either side' from the reentry spec". WAS 'both', banked 1103 on his "let's bank E, and make it the machine" - that arm opened where ws1b was oob AND gcws30b ex-5/95, and the 28-run sweep had it the only arm positive on 08-03 at +0.152% and tied best on 09-15 at +14.325%. The other settings are gcws30b, both, first and sameside |
| `FDM_RE_WIN_CLOSE` | ws1b | ? | YES | HIS 1103 "close the window on ws1b to ib". "gcws30b" is the arm it replaced |
| `FDM_RE_REV_READ` | closed_prev | ? | YES | BANKED 1104 - his "-use closed-prev" for the ws5 and ws6 reversals, overriding the standing rule that lift-off is the one emerging read. "emerging" is the arm it replaced |
| `FDM_RE_WS5_FNC` | 20.0 | ? | YES | BANKED 1104 - his "if ws5r reverses while ex-20/80-fence". The smaller end of the pair, and its own knob so a sweep cannot move step 1's fence |
| `FDM_RE_WS6_GATE` | ex2080 | ? | YES | BANKED 1104 - his "the ws6r gate might need to move from oob to ex-20/80-fence", then "that looks like our reentry mech". "oob" is the arm it replaced. The one cluster that moved: 2026-09-15 18:17, from -5.470% to -0.824% |
| `FDM_RE_CLIMB` | off | ? | YES | BANKED OFF - his 1104 probe "ride upwards through the TFs until you reach a tf showing the in fence r line". "value" reads each rung at one bar; "reversal" makes each ex-fence rung print its own reversal first |
| `FDM_RE_CLIMB_HI` | 12 | ? | YES | the climb's ceiling, wsf's own top |
| `FDM_RE_REV_TF` | 4 | ? | YES | HIS 1105 "set FDM_RE_REV_TF 4". WAS 5, from his 1104 "walk until ws5 reverses". The walk's first target is now ws4r and his support gate reads ws4Mage |
| `FDM_RE_GATE_TF` | 6 | ? | YES | the line that gates the wait. His spec is ws6 |
| `FDM_RE_SCAN_FLOOR` | gate | ? | YES | where the scan band starts: "gate" is the TF above the gate line, the mech's own shape; "ws13" is his "scan higher than ws12" read literally |
| `FDM_RE_SCAN_LO` | 7 | ? | YES | the scan band's floor when FDM_RE_SCAN_FLOOR is a fixed TF rather than the gate + 1 |
| `FDM_RE_SCAN_HI` | 12 | ? | YES | the scan band's ceiling. wsf is ws1-ws12, his 1017 band names |
| `FDM_RE_FIRE_IB` | 1 | ? | YES | BANKED 1104 - ws1b's ib close is in the last-to-fire set, his "out of ws5r reversing or ws6r reversal or ws1b crossing to ib". 0 drops it |
| `FDM_FNC_2080` | 20.0 | ? | YES | HIS OWN KNOB NAME, "fdm-20-80-fnc", at his own value. Both the step-1 test and the reversal population read it; "ex" includes oob |
| `FDM_M3_FNC` | 25.0 | ? | YES | HIS 1103 "ws3Mage is settled on 25/75". The knob name is mine; the value is his |
| `FDM_M3_RESCUE_ON` | 1 | ? | YES | HIS 1103 MECH UPDATE - a cadence gated on ws3Mage staying infence is rescued when ws3r went oob and ws3Mage reached ex-40/60 in the gcws30b-to-ws1b window |
| `FDM_M3_RESCUE_FNC` | 40.0 | ? | YES | HIS 1103 "IF ws3Mage was ex-40/60-fence during the window". Wider than the 25/75 it rescues |
| `FDM_POP_LO` | 3 | ? | YES | HIS 1103 "ws3 to ws30 for both the cadence and the ws10x-cadence". The top comes from L2_MOM_MAXTF 30, not from a second knob |
| `FDM_STEP1_ABOVE_TF` | 3 | ? | YES | HIS 1103 "above in timeframe" - step 1 scans ws4..ws30. STRICTLY above, so this knob is the excluded rung, not the floor |
| `FDM_X10_WOB` | 24 | ? | YES | HIS 1103 RULING "now that we have the grade period, we can leverage a smaller wob: use 24". 36 is the other arm, from his own 1841 example |
| `FDM_X10_FRM` | cross | ? | YES | RULED 1103 - he read it marked #MINE in the as-built spec and said "your #MINE lines are all good". "confirm" is the arm |
| `FDM_REV_FROM` | event | ? | YES | HIS 1103 2-POLE ASK. "event" is the bank because every number so far was measured on it; "window" starts at the cadence event's ws1b excursion open and is unmeasured |
| `FDM_X10_GRACE_PCT` | 40.0 | ? | YES | HIS OWN KNOB NAME, "fdm-ws10x-cad-grace", at his own value |
| `FDM_X10_TRADE_PCT` | 50.0 | ? | YES | HIS VALUE ">=50%". The knob is mine - a stated threshold with no knob cannot be moved without an edit |
| `FDM_X10_GRACE_MIN` | 5.0 | ? | YES | HIS VALUE "we add a 5 minute walk". The knob is mine. 5.0 min = 60 bars at the 5 s grid |
| `FDM_MAE_CAP` | 1.1 | ? | YES | HIS 1103 "add the typical mae1.1 stop" + "yes, move it to default". ALWAYS ON, unlike LIN2_MAE_CAP which stayed behind W_MAE_CAP=on |
| `FDM_RE_REV_MECH` | cp | ? | YES | HIS 1105 "because we are using closed-prev, the wob can be cut for the closed-prev reversals". Measured 35 s earlier than the lift-off on every 2026-08-07 ws4 reversal, and 4 to 7 times as many firings. "liftoff" is the arm it replaced |
| `FDM_RE_M4_ON` | 1 | ? | YES | ON, his 1105 support gate. At 0 the trigger line fires with no Mage support test |
| `FDM_RE_M4_FNC` | 23.0 | ? | YES | HIS VALUE "sameside ex-23/77-fence". The knob holds the smaller end, his convention |
| `FDM_RE_M4_AT` | extremum | ? | YES | HIS 1105 "ws4Mage is tested at the ws4r extremum, eg highside 0430, 0512, 0600". "reversal" reads the stamp bar. The extremum SPAN and the SERIES are my call, stated in the knob note |
| `FDM_RE_XCROSS_ON` | 1 | ? | YES | ON, his 1104 "let's make a small mod to the reentry". At 0 the re-entry walk is the 1104 banked one and every number before this mod is reproduced |
| `FDM_RE_XWOB` | 12 | ? | YES | HIS VALUE "wob 12" = 60 s. Held apart from LIN2_CROSS_WOB 12, a different mechanic |
| `FDM_RE_XCROSS_LO` | 4 | ? | YES | HIS 1105 "make ws4 the lowest TF". It is NOT tied to the trigger line - that floor was mine and it hid the ws4x cross at 2026-08-07 05:44:20 which is the only one in that stretch to pass all three of his gates |
| `FDM_RE_XCROSS_TFS` | band | ? | YES | HIS 1105 "I intentionally referd to `a TF`, so that you would see the dynamic nature of the mod" - every line from FDM_RE_REV_TF up to FDM_RE_SCAN_HI. WAS 'both', two fixed waiting points. THE KNOB NAME AND THE BAND'S TOP ARE MINE |
| `FDM_RE_XCROSS_FNC_AT` | stretch | ? | YES | HIS 1105 "there was no such ws4r is not past the 20 fence gate on the ws{a TF}x cross" - the fence is the state the line is in while waiting, read across the stretch from the window open to the cross. "cross" is the arm I had wrongly built |
| `FDM_RE_XCROSS_UP_READ` | closed_prev | ? | YES | his own example number "ws6r is 43" is the closed-prev value; emerging reads 40.79 there. THE READ IS MY CALL |
| `FDM_CONF_READ` | closed_prev | ? | YES | BANKED 1104 - his "make sure that closed-prev is the standard for everything except lift-off", the LATER of his two rulings for this table. "emerging" is the arm it replaced |
| `FDM_CONF_BARS` | event+x10 | ? | YES | BANKED 1104 - the two data bars the machine owns, the cadence event and that event's ws10x race confirm. "event" is the narrower arm. THE KNOB NAME IS MINE |
| `FDM_EXF_EM_BARS` | 12 | ? | YES | HIS 1105 "taking the values based on the highest/lowest emerging bar between the seams". 12 bars = 60 s, one minute, ending AT the read bar. At 1 it is the single bar's value, the read it replaced |
| `FDM_EXF_READ` | either | ? | YES | HIS 1105 "collect the closed-prev and the emerging value for each line. if either qualify then walk to the next cadence". Driven by 2026-08-07 08:51:00, where closed-prev had 0 lines past 80 and his chart showed ws4 oob. Routes the cadence side only; the re-entry scan keeps FDM_RE_REV_READ. THAT BOUNDARY IS MINE |
| `FDM_XCAD_ON` | 1 | ? | YES | ON, HIS 1104 "apply the update to the code so that ws10 does not interfere with the intention of the spec". At 0 the race pins ws10 and every banked fdm2 number is reproduced |
| `FDM_XCAD_C2_SCOPE` | tagged | ? | YES | HIS WORD "tagged" in the second clause. "board" tests every ex-20/80 line at the test bar instead. The report prints both verdicts; THE KNOB IS MINE |
| `FDM_XCAD_RULE` | A | ? | YES | HIS 1105 ruling after reading the 2026-08-07 02:20:00 event. WAS 'B' from his 1104 "use B for now, we can change it to A if the data doesn't match my eye's verdict". At B that event found no candidate and the leg stopped at -1.100; at A it picks ws20r and the leg closes 02:23:15 |
| `FDM_XCAD_ABOVE` | 2 | ? | YES | HIS OWN COUNT from the confluence rule, "the 2 lines above the highest TF". At 3 his 16:11:00 example produces no candidate |
| `FDM_XCAD_EXF` | 0 | ? | YES | HIS 1104 "no" - the candidate line does not have to be ex-20/80 itself |
| `FDM_XCAD_FRM` | confirm | ? | YES | HIS 1104 "the conf bar". "cross" is the arm, 1 min 55 s earlier at his own example |
| `FDM_XCAD_TAG_AT` | event | ? | YES | HIS 1104 "tagged at the cadence event bar" |
| `FDM_XCAD_REV_FROM` | window | ? | YES | HIS 1104 "the target-side reversal must fire between the opening of the cadence window and the confirmed x-cross bar". It gates the reversal only; the extremum keeps the trade open as its anchor, and THAT reading is mine |
| `FDM_XCAD_REV_TO` | read | ? | YES | HIS 1104 CORRECTION "the window's end can't be the confirmed x-cross - that would mean the grace period has zero value". At "confirm" the turn count is frozen for the whole walk |
| `FDM_XCAD_SEAM_S` | 15.0 | ? | YES | HIS VALUE "the next ws1 seam+15s". 15 s = 3 bars |
| `FDM_XCAD_WALK_MIN` | 10.0 | ? | YES | HIS VALUE "walk forward 10 minutes". The shape is the grace walk he called "the established walk" - re-test every 5 s bar, break on the first pass |
| `FDM_XCAD_FALLBACK` | exfnc | ? | YES | HIS 1105 "scan the entire range for ex-20/80-fence lines instead. if any are found, the cadence verdict is keep on walking". "off" is the arm it replaced, where no candidate went straight to FDM_XCAD_NONE |
| `FDM_XCAD_NONE` | rev-trade | ? | YES | HIS 1104 "no candidates = rev-trade", validated against v4_fdm2.walk which already rev-trades when step 1 counts 0 |
| `FDM2_BLAST_SCAN_HI` | 12 | TF | YES | HIS 1105 VALUE "ws12" for the away run's top rung. The knob NAME is mine; 12 is wsf's ceiling, the same number FDM_RE_SCAN_HI carries |
| `FDM2_MATR_LFTOF_CONF` | 10 | TF | YES | HIS OWN KNOB NAME AND VALUE, 1105 - "the samples should only be captured for ws{{<={knob:10,`FDM2_MATR_LFTOF_CONF`}}r". It caps the flattening SAMPLE CAPTURE, not the away run |
| `FDM2_CAD_FLATIN_WIDTH` | 3 | TF | YES | HIS OWN KNOB NAME AND VALUE, 1105 - "they should be in sync. let's use ws{knob:3,'FDM2_CAD_FLATIN_WIDTH}". Every line's flattening reads ws3's lattice: gap 8 bars, span 40 bars = 200 s |
| `FDM2_CAD_FLATIN_TOL` | 8 | bars | YES | HIS VALUE 40 s, 1105, label mine - "make it a knob - your call on the label". How far apart the flattening starts may be and still read as his "~same wallclock". 8 bars = 40 s, which is both one sample step on ws3's lattice and LIFT_WOB 8 |
| `FDM_SAV_ON` | 0 | ? | YES | OFF, HIS 1103 "we're dropping saviour for now". It was wired and measured: 2026-08-03 -1.051% -> -3.103% net, 2026-09-15 +7.316% -> -15.040% |
| `FDM_SAV_READ` | emerging | ? | YES | HIS 1103 "use emerging values, at the emerging ws1Mage extermum". "chart" is the other arm |
| `FDM_SAV_TF_HI` | 3 | ? | YES | HIS 1103 "reduce the cascade to ws1-3". fdm2's own knob, not SAV_CASCADE_TF_HI, so the live machine keeps 12 |
| `FDM_SAV_MIN` | 3 | ? | YES | HIS 1103 "SAV_CASCADE_MIN 4 -> 3" - the arm that fired branch B at 2026-09-15 14:04:05. fdm2's own knob; SAV_CASCADE_MIN stays 4 for the live machine |
| `FDM_SAV_ZOOM` | 2 | ? | YES | UNCHANGED FROM THE SHARED VALUE but held separately. Measured: at zoom 1 the 1356 LONG stays open at either min, because the ws2->ws3 step +1.6574 breaks the low cluster |
| `FDM_SAV_ARM` | 0 | ? | YES | HIS 1103 "remove the armed gate". At 0 the ws5r walkback is skipped and ws5r is not read |
| `LIN2_CP_LIFT` | closed_prev | ? | YES | BANKED 1101 - "lift-off needs a close-p mode - it only reacts to full 1 minute bars". The t1 ws1r reversal BARS; it REVISES his earlier "keeping the lift-off on emerging" and gives up the 0445 reversals. _rev_pairs is not routed |
| `LIN2_CP_WS1R` | closed_prev | ? | YES | BANKED 1101 - "change ws1r to closed-p". The t1 r gate's VALUE read only; the reversal BARS stay emerging |
| `LIN2_CP_GCWS30B` | closed_prev | ? | YES | BANKED 1101 on his "yes" to routing gcws30b. It moves the t1 cadence AND the arm race - both read CL['g30b']. "emerging" is the other arm |
| `LIN2_CP_MIN_TF` | 1 | ? | YES | HIS RULE 1101, AS HE LEFT IT: "change ws1r to closed-p" moved the floor from 2 to 1, reversing the ws1 half of "ws1{any} and gcws1{any} stay on emerging". WAS (2, HIS RULE 1101: "ws1{any} and gcws1{any} stay on emerging (otherwise we lose the 09-03 0326 arm). all else is closed-prev". At 2 every ws1 line is exempt. THE gcws HALF IS A READING OF MINE - no gcws1 line exists, so no sub-wsf line is routed at all |
| `LIN2_LATCH_OOB_ON` | 0 | on/off | YES | OFF, the banked arm. His 1029 ask to A/B it: "do a 08-30 chain AB test to validate or drop the oob latch". One latch read at depth, never a second latch |
| `LIN2_CASC_REV_GATE_ON` | 0 | ? | YES | OFF is the bank - his 1030 mech, measured before it can be the default. The knob name is mine; he has not named the mech |
| `LIN2_CASC_REV_GATE_HI` | 4 | ? | YES | his "ws1-4r". The knob name is mine, the floor is ws1 |
| `LIN2_MATRY_WSF_TAKEOVER_ON` | 0 | ? | YES | OFF is the bank - his 1030 mech, measured before it can be the default. The _ON suffix is mine |
| `LIN2_MATRY_WSF_TAKEOVER_TF` | 7 | ? | YES | HIS knob name and HIS value, written into his own spec line as {knob:7} |
| `LIN2_MATRY_WSF_TAKEOVER_AT` | event | ? | YES | the cadence bar. "extremum" reads the ws1Mage extremum instead - his "test both" and NEITHER is ruled |
| `LIN2_MATRY_WSF_SCAN_HI` | 4 | ? | YES | his "a scan from ws1 to ws4". The knob name is mine |
| `LIN2_B1_OOB_DWELL` | 0 | ? | YES | the plain per-bar read - the bank, so nothing measured so far moves. His 1030 value is 12 bars = 60 s, after the 2026-08-30 22:22 trace showed cws1b entering the LOW oob four times in 85 s. Read by t1, t2, the arm and the counter-oob cadence, all through b1_beyond |
| `LIN2_EXFNC_LATCH_REL` | lift | ? | YES | the latched line's own lift-off and nothing else - his 1031 revision of the 1029 release line. WAS 'bank' at the barrage plus the opposite-side clear, which is now the 'barrage' arm and carries every pre-1031 latch figure. THE KNOB NAME IS MINE, the mech is his, and three choices inside the arm are mine and unruled - see the declaration |
| `LIN2_EXFNC_LATCH_WOB` | 4 | bars | YES | HIS NAME AND HIS VALUE - "a small {knob:4,'LIN2_EXFNC_LATCH_WOB'} WOB" - 1029. Bars is mine |
| `LIN2_T3_MIN_TF` | 5 | ? | YES | HIS NAME, HIS VALUE - "the rider between ws{knob:5,'lin2_t3_min_tf'} and ws12" |
| `LIN2_CAD_LATCH_LIFE_S` | 600 | ? | YES | "10 minutes (knob)" - 1026. How long latch 1 stays latched. Seconds. The value is his; the knob name is mine |
| `LIN2_SUPPORT_LINES` | 3 | ? | YES | "3 lines below the rider" - 1026. ALL of them must have reversed; his own reading named ws4, ws5, ws6 under a ws7 rider |
| `LIN2_DIV_ON` | 0 | ? | YES | OFF, AND HIS 1101 WORD IS "divergence can be completely disabled". ws1r is the wrong line for the test - "ws1 works in small cycles that are not profitable" - and "ws3r seems to have more divergence potential (eyeballed)". ws3r is unbuilt. HIS knob name. At 0 the divergence runs only at the arm |
| `LIN2_DIV_AT` | cadence | ? | YES | the cadence bar itself, the pre-1101 behaviour. "extremum" anchors on the target-side ws1Mage extremum - his 1101 proposal. NEITHER arm is ruled; the knob name is mine |
| `LIN2_DIV_PM_FLOOR` | 0.0 | ? | YES | PM DISABLED - "it needs a floor that I don't have yet". HIS knob name. Declared and read by nothing, on purpose |
| `LIN2_T1_B_IB_DWELL` | 12 | ? | YES | HIS 1101 ADDITION - "add a 1 minute minimum dwell on gcws30b ib" = 12 bars = 60 s. ADDITIVE to the wob 6. THE SIDE IS HIS WORD "ib" READ LITERALLY; a beyond-side minimum would be LIN2_B1_OOB_DWELL and would delete the 05:19:25 cadence rather than move it |
| `LIN2_T1_B_FNC` | 95.0 | ? | YES | HIS 1101 SPEC REVISION - "I omitted the 5/95 requirement for gcws30b". t1's b read was oob 15/85 before this. At the ws1b arm it wants 85.0 |
| `LIN2_T1_B_LINE` | gcws30b | ? | YES | HIS line, 1031 - ws1b is replaced by gcws30b. "ws1b" is the pre-1031 arm. The knob name is mine |
| `LIN2_T1_B_WOB` | 6 | ? | YES | HIS value - wob 6. Replaces LIN2_CROSS_WOB 12 for t1's b-line cross only; every other cross to ib keeps 12 |
| `LIN2_T1_R_FNC` | 56.0 | ? | YES | HIS value and his own {knob:56} notation - the r reversal gate's fence, mirrored to (44.0, 56.0), replacing the side-of-50 test |
| `LIN2_T1_GRACE_AT` | cross | ? | YES | the pre-1031 behaviour. He asked for an on/off knob and the diff, so NEITHER arm is ruled |
| `LIN2_ARM_B_LINE` | gcws30b | ? | YES | HIS line, 1031 - gcws30b ex-5/95-fence replaces ws1b oob in arm_race condition 2 |
| `LIN2_ARM_B_FNC` | 95.0 | ? | YES | HIS value - a 95/5 fence, mirrored to (5.0, 95.0), "at or beyond" his word |
| `LIN2_ARM_B_WOB` | 6 | ? | YES | HIS value - the to-oob cross, the to-ib cross, and the dwell beyond the 5/95 fence |
| `LIN2_ARM_WS3R_ON` | 0 | ? | YES | OFF - he bracketed ws3r in question marks, then said he is not convinced. ws2r is IN unconditionally |
| `LIN2_BOARD_HOLD` | linhop_exfnc | ? | YES | BANKED at his 1101 third arm - "if a line that is inside of lin-hop's reach is ex-fence, then walk to the next cadence". The arms are off, board_oob, board_oob_rev and linhop_exfnc; the names are mine, the four rules are his |
| `LIN2_BOARD_OOB_HOLD` | 1 | ? | YES | HIS RULE 1101 - "the oob rule doesn't apply to a rider - it's a blanket rule across the board". No exhaust while any ws1..L2_MOM_MAXTF r is oob on the target side; the walk holds to the next cadence |
| `LIN2_TOP_RESET_ON` | 1 | ? | YES | BANKED ON 1031 after the truncation test passed on the 08-14 0659 walk. His "new trick"; the knob name is mine and the mech is unnamed. No limit on repeats, his own "yes" |
| `LIN2_RELATCH_ON` | 1 | ? | YES | BANKED ON 1031 - his re-latch, with his candidate rule and his fall-back test both kept. The _ON suffix and the knob name are mine |
| `LIN2_RIDER_JUMP` | 8 | ? | YES | HIS value and HIS mech, BANKED 1031 - "a riderTF can advance no more than 8 TFs" at a cadence marker, from a rider of 0 at the arm. It bounds the rider scan AND the cadence candidate scan. The name is mine |
| `LIN2_CAD_TYPES` | t1 | ? | YES | no filter - every cadence the mechs produce is reviewed. His 1031 "test only at the t1 cadences" is a test arm, not a bank move. The knob name and the type strings are mine |
| `LIN2_PASS` | ib | ? | YES | the bank - _pass_bars' two rules. His 1031 asks for 'reversal' and 'reversal+quarter' as tables, not as a bank move |
| `LIN2_PASS_QUARTER` | 0.25 | ? | YES | HIS value, from his ws22 worked example. The knob name is mine. Only read when LIN2_PASS is 'reversal+quarter' |
| `LIN2_REV_WOB` | 12 | ? | YES | "static wob12. noted, we'll keep the static" - 1026. THIS MECH ONLY; LIFT_WOB 8 is untouched. A seam-aligned dynamic wob kept ~25% fewer reversals and was slower on every one, measured 08-30..09-03 |
| `L2_T3_ON` | 0 | ? | YES | BANKED OFF 1026 - "the old t3 is defunct". 1 is the A/B arm; 0 is the experiment arm he asked for on 1026 after its 24 events scored - 11 of the 24 fired with the rider already at cws12, where no pass is possible |
| `L2_GATE_MODE` | closed | ? | YES | "move everything except reversal detection to closed bars" - 1026 FINAL. t3cadence's oob population gate |
| `L2_CWS1R_WOB` | 1 | bars | YES | "a lineage2-only wob 1 for cws1r" - 1026. On the closed line the wob suppresses 3.0% against the emerging line's 69.4%, and the value is unchanged across the whole hold on 99.2% of lift-offs |
| `L2_RE_IB_MIN` | 2 | Mage rungs that stayed IB | YES | "it should be 2 or more TFs that were ib while ws5Mage was oob" - 1026. He asks whether 2 is too loose; the sweep-pivot scoring of the signals it produces is the measurement he called for |
