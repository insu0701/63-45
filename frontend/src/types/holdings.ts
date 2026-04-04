export type HoldingsFilterState = {
  sleeve: "ALL" | "KR" | "US";
  sector: string;
  search: string;
  performance: "ALL" | "WINNERS" | "LOSERS";
  minWeightPercent: string;
};

export type HoldingListItem = {
  symbol: string;
  security_name: string;
  sleeve: string;
  country: string;
  sector: string | null;
  industry: string | null;
  market: string;
  currency: string;
  quantity: number;
  avg_cost_native: number | null;
  current_price_native: number | null;
  cost_basis_base: number | null;
  market_value_base: number | null;
  unrealized_pnl_base: number | null;
  unrealized_return_pct: number | null;
  weight_of_total_nav: number;
  weight_of_sleeve: number;
  price_timestamp: string | null;
  source_type: string;
};

export type HoldingDetailItem = {
  symbol: string;
  security_name: string;
  sleeve: string;
  country: string;
  sector: string | null;
  industry: string | null;
  market: string;
  currency: string;
  quantity: number;
  avg_cost_native: number | null;
  current_price_native: number | null;
  cost_basis_native: number | null;
  market_value_native: number | null;
  unrealized_pnl_native: number | null;
  unrealized_return_pct: number | null;
  fx_rate_to_base: number | null;
  cost_basis_base: number | null;
  market_value_base: number | null;
  unrealized_pnl_base: number | null;
  price_timestamp: string | null;
  snapshot_time: string;
  source_type: string;
};