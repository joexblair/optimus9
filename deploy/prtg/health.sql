-- PRTG MySQL v2 sensor — Optimus9 data-pipeline health (one sensor, 5 channels).
-- Each aliased column becomes a PRTG channel; set the Error thresholds per the comments.
-- Single pair (tp_pk = 1, FARTCOIN) — clone per pair when more are live.
SELECT
  -- collector writing 5s bars? seconds since the last kline_collection bar.   Error > 15
  (UNIX_TIMESTAMP()*1000 - (SELECT MAX(kc_timestamp) FROM kline_collection WHERE kc_tp_pk=1)) / 1000  AS kc_age_s,

  -- WS tick stream alive? seconds since the last tick.                          Error > 10
  (UNIX_TIMESTAMP()*1000 - (SELECT MAX(tk_timestamp) FROM ticks WHERE tk_tp_pk=1)) / 1000             AS tick_age_s,

  -- auditor 5s freeze/missing faults in the last 5 min.                          Error > 0
  (SELECT COUNT(*) FROM kline_audit
     WHERE ka_tier='5s' AND ka_verdict IN ('missing','frozen')
       AND ka_created > NOW() - INTERVAL 5 MINUTE)                                AS faults_5s,

  -- tape != exchange (the 1m tick-exact gate) in the last 10 min.                Error > 0
  (SELECT COUNT(*) FROM kline_audit
     WHERE ka_tier='1m' AND ka_verdict='variance'
       AND ka_created > NOW() - INTERVAL 10 MINUTE)                               AS variance_1m,

  -- auditor itself alive? seconds since its last write.                          Error > 60
  TIMESTAMPDIFF(SECOND, (SELECT MAX(ka_created) FROM kline_audit), NOW())         AS audit_age_s;
