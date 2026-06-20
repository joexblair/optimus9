"""
bias_pk_floater_verdict_grind.py — all-windows sweep of the floater mechanics (Joe 0620), to set
direction before committing any spec. Holds entry = seq/m (cascade winner), osc s12m, gate s14M-OOB,
MAE 0.4 / target 0.9. Sweeps floater_anchor {same,last} × verdict {magnitude,pk} × g_gated {off,on}
= 8 configs. Lines built once per window (cfg-driven from the DB); knobs swapped without rebuild.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
import bias_machine as bm

H = bm.H; MAE, TARGET = 0.4, 0.9
def dd(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%m%d')
CFGS = [(fa, vd, gg) for fa in ('same', 'last') for vd in ('magnitude', 'pk') for gg in (False, True)]
BASE = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False)

db = DatabaseManager(**get_db_config()); db.connect()
det = BLDetect(db, lookback_hours=168, warmup_hours=80); tp = det._tp
rng = db.execute(f'SELECT MIN(kc_timestamp) mn, MAX(kc_timestamp) mx FROM kline_collection WHERE kc_tp_pk={tp}', fetch=True)[0]
earliest, latest = int(rng['mn']), int(rng['mx'])
ends = []; e = latest
while e - (168 + 80) * H >= earliest:
    ends.append(e); e -= 120 * H
ends.reverse()
print(f'{len(ends)} windows · {len(CFGS)} configs (floater × verdict × g_gated) · entry seq/m, osc s12m')

res = {c: [] for c in CFGS}
db2 = DatabaseManager(**get_db_config()); db2.connect()
for wi, end in enumerate(ends):
    W = bm.BiasWindow(db2, end, cfg=BASE)
    trigs = W.trigs(BASE.trigger_tf)
    for fa, vd, gg in CFGS:
        events = W.pk_events(trigs, BASE.gate, BASE.flt_half, fa, gg)
        calls = W.verdict_pk(events, BASE.slope_floor, BASE.delay) if vd == 'pk' else W.verdict_magnitude(events)
        pls = W.placements(calls, MAE, TARGET)
        res[(fa, vd, gg)].append((sum(p['hit'] for p in pls), len(pls)))
    print(f'  window {wi+1}/{len(ends)} → {dd(W.W1)} done')
db2.disconnect(); db.disconnect()

print(f'\nLEADERBOARD — rolled placement rate, {len(ends)} windows:')
print(f'  {"floater":>8} {"verdict":>9} {"g_gated":>7} | {"rate":>5} {"correct":>7} {"trades":>6} {">=40%":>6}')
lb = []
for c in CFGS:
    cc = sum(x[0] for x in res[c]); nn = sum(x[1] for x in res[c])
    posw = sum(1 for (a, b) in res[c] if b and a / b >= 0.40)
    lb.append((cc / nn if nn else 0, cc, nn, posw, c))
for rate, cc, nn, posw, (fa, vd, gg) in sorted(lb, reverse=True):
    flag = '  ← old baseline' if (fa, vd, gg) == ('same', 'magnitude', False) else ''
    print(f'  {fa:>8} {vd:>9} {str(gg):>7} | {rate:>5.0%} {cc:>7} {nn:>6} {posw:>3}/{len(ends)}{flag}')
