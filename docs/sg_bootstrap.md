# o9-sg-01 bootstrap — twin runbook

Bring the vanilla SG box to parity with WSL + connect to the Akamai Managed MySQL. Run top-to-bottom; verify each
step. **Branch: clone `live`** (the promoted/validated set), not `main`. See docs/o9-live/o9live_changelog.md for what's live.

> **Status 2026-07-09: §1–§7 COMPLETE on sg-app-01.** o9_infra = 15 tables + 1 view, 1,240,908 klines /
> 2,428,123 ticks (71.8 days, to 2026-07-09 02:02Z). o9_live = 9 tables. §7 returns `gate_mode curl seam_gate 105000`.
> §8 (services) not yet started. Every command below was actually run; the corrections are not theoretical.

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
> **Run these ON THE SG BOX** (`ssh` in first). Every step below is SG-side unless it says otherwise —
> running them on WSL (`sifu01`) silently "succeeds" because WSL already has mysql/pip.
```
# hostname: left as-is (sg-app-01) by decision — the runbook name o9-sg-01 is aspirational only
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
sudo apt install -y python3-venv mysql-client     # stock Ubuntu 24.04 has NEITHER; no pip, no ensurepip
python3 --version && git --version
```

## 2. Code (clone the live branch)
```
git clone git@github.com:joexblair/optimus9.git ~/thecodes    # gh SSH already authed
cd ~/thecodes && git checkout live && git log --oneline -1
```

## 3. Python deps  (venv — Ubuntu 24.04 is PEP-668 externally-managed, `pip install --user` is REFUSED)
```
cd ~/thecodes && python3 -m venv .venv          # needs python3-venv from §1, else pip is not bootstrapped
.venv/bin/pip install -U pip
.venv/bin/pip install numpy pandas mysql-connector-python fastapi "uvicorn[standard]" requests websockets python-multipart
# httpx only needed to run the test suite
```
From here on `.venv/bin/python` is the interpreter. Bare `python3` has NONE of these deps.
`.venv/` is gitignored. Always run from `~/thecodes` (repo root must be cwd — `logger` is a top-level import).

## 4. DB config file  (get_db_config reads ./optimus9_config.json)
**The keys MUST be nested under `"db"`.** `get_db_config()` does `cfg.get('db', {})` (optimus9/config.py) — a
flat file parses fine, yields no keys, and every field falls back to its default (`localhost`/`root`/`pk_optimizer`).
You get a confusing "can't connect to localhost", not a config error.
```
cat > ~/thecodes/optimus9_config.json <<'JSON'
{ "db": { "host": "a493943-akamai-prod-5255352-default.g2a.akamaidb.net",
          "port": <AKAMAI_PORT>, "user": "<USER>", "password": "<PASS>",
          "database": "o9_infra" } }
JSON
.venv/bin/python -c "from optimus9.config import get_db_config; from optimus9 import DatabaseManager; d=DatabaseManager(**get_db_config()); d.connect(); print('DB ok'); d.disconnect()"
```
`optimus9_config.json` is now gitignored (it used to be TRACKED — see Notes). The committed placeholder lives at
`optimus9_config.example.json`. Env vars `PK_DB_HOST/PORT/USER/PASS/NAME` override the file.

**`<AKAMAI_PORT>` is NOT 3306.** The example template carries `3306`; copying it through leaves you with a config
that looks right and hangs. Verified from the SG box: TCP 3306 *times out* (filtered, not refused) on both the A
record (104.64.209.137) and the AAAA (2600:3c15::2000:c3ff:fe85:e6c8). Get the real port from the Akamai console.
Two independent causes produce the identical hang, so check both:
  1. wrong port (the managed-MySQL listener is on a high port, not 3306);
  2. source-IP allowlist — this box egresses from **172.236.152.81** (v4) / **2600:3c15::2000:abff:fe39:351** (v6).
     Both need adding to the Akamai DB's allowed-IP list. WSL's IP is already on it; the SG box's is not.
`d.connect()` hangs rather than erroring, and `DatabaseManager` has no connect_timeout — so a misconfig here looks
like a freeze, not a failure. Probe the port with `timeout 6 bash -c 'cat </dev/null >/dev/tcp/<host>/<port>'` first.

**TLS:** `DatabaseManager.__init__` takes only host/user/password/database/port — there is no `ssl_ca`/`ssl_disabled`
passthrough. mysql-connector negotiates TLS automatically (no cert verification), which Akamai accepts. If Akamai ever
demands a *verified* CA, that is a code change to `DatabaseManager`, not a config edit.

## 5. Create the two databases (on Akamai)
```
mysql -h $H -P $P -u $U -p -e "CREATE DATABASE IF NOT EXISTS o9_infra; CREATE DATABASE IF NOT EXISTS o9_live;"
```

## 6. Seed data  (dumps produced on WSL, rsync'd to ~/seed/ — see Appendix)
§5+§6 are scripted end-to-end in **`~/seed/load.sh`** (not versioned; regenerate from this section). It reads creds
from optimus9_config.json without echoing them and prints verification counts. Steps, if doing it by hand:

**The raw `config.sql` will NOT load.** mysqldump stamps `DEFINER=\`root\`@...` on the 4 `bl_lines` triggers and on
`vw_indicator_configs_live`. Akamai's `akmadmin` has neither `SUPER` nor `SET_USER_ID`, so creating an object owned
by another user fails: `ERROR 1227 (42000): Access denied; you need SUPER or SET_USER_ID`. Strip the DEFINERs first
(the view must also drop to `SQL SECURITY INVOKER`, since a DEFINER view needs a definer that exists):
```
sed -e 's|/\*!50017 DEFINER=[^*]*\*/||g' \
    -e 's|/\*!50013 DEFINER=[^*]*SQL SECURITY DEFINER \*/|/*!50013 SQL SECURITY INVOKER */|g' \
    -e 's|DEFINER=`[^`]*`@`[^`]*` ||g' \
    ~/seed/config.sql > ~/seed/config.sanitized.sql
grep -c DEFINER ~/seed/config.sanitized.sql          # must be 0
```
```
# o9_infra <- config + tape (structure + data). config.sql = 13 tables + 4 triggers + vw_indicator_configs_live.
mysql -h $H -P $P -u $U -p o9_infra < ~/seed/config.sanitized.sql
zcat ~/seed/tape.sql.gz | mysql -h $H -P $P -u $U -p o9_infra   # ~339MB uncompressed: kline_collection + ticks
```
`docs/o9_live_schema.sql` holds **22** CREATEs = 13 config tables (which belong in `o9_infra`, NOT here) + the 9
below. Extract exactly those 9 — no foreign keys, so order is irrelevant:
```
.venv/bin/python - <<'PY' > /tmp/o9_live_tables.sql
import re
src = open('docs/o9_live_schema.sql').read()
LIVE = ['fx_order','fx_fill','fx_position','o9_ledger','o9_account',
        'o9_decision','o9_control','o9_health','o9_trade_archive']
for t in LIVE:
    m = re.search(r"CREATE TABLE (?:IF NOT EXISTS )?`?%s`?\s*\(.*?\n\)[^;]*;" % t, src, re.S|re.I)
    assert m, "NOT FOUND: " + t
    # IF NOT EXISTS, never DROP: a re-run must not destroy o9_ledger / fx_position / o9_trade_archive.
    print(re.sub(r"^CREATE TABLE (?:IF NOT EXISTS )?", "CREATE TABLE IF NOT EXISTS ",
                 m.group(0), count=1, flags=re.I), "\n")
PY
mysql -h $H -P $P -u $U -p o9_live < ~/seed/o9_live_tables.sql
.venv/bin/python migrate_hedge_mode.py o9_live    # idempotent; a NO-OP (schema already ships position_idx)
```
**`o9_forecast`, `o9_state_log`, `o9_state_log_line` are NOT created here** — they self-create at first use via
`CREATE TABLE IF NOT EXISTS` (ops/o9_forecast.py, optimus9/live/state_log.py). `o9_health` IS in the schema file
and is created above. (The old §6 listed the three self-creating tables and omitted `o9_health` — both wrong.)

**Do NOT run `ops/provision_o9live.py` on SG.** It is the WSL single-DB path: it seeds the config/reference tables
*into* `o9_live`, which contradicts §2's topology. The code reads config from the DEFAULT db (`o9_infra`), so those
copies would be silently ignored — until someone edited the wrong one.

Expected after §6: `o9_infra` = 15 base tables + 1 view; `o9_live` = 9 tables.

## 7. Verify config loaded (curl exit + risk knobs came across)
```
.venv/bin/python -c "from optimus9.config import get_db_config; from optimus9 import DatabaseManager; from optimus9.analysis.lr import lr_config; d=DatabaseManager(**get_db_config()); d.connect(); lr=lr_config(d); print('gate_mode', lr.gate_mode, 'seam_gate', lr.seam_gate); assert lr.gate_mode=='curl'; print('config OK')"
```
`gate_mode` is derived, not stored: it reads `lp_config.lp_lr_gate_mode` (1=curl, 0/absent=breach). The seed
carries `lp_lr_gate_mode=1`, so this passes. If the row were missing the assert would fail with no clue why —
`k.get(...)` defaults it to breach. Expect `gate_mode curl seam_gate 105000`.

## 8. Services (phase 2 — only after §7 passes)
All four MUST use `.venv/bin/python`, from cwd `~/thecodes`. Bare `python3` will `ModuleNotFoundError`.
```
cd ~/thecodes
# collector (fills o9_infra.kline_collection + ticks from Bybit, near-zero latency here).
# NOT `python -m optimus9.data.tick_collector` — that module has no __main__; it imports and exits silently.
# run.py supervisor runs TickCollector + BarBuilder together under ProcessManager.
nohup setsid .venv/bin/python run.py supervisor --tp_pk 1 --symbol FARTCOINUSDT >> collector.log 2>&1 & disown
#   --lookback_days is INERT: synthetic backfill was sunset (Joe 2026-07-05, run.py:438 commented out) because
#   1m->5s splitting manufactured phantom flat bars that drift oscillators into false reversals. Gaps are now
#   absorbed by optimus9_system.filler_invisible=1 (verified present in the seed) + TV-CSV -> KlineSanitiser.
#   NEVER run `run.py backfill_synthetic` against this tape — it reintroduces exactly those phantom bars.
#   The seed tape ends at the dump time; the collector fills forward from first tick.
# fakeAPI
PK_DB_NAME=o9_live O9_LIVE_BOOK=FARTCOINUSDT nohup setsid .venv/bin/python -m uvicorn services.fakeapi.app:app --host 127.0.0.1 --port 8098 >> fakeapi.log 2>&1 & disown
# loop
O9_DELAY_MS=2000 O9_PRODUCER=ad nohup setsid .venv/bin/python -u ops/run_o9live.py >> o9live.log 2>&1 & disown
# UI  (0.0.0.0 — firewall port 8099, it is internet-facing on a public Linode)
nohup setsid .venv/bin/python -m uvicorn optimus9.live.ui_server:app --host 0.0.0.0 --port 8099 >> ui_server.log 2>&1 & disown
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
- **`optimus9_config.json` was TRACKED in git** on `main`/`live`/`origin` (commit e915885) despite config.py's
  comment and this doc both assuming otherwise. It only ever held placeholders — no secret leaked. Now fixed:
  untracked + gitignored, placeholder preserved as `optimus9_config.example.json`.
  **On WSL that file is locally modified with REAL creds**: back it up (`cp optimus9_config.json ~/o9_creds.bak`)
  before pulling the untracking commit, and never `git add -A` there until the fix lands.
- Deploy a new version later: on WSL `git checkout live && git merge main && git tag live-<date> && git push --tags`; on SG `git pull`. Rollback: `git checkout <prev-tag>`.
- The SG box will run its OWN collector → its OWN clean tape going forward; the seed tape just warms it up.
