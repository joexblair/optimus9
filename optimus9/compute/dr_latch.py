"""dr_latch — the ONE global dr source, and the wob that Joe ruled on.

ONE JOB: turn ws1Mage and ws{LATCH_TF}m into the dr series. It owns no fence beyond the two it is
handed, reads no DB, and decides no trade.

JOE 0925, asked whether the dr flip came off anything else: *"dr-flip taken off the ws1Mage + ws13m
latch. there's only one global source for dr"*.

TWO PRODUCERS, AND THEY ARE NOT THE SAME SERIES.

  `latch`      lifted from `walk_mom_models.dr_latch`. It latches on the FIRST bar both lines are
               beyond the fence on the same side. This is what built `wsf_dtf_v3` and, through it,
               `wsf_leash.wsl_dr` - BUT NOT AT THIS MODULE'S DEFAULT FENCE. See the correction below.
  `latch_wob`  the same with a `wob`: both lines must hold the same side for `wob` CONSECUTIVE bars
               before the latch moves. Lifted from `docs/mage_cascade/stopsweep.py:62`.

MEASURED over the whole tape, 1,632,960 bars: `latch` gives 3,217 stretches, `latch_wob` at wob 8
gives 2,497, and they disagree on 112,984 bars = 6.92%.

JOE RULED wob 8, 0926, with the cost in front of him: *"we have to stick on 8 - there's too many `t`s
affected"*. Swapping to `latch` moved walk-complete on 25 of 154 sig_utc rows, 12 of them carrying his
`t` tag. His first instinct had been the other way - *"for the last few days I've been thinking about
moving the dr-flip earlier to improve the backstop... no wob"* - and he reversed it on the numbers.

`wsl_dr` IS NOT THIS SERIES READ AT THE SIGNAL BAR. It is `latch` read at the moment's FIRST bar, and
it reproduces `wsf_leash.wsl_dr` on 242 of 242 rows. The walk's dr is `latch_wob` read live at the bar
it starts from. Joe 0926 knows and intends the difference; spec §22.21 and §22.22 carry it.

CORRECTED 1001 - THE FENCE LINEAGE. This module's defaults are the Mage fence **75/25**. Joe's own
view of dr, stated 1001: *"my view of dr is ws1Mage + ws13m oob"* - and `oob` is ALWAYS 15/85. He is
right, and the original agrees with him:

| what | fence | where the fence comes from |
|---|---|---|
| `build_wsf_dtf_v3.py:317-318` - THE ORIGINAL | **85 / 15** | `optimus9_system.hi_boundary`/`lo_boundary`, read from the DB at `:217` |
| `sweep_v3_signal.Rig.DR` - what `octo-freedom`'s walk reads | **85 / 15** | hardcoded inline at `:99-106`, same values |
| `walk_mom_models.dr_latch` | 75 / 25 | its own `MAGE_HI/LO` constant |
| THIS MODULE's defaults | 75 / 25 | inherited from the line above |
| `Rig.DRW` - what rule#1 reads, via `latch_wob` | 75 / 25, wob 8 | `trade_config.mage_fence_*` |

The chain of docstrings claiming "verbatim" and "oob" was wrong at two links, and this module
inherited it. **Joe's oob dr was never dropped** - it is the original and it is live in the walk.

WHAT THIS MEANS FOR THE wob RULING, STATED AND NOT RESOLVED. The 0926 measurement behind Joe's
*"we have to stick on 8"* was taken on THIS module's 75/25 series. If he was ruling on his oob view,
the wob was ruled against a series he was not looking at. He has seen this and ruled: *"no changes
for now. fix the docstrings to suit, and add 'dr fence + wob' sweep to MVP2"*. The sweep is MVP2
item 5.

CAUSAL. Both walk forward bar by bar and read nothing ahead.
"""
import numpy as np

MAGE_HI, MAGE_LO = 75.0, 25.0     # the Mage fence. CORRECTED 1001 - this comment used to read
#                                   "the Mage fence, build_wsf_dtf_v3. NOT oob, which is 15/85",
#                                   which asserts the OPPOSITE of what build_wsf_dtf_v3 does. See
#                                   the module docstring
LATCH_TF = 13                     # the second line is ws13m
LATCH_W = 8                       # Joe 0926: "we have to stick on 8". 8 bars = 40 s at the 5 s grid


def latch(m1, mx, i0, i1, hi=MAGE_HI, lo=MAGE_LO):
    """The dr series with NO wob. -> int8 array the length of `m1`.

    Latches +1 the first bar both lines are at or above `hi`, -1 the first bar both are at or below
    `lo`. The previous dr holds until both agree on a side. 0 before the first agreement.
    """
    m1 = np.asarray(m1, float); mx = np.asarray(mx, float)
    out = np.zeros(len(m1), np.int8); cur = 0
    for k in range(int(i0), int(i1) + 1):
        a, b = float(m1[k]), float(mx[k])
        if a == a and b == b:
            if a >= hi and b >= hi:
                cur = +1
            elif a <= lo and b <= lo:
                cur = -1
        out[k] = cur
    return out


def latch_wob(m1, mx, i0, i1, wob=LATCH_W, hi=MAGE_HI, lo=MAGE_LO):
    """The dr series requiring `wob` CONSECUTIVE bars of agreement. -> int8 array.

    `wob` 8 = 40 s at the 5 s grid. A run of fewer than `wob` bars never moves the latch, so a short
    stretch that `latch` sees can be absent here entirely - that is why the two differ on 6.92% of
    bars and not merely by a lag.
    """
    m1 = np.asarray(m1, float); mx = np.asarray(mx, float)
    out = np.zeros(len(m1), np.int8); cur = 0; up = 0; dn = 0
    for k in range(int(i0), int(i1) + 1):
        a, b = float(m1[k]), float(mx[k])
        if a == a and b == b:
            up = up + 1 if (a >= hi and b >= hi) else 0
            dn = dn + 1 if (a <= lo and b <= lo) else 0
            if up >= wob:
                cur = +1
            elif dn >= wob:
                cur = -1
        out[k] = cur
    return out
