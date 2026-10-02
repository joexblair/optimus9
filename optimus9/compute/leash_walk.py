"""leash_walk — the walk that emits `WALK FIRES FROM`, the mech's one and only signal.

JOE 1001: *"`WALK FIRES FROM` is the signal bar"* and *"there is no surviving mech that relies on
`brk`, because our verified strategy uses `WALK FIRES FROM` as our one and only signal"*.

ONE JOB: compose the five tests into an emitted bar. It owns no fence, no wob and no timeframe
ladder — every knob arrives as an argument — reads no DB, builds no line, and applies no gate. The
caller supplies the data through three callables, so the SAME code runs on a cache in the backtest
and on live klines in o9-live.

THE CHAIN, per bar k, reading only bars <= k:

    arm       `arm_state.ArmState` — ws5Mage oob on the dr side for `arm_wob` bars, cancelled on a
              MID cross. It carries the dr, and the ARM'S dr is the signal's dr — Joe 1001:
              *"you were right to require same dr"*
    turn      the first bar at or after the arm where the combined coil (CC * dr) ticks DOWN
    qualify   the bar the `fall`-th DISTINCT timeframe at or above `min_tf` leaves the momTF bucket.
              A timeframe leaves when it has been momentum-true since the arm and then is not; only
              its FIRST departure in an episode counts
    race      `race` flat-run STARTS, from timeframes at or above `frmin`, inside a trailing
              `lb_bars` window. THE EMIT BAR is at or after both the turn and the qualify; the
              STARTS THEMSELVES ARE NOT RESTRICTED TO THAT — they are filtered only by the trailing
              window [k - lb_bars, k]. DO NOT "FIX" THIS: a 1001 mutation that also required the
              starts to be at or after the scan dropped 2 of Joe's 9 validated bars (03:38:00 and
              17:59:25) and moved the day to mech 2706 / cut 1663 / emitted 1043 / runs 21. The
              implemented reading is the one that reproduces his bars
    rev       a ws1mage-rev cross in [k - rev_lookback, k] whose `sig_conf` is at or before k —
              `coil_exit.resolve`'s LOOKBACK leg, with the mech's own bar as `named`. Joe 1001:
              *"it has to be re-inserted in the same way it was before"*

    all five -> EMIT k. rule#1 is the CALLER's: it needs the r lines, and `rule1_gate.gate` already
    owns it. `walk()` returns the bars that passed these five; the caller filters on the gate.

WHAT IS NOT HERE, AND WHY: no `release`, no `coil_moment.moments`, no `coil_exit.resolve`, no `i1`,
no `brk`, no `actionable_*`. Joe 1001 ruled them out — *"there is no surviving mech that relies on
`brk`"* — and the chain that produced the validated 09-01 report referenced none of them.

ONE THING THAT LOOKS NON-CAUSAL AND IS NOT. The offline form of `qualify` collects every departure
in the episode, sorts them, and takes index `fall - 1`. That reads like an end-of-episode
computation. It is not: the `fall`-th smallest departure bar IS the bar on which the `fall`-th
distinct timeframe departed, so a live counter that increments on each timeframe's first departure
reaches `fall` on exactly that bar. This module carries the COUNTER form, and
`test_leash_walk.py::test_qualify_counter_matches_the_sorted_form` holds the two against each other
rather than asserting the equivalence.

THE dr SERIES IS NOT `dr_latch`'s DEFAULT, AND THIS IS THE EASIEST THING TO GET WRONG. Joe 1001:
*"it needs to use whatever built my validated WALK FIRES FROM timestamps"*. That series is the INLINE
loop at `sweep_v3_signal.py:99-106` — ws1Mage + **ws13m** (hardcoded, NOT `latch_tf`), at **85/15**
which is **oob**, with **no wob**. `dr_latch.latch()`'s module defaults are **75/25**
(`dr_latch.py:33`), a different series. Banked as `walk_dr_*` in `wsf_trade_config` v4 so a live
producer has the recipe rather than a loop to copy. A producer that calls `dr_latch.latch(g1, m13,
i0, i1)` without passing `hi=85.0, lo=15.0` gets the wrong dr, and the walk inherits it everywhere.

`rig.DRW` — `latch_wob` at 75/25 wob 8 — is a DIFFERENT series again, and it is what `rule1_gate`
reads inside `Rig.gate_open`. Two series in one mech is the documented v7 precedent (`OPEN.md`:
*"This is intended, not a bug to fix"*) and Joe 1001 confirmed it stands for the walk.

CAUSAL. `step` reads bar k and k-1 from its inputs, the trailing `lb_bars` of flat-run starts it has
already seen, and its own carried state. Nothing ahead of k.
"""
import numpy as np

from optimus9.compute.arm_state import MID, ArmState


class LeashWalk:
    """The walk as carried state. Feed bars in order with `step`; it returns True to EMIT.

    No knob has a default. Joe's 1001 values for this mech, for a caller reading
    `wsf_trade_config`:

        arm_fence     (25.0, 75.0)   the Mage fence
        arm_wob       6 bars = 30 s
        min_tf        7              ws7, the lowest TF whose DEPARTURE counts toward `fall`
        fall          3              distinct departures needed to qualify the race
        race          1              flat-run starts needed inside the lookback
        frmin         4              ws4, the lowest TF whose FLAT-RUN enters the race pool
        lb_bars       48 bars = 4 min
        rev_lookback  48 bars = 240 s, `lookback_s` from the config

    `ladder` is the ordered timeframe list, ascending.
    """

    __slots__ = ('arm', 'ladder', 'min_tf', 'fall', 'race', 'frmin', 'lb', 'rev_lb',
                 '_elig', '_pool', '_seen_mom', '_departed', '_ndep', '_qual', '_turn',
                 '_fr_starts', '_fr_prev', '_cur_arm', '_k')

    def __init__(self, ladder, arm_fence, arm_wob, min_tf, fall, race, frmin, lb_bars,
                 rev_lookback, mid=MID):
        self.arm = ArmState(arm_fence, arm_wob, mid)
        self.ladder = [int(t) for t in ladder]
        self.min_tf = int(min_tf)
        self.fall = int(fall)
        self.race = int(race)
        self.frmin = int(frmin)
        self.lb = int(lb_bars)
        self.rev_lb = int(rev_lookback)
        if self.fall < 1 or self.race < 1:
            raise ValueError('fall and race must be >= 1, got fall=%r race=%r' % (fall, race))
        if self.lb < 0 or self.rev_lb < 0:
            raise ValueError('lb_bars and rev_lookback must be >= 0 bars')
        self._elig = [t for t in self.ladder if t >= self.min_tf]
        self._pool = [t for t in self.ladder if t >= self.frmin]
        self._cur_arm = -1
        self._k = None
        self._reset_episode()

    def _reset_episode(self):
        """Clear every per-episode field. Called on each new arm, so no state crosses an episode."""
        self._seen_mom = set()
        self._departed = set()
        self._ndep = 0
        self._qual = None
        self._turn = None
        self._fr_starts = []
        self._fr_prev = {}

    def step(self, k, mage_k, mage_prev, dr_k, dr_prev, cc_k, cc_prev, mom, fr, rev_ok):
        """Advance to bar `k`. -> True to EMIT at `k`.

        mage_k/mage_prev   the arm's Mage line at k and k-1. `mage_prev` None on the first bar
        dr_k/dr_prev       the dr series at k and k-1
        cc_k/cc_prev       the COMBINED COIL at k and k-1, UNSIGNED. The dr is applied here, using
                           the arm's dr, so the caller does not have to know which dr is in force
        mom                callable(tf) -> bool: is `tf` momentum-true at k on the arm's dr
        fr                 callable(tf) -> bool: is `tf` in a flat run at k on the arm's dr
        rev_ok             bool: a ws1mage-rev cross in [k - rev_lookback, k] with sig_conf <= k
        """
        if self._k is not None and k != self._k + 1:
            raise ValueError('LeashWalk.step must be called on consecutive bars: '
                             'last %r, got %r' % (self._k, k))
        self._k = int(k)
        live, arm_bar, arm_dr = self.arm.step(k, mage_k, mage_prev, dr_k, dr_prev)
        if not live:
            self._cur_arm = -1
            return False
        if arm_bar != self._cur_arm:
            self._cur_arm = int(arm_bar)
            self._reset_episode()

        # --- the turn: first bar at or after the arm where the coil * dr ticks DOWN -------------
        if self._turn is None and cc_prev is not None and k > arm_bar:
            if float(cc_k) * arm_dr < float(cc_prev) * arm_dr:
                self._turn = int(k)

        # --- the qualify: the fall-th DISTINCT eligible timeframe to leave the momTF bucket ------
        for t in self._elig:
            if t in self._departed:
                continue
            if mom(t):
                self._seen_mom.add(t)
            elif t in self._seen_mom:
                self._departed.add(t)
                self._ndep += 1
                if self._ndep == self.fall:
                    self._qual = int(k)

        # --- the race pool: flat-run STARTS, a rising edge per timeframe -------------------------
        for t in self._pool:
            f = bool(fr(t))
            if f and not self._fr_prev.get(t, False):
                self._fr_starts.append(int(k))
            self._fr_prev[t] = f
        if self.lb > 0 and self._fr_starts:
            lo = k - self.lb
            if self._fr_starts[0] < lo:
                self._fr_starts = [x for x in self._fr_starts if x >= lo]

        # --- scan, race, rev --------------------------------------------------------------------
        if self._turn is None or self._qual is None:
            return False
        if k < max(self._turn, self._qual):
            return False
        lo = k - self.lb if self.lb > 0 else k
        if sum(1 for x in self._fr_starts if lo <= x <= k) < self.race:
            return False
        return bool(rev_ok)

    @property
    def state(self):
        """The episode's bars, for a report or a recon row. -> dict, never None."""
        return dict(arm=self._cur_arm, arm_dr=self.arm.arm_dr, turn=self._turn,
                    qualify=self._qual,
                    scan=None if (self._turn is None or self._qual is None)
                    else max(self._turn, self._qual),
                    departed=sorted(self._departed))


def rev_lookback_mask(sig, sig_conf, n, lookback):
    """The LOOKBACK leg as a per-bar mask. -> bool array of length `n`.

    A bar `k` is True when some ws1mage-rev cross sits in [k - lookback, k] AND that cross's
    `sig_conf` is at or before `k`. That is `coil_exit._knowable(legs, k - lookback, k, k)` being
    non-empty, which `test_leash_walk.py` holds this against bar for bar.

    `sig` and `sig_conf` are one dr's arrays from `jig.ws1mage_rev`.
    """
    ok = np.zeros(int(n), bool)
    for s_, c_ in zip(np.asarray(sig, np.int64), np.asarray(sig_conf, np.int64)):
        a = max(int(c_), int(s_))                  # k >= the conf bar AND k >= the cross bar
        b = min(int(n) - 1, int(s_) + int(lookback))
        if a <= b:
            ok[a:b + 1] = True
    return ok


def step_bar(w, k, m_k, m_prev, d_k, d_prev, c_k, c_prev, mom_at, fr_at, rev_ok):
    """ONE bar of the walk, with the dr routed the way the mech requires. -> True to EMIT at `k`.

    While the arm is live, momentum, flat-run and the rev leg are read on the ARM'S dr; otherwise on
    the bar's own dr. That routing used to be inline in `walk()`. It moved here 1002 so `walk()` (the
    backtest) and `optimus9/live/octo_freedom.py` (the live producer, which steps one bar per 5 s
    across windows) run the SAME lines - Joe ruled the evolving cache, and a copied routing is the
    next divergent copy.

    mom_at(tf, dr) / fr_at(tf, dr)   the caller's readers AT THIS BAR
    rev_ok(dr)                       the rev mask at this bar on `dr`; a dr it has no mask for -> False
    """
    adr = w.arm.arm_dr if w.arm.live else int(d_k)
    return w.step(k, m_k, m_prev, d_k, d_prev, c_k, c_prev,
                  (lambda t, _d=adr: mom_at(t, _d)),
                  (lambda t, _d=adr: fr_at(t, _d)),
                  bool(rev_ok(adr)))


def walk(ladder, mage, dr, cc, mom_at, fr_at, rev_mask, i0, i1, **knobs):
    """Drive `LeashWalk` over [i0, i1]. -> (bars, {bar: episode state at that bar}).

    The state is returned KEYED BY BAR, not as a parallel list. A list invites the caller to index
    it with a position from a FILTERED set: `report_leash_walk.py` did exactly that on its first
    run — `states[emit.index(k)]` after rule#1 had removed 1,673 of 2,768 bars — and printed the
    wrong arm bar beside every correct fire bar.

    The BACKTEST's convenience, running the identical `step` a live walk runs — there is no second
    implementation. `mom_at(tf, k, dr)` and `fr_at(tf, k, dr)` are the caller's data source;
    `rev_mask` is {dr: bool array} from `rev_lookback_mask`. Each bar goes through `step_bar`.
    """
    m = np.asarray(mage, float)
    d = np.asarray(dr, np.int8)
    c = np.asarray(cc, float)
    w = LeashWalk(ladder, **knobs)
    out = []
    states = {}
    i0 = int(i0)
    for k in range(i0, int(i1) + 1):
        hit = step_bar(w, k, float(m[k]), None if k == i0 else float(m[k - 1]),
                       int(d[k]), None if k == i0 else int(d[k - 1]),
                       float(c[k]), None if k == i0 else float(c[k - 1]),
                       (lambda t, a, _k=k: mom_at(t, _k, a)),
                       (lambda t, a, _k=k: fr_at(t, _k, a)),
                       (lambda a, _k=k: bool(rev_mask[a][_k]) if a in rev_mask else False))
        if hit:
            out.append(int(k))
            states[int(k)] = dict(w.state)
    return out, states


def walk_fires_from(emit):
    """Joe's `WALK FIRES FROM`: the FIRST bar of each run of CONSECUTIVE emitted bars.

    -> [(first, last)] in bar order, one tuple per run. `first` IS the `WALK FIRES FROM` bar and the
    bar an `octo-sig` trade opens on; `last` is the run's final emitted bar and opens nothing.

    MOVED HERE 1001 FROM `report_leash_walk.py`'s main(). Joe, on the finding that the rule defining
    his own signal lived in a report rather than in the mech: *"I'm taking your recommendation - clean
    the house before we handover"*. It was the next divergent copy waiting to happen - the same shape
    as `bank_emit_entry.walk_no_flip_open` losing a ruled clause (`docs/octo-freedom/1001_rewalk_on_ruled_dr.md`).

    WHY IT IS NOT INSIDE `walk()`. `walk()` returns the MECH bars; rule#1 is the CALLER's, because it
    needs the r lines this module never sees. The run grouping has to happen AFTER that gate, so it
    cannot live in the stepper. On 09-01 the three populations are 2,768 MECH -> 1,095 EMITTED -> 23
    runs, and only the 23 are signals.

    FEEDING THE EMITTED BARS STRAIGHT TO `trade_walk.walk` IS THE MISTAKE THIS GUARDS. 1,095 bars
    would be offered as opens where 23 are signals.

    `emit` must be STRICTLY ASCENDING - it is `[k for k in mech if gate_open(k)]` and `walk()` emits
    in bar order. A duplicate or an out-of-order bar silently merges or splits runs, so it raises
    instead, the same discipline as `LeashWalk.step`'s consecutive-bar guard.
    """
    e = [int(x) for x in emit]
    for a, b in zip(e, e[1:]):
        if b <= a:
            raise ValueError('walk_fires_from needs STRICTLY ASCENDING bars: %d then %d' % (a, b))
    runs = []
    st = None
    for i, k in enumerate(e):
        if st is None:
            st = k
        if i + 1 == len(e) or e[i + 1] != k + 1:
            runs.append((st, k))
            st = None
    return runs
