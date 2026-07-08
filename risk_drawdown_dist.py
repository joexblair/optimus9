"""risk_drawdown_dist.py — ground the RiskGovernor drawdown thresholds in v2_walk's actual equity-drawdown
profile (Joe 0708), instead of hand-picked 5/10/15%. Walk the shipping stack's compounding equity, track the
running drawdown from high-water at each trade, and read its distribution. The dd steps should sit where
drawdown becomes ABNORMAL for this strategy (don't deleverage during normal drawdowns; do when it's a tail).
Read-only. Run:  python3 risk_drawdown_dist.py"""
import numpy as np
from v2walk_ad_pnl import get_trades, START, LEV, MAX_LOT, COST


def equity_curve(trades, stop):
    acct = START; curve = [acct]
    for t in trades:
        if acct <= 0:
            break
        r = -stop if (stop is not None and t['mae'] <= -stop) else t['ret']
        acct += min(MAX_LOT, acct * LEV / t['epx']) * t['epx'] * (r - COST) / 100.0
        curve.append(max(acct, 0.0))
    return np.array(curve)


def drawdowns(curve):
    peak = np.maximum.accumulate(curve)
    return (peak - curve) / peak * 100.0                    # % below the running high-water, at each step


def main():
    tr = get_trades()
    # use the profit-max stop curve (the intended operating config) — realistic drawdown shape
    stop = 0.90
    dd = drawdowns(equity_curve(tr, stop))
    dd_pos = dd[dd > 1e-9]                                   # in-drawdown steps only (exclude at-peak)
    print("=== v2_walk_ad equity drawdown (%d trades, stop %.2f%%, %d in-drawdown steps) ===" %
          (len(tr), stop, len(dd_pos)))
    print("  time in drawdown: %.0f%%" % (100.0 * len(dd_pos) / len(dd)))
    for p in (50, 75, 90, 95, 99):
        print("  p%-3d = %5.2f%%" % (p, np.percentile(dd_pos, p)))
    print("  max  = %5.2f%%" % dd.max())
    p90, p97, mx = np.percentile(dd_pos, 90), np.percentile(dd_pos, 97), dd.max()
    print("\nPROPOSED dd thresholds (ground the governor, deleverage only when ABNORMAL):")
    print("  dd_step1 = %.1f%%  (p90 — above normal drawdown → ease to x0.5)" % p90)
    print("  dd_step2 = %.1f%%  (p97 — deep → x0.25)" % p97)
    print("  dd_halt  = %.1f%%  (~max %.1f → veto adds + x0)" % (max(mx, p97 * 1.5), mx))


if __name__ == "__main__":
    main()
