"""insert_risk_config.py — create + seed risk_config (Joe 0708). Key-value like lp_config, one row per knob,
with a note for legibility. Values are the MEDIUM baseline: cap is DATA-DERIVED (p99 of the v2_walk_ad stack
distribution, risk_stack_dist.py); the rest are the agreed medium combo. All are DB knobs — tune with UPDATE,
no code. Consumer = RiskGovernor (docs/dynamic_risk_spec.md), built next. Idempotent. Run: python3 insert_risk_config.py"""
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

ROWS = [
    # name,                 val,       note
    ("base_appetite",      "1.0",   "master risk scalar (× leverage_factor) — the single 'dial up as we learn' knob; 1.0 = medium"),
    ("base_leverage",      "5.0",   "per-order base leverage (the validated dynamic5x) — unchanged"),
    ("max_exposure_mult",  "16.0",  "GROSS exposure cap × equity; p99 of one-way v2_walk_ad stack (clips 16-30x runaway). RE-DERIVE post-hedge"),
    # dynamic leverage — drawdown steps (reference = high-water peak, realized + open-leg MtM)
    ("dd_ref",             "hwm_mtm", "drawdown reference: high-water mark, realized + open-leg mark-to-market (reacts before the stop)"),
    ("dd_step1_pct",       "5.0",   "drawdown >5% → leverage ×0.5"),
    ("dd_step1_factor",    "0.5",   "leverage factor at dd_step1"),
    ("dd_step2_pct",       "10.0",  "drawdown >10% → leverage ×0.25"),
    ("dd_step2_factor",    "0.25",  "leverage factor at dd_step2"),
    ("dd_halt_pct",        "15.0",  "drawdown >15% → leverage ×0 + veto adds (bank floor)"),
    # dynamic leverage — vol (reuse s30 BB-band width, normalized vs its own trailing window)
    ("vol_source",         "s30_bbw", "volatility input: s30 BB-band width (already computed; coarse = steady)"),
    ("vol_window",         "500",   "bars to normalize band width against (percentile ranking)"),
    ("vol_hi_pctile",      "80",    "band-width percentile that counts as 'high vol'"),
    ("vol_hi_factor",      "0.5",   "leverage ×0.5 when vol ≥ vol_hi_pctile"),
    # pyramid gate/taper
    ("add_mode",           "taper", "adds inherit leverage_factor (soft taper); hard-veto only at max_exposure_mult or dd_halt"),
]


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute("""CREATE TABLE IF NOT EXISTS risk_config (
                    name VARCHAR(64) PRIMARY KEY,
                    val  VARCHAR(32) NOT NULL,
                    note VARCHAR(255) DEFAULT '')""")
    db.executemany("REPLACE INTO risk_config (name, val, note) VALUES (%s,%s,%s)", ROWS)
    print("=== risk_config (%d knobs) ===" % len(ROWS))
    for r in db.execute("SELECT name, val, note FROM risk_config ORDER BY name", fetch=True):
        print("  %-18s = %-8s  %s" % (r["name"], r["val"], r["note"]))
    db.disconnect()


if __name__ == "__main__":
    main()
