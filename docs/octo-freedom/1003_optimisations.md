# 1003 — optimisation hunt, found while adding `mlc_tf_list`

Joe: *"while you work, hunt for optimisations and provide ideas if you find anything"*. Each item
below is measured, not guessed. Nothing here is applied except item 1, which he asked for.

## 1 — DONE: the registry duplication, quantified

| | |
|---|---|
| named lines in `vw_indicator_configs_live` | **175** |
| distinct specs behind them | **62** — 20 shared by >=2 lines, 42 used once |
| the worst offender | `bb 38/0.93 close` — **the Mage role, written out 14 times** across 15..1320 s |
| next | `k 6/6/5 close` 11 times, `bb 37/0.72 ohlc4` 6 times |
| banded rows doing the same job today | **7**, for the whole system |
| `wsf` v2, after this change | **5 rows express 75 lines** |

- 131 of the 175 named lines are NOT expressible by any current band. Of those, **30 are wsf role
  specs sitting outside the band** (gcws15/30 below it, ws9/10/15/22 above) and **0 had a different
  spec** — so they migrate with no new mech name. The rest need names, which is Joe's (below).

## 2 — IDEA, MEASURED: `mmap_mode='r'` on the line cache

`np.load` without `mmap_mode` parses and COPIES each 13 MB line file into RSS. The arrays are
read-only in every consumer.

| 40 files, 513 MB, page cache warm | time | RSS |
|---|---|---|
| `np.load(f)` | **0.315 s** | **513 MB** |
| `np.load(f, mmap_mode='r')` | **0.005 s** | 0 MB, paged on demand |
| | **68x** | |

**Verified byte-for-byte, and my first check was wrong.** `np.array_equal` returned False, which I
nearly reported as a difference; it is `NaN != NaN` over the 12,240 warmup NaNs. With
`equal_nan=True`: True. NaN masks identical, finite values identical, **`tobytes()` identical**.

- where it pays: `Rig.__init__` loads 92 of these per build, and a sweep process pays 70-81 s before
  the first variant. `report_coil_exit._cached` and `rpl_cache.cache_jig_perline`'s load path are the
  two call sites.
- the caveat: an mmap'd array is read-only, so any consumer that writes in place would raise. That is
  a feature here - the lines should never be mutated - but it has to be checked per consumer before
  the flag goes in.

## 3 — IDEA: the line cache cannot be garbage-collected

| | |
|---|---|
| files / size | **1,543 files, 19.56 GB** |
| distinct file sizes | 4 — one per tape span |
| tape generations live right now | at least 3 (09-08, 09-30, 10-02), ~108 of 120 probed ws lines each |
| growth per tape move | **~1.2 GB**, and nothing ever deletes |

`build_wsf_role_lines.py` states the policy: *"the old files keep their own names and are not
touched. Nothing here deletes."* The problem is not the policy, it is that **the filename is a hash of
`(END_MS, HOURS, WARMUP, spec)`**, so which generation a file belongs to is not recoverable from the
name. Dead generations cannot be found, let alone pruned.

**Idea:** write a sidecar index at build time - one small JSON per build, `key -> {end_ms, hours,
warmup, name, spec}`. Then a prune tool can list generations and drop the dead ones. It is the
difference between 19.56 GB you can manage and 19.56 GB you cannot.

**NOT an opportunity, so nobody chases it:** the cache key is spec-based, so two NAMED lines sharing
a `(tf, spec)` already share ONE file. The de-duplication is already there.

## 4 — IDEA: `mech_line_config` has no owning module

The house pattern is a module that owns its DDL and seeds idempotently - `trade_config.py` carries
`DDL`, `SEED`, `seed()` and `key()`. `mech_line_config` has no such owner: `line_config.py` READS it
(`from_mech_row`, `mech_lines`) but never creates or seeds it. That is why this change needed a
one-off migration script instead of an idempotent `seed()` call, and it is the same
*"numbers that live outside the repo"* trap in a different coat.

**Idea:** give `line_config.py` a `DDL` + `seed(db, version)` the way `trade_config.py` has one. Then
a clean DB reproduces the mech line config, and a version bump is one function call.

## 5 — JOE'S CALL: 101 lines across 16 families still need mech names

The migration covered the wsf family. The remainder cannot move without a `mlc_mech` value per
family, and naming a mechanic is Joe's.

| prefix | lines | distinct specs | timeframes (s) |
|---|---|---|---|
| `s` | 42 | 23 | 15, 30, 60, 120, 180, 240, 300, 360, 420, 480, 720, 1320 |
| `hb` | 11 | 7 | 540, 900, 960 |
| `b` | 7 | 5 | 30, 360 |
| `blp` | 6 | 6 | 360, 420 |
| `gcs` | 6 | 6 | 5, 15 |
| `hs` | 6 | 4 | 540, 900 |
| `hbhi` / `hbhl` / `hblo` | 4 each | 2 each | 960, 1980 |
| `st` | 3 | 3 | 600 |
| `xm` | 3 | 3 | 45 |
| `bny` / `gca` / `gcb` / `mnm` | 2 each | 2 each | 30 / 5 / 5 / 240 |
| `mo` | 1 | 1 | 720 |

- `s` is the big one: 42 lines, 23 specs. It is the bias-machine family (`s30r`, `s5M` and friends),
  and 23 distinct specs over 12 timeframes means the band would not collapse it much anyway - the
  duplication there is in the SPECS, not the timeframes.
