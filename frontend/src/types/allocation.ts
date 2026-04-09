export type SleeveAllocationItem = {
  sleeve: string;
  equity_value_base: number;
  cash_value_base: number;
  total_base_value: number;
  weight_of_total_nav: number;
  position_count: number;
  unrealized_pnl_base: number;
};

export type CountryAllocationItem = {
  country: string;
  market_value_base: number;
  weight_of_total_nav: number;
};

export type SectorAllocationItem = {
  sector: string;
  market_value_base: number;
  weight_of_total_nav: number;
};

export type CurrencyAllocationItem = {
  currency: string;
  total_base_value: number;
  weight_of_total_nav: number;
};