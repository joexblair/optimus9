"""st5_v2_walk_msweep.py (Joe 0706) — st5Mage@10min v2 walk, multi-window × stop sweep.

build_v2_walk pipeline (v2_walk → lr_exit_v2 predict=False → strand_rescue → dynamic-5x compounding), arm line
= st5M @10min. Entries computed once per window (SL is exit-only), then the stop swept {0.35..0.50}. 5 windows
inside the clean tape (7d lookback each). Reports per-SL: per-window x-multiple + WORST-window + mean + win%/DD.
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
def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)
WINDOW_ENDS = [ms(d) for d in ('2026-06-26 00:00', '2026-06-29 00:00', '2026-07-02 00:00',
                               '2026-07-05 00:00', '2026-07-06 12:00')]
SLS = [0.35, 0.40, 0.45, 0.50]

db = DatabaseManager(**get_db_config()); db.connect()
db.execute('UPDATE indicator_timeframes SET itf_seconds=600 WHERE itf_pk=27')          # st5 @10min
BCFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                     mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
lrcfg = lr_config(db); lrcfg.arm_line = 'st5M'


def equity(resc):
    acct = START; peak = START; maxdd = 0.0; wins = 0
    for (tms, exms, bd, epx, xpx, r, reason) in resc:
        lot = min(MAX_LOT, acct * LEV / float(epx))
        acct += lot * float(epx) * (r - RT_COST) / 100.0
        wins += (r - RT_COST) > 0; peak = max(peak, acct); maxdd = max(maxdd, (peak - acct) / peak * 100.0)
    return acct / START, 100 * wins / max(len(resc), 1), maxdd, len(resc)


res = {sl: [] for sl in SLS}
for wend in WINDOW_ENDS:
    W = bm.BiasWindow(db, wend, cfg=BCFG)                                               # default lookback (~7d, as build_v2_walk)
    ent = v2_walk(W, lrcfg)                                                             # entries: SL-independent
    for sl in SLS:
        lrcfg.sl = sl
        resc = sorted(strand_rescue(W, lrcfg, ent, lr_exit_v2(W, lrcfg, ent, predict=False)), key=lambda x: x[0])
        res[sl].append(equity(resc))
db.disconnect()

wl = [dtm.datetime.utcfromtimestamp(w / 1000).strftime('%m-%d') for w in WINDOW_ENDS]
print('st5Mage@10min v2 walk — multi-window × stop sweep (dynamic-5x, %.2f%% RT)\n' % RT_COST)
print('%-5s %s   %7s %7s %6s' % ('SL', '  '.join('%6s' % w for w in wl), 'WORST', 'mean', 'DD%'))
for sl in SLS:
    xs = [c[0] for c in res[sl]]; dd = sum(c[2] for c in res[sl]) / len(res[sl]); wn = sum(c[1] for c in res[sl]) / len(res[sl])
    print('%-5.2f %s   %6.2fx %6.2fx %5.0f%%  (win %.0f%%)' % (
        sl, '  '.join('%5.2fx' % x for x in xs), min(xs), sum(xs) / len(xs), dd, wn))
