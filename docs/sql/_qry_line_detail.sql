SELECT
  indicator_configs.ic_pk,
  indicator_timeframes.itf_label,
  indicator_series.is_prefix,
  indicator_lines.il_suffix,
  indicator_configs.ic_line_type,
  indicator_configs.ic_src,
  indicator_configs.ic_bb_len,
  indicator_configs.ic_bb_mult,
  indicator_configs.ic_k_len,
  indicator_configs.ic_rsi_len,
  indicator_configs.ic_stc_len,
  indicator_configs.ic_low_boundary,
  indicator_configs.ic_high_boundary
FROM indicator_configs
  INNER JOIN indicator_series
    ON indicator_configs.ic_is_pk = indicator_series.is_pk
  INNER JOIN indicator_lines
    ON indicator_configs.ic_il_pk = indicator_lines.il_pk
  INNER JOIN indicator_timeframes
    ON indicator_configs.ic_itf_pk = indicator_timeframes.itf_pk