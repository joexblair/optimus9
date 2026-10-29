# HIS ws1b FIRING MECH - EVERY READ ON EMERGING, against the closed_prev version
# SPAN 2026-08-29 23:00:00 .. 2026-08-30 00:30:00 | RULED_OK True
# the band is ws6..ws12. required lines 2. the oob lookback is 300 s.
# the anchor extremum is taken over [run start, FIRING BAR] - never past it.

## every ws1b oob->ib cross, per arm

| arm | the raw cross | the firing bar | candidate side | ws5Mage oob gate | the anchor bar | ws5Mage at the anchor | lines away | FIRES? | side |
|---|---|---|---|---|---|---|---|---|---|
| EMERGING, raw cross | 2026-08-29 23:13:20 | 2026-08-29 23:13:20 | LOW | no | - | - | 0 - none | no | - |
| EMERGING, raw cross | 2026-08-29 23:16:05 | 2026-08-29 23:16:05 | LOW | no | - | - | 0 - none | no | - |
| EMERGING, raw cross | 2026-08-29 23:19:40 | 2026-08-29 23:19:40 | LOW | no | - | - | 0 - none | no | - |
| EMERGING, raw cross | 2026-08-29 23:27:10 | 2026-08-29 23:27:10 | LOW | no | - | - | 0 - none | no | - |
| EMERGING, raw cross | 2026-08-29 23:53:50 | 2026-08-29 23:53:50 | HIGH | YES | 2026-08-29 23:52:10 | 89.64 | 7 - ws6,ws7,ws8,ws9,ws10,ws11,ws12 | YES | SHORT |
| EMERGING, raw cross | 2026-08-29 23:56:00 | 2026-08-29 23:56:00 | HIGH | YES | 2026-08-29 23:52:10 | 89.64 | 7 - ws6,ws7,ws8,ws9,ws10,ws11,ws12 | YES | SHORT |
| EMERGING, raw cross | 2026-08-30 00:17:15 | 2026-08-30 00:17:15 | HIGH | YES | 2026-08-30 00:17:10 | 86.48 | 7 - ws6,ws7,ws8,ws9,ws10,ws11,ws12 | YES | SHORT |
| EMERGING, raw cross | 2026-08-30 00:18:40 | 2026-08-30 00:18:40 | HIGH | YES | 2026-08-30 00:18:20 | 108.68 | 6 - ws6,ws8,ws9,ws10,ws11,ws12 | YES | SHORT |
| EMERGING, raw cross | 2026-08-30 00:20:00 | 2026-08-30 00:20:00 | HIGH | YES | 2026-08-30 00:19:55 | 93.77 | 7 - ws6,ws7,ws8,ws9,ws10,ws11,ws12 | YES | SHORT |
| EMERGING, wob 12 confirm | 2026-08-29 23:16:05 | 2026-08-29 23:17:00 | LOW | no | - | - | 0 - none | no | - |
| EMERGING, wob 12 confirm | 2026-08-29 23:27:10 | 2026-08-29 23:28:05 | LOW | no | - | - | 0 - none | no | - |
| EMERGING, wob 12 confirm | 2026-08-29 23:53:50 | 2026-08-29 23:54:45 | HIGH | YES | 2026-08-29 23:52:10 | 89.64 | 7 - ws6,ws7,ws8,ws9,ws10,ws11,ws12 | YES | SHORT |
| EMERGING, wob 12 confirm | 2026-08-29 23:56:00 | 2026-08-29 23:56:55 | HIGH | YES | 2026-08-29 23:52:10 | 89.64 | 7 - ws6,ws7,ws8,ws9,ws10,ws11,ws12 | YES | SHORT |
| EMERGING, wob 12 confirm | 2026-08-30 00:20:00 | 2026-08-30 00:20:55 | HIGH | YES | 2026-08-30 00:19:55 | 93.77 | 7 - ws6,ws7,ws8,ws9,ws10,ws11,ws12 | YES | SHORT |
| closed_prev, raw cross | 2026-08-29 23:17:00 | 2026-08-29 23:17:00 | LOW | no | - | - | 0 - none | no | - |
| closed_prev, raw cross | 2026-08-29 23:28:00 | 2026-08-29 23:28:00 | LOW | no | - | - | 0 - none | no | - |
| closed_prev, raw cross | 2026-08-29 23:54:00 | 2026-08-29 23:54:00 | HIGH | YES | 2026-08-29 23:50:00 | 87.75 | 7 - ws6,ws7,ws8,ws9,ws10,ws11,ws12 | YES | SHORT |
| closed_prev, raw cross | 2026-08-29 23:57:00 | 2026-08-29 23:57:00 | HIGH | YES | 2026-08-29 23:50:00 | 87.75 | 7 - ws6,ws7,ws8,ws9,ws10,ws11,ws12 | YES | SHORT |
| closed_prev, raw cross | 2026-08-30 00:19:00 | 2026-08-30 00:19:00 | HIGH | no | - | - | 0 - none | no | - |
| closed_prev, raw cross | 2026-08-30 00:21:00 | 2026-08-30 00:21:00 | HIGH | YES | 2026-08-30 00:20:00 | 93.77 | 6 - ws7,ws8,ws9,ws10,ws11,ws12 | YES | SHORT |
| closed_prev, wob 12 confirm | 2026-08-29 23:17:00 | 2026-08-29 23:17:55 | LOW | no | - | - | 0 - none | no | - |
| closed_prev, wob 12 confirm | 2026-08-29 23:28:00 | 2026-08-29 23:28:55 | LOW | no | - | - | 0 - none | no | - |
| closed_prev, wob 12 confirm | 2026-08-29 23:54:00 | 2026-08-29 23:54:55 | HIGH | YES | 2026-08-29 23:50:00 | 87.75 | 7 - ws6,ws7,ws8,ws9,ws10,ws11,ws12 | YES | SHORT |
| closed_prev, wob 12 confirm | 2026-08-29 23:57:00 | 2026-08-29 23:57:55 | HIGH | YES | 2026-08-29 23:50:00 | 87.75 | 7 - ws6,ws7,ws8,ws9,ws10,ws11,ws12 | YES | SHORT |
| closed_prev, wob 12 confirm | 2026-08-30 00:19:00 | 2026-08-30 00:19:55 | HIGH | no | - | - | 0 - none | no | - |
| closed_prev, wob 12 confirm | 2026-08-30 00:21:00 | 2026-08-30 00:21:55 | HIGH | YES | 2026-08-30 00:20:00 | 93.77 | 6 - ws7,ws8,ws9,ws10,ws11,ws12 | YES | SHORT |

## the FIRST firing cross per arm - the chain open

| arm | the open bar | the trade side | the anchor bar | ws5Mage at the anchor | lines away | gap from his 23:53 |
|---|---|---|---|---|---|---|
| EMERGING, raw cross | 2026-08-29 23:53:50 | SHORT | 2026-08-29 23:52:10 | 89.64 | 7 of 7 | +0.8 min |
| EMERGING, wob 12 confirm | 2026-08-29 23:54:45 | SHORT | 2026-08-29 23:52:10 | 89.64 | 7 of 7 | +1.8 min |
| closed_prev, raw cross | 2026-08-29 23:54:00 | SHORT | 2026-08-29 23:50:00 | 87.75 | 7 of 7 | +1.0 min |
| closed_prev, wob 12 confirm | 2026-08-29 23:54:55 | SHORT | 2026-08-29 23:50:00 | 87.75 | 7 of 7 | +1.9 min |

## the ws6..ws12 Mage ladder at the EMERGING anchor, raw-cross arm

| the line | EMERGING at the anchor | away from the HIGH candidate side? |
|---|---|---|
| ws5Mage | 89.64 | the anchor itself |
| ws6Mage | 86.66 | YES |
| ws7Mage | 84.36 | YES |
| ws8Mage | 72.83 | YES |
| ws9Mage | 70.73 | YES |
| ws10Mage | 73.15 | YES |
| ws11Mage | 73.53 | YES |
| ws12Mage | 65.16 | YES |

| the read | value |
|---|---|
| his prediction | 2026-08-29 ~23:53, a SHORT |
| the ws5Mage-oob-entry open I built first | 2026-08-29 23:50:00 |
