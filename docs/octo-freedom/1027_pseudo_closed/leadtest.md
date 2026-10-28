# EX-FENCE ENTRY: LEAD AND UNCONFIRMED RATE, 2026-08-30 00:00:00 .. 2026-09-06 23:59:55
# the reference is the CLOSED read - where TV's closed bars put the entry.
# LEAD = the candidate entry inside the one TF BEFORE a closed entry, in minutes.
# UNCONFIRMED = a candidate entry with no closed entry inside the one TF after it.
# the matching window is ONE TF WIDTH - the lag the closed read carries by construction.
# RULED_OK True | pseudo BARS 120

| the line | side | the read | entries | closed entries matched | median lead min | unconfirmed | unconfirmed % |
|---|---|---|---|---|---|---|---|
| ws13r | LOW | pseudo | 1117 | 35 of 35 | 1.2 | 927 | 83.0% |
| ws13r | LOW | emerging | 236 | 35 of 35 | 12.9 | 150 | 63.6% |
| ws13r | HIGH | pseudo | 829 | 23 of 23 | 1.2 | 701 | 84.6% |
| ws13r | HIGH | emerging | 173 | 23 of 23 | 13.0 | 121 | 69.9% |
| ws14r | LOW | pseudo | 1142 | 30 of 30 | 1.2 | 955 | 83.6% |
| ws14r | LOW | emerging | 200 | 30 of 30 | 14.0 | 132 | 66.0% |
| ws14r | HIGH | pseudo | 756 | 23 of 23 | 1.3 | 632 | 83.6% |
| ws14r | HIGH | emerging | 171 | 23 of 23 | 14.0 | 125 | 73.1% |
| ws15r | LOW | pseudo | 1095 | 29 of 29 | 1.9 | 925 | 84.5% |
| ws15r | LOW | emerging | 192 | 29 of 29 | 15.0 | 119 | 62.0% |
| ws15r | HIGH | pseudo | 753 | 15 of 15 | 2.0 | 675 | 89.6% |
| ws15r | HIGH | emerging | 120 | 15 of 15 | 15.0 | 86 | 71.7% |
| ws16r | LOW | pseudo | 1050 | 21 of 21 | 1.4 | 892 | 85.0% |
| ws16r | LOW | emerging | 125 | 21 of 21 | 16.0 | 83 | 66.4% |
| ws16r | HIGH | pseudo | 729 | 19 of 19 | 0.8 | 588 | 80.7% |
| ws16r | HIGH | emerging | 115 | 19 of 19 | 16.0 | 81 | 70.4% |
