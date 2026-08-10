"""build_rpl_jig — THE CAUSAL TEST JIG. Joe 0802.

WHY. Every number in this project comes from a vectorised pass, and that pass was caught peeking twice in
one session — the exit and the walk both read 240 s of future. Each correction moved real figures (return
sum +42.00 -> +22.34; the reverse-order anti-signal went from 0.00x to 0.85x and stopped being a finding).
Code review did not catch either. A bar-by-bar loop does, because a forward index cannot be written.

WHAT JOE SPECIFIED (0802, verbatim intent)
  "the jig is triggered every 5 seconds, reads pxs, and goes to work"
  "writes pxsmooth as a heartbeat to a db table (we'll only run this for 24 hours)"
  "at random intervals that are no smaller than 30 minutes, jig will delegate r-pred to exhv2, and write
   that event to jigs heartbeat table"     -> interval uniform 30-60 min (Joe 0802)
  "the jig does not derive bias, exhv2 does with its existing mechanisms"
  "I'm assuming you'll be looping exhv2 - it may as well be triggered from jig"   -> ONE process

THE TRIGGER CARRIES NOTHING.  No bias, no cur_tf.
  cur_tf  is never read by any exhv2 logic — it is a reporting passthrough (build_exhv2.py:407 / :426).
  bias    reaches only two lines, :308 and :310, and the four-case enumeration shows the working direction
          `ed` resolves to the s4Mage breach side in EVERY combination. So bias changes no decision; it
          feeds only the MFE-side flag `mf`. A synthetic trigger has no real bias, so faking one would fill
          that flag with noise dressed as data. exhv2 derives direction from the breach, as it already does,
          and `jg_mfe_side` is written NULL.
  The five rsd Mages are recorded at every tick under BOTH readings so the bias rule can be chosen from
  data later (Joe 0802: the combo needs a sweep, the reading needs a pine emit). NOTHING acts on them yet.

CAUSALITY, STRUCTURALLY
  Each tick rebuilds every line over a rolling window ENDING AT THE CURRENT BAR and reads index -1 or a
  slice that ends there. There is no array position after `now` for anything to read. Measured cost:
  12 line specs over 51,840 bars = 1.39 s, inside the 5 s tick.
  Detection can only ever be LATE, never early — the conservative direction.

STATE MACHINE, one per open trigger — exhv2's own chain
  WALK    first bar where s4Mage HAS BEEN OOB for WALK_DWELL_BARS (B.oob_qualified — the 0802 causal form)
  HOP     REWALK 2: while s22 reads momo at the walk bar, hop to the next qualified bar
  ANCHOR  s15x X s15m cross in the trade direction at/after the walk bar
  CONFIRM first gcs15x X gcs15m cross at/after the anchor  ->  THE SIGNAL
  EXIT    the next qualified bar after the signal
  The walk has NO terminator (spec §4). A trigger still open at the end of the run is written as open.

    python3 build_rpl_jig.py [--hours 24] [--trigger-now]
    touch .jig_trigger          # fire a delegate on the next tick, without restarting the loop
"""
import os, sys, json, time, random, datetime as dt

# ceiling 4 BEFORE importing build_exhv2: the jig never touches R.L0, and ceiling 120 would load a ~5.8 GB
# bundle into a 24 h process. momo() and oob_qualified() do not depend on TFS.
os.environ.setdefault('RPL_TF_CEILING', '4')
import numpy as np
import build_exhv2 as B
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline, kline, _Causal
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.compute.breaching_line import predict_breach
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

WIN_HOURS, WIN_WARMUP = 24, 24        # rolling window: 3 days. Covers a walk open for up to 24 h
TRIG_LO_MIN, TRIG_HI_MIN = 30, 60     # Joe 0802: "no smaller than 30 minutes" -> uniform 30-60
BAR_MS = 5000
# ON-DEMAND TRIGGER. Touch this file and the next tick fires a delegate, then deletes it. Added so a
# trigger can be sent without restarting the loop — a restart costs ~2 min of heartbeat (the L0 load)
# and breaks the run's continuity. The scheduled 30-60 min draw is unaffected and keeps running.
TRIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.jig_trigger')

LINES = {}
LINES.update(bbline('jM4', 4, length=37, mult=0.7, src='close'))            # s4Mage — the walk/exit producer
LINES.update(bbline('jx15', 15, length=4, mult=0.37, src='close'))          # s15x — the anchor pair
LINES.update(bbline('jm15', 15, length=6, mult=0.45, src='close'))          # s15m
LINES.update(bbline('jg15x', 0.25, length=5, mult=0.37, src='close'))       # gcs15x — the confirm pair, 15 s
LINES.update(bbline('jg15m', 0.25, length=6, mult=0.45, src='close'))       # gcs15m
LINES.update(kline('jr15', 15, k_len=10, rsi=4, stc=11, src='close'))       # s15r — momentum
LINES.update(kline('jr22', 22, k_len=10, rsi=4, stc=11, src='close'))       # s22r — momentum + the REWALK gate
# exhv2's STANDALONE r-prediction needs r, m and M on each of s4 / s15 / s22 (spec §2: "a direct
# predict_breach evaluation on those lines. It is not rp_matrix, not the ladder"). Joe 0802: without it
# the loop cannot tell that momentum is still strong, so the re-walk stops on `momo` reading flat instead
# of holding until r nears the boundary. Specs are exhv2's own LINE_SPEC / R_SPEC, not the RPL baseline.
LINES.update(kline('jr4', 4, k_len=7, rsi=6, stc=11, src='close'))          # s4r  — R_SPEC[4]
LINES.update(bbline('jm4', 4, length=6, mult=0.45, src='close'))            # s4m
LINES.update(bbline('jx4', 4, length=4, mult=0.37, src='close'))            # s4x  — for the local x/r cross
LINES.update(bbline('jM15', 15, length=37, mult=0.7, src='close'))          # s15M
LINES.update(bbline('jx22', 22, length=4, mult=0.37, src='close'))          # s22x
LINES.update(bbline('jm22', 22, length=6, mult=0.45, src='close'))          # s22m
LINES.update(bbline('jM22', 22, length=37, mult=0.7, src='close'))          # s22M
# s1r and s30r — Joe 0802 read these off his chart and the jig could not show them. Built with the
# rpl_config generic r spec via rpl_walk's own producer, matching the gcs5r precedent
# (rpl_walk.py: _mk('gcs5r', 5/60, LN['r'])). If the named LN['s30r'] spec is wanted instead it is one line.
LINES.update(R._mk('js1r', 1.0, R.LN['r']))                                 # s1r
LINES.update(R._mk('js30r', 0.5, R.LN['r']))                                # s30r
# THE SMALL-TF SETS — Joe 0802, his last note before signing off, verbatim intent:
#   "if you want to know if a line is going to reverse, take guidance from the smaller TFs (gcs5, gcs15,
#    s30, possibly s1). their lines will GATHER TO A BOUNDARY before they push away from it, and this
#    momentum feeds into the TFs above it ... you'll get to understand when they're committed (trending)
#    and when they're unsure (sideways)"
# So the full r/m/x set is needed at each small TF, not just the Mage — gathering is a property of the SET.
# Built with rpl_walk's own producer on the rpl_config generic specs, matching the gcs5r/gcs5m/gcs5x
# precedent at rpl_walk.py:84.
SMALL_TF = [('g5', 5.0 / 60), ('g15', 0.25), ('s30', 0.5), ('s1', 1.0)]
for _n, _t in SMALL_TF:
    for _k in ('r', 'm', 'x'):
        LINES.update(R._mk('j%s%s' % (_n, _k), _t, R.LN[_k]))
# HTF MAGES ABOVE s22 — Joe 0802, his last tip: "if your predictions don't pan out, start by looking at
# the HTFs (>22) - you might find something bigger cutting an opposing path". Banked so a FAILED call can
# be diagnosed against what the bigger timeframes were doing, rather than guessed at. Same bb 37|0.7 spec
# as every other Mage here.
#   NOT TF120: bb length 37 at a 2 h bar needs 37 x 2 h = 74 h of history and the rolling window is
#   24 + 2x24 = 72 h. It would bank NaN and look like data. Widening the window to reach it would push the
#   per-tick build past the 5 s budget, so s120 waits for a deliberate decision rather than a silent one.
HTF_MAGE = [('jH30', 30.0), ('jH45', 45.0), ('jH60', 60.0), ('jH90', 90.0)]
for _n, _t in HTF_MAGE:
    LINES.update(bbline(_n, _t, length=37, mult=0.7, src='close'))
RPRED_TF = {4: ('jr4', 'jm4', 'jM4', 'jx4'), 15: ('jr15', 'jm15', 'jM15', 'jx15'), 22: ('jr22', 'jm22', 'jM22', 'jx22')}
SLIP = 2.0                            # momo_ride_oob_slip — r-units of gap to the 15/85 boundary.
#                                       Joe 0802: the x-cross fire allowance and the r-pred release are the
#                                       SAME predicate seen from two sides, so one knob, not two.
MAGES = [('jMg5', 5.0 / 60), ('jMg15', 0.25), ('jMg30', 0.5), ('jMg1', 1.0), ('jMg2', 2.0)]
for _n, _t in MAGES:
    LINES.update(bbline(_n, _t, length=37, mult=0.7, src='close'))          # the rsd set, mult 0.7 (Joe 0802)

DDL = '''CREATE TABLE IF NOT EXISTS rpl_jig (
    jg_pk BIGINT AUTO_INCREMENT PRIMARY KEY, jg_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    jg_run       VARCHAR(20),                        -- one run id, so re-runs sit side by side
    jg_ms        BIGINT, jg_utc VARCHAR(20),         -- the BAR this row is about
    jg_kind      VARCHAR(12),                        -- heartbeat|delegate|walk|hop|anchor|confirm|exit|open
    jg_trigger_ms BIGINT,                            -- which delegated trigger this belongs to
    jg_pxs       DOUBLE, jg_close DOUBLE,
    jg_m4 DOUBLE, jg_r15 DOUBLE, jg_r22 DOUBLE,
    jg_x15 DOUBLE, jg_m15 DOUBLE, jg_g15x DOUBLE, jg_g15m DOUBLE,
    jg_mg5 DOUBLE, jg_mg15 DOUBLE, jg_mg30 DOUBLE, jg_mg1 DOUBLE, jg_mg2 DOUBLE,
    jg_oob_side  VARCHAR(2),                         -- s4Mage OOB side at this bar, or NULL if inside
    jg_run_bars  INT, jg_qualified TINYINT,          -- consecutive OOB bars; has it reached 240 s
    jg_side      VARCHAR(2), jg_dir VARCHAR(5),      -- set at the walk. hi->SHORT, lo->LONG
    jg_mfe_side  TINYINT,                            -- ALWAYS NULL: the trigger carries no bias to disagree with
    jg_s15_state VARCHAR(8), jg_s15_slope DOUBLE, jg_s15_r2 DOUBLE, jg_s15_r DOUBLE,
    jg_s22_state VARCHAR(8), jg_s22_slope DOUBLE, jg_s22_r2 DOUBLE, jg_s22_r DOUBLE,
    jg_hops      INT,
    jg_m15M DOUBLE, jg_m22M DOUBLE, jg_r4 DOUBLE,          -- s15 Mage, s22 Mage, s4r
    jg_s1r DOUBLE, jg_s30r DOUBLE,                         -- the LTF r set Joe reads
    jg_gsp_g5 DOUBLE, jg_gsp_g15 DOUBLE, jg_gsp_s30 DOUBLE, jg_gsp_s1 DOUBLE,   -- GATHER spread
    jg_gbd_g5 DOUBLE, jg_gbd_g15 DOUBLE, jg_gbd_s30 DOUBLE, jg_gbd_s1 DOUBLE,   -- signed dist to near boundary
    jg_h30 DOUBLE, jg_h45 DOUBLE, jg_h60 DOUBLE, jg_h90 DOUBLE,   -- HTF Mages above s22
    jg_rp4 TINYINT, jg_rp15 TINYINT, jg_rp22 TINYINT,      -- standalone predict_breach state per TF
    jg_gap4 DOUBLE, jg_gap15 DOUBLE, jg_gap22 DOUBLE,      -- r-units from r to the NEAR boundary; slip is a query
    jg_mage_lastoob VARCHAR(40), jg_mage_mid VARCHAR(40),   -- the 5 rsd Mages, both readings, fastest first
    jg_extra     TEXT,                               -- JSON: anything not worth a column
    KEY (jg_run), KEY (jg_ms), KEY (jg_kind), KEY (jg_trigger_ms))'''

COLS = ('jg_run,jg_ms,jg_utc,jg_kind,jg_trigger_ms,jg_pxs,jg_close,jg_m4,jg_r15,jg_r22,jg_x15,jg_m15,'
        'jg_g15x,jg_g15m,jg_mg5,jg_mg15,jg_mg30,jg_mg1,jg_mg2,jg_oob_side,jg_run_bars,jg_qualified,'
        'jg_side,jg_dir,jg_mfe_side,jg_s15_state,jg_s15_slope,jg_s15_r2,jg_s15_r,jg_s22_state,'
        'jg_s22_slope,jg_s22_r2,jg_s22_r,jg_hops,jg_m15M,jg_m22M,jg_r4,jg_s1r,jg_s30r,'
        'jg_gsp_g5,jg_gsp_g15,jg_gsp_s30,jg_gsp_s1,jg_gbd_g5,jg_gbd_g15,jg_gbd_s30,jg_gbd_s1,'
        'jg_h30,jg_h45,jg_h60,jg_h90,'
        'jg_rp4,jg_rp15,jg_rp22,'
        'jg_gap4,jg_gap15,jg_gap22,'
        'jg_mage_lastoob,jg_mage_mid,jg_extra')
NCOL = len(COLS.split(','))

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')


def _side_lastoob(v, hi, lo):
    """+1/-1/0 per bar: the side of the most recent OOB breach at or before this bar. Causal."""
    s = np.where(v >= hi, 1, np.where(v <= lo, -1, 0)).astype(np.int8)
    idx = np.arange(len(s))
    last = np.maximum.accumulate(np.where(s != 0, idx, -1))
    out = np.zeros(len(s), np.int8)
    m = last >= 0
    out[m] = s[last[m]]
    return out


def _side_mid(v):
    w = np.where(np.isfinite(v), v, 50.0)
    return np.where(w > 50.0, 1, np.where(w < 50.0, -1, 0)).astype(np.int8)


def _runlen(o):
    idx = np.arange(len(o))
    rst = np.where(o, 0, idx + 1)
    return (idx + 1) - np.maximum.accumulate(rst)


class Trigger:
    """One delegated r-pred, walked forward by exhv2's own chain. All reads end at the current bar."""
    def __init__(self, ms):
        self.ms = int(ms)
        self.state = 'WALK'
        self.walk_ms = self.anchor_ms = self.sig_ms = self.exit_ms = None
        self.side = self.dir = None
        self.hops = 0
        self.hop_bars = []
        self.xdr = None


def main(argv):
    hours = float(argv[argv.index('--hours') + 1]) if '--hours' in argv else 24.0
    force_first = '--trigger-now' in argv          # fire a delegate on the first tick
    run_id = dt.datetime.now(dt.timezone.utc).strftime('%m%d_%H%M%S')
    HI, LO, D = R.HI, R.LO, B.WALK_DWELL_BARS
    PXS = R.PXS_CFG
    d = DatabaseManager(**get_db_config()); d.connect()
    d.execute(DDL)
    # SELF-HEALING COLUMNS. CREATE TABLE IF NOT EXISTS does NOT add columns to a table that already
    # exists, so a new field silently fails every INSERT with 1054 until someone ALTERs by hand — which
    # is exactly what happened when jg_rp*/jg_gap* were added mid-run. Precedent: build_exhv2.py:409.
    for _c, _t in (('jg_rp4', 'TINYINT'), ('jg_rp15', 'TINYINT'), ('jg_rp22', 'TINYINT'),
                   ('jg_gap4', 'DOUBLE'), ('jg_gap15', 'DOUBLE'), ('jg_gap22', 'DOUBLE'),
                   ('jg_m15M', 'DOUBLE'), ('jg_m22M', 'DOUBLE'), ('jg_r4', 'DOUBLE'),
                   ('jg_s1r', 'DOUBLE'), ('jg_s30r', 'DOUBLE'),
                   ('jg_gsp_g5', 'DOUBLE'), ('jg_gsp_g15', 'DOUBLE'), ('jg_gsp_s30', 'DOUBLE'),
                   ('jg_gsp_s1', 'DOUBLE'), ('jg_gbd_g5', 'DOUBLE'), ('jg_gbd_g15', 'DOUBLE'),
                   ('jg_gbd_s30', 'DOUBLE'), ('jg_gbd_s1', 'DOUBLE'),
                   ('jg_h30', 'DOUBLE'), ('jg_h45', 'DOUBLE'), ('jg_h60', 'DOUBLE'),
                   ('jg_h90', 'DOUBLE')):
        try:
            d.execute('ALTER TABLE rpl_jig ADD COLUMN %s %s' % (_c, _t))
        except Exception:
            pass                                     # already present
    print('rpl_jig run %s   window %dh+%dh warmup   trigger uniform %d-%d min   for %.1f h'
          % (run_id, WIN_HOURS, WIN_WARMUP, TRIG_LO_MIN, TRIG_HI_MIN, hours))
    print('%d line specs   WALK_DWELL_BARS %d = %d s   HI/LO %g/%g' % (len(LINES), D, D * 5, HI, LO))

    t_end = time.time() + hours * 3600.0
    last_bar = None
    trigs, done = [], []
    # first trigger: uniform 30-60 min from now, same rule as every subsequent one
    next_trig = time.time() + random.uniform(TRIG_LO_MIN, TRIG_HI_MIN) * 60.0
    print('first delegate at %s' % u(next_trig * 1000))
    nrow = ntick = 0

    while time.time() < t_end:
        row = d.execute('SELECT MAX(kc_timestamp) m FROM kline_collection', fetch=True)[0]['m']
        if row is None or (last_bar is not None and int(row) <= last_bar):
            time.sleep(1.0)
            continue
        bar = int(row)

        with Jig(bar, hours=WIN_HOURS, warmup=WIN_WARMUP, overrides=LINES) as j:
            ts = np.asarray(j.ts, np.int64)
            base = j.W.base
            evt = base['volume'].to_numpy(dtype=float) > 0
            src = IC.build_source(base, PXS['src'])
            ei = np.flatnonzero(evt)
            pxs = np.full(len(src), np.nan)
            pxs[ei] = IC.dema(src[ei], int(PXS['len']))
            fin = np.isfinite(pxs)
            if fin.any():                                    # forward-fill onto the 5 s grid, as rpl_cache does
                ix = np.where(fin, np.arange(len(pxs)), 0)
                np.maximum.accumulate(ix, out=ix)
                pxs = pxs[ix]
                pxs[:int(np.argmax(fin))] = pxs[int(np.argmax(fin))]
            L = {n: np.asarray(j.W.line(n), float) for n in LINES}
            cau = _Causal(None)

        n = len(ts)
        i = n - 1                                            # THE CURRENT BAR. Nothing may read past it.
        if ts[i] != bar:
            i = int(np.searchsorted(ts, bar))
            i = min(i, n - 1)
        M4 = L['jM4']
        o = (M4 >= HI) | (M4 <= LO)
        rl = _runlen(o)
        QB = np.flatnonzero(B.oob_qualified(M4, HI, LO))      # the causal 240 s test
        # STANDALONE r-pred per TF (spec §2) + the gap from r to its NEAR boundary. Both are OBSERVED and
        # banked; nothing acts on them yet — the re-walk gate is still `momo`. Banking the gap per bar
        # makes the slip a QUERY rather than a rebuild, the same discipline rpl_momo_slip uses.
        # GATHER (Joe 0802). Per small TF: the spread of its {r, m, x, Mage} set and how far that set
        # sits from the boundary it is nearest. A TIGHT spread parked ON a boundary is the gather; the
        # push away is what follows. Banked, not acted on — the model is not defined yet.
        GATH = {}
        for _n, _ in SMALL_TF:
            _mg = {'g5': 'jMg5', 'g15': 'jMg15', 's30': 'jMg30', 's1': 'jMg1'}[_n]
            _set = [L['j%sr' % _n][i], L['j%sm' % _n][i], L['j%sx' % _n][i], L[_mg][i]]
            _set = [v for v in _set if np.isfinite(v)]
            if _set:
                _c = float(np.median(_set))
                GATH[_n] = (float(max(_set) - min(_set)),                       # spread
                            float(_c - LO) if abs(_c - LO) <= abs(_c - HI) else float(HI - _c))
            else:
                GATH[_n] = (None, None)
        RPB, GAP = {}, {}
        for _tf, (_r, _m, _M, _x) in RPRED_TF.items():
            RPB[_tf] = predict_breach(L[_r], L[_m], L[_M], HI, LO, R.FH, R.FL, 0.0)
            _rv = L[_r][i]
            # SIGNED: distance to the NEAR boundary, NEGATIVE once already through it. An unsigned
            # gap read 4.85 for an r of 10.15 that was already 4.85 BELOW LO — approaching and
            # spent look identical, which is exactly the distinction the slip rule turns on.
            GAP[_tf] = (float(_rv - LO) if abs(_rv - LO) <= abs(_rv - HI) else float(HI - _rv)) \
                if np.isfinite(_rv) else None
        LA = {nm: _side_lastoob(L[nm], HI, LO) for nm, _ in MAGES}
        MI = {nm: _side_mid(L[nm]) for nm, _ in MAGES}
        s = lambda a: ','.join(str(int(a[nm][i])) for nm, _ in MAGES)
        mg_la, mg_mid = s(LA), s(MI)

        def base_row(kind, trg=None, **kw):
            r = dict(jg_run=run_id, jg_ms=int(ts[i]), jg_utc=u(ts[i]), jg_kind=kind,
                     jg_trigger_ms=trg, jg_pxs=float(pxs[i]), jg_close=float(base['close'].to_numpy(float)[i]),
                     jg_m4=float(M4[i]), jg_r15=float(L['jr15'][i]), jg_r22=float(L['jr22'][i]),
                     jg_x15=float(L['jx15'][i]), jg_m15=float(L['jm15'][i]),
                     jg_g15x=float(L['jg15x'][i]), jg_g15m=float(L['jg15m'][i]),
                     jg_mg5=float(L['jMg5'][i]), jg_mg15=float(L['jMg15'][i]), jg_mg30=float(L['jMg30'][i]),
                     jg_mg1=float(L['jMg1'][i]), jg_mg2=float(L['jMg2'][i]),
                     jg_oob_side=('hi' if M4[i] >= HI else 'lo') if o[i] else None,
                     jg_run_bars=int(rl[i]), jg_qualified=int(rl[i] >= D),
                     jg_side=None, jg_dir=None, jg_mfe_side=None,
                     jg_s15_state=None, jg_s15_slope=None, jg_s15_r2=None, jg_s15_r=None,
                     jg_s22_state=None, jg_s22_slope=None, jg_s22_r2=None, jg_s22_r=None,
                     jg_hops=None,
                     jg_m15M=float(L['jM15'][i]), jg_m22M=float(L['jM22'][i]), jg_r4=float(L['jr4'][i]),
                     jg_s1r=float(L['js1r'][i]), jg_s30r=float(L['js30r'][i]),
                     jg_gsp_g5=GATH['g5'][0], jg_gsp_g15=GATH['g15'][0],
                     jg_gsp_s30=GATH['s30'][0], jg_gsp_s1=GATH['s1'][0],
                     jg_gbd_g5=GATH['g5'][1], jg_gbd_g15=GATH['g15'][1],
                     jg_gbd_s30=GATH['s30'][1], jg_gbd_s1=GATH['s1'][1],
                     jg_h30=float(L['jH30'][i]), jg_h45=float(L['jH45'][i]),
                     jg_h60=float(L['jH60'][i]), jg_h90=float(L['jH90'][i]),
                     jg_rp4=int(RPB[4][i]), jg_rp15=int(RPB[15][i]), jg_rp22=int(RPB[22][i]),
                     jg_gap4=GAP[4], jg_gap15=GAP[15], jg_gap22=GAP[22],
                     jg_mage_lastoob=mg_la, jg_mage_mid=mg_mid, jg_extra=None)
            r.update(kw)
            # NaN NEVER REACHES THE DB. The connector renders float('nan') as the bare literal `nan`,
            # which MySQL parses as a COLUMN NAME -> 1054 Unknown column 'nan' in 'field list', and the
            # whole process dies mid-tick. It killed run 0802_081401 at 08:16:00, two minutes after the
            # HTF Mages went in: a high-TF line whose current resampled bar is still partial returns NaN
            # at index -1. Coerce at the boundary rather than guarding each of 40-odd fields.
            def _san(v):
                if isinstance(v, float) and not np.isfinite(v):
                    return None
                return v
            return tuple(_san(r[c]) for c in COLS.split(','))

        OUT = [base_row('heartbeat')]
        ntick += 1

        # --- delegate ---------------------------------------------------------------------------------
        forced = os.path.exists(TRIG_FILE) or (force_first and ntick == 1)
        if forced:
            try:
                os.remove(TRIG_FILE)
            except OSError:
                pass
        if forced or time.time() >= next_trig:
            t = Trigger(ts[i]); trigs.append(t)
            OUT.append(base_row('delegate', trg=t.ms,
                                jg_extra=json.dumps({'note': 'bare trigger: no bias, no cur_tf',
                                                     'source': 'on-demand' if forced else 'scheduled'})))
            if not forced:                                   # an on-demand trigger does not reset the draw
                gap = random.uniform(TRIG_LO_MIN, TRIG_HI_MIN)
                next_trig = time.time() + gap * 60.0
            print('%s  DELEGATE (%s)  -> next scheduled %s'
                  % (u(ts[i]), 'on-demand' if forced else 'scheduled', u(next_trig * 1000)))

        # --- advance every open trigger ---------------------------------------------------------------
        for t in list(trigs):
            t0 = int(np.searchsorted(ts, t.ms))
            if t.state == 'WALK':
                nx = QB[QB > t0]
                if not len(nx):
                    continue
                w = int(nx[0])
                # REWALK 2 — hop while s22 reads momo at the candidate bar.
                # HOP-PENDING (fixed 0802 live, caught by the first backtest): if s22 reads momo but NO
                # later qualified bar exists YET, the rule says hop and there is nothing to hop to. The
                # causal answer is to WAIT and re-evaluate next tick, NOT to settle the walk here. The
                # first live trigger settled at 06:10:55 with s22 momo (slope -1.773, r2 0.852) and 0
                # qualified bars after it — the batch path would hop the moment one appears, and the jig
                # never would. That is a divergence, and it is the jig's, not the batch's.
                # NOTE: the batch path has the same shape at the TAPE EDGE — its last rows settle on a
                # truncated candidate list. Small, but real. Flagged, not yet fixed.
                pending = False
                while True:
                    sd = 'hi' if M4[w] >= HI else 'lo'
                    ed = 1 if sd == 'hi' else -1              # exhv2's own rule: the breach side IS the direction
                    st22 = B.momo(L['jr22'], ed, w)
                    nh = QB[QB > w]
                    # THE HOP GATE IS `momo`. Joe 0802: "we're not swapping - we're adding r-pred as a
                    # tool to SUPPORT momo. exactly how that will integrate needs to be figured out."
                    # r-pred (RPB) is computed and banked on every heartbeat and on this bar, but it
                    # GATES NOTHING. The two states are recorded side by side so the integration can be
                    # designed from their measured disagreement rather than guessed.
                    if st22[0] != 'momo':
                        break                                 # the rule says stop here
                    if not len(nh):
                        pending = True                        # must hop, cannot yet -> wait
                        break
                    w = int(nh[0])
                    # DEDUP ON THE TIMESTAMP, NOT THE INDEX (fixed 0802 live). The window slides forward
                    # every tick, so the same bar gets a DIFFERENT index each tick and an index-keyed
                    # guard never matches — one real hop was emitted once per tick with an inflating
                    # count (4 rows, all pointing at 08-02 07:04:20). Timestamps are stable; indices are not.
                    wms = int(ts[w])
                    if wms not in t.hop_bars:
                        t.hop_bars.append(wms)
                        OUT.append(base_row('hop', trg=t.ms, jg_hops=len(t.hop_bars), jg_side=sd,
                                            jg_s22_state=st22[0],
                                            jg_extra=json.dumps({'hop_to': u(wms), 's22_momo': st22[0],
                                                                 's22_rpred': int(RPB[22][w]), 'ed': int(ed),
                                                                 'agree': bool((st22[0] == 'momo') == (RPB[22][w] == ed))})))
                t.hops = len(t.hop_bars)                      # derived, never accumulated
                if pending:
                    continue
                sd = 'hi' if M4[w] >= HI else 'lo'
                ed = 1 if sd == 'hi' else -1
                st15 = B.momo(L['jr15'], ed, w); st22 = B.momo(L['jr22'], ed, w)   # OBSERVED, no longer gating
                t.walk_ms = int(ts[w]); t.side = sd
                t.dir = 'SHORT' if sd == 'hi' else 'LONG'
                t.xdr = -1 if sd == 'hi' else 1
                t.state = 'ANCHOR'
                OUT.append(base_row('walk', trg=t.ms, jg_side=sd, jg_dir=t.dir, jg_hops=t.hops,
                                    jg_s15_state=st15[0], jg_s15_slope=float(st15[1]), jg_s15_r2=float(st15[2]),
                                    jg_s15_r=float(st15[3]), jg_s22_state=st22[0], jg_s22_slope=float(st22[1]),
                                    jg_s22_r2=float(st22[2]), jg_s22_r=float(st22[3]),
                                    jg_extra=json.dumps({'walk_utc': u(ts[w]), 'lag_min': (int(ts[w]) - t.ms) / 60000.0})))
                print('%s  WALK %s %s  hops %d  s15 %s  s22 %s' % (u(ts[w]), sd, t.dir, t.hops, st15[0], st22[0]))

            if t.state == 'ANCHOR':
                # THE SLIP GATE (Joe 0802: "release on x-cross-m when gap <= 2.0"). The x X m cross only
                # counts once r is within momo_ride_oob_slip of the boundary it is heading for. Identical
                # to build_momo_slip.py:12-14 — the x-cross fire allowance and the r-pred release are the
                # same predicate seen from two sides, so ONE knob governs both.
                #   side hi -> max(s15r, s22r) >= HI - SLIP
                #   side lo -> min(s15r, s22r) <= LO + SLIP
                # RE-DERIVE THE WALK BAR FROM ITS TIMESTAMP, EVERY TICK (fixed 0802 18:15, task #46).
                # The window slides forward each tick, so a bar's INDEX changes while its TIMESTAMP does
                # not. t.wbar used to be stored raw at the walk and reused here, which made this filter
                # progressively stricter as a trigger aged — it demanded crosses further and further into
                # the future. Same class as the hop-dedup fault (index-keyed, fixed by keying on ts).
                # The trigger origin already did it correctly at :355; these three stages did not.
                wbar = int(np.searchsorted(ts, t.walk_ms))
                c = cau.cross_wob(L['jx15'] - L['jm15'], 0.0, t.xdr, R.WOBN)
                e = np.flatnonzero((c & ~np.r_[False, c[:-1]]))
                e = e[e >= wbar]
                a = None
                for _c in e:
                    _c = int(_c)
                    if t.side == 'hi':
                        ok = max(L['jr15'][_c], L['jr22'][_c]) >= HI - SLIP
                    else:
                        ok = min(L['jr15'][_c], L['jr22'][_c]) <= LO + SLIP
                    if ok:
                        a = _c
                        break
                if a is not None:
                    t.anchor_ms = int(ts[a]); t.state = 'CONFIRM'
                    _g = (max(L['jr15'][a], L['jr22'][a]) - (HI - SLIP)) if t.side == 'hi' \
                        else ((LO + SLIP) - min(L['jr15'][a], L['jr22'][a]))
                    OUT.append(base_row('anchor', trg=t.ms, jg_side=t.side, jg_dir=t.dir,
                                        jg_extra=json.dumps({'anchor_utc': u(ts[a]), 'slip': SLIP,
                                                             'crosses_rejected_by_slip': int((e < a).sum()),
                                                             'slip_margin': float(_g),
                                                             's15r': float(L['jr15'][a]), 's22r': float(L['jr22'][a])})))
                    print('%s  ANCHOR (slip ok, %d crosses rejected)' % (u(ts[a]), int((e < a).sum())))

            if t.state == 'CONFIRM':
                abar = int(np.searchsorted(ts, t.anchor_ms))      # re-derived every tick — see :425
                c = cau.cross_wob(L['jg15x'] - L['jg15m'], 0.0, t.xdr, R.WOBN)
                e = np.flatnonzero((c & ~np.r_[False, c[:-1]]))
                e = e[e >= abar]
                if len(e):
                    sbar = int(e[0]); t.sig_ms = int(ts[sbar]); t.state = 'EXIT'
                    OUT.append(base_row('confirm', trg=t.ms, jg_side=t.side, jg_dir=t.dir,
                                        jg_extra=json.dumps({'signal_utc': u(ts[sbar]),
                                                             'confirm_lag_min': (t.sig_ms - t.anchor_ms) / 60000.0,
                                                             'sig_px': float(pxs[sbar])})))
                    print('%s  *** SIGNAL *** %s' % (u(ts[sbar]), t.dir))

            if t.state == 'EXIT':
                # THE STAGE THAT NEVER FIRED. 0 exit rows in the 9h50m run of 0802 despite two confirmed
                # signals, because t.sbar was a stored INDEX and the window slid out from under it — see
                # :425. The 11:34:40 confirms had a qualified bar 22.8 min later at 11:57:30 and never
                # exited. sbar is now re-derived from t.sig_ms, like every other bar reference here.
                sbar = int(np.searchsorted(ts, t.sig_ms))
                nx = QB[QB > sbar]
                if len(nx):
                    eb = int(nx[0]); t.exit_ms = int(ts[eb]); t.state = 'DONE'
                    sgn = -1.0 if t.side == 'hi' else 1.0
                    seg = pxs[sbar:eb + 1]
                    ret = float(sgn * (pxs[eb] - pxs[sbar]) / pxs[sbar] * 100.0)
                    up = (np.nanmax(seg) - pxs[sbar]) / pxs[sbar] * 100.0
                    dn = (pxs[sbar] - np.nanmin(seg)) / pxs[sbar] * 100.0
                    OUT.append(base_row('exit', trg=t.ms, jg_side=t.side, jg_dir=t.dir,
                                        jg_extra=json.dumps({'exit_utc': u(ts[eb]), 'ret_pct': ret,
                                                             'mae_pct': float(up if t.side == 'hi' else dn),
                                                             'mfe_pct': float(dn if t.side == 'hi' else up),
                                                             'hold_min': (t.exit_ms - t.sig_ms) / 60000.0})))
                    print('%s  EXIT  ret %+.3f' % (u(ts[eb]), ret))
                    trigs.remove(t); done.append(t)

        d.executemany('INSERT INTO rpl_jig (' + COLS + ') VALUES (' + ','.join(['%s'] * NCOL) + ')', OUT)
        nrow += len(OUT)
        last_bar = bar
        if ntick % 60 == 0:
            print('%s  tick %d  rows %d  open %d  done %d' % (u(bar), ntick, nrow, len(trigs), len(done)))

    for t in trigs:                                          # still open at the end — recorded, not dropped
        d.execute('INSERT INTO rpl_jig (jg_run,jg_ms,jg_utc,jg_kind,jg_trigger_ms,jg_extra) '
                  'VALUES (%s,%s,%s,%s,%s,%s)',
                  (run_id, t.ms, u(t.ms), 'open', t.ms,
                   json.dumps({'state': t.state, 'walk': u(t.walk_ms) if t.walk_ms else None,
                               'anchor': u(t.anchor_ms) if t.anchor_ms else None,
                               'signal': u(t.sig_ms) if t.sig_ms else None, 'hops': t.hops})))
    print('DONE  run %s  ticks %d  rows %d  triggers %d (%d completed, %d open)'
          % (run_id, ntick, nrow, len(trigs) + len(done), len(done), len(trigs)))
    d.disconnect()


if __name__ == '__main__':
    main(sys.argv[1:])
