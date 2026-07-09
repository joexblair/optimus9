"""stop_classify.py — classify each o9-live LOSS by its excursion SHAPE (Joe 0708), the spine of the stop tool.
For each losing trade, walk the tape entry->exit and find WHEN the favourable peak (MFE) happened vs when the
adverse worst (MAE) happened. Shape decides the fix:
  banked-then-bled : peaked favourable EARLY then gave it back  -> a take-profit is the lever
  bad-entry        : never meaningfully green                    -> an entry filter / fast stop is the lever
  late/mixed       : neither clean                               -> needs the reversal exit or a trailing stop
Also: would a 0.5% TP have saved it? Read-only. Run:  python3 stop_classify.py [hours]"""
import sys, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

HOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 12
TP = 0.5                                                            # candidate take-profit %


def main():
    o = get_db_config(); o['database'] = 'o9_live'; d = DatabaseManager(**o); d.connect()
    dev = DatabaseManager(**get_db_config()); dev.connect()
    tp = dev.execute("SELECT tp_pk FROM trading_pairs WHERE tp_symbol_bybit=%s", ('FARTCOINUSDT',), fetch=True)[0]['tp_pk']
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
    rows = d.execute("""SELECT led_id,side,entry_px,net,opened_ms,closed_ms FROM o9_ledger
        WHERE status='closed' AND net<0 AND closed_ms>=%s ORDER BY opened_ms""", (now - HOURS * 3600000,), fetch=True)
    print("led  side hold  MFE%%  t_mfe  MAE%%  t_mae   class            TP0.5 saves?")
    tally = {'banked-then-bled': 0, 'bad-entry': 0, 'late/mixed': 0}; tp_saves = 0
    for r in rows:
        e = float(r['entry_px']); o0 = int(r['opened_ms']); c0 = int(r['closed_ms']); dch = 1.0 if r['side'] == 'Buy' else -1.0
        kk = dev.execute("SELECT kc_timestamp t,kc_high h,kc_low l FROM kline_collection WHERE kc_tp_pk=%s AND kc_timestamp BETWEEN %s AND %s ORDER BY kc_timestamp",
                         (tp, o0 // 5000 * 5000, c0), fetch=True)
        if not kk:
            continue
        t = np.array([int(x['t']) for x in kk]); hi = np.array([float(x['h']) for x in kk]); lo = np.array([float(x['l']) for x in kk])
        fav = (hi - e) / e * 100 * dch if dch > 0 else (e - lo) / e * 100     # favourable excursion per bar
        adv = (lo - e) / e * 100 * dch if dch > 0 else (e - hi) / e * 100     # adverse excursion per bar
        i_mfe = int(np.argmax(fav)); i_mae = int(np.argmin(adv))
        mfe, mae = float(fav[i_mfe]), float(adv[i_mae])
        hold = (c0 - o0) / 60000.0; t_mfe = (t[i_mfe] - o0) / 60000.0; t_mae = (t[i_mae] - o0) / 60000.0
        if mfe < 0.20:
            cls = 'bad-entry'
        elif t_mfe < 0.4 * hold and mfe >= 0.30:
            cls = 'banked-then-bled'
        else:
            cls = 'late/mixed'
        tally[cls] += 1
        saves = mfe >= TP and t_mfe < t_mae                          # peak reached TP before the worst adverse
        tp_saves += 1 if saves else 0
        print("%-4d %-4s %4.0fm %5.2f %5.0fm %6.2f %5.0fm  %-16s %s"
              % (r['led_id'], r['side'], hold, mfe, t_mfe, mae, t_mae, cls, 'YES' if saves else '-'))
    n = sum(tally.values())
    print("\n%d losses: banked-then-bled=%d  bad-entry=%d  late/mixed=%d   | TP0.5%% would save %d"
          % (n, tally['banked-then-bled'], tally['bad-entry'], tally['late/mixed'], tp_saves))
    d.disconnect(); dev.disconnect()


if __name__ == "__main__":
    main()
