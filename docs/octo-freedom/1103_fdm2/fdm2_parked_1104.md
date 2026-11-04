# PARKED, to resume when the sweep is closed - his 1104 words

*"before I worked on the reentry, we were looking at a table that produced the groups of towards
lines and reversed lines, that we were using to confluence or stay the ws10x-cadence verdicts.
we'll return to this work after the sweep is closed"*

## what that work was

The `fdm2-conf` table - his name, 1104 - reads the board at each trade-setup's signal bar and
groups the lines two ways:

- `towards` / `away` from `jig.towards_away`, his rolling-extremum mech on EMERGING values with an
  exact gap: one anchor per trade side, so a line cannot be both
- the reversal groups from the lift-off stamps, which is what the ws10x-cadence's own reversal
  count already uses

The purpose, in his words, was to **confluence or stay** a ws10x-cadence verdict: the cadence says
rev-trade, and the groups of towards lines and reversed lines either back that or hold it.

## where it stands

| what exists | where |
|---|---|
| the fdm2-conf table | `W_FDM2_CONF=on` in fdm2_chain.py, 11 columns, every re-entry leg plus incoming setups at or under zero |
| towards / away | `jig.towards_away`, banked on the Jig as the single source |
| the reversal count | `v4_fdm2.reversed_tfs` and `reversed_since`, the ws10x-cadence's own |
| what was NOT built | the confluence or stay rule itself. He never ruled it |

## why it matters more now than it did

The 1104 sweep found the exit is the stage that loses: the walk and the stop keep -2.1% of the
move the openings find, against a hindsight ceiling of +0.6059% per open. The ws10x-cadence IS the
exit's decision, and staying a bad verdict is exactly the lever the baseline says is missing.

See `fdm2_baseline_1104.md` for the numbers this resumes against.
