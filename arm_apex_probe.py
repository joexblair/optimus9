"""arm_apex_probe.py — ARM DELAY SPEC 0709: momentum-apex hunt, event trace. (Joe 0710)

Read-only. Builds every s{tf}{r,m,Mage} line for tf in [5,7,9..45,50] as in-memory overrides (emerging,
causal), then walks the tape per-bar and records EVERY event chronologically:

    HUNT   s5m breaches on a 300s seam  -> es latched (hi = hunting a short)
    PRED   s{tf}r predicted (tolerance TOL) at a 1/3-TF seam
    BREACH s{tf}r crosses OOB on es
    CLIMB  apex moves up a TF (the HTF r has momentum to contribute)
    CURL   s{tf}Mage (or s{tf}r) coarse-curls against es at a 1/4-TF seam (3-seam triangle)
    ARM    curl + HTF has nothing + apex r back IB
    BACK   backstop: sub_apex and apex r breached together, both curl together
    CANCEL s5m returns IB  |  opposite-side s5m breach

Both curl variants are traced side by side: --curl mage (spec) and --curl r (Joe 0710, "no harm in testing").

Run:  python3 arm_apex_probe.py --at "2026-07-08 06:01" --span 3
"""
import argparse
import datetime as dtm
from datetime import timezone

import numpy as np

import bias_machine as bm
from optimus9 import DatabaseManager
from optimus9.compute.breaching_line import predict_breach, FENCE_HI, FENCE_LO
from optimus9.analysis.lr_v2 import _curl_detect
from optimus9.config import get_db_config
from sweep_eval import BASE_BIAS

HI, LO = 85.0, 15.0
FENCE_HI, FENCE_LO = 70.0, 30.0
DAY = 86_400_000

TFS = [5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 50]


def predict_tol(k, pmin, pmaj, tol=0.0):
    """DEPRECATED shim — delegates to the one prediction impl. Use jig.causal.predict_set()."""
    return predict_breach(k, pmin, pmaj, HI, LO, FENCE_HI, FENCE_LO, tol)


def seam_mask(ts, seam_ms, anchor):
    return ((ts - anchor) % seam_ms) == 0


def curl_bars(ts, vals, seam_ms, anchor, direction):
    """Coarse-curl fire bars (5s indices) for `direction` (+1 trough / -1 peak)."""
    m = seam_mask(ts, seam_ms, anchor)
    hits = _curl_detect(ts[m], np.asarray(vals, float)[m], direction)
    return {int(np.searchsorted(ts, t)) for t in hits}


def overrides(m_len):
    o = {}
    for tf in TFS:
        s = tf * 60
        o[f's{tf}r'] = (s, ('k', 5, 6, 5, 'close'), 'emerging')       # 5|5|6|close  (k_len|rsi|stc)
        o[f's{tf}m'] = (s, ('bb', m_len, 0.5, 'ohlc4'), 'emerging')
        o[f's{tf}Mage'] = (s, ('bb', 37, 0.7, 'ohlc4'), 'emerging')
    return o


def hhmmss(t):
    return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%m-%d %H:%M:%S')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--at', default='2026-07-08 06:01')
    ap.add_argument('--span', type=float, default=3.0, help='hours of tape to trace, centred back from --at+1h')
    ap.add_argument('--tol', type=float, default=4.0)
    ap.add_argument('--m-len', type=int, default=7)
    ap.add_argument('--curl', default='mage', choices=['mage', 'r', 'both'])
    a = ap.parse_args()

    at = int(dtm.datetime.strptime(a.at, '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc).timestamp() * 1000)
    end = at + 3_600_000

    db = DatabaseManager(**get_db_config()); db.connect()
    W = bm.BiasWindow(db, end, lookback=24, warmup=90, cfg=bm.BiasConfig(**BASE_BIAS),
                      line_overrides=overrides(a.m_len), lean=True)
    ts, px = np.asarray(W.ts, np.int64), np.asarray(W.px, float)
    anchor = (int(ts[0]) // DAY) * DAY

    L = {}
    for tf in TFS:
        r, m, M = (np.asarray(W.line(f's{tf}{x}'), float) for x in ('r', 'm', 'Mage'))
        L[tf] = dict(
            r=r, m=m, M=M,
            pred=predict_tol(r, m, M, a.tol),
            r_oob=np.where(r >= HI, 1, np.where(r <= LO, -1, 0)).astype(np.int8),
            m_oob=np.where(m >= HI, 1, np.where(m <= LO, -1, 0)).astype(np.int8),
            pseam=seam_mask(ts, (tf * 60 // 3) * 1000, anchor),
            cseam=seam_mask(ts, (tf * 60 // 4) * 1000, anchor),
            curlM={d: curl_bars(ts, M, (tf * 60 // 4) * 1000, anchor, d) for d in (1, -1)},
            curlR={d: curl_bars(ts, r, (tf * 60 // 4) * 1000, anchor, d) for d in (1, -1)},
        )

    # per-seam latched prediction state (spec: "test r prediction at every 1/3 TF seam")
    for tf in TFS:
        d = L[tf]; p = np.zeros(len(ts), np.int8); cur = 0
        for k in range(len(ts)):
            if d['pseam'][k]:
                cur = int(d['pred'][k])
            p[k] = cur
        d['pred_seam'] = p

    s5m_oob = L[5]['m_oob']
    seam300 = seam_mask(ts, 300_000, anchor)

    k0 = int(np.searchsorted(ts, at - int(a.span * 3_600_000)))
    k1 = int(np.searchsorted(ts, end))
    ev = []

    def log(k, kind, txt):
        ev.append((int(ts[k]), kind, txt, float(px[k])))

    which = ['mage', 'r'] if a.curl == 'both' else [a.curl]
    for variant in which:
        ck = 'curlM' if variant == 'mage' else 'curlR'
        hunting = False; es = 0; apex = 5; sub = 5; seen_pred = set(); seen_brc = set()
        armed_at = None
        for k in range(k0, k1):
            if not hunting:
                if seam300[k] and s5m_oob[k] != 0:
                    hunting, es, apex, sub = True, int(s5m_oob[k]), 5, 5
                    seen_pred.clear(); seen_brc.clear()
                    log(k, 'HUNT', f'[{variant}] s5m breach es={es:+d}  s5m={L[5]["m"][k]:.1f}')
                continue

            if seam300[k] and s5m_oob[k] == -es:
                log(k, 'CANCEL', f'[{variant}] opposite s5m breach'); hunting = False; continue
            if seam300[k] and s5m_oob[k] == 0 and apex == 5 and 5 not in seen_pred:
                log(k, 'CANCEL', f'[{variant}] s5m back IB, no s5r prediction'); hunting = False; continue

            for tf in TFS:
                d = L[tf]
                if d['pred_seam'][k] == es and tf not in seen_pred:
                    seen_pred.add(tf); log(k, 'PRED', f'[{variant}] s{tf}r predicted  r={d["r"][k]:.1f} m={d["m"][k]:.1f} Mage={d["M"][k]:.1f}')
                if d['r_oob'][k] == es and tf not in seen_brc:
                    seen_brc.add(tf); log(k, 'BREACH', f'[{variant}] s{tf}r OOB  r={d["r"][k]:.1f}')

            if apex == 5 and L[5]['pred_seam'][k] != es:
                continue                                                # pre-loop: wait for s5r prediction

            # CLIMB — the HTF r still has momentum to contribute
            while True:
                i = TFS.index(apex)
                if i + 1 >= len(TFS):
                    break
                nxt = TFS[i + 1]
                d = L[nxt]
                if d['pred_seam'][k] == es or d['r_oob'][k] == es:
                    sub, apex = apex, nxt
                    log(k, 'CLIMB', f'[{variant}] apex {sub}->{apex}  '
                                    f'(pred={d["pred_seam"][k]:+d} r={d["r"][k]:.1f})')
                else:
                    break

            i = TFS.index(apex)
            nxt = TFS[i + 1] if i + 1 < len(TFS) else None
            d = L[apex]
            if d['cseam'][k] and k in d[ck][-es]:
                htf = nxt is not None and (L[nxt]['pred_seam'][k] == es or L[nxt]['r_oob'][k] == es)
                ib = LO < d['r'][k] < HI
                log(k, 'CURL', f'[{variant}] s{apex}{"Mage" if variant == "mage" else "r"} curls  '
                               f'htf_momentum={htf}  s{apex}r={d["r"][k]:.1f} ib={ib}')
                if not htf and ib:
                    log(k, 'ARM', f'[{variant}] apex TF{apex}  es={es:+d}  px={px[k]:.8f}')
                    armed_at = (int(ts[k]), apex); hunting = False; continue

            # BACKSTOP — top two r's breached together, both curl together
            if sub != apex and sub in seen_brc and apex in seen_brc:
                if k in L[apex][ck][-es] and k in L[sub][ck][-es]:
                    log(k, 'BACK', f'[{variant}] backstop arm  apex={apex} sub={sub}')
                    armed_at = (int(ts[k]), apex); hunting = False

        print(f"\n[{variant}] armed_at = {hhmmss(armed_at[0]) if armed_at else None}"
              f"  apex TF{armed_at[1] if armed_at else '-'}")

    ev.sort()
    print(f"\ntape {hhmmss(ts[k0])} -> {hhmmss(ts[k1 - 1])}   tol={a.tol}  m_len={a.m_len}  "
          f"target = 07-08 06:01 TF19\n")
    print(f"{'time':<16} {'event':<7} {'px':>11}  detail")
    print('-' * 116)
    for (t, kind, txt, p) in ev:
        print(f"{hhmmss(t):<16} {kind:<7} {p:>11.8f}  {txt}")
    db.disconnect()


if __name__ == '__main__':
    main()
