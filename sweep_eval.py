"""
sweep_eval.py (Joe 0701) — the atomic sweep unit: one config + one window → net profit.
SRP: build → walk → (optional bias filter) → exit → score, nothing else. Config is a dict of in-memory
overrides (no DB writes → 16 workers race-free via BiasWindow.line_overrides). Metric = net-of-cost total %
(sum of exit_pct − cost) — comparable/additive across equal-length windows; the dynamic-5× equity is a top-N
projection, not per-config.
"""
import sys, bisect; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
import bias_machine as bm
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import v2_walk, lr_exit_v2, strand_rescue
from optimus9.analysis.bias_state import bro_stream, bro_verdict

BASE_BIAS = dict(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                 mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
RT_COST = 0.20   # % round-trip (est; real from o9-live)


def _bias_filter(db, W, ent, b):
    """Recompute the 3 hb33 sets with `b` params → bro-cross flips → reject against-grain entries.
    b: {tf, lenM, lenm, multM, multm, srcM, srcm, N, oob}. hblo/hbhi sources stay low/high (Joe: bar those)."""
    base, ts = W.base, np.array(W.ts)
    sysr = db.execute('SELECT hi_boundary, lo_boundary FROM optimus9_system', fetch=True)[0]
    HI, LO = float(sysr['hi_boundary']), float(sysr['lo_boundary'])
    fr = IC.resample(base, b['tf'] * 60, 'midnight')
    def bb(s, l, m): return IC.align_to_base(IC.f_bb(IC.build_source(fr, s), l, m), fr, base)
    st = [bro_stream(ts, bb(b['srcm'], b['lenm'], b['multm']), bb(b['srcM'], b['lenM'], b['multM']), 'hbhl33'),
          bro_stream(ts, bb('low', b['lenm'], b['multm']),  bb('low', b['lenM'], b['multM']),  'hblo33'),
          bro_stream(ts, bb('high', b['lenm'], b['multm']), bb('high', b['lenM'], b['multM']), 'hbhi33')]
    fl = bro_verdict(st, b['N'], HI, LO, 30, b.get('oob', True))
    ft = [f['t'] for f in fl]; fd = [f['dir'] for f in fl]
    def bias(k):
        j = bisect.bisect_right(ft, int(ts[k])) - 1
        return fd[j] if j >= 0 else 0
    return [e for e in ent if bias(e[3]) != -e[2]]


def evaluate(db, end_ms, config, lrcfg=None, base_cache=None):
    """config keys (all optional): line_overrides · bias(BiasConfig knobs) · lrcfg · exit{predict,gate_fam,slip}
    · bias_filter{tf,lenM,lenm,multM,multm,srcM,srcm,N,oob} (None = off). base_cache = (base,ts,px) reuse.
    Returns (net_of_cost_total%, n_trades, win%)."""
    bcfg = bm.BiasConfig(**{**BASE_BIAS, **config.get('bias', {})})
    W = bm.BiasWindow(db, end_ms, cfg=bcfg, line_overrides=config.get('line_overrides'), base_cache=base_cache)
    lc = lrcfg or lr_config(db)
    for k, v in config.get('lrcfg', {}).items():
        setattr(lc, k, v)
    ent = v2_walk(W, lc)
    if config.get('bias_filter'):
        ent = _bias_filter(db, W, ent, config['bias_filter'])
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
    db = DatabaseManager(**get_db_config()); db.connect(); END = ms('2026-06-22 00:00')
    print('baseline (no filter):   net %+.1f%% n=%d win=%.0f%% (expect ~+108.5/555/70)' % evaluate(db, END, {}))
    bf = dict(tf=26, lenM=24, lenm=9, multM=0.64, multm=0.68, srcM='high', srcm='close', N=1, oob=True)
    print('bias-filter (winner):   net %+.1f%% n=%d win=%.0f%% (expect ~higher/-half n)' % evaluate(db, END, {'bias_filter': bf}))
    db.disconnect()
