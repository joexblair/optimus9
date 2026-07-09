"""tide_sweep_mm.py — comprehensive minimax sweep of the greenfield causal tide machine (NO arm_delay). Each config
scored on its WORST window across the tape (5 windows spanning ~40d) — robust, not lucky-window. Sweeps: entry profile
(strict box sizes incl the 7,2 box + 7of9 N6/N7), PROX, exit_gate, wait_breach, and the s10r TF/src (Jig-rebuild axis).
Ranks TOP MAE performers (tightest worst-window realised MAE) and TOP MFE performers (biggest worst-window MFE) into
SEPARATE tables, report style. Writes tide_sweep_results.txt incrementally so partial results survive.
Run:  python3 tide_sweep_mm.py   (smoke test:  python3 tide_sweep_mm.py smoke)"""
import sys, itertools, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
from tide_machine import run_config

OUT = "/home/joe/thecodes/tide_sweep_results.txt"
WARMUP_D, LOOK_D, N_WIN, WIN_GAP_D = 2, 5, 5, 10                 # 5 windows, 5d each, 10d apart (spans ~40d)
S1 = {'s1m': (60, ('bb', 6, 0.56, 'close'), 'emerging'), 's1M': (60, ('bb', 37, 0.72, 'hlcc4'), 'emerging'),
      's1r': (60, ('k', 6, 6, 5, 'close'), 'emerging')}         # for the 7of9 profiles (fin_sets uses s1)

LINE_CFGS = [(720, 'close'), (600, 'close'), (540, 'close'), (480, 'close'), (360, 'close'), (600, 'hl2'), (480, 'hl2')]
ENTRY = [                                                       # named entry profiles (strict box sizes + 7of9 swap)
    ('strict 1,1', dict(fin_mode='strict', fin_lb=6, fin_fwd=6)),
    ('strict 2,1', dict(fin_mode='strict', fin_lb=12, fin_fwd=6)),
    ('strict 2,2', dict(fin_mode='strict', fin_lb=12, fin_fwd=12)),
    ('strict 4,2', dict(fin_mode='strict', fin_lb=24, fin_fwd=12)),
    ('strict 7,2', dict(fin_mode='strict', fin_lb=42, fin_fwd=12)),      # the classic 7,2 box
    ('7of9 N6', dict(fin_mode='nof9', box_lb=42, tol=24, N=6, fin_sets=('s1', 's15', 's30'))),
    ('7of9 N7', dict(fin_mode='nof9', box_lb=42, tol=24, N=7, fin_sets=('s1', 's15', 's30'))),
]
CROSS = dict(PROX=[33, 40], exit_gate=['oob', 'mid'], wait_breach=[False, True])
BASE = dict(seam=150000, stall_floor=0.0)


def windows(now):
    return [now - dtm.timedelta(days=WIN_GAP_D * k) for k in range(N_WIN)]


def cross():
    ks = list(CROSS)
    for vs in itertools.product(*[CROSS[k] for k in ks]):
        yield dict(zip(ks, vs))


def configs():
    for ename, eprof in ENTRY:
        for cx in cross():
            yield ename, dict(BASE, **eprof, **cx), cx


def label(lc, ename, cx):
    return "s10r=%d/%-5s %-10s PROX=%d gate=%s wb=%s" % (lc[0], lc[1], ename, cx['PROX'], cx['exit_gate'], str(cx['wait_breach'])[0])


def main():
    smoke = len(sys.argv) > 1 and sys.argv[1] == 'smoke'
    now = dtm.datetime.now(timezone.utc)
    wins = windows(now)
    line_cfgs = LINE_CFGS[:1] if smoke else LINE_CFGS
    cfg_list = list(configs())
    if smoke:
        cfg_list = cfg_list[:1] + [c for c in cfg_list if '7of9' in c[0]][:1]   # one strict + one nof9
        wins = wins[:1]
    n_runs = len(line_cfgs) * len(cfg_list) * len(wins)
    print("sweep: %d line-cfgs x %d configs x %d windows = %d runs (~%.1f min est @4s)" %
          (len(line_cfgs), len(cfg_list), len(wins), n_runs, n_runs * 4 / 60))
    md = lambda rows, k: float(np.median([r[k] for r in rows]))
    results = []; done = 0
    for lc in line_cfgs:
        ovr = {'s10r': (lc[0], ('k', 6, 6, 5, lc[1]), 'emerging'), **S1}
        jigs = [Jig(int(e.timestamp() * 1000), hours=LOOK_D * 24, warmup=WARMUP_D * 24, overrides=ovr) for e in wins]
        for ename, cfg, cx in cfg_list:
            rows = []
            for J in jigs:
                try:
                    m = run_config(J, cfg)
                    if m['n'] > 0:
                        rows.append(m)
                except Exception as ex:
                    print("  ERR", label(lc, ename, cx), repr(ex)[:120])
                done += 1
            if not rows:
                continue
            results.append(dict(label=label(lc, ename, cx),
                worst_rmae=min(r['r_mae'] for r in rows), worst_rmfe=min(r['r_mfe'] for r in rows),
                n=md(rows, 'n'), emae=md(rows, 'e_mae'), emfe=md(rows, 'e_mfe'),
                mean=md(rows, 'r_mean'), med=md(rows, 'r_ret'), rmae=md(rows, 'r_mae'), rmfe=md(rows, 'r_mfe'),
                tail=min(r['mae_tail'] for r in rows), win=md(rows, 'win')))
            if len(results) % 8 == 0:
                write_tables(results, done, n_runs, wins, False)
        for J in jigs:
            J.close()
        print("  line-cfg %s done (%d/%d runs)" % (str(lc), done, n_runs))
    write_tables(results, done, n_runs, wins, True)
    print("DONE — %d configs scored -> %s" % (len(results), OUT))


def write_tables(results, done, total, wins, final):
    hdr = "%-42s %4s | %5s %5s | %6s %6s | %7s %6s %6s %4s" % (
        "config", "n", "eMAE", "eMFE", "wMAE", "wMFE", "mean", "rMFE", "tail", "win")
    def row(r):
        return "%-42s %4d | %5.2f %5.2f | %6.2f %6.2f | %+7.3f %6.2f %6.2f %4.2f" % (
            r['label'], r['n'], r['emae'], r['emfe'], r['worst_rmae'], r['worst_rmfe'], r['mean'], r['rmfe'], r['tail'], r['win'])
    mae_top = sorted(results, key=lambda r: -r['worst_rmae'])[:20]
    mfe_top = sorted(results, key=lambda r: -r['worst_rmfe'])[:20]
    with open(OUT, 'w') as f:
        f.write("=== minimax sweep (greenfield causal, NO arm_delay) — %d/%d runs%s ===\n" % (done, total, "  [FINAL]" if final else "  [partial]"))
        f.write("windows end: %s ; LOOK %dd, WARMUP %dd\n\n" % (", ".join(e.strftime('%m-%d') for e in wins), LOOK_D, WARMUP_D))
        f.write("### TOP MAE — ranked by worst-window realised MAE (wMAE, least-negative = tightest) ###\n" + hdr + "\n")
        for r in mae_top:
            f.write(row(r) + "\n")
        f.write("\n### TOP MFE — ranked by worst-window realised MFE (wMFE, biggest = most reach) ###\n" + hdr + "\n")
        for r in mfe_top:
            f.write(row(r) + "\n")


if __name__ == "__main__":
    main()
