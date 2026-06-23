"""
alchemy_wob_rig.py (Joe 0622) — wob test rig. Finds the blc_wob (n, strict) whose emerging-line
wob reversal fires CLOSEST to the swing (the true turn), traded off against premature-entry HARM.

swing (Joe's def) = the emerging line's min/max BETWEEN the previous and following TF-closed bar,
per closed OOB reversal. TF-reversal time = the next close after the peak (the lagged baseline).
Per (n, strict):
  • coverage   — % of OOB swings the wob catches
  • median_lag — wob_fire − swing (seconds); lower = closer to the true turn
  • harm%      — % of the setting's wob fires that land during a SAME-SIDE s30a (s14M-constrained):
                 a wob exit there opens the gate to a premature same-side entry. The asymmetry
                 (early is worse than late) lives here, so closeness stays symmetric (Joe 0622).
Sweep stored via GrindStore (grind_storage_spec) — kind 'wob_rig', kpi = median_lag.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np, datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.db.grind_store import GrindStore
import bias_machine as bm

HI, LO = 85.0, 15.0


def s30a_active(W):
    """Per base bar: is a same-side s30a active (all m/M/r OOB) AND s14M on that side? → (hi, lo)."""
    c = W.cfg
    (s30, cM), (_, cm), (_, cr) = (W._ls.resolve(c.s30_M), W._ls.resolve(c.s30_m), W._ls.resolve(c.s30_r))
    f30 = IC.resample(W.base, s30); t30 = f30['timestamp'].to_numpy() + s30 * 1000
    M = IC.f_bb(IC.build_source(f30, cM[3]), cM[1], cM[2])
    m = IC.f_bb(IC.build_source(f30, cm[3]), cm[1], cm[2])
    r = IC.f_k(IC.build_source(f30, cr[4]), cr[1], cr[2], cr[3])
    hi = (M >= HI) & (m >= HI) & (r >= HI); lo = (M <= LO) & (m <= LO) & (r <= LO)
    idx = np.searchsorted(t30, W.ts, 'right') - 1; ok = idx >= 0
    hb = np.zeros(len(W.ts), bool); lb = np.zeros(len(W.ts), bool)
    hb[ok] = hi[idx[ok]]; lb[ok] = lo[idx[ok]]
    s14 = W.s14M
    return hb & (s14 > 50), lb & (s14 < 50)


def _swings(em, ts, closed, t_close):
    out = []
    for j in range(1, len(closed) - 1):
        a, b, c = closed[j - 1], closed[j], closed[j + 1]
        if not (a == a and b == b and c == c):
            continue
        if b > a and b >= c and b >= HI:
            side = 1
        elif b < a and b <= c and b <= LO:
            side = -1
        else:
            continue
        sel = np.where((ts >= t_close[j - 1]) & (ts <= t_close[j + 1]))[0]
        if not len(sel) or np.all(em[sel] != em[sel]):
            continue
        k = sel[np.nanargmax(em[sel]) if side == 1 else np.nanargmin(em[sel])]
        out.append((int(ts[k]), side, int(t_close[j + 1])))
    return out


def run_line(name, tf, length, mult, src, base, ts, hi_active, lo_active):
    em = IC.f_bb_lookahead(base, tf, length, mult, src)
    rs = IC.resample(base, tf); closed = IC.f_bb(IC.build_source(rs, src), length, mult)
    t_close = rs['timestamp'].to_numpy() + tf * 1000
    sw = _swings(em, ts, closed, t_close)
    base_lag = float(np.median([(b - s) / 1000 for s, _, b in sw])) if sw else float('nan')
    print(f"\n=== {name}  (tf={tf} {length}|{mult}|{src})  ·  {len(sw)} OOB swings  ·  TF-baseline lag {base_lag:.0f}s ===")
    print('  n  strict | coverage  median_lag(s)  harm%  vs_TF')
    cells = []
    for strict in (0, 1):
        for n in (2, 3, 5, 7):
            wob = IC.wobble_slayer(em, n, HI, LO, anchored=True, strict=bool(strict))
            fhi = np.where(wob == -1)[0]; flo = np.where(wob == 1)[0]    # hi-exit / lo-exit fires
            lags = []; mhi, mlo = set(), set()                          # matched-to-a-real-swing fire idx
            for s_time, side, b_time in sw:
                ci = fhi if side == 1 else flo; ct = ts[ci]
                w = np.where((ct >= s_time) & (ct <= b_time + tf * 1000))[0]
                if len(w):
                    lags.append((ct[w[0]] - s_time) / 1000)
                    (mhi if side == 1 else mlo).add(int(ci[w[0]]))
            cov = round(len(lags) / len(sw) * 100, 1) if sw else 0.0
            ml = float(np.median(lags)) if lags else float('nan')
            total = len(fhi) + len(flo)
            # HARM = NOISE fires (not matched to any real swing) that land during a same-side s30a —
            # a phantom exit there opens the gate to a premature same-side entry.
            uhi = [i for i in fhi if i not in mhi]; ulo = [i for i in flo if i not in mlo]
            harm = int(hi_active[uhi].sum() + lo_active[ulo].sum())
            hr = round(harm / total * 100, 1) if total else 0.0
            print(f"  {n}    {strict}   |   {cov:4.0f}%      {ml:6.0f}       {hr:4.0f}%  {ml - base_lag:+6.0f}")
            cells.append({'cell': {'n': n, 'strict': strict},
                          'metrics': {'coverage_pct': cov, 'median_lag_s': None if ml != ml else ml,
                                      'harm_pct': hr, 'harm_fires': harm, 'fires': total,
                                      'vs_tf_s': None if ml != ml else round(ml - base_lag)},
                          'kpi': None if ml != ml else ml})
    meta = {'line': name, 'tf': tf, 'len': length, 'mult': mult, 'src': src,
            'swings': len(sw), 'tf_baseline_lag_s': base_lag}
    return meta, cells


if __name__ == '__main__':
    db = DatabaseManager(**get_db_config()); db.connect()
    END = int(dtm.datetime(2026, 6, 16, tzinfo=timezone.utc).timestamp() * 1000)
    CFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m',
                        xm45=False, mae=0.4, target=0.9, floater_anchor='last', verdict='pk')
    W = bm.BiasWindow(db, END, cfg=CFG)
    hi_active, lo_active = s30a_active(W)
    gs = GrindStore(db)
    for cfg in [('s14m', 420, 20, 0.77, 'hlc3'), ('hb9M', 540, 19, 0.64, 'close')]:
        meta, cells = run_line(*cfg, W.base, W.ts, hi_active, lo_active)
        run = gs.register_run('wob_rig', config=meta, window_start=int(W.ts[0]), window_end=END,
                              kpi_name='median_lag_to_swing_s', notes=f"{meta['swings']} OOB swings")
        gs.write_results(run, cells)
        best = min((c['kpi'] for c in cells if c['kpi'] is not None), default=None)
        gs.finalize(run, kpi_value=best)
        print(f"  → stored grind_run {run} ({len(cells)} cells, best closeness {best:.0f}s)")
    db.disconnect()
