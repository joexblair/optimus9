"""THE octo-sig RULING TABLE. Joe 1005: *"drop the octo-signals into a db table. add the block/fire
(based on MAE/MFE) and any other data you think would help me to make ruling decisions ... the
momentum columns (recent stalled TFs, current rider) ... there were some adjustments I made to that
momentum report, please bake them in"*.

EVERY PRODUCER IS CALLED, NOTHING RE-IMPLEMENTED — the point of the exercise:
  baton.compute(start, end, octosig)   rig.DR per bar, mom-true, stalled, the baton chain, traj.
                                       Split out of module scope 1005, verified byte-identical
                                       against transfer/2026-09-25_baton_stall_octosig_fullday.txt
  score39.classify(k)                  mtd route + branch D -> BLOCKED / CONFLUENCE / OPEN + grade.
                                       Lifted out of score39's ROWS loop 1005, output unchanged
  score39.score(k, d, H, L)            swing_detect MAE / MFE, banked convention
  report_leash_walk                    the octo-sigs themselves, read from 1005_scoring/octosig/

JOE'S ADJUSTMENTS TO THE MOMENTUM REPORT, BAKED (each one sourced to the turn he made it):
  1004  "the report's rows must honour rig.DR ... we are simulating o9-live walks, therefore we must
        be completely aligned"            -> dr is PER-BAR rig.DR, never the walk frame
  1004  "move the `dr` column to the right of `traj`"   -> column order riding, traj, dr
  1004  "next to riding, add a traj (r's trajectory direction) column"
  1004  "remove the STOP column"                       -> no stop column, and MAE/MFE carry no stop
  1004  "add 2 momentum columns: of ws3r to ws23r: the highest mom-true TF, the lowest mom-true TF"
  1004  "mom-true is colloquial - you're hunting for the `momo` and `curl` state"  -> momo_g_why in
        ('momo','curl'), via baton.compute
  1004  "drop the casc-max-step column and remove g30,g15,g5 from the mage cascade"
  1004  "show me the baton and stalled data - that's what's most important"
  1004  "add a dr column"
  1005  "we're not introducing any changes to octo-freedom. drop the sig_conf ref"
  1005  b/Mage is "info-only for now"                  -> not a column
  Config carried from the banked report header: STALL_N 6 · ws3..ws23 · traj block 60 · min_bars 24

BLOCK / FIRE: MAE > 0.70 % -> BLOCK. Joe's delegated call, 1005: *"any signal which creates >0.7
MAE% (or maybe 0.8% - your call) should be blocked"*. `os_mae_pct`, `os_mfe_pct` and
`os_mfe_over_mae` are stored raw so the threshold can be moved in SQL without a rebuild.

THE LINEAGE COLUMNS, Joe 1005 agreed: `riding` and `traj` are carried WITH the facts that make them
judgeable, because the rider tag has no lineage rule yet (`baton.py` successor = highest available,
the outgoing rider's TF never consulted). `os_hop` is the signed TF distance from the outgoing rider
and `os_legal_succ` whether any candidate sat within +-3 of it at the seat bar. Joe's three open
rulings - hop window <=2 or <=3, the no-successor case, whether a downward pass counts - change
`riding` itself, so filter on these before trusting it.

CONTIGUITY IS NOT RULED. `os_stalled_now` carries the raw stalled STATE list; `os_stall_clusters`
and `os_stall_widest_gap` are the plain adjacent-TF reading. Joe's *"3 TFs stalled inside of a 4 TF
window"* is NOT computed - whether "4 TF window" means 4 slots or 4 steps is unresolved, and task
#60 is held on his word.

argv: none. env LG_TAPE_END (default 2026-10-05), LG_TABLE (default octosig_rulings), LG_DAYS.
"""
import os as _os, sys, io, contextlib, datetime as dt
import numpy as np
_HERE = _os.path.dirname(_os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, '/home/joe/thecodes')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    with contextlib.redirect_stderr(io.StringIO()):
        import baton as BT
        import score39 as SC
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

TABLE = _os.environ.get('LG_TABLE', 'octosig_rulings')
Q = lambda s: s.replace('__TBL__', TABLE)
SWING = 0.70
MAE_BLOCK = 0.70
# SEPTEMBER + OCTOBER ONLY. Joe 1005: *"reduce the report to the september and october dates"*.
# The five July/August days (07-23, 07-25, 08-06, 08-20, 08-30) are OUT - they were the non-adjacent
# OOS draw from when FIT/TEST was still in force, and Joe dropped FIT/TEST earlier today. 12 days.
DAYS = _os.environ.get('LG_DAYS', '2026-09-14,2026-09-17,2026-09-25,2026-09-26,2026-09-27,'
                       '2026-09-28,2026-09-29,2026-09-30,2026-10-01,2026-10-02,2026-10-03,'
                       '2026-10-04').split(',')
# Joe 1005 baked two mtd/branch-D knobs today. Both are in the key - a knob that moves rows and is
# not in the unique key lets an A/B overwrite itself.
KNOB_KEY = ('stall_n6|tf3-23|trajblk%d|minbars%d|swing%.2f|lookback_s%s|dwell%s|rev_wob%s|hold%s|%s'
            '|%.0f/%.0f|mtdwalk%d|claimhop%d|flip-towards'
            % (BT.AF_BLOCK, BT.TRAJ_MIN_BARS, SWING, SC.LOOKBACK_BARS * 5, 3, 2, 4, 'gcws30Mage',
               SC.HI, SC.LO, SC.MTD_WALK_BARS, SC.CLAIM_HOP))
H, L = SC.pivots(SWING)
print('# table %s | knob_key %s' % (TABLE, KNOB_KEY))
print('# MAE > %.2f%% -> BLOCK (Joe 1005, delegated). raw MAE/MFE stored.' % MAE_BLOCK)

db = DatabaseManager(**get_db_config()); db.connect()
db.execute(Q('''CREATE TABLE IF NOT EXISTS __TBL__ (
    os_pk            BIGINT AUTO_INCREMENT PRIMARY KEY,
    os_knob_key      VARCHAR(190) NOT NULL,     -- every knob that moves a row, in the unique key
    os_day           DATE         NOT NULL,
    os_ts            VARCHAR(8)   NOT NULL,     -- WALK FIRES FROM, HH:MM:SS
    os_bar_ms        BIGINT       NOT NULL,
    os_arm_ts        VARCHAR(8)   NOT NULL,
    os_dr            TINYINT      NOT NULL,     -- PER-BAR rig.DR at the signal bar (Joe 1004)
    os_side          VARCHAR(5)   NOT NULL,     -- dr +1 = SHORT
    os_riding        SMALLINT     NOT NULL,     -- the baton holder TF, 0 = no rider
    os_traj          VARCHAR(8)   NOT NULL,     -- towards | away | -
    os_hop           SMALLINT     NULL,         -- signed TF distance from the outgoing rider
    os_legal_succ    TINYINT      NULL,         -- 1 = a candidate sat within +-3 at the seat bar
    os_stalled_n     TINYINT      NOT NULL,     -- stalled STATE count
    os_stalled_of    TINYINT      NOT NULL,     -- 21 (ws3..ws23)
    os_momtrue_n     TINYINT      NOT NULL,     -- momo+curl count
    os_momtrue_hi_tf SMALLINT     NOT NULL,     -- highest momo+curl TF of ws3r..ws23r, 0 = none
    os_momtrue_lo_tf SMALLINT     NOT NULL,     -- lowest  momo+curl TF of ws3r..ws23r, 0 = none
    os_candidates    VARCHAR(255) NOT NULL,     -- mom-true AND not stalled
    os_stalled_now   VARCHAR(255) NOT NULL,     -- the stalled STATE list; read contiguity here
    os_stall_clusters TINYINT     NOT NULL,     -- adjacent-TF runs in os_stalled_now (plain reading)
    os_stall_widest_gap TINYINT   NOT NULL,     -- widest gap between stalled TFs
    os_new_stalls    VARCHAR(255) NOT NULL,     -- stall ONSETS since the PREVIOUS octo-sig row
    os_baton_ts      VARCHAR(8)   NOT NULL,     -- most recent pass at or before the bar
    os_stalled_ts    VARCHAR(8)   NOT NULL,     -- most recent onset at or before the bar
    os_pxs           DECIMAL(16,8) NOT NULL,
    os_route         VARCHAR(16)  NOT NULL,     -- mtd.r1 | mtd.r2 | neither | no dr
    os_status        VARCHAR(16)  NOT NULL,     -- CONFLUENCE | BLOCKED | OPEN
    os_grade         VARCHAR(32)  NOT NULL,
    os_mtd_oob       VARCHAR(24)  NOT NULL,
    os_d_keep        VARCHAR(128) NOT NULL,
    os_d_claim       VARCHAR(128) NOT NULL,
    os_mage_net      DECIMAL(12,4) NULL,        -- ws12Mage - ws1Mage at the mtd extrema
    os_mae_pct       DECIMAL(10,4) NULL,        -- swing 0.70, swing-to-pivot, max(0,adverse), NO STOP
    os_mfe_pct       DECIMAL(10,4) NULL,
    os_mfe_over_mae  DECIMAL(12,4) NULL,
    os_hold_min      DECIMAL(10,2) NULL,
    os_flip          TINYINT      NOT NULL,     -- 1 = with-trend (net TOWARDS dr) = the pyramid signal
    os_trade_side    VARCHAR(5)   NOT NULL,     -- the side ACTUALLY taken after the flip rule
    os_mae_traded    DECIMAL(10,4) NULL,        -- MAE on the side actually taken
    os_mfe_traded    DECIMAL(10,4) NULL,        -- MFE on the side actually taken
    os_mo_traded     DECIMAL(12,4) NULL,        -- MFE/MAE on the side actually taken
    os_verdict       VARCHAR(8)   NOT NULL,     -- BLOCK if os_mae_traded > 0.70 else FIRE; UNSCORED if no pivot
    UNIQUE KEY uq_os (os_knob_key, os_day, os_bar_ms),
    INDEX (os_day), INDEX (os_status), INDEX (os_verdict), INDEX (os_riding))'''))

# the mtd-oob string, VERBATIM from score39.py:255 - the only line of rendering carried across,
# and it is a format not a mechanic. '4/4' when all four mtd Mages are oob, else 'n/4 (the misses)'.
MTD_OOB = lambda m: ('4/4' if m.get('noob') == 4
                     else '%d/4 (%s)' % (m.get('noob', 0), ','.join(m.get('miss', []))))


have = {r['c'] for r in db.execute('''SELECT COLUMN_NAME c FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s''', (TABLE,), fetch=True)}
for col, ddl in (('os_flip',       'TINYINT NOT NULL DEFAULT 0 AFTER os_hold_min'),
                 ('os_trade_side', "VARCHAR(5) NOT NULL DEFAULT '' AFTER os_flip"),
                 ('os_mae_traded', 'DECIMAL(10,4) NULL AFTER os_trade_side'),
                 ('os_mfe_traded', 'DECIMAL(10,4) NULL AFTER os_mae_traded'),
                 ('os_mo_traded',  'DECIMAL(12,4) NULL AFTER os_mfe_traded')):
    if col not in have:
        db.execute('ALTER TABLE %s ADD COLUMN %s %s' % (TABLE, col, ddl))
        print('# ALTER: added %s' % col, flush=True)


def clusters(tfs):
    """adjacent-TF runs and the widest gap. The PLAIN reading - Joe's 3-in-4 rule is not ruled."""
    if not tfs: return (0, 0)
    n = 1; widest = 0
    for a, b in zip(tfs, tfs[1:]):
        g = b - a
        widest = max(widest, g)
        if g > 1: n += 1
    return (n, widest)

# INSERT PER DAY, not one batch at the end. Joe 1005: *"so that I can work on the rulings in the
# background"* - and the first build accumulated all 17 days in memory and inserted once at the very
# end, so the table read EMPTY for the whole run. The DELETE for this knob_key therefore happens
# ONCE here, before the first day, and each day commits as it completes.
db.execute(Q('DELETE FROM __TBL__ WHERE os_knob_key=%s'), (KNOB_KEY,))
COLS = ('os_knob_key,os_day,os_ts,os_bar_ms,os_arm_ts,os_dr,os_side,os_riding,os_traj,os_hop,'
        'os_legal_succ,os_stalled_n,os_stalled_of,os_momtrue_n,os_momtrue_hi_tf,os_momtrue_lo_tf,'
        'os_candidates,os_stalled_now,os_stall_clusters,os_stall_widest_gap,os_new_stalls,'
        'os_baton_ts,os_stalled_ts,os_pxs,os_route,os_status,os_grade,os_mtd_oob,os_d_keep,'
        'os_d_claim,os_mage_net,os_mae_pct,os_mfe_pct,os_mfe_over_mae,os_hold_min,'
        'os_flip,os_trade_side,os_mae_traded,os_mfe_traded,os_mo_traded,os_verdict')
NCOL = len(COLS.split(','))
SQL = Q('INSERT INTO __TBL__ (%s) VALUES (%s)' % (COLS, ','.join(['%s'] * NCOL)))
total = 0
for day in DAYS:
    sig_path = _os.path.join(_HERE, 'octosig', '%s.out' % day)
    if not _os.path.exists(sig_path):
        print('# %s SKIPPED - no octosig file' % day); continue
    ins = []
    C = BT.compute(day + ' 00:00:00', day + ' 23:59:55', sig_path, warn=False)
    # the chain, for the lineage facts: (nn, rider, start, end, why, candidates_at_pass)
    chains = sorted(C.CHAIN, key=lambda c: c[2])
    prev_bar = None
    for k, sig, _last, _bars, _wdr, arm in sorted(C.OS):
        j = k - C.A
        rd = int(C.RIDER[j])
        d = int(C.D[j])
        mt = [t for t in BT.TFS if C.MT[t][j]]
        st = [t for t in BT.TFS if C.ST[t][j]]
        nc, wg = clusters(st)
        cav = C.avail(j)
        # lineage: the chain whose reign covers j, and the one before it
        cur = next((i for i, c in enumerate(chains) if c[2] <= j <= c[3]), None)
        hop = lsucc = None
        if cur is not None and cur > 0:
            out_tf = chains[cur - 1][1]
            hop = int(chains[cur][1] - out_tf)
            lsucc = 1 if any(abs(x - out_tf) <= 3 for x in chains[cur - 1][5]) else 0
        if prev_bar is None:
            ns = '—'
        else:
            cnt = {}
            for x, t in C.STALL_EV:
                if prev_bar < x <= j: cnt[t] = cnt.get(t, 0) + 1
            ns = ', '.join('ws%d%s' % (t, '' if cnt[t] == 1 else ' x%d' % cnt[t])
                           for t in sorted(cnt)) or '—'
        r = SC.classify(k, sig)
        f, a, xb = SC.score(k, d, H, L)                     # the dr-bias side, kept as a reference
        mo = (f / a) if (f is not None and a and a > 0) else None
        D_ = r.get('D') or {}
        # THE SIDE ACTUALLY TRADED. Joe 1006, from the table: *"979 (os_pk) and more are `CONFLUENCE
        # with-trend` which is our agreed pyramid signal. the os_verdict is BLOCK, probably because
        # the MAE and MFE weren't swapped to honour `with-trend`"*. He was right - every row was
        # scored at the dr-bias side, so a flip row carried its MFE in the MAE column. 979 went
        # MAE 2.1076 / MFE 0.0368 as banked and MAE 0.0368 / MFE 2.1076 on the side it would trade.
        # MAE/MFE are RESCORED, not swapped: the exit is the next favourable pivot FOR THAT SIDE.
        flip = bool(r['status'] == 'CONFLUENCE' and not D_.get('away', True))
        dt = -d if flip else d
        ft, at, _xt = (f, a, xb) if not flip else SC.score(k, dt, H, L)
        mot = (ft / at) if (ft is not None and at and at > 0) else None
        verdict = 'UNSCORED' if at is None else ('BLOCK' if at > MAE_BLOCK else 'FIRE')
        ins.append((KNOB_KEY, day, sig, int(BT.ts[k]), arm, d, 'SHORT' if d > 0 else 'LONG',
                    rd, C.traj(rd, j), hop, lsucc,
                    len(st), len(BT.TFS), len(mt), max(mt) if mt else 0, min(mt) if mt else 0,
                    ', '.join('ws%d' % x for x in cav) or 'NONE',
                    ', '.join('ws%d' % t for t in st) or '—', nc, wg, ns,
                    C.last_baton(j), C.last_stall(j), float(BT.PX[k]),
                    r['m']['route'], r['status'], r['grade'], MTD_OOB(r['m']),
                    ', '.join('ws%d' % t for t in D_.get('keep', [])) or '—',
                    ', '.join('ws%d' % t for t in D_.get('claim', [])) or '—',
                    (float(D_['net']) if D_.get('net') is not None else None),
                    (round(a, 4) if a is not None else None),
                    (round(f, 4) if f is not None else None),
                    (round(mo, 4) if mo is not None else None),
                    (round((BT.ts[xb] - BT.ts[k]) / 60000.0, 2) if xb is not None else None),
                    1 if flip else 0, 'SHORT' if dt > 0 else 'LONG',
                    (round(at, 4) if at is not None else None),
                    (round(ft, 4) if ft is not None else None),
                    (round(mot, 4) if mot is not None else None),
                    verdict))
        prev_bar = j
    assert not ins or len(ins[0]) == NCOL, 'tuple %d vs %d columns' % (len(ins[0]), NCOL)
    if ins:
        db.executemany(SQL, ins)
    total += len(ins)
    print('# %s INSERTED %d rows, %d in the table so far' % (day, len(ins), total), flush=True)

print('# DONE. %d rows in %s at knob_key %s' % (total, TABLE, KNOB_KEY))
db.disconnect()
