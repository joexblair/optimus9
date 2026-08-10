"""build_tape_seq — the SETUP: when each Mage arrived at and left each boundary, and in what order.

    Joe 0803: "every trade has a setup. granted it's slower to unpack in code, but I'm in no hurry"

WHY THIS EXISTS. Everything measured across the whole session was a still frame at one bar — band
position, momo state, cross presence, cross direction, HTF ladder, arm side. Forty-two feature families,
none surviving. A still frame cannot express a setup, because a setup is an ORDER of events.

THE PRECEDENT IS JOE'S OWN. rpl_dominoes already banks dm_gcs15m_x_ms / dm_s30m_x_ms / dm_s1m_x_ms — the
three LTF-Mage crossing bars — and scores their ordering as dm_dom_strict / dm_dom_loose / dm_dom_reverse.
This is that, generalised: ten Mages instead of three, both crossing directions instead of one, and the
raw ages banked instead of three summary verdicts, so every summary stays derivable including ones not
yet thought of.

JOE'S RULINGS 0803 03:20
  the domino   BOTH directions — arrival (IB->OOB) and departure (OOB->IB), at both boundaries
  the ladder   10 Mages, one per timeframe: gcs5 5 s | gcs15 15 s | s30 30 s | s1 1 min | s2 2 min |
               s4 4 min | h30 | h45 | h60 | h90 min. All bb 37 | 0.7 | close, the rsd Mage spec.
               His BOBBING note is explicitly cross-timeframe — a Mage bobs on a boundary while a HIGHER
               TF Mage makes its way to the same one — so the ladder needs both ends.
  the shape    ORDER PLUS TIMING GAPS. Raw ages are banked, so the rank string gives the order and the
               differences give the gaps. "gcs5 then s30 then s1, 40 s apart" is a different setup from
               the same order spread over 20 minutes.

NO WINDOW. Bars-since is unbounded — however long ago the crossing was. Joe's standing rule: no cap,
horizon or window unless he sets one. A line that has never crossed banks NULL, not a truncated age.

THE COLUMNS
  sq_{a|d}_{h|l}_{line}   bars since that line's last ARRIVAL at / DEPARTURE from the HI / LO boundary.
                          40 columns: 10 lines x 2 events x 2 boundaries. NULL = never, in this tape.
  sq_rank_{a|d}_{h|l}     10 chars, one per line in ladder order, giving that line's arrival rank by
                          recency: '1' most recent ... '9', 'a' for tenth, '-' never. So the ordering is
                          a string comparison and the dominoes verdicts become queries.

CAUSAL. Every value reads only bars <= the current one.

    python3 build_tape_seq.py
"""
import os, sys, time, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '4')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_rpl_jig as J
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
from build_scn import TAPE0

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')

# ladder, fastest -> slowest. one Mage per timeframe, bb 37|0.7|close throughout.
LADDER = [('g5', 5.0 / 60), ('g15', 0.25), ('s30', 0.5), ('s1', 1.0), ('s2', 2.0), ('s4', 4.0),
          ('h30', 30.0), ('h45', 45.0), ('h60', 60.0), ('h90', 90.0)]
RANKCH = '123456789a'

COLS = ['sq_%s_%s_%s' % (e, s, nm) for e in ('a', 'd') for s in ('h', 'l') for nm, _ in LADDER]
RANKS = ['sq_rank_%s_%s' % (e, s) for e in ('a', 'd') for s in ('h', 'l')]

DDL = '''CREATE TABLE IF NOT EXISTS rpl_tape_seq (
    sq_ms BIGINT PRIMARY KEY, sq_utc VARCHAR(20),
    %s,
    %s,
    KEY (sq_rank_a_h), KEY (sq_rank_a_l), KEY (sq_rank_d_h), KEY (sq_rank_d_l)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''' % (
    ',\n    '.join('%s INT' % c for c in COLS),
    ',\n    '.join('%s VARCHAR(10)' % c for c in RANKS))


def bars_since(ev):
    """bars since the most recent True in `ev`, per bar. -1 = never yet. Causal, vectorised."""
    idx = np.arange(len(ev))
    last = np.maximum.accumulate(np.where(ev, idx, -1))
    out = np.where(last >= 0, idx - last, -1)
    return out.astype(np.int32)


def rank_string(AGES):
    """(bars, 10) ages -> per-bar 10-char rank string by recency. '-' where the age is -1 (never).
    Ties take the ladder order, which is deterministic and stated rather than arbitrary."""
    n, k = AGES.shape
    A = np.where(AGES < 0, np.iinfo(np.int32).max, AGES)
    order = np.argsort(A, axis=1, kind='stable')          # positions sorted by age ascending
    rank = np.empty_like(order)
    np.put_along_axis(rank, order, np.arange(k)[None, :].repeat(n, 0), axis=1)
    ch = np.array(list(RANKCH))[rank]
    ch[AGES < 0] = '-'
    return np.array([''.join(r) for r in ch])


def main(argv):
    HI, LO = R.HI, R.LO
    ovr = {}
    for nm, tf in LADDER:
        ovr.update(bbline('lad_%s' % nm, tf, length=37, mult=0.7, src='close'))

    d = DatabaseManager(**get_db_config()); d.connect()
    end_ms = int(d.execute('SELECT MAX(kc_timestamp) m FROM kline_collection', fetch=True)[0]['m'])
    hours = int((end_ms - TAPE0) / 3600000) + 1
    t0 = time.time()
    with Jig(end_ms, hours=hours, warmup=J.WIN_WARMUP, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64)
        V = np.vstack([np.asarray(j.W.line('lad_%s' % nm), float) for nm, _ in LADDER]).T   # (n,10)
    n = len(ts)
    print('jig build %.1f s   bars %d   ladder %d Mages' % (time.time() - t0, n, len(LADDER)), flush=True)

    AGE = {}
    for si, (sk, oob) in enumerate((('h', V >= HI), ('l', V <= LO))):
        prev = np.r_[np.zeros((1, oob.shape[1]), bool), oob[:-1]]
        arrive = oob & ~prev
        depart = (~oob) & prev
        AGE[('a', sk)] = np.column_stack([bars_since(arrive[:, k]) for k in range(len(LADDER))])
        AGE[('d', sk)] = np.column_stack([bars_since(depart[:, k]) for k in range(len(LADDER))])
        print('  %s boundary: arrivals %s   departures %s'
              % ('HI' if sk == 'h' else 'LO',
                 ' '.join('%s=%d' % (LADDER[k][0], int(arrive[:, k].sum())) for k in range(len(LADDER))),
                 ' '.join('%s=%d' % (LADDER[k][0], int(depart[:, k].sum())) for k in range(len(LADDER)))),
              flush=True)
    RK = {key: rank_string(AGE[key]) for key in AGE}
    print('ages + ranks  %.1f s' % (time.time() - t0), flush=True)
    for key in (('a', 'h'), ('a', 'l'), ('d', 'h'), ('d', 'l')):
        uq = len(np.unique(RK[key]))
        print('  rank_%s_%s : %d distinct orderings over the tape' % (key[0], key[1], uq), flush=True)

    d.execute(DDL)
    d.execute('DELETE FROM rpl_tape_seq')
    allcols = ['sq_ms', 'sq_utc'] + COLS + RANKS
    sql = 'INSERT INTO rpl_tape_seq (%s) VALUES (%s)' % (','.join(allcols), ','.join(['%s'] * len(allcols)))
    order = [(e, s) for e in ('a', 'd') for s in ('h', 'l')]
    t1 = time.time(); CH = 20000
    for a in range(0, n, CH):
        b = min(a + CH, n)
        rows = []
        for i in range(a, b):
            vals = [int(ts[i]), u(ts[i])]
            for e, s in order:
                A = AGE[(e, s)]
                vals += [(None if A[i, k] < 0 else int(A[i, k])) for k in range(len(LADDER))]
            vals += [RK[(e, s)][i] for e, s in order]
            rows.append(tuple(vals))
        d.executemany(sql, rows, chunk=4000)
        if (b // CH) % 15 == 0:
            print('  banked %d / %d   %.0f s' % (b, n, time.time() - t1), flush=True)
    got = d.execute('SELECT COUNT(*) n FROM rpl_tape_seq', fetch=True)[0]['n']
    print('rpl_tape_seq rows %d   total %.0f s' % (got, time.time() - t0), flush=True)
    d.disconnect()


if __name__ == '__main__':
    main(sys.argv[1:])
