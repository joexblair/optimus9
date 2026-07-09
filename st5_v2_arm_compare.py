"""st5_v2_arm_compare.py (Joe 0706) — reproduce the >10K baseline: s5m arm vs s5Mage@5min vs st5Mage@10min.

Same build_v2_walk pipeline/window (R1_END=now, default lookback ~10d), in-memory (no table clobber). Varies
the ARM (arm_mode / arm_line) + the stop (0.7 current, 0.4). Confirms whether the loss is arm-specific (s5Mage
family) vs the s5m shipping arm's >10K.
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
db = DatabaseManager(**get_db_config()); db.connect()
db.execute('UPDATE indicator_timeframes SET itf_seconds=600 WHERE itf_pk=27')       # st5 @10min
END = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
BCFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                     mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
W = bm.BiasWindow(db, END, cfg=BCFG)                                                 # default lookback (build_v2_walk)
lrcfg = lr_config(db)
span = (int(W.ts[-1]) - int(W.ts[0])) / 86400000.0


def equity(resc):
    acct = START; wins = 0
    for (tms, exms, bd, epx, xpx, r, reason) in resc:
        lot = min(MAX_LOT, acct * LEV / float(epx)); acct += lot * float(epx) * (r - RT_COST) / 100.0
        wins += (r - RT_COST) > 0
    return acct, 100 * wins / max(len(resc), 1)


ARMS = [('s5m  (shipping)', 's5m', 's5M'), ('s5Mage@5min', 's5Mage', 's5M'),
        ('s3Mage@3min', 's5Mage', 's3M'), ('st5Mage@10min', 's5Mage', 'st5M')]
print('v2 walk arm A/B — window %.1fd, dynamic-5x, %.2f%% RT  (canonical lp_lr_sl=0.7)\n' % (span, RT_COST))
print('%-18s %5s %7s %10s %8s %6s' % ('arm', 'SL', 'n', 'final$', 'x', 'win%'))
for name, mode, line in ARMS:
    lrcfg.arm_mode = mode; lrcfg.arm_line = line
    ent = v2_walk(W, lrcfg)
    for sl in (0.7, 0.4):
        lrcfg.sl = sl
        resc = strand_rescue(W, lrcfg, ent, lr_exit_v2(W, lrcfg, ent, predict=False))
        acct, win = equity(sorted(resc, key=lambda x: x[0]))
        print('%-18s %5.2f %7d %10.0f %7.1fx %5.0f%%' % (name, sl, len(resc), acct, acct / START, win))
db.disconnect()
