"""s5m_episode_census.py — does a same-side s5m re-breach carry momentum? (Joe 0710)

Today's spec re-latches the hunt at EVERY 300s seam while s5m is OOB. The fork:
  (e) re-breach is momentum  -> a later seam in the same episode gives a BETTER entry
  (b) re-breach is nothing   -> entry quality is flat across the episode; s5m OOB is just permission

Census over 42d on the 300s seam grid:
  s5m side at each seam -> episodes = maximal runs of the SAME non-zero side.
  For every seam in every episode: enter AGAINST es (short on a hi breach) and score
    MAE/MFE over a 30-min horizon, and the realized net through lr_exit_v2 (cost 0.20%).
  Report by seam index within the episode (1 = the crossing, 2+ = the re-breaches).

Read-only.  Run:  python3 s5m_episode_census.py
"""
import datetime as dtm
from datetime import timezone

import numpy as np

import bias_machine as bm
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import lr_exit_v2
from optimus9.config import get_db_config
from sweep_eval import BASE_BIAS

SPAN_D = 42
COST = 0.20
HORIZON_MIN = 30
HI, LO = 85.0, 15.0


def episodes(side):
    """[(start_idx_in_seams, es, [seam_idx...])] — maximal runs of the same non-zero side."""
    out, run, cur = [], [], 0
    for i, s in enumerate(side):
        if s != 0 and s == cur:
            run.append(i)
        else:
            if cur != 0 and run:
                out.append((cur, run))
            run, cur = ([i], s) if s != 0 else ([], 0)
    if cur != 0 and run:
        out.append((cur, run))
    return out


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000) - 3_600_000
    W = bm.BiasWindow(db, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(db)
    ts, px = np.asarray(W.ts, np.int64), np.asarray(W.px, float)
    s5m = np.asarray(W.line('s5m'), float)

    seam_bars = np.flatnonzero(ts % 300_000 == 0)
    side = np.where(s5m[seam_bars] >= HI, 1, np.where(s5m[seam_bars] <= LO, -1, 0)).astype(int)
    eps = episodes(side)

    lens = np.array([len(r) for (_es, r) in eps])
    flips = sum(1 for i in range(1, len(eps)) if eps[i][0] == -eps[i - 1][0])
    print(f"42d · {len(seam_bars)} seams · s5m OOB at {int((side != 0).sum())} ({100*(side!=0).mean():.1f}%)")
    print(f"episodes {len(eps)}   len p50={np.median(lens):.0f} p90={np.percentile(lens,90):.0f} max={lens.max()}")
    print(f"consecutive episodes that FLIP side: {flips}/{len(eps)-1} ({100*flips/(len(eps)-1):.1f}%)\n")

    # per-seam entries, tagged by index within the episode
    H = HORIZON_MIN * 60 // 5
    n = len(px)
    rows, ent = [], []
    for (es, run) in eps:
        for j, si in enumerate(run):
            k = int(seam_bars[si])
            if k <= 0 or k + 2 >= n:
                continue
            rows.append((k, es, j + 1, len(run)))
            ent.append((int(ts[k]), es, -es, k))          # trade AGAINST es

    by_k = {k: (idx, tot) for (k, _es, idx, tot) in rows}
    mae, mfe = {}, {}
    for (k, es, idx, tot) in rows:
        seg = px[k:k + H]
        e = px[k]; bd = -es
        adv = (np.nanmax(seg) / e - 1) * 100 if bd < 0 else (1 - np.nanmin(seg) / e) * 100
        fav = (1 - np.nanmin(seg) / e) * 100 if bd < 0 else (np.nanmax(seg) / e - 1) * 100
        mae.setdefault(idx, []).append(adv); mfe.setdefault(idx, []).append(fav)

    net = {}
    for (tms, exms, bd, epx, xpx, r, reason) in lr_exit_v2(W, lr, ent, predict=False):
        e = int(np.searchsorted(ts, int(tms))); x = int(np.searchsorted(ts, int(exms)))
        if x <= e or x >= n or e not in by_k:
            continue
        idx = by_k[e][0]
        net.setdefault(idx, []).append(bd * (xpx - epx) / epx * 100.0 - COST)

    print("by seam index within the episode  (1 = the IB->OOB crossing, 2+ = re-breaches)")
    print(f"{'idx':>4} {'n':>6} {'MAE p50':>9} {'MFE p50':>9} {'MFE-MAE':>9} | {'trades':>7} {'mean net':>10} {'win%':>6}")
    for idx in sorted(mae):
        if len(mae[idx]) < 30:
            continue
        a = np.array(net.get(idx, []))
        nm = f"{a.mean():+9.4f}%" if a.size >= 30 else f"{'-':>10}"
        nw = f"{100*(a>0).mean():5.1f}%" if a.size >= 30 else f"{'-':>6}"
        print(f"{idx:>4} {len(mae[idx]):>6} {np.median(mae[idx]):8.3f}% {np.median(mfe[idx]):8.3f}%"
              f" {np.median(mfe[idx])-np.median(mae[idx]):8.3f}% | {a.size:>7} {nm} {nw}")

    print("\nfirst seam only vs all later seams (pooled)")
    for label, sel in (("idx=1", [1]), ("idx>=2", [i for i in sorted(mae) if i >= 2])):
        A = np.concatenate([np.array(mae[i]) for i in sel if i in mae])
        F = np.concatenate([np.array(mfe[i]) for i in sel if i in mfe])
        N = np.concatenate([np.array(net[i]) for i in sel if i in net]) if any(i in net for i in sel) else np.array([])
        print(f"  {label:<7} n={A.size:<6} MAE p50 {np.median(A):.3f}%  MFE p50 {np.median(F):.3f}%"
              f"  net mean {N.mean():+.4f}%  win {100*(N>0).mean():.1f}%  (n={N.size})")
    db.disconnect()


if __name__ == '__main__':
    main()
