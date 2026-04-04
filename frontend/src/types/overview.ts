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