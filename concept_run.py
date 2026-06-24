"""
concept_run.py — confluence dataset CONCEPT RUN (docs/confluence_dataset_design.md).
11 itf=30s lines · one window (0611→0618) · s3m bias stream · OOB = global optimus9_system 85/15.
3-stage SRP pipeline → 6 tables (cf_*). Proves the cross/rating/x-sweep logic + storage shape.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import numpy as np
from itertools import combinations
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
def ms(dt): return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)
R1 = ms(dtm.datetime(2026, 6, 18, 0, 0)); R0 = R1 - 168 * bm.H
STEP = 30000   # 30s bars

db = DatabaseManager(**get_db_config()); db.connect()
sysrow = db.execute('SELECT hi_boundary, lo_boundary FROM optimus9_system', fetch=True)[0]
HI, LO = float(sysrow['hi_boundary']), float(sysrow['lo_boundary'])
lines = [(r['ic_pk'], r['ind_name']) for r in db.execute(
    "SELECT ic_pk, ind_name FROM pk_optimizer.vw_indicator_configs_live WHERE itf_seconds=30 ORDER BY ic_pk", fetch=True)]
icp = {p: nm for p, nm in lines}
print(f"lines={len(lines)} (itf=30) · OOB {HI}/{LO} · window {R0}→{R1}")

# ── DDL (re-runnable) ──
for t in ('cf_cross_line', 'cf_cross', 'cf_pair_cross', 'cf_bias_walk', 'cf_group_member', 'cf_group'):
    db.execute(f'DROP TABLE IF EXISTS {t}')
db.execute("""CREATE TABLE cf_group (group_pk INT PRIMARY KEY, sz TINYINT,
              members VARCHAR(80) COLLATE utf8mb4_bin UNIQUE)""")   # bin = case-sensitive (M != m)
db.execute("""CREATE TABLE cf_group_member (group_pk INT, ic_pk INT, INDEX(ic_pk), INDEX(group_pk))""")
db.execute("""CREATE TABLE cf_pair_cross (pair_cross_pk INT PRIMARY KEY, ic_a INT, ic_b INT, cross_ms BIGINT,
              breach CHAR(2), val_a FLOAT, val_b FLOAT, INDEX(ic_a, ic_b), INDEX(cross_ms))""")
db.execute("""CREATE TABLE cf_cross (cross_pk INT PRIMARY KEY, group_pk INT, pair_cross_pk INT, cross_ms BIGINT,
              breach CHAR(2), rating FLOAT, n_aligned TINYINT, n_total TINYINT,
              INDEX(group_pk, cross_ms), INDEX(cross_ms))""")
db.execute("""CREATE TABLE cf_cross_line (cross_pk INT, ic_pk INT, val FLOAT, INDEX(cross_pk))""")
db.execute("""CREATE TABLE cf_bias_walk (walk_pk INT PRIMARY KEY, bias_ms BIGINT, bias_dir TINYINT, bias_mae FLOAT,
              group_pk INT, x TINYINT, n_crosses INT, mean_rating FLOAT, best_rating FLOAT, nearest_bars INT,
              INDEX(group_pk, x), INDEX(bias_ms))""")

# ── line values on the 30s grid (via bias engine, forward-filled, sampled at 30s boundaries) ──
cfg = bm.BiasConfig(osc='s3m', trigger_tf=6, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                    mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
Wd = bm.BiasWindow(db, R1, cfg=cfg); ts = Wd.ts
idx30 = np.where(ts % STEP == 0)[0]; ts30 = ts[idx30]
vals = {}
for p, nm in lines:
    vals[p] = Wd._line(nm)[idx30]
rng = {nm: (round(float(np.nanmin(vals[p])), 1), round(float(np.nanmax(vals[p])), 1)) for p, nm in lines}
print(f"line value ranges (osc sanity): {rng}")
inwin = (ts30 >= R0) & (ts30 < R1)

# ── stage 1: groups ──
groups = list(combinations(lines, 3)) + list(combinations(lines, 4))
g_rows, gm_rows, pair_groups = [], [], {}
for gp, g in enumerate(groups):
    pks = [p for p, _ in g]; nms = '+'.join(sorted(icp[p] for p in pks))
    g_rows.append((gp, len(g), nms))
    for p in pks: gm_rows.append((gp, p))
    for a, b in combinations(sorted(pks), 2): pair_groups.setdefault((a, b), []).append(gp)
db.executemany("INSERT INTO cf_group VALUES (%s,%s,%s)", g_rows)
db.executemany("INSERT INTO cf_group_member VALUES (%s,%s)", gm_rows)
print(f"stage1: {len(g_rows)} groups, {len(gm_rows)} memberships")

# ── stage 2: pair-cross pre-walk + fan to groups + rating ──
pc_rows = []; pc_meta = []   # meta: (pc_pk, idx30_pos)
for a, b in combinations([p for p, _ in lines], 2):
    va, vb = vals[a], vals[b]; d = np.sign(va - vb)
    flips = np.where((d[1:] != d[:-1]) & (d[1:] != 0))[0] + 1
    for i in flips:
        if not inwin[i]: continue
        if va[i] > HI and vb[i] > HI: br = 'hi'
        elif va[i] < LO and vb[i] < LO: br = 'lo'
        else: continue
        pk = len(pc_rows)
        pc_rows.append((pk, a, b, int(ts30[i]), br, float(va[i]), float(vb[i]))); pc_meta.append((pk, a, b, br, int(i)))
db.executemany("INSERT INTO cf_pair_cross VALUES (%s,%s,%s,%s,%s,%s,%s)", pc_rows)
print(f"stage2a: {len(pc_rows)} pair-crosses")

cx_rows, cxl_rows, cross_mem = [], [], []   # cross_mem: (group_pk, cross_ms, rating) for stage3
cxpk = 0
gmem = {}
for gp, p in gm_rows: gmem.setdefault(gp, []).append(p)
for pc_pk, a, b, br, i in pc_meta:
    t = int(ts30[i])
    for gp in pair_groups[(a, b)]:
        mem = gmem[gp]
        al = sum(1 for p in mem if (vals[p][i] > 50 if br == 'hi' else vals[p][i] < 50))
        rt = al / len(mem)
        cx_rows.append((cxpk, gp, pc_pk, t, br, rt, al, len(mem)))
        for p in mem: cxl_rows.append((cxpk, p, float(vals[p][i])))
        cross_mem.append((gp, t, rt)); cxpk += 1
db.executemany("INSERT INTO cf_cross VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", cx_rows)
db.executemany("INSERT INTO cf_cross_line VALUES (%s,%s,%s)", cxl_rows)
print(f"stage2b: {len(cx_rows)} group-crosses, {len(cxl_rows)} cross-line values")

# ── stage 3: bias-walk (s3m, loose-stop MAE, x sweep 0..4) ──
pls = {int(p['pk_t']): float(p['mae']) for p in Wd.placements(Wd.signals(), 2.0, 0.9, s3_lookback=2) if R0 <= p['pk_t'] < R1}
cm = sorted(cross_mem, key=lambda c: c[1]); cm_t = np.array([c[1] for c in cm]); cm_gp = np.array([c[0] for c in cm]); cm_rt = np.array([c[2] for c in cm])
bw_rows, wpk = [], 0
for u in Wd.signals():
    if u['call'] not in ('BULL', 'BEAR') or int(u['t']) not in pls: continue
    bms = int(u['t']); mae = pls[bms]; bd = 1 if u['call'] == 'BULL' else -1
    for x in range(5):
        w = x * STEP; lo_i, hi_i = np.searchsorted(cm_t, bms - w), np.searchsorted(cm_t, bms + w, 'right')
        if hi_i <= lo_i: continue
        sl_gp, sl_rt, sl_t = cm_gp[lo_i:hi_i], cm_rt[lo_i:hi_i], cm_t[lo_i:hi_i]
        for gp in np.unique(sl_gp):
            m = sl_gp == gp; nb = int(np.min(np.abs(sl_t[m] - bms)) // STEP)
            bw_rows.append((wpk, bms, bd, mae, int(gp), x, int(m.sum()), float(sl_rt[m].mean()), float(sl_rt[m].max()), nb)); wpk += 1
db.executemany("INSERT INTO cf_bias_walk VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", bw_rows)
print(f"stage3: {len(bw_rows)} bias-walk rows ({len(pls)} bias updates w/ a trade)")

# ── DoD: metric computable — rank groups by swing-proximity (avg bias_mae of crosses within x=2) ──
print("\nDoD — top swing-proximity groups (lowest avg |MAE| of bias updates with a cross within x=2, n>=4):")
q = db.execute("""SELECT bw.group_pk, g.members, COUNT(*) n, ROUND(AVG(ABS(bw.bias_mae)),2) avg_mae
                  FROM cf_bias_walk bw JOIN cf_group g ON g.group_pk=bw.group_pk
                  WHERE bw.x=2 GROUP BY bw.group_pk HAVING n>=4 ORDER BY avg_mae ASC LIMIT 5""", fetch=True)
for r in q: print(f"  {r['members']:34s} avg|MAE| {r['avg_mae']}  (n={r['n']})")
db.disconnect()
print("✓ concept run complete")
