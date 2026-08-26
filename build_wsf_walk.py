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

JOE 0825, the two calls that settled the slot accounting:

    "1:06:30 shouldn't print, because the 2nd wsf-exhaust event is already locked in and waiting
     for its x-cross trade signal --this means the pyramid mech needs to hold 2 slots for
     wsf-exhaust, as well as 2 slots for open positions <- this is only my guess at the logic -
     the build logic is your call"

    "all open trades (1 or 2) are closed by the next opposing dr trade"

ONE POOL OF TWO SLOTS, AND THAT IS MY CALL. Each slot is either ARMED - a wsf-exhaust locked in and
walking forward for its cross - or OPEN, once that cross has printed. A slot moves armed -> open; it
is never both and never a third thing.

  WHY NOT 2 ARMED PLUS 2 OPEN, which is Joe's guess. With one open position and two armed setups,
  both armed setups can convert, and that is three open trades against "max 2 trades". The second
  conversion would have to be blocked and thrown away, which is a worse outcome than never arming
  it. One pool cannot overfill.
  IT GIVES JOE THE BEHAVIOUR HE ASKED FOR. At 01:06:30 the pool holds one open trade from 01:02:35
  and one armed setup from 00:58:15, so nothing new arms - which is his point exactly.

CLOSING, Joe 0825: an opposing dr closes ALL open trades, one or two. MY ADDITION, STATED: it also
CLEARS ARMED SLOTS. An armed setup faces the direction that has just been contradicted, so walking
it forward would enter against the new dr. Not Joe's instruction.

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
HI, LO        = 85.0, 15.0   # the system boundary. A line at/past it is OUT of the fence
MID_FENCE_KNOB = 35     # KNOB, Joe 0825: "start with a fence based on 100-{knob:35} (ie 65:35
                        # fence)". RECORDED, NOT CONSUMED - Joe corrected the condition on 0825 to
                        # "it's not always mid-board, it just needs to be inside the fence". Kept
                        # here for the sweep Joe asked for.
WMT_TF_LO     = 2       # the weak-mage scan floor, Joe 0821
MAX_TRADES    = 2       # KNOB, Joe 0825: "allows pyramiding, max 2 trades"
GRID          = 5       # seconds per bar

DDL = '''CREATE TABLE IF NOT EXISTS wsf_walk (
    wwk_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    wwk_knobs VARCHAR(96) NOT NULL,
    wwk_seq INT NOT NULL,
    wwk_utc DATETIME NOT NULL,
    wwk_event VARCHAR(12) NOT NULL,  -- armed | signal | dormant | wake | flip | close | forced
    wwk_dr TINYINT,                  -- the dr in force at the event
    wwk_slots TINYINT,               -- slots occupied AFTER the event
    wwk_tf SMALLINT,                 -- the x line, on a signal row
    wwk_target VARCHAR(10),          -- which target x crossed, on a signal row
    wwk_source VARCHAR(12),          -- on a wake row: three-mage | wsf9of12
    wwk_note VARCHAR(160) NOT NULL DEFAULT '',
    -- the pyramid slots AFTER the event, so report_wsf_bar can print them at any bar
    wwk_slot1_utc DATETIME, wwk_slot1_state VARCHAR(6),
    wwk_slot2_utc DATETIME, wwk_slot2_state VARCHAR(6),
    UNIQUE KEY uq_wwk (wwk_knobs, wwk_utc, wwk_event))'''

COLS = ['wwk_knobs', 'wwk_seq', 'wwk_utc', 'wwk_event', 'wwk_dr', 'wwk_slots',
        'wwk_tf', 'wwk_target', 'wwk_source', 'wwk_note',
        'wwk_slot1_utc', 'wwk_slot1_state', 'wwk_slot2_utc', 'wwk_slot2_state']


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
    XR = {}
    for x in db.execute('SELECT wxc_utc t, wxc_tf tf, wxc_dr d, wxc_race_won w, wxc_x_r xr '
                        'FROM wsf_x_cross WHERE wxc_xwob=%s AND wxc_utc >= %s AND wxc_utc < %s',
                        (XCROSS_XWOB, WIN_FROM, WIN_TO), fetch=True):
        XC[(str(x['t']), int(x['tf']), int(x['d']))] = x['w']
        XR[(str(x['t']), int(x['tf']), int(x['d']))] = int(x['xr'] or 0)

    RV = defaultdict(dict)
    for x in db.execute('SELECT wflb_utc t, wflb_tf tf, wflb_dr d, wflb_r r FROM wsf_line_bar '
                        'WHERE wflb_knobs=%s AND wflb_utc >= %s AND wflb_utc < %s',
                        (KNOBS, WIN_FROM, WIN_TO), fetch=True):
        RV[str(x['t'])][(int(x['d']), int(x['tf']))] = float(x['r'])

    SIG = {}
    for x in db.execute("SELECT wsf_utc t, wsf_side s FROM ws_fin_9of12 WHERE wsf_ho_rule='median' "
                        "AND wsf_line_hcap='ws1b:1' AND wsf_utc >= %s AND wsf_utc < %s",
                        (WIN_FROM, WIN_TO), fetch=True):
        SIG[str(x['t'])] = int(x['s'])

    rows = []
    seq = 0
    pool = []          # ONE POOL OF MAX_TRADES SLOTS. Each is {'dr': +-1, 'state': armed | open}
    prev_won = {}      # (tf, dr) -> the previous bar's race winner, for the rising edge
    was_ready = False  # the previous bar was a wsf-exhaust with a dr, for the arming rising edge
    forced_armed = True  # the x-cross forced exhaust is ONE SHOT. Joe 0825: "does the exhaust
                         # re-fire if r continues - no ... the mechanisms will need to re-start when
                         # dr is captured (ie, keep walking until dr)". So it disarms on a fire and
                         # re-arms only on a LIVE three-Mage print, not on the latch.
    flip = None        # the opposing setup that will close the pool. Outside the pool by design.
    awake = None       # which source printed the opposing dr that ended dormancy
    dormant_from = None

    def side():
        return pool[0]['dr'] if pool else 0

    def slots_of(pl, when):
        """the two pyramid slots AFTER the event, for report_wsf_bar's footer line.
        A slot carries the bar it was TAKEN and whether it is armed or open."""
        out = []
        for k in range(MAX_TRADES):
            if k < len(pl):
                out += [pl[k].get('at', when), pl[k]['state']]
            else:
                out += [None, None]
        return tuple(out)

    def n_open():
        return sum(1 for s_ in pool if s_['state'] == 'open')

    for i, t in enumerate(T):
        dr = int(DR[i])
        board = V.get(t)
        if int(DRr[i]) != 0:            # a LIVE three-Mage print re-arms the forced exhaust
            forced_armed = True

        # RULE 2's WAKE. Joe 0825: "stay dormant until an opposing (three-mage or wsf9of12) dr
        # prints". The wake does NOT close anything - it only permits the walk to start watching
        # the opposing side.
        if pool and not awake:
            src = None
            if dr != 0 and dr == -side():
                src = 'three-mage'
            elif t in SIG and SIG[t] == -side():
                src = 'wsf9of12'
            if src:
                awake = src
                seq += 1
                rows.append((KNOBS, seq, t, 'wake', -side(), len(pool), None, None, src,
                             f'opposing dr {-side():+d} from {src}'
                             + (f' after {(i - dormant_from) * GRID} s dormant' if dormant_from else '')
                             + '. Watching for the opposing trade. Nothing closed.')
                            + slots_of(pool, t))

        # THE x-CROSS FORCED wsf-exhaust. Joe 0825, the ingredient:
        #   "because ws8r is mid-board, and ws7r's verdict is recently none (ie has just left the
        #    fence), AND ws7r was crossed, ws8r is confirming that it cannot carry its momentum
        #    past the fence ... the wsf-exhaust is declared at the time of the x-cross ... it will
        #    simultaeneously create a trade signal"
        # and the condition, Joe 0825: "it needs to have a higher momentum=true TF (eg ws8) INSIDE
        # the fence while the crossed (lower, eg 7) line is OUTSIDE the fence".
        #
        # THE WATCHED x IS THE CROSSED LINE'S OWN x, NOT THE CONFIRMER'S. Joe guessed the
        # confirmer's - "use the highest line holding the momo (ws8x)" - and his own 19 labelled
        # events say otherwise: the crossed line's own x lands nearer on 17 of the 19, exactly at
        # 10:57:00 on one of them. MEASURED, not chosen.
        #
        # THE CROSS IS wxc_x_r AT XCROSS_XWOB 5, already banked on all 276,496 rows. Not recomputed.
        # THE RACE, Joe 0825: "many lines past the fence when x crosses - create a race condition".
        # First to cross wins; on a tie at the same bar the lowest timeframe takes it.
        # ONE SHOT, Joe 0825: "does the exhaust re-fire if r continues - no. if that happens, the
        # trade will fail and the mechanisms will need to re-start when dr is captured".
        if dr != 0 and board and forced_armed:
            rv = RV.get(t, {})
            out = [tf for tf in range(1, 9) if board.get((dr, tf)) == 'none'
                   and (dr, tf) in rv
                   and (rv[(dr, tf)] >= HI if dr > 0 else rv[(dr, tf)] <= LO)]
            inside = [tf for tf in range(1, 9) if board.get((dr, tf)) in ('momo', 'curl')
                      and (dr, tf) in rv
                      and not (rv[(dr, tf)] >= HI if dr > 0 else rv[(dr, tf)] <= LO)]
            forced = next((p for p in sorted(out)
                           if any(h > p for h in inside) and XR.get((t, p, dr))), None)
            if forced is not None:
                op, ar = n_open(), len(pool) - n_open()
                pool = [{'dr': dr, 'state': 'open', 'at': t}]
                seq += 1
                rows.append((KNOBS, seq, t, 'forced', dr, 1, forced, 'r', None,
                             f'ws{forced}x crossed ws{forced}r while ws{forced}r is past the fence '
                             f'and ws{max(h for h in inside if h > forced)}r holds momo inside it'
                             + (f' - closes {op} open' if op else '')
                             + (f', clears {ar} armed' if ar else '')
                             + '. Slot 1 of the new pool.') + slots_of(pool, t))
                flip, awake, dormant_from, was_ready = None, None, None, True
                forced_armed = False
                for tf in range(1, 9):
                    for d in (1, -1):
                        prev_won[(tf, d)] = XC.get((t, tf, d))
                continue

        # THE OPPOSING TRADE. Joe 0825: "all open trades (1 or 2) are closed by the next opposing
        # dr trade" and "did the model verdict a short signal + x-cross at 01:34:05? that's the
        # only thing that should close trades". So the close needs the FULL chain on the opposing
        # side: an opposing wsf-exhaust with an opposing dr, walked forward to its own x-cross.
        # A bare dr print closes nothing.
        # THE FLIP SITS OUTSIDE THE TWO-SLOT POOL. My call: the pool is Joe's "max 2 trades" for
        # positions; the flip is the closing mechanism, and it becomes slot 1 of the new pool the
        # moment it fires.
        if flip and flip['state'] == 'armed':
            wm = WM.get((t, flip['dr']))
            if wm:
                won = XC.get((t, int(wm), flip['dr']))
                if won is not None and prev_won.get((int(wm), flip['dr'])) is None:
                    op, ar = n_open(), len(pool) - n_open()
                    newpool = [{'dr': flip['dr'], 'state': 'open', 'at': t}]
                    seq += 1
                    rows.append((KNOBS, seq, t, 'close', flip['dr'], 1, int(wm), won, awake,
                                 f'ws{wm}x crossed its {won} target on the opposing side - '
                                 f'closes {op} open'
                                 + (f' and clears {ar} armed' if ar else '')
                                 + f'. Becomes slot 1 of the new pool.') + slots_of(newpool, t))
                    pool = newpool
                    flip, awake, dormant_from, was_ready = None, None, None, True

        # a pending setup: has the weak-mage line's cross printed at THIS bar?
        for s_ in pool:
            if s_['state'] != 'armed':
                continue
            wm = WM.get((t, s_['dr']))
            if not wm:
                continue
            won = XC.get((t, int(wm), s_['dr']))
            if won is not None and prev_won.get((int(wm), s_['dr'])) is None:
                s_['state'] = 'open'
                seq += 1
                rows.append((KNOBS, seq, t, 'signal', s_['dr'], len(pool), int(wm), won, None,
                             f'ws{wm}x crossed its {won} target. '
                             f'{n_open()} open, {len(pool) - n_open()} armed.') + slots_of(pool, t))
                if n_open() >= MAX_TRADES:
                    dormant_from = i
                    seq += 1
                    rows.append((KNOBS, seq, t, 'dormant', s_['dr'], len(pool), None, None, None,
                                 'both slots occupied - no action until an opposing dr prints')
                                + slots_of(pool, t))
                break                                  # one conversion per bar

        # arm on the RISING EDGE of a wsf-exhaust bar that has a dr, when the pool has room and
        # the side agrees.
        # THE RISING EDGE IS THE POINT. A wsf-exhaust runs for many consecutive bars, so arming on
        # every bar of it filled BOTH slots from ONE event, 5 s apart - 00:53:15 and 00:53:20. Two
        # setups five seconds apart is one event, not a pyramid. Joe 0825 made the same point about
        # 01:06:30: "the 2nd wsf-exhaust event is already locked in and waiting for its x-cross".
        ready = (dr != 0 and board is not None
                 and not [tf for tf in range(1, 9) if board.get((dr, tf)) in ('momo', 'curl')])
        if ready and not was_ready:
            if pool and dr == -side() and awake and flip is None:
                flip = {'dr': dr, 'state': 'armed', 'at': t}   # the opposing setup that closes the pool
                seq += 1
                rows.append((KNOBS, seq, t, 'flip', dr, len(pool), None, None, awake,
                             'opposing wsf-exhaust - walking forward for the x-cross that closes '
                             'the open trades') + slots_of(pool, t))
            elif len(pool) < MAX_TRADES and (not pool or dr == side()):   # RULE 1: same-side only
                pool.append({'dr': dr, 'state': 'armed', 'at': t})
                seq += 1
                rows.append((KNOBS, seq, t, 'armed', dr, len(pool), None, None, None,
                             f'wsf-exhaust with a dr - walking forward for the x-cross. '
                             f'{n_open()} open, {len(pool) - n_open()} armed.') + slots_of(pool, t))
        was_ready = ready

        for tf in range(1, 9):
            for d in (1, -1):
                prev_won[(tf, d)] = XC.get((t, tf, d))

    db.execute(DDL)
    have = {c['Field'] for c in db.execute('SHOW COLUMNS FROM wsf_walk', fetch=True)}
    for col, spec in (('wwk_slot1_utc', 'DATETIME'), ('wwk_slot1_state', 'VARCHAR(6)'),
                      ('wwk_slot2_utc', 'DATETIME'), ('wwk_slot2_state', 'VARCHAR(6)')):
        if col not in have:
            db.execute(f'ALTER TABLE wsf_walk ADD COLUMN {col} {spec}')
            print(f'  added {col}', flush=True)
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
