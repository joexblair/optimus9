# o9-sg-01 bootstrap — twin runbook

Bring the vanilla SG box to parity with WSL + connect to the Akamai Managed MySQL. Run top-to-bottom; verify each
step. **Branch: clone `live`** (the promoted/validated set), not `main`. See docs/o9-live/o9live_changelog.md for what's live.

## Topology (decided)
- **Akamai MySQL** host `a493943-akamai-prod-5255352-default.g2a.akamaidb.net` (port + creds: Joe supplies on box).
- **`o9_infra`** = the DEFAULT db = **tape (kline_collection, ticks) + all config** (indicator_*, lp_config, lr_gate*,
  optimus9_system, trading_pairs, risk_config, cascade_state, the `vw_indicator_configs_live` view). This plays
  `pk_optimizer`'s role on SG. `pk_optimizer` itself stays WSL-only.
- **`o9_live`** = exchange + o9-live tables ONLY (fx_*, o9_ledger, o9_account, o9_decision, o9_forecast, o9_control,
  o9_state_log(+_line), o9_trade_archive).
- The code reads the tape+config from the default db and the exchange via `c['database']='o9_live'` — so config MUST
  live in `o9_infra` with the tape (not in `o9_live`).

## 1. System prep
```
sudo hostnamectl set-hostname o9-sg-01
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
python3 --version && pip3 --version && git --version   # Linode default has python3; install if missing
```

## 2. Code (clone the live branch)
```
git clone git@github.com:joexblair/optimus9.git ~/thecodes    # gh SSH already authed
cd ~/thecodes && git checkout live && git log --oneline -1
```

## 3. Python deps
```
pip3 install --user numpy pandas mysql-connector-python fastapi "uvicorn[standard]" requests websockets python-multipart
# httpx only needed to run the test suite
```

## 4. DB config file  (get_db_config reads ./optimus9_config.json)
```
cat > ~/thecodes/optimus9_config.json <<'JSON'
{ "host": "a493943-akamai-prod-5255352-default.g2a.akamaidb.net",
  "port": <AKAMAI_PORT>, "user": "<USER>", "password": "<PASS>", "database": "o9_infra" }
JSON
python3 -c "from optimus9.config import get_db_config; from optimus9 import DatabaseManager; d=DatabaseManager(**get_db_config()); d.connect(); print('DB ok'); d.disconnect()"
```

## 5. Create the two databases (on Akamai)
```
mysql -h $H -P $P -u $U -p -e "CREATE DATABASE IF NOT EXISTS o9_infra; CREATE DATABASE IF NOT EXISTS o9_live;"
```

## 6. Seed data  (dumps produced on WSL, rsync'd to ~/seed/ — see Appendix)
```
# o9_infra <- config + tape (structure + data)
mysql -h $H -P $P -u $U -p o9_infra < ~/seed/config.sql
zcat ~/seed/tape.sql.gz | mysql -h $H -P $P -u $U -p o9_infra
# o9_live <- exchange + o9-live tables (schema only; fresh paper account)
python3 - <<'PY'
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
c=get_db_config(); c['database']='o9_live'; d=DatabaseManager(**c); d.connect()
# create the o9-live/exchange tables. Source: docs/o9_live_schema.sql (fx_order/fx_fill/fx_position,
# o9_ledger, o9_account, o9_decision, o9_forecast, o9_control, o9_state_log, o9_state_log_line) + o9_trade_archive.
# Run each CREATE from that file that is NOT a config/reference table (those live in o9_infra).
PY
python3 migrate_hedge_mode.py o9_live        # ensure fx_position.position_idx
```

## 7. Verify config loaded (curl exit + risk knobs came across)
```
python3 -c "from optimus9.config import get_db_config; from optimus9 import DatabaseManager; from optimus9.analysis.lr import lr_config; d=DatabaseManager(**get_db_config()); d.connect(); lr=lr_config(d); print('gate_mode', lr.gate_mode, 'seam_gate', lr.seam_gate); assert lr.gate_mode=='curl'; print('config OK')"
```

## 8. Services (phase 2 — only after §7 passes)
```
# collector (fills o9_infra.kline_collection + ticks from Bybit, near-zero latency here)
python3 -m optimus9.data.tick_collector   # (wire per its run(tp_pk, symbol); or the run supervisor)
# fakeAPI
PK_DB_NAME=o9_live O9_LIVE_BOOK=FARTCOINUSDT nohup setsid python3 -m uvicorn services.fakeapi.app:app --host 127.0.0.1 --port 8098 >> fakeapi.log 2>&1 & disown
# loop
O9_DELAY_MS=2000 O9_PRODUCER=ad nohup setsid python3 -u ops/run_o9live.py >> o9live.log 2>&1 & disown
# UI
nohup setsid python3 -m uvicorn optimus9.live.ui_server:app --host 0.0.0.0 --port 8099 >> ui_server.log 2>&1 & disown
```

## Appendix — producing the seed dumps (ON WSL, then rsync to SG)
```
# config (already produced): ~/thecodes/sg_seed/config.sql
# tape (big; gzip):
MYSQL_PWD=... mysqldump -h <wsl_host> -u <wsl_user> --no-tablespaces --skip-lock-tables pk_optimizer \
  kline_collection ticks | gzip > ~/thecodes/sg_seed/tape.sql.gz
# transfer:
rsync -avz ~/thecodes/sg_seed/config.sql ~/thecodes/sg_seed/tape.sql.gz joe@<sg-ip>:~/seed/
```

## Notes
- `<AKAMAI_PORT>/<USER>/<PASS>` and the WSL/SG hosts are Joe-supplied (never committed).
- Deploy a new version later: on WSL `git checkout live && git merge main && git tag live-<date> && git push --tags`; on SG `git pull`. Rollback: `git checkout <prev-tag>`.
- The SG box will run its OWN collector → its OWN clean tape going forward; the seed tape just warms it up.
