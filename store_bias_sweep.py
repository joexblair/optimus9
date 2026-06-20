"""
store_bias_sweep.py — persist the floater×verdict×g_gated sweep into bias_config/bias_eval/
bias_pk_results as the current/live snapshot (Joe 0620). All 8 configs stored live_after=now
(holding pattern — no single winner promoted yet). Entry seq/m, osc s12m, gate s14M-OOB.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
import bias_machine as bm
from bias_results import BiasResults, engine_rev

H = bm.H; MAE, TARGET = 0.4, 0.9
def ms2dt(ms): return dtm.datetime.fromtimestamp(ms / 1000, timezone.utc).replace(tzinfo=None)
CFGS = [(fa, vd, gg) for fa in ('same', 'last') for vd in ('magnitude', 'pk') for gg in (False, True)]
BASE = dict(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False)

db = DatabaseManager(**get_db_config()); db.connect()
for t in ('bias_pk_results', 'bias_eval', 'bias_config'):     # fresh initial build (children first for FKs)
    db.execute(f'DROP TABLE IF EXISTS {t}')
br = BiasResults(db); br.ensure_tables()
now = dtm.datetime.now(timezone.utc).replace(tzinfo=None); rev = engine_rev()

# 8 config rows (live_after=now → all current; promotion of one live stream is deferred)
cfg_pk = {}
for fa, vd, gg in CFGS:
    cfg = bm.BiasConfig(floater_anchor=fa, verdict=vd, g_gated=gg, **BASE)
    cfg_pk[(fa, vd, gg)] = br.config_pk(cfg, created=now, live_after=now)
print(f'configs: {len(set(cfg_pk.values()))} rows · engine_rev {rev}')

det = BLDetect(db, lookback_hours=168, warmup_hours=80); tp = det._tp
rng = db.execute(f'SELECT MIN(kc_timestamp) mn, MAX(kc_timestamp) mx FROM kline_collection WHERE kc_tp_pk={tp}', fetch=True)[0]
earliest, latest = int(rng['mn']), int(rng['mx'])
ends = []; e = latest
while e - (168 + 80) * H >= earliest:
    ends.append(e); e -= 120 * H
ends.reverse()

db2 = DatabaseManager(**get_db_config()); db2.connect()
n_eval = 0
for wi, end in enumerate(ends):
    W = bm.BiasWindow(db2, end, cfg=bm.BiasConfig(**BASE))
    trigs = W.trigs(12)
    w0, w1 = ms2dt(W.W0), ms2dt(W.W1)
    for fa, vd, gg in CFGS:
        events = W.pk_events(trigs, 'oob', 2, fa, gg)
        calls = W.verdict_pk(events, 0.0, 0) if vd == 'pk' else W.verdict_magnitude(events)
        pls = W.placements(calls, MAE, TARGET)
        eval_pk = br.write_eval(cfg_pk[(fa, vd, gg)], w0, w1, now, rev)
        br.write_pk_result(eval_pk, sum(p['hit'] for p in pls), len(pls))
        n_eval += 1
    print(f'  window {wi+1}/{len(ends)} → {w1:%m%d} stored')
db2.disconnect()

print(f'\nstored: {n_eval} evals + results across {len(ends)} windows')
# rolled rate per config straight from the tables (proves the read path)
rows = db.execute('''SELECT c.floater_anchor, c.verdict, c.g_gated,
    SUM(r.res_correct) cc, SUM(r.res_total) nn
    FROM bias_config c JOIN bias_eval e ON e.eval_cfg_pk=c.cfg_pk
    JOIN bias_pk_results r ON r.res_eval_pk=e.eval_pk
    GROUP BY c.cfg_pk ORDER BY SUM(r.res_correct)/SUM(r.res_total) DESC''', fetch=True)
print('\nrolled from tables:')
for r in rows:
    print(f"  {r['floater_anchor']:>4} {r['verdict']:>9} g{r['g_gated']} | {r['cc']/r['nn']:.0%} ({r['cc']}/{r['nn']})")
db.disconnect()
