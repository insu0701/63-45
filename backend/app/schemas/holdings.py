from pydantic import BaseModel


class HoldingListItem(BaseModel):
    symbol: str
    security_name: str
    sleeve: str
    country: str
    sector: str | None
    industry: str | None
    market: str
    currency: str
    quantity: float
    avg_cost_native: float | None
    current_price_native: float | None
    cost_basis_base: float | None
    market_value_base: float | None
    unrealized_pnl_base: float | None
    unrealized_return_pct: float | None
    weight_of_total_nav: float
    weight_of_sleeve: float
    price_timestamp: str | None
    source_type: str


class HoldingDetailItem(BaseModel):
    symbol: str
    security_name: str
    sleeve: str
    country: str
    sector: str | None
    industry: str | None
    market: str
    currency: str
    quantity: float
    avg_cost_native: float | None
    current_price_native: float | None
    cost_basis_native: float | None
    market_value_native: float | None
    unrealized_pnl_native: float | None
    unrealized_return_pct: float | None
    fx_rate_to_base: float | None
    cost_basis_base: float | None
    market_value_base: float | None
    unrealized_pnl_base: float | None
    price_timestamp: str | None
    snapshot_time: str
    source_type: str