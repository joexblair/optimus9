"""st5_v2_walk.py (Joe 0706) — st5Mage@10min through the v2 walk (PnL), vs the s5Mage@5min baseline.

Mirrors build_v2_walk's shipping pipeline (v2_walk entries → lr_exit_v2 predict=False → strand_rescue →
dynamic-5x compounding equity), swapping only cfg.arm_line ('s5M' vs 'st5M') + itf 27→600s for st5@10min.
In-memory only (does NOT clobber the canonical v2_walk table). Same window build_v2_walk uses (last 7d).
"""
import sys, datetime as dtm
from datetime import timezone
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import v2_walk, lr_exit_v2, strand_rescue

START, LEV, MAX_LOT, RT_COST = 500.0, 5.0, 66000, 0.20
R1_END = dtm.datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')
def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)

db = DatabaseManager(**get_db_config()); db.connect()
BCFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                     mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')


def run(arm_line, itf_secs=None):
    if itf_secs:
        db.execute('UPDATE indicator_timeframes SET itf_seconds=%s WHERE itf_pk=27', (itf_secs,))
    W = bm.BiasWindow(db, ms(R1_END), cfg=BCFG)
    lrcfg = lr_config(db); lrcfg.arm_line = arm_line
    ent = v2_walk(W, lrcfg)
    resc = sorted(strand_rescue(W, lrcfg, ent, lr_exit_v2(W, lrcfg, ent, predict=False)), key=lambda x: x[0])
    acct = START; peak = START; maxdd = 0.0; wins = 0
    for (tms, exms, bd, epx, xpx, r, reason) in resc:
        lot = min(MAX_LOT, acct * LEV / float(epx))
        pnl = lot * float(epx) * (r - RT_COST) / 100.0
        acct += pnl; wins += (r - RT_COST) > 0
        peak = max(peak, acct); maxdd = max(maxdd, (peak - acct) / peak * 100.0)
    n = len(resc)
    return dict(arm=arm_line, n=n, final=acct, x=acct / START, win=100 * wins / max(n, 1), maxdd=maxdd)


base = run('s5M')                 # s5Mage @5min (baseline)
st5 = run('st5M', itf_secs=600)   # st5Mage @10min
db.execute('UPDATE indicator_timeframes SET itf_seconds=600 WHERE itf_pk=27')   # leave st5 at 10min
db.disconnect()

print('v2 walk (dynamic-5x, cost %.2f%% RT, last 7d) — arm-line A/B\n' % RT_COST)
print('%-16s %5s %9s %6s %6s %7s' % ('arm line', 'n', 'final$', 'x', 'win%', 'maxDD%'))
for r in (base, st5):
    lbl = 's5Mage@5min' if r['arm'] == 's5M' else 'st5Mage@10min'
    print('%-16s %5d %9.0f %5.1fx %5.0f%% %6.0f%%' % (lbl, r['n'], r['final'], r['x'], r['win'], r['maxdd']))
