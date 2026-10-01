"""time_rebuild — what ONE stateless 104 h rebuild costs, the per-bar work `OPEN.md`'s bounded re-walk
ruling implies. Joe 1001: *"go for it"*, on timing one 104 h rebuild before choosing between the
re-walk and an evolving cache.

TWO PARTS, because the rebuild is two kinds of work:

  lines   build a fresh 104 h `BiasWindow` (lookback 24 h + warmup 80 h, `strategy.py:23` defaults)
          ending at a 09-01 bar, then every line octo-freedom reads. Done at 3 consecutive bars, each
          a fresh window, as the live loop would. The ws lines are built from the SAME role recipe the
          backtest cache uses - `override(tf * 60, *spec[role])`, spec from `mech_lines(db, 'wsf')`
          (`report_coil_exit.py:39-50`, `build_wsf_trades.py:96-103`) - because 12 of them are not in
          `vw_indicator_configs_live` and cannot be built by name. gcws30 lines are read by name, as
          the backtest does through the Jig.
  walk    re-run `leash_walk.walk` and rule#1 (`gate_open(k, 60)`) over the last 104 h ending
          2026-09-01 23:59:55, on the backtest's own arrays, with every memo cold. Same code and sizes
          a stateless re-walk would run each bar; the line build is excluded here and timed above.

Reads only. Writes nothing to the DB or the repo.

    python3 time_rebuild.py lines
    python3 time_rebuild.py walk
"""
import datetime as dt
import io
import json
import sys
import time

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')

END_UTC = dt.datetime(2026, 9, 1, 12, 0, 0, tzinfo=dt.timezone.utc)
LOOKBACK_H, WARMUP_H = 24, 80                     # strategy.py:23 defaults = 104 h, Joe 1001 approved


def lines():
    import bias_machine as bm
    from sweep_eval import BASE_BIAS
    from optimus9.config import get_db_config
    from optimus9.db.database_manager import DatabaseManager
    from optimus9.compute.line_config import override, mech_lines

    db = DatabaseManager(**get_db_config()); db.connect()
    spec = {}
    for g in mech_lines(db, 'wsf'):
        if g['role'] not in spec:
            _t, s_, m_ = g['override']
            spec[g['role']] = (s_, m_)
    ovr = {}
    for t in range(1, 24):
        ovr['ws%dr' % t] = override(t * 60, *spec['r'])
    for t in (1, 5):
        ovr['ws%dMage' % t] = override(t * 60, *spec['Mage'])
    for t in (1, 13):
        ovr['ws%dm' % t] = override(t * 60, *spec['m'])
    ovr['ws2x'] = override(2 * 60, *spec['x'])
    names = list(ovr) + ['gcws30m', 'gcws30Mage', 'gcws30r']
    bcfg = bm.BiasConfig(**BASE_BIAS)
    end0 = int(END_UTC.timestamp() * 1000)
    out = []
    for i in range(3):
        end = end0 + i * 5000
        t0 = time.perf_counter()
        W = bm.BiasWindow(db, end, lookback=LOOKBACK_H, warmup=WARMUP_H, cfg=bcfg,
                          line_overrides=ovr, lean=True)
        t_win = time.perf_counter() - t0
        per = {}
        for n in names:
            a = time.perf_counter()
            v = np.asarray(W.line(n), float)
            per[n] = round(time.perf_counter() - a, 3)
            assert len(v) == len(W.ts), n
        tot = time.perf_counter() - t0
        out.append(dict(bar=i, end_utc=dt.datetime.fromtimestamp(end / 1000, dt.timezone.utc)
                        .strftime('%Y-%m-%d %H:%M:%S'), bars=len(W.ts), window_s=round(t_win, 3),
                        lines_s=round(tot - t_win, 3), total_s=round(tot, 3), n_lines=len(names),
                        per_line_s=per))
        print(json.dumps(out[-1]), flush=True)
    db.disconnect()


def walk():
    import optimus9.orchestration.build_ws_lines as BWL
    ve = dt.datetime(2026, 9, 8, 0, 0, tzinfo=dt.timezone.utc)
    BWL.TAPE_END = ve
    BWL.END_MS = int(ve.timestamp() * 1000)
    for m in [k for k in list(sys.modules) if k in ('report_coil_exit', 'sweep_v3_signal',
                                                       'measure_live_stop', 'build_wsf_trades')]:
        del sys.modules[m]
    _e, sys.stderr = sys.stderr, io.StringIO()
    import sweep_v3_signal as S
    sys.stderr = _e
    import walk_mom_models as W
    from optimus9.analysis.jig import ws1mage_rev
    from optimus9.compute import trade_config as TC
    from optimus9.compute.leash_walk import rev_lookback_mask, walk as lwalk
    from optimus9.compute.momo_seam import seam_mask
    from optimus9.compute.test_points import flat_run_at
    from optimus9.config import get_db_config
    from optimus9.db.database_manager import DatabaseManager

    ms0 = int(dt.datetime(2026, 9, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
    rig = S.Rig((ms0, ms0 + 86400000))
    ts = np.asarray(rig.ts, np.int64)
    k1 = int(np.searchsorted(ts, ms0 + 86400000)) - 1
    span = (LOOKBACK_H + WARMUP_H) * 3600 // 5
    k0 = k1 - span + 1
    db = DatabaseManager(**get_db_config()); db.connect()
    cfg = TC.load(db, TC.WALK_V); db.disconnect()
    lad = list(range(int(cfg['walk_ladder_lo']), int(cfg['walk_ladder_hi']) + 1))
    knobs = dict(arm_fence=(float(cfg['arm_fence_lo']), float(cfg['arm_fence_hi'])),
                 arm_wob=int(cfg['arm_wob']), min_tf=int(cfg['walk_min_tf']),
                 fall=int(cfg['walk_fall']), race=int(cfg['walk_race']),
                 frmin=int(cfg['walk_frmin']), lb_bars=int(cfg['walk_lb_bars']),
                 rev_lookback=int(rig.C['lookback_s']) // 5)
    r1_back = int(float(cfg['walk_rule1_back_min']) * 60 / 5)
    mfr = float(rig.C['momo_fence_r']); fence = (mfr, 100.0 - mfr)
    mage = np.asarray(rig.lines[str(cfg['arm_line']).replace('Mage', '')]['Mage'], float)
    RL = {t: np.asarray(rig.lines['ws%d' % t]['r'], float) for t in lad}
    SM = {t: seam_mask(rig.ts, t) for t in lad}
    _mom, _fr = {}, {}

    def mom_at(t, k, d):
        ck = (t, k, d)
        if ck not in _mom:
            _mom[ck] = bool(W.momentum_true(RL[t], rig.BK[t], W.WS1_CFG, d, k, SM[t], t,
                                            strip_mom_at_fence=fence)[0])
        return _mom[ck]

    def fr_at(t, k, d):
        ck = (t, k, d)
        if ck not in _fr:
            _fr[ck] = flat_run_at(RL[t], k, d, fence, 3, 2.0) is not None
        return _fr[ck]

    t0 = time.perf_counter()
    legs = ws1mage_rev(rig.lines['ws1']['Mage'],
                       rig.lines[rig.C['sig_line'].replace('Mage', '')]['Mage'], rig.hi, rig.lo,
                       dwell=int(rig.C['dwell']), rev_wob=int(rig.C['rev_wob']),
                       hold=int(rig.C['boundary_xwob']))
    rev = {d: rev_lookback_mask(legs[d]['sig'], legs[d]['sig_conf'], rig.n, knobs['rev_lookback'])
           for d in (1, -1)}
    t_rev = time.perf_counter() - t0
    t1 = time.perf_counter()
    mech, _ = lwalk(lad, mage, rig.DR, rig.CC, mom_at, fr_at, rev, k0, k1, **knobs)
    t_walk = time.perf_counter() - t1
    rig._gate = {}
    t2 = time.perf_counter()
    emit = [k for k in mech if rig.gate_open(k, r1_back)]
    t_gate = time.perf_counter() - t2
    print(json.dumps(dict(span_bars=span, span_h=span * 5 / 3600, from_utc=str(dt.datetime.fromtimestamp(
        int(ts[k0]) / 1000, dt.timezone.utc)), to_utc=str(dt.datetime.fromtimestamp(
        int(ts[k1]) / 1000, dt.timezone.utc)), rev_legs_s=round(t_rev, 3), walk_s=round(t_walk, 3),
        gate_s=round(t_gate, 3), total_s=round(t_rev + t_walk + t_gate, 3), mech=len(mech),
        emitted=len(emit), momentum_true_calls=len(_mom), flat_run_at_calls=len(_fr),
        walk_s_per_bar_stepped=round(t_walk / span, 6))), flush=True)

    # --- is the timed line build the backtest's line build? ------------------------------------
    # The `lines` timing is only worth quoting if its lines are the ones the walk reads. Rebuild the
    # same 104 h window ending 09-01 12:00 the same way and compare its last hour against the rig.
    _check(rig)


def _check(rig):
    import bias_machine as bm
    from sweep_eval import BASE_BIAS
    from optimus9.config import get_db_config
    from optimus9.db.database_manager import DatabaseManager
    from optimus9.compute.line_config import override, mech_lines
    db = DatabaseManager(**get_db_config()); db.connect()
    spec = {}
    for g in mech_lines(db, 'wsf'):
        if g['role'] not in spec:
            _t, s_, m_ = g['override']
            spec[g['role']] = (s_, m_)
    ovr = {'ws%dr' % t: override(t * 60, *spec['r']) for t in range(1, 24)}
    ovr.update({'ws1Mage': override(60, *spec['Mage']), 'ws5Mage': override(300, *spec['Mage']),
                'ws1m': override(60, *spec['m']), 'ws13m': override(780, *spec['m']),
                'ws2x': override(120, *spec['x'])})
    end = int(END_UTC.timestamp() * 1000)
    Wn = bm.BiasWindow(db, end, lookback=LOOKBACK_H, warmup=WARMUP_H, cfg=bm.BiasConfig(**BASE_BIAS),
                       line_overrides=ovr, lean=True)
    db.disconnect()
    wts = np.asarray(Wn.ts, np.int64)
    rts = np.asarray(rig.ts, np.int64)
    last = wts[-720:]                                     # the window's last hour = 720 bars
    ri = np.searchsorted(rts, last)
    ok = (ri < len(rts)) & (rts[np.clip(ri, 0, len(rts) - 1)] == last)
    ref = {('ws%dr' % t): rig.lines['ws%d' % t]['r'] for t in range(1, 24)}
    ref.update({'ws1Mage': rig.lines['ws1']['Mage'], 'ws5Mage': rig.lines['ws5']['Mage'],
                'ws1m': rig.lines['ws1']['m'], 'ws13m': rig.lines['ws13']['m'], 'ws2x': rig.xn,
                'gcws30m': rig.lines['gcws30']['m'], 'gcws30Mage': rig.lines['gcws30']['Mage'],
                'gcws30r': rig.lines['gcws30']['r']})
    res = {}
    for n, rv in ref.items():
        a = np.asarray(Wn.line(n), float)[-720:][ok]
        b = np.asarray(rv, float)[ri[ok]]
        both = np.isfinite(a) & np.isfinite(b)
        res[n] = dict(max_abs_diff=float(np.max(np.abs(a[both] - b[both]))) if both.any() else None,
                      nan_mismatch=int((np.isfinite(a) != np.isfinite(b)).sum()))
    print(json.dumps(dict(check='timed build vs backtest arrays, last 720 bars to 09-01 12:00',
                          bars_aligned=int(ok.sum()),
                          worst=max((v['max_abs_diff'] or 0.0) for v in res.values()),
                          nan_mismatch_total=sum(v['nan_mismatch'] for v in res.values()),
                          per_line=res)), flush=True)


if __name__ == '__main__':
    {'lines': lines, 'walk': walk}[sys.argv[1]]()
