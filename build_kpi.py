#!/usr/bin/env python3
"""build_kpi.py — the RPL evo-sweep KPI dashboard (Joe 0726). Fired automatically by the pulse.

Sources EVERY cell from the authoritative record — the pulse no longer hand-marks anything:
  MFE, MAE           <- latest `[HH:MM:SS] rN adopted MAE/MFE` log line
  net(IS), oos10,    <- latest `round N [...]` log line  (tnet / vnet / vmm)
  val-mm
  oos7               <- rpl_oos32.o32_oos32 (the CLEAN disjoint-7 read; latest row this cycle)
  maximin            <- min(net(IS), oos10, oos7)  [= the rotating-driver bank target]

Per-cell CHANGE HIGHLIGHT: each cell is diffed against the previous build (state file) at 3-decimal
precision — the SAME precision it's displayed at — so an unchanged value can never spuriously light up.
Changed cells are bracketed [value]; unchanged cells are bare.  First run = baseline (no prior snapshot).

Cols: leg | MFE | MAE | net(IS) | oos10 | oos7 | val-mm | maximin.  Rows: RC · RPL(climb).
Usage: python3 build_kpi.py   (prints the box; rewrites the state file for the next diff)."""
import re, json, os
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

LOG = '/home/joe/thecodes/rpl_evo.log'
STATE = '/home/joe/thecodes/.rpl_kpi_state.json'
LEGS = [('RC', 'rc', 'RC'), ('RPL (climb)', 'climb', 'RPL')]   # (display, obj-token, adopted-line-token)
# column key -> (header, inner width)
COLS = [('mfe', 'MFE', 9), ('mae', 'MAE', 9), ('net', 'net (IS)', 11),
        ('oos10', 'oos10', 10), ('oos7', 'oos7', 9), ('valmm', 'val-mm', 9)]


def _last(lines, needle_re):
    for l in reversed(lines):
        if re.search(needle_re, l):
            return l
    return None


def parse_log():
    lines = open(LOG).read().splitlines()
    rnd = _last(lines, r'round \d+ \[')
    adopt = _last(lines, r'adopted MAE/MFE')
    cyc = _last(lines, r'--- CYCLE \d+')
    out = {}
    cyc_no = int(re.search(r'--- CYCLE (\d+)', cyc).group(1)) if cyc else None
    rnd_no = int(re.search(r'round (\d+)', rnd).group(1)) if rnd else None
    drv = (re.search(r'drv:(\w+)', rnd).group(1) if rnd else None)
    stamp = (re.search(r'\[(\d\d:\d\d:\d\d)\]', adopt).group(1) if adopt else None)
    for disp, obj, tok in LEGS:
        d = {}
        if rnd:
            m = re.search(obj + r' tnet ([+-]\d+\.\d+).*?vnet ([+-]\d+\.\d+) vmm ([+-]\d+\.\d+)', rnd)
            if m:
                d['net'], d['oos10'], d['valmm'] = float(m.group(1)), float(m.group(2)), float(m.group(3))
        if adopt:
            m = re.search(tok + r' mfe ([+-]\d+\.\d+) mae ([+-]\d+\.\d+)', adopt)
            if m:
                d['mfe'], d['mae'] = float(m.group(1)), float(m.group(2))
        out[obj] = d
    return out, cyc_no, rnd_no, drv, stamp


def fetch_oos7(cyc_no):
    db = DatabaseManager(**get_db_config()); db.connect()
    res = {}
    for _, obj, _ in LEGS:
        row = db.execute('SELECT o32_oos32 v, o32_round r FROM rpl_oos32 WHERE o32_objective=%s AND o32_cycle=%s '
                         'ORDER BY o32_ts DESC LIMIT 1', (obj, cyc_no), fetch=True)   # freshest WRITE, not max round
        res[obj] = (float(row[0]['v']), int(row[0]['r'])) if row else None
    db.disconnect()
    return res


def _dwidth(s):
    return len(s) + s.count('✅')          # ✅ renders 2 cells; no wcwidth dep


def cell(val, width, d):
    s = val + ('' if d == 0 else (' ▲' if d > 0 else ' ▼'))   # ▲ rose · ▼ fell vs last pulse; 0 -> bare
    pad = width - _dwidth(s)
    lo = pad // 2
    return ' ' * lo + s + ' ' * (pad - lo)


def fmt(v):
    return '—' if v is None else '%+.3f' % v


def main():
    vals, cyc_no, rnd_no, drv, stamp = parse_log()
    o7 = fetch_oos7(cyc_no)
    # assemble per-leg cell values + maximin
    data = {}
    for disp, obj, tok in LEGS:
        d = dict(vals.get(obj, {}))
        d['oos7'] = o7[obj][0] if o7.get(obj) else None
        reads = [d.get('net'), d.get('oos10'), d.get('oos7')]
        rk = [x for x in reads if x is not None]
        mm = min(rk) if rk else None
        if None in reads:
            annot = '(o7 pend)'
        elif all(x > 0 for x in reads):
            annot = '✅ (all +)'
        elif all(x < 0 for x in reads):
            annot = '(all −)'
        else:
            annot = '(split)'
        d['maximin'] = mm; d['_annot'] = annot
        data[obj] = d

    prev = {}
    if os.path.exists(STATE):
        try:
            prev = json.load(open(STATE))
        except Exception:
            prev = {}
    baseline = not prev

    def direction(obj, key, v):
        """0 = unchanged/baseline/no-prior · +1 = rose vs last pulse · -1 = fell. Diff at 3dp = display precision."""
        if baseline or v is None:
            return 0
        pv = prev.get(obj, {}).get(key)
        if pv is None or round(pv, 3) == round(v, 3):
            return 0
        return 1 if v > pv else -1

    # ---- render ----
    W = [w for _, _, w in COLS]
    LEGW, MMW = 13, 20                      # MMW holds "[-0.398] ✅ (all +)" (dwidth 19) without breaking the border
    def bar(l, m, r):
        return l + m.join(['─' * LEGW] + ['─' * w for w in W] + ['─' * MMW]) + r
    def row(cells):
        return '│' + '│'.join(cells) + '│'
    lines = []
    lines.append(bar('┌', '┬', '┐'))
    hdr = ['leg'.center(LEGW)] + [h.center(w) for _, h, w in COLS] + ['maximin'.center(MMW)]
    lines.append(row(hdr))
    lines.append(bar('├', '┼', '┤'))
    for disp, obj, tok in LEGS:
        d = data[obj]
        cells = [' ' + disp.ljust(LEGW - 1)]
        for key, _, w in COLS:
            cells.append(cell(fmt(d.get(key)), w, direction(obj, key, d.get(key))))
        mms = fmt(d.get('maximin'))
        mmd = direction(obj, 'maximin', d.get('maximin'))
        mmg = '' if mmd == 0 else (' ▲' if mmd > 0 else ' ▼')
        mm_full = mms + mmg + ' ' + d['_annot']
        pad = MMW - _dwidth(mm_full)
        cells.append(' ' + mm_full + ' ' * max(0, pad - 1))
        lines.append(row(cells))
    lines.append(bar('└', '┴', '┘'))

    o7src = o7.get('rc')
    hdrline = 'KPI — cycle %s · round %s · drv:%s · adopt @%s   [▲ rose · ▼ fell vs last pulse]' % (
        cyc_no, rnd_no, drv, stamp)
    if baseline:
        hdrline += '   (baseline — no prior snapshot)'
    elif o7src:
        hdrline += '   (oos7 = clean-7 read, cyc%s r%s)' % (cyc_no, o7src[1])
    print(hdrline)
    print('\n'.join(lines))

    # ---- persist state for the next diff ----
    snap = {obj: {k: data[obj].get(k) for k in ('mfe', 'mae', 'net', 'oos10', 'oos7', 'valmm', 'maximin')}
            for _, obj, _ in LEGS}
    json.dump(snap, open(STATE, 'w'))


if __name__ == '__main__':
    main()
