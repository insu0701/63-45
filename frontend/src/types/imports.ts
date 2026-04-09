export type SyncActionResult = {
  sync_run_id: number;
  snapshot_time: string;
  holdings_written: number;
  cash_rows_written: number;
  prices_written: number;
  carry_forward_holdings: number;
  carry_forward_cash: number;
  warning_count: number;
  error_count: number;
  imported_symbols?: string[];
  archive_paths?: Record<string, string>;
};

export type PriceSyncActionResult = {
  sync_run_id: number;
  snapshot_time: string;
  holdings_written: number;
  prices_written: number;
  kr_symbols_priced: number;
  us_symbols_priced: number;
  carry_forward_symbols: number;
  warning_count: number;
  error_count: number;
};

export type FxSyncActionResult = {
  sync_run_id: number;
  snapshot_time: string;
  rates_written: number;
  warning_count: number;
  error_count: number;
  provider: string;
};

export type FullSyncActionResult = {
  started_at: string;
  finished_at: string;
  fx_sync_run_id: number;
  kiwoom_sync_run_id: number;
  price_sync_run_id: number;
  fx_rates_written: number;
  holdings_written: number;
  cash_rows_written: number;
  prices_written: number;
  carry_forward_holdings: number;
  carry_forward_cash: number;
  price_refresh_holdings_written: number;
  price_refresh_prices_written: number;
  price_carry_forward_symbols: number;
  warning_count: number;
  error_count: number;
};