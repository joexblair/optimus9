"""walk_long — run the proven walk chain for a LONG on a hi-side OOB. Joe 0802 21:52.

    Joe: "a hi OOB Mage doesn't always have to produce a short trade ... re-build the full walk and find
    the correct moment for the LONG entry that capitalises on momo"

THE CHAIN IS NOT REIMPLEMENTED. Every stage calls the same objects build_rpl_jig.py calls:
  WALK    B.oob_qualified(M4, HI, LO)             build_exhv2.py:83  — 48-bar / 240 s causal dwell
  HOP     B.momo(jr22, ed, w) == 'momo'           build_exhv2.py:113 — REWALK 2
  ANCHOR  cau.cross_wob(jx15 - jm15, 0, xdr, WOBN) + the slip gate
  CONFIRM cau.cross_wob(jg15x - jg15m, 0, xdr, WOBN)
  EXIT    the next qualified bar after the signal
Knobs come from the modules, not from literals here: R.HI, R.LO, R.WOBN, J.SLIP, B.WALK_DWELL_BARS.

WHAT IS CHANGED, AND IT IS EXACTLY ONE THING
  build_rpl_jig.py:395-397 derives the trade direction from the breach side and nothing else:
      sd = 'hi' if M4[w] >= HI else 'lo';  t.dir = 'SHORT' if sd=='hi' else 'LONG';  t.xdr = -1 if hi else 1
  This script runs the SAME chain with `dir` supplied instead of derived, so a hi breach can be walked
  LONG. `xdr` follows the trade direction because that is what xdr is — the sense the x/m and gcs15 crosses
  must run in for the entry to be an entry.

THE SLIP GATE IS UNCHANGED AND UNAMBIGUOUS HERE
  build_rpl_jig.py:437-439 gates on the r pair nearing the boundary the BREACH is heading for:
      hi -> max(s15r, s22r) >= HI - SLIP ;  lo -> min(s15r, s22r) <= LO + SLIP
  For a LONG on a hi breach both readings — "the breach side" and "the trade direction" — select the HI
  boundary, so there is no choice to make. It stays `max(s15r, s22r) >= HI - SLIP`.

THE HOP GATE IS UNCHANGED
  `ed` stays the breach side (+1 for hi). momo is read in the direction the Mage broke, not the direction
  of the trade. Changing that would be a second edit and it is not needed to answer the question.

BOTH DIRECTIONS ARE RUN AND PRINTED SIDE BY SIDE — the SHORT the code produces today and the LONG asked
for — so the two entries are comparable rather than asserted.

MOMO IS REPORTED AT TWO WINDOWS at every stage bar: the live 55 min / 5 min-sample setting, and a 5 min
window. rpl_learn ln_pk 40/41: MOMO_SLOPE_MIN is denominated per SAMPLE, so the two are not comparable as
slopes — the per-minute column is printed for that reason. Nothing is gated on the 5 min read.

    python3 walk_long.py                  # the most recent hi-side OOB episode
    python3 walk_long.py --hours 24       # widen the rebuild window
"""
import os, sys, time, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '4')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_rpl_jig as J
import build_exhv2 as B
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, _Causal
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')


def fit(r, w, win_min, ns=12):
    """Least-squares fit of `ns` samples spanning win_min, ending at bar w. Returns (slope_per_sample,
    slope_per_min, r2). Separate from B.momo because B.momo's spacing is fixed at MOMO_STEP_BARS."""
    sb = max(1, int(round(win_min * 12 / (ns - 1))))
    idx = np.array([w - k * sb for k in range(ns - 1, -1, -1)])
    if idx[0] < 0 or not np.isfinite(r[idx]).all():
        return float('nan'), float('nan'), float('nan')
    y = r[idx]; x = np.arange(len(y), dtype=float)
    sl, ic = np.polyfit(x, y, 1)
    res = ((y - (sl * x + ic)) ** 2).sum(); tot = ((y - y.mean()) ** 2).sum()
    r2 = 1 - res / tot if tot > 1e-12 else 0.0
    return float(sl), float(sl * 12.0 / sb), float(r2)


def stage_read(L, px, w, ed, tag):
    print('  %-8s %s   pxs %.8f' % (tag, u_ts[w], px[w]))
    for nm, key in (('s4r', 'jr4'), ('s15r', 'jr15'), ('s22r', 'jr22')):
        st, sl, r2, rw = B.momo(L[key], ed, w)
        s5, pm5, r5 = fit(L[key], w, 5)
        print('      %-5s r %7.2f | 55min %-8s slope %+7.3f/sample R2 %5.3f | 5min %+7.3f/min R2 %5.3f'
              % (nm, rw, st, sl, r2, pm5, r5))


def run_chain(L, M4, px, ts, cau, QB, t0, want_dir, HI, LO, SLIP):
    """The chain from build_rpl_jig.py:355-485, with `dir` supplied rather than derived."""
    nx = QB[QB > t0]
    if not len(nx):
        return {'err': 'no qualified bar after the episode start'}
    w = int(nx[0])
    sd = 'hi' if M4[w] >= HI else 'lo'
    ed = 1 if sd == 'hi' else -1                 # HOP gate direction = the breach side. Unchanged.
    hops = []
    pending = False
    while True:
        st22 = B.momo(L['jr22'], ed, w)
        nh = QB[QB > w]
        if st22[0] != 'momo':
            break
        if not len(nh):
            pending = True; break
        w = int(nh[0]); hops.append(int(ts[w]))
    sd = 'hi' if M4[w] >= HI else 'lo'
    xdr = 1 if want_dir == 'LONG' else -1        # THE ONE CHANGE: xdr follows the TRADE, not the breach
    out = {'walk_bar': w, 'walk_ms': int(ts[w]), 'side': sd, 'dir': want_dir, 'hops': hops,
           'pending': pending, 'ed': ed, 'xdr': xdr,
           's15_momo': B.momo(L['jr15'], ed, w), 's22_momo': B.momo(L['jr22'], ed, w)}

    c = cau.cross_wob(L['jx15'] - L['jm15'], 0.0, xdr, R.WOBN)
    e = np.flatnonzero(c & ~np.r_[False, c[:-1]]); e = e[e >= w]
    a = None; rejected = 0
    for _c in e:
        _c = int(_c)
        ok = (max(L['jr15'][_c], L['jr22'][_c]) >= HI - SLIP) if sd == 'hi' \
            else (min(L['jr15'][_c], L['jr22'][_c]) <= LO + SLIP)
        if ok:
            a = _c; break
        rejected += 1
    out['x_crosses_after_walk'] = int(len(e))
    out['crosses_rejected_by_slip'] = rejected
    if a is None:
        out['anchor'] = None
        return out
    out['anchor'] = a; out['anchor_ms'] = int(ts[a])
    out['anchor_r'] = (float(L['jr15'][a]), float(L['jr22'][a]))

    c2 = cau.cross_wob(L['jg15x'] - L['jg15m'], 0.0, xdr, R.WOBN)
    e2 = np.flatnonzero(c2 & ~np.r_[False, c2[:-1]]); e2 = e2[e2 >= a]
    if not len(e2):
        out['signal'] = None
        return out
    sbar = int(e2[0]); out['signal'] = sbar; out['sig_ms'] = int(ts[sbar]); out['sig_px'] = float(px[sbar])

    nq = QB[QB > sbar]
    if len(nq):
        eb = int(nq[0]); sgn = 1.0 if want_dir == 'LONG' else -1.0
        seg = px[sbar:eb + 1]
        out['exit'] = eb; out['exit_ms'] = int(ts[eb])
        out['ret_pct'] = float(sgn * (px[eb] - px[sbar]) / px[sbar] * 100.0)
        up = (np.nanmax(seg) - px[sbar]) / px[sbar] * 100.0
        dn = (px[sbar] - np.nanmin(seg)) / px[sbar] * 100.0
        out['mfe_pct'] = float(up if want_dir == 'LONG' else dn)
        out['mae_pct'] = float(dn if want_dir == 'LONG' else up)
    else:
        out['exit'] = None
        sgn = 1.0 if want_dir == 'LONG' else -1.0
        seg = px[sbar:]
        out['open_pct'] = float(sgn * (px[-1] - px[sbar]) / px[sbar] * 100.0)
        up = (np.nanmax(seg) - px[sbar]) / px[sbar] * 100.0
        dn = (px[sbar] - np.nanmin(seg)) / px[sbar] * 100.0
        out['mfe_pct'] = float(up if want_dir == 'LONG' else dn)
        out['mae_pct'] = float(dn if want_dir == 'LONG' else up)
    return out


def show(tag, o, px):
    print('\n== %s ==' % tag)
    if 'err' in o:
        print('  ' + o['err']); return
    print('  WALK    %s   side %s   s4Mage %s   hops %d%s'
          % (u(o['walk_ms']), o['side'], '', len(o['hops']), '   HOP-PENDING' if o['pending'] else ''))
    print('          s15 momo %-8s slope %+7.3f R2 %5.3f | s22 momo %-8s slope %+7.3f R2 %5.3f'
          % (o['s15_momo'][0], o['s15_momo'][1], o['s15_momo'][2],
             o['s22_momo'][0], o['s22_momo'][1], o['s22_momo'][2]))
    print('  xdr     %+d  (%s)' % (o['xdr'], o['dir']))
    print('  x/m crosses at/after the walk: %d   rejected by slip: %d'
          % (o['x_crosses_after_walk'], o['crosses_rejected_by_slip']))
    if o.get('anchor') is None:
        print('  ANCHOR  none — no x15 X m15 cross in the %s sense has passed the slip gate yet' % o['dir'])
        return
    print('  ANCHOR  %s   s15r %.2f  s22r %.2f   (gate: max >= %.1f)'
          % (u(o['anchor_ms']), o['anchor_r'][0], o['anchor_r'][1], R.HI - J.SLIP))
    if o.get('signal') is None:
        print('  SIGNAL  none — no gcs15x X gcs15m cross in the %s sense at/after the anchor yet' % o['dir'])
        return
    print('  SIGNAL  %s   pxs %.8f   lag from anchor %.1f min   *** THE ENTRY ***'
          % (u(o['sig_ms']), o['sig_px'], (o['sig_ms'] - o['anchor_ms']) / 60000.0))
    if o.get('exit') is None:
        print('  EXIT    none yet — no qualified bar after the signal')
        print('          open %+.3f%%   mfe %.3f%%   mae %.3f%%' % (o['open_pct'], o['mfe_pct'], o['mae_pct']))
    else:
        print('  EXIT    %s   ret %+.3f%%   mfe %.3f%%   mae %.3f%%   hold %.1f min'
              % (u(o['exit_ms']), o['ret_pct'], o['mfe_pct'], o['mae_pct'],
                 (o['exit_ms'] - o['sig_ms']) / 60000.0))


def main(argv):
    hours = int(argv[argv.index('--hours') + 1]) if '--hours' in argv else 24
    d = DatabaseManager(**get_db_config()); d.connect()
    end_ms = int(d.execute('SELECT MAX(kc_timestamp) m FROM kline_collection', fetch=True)[0]['m'])
    d.disconnect()
    HI, LO, SLIP, D = R.HI, R.LO, J.SLIP, B.WALK_DWELL_BARS

    t0c = time.time()
    with Jig(end_ms, hours=hours, warmup=J.WIN_WARMUP, overrides=J.LINES) as j:
        ts = np.asarray(j.ts, np.int64)
        base = j.W.base
        evt = base['volume'].to_numpy(dtype=float) > 0
        src = IC.build_source(base, R.PXS_CFG['src'])
        ei = np.flatnonzero(evt)
        px = np.full(len(src), np.nan); px[ei] = IC.dema(src[ei], int(R.PXS_CFG['len']))
        fin = np.isfinite(px)
        ix = np.where(fin, np.arange(len(px)), 0); np.maximum.accumulate(ix, out=ix)
        px = px[ix]; px[:int(np.argmax(fin))] = px[int(np.argmax(fin))]
        L = {n: np.asarray(j.W.line(n), float) for n in J.LINES}
        cau = _Causal(None)
    M4 = L['jM4']
    QB = np.flatnonzero(B.oob_qualified(M4, HI, LO))
    print('jig build %.1f s   bars %d   HI/LO %g/%g   DWELL %d bars = %d s   SLIP %.1f   WOBN %d'
          % (time.time() - t0c, len(ts), HI, LO, D, D * 5, SLIP, R.WOBN))
    print('span %s -> %s   qualified bars %d' % (u(ts[0]), u(ts[-1]), len(QB)))

    # the most recent hi-side OOB crossing
    o = (M4 >= HI) | (M4 <= LO)
    rise = np.flatnonzero(o & ~np.r_[False, o[:-1]])
    hi_rise = [int(z) for z in rise if M4[int(z)] >= HI]
    if not hi_rise:
        print('no hi-side OOB crossing in the window'); return
    z = hi_rise[-1]
    print('\nmost recent hi-side OOB crossing: %s   s4Mage %.2f' % (u(ts[z]), M4[z]))
    globals()['u_ts'] = [u(t) for t in ts]

    for want in ('SHORT', 'LONG'):
        show('%s  (%s)' % (want, 'what the code produces today' if want == 'SHORT' else 'what Joe asked for'),
             run_chain(L, M4, px, ts, cau, QB, z, want, HI, LO, SLIP), px)

    print('\n== momo at the qualified WALK bar, both windows ==')
    nx = QB[QB > z]
    if len(nx):
        stage_read(L, px, int(nx[0]), 1, 'walk')


if __name__ == '__main__':
    main(sys.argv[1:])
