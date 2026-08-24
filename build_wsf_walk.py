"""build_wsf_walk — the ws-finisher walk. Joe's IF statements at each checkpoint, bar by bar.

Joe 0819: "walk the bars, and use IF statements at each checkpoint (ie per bar, per wsf9of12, per
handoff, so-on)". This is that walk, run over 08-04 against the 121 tagged timestamps in
transfer/260819_wsf_model_training_timestamps.csv.

PASS ONE IS FOR FINDING GAPS, NOT FOR A HIT RATE. Joe 0819: "we're not modelling for a hit rate in
these first few passes - we're modelling to find the gaps ... for me, it means investigating the
'non covered' datasets that you'll store, so I can find the next lesson".

CAUSAL. Every test reads the bar it is on or an earlier one. Nothing reads forward. The one
exception is `wsw_mae`, the maximum adverse excursion, which is a REPORT field measured after the
fact - it is never read by a decision.

────────────────────────────────────────────────────────────────────────────────────────────────
THE THREE CHECKPOINTS

  1. a wsf9of12 signal bar                      121 on 08-04
  2. a domTF handoff bar                        61 on 08-04
  3. a retest - a line that was tagged as of the PREVIOUS bar now stalls or crosses out of bounds

Joe 0819 on "tagged": "my shorthand for a line that is in momo or curl state".

────────────────────────────────────────────────────────────────────────────────────────────────
THE ORDER INSIDE A BAR. Joe 0819 twice.

    read this bar's stall and boundary-cross state
    IF a tagged line now stalls or crosses out of bounds -> RETEST HERE, still tagged
    IF latch 1 conditions -> create wsf-exhaust
    IF latch 2 conditions -> fire the trade
    IF reset conditions   -> clear both latches

Joe 0819: "it seems that the best solution is to inject the retest code between `stall detected`
and `momentum=none`", then "do the momentum scan on the previous bar (ie 5sec earlier)". So BOTH
the retest trigger and the momentum scan read the bar 5 seconds earlier.

────────────────────────────────────────────────────────────────────────────────────────────────
THE FLOW AT A CHECKPOINT. Joe 0818-19, the IF / ELIF.

    IF   any of ws4r..ws8r carries momentum  -> blocked
    ELIF any of ws1r..ws3r carries momentum  -> blocked
    ELSE                                     -> no r line carries momentum, LATCH 1 fires

Joe 0819 on the retest re-entering: "use the ELSE/ELIF flow", and on the lower branch: "this
captures the potential LTF 'last mile' granularity that could exist after ws{4:8}r has completed
its high level run".

Joe 0819 on what fires latch 1: "wsf-exhaust can fire only when the mech's conditions are true
(simply put, there are no more r lines showing momentum, therefore no more retests will occur)".

────────────────────────────────────────────────────────────────────────────────────────────────
THE DUAL LATCH. Joe 0819: "'wsf-exhaust' and 'trade signal' are 2 parts of a dual latch. trade
signal cannot fire unless wsf-exhaust has fired".

  latch 1  wsf-exhaust. Fires when the flow above reaches the ELSE.
  latch 2  the trade signal. Arms with the weak-mage-tf, fires on the x-cross.

THE x-CROSS IS A RACE. Joe 0819: "the cross target: any one - race condition" over
[Mage, b, boundary]. Direction, Joe 0818: "x crosses over if dr==-1, and x crosses under if dr==1"
- so a downward position fires when the fast partner crosses UP over a target, and an upward
position when it crosses DOWN under one. The boundary in the race follows from that: the HIGH
fence when the position is down, the LOW fence when it is up.

RESET. Joe 0819: "latch 1 and 2 reset on a trade fire, or when all ws{current-max-tf-with-momentum}
lines are IB", with "when I don't add the suffix, I'm telling you to use all lines in the
ws{current-max-tf-with-momentum} inidcator set" - so all five of r, x, m, b and Mage at that
timeframe, tested against the RAW fences (D13).

────────────────────────────────────────────────────────────────────────────────────────────────
WHAT IS NOT BUILT, AND IS FLAGGED RATHER THAN GUESSED

  wsf-r-weakness      Joe 0819 deferred it. Where his tag says fire and v_ws_fin_walk says BLOCKED,
                      the walk CAPTURES the r picture instead: how many lines in bounds, which ones.
  the domTF override  "when the wsf LTFs are all/mostly in agreeance, then the domTF BLOCK is
                      overriden" has no threshold. Not implemented.
  the reset with no   when no line carries momentum there is no current max timeframe, so the reset
  max timeframe       has no indicator set to test. UNRULED - the walk flags it not-covered.

────────────────────────────────────────────────────────────────────────────────────────────────
EVERY SIGNAL IS A CHECKPOINT. Joe 0819: "recreate the walk so that all signals are read".
Run 1 read only the signals whose direction matched the open position's, skipping 58 of the 121.
That was my assumption and Joe never said it. Run 2 reads all 121.

THE RATCHET AND THE ws8r DECLARATION. Joe 0819, two additions.

  "stall TF values can only increase (eg a ws6r stall event cannot happen after a ws7r stall)"
      A retest trigger on timeframe N is only honoured if N is at or above the highest timeframe
      that has already triggered. Joe 0819 ruled it governs BOTH the stall and the boundary cross,
      and that it resets ONLY on a trade fire - not when the latches reset.

  "when ws8r stalls or crosses to oob, wsf-exhaustion is declared"
      A second, independent path to latch 1, alongside the ELSE. Joe 0819 confirmed it fires
      "regardless of what ws1r to ws7r are doing". Joe 0819: "it needs to be carrying
      momentum before it stalls" - the same tagged condition the retest trigger uses.

THE POSITION. Joe 0819: "start with an open trade at 0804 00:18:35, and walk forward from there",
"it's the direction of the open position", and "trades reverse on the next wsf trade signal".
"""
import csv
import os
import sys
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import mech_lines
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key
from optimus9.analysis.jig import weak_mage_tf, WMT_TFS, WMT_LOOKBACK_S

WIN_FROM = '2026-08-04 00:00:00'
WIN_TO   = '2026-08-05 00:00:00'
OPEN_AT  = '2026-08-04 00:18:35'      # Joe 0819: start with an open trade here
TAGS_CSV = '/home/joe/thecodes/transfer/260819_wsf_model_training_timestamps.csv'
HI_BAND  = (4, 8)                     # the IF  branch. Joe 0818: momentum in ANY of ws4:8
LO_BAND  = (1, 3)                     # the ELIF branch
GRID_S   = 5
ROLES    = ('r', 'x', 'm', 'b', 'Mage')

STATE_DDL = '''CREATE TABLE IF NOT EXISTS wsf_exhaust_state (
    wes_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    wes_win_from DATETIME NOT NULL,
    wes_run      INT NOT NULL,
    wes_utc      DATETIME NOT NULL,      -- the bar wsf-exhaust changed
    wes_on       TINYINT NOT NULL,       -- 1 = it went on here, 0 = it went off here
    wes_cause    VARCHAR(16) NOT NULL,   -- ELSE | ws8r | trade fired | reset
    wes_pos_dr   TINYINT NOT NULL,       -- the open position's direction at that bar
    wes_attr_utc DATETIME,               -- on a turn-on: the most recent wsf9of12 signal OR domTF
                                         -- handoff at or before this bar. Joe 0819, backtesting
    wes_attr_kind VARCHAR(8),            -- signal | handoff. A signal on the same bar wins
    UNIQUE KEY uq_wes (wes_win_from, wes_run, wes_utc),
    KEY k_on (wes_on), KEY k_attr (wes_attr_utc))'''

CHK_DDL = '''CREATE TABLE IF NOT EXISTS wsf_walk_checkpoint (
    wwc_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    wwc_win_from DATETIME NOT NULL,
    wwc_run      INT NOT NULL,           -- the walk run. Knobs that change rows go in the key with it
    wwc_utc      DATETIME NOT NULL,      -- the checkpoint bar
    wwc_kind     VARCHAR(8) NOT NULL,    -- signal | handoff | retest
    wwc_pos_dr   TINYINT NOT NULL,       -- the open position's direction the walk read in
    wwc_branch   VARCHAR(8) NOT NULL,    -- ws4:8 | ws1:3 | ELSE. The IF/ELIF, scanned on the previous bar
    wwc_max_tf   SMALLINT,               -- highest timeframe carrying momentum on the previous bar
    wwc_n_hi     SMALLINT NOT NULL,      -- how many of ws4r..ws8r carried momentum
    wwc_n_lo     SMALLINT NOT NULL,      -- how many of ws1r..ws3r carried momentum
    wwc_trig_tf  SMALLINT,               -- on a retest, the line that stalled or crossed
    wwc_trig_how VARCHAR(8),             -- stall | cross
    wwc_weak_tf  SMALLINT,               -- weak-mage-tf, the producer run AT THIS BAR. NULL = none found
    wwc_latch1   TINYINT NOT NULL,       -- wsf-exhaust set after this checkpoint
    wwc_latch2_tf SMALLINT,              -- the timeframe latch 2 armed with
    wwc_domtf    VARCHAR(8),             -- on a signal bar, domTF as given by v_ws_fin_walk
    wwc_tag      VARCHAR(8),             -- on a signal bar, Joe's fire/delay tag
    wwc_not_covered VARCHAR(64),         -- a mechanic the walk does not have was needed here
    UNIQUE KEY uq_wwc (wwc_win_from, wwc_run, wwc_utc, wwc_kind, wwc_trig_tf),
    KEY k_kind (wwc_kind), KEY k_nc (wwc_not_covered), KEY k_tag (wwc_tag))'''

SEQ_DDL = '''CREATE TABLE IF NOT EXISTS wsf_walk_sequence (
    wws_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    wws_win_from DATETIME NOT NULL,
    wws_run      INT NOT NULL,
    wws_open_utc DATETIME NOT NULL,      -- the bar the position opened
    wws_pos_dr   TINYINT NOT NULL,       -- its direction
    wws_open_pxs DOUBLE,                 -- pxs at the open. From the jig, Joe 0819
    wws_latch1_utc DATETIME,             -- the bar wsf-exhaust fired
    wws_arm_utc  DATETIME,               -- the bar latch 2 armed
    wws_arm_tf   SMALLINT,               -- the weak-mage-tf it armed with
    wws_fire_utc DATETIME,               -- the bar the trade signal fired
    wws_fire_by  VARCHAR(10),            -- which of the race won: Mage | b | boundary
    wws_fire_pxs DOUBLE,
    wws_mae      DOUBLE,                 -- maximum adverse excursion, open to close. REPORT ONLY
    wws_bars     INT,                    -- bars the position was open
    wws_checkpoints INT,                 -- checkpoints walked inside it
    wws_not_covered VARCHAR(64),
    wws_attr_utc  DATETIME,              -- the most recent wsf9of12 signal OR domTF handoff at or
                                         -- before the bar wsf-exhaust switched on. Joe 0819,
                                         -- backtesting only: it lets an exhaust carry a timestamp
                                         -- that exists in his csv
    wws_attr_kind VARCHAR(8),            -- signal | handoff. A signal on the same bar beats a handoff
    UNIQUE KEY uq_wws (wws_win_from, wws_run, wws_open_utc),
    KEY k_fire (wws_fire_utc))'''


def _load(db):
    """Everything the walk reads. Nothing is computed here."""
    s = db.execute('SELECT pxsmooth_dema_src src, pxsmooth_dema_len len, hi_boundary hi, '
                   'lo_boundary lo FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
    HI, LO = float(s['hi']), float(s['lo'])
    tp = np.load(os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP,
                                                  {'src': s['src'], 'len': s['len']}) + '.npz'))
    ts, pxs = tp['__ts__'], tp['__pxs__']

    # the lines, spread from mech_line_config. ONE source - ws_line_bar's Mage is identical to
    # the cache's on all 17,281 bars, verified 0819, so there is no second copy to fork from.
    L = {}
    for g in mech_lines(db, 'wsf'):
        L[(g['role'], g['tf_seconds'] // 60)] = np.load(
            os.path.join(LINE_DIR, _line_key(END_MS, HOURS, WARMUP, g['override']) + '.npy'))

    # the r measurements, per timeframe per direction
    M, S, O = {}, {}, {}
    for tf in range(1, 9):
        for dr in (+1, -1):
            rows = db.execute('SELECT wflb_ungated v, wflb_stalled s, wflb_oob o FROM wsf_line_bar '
                              'WHERE wflb_tf=%s AND wflb_dr=%s ORDER BY wflb_utc',
                              (tf, dr), fetch=True)
            M[(tf, dr)] = np.array([r['v'] in ('momo', 'curl') for r in rows], bool)
            S[(tf, dr)] = np.array([r['s'] for r in rows], bool)
            O[(tf, dr)] = np.array([r['o'] for r in rows], bool)

    sig = {str(r['g']): (int(r['side']), r['domTF']) for r in db.execute(
        'SELECT g30_marker g, side, domTF FROM v_ws_fin_walk', fetch=True)}
    ho = {str(r['h']) for r in db.execute(
        "SELECT wsf_ho_utc h FROM ws_fin_9of12 WHERE wsf_win_from=%s AND wsf_ho_rule='median' "
        "AND wsf_line_hcap='ws1b:1' AND wsf_ho_utc IS NOT NULL", (WIN_FROM,), fetch=True)}
    tags = {}
    with open(TAGS_CSV, encoding='utf-8-sig') as f:
        for r in csv.reader(f):
            if len(r) < 2 or not r[0].strip() or r[0].strip().startswith('g30'):
                continue
            d, t = r[0].split()
            tags[f'2026-{d[:2]}-{d[2:]} {t}'] = 'fire' if r[1].strip().lower().startswith('f') else 'delay'
    return HI, LO, ts, pxs, L, M, S, O, sig, ho, tags


def main():
    # RUN 1 skipped opposite-direction signals. RUN 2 reads every signal. Both stay in the
    # tables side by side - the run number is in the unique key.
    run = 6
    db = DatabaseManager(**get_db_config()); db.connect()
    HI, LO, ts, pxs, L, M, S, O, sig, ho, tags = _load(db)
    look = WMT_LOOKBACK_S // GRID_S + 1
    MAGE = {t: L[('Mage', t)] for t in WMT_TFS}

    def u(ms):
        return dt.datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    i0 = int(np.searchsorted(ts, int(dt.datetime.fromisoformat(WIN_FROM)
                                     .replace(tzinfo=timezone.utc).timestamp() * 1000)))
    i1 = int(np.searchsorted(ts, int(dt.datetime.fromisoformat(WIN_TO)
                                     .replace(tzinfo=timezone.utc).timestamp() * 1000)))
    w0 = int(np.searchsorted(ts, int(dt.datetime.fromisoformat(OPEN_AT)
                                     .replace(tzinfo=timezone.utc).timestamp() * 1000)))
    base = {u(int(ts[k])): k - i0 for k in range(i0, i1 + 1)}       # bar utc -> row in the M/S/O arrays
    print(f'  window {WIN_FROM} -> {WIN_TO}   {i1 - i0 + 1:,} bars', flush=True)
    print(f'  signals {len(sig)}   handoffs {len(ho)}   tags {len(tags)}', flush=True)

    pos_dr = sig[OPEN_AT][0]                       # the opening trade takes that signal's direction
    print(f'  opening position at {OPEN_AT}, direction '
          f'{"down" if pos_dr < 0 else "up"}', flush=True)

    latch1 = False
    arm_tf = None
    ratchet = 0        # the highest timeframe that has triggered. Resets ONLY on a trade fire
    state_rows = []

    def _state(utc, on, cause, dr):
        """One row per CHANGE of wsf-exhaust. Joe 0820: "record every time wsf-exhaust changes,
        on and off, as its own row. One position can then hold several." Before this the walk kept
        one timestamp per position and threw away every later change."""
        a = k = None
        if on:
            cand = [(x, 'handoff') for x in ho if x <= utc] + [(x, 'signal') for x in sig if x <= utc]
            if cand:
                a, k = sorted(cand)[-1]
        state_rows.append((WIN_FROM, run, utc, int(on), cause, dr, a, k))
    seq = {'open': OPEN_AT, 'dr': pos_dr, 'open_pxs': float(pxs[w0]), 'l1': None,
           'arm': None, 'arm_tf': None, 'chk': 0, 'nc': ''}
    chk_rows, seq_rows = [], []

    for w in range(w0 + 1, i1 + 1):
        j = w - i0                                  # the row in M/S/O for this bar
        utc = u(int(ts[w]))
        prev = j - 1

        # ── the retest trigger. A line TAGGED AS OF THE PREVIOUS BAR that now stalls or crosses.
        # the ws8r DECLARATION. Joe 0819: "it needs to be carrying momentum before it stalls" -
        # the same tagged condition the retest trigger uses, read on the PREVIOUS bar. It still
        # fires "regardless of what ws1r to ws7r are doing".
        ws8_declare = (M[(8, pos_dr)][prev]
                       and ((S[(8, pos_dr)][j] and not S[(8, pos_dr)][prev])
                            or (O[(8, pos_dr)][j] and not O[(8, pos_dr)][prev])))
        # the retest trigger. RATCHETED - a timeframe below one that has already triggered is
        # ignored. Scanning downward from 8 so the highest eligible line wins.
        trig_tf = trig_how = None
        for tf in range(8, 0, -1):
            if tf < ratchet or not M[(tf, pos_dr)][prev]:
                continue
            if S[(tf, pos_dr)][j] and not S[(tf, pos_dr)][prev]:
                trig_tf, trig_how = tf, 'stall'; break
            if O[(tf, pos_dr)][j] and not O[(tf, pos_dr)][prev]:
                trig_tf, trig_how = tf, 'cross'; break
        if trig_tf:
            ratchet = trig_tf
        if ws8_declare:
            ratchet = 8

        # EVERY signal is a checkpoint, whatever direction it carries. Joe 0819: "recreate
        # the walk so that all signals are read". Run 1 skipped the 58 signals whose
        # direction differed from the position's - that was my assumption, never his.
        # The scan still reads in the POSITION's direction, per Joe's D11: "it's the
        # direction of the open position". A signal being a checkpoint and a signal
        # setting the read direction are two different things.
        is_sig = utc in sig
        is_ho = utc in ho
        kind = 'signal' if is_sig else ('handoff' if is_ho else
               ('retest' if trig_tf else ('ws8r' if ws8_declare else None)))

        if kind:
            seq['chk'] += 1
            nc = ''
            # ── THE SCAN, on the previous bar. Joe 0819: "do the momentum scan on the previous bar"
            n_hi = sum(1 for tf in range(HI_BAND[0], HI_BAND[1] + 1) if M[(tf, pos_dr)][prev])
            n_lo = sum(1 for tf in range(LO_BAND[0], LO_BAND[1] + 1) if M[(tf, pos_dr)][prev])
            branch = 'ws4:8' if n_hi else ('ws1:3' if n_lo else 'ELSE')
            mx = [tf for tf in range(1, 9) if M[(tf, pos_dr)][prev]]
            max_tf = max(mx) if mx else None
            if ws8_declare:
                branch = 'ws8r'          # the declaration overrides whatever the IF/ELIF found
            if branch in ('ELSE', 'ws8r'):
                if not latch1:
                    _state(utc, True, branch, pos_dr)
                latch1 = True
                if seq['l1'] is None:
                    seq['l1'] = utc
            # ── the weakness test, run AT THIS BAR. Joe 0819: "you can run the weakness tests at
            #    any time" - it is a producer, not a stored column.
            weak_tf = weak_mage_tf(MAGE, HI, LO, w, look, pos_dr)[0]
            if latch1 and arm_tf is None:
                if weak_tf is None:
                    nc = 'latch 1 set but no weak-mage-tf to arm latch 2'
                else:
                    arm_tf = weak_tf
                    seq['arm'], seq['arm_tf'] = utc, weak_tf
            tag = tags.get(utc) if is_sig else None
            dom = sig[utc][1] if is_sig else None
            if is_sig and tag == 'fire' and dom == 'BLOCKED':
                ib = [tf for tf in range(1, 9) if LO < L[('r', tf)][w] < HI]
                nc = (f'r-weakness capture: {len(ib)} of 8 r lines in bounds, '
                      f'{",".join("ws%dr" % t for t in ib)}')[:64]
            chk_rows.append((WIN_FROM, run, utc, kind, pos_dr, branch, max_tf, n_hi, n_lo,
                             trig_tf, trig_how, weak_tf, int(latch1), arm_tf, dom, tag, nc))

        # ── LATCH 2. The x-cross race over Mage, b and the boundary. Any one wins.
        fired_by = None
        if arm_tf is not None:
            fence = HI if pos_dr < 0 else LO
            for name, tgt in (('Mage', L[('Mage', arm_tf)]), ('b', L[('b', arm_tf)]),
                              ('boundary', None)):
                a = L[('x', arm_tf)][w - 1]; b_ = L[('x', arm_tf)][w]
                t0 = fence if tgt is None else tgt[w - 1]
                t1 = fence if tgt is None else tgt[w]
                if pos_dr < 0 and a <= t0 and b_ > t1:
                    fired_by = name; break
                if pos_dr > 0 and a >= t0 and b_ < t1:
                    fired_by = name; break

        if fired_by:
            seq_rows.append((WIN_FROM, run, seq['open'], seq['dr'], seq['open_pxs'], seq['l1'],
                             seq['arm'], seq['arm_tf'], utc, fired_by, float(pxs[w]),
                             None, None, seq['chk'], seq['nc']))
            if latch1:
                _state(utc, False, 'trade fired', pos_dr)
            pos_dr = -pos_dr                       # Joe 0819: trades reverse on the next signal
            latch1 = False; arm_tf = None
            ratchet = 0                            # Joe 0819: the ratchet resets ONLY here
            seq = {'open': utc, 'dr': pos_dr, 'open_pxs': float(pxs[w]), 'l1': None,
                   'arm': None, 'arm_tf': None, 'chk': 0, 'nc': ''}
            continue

        # ── RESET. All five lines of the current max timeframe inside the RAW fences (D13).
        if kind and max_tf is not None:
            if all(LO < L[(role, max_tf)][w] < HI for role in ROLES):
                if latch1:
                    _state(utc, False, 'reset', pos_dr)
                latch1 = False; arm_tf = None
        elif kind and max_tf is None and not seq['nc']:
            seq['nc'] = 'reset has no max timeframe to watch'

    seq_rows.append((WIN_FROM, run, seq['open'], seq['dr'], seq['open_pxs'], seq['l1'],
                     seq['arm'], seq['arm_tf'], None, None, None, None, None, seq['chk'], seq['nc']))

    # ── the maximum adverse excursion. MEASURED AFTER THE FACT, never read by a decision.
    out = []
    for k, s in enumerate(seq_rows):
        a = int(np.searchsorted(ts, int(dt.datetime.fromisoformat(s[2])
                                        .replace(tzinfo=timezone.utc).timestamp() * 1000)))
        end = s[8] or u(int(ts[i1]))
        b_ = int(np.searchsorted(ts, int(dt.datetime.fromisoformat(end)
                                         .replace(tzinfo=timezone.utc).timestamp() * 1000)))
        seg = pxs[a:b_ + 1]
        mae = float((seg.min() - seg[0]) if s[3] > 0 else (seg[0] - seg.max())) if len(seg) else None
        # the attribution. Backward from the bar wsf-exhaust switched on, to the most recent
        # signal OR handoff. A signal on the same bar wins, because that is the timestamp Joe's
        # csv carries.
        attr_u = attr_k = None
        if s[5]:
            cand = [(x, 'handoff') for x in ho if x <= s[5]] + [(x, 'signal') for x in sig if x <= s[5]]
            if cand:
                attr_u, attr_k = sorted(cand)[-1]
        out.append(s[:11] + (mae, b_ - a) + s[13:] + (attr_u, attr_k))

    db.execute(CHK_DDL); db.execute(SEQ_DDL); db.execute(STATE_DDL)
    db.execute('DELETE FROM wsf_walk_checkpoint WHERE wwc_win_from=%s AND wwc_run=%s', (WIN_FROM, run))
    db.execute('DELETE FROM wsf_walk_sequence   WHERE wws_win_from=%s AND wws_run=%s', (WIN_FROM, run))
    C = ['wwc_win_from', 'wwc_run', 'wwc_utc', 'wwc_kind', 'wwc_pos_dr', 'wwc_branch', 'wwc_max_tf',
         'wwc_n_hi', 'wwc_n_lo', 'wwc_trig_tf', 'wwc_trig_how', 'wwc_weak_tf', 'wwc_latch1',
         'wwc_latch2_tf', 'wwc_domtf', 'wwc_tag', 'wwc_not_covered']
    Q = ['wws_win_from', 'wws_run', 'wws_open_utc', 'wws_pos_dr', 'wws_open_pxs', 'wws_latch1_utc',
         'wws_arm_utc', 'wws_arm_tf', 'wws_fire_utc', 'wws_fire_by', 'wws_fire_pxs', 'wws_mae',
         'wws_bars', 'wws_checkpoints', 'wws_not_covered', 'wws_attr_utc', 'wws_attr_kind']
    db.executemany(f'INSERT INTO wsf_walk_checkpoint ({",".join(C)}) VALUES '
                   f'({",".join(["%s"] * len(C))})', chk_rows)
    db.executemany(f'INSERT INTO wsf_walk_sequence ({",".join(Q)}) VALUES '
                   f'({",".join(["%s"] * len(Q))})', out)
    db.execute('DELETE FROM wsf_exhaust_state WHERE wes_win_from=%s AND wes_run=%s', (WIN_FROM, run))
    db.executemany('INSERT INTO wsf_exhaust_state (wes_win_from,wes_run,wes_utc,wes_on,wes_cause,'
                   'wes_pos_dr,wes_attr_utc,wes_attr_kind) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', state_rows)
    print(f'\n  wsf_exhaust_state   : {len(state_rows):,} rows', flush=True)
    print(f'  wsf_walk_checkpoint : {len(chk_rows):,} rows', flush=True)
    print(f'  wsf_walk_sequence   : {len(out):,} rows', flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
