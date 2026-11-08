"""HIS per-day stop rulings in `c3r_stop_day`, with the measured leg travel beside them.

HIS 1108 ASK, verbatim: *"instead of answering the 4 questions, I'd like to tell you which days I
see that need a larger or smaller stop. for example, 0825 (and possibly the days befor and after)
needs a 2% stop / I think our baseline is 1.1, but that could be wrong / the answers will come over
time, so this data needs its own db table to assist the build"*, and his standing *"DB tables are
in your wheelhouse - you have complete control of the infra"*.

TWO TABLES, and the split is the point.

  c3r_stop_day   HIS rulings. One row per UTC day, his stop percent and his words. Nothing
                 computes a row here - only he does. A day with no row falls back to the baseline.
  c3r_leg_mfe    THE MEASUREMENT. One row per (day, timeframe): how far that Mage's legs travelled
                 on that day, from v4_sweep_pivots' own legs. He reads it beside his own ruling so
                 a later ruling has the numbers under it.

WHY NOT ONE TABLE. His rulings are sparse, hand-entered and permanent; the measurement is dense,
recomputed whenever a knob moves, and carries a knob hash. Putting them in one table would make a
rebuild of the measurement able to overwrite one of his rulings, which is the one thing that must
never happen.

THE MEASUREMENT CARRIES THE KNOB HASH, his standing rule. SP_XWOB and SP_TFS both change which
legs exist, so a row that cannot say what produced it is a trap. HIS RULINGS DO NOT carry one - a
ruling is his reading of the chart and no knob moves it.

NO DAY IS INVENTED. `bank` writes only the days it is given.

    python3 out/c3r_stop_db.py ddl                        create or verify both tables
    python3 out/c3r_stop_db.py set <day> <pct> [note]     HIS ruling for that day
    python3 out/c3r_stop_db.py drop <day>                 remove his ruling for that day
    python3 out/c3r_stop_db.py rulings                    every ruling he has given, by day
    python3 out/c3r_stop_db.py measure <day> [<day>...]  bank the leg travel for those days
    python3 out/c3r_stop_db.py show <from> <to>           his rulings beside the measurement
"""
import datetime as dt
import hashlib
import io
import os
import sys

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
os.environ.setdefault('W_V4_EXPERIMENT', '1')

T_RULE = 'c3r_stop_day'
T_MFE = 'c3r_leg_mfe'

DDL_RULE = """CREATE TABLE IF NOT EXISTS %s (
  csd_pk bigint NOT NULL AUTO_INCREMENT,
  csd_day date NOT NULL,
  csd_stop_pct double NOT NULL,
  csd_note text,
  csd_dt_set datetime NOT NULL,
  PRIMARY KEY (csd_pk),
  UNIQUE KEY uq_csd (csd_day)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""" % T_RULE

DDL_MFE = """CREATE TABLE IF NOT EXISTS %s (
  clm_pk bigint NOT NULL AUTO_INCREMENT,
  clm_knobs varchar(16) NOT NULL,
  clm_tape_end datetime NOT NULL,
  clm_day date NOT NULL,
  clm_tf varchar(24) NOT NULL,
  clm_legs int NOT NULL,
  clm_mfe_min double DEFAULT NULL,
  clm_mfe_p25 double DEFAULT NULL,
  clm_mfe_med double DEFAULT NULL,
  clm_mfe_p75 double DEFAULT NULL,
  clm_mfe_max double DEFAULT NULL,
  clm_len_med double DEFAULT NULL,
  clm_dt_created datetime NOT NULL,
  PRIMARY KEY (clm_pk),
  UNIQUE KEY uq_clm (clm_knobs, clm_tape_end, clm_day, clm_tf),
  KEY k_clm_day (clm_day)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""" % T_MFE

TFS = ('ws1Mage', 'ws2Mage', 'ws3Mage', 'gcws30Mage')

_e = sys.stderr
sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_sweep_pivots as SP
    import ln
    from optimus9 import DatabaseManager
    from optimus9.config import get_db_config
finally:
    sys.stderr = _e

EM = dt.datetime.strptime(os.environ['LG_TAPE_END'], '%Y-%m-%d')


def knob_hash():
    """12 hex chars over every banked knob's live value. -> str."""
    items = sorted((n, str(getattr(K, n, None))) for n in K.RULED)
    return hashlib.sha256('|'.join('%s=%s' % kv for kv in items).encode()).hexdigest()[:12]


def db():
    _s = sys.stderr; sys.stderr = io.StringIO()
    d = DatabaseManager(**get_db_config()); d.connect()
    sys.stderr = _s
    return d


def ddl():
    d = db()
    try:
        for q in (DDL_RULE, DDL_MFE):
            d.execute(q)
        print('%s and %s are ready' % (T_RULE, T_MFE))
    finally:
        d.disconnect()


def set_rule(day, pct, note=''):
    """HIS ruling for one day. -> None. An upsert, so correcting a day is one call."""
    d = db()
    try:
        d.execute('INSERT INTO %s (csd_day, csd_stop_pct, csd_note, csd_dt_set) '
                  'VALUES (%%s, %%s, %%s, %%s) ON DUPLICATE KEY UPDATE '
                  'csd_stop_pct=VALUES(csd_stop_pct), csd_note=VALUES(csd_note), '
                  'csd_dt_set=VALUES(csd_dt_set)' % T_RULE,
                  (str(day), float(pct), str(note),
                   dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)))
        print('%s -> %.3f%%%s' % (day, float(pct), ' | %s' % note if note else ''))
    finally:
        d.disconnect()


def drop_rule(day):
    d = db()
    try:
        d.execute('DELETE FROM %s WHERE csd_day=%%s' % T_RULE, (str(day),))
        print('%s removed' % day)
    finally:
        d.disconnect()


def rulings():
    """Every ruling he has given. -> {date str: (pct, note)}."""
    d = db()
    try:
        r = d.execute('SELECT csd_day, csd_stop_pct, csd_note FROM %s ORDER BY csd_day' % T_RULE,
                      fetch=True) or []
    finally:
        d.disconnect()
    return {str(x['csd_day']): (float(x['csd_stop_pct']), str(x['csd_note'] or '')) for x in r}


def stop_for(day, base=None):
    """The stop percent for one UTC day. -> (percent, where it came from).

    HIS ruling if he has given one for that day, otherwise the baseline. His 1108: *"I think our
    baseline is 1.1, but that could be wrong"* - so the baseline is `FDM2_C3R_STOP_BASE`, a knob,
    and not a literal sitting in this function.
    """
    b = float(K.FDM2_C3R_STOP_BASE if base is None else base)
    r = rulings().get(str(day))
    return (r[0], 'HIS ruling: %s' % r[1] if r[1] else 'HIS ruling') if r else (b, 'the baseline')


def measure(days):
    """Bank the leg travel for those UTC days, per timeframe. -> rows written."""
    import numpy as np
    close = np.asarray(SP.px(), float) if hasattr(SP, 'px') else None
    if close is None:
        import v4_backstop_trades as BT
        close = np.asarray(BT.prices()[0], float)
    xw = int(K.SP_XWOB)
    kh, now = knob_hash(), dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
    out = []
    for tf in TFS:
        per = {}
        for o, z, sd in SP.legs(tf):
            cb = int(z) + xw - 1
            if cb >= len(close):
                continue
            seg = close[int(o):int(z) + 1]
            if not np.isfinite(seg).any():
                continue
            fav = -int(sd)
            p0 = float(np.nanmin(seg)) if fav > 0 else float(np.nanmax(seg))
            ext = float(np.nanmax(seg)) if fav > 0 else float(np.nanmin(seg))
            if p0 <= 0:
                continue
            per.setdefault(ln.U(cb)[:10], []).append((abs(ext - p0) / p0 * 100.0,
                                                      (int(z) - int(o)) * 5 / 60.0))
        for day in days:
            g = per.get(str(day), [])
            m = sorted(x[0] for x in g)
            L = sorted(x[1] for x in g)
            out.append((kh, EM, str(day), tf, len(g),
                        m[0] if m else None,
                        float(np.percentile(m, 25)) if m else None,
                        float(np.median(m)) if m else None,
                        float(np.percentile(m, 75)) if m else None,
                        m[-1] if m else None,
                        float(np.median(L)) if L else None, now))
    d = db()
    try:
        d.execute('INSERT INTO %s (clm_knobs, clm_tape_end, clm_day, clm_tf, clm_legs, '
                  'clm_mfe_min, clm_mfe_p25, clm_mfe_med, clm_mfe_p75, clm_mfe_max, clm_len_med, '
                  'clm_dt_created) VALUES ' % T_MFE
                  + ', '.join(['(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'] * len(out))
                  + ' ON DUPLICATE KEY UPDATE clm_legs=VALUES(clm_legs), '
                    'clm_mfe_min=VALUES(clm_mfe_min), clm_mfe_p25=VALUES(clm_mfe_p25), '
                    'clm_mfe_med=VALUES(clm_mfe_med), clm_mfe_p75=VALUES(clm_mfe_p75), '
                    'clm_mfe_max=VALUES(clm_mfe_max), clm_len_med=VALUES(clm_len_med), '
                    'clm_dt_created=VALUES(clm_dt_created)',
                  tuple(v for r in out for v in r))
    finally:
        d.disconnect()
    return len(out)


def show(a, b):
    """His rulings beside the measurement, one row per day. -> the markdown lines."""
    kh = knob_hash()
    d = db()
    try:
        r = d.execute('SELECT clm_day, clm_tf, clm_legs, clm_mfe_med, clm_mfe_p75, clm_mfe_max '
                      'FROM %s WHERE clm_knobs=%%s AND clm_day BETWEEN %%s AND %%s '
                      'ORDER BY clm_day, clm_tf' % T_MFE, (kh, str(a), str(b)), fetch=True) or []
    finally:
        d.disconnect()
    R = rulings()
    by = {}
    for x in r:
        by.setdefault(str(x['clm_day']), {})[str(x['clm_tf'])] = x
    out = ['| the day | HIS stop %% | where it came from | his note | '
           + ' | '.join('%s legs | %s median leg MFE %%' % (t, t) for t in TFS) + ' |',
           '|---|---|---|---|' + '---|' * (2 * len(TFS))]
    for day in sorted(by):
        pct, src = stop_for(day)
        note = R.get(day, (None, ''))[1]
        cells = []
        for t in TFS:
            x = by[day].get(t)
            cells += [str(x['clm_legs']) if x else '-',
                      '%.3f' % x['clm_mfe_med'] if x and x['clm_mfe_med'] is not None else '-']
        out.append('| %s | %.3f | %s | %s | %s |' % (day, pct, src, note or '.', ' | '.join(cells)))
    return out


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'ddl'
    if cmd == 'ddl':
        ddl()
    elif cmd == 'set':
        set_rule(sys.argv[2], sys.argv[3], ' '.join(sys.argv[4:]))
    elif cmd == 'drop':
        drop_rule(sys.argv[2])
    elif cmd == 'rulings':
        for day, (pct, note) in sorted(rulings().items()):
            print('%s | %.3f%% | %s' % (day, pct, note))
    elif cmd == 'measure':
        print('%d rows banked' % measure(sys.argv[2:]))
    elif cmd == 'show':
        print('\n'.join(show(sys.argv[2], sys.argv[3])))
    else:
        raise SystemExit(__doc__)
