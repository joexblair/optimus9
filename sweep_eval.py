"""
sweep_eval.py (Joe 0701) — the atomic sweep unit: one config + one window → net profit.
SRP: build → walk → exit → score, nothing else. Config is a dict of in-memory overrides (no DB writes, so
16 workers run race-free via BiasWindow.line_overrides). Metric = net-of-cost total % (sum of exit_pct − cost)
— comparable/additive across the equal-length windows; the dynamic-5× equity is a top-N projection, not per-config.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import v2_walk, lr_exit_v2, strand_rescue

BASE_BIAS = dict(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                 mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
RT_COST = 0.20   # % round-trip (est; real from o9-live)


def evaluate(db, end_ms, config, lrcfg=None):
    """config keys (all optional):
        line_overrides {ind_name: (tf_sec, cfg_tuple, value_mode)}  · bias BiasConfig-knob overrides {attr: val}
        lrcfg  {attr: val} (sl, curl_n, exit_rlb, wob_n, …)         · exit {predict, gate_fam, slip}
    Returns (net_of_cost_total%, n_trades, win%). Raises → caller records a NaN (bad combo, not a crash)."""
    bcfg = bm.BiasConfig(**{**BASE_BIAS, **config.get('bias', {})})
    W = bm.BiasWindow(db, end_ms, cfg=bcfg, line_overrides=config.get('line_overrides'))
    lc = lrcfg or lr_config(db)
    for k, v in config.get('lrcfg', {}).items():
        setattr(lc, k, v)
    ent = v2_walk(W, lc)
    ex = config.get('exit', {})
    casc = lr_exit_v2(W, lc, ent, predict=ex.get('predict', False),
                      gate_fam=ex.get('gate_fam', 's7'), slip=ex.get('slip', 0.0))
    resc = strand_rescue(W, lc, ent, casc)
    r = np.array([x[5] for x in resc]) if resc else np.array([])
    if not len(r):
        return 0.0, 0, 0.0
    return float((r - RT_COST).sum()), len(r), float((r > 0).mean() * 100)


if __name__ == '__main__':
    import datetime as dtm; from datetime import timezone
    from optimus9.config import get_db_config
    from optimus9 import DatabaseManager
    def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)
    db = DatabaseManager(**get_db_config()); db.connect()
    net, n, win = evaluate(db, ms('2026-06-22 00:00'), {})
    print('BASELINE (config={}): net-of-cost %+.1f%% · n=%d · win=%.0f%%  (expect ~+108.5%%/555/70%%)' % (net, n, win))
    net2, n2, win2 = evaluate(db, ms('2026-06-22 00:00'), {'lrcfg': {'sl': 0.7}})
    print('SL 0.5→0.7 override:  net-of-cost %+.1f%% · n=%d · win=%.0f%%  (changed=%s)' % (net2, n2, win2, net != net2))
    db.disconnect()
