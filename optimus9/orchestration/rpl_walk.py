"""rpl auto-chain: walk the whole day's flip stream from ONE seed. IMPORTABLE.
Config (DB baseline) + jig warmup are loaded ONCE at import; run_chain(seed_bias, seed_start) walks the
cached line arrays flip-to-flip. Emerging lines only (causal — what o9-live sees). See docs/rpl_flow_spec.md.
Line/knob source = rpl_config 'baseline'.

Each flip is first-class (own MMDD_NN id, rr_rollercoaster tag): an s2-cycle ROLLERCOASTER reversal (counter
to the trend, gcs5-timed, no pyramid) or an s8-CLIMB flip (trend, s30-timed). A counter-trend leg exits when
the trend r-preds again (option 1). MMDD_01 = first flip of the UTC day."""
import numpy as np, datetime as dtm, hashlib
from datetime import timezone
from optimus9 import DatabaseManager
from optimus9.config import get_db_config
from optimus9.analysis.jig import kline, bbline, _latch_with_reset
from optimus9.compute.breaching_line import predict_breach
from optimus9.db.rpl_event_store import RplEventStore
from optimus9.orchestration.rpl_cache import cache_jig

# --- config (once) ---
_db = DatabaseManager(**get_db_config()); _db.connect(); _st = RplEventStore(_db); C = _st.load_config('baseline')
_sysrow = _db.execute("SELECT pxsmooth_dema_src, pxsmooth_dema_len, hi_boundary, lo_boundary "
                      "FROM optimus9_system LIMIT 1", fetch=True)   # px_smooth params + THE boundary home (0727)
PXS_CFG = {'src': _sysrow[0]['pxsmooth_dema_src'], 'len': _sysrow[0]['pxsmooth_dema_len']} if _sysrow else {'src': 'close', 'len': 2}
_db.disconnect()
# boundary: optimus9_system is the single home (was duplicated in rpl_config.boundary + two script literals).
# fence: rpl_config, because it is machine-specific (Joe 0727) — NOT a system-wide value.
HI, LO = float(_sysrow[0]['hi_boundary']), float(_sysrow[0]['lo_boundary'])
FH, FL = C['fence']['fh'], C['fence']['fl']; LN = C['lines']
DELOFF = C['delegate_offset']; WOBN = C['wob_n']; ANTI = C['anti']; BND4 = C['xcp_bnd_offset']; FLOOR = C['xcp_tf_floor']
LATCH_DEPTH = C['latch_depth']; LATCH_DWELL = C['latch_dwell']; DELFLOOR = C['delegate_tf_floor']
CATCHMANY = C['catch_many_tf']; XPRED_THRESH = C['xpred_thresh']; XPRED_BAND = C['xpred_band']   # delegate split (0727)
FIN_BIND_TOL = C['finisher_bind_tol']   # flip_finisher vote-clustering window, 5s event bars (0 = votes simultaneous)
FIN_N_OF9 = C['finisher_n_of9']         # flip_finisher set-votes required, of 9 (3 sets x {m OOB, Mage OOB, r-in-lb})
S3A_TOL_TF_BARS = C['s3a_tolerance_tf_bars']  # capture a flip_finisher within N TF3 bars BEFORE the s3x cross (0 = none)
S3A_CROSS_WOB = C['s3a_cross_wob']            # s3x x s3am cross debounce, EMERGING 5s bars
S3A_R_LB = C['s3a_r_lb']                      # s3a qualify r-lookback, in the r-line's OWN TF bars
S3A_X_LEN = C['s3a_x_len']; S3A_X_MULT = C['s3a_x_mult']   # the s3x line (BB at TF3) the s3a stage crosses
XCPW = C['xcp_cross_wob']    # x-cross-pred DESTINATION debounce, EMERGING 5s bars. 1 = identity/raw edge
XCPD = C['xcp_origin_dwell'] # x-cross-pred ORIGIN dwell: bars x must hold the pre-cross side. 1 = no filter
FIN_S30R_SLIP = C['finisher_s30r_boundary_slip']; FIN_NEAR_DWELL = C['finisher_s30r_near_dwell']; FIN_S1R_SLIP = C['finisher_s1r_boundary_slip']
EXIT_TF_FLOOR = C['exit_tf_floor']
RETEST_PROX = C['retest_proximity_pct']; RETEST_VOTE_MIN = C['retest_vote_min']; RETEST_VOTE_TFS = list(C['retest_vote_tfs'])
RETEST_MIN_IB_MS = C['retest_min_ib_sec'] * 1000
CONFIRM_TOL = C['s1s2_confirm_tol_ms']; GCS5_RTOL = C['gcs5_r_tol']
import os as _os
# Joe 0730: RPL_TF_CEILING lets a caller build L0 ONCE at the ceiling it needs. Without it, research at
# ceiling 120 pays for a full ceiling-90 build at import (14.7 s) and then rebuilds at 120 (9.9 s), and
# reaching rebuild_cache costs a build_exhaust import (37.7 s). Unset = rpl_config.tf_ceiling, unchanged.
TFS = list(range(1, int(_os.environ.get('RPL_TF_CEILING', C['tf_ceiling'])) + 1))
# THE TAPE — ONE SOURCE OF TRUTH (Joe 0802: "there should be a single line cache that spans 05-18 to 08-01").
# Home is here because this module already owns end_ms and the RPL_TF_CEILING override above, and every
# consumer already imports it as R. Three literals used to disagree: this file (07-13), build_rpl_6of9
# (JUNE_END 06-14) and linelab (06-14) — and build_rpl_6of9 reassigned R.end_ms at import, so the tape you
# got depended on your import order. That silently folded every pre-tape row onto bar index 0 in any script
# that imported rpl_walk without build_exhv2 (np.searchsorted returns 0, no error).
#   span    = HOURS + 2*WARMUP = 2536 h, floored by the kline_collection start at 2026-04-28 06:34
#   ts      = 04-28 06:34:00 -> 07-31 23:59:55, 1,636,872 bars
#   W0      = END_MS - (HOURS + WARMUP) h = 06-08 08:00 (bias_machine only; never reaches the line cache)
# 40/1248 is kept because the tape .npz for this key already exists on disk (the OOS build).
# THE REGISTRY. Keyed by the tape's own end date — no coined name, so the key cannot drift from the thing.
# Selected by RPL_TAPE; unset = the default below. An unknown key raises rather than falling back silently.
# (end_ms, hours, warmup) travel together because the cache key hashes all three — changing one alone
# produces a different file holding identical data. One env var, one tuple: SRP.
#
#   '06-14'  the DIAL-IN tape. 04-28 06:34:00 -> 06-13 23:59:55, 807,432 bars, 46.7 days.
#            Already built on disk. Every artefact banked on 0802 is on this key, so it is also the
#            controlled baseline: same bars, only the code differs.
#   '08-01'  the FULL tape. 04-28 06:34:00 -> 07-31 23:59:55, 1,636,872 bars, 95.7 days.
#            Joe 0802: "a single line cache that spans 05-18 to 08-01". Its tape .npz already exists
#            (the OOS build); its line .npy files do not. 13,095,104 bytes per line, 2.03x the dial-in tape.
#            Joe 0802: dial the code in on smaller IS windows BEFORE consuming this.
#   '08-02'  the LAST-7-DAYS tape (Joe 0802: "re-build exhv2 for the last 7 days"). End is the last clean
#            hour before the live kline head (08-02 21:32:15), so the final signal still has bars to exit
#            into. HOURS 168 = the 7 days. WARMUP 600 is the '06-14' value, NOT a new number: 600 h = 25 d,
#            far past the slowest line (bb 37 @ TF120 = 74 h).
#            span = HOURS + 2*WARMUP = 1368 h = 57 d -> ts 06-06 21:00 -> 08-02 21:00, ~984,960 bars.
#            The kline floor is 05-07 00:00 (the pre-05-07 synthetics were deleted 0802), so this tape is
#            built entirely from real 5 s data — no ANALYSIS_START clipping is doing any work on it.
#            The 7-day ANALYSIS scope is applied downstream by build_exh_stat/build_rpred --window 7-26 8-2,
#            which is the flag that already owns "scope the exhaustions" (Joe 0730). Warmup and analysis
#            window are separate concerns and stay separate knobs.
TAPES = {
    '06-14': (dtm.datetime(2026, 6, 14, 0, 0, tzinfo=timezone.utc), 40, 600),
    '08-01': (dtm.datetime(2026, 8,  1, 0, 0, tzinfo=timezone.utc), 40, 1012),
    '08-02': (dtm.datetime(2026, 8,  2, 21, 0, tzinfo=timezone.utc), 168, 600),
}
# DEFAULT '08-01' (Joe 0802). Measured before flipping: built through Jig directly, both tapes give
# bit-identical close, volume and bb 37|0.7|close @ TF4 over the identical 807,432 overlapping bars.
# The tape width changes nothing. The 06-14 line FILES are stale — they were written before the
# pre-05-18 synthetic klines were replaced with real 5 s data on the morning of 0802 — so the 08-01 key
# is also the only one whose lines are guaranteed to be built from the corrected data. See task #42.
TAPE = _os.environ.get('RPL_TAPE', '08-01')
if TAPE not in TAPES:
    raise SystemExit('RPL_TAPE=%r is not a known tape. Known: %s' % (TAPE, ', '.join(sorted(TAPES))))
_tape_end, HOURS, WARMUP = TAPES[TAPE]
END_MS = int(_tape_end.timestamp() * 1000)
end_ms = END_MS                      # lowercase alias: every existing call site reads R.end_ms
RPRED_VETO = True    # ⚠ TODO REMOVE (Joe 0725): DEAD NO-OP — cannot fire. For an `exh` to win the earliest-wins sort it must
#                      beat `rp`, so no s3-8 TF r-preds cur at that bar; the veto check below is therefore always False.
#                      Added by mistake — blurs RPL/RC-sweep work with the linelab spec. Left in place for now; strip later.
fmt = lambda t: dtm.datetime.fromtimestamp(int(t) / 1000, timezone.utc).strftime('%H:%M:%S')

def _mk(nm, tf, t): return kline(nm, tf, k_len=t['k_len'], rsi=t['rsi'], stc=t['stc'], src=t['src']) if t['kind'] == 'kline' else bbline(nm, tf, length=t['length'], mult=t['mult'], src=t['src'])
_ovr = {}
for _TF in TFS:
    for _k in ('r', 'x', 'm', 'M'): _ovr.update(_mk(f'{_k}{_TF}', _TF, LN[_k]))
for _nm in ('s1x', 's1m'): _ovr.update(_mk(_nm, 1.0, LN[_nm]))
for _nm in ('s30r', 's30M'): _ovr.update(_mk(_nm, 0.5, LN[_nm]))
_ovr.update(_mk('s30x', 0.5, LN['x'])); _ovr.update(_mk('s30m', 0.5, LN['m']))
_GCS5 = 5.0 / 60.0                                                     # gcs5 = generic r/m/x at 5-second itf (s2-cycle reversal finisher)
_ovr.update(_mk('gcs5r', _GCS5, LN['r'])); _ovr.update(_mk('gcs5m', _GCS5, LN['m'])); _ovr.update(_mk('gcs5x', _GCS5, LN['x']))

# --- r-pred persistence (Joe 0730) ---------------------------------------------------------------
# predict_breach emits a per-bar STATE {+1 hi, -1 lo, 0 none}; nothing recorded WHEN it turned on, so every
# "r-pred time" in the project was reconstructed downstream and three derives gave three answers. This writes
# the moment at the only place that owns the state: immediately after P is built.
#   ROW      one contiguous non-zero run of P[TF] = one r-pred. Repeats inside a run are the same signal.
#   DEDUP    an IF on the write, walking the line forward in time (Joe 0730): a run start is written only if
#            no row has been written for that line since the last exhaustion on it. Causal - at bar a it reads
#            only exhaustions that already happened. r straddling the fence re-fires; those re-fires are the
#            "further signals" and are not written.
#   WINDOW   RPRED_START = 05-18. Pre-05-18 is synthetic warmup, never analysis (Joe 0729).
#   DEFAULT  OFF. build_lines runs at IMPORT and ~20 scripts import this module; an unconditional write would
#            make every import a DB writer. build_rpred.py flips it and rebuilds.
RPRED_PERSIST = False
RPRED_START = int(dtm.datetime(2026, 5, 18, tzinfo=timezone.utc).timestamp() * 1000)
RPRED_END = None     # Joe 0730: cap the WRITE to the working window's end. r-pred still looks back freely
#                      to RPRED_START; this only stops writing episodes that no exhaustion under study can use.
RPRED_DDL = '''CREATE TABLE IF NOT EXISTS rpl_rpred (
    rp_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    rp_ts        BIGINT NOT NULL, rp_utc VARCHAR(19),   -- FIRST bar of the run = the r-pred moment
    rp_tf        INT NOT NULL,                          -- the line: s{tf}r
    rp_dir       TINYINT NOT NULL,                      -- +1 hi-breach predicted, -1 lo-breach predicted
    rp_r         DOUBLE, rp_mini_bb DOUBLE, rp_maj_bb DOUBLE,
    rp_anchor    DOUBLE,                                -- max(mini,Major) for +1, min(...) for -1
    rp_margin    DOUBLE,                                -- anchor overshoot minus r's undershoot; >0 = predicted
    rp_end_ts    BIGINT, rp_end_utc VARCHAR(19), rp_run_bars INT,   -- run end (state returns to 0)
    rp_prev_exh_ms BIGINT,                              -- the exhaustion on this line that re-armed the write
    UNIQUE KEY uq_rpred (rp_tf, rp_dir, rp_ts),
    KEY (rp_ts), KEY (rp_tf, rp_dir))'''


def persist_rpred(ts, E, P, fx_bull, fx_bear):
    """[PRODUCER] Write the r-pred MOMENT: the first bar of an r-pred run on a line.

    THE RUN (Joe 0730): the r-pred is CANCELLED by the x/r cross on the same line - set on the predict
    rising edge, reset by the cross. Same definition as build_rplwalk2.rp_matrix; the ladder and this
    table must not disagree about what an r-pred is.

    THE DEDUP is the latch itself. A latched run can only end at a cross, so the fence re-fires that Joe
    asked to dedup ("any further signals for the same line up to the exhaustion") are already inside one
    run and never reach the writer. One row = one r-pred episode. The earlier exhaustion-arming on top of
    this was double-dedup: it pinned the stored r-pred to whatever fired first after 05-18 and suppressed
    every episode after it, which is why s69's 0520 10:26 exhaustion was reporting a 0518 20:42 r-pred.
    Line = (rp_tf, rp_dir); rp_dir = _polar CS, +1 bull / -1 bear."""
    _u = lambda ms: dtm.datetime.fromtimestamp(ms / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    from optimus9.analysis.jig import _latch_with_reset
    d = DatabaseManager(**get_db_config()); d.connect()
    d.execute(RPRED_DDL)
    EX = {}
    for r_ in d.execute('SELECT DISTINCT ea_conf_ms, ea_cur_tf, ea_bias FROM rpl_exh_applied', fetch=True):
        EX.setdefault((int(r_['ea_cur_tf']), 1 if r_['ea_bias'] == 'bull' else -1), []).append(int(r_['ea_conf_ms']))
    for k in EX:
        EX[k].sort()
    rows = 0; out = []
    for tf in sorted(P):
        r = E[tf]['r']; mn = E[tf]['m']; mj = E[tf]['M']
        for dr in (1, -1):
            fx = np.asarray((fx_bull if dr > 0 else fx_bear)[tf], bool)
            pr = (np.asarray(P[tf], np.int8) == dr)
            s = _latch_with_reset(pr & ~np.r_[False, pr[:-1]], fx)   # r-pred cancelled by the x/r cross
            if not s.any():
                continue
            ch = np.flatnonzero(s[1:] != s[:-1]) + 1
            st = np.r_[0, ch]; en = np.r_[ch, len(s)]          # en exclusive
            keep = s[st] & (ts[st] >= RPRED_START)             # synthetic warmup is not analysis
            if RPRED_END:
                keep &= (ts[st] < RPRED_END)
            st = st[keep]; en = en[keep]
            ex = EX.get((tf, dr), []); j = 0; prev = None
            for a, b in zip(st.tolist(), en.tolist()):
                t0 = int(ts[a])
                while j < len(ex) and ex[j] <= t0:             # record which exhaustion this episode follows
                    prev = ex[j]; j += 1
                anc = max(mn[a], mj[a]) if dr > 0 else min(mn[a], mj[a])
                marg = ((anc - HI) - (HI - r[a])) if dr > 0 else ((LO - anc) - (r[a] - LO))
                out.append((t0, _u(t0), int(tf), dr, float(r[a]), float(mn[a]), float(mj[a]), float(anc),
                            float(marg), int(ts[b - 1]), _u(int(ts[b - 1])), int(b - a), prev))
                rows += 1
    d.executemany('''INSERT INTO rpl_rpred (rp_ts,rp_utc,rp_tf,rp_dir,rp_r,rp_mini_bb,rp_maj_bb,rp_anchor,
        rp_margin,rp_end_ts,rp_end_utc,rp_run_bars,rp_prev_exh_ms) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE rp_r=VALUES(rp_r), rp_mini_bb=VALUES(rp_mini_bb), rp_maj_bb=VALUES(rp_maj_bb),
        rp_anchor=VALUES(rp_anchor), rp_margin=VALUES(rp_margin), rp_end_ts=VALUES(rp_end_ts),
        rp_end_utc=VALUES(rp_end_utc), rp_run_bars=VALUES(rp_run_bars),
        rp_prev_exh_ms=VALUES(rp_prev_exh_ms)''', out)
    n = d.execute('SELECT COUNT(*) c FROM rpl_rpred', fetch=True)[0]['c']
    d.disconnect()
    print('persist_rpred: %d r-pred episodes written over %d TFs from %s -> rpl_rpred now %d rows'
          % (rows, len(P), _u(RPRED_START)[:10], n))
    return rows


# --- warmup (once, cached) + walk-independent arrays ---
def build_lines(src):
    """Read every line the flow needs from a line-source (JigCache or jig) into a dict. Line production stays
    in the jig/BiasWindow (SRP) — this only assembles the arrays + the derived predict_breach series. Loaded
    once at import into L0; run_chain walks L0."""
    ts = np.asarray(src.ts, np.int64)
    evt = getattr(src, 'evt', None)                                   # event bars (volume>0); index-vs-event gotcha
    if evt is None:
        try: evt = src.W.base['volume'].to_numpy(dtype=float) > 0
        except Exception: evt = np.ones(len(ts), bool)
    E = {TF: {k: np.asarray(src.W.line(f'{k}{TF}'), float) for k in ('r', 'x', 'm', 'M')} for TF in TFS}
    P = {TF: predict_breach(E[TF]['r'], E[TF]['m'], E[TF]['M'], HI, LO, FH, FL, 0.0) for TF in TFS}
    # persist_rpred is fired below, once fx_bull/fx_bear exist - the r-pred RUN is cancelled by the x/r
    # cross, so the writer needs the cross series that this same function produces a few lines down.
    _up = lambda s: (s > 0) & (np.roll(s, 1) <= 0); _dn = lambda s: (s < 0) & (np.roll(s, 1) >= 0)   # match _polar up/dn
    # DEBOUNCED fcross(x-r) (Joe 0728). Was a raw 1-bar edge — the only cross in the chain with no wob, which let a
    # single-bar x spike register an exhaustion (06-13 18:28:40: x jumped +39.7 in one bar, poked 0.4 above r, fell
    # back 48 -> a spurious crossunder that gated the whole 19:42 trade). cross_wob is the sanctioned producer; the
    # consumer takes the rising edge. XCPW=1 is the IDENTITY (run>=1 = on the crossed side), i.e. the old behaviour.
    # ORIGIN-SIDE DWELL (Joe 0728) is the filter that actually kills the spike: debouncing the DESTINATION does
    # nothing here, because x sits below r almost continuously — the spurious edge comes from a one-bar visit to
    # the ORIGIN side. So x must hold the pre-cross side for XCPD bars before a cross counts.
    def _wx(delta, direction):
        c = src.causal.cross_wob(delta, 0.0, direction, XCPW)        # destination held >= XCPW
        edge = c & ~np.roll(c, 1)                                    # confirmation bar = cross bar + XCPW-1
        orig = src.causal.cross_wob(delta, 0.0, -direction, XCPD)    # ORIGIN side held >= XCPD
        return edge & np.roll(orig, XCPW)                            # ...ending immediately before the cross
    fx_bull = {TF: _wx(E[TF]['x'] - E[TF]['r'], -1) for TF in TFS}   # BULL = x crosses UNDER r
    fx_bear = {TF: _wx(E[TF]['x'] - E[TF]['r'], +1) for TF in TFS}   # BEAR = x crosses OVER r
    if RPRED_PERSIST:                                                # Joe 0730: persist the r-pred MOMENT
        persist_rpred(ts, E, P, fx_bull, fx_bear)
    s30r_ = np.asarray(src.W.line('s30r'), float); s30M_ = np.asarray(src.W.line('s30M'), float)
    s30x_ = np.asarray(src.W.line('s30x'), float); s30m_ = np.asarray(src.W.line('s30m'), float)
    return dict(src=src, ts=ts, n=len(ts), idxn=np.arange(len(ts)), ei=np.flatnonzero(evt), E=E, P=P, s2r=E[2]['r'], pxs=getattr(src, 'pxs', None),
                fx_bull=fx_bull, fx_bear=fx_bear,
                s1x=np.asarray(src.W.line('s1x'), float), s1m=np.asarray(src.W.line('s1m'), float),
                s30r_=s30r_, s30M_=s30M_, s30x_=s30x_, s30m_=s30m_,
                g5r=np.asarray(src.W.line('gcs5r'), float), g5m=np.asarray(src.W.line('gcs5m'), float), g5x=np.asarray(src.W.line('gcs5x'), float),
                Ps30=predict_breach(s30r_, s30m_, s30M_, HI, LO, FH, FL, 0.0))

J = cache_jig(end_ms, HOURS, WARMUP, _ovr, pxs_cfg=PXS_CFG)
L0 = build_lines(J)

def _ms(h, m, s=0, day=12): return int(dtm.datetime(2026, 7, day, h, m, s, tzinfo=timezone.utc).timestamp() * 1000)

def _polar(bias):
    BULL = (bias == 'bull'); FLIP = 'bear' if BULL else 'bull'
    CB = HI if BULL else LO; CS = 1 if BULL else -1; FS = -1 if BULL else 1
    up = lambda s: (s > 0) & (np.roll(s, 1) <= 0); dn = lambda s: (s < 0) & (np.roll(s, 1) >= 0)
    return dict(BULL=BULL, FLIP=FLIP, CB=CB, CS=CS, FS=FS,
        fcross=(dn if BULL else up),
        oob_climb=((lambda r: r >= CB) if BULL else (lambda r: r <= CB)),
        near_ib=((lambda r: r > CB - BND4) if BULL else (lambda r: r < CB + BND4)),
        s2r_es=((lambda s: s > ANTI) if BULL else (lambda s: s < ANTI)),
        oob_climb_m=((lambda m: m > HI) if BULL else (lambda m: m < LO)),
        WOB_DIR=(-1 if BULL else 1))

_REV = hashlib.md5(open(__file__, 'rb').read()).hexdigest()[:12]

def retest_scan(direction='bear'):
    """Detect double-top/bottom RETESTS (causal), gcs5 finisher bolted on. direction='bear' = hi-breach short
    (retest a prior high). Trigger = s1Mage re-enters OOB (was IB). Reference = max/min px_smooth over the PRIOR
    s1Mage-OOB excursion. DECLARED at the first event bar of the current excursion where px_smooth is within
    retest_proximity_pct of that reference AND s1/s2 {r,Mage} show >= retest_vote_min divergence votes (weaker
    momentum at the equal extreme) vs the reference bar. The gcs5 latch finisher (times the entry) follows the
    declare. Returns [{dir, declare, finisher, ref, votes}, ...]."""
    L = L0; E = L['E']; ts = L['ts']; pxs = L['pxs']; ei = L['ei']; g5r = L['g5r']; g5m = L['g5m']; g5x = L['g5x']
    hi = (direction == 'bear'); s1M = E[1]['M']
    oob = (s1M > HI) if hi else (s1M < LO)
    pc = _polar('bull' if hi else 'bear')                        # bear retest reverses a bull leg (and vice-versa)
    ex = g5x[ei]; em = g5m[ei]; roob = pc['oob_climb'](g5r[ei]); cross = pc['fcross'](ex - em)
    eb = ei[oob[ei]]                                              # event bars that are OOB
    if len(eb) == 0: return []
    brk = np.flatnonzero(np.diff(ts[eb]) >= RETEST_MIN_IB_MS)     # new excursion only after a GENUINE IB dwell (merge micro-wiggles)
    starts = np.concatenate(([eb[0]], eb[brk + 1])); ends = np.concatenate((eb[brk], [eb[-1]]))
    out = []
    for k in range(1, len(starts)):
        seg = pxs[starts[k - 1]:ends[k - 1] + 1]                  # prior excursion (whole excursion)
        ref_i = starts[k - 1] + (int(np.nanargmax(seg)) if hi else int(np.nanargmin(seg))); ref = pxs[ref_i]
        for j in ei[(ei >= starts[k]) & (ei <= ends[k])]:        # current excursion, event bars
            if abs(pxs[j] - ref) / ref * 100.0 > RETEST_PROX: continue
            votes = 0
            for tf in RETEST_VOTE_TFS:
                for arr in (E[tf]['r'], E[tf]['M']):
                    votes += (arr[j] < arr[ref_i]) if hi else (arr[j] > arr[ref_i])
            if votes >= RETEST_VOTE_MIN:
                latch = np.maximum.accumulate((roob & (ei > j)).astype(np.int8)).astype(bool)
                gf = ei[np.flatnonzero(cross & latch & (ei > j))]
                fin = int(ts[gf[0]]) if len(gf) else None        # gcs5 latch finisher (entry), bolted onto the declare
                out.append(dict(dir=direction, declare=int(ts[j]), finisher=fin, ref=int(ts[ref_i]), votes=int(votes)))
                break
    return out


def _persist_chain(flips):
    """Refresh rpl_run/rpl_event for every day the chain touched: drop that day's prior runs (the chain
    renumbers), then register each flip as its own MMDD_NN run + log its event stream (rr_rollercoaster set)."""
    if not flips:
        return
    db = DatabaseManager(**get_db_config()); db.connect(); st = RplEventStore(db)
    days = {f['walk'][:4] for f in flips}                        # MMDD prefix scopes the renumber to that calendar day
    for r in db.execute("SELECT rr_pk, rr_walk FROM rpl_run WHERE rr_walk IS NOT NULL", fetch=True):
        if r['rr_walk'][:4] in days:
            db.execute("DELETE FROM rpl_run WHERE rr_pk=%s", (r['rr_pk'],))
    for f in flips:
        w0 = f['ev'][0][0] if f['ev'] else f['ts']
        run_pk = st.register_run(f['dir'], w0, f['ts'], C['rc_pk'], engine_rev=_REV, walk=f['walk'],
                                 notes=f"{'RC' if f['rc'] else 'climb'} flip -> {f['dir']}", rollercoaster=f['rc'])
        st.log_events(run_pk, [{'ts': t, 'stage': e, 'tf': r, 'note': nt} for t, e, r, nt in f['ev']])
    db.disconnect()



def delegate_tf(etf):
    """[PRODUCER] The DELEGATE SPLIT (Joe 0727) — the one definition of which TF the provisional delegates to,
    given the exhaustion TF `etf`. Above the split, the -5 lookback applies (spec'd for TFs above the split);
    at or below it, the catch-many delegate. Floored at delegate_tf_floor either way. Every knob comes from
    rpl_config (no hardcoding); _climb_to_prov calls this, build_delsweep sweeps CATCHMANY through it."""
    return max(DELFLOOR, (etf - DELOFF) if etf > XPRED_THRESH else CATCHMANY)


def _climb_to_prov(bias, conf_i, xpred_thresh=None, xpred_band=None):
    """[extract-method, Joe 0727] The climb->provisional half of _climb_flip (was inline lines 184-202), lifted to
    module level so the bp50 RPL interception can run it from an ARBITRARY fire bar. BEHAVIOR-IDENTICAL to the
    original inline body (proven by the run_chain flip regression). Reads module L0 + globals; causal (only bars
    <= each cadence bar). Returns (ict, dTF, ev): ict/dTF = None if the climb dead-ends (cand but no delegate
    reversal) or never exhausts; ev = r-pred ladder + x-cross-pred + flip_provisional. The s30 finisher is the
    CALLER's job (kept in _climb_flip for the sweep; bp50 discards it and uses rpl_fin_6of9 instead)."""
    if xpred_thresh is None: xpred_thresh = XPRED_THRESH      # 0727: knobs now live in rpl_config, not a per-call
    if xpred_band is None:   xpred_band = XPRED_BAND          # opt-in default — one home, no None branch (SRP)
    L = L0; S = L['src']; ts = L['ts']; E = L['E']; P = L['P']; s2r = L['s2r']; ei = L['ei']
    fxB = L['fx_bull']; fxb = L['fx_bear']
    p = _polar(bias); fx = fxB if p['BULL'] else fxb
    # Joe 0731: the x/r cancel, propagated from build_rplwalk2.rp_matrix into the LIVE climb. A
    # predict_breach state survives its own invalidation - x can cross back through r while P still reads
    # CS - which kept a spent TF participating (s69: an 8.2-min r-pred at 0518 20:42 still counted at the
    # 0520 10:26 exhaustion, 37.75 h later). The run is now a latch: set on the predict rising edge, reset
    # by the polarity-matched cross already in `fx`. oob_climb is NOT cancelled - r out of bounds is a
    # fact, not a prediction. Cached on L0 so a rebuild invalidates it.
    # NOT propagated: the clean/dirty gate. It needs the applied-exhaustion bars, which this function has
    # no causal access to in batch - see rpred_spec.md §6 and task #25.
    _lv = L.setdefault('_rpred_live', {})
    if bias not in _lv:
        _lv[bias] = {TF: _latch_with_reset((lambda q: q & ~np.r_[False, q[:-1]])(P[TF] == p['CS']),
                                           np.asarray(fx[TF], bool)) for TF in TFS}
    live = _lv[bias]
    rpred = lambda TF, i: bool(live[TF][i]) or p['oob_climb'](E[TF]['r'][i])
    CONF = int(ts[conf_i]); cadence = ei[ts[ei] > CONF]
    rung = 3; prev_mi = conf_i; ev = []
    for i in cadence:
        hi = max([TF for TF in TFS if TF > rung and rpred(TF, i)], default=rung)
        if hi > rung:
            mode = 'breach' if p['oob_climb'](E[hi]['r'][i]) else 'predict'
            ev.append((int(ts[i]), 'r-pred', hi, f'by s{rung} ({mode})')); rung = hi
        w = np.arange(prev_mi + 1, i + 1); cand = []
        _lo = max(FLOOR, rung - xpred_band) if rung >= xpred_thresh else FLOOR
        for tf in range(rung, _lo - 1, -1):                # Joe 0726: rung>=thresh -> only TFs >= rung-band (opt-in)
            if len(w):
                cb = w[fx[tf][w] & p['near_ib'](E[tf]['r'][w]) & p['s2r_es'](s2r[w])]
                for k in cb: cand.append((int(k), tf))
        prev_mi = i
        if cand:
            cand.sort(); xki, etf = cand[0]; xt = int(ts[xki])
            ev.append((xt, 'x-cross-pred', etf, f'r={E[etf]["r"][xki]:.0f} x={E[etf]["x"][xki]:.0f} s2r={s2r[xki]:.0f} EXHAUST cur=s{rung}'))
            dTF = delegate_tf(etf); rD = E[dTF]['r']; xD = E[dTF]['x']      # delegate split (SRP: rule lives in the producer)
            conf = S.causal.cross_wob(xD - rD, 0.0, p['WOB_DIR'], WOBN); fe = np.flatnonzero((conf & ~np.roll(conf, 1)) & (ts >= xt))
            if len(fe):
                ict = int(fe[0]); ct = int(ts[ict]); ev.append((ct, 'flip_provisional', dTF, f"{p['FLIP'].upper()}: exh s{etf} -> del s{dTF}"))
                return ict, dTF, ev
            return None, None, ev                          # cand but delegate never reversed -> dead-end (break)
    return None, None, ev                                  # no exhaustion in the cadence -> no flip


def run_chain(seed_bias='bear', seed_start=None, depth=None, dwell=None, tee=False, persist=None, end=None,
              xpred_thresh=None, xpred_band=None):
    # Joe 0726 (past-50 RPL integration, OPT-IN — default None = unchanged; the sweep passes neither so it's untouched):
    #   when the climb rung (current_tf) >= xpred_thresh, restrict the x-cross-pred search to TFs >= rung - xpred_band,
    #   so a granular low TF can't win the earliest-bar sort and prematurely trigger. Both are knobs to sweep.
    """Auto-walk the whole day's flip chain from ONE seed (confirmed bias + start). Every flip is first-class:
    an s2-cycle ROLLERCOASTER reversal (gcs5-timed, no pyramid) or an s8-CLIMB flip (s30-timed, pyramid ok).
    Each gets its own MMDD_NN id (NN resets per UTC day; MMDD_01 = first flip of the day) + rr_rollercoaster tag,
    and emits x-cross-pred -> flip_provisional -> flip_finisher. Emerging/causal only. Returns flip dicts.
    persist: refresh rpl_run/rpl_event for the days walked; default = tee (a reported run persists)."""
    if depth is None: depth = LATCH_DEPTH
    if dwell is None: dwell = LATCH_DWELL
    if seed_start is None: seed_start = _ms(21, 32, 0, day=11)
    L = L0; S = L['src']; ts = L['ts']; idxn = L['idxn']; E = L['E']; P = L['P']; s2r = L['s2r']
    s30r_ = L['s30r_']; s30M_ = L['s30M_']; s30x_ = L['s30x_']; s30m_ = L['s30m_']
    g5r = L['g5r']; g5m = L['g5m']; g5x = L['g5x']; ei = L['ei']; s1r = E[1]['r']
    fxB = L['fx_bull']; fxb = L['fx_bear']   # precomputed fcross(x-r) per polarity (BULL=dn, BEAR=up)

    def _rc_flip(cur, io, otf):
        """s2-cycle reversal -> RC flip: x-cross-pred(exhaustion) -> flip_provisional(delegate) -> flip_finisher(gcs5)."""
        pc = _polar(cur); rev = 'bear' if cur == 'bull' else 'bull'
        dTF = max(DELFLOOR, otf - DELOFF); xD = E[dTF]['x']; rD = E[dTF]['r']
        ev = [(int(ts[io]), 'x-cross-pred', otf, f'r={E[otf]["r"][io]:.0f} x={E[otf]["x"][io]:.0f} s2r={s2r[io]:.0f} EXHAUST s{otf}')]
        conf = S.causal.cross_wob(xD - rD, 0.0, pc['WOB_DIR'], WOBN); fe = np.flatnonzero((conf & ~np.roll(conf, 1)) & (idxn >= io))
        rio = int(fe[0]) if len(fe) else io
        ev.append((int(ts[rio]), 'flip_provisional', dTF, f'{rev.upper()}: exh s{otf} -> del s{dTF}'))
        ex = g5x[ei]; em = g5m[ei]; roob = pc['oob_climb'](g5r[ei])   # gcs5 finisher: LATCH gcs5r OOB from the provisional,
        latch = np.maximum.accumulate((roob & (ei > rio)).astype(np.int8)).astype(bool)  # fire at the first flip-dir gcs5x*gcs5m cross while latched
        gate_ev = pc['fcross'](ex - em) & latch & (ei > rio)
        gc = np.flatnonzero(gate_ev); rev_i = int(ei[gc[0]]) if len(gc) else rio
        ev.append((int(ts[rev_i]), 'flip_finisher', 1, f'RC gcs5 {cur}->{rev} s{otf}exh'))
        return rev_i, rev, ev

    def _climb_flip(bias, conf_i):
        """s8 climb -> r-pred ladder -> x-cross-pred -> flip_provisional (via module-level _climb_to_prov, Joe 0727
        extract-method) -> flip_finisher(s30). The climb->provisional is now shared with the bp50 RPL interception;
        the s30 finisher below is UNCHANGED and stays on the sweep's path."""
        p = _polar(bias); BULL = p['BULL']; oob_supp = p['oob_climb_m']
        ict, dTF, ev = _climb_to_prov(bias, conf_i, xpred_thresh, xpred_band); flip_i = None
        if ict is not None:
            xc = p['fcross'](s30x_ - s30m_); xc_l = np.maximum.accumulate((xc & (idxn >= ict)).astype(np.int8)).astype(bool)
            lvl = (LO - depth) if not BULL else (HI + depth); wdir = -1 if not BULL else 1
            held = S.causal.cross_wob(s30M_, lvl, wdir, dwell)
            latch = np.maximum.accumulate((held & (idxn >= ict)).astype(np.int8)).astype(bool)
            nb = (HI - FIN_S30R_SLIP) if BULL else (LO + FIN_S30R_SLIP)
            near_h = S.causal.cross_wob(s30r_, nb, 1 if BULL else -1, FIN_NEAR_DWELL)
            ons = (s1r > HI - FIN_S1R_SLIP) if BULL else (s1r < LO + FIN_S1R_SLIP)
            ff = np.flatnonzero(xc_l & oob_supp(s30m_) & latch & near_h & ons & (idxn >= ict))
            if len(ff):
                flip_i = int(ff[0])
                ev.append((int(ts[flip_i]), 'flip_finisher', 1, f'FIN x*m OOB{"LO" if not BULL else "HI"} s30r{s30r_[flip_i]:.0f} s1r{s1r[flip_i]:.0f} d{depth}/w{dwell}'))
        return flip_i, p['FLIP'], ev

    cur = seed_bias; cst_i = int(np.searchsorted(ts, seed_start)); flips = []; trend = seed_bias
    _end = end if end is not None else end_ms
    while int(ts[cst_i]) < _end:
        pc = _polar(cur); cs = pc['CS']
        counter = (cur != trend)                          # this leg is a counter-trend RC reversal
        exh = None                                        # (a) s1/s2 exhaustion-against-cur -> RC reversal
        fxsel = fxB if pc['BULL'] else fxb
        for tf in (1, 2):
            fxt = fxsel[tf]
            hit = np.flatnonzero(fxt & pc['near_ib'](E[tf]['r']) & pc['s2r_es'](s2r) & (idxn > cst_i))
            if len(hit) and (exh is None or int(hit[0]) < exh[0]): exh = (int(hit[0]), tf)
        rp = None                                         # (b) s3..s8 r-pred-cur -> climb cur
        for tf in range(3, 9):
            hit = np.flatnonzero(((P[tf] == cs) | pc['oob_climb'](E[tf]['r'])) & (idxn > cst_i))
            if len(hit) and (rp is None or int(hit[0]) < rp[0]): rp = (int(hit[0]), tf)
        rpo = None                                        # (c) 0720 option 1: on a COUNTER-trend leg, trend re-BREACH = causal exit
        if counter:                                       # breach-only (not predict): a velocity-predict spike whipsaws a good
            pt = _polar(trend)                            # counter-trend trade out. exit_tf_floor=4 keeps s3 in the s2-cycle: s3
            for tf in range(EXIT_TF_FLOOR, 9):            # is fast enough to blip-breach (09:27) and blur the s2/s8 boundary.
                hit = np.flatnonzero(pt['oob_climb'](E[tf]['r']) & (idxn > cst_i))
                if len(hit) and (rpo is None or int(hit[0]) < rpo[0]): rpo = (int(hit[0]), tf)
        cands = [(exh[0], 'exh', exh) if exh else None, (rp[0], 'clm', rp) if rp else None, (rpo[0], 'exit', rpo) if rpo else None]
        cands = [c for c in cands if c]
        if not cands: break
        cands.sort(); trig_i, kind, sig = cands[0]
        if RPRED_VETO and kind == 'exh' and any(                       # RPRED VETO (Joe 0725): don't take the s1/s2
                (P[tf][trig_i] == cs) or pc['oob_climb'](E[tf]['r'][trig_i]) for tf in range(3, 9)):  # exhaustion
            cst_i = trig_i; continue                                   # reversal while ANY s3-8 TF still r-preds cur's
        #                                                                continuation. Mechanic only — no knobs touched.
        if kind == 'exh':
            io, otf = sig; fi, ndir, ev = _rc_flip(cur, io, otf); rc = 1
        elif kind == 'exit':                              # trend re-confirmed -> exit the counter-trend leg, back to trend
            io, rtf = sig; fi = io; ndir = trend; rc = 1
            ev = [(int(ts[io]), 'flip_finisher', rtf, f'RC exit: s{rtf} r-pred {trend} closes {cur}')]
        else:
            io, rtf = sig; fi, ndir, ev = _climb_flip(cur, io); rc = 0
            if fi is None: break
            trend = ndir                                  # a climb flip sets the trend
        flips.append(dict(i=fi, ts=int(ts[fi]), dir=ndir, rc=rc, ev=sorted(ev, key=lambda z: z[0])))
        cur = ndir; cst_i = fi
    daycount = {}
    for f in flips:
        dt = dtm.datetime.fromtimestamp(f['ts'] / 1000, tz=timezone.utc)
        key = (dt.month, dt.day)                       # per calendar-day counter (month+day, no cross-month collision)
        daycount[key] = daycount.get(key, 0) + 1
        f['walk'] = f"{dt.month:02d}{dt.day:02d}_{daycount[key]:02d}"   # MMDD_NN; MMDD_01 = first flip of the day
    if tee:
        print(f"  {'walk':>6} {'time':>8} {'dir':>4} {'kind':>5}")
        for f in flips: print(f"  {f['walk']:>6} {fmt(f['ts']):>8} {f['dir']:>4} {'RC' if f['rc'] else 'climb':>5}")
    if tee if persist is None else persist:
        _persist_chain(flips)
        if tee: print(f"  persisted {len(flips)} flips ({sum(f['rc'] for f in flips)} RC)")
    return flips
