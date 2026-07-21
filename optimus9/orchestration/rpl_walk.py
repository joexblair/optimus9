"""rpl auto-chain: walk the whole day's flip stream from ONE seed. IMPORTABLE.
Config (DB baseline) + jig warmup are loaded ONCE at import; run_chain(seed_bias, seed_start) walks the
cached line arrays flip-to-flip. Emerging lines only (causal — what o9-live sees). See docs/rpl_flow_spec.md.
Line/knob source = rpl_config 'baseline'.

Each flip is first-class (own DD_NN id, rr_rollercoaster tag): an s2-cycle ROLLERCOASTER reversal (counter
to the trend, gcs5-timed, no pyramid) or an s8-CLIMB flip (trend, s30-timed). A counter-trend leg exits when
the trend r-preds again (option 1). DD_01 = first flip of the UTC day."""
import numpy as np, datetime as dtm, hashlib
from datetime import timezone
from optimus9 import DatabaseManager
from optimus9.config import get_db_config
from optimus9.analysis.jig import kline, bbline
from optimus9.compute.breaching_line import predict_breach
from optimus9.db.rpl_event_store import RplEventStore
from optimus9.orchestration.rpl_cache import cache_jig

# --- config (once) ---
_db = DatabaseManager(**get_db_config()); _db.connect(); _st = RplEventStore(_db); C = _st.load_config('baseline'); _db.disconnect()
HI, LO = C['boundary']['hi'], C['boundary']['lo']; FH, FL = C['fence']['fh'], C['fence']['fl']; LN = C['lines']
DELOFF = C['delegate_offset']; WOBN = C['wob_n']; ANTI = C['anti']; BND4 = C['xcp_bnd_offset']; FLOOR = C['xcp_tf_floor']
LATCH_DEPTH = C['latch_depth']; LATCH_DWELL = C['latch_dwell']; DELFLOOR = C['delegate_tf_floor']
FIN_S30R_SLIP = C['finisher_s30r_boundary_slip']; FIN_NEAR_DWELL = C['finisher_s30r_near_dwell']; FIN_S1R_SLIP = C['finisher_s1r_boundary_slip']
EXIT_TF_FLOOR = C['exit_tf_floor']
CONFIRM_TOL = C['s1s2_confirm_tol_ms']; GCS5_RTOL = C['gcs5_r_tol']
TFS = list(range(1, C['tf_ceiling'] + 1)); end_ms = int(dtm.datetime(2026, 7, 13, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
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
    s30r_ = np.asarray(src.W.line('s30r'), float); s30M_ = np.asarray(src.W.line('s30M'), float)
    s30x_ = np.asarray(src.W.line('s30x'), float); s30m_ = np.asarray(src.W.line('s30m'), float)
    return dict(src=src, ts=ts, n=len(ts), idxn=np.arange(len(ts)), ei=np.flatnonzero(evt), E=E, P=P, s2r=E[2]['r'],
                s1x=np.asarray(src.W.line('s1x'), float), s1m=np.asarray(src.W.line('s1m'), float),
                s30r_=s30r_, s30M_=s30M_, s30x_=s30x_, s30m_=s30m_,
                g5r=np.asarray(src.W.line('gcs5r'), float), g5m=np.asarray(src.W.line('gcs5m'), float), g5x=np.asarray(src.W.line('gcs5x'), float),
                Ps30=predict_breach(s30r_, s30m_, s30M_, HI, LO, FH, FL, 0.0))

J = cache_jig(end_ms, 40, 600, _ovr)
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

def _persist_chain(flips):
    """Refresh rpl_run/rpl_event for every day the chain touched: drop that day's prior runs (the chain
    renumbers), then register each flip as its own DD_NN run + log its event stream (rr_rollercoaster set)."""
    if not flips:
        return
    db = DatabaseManager(**get_db_config()); db.connect(); st = RplEventStore(db)
    days = {f['walk'][:2] for f in flips}
    for r in db.execute("SELECT rr_pk, rr_walk FROM rpl_run WHERE rr_walk IS NOT NULL", fetch=True):
        if r['rr_walk'][:2] in days:
            db.execute("DELETE FROM rpl_run WHERE rr_pk=%s", (r['rr_pk'],))
    for f in flips:
        w0 = f['ev'][0][0] if f['ev'] else f['ts']
        run_pk = st.register_run(f['dir'], w0, f['ts'], C['rc_pk'], engine_rev=_REV, walk=f['walk'],
                                 notes=f"{'RC' if f['rc'] else 'climb'} flip -> {f['dir']}", rollercoaster=f['rc'])
        st.log_events(run_pk, [{'ts': t, 'stage': e, 'tf': r, 'note': nt} for t, e, r, nt in f['ev']])
    db.disconnect()



def run_chain(seed_bias='bear', seed_start=None, depth=None, dwell=None, tee=False, persist=None):
    """Auto-walk the whole day's flip chain from ONE seed (confirmed bias + start). Every flip is first-class:
    an s2-cycle ROLLERCOASTER reversal (gcs5-timed, no pyramid) or an s8-CLIMB flip (s30-timed, pyramid ok).
    Each gets its own DD_NN id (NN resets per UTC day; DD_01 = first flip of the day) + rr_rollercoaster tag,
    and emits x-cross-pred -> flip_provisional -> flip_finisher. Emerging/causal only. Returns flip dicts.
    persist: refresh rpl_run/rpl_event for the days walked; default = tee (a reported run persists)."""
    if depth is None: depth = LATCH_DEPTH
    if dwell is None: dwell = LATCH_DWELL
    if seed_start is None: seed_start = _ms(21, 32, 0, day=11)
    L = L0; S = L['src']; ts = L['ts']; idxn = L['idxn']; E = L['E']; P = L['P']; s2r = L['s2r']
    s30r_ = L['s30r_']; s30M_ = L['s30M_']; s30x_ = L['s30x_']; s30m_ = L['s30m_']
    g5r = L['g5r']; g5m = L['g5m']; g5x = L['g5x']; ei = L['ei']; s1r = E[1]['r']

    def _rc_flip(cur, io, otf):
        """s2-cycle reversal -> RC flip: x-cross-pred(exhaustion) -> flip_provisional(delegate) -> flip_finisher(gcs5)."""
        pc = _polar(cur); rev = 'bear' if cur == 'bull' else 'bull'
        dTF = max(DELFLOOR, otf - DELOFF); xD = E[dTF]['x']; rD = E[dTF]['r']
        ev = [(int(ts[io]), 'x-cross-pred', otf, f'r={E[otf]["r"][io]:.0f} x={E[otf]["x"][io]:.0f} s2r={s2r[io]:.0f} EXHAUST s{otf}')]
        conf = S.causal.cross_wob(xD - rD, 0.0, pc['WOB_DIR'], WOBN); fe = np.flatnonzero((conf & ~np.roll(conf, 1)) & (idxn >= io))
        rio = int(fe[0]) if len(fe) else io
        ev.append((int(ts[rio]), 'flip_provisional', dTF, f'{rev.upper()}: exh s{otf} -> del s{dTF}'))
        ex = g5x[ei]; em = g5m[ei]; roob = pc['oob_climb'](g5r[ei]); oob_tol = roob.copy()
        for _w in range(1, GCS5_RTOL): oob_tol[_w:] |= roob[:-_w]
        gate_ev = pc['fcross'](ex - em) & oob_tol & (ei > rio)
        gc = np.flatnonzero(gate_ev); rev_i = int(ei[gc[0]]) if len(gc) else rio
        ev.append((int(ts[rev_i]), 'flip_finisher', 1, f'RC gcs5 {cur}->{rev} s{otf}exh'))
        return rev_i, rev, ev

    def _climb_flip(bias, conf_i):
        """s8 climb -> r-pred ladder -> x-cross-pred(exhaustion) -> flip_provisional -> flip_finisher(s30)."""
        p = _polar(bias); BULL = p['BULL']; oob_supp = p['oob_climb_m']
        fx = {tf: p['fcross'](E[tf]['x'] - E[tf]['r']) for tf in TFS}
        rpred = lambda TF, i: (P[TF][i] == p['CS']) or p['oob_climb'](E[TF]['r'][i])
        CONF = int(ts[conf_i]); cadence = ei[ts[ei] > CONF]
        rung = 3; prev_mi = conf_i; ev = []; flip_i = None
        for i in cadence:
            hi = max([TF for TF in TFS if TF > rung and rpred(TF, i)], default=rung)
            if hi > rung:
                mode = 'breach' if p['oob_climb'](E[hi]['r'][i]) else 'predict'
                ev.append((int(ts[i]), 'r-pred', hi, f'by s{rung} ({mode})')); rung = hi
            w = np.arange(prev_mi + 1, i + 1); cand = []
            for tf in range(rung, FLOOR - 1, -1):
                if len(w):
                    cb = w[fx[tf][w] & p['near_ib'](E[tf]['r'][w]) & p['s2r_es'](s2r[w])]
                    for k in cb: cand.append((int(k), tf))
            prev_mi = i
            if cand:
                cand.sort(); xki, etf = cand[0]; xt = int(ts[xki])
                ev.append((xt, 'x-cross-pred', etf, f'r={E[etf]["r"][xki]:.0f} x={E[etf]["x"][xki]:.0f} s2r={s2r[xki]:.0f} EXHAUST cur=s{rung}'))
                dTF = max(DELFLOOR, etf - DELOFF); rD = E[dTF]['r']; xD = E[dTF]['x']
                conf = S.causal.cross_wob(xD - rD, 0.0, p['WOB_DIR'], WOBN); fe = np.flatnonzero((conf & ~np.roll(conf, 1)) & (ts >= xt))
                if len(fe):
                    ict = int(fe[0]); ct = int(ts[ict]); ev.append((ct, 'flip_provisional', dTF, f"{p['FLIP'].upper()}: exh s{etf} -> del s{dTF}"))
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
                break  # first exhaustion ends the climb (flip, or dead-end -> chain stops)
        return flip_i, p['FLIP'], ev

    cur = seed_bias; cst_i = int(np.searchsorted(ts, seed_start)); flips = []; trend = seed_bias
    while int(ts[cst_i]) < end_ms:
        pc = _polar(cur); cs = pc['CS']
        counter = (cur != trend)                          # this leg is a counter-trend RC reversal
        exh = None                                        # (a) s1/s2 exhaustion-against-cur -> RC reversal
        for tf in (1, 2):
            fxt = pc['fcross'](E[tf]['x'] - E[tf]['r'])
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
        cands.sort(); _, kind, sig = cands[0]
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
        d = dtm.datetime.fromtimestamp(f['ts'] / 1000, tz=timezone.utc).day
        daycount[d] = daycount.get(d, 0) + 1
        f['walk'] = f"{d:02d}_{daycount[d]:02d}"
    if tee:
        print(f"  {'walk':>6} {'time':>8} {'dir':>4} {'kind':>5}")
        for f in flips: print(f"  {f['walk']:>6} {fmt(f['ts']):>8} {f['dir']:>4} {'RC' if f['rc'] else 'climb':>5}")
    if tee if persist is None else persist:
        _persist_chain(flips)
        if tee: print(f"  persisted {len(flips)} flips ({sum(f['rc'] for f in flips)} RC)")
    return flips
