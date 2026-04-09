export type OverviewCashCurrency = {
  base_currency: string;
  krw_cash_native: number;
  krw_cash_base: number;
  usd_cash_native: number;
  usd_cash_base: number;
  total_cash_base: number;
  fx_rate_krw_to_base: number;
  fx_rate_base_to_krw: number;
  fx_rate_timestamp: string | null;
};

export type OverviewSnapshotMetadata = {
  holdings_snapshot_time: string | null;
  cash_snapshot_time: string | null;
  price_snapshot_time: string | null;
  fx_snapshot_time: string | null;
  holdings_source_type: string | null;
  cash_source_type: string | null;
  price_source_type: string | null;
  fx_source_type: string | null;
  holdings_detail: string | null;
  cash_detail: string | null;
  price_detail: string | null;
  fx_detail: string | null;
};

export type OverviewSummary = {
  total_equity_value_base: number;
  total_cash_base: number;
  total_nav_base: number;
  total_unrealized_pnl_base: number;
  total_unrealized_return_pct: number;
  kr_equity_value_base: number;
  us_equity_value_base: number;
  krw_cash_base: number;
  usd_cash_base: number;
  cash_currency: OverviewCashCurrency;
  snapshot_metadata: OverviewSnapshotMetadata;
};

export type TopHolding = {
  symbol: string;
  security_name: string;
  sleeve: string;
  country: string;
  market_value_base: number;
  cost_basis_base: number;
  unrealized_pnl_base: number;
  unrealized_return_pct: number;
  weight_of_total_nav: number;
};

export type Concentration = {
  top1_pct: number;
  top3_pct: number;
  top5_pct: number;
  largest_sector_pct: number;
  largest_sleeve_pct: number;
};