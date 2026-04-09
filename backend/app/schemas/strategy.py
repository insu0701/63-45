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


class ReasonCodeOption(BaseModel):
    code: str
    label: str
    description: str


class StrategyOptionsPayload(BaseModel):
    strategy_state_options: list[str]
    target_state_options: list[str]
    eligibility_status_options: list[str]
    buy_list_status_options: list[str]
    reason_codes: list[ReasonCodeOption]


class ManualStrategyOverlayUpsertRequest(BaseModel):
    symbol: str
    sleeve: str
    strategy_state: str | None = None
    target_state: str | None = None
    target_weight: float | None = None
    target_dollars: float | None = None
    eligibility_status: str | None = None
    buy_list_status: str | None = None
    reason_code: str
    notes: str | None = None
    append_decision_log: bool = True


class ManualStrategyOverlayUpsertResult(BaseModel):
    overlay_id: int
    symbol: str
    sleeve: str
    as_of_date: str
    reason_code: str
    actual_position_dollars: float
    target_dollars: float | None
    actual_vs_target_delta: float | None
    decision_log_written: bool


class RebalanceCandidateItem(BaseModel):
    symbol: str
    security_name: str
    sleeve: str
    market: str
    country: str
    current_market_value_base: float
    target_dollars: float
    actual_vs_target_delta: float
    abs_delta_dollars: float
    current_weight_of_nav: float
    target_weight: float | None
    strategy_state: str | None
    target_state: str | None
    reason_code: str | None
    suggested_action: str


class StrategyReviewMetrics(BaseModel):
    overlay_row_count: int
    rows_with_target: int
    rows_without_target: int
    rows_with_delta: int
    on_target_count: int
    add_count: int
    trim_count: int
    exit_count: int
    gross_abs_delta_dollars: float
    net_delta_dollars: float


class StrategyReviewPayload(BaseModel):
    metrics: StrategyReviewMetrics
    candidates: list[RebalanceCandidateItem]