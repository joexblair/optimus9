# the 1104 overnight sweep status, appended per watchdog wake

| UTC | what |
|---|---|
| 2026-11-04 06:28:22 | the 3 x 94-day grids launched; knobs grid at config 17 of 48; watchdog every 27 min |
| 2026-11-04 06:34:02 | the arm re-print is wired: fdm2_arms.py runs per finished grid into sweep_1104_arms.md |
| 2026-11-04 06:57:44 | the 94-day settings grid finished: config 0 nets -195.721% on 898 legs, 19 of 94 days above zero, gross per leg -0.0205% against the 0.1975% round trip. Arm table appended. The r-trip grid is at config 8 of 27. |
| 2026-11-04 07:11:05 | he went offline; handover written to sweep_1104_handover.md |
| 2026-11-04 07:20:21 | r-trip and ws1b-multiplier grids finished, arm tables appended, both deeply negative on 94 days. Patches applied with no default move (08-03 still 15 legs / -3.940). Stage 7 tfpair (112 configs) and the coverage grid (103 rungs) launched over 94 days. |
| 2026-11-04 07:24:21 | tfpair at config 5 of 112, 85 min projected; the coverage grid queued behind it. Nothing to relaunch. |
| 2026-11-04 07:43:20 | tfpair running, no change to report |
| 2026-11-04 07:57:58 | tfpair running, no change to report |
| 2026-11-04 08:05:17 | tfpair running, no change to report |
| 2026-11-04 08:25:28 | tfpair finished, control holds. Best gross per leg: pair (8,9) scan to ws12 on the live read at +0.1193%, and pair (7,8) chart-matched at +0.1138% - both still under the 0.1975% round trip, best net -60.853%. Pair (7,8) and (8,9) beat (5,6) on the 4 random days by +195.753 and +84.825 against -13.677. Coverage grid at config 20 of 97. |
| 2026-11-04 08:42:03 | coverage grid running, nothing to relaunch |
| 2026-11-04 08:55:23 | coverage grid running, nothing to relaunch |
| 2026-11-04 09:08:09 | coverage grid at config 85 of 97, ~8 min left; climb patch queued for the idle gap |
| 2026-11-04 09:18:50 | coverage grid finished, 97 rungs over 24 knobs, control holds. Its own report is sweep_1104_curve_report.md (fdm2_arms.py cuts a cross grid, not a curve). Best single rung by gross per leg: the stop at 3.0% = +0.0412%, still a fifth of the round trip. Climb grid launched, 108 configs. |
| 2026-11-04 09:24:55 | climb grid running |
| 2026-11-04 09:41:58 | climb grid running |
| 2026-11-04 09:55:15 | climb grid running |
| 2026-11-04 10:07:56 | climb grid running |
| 2026-11-04 10:24:56 | climb grid running |
| 2026-11-04 10:41:55 | climb grid running |
| 2026-11-04 10:55:18 | climb grid running |
| 2026-11-04 11:07:55 | climb grid running |
| 2026-11-04 11:24:56 | climb grid running |
| 2026-11-04 11:41:55 | climb grid running |
| 2026-11-04 11:55:22 | climb grid running |
| 2026-11-04 12:07:56 | climb grid running |
| 2026-11-04 12:25:00 | climb grid running |
| 2026-11-04 12:41:55 | climb grid running |
| 2026-11-04 12:55:23 | climb grid running |
| 2026-11-04 13:08:11 | climb grid running |
| 2026-11-04 13:24:56 | climb grid running |
| 2026-11-04 13:41:55 | climb grid running |
| 2026-11-04 13:55:24 | climb grid running |
| 2026-11-04 14:08:11 | climb grid running |
| 2026-11-04 14:25:00 | climb at config 106 of 108, ~6 min left |
| 2026-11-04 14:32:44 | climb grid finished, control holds. Best per-leg gross of the night: the reversal climb from ws8, ceiling ws12, rung gate at 20/80, live read = +0.1262% over 883 legs, net -62.972%. The climb beats the fixed pair by a hair (+0.1193%). Stages 8 and 9 refused on my env override - the read is now a grid slot and both relaunched. |
| 2026-11-04 14:42:15 | stages 8 and 9 running as grids |
| 2026-11-04 14:55:26 | stage 8 running |
| 2026-11-04 15:07:57 | stage 8 running |
| 2026-11-04 15:24:56 | stage 8 running |
| 2026-11-04 15:37:30 | stages 8 and 9 done, control holds on both. Night summary: 437 configs over 94 days, 0 reached the 0.1975% round trip and 0 netted positive. Best is +0.1262% gross per leg. The one lever is the start line, ws8 over ws5. Stage 12 (start line ws5..ws12) launched. |
| 2026-11-04 15:41:54 | stage 12 start-line curve running |
| 2026-11-04 15:55:23 | stage 12 start-line curve at config 3 of 16 |
| 2026-11-04 16:07:57 | stage 12 running |
| 2026-11-04 16:25:02 | stage 12 running |
| 2026-11-04 16:29:38 | stage 12 done, control holds. The start-line curve is bumpy, not a trend: ws7 peaks at +0.1138% gross per leg on the chart-matched read while ws8 falls to +0.0287%. The band ws6..ws9 beats ws5; the rung inside it is unstable across grids. Queue empty. |
| 2026-11-04 16:42:07 | queue empty, all stages done. Isolated the re-entry openings over 94 days: 737 distinct opens, 502 with MFE beating MAE, 64.6% of the leg MFE captured - the opening is not the weak stage. |
| 2026-11-04 16:55:52 | queue empty. Added a realised-at-leg-close reporting column to the trace arm and running it over the whole tape: what the openings make with no rev-trade and no stop, against the 0.1975% round trip. |
| 2026-11-04 16:56:43 | THE RESULT: the same 737 openings held to their own sweep-pivot leg close realise +0.6059% per open with 456 of 737 clearing the 0.1975% round trip, against the machine -0.0205% per leg. The leg close is a hindsight read so it is a CEILING, not a tradeable number. The exit is where it is lost. |
