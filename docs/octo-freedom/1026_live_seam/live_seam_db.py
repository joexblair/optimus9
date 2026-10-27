"""live_seam_db - bank live_seam's firings in `l2_live_seam_event`. 1026.

Joe 1026, relayed by ac06c2 (`sidegigs/1/log.jsonl` #20): *"the events should be in the db"*. The
table, its columns and its unique key are ac06c2's (#20), on the `wsf_pxs4_exhaust_event` pattern.
Two changes, both stated in #29 and here:
    lse_tf_to    NOT NULL, 0 = no receiving line. A NULL inside a UNIQUE KEY never collides in MySQL,
                 so every re-run would have duplicated the rows with no receiver.
    lse_knobs    #20's list plus the knobs that move a row here and that list left out:
                 TRAJ_WIDTH, TRAJ_MIN_FRAC, TRAJ_MIN_TRAVEL (`towards`), GAP_PER_TF (the lift-off
                 gap), the window and the read delay.

#2 IS DERIVED, not read from events.jsonl: `live_seam_report.record` runs `live_seam.passes` over the
bar record for every adjacent pair ws1..ws12 (Joe 1026 via ac06c2 #34). The pass range is in lse_knobs
as PT1-11, so rows from before the widening are a different signature.

lse_ladder, Joe 1026 via ac06c2 #31. #1 rows: ws1r..ws12r at the firing bar, on the read that fired,
read from the bar record - every bar already stores all 21 values for both reads, so nothing was
added to the run. #2 rows: the rung scan the run recorded.

ONE JOB: turn one run folder's jsonl into rows. It measures nothing. Every value is what live_seam
recorded, except the columns that need later bars - dwell, survives close, wob 12 - which come from
`live_seam_report.post_hoc`, and the pairing, which is `live_seam_report.pair`, so the table and the
report cannot disagree. Those columns stay NULL until the bars that decide them exist.

SEPARATE FROM THE RUN on purpose: adding the writer did not touch the measurement loop. Every write
is an upsert on the unique key, so a re-run is safe.

    python3 live_seam_db.py backfill <run_dir> [<run_dir> ...]
    python3 live_seam_db.py follow <run_dir>        # every 5 s until the run's last bar, then a final pass
"""
import datetime as dt
import json
import os
import sys
import time

import numpy as np

import live_seam as LS
import live_seam_report as R

TABLE = 'l2_live_seam_event'
EVENT = {1: '#1 b oob->ib', 2: '#2 baton', 3: '#3 Mage oob', 4: '#4 r oob'}
ROLE = {1: 'b', 2: 'r', 3: 'Mage', 4: 'r'}
COLS = ('lse_run', 'lse_knobs', 'lse_dt_created', 'lse_read', 'lse_event', 'lse_utc', 'lse_role', 'lse_tf_from',
        'lse_tf_to', 'lse_side', 'lse_val_a', 'lse_val_b', 'lse_b_src_utc', 'lse_b_age_s', 'lse_dwell_s',
        'lse_survives_close', 'lse_wob12', 'lse_receiver_found', 'lse_rev_from_raw', 'lse_rev_from_stamp',
        'lse_rev_to_raw', 'lse_rev_to_stamp', 'lse_pxs', 'lse_ladder', 'lse_note')
KEY = ('lse_run', 'lse_knobs', 'lse_read', 'lse_event', 'lse_tf_from', 'lse_tf_to', 'lse_side', 'lse_utc')

DDL = """CREATE TABLE IF NOT EXISTS %s (
  lse_pk bigint NOT NULL AUTO_INCREMENT,
  lse_run int NOT NULL,
  lse_knobs varchar(160) COLLATE utf8mb4_unicode_ci NOT NULL,
  lse_dt_created datetime NOT NULL,
  lse_read char(1) COLLATE utf8mb4_unicode_ci NOT NULL,
  lse_event varchar(24) COLLATE utf8mb4_unicode_ci NOT NULL,
  lse_utc datetime NOT NULL,
  lse_role varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL,
  lse_tf_from smallint NOT NULL,
  lse_tf_to smallint NOT NULL DEFAULT '0',
  lse_side tinyint NOT NULL,
  lse_val_a double DEFAULT NULL,
  lse_val_b double DEFAULT NULL,
  lse_b_src_utc datetime DEFAULT NULL,
  lse_b_age_s int DEFAULT NULL,
  lse_dwell_s int DEFAULT NULL,
  lse_survives_close tinyint DEFAULT NULL,
  lse_wob12 tinyint DEFAULT NULL,
  lse_receiver_found tinyint DEFAULT NULL,
  lse_rev_from_raw datetime DEFAULT NULL,
  lse_rev_from_stamp datetime DEFAULT NULL,
  lse_rev_to_raw datetime DEFAULT NULL,
  lse_rev_to_stamp datetime DEFAULT NULL,
  lse_pxs double DEFAULT NULL,
  lse_ladder varchar(400) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  lse_pair_pk bigint DEFAULT NULL,
  lse_note varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  PRIMARY KEY (lse_pk),
  UNIQUE KEY uq_lse (lse_run, lse_knobs, lse_read, lse_event, lse_tf_from, lse_tf_to, lse_side, lse_utc),
  KEY k_lse_bar (lse_utc)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""" % TABLE


LADDER_DDL = ("ALTER TABLE %s ADD COLUMN lse_ladder varchar(400) COLLATE utf8mb4_unicode_ci NOT NULL "
              "DEFAULT '' AFTER lse_pxs" % TABLE)


def ladder_1(rec, read):
    """#1's r ladder, Joe 1026: *"at the ws1b oob to ib event, capture the r values of the ws1-12 lines"*.

    ws1r..ws12r at the firing bar, on the read that fired, each with the side it is ex-fence on: H at
    or above the high fence, L at or below the low, - neither. BOTH SIDES, not "the target side": this
    harness has no trade side, and a side is an input, never derived here.
    """
    v = rec['a'] if read == 'A' else rec['b']
    out = []
    for t in LS.R_TFS:
        x = v['ws%dr' % t]
        f = '-' if x is None else ('H' if LS.K.ex_fence(x, 1) else ('L' if LS.K.ex_fence(x, -1) else '-'))
        out.append('ws%dr %s %s' % (t, 'nan' if x is None else '%.2f' % x, f))
    return '; '.join(out)


def knobs(meta):
    """The signature of every knob that can move a row. -> str, <= 160 chars."""
    K = LS.K
    sp = {n: meta['overrides'][n][1] for n in ('ws1b', 'ws1r', 'ws5Mage')}
    s = ('OOB%g RF%g LP%d LT%g LW%d GPT%g TW%g TF%g TT%g HOP%d MAX%d PT%d-%d W%s+%s D%d b%s r%s M%s' % (
        K.OOB_FNC, K.RMOM_FNC, K.LIFT_PTS, K.LIFT_TOL, K.LIFT_WOB, K.GAP_PER_TF, K.TRAJ_WIDTH, K.TRAJ_MIN_FRAC,
        K.TRAJ_MIN_TRAVEL, K.L2_LIN_HOP, K.L2_MOM_MAXTF, LS.PASS_TFS[0], LS.PASS_TFS[-1],
        meta['lookback_h'], meta['warmup_h'], meta['delay_ms'],
        *[''.join(c for c in sp[n] if c.isalnum() or c in '.,') for n in ('ws1b', 'ws1r', 'ws5Mage')]))
    assert len(s) <= 160, s
    return s


def _dt(u):
    return None if u is None else dt.datetime.strptime(u, '%Y-%m-%d %H:%M:%S')


def _scan(e):
    """#2's rung scan: value, ex-fence on the row's side, towards that side."""
    if 'rungs' not in e:
        return 'not recorded by this run'
    return '; '.join('%s %s ex %s tw %s' % (r['line'], 'nan' if r['value'] is None else '%.2f' % r['value'],
                                           'y' if r['ex_fence'] else 'n', 'y' if r['towards'] else 'n')
                     for r in e['rungs'])


def rows(rd, final, dcache=None):
    """Every row of one run, as {key: (column tuple)}, plus the pairs. `final` = the run has ended.

    #2 comes from `live_seam_report.record`, derived over PASS_TFS; `dcache` carries it between passes.
    """
    meta, seed, bars, evs, ts, A, B = R.record(rd, dcache)
    for b in bars:                                    # the B the run recorded IS series() over its A
        if b.get('b'):
            i = int(np.searchsorted(ts, b['ts']))
            for n in LS.NAMES:
                rec = b['b'][n]
                assert (rec is None and np.isnan(B[n][i])) or rec == B[n][i], 'recorded B differs on %s' % n
    idx = {int(t): i for i, t in enumerate(ts)}
    pxs = {b['ts']: b.get('pxs') for b in bars}
    brec = {b['ts']: b for b in bars}
    run = int(bars[0]['ts'] // 1000)
    kn = knobs(meta)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0, tzinfo=None)
    out = {}
    for e in evs:
        ev = e['ev']
        L = e['lines']
        n0 = L[0]
        tf_to = LS.tf_of(L[1]) if (ev == 2 and e['kind'] == 'fire') else 0
        dwell = bc = w12 = None
        note = []
        if ev != 2:
            X = A if e['read'] == 'A' else B
            nb, open_end, bc, w12 = R.post_hoc(ts, X, idx[int(e['ts'])], n0, ev, e['side'])
            if not open_end:
                dwell = nb * 5
            elif final:
                note.append('state still true at the run end: dwell >= %d s' % (nb * 5))
            lad = ladder_1(brec[e['ts']], e['read']) if ev == 1 else ''
        else:
            note.append('why: %s' % e['why'])
            if e['kind'] == 'fire':
                note.append('receiver %s A %.4f B %.4f' % (L[1], e['a'][L[1]], e['b'][L[1]]))
            lad = _scan(e)
        h, r = e.get('rev_hand'), e.get('rev_recv')
        row = dict(lse_run=run, lse_knobs=kn, lse_dt_created=now, lse_read=e['read'], lse_event=EVENT[ev],
                   lse_utc=_dt(e['utc']), lse_role=ROLE[ev], lse_tf_from=LS.tf_of(n0), lse_tf_to=tf_to,
                   lse_side=int(e['side']), lse_val_a=e['a'][n0], lse_val_b=e['b'][n0],
                   lse_b_src_utc=_dt(e['b_src'][n0]), lse_b_age_s=e['b_age'][n0], lse_dwell_s=dwell,
                   lse_survives_close=None if bc is None else int(bc), lse_wob12=None if w12 is None else int(w12),
                   lse_receiver_found=(int(e['kind'] == 'fire') if ev == 2 else None),
                   lse_rev_from_raw=_dt(h['raw_utc']) if h else None, lse_rev_from_stamp=_dt(h['stamp_utc']) if h else None,
                   lse_rev_to_raw=_dt(r['raw_utc']) if r else None, lse_rev_to_stamp=_dt(r['stamp_utc']) if r else None,
                   lse_pxs=pxs.get(e['ts']), lse_ladder=lad[:400], lse_note='; '.join(note)[:255])
        out[tuple(row[k] for k in KEY)] = tuple(row[c] for c in COLS)
    pairs = [(a, b) for a, b in R.pair(evs) if a is not None and b is not None]
    return run, kn, out, pairs


def _key_of(run, kn, e):
    ev = e['ev']
    tf_to = LS.tf_of(e['lines'][1]) if (ev == 2 and e['kind'] == 'fire') else 0
    return (run, kn, e['read'], EVENT[ev], LS.tf_of(e['lines'][0]), tf_to, int(e['side']), _dt(e['utc']))


SQL = ('INSERT INTO %s (%s) VALUES (%s) ON DUPLICATE KEY UPDATE %s' % (
    TABLE, ', '.join(COLS), ', '.join(['%s'] * len(COLS)),
    ', '.join('%s=VALUES(%s)' % (c, c) for c in COLS if c not in KEY and c != 'lse_dt_created')))


def sync(db, rd, final, cache, dcache=None):
    """Upsert the rows that changed since the last call, then the pair links. -> rows written."""
    run, kn, out, pairs = rows(rd, final, dcache)
    ch = [v for k, v in out.items() if cache.get(k) != v[:2] + v[3:]]   # ignore dt_created in the compare
    if ch:
        db.executemany(SQL, ch)
        for v in ch:
            cache[tuple(v[COLS.index(k)] for k in KEY)] = v[:2] + v[3:]
    if pairs:
        got = db.execute('SELECT lse_pk, lse_read, lse_event, lse_tf_from, lse_tf_to, lse_side, lse_utc, lse_pair_pk '
                         'FROM %s WHERE lse_run=%%s AND lse_knobs=%%s' % TABLE, (run, kn), fetch=True)
        pk = {(run, kn, g['lse_read'], g['lse_event'], g['lse_tf_from'], g['lse_tf_to'], g['lse_side'], g['lse_utc']):
              (g['lse_pk'], g['lse_pair_pk']) for g in got}
        for a, b in pairs:
            ap, bp = pk[_key_of(run, kn, a)], pk[_key_of(run, kn, b)]
            if bp[1] != ap[0]:
                db.execute('UPDATE %s SET lse_pair_pk=%%s WHERE lse_pk=%%s' % TABLE, (ap[0], bp[0]))
    return len(ch)


def main():
    cmd, dirs = sys.argv[1], sys.argv[2:]
    db = LS.DatabaseManager(**LS.get_db_config()); db.connect()
    db.execute(DDL)
    if not db.execute("SHOW COLUMNS FROM %s LIKE 'lse_ladder'" % TABLE, fetch=True):
        db.execute(LADDER_DDL)
    if cmd == 'backfill':
        for rd in dirs:
            n = sync(db, rd, True, {})
            print('%s: %d rows written' % (rd, n), flush=True)
        return
    rd = dirs[0]
    meta = json.load(open(LS.paths(rd)[0]))
    seed_to = int(dt.datetime.strptime(meta['seed_to'], '%Y-%m-%d %H:%M:%S')
                  .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    last = seed_to + int(meta['hours'] * 3600_000)            # the run's last live bar
    cache, dcache = {}, {}
    while True:
        bars_path = LS.paths(rd)[2]
        done = False
        with open(bars_path) as fh:
            tail = fh.readlines()[-1:] if os.path.getsize(bars_path) else []
        if tail and json.loads(tail[0])['ts'] >= last:
            done = True
        try:
            n = sync(db, rd, done, cache, dcache)
            if n:
                print('%s %d rows written' % (LS.utc(time.time() * 1000), n), flush=True)
        except Exception as e:                                 # a write failure must be seen, not end the follow
            print('%s sync failed: %s: %s' % (LS.utc(time.time() * 1000), type(e).__name__, e), flush=True)
        if done:
            print('final pass done', flush=True)
            return
        time.sleep(5)


if __name__ == '__main__':
    main()
