"""tide_sweep.py — parallel sweeps over the tide-trigger machine (tide_machine.run_config). One subset per process:
  1 = FINISHER precision  : rev_sets x N x tol           (which sets require Mage-REVERSING vs breach; s1 finisher fixed)
  2 = EXIT s10r gauge     : s10r_tf x src x seam x wait-breach x stall-floor
  3 = ENTRY (arm+oversold): anchor x tide-line x wob x predict x PROX (oversold threshold)
Fin set fixed at s1 (the validated tight config — Joe: don't sweep finisher TFs). Writes tide_sweep_{n}.txt ranked by
realised r_ret. Run:  python3 tide_sweep.py {1|2|3}
"""
import sys, itertools, datetime as dtm
from datetime import timezone
from optimus9.analysis.jig import Jig
from tide_machine import run_config

END = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
S1 = {'s1m': (60, ('bb', 6, 0.56, 'close'), 'emerging'), 's1M': (60, ('bb', 37, 0.72, 'hlcc4'), 'emerging'),
      's1r': (60, ('k', 6, 6, 5, 'close'), 'emerging')}
FIN = ('s1', 's15', 's30')                                  # finisher fixed (validated); precision/exit/arm are the axes
def s10r(tf, src): return {'s10r': (tf, ('k', 6, 6, 5, src), 'emerging')}


def sweep1():
    J = Jig(END, hours=48, warmup=24, overrides={**s10r(600, 'hl2'), **S1}); rows = []
    for revs, N, tol in itertools.product([(), ('s15',), ('s30',), ('s15', 's30')], [5, 6, 7], [12, 24]):
        m = run_config(J, {'fin_sets': FIN, 'rev_sets': revs, 'N': N, 'tol': tol})
        rows.append(('rev=%-11s N=%d tol=%d' % (str(revs) if revs else '()', N, tol // 6), m))
    J.close(); return rows


def sweep2():
    rows = []
    for tf, src in itertools.product([720, 600, 540, 480, 360], ['hl2', 'close']):
        J = Jig(END, hours=48, warmup=24, overrides={**s10r(tf, src), **S1})
        for seam, wb, fl in itertools.product([150000, 300000], [True, False], [0.0, 5.0]):
            m = run_config(J, {'fin_sets': FIN, 'seam': seam, 'wait_breach': wb, 'stall_floor': fl})
            rows.append(('s10r=%ds src=%-5s seam=%dm wb=%-5s fl=%g' % (tf, src, seam // 60000, str(wb), fl), m))
        J.close()
    return rows


def sweep3():
    J = Jig(END, hours=48, warmup=24, overrides={**s10r(600, 'hl2'), **S1}); rows = []
    for anch, line, wob, pred, prox in itertools.product(['brk', 'rev'], ['s5M', 's7M'], [2, 4, 6, 8], [True, False], [25, 33, 40]):
        m = run_config(J, {'fin_sets': FIN, 'ad_anchor': anch, 'ad_line': line, 'ad_wob': wob, 'ad_predict': pred, 'PROX': prox})
        rows.append(('ad=%s line=%s wob=%d pred=%-5s PROX=%d' % (anch, line, wob, str(pred), prox), m))
    J.close(); return rows


name = sys.argv[1] if len(sys.argv) > 1 else '1'
rows = {'1': sweep1, '2': sweep2, '3': sweep3}[name]()
rows.sort(key=lambda r: -r[1]['r_ret'])
out = 'tide_sweep_%s.txt' % name
with open(out, 'w') as f:
    f.write('=== SWEEP %s — %d configs, ranked by realised r_ret (window 07-05 20:00 -> 07-07 20:00) ===\n' % (name, len(rows)))
    f.write('%-42s %4s %6s %6s %5s %8s %5s\n' % ('config', 'n', 'eMAE', 'eMFE', 'mfeS', 'r_ret', 'win'))
    for label, m in rows:
        f.write('%-42s %4d %6.2f %6.2f %5d %8.3f %5.2f\n' % (label, m['n'], m['e_mae'], m['e_mfe'], m['mfeside'], m['r_ret'], m['win']))
print('wrote', out, '(%d configs)' % len(rows))
