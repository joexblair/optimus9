"""
bl_review — a materialised report over bl_states + on-the-fly swings (px_smooth).

Per meaningful row (a state change OR an exit firing) it projects the BL data.
At each gate-open via a *completed* breach (state → 3, with a breach direction) it
adds the trade's risk/reward against the realised swing structure:

  gate opens (state→3)  →  the reversal trade is short (hi breach) / long (lo breach)
     └─ req2 (stop)   = abs % from gate-open px_smooth to the NEXT swing peak/trough
                        in the trade direction (the adverse excursion — how far price
                        ran the wrong way because the gate opened early)
     └─ req3 (profit) = abs % of the following leg (that peak→trough / trough→peak):
                        the move the trade is opening for

Swings = swing_detect ZigZag (0.9%) on px_smooth. NOTE: swings computed live (no
cache yet — task #18). Gate is single-line (hb9b) until s18b activates.
"""
import numpy as np

from logger import get_logger
from ..compute.swing_detect import find_pivots

_TABLE = 'bl_review'


def build_review(db, pct: float = 0.9) -> list:
    log = get_logger('BLReview')
    rows = db.execute(
        '''SELECT bls_pk, bar_time, line_name, px_smooth, k_line, bb_main, breach_dir,
                  predicted, state, exit1, exit2, exit3
           FROM bl_states WHERE px_smooth IS NOT NULL ORDER BY bar_time''', fetch=True)
    if not rows:
        log.warning('bl_states has no px_smooth rows — run bl_detect first')
        return []
    px     = np.array([float(r['px_smooth']) for r in rows])
    pivots = sorted(find_pivots(px, pct))                 # [(idx, 'H'|'L')] by idx

    def next_kind(i, kind):                               # next pivot of `kind` after i
        return next((idx for idx, k in pivots if idx > i and k == kind), None)

    def first_after(idx0):                                # next pivot of any kind after idx0
        return next((idx for idx, k in pivots if idx > idx0), None)

    # ── identify event rows (state change / exit) ────────────────────────────
    events = {}
    for j, r in enumerate(rows):
        prev    = int(rows[j - 1]['state']) if j > 0 else 0
        st      = int(r['state'])
        exits   = (1 if r['exit1'] else 0) | (2 if r['exit2'] else 0) | (4 if r['exit3'] else 0)
        changed = st != prev
        if changed or exits:
            events[j] = ('gate_open' if (changed and prev in (1, 2) and st in (0, 3))
                         else ('state' if changed else 'exit_raw'))

    # 'exit_raw' = a raw exit *condition* fired but did NOT complete the journey (e.g.
    # exit3 pseudo-cross while still bls1 — never curls). Collapse a consecutive run of
    # them to its first bar (one slow approach should be one row, not 15).
    drop, prev_kept = [], None
    for j in sorted(events):
        if events[j] == 'exit_raw' and prev_kept == 'exit_raw':
            drop.append(j)
        else:
            prev_kept = events[j]
    for j in drop:
        del events[j]

    # context: include the 11 rows preceding each STATE CHANGE (incl gate_open) — the run-up
    emit = set(events)
    for j, ev in events.items():
        if ev in ('state', 'gate_open'):
            emit.update(range(max(0, j - 11), j))

    out = []
    for j in sorted(emit):
        r     = rows[j]
        ev    = events.get(j, 'context')
        exits = (1 if r['exit1'] else 0) | (2 if r['exit2'] else 0) | (4 if r['exit3'] else 0)
        rec = {'bls_pk': r['bls_pk'], 'bar_time': r['bar_time'], 'bl_line': r['line_name'],
               'event': ev, 'state': int(r['state']), 'breach_dir': int(r['breach_dir']),
               'predicted': int(bool(r['predicted'])),
               'px_smooth': r['px_smooth'], 'k_line': r['k_line'], 'bb_main': r['bb_main'],
               'exit_bits': exits, 'stop_pct': None, 'stop_at': None,
               'profit_pct': None, 'profit_at': None}
        if ev == 'gate_open':
            # direction is the IN-BREACH dir (the gate-open row may be a state→0 reset
            # with breach_dir=0), so read it from the bar before the gate opened.
            bdir = int(rows[j - 1]['breach_dir']) if j > 0 else 0
            if bdir in (1, -1):
                kind = 'H' if bdir == 1 else 'L'              # hi→short→next peak; lo→long→next trough
                pk = next_kind(j, kind)
                if pk is not None:
                    rec['stop_pct'] = round(abs(px[pk] - px[j]) / px[j] * 100, 3)
                    rec['stop_at']  = rows[pk]['bar_time']
                    tk = first_after(pk)
                    if tk is not None:
                        rec['profit_pct'] = round(abs(px[tk] - px[pk]) / px[pk] * 100, 3)
                        rec['profit_at']  = rows[tk]['bar_time']
        out.append(rec)

    _persist(db, out)
    ngate = sum(1 for o in out if o['stop_pct'] is not None)
    log.info(f'{_TABLE}: {len(out)} rows ({ngate} gate-opens with stop/profit) → table {_TABLE}')
    return out


def _persist(db, rows):
    db.execute(f'DROP TABLE IF EXISTS {_TABLE}')
    db.execute(f'''CREATE TABLE {_TABLE} (
        blr_pk BIGINT AUTO_INCREMENT PRIMARY KEY, bls_pk BIGINT, bar_time DATETIME,
        bl_line VARCHAR(16), event VARCHAR(12), state TINYINT, breach_dir TINYINT,
        predicted TINYINT, px_smooth FLOAT, k_line FLOAT, bb_main FLOAT, exit_bits TINYINT,
        stop_pct FLOAT, stop_at DATETIME, profit_pct FLOAT, profit_at DATETIME)''')
    if not rows:
        return
    cols = ['bls_pk', 'bar_time', 'bl_line', 'event', 'state', 'breach_dir', 'predicted',
            'px_smooth', 'k_line', 'bb_main', 'exit_bits', 'stop_pct', 'stop_at',
            'profit_pct', 'profit_at']
    ph = ','.join(['%s'] * len(cols))
    db.executemany(f"INSERT INTO {_TABLE} ({','.join(cols)}) VALUES ({ph})",
                   [[r[c] for c in cols] for r in rows])
