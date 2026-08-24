"""build_dtf_state_flip — the domTF state-flip report. One row per flip, Joe's columns.

Joe 0823: "for each new timestamp that we uncover, update a report that uses these columns:
event_time  TF  dr  x-cross_forced_wsf-exhaust  state_flip  delegated_to_wsf  notes".

THE DELEGATION, Joe 0823, verbatim: "the replacement for handoff has become clear now: when dtf
flips to dtf-free, it needs to delegate to wsf (who will manage the trade creation)". So
`delegated_to_wsf` is yes on every flip TO dtf-free and blank on every flip to dtf-blocked.

THE ROWS ARE JOE'S READS, not a walk's output. He is building the label set the way he built the
37 wsf-exhaust timestamps. This file stores what he has settled; it derives nothing.

OPEN: what `x-cross_forced_wsf-exhaust` holds on a dtf row. In the wsf-exhaust CSV it meant the
exhaust had to be located by an x-cross rather than a fence exit. On a dtf state flip that meaning
does not carry, and Joe has not defined it. The column exists and is left empty.
"""
import sys
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

WIN_FROM = '2026-08-04 00:00:00'

DDL = '''CREATE TABLE IF NOT EXISTS dtf_state_flip (
    dsf_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    dsf_win_from  DATETIME NOT NULL,
    dsf_seq       INT NOT NULL,           -- chronological, 1-based
    dsf_event_time DATETIME NOT NULL,     -- the bar the flip happens
    dsf_tf        VARCHAR(8),             -- the timeframe that created the flip
    dsf_dr        VARCHAR(8),             -- the direction being read: upward | downward
    dsf_xcross_forced VARCHAR(8),         -- Joe's column. Meaning on a dtf row NOT YET DEFINED
    dsf_state_flip VARCHAR(12) NOT NULL,  -- dtf-blocked | dtf-free
    dsf_delegated VARCHAR(4),             -- yes on every flip TO dtf-free
    dsf_notes     VARCHAR(255) NOT NULL DEFAULT '',
    UNIQUE KEY uq_dsf (dsf_win_from, dsf_seq),
    KEY k_time (dsf_event_time))'''

COLS = ['dsf_win_from','dsf_seq','dsf_event_time','dsf_tf','dsf_dr','dsf_xcross_forced',
        'dsf_state_flip','dsf_delegated','dsf_notes']

# THE GUIDE-WIRE IS ws13x. Joe 0823: "go back to the previous model (dr set on ib x oob), and use
# ws13x in place of ws27x". Every dr below is read off ws13x under that rule: -1 while ws13x has
# been at or below 15 for 6 bars, +1 while at or above 85 for 6 bars, `none` while between them.
ROWS = [
 (1,'2026-08-04 00:39:05','ws13','-1',None,'dtf-blocked',None,
  "ws13r carrying the move. Joe read ~00:45. EXACT on the state series"),
 (2,'2026-08-04 01:21:05','ws13','none',None,'dtf-free','yes',
  "ws13x back between 15 and 85, held 6 bars. dr is none because ws13x IS the guide-wire - "
  "the flip and the loss of dr are the same event. Series changes 01:20:40, 25 s earlier"),
 (3,'2026-08-04 02:24:25','ws13','+1',None,'dtf-blocked',None,
  "carried by ws13r,ws14r,ws15r. Joe read ~02:22; this is MY match to that read, not his bar. "
  "EXACT on the state series"),
 (4,'2026-08-04 02:56:30','ws13','none',None,'dtf-free','yes',
  "ws13x back between 15 and 85 from above, held 6 bars. dr none, same reason as row 2. "
  "Series changes 02:56:05, 25 s earlier"),
]

def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(DDL)
    n = db.execute('SELECT COUNT(*) c FROM dtf_state_flip WHERE dsf_win_from=%s',
                   (WIN_FROM,), fetch=True)[0]['c']
    if n:
        print(f'  replacing {n} rows already stored for {WIN_FROM[:10]}', flush=True)
        db.execute('DELETE FROM dtf_state_flip WHERE dsf_win_from=%s', (WIN_FROM,))
    out = [(WIN_FROM, s, t, tf, dr, xf, st, dg, nt) for s, t, tf, dr, xf, st, dg, nt in ROWS
           if t is not None]
    db.executemany(f'INSERT INTO dtf_state_flip ({",".join(COLS)}) VALUES '
                   f'({",".join(["%s"]*len(COLS))})', out)
    print(f'  dtf_state_flip : {len(out)} rows written, '
          f'{sum(1 for r in ROWS if r[1] is None)} awaiting a timestamp', flush=True)
    print(f"\n  {'event_time':<12}{'TF':<7}{'dr':<11}{'x-cross_forced':<16}"
          f"{'state_flip':<13}{'delegated_to_wsf':<18}notes", flush=True)
    for s, t, tf, dr, xf, st, dg, nt in ROWS:
        print(f"  {(t[11:] if t else 'NOT SETTLED'):<12}{tf:<7}{dr:<11}{(xf or ''):<16}"
              f"{st:<13}{(dg or ''):<18}{nt}", flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
