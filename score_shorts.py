"""score_shorts — MFE-side-aware MAE/MFE for the short-locator signals (Joe 0724). SAVED.

Rule (deduped, multi-dim): gr_dir=short AND gapval_s4<=0 AND max(dtf_now_s15,dtf_now_s22)>=10, one row per T* (min gr_ts).
Measurement (swing_detect 1%, MFE-side aware):
  entry j = the cadence-marker bar. find_pivots(epx,1%).
  offset  = how far DOWN the MFE side the entry fired = (prior_H - entry)/prior_H*100  (the late-entry cost).
  MFE     = max favourable fall from entry to the next L pivot = (entry - min(seg))/entry*100.
  MAE     = max adverse RISE after entry over that seg = max(0, (max(seg)-entry)/entry*100).  <- 0 if clean MFE-side entry.
  full    = the whole swing prior_H->next_L available = (prior_H - next_L)/prior_H*100.
"""
import numpy as np
import linelab as LL
from optimus9.compute.swing_detect import find_pivots
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

STOP = 1.0   # would-stop threshold on MAE (the finisher's ~1% stop, per Joe)


def signals():
    d = DatabaseManager(**get_db_config()); d.connect()
    rows = d.execute("""SELECT gr_ts, gr_ext_ts, gr_time FROM gap_report
        WHERE gr_dir='short' AND gapval_s4<=0 AND GREATEST(dtf_now_s15, dtf_now_s22)>=10
        ORDER BY gr_ts""", fetch=True)
    d.disconnect()
    seen, out = set(), []
    for r in rows:
        if r['gr_ext_ts'] in seen:
            continue
        seen.add(r['gr_ext_ts']); out.append(r)
    return out


def score(entries, ets, epx, pct=1.0):
    piv = find_pivots(epx, pct)
    Hs = [pi for pi, k in piv if k == 'H']
    Ls = [pi for pi, k in piv if k == 'L']
    out = []
    for e in entries:
        j = min(int(np.searchsorted(ets, e['gr_ts'])), len(epx) - 1)
        entry = float(epx[j])
        topi = max([p for p in Hs if p <= j], default=None)
        lowi = min([p for p in Ls if p > j], default=len(epx) - 1)
        seg = epx[j:lowi + 1]
        mfe = (entry - float(seg.min())) / entry * 100
        mae = max(0.0, (float(seg.max()) - entry) / entry * 100)
        offset = ((float(epx[topi]) - entry) / float(epx[topi]) * 100) if topi is not None else None
        full = ((float(epx[topi]) - float(epx[lowi])) / float(epx[topi]) * 100) if topi is not None else None
        out.append(dict(time=e['gr_time'][6:], entry=entry, offset=offset, mfe=mfe, mae=mae, full=full,
                        stop=(mae >= STOP)))
    return out


if __name__ == '__main__':
    cache, ets, epx, names = LL.warm()
    sigs = signals()
    rows = score(sigs, ets, epx, 1.0)
    print('=== %d short signals | swing_detect 1%% | MFE-side aware ===' % len(rows))
    print('time      | entry   | offset(late) | MFE   | MAE   | full swing | outcome')
    banked = 0; mfes = []; maes = []; offs = []
    for r in rows:
        oc = 'STOP ~%.2f%%' % r['mae'] if r['stop'] else 'bank'
        banked += 0 if r['stop'] else 1
        mfes.append(r['mfe']); maes.append(r['mae'])
        if r['offset'] is not None:
            offs.append(r['offset'])
        print('  %s | %7.1f | %s | %5.2f | %5.2f | %s | %s' % (
            r['time'], r['entry'],
            ('%+5.2f%%' % r['offset']) if r['offset'] is not None else '   -   ',
            r['mfe'], r['mae'],
            ('%5.2f%%' % r['full']) if r['full'] is not None else '  -  ', oc))
    print('--- %d/%d bank | med MFE %.2f%% med MAE %.2f%% | med late-entry offset %.2f%% ---' % (
        banked, len(rows), float(np.median(mfes)), float(np.median(maes)),
        float(np.median(offs)) if offs else float('nan')))
