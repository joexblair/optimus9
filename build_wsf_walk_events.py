"""build_wsf_walk_events — the walk's events, the ingredients it read, and the signals it produced.

Joe 0827: "build the 3 SRP tables", after asking "would we be smarter if we maintain a collection of
SRP db tables that tracks the usage of the ingredients, per wsf-exhaust timestamp?"

THE RECIPE IS docs/wsf_walk.md SECTION 2. This script is the engine for it. Every rule it applies
is quoted there with Joe's own words; nothing new is invented here.

THREE TABLES, THREE CONCERNS, JOINED BY FOREIGN KEYS. Joe 0827: "the tables should be relational,
joined by FKs".
    wsf_exhaust_event      one row per declared wsf-exhaust. THE PARENT
    wsf_event_ingredient   one row per (event, ingredient) - the usage Joe asked for. It joins
                           BOTH ways: to wsf_exhaust_event for the bar, and to wsf_ingredient for
                           what the ingredient is
    wsf_event_signal       one row per trade signal, or per event that never produced one

NOTHING IS EVER DELETED. Joe 0827: "no deletes - here's the reason why: if we add a new ingredient
to support a decision that overrides an existing verdict, there is always a possibility that the new
ingredient is malformed. if we have a history of its usage, we can 1) easily compare the facts needed
to repair (or enhance) that ingredient and 2) be sure that we have not broken an earlier confirmed
wsf-exhaust event". Every run APPENDS under a new `wee_run` number. Re-running this script never
removes a row.

THE CHILDREN CARRY ONLY THE FOREIGN KEY. wee_utc, wee_dr and wee_knobs live on the parent and are
not repeated - that is what relational means. ON DELETE CASCADE, so replacing a run at one knob set
clears its children with it.
THE KNOBS RULE IS SATISFIED THROUGH THE PARENT. Joe's standing rule is that every knob that changes
rows sits in the unique key. wee_knobs is in the parent's key, and each child row belongs to exactly
one parent, so a run at another ceiling lands alongside rather than on top.

WHY THREE AND NOT ONE. The event exists without a signal - that is Joe's dual latch, 0819: "trade
signal cannot fire unless wsf-exhaust has fired". And an event carries ~40 ingredient rows, so
folding them in would repeat every event field 40 times.

WHY ONE SCRIPT AND NOT THREE. The three tables are three projections of ONE walk pass. Three
scripts would run the walk three times and could diverge. MINE, STATED.

RELATIONSHIP TO build_wsf_walk.py. That script is the maxTF-8 walk with Joe's trade-slot rules; its
rows stay untouched. This one implements the document's recipe at maxTF 12. THE TWO NOW HOLD THE
SAME WALK LOGIC IN TWO PLACES - Joe 0823 said "import, don't duplicate/split/fork". Consolidating
them is a change to Joe's existing artefact and I have not made it. FLAGGED, NOT RESOLVED.

    python3 build_wsf_walk_events.py
"""
import sys
import datetime as dt
from collections import defaultdict

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.jig import wsf_facing_dr, wsf_dr_lookback
from optimus9.compute.momo_gated import curl_gates
from optimus9.compute import momo_core as MC

WIN_FROM, WIN_TO = '2026-08-04 00:00:00', '2026-08-05 00:00:00'
KNOBS = 'kw4_fs21_sn6_hi85_lo15_r20.5_sl1_arc4_sk13.9_cr0.4_mkstate_mf17_xw4'
MAX_TF        = 12    # KNOB. Joe 0826: "wsf is limited to TF12"
MAGE_KNOB     = 20    # the three-Mage dr fence is 80 / 20. Joe 0823
DR_LOOKBACK_S = 180   # KNOB, Joe 0823: "restrict the lookback to 3 minutes". 36 bars at the 5 s grid
XCROSS_XWOB   = 5     # KNOB. 5 bars = 20 s the x must hold on the far side
BANK_FROM     = '01:03:00'  # RUN SCOPE, not a model knob. '' = bank from the first bar. A 'HH:MM:SS'
                      # holds banking until that bar. Joe 0828: "walk forward from 00:16".
                      # THE WALK ALWAYS STARTS AT WIN_FROM. This is a BANKING FLOOR, not a walk
                      # start - the trade pool depends on everything before it, so starting the
                      # walk late would report the wrong slots. MINE, STATED.
TRACE_ONLY    = 0     # RUN SCOPE. 1 = print every event and its pool move, bank NOTHING. Added
                      # 0828 because the console showed only the BANKED event, so the pool moves
                      # behind a banking floor were invisible and I described them from inference
                      # instead of from a reading.
STOP_AFTER    = 1     # RUN SCOPE, not a model knob. 0 = walk the whole window. N = bank the first
                      # N events and stop. Joe 0827: "for the walk: stop on the first wsf-exhaust".
                      # It changes WHAT IS BANKED but not what the rules do, so it lives on the run
                      # columns (wee_stop_after) and NOT in the knob signature. MINE, STATED.
WMT_TF_LO     = 2     # KNOB, Joe 0821. the weak-mage scan's floor
WMT_TF_HI     = 12    # KNOB, Joe 0826: "weak-mage-tf scan is now TF2 to TF12"
MAX_TRADES    = 2     # KNOB, Joe 0825: "allows pyramiding, max 2 trades"
HI, LO        = 85.0, 15.0   # the system boundary
GRID          = 5     # seconds per bar

# EVERY KNOB THAT CHANGES ROWS IS IN THE SIGNATURE, AND THE SIGNATURE IS IN ALL THREE UNIQUE KEYS.
# Joe's standing rule. A run at another ceiling or another hold lands alongside, not on top.
SIG = (f'{KNOBS}_mt{MAX_TF}_mg{MAGE_KNOB}_dl{DR_LOOKBACK_S}_xw{XCROSS_XWOB}'
       f'_wl{WMT_TF_LO}_wh{WMT_TF_HI}_tr{MAX_TRADES}')

DDL_EVENT = '''CREATE TABLE IF NOT EXISTS wsf_exhaust_event (
    wee_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    wee_knobs      VARCHAR(160) NOT NULL,  -- the full knob signature. In the unique key
    wee_run        INT      NOT NULL,      -- the run number at this knob signature. In the unique
    --   key. Joe 0827: "no deletes" - each run appends beside the last so the usage history stands
    wee_dt_created DATETIME NOT NULL,      -- wall-clock UTC the row was created. Joe 0828: "if
    --   they are the UTC times when the run was completed, then the column should be named
    --   `dt_created`". Stamped at INSERT, so it is a creation time and not a start time
    wee_stop_after INT      NOT NULL DEFAULT 0,  -- the run's scope. 0 = the whole window was
    --   walked. N = the run stopped after N events, so absence of a later event proves nothing
    wee_bank_from  VARCHAR(8) NOT NULL DEFAULT '',  -- the run's banking floor. '' = from the first
    --   bar. 'HH:MM:SS' = events before that bar were walked but not banked
    wee_seq        INT      NOT NULL,      -- order within the run
    wee_utc        DATETIME NOT NULL,      -- the bar the wsf-exhaust is declared
    wee_dr         TINYINT  NOT NULL,      -- the latched three-Mage dr in force. +1 or -1
    wee_test       VARCHAR(24) NOT NULL,   -- which recipe test fired: maxtf | plain | forced
    wee_max_tf     SMALLINT NOT NULL,      -- the ladder ceiling in force
    wee_trigger_tf SMALLINT,               -- the line that declared it, where the test names one
    wee_holding    VARCHAR(96),            -- lines still reading momo or curl at the bar
    wee_past_fence VARCHAR(96),            -- lines past the 85/15 boundary reading none
    wee_note       VARCHAR(255) NOT NULL DEFAULT '',
    -- THE TRADE SLOTS. Joe 0825: "allows pyramiding, max 2 trades" and "if both trade slots are
    -- occupied, the walk will take no action/stay dormant until an opposing (three-mage or
    -- wsf9of12) dr prints".
    -- ARMED IS NOT STORED. Joe 0828: "I want to change the pyramid slots, because I don't need to
    -- know about `armed`. what I'm looking for, at a glance, is: how many trades are open, and
    -- when did they open". So a slot holds the bar the TRADE OPENED - the x-cross - and the line
    -- whose cross opened it. NULL = the slot is free. The pool still arms internally, unbanked.
    -- THE LINE IS PER TRADE, not per event. Joe 0828: "I also need the trade creation data baked
    -- into the 'FOOTNOTES' section: timestamp and which TF created the x-cross". Two trades in the
    -- pool come from two different exhausts and can be watching two different lines.
    wee_trade1_utc DATETIME, wee_trade1_tf SMALLINT,
    wee_trade2_utc DATETIME, wee_trade2_tf SMALLINT,
    -- JOE'S CONFIRMATION, 0828: "bank your 00:02:30 wsf-exhaust as confirmed. x-cross is also
    -- confirmed". His column, not mine - this script never writes a 1.
    wee_confirmed     TINYINT NOT NULL DEFAULT 0,
    wee_confirmed_utc DATETIME,
    -- THE X-CROSS ON THE SAME ROW, Joe 0828: "it's a 1:1 map, so the x-cross data (timestamp,
    -- ws{TF}) can live on the same row as the validated wsf-exhaust". Written by the walk from
    -- the same forward scan that fills wsf_event_signal.
    wee_xc_utc     DATETIME, wee_xc_tf SMALLINT,
    wee_xc_confirmed TINYINT NOT NULL DEFAULT 0,
    UNIQUE KEY uq_wee (wee_knobs, wee_run, wee_utc, wee_dr),
    KEY k_wee_bar (wee_utc)) ENGINE=InnoDB'''

DDL_INGR = '''CREATE TABLE IF NOT EXISTS wsf_event_ingredient (
    wei_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    wei_event_pk      BIGINT NOT NULL,   -- FK -> wsf_exhaust_event.wee_pk
    wei_ingredient_pk BIGINT NOT NULL,   -- FK -> wsf_ingredient.wig_pk
    wei_used      TINYINT  NOT NULL,       -- 1 = the recipe READ it to reach THIS verdict
    wei_value     VARCHAR(255),            -- the reading as the recipe saw it at THIS bar
    UNIQUE KEY uq_wei (wei_event_pk, wei_ingredient_pk),
    KEY k_wei_used (wei_used),
    CONSTRAINT fk_wei_event FOREIGN KEY (wei_event_pk)
        REFERENCES wsf_exhaust_event (wee_pk) ON DELETE CASCADE,
    CONSTRAINT fk_wei_ingredient FOREIGN KEY (wei_ingredient_pk)
        REFERENCES wsf_ingredient (wig_pk)) ENGINE=InnoDB'''
# THE NAME, NUMBER AND SOURCE ARE GONE FROM THIS ROW. They belong to wsf_ingredient and are reached
# through wei_ingredient_pk. Joe 0827: "the other tables will simply join to the ingredient's PKs.
# we are SRP all the way". What stays here is what varies BY EVENT: was it read, and what did it say.
# NO for/against COLUMN, AND THAT IS DELIBERATE. Joe's 0825 list carried "contributed for / against /
# nothing" and that judgement is exactly what drifted - it is narration, and narration is what this
# table exists to replace. `wei_used` comes from which recipe step ran; `wei_value` is a measurement.
# MINE, STATED.

DDL_SIG = '''CREATE TABLE IF NOT EXISTS wsf_event_signal (
    wes_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    wes_event_pk  BIGINT   NOT NULL,       -- FK -> wsf_exhaust_event.wee_pk
    wes_utc       DATETIME,                -- the bar the cross confirmed. NULL = never fired
    wes_lag_s     INT,                     -- seconds from the exhaust to the signal
    wes_watch_tf  SMALLINT,                -- the line whose x was watched
    wes_route     VARCHAR(12) NOT NULL,    -- weak-mage | rule-c
    wes_target    VARCHAR(10),             -- which race target won: Mage | b | boundary
    wes_note      VARCHAR(255) NOT NULL DEFAULT '',
    UNIQUE KEY uq_wes (wes_event_pk),
    CONSTRAINT fk_wes_event FOREIGN KEY (wes_event_pk)
        REFERENCES wsf_exhaust_event (wee_pk) ON DELETE CASCADE) ENGINE=InnoDB'''

E_COLS = ['wee_knobs','wee_run','wee_dt_created','wee_stop_after','wee_bank_from','wee_seq',
          'wee_utc','wee_dr','wee_test','wee_max_tf','wee_trigger_tf','wee_holding',
          'wee_past_fence','wee_note',
          'wee_trade1_utc','wee_trade1_tf','wee_trade2_utc','wee_trade2_tf',
          'wee_xc_utc','wee_xc_tf']
I_COLS = ['wei_event_pk','wei_ingredient_pk','wei_used','wei_value']
S_COLS = ['wes_event_pk','wes_utc','wes_lag_s','wes_watch_tf','wes_route','wes_target','wes_note']

# THE CATALOGUE IS NOT IN THIS FILE. It lives in wsf_ingredient, built by build_wsf_ingredient.py.
# Joe 0827: "you should have every ingredient listed in single table. that table holds the dataset
# that you refer to for each decision - when you have a confirmed ingredient list, you won't miss
# any of them". This script reads it, so an ingredient added there appears here without a code edit.


def _lines(tfs):
    return ','.join(f'ws{t}' for t in tfs) if tfs else None


def _col(bar, dr, key):
    """[(tf, value)] for one column across ws1..ws{MAX_TF} at this bar and dr, NULLs dropped."""
    return [(tf, bar[(dr, tf)][key]) for tf in range(1, MAX_TF + 1)
            if (dr, tf) in bar and bar[(dr, tf)][key] is not None]


def _per_line(pairs, fmt='{:.2f}'):
    """ws1 12.34  ws2 56.78 ... one reading per line, in ladder order."""
    return '  '.join(f'ws{tf} ' + fmt.format(v) for tf, v in pairs) or None


def _flag(pairs):
    """the lines whose flag is set, as a ws-list."""
    return _lines([tf for tf, v in pairs if v]) or 'none'


def _depth(bar, dr):
    """Joe 0825: `sat left` says how long before r must move."""
    v = _col(bar, dr, 'sl')
    if not v:
        return None
    at_zero = [tf for tf, x in v if int(x) == 0]
    return (f'sat left min {min(int(x) for _, x in v)} max {max(int(x) for _, x in v)} bars; '
            f'must move now: {_lines(at_zero) or "none"}')


def _level_gate(row, dr):
    """the level the line had to reach at this bar. Recomputed from the banked fit and slope,
    the same expression report_wsf_bar prints - not a second implementation of the gate."""
    if row['fi'] is None or row['sp'] is None:
        return None
    trk = max(0.0, min(1.0, float(row['fi'])
                       * min(1.0, abs(float(row['sp'])) / MC.MOMO_SLOPE_MIN)))
    return (50 - MC.LEVEL_SLACK * trk) if dr > 0 else (50 + MC.LEVEL_SLACK * trk)


def _curl_mode(row):
    """wsf-curl-mode, Joe 0824: the curl reading with gate 2 excluded. curl_gates is momo_gated's
    own, fed the five banked measurements - not re-implemented here."""
    if row['g'] != 'curl':
        return ''
    if row['v'] != 'curl':
        return 'none'          # the momentum-kill already turned it off, before any gate
    return 'curl' if curl_gates(
        {'aligned': bool(row['al']), 'quad': row['ba'] is not None,
         'quad_aligned': None if row['ba'] is None else bool(row['ba']),
         'quad_r2': row['bf'], 'quad_why': None}, gate2=False)[0] else 'none'


def _heading(row):
    """report_wsf_bar's rule: past momo-fence-r is away, else the slope's sign against dr."""
    if row['m']:
        return 'away'
    sp = float(row['sp'] or 0.0)
    return 'toward' if sp > 0 else 'away' if sp < 0 else 'flat'


def main():
    db = DatabaseManager(**get_db_config()); db.connect()

    face = db.execute('SELECT wlb_utc t, wlb_g30Mage a, wlb_ws1Mage b, wlb_ws2Mage c '
                      'FROM ws_line_bar WHERE wlb_utc >= %s AND wlb_utc < %s ORDER BY wlb_utc',
                      (WIN_FROM, WIN_TO), fetch=True)
    T = [str(x['t']) for x in face]
    IDX = {t: i for i, t in enumerate(T)}
    DRr = wsf_facing_dr([[float(x['a']) for x in face], [float(x['b']) for x in face],
                         [float(x['c']) for x in face]], 100.0 - MAGE_KNOB, float(MAGE_KNOB))
    DR, LAG = wsf_dr_lookback(DRr, DR_LOOKBACK_S // GRID)
    print(f'  {len(T):,} bars   knobs {SIG}', flush=True)

    # EVERY COLUMN THE 22 READERS NEED, in one pass. LB[bar][(dr, tf)] is the whole line row.
    V, U, R, MFR = defaultdict(dict), defaultdict(dict), defaultdict(dict), defaultdict(dict)
    LB = defaultdict(dict)
    for x in db.execute('SELECT wflb_utc t, wflb_tf tf, wflb_dr d, wflb_verdict v, wflb_ungated g, '
                        'wflb_r r, wflb_mfr_out m, wflb_stalled st, wflb_level lv, wflb_slope sp, '
                        'wflb_fit fi, wflb_curl_ends ce, wflb_last_verdict lastv, '
                        'wflb_verdict_dwell dw, wflb_aligned al, wflb_bend_align ba, '
                        'wflb_bendfit bf FROM wsf_line_bar '
                        'WHERE wflb_knobs=%s AND wflb_tf <= %s AND wflb_utc >= %s AND wflb_utc < %s',
                        (KNOBS, MAX_TF, WIN_FROM, WIN_TO), fetch=True):
        k = (int(x['d']), int(x['tf']))
        V[str(x['t'])][k] = x['v']; U[str(x['t'])][k] = x['g']
        R[str(x['t'])][k] = float(x['r']); MFR[str(x['t'])][k] = int(x['m'] or 0)
        LB[str(x['t'])][k] = x

    BT = defaultdict(dict)
    for x in db.execute('SELECT wbt_utc t, wbt_tf tf, wbt_dr d, wbt_sat_left sl, wbt_sat_bars sb, '
                        'wbt_mage mg, wbt_mage_oob_tol mt, wbt_stoch_now sn, wbt_stoch_out so, '
                        'wbt_rsi rsi, wbt_rsi_lo rlo, wbt_rsi_hi rhi FROM wsf_bar_tf '
                        'WHERE wbt_tf <= %s AND wbt_wmt_tf_lo=%s AND wbt_wmt_tf_hi=%s '
                        'AND wbt_utc >= %s AND wbt_utc < %s',
                        (MAX_TF, WMT_TF_LO, WMT_TF_HI, WIN_FROM, WIN_TO), fetch=True):
        BT[str(x['t'])][(int(x['d']), int(x['tf']))] = x

    WM = {}
    for x in db.execute('SELECT wbt_utc t, wbt_dr d, wbt_weak_mage_tf w FROM wsf_bar_tf '
                        'WHERE wbt_tf=1 AND wbt_wmt_tf_lo=%s AND wbt_wmt_tf_hi=%s '
                        'AND wbt_utc >= %s AND wbt_utc < %s',
                        (WMT_TF_LO, WMT_TF_HI, WIN_FROM, WIN_TO), fetch=True):
        WM[(str(x['t']), int(x['d']))] = x['w']

    XR, XRACE = {}, {}
    for x in db.execute('SELECT wxc_utc t, wxc_tf tf, wxc_dr d, wxc_x_r xr, wxc_race_won w '
                        'FROM wsf_x_cross WHERE wxc_xwob=%s AND wxc_tf <= %s '
                        'AND wxc_utc >= %s AND wxc_utc < %s',
                        (XCROSS_XWOB, MAX_TF, WIN_FROM, WIN_TO), fetch=True):
        XR[(str(x['t']), int(x['tf']), int(x['d']))] = int(x['xr'] or 0)
        XRACE[(str(x['t']), int(x['tf']), int(x['d']))] = x['w']

    RUN_UTC = None   # stamped at INSERT, below, so wee_dt_created is a creation time
    RUN = 1                         # replaced below, once the table exists
    # THE CATALOGUE IS THE CONTRACT. Joe 0827: "that table holds the dataset that you refer to
    # for each decision - when you have a confirmed ingredient list, you won't miss any of them".
    #   wig_confirmed = 1  live. The default, so a new ingredient is picked up with no code edit.
    #   wig_confirmed = 0  SUPERSEDED, on Joe's ruling. Not read, and no row written for it.
    #   wig_retired_utc    set instead of deleting. Also excluded.
    CAT = {r['wig_name']: (int(r['wig_pk']), int(r['wig_read'])) for r in db.execute(
        'SELECT wig_pk, wig_name, wig_read FROM wsf_ingredient '
        'WHERE wig_confirmed=1 AND wig_retired_utc IS NULL', fetch=True)}
    if not CAT:
        print('  wsf_ingredient has no live rows. Run build_wsf_ingredient.py first.', flush=True)
        return 1
    sup = db.execute('SELECT COUNT(*) c FROM wsf_ingredient WHERE wig_confirmed=0 '
                     'OR wig_retired_utc IS NOT NULL', fetch=True)[0]['c']
    print(f'  {len(CAT)} live ingredients in the catalogue, {sup} superseded or retired',
          flush=True)

    # THE IN-FLIGHT GATE, Joe 0828: "gate any events that fire between an exhaust event, and the
    # x-cross event. if it's a forced-exhaust, then there is no gate applied".
    # An exhaust that has fired is walking forward for its own cross. Anything that fires inside
    # that window is suppressed - no row, no ingredients, no pool move.
    # THREE CONCRETIONS, DECIDED AND STATED:
    #   1. THE WINDOW IS STRICTLY BETWEEN. E < t < X. Joe said "between", so neither the exhaust
    #      bar nor the cross bar is itself gated.
    #   2. THE GATE IS HELD BY THE MOST RECENT EVENT THAT WAS NOT ITSELF GATED, and it ends at
    #      that event's cross. An exhaust whose cross never prints holds the gate to the end.
    #   3. "IF IT'S A FORCED-EXHAUST" READS AS THE EVENT UNDER TEST, not the one holding the gate.
    #      A forced exhaust fires through the window; a maxtf or plain exhaust does not.
    gate_until = None      # the cross bar of the event holding the gate. None = no gate in flight

    # THE POOL. Ported from build_wsf_walk.py 0828. ONE pool of MAX_TRADES slots, each armed or
    # open. My call there and unchanged here: 2 armed plus 2 open would let both armed convert and
    # give 3 open against Joe's "max 2 trades". One pool cannot overfill.
    pool = []

    def slots_of():
        """the bar each pooled trade OPENED and the line that opened it, in slot order.

        Joe 0828: the slot answers "when did the trade open", so it carries the x-cross bar, not
        the exhaust bar that armed it. A pooled event whose cross never printed opened no trade
        and reads NULL as well - the pool count and the displayed count can differ, and that
        difference is the honest reading. MINE, STATED."""
        out = []
        for k in range(MAX_TRADES):
            out += [pool[k]['xc'], pool[k]['tf']] if k < len(pool) else [None, None]
        return tuple(out)

    VALUE_NAMES = set()   # every ingredient this script knows how to read, filled as it walks
    events, ingr, sigs = [], [], []
    prev_top = {}          # last bar's verdict on the ceiling line, per dr
    was_on = {1: False, -1: False}   # the exhaust condition on the previous bar, per dr
    seq = 0

    for i, t in enumerate(T):
        dr = int(DR[i])
        if dr == 0:
            continue
        board, rv = V.get(t), R.get(t)
        if not board:
            continue

        top_now = board.get((dr, MAX_TF))
        top_prev = prev_top.get(dr)
        prev_top[dr] = top_now

        # 3a  the maxTF declaration, Joe 0819
        a = (top_prev in ('momo', 'curl')) and top_now == 'none'
        # 3b  the plain wsf-exhaust
        holding = [tf for tf in range(1, MAX_TF + 1) if board.get((dr, tf)) in ('momo', 'curl')]
        b = not holding
        # 3c  the x-cross forced exhaust, Joe 0825
        past = [tf for tf in range(1, MAX_TF + 1) if board.get((dr, tf)) == 'none'
                and (dr, tf) in rv and (rv[(dr, tf)] >= HI if dr > 0 else rv[(dr, tf)] <= LO)]
        inside = [tf for tf in range(1, MAX_TF + 1) if board.get((dr, tf)) in ('momo', 'curl')
                  and (dr, tf) in rv
                  and not (rv[(dr, tf)] >= HI if dr > 0 else rv[(dr, tf)] <= LO)]
        c = next((p for p in sorted(past)
                  if any(h > p for h in inside) and XR.get((t, p, dr))), None)

        on = a or b or (c is not None)
        # THE RISING EDGE. A wsf-exhaust stretch runs for many consecutive bars; one event is one
        # event. MINE, STATED, and recorded in docs/wsf_walk.md section 4 as M3.
        if not on or was_on[dr]:
            was_on[dr] = on
            continue
        was_on[dr] = on

        tests = [n for n, f in (('maxtf', a), ('plain', b), ('forced', c is not None)) if f]
        trig = MAX_TF if a else (c if c is not None else None)
        bank = (not BANK_FROM) or t[11:] >= BANK_FROM
        seq += 1

        # ---- the signal, recipe steps 4 and 5
        wm = WM.get((t, dr))
        route = 'weak-mage' if wm else 'rule-c'
        watch = int(wm) if wm else 2          # rule C's fallback line, Joe 0826: "the next ws2x-cross"
        fired_utc, fired_target = None, None
        prev_won = XRACE.get((t, watch, dr))
        for j in range(i + 1, len(T)):
            w = XRACE.get((T[j], watch, dr))
            if w is not None and prev_won is None:
                fired_utc, fired_target = T[j], w
                break
            prev_won = w
        lag = None if fired_utc is None else (IDX[fired_utc] - i) * GRID
        if bank and not gated:
            sigs.append(((t, dr), fired_utc, lag, watch, route, fired_target,
                         '' if fired_utc else 'no cross to the end of the tape'))

        # ---- THE POOL, recipe step 6. An opposing exhaust closes what is open and takes slot 1;
        # Joe 0825: "when x-cross forces the wsf-exhaust event, any open positions are closed and
        # the first pyramid slot is opened". A same-side exhaust arms a free slot. A full pool
        # takes no action - Joe 0825: "stay dormant until an opposing dr prints".
        if pool and dr != pool[0]['dr']:
            pool = [{'dr': dr, 'at': t, 'xc': fired_utc, 'tf': watch if fired_utc else None}]
            pool_note = 'opposing dr - closed the pool, took slot 1'
        elif len(pool) < MAX_TRADES:
            pool.append({'dr': dr, 'at': t, 'xc': fired_utc, 'tf': watch if fired_utc else None})
            pool_note = f'took slot {len(pool)} of {MAX_TRADES}'
        else:
            pool_note = 'both slots occupied - dormant, no action'
        # THE GATE. Applied AFTER the cross is known, because the gate the event would itself
        # hold is its own cross, and before the pool moves, because a gated event moves nothing.
        gated = (gate_until is not None and t < gate_until and 'forced' not in tests)
        if gated:
            if TRACE_ONLY:
                print(f"  {seq:<4}{t[11:]:<10}{dr:>+3}  {','.join(tests):<14}"
                      f"watch ws{watch:<3}{('cross ' + fired_utc[11:]) if fired_utc else 'no cross':<16}"
                      f"GATED - in flight to {gate_until[11:]}", flush=True)
            continue
        gate_until = fired_utc or T[-1]

        if TRACE_ONLY:
            print(f"  {seq:<4}{t[11:]:<10}{dr:>+3}  {','.join(tests):<14}"
                  f"watch ws{watch:<3}{('cross ' + fired_utc[11:]) if fired_utc else 'no cross':<16}"
                  f"{pool_note:<40}"
                  f"slots {[ (p['xc'][11:] if p['xc'] else None) for p in pool ]}", flush=True)
        # THE BANKING FLOOR. The pool above has already been updated - the walk is unbroken - and
        # only the rows are withheld. seq keeps counting so the sequence numbers stay honest.
        if not bank:
            continue
        events.append((SIG, RUN, RUN_UTC, STOP_AFTER, BANK_FROM, seq, t, dr, ','.join(tests), MAX_TF, trig,
                       _lines(holding), _lines(past),
                       f'declared by {" + ".join(tests)}. {pool_note}')
                      + slots_of() + (fired_utc, watch))

        # ---- the ingredients, one row per (event, ingredient)
        killed = [tf for tf in range(1, MAX_TF + 1)
                  if U.get(t, {}).get((dr, tf)) in ('momo', 'curl')
                  and board.get((dr, tf)) == 'none']
        vals = {
            'three-mage dr':             f'dr {dr:+d}, lookback lag {int(LAG[i]) * GRID} s',
            'the dr latch':              f'live print at this bar: {"yes" if int(DRr[i]) else "no"}',
            'verdict':                   f'holding momo or curl: {_lines(holding) or "none"}',
            'r value':                   f'past the fence: {_lines(past) or "none"}',
            'the maxTF declaration':     f'ws{MAX_TF}r {top_prev} -> {top_now}',
            'the plain wsf-exhaust':     'true' if b else 'false',
            'the x-cross forced exhaust': (f'ws{c}x crossed ws{c}r' if c is not None else 'no cross'),
            'weak-mage-tf':              (f'ws{wm}' if wm else 'NONE'),
            'rule C':                    ('applied - watch ws2x' if not wm else 'not applied'),
            'the x-cross race':          (f'{fired_target} at {fired_utc[11:]}' if fired_utc else 'none'),
            'x-cross direction':         ('x crosses UNDER' if dr > 0 else 'x crosses OVER'),
            'the momentum-kill':         f'killed: {_lines(killed) or "none"}',
            'momo-fence-r':              f'{100 - 17} / 17, out: '
                                         + (_lines([tf for tf in range(1, MAX_TF + 1)
                                                    if MFR.get(t, {}).get((dr, tf))]) or 'none'),
            'the 85/15 boundary':        f'{HI:.0f} / {LO:.0f}',
            'the ladder ceiling':        f'ws1 to ws{MAX_TF}',
            'maxTF distance from fence': (f'ws{MAX_TF}r {rv[(dr, MAX_TF)]:.2f}, '
                                          f'{abs((HI if dr > 0 else LO) - rv[(dr, MAX_TF)]):.2f} from the fence'
                                          if (dr, MAX_TF) in rv else None),
            # JOE 0827's four. Each reads a column that was already banked.
            'the baton':      (f'killed: {_lines(killed) or "none"}. baton now held by '
                               + (f'ws{max(holding)}' if holding else 'NOBODY - dropped')),
            'depth':          _depth(BT.get(t, {}), dr),
            'limits':         ('r at a limit: '
                               + (_lines([tf for tf in range(1, MAX_TF + 1)
                                          if (dr, tf) in rv and rv[(dr, tf)] in (0.0, 100.0)]) or 'none')),
            'am I in trade': (f'{sum(1 for s_ in pool if s_["xc"])} of {MAX_TRADES} trades open: '
                              + ('  '.join(f'trade {k + 1} {s_["xc"][11:]} on ws{s_["tf"]}x'
                                           for k, s_ in enumerate(pool) if s_['xc']) or 'none')),
            'the matryoshka': (f'holding ws1-ws4: {_lines([h for h in holding if h <= 4]) or "none"}   '
                               f'holding ws5-ws{MAX_TF}: {_lines([h for h in holding if h > 4]) or "none"}'),
        }
        # ---- THE 22 READERS. Every live ingredient that had no value expression now has one.
        # Each reads the SAME banked column report_wsf_bar prints, so the two cannot disagree.
        lb, bt = LB.get(t, {}), BT.get(t, {})
        hd = {tf: _heading(lb[(dr, tf)]) for tf in range(1, MAX_TF + 1) if (dr, tf) in lb}
        rib = [tf for tf in range(1, MAX_TF + 1)
               if (dr, tf) in rv and LO < rv[(dr, tf)] < HI]
        so = _col(bt, dr, 'so')
        vals.update({
            # wsf_line_bar
            'heading':          '  '.join(f'ws{tf} {h}' for tf, h in sorted(hd.items())) or None,
            'r IB':             _lines(rib) or 'none',
            'curl_dr':          ('  '.join(
                                    f'ws{tf} ' + ('+1' if lb[(dr, tf)]['ce'] == 'up' else '-1')
                                    for tf in range(1, MAX_TF + 1)
                                    if (dr, tf) in lb and lb[(dr, tf)]['v'] == 'curl'
                                    and lb[(dr, tf)]['ce'] in ('up', 'down')) or 'none'),
            'stalled':          _flag(_col(lb, dr, 'st')),
            '50 gate':          _per_line([(tf, g) for tf in range(1, MAX_TF + 1)
                                           if (dr, tf) in lb
                                           for g in [_level_gate(lb[(dr, tf)], dr)]
                                           if g is not None]),
            'blocked by 50':    _lines([tf for tf in range(1, MAX_TF + 1)
                                        if (dr, tf) in lb and not int(lb[(dr, tf)]['lv'] or 0)]) or 'none',
            'last-verdict':     '  '.join(f'ws{tf} {lb[(dr, tf)]["lastv"]}'
                                          for tf in range(1, MAX_TF + 1)
                                          if (dr, tf) in lb and lb[(dr, tf)]['lastv']) or 'none',
            'last-verdict-dwell': _per_line(_col(lb, dr, 'dw'), '{:.0f} s'),
            # wsf_bar_tf
            'Mage value':       _per_line(_col(bt, dr, 'mg')),
            'lb-mage-oob':      _flag(_col(bt, dr, 'mt')),
            'Mage lines out of bounds': (f'{sum(1 for _, v in _col(bt, dr, "mt") if v)} of '
                                         f'{len(_col(bt, dr, "mt"))}'),
            'stoch now':        _per_line(_col(bt, dr, 'sn')),
            'stoch out':        _per_line(so),
            'sat clock':        _per_line(_col(bt, dr, 'sb'), '{:.0f}'),
            'sat left':         _per_line(_col(bt, dr, 'sl'), '{:.0f}'),
            'RSI':              _per_line(_col(bt, dr, 'rsi')),
            # jig
            # DR IS BAKED IN. Joe 0828: "this would be resolved if `dr` was taming the
            # statements ... if your refering to 'only fall' then the line must be high. bake the
            # dr into the ingredient". "only fall" and "cannot rise" are the same reading; without
            # dr the two phrasings look like a disagreement. The wording is Joe's own footer:
            # "a dr +1 trade needs r to fall, so N of M lines are mechanically committed to it".
            #   stoch out 100 -> r cannot rise, so it can only FALL
            #   stoch out   0 -> r cannot fall, so it can only RISE
            'stoch_out_extreme': (
                lambda need, committed, blocked:
                    f'a dr {dr:+d} trade needs r to {need}, so {len(committed)} of {len(so)} '
                    f'lines are mechanically committed to it: {_lines(committed) or "none"}   '
                    f'blocked (r cannot {need}): {_lines(blocked) or "none"}'
                )('fall' if dr > 0 else 'rise',
                  [tf for tf, v in so if round(float(v), 6) == (100.0 if dr > 0 else 0.0)],
                  [tf for tf, v in so if round(float(v), 6) == (0.0 if dr > 0 else 100.0)]),
            # momo_gated
            'wsf-curl-mode':    ('  '.join(
                                    f'ws{tf} ' + _curl_mode(lb[(dr, tf)])
                                    for tf in range(1, MAX_TF + 1)
                                    if (dr, tf) in lb and _curl_mode(lb[(dr, tf)])) or 'none'),
            # report_wsf_bar's footer aggregates, from the same headings
            'away / toward counts': (
                f'away {sum(1 for h in hd.values() if h == "away")} '
                f'({_lines([tf for tf, h in sorted(hd.items()) if h == "away"]) or "-"})   '
                f'toward {sum(1 for h in hd.values() if h == "toward")} '
                f'({_lines([tf for tf, h in sorted(hd.items()) if h == "toward"]) or "-"})'),
            'r IB count':       f'{len(rib)} of {MAX_TF}',
            'LTF away / HTF toward': (
                f'LTF away {sum(1 for tf, h in hd.items() if tf <= 4 and h == "away")}   '
                f'HTF toward {sum(1 for tf, h in hd.items() if tf > 4 and h == "toward")}   '
                f'(LTF is ws1-ws4, HTF is ws5-ws{MAX_TF})'),
        })
        # EVERY ingredient in the catalogue gets a row, read or not. That is the point of the
        # list - a missing row would be a silently skipped ingredient.
        VALUE_NAMES.update(vals)
        for name, (wig, read) in CAT.items():
            ingr.append(((t, dr), wig, read, vals.get(name)))


        # RUN SCOPE. Joe 0827: "for the walk: stop on the first wsf-exhaust". The stop is recorded
        # on every event row as wee_stop_after, so a truncated run can never be mistaken for a
        # complete one.
        if STOP_AFTER and len(events) >= STOP_AFTER:
            print(f'  stopping after {len(events)} event(s) at {t} - STOP_AFTER={STOP_AFTER}',
                  flush=True)
            break

    if TRACE_ONLY:
        print('\n  TRACE ONLY - nothing banked', flush=True)
        db.disconnect()
        return 0
    for ddl in (DDL_EVENT, DDL_INGR, DDL_SIG):
        db.execute(ddl)
    # NO DELETE. The run number is one past the highest already banked at this signature, so the
    # previous run's events, ingredient usage and signals all stand.
    prev = db.execute('SELECT COALESCE(MAX(wee_run), 0) r FROM wsf_exhaust_event WHERE wee_knobs=%s',
                      (SIG,), fetch=True)[0]['r']
    RUN = int(prev) + 1
    RUN_UTC = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    events = [(e[0], RUN, RUN_UTC) + e[3:] for e in events]
    print(f'  run {RUN} at these knobs. {prev} earlier run(s) kept.', flush=True)
    db.executemany(f'INSERT INTO wsf_exhaust_event ({",".join(E_COLS)}) VALUES '
                   f'({",".join(["%s"] * len(E_COLS))})', events)
    # THE PARENT KEYS, READ BACK. The children carry the FK and nothing else of the parent's.
    PK = {(str(x['u']), int(x['d'])): int(x['p']) for x in db.execute(
        'SELECT wee_pk p, wee_utc u, wee_dr d FROM wsf_exhaust_event '
        'WHERE wee_knobs=%s AND wee_run=%s', (SIG, RUN), fetch=True)}
    db.executemany(f'INSERT INTO wsf_event_ingredient ({",".join(I_COLS)}) VALUES '
                   f'({",".join(["%s"] * len(I_COLS))})',
                   [(PK[k],) + tuple(r) for k, *r in ((x[0],) + x[1:] for x in ingr)])
    db.executemany(f'INSERT INTO wsf_event_signal ({",".join(S_COLS)}) VALUES '
                   f'({",".join(["%s"] * len(S_COLS))})',
                   [(PK[k],) + tuple(r) for k, *r in ((x[0],) + x[1:] for x in sigs)])

    # THE GUARD THAT MAKES AUTO-CONFIRM SAFE. A new ingredient lands live the moment it is added
    # to wsf_ingredient, so it gets a row here whether or not this script knows how to read it. A
    # row with a NULL value is either "no machine reading" by design or "nobody wrote the reader
    # yet", and those must not look the same. This names the second kind out loud.
    #   MINE, STATED. Joe asked for the auto-confirm; the visibility of the gap is my addition.
    NO_HOME = {r['wig_name'] for r in db.execute(
        "SELECT wig_name FROM wsf_ingredient WHERE wig_home='nowhere'", fetch=True)}
    # no events means VALUE_NAMES was never filled, and every name would read as unwired
    unread = sorted(n for n in CAT if n not in VALUE_NAMES and n not in NO_HOME) if events else []
    if unread:
        print(f'\n  {len(unread)} live ingredient(s) have no value expression in this script:',
              flush=True)
        for n in unread:
            print(f'    {n}   -> every row banked with a NULL value', flush=True)

    print(f'\n  run {RUN}   dt_created {RUN_UTC}', flush=True)
    print(f'  wsf_exhaust_event    : {len(events):,} events', flush=True)
    print(f'  wsf_event_ingredient : {len(ingr):,} rows  ({len(CAT)} ingredients per event)',
          flush=True)
    print(f'  wsf_event_signal     : {len(sigs):,} rows, '
          f'{sum(1 for s in sigs if s[3])} with a cross\n', flush=True)
    print(f"  {'#':<5}{'utc':<11}{'dr':>4}  {'declared by':<20}{'watch':<8}{'signal':<11}{'lag':>8}",
          flush=True)
    # THE PRINT READS E_COLS BY NAME, NOT BY POSITION. Adding wee_run and wee_run_utc shifted every
    # index and the first run printed the run number where the bar belonged. Rows were correct; the
    # display was not.
    E_AT = {c: i for i, c in enumerate(E_COLS)}
    for e, s in zip(events, sigs):
        lag = '' if s[2] is None else f'{s[2] // 60}m{s[2] % 60:02d}s'
        print(f"  {e[E_AT['wee_seq']]:<5}{e[E_AT['wee_utc']][11:]:<11}"
              f"{e[E_AT['wee_dr']]:>+4}  {e[E_AT['wee_test']]:<20}"
              f"{('ws' + str(s[3]) + (' rc' if s[4] == 'rule-c' else '')):<8}"
              f"{(s[1][11:] if s[1] else '-'):<11}{lag:>8}", flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
