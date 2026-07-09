SET @or = 40;

SELECT
    -- Run identifiers
    o.or_pk,
    FROM_UNIXTIME(o.or_timestamp / 1000) AS or_started_at,
    o.or_completed_at,
    o.or_p_rev_enabled,
    o.or_pk5s_gate_enabled,
    o.or_dema_len,
    o.or_dema_src,

    -- TC details
    tc.tc_pk,
    tc.tc_indicator_label,
    tc.tc_stop_pct,
    tc.tc_profit_zone,

    -- Calibration line (single composed name)
    CONCAT(s.is_prefix, itf.itf_label, il.il_suffix) AS calib_line_name,
    ic.ic_pk            AS calib_ic_pk,
    ic.ic_line_type     AS calib_line_type,
    ic.ic_src           AS calib_src,
    ic.ic_high_boundary AS calib_hi_bound,
    ic.ic_low_boundary  AS calib_lo_bound,
    ic.ic_bb_len, ic.ic_bb_mult,
    ic.ic_k_len, ic.ic_rsi_len, ic.ic_stc_len,
    itf.itf_seconds     AS calib_tf_seconds,

    -- Trading pair
    tp.tp_pk,
    tp.tp_symbol_bybit,

    -- Extensions attached (gates + pk_5s) — group_concat
    (SELECT GROUP_CONCAT(
        DISTINCT CONCAT(s2.is_prefix, itf2.itf_label, il2.il_suffix, ':', tce.tce_type)
        ORDER BY tce.tce_sort_order SEPARATOR ', ')
     FROM test_config_extensions tce
     LEFT JOIN indicator_configs    ic2  ON ic2.ic_pk   = tce.tce_ic_pk
     LEFT JOIN indicator_series     s2   ON s2.is_pk    = ic2.ic_is_pk
     LEFT JOIN indicator_timeframes itf2 ON itf2.itf_pk = ic2.ic_itf_pk
     LEFT JOIN indicator_lines      il2  ON il2.il_pk   = ic2.ic_il_pk
     WHERE tce.tce_tc_pk = tc.tc_pk
       AND tce.tce_is_active = 1
    ) AS attached_extensions

FROM optimizer_runs o
JOIN test_configs         tc  ON tc.tc_pk    = o.or_tc_pk
JOIN indicator_configs    ic  ON ic.ic_pk    = tc.tc_ic_pk
JOIN indicator_timeframes itf ON itf.itf_pk  = ic.ic_itf_pk
JOIN indicator_series     s   ON s.is_pk     = ic.ic_is_pk
JOIN indicator_lines      il  ON il.il_pk    = ic.ic_il_pk
LEFT JOIN trading_pairs   tp  ON tp.tp_pk    = o.or_tp_pk
WHERE tc.tc_pk = 18;
WHERE o.or_pk = @or;