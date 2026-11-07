"""Bank every actionable fdm2 leg event in `fdm2_leg_event`. HIS 1107 list, HIS 1107 go.

HIS ASK, verbatim: *"actioanable events to cache (and to report on in the leg report) -cadence
window open -cadence window closed -any race results -grace walk events -50% test decisions
-4-pronged-exfence-test decisions -ws{TF}x cross -fdm-momo2 decisions -rev-trade signal -exit
event"*, and on the infrastructure: *"DB tables are in your wheelhouse - you have complete control
of the infra"*.

ONE TABLE, NULLABLE PER-KIND COLUMNS, on the `l2_live_seam_event` pattern - the house style for a
timeline of several event kinds that share a spine. A table per kind would split one leg's timeline
across ten joins to read it back in order, which is the opposite of what a leg report is for.

THE UNIQUE KEY CARRIES THE KNOBS, which is his own standing rule and the fault that bit us on
1106: ab_legs.json held 2,453 decision rows with no record of which knobs produced them, so a leg
report replayed a superseded arm and printed two identical arms for two different mechs. A cached
row that cannot say what produced it is a trap.

  f2e_knobs      a 12-char sha256 over EVERY banked knob's live value. Any knob move is a new key,
                 so an old arm's rows are never mistaken for the current one
  f2e_tape_end   the tape's last bar. A different tape is different rows
  f2e_seq        0 for the first row of a (leg, bar, kind, tf). It exists because MySQL lets two
                 genuinely distinct events collide on a key, and a silent overwrite is worse than a
                 duplicate - the re-entry producer already emits two signals on one bar

EVERY WRITE IS AN UPSERT on that key, so a re-run is safe and never duplicates.

NOTHING HERE MEASURES ANYTHING. It turns the rows v4_fdm2.legs already produced into table rows.
The 4-pronged-exfence-test's rows will appear the moment the 1107 redesign builds them; this module
needs no change for that, because the kind is a column and not a schema.

    python3 out/fdm2_event_db.py ddl                     create or verify the table
    python3 out/fdm2_event_db.py bank <day> [<day> ...]  run those days' chains and bank them
    python3 out/fdm2_event_db.py show <day>              read the day's rows back, in bar order
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

TABLE = 'fdm2_leg_event'

#   THE OWNERS, his 1106/1107 prefixes. The column is derived from the kind so a reader never has
#   to know the prefix rules, and an unprefixed kind is flagged rather than guessed at.
OWNER = {'cad': 'the cadence event', 'cwlk': 'the cad walk', 'cwsx': 'the ws{TF}x-cross event',
         'leg': 'the leg'}

COLS = ('f2e_knobs', 'f2e_tape_end', 'f2e_dt_created', 'f2e_arm',
        'f2e_leg_open', 'f2e_leg_side', 'f2e_leg_src', 'f2e_leg_exit', 'f2e_leg_ctype',
        'f2e_leg_mae', 'f2e_leg_mfe', 'f2e_leg_rel',
        'f2e_utc', 'f2e_bar', 'f2e_kind', 'f2e_owner', 'f2e_seq', 'f2e_tf',
        'f2e_ev_utc', 'f2e_k', 'f2e_n', 'f2e_pct', 'f2e_votes', 'f2e_rpred', 'f2e_mx', 'f2e_pin',
        'f2e_why')
KEY = ('f2e_knobs', 'f2e_tape_end', 'f2e_leg_open', 'f2e_utc', 'f2e_kind', 'f2e_tf', 'f2e_seq')

DDL = """CREATE TABLE IF NOT EXISTS %s (
  f2e_pk bigint NOT NULL AUTO_INCREMENT,
  f2e_knobs varchar(16) NOT NULL,
  f2e_tape_end datetime NOT NULL,
  f2e_dt_created datetime NOT NULL,
  f2e_arm varchar(32) NOT NULL DEFAULT '',
  f2e_leg_open datetime NOT NULL,
  f2e_leg_side tinyint NOT NULL,
  f2e_leg_src varchar(255) NOT NULL DEFAULT '',
  f2e_leg_exit datetime NOT NULL,
  f2e_leg_ctype varchar(48) NOT NULL DEFAULT '',
  f2e_leg_mae double DEFAULT NULL,
  f2e_leg_mfe double DEFAULT NULL,
  f2e_leg_rel double DEFAULT NULL,
  f2e_utc datetime NOT NULL,
  f2e_bar bigint NOT NULL,
  f2e_kind varchar(32) NOT NULL,
  f2e_owner varchar(32) NOT NULL DEFAULT '',
  f2e_seq smallint NOT NULL DEFAULT '0',
  f2e_tf smallint NOT NULL DEFAULT '0',
  f2e_ev_utc datetime DEFAULT NULL,
  f2e_k smallint DEFAULT NULL,
  f2e_n smallint DEFAULT NULL,
  f2e_pct double DEFAULT NULL,
  f2e_votes tinyint DEFAULT NULL,
  f2e_rpred smallint DEFAULT NULL,
  f2e_mx smallint DEFAULT NULL,
  f2e_pin smallint DEFAULT NULL,
  f2e_why text,
  PRIMARY KEY (f2e_pk),
  UNIQUE KEY uq_f2e (f2e_knobs, f2e_tape_end, f2e_leg_open, f2e_utc, f2e_kind, f2e_tf, f2e_seq),
  KEY k_f2e_bar (f2e_utc),
  KEY k_f2e_leg (f2e_leg_open),
  KEY k_f2e_kind (f2e_kind)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""" % TABLE

_e = sys.stderr
sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_fdm2 as F2
    import v4_signal as SG
    import v4_fdm_reentry as RE
    import ln
    import re_sigcache as SC
    from optimus9 import DatabaseManager
    from optimus9.config import get_db_config
finally:
    sys.stderr = _e


def knob_hash():
    """12 hex chars over every banked knob's live value. -> str."""
    items = sorted((n, str(getattr(K, n, None))) for n in K.RULED)
    return hashlib.sha256('|'.join('%s=%s' % kv for kv in items).encode()).hexdigest()[:12]


def arm():
    """A short human label for the arm, so a reader does not have to decode the hash. -> str."""
    off = [n for n in K.RULED if str(getattr(K, n, None)) != str(K.RULED[n][0])]
    return ('banked' if not off
            else ','.join('%s=%s' % (n.replace('FDM2_MOMO_', 'momo_').replace('FDM_', ''),
                                     getattr(K, n)) for n in sorted(off))[:32])


def owner_of(kind):
    return OWNER.get(str(kind).split('_')[0], 'UNPREFIXED - %s' % kind)


def rows_for(LN, LG):
    """Every leg's events as table rows, chronological inside each leg. -> [tuple].

    THE LEG'S OWN EVENTS ARE INCLUDED - the open, the rev-trade signal and the exit - because his
    list names the last two and a timeline without its open cannot be read.
    """
    now = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None, microsecond=0)
    te = dt.datetime.strptime(ln.U(len(LN['close']) - 1), '%Y-%m-%d %H:%M:%S')
    h, a = knob_hash(), arm()
    out, seen = [], {}
    for L in LG:
        base = (h, te, now, a, ln.U(int(L['opn'])), int(L['side']), str(L['src']),
                ln.U(int(L['exit'])), str(L['ctype']), abs(float(L['mae'])), float(L['mfe']),
                float(L['rel']))
        ev = [(int(L['opn']), 'leg_open', 0, None, {}, 'the leg opens - %s at %s, %s'
               % ('LONG' if int(L['side']) > 0 else 'SHORT', ln.U(int(L['opn'])), L['src']))]
        for r in L['rows']:
            ev.append((int(r['bar']), str(r['stage']), int(r.get('xtf') or 0),
                       r.get('ev'), r, str(r['why'])))
        if L['sig'] is not None:
            ev.append((int(L['sig']), 'leg_rev_trade_signal', 0, None, {},
                       'the rev-trade signal - the router closes at signal + 1'))
        ev.append((int(L['exit']), 'leg_exit', 0, None, {},
                   'the leg exits - %s, realised %+.3f%%' % (L['ctype'], float(L['rel']))))
        for bar, kind, tf, evb, r, why in sorted(ev, key=lambda z: (z[0], z[1])):
            kk = (ln.U(int(L['opn'])), ln.U(bar), kind, tf)
            seq = seen.get(kk, 0)
            seen[kk] = seq + 1
            out.append(base + (ln.U(bar), bar, kind, owner_of(kind), seq, tf,
                               ln.U(int(evb)) if evb is not None else None,
                               r.get('k'), r.get('n'),
                               float(r['pct']) if r.get('pct') is not None else None,
                               r.get('votes'), r.get('rpred'), r.get('mx'), r.get('pin'),
                               why))
    return out


def upsert(db, rows):
    """Upsert on the unique key. -> the row count sent."""
    if not rows:
        return 0
    ph = ', '.join(['%s'] * len(COLS))
    upd = ', '.join('%s=VALUES(%s)' % (c, c) for c in COLS if c not in KEY)
    db.executemany('INSERT INTO %s (%s) VALUES (%s) ON DUPLICATE KEY UPDATE %s'
                   % (TABLE, ', '.join(COLS), ph, upd), rows)
    return len(rows)


def chain(LN, SIGS, day):
    A, B = ln.K(day + ' 00:00:00'), ln.K(day + ' 23:59:55')
    hit = [x for x in SIGS if int(x['bar']) >= A]
    assert hit, 'no fdm re-entry signal at or after %s' % ln.U(A)
    g = hit[0]
    return F2.legs(LN, (SG.fire_bar(g), SG.target_side(SG.direction(int(g['side']))),
                        'fdm re-entry %s' % ln.U(int(g['bar']))), B, resig=SIGS)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'ddl'
    db = DatabaseManager(**get_db_config())
    db.connect()
    try:
        db.execute(DDL)
        if cmd == 'ddl':
            c = db.execute('describe ' + TABLE, fetch=True)
            print('| the column | type | null | key | default |')
            print('|---|---|---|---|---|')
            for r in (c or []):
                print('| %s | %s | %s | %s | %s |'
                      % (r['Field'], r['Type'], r['Null'], r['Key'] or '-',
                         '-' if r['Default'] is None else r['Default']))
            return
        if cmd == 'bank':
            LN = F2.load()
            SIGS, info = SC.load_or_build(K, RE, LN['B1'], LN['CPR'], LN['G30B'], LN['EMR'],
                                          LN['CPM'])
            print('| the run | value |')
            print('|---|---|')
            print('| the tape | %d bars, ends %s |' % (len(LN['close']),
                                                       ln.U(len(LN['close']) - 1)))
            print('| the signal cache | %s, key %s |'
                  % ('HIT' if info['hit'] else 'built', info['key']))
            print('| the knob hash | %s |' % knob_hash())
            print('| the arm | %s |' % arm())
            print()
            print('| the day | legs | rows banked |')
            print('|---|---|---|')
            for day in sys.argv[2:]:
                LG = chain(LN, SIGS, day)
                n = upsert(db, rows_for(LN, LG))
                print('| %s | %d | %d |' % (day, len(LG), n))
            return
        if cmd == 'show':
            day = sys.argv[2]
            q = db.execute("SELECT f2e_utc, f2e_kind, f2e_owner, f2e_leg_open, f2e_tf, f2e_why "
                           "FROM %s WHERE f2e_knobs=%%s AND DATE(f2e_leg_open)=%%s "
                           "ORDER BY f2e_leg_open, f2e_utc, f2e_kind" % TABLE,
                           (knob_hash(), day), fetch=True)
            print('| the bar | the kind | the owner | the leg | tf | why |')
            print('|---|---|---|---|---|---|')
            for r in (q or []):
                print('| %s | %s | %s | %s | %s | %s |'
                      % (r['f2e_utc'], r['f2e_kind'], r['f2e_owner'], r['f2e_leg_open'],
                         r['f2e_tf'] or '-',
                         str(r['f2e_why']).replace('|', '\\|')[:150]))
            return
        raise SystemExit('unknown command %r' % cmd)
    finally:
        db.disconnect()


if __name__ == '__main__':
    main()
