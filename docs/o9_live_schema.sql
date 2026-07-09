-- o9_live_schema.sql (Joe 0628) — o9-live forward-test DB schema.
-- COPIED config/reference + live-data tables (trace-verified deps + FK parents), NO backtest tables.
-- + fake-exchange / pyramiding tables. See docs/o9_live_design.md.

-- ===== COPIED: config/reference (seed from dev) + live-data (collector fills) =====
CREATE TABLE `indicator_value_modes` (
  `ivm_pk` int NOT NULL,
  `ivm_label` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ivm_description` varchar(160) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ivm_pk`),
  UNIQUE KEY `ivm_label` (`ivm_label`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `indicator_series` (
  `is_pk` smallint unsigned NOT NULL AUTO_INCREMENT,
  `is_prefix` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`is_pk`),
  UNIQUE KEY `uq_is_prefix` (`is_prefix`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `indicator_lines` (
  `il_pk` smallint unsigned NOT NULL AUTO_INCREMENT,
  `il_suffix` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `il_description` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`il_pk`),
  UNIQUE KEY `uq_il_suffix` (`il_suffix`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `indicator_timeframes` (
  `itf_pk` smallint unsigned NOT NULL AUTO_INCREMENT,
  `itf_label` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL,
  `itf_seconds` smallint unsigned NOT NULL,
  PRIMARY KEY (`itf_pk`),
  UNIQUE KEY `uq_itf_label_seconds` (`itf_label`,`itf_seconds`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `indicator_configs` (
  `ic_pk` int unsigned NOT NULL AUTO_INCREMENT,
  `ic_is_pk` smallint unsigned NOT NULL,
  `ic_itf_pk` smallint unsigned NOT NULL,
  `ic_il_pk` smallint unsigned NOT NULL,
  `ic_line_type` enum('bb','k') COLLATE utf8mb4_unicode_ci NOT NULL,
  `ic_live_after_dt` datetime NOT NULL DEFAULT '2000-01-01 00:00:00',
  `ic_src` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ic_high_boundary` decimal(6,2) NOT NULL DEFAULT '85.00',
  `ic_low_boundary` decimal(6,2) NOT NULL DEFAULT '15.00',
  `ic_bb_len` smallint unsigned DEFAULT NULL,
  `ic_bb_mult` decimal(8,4) DEFAULT NULL,
  `ic_k_len` smallint unsigned DEFAULT NULL,
  `ic_rsi_len` smallint unsigned DEFAULT NULL,
  `ic_stc_len` smallint unsigned DEFAULT NULL,
  `ic_ivm_pk` int DEFAULT '1',
  `ic_wobble` smallint unsigned DEFAULT NULL,
  PRIMARY KEY (`ic_pk`),
  UNIQUE KEY `uq_ic_instance_dt` (`ic_is_pk`,`ic_itf_pk`,`ic_il_pk`,`ic_live_after_dt`),
  KEY `ic_itf_pk` (`ic_itf_pk`),
  KEY `ic_il_pk` (`ic_il_pk`),
  CONSTRAINT `indicator_configs_ibfk_1` FOREIGN KEY (`ic_is_pk`) REFERENCES `indicator_series` (`is_pk`),
  CONSTRAINT `indicator_configs_ibfk_2` FOREIGN KEY (`ic_itf_pk`) REFERENCES `indicator_timeframes` (`itf_pk`),
  CONSTRAINT `indicator_configs_ibfk_3` FOREIGN KEY (`ic_il_pk`) REFERENCES `indicator_lines` (`il_pk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `optimus9_system` (
  `sys_pk` bigint NOT NULL AUTO_INCREMENT,
  `pxsmooth_dema_src` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT 'close',
  `pxsmooth_dema_len` int DEFAULT '2',
  `pxsmooth_dema_tf` int DEFAULT '5',
  `hi_boundary` float DEFAULT '85',
  `lo_boundary` float DEFAULT '15',
  PRIMARY KEY (`sys_pk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `bl_lines` (
  `bl_pk` bigint NOT NULL AUTO_INCREMENT,
  `bl_ic_pk` bigint NOT NULL,
  `bl_line_name` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bl_role` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
  `bl_exit_mask` int DEFAULT NULL,
  `bl_pk_ic_pk` bigint DEFAULT NULL,
  `bl_pk_line_name` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bl_is_active` tinyint DEFAULT '0',
  `bl_live_after_date` datetime DEFAULT '2000-01-01 00:00:00',
  `bl_support_ic_pk` bigint DEFAULT NULL,
  `bl_exit3_support_ic_pk` bigint DEFAULT NULL,
  PRIMARY KEY (`bl_pk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `trading_pairs` (
  `tp_pk` int unsigned NOT NULL AUTO_INCREMENT,
  `tp_symbol_bybit` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tp_symbol_bnc` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tp_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`tp_pk`),
  UNIQUE KEY `uq_tp_bybit` (`tp_symbol_bybit`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `lp_config` (
  `name` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `val` double NOT NULL,
  `note` varchar(160) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- lr cascade gate-sets (roles arm/finisher/gate) — lr_config/lr_detect read these (were missing 0702)
CREATE TABLE `lr_gate` (
  `lrg_pk` int NOT NULL AUTO_INCREMENT,
  `lrg_role` enum('arm','finisher','gate') COLLATE utf8mb4_unicode_ci NOT NULL,
  `lrg_name` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `lrg_op` enum('AND','OR') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'AND',
  `lrg_active` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`lrg_pk`),
  UNIQUE KEY `lrg_name` (`lrg_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `lr_gate_line` (
  `lrgl_pk` int NOT NULL AUTO_INCREMENT,
  `lrgl_lrg_pk` int NOT NULL,
  `lrgl_ic_pk` int NOT NULL,
  `lrgl_check` enum('oob','lookback','mid') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'oob',
  `lrgl_lookback` int DEFAULT NULL,
  PRIMARY KEY (`lrgl_pk`),
  KEY `lrgl_lrg_pk` (`lrgl_lrg_pk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `kline_collection` (
  `kc_pk` int unsigned NOT NULL AUTO_INCREMENT,
  `kc_tp_pk` int unsigned NOT NULL,
  `kc_timestamp` bigint NOT NULL,
  `kc_open` decimal(20,8) NOT NULL,
  `kc_high` decimal(20,8) NOT NULL,
  `kc_low` decimal(20,8) NOT NULL,
  `kc_close` decimal(20,8) NOT NULL,
  `kc_volume` decimal(20,8) NOT NULL,
  PRIMARY KEY (`kc_pk`),
  UNIQUE KEY `uq_kc_tp_ts` (`kc_tp_pk`,`kc_timestamp`),
  KEY `idx_kc_tp_ts` (`kc_tp_pk`,`kc_timestamp`),
  CONSTRAINT `kline_collection_ibfk_1` FOREIGN KEY (`kc_tp_pk`) REFERENCES `trading_pairs` (`tp_pk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `ticks` (
  `tk_pk` bigint unsigned NOT NULL AUTO_INCREMENT,
  `tk_tp_pk` int unsigned NOT NULL,
  `tk_timestamp` bigint NOT NULL,
  `tk_price` decimal(20,8) NOT NULL,
  `tk_volume` decimal(20,8) NOT NULL,
  `tk_side` enum('buy','sell') COLLATE utf8mb4_unicode_ci NOT NULL,
  `tk_trade_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`tk_pk`),
  UNIQUE KEY `uq_tk_tp_tid` (`tk_tp_pk`,`tk_trade_id`),
  KEY `idx_tk_tp_ts` (`tk_tp_pk`,`tk_timestamp`),
  CONSTRAINT `ticks_ibfk_1` FOREIGN KEY (`tk_tp_pk`) REFERENCES `trading_pairs` (`tp_pk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- live-config view
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`%` SQL SECURITY DEFINER VIEW `vw_indicator_configs_live` AS select `ic`.`ic_pk` AS `ic_pk`,`ic`.`ic_is_pk` AS `ic_is_pk`,`ic`.`ic_itf_pk` AS `ic_itf_pk`,`ic`.`ic_il_pk` AS `ic_il_pk`,`ic`.`ic_line_type` AS `ic_line_type`,`ic`.`ic_live_after_dt` AS `ic_live_after_dt`,`ic`.`ic_src` AS `ic_src`,`ic`.`ic_high_boundary` AS `ic_high_boundary`,`ic`.`ic_low_boundary` AS `ic_low_boundary`,`ic`.`ic_bb_len` AS `ic_bb_len`,`ic`.`ic_bb_mult` AS `ic_bb_mult`,`ic`.`ic_k_len` AS `ic_k_len`,`ic`.`ic_rsi_len` AS `ic_rsi_len`,`ic`.`ic_stc_len` AS `ic_stc_len`,concat(`s`.`is_prefix`,`itf`.`itf_label`,`il`.`il_suffix`) AS `ind_name`,`itf`.`itf_seconds` AS `itf_seconds`,`ic`.`ic_ivm_pk` AS `ic_ivm_pk`,`vm`.`ivm_label` AS `value_mode` from ((((`indicator_configs` `ic` join `indicator_series` `s` on((`s`.`is_pk` = `ic`.`ic_is_pk`))) join `indicator_lines` `il` on((`il`.`il_pk` = `ic`.`ic_il_pk`))) join `indicator_timeframes` `itf` on((`itf`.`itf_pk` = `ic`.`ic_itf_pk`))) left join `indicator_value_modes` `vm` on((`vm`.`ivm_pk` = `ic`.`ic_ivm_pk`))) where (`ic`.`ic_live_after_dt` = (select max(`ic2`.`ic_live_after_dt`) from `indicator_configs` `ic2` where ((`ic2`.`ic_is_pk` = `ic`.`ic_is_pk`) and (`ic2`.`ic_il_pk` = `ic`.`ic_il_pk`) and (`ic2`.`ic_itf_pk` = `ic`.`ic_itf_pk`) and (`ic2`.`ic_live_after_dt` <= now()))));

-- ===== NEW: fake-exchange + pyramiding (o9-live forward-test) =====
-- Position model = Bybit one-way: cascade re-arms ADD to one accumulating same-side position
-- (size grows, avg_entry re-weights), exits reduce it. Slippage = live order-book walk per fill.

CREATE TABLE fx_order (
  order_id      VARCHAR(40)  NOT NULL PRIMARY KEY,         -- our uuid (mirrors Bybit orderId)
  order_link_id VARCHAR(40),                               -- client id (orderLinkId)
  symbol        VARCHAR(20)  NOT NULL,
  side          ENUM('Buy','Sell') NOT NULL,
  order_type    ENUM('Market','Limit') NOT NULL,
  qty           DECIMAL(20,8) NOT NULL,                    -- coins
  price         DECIMAL(20,8),                             -- limit price (NULL for market)
  reduce_only   TINYINT DEFAULT 0,
  order_status  ENUM('New','Filled','Cancelled','Rejected') NOT NULL,
  created_ms    BIGINT NOT NULL,
  updated_ms    BIGINT,
  INDEX(symbol), INDEX(created_ms)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE fx_position (
  position_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
  symbol         VARCHAR(20) NOT NULL,
  side           ENUM('Buy','Sell') NOT NULL,             -- the leg's fixed direction (positionIdx 1→Buy, 2→Sell)
  position_idx   TINYINT NOT NULL DEFAULT 1,              -- Bybit hedge mode: 1=long leg, 2=short leg (both open at once)
  size           DECIMAL(20,8) NOT NULL,                  -- current accumulated size (coins)
  avg_entry      DECIMAL(20,8) NOT NULL,                  -- volume-weighted avg entry
  entry_count    INT DEFAULT 1,                           -- pyramid adds
  leverage       INT DEFAULT 50,
  stop_loss      DECIMAL(20,8),                           -- server-side SL price (0.5%)
  status         ENUM('open','closed') NOT NULL,
  opened_ms      BIGINT NOT NULL,
  closed_ms      BIGINT,
  realized_pnl   DECIMAL(20,8) DEFAULT 0,                 -- net of fees + slippage, on (partial/full) close
  total_fees     DECIMAL(20,8) DEFAULT 0,
  total_slip_bps DECIMAL(10,2),                           -- size-weighted avg slippage across fills
  INDEX(symbol), INDEX(status), INDEX(opened_ms), INDEX(symbol, position_idx, status)  -- per-leg open lookup
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE fx_fill (
  exec_id       BIGINT AUTO_INCREMENT PRIMARY KEY,        -- mirrors execId
  order_id      VARCHAR(40) NOT NULL,
  position_id   BIGINT NOT NULL,                          -- position this fill built / reduced
  symbol        VARCHAR(20) NOT NULL,
  side          ENUM('Buy','Sell') NOT NULL,
  exec_price    DECIMAL(20,8) NOT NULL,                   -- order-book-walk avg fill
  exec_qty      DECIMAL(20,8) NOT NULL,
  mid_price     DECIMAL(20,8) NOT NULL,                   -- book mid at fill (slippage basis)
  slippage_bps  DECIMAL(10,2) NOT NULL,                   -- (exec_price - mid)/mid, signed by side
  fee           DECIMAL(20,8) NOT NULL,                   -- taker fee on this fill
  is_maker      TINYINT DEFAULT 0,
  closed_size   DECIMAL(20,8) DEFAULT 0,                  -- size reduced (exit fills)
  exec_ms       BIGINT NOT NULL,
  INDEX(order_id), INDEX(position_id), INDEX(exec_ms)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE o9_decision (                                 -- o9-live's per-5s output (to test the strategy output)
  decision_id   BIGINT AUTO_INCREMENT PRIMARY KEY,
  kline_ms      BIGINT NOT NULL,                          -- the 5s bar decided on
  action        ENUM('open_long','open_short','add','close','hold') NOT NULL,
  reason        VARCHAR(60),                              -- cf15_finisher | sl_hit | exit_signal | ...
  order_id      VARCHAR(40),                              -- order it triggered (NULL for hold)
  line_snapshot JSON,                                     -- W.line values at decision (audit/debug)
  created_ms    BIGINT NOT NULL,
  INDEX(kline_ms)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===== o9-live OWNED (client-side, NOT the exchange's fx_*) — the UI reads these; reconciled to the exchange =====
-- Independent-rows trades (Joe's UI model), built from fills o9 receives via the adapter (mirror of fx_fill).
CREATE TABLE o9_ledger (
  led_id         BIGINT AUTO_INCREMENT PRIMARY KEY,
  symbol         VARCHAR(20) NOT NULL,
  side           ENUM('Buy','Sell') NOT NULL,
  qty            DECIMAL(20,8) NOT NULL,
  entry_px       DECIMAL(20,8) NOT NULL,                  -- o9's observed entry fill
  exit_px        DECIMAL(20,8),                           -- o9's observed exit fill
  entry_order_id VARCHAR(40),
  exit_order_id  VARCHAR(40),
  gross          DECIMAL(20,8),                           -- o9's computed gross
  net            DECIMAL(20,8),                           -- o9's computed net (after est fee)
  fee            DECIMAL(20,8),
  mae            DECIMAL(10,4),                           -- filled when live price-tracking lands (nullable)
  reason         VARCHAR(40),
  status         ENUM('open','closed') NOT NULL,
  opened_ms      BIGINT NOT NULL,
  closed_ms      BIGINT,
  INDEX(symbol), INDEX(status), INDEX(opened_ms)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- o9's OWN running equity tally (NOT the exchange balance — reconciled to Bybit daily; see the recon task).
CREATE TABLE o9_account (
  acct_id        INT PRIMARY KEY,                         -- single row (1)
  equity         DECIMAL(20,8) NOT NULL,
  realized_total DECIMAL(20,8) NOT NULL DEFAULT 0,
  trade_count    INT NOT NULL DEFAULT 0,
  updated_ms     BIGINT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- operator control state — the UI writes, the loop reads next bar (sizing / halt / flatten). Single row (1).
CREATE TABLE o9_control (
  ctl_id      INT PRIMARY KEY,
  mode        VARCHAR(16) NOT NULL DEFAULT 'fixed',       -- smallest | fixed | dynamic5x
  max_order   INT NOT NULL DEFAULT 66000,
  split       INT NOT NULL DEFAULT 1,
  halted      TINYINT NOT NULL DEFAULT 0,                 -- kill-switch: stop opening new trades
  flatten_req TINYINT NOT NULL DEFAULT 0,                 -- close the net position now (exit / kill)
  updated_ms  BIGINT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- live health heartbeat — the running processes WRITE, the UI READS (mirror of o9_control's direction).
-- cascade phase (loop, via v2_phase) + feed-health counters (loop/adapter/feed). Tape-health
-- (kline gaps / frozen / synthetic) is computed live in the UI from kline_collection, not stored. Single row (1).
CREATE TABLE o9_health (
  health_id       INT PRIMARY KEY,                        -- single row (1)
  phase_label     VARCHAR(64) NOT NULL DEFAULT 'flat',    -- composed cascade chip (v2_phase)
  phase_tone      VARCHAR(8)  NOT NULL DEFAULT 'idle',    -- go | wait | idle → block colour
  arm             VARCHAR(8),                             -- s5m | s5r | NULL
  gate            VARCHAR(8),                             -- open | latched | NULL
  gate_reason     VARCHAR(4),                             -- a | b | c | NULL
  exit_line       VARCHAR(8),                             -- s7 | NULL (exit-watch)
  -- cascade mirror-grid (HealthStore.set_cascade; UI reads via int() → must be NOT NULL)
  cascade_mask    INT     NOT NULL DEFAULT 0,             -- per-bar bitfield, bit=(col-1)*4+(row-1), 4x5 grid
  cascade_es      TINYINT NOT NULL DEFAULT 0,             -- arm side: -1 | +1 (0 = none)
  cascade_armed   TINYINT NOT NULL DEFAULT 0,             -- 0 | 1
  loop_ms         INT,                                    -- decision-loop latency (bar-close → order sent)
  rtt_ms          INT,                                    -- exchange round-trip
  clock_skew_ms   INT,                                    -- local vs exchange server time
  pubtrade_age_ms INT,                                    -- last publicTrade age
  order_rejects   INT NOT NULL DEFAULT 0,                 -- session cumulative
  ws_reconnects   INT NOT NULL DEFAULT 0,
  db_reconnects   INT NOT NULL DEFAULT 0,
  updated_ms      BIGINT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- o9_trade_archive: durable closed-trade store (Joe 0709). NOT wiped by /api/reset — persistent trade
-- history for the stop-tool. label = mmdd_NN (the pine-emit label). Written by O9Ledger._archive on close.
CREATE TABLE o9_trade_archive (
  label        VARCHAR(16) PRIMARY KEY,                  -- mmdd_NN (0709_01, ...)
  symbol       VARCHAR(20) NOT NULL,
  side         ENUM('Buy','Sell') NOT NULL,
  position_idx TINYINT NOT NULL,                         -- 1=long 2=short (hedge)
  qty          DECIMAL(20,8) NOT NULL,
  entry_px     DECIMAL(20,8) NOT NULL,
  exit_px      DECIMAL(20,8) NOT NULL,
  entry_ms     BIGINT NOT NULL,
  exit_ms      BIGINT NOT NULL,
  gross        DECIMAL(20,8),
  net          DECIMAL(20,8),
  fee          DECIMAL(20,8),
  mae          DECIMAL(20,8),                            -- TODO: loop does not yet record live MAE
  open_reason  VARCHAR(24),
  close_reason VARCHAR(24),                              -- exit | SL
  archived_ms  BIGINT NOT NULL,
  INDEX(entry_ms), INDEX(net)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
