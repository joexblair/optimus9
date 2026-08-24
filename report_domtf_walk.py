"""report_domtf_walk — the domTF mechanic walked at EVERY bar, on its own. domTF outputs only.

Joe 0822: "ok, I guess walking the domTF mech will show the flips. am I wrong?" ... "I'm not
asking you to merge domTF with wsf. I'm asking only for domTF outputs" ... "show me the timestamps
where domTF BLOCKS and FREES, for 08-04. for each row, add the TF that created the BLOCKED, and
the cross that created the FREE".

WHAT IS DIFFERENT FROM build_ws_fin.py. That walk asks domTF for a verdict at 121 wsf9of12 signal
bars. Nothing else changes: same lines, same momentum knobs, same handover rule. Here the SEED is
the mechanic's own state instead of a wsf9of12 signal, so no wsf mechanic is read at all.

THE FIVE CONCRETIONS, decided here and stated on the report:
  D1  one row per DIRECTION, direction carried as a column. Every existing domTF row carries a
      side (wsf_side), so a bar can be blocked reading upward and free reading downward.
  D2  SUPERSEDED 0822 by Joe: "don't wait. the HANDOFF is the seam, everything after that is a
      fresh cycle with no baggage". The old rule made a BLOCKED event wait for the blocking list to
      go EMPTY before it could fire again, so after a handover the report read FREE while the lines
      were still carrying the move - 4 h 10 min of it on the downward read of 08-04, which Joe
      caught at 05:36:50. Now:
        BLOCKED   the blocking list goes from empty to non-empty. The STATE.
        HANDOFF   a turn ends - the watched line crossed or stalled. Joe 0822: "the report does not
                  show domTF handoff moments". A handoff does NOT free domTF; it ends one turn and
                  a fresh one starts on the very next bar, seeded from whatever is tagged THEN.
        FREE      the blocking list goes from non-empty to empty. The STATE.
      So a BLOCKED stretch can carry many HANDOFFs before it frees.
  D3  the nested-opposition override IS applied, from the cached opposite-direction masks. The
      RESCUE_REJECTED_CURL addition is NOT - it needs a fresh quadratic fit per line per bar.
      Excluding it can only REMOVE opposition, so the true answer has the same or FEWER blocked
      bars than this report.
  D4  FREE is the handover from that BLOCKED bar, run by domtf_handover_median exactly as
      build_ws_fin runs it. BOTH endings are reported - cross and stall. Joe 0814: "the reason for
      having stall, is to catch the moments that a x cross misses".
  D5  the watched line is the median of the tagged group, re-derived every bar, group uncut.

THE wsf-exhaust HALF, Joe 0822: "extend the script to add (chronologically) the wsf-exhaust
events that you have validated so far ... your script must derive the validated wsf-exhaust events
(ie the events are NOT hardcoded in the script), to ensure that the validated events show up in the
report as they become validated".

  D6  VALIDATED = wsf_exhaust_bar.wxb_found = 1, read from the database on every run. Nothing is
      hardcoded. A row that becomes found appears in the next run with no edit here.
  D7  the timestamp used is wxb_conf_utc, the CONFIRMED bar - the bar the hold completes on.
      wxb_raw_utc, the raw bar before the hold, is printed alongside it.
  D8  the exhaust knob set is PINNED (window + tolerance). One set exists today; pinning stops a
      second reconciliation at a different tolerance from silently merging into this report.
  D9  rows that are NOT validated are DECLARED in a footer, never silently dropped.

CROSS_NEEDS_R_INSIDE, Joe 0822: "this is a conflation of some sort - it defenitely wasn't my spec.
r can be anywhere on the board, ie not restricted". The extra condition - that the r line must be
back between 85 and 15 for a cross to count - is MINE, not Joe's. It is written into
jig.domtf_handover / domtf_handover_median ("the cross also requires the line to be back inside the
boundaries") and into domTF-finisher_spec M11. It is a knob here so both readings can be banked
side by side; False is Joe's ruling.

  NOT CHANGED: jig.domtf_handover_median still TAKES an `inside` mask, and build_ws_fin.py still
  passes the real one. The 121-signal walk in ws_fin_9of12 is still on the old rule. Removing the
  condition from the Jig would silently change that walk's output on its next run, and its unique
  key does not carry this flag - so that is Joe's call, not mine.

THE REPORT IS BANKED. Joe 0822: "dump this into a db table. everytime an update impacts the report,
the db table will be updated". Every run rewrites its own knob-keyed rows in `domtf_wsf_report`, so
a run at different knobs lands ALONGSIDE instead of overwriting. The knobs live in one string,
`dwr_knobs`, the same shape build_wsf_line_bar uses - MySQL caps a unique key at 16 parts.
"""
import os
import sys
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import LineStore, KLine, BBLine, override
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.analysis import ws_strat as WS
from optimus9.analysis.jig import stall_mask, domtf_handover_median
from optimus9.compute import momo_gated as MG
from optimus9.compute.momo_gated import momo_window

MG.MOMO_FIXED_SAMPLES = 21
from optimus9.compute import momo_core as MC
import build_momo_landed as B

DOMTF_TFS = list(range(13, 28))
X_SPEC = dict(length=5, mult=0.35, src='close')
STALL_N = 6
HANDOVER_XWOB = 4
NESTED_OPPOSITION_MIN = 3
CROSS_NEEDS_R_INSIDE = False   # KNOB. Joe 0822: "r can be anywhere on the board, ie not restricted"
#                                True reinstates the boundary condition I had conflated in.
EXH_WIN_FROM = '2026-08-04 00:00:00'   # wsf_exhaust_bar knob set. D8 - pinned, not defaulted
EXH_TOL_MIN = 7                        # the +/- minutes Joe's estimates were matched at
START = dt.datetime(2026, 8, 4, 0, 0, tzinfo=timezone.utc)
END = dt.datetime(2026, 8, 5, 0, 0, tzinfo=timezone.utc)
LINES = ([f'{g}{s}' for g in ('gcws15', 'gcws30') for s in ('b', 'm', 'Mage', 'r')]
         + [f'ws1{s}' for s in ('b', 'm', 'Mage', 'r')])

DDL = '''CREATE TABLE IF NOT EXISTS domtf_wsf_report (
    dwr_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    dwr_knobs   VARCHAR(160) NOT NULL,  -- every knob that changes a row, in one deterministic string.
    --   MySQL caps a unique key at 16 parts, so the knobs are packed the way wflb_knobs is.
    dwr_seq     INT NOT NULL,           -- position in the report, 1-based. Same bar keeps its order
    dwr_utc     DATETIME NOT NULL,      -- the bar
    dwr_read    VARCHAR(8) NOT NULL,    -- upward | downward
    dwr_event   VARCHAR(16) NOT NULL,   -- BLOCKED | HANDOFF | FREE | wsf-exhaust
    dwr_what    VARCHAR(255) NOT NULL,  -- what created it, exactly as the report prints it
    UNIQUE KEY uq_dwr (dwr_knobs, dwr_seq),
    KEY k_utc (dwr_utc), KEY k_event (dwr_event))'''

DWR_COLS = ['dwr_knobs', 'dwr_seq', 'dwr_utc', 'dwr_read', 'dwr_event', 'dwr_what']


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    s = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l, hi_boundary h, '
                   'lo_boundary lo FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
    HI, LO = float(s['h']), float(s['lo'])
    ls = LineStore(db)
    ovr = {n: (*ls.resolve(n), ls.value_mode(n)) for n in set(LINES + list(WS.LINES))}
    for tf in DOMTF_TFS:
        ovr[f'r{tf}'] = override(tf * 60, KLine(**B.R_SPEC), 'emerging')
        ovr[f'x{tf}'] = override(tf * 60, BBLine(**X_SPEC), 'emerging')
    J = cache_jig_perline(END_MS, HOURS, WARMUP, ovr,
                          pxs_cfg={'src': s['s'], 'len': s['l']}, rebuild=False)
    ts = np.asarray(J.ts); W = J.W
    R = {tf: np.asarray(W.line(f'r{tf}'), float) for tf in DOMTF_TFS}
    Xl = {tf: np.asarray(W.line(f'x{tf}'), float) for tf in DOMTF_TFS}

    # THE HOLD comes from the Jig, not a local run counter. Joe 0822: "if you've handrolled
    # anything in the script: use the Jig to produce consistent results". Jig.cross_wob is the
    # wobble-debounced crossover - `n` consecutive bars on the crossed side, one bar back resets it.
    # direction -1 asks "x below its r line", which by Joe's rule is the UPWARD read; +1 is downward.
    CW = J.causal.cross_wob
    CROSS = {+1: {tf: CW(Xl[tf], R[tf], -1, HANDOVER_XWOB) for tf in DOMTF_TFS},
             -1: {tf: CW(Xl[tf], R[tf], +1, HANDOVER_XWOB) for tf in DOMTF_TFS}}
    # Joe 0822: the cross does NOT require the r line to be back between the fences. All-True mask
    # = the condition is absent. The Jig seam is unchanged; only what is handed to it changes.
    INSIDE = ({tf: (R[tf] > LO) & (R[tf] < HI) for tf in DOMTF_TFS} if CROSS_NEEDS_R_INSIDE
              else {tf: np.ones(len(R[tf]), bool) for tf in DOMTF_TFS})

    i0 = int(np.searchsorted(ts, int(START.timestamp() * 1000)))
    i1 = int(np.searchsorted(ts, int(END.timestamp() * 1000)))
    LAT = {}
    for tf in DOMTF_TFS:
        with momo_window(B.K_WINDOW * tf):
            LAT[tf] = (int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES))
    STALL = {dr: {tf: stall_mask(R[tf], dr, STALL_N, *LAT[tf]) for tf in DOMTF_TFS}
             for dr in (+1, -1)}

    TAGDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'optimus9', 'orchestration', '.ws_cache', 'tagged')
    TAG = {+1: {}, -1: {}}
    for dr, c in ((+1, 'u'), (-1, 'd')):
        for tf in DOMTF_TFS:
            f = os.path.join(TAGDIR, f'tag_{tf}_{c}_{B.K_WINDOW}_{MG.MOMO_FIXED_SAMPLES}_'
                                     f'{i0}_{i1}.npy')
            if not os.path.exists(f):
                print(f'  MISSING cached mask {f}', flush=True); return 1
            TAG[dr][tf] = np.load(f)

    u = lambda i: dt.datetime.fromtimestamp(int(ts[i]) / 1000, timezone.utc).strftime('%H:%M:%S')
    print(f'  window {START:%Y-%m-%d %H:%M} -> {END:%Y-%m-%d %H:%M}   bars {i1 - i0 + 1:,}   '
          f'fences {HI:.0f}/{LO:.0f}   lines ws13r to ws27r', flush=True)

    FLIPS = []
    for dr, name in ((+1, 'upward'), (-1, 'downward')):
        # the blocking set at every bar, with the nested-opposition override applied
        blk = np.zeros(i1 + 1, bool)
        who = {}
        for i in range(i0, i1 + 1):
            b = [tf for tf in DOMTF_TFS if TAG[dr][tf][i]]
            if b:
                opp = [tf for tf in DOMTF_TFS if TAG[-dr][tf][i] and tf < max(b)]
                if len(opp) >= NESTED_OPPOSITION_MIN:
                    b = []
            blk[i] = bool(b)
            who[i] = b
        # THE STATE MACHINE. Joe 0822: "the HANDOFF is the seam, everything after that is a fresh
        # cycle with no baggage". A handoff ends a turn and the next turn seeds on the NEXT bar
        # from whatever is tagged there - it does not free domTF and it carries no group forward.
        ev = []                                   # (bar, kind, what)
        stall_fn = lambda tf, i: bool(STALL[dr][tf][i])
        i = i0
        blocked = bool(blk[i0])
        if blocked:
            ev.append((i0, 'BLOCKED',
                       ','.join(f'ws{t}r' for t in who[i0]) + ' (window open)'))
        seed = i0 if blocked else None
        while i <= i1:
            if not blocked:
                nb = next((j for j in range(i + 1, i1 + 1) if blk[j]), None)
                if nb is None:
                    break
                ev.append((nb, 'BLOCKED', ','.join(f'ws{t}r' for t in who[nb])))
                blocked, seed, i = True, nb, nb
                continue
            # a turn runs from `seed`. It ends at its handoff, OR is abandoned if the blocking
            # list empties first - "all domTF activity stops" when nothing carries the move.
            ho_i, ho_tf, ho_how, _j, _l = domtf_handover_median(
                TAG[dr], who[seed], CROSS[dr], INSIDE, stall_fn, seed, i1)
            gone = next((j for j in range(seed + 1, i1 + 1) if not blk[j]), None)
            if ho_i and (gone is None or ho_i <= gone):
                ev.append((ho_i, 'HANDOFF',
                           (f'ws{ho_tf}x crossed ws{ho_tf}r' if ho_how == 'cross'
                            else f'ws{ho_tf}r stalled')))
                nxt = ho_i + 1
                if nxt > i1:
                    break
                if blk[nxt]:                       # fresh cycle, seeded from THIS bar
                    seed, i = nxt, nxt
                else:
                    ev.append((nxt, 'FREE', 'no line is carrying the move'))
                    blocked, seed, i = False, None, nxt
                continue
            if gone is not None:
                ev.append((gone, 'FREE', 'no line is carrying the move'))
                blocked, seed, i = False, None, gone
                continue
            ev.append((i1, 'HANDOFF', 'no handoff before the window ends'))
            break

        nb_ = sum(1 for e in ev if e[1] == 'BLOCKED')
        nh_ = sum(1 for e in ev if e[1] == 'HANDOFF')
        nf_ = sum(1 for e in ev if e[1] == 'FREE')
        print(f'\n\n  ======== read {name.upper()}   BLOCKED {nb_}   HANDOFF {nh_}   FREE {nf_}',
              flush=True)
        print(f"  {'time':<10}{'event':<10}{'what created it':<52}{'since previous':>15}", flush=True)
        prev = None
        for b, kind, what in ev:
            gap = '-' if prev is None else f'{(int(ts[b]) - int(ts[prev])) / 60000.0:.1f}m'
            print(f'  {u(b):<10}{kind:<10}{what:<52}{gap:>15}', flush=True)
            FLIPS.append((int(ts[b]), name, kind, what))
            prev = b
    # THE VALIDATED wsf-exhaust EVENTS. D6 - derived from the table, never hardcoded.
    exh = db.execute(
        'SELECT wxb_est, wxb_tf, wxb_dr, wxb_method, wxb_wm_tf, wxb_raw_utc, wxb_conf_utc, '
        '       wxb_offset_s, wxb_elif '
        'FROM wsf_exhaust_bar WHERE wxb_win_from=%s AND wxb_tol_min=%s AND wxb_found=1 '
        'ORDER BY wxb_conf_utc', (EXH_WIN_FROM, EXH_TOL_MIN), fetch=True)
    missing = db.execute(
        'SELECT wxb_est, wxb_tf, wxb_dr, wxb_method, wxb_wm_tf '
        'FROM wsf_exhaust_bar WHERE wxb_win_from=%s AND wxb_tol_min=%s AND wxb_found=0 '
        'ORDER BY wxb_est', (EXH_WIN_FROM, EXH_TOL_MIN), fetch=True)
    for e in exh:
        d = 'upward' if e['wxb_dr'] > 0 else 'downward'
        wm = f"ws{e['wxb_wm_tf']}Mage" if e['wxb_wm_tf'] else 'no weak-mage'
        elif_ = '  [your ELIF time]' if e['wxb_elif'] else ''
        what = (f"ws{e['wxb_tf']}r {e['wxb_method']}, weak-mage {wm}, "
                f"raw bar {e['wxb_raw_utc'].strftime('%H:%M:%S')}, "
                f"your estimate {e['wxb_est']} ({e['wxb_offset_s']:+d}s){elif_}")
        FLIPS.append((int(e['wxb_conf_utc'].replace(tzinfo=timezone.utc).timestamp() * 1000),
                      d, 'wsf-exhaust', what))

    # THE CHRONOLOGICAL TABLE. Joe 0822: "I need to see both the BLOCKED and FREE flips,
    # chronoligically in one table". Both directions merged, one row per flip.
    nd = sum(1 for f in FLIPS if f[2] != 'wsf-exhaust')
    print(f'\n\n  ======== domTF FLIPS + VALIDATED wsf-exhaust EVENTS, 08-04, BOTH DIRECTIONS, '
          f'CHRONOLOGICAL   ({nd} domTF flips + {len(exh)} exhaust events = {len(FLIPS)} rows)',
          flush=True)
    ORD = {'HANDOFF': 0, 'FREE': 1, 'BLOCKED': 2, 'wsf-exhaust': 3}   # order within one bar
    print(f"  {'time':<10}{'read':<11}{'event':<14}{'what created it'}", flush=True)
    ordered = sorted(FLIPS, key=lambda r: (r[0], ORD[r[2]]))
    for ms, name, kind, what in ordered:
        t = dt.datetime.fromtimestamp(ms / 1000, timezone.utc).strftime('%H:%M:%S')
        print(f'  {t:<10}{name:<11}{kind:<14}{what}', flush=True)

    # BANK IT. Joe 0822: "dump this into a db table. everytime an update impacts the report, the db
    # table will be updated". The run rewrites ONLY its own knob-keyed rows.
    knobs = (f'w{START:%m%d}_tf{DOMTF_TFS[0]}-{DOMTF_TFS[-1]}_sn{STALL_N}_hx{HANDOVER_XWOB}'
             f'_hi{HI:.0f}_lo{LO:.0f}_no{NESTED_OPPOSITION_MIN}'
             f'_cri{int(CROSS_NEEDS_R_INSIDE)}_extol{EXH_TOL_MIN}_seam1')
    # seam1 = Joe 0822's restart rule, "the HANDOFF is the seam ... a fresh cycle with no baggage".
    # In the knob string so the rows banked under the old wait-for-empty rule stay comparable.
    db.execute(DDL)
    had = db.execute('SELECT COUNT(*) c FROM domtf_wsf_report WHERE dwr_knobs=%s',
                     (knobs,), fetch=True)[0]['c']
    if had:
        db.execute('DELETE FROM domtf_wsf_report WHERE dwr_knobs=%s', (knobs,))
    banked = [(knobs, k + 1,
               dt.datetime.fromtimestamp(ms / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
               name, kind, what[:255])
              for k, (ms, name, kind, what) in enumerate(ordered)]
    db.executemany(f'INSERT INTO domtf_wsf_report ({",".join(DWR_COLS)}) VALUES '
                   f'({",".join(["%s"] * len(DWR_COLS))})', banked)
    print(f'\n  domtf_wsf_report : {len(banked)} rows banked at knobs {knobs}'
          f'{f"   (replaced {had})" if had else ""}', flush=True)

    # D9. NOT VALIDATED - declared, never silently dropped.
    print(f'\n  wsf-exhaust estimates NOT YET VALIDATED, so absent from the table above: '
          f'{len(missing)}', flush=True)
    # the weak-mage column is only READ once a bar is located, so on a not-found row it is blank
    # because nothing was measured - NOT because the scan returned none. Say which.
    for m in missing:
        d = 'upward' if m['wxb_dr'] > 0 else 'downward'
        wm = (f"weak-mage ws{m['wxb_wm_tf']}Mage" if m['wxb_wm_tf']
              else 'weak-mage not read - no bar was located')
        print(f"    your estimate {m['wxb_est']:<8}read {d:<10}ws{m['wxb_tf']}r  "
              f"{m['wxb_method']:<12}{wm}", flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
