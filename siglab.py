"""siglab — bi-directional short/long signal primitives (Joe 0724). Shared core for the gap-signal sweeps.

Convention: d = -1 SHORT (s4 HI episode), +1 LONG (s4 LO episode). Everything mirrors.
  T*        = the s4x episode extreme within LOOKBACK of the cadence marker (argmax on HI / argmin on LO).
  roll      = the fast s4 exhausted — x didn't clear its own mid m in the excursion dir:  d * gap_s4 >= 0
              (SHORT: x peaked <= m -> gap_s4<=0;  LONG: x troughed >= m -> gap_s4>=0).
  strength  = how much an HTF is stretched the FAVOURABLE way vs s4 (both dirs: larger = stronger):
              SHORT gap_htf-gap_s4 (HTF more overbought) ; LONG gap_s4-gap_htf (HTF more oversold).
  score     = swing-to-pivot @1%: MFE favourable to the next pivot, MAE adverse (0 if entry already favourable).
              SHORT fav=fall to next L ; LONG fav=rise to next H. offset = how far past the swing pivot we entered.
"""
import numpy as np
import linelab as LL
import optimus9.orchestration.rpl_walk as R
from optimus9.compute.swing_detect import find_pivots


def strength(gap_htf, gap_s4, d):
    return (gap_s4 - gap_htf) if d == 1 else (gap_htf - gap_s4)


class Lab:
    def __init__(self, cache, ets, epx, lookback_bars=216, swing_pct=2.0):   # Joe 0725: 2% operating yardstick (no entries lost vs 1%)
        self.ts = cache.ts; self.ets = ets; self.epx = epx; self.lb = lookback_bars
        piv = find_pivots(epx, swing_pct)
        self.Hs = [p for p, k in piv if k == 'H']; self.Ls = [p for p, k in piv if k == 'L']
        self.s4x = LL.line(cache, 's4x'); self.s4m = LL.line(cache, 's4m')

    def extreme(self, t, d):
        """T* index of the most recent s4x-OOB(dir) run at/before t, else None. HI->argmax, LO->argmin."""
        i = int(np.searchsorted(self.ts, t))
        oob = (self.s4x <= R.LO) if d == 1 else (self.s4x >= R.HI)
        j = i
        while j >= 0 and j > i - self.lb and not oob[j]:
            j -= 1
        if j < 0 or j <= i - self.lb or not oob[j]:
            return None
        lo = j
        while lo > 0 and oob[lo - 1]:
            lo -= 1
        hi = j
        while hi < len(oob) - 1 and oob[hi + 1]:
            hi += 1
        seg = self.s4x[lo:hi + 1]
        return lo + (int(np.argmin(seg)) if d == 1 else int(np.argmax(seg)))

    def gap_s4(self, star):
        return float(self.s4x[star] - self.s4m[star])

    def leg(self, t0, t1, d):
        """Point-to-point MFE/MAE: hold dir d from entry t0 until the next flip t1 (t1=None -> run to end).
        -> (entry_px, exit_px, mfe, mae). MFE favourable, MAE adverse (0 if never adverse)."""
        i = int(np.searchsorted(self.ets, t0))
        j = len(self.epx) - 1 if t1 is None else min(int(np.searchsorted(self.ets, t1)), len(self.epx) - 1)
        if j <= i:
            j = min(i + 1, len(self.epx) - 1)
        seg = self.epx[i:j + 1]; entry = float(self.epx[i])
        if d == 1:
            mfe = (float(seg.max()) - entry) / entry * 100; mae = max(0.0, (entry - float(seg.min())) / entry * 100)
        else:
            mfe = (entry - float(seg.min())) / entry * 100; mae = max(0.0, (float(seg.max()) - entry) / entry * 100)
        return entry, float(self.epx[j]), mfe, mae

    def score(self, t, d):
        """-> (offset, mfe, mae) in %, swing-to-pivot @1%, direction-aware."""
        j = min(int(np.searchsorted(self.ets, t)), len(self.epx) - 1); entry = float(self.epx[j])
        if d == 1:                                                        # LONG: favourable = up, to next H
            hi = min([p for p in self.Hs if p > j], default=len(self.epx) - 1); seg = self.epx[j:hi + 1]
            mfe = (float(seg.max()) - entry) / entry * 100
            mae = max(0.0, (entry - float(seg.min())) / entry * 100)
            loi = max([p for p in self.Ls if p <= j], default=None)
            off = ((entry - float(self.epx[loi])) / float(self.epx[loi]) * 100) if loi is not None else None
        else:                                                             # SHORT: favourable = down, to next L
            loi = min([p for p in self.Ls if p > j], default=len(self.epx) - 1); seg = self.epx[j:loi + 1]
            mfe = (entry - float(seg.min())) / entry * 100
            mae = max(0.0, (float(seg.max()) - entry) / entry * 100)
            topi = max([p for p in self.Hs if p <= j], default=None)
            off = ((float(self.epx[topi]) - entry) / float(self.epx[topi]) * 100) if topi is not None else None
        return off, mfe, mae


def markers(cache, lab, cadence, S, E, htf_tfs, d):
    """Precompute the deduped rolled-s4 markers of direction d over [S,E]:
    each -> {star, gap_s4, str{tf: strength}, off, mfe, mae}.  Rule callers filter on str/gap later."""
    cad = LL.xm_cross(cache, cadence, wob=6, lookback_tf=3, min_dwell_s=180, align_line=None, start=S, end=E)
    HX = {tf: LL.line(cache, 's%dx' % tf) for tf in htf_tfs}
    HM = {tf: LL.line(cache, 's%dm' % tf) for tf in htf_tfs}
    seen, out = set(), []
    for tms, bd in cad:
        if bd != d:
            continue
        star = lab.extreme(tms, d)
        if star is None or star in seen:
            continue
        seen.add(star)
        g4 = lab.gap_s4(star)
        if d * g4 < 0:                                                    # s4 must have exhausted (rolled)
            continue
        st = {tf: strength(float(HX[tf][star] - HM[tf][star]), g4, d) for tf in htf_tfs}
        off, mfe, mae = lab.score(tms, d)
        out.append(dict(tms=tms, d=d, star=star, gap_s4=g4, strn=st, off=off, mfe=mfe, mae=mae))
    return out
