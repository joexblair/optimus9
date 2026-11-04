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
