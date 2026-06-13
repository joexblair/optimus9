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
from ..compute.swing_detect import find_pivots, nearest

_TABLE = 'bl_review'


def build_review(db, pct: float = 0.9) -> list:
    log = get_logger('BLReview')
    rows = db.execute(
        '''SELECT bls_pk, bar_time, line_name, px_smooth, breach_line,
                  exit_support AS bb_main, breach_dir,
                  predicted, state, exit1, exit2, exit3, raw_pk, combined_state,
                  swing_closest_dt, entry_dt, swing_adverse_dt
           FROM bl_states WHERE px_smooth IS NOT NULL ORDER BY line_name, bar_time''', fetch=True)
    if not rows:
        log.warning('bl_states has no px_smooth rows — run bl_detect first')
        return []

    # per-bar shared series (px / combined / raw_pk are identical across lines) + the
    # in-breach direction seen at each bar (the combined gate-open's trade side) + a
    # representative row per bar (for the gate rec's shared columns).
    bar_i, bars, px, comb, rawpk, bdir, rep, by_line = {}, [], [], [], [], [], {}, {}
    for r in rows:
        bt = r['bar_time']
        if bt not in bar_i:
            bar_i[bt] = len(bars); bars.append(bt); rep[bt] = r
            px.append(float(r['px_smooth'])); comb.append(int(r['combined_state']))
            rawpk.append(int(r['raw_pk'] or 0)); bdir.append(0)
        if int(r['state']) in (1, 2) and int(r['breach_dir']) in (1, -1):
            bdir[bar_i[bt]] = int(r['breach_dir'])
        by_line.setdefault(r['line_name'], []).append(r)
    px     = np.array(px)
    pivots = sorted(find_pivots(px, pct))

    def next_kind(i, kind): return next((x for x, k in pivots if x > i and k == kind), None)
    def first_after(i0):    return next((x for x, k in pivots if x > i0), None)

    def rec(line, bt, ev, st, bd, raw, src):
        e = (1 if src['exit1'] else 0) | (2 if src['exit2'] else 0) | (4 if src['exit3'] else 0)
        return {'bls_pk': src['bls_pk'], 'bar_time': bt, 'bl_line': line, 'event': ev,
                'state': st, 'c_bls': int(src['combined_state']), 'breach_dir': bd, 'predicted': int(bool(src['predicted'])),
                'raw_pk': raw, 'px_smooth': src['px_smooth'], 'breach_line': src['breach_line'],
                'bb_main': src['bb_main'], 'exit_bits': e, 'stop_px': None, 'stop_at': None,
                'profit_px': None, 'profit_at': None,                 # swing UTCs inherited from bl_states (close-based)
                'swing_closest_dt': src['swing_closest_dt'], 'entry_dt': src['entry_dt'],
                'swing_adverse_dt': src['swing_adverse_dt']}

    # ── gate-opens (req2/3): the gate is OPEN when combined∈{0,3} (all lines idle/done);
    # a gate-open is the transition INTO that. The corrected combined fold (min of non-zero
    # states, 0 iff all idle) makes this exact — a still-breaching line forces combined to
    # 1/2, so {0,3} can't be masked by a plain min. Single-sources off combined_state. ──
    done = [comb[i] in (0, 3) for i in range(len(bars))]
    out  = []
    gate = {i: 'gate_open' for i in range(len(bars))
            if done[i] and not (done[i - 1] if i > 0 else True)}
    g_emit = set(gate)
    for i in gate:
        g_emit.update(range(max(0, i - 11), i))           # 11-bar run-up into the gate
    for i in sorted(g_emit):
        ev = gate.get(i, 'context')
        d  = bdir[i - 1] if i > 0 else 0                   # trade side = the in-breach dir before the open
        r  = rec('gate', bars[i], ev, comb[i], d, rawpk[i], rep[bars[i]])
        if ev == 'gate_open' and d in (1, -1):
            pk = next_kind(i, 'H' if d == 1 else 'L')       # hi→short→next peak; lo→long→next trough
            if pk is not None:
                r['stop_px'] = round(abs(px[pk] - px[i]) / px[i] * 100, 3); r['stop_at'] = bars[pk]
                tk = first_after(pk)
                if tk is not None:
                    r['profit_px'] = round(abs(px[tk] - px[pk]) / px[pk] * 100, 3); r['profit_at'] = bars[tk]
        out.append(r)

    # ── per-line state changes / exits (req1) + the 11-bar run-up per change ──
    for line, lrows in by_line.items():
        ev = {}
        for k, r in enumerate(lrows):
            prev = int(lrows[k - 1]['state']) if k > 0 else 0
            st   = int(r['state'])
            if st != prev or r['exit1'] or r['exit2'] or r['exit3']:
                ev[k] = 'state' if st != prev else 'exit_raw'
        drop, kept = [], None                              # collapse consecutive exit_raw runs
        for k in sorted(ev):
            if ev[k] == 'exit_raw' and kept == 'exit_raw': drop.append(k)
            else: kept = ev[k]
        for k in drop: del ev[k]
        em = set(ev)
        for k, e in ev.items():
            if e == 'state': em.update(range(max(0, k - 11), k))
        for k in sorted(em):
            r = lrows[k]
            out.append(rec(line, r['bar_time'], ev.get(k, 'context'), int(r['state']),
                           int(r['breach_dir']), int(r['raw_pk'] or 0), r))

    out.sort(key=lambda o: (o['bar_time'], o['bl_line']))
    _persist(db, out)
    ng = sum(1 for o in out if o['stop_px'] is not None)
    log.info(f'{_TABLE}: {len(out)} rows ({ng} combined gate-opens w/ stop/profit, '
             f'{len(by_line)} lines) → table {_TABLE}')
    return out


def _persist(db, rows):
    db.execute(f'DROP TABLE IF EXISTS {_TABLE}')
    db.execute(f'''CREATE TABLE {_TABLE} (
        blr_pk BIGINT AUTO_INCREMENT PRIMARY KEY, bls_pk BIGINT, bar_time DATETIME,
        bl_line VARCHAR(16), event VARCHAR(12), state TINYINT, c_bls TINYINT, breach_dir TINYINT,
        predicted TINYINT, raw_pk TINYINT, px_smooth FLOAT, breach_line FLOAT, bb_main FLOAT,
        exit_bits TINYINT, stop_px FLOAT, stop_at DATETIME, profit_px FLOAT, profit_at DATETIME,
        swing_closest_dt DATETIME, entry_dt DATETIME, swing_adverse_dt DATETIME)''')
    if not rows:
        return
    cols = ['bls_pk', 'bar_time', 'bl_line', 'event', 'state', 'c_bls', 'breach_dir', 'predicted',
            'raw_pk', 'px_smooth', 'breach_line', 'bb_main', 'exit_bits', 'stop_px', 'stop_at',
            'profit_px', 'profit_at', 'swing_closest_dt', 'entry_dt', 'swing_adverse_dt']
    ph = ','.join(['%s'] * len(cols))
    db.executemany(f"INSERT INTO {_TABLE} ({','.join(cols)}) VALUES ({ph})",
                   [[r[c] for c in cols] for r in rows])
