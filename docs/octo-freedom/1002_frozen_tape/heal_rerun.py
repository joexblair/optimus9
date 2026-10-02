"""The chain run twice over ONE window: A on the stored tape (what o9-live read), B with Joe's TV export
spliced into the frozen span. Reads only - nothing is written to the DB.

Joe 1002: *"~/thecodes/transfer/BYBIT_FARTCOINUSDT.P, 5S_d6c05.csv is the source data to recon the frozen tape"*.

THE SPLICE, and only the splice, separates A from B:
    span     05:08:35 -> 05:25:35 UTC 10-02: the 205 slots the stored tape holds as V=0 filler at close
             0.18573 after its last trade bar (05:08:30), up to the last slot before the collector's first
             trade bar after reconnect (05:25:40)
    TV row   close = the TV close; volume = 1, a marker. Volume is read only as `> 0` (the filler-invisible
             event mask, bias_machine.py:142 and jig.py:91), so the magnitude moves no number
    no row   stays V=0 filler; close = the previous healed close, the bar builder's carry-forward
    o/h/l    set to the bar builder's convention (open = previous close). No line and not `px` reads them:
             all 31 lines and px read `close` (printed below), so they move no number either
    px       recomputed from the spliced base the same way bl_detect._setup builds it
"""
import sys, time, json, datetime as dt
import numpy as np, pandas as pd
sys.path.insert(0, '/home/joe/thecodes')
import bias_machine as bm
from sweep_eval import BASE_BIAS
from optimus9.config import get_db_config
from optimus9.db.database_manager import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.live.octo_inputs import OctoConfig, Inputs
from optimus9.live.octo_freedom import OctoFreedom, WARMUP_H, BAR_MS
from optimus9.live import octo_recon as R

CSV = '/home/joe/thecodes/transfer/BYBIT_FARTCOINUSDT.P, 5S_d6c05.csv'
SPAN = (1790917715000, 1790918735000)          # 05:08:35 .. 05:25:35 UTC 2026-10-02
LAST = int(sys.argv[1]) if len(sys.argv) > 1 else 1790973335000   # the CSV's last bar, 20:35:35
OUT = '/home/joe/thecodes/docs/octo-freedom/1002_frozen_tape/heal_rerun.%s.jsonl'
h = lambda t: dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')

db = DatabaseManager(**get_db_config()); db.connect()
cfg = OctoConfig(db)
bias_cfg = bm.BiasConfig(**BASE_BIAS)
live_start = R.live_start_from_log()
book_start = live_start - 24 * 3600 * 1000
hours = (LAST - book_start) / 3600000.0 + 1.0 / 720
print('live start', h(live_start), '| book start', h(book_start), '| last bar', h(LAST), flush=True)

det = BLDetect(db, lookback_hours=hours, warmup_hours=WARMUP_H)
base, ts, _ws, _x, px = det._setup(LAST + 1)
for c in ('open', 'high', 'low', 'close', 'volume'):
    base[c] = base[c].to_numpy(dtype=float)
assert int(ts[-1]) == LAST, h(ts[-1])
s = det._sys
assert int(s['pxsmooth_dema_tf']) <= 5 and s['pxsmooth_dema_src'] == 'close', s

tv = pd.read_csv(CSV); tv['ts'] = tv['time'].astype(np.int64) * 1000
tvc = dict(zip(tv.ts, tv.close))
healed = base.copy()
tsa = healed['timestamp'].to_numpy(np.int64)
j0, j1 = int(np.searchsorted(tsa, SPAN[0])), int(np.searchsorted(tsa, SPAN[1]))
assert int(tsa[j0]) == SPAN[0] and int(tsa[j1]) == SPAN[1] and j1 - j0 + 1 == 205
assert (healed['volume'].iloc[j0:j1 + 1] == 0).all(), 'span is not all V=0 filler'
n_tv = 0
for j in range(j0, j1 + 1):
    prev = float(healed.at[j - 1, 'close'])
    t = int(tsa[j])
    if t in tvc:
        c = float(tvc[t]); v = 1.0; n_tv += 1
    else:
        c = prev; v = 0.0
    healed.loc[j, ['open', 'high', 'low', 'close', 'volume']] = [prev, max(prev, c), min(prev, c), c, v]
px_h = IC.dema(IC.build_source(healed, 'close'), int(s['pxsmooth_dema_len']))
print('spliced', j1 - j0 + 1, 'slots,', n_tv, 'with a TV row', flush=True)


def run(label, b, p):
    t = time.time()
    prod = OctoFreedom(db, cfg, bias_cfg, lookback_h=hours, warmup_h=WARMUP_H)
    W = bm.BiasWindow(db, LAST + 1, lookback=hours, warmup=WARMUP_H, cfg=bias_cfg,
                      line_overrides=cfg.overrides, lean=True, base_cache=(b, ts, p))
    inp = Inputs(W, cfg)
    recs = prod.advance(inp, book_start)
    recs = [r for r in recs if r['ts'] >= book_start]
    ev = R.live_shaped(recs, inp, cfg, live_start)
    lines = {n: np.asarray(W.line(n), float) for n in cfg.names()}
    print(label, 'done', round(time.time() - t), 's', flush=True)
    return dict(recs=recs, ev=ev, inp=inp, lines=lines)


A = run('A stored', base, px)
B = run('B healed', healed, px_h)


def evkey(t, e):
    if e[0] == 'open':
        return (t, 'open', R.side_of(e[1]['dr']), e[1]['opened_by'])
    if e[0] == 'close':
        return (t, 'close', R.side_of(e[1]['dr']), e[1]['closed_by'])
    return (t, 'inert', R.side_of(e[2]), '')


with open(OUT % 'events', 'w') as fh:
    for lab, X in (('A', A), ('B', B)):
        for t, e in X['ev']:
            fh.write(json.dumps(dict(run=lab, book='live-start', bar=h(t), ev=evkey(t, e)[1:])) + '\n')
        for r in X['recs']:
            for e in r['events']:
                fh.write(json.dumps(dict(run=lab, book='24h-earlier', bar=h(r['ts']), ev=evkey(r['ts'], e)[1:])) + '\n')

ea = [evkey(t, e) for t, e in A['ev']]; eb = [evkey(t, e) for t, e in B['ev']]
print('--- live-start book: A', len(ea), 'events | B', len(eb), 'events')
sa, sb = set(ea), set(eb)
for k in sorted(sa | sb):
    if (k in sa) != (k in sb):
        print('  ', 'A only' if k in sa else 'B only', h(k[0]), k[1:])
print('--- live-start book vs the dump (A should equal the live dump lines <= last bar)')
dump = [json.loads(l) for l in open('/home/joe/thecodes/o9live_trade_signal_dump.log')]
print('   dump lines <= last bar', sum(1 for d in dump if d['bar_ms'] <= LAST))

ra = {r['ts']: r for r in A['recs']}; rb = {r['ts']: r for r in B['recs']}
for f in ('hit', 'emitted', 'fires', 'arm', 'arm_dr'):
    d = [t for t in ra if ra[t][f] != rb[t][f]]
    print('--- walk field %-8s bars differing %6d' % (f, len(d)), '| first', h(d[0]) if d else '-', '| last', h(d[-1]) if d else '-')
fa = [t for t in ra if ra[t]['fires']]; fb = [t for t in rb if rb[t]['fires']]
print('--- WALK FIRES FROM bars: A', len(fa), '| B', len(fb))
for t in sorted(set(fa) ^ set(fb)):
    r = ra[t] if t in fa else rb[t]
    print('  ', 'A only' if t in fa else 'B only', h(t), 'arm', h(r['arm'] * BAR_MS) if r['arm'] not in (None, -1) else r['arm'], 'arm_dr', r['arm_dr'])
ti = A['inp'].ts
for nm, arr in (('DR', 'DR'), ('DRW', 'DRW')):
    x, y = getattr(A['inp'], arr), getattr(B['inp'], arr)
    d = np.nonzero(x != y)[0]
    print('--- %-4s bars differing %6d' % (nm, len(d)), '| first', h(ti[d[0]]) if len(d) else '-', '| last', h(ti[d[-1]]) if len(d) else '-')
print('--- lines: bars differing (|A-B| > 1e-9) and the last such bar')
for n in A['lines']:
    a, b = A['lines'][n], B['lines'][n]
    dd = np.abs(a - b); m = (dd > 1e-9) | (np.isnan(a) != np.isnan(b))
    k = np.nonzero(m)[0]
    print('   %-11s %6d bars | max %.4f | first %s | last %s | at the last bar A %.4f B %.4f' % (
          n, len(k), np.nanmax(dd) if len(k) else 0.0, h(ti[k[0]]) if len(k) else '-',
          h(ti[k[-1]]) if len(k) else '-', a[-1], b[-1]))
np.savez_compressed(OUT.replace('.jsonl', '.npz') % 'lines', ts=ti,
                    **{'A_' + n: A['lines'][n] for n in A['lines']}, **{'B_' + n: B['lines'][n] for n in B['lines']})
