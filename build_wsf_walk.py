"""build_wsf_walk - the causal forward walk over 08-04, with Joe's two 0825 trade-slot rules.

JOE 0825, verbatim, the two rules this adds:

    1. "allows pyramiding, max 2 trades"
    2. "if both trade slots are occupied, the walk will take no action/stay dormant until an
        opposing (three-mage or wsf9of12) dr prints. keep it causal"

CAUSAL BY CONSTRUCTION. The walk visits bars in order and every test reads that bar or earlier:
  - the dr is jig.wsf_facing_dr on gcws30Mage/ws1Mage/ws2Mage against the 80/20 fence, then
    jig.wsf_dr_lookback over DR_LOOKBACK_S - a BACKWARD lookback only.
  - the state is the wsf-model-report footer read from wsf_line_bar at that bar.
  - the entry is not the setup bar. Joe, spec 1.6: "the next action after `wsf-exhaust`: walk
    forward. if ws{weak-mage}x-cross has printed, then create a trade signal". So the walk ARMS on
    a wsf-exhaust bar that has a dr, and OPENS a slot on the later bar where that cross prints.
    The weak-mage timeframe is re-read at each bar of the walk.
  - the cross is the RISING EDGE of a race held XCROSS_XWOB bars. wsf_x_cross latches `fired`.

WHAT JOE HAS NOT SAID, and what this does about it - see docs/wsf_setup_model.md 3.22.4:
  - nothing closes a slot. IMPLEMENTED AS: the opposing dr that ends dormancy frees both slots,
    because otherwise the walk is dormant forever after the second trade and Rule 2's "until"
    means nothing. THIS IS MY READING OF JOE'S SENTENCE, NOT HIS INSTRUCTION.
  - nothing disarms a pending setup. As built it stays armed until the cross prints.
  - an opposing dr with only ONE slot filled does nothing. Rule 2 names both slots occupied.

    python3 build_wsf_walk.py
"""
import sys
from collections import defaultdict

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.jig import wsf_facing_dr, wsf_dr_lookback

WIN_FROM, WIN_TO = '2026-08-04 00:00:00', '2026-08-05 00:00:00'
KNOBS = 'kw4_fs21_sn6_hi85_lo15_r20.5_sl1_arc4_sk13.9_cr0.4_mkstate_mf17_xw4'
MAGE_KNOB     = 20      # Joe 0823: the dr fence is 80 / 20
DR_LOOKBACK_S = 180     # Joe 0823: "restrict the lookback to 3 minutes"
XCROSS_XWOB   = 5       # the x-cross hold
WMT_TF_LO     = 2       # the weak-mage scan floor, Joe 0821
MAX_TRADES    = 2       # KNOB, Joe 0825: "allows pyramiding, max 2 trades"
GRID          = 5       # seconds per bar

DDL = '''CREATE TABLE IF NOT EXISTS wsf_walk (
    wwk_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    wwk_knobs VARCHAR(96) NOT NULL,
    wwk_seq INT NOT NULL,
    wwk_utc DATETIME NOT NULL,
    wwk_event VARCHAR(12) NOT NULL,  -- armed | signal | dormant | wake
    wwk_dr TINYINT,                  -- the dr in force at the event
    wwk_slots TINYINT,               -- slots occupied AFTER the event
    wwk_tf SMALLINT,                 -- the x line, on a signal row
    wwk_target VARCHAR(10),          -- which target x crossed, on a signal row
    wwk_source VARCHAR(12),          -- on a wake row: three-mage | wsf9of12
    wwk_note VARCHAR(160) NOT NULL DEFAULT '',
    UNIQUE KEY uq_wwk (wwk_knobs, wwk_utc, wwk_event))'''

COLS = ['wwk_knobs', 'wwk_seq', 'wwk_utc', 'wwk_event', 'wwk_dr', 'wwk_slots',
        'wwk_tf', 'wwk_target', 'wwk_source', 'wwk_note']


def main():
    db = DatabaseManager(**get_db_config()); db.connect()

    face = db.execute('SELECT wlb_utc t, wlb_g30Mage a, wlb_ws1Mage b, wlb_ws2Mage c '
                      'FROM ws_line_bar WHERE wlb_utc >= %s AND wlb_utc < %s ORDER BY wlb_utc',
                      (WIN_FROM, WIN_TO), fetch=True)
    T = [str(x['t']) for x in face]
    DRr = wsf_facing_dr([[float(x['a']) for x in face], [float(x['b']) for x in face],
                         [float(x['c']) for x in face]], 100.0 - MAGE_KNOB, float(MAGE_KNOB))
    DR, _LG = wsf_dr_lookback(DRr, DR_LOOKBACK_S // GRID)

    V = defaultdict(dict)
    for x in db.execute('SELECT wflb_utc t, wflb_tf tf, wflb_dr d, wflb_verdict v FROM wsf_line_bar '
                        'WHERE wflb_knobs=%s AND wflb_utc >= %s AND wflb_utc < %s',
                        (KNOBS, WIN_FROM, WIN_TO), fetch=True):
        V[str(x['t'])][(int(x['d']), int(x['tf']))] = x['v']

    WM = {}
    for x in db.execute('SELECT wbt_utc t, wbt_dr d, wbt_weak_mage_tf w FROM wsf_bar_tf '
                        'WHERE wbt_tf=1 AND wbt_wmt_tf_lo=%s AND wbt_utc >= %s AND wbt_utc < %s',
                        (WMT_TF_LO, WIN_FROM, WIN_TO), fetch=True):
        WM[(str(x['t']), int(x['d']))] = x['w']

    XC = {}
    for x in db.execute('SELECT wxc_utc t, wxc_tf tf, wxc_dr d, wxc_race_won w FROM wsf_x_cross '
                        'WHERE wxc_xwob=%s AND wxc_utc >= %s AND wxc_utc < %s',
                        (XCROSS_XWOB, WIN_FROM, WIN_TO), fetch=True):
        XC[(str(x['t']), int(x['tf']), int(x['d']))] = x['w']

    SIG = {}
    for x in db.execute("SELECT wsf_utc t, wsf_side s FROM ws_fin_9of12 WHERE wsf_ho_rule='median' "
                        "AND wsf_line_hcap='ws1b:1' AND wsf_utc >= %s AND wsf_utc < %s",
                        (WIN_FROM, WIN_TO), fetch=True):
        SIG[str(x['t'])] = int(x['s'])

    rows = []
    seq = 0
    slots = 0          # occupied trade slots
    open_dr = 0        # the dr the open trades face
    armed_dr = 0       # 0 = not armed
    prev_won = {}      # (tf, dr) -> the previous bar's race winner, for the rising edge
    dormant_from = None

    for i, t in enumerate(T):
        dr = int(DR[i])
        board = V.get(t)

        # RULE 2. Both slots occupied: no action until an OPPOSING dr prints, from either source.
        if slots >= MAX_TRADES:
            src = None
            if dr != 0 and dr == -open_dr:
                src = 'three-mage'
            elif t in SIG and SIG[t] == -open_dr:
                src = 'wsf9of12'
            if src:
                seq += 1
                rows.append((KNOBS, seq, t, 'wake', -open_dr, 0, None, None, src,
                             f'opposing dr {-open_dr:+d} from {src} after '
                             f'{(i - dormant_from) * GRID} s dormant. Both slots freed.'))
                slots, open_dr, armed_dr, dormant_from = 0, 0, 0, None
            # nothing else happens while dormant, including arming
            for k in list(prev_won):
                prev_won[k] = XC.get((t, k[0], k[1]))
            continue

        # a pending setup: has the weak-mage line's cross printed at THIS bar?
        if armed_dr:
            wm = WM.get((t, armed_dr))
            if wm:
                won = XC.get((t, int(wm), armed_dr))
                was = prev_won.get((int(wm), armed_dr))
                if won is not None and was is None:
                    slots += 1
                    open_dr = armed_dr
                    seq += 1
                    rows.append((KNOBS, seq, t, 'signal', armed_dr, slots, int(wm), won, None,
                                 f'ws{wm}x crossed its {won} target. Slot {slots} of {MAX_TRADES}.'))
                    armed_dr = 0
                    if slots >= MAX_TRADES:
                        dormant_from = i
                        seq += 1
                        rows.append((KNOBS, seq, t, 'dormant', open_dr, slots, None, None, None,
                                     'both slots occupied - no action until an opposing dr prints'))

        # arm on a wsf-exhaust bar that has a dr, when a slot is free and the side agrees
        if not armed_dr and slots < MAX_TRADES and dr != 0 and board:
            if slots == 0 or dr == open_dr:          # RULE 1: pyramiding is same-side only
                if not [tf for tf in range(1, 9) if board.get((dr, tf)) in ('momo', 'curl')]:
                    armed_dr = dr
                    seq += 1
                    rows.append((KNOBS, seq, t, 'armed', dr, slots, None, None, None,
                                 'wsf-exhaust with a dr - walking forward for the x-cross'))

        for k in list(prev_won):
            prev_won[k] = XC.get((t, k[0], k[1]))
        for tf in range(1, 9):
            for d in (1, -1):
                prev_won[(tf, d)] = XC.get((t, tf, d))

    db.execute(DDL)
    n = db.execute('SELECT COUNT(*) c FROM wsf_walk WHERE wwk_knobs=%s', (KNOBS,), fetch=True)[0]['c']
    if n:
        print(f'  replacing {n} rows at these knobs', flush=True)
        db.execute('DELETE FROM wsf_walk WHERE wwk_knobs=%s', (KNOBS,))
    db.executemany(f'INSERT INTO wsf_walk ({",".join(COLS)}) VALUES '
                   f'({",".join(["%s"] * len(COLS))})', rows)

    ev = defaultdict(int)
    for r in rows:
        ev[r[3]] += 1
    print(f'\n  wsf_walk : {len(rows)} events over {len(T):,} bars   MAX_TRADES {MAX_TRADES}\n'
          f'    armed {ev["armed"]}   signal {ev["signal"]}   dormant {ev["dormant"]}'
          f'   wake {ev["wake"]}\n', flush=True)
    print(f"  {'#':<5}{'utc':<11}{'event':<9}{'dr':>4}{'slots':>7}   note", flush=True)
    for r in rows:
        print(f"  {r[1]:<5}{r[2][11:]:<11}{r[3]:<9}{(f'{r[4]:+d}' if r[4] else '  0'):>4}"
              f"{r[5]:>7}   {r[9]}", flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
