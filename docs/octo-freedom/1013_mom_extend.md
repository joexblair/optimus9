# THE MOMENTUM EXTENSION MECH — 1013

Joe 1013, verbatim:

> we're going to use this momentum to extend trades.
> the mech fires at the the close event:
> -the close event will be held
> -ongoing momentum is tested using n of 7 `toward this column's board`
> -if n >=4 then ride ws{mom_cont_tf}r until it is stalled
> --the ws{mom-cont-tf}r stall can fire infence
> -on stall, the held close will fire
> eg for 07-18 10:40, mom-cont-tf=10, n=4, the leg should extend to ~11:11 or ~11:55

Built in `docs/octo-freedom/1005_scoring/_extmom.py`. SRP: that file answers one question — which
bar does a held close actually fire on. It does not open a trade, does not close one, and holds no
state across calls. The lineage walk (`_chain10`) and the IB-cross mech (`_ibmech`) are untouched.

## THE BOARD

The close column's board — the **flipped dr**, not the leg's own. Joe 1013: *"flip the dr on the
close trade - we're not reversing, we're extending the leg using those mom-true lines"*.

The leg's own board is `-dr`. The close column reads the board of the flipped dr, i.e. `+dr`.

| leg | dr | own board | the close column's board |
|---|---|---|---|
| 07-17 21:58 LONG | -1 | HIGH | LOW |
| 07-18 02:31 SHORT | +1 | LOW | HIGH |
| 07-18 08:46 LONG | -1 | HIGH | LOW |
| 07-18 16:07 LONG | -1 | HIGH | LOW |

## THE 7 LINES

The momentum report's rows: ws12, ws15, ws20, ws30, dws8r, dws10r, dws15r. `n` is how many of them
are mom-true toward the board at a bar. They are passed INTO the mech as (name, mask) pairs — the
caller owns `MOMT` / `MOMD` and this file does not know how a mask is built.

| close bar | leg | board | n of 7 | held? |
|---|---|---|---|---|
| 2026-07-18 01:15:20 | 07-17 21:58 LONG | LOW | 0 of 7 | no, fires unheld |
| 2026-07-18 10:40:40 | 07-18 02:31 SHORT | HIGH | 6 of 7 | YES |
| 2026-07-18 10:07:10 | 07-18 08:46 LONG | LOW | 0 of 7 | no, fires unheld |
| 2026-07-18 16:38:15 | 07-18 16:07 LONG | LOW | 5 of 7 | YES |

## THE RIDE LINE — WHY dws10r AND NOT ws10r

Joe's notation is `ws{mom_cont_tf}r` and his example sets `mom_cont_tf` 10. Measured on both
families at both qualifying closes, gate off, as the 4-leg gross against the standing +6.4370%:

| mom_cont_tf | 4-leg gross | vs standing | both legs up? |
|---|---|---|---|
| dws15r | +7.6278% | +1.1908% | no — the SHORT loses 0.0457%, its ride runs 287.2 min |
| dws10r | +7.1028% | +0.6658% | yes — +0.3548% and +0.3110% |
| dws8r | +7.0846% | +0.6476% | yes — +0.3410% and +0.3066% |
| ws20r | +6.6312% | +0.1942% | yes — +0.1718% and +0.0225% |
| ws12r | +6.4902% | +0.0532% | no |
| ws8r | +6.4341% | -0.0029% | no |
| ws10r | +6.4341% | -0.0029% | no |
| ws15r | +6.4320% | -0.0050% | no |
| ws30r | +6.0751% | -0.3619% | no — both legs lose |

ws10r, the literal reading, is ALREADY stalled at both close bars — it fires 5 s after each one and
extends nothing. Joe banked dws10r: *"your proposal is good, let's bank it"*.

Joe's two candidate timestamps for the 10:40:40 close were ~11:11 and ~11:55. Three readings land on
~11:11 and none on ~11:55:

| reading | bar | +min held |
|---|---|---|
| dws8r stall, HIGH board, gate off | 2026-07-18 11:10:30 | 29.8 |
| dws10r stall, HIGH board, gate off | 2026-07-18 11:11:15 | 30.6 |
| n of 7 re-asked every bar, first below 4 | 2026-07-18 11:12:00 | 31.3 |

The nearest thing to ~11:55 is dws10r with the ex-fence gate **on**, 2026-07-18 11:47:05, 8 min
short. ~11:55 has no mech behind it. STATED, not explained.

## THE STALL

`jig.stall_mask` with `stall_n` 6 samples on the ride line's own momo lattice — at tf 10 that is
step 36 bars, 21 samples, a span of 720 bars = 60.0 min.

The ex-fence gate is **OFF**, per Joe: *"the ws{mom-cont-tf}r stall can fire infence"*. `_chain10`
gates its own stall to the same-side ex-fence 17/83 for the lineage walk; this mech does not.
`W_EXT_FENCE=1` is kept only to re-measure that difference.

The stall's side is the board being ridden. The ride goes toward the board that passed the n test,
so the stall is asked on that side.

## THE EXIT RULE — THE ONE THING NOT RULED

`W_EXT_EXIT`, three values, three different numbers:

| W_EXT_EXIT | the rule | 4-leg gross | the 02:31 SHORT fires | the 16:07 LONG fires |
|---|---|---|---|---|
| `stall` | the first ride-line stall | +7.1028% | 2026-07-18 11:11:15 | 2026-07-18 17:39:10 |
| `n` | n first falls under `W_EXT_N` | +7.1898% | 2026-07-18 11:12:00 | 2026-07-18 16:57:00 |
| `first` | whichever comes first | +7.0684% | 2026-07-18 11:11:15 | 2026-07-18 16:57:00 |

DEFAULT `stall` — Joe banked the proposal, and the proposal was the stall exit with `mom_cont_tf`
10. The `n` reading is his own words *"ongoing momentum is tested"* taken literally, and it is the
better of the three on this sample. He has not ruled between them, so it is a knob and not a silent
choice.

## PER-LEG, UNDER THE BANKED DEFAULT

| leg | held close | fires | +min held | why | gross | standing gross |
|---|---|---|---|---|---|---|
| 07-17 21:58 LONG | 2026-07-18 01:15:20 | 2026-07-18 01:15:20 | 0.0 | n 0 of 7 under 4 — fires unheld | +1.0517% | +1.0517% |
| 07-18 02:31 SHORT | 2026-07-18 10:40:40 | 2026-07-18 11:11:15 | 30.6 | dws10r stalled at 79.84 | +4.8615% | +4.5067% |
| 07-18 08:46 LONG | 2026-07-18 10:07:10 | 2026-07-18 10:07:10 | 0.0 | n 0 of 7 under 4 — fires unheld | +0.3929% | +0.3929% |
| 07-18 16:07 LONG | 2026-07-18 16:38:15 | 2026-07-18 17:39:10 | 60.9 | dws10r stalled at 37.93 | +0.7967% | +0.4857% |
| **TOTAL** | — | — | — | — | **+7.1028%** | **+6.4370%** |

The hold adds no leg boundary, so drag is unchanged by every row above. These are gross figures.

## WHAT IS NOT IN THE MECH

- NO BOUND ON THE RIDE. Joe has not specified one, so there is no cap, no horizon and no maximum
  hold. A ride that finds no stall on the tape returns None and the caller decides.
- `n` under the threshold at the close bar means the close is NOT held — `exit_bar` returns the
  close bar itself.
- The mech does not open anything. Joe 1012: *"exits no longer create an open. they are two
  different mechs, and I haven't shared the open mech yet"*.

## THE SAMPLE

2 qualifying closes, both on 2026-07-18. One day. The other two closes read 0 of 7, so no value of
`mom_cont_tf` touches them and the whole comparison above rests on 2 episodes. Not a basis for
fixing a knob.

## CONTROL

The four legs reproduce their banked gross exactly from the entry/exit bars and the gross formula
before anything is swept — +1.0517%, +4.5067%, +0.3929%, +0.4857%, total +6.4370%. All three
`W_EXT_EXIT` values reproduce their measured totals through the module.

Verification driver: `/home/joe/.claude/jobs/6eb9931e/tmp/_extv.py`, run as
`LG_TAPE_END=2026-10-05 W_CEIL=30 W_BATON=momentum python3 _extv.py` from `1005_scoring`.
`W_CEIL=30` is required — the default ceiling is ws23 and `MOMT[30]` does not exist without it.
