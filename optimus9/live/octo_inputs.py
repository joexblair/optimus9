"""octo_inputs — what `octo-freedom`'s walk and rule#1 read, assembled from a LIVE window.

ONE JOB: given a `BiasWindow` built from DB klines, produce the arrays and readers the walk and rule#1
need, built the way the backtest builds them - `sweep_v3_signal.Rig` and `report_leash_walk.main()` -
so the live decision and the acceptance test read the same numbers. It decides nothing, steps nothing
and trades nothing.

WHY A SEPARATE MODULE. The backtest assembles these from the line CACHE (`Rig`); o9-live has no cache
(Joe 1001: *"I'm expecting o9-live + fakeAPI to run on live tape - no caches"*). The recipes are
copied here from those two files, not re-derived, and the 09-01 replay
(`docs/octo-freedom/1002_live_producer/replay_0901.py`) holds the two against each other bar for bar.

THE LINES. 12 of the 31 lines the walk and rule#1 read are not in `vw_indicator_configs_live`
(ws11r-ws21r except ws15r, plus ws23r and ws13m), so `BiasWindow.line(name)` cannot build them by
name. The backtest builds every ws line from the role recipe `override(tf * 60, *spec[role])` with
`spec` from `mech_lines(db, 'wsf')` (`report_coil_exit.py:39-50`, `build_wsf_trades.py:96-103`).
`line_overrides` builds the same dict for `BiasWindow(line_overrides=...)`. The gcws30 lines are
read by name, as the backtest reads them through the Jig.

Measured 1001 (`docs/octo-freedom/1001_rebuild_timing.md`): built this way over 104 h, the lines
match the backtest's to <= 8.5e-14 on the k role and <= 2.0e-07 on the bb role, 0 NaN mismatches.

THE KNOBS, AND WHERE EACH COMES FROM - the same sources the backtest reads, no literal duplicated:
    wsf_trade_config v4 (TC.WALK_V)   the walk's knobs, `walk_rule1_back_min`, `walk_dr_*`
    wsf_trade_config v3 (TC.V)        rule#1's fence/oob/div_tf and rig.DRW's latch, via Rig.Ct
    wsf_dtf_v3_config (v3_config)     block, dwell_min_per_tf, coil_lines, sig_line, lookback_s,
                                      dwell, rev_wob, boundary_xwob, momo_fence_r
    lr_config                         ws1mage-rev's boundary, 85/15 (`report_coil_exit.py:71`)
    momo_config v1                    the momentum banks, per timeframe
The hardcoded ones are the backtest's own and are named where used: flat-run samples 3 and
tolerance 2.0 (`report_leash_walk.py:73-74`), `mid=50.0` in rule#1's anchor_floater
(`sweep_v3_signal.py:185`), `walk_mom_models.WS1_CFG`.
"""
import numpy as np

from optimus9.compute import trade_config as TC
from optimus9.compute.dr_latch import latch, latch_wob
from optimus9.compute.line_config import mech_lines, override
from optimus9.compute.momo_config import momo_bank
from optimus9.compute.momo_seam import seam_mask
from optimus9.compute.rule1_gate import gate
from optimus9.compute.stretchy_leash import coil as leash_coil
from optimus9.compute.test_points import flat_run_at
from optimus9.compute.v3_config import v3_config

FR_SAMPLES = 3       # flat_run_at's sample count - report_leash_walk.py:73, the validated run's
FR_TOL = 2.0         # flat_run_at's tolerance, r points - report_leash_walk.py:74
AF_MID = 50.0        # anchor_floater's mid - sweep_v3_signal.py:185


class OctoConfig:
    """Every knob, read once. Values are cast here so a caller never re-parses a config string."""

    def __init__(self, db):
        from optimus9.analysis.lr import lr_config
        self.walk = TC.load(db, TC.WALK_V)                      # v4
        self.trade = TC.load(db, TC.V)                          # v3 - what Rig.Ct is
        self.C = v3_config(db)                                  # Rig.C
        lr = lr_config(db)
        self.rev_hi, self.rev_lo = float(lr.hi), float(lr.lo)   # report_coil_exit.py:71
        w = self.walk
        self.ladder = list(range(int(w['walk_ladder_lo']), int(w['walk_ladder_hi']) + 1))
        self.knobs = dict(arm_fence=(float(w['arm_fence_lo']), float(w['arm_fence_hi'])),
                          arm_wob=int(w['arm_wob']), min_tf=int(w['walk_min_tf']),
                          fall=int(w['walk_fall']), race=int(w['walk_race']),
                          frmin=int(w['walk_frmin']), lb_bars=int(w['walk_lb_bars']),
                          rev_lookback=int(self.C['lookback_s']) // 5)
        self.r1_back = int(float(w['walk_rule1_back_min']) * 60 / 5)     # 5.0 min = 60 bars
        self.mae_cap = float(w['mae_cap'])
        self.arm_line = str(w['arm_line'])                                # ws5Mage
        if int(w['walk_dr_wob']) != 0:
            raise ValueError('walk_dr_wob is %s but the walk dr is latch() with no wob - the same '
                             'guard as report_leash_walk.py' % w['walk_dr_wob'])
        self.dr_a, self.dr_b = str(w['walk_dr_line_a']), str(w['walk_dr_line_b'])   # ws1Mage, ws13m
        self.dr_hi, self.dr_lo = float(w['walk_dr_fence_hi']), float(w['walk_dr_fence_lo'])
        mfr = float(self.C['momo_fence_r'])
        self.momo_fence = (mfr, 100.0 - mfr)                              # 17/83
        t = self.trade
        self.latch_tf = int(t['latch_tf'])
        self.div_tf = int(t['div_tf'])
        self.BK = {tf: momo_bank(db, tf, version=1) for tf in self.ladder}
        self.overrides = line_overrides(db, self)

    def names(self):
        """Every line the walk and rule#1 read, as BiasWindow names."""
        cl = [str(x) for x in self.C['coil_lines']]
        out = ['ws%dr' % t for t in sorted(set(self.ladder) | {1, 2, 3})]
        out += [self.arm_line, self.dr_a, self.dr_b, 'ws%dx' % (self.div_tf + 1),
                'ws%dm' % self.latch_tf]
        for c in cl:
            out += [c + 'm', c + 'Mage', c + 'r']
        out.append(str(self.C['sig_line']))
        return list(dict.fromkeys(out))


def line_overrides(db, cfg):
    """{name: (tf_seconds, cfg_tuple, value_mode)} for every ws line, from the backtest cache's recipe."""
    spec = {}
    for g in mech_lines(db, 'wsf'):
        if g['role'] not in spec:
            _t, s_, m_ = g['override']
            spec[g['role']] = (s_, m_)
    ovr = {}
    for n in cfg.names():
        if not n.startswith('ws'):
            continue                                            # gcws30*: read by name, as the Jig does
        tf, role = _split(n)
        ovr[n] = override(tf * 60, *spec[role])
    return ovr


def _split(name):
    """'ws23r' -> (23, 'r'); 'ws5Mage' -> (5, 'Mage'); 'ws2x' -> (2, 'x')."""
    s = name[2:]
    i = 0
    while i < len(s) and s[i].isdigit():
        i += 1
    return int(s[:i]), s[i:]


class Inputs:
    """The arrays of ONE window, on its own bar grid. Built once per window; read by the stepper."""

    def __init__(self, W, cfg):
        from optimus9.analysis.jig import ws1mage_rev
        from optimus9.compute.leash_walk import rev_lookback_mask
        self.cfg = cfg
        self.ts = np.asarray(W.ts, np.int64)
        n = len(self.ts)
        self.n = n
        L = lambda nm: np.asarray(W.line(nm), float)              # noqa: E731
        self.mage = L(cfg.arm_line)
        # the walk's dr: the v4 walk_dr_* recipe, as report_leash_walk.py:131-135 rebuilds it
        self.DR = np.asarray(latch(L(cfg.dr_a), L(cfg.dr_b), 0, n - 1, hi=cfg.dr_hi, lo=cfg.dr_lo),
                             np.int8)
        # rule#1's dr: Rig.DRW, sweep_v3_signal.py:107-109
        t = cfg.trade
        self.DRW = latch_wob(L('ws1Mage'), L('ws%dm' % cfg.latch_tf), 0, n - 1,
                             wob=int(t['latch_wob']), hi=float(t['mage_fence_hi']),
                             lo=float(t['mage_fence_lo']))
        # the combined coil, unsigned: Rig.CC, sweep_v3_signal.py:134-136
        self.CC = np.sum(np.vstack([leash_coil(L(c + 'm'), L(c + 'Mage'), L(c + 'r'), 1)
                                    for c in [str(x) for x in cfg.C['coil_lines']]]), axis=0)
        self.RL = {t_: L('ws%dr' % t_) for t_ in cfg.ladder}
        self.SM = {t_: seam_mask(self.ts, t_) for t_ in cfg.ladder}
        C = cfg.C
        legs = ws1mage_rev(L('ws1Mage'), L(str(C['sig_line'])), cfg.rev_hi, cfg.rev_lo,
                           dwell=int(C['dwell']), rev_wob=int(C['rev_wob']),
                           hold=int(C['boundary_xwob']))
        self.rev = {d: rev_lookback_mask(legs[d]['sig'], legs[d]['sig_conf'], n,
                                         cfg.knobs['rev_lookback']) for d in (1, -1)}
        # rule#1's lines: build_wsf_trades.load, the same seven
        self.r1, self.r2, self.r3 = L('ws1r'), L('ws2r'), L('ws3r')
        self.g30r = L('gcws30r')
        self.xn = L('ws%dx' % (cfg.div_tf + 1))
        px = np.asarray(W.px, float)
        good = np.isfinite(px)
        if not good.all():                                      # build_wsf_trades.py:126-129
            px = np.interp(np.arange(len(px)), np.flatnonzero(good), px[good])
        self.px = px
        self._mom, self._fr, self._gate = {}, {}, {}

    def mom_at(self, t, k, d):
        """report_leash_walk.mom_at - is timeframe `t` momentum-true at `k` on dr `d`."""
        ck = (t, k, d)
        if ck not in self._mom:
            import walk_mom_models as W_
            self._mom[ck] = bool(W_.momentum_true(self.RL[t], self.cfg.BK[t], W_.WS1_CFG, d, k,
                                                  self.SM[t], t,
                                                  strip_mom_at_fence=self.cfg.momo_fence)[0])
        return self._mom[ck]

    def fr_at(self, t, k, d):
        """report_leash_walk.fr_at - is timeframe `t` in a complete flat run at `k` on dr `d`."""
        ck = (t, k, d)
        if ck not in self._fr:
            self._fr[ck] = flat_run_at(self.RL[t], k, d, self.cfg.momo_fence, FR_SAMPLES,
                                       FR_TOL) is not None
        return self._fr[ck]

    def gate_open(self, k, back_bars):
        """rule#1 at `k` - Rig.gate_open, sweep_v3_signal.py:172-196, on this window's arrays."""
        from optimus9.analysis.jig import anchor_floater
        ck = (int(k), int(back_bars))
        if ck not in self._gate:
            cfg, C, t = self.cfg, self.cfg.C, self.cfg.trade
            d = int(self.DRW[k])
            res = anchor_floater(self.r1, self.px, d, k, block=int(C['block']), mid=AF_MID,
                                 xn=self.xn,
                                 dwell_bars=cfg.div_tf * int(C['dwell_min_per_tf']) * 12,
                                 oob=(float(t['oob_lo']), float(t['oob_hi'])))
            self._gate[ck] = bool(gate(
                self.r1, self.r2, self.r3, self.g30r, d, k, int(back_bars),
                (float(t['rule1_fence_lo']), float(t['rule1_fence_hi'])),
                (float(t['oob_lo']), float(t['oob_hi'])),
                0 if res is None else int(res['fired']),
                fwd_bars=int(float(t['rule1_fwd_min']) * 60 / 5),
                run_clamp=t['rule1_run_clamp'])['open'])
        return self._gate[ck]
