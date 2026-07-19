"""rpl s8-cycle + s30-finishing walk, DIRECTION-PARAMETERIZED and IMPORTABLE.
Config (DB baseline) + jig warmup are loaded ONCE at import; run_walk(walk, depth, dwell) is a pure
function over the cached line arrays so the sweep reuses ONE code path (no fork). Emerging lines only
(causal — what o9-live sees). See docs/rpl_flow_spec.md. Line/knob source = rpl_config 'baseline'.

A walk = one flip cycle: confirmed BIAS (leg climbed) -> hunt the opposite flip.
  12_01 bear leg -> bull flip (bottom)   12_02 bull leg -> bear flip (top)   12_03 bear leg -> bull flip."""
import numpy as np, datetime as dtm
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
LATCH_DEPTH = C['latch_depth']; LATCH_DWELL = C['latch_dwell']
TFS = list(range(2, 46)); end_ms = int(dtm.datetime(2026, 7, 12, 7, 0, tzinfo=timezone.utc).timestamp() * 1000)
fmt = lambda t: dtm.datetime.fromtimestamp(int(t) / 1000, timezone.utc).strftime('%H:%M:%S')

def _mk(nm, tf, t): return kline(nm, tf, k_len=t['k_len'], rsi=t['rsi'], stc=t['stc'], src=t['src']) if t['kind'] == 'kline' else bbline(nm, tf, length=t['length'], mult=t['mult'], src=t['src'])
_ovr = {}
for _TF in TFS:
    for _k in ('r', 'x', 'm', 'M'): _ovr.update(_mk(f'{_k}{_TF}', _TF, LN[_k]))
for _nm in ('s1x', 's1m'): _ovr.update(_mk(_nm, 1.0, LN[_nm]))
for _nm in ('s30r', 's30M'): _ovr.update(_mk(_nm, 0.5, LN[_nm]))
_ovr.update(_mk('s30x', 0.5, LN['x'])); _ovr.update(_mk('s30m', 0.5, LN['m']))

# --- warmup (once, cached) + walk-independent arrays ---
J = cache_jig(end_ms, 40, 600, _ovr)
ts = np.asarray(J.ts, np.int64); n = len(ts); idxn = np.arange(n)
E = {TF: {k: np.asarray(J.W.line(f'{k}{TF}'), float) for k in ('r', 'x', 'm', 'M')} for TF in TFS}
P = {TF: predict_breach(E[TF]['r'], E[TF]['m'], E[TF]['M'], HI, LO, FH, FL, 0.0) for TF in TFS}
s2r = E[2]['r']
s1x = np.asarray(J.W.line('s1x'), float); s1m = np.asarray(J.W.line('s1m'), float)
s30r_ = np.asarray(J.W.line('s30r'), float); s30M_ = np.asarray(J.W.line('s30M'), float)
s30x_ = np.asarray(J.W.line('s30x'), float); s30m_ = np.asarray(J.W.line('s30m'), float)
Ps30 = predict_breach(s30r_, s30m_, s30M_, HI, LO, FH, FL, 0.0)

def _ms(h, m, s=0, day=12): return int(dtm.datetime(2026, 7, day, h, m, s, tzinfo=timezone.utc).timestamp() * 1000)
WALKS = {  # walk -> (confirmed BIAS = leg climbed, walk start ms = the prior flip)
    '12_01': ('bear', _ms(21, 32, 0, day=11)),
    '12_02': ('bull', _ms(1, 2, 35)),
    '12_03': ('bear', _ms(3, 30, 55)),   # starts at 12_02's bear flip -> hunt next bull flip (bottom)
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

def run_walk(walk, depth=None, dwell=None, tee=False):
    """Run one flip walk. depth/dwell default to the DB baseline; the sweep overrides them.
    Returns (ev, meta) where ev=[(ts,stage,tf,note)...] and meta={bias,conf,flip,flip_ts,rc_pk}."""
    if depth is None: depth = LATCH_DEPTH
    if dwell is None: dwell = LATCH_DWELL
    bias, CONF = WALKS[walk]; p = _polar(bias)
    BULL = p['BULL']; FS = p['FS']; oob_supp = p['oob_climb_m']  # supporting lines OOB on the PROFITABLE (exhausted-leg) side
    fx = {tf: p['fcross'](E[tf]['x'] - E[tf]['r']) for tf in TFS}
    rpred = lambda TF, i: (P[TF][i] == p['CS']) or p['oob_climb'](E[TF]['r'][i])
    crx = np.concatenate(([False], np.sign(s1x - s1m)[1:] != np.sign(s1x - s1m)[:-1]))
    mk_idx = np.flatnonzero(crx & p['oob_climb_m'](s1m) & (ts > CONF))
    ev = []; flip_ts = None; rung = 3; prev_mi = int(np.searchsorted(ts, CONF)); flipped = False
    if tee: print(f"  s8-cycle walk {walk}  BIAS={bias} -> hunt {p['FLIP'].upper()} flip  start={fmt(CONF)}  depth={depth} dwell={dwell}")
    for i in mk_idx:
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
            dTF = max(2, etf - DELOFF); rD = np.asarray(J.W.line(f'r{dTF}'), float); xD = np.asarray(J.W.line(f'x{dTF}'), float)
            conf = J.causal.cross_wob(xD - rD, 0.0, p['WOB_DIR'], WOBN); fe = np.flatnonzero((conf & ~np.roll(conf, 1)) & (ts >= xt))
            if len(fe):
                ict = int(fe[0]); ct = int(ts[ict]); ev.append((ct, 'flip_provisional', dTF, f"{p['FLIP'].upper()}: exh s{etf} -> del s{dTF}"))
                rf = np.flatnonzero((Ps30 == FS) & (ts >= ct))
                if len(rf):
                    t0 = int(rf[0]); xc = p['fcross'](s30x_ - s30m_)
                    # s30Mage latch = held PAST-DEPTH for DWELL bars (cross_wob), then latched from the provisional
                    lvl = (LO - depth) if not BULL else (HI + depth); wdir = -1 if not BULL else 1
                    held = J.causal.cross_wob(s30M_, lvl, wdir, dwell)
                    latch = np.maximum.accumulate((held & (idxn >= ict)).astype(np.int8)).astype(bool)
                    ff = np.flatnonzero(xc & oob_supp(s30m_) & latch & (idxn >= t0))
                    if len(ff):
                        flip_ts = int(ts[ff[0]])
                        ev.append((flip_ts, 'bias_trend_flip', 1, f'FIN s30r {"HI" if FS>0 else "LO"}@{fmt(ts[t0])} x*m OOB{"LO" if not BULL else "HI"} d{depth}/w{dwell}'))
                flipped = True
    ev = sorted(ev, key=lambda z: z[0])
    if tee:
        print(f"  {'time':>8} {'event':>16} {'tf':>3}  note")
        for t, e, r, nt in ev: print(f"  {fmt(t):>8} {e:>16} {r:>3}  {nt}")
        if not flipped: print(f"  (no flip; current_tf s{rung})")
    return ev, dict(bias=bias, conf=CONF, flip=p['FLIP'], flip_ts=flip_ts, rc_pk=C['rc_pk'])
