export type StrategyOverlayItem = {
  symbol: string;
  security_name: string;
  sleeve: string;
  market: string;
  country: string;
  current_market_value_base: number;
  current_weight_of_nav: number;
  strategy_state: string | null;
  target_state: string | null;
  target_weight: number | null;
  target_dollars: number | null;
  actual_position_dollars: number | null;
  actual_vs_target_delta: number | null;
  eligibility_status: string | null;
  buy_list_status: string | null;
  reason_code: string | null;
  as_of_date: string | null;
};

export type DailyDecisionLogItem = {
  decision_date: string;
  symbol: string;
  market: string;
  sleeve: string;
  sector: string | null;
  eligibility_status: string | null;
  buy_list_status: string | null;
  current_state: string | null;
  target_state: string | null;
  current_position_dollars: number | null;
  target_position_dollars: number | null;
  generated_order_quantity: number | null;
  fill_quantity: number | null;
  rejection_status: string | null;
  reason_code: string | null;
  decision_timestamp: string | null;
};

export type ReasonCodeOption = {
  code: string;
  label: string;
  description: string;
};

export type StrategyOptionsPayload = {
  strategy_state_options: string[];
  target_state_options: string[];
  eligibility_status_options: string[];
  buy_list_status_options: string[];
  reason_codes: ReasonCodeOption[];
};

export type ManualStrategyOverlayUpsertRequest = {
  symbol: string;
  sleeve: string;
  strategy_state: string | null;
  target_state: string | null;
  target_weight: number | null;
  target_dollars: number | null;
  eligibility_status: string | null;
  buy_list_status: string | null;
  reason_code: string;
  notes: string | null;
  append_decision_log: boolean;
};

export type ManualStrategyOverlayUpsertResult = {
  overlay_id: number;
  symbol: string;
  sleeve: string;
  as_of_date: string;
  reason_code: string;
  actual_position_dollars: number;
  target_dollars: number | null;
  actual_vs_target_delta: number | null;
  decision_log_written: boolean;
};