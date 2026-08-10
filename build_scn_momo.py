"""build_scn_momo — the same backtest modelling, matched on the MOMO DECISIONS ALONE. Joe 0802 23:45.

    Joe: "now run the same backtest modelling using only the momo decisions"

DIFFERENCE FROM build_scn.py — exactly two things
  1. THE VECTOR. Band positions are dropped. A scenario is the 9 momo states read at the signal's own
     direction: s4r / s15r / s22r (exhv2's R_SPEC trio, the lines the decision is actually made on) plus
     the six rsd r lines gcs5_r .. s4_r (generic R.LN['r'] at each TF). Agreement is 0-9.
  2. THE MATCH SPAN IS OUT OF SAMPLE BY CONSTRUCTION. 05-18 00:00 -> the FIRST signal bar, exclusive.

WHY 2 IS NOT OPTIONAL. rpl_learn ln_pk 47: the band run's match span overlapped the signal window by five
days, so 339 of 1,477 complete matches were a signal matching its own bar, and those bars had been
SELECTED for being clean. It reported 58.77%; out of sample the same cell was 28.10%. A model cannot be
allowed to read its own selection back to itself.

UNCHANGED. The 461 signals, target 1.3%, MAE gate 0.65%, the forward-leg computation, and the SRP tables.
vmomo() is the vectorised momo() verified bar-for-bar against build_exhv2.momo() across 1,172 samples per
direction with zero mismatches.

    python3 build_scn_momo.py
"""
import os, sys, time, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '4')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_rpl_jig as J
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
from vmomo import vmomo
from build_scn import SETS, MOMO_LINES, MOMO_STATE, TAPE0, TAPE1, DDL, forward_leg
from predict_walk import walk, resolve

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')


def main(argv):
    g = lambda k, d: (type(d)(argv[argv.index(k) + 1]) if k in argv else d)
    TARGET, MAEMAX, QUORUM = g('--target', 1.3), g('--mae', 0.65), g('--quorum', 1)
    HI, LO = R.HI, R.LO
    NL = len(MOMO_LINES)

    ovr = {}
    for s, tf in SETS:
        ovr.update(R._mk('%s_r' % s, tf, R.LN['r']))
    ovr.update(J.LINES)

    d = DatabaseManager(**get_db_config()); d.connect()
    end_ms = int(d.execute('SELECT MAX(kc_timestamp) m FROM kline_collection', fetch=True)[0]['m'])
    hours = int((end_ms - TAPE0) / 3600000) + 1
    t0 = time.time()
    with Jig(end_ms, hours=hours, warmup=J.WIN_WARMUP, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64)
        base = j.W.base
        evt = base['volume'].to_numpy(dtype=float) > 0
        src = IC.build_source(base, R.PXS_CFG['src'])
        ei = np.flatnonzero(evt)
        px = np.full(len(src), np.nan); px[ei] = IC.dema(src[ei], int(R.PXS_CFG['len']))
        fin = np.isfinite(px)
        ix = np.where(fin, np.arange(len(px)), 0); np.maximum.accumulate(ix, out=ix)
        px = px[ix]; px[:int(np.argmax(fin))] = px[int(np.argmax(fin))]
        RLALL = {v: np.asarray(j.W.line(v), float) for _, v in MOMO_LINES}
        G1 = np.asarray(j.W.line('jMg1'), float); G2 = np.asarray(j.W.line('jMg2'), float)
    n = len(ts)
    print('jig build %.1f s   bars %d   momo lines %d' % (time.time() - t0, n, NL), flush=True)

    t1 = time.time()
    ST = {}
    for tag, src_ in MOMO_LINES:
        for dr in (1, -1):
            ST[(tag, dr)] = vmomo(RLALL[src_], dr)[0]            # state array only
    SV = {dr: np.vstack([ST[(t_, dr)] for t_, _ in MOMO_LINES]).T for dr in (1, -1)}   # (n, 9) int8
    print('momo %d lines x 2 dirs  %.1f s' % (NL, time.time() - t1), flush=True)

    HITL, MAEL = forward_leg(px, 1, TARGET)
    HITS, MAES = forward_leg(px, -1, TARGET)
    print('forward legs done  %.1f s' % (time.time() - t0), flush=True)

    W = walk(ts, px, {'jMg1': G1, 'jMg2': G2, 'jr4': RLALL['jr4'], 'jr15': RLALL['jr15'],
                      'jr22': RLALL['jr22']}, HI, LO, end_ms - 168 * 3600000)
    SIG = []
    for w in W:
        r = resolve(w, ts, px, QUORUM)
        if r is None:
            continue
        i, mn, which = r
        hit, mae = (HITL[i], MAEL[i]) if w['dr'] > 0 else (HITS[i], MAES[i])
        if hit < 0 or not np.isfinite(mae) or mae > MAEMAX:
            continue
        SIG.append(dict(i=i, w=w, momo_n=mn, which=which, hit=int(hit), mae=float(mae)))
    print('KEPT quorum-%d signals: %d' % (QUORUM, len(SIG)), flush=True)

    # OUT OF SAMPLE BY CONSTRUCTION — strictly before the first signal bar
    first_sig = min(int(ts[s['i']]) for s in SIG)
    oos = (ts >= TAPE0) & (ts < first_sig)
    print('match span %s -> %s (exclusive)   bars %d'
          % (u(TAPE0), u(first_sig), int(oos.sum())), flush=True)

    for q in DDL:
        d.execute(q)
    run = d.execute(
        'INSERT INTO rpl_scn_run (rn_target_pct,rn_mae_max_pct,rn_band_lo,rn_band_lomid,rn_band_himid,'
        'rn_band_hi,rn_cross_bars,rn_cross_sec,rn_tape0_ms,rn_tape1_ms,rn_tape_bars,rn_quorum,rn_n_signal,'
        'rn_lines,rn_pairs,rn_note) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (TARGET, MAEMAX, LO, None, None, HI, 0, 0, TAPE0, first_sig, int(oos.sum()), QUORUM, len(SIG),
         NL, 0,
         'MOMO-ONLY vector: the %d momo states (s4r/s15r/s22r + the 6 rsd r lines) read at the signal own '
         'direction. Agreement 0-%d. NO band positions. Match span is OUT OF SAMPLE BY CONSTRUCTION: '
         '05-18 00:00 -> the first signal bar exclusive, which is the fix for the self-match leak in '
         'rpl_learn ln_pk 47.' % (NL, NL)))
    print('run pk %d' % run, flush=True)

    t2 = time.time()
    for si, s in enumerate(SIG):
        i, w, dr = s['i'], s['w'], s['w']['dr']
        sv = SV[dr]
        sg = d.execute(
            'INSERT INTO rpl_scn_signal (sg_run,sg_ms,sg_utc,sg_arm_ms,sg_arm_utc,sg_arm_line,sg_arm_side,'
            'sg_dir,sg_dr,sg_px,sg_momo_n,sg_momo_which,sg_bars_to_target,sg_min_to_target,sg_mae_pct,'
            'sg_band_vec,sg_max_agree,sg_momo_up,sg_momo_dn) VALUES (' + ','.join(['%s'] * 19) + ')',
            (run, int(ts[i]), u(ts[i]), int(ts[w['arm']]), u(ts[w['arm']]), w['line'], w['side'],
             'LONG' if dr > 0 else 'SHORT', dr, float(px[i]), s['momo_n'], s['which'],
             s['hit'] - i, (s['hit'] - i) * 5 / 60.0, s['mae'],
             ''.join(str(int(v)) for v in sv[i]), None,
             int(sum(SV[1][i][k] == 3 for k in range(3))), int(sum(SV[-1][i][k] == 3 for k in range(3)))))
        rows = [(run, 'signal', sg, tag, dr, MOMO_STATE[int(SV[dr][i][k])], None, None, None)
                for k, (tag, _) in enumerate(MOMO_LINES)]
        d.executemany('INSERT INTO rpl_scn_momo (mo_run,mo_owner_kind,mo_owner,mo_line,mo_dr,mo_state,'
                      'mo_slope,mo_r2,mo_r) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)', rows)

        agree = (sv == sv[i]).sum(axis=1).astype(np.int8)
        HIT, MAE = (HITL, MAEL) if dr > 0 else (HITS, MAES)
        reached = HIT >= 0
        clean = reached & (MAE <= MAEMAX)
        arows = []
        for lv in range(NL + 1):
            m = oos & (agree == lv)
            nb_ = int(m.sum())
            if not nb_:
                continue
            nr = int((m & reached).sum()); mc = m & clean; nc = int(mc.sum())
            mm = ((HIT[mc] - np.flatnonzero(mc)) * 5 / 60.0) if nc else np.array([])
            arows.append((run, sg, lv, nb_, nr, nc, nc / nb_ * 100.0,
                          float(np.median(mm)) if nc else None,
                          float(np.median(MAE[mc])) if nc else None))
        d.executemany('INSERT INTO rpl_scn_agree (ag_run,ag_signal,ag_level,ag_n_bars,ag_n_reached,'
                      'ag_n_clean,ag_rate_clean,ag_med_min,ag_med_mae) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                      arows)
        d.execute('UPDATE rpl_scn_signal SET sg_max_agree=%s WHERE sg_pk=%s',
                  (int(agree[oos].max()) if oos.any() else None, sg))
        if (si + 1) % 50 == 0:
            print('  %d/%d signals  %.0f s' % (si + 1, len(SIG), time.time() - t2), flush=True)
    print('done  %.0f s total' % (time.time() - t0), flush=True)
    d.disconnect()


if __name__ == '__main__':
    main(sys.argv[1:])
