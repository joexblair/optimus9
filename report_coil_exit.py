"""report_coil_exit — the stretchy leash's confluence moments, their coil release, and the bar
each exit becomes ACTIONABLE, validated by a ws1mage-rev.

Joe 0917 built this rule over one session. The mechanics live in three producers and every value
lives in wsf_dtf_v3_config; this file only walks the rows and prints.

    optimus9/compute/stretchy_leash.py   coil = dr*((m+Mage)/2 - r), and the support count
    optimus9/compute/coil_moment.py      the confluence moment, and the confirmed coil release
    optimus9/compute/coil_exit.py        Joe's exit rule - confirm / lookback / gap / forward
    optimus9/analysis/jig.py             ws1mage_rev - the event producer, NOT re-implemented here

NOTHING IS HARD-CODED. The knobs come from wsf_dtf_v3_config (section `stretchy_leash`, plus
`bands` for the support set, `ws1mage_rev` for the event, `wsf_chain.grid_s` for the bar width).
The window and the knob string default to what the wsf_dtf_v3 table itself holds.

    python3 report_coil_exit.py
    python3 report_coil_exit.py --from 2026-09-01 --to 2026-09-06
    python3 report_coil_exit.py --md          pipe-delimited, for pasting into a report
"""
import sys, os, argparse, datetime as dt
import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.v3_config import v3_config
from optimus9.compute.line_config import override, mech_lines
from optimus9.compute.stretchy_leash import combined_coil, support_count
from optimus9.compute.coil_moment import moments, release
from optimus9.compute import coil_exit
from optimus9.compute.leash_bank import TABLE as LEASH_TABLE, bank, knob_string
from optimus9.analysis.jig import Jig, ws1mage_rev
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP

V3 = 'wsf_dtf_v3'
ROLES = ('m', 'Mage', 'r')


def _line_specs(db):
    """role -> (src, mode) for the wsf mech, as build_wsf_dtf_v3 reads them."""
    spec = {}
    for g in mech_lines(db, 'wsf'):
        if g['role'] not in spec:
            _t, s_, m_ = g['override']
            spec[g['role']] = (s_, m_)
    return spec


def _cached(spec, tf, role):
    return np.load(os.path.join(LINE_DIR, _line_key(END_MS, HOURS, WARMUP,
                                                    override(tf * 60, *spec[role])) + '.npy'))


def load(db, C):
    """Every line the report needs, all on the 5 s tape grid.

    The ws lines come from the per-line cache (the same files build_wsf_dtf_v3 reads); gcws30 comes
    off the Jig and is mapped onto the same grid. Returns (ts, lines, hi, lo).
    """
    sy = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system WHERE sys_pk=1',
                    fetch=True)[0]
    spec = _line_specs(db)
    ts = np.load(os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP,
                                                  {'src': sy['s'], 'len': sy['l']}) + '.npz'))['__ts__']
    tfs = list(range(C['band_wsf_lo'], C['band_dtf_hi'] + 1))
    lines = {f'ws{t}': {r: _cached(spec, t, r) for r in ROLES} for t in tfs}
    jig_names = sorted({n for n in C['coil_lines'] if not n.startswith('ws')} |
                       {C['sig_line'].replace('Mage', ''), C['dr_line_a'].replace('Mage', '')})
    with Jig(END_MS, hours=HOURS, warmup=WARMUP) as J:
        jt = np.asarray(J.ts, dtype=np.int64)
        hi, lo = J.cfg.hi, J.cfg.lo
        pulled = {n: {r: np.asarray(J.causal.line(n + r), float) for r in ROLES} for n in jig_names}
    idx = np.clip(np.searchsorted(jt, ts), 0, len(jt) - 1)
    for n, d in pulled.items():
        lines[n] = {r: v[idx] for r, v in d.items()}
    return ts, lines, hi, lo, tfs


def walk(db, C, knobs, w0, w1):
    """-> (ts, rows) where each row is one confluence moment with its resolved exit."""
    ts, lines, hi, lo, tfs = load(db, C)
    grid = C['grid_s']
    lag = C['confirm_lag_s'] // grid
    look = C['lookback_s'] // grid
    keys = C['coil_lines']
    support_keys = [f'ws{t}' for t in tfs]

    legs = ws1mage_rev(lines[C['dr_line_a'].replace('Mage', '')]['Mage'],
                       lines[C['sig_line'].replace('Mage', '')]['Mage'], hi, lo,
                       dwell=C['dwell'], rev_wob=C['rev_wob'], hold=C['boundary_xwob'])

    src = db.execute(f'SELECT wdv_ms, wdv_dr FROM {V3} WHERE wdv_knobs=%s AND wdv_utc>=%s '
                     f'AND wdv_utc<%s ORDER BY wdv_ms, wdv_line', (knobs, w0, w1), fetch=True)
    ann = []
    for r in src:
        d = int(r['wdv_dr'])
        i = int(np.searchsorted(ts, int(r['wdv_ms'])))
        ann.append(dict(i=i, dr=d,
                        ok=support_count(lines, support_keys, d, i) >= C['support_min']))

    out = []
    for n, mo in enumerate(moments(ann), 1):
        d = mo['dr']
        cc = lambda i, _d=d: float(combined_coil({k: {rr: lines[k][rr][i] for rr in ROLES} for k in keys},
                                                 keys, _d))
        p, conf = release(cc, mo['i0'], mo['i1'], lag, last_bar=len(ts) - 1)
        ex = coil_exit.resolve(mo, p, conf, legs[d], lag, look, bool(C['gap_fill']))
        out.append(dict(n=n, mo=mo, cc=cc, **ex))
    return ts, out


def main(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument('--knobs'); a.add_argument('--from', dest='w0'); a.add_argument('--to', dest='w1')
    a.add_argument('--md', action='store_true')
    a.add_argument('--bank', action='store_true',
                   help='write the seven banked columns to %s and exit' % LEASH_TABLE)
    o = a.parse_args(argv)

    db = DatabaseManager(**get_db_config()); db.connect()
    C = v3_config(db)
    knobs = o.knobs or db.execute(
        f'SELECT wdv_knobs k FROM {V3} GROUP BY 1 ORDER BY MAX(wdv_ms) DESC LIMIT 1', fetch=True)[0]['k']
    rng = db.execute(f'SELECT MIN(wdv_utc) a, MAX(wdv_utc) b FROM {V3} WHERE wdv_knobs=%s',
                     (knobs,), fetch=True)[0]
    w0 = o.w0 or str(rng['a']); w1 = o.w1 or str(rng['b'] + dt.timedelta(seconds=1))
    ts, rows = walk(db, C, knobs, w0, w1)

    U = lambda i: dt.datetime.fromtimestamp(int(ts[i]) / 1000.0, dt.timezone.utc).replace(tzinfo=None)
    if o.bank:
        kn = knob_string(C); win = '%s..%s' % (w0, w1)
        payload = [dict(n=r['n'], source=('CONFIRM' if r['via'] == coil_exit.CONFIRMED else 'END'),
                        dr=r['mo']['dr'],
                        act_utc=U(r['actionable']), act_ms=int(ts[r['actionable']]),
                        sig_utc=(U(r['rev']) if r['rev'] is not None else None),
                        sig_ms=(int(ts[r['rev']]) if r['rev'] is not None else None),
                        rows=r['mo']['rows'],
                        first_utc=U(r['mo']['i0']), first_ms=int(ts[r['mo']['i0']]))
                   for r in rows]
        w, ex = bank(db, payload, kn, knobs, win)
        db.disconnect()
        print('  %s' % LEASH_TABLE)
        print('  wsl_knobs    %s' % kn)
        print('  wsl_v3_knobs %s' % knobs)
        print('  wsl_win      %s' % win)
        print('  %s' % ('%d rows already banked at this key - nothing written' % ex if ex
                        else 'banked %d rows' % w))
        return 0
    db.disconnect()

    T = lambda i: dt.datetime.fromtimestamp(int(ts[i]) / 1000.0, dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    hdr = ('#', 'source', 'dr', 'ACTIONABLE', 'signal', 'rows', 'moment first', 'named bar',
           'coil at named', 'sig gap s', 'was actionable', 'pulled fwd s', 'coil at actionable')
    if o.md:
        print('|'.join(hdr))
    else:
        print(f'  {V3} knobs {knobs}')
        print(f'  window {w0} -> {w1}   config v{C.version}')
        print(f"  coil {'+'.join(C['coil_lines'])}   support >= {C['support_min']}   "
              f"confirm {C['confirm_lag_s']} s   lookback {C['lookback_s']} s   "
              f"gap_fill {C['gap_fill']}   grid {C['grid_s']} s")
        print(f"  MINE, unruled by Joe: {', '.join(C.mine_keys())}")
        print()
        print('  %-4s %-8s %4s %-19s %-19s %5s %-19s %-19s %9s %9s %-19s %11s %9s' % hdr)
    tally = {}
    for r in rows:
        mo, cc = r['mo'], r['cc']
        tally[r['via']] = tally.get(r['via'], 0) + 1
        src = 'CONFIRM' if r['via'] == coil_exit.CONFIRMED else 'END'
        rev = T(r['rev']) if r['rev'] is not None else '-'
        gap = str((r['rev'] - r['actionable']) * C['grid_s']) if r['rev'] is not None else '-'
        vals = (r['n'], src, '%+d' % mo['dr'], T(r['actionable']), rev, mo['rows'], T(mo['i0']),
                T(r['named']), '%.1f' % cc(r['named']), gap, T(r['base']),
                (r['base'] - r['actionable']) * C['grid_s'], '%.1f' % cc(r['actionable']))
        print('|'.join(str(v) for v in vals) if o.md else
              '  %-4d %-8s %4s %-19s %-19s %5d %-19s %-19s %9s %9s %-19s %11d %9s' % vals)
    if not o.md:
        print()
        for k in (coil_exit.CONFIRMED, coil_exit.LOOKBACK, coil_exit.GAP, coil_exit.FORWARD):
            print('  %-10s %4d of %d' % (k, tally.get(k, 0), len(rows)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
