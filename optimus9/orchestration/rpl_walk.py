"""rpl s8-cycle + s30-finishing walk, DIRECTION-PARAMETERIZED and IMPORTABLE.
Config (DB baseline) + jig warmup are loaded ONCE at import; run_walk(walk, depth, dwell) is a pure
function over the cached line arrays so the sweep reuses ONE code path (no fork). Emerging lines only
(causal — what o9-live sees). See docs/rpl_flow_spec.md. Line/knob source = rpl_config 'baseline'.

A walk = one flip cycle: confirmed BIAS (leg climbed) -> hunt the opposite flip.
  12_01 bear leg -> bull flip (bottom)   12_02 bull leg -> bear flip (top)   12_03 bear leg -> bull flip."""
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
    """Read every line the flow needs from a line-source (JigCache or jig) into a dict. The sweep passes a
    src built with swept line configs; run_walk uses whichever src it's given. Line production stays in the
    jig/BiasWindow (SRP) — this only assembles the arrays + the derived predict_breach series."""
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
WALKS = {  # walk -> (confirmed BIAS = leg climbed, walk start ms = the prior flip)
    '12_01': ('bear', _ms(21, 32, 0, day=11)),
    '12_02': ('bull', _ms(1, 2, 35)),
    '12_03': ('bear', _ms(3, 30, 55)),   # starts at 12_02's bear flip -> hunt next bull flip (bottom)
    '12_04': ('bull', _ms(4, 54, 40)),   # starts at 12_03's bull flip (ceiling-90) -> hunt next bear flip (top)
    '12_05': ('bear', _ms(8, 52, 45)),   # starts at 12_04's bear flip -> hunt next bull flip (bottom)
}

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

def _persist_run(walk, ev, meta):
    """Refresh rpl_run/rpl_event for this walk: drop prior runs, register + log the fresh stream."""
    db = DatabaseManager(**get_db_config()); db.connect(); st = RplEventStore(db)
    for r in db.execute("SELECT rr_pk FROM rpl_run WHERE rr_walk=%s", (walk,), fetch=True):
        db.execute("DELETE FROM rpl_run WHERE rr_pk=%s", (r['rr_pk'],))
    b = ev[-1][0] if ev else meta['conf']
    run_pk = st.register_run(meta['flip'], meta['conf'], b, meta['rc_pk'], engine_rev=_REV, walk=walk,
                             notes=f"{meta['bias']} climb -> {fmt(meta['flip_ts']) if meta['flip_ts'] else 'no'} flip")
    st.log_events(run_pk, [{'ts': t, 'stage': e, 'tf': r, 'note': nt} for t, e, r, nt in ev])
    db.disconnect(); return run_pk


def run_walk(walk, depth=None, dwell=None, tee=False, src=None, persist=None):
    """Run one flip walk. depth/dwell default to the DB baseline; the sweep overrides them. src = a line
    source (JigCache/jig) with swept configs; None => the module baseline L0. Returns (ev, meta).
    persist: refresh rpl_event for this walk on completion; default = tee (a reported run persists, a
    pure-compute/sweep call does not). Pass persist=False on a swept src to keep it side-effect-free."""
    if depth is None: depth = LATCH_DEPTH
    if dwell is None: dwell = LATCH_DWELL
    L = L0 if src is None else build_lines(src)
    S = L['src']; ts = L['ts']; idxn = L['idxn']; E = L['E']; P = L['P']; s2r = L['s2r']
    s1x = L['s1x']; s1m = L['s1m']; s30r_ = L['s30r_']; s30M_ = L['s30M_']; s30x_ = L['s30x_']; s30m_ = L['s30m_']; Ps30 = L['Ps30']
    g5r = L['g5r']; g5m = L['g5m']; g5x = L['g5x']; ei = L['ei']
    bias0, CONF = WALKS[walk]
    ev = []; flip_ts = None
    # --- STEP 2: s1/s2 direction cycle. NO timeout — watches from the flip until whichever fires FIRST:
    #     (a) an s1/s2 exhaustion (LTF x-cross-pred AGAINST the current dir; r at boundary + x-cross) -> close +
    #         OPEN THE OPPOSITE trade (reverse), re-watch from there; or
    #     (b) any s8-cycle TF (s3..s8) r-pred'd in the current dir -> s8 climb takes over from there.
    #     One is guaranteed, so no window is needed. (s1s2_confirm_tol_ms retired here.) ---
    cur = bias0; cst = CONF; reverses = 0
    while True:
        pc = _polar(cur); cs = pc['CS']; cst_i = int(np.searchsorted(ts, cst))
        exh = None  # (a) s1/s2 exhaustion against cur
        for tf in (1, 2):
            fxt = pc['fcross'](E[tf]['x'] - E[tf]['r'])
            hit = np.flatnonzero(fxt & pc['near_ib'](E[tf]['r']) & pc['s2r_es'](s2r) & (idxn > cst_i))
            if len(hit) and (exh is None or int(hit[0]) < exh[0]): exh = (int(hit[0]), tf)
        rp = None   # (b) s3..s8 r-pred in cur dir (predict OR breach)
        for tf in range(3, 9):
            rpt = (P[tf] == cs) | pc['oob_climb'](E[tf]['r'])
            hit = np.flatnonzero(rpt & (idxn > cst_i))
            if len(hit) and (rp is None or int(hit[0]) < rp[0]): rp = (int(hit[0]), tf)
        if exh is not None and (rp is None or exh[0] <= rp[0]):
            io, otf = exh                                             # exhaustion (x-cross-pred) = step 1
            dTF = max(DELFLOOR, otf - DELOFF)                         # delegate: TF2 -> TF1 (floor=1)
            xD = E[dTF]['x']; rD = E[dTF]['r']                        # step 2: delegate x*r wob cross (flip dir), like the main flip
            conf = S.causal.cross_wob(xD - rD, 0.0, pc['WOB_DIR'], WOBN); fe = np.flatnonzero((conf & ~np.roll(conf, 1)) & (idxn >= io))
            rio = int(fe[0]) if len(fe) else io
            # step 3: gcs5 finisher FOLLOWS the delegate cross, on EVENT bars — FIRST flip-dir gcs5x*gcs5m cross with
            # gcs5r OOB (exhausted-leg side) within the last GCS5_RTOL event bars (r drops out as the top rolls over).
            ex = g5x[ei]; em = g5m[ei]; roob = pc['oob_climb'](g5r[ei]); oob_tol = roob.copy()
            for _w in range(1, GCS5_RTOL): oob_tol[_w:] |= roob[:-_w]   # r OOB within GCS5_RTOL event bars
            gate_ev = pc['fcross'](ex - em) & oob_tol & (ei > rio)      # fcross vs previous EVENT bar
            gc = np.flatnonzero(gate_ev); rev_i = int(ei[gc[0]]) if len(gc) else rio
            rev = 'bear' if cur == 'bull' else 'bull'
            ev.append((int(ts[rev_i]), 'dir_reverse', dTF, f's{otf} exh -> del s{dTF} -> gcs5 -> close {cur}, open {rev}'))
            cur = rev; cst = int(ts[rev_i]); reverses += 1
            if reverses <= 60: continue
            climb_bias = cur; climb_conf = cst; break
        elif rp is not None:
            io, rtf = rp; ev.append((int(ts[io]), 'dir_confirm', rtf, f's{rtf} r-pred {cur} -> s8 takes over'))
            climb_bias = cur; climb_conf = int(ts[io]); break
        else:
            climb_bias = cur; climb_conf = cst; ev.append((cst, 'dir_confirm', 1, f'{cur} (no signal to end of tape)')); break
    # --- s8 climb, from the confirmed direction/time ---
    bias = climb_bias; CONF = climb_conf; p = _polar(bias)
    BULL = p['BULL']; FS = p['FS']; oob_supp = p['oob_climb_m']  # supporting lines OOB on the PROFITABLE (exhausted-leg) side
    fx = {tf: p['fcross'](E[tf]['x'] - E[tf]['r']) for tf in TFS}
    rpred = lambda TF, i: (P[TF][i] == p['CS']) or p['oob_climb'](E[TF]['r'][i])
    # cadence = every EVENT bar (0720 look-ahead fix): the old s1x*s1m marker cadence had multi-min gaps, so the
    # look-back window (prev, now] could swallow an exhaustion cross detected minutes late but stamped early (back-dated).
    # Per-event-bar detection catches each cross at its true time — causal. (index-vs-event: use event bars, not the 5s grid.)
    cadence = ei[ts[ei] > CONF]
    rung = 3; prev_mi = int(np.searchsorted(ts, CONF)); flipped = False
    if tee: print(f"  s8-cycle walk {walk}  BIAS0={bias0} -> confirmed {bias} (rev {reverses}) -> hunt {p['FLIP'].upper()} flip  start={fmt(CONF)}  depth={depth} dwell={dwell}")
    for i in cadence:
        if flipped: break
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
                # finisher (0720): s30 r-pred pulled. Fire = FIRST bar from the provisional where ALL hold:
                #   x-cross latched (s30x*s30m), s30m OOB (supp side), s30Mage held past depth,
                #   s30r within slip of its boundary (dwell-held -> a real s30r cycle, not a blip), AND
                #   s1r within slip of ITS OWN boundary (the leg has reached its extreme, not a premature poke).
                xc = p['fcross'](s30x_ - s30m_); xc_l = np.maximum.accumulate((xc & (idxn >= ict)).astype(np.int8)).astype(bool)
                lvl = (LO - depth) if not BULL else (HI + depth); wdir = -1 if not BULL else 1
                held = S.causal.cross_wob(s30M_, lvl, wdir, dwell)
                latch = np.maximum.accumulate((held & (idxn >= ict)).astype(np.int8)).astype(bool)
                nb = (HI - FIN_S30R_SLIP) if BULL else (LO + FIN_S30R_SLIP)
                near_h = S.causal.cross_wob(s30r_, nb, 1 if BULL else -1, FIN_NEAR_DWELL)
                s1r = E[1]['r']; ons = (s1r > HI - FIN_S1R_SLIP) if BULL else (s1r < LO + FIN_S1R_SLIP)
                ff = np.flatnonzero(xc_l & oob_supp(s30m_) & latch & near_h & ons & (idxn >= ict))
                if len(ff):
                    flip_ts = int(ts[ff[0]])
                    ev.append((flip_ts, 'flip_finisher', 1, f'FIN x*m OOB{"LO" if not BULL else "HI"} s30r{s30r_[ff[0]]:.0f} s1r{s1r[ff[0]]:.0f} d{depth}/w{dwell}'))
                flipped = True
    ev = sorted(ev, key=lambda z: z[0])
    if tee:
        print(f"  {'time':>8} {'event':>16} {'tf':>3}  note")
        for t, e, r, nt in ev: print(f"  {fmt(t):>8} {e:>16} {r:>3}  {nt}")
        if not flipped: print(f"  (no flip; current_tf s{rung})")
    meta = dict(bias=bias, bias0=bias0, conf=WALKS[walk][1], climb_conf=CONF, flip=p['FLIP'], flip_ts=flip_ts, reverses=reverses, rc_pk=C['rc_pk'])
    if (tee if persist is None else persist) and src is None:
        run_pk = _persist_run(walk, ev, meta)
        if tee: print(f"  persisted walk {walk} run_pk={run_pk} events={len(ev)}")
    return ev, meta
