"""
null_baseline — sanity-check the "too good" daily profit two ways:
  1) RANDOM-entry null: do random 5s entries (both dirs) hit +0.9% before −0.33% at the
     same base rate the gated combos do? If yes → the edge is the window/asset, not BL.
  2) RAW vs px_smooth: re-run the win/stop race on raw close vs the DEMA px_smooth — the
     gap is the optimism the smoothing buys.
Reference: gated combos scored ~+0.188 net/trade (px_smooth, 0.33 stop, 0.9 take).
"""
import sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.orchestration import bl_group_grind as G

W, STOP, HORIZON, STEP = 0.9, 0.33, 2160, 8


def race(px, i, d):
    seg = px[i + 1:i + 1 + HORIZON]
    if len(seg) == 0:
        return None
    rel = (seg - px[i]) / px[i] * 100.0 * d
    adv = np.maximum.accumulate(np.maximum(0.0, -rel))
    won = rel >= W
    if won.any():
        wi = int(np.argmax(won)); mbw = float(adv[:wi].max()) if wi > 0 else 0.0
        return W if STOP > mbw else -STOP
    return -STOP if STOP <= float(adv[-1]) else 0.0


def stats(px, label):
    n = len(px)
    outs = [race(px, i, d) for i in range(0, n - HORIZON, STEP) for d in (1, -1)]
    outs = [o for o in outs if o is not None]
    a = np.array(outs)
    won = int((a == W).sum()); stopd = int((a == -STOP).sum()); dec = won + stopd
    print(f'  {label:<22} n={len(a):>5}  win%={(won/dec*100 if dec else 0):5.1f}  '
          f'net/trade={a.mean():+.4f}  (won {won} / stopped {stopd} / undecided {len(a)-dec})')
    return a.mean()


def main():
    G.prepare()
    base, mask = G._CTX['base'], G._CTX['mask']
    px_s = np.asarray(G._CTX['px'], float)
    raw  = base['close'].to_numpy(dtype=float)[mask]
    print(f'NULL BASELINE — random entries (every {STEP}th bar, both dirs), {W} take / {STOP} stop')
    print(f'  window {len(px_s)} bars · gated combos reference: ~+0.188 net/trade (px_smooth)')
    print()
    m_smooth = stats(px_s, 'random @ px_smooth')
    m_raw    = stats(raw,  'random @ raw close')
    print()
    print(f'  px_smooth optimism (smooth − raw): {m_smooth - m_raw:+.4f} net/trade')
    print(f'  if random@smooth ≈ +0.188 → the gate adds ~nothing; the edge is the window/asset')


if __name__ == '__main__':
    main()
