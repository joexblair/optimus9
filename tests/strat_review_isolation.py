"""strat_review module-isolation scan (Joe 0627) — toggle each module alone, confirm its events belong
ONLY to it (no cross-contamination). Post-build verification; run after changing the module wiring."""
import sys; sys.path.insert(0,'/home/joe/thecodes')
import datetime as dtm; from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from strat_review import build_strat_review

MODULE_EVENTS = {            # bias_producer.bp_name -> its ALLOWED event types (context = run-up padding)
    'bl_state':  {'state', 'exit_raw', 'context'},   # the bl lifecycle module
    'trades':    {'gate_open', 'context'},
    'cascade':   {'pl_cas_start', 'pl_cas_end', 'TRADE'},
    'pk':        {'pk_bias'},
    'bro_cross': {'bro_x_bias'},
}

def run():
    db = DatabaseManager(**get_db_config()); db.connect()
    END = int(dtm.datetime(2026, 6, 22, tzinfo=timezone.utc).timestamp() * 1000)
    saved = {r['bp_name']: r['bp_active'] for r in db.execute('SELECT bp_name,bp_active FROM bias_producer', fetch=True)}
    def events():
        return {r['event'] for r in db.execute("SELECT DISTINCT event FROM strat_review", fetch=True)}
    ok = True
    for mod, allowed in MODULE_EVENTS.items():
        db.execute('UPDATE bias_producer SET bp_active=0'); db.execute('UPDATE bias_producer SET bp_active=1 WHERE bp_name=%s', (mod,))
        build_strat_review(db, END)
        ev = events(); leak = ev - allowed
        ok &= not leak
        print(f"  {mod:10s} alone -> events {sorted(ev) or '[]'}  {'LEAK ' + str(leak) if leak else 'isolated ✓'}")
    # cascade needs bias to fire — confirm it emits ONLY pl_cas alongside a bias producer (bro)
    db.execute('UPDATE bias_producer SET bp_active=0'); db.execute("UPDATE bias_producer SET bp_active=1 WHERE bp_name IN ('cascade','bro_cross')")
    build_strat_review(db, END); ev = events(); allowed = MODULE_EVENTS['cascade'] | MODULE_EVENTS['bro_cross']
    leak = ev - allowed; ok &= not leak
    print(f"  cascade+bro    -> events {sorted(ev)}  {'LEAK ' + str(leak) if leak else 'isolated ✓'}")
    for k, v in saved.items(): db.execute('UPDATE bias_producer SET bp_active=%s WHERE bp_name=%s', (v, k))
    print('RESTORED bp:', {r['bp_name']: r['bp_active'] for r in db.execute('SELECT bp_name,bp_active FROM bias_producer', fetch=True)})
    print('ALL MODULES ISOLATED?:', ok)
    db.disconnect()

if __name__ == '__main__':
    run()
