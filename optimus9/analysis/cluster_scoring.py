"""
cluster_scoring — r08 KPI: rank AM's top-N centroids by profit banked from
genuine swing-catches. Spec: optimus9-docs-handover/cluster_scoring_design.md.

Input is AM's materialised centroids (am_centroids / am_centroid_signals), NOT
the raw grind firehose. Each centroid is scored two ways over a swept (win, stop)
grid and the cells averaged:

  • near_swing — Σ realised win% over signals that are NEAR a swing AND WALK-WIN
                 (entry value let the trade pass through to profit without being
                 stopped). Winners-only, ≥ 0. PRIMARY sort — "what it caught".
  • total_net  — net over ALL the centroid's signals (+win/−stop/0); off-swing and
                 misfired losers drag it down. SECONDARY sort — "what it cost".

Near a swing = PRE (in the leg, leg's dir; uncapped) ∪ POST (first 2 after the
extreme, same dir, entry within `stop` of it). Swings: swing_detect ZigZag,
significance = win. Outcomes: walk_to_first_cross. Stop grid auto-centred on
GoalAlignment's winners-MAE (mean+k·σ). horizon caps each walk (default 3h).
"""
import numpy as np

from logger import get_logger
from ..db.kline_loader import KlineLoader
from ..compute.swing_detect import find_pivots, legs
from ..compute.outcome_walker import walk_to_first_cross
from .analyze_manager import AnalyzeManager
from .goal_alignment import GoalAlignment


WIN_GRID = (0.5, 0.7, 0.9)
HORIZON  = 2160                        # 3h of 5s bars; caps each outcome walk


class ClusterScoring:
    _TABLE = 'cluster_scores'

    def __init__(self, db, win_grid=WIN_GRID, stop_grid=None, tp_pk=1,
                 horizon=HORIZON, top_n=20, min_signals=30):
        self._db       = db
        self._wins     = tuple(float(w) for w in win_grid)
        self._stops    = tuple(float(s) for s in stop_grid) if stop_grid else None
        self._tp_pk    = int(tp_pk)
        self._horizon  = int(horizon) if horizon else None
        self._top_n    = int(top_n)
        self._min_sig  = int(min_signals)
        self._log      = get_logger(self.__class__.__name__)

    # ── public ───────────────────────────────────────────────────────────────
    def score(self, or_pk) -> list:
        or_pk = int(or_pk)
        combos, ts, close = self._load(or_pk)
        idx_of = {int(t): i for i, t in enumerate(ts.tolist())}
        for c in combos:
            c['idx'] = [(idx_of[t], d) for t, d in c['sig'] if t in idx_of]

        sig_ts = [t for c in combos for t, _ in c['sig']]
        stops  = self._stop_grid(min(sig_ts), max(sig_ts))
        entries = {e for c in combos for e in c['idx']}
        self._log.info(f'or_pk={or_pk}: {len(combos)} centroids, {len(entries)} '
                       f'distinct entries, {len(self._wins)}×{len(stops)} grid')

        for c in combos:
            c['ns'], c['tn'] = [], []
        for win in self._wins:
            lg = [l for l in legs(close, find_pivots(close, win))
                  if abs(l['amp_pct']) >= win]
            for stop in stops:
                outc = self._outcomes(entries, close, win, stop)
                for c in combos:
                    ns, tn = self._score_combo(c['idx'], close, lg, stop, outc)
                    c['ns'].append(ns); c['tn'].append(tn)

        rows = []
        for c in combos:
            rows.append({'am_rank': c['rank'], 'combo': c['combo'],
                         'n_signals':  len(c['idx']),
                         'near_swing': round(float(np.mean(c['ns'])), 4),
                         'total_net':  round(float(np.mean(c['tn'])), 4)})
        rows.sort(key=lambda r: (r['near_swing'], r['total_net']), reverse=True)
        self._persist(or_pk, rows)
        self._log.info(f'cluster_scores: {len(rows)} centroids ranked; '
                       f'top {rows[0]["combo"]} near_swing={rows[0]["near_swing"]:.3f}')
        return rows

    # ── internals ──────────────────────────────────────────────────────────
    def _stop_grid(self, t0_ms, t1_ms):
        """Use an explicit stop grid if given, else auto-centre on the winners-MAE
        (mean+σ) over the SAME window being scored, and bracket it ±0.2."""
        if self._stops:
            return self._stops
        lookback = max(1.0, (int(t1_ms) - int(t0_ms)) / 3600_000)
        info = GoalAlignment(self._db, tp_pk=self._tp_pk, lookback_hours=lookback
                             ).winner_mae_stop(end_ms=int(t1_ms), horizon=self._horizon)
        c = info.get('stop_centre') or 0.4
        grid = tuple(round(max(0.1, c + d), 2) for d in (-0.2, 0.0, 0.2))
        self._log.info(f'auto stop grid from winners-MAE centre {c} '
                       f'({lookback:.0f}h window): {grid}')
        return grid

    def _outcomes(self, entries, close, win, stop) -> dict:
        """{(bar, dir): (contrib, won)} for one (win, stop). contrib +win on a
        winner, -stop on a stop-out, 0.0 if undecided within horizon (won=None)."""
        out = {}
        for i, d in entries:
            wo, so = walk_to_first_cross(close, i, d, win, stop, self._horizon)
            if wo is not None:
                out[(i, d)] = (win, True)
            elif so is not None:
                out[(i, d)] = (-stop, False)
            else:
                out[(i, d)] = (0.0, None)
        return out

    def _score_combo(self, idxdirs, close, lg, stop, outc):
        """Return (near_swing, total_net) for one centroid at one cell.
        near_swing counts ONLY viable entries that WON (a misfire near a swing is
        drag in total_net, not a catch)."""
        total = sum(outc[e][0] for e in idxdirs)

        viable = set()
        by_time = sorted(idxdirs)                       # by bar index = time order
        for leg in lg:
            s, e, dr = leg['start'], leg['end'], leg['dir']
            # PRE: pks inside the leg, in the leg's direction (uncapped)
            for i, d in idxdirs:
                if d == dr and s <= i <= e:
                    viable.add((i, d))
            # POST: first 2 continuation pks after the extreme, entry within `stop`
            peak = close[e]
            lo, hi = ((peak * (1 - stop / 100), peak) if dr > 0
                      else (peak, peak * (1 + stop / 100)))
            cnt = 0
            for i, d in by_time:
                if i > e and d == dr and lo <= close[i] <= hi:
                    viable.add((i, d))
                    cnt += 1
                    if cnt >= 2:
                        break
        near = sum(outc[e][0] for e in viable if outc[e][1] is True)   # winners-only
        return near, total

    def _load(self, or_pk):
        """Read AM's materialised centroids (materialise on first miss), + the
        covering kline window (extended by horizon so late entries can resolve)."""
        am  = AnalyzeManager(self._db)
        top = am.centroids(or_pk)
        if not top:
            self._log.info(f'no materialised centroids for or_pk={or_pk}; building')
            am.materialize_centroids(or_pk, top_n=self._top_n, min_signals=self._min_sig)
            top = am.centroids(or_pk)
        if not top:
            raise ValueError(f'no centroids for or_pk={or_pk}')
        combos = [{'rank': c['rank'], 'combo': c['combo'], 'sig': c['signals']}
                  for c in top]

        all_ts = [t for c in top for t, _ in c['signals']]
        t0, t1 = min(all_ts), max(all_ts)
        pad = (self._horizon or 0) * 5000
        base = KlineLoader(self._db).load_window(self._tp_pk, int(t0), int(t1) + pad)
        return combos, base['timestamp'].to_numpy(), base['close'].to_numpy(dtype=float)

    def _persist(self, or_pk, rows):
        self._db.execute(f'DROP TABLE IF EXISTS {self._TABLE}')
        self._db.execute(f'''CREATE TABLE {self._TABLE} (
            cs_pk BIGINT AUTO_INCREMENT PRIMARY KEY, cs_or_pk INT, rank_n INT,
            am_rank INT, combo VARCHAR(160), n_signals INT,
            near_swing FLOAT, total_net FLOAT)''')
        if not rows:
            return
        data = [(or_pk, n, r['am_rank'], r['combo'], r['n_signals'],
                 r['near_swing'], r['total_net']) for n, r in enumerate(rows, 1)]
        self._db.executemany(
            f'''INSERT INTO {self._TABLE}
                (cs_or_pk, rank_n, am_rank, combo, n_signals, near_swing, total_net)
                VALUES (%s,%s,%s,%s,%s,%s,%s)''', data)
