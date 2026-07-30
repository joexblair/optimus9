"""linelab — warm-cache line laboratory (Joe 0724).

Lines are cached PER-SPEC via rpl_cache.cache_jig_perline: adding a line only computes THAT line; the
px_smooth EVENT tape (ts/evt/pxs) is cached once. Every MAE is measured on px_smooth event bars with
find_pivots — the sweep's exact `_leg_net` basis (NOT lr_walk's raw-px). So numbers are bit-comparable to
the sweep / failscan / RC-RPL pines.

Register a line once (persists in linelab_lines.json); thereafter warm() reloads it instantly.

    import linelab as LL
    LL.register('hs60x', kind='bb', tf=60, length=4, mult=0.37)     # BBLine  (length|mult|src)
    LL.register('hh11r', kind='k',  tf=11, k_len=9, rsi=5, stc=11)  # KLine   (k_len|rsi|stc|src)
    cache, ets, epx, names = LL.warm()
    ents = LL.cross(cache, 'hs60x', 'hs60m', grid_ms=5000, wob=8, start=S, end=E)   # emerging cross
    rows = LL.mae(ets, epx, ents, swing_pct=1.0)                                    # px_smooth MAE @1%
"""
import json, os, numpy as np
from datetime import datetime, timezone
import optimus9.orchestration.rpl_walk as R
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.analysis.jig import kline, bbline
from optimus9.compute.swing_detect import find_pivots

END = int(datetime(2026, 6, 14, tzinfo=timezone.utc).timestamp() * 1000)   # tape end — build_rpl_6of9's JUNE_END / the R.L0 key
HOURS, WARMUP = 40, 600     # Joe 0727: the SAME cache key as J3/L0, so the whole chain (bp50 setup/trigger AND the RPL
#                             climb/delegate/finisher) runs on ONE tape. Span = hours + 2*warmup = 1240h, truncated by the
#                             kline_collection floor at 2026-04-28 06:34 -> 06-13 gets 45.96d warmup, the max the data allows.
#                             (52d is unreachable: 06-13 minus 52d = 04-22, five days before any data exists.)
#                             Was 07-13 / 1152|24 (Joe 0725, 48d matching sweep POOL_DAYS) — that gave 06-13 only 20.23d.
REG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'linelab_lines.json')

_DEFAULT = {
    'hs60x': {'kind': 'bb', 'tf': 60, 'length': 4, 'mult': 0.37, 'src': 'close'},
    'hs60m': {'kind': 'bb', 'tf': 60, 'length': 6, 'mult': 0.45, 'src': 'close'},
}

def _load():
    if os.path.exists(REG):
        return json.load(open(REG))
    json.dump(_DEFAULT, open(REG, 'w'), indent=1)
    return dict(_DEFAULT)

def register(name, kind, tf, src='close', **params):
    """Add/replace a line spec (persists). kind='bb' (length,mult) or 'k' (k_len,rsi,stc)."""
    reg = _load()
    reg[name] = {'kind': kind, 'tf': tf, 'src': src, **params}
    json.dump(reg, open(REG, 'w'), indent=1)
    return reg

def _ovr_of(name, s):
    if s['kind'] in ('k', 'kline'):
        return kline(name, s['tf'], k_len=s['k_len'], rsi=s['rsi'], stc=s['stc'], src=s.get('src', 'close'))
    return bbline(name, s['tf'], length=s['length'], mult=s['mult'], src=s.get('src', 'close'))

def warm(rebuild=False):
    """Build/reload the warm cache: returns (cache, ets, epx, names). ets/epx = px_smooth event tape."""
    reg = _load()
    ovr = {}
    for n, s in reg.items():
        ovr.update(_ovr_of(n, s))
    cache = cache_jig_perline(END, HOURS, WARMUP, ovr, pxs_cfg=R.PXS_CFG, rebuild=rebuild)
    ei = np.flatnonzero(cache.evt)
    return cache, cache.ts[ei], cache.pxs[ei], list(reg)

def evi(cache):
    """Event-bar indices (volume>0) — THE px_smooth event tape the sweep/live engine acts on (the index-vs-event
    gotcha, quirks_to_remember.md). Non-event 'filler' bars are invisible to the engine, so trigger detection must
    live on this tape, not the full 5s grid."""
    return np.flatnonzero(cache.evt)


def line(cache, name, events=True):
    """Line values. DEFAULT (Joe 0726) = px_smooth EVENT bars only (matches the engine / sweep / o9-live). Pass
    events=False for the raw full 5s grid (inspection only — NOT what gets traded)."""
    v = np.asarray(cache.W.line(name), float)
    return v[np.flatnonzero(cache.evt)] if events else v


def ets_of(cache):
    """Event-bar timestamps — the timebase paired with the event-tape line reads."""
    return cache.ts[np.flatnonzero(cache.evt)]

def _seam_hold(ts, v, seam_ms):
    seams = np.flatnonzero((ts % seam_ms) == 0)
    if not len(seams):
        return v
    i = np.searchsorted(ts[seams], ts, side='right') - 1
    out = np.zeros(len(ts)); ok = i >= 0; out[ok] = v[seams[i[ok]]]
    return out

def cross(cache, a, b, grid_ms, wob, start, end):
    """Crossover of (line a - line b) at level 0, wob-debounced, within [start,end).
    grid_ms<=5000 = emerging (varied times); coarser = seam-held (pins to the grid). -> [(ts, bd)] bd=+1 up/long.
    EVENT-TAPE (Joe 0726): line reads + cross_wob run on px_smooth event bars, so crosses match the engine."""
    ts = ets_of(cache)
    xm = line(cache, a) - line(cache, b)
    v = xm if grid_ms <= 5000 else _seam_hold(ts, xm, grid_ms)
    up = cache.causal.cross_wob(v, 0.0, +1, wob); dn = cache.causal.cross_wob(v, 0.0, -1, wob)
    win = (ts >= start) & (ts < end)
    ue = np.flatnonzero((up & ~np.roll(up, 1)) & win)
    de = np.flatnonzero((dn & ~np.roll(dn, 1)) & win)
    return sorted([(int(ts[i]), 1) for i in ue] + [(int(ts[i]), -1) for i in de])

def xcross_pred(cache, base='s11', bnd_offset=4):
    """x-cross-pred — the EXHAUSTION x X r cross near the in-band boundary (rpl_walk._polar geometry). SRP: this
    is the single 'x-cross-pred' detector; it is NOT predict_breach (that's the r-pred ladder that feeds it).
    It fires EARLIER than the x X m cross (r sits nearer the boundary than the mid m), so it's the lead anchor.
      LONG side  (exhaust oversold):  {base}x crosses UP  over {base}r  while r < LO + bnd_offset.
      SHORT side (exhaust overbought):{base}x crosses DOWN under {base}r while r > HI - bnd_offset.
    Raw rising-edge cross (no wob) — the pred is the early anchor; the wob debounce lives downstream (flip_provisional).
    -> (long_edge, short_edge) per-bar bool arrays."""
    d = line(cache, base + 'x') - line(cache, base + 'r'); r = line(cache, base + 'r')
    up = (d > 0) & (np.roll(d, 1) <= 0); dn = (d < 0) & (np.roll(d, 1) >= 0)
    long_edge  = up & (r < R.LO + bnd_offset)      # exhaust bear leg: x over r near LO -> long
    short_edge = dn & (r > R.HI - bnd_offset)      # exhaust bull leg: x under r near HI -> short
    long_edge[0] = short_edge[0] = False
    return long_edge, short_edge


def xm_cross(cache, base='s11', wob=8, lookback_tf=3, min_dwell_s=180, align_line=None,
             lead_via_xcp=False, xcp_bnd_offset=4, xcp_lead_s=300, start=None, end=None):
    """{base}x X {base}m cross with side-specific, dwell-gated OOB (Joe 0724). One engine, any band (base='s8'/'s11'..).
    CANONICAL x-cross:
      LONG  = {base}x crosses OVER  {base}m  AND {base}m's most-recent OOB was a SUSTAINED LO-OOB.
      SHORT = {base}x crosses UNDER {base}m  AND {base}m's most-recent OOB was a SUSTAINED HI-OOB.
    Both the cross AND the OOB-dwell are jig events (cache.causal.cross_wob) — no hand-rolled run loops:
      - x-cross:  cross_wob({base}x-{base}m, 0, dir, wob)           wobble-debounced crossover.
      - LO/HI dwell: cross_wob({base}m, LO/HI, -/+1, dwell_bars)    m held past-boundary for >= dwell_bars 5s bars.
    A brief 'small swell' poke (< min_dwell_s) never confirms the dwell, so it can't gate a cross.
    min_dwell_s is in SECONDS -> dwell_bars = round(sec/5). lookback_tf = OOB recency in base-TF bars (tf parsed
    from base). align_line = name or [names] that must ALSO be OOB on the same side. -> [(ts, bd)] bd=+1 long/-1 short."""
    tf = int(''.join(c for c in base if c.isdigit()))
    ts = ets_of(cache); n = len(ts); idx = np.arange(n)     # EVENT tape (Joe 0726): dwell/lookback now count EVENT bars
    sx = line(cache, base + 'x'); sm = line(cache, base + 'm')
    up = cache.causal.cross_wob(sx - sm, 0.0, +1, wob); dn = cache.causal.cross_wob(sx - sm, 0.0, -1, wob)
    up_e = up & ~np.roll(up, 1); dn_e = dn & ~np.roll(dn, 1)
    dwell_bars = max(1, round(min_dwell_s / 5))
    lo_dw = cache.causal.cross_wob(sm, R.LO, -1, dwell_bars)          # SUSTAINED LO-OOB (jig)
    hi_dw = cache.causal.cross_wob(sm, R.HI, +1, dwell_bars)          # SUSTAINED HI-OOB (jig)
    last_lo = np.maximum.accumulate(np.where(lo_dw, idx, -1))
    last_hi = np.maximum.accumulate(np.where(hi_dw, idx, -1))
    win = int(lookback_tf * tf * 60 / 5)
    long_gate  = (last_lo > last_hi) & ((idx - last_lo) <= win)       # most-recent SUSTAINED OOB was LO
    short_gate = (last_hi > last_lo) & ((idx - last_hi) <= win)       # most-recent SUSTAINED OOB was HI
    long_gate  &= ~(sm >= R.HI)      # ...and m hasn't swung clean across to HI-OOB now (no stale reversal)
    short_gate &= ~(sm <= R.LO)      # ...and m hasn't swung clean across to LO-OOB now
    if align_line:                           # confluence: EVERY named mid line must be OOB on the SAME side (AND gate)
        names = [align_line] if isinstance(align_line, str) else list(align_line)
        for nm in names:
            hm = line(cache, nm)
            long_gate  &= (hm <= R.LO)       # LONG kept only while each align line is LO-OOB (also oversold)
            short_gate &= (hm >= R.HI)       # SHORT kept only while each is HI-OOB
    le = np.flatnonzero(up_e & long_gate); se = np.flatnonzero(dn_e & short_gate)
    if lead_via_xcp:                          # ONE JOB: pull each x X m entry back to its leading x-cross-pred
        lp, sp = xcross_pred(cache, base, xcp_bnd_offset)
        lead_bars = max(1, int(xcp_lead_s / 5))
        def _pull(idxs, edge):
            ei = np.flatnonzero(edge)
            out = []
            for i in idxs:                    # earliest same-side x-cross-pred within the lead window before the cross
                c = ei[(ei <= i) & (ei > i - lead_bars)]
                out.append(int(c[0]) if len(c) else int(i))
            return out
        le = _pull(le, lp); se = _pull(se, sp)
    out = [(int(ts[i]), 1) for i in le] + [(int(ts[i]), -1) for i in se]
    if start is not None: out = [(t, b) for (t, b) in out if t >= start]
    if end is not None:   out = [(t, b) for (t, b) in out if t < end]
    return sorted(out)


def s9x_cross(cache, wob=8, lookback_tf=3, min_dwell_s9x=180, align_line=None,
              lead_via_xcp=False, xcp_bnd_offset=4, xcp_lead_s=300, start=None, end=None):
    """Thin wrapper — the s9 instance of xm_cross = THE trade cross (swapped s11->s9, Joe 0724).
    Keeps every mechanic of the canonical cross (side-specific dwell-gated OOB, opposite-side guard,
    align_line confluence); only the band changed s11->s9. min_dwell_s9x keeps the dwell knob name."""
    return xm_cross(cache, 's9', wob, lookback_tf, min_dwell_s9x, align_line,
                    lead_via_xcp, xcp_bnd_offset, xcp_lead_s, start, end)


def mae(ets, epx, entries, swing_pct=1.0, up_long=True):
    """MAE/MFE from each entry to the next favourable swing on px_smooth EVENT bars (sweep basis).
    -> [(ts, dir, mae, mfe)]. up_long: bd=+1 -> long (fav=High)."""
    piv = find_pivots(epx, swing_pct)
    out = []
    for (tms, bd0) in entries:
        bd = bd0 if up_long else -bd0
        j = min(int(np.searchsorted(ets, tms)), len(epx) - 1)
        fav = 'H' if bd == 1 else 'L'
        nxt = next((pi for pi, pk in piv if pi > j and pk == fav), None)
        seg = epx[j:(nxt + 1)] if nxt is not None else epx[j:]
        if len(seg) < 1 or epx[j] <= 0:
            out.append((tms, 'long' if bd == 1 else 'short', 0.0, 0.0)); continue
        dd = (seg - epx[j]) / epx[j] * 100.0 * bd
        out.append((tms, 'long' if bd == 1 else 'short', float(-dd.min()), float(dd.max())))
    return out
