"""
bl_dialin — BL line-pair dial-in (docs/bl_dialin_process.md). Stage 1 (the grind).

Machine-native trade: combined c_bls re-folded with the BREACH line at the swept combo
(the other active lines precomputed once per window); entry = bias-gated raw PK within
±lookback of a c_bls:3 gate-open; metric = smallest adverse swing to overcome (drop >0.44).
Sweeps breach K × support BB (ic 34) × exit_mask × lookback. Self-sizes to --budget via a
speedtest. Random days from the past ~35d (fresh; --replay re-uses the logged draw).

  python3 bl_dialin.py --budget 7          # 7-hour grind
  python3 bl_dialin.py --budget 0.05        # ~3-min smoke
  python3 bl_dialin.py --budget 7 --replay  # same days as the last run
"""
import sys, os, time, json, random
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import logging
for n in ('BybitKlineClient', 'BLDetect', 'KlineLoader', 'DatabaseManager'):
    logging.getLogger(n).setLevel('ERROR')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect, GCA5M_RAW
from optimus9.orchestration.gate_signal_sweep import bny30_oob_side, bny30_latched_bias, pine_aligned_signals

TAKE, CAP, STOPMAX = 0.9, 540, 0.44
BREACH, SUPPORT_IC = 's30r', 34                       # support = ic 34 (s30m mini), per Joe
DAY_MS, HORIZON_D = 86400000, 35
WIN_FILE = '/home/joe/optimus9-docs-handover/logs/bl_dialin_windows.json'
SRCS = ['close', 'hl2', 'hlc3', 'ohlc4', 'hlcc4']
LOOKBACKS = [16, 33, 56]                              # ±bars (5s) — free inner sweep per combo
MASKS = [1, 4, 5, 7]                                  # exit_mask bit combos
# champion (placement 0.055) — centre of the --champion small sweep (with-p vs without-p A/B)
CHAMPION = dict(k_len=5, rsi=6, stc=6, k_src='hl2', bb_len=10, bb_mult=0.40, bb_src='hlc3', exit_mask=5)


def arg(name, default):
    return next((sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == name and i + 1 < len(sys.argv)), default)


def latched_bias(oob, threshold=2):
    """Inverted bny30 direction bias. Re-latches (a RESET, not a flip) only after `threshold`
    CONSECUTIVE same-side OOB closes — a single touch-and-go rarely marks a profitable swing
    edge, and BB lines often return to the prior boundary before committing to the other side
    (Joe 2026-06-14). cur = -side. The threshold lives in bl_config (blc_bny30_bias_reset_threshold)."""
    oob = np.asarray(oob, np.int8)
    b = np.zeros(len(oob), np.int8)
    cur = run_side = run_len = 0
    for i in range(len(oob)):
        s = int(oob[i])
        if s != 0 and s == run_side:
            run_len += 1
        elif s != 0:
            run_side, run_len = s, 1
        else:
            run_side = run_len = 0
        if run_len >= threshold:
            cur = -run_side                                  # confirmed OOB run → reset the bias
        b[i] = cur
    return b


def main():
    budget_s = float(arg('--budget', '7')) * 3600
    replay = '--replay' in sys.argv
    withp = '--withp' in sys.argv                     # arm A: include bny30p in the bias (else M-only)
    t_start = time.time()
    db = DatabaseManager(**get_db_config()); db.connect()
    dmax = int(db.execute('SELECT MAX(kc_timestamp) m FROM kline_collection WHERE kc_tp_pk=1', fetch=True)[0]['m'])
    det = BLDetect(db, lookback_hours=24, warmup_hours=12)
    s30r = [f for f in det._families if f['name'] == BREACH][0]
    sup0 = det._cfg_dict(SUPPORT_IC)                  # support base (ic 34 = s30m)
    bias_reset_thr = int(det._cfg['blc_bny30_bias_reset_threshold'])   # consec OOB closes to reset bias
    # c_bls fold scope = the tested breach SOLO (P / LOI). The other 7 breaches are NOT folded
    # in → c_bls ≡ s30r.state, so c_bls:3 ⟺ s30r:3. The {s30r + 7 others} group fold was the
    # confound (the others suppressed s30r's gate-opens). See bl_dialin_process.md.
    others = []

    # ── windows: random days in the past 35d (fresh, or --replay the logged draw) ──
    n_win = min(11, max(3, round(budget_s / 3600 + 2)))
    if replay and os.path.exists(WIN_FILE):
        ends = json.load(open(WIN_FILE))['ends']
    else:
        lo = dmax - HORIZON_D * DAY_MS; hi = dmax - DAY_MS
        days = sorted(random.sample(range(lo // DAY_MS, hi // DAY_MS), n_win))
        ends = [int(d * DAY_MS + DAY_MS) for d in days]   # 24h window ending here
        json.dump({'ends': ends}, open(WIN_FILE, 'w'))
    print(f'budget {budget_s/3600:.2f}h · {len(ends)} random windows · support ic{SUPPORT_IC} · replay={replay}', flush=True)

    # ── precompute per window: the OTHER lines' fold, px_smooth, bias, raw PKs ──
    W = []
    for e in ends:
        base, ts, ws, _, px = det._setup(e)
        Mk = ts >= ws
        if others:
            st = np.vstack([det._run_family(f, base, ts)[3]['state'] for f in others])
            fixed_nz = np.where((st == 0).all(axis=0), 99, np.where(st == 0, 99, st).min(axis=0))  # others' min-nonzero
        else:
            fixed_nz = np.full(len(ts), 99, np.int8)   # solo fold → c_bls = s30r.state (P/LOI)
        bias = bny30_latched_bias(base, bias_reset_thr, use_k=withp)
        ai, ad = pine_aligned_signals(base, det._db, GCA5M_RAW, gate=False)
        pk = np.zeros(len(ts), np.int8); pk[ai] = ad
        W.append(dict(base=base, ts=ts, Mk=Mk, fixed=fixed_nz, bias=bias, pk=pk, px=np.asarray(px, float)))
    print(f'  {len(W)} windows ready ({time.time()-t_start:.0f}s)', flush=True)

    def eval_combo(w, k, r, s, ksrc, bl, bm, bsrc, mask):
        """One combo on one window → list of clean placements (stop≤0.44) per lookback."""
        fam = {**s30r, 'k': {**s30r['k'], 'k_len': k, 'rsi_len': r, 'stc_len': s, 'src': ksrc},
               'exit_support': {**sup0, 'bb_len': bl, 'bb_mult': bm, 'src': bsrc}, 'exit_mask': mask}
        srstate = det._run_family(fam, w['base'], w['ts'])[3]['state']
        srnz = np.where(srstate == 0, 99, srstate)
        cb = np.minimum(w['fixed'], srnz); cb = np.where(cb == 99, 0, cb).astype(np.int8)[w['Mk']]
        pk = w['pk'][w['Mk']]; bm_ = w['bias'][w['Mk']]; px = w['px'][w['Mk']]; n = len(cb)
        g3 = np.flatnonzero((cb[1:] == 3) & (cb[:-1] != 3)) + 1
        pkbars = np.flatnonzero((pk != 0) & (pk == bm_))
        out = {}
        for lb in LOOKBACKS:
            stops = []
            for i in pkbars:
                if not len(g3) or np.min(np.abs(g3 - i)) > lb:
                    continue
                d = int(pk[i]); seg = px[i + 1:i + 1 + CAP]
                if len(seg) == 0:
                    continue
                rel = (seg - px[i]) / px[i] * 100 * d; hit = np.where(rel >= TAKE)[0]
                if not len(hit):
                    continue
                st = float(np.maximum(0.0, -rel[:int(hit[0]) + 1]).max()) if hit[0] > 0 else 0.0
                if st <= STOPMAX:
                    stops.append(st)
            out[lb] = stops
        return out

    # ── speedtest: time a few combos across all windows ──
    test = [(3, 10, 12, 'close', 7, 0.74, 'hlcc4', 7), (4, 12, 10, 'hlcc4', 9, 1.2, 'hl2', 5),
            (5, 8, 8, 'ohlc4', 14, 1.5, 'ohlc4', 1), (2, 14, 6, 'close', 22, 0.6, 'close', 4)]
    ts0 = time.time()
    for c in test:
        for w in W:
            eval_combo(w, *c)
    sec_combo = (time.time() - ts0) / len(test)
    remaining = budget_s - (time.time() - t_start)
    max_combos = int(remaining * 0.85 / sec_combo)
    print(f'  speedtest: {sec_combo:.2f}s/combo (all windows) → budget fits ~{max_combos:,} combos', flush=True)

    # ── grid: --champion = small sweep around the champion (reduce time drag); else full, budget-capped ──
    champ = '--champion' in sys.argv
    if champ:
        K = [(k, r, s, ks) for k in (4, 5, 6) for r in (6, 9) for s in (6, 10) for ks in ('hl2', 'hlc3')]
        B = [(bl, bm, bs) for bl in (8, 10, 12) for bm in (0.4, 0.6) for bs in ('hlc3', 'hl2')]
        grid = [(*k, *b, CHAMPION['exit_mask']) for k in K for b in B]   # exit_mask fixed at champion (5)
    else:
        K = [(k, r, s, ks) for k in range(2, 11) for r in range(6, 25, 3) for s in range(6, 29, 4) for ks in SRCS]
        B = [(bl, bm, bs) for bl in range(4, 16, 2) for bm in [round(0.4 + 0.2 * i, 2) for i in range(8)] for bs in SRCS]
        grid = [(*k, *b, m) for k in K for b in B for m in MASKS]
        random.shuffle(grid); grid = grid[:max_combos]
    print(f'  grid: {len(grid):,} combos × {len(LOOKBACKS)} lookbacks × {len(W)} windows · champion={champ} withp={withp}', flush=True)

    db.execute('DROP TABLE IF EXISTS bl_dialin_results')
    db.execute('''CREATE TABLE bl_dialin_results (bdr_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
        k_len INT,rsi INT,stc INT,k_src VARCHAR(6), bb_len INT,bb_mult FLOAT,bb_src VARCHAR(6),
        exit_mask INT, lookback INT, n_clean INT, min_clean INT, med_stop FLOAT, mean_stop FLOAT,
        n_win INT, all_win TINYINT, KEY(all_win), KEY(med_stop))''')

    rows = []; done = 0; t1 = time.time()
    for combo in grid:
        per_lb = {lb: [] for lb in LOOKBACKS}              # per lookback: per-window clean-stop lists
        for w in W:
            o = eval_combo(w, *combo)
            for lb in LOOKBACKS:
                per_lb[lb].append(o[lb])
        for lb in LOOKBACKS:
            allstops = [x for ws in per_lb[lb] for x in ws]
            if not allstops:
                continue
            mc = min(len(ws) for ws in per_lb[lb])
            rows.append((*combo, lb, len(allstops), mc, float(np.median(allstops)), float(np.mean(allstops)),
                         len(W), int(mc >= 3)))
        done += 1
        if len(rows) >= 5000:
            db.executemany('''INSERT INTO bl_dialin_results (k_len,rsi,stc,k_src,bb_len,bb_mult,bb_src,exit_mask,
                lookback,n_clean,min_clean,med_stop,mean_stop,n_win,all_win) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', rows)
            rows = []
        if done % 500 == 0:
            el = time.time() - t1
            print(f'  {done:,}/{len(grid):,} ({el:.0f}s, {done/el:.1f}/s, ~{el/done*len(grid)/3600:.1f}h total)', flush=True)
        if time.time() - t_start > budget_s * 0.97:
            print(f'  budget reached at {done:,}/{len(grid):,} — stopping clean', flush=True)
            break
    if rows:
        db.executemany('''INSERT INTO bl_dialin_results (k_len,rsi,stc,k_src,bb_len,bb_mult,bb_src,exit_mask,
            lookback,n_clean,min_clean,med_stop,mean_stop,n_win,all_win) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', rows)
    print(f'done: {done:,} combos in {(time.time()-t_start)/3600:.2f}h → bl_dialin_results', flush=True)

    print('\\n=== TOP 15 by placement (closest to swing; ≥3 clean/window in all) ===', flush=True)
    for t in db.execute('SELECT * FROM bl_dialin_results WHERE all_win=1 ORDER BY med_stop ASC LIMIT 15', fetch=True):
        print(f"  k{t['k_len']} r{t['rsi']} s{t['stc']}/{t['k_src']:>5} bb{t['bb_len']}/{t['bb_mult']:.2f}/{t['bb_src']:>5} "
              f"mask{t['exit_mask']} lb{t['lookback']:>2} medStop={t['med_stop']:.3f} n={t['n_clean']} minCln={t['min_clean']}", flush=True)
    db.disconnect()


if __name__ == '__main__':
    main()
