"""sweep_live_stop - the 0.05 cap ladder RE-WALKED at every rung, with the stop as a live exit.

Joe 0929-late: *"re-sweep the ladder against the live stop"*.

WHY IT HAD TO BE RE-SWEPT. The ladder that produced the 0.70 ruling was computed on ONE trade set:
sweep_mae_cap.py walks once with no stop, then scores that fixed set of 753 trades at every cap. The
trade count is 753 on all 80 rungs.

With the stop LIVE it is a third exit racing the opposing-dr sig_utc and the dr-flip backstop - the
first to fire ends the trade. A tighter cap ends trades sooner, frees the book sooner, and lets
ungated sig_utc bars that are currently INERT open new trades. So EVERY RUNG HAS ITS OWN TRADE
POPULATION, and the ladder and the trade count are coupled.

    python3 sweep_live_stop.py

Every rung from 0.05 to 4.00 is printed. Nothing is truncated and nothing is ranked away.
"""
import sys, io, numpy as np, datetime as dt
sys.path.insert(0, '/home/joe/thecodes')
_e = sys.stderr; sys.stderr = io.StringIO()
import sweep_v3_signal as S
from measure_live_stop import build, FROM_MS, TO_MS
sys.stderr = _e


def walk_live(opens, dr, PX, start, end, cap):
    """The banked walk with the stop live. cap=None -> no stop at all.

    PX is a plain Python list of floats - scalar access dominates an 80-rung sweep.
    """
    O = set(int(x) for x in opens); start = max(1, int(start)); out = []
    o = d0 = None; left = False; ob = None; e = 0.0
    for k in range(start, int(end) + 1):
        if o is not None:
            d = int(dr[k])
            if cap is not None and -((PX[k] - e) / e * 100.0) * d0 <= -cap:
                out.append((o, k, d0, ob, 'stop')); o = None
                continue                                  # the stop wins the bar
            if d == -d0 and d != 0:
                left = True
            if left and d == d0 and d != int(dr[k - 1]):
                out.append((o, k, d0, ob, 'dr-flip')); o = None
                continue                                  # the flip wins the bar
        if k in O:
            d = int(dr[k])
            if o is not None and not (d == -d0 and d != 0):
                continue                                  # same-dr sig_utc is INERT
            if o is not None:
                out.append((o, k, d0, ob, 'sig_utc'))
            o, d0, ob, left, e = k, d, 'sig_utc', False, PX[k]
    return out


def score(px, T, cap):
    """-cap for a stopped trade, else mfe - mae over its span. Joe's rule."""
    tot = 0.0; smae = 0.0; w = 0; ns = 0
    for (o, c, d, _ob, _cb) in T:
        e = float(px[o])
        adv = -((np.asarray(px[o:c + 1], float) - e) / e * 100.0) * d
        mae = float(-np.minimum.accumulate(adv)[-1])
        if cap is not None and mae >= cap:
            ns += 1; tot += -cap; smae += cap
        else:
            v = float(adv.max()) - mae
            tot += v; smae += mae
            if v > 0: w += 1
    return len(T), w, ns, smae, tot


def main():
    rig = S.Rig((FROM_MS, TO_MS)); px = rig.px; B = rig.B
    PX = [float(x) for x in px]
    sig, opens = build(rig)
    st = min(opens)
    days = (TO_MS - FROM_MS) / 86400000.0
    print('B|window %s .. %s = %.0f days' % (
        dt.datetime.fromtimestamp(FROM_MS/1000, dt.timezone.utc).strftime('%Y-%m-%d'),
        dt.datetime.fromtimestamp(TO_MS/1000, dt.timezone.utc).strftime('%Y-%m-%d'), days))
    print('B|sig bars %d|rule#1 open %d' % (len(sig), len(opens)))
    print()
    print('C|cap %|trades|net>0|net>0 %|stopped|stopped %|MAE sum|net sum|NET PER TRADE')
    best = None
    caps = [round(0.05 * i, 2) for i in range(1, 81)]          # 0.05 .. 4.00, every rung
    for cap in caps + [None]:
        T = walk_live(opens, rig.DRW, PX, st, B, cap)
        n, w, ns, smae, tot = score(px, T, cap)
        per = tot / n
        lab = ('%.2f' % cap) if cap is not None else 'no stop'
        print('C|%s|%d|%d|%.1f%%|%d|%.1f%%|%.3f|%+.3f|%+.4f'
              % (lab, n, w, 100.0*w/n, ns, 100.0*ns/n, smae, tot, per))
        sys.stdout.flush()
        if cap is not None and (best is None or per > best[1]):
            best = (cap, per, n, w, ns, tot)
    print()
    print('C|BEST per trade|cap %.2f|net per trade %+.4f|trades %d|net>0 %d|stopped %d|net sum %+.3f'
          % (best[0], best[1], best[2], best[3], best[4], best[5]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
