"""
sweep_run.py (Joe 0701) — the extreme sweep. Overlapping-subset (covering) blocks over the ACTIVE configs
(line space DERIVED from what the stack actually fetches), each config scored on 7 windows by WORST-window net
(minimax). 14-core parallel, checkpointed to `sweep_results` (resumable/crash-safe). MODE: 'smoke' | 'full'.
Windows tile 05-18→06-24, 7-day each, 2-day overlaps (TV-sanitised span).
"""
import sys, os, time, json, random, itertools, copy, datetime as dtm
# pin BLAS to 1 thread/worker BEFORE numpy imports — else 16 procs × 16 threads oversubscribe the cores (~4× slower)
os.environ.update({k: '1' for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS')})
from datetime import timezone
from multiprocessing import Pool
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from sweep_eval import evaluate, BASE_BIAS
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import v2_walk, lr_exit_v2, strand_rescue

MODE = sys.argv[1] if len(sys.argv) > 1 else 'smoke'
SEED = 12345
def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)
WINDOW_ENDS = [ms('2026-05-25 00:00') + i * 5 * 86400000 for i in range(7)]   # 05-25 … 06-24
SRCS = ['close', 'ohlc4', 'hl2', 'hlc3', 'high', 'low']

# knob + bias param space (value lists) and their defaults (= current shipping config)
KNOB_SPACE = {
    'SL': [0.33, 0.6, 0.7, 0.9], 'curl_fam': ['s5', 's6', 's7', 's8'], 'exit_rlb': [15, 22, 30],
    'predict': [False, True], 'slip': [0.0, 10.0, 20.0], 'gate_fam': ['s5', 's6', 's7'],
    'bias_on': [False, True], 'hb_tf': [16, 26, 33], 'hb_lenM': [19, 22, 24], 'hb_lenm': [9, 13, 15],
    'hb_multM': [0.58, 0.64, 0.70], 'hb_multm': [0.62, 0.68, 0.74],
    'hb_srcM': ['close', 'hl2', 'hlc3', 'ohlc4', 'hlcc4'],   # blend set: 5 balanced srcs (high/low are hbhi/hblo's job)
    'hb_srcm': ['close', 'hl2', 'hlc3', 'ohlc4', 'hlcc4'], 'bro_N': [1, 3, 6],
}
KNOB_DEFAULT = {'SL': 0.5, 'curl_fam': 's7', 'exit_rlb': 22, 'predict': False, 'slip': 0.0, 'gate_fam': 's7',
                'bias_on': False, 'hb_tf': 33, 'hb_lenM': 19, 'hb_lenm': 13, 'hb_multM': 0.64, 'hb_multm': 0.68,
                'hb_srcM': 'hl2', 'hb_srcm': 'ohlc4', 'bro_N': 1}

# globals filled by init_space() BEFORE the Pool forks (children inherit)
BB, KLINE, BASE_TUP, PARAM_SPACE, PARAMS, DEFAULT = {}, {}, {}, {}, [], {}


def _vals(base, kind):
    if kind == 'len':  return sorted({max(3, base - 4), base, base + 4})
    if kind == 'mult': return sorted({round(max(0.1, base - 0.12), 2), round(base, 2), round(base + 0.12, 2)})
    if kind == 'src':  return [base] + [s for s in SRCS if s != base][:2]


def init_space(cache):
    """Derive BB/KLINE (+ base tuples + param ranges) from the fetched s-line cache; merge knobs."""
    global PARAMS
    for nm, (tf, cfgt, vmode) in cache.items():
        if not (nm[0] == 's' and nm[1:2].isdigit()):
            continue
        BASE_TUP[nm] = (tf, vmode, cfgt[1:4] if cfgt[0] == 'k' else None)   # k = (rsi,stc,klen)
        if cfgt[0] == 'bb':
            _, l, m, s = cfgt; BB[nm] = (l, m, s)
            PARAM_SPACE['%s_len' % nm] = _vals(l, 'len'); PARAM_SPACE['%s_mult' % nm] = _vals(m, 'mult')
            PARAM_SPACE['%s_src' % nm] = _vals(s, 'src')
            DEFAULT.update({'%s_len' % nm: l, '%s_mult' % nm: m, '%s_src' % nm: s})
        else:
            s = cfgt[4]; KLINE[nm] = s
            PARAM_SPACE['%s_src' % nm] = _vals(s, 'src'); DEFAULT['%s_src' % nm] = s
    PARAM_SPACE.update(KNOB_SPACE); DEFAULT.update(KNOB_DEFAULT)
    PARAMS[:] = list(PARAM_SPACE)


def param_to_config(pv):
    lo = {}
    for nm in list(BB) + list(KLINE):
        tf, vmode, kp = BASE_TUP[nm]
        cfgt = ('bb', pv['%s_len' % nm], pv['%s_mult' % nm], pv['%s_src' % nm]) if nm in BB \
            else ('k', kp[0], kp[1], kp[2], pv['%s_src' % nm])
        lo[nm] = (tf, cfgt, vmode)
    cfg = {'line_overrides': lo, 'lrcfg': {'sl': pv['SL'], 'exit_rlb': pv['exit_rlb'], 'curl_n': 1},
           'exit': {'predict': pv['predict'], 'gate_fam': pv['gate_fam'], 'slip': pv['slip']}}
    if pv['bias_on']:
        cfg['bias_filter'] = dict(tf=pv['hb_tf'], lenM=pv['hb_lenM'], lenm=pv['hb_lenm'], multM=pv['hb_multM'],
                                  multm=pv['hb_multm'], srcM=pv['hb_srcM'], srcm=pv['hb_srcm'], N=pv['bro_N'], oob=True)
    return cfg


def gen_configs(target, block=6, breadth_combos=8, depth_combos=24):
    """Overlapping covering blocks, BOUNDED by target. Phase 1 (BREADTH): seed each block with a still-UNCOVERED
    pair so EVERY setting-pair co-varies in some block (Joe: 'all settings interact with all other settings').
    Phase 2 (DEPTH): random blocks with deeper value-samples fill the remaining budget. Deterministic (SEED)."""
    rng = random.Random(SEED)
    need = {tuple(sorted((a, b))) for i, a in enumerate(PARAMS) for b in PARAMS[i + 1:]}   # sorted → deterministic
    seen, out = set(), []

    def emit(blk, k):
        for pair in itertools.combinations(sorted(blk), 2):
            need.discard(pair)
        combos = list(itertools.product(*[PARAM_SPACE[p] for p in blk])); rng.shuffle(combos)
        for combo in combos[:k]:
            if len(out) >= target:
                return
            pv = dict(DEFAULT); pv.update(dict(zip(blk, combo)))
            key = tuple(pv[p] for p in PARAMS)
            if key not in seen:
                seen.add(key); out.append(pv)

    while need and len(out) < target:                              # breadth: guarantee every pair co-varies
        nl = sorted(need); a, b = nl[rng.randrange(len(nl))]
        rest = rng.sample([p for p in PARAMS if p not in (a, b)], block - 2)
        emit([a, b] + rest, breadth_combos)
    while len(out) < target:                                       # depth: deeper value-samples until budget
        emit(rng.sample(PARAMS, block), depth_combos)
    globals()['_UNCOVERED'] = len(need)
    return out


_DB = None
_LC = None                # per-worker cached lr_config (avoids 7 DB round-trips/config)
_BASE_CACHE = {}          # per-worker: end_ms -> (base, ts, px), loaded once
def _init():
    global _DB, _LC
    _DB = DatabaseManager(**get_db_config()); _DB.connect()
    _LC = lr_config(_DB)


def _work(args):
    idx, pv = args
    try:
        cfg = param_to_config(pv)
        lrov = cfg.pop('lrcfg', {})                          # apply lrcfg overrides to a shallow copy (scalars only)
        lc = copy.copy(_LC)
        for k, v in lrov.items():
            setattr(lc, k, v)
        nets = []
        for end in WINDOW_ENDS:
            if end not in _BASE_CACHE:
                W0 = bm.BiasWindow(_DB, end)                  # load base once, then reuse (kills DB contention)
                _BASE_CACHE[end] = (W0.base, W0.ts, W0.px)
            nets.append(evaluate(_DB, end, cfg, lrcfg=lc, base_cache=_BASE_CACHE[end])[0])
        return idx, min(nets), nets, None
    except Exception as e:
        return idx, None, None, str(e)[:120]


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    bcfg = bm.BiasConfig(**BASE_BIAS); lc = lr_config(db)
    Wb = bm.BiasWindow(db, WINDOW_ENDS[-1], cfg=bcfg)
    ent = v2_walk(Wb, lc); strand_rescue(Wb, lc, ent, lr_exit_v2(Wb, lc, ent, predict=False))
    init_space(Wb._ls._cache)
    target = int(MODE) if MODE.isdigit() else (40 if MODE == 'smoke' else 5500)   # 5500 @ ~4.6/min ≈ 20h; covers all pairs + depth
    configs = gen_configs(target)
    print('MODE=%s · %d params · %d configs · %d windows · %d cores' % (MODE, len(PARAMS), len(configs), len(WINDOW_ENDS), os.cpu_count()))
    db.execute('''CREATE TABLE IF NOT EXISTS sweep_results (idx INT PRIMARY KEY, worst FLOAT, nets TEXT,
                  pv TEXT, err VARCHAR(140), ts BIGINT)''')
    done = {r['idx'] for r in db.execute('SELECT idx FROM sweep_results', fetch=True)}
    todo = [(i, pv) for i, pv in enumerate(configs) if i not in done]
    print('resume: %d done, %d to do' % (len(done), len(todo)))
    t0 = time.time(); wall = int(t0 * 1000); n = 0; tmark = t0; nmark = 0
    workers = int(os.environ.get('SWEEP_WORKERS', 0)) or max(1, os.cpu_count() - 2)   # phys-core-bound: tune via env
    print('workers=%d' % workers)
    with Pool(processes=workers, initializer=_init) as pool:
        for idx, worst, nets, err in pool.imap_unordered(_work, todo, chunksize=1):
            db.execute('INSERT INTO sweep_results VALUES (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE worst=VALUES(worst)',
                       (idx, worst, json.dumps(nets), json.dumps(configs[idx]), err, wall + int((time.time()-t0)*1000)))
            n += 1
            if n % 20 == 0:
                cum = n / (time.time()-t0); inc = (n-nmark) / (time.time()-tmark)   # inc = steady-state (excludes cold-start)
                print('  %d/%d · cum %.1f/min · inc %.1f/min · ETA(inc) %.1fh' % (n, len(todo), cum*60, inc*60, (len(todo)-n)/inc/3600))
                tmark = time.time(); nmark = n
    print('DONE %d in %.1f min' % (n, (time.time()-t0)/60))
    for r in db.execute('SELECT idx,worst,nets FROM sweep_results WHERE err IS NULL ORDER BY worst DESC LIMIT 8', fetch=True):
        print('  idx%-5d worst=%+.1f%% nets=%s' % (r['idx'], r['worst'], [round(x) for x in json.loads(r['nets'])]))
    errs = db.execute('SELECT COUNT(*) c FROM sweep_results WHERE err IS NOT NULL', fetch=True)[0]['c']
    print('errors: %d' % errs)
    db.disconnect()


if __name__ == '__main__':
    main()
