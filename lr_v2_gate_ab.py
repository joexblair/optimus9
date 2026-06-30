"""
lr_v2_gate_ab.py (Joe 0630) — AB the EXIT cascade's gate oscillator: swap s7r → s6r / s5r / s7r+boundary-slip,
× the predict toggle. Over the 266 v2 entries. Metric = SL/exit/win/avg/net AND the CULL count: how many of the
OLD exit's WINNERS (lr_exit, 75%-win small-profit exits) this variant turns into an SL (signal lost = no gate OOB).
Joe will use the per-row culls (next step) to hunt chart signs that forewarn an 'early' exit. slip magnitude is a
KNOB (10 = boundaries 85/15 → 75/25) — tunable.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np, datetime as dtm
from datetime import timezone
from collections import Counter
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config, lr_walk, lr_exit
from optimus9.analysis.lr_v2 import v2_walk, lr_exit_v2


def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)


db = DatabaseManager(**get_db_config()); db.connect()
cfg = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                    mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
W = bm.BiasWindow(db, ms('2026-06-22 00:00'), cfg=cfg); lrcfg = lr_config(db); START = ms('2026-06-17 00:00')
print('live s5/s6/s7:', [r['ind_name'] for r in db.execute(
    "SELECT ind_name FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name REGEXP '^s[567][mMr]$' ORDER BY ind_name", fetch=True)])
ent = [e for e in v2_walk(W, lrcfg) if e[0] >= START]
old = lr_exit(W, ent, lrcfg, curl_fam='s7', exit_on='s30a_s15a', predict_gate=True)   # the 75%-win OLD exit
old_win = {x[0]: x[5] > 0 for x in old}
n_oldwin = sum(old_win.values())
print('entries=%d · OLD exit winners=%d (the "early" small-profit exits to preserve)\n' % (len(ent), n_oldwin))

variants = [('s7r', dict(gate_fam='s7')), ('s6r', dict(gate_fam='s6')), ('s5r', dict(gate_fam='s5')),
            ('s7r+slip10', dict(gate_fam='s7', slip=10.0))]
print('%-12s %-8s | %-22s win  avg     net     | culled(of %d old-win)' % ('gate', 'predict', 'reasons', n_oldwin))
for name, kw in variants:
    for predict in (True, False):
        ex = lr_exit_v2(W, lrcfg, ent, predict=predict, **kw)
        r = np.array([x[5] for x in ex]); rs = dict(Counter(x[6] for x in ex))
        culled = sum(1 for x in ex if old_win.get(x[0]) and x[6] == 'SL')
        print('%-12s %-8s | %-22s %3d%% %+.3f%% %+6.1f%% | %3d (%2d%%)' % (
            name, predict, str(rs), (r > 0).mean() * 100, r.mean(), r.sum(), culled, culled * 100 // max(1, n_oldwin)))
db.disconnect()
