# the 08-04 line dataset — `build_ws_line_bar.py`

Built 0816 on Joe's ask: *"prepare a 08-04 24 hour dataset that allows for quick response to these
kind of questions"* and *"keep your data durable, 5s granularity"*. It exists so a line question is
answered by a query instead of a rebuild.

It belongs to neither spec. domTF and the ws-finisher both read from it; neither owns it.

## the two tables

| table | rows | one row is |
|---|---|---|
| `ws_line_bar` | **17,281** | one 5-second bar, 08-04 00:00:00 to 08-05 00:00:00 inclusive. 74 columns: every line's value, plus a `wlb_{group}_newbar` flag marking the bar where that group's own timeframe rolls over |
| `ws_line_cross` | **110,330** | one crossing. Every pair inside a group, plus each line against 85 and against 15, in both directions |

The end of the window is INCLUSIVE — the last row sits ON 08-05 00:00:00, so the delete that
precedes a rebuild uses `<=`, not `<`. A `<` there is a duplicate-key error on the next run.

## coverage

| | |
|---|---|
| groups | ws1 … ws10, gcws15, gcws30 |
| kinds | `x`, `m`, `Mage`, `b`, `r` |
| grid | 5 seconds |
| boundaries | 85 / 15, from `optimus9_system` |

All five kinds are built from the line store, by name, never from a hand-written tuple. ws10 did
not exist in the store until 0816; Joe: *"create the new row / add all 5 lines / for the new lines,
ic_live_after_date = 2026-08-15"*. The live config is read through `vw_indicator_configs_live`,
per Joe: *"there is a view that selects only the active config. use the view."*

## the report names Joe uses

| name | what it prints |
|---|---|
| **mage_r_snapshot** | for a timestamp: ws1Mage … ws10Mage with each line's r beside it, and the same pair again at a second timestamp so the two can be read side by side. Joe named it 0816 so he can ask for it by name |
| the per-xwob cross table | for a crossing: the timestamp at each xwob from 1 to 8, and per xwob the timeframes tagged momo or curl. Joe 0816: *"I still need to see the timestamp per wob"* and *"print only the race winner"* |

## knob

| knob | value | what it does |
|---|---|---|
| `MOMO_CHECK_TFS` | **2 to 10** | which ws{tf}r lines the momentum column covers in these reports. Joe 0816: *"permanently include ws[2,3,4,5]r in the momo check"*, then *"reduce coverage: ws2 to w10"*. Lives in `optimus9/analysis/jig.py`. It is NOT the domTF ladder and NOT the ws-finisher's TF1-8 scan |
