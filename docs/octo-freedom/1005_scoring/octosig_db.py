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
SWING = float(SC.LG['swing'])
"""THE SWING pct FOR swing_detect, Joe 1006: *"I'm fine with it being 1.25"*. Was 0.70.

WHY HE MOVED IT, his words on 09-25 08:39:00: *"the swing_detect value is too low, that's why the
traded mae mfe data is so small - it tripped on a non-tradeable pullback at 08:40. the swing detect
needs to be large enough to carrying the trade to the signal at 09:32"*. Measured on that signal:

  0.70 / 0.90 / 1.00   stretch ends 08:40:05, 1.1 min,  MAE 0.022  MFE 0.176
  1.25 / 1.50 / 1.75   stretch ends 09:28:25, 49.4 min, MAE 1.039  MFE 1.150
  2.00 / 2.50 / 3.00   stretch ends 11:35:40, 176.7 min, MAE 1.039 MFE 5.808

The knee sits between 1.00 and 1.25 and it is SHARP - nothing lands in between. 1.25 is the first
value that carries past the 08:40 pullback.

IT IS NOT MAE_BLOCK. That is a separate 0.70 and it has NOT moved."""
MAE_BLOCK = float(SC.LG['mae_block'])
# SEPTEMBER + OCTOBER ONLY. Joe 1005: *"reduce the report to the september and october dates"*.
# The five July/August days (07-23, 07-25, 08-06, 08-20, 08-30) are OUT - they were the non-adjacent
# OOS draw from when FIT/TEST was still in force, and Joe dropped FIT/TEST earlier today. 12 days.
DAYS = _os.environ.get('LG_DAYS', '2026-09-14,2026-09-17,2026-09-25,2026-09-26,2026-09-27,'
                       '2026-09-28,2026-09-29,2026-09-30,2026-10-01,2026-10-02,2026-10-03,'
                       '2026-10-04').split(',')
# Joe 1005 baked two mtd/branch-D knobs today. Both are in the key - a knob that moves rows and is
# not in the unique key lets an A/B overwrite itself.
KNOB_KEY = '%s|%s|flip-towards+norblock|stamp-resolved|routing-banked|lineage-ws1|mtdwalk-drguard' % (
    SC.LG_KEY, 'gcws30Mage')
"""THE KNOB KEY CARRIES THE CONFIG VERSION, NOT THE VALUES. Joe 1006 moved every lazy-g constant
into `lazy_g_config`; 20+ in_key knobs spelled into one string overflows os_knob_key VARCHAR(190) and
is unreadable in Excel. `lazy_g_config.v1` resolves to the exact knob set with one SELECT, cannot
drift from it, and changing any in_key knob forces a new version - so a new version IS a new key.

What stays spelled out is what is NOT in the config: the ws1mage-rev signal line, and the RULINGS
that changed the mech's shape rather than a number."""
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
    os_legal_succ    TINYINT      NULL,         -- REDEFINED 1006: 1 = the ws1 lineage strands no momentum
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
    os_lin_chain     VARCHAR(96)  NOT NULL,     -- Joe's lineage from ws1, hop <= 2 TF numbers
    os_lin_top       SMALLINT     NOT NULL,     -- the highest TF the lineage reached
    os_lin_len       TINYINT      NOT NULL,     -- how many TFs are in the chain, ws1 included
    os_lin_broke_at  SMALLINT     NOT NULL,     -- the TF it could not hop past
    os_lin_mt_hi     SMALLINT     NOT NULL,     -- highest mom-true TF in ws1..ws12, 0 = none
    os_lin_mt        VARCHAR(96)  NOT NULL,     -- every mom-true TF in ws1..ws12, the raw read
    os_r_ladder      VARCHAR(32)  NOT NULL,     -- ws1..ws12 banded: O = oob, x = 83..85, . = in-fence
    os_r_ws1         DECIMAL(12,4) NULL,        -- the anchor's own r
    os_r_oob_top     SMALLINT     NOT NULL,     -- highest TF with r oob, 0 = none
    os_r_between_n   TINYINT      NOT NULL,     -- how many sit in the 83..85 band
    os_casc_str      VARCHAR(160) NOT NULL,     -- the mage cascade ws1..ws12, as a string
    os_casc_mid_end  DECIMAL(12,4) NULL,        -- middle (ws3,ws4) minus ends (ws1,ws12)
    os_casc_fast     DECIMAL(12,4) NULL,        -- ws1 -> ws3, the fast half
    os_casc_slow     DECIMAL(12,4) NULL,        -- ws6 -> ws11, the slow half
    os_casc_spread   DECIMAL(12,4) NULL,        -- the ladder's max minus its min
    os_casc_argmin   SMALLINT     NOT NULL,     -- which TF is the ladder's minimum
    os_casc_argmax   SMALLINT     NOT NULL,     -- which TF is the ladder's maximum
    os_casc_monotone TINYINT      NOT NULL,     -- 1 = rises at every step up the ladder
    os_mtd_fence     DECIMAL(6,2) NOT NULL,     -- the oob fence the four Mages are tested against
    os_mtd_g5        DECIMAL(12,4) NULL,        -- g5Mage  at the anchor (TOL 0 bars)
    os_mtd_g5_ts     VARCHAR(8)   NOT NULL,     -- the bar that value came from
    os_mtd_g15       DECIMAL(12,4) NULL,        -- g15Mage at its extremum within TOL +-3 bars
    os_mtd_g15_ts    VARCHAR(8)   NOT NULL,
    os_mtd_g30       DECIMAL(12,4) NULL,        -- g30Mage at its extremum within TOL +-6 bars
    os_mtd_g30_ts    VARCHAR(8)   NOT NULL,
    os_mtd_ws1       DECIMAL(12,4) NULL,        -- ws1Mage at the anchor (TOL 0 bars)
    os_mtd_ws1_ts    VARCHAR(8)   NOT NULL,
    os_mtd_r1        TINYINT      NOT NULL,     -- 1 = all four oob -> mtd.r1
    os_mtd_net       DECIMAL(12,4) NULL,        -- ws1Mage - g15Mage, the cascade net
    os_mtd_towards   TINYINT      NOT NULL,     -- 1 = net faces dr -> mtd.r2 when r1 fails
    os_d_blk         VARCHAR(128) NOT NULL,     -- every TF whose r is oob at the anchor
    os_d_drop        VARCHAR(128) NOT NULL,     -- of those, dropped by the GAP_MAX 4 rule
    os_d_weak        SMALLINT     NOT NULL,     -- the keep member closest to the fence, 0 = none
    os_d_band_lo     DECIMAL(12,4) NULL,        -- the band the claim test reads
    os_d_band_hi     DECIMAL(12,4) NULL,
    os_d_fire        TINYINT      NOT NULL,     -- branch D's own verdict: 1 = fires, 0 = claimed/no block
    os_route         VARCHAR(16)  NOT NULL,     -- mtd.r1 | mtd.r2 | neither | no dr
    os_status        VARCHAR(16)  NOT NULL,     -- CONFLUENCE | BLOCKED | OPEN
    os_grade         VARCHAR(32)  NOT NULL,
    os_mtd_oob       VARCHAR(24)  NOT NULL,
    os_d_keep        VARCHAR(128) NOT NULL,
    os_d_claim       VARCHAR(128) NOT NULL,
    os_mage_net      DECIMAL(12,4) NULL,        -- ws12Mage - ws1Mage at the mtd extrema
    os_mae_pct       DECIMAL(10,4) NULL,        -- swing 1.25, swing-to-pivot, max(0,adverse), NO STOP
    os_mfe_pct       DECIMAL(10,4) NULL,
    os_mfe_over_mae  DECIMAL(12,4) NULL,
    os_hold_min      DECIMAL(10,2) NULL,
    os_walk_ts       VARCHAR(8)   NOT NULL,     -- the WALK's own fire bar, what report_leash_walk emits
    os_stamp_src     VARCHAR(16)  NOT NULL,     -- walk | fwd-extrema : which bar os_ts was taken from
    os_g5ex_ts       VARCHAR(8)   NOT NULL,     -- the mtd step-1 g5Mage extrema bar: where branch D is READ
    os_g5ex_src      VARCHAR(10)  NOT NULL,     -- lookback | fwd  (fwd lands AFTER the signal)
    os_g5ex_lag_min  DECIMAL(10,2) NOT NULL,    -- extrema bar minus the signal bar, minutes. - = before
    os_flip          TINYINT      NOT NULL,     -- 1 = with-trend (net TOWARDS dr) = the pyramid signal
    os_trade_side    VARCHAR(5)   NOT NULL,     -- the side ACTUALLY taken after the flip rule
    os_mae_traded    DECIMAL(10,4) NULL,        -- MAE on the side actually taken
    os_mfe_traded    DECIMAL(10,4) NULL,        -- MFE on the side actually taken
    os_mo_traded     DECIMAL(12,4) NULL,        -- MFE/MAE on the side actually taken
    os_verdict       VARCHAR(8)   NOT NULL,     -- BLOCK if os_mae_traded > 0.70 else FIRE; UNSCORED if no pivot
    -- `os_walk_ts` IS IN THE KEY. Joe 1006 ruled os_ts = the fwd-g5extrema when the lookback found
    -- none, which can collapse TWO walk fires onto ONE anchor: measured, 1 collision in 397 -
    -- 09-29 23:46:05 and 23:46:40 both forward-walk to 23:47:25. Keying on the walk bar as well
    -- keeps BOTH rows rather than dropping one. Whether they are one event or two is Joe's ruling.
    UNIQUE KEY uq_os (os_knob_key, os_day, os_bar_ms, os_walk_ts),
    INDEX (os_day), INDEX (os_status), INDEX (os_verdict), INDEX (os_riding))'''))

# the mtd-oob string, VERBATIM from score39.py:255 - the only line of rendering carried across,
# and it is a format not a mechanic. '4/4' when all four mtd Mages are oob, else 'n/4 (the misses)'.
MTD_OOB = lambda m: ('4/4' if m.get('noob') == 4
                     else '%d/4 (%s)' % (m.get('noob', 0), ','.join(m.get('miss', []))))


have = {r['c'] for r in db.execute('''SELECT COLUMN_NAME c FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s''', (TABLE,), fetch=True)}
for col, ddl in ((('os_mtd_fence'),   'DECIMAL(6,2) NOT NULL DEFAULT 0 AFTER os_g5ex_lag_min'),
                 ('os_mtd_g5',      'DECIMAL(12,4) NULL AFTER os_mtd_fence'),
                 ('os_mtd_g5_ts',   "VARCHAR(8) NOT NULL DEFAULT '' AFTER os_mtd_g5"),
                 ('os_mtd_g15',     'DECIMAL(12,4) NULL AFTER os_mtd_g5_ts'),
                 ('os_mtd_g15_ts',  "VARCHAR(8) NOT NULL DEFAULT '' AFTER os_mtd_g15"),
                 ('os_mtd_g30',     'DECIMAL(12,4) NULL AFTER os_mtd_g15_ts'),
                 ('os_mtd_g30_ts',  "VARCHAR(8) NOT NULL DEFAULT '' AFTER os_mtd_g30"),
                 ('os_mtd_ws1',     'DECIMAL(12,4) NULL AFTER os_mtd_g30_ts'),
                 ('os_mtd_ws1_ts',  "VARCHAR(8) NOT NULL DEFAULT '' AFTER os_mtd_ws1"),
                 ('os_mtd_r1',      'TINYINT NOT NULL DEFAULT 0 AFTER os_mtd_ws1_ts'),
                 ('os_mtd_net',     'DECIMAL(12,4) NULL AFTER os_mtd_r1'),
                 ('os_mtd_towards', 'TINYINT NOT NULL DEFAULT 0 AFTER os_mtd_net'),
                 ('os_d_blk',       "VARCHAR(128) NOT NULL DEFAULT '' AFTER os_mtd_towards"),
                 ('os_d_drop',      "VARCHAR(128) NOT NULL DEFAULT '' AFTER os_d_blk"),
                 ('os_d_weak',      'SMALLINT NOT NULL DEFAULT 0 AFTER os_d_drop'),
                 ('os_d_band_lo',   'DECIMAL(12,4) NULL AFTER os_d_weak'),
                 ('os_d_band_hi',   'DECIMAL(12,4) NULL AFTER os_d_band_lo'),
                 ('os_d_fire',      'TINYINT NOT NULL DEFAULT 0 AFTER os_d_band_hi'),
                 ('os_walk_ts',    "VARCHAR(8) NOT NULL DEFAULT '' AFTER os_hold_min"),
                 ('os_stamp_src',  "VARCHAR(16) NOT NULL DEFAULT '' AFTER os_walk_ts"),
                 ('os_g5ex_ts',     "VARCHAR(8) NOT NULL DEFAULT '' AFTER os_stamp_src"),
                 ('os_g5ex_src',    "VARCHAR(10) NOT NULL DEFAULT '' AFTER os_g5ex_ts"),
                 ('os_g5ex_lag_min','DECIMAL(10,2) NOT NULL DEFAULT 0 AFTER os_g5ex_src'),
                 ('os_flip',       'TINYINT NOT NULL DEFAULT 0 AFTER os_g5ex_lag_min'),
                 ('os_trade_side', "VARCHAR(5) NOT NULL DEFAULT '' AFTER os_flip"),
                 ('os_mae_traded', 'DECIMAL(10,4) NULL AFTER os_trade_side'),
                 ('os_mfe_traded', 'DECIMAL(10,4) NULL AFTER os_mae_traded'),
                 ('os_mo_traded',  'DECIMAL(12,4) NULL AFTER os_mfe_traded'),
                 ('os_lin_chain',   "VARCHAR(96) NOT NULL DEFAULT '' AFTER os_verdict"),
                 ('os_lin_top',     'SMALLINT NOT NULL DEFAULT 0 AFTER os_lin_chain'),
                 ('os_lin_len',     'TINYINT NOT NULL DEFAULT 0 AFTER os_lin_top'),
                 ('os_lin_broke_at','SMALLINT NOT NULL DEFAULT 0 AFTER os_lin_len'),
                 ('os_lin_mt_hi',   'SMALLINT NOT NULL DEFAULT 0 AFTER os_lin_broke_at'),
                 ('os_lin_mt',      "VARCHAR(96) NOT NULL DEFAULT '' AFTER os_lin_mt_hi"),
                 ('os_r_ladder',    "VARCHAR(32) NOT NULL DEFAULT '' AFTER os_lin_mt"),
                 ('os_r_ws1',       'DECIMAL(12,4) NULL AFTER os_r_ladder'),
                 ('os_r_oob_top',   'SMALLINT NOT NULL DEFAULT 0 AFTER os_r_ws1'),
                 ('os_r_between_n', 'TINYINT NOT NULL DEFAULT 0 AFTER os_r_oob_top'),
                 ('os_casc_str',    "VARCHAR(160) NOT NULL DEFAULT '' AFTER os_r_between_n"),
                 ('os_casc_mid_end','DECIMAL(12,4) NULL AFTER os_casc_str'),
                 ('os_casc_fast',   'DECIMAL(12,4) NULL AFTER os_casc_mid_end'),
                 ('os_casc_slow',   'DECIMAL(12,4) NULL AFTER os_casc_fast'),
                 ('os_casc_spread', 'DECIMAL(12,4) NULL AFTER os_casc_slow'),
                 ('os_casc_argmin', 'SMALLINT NOT NULL DEFAULT 0 AFTER os_casc_spread'),
                 ('os_casc_argmax', 'SMALLINT NOT NULL DEFAULT 0 AFTER os_casc_argmin'),
                 ('os_casc_monotone','TINYINT NOT NULL DEFAULT 0 AFTER os_casc_argmax')):
    if col not in have:
        db.execute('ALTER TABLE %s ADD COLUMN %s %s' % (TABLE, col, ddl))
        print('# ALTER: added %s' % col, flush=True)


R_OOB = float(SC.LG['oob_hi']); R_EXF = 100.0 - float(SC.LG['momo_fence_r'])
"""THE TWO r FENCES. oob is `oob_hi`/`oob_lo` 85/15; the ex-fence is `momo_fence_r` 17, i.e. 83/17
(`wsf_dtf_v3_spec.md:83`, Joe 0820: *"create a new fence: momo-fence-r 100-{knob:17}"*). The band
BETWEEN them is what Joe 1006 read at 11:28:15: *"ws9 oob, ws10 is between ex-fence and oob, and
ws11 and ws12 are infence. this is a perfect picture of waning momentum"*."""

LIN_HOP = int(SC.LG['lin_hop'])
"""THE LINEAGE HOP, Joe 1006: *"for the lineage to qualify legal, it needs to be measured from ws1
and jump no more than 2 higher TFs to find the next TF with momentum"*, and on how to count it:
*"TF numbers. eg, ws1 can only look to ws2 and ws3 for a baton pass"*.

UPWARD ONLY, NEVER BACKWARDS. Joe 1006: *"it's important that the lineage walks TFs upward, never
backwards"*. The candidate set for a rider on ws{t} is exactly {ws{t+1}, ws{t+2}} - every lower TF is
out of the walk for good, including ones still sitting oob. Measured on 09-25's dr +1 leg: at 11:15
ws7 (r 90.91) and ws8 (r 87.91) are both oob behind the rider ws9 and neither is a candidate.

MOMENTUM IS A STATE, AND THERE ARE TWO OF THEM. Joe 1006:
  per line      - *"an `r` line either has it or it doesn't, based on the established momentum
                  machine's mechs"* -> mom-true, momo_g_why state in ('momo', 'curl').
  per collective- *"momentum is held by an `r` line as the rider of momentum, and collective momentum
                  is lost when the {riderTF +2} TFs have not proven strong enough to exit the fence
                  at the moment when riderTF has stalled"*.
The r band is NOT the momentum test - it is the fence-exit proof. oob = exited, 83..85 = might exit,
in-fence = too weak."""

LIN_TF = list(range(int(SC.LG['band_lo']), int(SC.LG['band_hi']) + 1))
LIN_ANCHOR = int(SC.LG['lin_anchor'])
"""ws1r IS THE ANCHOR. Joe 1006: *"I know the spec doesn't include ws1r at the moment, but this
example shows me that we need it as an anchor"*. baton.py's TFS is range(3, 24) - ws1 and ws2 are
NOT in it, so the lineage Joe describes CANNOT be expressed by the baton chain at all.

AND IT IS A DIFFERENT MECHANIC FROM THE BATON, though Joe 1006 called the difference subtle:
*"the lineage check and baton pass is time based, the data to measure at the signal is a snapshot of
that evolving time"*. The baton chains THROUGH TIME - a rider holds until it stalls, successor =
max(available). This chains UP THE LADDER AT ONE BAR - from ws1, hop <= 2, find the next TF with
momentum, repeat. Both are kept; neither replaces the other."""


def r_band(v, d):
    """THE THREE-BAND READ, on the dr side. -> 'O' oob | 'x' between the fences | '.' in-fence.

    Joe 1006 at 11:28:15: *"ws9 oob, ws10 is between ex-fence and oob, and ws11 and ws12 are
    infence. this is a perfect picture of waning momentum: 10 is signalling that it might be able to
    reach oob, and 11 and 12 are too weak AT THAT moment."*

    dr +1 reads the HIGH side (oob >= 85, between 83..85), dr -1 the LOW side (oob <= 15, between
    15..17). The fences are score39's own HI/LO and momo_fence_r's mirror of them.
    """
    if v is None or not np.isfinite(v): return '?'
    if d > 0:
        return 'O' if v >= R_OOB else ('x' if v >= R_EXF else '.')
    return 'O' if v <= (100.0 - R_OOB) else ('x' if v <= (100.0 - R_EXF) else '.')


def lineage(mt_at, lo=LIN_ANCHOR, hi_tf=12):
    """Joe's lineage: start at ws`lo`, hop at most LIN_HOP TF NUMBERS to the next TF WITH MOMENTUM,
    repeat. -> (chain, broke_at). `mt_at(t)` is True when ws{t} is mom-true.

    MOM-TRUE IS INHERITED, NOT CHOSEN: momo_g_why's state in ('momo','curl'). `sideways` counts as
    NOT mom-true, which is the existing definition everywhere in this project - Joe has not ruled on
    whether a sideways line may carry a lineage hop.
    """
    cur = lo
    chain = [cur]
    while True:
        nxt = next((t for t in range(cur + 1, min(cur + LIN_HOP, hi_tf) + 1) if mt_at(t)), None)
        if nxt is None:
            return chain, cur
        chain.append(nxt); cur = nxt


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
        'os_walk_ts,os_stamp_src,os_g5ex_ts,os_g5ex_src,os_g5ex_lag_min,'
        'os_mtd_fence,os_mtd_g5,os_mtd_g5_ts,os_mtd_g15,os_mtd_g15_ts,os_mtd_g30,os_mtd_g30_ts,'
        'os_mtd_ws1,os_mtd_ws1_ts,os_mtd_r1,os_mtd_net,os_mtd_towards,'
        'os_d_blk,os_d_drop,os_d_weak,os_d_band_lo,os_d_band_hi,os_d_fire,'
        'os_flip,os_trade_side,os_mae_traded,os_mfe_traded,os_mo_traded,os_verdict,'
        'os_lin_chain,os_lin_top,os_lin_len,os_lin_broke_at,os_lin_mt_hi,os_lin_mt,'
        'os_r_ladder,os_r_ws1,os_r_oob_top,os_r_between_n,'
        'os_casc_str,os_casc_mid_end,os_casc_fast,os_casc_slow,os_casc_spread,'
        'os_casc_argmin,os_casc_argmax,os_casc_monotone')
NCOL = len(COLS.split(','))
db.execute(Q("ALTER TABLE __TBL__ MODIFY os_stamp_src VARCHAR(16) NOT NULL DEFAULT ''"))
_ix = {r['Key_name'] + '/' + str(r['Seq_in_index']) + '/' + r['Column_name']
       for r in db.execute(Q('SHOW INDEX FROM __TBL__'), fetch=True)}
if 'uq_os/4/os_walk_ts' not in _ix:
    db.execute(Q('ALTER TABLE __TBL__ DROP INDEX uq_os, '
                 'ADD UNIQUE KEY uq_os (os_knob_key, os_day, os_bar_ms, os_walk_ts)'))
    print('# ALTER: uq_os now includes os_walk_ts', flush=True)
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
        hop = None
        if cur is not None and cur > 0:
            hop = int(chains[cur][1] - chains[cur - 1][1])
        if prev_bar is None:
            ns = '—'
        else:
            cnt = {}
            for x, t in C.STALL_EV:
                if prev_bar < x <= j: cnt[t] = cnt.get(t, 0) + 1
            ns = ', '.join('ws%d%s' % (t, '' if cnt[t] == 1 else ' x%d' % cnt[t])
                           for t in sorted(cnt)) or '—'
        r = SC.classify(k, sig)
        # THE STAMPED BAR. Joe 1006: *"to make as whole, I vote that os_ts represents the forward
        # g5extrema if there is no lookback"*. mtd reads the four Mages at `base = ex` (score39:98)
        # and branch D at `m['ex']` (:256), so on a `fwd` row the ROUTING uses bars 0.58..15.08 min
        # AFTER the walk's fire bar while MAE/MFE started AT that bar. One bar now serves both.
        # mtd appears 0 times in report_leash_walk.py and 0 times in optimus9/live/octo_freedom.py,
        # so this is a scoring-layer definition - nothing the live machine emits moves, and
        # `WALK FIRES FROM` keeps its meaning. It is preserved here as `os_walk_ts`.
        # COLUMN NAME `os_walk_ts` IS MINE, not Joe's - say the word and it changes.
        walk_k = k
        kx = r['m'].get('ex')
        if kx is not None and int(kx) > k:
            k = int(kx)                                     # fwd extrema becomes the stamped bar
            sig = BT.U(k)
        stamp_src = 'fwd-extrema' if k != walk_k else 'walk'
        # THE ROUTING'S WORKING, banked 1006 on Joe's word: *"recreate the routing calculations and
        # verdicts, and drop them in the table on a new key"*. EVERY routing value is read at the
        # ANCHOR - the lookback-g5extrema bar, or the fwd-g5extrema bar when the lookback found none.
        # `vbar` records which bar each Mage's value came from: g5 and ws1 are read AT the anchor
        # (TOL 0), g15 within +-3 bars and g30 within +-6 bars of it.
        _v = r['m'].get('v') or {}; _vb = r['m'].get('vbar') or {}
        MV = lambda n: (round(float(_v[n]), 4) if n in _v and _v[n] == _v[n] else None)
        MB = lambda n: (BT.U(_vb[n]) if n in _vb else '—')
        # ---- JOE'S LINEAGE, THE THREE-BAND r READ AND THE MAGE CASCADE, 1006.
        # ALL THREE ARE READ AT THE ROUTING ANCHOR `anc` - the same bar mtd and branch D read, i.e.
        # the lookback-g5extrema bar, or the fwd-g5extrema bar when the lookback found none. Joe
        # 1006: *"the data to measure at the signal is a snapshot of that evolving time"*.
        anc = int(r['m']['ex']) if r['m'].get('ex') is not None else k
        ja = anc - C.A                                      # the baton window's own index
        if 0 <= ja < C.N:
            mt_at = lambda t: bool(C.MT12[t][ja])
            lin, broke = lineage(mt_at)
            mt12 = [t for t in LIN_TF if mt_at(t)]
        else:                                               # anchor outside the warmed window
            lin, broke, mt12 = [LIN_ANCHOR], LIN_ANCHOR, []
        mt_hi = max(mt12) if mt12 else 0
        # os_legal_succ, REDEFINED. Joe 1006: *"os_legal_succ should be a confirmation of the lineage
        # - if its 1, we can act on os_stalled_now and os_new_stalls"*. The ws1-anchored walk can
        # only make legal hops, so the question it answers is whether anything was STRANDED: 1 = the
        # chain reached the highest mom-true TF on the ladder, 0 = momentum sits above a gap wider
        # than LIN_HOP and the lineage could not carry to it. NULL = no mom-true TF at all in
        # ws1..ws12, so there is no lineage to confirm.
        # THE DEFINITION IS MINE, read off Joe's sentence - the raw parts (os_lin_chain,
        # os_lin_top, os_lin_broke_at, os_lin_mt, os_lin_mt_hi) are all banked, so it can be
        # redefined against the table without another rebuild.
        lsucc = None if not mt12 else (1 if lin[-1] == mt_hi else 0)
        _r = {t: (float(SC.Rl[t][anc]) if np.isfinite(SC.Rl[t][anc]) else None) for t in LIN_TF}
        ladder = ''.join(r_band(_r[t], d) for t in LIN_TF)
        oobs = [t for t in LIN_TF if r_band(_r[t], d) == 'O']
        _mg = {t: (float(SC.Mg[t][anc]) if np.isfinite(SC.Mg[t][anc]) else None) for t in LIN_TF}
        fin = [t for t in LIN_TF if _mg[t] is not None]
        casc = ','.join(('%.1f' % _mg[t]) if _mg[t] is not None else '-' for t in LIN_TF)
        MID, END = (3, 4), (1, 12)                          # the matryoshka read, 1006_g5extrema_sweep.md
        _av = lambda tt: (sum(_mg[t] for t in tt) / len(tt)
                          if all(_mg[t] is not None for t in tt) else None)
        _mid, _end = _av(MID), _av(END)
        mid_end = (_mid - _end) if (_mid is not None and _end is not None) else None
        _sub = lambda hi, lo: ((_mg[hi] - _mg[lo]) if (_mg[hi] is not None and _mg[lo] is not None)
                               else None)
        f, a, xb = SC.score(k, d, H, L)                     # the dr-bias side, kept as a reference
        mo = (f / a) if (f is not None and a and a > 0) else None
        D_ = r.get('D') or {}
        # THE SIDE ACTUALLY TRADED. Joe 1006, from the table: *"979 (os_pk) and more are `CONFLUENCE
        # with-trend` which is our agreed pyramid signal. the os_verdict is BLOCK, probably because
        # the MAE and MFE weren't swapped to honour `with-trend`"*. He was right - every row was
        # scored at the dr-bias side, so a flip row carried its MFE in the MAE column. 979 went
        # MAE 2.1076 / MFE 0.0368 as banked and MAE 0.0368 / MFE 2.1076 on the side it would trade.
        # MAE/MFE are RESCORED, not swapped: the stretch runs to the next favourable PIVOT for that side.
        # `no r block` JOINS THE FLIP, Joe 1006. branchD:162 returns why='no r block' when no line
        # in ws1..ws12 is oob at the g5extrema - there is no wall, so there is no grade and net is
        # None, which is why these rows were never flipped and were scored on the dr-bias side.
        # MEASURED over 46 rows / 41 g5extrema bars / 12 days, at swing 1.25:
        #     counter-dr side   median MAE 0.4007  MFE 1.3893   MFE>MAE 36 of 46   MAE>0.70 14
        #     dr-bias side      median MAE 1.0812  MFE 0.7585   MFE>MAE 23 of 45   MAE>0.70 29
        # Joe's r-vs-Mage "mostly" threshold was tested and DROPPED: held out chronologically
        # (FIT 8 days / OOS 4), T 0..8 are the identical OOS population, T 9 is worse than no filter
        # at all, and the thresholds that score best are 5 and 9 rows. Joe 1006: *"the only path to
        # the truth is OOS"*, and the OOS said the side is the finding and "mostly" is not.
        # The r-vs-Mage statistic is NOT banked as a knob - nothing to back out.
        flip = bool((r['status'] == 'CONFLUENCE' and not D_.get('away', True))
                    or D_.get('why') == 'no r block')
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
                    BT.U(walk_k), stamp_src,
                    (BT.U(r['m']['ex']) if r['m'].get('ex') is not None else '—'),
                    str(r['m'].get('src', '-')),
                    round(float(r['m'].get('lag') or 0.0), 2),
                    (SC.HI if d > 0 else SC.LO),
                    MV('g5'), MB('g5'), MV('g15'), MB('g15'),
                    MV('g30'), MB('g30'), MV('ws1'), MB('ws1'),
                    1 if (r['m'].get('noob') == 4) else 0,
                    (round(float(r['m']['net']), 4) if r['m'].get('net') is not None else None),
                    1 if r['m'].get('towards') else 0,
                    ', '.join('ws%d' % t for t in sorted(D_.get('keep', []) + D_.get('drop', []))) or '—',
                    ', '.join('ws%d' % t for t in D_.get('drop', [])) or '—',
                    int(D_.get('weak') or 0),
                    (round(float(D_['band'][0]), 4) if D_.get('band') else None),
                    (round(float(D_['band'][1]), 4) if D_.get('band') else None),
                    1 if D_.get('fire') else 0,
                    1 if flip else 0, 'SHORT' if dt > 0 else 'LONG',
                    (round(at, 4) if at is not None else None),
                    (round(ft, 4) if ft is not None else None),
                    (round(mot, 4) if mot is not None else None),
                    verdict,
                    ' > '.join('ws%d' % t for t in lin), lin[-1], len(lin), broke,
                    mt_hi, ', '.join('ws%d' % t for t in mt12) or '—',
                    ladder,
                    (round(_r[1], 4) if _r[1] is not None else None),
                    (max(oobs) if oobs else 0), ladder.count('x'),
                    casc,
                    (round(mid_end, 4) if mid_end is not None else None),
                    (round(_sub(3, 1), 4) if _sub(3, 1) is not None else None),
                    (round(_sub(11, 6), 4) if _sub(11, 6) is not None else None),
                    (round(max(_mg[t] for t in fin) - min(_mg[t] for t in fin), 4) if fin else None),
                    (min(fin, key=lambda t: _mg[t]) if fin else 0),
                    (max(fin, key=lambda t: _mg[t]) if fin else 0),
                    (1 if len(fin) == len(LIN_TF)
                       and all(_mg[LIN_TF[i + 1]] > _mg[LIN_TF[i]] for i in range(len(LIN_TF) - 1))
                     else 0)))
        prev_bar = j
    assert not ins or len(ins[0]) == NCOL, 'tuple %d vs %d columns' % (len(ins[0]), NCOL)
    if ins:
        db.executemany(SQL, ins)
    total += len(ins)
    print('# %s INSERTED %d rows, %d in the table so far' % (day, len(ins), total), flush=True)

print('# DONE. %d rows in %s at knob_key %s' % (total, TABLE, KNOB_KEY))
db.disconnect()
