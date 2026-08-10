"""scn_effective_n — re-measure the momo model with the three shortcuts removed. Joe 0803 00:15.

    Joe: "why is your data so ambiguous? have you skimmed the data instead of taking time to carefully
    analyse?"

THE THREE SHORTCUTS IN build_scn_momo.py, AND THE FIX FOR EACH

1. MATCHED ON STATE ONLY. A signal is a bar where s1Mage or s2Mage is OOB, the walk has run, and the momo
   quorum has established. The match side required NONE of that — any bar in the tape with the same 9 momo
   states counted, including bars where no Mage was anywhere near a boundary. That is not the same
   scenario, it is the same reading. FIX: `--armed` restricts matches to bars that are themselves inside an
   s1M/s2M OOB stretch, so a match is a comparable moment rather than a comparable number.

2. BASE RATE OVER ALL BARS. ~33% is the clean-rate of every bar on the tape. The model was being compared
   against the wrong reference. FIX: report the armed base rate alongside the all-bar base rate.

3. BAR COUNTS QUOTED AS SAMPLE SIZE. This is the one that makes the earlier numbers wrong rather than
   merely incomplete. Consecutive 5 s bars share nearly all their information — a run of 400 matching bars
   is one episode, not 400 samples. I wrote "level 9 rests on 2,059,484 bars so the number is precise, not
   noisy". FIX: collapse each match mask into CONTIGUOUS EPISODES and report the episode count as the
   effective n, plus the clean-rate computed once per episode at its first bar.

Everything else is held identical to run 4: the same signals, target 1.3%, MAE gate 0.65%, the same
forward legs, the same vmomo() verified against build_exhv2.momo().

    python3 scn_effective_n.py            # all matches
    python3 scn_effective_n.py --armed    # matches restricted to armed bars
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
from build_scn import SETS, MOMO_LINES, TAPE0, forward_leg
from predict_walk import walk, resolve

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')


def episodes(mask):
    """(starts, n_episodes) — contiguous True runs collapsed to their first bar. THE effective n."""
    s = np.flatnonzero(mask & ~np.r_[False, mask[:-1]])
    return s, len(s)


def main(argv):
    ARMED = '--armed' in argv
    TARGET, MAEMAX, QUORUM = 1.3, 0.65, 1
    HI, LO = R.HI, R.LO
    NL = len(MOMO_LINES)

    ovr = {}
    for s, tf in SETS:
        ovr.update(R._mk('%s_r' % s, tf, R.LN['r']))
    ovr.update(J.LINES)

    d = DatabaseManager(**get_db_config()); d.connect()
    end_ms = int(d.execute('SELECT MAX(kc_timestamp) m FROM kline_collection', fetch=True)[0]['m'])
    d.disconnect()
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
    print('jig build %.1f s   bars %d' % (time.time() - t0, len(ts)), flush=True)

    SV = {}
    for dr in (1, -1):
        SV[dr] = np.vstack([vmomo(RLALL[src_], dr)[0] for _, src_ in MOMO_LINES]).T
    HITL, MAEL = forward_leg(px, 1, TARGET)
    HITS, MAES = forward_leg(px, -1, TARGET)
    print('momo + forward legs  %.1f s' % (time.time() - t0), flush=True)

    W = walk(ts, px, {'jMg1': G1, 'jMg2': G2, 'jr4': RLALL['jr4'], 'jr15': RLALL['jr15'],
                      'jr22': RLALL['jr22']}, HI, LO, end_ms - 168 * 3600000)
    SIG = []
    for w in W:
        r = resolve(w, ts, px, QUORUM)
        if r is None:
            continue
        i, mn, _ = r
        hit, mae = (HITL[i], MAEL[i]) if w['dr'] > 0 else (HITS[i], MAES[i])
        if hit < 0 or not np.isfinite(mae) or mae > MAEMAX:
            continue
        SIG.append((i, w['dr']))
    first_sig = min(ts[i] for i, _ in SIG)
    oos = (ts >= TAPE0) & (ts < first_sig)
    armed = ((G1 >= HI) | (G1 <= LO) | (G2 >= HI) | (G2 <= LO))
    pool = oos & armed if ARMED else oos
    print('signals %d   oos bars %d   armed-oos bars %d   POOL = %s (%d bars)'
          % (len(SIG), int(oos.sum()), int((oos & armed).sum()),
             'armed only' if ARMED else 'all oos', int(pool.sum())), flush=True)

    # ---- base rates, by bar AND by episode ---------------------------------------------------------
    print('\n== BASE RATES ==')
    print('  %-26s %10s %10s %9s %10s' % ('pool', 'bars', 'episodes', 'clean/bar', 'clean/epis'))
    for tag, m in (('all oos bars', oos), ('armed oos bars', oos & armed)):
        for dr, HIT, MAE in ((1, HITL, MAEL), (-1, HITS, MAES)):
            cb = (HIT >= 0) & (MAE <= MAEMAX)
            st, ne = episodes(m)
            print('  %-26s %10d %10d %8.2f%% %9.2f%%'
                  % ('%s dr=%+d' % (tag, dr), int(m.sum()), ne,
                     100.0 * (m & cb).sum() / max(1, m.sum()),
                     100.0 * cb[st].sum() / max(1, ne)))

    # ---- the model, per agreement level, with episodes as the effective n ---------------------------
    # SPLIT BY DIRECTION. The armed base differs by direction (LONG 32.27%, SHORT 35.08%), so an
    # aggregated lift can be nothing but a shift in the direction mix. Reported separately.
    print('\n== MOMO MODEL by DIRECTION, effective n = contiguous episodes ==')
    print('  %-4s %-6s %11s %10s %9s %11s %7s' %
          ('lvl', 'dir', 'match bars', 'episodes', 'bars/epi', 'clean/epis', 'sigs'))
    for lv in range(NL + 1):
        for dtag, dsel in (('LONG', 1), ('SHORT', -1)):
            tb = te = tc = 0; nsig = 0
            for i, dr in SIG:
                if dr != dsel:
                    continue
                ag = (SV[dr] == SV[dr][i]).sum(axis=1)
                m = pool & (ag == lv)
                if not m.any():
                    continue
                nsig += 1
                HIT, MAE = (HITL, MAEL) if dr > 0 else (HITS, MAES)
                cb = (HIT >= 0) & (MAE <= MAEMAX)
                st, ne = episodes(m)
                tb += int(m.sum()); te += ne; tc += int(cb[st].sum())
            if te:
                print('  %-4d %-6s %11d %10d %9.1f %10.2f%% %7d'
                      % (lv, dtag, tb, te, tb / te, 100.0 * tc / te, nsig))
    print('  signal mix: LONG %d  SHORT %d'
          % (sum(1 for _, dr in SIG if dr > 0), sum(1 for _, dr in SIG if dr < 0)))
    print('\ntotal %.0f s' % (time.time() - t0))


if __name__ == '__main__':
    main(sys.argv[1:])
