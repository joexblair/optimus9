"""bob_dive — test Joe's BOBBING note as he actually stated it. Joe 0803 04:05.

    "if a Mage is bobbing on a boundary line, a higher TF Mage is making it's way to the same boundary
     <-this is gold: now you know which HTF Mage to track to its oob"

WHAT seq_sweep.py GOT WRONG. It encoded 'did an HTF ARRIVE at this boundary before s4 did'. The note says
two different things: a fast Mage is BOBBING — repeatedly touching the boundary, which is a COUNT and was
never computed anywhere — and a higher-TF Mage is MAKING ITS WAY TO it, which is an approach, not an
arrival. Neither was measured.

AND THE NOTE IS A POINTER, NOT A TIMING SIGNAL (handover 2). "now you know which HTF Mage to track to its
oob" is a claim about WHICH LINE to watch. That is testable without any trade outcome at all, on every
bobbing episode rather than only on armed bars, which is roughly an order of magnitude more data.

SO THERE ARE TWO TESTS, AND THE FIRST ONE IS THE NOTE ITSELF

  TEST A — THE POINTER. When line L is bobbing at boundary S, does an HTF arrive at S sooner than it does
  when L is not bobbing? Compare the time-to-next-HTF-arrival under bobbing against the same quantity
  under no bobbing. No trade, no MAE, no clean flag — just the note's own claim.

  TEST B — THE CONSEQUENCE. On armed bars, does bobbing-plus-an-approaching-HTF separate clean from dirty.

DEFINITIONS, all swept rather than chosen
  bobbing      >= K arrivals of line L at boundary S within the trailing W bars. K in 2,3,4 ; W in
               60 / 180 / 720 bars = 5 / 15 / 60 min. The window IS the definition of the mechanic, so it
               is a swept parameter, not a cap on the analysis.
  approaching  the HTF's value has moved toward boundary S over the trailing W bars.
  the ladder   fast lines g5 g15 s30 s1 s2 s4 ; HTFs h30 h45 h60 h90. bb 37|0.7|close throughout.

CAUSAL. Counts and approaches read only bars <= the current one. Time-to-next-arrival is the forward
quantity being PREDICTED in test A, and it is never an input.

    python3 bob_dive.py
"""
import os, sys, time, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '4')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_rpl_jig as J
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
from build_scn import TAPE0

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
FAST = [('g5', 5.0 / 60), ('g15', 0.25), ('s30', 0.5), ('s1', 1.0), ('s2', 2.0), ('s4', 4.0)]
HTFS = [('h30', 30.0), ('h45', 45.0), ('h60', 60.0), ('h90', 90.0)]
WINS = [60, 180, 720]                                   # 5 / 15 / 60 min at the 5 s grid
KS = [2, 3, 4]


def roll_count(ev, w):
    """count of True in the trailing w bars ending at each bar, inclusive. Causal."""
    c = np.cumsum(np.r_[0, ev.astype(np.int32)])
    out = np.empty(len(ev), np.int32)
    idx = np.arange(len(ev))
    lo = np.maximum(0, idx - w + 1)
    out = c[idx + 1] - c[lo]
    return out


def next_event_bars(ev):
    """bars until the NEXT True at or after each bar; -1 if none. Forward — the thing being predicted."""
    n = len(ev); idx = np.arange(n)
    nxt = np.full(n, -1, np.int64)
    pos = np.where(ev, idx, n + 1)
    m = np.minimum.accumulate(pos[::-1])[::-1]
    ok = m <= n
    nxt[ok] = m[ok] - idx[ok]
    return nxt


def main(argv):
    HI, LO = R.HI, R.LO
    ovr = {}
    for nm, tf in FAST + HTFS:
        ovr.update(bbline('bb_%s' % nm, tf, length=37, mult=0.7, src='close'))
    d = DatabaseManager(**get_db_config()); d.connect()
    end_ms = int(d.execute('SELECT MAX(kc_timestamp) m FROM kline_collection', fetch=True)[0]['m'])
    hours = int((end_ms - TAPE0) / 3600000) + 1
    t0 = time.time()
    with Jig(end_ms, hours=hours, warmup=J.WIN_WARMUP, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64)
        VF = {nm: np.asarray(j.W.line('bb_%s' % nm), float) for nm, _ in FAST}
        VH = {nm: np.asarray(j.W.line('bb_%s' % nm), float) for nm, _ in HTFS}
    n = len(ts)
    d.disconnect()
    print('jig build %.1f s   bars %d' % (time.time() - t0, n), flush=True)

    ARR = {}
    for side, sgn in (('hi', 1), ('lo', -1)):
        for nm in list(VF) + list(VH):
            v = VF.get(nm, VH.get(nm))
            oob = (v >= HI) if side == 'hi' else (v <= LO)
            ARR[(nm, side)] = oob & ~np.r_[False, oob[:-1]]

    print('\n== TEST A — THE POINTER: does bobbing predict an HTF arriving at the same boundary? ==')
    print('%-5s %-5s %4s %5s %10s %12s %12s %9s %9s' %
          ('side', 'line', 'K', 'W', 'bob bars', 'med bars-to', 'med no-bob', 'ratio', 'n_bob'))
    for side in ('hi', 'lo'):
        anyh = np.zeros(n, bool)
        for nm, _ in HTFS:
            anyh |= ARR[(nm, side)]
        nxt = next_event_bars(anyh)
        have = nxt >= 0
        for lnm, _ in FAST[:4]:
            for W in WINS:
                cnt = roll_count(ARR[(lnm, side)], W)
                for K in KS:
                    bob = (cnt >= K) & have
                    nob = (cnt == 0) & have
                    if bob.sum() < 2000 or nob.sum() < 2000:
                        continue
                    mb = float(np.median(nxt[bob])); mn = float(np.median(nxt[nob]))
                    print('%-5s %-5s %4d %5d %10d %12.0f %12.0f %9.3f %9d'
                          % (side, lnm, K, W, int(bob.sum()), mb, mn, mb / max(mn, 1), int(bob.sum())))

    print('\n== TEST A2 — WHICH HTF: given bobbing, is the NEAREST HTF the one that arrives first? ==')
    print('%-5s %-5s %4s %5s %10s %11s %11s %8s' %
          ('side', 'line', 'K', 'W', 'episodes', 'nearest 1st', 'chance', 'lift'))
    for side in ('hi', 'lo'):
        bnd = HI if side == 'hi' else LO
        DIST = np.vstack([(bnd - VH[nm]) if side == 'hi' else (VH[nm] - bnd) for nm, _ in HTFS]).T
        NXT = np.vstack([next_event_bars(ARR[(nm, side)]) for nm, _ in HTFS]).T
        okall = (NXT >= 0).all(1) & np.isfinite(DIST).all(1)
        near = np.argmin(np.where(np.isfinite(DIST), DIST, np.inf), axis=1)
        first = np.argmin(np.where(NXT >= 0, NXT, np.iinfo(np.int64).max), axis=1)
        for lnm, _ in FAST[:4]:
            for W in (180, 720):
                cnt = roll_count(ARR[(lnm, side)], W)
                for K in (2, 3):
                    m = (cnt >= K) & okall
                    ep = m & ~np.r_[False, m[:-1]]
                    if ep.sum() < 200:
                        continue
                    hit = (near[ep] == first[ep]).mean()
                    print('%-5s %-5s %4d %5d %10d %10.1f%% %10.1f%% %+8.1f'
                          % (side, lnm, K, W, int(ep.sum()), 100 * hit, 25.0, 100 * hit - 25.0))
    print('\ntotal %.0f s' % (time.time() - t0))


if __name__ == '__main__':
    main(sys.argv[1:])
