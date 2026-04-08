from pydantic import BaseModel


class StrategyOverlayItem(BaseModel):
    symbol: str
    security_name: str
    sleeve: str
    market: str
    country: str
    current_market_value_base: float
    current_weight_of_nav: float
    strategy_state: str | None
    target_state: str | None
    target_weight: float | None
    target_dollars: float | None
    actual_position_dollars: float | None
    actual_vs_target_delta: float | None
    eligibility_status: str | None
    buy_list_status: str | None
    reason_code: str | None
    as_of_date: str | None


class DailyDecisionLogItem(BaseModel):
    decision_date: str
    symbol: str
    market: str
    sleeve: str
    sector: str | None
    eligibility_status: str | None
    buy_list_status: str | None
    current_state: str | None
    target_state: str | None
    current_position_dollars: float | None
    target_position_dollars: float | None
    generated_order_quantity: float | None
    fill_quantity: float | None
    rejection_status: str | None
    reason_code: str | None
    decision_timestamp: str | None


class StrategyOverlaySummary(BaseModel):
    overlay_row_count: int
    decision_log_row_count: int
    rows_with_target: int
    rows_with_delta: int