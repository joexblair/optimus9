"""
bias_grav_sweep.py (Joe 0701) — sweep the 3 hb33 bro-cross sets to dial the bias against the OG BOOK.
og_book = the 266 v2 entries scored by the OLD s7-curl exit (lr_exit exit_on=s30a_s15a, 75% win). Metric (b):
the bias rejects AGAINST-grain entries (bias == −bd), the kept set's WIN + NET on og_book is the score.
Grid (84,700): TF(9..36) × mage-len(19±5) × min-len(13±5) × hbhl33 mage-src(5) × min-src(5). TF/lens shared
across all 3 sets; sources sweep hbhl33 only (hblo33=low/low, hbhi33=high/high). Reuses bro_stream/bro_verdict
(SRP split). MODE: 'test' (timed sample + top-8) · 'full' (all → hb33_sweep table). Resamples precompute per TF.
"""
import sys, time, bisect, itertools; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np, datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.analysis.lr import lr_config, lr_exit
from optimus9.analysis.lr_v2 import v2_walk
from optimus9.analysis.bias_state import bro_stream, bro_verdict


def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)


MODE = sys.argv[1] if len(sys.argv) > 1 else 'test'
db = DatabaseManager(**get_db_config()); db.connect()
cfg = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                    mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
W = bm.BiasWindow(db, ms('2026-06-22 00:00'), cfg=cfg); lrcfg = lr_config(db)
base = W.base; ts = np.array(W.ts); n = len(ts)

ent = [e for e in v2_walk(W, lrcfg) if e[0] >= ms('2026-06-17 00:00')]
ogx = {x[0]: x[5] for x in lr_exit(W, ent, lrcfg, curl_fam='s7', exit_on='s30a_s15a', predict_gate=True, arm_gate=True)}
ent_bd = [(e[3], e[2], ogx[e[0]]) for e in ent]                 # (entry_k, bd, og_ret)
base_net = sum(r for _, _, r in ent_bd); base_win = 100.0 * np.mean([r > 0 for _, _, r in ent_bd])

N = int(db.execute("SELECT val FROM lp_config WHERE name='lp_bro_wob'", fetch=True)[0]['val'])
sysr = db.execute('SELECT hi_boundary, lo_boundary FROM optimus9_system', fetch=True)[0]
HI, LO = float(sysr['hi_boundary']), float(sysr['lo_boundary'])

TFs = list(range(9, 37))                                        # 28
LEN_M = [19 + d for d in range(-5, 6)]                          # mage 19 ±5 → 11
LEN_m = [13 + d for d in range(-5, 6)]                          # min 13 ±5 → 11
SRCS = ['close', 'ohlc4', 'hl2', 'hlc3', 'high']               # 5 (hbhl33)
M_MULT, m_MULT = 0.64, 0.68
resamples = {tf: IC.resample(base, tf * 60, 'midnight') for tf in TFs}


def bbline(fr, src, blen, mult):
    return IC.align_to_base(IC.f_bb(IC.build_source(fr, src), blen, mult), fr, base)


def one_combo(tf, lenM, lenm, magesrc, minsrc):
    fr = resamples[tf]; streams = []
    for st, msrc, Msrc in (('hbhl33', minsrc, magesrc), ('hblo33', 'low', 'low'), ('hbhi33', 'high', 'high')):
        M = bbline(fr, Msrc, lenM, M_MULT); m = bbline(fr, msrc, lenm, m_MULT)
        streams.append(bro_stream(ts, m, M, st))
    flips = bro_verdict(streams, N, HI, LO, cluster_min=30, require_oob=True)
    ft = [f['t'] for f in flips]; fd = [f['dir'] for f in flips]
    net = 0.0; wins = kept = 0
    for k, bd, r in ent_bd:
        j = bisect.bisect_right(ft, int(ts[k])) - 1
        if (fd[j] if j >= 0 else 0) != -bd:                    # keep with-grain + neutral; reject against
            net += r; wins += (r > 0); kept += 1
    return net, (100.0 * wins / kept if kept else 0.0), kept


combos = list(itertools.product(TFs, LEN_M, LEN_m, SRCS, SRCS))
print('grid=%d · og_book baseline (keep all): net=%+.1f%% win=%.0f%% n=%d' % (len(combos), base_net, base_win, len(ent_bd)))

if MODE == 'test':
    t0 = time.time(); res = []
    for c in combos:
        res.append((c,) + one_combo(*c))
        if time.time() - t0 > 60:
            break
    el = time.time() - t0; rate = len(res) / el
    print('TIMED %d combos in %.0fs → %.1f/s → FULL %d = %.1f min' % (len(res), el, rate, len(combos), len(combos) / rate / 60))
    res.sort(key=lambda x: -x[1])
    print('top 8 of the sample by net:')
    for c, net, win, kept in res[:8]:
        print('  TF%-2d lenM%-2d lenm%-2d Msrc=%-5s msrc=%-5s | net=%+.1f%% win=%.0f%% kept=%d' % (*c, net, win, kept))
else:
    db.execute('DROP TABLE IF EXISTS hb33_sweep')
    db.execute('CREATE TABLE hb33_sweep (tf INT, len_mage INT, len_min INT, mage_src VARCHAR(8), min_src VARCHAR(8), net FLOAT, avg_ret FLOAT, win FLOAT, kept INT)')
    t0 = time.time(); buf = []
    for i, c in enumerate(combos):
        net, win, kept = one_combo(*c)
        buf.append((*c, round(net, 3), round(net / kept if kept else 0, 4), round(win, 2), kept))
        if len(buf) >= 2000:
            db.executemany('INSERT INTO hb33_sweep VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)', buf); buf = []
        if i % 20000 == 0:
            print('  %d/%d (%.0fs)' % (i, len(combos), time.time() - t0))
    if buf:
        db.executemany('INSERT INTO hb33_sweep VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)', buf)
    print('DONE %d combos in %.1f min → hb33_sweep · baseline net=%+.1f avg=%+.3f win=%.0f n=266'
          % (len(combos), (time.time() - t0) / 60, base_net, base_net / 266, base_win))
    print('top 12 by avg_ret (kept>=120):')
    for r in db.execute('SELECT * FROM hb33_sweep WHERE kept>=120 ORDER BY avg_ret DESC LIMIT 12', fetch=True):
        print('  ', r)
db.disconnect()
