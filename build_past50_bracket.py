"""build_past50_bracket — stop/TP bracket optimization for the past-50 mechanic (Joe 0726). SAVED.
Turns the MFE/MAE envelope into a realized-ish bracket P&L:
  STEP 1 (stop, from MAE): grid stop S; a trade stopped (-S) if MAE>=S, else 'let it run' to MFE. Pick S* = max mean P&L.
  STEP 2 (TP, from MFE | S*): grid TP T; stopped(-S*) if MAE>=S*, else +T if MFE>=T, else flat(0). Pick T* = max mean.
Ambiguity (MAE>=S AND MFE>=T): assume STOP hits first (conservative, path unknown). Reports MEAN-primary (+median),
flags NO costs (subtract ~fee+funding+slippage per round-trip for realized). In-sample on the 21-day set (bracket params).
"""
import numpy as np
import build_past50_sweep as S
import build_past50 as P

CFG = dict(wob=5, oob=87, dev=48, seam=2)      # x×Mage best from the all-dials sweep
SEED, KDAYS = 21, 21
STOPS = np.round(np.arange(0.25, 4.01, 0.25), 2)
TPS = np.round(np.arange(0.25, 8.01, 0.25), 2)


def trades():
    days = S.random_days(SEED, KDAYS)
    ons = [(i, de) for i, de in S.qualify(CFG['oob'], CFG['seam']) if any(a <= P.te[i] < b for a, b in days)]
    F = S.fires(CFG['wob'], CFG['dev'], CFG['oob'], 'x')
    tr = S.deduped(ons, F)
    mfe, mae = [], []
    for (ts, tf), d in tr.items():
        _, mf, ma = P.lab.score(ts, d); mfe.append(mf); mae.append(ma)
    return np.array(mfe), np.array(mae)


def stat(pnl):
    return pnl.mean(), np.median(pnl), 100 * np.mean(pnl > 0), pnl.std()


if __name__ == '__main__':
    mfe, mae = trades()
    N = len(mfe)
    print('=== past-50 x×Mage best | %d trades / 21 days | MFE mean %.2f  MAE mean %.2f ===' % (N, mfe.mean(), mae.mean()))

    # STEP 1 — stop from MAE (survivors 'run to MFE')
    print('\n-- STEP 1: STOP (from MAE) | survivor captures MFE --')
    best_s = None
    for s in STOPS:
        pnl = np.where(mae >= s, -s, mfe)
        m, md, w, sd = stat(pnl)
        if best_s is None or m > best_s[1]:
            best_s = (s, m, md, w, sd)
    for s in STOPS:
        pnl = np.where(mae >= s, -s, mfe); m = pnl.mean()
        mark = '  <== S*' if s == best_s[0] else ''
        if s in (STOPS[0],) or abs(s - best_s[0]) <= 0.75 or s == STOPS[-1]:
            print('  stop %.2f | mean %+.3f  median %+.3f  win %2.0f%%  stopped %2.0f%%%s' % (
                s, m, np.median(pnl), 100 * np.mean(pnl > 0), 100 * np.mean(mae >= s), mark))
    Sstar = best_s[0]
    print('  -> S* = %.2f  (mean %+.3f, %.0f%% of trades stopped)' % (Sstar, best_s[1], 100 * np.mean(mae >= Sstar)))

    # STEP 2 — TP from MFE given S*
    print('\n-- STEP 2: TP (from MFE | stop S*=%.2f) | stop-first on ambiguity --' % Sstar)
    stopped = mae >= Sstar
    best_t = None
    for t in TPS:
        pnl = np.where(stopped, -Sstar, np.where(mfe >= t, t, 0.0))
        m = pnl.mean()
        if best_t is None or m > best_t[1]:
            best_t = (t, m, np.median(pnl), 100 * np.mean(pnl > 0))
    for t in TPS:
        pnl = np.where(stopped, -Sstar, np.where(mfe >= t, t, 0.0)); m = pnl.mean()
        if abs(t - best_t[0]) <= 1.0 or t in (TPS[0], TPS[-1]):
            mark = '  <== T*' if t == best_t[0] else ''
            print('  tp %.2f | mean %+.3f  median %+.3f  win %2.0f%%  tp-hit %2.0f%%%s' % (
                t, m, np.median(pnl), 100 * np.mean(pnl > 0), 100 * np.mean((~stopped) & (mfe >= t)), mark))
    Tstar = best_t[0]

    # FINAL bracket strategy
    pnl = np.where(stopped, -Sstar, np.where(mfe >= Tstar, Tstar, 0.0))
    m, md, w, sd = stat(pnl)
    print('\n=== BRACKET STRATEGY  stop %.2f / TP %.2f ===' % (Sstar, Tstar))
    print('  per-trade: MEAN %+.3f%%  (median %+.3f)  win %.0f%%  std %.2f  | %d trades / 21d = %.1f/day' % (
        m, md, w, sd, N, N / 21))
    print('  stopped %.0f%% (-%.2f each) | TP-hit %.0f%% (+%.2f) | flat %.0f%%' % (
        100 * np.mean(stopped), Sstar, 100 * np.mean((~stopped) & (mfe >= Tstar)), Tstar,
        100 * np.mean((~stopped) & (mfe < Tstar))))
    print('  reward:risk = %.2f  | ⚠ NO costs — subtract ~fee+funding+slippage/round-trip for realized' % (Tstar / Sstar))
