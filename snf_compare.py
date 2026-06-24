"""
snf_compare.py (Joe 0624) — SnF (Support and Friction) line-comparison table.

Compares the bias-pk outcomes of 6 osc lines under a fixed s3-lookback footing (N=2): s12m/s12M (trig
s12m, TF12) + s3m/s3M (trig s6m, TF6) + blp6m/blp6M (trig blp6m close/20/0.5, TF6). Per line: the pk stream
(state ±1) + the first-trade placement (pnl/mae). Rows = union of directional pk-times; a line that
didn't fire at a time = state 0, null pnl/mae (Joe's placeholder). The start of SnF dev.

  python3 snf_compare.py         → build the CURRENT window (0611 00:00 → 0618 00:00), write snf_compare, print per-line
  python3 snf_compare.py grind   → per-line summary aggregated across the 9 bias_eval windows
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm

GM = bm.GEN_M                                                # trigger BB default (10/0.4/hlc3)
STREAMS = {  # col: osc line · trigger TF · [trigger BB config tlen/tmult/tsrc, default GEN_M]; maj dodges MySQL case-blind cols
    's12m':   dict(osc='s12m', tf=12),
    's12maj': dict(osc='s12M', tf=12),
    's3m':    dict(osc='s3m',  tf=6),
    's3maj':  dict(osc='s3M',  tf=6),
    'blp6m':   dict(osc='blp6m', tf=6, tlen=20, tmult=0.5, tsrc='close'),   # blp6m reversing = trigger (grind winner close/20/0.5)
    'blp6maj': dict(osc='blp6M', tf=6, tlen=20, tmult=0.5, tsrc='close'),
}
S3_LOOKBACK = 2
def ms(dt): return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)
def utc(t):  return dtm.datetime.utcfromtimestamp(t / 1000)


def snf_streams(db, R0, R1):
    """Per-line {pk-time → (state, pnl, mae)} + the union of directional pk-times + a per-line summary."""
    data = {c: {} for c in STREAMS}; alltimes = set(); summary = {}
    for c, s in STREAMS.items():
        cfg = bm.BiasConfig(osc=s['osc'], trigger_tf=s['tf'],
                            trigger_len=s.get('tlen', GM[1]), trigger_mult=s.get('tmult', GM[2]),
                            trigger_src=s.get('tsrc', GM[3]),
                            gate='oob', entry_order='seq', s3_variant='m',
                            xm45=False, mae=0.4, target=0.9, floater_anchor='last', verdict='pk')
        W = bm.BiasWindow(db, R1, cfg=cfg); ups = W.signals()
        pls = W.placements(ups, cfg.mae, cfg.target, s3_lookback=S3_LOOKBACK)
        pnls = {int(p['pk_t']): (round(float(p['potential']), 3), round(float(p['mae']), 3), p['hit'])
                for p in pls if R0 <= p['pk_t'] < R1}
        tr = []
        for u in ups:
            if u['call'] in ('BULL', 'BEAR') and R0 <= u['t'] < R1:
                t = int(u['t']); st = 1 if u['call'] == 'BULL' else -1; pm = pnls.get(t)
                data[c][t] = (st, pm[0] if pm else None, pm[1] if pm else None)
                alltimes.add(t)
                if pm: tr.append(pm)
        summary[c] = dict(pks=len(data[c]), trades=len(tr), hits=sum(1 for x in tr if x[2]),
                          mean_pnl=float(np.mean([x[0] for x in tr])) if tr else 0.0,
                          mean_mae=float(np.mean([x[1] for x in tr])) if tr else 0.0)
    return data, alltimes, summary


def write_snf_compare(db, data, alltimes):
    cols = list(STREAMS)
    db.execute('DROP TABLE IF EXISTS snf_compare')
    cd = ', '.join(f'{c}_state TINYINT, {c}_pnl FLOAT, {c}_mae FLOAT' for c in cols)
    db.execute(f'CREATE TABLE snf_compare (snf_pk INT AUTO_INCREMENT PRIMARY KEY, bar_time DATETIME NOT NULL, {cd})')
    ic = 'bar_time, ' + ', '.join(f'{c}_state, {c}_pnl, {c}_mae' for c in cols)
    rows = []
    for t in sorted(alltimes):
        v = [utc(t)]
        for c in cols:
            st, pnl, mae = data[c].get(t, (0, None, None)); v += [st, pnl, mae]
        rows.append(tuple(v))
    ph = ', '.join(['%s'] * (1 + 3 * len(cols)))
    db.executemany(f'INSERT INTO snf_compare ({ic}) VALUES ({ph})', rows)
    return len(rows)


def grind(db):
    """Per-line summary aggregated across the 9 bias_eval windows (the trustworthy SnF read)."""
    wins = [(ms(r['s']), ms(r['e'])) for r in db.execute(
        'SELECT DISTINCT eval_window_start s, eval_window_end e FROM bias_eval ORDER BY eval_window_end', fetch=True)]
    agg = {c: dict(pks=0, trades=0, hits=0, pnls=[], maes=[]) for c in STREAMS}
    for R0, R1 in wins:
        _, _, summ = snf_streams(db, R0, R1)
        for c in STREAMS:
            s = summ[c]; a = agg[c]
            a['pks'] += s['pks']; a['trades'] += s['trades']; a['hits'] += s['hits']
            if s['trades']:
                a['pnls'].append((s['mean_pnl'], s['trades'])); a['maes'].append((s['mean_mae'], s['trades']))
    return agg


def _wmean(pairs):
    tot = sum(n for _, n in pairs)
    return sum(v * n for v, n in pairs) / tot if tot else 0.0


def _print_line(c, pks, trades, hits, mp, mm):
    hp = hits / trades * 100 if trades else 0
    print(f'  {c:7s} {pks:4d} pks · {trades:4d} tr · {hp:3.0f}% · {mp:+6.2f} · {mm:+.2f}')


if __name__ == '__main__':
    db = DatabaseManager(**get_db_config()); db.connect()
    if 'grind' in sys.argv:
        agg = grind(db)
        print('snf_compare — 9-window grind (per-line, footing hlc3/N=2):')
        for c in STREAMS:
            a = agg[c]
            _print_line(c, a['pks'], a['trades'], a['hits'], _wmean(a['pnls']), _wmean(a['maes']))
    else:
        R1 = ms(dtm.datetime(2026, 6, 18, 0, 0)); R0 = R1 - 168 * bm.H
        data, alltimes, summary = snf_streams(db, R0, R1)
        n = write_snf_compare(db, data, alltimes)
        print(f'snf_compare: {n} rows · window {utc(R0):%m-%d %H:%M} → {utc(R1):%m-%d %H:%M} · footing hlc3/N={S3_LOOKBACK}')
        for c in STREAMS:
            s = summary[c]
            _print_line(c, s['pks'], s['trades'], s['hits'], s['mean_pnl'], s['mean_mae'])
    db.disconnect()
