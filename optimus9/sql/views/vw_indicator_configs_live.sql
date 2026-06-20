-- vw_indicator_configs_live — current line config per (series, line, timeframe),
-- resolved via ic_live_after_dt (the latest version whose dt <= now).
-- Renamed from indicator_configs_live + ind_name fixed to include itf_label (Joe 0620):
-- ind_name now = prefix+timeframe+suffix (e.g. 's30M', 'bny30M'), unique per line — the old
-- concat(prefix,suffix) collided every TF of a series ('sM' = s14M AND s30M).
CREATE OR REPLACE VIEW vw_indicator_configs_live AS
SELECT ic.*,
       CONCAT(s.is_prefix, itf.itf_label, il.il_suffix) AS ind_name,
       itf.itf_seconds                                  AS itf_seconds
FROM indicator_configs    ic
JOIN indicator_series     s   ON s.is_pk    = ic.ic_is_pk
JOIN indicator_lines      il  ON il.il_pk   = ic.ic_il_pk
JOIN indicator_timeframes itf ON itf.itf_pk = ic.ic_itf_pk
WHERE ic.ic_live_after_dt = (
    SELECT MAX(ic2.ic_live_after_dt)
    FROM indicator_configs ic2
    WHERE ic2.ic_is_pk  = ic.ic_is_pk
      AND ic2.ic_il_pk  = ic.ic_il_pk
      AND ic2.ic_itf_pk = ic.ic_itf_pk
      AND ic2.ic_live_after_dt <= NOW()
);
