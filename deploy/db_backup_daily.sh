#!/usr/bin/env bash
#   HIS 1122 DAILY BACKUP. His words: *"cretae a cron job that runs this db backup every 24 hours.
#   dump them into a 'mysql_backup' folder under ./transfer/ , prefixed with yymmdd (eg
#   261122_pkoptimzer and 261122_o9live). keep a rolling 14 day backup regime"* and *"add o9-live
#   and fakeAPI to the backups"*, which he ruled as THEIR LOGS - neither service has its own
#   database, and the o9_live database is already dumped here.
#
#   WHAT EACH TABLE GETS. His 1122 rulings, in his own words:
#     *"for the kline and tick tables, backup only the structure"* - they ship as CREATE only,
#     *"include kline_collection's data in the backup"* - that one table is dumped with its rows.
#   The six bulk tables he truncated are dumped like any other: they are simply empty now.
#
#   NO TRUNCATE HERE. His truncate was a one-off for the 1122 transfer, not part of a daily job,
#   and a cron job that silently empties tables every night is not what he asked for.
#
#   IT LIVES IN deploy/ beside install_o9_units.sh - MY CALL, structural: there is no scripts/
#   directory, and this is an ops script of the same kind as the one already there.
set -euo pipefail

OUT=/home/joe/thecodes/transfer/mysql_backup
CNF=/home/joe/thecodes/.db_backup.cnf          # [client] host/port/user/password, mode 600
STAMP=$(date -u +%y%m%d)
KEEP_DAYS=14                                   # his *"rolling 14 day backup regime"*
LOG=$OUT/backup.log

#   the kline and tick tables that ship as STRUCTURE ONLY. kline_collection is NOT here: his 1122
#   *"include kline_collection's data in the backup"* takes it out of this set.
PK_NODATA="ticks kline_sanitise_log kline_audit kline_tv kline_tv30 synthetic_klines kline_audit_config"
LIVE_NODATA="ticks"

#   his *"add o9-live and fakeAPI to the backups"* - the logs, gzipped beside the dumps
LOGS="/home/joe/thecodes/fakeapi.log /home/joe/thecodes/o9live_octo.log /home/joe/thecodes/ws_liveness_fakeapi_book.log"

say() { printf '%s  %s\n' "$(date -u '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG"; }

mkdir -p "$OUT"
say "START $STAMP"

COMMON="--defaults-file=$CNF --single-transaction --quick --routines --events --triggers --set-gtid-purged=OFF --default-character-set=utf8mb4"

#   the main database: every table with data, except the structure-only set, then that set's CREATEs
IGN=""; for t in $PK_NODATA; do IGN="$IGN --ignore-table=pk_optimizer.$t"; done
{ mysqldump $COMMON --databases pk_optimizer $IGN
  mysqldump $COMMON --no-data pk_optimizer $PK_NODATA
} | gzip -6 > "$OUT/${STAMP}_pkoptimizer.sql.gz.part"
mv "$OUT/${STAMP}_pkoptimizer.sql.gz.part" "$OUT/${STAMP}_pkoptimizer.sql.gz"
say "pkoptimizer $(du -h "$OUT/${STAMP}_pkoptimizer.sql.gz" | cut -f1)"

#   the live database, the same way
LIGN=""; for t in $LIVE_NODATA; do LIGN="$LIGN --ignore-table=o9_live.$t"; done
{ mysqldump $COMMON --databases o9_live $LIGN
  mysqldump $COMMON --no-data o9_live $LIVE_NODATA
} | gzip -6 > "$OUT/${STAMP}_o9live.sql.gz.part"
mv "$OUT/${STAMP}_o9live.sql.gz.part" "$OUT/${STAMP}_o9live.sql.gz"
say "o9live $(du -h "$OUT/${STAMP}_o9live.sql.gz" | cut -f1)"

#   the live-test database
mysqldump $COMMON --databases o9_live_test | gzip -6 > "$OUT/${STAMP}_o9livetest.sql.gz.part"
mv "$OUT/${STAMP}_o9livetest.sql.gz.part" "$OUT/${STAMP}_o9livetest.sql.gz"
say "o9livetest $(du -h "$OUT/${STAMP}_o9livetest.sql.gz" | cut -f1)"

#   HIS o9-live and fakeAPI logs. A missing log is RECORDED, not fatal - a service may be stopped.
for f in $LOGS; do
    b=$(basename "$f" .log)
    if [ -f "$f" ]; then
        gzip -6 -c "$f" > "$OUT/${STAMP}_${b}.log.gz.part"
        mv "$OUT/${STAMP}_${b}.log.gz.part" "$OUT/${STAMP}_${b}.log.gz"
        say "$b $(du -h "$OUT/${STAMP}_${b}.log.gz" | cut -f1)"
    else
        say "$b MISSING - not backed up"
    fi
done

#   EVERY ARCHIVE IS TESTED. A corrupt dump that restores nothing is worse than no dump, so a bad
#   file is reported and REMOVED rather than left there to be trusted.
for f in "$OUT/${STAMP}"_*.gz; do
    if gzip -t "$f" 2>/dev/null; then say "OK $(basename "$f")"
    else say "CORRUPT $(basename "$f") - REMOVED"; rm -f "$f"; fi
done

#   his rolling 14 days, read off the FILE'S OWN DATE PREFIX rather than its mtime - a file copied
#   or touched keeps the day it belongs to
CUT=$(date -u -d "$KEEP_DAYS days ago" +%y%m%d)
for f in "$OUT"/*.gz; do
    [ -e "$f" ] || continue
    b=$(basename "$f"); d=${b%%_*}
    case "$d" in
        [0-9][0-9][0-9][0-9][0-9][0-9])
            if [ "$d" -lt "$CUT" ]; then rm -f "$f"; say "AGED OUT $b"; fi ;;
    esac
done

say "DONE $STAMP  $(ls -1 "$OUT"/*.gz 2>/dev/null | wc -l) archives, $(du -sh "$OUT" | cut -f1)"
