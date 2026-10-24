# v4 CLOSED LINES. tape end 2026-10-05, hours 40, warmup 1114, mode closed
# the DB row is NOT changed - a closed line is an override on its own cache key

| the line | tf | the spec | the cache key | before |
|---|---|---|---|---|
| gcws30Mage | 30s | ('bb', 38, 0.93, 'close') | 1a46b7d58cb75ccd0803 | missing |

# ts 2026-07-02 12:00:00 -> 2026-10-04 23:59:55, 1632960 bars

| the line | finite | min | median | max | first finite |
|---|---|---|---|---|---|
| gcws30Mage | 1632738 | -79.70 | 49.10 | 174.41 | 2026-07-02 12:18:30 |

| the line | mode | bars that changed | % of bars |
|---|---|---|---|
| gcws30Mage | closed | 270328 | 16.6% |
| gcws30Mage | emerging | 1137620 | 69.7% |
