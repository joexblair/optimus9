"""
lr_v2_exit_ab.py (Joe 0630, #45 exit half) — AB the exit decisions over the v2 entries:
  s5m multi (0.4/0.65) × curl_fam (s5/s6/s7/s8) × exit_on (curl/s30a/s30a_s15a) × predict_gate (on/off).
Metric = SL'd return (lr_exit has the −sl floor): avg ret%, win%, n, net. Ranked. Restores s5m=0.65 after.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np, datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config, lr_exit
from optimus9.analysis.lr_v2 import v2_walk


def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)


db = DatabaseManager(**get_db_config()); db.connect()
cfg = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                    mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
R1 = ms('2026-06-22 00:00'); START = ms('2026-06-17 00:00')
pk = db.execute("SELECT ic_pk FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name='s5m'", fetch=True)[0]['ic_pk']
rows = []
for mult in (0.40, 0.65):
    db.execute('UPDATE indicator_configs SET ic_bb_mult=%s WHERE ic_pk=%s', (mult, pk))
    W = bm.BiasWindow(db, R1, cfg=cfg); lrcfg = lr_config(db)
    ent = [e for e in v2_walk(W, lrcfg, stale_exit=False) if e[0] >= START]
    for cf in ('s5', 's6', 's7', 's8'):
        for eo in ('curl', 's30a', 's30a_s15a'):
            for pg in (True, False):
                ex = lr_exit(W, ent, lrcfg, curl_fam=cf, exit_on=eo, predict_gate=pg)
                r = np.array([x[5] for x in ex]) if ex else np.array([0.0])
                rows.append((mult, cf, eo, pg, len(ex), float(r.mean()), float((r > 0).mean() * 100), float(r.sum())))
db.execute('UPDATE indicator_configs SET ic_bb_mult=0.65 WHERE ic_pk=%s', (pk,))   # restore the tested value
print('TOP 14 by avg ret% (SL-floored):')
for r in sorted(rows, key=lambda x: -x[5])[:14]:
    print(f'  m{r[0]:.2f} {r[1]} {r[2]:<11} pg={r[3]!s:5} | n={r[4]:3} avg={r[5]:+.3f}% win={r[6]:3.0f}% net={r[7]:+6.1f}%')
print('multi verdict — same config, 0.4 vs 0.65 (s7·s30a_s15a·pg=on):')
for mult in (0.40, 0.65):
    r = [x for x in rows if x[:4] == (mult, 's7', 's30a_s15a', True)][0]
    print(f'  m{mult:.2f}: n={r[4]} avg={r[5]:+.3f}% win={r[6]:.0f}% net={r[7]:+.1f}%')
db.disconnect()
