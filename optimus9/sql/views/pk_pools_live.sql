-- pk_pools_live: the live PK pool per series, mirroring indicator_configs_live —
-- the row whose pkp_live_after_date is the latest <= NOW() for each series.
CREATE OR REPLACE VIEW pk_pools_live AS
SELECT p.*, s.is_prefix
FROM pk_pools p
JOIN indicator_series s ON s.is_pk = p.pkp_is_pk
WHERE p.pkp_live_after_date = (
    SELECT MAX(p2.pkp_live_after_date)
    FROM pk_pools p2
    WHERE p2.pkp_is_pk = p.pkp_is_pk
      AND p2.pkp_live_after_date <= NOW()
);
