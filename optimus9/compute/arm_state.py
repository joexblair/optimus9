"""arm_state — the ws5Mage arm, as a STATE a walk carries bar by bar.

ONE JOB: given the Mage line and the dr series, say whether the arm is live at each bar, which bar
set it, and which dr it carries. It owns no fence and no wob — both arrive as arguments — reads no
DB, and decides no signal.

JOE 1001: *"`arm` is a state, not a column"* and *"you were right to require same dr. update the
mech"* — the arm's dr MUST equal the signal's dr, so the dr is carried on the state rather than
re-read at the signal bar.

    set      the Mage line is oob on the dr side for `wob` CONSECUTIVE bars, and the dr has not
             changed across that run. The arm is set on the FIRST bar the run REACHES `wob`, not
             on any later bar inside the same run. Joe 0930 caught that defect twice.
    cancel   the Mage line crosses MID — the sign of (Mage - MID) changes, EITHER direction
    carries  the dr in force at the bar the run completed
    live     set, and not cancelled since

WHY IT IS A STEPPER AND NOT A VECTORISED FUNCTION. The state is path-dependent: `run`, `live`,
`arm` and `arm_dr` all carry forward, so the value at bar k is a function of the bars before it. A
vectorised helper that silently started at the caller's window edge would give a different answer
live than in the backtest — the same hazard `dr_latch.latch_wob` carries, flagged in
`docs/o9-live-recon/CODE_MAP.md`.

THE WARMUP IS BOUNDED, AND THAT IS WHAT MAKES IT LIVE-SAFE. A MID cross resets every field to its
initial value, so the state at bar k is fully determined by the bars since the last MID cross. A
live walk that seeds at or before the most recent MID cross reproduces the backtest exactly.
`warmup_from` returns that bar. `test_arm_state.py` proves the property rather than asserting it.

CAUSAL. `step` reads `mage[k]`, `mage[k-1]`, `dr[k]`, `dr[k-1]` and its own carried state. Nothing
ahead of k.
"""
import numpy as np

MID = 50.0


class ArmState:
    """The arm as carried state. Feed it bars in order with `step`; read `live`/`arm`/`arm_dr`.

    `fence` is (lo, hi) — the dr-side test is `mage >= hi` at dr +1 and `mage <= lo` at dr -1.
    `wob` is the number of CONSECUTIVE bars the run must reach, in bars.
    Neither has a default: Joe 1001 ruled 25/75 and 6 bars = 30 s for this mech, and a caller that
    reads them from `wsf_trade_config` cannot then drift from it.
    """

    __slots__ = ('lo', 'hi', 'wob', 'mid', 'live', 'arm', 'arm_dr', '_run', '_k')

    def __init__(self, fence, wob, mid=MID):
        self.lo, self.hi = float(fence[0]), float(fence[1])
        self.wob = int(wob)
        self.mid = float(mid)
        if self.wob < 1:
            raise ValueError('wob must be >= 1 bar, got %r' % (wob,))
        self.live = False
        self.arm = -1
        self.arm_dr = 0
        self._run = 0
        self._k = None

    def step(self, k, mage_k, mage_prev, dr_k, dr_prev):
        """Advance to bar `k`. -> (live, arm, arm_dr) after this bar.

        `mage_prev`/`dr_prev` are bar k-1. Pass `mage_prev=None` on the first bar of a walk, which
        suppresses the MID-cross test for that bar only — there is no previous bar to cross from.
        """
        if self._k is not None and k != self._k + 1:
            raise ValueError('ArmState.step must be called on consecutive bars: '
                             'last %r, got %r' % (self._k, k))
        self._k = int(k)
        if mage_prev is not None and (mage_k - self.mid) * (mage_prev - self.mid) < 0:
            self.live = False
            self.arm = -1
            self.arm_dr = 0
            self._run = 0
        d = int(dr_k)
        oob = (mage_k >= self.hi) if d > 0 else (mage_k <= self.lo)
        if oob and (self._run == 0 or dr_prev is None or int(dr_prev) == d):
            self._run += 1
        else:
            self._run = 0
        if self._run >= self.wob and not self.live:
            self.live = True
            self.arm = int(k)
            self.arm_dr = d
        return self.live, self.arm, self.arm_dr


def warmup_from(mage, k, floor=0, mid=MID):
    """The earliest bar a walk may seed at to reproduce `ArmState` at bar `k`. -> bar index.

    Walks back from `k` to the most recent MID cross, which resets every field. `floor` bounds the
    search; the returned bar is `floor` when no cross is found, and the caller then has a state that
    depends on bars it has not seen.
    """
    m = np.asarray(mage, float)
    j = int(k)
    while j > int(floor):
        if (m[j] - mid) * (m[j - 1] - mid) < 0:
            return j
        j -= 1
    return int(floor)


def run(mage, dr, i0, i1, fence, wob, mid=MID):
    """Drive `ArmState` over [i0, i1]. -> (live, arm, arm_dr) as arrays indexed by bar.

    This is the BACKTEST's convenience and it runs the identical `step` a live walk runs — there is
    no second implementation. Bars outside [i0, i1] are left at their initial values: live False,
    arm -1, arm_dr 0.
    """
    m = np.asarray(mage, float)
    d = np.asarray(dr, np.int8)
    n = len(m)
    live = np.zeros(n, bool)
    arm = np.full(n, -1, np.int64)
    adr = np.zeros(n, np.int8)
    st = ArmState(fence, wob, mid)
    i0 = int(i0)
    for k in range(i0, int(i1) + 1):
        lv, ab, ad = st.step(k, float(m[k]), None if k == i0 else float(m[k - 1]),
                             int(d[k]), None if k == i0 else int(d[k - 1]))
        live[k] = lv
        arm[k] = ab
        adr[k] = ad
    return live, arm, adr


def episodes(live, arm, arm_dr, i0, i1):
    """The armed spans inside [i0, i1]. -> [(arm_bar, end_bar, dr, cancelled)], ascending.

    `end_bar` has ONE meaning: the first bar the arm is NOT live. So `[arm_bar, end_bar)` is exactly
    the live span and a caller slices it without an off-by-one. `cancelled` says WHY it ended —
    True for a MID cross, False for an episode still live when the walk ended, in which case
    `end_bar` is `i1 + 1` and is outside the walked range.

    Joe 0930 split `coil_exit`'s single `actionable` key into four fields for exactly this reason:
    one field carrying two events makes every statement about it true on one case and false on the
    other. An earlier draft of this function returned the MID-cross bar in one case and the last
    live bar in the other; `test_arm_state.py` caught it.

    An episode's dr is the one the ARM carried, not the dr at `end_bar`.
    """
    out = []
    cur = -1
    for k in range(int(i0), int(i1) + 1):
        if live[k] and arm[k] != cur:
            cur = int(arm[k])
            out.append([cur, None, int(arm_dr[k]), False])
        elif not live[k] and out and out[-1][1] is None:
            out[-1][1] = int(k)
            out[-1][3] = True
            cur = -1
    if out and out[-1][1] is None:
        out[-1][1] = int(i1) + 1
        out[-1][3] = False
    return [(a, b, d, c) for a, b, d, c in out]
